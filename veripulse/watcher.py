import hashlib
import time
from urllib.parse import urlparse
import httpx
from bs4 import BeautifulSoup
from rich.console import Console
from rich.panel import Panel
from veripulse.collectors.medium import MediumCollector
from veripulse.collectors.news import NewsAndHNCollector
from veripulse.collectors.reddit import RedditCollector
from veripulse.config import settings
from veripulse.formatter import format_chat_message
from veripulse.models import RawItem, VerifiedStory
from veripulse.notifiers import NotificationDispatcher
from veripulse.storage import StoryStore
from veripulse.verifier import USER_AGENT, StoryVerifier

console = Console()


class VeriPulseEngine:
    """Orchestrates collection, deduplication, cross-verification, and real-time notifications."""

    def __init__(self):
        self.store = StoryStore()
        self.verifier = StoryVerifier()
        self.dispatcher = NotificationDispatcher()
        self.reddit = RedditCollector(settings.subreddits, limit_per_sub=2)
        self.medium = MediumCollector(settings.medium_tags, limit_per_tag=1)
        self.news = NewsAndHNCollector(settings.news_feeds, limit_per_feed=1, hn_limit=2)

    def run_cycle(self, ignore_seen: bool = False, max_items: int | None = None) -> tuple[list[VerifiedStory], dict[str, str]]:
        limit = max_items or settings.max_alerts_per_cycle
        console.print("[bold cyan]📡 Polling Reddit, Medium, BBC/News RSS, and Hacker News...[/bold cyan]")

        raw_candidates: list[RawItem] = []
        raw_candidates.extend(self.reddit.fetch_all())
        raw_candidates.extend(self.news.fetch_all())
        raw_candidates.extend(self.medium.fetch_all())

        # Filter unseen candidates and prioritize varied sources
        unseen: list[RawItem] = []
        for item in raw_candidates:
            if not ignore_seen and self.store.is_seen(item.item_id, item.url):
                continue
            unseen.append(item)

        # Interleave sources so a single cycle includes Reddit, News, HN, and Medium
        selected = self._select_diverse_batch(unseen, limit)
        verified_stories: list[VerifiedStory] = []

        for item in selected:
            console.print(f"  [dim]🔍 Verifying & cross-referencing:[/dim] [bold]{item.title[:80]}[/bold] ({item.source_name})")
            story = self.verifier.verify_item(item)
            self.store.mark_seen(item.item_id, item.url)

            if story.trust_score >= settings.min_trust_score or story.verification_status.value == "DISPUTED / NEEDS CAUTION":
                self.store.save_verified_story(story)
                verified_stories.append(story)
                self._print_story_card(story)

        dispatch_status = self.dispatcher.dispatch(verified_stories)
        return verified_stories, dispatch_status

    def watch_forever(self) -> None:
        console.print(
            Panel(
                f"[bold green]VeriPulse Real-Time High-Signal Watcher Active[/bold green]\n"
                f"• Subreddits: {', '.join(settings.subreddits)}\n"
                f"• Medium Tags: {', '.join(settings.medium_tags)}\n"
                f"• News Feeds: {', '.join(settings.news_feeds.keys())} + Hacker News\n"
                f"• Poll Interval: {settings.poll_interval_seconds}s | Min Trust Score: {settings.min_trust_score}/100",
                title="⚡ VeriPulse Daemon",
                border_style="cyan",
            )
        )
        while True:
            try:
                stories, status = self.run_cycle()
                console.print(f"[dim]Cycle complete: {len(stories)} alert(s) triggered. Dispatch: {status}[/dim]")
            except KeyboardInterrupt:
                console.print("\n[yellow]Stopping VeriPulse watcher.[/yellow]")
                break
            except Exception as exc:
                console.print(f"[red]Cycle error: {exc}[/red]")

            time.sleep(settings.poll_interval_seconds)

    def verify_single_url(self, url: str) -> VerifiedStory:
        """On-demand verification of any Reddit thread, Medium post, or News URL."""
        domain = urlparse(url).netloc.removeprefix("www.")
        short_hash = hashlib.sha1(url.encode("utf-8")).hexdigest()[:10]
        title = url
        summary = ""
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=12.0, follow_redirects=True) as client:
            try:
                resp = client.get(url)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    if soup.title and soup.title.string:
                        title = soup.title.string.strip()
                    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p") if len(p.get_text(" ", strip=True)) > 50]
                    summary = " ".join(paragraphs[:10])
            except Exception:
                pass

        item = RawItem(
            item_id=f"custom_{short_hash}",
            source_type="custom",
            source_name=domain or "Direct URL",
            title=title,
            url=url,
            discussion_url=url if "reddit.com" in url or "ycombinator.com" in url else "",
            summary_text=summary,
        )
        story = self.verifier.verify_item(item)
        self.store.save_verified_story(story)
        self._print_story_card(story)
        return story

    def _select_diverse_batch(self, items: list[RawItem], limit: int) -> list[RawItem]:
        buckets: dict[str, list[RawItem]] = {"reddit": [], "news": [], "hackernews": [], "medium": []}
        for item in items:
            buckets.setdefault(item.source_type, []).append(item)

        selected: list[RawItem] = []
        while len(selected) < limit and any(buckets.values()):
            for key in ("reddit", "news", "hackernews", "medium"):
                if buckets.get(key) and len(selected) < limit:
                    selected.append(buckets[key].pop(0))
        return selected

    def _print_story_card(self, story: VerifiedStory) -> None:
        border = "green" if story.trust_score >= 80 else ("yellow" if story.trust_score >= 65 else "red")
        console.print(
            Panel(
                format_chat_message(story),
                title=f"{story.badge_emoji} {story.category} • Trust {story.trust_score}/100",
                border_style=border,
            )
        )
