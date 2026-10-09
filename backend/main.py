import os
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional

from engine.models import (
    AnalysisResult,
    AnalyzeRequest,
    ScenarioMetadata,
    ConversationTurn
)
from engine.analyzer import engine, parse_raw_transcript
from engine.scenarios import DEMO_SCENARIOS, SCENARIO_LOOKUP

app = FastAPI(
    title="ElderShield API",
    description="Real-Time Conversational Scam Detection Engine for Elderly Users — Hack With Vizag 4.0",
    version="1.0.0"
)

# CORS configuration to allow local frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory recent analysis store
RECENT_ANALYSES: List[AnalysisResult] = []

@app.on_event("startup")
def preseed_analyses():
    """Pre-seed recent analyses with initial demonstrations."""
    for sc in DEMO_SCENARIOS:
        res = engine.analyze(
            turns=sc.turns,
            raw_transcript="\n".join([f"{t.speaker}: {t.text}" for t in sc.turns]),
            is_demo=True,
            demo_id=sc.id
        )
        RECENT_ANALYSES.append(res)

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "service": "ElderShield Scam Detection Core",
        "engine_version": "1.0.0-hwv4",
        "supported_languages": ["English", "Hindi (हिन्दी)", "Telugu (తెలుగు)", "Hinglish", "Teluglish"],
        "active_monitors": len(RECENT_ANALYSES)
    }

@app.get("/api/scenarios", response_model=List[ScenarioMetadata])
def get_demo_scenarios():
    """Retrieve verified benchmark demo scenarios."""
    return DEMO_SCENARIOS

@app.get("/api/scenarios/{scenario_id}", response_model=ScenarioMetadata)
def get_single_scenario(scenario_id: str):
    if scenario_id not in SCENARIO_LOOKUP:
        raise HTTPException(status_code=404, detail="Scenario not found")
    return SCENARIO_LOOKUP[scenario_id]

@app.post("/api/analyze", response_model=AnalysisResult)
def analyze_conversation(request: AnalyzeRequest):
    """
    Analyzes a conversation transcript or structured turns.
    Evaluates progressive risk turn-by-turn and flags evidence findings.
    """
    is_demo = False
    scenario_id = request.demo_scenario_id
    
    if scenario_id and scenario_id in SCENARIO_LOOKUP:
        sc = SCENARIO_LOOKUP[scenario_id]
        turns = sc.turns
        raw_text = "\n".join([f"{t.speaker}: {t.text}" for t in turns])
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

    result = engine.analyze(
        turns=turns,
        raw_transcript=raw_text,
        is_demo=is_demo,
        demo_id=scenario_id
    )

    # Insert at beginning of recent analyses
    RECENT_ANALYSES.insert(0, result)
    if len(RECENT_ANALYSES) > 50:
        RECENT_ANALYSES.pop()

    return result

@app.get("/api/recent", response_model=List[AnalysisResult])
def get_recent_analyses(limit: int = 10):
    """Retrieve recent conversation analyses."""
    return RECENT_ANALYSES[:limit]

@app.get("/api/analyses/{analysis_id}", response_model=AnalysisResult)
def get_analysis_by_id(analysis_id: str):
    for item in RECENT_ANALYSES:
        if item.id == analysis_id:
            return item
    raise HTTPException(status_code=404, detail="Analysis result not found")

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
