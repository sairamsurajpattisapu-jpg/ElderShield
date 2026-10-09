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
        self.turns: List[ConversationTurn] = []
        self.audio_buffer = bytearray()
        self.sequence_number = 0
        self.last_assessment: Optional[RiskAssessment] = None
        self.warning_sent = False
        self.is_active = True

    def add_audio_chunk(self, chunk_bytes: bytes, seq: int) -> int:
        self.sequence_number = max(self.sequence_number, seq)
        if len(self.audio_buffer) + len(chunk_bytes) <= self.MAX_BUFFER_BYTES:
            self.audio_buffer.extend(chunk_bytes)
        return len(self.audio_buffer)

    def add_transcript_segment(self, speaker: str, text: str) -> Optional[RiskAssessment]:
        """
        Appends a newly transcribed speech segment and re-evaluates multi-turn risk velocity.
        """
        clean_text = text.strip()
        if not clean_text:
            return None

        turn_num = len(self.turns) + 1
        if len(self.turns) >= self.MAX_TURNS:
            self.turns.pop(0)

        turn = ConversationTurn(
            turn_number=turn_num,
            speaker=speaker,
            text=clean_text
        )
        self.turns.append(turn)

        # Re-evaluate live progressive risk
        assessment = engine.analyze(
            turns=self.turns,
            raw_transcript="\n".join([f"{t.speaker}: {t.text}" for t in self.turns])
        )
        self.last_assessment = assessment
        return assessment

    def get_summary_stats(self) -> Dict[str, Any]:
        duration = round(time.time() - self.start_time, 2)
        return {
            "session_id": self.session_id,
            "duration_seconds": duration,
            "turns_processed": len(self.turns),
            "final_risk_level": self.last_assessment.risk_level if self.last_assessment else "INSUFFICIENT_EVIDENCE",
            "final_risk_score": self.last_assessment.risk_score if self.last_assessment else 0.0,
            "decision": self.last_assessment.decision if self.last_assessment else "INCONCLUSIVE",
            "audio_bytes_buffered": len(self.audio_buffer)
        }

class SessionRegistry:
    def __init__(self):
        self.sessions: Dict[str, LiveCallSession] = {}

    def create_session(self, websocket: WebSocket, language_hint: str = "auto") -> LiveCallSession:
        sid = f"live_{uuid.uuid4().hex[:8]}"
        session = LiveCallSession(session_id=sid, websocket=websocket, language_hint=language_hint)
        self.sessions[sid] = session
        return session

    def get_session(self, session_id: str) -> Optional[LiveCallSession]:
        return self.sessions.get(session_id)

    def remove_session(self, session_id: str):
        if session_id in self.sessions:
            self.sessions[session_id].is_active = False
            del self.sessions[session_id]

session_registry = SessionRegistry()
