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
    """
    if not text:
        return text
    
    sanitized = REDACT_CARD_PATTERN.sub("[REDACTED_CARD_NUMBER]", text)
    sanitized = REDACT_AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", sanitized)
    sanitized = REDACT_PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
    
    # Redact 4-8 digit codes when credential keywords like 'otp', 'code', 'pin', 'password' are nearby
    if re.search(r"\b(otp|code|pin|sms|password|cvv)\b", sanitized, re.IGNORECASE):
        sanitized = REDACT_OTP_PATTERN.sub("[REDACTED_CREDENTIAL]", sanitized)
        
    return sanitized

