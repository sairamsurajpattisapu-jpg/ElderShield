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

def test_live_call_websocket_pipeline():
    """
    Test real-time WebSocket /ws/live-call stream:
    1. Connect and verify session_ready handshake
    2. Stream predatory transcript segments
    3. Verify live risk_update and critical warning push
    4. Send stop and receive session_summary
    """
    with client.websocket_connect("/ws/live-call") as ws:
        ready_msg = ws.receive_json()
        assert ready_msg["type"] == "session_ready"
        assert "session_id" in ready_msg

        # Turn 1: Caller impersonation
        ws.send_json({
            "type": "transcript_segment",
            "speaker": "Caller",
            "text": "This is Officer Sharma from Central Bureau of Investigation.",
            "is_final": True
        })
        msg1 = ws.receive_json()
        assert msg1["type"] == "risk_update"
        assert msg1["risk_level"] in ["LOW_RISK", "SUSPICIOUS", "INSUFFICIENT_EVIDENCE"]

        # Turn 2: Urgency & credential extraction (triggers warning)
        ws.send_json({
            "type": "transcript_segment",
            "speaker": "Caller",
            "text": "You are under digital arrest. Transfer 80000 rupees to our RBI verification account immediately or police will arrest you.",
            "is_final": True
        })
        msg2 = ws.receive_json()
        assert msg2["type"] == "risk_update"
        assert msg2["risk_level"] == "HIGH_RISK"

        # Warning is delivered immediately
        warning_msg = ws.receive_json()
        assert warning_msg["type"] == "warning"
        assert warning_msg["severity"] == "CRITICAL"
        assert "evidence_quotes" in warning_msg

        # Stop session cleanly
        ws.send_json({"type": "stop"})
        summary_msg = ws.receive_json()
        assert summary_msg["type"] == "session_summary"
        assert summary_msg["summary"]["final_risk_level"] == "HIGH_RISK"

def test_audio_upload_endpoint():
    """
    Test POST /api/analyze/audio endpoint with audio payload.
    """
    import io
    fake_wav_data = b"RIFF" + b"\x00" * 200 # Minimal test payload
    res = client.post(
        "/api/analyze/audio",
        files={"file": ("test.wav", io.BytesIO(fake_wav_data), "audio/wav")}
    )
    assert res.status_code == 200
    data = res.json()
    assert "audio_metrics" in data
    assert "transcript" in data
    assert "risk_assessment" in data
    assert data["risk_assessment"]["risk_level"] in ["LOW_RISK", "INSUFFICIENT_EVIDENCE", "SUSPICIOUS", "HIGH_RISK"]

def test_caller_intelligence_lookup():
    """
    Test POST /api/caller-lookup across verified institutional numbers,
    spoofing conflicts, and invalid formats.
    """
    # 1. Verified institutional toll-free
    res_sbi = client.post("/api/caller-lookup", json={"phone_number": "18001234", "claimed_organization": "SBI"})
    assert res_sbi.status_code == 200
    data_sbi = res_sbi.json()
    assert data_sbi["is_valid"] is True
    assert data_sbi["verdict"] in ["KNOWN_REGISTRY_MATCH", "VERIFIED_INSTITUTION"]
    assert data_sbi["caller_classification"] == "KNOWN_REGISTRY_MATCH"
    assert data_sbi["caller_authenticated"] is False
    assert "DOES NOT authenticate" in data_sbi["advisory"] or "NOT authenticate" in data_sbi["advisory"]
    assert "State Bank of India" in data_sbi["registered_organization"]
    assert data_sbi["spoofing_suspected"] is False

    # 2. Spoofing conflict: Mobile claiming to represent SBI
    res_spoof = client.post(
        "/api/caller-lookup",
        json={"phone_number": "+91 98490 12345", "claimed_organization": "State Bank of India"}
    )
    assert res_spoof.status_code == 200
    data_spoof = res_spoof.json()
    assert data_spoof["is_valid"] is True
    assert data_spoof["number_type"] == "MOBILE"
    assert data_spoof["verdict"] in ["POTENTIAL_IDENTITY_CONFLICT", "SPOOF_CONFLICT"]
    assert data_spoof["caller_classification"] == "POTENTIALLY_SUSPICIOUS"
    assert data_spoof["spoofing_suspected"] is True
    assert "CONFLICT" in data_spoof["spoofing_conflict_details"]

    # 3. National Cyber Crime Helpline
    res_1930 = client.post("/api/caller-lookup", json={"phone_number": "1930"})
    assert res_1930.status_code == 200
    assert res_1930.json()["verdict"] in ["KNOWN_REGISTRY_MATCH", "VERIFIED_INSTITUTION"]
    assert res_1930.json()["caller_authenticated"] is False

    # 4. Normal unlisted mobile number is NOT automatically classified as a scam
    res_unlisted = client.post("/api/caller-lookup", json={"phone_number": "+91 98490 99999"})
    assert res_unlisted.status_code == 200
    data_unlisted = res_unlisted.json()
    assert data_unlisted["is_valid"] is True
    assert data_unlisted["caller_classification"] == "CALLER_IDENTITY_UNVERIFIED"
    assert data_unlisted["caller_authenticated"] is False
    assert data_unlisted["spoofing_suspected"] is False
    assert data_unlisted["reputation_score"] <= 40.0 # Neutral, not scam

    # 5. Malformed / Invalid number
    res_invalid = client.post("/api/caller-lookup", json={"phone_number": "abc-invalid"})
    assert res_invalid.status_code == 200
    assert res_invalid.json()["verdict"] in ["INVALID_FORMAT", "INVALID_NUMBER"]
    assert res_invalid.json()["caller_classification"] == "INVALID_NUMBER"

def test_websocket_caller_info_message():
    """
    Test streaming caller_info message over WebSocket /ws/live-call
    and receiving immediate caller_intelligence and spoof warning events.
    """
    with client.websocket_connect("/ws/live-call") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"

        # Send spoofed caller info
        ws.send_json({
            "type": "caller_info",
            "phone_number": "+91 98490 12345",
            "claimed_organization": "State Bank of India"
        })

        intel_msg = ws.receive_json()
        assert intel_msg["type"] == "caller_intelligence"
        assert intel_msg["caller_data"]["verdict"] in ["POTENTIAL_IDENTITY_CONFLICT", "SPOOF_CONFLICT"]

        # Immediate spoofing warning is delivered
        warning_msg = ws.receive_json()
        assert warning_msg["type"] == "warning"
        assert warning_msg["title"] == "SPOOFED IDENTITY DETECTED"
        assert warning_msg["severity"] == "CRITICAL"

        ws.send_json({"type": "stop"})
        assert ws.receive_json()["type"] == "session_summary"


