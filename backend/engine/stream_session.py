import time
import base64
import uuid
from typing import Dict, Any, List, Optional
from fastapi import WebSocket

from .models import ConversationTurn, RiskAssessment
from .analyzer import engine
from .privacy import redact_sensitive_data
from .asr_service import asr_service

class LiveCallSession:
    """
    Manages a live real-time audio & conversational risk analysis session.
    Buffers incoming audio and transcript segments, measures latency,
    and streams immediate risk updates and warnings over WebSocket.
    """
    MAX_BUFFER_BYTES = 10 * 1024 * 1024 # 10MB memory bound
    MAX_TURNS = 50

    def __init__(self, session_id: str, websocket: WebSocket, language_hint: str = "auto"):
        self.session_id = session_id
        self.websocket = websocket
        self.language_hint = language_hint
        self.start_time = time.time()
        self.last_activity = time.time()
        self.turns: List[ConversationTurn] = []
        self.audio_buffer = bytearray()
        self.sequence_number = 0
        self.last_assessment: Optional[RiskAssessment] = None
        self.warning_sent = False
        self.last_warning_fingerprint: Optional[str] = None
        self.is_active = True

    def add_audio_chunk(self, chunk_bytes: bytes, seq: int) -> int:
        self.last_activity = time.time()
        self.sequence_number = max(self.sequence_number, seq)
        if len(self.audio_buffer) + len(chunk_bytes) <= self.MAX_BUFFER_BYTES:
            self.audio_buffer.extend(chunk_bytes)
        return len(self.audio_buffer)

    def add_transcript_segment(self, speaker: str, text: str, is_final: bool = True) -> Optional[RiskAssessment]:
        """
        Appends a newly transcribed speech segment and re-evaluates multi-turn risk velocity.
        Includes deduplication of duplicate segments and partial transcript updates.
        """
        self.last_activity = time.time()
        clean_text = text.strip()
        if not clean_text:
            return None

        # Redact sensitive data from stored dialogue turns (Workstream E)
        sanitized_text = redact_sensitive_data(clean_text)

        # Segment deduplication: check if identical to recent turn from same speaker
        if self.turns and self.turns[-1].speaker.lower() == speaker.lower():
            prev_turn = self.turns[-1]
            if prev_turn.text.lower() == sanitized_text.lower():
                # Duplicate segment, reuse last assessment
                return self.last_assessment
            elif sanitized_text.lower().startswith(prev_turn.text.lower()) and len(sanitized_text) > len(prev_turn.text):
                # Continuation of interim utterance: update in-place
                prev_turn.text = sanitized_text
                assessment = engine.analyze(
                    turns=self.turns,
                    raw_transcript="\n".join([f"{t.speaker}: {t.text}" for t in self.turns])
                )
                self.last_assessment = assessment
                return assessment

        turn_num = len(self.turns) + 1
        if len(self.turns) >= self.MAX_TURNS:
            self.turns.pop(0)

        turn = ConversationTurn(
            turn_number=turn_num,
            speaker=speaker,
            text=sanitized_text
        )
        self.turns.append(turn)

        # Re-evaluate live progressive risk
        assessment = engine.analyze(
            turns=self.turns,
            raw_transcript="\n".join([f"{t.speaker}: {t.text}" for t in self.turns])
        )
        self.last_assessment = assessment
        return assessment

    def transcribe_buffered_audio(self) -> Optional[RiskAssessment]:
        """
        Transcribes accumulated audio buffer using faster-whisper with Silero VAD.
        Appends discovered dialogue turns and returns updated risk assessment.
        """
        if len(self.audio_buffer) < 4000:
            return None

        try:
            transcription = asr_service.transcribe_audio_bytes(
                audio_bytes=bytes(self.audio_buffer),
                filename="stream.webm",
                language_hint=self.language_hint
            )
            text = transcription.get("transcript", "").strip()
            if text:
                return self.add_transcript_segment(speaker="Caller", text=text, is_final=True)
        except Exception as e:
            print(f"[LiveCallSession] Buffered audio transcription note: {e}")
        return None

    def clear_memory(self):
        """
        Zeroes out in-memory audio buffers and dialogue turns upon session closure
        to enforce zero-retention privacy standards (Workstream E).
        """
        self.is_active = False
        self.audio_buffer.clear()
        self.turns.clear()
        self.last_assessment = None

    def get_summary_stats(self) -> Dict[str, Any]:
        duration = round(time.time() - self.start_time, 2)
        return {
            "session_id": self.session_id,
            "duration_seconds": duration,
            "turns_processed": len(self.turns),
            "final_risk_level": self.last_assessment.risk_level if self.last_assessment else "INSUFFICIENT_EVIDENCE",
            "final_risk_score": self.last_assessment.risk_score if self.last_assessment else 0.0,
            "decision": self.last_assessment.decision if self.last_assessment else "INCONCLUSIVE",
            "audio_bytes_buffered": len(self.audio_buffer),
            "privacy_retention": "EPHEMERAL_CLEARED_ON_CLOSE"
        }

class SessionRegistry:
    def __init__(self):
        self.sessions: Dict[str, LiveCallSession] = {}

    def create_session(self, websocket: WebSocket, language_hint: str = "auto") -> LiveCallSession:
        self.cleanup_stale_sessions()
        sid = f"live_{uuid.uuid4().hex[:8]}"
        session = LiveCallSession(session_id=sid, websocket=websocket, language_hint=language_hint)
        self.sessions[sid] = session
        return session

    def get_session(self, session_id: str) -> Optional[LiveCallSession]:
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.clear_memory()
            del self.sessions[session_id]

    def cleanup_stale_sessions(self, max_idle_seconds: int = 1800):
        """Removes sessions idle for longer than 30 minutes."""
        now = time.time()
        stale_ids = [
            sid for sid, sess in self.sessions.items()
            if (now - sess.last_activity) > max_idle_seconds
        ]
        for sid in stale_ids:
            self.remove_session(sid)

session_registry = SessionRegistry()

