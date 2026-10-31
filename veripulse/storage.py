import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from veripulse.config import settings
from veripulse.models import InterrogationLayer, SourceLink, VerificationStatus, VerifiedStory


class StoryStore:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or settings.db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS seen_items (
                    item_id TEXT PRIMARY KEY,
                    url TEXT,
                    first_seen_at TEXT
                )
                """
            )
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS verified_stories (
                    item_id TEXT PRIMARY KEY,
                    category TEXT,
                    headline TEXT,
                    verification_status TEXT,
                    trust_score INTEGER,
                    quick_bite TEXT,
                    important_pointers_json TEXT,
                    interrogation_layers_json TEXT DEFAULT '[]',
                    community_verification_notes TEXT,
                    fluff_removed_reason TEXT,
                    sources_json TEXT,
                    created_at TEXT
                )
                """
            )
            # Ensure column exists if table was created earlier
            try:
                conn.execute("ALTER TABLE verified_stories ADD COLUMN interrogation_layers_json TEXT DEFAULT '[]'")
            except sqlite3.OperationalError:
                pass
            conn.commit()

    def is_seen(self, item_id: str, url: str = "") -> bool:
        with sqlite3.connect(self.db_path) as conn:
            cur = conn.execute(
                "SELECT 1 FROM seen_items WHERE item_id = ? OR (url != '' AND url = ?)",
                (item_id, url),
            )
            return cur.fetchone() is not None

    def mark_seen(self, item_id: str, url: str = "") -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO seen_items (item_id, url, first_seen_at) VALUES (?, ?, ?)",
                (item_id, url, datetime.now(timezone.utc).isoformat()),
            )
            conn.commit()

    def save_verified_story(self, story: VerifiedStory) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                """
                INSERT OR REPLACE INTO verified_stories (
                    item_id, category, headline, verification_status, trust_score,
                    quick_bite, important_pointers_json, interrogation_layers_json,
                    community_verification_notes, fluff_removed_reason, sources_json, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    story.item_id,
                    story.category,
                    story.headline,
                    story.verification_status.value,
                    story.trust_score,
                    story.quick_bite,
                    json.dumps(story.important_pointers),
                    json.dumps(
                        [
                            {
                                "layer_tag": l.layer_tag,
                                "question": l.question,
                                "answer": l.answer,
                            }
                            for l in story.interrogation_layers
                        ]
                    ),
                    story.community_verification_notes,
                    story.fluff_removed_reason,
                    json.dumps([{"label": s.label, "url": s.url} for s in story.sources]),
                    story.created_at.isoformat(),
                ),
            )
            conn.commit()

    def get_recent_stories(self, limit: int = 20) -> list[VerifiedStory]:
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            rows = conn.execute(
                "SELECT * FROM verified_stories ORDER BY created_at DESC LIMIT ?",
                (limit,),
            ).fetchall()

        stories: list[VerifiedStory] = []
        for row in rows:
            raw_sources = json.loads(row["sources_json"] or "[]")
            raw_layers = json.loads(row["interrogation_layers_json"] or "[]") if "interrogation_layers_json" in row.keys() else []
            stories.append(
                VerifiedStory(
                    item_id=row["item_id"],
                    category=row["category"],
                    headline=row["headline"],
                    verification_status=VerificationStatus(row["verification_status"]),
                    trust_score=int(row["trust_score"]),
                    quick_bite=row["quick_bite"],
                    important_pointers=json.loads(row["important_pointers_json"] or "[]"),
                    interrogation_layers=[
                        InterrogationLayer(
                            layer_tag=l["layer_tag"],
                            question=l["question"],
                            answer=l["answer"],
                        )
                        for l in raw_layers
                    ],
                    community_verification_notes=row["community_verification_notes"],
                    fluff_removed_reason=row["fluff_removed_reason"] or "",
                    sources=[SourceLink(label=s["label"], url=s["url"]) for s in raw_sources],
                    created_at=datetime.fromisoformat(row["created_at"]),
                )
            )
        return stories
