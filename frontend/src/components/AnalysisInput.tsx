import React, { useState } from 'react';
import { Send, Trash2, Languages, MessageSquare, Info, FileAudio, RefreshCw, AlertCircle } from 'lucide-react';
import { analyzeAudioFile } from '../api';

interface AnalysisInputProps {
  transcript: string;
  setTranscript: (val: string) => void;
  onAnalyze: () => void;
  isLoading: boolean;
  isDemoLoaded: boolean;
  demoScenarioTitle?: string;
  onResetToCustom: () => void;
}

export const AnalysisInput: React.FC<AnalysisInputProps> = ({
  transcript,
  setTranscript,
  onAnalyze,
  isLoading,
  isDemoLoaded,
  demoScenarioTitle,
  onResetToCustom,
}) => {
  const [isTranscribing, setIsTranscribing] = useState<boolean>(false);
  const [audioFeedback, setAudioFeedback] = useState<string | null>(null);

  const insertPrefix = (prefix: string) => {
    const trimmed = transcript.trim();
    if (!trimmed) {
      setTranscript(`${prefix}: `);
    } else {
      setTranscript(`${transcript}\n${prefix}: `);
    }
  };

  const handleAudioFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    setIsTranscribing(true);
    setAudioFeedback(null);
    try {
      const res = await analyzeAudioFile(file);
      if (res.transcript && res.transcript.trim()) {
        setTranscript(res.transcript.trim());
        setAudioFeedback(
          `Transcribed "${file.name}" (${res.audio_metrics.duration_seconds}s) via faster-whisper in ${res.audio_metrics.transcription_latency_ms}ms.`
        );
      } else {
        setAudioFeedback('Audio file was processed but no speech was detected.');
      }
    } catch (err: unknown) {
      setAudioFeedback(`Audio recognition error: ${err instanceof Error ? err.message : 'Transcription failed'}`);
    } finally {
      setIsTranscribing(false);
      e.target.value = '';
    }
  };

  const lineCount = transcript ? transcript.split('\n').filter((l) => l.trim().length > 0).length : 0;

  return (
    <div className="es-card" style={{ marginBottom: '24px' }}>
      {/* Header of input area */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '14px',
        }}
      >
        <div>
          <h3
            style={{
              fontSize: '1.15rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <MessageSquare size={18} color="var(--brand-primary)" />
            <span>Conversation Dialogue & Audio Input</span>
          </h3>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Paste dialogue text or upload a recorded call (.wav, .mp3) for server-side faster-whisper transcription.
          </p>
        </div>

        {/* Language badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span
            style={{
              fontSize: '0.74rem',
              color: 'var(--text-muted)',
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              marginRight: '2px',
            }}
          >
            <Languages size={13} /> Languages:
          </span>
          <span style={{ fontSize: '0.72rem', padding: '2px 7px', borderRadius: 'var(--radius-xs)', background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>English</span>
          <span style={{ fontSize: '0.72rem', padding: '2px 7px', borderRadius: 'var(--radius-xs)', background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>हिन्दी (Hindi)</span>
          <span style={{ fontSize: '0.72rem', padding: '2px 7px', borderRadius: 'var(--radius-xs)', background: 'var(--bg-secondary)', border: '1px solid var(--border-subtle)', color: 'var(--text-secondary)' }}>తెలుగు (Telugu)</span>
        </div>
      </div>

      {/* Demo loaded indicator */}
      {isDemoLoaded && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            padding: '10px 14px',
            backgroundColor: 'var(--bg-soft-sage)',
            border: '1px solid var(--brand-subtle)',
            borderRadius: 'var(--radius-sm)',
            marginBottom: '14px',
            fontSize: '0.84rem',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Info size={16} color="var(--brand-primary)" />
            <span>
              Loaded Benchmark Scenario: <strong>{demoScenarioTitle || 'Selected Scenario'}</strong>
            </span>
          </div>
          <button
            onClick={onResetToCustom}
            style={{
              background: 'none',
              border: 'none',
              color: 'var(--brand-primary)',
              cursor: 'pointer',
              fontSize: '0.8rem',
              fontWeight: 600,
              textDecoration: 'underline',
            }}
          >
            Clear to Custom
          </button>
        </div>
      )}

      {/* Audio upload feedback banner */}
      {audioFeedback && (
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            padding: '10px 14px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: audioFeedback.includes('error') ? 'var(--risk-high-bg)' : 'var(--bg-soft-sage)',
            border: `1px solid ${audioFeedback.includes('error') ? 'var(--risk-high-border)' : 'var(--brand-subtle)'}`,
            color: audioFeedback.includes('error') ? 'var(--risk-high)' : 'var(--brand-primary)',
            fontSize: '0.82rem',
            marginBottom: '14px',
          }}
        >
          {audioFeedback.includes('error') ? <AlertCircle size={15} /> : <FileAudio size={15} />}
          <span>{audioFeedback}</span>
        </div>
      )}

      {/* Quick Speaker Buttons */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Insert Speaker Prefix:</span>
        <button
          type="button"
          onClick={() => insertPrefix('Caller')}
          className="btn-secondary"
          style={{ fontSize: '0.76rem', padding: '3px 8px' }}
        >
          + Caller:
        </button>
        <button
          type="button"
          onClick={() => insertPrefix('Senior')}
          className="btn-secondary"
          style={{ fontSize: '0.76rem', padding: '3px 8px' }}
        >
          + Senior:
        </button>
      </div>

      {/* Textarea */}
      <textarea
        value={transcript}
        onChange={(e) => setTranscript(e.target.value)}
        placeholder="Paste conversation transcript here, e.g.:&#10;Caller: This is Officer Sharma from Central Bureau of Investigation.&#10;Senior: Hello, what is this regarding?&#10;Caller: A parcel in your name was intercepted. You are under digital arrest. Transfer 85,000 rupees immediately."
        rows={7}
        style={{
          width: '100%',
          padding: '12px 14px',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
          backgroundColor: 'var(--bg-primary)',
          color: 'var(--text-primary)',
          fontSize: '0.92rem',
          fontFamily: 'monospace',
          lineHeight: 1.5,
          resize: 'vertical',
        }}
      />

      {/* Footer Actions */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginTop: '12px',
        }}
      >
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          {lineCount} turn line(s) • {transcript.length} characters
        </span>

        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
          {/* Audio Upload File Selector */}
          <label
            className="btn-secondary"
            style={{
              fontSize: '0.82rem',
              padding: '7px 12px',
              cursor: isTranscribing ? 'not-allowed' : 'pointer',
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
            }}
            title="Upload .wav, .mp3 or .m4a call audio for automated faster-whisper transcription"
          >
            <input
              type="file"
              accept=".wav,.mp3,.m4a"
              onChange={handleAudioFile}
              disabled={isTranscribing}
              style={{ display: 'none' }}
            />
            {isTranscribing ? (
              <RefreshCw size={14} className="animate-spin" />
            ) : (
              <FileAudio size={14} color="var(--brand-primary)" />
            )}
            <span>{isTranscribing ? 'Transcribing...' : 'Upload Call Audio'}</span>
          </label>

          {transcript && (
            <button
              type="button"
              onClick={() => {
                setTranscript('');
                setAudioFeedback(null);
              }}
              className="btn-secondary"
              style={{ fontSize: '0.82rem', padding: '7px 12px' }}
            >
              <Trash2 size={14} />
              <span>Clear</span>
            </button>
          )}

          <button
            type="button"
            onClick={onAnalyze}
            disabled={isLoading || !transcript.trim()}
            className="btn-primary"
            style={{ fontSize: '0.88rem', padding: '8px 18px' }}
          >
            <Send size={15} />
            <span>{isLoading ? 'Evaluating Conversation...' : 'Evaluate Transcript'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
