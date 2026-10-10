import React, { useState, useEffect, useRef } from 'react';
import {
  Mic,
  MicOff,
  Radio,
  PhoneOff,
  Play,
  Pause,
  RotateCcw,
  Clock,
  Activity,
  FileAudio,
  X,
  ArrowRight,
  AlertOctagon,
  Phone,
} from 'lucide-react';
import type {
  RiskAssessment,
  RiskLevel,
  LiveWarning,
  OtpRiskState,
  OtpInterventionEvent,
} from '../types';
import { getLiveCallWsUrl, analyzeAudioFile, analyzeConversation } from '../api';
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
  onOpenCallerLookup?: () => void;
}

// Built-in live demo simulation scripts
const SIMULATED_CALLS = [
  {
    id: 'sim_cbi_arrest',
    title: 'CBI Digital Arrest (High Risk)',
    lang: 'English / Hinglish',
    description: 'Impersonation of Central Bureau of Investigation claiming seized contraband, issuing false arrest warrants, and demanding RBI escrow transfer.',
    turns: [
      { speaker: 'Caller' as const, text: 'This is Officer Sharma from Central Bureau of Investigation, New Delhi headquarters.' },
      { speaker: 'Senior' as const, text: 'Hello, why are you calling me?' },
      { speaker: 'Caller' as const, text: 'A parcel addressed to you containing fake passports and contraband was intercepted at Mumbai customs. You are under digital arrest.' },
      { speaker: 'Senior' as const, text: 'Oh God! I have never ordered any parcel! Please help me.' },
      { speaker: 'Caller' as const, text: 'Do not disconnect this call or inform your family, otherwise local police will be dispatched to arrest you immediately.' },
      { speaker: 'Caller' as const, text: 'To prove your innocence and clear your bank account from money laundering charges, transfer 85,000 rupees to our RBI verification escrow account right now.' },
    ],
  },
  {
    id: 'sim_bank_otp',
    title: 'SBI NetBanking Expiry (High Risk — OTP Solicitation)',
    lang: 'English / Hindi',
    description: 'Bank impersonator threatening immediate account suspension and demanding immediate dictation of a 6-digit verification code.',
    turns: [
      { speaker: 'Caller' as const, text: 'Good morning sir, I am calling from State Bank of India cards security division.' },
      { speaker: 'Senior' as const, text: 'Yes, what is the issue with my card?' },
      { speaker: 'Caller' as const, text: 'Your debit card and NetBanking services are expiring today. Your account will be frozen within one hour.' },
      { speaker: 'Senior' as const, text: 'How do I stop it from getting frozen?' },
      { speaker: 'Caller' as const, text: 'I am sending a 6-digit verification code to your registered mobile. Read the OTP immediately to update your KYC.' },
    ],
  },
  {
    id: 'sim_legit_courier',
    title: 'Legitimate Courier Delivery (Low Risk)',
    lang: 'English',
    description: 'Standard delivery coordination advising the senior to never disclose verification codes over the phone.',
    turns: [
      { speaker: 'Caller' as const, text: 'Hello, I am calling from BlueDart courier regarding your parcel delivery scheduled today.' },
      { speaker: 'Senior' as const, text: 'Yes, I am expecting a book delivery. What time will you arrive?' },
      { speaker: 'Caller' as const, text: 'I will be at your address by 3 PM. Remember, never share any OTP or payment credentials with anyone over the phone.' },
      { speaker: 'Senior' as const, text: 'Understood, thank you. See you at 3 PM.' },
    ],
  },
];

// Helper to mask sensitive OTP digits for elder privacy
function maskSensitiveDigits(text: string): string {
  return text.replace(/\b(\d{4,8})\b/g, (match) => {
    return '•'.repeat(match.length);
  });
}

// High-fidelity linear interpolation downsampler from any hardware sample rate to 16,000 Hz
function resampleTo16k(input: Float32Array, inputSampleRate: number): Int16Array {
  if (inputSampleRate === 16000) {
    const pcm16 = new Int16Array(input.length);
    for (let i = 0; i < input.length; i++) {
      const s = Math.max(-1, Math.min(1, input[i]));
      pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
    }
    return pcm16;
  }
  const ratio = inputSampleRate / 16000;
  const outputLength = Math.floor(input.length / ratio);
  const pcm16 = new Int16Array(outputLength);
  for (let i = 0; i < outputLength; i++) {
    const srcPos = i * ratio;
    const srcIndex = Math.floor(srcPos);
    const frac = srcPos - srcIndex;
    const s1 = input[srcIndex];
    const s2 = srcIndex + 1 < input.length ? input[srcIndex + 1] : s1;
    const interpolated = s1 + frac * (s2 - s1);
    const s = Math.max(-1, Math.min(1, interpolated));
    pcm16[i] = s < 0 ? s * 0x8000 : s * 0x7FFF;
  }
  return pcm16;
}

// Memory-efficient fast base64 converter for Int16Array PCM buffers
function pcm16ToBase64(pcm16: Int16Array): string {
  const uint8 = new Uint8Array(pcm16.buffer, pcm16.byteOffset, pcm16.byteLength);
  let binary = '';
  const len = uint8.byteLength;
  const chunkSize = 0x8000;
  for (let i = 0; i < len; i += chunkSize) {
    const sub = uint8.subarray(i, Math.min(i + chunkSize, len));
    binary += String.fromCharCode.apply(null, sub as unknown as number[]);
  }
  return window.btoa(binary);
}

export const LiveCallMonitor: React.FC<LiveCallMonitorProps> = ({
  onLoadFullAnalysis,
  soundAlertsEnabled,
  onOpenCallerLookup,
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
  const [interimSpeech, setInterimSpeech] = useState<string>('');

  // Runtime Streaming Diagnostics
  const [chunksSentCount, setChunksSentCount] = useState<number>(0);
  const [totalBytesSent, setTotalBytesSent] = useState<number>(0);
  const [chunksAckedCount, setChunksAckedCount] = useState<number>(0);
  const [transcriptsCount, setTranscriptsCount] = useState<number>(0);
  const [inputSampleRate, setInputSampleRate] = useState<number>(16000);

  // OTP Disclosure Prevention state machine
  const [otpState, setOtpState] = useState<OtpRiskState>('IDLE');
  const [activeOtpIntervention, setActiveOtpIntervention] = useState<OtpInterventionEvent | null>(null);
  const [isWarningDismissed, setIsWarningDismissed] = useState<boolean>(false);

  // Upload state
  const [isUploadingAudio, setIsUploadingAudio] = useState<boolean>(false);
  const [audioUploadFeedback, setAudioUploadFeedback] = useState<string | null>(null);

  // Simulation state
  const [isSimulating, setIsSimulating] = useState<boolean>(false);

  // Latest full assessment result from this session
  const [finalAssessment, setFinalAssessment] = useState<RiskAssessment | null>(null);

  // Pause and Audible Alert States
  const [isPaused, setIsPaused] = useState<boolean>(false);
  const isPausedRef = useRef<boolean>(false);
  const lastWarningFingerprintRef = useRef<string>('');
  const lastWarningTimeRef = useRef<number>(0);

  // Refs for audio and websocket
  const wsRef = useRef<WebSocket | null>(null);
  const mediaStreamRef = useRef<MediaStream | null>(null);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const speechRecognizerRef = useRef<SpeechRecognitionLike | null>(null);
  const audioContextRef = useRef<AudioContext | null>(null);
  const processorNodeRef = useRef<ScriptProcessorNode | null>(null);
  const sourceNodeRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const muteGainRef = useRef<GainNode | null>(null);
  const pingIntervalRef = useRef<number | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sessionTimerRef = useRef<number | null>(null);
  const sequenceIdRef = useRef<number>(0);
  const turnsRef = useRef<LiveTurn[]>([]);

  useEffect(() => {
    turnsRef.current = turns;
  }, [turns]);

  useEffect(() => {
    return () => {
      stopLiveMonitoring();
    };
  }, []);

  // Senior-friendly audible announcement with speech synthesis
  const announceAudibleWarning = (title: string, message: string) => {
    if (!soundAlertsEnabled) return;
    const now = Date.now();
    const fingerprint = `${title}:${message}`;
    if (lastWarningFingerprintRef.current === fingerprint && now - lastWarningTimeRef.current < 4000) return;
    lastWarningFingerprintRef.current = fingerprint;
    lastWarningTimeRef.current = now;

    playRiskAlert('HIGH_RISK');
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
        const speechText = message.trim() ? `${title}. ${message}` : title;
        const utterance = new SpeechSynthesisUtterance(speechText);
        utterance.rate = 0.95;
        utterance.pitch = 1.0;
        window.speechSynthesis.speak(utterance);
      } catch {
        // ignore
      }
    }
  };

  const announceAudibleIntervention = (spokenText: string, langHint?: string) => {
    if (!soundAlertsEnabled) return;
    const now = Date.now();
    if (lastWarningFingerprintRef.current === spokenText && now - lastWarningTimeRef.current < 5000) return;
    lastWarningFingerprintRef.current = spokenText;
    lastWarningTimeRef.current = now;

    playRiskAlert('HIGH_RISK');
    if ('speechSynthesis' in window) {
      try {
        window.speechSynthesis.cancel();
        const utterance = new SpeechSynthesisUtterance(spokenText);
        utterance.rate = 0.9;
        utterance.pitch = 1.0;
        if (langHint === 'hi' || langHint === 'hi-IN') {
          utterance.lang = 'hi-IN';
        } else if (langHint === 'te' || langHint === 'te-IN') {
          utterance.lang = 'te-IN';
        } else {
          utterance.lang = 'en-IN';
        }
        window.speechSynthesis.speak(utterance);
      } catch {
        // ignore
      }
    }
  };

  // Timer for active monitoring
  useEffect(() => {
    if (isMonitoring && !isPaused) {
      sessionTimerRef.current = window.setInterval(() => {
        setSessionDuration((prev) => prev + 1);
      }, 1000);
    } else {
      if (sessionTimerRef.current) {
        clearInterval(sessionTimerRef.current);
        sessionTimerRef.current = null;
      }
    }
    return () => {
      if (sessionTimerRef.current) {
        clearInterval(sessionTimerRef.current);
      }
    };
  }, [isMonitoring, isPaused]);

  // Audio level polling for visual microphone meter
  useEffect(() => {
    let animFrame: number;
    const checkAudioLevel = () => {
      if (analyserRef.current && isMonitoring && !isPaused) {
        const dataArray = new Uint8Array(analyserRef.current.frequencyBinCount);
        analyserRef.current.getByteFrequencyData(dataArray);
        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const avg = sum / dataArray.length;
        setMicAudioLevel(Math.min(100, Math.round((avg / 128) * 100)));
      } else {
        setMicAudioLevel(0);
      }
      animFrame = requestAnimationFrame(checkAudioLevel);
    };
    if (isMonitoring) {
      checkAudioLevel();
    }
    return () => cancelAnimationFrame(animFrame);
  }, [isMonitoring, isPaused]);

  // Stop monitoring clean-up
  const stopLiveMonitoring = () => {
    setIsMonitoring(false);
    setIsSimulating(false);
    setConnectionStatus('idle');
    setInterimSpeech('');

    if (pingIntervalRef.current) {
      clearInterval(pingIntervalRef.current);
      pingIntervalRef.current = null;
    }

    if (wsRef.current) {
      try {
        if (wsRef.current.readyState === WebSocket.OPEN) {
          // Send final stop flush command so backend processes remaining speech
          wsRef.current.send(JSON.stringify({ type: 'stop' }));
          const currentWs = wsRef.current;
          setTimeout(() => {
            try { currentWs.close(1000, 'Session stopped by user'); } catch {}
          }, 200);
        } else {
          wsRef.current.close(1000, 'Session stopped by user');
        }
      } catch {
        // ignore
      }
      wsRef.current = null;
    }

    if (processorNodeRef.current) {
      try {
        processorNodeRef.current.onaudioprocess = null;
        processorNodeRef.current.disconnect();
      } catch {}
      processorNodeRef.current = null;
    }

    if (sourceNodeRef.current) {
      try { sourceNodeRef.current.disconnect(); } catch {}
      sourceNodeRef.current = null;
    }

    if (muteGainRef.current) {
      try { muteGainRef.current.disconnect(); } catch {}
      muteGainRef.current = null;
    }

    if (speechRecognizerRef.current) {
      try {
        speechRecognizerRef.current.stop();
      } catch {
        // ignore
      }
      speechRecognizerRef.current = null;
    }

    if (mediaRecorderRef.current && mediaRecorderRef.current.state !== 'inactive') {
      try {
        mediaRecorderRef.current.stop();
      } catch {
        // ignore
      }
      mediaRecorderRef.current = null;
    }

    if (mediaStreamRef.current) {
      mediaStreamRef.current.getTracks().forEach((t) => t.stop());
      mediaStreamRef.current = null;
    }

    if (audioContextRef.current && audioContextRef.current.state !== 'closed') {
      try {
        audioContextRef.current.close();
      } catch {
        // ignore
      }
      audioContextRef.current = null;
    }
    analyserRef.current = null;
  };

  // Start Live Monitoring via WebSocket + Microphone
  const startLiveMonitoring = async () => {
    stopLiveMonitoring();
    setMicError(null);
    setInterimSpeech('');
    setTurns([]);
    setCurrentScore(0);
    setCurrentRiskLevel('LOW_RISK');
    setActiveWarning(null);
    setActiveOtpIntervention(null);
    setIsWarningDismissed(false);
    setSessionDuration(0);
    setFinalAssessment(null);
    setChunksSentCount(0);
    setTotalBytesSent(0);
    setChunksAckedCount(0);
    setTranscriptsCount(0);
    setConnectionStatus('connecting');
    setOtpState('CONNECTING');

    // 1. Initialize AudioContext synchronously first so user gesture is attached directly
    const AudioCtxClass = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
    let audioCtx: AudioContext | null = null;
    if (AudioCtxClass) {
      try {
        audioCtx = new AudioCtxClass();
        audioContextRef.current = audioCtx;
        setInputSampleRate(audioCtx.sampleRate);
        if (audioCtx.state === 'suspended') {
          audioCtx.resume().catch(() => {});
        }
      } catch (e) {
        console.warn('AudioContext initialization note', e);
      }
    }

    // 2. Establish WebSocket Connection
    try {
      const wsUrl = getLiveCallWsUrl();
      const ws = new WebSocket(wsUrl);
      wsRef.current = ws;

      ws.onopen = () => {
        setConnectionStatus('connected');
        setIsMonitoring(true);
        setOtpState('MONITORING');

        // Resilient heartbeat: ping every 10 seconds to keep connection alive across proxies
        if (pingIntervalRef.current) clearInterval(pingIntervalRef.current);
        pingIntervalRef.current = window.setInterval(() => {
          if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
            wsRef.current.send(JSON.stringify({ type: 'ping', timestamp: Date.now() }));
          }
        }, 10000);
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleIncomingWsMessage(data);
        } catch (e) {
          console.warn('Malformed WS message', e);
        }
      };

      ws.onerror = (e) => {
        console.warn('Live WebSocket error', e);
        setConnectionStatus('disconnected');
        setOtpState('ERROR');
      };

      ws.onclose = () => {
        if (pingIntervalRef.current) {
          clearInterval(pingIntervalRef.current);
          pingIntervalRef.current = null;
        }
        setConnectionStatus('disconnected');
        setIsMonitoring(false);
      };
    } catch (err: unknown) {
      console.error('Failed to initialize WebSocket', err);
      setConnectionStatus('disconnected');
      setOtpState('ERROR');
      return;
    }

    // 3. Request Microphone Access
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: true,
        },
        video: false,
      });
      mediaStreamRef.current = stream;

      if (audioCtx) {
        if (audioCtx.state === 'suspended') {
          await audioCtx.resume();
        }

        const source = audioCtx.createMediaStreamSource(stream);
        sourceNodeRef.current = source;

        // Visual dB meter analyser
        const analyser = audioCtx.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);
        analyserRef.current = analyser;

        // ScriptProcessorNode producing exact 16kHz 16-bit Mono Little-Endian PCM frames for backend faster-whisper
        const bufferSize = 4096;
        const processor = audioCtx.createScriptProcessor(bufferSize, 1, 1);
        processorNodeRef.current = processor;
        // Keep persistent reference to prevent V8 GC collection
        (window as unknown as { __eldershield_processor?: ScriptProcessorNode }).__eldershield_processor = processor;

        let localSentChunks = 0;
        let localSentBytes = 0;

        processor.onaudioprocess = (e) => {
          if (isPausedRef.current || !wsRef.current || wsRef.current.readyState !== WebSocket.OPEN) return;
          const input = e.inputBuffer.getChannelData(0);
          if (!input || input.length === 0) return;

          // High-fidelity downsample from hardware sample rate to 16,000 Hz PCM
          const pcm16 = resampleTo16k(input, audioCtx.sampleRate);
          if (pcm16.length === 0) return;

          const b64 = pcm16ToBase64(pcm16);
          sequenceIdRef.current++;
          const seq = sequenceIdRef.current;
          const byteLen = pcm16.byteLength;

          wsRef.current.send(
            JSON.stringify({
              type: 'audio_chunk',
              sequence_id: seq,
              chunk: b64,
              client_time_ms: Date.now(),
            })
          );

          localSentChunks++;
          localSentBytes += byteLen;
          if (localSentChunks % 6 === 0) {
            setChunksSentCount(localSentChunks);
            setTotalBytesSent(localSentBytes);
          }
        };

        // Mute gain node avoids routing mic sound into user laptop speakers
        // Value 1e-6 (-120 dB) prevents Chromium silent-device sleep while remaining inaudible
        const muteGain = audioCtx.createGain();
        muteGain.gain.value = 0.000001;
        muteGainRef.current = muteGain;

        source.connect(processor);
        processor.connect(muteGain);
        muteGain.connect(audioCtx.destination);
      }

      // 4. Web Speech API for immediate client speech-to-text
      initSpeechRecognition();
    } catch (err: unknown) {
      console.warn('Microphone permission rejected or not available', err);
      setMicError('Microphone access was denied or is not available. Please allow microphone access in your browser settings.');
    }
  };

  // Web Speech API initialization with real-time interim results
  const initSpeechRecognition = () => {
    const win = window as unknown as WindowWithSpeech;
    const SpeechRec = win.SpeechRecognition || win.webkitSpeechRecognition;

    if (!SpeechRec) {
      console.warn('Browser SpeechRecognition not supported');
      return;
    }

    const rec = new SpeechRec();
    speechRecognizerRef.current = rec;
    rec.continuous = true;
    rec.interimResults = true;
    rec.lang = selectedLanguage;

    rec.onresult = (event: SpeechRecognitionEventLike) => {
      if (isPausedRef.current) return;
      let interimTranscript = '';
      for (let i = event.resultIndex; i < event.results.length; i++) {
        const res = event.results[i];
        const text = res[0].transcript.trim();
        const isFinal = res.isFinal;

        if (text) {
          if (isFinal) {
            handleNewRecognizedTurn(text, 'Caller');
            setInterimSpeech('');
          } else {
            interimTranscript += text + ' ';
          }
        }
      }
      if (interimTranscript.trim()) {
        setInterimSpeech(interimTranscript.trim());
      }
    };

    rec.onerror = (e) => {
      console.warn('SpeechRecognition error', e);
    };

    rec.onend = () => {
      if (isMonitoring && !isPausedRef.current && speechRecognizerRef.current) {
        try {
          speechRecognizerRef.current.start();
        } catch {
          // ignore
        }
      }
    };

    try {
      rec.start();
    } catch {
      // ignore
    }
  };

  // Process incoming turn from client speech recognition or simulated audio
  const handleNewRecognizedTurn = (text: string, speaker: 'Caller' | 'Senior') => {
    setInterimSpeech('');
    const cleanText = text.trim();
    if (!cleanText) return;

    setTurns((prev) => {
      if (prev.length > 0 && prev[prev.length - 1].text.trim().toLowerCase() === cleanText.toLowerCase()) {
        return prev;
      }
      const turnNumber = prev.length + 1;
      return [
        ...prev,
        {
          id: `turn_${turnNumber}_${Date.now()}`,
          turnNumber,
          speaker,
          text: cleanText,
          timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
          isFinal: true,
        },
      ];
    });

    // Send transcript segment to backend over WebSocket
    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          type: 'transcript_segment',
          turn_number: turnsRef.current.length + 1,
          speaker,
          text: cleanText,
          client_capture_time_ms: Date.now(),
        })
      );
    }
  };

  // Handle server WebSocket messages
  const handleIncomingWsMessage = (data: Record<string, unknown>) => {
    const msgType = data.type as string;

    if (msgType === 'chunk_ack') {
      setChunksAckedCount((c) => c + 1);
      return;
    }

    if (msgType === 'pong') {
      return;
    }

    if (msgType === 'risk_update') {
      const riskLevel = (data.risk_level as RiskLevel) || 'LOW_RISK';
      const riskScore = (data.risk_score as number) || 0;
      const detectedOtpState = (data.otp_state as OtpRiskState) || 'SAFE_OR_INCONCLUSIVE';
      const recognizedText = data.text as string | undefined;
      const speaker = (data.speaker as string) || 'Caller';

      setCurrentRiskLevel(riskLevel);
      setCurrentScore(riskScore);
      setOtpState(detectedOtpState);

      // Append recognized speech turn from server ASR to live dialogue stream
      if (recognizedText && recognizedText.trim()) {
        const cleanText = recognizedText.trim();
        setTranscriptsCount((t) => t + 1);
        setTurns((prev) => {
          if (prev.length > 0 && prev[prev.length - 1].text.trim().toLowerCase() === cleanText.toLowerCase()) {
            return prev;
          }
          const turnNumber = prev.length + 1;
          return [
            ...prev,
            {
              id: `ws_turn_${turnNumber}_${Date.now()}`,
              turnNumber,
              speaker: speaker === 'Senior' ? 'Senior' : 'Caller',
              text: cleanText,
              timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
              isFinal: true,
            },
          ];
        });
      }

      // Play alert sound if elevated
      if (riskLevel === 'HIGH_RISK') {
        playRiskAlert('HIGH_RISK');
      } else if (riskLevel === 'SUSPICIOUS') {
        playRiskAlert('SUSPICIOUS');
      }
    } else if (msgType === 'otp_intervention') {
      const interventionEvent: OtpInterventionEvent = {
        type: 'otp_intervention',
        event_id: (data.event_id as string) || `event_${Date.now()}`,
        session_id: (data.session_id as string) || '',
        otp_state: (data.otp_state as OtpRiskState) || 'URGENT_INTERVENTION',
        heading: (data.heading as string) || 'DO NOT SHARE YOUR OTP',
        message: (data.message as string) || 'Never tell anyone your verification code.',
        spoken_text: (data.spoken_text as string) || 'Stop! Do not share your OTP code.',
        language: (data.language as string) || 'en',
        evidence_quotes: (data.evidence_quotes as string[]) || [],
        timestamp: (data.timestamp as number) || Date.now(),
      };

      setOtpState('URGENT_INTERVENTION');
      setActiveOtpIntervention(interventionEvent);
      setIsWarningDismissed(false);
      setCurrentRiskLevel('HIGH_RISK');

      announceAudibleIntervention(interventionEvent.spoken_text, interventionEvent.language);
    } else if (msgType === 'warning') {
      const warn: LiveWarning = {
        type: 'warning',
        severity: (data.severity as 'CRITICAL' | 'HIGH') || 'HIGH',
        title: (data.title as string) || 'SCAM ALERT',
        message: (data.message as string) || 'Manipulative tactics detected.',
        evidence_quotes: (data.evidence_quotes as string[]) || [],
        timestamp: (data.timestamp as number) || Date.now(),
        otp_state: (data.otp_state as OtpRiskState) || 'OTP_RISK_DETECTED',
        spoken_text: (data.spoken_text as string) || undefined,
      };

      setActiveWarning(warn);
      announceAudibleWarning(warn.title, warn.spoken_text || warn.message);
    }
  };

  // Toggle pause monitoring
  const togglePauseMonitoring = () => {
    if (!isMonitoring) return;
    const nextPaused = !isPaused;
    setIsPaused(nextPaused);
    isPausedRef.current = nextPaused;

    if (nextPaused) {
      if (speechRecognizerRef.current) {
        try { speechRecognizerRef.current.stop(); } catch { /* ignore */ }
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'recording') {
        try { mediaRecorderRef.current.pause(); } catch { /* ignore */ }
      }
    } else {
      if (speechRecognizerRef.current) {
        try { speechRecognizerRef.current.start(); } catch { /* ignore */ }
      }
      if (mediaRecorderRef.current && mediaRecorderRef.current.state === 'paused') {
        try { mediaRecorderRef.current.resume(); } catch { /* ignore */ }
      }
    }
  };

  // Reset live session
  const handleResetSession = () => {
    stopLiveMonitoring();
    setTurns([]);
    setCurrentScore(0);
    setCurrentRiskLevel('LOW_RISK');
    setActiveWarning(null);
    setActiveOtpIntervention(null);
    setIsWarningDismissed(false);
    setOtpState('IDLE');
    setFinalAssessment(null);
    setSessionDuration(0);
  };

  // Run benchmark simulation
  const handleRunSimulation = async (sim: typeof SIMULATED_CALLS[0]) => {
    stopLiveMonitoring();
    setIsSimulating(true);
    setTurns([]);
    setCurrentScore(0);
    setCurrentRiskLevel('LOW_RISK');
    setActiveWarning(null);
    setActiveOtpIntervention(null);
    setIsWarningDismissed(false);
    setConnectionStatus('connected');
    setSessionDuration(0);

    // Play turns with staggered intervals
    for (let i = 0; i < sim.turns.length; i++) {
      const turnItem = sim.turns[i];
      const turnNum = i + 1;

      const newTurn: LiveTurn = {
        id: `sim_turn_${turnNum}_${Date.now()}`,
        turnNumber: turnNum,
        speaker: turnItem.speaker,
        text: turnItem.text,
        timestamp: new Date().toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
        isFinal: true,
      };

      setTurns((prev) => [...prev, newTurn]);

      // Analyze accumulated turns with backend
      const transcriptSoFar = [...sim.turns.slice(0, i + 1)].map((t) => `${t.speaker}: ${t.text}`).join('\n');
      try {
        const assessment = await analyzeConversation(transcriptSoFar);
        setCurrentScore(assessment.risk_score);
        setCurrentRiskLevel(assessment.risk_level);

        if (assessment.otp_state) {
          setOtpState(assessment.otp_state);
        }

        if (assessment.urgent_intervention_required) {
          setOtpState('URGENT_INTERVENTION');
          const interventionEvent: OtpInterventionEvent = {
            type: 'otp_intervention',
            event_id: assessment.event_id || `sim_${Date.now()}`,
            session_id: `sim_session_${sim.id}`,
            otp_state: 'URGENT_INTERVENTION',
            heading: assessment.intervention_heading || 'DO NOT SHARE YOUR OTP',
            message: assessment.recommended_action || 'Never tell anyone your verification code.',
            spoken_text: assessment.intervention_spoken_text || 'Stop! Do not share your OTP code.',
            language: assessment.intervention_language || 'en',
            evidence_quotes: assessment.evidence.map((e) => e.exact_quote).slice(0, 3),
            timestamp: Date.now(),
          };
          setActiveOtpIntervention(interventionEvent);
          announceAudibleIntervention(interventionEvent.spoken_text, interventionEvent.language);
        } else if (assessment.risk_level === 'HIGH_RISK') {
          setActiveWarning({
            type: 'warning',
            severity: 'CRITICAL',
            title: 'URGENT SCAM DETECTED',
            message: assessment.recommended_action,
            evidence_quotes: assessment.evidence.map((e) => e.exact_quote).slice(0, 2),
            timestamp: Date.now(),
          });
          announceAudibleWarning('URGENT SCAM DETECTED', assessment.recommended_action);
        }

        if (i === sim.turns.length - 1) {
          setFinalAssessment(assessment);
        }
      } catch (e) {
        console.warn('Simulation evaluation error', e);
      }

      await new Promise((resolve) => setTimeout(resolve, 1400));
    }

    setIsSimulating(false);
  };

  // Handle raw audio recording file upload
  const handleAudioUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setIsUploadingAudio(true);
    setAudioUploadFeedback(null);

    try {
      const res = await analyzeAudioFile(file);
      setAudioUploadFeedback(
        `Transcribed ${res.audio_metrics.duration_seconds}s audio via faster-whisper in ${res.audio_metrics.transcription_latency_ms}ms.`
      );

      // Populate turns from faster-whisper segments or raw transcript
      if (res.segments && res.segments.length > 0) {
        const segTurns: LiveTurn[] = res.segments.map((seg, idx) => ({
          id: `upload_seg_${idx}_${Date.now()}`,
          turnNumber: idx + 1,
          speaker: 'Caller',
          text: seg.text,
          timestamp: `${seg.start.toFixed(1)}s – ${seg.end.toFixed(1)}s`,
          isFinal: true,
        }));
        setTurns(segTurns);
      } else {
        const rawText = res.transcript || '(No speech detected in audio file)';
        setTurns([
          {
            id: `upload_1_${Date.now()}`,
            turnNumber: 1,
            speaker: 'Caller',
            text: rawText,
            timestamp: new Date().toLocaleTimeString(),
            isFinal: true,
          },
        ]);
      }

      const assessment = res.risk_assessment;
      setCurrentScore(assessment.risk_score);
      setCurrentRiskLevel(assessment.risk_level);
      setFinalAssessment(assessment);

      if (assessment.urgent_intervention_required) {
        setOtpState('URGENT_INTERVENTION');
        setActiveOtpIntervention({
          type: 'otp_intervention',
          event_id: assessment.event_id || `upload_${Date.now()}`,
          session_id: `upload_session_${Date.now()}`,
          otp_state: 'URGENT_INTERVENTION',
          heading: assessment.intervention_heading || 'DO NOT SHARE YOUR OTP',
          message: assessment.recommended_action || 'Never tell anyone your verification code.',
          spoken_text: assessment.intervention_spoken_text || 'Stop! Do not share your OTP code.',
          language: assessment.intervention_language || 'en',
          evidence_quotes: assessment.evidence.map((e) => e.exact_quote).slice(0, 3),
          timestamp: Date.now(),
        });
        announceAudibleIntervention(assessment.intervention_spoken_text || 'Stop! Do not share your OTP code.');
      }
    } catch (err: unknown) {
      const msg = err instanceof Error ? err.message : 'Audio upload evaluation failed';
      setAudioUploadFeedback(`Error: ${msg}`);
    } finally {
      setIsUploadingAudio(false);
      event.target.value = '';
    }
  };

  // Format session duration mm:ss
  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* SECTION 7: DEDICATED HIGH-RISK OTP DISCLOSURE PREVENTION BANNER */}
      {(otpState === 'URGENT_INTERVENTION' || activeOtpIntervention) && !isWarningDismissed && (
        <div
          role="alert"
          aria-live="assertive"
          style={{
            padding: '24px 28px',
            backgroundColor: 'var(--high-risk-bg)',
            border: '2px solid var(--risk-high)',
            borderRadius: 'var(--radius-md)',
            boxShadow: 'var(--shadow-elevated)',
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '18px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '16px', maxWidth: '860px' }}>
            <div
              style={{
                width: '46px',
                height: '46px',
                borderRadius: '50%',
                backgroundColor: 'var(--risk-high)',
                color: '#FFFFFF',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <AlertOctagon size={26} strokeWidth={2.4} />
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
                <h2
                  style={{
                    fontFamily: 'var(--font-heading)',
                    fontSize: '1.4rem',
                    fontWeight: 800,
                    color: 'var(--risk-high)',
                    letterSpacing: '-0.02em',
                  }}
                >
                  {activeOtpIntervention?.heading || 'DO NOT SHARE YOUR OTP'}
                </h2>
                <span className="badge-danger">
                  Urgent Fraud Intervention
                </span>
              </div>

              <p
                style={{
                  fontSize: '1.02rem',
                  fontWeight: 600,
                  color: 'var(--text-primary)',
                  marginTop: '8px',
                  lineHeight: 1.5,
                }}
              >
                Never tell anyone your verification code. If someone is pressuring you, stop the conversation and verify their identity independently.
              </p>

              {activeOtpIntervention?.evidence_quotes && activeOtpIntervention.evidence_quotes.length > 0 && (
                <div
                  style={{
                    marginTop: '12px',
                    padding: '10px 14px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: 'rgba(200, 61, 67, 0.08)',
                    border: '1px solid var(--risk-high-border)',
                    fontSize: '0.86rem',
                    color: 'var(--text-primary)',
                  }}
                >
                  <span style={{ fontWeight: 700, color: 'var(--risk-high)' }}>Flagged Caller Demand: </span>
                  <em>"{activeOtpIntervention.evidence_quotes[0]}"</em>
                </div>
              )}

              <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginTop: '10px' }}>
                ℹ️ The Android ElderShield Companion App is actively vibrating and announcing spoken guidance to the senior.
              </p>
            </div>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', alignSelf: 'center' }}>
            <button
              onClick={() => setIsWarningDismissed(true)}
              className="btn-secondary"
              style={{
                borderColor: 'var(--risk-high-border)',
                color: 'var(--risk-high)',
                fontSize: '0.86rem',
                padding: '8px 16px',
              }}
            >
              <X size={15} />
              <span>Acknowledge Warning</span>
            </button>

            <a
              href="tel:1930"
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '6px',
                padding: '8px 16px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--risk-high)',
                color: '#FFFFFF',
                fontSize: '0.86rem',
                fontWeight: 700,
              }}
            >
              <Phone size={14} />
              <span>Speed-Dial 1930</span>
            </a>
          </div>
        </div>
      )}

      {/* Behavioral Warning Banner */}
      {activeWarning && !activeOtpIntervention && (
        <div
          role="alert"
          style={{
            backgroundColor: 'var(--risk-warning-bg)',
            border: '2px solid var(--risk-warning-border)',
            borderRadius: 'var(--radius-md)',
            padding: '16px 20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            gap: '12px',
            marginBottom: '20px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <AlertOctagon size={22} color="var(--risk-warning)" />
            <div>
              <strong style={{ color: 'var(--risk-warning)' }}>{activeWarning.title}</strong>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-primary)', margin: 0 }}>
                {activeWarning.message}
              </p>
            </div>
          </div>
          <button
            onClick={() => setActiveWarning(null)}
            className="btn-secondary"
            style={{ padding: '4px 10px', fontSize: '0.78rem' }}
          >
            Dismiss
          </button>
        </div>
      )}

      {/* SECTION 6: MONITORING PIPELINE STATUS & CONTROL PANEL */}
      <div className="es-card">
        {/* Status Strip Header */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px',
            paddingBottom: '20px',
            borderBottom: '1px solid var(--divider-subtle)',
          }}
        >
          {/* Active Status Explanation */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
            <div
              style={{
                width: '42px',
                height: '42px',
                borderRadius: 'var(--radius-md)',
                backgroundColor: isMonitoring
                  ? currentRiskLevel === 'HIGH_RISK'
                    ? 'var(--risk-high-bg)'
                    : currentRiskLevel === 'SUSPICIOUS'
                    ? 'var(--risk-warning-bg)'
                    : 'var(--bg-soft-sage)'
                  : 'var(--bg-secondary)',
                color: isMonitoring
                  ? currentRiskLevel === 'HIGH_RISK'
                    ? 'var(--risk-high)'
                    : currentRiskLevel === 'SUSPICIOUS'
                    ? 'var(--risk-warning)'
                    : 'var(--brand-primary)'
                  : 'var(--text-muted)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              {isMonitoring ? <Radio size={22} /> : <PhoneOff size={22} />}
            </div>

            <div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                <span
                  style={{
                    fontSize: '1.08rem',
                    fontWeight: 700,
                    color: 'var(--text-primary)',
                  }}
                >
                  {isMonitoring
                    ? isPaused
                      ? 'Live Audio Monitoring: PAUSED'
                      : 'Live Audio Monitoring: ACTIVE'
                    : isSimulating
                    ? 'Benchmark Simulation In Progress'
                    : 'Audio Monitoring: INACTIVE'}
                </span>

                {isMonitoring && (
                  <span
                    style={{
                      display: 'inline-flex',
                      alignItems: 'center',
                      gap: '5px',
                      fontSize: '0.78rem',
                      fontWeight: 600,
                      color: 'var(--brand-primary)',
                      backgroundColor: 'var(--bg-soft-sage)',
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                    }}
                  >
                    <span
                      style={{
                        width: '6px',
                        height: '6px',
                        borderRadius: '50%',
                        backgroundColor: 'var(--brand-primary)',
                      }}
                    />
                    WS ({connectionStatus})
                  </span>
                )}
              </div>

              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                {isMonitoring
                  ? isPaused
                    ? 'Audio stream temporarily paused. Click Resume to continue acoustic evaluation.'
                    : 'Receiving live microphone or speakerphone audio. Behavioral engine evaluates frames every 250ms.'
                  : 'Protection is not currently receiving audio. Click Start Live Monitoring or run a benchmark scenario to begin.'}
              </p>
            </div>
          </div>

          {/* Primary Action Buttons */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
            {!isMonitoring ? (
              <button
                onClick={startLiveMonitoring}
                className="btn-primary"
                style={{ padding: '10px 20px' }}
              >
                <Mic size={17} />
                <span>Start Live Protection</span>
              </button>
            ) : (
              <>
                <button
                  onClick={togglePauseMonitoring}
                  className="btn-secondary"
                  style={{ fontSize: '0.86rem', padding: '9px 15px' }}
                >
                  {isPaused ? <Play size={15} /> : <Pause size={15} />}
                  <span>{isPaused ? 'Resume' : 'Pause'}</span>
                </button>

                <button
                  onClick={stopLiveMonitoring}
                  className="btn-secondary"
                  style={{
                    fontSize: '0.86rem',
                    padding: '9px 15px',
                    borderColor: 'var(--risk-high-border)',
                    color: 'var(--risk-high)',
                  }}
                >
                  <MicOff size={15} />
                  <span>Stop Monitoring</span>
                </button>
              </>
            )}

            {onOpenCallerLookup && (
              <button
                onClick={onOpenCallerLookup}
                className="btn-secondary"
                title="Verify Caller Identity"
                style={{ fontSize: '0.86rem', padding: '9px 14px' }}
              >
                <Phone size={15} />
                <span>Verify Caller</span>
              </button>
            )}

            <button
              onClick={handleResetSession}
              className="btn-secondary"
              title="Reset session and clear dialogue"
              style={{ fontSize: '0.86rem', padding: '9px 12px' }}
            >
              <RotateCcw size={15} />
            </button>
          </div>
        </div>

        {/* Telemetry Row: Duration, Audio Meter, Language Selector, Score */}
        <div
          style={{
            marginTop: '18px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '16px',
            fontSize: '0.85rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '18px', flexWrap: 'wrap' }}>
            {/* Session Duration */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)' }}>
              <Clock size={15} color="var(--text-muted)" />
              <span>Session Duration: <strong>{formatTime(sessionDuration)}</strong></span>
            </div>

            {/* Mic Meter (Active Only) */}
            {isMonitoring && (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ color: 'var(--text-secondary)' }}>Mic Input:</span>
                <div
                  style={{
                    width: '80px',
                    height: '8px',
                    borderRadius: '4px',
                    backgroundColor: 'var(--bg-secondary)',
                    overflow: 'hidden',
                  }}
                >
                  <div
                    style={{
                      height: '100%',
                      width: `${micAudioLevel}%`,
                      backgroundColor: 'var(--brand-primary)',
                      transition: 'width 0.1s ease',
                    }}
                  />
                </div>
              </div>
            )}

            {/* Language Selector */}
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
              <label htmlFor="lang-select" style={{ color: 'var(--text-secondary)' }}>Language:</label>
              <select
                id="lang-select"
                value={selectedLanguage}
                onChange={(e) => setSelectedLanguage(e.target.value)}
                disabled={isMonitoring}
                style={{
                  padding: '4px 8px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--border-subtle)',
                  backgroundColor: 'var(--bg-primary)',
                  color: 'var(--text-primary)',
                  fontSize: '0.82rem',
                }}
              >
                <option value="en-IN">English (India)</option>
                <option value="hi-IN">हिन्दी (Hindi)</option>
                <option value="te-IN">తెలుగు (Telugu)</option>
                <option value="en-US">English (US)</option>
              </select>
            </div>
          </div>

          {/* Current Evaluation Score Badge */}
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ color: 'var(--text-secondary)' }}>Current Risk:</span>
            <span
              style={{
                fontWeight: 700,
                fontSize: '0.94rem',
                color:
                  currentRiskLevel === 'HIGH_RISK'
                    ? 'var(--risk-high)'
                    : currentRiskLevel === 'SUSPICIOUS'
                    ? 'var(--risk-warning)'
                    : 'var(--brand-primary)',
              }}
            >
              {currentScore}/100 ({currentRiskLevel})
            </span>
          </div>
        </div>

        {/* Live Acoustic & WebSocket Stream Telemetry */}
        {isMonitoring && (
          <div
            style={{
              marginTop: '12px',
              padding: '6px 12px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              display: 'flex',
              alignItems: 'center',
              flexWrap: 'wrap',
              gap: '14px',
              fontSize: '0.78rem',
              color: 'var(--text-secondary)',
            }}
          >
            <span>Mic Resampler: <strong>{inputSampleRate} Hz → 16 kHz PCM</strong></span>
            <span>Audio Chunks Sent: <strong>{chunksSentCount}</strong> ({(totalBytesSent / 1024).toFixed(1)} KB)</span>
            <span>Server ACKs: <strong>{chunksAckedCount}</strong></span>
            <span>ASR Turns: <strong>{transcriptsCount}</strong></span>
          </div>
        )}

        {/* Microphone Error Banner */}
        {micError && (
          <div
            style={{
              marginTop: '14px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--warning-bg)',
              border: '1px solid var(--warning-border)',
              color: 'var(--warning-amber)',
              fontSize: '0.84rem',
              fontWeight: 500,
            }}
          >
            {micError}
          </div>
        )}
      </div>

      {/* BENCHMARK TEST SCENARIOS (FOR CONTROLLED EXPERIMENTS) */}
      <div className="es-card">
        <div style={{ marginBottom: '14px' }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Benchmark Test Scenarios
          </h3>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Run controlled, non-private test transcripts through the live WebSocket streaming pipeline without making real phone calls.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: '12px' }}>
          {SIMULATED_CALLS.map((sim) => (
            <div
              key={sim.id}
              style={{
                padding: '14px 16px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-subtle)',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '4px' }}>
                  <span style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    {sim.title}
                  </span>
                  <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>{sim.lang}</span>
                </div>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                  {sim.description}
                </p>
              </div>

              <button
                onClick={() => handleRunSimulation(sim)}
                disabled={isSimulating || isMonitoring}
                className="btn-secondary"
                style={{
                  marginTop: '12px',
                  fontSize: '0.8rem',
                  padding: '6px 12px',
                  alignSelf: 'flex-start',
                }}
              >
                <Play size={13} />
                <span>Run Simulation ({sim.turns.length} turns)</span>
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* AUDIO FILE UPLOAD PIPELINE */}
      <div className="es-card">
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <FileAudio size={18} color="var(--brand-primary)" />
              <span>Analyze Call Audio Recording (WAV / MP3)</span>
            </h3>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Upload recorded speech to transcribe with server-side faster-whisper and execute multi-turn scam evaluation.
            </p>
          </div>

          <label
            className="btn-secondary"
            style={{
              cursor: isUploadingAudio ? 'not-allowed' : 'pointer',
              fontSize: '0.84rem',
              padding: '8px 14px',
            }}
          >
            <input
              type="file"
              accept=".wav,.mp3,.m4a"
              onChange={handleAudioUpload}
              disabled={isUploadingAudio}
              style={{ display: 'none' }}
            />
            <span>{isUploadingAudio ? 'Transcribing & Analyzing...' : 'Upload Recording File'}</span>
          </label>
        </div>

        {audioUploadFeedback && (
          <div
            style={{
              marginTop: '12px',
              padding: '10px 14px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-secondary)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.82rem',
              color: 'var(--text-primary)',
            }}
          >
            {audioUploadFeedback}
          </div>
        )}
      </div>

      {/* LIVE DIALOGUE STREAM (READABLE TRANSCRIPT FEED) */}
      <div className="es-card">
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            marginBottom: '16px',
            paddingBottom: '12px',
            borderBottom: '1px solid var(--divider-subtle)',
          }}
        >
          <div>
            <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Dialogue Transcript & Turn Stream
            </h3>
            <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Transcribed conversational speech frames with private verification digits masked.
            </p>
          </div>

          {finalAssessment && (
            <button
              onClick={() => onLoadFullAnalysis(finalAssessment)}
              className="btn-primary"
              style={{ fontSize: '0.84rem', padding: '6px 14px' }}
            >
              <span>View Full Evidence Ledger</span>
              <ArrowRight size={14} />
            </button>
          )}
        </div>

        {/* Turn Cards Container */}
        {turns.length > 0 || interimSpeech ? (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', maxHeight: '420px', overflowY: 'auto', paddingRight: '4px' }}>
            {turns.map((turn) => {
              const isCaller = turn.speaker === 'Caller';
              return (
                <div
                  key={turn.id}
                  style={{
                    padding: '12px 16px',
                    borderRadius: 'var(--radius-sm)',
                    backgroundColor: isCaller ? 'var(--bg-primary)' : 'var(--bg-soft-sage)',
                    border: `1px solid ${isCaller ? 'var(--border-subtle)' : 'var(--brand-subtle)'}`,
                    display: 'flex',
                    flexDirection: 'column',
                    gap: '4px',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                      <span
                        style={{
                          fontSize: '0.74rem',
                          fontWeight: 700,
                          padding: '2px 7px',
                          borderRadius: 'var(--radius-full)',
                          backgroundColor: isCaller ? 'var(--bg-secondary)' : 'var(--brand-primary)',
                          color: isCaller ? 'var(--text-primary)' : '#FFFFFF',
                        }}
                      >
                        {turn.speaker} • Turn {turn.turnNumber}
                      </span>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{turn.timestamp}</span>
                    </div>
                  </div>

                  <p style={{ fontSize: '0.92rem', color: 'var(--text-primary)', lineHeight: 1.5, marginTop: '2px' }}>
                    {maskSensitiveDigits(turn.text)}
                  </p>
                </div>
              );
            })}

            {interimSpeech && (
              <div
                style={{
                  padding: '12px 16px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-soft-sage)',
                  border: '1px dashed var(--brand-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '10px',
                  color: 'var(--brand-primary)',
                  fontSize: '0.92rem',
                }}
              >
                <Radio size={16} />
                <span>
                  <strong>Listening:</strong> <em>"{interimSpeech}..."</em>
                </span>
              </div>
            )}
          </div>
        ) : (
          <div
            style={{
              padding: '36px 20px',
              textAlign: 'center',
              backgroundColor: 'var(--bg-primary)',
              border: '1px dashed var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-secondary)',
            }}
          >
            <Activity size={26} color="var(--text-muted)" style={{ margin: '0 auto 8px' }} />
            <h4 style={{ fontSize: '0.96rem', fontWeight: 600, color: 'var(--text-primary)' }}>
              No Conversational Speech Recorded Yet
            </h4>
            <p style={{ fontSize: '0.84rem', maxWidth: '420px', margin: '4px auto 0' }}>
              When live monitoring starts or an audio simulation runs, recognized dialogue turns will stream here in real time.
            </p>
          </div>
        )}
      </div>
    </div>
  );
};
