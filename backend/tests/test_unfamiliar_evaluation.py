"""
ElderShield — Unfamiliar Evaluation Pytest Suite
Executes the independent 112-conversation test set.
"""

import pytest
from engine.analyzer import engine, parse_raw_transcript
from tests.unfamiliar_evaluation_dataset import UNFAMILIAR_EVALUATION_SAMPLES

@pytest.mark.parametrize("sample", UNFAMILIAR_EVALUATION_SAMPLES, ids=[s["id"] for s in UNFAMILIAR_EVALUATION_SAMPLES])
def test_unfamiliar_evaluation_sample(sample):
    sid = sample["id"]
    category = sample["category"]
    ground_truth = sample["ground_truth"]
    transcript = sample["transcript"]

    turns = parse_raw_transcript(transcript)
    assessment = engine.analyze(turns=turns, raw_transcript=transcript)

    if ground_truth == "SCAM":
        assert assessment.decision == "BLOCK" or assessment.risk_level == "HIGH_RISK", (
            f"Unfamiliar sample {sid} ({category}) expected SCAM detection, got "
            f"level={assessment.risk_level}, decision={assessment.decision}, score={assessment.risk_score}"
        )
    elif ground_truth == "SAFE":
        assert assessment.decision != "BLOCK", (
            f"Unfamiliar sample {sid} ({category}) falsely BLOCKED: "
            f"score={assessment.risk_score}, reasons={assessment.reasons}"
        )
        assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE"), (
            f"Unfamiliar sample {sid} ({category}) elevated to unexpected risk level: {assessment.risk_level}"
        )
    elif ground_truth == "INSUFFICIENT_EVIDENCE":
        assert assessment.insufficient_evidence is True or assessment.risk_level == "INSUFFICIENT_EVIDENCE" or assessment.decision == "INCONCLUSIVE", (
            f"Unfamiliar sample {sid} ({category}) failed to report insufficient evidence: "
            f"level={assessment.risk_level}, score={assessment.risk_score}"
        )
