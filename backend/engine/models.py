from typing import List, Optional, Dict, Literal
from pydantic import BaseModel, Field

RiskLevel = Literal["LOW_RISK", "SUSPICIOUS", "HIGH_RISK", "INSUFFICIENT_EVIDENCE"]
DecisionType = Literal["ALLOW", "WARN", "BLOCK", "INCONCLUSIVE"]

SignalCategory = Literal[
    "IMPERSONATION",
    "URGENCY_INTIMIDATION",
    "SECRECY_ISOLATION",
    "CREDENTIAL_REQUEST",
    "FINANCIAL_TRANSFER",
    "REMOTE_ACCESS",
    "VERIFICATION_BYPASS",
    "LEGITIMATE_SAFEGUARD",
    "NEUTRAL_INQUIRY"
]

class ConversationTurn(BaseModel):
    turn_number: int
    speaker: str = Field(..., description="e.g. 'Caller', 'Senior', 'Bank Official'")
    text: str

class EvidenceItem(BaseModel):
    turn_number: int
    exact_quote: str
    signal_category: SignalCategory
    explanation: str
    severity: Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]
    contribution: str = Field(..., description="Contribution or impact to risk assessment score")

class TurnEvaluation(BaseModel):
    turn_number: int
    speaker: str
    text: str
    cumulative_risk_score: float = Field(..., ge=0, le=100)
    turn_risk_level: RiskLevel
    newly_detected_signals: List[str]
    turn_rationale: str
    highlighted_spans: List[str] = Field(default_factory=list)

class BehavioralSignalsSummary(BaseModel):
    impersonation: bool = False
    urgency_and_threats: bool = False
    requests_for_secrecy: bool = False
    credential_requests: bool = False
    financial_transfer_requests: bool = False
    remote_access_requests: bool = False
    verification_bypass_attempts: bool = False
    legitimate_safeguards_present: bool = False

class RiskAssessment(BaseModel):
    risk_level: RiskLevel
    risk_score: float = Field(..., ge=0, le=100, description="Rule-based calibrated score index from 0 to 100")
    decision: DecisionType
    evidence: List[EvidenceItem]
    reasons: List[str]
    recommended_action: str
    insufficient_evidence: bool
    analysis_method: str = "rule-based-behavioral-v1"

    # Additional contextual fields for complete UX & compliance
    score_semantics: str
    confidence_level: Literal["HIGH", "MEDIUM", "LOW"]
    language_detected: str
    signals_summary: BehavioralSignalsSummary
    turn_progression: List[TurnEvaluation]
    unsupported_linguistic_cases: List[str] = Field(default_factory=list)
    id: str
    timestamp: str
    raw_transcript: Optional[str] = None
    is_demo: bool = False
    demo_scenario_id: Optional[str] = None

class AnalyzeRequest(BaseModel):
    transcript: Optional[str] = None
    turns: Optional[List[ConversationTurn]] = None
    demo_scenario_id: Optional[str] = None
    language_hint: Optional[str] = "auto"

class ProgressionResponse(BaseModel):
    id: str
    turns: List[TurnEvaluation]
    final_risk_level: RiskLevel
    final_risk_score: float
    decision: DecisionType
    reasons: List[str]
    analysis_method: str = "rule-based-behavioral-v1"

class DemoScenario(BaseModel):
    id: str
    title: str
    expected_classification: RiskLevel
    tag: str
    target_demographic: str
    language: str
    description: str
    turns: List[ConversationTurn]
    raw_transcript: str

class CallerLookupRequest(BaseModel):
    phone_number: str
    claimed_organization: Optional[str] = None
    country_hint: Optional[str] = "IN"

class CallerIntelligenceResult(BaseModel):
    raw_input: str
    is_valid: bool
    e164_format: Optional[str] = None
    national_format: Optional[str] = None
    country_code: Optional[str] = None
    carrier: Optional[str] = None
    geographic_region: Optional[str] = None
    metadata_disclaimer: str = Field(
        default="Carrier and circle metadata reflect ITU number plan allocation, not verified physical GPS location or live roaming carrier.",
        description="Explicit limitation regarding Mobile Number Portability and VoIP masking"
    )
    number_type: Literal["MOBILE", "FIXED_LINE", "TOLL_FREE", "VOIP", "PREMIUM_RATE", "SPECIAL", "UNKNOWN"]
    claimed_organization: Optional[str] = None
    verified_caller_identity: Optional[str] = None
    is_registered_institution: bool = False
    registered_organization: Optional[str] = None
    official_helplines: List[str] = Field(default_factory=list)
    official_url: Optional[str] = None
    identity_conflict_status: Literal["VERIFIED_MATCH", "POTENTIAL_IDENTITY_CONFLICT", "NO_CONFLICT_UNVERIFIED", "UNKNOWN"] = "UNKNOWN"
    spoofing_suspected: bool = False
    spoofing_conflict_details: Optional[str] = None
    reputation_score: float = Field(default=50.0, ge=0, le=100)
    verdict: Literal["VERIFIED_INSTITUTION", "NORMAL_PERSONAL", "POTENTIAL_IDENTITY_CONFLICT", "SPOOF_CONFLICT", "HIGH_RISK_SUSPECT", "INVALID_FORMAT"]
    advisory: str
    evidence_source: str = "ITU E.164 + Google phonenumbers + National Official Institutional Registry v2.2"
    lookup_timestamp: Optional[str] = None


