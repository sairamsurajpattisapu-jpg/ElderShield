import re
from typing import Dict, List, Tuple

# Multi-lingual keyword & phrase registries for ElderShield Scam Engine
# Covers English, Hindi (Devanagari + Hinglish), Telugu (Telugu Script + Teluglish)

PATTERNS_IMPERSONATION = {
    "BANK_AUTHORITY": [
        r"\b(?:calling\s+from|this\s+is\s+[\w\s]+from)\s+(?:sbi|hdfc|icici|axis|pnb|rbi|reserve\s+bank|central\s+bank)\b",
        r"\b(?:i\s+am|speaking\s+from)\s+(?:the\s+)?(?:bank|head\s+office|fraud\s+prevention\s+department|security\s+division)\b",
        r"(बैंक\s+अधिकारी|बैंक\s+मैनेजर|आरबीआई|रिजर्व\s+बैंक|बैंक\s+से\s+बोल\s+रहा)",
        r"(బ్యాంకు\s+మేనేజర్|రిజర్వ్\s+బ్యాంక్|ఆర్\s+బి\s+ఐ|బ్యాంకు\s+నుంచి\s+కాల్)",
        r"\b(bank\s+nunchi\s+call|bank\s+se\s+bol\s+raha|bank\s+officer\s+ni)\b"
    ],
    "LAW_ENFORCEMENT_GOVT": [
        r"\b(?:from|officer\s+from|calling\s+from)\s+(?:police|cbi|ed|enforcement\s+directorate|customs|cyber\s+crime|cyber\s+cell|trai|narcotics)\b",
        r"\b(?:dsp|sub\s+inspector|commissioner|inspector)\s+[\w\s]+(?:calling|from)\b",
        r"\b(digital\s+arrest|arrest\s+warrant|case\s+registered|parcel\s+seized|contraband|drugs\s+found)\b",
        r"(पुलिस|सीबीआई|कस्टम्स|साइबर\s+क्राइम|डिजिटल\s+अरेस्ट|गिरफ्तारी|वारंट)",
        r"(పోలీస్|సిబిఐ|కస్టమ్స్|సైబర్\s+క్రైమ్|డిజిటల్\s+అరెస్ట్|వారెంట్|కేసు\s+నమోదు)",
        r"\b(police\s+case|digital\s+arrest|warrant\s+issue|customs\s+lo\s+pattukunnaru|parcel\s+lo\s+drugs)\b"
    ],
    "UTILITY_TELECOM": [
        r"\b(?:from|calling\s+from)\s+(?:electricity\s+board|power\s+department|discom|tneb|bescom|apepdcl|apspdcl|bijli\s+vibhag)\b",
        r"\b(?:sim\s+will\s+be\s+blocked|telecom\s+department|trai\s+verification|meter\s+officer)\b",
        r"(बिजली\s+विभाग|पावर\s+ऑफिस|मीटर\s+रीडर|सिम\s+बंद|दूरसंचार)",
        r"(కరెంట్\s+ఆఫీస్|విద్యుత్\s+శాఖ|సిమ్\s+బ్లాక్|టెలికాం|మీటర్\s+రీడింగ్)",
        r"\b(current\s+bill\s+cut|bijli\s+kat\s+jayegi|sim\s+card\s+block)\b"
    ],
    "PENSION_SCHEME": [
        r"\b(?:from\s+the\s+)?(?:pension\s+disbursement|treasury\s+office|jeevan\s+pramaan|life\s+certificate|epfo\s+department)\b",
        r"(पेंशन\s+विभाग|जीवन\s+प्रमाण\s+पत्र|ट्रेजरी|आधार\s+केवाईसी\s+सत्यापन)",
        r"(పెన్షన్\s+ఆఫీస్|జీవన్\s+ప్రమాణ్|ట్రెజరీ|ఆధార్\s+కెవైసి)",
        r"\b(pension\s+aagipothundi|pension\s+band\s+hoga|jeevan\s+praman\s+patra)\b"
    ]
}

PATTERNS_URGENCY_INTIMIDATION = [
    r"\b(?:within\s+(?:5|10|15|30)\s+minutes|power\s+will\s+be\s+cut|disconnect\s+tonight|power\s+cut\s+at\s+\d+)\b",
    r"\b(?:account\s+(?:blocked|suspended|frozen)\s+today|immediate\s+custody|police\s+on\s+the\s+way|police\s+lu\s+vasthunnaru)\b",
    r"\b(?:last\s+chance|before\s+disconnection|will\s+face\s+immediate\s+custody|arrest\s+warrant\s+issued)\b",
    r"(तुरंत\s+कीजिए|10\s+मिनट\s+में|आज\s+रात\s+बिजली\s+कट|अकाउंट\s+फ्रीज|जेल\s+होगी|गिरफ्तारी\s+होगी)",
    r"(10\s+నిమిషాల్లో|ఈరోజే\s+కరెంట్\s+కట్|అకౌంట్\s+బ్లాక్\s+అవుతుంది|పోలీసులు\s+వస్తున్నారు|అరెస్ట్\s+చేస్తారు)",
    r"\b(turant\s+kijiye|aaj\s+raat\s+8\s+baje|abhi\s+nahi\s+kiya\s+toh|10\s+nimishallo|eeroju\s+night\s+current\s+cut)\b"
]

PATTERNS_SECRECY_ISOLATION = [
    r"\b(?:do\s+not\s+tell\s+(?:anyone|family|children|son|daughter|wife|husband)|don't\s+tell\s+anyone)\b",
    r"\b(?:keep\s+this\s+(?:confidential|secret|strictly\s+between\s+us))\b",
    r"\b(?:do\s+not\s+disconnect\s+the\s+call|stay\s+on\s+the\s+line|stay\s+on\s+the\s+video\s+call|stay\s+in\s+a\s+closed\s+room|isolate\s+yourself)\b",
    r"(किसी\s+को\s+मत\s+बताना|घर\s+वालों\s+को\s+मत\s+बताओ|फोन\s+मत\s+काटना|गोपनीय\s+रखें|अकेले\s+कमरे\s+में)",
    r"(ఎవరికీ\s+చెప్పకండి|పిల్లలకు\s+చెప్పొద్దు|రహస్యంగా\s+ఉంచండి|కాల్\s+కట్\s+చేయొద్దు|ఒంటరిగా\s+గదిలో)",
    r"\b(kisi\s+ko\s+mat\s+batana|ghar\s+pe\s+mat\s+batao|evariki\s+cheppakandi|phone\s+pettaddu|call\s+cut\s+cheyoddu)\b"
]

# Note: Negated occurrences like "never share OTP" are explicitly filtered in analyzer
PATTERNS_CREDENTIAL_SOLICITATION = [
    r"\b(?:share|tell|give|read\s+out|send|enter)\s+(?:the|your)?\s*(?:otp|one\s*time\s*password|six\s*digit\s*code|sms\s*code|pin|upi\s*pin|cvv)\b",
    r"\b(?:share\s+the\s+6\s*digit|read\s+out\s+the\s+9\s*digit|share\s+the\s+code)\b",
    r"\b(?:enter\s+your\s+upi\s*pin|provide\s+your\s+atm\s*pin|what\s+is\s+the\s+otp)\b",
    r"(ओटीपी\s*बताइए|पिन\s*दर्ज\s*करें|ओटीपी\s*दीजिए|कोड\s*बोलो|सीवीवी\s*बताओ)",
    r"(ఓటీపీ\s*చెప్పండి|పిన్\s*నొక్కండి|కోడ్\s*ఇవ్వండి|ఓటీపీ\s*పంపండి)",
    r"\b(otp\s+batao|otp\s+boliye|otp\s+cheppandi|pin\s+number\s+ivvandi|sms\s+code\s+cheppandi)\b"
]

PATTERNS_FINANCIAL_COERCION = [
    r"\b(?:transfer|send)\s+(?:your\s+savings|funds|money|\d+|rs|inr|₹)\s+to\s+(?:the\s+)?(?:rbi|safety|clearing|verification)\s+account\b",
    r"\b(?:clear\s+the\s+[\w\s₹\d]+\s+bill\s+before\s+disconnection|pay\s+(?:via\s+)?(?:gpay|google\s+pay|phonepe|paytm|upi)\s+right\s+now)\b",
    r"(सुरक्षित\s+खाते\s+में\s+भेजें|आरबीआई\s+खाते\s+में\s+ट्रांसफर|पैसे\s+तुरंत\s+भेजें)",
    r"(సేఫ్\s+అకౌంట్\s+కి\s+ట్రాన్స్\s*ఫర్|ఆర్\s*బి\s*ఐ\s+అకౌంట్\s+కి|వెంటనే\s+డబ్బులు\s+పంపండి)",
    r"\b(rbi\s+safe\s+account|rbi\s+safety\s+account|dabbu\s+transfer\s+cheyyandi|paise\s+transfer\s+karo)\b"
]

PATTERNS_REMOTE_ACCESS_MALWARE = [
    r"\b(?:download|install|open)\s+(?:the\s+)?(?:quicksupport|anydesk|teamviewer|rustdesk|airdroid)(?:\s+app)?\b",
    r"\b(?:download\s+(?:the\s+)?(?:apk|software)\s+from\s+(?:the\s+)?sms\s+link|install\s+this\s+link)\b",
    r"(क्विक\s*सपोर्ट\s+ऐप\s+डाउनलोड|एनीडेस्क\s+डाउनलोड|लिंक\s+से\s+ऐप\s+इंस्टॉल)",
    r"(క్విక్\s*సపోర్ట్\s+డౌన్లోడ్|ఎనీడెస్క్\s+ఇన్స్టాల్|యాప్\s+డౌన్లోడ్\s+చేయండి)",
    r"\b(quicksupport\s+app|anydesk\s+install|apk\s+download)\b"
]

PATTERNS_LEGITIMATE_SAFEGUARDS = [
    r"\b(?:visit\s+(?:your\s+)?(?:local\s+)?branch(?:\s+in\s+person)?|come\s+to\s+(?:our|the)\s+branch)\b",
    r"\b(?:bank\s+never\s+asks\s+for\s+otp|never\s+share\s+your\s+otp|do\s+not\s+share\s+(?:your\s+)?otp)\b",
    r"\b(?:at\s+your\s+convenience|no\s+need\s+to\s+hurry|whenever\s+you\s+feel\s+comfortable|next\s+month)\b",
    r"(शाखा\s+में\s+आएं|बैंक\s+कभी\s+ओटीपी\s+नहीं\s+मांगता|ओटीपी\s+कभी\s+साझा\s+न\s+करें|आराम\s+से\s+आएं)",
    r"(శాఖకు\s+రండి|బ్యాంక్\s+ఎప్పుడూ\s+ఓటీపీ\s+అడగదు|ఓటీపీ\s+ఎవరికీ\s+చెప్పవద్దు|సౌకర్యవంతంగా\s+రండి)",
    r"\b(branch\s+ki\s+randi|branch\s+aakar\s+miliye|bank\s+kabhi\s+otp\s+nahi\s+mangta|otp\s+evariki\s+cheppavoddu)\b"
]

def detect_language(text: str) -> str:
    """Detect primary language or mixed script."""
    has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
    has_telugu = bool(re.search(r"[\u0C00-\u0C7F]", text))
    
    lower = text.lower()
    hinglish_markers = ["aapka", "kijiye", "karo", "batao", "boliye", "hoga", "aayega", "hum", "nahi", "mat"]
    teluglish_markers = ["cheppandi", "cheyyandi", "randi", "pampandi", "vachindi", "ayyindi", "nunchi", "cheyoddu", "pillalaki", "saar"]
    
    hinglish_count = sum(1 for m in hinglish_markers if m in lower)
    teluglish_count = sum(1 for m in teluglish_markers if m in lower)
    
    if has_telugu and has_devanagari:
        return "Telugu / Hindi (Multilingual)"
    elif has_telugu:
        return "Telugu (తెలుగు)"
    elif has_devanagari:
        return "Hindi (हिन्दी)"
    elif teluglish_count >= 2:
        return "Teluglish (Telugu in Roman Script)"
    elif hinglish_count >= 2:
        return "Hinglish (Hindi in Roman Script)"
    else:
        return "English"
