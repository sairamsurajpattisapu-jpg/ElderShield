import React, { useState } from 'react';
import {
  ShieldAlert,
  PhoneCall,
  Printer,
  Copy,
  Check,
  ExternalLink,
} from 'lucide-react';
import type { RiskAssessment } from '../types';

interface ProtectionRecommendationsProps {
  result: RiskAssessment;
}

export const ProtectionRecommendations: React.FC<ProtectionRecommendationsProps> = ({ result }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyReport = () => {
    const reportText = `=== ELDERSHIELD SCAM INCIDENT REPORT ===
Scan ID: ${result.id}
Timestamp: ${result.timestamp}
Classification: ${result.risk_level} (Score: ${result.risk_score}/100)
Decision: ${result.decision}
Language Detected: ${result.language_detected}
Method: ${result.analysis_method}

SCORE SEMANTICS:
${result.score_semantics}

RECOMMENDED ACTION FOR SENIOR:
${result.recommended_action}

DETERMINISTIC REASONS:
${result.reasons.map((r, i) => `${i + 1}. ${r}`).join('\n')}

FLAGGED EVIDENCE ITEMS:
${result.evidence.map((f) => `- Turn ${f.turn_number} (${f.signal_category}): "${f.exact_quote}" -> ${f.explanation}`).join('\n')}

NATIONAL CYBERCRIME HELPLINE: Dial 1930
Reporting Portal: https://cybercrime.gov.in
========================================`;

    navigator.clipboard.writeText(reportText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 3000);
    });
  };

  const handlePrint = () => {
    window.print();
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
        gap: '14px',
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
            <ShieldAlert size={20} color="var(--accent-cyan)" />
            <span>Recommended Actions & Protection Plan</span>
          </h3>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Actionable instructions designed to protect elderly citizens from unauthorized debit and emotional manipulation.
          </p>
        </div>

        {/* Action buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleCopyReport}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              backgroundColor: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              fontWeight: 600,
            }}
          >
            {copied ? <Check size={14} color="#10b981" /> : <Copy size={14} />}
            <span>{copied ? 'Copied to Clipboard' : 'Copy Incident Report'}</span>
          </button>

          <button
            onClick={handlePrint}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              padding: '8px 14px',
              backgroundColor: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              fontSize: '0.82rem',
              fontWeight: 600,
            }}
          >
            <Printer size={14} />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Main Recommended Action Callout */}
      <div style={{
        backgroundColor: 'var(--bg-primary)',
        border: '1.5px solid var(--border-prominent)',
        borderRadius: 'var(--radius-md)',
        padding: '18px 22px',
        marginBottom: '18px',
      }}>
        <div style={{ fontSize: '0.78rem', color: 'var(--accent-cyan)', textTransform: 'uppercase', fontWeight: 800, marginBottom: '6px' }}>
          Primary Protection Directive
        </div>
        <p style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-primary)', lineHeight: 1.5 }}>
          {result.recommended_action}
        </p>
      </div>

      {/* Specific Deterministic Reasons */}
      <div style={{ marginBottom: '20px' }}>
        <div style={{ fontSize: '0.84rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '8px' }}>
          Rationale Summary ({result.reasons.length} Points)
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
          {result.reasons.map((rec, index) => (
            <div
              key={index}
              style={{
                backgroundColor: 'var(--bg-primary)',
                border: '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '12px 16px',
                display: 'flex',
                alignItems: 'center',
                gap: '12px',
              }}
            >
              <div style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: 'rgba(6, 182, 212, 0.15)',
                color: 'var(--accent-cyan)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontWeight: 800,
                fontSize: '0.8rem',
                flexShrink: 0,
              }}>
                {index + 1}
              </div>
              <div style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.4 }}>
                {rec}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Emergency Cyber helpline and Family escalation card */}
      <div style={{
        padding: '18px 22px',
        backgroundColor: 'rgba(239, 68, 68, 0.08)',
        border: '1.5px solid var(--risk-high-border)',
        borderRadius: 'var(--radius-md)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '16px',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '44px',
            height: '44px',
            borderRadius: '10px',
            backgroundColor: '#ef4444',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#ffffff',
            flexShrink: 0,
          }}>
            <PhoneCall size={22} />
          </div>
          <div>
            <div style={{ fontSize: '1rem', fontWeight: 800, color: '#fca5a5' }}>
              National Cybercrime Reporting Helpline: 1930
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Toll-free emergency financial fraud helpline. Call immediately within the golden hour to freeze fraudulent bank transfers.
            </p>
          </div>
        </div>

        <a
          href="https://cybercrime.gov.in"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '6px',
            padding: '10px 18px',
            backgroundColor: '#dc2626',
            color: '#ffffff',
            textDecoration: 'none',
            borderRadius: 'var(--radius-sm)',
            fontWeight: 700,
            fontSize: '0.88rem',
          }}
        >
          <span>cybercrime.gov.in</span>
          <ExternalLink size={14} />
        </a>
      </div>
    </div>
  );
};
