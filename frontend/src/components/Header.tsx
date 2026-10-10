import React from 'react';
import { Menu, Phone, ShieldCheck, Activity } from 'lucide-react';

export type NavTab =
  | 'dashboard'
  | 'live'
  | 'caller'
  | 'analyze'
  | 'results'
  | 'timeline'
  | 'recent'
  | 'settings';

interface HeaderProps {
  currentTab: NavTab;
  onOpenMobileSidebar: () => void;
  isBackendHealthy: boolean;
  hasActiveResult: boolean;
  onSelectTab: (tab: NavTab) => void;
}

const TAB_META: Record<NavTab, { title: string; description: string }> = {
  dashboard: {
    title: 'Protection Overview',
    description: 'Real-time telemetry, companion status, and multi-vector scam triage.',
  },
  live: {
    title: 'Live Audio Monitor',
    description: 'Acoustic stream processing, behavioral rule extraction, and live OTP protection.',
  },
  caller: {
    title: 'Caller Intelligence & Spoof Defense',
    description: 'ITU E.164 normalization, institutional registry matching, and conflict verification.',
  },
  analyze: {
    title: 'Conversation Analysis',
    description: 'Evaluate speech recordings or transcripts against multi-vector fraud indicators.',
  },
  results: {
    title: 'Evidence Ledger & Assessment',
    description: 'Verifiable multi-turn forensic findings, behavioral quotes, and elder safety guidance.',
  },
  timeline: {
    title: 'Turn-by-Turn Risk Velocity',
    description: 'Incremental velocity tracking calculated across each conversational dialogue exchange.',
  },
  recent: {
    title: 'Evaluation History & Audits',
    description: 'Inspect past session evaluations, risk determinations, and diagnostic reports.',
  },
  settings: {
    title: 'Settings & Privacy Controls',
    description: 'Senior accessibility typography, audible alert parameters, and data governance.',
  },
};

export const Header: React.FC<HeaderProps> = ({
  currentTab,
  onOpenMobileSidebar,
  isBackendHealthy,
}) => {
  const currentMeta = TAB_META[currentTab] || {
    title: 'ElderShield Console',
    description: 'Conversational fraud protection for seniors.',
  };

  return (
    <header
      style={{
        backgroundColor: 'var(--bg-surface)',
        borderBottom: '1px solid var(--border-subtle)',
        padding: '16px 28px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        gap: '16px',
        position: 'sticky',
        top: 0,
        zIndex: 100,
      }}
    >
      {/* Left: Mobile Toggle & Page Title */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', minWidth: 0 }}>
        <button
          onClick={onOpenMobileSidebar}
          className="mobile-hamburger-btn"
          style={{
            background: 'none',
            border: '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            padding: '7px',
            color: 'var(--text-primary)',
            cursor: 'pointer',
            display: 'none',
            alignItems: 'center',
            justifyContent: 'center',
          }}
          aria-label="Open navigation menu"
        >
          <Menu size={20} />
        </button>

        <div style={{ minWidth: 0 }}>
          <h1
            style={{
              fontSize: '1.28rem',
              fontWeight: 700,
              color: 'var(--text-primary)',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {currentMeta.title}
          </h1>
          <p
            style={{
              fontSize: '0.84rem',
              color: 'var(--text-secondary)',
              marginTop: '2px',
              whiteSpace: 'nowrap',
              overflow: 'hidden',
              textOverflow: 'ellipsis',
            }}
          >
            {currentMeta.description}
          </p>
        </div>
      </div>

      {/* Right: Actions & Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', flexShrink: 0 }}>
        {/* Backend Status Chip */}
        <div
          title={isBackendHealthy ? 'ElderShield FastAPI Backend 127.0.0.1:8000 Healthy' : 'Backend Unreachable'}
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '5px 10px',
            borderRadius: 'var(--radius-full)',
            backgroundColor: isBackendHealthy ? 'var(--risk-safe-bg)' : 'var(--risk-high-bg)',
            border: `1px solid ${isBackendHealthy ? 'var(--risk-safe-border)' : 'var(--risk-high-border)'}`,
            color: isBackendHealthy ? 'var(--risk-safe)' : 'var(--risk-high)',
            fontSize: '0.78rem',
            fontWeight: 600,
          }}
        >
          {isBackendHealthy ? (
            <ShieldCheck size={14} color="var(--risk-safe)" />
          ) : (
            <Activity size={14} color="var(--risk-high)" />
          )}
          <span>{isBackendHealthy ? 'Engine Ready' : 'Backend Degraded'}</span>
        </div>

        {/* Emergency Helpline Callout */}
        <a
          href="tel:1930"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '7px',
            padding: '6px 12px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-secondary)',
            border: '1px solid var(--border-subtle)',
            color: 'var(--text-primary)',
            fontSize: '0.82rem',
            fontWeight: 600,
          }}
        >
          <Phone size={13} color="var(--risk-high)" />
          <span>Helpline: <strong>1930</strong></span>
        </a>
      </div>
    </header>
  );
};
