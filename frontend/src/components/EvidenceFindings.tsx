import React from 'react';
import {
  CheckCircle,
  FileText,
  Lightbulb,
  ShieldAlert,
} from 'lucide-react';
import type { EvidenceFinding } from '../types';

interface EvidenceFindingsProps {
  findings: EvidenceFinding[];
}

export const EvidenceFindings: React.FC<EvidenceFindingsProps> = ({ findings }) => {
  if (!findings || findings.length === 0) {
    return (
      <div style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        marginBottom: '28px',
        textAlign: 'center',
      }}>
        <CheckCircle size={32} color="var(--risk-low)" style={{ margin: '0 auto 10px' }} />
        <h4 style={{ fontSize: '1.05rem', fontWeight: 600 }}>No Adverse Evidence Flagged</h4>
        <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
          The conversation contains no predatory indicators or coercive credential demands.
        </p>
      </div>
    );
  }

  const getSeverityStyle = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
        return { text: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', border: '#dc2626' };
      case 'HIGH':
        return { text: '#f97316', bg: 'rgba(249, 115, 22, 0.15)', border: '#ea580c' };
      case 'MEDIUM':
        return { text: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', border: '#d97706' };
      case 'LOW':
      default:
        return { text: '#10b981', bg: 'rgba(16, 185, 129, 0.15)', border: '#059669' };
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
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '18px',
      }}>
        <div>
          <h3 style={{
            fontSize: '1.2rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <FileText size={20} color="var(--accent-cyan)" />
            <span>Deterministic Evidence Ledger ({findings.length} Items Linked)</span>
          </h3>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Every finding links directly to an exact quote and turn number in the transcript. No hallucinations or ungrounded claims.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '16px' }}>
        {findings.map((finding, idx) => {
          const sev = getSeverityStyle(finding.severity);

          return (
            <div
              key={idx}
              style={{
                backgroundColor: 'var(--bg-primary)',
                border: `1px solid var(--border-subtle)`,
                borderRadius: 'var(--radius-md)',
                padding: '18px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
              }}
            >
              <div>
                {/* Category & Severity Tag */}
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  gap: '8px',
                  marginBottom: '12px',
                }}>
                  <span style={{
                    fontSize: '0.74rem',
                    fontWeight: 800,
                    letterSpacing: '0.04em',
                    textTransform: 'uppercase',
                    color: 'var(--accent-cyan)',
                    backgroundColor: 'rgba(6, 182, 212, 0.1)',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    border: '1px solid rgba(6, 182, 212, 0.25)',
                  }}>
                    {finding.behavior_category.replace('_', ' ')}
                  </span>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span style={{
                      fontSize: '0.72rem',
                      fontWeight: 700,
                      padding: '2px 6px',
                      borderRadius: '3px',
                      backgroundColor: sev.bg,
                      color: sev.text,
                      border: `1px solid ${sev.border}`,
                    }}>
                      {finding.severity}
                    </span>
                    <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                      Turn {finding.turn_number}
                    </span>
                  </div>
                </div>

                {/* Exact Supporting Text Quote */}
                <div style={{
                  backgroundColor: 'var(--bg-surface-elevated)',
                  borderLeft: `3px solid ${sev.text}`,
                  padding: '10px 14px',
                  borderRadius: '0 var(--radius-sm) var(--radius-sm) 0',
                  marginBottom: '14px',
                }}>
                  <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 600, marginBottom: '2px' }}>
                    Exact Transcript Evidence Quote
                  </div>
                  <div style={{ fontSize: '0.92rem', fontWeight: 600, color: 'var(--text-primary)', fontStyle: 'italic' }}>
                    "{finding.exact_quote}"
                  </div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '4px' }}>
                    Spoken by: {finding.speaker}
                  </div>
                </div>

                {/* Explanation */}
                <div style={{ marginBottom: '10px' }}>
                  <div style={{ fontSize: '0.76rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700, marginBottom: '2px' }}>
                    Behavioral Explanation
                  </div>
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                    {finding.explanation}
                  </p>
                </div>

                {/* Why it Matters */}
                <div style={{
                  marginBottom: '14px',
                  backgroundColor: 'rgba(15, 23, 42, 0.6)',
                  padding: '8px 12px',
                  borderRadius: 'var(--radius-sm)',
                  border: '1px solid var(--border-subtle)',
                }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontSize: '0.74rem', color: 'var(--accent-teal)', fontWeight: 700, marginBottom: '2px' }}>
                    <Lightbulb size={13} /> Why This Matters for Elderly Users
                  </div>
                  <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.4 }}>
                    {finding.why_it_matters}
                  </p>
                </div>
              </div>

              {/* Protective Action */}
              <div style={{
                paddingTop: '10px',
                borderTop: '1px solid var(--border-subtle)',
                display: 'flex',
                alignItems: 'flex-start',
                gap: '8px',
              }}>
                <ShieldAlert size={16} color={sev.text} style={{ flexShrink: 0, marginTop: '2px' }} />
                <span style={{ fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                  Action: {finding.recommended_action}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
