import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Radio,
  PhoneOff,
  AlertTriangle,
  PhoneCall,
  Play,
  RotateCcw,
  Sparkles,
  ArrowRight,
  Clock,
  Activity,
  FileAudio,
  UserCheck,
  ShieldCheck,
} from 'lucide-react';
import type { RiskAssessment, RiskLevel, LiveRiskUpdate, LiveWarning, CallerIntelligenceResult } from '../types';
import { getLiveCallWsUrl, analyzeAudioFile, analyzeConversation, analyzeProgression, lookupCallerIdentity } from '../api';
import { playRiskAlert } from '../utils/audioAlert';

// Browser Web Speech API interface declaration for TypeScript
interface SpeechRecognitionEventLike {
  resultIndex: number;
  results: {
    length: number;
    [index: number]: {
      isFinal: boolean;
      [index: number]: {
        transcript: string;
      };
    };
  };
}

interface SpeechRecognitionLike {
  continuous: boolean;
  interimResults: boolean;
  lang: string;
  start: () => void;
  stop: () => void;
  onresult: (event: SpeechRecognitionEventLike) => void;
  onerror: (event: unknown) => void;
  onend: () => void;
}

interface WindowWithSpeech {
  SpeechRecognition?: { new (): SpeechRecognitionLike };
  webkitSpeechRecognition?: { new (): SpeechRecognitionLike };
}

interface LiveTurn {
  id: string;
  turnNumber: number;
  speaker: 'Caller' | 'Senior' | 'System';
  text: string;
  timestamp: string;
  score?: number;
  level?: RiskLevel;
  detectedSignals?: string[];
  isFinal: boolean;
}

interface LiveCallMonitorProps {
  onLoadFullAnalysis: (assessment: RiskAssessment) => void;
  soundAlertsEnabled: boolean;
}

// Built-in live demo simulation scripts
const SIMULATED_CALLS = [
  {
    id: 'sim_cbi_arrest',
    title: 'CBI Digital Arrest (High Risk)',
    lang: 'English / Hinglish',
    turns: [
      { speaker: 'Caller' as const, text: 'This is Officer Sharma from Central Bureau of Investigation, New Delhi headquarters.' },
      { speaker: 'Senior' as const, text: 'Hello, why are you calling me?' },
      { speaker: 'Caller' as const, text: 'A parcel addressed to you containing fake passports and contraband was intercepted at Mumbai customs. You are under digital arrest.' },
      { speaker: 'Senior' as const, text: 'Oh God! I have never ordered any parcel! Please help me.' },
      { speaker: 'Caller' as const, text: 'Do not disconnect this call or inform your family, otherwise local police will be dispatched to arrest you immediately.' },
      { speaker: 'Caller' as const, text: 'To prove your innocence and clear your bank account from money laundering charges, transfer 85,000 rupees to our RBI verification escrow account right now.' }
    ]
  },
  {
    id: 'sim_bank_otp',
    title: 'SBI NetBanking Expiry (High Risk)',
    lang: 'English / Hindi',
    turns: [
      { speaker: 'Caller' as const, text: 'Good morning sir, I am calling from State Bank of India cards security division.' },
      { speaker: 'Senior' as const, text: 'Yes, what is the issue with my card?' },
      { speaker: 'Caller' as const, text: 'Your debit card and NetBanking services are expiring today. Your account will be frozen within one hour.' },
      { speaker: 'Senior' as const, text: 'How do I stop it from getting frozen?' },
      { speaker: 'Caller' as const, text: 'I am sending a 6-digit verification code to your registered mobile. Read the OTP immediately to update your KYC.' }
    ]
  },
  {
    id: 'sim_legit_courier',
    title: 'Legitimate Delivery Check (Low Risk)',
    lang: 'English',
    turns: [
      { speaker: 'Caller' as const, text: 'Hello, I am calling from BlueDart courier regarding your parcel delivery scheduled today.' },
      { speaker: 'Senior' as const, text: 'Yes, I am expecting a book delivery. What time will you arrive?' },
      { speaker: 'Caller' as const, text: 'I will be at your address by 3 PM. Remember, never share any OTP or payment credentials with anyone over the phone.' },
      { speaker: 'Senior' as const, text: 'Understood, thank you. See you at 3 PM.' }
    ]
  }
];

export const LiveCallMonitor: React.FC<LiveCallMonitorProps> = ({
  onLoadFullAnalysis,
  soundAlertsEnabled,
}) => {
  // Live session states
  const [isMonitoring, setIsMonitoring] = useState<boolean>(false);
  const [connectionStatus, setConnectionStatus] = useState<'idle' | 'connecting' | 'connected' | 'disconnected'>('idle');
  const [selectedLanguage, setSelectedLanguage] = useState<string>('en-IN');
  const [turns, setTurns] = useState<LiveTurn[]>([]);
  const [currentScore, setCurrentScore] = useState<number>(0);
  const [currentRiskLevel, setCurrentRiskLevel] = useState<RiskLevel>('LOW_RISK');
  const [activeWarning, setActiveWarning] = useState<LiveWarning | null>(null);
  const [sessionDuration, setSessionDuration] = useState<number>(0);
  const [micAudioLevel, setMicAudioLevel] = useState<number>(0);
  const [micError, setMicError] = useState<string | null>(null);

  // Upload state
  const [isUploadingAudio, setIsUploadingAudio] = useState<boolean>(false);
  const [audioUploadFeedback, setAudioUploadFeedback] = useState<string | null>(null);

  // Simulation state
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Latest full assessment result from this session
  const [finalAssessment, setFinalAssessment] = useState<RiskAssessment | null>(null);

  // Caller verification state
  const [callerPhone, setCallerPhone] = useState<string>('');
  const [claimedOrg, setClaimedOrg] = useState<string>('');
  const [callerIntel, setCallerIntel] = useState<CallerIntelligenceResult | null>(null);
  const [isLookingUpCaller, setIsLookingUpCaller] = useState<boolean>(false);

  // Handle caller verification
  const handleVerifyCaller = async (phoneToVerify?: string, orgToVerify?: string) => {
    const num = phoneToVerify !== undefined ? phoneToVerify : callerPhone;
    const org = orgToVerify !== undefined ? orgToVerify : claimedOrg;
    if (!num.trim()) return;

    setIsLookingUpCaller(true);
    try {
      const result = await lookupCallerIdentity(num, org);
      setCallerIntel(result);

      // Send caller_info to WebSocket if connected
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          type: 'caller_info',
          phone_number: num,
          claimed_organization: org || undefined
        }));
      }

      if (result.spoofing_suspected) {
        setActiveWarning({
          type: 'warning',
          severity: 'CRITICAL',
          title: 'IDENTITY SPOOFING CONFLICT DETECTED',
          message: result.advisory,
          evidence_quotes: [
            `Caller claimed: ${org || 'Official Institution'}`,
            `Actual Origin: ${result.national_format || num} (${result.number_type} line)`
          ],
          timestamp: Date.now()
        });
        if (soundAlertsEnabled) {
          playRiskAlert('HIGH_RISK');
        }
      }
    } catch (e) {
      console.warn('Caller lookup error:', e);
    } finally {
      setIsLookingUpCaller(false);
    }
  };

  // References
  const wsRef = useRef<WebSocket | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const animFrameRef = useRef<number | null>(null);
  const speechRecognizerRef = useRef<SpeechRecognitionLike | null>(null);
  const timerIntervalRef = useRef<number | null>(null);
  const dialogueEndRef = useRef<HTMLDivElement | null>(null);
  const simulationTimerRef = useRef<number | null>(null);

  // Scroll to bottom of turns automatically
  useEffect(() => {
    dialogueEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [turns]);

  // Audio Level Meter Loop
  const updateAudioMeter = () => {
    if (!analyserRef.current) return;
    const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
    analyserRef.current.getByteFrequencyData(dataArray);

    let sum = 0;
    for (let i = 0; i < dataArray.length; i++) {
      sum += dataArray[i];
    }
    const average = sum / dataArray.length;
    // Map average (0 - 128) to 0 - 100 percentage
    const level = Math.min(100, Math.round((average / 60) * 100));
    setMicAudioLevel(level);

    animFrameRef.current = requestAnimationFrame(updateAudioMeter);
  };

  // Start live monitoring with microphone + WebSocket
  const startLiveMonitoring = async () => {
    setMicError(null);
    setActiveWarning(null);
    setTurns([]);
    setCurrentScore(0);
    setCurrentRiskLevel('LOW_RISK');
    setFinalAssessment(null);
    setConnectionStatus('connecting');

    try {
      // 1. Request microphone access
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
      });
      mediaStreamRef.current = stream;

      // 2. Set up Web Audio API visualizer
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof window.AudioContext }).webkitAudioContext;
      if (AudioCtx) {
        const audioCtx = new AudioCtx();
        const source = audioCtx.createMediaStreamSource(stream);
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        audioContextRef.current = audioCtx;
        analyserRef.current = analyser;
        updateAudioMeter();
      }

      // 3. Connect to ElderShield live WebSocket
      const wsUrl = getLiveCallWsUrl();
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnectionStatus('connected');
        setIsMonitoring(true);
        setSessionDuration(0);

        // Start session timer
        timerIntervalRef.current = window.setInterval(() => {
          setSessionDuration((prev) => prev + 1);
        }, 1000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'risk_update') {
            const update = data as LiveRiskUpdate;
            setCurrentScore(update.risk_score);
            setCurrentRiskLevel(update.risk_level);

            // Update turn list
            setTurns((prev) => {
              const existingIdx = prev.findIndex((t) => t.turnNumber === update.turn_number);
              const updatedTurn: LiveTurn = {
                id: `turn_${update.turn_number}`,
                turnNumber: update.turn_number,
                speaker: update.speaker as 'Caller' | 'Senior',
                text: update.text,
                timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                score: update.risk_score,
                level: update.risk_level,
                detectedSignals: update.reasons,
                isFinal: update.is_final,
              };

              if (existingIdx >= 0) {
                const nextTurns = [...prev];
                nextTurns[existingIdx] = updatedTurn;
                return nextTurns;
              }
              return [...prev, updatedTurn];
            });

            if (soundAlertsEnabled && update.risk_level === 'HIGH_RISK') {
              playRiskAlert('HIGH_RISK');
            }
          } else if (data.type === 'warning') {
            const warning = data as LiveWarning;
            setActiveWarning(warning);
            if (soundAlertsEnabled) {
              playRiskAlert('HIGH_RISK');
            }
          } else if (data.type === 'caller_intelligence') {
            setCallerIntel(data.caller_data as CallerIntelligenceResult);
          } else if (data.type === 'session_summary') {
            // Received final summary
          }
        } catch (e) {
          console.error('Error handling WebSocket message:', e);
        }
      };

      ws.onerror = (e) => {
        console.warn('WebSocket error, falling back to local speech recognition:', e);
        setConnectionStatus('disconnected');
      };

      ws.onclose = () => {
        setConnectionStatus('disconnected');
      };

      // 4. Set up Web Speech API for real-time streaming speech recognition
      const winWithSpeech = window as unknown as WindowWithSpeech;
      const SpeechRecognitionConstructor = winWithSpeech.SpeechRecognition || winWithSpeech.webkitSpeechRecognition;

      if (SpeechRecognitionConstructor) {
        const recognition = new SpeechRecognitionConstructor();
        recognition.continuous = true;
        recognition.interimResults = true;
        recognition.lang = selectedLanguage;

        let currentTurnCounter = 1;

        recognition.onresult = (evt: SpeechRecognitionEventLike) => {
          for (let i = evt.resultIndex; i < evt.results.length; i++) {
            const res = evt.results[i];
            const transcriptText = res[0].transcript.trim();
            const isFinal = res.isFinal;

            if (transcriptText) {
              // Send speech segment to backend WebSocket
              if (ws.readyState === WebSocket.OPEN) {
                ws.send(JSON.stringify({
                  type: 'transcript_segment',
                  speaker: 'Caller',
                  text: transcriptText,
                  is_final: isFinal,
                }));
              } else {
                // If WS disconnected, do local turn display
                setTurns((prev) => {
                  const existingIdx = prev.findIndex((t) => t.turnNumber === currentTurnCounter);
                  const newTurn: LiveTurn = {
                    id: `local_${currentTurnCounter}`,
                    turnNumber: currentTurnCounter,
                    speaker: 'Caller',
                    text: transcriptText,
                    timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                    isFinal: isFinal,
                  };
                  if (existingIdx >= 0) {
                    const updated = [...prev];
                    updated[existingIdx] = newTurn;
                    return updated;
                  }
                  return [...prev, newTurn];
                });
              }

              if (isFinal) {
                currentTurnCounter++;
              }
            }
          }
        };

        recognition.onerror = (err) => {
          console.warn('Speech recognition status:', err);
        };

        recognition.onend = () => {
          // Restart speech recognition if still monitoring
          if (mediaStreamRef.current && wsRef.current?.readyState === WebSocket.OPEN) {
            try {
              recognition.start();
            } catch {
              // ignore
            }
          }
        };

        recognition.start();
        speechRecognizerRef.current = recognition;
      }

      // 5. Set up MediaRecorder to capture audio slices and send binary chunks
      try {
        const mediaRecorder = new MediaRecorder(stream, { mimeType: 'audio/webm;codecs=opus' });
        mediaRecorderRef.current = mediaRecorder;
        let sequence = 1;

        mediaRecorder.ondataavailable = async (e) => {
          if (e.data && e.data.size > 0 && ws.readyState === WebSocket.OPEN) {
            const arrayBuffer = await e.data.arrayBuffer();
            const uint8Array = new Uint8Array(arrayBuffer);
            let binary = '';
            for (let i = 0; i < uint8Array.byteLength; i++) {
              binary += String.fromCharCode(uint8Array[i]);
            }
            const base64Chunk = btoa(binary);

            ws.send(JSON.stringify({
              type: 'audio_chunk',
              sequence_id: sequence++,
              chunk: base64Chunk,
            }));
          }
        };

        mediaRecorder.start(1500); // 1.5s slice intervals
      } catch (e) {
        console.warn('MediaRecorder opus stream not supported in this environment, using Speech recognition.', e);
      }

    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Microphone permission denied or audio input unavailable.';
      setMicError(msg);
      stopLiveMonitoring();
    }
  };

  // Stop live monitoring & finalize session
  const stopLiveMonitoring = async () => {
    setIsMonitoring(false);
    setIsSimulating(false);

    if (timerIntervalRef.current) {
      clearInterval(timerIntervalRef.current);
      timerIntervalRef.current = null;
    }

    if (simulationTimerRef.current) {
      clearInterval(simulationTimerRef.current);
      simulationTimerRef.current = null;
    }

    if (animFrameRef.current) {
      cancelAnimationFrame(animFrameRef.current);
      animFrameRef.current = null;
    }

    setMicAudioLevel(0);

    // Stop speech recognition
    if (speechRecognizerRef.current) {
      try {
        speechRecognizerRef.current.stop();
      } catch {
        // ignore
      }
      speechRecognizerRef.current = null;
    }

    // Stop MediaRecorder
    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch {
        // ignore
      }
      mediaRecorderRef.current = null;
    }

    // Stop mic stream tracks
    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((track) => track.stop());
      mediaStreamRef.current = null;
    }

    // Close AudioContext
    if (audioContextRef.current) {
      try {
        audioContextRef.current.close();
      } catch {
        // ignore
      }
      audioContextRef.current = null;
    }

    // Send stop to WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(JSON.stringify({ type: 'stop' }));
        setTimeout(() => {
          wsRef.current?.close();
        }, 500);
      } catch {
        // ignore
      }
    }

    setConnectionStatus('idle');

    // If turns were collected, run a final comprehensive analysis through backend to generate the dossier
    if (turns.length > 0) {
      try {
        const fullTranscript = turns.map((t) => `${t.speaker}: ${t.text}`).join('\n');
        const assessment = await analyzeConversation(fullTranscript);
        setFinalAssessment(assessment);
      } catch (e) {
        console.warn('Could not compile final dossier:', e);
      }
    }
  };

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopLiveMonitoring();
    };
  }, []);

  // Run deterministic simulation of live calls
  const runSimulation = (scenarioId: string) => {
    stopLiveMonitoring();
    const sim = SIMULATED_CALLS.find((s) => s.id === scenarioId);
    if (!sim) return;

    setActiveWarning(null);
    setTurns([]);
    setCurrentScore(0);
    setCurrentRiskLevel('LOW_RISK');
    setFinalAssessment(null);
    setIsSimulating(true);
    setSessionDuration(0);

    // Start timer
    timerIntervalRef.current = window.setInterval(() => {
      setSessionDuration((prev) => prev + 1);
    }, 1000);

    let idx = 0;
    const simTurns = sim.turns;

    const playNextTurn = async () => {
      if (idx >= simTurns.length) {
        setIsSimulating(false);
        if (timerIntervalRef.current) clearInterval(timerIntervalRef.current);

        // Compile final assessment
        const transcriptText = simTurns.map((t) => `${t.speaker}: ${t.text}`).join('\n');
        try {
          const assessment = await analyzeConversation(transcriptText);
          setFinalAssessment(assessment);
        } catch {
          // ignore
        }
        return;
      }

      const turnData = simTurns[idx];
      const partialTurns = simTurns.slice(0, idx + 1);
      const partialTranscript = partialTurns.map((t) => `${t.speaker}: ${t.text}`).join('\n');

      try {
        // Run progression evaluate
        const progression = await analyzeProgression(partialTranscript);
        const lastTurnEval = progression.turns[progression.turns.length - 1];

        setCurrentScore(progression.final_risk_score);
        setCurrentRiskLevel(progression.final_risk_level);

        setTurns((prev) => [
          ...prev,
          {
            id: `sim_${idx + 1}`,
            turnNumber: idx + 1,
            speaker: turnData.speaker,
            text: turnData.text,
            timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
            score: lastTurnEval?.cumulative_risk_score ?? progression.final_risk_score,
            level: lastTurnEval?.turn_risk_level ?? progression.final_risk_level,
            detectedSignals: lastTurnEval?.newly_detected_signals ?? [],
            isFinal: true,
          },
        ]);

        if (progression.final_risk_level === 'HIGH_RISK') {
          setActiveWarning({
            type: 'warning',
            severity: 'CRITICAL',
            title: 'URGENT FRAUD ALERT',
            message: progression.reasons[0] || 'Predatory urgency and credential/transfer demands detected.',
            evidence_quotes: [turnData.text],
            timestamp: Date.now(),
          });
          if (soundAlertsEnabled) {
            playRiskAlert('HIGH_RISK');
          }
        }
      } catch (err) {
        console.error('Simulation step error:', err);
      }

      idx++;
      simulationTimerRef.current = window.setTimeout(playNextTurn, 2200);
    };

    simulationTimerRef.current = window.setTimeout(playNextTurn, 600);
  };

  // Handle prerecorded audio file upload
  const handleAudioUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploadingAudio(true);
    setAudioUploadFeedback(null);
    setActiveWarning(null);

    try {
      setAudioUploadFeedback(`Transcribing audio with faster-whisper (${(file.size / 1024).toFixed(1)} KB)...`);
      const response = await analyzeAudioFile(file, selectedLanguage.split('-')[0] || 'auto');

      // Populate live monitor with the transcribed turns
      const assessment = response.risk_assessment;
      setFinalAssessment(assessment);
      setCurrentScore(assessment.risk_score);
      setCurrentRiskLevel(assessment.risk_level);

      const parsedTurns: LiveTurn[] = (assessment.turn_progression || []).map((t, idx) => ({
        id: `audio_${idx + 1}`,
        turnNumber: t.turn_number,
        speaker: t.speaker as 'Caller' | 'Senior',
        text: t.text,
        timestamp: `${(idx * 4)}s`,
        score: t.cumulative_risk_score,
        level: t.turn_risk_level,
        detectedSignals: t.newly_detected_signals,
        isFinal: true,
      }));

      setTurns(parsedTurns);

      if (assessment.risk_level === 'HIGH_RISK') {
        setActiveWarning({
          type: 'warning',
          severity: 'CRITICAL',
          title: 'HIGH-RISK CALL DETECTED FROM AUDIO RECORDING',
          message: assessment.recommended_action,
          evidence_quotes: assessment.evidence.map((e) => e.exact_quote).slice(0, 2),
          timestamp: Date.now(),
        });
        if (soundAlertsEnabled) {
          playRiskAlert('HIGH_RISK');
        }
      }

      setAudioUploadFeedback(`Audio processed successfully! Duration: ${response.audio_metrics.duration_seconds}s • Model latency: ${response.audio_metrics.transcription_latency_ms}ms.`);
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Failed to analyze audio file';
      setAudioUploadFeedback(`Error: ${msg}`);
    } finally {
      setIsUploadingAudio(false);
      event.target.value = '';
    }
  };

  // Helper format seconds to mm:ss
  const formatTime = (seconds: number) => {
    const m = Math.floor(seconds / 60).toString().padStart(2, '0');
    const s = (seconds % 60).toString().padStart(2, '0');
    return `${m}:${s}`;
  };

  // Helper color for score
  const getScoreColor = (score: number) => {
    if (score >= 66) return 'var(--risk-high)';
    if (score >= 26) return 'var(--risk-suspicious)';
    return 'var(--risk-low)';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Top Banner / Heading */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        padding: '20px 24px',
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '12px',
            backgroundColor: isMonitoring ? 'rgba(239, 68, 68, 0.15)' : 'rgba(6, 182, 212, 0.15)',
            border: `1.5px solid ${isMonitoring ? 'var(--risk-high)' : 'var(--accent-cyan)'}`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: isMonitoring ? 'var(--risk-high)' : 'var(--accent-cyan)',
            position: 'relative',
          }}>
            {isMonitoring ? <Radio size={26} className="animate-pulse" /> : <Mic size={26} />}
            {isMonitoring && (
              <span style={{
                position: 'absolute',
                top: '-4px',
                right: '-4px',
                width: '12px',
                height: '12px',
                borderRadius: '50%',
                backgroundColor: 'var(--risk-high)',
                boxShadow: '0 0 8px var(--risk-high)',
              }} />
            )}
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.35rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                Live Call Scam Monitor
              </h2>
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 700,
                textTransform: 'uppercase',
                padding: '3px 8px',
                borderRadius: '4px',
                backgroundColor: isMonitoring ? 'rgba(239, 68, 68, 0.2)' : 'rgba(16, 185, 129, 0.15)',
                color: isMonitoring ? '#fca5a5' : '#6ee7b7',
                border: `1px solid ${isMonitoring ? 'var(--risk-high-border)' : 'var(--risk-low-border)'}`,
              }}>
                {isMonitoring ? '🔴 LIVE STREAM ACTIVE' : isSimulating ? 'SIMULATION IN PROGRESS' : 'STANDBY'}
              </span>
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Sub-second conversational behavioral scanning. Protects elderly seniors during ongoing calls before credentials or money are transferred.
            </p>
          </div>
        </div>

        {/* Live Call Duration & Emergency Button */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          {(isMonitoring || isSimulating) && (
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '6px 14px',
              backgroundColor: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.9rem',
              fontWeight: 700,
              color: 'var(--accent-cyan)',
            }}>
              <Clock size={16} />
              <span>{formatTime(sessionDuration)}</span>
            </div>
          )}

          <a
            href="tel:1930"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '10px 18px',
              backgroundColor: 'rgba(239, 68, 68, 0.15)',
              border: '1.5px solid var(--risk-high)',
              borderRadius: 'var(--radius-md)',
              color: '#fca5a5',
              textDecoration: 'none',
              fontWeight: 800,
              fontSize: '0.92rem',
            }}
          >
            <PhoneCall size={18} color="#ef4444" />
            <span>Emergency Cyber Helpline: <strong>1930</strong></span>
          </a>
        </div>
      </div>

      {/* CRITICAL EMERGENCY WARNING OVERLAY / BANNER */}
      {activeWarning && (
        <div style={{
          backgroundColor: 'rgba(239, 68, 68, 0.22)',
          border: '2.5px solid var(--risk-high)',
          borderRadius: 'var(--radius-lg)',
          padding: '20px 24px',
          boxShadow: '0 0 30px rgba(239, 68, 68, 0.35)',
          animation: 'pulse 2s infinite',
        }}>
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px' }}>
            <div style={{
              width: '46px',
              height: '46px',
              borderRadius: '50%',
              backgroundColor: 'var(--risk-high)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: '#ffffff',
              flexShrink: 0,
            }}>
              <AlertTriangle size={28} />
            </div>
            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 800, color: '#fca5a5', letterSpacing: '0.02em' }}>
                  🚨 URGENT SCAM WARNING: SUSPECTED FRAUD DETECTED IN THIS CALL!
                </h3>
              </div>
              <p style={{
                fontSize: '1.05rem',
                fontWeight: 700,
                color: '#ffffff',
                margin: '8px 0 12px 0',
                lineHeight: 1.4,
              }}>
                {activeWarning.message}
              </p>

              {activeWarning.evidence_quotes.length > 0 && (
                <div style={{
                  padding: '10px 14px',
                  backgroundColor: 'rgba(0, 0, 0, 0.4)',
                  borderRadius: 'var(--radius-sm)',
                  borderLeft: '4px solid var(--risk-high)',
                  marginBottom: '14px',
                }}>
                  <div style={{ fontSize: '0.78rem', color: '#fca5a5', fontWeight: 700, textTransform: 'uppercase' }}>
                    Flagged Predator Statement:
                  </div>
                  <div style={{ fontSize: '0.95rem', color: '#f1f5f9', fontStyle: 'italic', marginTop: '2px' }}>
                    "{activeWarning.evidence_quotes[0]}"
                  </div>
                </div>
              )}

              {/* Protective Action Buttons for Seniors */}
              <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
                <button
                  onClick={stopLiveMonitoring}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 20px',
                    backgroundColor: 'var(--risk-high)',
                    border: 'none',
                    borderRadius: 'var(--radius-md)',
                    color: '#ffffff',
                    fontWeight: 800,
                    fontSize: '0.95rem',
                    cursor: 'pointer',
                  }}
                >
                  <PhoneOff size={18} />
                  <span>Hang Up & Terminate Call Protection</span>
                </button>

                <a
                  href="tel:1930"
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '8px',
                    padding: '10px 18px',
                    backgroundColor: '#1e293b',
                    border: '1px solid #475569',
                    borderRadius: 'var(--radius-md)',
                    color: '#ffffff',
                    fontWeight: 700,
                    fontSize: '0.9rem',
                    textDecoration: 'none',
                  }}
                >
                  <PhoneCall size={16} color="#ef4444" />
                  <span>Report Call to National Cybercrime Helpline (1930)</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Main Grid: Left Controls & Speedometer, Right Live Dialogue Stream */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(360px, 1fr))',
        gap: '24px',
      }}>
        {/* Left Column: Input Modes, VU Meter & Dynamic Risk Meter */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
          {/* Audio Input Control Box */}
          <div style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '22px',
          }}>
            <h3 style={{
              fontSize: '1.05rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: '14px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <Activity size={18} color="var(--accent-cyan)" />
              <span>Audio Input Controls</span>
            </h3>

            {/* Language Selection */}
            <div style={{ marginBottom: '16px' }}>
              <label style={{ display: 'block', fontSize: '0.82rem', color: 'var(--text-secondary)', marginBottom: '6px', fontWeight: 600 }}>
                Spoken Language Hint:
              </label>
              <select
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                disabled={isMonitoring || isSimulating}
                style={{
                  width: '100%',
                  padding: '9px 12px',
                  backgroundColor: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-subtle)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--text-primary)',
                  fontSize: '0.9rem',
                  outline: 'none',
                }}
              >
                <option value="en-IN">English (India / Hinglish)</option>
                <option value="hi-IN">Hindi (हिन्दी)</option>
                <option value="te-IN">Telugu (తెలుగు)</option>
                <option value="en-US">English (Standard)</option>
              </select>
            </div>

            {/* Mic Visualizer / Audio Meter */}
            <div style={{ marginBottom: '18px' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '6px' }}>
                <span>Microphone Signal Level</span>
                <span style={{ fontWeight: 700, color: micAudioLevel > 0 ? 'var(--accent-cyan)' : 'var(--text-muted)' }}>
                  {micAudioLevel > 0 ? `${micAudioLevel}% (Voice Detected)` : 'Inactive / Muted'}
                </span>
              </div>
              <div style={{
                height: '10px',
                width: '100%',
                backgroundColor: 'var(--bg-surface-elevated)',
                borderRadius: '5px',
                overflow: 'hidden',
                border: '1px solid var(--border-subtle)',
              }}>
                <div style={{
                  height: '100%',
                  width: `${micAudioLevel}%`,
                  backgroundColor: micAudioLevel > 60 ? 'var(--risk-high)' : micAudioLevel > 25 ? 'var(--accent-cyan)' : 'var(--accent-teal)',
                  transition: 'width 0.08s ease',
                }} />
              </div>
            </div>

            {/* Mic Error Callout */}
            {micError && (
              <div style={{
                padding: '10px 14px',
                backgroundColor: 'rgba(239, 68, 68, 0.15)',
                border: '1px solid var(--risk-high-border)',
                borderRadius: 'var(--radius-sm)',
                color: '#fca5a5',
                fontSize: '0.84rem',
                marginBottom: '16px',
              }}>
                {micError}
              </div>
            )}

            {/* Primary Action Button */}
            {!isMonitoring ? (
              <button
                onClick={startLiveMonitoring}
                disabled={isSimulating || isUploadingAudio}
                style={{
                  width: '100%',
                  padding: '13px 20px',
                  backgroundColor: 'var(--accent-cyan)',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  color: '#080c16',
                  fontWeight: 800,
                  fontSize: '1rem',
                  cursor: (isSimulating || isUploadingAudio) ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  boxShadow: '0 4px 14px rgba(6, 182, 212, 0.3)',
                  transition: 'all 0.15s ease',
                  opacity: (isSimulating || isUploadingAudio) ? 0.5 : 1,
                }}
              >
                <Mic size={20} />
                <span>Start Live Microphone Protection</span>
              </button>
            ) : (
              <button
                onClick={stopLiveMonitoring}
                style={{
                  width: '100%',
                  padding: '13px 20px',
                  backgroundColor: 'var(--risk-high)',
                  border: 'none',
                  borderRadius: 'var(--radius-md)',
                  color: '#ffffff',
                  fontWeight: 800,
                  fontSize: '1rem',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '10px',
                  boxShadow: '0 4px 14px rgba(239, 68, 68, 0.35)',
                }}
              >
                <MicOff size={20} />
                <span>Stop Live Call Protection</span>
              </button>
            )}

            {/* Divider */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '12px',
              margin: '20px 0 16px 0',
              color: 'var(--text-muted)',
              fontSize: '0.78rem',
              fontWeight: 700,
              textTransform: 'uppercase',
            }}>
              <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--border-subtle)' }} />
              <span>Or Upload Pre-Recorded Call Audio</span>
              <div style={{ flex: 1, height: '1px', backgroundColor: 'var(--border-subtle)' }} />
            </div>

            {/* Audio File Upload Dropzone */}
            <label style={{
              display: 'flex',
              flexDirection: 'column',
              alignItems: 'center',
              justifyContent: 'center',
              padding: '18px',
              border: '1.5px dashed var(--border-prominent)',
              borderRadius: 'var(--radius-md)',
              backgroundColor: 'var(--bg-surface-elevated)',
              cursor: isMonitoring ? 'not-allowed' : 'pointer',
              textAlign: 'center',
              opacity: isMonitoring ? 0.5 : 1,
            }}>
              <FileAudio size={24} color="var(--accent-teal)" style={{ marginBottom: '8px' }} />
              <span style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                {isUploadingAudio ? 'Transcribing with faster-whisper...' : 'Upload Call Recording (.wav, .mp3, .m4a)'}
              </span>
              <span style={{ fontSize: '0.76rem', color: 'var(--text-muted)', marginTop: '2px' }}>
                Runs offline ASR & extracts conversational fraud indicators
              </span>
              <input
                type="file"
                accept="audio/*"
                onChange={handleAudioUpload}
                disabled={isMonitoring || isUploadingAudio}
                style={{ display: 'none' }}
              />
            </label>

            {audioUploadFeedback && (
              <div style={{
                marginTop: '12px',
                fontSize: '0.82rem',
                color: audioUploadFeedback.startsWith('Error') ? '#fca5a5' : 'var(--accent-teal)',
                fontWeight: 600,
              }}>
                {audioUploadFeedback}
              </div>
            )}
          </div>

          {/* Caller Identity & Institutional Spoofing Verification Card */}
          <div style={{
            backgroundColor: 'var(--bg-surface)',
            border: callerIntel?.spoofing_suspected ? '1.5px solid var(--risk-high)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '22px',
            boxShadow: callerIntel?.spoofing_suspected ? '0 0 16px rgba(239, 68, 68, 0.2)' : 'none',
          }}>
            <h3 style={{
              fontSize: '1.05rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: '4px',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              <UserCheck size={18} color="var(--accent-cyan)" />
              <span>Caller Identity & Spoof Verification</span>
            </h3>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '14px' }}>
              Telecom circle mapping, ITU normalization, and official institutional conflict checks.
            </p>

            {/* Inputs */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginBottom: '12px' }}>
              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                  Incoming Caller Phone Number:
                </label>
                <input
                  type="text"
                  value={callerPhone}
                  onChange={(e) => setCallerPhone(e.target.value)}
                  placeholder="+91 98490 12345 or 1800 1234"
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    backgroundColor: 'var(--bg-surface-elevated)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-primary)',
                    fontSize: '0.9rem',
                    outline: 'none',
                  }}
                />
              </div>

              <div>
                <label style={{ display: 'block', fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '4px', fontWeight: 600 }}>
                  Claimed Organization (Optional):
                </label>
                <input
                  type="text"
                  value={claimedOrg}
                  onChange={(e) => setClaimedOrg(e.target.value)}
                  placeholder="e.g. State Bank of India, CBI, Courier"
                  style={{
                    width: '100%',
                    padding: '9px 12px',
                    backgroundColor: 'var(--bg-surface-elevated)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-primary)',
                    fontSize: '0.9rem',
                    outline: 'none',
                  }}
                />
              </div>

              <button
                onClick={() => handleVerifyCaller()}
                disabled={isLookingUpCaller || !callerPhone.trim()}
                style={{
                  padding: '9px 16px',
                  backgroundColor: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--accent-cyan)',
                  borderRadius: 'var(--radius-sm)',
                  color: 'var(--accent-cyan)',
                  fontWeight: 700,
                  fontSize: '0.88rem',
                  cursor: (isLookingUpCaller || !callerPhone.trim()) ? 'not-allowed' : 'pointer',
                  opacity: (isLookingUpCaller || !callerPhone.trim()) ? 0.5 : 1,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  gap: '6px',
                }}
              >
                <ShieldCheck size={16} />
                <span>{isLookingUpCaller ? 'Checking Telecom Registries...' : 'Verify Caller Number'}</span>
              </button>
            </div>

            {/* Quick Test Preset Buttons */}
            <div style={{ marginBottom: '14px' }}>
              <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)', marginBottom: '6px', fontWeight: 600 }}>
                Test Scenarios:
              </div>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
                <button
                  onClick={() => {
                    setCallerPhone('+91 98490 12345');
                    setClaimedOrg('State Bank of India');
                    handleVerifyCaller('+91 98490 12345', 'State Bank of India');
                  }}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: 'rgba(239, 68, 68, 0.15)',
                    border: '1px solid var(--risk-high-border)',
                    borderRadius: '4px',
                    color: '#fca5a5',
                    fontSize: '0.72rem',
                    cursor: 'pointer',
                  }}
                >
                  ⚠️ Spoof Mobile (SBI Claim)
                </button>

                <button
                  onClick={() => {
                    setCallerPhone('1800 1234');
                    setClaimedOrg('State Bank of India');
                    handleVerifyCaller('1800 1234', 'State Bank of India');
                  }}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: 'rgba(16, 185, 129, 0.15)',
                    border: '1px solid var(--risk-low-border)',
                    borderRadius: '4px',
                    color: '#6ee7b7',
                    fontSize: '0.72rem',
                    cursor: 'pointer',
                  }}
                >
                  🛡️ SBI Official Toll-Free
                </button>

                <button
                  onClick={() => {
                    setCallerPhone('1930');
                    setClaimedOrg('National Cybercrime');
                    handleVerifyCaller('1930', 'National Cybercrime');
                  }}
                  style={{
                    padding: '4px 8px',
                    backgroundColor: 'rgba(6, 182, 212, 0.15)',
                    border: '1px solid var(--accent-cyan)',
                    borderRadius: '4px',
                    color: 'var(--accent-cyan)',
                    fontSize: '0.72rem',
                    cursor: 'pointer',
                  }}
                >
                  📞 Cyber Helpline 1930
                </button>
              </div>
            </div>

            {/* Caller Intelligence Result Badge & Details */}
            {callerIntel && (
              <div style={{
                padding: '12px 14px',
                backgroundColor: callerIntel.spoofing_suspected
                  ? 'rgba(239, 68, 68, 0.16)'
                  : callerIntel.verdict === 'VERIFIED_INSTITUTION'
                  ? 'rgba(16, 185, 129, 0.15)'
                  : 'var(--bg-surface-elevated)',
                border: `1px solid ${
                  callerIntel.spoofing_suspected
                    ? 'var(--risk-high-border)'
                    : callerIntel.verdict === 'VERIFIED_INSTITUTION'
                    ? 'var(--risk-low-border)'
                    : 'var(--border-subtle)'
                }`,
                borderRadius: 'var(--radius-md)',
              }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '6px' }}>
                  <span style={{ fontSize: '0.86rem', fontWeight: 800, color: 'var(--text-primary)' }}>
                    {callerIntel.national_format || callerIntel.raw_input}
                  </span>
                  <span style={{
                    fontSize: '0.7rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    padding: '2px 7px',
                    borderRadius: '4px',
                    backgroundColor: callerIntel.spoofing_suspected
                      ? 'var(--risk-high)'
                      : callerIntel.verdict === 'VERIFIED_INSTITUTION'
                      ? 'var(--risk-low)'
                      : 'rgba(255, 255, 255, 0.1)',
                    color: '#ffffff',
                  }}>
                    {callerIntel.verdict.replace('_', ' ')}
                  </span>
                </div>

                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginBottom: '6px', display: 'flex', gap: '10px', flexWrap: 'wrap' }}>
                  <span>📡 {callerIntel.carrier || 'Telecom'}</span>
                  <span>📍 {callerIntel.geographic_region || 'India'}</span>
                  <span>🏷️ {callerIntel.number_type} line</span>
                </div>

                {callerIntel.registered_organization && (
                  <div style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--accent-teal)', marginBottom: '4px' }}>
                    Registered Entity: {callerIntel.registered_organization}
                  </div>
                )}

                <div style={{
                  fontSize: '0.8rem',
                  color: callerIntel.spoofing_suspected ? '#fca5a5' : 'var(--text-primary)',
                  fontWeight: callerIntel.spoofing_suspected ? 700 : 400,
                  marginTop: '6px',
                  lineHeight: 1.4,
                }}>
                  {callerIntel.advisory}
                </div>
              </div>
            )}
          </div>

          {/* Real-Time Risk Velocity Gauge Card */}
          <div style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '22px',
          }}>
            <h3 style={{
              fontSize: '1.05rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: '16px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
            }}>
              <span>Current Scam Risk Velocity</span>
              <span style={{
                fontSize: '0.76rem',
                fontWeight: 700,
                color: getScoreColor(currentScore),
                padding: '2px 8px',
                borderRadius: '4px',
                backgroundColor: currentScore >= 66 ? 'var(--risk-high-bg)' : currentScore >= 26 ? 'var(--risk-suspicious-bg)' : 'var(--risk-low-bg)',
                border: `1px solid ${getScoreColor(currentScore)}`,
              }}>
                {currentRiskLevel.replace('_', ' ')}
              </span>
            </h3>

            {/* Score Display Ring / Progress */}
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              flexDirection: 'column',
              padding: '14px 0',
            }}>
              <div style={{
                fontSize: '3.4rem',
                fontWeight: 900,
                letterSpacing: '-0.04em',
                color: getScoreColor(currentScore),
                lineHeight: 1,
              }}>
                {currentScore.toFixed(0)}
                <span style={{ fontSize: '1.2rem', color: 'var(--text-muted)', fontWeight: 600 }}>/100</span>
              </div>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '8px' }}>
                Index calibrated against ICFD-31k conversational fraud patterns
              </div>
            </div>

            {/* Color spectrum scale */}
            <div style={{ marginTop: '10px' }}>
              <div style={{
                height: '8px',
                borderRadius: '4px',
                background: 'linear-gradient(to right, #10b981 0%, #10b981 25%, #f59e0b 26%, #f59e0b 65%, #ef4444 66%, #ef4444 100%)',
                position: 'relative',
              }}>
                <div style={{
                  position: 'absolute',
                  top: '-4px',
                  left: `${Math.min(100, Math.max(0, currentScore))}%`,
                  width: '16px',
                  height: '16px',
                  borderRadius: '50%',
                  backgroundColor: '#ffffff',
                  boxShadow: '0 0 6px rgba(0,0,0,0.6)',
                  transform: 'translateX(-50%)',
                  border: `3px solid ${getScoreColor(currentScore)}`,
                  transition: 'left 0.25s ease',
                }} />
              </div>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: '6px' }}>
                <span>0 Safe</span>
                <span>25 Guarded</span>
                <span>65 Suspicious</span>
                <span>100 Critical</span>
              </div>
            </div>

            {/* If Final Assessment Ready -> Button to View Dossier */}
            {finalAssessment && (
              <div style={{
                marginTop: '18px',
                paddingTop: '16px',
                borderTop: '1px solid var(--border-subtle)',
              }}>
                <button
                  onClick={() => onLoadFullAnalysis(finalAssessment)}
                  style={{
                    width: '100%',
                    padding: '11px 16px',
                    backgroundColor: 'var(--bg-surface-elevated)',
                    border: '1.5px solid var(--accent-cyan)',
                    borderRadius: 'var(--radius-md)',
                    color: 'var(--accent-cyan)',
                    fontWeight: 700,
                    fontSize: '0.9rem',
                    cursor: 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    gap: '8px',
                  }}
                >
                  <span>Open Complete Evidence Dossier</span>
                  <ArrowRight size={16} />
                </button>
              </div>
            )}
          </div>

          {/* One-Click Real-Time Simulation Scenarios */}
          <div style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-lg)',
            padding: '20px',
          }}>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              fontSize: '0.95rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              marginBottom: '12px',
            }}>
              <Sparkles size={17} color="var(--accent-cyan)" />
              <span>Instant Live Call Demonstrations</span>
            </div>
            <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: '14px' }}>
              Simulates live conversational audio turn-by-turn with sub-second backend detection:
            </p>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
              {SIMULATED_CALLS.map((sim) => (
                <button
                  key={sim.id}
                  onClick={() => runSimulation(sim.id)}
                  disabled={isMonitoring}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'space-between',
                    padding: '10px 14px',
                    backgroundColor: 'var(--bg-surface-elevated)',
                    border: '1px solid var(--border-subtle)',
                    borderRadius: 'var(--radius-sm)',
                    color: 'var(--text-primary)',
                    fontSize: '0.86rem',
                    fontWeight: 600,
                    cursor: isMonitoring ? 'not-allowed' : 'pointer',
                    opacity: isMonitoring ? 0.5 : 1,
                    textAlign: 'left',
                  }}
                >
                  <div>
                    <div>{sim.title}</div>
                    <div style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>{sim.lang} • {sim.turns.length} turns</div>
                  </div>
                  <Play size={14} color="var(--accent-cyan)" />
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Right Column: Live Turn-by-Turn Spoken Dialogue Feed */}
        <div style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-lg)',
          display: 'flex',
          flexDirection: 'column',
          height: '680px',
          overflow: 'hidden',
        }}>
          {/* Feed Header */}
          <div style={{
            padding: '16px 20px',
            borderBottom: '1px solid var(--border-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            backgroundColor: 'var(--bg-surface-elevated)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Radio size={16} color="var(--accent-cyan)" />
              <span style={{ fontSize: '0.95rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Live Conversational Audio Feed
              </span>
              <span style={{
                fontSize: '0.75rem',
                padding: '2px 8px',
                borderRadius: '12px',
                backgroundColor: 'rgba(255, 255, 255, 0.08)',
                color: 'var(--text-secondary)',
              }}>
                {turns.length} turns
              </span>
            </div>

            {turns.length > 0 && (
              <button
                onClick={() => {
                  setTurns([]);
                  setCurrentScore(0);
                  setActiveWarning(null);
                  setFinalAssessment(null);
                }}
                disabled={isMonitoring || isSimulating}
                style={{
                  background: 'none',
                  border: 'none',
                  color: 'var(--text-muted)',
                  fontSize: '0.8rem',
                  cursor: (isMonitoring || isSimulating) ? 'not-allowed' : 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '4px',
                }}
              >
                <RotateCcw size={13} />
                <span>Clear Feed</span>
              </button>
            )}
          </div>

          {/* Turns Container */}
          <div style={{
            flex: 1,
            overflowY: 'auto',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '16px',
          }}>
            {turns.length === 0 ? (
              <div style={{
                height: '100%',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                textAlign: 'center',
                color: 'var(--text-muted)',
                padding: '40px 20px',
              }}>
                <Mic size={42} strokeWidth={1.5} style={{ marginBottom: '14px', opacity: 0.5 }} />
                <div style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-secondary)' }}>
                  Awaiting Audio or Conversation Stream
                </div>
                <p style={{ fontSize: '0.85rem', maxWidth: '360px', marginTop: '6px' }}>
                  Click "Start Live Microphone Protection", select a demo simulation on the left, or upload an audio recording to observe real-time fraud scoring.
                </p>
              </div>
            ) : (
              turns.map((turn) => {
                const isCaller = turn.speaker === 'Caller';
                const turnHighRisk = turn.level === 'HIGH_RISK';
                const turnSuspicious = turn.level === 'SUSPICIOUS';

                return (
                  <div
                    key={turn.id}
                    style={{
                      display: 'flex',
                      flexDirection: 'column',
                      alignItems: isCaller ? 'flex-start' : 'flex-end',
                    }}
                  >
                    {/* Speaker Header with Turn number and timestamp */}
                    <div style={{
                      display: 'flex',
                      alignItems: 'center',
                      gap: '8px',
                      fontSize: '0.76rem',
                      color: 'var(--text-secondary)',
                      marginBottom: '4px',
                    }}>
                      <span style={{
                        fontWeight: 700,
                        color: isCaller ? (turnHighRisk ? '#fca5a5' : 'var(--accent-cyan)') : 'var(--accent-teal)',
                      }}>
                        Turn #{turn.turnNumber}: {turn.speaker}
                      </span>
                      <span>•</span>
                      <span>{turn.timestamp}</span>
                      {turn.score !== undefined && (
                        <span style={{
                          padding: '1px 6px',
                          borderRadius: '4px',
                          fontSize: '0.72rem',
                          fontWeight: 700,
                          backgroundColor: turnHighRisk ? 'var(--risk-high-bg)' : turnSuspicious ? 'var(--risk-suspicious-bg)' : 'var(--risk-low-bg)',
                          color: turnHighRisk ? '#fca5a5' : turnSuspicious ? '#fcd34d' : '#6ee7b7',
                        }}>
                          Risk: {turn.score.toFixed(0)}
                        </span>
                      )}
                    </div>

                    {/* Speech Bubble */}
                    <div style={{
                      maxWidth: '85%',
                      padding: '12px 16px',
                      borderRadius: 'var(--radius-md)',
                      backgroundColor: isCaller
                        ? (turnHighRisk ? 'rgba(239, 68, 68, 0.16)' : 'var(--bg-surface-elevated)')
                        : 'rgba(20, 184, 166, 0.12)',
                      border: `1px solid ${
                        isCaller
                          ? (turnHighRisk ? 'var(--risk-high-border)' : 'var(--border-subtle)')
                          : 'rgba(20, 184, 166, 0.3)'
                      }`,
                      color: 'var(--text-primary)',
                      fontSize: '0.92rem',
                      lineHeight: 1.5,
                      boxShadow: turnHighRisk ? '0 0 14px rgba(239, 68, 68, 0.2)' : 'none',
                    }}>
                      {turn.text}

                      {/* Signals Tag Pills */}
                      {turn.detectedSignals && turn.detectedSignals.length > 0 && (
                        <div style={{
                          display: 'flex',
                          flexWrap: 'wrap',
                          gap: '6px',
                          marginTop: '8px',
                          paddingTop: '6px',
                          borderTop: '1px solid rgba(255, 255, 255, 0.08)',
                        }}>
                          {turn.detectedSignals.map((sig, sidx) => (
                            <span
                              key={sidx}
                              style={{
                                fontSize: '0.68rem',
                                fontWeight: 700,
                                textTransform: 'uppercase',
                                padding: '2px 6px',
                                borderRadius: '3px',
                                backgroundColor: 'rgba(239, 68, 68, 0.2)',
                                color: '#fca5a5',
                                border: '1px solid rgba(239, 68, 68, 0.4)',
                              }}
                            >
                              ⚠️ {sig}
                            </span>
                          ))}
                        </div>
                      )}
                    </div>
                  </div>
                );
              })
            )}
            <div ref={dialogueEndRef} />
          </div>

          {/* Footer Status Bar */}
          <div style={{
            padding: '12px 20px',
            borderTop: '1px solid var(--border-subtle)',
            backgroundColor: 'var(--bg-surface-elevated)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            fontSize: '0.78rem',
            color: 'var(--text-secondary)',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{
                width: '8px',
                height: '8px',
                borderRadius: '50%',
                backgroundColor: connectionStatus === 'connected' ? '#10b981' : connectionStatus === 'connecting' ? '#f59e0b' : '#64748b',
              }} />
              <span>
                Backend WebSocket: {connectionStatus === 'connected' ? 'Connected (ws://127.0.0.1:8000/ws/live-call)' : connectionStatus === 'connecting' ? 'Connecting...' : 'Ready'}
              </span>
            </div>
            <span>Language: {selectedLanguage}</span>
          </div>
        </div>
      </div>
    </div>
  );
};
