from typing import List, Dict
from .models import ScenarioMetadata, ConversationTurn

DEMO_SCENARIOS: List[ScenarioMetadata] = [
    ScenarioMetadata(
        id="legitimate_bank_kyc",
        title="1. Legitimate Bank Call (Contains Sensitive Keywords)",
        expected_classification="LOW RISK",
        tag="Legitimate Protocol",
        target_demographic="Elderly Account Holder",
        language="English / Hinglish",
        description="A genuine SBI branch relationship manager calling regarding an upcoming annual KYC re-verification. The manager explicitly reminds the elderly citizen NEVER to share OTPs or passwords over the phone, and invites them to visit the local branch at their convenience.",
        turns=[
            ConversationTurn(
                turn_number=1,
                speaker="Caller",
                text="Good morning, Mr. Sharma. This is Ramesh from State Bank of India, your home branch manager's office."
            ),
            ConversationTurn(
                turn_number=2,
                speaker="Senior",
                text="Good morning. Is there any problem with my pension account or my fixed deposits?"
            ),
            ConversationTurn(
                turn_number=3,
                speaker="Caller",
                text="No problem at all, sir. We are reviewing accounts due for periodic KYC updates next month. I am calling to inform you that you may visit your local branch in person at your convenience whenever you are free."
            ),
            ConversationTurn(
                turn_number=4,
                speaker="Senior",
                text="Can I update this online or do I need to send my OTP or documents to someone?"
            ),
            ConversationTurn(
                turn_number=5,
                speaker="Caller",
                text="Please note, sir, our bank never asks for OTP or PIN over phone calls. Never share your OTP with anyone, even bank staff. Please simply come to our branch with your passbook and Aadhaar copy whenever you feel comfortable. No need to hurry."
            ),
            ConversationTurn(
                turn_number=6,
                speaker="Senior",
                text="Thank you Ramesh, that is very reassuring. I will come to the branch next Tuesday with my son."
            )
        ]
    ),
    ScenarioMetadata(
        id="progressive_electricity_scam",
        title="2. Progressive Electricity Disconnection Scam",
        expected_classification="HIGH RISK",
        tag="Progressive Threat",
        target_demographic="Elderly Homeowner",
        language="English / Mixed Hindi",
        description="A predator contacts an elderly citizen claiming to be from the Electricity Board (APEPDCL/Discom). Over 5 turns, the caller claims the power will be disconnected at 8 PM tonight, manufactures urgency, demands remote app installation (QuickSupport), and pressures the senior for an OTP/UPI transfer.",
        turns=[
            ConversationTurn(
                turn_number=1,
                speaker="Caller",
                text="Hello, I am calling from Electricity Board Power Department regarding your home electric meter connection."
            ),
            ConversationTurn(
                turn_number=2,
                speaker="Senior",
                text="Yes? What is this about? I paid my electricity bill last week only."
            ),
            ConversationTurn(
                turn_number=3,
                speaker="Caller",
                text="Sir, your previous month bill of ₹120 was not updated in the central server. Power will be cut tonight at 8 PM immediately unless your meter software is updated within 15 minutes."
            ),
            ConversationTurn(
                turn_number=4,
                speaker="Senior",
                text="Tonight 8 PM? Oh dear, my wife is unwell, we cannot have power cut! How do I pay this ₹120?"
            ),
            ConversationTurn(
                turn_number=5,
                speaker="Caller",
                text="Do not tell anyone or disconnect the call. Stay on the line. Immediately download QuickSupport app on your mobile phone from the SMS link I sent."
            ),
            ConversationTurn(
                turn_number=6,
                speaker="Senior",
                text="I have installed it. Now it is showing a 9 digit code on screen. What should I do?"
            ),
            ConversationTurn(
                turn_number=7,
                speaker="Caller",
                text="Read out the 9 digit code and then share the 6 digit OTP you received right now so I can connect and clear the ₹120 bill before disconnection!"
            )
        ]
    ),
    ScenarioMetadata(
        id="ambiguous_delivery_inquiry",
        title="3. Ambiguous Delivery Inquiry (Insufficient Evidence)",
        expected_classification="INSUFFICIENT EVIDENCE",
        tag="Incomplete Context",
        target_demographic="General Senior",
        language="English",
        description="A very brief, inconclusive dialogue from an unknown caller inquiring about a delivery package address with no coercive demands, no credential requests, and no verified institutional identity.",
        turns=[
            ConversationTurn(
                turn_number=1,
                speaker="Caller",
                text="Hello, good afternoon. Am I speaking to the resident at Plot 42?"
            ),
            ConversationTurn(
                turn_number=2,
                speaker="Senior",
                text="Yes, who is this? I am having lunch right now."
            ),
            ConversationTurn(
                turn_number=3,
                speaker="Caller",
                text="I have a parcel delivery scheduled for this afternoon. Is there anyone available at home?"
            )
        ]
    ),
    ScenarioMetadata(
        id="digital_arrest_telugu_scam",
        title="4. Vizag CBI Digital Arrest & Parcel Scam (Telugu / English)",
        expected_classification="HIGH RISK",
        tag="Regional / High Threat",
        target_demographic="Telugu Senior Citizen (AP/Vizag)",
        language="Telugu (తెలుగు) & English",
        description="A high-intensity scam targeting elderly citizens in Andhra Pradesh. The scammer poses as Visakhapatnam Cyber Crime / CBI Officer claiming a seized customs parcel containing illegal passports and drugs, threatening 'digital arrest' and demanding transfer to a 'safe RBI clearance account'.",
        turns=[
            ConversationTurn(
                turn_number=1,
                speaker="Caller",
                text="Hello, I am DSP Rao calling from Cyber Crime Police & CBI Special Task Force, Visakhapatnam."
            ),
            ConversationTurn(
                turn_number=2,
                speaker="Senior",
                text="Police ah? Em jarigindi saar? Nenemi cheyaledu."
            ),
            ConversationTurn(
                turn_number=3,
                speaker="Caller",
                text="A parcel with your Aadhaar card containing illegal contraband was seized at customs. Digital arrest warrant issue ayyindi. Police lu vasthunnaru to your house."
            ),
            ConversationTurn(
                turn_number=4,
                speaker="Senior",
                text="Ayyo! Naaku emi teleedu saar. Naa pillalaki phone chesi matladatha please."
            ),
            ConversationTurn(
                turn_number=5,
                speaker="Caller",
                text="Evariki cheppakandi! Do not disconnect the call! Stay on the video call in a closed room or you will face immediate custody."
            ),
            ConversationTurn(
                turn_number=6,
                speaker="Caller",
                text="To clear your name from digital arrest, immediately transfer your savings to the RBI safety account via Google Pay right now!"
            )
        ]
    )
]

SCENARIO_LOOKUP: Dict[str, ScenarioMetadata] = {
    sc.id: sc for sc in DEMO_SCENARIOS
}
