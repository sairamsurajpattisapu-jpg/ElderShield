import os
import json
import time
import base64
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware

from engine.models import (
    RiskAssessment,
    AnalyzeRequest,
    ProgressionResponse,
    DemoScenario,
    ConversationTurn,
    CallerLookupRequest,
    CallerIntelligenceResult
)
from engine.analyzer import engine, parse_raw_transcript
from engine.scenarios import DEMO_SCENARIOS, SCENARIO_LOOKUP
from engine.asr_service import asr_service
from engine.caller_intelligence import caller_service
from engine.stream_session import session_registry
from engine.privacy import redact_sensitive_data

# Initialize FastAPI application
app = FastAPI(
    title="ElderShield Scam Detection API",
    description="Conversational scam detection engine protecting elderly users against social engineering fraud with real-time live audio analysis.",
    version="2.1.0"
)

# CORS configuration via environment variables
raw_origins = os.getenv("ALLOWED_ORIGINS", "*")
allowed_origins = [orig.strip() for orig in raw_origins.split(",") if orig.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory recent analyses store (session-scoped)
RECENT_ANALYSES: List[RiskAssessment] = []

@app.on_event("startup")
def preseed_initial_benchmarks():
    """Initializes recent evaluations with verified demo scenarios for immediate inspection."""
    for sc in DEMO_SCENARIOS:
        assessment = engine.analyze(
            turns=sc.turns,
            raw_transcript=sc.raw_transcript,
            is_demo=True,
            demo_id=sc.id
        )
        RECENT_ANALYSES.append(assessment)

@app.get("/health")
@app.get("/api/health")
def health_status():
    """Service health and engine capability status."""
    return {
        "status": "healthy",
        "service": "ElderShield Scam Detection Core",
        "analysis_method": engine.ANALYSIS_METHOD,
        "engine_version": "2.1.0",
        "asr_engine": "faster-whisper-tiny" if asr_service.is_engine_ready else "faster-whisper-ready",
        "supported_languages": ["English", "Hindi (हिन्दी)", "Telugu (తెలుగు)", "Hinglish", "Teluglish"],
        "endpoints": [
            "GET /health",
            "POST /api/analyze",
            "POST /api/analyze/progression",
            "POST /api/analyze/audio",
            "GET /api/demo-scenarios",
            "WS /ws/live-call"
        ]
    }

@app.get("/api/demo-scenarios", response_model=List[DemoScenario])
def get_demo_scenarios():
    """Retrieve verified benchmark demo scenarios."""
    return DEMO_SCENARIOS

@app.get("/api/demo-scenarios/{scenario_id}", response_model=DemoScenario)
def get_demo_scenario_by_id(scenario_id: str):
    if scenario_id not in SCENARIO_LOOKUP:
        raise HTTPException(status_code=404, detail="Demo scenario not found")
    return SCENARIO_LOOKUP[scenario_id]

@app.post("/api/analyze", response_model=RiskAssessment)
def analyze_conversation(request: AnalyzeRequest):
    """
    Evaluates conversation transcript or turns across multi-vector behavioral signals.
    Produces comprehensive evidence-based risk assessment.
    """
    is_demo = False
    scenario_id = request.demo_scenario_id

    if scenario_id and scenario_id in SCENARIO_LOOKUP:
        sc = SCENARIO_LOOKUP[scenario_id]
        turns = sc.turns
        raw_text = sc.raw_transcript
        is_demo = True
    elif request.turns and len(request.turns) > 0:
        turns = request.turns
        raw_text = request.transcript or "\n".join([f"{t.speaker}: {t.text}" for t in turns])
    elif request.transcript and request.transcript.strip():
        raw_text = request.transcript.strip()
        turns = parse_raw_transcript(raw_text)
    else:
        raise HTTPException(
            status_code=400,
            detail="Either 'transcript', 'turns', or a valid 'demo_scenario_id' must be provided."
        )

    assessment = engine.analyze(
        turns=turns,
        raw_transcript=raw_text,
        is_demo=is_demo,
        demo_id=scenario_id
    )

    RECENT_ANALYSES.insert(0, assessment)
    if len(RECENT_ANALYSES) > 50:
        RECENT_ANALYSES.pop()

    return assessment

@app.post("/api/analyze/progression", response_model=ProgressionResponse)
def analyze_conversation_progression(request: AnalyzeRequest):
    """
    Incrementally analyzes conversation turn-by-turn to produce real-time timeline assessment.
    """
    assessment = analyze_conversation(request)
    return ProgressionResponse(
        id=assessment.id,
        turns=assessment.turn_progression,
        final_risk_level=assessment.risk_level,
        final_risk_score=assessment.risk_score,
        decision=assessment.decision,
        reasons=assessment.reasons,
        analysis_method=assessment.analysis_method
    )

@app.post("/api/analyze/audio")
async def analyze_audio_upload(
    file: UploadFile = File(...),
    language_hint: Optional[str] = Form("auto")
):
    """
    Accepts explicitly uploaded audio recording, performs automated speech recognition,
    and runs progressive scam detection on the resulting transcript.
    """
    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Invalid audio file or empty upload.")

    MAX_AUDIO_BYTES = 25 * 1024 * 1024 # 25MB security limit
    if len(audio_bytes) > MAX_AUDIO_BYTES:
        raise HTTPException(status_code=413, detail="Audio file exceeds maximum allowed limit of 25MB.")

    # 1. Transcribe audio with ASR service
    transcription = asr_service.transcribe_audio_bytes(
        audio_bytes=audio_bytes,
        filename=file.filename or "call_audio.wav",
        language_hint=language_hint
    )

    transcript_text = transcription.get("transcript", "").strip()
    if not transcript_text:
        transcript_text = "Caller: Audio uploaded with inaudible speech or background noise."

    # 2. Run detection engine on transcribed dialogue
    turns = parse_raw_transcript(transcript_text)
    assessment = engine.analyze(turns=turns, raw_transcript=transcript_text)

    RECENT_ANALYSES.insert(0, assessment)
    if len(RECENT_ANALYSES) > 50:
        RECENT_ANALYSES.pop()

    return {
        "audio_metrics": {
            "duration_seconds": transcription.get("duration_seconds", 0.0),
            "transcription_latency_ms": transcription.get("latency_ms", 0.0),
            "engine": transcription.get("engine_used", "faster-whisper"),
            "segments_count": len(transcription.get("segments", [])),
            "detected_language": transcription.get("language", "en")
        },
        "transcript": transcript_text,
        "segments": transcription.get("segments", []),
        "risk_assessment": assessment
    }

@app.post("/api/caller-lookup", response_model=CallerIntelligenceResult)
def lookup_caller_identity(request: CallerLookupRequest):
    """
    Performs E.164 normalization, carrier lookup, circle geocoding,
    and institutional identity spoofing conflict verification.
    """
    return caller_service.lookup_caller(
        phone_number=request.phone_number,
        claimed_organization=request.claimed_organization,
        country_hint=request.country_hint or "IN"
    )

@app.get("/api/recent", response_model=List[RiskAssessment])
def get_recent_analyses(limit: int = 15):
    """Retrieve recent conversation analyses for the current session."""
    return RECENT_ANALYSES[:limit]

# Real-Time Live Call WebSocket Pipeline
@app.websocket("/ws/live-call")
async def live_call_websocket(websocket: WebSocket):
    """
    Full-duplex WebSocket stream for real-time live scam detection.
    Receives live audio chunks and speech segments, extracts behavioral cues,
    and pushes instant warnings before the caller can execute fraudulent extraction.
    """
    await websocket.accept()
    session = session_registry.create_session(websocket)

    # Initial ready handshake
    await websocket.send_json({
        "type": "session_ready",
        "session_id": session.session_id,
        "status": "connected",
        "asr_ready": True,
        "timestamp": time.time()
    })

    try:
        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            msg_type = data.get("type")

            if msg_type == "audio_chunk":
                # Handle streaming audio chunk
                seq = data.get("sequence_id", 0)
                chunk_b64 = data.get("chunk", "")
                if chunk_b64:
                    try:
                        chunk_bytes = base64.b64decode(chunk_b64)
                        session.add_audio_chunk(chunk_bytes, seq)
                    except Exception:
                        pass

                await websocket.send_json({
                    "type": "chunk_ack",
                    "sequence_id": seq,
                    "buffered_bytes": len(session.audio_buffer)
                })

            elif msg_type == "transcript_segment":
                # Real-time incremental speech segment received
                speaker = data.get("speaker", "Caller")
                text = data.get("text", "")
                is_final = data.get("is_final", True)
                latency_ms = data.get("latency_ms", 0)

                assessment = session.add_transcript_segment(speaker=speaker, text=text)

                if assessment:
                    # Send live progressive risk update
                    await websocket.send_json({
                        "type": "risk_update",
                        "session_id": session.session_id,
                        "turn_number": len(session.turns),
                        "speaker": speaker,
                        "text": text,
                        "risk_level": assessment.risk_level,
                        "risk_score": assessment.risk_score,
                        "decision": assessment.decision,
                        "reasons": assessment.reasons,
                        "is_final": is_final,
                        "timestamp": time.time()
                    })

                    # If HIGH RISK detected, deliver immediate prominent warning (deduplicated by evidence fingerprint)
                    if assessment.risk_level == "HIGH_RISK":
                        warning_fp = f"HIGH_RISK:{':'.join(sorted([ev.exact_quote for ev in assessment.evidence[:3]]))}"
                        if session.last_warning_fingerprint != warning_fp:
                            session.last_warning_fingerprint = warning_fp
                            await websocket.send_json({
                                "type": "warning",
                                "severity": "CRITICAL",
                                "title": "URGENT FRAUD ALERT",
                                "message": assessment.recommended_action,
                                "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:2]],
                                "timestamp": time.time()
                            })

            elif msg_type == "caller_info":
                phone = data.get("phone_number", "")
                claimed = data.get("claimed_organization")
                caller_intel = caller_service.lookup_caller(phone, claimed)
                await websocket.send_json({
                    "type": "caller_intelligence",
                    "session_id": session.session_id,
                    "caller_data": caller_intel.model_dump(),
                    "timestamp": time.time()
                })
                if caller_intel.spoofing_suspected:
                    await websocket.send_json({
                        "type": "warning",
                        "severity": "CRITICAL",
                        "title": "SPOOFED IDENTITY DETECTED",
                        "message": caller_intel.advisory,
                        "evidence_quotes": [
                            f"Claimed Identity: {claimed or 'Institution'}",
                            f"Originating Number: {caller_intel.national_format or phone}"
                        ],
                        "timestamp": time.time()
                    })

            elif msg_type == "stop":
                if len(session.turns) == 0 and len(session.audio_buffer) >= 4000:
                    assessment = session.transcribe_buffered_audio()
                    if assessment:
                        await websocket.send_json({
                            "type": "risk_update",
                            "session_id": session.session_id,
                            "turn_number": len(session.turns),
                            "speaker": "Caller",
                            "text": session.turns[-1].text if session.turns else "",
                            "risk_level": assessment.risk_level,
                            "risk_score": assessment.risk_score,
                            "decision": assessment.decision,
                            "reasons": assessment.reasons,
                            "is_final": True,
                            "timestamp": time.time()
                        })
                        if assessment.risk_level == "HIGH_RISK":
                            await websocket.send_json({
                                "type": "warning",
                                "severity": "CRITICAL",
                                "title": "URGENT FRAUD ALERT",
                                "message": assessment.recommended_action,
                                "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:2]],
                                "timestamp": time.time()
                            })

                summary = session.get_summary_stats()
                await websocket.send_json({
                    "type": "session_summary",
                    "summary": summary
                })
                break

    except WebSocketDisconnect:
        pass
    except Exception as e:
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except Exception:
            pass
    finally:
        session_registry.remove_session(session.session_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
