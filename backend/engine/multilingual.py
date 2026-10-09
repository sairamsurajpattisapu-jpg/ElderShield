import re
from typing import Dict, List, Tuple

# Multi-lingual keyword & phrase registries for ElderShield Scam Detection Engine
# Supports English, Hindi (Devanagari + Hinglish transliterations), Telugu (Telugu Script + Teluglish)
# Accommodates common ASR phonetic corruptions (e.g. 'otpp', 'any desk', 'quik suport')

PATTERNS_IMPERSONATION = {
    "BANK_AUTHORITY": [
        r"\b(?:calling\s+from|this\s+is\s+[\w\s]+from)\s+(?:sbi|state\s+bank(?:\s+of\s+india)?|hdfc|icici|axis|pnb|rbi|reserve\s+bank|central\s+bank)\b",
        r"\b(?:i\s+am|speaking\s+from)\s+(?:the\s+)?(?:bank|head\s+office|fraud\s+prevention\s+department|security\s+division)\b",
        r"\b(?:bank\s+manager|branch\s+manager|bank\s+officer|rbi\s+officer)\s+(?:calling|here)\b",
        r"\b(?:credit\s+card|debit\s+card)\s+(?:department|division|rewards\s+department|fraud\s+cell)\b",
        r"(बैंक\s+अधिकारी|बैंक\s+मैनेजर|आरबीआई|रिजर्व\s+बैंक|बैंक\s+से\s+बोल\s+रहा)",
        r"(బ్యాంకు\s+మేనేజర్|రిజర్వ్\s+బ్యాంక్|ఆర్\s+బి\s+ఐ|బ్యాంకు\s+నుంచి\s+కాల్)",
        r"\b(?:bank\s+nunchi\s+call|bank\s+se\s+bol\s+raha|bank\s+officer\s+ni)\b"
    ],
    "LAW_ENFORCEMENT_GOVT": [
        r"\b(?:from|officer\s+from|calling\s+from)\s+(?:police|cbi|central\s+bureau\s+of\s+investigation|ed|enforcement\s+directorate|customs|cyber\s+crime|cyber\s+cell|trai|narcotics)\b",
        r"\b(?:dsp|sub\s+inspector|commissioner|inspector)\s+[\w\s]+(?:calling|from)\b",
        r"\b(central\s+bureau\s+of\s+investigation|digital\s+arrest|arrest\s+warrant|case\s+registered|parcel\s+seized|contraband|drugs\s+found|supreme\s+court\s+order)\b",
        r"\b(?:high\s+court|supreme\s+court|district\s+court|court\s+registry|contempt\s+of\s+court|asset\s+attachment)\b",
        r"\b(?:uidai|aadhaar\s+(?:verification|authority|cell)|national\s+relief\s+fund|defense\s+directive)\b",
        r"(पुलिस|सीबीआई|कस्टम्स|साइबर\s+क्राइम|डिजिटल\s+अरेस्ट|गिरफ्तारी|वारंट)",
        r"(పోలీస్|సిబిఐ|కస్టమ్స్|సైబర్\s+క్రైమ్|డిజిటల్\s+అరెస్ట్|వారెంట్|కేసు\s+నమోదు)",
        r"\b(police\s+case|digital\s+arrest|warrant\s+issue|customs\s+lo\s+pattukunnaru|parcel\s+lo\s+drugs)\b"
    ],
    "UTILITY_TELECOM": [
        r"\b(?:(?:from|calling\s+from|office\s+of)?\s*(?:electricity\s+board|power\s+(?:department|office)|discom|tneb|bescom|apepdcl|apspdcl|bijli\s+vibhag|current\s+office))\b",
        r"\b(?:sim\s+will\s+be\s+blocked|telecom\s+department|trai\s+verification|meter\s+officer|power\s+cut\s+notice)\b",
        r"\b(?:department\s+of\s+telecommunications|dot\s+legal|dot\s+officer|\bdot\b|telecom\s+(?:authority|cellular|upgrade)|5g\s+upgrade)\b",
        r"\b(?:gas\s+(?:cylinder|agency|authority|distribution)|lpg\s+(?:subsidy|department|connection))\b",
        r"(बिजली\s+विभाग|पावर\s+ऑफिस|मीटर\s+रीडर|सिम\s+बंद|दूरसंचार)",
        r"(కరెంట్\s+ఆఫీస్|విద్యుత్\s+శాఖ|సిమ్\s+బ్లాక్|టెలికాం|మీటర్\s+రీడింగ్|గ్యాస్\s+సిలిండర్)",
        r"\b(current\s+bill\s+cut|bijli\s+kat\s+jayegi|sim\s+card\s+block|gas\s+cylinder|lpg\s+subsidy)\b"
    ],
    "PENSION_SCHEME": [
        r"\b(?:from\s+the\s+)?(?:pension\s+disbursement|treasury\s+office|jeevan\s+pramaan|life\s+certificate|epfo\s+department|epfo|provident\s+fund)\b",
        r"(पेंशन\s+विभाग|जीवन\s+प्रमाण\s+पत्र|ट्रेजरी|आधार\s+केवाईसी\s+सत्यापन|ईपीएफओ|भविष्य\s+निधि)",
        r"(పెన్షన్\s+ఆఫీస్|జీవన్\s+ప్రమాణ్|ట్రెజరీ|ఆధార్\s+కెవైసి|ఈపీఎఫ్ఓ)",
        r"\b(pension\s+aagipothundi|pension\s+band\s+hoga|jeevan\s+praman\s+patra|pf\s+pension|epfo)\b"
    ]
}

PATTERNS_URGENCY_INTIMIDATION = [
    r"\b(?:within\s+\d+\s+(?:minutes|hours|mins|hrs)|power\s+will\s+be\s+cut|disconnect\s+tonight|power\s+cut\s+at\s+\d+|digital\s+arrest|under\s+digital\s+arrest)\b",
    r"\b(?:account\s+(?:is\s+)?(?:blocked|suspended|frozen|permanently\s+freeze)(?:\s+(?:today|immediately|now))?|immediate\s+custody|police\s+on\s+the\s+way|police\s+lu\s+vasthunnaru)\b",
    r"\b(?:last\s+chance|before\s+disconnection|will\s+face\s+immediate\s+custody|arrest\s+warrant\s+issued|legal\s+notice\s+immediately)\b",
    r"\b(?:mobile\s+number\s+block|sim\s+cards?\s+chal\s+rahe|line\s+kat\s+jayegi|gas\s+supply\s+aagipothundi|connection\s+cancel|tax\s+audit\s+penalties)\b",
    r"(तुरंत\s+कीजिए|10\s+मिनट\s+में|आज\s+रात\s+बिजली\s+कट|अकाउंट\s+फ्रीज|जेल\s+होगी|गिरफ्तारी\s+होगी|आखिरी\s+मौका)",
    r"(10\s+నిమిషాల్లో|ఈరోజే\s+కరెంట్\s+కట్|అకౌంట్\s+బ్లాక్\s+అవుతుంది|పోలీసులు\s+వస్తున్నారు|అరెస్ట్\s+చేస్తారు|ఆఖరి\s+అవకాశం)",
    r"\b(turant\s+kijiye|aaj\s+raat\s+8\s+baje|abhi\s+nahi\s+kiya\s+toh|10\s+nimishallo|eeroju\s+night\s+current\s+cut|ippude\s+cheyyandi|disconnection\s+rokna)\b"
]

PATTERNS_SECRECY_ISOLATION = [
    r"\b(?:do\s+not\s+(?:tell|inform)\s+(?:anyone|family|children|your\s+family|son|daughter|wife|husband)|don't\s+(?:tell|inform)\s+anyone)\b",
    r"\b(?:keep\s+this\s+(?:confidential|secret|strictly\s+between\s+us))\b",
    r"\b(?:do\s+not\s+disconnect\s+(?:the|this)\s+call|stay\s+on\s+the\s+line|stay\s+on\s+the\s+video\s+call|stay\s+in\s+a\s+closed\s+room|isolate\s+yourself)\b",
    r"(किसी\s+को\s+मत\s+बताना|घर\s+वालों\s+को\s+मत\s+बताओ|फोन\s+मत\s+काटना|गोपनीय\s+रखें|अकेले\s+कमरे\s+में)",
    r"(ఎవరికీ\s+చెప్పకండి|పిల్లలకు\s+చెప్పొద్దు|రహస్యంగా\s+ఉంచండి|కాల్\s+కట్\s+చేయొద్దు|ఒంటరిగా\s+గదిలో)",
    r"\b(kisi\s+ko\s+mat\s+batana|ghar\s+pe\s+mat\s+batao|evariki\s+cheppakandi|phone\s+pettaddu|call\s+cut\s+cheyoddu|line\s+lo\s+undandi)\b"
]

# Excludes occurrences that are preceded by negative safeguards
PATTERNS_CREDENTIAL_REQUEST = [
    r"\b(?:share|tell|give|read\s+out|send|enter|verify|provide|state|confirm)\s+(?:me\s+)?(?:the|your)?\s*(?:\d+\s*digit\s+)?(?:otp|otpp|one\s*time\s*password|code|six\s*digit\s*code|sms\s*code|pin|upi\s*pin|atm\s*pin|cvv|password|confirmation\s*code|verification\s*code)\b",
    r"\b(?:share\s+the\s+6\s*digit|read\s+out\s+the\s+9\s*digit|share\s+the\s+code|what\s+is\s+the\s+code)\b",
    r"\b(?:enter\s+your\s+upi\s*pin|provide\s+your\s+atm\s*pin|what\s+is\s+the\s+otp|tell\s+me\s+the\s+otp)\b",
    r"\b(?:(?:16\s*digit\s*)?card\s*number|cvv\s+on\s+the\s+back|\bcvv\b)\b",
    r"(ओटीपी\s*बताइए|ओटीपी\s*बताएं|पिन\s*दर्ज\s*करें|ओटीपी\s*दीजिए|कोड\s*बोलो|सीवीवी\s*बताओ|पासवर्ड\s*दीजिए)",
    r"(ఓటీపీ\s*చెప్పండి|పిన్\s*నొక్కండి|కోడ్\s*ఇవ్వండి|ఓటీపీ\s*పంపండి|పాస్\s*వర్డ్\s*చెప్పండి)",
    r"\b(otp\s+batao|otp\s+bataiye|otp\s+batayein|otp\s+boliye|otp\s+cheppandi|pin\s+number\s+ivvandi|sms\s+code\s+cheppandi|pin\s+cheppandi|cvv\s+batao|cvv\s+bataiye)\b"
]

PATTERNS_FINANCIAL_TRANSFER = [
    r"\b(?:transfer|send|deposit|pay)\s+(?:your\s+savings|funds|money|(?:rupees|rs|inr|₹)\s*[\d,]+|[\d,]+\s*(?:rupees|rs|inr)?|rs|inr|₹|the\s+funds)\s+(?:to|into)\s+(?:the|our|a|my)?\s*(?:rbi|safety|clearing|verification|government|treasury|judicial|escrow|clearance|emergency)?\s*(?:verification\s+|escrow\s+|clearance\s+)?(?:account|upi\s*id)\b",
    r"\b(?:clear\s+the\s+[\w\s₹\d]+\s+bill\s+before\s+disconnection|pay\s+(?:via\s+)?(?:gpay|google\s+pay|phonepe|phone\s*pe|phone\s*pay|paytm|upi)\s+right\s+now)\b",
    r"\b(?:send\s+(?:rs|inr|₹)?\s*\d+\s+to\s+verify|transfer\s+all\s+funds\s+temporarily)\b",
    r"\b(?:processing\s+charge|security\s+deposit|mandatory\s+contribution|penalty)\s+[\d,]+\s*(?:rupees|rs|inr)?\s+(?:online\s+)?(?:transfer|deposit|pay|cheyyandi)\b",
    r"(सुरक्षित\s+खाते\s+में\s+भेजें|आरबीआई\s+खाते\s+में\s+ट्रांसफर|पैसे\s+तुरंत\s+भेजें|पैसे\s+जमा\s+करें)",
    r"(సేఫ్\s+అకౌంట్\s+కి\s+ట్రాన్స్\s*ఫర్|ఆర్\s*బి\s*ఐ\s+అకౌంట్\s+కి|వెంటనే\s+డబ్బులు\s+పంపండి|గూగుల్\s+పే\s+చేయండి)",
    r"\b(rbi\s+safe\s+account|rbi\s+safety\s+account|judicial\s+escrow|dabbu\s+transfer\s+cheyyandi|paise\s+transfer\s+karo|online\s+transfer\s+kijiye|(?:gpay|google\s+pay|phonepe|phone\s*pe|phone\s*pay|paytm|upi)\s+(?:cheyyandi|karo|par|kijiye))\b"
]

PATTERNS_REMOTE_ACCESS = [
    r"\b(?:download|install|open)\s+(?:the\s+)?(?:quicksupport|anydesk|teamviewer|rustdesk|airdroid|any\s*desk|quik\s*suport)(?:\s+app)?\b",
    r"\b(?:download\s+(?:the\s+)?(?:apk|software)\s+from\s+(?:the\s+)?sms\s+link|install\s+this\s+link|click\s+on\s+this\s+link)\b",
    r"\b(?:share\s+your\s+screen|allow\s+remote\s+support\s+access)\b",
    r"(क्विक\s*सपोर्ट\s+ऐप\s+डाउनलोड|एनीडेस्क\s+डाउनलोड|लिंक\s+से\s+ऐप\s+इंस्टॉल|स्क्रीन\s+शेयर\s+करें)",
    r"(క్విక్\s*సపోర్ట్\s+డౌన్లోడ్|ఎనీడెస్క్\s+ఇన్స్టాల్|యాప్\s+డౌన్లోడ్\s+చేయండి|స్క్రీన్\s+షేర్)",
    r"\b(quicksupport\s+app|anydesk\s+install|apk\s+download|app\s+install\s+cheyyandi|screen\s+share\s+karo)\b"
]

PATTERNS_VERIFICATION_BYPASS = [
    r"\b(?:do\s+not\s+go\s+to\s+(?:the\s+)?(?:branch|office)|branch\s+cannot\s+resolve\s+this)\b",
    r"\b(?:customer\s+care\s+cannot\s+help\s+you|only\s+this\s+special\s+cell\s+can\s+clear\s+this)\b",
    r"\b(?:bypass\s+the\s+branch|do\s+not\s+call\s+bank\s+support|official\s+counter\s+is\s+closed)\b",
    r"(शाखा\s+जाने\s+की\s+जरूरत\s+नहीं|बैंक\s+में\s+मत\s+जाना|कस्टमर\s+केयर\s+मदद\s+नहीं\s+करेगा)",
    r"(బ్రాంచ్\s+కి\s+వెళ్లాల్సిన\s+అవసరం\s+లేదు|కస్టమర్\s+కేర్\s+తో\s+చెప్పొద్దు|బ్యాంకుకు\s+వెళ్లొద్దు)",
    r"\b(branch\s+ki\s+velloddu|branch\s+aane\s+ki\s+zaroorat\s+nahi|customer\s+care\s+mat\s+karo)\b"
]

PATTERNS_LEGITIMATE_SAFEGUARDS = [
    r"\b(?:visit\s+(?:your|our|the|a|local)?\s*(?:bank\s+)?(?:branch|office|station|counter|center)(?:\s+in\s+person)?|come\s+to\s+(?:our|the|your)\s+(?:branch|office|station|counter))\b",
    r"\b(?:(?:our\s+)?bank\s+never\s+asks\s+for\s+(?:your\s+)?otp|never\s+share\s+(?:your\s+)?otp|do\s+not\s+share\s+(?:your\s+)?otp)\b",
    r"\b(?:at\s+your\s+convenience|no\s+need\s+to\s+hurry|whenever\s+you\s+feel\s+comfortable|next\s+month|next\s+tuesday)\b",
    r"\b(?:official\s+counter|submit\s+(?:passbook|application|documents|id)\s+copy|scheduled\s+in-person\s+appointment|in-person\s+verification|pay\s+at\s+the\s+(?:office|counter))\b",
    r"(शाखा\s+में\s+आएं|कार्यालय\s+में\s+आएं|बैंक\s+कभी\s+ओटीपी\s+नहीं\s+मांगता|ओटीपी\s+कभी\s+साझा\s+न\s+करें|आराम\s+से\s+आएं)",
    r"(శాఖకు\s+రండి|ఆఫీసుకు\s+రండి|బ్యాంక్\s+ఎప్పుడూ\s+ఓటీపీ\s+అడగదు|ఓటీపీ\s+ఎవరికీ\s+చెప్పవద్దు|సౌకర్యవంతంగా\s+రండి)",
    r"\b(branch\s+ki\s+randi|office\s+ki\s+randi|branch\s+aakar\s+miliye|bank\s+kabhi\s+otp\s+nahi\s+mangta|otp\s+evariki\s+cheppavoddu)\b"
]

UNSUPPORTED_LINGUISTIC_CASES = [
    "Raw audio prosodic cues, caller emotional tone, and speech acoustics without transcript text.",
    "Ultra-regional archaic Telugu or Hindi dialects with zero common lexical tokens.",
    "Encrypted conversational slang or criminal cryptophasia not matching standard cyber extortion patterns.",
    "Script-mixing within single concatenated tokens that corrupt UTF-8 text segmentation."
]

def detect_language(text: str) -> str:
    """Detect primary language or mixed script."""
    has_devanagari = bool(re.search(r"[\u0900-\u097F]", text))
    has_telugu = bool(re.search(r"[\u0C00-\u0C7F]", text))
    
    lower = text.lower()
    hinglish_markers = ["aapka", "kijiye", "karo", "batao", "boliye", "hoga", "aayega", "hum", "nahi", "mat", "dar", "beta"]
    teluglish_markers = ["cheppandi", "cheyyandi", "randi", "pampandi", "vachindi", "ayyindi", "nunchi", "cheyoddu", "pillalaki", "saar", "emaindi", "ayyo"]
    
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
