from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class VerificationStatus(str, Enum):
    VERIFIED_MULTI_SOURCE = "VERIFIED MULTI-SOURCE"
    CREDIBLE_SINGLE_SOURCE = "CREDIBLE PRIMARY SOURCE"
    COMMUNITY_DISPUTED = "DISPUTED / NEEDS CAUTION"
    DEVELOPING = "DEVELOPING / UNCONFIRMED"


@dataclass
class SourceLink:
    label: str
    url: str


@dataclass
class RawItem:
    item_id: str
    source_type: str  # "reddit", "medium", "news", "hackernews"
    source_name: str  # e.g., "r/worldnews", "BBC World News", "Medium (#technology)"
    title: str
    url: str
    discussion_url: str = ""
    summary_text: str = ""
    author: str = ""
    score: int = 0
    comments_count: int = 0
    top_comments: list[str] = field(default_factory=list)
    external_links: list[str] = field(default_factory=list)
    published_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


@dataclass
class VerifiedStory:
    item_id: str
    category: str  # e.g., "WORLD", "TECH", "SCIENCE", "SECURITY"
    headline: str
    verification_status: VerificationStatus
    trust_score: int  # 0 to 100
    quick_bite: str  # 1-2 sentence zero-fluff core fact
    important_pointers: list[str]  # 3-5 hard-fact bullet points
    community_verification_notes: str  # What Reddit/HN comments or cross-checks revealed
    fluff_removed_reason: str  # What clickbait/fluff was stripped out
    sources: list[SourceLink]
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    @property
    def badge_emoji(self) -> str:
        if self.verification_status == VerificationStatus.VERIFIED_MULTI_SOURCE:
            return "✅"
        if self.verification_status == VerificationStatus.CREDIBLE_SINGLE_SOURCE:
            return "🛡️"
        if self.verification_status == VerificationStatus.COMMUNITY_DISPUTED:
            return "🚨"
        return "⚠️"
