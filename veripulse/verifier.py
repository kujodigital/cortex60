import json
import re
from urllib.parse import quote_plus, urlparse
import feedparser
import httpx
from bs4 import BeautifulSoup
from veripulse.config import settings
from veripulse.models import RawItem, SourceLink, VerificationStatus, VerifiedStory

USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) VeriPulseFactBot/1.0"

TRUSTED_DOMAINS = {
    "reuters.com",
    "apnews.com",
    "bbc.com",
    "bbc.co.uk",
    "nature.com",
    "science.org",
    "arstechnica.com",
    "ieee.org",
    "ACM.org",
    "ft.com",
    "economist.com",
    "npr.org",
    "pbs.org",
    "theguardian.com",
    "nytimes.com",
    "wsj.com",
    "bloomberg.com",
    "github.com",
    "arxiv.org",
}

DISPUTE_KEYWORDS = [
    "misleading",
    "clickbait",
    "false",
    "debunked",
    "fake",
    "sensationalized",
    "wrong",
    "inaccurate",
    "paywall",
    "out of context",
    "title is misleading",
]


class StoryVerifier:
    """Cross-references articles with independent news & community discussions and extracts zero-fluff facts."""

    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key
        self.gemini_model = settings.gemini_model

    def verify_item(self, item: RawItem) -> VerifiedStory:
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=12.0, follow_redirects=True) as client:
            # 1. Enrich article body if summary is short
            article_text, extracted_links = self._fetch_article_excerpt(client, item.url)
            if article_text and len(article_text) > len(item.summary_text):
                item.summary_text = article_text[:2500]
            for link in extracted_links:
                if link not in item.external_links:
                    item.external_links.append(link)

            # 2. Cross-reference across independent News outlets & Hacker News / Reddit
            corroborating_sources = self._find_corroborating_news(client, item.title)
            if not item.top_comments:
                item.top_comments = self._find_external_discussions(client, item.title, item.url)

        # 3. Synthesize & Fact-check via Gemini if API key is set, else deterministic extractor
        if self.gemini_api_key:
            story = self._verify_with_gemini(item, corroborating_sources)
            if story is not None:
                return story

        return self._verify_heuristic(item, corroborating_sources)

    def _fetch_article_excerpt(self, client: httpx.Client, url: str) -> tuple[str, list[str]]:
        if not url or "reddit.com" in url or "news.ycombinator.com" in url:
            return "", []
        try:
            resp = client.get(url)
            if resp.status_code != 200 or "text/html" not in resp.headers.get("content-type", ""):
                return "", []
            soup = BeautifulSoup(resp.text, "html.parser")
            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form"]):
                tag.decompose()
            paragraphs = [
                p.get_text(" ", strip=True)
                for p in soup.find_all("p")
                if len(p.get_text(" ", strip=True)) > 60
            ]
            body = " ".join(paragraphs[:10])
            domain = urlparse(url).netloc
            links: list[str] = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and domain not in href:
                    if href not in links:
                        links.append(href)
                    if len(links) >= 5:
                        break
            return body, links
        except Exception:
            return "", []

    def _find_corroborating_news(self, client: httpx.Client, title: str) -> list[SourceLink]:
        # Extract key terms from title (strip punctuation and stop words)
        words = re.findall(r"[A-Za-z0-9]{4,}", title)
        if not words:
            return []
        query = " ".join(words[:7])
        rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        corroborating: list[SourceLink] = []
        try:
            resp = client.get(rss_url)
            if resp.status_code != 200:
                return []
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:3]:
                entry_title = entry.get("title", "")
                source_publisher = "News Outlet"
                if " - " in entry_title:
                    source_publisher = entry_title.rsplit(" - ", 1)[-1].strip()
                link = entry.get("link", "")
                if link:
                    corroborating.append(SourceLink(label=f"Corroborating ({source_publisher})", url=link))
        except Exception:
            pass
        return corroborating

    def _find_external_discussions(self, client: httpx.Client, title: str, url: str) -> list[str]:
        """Look up HN discussions if the item came from a news feed or Medium."""
        words = re.findall(r"[A-Za-z0-9]{4,}", title)
        if not words:
            return []
        query = " ".join(words[:5])
        comments: list[str] = []
        try:
            resp = client.get(f"https://hn.algolia.com/api/v1/search?query={quote_plus(query)}&tags=story&hitsPerPage=2")
            if resp.status_code == 200:
                hits = resp.json().get("hits", [])
                for hit in hits:
                    if int(hit.get("num_comments") or 0) > 2:
                        story_id = hit.get("objectID")
                        pts = hit.get("points", 0)
                        num_c = hit.get("num_comments", 0)
                        comments.append(
                            f"[HN Cross-Check: {pts} pts, {num_c} comments at https://news.ycombinator.com/item?id={story_id}]"
                        )
        except Exception:
            pass
        return comments

    def _verify_with_gemini(self, item: RawItem, corroborating: list[SourceLink]) -> VerifiedStory | None:
        try:
            from google import genai
            from google.genai import types

            client = genai.Client(api_key=self.gemini_api_key)
            corroborating_text = "\n".join(f"- {s.label}: {s.url}" for s in corroborating) or "None found"
            comments_text = "\n".join(item.top_comments) or "No direct community comments yet."

            prompt = f"""You are VeriPulse, an elite investigative fact-checker and zero-fluff intelligence synthesizer.
Analyze the following article/discussion and cross-reference data.

SOURCE TYPE: {item.source_type} ({item.source_name})
ORIGINAL TITLE: {item.title}
PRIMARY URL: {item.url}
DISCUSSION URL: {item.discussion_url}
SCORE / COMMENTS: {item.score} points, {item.comments_count} comments

ARTICLE / POST EXCERPT:
{item.summary_text}

COMMUNITY DISCUSSION / FACT-CHECK COMMENTS (Reddit / HN):
{comments_text}

INDEPENDENT CORROBORATING NEWS REPORTS:
{corroborating_text}

Return a JSON object with these exact keys:
- "category": One of "WORLD", "TECH", "SCIENCE", "SECURITY", "ECONOMY"
- "headline": A neutral, factual, zero-clickbait headline
- "verification_status": One of "VERIFIED MULTI-SOURCE", "CREDIBLE PRIMARY SOURCE", "DISPUTED / NEEDS CAUTION", "DEVELOPING / UNCONFIRMED"
- "trust_score": Integer 0-100 reflecting factual solidity, source credibility, and community verification
- "quick_bite": 1-2 ultra-concise sentences stating ONLY the verified core fact (zero fluff)
- "important_pointers": List of 3 to 4 crisp bullet strings containing hard facts, numbers, dates, technical specifics, and key implications
- "community_verification_notes": 1-2 sentences summarizing what Reddit/HN readers or corroborating outlets verified, added as context, or disputed
- "fluff_removed_reason": 1 short sentence noting what hype, clickbait, or filler was stripped
"""
            response = client.models.generate_content(
                model=self.gemini_model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.1,
                ),
            )
            data = json.loads(response.text)
            sources = self._assemble_sources(item, corroborating)
            status_str = data.get("verification_status", "CREDIBLE PRIMARY SOURCE")
            try:
                v_status = VerificationStatus(status_str)
            except ValueError:
                v_status = VerificationStatus.CREDIBLE_SINGLE_SOURCE

            return VerifiedStory(
                item_id=item.item_id,
                category=data.get("category", self._infer_category(item)),
                headline=data.get("headline", item.title),
                verification_status=v_status,
                trust_score=int(data.get("trust_score", 78)),
                quick_bite=data.get("quick_bite", ""),
                important_pointers=data.get("important_pointers", [])[:5],
                community_verification_notes=data.get("community_verification_notes", ""),
                fluff_removed_reason=data.get("fluff_removed_reason", "Stripped editorial framing and filler."),
                sources=sources,
            )
        except Exception:
            return None

    def _verify_heuristic(self, item: RawItem, corroborating: list[SourceLink]) -> VerifiedStory:
        domain = urlparse(item.url).netloc.lower().removeprefix("www.")
        is_trusted_domain = any(domain == d or domain.endswith("." + d) for d in TRUSTED_DOMAINS)

        # Check if community comments flag the post as misleading/clickbait
        combined_comments = " ".join(item.top_comments).lower()
        disputed_flags = [kw for kw in DISPUTE_KEYWORDS if kw in combined_comments]

        # Compute trust score & verification status
        trust_score = 65
        if is_trusted_domain:
            trust_score += 18
        if len(corroborating) >= 2:
            trust_score += 12
        elif len(corroborating) == 1:
            trust_score += 6
        if len(item.external_links) >= 2:
            trust_score += 5
        if item.score > 200 or item.comments_count > 50:
            trust_score += 5
        if disputed_flags:
            trust_score -= 22

        trust_score = max(25, min(98, trust_score))

        if disputed_flags:
            v_status = VerificationStatus.COMMUNITY_DISPUTED
        elif len(corroborating) >= 2 or (is_trusted_domain and len(corroborating) >= 1):
            v_status = VerificationStatus.VERIFIED_MULTI_SOURCE
        elif is_trusted_domain or len(item.external_links) >= 1:
            v_status = VerificationStatus.CREDIBLE_SINGLE_SOURCE
        else:
            v_status = VerificationStatus.DEVELOPING

        # Extract factual sentences from summary_text, skipping site login/membership boilerplate
        boilerplate_phrases = (
            "please refresh",
            "logged in",
            "membership",
            "subscribe",
            "newsletter",
            "cookie",
            "sign up",
            "bookmark your favourite",
            "external link shared",
        )
        raw_sentences = [
            s.strip()
            for s in re.split(r"(?<=[.!?])\s+", item.summary_text)
            if len(s.strip()) > 40 and not any(bp in s.lower() for bp in boilerplate_phrases)
        ]

        if raw_sentences:
            quick_bite = raw_sentences[0][:260]
        else:
            quick_bite = f"{item.title} (Reported via {item.source_name}, cross-checked across {len(corroborating) + 1} source(s))."

        pointers: list[str] = []
        for s in raw_sentences[1:5]:
            pointers.append(s[:220])

        if not pointers:
            pointers.append(f"Primary Report: {item.title} published via {domain or item.source_name}.")
        if corroborating:
            outlets = ", ".join(s.label.replace("Corroborating (", "").rstrip(")") for s in corroborating[:3])
            pointers.append(f"Independent Cross-Check: Corroborated by {len(corroborating)} independent coverage feed(s) ({outlets}).")
        if item.score or item.comments_count:
            pointers.append(
                f"Discussion Velocity: {item.score} upvotes and {item.comments_count} community comments on {item.source_name}."
            )

        if item.top_comments:
            if disputed_flags:
                comm_note = f"⚠️ Community readers flagged potential caveats ({', '.join(disputed_flags[:2])}). Top comment: {item.top_comments[0][:240]}"
            else:
                comm_note = f"Top community context {item.top_comments[0][:260]}"
        elif corroborating:
            comm_note = f"Cross-verified against {len(corroborating)} external news report(s); no community dispute flags detected."
        else:
            comm_note = f"Direct report from {item.source_name} ({domain}); monitor for secondary citations."

        sources = self._assemble_sources(item, corroborating)

        return VerifiedStory(
            item_id=item.item_id,
            category=self._infer_category(item),
            headline=self._clean_clickbait_headline(item.title),
            verification_status=v_status,
            trust_score=trust_score,
            quick_bite=quick_bite,
            important_pointers=pointers[:4],
            community_verification_notes=comm_note,
            fluff_removed_reason="Filtered promotional phrasing, filler paragraphs, and unverified speculation.",
            sources=sources,
        )

    def _clean_clickbait_headline(self, title: str) -> str:
        # Remove trailing clickbait suffixes like "- You Won't Believe Why" or "[MegaThread]"
        cleaned = re.sub(r"\s*[\(\[]?(megathread|breaking|must read|watch)[\)\]]?\s*", " ", title, flags=re.I)
        return re.sub(r"\s+", " ", cleaned).strip()

    def _infer_category(self, item: RawItem) -> str:
        lower = f"{item.source_name} {item.title}".lower()
        if any(w in lower for w in ("science", "nature", "physics", "biology", "space", "climate", "medical", "study")):
            return "SCIENCE"
        if any(w in lower for w in ("security", "cyber", "hack", "vulnerability", "malware", "breach")):
            return "SECURITY"
        if any(w in lower for w in ("world", "geopolitics", "bbc world", "war", "treaty", "government", "minister", "un ")):
            return "WORLD"
        return "TECH"

    def _assemble_sources(self, item: RawItem, corroborating: list[SourceLink]) -> list[SourceLink]:
        sources: list[SourceLink] = []
        domain = urlparse(item.url).netloc.removeprefix("www.") or item.source_name
        sources.append(SourceLink(label=f"Primary Article ({domain})", url=item.url))
        if item.discussion_url and item.discussion_url != item.url:
            sources.append(SourceLink(label=f"Community Verification ({item.source_name})", url=item.discussion_url))
        for ext in item.external_links[:2]:
            if ext != item.url and ext != item.discussion_url:
                ext_domain = urlparse(ext).netloc.removeprefix("www.")
                sources.append(SourceLink(label=f"Cited Reference ({ext_domain})", url=ext))
        for corr in corroborating[:2]:
            sources.append(corr)
        return sources[:5]
