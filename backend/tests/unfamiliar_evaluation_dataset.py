"""
ElderShield — Unfamiliar Conversation Evaluation Dataset (101 Samples)
========================================================================
Purpose:
  Independent evaluation dataset designed to test the frozen ElderShield scam
  detection engine against diverse, unfamiliar conversations, edge cases,
  and false-alarm stress vectors.

Provenance & Methodology:
  - Provenance: Carefully constructed synthetic stress-test dialogues and
    realistic scenarios derived from public consumer fraud advisories
    (Indian Cyber Crime Coordination Centre / I4C, Reserve Bank of India / RBI,
    and Department of Telecommunications / DoT advisory bulletins).
  - Explicit Non-Overlap: Does NOT reuse sentences or exact trigger templates
    from development fixtures (scenarios.py, dataset.py, or evaluation_dataset.py).
  - Lexical Diversity: Varies sentence order, conversational turn counts,
    speaker behaviors, subtle indirect requests, and contextual nuances.
  - False-Alarm Stress Vectors: Contains numerous legitimate conversations
    mentioning sensitive words (police, OTP, urgency, payments, bills, KYC)
    without fraudulent coercion.
  - Multi-Lingual Representation: English, Hindi (Devanagari), Hinglish
    (Romanized Hindi), Telugu (Telugu Script), and Teluglish (Romanized Telugu).

Total Sample Count: 101 Distinct Conversations
"""

from typing import List, Dict, Any

UNFAMILIAR_EVALUATION_SAMPLES: List[Dict[str, Any]] = [
    # =========================================================================
    # CATEGORY 1: CREDENTIAL THEFT AND OTP REQUESTS (12 SAMPLES)
    # Ground Truth: SCAM | Expected Decision: BLOCK | Expected Level: HIGH_RISK
    # =========================================================================
    {
        "id": "unfam_cred_001_en",
        "category": "credential_theft_otp",
        "language": "English",
        "provenance": "public_advisory_case_pattern (RBI Banking Fraud)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Greetings, I am reaching out from Punjab National Bank credit cards desk.\n"
            "Senior: Yes, what is this call about?\n"
            "Caller: Your card has accumulated 14,000 reward points expiring in 15 minutes. To convert into direct bank cash, please read out the one time password just generated on your mobile phone.\n"
            "Senior: Is it required over phone?\n"
            "Caller: Yes sir, give the code immediately or points will lapse permanently."
        )
    },
    {
        "id": "unfam_cred_002_en",
        "category": "credential_theft_otp",
        "language": "English",
        "provenance": "synthetic_stress_test (Subtle Credential Extraction)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Hello ma'am, this is ICICI Bank security division.\n"
            "Senior: Yes, is something wrong?\n"
            "Caller: We flagged an international charge of $450 from London. Account suspended today unless you cancel it.\n"
            "Senior: I never bought anything from London!\n"
            "Caller: Don't worry. To reverse this debit, share the 6 digit OTP you see on your SMS right now."
        )
    },
    {
        "id": "unfam_cred_003_hi",
        "category": "credential_theft_otp",
        "language": "Hindi",
        "provenance": "public_advisory_case_pattern (I4C Helpline Report)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: नमस्कार, मैं बैंक अधिकारी बोल रहा हूँ हेड ऑफिस से। आपका एटीएम कार्ड ब्लॉक हो गया है।\n"
            "Senior: अरे, मैं तो कल ही पेंशन निकालने वाला था।\n"
            "Caller: तुरंत चालू करने के लिए आपके फोन पर 6 अंकों का ओटीपी आया है। तुरंत ओटीपी बताइए, 10 मिनट में कार्ड बंद हो जाएगा।"
        )
    },
    {
        "id": "unfam_cred_004_hinglish",
        "category": "credential_theft_otp",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish Debit Card Phishing)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Hello sir, main Axis Bank head office se baat kar raha hoon.\n"
            "Senior: Haan boliye beta.\n"
            "Caller: Sir aapka NetBanking account blocked immediately ho raha hai KYC expire hone ki wajah se.\n"
            "Senior: Toh branch aana padega kya?\n"
            "Caller: Branch aane ki zaroorat nahi hai sir, turant phone par SMS code batao verification ke liye."
        )
    },
    {
        "id": "unfam_cred_005_te",
        "category": "credential_theft_otp",
        "language": "Telugu",
        "provenance": "public_advisory_case_pattern (Telangana Cyber Police Bulletin)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: నమస్కారం అండి, నేను స్టేట్ బ్యాంక్ ఆఫ్ ఇండియా మేనేజర్ ని మాట్లాడుతున్నాను.\n"
            "Senior: అవునా, ఏమిటండీ విషయం?\n"
            "Caller: మీ ఏటీఎం కార్డు ఈరోజే బ్లాక్ అవుతుంది. వెంటనే మీ ఫోన్ కి వచ్చిన ఓటీపీ చెప్పండి, లేకపోతే అకౌంట్ ఆగిపోతుంది."
        )
    },
    {
        "id": "unfam_cred_006_teluglish",
        "category": "credential_theft_otp",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Teluglish Banking Phish)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Hello amma, nenu SBI bank officer ni call chesthunnanu.\n"
            "Senior: Cheppandi babu, pension vachinda?\n"
            "Caller: Me pension account freeze ayyindi eeroju. Ippude mobile lo vachina otp cheppandi, lekapothe money cut avthundi."
        )
    },
    {
        "id": "unfam_cred_007_en",
        "category": "credential_theft_otp",
        "language": "English",
        "provenance": "public_advisory_case_pattern (EPFO Pension Update Fraud)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Good afternoon, calling from EPFO department life certificate verification desk.\n"
            "Senior: Hello, yes? My Jeevan Pramaan was due this month.\n"
            "Caller: Exactly sir, your pension disbursement will stop from Monday unless authenticated now. Enter your UPI PIN on the prompt or share the SMS code."
        )
    },
    {
        "id": "unfam_cred_008_hinglish",
        "category": "credential_theft_otp",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Telecom SIM Block Urgency)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: TRAI verification desk se bol raha hoon. Aapka SIM card block hoga aaj raat 8 baje.\n"
            "Senior: Kyun block hoga bhai?\n"
            "Caller: Aadhar link nahi hai. Turant aadhar verification ke liye mobile par aaya hua OTP boliye."
        )
    },
    {
        "id": "unfam_cred_009_en",
        "category": "credential_theft_otp",
        "language": "English",
        "provenance": "public_advisory_case_pattern (Electricity DISCOM OTP Phish)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: This is Officer Verma from Electricity Board central server billing.\n"
            "Senior: Yes sir?\n"
            "Caller: Disconnect tonight at 9 PM because bill status is pending. Tell me the OTP sent to your phone to update the power meter."
        )
    },
    {
        "id": "unfam_cred_010_te",
        "category": "credential_theft_otp",
        "language": "Telugu",
        "provenance": "public_advisory_case_pattern (Power Disconnection Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: విద్యుత్ శాఖ నుంచి మాట్లాడుతున్నాం. మీ కరెంట్ బిల్లు కట్టలేదు, ఈరోజే కరెంట్ కట్ చేస్తాం.\n"
            "Senior: నేను గత వారమే కట్టానండి.\n"
            "Caller: రికార్డులో రాలేదు. వెంటనే 10 నిమిషాల్లో ఫోన్ కు వచ్చిన ఓటీపీ చెప్పండి."
        )
    },
    {
        "id": "unfam_cred_011_hinglish",
        "category": "credential_theft_otp",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Fake Reward Point Phishing)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: HDFC Bank credit card reward department se baat kar raha hoon.\n"
            "Senior: Haan boliye?\n"
            "Caller: Aapka card block ho jayega agar reward claim nahi kiya. Turant screen par aaya hua pin number ivvandi ya OTP batao."
        )
    },
    {
        "id": "unfam_cred_012_teluglish",
        "category": "credential_theft_otp",
        "language": "Teluglish",
        "provenance": "public_advisory_case_pattern (Pension Scheme Aadhaar Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Jeevan pramaan patra office nunchi call chesthunnamu saar. Me pension aagipothundi.\n"
            "Senior: Ayyo, pension aagipothe ela?\n"
            "Caller: Ventane me phone ki vachina 6 digit code cheppandi, customer care mat karo."
        )
    },

    # =========================================================================
    # CATEGORY 2: DIGITAL ARREST AND LAW ENFORCEMENT IMPERSONATION (12 SAMPLES)
    # Ground Truth: SCAM | Expected Decision: BLOCK | Expected Level: HIGH_RISK
    # =========================================================================
    {
        "id": "unfam_arrest_001_en",
        "category": "digital_arrest_impersonation",
        "language": "English",
        "provenance": "public_advisory_case_pattern (CBI Digital Arrest Case)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: This is Inspector Ajay Rao calling from Central Bureau of Investigation cyber crime branch.\n"
            "Senior: Officer? What is the matter?\n"
            "Caller: A courier in Mumbai containing 16 fake passports and narcotic contraband was registered with your Aadhaar. You are under digital arrest.\n"
            "Senior: I am an elderly pensioner in Pune, this is a terrible mistake!\n"
            "Caller: Stay in a closed room. Do not inform family or disconnect this call. You will face immediate custody unless you cooperate."
        )
    },
    {
        "id": "unfam_arrest_002_en",
        "category": "digital_arrest_impersonation",
        "language": "English",
        "provenance": "public_advisory_case_pattern (Customs Narcotics Threat)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: This is Officer Rajesh from Customs Department Indira Gandhi International Airport.\n"
            "Senior: Hello?\n"
            "Caller: A parcel seized under your name contained illegal MDMA drugs. Police on the way to your house.\n"
            "Senior: Oh God, I have high blood pressure, please listen to me!\n"
            "Caller: Isolate yourself immediately. Keep this confidential and stay on the video call."
        )
    },
    {
        "id": "unfam_arrest_003_hi",
        "category": "digital_arrest_impersonation",
        "language": "Hindi",
        "provenance": "public_advisory_case_pattern (Delhi Police Digital Arrest)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: मैं सब इंस्पेक्टर पाटिल बोल रहा हूँ दिल्ली साइबर क्राइम सेल से। आपके खिलाफ मनी लॉन्ड्रिंग में अरेस्ट वारंट जारी हुआ है।\n"
            "Senior: साहब, मैंने कभी कोई गलत काम नहीं किया।\n"
            "Caller: आप डिजिटल अरेस्ट में हैं। अकेले कमरे में बैठिए और किसी को मत बताना, नहीं तो तुरंत जेल होगी।"
        )
    },
    {
        "id": "unfam_arrest_004_hinglish",
        "category": "digital_arrest_impersonation",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish Enforcement Directorate Intimidation)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Enforcement Directorate officer bol raha hoon. Supreme Court order ke mutabik aapka bank account freeze ho raha hai.\n"
            "Senior: Arre sahab maine kya kiya?\n"
            "Caller: Digital arrest warrant issue hua hai. Phone mat kaatna aur ghar pe kisi ko mat batana."
        )
    },
    {
        "id": "unfam_arrest_005_te",
        "category": "digital_arrest_impersonation",
        "language": "Telugu",
        "provenance": "public_advisory_case_pattern (Hyderabad Cyber Cell Arrest Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: నేను సైబర్ క్రైమ్ పోలీస్ స్టేషన్ నుంచి డీఎస్పీ మాట్లాడుతున్నాను. మీ ఆధార్ కార్డు పై 20 అక్రమ బ్యాంకు ఖాతాలు తెరిచారు.\n"
            "Senior: అయ్యో సర్, నాకేమీ తెలియదు.\n"
            "Caller: మీరు డిజిటల్ అరెస్ట్ లో ఉన్నారు. లైన్ లో ఉండండి, పిల్లలకు చెప్పొద్దు, పోలీసులు వస్తున్నారు."
        )
    },
    {
        "id": "unfam_arrest_006_teluglish",
        "category": "digital_arrest_impersonation",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Teluglish Narcotics Contraband Extortion)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Delhi narcotics police calling saar. Parcel lo drugs dorikayi me peru meeda.\n"
            "Senior: Naa peru meeda na? Nenu eppudu parcel order cheyaledu!\n"
            "Caller: Police case file ayyindi. Call cut cheyoddu, evariki cheppakandi, arrest chestaru."
        )
    },
    {
        "id": "unfam_arrest_007_en",
        "category": "digital_arrest_impersonation",
        "language": "English",
        "provenance": "public_advisory_case_pattern (Telecom TRAI Deactivation Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Calling from Telecom Regulatory Authority of India headquarters.\n"
            "Senior: Yes, who is this?\n"
            "Caller: Your mobile number was used to transmit 2,000 harassing messages. SIM will be blocked within 30 minutes and case registered with police cell."
        )
    },
    {
        "id": "unfam_arrest_008_hinglish",
        "category": "digital_arrest_impersonation",
        "language": "Hinglish",
        "provenance": "public_advisory_case_pattern (CBI Fake Warrant Extortion)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Central Bureau of Investigation Head Office se DSP bol raha hoon.\n"
            "Senior: Haan sir?\n"
            "Caller: Aapke khilaaf arrest warrant issue ho chuka hai. Turant kijiye jo hum keh rahe hain, kisi ko mat batana."
        )
    },
    {
        "id": "unfam_arrest_009_en",
        "category": "digital_arrest_impersonation",
        "language": "English",
        "provenance": "synthetic_stress_test (Supreme Court Contempt Notice Threat)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: This is Officer Bannerjee from Enforcement Directorate national squad.\n"
            "Senior: What is this regarding?\n"
            "Caller: Supreme court order issued under anti-terror funding against your account. Under digital arrest immediately. Stay on the line."
        )
    },
    {
        "id": "unfam_arrest_009b_te",
        "category": "digital_arrest_impersonation",
        "language": "Telugu",
        "provenance": "public_advisory_case_pattern (Customs Contraband Seizure)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: కస్టమ్స్ ఆఫీస్ నుంచి కాల్ చేస్తున్నాము. మీ పార్శిల్ లో డ్రగ్స్ పట్టుకున్నారు.\n"
            "Senior: బాబోయ్, అది నా పార్శిల్ కాదండి.\n"
            "Caller: కోర్టు నుంచి అరెస్ట్ వారెంట్ వచ్చింది. ఒంటరిగా గదిలో ఉండండి, ఫోన్ పెట్టొద్దు."
        )
    },
    {
        "id": "unfam_arrest_011_hinglish",
        "category": "digital_arrest_impersonation",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Cyber Police Intimidation)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Mumbai cyber cell police station se inspector bol raha hoon.\n"
            "Senior: Kya hua sahab?\n"
            "Caller: Aapke number se illegal trading hui hai. Immediate custody hogi agar line disconnect ki toh. Ghar pe mat batao."
        )
    },
    {
        "id": "unfam_arrest_012_teluglish",
        "category": "digital_arrest_impersonation",
        "language": "Teluglish",
        "provenance": "public_advisory_case_pattern (Warrant Intimidation)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: DSP nunchi call saar, police case registered against your bank account.\n"
            "Senior: Naa account meeda case enti sir?\n"
            "Caller: Digital arrest chesamu. 10 nimishallo police lu vasthunnaru, phone pettaddu."
        )
    },

    # =========================================================================
    # CATEGORY 3: URGENT PAYMENT DEMANDS & FAKE SAFE ACCOUNTS (12 SAMPLES)
    # Ground Truth: SCAM | Expected Decision: BLOCK | Expected Level: HIGH_RISK
    # =========================================================================
    {
        "id": "unfam_pay_001_en",
        "category": "urgent_payment_demands",
        "language": "English",
        "provenance": "public_advisory_case_pattern (RBI Escrow Impersonation)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: I am calling from Reserve Bank of India fraud prevention wing.\n"
            "Senior: Yes, I am listening.\n"
            "Caller: All commercial bank accounts are compromised by malware today. You must transfer your savings to the RBI safety account right now to safeguard your balance."
        )
    },
    {
        "id": "unfam_pay_002_en",
        "category": "urgent_payment_demands",
        "language": "English",
        "provenance": "public_advisory_case_pattern (Electricity Utility Extortion)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Calling from electricity board power department.\n"
            "Senior: Yes?\n"
            "Caller: Your power will be cut tonight at 8 PM for unpaid bills. Clear the electricity bill before disconnection via Google Pay immediately."
        )
    },
    {
        "id": "unfam_pay_003_hi",
        "category": "urgent_payment_demands",
        "language": "Hindi",
        "provenance": "public_advisory_case_pattern (RBI Verification Deposit Fraud)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: आरबीआई अधिकारी बात कर रहा हूँ। आपके बैंक खाते में अवैध लेनदेन पकड़ा गया है।\n"
            "Senior: मैंने तो कोई लेनदेन नहीं किया।\n"
            "Caller: अपने पैसे बचाने के लिए आरबीआई खाते में ट्रांसफर तुरंत कीजिए, 10 मिनट में खाता सील हो जाएगा।"
        )
    },
    {
        "id": "unfam_pay_004_hinglish",
        "category": "urgent_payment_demands",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish Urgent Clearance Demand)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Discom bijli vibhag se bol raha hoon sir. Aaj raat bijli kat jayegi agar bill update nahi hua.\n"
            "Senior: Kitna rupaye baki hai?\n"
            "Caller: Sir turant ₹450 pay via PhonePe right now to stop disconnection."
        )
    },
    {
        "id": "unfam_pay_005_te",
        "category": "urgent_payment_demands",
        "language": "Telugu",
        "provenance": "public_advisory_case_pattern (APSPDCL Power Bill Fraud)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: విద్యుత్ శాఖ ఆఫీసర్ ని. ఈరోజే కరెంట్ కట్ ఆర్డర్ వచ్చింది.\n"
            "Senior: ఎందుకు కట్ చేస్తారు బాబు?\n"
            "Caller: బిల్లు సర్వర్ లో అప్డేట్ కాలేదు. గూగుల్ పే చేయండి వెంటనే, 10 నిమిషాల్లో లైన్ కట్ అవుతుంది."
        )
    },
    {
        "id": "unfam_pay_006_teluglish",
        "category": "urgent_payment_demands",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Teluglish Safe Account Transfer)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: RBI officer ni saar. Me account freeze lo undi.\n"
            "Senior: Naa dabbu emavthundi sir?\n"
            "Caller: RBI safety account ki dabbu transfer cheyyandi ippude, lekapothe motham balance freeze aypothundi."
        )
    },
    {
        "id": "unfam_pay_007_en",
        "category": "urgent_payment_demands",
        "language": "English",
        "provenance": "public_advisory_case_pattern (CBI Clearance Escrow Demand)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: From Central Bureau of Investigation headquarters Delhi.\n"
            "Senior: Yes sir?\n"
            "Caller: Case registered for illegal remittances. Transfer 50,000 rupees to government verification escrow account within 15 minutes to obtain clearance certificate."
        )
    },
    {
        "id": "unfam_pay_008_hinglish",
        "category": "urgent_payment_demands",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish Safe Account Transfer)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Bank fraud prevention department head office se bol raha hoon.\n"
            "Senior: Kya hua sahab mere account ko?\n"
            "Caller: Account freeze ho gaya hai. Paise transfer karo to RBI safe account immediately to unfreeze."
        )
    },
    {
        "id": "unfam_pay_009_en",
        "category": "urgent_payment_demands",
        "language": "English",
        "provenance": "public_advisory_case_pattern (Electricity DISCOM Emergency Pay)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: BESCOM power office assistant engineer speaking.\n"
            "Senior: Good afternoon sir.\n"
            "Caller: Your power will be cut tonight at 9 PM. Transfer rupees 350 to our clearing account right now."
        )
    },
    {
        "id": "unfam_pay_010_te",
        "category": "urgent_payment_demands",
        "language": "Telugu",
        "provenance": "public_advisory_case_pattern (Safe Escrow Telugu Fraud)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: రిజర్వ్ బ్యాంక్ అధికారిని. మీ సేవింగ్స్ ఖాతా ప్రమాదంలో ఉంది.\n"
            "Senior: ఇప్పుడు నేను ఏమి చేయాలి?\n"
            "Caller: వెంటనే సేఫ్ అకౌంట్ కి ట్రాన్స్ ఫర్ చేయండి మీ డిపాజిట్లు, ఆఖరి అవకాశం ఇది."
        )
    },
    {
        "id": "unfam_pay_011_hinglish",
        "category": "urgent_payment_demands",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish Bill Disconnection Urgency)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Power department head office se notice hai. Bijli kat jayegi aaj raat 8 baje.\n"
            "Senior: Beta maine pay kiya tha.\n"
            "Caller: Server par zero balance hai. Abhi nahi kiya toh disconnection hoga, pay via Paytm right now."
        )
    },
    {
        "id": "unfam_pay_012_teluglish",
        "category": "urgent_payment_demands",
        "language": "Teluglish",
        "provenance": "public_advisory_case_pattern (APEPDCL Power Threat)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Current office nunchi calling saar. Eeroju night current cut untundi bill kattakapothe.\n"
            "Senior: Ela kattali babu?\n"
            "Caller: Ippude gpay cheyyandi rupees 500, lekapothe 10 nimishallo power cutoff chesthamu."
        )
    },

    # =========================================================================
    # CATEGORY 4: REMOTE ACCESS SCAMS (10 SAMPLES)
    # Ground Truth: SCAM | Expected Decision: BLOCK | Expected Level: HIGH_RISK
    # =========================================================================
    {
        "id": "unfam_remote_001_en",
        "category": "remote_access_scams",
        "language": "English",
        "provenance": "public_advisory_case_pattern (AnyDesk Screen Sharing Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Customer care officer from State Bank of India IT support desk.\n"
            "Senior: Hello, I had trouble with my mobile banking app earlier.\n"
            "Caller: Exactly, your server connection is corrupt. Install the AnyDesk app right now from Play Store.\n"
            "Senior: Okay, I see it downloading.\n"
            "Caller: Once installed, open it and share your screen so our executive can resolve your banking error."
        )
    },
    {
        "id": "unfam_remote_002_en",
        "category": "remote_access_scams",
        "language": "English",
        "provenance": "public_advisory_case_pattern (QuickSupport APK Phishing)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Calling from telecom department network support.\n"
            "Senior: Yes?\n"
            "Caller: 5G network towers require manual SIM profile setup. Download the QuickSupport app immediately from the SMS link sent to your phone."
        )
    },
    {
        "id": "unfam_remote_003_hi",
        "category": "remote_access_scams",
        "language": "Hindi",
        "provenance": "public_advisory_case_pattern (Screen Share Banking Takeover)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: बैंक अधिकारी बात कर रहा हूँ कस्टमर सपोर्ट से। आपके खाते में तकनीकी खराबी आ गई है।\n"
            "Senior: क्या खराबी आई है?\n"
            "Caller: इसे ठीक करने के लिए एनीडेस्क डाउनलोड कीजिए और स्क्रीन शेयर करें तुरंत।"
        )
    },
    {
        "id": "unfam_remote_004_hinglish",
        "category": "remote_access_scams",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish APK Link Fraud)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: HDFC Bank technical division se baat kar raha hoon.\n"
            "Senior: Haan boliye?\n"
            "Caller: Sir aapka account blocked ho jayega. Download the apk from the sms link turant kijiye."
        )
    },
    {
        "id": "unfam_remote_005_te",
        "category": "remote_access_scams",
        "language": "Telugu",
        "provenance": "public_advisory_case_pattern (Telugu Remote Tool Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: బ్యాంక్ మేనేజర్ ని మాట్లాడుతున్నాను. మీ మొబైల్ బ్యాంకింగ్ పని చేయడం లేదు కదా.\n"
            "Senior: అవును బాబు, లాగిన్ అవ్వడం లేదు.\n"
            "Caller: క్విక్ సపోర్ట్ డౌన్లోడ్ చేయండి వెంటనే, స్క్రీన్ షేర్ చేసి సర్వీస్ యాక్టివేట్ చేస్తాం."
        )
    },
    {
        "id": "unfam_remote_006_teluglish",
        "category": "remote_access_scams",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Teluglish TeamViewer Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: SBI tech team nunchi call amma. Me account security check cheyyali.\n"
            "Senior: Nenu em cheyali babu?\n"
            "Caller: QuickSupport app install cheyyandi, screen share karo so memu check chesthamu."
        )
    },
    {
        "id": "unfam_remote_007_en",
        "category": "remote_access_scams",
        "language": "English",
        "provenance": "public_advisory_case_pattern (Power Discom APK Link)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: From Electricity Board meter maintenance wing.\n"
            "Senior: Yes?\n"
            "Caller: Smart meter update pending. Download the apk software from sms link and allow remote support access within 10 minutes to avoid power cut."
        )
    },
    {
        "id": "unfam_remote_008_hinglish",
        "category": "remote_access_scams",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish RustDesk Takeover)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Main bank officer bol raha hoon branch se.\n"
            "Senior: Ji boliye.\n"
            "Caller: Sir branch aane ki zaroorat nahi hai. Install AnyDesk app on your phone abhi aur 9 digit code batao."
        )
    },
    {
        "id": "unfam_remote_009_te",
        "category": "remote_access_scams",
        "language": "Telugu",
        "provenance": "public_advisory_case_pattern (Remote Software Download)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: రిజర్వ్ బ్యాంక్ ఐటీ డిపార్ట్మెంట్ నుంచి కాల్.\n"
            "Senior: ఏమిటండీ?\n"
            "Caller: మీ ఫోన్ హ్యాక్ అయింది. ఎనీడెస్క్ ఇన్స్టాల్ చేసి మీ ఫోన్ ను క్లీన్ చేసుకోవాలి త్వరగా."
        )
    },
    {
        "id": "unfam_remote_010_teluglish",
        "category": "remote_access_scams",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Teluglish SMS Link Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Telecom TRAI verification officer saar. Me sim card block aypothundi.\n"
            "Senior: Enti saar, eppudu?\n"
            "Caller: Aaj raat sim card block. Install this link nunchi app download cheyandi ventane."
        )
    },

    # =========================================================================
    # CATEGORY 5: LEGITIMATE BANKING AND SECURITY ADVICE (10 SAMPLES)
    # Ground Truth: SAFE | Expected Decision: ALLOW | Expected Level: LOW_RISK
    # =========================================================================
    {
        "id": "unfam_legit_bank_001_en",
        "category": "legitimate_banking_advice",
        "language": "English",
        "provenance": "synthetic_stress_test (Legitimate Branch Passbook Service)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Good morning Mr. Nambiar, this is State Bank of India customer service.\n"
            "Senior: Hello, yes?\n"
            "Caller: We noticed your quarterly interest certificate is ready. Whenever you visit your bank branch in person at your convenience, you can collect it from the counter.\n"
            "Senior: Thank you, I will drop by next week."
        )
    },
    {
        "id": "unfam_legit_bank_002_en",
        "category": "legitimate_banking_advice",
        "language": "English",
        "provenance": "public_advisory_case_pattern (Legitimate Bank Security Call)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Hello Mrs. Gupta, I am calling from ICICI Bank branch office.\n"
            "Senior: Yes, is this about my locker renewal?\n"
            "Caller: Yes madam. Please note our bank never asks for your OTP or password. Please visit our branch in person with your locker key at your convenience."
        )
    },
    {
        "id": "unfam_legit_bank_003_hi",
        "category": "legitimate_banking_advice",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Hindi Official Branch Visit)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: नमस्ते वर्मा जी, मैं एसबीआई शाखा से बोल रहा हूँ।\n"
            "Senior: हाँ बेटा, कोई काम था?\n"
            "Caller: जी आपकी पासबुक पूरी भर गई है। जब भी आपको समय मिले, आराम से शाखा में आएं और नई पासबुक ले लें। कोई जल्दी नहीं है।"
        )
    },
    {
        "id": "unfam_legit_bank_004_hinglish",
        "category": "legitimate_banking_advice",
        "language": "Hinglish",
        "provenance": "public_advisory_case_pattern (Hinglish Banking Safeguard)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Namaste auntyji, main HDFC Bank branch se bol raha hoon.\n"
            "Senior: Haan beta, sab theek hai na?\n"
            "Caller: Haanji bilkul. Sirf yaad dila rahe the ki bank kabhi otp nahi mangta. Aap aaram se branch aakar miliye agle hafte."
        )
    },
    {
        "id": "unfam_legit_bank_005_te",
        "category": "legitimate_banking_advice",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Telugu Branch Service Invitation)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: నమస్కారం రావు గారు, మేము ఆంధ్రా బ్యాంక్ శాఖ నుంచి మాట్లాడుతున్నాము.\n"
            "Senior: చెప్పండి బాబు, పెన్షన్ వచ్చిందా?\n"
            "Caller: అవునండి, పెన్షన్ జమ అయింది. మీకు తీరిక ఉన్నప్పుడు సౌకర్యవంతంగా రండి, శాఖకు రండి ఎప్పుడైనా."
        )
    },
    {
        "id": "unfam_legit_bank_006_teluglish",
        "category": "legitimate_banking_advice",
        "language": "Teluglish",
        "provenance": "public_advisory_case_pattern (Teluglish Legitimate Caution)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Namaskaram sir, SBI branch manager office nunchi call.\n"
            "Senior: Cheppandi sir.\n"
            "Caller: Bank eppudu otp adagadu phone lo. Branch ki randi next tuesday passbook update cheyadaniki."
        )
    },
    {
        "id": "unfam_legit_bank_007_en",
        "category": "legitimate_banking_advice",
        "language": "English",
        "provenance": "synthetic_stress_test (FD Renewal Information)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Hello Mr. Deshmukh, calling from Bank of Baroda.\n"
            "Senior: Yes, good afternoon.\n"
            "Caller: Your senior citizen fixed deposit is maturing next month. There is no need to hurry, visit our branch in person whenever you feel comfortable to renew."
        )
    },
    {
        "id": "unfam_legit_bank_008_hi",
        "category": "legitimate_banking_advice",
        "language": "Hindi",
        "provenance": "public_advisory_case_pattern (Official Counter Service)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: नमस्कार सर, पंजाब नेशनल बैंक से बोल रहे हैं।\n"
            "Senior: जी नमस्कार।\n"
            "Caller: बैंक कभी भी फोन पर पासवर्ड या पिन नहीं मांगता। आप अगले महीने शाखा में आएं और फॉर्म जमा कर दें।"
        )
    },
    {
        "id": "unfam_legit_bank_009_te",
        "category": "legitimate_banking_advice",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Telugu Safeguard Advisory)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: నమస్తే అండి, స్టేట్ బ్యాంక్ ఆఫ్ ఇండియా హెల్ప్ డెస్క్.\n"
            "Senior: చెప్పండి అమ్మా.\n"
            "Caller: బ్యాంకు ఎప్పుడూ ఓటీపీ అడగదు. మీకు సమయం ఉన్నప్పుడు ఆఫీసుకు రండి, ఫారం సైన్ చేయండి."
        )
    },
    {
        "id": "unfam_legit_bank_010_en",
        "category": "legitimate_banking_advice",
        "language": "English",
        "provenance": "synthetic_stress_test (Senior Health Card Advisory)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Good morning Mr. Nair, this is your Canara Bank home branch.\n"
            "Senior: Hello, what is this regarding?\n"
            "Caller: Your new ATM chip card has arrived at our official counter. Please visit our branch in person next week to collect it safely."
        )
    },

    # =========================================================================
    # CATEGORY 6: LEGITIMATE DIALOGUE WITH SENSITIVE KEYWORDS (15 SAMPLES)
    # Testing false-alarm resistance when words like police, OTP, payments appear
    # Ground Truth: SAFE | Expected Decision: ALLOW/INCONCLUSIVE | Expected Level: LOW/INSUFFICIENT
    # =========================================================================
    {
        "id": "unfam_sens_001_en",
        "category": "legitimate_sensitive_context",
        "language": "English",
        "provenance": "synthetic_stress_test (Senior Reports Lost Purse to Police)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Senior: Hello, is this the local police station helpdesk?\n"
            "Caller: Yes madam, Mayur Vihar police station. How can we help you today?\n"
            "Senior: I think I left my handbag in an auto rickshaw near the market with my glasses and pensioner ID.\n"
            "Caller: Please come to the desk at your convenience to note the complaint details."
        )
    },
    {
        "id": "unfam_sens_002_en",
        "category": "legitimate_sensitive_context",
        "language": "English",
        "provenance": "synthetic_stress_test (Hospital Billing Grace Period)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello Mrs. Chatterjee, calling from Apollo Hospital accounts desk regarding Mr. Chatterjee's discharge summary.\n"
            "Senior: Yes, I was checking the pharmacy bill.\n"
            "Caller: The insurance payment was settled. There is an outstanding balance of 840 rupees for medicines. You can settle it at the counter whenever you come for follow-up next Tuesday."
        )
    },
    {
        "id": "unfam_sens_003_en",
        "category": "legitimate_sensitive_context",
        "language": "English",
        "provenance": "synthetic_stress_test (Bank Advises Never Share OTP)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Hello Mr. Kapoor, this is SBI customer service.\n"
            "Senior: Yes? I received an SMS saying someone tried to login.\n"
            "Caller: Do not worry sir, our system automatically blocked that attempt. Remember, never share your OTP with anyone who calls. Please visit your branch in person if you wish to reset your net banking password."
        )
    },
    {
        "id": "unfam_sens_004_hi",
        "category": "legitimate_sensitive_context",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Society Maintenance Normal Bill Reminder)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: नमस्ते अंकल, मैं सोसाइटी ऑफिस से पवन बोल रहा हूँ।\n"
            "Senior: हाँ पवन, क्या बात है?\n"
            "Caller: इस महीने का मेंटेनेंस बिल 1,200 रुपये बकाया है। आप आराम से महीने की 20 तारीख तक ऑफिस काउंटर पर जमा करवा सकते हैं।"
        )
    },
    {
        "id": "unfam_sens_005_hinglish",
        "category": "legitimate_sensitive_context",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Electricity Normal Due Date)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello Sharmaji, bijli office se meter reading slip ke baare mein call hai.\n"
            "Senior: Haan kitna bill aaya is baar?\n"
            "Caller: 680 rupees ka bill bana hai sir. Due date 25 tarikh hai, aaram se online ya counter par pay kar dena."
        )
    },
    {
        "id": "unfam_sens_006_te",
        "category": "legitimate_sensitive_context",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Apartment Maintenance Telugu)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: నమస్తే అంకుల్, అపార్ట్మెంట్ సెక్రటరీ మాట్లాడుతున్నాను.\n"
            "Senior: చెప్పండి బాబు.\n"
            "Caller: లిఫ్ట్ రిపేర్ కోసం 500 రూపాయలు వేయాలి. వచ్చే వారం మీటింగ్ లో ఇవ్వండి, తొందరేమీ లేదు."
        )
    },
    {
        "id": "unfam_sens_007_en",
        "category": "legitimate_sensitive_context",
        "language": "English",
        "provenance": "synthetic_stress_test (Daughter Asking Senior About Online Payment)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hi Papa, it's Ananya. Did you receive the groceries I ordered for you?\n"
            "Senior: Yes beta, the delivery person just arrived.\n"
            "Caller: Okay great! I already completed the payment online, so you don't need to give any money at the door."
        )
    },
    {
        "id": "unfam_sens_008_hinglish",
        "category": "legitimate_sensitive_context",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Son Reminding Dad on Pension Date)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Papa pranam, main Rohit bol raha hoon.\n"
            "Senior: Jeete raho beta. Kaisi chal rahi hai naukri?\n"
            "Caller: Sab badhiya papa. Main pooch raha tha ki pension credit hui kya account mein? Agar nahi hui toh bank chalenge weekend par."
        )
    },
    {
        "id": "unfam_sens_009_en",
        "category": "legitimate_sensitive_context",
        "language": "English",
        "provenance": "synthetic_stress_test (Broadband Routine Service Bill)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello, Airtel broadband customer support calling.\n"
            "Senior: Yes, my wifi router was blinking red this morning.\n"
            "Caller: We did an exchange check on your fiber line, it is restored now. Your regular bill of 599 is generated with a due date of next fortnight."
        )
    },
    {
        "id": "unfam_sens_010_te",
        "category": "legitimate_sensitive_context",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Telugu Grandson Call)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: తాతయ్య, నేను సురేష్ ని మాట్లాడుతున్నాను.\n"
            "Senior: ఎలా ఉన్నావురా మనవడా?\n"
            "Caller: బాగున్నాను తాతయ్య. మీ కంటి ఆస్పత్రి బిల్లు నేను కట్టేశాను, మీరు రెస్ట్ తీసుకోండి."
        )
    },
    {
        "id": "unfam_sens_011_teluglish",
        "category": "legitimate_sensitive_context",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Teluglish Grocery Delivery Confirmation)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Amma, BigBasket delivery boy call chesthunnadu gate daggara nunchi.\n"
            "Senior: Haan gate open lo undi babu.\n"
            "Caller: Sare amma, parcels anni door daggara peduthunnanu."
        )
    },
    {
        "id": "unfam_sens_012_en",
        "category": "legitimate_sensitive_context",
        "language": "English",
        "provenance": "synthetic_stress_test (Tax Consultant Routine Followup)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Good evening Mr. Joshi, this is Mehta from tax consultancy.\n"
            "Senior: Hello Mehta ji, is my pension tax return processed?\n"
            "Caller: Yes sir, your refund is approved by the income tax department. I will drop the assessment papers at your home tomorrow."
        )
    },
    {
        "id": "unfam_sens_013_hi",
        "category": "legitimate_sensitive_context",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Hindi Medical Prescription Delivery)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: नमस्ते आंटीजी, अपोलो फार्मेसी से दवाइयों का पैकेट लेकर आया हूँ।\n"
            "Senior: हाँ बेटा, बिल कितने का बना?\n"
            "Caller: आंटी डॉक्टर का पर्चा देखकर 420 रुपये का बिल है, कैश दे दीजिए।"
        )
    },
    {
        "id": "unfam_sens_014_hinglish",
        "category": "legitimate_sensitive_context",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish Driver Salary Discussion)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Namaste sahab, main driver Ramesh bol raha hoon.\n"
            "Senior: Haan Ramesh, kal subah 9 baje gaadi nikaalna hai.\n"
            "Caller: Theek hai sahab. Aur mahine ki salary jab aap aaram se ghar aao tab de dena."
        )
    },
    {
        "id": "unfam_sens_015_en",
        "category": "legitimate_sensitive_context",
        "language": "English",
        "provenance": "synthetic_stress_test (Bank Official Clarifies Security Safeguard)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Good afternoon, this is State Bank of India customer service.\n"
            "Senior: I had a question about phone security.\n"
            "Caller: Please remember sir, our bank never asks for your OTP or UPI PIN under any circumstance. Always come to our branch in person if you need assistance."
        )
    },

    # =========================================================================
    # CATEGORY 7: ORDINARY COURIER AND DELIVERY CONVERSATIONS (10 SAMPLES)
    # Ground Truth: SAFE | Expected Decision: INCONCLUSIVE | Expected Level: INSUFFICIENT
    # =========================================================================
    {
        "id": "unfam_cour_001_en",
        "category": "ordinary_courier_delivery",
        "language": "English",
        "provenance": "synthetic_stress_test (Courier Direction Check)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello sir, I am Blue Dart courier executive standing near lane number 4.\n"
            "Senior: Yes, which building are you looking for?\n"
            "Caller: House number 42B. Is it next to the yellow water tank?\n"
            "Senior: Yes, walk fifty meters straight, my gate is right on the corner."
        )
    },
    {
        "id": "unfam_cour_002_en",
        "category": "ordinary_courier_delivery",
        "language": "English",
        "provenance": "synthetic_stress_test (Amazon Delivery Arrival)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello ma'am, Amazon delivery. I have a package containing books for Mr. Rakesh.\n"
            "Senior: Rakesh is my son, he is at his office right now.\n"
            "Caller: Can you take delivery on his behalf, ma'am?\n"
            "Senior: Yes, I am coming down to the security gate."
        )
    },
    {
        "id": "unfam_cour_003_hi",
        "category": "ordinary_courier_delivery",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Hindi Courier Landmark Check)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: भैया, मैं फ्लिपकार्ट से पार्सल लेकर आया हूँ। आपका घर मंदिर के पीछे है क्या?\n"
            "Senior: हाँ बेटा, शिव मंदिर के पीछे वाली गली में तीसरा मकान।\n"
            "Caller: ठीक है अंकल, मैं दो मिनट में बेल बजाता हूँ।"
        )
    },
    {
        "id": "unfam_cour_004_hinglish",
        "category": "ordinary_courier_delivery",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish Delivery Reschedule)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello sir, DTDC courier delivery se bol raha hoon.\n"
            "Senior: Haan bhaiya, parcel kab aayega?\n"
            "Caller: Sir aaj baarish bohot zyada hai, kal subah 11 baje deliver kar doon chalega?\n"
            "Senior: Haan bilkul, kal bhej dena."
        )
    },
    {
        "id": "unfam_cour_005_te",
        "category": "ordinary_courier_delivery",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Telugu Swiggy Grocery Delivery)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: నమస్తే సార్, స్విగ్గీ ఇన్స్టామార్ట్ డెలివరీ అండి. మీ అపార్ట్మెంట్ సెక్యూరిటీ దగ్గర ఉన్నాను.\n"
            "Senior: సరే బాబు, లిఫ్ట్ లో థర్డ్ ఫ్లోర్ కి రా.\n"
            "Caller: అలాగే సార్, వస్తున్నాను."
        )
    },
    {
        "id": "unfam_cour_006_teluglish",
        "category": "ordinary_courier_delivery",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Teluglish Landmark Clarification)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello saar, Amazon parcel delivery. Me address dorakadam ledu.\n"
            "Senior: Gandhi bomma daggara unna road lo straight ga ra babu.\n"
            "Caller: Sare saar, 5 minutes lo akkada untanu."
        )
    },
    {
        "id": "unfam_cour_007_en",
        "category": "ordinary_courier_delivery",
        "language": "English",
        "provenance": "synthetic_stress_test (Delivery Gate Code)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello, Delhivery logistics here. Security is asking for visitor entry pass.\n"
            "Senior: I have notified them through MyGate app, please show your phone.\n"
            "Caller: Thank you sir, they let me through now."
        )
    },
    {
        "id": "unfam_cour_008_hi",
        "category": "ordinary_courier_delivery",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Medicine Courier Delivery)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: नमस्ते आंटीजी, 1mg से पार्सल है आपकी बीपी की दवाइयों का।\n"
            "Senior: बेटा मैं पहली मंजिल पर रहती हूँ, ऊपर आ जाओगे?\n"
            "Caller: जी आंटीजी, सीढ़ियों से ऊपर आ रहा हूँ।"
        )
    },
    {
        "id": "unfam_cour_009_te",
        "category": "ordinary_courier_delivery",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Postal Registered Letter)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: పోస్ట్ మ్యాన్ ని అండి. మీకు రిజిస్టర్ పోస్ట్ ఉత్తరం వచ్చింది.\n"
            "Senior: ఎక్కడి నుంచి వచ్చిందండి ఉత్తరం?\n"
            "Caller: ఎల్ఐసి ఆఫీస్ నుంచి వచ్చింది సార్, సైన్ చేయండి."
        )
    },
    {
        "id": "unfam_cour_010_en",
        "category": "ordinary_courier_delivery",
        "language": "English",
        "provenance": "synthetic_stress_test (Package Handover to Neighbor)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello Mr. Fernandez, courier boy calling. Nobody is opening flat 302.\n"
            "Senior: Oh, I went for a brief morning walk. Could you hand it to Mr. Sharma next door in flat 301?\n"
            "Caller: Sure sir, he signed for it."
        )
    },

    # =========================================================================
    # CATEGORY 8: LEGITIMATE GOVERNMENT SERVICE INTERACTIONS (10 SAMPLES)
    # Ground Truth: SAFE | Expected Decision: ALLOW/INCONCLUSIVE | Expected Level: LOW/INSUFFICIENT
    # =========================================================================
    {
        "id": "unfam_govt_001_en",
        "category": "legitimate_govt_services",
        "language": "English",
        "provenance": "synthetic_stress_test (Municipal Property Tax Receipt Notice)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Good morning, this is the municipal corporation citizen desk.\n"
            "Senior: Hello, yes?\n"
            "Caller: We are verifying property tax assessments for ward 12. Your annual receipt has been generated. You may download it from the citizen portal whenever you wish.\n"
            "Senior: Thank you, my daughter helps me with the online downloads."
        )
    },
    {
        "id": "unfam_govt_002_en",
        "category": "legitimate_govt_services",
        "language": "English",
        "provenance": "synthetic_stress_test (Post Office Senior Camp)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: Hello Mr. Pillai, calling from Head Post Office pension cell.\n"
            "Senior: Good morning sir.\n"
            "Caller: We are setting up a special Jeevan Pramaan digital life certificate camp at the community center this Saturday. Come to our office station at your convenience if you wish to update your biometric record."
        )
    },
    {
        "id": "unfam_govt_003_hi",
        "category": "legitimate_govt_services",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Voter ID Revision Camp Hindi)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: नमस्कार, निर्वाचन आयोग के बूथ लेवल ऑफिसर (BLO) बोल रहे हैं।\n"
            "Senior: जी नमस्कार, कोई लिस्ट आई है क्या?\n"
            "Caller: जी मतदाता सूची में नाम जांच के लिए प्राथमिक विद्यालय में शिविर लगा है। आप रविवार को आकर अपना नाम देख सकते हैं।"
        )
    },
    {
        "id": "unfam_govt_004_hinglish",
        "category": "legitimate_govt_services",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Health Center Vaccine Camp)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Primary health centre se ASHA worker Sunita bol rahi hoon.\n"
            "Senior: Haan Sunita, sab theek hai?\n"
            "Caller: Ji dadi, seniors ke liye free booster dose lag raha hai dispensary mein agle somwar ko. Aaram se aana subah 10 baje."
        )
    },
    {
        "id": "unfam_govt_005_te",
        "category": "legitimate_govt_services",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Village Secretariat Pension Camp)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: గ్రామ సచివాలయం నుంచి వాలంటీర్ ని మాట్లాడుతున్నాను.\n"
            "Senior: చెప్పమ్మా, పెన్షన్ ఎప్పుడు ఇస్తారు?\n"
            "Caller: ఒకటవ తేదీన ఉదయాన్నే ఇంటికి వచ్చి ఇస్తాము తాతయ్య. మీరు ఆఫీసుకు రండి లేదా ఇంట్లోనే ఉండండి, సౌకర్యవంతంగా రండి."
        )
    },
    {
        "id": "unfam_govt_006_teluglish",
        "category": "legitimate_govt_services",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Ration Card Update Camp)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Ward secretariat nunchi call amma. Ration card e-kyc camp undi.\n"
            "Senior: Ekkada camp petteru babu?\n"
            "Caller: Ward office lo petteru amma, next week eppudaina velli biometric ivvandi."
        )
    },
    {
        "id": "unfam_govt_007_en",
        "category": "legitimate_govt_services",
        "language": "English",
        "provenance": "synthetic_stress_test (Ayushman Bharat Senior Card Camp)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Calling from Taluk government hospital administration.\n"
            "Senior: Yes, please go ahead.\n"
            "Caller: Senior citizens above 70 are eligible for the expanded Ayushman Vay Vandana card. Registration counters are open at the taluk office every weekday."
        )
    },
    {
        "id": "unfam_govt_008_hi",
        "category": "legitimate_govt_services",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Jal Board Water Pipeline Inspection)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: जल बोर्ड लाइनमैन बोल रहा हूँ। आपके इलाके में नई पाइपलाइन का काम पूरा हो गया है।\n"
            "Senior: बहुत बढ़िया, पानी का प्रेशर ठीक आएगा अब?\n"
            "Caller: जी अंकल, कल सुबह टेस्ट पानी आएगा, जांच कर लीजिएगा।"
        )
    },
    {
        "id": "unfam_govt_009_te",
        "category": "legitimate_govt_services",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Telugu Municipal Tax Receipt)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: మునిసిపల్ కార్పొరేషన్ నుంచి మాట్లాడుతున్నాము.\n"
            "Senior: చెప్పండి సర్.\n"
            "Caller: మీ ఇంటి నంబర్ పై అసెస్మెంట్ అప్డేట్ అయింది. రసీదు వార్డ్ ఆఫీస్ లో తీసుకోవచ్చు."
        )
    },
    {
        "id": "unfam_govt_010_en",
        "category": "legitimate_govt_services",
        "language": "English",
        "provenance": "synthetic_stress_test (Election Polling Location Check)",
        "ground_truth": "SAFE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Good morning, this is the election returning officer's helpline.\n"
            "Senior: Hello, I wanted to confirm wheelchair facilities for voting.\n"
            "Caller: Yes sir, polling station 84 at Model High School has a ground-floor ramp and volunteers for senior citizens."
        )
    },

    # =========================================================================
    # CATEGORY 9: AMBIGUOUS CONVERSATIONS & BRIEF DIALOGUE (10 SAMPLES)
    # Ground Truth: INSUFFICIENT_EVIDENCE | Expected Decision: INCONCLUSIVE
    # =========================================================================
    {
        "id": "unfam_ambi_001_en",
        "category": "ambiguous_conversations",
        "language": "English",
        "provenance": "synthetic_stress_test (Wrong Number Interaction)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello, can I speak to Dr. Kulkarni?\n"
            "Senior: No, this is not Dr. Kulkarni's clinic. You have the wrong number.\n"
            "Caller: Oh, I apologize for disturbing you. Good day."
        )
    },
    {
        "id": "unfam_ambi_002_en",
        "category": "ambiguous_conversations",
        "language": "English",
        "provenance": "synthetic_stress_test (Real Estate Cold Pitch)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Good afternoon sir, are you interested in investment plots near the airport?\n"
            "Senior: No, I am an eighty year old pensioner, I have no interest in plots.\n"
            "Caller: Thank you for your time sir."
        )
    },
    {
        "id": "unfam_ambi_003_hi",
        "category": "ambiguous_conversations",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Hindi Network Audio Check)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: हैलो? आवाज़ आ रही है मेरी?\n"
            "Senior: हाँ बेटा, आवाज़ थोड़ी कट रही है। कौन बोल रहे हो?\n"
            "Caller: मैं बाद में कॉल करता हूँ, सिग्नल कमज़ोर है।"
        )
    },
    {
        "id": "unfam_ambi_004_hinglish",
        "category": "ambiguous_conversations",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Hinglish Telemarketing Credit Card Pitch)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello sir, lifetime free credit card offer available for you.\n"
            "Senior: Mujhe koi naya card nahi chahiye beta, phone rakho.\n"
            "Caller: Okay sir, thank you."
        )
    },
    {
        "id": "unfam_ambi_005_te",
        "category": "ambiguous_conversations",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Telugu Wrong Number Dialogue)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: హలో, శ్రీనివాస్ ఉన్నారా అండి?\n"
            "Senior: లేదు బాబు, రాంగ్ నెంబర్.\n"
            "Caller: సారీ అండి."
        )
    },
    {
        "id": "unfam_ambi_006_teluglish",
        "category": "ambiguous_conversations",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Teluglish Short Inquiry)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello saar, me car sell chesthara?\n"
            "Senior: Na daggara car ledu babu.\n"
            "Caller: Okay saar, thank you."
        )
    },
    {
        "id": "unfam_ambi_007_en",
        "category": "ambiguous_conversations",
        "language": "English",
        "provenance": "synthetic_stress_test (Brief Acoustic Echo)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello? Can you hear me clearly?\n"
            "Senior: Yes, who is speaking?\n"
            "Caller: Sorry, wrong connection."
        )
    },
    {
        "id": "unfam_ambi_008_hi",
        "category": "ambiguous_conversations",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Hindi Insurance Renewal Inquiry)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: नमस्कार सर, क्या आप कार बीमा रिन्यू करवाना चाहते हैं?\n"
            "Senior: मेरी गाड़ी का बीमा पहले से ही हो चुका है।\n"
            "Caller: ठीक है सर, धन्यवाद।"
        )
    },
    {
        "id": "unfam_ambi_009_te",
        "category": "ambiguous_conversations",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Telugu Silent Call)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: హలో... హలో...\n"
            "Senior: ఎవరు మాట్లాడుతున్నారు?\n"
            "Caller: ..."
        )
    },
    {
        "id": "unfam_ambi_010_en",
        "category": "ambiguous_conversations",
        "language": "English",
        "provenance": "synthetic_stress_test (Survey Agency Brief Call)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Good morning, we are conducting a quick 2-minute radio listenership survey in your area.\n"
            "Senior: I am busy reading my newspaper, please do not call back.\n"
            "Caller: Understood sir, removing your number."
        )
    },

    # =========================================================================
    # CATEGORY 10: INCOMPLETE OR NOISY ASR TRANSCRIPTS (11 SAMPLES)
    # Mixed ground truth: test robustness under realistic speech recognition corruptions
    # =========================================================================
    {
        "id": "unfam_noisy_001_en",
        "category": "incomplete_noisy_transcripts",
        "language": "English",
        "provenance": "synthetic_stress_test (Noisy ASR Scam with Misrecognized Tokens)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Calling from Central Bureau of Investigation cyber cell.\n"
            "Senior: Yes what happened?\n"
            "Caller: Arrest warrant issued contraband narcotics parcel seized. Transfer money to rbi safety account within 10 minutes."
        )
    },
    {
        "id": "unfam_noisy_002_en",
        "category": "incomplete_noisy_transcripts",
        "language": "English",
        "provenance": "synthetic_stress_test (Truncated Audio Fragment)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello good... morning sir... can you...\n"
            "Senior: Hello? Speak loudly please...\n"
            "Caller: Yes sir... regarding..."
        )
    },
    {
        "id": "unfam_noisy_003_hi",
        "category": "incomplete_noisy_transcripts",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Noisy Hindi Scam)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: बैंक अधिकारी बोल रहा हूँ। आपका खाता तुरंत बंद होगा।\n"
            "Senior: क्या?\n"
            "Caller: 10 मिनट में ओटीपी बताइए जल्दी।"
        )
    },
    {
        "id": "unfam_noisy_004_hinglish",
        "category": "incomplete_noisy_transcripts",
        "language": "Hinglish",
        "provenance": "synthetic_stress_test (Phonetic Corruption ASR)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: Discom bijli vibhag current bill cut aaj raat 8 baje.\n"
            "Senior: Kya cut hoga?\n"
            "Caller: Power cut hoga abhi nahi kiya toh. Paytm right now turant kijiye."
        )
    },
    {
        "id": "unfam_noisy_005_te",
        "category": "incomplete_noisy_transcripts",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Noisy Telugu Digital Arrest Fragment)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: సైబర్ క్రైమ్ పోలీస్ స్టేషన్... డిజిటల్ అరెస్ట్.\n"
            "Senior: బాబోయ్...\n"
            "Caller: ఫోన్ పెట్టొద్దు, పోలీసులు వస్తున్నారు."
        )
    },
    {
        "id": "unfam_noisy_006_teluglish",
        "category": "incomplete_noisy_transcripts",
        "language": "Teluglish",
        "provenance": "synthetic_stress_test (Fragmented Teluglish App Download)",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: QuickSupport app download cheyyandi saar.\n"
            "Senior: Enti app ah?\n"
            "Caller: Screen share karo lekapothe account block."
        )
    },
    {
        "id": "unfam_noisy_007_en",
        "category": "incomplete_noisy_transcripts",
        "language": "English",
        "provenance": "synthetic_stress_test (Garbled Safe Dialogue)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: ...truck arriving... lane four...\n"
            "Senior: Yes near the shop...\n"
            "Caller: ...okay..."
        )
    },
    {
        "id": "unfam_noisy_008_hi",
        "category": "incomplete_noisy_transcripts",
        "language": "Hindi",
        "provenance": "synthetic_stress_test (Garbled Hindi Innocent Call)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: हाँ भैया... दूध का पैकेट...\n"
            "Senior: रख दो बाहर..."
        )
    },
    {
        "id": "unfam_noisy_009_en",
        "category": "incomplete_noisy_transcripts",
        "language": "English",
        "provenance": "synthetic_stress_test (Phonetic OTP Corruption 'otpp')",
        "ground_truth": "SCAM",
        "expected_decision": "BLOCK",
        "expected_risk_level": "HIGH_RISK",
        "transcript": (
            "Caller: I am speaking from SBI bank head office.\n"
            "Senior: Yes?\n"
            "Caller: Account suspended today. Give the otpp code sent on mobile right now to unfreeze."
        )
    },
    {
        "id": "unfam_noisy_010_te",
        "category": "incomplete_noisy_transcripts",
        "language": "Telugu",
        "provenance": "synthetic_stress_test (Telugu Garbled Dialogue)",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "expected_decision": "INCONCLUSIVE",
        "expected_risk_level": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: ఆఫీస్... రేపు రండి...\n"
            "Senior: సరే..."
        )
    },
    {
        "id": "unfam_noisy_011_en",
        "category": "incomplete_noisy_transcripts",
        "language": "English",
        "provenance": "synthetic_stress_test (Background Noise with Legitimate Branch Mention)",
        "ground_truth": "SAFE",
        "expected_decision": "ALLOW",
        "expected_risk_level": "LOW_RISK",
        "transcript": (
            "Caller: State Bank of India customer verification... visit our branch in person next week at your convenience."
        )
    }
]
