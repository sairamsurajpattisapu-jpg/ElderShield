"""
ElderShield Structured Scenario Dataset (17 Synthetic Test Cases)
Covers all requirements from the HWV4 validation specification:
1. Legitimate bank conversation.
2. Legitimate OTP discussion.
3. Government-authority impersonation.
4. Fake account suspension.
5. Urgent payment request.
6. OTP theft.
7. UPI PIN request.
8. Remote-access application scam.
9. Secrecy and isolation tactics.
10. Mixed legitimate and suspicious conversation.
11. Ambiguous conversation.
12. English-Hindi code-switching.
13. English-Telugu code-switching.
14. Telugu transliteration.
15. Hindi transliteration.
16. Conversation with ASR-like spelling errors.
17. Suspicious conversation without explicit OTP or payment keywords.
"""

from typing import List, Dict, Any

SCENARIO_DATASET: List[Dict[str, Any]] = [
    {
        "id": "scenario_01_legit_bank",
        "name": "1. Legitimate bank conversation",
        "expected_label": "LOW_RISK",
        "description": "Branch official schedules regular branch appointment for passbook update without requests for credentials.",
        "transcript": (
            "Caller: Good morning Mr. Verma, this is SBI branch customer desk regarding your passbook renewal.\n"
            "Senior: Hello, do I need to submit any fee or payment?\n"
            "Caller: No fee at all sir. Please come to our branch with your passbook copy at your convenience whenever you have time."
        )
    },
    {
        "id": "scenario_02_legit_otp",
        "name": "2. Legitimate OTP discussion",
        "expected_label": "LOW_RISK",
        "description": "Senior asks if they should give OTP, and bank officer explicitly warns NEVER to share OTP and invites them to the branch.",
        "transcript": (
            "Caller: Hello Mrs. Rao, calling from HDFC home branch to inform you your fixed deposit matured.\n"
            "Senior: Should I tell you my OTP or net banking details to renew it?\n"
            "Caller: Never share your OTP with anyone, even bank staff. Bank never asks for OTP. Please visit your local branch in person next week."
        )
    },
    {
        "id": "scenario_03_govt_impersonation",
        "name": "3. Government-authority impersonation",
        "expected_label": "HIGH_RISK",
        "description": "Caller impersonates CBI Special Task Force, claims arrest warrant, and demands funds in safe account.",
        "transcript": (
            "Caller: I am DSP Kumar calling from CBI Special Task Force. An arrest warrant was issued for money laundering.\n"
            "Senior: Sir I am a retired teacher, I have done nothing illegal!\n"
            "Caller: Stay on the line. Transfer your savings to the RBI safety account right now to clear your name."
        )
    },
    {
        "id": "scenario_04_fake_account_suspension",
        "name": "4. Fake account suspension",
        "expected_label": "HIGH_RISK",
        "description": "Threatens bank account suspension today unless OTP is shared within 10 minutes.",
        "transcript": (
            "Caller: This is Central Bank security division. Your account suspended today due to KYC failure.\n"
            "Senior: How do I prevent suspension? I need my pension.\n"
            "Caller: You have last chance within 10 minutes. Read out the sms code on your phone right now."
        )
    },
    {
        "id": "scenario_05_urgent_payment",
        "name": "5. Urgent payment request",
        "expected_label": "HIGH_RISK",
        "description": "Electricity department disconnection threat requiring immediate UPI transfer.",
        "transcript": (
            "Caller: Calling from electricity board power department. Power will be cut tonight at 8 unless unpaid bill cleared.\n"
            "Senior: I always pay my bills on time!\n"
            "Caller: System shows penalty pending. Pay via Google Pay right now before disconnection!"
        )
    },
    {
        "id": "scenario_06_otp_theft",
        "name": "6. OTP theft",
        "expected_label": "HIGH_RISK",
        "description": "Direct aggressive solicitation of 6-digit OTP code pretending to be fraud security department.",
        "transcript": (
            "Caller: Fraud prevention department speaking. We detected unauthorized debit.\n"
            "Senior: Oh my goodness, please stop it!\n"
            "Caller: To block the transaction, share the 6 digit OTP you just received immediately."
        )
    },
    {
        "id": "scenario_07_upi_pin_request",
        "name": "7. UPI PIN request",
        "expected_label": "HIGH_RISK",
        "description": "Lures senior with pension refund but asks to enter UPI PIN to receive money.",
        "transcript": (
            "Caller: We are disbursing your bonus pension amount of ₹15000.\n"
            "Senior: Thank you, how do I receive it?\n"
            "Caller: Open PhonePe, scan this QR code, and enter your UPI PIN to claim your refund."
        )
    },
    {
        "id": "scenario_08_remote_access_scam",
        "name": "8. Remote-access application scam",
        "expected_label": "HIGH_RISK",
        "description": "Instructs elderly victim to install AnyDesk or QuickSupport application.",
        "transcript": (
            "Caller: This is customer technical support for your phone banking application.\n"
            "Senior: My app was crashing yesterday.\n"
            "Caller: Download QuickSupport app from the sms link and share your screen so we can configure your phone."
        )
    },
    {
        "id": "scenario_09_secrecy_isolation",
        "name": "9. Secrecy and isolation tactics",
        "expected_label": "HIGH_RISK",
        "description": "Caller demands absolute secrecy and forbids telling children while soliciting money transfer.",
        "transcript": (
            "Caller: This is high court legal summons department. You are under secret financial investigation.\n"
            "Senior: Can I ask my daughter to look into this?\n"
            "Caller: Do not tell anyone! Keep this strictly confidential and transfer funds to the government clearing account immediately."
        )
    },
    {
        "id": "scenario_10_mixed_legit_suspicious",
        "name": "10. Mixed legitimate and suspicious conversation",
        "expected_label": "SUSPICIOUS",
        "description": "Caller mentions bank account inquiry and creates mild urgency, but stops short of requesting OTP or remote app.",
        "transcript": (
            "Caller: Hello, I am calling from bank verification team regarding recent card activity.\n"
            "Senior: Yes, I used it at the grocery store.\n"
            "Caller: We need to verify your address quickly within 15 minutes before the daily cutoff."
        )
    },
    {
        "id": "scenario_11_ambiguous_conversation",
        "name": "11. Ambiguous conversation",
        "expected_label": "INSUFFICIENT_EVIDENCE",
        "description": "Neutral inquiry about residence and parcels with no authority claim or threat.",
        "transcript": (
            "Caller: Hello, is this resident at flat 102?\n"
            "Senior: Yes, who is speaking please?\n"
            "Caller: I have a parcel delivery packet for this address. Are you available?"
        )
    },
    {
        "id": "scenario_12_english_hindi_code_switching",
        "name": "12. English-Hindi code-switching",
        "expected_label": "HIGH_RISK",
        "description": "Code-switched Hinglish call threatening digital arrest and asking for bank transfer.",
        "transcript": (
            "Caller: Hello, police officer from cyber cell bol raha hu. Parcel me illegal contraband pakda gaya.\n"
            "Senior: Maine koi parcel nahi bheja sir.\n"
            "Caller: Digital arrest warrant issue hua hai. Turant safe account me paise transfer karo to clear your name."
        )
    },
    {
        "id": "scenario_13_english_telugu_code_switching",
        "name": "13. English-Telugu code-switching",
        "expected_label": "HIGH_RISK",
        "description": "Code-switched Teluglish call claiming power cutoff and demanding OTP.",
        "transcript": (
            "Caller: Hello, electricity board power department nunchi call chesthunna.\n"
            "Senior: Em jarigindi saar?\n"
            "Caller: Eeroju night current cut chestharu bill pending undi. QuickSupport app download chesi OTP cheppandi ventane!"
        )
    },
    {
        "id": "scenario_14_telugu_transliteration",
        "name": "14. Telugu transliteration",
        "expected_label": "HIGH_RISK",
        "description": "Pure Telugu transliteration with secrecy and arrest intimidation.",
        "transcript": (
            "Caller: Police station nunchi call chesthunnam. Mee meeda case register ayyindi.\n"
            "Senior: Ayyo naaku em teleedu saar.\n"
            "Caller: Evariki cheppakandi, phone cut cheyyakunda RBI safe account ki dabbu transfer cheyyandi."
        )
    },
    {
        "id": "scenario_15_hindi_transliteration",
        "name": "15. Hindi transliteration",
        "expected_label": "HIGH_RISK",
        "description": "Hinglish call claiming bank account freeze and demanding OTP.",
        "transcript": (
            "Caller: Main SBI head office se bol raha hu. Aapka account aaj raat freeze ho jayega.\n"
            "Senior: Beta mera pension kaise aayega phir?\n"
            "Caller: Jaldi se mobile pe aaya hua OTP batao warna account band hoga."
        )
    },
    {
        "id": "scenario_16_asr_spelling_errors",
        "name": "16. Conversation with ASR-like spelling errors",
        "expected_label": "HIGH_RISK",
        "description": "Speech-to-text corruptions (otpp, kwick suport, disconect tonite).",
        "transcript": (
            "Caller: Bank security here. Power and account will disconnect tonight at 8.\n"
            "Senior: What is required to fix this?\n"
            "Caller: Install quicksupport and read out the otpp code immediately right now."
        )
    },
    {
        "id": "scenario_17_suspicious_no_explicit_otp",
        "name": "17. Suspicious conversation without explicit OTP or payment keywords",
        "expected_label": "SUSPICIOUS",
        "description": "Impersonator demands secrecy and isolation without yet naming OTP or money.",
        "transcript": (
            "Caller: This is inspector from cyber crime division calling on a confidential matter.\n"
            "Senior: Yes inspector, how can I help?\n"
            "Caller: You must keep this strictly confidential and do not tell family. Move to a quiet room and stay on the line."
        )
    }
]
