package org.eldershield.companion

import android.os.Bundle
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import org.eldershield.companion.data.PreferenceManager
import org.eldershield.companion.databinding.ActivitySettingsBinding

class SettingsActivity : AppCompatActivity() {

    private lateinit var binding: ActivitySettingsBinding
    private lateinit var prefs: PreferenceManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivitySettingsBinding.inflate(layoutInflater)
        setContentView(binding.root)

        prefs = PreferenceManager(this)

        // Load current preferences
        binding.etServerUrl.setText(prefs.serverUrl)
        binding.etApiKey.setText(prefs.apiKey)
        binding.switchVibrate.isChecked = prefs.isVibrateEnabled
        binding.switchSound.isChecked = prefs.isSoundEnabled
        binding.switchCallScreening.isChecked = prefs.isCallScreeningEnabled

        binding.btnBackSettings.setOnClickListener {
            finish()
        }

        binding.btnSaveSettings.setOnClickListener {
            val newUrl = binding.etServerUrl.text?.toString()?.trim() ?: ""
            val newKey = binding.etApiKey.text?.toString()?.trim() ?: ""

            val (isValid, errorMsg) = PreferenceManager.validateServerUrl(newUrl)
            if (!isValid) {
                Toast.makeText(this, errorMsg ?: "Invalid Server URL format", Toast.LENGTH_LONG).show()
                return@setOnClickListener
            }

            prefs.serverUrl = newUrl
            prefs.apiKey = newKey
            prefs.isVibrateEnabled = binding.switchVibrate.isChecked
            prefs.isSoundEnabled = binding.switchSound.isChecked
            prefs.isCallScreeningEnabled = binding.switchCallScreening.isChecked

            Toast.makeText(this, "Settings saved successfully", Toast.LENGTH_SHORT).show()
            finish()
        }
    }
}
