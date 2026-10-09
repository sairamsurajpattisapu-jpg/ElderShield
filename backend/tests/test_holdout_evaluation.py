"""
ElderShield — Holdout Evaluation Pytest Suite
Executes the independent 30-conversation holdout test set via Pytest.
"""

import pytest
from engine.analyzer import engine, parse_raw_transcript
from tests.holdout_evaluation_dataset import HOLDOUT_EVALUATION_DATASET

@pytest.mark.parametrize("sample", HOLDOUT_EVALUATION_DATASET, ids=[s["id"] for s in HOLDOUT_EVALUATION_DATASET])
def test_holdout_evaluation_sample(sample):
    sid = sample["id"]
    category = sample["category"]
    ground_truth = sample["ground_truth"]
    transcript = sample["transcript"]

    turns = parse_raw_transcript(transcript)
    assessment = engine.analyze(turns=turns, raw_transcript=transcript)

    if ground_truth == "SCAM":
        assert assessment.decision == "BLOCK" or assessment.risk_level in ("HIGH_RISK", "SUSPICIOUS"), (
            f"Holdout sample {sid} ({category}) expected SCAM detection, got "
            f"level={assessment.risk_level}, decision={assessment.decision}, score={assessment.risk_score}"
        )
    elif ground_truth == "SAFE":
        assert assessment.decision != "BLOCK", (
            f"Holdout sample {sid} ({category}) falsely BLOCKED: "
            f"score={assessment.risk_score}, reasons={assessment.reasons}"
        )
        assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE"), (
            f"Holdout sample {sid} ({category}) elevated to unexpected risk level: {assessment.risk_level}"
        )
    elif ground_truth == "INSUFFICIENT_EVIDENCE":
        assert assessment.insufficient_evidence is True or assessment.risk_level == "INSUFFICIENT_EVIDENCE" or assessment.decision == "INCONCLUSIVE", (
            f"Holdout sample {sid} ({category}) failed to report insufficient evidence: "
            f"level={assessment.risk_level}, score={assessment.risk_score}"
        )
