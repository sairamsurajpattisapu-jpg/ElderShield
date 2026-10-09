export type RiskLevel = 'LOW_RISK' | 'SUSPICIOUS' | 'HIGH_RISK' | 'INSUFFICIENT_EVIDENCE';
export type DecisionType = 'ALLOW' | 'WARN' | 'BLOCK' | 'INCONCLUSIVE';

export type SignalCategory =
  | 'IMPERSONATION'
  | 'URGENCY_INTIMIDATION'
  | 'SECRECY_ISOLATION'
  | 'CREDENTIAL_REQUEST'
  | 'FINANCIAL_TRANSFER'
  | 'REMOTE_ACCESS'
  | 'VERIFICATION_BYPASS'
  | 'LEGITIMATE_SAFEGUARD'
  | 'NEUTRAL_INQUIRY';

export interface ConversationTurn {
  turn_number: number;
  speaker: string;
  text: string;
}

export interface EvidenceItem {
  turn_number: number;
  exact_quote: string;
  signal_category: SignalCategory;
  explanation: string;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  contribution: string;
}

export interface TurnEvaluation {
  turn_number: number;
  speaker: string;
  text: string;
  cumulative_risk_score: number;
  turn_risk_level: RiskLevel;
  newly_detected_signals: string[];
  turn_rationale: string;
  highlighted_spans?: string[];
}

export interface BehavioralSignalsSummary {
  impersonation: boolean;
  urgency_and_threats: boolean;
  requests_for_secrecy: boolean;
  credential_requests: boolean;
  financial_transfer_requests: boolean;
  remote_access_requests: boolean;
  verification_bypass_attempts: boolean;
  legitimate_safeguards_present: boolean;
}

export interface RiskAssessment {
  id: string;
  timestamp: string;
  risk_level: RiskLevel;
  risk_score: number;
  decision: DecisionType;
  evidence: EvidenceItem[];
  reasons: string[];
  recommended_action: string;
  insufficient_evidence: boolean;
  analysis_method: string;
  score_semantics: string;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  language_detected: string;
  signals_summary: BehavioralSignalsSummary;
  turn_progression: TurnEvaluation[];
  unsupported_linguistic_cases?: string[];
  raw_transcript?: string;
  is_demo: boolean;
  demo_scenario_id?: string | null;
}

export interface ProgressionResponse {
  id: string;
  turns: TurnEvaluation[];
  final_risk_level: RiskLevel;
  final_risk_score: number;
  decision: DecisionType;
  reasons: string[];
  analysis_method: string;
}

export interface DemoScenario {
  id: string;
  title: string;
  expected_classification: RiskLevel;
  tag: string;
  target_demographic: string;
  language: string;
  description: string;
  turns: ConversationTurn[];
  raw_transcript: string;
}

export interface UserPreferences {
  fontSize: 'normal' | 'large' | 'xlarge';
  highContrast: boolean;
  soundAlerts: boolean;
  saveHistoryLocally: boolean;
}

export interface AudioMetrics {
  duration_seconds: number;
  transcription_latency_ms: number;
  engine: string;
  segments_count: number;
  detected_language: string;
}

export interface AudioSegment {
  start: number;
  end: number;
  text: string;
}

export interface AudioAnalysisResponse {
  audio_metrics: AudioMetrics;
  transcript: string;
  segments: AudioSegment[];
  risk_assessment: RiskAssessment;
}

export interface LiveRiskUpdate {
  type: 'risk_update';
  session_id: string;
  turn_number: number;
  speaker: string;
  text: string;
  risk_level: RiskLevel;
  risk_score: number;
  decision: DecisionType;
  reasons: string[];
  is_final: boolean;
  timestamp: number;
}

export interface LiveWarning {
  type: 'warning';
  severity: 'CRITICAL' | 'HIGH';
  title: string;
  message: string;
  evidence_quotes: string[];
  timestamp: number;
}

export interface LiveSessionSummary {
  session_id: string;
  duration_seconds: number;
  turns_processed: number;
  final_risk_level: RiskLevel;
  final_risk_score: number;
  decision: DecisionType;
  audio_bytes_buffered: number;
}

