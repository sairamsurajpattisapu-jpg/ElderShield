"""
ElderShield — Pipeline Latency Benchmarking Suite
Measures actual stage-by-stage latencies with monotonic clocks (time.perf_counter):
  Stage 1: ASR Inference Latency (faster-whisper-tiny INT8)
  Stage 2: Behavioral Scam Detection (Multi-Vector Engine)
  Stage 3: WebSocket Delivery Frame Transit
  Stage 4: End-to-End Turn-to-Alert Latency

Test environment:
  OS: Windows (Local Workstation)
  CPU: Native Multi-Core (4 threads)
  ASR Backend: CTranslate2 faster-whisper-tiny (INT8)
  Transport: Local ASGI WebSocket / Loopback HTTP
  Fixture Type: Automated Local Audio & Transcript Fixtures (Synthetic Benchmark)
"""

import io
import os
import sys
import time
import json
import wave
import statistics
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "backend"))
from fastapi.testclient import TestClient
from main import app
from engine.asr_service import asr_service
from engine.analyzer import engine

client = TestClient(app)

def generate_tone_with_silence(duration_sec=3.0, sample_rate=16000):
    """Generates synthetic 16kHz PCM audio buffer with pause/silence in the middle."""
    t = np.linspace(0, duration_sec, int(sample_rate * duration_sec), endpoint=False)
    # Sine wave for first half, silence for 0.5s, sine wave for second half
    audio = 0.3 * np.sin(2 * np.pi * 440 * t)
    silence_start = int(sample_rate * 1.0)
    silence_end = int(sample_rate * 1.5)
    audio[silence_start:silence_end] = 0.0
    pcm16 = (audio * 32767).astype(np.int16)
    
    buf = io.BytesIO()
    with wave.open(buf, 'wb') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)
        wav.setframerate(sample_rate)
        wav.writeframes(pcm16.tobytes())
    return buf.getvalue()

def run_asr_inference_benchmarks(iterations=5):
    """Benchmark Stage 1: Speech recognition latency across audio fixture types."""
    results = {
        "short_utterance_3s": [],
        "pause_segmented_3s": [],
        "real_speech_scam_21s": [],
    }

    # 1. Short utterance
    short_audio = generate_tone_with_silence(3.0)
    for _ in range(iterations):
        t0 = time.perf_counter()
        res = asr_service.transcribe_audio_bytes(short_audio, filename="short.wav")
        results["short_utterance_3s"].append(res.get("inference_latency_ms", (time.perf_counter() - t0) * 1000))

    # 2. Pause-segmented audio
    pause_audio = generate_tone_with_silence(3.0)
    for _ in range(iterations):
        t0 = time.perf_counter()
        res = asr_service.transcribe_audio_bytes(pause_audio, filename="pause.wav")
        results["pause_segmented_3s"].append(res.get("inference_latency_ms", (time.perf_counter() - t0) * 1000))

    # 3. Real speech fixture (scam_speech.wav - 21.5s)
    try:
        with open("scam_speech.wav", "rb") as f:
            scam_wav = f.read()
        for _ in range(iterations):
            t0 = time.perf_counter()
            res = asr_service.transcribe_audio_bytes(scam_wav, filename="scam.wav")
            results["real_speech_scam_21s"].append(res.get("inference_latency_ms", (time.perf_counter() - t0) * 1000))
    except Exception as e:
        print(f"Note: scam_speech.wav read exception: {e}")

    return results

def run_behavioral_detection_benchmarks(iterations=20):
    """Benchmark Stage 2: Multi-vector behavioral risk scoring latency."""
    dialogues = [
        # Short scam
        [("Caller", "You are under digital arrest. Transfer 50,000 rupees immediately.")],
        # Multi-turn progressive scam (6 turns)
        [
            ("Caller", "Hello, I am calling from Electricity Board regarding your meter."),
            ("Senior", "What is this regarding? I paid my bill."),
            ("Caller", "Power will be cut at 8 PM tonight immediately."),
            ("Senior", "Please no! How do I pay?"),
            ("Caller", "Download QuickSupport app right now and do not disconnect."),
            ("Caller", "Now read out the 6 digit OTP you received!")
        ],
        # Legitimate banking safeguard (6 turns)
        [
            ("Caller", "Good morning, Ramesh from State Bank of India home branch."),
            ("Senior", "Is there an issue with my pension account?"),
            ("Caller", "No issue, reviewing accounts due for KYC next month."),
            ("Senior", "Can I update online or send OTP?"),
            ("Caller", "Our bank never asks for OTP or PIN. Visit our branch next Tuesday."),
            ("Senior", "Thank you, I will visit with my son.")
        ],
        # Ambiguous conversation
        [
            ("Caller", "Hello, I have a parcel for flat 402."),
            ("Senior", "I am having lunch, who is this?"),
            ("Caller", "Delivery service. Is someone home?")
        ]
    ]

    durations = []
    for _ in range(iterations):
        for turns_list in dialogues:
            from engine.models import ConversationTurn
            turns = [ConversationTurn(turn_number=i+1, speaker=s, text=t) for i, (s, t) in enumerate(turns_list)]
            t0 = time.perf_counter()
            engine.analyze(turns=turns)
            durations.append((time.perf_counter() - t0) * 1000)

    return durations

def run_websocket_turn_to_alert_benchmarks(iterations=10):
    """Benchmark Stage 3 & 4: Live WebSocket full-duplex transit and warning dispatch."""
    e2e_latencies = []
    server_process_latencies = []

    for _ in range(iterations):
        with client.websocket_connect("/ws/live-call") as ws:
            ready = ws.receive_json()
            assert ready["type"] == "session_ready"

            # Turn 1: Caller introduces threat
            # Turn 1: Neutral opening (no warning yet)
            ws.send_json({
                "type": "transcript_segment",
                "speaker": "Caller",
                "text": "Hello, good morning. Can you hear me?",
                "is_final": True
            })
            resp1 = ws.receive_json()
            assert resp1["type"] == "risk_update"
            assert resp1["risk_level"] in ["LOW_RISK", "INSUFFICIENT_EVIDENCE"]

            # Turn 2: Critical scam extraction triggering immediate warning
            t_client_send2 = time.perf_counter()
            ws.send_json({
                "type": "transcript_segment",
                "speaker": "Caller",
                "text": "This is Officer Rao from CBI. You are under digital arrest. Transfer 85000 rupees to RBI safety account right now and do not tell your family.",
                "is_final": True,
                "client_turn_start_ms": t_client_send2 * 1000
            })
            
            # Receive risk_update
            upd = ws.receive_json()
            assert upd["type"] == "risk_update"
            
            # Receive warning
            warn = ws.receive_json()
            t_client_recv_warn = time.perf_counter()
            assert warn["type"] == "warning"

            e2e_lat = (t_client_recv_warn - t_client_send2) * 1000
            e2e_latencies.append(e2e_lat)

            if "timing" in warn and "transcript_to_risk_decision_ms" in warn["timing"]:
                server_process_latencies.append(warn["timing"]["transcript_to_risk_decision_ms"])

    return e2e_latencies, server_process_latencies

def compute_stats(data):
    if not data:
        return {"count": 0, "median": 0.0, "p95": 0.0, "max": 0.0}
    sorted_d = sorted(data)
    n = len(sorted_d)
    p95_idx = min(int(0.95 * n), n - 1)
    return {
        "count": n,
        "median": round(statistics.median(sorted_d), 2),
        "p95": round(sorted_d[p95_idx], 2),
        "max": round(max(sorted_d), 2)
    }

def main():
    print("=" * 80)
    print("ELDERSHIELD — SYSTEMATIC PIPELINE LATENCY BENCHMARKS")
    print("=" * 80)
    print("Environment: Windows Local Machine | faster-whisper-tiny INT8 (CPU)")
    print("Disclaimer: Measurements use automated loopback fixtures; not cellular modem audio.")
    print("-" * 80)

    # 1. ASR Benchmarks
    print("\n[STAGE 1] Server Speech Recognition (faster-whisper-tiny INT8):")
    asr_data = run_asr_inference_benchmarks(iterations=3)
    for name, times in asr_data.items():
        stats = compute_stats(times)
        print(f"  {name:25s} | N={stats['count']:2d} | Median: {stats['median']:7.2f}ms | P95: {stats['p95']:7.2f}ms | Max: {stats['max']:7.2f}ms")

    # 2. Behavioral Detection Core
    print("\n[STAGE 2] Behavioral Detection Core (Multi-Vector Multi-Turn Rules):")
    det_times = run_behavioral_detection_benchmarks(iterations=10)
    det_stats = compute_stats(det_times)
    print(f"  {'rule_engine_analyze':25s} | N={det_stats['count']:2d} | Median: {det_stats['median']:7.2f}ms | P95: {det_stats['p95']:7.2f}ms | Max: {det_stats['max']:7.2f}ms")

    # 3 & 4. Live WebSocket Turn-to-Alert End-to-End
    print("\n[STAGE 3 & 4] Full-Duplex WebSocket Turn-to-Alert End-to-End Transit:")
    e2e_times, srv_times = run_websocket_turn_to_alert_benchmarks(iterations=10)
    e2e_stats = compute_stats(e2e_times)
    srv_stats = compute_stats(srv_times)
    print(f"  {'turn_to_alert_e2e':25s} | N={e2e_stats['count']:2d} | Median: {e2e_stats['median']:7.2f}ms | P95: {e2e_stats['p95']:7.2f}ms | Max: {e2e_stats['max']:7.2f}ms")
    print(f"  {'server_internal_decision':25s} | N={srv_stats['count']:2d} | Median: {srv_stats['median']:7.2f}ms | P95: {srv_stats['p95']:7.2f}ms | Max: {srv_stats['max']:7.2f}ms")

    print("\n" + "=" * 80)
    print("PIPELINE LATENCY SUMMARY BREAKDOWN:")
    print(f"  - Model Inference (3s Audio Chunk) : Median ~{compute_stats(asr_data['short_utterance_3s'])['median']:.1f}ms")
    print(f"  - Model Inference (21s Audio Batch): Median ~{compute_stats(asr_data['real_speech_scam_21s'])['median']:.1f}ms")
    print(f"  - Behavioral Detection Engine      : Median ~{det_stats['median']:.2f}ms (P95: {det_stats['p95']:.2f}ms)")
    print(f"  - Live Turn-to-Alert (WS Loopback) : Median ~{e2e_stats['median']:.2f}ms (P95: {e2e_stats['p95']:.2f}ms)")
    print("=" * 80)

if __name__ == "__main__":
    main()
