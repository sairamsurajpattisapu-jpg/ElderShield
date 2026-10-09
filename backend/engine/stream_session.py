import time
import base64
import uuid
from typing import Dict, Any, List, Optional, Tuple
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
        self.unprocessed_offset = 0
        self.min_chunk_bytes_to_transcribe = 32000 * 2 # ~2.0 seconds of 16kHz 16-bit PCM
        self.last_segment_was_interim = False

    def add_audio_chunk(self, chunk_bytes: bytes, seq: int) -> int:
        self.last_activity = time.time()
        self.sequence_number = max(self.sequence_number, seq)
        if len(self.audio_buffer) + len(chunk_bytes) <= self.MAX_BUFFER_BYTES:
            self.audio_buffer.extend(chunk_bytes)
        return len(self.audio_buffer)

    def process_live_audio_chunk(
        self,
        chunk_bytes: bytes,
        seq: int,
        client_capture_time_ms: Optional[float] = None
    ) -> Optional[Tuple[RiskAssessment, str, Dict[str, Any]]]:
        """
        Processes streaming audio frames:
        Accumulates chunks, identifies segment boundaries, executes in-memory ASR,
        and triggers scam risk assessment with correlated monotonic timing.
        """
        t_recv = time.perf_counter()
        self.add_audio_chunk(chunk_bytes, seq)

        pending_bytes = len(self.audio_buffer) - self.unprocessed_offset
        if pending_bytes < self.min_chunk_bytes_to_transcribe:
            return None

        # Take newly accumulated audio slice
        audio_slice = bytes(self.audio_buffer[self.unprocessed_offset:])
        
        t_asr_start = time.perf_counter()
        asr_res = asr_service.transcribe_audio_bytes(
            audio_bytes=audio_slice,
            filename="live_chunk.pcm",
            language_hint=self.language_hint
        )
        asr_ms = round((time.perf_counter() - t_asr_start) * 1000, 2)
        
        raw_text = asr_res.get("transcript", "").strip()
        if not raw_text or "initializing in background" in raw_text or raw_text == "Audio segment processed.":
            return None

        # Advance processed offset to prevent duplicate re-transcription
        self.unprocessed_offset = len(self.audio_buffer)

        # Run behavioral scam analysis
        t_analysis_start = time.perf_counter()
        assessment = self.add_transcript_segment(speaker="Caller", text=raw_text, is_final=True)
        analysis_ms = round((time.perf_counter() - t_analysis_start) * 1000, 2)
        total_server_ms = round((time.perf_counter() - t_recv) * 1000, 2)

        timing_metrics = {
            "server_receipt_to_transcript_ms": asr_ms,
            "transcript_to_risk_decision_ms": analysis_ms,
            "total_server_turn_to_alert_ms": total_server_ms,
            "audio_duration_seconds": asr_res.get("duration_seconds", round(len(audio_slice) / 32000.0, 2)),
            "real_time_factor": asr_res.get("real_time_factor", 0.0),
            "client_capture_time_ms": client_capture_time_ms,
            "turn_number": len(self.turns)
        }

        if assessment:
            return (assessment, raw_text, timing_metrics)
        return None

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

        # Check if updating an in-flight utterance from the same speaker
        if self.turns and self.turns[-1].speaker.lower() == speaker.lower():
            prev_turn = self.turns[-1]
            if prev_turn.text.lower() == sanitized_text.lower():
                # Duplicate segment, reuse last assessment
                self.last_segment_was_interim = not is_final
                return self.last_assessment
            elif self.last_segment_was_interim:
                # Continuation/refinement of ongoing interim utterance: update in-place
                prev_turn.text = sanitized_text
                self.last_segment_was_interim = not is_final
                assessment = engine.analyze(
                    turns=self.turns,
                    raw_transcript="\n".join([f"{t.speaker}: {t.text}" for t in self.turns])
                )
                self.last_assessment = assessment
                return assessment
            elif sanitized_text.lower().startswith(prev_turn.text.lower()) and len(sanitized_text) > len(prev_turn.text):
                # Continuation of utterance: update in-place
                prev_turn.text = sanitized_text
                self.last_segment_was_interim = not is_final
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
        self.last_segment_was_interim = not is_final

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
        self.unprocessed_offset = 0
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

    @property
    def active_count(self) -> int:
        return len(self.sessions)

    def can_accept_session(self) -> bool:
        from config import settings
        self.cleanup_stale_sessions(settings.session_idle_timeout_seconds)
        return len(self.sessions) < settings.max_concurrent_sessions

    def create_session(self, websocket: Optional[WebSocket] = None, language_hint: str = "auto") -> Optional[LiveCallSession]:
        from config import settings
        self.cleanup_stale_sessions(settings.session_idle_timeout_seconds)
        if len(self.sessions) >= settings.max_concurrent_sessions:
            return None
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
        """Removes sessions idle for longer than configured timeout."""
        now = time.time()
        stale_ids = [
            sid for sid, sess in self.sessions.items()
            if (now - sess.last_activity) > max_idle_seconds
        ]
        for sid in stale_ids:
            self.remove_session(sid)

session_registry = SessionRegistry()


