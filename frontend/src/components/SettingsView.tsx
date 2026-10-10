import React, { useState } from 'react';
import {
  Sliders,
  Type,
  Volume2,
  VolumeX,
  ShieldAlert,
  Server,
  Trash2,
  CheckCircle2,
  Lock,
  Phone,
  Copy,
  Check,
  RefreshCw,
  Eye,
  Info,
} from 'lucide-react';
import type { UserPreferences } from '../types';
import { fetchHealth } from '../api';
import { playRiskAlert } from '../utils/audioAlert';

interface SettingsViewProps {
  preferences: UserPreferences;
  onUpdatePreferences: (prefs: Partial<UserPreferences>) => void;
  onClearLocalHistory: () => void;
  localHistoryCount: number;
}

export const SettingsView: React.FC<SettingsViewProps> = ({
  preferences,
  onUpdatePreferences,
  onClearLocalHistory,
  localHistoryCount,
}) => {
  const [healthStatus, setHealthStatus] = useState<string | null>(null);
  const [healthLatency, setHealthLatency] = useState<number | null>(null);
  const [isTestingBackend, setIsTestingBackend] = useState<boolean>(false);
  const [copiedHelpline, setCopiedHelpline] = useState<boolean>(false);
  const [clearedConfirm, setClearedConfirm] = useState<boolean>(false);

  const testConnection = async () => {
    setIsTestingBackend(true);
    setHealthStatus(null);
    setHealthLatency(null);
    const start = performance.now();
    try {
      const data = await fetchHealth();
      const elapsed = Math.round(performance.now() - start);
      setHealthLatency(elapsed);
      setHealthStatus(
        `Connected to ${data.service} (${data.status.toUpperCase()}) • Engine: ${data.analysis_method}`
      );
    } catch {
      setHealthStatus('Connection failed: Unable to reach ElderShield backend service at 127.0.0.1:8000.');
    } finally {
      setIsTestingBackend(false);
    }
  };

  const copyHelplineNumber = () => {
    navigator.clipboard.writeText('1930');
    setCopiedHelpline(true);
    setTimeout(() => setCopiedHelpline(false), 2500);
  };

  const handleClearHistoryWithFeedback = () => {
    onClearLocalHistory();
    setClearedConfirm(true);
    setTimeout(() => setClearedConfirm(false), 3000);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '24px' }}>
      {/* Settings Header */}
      <div
        style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '24px',
          boxShadow: 'var(--shadow-card)',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
          <div
            style={{
              width: '40px',
              height: '40px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-soft-sage)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--brand-primary)',
            }}
          >
            <Sliders size={22} />
          </div>
          <div>
            <h2
              style={{
                fontSize: '1.28rem',
                fontWeight: 700,
                color: 'var(--text-primary)',
                letterSpacing: '-0.01em',
              }}
            >
              System Configuration & Privacy Governance
            </h2>
            <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)' }}>
              Configure senior accessibility, auditory alert parameters, local storage retention, and verify backend telemetry.
            </p>
          </div>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(340px, 1fr))', gap: '20px' }}>
        {/* Section 1: Senior Accessibility & Readability */}
        <div
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '22px',
            boxShadow: 'var(--shadow-card)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <Type size={18} color="var(--brand-primary)" />
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Senior Accessibility & Typography
              </h3>
            </div>

            {/* Font Size Selector */}
            <div style={{ marginBottom: '20px' }}>
              <label
                style={{
                  fontSize: '0.84rem',
                  fontWeight: 600,
                  color: 'var(--text-secondary)',
                  display: 'block',
                  marginBottom: '8px',
                }}
              >
                Interface Text Scaling
              </label>
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '8px' }}>
                {(['normal', 'large', 'xlarge'] as const).map((size) => {
                  const isSelected = preferences.fontSize === size;
                  return (
                    <button
                      key={size}
                      onClick={() => onUpdatePreferences({ fontSize: size })}
                      style={{
                        padding: '10px 8px',
                        borderRadius: 'var(--radius-sm)',
                        border: isSelected ? '1.5px solid var(--brand-primary)' : '1px solid var(--border-subtle)',
                        backgroundColor: isSelected ? 'var(--bg-soft-sage)' : 'var(--bg-primary)',
                        color: isSelected ? 'var(--brand-primary)' : 'var(--text-secondary)',
                        fontWeight: isSelected ? 700 : 500,
                        fontSize: size === 'normal' ? '0.82rem' : size === 'large' ? '0.92rem' : '1.02rem',
                        transition: 'all 0.12s ease',
                      }}
                    >
                      {size === 'normal' ? 'Standard' : size === 'large' ? 'Large (17px)' : 'Max (19px)'}
                    </button>
                  );
                })}
              </div>
            </div>

            {/* High Contrast Mode */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '14px 0',
                borderTop: '1px solid var(--divider-subtle)',
              }}
            >
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  <Eye size={15} color="var(--brand-primary)" />
                  <span>High Contrast Mode</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Amplifies border contrast and text definition for low-vision seniors.
                </div>
              </div>
              <button
                onClick={() => onUpdatePreferences({ highContrast: !preferences.highContrast })}
                style={{
                  padding: '7px 14px',
                  borderRadius: 'var(--radius-full)',
                  border: preferences.highContrast ? '1px solid var(--brand-primary)' : '1px solid var(--border-subtle)',
                  backgroundColor: preferences.highContrast ? 'var(--brand-primary)' : 'var(--bg-secondary)',
                  color: preferences.highContrast ? 'var(--text-on-brand)' : 'var(--text-secondary)',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  transition: 'all 0.12s ease',
                }}
              >
                {preferences.highContrast ? 'Active' : 'Disabled'}
              </button>
            </div>

            {/* Auditory Chimes & Sound Test */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '14px',
                borderTop: '1px solid var(--divider-subtle)',
              }}
            >
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '6px' }}>
                  {preferences.soundAlerts ? <Volume2 size={15} color="var(--brand-primary)" /> : <VolumeX size={15} color="var(--text-muted)" />}
                  <span>Auditory Alert Chimes</span>
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                  Generates distinct frequency tones when suspicious behavior is intercepted.
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                {preferences.soundAlerts && (
                  <button
                    onClick={() => playRiskAlert('HIGH_RISK')}
                    title="Test High-Risk tone chime"
                    style={{
                      padding: '5px 9px',
                      borderRadius: 'var(--radius-sm)',
                      backgroundColor: 'var(--bg-secondary)',
                      border: '1px solid var(--border-subtle)',
                      fontSize: '0.74rem',
                      fontWeight: 600,
                      color: 'var(--text-secondary)',
                    }}
                  >
                    Test Tone
                  </button>
                )}
                <button
                  onClick={() => onUpdatePreferences({ soundAlerts: !preferences.soundAlerts })}
                  style={{
                    padding: '7px 14px',
                    borderRadius: 'var(--radius-full)',
                    border: preferences.soundAlerts ? '1px solid var(--brand-primary)' : '1px solid var(--border-subtle)',
                    backgroundColor: preferences.soundAlerts ? 'var(--brand-primary)' : 'var(--bg-secondary)',
                    color: preferences.soundAlerts ? 'var(--text-on-brand)' : 'var(--text-secondary)',
                    fontSize: '0.8rem',
                    fontWeight: 600,
                    transition: 'all 0.12s ease',
                  }}
                >
                  {preferences.soundAlerts ? 'Active' : 'Muted'}
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Section 2: Privacy Governance & Zero-Retention Architecture */}
        <div
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '22px',
            boxShadow: 'var(--shadow-card)',
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <Lock size={18} color="var(--brand-primary)" />
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Privacy Governance & Zero-Retention
              </h3>
            </div>

            {/* Storage Mode Toggle */}
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingBottom: '14px',
                borderBottom: '1px solid var(--divider-subtle)',
                marginBottom: '14px',
              }}
            >
              <div>
                <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Local Browser Persistence
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-secondary)', marginTop: '2px', maxWidth: '240px' }}>
                  If disabled, all scan traces and transcripts evaporate immediately upon tab closure.
                </div>
              </div>
              <button
                onClick={() => onUpdatePreferences({ saveHistoryLocally: !preferences.saveHistoryLocally })}
                style={{
                  padding: '7px 14px',
                  borderRadius: 'var(--radius-full)',
                  border: preferences.saveHistoryLocally ? '1px solid var(--brand-primary)' : '1px solid var(--border-subtle)',
                  backgroundColor: preferences.saveHistoryLocally ? 'var(--bg-soft-sage)' : 'var(--bg-secondary)',
                  color: preferences.saveHistoryLocally ? 'var(--brand-primary)' : 'var(--text-secondary)',
                  fontSize: '0.8rem',
                  fontWeight: 600,
                  transition: 'all 0.12s ease',
                }}
              >
                {preferences.saveHistoryLocally ? 'Retaining (Local)' : 'Session Only'}
              </button>
            </div>

            {/* Zero-Cloud-Retention Guarantee Banner */}
            <div
              style={{
                padding: '12px 14px',
                backgroundColor: 'var(--bg-soft-sage)',
                borderRadius: 'var(--radius-sm)',
                border: '1px solid var(--brand-subtle)',
                marginBottom: '16px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'flex-start', gap: '8px' }}>
                <CheckCircle2 size={16} color="var(--brand-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
                <div style={{ fontSize: '0.8rem', color: 'var(--brand-primary)', lineHeight: 1.45 }}>
                  <strong>Zero-Cloud Retention Guarantee:</strong> Audio streams and dialogue transcripts are processed strictly in-memory. No voice data or conversation buffers are ever uploaded to third-party cloud servers.
                </div>
              </div>
            </div>
          </div>

          {/* Clear History Button */}
          <div>
            <button
              onClick={handleClearHistoryWithFeedback}
              disabled={localHistoryCount === 0}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 16px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: localHistoryCount === 0 ? 'var(--disabled-bg)' : 'var(--risk-high-bg)',
                border: `1px solid ${localHistoryCount === 0 ? 'var(--disabled-border)' : 'var(--risk-high-border)'}`,
                color: localHistoryCount === 0 ? 'var(--disabled-text)' : 'var(--risk-high)',
                fontSize: '0.84rem',
                fontWeight: 600,
                cursor: localHistoryCount === 0 ? 'not-allowed' : 'pointer',
                transition: 'all 0.12s ease',
              }}
            >
              {clearedConfirm ? (
                <>
                  <Check size={16} />
                  <span>Local History Cleared!</span>
                </>
              ) : (
                <>
                  <Trash2 size={16} />
                  <span>Clear Browser History ({localHistoryCount} stored)</span>
                </>
              )}
            </button>
          </div>
        </div>

        {/* Section 3: Detection Engine & Telemetry */}
        <div
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '22px',
            boxShadow: 'var(--shadow-card)',
            gridColumn: '1 / -1',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px', marginBottom: '16px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <Server size={18} color="var(--brand-primary)" />
              <div>
                <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Backend Detection Engine & Architecture
                </h3>
                <p style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                  ElderShield FastAPI service operating locally on <code>127.0.0.1:8000</code>.
                </p>
              </div>
            </div>

            <button
              onClick={testConnection}
              disabled={isTestingBackend}
              className="btn-primary"
              style={{ padding: '8px 16px', fontSize: '0.84rem' }}
            >
              <RefreshCw size={14} className={isTestingBackend ? 'animate-spin' : ''} />
              <span>{isTestingBackend ? 'Pinging Engine...' : 'Ping Backend Health'}</span>
            </button>
          </div>

          {/* Diagnostic Result Callout */}
          {healthStatus && (
            <div
              style={{
                marginBottom: '16px',
                padding: '12px 16px',
                backgroundColor: healthStatus.includes('Connected') ? 'var(--bg-soft-sage)' : 'var(--risk-high-bg)',
                border: `1px solid ${healthStatus.includes('Connected') ? 'var(--brand-subtle)' : 'var(--risk-high-border)'}`,
                borderRadius: 'var(--radius-sm)',
                fontSize: '0.84rem',
                color: healthStatus.includes('Connected') ? 'var(--brand-primary)' : 'var(--risk-high)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                flexWrap: 'wrap',
                gap: '8px',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                {healthStatus.includes('Connected') ? <CheckCircle2 size={16} /> : <ShieldAlert size={16} />}
                <span>{healthStatus}</span>
              </div>
              {healthLatency !== null && (
                <span style={{ fontSize: '0.78rem', fontWeight: 700, opacity: 0.9 }}>
                  Latency: {healthLatency}ms
                </span>
              )}
            </div>
          )}

          {/* Registered Engine Endpoints Grid */}
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
              gap: '12px',
              padding: '14px',
              backgroundColor: 'var(--bg-primary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
            }}
          >
            <div>
              <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                Acoustic WebSocket
              </div>
              <div style={{ fontSize: '0.82rem', fontFamily: 'monospace', color: 'var(--text-primary)', marginTop: '2px' }}>
                ws://127.0.0.1:8000/ws/live-call
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                Speech & Audio Ingestion
              </div>
              <div style={{ fontSize: '0.82rem', fontFamily: 'monospace', color: 'var(--text-primary)', marginTop: '2px' }}>
                POST /api/analyze/audio
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                Caller Intelligence
              </div>
              <div style={{ fontSize: '0.82rem', fontFamily: 'monospace', color: 'var(--text-primary)', marginTop: '2px' }}>
                POST /api/caller-lookup
              </div>
            </div>

            <div>
              <div style={{ fontSize: '0.74rem', textTransform: 'uppercase', color: 'var(--text-muted)', fontWeight: 700 }}>
                Turn-by-Turn Velocity
              </div>
              <div style={{ fontSize: '0.82rem', fontFamily: 'monospace', color: 'var(--text-primary)', marginTop: '2px' }}>
                POST /api/analyze/progression
              </div>
            </div>
          </div>
        </div>

        {/* Section 4: National Cybercrime Registry & Senior Safety Protocols */}
        <div
          style={{
            backgroundColor: 'var(--bg-surface)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '22px',
            boxShadow: 'var(--shadow-card)',
            gridColumn: '1 / -1',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '14px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
              <div
                style={{
                  width: '42px',
                  height: '42px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--risk-high-bg)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--risk-high)',
                }}
              >
                <Phone size={22} />
              </div>
              <div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    National Cybercrime Helpline: 1930
                  </h3>
                  <span
                    style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      padding: '2px 8px',
                      borderRadius: 'var(--radius-full)',
                      backgroundColor: 'var(--risk-high-bg)',
                      border: '1px solid var(--risk-high-border)',
                      color: 'var(--risk-high)',
                    }}
                  >
                    MHA / I4C Authorized
                  </span>
                </div>
                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                  In case of fraudulent money transfers or OTP disclosure, contact 1930 within the golden hour to initiate immediate financial freezing.
                </p>
              </div>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <button
                onClick={copyHelplineNumber}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-secondary)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-primary)',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                }}
              >
                {copiedHelpline ? <Check size={14} color="var(--brand-primary)" /> : <Copy size={14} />}
                <span>{copiedHelpline ? 'Copied 1930' : 'Copy Number'}</span>
              </button>

              <a
                href="tel:1930"
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 16px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--risk-high)',
                  color: '#FFFFFF',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                }}
              >
                <Phone size={14} />
                <span>Call 1930</span>
              </a>
            </div>
          </div>

          <div
            style={{
              marginTop: '16px',
              padding: '12px 14px',
              backgroundColor: 'var(--bg-primary)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              fontSize: '0.8rem',
              color: 'var(--text-secondary)',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}
          >
            <Info size={15} color="var(--text-muted)" style={{ flexShrink: 0 }} />
            <span>
              Official Cybercrime Reporting Portal: <a href="https://cybercrime.gov.in" target="_blank" rel="noreferrer" style={{ color: 'var(--brand-primary)', textDecoration: 'underline' }}>cybercrime.gov.in</a> • Hack With Vizag 4.0 (HWV4-PS05)
            </span>
          </div>
        </div>
      </div>
    </div>
  );
};
