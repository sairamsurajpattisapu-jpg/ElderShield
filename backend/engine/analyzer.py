import re
import uuid
from datetime import datetime
from typing import List, Tuple, Dict, Any, Optional

from .models import (
    RiskLevel,
    BehaviorCategory,
    ConversationTurn,
    EvidenceFinding,
    TurnProgression,
    BehaviorMatrix,
    AnalysisResult
)
from .multilingual import (
    detect_language,
    PATTERNS_IMPERSONATION,
    PATTERNS_URGENCY_INTIMIDATION,
    PATTERNS_SECRECY_ISOLATION,
    PATTERNS_CREDENTIAL_SOLICITATION,
    PATTERNS_FINANCIAL_COERCION,
    PATTERNS_REMOTE_ACCESS_MALWARE,
    PATTERNS_LEGITIMATE_SAFEGUARDS
)

def parse_raw_transcript(transcript: str) -> List[ConversationTurn]:
    """Parses a raw text transcript into structured turns."""
    lines = [line.strip() for line in transcript.strip().splitlines() if line.strip()]
    turns: List[ConversationTurn] = []
    
    turn_counter = 1
    speaker_regex = re.compile(r"^(Caller|Senior|Bank\s+Official|Official|Victim|Agent|Customer|Person\s+[A-Z0-9]+|User|Manager|Police|Operator|Unknown)[\s*:\-\]]+(.*)$", re.IGNORECASE)
    
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

class ScamDetectionEngine:
    def __init__(self):
        pass

    def _is_senior_speaker(self, speaker: str) -> bool:
        spk = speaker.lower()
        return "senior" in spk or "victim" in spk or "customer" in spk or "user" in spk

    def _extract_turn_markers(self, turn: ConversationTurn) -> Tuple[Dict[str, List[str]], List[EvidenceFinding]]:
        """Analyzes a single turn and extracts behavioral markers and evidence findings."""
        findings: List[EvidenceFinding] = []
        behaviors_detected: Dict[str, List[str]] = {
            "impersonation": [],
            "urgency": [],
            "secrecy": [],
            "credentials": [],
            "coercion": [],
            "remote_access": [],
            "legitimate_safeguard": []
        }
        
        text = turn.text
        is_senior = self._is_senior_speaker(turn.speaker)

        # First check legitimate safeguards (can come from caller or senior)
        for pat in PATTERNS_LEGITIMATE_SAFEGUARDS:
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                quote = m.group(0)
                behaviors_detected["legitimate_safeguard"].append(quote)
                findings.append(EvidenceFinding(
                    turn_number=turn.turn_number,
                    speaker=turn.speaker,
                    behavior_category="LEGITIMATE_SAFEGUARD",
                    severity="LOW",
                    exact_quote=quote,
                    explanation="Explicit institutional safeguard detected (advising physical branch visit or explicitly warning NEVER to disclose OTPs/PINs).",
                    why_it_matters="Legitimate banking and government protocol strictly adheres to customer security by discouraging remote credential sharing.",
                    recommended_action="Safe to verify at your local branch during regular banking hours at your convenience."
                ))
                break

        # Threat behaviors should only be attributed to the Caller/External party, not the Senior responding
        if not is_senior:
            # 1. Impersonation checks
            for subcat, patterns in PATTERNS_IMPERSONATION.items():
                for pat in patterns:
                    m = re.search(pat, text, re.IGNORECASE)
                    if m:
                        quote = m.group(0)
                        behaviors_detected["impersonation"].append(subcat)
                        findings.append(EvidenceFinding(
                            turn_number=turn.turn_number,
                            speaker=turn.speaker,
                            behavior_category="IMPERSONATION",
                            severity="MEDIUM" if subcat == "UTILITY_TELECOM" else "HIGH",
                            exact_quote=quote,
                            explanation=f"Caller asserts official institutional identity ({subcat.replace('_', ' ').title()}). Scammers exploit authority to bypass natural skepticism.",
                            why_it_matters="Elderly citizens naturally respect banks, electricity officials, and police, making impersonation the primary manipulation hook.",
                            recommended_action="Do not accept incoming caller claims. Terminate the call and verify through an official publicly published contact number."
                        ))
                        break

            # 2. Urgency and Intimidation
            for pat in PATTERNS_URGENCY_INTIMIDATION:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    behaviors_detected["urgency"].append(quote)
                    findings.append(EvidenceFinding(
                        turn_number=turn.turn_number,
                        speaker=turn.speaker,
                        behavior_category="URGENCY_INTIMIDATION",
                        severity="HIGH",
                        exact_quote=quote,
                        explanation="Artificial deadline or threat of imminent punitive action (power cutoff, arrest, or immediate financial penalty).",
                        why_it_matters="Manufactured panic induces cognitive tunnel vision, preventing the senior from contacting their children or advisors.",
                        recommended_action="Take a deliberate pause. Legitimate legal and utility procedures provide advance postal notices, never 10-minute ultimatums."
                    ))
                    break

            # 3. Secrecy and Isolation
            for pat in PATTERNS_SECRECY_ISOLATION:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    behaviors_detected["secrecy"].append(quote)
                    findings.append(EvidenceFinding(
                        turn_number=turn.turn_number,
                        speaker=turn.speaker,
                        behavior_category="SECRECY_ISOLATION",
                        severity="CRITICAL",
                        exact_quote=quote,
                        explanation="Mandate to keep conversation secret, avoid family contact, or remain isolated on the phone call.",
                        why_it_matters="Isolation is the primary tactic used to prevent tech-savvy family members or neighbors from intervening.",
                        recommended_action="Hang up immediately and inform your children, family members, or a trusted neighbor."
                    ))
                    break

            # 4. Credential Solicitation (only if NOT preceded by 'never share' or 'bank never asks')
            if not behaviors_detected["legitimate_safeguard"]:
                for pat in PATTERNS_CREDENTIAL_SOLICITATION:
                    m = re.search(pat, text, re.IGNORECASE)
                    if m:
                        quote = m.group(0)
                        behaviors_detected["credentials"].append(quote)
                        findings.append(EvidenceFinding(
                            turn_number=turn.turn_number,
                            speaker=turn.speaker,
                            behavior_category="CREDENTIAL_SOLICITATION",
                            severity="CRITICAL",
                            exact_quote=quote,
                            explanation="Direct solicitation of confidential credentials (OTP, PIN, or verification code).",
                            why_it_matters="RBI guidelines mandate that banks never solicit OTPs or PINs. Sharing this code enables instant irreversible fraud.",
                            recommended_action="NEVER share OTP, PIN, or CVV. No bank official, police officer, or utility provider has legitimate access to your OTP."
                        ))
                        break

            # 5. Financial Coercion / Transfers
            for pat in PATTERNS_FINANCIAL_COERCION:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    behaviors_detected["coercion"].append(quote)
                    findings.append(EvidenceFinding(
                        turn_number=turn.turn_number,
                        speaker=turn.speaker,
                        behavior_category="FINANCIAL_COERCION",
                        severity="CRITICAL",
                        exact_quote=quote,
                        explanation="Demand to make immediate payments via UPI/QR code or transfer savings to an alleged 'safety/RBI account'.",
                        why_it_matters="Neither the RBI nor police operate 'safety accounts' where citizens deposit money for clearance.",
                        recommended_action="Stop all financial transfers immediately. If any debit occurred, immediately report to Cyber Helpline 1930."
                    ))
                    break

            # 6. Remote Access Malware
            for pat in PATTERNS_REMOTE_ACCESS_MALWARE:
                m = re.search(pat, text, re.IGNORECASE)
                if m:
                    quote = m.group(0)
                    behaviors_detected["remote_access"].append(quote)
                    findings.append(EvidenceFinding(
                        turn_number=turn.turn_number,
                        speaker=turn.speaker,
                        behavior_category="REMOTE_ACCESS_MALWARE",
                        severity="CRITICAL",
                        exact_quote=quote,
                        explanation="Instruction to install screen-sharing software (QuickSupport, AnyDesk) or download untrusted APK files.",
                        why_it_matters="Screen-sharing software grants criminals complete visibility and remote takeover of mobile banking apps and OTPs.",
                        recommended_action="Do not download or install any applications requested over a phone call. Disconnect now."
                    ))
                    break

        return behaviors_detected, findings

    def analyze(self, turns: List[ConversationTurn], raw_transcript: str = "", is_demo: bool = False, demo_id: Optional[str] = None) -> AnalysisResult:
        if not turns:
            turns = parse_raw_transcript(raw_transcript)

        full_text = " ".join([t.text for t in turns])
        lang_detected = detect_language(full_text)
        
        all_findings: List[EvidenceFinding] = []
        turn_progressions: List[TurnProgression] = []
        
        # Cumulative state tracking
        active_impersonation = False
        active_urgency = False
        active_secrecy = False
        active_credentials = False
        active_coercion = False
        active_remote_access = False
        active_safeguard = False
        
        current_score = 0.0
        
        for turn in turns:
            markers, turn_findings = self._extract_turn_markers(turn)
            all_findings.extend(turn_findings)
            
            new_behaviors_this_turn = []
            
            if markers["impersonation"]:
                if not active_impersonation:
                    new_behaviors_this_turn.append("Impersonation Claim")
                active_impersonation = True
                
            if markers["urgency"]:
                if not active_urgency:
                    new_behaviors_this_turn.append("Urgency & Pressure")
                active_urgency = True
                
            if markers["secrecy"]:
                if not active_secrecy:
                    new_behaviors_this_turn.append("Secrecy / Isolation Mandate")
                active_secrecy = True
                
            if markers["credentials"]:
                if not active_credentials:
                    new_behaviors_this_turn.append("Credential Solicitation (OTP/PIN)")
                active_credentials = True
                
            if markers["coercion"]:
                if not active_coercion:
                    new_behaviors_this_turn.append("Coercive Money Transfer / QR Request")
                active_coercion = True
                
            if markers["remote_access"]:
                if not active_remote_access:
                    new_behaviors_this_turn.append("Remote Access App / APK Request")
                active_remote_access = True
                
            if markers["legitimate_safeguard"]:
                active_safeguard = True
                new_behaviors_this_turn.append("Official Protective Safeguard")

            # Progressive score calculation
            if active_safeguard and not (active_credentials or active_coercion or active_remote_access):
                # Safeguards hold risk strictly low
                current_score = min(12.0, max(current_score * 0.4, 5.0))
            else:
                base = 0.0
                if active_impersonation:
                    base += 28.0
                if active_urgency:
                    base += 24.0
                if active_secrecy:
                    base += 26.0
                if active_remote_access:
                    base += 32.0
                if active_credentials:
                    base += 38.0
                if active_coercion:
                    base += 38.0
                    
                # Combinatorial amplification for toxic multi-vector scams
                if active_impersonation and active_urgency and (active_credentials or active_coercion or active_remote_access):
                    base = max(base, 94.0)
                elif active_impersonation and (active_credentials or active_remote_access or active_coercion):
                    base = max(base, 85.0)
                elif (active_urgency or active_secrecy) and (active_credentials or active_coercion or active_remote_access):
                    base = max(base, 88.0)
                    
                current_score = min(98.5, max(current_score, base))
                
            # Classify turn risk level
            turn_risk: RiskLevel
            if (not active_impersonation and not active_urgency and not active_secrecy and 
                not active_credentials and not active_coercion and not active_remote_access and 
                not active_safeguard):
                turn_risk = "INSUFFICIENT EVIDENCE"
            elif active_safeguard and not (active_credentials or active_coercion or active_remote_access):
                turn_risk = "LOW RISK"
            elif current_score >= 61.0:
                turn_risk = "HIGH RISK"
            elif current_score >= 26.0:
                turn_risk = "SUSPICIOUS"
            else:
                turn_risk = "LOW RISK"
                
            if new_behaviors_this_turn:
                turn_rationale = f"Detected: {', '.join(new_behaviors_this_turn)}."
            elif active_safeguard:
                turn_rationale = "Legitimate institution safeguard maintains low risk."
            elif current_score > 60:
                turn_rationale = "High scam momentum continues from previous coercive tactics."
            elif turn_risk == "INSUFFICIENT EVIDENCE":
                turn_rationale = "Ambiguous dialogue with no distinguishable scam or safety markers."
            else:
                turn_rationale = "Dialogue continues without new threat markers."

            turn_progressions.append(TurnProgression(
                turn_number=turn.turn_number,
                speaker=turn.speaker,
                text=turn.text,
                cumulative_risk_score=round(current_score, 1),
                turn_risk_level=turn_risk,
                newly_detected_behaviors=new_behaviors_this_turn,
                turn_rationale=turn_rationale
            ))

        behavior_matrix = BehaviorMatrix(
            impersonation=active_impersonation,
            urgency_intimidation=active_urgency,
            secrecy_isolation=active_secrecy,
            credential_solicitation=active_credentials,
            financial_coercion=active_coercion,
            remote_access_malware=active_remote_access,
            legitimate_safeguards_present=active_safeguard
        )

        total_suspicious_flags = (
            int(active_impersonation) +
            int(active_urgency) +
            int(active_secrecy) +
            int(active_credentials) +
            int(active_coercion) +
            int(active_remote_access)
        )
        
        final_risk_level: RiskLevel
        final_score: float = current_score
        confidence: str = "HIGH"
        score_semantics: str
        
        # Check explicit classification conditions
        if total_suspicious_flags == 0 and not active_safeguard:
            final_risk_level = "INSUFFICIENT EVIDENCE"
            final_score = 15.0
            confidence = "LOW"
            score_semantics = "Indeterminate Context (Score 15/100). The conversation does not exhibit fraud markers, nor does it establish authenticated safety protocols. Additional context is required."
            summary = "The provided transcript contains neutral conversational exchanges without sufficient evidence to determine fraudulent intent or legitimate institutional protocol."
        elif active_safeguard and not (active_credentials or active_coercion or active_remote_access):
            final_risk_level = "LOW RISK"
            final_score = 10.0
            confidence = "HIGH"
            score_semantics = "Legitimate Protocol (Score 10/100). The caller explicitly observes customer security guidelines (physical branch visit, refusal to accept OTPs)."
            summary = "Legitimate communication confirmed. Despite the presence of sensitive domain keywords (bank, KYC, passbook), the interaction adheres strictly to official customer safety guidelines."
        elif (active_credentials or active_remote_access or active_coercion) and (active_impersonation or active_urgency or active_secrecy):
            final_risk_level = "HIGH RISK"
            final_score = max(current_score, 92.0)
            confidence = "HIGH"
            score_semantics = f"Critical Threat (Score {final_score:.0f}/100). Compounded fraudulent combination: Authority Impersonation + Pressure/Secrecy + Credential/Transfer Solicitation."
            summary = "Critical scam detected! The caller utilizes predatory tactics designed to deceive elderly citizens, including false authority, manufactured urgency, isolation demands, and credential/financial theft."
        elif total_suspicious_flags >= 2 or active_credentials or active_coercion or active_remote_access:
            final_risk_level = "HIGH RISK"
            final_score = max(current_score, 75.0)
            confidence = "HIGH"
            score_semantics = f"High Risk (Score {final_score:.0f}/100). Coercive tactics or credential requests detected."
            summary = "High probability scam. Dangerous patterns observed that violate standard security protocols."
        elif total_suspicious_flags == 1:
            final_risk_level = "SUSPICIOUS"
            final_score = 42.0
            confidence = "MEDIUM"
            score_semantics = "Elevated Precaution (Score 42/100). Unverified authority claims or artificial urgency detected without direct credential theft yet."
            summary = "Suspicious conversational patterns detected. While direct credential theft has not occurred yet, the caller's pressure or unsolicited claims warrant high caution."
        else:
            final_risk_level = "LOW RISK"
            final_score = 8.0
            confidence = "HIGH"
            score_semantics = "Low Risk (Score 8/100). Standard conversation without threat markers."
            summary = "No scam indicators observed in this conversation."

        protection_recommendations = self._generate_elder_advice(final_risk_level, behavior_matrix)
        
        primary_threat = None
        if active_remote_access:
            primary_threat = "Remote Access Tool (AnyDesk/QuickSupport) Device Takeover"
        elif active_credentials:
            primary_threat = "Direct Credential / OTP Harvesting"
        elif active_coercion:
            primary_threat = "Coercive Financial Transfer Fraud"
        elif active_impersonation and active_urgency:
            primary_threat = "Authority Impersonation & Panic Intimidation"
        elif active_impersonation:
            primary_threat = "Unsolicited Identity Claim"

        analysis_id = str(uuid.uuid4())[:8]

        return AnalysisResult(
            id=analysis_id,
            timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            overall_risk_level=final_risk_level,
            overall_risk_score=final_score,
            score_semantics=score_semantics,
            confidence_level=confidence,
            language_detected=lang_detected,
            summary=summary,
            primary_threat_vector=primary_threat,
            behavior_matrix=behavior_matrix,
            turn_progression=turn_progressions,
            evidence_findings=all_findings,
            protection_recommendations=protection_recommendations,
            raw_transcript=raw_transcript or "\n".join([f"{t.speaker}: {t.text}" for t in turns]),
            is_demo=is_demo,
            demo_scenario_id=demo_id
        )

    def _generate_elder_advice(self, risk: RiskLevel, matrix: BehaviorMatrix) -> List[str]:
        """Provides high-contrast, accessible, senior-focused actionable advice."""
        advice = []
        if risk == "HIGH RISK":
            advice.append("🛑 STOP & HANG UP: Disconnect the call immediately. Do not stay on the line.")
            if matrix.credential_solicitation:
                advice.append("🔒 NEVER DISCLOSE OTPs OR PINs: Banks and police never ask for 6-digit OTPs, ATM PINs, or UPI PINs under any circumstances.")
            if matrix.remote_access_malware:
                advice.append("⚠️ DO NOT INSTALL APPS: Do not install AnyDesk, QuickSupport, or click any APK link received on SMS.")
            if matrix.financial_coercion:
                advice.append("🚫 ZERO TRANSFERS: Never send money to any alleged 'safe account' or 'RBI verification account'. These are 100% fraudulent.")
            advice.append("📞 CALL NATIONAL CYBER HELPLINE 1930: If you have shared any money or credentials, dial 1930 immediately to freeze transactions.")
            advice.append("👨‍👩‍👦 TALK TO FAMILY: Immediately inform your son, daughter, or trusted neighbor. Scammers rely on keeping you isolated.")
        elif risk == "SUSPICIOUS":
            advice.append("⏸️ PAUSE BEFORE ACTING: Do not rush into making payments or decisions due to deadlines.")
            advice.append("🏢 INDEPENDENT VERIFICATION: Ask for the caller's name and designation, hang up, and call the official telephone number printed on your utility bill or bank card.")
            advice.append("🤝 CONSULT A SECOND OPINION: Discuss this request with a family member or trusted friend before agreeing.")
            advice.append("🔐 KEEP CREDENTIALS SAFE: Remember that official agencies will never penalize you for taking time to verify.")
        elif risk == "INSUFFICIENT EVIDENCE":
            advice.append("🔍 REMAIN VIGILANT: This interaction is too brief to confirm intent. Ask who is calling and their official purpose.")
            advice.append("🛡️ DO NOT VOLUNTEER INFORMATION: Do not share personal details, bank accounts, or identity numbers to unverified inquiries.")
            advice.append("📞 VERIFY CALLER ID: If in doubt, ask them to send an official letter or written notice.")
        else: # LOW RISK
            advice.append("✅ ROUTINE PROTOCOL: The interaction complies with safe banking practices.")
            advice.append("🏛️ BRANCH VISIT: For KYC or document updates, always prefer visiting your local bank branch in person at your convenience.")
            advice.append("🛡️ GENERAL RULE: Continue your healthy habit of never sharing OTPs or passwords over phone calls.")
            
        return advice

engine = ScamDetectionEngine()
