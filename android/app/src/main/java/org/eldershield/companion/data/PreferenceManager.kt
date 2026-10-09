package org.eldershield.companion.data

import android.content.Context
import android.content.SharedPreferences
import org.eldershield.companion.BuildConfig
import java.net.URI

class PreferenceManager(context: Context) {

    private val prefs: SharedPreferences =
        context.getSharedPreferences("eldershield_prefs", Context.MODE_PRIVATE)

    companion object {
        private const val KEY_SERVER_URL = "server_url"
        private const val KEY_API_KEY = "api_key"
        private const val KEY_VIBRATE = "vibrate_enabled"
        private const val KEY_SOUND = "sound_enabled"
        private const val KEY_CALL_SCREENING = "call_screening_enabled"

        /**
         * Resolves default base URL:
         * Uses BuildConfig.DEFAULT_SERVER_URL if configured, otherwise falls back to emulator loopback.
         */
        val DEFAULT_SERVER_URL: String
            get() = BuildConfig.DEFAULT_SERVER_URL.ifEmpty { "http://10.0.2.2:8000" }

        /**
         * Validates a candidate server URL.
         * Returns (isValid, errorMessage)
         */
        fun validateServerUrl(rawUrl: String): Pair<Boolean, String?> {
            val trimmed = rawUrl.trim()
            if (trimmed.isEmpty()) {
                return Pair(false, "Server URL cannot be empty")
            }
            val formatted = if (!trimmed.startsWith("http://") && !trimmed.startsWith("https://")) {
                "http://$trimmed"
            } else {
                trimmed
            }
            return try {
                val uri = URI(formatted)
                val host = uri.host
                if (host.isNullOrEmpty()) {
                    Pair(false, "Server URL must contain a valid host name or IP address")
                } else if (BuildConfig.IS_PRODUCTION && formatted.startsWith("http://") && !host.equals("127.0.0.1") && !host.equals("localhost") && !host.equals("10.0.2.2")) {
                    Pair(false, "Production server connection requires a secure HTTPS endpoint")
                } else {
                    Pair(true, null)
                }
            } catch (e: Exception) {
                Pair(false, "Malformed server URL format: ${e.message}")
            }
        }
    }

    var serverUrl: String
        get() = prefs.getString(KEY_SERVER_URL, DEFAULT_SERVER_URL) ?: DEFAULT_SERVER_URL
        set(value) = prefs.edit().putString(KEY_SERVER_URL, value.trim()).apply()

    var apiKey: String
        get() = prefs.getString(KEY_API_KEY, "") ?: ""
        set(value) = prefs.edit().putString(KEY_API_KEY, value.trim()).apply()

    var isVibrateEnabled: Boolean
        get() = prefs.getBoolean(KEY_VIBRATE, true)
        set(value) = prefs.edit().putBoolean(KEY_VIBRATE, value).apply()

    var isSoundEnabled: Boolean
        get() = prefs.getBoolean(KEY_SOUND, true)
        set(value) = prefs.edit().putBoolean(KEY_SOUND, value).apply()

    var isCallScreeningEnabled: Boolean
        get() = prefs.getBoolean(KEY_CALL_SCREENING, true)
        set(value) = prefs.edit().putBoolean(KEY_CALL_SCREENING, value).apply()
}
