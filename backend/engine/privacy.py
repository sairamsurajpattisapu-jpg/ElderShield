import re

RAW_AUDIO_RETENTION_POLICY = "EPHEMERAL_IN_MEMORY_ONLY"
DATA_RETENTION_HOURS = 0
MAX_IN_MEMORY_TURNS = 50

REDACT_OTP_PATTERN = re.compile(r"\b(\d{4,8})\b")
REDACT_CARD_PATTERN = re.compile(r"\b(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})\b")
REDACT_AADHAAR_PATTERN = re.compile(r"\b(\d{4}\s\d{4}\s\d{4})\b")
REDACT_PHONE_PATTERN = re.compile(r"\b(?:\+91[-\s]?)?([6-9]\d{9})\b")

def redact_sensitive_data(text: str) -> str:
    """
    Sanitizes raw text or logs to prevent storing or transmitting sensitive personal
    information such as OTPs, Aadhaar numbers, card numbers, or UPI PINs.
    Contextually redacts verification codes while preserving ordinary numbers.
    """
    if not text:
        return text
    
    sanitized = REDACT_CARD_PATTERN.sub("[REDACTED_CARD_NUMBER]", text)
    sanitized = REDACT_AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", sanitized)
    sanitized = REDACT_PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
    
    # 1. Forward contextual credential mentions (e.g. "OTP is 492018", "enter PIN 1234")
    sanitized = re.sub(
        r"(?i)\b((?:otp|pin|password|cvv|verification\s*code|sms\s*code|ओटीपी|ఓటీపీ)\b[^\d\n]{0,25})(\d{4,8})\b",
        r"\1[REDACTED_CREDENTIAL]",
        sanitized
    )

    # 2. Reverse contextual mentions (e.g. "492018 is your code", "1234 is the OTP")
    sanitized = re.sub(
        r"(?i)\b(\d{4,8})\b([^\d\n]{0,25}\b(?:is\s+(?:the|your)?\s*(?:otp|code|pin|password|verification)|is\s+the\s+code)\b)",
        r"[REDACTED_CREDENTIAL]\2",
        sanitized
    )

    # 3. If explicit authentication token keywords are present in the sentence, redact remaining standalone 4-8 digit sequences
    if re.search(r"\b(otp|one\s*time\s*password|verification\s*code|atm\s*pin|upi\s*pin|cvv|ओटीपी|ఓటీపీ)\b", sanitized, re.IGNORECASE):
        sanitized = REDACT_OTP_PATTERN.sub("[REDACTED_CREDENTIAL]", sanitized)

    return sanitized

