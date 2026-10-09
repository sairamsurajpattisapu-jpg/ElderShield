"""
ElderShield — Standardized Multi-Category Scam Detection Evaluation Dataset
Contains labeled multi-turn conversational evaluation samples across 12 required categories:
  1. Legitimate banking conversations
  2. Legitimate conversations mentioning OTPs or account security
  3. Scam attempts requesting OTPs, PINs, or passwords
  4. Digital-arrest and law-enforcement impersonation
  5. Urgent payment demands
  6. Remote-access installation scams
  7. Legitimate courier and delivery conversations
  8. Legitimate government-service conversations
  9. Ambiguous conversations with insufficient evidence
 10. Multilingual and code-switched utterances (English, Hindi, Telugu, Hinglish, Teluglish)
 11. ASR transcription errors and incomplete utterances
 12. Conflicting or contradictory conversational evidence

Disclaimer:
  All samples in this dataset are curated synthetic/benchmarked test cases created specifically
  for systematic rule validation, regression prevention, and false-alarm rate auditing.
  They are kept distinct from development training fixtures.
"""

from typing import List, Dict, Any

EVALUATION_SAMPLES: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # 1. Legitimate Banking Conversations
    # -------------------------------------------------------------------------
    {
        "id": "eval_legit_bank_01",
        "category": "legitimate_banking",
        "language": "English",
        "ground_truth": "SAFE",
        "expected_risk_level": "LOW_RISK",
        "expected_decision": "ALLOW",
        "transcript": (
            "Caller: Good morning Mrs. Kulkarni, this is Priya from State Bank of India.\n"
            "Senior: Hello, yes? Is everything fine with my fixed deposit renewal?\n"
            "Caller: Yes madam, your deposit matured yesterday. I am calling to inform you that you can visit our branch in person next week whenever you are free to sign the renewal form.\n"
            "Senior: Okay, I will come with my daughter on Thursday.\n"
            "Caller: Wonderful, please take your time and have a pleasant day."
        )
    },
    {
        "id": "eval_legit_bank_02",
        "category": "legitimate_banking",
        "language": "English",
        "ground_truth": "SAFE",
        "expected_risk_level": "LOW_RISK",
        "expected_decision": "ALLOW",
        "transcript": (
            "Caller: Hello, I am calling from HDFC Bank customer service.\n"
            "Senior: Yes, what is this regarding?\n"
            "Caller: We noticed your passbook has not been printed for six months. You can use our passbook kiosk at any local branch at your convenience.\n"
            "Senior: Thank you, I will do that when I go to market."
        )
    },

    # -------------------------------------------------------------------------
    # 2. Legitimate Conversations Mentioning OTPs / Security Safeguards
    # -------------------------------------------------------------------------
    {
        "id": "eval_legit_otp_safeguard_01",
        "category": "legitimate_otp_safeguards",
        "language": "English",
        "ground_truth": "SAFE",
        "expected_risk_level": "LOW_RISK",
        "expected_decision": "ALLOW",
        "transcript": (
            "Caller: Hello Mr. Rao, this is Anand from ICICI Bank security desk.\n"
            "Senior: Did someone try to hack my pension account?\n"
            "Caller: No sir, this is a routine annual security awareness check. Please remember our bank never asks for your OTP or password over phone calls. Never share your OTP with anyone.\n"
            "Senior: Yes, my son also warned me never to share any OTP.\n"
            "Caller: Exactly sir. If you ever have any doubt, visit your branch in person. No need to hurry."
        )
    },
    {
        "id": "eval_legit_otp_safeguard_02",
        "category": "legitimate_otp_safeguards",
        "language": "Hinglish",
        "ground_truth": "SAFE",
        "expected_risk_level": "LOW_RISK",
        "expected_decision": "ALLOW",
        "transcript": (
            "Caller: Namaste Sharmaji, main Axis Bank branch se bol raha hoon.\n"
            "Senior: Haan boliye, kya hua?\n"
            "Caller: Bank kabhi bhi aapka OTP ya PIN phone par nahi mangta. Agar koi phone karke OTP maange toh mat dena. Aap aaram se branch aakar miliye agle hafte.\n"
            "Senior: Theek hai beta, main branch aa jaunga."
        )
    },

    # -------------------------------------------------------------------------
    # 3. Scam Attempts Requesting OTPs, PINs, or Passwords
    # -------------------------------------------------------------------------
    {
        "id": "eval_scam_otp_demand_01",
        "category": "scam_credential_theft",
        "language": "English",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: I am calling from State Bank of India debit card division.\n"
            "Senior: Yes? What happened to my card?\n"
            "Caller: Your NetBanking is expiring today and account blocked immediately. Tell me the 6 digit OTP you received right now to stop disconnection!"
        )
    },
    {
        "id": "eval_scam_otp_demand_02",
        "category": "scam_credential_theft",
        "language": "Hindi",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: बैंक से बोल रहा हूँ। आपका खाता तुरंत फ्रीज हो जाएगा।\n"
            "Senior: अरे, ऐसा क्यों?\n"
            "Caller: तुरंत ओटीपी बताइए ताकि ब्लॉक रोक सकें! कोड बोलो जल्दी!"
        )
    },

    # -------------------------------------------------------------------------
    # 4. Digital-Arrest & Law-Enforcement Impersonation
    # -------------------------------------------------------------------------
    {
        "id": "eval_scam_digital_arrest_01",
        "category": "digital_arrest",
        "language": "English",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: This is Officer Verma from Central Bureau of Investigation, New Delhi Headquarters.\n"
            "Senior: Why are you calling an old woman like me?\n"
            "Caller: A parcel seized at Mumbai customs had contraband and your Aadhaar card. You are under digital arrest. Do not inform your family or disconnect this call."
        )
    },
    {
        "id": "eval_scam_digital_arrest_02",
        "category": "digital_arrest",
        "language": "Telugu",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: నేను సైబర్ క్రైమ్ పోలీస్ స్టేషన్ నుంచి డీఎస్పీ రావు మాట్లాడుతున్నాను. మీ పేరు మీద పార్శిల్ లో డ్రగ్స్ దొరికాయి. డిజిటల్ అరెస్ట్ వారెంట్ ఇష్యూ అయింది.\n"
            "Senior: అయ్యో! నాకు తెలియదు బాబు.\n"
            "Caller: ఎవరికీ చెప్పకండి! కాల్ కట్ చేయొద్దు. వెంటనే ఆర్ బి ఐ సేఫ్ అకౌంట్ కి డబ్బులు ట్రాన్స్ ఫర్ చేయండి!"
        )
    },

    # -------------------------------------------------------------------------
    # 5. Urgent Payment Demands (Utility Disconnection / Extortion)
    # -------------------------------------------------------------------------
    {
        "id": "eval_scam_urgent_payment_01",
        "category": "urgent_payment_demand",
        "language": "English",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: Hello, I am calling from Electricity Board power department.\n"
            "Senior: Yes, I paid my bill already.\n"
            "Caller: Your payment failed on server. Power will be cut at 8 PM tonight within 15 minutes unless you clear the 120 rupees bill via Google Pay right now!"
        )
    },
    {
        "id": "eval_scam_urgent_payment_02",
        "category": "urgent_payment_demand",
        "language": "Hinglish",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: Bijli vibhag se bol raha hoon. Aaj raat bijli kat jayegi 10 minute me.\n"
            "Senior: Please light mat kaatiye.\n"
            "Caller: Turant kijiye, abhi nahi kiya toh transfer 500 rs to safety account abhi!"
        )
    },

    # -------------------------------------------------------------------------
    # 6. Remote-Access Installation Scams (AnyDesk / QuickSupport)
    # -------------------------------------------------------------------------
    {
        "id": "eval_scam_remote_access_01",
        "category": "remote_access_scam",
        "language": "English",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: I am calling from telecom department regarding your SIM card.\n"
            "Senior: Is my SIM blocked?\n"
            "Caller: Yes, download QuickSupport app immediately from SMS link I sent and share your screen to unblock."
        )
    },
    {
        "id": "eval_scam_remote_access_02",
        "category": "remote_access_scam",
        "language": "English",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: Technical support officer calling. Your mobile has viruses.\n"
            "Senior: What should I do?\n"
            "Caller: Install AnyDesk app right now on your phone and read out the 9 digit code on screen!"
        )
    },

    # -------------------------------------------------------------------------
    # 7. Legitimate Courier & Delivery Conversations
    # -------------------------------------------------------------------------
    {
        "id": "eval_legit_courier_01",
        "category": "legitimate_courier",
        "language": "English",
        "ground_truth": "SAFE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "transcript": (
            "Caller: Good afternoon, this is delivery driver with BlueDart parcel.\n"
            "Senior: Yes, I am at home on third floor.\n"
            "Caller: I am at your security gate now, please open door.\n"
            "Senior: Coming down in one minute."
        )
    },
    {
        "id": "eval_legit_courier_02",
        "category": "legitimate_courier",
        "language": "Hinglish",
        "ground_truth": "SAFE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "transcript": (
            "Caller: Namaste sir, delivery boy bol raha hoon parcel leke.\n"
            "Senior: Haan beta, main ghar par hoon.\n"
            "Caller: Gate par security ko bata dijiye parcel chhod doon."
        )
    },

    # -------------------------------------------------------------------------
    # 8. Legitimate Government-Service Conversations
    # -------------------------------------------------------------------------
    {
        "id": "eval_legit_govt_01",
        "category": "legitimate_govt_service",
        "language": "English",
        "ground_truth": "SAFE",
        "expected_risk_level": "LOW_RISK",
        "expected_decision": "ALLOW",
        "transcript": (
            "Caller: Hello Mr. Murthy, this is Visakhapatnam municipal water department.\n"
            "Senior: Yes sir, is water coming tomorrow?\n"
            "Caller: Yes, we are scheduling annual pipeline testing next month. You can visit our local office counter at your convenience if you need new connection forms.\n"
            "Senior: Thank you for informing."
        )
    },
    {
        "id": "eval_legit_govt_02",
        "category": "legitimate_govt_service",
        "language": "English",
        "ground_truth": "SAFE",
        "expected_risk_level": "LOW_RISK",
        "expected_decision": "ALLOW",
        "transcript": (
            "Caller: This is the pension disbursement office calling regarding your Jeevan Pramaan submission.\n"
            "Senior: Do I have to pay anything?\n"
            "Caller: No payment needed at all. You can submit documents copy at our official counter or visit our branch in person whenever you feel comfortable next Tuesday."
        )
    },

    # -------------------------------------------------------------------------
    # 9. Ambiguous Conversations with Insufficient Evidence
    # -------------------------------------------------------------------------
    {
        "id": "eval_ambiguous_01",
        "category": "ambiguous_dialogue",
        "language": "English",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "transcript": (
            "Caller: Hello, is this the Sharma residence?\n"
            "Senior: Yes, who is calling?\n"
            "Caller: I will call back in the evening when your son is home."
        )
    },
    {
        "id": "eval_ambiguous_02",
        "category": "ambiguous_dialogue",
        "language": "English",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "transcript": (
            "Caller: Hello, can you hear me properly?\n"
            "Senior: The line is very noisy, speak louder please.\n"
            "Caller: Okay, let me redial you."
        )
    },

    # -------------------------------------------------------------------------
    # 10. Multilingual & Code-Switched Utterances (Hindi, Telugu, Hinglish, Teluglish)
    # -------------------------------------------------------------------------
    {
        "id": "eval_multilingual_teluglish_scam_01",
        "category": "multilingual_code_switched",
        "language": "Teluglish",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: Hello, police case registered against you. Digital arrest warrant issue ayyindi.\n"
            "Senior: Ayyo saar! Nenu em cheyaledu please.\n"
            "Caller: Evariki cheppakandi, phone cut cheyoddu. Google pay cheyandi right now!"
        )
    },
    {
        "id": "eval_multilingual_hinglish_scam_02",
        "category": "multilingual_code_switched",
        "language": "Hinglish",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: Main crime branch officer bol raha hoon. Parcel lo drugs mila hai.\n"
            "Senior: Mujhe pata nahi tha sir.\n"
            "Caller: Kisi ko mat batana, phone mat kaatna. Turant paise transfer karo!"
        )
    },

    # -------------------------------------------------------------------------
    # 11. ASR Transcription Errors & Incomplete Utterances
    # -------------------------------------------------------------------------
    {
        "id": "eval_asr_noisy_01",
        "category": "asr_noisy_incomplete",
        "language": "English",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: Calling from central bureau of investigation... parcel seized...\n"
            "Senior: Hello... static...\n"
            "Caller: Under digital arrest! Share the otp right now!"
        )
    },
    {
        "id": "eval_asr_incomplete_02",
        "category": "asr_noisy_incomplete",
        "language": "English",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "transcript": (
            "Caller: Yes hello... audio crackle...\n"
            "Senior: Who is this?\n"
            "Caller: Yes hello... call dropped."
        )
    },

    # -------------------------------------------------------------------------
    # 12. Conflicting or Contradictory Conversational Evidence
    # -------------------------------------------------------------------------
    {
        "id": "eval_conflicting_01",
        "category": "conflicting_evidence",
        "language": "English",
        "ground_truth": "SAFE",
        "expected_risk_level": "LOW_RISK",
        "expected_decision": "ALLOW",
        "transcript": (
            "Caller: Good morning Mr. Bannerjee, State Bank of India.\n"
            "Senior: Is this about my online bill payment or OTP?\n"
            "Caller: No sir, our bank never asks for your OTP over phone calls. You can visit our branch in person whenever you feel comfortable next month."
        )
    },
    {
        "id": "eval_conflicting_02",
        "category": "conflicting_evidence",
        "language": "English",
        "ground_truth": "SCAM",
        "expected_risk_level": "HIGH_RISK",
        "expected_decision": "BLOCK",
        "transcript": (
            "Caller: We are from bank security. We normally say visit our branch, BUT today your account has emergency attack!\n"
            "Senior: Should I come to the branch?\n"
            "Caller: Do not go to the branch! Branch cannot resolve this! Share your OTP immediately or account frozen!"
        )
    }
]
