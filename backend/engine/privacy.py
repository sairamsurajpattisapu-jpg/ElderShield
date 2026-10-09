import re

REDACT_OTP_PATTERN = re.compile(r"\b(\d{6})\b")
REDACT_CARD_PATTERN = re.compile(r"\b(\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4})\b")
REDACT_AADHAAR_PATTERN = re.compile(r"\b(\d{4}\s\d{4}\s\d{4})\b")
REDACT_PHONE_PATTERN = re.compile(r"\b(?:\+91[-\s]?)?([6-9]\d{9})\b")

def redact_sensitive_data(text: str) -> str:
    """
    Sanitizes raw text or logs to prevent logging sensitive personal information
    such as OTPs, Aadhaar numbers, or card numbers.
    """
    if not text:
        return text
    
    sanitized = REDACT_CARD_PATTERN.sub("[REDACTED_CARD_NUMBER]", text)
    sanitized = REDACT_AADHAAR_PATTERN.sub("[REDACTED_AADHAAR]", sanitized)
    sanitized = REDACT_PHONE_PATTERN.sub("[REDACTED_PHONE]", sanitized)
    
    # Redact 6-digit codes only when nearby keywords like 'otp', 'code', 'pin' are present
    def replace_otp(match):
        return "[REDACTED_OTP]"
    
    if re.search(r"\b(otp|code|pin|sms)\b", sanitized, re.IGNORECASE):
        sanitized = REDACT_OTP_PATTERN.sub(replace_otp, sanitized)
        
    return sanitized
