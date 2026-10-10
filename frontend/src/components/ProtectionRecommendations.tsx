import React, { useState } from 'react';
import {
  ShieldAlert,
  Printer,
  Copy,
  Check,
} from 'lucide-react';
import type { RiskAssessment } from '../types';

interface ProtectionRecommendationsProps {
  result: RiskAssessment;
}

export const ProtectionRecommendations: React.FC<ProtectionRecommendationsProps> = ({ result }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyReport = () => {
    const reportText = `=== ELDERSHIELD SCAM INCIDENT REPORT ===
Evaluation ID: ${result.id}
Timestamp: ${result.timestamp}
Classification: ${result.risk_level} (Score: ${result.risk_score}/100)
Decision: ${result.decision}
Language Detected: ${result.language_detected}
Method: ${result.analysis_method}

RECOMMENDED ACTION FOR SENIOR:
${result.recommended_action}

DETERMINISTIC REASONS:
${result.reasons.map((r, i) => `${i + 1}. ${r}`).join('\n')}

FLAGGED EVIDENCE ITEMS:
${result.evidence.map((f) => `- Turn ${f.turn_number} (${f.signal_category}): "${f.exact_quote}" -> ${f.explanation}`).join('\n')}

NATIONAL CYBERCRIME HELPLINE: Dial 1930
Portal: https://cybercrime.gov.in
========================================`;

    navigator.clipboard.writeText(reportText).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2500);
    });
  };

  const handlePrint = () => {
    window.print();
  };

  const isHighOrSuspicious = result.risk_level === 'HIGH_RISK' || result.risk_level === 'SUSPICIOUS';

  return (
    <div className="es-card" style={{ marginBottom: '24px' }}>
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '14px',
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
            <ShieldAlert size={18} color="var(--brand-primary)" />
            <span>Senior Protection Protocol & Incident Actions</span>
          </h3>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Actionable safety steps designed to protect elderly citizens from coercion and financial extraction.
          </p>
        </div>

        {/* Action buttons */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={handleCopyReport}
            className="btn-secondary"
            style={{ fontSize: '0.82rem', padding: '7px 12px' }}
          >
            {copied ? <Check size={14} color="var(--brand-primary)" /> : <Copy size={14} />}
            <span>{copied ? 'Copied' : 'Copy Audit Report'}</span>
          </button>

          <button
            onClick={handlePrint}
            className="btn-secondary"
            style={{ fontSize: '0.82rem', padding: '7px 12px' }}
          >
            <Printer size={14} />
            <span>Print Report</span>
          </button>
        </div>
      </div>

      {/* Primary Recommended Action Card */}
      <div
        style={{
          padding: '16px 18px',
          borderRadius: 'var(--radius-sm)',
          backgroundColor: isHighOrSuspicious ? 'var(--risk-high-bg)' : 'var(--bg-soft-sage)',
          border: `1px solid ${isHighOrSuspicious ? 'var(--risk-high-border)' : 'var(--brand-subtle)'}`,
          marginBottom: '20px',
        }}
      >
        <div
          style={{
            fontSize: '0.76rem',
            fontWeight: 700,
            textTransform: 'uppercase',
            letterSpacing: '0.04em',
            color: isHighOrSuspicious ? 'var(--risk-high)' : 'var(--brand-primary)',
            marginBottom: '4px',
          }}
        >
          Senior Action Recommendation
        </div>
        <p
          style={{
            fontSize: '0.94rem',
            fontWeight: 600,
            color: 'var(--text-primary)',
            lineHeight: 1.5,
          }}
        >
          {result.recommended_action}
        </p>
      </div>

      {/* 3 Step Protocol Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: '14px' }}>
        {/* Step 1 */}
        <div
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: 'var(--brand-primary)',
                color: '#FFFFFF',
                fontSize: '0.78rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              1
            </span>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Terminate Call
            </span>
          </div>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Do not engage in arguments or attempt to reason with callers who threaten arrest or demand OTPs. Hang up immediately.
          </p>
        </div>

        {/* Step 2 */}
        <div
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: 'var(--brand-primary)',
                color: '#FFFFFF',
                fontSize: '0.78rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              2
            </span>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Consult Family or Bank
            </span>
          </div>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            Inform a trusted family member, neighbor, or visit your local branch in person. Never install remote screen-sharing apps like AnyDesk.
          </p>
        </div>

        {/* Step 3 */}
        <div
          style={{
            padding: '16px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--border-subtle)',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '8px' }}>
            <span
              style={{
                width: '24px',
                height: '24px',
                borderRadius: '50%',
                backgroundColor: 'var(--brand-primary)',
                color: '#FFFFFF',
                fontSize: '0.78rem',
                fontWeight: 700,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              3
            </span>
            <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text-primary)' }}>
              Call 1930 Helpline
            </span>
          </div>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
            If any financial transaction was made, dial the National Cybercrime Helpline <strong>1930</strong> within 2 hours to freeze fraudulent fund transfers.
          </p>
        </div>
      </div>
    </div>
  );
};
