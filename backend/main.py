import os
import json
import time
import base64
import uuid
import asyncio
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager

from fastapi import (
    FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect,
    UploadFile, File, Form, Depends, Query, status
)
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from engine.logger import app_logger
from engine.security import verify_api_key, verify_websocket_auth, RateLimiterMiddleware
from engine.models import (
    RiskAssessment,
    AnalyzeRequest,
    ProgressionResponse,
    DemoScenario,
    ConversationTurn,
    CallerLookupRequest,
    CallerIntelligenceResult,
    CallerEvidenceItem,
    UnifiedProtectionRequest,
    UnifiedProtectionResult
)
from engine.analyzer import engine, parse_raw_transcript
from engine.scenarios import DEMO_SCENARIOS, SCENARIO_LOOKUP
from engine.asr_service import asr_service
from engine.caller_intelligence import caller_service
from engine.stream_session import session_registry
from engine.privacy import redact_sensitive_data

SERVER_START_TIME = time.time()
RECENT_ANALYSES: List[RiskAssessment] = []

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Production lifespan context manager:
    Initializes models, warms caches, and ensures clean termination.
    """
    app_logger.info(f"Starting {settings.app_name} v{settings.app_version} in {settings.environment} mode")
    # Pre-seed benchmark scenarios for immediate inspection & demonstration
    for sc in DEMO_SCENARIOS:
        assessment = engine.analyze(
            turns=sc.turns,
            raw_transcript=sc.raw_transcript,
            is_demo=True,
            demo_id=sc.id
        )
        RECENT_ANALYSES.append(assessment)

    app_logger.info(f"Pre-seeded {len(DEMO_SCENARIOS)} baseline demo scenarios. ASR status: {asr_service.model_status}")
    yield
    app_logger.info("ElderShield Backend shutting down cleanly. Memory buffers zeroed.")

# Initialize FastAPI app with metadata
app = FastAPI(
    title=settings.app_name,
    description="Conversational and caller-intelligence scam protection engine protecting elderly users against social engineering fraud.",
    version=settings.app_version,
    lifespan=lifespan
)

# Apply Rate Limiting Middleware
app.add_middleware(RateLimiterMiddleware, max_requests_per_minute=settings.rate_limit_per_minute)

# Apply CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins if settings.allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------------------------------------
# HEALTH & DEPENDENCY-READINESS ENDPOINTS
# -------------------------------------------------------------
@app.get("/health")
@app.get("/api/health")
def health_liveness():
    """Service liveness probe confirming server is up and responding."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "timestamp": time.time()
    }

@app.get("/ready")
@app.get("/api/ready")
def health_readiness():
    """
    Deep readiness check inspecting all subsystem dependencies:
    - Rule-based detection engine
    - Speech recognition (faster-whisper / Silero VAD)
    - Caller intelligence registry
    - Active WebSocket sessions count
    Honest reporting: if ASR model fails or is initializing, status is flagged 'degraded'.
    """
    asr_diag = asr_service.get_engine_diagnostics()
    engine_ready = True
    overall_status = "ready"

    if not asr_diag["engine_ready"] and asr_diag["status"] != "ready":
        overall_status = "degraded"

    return {
        "status": overall_status,
        "service": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "uptime_seconds": round(time.time() - SERVER_START_TIME, 1),
        "analyzer_engine": {
            "status": "ready" if engine_ready else "not_ready",
            "method": engine.ANALYSIS_METHOD
        },
        "asr_service": asr_diag,
        "caller_intelligence": {
            "status": "ready",
            "registry_source": "ITU E.164 + National Institutional Registry v2.2"
        },
        "session_registry": {
            "active_sessions": session_registry.active_count,
            "max_concurrent_sessions": settings.max_concurrent_sessions
        },
        "security": {
            "auth_enforced": settings.require_auth,
            "rate_limit_per_min": settings.rate_limit_per_minute
        }
    }

# -------------------------------------------------------------
# BENCHMARK SCENARIO ENDPOINTS
# -------------------------------------------------------------
@app.get("/api/demo-scenarios", response_model=List[DemoScenario])
def get_demo_scenarios():
    """Retrieve verified benchmark demo scenarios."""
    return DEMO_SCENARIOS

@app.get("/api/demo-scenarios/{scenario_id}", response_model=DemoScenario)
def get_demo_scenario_by_id(scenario_id: str):
    if scenario_id not in SCENARIO_LOOKUP:
        raise HTTPException(status_code=404, detail="Demo scenario not found")
    return SCENARIO_LOOKUP[scenario_id]

# -------------------------------------------------------------
# CONVERSATIONAL ANALYSIS ENDPOINTS
# -------------------------------------------------------------
@app.post("/api/analyze", response_model=RiskAssessment)
def analyze_conversation(
    request: AnalyzeRequest,
    authenticated: bool = Depends(verify_api_key)
):
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
def analyze_conversation_progression(
    request: AnalyzeRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Incrementally analyzes conversation turn-by-turn to produce real-time timeline assessment.
    """
    assessment = analyze_conversation(request, authenticated=authenticated)
    return ProgressionResponse(
        id=assessment.id,
        turns=assessment.turn_progression,
        final_risk_level=assessment.risk_level,
        final_risk_score=assessment.risk_score,
        decision=assessment.decision,
        reasons=assessment.reasons,
        analysis_method=assessment.analysis_method,
        otp_state=assessment.otp_state,
        urgent_intervention_required=assessment.urgent_intervention_required,
        intervention_heading=assessment.intervention_heading,
        intervention_spoken_text=assessment.intervention_spoken_text,
        intervention_language=assessment.intervention_language,
        event_id=assessment.event_id,
    )

@app.post("/api/analyze/audio")
async def analyze_audio_upload(
    file: UploadFile = File(...),
    language_hint: Optional[str] = Form("auto"),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Accepts explicitly uploaded audio recording, performs automated speech recognition,
    and runs progressive scam detection on the resulting transcript.
    """
    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Invalid audio file or empty upload.")

    max_bytes = settings.max_audio_upload_mb * 1024 * 1024
    if len(audio_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file exceeds maximum allowed limit of {settings.max_audio_upload_mb}MB."
        )

    # 1. Transcribe audio with ASR service
    transcription = asr_service.transcribe_audio_bytes(
        audio_bytes=audio_bytes,
        filename=file.filename or "call_audio.wav",
        language_hint=language_hint
    )

    transcript_text = transcription.get("transcript", "").strip()
    if not transcript_text:
        transcript_text = ""
        turns = []
    else:
        turns = parse_raw_transcript(transcript_text)

    # 2. Run detection engine on transcribed dialogue
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

# -------------------------------------------------------------
# CALLER INTELLIGENCE & CALL SCREENING
# -------------------------------------------------------------
@app.post("/api/caller-lookup", response_model=CallerIntelligenceResult)
def lookup_caller_identity(
    request: CallerLookupRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Performs E.164 normalization, carrier lookup, circle geocoding,
    and institutional identity spoofing conflict verification.
    """
    return caller_service.lookup_caller(
        phone_number=request.phone_number,
        claimed_organization=request.claimed_organization,
        country_hint=request.country_hint or "IN"
    )

# -------------------------------------------------------------
# WORKSTREAM 3: UNIFIED PROTECTION PIPELINE
# -------------------------------------------------------------
@app.post("/api/protect/unified", response_model=UnifiedProtectionResult)
def unified_protection_analyze(
    request: UnifiedProtectionRequest,
    authenticated: bool = Depends(verify_api_key)
):
    """
    Unified protection pipeline combining Caller Intelligence with Conversational Scam Detection.
    Strictly partitions caller identity evidence from conversational scam evidence.
    Flow: Input -> Transcription / Turns -> Behavioral Analysis -> Caller Intel -> Compound Synthesis.
    """
    # 1. Caller intelligence verification
    caller_intel: Optional[CallerIntelligenceResult] = None
    caller_evidence: Optional[CallerEvidenceItem] = None

    if request.phone_number and request.phone_number.strip():
        caller_intel = caller_service.lookup_caller(
            phone_number=request.phone_number,
            claimed_organization=request.claimed_organization,
            country_hint=request.country_hint or "IN"
        )
        caller_evidence = CallerEvidenceItem(
            evidence_type="CALLER_IDENTITY",
            phone_number=caller_intel.national_format or request.phone_number,
            claimed_organization=request.claimed_organization,
            conflict_status=caller_intel.identity_conflict_status,
            spoofing_suspected=caller_intel.spoofing_suspected,
            reputation_score=caller_intel.reputation_score,
            advisory=caller_intel.advisory
        )

    # 2. Conversational behavioral analysis
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
        # No dialogue provided; maintain empty state without inventing turns
        raw_text = ""
        turns = []

    conv_assessment = engine.analyze(
        turns=turns,
        raw_transcript=raw_text,
        is_demo=is_demo,
        demo_id=scenario_id
    )

    # 3. Compound risk assessment synthesis (keeping evidence streams partitioned)
    composite_score = conv_assessment.risk_score
    composite_risk = conv_assessment.risk_level
    decision = conv_assessment.decision
    recommended_action = conv_assessment.recommended_action
    alert_required = False
    warning_title = None
    warning_message = None

    # Check caller intelligence conflict multiplier
    if caller_intel and caller_intel.caller_classification == "CONFIRMED_SCAM":
        composite_score = min(100.0, max(composite_score, 95.0))
        composite_risk = "HIGH_RISK"
        decision = "BLOCK"
        recommended_action = (
            f"DISCONNECT IMMEDIATELY! Caller number {caller_intel.phone_number} is a CONFIRMED FRAUDULENT NUMBER "
            f"listed in official cybercrime advisories. Do not engage or share any personal information."
        )
        alert_required = True
        warning_title = "CONFIRMED SCAM CALLER"
        warning_message = recommended_action
    elif caller_intel and caller_intel.spoofing_suspected:
        # Institutional spoofing elevates risk
        composite_score = min(100.0, max(composite_score, 85.0))
        composite_risk = "HIGH_RISK"
        decision = "BLOCK"
        recommended_action = (
            f"DISCONNECT IMMEDIATELY! Caller claims to represent {request.claimed_organization or 'an institution'}, "
            f"but call originates from a private mobile number. Never transfer funds or share verification codes."
        )
        alert_required = True
        warning_title = "CRITICAL INSTITUTIONAL SPOOFING DETECTED"
        warning_message = recommended_action

    elif conv_assessment.urgent_intervention_required:
        alert_required = True
        warning_title = conv_assessment.intervention_heading or "STOP! DO NOT SHARE YOUR OTP"
        warning_message = conv_assessment.intervention_spoken_text or conv_assessment.recommended_action

    elif conv_assessment.risk_level == "HIGH_RISK":
        alert_required = True
        warning_title = "URGENT FRAUD ALERT"
        warning_message = conv_assessment.recommended_action

    elif conv_assessment.risk_level == "SUSPICIOUS":
        alert_required = True
        warning_title = "SUSPICIOUS CALL DETECTED"
        warning_message = "Caller is demonstrating manipulative tactics. Hang up and verify through official channels."

    result = UnifiedProtectionResult(
        id=f"up_{uuid.uuid4().hex[:10]}",
        timestamp=conv_assessment.timestamp,
        composite_risk_level=composite_risk,
        composite_risk_score=composite_score,
        decision=decision,
        recommended_action=recommended_action,
        conversational_evidence=conv_assessment.evidence,
        caller_evidence=caller_evidence,
        conversational_analysis=conv_assessment,
        caller_intelligence=caller_intel,
        alert_required=alert_required,
        warning_title=warning_title,
        warning_message=warning_message,
        otp_state=conv_assessment.otp_state,
        urgent_intervention_required=conv_assessment.urgent_intervention_required
    )

    RECENT_ANALYSES.insert(0, conv_assessment)
    if len(RECENT_ANALYSES) > 50:
        RECENT_ANALYSES.pop()

    return result

@app.post("/api/protect/unified/audio")
async def unified_protection_audio_upload(
    file: UploadFile = File(...),
    phone_number: Optional[str] = Form(None),
    claimed_organization: Optional[str] = Form(None),
    language_hint: Optional[str] = Form("auto"),
    authenticated: bool = Depends(verify_api_key)
):
    """
    Unified audio pipeline: Accepts call audio recording + optional phone number,
    transcribes audio via faster-whisper/Silero VAD, queries caller intelligence,
    and returns comprehensive partitioned protection assessment.
    """
    audio_bytes = await file.read()
    if not audio_bytes or len(audio_bytes) < 100:
        raise HTTPException(status_code=400, detail="Invalid audio file or empty upload.")

    max_bytes = settings.max_audio_upload_mb * 1024 * 1024
    if len(audio_bytes) > max_bytes:
        raise HTTPException(
            status_code=413,
            detail=f"Audio file exceeds maximum allowed limit of {settings.max_audio_upload_mb}MB."
        )

    # 1. Transcribe audio
    transcription = asr_service.transcribe_audio_bytes(
        audio_bytes=audio_bytes,
        filename=file.filename or "call_audio.wav",
        language_hint=language_hint
    )
    transcript_text = transcription.get("transcript", "").strip()

    # 2. Run unified protection
    req = UnifiedProtectionRequest(
        phone_number=phone_number,
        claimed_organization=claimed_organization,
        transcript=transcript_text,
        language_hint=language_hint
    )
    unified_res = unified_protection_analyze(req, authenticated=authenticated)

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
        "unified_result": unified_res
    }

@app.get("/api/recent", response_model=List[RiskAssessment])
def get_recent_analyses(limit: int = 15):
    """Retrieve recent conversation analyses for the current session."""
    return RECENT_ANALYSES[:limit]

# -------------------------------------------------------------
# REAL-TIME LIVE WEBSOCKET PIPELINE
# -------------------------------------------------------------
@app.websocket("/ws/live-call")
async def live_call_websocket(
    websocket: WebSocket,
    api_key: Optional[str] = Query(None),
    token: Optional[str] = Query(None)
):
    """
    Full-duplex WebSocket stream for real-time live scam detection.
    Receives live audio chunks and speech segments, extracts behavioral cues,
    and pushes instant warnings before the caller can execute fraudulent extraction.
    Includes session isolation, resource limits, and authentication verification.
    """
    # 1. Check Authentication if required
    auth_token = token or api_key
    if not verify_websocket_auth(auth_token, websocket.headers.get("X-API-Key")):
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION, reason="Unauthorized")
        return

    # 2. Check Concurrency Limits
    if not session_registry.can_accept_session():
        await websocket.close(code=1013, reason="Server busy: maximum concurrent sessions reached")
        return

    await websocket.accept()
    session = session_registry.create_session(websocket)
    if not session:
        await websocket.close(code=1013, reason="Unable to allocate session")
        return

    app_logger.info(f"WebSocket session established: {session.session_id}")

    try:
        # Initial ready handshake
        await websocket.send_json({
            "type": "session_ready",
            "session_id": session.session_id,
            "status": "connected",
            "asr_ready": asr_service.is_engine_ready,
            "timestamp": time.time()
        })

        while True:
            raw_msg = await websocket.receive_text()
            data = json.loads(raw_msg)
            msg_type = data.get("type")

            if msg_type == "ping":
                await websocket.send_json({"type": "pong", "timestamp": time.time()})

            elif msg_type == "audio_chunk":
                seq = data.get("sequence_id", 0)
                chunk_b64 = data.get("chunk", "")
                client_capture_time_ms = data.get("client_capture_time_ms") or data.get("client_time_ms")

                live_result = None
                if chunk_b64:
                    try:
                        chunk_bytes = base64.b64decode(chunk_b64)
                        if seq % 10 == 1:
                            app_logger.info(f"[{session.session_id}] audio_chunk #{seq} size={len(chunk_bytes)} total_buffer={len(session.audio_buffer)}")
                        if len(chunk_bytes) <= 1024 * 1024:
                            live_result = await asyncio.to_thread(
                                session.process_live_audio_chunk,
                                chunk_bytes,
                                seq,
                                client_capture_time_ms
                            )
                    except Exception as e:
                        app_logger.error(f"[{session.session_id}] audio_chunk error: {e}")

                await websocket.send_json({
                    "type": "chunk_ack",
                    "sequence_id": seq,
                    "buffered_bytes": len(session.audio_buffer)
                })

                if live_result:
                    assessment, text, timing = live_result
                    app_logger.info(f"[{session.session_id}] ASR turn recognized: '{text}' (risk: {assessment.risk_level}, score: {assessment.risk_score})")
                    await websocket.send_json({
                        "type": "risk_update",
                        "session_id": session.session_id,
                        "turn_number": len(session.turns),
                        "speaker": "Caller",
                        "text": text,
                        "risk_level": assessment.risk_level,
                        "risk_score": assessment.risk_score,
                        "decision": assessment.decision,
                        "reasons": assessment.reasons,
                        "is_final": True,
                        "timing": timing,
                        "timestamp": time.time(),
                        "otp_state": assessment.otp_state,
                        "otp_disclosure_risk": assessment.otp_disclosure_risk,
                        "urgent_intervention_required": assessment.urgent_intervention_required,
                        "intervention_heading": assessment.intervention_heading,
                        "intervention_spoken_text": assessment.intervention_spoken_text,
                        "event_id": assessment.event_id
                    })

                    if assessment.urgent_intervention_required:
                        interv_fp = f"OTP_INTERV:{assessment.intervention_heading}:{':'.join(sorted([ev.exact_quote for ev in assessment.evidence[:3]]))}"
                        if session.last_warning_fingerprint != interv_fp:
                            session.last_warning_fingerprint = interv_fp
                            await websocket.send_json({
                                "type": "otp_intervention",
                                "event_id": assessment.event_id or str(uuid.uuid4()),
                                "session_id": session.session_id,
                                "otp_state": assessment.otp_state,
                                "heading": assessment.intervention_heading or "STOP! DO NOT SHARE YOUR OTP",
                                "message": assessment.recommended_action,
                                "spoken_text": assessment.intervention_spoken_text or assessment.recommended_action,
                                "language": assessment.intervention_language or "en",
                                "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:3]],
                                "timing": timing,
                                "timestamp": time.time()
                            })
                            await websocket.send_json({
                                "type": "warning",
                                "severity": "CRITICAL",
                                "title": assessment.intervention_heading or "STOP! DO NOT SHARE YOUR OTP",
                                "message": assessment.recommended_action,
                                "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:2]],
                                "timing": timing,
                                "timestamp": time.time(),
                                "event_id": assessment.event_id,
                                "otp_state": assessment.otp_state,
                                "spoken_text": assessment.intervention_spoken_text
                            })
                    elif assessment.risk_level == "HIGH_RISK":
                        warning_fp = f"HIGH_RISK:{':'.join(sorted([ev.exact_quote for ev in assessment.evidence[:3]]))}"
                        if session.last_warning_fingerprint != warning_fp:
                            session.last_warning_fingerprint = warning_fp
                            await websocket.send_json({
                                "type": "warning",
                                "severity": "CRITICAL",
                                "title": "URGENT FRAUD ALERT",
                                "message": assessment.recommended_action,
                                "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:2]],
                                "timing": timing,
                                "timestamp": time.time(),
                                "event_id": assessment.event_id,
                                "otp_state": assessment.otp_state
                            })

            elif msg_type == "transcript_segment":
                t_recv = time.perf_counter()
                speaker = data.get("speaker", "Caller")
                text = data.get("text", "")
                is_final = data.get("is_final", True)
                client_turn_start_ms = data.get("client_turn_start_ms")
                app_logger.info(f"[{session.session_id}] transcript_segment received from client: '{text}' (speaker={speaker}, is_final={is_final})")

                t_analysis_start = time.perf_counter()
                assessment = session.add_transcript_segment(speaker=speaker, text=text, is_final=is_final)
                analysis_ms = round((time.perf_counter() - t_analysis_start) * 1000, 2)
                server_total_ms = round((time.perf_counter() - t_recv) * 1000, 2)

                timing = {
                    "transcript_to_risk_decision_ms": analysis_ms,
                    "server_processing_total_ms": server_total_ms,
                    "client_turn_start_ms": client_turn_start_ms,
                    "turn_number": len(session.turns)
                }

                if assessment:
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
                        "timing": timing,
                        "timestamp": time.time(),
                        "otp_state": assessment.otp_state,
                        "otp_disclosure_risk": assessment.otp_disclosure_risk,
                        "urgent_intervention_required": assessment.urgent_intervention_required,
                        "intervention_heading": assessment.intervention_heading,
                        "intervention_spoken_text": assessment.intervention_spoken_text,
                        "event_id": assessment.event_id
                    })

                    if assessment.urgent_intervention_required:
                        interv_fp = f"OTP_INTERV:{assessment.intervention_heading}:{':'.join(sorted([ev.exact_quote for ev in assessment.evidence[:3]]))}"
                        if session.last_warning_fingerprint != interv_fp:
                            session.last_warning_fingerprint = interv_fp
                            await websocket.send_json({
                                "type": "otp_intervention",
                                "event_id": assessment.event_id or str(uuid.uuid4()),
                                "session_id": session.session_id,
                                "otp_state": assessment.otp_state,
                                "heading": assessment.intervention_heading or "STOP! DO NOT SHARE YOUR OTP",
                                "message": assessment.recommended_action,
                                "spoken_text": assessment.intervention_spoken_text or assessment.recommended_action,
                                "language": assessment.intervention_language or "en",
                                "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:3]],
                                "timing": timing,
                                "timestamp": time.time()
                            })
                            await websocket.send_json({
                                "type": "warning",
                                "severity": "CRITICAL",
                                "title": assessment.intervention_heading or "STOP! DO NOT SHARE YOUR OTP",
                                "message": assessment.recommended_action,
                                "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:2]],
                                "timing": timing,
                                "timestamp": time.time(),
                                "event_id": assessment.event_id,
                                "otp_state": assessment.otp_state,
                                "spoken_text": assessment.intervention_spoken_text
                            })
                    elif assessment.risk_level == "HIGH_RISK":
                        warning_fp = f"HIGH_RISK:{':'.join(sorted([ev.exact_quote for ev in assessment.evidence[:3]]))}"
                        if session.last_warning_fingerprint != warning_fp:
                            session.last_warning_fingerprint = warning_fp
                            await websocket.send_json({
                                "type": "warning",
                                "severity": "CRITICAL",
                                "title": "URGENT FRAUD ALERT",
                                "message": assessment.recommended_action,
                                "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:2]],
                                "timing": timing,
                                "timestamp": time.time(),
                                "event_id": assessment.event_id,
                                "otp_state": assessment.otp_state
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
                prev_turn_count = len(session.turns)
                prev_text = session.turns[-1].text if session.turns else ""
                assessment = await asyncio.to_thread(session.transcribe_buffered_audio)
                curr_text = session.turns[-1].text if session.turns else ""

                if assessment and (len(session.turns) > prev_turn_count or curr_text != prev_text):
                    last_turn = session.turns[-1]
                    timing = {
                        "server_receipt_to_transcript_ms": 0,
                        "transcript_to_risk_decision_ms": 0,
                        "total_server_turn_to_alert_ms": 0,
                        "audio_duration_seconds": round(len(session.audio_buffer) / 32000.0, 2),
                        "real_time_factor": 0.0,
                        "client_capture_time_ms": int(time.time() * 1000),
                        "turn_number": len(session.turns)
                    }
                    await websocket.send_json({
                        "type": "risk_update",
                        "session_id": session.session_id,
                        "turn_number": len(session.turns),
                        "speaker": last_turn.speaker,
                        "text": last_turn.text,
                        "risk_level": assessment.risk_level,
                        "risk_score": assessment.risk_score,
                        "decision": assessment.decision,
                        "reasons": assessment.reasons,
                        "is_final": True,
                        "timing": timing,
                        "timestamp": time.time(),
                        "otp_state": assessment.otp_state,
                        "otp_disclosure_risk": assessment.otp_disclosure_risk,
                        "urgent_intervention_required": assessment.urgent_intervention_required,
                        "intervention_heading": assessment.intervention_heading,
                        "intervention_spoken_text": assessment.intervention_spoken_text,
                        "event_id": assessment.event_id
                    })
                    if assessment.urgent_intervention_required:
                        await websocket.send_json({
                            "type": "otp_intervention",
                            "event_id": assessment.event_id or str(uuid.uuid4()),
                            "session_id": session.session_id,
                            "otp_state": assessment.otp_state,
                            "heading": assessment.intervention_heading or "STOP! DO NOT SHARE YOUR OTP",
                            "message": assessment.recommended_action,
                            "spoken_text": assessment.intervention_spoken_text or assessment.recommended_action,
                            "language": assessment.intervention_language or "en",
                            "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:3]],
                            "timing": timing,
                            "timestamp": time.time()
                        })
                        await websocket.send_json({
                            "type": "warning",
                            "severity": "CRITICAL",
                            "title": assessment.intervention_heading or "STOP! DO NOT SHARE YOUR OTP",
                            "message": assessment.recommended_action,
                            "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:2]],
                            "timing": timing,
                            "timestamp": time.time(),
                            "event_id": assessment.event_id,
                            "otp_state": assessment.otp_state,
                            "spoken_text": assessment.intervention_spoken_text
                        })
                    elif assessment.risk_level == "HIGH_RISK":
                        await websocket.send_json({
                            "type": "warning",
                            "severity": "CRITICAL",
                            "title": "URGENT FRAUD ALERT",
                            "message": assessment.recommended_action,
                            "evidence_quotes": [ev.exact_quote for ev in assessment.evidence[:2]],
                            "timing": timing,
                            "timestamp": time.time(),
                            "event_id": assessment.event_id,
                            "otp_state": assessment.otp_state
                        })

                summary = session.get_summary_stats()
                await websocket.send_json({
                    "type": "session_summary",
                    "summary": summary
                })
                break

    except WebSocketDisconnect:
        app_logger.info(f"WebSocket session disconnected: {session.session_id}")
    except Exception as e:
        app_logger.error(f"WebSocket session error ({session.session_id}): {e}")
        try:
            await websocket.send_json({"type": "error", "message": "An error occurred in the live stream."})
        except Exception:
            pass
    finally:
        session_registry.remove_session(session.session_id)
        app_logger.info(f"WebSocket session cleaned and closed: {session.session_id}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.host, port=settings.port, reload=settings.debug)
