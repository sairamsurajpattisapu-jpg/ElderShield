package org.eldershield.companion.data

import com.google.gson.annotations.SerializedName

enum class ProtectionState {
    STOPPED,
    STARTING,
    CAPTURE_ACTIVE,
    CONNECTING,
    LIVE_PROTECTED,
    RECONNECTING,
    DEGRADED,
    FAILED
}

data class HealthResponse(
    val status: String,
    val service: String,
    val version: String,
    val environment: String?
)

data class CallerLookupRequest(
    @SerializedName("phone_number") val phoneNumber: String,
    @SerializedName("claimed_organization") val claimedOrganization: String? = null,
    @SerializedName("country_hint") val countryHint: String = "IN"
)

data class CallerIntelligenceResult(
    @SerializedName("raw_input") val rawInput: String,
    @SerializedName("is_valid") val isValid: Boolean,
    @SerializedName("e164_format") val e164Format: String?,
    @SerializedName("national_format") val nationalFormat: String?,
    @SerializedName("carrier") val carrier: String?,
    @SerializedName("geographic_region") val geographicRegion: String?,
    @SerializedName("number_type") val numberType: String,
    @SerializedName("claimed_organization") val claimedOrganization: String?,
    @SerializedName("verified_caller_identity") val verifiedCallerIdentity: String?,
    @SerializedName("is_registered_institution") val isRegisteredInstitution: Boolean,
    @SerializedName("registered_organization") val registeredOrganization: String?,
    @SerializedName("identity_conflict_status") val identityConflictStatus: String,
    @SerializedName("spoofing_suspected") val spoofingSuspected: Boolean,
    @SerializedName("reputation_score") val reputationScore: Double,
    @SerializedName("caller_authenticated") val callerAuthenticated: Boolean = false,
    @SerializedName("authentication_notice") val authenticationNotice: String? = null,
    @SerializedName("caller_classification") val callerClassification: String? = null,
    @SerializedName("number_format_validity") val numberFormatValidity: String? = null,
    @SerializedName("registry_matching") val registryMatching: String? = null,
    @SerializedName("caller_reputation_status") val callerReputationStatus: String? = null,
    val verdict: String,
    val advisory: String
)

data class EvidenceItem(
    @SerializedName("turn_number") val turnNumber: Int,
    @SerializedName("exact_quote") val exactQuote: String,
    @SerializedName("signal_category") val signalCategory: String,
    val explanation: String,
    val severity: String
)

data class RiskAssessment(
    @SerializedName("risk_level") val riskLevel: String,
    @SerializedName("risk_score") val riskScore: Double,
    val decision: String,
    val evidence: List<EvidenceItem>,
    val reasons: List<String>,
    @SerializedName("recommended_action") val recommendedAction: String,
    @SerializedName("insufficient_evidence") val insufficientEvidence: Boolean
)

data class WarningEvent(
    val severity: String,
    val title: String,
    val message: String,
    @SerializedName("evidence_quotes") val evidenceQuotes: List<String>?,
    val timestamp: Double
)

data class RiskUpdateEvent(
    @SerializedName("session_id") val sessionId: String,
    @SerializedName("turn_number") val turnNumber: Int,
    val speaker: String,
    val text: String,
    @SerializedName("risk_level") val riskLevel: String,
    @SerializedName("risk_score") val riskScore: Double,
    val decision: String,
    val reasons: List<String>
)
