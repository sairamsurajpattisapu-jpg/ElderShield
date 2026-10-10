package org.eldershield.companion.service

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationManager
import android.app.PendingIntent
import android.app.Service
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.os.Build
import android.os.IBinder
import android.util.Base64
import androidx.core.app.NotificationCompat
import androidx.core.content.ContextCompat
import com.google.gson.Gson
import kotlinx.coroutines.*
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.eldershield.companion.ElderShieldApp
import org.eldershield.companion.MainActivity
import org.eldershield.companion.alert.ElderAlertManager
import org.eldershield.companion.data.*

/**
 * Foreground Service for Active Acoustic Scam Protection.
 *
 * Supported OS Capabilities & Architecture:
 * - Runs as a Foreground Service with FOREGROUND_SERVICE_MICROPHONE on Android 14+ (API 34).
 * - Implements AudioRecord capture at 16,000 Hz 16-bit Mono Little-Endian PCM.
 * - Streams audio frames to ElderShield live WebSocket pipeline (/ws/live-call).
 * - Implements truthful state tracking (STOPPED, STARTING, CONNECTING, LIVE_PROTECTED, RECONNECTING, DEGRADED, FAILED).
 * - Implements resilient WebSocket reconnection with bounded exponential backoff.
 * - Receives immediate progressive risk updates and triggers multi-modal accessible warnings.
 *
 * Technical Restriction & Practical Solution:
 * - Android 9/10+ prohibits arbitrary third-party apps from capturing raw cellular downlink audio
 *   via MediaRecorder.AudioSource.VOICE_CALL for user privacy and wiretapping compliance.
 * - Practical supported implementation: 'Speakerphone Protection Mode'.
 *   When the senior places the suspicious call on speakerphone (or during WhatsApp audio calls
 *   or doorstep interactions), the microphone captures the acoustic output from the phone speaker.
 */
class ElderShieldProtectionService : Service() {

    companion object {
        const val ACTION_START = "org.eldershield.action.START_PROTECTION"
        const val ACTION_STOP = "org.eldershield.action.STOP_PROTECTION"
        const val ACTION_RISK_UPDATE = "org.eldershield.action.RISK_UPDATE"
        const val ACTION_WARNING = "org.eldershield.action.WARNING"
        const val ACTION_STATE_CHANGED = "org.eldershield.action.STATE_CHANGED"

        const val EXTRA_PROTECTION_STATE = "extra_protection_state"
        const val EXTRA_STATE_MESSAGE = "extra_state_message"
        const val EXTRA_RETRY_ATTEMPT = "extra_retry_attempt"
        const val EXTRA_RISK_LEVEL = "extra_risk_level"
        const val EXTRA_RISK_SCORE = "extra_risk_score"
        const val EXTRA_WARNING_TITLE = "extra_warning_title"
        const val EXTRA_WARNING_MESSAGE = "extra_warning_message"
        const val EXTRA_LAST_TEXT = "extra_last_text"

        const val MAX_RETRY_ATTEMPTS = 5
        private const val SAMPLE_RATE = 16000
        private const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        private const val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
        private const val NOTIFICATION_ID = 1001

        var isRunning = false
            private set

        var currentState = ProtectionState.STOPPED
            private set

        var currentStatusMessage = "Protection stopped"
            private set

        fun calculateBackoffMs(attempt: Int): Long {
            val exponent = minOf(maxOf(0, attempt - 1), 4)
            return minOf(1000L * (1L shl exponent), 16000L)
        }
    }

    private val serviceScope = CoroutineScope(Dispatchers.IO + SupervisorJob())
    private var audioRecord: AudioRecord? = null
    private var isRecording = false
    private var audioCaptureJob: Job? = null
    private var webSocket: WebSocket? = null
    private var retryAttempt = 0
    private var reconnectJob: Job? = null
    private val gson = Gson()
    private lateinit var alertManager: ElderAlertManager
    private lateinit var apiClient: ElderShieldApiClient

    override fun onCreate() {
        super.onCreate()
        alertManager = ElderAlertManager(applicationContext)
        apiClient = ElderShieldApiClient(applicationContext)
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            ACTION_START -> startProtection()
            ACTION_STOP -> stopProtection()
            else -> startProtection()
        }
        return START_STICKY
    }

    private fun updateProtectionState(state: ProtectionState, message: String, retryCount: Int = 0) {
        currentState = state
        currentStatusMessage = message

        val intent = Intent(ACTION_STATE_CHANGED).apply {
            putExtra(EXTRA_PROTECTION_STATE, state.name)
            putExtra(EXTRA_STATE_MESSAGE, message)
            putExtra(EXTRA_RETRY_ATTEMPT, retryCount)
            setPackage(packageName)
        }
        sendBroadcast(intent)
        updateForegroundNotificationText(message)
    }

    private fun startProtection() {
        if (isRunning) return

        if (ContextCompat.checkSelfPermission(this, android.Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED) {
            android.util.Log.e("ElderShieldService", "RECORD_AUDIO permission not granted; stopping service")
            updateProtectionState(ProtectionState.FAILED, "Microphone permission required")
            stopSelf()
            return
        }

        try {
            val notification = buildForegroundNotification("Starting protection...")
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
                androidx.core.app.ServiceCompat.startForeground(
                    this,
                    NOTIFICATION_ID,
                    notification,
                    android.content.pm.ServiceInfo.FOREGROUND_SERVICE_TYPE_MICROPHONE
                )
            } else {
                startForeground(NOTIFICATION_ID, notification)
            }
            isRunning = true
            retryAttempt = 0
            updateProtectionState(ProtectionState.STARTING, "Initializing protection audio...")
            initWebSocketAndStreaming()
        } catch (e: Exception) {
            android.util.Log.e("ElderShieldService", "Failed to start foreground service: ${e.message}", e)
            isRunning = false
            updateProtectionState(ProtectionState.FAILED, "Failed to start service: ${e.message}")
            stopSelf()
        }
    }

    private fun stopProtection() {
        isRunning = false
        isRecording = false
        audioCaptureJob?.cancel()
        audioCaptureJob = null
        reconnectJob?.cancel()
        reconnectJob = null
        retryAttempt = 0

        try {
            audioRecord?.stop()
            audioRecord?.release()
            audioRecord = null
        } catch (e: Exception) {
            e.printStackTrace()
        }

        try {
            webSocket?.close(1000, "User stopped protection")
            webSocket = null
        } catch (e: Exception) {
            e.printStackTrace()
        }

        updateProtectionState(ProtectionState.STOPPED, "Protection paused")
        stopForeground(STOP_FOREGROUND_REMOVE)
        stopSelf()
    }

    private fun initWebSocketAndStreaming() {
        val connectingMsg = if (retryAttempt > 0) {
            "Reconnecting to protection server (attempt $retryAttempt/$MAX_RETRY_ATTEMPTS)..."
        } else {
            "Connecting to ElderShield security server..."
        }
        updateProtectionState(ProtectionState.CONNECTING, connectingMsg, retryAttempt)

        val wsListener = object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, response: Response) {
                webSocket = ws
                retryAttempt = 0
                // When connected, wait for session_ready handshake or transition to active
                updateProtectionState(ProtectionState.LIVE_PROTECTED, "Active Protection: Listening for scam signs")
                startAudioCapture()
            }

            override fun onMessage(ws: WebSocket, text: String) {
                handleIncomingWsMessage(text)
            }

            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                android.util.Log.w("ElderShieldService", "WebSocket connection failure: ${t.message}")
                webSocket = null

                if (!isRunning) return

                // Temporary pause audio capture while disconnected
                isRecording = false
                audioCaptureJob?.cancel()
                audioCaptureJob = null
                try {
                    audioRecord?.stop()
                    audioRecord?.release()
                    audioRecord = null
                } catch (e: Exception) {
                    e.printStackTrace()
                }

                if (retryAttempt < MAX_RETRY_ATTEMPTS) {
                    retryAttempt++
                    val backoffMs = calculateBackoffMs(retryAttempt)
                    val retryMsg = "Connection interrupted. Reconnecting in ${backoffMs / 1000}s (attempt $retryAttempt/$MAX_RETRY_ATTEMPTS)..."
                    updateProtectionState(ProtectionState.RECONNECTING, retryMsg, retryAttempt)

                    reconnectJob?.cancel()
                    reconnectJob = serviceScope.launch {
                        delay(backoffMs)
                        if (isRunning) {
                            initWebSocketAndStreaming()
                        }
                    }
                } else {
                    val offlineMsg = "Protection paused: Server unreachable after $MAX_RETRY_ATTEMPTS attempts."
                    updateProtectionState(ProtectionState.DEGRADED, offlineMsg, retryAttempt)
                    alertManager.triggerTechnicalAlert(
                        "PROTECTION OFFLINE",
                        "Cannot connect to security server. Tap ElderShield to retry."
                    )
                }
            }

            override fun onClosed(ws: WebSocket, code: Int, reason: String) {
                if (isRunning && code != 1000) {
                    onFailure(ws, Exception("Closed by server: $reason (code $code)"), null)
                }
            }
        }

        try {
            webSocket = apiClient.createLiveCallWebSocket(wsListener)
        } catch (e: Exception) {
            android.util.Log.e("ElderShieldService", "Error initiating WebSocket: ${e.message}", e)
        }
    }

    @SuppressLint("MissingPermission")
    private fun startAudioCapture() {
        if (isRecording || audioCaptureJob?.isActive == true) return
        isRecording = true

        audioCaptureJob = serviceScope.launch {
            val minBufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)
            val internalBufferSize = maxOf(minBufferSize * 4, 16000)
            val chunkSize = 3200 // ~100ms frames of 16kHz 16-bit mono PCM

            try {
                audioRecord = AudioRecord(
                    MediaRecorder.AudioSource.MIC,
                    SAMPLE_RATE,
                    CHANNEL_CONFIG,
                    AUDIO_FORMAT,
                    internalBufferSize
                )

                if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                    android.util.Log.e("ElderShieldService", "AudioRecord failed to initialize! Stopping protection.")
                    updateProtectionState(ProtectionState.FAILED, "Microphone initialization failed")
                    stopProtection()
                    return@launch
                }

                audioRecord?.startRecording()

                val audioBuffer = ByteArray(chunkSize)
                var sequenceId = 0

                while (isRecording && isRunning && currentState == ProtectionState.LIVE_PROTECTED) {
                    val bytesRead = audioRecord?.read(audioBuffer, 0, audioBuffer.size) ?: -1
                    if (bytesRead > 0 && webSocket != null) {
                        sequenceId++
                        val base64Chunk = Base64.encodeToString(audioBuffer, 0, bytesRead, Base64.NO_WRAP)
                        val captureTime = android.os.SystemClock.elapsedRealtime()
                        val payload = mapOf(
                            "type" to "audio_chunk",
                            "sequence_id" to sequenceId,
                            "chunk" to base64Chunk,
                            "client_time_ms" to captureTime
                        )
                        webSocket?.send(gson.toJson(payload))
                    }
                }
            } catch (e: Exception) {
                android.util.Log.e("ElderShieldService", "Audio capture error: ${e.message}", e)
            } finally {
                isRecording = false
                try {
                    audioRecord?.stop()
                    audioRecord?.release()
                    audioRecord = null
                } catch (e: Exception) {
                    e.printStackTrace()
                }
            }
        }
    }

    private fun handleIncomingWsMessage(text: String) {
        try {
            val json = gson.fromJson(text, Map::class.java)
            val msgType = json["type"] as? String
            val timing = json["timing"] as? Map<*, *>

            // Log correlated pipeline latency
            if (timing != null) {
                val clientTime = (timing["client_capture_time_ms"] as? Number)?.toLong()
                if (clientTime != null && clientTime > 0) {
                    val clientRtt = android.os.SystemClock.elapsedRealtime() - clientTime
                    android.util.Log.i(
                        "ElderShieldTiming",
                        "End-to-End Client Roundtrip: ${clientRtt}ms | Server ASR: ${timing["server_receipt_to_transcript_ms"]}ms | Server Risk: ${timing["transcript_to_risk_decision_ms"]}ms"
                    )
                }
            }

            when (msgType) {
                "session_ready" -> {
                    retryAttempt = 0
                    updateProtectionState(ProtectionState.LIVE_PROTECTED, "Active Protection: Listening for scam signs")
                    if (!isRecording) {
                        startAudioCapture()
                    }
                }

                "risk_update" -> {
                    val riskLevel = json["risk_level"] as? String ?: "LOW_RISK"
                    val riskScore = (json["risk_score"] as? Number)?.toDouble() ?: 0.0
                    val speechText = json["text"] as? String ?: ""

                    // Broadcast to UI
                    val intent = Intent(ACTION_RISK_UPDATE).apply {
                        putExtra(EXTRA_RISK_LEVEL, riskLevel)
                        putExtra(EXTRA_RISK_SCORE, riskScore)
                        putExtra(EXTRA_LAST_TEXT, speechText)
                        setPackage(packageName)
                    }
                    sendBroadcast(intent)
                }

                "warning" -> {
                    val title = json["title"] as? String ?: "SCAM ALERT"
                    val message = json["message"] as? String ?: "Disconnect immediately!"

                    // Broadcast to UI
                    val intent = Intent(ACTION_WARNING).apply {
                        putExtra(EXTRA_WARNING_TITLE, title)
                        putExtra(EXTRA_WARNING_MESSAGE, message)
                        setPackage(packageName)
                    }
                    sendBroadcast(intent)

                    // Fire vibration, tone, and speech alert
                    alertManager.triggerUrgentAlert(title, message)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun updateForegroundNotificationText(contentText: String) {
        if (!isRunning) return
        try {
            val notification = buildForegroundNotification(contentText)
            val notificationManager = getSystemService(Context.NOTIFICATION_SERVICE) as? NotificationManager
            notificationManager?.notify(NOTIFICATION_ID, notification)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun buildForegroundNotification(contentText: String): Notification {
        val openIntent = Intent(this, MainActivity::class.java)
        val pendingOpen = PendingIntent.getActivity(
            this,
            0,
            openIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, ElderShieldApp.CHANNEL_PROTECTION)
            .setSmallIcon(android.R.drawable.ic_lock_idle_lock)
            .setContentTitle("ElderShield Scam Protection")
            .setContentText(contentText)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setContentIntent(pendingOpen)
            .setOngoing(true)
            .build()
    }

    override fun onDestroy() {
        super.onDestroy()
        stopProtection()
        alertManager.shutdown()
        serviceScope.cancel()
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
