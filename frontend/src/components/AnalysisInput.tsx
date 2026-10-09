import React from 'react';
import { Send, Trash2, Languages, Sparkles, MessageSquare } from 'lucide-react';

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
  const insertPrefix = (prefix: string) => {
    const trimmed = transcript.trim();
    if (!trimmed) {
      setTranscript(`${prefix}: `);
    } else {
      setTranscript(`${transcript}\n${prefix}: `);
    }
  };

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: '24px',
      marginBottom: '28px',
    }}>
      {/* Header of input area */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '14px',
      }}>
        <div>
          <h3 style={{
            fontSize: '1.15rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <MessageSquare size={19} color="var(--accent-cyan)" />
            <span>Conversation Transcript Input</span>
          </h3>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Paste any phone call transcript below. Supports English, Hindi (हिन्दी), Telugu (తెలుగు), and mixed dialects.
          </p>
        </div>

        {/* Language badges */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', flexWrap: 'wrap' }}>
          <span style={{
            fontSize: '0.72rem',
            color: 'var(--text-muted)',
            display: 'flex',
            alignItems: 'center',
            gap: '4px',
            marginRight: '4px',
          }}>
            <Languages size={14} /> Engine Support:
          </span>
          <span style={{ fontSize: '0.72rem', padding: '2px 7px', borderRadius: '4px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-subtle)' }}>English</span>
          <span style={{ fontSize: '0.72rem', padding: '2px 7px', borderRadius: '4px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-subtle)' }}>हिन्दी (Hindi)</span>
          <span style={{ fontSize: '0.72rem', padding: '2px 7px', borderRadius: '4px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-subtle)' }}>తెలుగు (Telugu)</span>
          <span style={{ fontSize: '0.72rem', padding: '2px 7px', borderRadius: '4px', background: 'var(--bg-surface-elevated)', border: '1px solid var(--border-subtle)' }}>Hinglish / Teluglish</span>
        </div>
      </div>

      {/* Demo loaded indicator */}
      {isDemoLoaded && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          padding: '10px 14px',
          backgroundColor: 'rgba(6, 182, 212, 0.1)',
          border: '1px solid rgba(6, 182, 212, 0.3)',
          borderRadius: 'var(--radius-md)',
          marginBottom: '14px',
          fontSize: '0.86rem',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--accent-cyan)' }}>
            <Sparkles size={16} />
            <span>Currently loaded: <strong>{demoScenarioTitle}</strong> (Deterministic Benchmark)</span>
          </div>
          <button
            onClick={onResetToCustom}
            style={{
              background: 'transparent',
              border: 'none',
              color: 'var(--text-secondary)',
              fontSize: '0.82rem',
              textDecoration: 'underline',
              cursor: 'pointer',
            }}
          >
            Clear & Write Custom
          </button>
        </div>
      )}

      {/* Transcript Textarea */}
      <div style={{ position: 'relative' }}>
        <textarea
          value={transcript}
          onChange={(e) => setTranscript(e.target.value)}
          placeholder={`Enter conversation transcript lines here, for example:\n\nCaller: Hello, I am calling from State Bank of India.\nSenior: Yes, what is this regarding?\nCaller: Your account needs urgent KYC verification, please share the 6-digit OTP right now.`}
          rows={8}
          style={{
            width: '100%',
            backgroundColor: 'var(--bg-primary)',
            border: '1.5px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '16px',
            color: 'var(--text-primary)',
            lineHeight: 1.6,
            resize: 'vertical',
            outline: 'none',
            fontSize: 'inherit',
          }}
          onFocus={(e) => e.target.style.borderColor = 'var(--accent-cyan)'}
          onBlur={(e) => e.target.style.borderColor = 'var(--border-subtle)'}
        />
      </div>

      {/* Quick turn helpers & action buttons */}
      <div style={{
        marginTop: '14px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
      }}>
        {/* Quick insertion chips */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>Quick Format:</span>
          <button
            type="button"
            onClick={() => insertPrefix('Caller')}
            style={{
              padding: '4px 10px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              fontSize: '0.82rem',
            }}
          >
            + Caller:
          </button>
          <button
            type="button"
            onClick={() => insertPrefix('Senior')}
            style={{
              padding: '4px 10px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              fontSize: '0.82rem',
            }}
          >
            + Senior:
          </button>
          {transcript && (
            <button
              type="button"
              onClick={() => setTranscript('')}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
                padding: '4px 10px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'transparent',
                border: 'none',
                color: 'var(--text-muted)',
                fontSize: '0.82rem',
              }}
            >
              <Trash2 size={13} />
              <span>Clear</span>
            </button>
          )}
        </div>

        {/* Submit button */}
        <button
          onClick={onAnalyze}
          disabled={isLoading || !transcript.trim()}
          style={{
            backgroundColor: 'var(--accent-cyan)',
            color: '#080c16',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            padding: '12px 26px',
            fontWeight: 700,
            fontSize: '0.98rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            cursor: isLoading || !transcript.trim() ? 'not-allowed' : 'pointer',
            opacity: isLoading || !transcript.trim() ? 0.6 : 1,
            boxShadow: '0 4px 14px rgba(6, 182, 212, 0.25)',
          }}
        >
          {isLoading ? (
            <>
              <div style={{
                width: '16px',
                height: '16px',
                border: '2px solid #080c16',
                borderTopColor: 'transparent',
                borderRadius: '50%',
                animation: 'spin 0.8s linear infinite',
              }} />
              <span>Analyzing Conversation...</span>
            </>
          ) : (
            <>
              <Send size={16} />
              <span>Analyze Conversation</span>
            </>
          )}
        </button>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
      `}</style>
    </div>
  );
};
