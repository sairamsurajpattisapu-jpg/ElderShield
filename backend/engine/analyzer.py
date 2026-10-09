import re
import uuid
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional, Set

from .models import (
    RiskLevel,
    DecisionType,
    SignalCategory,
    ConversationTurn,
    EvidenceItem,
    TurnEvaluation,
    BehavioralSignalsSummary,
    RiskAssessment
)
from .multilingual import (
    detect_language,
    PATTERNS_IMPERSONATION,
    PATTERNS_URGENCY_INTIMIDATION,
    PATTERNS_SECRECY_ISOLATION,
    PATTERNS_CREDENTIAL_REQUEST,
    PATTERNS_FINANCIAL_TRANSFER,
    PATTERNS_REMOTE_ACCESS,
    PATTERNS_VERIFICATION_BYPASS,
    PATTERNS_LEGITIMATE_SAFEGUARDS,
    UNSUPPORTED_LINGUISTIC_CASES
)

def parse_raw_transcript(transcript: str) -> List[ConversationTurn]:
    """Parses raw text transcripts into structured turns with speaker identification."""
    lines = [line.strip() for line in transcript.strip().splitlines() if line.strip()]
    turns: List[ConversationTurn] = []
    
    turn_counter = 1
    speaker_regex = re.compile(
        r"^(Caller|Senior|Bank\s+Official|Official|Victim|Agent|Customer|Person\s+[A-Z0-9]+|User|Manager|Police|Operator|Unknown)[\s*:\-\]]+(.*)$",
        re.IGNORECASE
    )
    
    for line in lines:
        match = speaker_regex.match(line)
        if match:
            spk = match.group(1).capitalize()
            txt = match.group(2).strip()
            turns.append(ConversationTurn(turn_number=turn_counter, speaker=spk, text=txt))
            turn_counter += 1
        elif ":" in line and len(line.split(":", 1)[0].split()) <= 3:
            parts = line.split(":", 1)
            spk = parts[0].strip()
            txt = parts[1].strip()
            turns.append(ConversationTurn(turn_number=turn_counter, speaker=spk, text=txt))
            turn_counter += 1
        else:
            spk = "Caller" if turn_counter % 2 != 0 else "Senior"
            turns.append(ConversationTurn(turn_number=turn_counter, speaker=spk, text=line))
            turn_counter += 1
                
    return turns

class ConversationRiskEngine:
    """
    Modular, deterministic rule-based scam detection engine.
    Evaluates multi-vector behavioral combinations across English, Hindi, and Telugu.
    """
    ANALYSIS_METHOD = "rule-based-behavioral-v1"

    def __init__(self):
        pass

    def _is_senior_speaker(self, speaker: str) -> bool:
        spk = speaker.lower()
        return any(term in spk for term in ["senior", "victim", "customer", "user", "elder"])

    def _extract_turn_signals(
        self,
        turn: ConversationTurn,
        seen_quotes: Set[str]
    ) -> Tuple[Dict[str, List[str]], List[EvidenceItem]]:
        """
        Extracts behavioral signals from a single turn, preventing duplicate evidence.
        """
        evidence_items: List[EvidenceItem] = []
        signals_detected: Dict[str, List[str]] = {
            "impersonation": [],
            "urgency": [],
            "secrecy": [],
            "credentials": [],
            "transfer": [],
            "remote_access": [],
            "verification_bypass": [],
            "legitimate_safeguard": []
        }
        
        text = turn.text
        is_senior = self._is_senior_speaker(turn.speaker)

        # 1. Legitimate Safeguard Check (invitation to branch or warning against sharing OTPs)
        for pat in PATTERNS_LEGITIMATE_SAFEGUARDS:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                quote = m.group(0)
                norm_quote = quote.lower().strip()
                if norm_quote not in seen_quotes:
                    seen_quotes.add(norm_quote)
                    signals_detected["legitimate_safeguard"].append(quote)
                    evidence_items.append(EvidenceItem(
                        turn_number=turn.turn_number,
                        exact_quote=quote,
                        signal_category="LEGITIMATE_SAFEGUARD",
                        explanation="Explicit institutional safeguard: caller urges physical branch visit or warns customer NEVER to disclose OTPs.",
                        severity="LOW",
                        contribution="-40.0 (Suppresses suspicion and validates institutional safety protocol)"
                    ))
                break

        # Threat actions are attributes of the Caller / external contact, not the senior victim
        if not is_senior:
            # 2. Impersonation
            for subcat, patterns in PATTERNS_IMPERSONATION.items():
                matched = False
                for pat in patterns:
                    m = re.search(pat, text, re.IGNORECASE)
                    if m:
                        quote = m.group(0)
                        norm_quote = quote.lower().strip()
                        if norm_quote not in seen_quotes:
                            seen_quotes.add(norm_quote)
                            signals_detected["impersonation"].append(subcat)
                            evidence_items.append(EvidenceItem(
                                turn_number=turn.turn_number,
                                exact_quote=quote,
                                signal_category="IMPERSONATION",
                                explanation=f"Caller asserts authority or institution identity ({subcat.replace('_', ' ').title()}). Impersonation creates false trust or fear.",
                                severity="MEDIUM" if subcat == "UTILITY_TELECOM" else "HIGH",
                                contribution="+25.0 (Initial baseline hook)"
                            ))
                        matched = True
                        break
                if matched:
                    break

            # 3. Urgency & Intimidation
            for pat in PATTERNS_URGENCY_INTIMIDATION:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    norm_quote = quote.lower().strip()
                    if norm_quote not in seen_quotes:
                        seen_quotes.add(norm_quote)
                        signals_detected["urgency"].append(quote)
                        evidence_items.append(EvidenceItem(
                            turn_number=turn.turn_number,
                            exact_quote=quote,
                            signal_category="URGENCY_INTIMIDATION",
                            explanation="Artificial deadline or threat of punitive action (power cutoff, account freeze, or arrest warrant).",
                            severity="HIGH",
                            contribution="+25.0 (Creates cognitive tunnel vision)"
                        ))
                    break

            # 4. Secrecy & Isolation
            for pat in PATTERNS_SECRECY_ISOLATION:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    norm_quote = quote.lower().strip()
                    if norm_quote not in seen_quotes:
                        seen_quotes.add(norm_quote)
                        signals_detected["secrecy"].append(quote)
                        evidence_items.append(EvidenceItem(
                            turn_number=turn.turn_number,
                            exact_quote=quote,
                            signal_category="SECRECY_ISOLATION",
                            explanation="Active demand to keep conversation secret or isolate senior from family/advisors.",
                            severity="CRITICAL",
                            contribution="+30.0 (High-risk isolation tactic)"
                        ))
                    break

            # 5. Credential Requests (only if not a legitimate safeguard)
            if not signals_detected["legitimate_safeguard"]:
                for pat in PATTERNS_CREDENTIAL_REQUEST:
                    m = re.search(pat, text, re.IGNORECASE)
                    if m:
                        quote = m.group(0)
                        norm_quote = quote.lower().strip()
                        if norm_quote not in seen_quotes:
                            seen_quotes.add(norm_quote)
                            signals_detected["credentials"].append(quote)
                            evidence_items.append(EvidenceItem(
                                turn_number=turn.turn_number,
                                exact_quote=quote,
                                signal_category="CREDENTIAL_REQUEST",
                                explanation="Direct solicitation of OTP, UPI PIN, ATM PIN, or banking password over the call.",
                                severity="CRITICAL",
                                contribution="+40.0 (Direct credential harvesting)"
                            ))
                        break

            # 6. Financial Transfers
            for pat in PATTERNS_FINANCIAL_TRANSFER:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    norm_quote = quote.lower().strip()
                    if norm_quote not in seen_quotes:
                        seen_quotes.add(norm_quote)
                        signals_detected["transfer"].append(quote)
                        evidence_items.append(EvidenceItem(
                            turn_number=turn.turn_number,
                            exact_quote=quote,
                            signal_category="FINANCIAL_TRANSFER",
                            explanation="Demand to make immediate payments via UPI/QR or transfer savings to alleged 'RBI safety account'.",
                            severity="CRITICAL",
                            contribution="+40.0 (Direct financial extraction)"
                        ))
                    break

            # 7. Remote Access Software
            for pat in PATTERNS_REMOTE_ACCESS:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    norm_quote = quote.lower().strip()
                    if norm_quote not in seen_quotes:
                        seen_quotes.add(norm_quote)
                        signals_detected["remote_access"].append(quote)
                        evidence_items.append(EvidenceItem(
                            turn_number=turn.turn_number,
                            exact_quote=quote,
                            signal_category="REMOTE_ACCESS",
                            explanation="Request to download screen-sharing tools (QuickSupport, AnyDesk) or install APK files.",
                            severity="CRITICAL",
                            contribution="+35.0 (Remote device takeover)"
                        ))
                    break

            # 8. Verification Bypass
            for pat in PATTERNS_VERIFICATION_BYPASS:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    norm_quote = quote.lower().strip()
                    if norm_quote not in seen_quotes:
                        seen_quotes.add(norm_quote)
                        signals_detected["verification_bypass"].append(quote)
                        evidence_items.append(EvidenceItem(
                            turn_number=turn.turn_number,
                            exact_quote=quote,
                            signal_category="VERIFICATION_BYPASS",
                            explanation="Attempt to discourage visiting bank branch or consulting official customer care.",
                            severity="HIGH",
                            contribution="+20.0 (Bypasses authentic validation)"
                        ))
                    break

        return signals_detected, evidence_items

    def analyze(
        self,
        turns: List[ConversationTurn],
        raw_transcript: str = "",
        is_demo: bool = False,
        demo_id: Optional[str] = None
    ) -> RiskAssessment:
        """
        Executes progressive risk assessment across all conversation turns.
        """
        if not turns:
            turns = parse_raw_transcript(raw_transcript)

        full_text = " ".join([t.text for t in turns])
        lang_detected = detect_language(full_text)

        all_evidence: List[EvidenceItem] = []
        turn_evaluations: List[TurnEvaluation] = []
        seen_quotes: Set[str] = set()

        # Cumulative state across turns
        active_impersonation = False
        active_urgency = False
        active_secrecy = False
        active_credentials = False
        active_transfer = False
        active_remote_access = False
        active_bypass = False
        active_safeguard = False

        current_score = 0.0

        for turn in turns:
            signals, turn_evidence = self._extract_turn_signals(turn, seen_quotes)
            all_evidence.extend(turn_evidence)

            new_signals_this_turn = []
            highlight_spans = []

            if signals["impersonation"] and not active_impersonation:
                new_signals_this_turn.append("Impersonation Claim")
                active_impersonation = True

            if signals["urgency"] and not active_urgency:
                new_signals_this_turn.append("Urgency & Intimidation")
                active_urgency = True

            if signals["secrecy"] and not active_secrecy:
                new_signals_this_turn.append("Secrecy / Isolation Mandate")
                active_secrecy = True

            if signals["credentials"] and not active_credentials:
                new_signals_this_turn.append("Credential Solicitation (OTP/PIN)")
                active_credentials = True

            if signals["transfer"] and not active_transfer:
                new_signals_this_turn.append("Coercive Financial Transfer Request")
                active_transfer = True

            if signals["remote_access"] and not active_remote_access:
                new_signals_this_turn.append("Remote Access Software / APK Request")
                active_remote_access = True

            if signals["verification_bypass"] and not active_bypass:
                new_signals_this_turn.append("Verification Bypass Attempt")
                active_bypass = True

            if signals["legitimate_safeguard"]:
                active_safeguard = True
                new_signals_this_turn.append("Official Safeguard (In-Person Branch Invitation)")

            for ev in turn_evidence:
                highlight_spans.append(ev.exact_quote)

            # Progressive score calculation
            if active_safeguard and not (active_credentials or active_transfer or active_remote_access):
                # Safeguards hold risk low
                current_score = min(12.0, max(current_score * 0.4, 5.0))
            else:
                base = 0.0
                if active_impersonation:
                    base += 28.0
                if active_urgency:
                    base += 24.0
                if active_secrecy:
                    base += 26.0
                if active_bypass:
                    base += 20.0
                if active_remote_access:
                    base += 32.0
                if active_credentials:
                    base += 38.0
                if active_transfer:
                    base += 38.0

                # Compounding multi-vector amplification:
                # If Impersonation + Urgency/Secrecy + Credential/Transfer/Remote Access
                if active_impersonation and (active_urgency or active_secrecy) and (active_credentials or active_transfer or active_remote_access):
                    base = max(base, 94.0)
                elif active_impersonation and (active_credentials or active_remote_access or active_transfer):
                    base = max(base, 85.0)
                elif (active_urgency or active_secrecy) and (active_credentials or active_transfer or active_remote_access):
                    base = max(base, 88.0)

                current_score = min(98.5, max(current_score, base))

            # Turn-level risk classification
            turn_risk: RiskLevel
            total_active_threat_signals = (
                int(active_impersonation) +
                int(active_urgency) +
                int(active_secrecy) +
                int(active_credentials) +
                int(active_transfer) +
                int(active_remote_access) +
                int(active_bypass)
            )

            if total_active_threat_signals == 0 and not active_safeguard:
                turn_risk = "INSUFFICIENT_EVIDENCE"
            elif active_safeguard and not (active_credentials or active_transfer or active_remote_access):
                turn_risk = "LOW_RISK"
            elif current_score >= 61.0:
                turn_risk = "HIGH_RISK"
            elif current_score >= 26.0:
                turn_risk = "SUSPICIOUS"
            else:
                turn_risk = "LOW_RISK"

            if new_signals_this_turn:
                turn_rationale = f"Detected: {', '.join(new_signals_this_turn)}."
            elif active_safeguard:
                turn_rationale = "Legitimate institution safeguard maintains low risk."
            elif current_score > 60:
                turn_rationale = "High scam momentum continues from previous coercive tactics."
            elif turn_risk == "INSUFFICIENT_EVIDENCE":
                turn_rationale = "Ambiguous dialogue with no distinguishable scam or safety markers."
            else:
                turn_rationale = "Dialogue continues without new threat markers."

            turn_evaluations.append(TurnEvaluation(
                turn_number=turn.turn_number,
                speaker=turn.speaker,
                text=turn.text,
                cumulative_risk_score=round(current_score, 1),
                turn_risk_level=turn_risk,
                newly_detected_signals=new_signals_this_turn,
                turn_rationale=turn_rationale,
                highlighted_spans=highlight_spans
            ))

        signals_summary = BehavioralSignalsSummary(
            impersonation=active_impersonation,
            urgency_and_threats=active_urgency,
            requests_for_secrecy=active_secrecy,
            credential_requests=active_credentials,
            financial_transfer_requests=active_transfer,
            remote_access_requests=active_remote_access,
            verification_bypass_attempts=active_bypass,
            legitimate_safeguards_present=active_safeguard
        )

        total_threat_signals = (
            int(active_impersonation) +
            int(active_urgency) +
            int(active_secrecy) +
            int(active_credentials) +
            int(active_transfer) +
            int(active_remote_access) +
            int(active_bypass)
        )

        final_risk_level: RiskLevel
        final_risk_score: float = current_score
        final_decision: DecisionType
        insufficient_ev: bool = False
        confidence: str = "HIGH"
        score_semantics: str
        reasons: List[str] = []

        # 1. Conservative rules for ambiguous / insufficient conversations
        if total_threat_signals == 0 and not active_safeguard:
            final_risk_level = "INSUFFICIENT_EVIDENCE"
            final_risk_score = 15.0
            final_decision = "INCONCLUSIVE"
            insufficient_ev = True
            confidence = "LOW"
            score_semantics = (
                "Score 15/100 (Indeterminate Baseline). The conversation lacks actionable indicators "
                "of either fraudulent coercion or verified institutional safeguards. "
                "This score represents uncertainty under insufficient evidence, not a probability."
            )
            reasons.append("The dialogue is too brief or generic to establish fraudulent intent.")
            reasons.append("No institutional authority claims, urgency markers, or credential requests were identified.")
            reasons.append("Remains indeterminate until additional conversational turns are observed.")

        # 2. Legitimate conversation (contains sensitive keywords like OTP/KYC, but safeguards present)
        elif active_safeguard and not (active_credentials or active_transfer or active_remote_access):
            final_risk_level = "LOW_RISK"
            final_risk_score = 10.0
            final_decision = "ALLOW"
            confidence = "HIGH"
            score_semantics = (
                "Score 10/100 (Legitimate Safeguard Verified). The interaction adheres to official banking "
                "security standards. While sensitive keywords (e.g., OTP, bank, account) were mentioned, "
                "the speaker explicitly warned against sharing credentials and scheduled an in-person branch verification."
            )
            reasons.append("Official security advice detected: customer was instructed never to disclose OTPs.")
            reasons.append("Invitation to visit local bank branch physically removes coercion.")
            reasons.append("No pressure, secrecy, or remote application installation requested.")

        # 3. High Risk Scams (multi-vector combination)
        elif (active_credentials or active_remote_access or active_transfer) and (active_impersonation or active_urgency or active_secrecy):
            final_risk_level = "HIGH_RISK"
            final_risk_score = max(current_score, 92.0)
            final_decision = "BLOCK"
            confidence = "HIGH"
            score_semantics = (
                f"Score {final_risk_score:.0f}/100 (Critical Scam Threat). Compounded fraudulent vectors detected: "
                "Authority Impersonation + Psychological Pressure/Secrecy + Credential/Asset Extraction. "
                "Score reflects maximum rule severity based on predatory social engineering patterns."
            )
            reasons.append("Caller claimed official authority (Bank, Law Enforcement, or Utility Board).")
            if active_urgency:
                reasons.append("Manufactured urgency or punitive threats (arrest, account freeze, power disconnection).")
            if active_secrecy:
                reasons.append("Demanded secrecy or forbade consulting family members.")
            if active_credentials:
                reasons.append("Directly solicited confidential OTPs or PINs over the phone.")
            if active_remote_access:
                reasons.append("Instructed victim to download remote screen-sharing tools (AnyDesk/QuickSupport).")
            if active_transfer:
                reasons.append("Demanded money transfer or payment under pressure to a purported 'safety account'.")

        elif total_threat_signals >= 2 or active_credentials or active_transfer or active_remote_access:
            final_risk_level = "HIGH_RISK"
            final_risk_score = max(current_score, 75.0)
            final_decision = "BLOCK"
            confidence = "HIGH"
            score_semantics = (
                f"Score {final_risk_score:.0f}/100 (High Risk Violation). Direct violation of banking/legal protocols "
                "involving credential or remote tool demands."
            )
            reasons.append("Severe behavioral violations detected that match recognized cyber scam vectors.")

        # 4. Suspicious
        elif total_threat_signals == 1:
            final_risk_level = "SUSPICIOUS"
            final_risk_score = 42.0
            final_decision = "WARN"
            confidence = "MEDIUM"
            score_semantics = (
                "Score 42/100 (Elevated Precaution). An isolated suspicious signal was detected "
                "(such as an unsolicited authority claim or artificial urgency) without active credential theft yet."
            )
            reasons.append("Unverified authority claim or artificial urgency detected.")
            reasons.append("Direct credential or monetary theft has not yet occurred, but high caution is required.")

        else:
            final_risk_level = "LOW_RISK"
            final_risk_score = 8.0
            final_decision = "ALLOW"
            confidence = "HIGH"
            score_semantics = "Score 8/100 (Neutral Conversation). Standard interaction with no threat signals."
            reasons.append("Standard conversational flow with no malicious indicators.")

        # Recommended Action for elderly user
        recommended_action = self._determine_recommended_action(final_risk_level, signals_summary)

        analysis_id = str(uuid.uuid4())[:8]

        return RiskAssessment(
            id=analysis_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            risk_level=final_risk_level,
            risk_score=final_risk_score,
            decision=final_decision,
            evidence=all_evidence,
            reasons=reasons,
            recommended_action=recommended_action,
            insufficient_evidence=insufficient_ev,
            analysis_method=self.ANALYSIS_METHOD,
            score_semantics=score_semantics,
            confidence_level=confidence,
            language_detected=lang_detected,
            signals_summary=signals_summary,
            turn_progression=turn_evaluations,
            unsupported_linguistic_cases=UNSUPPORTED_LINGUISTIC_CASES,
            raw_transcript=raw_transcript or "\n".join([f"{t.speaker}: {t.text}" for t in turns]),
            is_demo=is_demo,
            demo_scenario_id=demo_id
        )

    def _determine_recommended_action(self, risk: RiskLevel, summary: BehavioralSignalsSummary) -> str:
        """Determines concise, practical senior protection directive."""
        if risk == "HIGH_RISK":
            actions = ["Disconnect the phone call immediately. Do not stay on the line."]
            if summary.credential_requests:
                actions.append("Never share your 6-digit OTP, ATM PIN, or UPI PIN with anyone.")
            if summary.remote_access_requests:
                actions.append("Do not install AnyDesk or QuickSupport apps requested over the phone.")
            if summary.financial_transfer_requests:
                actions.append("Never transfer money to alleged 'safety accounts' or scan QR codes.")
            actions.append("Call National Cybercrime Helpline 1930 immediately if money was transferred.")
            actions.append("Inform a family member or trusted neighbor right away.")
            return " ".join(actions)
        elif risk == "SUSPICIOUS":
            return (
                "Pause before taking any action. Do not rush into making payments or decisions due to deadlines. "
                "Hang up, look up the official phone number printed on your utility bill or bank card, and verify independently. "
                "Consult a trusted family member before proceeding."
            )
        elif risk == "INSUFFICIENT_EVIDENCE":
            return (
                "Remain vigilant. This conversation is too brief or ambiguous to determine intent. "
                "Do not volunteer personal banking details, Aadhaar numbers, or passwords. "
                "Ask the caller to send an official written notice if they represent an institution."
            )
        else: # LOW_RISK
            return (
                "Safe communication protocol verified. For any account or KYC updates, always visit your local "
                "bank branch in person at your convenience. Continue the safe practice of never disclosing OTPs."
            )

engine = ConversationRiskEngine()
