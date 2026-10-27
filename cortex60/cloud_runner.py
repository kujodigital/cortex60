"""
Serverless Cloud Runner for Cortex60 + VeriPulse.
Designed to run on a 100% free GitHub Actions Cron schedule (or any cloud cron):
1. Polls Reddit, Medium, BBC, Ars Technica, Nature, and Hacker News via VeriPulse.
2. Cross-verifies stories, strips fluff, and injects them into Cortex60 Block 1 & Block 4 SRS.
3. Synthesizes a Unified Cloud Briefing (Verified News + 4x15m Cognitive Enhancement Protocol).
4. Dispatches alerts to Telegram, Email (SMTP), and WhatsApp (Twilio/Meta).
5. Exports a static serverless web bundle (`docs/`) for free GitHub Pages hosting.
"""

from datetime import datetime, timezone
import html
import json
from pathlib import Path
import shutil
from cortex60.database import CortexDatabase
from cortex60.live_ingestor import ingest_live_verified_stories
from cortex60.logic_crucible import generate_crucible_problem
from cortex60.seed_data import MENTAL_MODELS
from veripulse.config import settings
from veripulse.formatter import format_chat_message, format_email_html, format_telegram_html
from veripulse.models import SourceLink, VerificationStatus, VerifiedStory
from veripulse.notifiers import NotificationDispatcher

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def build_cognitive_protocol_story(db: CortexDatabase, live_stories: list[VerifiedStory]) -> VerifiedStory:
    """Builds a companion VerifiedStory card containing today's 4x15-Minute Cognitive Enhancement Protocol."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    model = MENTAL_MODELS[day_of_year % len(MENTAL_MODELS)]
    seq_puzzle = generate_crucible_problem(difficulty=2, preferred_type="sequence")
    srs_queue = db.get_srs_queue(limit=3)
    top_weak = srs_queue[0] if srs_queue else None

    lead_headline = live_stories[0].headline if live_stories else "Global Semiconductor & Energy Chokepoints"

    pointers = [
        f"📖 BLOCK 1 (Insight Engine • 15m): Read today's {len(live_stories)} live verified briefing(s) above for 10m, then lock text for 5m Active Recall.",
        f"🧩 BLOCK 2 (Logic Crucible • 15m): Daily Fluid-IQ Sequence Challenge → {seq_puzzle['sequence_display']} (Options: {', '.join(seq_puzzle['options'])})",
        f"⚙️ BLOCK 3 (Mental Model Re-Wiring • 15m): Apply '{model['name']}' ({model['summary'][:110]}...) to today's lead story: \"{lead_headline}\".",
    ]
    if top_weak:
        pointers.append(
            f"🔁 BLOCK 4 (Integration Loop SRS • 15m): Priority Weak-Concept Recall [{top_weak['domain_or_model']}] → {top_weak['question'][:140]}"
        )

    return VerifiedStory(
        item_id=f"cortex60_daily_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        category="CORTEX-60 PROTOCOL",
        headline=f"Daily 1-Hour Cognitive Enhancement Protocol ({model['name']})",
        verification_status=VerificationStatus.VERIFIED_MULTI_SOURCE,
        trust_score=99,
        quick_bite=(
            f"Your 60-minute cognitive schedule is ready: 4 × 15-minute blocks combining today's {len(live_stories)} "
            f"live verified world/tech/science stories with Fluid IQ pattern recognition, '{model['name']}', and SM-2 Spaced Repetition."
        ),
        important_pointers=pointers,
        community_verification_notes=(
            f"Block 2 Answer Key: {seq_puzzle['options'][seq_puzzle['correct_index']]} ({seq_puzzle['explanation']}) | "
            f"Remember to log your 3 Daily Biometric Toggles (7–8h Sleep, Cardio, Omega-3/Hydration) to keep 7-day compliance ≥ 70%."
        ),
        fluff_removed_reason="Structured into 4 × 15-minute neuro-targeted blocks.",
        sources=[
            SourceLink(label="Block 1–4 Interactive Cortex60 Web App", url="https://github.com"),
        ],
    )


def export_static_cloud_bundle(db: CortexDatabase) -> Path:
    """Exports the Cortex60 web app + live bootstrap JSON to `docs/` for serverless GitHub Pages hosting."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    diff, streak = db.get_crucible_state()

    # Pre-generate problems for all 4 modalities so static serverless mode works interactively too
    static_problems = {
        mod: [generate_crucible_problem(difficulty=d, preferred_type=mod) for d in range(1, 6)]
        for mod in ("matrix", "sequence", "cryptogram", "spatial")
    }

    bootstrap_payload = {
        "schedule": db.get_schedule_status(),
        "insights": db.get_all_insights(),
        "initial_crucible": static_problems["matrix"][1],
        "crucible_state": {"difficulty": diff, "streak": streak},
        "mental_models": MENTAL_MODELS,
        "srs_queue": db.get_srs_queue(limit=12),
        "benchmarks": db.get_benchmarks(),
        "biometrics": db.get_biometrics_status(),
        "static_crucible_bank": static_problems,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
    }

    (DOCS_DIR / "api_bootstrap.json").write_text(
        json.dumps(bootstrap_payload, indent=2),
        encoding="utf-8",
    )

    # Copy static frontend files and rewrite /static/ paths for relative GitHub Pages compatibility
    shutil.copy2(STATIC_DIR / "styles.css", DOCS_DIR / "styles.css")
    shutil.copy2(STATIC_DIR / "app.js", DOCS_DIR / "app.js")
    index_html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    index_html = index_html.replace('href="/static/styles.css"', 'href="./styles.css"')
    index_html = index_html.replace('src="/static/app.js"', 'src="./app.js"')
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")

    return DOCS_DIR


def run_cloud_pipeline(max_items: int = 4) -> dict:
    db = CortexDatabase()
    live_stories, live_modules = ingest_live_verified_stories(db, max_items=max_items, ignore_seen=True)
    protocol_card = build_cognitive_protocol_story(db, live_stories)
    all_cards = live_stories + [protocol_card]

    dispatcher = NotificationDispatcher()
    dispatch_results = dispatcher.dispatch(all_cards)

    # Also save unified cloud briefing files
    (PROJECT_ROOT / "cloud_briefing.html").write_text(format_email_html(all_cards), encoding="utf-8")
    (PROJECT_ROOT / "cloud_briefing.md").write_text(
        ("\n\n---\n\n").join(format_chat_message(c) for c in all_cards),
        encoding="utf-8",
    )

    docs_path = export_static_cloud_bundle(db)
    return {
        "verified_stories_count": len(live_stories),
        "live_modules_injected": len(live_modules),
        "dispatch_results": dispatch_results,
        "static_bundle_dir": str(docs_path),
    }


if __name__ == "__main__":
    summary = run_cloud_pipeline(max_items=4)
    print(json.dumps(summary, indent=2))
