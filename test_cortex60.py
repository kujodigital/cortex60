"""End-to-end verification suite for the 1-Hour Cognitive Enhancement App (Cortex60)."""

from pathlib import Path
from cortex60.database import CortexDatabase
from cortex60.logic_crucible import generate_crucible_problem
from cortex60.seed_data import INSIGHT_CONCEPTS, MENTAL_MODELS


def run_tests() -> None:
    test_db_path = Path("/tmp/test_cortex60.db")
    if test_db_path.exists():
        test_db_path.unlink()

    db = CortexDatabase(db_path=test_db_path)

    # 1. Verify 6 Domains in Block 1 (The Insight Engine)
    domains = [c["domain"] for c in INSIGHT_CONCEPTS]
    expected_domains = [
        "History/Geography",
        "Science/Tech",
        "Politics/Economics",
        "Philosophy/Literature",
        "Arts/Culture",
        "Finance/Health",
    ]
    assert domains == expected_domains, f"Expected 6 domains {expected_domains}, got {domains}"
    print("✔ Block 1 (Insight Engine): All 6 multi-disciplinary domains verified (10m Read + 5m Recall).")

    # 2. Verify Block 1 Active Recall submission + WPM velocity + Weak Concept flagging to Block 4
    res_b1 = db.record_insight_submission("insight_hist_geo_01", reading_seconds=120, answers=[0, 1, 0])
    assert res_b1["reading_wpm"] > 100
    assert res_b1["weak_flagged_count"] == 1  # Question index 1 intentionally missed
    print(f"✔ Block 1 Active Recall: Computed {res_b1['reading_wpm']} WPM and flagged {res_b1['weak_flagged_count']} missed concept to Block 4 SRS.")

    # 3. Verify Block 2 (The Logic Crucible) 4 Modalities + Dynamic Difficulty Scaling
    for modality in ("matrix", "sequence", "cryptogram", "spatial"):
        for lvl in range(1, 6):
            prob = generate_crucible_problem(difficulty=lvl, preferred_type=modality)
            assert prob["puzzle_type"] == modality
            assert len(prob["options"]) == 4
            assert 0 <= prob["correct_index"] < 4

    # Test dynamic difficulty scaling up on 2 consecutive correct answers
    db.record_crucible_attempt("matrix", 2, True, 18.0)
    up_state = db.record_crucible_attempt("spatial", 2, True, 20.0)
    assert up_state["new_difficulty"] == 3, f"Expected difficulty to scale up to 3, got {up_state}"
    print("✔ Block 2 (Logic Crucible): Matrix, Sequence, Cryptogram, and Spatial generators + dynamic difficulty scaling verified.")

    # 4. Verify Block 3 (Mental Model Re-Wiring) Case Study + Cross-Disciplinary Synthesis
    assert len(MENTAL_MODELS) >= 4
    res_b3 = db.record_mental_model_application(
        model_id="model_first_principles",
        fallacy_choice=0,
        app_choice=0,
        synthesis_text="Deconstructing battery pack cost down to the physical material floor parallels the Bessemer steel process, shifting capital allocation and production margin.",
    )
    assert res_b3["fallacy_correct"] is True
    assert res_b3["application_correct"] is True
    assert res_b3["synthesis_score"] >= 80.0
    print(f"✔ Block 3 (Mental Model Re-Wiring): Case study evaluated, synthesis score = {res_b3['synthesis_score']}%.")

    # 5. Verify Block 4 (The Integration Loop - SM-2 Spaced Repetition pulling from Blocks 1 & 3, Weak First)
    queue = db.get_srs_queue(limit=10)
    assert len(queue) > 0
    assert queue[0]["is_weak"] is True, "Expected weak-flagged concepts to be prioritized at the top of Block 4 queue"
    sources = {c["source_block"] for c in queue}
    assert "BLOCK_1" in sources and "BLOCK_3" in sources
    rev = db.record_srs_review(queue[0]["card_id"], queue[0]["correct_index"], confidence_grade=5)
    assert rev["is_correct"] is True
    assert rev["new_interval_days"] >= 1
    print("✔ Block 4 (Integration Loop): SM-2 Spaced Repetition queue verified (weak concepts prioritized from Blocks 1 & 3).")

    # 6. Verify Section 2 (Benchmarking & Metrics Engine across 3 Tiers)
    bench = db.get_benchmarks()
    for tier_key in ("foundational", "intermediate", "advanced"):
        assert tier_key in bench
        assert 0 <= bench[tier_key]["score_pct"] <= 100
    print(
        f"✔ Section 2 (Benchmarks): Foundational={bench['foundational']['score_pct']}%, "
        f"Intermediate={bench['intermediate']['score_pct']}% ({bench['intermediate']['reading_wpm']} WPM), "
        f"Advanced={bench['advanced']['score_pct']}%."
    )

    # 7. Verify Section 3 (Biometric & Compliance Tracking <70% Rolling 7-Day Alert)
    bio_initial = db.get_biometrics_status()
    assert bio_initial["rolling_7day_compliance_pct"] < 70.0
    assert bio_initial["bottleneck_alert_active"] is True
    print(f"✔ Section 3 (Biometrics <70% Alert): Initial 7-day compliance = {bio_initial['rolling_7day_compliance_pct']}% -> Bottleneck Alert ACTIVE.")

    # Toggle Today's 3 switches ON -> 16/21 = 76.2% >= 70% -> Bottleneck Alert clears!
    bio_updated = db.update_biometric_checkin(
        day_iso=bio_initial["today"]["day_iso"],
        sleep_quality=True,
        physical_activity=True,
        brain_nutrition=True,
    )
    assert bio_updated["rolling_7day_compliance_pct"] >= 70.0
    assert bio_updated["bottleneck_alert_active"] is False
    print(f"✔ Section 3 (Biometrics >=70% Recovery): Updated 7-day compliance = {bio_updated['rolling_7day_compliance_pct']}% -> Bottleneck Alert CLEARED.")


if __name__ == "__main__":
    run_tests()
