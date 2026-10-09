import os
import sys
import base64
import pytest
from fastapi.testclient import TestClient

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from main import app
from engine.stream_session import session_registry

client = TestClient(app)

def test_websocket_reconnection_and_cleanup():
    """Verify clean session lifecycle across client disconnects and reconnections."""
    initial_count = session_registry.active_count

    # Session 1 connects
    with client.websocket_connect("/ws/live-call") as ws1:
        ready1 = ws1.receive_json()
        assert ready1["type"] == "session_ready"
        session_id_1 = ready1["session_id"]
        assert session_registry.active_count == initial_count + 1

    # Session 1 closed: verify session unregistered
    assert session_registry.get_session(session_id_1) is None
    assert session_registry.active_count == initial_count

    # Session 2 connects (reconnection)
    with client.websocket_connect("/ws/live-call") as ws2:
        ready2 = ws2.receive_json()
        assert ready2["type"] == "session_ready"
        session_id_2 = ready2["session_id"]
        assert session_id_2 != session_id_1
        assert session_registry.active_count == initial_count + 1

    # Session 2 closed
    assert session_registry.get_session(session_id_2) is None
    assert session_registry.active_count == initial_count

def test_streaming_chunk_ack_and_sequencing():
    """Verify that audio chunk streaming acknowledges sequences properly."""
    with client.websocket_connect("/ws/live-call") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"

        # Stream small PCM chunk (100ms silence = 3200 bytes)
        silence_bytes = b"\x00" * 3200
        b64_chunk = base64.b64encode(silence_bytes).decode("ascii")

        ws.send_json({
            "type": "audio_chunk",
            "sequence_id": 1,
            "chunk": b64_chunk,
            "client_time_ms": 1000.0
        })

        ack = ws.receive_json()
        assert ack["type"] == "chunk_ack"
        assert ack["sequence_id"] == 1
        assert ack["buffered_bytes"] == 3200

        # Send sequence 2
        ws.send_json({
            "type": "audio_chunk",
            "sequence_id": 2,
            "chunk": b64_chunk,
            "client_time_ms": 1100.0
        })

        ack2 = ws.receive_json()
        assert ack2["type"] == "chunk_ack"
        assert ack2["sequence_id"] == 2
        assert ack2["buffered_bytes"] == 6400

def test_malformed_audio_chunk_resilience():
    """Verify WebSocket server handles corrupted or invalid base64 audio chunks without terminating connection."""
    with client.websocket_connect("/ws/live-call") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"

        # Send corrupted non-base64 payload
        ws.send_json({
            "type": "audio_chunk",
            "sequence_id": 99,
            "chunk": "NOT_VALID_BASE64_!@#$%",
            "client_time_ms": 500.0
        })

        ack = ws.receive_json()
        assert ack["type"] == "chunk_ack"
        assert ack["sequence_id"] == 99

        # Ping server after error to verify socket is healthy
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"

def test_simultaneous_isolated_sessions():
    """Verify that multiple concurrent WebSocket sessions maintain absolute memory isolation."""
    with client.websocket_connect("/ws/live-call") as ws1:
        ready1 = ws1.receive_json()
        assert ready1["type"] == "session_ready"
        sid1 = ready1["session_id"]

        with client.websocket_connect("/ws/live-call") as ws2:
            ready2 = ws2.receive_json()
            assert ready2["type"] == "session_ready"
            sid2 = ready2["session_id"]
            assert sid1 != sid2

            # Stream benign utterance in session 1
            ws1.send_json({
                "type": "transcript_segment",
                "speaker": "Caller",
                "text": "Good morning Mrs. Sharma, your passbook is ready."
            })
            update1 = ws1.receive_json()
            assert update1["type"] == "risk_update"
            assert update1["risk_level"] in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")

            # Stream scam utterance in session 2
            ws2.send_json({
                "type": "transcript_segment",
                "speaker": "Caller",
                "text": "This is CBI Police. You are under digital arrest. Transfer 50,000 to escrow account."
            })
            update2 = ws2.receive_json()
            assert update2["type"] == "risk_update"
            assert update2["risk_level"] == "HIGH_RISK"

            # Check that session 1 is completely unpolluted by session 2
            sess1 = session_registry.get_session(sid1)
            sess2 = session_registry.get_session(sid2)
            assert sess1 is not None and sess2 is not None
            assert len(sess1.turns) == 1
            assert len(sess2.turns) == 1
            assert "CBI" not in sess1.turns[0].text
            assert sess1.last_assessment.risk_level in ("LOW_RISK", "INSUFFICIENT_EVIDENCE")

def test_empty_and_corrupt_pcm_buffers():
    """Verify streaming handles empty chunks and random byte noise gracefully."""
    with client.websocket_connect("/ws/live-call") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"

        # 1. Empty base64
        ws.send_json({"type": "audio_chunk", "sequence_id": 1, "chunk": ""})
        ack1 = ws.receive_json()
        assert ack1["type"] == "chunk_ack"

        # 2. Corrupt noise bytes
        noise = base64.b64encode(b"\xFF\xFE\x00\x01\x80\x7F" * 100).decode("ascii")
        ws.send_json({"type": "audio_chunk", "sequence_id": 2, "chunk": noise})
        ack2 = ws.receive_json()
        assert ack2["type"] == "chunk_ack"

        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"

def test_long_silence_streaming():
    """Verify that multiple seconds of pure silence accumulate safely without false alarms."""
    with client.websocket_connect("/ws/live-call") as ws:
        ready = ws.receive_json()
        assert ready["type"] == "session_ready"

        # Stream 2.0s of silence (64,000 bytes)
        silence_chunk = base64.b64encode(b"\x00" * 32000).decode("ascii")
        for seq in range(1, 3):
            ws.send_json({"type": "audio_chunk", "sequence_id": seq, "chunk": silence_chunk})
            ack = ws.receive_json()
            assert ack["type"] == "chunk_ack"
            assert ack["sequence_id"] == seq

        # Ensure no accidental scam alerts fired during pure silence
        ws.send_json({"type": "ping"})
        pong = ws.receive_json()
        assert pong["type"] == "pong"

def test_memory_bounded_buffer_and_clear():
    """Verify that LiveCallSession enforces MAX_BUFFER_BYTES bound and clear_memory() purges all buffers."""
    from engine.stream_session import LiveCallSession

    session = LiveCallSession(session_id="test_bound", websocket=None)
    # Add large chunk
    chunk_1mb = b"\x00" * (1024 * 1024)
    for i in range(15):
        session.add_audio_chunk(chunk_1mb, seq=i)

    # Buffer must not exceed 10MB
    assert len(session.audio_buffer) <= session.MAX_BUFFER_BYTES

    # Verify clear_memory purges completely
    session.clear_memory()
    assert len(session.audio_buffer) == 0
    assert len(session.turns) == 0
    assert session.is_active is False

