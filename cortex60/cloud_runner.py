"""
Serverless Cloud Runner for Cortex60 + VeriPulse.
Designed to run on a 100% free GitHub Actions Cron schedule (or any cloud cron):
1. Polls Reddit, Medium, BBC, Ars Technica, Nature, and Hacker News via VeriPulse.
2. Cross-verifies stories, strips fluff, builds 4-Layer What/How/Why/Why/Why breakdowns, and injects them into Cortex60.
3. Synthesizes a Unified Cloud Briefing (Verified News + 4x15m Cognitive Enhancement Protocol with Full Answers).
4. Dispatches alerts to Telegram, Email (SMTP), and WhatsApp (Twilio/Meta).
5. Exports a static serverless web bundle (`docs/`) for free GitHub Pages hosting.
"""

from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
from cortex60.database import CortexDatabase
from cortex60.live_ingestor import ingest_live_verified_stories
from cortex60.logic_crucible import generate_crucible_problem
from cortex60.seed_data import INSIGHT_CONCEPTS, MENTAL_MODELS
from veripulse.formatter import format_chat_message, format_email_html
from veripulse.models import InterrogationLayer, SourceLink, VerificationStatus, VerifiedStory
from veripulse.notifiers import NotificationDispatcher

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = PROJECT_ROOT / "docs"
STATIC_DIR = Path(__file__).resolve().parent / "static"


def build_cognitive_protocol_story(db: CortexDatabase, live_stories: list[VerifiedStory]) -> VerifiedStory:
    """Builds the Daily 4x15-Minute Cognitive Enhancement Protocol card with COMPLETE Questions AND Answers."""
    day_of_year = datetime.now(timezone.utc).timetuple().tm_yday
    model = MENTAL_MODELS[day_of_year % len(MENTAL_MODELS)]
    cs = model["case_study"]
    concept = INSIGHT_CONCEPTS[day_of_year % len(INSIGHT_CONCEPTS)]
    c_q = concept["questions"][0]

    seq_puzzle = generate_crucible_problem(difficulty=2, preferred_type="sequence")
    seq_answer = seq_puzzle["options"][seq_puzzle["correct_index"]]

    srs_queue = db.get_srs_queue(limit=3)
    top_weak = srs_queue[0] if srs_queue else None

    lead_headline = live_stories[0].headline if live_stories else concept["title"]

    pointers = [
        f"📖 BLOCK 1 (Insight Engine • 15m): Deep-read today's {len(live_stories)} verified stories above + '{concept['title']}' (10m read, then 5m active recall).",
        f"🧩 BLOCK 2 (Logic Crucible • 15m): Fluid-IQ Sequence Challenge → {seq_puzzle['sequence_display']} | Choices: {', '.join(seq_puzzle['options'])}",
        f"⚙️ BLOCK 3 (Mental Model Re-Wiring • 15m): Apply '{model['name']}' to today's lead event: \"{lead_headline}\".",
        f"🔁 BLOCK 4 (Integration Loop SRS • 15m): Priority Weak-Concept Drill [{top_weak['domain_or_model'] if top_weak else concept['domain']}].",
    ]

    # 4 Complete Question + Answer Drill Layers for the 4 Cognitive Blocks
    protocol_layers = [
        InterrogationLayer(
            layer_tag="BLOCK 1 • THE INSIGHT ENGINE (15 MINS — QUESTION & VERIFIED ANSWER)",
            question=f"[{concept['domain']}] {c_q['question']}",
            answer=f"✅ ANSWER: {c_q['options'][c_q['correct_index']]} — {c_q['explanation']}",
        ),
        InterrogationLayer(
            layer_tag="BLOCK 2 • THE LOGIC CRUCIBLE (15 MINS — FLUID IQ PUZZLE & SOLUTION)",
            question=f"Deduce the 7th term in the sequence: {seq_puzzle['sequence_display']} (Choices: {', '.join(seq_puzzle['options'])})",
            answer=f"✅ ANSWER: {seq_answer} — {seq_puzzle['explanation']}",
        ),
        InterrogationLayer(
            layer_tag="BLOCK 3 • MENTAL MODEL RE-WIRING (15 MINS — CASE STUDY & SOLUTION)",
            question=f"[{model['name']}] {cs['application_question']}",
            answer=f"✅ ANSWER: {cs['application_options'][cs['application_correct']]} (Framework Principle: {model['summary']})",
        ),
        InterrogationLayer(
            layer_tag="BLOCK 4 • THE INTEGRATION LOOP (15 MINS — SPACED REPETITION QUESTION & ANSWER)",
            question=top_weak["question"] if top_weak else concept["questions"][2]["question"],
            answer=(
                f"✅ ANSWER: {top_weak['options'][top_weak['correct_index']]} — {top_weak['explanation']}"
                if top_weak
                else f"✅ ANSWER: {concept['questions'][2]['options'][concept['questions'][2]['correct_index']]} — {concept['questions'][2]['explanation']}"
            ),
        ),
    ]

    return VerifiedStory(
        item_id=f"cortex60_daily_{datetime.now(timezone.utc).strftime('%Y%m%d')}",
        category="CORTEX-60 PROTOCOL",
        headline=f"Daily 1-Hour Cognitive Enhancement Protocol & Answer Key ({model['name']})",
        verification_status=VerificationStatus.VERIFIED_MULTI_SOURCE,
        trust_score=99,
        quick_bite=(
            f"Your 60-minute daily cognitive workout is structured below into 4 × 15-minute blocks—complete with "
            f"today's active recall prompts and full step-by-step verified answers."
        ),
        important_pointers=pointers,
        interrogation_layers=protocol_layers,
        community_verification_notes=(
            "🧬 Biometric Neurogenesis Reminder: Log your 3 daily biological prerequisites (7–8h Sleep Quality, "
            "Cardio/Exercise, and Omega-3/Hydration) on the web dashboard to keep rolling 7-day compliance ≥ 70%."
        ),
        fluff_removed_reason="Structured into 4 × 15-minute neuro-targeted blocks with complete answer keys.",
        sources=[
            SourceLink(label="Launch Interactive Cortex60 Web App", url="https://kujodigital.github.io/cortex60/"),
            SourceLink(label="GitHub Cloud Automation Dashboard", url="https://github.com/kujodigital/cortex60/actions"),
        ],
    )


def export_static_cloud_bundle(db: CortexDatabase) -> Path:
    """Exports the Cortex60 web app + live bootstrap JSON to `docs/` for serverless GitHub Pages hosting."""
    DOCS_DIR.mkdir(parents=True, exist_ok=True)
    diff, streak = db.get_crucible_state()

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

    shutil.copy2(STATIC_DIR / "styles.css", DOCS_DIR / "styles.css")
    shutil.copy2(STATIC_DIR / "app.js", DOCS_DIR / "app.js")
    index_html = (STATIC_DIR / "index.html").read_text(encoding="utf-8")
    index_html = index_html.replace('href="/static/styles.css"', 'href="./styles.css"')
    index_html = index_html.replace('src="/static/app.js"', 'src="./app.js"')
    (DOCS_DIR / "index.html").write_text(index_html, encoding="utf-8")

    return DOCS_DIR


def run_cloud_pipeline(max_items: int = 4) -> dict:
    db = CortexDatabase()
    live_stories, live_modules = ingest_live_verified_stories(db, max_items=max_items, ignore_seen=False)
    protocol_card = build_cognitive_protocol_story(db, live_stories)
    all_cards = live_stories + [protocol_card]

    dispatcher = NotificationDispatcher()
    dispatch_results = dispatcher.dispatch(all_cards)

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
