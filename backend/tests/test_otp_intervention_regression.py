import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from engine.analyzer import ConversationRiskEngine
from engine.privacy import redact_sensitive_data
from engine.stream_session import session_registry
from engine.models import UnifiedProtectionRequest

client = TestClient(app)
analyzer = ConversationRiskEngine()


# ==============================================================================
# SCENARIO 1: Normal, legitimate conversation remains quiet
# ==============================================================================
def test_scenario_01_normal_legitimate_conversation_remains_silent():
    transcript = (
        "Caller: Hello Grandpa, how are you feeling today?\n"
        "Senior: Hello dear! I am doing well, just went for my morning walk.\n"
        "Caller: Great to hear! Don't forget to take your blood pressure medication after lunch.\n"
        "Senior: Yes, I already kept it on the dining table. Thank you."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")
    assert assessment.risk_score <= 15.0
    assert assessment.urgent_intervention_required is False
    assert assessment.otp_state in ("MONITORING", "SAFE_OR_INCONCLUSIVE")


# ==============================================================================
# SCENARIO 2: Unknown phone number alone with no red flags remains silent
# ==============================================================================
def test_scenario_02_unknown_phone_number_alone_remains_silent():
    req = UnifiedProtectionRequest(
        phone_number="+919876543210",
        transcript="Caller: Good afternoon, is this Mr. Sharma?\nSenior: Yes speaking, who is this?\nCaller: I am calling to follow up on the alumni meeting next Sunday."
    )
    response = client.post("/api/protect/unified", json=req.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["composite_risk_level"] in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")
    assert data["alert_required"] is False
    assert data["caller_evidence"]["conflict_status"] in ("NO_CONFLICT_UNVERIFIED", "UNKNOWN")


# ==============================================================================
# SCENARIO 3: OTP mentioned passively without request to reveal it
# ==============================================================================
def test_scenario_03_passive_otp_mention_does_not_trigger_urgent_warning():
    transcript = (
        "Caller: Good morning sir. Your one-time password has been dispatched to your mobile.\n"
        "Caller: Please remember never to share your OTP or PIN with anyone over the phone.\n"
        "Senior: Thank you, I know never to tell anyone my codes."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.urgent_intervention_required is False
    assert assessment.otp_state != "URGENT_INTERVENTION"
    assert assessment.risk_level != "HIGH_RISK"


# ==============================================================================
# SCENARIO 4: Caller asks user to read out or dictate OTP
# ==============================================================================
def test_scenario_04_caller_asks_to_dictate_otp_triggers_intervention():
    transcript = (
        "Caller: Hello, I am sending a 6-digit verification code to your phone.\n"
        "Caller: Dictate the OTP to me immediately so I can authenticate your account."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.otp_disclosure_risk is True
    assert assessment.otp_state in ("OTP_RISK_DETECTED", "URGENT_INTERVENTION")
    assert assessment.intervention_heading is not None
    assert "OTP" in assessment.intervention_heading
    assert "STOP!" in (assessment.intervention_spoken_text or "")


# ==============================================================================
# SCENARIO 5: OTP request + threats of account suspension
# ==============================================================================
def test_scenario_05_otp_request_with_account_suspension_threat():
    transcript = (
        "Caller: Your SBI bank account will be blocked and frozen within 30 minutes!\n"
        "Senior: Why? What happened?\n"
        "Caller: Your KYC has expired! Tell me the 6-digit OTP code received on your mobile right now to stop suspension!"
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.risk_level == "HIGH_RISK"
    assert assessment.urgent_intervention_required is True
    assert assessment.otp_state == "URGENT_INTERVENTION"
    assert assessment.signals_summary.credential_requests is True
    assert assessment.signals_summary.urgency_and_threats is True


# ==============================================================================
# SCENARIO 6: Caller impersonates bank manager asking for verification code
# ==============================================================================
def test_scenario_06_bank_manager_impersonation_asking_verification_code():
    transcript = (
        "Caller: I am the Chief Manager from State Bank of India main branch.\n"
        "Caller: We are verifying unauthorized debit card transactions. Read the verification code sent to your SMS."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.urgent_intervention_required is True
    assert assessment.otp_state == "URGENT_INTERVENTION"
    assert assessment.signals_summary.impersonation is True
    assert assessment.signals_summary.credential_requests is True


# ==============================================================================
# SCENARIO 7: Caller asks for banking PIN or card password
# ==============================================================================
def test_scenario_07_banking_pin_or_password_request_treated_with_same_severity():
    transcript = (
        "Caller: Please provide your 4-digit ATM card PIN and NetBanking login password to update your profile."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.otp_disclosure_risk is True
    assert assessment.signals_summary.credential_requests is True
    assert assessment.otp_state in ("OTP_RISK_DETECTED", "URGENT_INTERVENTION")


# ==============================================================================
# SCENARIO 8: User explicitly refuses to share OTP
# ==============================================================================
def test_scenario_08_user_explicitly_refuses_to_share_otp():
    transcript = (
        "Caller: Tell me the OTP code that was just sent to your phone.\n"
        "Senior: I will not share my OTP! Main apna OTP kisi ko nahi bataunga. Never ask me for verification codes."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.signals_summary.legitimate_safeguards_present is True
    senior_turn = assessment.turn_progression[1]
    assert senior_turn.is_otp_request is False


# ==============================================================================
# SCENARIO 9: Conversation discusses previous scam without live solicitation
# ==============================================================================
def test_scenario_09_previous_scam_discussion_does_not_trigger_false_alert():
    transcript = (
        "Caller: Hello auntie, I heard someone called uncle last month asking for his OTP?\n"
        "Senior: Yes, a scammer called pretending to be electricity board and asked for OTP, but he disconnected the call."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")
    assert assessment.urgent_intervention_required is False
    assert assessment.otp_disclosure_risk is False


# ==============================================================================
# SCENARIO 10: Legitimate hospital appointment scheduling
# ==============================================================================
def test_scenario_10_legitimate_hospital_appointment():
    transcript = (
        "Caller: Good morning, this is Apollo Hospital reception.\n"
        "Caller: Confirming your consultation with Dr. Reddy tomorrow at 10 AM.\n"
        "Senior: Yes, I will be there. Do I need to bring any previous reports?\n"
        "Caller: Yes, please bring your blood test reports and hospital card."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")
    assert assessment.risk_score <= 15.0
    assert assessment.urgent_intervention_required is False
    assert assessment.otp_state in ("MONITORING", "SAFE_OR_INCONCLUSIVE")


# ==============================================================================
# SCENARIO 11: Legitimate banking call without secret-disclosure request
# ==============================================================================
def test_scenario_11_legitimate_bank_call_directing_to_branch():
    transcript = (
        "Caller: Good morning Mr. Sharma, this is Canara Bank customer service.\n"
        "Caller: We noticed an address update request on your savings account.\n"
        "Caller: Please visit your nearest branch in person with your original passbook and photo ID to verify.\n"
        "Senior: Understood, I will visit the MG Road branch on Monday."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")
    assert assessment.urgent_intervention_required is False


# ==============================================================================
# SCENARIO 12: Genuine user-initiated authentication flow
# ==============================================================================
def test_scenario_12_genuine_user_initiated_authentication_flow():
    transcript = (
        "Senior: I am trying to login to my pension portal on my computer.\n"
        "Senior: I received the OTP on my mobile and I entered it directly on the portal website.\n"
        "Caller: That is fine father, let me know if the pension slip downloads properly."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")
    assert assessment.urgent_intervention_required is False


# ==============================================================================
# SCENARIO 13: Caller asks for OTP split across multiple speech chunks
# ==============================================================================
def test_scenario_13_otp_request_split_across_multiple_turns():
    turns_text = [
        "Caller: Sir, I am initiating your security update now.",
        "Caller: You will receive an SMS from bank.",
        "Caller: Please read the 6-digit OTP code to me."
    ]
    transcript = "\n".join(turns_text)
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.otp_disclosure_risk is True
    assert assessment.otp_state in ("OTP_RISK_DETECTED", "URGENT_INTERVENTION")
    last_turn = assessment.turn_progression[-1]
    assert last_turn.is_otp_request is True


# ==============================================================================
# SCENARIO 14: Repeated chunks deduplication prevents duplicate warnings
# ==============================================================================
def test_scenario_14_deduplication_prevents_duplicate_warnings():
    with client.websocket_connect("/ws/live-call") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"

        # Send high-risk request
        payload = {
            "type": "transcript_segment",
            "speaker": "Caller",
            "text": "Your account is blocked! Tell me the OTP immediately to stop police arrest!",
            "is_final": True
        }
        ws.send_json(payload)
        res1 = ws.receive_json()
        assert res1["type"] == "risk_update"
        assert res1["urgent_intervention_required"] is True

        ev1 = ws.receive_json()
        assert ev1["type"] == "otp_intervention"
        ev2 = ws.receive_json()
        assert ev2["type"] == "warning"

        # Send exact duplicate text immediately: risk update sent, but intervention deduplicated
        ws.send_json(payload)
        res2 = ws.receive_json()
        assert res2["type"] == "risk_update"

        # Using a benign segment to flush:
        ws.send_json({
            "type": "transcript_segment",
            "speaker": "Senior",
            "text": "Hello?",
            "is_final": True
        })
        res3 = ws.receive_json()
        assert res3["type"] == "risk_update"


# ==============================================================================
# SCENARIO 15: New independent high-risk request triggers fresh event
# ==============================================================================
def test_scenario_15_new_independent_threat_triggers_new_warning():
    with client.websocket_connect("/ws/live-call") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"

        # Event 1: OTP solicitation with urgency/threat
        ws.send_json({
            "type": "transcript_segment",
            "speaker": "Caller",
            "text": "Your account is frozen! Tell me your verification code immediately.",
            "is_final": True
        })
        u1 = ws.receive_json()
        assert u1["type"] == "risk_update"
        interv1 = ws.receive_json()
        assert interv1["type"] == "otp_intervention"
        warn1 = ws.receive_json()
        assert warn1["type"] == "warning"
        event1_id = interv1.get("event_id")

        # Event 2: New distinct escalation (CBI Digital Arrest + Immediate Escrow Transfer)
        ws.send_json({
            "type": "transcript_segment",
            "speaker": "Caller",
            "text": "You are under CBI digital arrest! Transfer 50,000 rupees to government escrow account right now!",
            "is_final": True
        })
        u2 = ws.receive_json()
        assert u2["type"] == "risk_update"
        interv2 = ws.receive_json()
        assert interv2["type"] == "otp_intervention"
        warn2 = ws.receive_json()
        assert warn2["type"] == "warning"
        event2_id = interv2.get("event_id")
        assert event1_id != event2_id


# ==============================================================================
# SCENARIO 16: ASR engine technical issues handled gracefully (not mislabeled as scam)
# ==============================================================================
def test_scenario_16_asr_technical_failure_handled_gracefully():
    # Sending invalid/empty audio upload
    response = client.post(
        "/api/analyze/audio",
        files={"file": ("empty.wav", b"", "audio/wav")}
    )
    # Technical failure: returns 400 Bad Request, never returns a false scam diagnosis
    assert response.status_code == 400


# ==============================================================================
# SCENARIO 17: WebSocket disconnect and reconnect cleanly preserves state
# ==============================================================================
def test_scenario_17_websocket_reconnect_preserves_clean_state():
    initial_count = session_registry.active_count

    with client.websocket_connect("/ws/live-call") as ws1:
        ready1 = ws1.receive_json()
        session_id_1 = ready1["session_id"]
        assert session_registry.get_session(session_id_1) is not None

    # After clean disconnect, old session is pruned
    assert session_registry.get_session(session_id_1) is None
    assert session_registry.active_count == initial_count

    # New connection starts with clean state (no false alarm on connect)
    with client.websocket_connect("/ws/live-call") as ws2:
        ready2 = ws2.receive_json()
        assert ready2["type"] == "session_ready"
        session_id_2 = ready2["session_id"]
        assert session_id_2 != session_id_1


# ==============================================================================
# SCENARIO 18: Simultaneous sessions multi-tenant isolation
# ==============================================================================
def test_scenario_18_simultaneous_sessions_multi_tenant_isolation():
    with client.websocket_connect("/ws/live-call") as ws_scam:
        ready_scam = ws_scam.receive_json()
        with client.websocket_connect("/ws/live-call") as ws_legit:
            ready_legit = ws_legit.receive_json()
            assert ready_scam["session_id"] != ready_legit["session_id"]

            # Send scam call to ws_scam
            ws_scam.send_json({
                "type": "transcript_segment",
                "speaker": "Caller",
                "text": "Your account is locked. Tell me the OTP immediately.",
                "is_final": True
            })

            # Send benign dialogue to ws_legit
            ws_legit.send_json({
                "type": "transcript_segment",
                "speaker": "Caller",
                "text": "Hello, doctor's clinic calling to confirm appointment.",
                "is_final": True
            })

            res_scam = ws_scam.receive_json()
            assert res_scam["urgent_intervention_required"] is True

            res_legit = ws_legit.receive_json()
            assert res_legit["urgent_intervention_required"] is False
            assert res_legit["risk_score"] <= 15.0


# ==============================================================================
# SCENARIO 19: Sensitive OTP values redacted from transcripts and logs
# ==============================================================================
def test_scenario_19_sensitive_otp_redacted_from_diagnostic_transcripts():
    raw_text = "Your one time password is 849201. Please keep it confidential."
    redacted = redact_sensitive_data(raw_text)
    assert "849201" not in redacted
    assert "[REDACTED_CREDENTIAL]" in redacted

    # Non-sensitive numbers like appointment time or date should NOT be redacted
    benign_text = "Your appointment is scheduled at 4 PM on 25th March."
    benign_redacted = redact_sensitive_data(benign_text)
    assert "4 PM" in benign_redacted
    assert "25th" in benign_redacted


# ==============================================================================
# SCENARIO 20: Android warning service delivery contract
# ==============================================================================
def test_scenario_20_android_warning_service_delivery_contract():
    transcript = (
        "Caller: Your account is blocked! Read the 6-digit verification code to me right now to stop suspension."
    )
    assessment = analyzer.analyze(raw_transcript=transcript)
    assert assessment.urgent_intervention_required is True
    assert assessment.otp_state == "URGENT_INTERVENTION"

    # Validate that fields required by Android ElderAlertManager are properly structured
    assert assessment.intervention_heading is not None
    assert len(assessment.intervention_heading) > 0
    assert assessment.intervention_spoken_text is not None
    assert "STOP!" in assessment.intervention_spoken_text
    assert assessment.event_id is not None
    assert assessment.intervention_language in ("en", "hi", "te")
