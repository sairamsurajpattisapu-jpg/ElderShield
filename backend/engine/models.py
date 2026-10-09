from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

RiskLevel = Literal["LOW RISK", "SUSPICIOUS", "HIGH RISK", "INSUFFICIENT EVIDENCE"]
BehaviorCategory = Literal[
    "IMPERSONATION",
    "URGENCY_INTIMIDATION",
    "SECRECY_ISOLATION",
    "CREDENTIAL_SOLICITATION",
    "FINANCIAL_COERCION",
    "REMOTE_ACCESS_MALWARE",
    "LEGITIMATE_SAFEGUARD",
    "NEUTRAL_INQUIRY"
]

class ConversationTurn(BaseModel):
    turn_number: int
    speaker: str = Field(..., description="e.g., 'Caller', 'Senior', 'Bank Official'")
    text: str

class EvidenceFinding(BaseModel):
    turn_number: int
    speaker: str
    behavior_category: BehaviorCategory
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    exact_quote: str
    explanation: str
    why_it_matters: str
    recommended_action: str

class TurnProgression(BaseModel):
    turn_number: int
    speaker: str
    text: str
    cumulative_risk_score: float = Field(..., ge=0, le=100)
    turn_risk_level: RiskLevel
    newly_detected_behaviors: List[str]
    turn_rationale: str

class BehaviorMatrix(BaseModel):
    impersonation: bool = False
    urgency_intimidation: bool = False
    secrecy_isolation: bool = False
    credential_solicitation: bool = False
    financial_coercion: bool = False
    remote_access_malware: bool = False
    legitimate_safeguards_present: bool = False

class AnalysisResult(BaseModel):
    id: str
    timestamp: str
    overall_risk_level: RiskLevel
    overall_risk_score: float = Field(..., ge=0, le=100)
    score_semantics: str
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"]
    language_detected: str
    summary: str
    primary_threat_vector: Optional[str] = None
    behavior_matrix: BehaviorMatrix
    turn_progression: List[TurnProgression]
    evidence_findings: List[EvidenceFinding]
    protection_recommendations: List[str]
    raw_transcript: str
    is_demo: bool = False
    demo_scenario_id: Optional[str] = None

class AnalyzeRequest(BaseModel):
    transcript: Optional[str] = None
    turns: Optional[List[ConversationTurn]] = None
    language_hint: Optional[str] = "auto"
    demo_scenario_id: Optional[str] = None

class ScenarioMetadata(BaseModel):
    id: str
    title: str
    expected_classification: RiskLevel
    tag: str
    target_demographic: str
    language: str
    description: str
    turns: List[ConversationTurn]
