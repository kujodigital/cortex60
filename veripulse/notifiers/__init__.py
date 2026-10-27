from pathlib import Path
from veripulse.config import PROJECT_ROOT
from veripulse.formatter import format_chat_message, format_email_html
from veripulse.models import VerifiedStory
from veripulse.notifiers.email_sender import EmailNotifier
from veripulse.notifiers.telegram import TelegramNotifier
from veripulse.notifiers.whatsapp import WhatsAppNotifier


class NotificationDispatcher:
    """Dispatches verified stories to all enabled channels and writes local HTML/MD previews."""

    def __init__(self):
        self.telegram = TelegramNotifier()
        self.email = EmailNotifier()
        self.whatsapp = WhatsAppNotifier()

    def dispatch(self, stories: list[VerifiedStory]) -> dict[str, str]:
        if not stories:
            return {"status": "No new stories to dispatch"}

        results: dict[str, str] = {}

        # Always save local HTML and Markdown preview files
        html_path: Path = PROJECT_ROOT / "latest_digest.html"
        md_path: Path = PROJECT_ROOT / "latest_digest.md"
        html_path.write_text(format_email_html(stories), encoding="utf-8")
        md_path.write_text(
            ("\n\n---\n\n").join(format_chat_message(s) for s in stories),
            encoding="utf-8",
        )
        results["local_preview"] = f"Saved to {html_path.name} and {md_path.name}"

        ok_tg, msg_tg = self.telegram.send_stories(stories)
        results["telegram"] = msg_tg

        ok_em, msg_em = self.email.send_stories(stories)
        results["email"] = msg_em

        ok_wa, msg_wa = self.whatsapp.send_stories(stories)
        results["whatsapp"] = msg_wa

        return results
