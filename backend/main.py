import os
from typing import List, Optional
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware

from engine.models import (
    RiskAssessment,
    AnalyzeRequest,
    ProgressionResponse,
    DemoScenario,
    ConversationTurn
)
from engine.analyzer import engine, parse_raw_transcript
from engine.scenarios import DEMO_SCENARIOS, SCENARIO_LOOKUP

# Initialize FastAPI application
app = FastAPI(
    title="ElderShield Scam Detection API",
    description="Conversational scam detection engine protecting elderly users against social engineering fraud.",
    version="2.0.0"
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
        "engine_version": "2.0.0",
        "supported_languages": ["English", "Hindi (हिन्दी)", "Telugu (తెలుగు)", "Hinglish", "Teluglish"],
        "endpoints": [
            "GET /health",
            "POST /api/analyze",
            "POST /api/analyze/progression",
            "GET /api/demo-scenarios"
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

@app.get("/api/recent", response_model=List[RiskAssessment])
def get_recent_analyses(limit: int = 15):
    """Retrieve recent conversation analyses for the current session."""
    return RECENT_ANALYSES[:limit]

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
