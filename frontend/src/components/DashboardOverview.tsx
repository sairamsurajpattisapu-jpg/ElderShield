import React from 'react';
import { ShieldCheck, Activity, AlertTriangle, AlertOctagon, ArrowRight, Layers } from 'lucide-react';
import type { AnalysisResult } from '../types';

interface DashboardOverviewProps {
  recentAnalyses: AnalysisResult[];
  onStartNewAnalysis: () => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  recentAnalyses,
  onStartNewAnalysis,
}) => {
  const totalScans = recentAnalyses.length;
  const highRiskCount = recentAnalyses.filter(a => a.overall_risk_level === 'HIGH RISK').length;
  const suspiciousCount = recentAnalyses.filter(a => a.overall_risk_level === 'SUSPICIOUS').length;
  const lowRiskCount = recentAnalyses.filter(a => a.overall_risk_level === 'LOW RISK').length;
  const uncertainCount = recentAnalyses.filter(a => a.overall_risk_level === 'INSUFFICIENT EVIDENCE').length;

  return (
    <section style={{
      marginBottom: '32px',
    }}>
      {/* Protection Status Banner */}
      <div style={{
        backgroundColor: 'var(--bg-surface)',
        border: '1px solid var(--border-subtle)',
        borderRadius: 'var(--radius-lg)',
        padding: '24px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '20px',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', gap: '18px', maxWidth: '780px' }}>
          <div style={{
            width: '52px',
            height: '52px',
            borderRadius: '14px',
            backgroundColor: 'rgba(16, 185, 129, 0.12)',
            border: '1.5px solid var(--risk-low-border)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'var(--risk-low)',
            flexShrink: 0,
          }}>
            <ShieldCheck size={30} />
          </div>
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
              <h2 style={{ fontSize: '1.25rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                ElderShield Protection Core: ACTIVE
              </h2>
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '6px',
                fontSize: '0.75rem',
                fontWeight: 600,
                color: 'var(--risk-low)',
                backgroundColor: 'rgba(16, 185, 129, 0.15)',
                padding: '3px 8px',
                borderRadius: '999px',
              }}>
                <span style={{
                  width: '6px',
                  height: '6px',
                  borderRadius: '50%',
                  backgroundColor: 'var(--risk-low)',
                  boxShadow: '0 0 8px var(--risk-low)',
                }} />
                Real-Time Guard
              </span>
            </div>
            <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', marginTop: '6px' }}>
              Specialized cybersecurity barrier for seniors in India. Evaluates conversational intent across English, Hindi, Telugu, and mixed dialect scripts to detect coercive payment demands, fake police arrest threats, and remote app takeovers.
            </p>
          </div>
        </div>

        <button
          onClick={onStartNewAnalysis}
          style={{
            backgroundColor: 'var(--accent-cyan)',
            color: '#080c16',
            border: 'none',
            borderRadius: 'var(--radius-md)',
            padding: '12px 22px',
            fontWeight: 700,
            fontSize: '0.96rem',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
            transition: 'background-color 0.15s ease',
            boxShadow: '0 4px 14px rgba(6, 182, 212, 0.3)',
          }}
        >
          <span>Analyze Call Transcript</span>
          <ArrowRight size={18} />
        </button>
      </div>

      {/* Activity and Risk Metrics Breakdown */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))',
        gap: '16px',
        marginTop: '16px',
      }}>
        {/* Metric 1 */}
        <div style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Conversations Evaluated
            </span>
            <Activity size={18} color="var(--accent-cyan)" />
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, marginTop: '8px', color: 'var(--text-primary)' }}>
            {totalScans}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            Multi-lingual transcripts processed
          </div>
        </div>

        {/* Metric 2: High Risk */}
        <div style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--risk-high-border)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
          background: 'var(--risk-high-bg)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#fca5a5' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              High Risk / Malicious
            </span>
            <AlertOctagon size={18} color="#ef4444" />
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, marginTop: '8px', color: '#fca5a5' }}>
            {highRiskCount}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#f87171', marginTop: '4px' }}>
            Critical predatory threats identified
          </div>
        </div>

        {/* Metric 3: Suspicious */}
        <div style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--risk-suspicious-border)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
          background: 'var(--risk-suspicious-bg)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: '#fcd34d' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Suspicious Cues
            </span>
            <AlertTriangle size={18} color="#f59e0b" />
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, marginTop: '8px', color: '#fcd34d' }}>
            {suspiciousCount}
          </div>
          <div style={{ fontSize: '0.8rem', color: '#fbbf24', marginTop: '4px' }}>
            Unverified pressure or authority claims
          </div>
        </div>

        {/* Metric 4: Safe / Insufficient */}
        <div style={{
          backgroundColor: 'var(--bg-surface)',
          border: '1px solid var(--border-subtle)',
          borderRadius: 'var(--radius-md)',
          padding: '16px 20px',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', color: 'var(--text-secondary)' }}>
            <span style={{ fontSize: '0.82rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Safe / Inconclusive
            </span>
            <Layers size={18} color="var(--accent-teal)" />
          </div>
          <div style={{ fontSize: '1.9rem', fontWeight: 800, marginTop: '8px', color: 'var(--text-primary)' }}>
            {lowRiskCount + uncertainCount}
          </div>
          <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '4px' }}>
            {lowRiskCount} Verified Safe • {uncertainCount} Insufficient Evidence
          </div>
        </div>
      </div>
    </section>
  );
};
