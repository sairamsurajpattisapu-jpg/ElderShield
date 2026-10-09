package org.eldershield.companion.data

import android.content.Context
import com.google.gson.Gson
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import okhttp3.*
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody.Companion.toRequestBody
import java.io.IOException
import java.util.concurrent.TimeUnit

class ElderShieldApiClient(private val context: Context) {

    private val prefs = PreferenceManager(context)
    private val gson = Gson()

    private val httpClient = OkHttpClient.Builder()
        .connectTimeout(5, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .writeTimeout(15, TimeUnit.SECONDS)
        .retryOnConnectionFailure(true)
        .build()

    private fun getBaseUrl(): String {
        var url = prefs.serverUrl.trim()
        if (!url.startsWith("http://") && !url.startsWith("https://")) {
            url = "http://$url"
        }
        return url.removeSuffix("/")
    }

    private fun getWsUrl(): String {
        val base = getBaseUrl()
        val wsBase = if (base.startsWith("https://")) {
            base.replace("https://", "wss://")
        } else {
            base.replace("http://", "ws://")
        }
        val apiKey = prefs.apiKey
        return if (apiKey.isNotEmpty()) {
            "$wsBase/ws/live-call?api_key=$apiKey"
        } else {
            "$wsBase/ws/live-call"
        }
    }

    private fun addAuthHeaders(builder: Request.Builder) {
        val key = prefs.apiKey
        if (key.isNotEmpty()) {
            builder.addHeader("X-API-Key", key)
        }
    }

    suspend fun checkHealth(): HealthResponse? = withContext(Dispatchers.IO) {
        try {
            val url = "${getBaseUrl()}/health"
            val request = Request.Builder().url(url).build()
            httpClient.newCall(request).execute().use { response ->
                if (response.isSuccessful) {
                    val body = response.body?.string() ?: return@withContext null
                    return@withContext gson.fromJson(body, HealthResponse::class.java)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
        null
    }

    suspend fun lookupCaller(phoneNumber: String, claimedOrg: String? = null): CallerIntelligenceResult? =
        withContext(Dispatchers.IO) {
            try {
                val url = "${getBaseUrl()}/api/caller-lookup"
                val jsonPayload = gson.toJson(CallerLookupRequest(phoneNumber, claimedOrg))
                val body = jsonPayload.toRequestBody("application/json; charset=utf-8".toMediaType())

                val reqBuilder = Request.Builder().url(url).post(body)
                addAuthHeaders(reqBuilder)

                httpClient.newCall(reqBuilder.build()).execute().use { response ->
                    if (response.isSuccessful) {
                        val responseBody = response.body?.string() ?: return@withContext null
                        return@withContext gson.fromJson(responseBody, CallerIntelligenceResult::class.java)
                    }
                }
            } catch (e: Exception) {
                e.printStackTrace()
            }
            null
        }

    fun createLiveCallWebSocket(listener: WebSocketListener): WebSocket {
        val url = getWsUrl()
        val reqBuilder = Request.Builder().url(url)
        addAuthHeaders(reqBuilder)
        return httpClient.newWebSocket(reqBuilder.build(), listener)
    }
}
