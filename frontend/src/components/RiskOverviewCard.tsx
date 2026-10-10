import React from 'react';
import {
  ShieldCheck,
  AlertOctagon,
  AlertTriangle,
  HelpCircle,
  Zap,
  Lock,
  EyeOff,
  KeyRound,
  Coins,
  Smartphone,
  CheckCircle2,
  Globe,
  Clock,
  ShieldBan,
} from 'lucide-react';
import type { RiskAssessment, RiskLevel } from '../types';

interface RiskOverviewCardProps {
  result: RiskAssessment;
}

export const RiskOverviewCard: React.FC<RiskOverviewCardProps> = ({ result }) => {
  const getRiskConfig = (risk: RiskLevel) => {
    switch (risk) {
      case 'HIGH_RISK':
        return {
          title: 'High Risk — Hostile Fraud Tactics Detected',
          badgeClass: 'badge-danger',
          scoreColor: 'var(--risk-high)',
          icon: <AlertOctagon size={28} color="var(--risk-high)" strokeWidth={2.2} />,
          actionAlert: 'DO NOT SHARE ANY DETAILS • HANG UP IMMEDIATELY',
          decisionLabel: 'Decision: BLOCK / TERMINATE',
        };
      case 'SUSPICIOUS':
        return {
          title: 'Suspicious — Elevated Precaution Advised',
          badgeClass: 'badge-warning',
          scoreColor: 'var(--risk-warning)',
          icon: <AlertTriangle size={28} color="var(--risk-warning)" strokeWidth={2.2} />,
          actionAlert: 'PAUSE BEFORE PROCEEDING • VERIFY CALLER INDEPENDENTLY',
          decisionLabel: 'Decision: WARN & PROCEED WITH CAUTION',
        };
      case 'LOW_RISK':
        return {
          title: 'Low Risk — Standard Protocol Observed',
          badgeClass: 'badge-safe',
          scoreColor: 'var(--risk-safe)',
          icon: <ShieldCheck size={28} color="var(--risk-safe)" strokeWidth={2.2} />,
          actionAlert: 'NO COERCIVE FRAUD BEHAVIOR OBSERVED',
          decisionLabel: 'Decision: ALLOW / ROUTINE',
        };
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return {
          title: 'Inconclusive — Insufficient Evidence',
          badgeClass: 'badge-neutral',
          scoreColor: 'var(--text-muted)',
          icon: <HelpCircle size={28} color="var(--text-muted)" strokeWidth={2.2} />,
          actionAlert: 'CONTEXT TOO BRIEF TO CONFIRM INTENT • REMAIN VIGILANT',
          decisionLabel: 'Decision: INCONCLUSIVE',
        };
    }
  };

  const config = getRiskConfig(result.risk_level);
  const signals = result.signals_summary;

  return (
    <div className="es-card" style={{ marginBottom: '24px' }}>
      {/* Top Banner Row */}
      <div
        style={{
          display: 'flex',
          alignItems: 'flex-start',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '16px',
          borderBottom: '1px solid var(--divider-subtle)',
          paddingBottom: '20px',
        }}
      >
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '14px', maxWidth: '680px' }}>
          <div style={{ marginTop: '2px', flexShrink: 0 }}>{config.icon}</div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <span className={config.badgeClass}>
                {result.risk_level.replace('_', ' ')}
              </span>

              <span
                style={{
                  fontSize: '0.78rem',
                  fontWeight: 700,
                  backgroundColor: 'var(--bg-secondary)',
                  color: 'var(--text-primary)',
                  padding: '3px 8px',
                  borderRadius: 'var(--radius-xs)',
                  border: '1px solid var(--border-subtle)',
                }}
              >
                {config.decisionLabel}
              </span>
            </div>

            <h2
              style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '1.35rem',
                fontWeight: 800,
                color: 'var(--text-primary)',
                marginTop: '6px',
                letterSpacing: '-0.01em',
              }}
            >
              {config.title}
            </h2>

            <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
              Evaluation #{result.id} • Method: <strong>{result.analysis_method}</strong> • Detected Language: {result.language_detected}
            </p>
          </div>
        </div>

        {/* Score & Method Box */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '18px',
            backgroundColor: 'var(--bg-secondary)',
            padding: '12px 18px',
            borderRadius: 'var(--radius-sm)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
              Calibrated Score
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
              <span
                style={{
                  fontFamily: 'var(--font-heading)',
                  fontSize: '2rem',
                  fontWeight: 900,
                  color: config.scoreColor,
                }}
              >
                {result.risk_score.toFixed(0)}
              </span>
              <span style={{ fontSize: '0.9rem', color: 'var(--text-muted)', fontWeight: 600 }}>/100</span>
            </div>
          </div>

          <div style={{ borderLeft: '1px solid var(--border-subtle)', paddingLeft: '16px' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, letterSpacing: '0.04em' }}>
              Confidence
            </div>
            <div style={{ fontSize: '0.92rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              {result.confidence_level}
            </div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>
              Deterministic
            </div>
          </div>
        </div>
      </div>

      {/* Senior Action Alert Banner */}
      <div
        style={{
          marginTop: '18px',
          padding: '12px 16px',
          backgroundColor:
            result.risk_level === 'HIGH_RISK'
              ? 'var(--risk-high-bg)'
              : result.risk_level === 'SUSPICIOUS'
              ? 'var(--risk-warning-bg)'
              : 'var(--bg-secondary)',
          border: `1px solid ${
            result.risk_level === 'HIGH_RISK'
              ? 'var(--risk-high-border)'
              : result.risk_level === 'SUSPICIOUS'
              ? 'var(--risk-warning-border)'
              : 'var(--border-subtle)'
          }`,
          borderRadius: 'var(--radius-sm)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '10px',
        }}
      >
        <div
          style={{
            fontSize: '0.9rem',
            fontWeight: 800,
            color:
              result.risk_level === 'HIGH_RISK'
                ? 'var(--risk-high)'
                : result.risk_level === 'SUSPICIOUS'
                ? 'var(--risk-warning)'
                : 'var(--text-primary)',
          }}
        >
          {config.actionAlert}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Globe size={13} /> {result.language_detected}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={13} /> {result.timestamp}
          </span>
        </div>
      </div>

      {/* Rationale & Documented Semantics */}
      <div
        style={{
          marginTop: '16px',
          padding: '14px 16px',
          backgroundColor: 'var(--bg-primary)',
          borderRadius: 'var(--radius-sm)',
          border: '1px solid var(--border-subtle)',
        }}
      >
        <div
          style={{
            fontSize: '0.75rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            color: 'var(--brand-primary)',
            letterSpacing: '0.04em',
            marginBottom: '4px',
          }}
        >
          Deterministic Evaluation Rationale
        </div>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          {result.score_semantics}
        </p>

        {result.reasons && result.reasons.length > 0 && (
          <div style={{ marginTop: '10px', paddingTop: '10px', borderTop: '1px solid var(--divider-subtle)' }}>
            <ul style={{ paddingLeft: '18px', fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
              {result.reasons.map((reason, idx) => (
                <li key={idx}>{reason}</li>
              ))}
            </ul>
          </div>
        )}
      </div>

      {/* Multi-Vector Behavioral Signals Matrix */}
      <div style={{ marginTop: '20px' }}>
        <div
          style={{
            fontSize: '0.76rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            color: 'var(--text-muted)',
            letterSpacing: '0.04em',
            marginBottom: '10px',
          }}
        >
          Multi-Vector Scam Behavioral Matrix
        </div>

        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '10px',
          }}
        >
          {/* Impersonation */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '9px 12px',
              backgroundColor: signals.impersonation ? 'var(--risk-high-bg)' : 'var(--bg-secondary)',
              border: `1px solid ${signals.impersonation ? 'var(--risk-high-border)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              color: signals.impersonation ? 'var(--risk-high)' : 'var(--text-muted)',
              fontSize: '0.84rem',
              fontWeight: signals.impersonation ? 700 : 500,
            }}
          >
            <Lock size={15} />
            <span>Authority Impersonation</span>
          </div>

          {/* Urgency */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '9px 12px',
              backgroundColor: signals.urgency_and_threats ? 'var(--risk-warning-bg)' : 'var(--bg-secondary)',
              border: `1px solid ${signals.urgency_and_threats ? 'var(--risk-warning-border)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              color: signals.urgency_and_threats ? 'var(--risk-warning)' : 'var(--text-muted)',
              fontSize: '0.84rem',
              fontWeight: signals.urgency_and_threats ? 700 : 500,
            }}
          >
            <Zap size={15} />
            <span>Urgency & Intimidation</span>
          </div>

          {/* Secrecy */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '9px 12px',
              backgroundColor: signals.requests_for_secrecy ? 'var(--risk-high-bg)' : 'var(--bg-secondary)',
              border: `1px solid ${signals.requests_for_secrecy ? 'var(--risk-high-border)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              color: signals.requests_for_secrecy ? 'var(--risk-high)' : 'var(--text-muted)',
              fontSize: '0.84rem',
              fontWeight: signals.requests_for_secrecy ? 700 : 500,
            }}
          >
            <EyeOff size={15} />
            <span>Secrecy & Isolation</span>
          </div>

          {/* Credentials */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '9px 12px',
              backgroundColor: signals.credential_requests ? 'var(--risk-high-bg)' : 'var(--bg-secondary)',
              border: `1px solid ${signals.credential_requests ? 'var(--risk-high-border)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              color: signals.credential_requests ? 'var(--risk-high)' : 'var(--text-muted)',
              fontSize: '0.84rem',
              fontWeight: signals.credential_requests ? 700 : 500,
            }}
          >
            <KeyRound size={15} />
            <span>OTP / PIN Solicitation</span>
          </div>

          {/* Remote Access */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '9px 12px',
              backgroundColor: signals.remote_access_requests ? 'var(--risk-high-bg)' : 'var(--bg-secondary)',
              border: `1px solid ${signals.remote_access_requests ? 'var(--risk-high-border)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              color: signals.remote_access_requests ? 'var(--risk-high)' : 'var(--text-muted)',
              fontSize: '0.84rem',
              fontWeight: signals.remote_access_requests ? 700 : 500,
            }}
          >
            <Smartphone size={15} />
            <span>Remote App / AnyDesk</span>
          </div>

          {/* Financial Demands */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '9px 12px',
              backgroundColor: signals.financial_transfer_requests ? 'var(--risk-high-bg)' : 'var(--bg-secondary)',
              border: `1px solid ${signals.financial_transfer_requests ? 'var(--risk-high-border)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              color: signals.financial_transfer_requests ? 'var(--risk-high)' : 'var(--text-muted)',
              fontSize: '0.84rem',
              fontWeight: signals.financial_transfer_requests ? 700 : 500,
            }}
          >
            <Coins size={15} />
            <span>Money Transfer / Escrow</span>
          </div>

          {/* Verification Bypass */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '9px 12px',
              backgroundColor: signals.verification_bypass_attempts ? 'var(--risk-warning-bg)' : 'var(--bg-secondary)',
              border: `1px solid ${signals.verification_bypass_attempts ? 'var(--risk-warning-border)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              color: signals.verification_bypass_attempts ? 'var(--risk-warning)' : 'var(--text-muted)',
              fontSize: '0.84rem',
              fontWeight: signals.verification_bypass_attempts ? 700 : 500,
            }}
          >
            <ShieldBan size={15} />
            <span>Verification Bypass</span>
          </div>

          {/* Legitimate Safeguards */}
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '9px',
              padding: '9px 12px',
              backgroundColor: signals.legitimate_safeguards_present ? 'var(--bg-soft-sage)' : 'var(--bg-secondary)',
              border: `1px solid ${signals.legitimate_safeguards_present ? 'var(--brand-subtle)' : 'var(--border-subtle)'}`,
              borderRadius: 'var(--radius-sm)',
              color: signals.legitimate_safeguards_present ? 'var(--brand-primary)' : 'var(--text-muted)',
              fontSize: '0.84rem',
              fontWeight: signals.legitimate_safeguards_present ? 700 : 500,
            }}
          >
            <CheckCircle2 size={15} />
            <span>Branch Safeguard Found</span>
          </div>
        </div>
      </div>
    </div>
  );
};
