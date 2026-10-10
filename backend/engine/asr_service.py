import os
import io
import time
import tempfile
from typing import Dict, Any, List, Optional, Tuple

# Try importing faster-whisper
_FASTER_WHISPER_AVAILABLE = False
_whisper_model = None

try:
    from faster_whisper import WhisperModel
    _FASTER_WHISPER_AVAILABLE = True
except ImportError:
    _FASTER_WHISPER_AVAILABLE = False

class SpeechRecognitionService:
    """
    Tiered Speech-to-Text service supporting faster-whisper on CPU/GPU
    with fallback decoding and benchmark synthesis.
    """
    def __init__(self, model_size: str = "tiny"):
        self.model_size = model_size
        self.model = None
        self.initialization_error: Optional[str] = None
        self.model_status: str = "uninitialized"
        self.device: str = os.getenv("WHISPER_DEVICE", "cpu")
        self.compute_type: str = os.getenv("WHISPER_COMPUTE_TYPE", "int8")
        self._init_model()

    def _init_model(self):
        global _whisper_model
        if not _FASTER_WHISPER_AVAILABLE:
            self.model_status = "unavailable_dependency_missing"
            self.initialization_error = "faster-whisper package not installed or CTranslate2 runtime unavailable"
            return

        if _whisper_model is None:
            t0 = time.time()
            try:
                # Load quantized CPU/configured-device optimized model
                _whisper_model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type,
                    cpu_threads=4
                )
                self.model_status = "ready"
                self.initialization_error = None
            except Exception as e:
                self.model_status = "failed"
                self.initialization_error = str(e)
                print(f"[ASRService] Note: Faster-Whisper local model init deferred: {e}")
        else:
            self.model_status = "ready"

        self.model = _whisper_model

    @property
    def is_engine_ready(self) -> bool:
        return self.model is not None and self.model_status == "ready"

    def get_engine_diagnostics(self) -> Dict[str, Any]:
        """Provides transparent status check on speech model readiness and runtime health."""
        return {
            "library_installed": _FASTER_WHISPER_AVAILABLE,
            "engine_ready": self.is_engine_ready,
            "status": self.model_status,
            "model_size": self.model_size,
            "device": self.device,
            "compute_type": self.compute_type,
            "initialization_error": self.initialization_error
        }

    def transcribe_audio_bytes(
        self,
        audio_bytes: bytes,
        filename: str = "audio.wav",
        language_hint: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Transcribes audio data bytes in-memory with ZERO persistent disk writes.
        Supports WAV, MP3, M4A, OGG, WebM, FLAC (via PyAV in-memory BytesIO),
        and raw 16kHz 16-bit Mono PCM (from WebSocket stream and Android companion).
        Instruments exact monotonic timing for ASR inference and VAD.
        """
        t_start = time.perf_counter()

        if not audio_bytes or len(audio_bytes) < 100:
            return {
                "transcript": "",
                "segments": [],
                "language": "en",
                "duration_seconds": 0.0,
                "latency_ms": 0.0,
                "inference_latency_ms": 0.0,
                "prep_latency_ms": 0.0,
                "real_time_factor": 0.0,
                "engine_used": f"faster-whisper-{self.model_size}",
                "disk_retention": "ZERO_DISK_IN_MEMORY"
            }

        # Ensure model is initialized if library became available
        if self.model is None and _FASTER_WHISPER_AVAILABLE:
            self._init_model()

        if self.model is None:
            return {
                "transcript": "",
                "segments": [],
                "error": self.initialization_error or "faster-whisper model not initialized",
                "language": "en",
                "duration_seconds": 0.0,
                "latency_ms": round((time.perf_counter() - t_start) * 1000, 2),
                "inference_latency_ms": 0.0,
                "engine_used": "unavailable",
                "disk_retention": "ZERO_DISK_IN_MEMORY"
            }

        try:
            import numpy as np

            # Normalize language code (e.g., 'en-IN' -> 'en', 'hi-IN' -> 'hi', 'te-IN' -> 'te')
            lang = None
            if language_hint and language_hint != "auto":
                lang = language_hint.split("-")[0].lower()
                if lang not in ("en", "hi", "te", "mr", "ta", "bn", "gu", "kn", "ml", "pa"):
                    lang = None

            # Detect whether input is a known audio container format or raw 16-bit PCM
            lower_name = (filename or "").lower()
            is_container = (
                audio_bytes.startswith(b"RIFF") or  # WAV
                audio_bytes.startswith(b"ID3") or   # MP3 with ID3v2
                (len(audio_bytes) > 2 and audio_bytes[:2] in (b"\xff\xfb", b"\xff\xf3", b"\xff\xf2")) or  # MP3 frame sync
                b"ftyp" in audio_bytes[:16] or      # M4A / MP4 / AAC
                audio_bytes.startswith(b"OggS") or  # OGG / Opus
                audio_bytes.startswith(b"fLaC") or  # FLAC
                audio_bytes.startswith(b"\x1a\x45\xdf\xa3") or  # WebM / Matroska
                lower_name.endswith((".wav", ".mp3", ".m4a", ".mp4", ".ogg", ".flac", ".webm", ".aac"))
            )

            is_explicit_pcm = lower_name.endswith((".pcm", ".raw")) or not is_container

            t_prep = time.perf_counter()
            if is_explicit_pcm and len(audio_bytes) % 2 == 0:
                # Convert raw 16-bit 16kHz mono PCM directly to float32 numpy array in RAM
                audio_input = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
            else:
                # Standard audio container format (WAV, MP3, etc.) decoded in-memory via PyAV
                audio_input = io.BytesIO(audio_bytes)

            prep_duration_ms = round((time.perf_counter() - t_prep) * 1000, 2)

            t_infer_start = time.perf_counter()
            vad_params = dict(min_silence_duration_ms=250, threshold=0.35, speech_pad_ms=200) if is_explicit_pcm else dict(min_silence_duration_ms=300)
            segments_generator, info = self.model.transcribe(
                audio_input,
                beam_size=3,
                language=lang,
                vad_filter=True,
                vad_parameters=vad_params
            )

            segments = []
            full_text_parts = []
            for seg in segments_generator:
                text_clean = seg.text.strip()
                if text_clean:
                    full_text_parts.append(text_clean)
                    segments.append({
                        "start": round(seg.start, 2),
                        "end": round(seg.end, 2),
                        "text": text_clean
                    })

            full_transcript = " ".join(full_text_parts)
            duration = info.duration if hasattr(info, "duration") else 0.0
            detected_lang = info.language if hasattr(info, "language") else (lang or "en")
            infer_duration_ms = round((time.perf_counter() - t_infer_start) * 1000, 2)
            total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
            rtf = round(infer_duration_ms / (duration * 1000), 3) if duration > 0 else 0.0

            return {
                "transcript": full_transcript,
                "segments": segments,
                "language": detected_lang,
                "duration_seconds": round(duration, 2),
                "latency_ms": total_duration_ms,
                "inference_latency_ms": infer_duration_ms,
                "prep_latency_ms": prep_duration_ms,
                "real_time_factor": rtf,
                "engine_used": f"faster-whisper-{self.model_size}",
                "transcription_architecture": "chunked_segment_vad",
                "disk_retention": "ZERO_DISK_IN_MEMORY"
            }
        except Exception as e:
            total_duration_ms = round((time.perf_counter() - t_start) * 1000, 2)
            print(f"[ASRService] In-memory transcription exception: {e}")
            return {
                "transcript": "",
                "segments": [],
                "error": f"Audio transcription failed: {str(e)}",
                "language": language_hint or "en",
                "duration_seconds": 0.0,
                "latency_ms": total_duration_ms,
                "inference_latency_ms": 0.0,
                "engine_used": f"faster-whisper-{self.model_size}",
                "disk_retention": "ZERO_DISK_IN_MEMORY"
            }

asr_service = SpeechRecognitionService()
