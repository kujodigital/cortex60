import hashlib
import feedparser
import httpx
from bs4 import BeautifulSoup
from veripulse.models import RawItem

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) VeriPulseFactBot/1.0"


class MediumCollector:
    """Fetches Medium articles via tag feeds and extracts body text + cited sources."""

    def __init__(self, tags: list[str], limit_per_tag: int = 2):
        self.tags = tags
        self.limit_per_tag = limit_per_tag

    def fetch_all(self) -> list[RawItem]:
        items: list[RawItem] = []
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=12.0, follow_redirects=True) as client:
            for tag in self.tags:
                items.extend(self._fetch_tag(client, tag))
        return items

    def _fetch_tag(self, client: httpx.Client, tag: str) -> list[RawItem]:
        url = f"https://medium.com/feed/tag/{tag}"
        results: list[RawItem] = []
        try:
            resp = client.get(url)
            if resp.status_code != 200:
                return []
            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                link = entry.get("link", "").split("?")[0]
                title = entry.get("title", "").strip()
                author = entry.get("author", "Medium Author")
                html_content = ""
                if entry.get("content"):
                    html_content = entry.content[0].get("value", "")
                elif entry.get("summary"):
                    html_content = entry.get("summary", "")

                soup = BeautifulSoup(html_content, "html.parser")
                clean_text = soup.get_text(" ", strip=True).replace("Continue reading on Medium »", "").strip()
                # Skip paywall stubs or shallow listicles with no body text
                if len(clean_text) < 250:
                    continue

                external_links = []
                for a in soup.find_all("a", href=True):
                    href = a["href"]
                    if href.startswith("http") and "medium.com" not in href:
                        if href not in external_links:
                            external_links.append(href)

                short_hash = hashlib.sha1(link.encode("utf-8")).hexdigest()[:10]
                results.append(
                    RawItem(
                        item_id=f"medium_{short_hash}",
                        source_type="medium",
                        source_name=f"Medium (#{tag})",
                        title=title,
                        url=link,
                        discussion_url=link,
                        summary_text=clean_text[:1800],
                        author=author,
                        external_links=external_links[:6],
                    )
                )
                if len(results) >= self.limit_per_tag:
                    break
        except Exception:
            pass
        return results
