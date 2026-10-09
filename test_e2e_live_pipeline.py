import time
import os
import io
import json
import sys
sys.path.insert(0, os.path.abspath("backend"))

from fastapi.testclient import TestClient
from main import app
from engine.asr_service import asr_service
from engine.analyzer import engine

client = TestClient(app)

def run_e2e_verification():
    print("=" * 70)
    print("EL DERSHIELD — END-TO-END LIVE PIPELINE VERIFICATION SUITE")
    print("=" * 70)

    # -------------------------------------------------------------
    # PRIORITY 3: VERIFY ASR PATH WITH REAL SPEECH AUDIO
    # -------------------------------------------------------------
    print("\n[PRIORITY 3] Verifying ASR Path (faster-whisper-tiny on real speech)...")
    assert os.path.exists("scam_speech.wav"), "scam_speech.wav missing"
    assert os.path.exists("legit_speech.wav"), "legit_speech.wav missing"
    assert os.path.exists("ambiguous_speech.wav"), "ambiguous_speech.wav missing"

    with open("scam_speech.wav", "rb") as f:
        scam_bytes = f.read()

    asr_start = time.time()
    scam_asr = asr_service.transcribe_audio_bytes(scam_bytes, filename="scam_speech.wav")
    asr_latency_ms = round((time.time() - asr_start) * 1000, 1)

    print(f"  ASR Engine Active: {scam_asr.get('engine_used')}")
    print(f"  Audio Duration: {scam_asr.get('duration_seconds')}s")
    print(f"  Measured ASR Latency: {asr_latency_ms}ms")
    print(f"  Recognized Transcript: \"{scam_asr.get('transcript')}\"")
    assert len(scam_asr.get("transcript", "")) > 10, "ASR failed to recognize speech"

    # -------------------------------------------------------------
    # PRIORITY 4: THREE END-TO-END SCENARIOS VIA AUDIO API
    # -------------------------------------------------------------
    print("\n[PRIORITY 4] Running 3 End-to-End Scenarios via POST /api/analyze/audio...")

    # Scenario A: Legitimate bank conversation mentioning OTP
    print("\n  --- Scenario A: Legitimate Bank Call (Mentions OTP & Branch Visit) ---")
    with open("legit_speech.wav", "rb") as f:
        res_a = client.post("/api/analyze/audio", files={"file": ("legit.wav", f, "audio/wav")})
    assert res_a.status_code == 200, f"Scenario A failed: {res_a.text}"
    data_a = res_a.json()
    ass_a = data_a["risk_assessment"]
    print(f"    Transcript: \"{data_a['transcript']}\"")
    print(f"    Classification: {ass_a['risk_level']} (Score: {ass_a['risk_score']}/100, Decision: {ass_a['decision']})")
    assert ass_a["risk_level"] == "LOW_RISK", f"Expected LOW_RISK for legitimate OTP call, got {ass_a['risk_level']}"
    assert ass_a["decision"] == "ALLOW", f"Expected ALLOW decision, got {ass_a['decision']}"
    print("    [PASSED] Legitimate conversation resistance verified: No false alarm despite 'OTP' keyword.")

    # Scenario B: Progressive scam conversation
    print("\n  --- Scenario B: Progressive Scam Call (CBI + Digital Arrest + Escrow) ---")
    with open("scam_speech.wav", "rb") as f:
        res_b = client.post("/api/analyze/audio", files={"file": ("scam.wav", f, "audio/wav")})
    assert res_b.status_code == 200, f"Scenario B failed: {res_b.text}"
    data_b = res_b.json()
    ass_b = data_b["risk_assessment"]
    print(f"    Transcript: \"{data_b['transcript']}\"")
    print(f"    Classification: {ass_b['risk_level']} (Score: {ass_b['risk_score']}/100, Decision: {ass_b['decision']})")
    print(f"    Evidence Count: {len(ass_b['evidence'])} items flagged")
    for ev in ass_b["evidence"]:
        print(f"      - [{ev['signal_category']}] \"{ev['exact_quote']}\" -> {ev['explanation']}")
    assert ass_b["risk_level"] == "HIGH_RISK", f"Expected HIGH_RISK, got {ass_b['risk_level']}"
    assert ass_b["decision"] == "BLOCK", f"Expected BLOCK, got {ass_b['decision']}"
    assert len(ass_b["evidence"]) >= 2, "Expected multiple compound evidence items"
    print("    [PASSED] Progressive scam correctly flagged with verifiable evidence.")

    # Scenario C: Ambiguous delivery conversation
    print("\n  --- Scenario C: Ambiguous Courier Call (Insufficient Context) ---")
    with open("ambiguous_speech.wav", "rb") as f:
        res_c = client.post("/api/analyze/audio", files={"file": ("ambiguous.wav", f, "audio/wav")})
    assert res_c.status_code == 200, f"Scenario C failed: {res_c.text}"
    data_c = res_c.json()
    ass_c = data_c["risk_assessment"]
    print(f"    Transcript: \"{data_c['transcript']}\"")
    print(f"    Classification: {ass_c['risk_level']} (Score: {ass_c['risk_score']}/100, Decision: {ass_c['decision']})")
    assert ass_c["risk_level"] == "INSUFFICIENT_EVIDENCE", f"Expected INSUFFICIENT_EVIDENCE, got {ass_c['risk_level']}"
    assert ass_c["insufficient_evidence"] is True
    print("    [PASSED] Ambiguous conversation correctly handled with conservative uncertainty.")

    # -------------------------------------------------------------
    # PRIORITY 2: LIVE WEBSOCKET PIPELINE & WARNING LATENCY
    # -------------------------------------------------------------
    print("\n[PRIORITY 2] Verifying Real-Time WebSocket Pipeline (/ws/live-call)...")
    with client.websocket_connect("/ws/live-call") as ws:
        # Handshake
        t0 = time.time()
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"
        session_id = ready["session_id"]
        print(f"  Handshake Complete. Session ID: {session_id}")

        # Stream Audio Chunks
        ws.send_json({
            "type": "audio_chunk",
            "sequence_id": 1,
            "chunk": "AAAA" # valid b64
        })
        ack = ws.receive_json()
        assert ack["type"] == "chunk_ack"
        print(f"  Audio Chunk Handling Verified (Chunk 1 ACK, buffered bytes: {ack['buffered_bytes']})")

        # Turn 1: Initial introduction (Safe / Insufficient)
        ws.send_json({
            "type": "transcript_segment",
            "speaker": "Caller",
            "text": "This is Officer Sharma from Central Bureau of Investigation.",
            "is_final": True
        })
        t_turn1 = ws.receive_json()
        assert t_turn1["type"] == "risk_update"
        print(f"  Turn 1 Update: Score={t_turn1['risk_score']}, Risk={t_turn1['risk_level']}")

        # Turn 2: Toxic Predatory Turn (Urgency + Secrecy + Escrow Transfer)
        t_sent = time.time()
        ws.send_json({
            "type": "transcript_segment",
            "speaker": "Caller",
            "text": "You are under digital arrest. Do not inform your family. Transfer 85000 rupees to our RBI verification escrow account immediately.",
            "is_final": True
        })
        t_turn2 = ws.receive_json()
        assert t_turn2["type"] == "risk_update"
        assert t_turn2["risk_level"] == "HIGH_RISK"

        # Receive Immediate Urgent Warning
        warning = ws.receive_json()
        warning_latency_ms = round((time.time() - t_sent) * 1000, 2)
        assert warning["type"] == "warning"
        assert warning["severity"] == "CRITICAL"
        print(f"  Turn 2 Update: Score={t_turn2['risk_score']}, Risk={t_turn2['risk_level']}")
        print(f"  Urgent Warning Delivered: \"{warning['title']}: {warning['message']}\"")
        print(f"  Measured End-to-End Warning Latency: {warning_latency_ms}ms")

        # Stop session cleanly
        ws.send_json({"type": "stop"})
        summary = ws.receive_json()
        assert summary["type"] == "session_summary"
        print(f"  Session Stopped Cleanly: Processed {summary['summary']['turns_processed']} turns, Duration={summary['summary']['duration_seconds']}s")

    print("\n" + "=" * 70)
    print("ALL PRIORITIES VERIFIED SUCCESSFULLY — ZERO FAILURES")
    print("=" * 70)

if __name__ == "__main__":
    run_e2e_verification()
