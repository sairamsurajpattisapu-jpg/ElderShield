package org.eldershield.companion.service

import android.os.Build
import android.telecom.Call
import android.telecom.CallScreeningService
import androidx.annotation.RequiresApi
import kotlinx.coroutines.*
import org.eldershield.companion.alert.ElderAlertManager
import org.eldershield.companion.data.ElderShieldApiClient
import org.eldershield.companion.data.PreferenceManager

/**
 * Android CallScreeningService Implementation.
 *
 * Supported OS Capabilities:
 * - Intercepts incoming call signaling events before the senior's phone rings.
 * - Extracts caller phone number from Call.Details handle.
 * - Queries ElderShield Caller Intelligence service for institutional spoofing conflict detection.
 * - Automatically rejects, disallows, or silences malicious calls.
 *
 * Known Architectural Limitation:
 * - CallScreeningService operates solely on telecom metadata (phone number / handle).
 *   Android security architecture does NOT provide call audio streams to CallScreeningService.
 *   In-call acoustic analysis is performed via ElderShieldProtectionService (Speakerphone Protection Mode).
 */
@RequiresApi(Build.VERSION_CODES.N)
class ElderShieldCallScreeningService : CallScreeningService() {

    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())

    override fun onScreenCall(details: Call.Details) {
        val prefs = PreferenceManager(applicationContext)
        if (!prefs.isCallScreeningEnabled) {
            respondToCall(details, CallResponse.Builder().build())
            return
        }

        val rawHandle = details.handle?.schemeSpecificPart ?: ""
        if (rawHandle.isEmpty()) {
            respondToCall(details, CallResponse.Builder().build())
            return
        }

        val apiClient = ElderShieldApiClient(applicationContext)
        val alertManager = ElderAlertManager(applicationContext)

        serviceScope.launch {
            try {
                // Strict 4-second timeout to comply with Android Telecom framework response bounds
                val result = withTimeoutOrNull(4000) {
                    apiClient.lookupCaller(rawHandle)
                }

                if (result != null && (result.spoofingSuspected || result.reputationScore >= 80.0)) {
                    // Block and silence confirmed malicious/spoofed call
                    val response = CallResponse.Builder()
                        .setDisallowCall(true)
                        .setRejectCall(true)
                        .setSilenceCall(true)
                        .setSkipCallLog(false)
                        .setSkipNotification(false)
                        .build()

                    respondToCall(details, response)

                    // Dispatch urgent elder-friendly warning with vibration and voice
                    val advisory = result.advisory.ifEmpty {
                        "Caller claims institutional identity but originates from unverified mobile number."
                    }
                    alertManager.triggerUrgentAlert(
                        title = "FRAUD CALL BLOCKED: ${result.claimedOrganization ?: "Unknown"}",
                        message = "ElderShield intercepted a suspected scam call from $rawHandle. $advisory"
                    )
                } else {
                    // Allow call to proceed
                    respondToCall(details, CallResponse.Builder().build())
                }
            } catch (e: Exception) {
                // Fail-safe: never hang the phone call on network failure
                respondToCall(details, CallResponse.Builder().build())
            }
        }
    }

    override fun onDestroy() {
        super.onDestroy()
        serviceScope.cancel()
    }
}
