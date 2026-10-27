from datetime import datetime, timezone
import re
import feedparser
import httpx
from bs4 import BeautifulSoup
from veripulse.models import RawItem

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) VeriPulseFactBot/1.0"


class RedditCollector:
    """Fetches high-signal Reddit posts AND top community verification comments."""

    def __init__(self, subreddits: list[str], limit_per_sub: int = 3):
        self.subreddits = subreddits
        self.limit_per_sub = limit_per_sub

    def fetch_all(self) -> list[RawItem]:
        items: list[RawItem] = []
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=12.0, follow_redirects=True) as client:
            for sub in self.subreddits:
                sub_items = self._fetch_subreddit(client, sub)
                items.extend(sub_items)
        return items

    def _fetch_subreddit(self, client: httpx.Client, subreddit: str) -> list[RawItem]:
        url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit={self.limit_per_sub + 4}"
        results: list[RawItem] = []
        try:
            resp = client.get(url)
            if resp.status_code == 200:
                data = resp.json()
                children = data.get("data", {}).get("children", [])
                for child in children:
                    post = child.get("data", {})
                    if post.get("stickied") or post.get("over_18"):
                        continue
                    post_id = post.get("id", "")
                    title = post.get("title", "").strip()
                    permalink = f"https://www.reddit.com{post.get('permalink', '')}"
                    article_url = post.get("url_overridden_by_dest") or post.get("url") or permalink
                    selftext = post.get("selftext", "").strip()
                    score = int(post.get("score", 0))
                    num_comments = int(post.get("num_comments", 0))

                    # Fetch top comments to see community fact-checking / context
                    top_comments = self._fetch_top_comments(client, post.get("permalink", ""))

                    results.append(
                        RawItem(
                            item_id=f"reddit_{post_id}",
                            source_type="reddit",
                            source_name=f"r/{subreddit}",
                            title=title,
                            url=article_url,
                            discussion_url=permalink,
                            summary_text=selftext[:1200] if selftext else f"External link shared on r/{subreddit}: {article_url}",
                            author=post.get("author", "unknown"),
                            score=score,
                            comments_count=num_comments,
                            top_comments=top_comments,
                            external_links=[article_url] if article_url != permalink else [],
                            published_at=datetime.fromtimestamp(
                                post.get("created_utc", datetime.now(timezone.utc).timestamp()),
                                tz=timezone.utc,
                            ),
                        )
                    )
                    if len(results) >= self.limit_per_sub:
                        break
                return results
        except Exception:
            pass

        # Fallback to Reddit RSS if JSON is rate-limited
        return self._fetch_subreddit_rss(client, subreddit)

    def _fetch_top_comments(self, client: httpx.Client, permalink: str, max_comments: int = 4) -> list[str]:
        if not permalink:
            return []
        try:
            resp = client.get(f"https://www.reddit.com{permalink}.json?limit=8&sort=top")
            if resp.status_code != 200:
                return []
            payload = resp.json()
            if not isinstance(payload, list) or len(payload) < 2:
                return []
            comment_children = payload[1].get("data", {}).get("children", [])
            comments: list[str] = []
            for c in comment_children:
                c_data = c.get("data", {})
                body = c_data.get("body", "").strip()
                author = c_data.get("author", "")
                if not body or body in ("[deleted]", "[removed]") or "AutoModerator" in author:
                    continue
                clean_body = re.sub(r"\s+", " ", body)[:450]
                score = c_data.get("score", 0)
                comments.append(f"[+{score} pts by u/{author}]: {clean_body}")
                if len(comments) >= max_comments:
                    break
            return comments
        except Exception:
            return []

    def _fetch_subreddit_rss(self, client: httpx.Client, subreddit: str) -> list[RawItem]:
        results: list[RawItem] = []
        try:
            resp = client.get(f"https://www.reddit.com/r/{subreddit}/hot/.rss")
            feed = feedparser.parse(resp.text)
            for entry in feed.entries:
                title = entry.get("title", "").strip()
                if "live thread" in title.lower() or "megathread" in title.lower():
                    continue
                soup = BeautifulSoup(entry.get("summary", ""), "html.parser")
                ext_links = [
                    a["href"]
                    for a in soup.find_all("a", href=True)
                    if "reddit.com" not in a["href"] and a["href"].startswith("http")
                ]
                if not ext_links:
                    continue
                primary_url = ext_links[0]
                results.append(
                    RawItem(
                        item_id=f"reddit_{entry.get('id', entry.get('link', ''))[-12:]}",
                        source_type="reddit",
                        source_name=f"r/{subreddit}",
                        title=title,
                        url=primary_url,
                        discussion_url=entry.get("link", ""),
                        summary_text="",
                        external_links=ext_links,
                    )
                )
                if len(results) >= self.limit_per_sub:
                    break
        except Exception:
            pass
        return results
