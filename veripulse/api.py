from fastapi import FastAPI, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from veripulse.formatter import format_email_html
from veripulse.watcher import VeriPulseEngine

app = FastAPI(
    title="VeriPulse API",
    description="Zero-Fluff Multi-Source News & Community Discussion Verification Engine",
    version="0.1.0",
)

engine = VeriPulseEngine()


class VerifyUrlRequest(BaseModel):
    url: str
    send_notifications: bool = False


@app.get("/", response_class=HTMLResponse)
def live_feed_dashboard() -> str:
    """Renders the latest verified stories in the clean zero-fluff card layout."""
    stories = engine.store.get_recent_stories(limit=20)
    if not stories:
        stories, _ = engine.run_cycle(max_items=4)
    return format_email_html(stories)


@app.get("/api/stories")
def list_verified_stories(limit: int = Query(15, ge=1, le=50)):
    stories = engine.store.get_recent_stories(limit=limit)
    return {"count": len(stories), "stories": stories}


@app.post("/api/scan")
def trigger_scan(ignore_seen: bool = False, max_items: int = 5):
    stories, dispatch_results = engine.run_cycle(ignore_seen=ignore_seen, max_items=max_items)
    return {
        "verified_count": len(stories),
        "dispatch": dispatch_results,
        "stories": stories,
    }


@app.post("/api/verify")
def verify_single_url(req: VerifyUrlRequest):
    story = engine.verify_single_url(req.url)
    dispatch_res = {}
    if req.send_notifications:
        dispatch_res = engine.dispatcher.dispatch([story])
    return {"story": story, "dispatch": dispatch_res}
