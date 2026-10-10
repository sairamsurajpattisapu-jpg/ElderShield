import React, { useState, useEffect, useRef } from 'react';
import {
  TrendingUp,
  Play,
  Pause,
  RotateCcw,
  Zap,
} from 'lucide-react';
import type { TurnEvaluation, RiskLevel } from '../types';

interface ProgressiveTimelineProps {
  progressions: TurnEvaluation[];
}

export const ProgressiveTimeline: React.FC<ProgressiveTimelineProps> = ({ progressions }) => {
  const [replayIndex, setReplayIndex] = useState<number>(() => progressions.length);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);
  const prevProgressionsRef = useRef(progressions);

  // Sync replay index when regressions reference changes without triggering unconditional setState
  if (prevProgressionsRef.current !== progressions) {
    prevProgressionsRef.current = progressions;
    if (replayIndex > progressions.length || !isPlaying) {
      setReplayIndex(progressions.length);
      setIsPlaying(false);
    }
  }

  // Playback timer
  useEffect(() => {
    let timer: ReturnType<typeof setInterval>;
    if (isPlaying) {
      timer = setInterval(() => {
        setReplayIndex((prev) => {
          if (prev >= progressions.length) {
            setIsPlaying(false);
            return progressions.length;
          }
          return prev + 1;
        });
      }, 1500);
    }
    return () => clearInterval(timer);
  }, [isPlaying, progressions.length]);

  const visibleProgressions = progressions.slice(0, replayIndex);
  const currentActiveTurn = visibleProgressions[visibleProgressions.length - 1];

  const getRiskBadgeClass = (risk: RiskLevel) => {
    switch (risk) {
      case 'HIGH_RISK':
        return 'badge-danger';
      case 'SUSPICIOUS':
        return 'badge-warning';
      case 'LOW_RISK':
        return 'badge-safe';
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return 'badge-neutral';
    }
  };

  return (
    <div className="es-card" style={{ marginBottom: '24px' }}>
      {/* Header & Controls */}
      <div
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          flexWrap: 'wrap',
          gap: '14px',
          borderBottom: '1px solid var(--divider-subtle)',
          paddingBottom: '16px',
          marginBottom: '20px',
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
            <TrendingUp size={18} color="var(--brand-primary)" />
            <span>Turn-by-Turn Behavioral Velocity ({progressions.length} Turns Evaluated)</span>
          </h3>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Inspects incremental risk acceleration as each dialogue statement was uttered.
          </p>
        </div>

        {/* Step Replay Controls */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="btn-secondary"
            style={{ fontSize: '0.82rem', padding: '7px 12px' }}
          >
            {isPlaying ? <Pause size={14} /> : <Play size={14} />}
            <span>{isPlaying ? 'Pause Replay' : 'Replay Timeline'}</span>
          </button>

          <button
            onClick={() => {
              setIsPlaying(false);
              setReplayIndex(progressions.length);
            }}
            className="btn-secondary"
            title="Reset to full view"
            style={{ fontSize: '0.82rem', padding: '7px 10px' }}
          >
            <RotateCcw size={14} />
          </button>

          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginLeft: '4px' }}>
            Turn {replayIndex} of {progressions.length}
          </span>
        </div>
      </div>

      {/* Active Turn Summary Callout */}
      {currentActiveTurn && (
        <div
          style={{
            padding: '14px 18px',
            borderRadius: 'var(--radius-sm)',
            backgroundColor: 'var(--bg-primary)',
            border: '1px solid var(--border-subtle)',
            marginBottom: '20px',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontSize: '0.82rem', fontWeight: 700, color: 'var(--brand-primary)' }}>
                Active Turn {currentActiveTurn.turn_number}: {currentActiveTurn.speaker}
              </span>
              <span className={getRiskBadgeClass(currentActiveTurn.turn_risk_level)}>
                {currentActiveTurn.turn_risk_level}
              </span>
            </div>
            <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', marginTop: '4px', fontStyle: 'italic' }}>
              "{currentActiveTurn.text}"
            </p>
            {currentActiveTurn.turn_rationale && (
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                {currentActiveTurn.turn_rationale}
              </p>
            )}
          </div>

          <div style={{ textAlign: 'right' }}>
            <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)', textTransform: 'uppercase', fontWeight: 700 }}>
              Cumulative Score
            </span>
            <div style={{ fontSize: '1.4rem', fontWeight: 800, color: 'var(--text-primary)', fontFamily: 'var(--font-heading)' }}>
              {currentActiveTurn.cumulative_risk_score}/100
            </div>
          </div>
        </div>
      )}

      {/* Vertical Turn Flow */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
        {visibleProgressions.map((turn, idx) => {
          const isCaller = turn.speaker.toLowerCase().includes('caller') || turn.speaker.toLowerCase().includes('officer');
          const prevScore = idx > 0 ? visibleProgressions[idx - 1].cumulative_risk_score : 0;
          const scoreDelta = turn.cumulative_risk_score - prevScore;

          return (
            <div
              key={turn.turn_number}
              style={{
                display: 'flex',
                gap: '14px',
                padding: '14px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: isCaller ? 'var(--bg-primary)' : 'var(--bg-surface)',
                border: '1px solid var(--border-subtle)',
              }}
            >
              {/* Turn Number Dot */}
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  backgroundColor: isCaller ? 'var(--bg-secondary)' : 'var(--bg-soft-sage)',
                  color: isCaller ? 'var(--text-secondary)' : 'var(--brand-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  fontSize: '0.82rem',
                  fontWeight: 700,
                  flexShrink: 0,
                }}
              >
                {turn.turn_number}
              </div>

              {/* Turn Content */}
              <div style={{ flex: 1 }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '8px', marginBottom: '4px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                    <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                      {turn.speaker}
                    </span>
                    <span className={getRiskBadgeClass(turn.turn_risk_level)}>
                      {turn.turn_risk_level}
                    </span>
                  </div>

                  <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.82rem' }}>
                    {scoreDelta > 0 && (
                      <span style={{ color: 'var(--risk-high)', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '2px' }}>
                        <Zap size={12} /> +{scoreDelta.toFixed(0)}
                      </span>
                    )}
                    <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>
                      Score: {turn.cumulative_risk_score}/100
                    </span>
                  </div>
                </div>

                <p style={{ fontSize: '0.9rem', color: 'var(--text-primary)', lineHeight: 1.45 }}>
                  "{turn.text}"
                </p>

                {turn.newly_detected_signals && turn.newly_detected_signals.length > 0 && (
                  <div style={{ marginTop: '8px', display: 'flex', gap: '6px', flexWrap: 'wrap' }}>
                    {turn.newly_detected_signals.map((sig, sIdx) => (
                      <span
                        key={sIdx}
                        style={{
                          fontSize: '0.72rem',
                          padding: '2px 7px',
                          borderRadius: 'var(--radius-xs)',
                          backgroundColor: 'var(--risk-high-bg)',
                          border: '1px solid var(--risk-high-border)',
                          color: 'var(--risk-high)',
                          fontWeight: 600,
                        }}
                      >
                        {sig.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
