from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
from veripulse.config import settings
from veripulse.formatter import format_chat_message, format_email_html
from veripulse.models import VerifiedStory


class EmailNotifier:
    """Sends rich HTML and plain-text verified briefs via SMTP (Gmail, Resend, etc.)."""

    def __init__(self):
        self.enabled = settings.enable_email
        self.host = settings.smtp_host
        self.port = settings.smtp_port
        self.user = settings.smtp_user
        self.password = settings.smtp_password
        self.email_from = settings.email_from or settings.smtp_user
        self.email_to = settings.email_to

    def send_stories(self, stories: list[VerifiedStory]) -> tuple[bool, str]:
        if not self.enabled:
            return False, "Email disabled in settings (ENABLE_EMAIL=false)"
        if not self.user or not self.password or not self.email_to:
            return False, "Missing SMTP_USER, SMTP_PASSWORD, or EMAIL_TO in .env"

        msg = MIMEMultipart("alternative")
        if len(stories) == 1:
            s = stories[0]
            msg["Subject"] = f"{s.badge_emoji} [{s.category}] {s.headline} (Trust: {s.trust_score}/100)"
        else:
            msg["Subject"] = f"📡 VeriPulse Alert: {len(stories)} High-Signal Verified Updates"

        msg["From"] = self.email_from
        msg["To"] = self.email_to

        plain_body = "\n\n" + ("\n" + "=" * 60 + "\n\n").join(format_chat_message(s) for s in stories)
        html_body = format_email_html(stories)

        msg.attach(MIMEText(plain_body, "plain", "utf-8"))
        msg.attach(MIMEText(html_body, "html", "utf-8"))

        try:
            with smtplib.SMTP(self.host, self.port, timeout=15) as server:
                server.starttls()
                server.login(self.user, self.password)
                recipients = [r.strip() for r in self.email_to.split(",") if r.strip()]
                server.sendmail(self.email_from, recipients, msg.as_string())
            return True, f"Sent email with {len(stories)} verified story(s) to {self.email_to}"
        except Exception as exc:
            return False, f"SMTP error: {exc}"
