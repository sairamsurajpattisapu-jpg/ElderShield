import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from config import settings
from main import app
from engine.models import UnifiedProtectionRequest

client = TestClient(app)

def test_health_endpoints():
    """Verify liveness probe returns healthy status."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert "version" in data

    res2 = client.get("/api/health")
    assert res2.status_code == 200
    assert res2.json()["status"] == "healthy"

def test_ready_dependency_checks():
    """Verify deep readiness probe honestly reports subsystem statuses."""
    res = client.get("/ready")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] in ("ready", "degraded")
    assert "analyzer_engine" in data
    assert "asr_service" in data
    assert "caller_intelligence" in data
    assert "session_registry" in data
    assert "uptime_seconds" in data
    assert data["analyzer_engine"]["status"] == "ready"
    assert data["caller_intelligence"]["status"] == "ready"

def test_unified_protection_legitimate():
    """Test unified protection with legitimate bank caller and clean transcript."""
    payload = {
        "phone_number": "18001234", # SBI official hotline
        "claimed_organization": "State Bank of India",
        "transcript": "Good morning. Please visit your branch to update your KYC details."
    }
    res = client.post("/api/protect/unified", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert "composite_risk_level" in data
    assert "conversational_evidence" in data
    assert "caller_evidence" in data
    # Evidence must remain partitioned
    assert data["caller_evidence"]["evidence_type"] == "CALLER_IDENTITY"
    assert data["caller_evidence"]["conflict_status"] == "VERIFIED_MATCH"
    assert data["caller_evidence"]["spoofing_suspected"] is False
    assert data["composite_risk_level"] in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")

def test_unified_protection_spoofing_conflict():
    """Test unified protection with personal mobile number claiming to be CBI."""
    payload = {
        "phone_number": "9849012345", # Indian mobile number
        "claimed_organization": "Central Bureau of Investigation",
        "transcript": "You are under digital arrest. Transfer money immediately."
    }
    res = client.post("/api/protect/unified", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["composite_risk_level"] == "HIGH_RISK"
    assert data["decision"] == "BLOCK"
    assert data["alert_required"] is True
    # Caller evidence must be present and distinct
    assert data["caller_evidence"]["spoofing_suspected"] is True
    assert "DISCONNECT IMMEDIATELY" in data["recommended_action"]
    # Conversational evidence must be distinct
    assert len(data["conversational_evidence"]) >= 1

def test_authentication_enforcement(monkeypatch):
    """Test API Key authentication validation and rejection when enabled."""
    # Temporarily enforce auth
    monkeypatch.setattr(settings, "require_auth", True)
    monkeypatch.setattr(settings, "api_key", "test-secret-key-123")

    # Request without key should fail 401
    res_no_auth = client.post("/api/caller-lookup", json={"phone_number": "18001234"})
    assert res_no_auth.status_code == 401

    # Request with invalid key should fail 403
    res_bad_auth = client.post(
        "/api/caller-lookup",
        json={"phone_number": "18001234"},
        headers={"X-API-Key": "wrong-key"}
    )
    assert res_bad_auth.status_code == 403

    # Request with valid X-API-Key should succeed
    res_valid_header = client.post(
        "/api/caller-lookup",
        json={"phone_number": "18001234"},
        headers={"X-API-Key": "test-secret-key-123"}
    )
    assert res_valid_header.status_code == 200

    # Request with valid Bearer token should succeed
    res_valid_bearer = client.post(
        "/api/caller-lookup",
        json={"phone_number": "18001234"},
        headers={"Authorization": "Bearer test-secret-key-123"}
    )
    assert res_valid_bearer.status_code == 200

def test_websocket_ping_pong():
    """Verify live WebSocket ping/pong keepalive and session handshake."""
    with client.websocket_connect("/ws/live-call") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"
        assert "session_id" in ready

        # Send ping
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"
        assert "timestamp" in pong

        # Send stop to clean up
        ws.send_json({"type": "stop"})
        summary = ws.receive_json()
        assert summary["type"] == "session_summary"
