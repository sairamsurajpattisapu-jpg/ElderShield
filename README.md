# ElderShield (HWV4-PS05)
### Real-Time Conversational Scam Protection for Elderly Users
**Hack With Vizag 4.0 — Cybersecurity & Elder Protection Track**

---

## 🛡️ Executive Summary

Elderly citizens are disproportionately targeted by aggressive social engineering fraud—notably **digital arrest extortion, fake utility disconnections, remote screen-share malware, and pension/KYC credential theft**.

**ElderShield** is a unified, multi-lingual cybersecurity protection system designed specifically for seniors and their caregivers. Operating across a **native Android companion app**, a **high-throughput FastAPI production backend**, and a **senior-accessible Web monitoring console**, ElderShield detects scams in real time using:
1. **Acoustic Speakerphone Protection** & Pre-Call `CallScreeningService` on Android.
2. **Compound Behavioral Risk Scoring** across English, Hindi, Telugu, Hinglish, and Teluglish.
3. **Institutional Caller Intelligence & Anti-Spoofing Verification** (`phonenumbers` + verified entity registries).
4. **Local Speech Recognition with Zero Permanent Disk Storage** (`faster-whisper`, CTranslate2 INT8, and Silero VAD).
5. **Accessible Multi-Modal Defensive Warnings** (audio sirens, rhythmic haptics, spoken voice alerts, and 1-touch 1930 Cybercrime Helpline speed dial).

---

## 🌟 Key Architecture & Capabilities

```
                           ┌──────────────────────────────────────────────────┐
                           │            INCOMING CELLULAR / VOIP CALL         │
                           │          (Put on Speakerphone by Senior)         │
                           └─────────────────────────┬────────────────────────┘
                                                     │ Acoustic Audio
                                                     ▼
┌───────────────────────────────────────┐   ┌───────────────────────────────────┐
│     CALL SCREENING SERVICE (API 29+)  │   │     ANDROID COMPANION APP         │
│  • Pre-call metadata caller triage    │   │  • Foreground Service Mic Audio   │
│  • Institutional spoofing detection   │   │  • 16kHz PCM WebSocket Stream    │
│  • Auto-block & alert notification    │   │  • TTS + Siren + Haptic Warnings  │
└──────────────────┬────────────────────┘   └─────────────────┬─────────────────┘
                   │                                          │ Full-Duplex WS
                   └──────────────────┬───────────────────────┘ (/ws/live-call)
                                      ▼
                   ┌────────────────────────────────────────────────────────────┐
                   │               ELDERSHIELD PRODUCTION BACKEND               │
                   │  • ASR: faster-whisper-tiny / Silero VAD (INT8 quantized)  │
                   │  • Engine: Multi-vector progressive behavioral analyzer    │
                   │  • Intelligence: E.164 normalization & spoofing conflict   │
                   │  • Security: Constant-time auth, Rate limiter, PII filter  │
                   │  • Privacy: Ephemeral zero-disk audio retention policy     │
                   └──────────────────────────┬─────────────────────────────────┘
                                              │ Real-Time Updates (< 2ms)
                                              ▼
                   ┌────────────────────────────────────────────────────────────┐
                   │           SENIOR-ACCESSIBLE WEB CONSOLE (VITE/REACT)       │
                   │  • Large font stepper (16px–20px) & High-contrast theme    │
                   │  • Verbatim evidence ledger & turn-by-turn replay          │
                   │  • 1-Click National Cybercrime Helpline (1930) escalation  │
                   └────────────────────────────────────────────────────────────┘
```

---

## 📱 Subsystems Overview

### 1. Android Companion Application (`android/`)
- **Package**: `org.eldershield.companion` (Target SDK 34, Min SDK 26).
- **Protection Lifecycle**: Explicit state tracking (`STOPPED`, `STARTING`, `CONNECTING`, `LIVE_PROTECTED`, `RECONNECTING`, `DEGRADED`, `FAILED`).
- **Resilient Reconnection**: Bounded exponential backoff reconnection (1s -> 2s -> 4s -> 8s -> 16s, max 5 attempts) with instant cancellation on manual stop.
- **Pre-Call Screening**: Implements Android `CallScreeningService` to intercept incoming calls, query caller metadata, and silence or block spoofed calls.
- **Speakerphone Protection Mode**: Captures in-call acoustic audio via `AudioRecord` (16,000 Hz, 16-bit Mono Little-Endian PCM, 100ms frames) within an Android Foreground Service with live WebSocket streaming.
- **Multi-Modal Warning System**: Instant haptic vibration patterns, loud emergency alarm audio (`STREAM_ALARM`), spoken voice alerts via Text-To-Speech ("Warning! Scam detected!"), and high-contrast alert UI.
- **Unit Tested**: Verified via `ProtectionLifecycleTest.kt` for states, backoff bounds, and audio frame dimensions.

### 2. Production Backend (`backend/`)
- **Real-Time Streaming**: High-throughput FastAPI ASGI server with full-duplex WebSocket (`/ws/live-call`) supporting up to 50 concurrent sessions with idle eviction and session isolation.
- **Speech-to-Text Pipeline**: In-memory `faster-whisper-tiny` with CTranslate2 INT8 and Silero VAD delivering 0.082x Real-Time Factor (RTF) speech recognition with zero disk tempfiles.
- **Contextual Scam Analysis**: Multi-vector behavioral scoring evaluating:
  - Institutional impersonation (CBI, Police, RBI, Customs, Electricity Board).
  - Urgency and punitive intimidation ("digital arrest", immediate power cut).
  - Secrecy and isolation ("do not tell anyone", "stay on the line").
  - Financial extraction (OTP disclosure, remote app installation, money transfers).
- **Caller Intelligence**: Normalizes phone numbers with Google's `phonenumbers` library and flags institutional spoofing conflicts (`KNOWN_REGISTRY_MATCH` with explicit spoofing disclaimer).
- **Production Hardening**: Constant-time token verification (`secrets.compare_digest`), sliding-window IP rate limiting, privacy-conscious PII log redaction, and `/health` + `/ready` diagnostic probes.
- **Test Suite**: 239 backend pytest tests passing with 100% success rate (177 core unit/integration + 30 targeted holdout + 32 adversarial stress).

### 3. Web Monitoring Console (`frontend/`)
- **Framework**: React 19, TypeScript, and Vite.
- **Senior Accessibility**: High-contrast theme, dynamic font scaling, Web Audio warning chimes, and plain-language protective guidance.
- **Live Monitor**: Truthful connection status badges, dynamic WebSocket URL resolution, and verbatim evidence ledger.

---

## ⚡ Certified Benchmark Scenarios

| Scenario | Demographics & Language | Behavioral Markers | Classification | Decision |
|---|---|---|---|---|
| **1. Legitimate Bank Discussion** | Senior Account Holder (English / Hinglish) | Explains KYC, explicitly reminds senior never to share OTP, invites branch visit | `LOW_RISK` (Score: 10) | **ALLOW** |
| **2. Progressive Electricity Scam** | Elderly Homeowner (English / Mixed Hindi) | Power cut threat at 8 PM, QuickSupport APK installation demand, OTP extraction | `HIGH_RISK` (Score: 85) | **BLOCK** |
| **3. Ambiguous Delivery Inquiry** | General Senior (English) | Inconclusive courier question, no credentials demanded, no threats | `INSUFFICIENT_EVIDENCE` (Score: 15) | **INCONCLUSIVE** |
| **4. Vizag CBI Digital Arrest** | Senior Citizen (Telugu & English) | Impersonates DSP Rao (CBI/Police), fake contraband parcel, digital arrest threat, Google Pay transfer | `HIGH_RISK` (Score: 85) | **BLOCK** |

---

## 🚀 Quick Start Instructions

### Prerequisites
- Python 3.11+
- Node.js 20+ / npm 10+
- Java 17/21 & Android SDK 34 (for Android build)

---

### Step 1: Run the Backend Service
```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```
- API Documentation: `http://localhost:8000/docs`
- Health Probe: `http://localhost:8000/health`
- Readiness Probe: `http://localhost:8000/ready`

---

### Step 2: Run the Web Frontend
```bash
cd frontend
npm install
npm run dev
```
- Accessible Web Dashboard: `http://localhost:5173`
- Production Build: `npm run build`

---

### Step 3: Build & Install Android Companion App
```bash
cd android
# Run Android unit tests and assemble debug APK
$env:JAVA_HOME = "C:\Program Files\Android\Android Studio\jbr" # or your local JDK path
./gradlew testDebugUnitTest assembleDebug

# Install onto connected phone or emulator
adb install -r app/build/outputs/apk/debug/app-debug.apk
```
Compiled APK path: `android/app/build/outputs/apk/debug/app-debug.apk`

---

### Step 4: Docker Container Deployment
```bash
# Build and run containers (requires Docker Engine on host)
docker compose up -d --build

# Verify container status
docker compose ps
```
*(Note: Manifests statically validated. See `DEPLOYMENT.md` for complete configuration details.)*

---

## 🧪 Comprehensive Verification Suite

Run automated test suites to verify the entire system:

```bash
# 1. Run all backend unit, security, streaming & regression tests (239/239 passing)
pytest backend -v

# 2. Run curated 24-sample detection benchmark
python run_detection_evaluation.py

# 3. Run 112-sample unfamiliar evaluation regression suite (5 languages)
python evaluate_unfamiliar_dataset.py

# 4. Run targeted holdout regression dataset (30 scenarios, 0 FP on hospital emergencies)
python evaluate_holdout_dataset.py

# 5. Run adversarial stress evaluation dataset (32 scenarios, novel multi-turn scams & safe emergencies)
python evaluate_adversarial_dataset.py

# 6. Run complete end-to-end protection pipeline (8 scenarios + latency profiling)
python test_complete_protection_pipeline.py

# 7. Run live audio speech ASR + live WebSocket test
python test_e2e_live_pipeline.py

# 8. Run systematic monotonic latency benchmark suite
python test_latency_benchmarks.py

# 9. Run speech recognition accuracy & intent preservation benchmark
python evaluate_speech_recognition.py
```

---

## 🎬 Hackathon Demonstration Guide (5-Minute Evaluation)

Follow this deterministic sequence to evaluate the end-to-end ElderShield platform:

### Step 1: Startup & Deep System Readiness Probe (30 seconds)
```bash
# Terminal 1: Run production FastAPI ASGI server
python -m uvicorn main:app --app-dir backend --host 0.0.0.0 --port 8000
```
Verify readiness at `http://localhost:8000/ready`:
- Returns `{"status":"ready","analyzer_engine":{"status":"ready"},"asr_service":{"engine_ready":true,"model_size":"tiny"},"session_registry":{"active_sessions":0}}`.

### Step 2: Launch Web Console or Android Companion (30 seconds)
```bash
# Terminal 2: Run senior-accessible React console
cd frontend && npm run dev
```
Open `http://localhost:5173`. Connection pill displays green `CONNECTED (WS)`.

### Step 3: Demonstrate Legitimate Banking Call — Zero False Alarm (30 seconds)
- Click **"Test Scenario 1: Legitimate Bank Discussion"** on the dashboard.
- Observe: Risk score remains `10/100 (LOW RISK, ALLOW)`.
- Key validation: Although the word *"OTP"* was spoken, the official bank safeguard (*"never ask for your OTP... visit branch"*) suppresses risk. **Zero false alarm.**

### Step 4: Demonstrate Legitimate Hospital Emergency — Zero False Alarm (30 seconds)
- In the **Custom Conversation Analysis** box, paste an urgent medical call:
  > *"Caller: Hello Mr. Rao, Dr. Sundaram from Apollo Hospital casualty ward. Your brother was brought in after an accident. He is stable but requires emergency consent. Please come to casualty counter 4 immediately. Billing will be handled at the hospital desk when you arrive."*
- Click **"Analyze Conversation"**.
- Observe: Risk is classified as `INSUFFICIENT_EVIDENCE` (Score: 15.0, `INCONCLUSIVE`).
- Key validation: Extreme medical urgency without credential extraction or remote APK demands does not trigger false alarms.

### Step 5: Demonstrate Ambiguous Dialogue — Conservative Uncertainty (30 seconds)
- Click **"Test Scenario 3: Ambiguous Delivery Inquiry"**.
- Observe: Classification is `INSUFFICIENT_EVIDENCE` (Score: 15.0, `INCONCLUSIVE`).
- The system displays an explicit uncertainty disclaimer rather than guessing or causing alarm.

### Step 6: Demonstrate Multi-Turn Scam Escalation & Evidence-Backed Warning (1 minute)
- Click **"Test Scenario 2: Progressive Impersonation & Payment Scam"** or **"4. Vizag CBI Digital Arrest"**.
- Watch turn progression in real time:
  - **Turn 1 (Impersonation)**: Score rises to `SUSPICIOUS (42/100)`.
  - **Turn 2 (Contraband & Digital Arrest)**: Escalates to `HIGH RISK (78/100)`.
  - **Turn 3 (Isolation & Escrow Demand)**: Peaks at `CRITICAL (94/100)`.
- Multi-modal alert fires instantly: High-contrast red banner, loud alarm chime, spoken alert ("ElderShield Alert: Potential scam call detected"), plain-language instruction (*"HANG UP THE PHONE"*), and verbatim evidence quotes.
- One-touch speed dial directly surfaces **National Cybercrime Helpline (1930)**.

### Step 7: Demonstrate WebSocket Interruption & Resilient Recovery (30 seconds)
- Disconnect the network or kill the backend server.
- The client transitions immediately to `RECONNECTING` with bounded exponential backoff (`1s -> 2s -> 4s -> 8s -> 16s`).
- Restart the backend: The client reconnects cleanly with a fresh isolated session ID and zero stale audio buffer carryover.

### Step 8: Android Speakerphone Mode & Telephony OS Limitations (30 seconds)
- In the companion app (`android/app/build/outputs/apk/debug/app-debug.apk`), tap **"START CALL SHIELD"**.
- Status transitions truthfully: `CONNECTING` &rarr; `SHIELD ACTIVE` (only upon receiving `session_ready`).
- **Telephony Reality**: Non-system Android apps are restricted by the Android OS from recording cellular audio directly (`AudioSource.VOICE_CALL`). ElderShield utilizes **Speakerphone Protection Mode** (`AudioSource.MIC`), capturing incoming call audio played over the handset speaker.

---

## ⏱️ Systematic Latency Decomposition

To provide honest, defensible figures, ElderShield distinguishes **turn-to-alert** (server processing time after speech transcript is available) from **speech-onset-to-visible-alert** (total time an elderly user waits from the moment suspicious speech is spoken):

| Pipeline Stage | Mechanism / Engine | Measured Duration |
| :--- | :--- | :--- |
| **1. Audio Accumulation Window** | Silero VAD sentence boundary / 2s chunk buffer | ~2,000 ms |
| **2. Audio Transit to Server** | WebSocket PCM chunk streaming (100ms frames) | ~20 – 50 ms |
| **3. Server Speech Recognition (ASR)** | faster-whisper-tiny CPU INT8 (3s chunk / 21s batch) | **625 ms** (chunk) / **1,774 ms** (batch, RTF: 0.082x) |
| **4. Behavioral Scam Analysis** | Multi-vector compound threat engine | **0.75 ms** (Median) / 8.33 ms (P95) |
| **5. WebSocket Alert Dispatch** | ASGI WebSocket push frame transit | **1.00 ms** |
| **6. Client Render & Multi-Modal Trigger** | Android haptic siren / Web synthesized chime | ~10 – 20 ms |
| **Live Turn-to-Alert (Server Processing)** | **Stages 4 + 5 (Transcript Arrival &rarr; Client Alert)** | **~1.81 ms** (Median) / 3.83 ms (P95) |
| **Total Speech-Onset to Visible Alert** | **Stages 1 through 6 (Spoken Speech &rarr; Visible Alert)** | **~2.6 – 2.8 seconds** |

---

## 🛡️ User Trust, Safety & Defensive Disclaimers

1. **Advisory Tool Notice**: ElderShield is an assistive cybersecurity shield designed to provide early warnings against common phone scams. It is not an infallible authority and cannot guarantee detection of all evolving fraud schemes. An unflagged call is not guaranteed to be safe.
2. **Caller ID Spoofing Disclaimer**: A phone number matching a known institution is marked as `KNOWN_REGISTRY_MATCH` and is accompanied by an explicit warning:
   > *"⚠️ DOES NOT AUTHENTICATE CALLER: Originating number matches a registered institutional contact, but Caller ID can be spoofed over telephony networks. Always verify independently through trusted official numbers."*
3. **Core Protective Directives**:
   - Never share One-Time Passwords (OTPs), ATM PINs, NetBanking passwords, or UPI MPINs over the phone.
   - Never install remote access applications (AnyDesk, TeamViewer, QuickSupport) at the request of an incoming caller.
   - If pressured with threats of "digital arrest", power disconnection, or parcel seizure, disconnect immediately and dial the National Cybercrime Helpline at **1930**.
4. **Zero Permanent Audio Retention**: Audio chunks are processed exclusively in volatile memory (RAM) and immediately purged upon session completion. No call audio is ever stored on disk or shared with third parties. Logs automatically mask PII.


