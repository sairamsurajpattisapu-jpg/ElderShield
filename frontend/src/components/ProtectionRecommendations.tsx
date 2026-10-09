import React, { useState } from 'react';
import {
  ShieldAlert,
  PhoneCall,
  Printer,
  Copy,
  Check,
  ExternalLink,
} from 'lucide-react';
import type { AnalysisResult } from '../types';

interface ProtectionRecommendationsProps {
  result: AnalysisResult;
}

export const ProtectionRecommendations: React.FC<ProtectionRecommendationsProps> = ({ result }) => {
  const [copied, setCopied] = useState(false);

  const handleCopyReport = () => {
    const reportText = `=== ELDERSHIELD SCAM INCIDENT REPORT ===
Scan ID: ${result.id}
Date & Time: ${result.timestamp}
Overall Risk Level: ${result.overall_risk_level} (Score: ${result.overall_risk_score}/100)
Language Detected: ${result.language_detected}
Primary Threat Vector: ${result.primary_threat_vector || 'None identified'}

RATIONALE:
${result.summary}

KEY PROTECTIVE ACTIONS FOR SENIOR:
${result.protection_recommendations.map((r, i) => `${i + 1}. ${r}`).join('\n')}

FLAGGED EVIDENCE QUOTES:
${result.evidence_findings.map((f) => `- Turn ${f.turn_number} (${f.behavior_category}): "${f.exact_quote}" -> ${f.explanation}`).join('\n')}

NATIONAL CYBERCRIME HELPLINE: 1930
Emergency Cyber Reporting Portal: https://cybercrime.gov.in
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
            <span>Senior Protection Protocol & Incident Action Plan</span>
          </h3>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Direct, practical guidance tailored for elderly citizens and their family members.
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

      {/* List of Practical Advice Cards */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
        {result.protection_recommendations.map((rec, index) => (
          <div
            key={index}
            style={{
              backgroundColor: 'var(--bg-primary)',
              border: '1px solid var(--border-subtle)',
              borderRadius: 'var(--radius-md)',
              padding: '14px 18px',
              display: 'flex',
              alignItems: 'center',
              gap: '14px',
            }}
          >
            <div style={{
              width: '28px',
              height: '28px',
              borderRadius: '50%',
              backgroundColor: 'rgba(6, 182, 212, 0.15)',
              color: 'var(--accent-cyan)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              fontWeight: 800,
              fontSize: '0.85rem',
              flexShrink: 0,
            }}>
              {index + 1}
            </div>
            <div style={{ fontSize: '0.94rem', fontWeight: 600, color: 'var(--text-primary)', lineHeight: 1.45 }}>
              {rec}
            </div>
          </div>
        ))}
      </div>

      {/* Emergency Cyber helpline and Family escalation card */}
      <div style={{
        marginTop: '20px',
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
              National Cybercrime Helpline: Dial 1930
            </div>
            <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
              Citizen Financial Cyber Fraud Reporting System (Govt of India). Call within the golden hour to freeze fraudulent bank transfers immediately.
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
