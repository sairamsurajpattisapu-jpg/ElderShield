# ElderShield (HWV4-PS05)
### Real-Time Conversational Scam Detection for Elderly Users
**Hack With Vizag 4.0 — Cybersecurity & Elder Protection Track**

---

## 🛡️ Executive Summary
Elderly citizens in India are disproportionately targeted by aggressive social engineering fraud—notably **digital arrest intimidation, utility disconnection threats, remote screen-share malware, and pension/KYC credential theft**. 

**ElderShield** is a specialized, multi-lingual conversational scam detection system designed from the ground up for seniors. Rather than flagging naive keyword matches (e.g. flagging a call just because someone mentions "OTP", "bank", or "account"), ElderShield analyzes **behavioral combinations, progressive dialogue velocity, and psychological pressure vectors** across English, Hindi (हिन्दी), Telugu (తెలుగు), Hinglish, and Teluglish.

---

## 🌟 Key Features

### 1. Progressive Risk Velocity Engine
- Evaluates risk **after each conversation turn** ($t_1 \to t_N$).
- Computes cumulative threat scores on a calibrated 0–100 scale:
  - **LOW RISK (0–25):** Safe communication or legitimate banking protocol observed (e.g., advising in-person branch verification, warning against disclosing OTPs).
  - **SUSPICIOUS (26–60):** Unverified institutional claims or artificial deadlines without direct credential theft yet.
  - **HIGH RISK (61–100):** Toxic combination detected (Impersonation + Urgency/Secrecy + OTP/PIN/Remote App/Transfer Solicitations).
  - **INSUFFICIENT EVIDENCE:** Inconclusive, ambiguous dialogue where intent cannot be confirmed.
- Interactive **Step-by-Step Call Replay Simulator** allows judges and users to witness risk escalations turn-by-turn.

### 2. Evidence-Based Ledger
- Every warning is strictly anchored to:
  - Exact verbatim transcript quote
  - Turn number & speaker attribution
  - Behavioral taxonomy category
  - Plain-language explanation for elderly comprehension
  - Protective counter-action

### 3. Senior-Accessible Design
- **High-Contrast Dark Theme:** Deep navy/near-black surfaces (`#080c16`, `#0f172a`), restrained cyan/teal accents (`#06b6d4`, `#14b8a6`), high-visibility risk badges.
- **Font Size Stepper:** Instant 1-click toggling between Standard (16px), Large (18px), and Extra Large (20px).
- **Web Audio Alert Chimes:** Distinct audio cues for visually impaired seniors (gentle chime for Safe, caution beep for Suspicious, urgent pulse for High Risk).
- **National Cybercrime Helpline 1930 Integration:** 1-click speed dial banner and copyable incident report for police and family escalation.

### 4. Certified Benchmark Scenarios
Built-in deterministic test cases:
1. **Legitimate Bank Call:** Contains sensitive keywords ("OTP", "bank", "KYC") but complies with official safety protocol and invites an in-person branch visit. *(Result: LOW RISK)*
2. **Progressive Electricity Scam:** 7-turn escalating fraud threatening power cutoff at 8 PM, demanding QuickSupport APK installation and OTP. *(Result: HIGH RISK)*
3. **Ambiguous Delivery Inquiry:** Neutral courier question with incomplete context. *(Result: INSUFFICIENT EVIDENCE)*
4. **Vizag CBI Digital Arrest:** Visakhapatnam Cyber Crime / CBI courier parcel fraud with "digital arrest" intimidation in Telugu and English. *(Result: HIGH RISK)*

---

## 📐 Architecture & Tech Stack

```
ElderShield/
├── backend/
│   ├── engine/
│   │   ├── __init__.py
│   │   ├── models.py          # Pydantic schemas (turns, findings, results)
│   │   ├── multilingual.py    # English, Hindi, Telugu regex registries
│   │   ├── analyzer.py        # Core progressive multi-vector scam engine
│   │   └── scenarios.py       # Deterministic benchmark scenarios
│   └── main.py                # FastAPI REST API + CORS middleware
├── frontend/
│   ├── src/
│   │   ├── components/        # Header, Dashboard, Timeline, Evidence, etc.
│   │   ├── utils/audioAlert.ts# Senior-accessible Web Audio API synthesizer
│   │   ├── api.ts             # Fetch API client
│   │   ├── types.ts           # Strict TypeScript contracts
│   │   ├── App.tsx            # Main reactive dashboard
│   │   └── index.css          # Senior-accessible CSS variables & dark palette
│   ├── vite.config.ts         # Vite server with /api proxy
│   └── package.json
└── start.bat                  # 1-click dual-service launcher
```

- **Backend:** Python 3.11, FastAPI, Pydantic v2, Uvicorn
- **Frontend:** React 19, TypeScript, Vite, Lucide Icons, Vanilla CSS
- **Audio:** Browser Web Audio API (zero external sound file dependencies)

---

## 🚀 Quick Start Instructions

### Prerequisites
- Python 3.10+
- Node.js 18+ and npm

### 1-Click Launch (Windows)
Double-click `start.bat` in the project root directory.

### Or Run Manually

#### 1. Backend Service
```bash
cd backend
python -m pip install fastapi uvicorn pydantic python-multipart
python -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload
```
API Documentation will be live at `http://localhost:8000/docs`

#### 2. Frontend Application
```bash
cd frontend
npm install
npm run dev
```
Open your browser at `http://localhost:5173`

---

## 🛡️ Hack With Vizag 4.0 Compliance Checklist
- [x] Functional, deployable full-stack application (not mockups).
- [x] Multi-lingual support for English, Hindi, Telugu, and mixed code.
- [x] Turn-by-turn progressive risk evaluation in the backend engine.
- [x] Rigorous context-awareness (prevents false positives on keywords like "OTP" when used in legitimate safeguards).
- [x] Concrete evidence quotes linked to every warning.
- [x] Accessible UI tailored specifically for elderly citizens.
- [x] Direct integration with National Cybercrime Helpline 1930 and incident reporting.
