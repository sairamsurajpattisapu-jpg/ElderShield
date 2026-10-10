import React from 'react';
import {
  FileText,
  CheckCircle2,
  Quote,
} from 'lucide-react';
import type { EvidenceItem } from '../types';

interface EvidenceFindingsProps {
  evidence: EvidenceItem[];
}

export const EvidenceFindings: React.FC<EvidenceFindingsProps> = ({ evidence }) => {
  if (!evidence || evidence.length === 0) {
    return (
      <div className="es-card" style={{ marginBottom: '24px', textAlign: 'center', padding: '32px 20px' }}>
        <CheckCircle2 size={32} color="var(--brand-primary)" style={{ margin: '0 auto 10px' }} />
        <h4 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
          No Malicious Behavioral Evidence Flagged
        </h4>
        <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px', maxWidth: '440px', margin: '4px auto 0' }}>
          The analyzed conversation did not contain coercive authority pressure, fake arrest threats, or illicit credential extraction demands.
        </p>
      </div>
    );
  }

  const getSeverityBadgeClass = (sev: string) => {
    switch (sev) {
      case 'CRITICAL':
      case 'HIGH':
        return 'badge-danger';
      case 'MEDIUM':
        return 'badge-warning';
      case 'LOW':
      default:
        return 'badge-safe';
    }
  };

  return (
    <div className="es-card" style={{ marginBottom: '24px' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '12px',
          marginBottom: '18px',
          paddingBottom: '14px',
          borderBottom: '1px solid var(--divider-subtle)',
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
            <FileText size={18} color="var(--brand-primary)" />
            <span>Forensic Evidence Ledger ({evidence.length} Indicators Flagged)</span>
          </h3>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Every finding is anchored strictly to an exact verbatim phrase in the conversation with turn attribution.
          </p>
        </div>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: '14px' }}>
        {evidence.map((item, idx) => {
          const badgeClass = getSeverityBadgeClass(item.severity);

          return (
            <div
              key={idx}
              style={{
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-sm)',
                padding: '16px',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                gap: '12px',
              }}
            >
              <div>
                {/* Header: Category & Severity */}
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: '10px' }}>
                  <span
                    style={{
                      fontSize: '0.74rem',
                      fontWeight: 700,
                      textTransform: 'uppercase',
                      letterSpacing: '0.04em',
                      color: 'var(--brand-primary)',
                    }}
                  >
                    {item.signal_category.replace(/_/g, ' ')}
                  </span>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span
                      style={{
                        fontSize: '0.72rem',
                        fontWeight: 600,
                        padding: '1px 6px',
                        borderRadius: 'var(--radius-xs)',
                        backgroundColor: 'var(--bg-secondary)',
                        color: 'var(--text-secondary)',
                      }}
                    >
                      Turn {item.turn_number}
                    </span>
                    <span className={badgeClass}>{item.severity}</span>
                  </div>
                </div>

                {/* Verbatim Quote */}
                <div
                  style={{
                    padding: '10px 12px',
                    borderRadius: 'var(--radius-xs)',
                    backgroundColor: 'var(--bg-surface)',
                    border: '1px solid var(--border-subtle)',
                    marginBottom: '10px',
                    borderLeft: '3px solid var(--brand-primary)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '6px' }}>
                    <Quote size={13} color="var(--brand-primary)" style={{ flexShrink: 0, marginTop: '2px' }} />
                    <span style={{ fontSize: '0.9rem', color: 'var(--text-primary)', fontStyle: 'italic', lineHeight: 1.45 }}>
                      "{item.exact_quote}"
                    </span>
                  </div>
                </div>

                {/* Plain-Language Explanation */}
                <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                  {item.explanation}
                </p>
              </div>

              {/* Behavioral Contribution Footer */}
              {item.contribution && (
                <div
                  style={{
                    paddingTop: '8px',
                    borderTop: '1px solid var(--divider-subtle)',
                    fontSize: '0.76rem',
                    color: 'var(--text-muted)',
                  }}
                >
                  Evaluation contribution: <strong>{item.contribution}</strong>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
};
