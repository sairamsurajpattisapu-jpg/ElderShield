package org.eldershield.companion.alert

import android.app.NotificationManager
import android.app.PendingIntent
import android.content.Context
import android.content.Intent
import android.media.AudioManager
import android.media.ToneGenerator
import android.net.Uri
import android.os.Build
import android.os.VibrationEffect
import android.os.Vibrator
import android.os.VibratorManager
import android.speech.tts.TextToSpeech
import androidx.core.app.NotificationCompat
import org.eldershield.companion.ElderShieldApp
import org.eldershield.companion.MainActivity
import org.eldershield.companion.data.PreferenceManager
import java.util.Locale

class ElderAlertManager(private val context: Context) {

    private val prefs = PreferenceManager(context)
    private var tts: TextToSpeech? = null
    private var isTtsReady = false

    init {
        tts = TextToSpeech(context.applicationContext) { status ->
            if (status == TextToSpeech.SUCCESS) {
                tts?.language = Locale.ENGLISH
                isTtsReady = true
            }
        }
    }

    fun triggerUrgentAlert(title: String, message: String) {
        // 1. Tactile Vibration Alert for hearing-impaired seniors
        if (prefs.isVibrateEnabled) {
            triggerVibration()
        }

        // 2. Audio Tone Alert
        if (prefs.isSoundEnabled) {
            playWarningTone()
            speakAlertMessage("Warning! Potential scam detected. Hang up the call now.")
        }

        // 3. High-Priority Heads-Up Notification
        sendAlertNotification(title, message)
    }

    private fun triggerVibration() {
        try {
            val pattern = longArrayOf(0, 500, 200, 500, 200, 800)
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
                val vibratorManager = context.getSystemService(Context.VIBRATOR_MANAGER_SERVICE) as VibratorManager
                val vibrator = vibratorManager.defaultVibrator
                vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1))
            } else {
                @Suppress("DEPRECATION")
                val vibrator = context.getSystemService(Context.VIBRATOR_SERVICE) as Vibrator
                if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                    vibrator.vibrate(VibrationEffect.createWaveform(pattern, -1))
                } else {
                    @Suppress("DEPRECATION")
                    vibrator.vibrate(pattern, -1)
                }
            }
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun playWarningTone() {
        try {
            val toneGen = ToneGenerator(AudioManager.STREAM_ALARM, 100)
            toneGen.startTone(ToneGenerator.TONE_CDMA_EMERGENCY_RINGBACK, 1500)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }

    private fun speakAlertMessage(speechText: String) {
        if (isTtsReady && tts != null) {
            try {
                tts?.speak(speechText, TextToSpeech.QUEUE_FLUSH, null, "ElderAlertTTS")
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    private fun sendAlertNotification(title: String, message: String) {
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Intent to launch app
        val openAppIntent = Intent(context, MainActivity::class.java).apply {
            flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TOP
        }
        val pendingOpen = PendingIntent.getActivity(
            context,
            101,
            openAppIntent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        // Action to dial 1930 Cyber Helpline
        val dial1930Intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:1930"))
        val pendingDial = PendingIntent.getActivity(
            context,
            102,
            dial1930Intent,
            PendingIntent.FLAG_UPDATE_CURRENT or PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(context, ElderShieldApp.CHANNEL_ALERTS)
            .setSmallIcon(android.R.drawable.ic_dialog_alert)
            .setContentTitle(title)
            .setContentText(message)
            .setStyle(NotificationCompat.BigTextStyle().bigText(message))
            .setPriority(NotificationCompat.PRIORITY_MAX)
            .setCategory(NotificationCompat.CATEGORY_ALARM)
            .setContentIntent(pendingOpen)
            .addAction(android.R.drawable.ic_menu_call, "CALL 1930 HELPLINE", pendingDial)
            .setAutoCancel(true)
            .build()

        notificationManager.notify(2001, notification)
    }

    fun shutdown() {
        try {
            tts?.stop()
            tts?.shutdown()
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
