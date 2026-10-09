import re
from typing import Dict, Any, List, Optional
import phonenumbers
from phonenumbers import geocoder, carrier, PhoneNumberType

from .models import CallerIntelligenceResult

# Registry of authentic institutional contact channels and public hotlines in India
OFFICIAL_INSTITUTIONAL_REGISTRY: Dict[str, Dict[str, Any]] = {
    "STATE BANK OF INDIA": {
        "aliases": ["sbi", "state bank", "sbi cards", "state bank of india"],
        "official_numbers": ["18001234", "18002100", "1800112211", "08026599990", "+918026599990"],
        "display_name": "State Bank of India (SBI)",
        "official_url": "https://sbi.co.in",
        "advisory": "SBI official representatives never conduct security investigations from personal mobile phone numbers."
    },
    "RESERVE BANK OF INDIA": {
        "aliases": ["rbi", "reserve bank", "reserve bank of india"],
        "official_numbers": ["14440", "02222660500", "+912222660500"],
        "display_name": "Reserve Bank of India (RBI)",
        "official_url": "https://rbi.org.in",
        "advisory": "RBI does not maintain individual savings escrow accounts or demand fund transfers from citizens."
    },
    "CENTRAL BUREAU OF INVESTIGATION": {
        "aliases": ["cbi", "central bureau of investigation", "cbi officer"],
        "official_numbers": ["01124368637", "01124362755", "+911124368637"],
        "display_name": "Central Bureau of Investigation (CBI)",
        "official_url": "https://cbi.gov.in",
        "advisory": "CBI does not enforce 'digital arrest' or demand funds over WhatsApp/phone calls."
    },
    "NATIONAL CYBER CRIME HELPLINE": {
        "aliases": ["cyber crime", "cyber cell", "1930", "national cybercrime portal"],
        "official_numbers": ["1930", "155260"],
        "display_name": "National Cyber Crime Reporting Helpline (Govt of India)",
        "official_url": "https://cybercrime.gov.in",
        "advisory": "1930 is the official citizen helpline to freeze stolen funds within the golden hour."
    },
    "TELECOM REGULATORY AUTHORITY": {
        "aliases": ["trai", "telecom department", "dot", "department of telecommunications"],
        "official_numbers": ["01123664145", "+911123664145"],
        "display_name": "Telecom Regulatory Authority of India (TRAI)",
        "official_url": "https://trai.gov.in",
        "advisory": "TRAI never calls subscribers threatening SIM card deactivation within hours."
    },
    "ELECTRICITY BOARD": {
        "aliases": ["electricity board", "power department", "apepdcl", "apspdcl", "bescom", "tneb", "discom", "bijli vibhag"],
        "official_numbers": ["1912"],
        "display_name": "State Electricity Distribution Corporation (DISCOM)",
        "official_url": "https://apeasternpower.com",
        "advisory": "Power distribution companies send written bill notices; they do not instruct customers to download APKs."
    },
    "POLICE EMERGENCY": {
        "aliases": ["police", "emergency", "112", "100"],
        "official_numbers": ["112", "100"],
        "display_name": "Emergency Police Control Room",
        "official_url": "https://112.gov.in",
        "advisory": "Official emergency police dispatch channel."
    }
}

class CallerIntelligenceService:
    """
    Modular Caller Intelligence & Phone Reputation Service.
    Performs E.164 normalization, carrier identification, telecom circle mapping,
    and institutional identity spoofing conflict analysis.
    """

    def lookup_caller(
        self,
        phone_number: str,
        claimed_organization: Optional[str] = None,
        country_hint: str = "IN"
    ) -> CallerIntelligenceResult:
        raw = phone_number.strip()
        if not raw:
            return CallerIntelligenceResult(
                raw_input="",
                is_valid=False,
                number_type="UNKNOWN",
                reputation_score=50.0,
                verdict="INVALID_FORMAT",
                advisory="No caller phone number provided."
            )

        # Check special national emergency/short codes (e.g. 1930, 112, 100, 1912)
        digits_only = re.sub(r"\D", "", raw)
        for org_key, org_data in OFFICIAL_INSTITUTIONAL_REGISTRY.items():
            for num in org_data["official_numbers"]:
                clean_num = re.sub(r"\D", "", num)
                if digits_only == clean_num or raw == num:
                    return CallerIntelligenceResult(
                        raw_input=raw,
                        is_valid=True,
                        e164_format=raw,
                        national_format=raw,
                        country_code="IN",
                        carrier="Official Government / Telecom Short Code",
                        geographic_region="India (National Toll-Free / Emergency)",
                        number_type="TOLL_FREE",
                        is_registered_institution=True,
                        registered_organization=org_data["display_name"],
                        official_helplines=org_data["official_numbers"],
                        spoofing_suspected=False,
                        reputation_score=5.0, # Highly safe
                        verdict="VERIFIED_INSTITUTION",
                        advisory=f"Verified official contact channel for {org_data['display_name']}."
                    )

        # Parse standard phone number with Google phonenumbers library
        try:
            parsed = phonenumbers.parse(raw, country_hint)
        except Exception:
            # Try with + prefix if missing
            try:
                parsed = phonenumbers.parse("+" + raw, country_hint)
            except Exception:
                return CallerIntelligenceResult(
                    raw_input=raw,
                    is_valid=False,
                    number_type="UNKNOWN",
                    reputation_score=60.0,
                    verdict="INVALID_FORMAT",
                    advisory="Malformed or invalid telephone number format."
                )

        is_valid = phonenumbers.is_valid_number(parsed)
        if not is_valid:
            return CallerIntelligenceResult(
                raw_input=raw,
                is_valid=False,
                e164_format=phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164) if parsed else None,
                number_type="UNKNOWN",
                reputation_score=65.0,
                verdict="INVALID_FORMAT",
                advisory="Number fails telecom ITU validation checks. Exercise caution."
            )

        e164_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
        nat_fmt = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.NATIONAL)
        region_code = phonenumbers.region_code_for_number(parsed) or country_hint

        # Number type resolution
        num_type_enum = phonenumbers.number_type(parsed)
        type_str = "UNKNOWN"
        if num_type_enum == PhoneNumberType.MOBILE:
            type_str = "MOBILE"
        elif num_type_enum == PhoneNumberType.FIXED_LINE:
            type_str = "FIXED_LINE"
        elif num_type_enum == PhoneNumberType.TOLL_FREE:
            type_str = "TOLL_FREE"
        elif num_type_enum == PhoneNumberType.VOIP:
            type_str = "VOIP"
        elif num_type_enum == PhoneNumberType.PREMIUM_RATE:
            type_str = "PREMIUM_RATE"

        # Carrier and Geographic Region resolution
        carrier_name = carrier.name_for_number(parsed, "en") or "Standard Telecom Provider"
        geo_location = geocoder.description_for_number(parsed, "en") or f"{region_code} Telecom Circle"

        # Check against official institutional registered numbers
        is_registered = False
        reg_org_name = None
        official_helplines: List[str] = []

        clean_digits = re.sub(r"\D", "", e164_fmt)
        for org_key, org_data in OFFICIAL_INSTITUTIONAL_REGISTRY.items():
            for num in org_data["official_numbers"]:
                clean_target = re.sub(r"\D", "", num)
                if clean_digits.endswith(clean_target) or clean_target.endswith(clean_digits):
                    is_registered = True
                    reg_org_name = org_data["display_name"]
                    official_helplines = org_data["official_numbers"]
                    break
            if is_registered:
                break

        # Impersonation & Potential Identity Conflict Check:
        # Separate number parsing metadata from claimed identity and verified identity
        spoofing_suspected = False
        conflict_details = None
        reputation_score = 30.0 # Standard personal neutral baseline
        verdict = "NORMAL_PERSONAL"
        conflict_status = "NO_CONFLICT_UNVERIFIED"
        verified_identity = None
        advisory = f"Standard {type_str.lower()} line registered under {geo_location} ({carrier_name})."

        if is_registered:
            verdict = "VERIFIED_INSTITUTION"
            conflict_status = "VERIFIED_MATCH"
            verified_identity = reg_org_name
            reputation_score = 5.0
            advisory = f"Verified official telephone line of {reg_org_name}."

        elif claimed_organization and claimed_organization.strip():
            claim_norm = claimed_organization.lower().strip()
            # Find which institution they claim to be
            matched_inst = None
            for org_key, org_data in OFFICIAL_INSTITUTIONAL_REGISTRY.items():
                if any(alias in claim_norm for alias in org_data["aliases"]):
                    matched_inst = org_data
                    break

            if matched_inst:
                # The caller claims to be a recognized institution (e.g. SBI, CBI, RBI)
                # But is calling from an unverified mobile SIM or VoIP line!
                if type_str in ["MOBILE", "VOIP", "UNKNOWN"]:
                    spoofing_suspected = True
                    reputation_score = 80.0 # Elevated caution due to unverified channel
                    verdict = "POTENTIAL_IDENTITY_CONFLICT"
                    conflict_status = "POTENTIAL_IDENTITY_CONFLICT"
                    conflict_details = (
                        f"POTENTIAL IDENTITY CONFLICT: Caller claims to represent {matched_inst['display_name']}, "
                        f"but is calling from an unverified {type_str.lower()} line ({nat_fmt}) "
                        f"instead of the institution's official registered helpline ({', '.join(matched_inst['official_numbers'][:2])}). "
                        f"This may indicate an unverified third-party representative, an employee mobile, or caller ID spoofing."
                    )
                    advisory = (
                        f"⚠️ CAUTION: Official representatives of {matched_inst['display_name']} do NOT conduct "
                        f"official business, security checks, or fund verifications from personal mobile numbers. "
                        f"Verify independently through their official channel: {matched_inst['official_numbers'][0]}."
                    )
                    official_helplines = matched_inst["official_numbers"]

        # Check foreign numbers claiming domestic jurisdiction (e.g., +92, +880, +1 calling Indian seniors)
        if region_code != "IN" and not is_registered:
            reputation_score = max(reputation_score, 75.0)
            verdict = "HIGH_RISK_SUSPECT"
            advisory = f"International call originating from {region_code}. Telecom metadata indicates foreign numbering allocation."

        return CallerIntelligenceResult(
            raw_input=raw,
            is_valid=True,
            e164_format=e164_fmt,
            national_format=nat_fmt,
            country_code=region_code,
            carrier=carrier_name,
            geographic_region=geo_location,
            metadata_disclaimer="Carrier and telecom circle metadata reflect ITU numbering plan allocations, not verified physical GPS location or live roaming carrier (MNP and VoIP masking may apply).",
            number_type=type_str, # type: ignore
            claimed_organization=claimed_organization,
            verified_caller_identity=verified_identity,
            is_registered_institution=is_registered,
            registered_organization=reg_org_name,
            official_helplines=official_helplines,
            identity_conflict_status=conflict_status, # type: ignore
            spoofing_suspected=spoofing_suspected,
            spoofing_conflict_details=conflict_details,
            reputation_score=reputation_score,
            verdict=verdict, # type: ignore
            advisory=advisory
        )

caller_service = CallerIntelligenceService()
