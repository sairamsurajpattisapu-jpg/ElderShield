export type RiskLevel = 'LOW RISK' | 'SUSPICIOUS' | 'HIGH RISK' | 'INSUFFICIENT EVIDENCE';

export type BehaviorCategory =
  | 'IMPERSONATION'
  | 'URGENCY_INTIMIDATION'
  | 'SECRECY_ISOLATION'
  | 'CREDENTIAL_SOLICITATION'
  | 'FINANCIAL_COERCION'
  | 'REMOTE_ACCESS_MALWARE'
  | 'LEGITIMATE_SAFEGUARD'
  | 'NEUTRAL_INQUIRY';

export interface ConversationTurn {
  turn_number: number;
  speaker: string;
  text: string;
}

export interface EvidenceFinding {
  turn_number: number;
  speaker: string;
  behavior_category: BehaviorCategory;
  severity: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  exact_quote: string;
  explanation: string;
  why_it_matters: string;
  recommended_action: string;
}

export interface TurnProgression {
  turn_number: number;
  speaker: string;
  text: string;
  cumulative_risk_score: number;
  turn_risk_level: RiskLevel;
  newly_detected_behaviors: string[];
  turn_rationale: string;
}

export interface BehaviorMatrix {
  impersonation: boolean;
  urgency_intimidation: boolean;
  secrecy_isolation: boolean;
  credential_solicitation: boolean;
  financial_coercion: boolean;
  remote_access_malware: boolean;
  legitimate_safeguards_present: boolean;
}

export interface AnalysisResult {
  id: string;
  timestamp: string;
  overall_risk_level: RiskLevel;
  overall_risk_score: number;
  score_semantics: string;
  confidence_level: 'HIGH' | 'MEDIUM' | 'LOW';
  language_detected: string;
  summary: string;
  primary_threat_vector?: string | null;
  behavior_matrix: BehaviorMatrix;
  turn_progression: TurnProgression[];
  evidence_findings: EvidenceFinding[];
  protection_recommendations: string[];
  raw_transcript: string;
  is_demo: boolean;
  demo_scenario_id?: string | null;
}

export interface ScenarioMetadata {
  id: string;
  title: string;
  expected_classification: RiskLevel;
  tag: string;
  target_demographic: string;
  language: string;
  description: string;
  turns: ConversationTurn[];
}
