# ElderShield Production Deployment & Operations Guide

This guide documents reproducible deployment configurations, environment variables, model requirements, network configurations, and operations for the ElderShield Scam Protection platform.

---

## 1. System Architecture

ElderShield comprises three core subsystems:
1. **Production Backend**: FastAPI with multi-vector behavioral scam detection, CTranslate2/faster-whisper ASR with Silero VAD, phone intelligence, and real-time WebSocket streaming.
2. **Web Frontend**: React + TypeScript + Vite responsive dashboard for caregivers, seniors, and demonstration workstations.
3. **Android Companion Application**: Native Kotlin application for seniors with pre-call `CallScreeningService` triage, Speakerphone Protection Mode (`AudioRecord`), and accessible multi-modal alerts (vibration, tones, Text-To-Speech).

---

## 2. Runtime Requirements

### Hardware Sizing
* **Minimum**: 2 CPU Cores, 2 GB RAM (for `tiny` Whisper model and rule-based engine).
* **Recommended Production**: 4 CPU Cores, 4 GB RAM (supports 50+ concurrent live WebSocket streams and <10ms behavioral risk scoring latency).
* **Storage**: Ephemeral memory processing. Disk persistence is zero by default under the `EPHEMERAL_ZERO_DISK_RETENTION` policy.

### Software Dependencies
* Python 3.11+
* Node.js 20+ / npm 10+
* Docker & Docker Compose (optional for containerized deployment)
* Java 17 or 21 + Android SDK 34 (for Android app compilation)

---

## 3. Environment Variables Reference

Create a `.env` file in the `backend/` directory based on `.env.example`:

| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `HOST` | `0.0.0.0` | Bind IP address for production server |
| `PORT` | `8000` | Port for the HTTP and WebSocket server |
| `ENVIRONMENT` | `production` | Environment name (`production`, `staging`, `development`) |
| `DEBUG` | `false` | Enable verbose debug output |
| `ALLOWED_ORIGINS` | `*` | Comma-delimited list of allowed CORS origins |
| `REQUIRE_AUTH` | `false` | When `true`, enforces `X-API-Key` or Bearer token on API and WS |
| `API_KEY` | `eldershield-production-key-hwv4` | Pre-shared key for client and mobile companion authorization |
| `RATE_LIMIT_PER_MINUTE` | `120` | Max requests allowed per client IP per minute before HTTP 429 |
| `MAX_AUDIO_UPLOAD_MB` | `25` | Security threshold limit for uploaded audio recordings |
| `WHISPER_MODEL_SIZE` | `tiny` | faster-whisper model variant (`tiny`, `base`, `small`, `medium`) |
| `WHISPER_DEVICE` | `cpu` | Device execution backend (`cpu`, `cuda`) |
| `WHISPER_COMPUTE_TYPE`| `int8` | Quantization type (`int8`, `float16`, `int8_float16`) |
| `MAX_CONCURRENT_SESSIONS`| `50` | Maximum simultaneous active WebSocket audio streams |
| `SESSION_IDLE_TIMEOUT_SECONDS`| `1800` | Eviction timeout for idle in-memory streaming sessions |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |
| `ENABLE_JSON_LOGGING`| `false` | When `true`, outputs structured single-line JSON logs |
| `MASK_LOG_PII` | `true` | Redacts phone numbers, bank accounts, and OTPs in logs |

---

## 4. Production Startup (Local / Bare Metal)

### 4.1 Backend Service
```bash
# 1. Navigate to backend directory
cd backend

# 2. Activate virtual environment (if applicable)
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install production dependencies
pip install -r requirements.txt

# 4. Start production Uvicorn server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --workers 1
```

### 4.2 Frontend Service
```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm ci

# 3. Build optimized production bundle
npm run build

# 4. Preview / Serve locally
npm run preview -- --host 0.0.0.0 --port 5173
```

---

## 5. Containerized Deployment (Docker Compose)

ElderShield includes pre-configured multi-stage production Dockerfiles and orchestration.

```bash
# Build and start all services in the background
docker compose up -d --build

# Verify running containers and health checks
docker compose ps

# View structured logs
docker compose logs -f backend
```

Services exposed:
* Web Application: `http://localhost:80`
* API & WebSocket: `http://localhost:8000`

---

## 6. Android Companion Application Build & Setup

### 6.1 Compiling the APK
```bash
cd android

# Build debug APK using Gradle
./gradlew :app:assembleDebug
```
The compiled APK will be located at:
`android/app/build/outputs/apk/debug/app-debug.apk`

### 6.2 Installing & Setting Up on Android Device
```bash
# Install onto connected Android phone or emulator
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

### 6.3 Required Initial Settings on Device
1. **Set as Default Caller ID & Spam App**:
   * Open Android **Settings** → **Apps** → **Default apps** → **Caller ID & spam app** → Select **ElderShield**.
   * This activates `ElderShieldCallScreeningService` to intercept calls before ringing.
2. **Microphone Permission**:
   * Open ElderShield app → Tap **START PROTECTION** → Grant **Microphone** permission.
   * This enables Speakerphone Protection Mode.
3. **Configure Backend URL**:
   * Tap the **Settings** icon in the app.
   * Set **Backend Server URL** to your server IP (e.g., `http://192.168.1.100:8000` or `http://10.0.2.2:8000` for the Android emulator).

---

## 7. Verification & Health Monitoring

### Health & Readiness Probes
* **Liveness Probe**: `GET /health` (Returns `{"status": "healthy"}`)
* **Readiness Probe**: `GET /ready` (Validates ASR model status, caller registry, active sessions, and engine status)

```bash
# Health check probe
curl http://localhost:8000/health

# Readiness check probe
curl http://localhost:8000/ready
```

### Running Test Verification Suites
```bash
# Run backend pytest suite (unit, integration, and security checks)
pytest

# Run End-to-End Live Pipeline Verification (ASR + WebSocket + Scenarios)
python test_e2e_live_pipeline.py
```
