import httpx
from veripulse.config import settings
from veripulse.formatter import format_telegram_html
from veripulse.models import VerifiedStory


class TelegramNotifier:
    """Sends real-time verified story alerts to Telegram via Bot API."""

    def __init__(self):
        self.enabled = settings.enable_telegram
        self.bot_token = settings.telegram_bot_token
        self.chat_id = settings.telegram_chat_id

    def send_stories(self, stories: list[VerifiedStory]) -> tuple[bool, str]:
        if not self.enabled:
            return False, "Telegram disabled in settings (ENABLE_TELEGRAM=false)"
        if not self.bot_token or not self.chat_id:
            return False, "Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID"

        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        sent_count = 0
        with httpx.Client(timeout=12.0) as client:
            for story in stories:
                html_msg = format_telegram_html(story)
                resp = client.post(
                    url,
                    json={
                        "chat_id": self.chat_id,
                        "text": html_msg,
                        "parse_mode": "HTML",
                        "disable_web_page_preview": True,
                    },
                )
                if resp.status_code == 200:
                    sent_count += 1
                else:
                    return False, f"Telegram API error ({resp.status_code}): {resp.text[:160]}"
        return True, f"Sent {sent_count} alert(s) to Telegram chat {self.chat_id}"
