import pytest
from fastapi.testclient import TestClient

from main import app
from engine.analyzer import engine, parse_raw_transcript
from engine.models import RiskAssessment
from tests.dataset import SCENARIO_DATASET

client = TestClient(app)

def test_health_endpoints():
    """Verify both /health and /api/health respond with 200 OK and healthy status."""
    res1 = client.get("/health")
    assert res1.status_code == 200
    assert res1.json()["status"] == "healthy"

    res2 = client.get("/api/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "healthy"

def test_demo_scenarios_endpoint():
    """Verify /api/demo-scenarios returns pre-configured reproducible test cases."""
    res = client.get("/api/demo-scenarios")
    assert res.status_code == 200
    scenarios = res.json()
    assert len(scenarios) >= 3
    ids = [s["id"] for s in scenarios]
    assert "legitimate_otp_discussion" in ids
    assert "progressive_impersonation_payment" in ids
    assert "ambiguous_delivery_inquiry" in ids

def test_legitimate_otp_discussion_not_flagged_high_risk():
    """
    Critical Requirement:
    Ensure conversation discussing OTP does not become high risk simply because it mentions OTP.
    When official safeguards are present, risk must be LOW_RISK.
    """
    legit_sc = next(s for s in SCENARIO_DATASET if s["id"] == "scenario_02_legit_otp")
    result = engine.analyze(turns=[], raw_transcript=legit_sc["transcript"])
    
    assert result.risk_level == "LOW_RISK"
    assert result.risk_score <= 25.0
    assert result.decision == "ALLOW"
    assert not result.insufficient_evidence

def test_progressive_scam_behavior_and_score_velocity():
    """
    Verify progressive risk escalation:
    Score must increase turn-by-turn as predatory vectors compound.
    """
    prog_sc = next(s for s in SCENARIO_DATASET if s["id"] == "scenario_05_urgent_payment")
    result = engine.analyze(turns=[], raw_transcript=prog_sc["transcript"])
    
    assert result.risk_level == "HIGH_RISK"
    assert result.risk_score >= 80.0
    assert result.decision == "BLOCK"
    assert len(result.turn_progression) == 3
    
    # Check that score in later turns is >= initial turn
    t1_score = result.turn_progression[0].cumulative_risk_score
    t3_score = result.turn_progression[2].cumulative_risk_score
    assert t3_score >= t1_score

def test_evidence_span_correctness():
    """
    Every evidence item must reference an actual verbatim phrase in the submitted conversation.
    """
    sc = next(s for s in SCENARIO_DATASET if s["id"] == "scenario_03_govt_impersonation")
    result = engine.analyze(turns=[], raw_transcript=sc["transcript"])
    
    assert len(result.evidence) > 0
    raw_lower = sc["transcript"].lower()
    for ev in result.evidence:
        assert ev.exact_quote.lower() in raw_lower, f"Quote '{ev.exact_quote}' not found in transcript!"
        assert ev.turn_number > 0
        assert ev.severity in ["LOW", "MEDIUM", "HIGH", "CRITICAL"]

def test_duplicate_signal_handling():
    """
    Ensure the engine avoids duplicate evidence when identical or related phrases repeat.
    """
    repeated_text = (
        "Caller: Hello, I am calling from State Bank of India.\n"
        "Senior: Yes, which bank?\n"
        "Caller: State Bank of India, calling from State Bank of India.\n"
    )
    result = engine.analyze(turns=[], raw_transcript=repeated_text)
    quotes = [ev.exact_quote.lower().strip() for ev in result.evidence]
    # Quotes should be deduplicated
    assert len(quotes) == len(set(quotes))

def test_ambiguous_conversation_uncertainty():
    """
    Conversations with insufficient context must be classified as INSUFFICIENT_EVIDENCE
    with conservative risk score and explicit uncertainty notice.
    """
    amb_sc = next(s for s in SCENARIO_DATASET if s["id"] == "scenario_11_ambiguous_conversation")
    result = engine.analyze(turns=[], raw_transcript=amb_sc["transcript"])
    
    assert result.risk_level == "INSUFFICIENT_EVIDENCE"
    assert result.decision == "INCONCLUSIVE"
    assert result.insufficient_evidence is True
    assert result.confidence_level == "LOW"

def test_empty_and_invalid_inputs():
    """
    Verify error handling on blank or missing inputs.
    """
    res1 = client.post("/api/analyze", json={})
    assert res1.status_code == 400

    res2 = client.post("/api/analyze", json={"transcript": "   \n  "})
    assert res2.status_code == 400

def test_api_analyze_progression_endpoint():
    """
    Test POST /api/analyze/progression endpoint.
    """
    sc = next(s for s in SCENARIO_DATASET if s["id"] == "scenario_08_remote_access_scam")
    res = client.post("/api/analyze/progression", json={"transcript": sc["transcript"]})
    assert res.status_code == 200
    data = res.json()
    assert "turns" in data
    assert len(data["turns"]) == 3
    assert data["final_risk_level"] == "HIGH_RISK"
    assert data["decision"] == "BLOCK"
