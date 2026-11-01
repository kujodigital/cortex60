import hashlib
import re
import feedparser
import httpx
from bs4 import BeautifulSoup
from veripulse.models import RawItem

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) VeriPulseFactBot/1.0"


class NewsAndHNCollector:
    """Fetches major verified news feeds (BBC, Ars Technica, Nature) and Hacker News discussions."""

    def __init__(self, feeds: dict[str, str], limit_per_feed: int = 2, hn_limit: int = 3):
        self.feeds = feeds
        self.limit_per_feed = limit_per_feed
        self.hn_limit = hn_limit

    def fetch_all(self) -> list[RawItem]:
        items: list[RawItem] = []
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=12.0, follow_redirects=True) as client:
            for source_name, rss_url in self.feeds.items():
                items.extend(self._fetch_rss_feed(client, source_name, rss_url))
            items.extend(self._fetch_hackernews_frontpage(client))
        return items

    def _fetch_rss_feed(self, client: httpx.Client, source_name: str, rss_url: str) -> list[RawItem]:
        results: list[RawItem] = []
        try:
            resp = client.get(rss_url)
            if resp.status_code != 200:
                return []
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[: self.limit_per_feed]:
                link = entry.get("link", "").strip()
                title = entry.get("title", "").strip()
                raw_summary = entry.get("summary", "") or entry.get("description", "")
                clean_summary = BeautifulSoup(raw_summary, "html.parser").get_text(" ", strip=True)
                short_hash = hashlib.sha1(link.encode("utf-8")).hexdigest()[:10]
                results.append(
                    RawItem(
                        item_id=f"news_{short_hash}",
                        source_type="news",
                        source_name=source_name,
                        title=title,
                        url=link,
                        discussion_url="",
                        summary_text=clean_summary[:1200],
                        external_links=[link],
                    )
                )
        except Exception:
            pass
        return results

    def _fetch_hackernews_frontpage(self, client: httpx.Client) -> list[RawItem]:
        results: list[RawItem] = []
        try:
            resp = client.get(f"https://hn.algolia.com/api/v1/search?tags=front_page&hitsPerPage={self.hn_limit}")
            if resp.status_code != 200:
                return []
            hits = resp.json().get("hits", [])
            for hit in hits:
                object_id = hit.get("objectID", "")
                title = hit.get("title", "").strip()
                hn_url = f"https://news.ycombinator.com/item?id={object_id}"
                article_url = hit.get("url") or hn_url
                points = int(hit.get("points") or 0)
                num_comments = int(hit.get("num_comments") or 0)
                top_comments = self._fetch_hn_comments(client, object_id)

                # Synthesize informative English summary from discussion instead of a bare placeholder
                comment_snippets = " ".join(re.sub(r"^\[HN\s*@[^\]]+\]:\s*", "", c) for c in top_comments[:2])
                if comment_snippets:
                    summary_text = f"Analysis regarding {title}. Technical and community discussion highlights: {comment_snippets}"
                else:
                    summary_text = f"Reporting and analysis regarding {title} across technical publications and industry discussion."

                results.append(
                    RawItem(
                        item_id=f"hn_{object_id}",
                        source_type="hackernews",
                        source_name="Hacker News",
                        title=title,
                        url=article_url,
                        discussion_url=hn_url,
                        summary_text=summary_text,
                        author=hit.get("author", ""),
                        score=points,
                        comments_count=num_comments,
                        top_comments=top_comments,
                        external_links=[article_url] if article_url != hn_url else [],
                    )
                )
        except Exception:
            pass
        return results

    def _fetch_hn_comments(self, client: httpx.Client, story_id: str, max_comments: int = 3) -> list[str]:
        try:
            resp = client.get(f"https://hn.algolia.com/api/v1/items/{story_id}")
            if resp.status_code != 200:
                return []
            children = resp.json().get("children", [])
            comments: list[str] = []
            for child in children:
                raw_text = child.get("text") or ""
                if not raw_text:
                    continue
                clean = BeautifulSoup(raw_text, "html.parser").get_text(" ", strip=True)
                clean = re.sub(r"\s+", " ", clean)[:420]
                author = child.get("author", "hn_user")
                if len(clean) > 40:
                    comments.append(f"[HN @{author}]: {clean}")
                if len(comments) >= max_comments:
                    break
            return comments
        except Exception:
            return []
