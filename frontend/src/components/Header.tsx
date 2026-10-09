import React from 'react';
import { Shield, PhoneCall, Volume2, VolumeX, Eye, Type } from 'lucide-react';

interface HeaderProps {
  fontSize: 'normal' | 'large' | 'xlarge';
  setFontSize: (size: 'normal' | 'large' | 'xlarge') => void;
  highContrast: boolean;
  setHighContrast: (val: boolean) => void;
  soundEnabled: boolean;
  setSoundEnabled: (val: boolean) => void;
}

export const Header: React.FC<HeaderProps> = ({
  fontSize,
  setFontSize,
  highContrast,
  setHighContrast,
  soundEnabled,
  setSoundEnabled,
}) => {
  return (
    <header style={{
      backgroundColor: 'var(--bg-surface)',
      borderBottom: '1px solid var(--border-subtle)',
      padding: '16px 24px',
      position: 'sticky',
      top: 0,
      zIndex: 100,
      backdropFilter: 'blur(8px)',
    }}>
      <div style={{
        maxWidth: '1280px',
        margin: '0 auto',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        {/* Brand identity */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
          <div style={{
            width: '46px',
            height: '46px',
            borderRadius: '12px',
            backgroundColor: 'rgba(6, 182, 212, 0.12)',
            border: '1.5px solid var(--accent-cyan)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--accent-cyan)',
            boxShadow: '0 0 16px rgba(6, 182, 212, 0.2)',
          }}>
            <Shield size={26} strokeWidth={2.4} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h1 style={{
                fontSize: '1.4rem',
                fontWeight: 700,
                letterSpacing: '-0.02em',
                color: 'var(--text-primary)',
              }}>
                Elder<span style={{ color: 'var(--accent-cyan)' }}>Shield</span>
              </h1>
              <span style={{
                fontSize: '0.72rem',
                fontWeight: 600,
                textTransform: 'uppercase',
                letterSpacing: '0.06em',
                padding: '2px 8px',
                borderRadius: '4px',
                backgroundColor: 'rgba(20, 184, 166, 0.15)',
                color: 'var(--accent-teal)',
                border: '1px solid rgba(20, 184, 166, 0.3)',
              }}>
                HWV4-PS05 • Vizag
              </span>
            </div>
            <p style={{
              fontSize: '0.85rem',
              color: 'var(--text-secondary)',
              marginTop: '2px',
            }}>
              Real-Time Conversational Scam Detection for Elderly Users
            </p>
          </div>
        </div>

        {/* Emergency Helpline & Senior Accessibility Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexWrap: 'wrap' }}>
          {/* Cyber Helpline 1930 */}
          <a
            href="tel:1930"
            title="National Cyber Crime Reporting Helpline"
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px',
              padding: '8px 14px',
              backgroundColor: 'rgba(239, 68, 68, 0.12)',
              border: '1px solid var(--risk-high-border)',
              borderRadius: 'var(--radius-md)',
              color: '#fca5a5',
              textDecoration: 'none',
              fontWeight: 600,
              fontSize: '0.88rem',
              transition: 'all 0.2s ease',
            }}
          >
            <PhoneCall size={16} color="#ef4444" />
            <span>Cyber Helpline: <strong>1930</strong></span>
          </a>

          {/* Senior Accessibility Group */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            backgroundColor: 'var(--bg-surface-elevated)',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-md)',
            padding: '3px',
            gap: '2px',
          }}>
            {/* Font size toggles */}
            <button
              onClick={() => setFontSize('normal')}
              title="Standard Text Size"
              style={{
                background: fontSize === 'normal' ? 'var(--accent-cyan)' : 'transparent',
                color: fontSize === 'normal' ? '#080c16' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 10px',
                fontWeight: 600,
                fontSize: '0.8rem',
                display: 'flex',
                alignItems: 'center',
                gap: '4px',
              }}
            >
              <Type size={13} /> A
            </button>
            <button
              onClick={() => setFontSize('large')}
              title="Large Text for Seniors"
              style={{
                background: fontSize === 'large' ? 'var(--accent-cyan)' : 'transparent',
                color: fontSize === 'large' ? '#080c16' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 10px',
                fontWeight: 700,
                fontSize: '0.9rem',
              }}
            >
              A+
            </button>
            <button
              onClick={() => setFontSize('xlarge')}
              title="Extra Large Text for Seniors"
              style={{
                background: fontSize === 'xlarge' ? 'var(--accent-cyan)' : 'transparent',
                color: fontSize === 'xlarge' ? '#080c16' : 'var(--text-secondary)',
                border: 'none',
                borderRadius: 'var(--radius-sm)',
                padding: '6px 10px',
                fontWeight: 800,
                fontSize: '1rem',
              }}
            >
              A++
            </button>
          </div>

          {/* High Contrast Mode */}
          <button
            onClick={() => setHighContrast(!highContrast)}
            title={highContrast ? 'Standard Contrast' : 'Enable High Contrast'}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              backgroundColor: highContrast ? 'var(--text-primary)' : 'var(--bg-surface-elevated)',
              color: highContrast ? 'var(--bg-primary)' : 'var(--text-secondary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.82rem',
              fontWeight: 600,
            }}
          >
            <Eye size={15} />
            <span>{highContrast ? 'High Contrast On' : 'Contrast'}</span>
          </button>

          {/* Audio alert toggle */}
          <button
            onClick={() => setSoundEnabled(!soundEnabled)}
            title={soundEnabled ? 'Mute Audio Chimes' : 'Enable Audio Chimes'}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 12px',
              backgroundColor: soundEnabled ? 'rgba(6, 182, 212, 0.15)' : 'var(--bg-surface-elevated)',
              color: soundEnabled ? 'var(--accent-cyan)' : 'var(--text-muted)',
              border: soundEnabled ? '1px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              fontSize: '0.82rem',
              fontWeight: 600,
            }}
          >
            {soundEnabled ? <Volume2 size={16} /> : <VolumeX size={16} />}
            <span>{soundEnabled ? 'Sound On' : 'Muted'}</span>
          </button>
        </div>
      </div>
    </header>
  );
};
