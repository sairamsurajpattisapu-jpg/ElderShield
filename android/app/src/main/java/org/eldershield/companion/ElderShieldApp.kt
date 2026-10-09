package org.eldershield.companion

import android.app.Application
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build

class ElderShieldApp : Application() {

    companion object {
        const val CHANNEL_PROTECTION = "eldershield_protection_service"
        const val CHANNEL_ALERTS = "eldershield_fraud_alerts"
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val notificationManager = getSystemService(NotificationManager::class.java)

            // Low-priority persistent channel for foreground protection status
            val protectionChannel = NotificationChannel(
                CHANNEL_PROTECTION,
                "ElderShield Active Shield",
                NotificationManager.IMPORTANCE_LOW
            ).apply {
                description = "Notifies when ElderShield is actively monitoring calls for scam indicators"
            }

            // High-priority urgent channel for fraud warnings with vibration and sound
            val alertsChannel = NotificationChannel(
                CHANNEL_ALERTS,
                "ElderShield Fraud Alerts",
                NotificationManager.IMPORTANCE_HIGH
            ).apply {
                description = "Urgent alerts when a phone scam, digital arrest, or impersonation attempt is detected"
                enableVibration(true)
                vibrationPattern = longArrayOf(0, 500, 200, 500, 200, 800)
            }

            notificationManager.createNotificationChannel(protectionChannel)
            notificationManager.createNotificationChannel(alertsChannel)
        }
    }
}
