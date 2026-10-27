"""Bridges VeriPulse Live Multi-Source Verification into Cortex60's Block 1 (Insight Engine) & Block 4 (SRS)."""

import html
import json
from cortex60.database import CortexDatabase
from veripulse.models import VerifiedStory
from veripulse.watcher import VeriPulseEngine

CATEGORY_TO_DOMAIN = {
    "WORLD": "Politics/Economics",
    "ECONOMY": "Politics/Economics",
    "TECH": "Science/Tech",
    "SCIENCE": "Science/Tech",
    "SECURITY": "Science/Tech",
}


def convert_verified_story_to_insight(story: VerifiedStory) -> dict:
    """Transforms a VeriPulse VerifiedStory into a Cortex60 Block 1 Insight Module + 3-Tier Recall Questions."""
    e = html.escape
    domain = CATEGORY_TO_DOMAIN.get(story.category.upper(), "Science/Tech")
    pointers_html = "".join(f"<li>{e(p)}</li>" for p in story.important_pointers)
    sources_html = "".join(
        f'<li><a href="{e(s.url)}" target="_blank" rel="noopener" style="color:var(--accent-primary);">{e(s.label)}</a></li>'
        for s in story.sources
    )

    content_html = f"""
        <div style="margin-bottom:10px;">
            <span class="badge">{story.badge_emoji} {e(story.verification_status.value)} • Trust Score: {story.trust_score}/100</span>
        </div>
        <p><strong>⚡ Zero-Fluff Quick Bite:</strong> {e(story.quick_bite)}</p>
        <p><strong>📌 Verified Story Pointers:</strong></p>
        <ul>{pointers_html}</ul>
        <p><strong>🔍 Community &amp; Multi-Source Fact-Check:</strong> {e(story.community_verification_notes)}</p>
        <p><strong>📚 Verified Primary &amp; Corroborating Sources:</strong></p>
        <ul>{sources_html}</ul>
    """

    primary_source_label = story.sources[0].label if story.sources else "Primary Source"
    key_pointer = story.important_pointers[0] if story.important_pointers else story.quick_bite

    questions = [
        {
            "tier": "Foundational",
            "question": f"[Live Verified Recall] Regarding '{story.headline}', what was the verified core finding and primary source?",
            "options": [
                f"{story.quick_bite[:140]} (Source: {primary_source_label})",
                "The report was retracted due to fabricated data with 0 corroborating outlets.",
                "The event occurred exclusively in 19th-century maritime trade with no modern impact.",
                "No primary sources or community discussions were available to evaluate the claim.",
            ],
            "correct_index": 0,
            "explanation": f"Verified at {story.trust_score}/100 trust ({story.verification_status.value}) via {primary_source_label}.",
        },
        {
            "tier": "Intermediate",
            "question": f"[Epistemic & Fallacy Check] When evaluating live coverage of '{story.headline}', why is multi-source & community verification critical?",
            "options": [
                f"To filter out single-source sensationalism and verify key details ({key_pointer[:110]}...) against independent outlets.",
                "Because headlines on social media should always be accepted at 100% face value without reading the primary source.",
                "Because upvote velocity alone guarantees scientific truth regardless of primary citations.",
                "Because corroborating reports reduce factual accuracy.",
            ],
            "correct_index": 0,
            "explanation": f"Cross-check context: {story.community_verification_notes}",
        },
        {
            "tier": "Advanced",
            "question": f"[Second-Order Synthesis] Applying Second-Order Thinking ('And then what?') to '{story.headline}', what is the highest-signal analytical takeaway?",
            "options": [
                f"Trace how the verified factual shift ({story.quick_bite[:100]}...) alters incentives, resource bottlenecks, and institutional responses over the next 6–24 months.",
                "Assume all global actors will remain completely static and no downstream adaptation will occur.",
                "Focus only on the emotional framing of the headline rather than structural constraints.",
                "Ignore primary source evidence in favor of unverified speculation.",
            ],
            "correct_index": 0,
            "explanation": "Advanced synthesis requires mapping verified first-order facts onto second-order incentive and bottleneck shifts.",
        },
    ]

    word_count = max(180, len((story.quick_bite + " " + " ".join(story.important_pointers)).split()) * 3)
    return {
        "id": f"live_{story.item_id}",
        "domain": f"LIVE • {domain}",
        "title": f"[LIVE VERIFIED] {story.headline}",
        "reading_target_minutes": 10,
        "recall_target_minutes": 5,
        "word_count": word_count,
        "cross_disciplines": [story.category, "Multi-Source Verification", "Second-Order Analysis"],
        "content_html": content_html,
        "questions": questions,
        "trust_score": story.trust_score,
        "verification_status": story.verification_status.value,
    }


def ingest_live_verified_stories(db: CortexDatabase, max_items: int = 4, ignore_seen: bool = True) -> tuple[list[VerifiedStory], list[dict]]:
    """Polls Reddit, Medium, BBC, and Hacker News via VeriPulse and injects verified modules into Cortex60."""
    vp_engine = VeriPulseEngine()
    stories, _ = vp_engine.run_cycle(ignore_seen=ignore_seen, max_items=max_items)
    live_modules = [convert_verified_story_to_insight(s) for s in stories]

    # Persist into CortexDatabase so Block 1 & Block 4 SRS immediately include these live verified concepts
    with db._connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS live_insights (
                id TEXT PRIMARY KEY,
                payload_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        for mod in live_modules:
            conn.execute(
                "INSERT OR REPLACE INTO live_insights (id, payload_json) VALUES (?, ?)",
                (mod["id"], json.dumps(mod)),
            )
            for idx, q in enumerate(mod["questions"]):
                card_id = f"srs_{mod['id']}_q{idx}"
                conn.execute(
                    """
                    INSERT OR REPLACE INTO srs_cards (
                        card_id, source_block, domain_or_model, tier, question,
                        options_json, correct_index, explanation, ease_factor, is_weak
                    ) VALUES (?, 'BLOCK_1', ?, ?, ?, ?, ?, ?, 2.3, ?)
                    """,
                    (
                        card_id,
                        mod["domain"],
                        q["tier"],
                        q["question"],
                        json.dumps(q["options"]),
                        q["correct_index"],
                        q["explanation"],
                        1 if idx == 2 else 0,
                    ),
                )
        conn.commit()

    return stories, live_modules
