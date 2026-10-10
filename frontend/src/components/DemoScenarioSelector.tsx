import React from 'react';
import { PlayCircle } from 'lucide-react';
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
  const getBadgeClass = (risk: RiskLevel) => {
    switch (risk) {
      case 'LOW_RISK':
        return 'badge-safe';
      case 'HIGH_RISK':
        return 'badge-danger';
      case 'SUSPICIOUS':
        return 'badge-warning';
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return 'badge-neutral';
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
          marginBottom: '16px',
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
            <span>Verified Benchmark Demo Scenarios</span>
            <span
              style={{
                fontSize: '0.72rem',
                color: 'var(--brand-primary)',
                backgroundColor: 'var(--bg-soft-sage)',
                padding: '2px 8px',
                borderRadius: 'var(--radius-full)',
                border: '1px solid var(--brand-subtle)',
                fontWeight: 600,
              }}
            >
              Deterministic Test Cases
            </span>
          </h3>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Click any reproducible benchmark scenario below to evaluate conversational fraud detection and turn-by-turn velocity.
          </p>
        </div>
      </div>

      {/* Grid of demo cards */}
      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '12px',
        }}
      >
        {scenarios.map((sc) => {
          const isSelected = sc.id === selectedScenarioId;
          const badgeClass = getBadgeClass(sc.expected_classification);

          return (
            <div
              key={sc.id}
              onClick={() => !isLoading && onSelectScenario(sc)}
              style={{
                padding: '16px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: isSelected ? 'var(--bg-soft-sage)' : 'var(--bg-primary)',
                border: isSelected ? '1.5px solid var(--brand-primary)' : '1px solid var(--border-subtle)',
                cursor: isLoading ? 'wait' : 'pointer',
                display: 'flex',
                flexDirection: 'column',
                justifyContent: 'space-between',
                transition: 'border-color 0.15s ease, background-color 0.15s ease',
              }}
            >
              <div>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: '8px', marginBottom: '8px' }}>
                  <span className={badgeClass}>
                    {sc.expected_classification.replace(/_/g, ' ')}
                  </span>

                  <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                    {sc.language}
                  </span>
                </div>

                <h4 style={{ fontSize: '0.96rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '4px' }}>
                  {sc.title}
                </h4>

                <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.45 }}>
                  {sc.description}
                </p>
              </div>

              <div
                style={{
                  marginTop: '12px',
                  paddingTop: '8px',
                  borderTop: '1px solid var(--divider-subtle)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  fontSize: '0.78rem',
                }}
              >
                <span style={{ color: 'var(--text-muted)' }}>
                  {sc.turns.length} dialogue turns
                </span>

                <span
                  style={{
                    color: isSelected ? 'var(--brand-primary)' : 'var(--text-secondary)',
                    fontWeight: 600,
                    display: 'flex',
                    alignItems: 'center',
                    gap: '4px',
                  }}
                >
                  <PlayCircle size={13} />
                  <span>{isSelected ? 'Loaded' : 'Load Benchmark'}</span>
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
