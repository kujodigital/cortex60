import httpx
from veripulse.config import settings
from veripulse.formatter import format_chat_message
from veripulse.models import VerifiedStory


class WhatsAppNotifier:
    """Pluggable WhatsApp Notifier supporting Twilio WhatsApp API and Meta Cloud API."""

    def __init__(self):
        self.enabled = settings.enable_whatsapp
        self.provider = settings.whatsapp_provider.lower()

    def send_stories(self, stories: list[VerifiedStory]) -> tuple[bool, str]:
        if not self.enabled:
            return False, "WhatsApp disabled in settings (ENABLE_WHATSAPP=false)"
        if self.provider == "meta":
            return self._send_via_meta(stories)
        return self._send_via_twilio(stories)

    def _send_via_twilio(self, stories: list[VerifiedStory]) -> tuple[bool, str]:
        sid = settings.twilio_account_sid
        token = settings.twilio_auth_token
        sender = settings.twilio_whatsapp_from
        recipient = settings.whatsapp_to
        if not sid or not token or not recipient:
            return False, "Missing TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, or WHATSAPP_TO"

        url = f"https://api.twilio.com/2010-04-01/Accounts/{sid}/Messages.json"
        sent = 0
        with httpx.Client(auth=(sid, token), timeout=12.0) as client:
            for story in stories:
                body = format_chat_message(story)[:1580]  # WhatsApp Twilio single-message safe limit
                resp = client.post(
                    url,
                    data={"From": sender, "To": recipient, "Body": body},
                )
                if resp.status_code in (200, 201):
                    sent += 1
                else:
                    return False, f"Twilio WhatsApp error ({resp.status_code}): {resp.text[:160]}"
        return True, f"Sent {sent} WhatsApp message(s) via Twilio to {recipient}"

    def _send_via_meta(self, stories: list[VerifiedStory]) -> tuple[bool, str]:
        token = settings.meta_whatsapp_token
        phone_id = settings.meta_phone_number_id
        recipient = settings.whatsapp_to.removeprefix("whatsapp:+").removeprefix("+")
        if not token or not phone_id or not recipient:
            return False, "Missing META_WHATSAPP_TOKEN, META_PHONE_NUMBER_ID, or WHATSAPP_TO"

        url = f"https://graph.facebook.com/v20.0/{phone_id}/messages"
        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
        sent = 0
        with httpx.Client(headers=headers, timeout=12.0) as client:
            for story in stories:
                body = format_chat_message(story)
                resp = client.post(
                    url,
                    json={
                        "messaging_product": "whatsapp",
                        "to": recipient,
                        "type": "text",
                        "text": {"preview_url": False, "body": body},
                    },
                )
                if resp.status_code in (200, 201):
                    sent += 1
                else:
                    return False, f"Meta WhatsApp error ({resp.status_code}): {resp.text[:160]}"
        return True, f"Sent {sent} WhatsApp message(s) via Meta Cloud API to +{recipient}"
