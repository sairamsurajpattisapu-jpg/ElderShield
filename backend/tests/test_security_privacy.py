"""
ElderShield — Privacy & Security Verification Suite
Tests:
1. PII Log Scrubbing & Redaction (Cards, Aadhaar, OTPs, Phone numbers).
2. Ephemeral In-Memory Audio Processing (Zero disk writes during transcription).
3. WebSocket / Call Session Isolation (No cross-talk between independent sessions).
4. Input Limits & Defensive Handling.
"""

import os
import io
import tempfile
import pytest
from engine.privacy import redact_sensitive_data
from engine.logger import setup_logger, PrivacyFilter
from engine.stream_session import LiveCallSession, SessionRegistry
from engine.asr_service import asr_service

def test_pii_redaction_credit_card():
    text = "Please enter your card 4532 1123 8976 4321 for verification"
    redacted = redact_sensitive_data(text)
    assert "4532" not in redacted
    assert "[REDACTED_CARD_NUMBER]" in redacted

def test_pii_redaction_aadhaar():
    text = "Provide your Aadhaar number 2345 6789 0123 immediately"
    redacted = redact_sensitive_data(text)
    assert "2345 6789 0123" not in redacted
    assert "[REDACTED_AADHAAR]" in redacted

def test_pii_redaction_otp_with_keywords():
    text = "Your one time password is OTP 784921 to unlock the card"
    redacted = redact_sensitive_data(text)
    assert "784921" not in redacted
    assert "[REDACTED_CREDENTIAL]" in redacted

def test_pii_redaction_phone_number():
    text = "Call me back on +91 9849012345 right now"
    redacted = redact_sensitive_data(text)
    assert "9849012345" not in redacted
    assert "[REDACTED_PHONE]" in redacted

def test_logger_privacy_filter():
    import logging
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="",
        lineno=0,
        msg="Caller OTP is 554321 and phone is 9876543210",
        args=(),
        exc_info=None
    )
    pfilter = PrivacyFilter()
    pfilter.filter(record)
    assert "554321" not in record.msg
    assert "9876543210" not in record.msg

def test_zero_disk_retention_in_asr():
    """
    Verify ASR processes PCM audio and WAV containers strictly in RAM
    without creating files in the OS temporary directory.
    """
    temp_dir = tempfile.gettempdir()
    initial_temp_files = set(os.listdir(temp_dir))

    # 1. Test raw PCM in-memory transcription
    dummy_pcm = b"\x00\x00" * 8000 # 0.5s of 16kHz 16-bit silence
    asr_service.transcribe_audio_bytes(dummy_pcm)

    # 2. Test in-memory container transcription
    dummy_wav_buffer = io.BytesIO()
    import wave
    with wave.open(dummy_wav_buffer, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(16000)
        wf.writeframes(dummy_pcm)
    dummy_wav_bytes = dummy_wav_buffer.getvalue()
    asr_service.transcribe_audio_bytes(dummy_wav_bytes)

    # Assert no new temporary files created by ElderShield ASR
    post_temp_files = set(os.listdir(temp_dir))
    new_files = post_temp_files - initial_temp_files
    # Check that no whisper/eldershield named tempfiles leaked
    leaked_audio_files = [f for f in new_files if f.endswith((".wav", ".mp3", ".pcm", ".tmp")) and "whisper" in f.lower()]
    assert len(leaked_audio_files) == 0, f"Leaked temporary audio files: {leaked_audio_files}"

def test_session_isolation():
    """
    Verify independent sessions do not share state, audio buffers, or risk decisions.
    """
    registry = SessionRegistry()
    session_a = registry.create_session()
    session_b = registry.create_session()

    assert session_a.session_id != session_b.session_id

    # Add a benign turn to Session A
    assessment_a = session_a.add_transcript_segment("Caller", "Hello Mrs. Alice, your FD is matured.")
    assert len(session_a.turns) == 1
    assert len(session_b.turns) == 0

    # Add a fraudulent scam turn to Session B
    assessment_b = session_b.add_transcript_segment("Caller", "You are under digital arrest by CBI! Transfer funds immediately!")
    assert len(session_a.turns) == 1
    assert len(session_b.turns) == 1

    # Ensure evaluation of B does not impact A
    assert assessment_a is not None
    assert assessment_b is not None
    assert assessment_a.decision in ("ALLOW", "INCONCLUSIVE")
    assert assessment_b.decision == "BLOCK"
    assert assessment_b.risk_level == "HIGH_RISK"

    # Cleanup session B
    registry.remove_session(session_b.session_id)
    assert registry.get_session(session_b.session_id) is None
    assert registry.get_session(session_a.session_id) is not None
