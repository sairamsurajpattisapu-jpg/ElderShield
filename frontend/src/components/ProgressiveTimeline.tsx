import React, { useState, useEffect } from 'react';
import {
  TrendingUp,
  User,
  Phone,
  Play,
  Pause,
  RotateCcw,
  ChevronRight,
  Highlighter,
} from 'lucide-react';
import type { TurnEvaluation, RiskLevel } from '../types';

interface ProgressiveTimelineProps {
  progressions: TurnEvaluation[];
}

export const ProgressiveTimeline: React.FC<ProgressiveTimelineProps> = ({ progressions }) => {
  const [replayIndex, setReplayIndex] = useState<number>(progressions.length);
  const [isPlaying, setIsPlaying] = useState<boolean>(false);

  // Sync replay index when new analysis loads
  useEffect(() => {
    setReplayIndex(progressions.length);
    setIsPlaying(false);
  }, [progressions]);

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
      }, 1600);
    }
    return () => clearInterval(timer);
  }, [isPlaying, progressions.length]);

  const visibleProgressions = progressions.slice(0, replayIndex);
  const currentActiveTurn = visibleProgressions[visibleProgressions.length - 1];

  const getRiskColor = (risk: RiskLevel) => {
    switch (risk) {
      case 'HIGH_RISK':
        return { text: '#ef4444', bg: 'rgba(239, 68, 68, 0.15)', border: '#ef4444' };
      case 'SUSPICIOUS':
        return { text: '#f59e0b', bg: 'rgba(245, 158, 11, 0.15)', border: '#f59e0b' };
      case 'LOW_RISK':
        return { text: '#10b981', bg: 'rgba(16, 185, 129, 0.15)', border: '#10b981' };
      case 'INSUFFICIENT_EVIDENCE':
      default:
        return { text: '#94a3b8', bg: 'rgba(148, 163, 184, 0.15)', border: '#94a3b8' };
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
      {/* Header and Replay Controls */}
      <div style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        flexWrap: 'wrap',
        gap: '14px',
        borderBottom: '1px solid var(--border-subtle)',
        paddingBottom: '16px',
        marginBottom: '20px',
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
            <TrendingUp size={20} color="var(--accent-cyan)" />
            <span>Progressive Conversation Timeline</span>
          </h3>
          <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
            Real-time evaluation for every turn rendered from actual backend progressive analysis.
          </p>
        </div>

        {/* Step Replay Controls */}
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          backgroundColor: 'var(--bg-primary)',
          padding: '6px 12px',
          borderRadius: 'var(--radius-md)',
          border: '1px solid var(--border-subtle)',
        }}>
          <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600 }}>
            Turn {replayIndex} of {progressions.length}
          </span>

          <button
            onClick={() => {
              if (replayIndex >= progressions.length) setReplayIndex(1);
              setIsPlaying(!isPlaying);
            }}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 10px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: isPlaying ? 'rgba(239, 68, 68, 0.2)' : 'rgba(6, 182, 212, 0.2)',
              border: `1px solid ${isPlaying ? '#ef4444' : 'var(--accent-cyan)'}`,
              color: isPlaying ? '#ef4444' : 'var(--accent-cyan)',
              fontSize: '0.78rem',
              fontWeight: 700,
            }}
          >
            {isPlaying ? <Pause size={13} /> : <Play size={13} />}
            <span>{isPlaying ? 'Pause' : 'Auto Play'}</span>
          </button>

          <button
            onClick={() => {
              setIsPlaying(false);
              setReplayIndex((prev) => Math.min(progressions.length, prev + 1));
            }}
            disabled={replayIndex >= progressions.length}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '2px',
              padding: '4px 8px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-secondary)',
              fontSize: '0.78rem',
              cursor: replayIndex >= progressions.length ? 'not-allowed' : 'pointer',
              opacity: replayIndex >= progressions.length ? 0.4 : 1,
            }}
          >
            <span>Next</span>
            <ChevronRight size={13} />
          </button>

          <button
            onClick={() => {
              setIsPlaying(false);
              setReplayIndex(progressions.length);
            }}
            style={{
              padding: '4px 8px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--bg-surface-elevated)',
              border: '1px solid var(--border-subtle)',
              color: 'var(--text-muted)',
              fontSize: '0.78rem',
            }}
            title="View All Turns"
          >
            <RotateCcw size={13} />
          </button>
        </div>
      </div>

      {/* Real-time score ticker for current turn */}
      {currentActiveTurn && (
        <div style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          backgroundColor: 'var(--bg-surface-elevated)',
          padding: '12px 18px',
          borderRadius: 'var(--radius-md)',
          marginBottom: '20px',
          border: '1px solid var(--border-subtle)',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <span style={{ fontSize: '0.84rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
              Assessment at Turn {currentActiveTurn.turn_number}:
            </span>
            <span style={{
              fontSize: '0.78rem',
              fontWeight: 800,
              padding: '3px 8px',
              borderRadius: '4px',
              backgroundColor: getRiskColor(currentActiveTurn.turn_risk_level).bg,
              color: getRiskColor(currentActiveTurn.turn_risk_level).text,
              border: `1px solid ${getRiskColor(currentActiveTurn.turn_risk_level).border}`,
            }}>
              {currentActiveTurn.turn_risk_level.replace('_', ' ')}
            </span>
          </div>

          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '0.82rem', color: 'var(--text-muted)' }}>Progressive Score:</span>
            <span style={{
              fontSize: '1.25rem',
              fontWeight: 900,
              color: getRiskColor(currentActiveTurn.turn_risk_level).text,
            }}>
              {currentActiveTurn.cumulative_risk_score.toFixed(1)} / 100
            </span>
          </div>
        </div>
      )}

      {/* Visual Timeline of Turns */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: '14px' }}>
        {visibleProgressions.map((p) => {
          const isCaller = p.speaker.toLowerCase().includes('caller') ||
                           p.speaker.toLowerCase().includes('agent') ||
                           p.speaker.toLowerCase().includes('police') ||
                           p.speaker.toLowerCase().includes('manager');
          const riskStyle = getRiskColor(p.turn_risk_level);
          const hasNewThreats = p.newly_detected_signals.length > 0;

          return (
            <div
              key={p.turn_number}
              style={{
                display: 'grid',
                gridTemplateColumns: '80px 1fr auto',
                gap: '16px',
                padding: '16px',
                backgroundColor: hasNewThreats && isCaller
                  ? 'rgba(239, 68, 68, 0.05)'
                  : 'var(--bg-primary)',
                border: hasNewThreats && isCaller
                  ? '1px solid rgba(239, 68, 68, 0.3)'
                  : '1px solid var(--border-subtle)',
                borderRadius: 'var(--radius-md)',
                alignItems: 'flex-start',
                transition: 'all 0.2s ease',
              }}
            >
              {/* Turn Number & Speaker */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px' }}>
                <span style={{
                  fontSize: '0.76rem',
                  fontWeight: 700,
                  color: 'var(--text-muted)',
                  letterSpacing: '0.04em',
                }}>
                  TURN {p.turn_number}
                </span>

                <div style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '4px',
                  fontSize: '0.8rem',
                  fontWeight: 700,
                  color: isCaller ? '#38bdf8' : '#34d399',
                }}>
                  {isCaller ? <Phone size={13} /> : <User size={13} />}
                  <span>{p.speaker}</span>
                </div>
              </div>

              {/* Spoken Text & Highlighted Spans */}
              <div>
                <p style={{
                  fontSize: '0.94rem',
                  color: 'var(--text-primary)',
                  lineHeight: 1.5,
                  fontWeight: 500,
                }}>
                  "{p.text}"
                </p>

                {/* Highlighted exact quote chips in context */}
                {p.highlighted_spans && p.highlighted_spans.length > 0 && (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    flexWrap: 'wrap',
                    marginTop: '6px',
                  }}>
                    <Highlighter size={13} color="var(--accent-cyan)" />
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>Flagged in turn:</span>
                    {p.highlighted_spans.map((span, sIdx) => (
                      <span
                        key={sIdx}
                        style={{
                          fontSize: '0.74rem',
                          padding: '1px 6px',
                          borderRadius: '3px',
                          backgroundColor: 'rgba(245, 158, 11, 0.15)',
                          color: '#fcd34d',
                          border: '1px solid rgba(245, 158, 11, 0.3)',
                          fontStyle: 'italic',
                        }}
                      >
                        "{span}"
                      </span>
                    ))}
                  </div>
                )}

                {/* Newly detected behaviors badges */}
                {p.newly_detected_signals.length > 0 && (
                  <div style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '6px',
                    flexWrap: 'wrap',
                    marginTop: '8px',
                  }}>
                    <span style={{ fontSize: '0.74rem', color: 'var(--text-muted)' }}>
                      Signals Triggered:
                    </span>
                    {p.newly_detected_signals.map((b, bIdx) => (
                      <span
                        key={bIdx}
                        style={{
                          fontSize: '0.74rem',
                          fontWeight: 700,
                          backgroundColor: b.includes('Safeguard')
                            ? 'rgba(16, 185, 129, 0.2)'
                            : 'rgba(239, 68, 68, 0.2)',
                          color: b.includes('Safeguard') ? '#10b981' : '#fca5a5',
                          border: `1px solid ${b.includes('Safeguard') ? '#059669' : '#dc2626'}`,
                          padding: '2px 8px',
                          borderRadius: '4px',
                        }}
                      >
                        {b}
                      </span>
                    ))}
                  </div>
                )}

                <div style={{
                  fontSize: '0.78rem',
                  color: 'var(--text-muted)',
                  marginTop: '6px',
                  fontStyle: 'italic',
                }}>
                  {p.turn_rationale}
                </div>
              </div>

              {/* Cumulative Turn Score Badge */}
              <div style={{
                textAlign: 'right',
                minWidth: '100px',
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'flex-end',
                gap: '4px',
              }}>
                <span style={{
                  fontSize: '1.15rem',
                  fontWeight: 900,
                  color: riskStyle.text,
                }}>
                  {p.cumulative_risk_score.toFixed(0)} <span style={{ fontSize: '0.72rem', color: 'var(--text-muted)' }}>/100</span>
                </span>
                <span style={{
                  fontSize: '0.7rem',
                  fontWeight: 800,
                  textTransform: 'uppercase',
                  padding: '2px 6px',
                  borderRadius: '3px',
                  backgroundColor: riskStyle.bg,
                  color: riskStyle.text,
                  border: `1px solid ${riskStyle.border}`,
                }}>
                  {p.turn_risk_level.replace('_', ' ')}
                </span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
