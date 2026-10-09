"""
ElderShield — Adversarial Evaluation Dataset (N=32)
=====================================================
Role: Adversarial Multi-Turn Stress Test Suite (HWV4-PS05)
Provenance: Explicitly synthetic, development-controlled test suite.
Purpose:
  Tests detector resilience on previously unseen phrasing, indirect demands,
  multi-turn escalation, and hard false-alarm edge cases (ICU consent, family breakdown).

Dataset Composition:
  - 16 Hard Positives (Scams): Government/police, digital arrest, card CVV, eSIM swap,
    remote screen share, fake refund, power arrears, pension freeze, secrecy/isolation,
    multi-turn escalation, Teluglish digital arrest, Aadhaar OTP, tax audit attachment,
    LPG subsidy cancel, KBC fee, emergency trauma payment demand.
  - 10 Hard Negatives (Legitimate): ICU consent, surgery recovery, family car breakdown,
    bank fraud warning with OTP safeguard, routine branch FD, courier delivery,
    ration card e-KYC in person, school infirmary fever, water maintenance, doctor appointment.
  - 6 Ambiguous / Incomplete: Dropped audio, wrong number carpenter, cold credit card pitch,
    poor connection Teluglish, rental inquiry, garbled Hindi.

Language Representation: English, Hindi, Hinglish, Telugu, Teluglish.
"""

from typing import List, Dict, Any

ADVERSARIAL_EVALUATION_DATASET: List[Dict[str, Any]] = [
    # =========================================================================
    # PART 1: ADVERSARIAL SCAM SCENARIOS (16 SAMPLES)
    # Ground Truth: SCAM | Expected Decision: BLOCK | Expected Level: HIGH_RISK or SUSPICIOUS
    # =========================================================================
    {
        "id": "adv_scam_customs_fedex_001_en",
        "category": "government_police_impersonation",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Narcotics Control Bureau and International Postal Clearing Directorate. "
            "A foreign consignment registered with your passport number was seized with illicit contraband. "
            "Senior: I never ordered any foreign parcel! "
            "Caller: A non-bailable attachment summons has been issued by the Cyber Crime unit. "
            "To stop immediate police detention, transfer 85,000 rupees to our government verification account immediately."
        )
    },
    {
        "id": "adv_scam_digital_arrest_videocall_002_hi",
        "category": "digital_arrest_legal_threat",
        "language": "Hindi",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Supreme Court e-Committee aur cyber cell vigilance se Inspector Malhotra bol raha hoon. "
            "Aapke naam par hawala money laundering case registered hai. "
            "Senior: Maine koi galat kaam nahi kiya sahab! "
            "Caller: Aap under digital arrest hain. Agle 24 ghante tak phone mat kaatna aur kisi ko mat batana, "
            "warna police van turant ghar par aayegi."
        )
    },
    {
        "id": "adv_scam_card_harvest_cvv_003_en",
        "category": "credential_harvesting_card_cvv",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: National Banking Card Operations Desk. Your global debit card security chip expires today. "
            "Senior: Can I renew it at the local branch? "
            "Caller: Branch counters cannot process chip re-certification. To avoid account freeze within 15 minutes, "
            "please state your 16 digit card number and the CVV on the back right now."
        )
    },
    {
        "id": "adv_scam_esim_takeover_004_en",
        "category": "sim_swapping_account_takeover",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Department of Telecommunications 5G upgrade verification cell. "
            "Your 4G SIM card will be deactivated within 1 hour. "
            "Senior: I need to stay connected with my doctor! "
            "Caller: Forward the SIM upgrade request text to 121 and read out the confirmation code sent to your phone immediately."
        )
    },
    {
        "id": "adv_scam_remote_screen_coercion_005_hinglish",
        "category": "remote_access_screen_sharing",
        "language": "Hinglish",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Microsoft Technical Support department se baat kar raha hoon. Aapke home network par banking trojan virus mila hai. "
            "Senior: Abhi kya karna hoga? "
            "Caller: Turant phone par AnyDesk install karke humare technical engineer ko screen share kijiye taaki malware remove kiya ja sake."
        )
    },
    {
        "id": "adv_scam_fake_refund_overpayment_006_en",
        "category": "fake_refund_overpayment",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Retail Billing Refund Desk. We accidentally transferred 60,000 rupees instead of 6,000 rupees into your savings account. "
            "Senior: Let me check my bank passbook tomorrow. "
            "Caller: No, our junior accountant will face criminal prosecution tonight! Keep this strictly between us and return the excess 54,000 rupees via Google Pay right now."
        )
    },
    {
        "id": "adv_scam_electricity_arrears_007_te",
        "category": "urgent_payment_demand",
        "language": "Telugu",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Electricity board vigilance officer matladuthunnanu. Mee current bill overdue undi. "
            "Eeroju night 8 baje current cut aipothundi. "
            "Senior: Nenu bill pay chesanu kada saar! "
            "Caller: Server lo pending undi. Ventane 2,400 rupees penalty phone pay cheyyandi line kat kakunda undalante."
        )
    },
    {
        "id": "adv_scam_pension_suspension_008_hi",
        "category": "urgency_pension_coercion",
        "language": "Hindi",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: EPFO treasury office pension cell. Aapka jeevan pramaan patra reject ho gaya hai aur pension freeze ho chuka hai. "
            "Senior: Meri dawaiyon ka kharcha pension se hi chalta hai! "
            "Caller: Agar pension chalu rakhna hai toh abhi aane wala 6 digit OTP batao turant, aakhiri mauka hai."
        )
    },
    {
        "id": "adv_scam_secrecy_isolation_009_en",
        "category": "secrecy_isolation_coercion",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Central Bureau of Investigation economic offences division. "
            "Your savings account is implicated in cross-border money laundering. "
            "Senior: I am a retired school teacher, I have nothing to hide! "
            "Caller: You must stay in a closed room and do not tell your family or children. "
            "Transfer all your savings temporarily to our RBI verification escrow account."
        )
    },
    {
        "id": "adv_scam_multiturn_escalation_010_en",
        "category": "multi_turn_escalation",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Good morning Mr. Bose, State Bank of India security division calling regarding account maintenance. "
            "Senior: Yes, good morning. Is everything fine? "
            "Caller: We noticed three unauthorized transactions from overseas attempting to empty your deposit. "
            "Senior: Oh God! What should I do? "
            "Caller: To protect your balance, account is suspended today. Transfer the funds to our emergency clearing account right now."
        )
    },
    {
        "id": "adv_scam_teluglish_digital_arrest_011_teluglish",
        "category": "digital_arrest_legal_threat",
        "language": "Teluglish",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Cyber crime branch investigation officer Sharma. Mee bank account nunchi illegal transactions jarigayi. "
            "Meeku digital arrest order issue chesamu. "
            "Senior: Nenu emi cheyyaledu saar! "
            "Caller: Evariki cheppakandi, phone cut chesthe arrest chestharu. Ventane 50,000 transfer cheyyandi maa safety account ki."
        )
    },
    {
        "id": "adv_scam_aadhaar_biometric_unblock_012_hinglish",
        "category": "credential_harvesting_otp",
        "language": "Hinglish",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: UIDAI head office verification department se bol rahe hain. Aapka Aadhaar card illegal activity mein link hua hai. "
            "Senior: Yeh kaise ho sakta hai? "
            "Caller: Bank account freeze hone se pehle SMS mein aaya hua OTP batao turant, warna jail hogi."
        )
    },
    {
        "id": "adv_scam_tax_audit_attachment_013_en",
        "category": "urgent_payment_demand",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: High Court Registry tax enforcement division. Contempt of court and asset attachment proceedings have started against you. "
            "Senior: I never evaded any tax in my life! "
            "Caller: To stop police attachment of your residential property, deposit 65,000 rupees into judicial escrow account within 30 minutes."
        )
    },
    {
        "id": "adv_scam_gas_disconnection_014_te",
        "category": "urgent_payment_demand",
        "language": "Telugu",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: Gas distribution agency. Mee LPG subsidy connection cancel cheyabaduthundi. "
            "Senior: Enduku cancel chesthunnaru saar? "
            "Caller: Overdue penalty undi. Gas supply aagipothundi ippude phone pay cheyyandi penalty amount."
        )
    },
    {
        "id": "adv_scam_lottery_processing_fee_015_hi",
        "category": "urgent_payment_demand",
        "language": "Hindi",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: National Relief Fund compliance officer. Under emergency defense directive, mandatory contribution required today. "
            "Senior: Kya yeh zaroori hai? "
            "Caller: Refusal will incur immediate tax audit penalties. Transfer the funds to our emergency upi id right now."
        )
    },
    {
        "id": "adv_scam_epfo_processing_fee_016_hinglish",
        "category": "multi_turn_escalation",
        "language": "Hinglish",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SCAM",
        "transcript": (
            "Caller: EPFO regional provident fund cell se baat kar rahe hain. Aapka PF claim sanction ho gaya hai. "
            "Senior: Bahut badhiya sir! "
            "Caller: Release approval ke liye processing charge 2500 rupees abhi online transfer kijiye hamare account mein."
        )
    },

    # =========================================================================
    # PART 2: HARD NEGATIVES: LEGITIMATE URGENT CALLS (10 SAMPLES)
    # Ground Truth: SAFE | Expected Decision: ALLOW | Expected Level: LOW_RISK or INSUFFICIENT_EVIDENCE
    # =========================================================================
    {
        "id": "adv_legit_hospital_icu_consent_017_en",
        "category": "legitimate_hospital_urgency",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Dr. Mehta calling from Max Healthcare Intensive Care Unit. "
            "Your husband was brought in with severe cardiac discomfort. "
            "Please come to the hospital casualty desk in person right away to sign the medical consent documents. "
            "Senior: Doctor, do I need to pay or transfer money over the phone? "
            "Caller: No madam, absolutely no phone payments are allowed. Just bring his identity papers and meet us at the reception."
        )
    },
    {
        "id": "adv_legit_hospital_surgery_recovery_018_hi",
        "category": "legitimate_hospital_urgency",
        "language": "Hindi",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Namaste, main Fortis Hospital se Dr. Joshi bol raha hoon. Aapki mataji ka knee surgery bilkul theek raha. "
            "Senior: Doctor sahab, unka hosh kab aayega? "
            "Caller: Sham tak theek ho jayengi. Kal subah hospital aakar discharge formalities counter par puri kijiye. "
            "Kisi ko phone par koi fees nahi deni hai."
        )
    },
    {
        "id": "adv_legit_family_breakdown_019_en",
        "category": "legitimate_family_emergency",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Hi Grandpa, this is Rahul calling from my friend's phone because my battery died on the highway. "
            "Senior: Rahul! Are you safe? Where are you? "
            "Caller: Yes Grandpa, my car had a flat tire near the toll plaza. "
            "Can you tell Dad to bring the spare tire from the garage? I don't need any money, just let Dad know."
        )
    },
    {
        "id": "adv_legit_bank_fraud_alert_020_en",
        "category": "legitimate_banking_safeguard",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: State Bank of India Fraud Management Desk. We detected a suspicious overseas login attempt on your account. "
            "We have temporarily locked NetBanking for your protection. "
            "Please remember: bank officials never ask for your passwords, OTP, or PIN over phone calls. Never disclose codes. "
            "Senior: Thank you, what should I do? "
            "Caller: Please visit your home branch in person on Monday at your convenience to reset your credentials."
        )
    },
    {
        "id": "adv_legit_bank_routine_branch_021_hi",
        "category": "legitimate_banking_safeguard",
        "language": "Hindi",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Bank of Baroda se branch manager bol raha hoon. Aapki fixed deposit agle hafte mature ho rahi hai. "
            "Senior: Haan, mujhe pata hai manager sahab. "
            "Caller: Koi jaldi nahi hai, jab bhi aapko samay mile aaram se branch aakar renewal form sign kar lijiye."
        )
    },
    {
        "id": "adv_legit_courier_delivery_022_te",
        "category": "legitimate_courier_delivery",
        "language": "Telugu",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Namaskaram sir, Amazon courier delivery nunchi matladuthunnanu. Me parcel tisukoni flat mundu unnanu. "
            "Senior: Vachanu, door open chesthunnanu. "
            "Caller: Dhanyavadhalu sir, parcel andindi."
        )
    },
    {
        "id": "adv_legit_govt_ration_notice_023_hi",
        "category": "legitimate_govt_services",
        "language": "Hindi",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Civil supplies ration office se suchna. Senior citizen ration card renewal ke liye Tehsil office mein aaiye agle Somvaar. "
            "Senior: Kya koi online link kholni hai? "
            "Caller: Bilkul nahi, sirf physical counter par aakar documents submit kijiye, phone par koi jankari mat dena."
        )
    },
    {
        "id": "adv_legit_school_urgent_fever_024_en",
        "category": "legitimate_family_emergency",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Mrs. Bannerjee, this is Principal D'Souza from the school infirmary. "
            "Your granddaughter has developed a high fever during afternoon class. "
            "Senior: Oh no! Is an ambulance needed? "
            "Caller: She is resting safely in our medical room. Please arrange for an adult family member to pick her up from the front gate."
        )
    },
    {
        "id": "adv_legit_water_board_repair_025_en",
        "category": "legitimate_govt_services",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Municipal Water Supply Board maintenance bulletin for Sector 9. "
            "Main transmission pipeline repair will occur tomorrow between 9 AM and 3 PM. "
            "Please store drinking water in advance. Thank you for your cooperation."
        )
    },
    {
        "id": "adv_legit_doctor_appointment_026_te",
        "category": "legitimate_hospital_urgency",
        "language": "Telugu",
        "provenance": "synthetic_adversarial",
        "ground_truth": "SAFE",
        "transcript": (
            "Caller: Apollo Clinic nunchi receptionist matladuthunnanu. Shastri garu mee blood test reports vachayi. "
            "Senior: Doctor garu chusara? "
            "Caller: Doctor garu repu morning 10 AM ki consultation ki rammannaru clinic ki. Aaram ga randi."
        )
    },

    # =========================================================================
    # PART 3: AMBIGUOUS / INCOMPLETE CONVERSATIONS (6 SAMPLES)
    # Ground Truth: INSUFFICIENT_EVIDENCE | Expected Decision: INCONCLUSIVE | Expected Level: INSUFFICIENT_EVIDENCE
    # =========================================================================
    {
        "id": "adv_ambi_dropped_audio_027_en",
        "category": "ambiguous_interrupted_dialogue",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello... yes... can you hear me? The signal is breaking up completely... "
            "Senior: Hello? Who is speaking? I can only hear static on the line."
        )
    },
    {
        "id": "adv_ambi_wrong_number_carpenter_028_hi",
        "category": "ambiguous_interrupted_dialogue",
        "language": "Hindi",
        "provenance": "synthetic_adversarial",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Haanji Sharmaji, kal subah table aur cupboard ka kaam start karna hai kya? "
            "Senior: Bhaiyya galat number lagaya aapne, yeh residential number hai. "
            "Caller: Acha sorry sahab, maafi chahta hoon."
        )
    },
    {
        "id": "adv_ambi_cold_call_credit_card_029_en",
        "category": "ambiguous_interrupted_dialogue",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Good afternoon sir, calling from Standard Chartered Bank. We have a pre-approved platinum credit card offer with lounge access. "
            "Senior: I am not interested, please remove my name from telemarketing. "
            "Caller: Understood sir, have a good day."
        )
    },
    {
        "id": "adv_ambi_incomplete_teluglish_030_teluglish",
        "category": "ambiguous_interrupted_dialogue",
        "language": "Teluglish",
        "provenance": "synthetic_adversarial",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello andi... voice chala low ga undi... speaker lo problem vachindi... "
            "Senior: Evaru matladuthunnaru? "
            "Caller: Signal sarigga ledu, nenu malli call chesthanu."
        )
    },
    {
        "id": "adv_ambi_general_inquiry_031_en",
        "category": "ambiguous_interrupted_dialogue",
        "language": "English",
        "provenance": "synthetic_adversarial",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Hello, I am inquiring about the apartment parking space listed on the building bulletin. "
            "Senior: Yes, parking slot number 4 is available. "
            "Caller: Thank you, I will speak with the association secretary."
        )
    },
    {
        "id": "adv_ambi_garbled_hindi_032_hi",
        "category": "ambiguous_interrupted_dialogue",
        "language": "Hindi",
        "provenance": "synthetic_adversarial",
        "ground_truth": "INSUFFICIENT_EVIDENCE",
        "transcript": (
            "Caller: Haan namaste... sunai nahi de raha... network problem chal rahi hai... "
            "Senior: Kisko phone lagaya aapne? "
            "Caller: Baad mein phone milate hain."
        )
    }
]
