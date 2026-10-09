import React from 'react';
import { PlayCircle, ShieldCheck, AlertOctagon, HelpCircle, ShieldAlert } from 'lucide-react';
import type { DemoScenario, RiskLevel } from '../types';

interface DemoScenarioSelectorProps {
  scenarios: DemoScenario[];
  selectedScenarioId: string | null;
  onSelectScenario: (scenario: DemoScenario) => void;
  isLoading: boolean;
}

export const DemoScenarioSelector: React.FC<DemoScenarioSelectorProps> = ({
  scenarios,
  selectedScenarioId,
  onSelectScenario,
  isLoading,
}) => {
  const getBadgeStyle = (risk: RiskLevel) => {
    switch (risk) {
      case 'LOW_RISK':
        return {
          bg: 'var(--risk-low-bg)',
          border: 'var(--risk-low-border)',
          color: 'var(--risk-low)',
          icon: <ShieldCheck size={14} />,
        };
      case 'HIGH_RISK':
        return {
          bg: 'var(--risk-high-bg)',
          border: 'var(--risk-high-border)',
          color: 'var(--risk-high)',
          icon: <AlertOctagon size={14} />,
        };
      case 'SUSPICIOUS':
        return {
          bg: 'var(--risk-suspicious-bg)',
          border: 'var(--risk-suspicious-border)',
          color: 'var(--risk-suspicious)',
          icon: <ShieldAlert size={14} />,
        };
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return {
          bg: 'var(--risk-uncertain-bg)',
          border: 'var(--risk-uncertain-border)',
          color: 'var(--risk-uncertain)',
          icon: <HelpCircle size={14} />,
        };
    }
  };

  return (
    <div style={{
      backgroundColor: 'var(--bg-surface)',
      border: '1px solid var(--border-subtle)',
      borderRadius: 'var(--radius-lg)',
      padding: '22px',
      marginBottom: '28px',
    }}>
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '12px',
        marginBottom: '16px',
      }}>
        <div>
          <h3 style={{
            fontSize: '1.1rem',
            fontWeight: 700,
            color: 'var(--text-primary)',
            display: 'flex',
            alignItems: 'center',
            gap: '8px',
          }}>
            <span>Benchmark Demo Scenarios</span>
            <span style={{
              fontSize: '0.72rem',
              color: 'var(--accent-cyan)',
              backgroundColor: 'rgba(6, 182, 212, 0.12)',
              padding: '2px 8px',
              borderRadius: '4px',
              border: '1px solid rgba(6, 182, 212, 0.3)',
            }}>
              Deterministic Test Cases
            </span>
          </h3>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Click any reproducible test case below to inspect turn-by-turn progressive risk evaluation in the core engine.
          </p>
        </div>
      </div>

      {/* Grid of demo cards */}
      <div style={{
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: '14px',
      }}>
        {scenarios.map((sc) => {
          const badge = getBadgeStyle(sc.expected_classification);
          const isSelected = selectedScenarioId === sc.id;

          return (
            <div
              key={sc.id}
              onClick={() => !isLoading && onSelectScenario(sc)}
              style={{
                backgroundColor: isSelected ? 'var(--bg-surface-elevated)' : 'var(--bg-primary)',
                border: isSelected ? '1.5px solid var(--accent-cyan)' : '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                padding: '16px',
                cursor: isLoading ? 'not-allowed' : 'pointer',
                transition: 'all 0.2s ease',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                position: 'relative',
              }}
            >
              <div>
                <div style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '10px',
                  gap: '8px',
                }}>
                  <span style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '5px',
                    fontSize: '0.74rem',
                    fontWeight: 700,
                    textTransform: 'uppercase',
                    padding: '3px 8px',
                    borderRadius: '4px',
                    backgroundColor: badge.bg,
                    border: `1px solid ${badge.border}`,
                    color: badge.color,
                  }}>
                    {badge.icon}
                    {sc.expected_classification.replace('_', ' ')}
                  </span>

                  <span style={{
                    fontSize: '0.75rem',
                    color: 'var(--text-muted)',
                  }}>
                    {sc.language}
                  </span>
                </div>

                <h4 style={{
                  fontSize: '0.98rem',
                  fontWeight: 600,
                  color: isSelected ? 'var(--accent-cyan)' : 'var(--text-primary)',
                  marginBottom: '6px',
                  lineHeight: 1.35,
                }}>
                  {sc.title}
                </h4>

                <p style={{
                  fontSize: '0.82rem',
                  color: 'var(--text-secondary)',
                  lineHeight: 1.45,
                  display: '-webkit-box',
                  WebkitLineClamp: 3,
                  WebkitBoxOrient: 'vertical',
                  overflow: 'hidden',
                }}>
                  {sc.description}
                </p>
              </div>

              <div style={{
                marginTop: '14px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'space-between',
                paddingTop: '10px',
                borderTop: '1px solid var(--border-subtle)',
              }}>
                <span style={{
                  fontSize: '0.78rem',
                  color: 'var(--text-muted)',
                }}>
                  {sc.turns.length} Conversation Turns
                </span>

                <button
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '5px',
                    fontSize: '0.82rem',
                    fontWeight: 600,
                    backgroundColor: isSelected ? 'var(--accent-cyan)' : 'transparent',
                    color: isSelected ? '#080c16' : 'var(--accent-cyan)',
                    border: isSelected ? 'none' : '1px solid var(--border-prominent)',
                    borderRadius: 'var(--radius-sm)',
                    padding: '4px 10px',
                  }}
                >
                  <PlayCircle size={14} />
                  <span>{isSelected ? 'Loaded' : 'Run Scenario'}</span>
                </button>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
