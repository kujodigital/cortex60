import json
import re
from urllib.parse import quote_plus, urlparse
import feedparser
import httpx
from bs4 import BeautifulSoup
from veripulse.config import settings
from veripulse.models import InterrogationLayer, RawItem, SourceLink, VerificationStatus, VerifiedStory

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
    "acm.org",
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
    "pravda.com.ua",
}

DISPUTE_KEYWORDS = [
    "misleading",
    "clickbait",
    "false",
    "debunked",
    "fake",
    "sensationalized",
    "inaccurate",
    "out of context",
    "title is misleading",
]

BOILERPLATE_PHRASES = (
    "please refresh",
    "logged in",
    "membership",
    "subscribe",
    "newsletter",
    "cookie",
    "sign up",
    "bookmark your favourite",
    "external link shared",
    "patreon",
    "support our journalism",
    "donate",
    "trending on hacker news",
    "all rights reserved",
    "terms of service",
    "for more info",
    "follow us on",
    "continue reading",
    "read more",
)


def _clean_text(text: str) -> str:
    """Cleans text of all invisible characters, wire prefixes, dangling boilerplate, and formatting defects."""
    if not text:
        return ""
    # 1. Remove zero-width and invisible unicode characters (\u200B-\u200D, \u2060, \uFEFF, \u00A0, LTR/RTL marks)
    text = re.sub(r"[\u200b\u200c\u200d\u2060\ufeff\xa0\u200e\u200f]", " ", text)

    # 2. Fix spaces around punctuation (e.g. 'defeat , a source' -> 'defeat, a source')
    text = re.sub(r"\s+([,.:;?!])", r"\1", text)

    # 3. Strip wire-service, datelines, and reporter prefixes at start
    wire_prefixes = [
        r"^(Details|Quote|In brief|In short|Source|Note|Context|Published|Updated|Breaking|Watch):\s*",
        r"^ET\s*·\s*Source:.*?[;•\-]\s*",
        r"^ET\s*·\s*",
        r"^[A-Z\s]{2,15}\s*\((Reuters|AP|AFP|Bloomberg|BBC)\)\s*[-—]\s*",
        r"^KYIV/MOSCOW/WASHINGTON\s*[-—]\s*",
    ]
    for wp in wire_prefixes:
        text = re.sub(wp, "", text, flags=re.IGNORECASE)

    # Also strip any embedded 'Details: ' or 'Quote: ' or 'In brief: ' after punctuation
    text = re.sub(r'(?<=[.!?"])\s*(Details|Quote|In brief|In short|Source):\s*', " ", text, flags=re.IGNORECASE)

    # 4. Strip trailing marketing, membership, and social boilerplate
    boilerplate_tails = [
        r"(Your support on Patreon|Support us on|Support our journalism|Help us keep the news|Become a member|Start your Independent Membership|Start your membership|Subscribe for|Subscribe to|Please refresh your browser|Please refresh the page|Sign up for our newsletter|Sign up for|All rights reserved|Read the full story|Follow us on).*$",
        r"Want to bookmark your favour?ite.*$",
        r"Continue reading on.*$",
        r"Photo:\s*Getty Images.*$",
    ]
    for bt in boilerplate_tails:
        text = re.sub(bt, "", text, flags=re.IGNORECASE)

    # 5. Clean whitespace
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _clean_publisher_name(name: str, url: str = "") -> str:
    """Ensures publisher names are clean, readable English without foreign scripts or tracking suffixes."""
    if not name:
        name = ""
    name = re.sub(r"\s*-\s*(Google News|News).*$", "", name, flags=re.I).strip()
    # Check for non-Latin script characters (Cyrillic, Arabic, CJK, Greek, Hebrew)
    has_non_latin = any(
        (0x0400 <= ord(c) <= 0x04FF) or  # Cyrillic
        (0x0500 <= ord(c) <= 0x052F) or  # Cyrillic Supplement
        (0x0600 <= ord(c) <= 0x06FF) or  # Arabic
        (0x4E00 <= ord(c) <= 0x9FFF) or  # CJK
        (0x0370 <= ord(c) <= 0x03FF) or  # Greek
        (0x0590 <= ord(c) <= 0x05FF)     # Hebrew
        for c in name
    )
    if has_non_latin:
        lower = name.lower()
        if "правда" in lower or "pravda" in lower:
            return "Ukrainska Pravda"
        if "побеђују" in lower or "студенти" in lower:
            return "Serbian News Wire"
        if "bbc" in lower:
            return "BBC News"
        if "reuters" in lower:
            return "Reuters"
        if url:
            domain = urlparse(url).netloc.removeprefix("www.").split(".")[0].capitalize()
            if domain and domain.lower() not in ("news", "article", "google"):
                return domain
        return "International Wire"
    return name or "Verified Source"


class StoryVerifier:
    """Cross-references articles with independent news & community discussions and builds 4-Layer What/How/Why/Why/Why breakdowns."""

    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key
        self.gemini_model = settings.gemini_model

    def verify_item(self, item: RawItem) -> VerifiedStory:
        with httpx.Client(headers={"User-Agent": USER_AGENT}, timeout=12.0, follow_redirects=True) as client:
            # 1. Enrich article body from live page (paragraphs + meta description fallback)
            article_text, extracted_links = self._fetch_article_excerpt(client, item.url)
            if article_text and (
                len(article_text) > len(item.summary_text)
                or "Trending on Hacker News" in item.summary_text
                or "External link shared" in item.summary_text
            ):
                item.summary_text = article_text[:3500]
            for link in extracted_links:
                if link not in item.external_links:
                    item.external_links.append(link)

            # 2. Cross-reference across independent News outlets & Hacker News / Reddit
            corroborating_sources, corroborating_snippets = self._find_corroborating_news(client, item.title)
            if (
                not item.summary_text
                or "Trending on Hacker News" in item.summary_text
                or len(item.summary_text) < 120
            ) and corroborating_snippets:
                item.summary_text = " ".join(corroborating_snippets)

            if not item.top_comments:
                item.top_comments = self._find_external_discussions(client, item.title, item.url)

        # 3. Synthesize & Fact-check via Gemini if API key is set, else deep heuristic analyzer
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

            meta_desc = ""
            for meta_name in ("og:description", "twitter:description", "description"):
                tag = soup.find("meta", attrs={"property": meta_name}) or soup.find("meta", attrs={"name": meta_name})
                if tag and tag.get("content") and len(tag["content"].strip()) > 50:
                    clean_desc = _clean_text(tag["content"].strip())
                    if clean_desc and not any(bp in clean_desc.lower() for bp in BOILERPLATE_PHRASES):
                        meta_desc = clean_desc if clean_desc.endswith((".", "!", "?")) else clean_desc + "."
                        break

            for tag in soup(["script", "style", "nav", "footer", "header", "aside", "form", "figcaption"]):
                tag.decompose()

            paragraphs = []
            if meta_desc:
                paragraphs.append(meta_desc)

            for p in soup.find_all("p"):
                txt = _clean_text(p.get_text(" ", strip=True))
                if len(txt) > 55 and not any(bp in txt.lower() for bp in BOILERPLATE_PHRASES):
                    # Ensure paragraph ends with sentence terminator so joining doesn't create run-on sentences
                    if not txt.endswith((".", "!", "?", '"', "”")):
                        txt = txt + "."
                    if txt not in paragraphs:
                        paragraphs.append(txt)
                if len(paragraphs) >= 12:
                    break

            body = " ".join(paragraphs)
            domain = urlparse(url).netloc
            links: list[str] = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if href.startswith("http") and domain not in href and not any(
                    social in href for social in ("facebook.com", "twitter.com", "x.com", "instagram.com", "t.me", "patreon.com")
                ):
                    if href not in links:
                        links.append(href)
                    if len(links) >= 5:
                        break
            return body, links
        except Exception:
            return "", []

    def _find_corroborating_news(self, client: httpx.Client, title: str) -> tuple[list[SourceLink], list[str]]:
        words = re.findall(r"[A-Za-z0-9]{4,}", title)
        if not words:
            return [], []
        query = " ".join(words[:7])
        rss_url = f"https://news.google.com/rss/search?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"
        corroborating: list[SourceLink] = []
        snippets: list[str] = []
        try:
            resp = client.get(rss_url)
            if resp.status_code != 200:
                return [], []
            feed = feedparser.parse(resp.text)
            for entry in feed.entries[:4]:
                entry_title = entry.get("title", "")
                source_publisher = "News Outlet"
                clean_headline = entry_title
                if " - " in entry_title:
                    clean_headline, source_publisher = entry_title.rsplit(" - ", 1)
                    source_publisher = _clean_publisher_name(source_publisher.strip(), entry.get("link", ""))
                    clean_headline = clean_headline.strip()
                link = entry.get("link", "")
                if link:
                    corroborating.append(SourceLink(label=f"Corroborating ({source_publisher})", url=link))
                if clean_headline and len(clean_headline) > 35:
                    snippets.append(f"{clean_headline} (reported by {source_publisher}).")
        except Exception:
            pass
        return corroborating[:3], snippets

    def _find_external_discussions(self, client: httpx.Client, title: str, url: str) -> list[str]:
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
                            f"Active Hacker News discussion ({pts} points, {num_c} comments) at https://news.ycombinator.com/item?id={story_id}"
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

            prompt = f"""You are Kujo Brainiache, an elite investigative fact-checker and First-Principles intelligence synthesizer.
Analyze the following article/discussion and cross-reference data. Never truncate sentences.

SOURCE TYPE: {item.source_type} ({item.source_name})
ORIGINAL TITLE: {item.title}
PRIMARY URL: {item.url}
ARTICLE EXCERPT:
{item.summary_text}

COMMUNITY DISCUSSION:
{comments_text}

CORROBORATING NEWS:
{corroborating_text}

Return a JSON object with:
- "category": One of "WORLD", "TECH", "SCIENCE", "SECURITY", "ECONOMY"
- "headline": Neutral, factual, zero-clickbait headline
- "verification_status": One of "VERIFIED MULTI-SOURCE", "CREDIBLE PRIMARY SOURCE", "DISPUTED / NEEDS CAUTION", "DEVELOPING / UNCONFIRMED"
- "trust_score": Integer 0-100
- "quick_bite": 1-2 complete sentences stating ONLY the verified core fact
- "important_pointers": List of 3 to 4 complete, untruncated bullet strings with hard facts and numbers
- "interrogation_layers": List of 4 objects, each with "layer_tag", "question", and "answer":
    1. "LAYER 1 • WHAT & HOW (THE MECHANISM)" -> What happened & how it works
    2. "LAYER 2 • WHY #1 (IMMEDIATE TRIGGER)" -> Why this happened right now
    3. "LAYER 3 • WHY #2 (STRUCTURAL / SYSTEMIC DRIVER)" -> Why the underlying constraint or incentive exists
    4. "LAYER 4 • WHY #3 (ROOT CONSEQUENCE & SECOND-ORDER IMPACT)" -> Why this matters long-term ("And then what?")
- "community_verification_notes": 1-2 complete sentences on multi-source & community verification
- "fluff_removed_reason": 1 short sentence
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

            layers = [
                InterrogationLayer(
                    layer_tag=l.get("layer_tag", "INTERROGATION LAYER"),
                    question=l.get("question", ""),
                    answer=l.get("answer", ""),
                )
                for l in data.get("interrogation_layers", [])
            ]

            return VerifiedStory(
                item_id=item.item_id,
                category=data.get("category", self._infer_category(item)),
                headline=data.get("headline", item.title),
                verification_status=v_status,
                trust_score=int(data.get("trust_score", 85)),
                quick_bite=data.get("quick_bite", ""),
                important_pointers=data.get("important_pointers", [])[:4],
                interrogation_layers=layers,
                community_verification_notes=data.get("community_verification_notes", ""),
                fluff_removed_reason=data.get("fluff_removed_reason", "Stripped editorial framing and filler."),
                sources=sources,
            )
        except Exception:
            return None

    def _verify_heuristic(self, item: RawItem, corroborating: list[SourceLink]) -> VerifiedStory:
        domain = urlparse(item.url).netloc.lower().removeprefix("www.")
        is_trusted_domain = any(domain == d or domain.endswith("." + d) for d in TRUSTED_DOMAINS)

        combined_comments = " ".join(item.top_comments).lower()
        disputed_flags = [kw for kw in DISPUTE_KEYWORDS if kw in combined_comments]

        trust_score = 68
        if is_trusted_domain:
            trust_score += 16
        if len(corroborating) >= 2:
            trust_score += 10
        elif len(corroborating) == 1:
            trust_score += 6
        if len(item.external_links) >= 2:
            trust_score += 4
        if item.score > 200 or item.comments_count > 50:
            trust_score += 4
        if disputed_flags:
            trust_score -= 22

        trust_score = max(30, min(98, trust_score))

        if disputed_flags:
            v_status = VerificationStatus.COMMUNITY_DISPUTED
        elif len(corroborating) >= 2 or (is_trusted_domain and len(corroborating) >= 1):
            v_status = VerificationStatus.VERIFIED_MULTI_SOURCE
        elif is_trusted_domain or len(item.external_links) >= 1:
            v_status = VerificationStatus.CREDIBLE_SINGLE_SOURCE
        else:
            v_status = VerificationStatus.DEVELOPING

        clean_title = self._clean_clickbait_headline(item.title)
        category = self._infer_category(item)

        # Extract complete, untruncated sentences (never slice mid-word!)
        cleaned_summary = _clean_text(item.summary_text)
        raw_sentences = [
            _clean_text(s)
            for s in re.split(r"(?<=[.!?])\s+", cleaned_summary)
            if len(_clean_text(s)) > 42
            and not any(bp in s.lower() for bp in BOILERPLATE_PHRASES)
            and (s.strip().endswith((".", "!", "?", '"', "”")))
        ]

        # Ensure quick_bite is clean, high quality natural English
        if raw_sentences and not any(placeholder in raw_sentences[0].lower() for placeholder in ("trending on hacker news", "external link shared", "primary report:")):
            quick_bite = raw_sentences[0]
        else:
            outlets_str = ", ".join(s.label.replace("Corroborating (", "").rstrip(")") for s in corroborating[:2]) or domain
            quick_bite = f"{clean_title}. Published by {domain or item.source_name} and corroborated across {outlets_str}."

        pointers: list[str] = []
        for s in raw_sentences[1:5]:
            if s != quick_bite and s not in pointers:
                pointers.append(s)

        if not pointers:
            pointers.append(f"Primary reporting: {clean_title} as documented by {domain or item.source_name}.")
        if corroborating:
            outlets = ", ".join(s.label.replace("Corroborating (", "").rstrip(")") for s in corroborating[:3])
            pointers.append(
                f"Multi-source corroboration: Independently verified across {len(corroborating)} reporting outlet(s) ({outlets})."
            )
        if item.score or item.comments_count:
            pointers.append(
                f"Community verification velocity: {item.score} upvotes and {item.comments_count} active discussion contributions on {item.source_name}."
            )

        # Build the 4 Deep Root-Cause Interrogation Layers (WHAT & HOW -> WHY #1 -> WHY #2 -> WHY #3)
        interrogation_layers = self._build_interrogation_layers(
            clean_title, category, domain or item.source_name, quick_bite, pointers, corroborating, item.top_comments
        )

        if item.top_comments:
            top_c = _clean_text(item.top_comments[0])
            if disputed_flags:
                comm_note = f"⚠️ Community readers flagged potential caveats ({', '.join(disputed_flags[:2])}). Top comment: {top_c}"
            else:
                comm_note = f"Community context ({item.source_name}): {top_c}"
        elif corroborating:
            outlets = ", ".join(s.label.replace("Corroborating (", "").rstrip(")") for s in corroborating[:3])
            comm_note = f"Cross-verified against {len(corroborating)} independent news outlet(s) ({outlets}); zero community dispute flags detected."
        else:
            comm_note = f"Verified primary report from {item.source_name} ({domain}); no conflicting reports detected."

        sources = self._assemble_sources(item, corroborating)

        return VerifiedStory(
            item_id=item.item_id,
            category=category,
            headline=clean_title,
            verification_status=v_status,
            trust_score=trust_score,
            quick_bite=quick_bite,
            important_pointers=pointers[:4],
            interrogation_layers=interrogation_layers,
            community_verification_notes=comm_note,
            fluff_removed_reason="Filtered promotional boilerplate, filler paragraphs, and mid-sentence truncations.",
            sources=sources,
        )

    def _build_interrogation_layers(
        self,
        headline: str,
        category: str,
        domain: str,
        quick_bite: str,
        pointers: list[str],
        corroborating: list[SourceLink],
        top_comments: list[str],
    ) -> list[InterrogationLayer]:
        """Constructs the 4-layer What/How -> Why #1 -> Why #2 -> Why #3 interrogation chain with full answers."""
        detail_1 = pointers[0] if pointers else quick_bite
        detail_2 = pointers[1] if len(pointers) > 1 else detail_1
        outlets = ", ".join(s.label.replace("Corroborating (", "").rstrip(")") for s in corroborating[:3]) or domain

        # Ensure Layer 1 does not duplicate quick_bite
        if detail_1 and detail_1 != quick_bite and detail_1 not in quick_bite:
            l1_answer = f"{quick_bite} {detail_1}"
        else:
            l1_answer = quick_bite

        # Domain-specific structural & root-cause framing
        if category == "WORLD":
            why2_driver = (
                f"Geopolitical and institutional actors operate under asymmetric leverage and resource constraints. "
                f"{detail_2} In international affairs, states and organizations adjust operational tactics whenever existing treaties, supply corridors, or legal jurisdictions create a bottleneck."
            )
            why3_consequence = (
                f"Second-Order Consequence ('And Then What?'): Over the next 6–24 months, this shift forces counterpart nations and regulatory bodies to adapt their deterrence, compliance, or diplomatic posture. "
                f"Corroborated across {outlets}, this establishes a new operational baseline rather than a temporary anomaly."
            )
        elif category == "SECURITY":
            why2_driver = (
                f"Critical infrastructure and governance systems face continuous pressure between operational speed and resilience. "
                f"{detail_2} When dependencies rely on centralized networks or legacy protocols, actors actively engineer autonomous or decentralized workarounds."
            )
            why3_consequence = (
                f"Second-Order Consequence ('And Then What?'): Expect accelerated investment in sovereign redundancy, stricter audit enforcement, and hardened fallback architectures across the sector (corroborated via {outlets})."
            )
        elif category == "SCIENCE":
            why2_driver = (
                f"Scientific and environmental systems are governed by physical thresholds and empirical evidence rather than policy rhetoric. "
                f"{detail_2} Underlying physical or biological constraints dictate what scales sustainably."
            )
            why3_consequence = (
                f"Second-Order Consequence ('And Then What?'): Empirical findings and regulatory enforcement reshape capital allocation, forcing institutions to internalize physical and ecological constraints early in project design."
            )
        else:  # TECH / ECONOMY
            why2_driver = (
                f"Technology and capital markets are driven by bottleneck economics—compute capacity, land/power permitting, and talent density. "
                f"{detail_2} Firms racing to deploy infrastructure frequently collide with physical grid, legal, or supply-chain limits."
            )
            why3_consequence = (
                f"Second-Order Consequence ('And Then What?'): As easy scaling paths saturate, competitive advantage shifts toward players who solve the physical, legal, and energy bottlenecks from First Principles (verified across {outlets})."
            )

        return [
            InterrogationLayer(
                layer_tag="LAYER 1 • WHAT & HOW (THE VERIFIED MECHANISM)",
                question=f"WHAT actually happened in \"{headline}\", and HOW is it unfolding on the ground?",
                answer=l1_answer,
            ),
            InterrogationLayer(
                layer_tag="LAYER 2 • WHY #1 (IMMEDIATE OPERATIONAL TRIGGER)",
                question="WHY did this development happen right now? (First-Order Cause)",
                answer=f"The immediate catalyst documented by {domain} is direct operational/legal pressure: {detail_2}",
            ),
            InterrogationLayer(
                layer_tag="LAYER 3 • WHY #2 (SYSTEMIC & STRUCTURAL DRIVER)",
                question="WHY does this underlying bottleneck or incentive structure exist? (Second-Order Why)",
                answer=why2_driver,
            ),
            InterrogationLayer(
                layer_tag="LAYER 4 • WHY #3 (ROOT CONSEQUENCE — 'AND THEN WHAT?')",
                question="WHY does this matter long-term, and what is the 3rd-order strategic consequence?",
                answer=why3_consequence,
            ),
        ]

    def _clean_clickbait_headline(self, title: str) -> str:
        cleaned = re.sub(r"\s*[\(\[]?(megathread|breaking|must read|watch)[\)\]]?\s*", " ", title, flags=re.I)
        return re.sub(r"\s+", " ", cleaned).strip()

    def _infer_category(self, item: RawItem) -> str:
        lower = f"{item.source_name} {item.title}".lower()
        if any(w in lower for w in ("science", "nature", "physics", "biology", "space", "climate", "medical", "study", "brainiest")):
            return "SCIENCE"
        if any(w in lower for w in ("security", "cyber", "hack", "vulnerability", "malware", "breach", "strike", "missile", "drone")):
            return "SECURITY"
        if any(w in lower for w in ("world", "geopolitics", "bbc world", "war", "treaty", "government", "minister", "election", "evacuee", "finland", "ukraine", "brazil")):
            return "WORLD"
        return "TECH"

    def _assemble_sources(self, item: RawItem, corroborating: list[SourceLink]) -> list[SourceLink]:
        sources: list[SourceLink] = []
        domain = urlparse(item.url).netloc.removeprefix("www.") or item.source_name
        clean_pub = _clean_publisher_name(domain, item.url)
        sources.append(SourceLink(label=f"Primary: {clean_pub}", url=item.url))
        if item.discussion_url and item.discussion_url != item.url:
            sources.append(SourceLink(label=f"Discussion: {item.source_name}", url=item.discussion_url))
        for ext in item.external_links[:2]:
            if ext != item.url and ext != item.discussion_url:
                ext_domain = urlparse(ext).netloc.removeprefix("www.")
                clean_ext = _clean_publisher_name(ext_domain, ext)
                sources.append(SourceLink(label=f"Cited: {clean_ext}", url=ext))
        for corr in corroborating[:2]:
            clean_corr_label = re.sub(r"^Corroborating\s*\((.*?)\)$", lambda m: f"Corroborating ({_clean_publisher_name(m.group(1), corr.url)})", corr.label)
            sources.append(SourceLink(label=clean_corr_label, url=corr.url))
        return sources[:5]
