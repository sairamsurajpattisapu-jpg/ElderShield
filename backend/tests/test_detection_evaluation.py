"""
ElderShield — Systematic Detection & False-Alarm Pytest Suite
Validates all 12 standardized categories on the 24-sample evaluation fixture.
"""

import pytest
from engine.analyzer import engine, parse_raw_transcript
from tests.evaluation_dataset import EVALUATION_SAMPLES

@pytest.mark.parametrize("sample", EVALUATION_SAMPLES, ids=[s["id"] for s in EVALUATION_SAMPLES])
def test_evaluation_sample_detection(sample):
    sid = sample["id"]
    category = sample["category"]
    ground_truth = sample["ground_truth"]
    transcript = sample["transcript"]
    expected_decision = sample["expected_decision"]

    turns = parse_raw_transcript(transcript)
    assessment = engine.analyze(turns=turns, raw_transcript=transcript)

    if ground_truth == "SCAM":
        assert assessment.decision == "BLOCK" or assessment.risk_level == "HIGH_RISK", (
            f"Sample {sid} ({category}) expected SCAM detection, got "
            f"level={assessment.risk_level}, decision={assessment.decision}, score={assessment.risk_score}"
        )
    elif ground_truth == "SAFE":
        assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE"), (
            f"Sample {sid} ({category}) falsely flagged as risky: "
            f"level={assessment.risk_level}, decision={assessment.decision}, score={assessment.risk_score}"
        )
        assert assessment.decision != "BLOCK", (
            f"Sample {sid} ({category}) falsely BLOCKED: score={assessment.risk_score}"
        )
    elif ground_truth == "INSUFFICIENT_EVIDENCE":
        assert assessment.insufficient_evidence is True or assessment.risk_level == "INSUFFICIENT_EVIDENCE", (
            f"Sample {sid} ({category}) failed to report insufficient evidence: "
            f"level={assessment.risk_level}, score={assessment.risk_score}"
        )
