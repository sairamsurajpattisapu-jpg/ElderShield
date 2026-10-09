"""
ElderShield — Independent Holdout Evaluation Dataset (HWV4-PS05)
Size: N=30 Distinct Scenarios
Role: Untouched Holdout Evaluation Set for Generalization & False-Alarm Testing
Design Principles:
  1. Genuinely distinct phrasing and conversational structures from previous benchmarks.
  2. Hard Negatives: Legitimate hospital emergencies, family calls, bank fraud warning
     calls that explicitly caution against OTP sharing, government subsidy notices,
     courier deliveries, and municipal utility announcements.
  3. Hard Positives: Novel scam scripts covering customs contraband, pension treasury
     suspension, telecom SIM cutoff, remote AnyDesk solicitation, overcharge refunds,
     Aadhaar biometric locking, High Court summons, and eSIM swap extraction.
  4. Multi-language: English, Hindi, Telugu, Hinglish, and Teluglish.
"""

from typing import List, Dict, Any

HOLDOUT_EVALUATION_DATASET: List[Dict[str, Any]] = [
    # -------------------------------------------------------------------------
    # HARD NEGATIVES: Legitimate Urgent Hospital, Family, Banking Safeguards (10)
    # -------------------------------------------------------------------------
    {
        "id": "holdout_legit_hospital_001_en",
        "category": "legitimate_hospital_urgency",
        "language": "English",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Dr. Sen calling from Apollo emergency room. Your brother was admitted after a road accident. "
            "Please come to the casualty ward immediately to sign the medical consent form. "
            "Senior: Oh no! Is he conscious? Do I need to pay anything right now? "
            "Caller: He is stabilized. No payment is required right now, just bring his identification and insurance card."
        )
    },
    {
        "id": "holdout_legit_hospital_002_hi",
        "category": "legitimate_hospital_urgency",
        "language": "Hindi",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Namaste, main City Hospital se Dr. Verma bol raha hoon. Aapke pitaji ki surgery theek rahi. "
            "Senior: Doctor sahab, unka hosh aa gaya kya? "
            "Caller: Ji bilkul, unhe room mein shift kar rahe hain. Kal subah discharge paperwork ke liye hospital billing counter par aaiye."
        )
    },
    {
        "id": "holdout_legit_family_001_en",
        "category": "legitimate_family_emergency",
        "language": "English",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Hi Dadu, this is Priya. My phone battery completely died so I borrowed my classmate's phone to call you. "
            "Senior: Priya beti, where are you right now? Everything okay? "
            "Caller: Yes, I am at college library. Can you ask mom to call me on this number when she gets home? I will be back by 6 PM."
        )
    },
    {
        "id": "holdout_legit_bank_otp_warning_001_en",
        "category": "legitimate_banking_safeguard",
        "language": "English",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Good morning Mrs. Kapoor, this is HDFC Card Fraud Monitoring Desk. "
            "We detected an unusual international transaction attempt of 14,000 rupees on your debit card. "
            "We have proactively blocked the card for your security. "
            "Please remember: our bank will never ask for your OTP or CVV over the phone. Never disclose verification codes to anyone. "
            "Senior: Thank you for alerting me. Should I visit the branch? "
            "Caller: Yes, please visit your home branch at your convenience to collect a reissued card."
        )
    },
    {
        "id": "holdout_legit_payment_reminder_001_te",
        "category": "legitimate_routine_reminder",
        "language": "Telugu",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Namaskaram Shastri garu, apartment welfare association nunchi secretary matladuthunnanu. "
            "Senior: Namaskaram, cheppandi. "
            "Caller: Ee nela maintenance bill notice board meeda pettamu. Next week Sunday general body meeting lo check ivvandi."
        )
    },
    {
        "id": "holdout_legit_govt_subsidy_001_hinglish",
        "category": "legitimate_govt_services",
        "language": "Hinglish",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Namaste Rao sahab, Krishi Bhavan agriculture department se patra mila tha aapka subsidy application ke liye. "
            "Senior: Ji sir, verification kab hoga? "
            "Caller: Documents verify karne ke liye Tehsil office mein aaiye Monday subah 11 baje. Koi online fees nahi lagegi."
        )
    },
    {
        "id": "holdout_legit_school_urgent_001_en",
        "category": "legitimate_school_urgent",
        "language": "English",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Mrs. Sharma, this is Principal D'Souza from Saint Mary's School. "
            "Your grandson twisted his ankle during basketball practice. "
            "Senior: Oh dear! Is it severe? "
            "Caller: The school nurse applied an ice pack and he is comfortable. Please arrange to pick him up from the infirmary."
        )
    },
    {
        "id": "holdout_legit_courier_001_en",
        "category": "legitimate_courier",
        "language": "English",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Good afternoon sir, BlueDart courier delivery. I am downstairs with an Amazon parcel for flat 301. "
            "Senior: Yes, I am upstairs. "
            "Caller: Ringing your doorbell right now."
        )
    },
    {
        "id": "holdout_legit_water_board_001_en",
        "category": "legitimate_govt_services",
        "language": "English",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Municipal water supply notification for Sector 4 residents. "
            "Pipeline maintenance is scheduled tomorrow from 10 AM to 4 PM. Water pressure will be low. "
            "Please store adequate drinking water in advance."
        )
    },
    {
        "id": "holdout_legit_telecom_warning_001_hi",
        "category": "legitimate_advisory",
        "language": "Hindi",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Aapka telecom provider aapko savdhaan karta hai. "
            "Kripya dhyan dein: bank fraud se surakshit rahein. Apne NetBanking password ya OTP kisi ke saath phone par share na karein."
        )
    },

    # -------------------------------------------------------------------------
    # INCONCLUSIVE / AMBIGUOUS SCENARIOS (5)
    # -------------------------------------------------------------------------
    {
        "id": "holdout_ambi_interrupted_001_en",
        "category": "ambiguous_dialogue",
        "language": "English",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello... yes who is speaking? The signal is breaking up completely. "
            "Senior: I can barely hear you, can you call back on the landline?"
        )
    },
    {
        "id": "holdout_ambi_wrong_number_001_en",
        "category": "ambiguous_dialogue",
        "language": "English",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello, is this Gupta Textile Traders? "
            "Senior: No, this is a residential number. You dialed the wrong number. "
            "Caller: My apologies for disturbing you."
        )
    },
    {
        "id": "holdout_ambi_sales_pitch_001_en",
        "category": "ambiguous_dialogue",
        "language": "English",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Good afternoon sir, calling from Star Health insurance. We have a new senior citizen health policy covering daycare treatments. "
            "Senior: I already have medical coverage. "
            "Caller: Understood sir, thank you for your time."
        )
    },
    {
        "id": "holdout_ambi_garbled_hindi_001_hi",
        "category": "ambiguous_dialogue",
        "language": "Hindi",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Haanji namaste... kaun bol raha hai... aawaz theek se nahi aa rahi. "
            "Senior: Kisko phone lagaya aapne? "
            "Caller: Network kharab hai, baad mein baat karte hain."
        )
    },
    {
        "id": "holdout_ambi_restaurant_booking_001_teluglish",
        "category": "ambiguous_dialogue",
        "language": "Teluglish",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello sir, Paradise restaurant nunchi call chesthunnanu table reservation kosam. "
            "Senior: Yes, dinner booking. "
            "Caller: 4 members table reserved at 8 PM sir, thank you."
        )
    },

    # -------------------------------------------------------------------------
    # HARD POSITIVES: Novel Scam Scripts Across 5 Languages (15)
    # -------------------------------------------------------------------------
    {
        "id": "holdout_scam_customs_drugs_001_en",
        "category": "digital_arrest_contraband",
        "language": "English",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Customs Border Clearance Narcotics Directorate. An international cargo consignment registered under your Aadhaar was impounded with contraband narcotics. "
            "Senior: I haven't sent any consignment! "
            "Caller: A non-bailable arrest warrant has been issued against you. You are under digital arrest. "
            "Do not disconnect or inform family. Transfer 1,20,000 rupees security deposit to our government treasury account immediately for clearance."
        )
    },
    {
        "id": "holdout_scam_pension_treasury_002_en",
        "category": "pension_credential_theft",
        "language": "English",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Directorate of Treasuries and Accounts pension disbursement cell. Your monthly pension has been suspended due to life certificate mismatch. "
            "Senior: How do I restore my pension? "
            "Caller: It will be permanently frozen within two hours. Read out the 6 digit OTP you just received on your phone right now to verify."
        )
    },
    {
        "id": "holdout_scam_telecom_disconnect_003_hi",
        "category": "telecom_disconnection_coercion",
        "language": "Hindi",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Department of Telecommunications legal branch se call hai. Aapke naam par paanch illegal SIM cards chal rahe hain. "
            "Senior: Mere paas toh sirf ek phone hai! "
            "Caller: Agle do ghante mein aapke saare mobile number block ho jayenge. Agar disconnection rokna hai toh humare officer ko apna OTP bataiye turant."
        )
    },
    {
        "id": "holdout_scam_power_arrears_004_hinglish",
        "category": "utility_disconnection_demand",
        "language": "Hinglish",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Power discom electricity vigilance officer bol raha hoon. Aapka bijli meter connection aaj raat 8 baje cut kar diya jayega. "
            "Senior: Maine toh pura bill pay kiya hai! "
            "Caller: Server par overdue dikha raha hai. Immediate reconnection ke liye abhi 1450 rupees transfer kijiye gpay par, warna line kat jayegi."
        )
    },
    {
        "id": "holdout_scam_digital_arrest_teluglish_005_te",
        "category": "digital_arrest_extortion",
        "language": "Teluglish",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Idhi CBI cyber crime branch investigation officer Sharma. Mee bank account nunchi illegal money laundering jarigindi. "
            "Meeku digital arrest notice issue chesamu. Evariki cheppakandi, phone cut chesthe police van intiki vasthundi. "
            "Maa clearance account ki ventane 50,000 transfer cheyyandi."
        )
    },
    {
        "id": "holdout_scam_device_takeover_006_en",
        "category": "remote_access_malware",
        "language": "English",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Microsoft Technical Support desk. We detected severe malware infection on your home network leaking banking passwords. "
            "Senior: What should I do to fix it? "
            "Caller: Download and install AnyDesk or TeamViewer on your phone immediately so our engineer can take remote control of your screen and fix the virus."
        )
    },
    {
        "id": "holdout_scam_credit_card_points_007_en",
        "category": "card_credential_harvesting",
        "language": "English",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Credit Card Rewards Department. You have 38,000 reward points worth 19,000 rupees expiring tonight. "
            "Senior: Can I convert them to cash? "
            "Caller: Yes, to credit the funds to your account immediately, please state your 16 digit card number, expiry date, and the CVV on the back."
        )
    },
    {
        "id": "holdout_scam_courier_customs_teluglish_008_te",
        "category": "courier_customs_extortion",
        "language": "Teluglish",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: FedEx courier customer service. Mee peru meeda vachina international parcel lo MDMA drugs dorikayi, customs police case pettaru. "
            "Senior: Nenu emi order cheyyaledu sir! "
            "Caller: Arrest warrant cancel cheyyalante maa verification officer ki 75,000 fine gpay cheyyandi turant."
        )
    },
    {
        "id": "holdout_scam_aadhaar_biometric_lock_009_hi",
        "category": "aadhaar_credential_theft",
        "language": "Hindi",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: UIDAI head office verification department. Aapka Aadhaar card illegal activity mein link hua hai aur bank account freeze hone wala hai. "
            "Senior: Main kya karoon? "
            "Caller: Aapke mobile par verification OTP bheja hai, turant batayein warna abhi account permanently freeze kar diya jayega."
        )
    },
    {
        "id": "holdout_scam_fake_refund_010_en",
        "category": "overpayment_refund_scam",
        "language": "English",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Online shopping refund manager. We made an accidental refund error of 45,000 rupees instead of 4,500 rupees into your account. "
            "Senior: I did not check my balance yet. "
            "Caller: Our employee will be terminated unless you return the extra 40,500 rupees immediately via Google Pay or gift cards. Keep this confidential."
        )
    },
    {
        "id": "holdout_scam_sim_swap_011_en",
        "category": "sim_swap_takeover",
        "language": "English",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Telecom Cellular 5G Upgrade Desk. Your 4G network will be permanently stopped at 6 PM today. "
            "Senior: I need my phone working! "
            "Caller: To prevent cellular disconnection, forward your SIM upgrade request SMS to 121 and read out the confirmation code sent to you right now."
        )
    },
    {
        "id": "holdout_scam_epfo_withdrawal_012_hinglish",
        "category": "epfo_advance_fee",
        "language": "Hinglish",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: EPFO regional provident fund cell. Aapka PF pension claim 1,50,000 rupees sanction ho gaya hai. "
            "Senior: Bahut accha, kab aayega account mein? "
            "Caller: Release approval ke liye processing charge 2500 rupees abhi online transfer kijiye hamare account mein."
        )
    },
    {
        "id": "holdout_scam_legal_court_warrant_013_en",
        "category": "court_warrant_extortion",
        "language": "English",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: High Court Registry Notice Branch. Contempt of court and asset attachment proceedings have started against you. "
            "Senior: I haven't received any court notice! "
            "Caller: To stop police attachment of your property, deposit 65,000 rupees into judicial escrow account within 45 minutes."
        )
    },
    {
        "id": "holdout_scam_gas_subsidy_014_te",
        "category": "utility_disconnection_demand",
        "language": "Telugu",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Gas cylinder distribution authority. Mee LPG subsidy connection cancel cheyabaduthundi. "
            "Senior: Enduku cancel chesthunnaru? "
            "Caller: Ventane 500 rupees penalty phone pay cheyyandi, lekapothe gas supply aagipothundi."
        )
    },
    {
        "id": "holdout_scam_fake_charity_coercion_015_en",
        "category": "mandatory_payment_coercion",
        "language": "English",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: National Relief Fund Compliance Officer. Under emergency defense directive, mandatory contribution of 10,000 rupees is required today. "
            "Senior: Is this compulsory? "
            "Caller: Refusal will incur immediate tax audit penalties and bank freeze. Transfer the funds to our emergency UPI ID right now."
        )
    }
]
