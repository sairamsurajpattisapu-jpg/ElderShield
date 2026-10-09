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
} from 'lucide-react';
import type { UserPreferences } from '../types';
import { fetchHealth } from '../api';

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
  const [isTestingBackend, setIsTestingBackend] = useState<boolean>(false);

  const testConnection = async () => {
    setIsTestingBackend(true);
    setHealthStatus(null);
    try {
      const data = await fetchHealth();
      setHealthStatus(`Connected: ${data.service} (${data.status.toUpperCase()}) • Method: ${data.analysis_method}`);
    } catch {
      setHealthStatus('Connection failed: Unable to reach ElderShield backend service.');
    } finally {
      setIsTestingBackend(false);
    }
  };

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: '28px',
      marginBottom: '32px',
    }}>
      <div style={{ marginBottom: '24px' }}>
        <h2 style={{
          fontSize: '1.35rem',
          fontWeight: 700,
          color: 'var(--text-primary)',
          display: 'flex',
          alignItems: 'center',
          gap: '10px',
        }}>
          <Sliders size={22} color="var(--accent-cyan)" />
          <span>Application Settings & Privacy Preferences</span>
        </h2>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
          Configure senior accessibility, display scaling, and transcript data retention controls.
        </p>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: '20px' }}>
        {/* Section 1: Display & Accessibility */}
        <div style={{
          backgroundColor: 'var(--bg-primary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Type size={18} color="var(--accent-cyan)" />
            <span>Senior Typography & Readability</span>
          </h3>

          <div style={{ marginBottom: '18px' }}>
            <label style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', display: 'block', marginBottom: '8px' }}>
              Base Text Size
            </label>
            <div style={{ display: 'flex', gap: '8px' }}>
              {(['normal', 'large', 'xlarge'] as const).map((size) => (
                <button
                  key={size}
                  onClick={() => onUpdatePreferences({ fontSize: size })}
                  style={{
                    flex: 1,
                    padding: '8px 12px',
                    borderRadius: 'var(--radius-sm)',
                    border: preferences.fontSize === size ? '1.5px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                    backgroundColor: preferences.fontSize === size ? 'rgba(6, 182, 212, 0.15)' : 'var(--bg-surface-elevated)',
                    color: preferences.fontSize === size ? 'var(--accent-cyan)' : 'var(--text-secondary)',
                    fontWeight: preferences.fontSize === size ? 700 : 500,
                    fontSize: '0.85rem',
                    textTransform: 'capitalize',
                  }}
                >
                  {size === 'normal' ? 'Standard' : size === 'large' ? 'Large' : 'Extra Large'}
                </button>
              ))}
            </div>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: '12px',
            borderTop: '1px solid var(--border-subtle)',
          }}>
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>High Contrast Mode</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Maximizes borders and luminescence</div>
            </div>
            <button
              onClick={() => onUpdatePreferences({ highContrast: !preferences.highContrast })}
              style={{
                padding: '6px 14px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: preferences.highContrast ? 'var(--text-primary)' : 'var(--bg-surface-elevated)',
                color: preferences.highContrast ? 'var(--bg-primary)' : 'var(--text-secondary)',
                border: '1px solid var(--border-subtle)',
                fontSize: '0.82rem',
                fontWeight: 600,
              }}
            >
              {preferences.highContrast ? 'Enabled' : 'Disabled'}
            </button>
          </div>

          <div style={{
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            paddingTop: '14px',
            marginTop: '12px',
            borderTop: '1px solid var(--border-subtle)',
          }}>
            <div>
              <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>Audio Alert Chimes</div>
              <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Synthesized tones for seniors</div>
            </div>
            <button
              onClick={() => onUpdatePreferences({ soundAlerts: !preferences.soundAlerts })}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 14px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: preferences.soundAlerts ? 'rgba(6, 182, 212, 0.15)' : 'var(--bg-surface-elevated)',
                color: preferences.soundAlerts ? 'var(--accent-cyan)' : 'var(--text-muted)',
                border: preferences.soundAlerts ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                fontSize: '0.82rem',
                fontWeight: 600,
              }}
            >
              {preferences.soundAlerts ? <Volume2 size={15} /> : <VolumeX size={15} />}
              <span>{preferences.soundAlerts ? 'Active' : 'Muted'}</span>
            </button>
          </div>
        </div>

        {/* Section 2: Privacy & Data Retention */}
        <div style={{
          backgroundColor: 'var(--bg-primary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'space-between',
        }}>
          <div>
            <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Lock size={18} color="var(--accent-teal)" />
              <span>Transcript Privacy & Local Storage</span>
            </h3>

            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '16px',
            }}>
              <div>
                <div style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Retain Transcripts in Browser
                </div>
                <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)', maxWidth: '240px' }}>
                  If disabled, transcripts are discarded at session end and never stored.
                </div>
              </div>
              <button
                onClick={() => onUpdatePreferences({ saveHistoryLocally: !preferences.saveHistoryLocally })}
                style={{
                  padding: '6px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: preferences.saveHistoryLocally ? 'rgba(16, 185, 129, 0.15)' : 'var(--bg-surface-elevated)',
                  color: preferences.saveHistoryLocally ? 'var(--risk-low)' : 'var(--text-muted)',
                  border: preferences.saveHistoryLocally ? '1px solid var(--risk-low-border)' : '1px solid var(--border-subtle)',
                  fontSize: '0.82rem',
                  fontWeight: 600,
                }}
              >
                {preferences.saveHistoryLocally ? 'Retaining' : 'Session Only'}
              </button>
            </div>

            <div style={{
              padding: '12px 14px',
              backgroundColor: 'var(--bg-surface-elevated)',
              borderRadius: 'var(--radius-sm)',
              border: '1px solid var(--border-subtle)',
              marginBottom: '16px',
            }}>
              <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                ElderShield strictly avoids retaining raw telephone conversations permanently without consent. All evaluations are processed in-memory.
              </div>
            </div>
          </div>

          <div>
            <button
              onClick={onClearLocalHistory}
              disabled={localHistoryCount === 0}
              style={{
                width: '100%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                padding: '10px 16px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'rgba(239, 68, 68, 0.12)',
                border: '1px solid var(--risk-high-border)',
                color: '#fca5a5',
                fontSize: '0.86rem',
                fontWeight: 600,
                cursor: localHistoryCount === 0 ? 'not-allowed' : 'pointer',
                opacity: localHistoryCount === 0 ? 0.5 : 1,
              }}
            >
              <Trash2 size={16} />
              <span>Clear Local History ({localHistoryCount} stored)</span>
            </button>
          </div>
        </div>

        {/* Section 3: Backend Diagnostic */}
        <div style={{
          backgroundColor: 'var(--bg-primary)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '20px',
          gridColumn: '1 / -1',
        }}>
          <h3 style={{ fontSize: '1rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '10px', display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Server size={18} color="var(--accent-cyan)" />
            <span>Detection Backend Connectivity & API Status</span>
          </h3>

          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
            <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
              Active Endpoint: <code>/health</code>, <code>/api/analyze</code>, <code>/api/analyze/progression</code>, <code>/api/demo-scenarios</code>
            </div>

            <button
              onClick={testConnection}
              disabled={isTestingBackend}
              style={{
                padding: '8px 16px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--accent-cyan)',
                color: '#080c16',
                border: 'none',
                fontWeight: 700,
                fontSize: '0.86rem',
              }}
            >
              {isTestingBackend ? 'Testing Connection...' : 'Ping Backend Health'}
            </button>
          </div>

          {healthStatus && (
            <div style={{
              marginTop: '12px',
              padding: '10px 14px',
              backgroundColor: healthStatus.includes('Connected') ? 'rgba(16, 185, 129, 0.12)' : 'rgba(239, 68, 68, 0.12)',
              border: `1px solid ${healthStatus.includes('Connected') ? 'var(--risk-low-border)' : 'var(--risk-high-border)'}`,
              borderRadius: 'var(--radius-sm)',
              fontSize: '0.85rem',
              color: healthStatus.includes('Connected') ? 'var(--risk-low)' : '#fca5a5',
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
            }}>
              {healthStatus.includes('Connected') ? <CheckCircle2 size={16} /> : <ShieldAlert size={16} />}
              <span>{healthStatus}</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
