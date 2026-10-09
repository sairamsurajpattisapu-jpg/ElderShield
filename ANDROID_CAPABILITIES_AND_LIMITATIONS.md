# ElderShield Android Companion Application
## Technical Investigation: Supported Android APIs, Call Screening, and Audio Capture Limitations

---

### 1. Executive Summary

ElderShield Companion for Android is designed to protect vulnerable seniors against telephone social engineering scams, institutional impersonation (CBI, Police, RBI, SBI, Electricity Board), and "digital arrest" extortion.

This document details the real-world capabilities and technical limitations enforced by the Android Operating System (Android 9 through Android 15), explaining the architecture of `ElderShieldCallScreeningService` and `ElderShieldProtectionService`.

---

### 2. Android Telephony & Cellular Call Audio Restrictions

#### The Architectural Restriction
Prior to Android 9 (Pie), third-party applications could occasionally capture cellular call audio using `MediaRecorder.AudioSource.VOICE_CALL`, `VOICE_DOWNLINK`, or `VOICE_UPLINK`. 

Beginning in **Android 9 (API 28)** and hardened in **Android 10 (API 29)**, **Android 14 (API 34)**, and **Android 15**:
1. **Operating System Level Blocking**: The Android audio policy service restricts access to raw cellular voice modem audio streams. Any non-system application attempting to record from `AudioSource.VOICE_CALL` receives silent audio buffers or throws a `java.lang.SecurityException`.
2. **Permission Sandboxing**: Direct access to cellular downlink/uplink audio requires signature-level carrier permissions (`android.permission.CAPTURE_AUDIO_OUTPUT`), which cannot be granted to ordinary third-party applications downloaded from Google Play or installed via standard APKs.
3. **Google Play Policy Enforcement**: Utilizing `AccessibilityService` APIs as a workaround to record telephone conversations violates Google Play Developer Policies (section 1.3 - User Data & Accessibility).

> **Conclusion**: It is technically impossible for any standard third-party Android application to silently and automatically capture raw cellular phone audio in the background on modern Android devices without system-level root access or carrier OEM firmware signing.

---

### 3. Investigation of Android `CallScreeningService`

ElderShield implements `android.telecom.CallScreeningService` in `ElderShieldCallScreeningService.kt`.

#### Supported Capabilities:
1. **Pre-Call Interception**: Intercepts incoming calls in the signaling phase before the senior's phone rings.
2. **Caller Number Extraction**: Extracts the originating phone number (`Call.Details.getHandle()`).
3. **Backend Caller Intelligence Query**: Queries ElderShield's `/api/caller-lookup` endpoint to check for:
   * Institutional identity spoofing (e.g. personal mobile numbers claiming to represent the CBI, RBI, or Courts).
   * High-risk telecom circles and invalid ITU E.164 formats.
4. **Automated Defensive Action (`CallResponse`)**:
   * `setDisallowCall(true)`: Blocks the call from connecting.
   * `setRejectCall(true)`: Terminates the incoming connection.
   * `setSilenceCall(true)`: Silences the ringer so the senior is not disturbed.
   * `setSkipCallLog(false)`: Preserves the call in call history for audit/evidence.
5. **Immediate Accessible Warning**: Dispatches a high-priority heads-up notification with urgent vibration and voice warning explaining the blocked spoof attempt.

#### Critical Limitation of `CallScreeningService`:
* **Zero Audio Access**: `CallScreeningService` runs strictly in the telecom signaling phase. It **has no access to call audio**. Once a call is answered by the user, the `CallScreeningService` is detached by the OS.

---

### 4. Supported Practical Alternative: Speakerphone Protection Mode

To provide live in-call scam detection without violating Android OS security rules, ElderShield implements the strongest supported alternative: **Speakerphone Protection Mode** (`ElderShieldProtectionService.kt`).

```
┌─────────────────────────────────────────────────────────────┐
│                      SUSPICIOUS CALL                        │
│                 (Put on Speakerphone by Senior)             │
└──────────────────────────────┬──────────────────────────────┘
                               │ Acoustic Sound Waves
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 DEVICE MICROPHONE (AudioRecord)             │
│        16,000 Hz, 16-bit Mono PCM, 100ms streaming chunks   │
└──────────────────────────────┬──────────────────────────────┘
                               │ Full-Duplex WebSocket (/ws/live-call)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                  ELDERSHIELD PRODUCTION BACKEND             │
│   • faster-whisper (tiny/base) + Silero VAD Speech Engine   │
│   • Multi-Vector Behavioral Scam Analyzer                   │
│   • Compound Risk Scoring & Fingerprinted Evidence          │
└──────────────────────────────┬──────────────────────────────┘
                               │ Real-Time Alerts (< 5ms latency)
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                   ACCESSIBLE ELDER ALERTS                   │
│   • Urgent Pulsed Haptic Vibration (Pattern: 500-200-800ms) │
│   • Emergency Alarm Tone via STREAM_ALARM                   │
│   • Spoken Voice Alert via Android Text-To-Speech (TTS)     │
│   • High-Contrast Fullscreen Alert with 1930 Speed Dial     │
└─────────────────────────────────────────────────────────────┘
```

#### How It Works:
1. **User Activation**: The senior taps the large green "START PROTECTION" button or leaves protection running in the background as a Foreground Service (`FOREGROUND_SERVICE_MICROPHONE`).
2. **Acoustic Ingestion**: When an incoming suspicious call arrives, the senior is prompted to put the call on speakerphone (the natural habit for seniors who struggle with hearing earpiece audio).
3. **Microphone Capture**: The standard Android microphone (`MediaRecorder.AudioSource.MIC`) captures the acoustic output from the phone's speaker. This works seamlessly for regular cellular calls, WhatsApp calls, Telegram calls, and in-person doorstep visitors.
4. **Streaming & Instant Warning**: The audio is streamed in real time to the ElderShield backend. When high-risk manipulative tactics (threat of arrest, secrecy demands, immediate fund transfer) are detected, ElderShield immediately interrupts with loud sound, distinctive vibration, and spoken advice to hang up.

---

### 5. Summary of Supported Capabilities vs. OS Constraints

| Feature | Android API Used | Feasibility | Limitation / Mitigation |
| :--- | :--- | :--- | :--- |
| **Pre-Call Screening** | `CallScreeningService` | Fully Supported (API 29+) | Metadata only; mitigates spoofing before call rings |
| **Call Auto-Block** | `CallResponse.Builder` | Fully Supported | Requires setting ElderShield as Default Caller ID & Spam app |
| **Direct Cellular Audio Recording** | `AudioSource.VOICE_CALL` | **Blocked by Android OS** | Mitigated via Speakerphone Protection Mode (`AudioSource.MIC`) |
| **Speakerphone Acoustic Protection** | `AudioRecord` + Foreground Service | Fully Supported | User puts call on speakerphone during suspicious conversations |
| **Voicemail / Audio File Upload** | `POST /api/analyze/audio` | Fully Supported | Caregivers or seniors can upload recorded files or voicemails |
| **Accessible Vibration Alert** | `Vibrator` / `VibrationEffect` | Fully Supported | Multi-stage rhythmic vibration for hearing-impaired users |
| **Spoken Voice Warning** | Android `TextToSpeech` | Fully Supported | Vocal speech alert ("Warning! Scam detected! Hang up now!") |
| **One-Touch Emergency 1930** | `Intent.ACTION_DIAL` | Fully Supported | Instantly opens dialer with 1930 prefilled |
| **Zero-Retention Privacy** | In-memory ephemeral buffers | Fully Supported | No audio stored on device or server; zero disk retention |
