"""SQLite Persistence & Cognitive Telemetry Engine for Cortex60."""

from datetime import date, datetime, timedelta, timezone
import json
from pathlib import Path
import sqlite3
from cortex60.seed_data import INSIGHT_CONCEPTS, MENTAL_MODELS

DB_PATH = Path(__file__).resolve().parent.parent / "cortex60.db"


class CortexDatabase:
    def __init__(self, db_path: Path | None = None):
        self.db_path = db_path or DB_PATH
        self._init_schema()
        self._seed_if_empty()

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.executescript(
                """
                CREATE TABLE IF NOT EXISTS daily_schedule (
                    day_iso TEXT PRIMARY KEY,
                    block1_seconds INTEGER DEFAULT 0,
                    block2_seconds INTEGER DEFAULT 0,
                    block3_seconds INTEGER DEFAULT 0,
                    block4_seconds INTEGER DEFAULT 0,
                    block1_done INTEGER DEFAULT 0,
                    block2_done INTEGER DEFAULT 0,
                    block3_done INTEGER DEFAULT 0,
                    block4_done INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS srs_cards (
                    card_id TEXT PRIMARY KEY,
                    source_block TEXT NOT NULL, -- 'BLOCK_1' or 'BLOCK_3'
                    domain_or_model TEXT NOT NULL,
                    tier TEXT NOT NULL, -- 'Foundational', 'Intermediate', 'Advanced'
                    question TEXT NOT NULL,
                    options_json TEXT NOT NULL,
                    correct_index INTEGER NOT NULL,
                    explanation TEXT NOT NULL,
                    ease_factor REAL DEFAULT 2.5,
                    interval_days INTEGER DEFAULT 0,
                    repetitions INTEGER DEFAULT 0,
                    is_weak INTEGER DEFAULT 0,
                    last_reviewed TEXT,
                    next_review_ts REAL DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS telemetry_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event_type TEXT NOT NULL,
                    tier TEXT NOT NULL,
                    is_correct INTEGER DEFAULT 0,
                    wpm REAL DEFAULT 0,
                    score REAL DEFAULT 0,
                    difficulty INTEGER DEFAULT 1,
                    details TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS biometric_logs (
                    day_iso TEXT PRIMARY KEY,
                    sleep_quality INTEGER DEFAULT 0,
                    physical_activity INTEGER DEFAULT 0,
                    brain_nutrition INTEGER DEFAULT 0,
                    updated_at TEXT
                );

                CREATE TABLE IF NOT EXISTS user_state (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS live_insights (
                    id TEXT PRIMARY KEY,
                    payload_json TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
                """
            )
            conn.commit()

    def get_all_insights(self) -> list[dict]:
        """Returns the 6 core domain insights plus any live verified insights from VeriPulse."""
        with self._connect() as conn:
            rows = conn.execute("SELECT payload_json FROM live_insights ORDER BY created_at DESC LIMIT 6").fetchall()
        live_list = [json.loads(r["payload_json"]) for r in rows]
        return INSIGHT_CONCEPTS + live_list

    def _seed_if_empty(self) -> None:
        today = date.today().isoformat()
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO daily_schedule (day_iso) VALUES (?)", (today,))
            conn.execute("INSERT OR IGNORE INTO user_state (key, value) VALUES ('crucible_difficulty', '2')")
            conn.execute("INSERT OR IGNORE INTO user_state (key, value) VALUES ('crucible_streak', '0')")

            # Seed SRS cards from Block 1 and Block 3 if table is empty
            count = conn.execute("SELECT COUNT(*) AS c FROM srs_cards").fetchone()["c"]
            if count == 0:
                for concept in INSIGHT_CONCEPTS:
                    for idx, q in enumerate(concept["questions"]):
                        card_id = f"srs_{concept['id']}_q{idx}"
                        # Flag a couple of initial concepts as weak so Block 4 immediately shows weak-concept prioritization
                        is_weak = 1 if idx == 2 and concept["id"] in ("insight_hist_geo_01", "insight_pol_econ_03") else 0
                        conn.execute(
                            """
                            INSERT INTO srs_cards (
                                card_id, source_block, domain_or_model, tier, question,
                                options_json, correct_index, explanation, ease_factor, is_weak
                            ) VALUES (?, 'BLOCK_1', ?, ?, ?, ?, ?, ?, ?, ?)
                            """,
                            (
                                card_id,
                                concept["domain"],
                                q["tier"],
                                q["question"],
                                json.dumps(q["options"]),
                                q["correct_index"],
                                q["explanation"],
                                1.9 if is_weak else 2.5,
                                is_weak,
                            ),
                        )

                for model in MENTAL_MODELS:
                    cs = model["case_study"]
                    card_id_f = f"srs_{model['id']}_fallacy"
                    conn.execute(
                        """
                        INSERT INTO srs_cards (
                            card_id, source_block, domain_or_model, tier, question,
                            options_json, correct_index, explanation, ease_factor, is_weak
                        ) VALUES (?, 'BLOCK_3', ?, 'Intermediate', ?, ?, ?, ?, 2.1, 1)
                        """,
                        (
                            card_id_f,
                            model["name"],
                            f"[{model['name']}] {cs['fallacy_question']}",
                            json.dumps(cs["fallacy_options"]),
                            cs["fallacy_correct"],
                            f"Mental Model Framework: {model['summary']}",
                        ),
                    )
                    card_id_a = f"srs_{model['id']}_app"
                    conn.execute(
                        """
                        INSERT INTO srs_cards (
                            card_id, source_block, domain_or_model, tier, question,
                            options_json, correct_index, explanation, ease_factor, is_weak
                        ) VALUES (?, 'BLOCK_3', ?, 'Advanced', ?, ?, ?, ?, 2.3, 0)
                        """,
                        (
                            card_id_a,
                            model["name"],
                            f"[{model['name']} Application] {cs['application_question']}",
                            json.dumps(cs["application_options"]),
                            cs["application_correct"],
                            f"Applied {model['name']} to: {cs['title']}",
                        ),
                    )

            # Seed realistic initial telemetry so the 3 Benchmark Tiers show meaningful starting baselines
            t_count = conn.execute("SELECT COUNT(*) AS c FROM telemetry_events").fetchone()["c"]
            if t_count == 0:
                now_str = datetime.now(timezone.utc).isoformat()
                seed_events = [
                    ("insight_recall", "Foundational", 1, 245.0, 88.0, 2, "Malacca 1511 & Jakarta recall", now_str),
                    ("insight_recall", "Intermediate", 1, 260.0, 84.0, 2, "Fallacy identification + reading velocity", now_str),
                    ("model_synthesis", "Advanced", 1, 0.0, 82.0, 3, "Cross-disciplinary synthesis: Triffin & supply chains", now_str),
                    ("crucible_solve", "Foundational", 1, 0.0, 90.0, 2, "Matrix Reasoning Level 2", now_str),
                ]
                conn.executemany(
                    """
                    INSERT INTO telemetry_events (event_type, tier, is_correct, wpm, score, difficulty, details, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    seed_events,
                )

            # Seed past 7 days of Biometric logs right on the 66.7% threshold (14/21 checks) so user can immediately see & test the <70% Biological Bottleneck notification and toggle switches above 70%!
            b_count = conn.execute("SELECT COUNT(*) AS c FROM biometric_logs").fetchone()["c"]
            if b_count == 0:
                base_date = date.today()
                # Past 6 days: 13 checks out of 18; Today starts with 0 checks out of 3 = 13/21 (61.9% < 70%)
                # When user toggles Today's 3 switches ON, it becomes 16/21 (76.2% >= 70%)!
                history_pattern = [
                    (6, 1, 1, 1),
                    (5, 1, 0, 1),
                    (4, 1, 1, 0),
                    (3, 0, 1, 1),
                    (2, 1, 1, 0),
                    (1, 1, 0, 1),
                    (0, 0, 0, 0),  # Today
                ]
                for days_ago, sleep_q, phys_a, brain_n in history_pattern:
                    d_iso = (base_date - timedelta(days=days_ago)).isoformat()
                    conn.execute(
                        """
                        INSERT OR IGNORE INTO biometric_logs (day_iso, sleep_quality, physical_activity, brain_nutrition, updated_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (d_iso, sleep_q, phys_a, brain_n, datetime.now(timezone.utc).isoformat()),
                    )

            conn.commit()

    def get_schedule_status(self) -> dict:
        today = date.today().isoformat()
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO daily_schedule (day_iso) VALUES (?)", (today,))
            row = conn.execute("SELECT * FROM daily_schedule WHERE day_iso = ?", (today,)).fetchone()
        b1 = min(900, int(row["block1_seconds"]))
        b2 = min(900, int(row["block2_seconds"]))
        b3 = min(900, int(row["block3_seconds"]))
        b4 = min(900, int(row["block4_seconds"]))
        total_seconds = b1 + b2 + b3 + b4
        return {
            "day_iso": today,
            "total_budget_seconds": 3600,
            "total_elapsed_seconds": total_seconds,
            "total_progress_pct": round((total_seconds / 3600) * 100, 1),
            "blocks": {
                "block1": {"elapsed": b1, "target": 900, "done": bool(row["block1_done"]), "label": "Block 1: The Insight Engine"},
                "block2": {"elapsed": b2, "target": 900, "done": bool(row["block2_done"]), "label": "Block 2: The Logic Crucible"},
                "block3": {"elapsed": b3, "target": 900, "done": bool(row["block3_done"]), "label": "Block 3: Mental Model Re-Wiring"},
                "block4": {"elapsed": b4, "target": 900, "done": bool(row["block4_done"]), "label": "Block 4: The Integration Loop"},
            },
        }

    def update_block_timer(self, block_num: int, add_seconds: int, mark_done: bool = False) -> dict:
        today = date.today().isoformat()
        col_sec = f"block{block_num}_seconds"
        col_done = f"block{block_num}_done"
        with self._connect() as conn:
            conn.execute("INSERT OR IGNORE INTO daily_schedule (day_iso) VALUES (?)", (today,))
            conn.execute(
                f"UPDATE daily_schedule SET {col_sec} = MIN(900, {col_sec} + ?), {col_done} = CASE WHEN ? THEN 1 ELSE {col_done} END WHERE day_iso = ?",
                (max(0, add_seconds), 1 if mark_done else 0, today),
            )
            conn.commit()
        return self.get_schedule_status()

    def record_insight_submission(self, concept_id: str, reading_seconds: int, answers: list[int]) -> dict:
        all_concepts = self.get_all_insights()
        concept = next((c for c in all_concepts if c["id"] == concept_id), all_concepts[0])
        minutes = max(0.4, reading_seconds / 60.0)
        wpm = round(concept["word_count"] / minutes, 1)
        wpm = min(650.0, max(90.0, wpm))

        results = []
        now_str = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            for idx, q in enumerate(concept["questions"]):
                chosen = answers[idx] if idx < len(answers) else -1
                is_correct = 1 if chosen == q["correct_index"] else 0
                score = 100.0 if is_correct else 25.0
                results.append(
                    {
                        "tier": q["tier"],
                        "question": q["question"],
                        "chosen_index": chosen,
                        "correct_index": q["correct_index"],
                        "is_correct": bool(is_correct),
                        "explanation": q["explanation"],
                    }
                )
                conn.execute(
                    """
                    INSERT INTO telemetry_events (event_type, tier, is_correct, wpm, score, difficulty, details, created_at)
                    VALUES ('insight_recall', ?, ?, ?, ?, 2, ?, ?)
                    """,
                    (q["tier"], is_correct, wpm if q["tier"] == "Intermediate" else 0.0, score, f"{concept['domain']}: {q['tier']}", now_str),
                )

                # Update or flag in Block 4 SRS queue! If missed, flag as weak (is_weak = 1)
                card_id = f"srs_{concept['id']}_q{idx}"
                if not is_correct:
                    conn.execute(
                        "UPDATE srs_cards SET is_weak = 1, ease_factor = MAX(1.3, ease_factor - 0.25), next_review_ts = 0 WHERE card_id = ?",
                        (card_id,),
                    )
                else:
                    conn.execute(
                        "UPDATE srs_cards SET repetitions = repetitions + 1 WHERE card_id = ?",
                        (card_id,),
                    )
            conn.commit()

        self.update_block_timer(1, min(900, reading_seconds + 180), mark_done=True)
        return {
            "concept_id": concept_id,
            "reading_wpm": wpm,
            "accuracy_pct": round((sum(1 for r in results if r["is_correct"]) / len(results)) * 100, 1),
            "results": results,
            "weak_flagged_count": sum(1 for r in results if not r["is_correct"]),
        }

    def get_crucible_state(self) -> tuple[int, int]:
        with self._connect() as conn:
            diff = int(conn.execute("SELECT value FROM user_state WHERE key = 'crucible_difficulty'").fetchone()["value"])
            streak = int(conn.execute("SELECT value FROM user_state WHERE key = 'crucible_streak'").fetchone()["value"])
        return diff, streak

    def record_crucible_attempt(self, puzzle_type: str, difficulty: int, is_correct: bool, elapsed_sec: float) -> dict:
        curr_diff, streak = self.get_crucible_state()
        if is_correct:
            streak += 1
            if streak >= 2 and curr_diff < 5:
                curr_diff += 1
                streak = 0
        else:
            streak = 0
            if curr_diff > 1:
                curr_diff -= 1

        tier = "Foundational" if difficulty <= 2 else ("Intermediate" if difficulty <= 3 else "Advanced")
        score = (100.0 if is_correct else 20.0) * (1.0 + (difficulty - 1) * 0.1)
        now_str = datetime.now(timezone.utc).isoformat()

        with self._connect() as conn:
            conn.execute("UPDATE user_state SET value = ? WHERE key = 'crucible_difficulty'", (str(curr_diff),))
            conn.execute("UPDATE user_state SET value = ? WHERE key = 'crucible_streak'", (str(streak),))
            conn.execute(
                """
                INSERT INTO telemetry_events (event_type, tier, is_correct, wpm, score, difficulty, details, created_at)
                VALUES ('crucible_solve', ?, ?, 0, ?, ?, ?, ?)
                """,
                (tier, 1 if is_correct else 0, min(100.0, score), difficulty, f"Logic Crucible ({puzzle_type}) L{difficulty}", now_str),
            )
            conn.commit()

        self.update_block_timer(2, int(min(120, max(15, elapsed_sec))))
        return {"new_difficulty": curr_diff, "streak": streak, "tier_updated": tier}

    def record_mental_model_application(
        self, model_id: str, fallacy_choice: int, app_choice: int, synthesis_text: str
    ) -> dict:
        model = next((m for m in MENTAL_MODELS if m["id"] == model_id), MENTAL_MODELS[0])
        cs = model["case_study"]
        fallacy_ok = fallacy_choice == cs["fallacy_correct"]
        app_ok = app_choice == cs["application_correct"]

        # Evaluate cross-disciplinary synthesis text quality & keyword density
        lower_text = synthesis_text.lower()
        matched_keywords = [kw for kw in cs["synthesis_keywords"] if kw in lower_text]
        word_len = len(synthesis_text.strip().split())
        synthesis_score = min(100.0, 45.0 + len(matched_keywords) * 12.0 + min(25.0, word_len * 0.8)) if word_len >= 8 else 35.0

        now_str = datetime.now(timezone.utc).isoformat()
        with self._connect() as conn:
            # Intermediate tier: Logical fallacy detection in case study
            conn.execute(
                """
                INSERT INTO telemetry_events (event_type, tier, is_correct, wpm, score, difficulty, details, created_at)
                VALUES ('model_fallacy', 'Intermediate', ?, 0, ?, 3, ?, ?)
                """,
                (1 if fallacy_ok else 0, 100.0 if fallacy_ok else 25.0, f"{model['name']}: Fallacy ID", now_str),
            )
            # Advanced tier: Executive application + cross-disciplinary synthesis
            adv_score = (synthesis_score * 0.6) + ((100.0 if app_ok else 30.0) * 0.4)
            conn.execute(
                """
                INSERT INTO telemetry_events (event_type, tier, is_correct, wpm, score, difficulty, details, created_at)
                VALUES ('model_synthesis', 'Advanced', ?, 0, ?, 4, ?, ?)
                """,
                (1 if (app_ok and synthesis_score >= 65) else 0, adv_score, f"{model['name']}: Cross-Disciplinary Synthesis", now_str),
            )

            # Flag in Block 4 SRS queue if fallacy or application was missed
            if not fallacy_ok:
                conn.execute(
                    "UPDATE srs_cards SET is_weak = 1, ease_factor = MAX(1.3, ease_factor - 0.3) WHERE card_id = ?",
                    (f"srs_{model['id']}_fallacy",),
                )
            if not app_ok:
                conn.execute(
                    "UPDATE srs_cards SET is_weak = 1, ease_factor = MAX(1.3, ease_factor - 0.3) WHERE card_id = ?",
                    (f"srs_{model['id']}_app",),
                )
            conn.commit()

        self.update_block_timer(3, 300, mark_done=True)
        return {
            "model_id": model_id,
            "fallacy_correct": fallacy_ok,
            "application_correct": app_ok,
            "synthesis_score": round(synthesis_score, 1),
            "matched_concepts": matched_keywords,
            "flagged_to_srs": (not fallacy_ok) or (not app_ok),
        }

    def get_srs_queue(self, limit: int = 8) -> list[dict]:
        """Pulls questions dynamically from Blocks 1 and 3, strictly prioritizing weak concepts first."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM srs_cards
                ORDER BY is_weak DESC, ease_factor ASC, repetitions ASC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        cards = []
        for r in rows:
            cards.append(
                {
                    "card_id": r["card_id"],
                    "source_block": r["source_block"],
                    "domain_or_model": r["domain_or_model"],
                    "tier": r["tier"],
                    "question": r["question"],
                    "options": json.loads(r["options_json"]),
                    "correct_index": r["correct_index"],
                    "explanation": r["explanation"],
                    "ease_factor": round(r["ease_factor"], 2),
                    "interval_days": r["interval_days"],
                    "repetitions": r["repetitions"],
                    "is_weak": bool(r["is_weak"]),
                }
            )
        return cards

    def record_srs_review(self, card_id: str, chosen_index: int, confidence_grade: int = 4) -> dict:
        """Executes SM-2 Spaced Repetition update and updates tier retention telemetry."""
        with self._connect() as conn:
            row = conn.execute("SELECT * FROM srs_cards WHERE card_id = ?", (card_id,)).fetchone()
            if not row:
                return {"error": "Card not found"}

            is_correct = chosen_index == int(row["correct_index"])
            grade = confidence_grade if is_correct else 1  # SM-2 quality 0-5
            ease = float(row["ease_factor"])
            reps = int(row["repetitions"])
            interval = int(row["interval_days"])

            if is_correct:
                if reps == 0:
                    interval = 1
                elif reps == 1:
                    interval = 4
                else:
                    interval = max(1, round(interval * ease))
                reps += 1
                ease = max(1.3, ease + (0.1 - (5 - grade) * (0.08 + (5 - grade) * 0.02)))
                is_weak = 1 if ease < 2.0 else 0
            else:
                reps = 0
                interval = 1
                ease = max(1.3, ease - 0.25)
                is_weak = 1

            now_iso = datetime.now(timezone.utc).isoformat()
            conn.execute(
                """
                UPDATE srs_cards
                SET ease_factor = ?, interval_days = ?, repetitions = ?, is_weak = ?, last_reviewed = ?
                WHERE card_id = ?
                """,
                (ease, interval, reps, is_weak, now_iso, card_id),
            )
            conn.execute(
                """
                INSERT INTO telemetry_events (event_type, tier, is_correct, wpm, score, difficulty, details, created_at)
                VALUES ('srs_review', ?, ?, 0, ?, 2, ?, ?)
                """,
                (row["tier"], 1 if is_correct else 0, 100.0 if is_correct else 15.0, f"SRS ({row['domain_or_model']})", now_iso),
            )
            conn.commit()

        self.update_block_timer(4, 90)
        return {
            "card_id": card_id,
            "is_correct": is_correct,
            "correct_index": int(row["correct_index"]),
            "explanation": row["explanation"],
            "new_ease_factor": round(ease, 2),
            "new_interval_days": interval,
            "is_weak": bool(is_weak),
        }

    def get_benchmarks(self) -> dict:
        """Computes progression across Foundational, Intermediate, and Advanced Tiers."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM telemetry_events ORDER BY id DESC LIMIT 100").fetchall()
            weak_count = conn.execute("SELECT COUNT(*) AS c FROM srs_cards WHERE is_weak = 1").fetchone()["c"]
            total_cards = conn.execute("SELECT COUNT(*) AS c FROM srs_cards").fetchone()["c"]

        def avg_score(tier_name: str, default_val: float) -> float:
            vals = [float(r["score"]) for r in rows if r["tier"] == tier_name]
            return round(sum(vals) / len(vals), 1) if vals else default_val

        wpm_vals = [float(r["wpm"]) for r in rows if float(r["wpm"]) > 0]
        avg_wpm = round(sum(wpm_vals) / len(wpm_vals), 0) if wpm_vals else 248.0

        foundational_score = avg_score("Foundational", 84.0)
        intermediate_score = avg_score("Intermediate", 78.0)
        advanced_score = avg_score("Advanced", 74.0)
        crucible_diff, crucible_streak = self.get_crucible_state()

        return {
            "foundational": {
                "tier_name": "Foundational Tier",
                "subtitle": "Basic Retention (World Capitals, Primary Historical Dates, Elementary Logic)",
                "score_pct": foundational_score,
                "status": "Mastered" if foundational_score >= 85 else ("Proficient" if foundational_score >= 70 else "Developing"),
            },
            "intermediate": {
                "tier_name": "Intermediate Tier",
                "subtitle": "Comprehension Velocity (Complex Article WPM & Logical Fallacy Identification)",
                "score_pct": intermediate_score,
                "reading_wpm": int(avg_wpm),
                "status": "Accelerated" if intermediate_score >= 85 else ("Active" if intermediate_score >= 70 else "Calibrating"),
            },
            "advanced": {
                "tier_name": "Advanced Tier",
                "subtitle": "Cross-Disciplinary Synthesis (Historical Event → Mental Model → Modern Economy)",
                "score_pct": advanced_score,
                "status": "Polymathic" if advanced_score >= 85 else ("Synthesizing" if advanced_score >= 70 else "Emerging"),
            },
            "srs_summary": {
                "total_cards": total_cards,
                "weak_flagged": weak_count,
                "crucible_difficulty": crucible_diff,
                "crucible_streak": crucible_streak,
            },
            "recent_events": [
                {
                    "event_type": r["event_type"],
                    "tier": r["tier"],
                    "score": round(float(r["score"]), 1),
                    "details": r["details"],
                }
                for r in rows[:6]
            ],
        }

    def get_biometrics_status(self) -> dict:
        """Computes rolling 7-day biological compliance and bottlenecks (<70% threshold)."""
        base_date = date.today()
        days_list = [(base_date - timedelta(days=i)).isoformat() for i in range(6, -1, -1)]
        with self._connect() as conn:
            for d_iso in days_list:
                conn.execute("INSERT OR IGNORE INTO biometric_logs (day_iso) VALUES (?)", (d_iso,))
            conn.commit()
            placeholders = ",".join("?" for _ in days_list)
            rows = conn.execute(
                f"SELECT * FROM biometric_logs WHERE day_iso IN ({placeholders}) ORDER BY day_iso ASC",
                days_list,
            ).fetchall()

        history = []
        total_possible = 21  # 7 days * 3 binary metrics
        total_achieved = 0
        sleep_sum = 0
        activity_sum = 0
        nutrition_sum = 0

        for r in rows:
            sq = int(r["sleep_quality"])
            pa = int(r["physical_activity"])
            bn = int(r["brain_nutrition"])
            sleep_sum += sq
            activity_sum += pa
            nutrition_sum += bn
            total_achieved += sq + pa + bn
            history.append(
                {
                    "day_iso": r["day_iso"],
                    "is_today": r["day_iso"] == base_date.isoformat(),
                    "sleep_quality": bool(sq),
                    "physical_activity": bool(pa),
                    "brain_nutrition": bool(bn),
                    "daily_pct": round(((sq + pa + bn) / 3.0) * 100, 0),
                }
            )

        compliance_pct = round((total_achieved / total_possible) * 100.0, 1)
        bottleneck_active = compliance_pct < 70.0

        # Identify which pillar is the primary biological bottleneck
        lagging = []
        if sleep_sum < 5:
            lagging.append("Sleep Architecture (<7–8h impairs glymphatic clearance & synaptic consolidation)")
        if activity_sum < 5:
            lagging.append("Aerobic/Cardio Output (reduces hippocampal BDNF & PGC-1α neurogenesis)")
        if nutrition_sum < 5:
            lagging.append("Brain Nutrition (Omega-3 DHA & hydration deficit slows axonal myelin conductivity)")

        today_entry = next((h for h in history if h["is_today"]), history[-1])
        return {
            "rolling_7day_compliance_pct": compliance_pct,
            "threshold_pct": 70.0,
            "achieved_checks": total_achieved,
            "possible_checks": total_possible,
            "bottleneck_alert_active": bottleneck_active,
            "bottleneck_message": (
                f"BIOLOGICAL BOTTLENECK DETECTED ({compliance_pct}% Rolling 7-Day Compliance < 70% Threshold): "
                "Your cognitive gains in Fluid IQ and Spaced Repetition retention are currently being bottlenecked by physical biology."
                if bottleneck_active
                else f"BIOLOGICAL PREREQUISITES OPTIMAL ({compliance_pct}% ≥ 70%): Neurogenesis (BDNF) and synaptic consolidation pathways are supported."
            ),
            "lagging_vectors": lagging,
            "today": today_entry,
            "history_7days": history,
        }

    def update_biometric_checkin(
        self, day_iso: str, sleep_quality: bool, physical_activity: bool, brain_nutrition: bool
    ) -> dict:
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO biometric_logs (day_iso, sleep_quality, physical_activity, brain_nutrition, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(day_iso) DO UPDATE SET
                    sleep_quality = excluded.sleep_quality,
                    physical_activity = excluded.physical_activity,
                    brain_nutrition = excluded.brain_nutrition,
                    updated_at = excluded.updated_at
                """,
                (
                    day_iso,
                    1 if sleep_quality else 0,
                    1 if physical_activity else 0,
                    1 if brain_nutrition else 0,
                    datetime.now(timezone.utc).isoformat(),
                ),
            )
            conn.commit()
        return self.get_biometrics_status()
