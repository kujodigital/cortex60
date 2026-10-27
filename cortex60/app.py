"""FastAPI Application for Cortex60: 1-Hour Cognitive Enhancement App."""

from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from cortex60.database import CortexDatabase
from cortex60.live_ingestor import ingest_live_verified_stories
from cortex60.logic_crucible import generate_crucible_problem
from cortex60.seed_data import MENTAL_MODELS
from veripulse.notifiers import NotificationDispatcher

app = FastAPI(
    title="Cortex60: 1-Hour Cognitive Enhancement Engine",
    version="1.0.0",
)

STATIC_DIR = Path(__file__).resolve().parent / "static"
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

db = CortexDatabase()


class ScheduleTickRequest(BaseModel):
    block_num: int
    add_seconds: int
    mark_done: bool = False


class InsightSubmitRequest(BaseModel):
    concept_id: str
    reading_seconds: int
    answers: list[int]


class CrucibleAttemptRequest(BaseModel):
    puzzle_type: str
    difficulty: int
    is_correct: bool
    elapsed_sec: float


class MentalModelSubmitRequest(BaseModel):
    model_id: str
    fallacy_choice: int
    app_choice: int
    synthesis_text: str


class SRSReviewRequest(BaseModel):
    card_id: str
    chosen_index: int
    confidence_grade: int = 4


class BiometricUpdateRequest(BaseModel):
    day_iso: str
    sleep_quality: bool
    physical_activity: bool
    brain_nutrition: bool


@app.get("/")
def serve_spa() -> FileResponse:
    return FileResponse(STATIC_DIR / "index.html")


@app.get("/api/bootstrap")
def bootstrap_state() -> dict:
    diff, streak = db.get_crucible_state()
    return {
        "schedule": db.get_schedule_status(),
        "insights": db.get_all_insights(),
        "initial_crucible": generate_crucible_problem(difficulty=diff, preferred_type="matrix"),
        "crucible_state": {"difficulty": diff, "streak": streak},
        "mental_models": MENTAL_MODELS,
        "srs_queue": db.get_srs_queue(limit=10),
        "benchmarks": db.get_benchmarks(),
        "biometrics": db.get_biometrics_status(),
    }


@app.post("/api/live-ingest")
def trigger_live_ingest(max_items: int = 3, notify: bool = False) -> dict:
    stories, live_modules = ingest_live_verified_stories(db, max_items=max_items, ignore_seen=True)
    dispatch_status = {}
    if notify and stories:
        dispatcher = NotificationDispatcher()
        dispatch_status = dispatcher.dispatch(stories)
    return {
        "ingested_count": len(live_modules),
        "insights": db.get_all_insights(),
        "srs_queue": db.get_srs_queue(limit=10),
        "dispatch": dispatch_status,
    }


@app.post("/api/schedule/tick")
def tick_schedule(req: ScheduleTickRequest) -> dict:
    return {
        "schedule": db.update_block_timer(req.block_num, req.add_seconds, req.mark_done),
    }


@app.post("/api/block1/submit")
def submit_insight_recall(req: InsightSubmitRequest) -> dict:
    result = db.record_insight_submission(req.concept_id, req.reading_seconds, req.answers)
    return {
        "result": result,
        "schedule": db.get_schedule_status(),
        "benchmarks": db.get_benchmarks(),
        "srs_queue": db.get_srs_queue(limit=10),
    }


@app.get("/api/block2/problem")
def get_crucible_problem(puzzle_type: str | None = None) -> dict:
    diff, streak = db.get_crucible_state()
    problem = generate_crucible_problem(difficulty=diff, preferred_type=puzzle_type)
    return {
        "problem": problem,
        "crucible_state": {"difficulty": diff, "streak": streak},
    }


@app.post("/api/block2/submit")
def submit_crucible_attempt(req: CrucibleAttemptRequest) -> dict:
    update = db.record_crucible_attempt(
        req.puzzle_type, req.difficulty, req.is_correct, req.elapsed_sec
    )
    return {
        "update": update,
        "schedule": db.get_schedule_status(),
        "benchmarks": db.get_benchmarks(),
    }


@app.post("/api/block3/submit")
def submit_mental_model(req: MentalModelSubmitRequest) -> dict:
    result = db.record_mental_model_application(
        req.model_id, req.fallacy_choice, req.app_choice, req.synthesis_text
    )
    return {
        "result": result,
        "schedule": db.get_schedule_status(),
        "benchmarks": db.get_benchmarks(),
        "srs_queue": db.get_srs_queue(limit=10),
    }


@app.post("/api/block4/review")
def submit_srs_review(req: SRSReviewRequest) -> dict:
    review = db.record_srs_review(req.card_id, req.chosen_index, req.confidence_grade)
    return {
        "review": review,
        "srs_queue": db.get_srs_queue(limit=10),
        "schedule": db.get_schedule_status(),
        "benchmarks": db.get_benchmarks(),
    }


@app.post("/api/biometrics/checkin")
def update_biometrics(req: BiometricUpdateRequest) -> dict:
    return {
        "biometrics": db.update_biometric_checkin(
            req.day_iso, req.sleep_quality, req.physical_activity, req.brain_nutrition
        )
    }
