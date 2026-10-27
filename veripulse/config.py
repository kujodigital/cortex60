import os
from dataclasses import dataclass, field
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root if present
PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")


def _parse_bool(val: str | None, default: bool = False) -> bool:
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


def _parse_csv(val: str | None, default: list[str]) -> list[str]:
    if not val:
        return default
    return [item.strip() for item in val.split(",") if item.strip()]


@dataclass
class Settings:
    # AI / LLM Settings
    gemini_api_key: str = field(default_factory=lambda: os.getenv("GEMINI_API_KEY", ""))
    gemini_model: str = field(default_factory=lambda: os.getenv("GEMINI_MODEL", "gemini-2.5-flash"))

    # Telegram Settings
    enable_telegram: bool = field(default_factory=lambda: _parse_bool(os.getenv("ENABLE_TELEGRAM"), False))
    telegram_bot_token: str = field(default_factory=lambda: os.getenv("TELEGRAM_BOT_TOKEN", ""))
    telegram_chat_id: str = field(default_factory=lambda: os.getenv("TELEGRAM_CHAT_ID", ""))

    # Email Settings
    enable_email: bool = field(default_factory=lambda: _parse_bool(os.getenv("ENABLE_EMAIL"), False))
    smtp_host: str = field(default_factory=lambda: os.getenv("SMTP_HOST", "smtp.gmail.com"))
    smtp_port: int = field(default_factory=lambda: int(os.getenv("SMTP_PORT", "587")))
    smtp_user: str = field(default_factory=lambda: os.getenv("SMTP_USER", ""))
    smtp_password: str = field(default_factory=lambda: os.getenv("SMTP_PASSWORD", ""))
    email_from: str = field(default_factory=lambda: os.getenv("EMAIL_FROM", ""))
    email_to: str = field(default_factory=lambda: os.getenv("EMAIL_TO", ""))

    # WhatsApp Settings (Pluggable for Twilio or Meta Cloud API)
    enable_whatsapp: bool = field(default_factory=lambda: _parse_bool(os.getenv("ENABLE_WHATSAPP"), False))
    whatsapp_provider: str = field(default_factory=lambda: os.getenv("WHATSAPP_PROVIDER", "twilio"))
    twilio_account_sid: str = field(default_factory=lambda: os.getenv("TWILIO_ACCOUNT_SID", ""))
    twilio_auth_token: str = field(default_factory=lambda: os.getenv("TWILIO_AUTH_TOKEN", ""))
    twilio_whatsapp_from: str = field(default_factory=lambda: os.getenv("TWILIO_WHATSAPP_FROM", "whatsapp:+14155238886"))
    whatsapp_to: str = field(default_factory=lambda: os.getenv("WHATSAPP_TO", ""))
    meta_whatsapp_token: str = field(default_factory=lambda: os.getenv("META_WHATSAPP_TOKEN", ""))
    meta_phone_number_id: str = field(default_factory=lambda: os.getenv("META_PHONE_NUMBER_ID", ""))

    # Watcher & Source Settings
    poll_interval_seconds: int = field(default_factory=lambda: int(os.getenv("POLL_INTERVAL_SECONDS", "300")))
    min_trust_score: int = field(default_factory=lambda: int(os.getenv("MIN_TRUST_SCORE", "65")))
    max_alerts_per_cycle: int = field(default_factory=lambda: int(os.getenv("MAX_ALERTS_PER_CYCLE", "5")))

    subreddits: list[str] = field(
        default_factory=lambda: _parse_csv(
            os.getenv("SUBREDDITS"),
            ["worldnews", "technology", "science"],
        )
    )
    medium_tags: list[str] = field(
        default_factory=lambda: _parse_csv(
            os.getenv("MEDIUM_TAGS"),
            ["technology", "science", "artificial-intelligence", "cybersecurity"],
        )
    )
    news_feeds: dict[str, str] = field(
        default_factory=lambda: {
            "BBC World News": "https://feeds.bbci.co.uk/news/world/rss.xml",
            "BBC Science & Environment": "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml",
            "BBC Technology": "https://feeds.bbci.co.uk/news/technology/rss.xml",
            "Ars Technica": "https://feeds.arstechnica.com/arstechnica/index",
            "Nature News": "https://www.nature.com/nature.rss",
        }
    )

    db_path: Path = field(default_factory=lambda: PROJECT_ROOT / "veripulse.db")


settings = Settings()
