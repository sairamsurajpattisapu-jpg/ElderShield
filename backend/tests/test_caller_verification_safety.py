import pytest
from fastapi.testclient import TestClient
from main import app
from engine.caller_intelligence import caller_service

client = TestClient(app)

def test_registry_match_is_not_authenticated():
    """
    Requirement: A registry match must NEVER, by itself, establish that a caller is genuine or safe.
    Caller ID can be spoofed over telephony networks.
    """
    res = client.post("/api/caller-lookup", json={"phone_number": "18001234", "claimed_organization": "SBI"})
    assert res.status_code == 200
    data = res.json()
    assert data["caller_classification"] == "KNOWN_REGISTRY_MATCH"
    assert data["caller_authenticated"] is False
    assert "DOES NOT authenticate" in data["advisory"] or "NOT authenticate" in data["advisory"]
    assert "spoofed" in data["advisory"].lower()
    assert data["registry_matching"] == "MATCHED_LOCAL_REGISTRY"
    assert data["caller_reputation_status"] == "STATIC_REGISTRY_ONLY"

def test_unrecognized_number_not_classified_as_scam():
    """
    Requirement: An unknown/unrecognized number is not automatically classified as a scam.
    A valid mobile number must not automatically be treated as suspicious.
    """
    # Valid Indian mobile number (+91 98765 43210)
    res = client.post("/api/caller-lookup", json={"phone_number": "+91 98765 43210"})
    assert res.status_code == 200
    data = res.json()
    assert data["is_valid"] is True
    assert data["caller_classification"] == "CALLER_IDENTITY_UNVERIFIED"
    assert data["caller_authenticated"] is False
    assert data["spoofing_suspected"] is False
    assert data["reputation_score"] == 30.0  # Neutral baseline
    assert data["registry_matching"] == "NO_REGISTRY_MATCH"
    assert data["caller_reputation_status"] == "REPUTATION_UNAVAILABLE"
    assert "identity is unverified" in data["advisory"]

def test_invalid_number_handled_safely():
    """
    Requirement: Invalid numbers must be handled safely without unhandled exceptions.
    """
    for bad_input in ["", "   ", "999", "abc-xyz", "+++", "123"]:
        res = client.post("/api/caller-lookup", json={"phone_number": bad_input})
        assert res.status_code == 200
        data = res.json()
        assert data["is_valid"] is False
        assert data["caller_classification"] == "INVALID_NUMBER"
        assert data["caller_authenticated"] is False

def test_missing_reputation_does_not_fabricate_results():
    """
    Requirement: If no trustworthy reputation source is available, explicitly indicate that
    reputation information is unavailable.
    """
    res = client.post("/api/caller-lookup", json={"phone_number": "+91 8023456789"})
    assert res.status_code == 200
    data = res.json()
    assert data["caller_reputation_status"] == "REPUTATION_UNAVAILABLE"
    assert data["registry_matching"] == "NO_REGISTRY_MATCH"
    assert data["caller_authenticated"] is False
    # Numbering region must include explicit allocation disclaimer
    assert "initial telecom circle allocation only" in data["location_disclaimer"]

def test_conversational_scam_evidence_remains_available_with_inconclusive_caller():
    """
    Requirement: Conversational scam evidence remains available even when caller information is inconclusive.
    """
    unified_req = {
        "phone_number": "+91 98765 43210", # Unrecognized neutral number
        "transcript": (
            "Caller: This is Officer Sharma from Central Bureau of Investigation. "
            "You are under digital arrest. Transfer 50,000 rupees to our RBI safety account immediately."
        )
    }
    res = client.post("/api/protect/unified", json=unified_req)
    assert res.status_code == 200
    data = res.json()
    
    # Caller is unverified and neutral
    assert data["caller_intelligence"]["caller_authenticated"] is False
    assert data["caller_intelligence"]["caller_classification"] == "CALLER_IDENTITY_UNVERIFIED"
    
    # Conversational evidence is fully captured and triggers HIGH_RISK
    assert data["composite_risk_level"] == "HIGH_RISK"
    assert data["decision"] == "BLOCK"
    assert len(data["conversational_evidence"]) >= 2
    categories = [ev["signal_category"] for ev in data["conversational_evidence"]]
    assert "IMPERSONATION" in categories
    assert "URGENCY_INTIMIDATION" in categories
