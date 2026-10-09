import React from 'react';
import { History, ShieldAlert, ShieldCheck, AlertOctagon, HelpCircle, ChevronRight } from 'lucide-react';
import type { RiskAssessment, RiskLevel } from '../types';

interface RecentAnalysesDrawerProps {
  recentList: RiskAssessment[];
  onSelectAnalysis: (result: RiskAssessment) => void;
  activeId?: string;
  isRetainingHistory: boolean;
}

export const RecentAnalysesDrawer: React.FC<RecentAnalysesDrawerProps> = ({
  recentList,
  onSelectAnalysis,
  activeId,
  isRetainingHistory,
}) => {
  if (!recentList || recentList.length === 0) return null;

  const getRiskBadge = (risk: RiskLevel) => {
    switch (risk) {
      case 'HIGH_RISK':
        return { text: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444', icon: <AlertOctagon size={13} /> };
      case 'SUSPICIOUS':
        return { text: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b', icon: <ShieldAlert size={13} /> };
      case 'LOW_RISK':
        return { text: '#10b981', bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981', icon: <ShieldCheck size={13} /> };
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return { text: '#94a3b8', bg: 'rgba(148, 163, 184, 0.15)', border: '#94a3b8', icon: <HelpCircle size={13} /> };
    }
  };

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: '24px',
      marginBottom: '32px',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        marginBottom: '16px',
        flexWrap: 'wrap',
        gap: '8px',
      }}>
        <div>
          <h3 style={{
            fontSize: '1.15rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <History size={19} color="var(--accent-cyan)" />
            <span>Recent Detection Activity ({recentList.length})</span>
          </h3>
          <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginTop: '2px' }}>
            {isRetainingHistory ? 'Stored locally in browser (Privacy mode: Retaining)' : 'Session-scoped in-memory storage only'}
          </p>
        </div>

        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
          Click to inspect evaluation
        </span>
      </div>

      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
        {recentList.map((item) => {
          const badge = getRiskBadge(item.risk_level);
          const isSelected = activeId === item.id;

          return (
            <div
              key={item.id}
              onClick={() => onSelectAnalysis(item)}
              style={{
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                padding: '12px 16px',
                backgroundColor: isSelected ? 'var(--bg-surface-elevated)' : 'var(--bg-primary)',
                border: isSelected ? '1.5px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                cursor: 'pointer',
                transition: 'all 0.15s ease',
              }}
            >
              <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                <span style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '0.74rem',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  padding: '3px 8px',
                  borderRadius: '4px',
                  backgroundColor: badge.bg,
                  color: badge.text,
                  border: `1px solid ${badge.border}`,
                }}>
                  {badge.icon}
                  {item.risk_level.replace('_', ' ')}
                </span>

                <div>
                  <div style={{ fontSize: '0.88rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                    Scan #{item.id} • {item.language_detected}
                    {item.is_demo && <span style={{ marginLeft: '8px', fontSize: '0.72rem', color: 'var(--accent-cyan)' }}>[Benchmark Demo]</span>}
                  </div>
                  <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
                    {item.timestamp} • {item.turn_progression.length} Turns • {item.evidence.length} Evidence Flags • Decision: {item.decision}
                  </div>
                </div>
              </div>

              <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                <span style={{ fontSize: '1rem', fontWeight: 800, color: badge.text }}>
                  {item.risk_score.toFixed(0)} <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>/100</span>
                </span>
                <ChevronRight size={16} color="var(--text-muted)" />
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
