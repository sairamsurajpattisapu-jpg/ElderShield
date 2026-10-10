package org.eldershield.companion

import android.Manifest
import android.app.role.RoleManager
import android.content.*
import android.content.pm.PackageManager
import android.graphics.Color
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import androidx.lifecycle.lifecycleScope
import kotlinx.coroutines.launch
import org.eldershield.companion.data.ElderShieldApiClient
import org.eldershield.companion.data.PreferenceManager
import org.eldershield.companion.databinding.ActivityMainBinding
import org.eldershield.companion.service.ElderShieldProtectionService

class MainActivity : AppCompatActivity() {

    private lateinit var binding: ActivityMainBinding
    private lateinit var apiClient: ElderShieldApiClient
    private lateinit var prefs: PreferenceManager

    private val permissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestMultiplePermissions()
    ) { permissions ->
        val recordAudioGranted = permissions[Manifest.permission.RECORD_AUDIO] == true
        if (recordAudioGranted) {
            toggleProtectionService()
        } else {
            Toast.makeText(
                this,
                "Microphone permission is required for live scam protection",
                Toast.LENGTH_LONG
            ).show()
        }
    }

    private val roleRequestLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { /* Role request result handling */ }

    private val serviceReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context?, intent: Intent?) {
            when (intent?.action) {
                ElderShieldProtectionService.ACTION_STATE_CHANGED -> {
                    val state = intent.getStringExtra(ElderShieldProtectionService.EXTRA_PROTECTION_STATE) ?: "STOPPED"
                    val message = intent.getStringExtra(ElderShieldProtectionService.EXTRA_STATE_MESSAGE)
                    val attempt = intent.getIntExtra(ElderShieldProtectionService.EXTRA_RETRY_ATTEMPT, 0)
                    updateProtectionStateUi(state, message, attempt)
                }
                ElderShieldProtectionService.ACTION_RISK_UPDATE -> {
                    val riskLevel = intent.getStringExtra(ElderShieldProtectionService.EXTRA_RISK_LEVEL) ?: "LOW_RISK"
                    val riskScore = intent.getDoubleExtra(ElderShieldProtectionService.EXTRA_RISK_SCORE, 0.0)
                    updateRiskUi(riskLevel, riskScore)
                }
                ElderShieldProtectionService.ACTION_WARNING -> {
                    val title = intent.getStringExtra(ElderShieldProtectionService.EXTRA_WARNING_TITLE) ?: "SCAM ALERT"
                    val message = intent.getStringExtra(ElderShieldProtectionService.EXTRA_WARNING_MESSAGE) ?: "Disconnect now!"
                    displayScamAlert(title, message)
                }
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        apiClient = ElderShieldApiClient(this)
        prefs = PreferenceManager(this)

        setupListeners()
        updateShieldStatusUi()
        requestCallScreeningRoleIfAvailable()

        // Register broadcast receiver for live service updates
        val filter = IntentFilter().apply {
            addAction(ElderShieldProtectionService.ACTION_STATE_CHANGED)
            addAction(ElderShieldProtectionService.ACTION_RISK_UPDATE)
            addAction(ElderShieldProtectionService.ACTION_WARNING)
        }
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            registerReceiver(serviceReceiver, filter, Context.RECEIVER_NOT_EXPORTED)
        } else {
            @Suppress("DEPRECATION")
            registerReceiver(serviceReceiver, filter)
        }
    }

    private fun setupListeners() {
        // Toggle Active Protection
        binding.btnToggleProtection.setOnClickListener {
            checkPermissionsAndToggle()
        }

        // Settings Button
        binding.btnSettings.setOnClickListener {
            val intent = Intent(this, SettingsActivity::class.java)
            startActivity(intent)
        }

        // Emergency 1930 Helpline Speed-Dial
        binding.btnHelpline1930.setOnClickListener {
            val dialIntent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:1930"))
            startActivity(dialIntent)
        }

        // Caller Lookup
        binding.btnCheckCaller.setOnClickListener {
            performCallerLookup()
        }

        // Dismiss Alert
        binding.btnDismissAlert.setOnClickListener {
            binding.cardAlert.visibility = View.GONE
            updateShieldStatusUi()
        }
    }

    private fun checkPermissionsAndToggle() {
        val permissionsToRequest = mutableListOf<String>()

        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO)
            != PackageManager.PERMISSION_GRANTED) {
            permissionsToRequest.add(Manifest.permission.RECORD_AUDIO)
        }

        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                != PackageManager.PERMISSION_GRANTED) {
                permissionsToRequest.add(Manifest.permission.POST_NOTIFICATIONS)
            }
        }

        if (permissionsToRequest.isNotEmpty()) {
            permissionLauncher.launch(permissionsToRequest.toTypedArray())
        } else {
            toggleProtectionService()
        }
    }

    private fun toggleProtectionService() {
        val intent = Intent(this, ElderShieldProtectionService::class.java)
        if (ElderShieldProtectionService.isRunning) {
            intent.action = ElderShieldProtectionService.ACTION_STOP
            startService(intent)
        } else {
            intent.action = ElderShieldProtectionService.ACTION_START
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
                startForegroundService(intent)
            } else {
                startService(intent)
            }
        }
        binding.root.postDelayed({ updateShieldStatusUi() }, 150)
    }

    private fun updateProtectionStateUi(stateName: String, message: String?, retryAttempt: Int) {
        when (stateName) {
            "LIVE_PROTECTED" -> {
                binding.tvStatusTitle.text = getString(R.string.shield_active)
                binding.tvStatusSubtitle.text = getString(R.string.status_monitoring)
                binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.status_green_text))
                binding.tvStatusSubtitle.setTextColor(ContextCompat.getColor(this, R.color.status_green_text))
                binding.cardStatus.setBackgroundResource(R.drawable.bg_status_box)
                binding.ivShieldIcon.imageTintList =
                    ContextCompat.getColorStateList(this, R.color.status_green_text)

                binding.btnToggleProtection.text = getString(R.string.btn_stop_protection)
                binding.btnToggleProtection.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.btn_stop)

                binding.tvMicBadge.text = "Mic: Listening"
                binding.tvMicBadge.setTextColor(ContextCompat.getColor(this, R.color.status_green_text))
                binding.tvEngineBadge.text = "Scam Engine: Active"
                binding.dotEngineStatus.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.status_green_text)
            }
            "STARTING", "CONNECTING" -> {
                binding.tvStatusTitle.text = "CONNECTING..."
                binding.tvStatusSubtitle.text = message ?: "Connecting to ElderShield security server..."
                binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.status_amber_text))
                binding.tvStatusSubtitle.setTextColor(ContextCompat.getColor(this, R.color.status_amber_text))
                binding.cardStatus.setBackgroundResource(R.drawable.bg_status_amber)
                binding.ivShieldIcon.imageTintList =
                    ContextCompat.getColorStateList(this, R.color.status_amber_text)

                binding.btnToggleProtection.text = getString(R.string.btn_stop_protection)
                binding.btnToggleProtection.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.btn_stop)

                binding.tvMicBadge.text = "Mic: Ready"
                binding.tvMicBadge.setTextColor(ContextCompat.getColor(this, R.color.text_secondary))
                binding.tvEngineBadge.text = "Connecting..."
                binding.dotEngineStatus.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.status_amber_text)
            }
            "RECONNECTING" -> {
                binding.tvStatusTitle.text = "RECONNECTING..."
                binding.tvStatusSubtitle.text = message ?: "Reconnecting to server (attempt $retryAttempt/5)..."
                binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.status_amber_text))
                binding.tvStatusSubtitle.setTextColor(ContextCompat.getColor(this, R.color.status_amber_text))
                binding.cardStatus.setBackgroundResource(R.drawable.bg_status_amber)
                binding.ivShieldIcon.imageTintList =
                    ContextCompat.getColorStateList(this, R.color.status_amber_text)

                binding.btnToggleProtection.text = getString(R.string.btn_stop_protection)
                binding.btnToggleProtection.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.btn_stop)

                binding.tvMicBadge.text = "Mic: Retrying"
                binding.tvMicBadge.setTextColor(ContextCompat.getColor(this, R.color.status_amber_text))
                binding.tvEngineBadge.text = "Reconnecting..."
                binding.dotEngineStatus.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.status_amber_text)
            }
            "DEGRADED", "FAILED" -> {
                binding.tvStatusTitle.text = "PROTECTION OFFLINE"
                binding.tvStatusSubtitle.text = message ?: "Server unreachable. Tap below to retry."
                binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.status_red_text))
                binding.tvStatusSubtitle.setTextColor(ContextCompat.getColor(this, R.color.status_red_text))
                binding.cardStatus.setBackgroundResource(R.drawable.bg_status_red)
                binding.ivShieldIcon.imageTintList =
                    ContextCompat.getColorStateList(this, R.color.status_red_text)

                binding.btnToggleProtection.text = "RETRY PROTECTION"
                binding.btnToggleProtection.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.btn_start)

                binding.tvMicBadge.text = "Mic: Off"
                binding.tvMicBadge.setTextColor(ContextCompat.getColor(this, R.color.text_secondary))
                binding.tvEngineBadge.text = "Server Offline"
                binding.dotEngineStatus.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.status_red_text)
            }
            else -> { // STOPPED
                binding.tvStatusTitle.text = getString(R.string.shield_inactive)
                binding.tvStatusSubtitle.text = getString(R.string.status_paused)
                binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.text_primary))
                binding.tvStatusSubtitle.setTextColor(ContextCompat.getColor(this, R.color.text_secondary))
                binding.cardStatus.setBackgroundResource(R.drawable.bg_elder_card)
                binding.ivShieldIcon.imageTintList =
                    ContextCompat.getColorStateList(this, R.color.primary)

                binding.btnToggleProtection.text = getString(R.string.btn_start_protection)
                binding.btnToggleProtection.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.btn_start)

                binding.tvMicBadge.text = "Mic: Standby"
                binding.tvMicBadge.setTextColor(ContextCompat.getColor(this, R.color.text_secondary))
                binding.tvEngineBadge.text = "Engine: Standby"
                binding.dotEngineStatus.backgroundTintList =
                    ContextCompat.getColorStateList(this, R.color.text_muted)
            }
        }
    }

    private fun updateShieldStatusUi() {
        val state = ElderShieldProtectionService.currentState.name
        val msg = ElderShieldProtectionService.currentStatusMessage
        updateProtectionStateUi(state, msg, 0)
    }

    private fun updateRiskUi(riskLevel: String, score: Double) {
        when (riskLevel) {
            "HIGH_RISK" -> {
                binding.tvStatusTitle.text = "HIGH RISK DETECTED"
                binding.tvStatusSubtitle.text = "Manipulative scam tactics detected on this call."
                binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.high_risk_red))
                binding.tvStatusSubtitle.setTextColor(ContextCompat.getColor(this, R.color.high_risk_red))
                binding.cardStatus.setBackgroundResource(R.drawable.bg_status_red)
                binding.ivShieldIcon.imageTintList =
                    ContextCompat.getColorStateList(this, R.color.high_risk_red)
            }
            "SUSPICIOUS" -> {
                binding.tvStatusTitle.text = "CAUTION: SUSPICIOUS CALL"
                binding.tvStatusSubtitle.text = "Caller is demanding urgency or credentials."
                binding.tvStatusTitle.setTextColor(ContextCompat.getColor(this, R.color.suspicious_amber))
                binding.tvStatusSubtitle.setTextColor(ContextCompat.getColor(this, R.color.suspicious_amber))
                binding.cardStatus.setBackgroundResource(R.drawable.bg_status_amber)
                binding.ivShieldIcon.imageTintList =
                    ContextCompat.getColorStateList(this, R.color.suspicious_amber)
            }
            else -> {
                updateShieldStatusUi()
            }
        }
    }

    private fun displayScamAlert(title: String, message: String) {
        val formattedTitle = if (title.contains("OTP", ignoreCase = true) || message.contains("OTP", ignoreCase = true)) {
            "STOP — DO NOT SHARE YOUR OTP"
        } else {
            title
        }
        val formattedMessage = if (title.contains("OTP", ignoreCase = true) || message.contains("OTP", ignoreCase = true)) {
            "Never tell anyone your verification code. If someone is pressuring you, stop the conversation and verify their identity independently."
        } else {
            message
        }
        binding.tvAlertTitle.text = formattedTitle
        binding.tvAlertMessage.text = formattedMessage
        binding.cardAlert.visibility = View.VISIBLE
    }

    private fun performCallerLookup() {
        val number = binding.etPhoneNumber.text?.toString()?.trim() ?: ""
        if (number.isEmpty()) {
            Toast.makeText(this, "Please enter a phone number", Toast.LENGTH_SHORT).show()
            return
        }

        binding.btnCheckCaller.isEnabled = false
        binding.btnCheckCaller.text = "CHECKING..."
        binding.tvCallerResult.visibility = View.GONE

        lifecycleScope.launch {
            try {
                val result = apiClient.lookupCaller(number)
                binding.btnCheckCaller.isEnabled = true
                binding.btnCheckCaller.text = getString(R.string.btn_check_caller)

                if (result != null) {
                    binding.tvCallerResult.visibility = View.VISIBLE
                    val displayText = StringBuilder()

                    if (result.isRegisteredInstitution) {
                        displayText.append("KNOWN REGISTRY MATCH: ${result.registeredOrganization}\n\n")
                        displayText.append("⚠️ DOES NOT AUTHENTICATE CALLER\n")
                        displayText.append("Number matches a listed institutional contact, but Caller ID can be spoofed over telephony networks.\n\n")
                        displayText.append("Action: Verify independently using the institution's official contact details.\n\n")
                        displayText.append(result.advisory)
                        binding.tvCallerResult.setBackgroundColor(ContextCompat.getColor(this@MainActivity, R.color.warning_background))
                        binding.tvCallerResult.setTextColor(ContextCompat.getColor(this@MainActivity, R.color.suspicious_amber))
                    } else if (result.spoofingSuspected) {
                        displayText.append("POTENTIALLY SUSPICIOUS: IDENTITY CONFLICT DETECTED!\n\n")
                        displayText.append("Originating Number: ${result.nationalFormat ?: number}\n")
                        displayText.append(result.advisory)
                        binding.tvCallerResult.setBackgroundColor(ContextCompat.getColor(this@MainActivity, R.color.high_risk_background))
                        binding.tvCallerResult.setTextColor(ContextCompat.getColor(this@MainActivity, R.color.high_risk_red))
                    } else if (!result.isValid) {
                        displayText.append("INVALID NUMBER FORMAT\n\n")
                        displayText.append(result.advisory)
                        binding.tvCallerResult.setBackgroundColor(ContextCompat.getColor(this@MainActivity, R.color.high_risk_background))
                        binding.tvCallerResult.setTextColor(ContextCompat.getColor(this@MainActivity, R.color.high_risk_red))
                    } else {
                        displayText.append("CALLER IDENTITY UNVERIFIED\n\n")
                        displayText.append("Assess the conversation and never disclose OTPs, PINs, passwords, or banking credentials.\n\n")
                        displayText.append("Number Type: ${result.numberType} (${result.carrier ?: "Standard Provider"})\n")
                        displayText.append("Allocation Area: ${result.geographicRegion ?: "India"}\n")
                        displayText.append("ℹ️ Region metadata reflects initial numbering allocation, not physical location.")
                        binding.tvCallerResult.setBackgroundColor(ContextCompat.getColor(this@MainActivity, R.color.bg_secondary))
                        binding.tvCallerResult.setTextColor(ContextCompat.getColor(this@MainActivity, R.color.text_primary))
                    }

                    binding.tvCallerResult.text = displayText.toString()
                } else {
                    Toast.makeText(this@MainActivity, "Unable to verify caller. Check connection.", Toast.LENGTH_SHORT).show()
                }
            } catch (e: Exception) {
                binding.btnCheckCaller.isEnabled = true
                binding.btnCheckCaller.text = getString(R.string.btn_check_caller)
                Toast.makeText(this@MainActivity, "Error: ${e.message}", Toast.LENGTH_SHORT).show()
            }
        }
    }

    private fun requestCallScreeningRoleIfAvailable() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.Q) {
            val roleManager = getSystemService(RoleManager::class.java)
            if (roleManager.isRoleAvailable(RoleManager.ROLE_CALL_SCREENING)) {
                if (!roleManager.isRoleHeld(RoleManager.ROLE_CALL_SCREENING)) {
                    val intent = roleManager.createRequestRoleIntent(RoleManager.ROLE_CALL_SCREENING)
                    roleRequestLauncher.launch(intent)
                }
            }
        }
    }

    override fun onResume() {
        super.onResume()
        updateShieldStatusUi()
    }

    override fun onDestroy() {
        super.onDestroy()
        try {
            unregisterReceiver(serviceReceiver)
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
}
