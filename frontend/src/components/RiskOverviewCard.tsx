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
} from 'lucide-react';
import type { AnalysisResult, RiskLevel } from '../types';

interface RiskOverviewCardProps {
  result: AnalysisResult;
}

export const RiskOverviewCard: React.FC<RiskOverviewCardProps> = ({ result }) => {
  const getRiskConfig = (risk: RiskLevel) => {
    switch (risk) {
      case 'HIGH RISK':
        return {
          title: 'HIGH RISK — CRITICAL THREAT DETECTED',
          border: 'var(--risk-high-border)',
          bg: 'var(--risk-high-bg)',
          color: 'var(--risk-high)',
          icon: <AlertOctagon size={36} color="#ef4444" />,
          actionAlert: 'DO NOT SHARE ANY DETAILS. HANG UP IMMEDIATELY.',
        };
      case 'SUSPICIOUS':
        return {
          title: 'SUSPICIOUS — ELEVATED PRECAUTION ADVISED',
          border: 'var(--risk-suspicious-border)',
          bg: 'var(--risk-suspicious-bg)',
          color: 'var(--risk-suspicious)',
          icon: <AlertTriangle size={36} color="#f59e0b" />,
          actionAlert: 'PAUSE BEFORE PROCEEDING. INDEPENDENTLY VERIFY THE CALLER.',
        };
      case 'LOW RISK':
        return {
          title: 'LOW RISK — VERIFIED PROTOCOL SAFE',
          border: 'var(--risk-low-border)',
          bg: 'var(--risk-low-bg)',
          color: 'var(--risk-low)',
          icon: <ShieldCheck size={36} color="#10b981" />,
          actionAlert: 'NO MALICIOUS BEHAVIOR DETECTED. LEGITIMATE BANKING PROTOCOL OBSERVED.',
        };
      case 'INSUFFICIENT EVIDENCE':
      default:
        return {
          title: 'INSUFFICIENT EVIDENCE — INCONCLUSIVE INTERACTION',
          border: 'var(--risk-uncertain-border)',
          bg: 'var(--risk-uncertain-bg)',
          color: 'var(--risk-uncertain)',
          icon: <HelpCircle size={36} color="#94a3b8" />,
          actionAlert: 'CONTEXT TOO BRIEF TO CONFIRM INTENT. REMAIN VIGILANT AND DO NOT VOLUNTEER DATA.',
        };
    }
  };

  const config = getRiskConfig(result.overall_risk_level);
  const matrix = result.behavior_matrix;

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: `2px solid ${config.border}`,
      borderRadius: 'var(--radius-lg)',
      padding: '26px',
      marginBottom: '28px',
      position: 'relative',
      background: `linear-gradient(180deg, ${config.bg} 0%, var(--bg-surface) 100%)`,
    }}>
      {/* Top Banner Row */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '20px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div>{config.icon}</div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexWrap: 'wrap' }}>
              <span style={{
                fontSize: '0.78rem',
                fontWeight: 800,
                letterSpacing: '0.06em',
                textTransform: 'uppercase',
                padding: '3px 10px',
                borderRadius: '4px',
                backgroundColor: config.bg,
                border: `1.5px solid ${config.border}`,
                color: config.color,
              }}>
                {result.overall_risk_level}
              </span>

              {result.primary_threat_vector && (
                <span style={{
                  fontSize: '0.76rem',
                  fontWeight: 600,
                  backgroundColor: 'rgba(239, 68, 68, 0.2)',
                  color: '#fca5a5',
                  padding: '2px 8px',
                  borderRadius: '4px',
                  border: '1px solid rgba(239, 68, 68, 0.4)',
                }}>
                  Vector: {result.primary_threat_vector}
                </span>
              )}
            </div>

            <h2 style={{
              fontSize: '1.45rem',
              fontWeight: 800,
              color: 'var(--text-primary)',
              marginTop: '6px',
              letterSpacing: '-0.01em',
            }}>
              {config.title}
            </h2>
          </div>
        </div>

        {/* Score & Confidence Box */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '20px',
          backgroundColor: 'var(--bg-surface-elevated)',
          padding: '12px 20px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
        }}>
          <div>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Calculated Risk Index
            </div>
            <div style={{ display: 'flex', alignItems: 'baseline', gap: '4px' }}>
              <span style={{ fontSize: '2.1rem', fontWeight: 900, color: config.color }}>
                {result.overall_risk_score.toFixed(0)}
              </span>
              <span style={{ fontSize: '1rem', color: 'var(--text-muted)', fontWeight: 600 }}>/100</span>
            </div>
          </div>

          <div style={{ borderLeft: '1px solid var(--border-subtle)', paddingLeft: '16px' }}>
            <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600 }}>
              Analysis Confidence
            </div>
            <div style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginTop: '2px' }}>
              {result.confidence_level}
            </div>
          </div>
        </div>
      </div>

      {/* Senior Action Alert Banner */}
      <div style={{
        marginTop: '18px',
        padding: '14px 18px',
        backgroundColor: config.bg,
        border: `1px solid ${config.border}`,
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '10px',
      }}>
        <div style={{ fontSize: '0.96rem', fontWeight: 800, color: config.color, letterSpacing: '0.01em' }}>
          {config.actionAlert}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '14px', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Globe size={14} color="var(--accent-cyan)" /> {result.language_detected}
          </span>
          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
            <Clock size={14} /> Scan #{result.id} • {result.timestamp}
          </span>
        </div>
      </div>

      {/* Explicit Score Semantics Box */}
      <div style={{
        marginTop: '16px',
        padding: '14px 18px',
        backgroundColor: 'var(--bg-primary)',
        borderRadius: 'var(--radius-md)',
        border: '1px solid var(--border-subtle)',
      }}>
        <div style={{ fontSize: '0.76rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent-cyan)', letterSpacing: '0.05em', marginBottom: '4px' }}>
          Explicit Score Semantics & Rationale
        </div>
        <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
          {result.score_semantics}
        </p>
      </div>

      {/* Behavioral Indicator Matrix */}
      <div style={{ marginTop: '20px' }}>
        <div style={{ fontSize: '0.82rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', letterSpacing: '0.04em', marginBottom: '10px' }}>
          Multi-Vector Scam Behavioral Matrix
        </div>

        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
          gap: '10px',
        }}>
          {/* Impersonation */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '10px 14px',
            backgroundColor: matrix.impersonation ? 'rgba(239, 68, 68, 0.12)' : 'var(--bg-surface-elevated)',
            border: matrix.impersonation ? '1px solid var(--risk-high-border)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: matrix.impersonation ? '#fca5a5' : 'var(--text-muted)',
          }}>
            <Lock size={16} />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Authority Impersonation</span>
          </div>

          {/* Urgency */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '10px 14px',
            backgroundColor: matrix.urgency_intimidation ? 'rgba(245, 158, 11, 0.12)' : 'var(--bg-surface-elevated)',
            border: matrix.urgency_intimidation ? '1px solid var(--risk-suspicious-border)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: matrix.urgency_intimidation ? '#fcd34d' : 'var(--text-muted)',
          }}>
            <Zap size={16} />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Urgency & Intimidation</span>
          </div>

          {/* Secrecy */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '10px 14px',
            backgroundColor: matrix.secrecy_isolation ? 'rgba(239, 68, 68, 0.12)' : 'var(--bg-surface-elevated)',
            border: matrix.secrecy_isolation ? '1px solid var(--risk-high-border)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: matrix.secrecy_isolation ? '#fca5a5' : 'var(--text-muted)',
          }}>
            <EyeOff size={16} />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Secrecy & Isolation</span>
          </div>

          {/* Credentials */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '10px 14px',
            backgroundColor: matrix.credential_solicitation ? 'rgba(239, 68, 68, 0.15)' : 'var(--bg-surface-elevated)',
            border: matrix.credential_solicitation ? '1px solid var(--risk-high-border)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: matrix.credential_solicitation ? '#ef4444' : 'var(--text-muted)',
          }}>
            <KeyRound size={16} />
            <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>OTP / PIN Solicitation</span>
          </div>

          {/* Remote Access */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '10px 14px',
            backgroundColor: matrix.remote_access_malware ? 'rgba(239, 68, 68, 0.15)' : 'var(--bg-surface-elevated)',
            border: matrix.remote_access_malware ? '1px solid var(--risk-high-border)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: matrix.remote_access_malware ? '#ef4444' : 'var(--text-muted)',
          }}>
            <Smartphone size={16} />
            <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>Remote App / AnyDesk</span>
          </div>

          {/* Financial Coercion */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '10px 14px',
            backgroundColor: matrix.financial_coercion ? 'rgba(239, 68, 68, 0.15)' : 'var(--bg-surface-elevated)',
            border: matrix.financial_coercion ? '1px solid var(--risk-high-border)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: matrix.financial_coercion ? '#ef4444' : 'var(--text-muted)',
          }}>
            <Coins size={16} />
            <span style={{ fontSize: '0.85rem', fontWeight: 700 }}>Money Transfer / QR Demands</span>
          </div>

          {/* Legitimate Safeguards */}
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '10px 14px',
            backgroundColor: matrix.legitimate_safeguards_present ? 'rgba(16, 185, 129, 0.12)' : 'var(--bg-surface-elevated)',
            border: matrix.legitimate_safeguards_present ? '1px solid var(--risk-low-border)' : '1px solid var(--border-subtle)',
            borderRadius: 'var(--radius-sm)',
            color: matrix.legitimate_safeguards_present ? 'var(--risk-low)' : 'var(--text-muted)',
          }}>
            <CheckCircle2 size={16} />
            <span style={{ fontSize: '0.85rem', fontWeight: 600 }}>Branch Safety Safeguard</span>
          </div>
        </div>
      </div>
    </div>
  );
};
