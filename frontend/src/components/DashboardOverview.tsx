import React, { useState, useEffect } from 'react';
import {
  ShieldCheck,
  Radio,
  PhoneCall,
  MessageSquare,
  ArrowRight,
  Activity,
  Server,
} from 'lucide-react';
import type { RiskAssessment } from '../types';
import { fetchHealth } from '../api';

interface DashboardOverviewProps {
  recentAnalyses: RiskAssessment[];
  onStartNewAnalysis: () => void;
  onExploreScenarios: () => void;
  onStartLiveMonitor?: () => void;
  onOpenCallerLookup?: () => void;
  onSelectRecentAnalysis?: (item: RiskAssessment) => void;
}

export const DashboardOverview: React.FC<DashboardOverviewProps> = ({
  recentAnalyses,
  onStartNewAnalysis,
  onExploreScenarios,
  onStartLiveMonitor,
  onOpenCallerLookup,
  onSelectRecentAnalysis,
}) => {
  // Query backend deep readiness endpoint
  const [readyInfo, setReadyInfo] = useState<{
    status: string;
    asrStatus?: string;
    engineMethod?: string;
    activeSessions?: number;
  } | null>(null);

  useEffect(() => {
    let isMounted = true;
    async function loadBackendReadiness() {
      try {
        const res = await fetch('/api/ready');
        if (res.ok) {
          const data = await res.json();
          if (isMounted) {
            setReadyInfo({
              status: data.status || 'ready',
              asrStatus: data.asr_service?.status || 'ready',
              engineMethod: data.analyzer_engine?.method || 'rule-based-behavioral-v1',
              activeSessions: data.session_registry?.active_sessions ?? 0,
            });
          }
        }
      } catch {
        // Fallback to basic health
        fetchHealth()
          .then((h) => {
            if (isMounted) {
              setReadyInfo({
                status: h.status,
                engineMethod: h.analysis_method,
              });
            }
          })
          .catch(() => {
            if (isMounted) setReadyInfo(null);
          });
      }
    }
    loadBackendReadiness();
    const interval = setInterval(loadBackendReadiness, 10000);
    return () => {
      isMounted = false;
      clearInterval(interval);
    };
  }, []);

  // Honest metrics derived strictly from actual evaluations
  const totalScans = recentAnalyses.length;
  const highRiskCount = recentAnalyses.filter((a) => a.risk_level === 'HIGH_RISK').length;
  const suspiciousCount = recentAnalyses.filter((a) => a.risk_level === 'SUSPICIOUS').length;
  const lowRiskCount = recentAnalyses.filter((a) => a.risk_level === 'LOW_RISK').length;
  const uncertainCount = recentAnalyses.filter((a) => a.risk_level === 'INSUFFICIENT_EVIDENCE').length;

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '28px' }}>
      {/* 1. Companion Protection Architecture Card */}
      <div className="es-card" style={{ padding: '26px 28px' }}>
        <div
          style={{
            display: 'flex',
            alignItems: 'flex-start',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '20px',
          }}
        >
          <div style={{ maxWidth: '780px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '8px' }}>
              <span className="badge-safe">
                <ShieldCheck size={14} />
                <span>Companion System Active</span>
              </span>
              <span
                style={{
                  fontSize: '0.78rem',
                  color: 'var(--text-muted)',
                  fontWeight: 600,
                }}
              >
                HWV4-PS05 • Real-Time Scam Intervention
              </span>
            </div>

            <h2
              style={{
                fontFamily: 'var(--font-heading)',
                fontSize: '1.45rem',
                fontWeight: 800,
                color: 'var(--text-primary)',
                letterSpacing: '-0.02em',
              }}
            >
              ElderShield Protection Station
            </h2>

            <p style={{ fontSize: '0.92rem', color: 'var(--text-secondary)', marginTop: '8px', lineHeight: 1.6 }}>
              The <strong>ElderShield Android companion app</strong> acts as the primary on-device acoustic defense during calls on speakerphone. This web application provides supporting live monitoring, conversational behavioral analysis, telecom identity verification, and multi-turn evidence ledgers.
            </p>
          </div>

          {/* Quick Primary Actions */}
          <div style={{ display: 'flex', gap: '10px', flexWrap: 'wrap', alignSelf: 'center' }}>
            {onStartLiveMonitor && (
              <button onClick={onStartLiveMonitor} className="btn-primary">
                <Radio size={16} />
                <span>Open Live Monitor</span>
              </button>
            )}
            {onOpenCallerLookup && (
              <button onClick={onOpenCallerLookup} className="btn-secondary">
                <PhoneCall size={16} />
                <span>Verify Caller</span>
              </button>
            )}
          </div>
        </div>

        {/* Diagnostic Subsystem Badges */}
        <div
          style={{
            marginTop: '22px',
            paddingTop: '18px',
            borderTop: '1px solid var(--divider-subtle)',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between',
            flexWrap: 'wrap',
            gap: '12px',
          }}
        >
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px', flexWrap: 'wrap', fontSize: '0.82rem' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)' }}>
              <Server size={14} color="var(--brand-primary)" />
              <span>Engine: <strong>{readyInfo?.engineMethod || 'Rule-Based Multi-Vector'}</strong></span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)' }}>
              <Activity size={14} color="var(--brand-primary)" />
              <span>ASR: <strong>faster-whisper (tiny)</strong></span>
            </div>

            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', color: 'var(--text-secondary)' }}>
              <PhoneCall size={14} color="var(--brand-primary)" />
              <span>Registry: <strong>ITU E.164 + National DB</strong></span>
            </div>
          </div>

          <div
            style={{
              fontSize: '0.8rem',
              color: 'var(--brand-primary)',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
            }}
          >
            <span
              style={{
                width: '7px',
                height: '7px',
                borderRadius: '50%',
                backgroundColor: 'var(--brand-primary)',
              }}
            />
            <span>{readyInfo?.activeSessions ?? 0} Live Stream Session(s) Connected</span>
          </div>
        </div>
      </div>

      {/* 2. Honest Activity Summary Metrics (No manufactured statistics) */}
      <div>
        <div style={{ marginBottom: '12px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Evaluation Telemetry
          </h3>
          <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
            Derived from current session logs
          </span>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(210px, 1fr))', gap: '14px' }}>
          {/* Total Evaluations */}
          <div className="es-card" style={{ padding: '18px 20px' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Total Evaluations
            </span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-primary)', marginTop: '4px', fontFamily: 'var(--font-heading)' }}>
              {totalScans}
            </div>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '2px', display: 'block' }}>
              Conversations & benchmarks evaluated
            </span>
          </div>

          {/* High-Risk Detected */}
          <div className="es-card" style={{ padding: '18px 20px', borderLeft: '3.5px solid var(--risk-high)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--risk-high)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              High-Risk Interventions
            </span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--risk-high)', marginTop: '4px', fontFamily: 'var(--font-heading)' }}>
              {highRiskCount}
            </div>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '2px', display: 'block' }}>
              Digital arrest, coercive extortion, OTP theft
            </span>
          </div>

          {/* Suspicious Activity */}
          <div className="es-card" style={{ padding: '18px 20px', borderLeft: '3.5px solid var(--risk-warning)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--risk-warning)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Suspicious Calls
            </span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--risk-warning)', marginTop: '4px', fontFamily: 'var(--font-heading)' }}>
              {suspiciousCount}
            </div>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '2px', display: 'block' }}>
              Artificial urgency, unverified authority
            </span>
          </div>

          {/* Low Risk / Legitimate */}
          <div className="es-card" style={{ padding: '18px 20px', borderLeft: '3.5px solid var(--risk-safe)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--risk-safe)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Low Risk / Safe
            </span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--risk-safe)', marginTop: '4px', fontFamily: 'var(--font-heading)' }}>
              {lowRiskCount}
            </div>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '2px', display: 'block' }}>
              Normal inquiries, legitimate bank branch visits
            </span>
          </div>

          {/* Inconclusive / Insufficient Evidence */}
          <div className="es-card" style={{ padding: '18px 20px', borderLeft: '3.5px solid var(--text-muted)' }}>
            <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.04em' }}>
              Insufficient Evidence
            </span>
            <div style={{ fontSize: '1.8rem', fontWeight: 800, color: 'var(--text-muted)', marginTop: '4px', fontFamily: 'var(--font-heading)' }}>
              {uncertainCount}
            </div>
            <span style={{ fontSize: '0.76rem', color: 'var(--text-secondary)', marginTop: '2px', display: 'block' }}>
              Ambiguous brief calls, inconclusive context
            </span>
          </div>
        </div>
      </div>

      {/* 3. Three Core Operational Workflows */}
      <div>
        <div style={{ marginBottom: '14px' }}>
          <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
            Primary Investigation Workflows
          </h3>
          <p style={{ fontSize: '0.84rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
            Choose an operational path to monitor audio, triage phone numbers, or analyze recorded speech.
          </p>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(290px, 1fr))', gap: '16px' }}>
          {/* Card A: Live Audio Monitoring */}
          <div
            className="es-card"
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              cursor: 'pointer',
              transition: 'border-color 0.15s ease',
            }}
            onClick={onStartLiveMonitor}
          >
            <div>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-soft-sage)',
                  color: 'var(--brand-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '14px',
                }}
              >
                <Radio size={20} />
              </div>
              <h4 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Live Audio Monitoring
              </h4>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '6px', lineHeight: 1.5 }}>
                Stream acoustic microphone input or speakerphone audio over WebSocket (/ws/live-call) with millisecond turn-by-turn fraud alerts.
              </p>
            </div>
            <div
              style={{
                marginTop: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: 'var(--brand-primary)',
                fontWeight: 600,
                fontSize: '0.84rem',
              }}
            >
              <span>Launch Live Monitor</span>
              <ArrowRight size={14} />
            </div>
          </div>

          {/* Card B: Caller Intelligence */}
          <div
            className="es-card"
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              cursor: 'pointer',
              transition: 'border-color 0.15s ease',
            }}
            onClick={onOpenCallerLookup}
          >
            <div>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-soft-sage)',
                  color: 'var(--brand-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '14px',
                }}
              >
                <PhoneCall size={20} />
              </div>
              <h4 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Caller Identity & Spoof Defense
              </h4>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '6px', lineHeight: 1.5 }}>
                Triage incoming numbers against telecom allocation registries and verify identity conflicts when private numbers impersonate institutions.
              </p>
            </div>
            <div
              style={{
                marginTop: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: 'var(--brand-primary)',
                fontWeight: 600,
                fontSize: '0.84rem',
              }}
            >
              <span>Verify Phone Number</span>
              <ArrowRight size={14} />
            </div>
          </div>

          {/* Card C: Analyze Conversation */}
          <div
            className="es-card"
            style={{
              display: 'flex',
              flexDirection: 'column',
              justifyContent: 'space-between',
              cursor: 'pointer',
              transition: 'border-color 0.15s ease',
            }}
            onClick={onStartNewAnalysis}
          >
            <div>
              <div
                style={{
                  width: '38px',
                  height: '38px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-soft-sage)',
                  color: 'var(--brand-primary)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  marginBottom: '14px',
                }}
              >
                <MessageSquare size={20} />
              </div>
              <h4 style={{ fontSize: '1.02rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Conversation Transcript Analysis
              </h4>
              <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '6px', lineHeight: 1.5 }}>
                Evaluate custom dialogue text or upload call audio recordings (.wav/.mp3) to inspect multi-vector behavioral signals and evidence quotes.
              </p>
            </div>
            <div
              style={{
                marginTop: '16px',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                color: 'var(--brand-primary)',
                fontWeight: 600,
                fontSize: '0.84rem',
              }}
            >
              <span>Analyze Text / Audio</span>
              <ArrowRight size={14} />
            </div>
          </div>
        </div>
      </div>

      {/* 4. Recent Incident Activity Table */}
      {recentAnalyses.length > 0 && (
        <div className="es-card">
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '18px',
            }}
          >
            <div>
              <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Recent Evaluation Activity
              </h3>
              <p style={{ fontSize: '0.82rem', color: 'var(--text-secondary)', marginTop: '2px' }}>
                Latest conversational determinations evaluated by the ElderShield behavioral engine.
              </p>
            </div>

            <button
              onClick={onExploreScenarios}
              className="btn-secondary"
              style={{ fontSize: '0.82rem', padding: '6px 12px' }}
            >
              <span>Explore Benchmark Scenarios</span>
            </button>
          </div>

          <div style={{ overflowX: 'auto' }}>
            <table
              style={{
                width: '100%',
                borderCollapse: 'collapse',
                fontSize: '0.86rem',
                textAlign: 'left',
              }}
            >
              <thead>
                <tr style={{ borderBottom: '1.5px solid var(--divider-subtle)', color: 'var(--text-secondary)' }}>
                  <th style={{ padding: '10px 12px', fontWeight: 600 }}>Evaluation ID</th>
                  <th style={{ padding: '10px 12px', fontWeight: 600 }}>Classification</th>
                  <th style={{ padding: '10px 12px', fontWeight: 600 }}>Risk Score</th>
                  <th style={{ padding: '10px 12px', fontWeight: 600 }}>Decision</th>
                  <th style={{ padding: '10px 12px', fontWeight: 600 }}>Primary Signal</th>
                  <th style={{ padding: '10px 12px', fontWeight: 600, textAlign: 'right' }}>Action</th>
                </tr>
              </thead>
              <tbody>
                {recentAnalyses.slice(0, 6).map((item) => {
                  const badgeClass =
                    item.risk_level === 'HIGH_RISK'
                      ? 'badge-danger'
                      : item.risk_level === 'SUSPICIOUS'
                      ? 'badge-warning'
                      : item.risk_level === 'LOW_RISK'
                      ? 'badge-safe'
                      : 'badge-neutral';

                  return (
                    <tr
                      key={item.id}
                      style={{
                        borderBottom: '1px solid var(--divider-subtle)',
                        transition: 'background-color 0.1s ease',
                      }}
                    >
                      <td style={{ padding: '12px 12px', color: 'var(--text-primary)', fontWeight: 600 }}>
                        <code>{item.id}</code>
                        {item.is_demo && (
                          <span
                            style={{
                              marginLeft: '6px',
                              fontSize: '0.7rem',
                              padding: '1px 5px',
                              borderRadius: '3px',
                              backgroundColor: 'var(--bg-secondary)',
                              color: 'var(--text-muted)',
                            }}
                          >
                            Demo
                          </span>
                        )}
                      </td>
                      <td style={{ padding: '12px 12px' }}>
                        <span className={badgeClass}>{item.risk_level}</span>
                      </td>
                      <td style={{ padding: '12px 12px', color: 'var(--text-primary)', fontWeight: 700 }}>
                        {item.risk_score}/100
                      </td>
                      <td style={{ padding: '12px 12px', fontWeight: 600, color: 'var(--text-primary)' }}>
                        {item.decision}
                      </td>
                      <td
                        style={{
                          padding: '12px 12px',
                          color: 'var(--text-secondary)',
                          maxWidth: '240px',
                          overflow: 'hidden',
                          textOverflow: 'ellipsis',
                          whiteSpace: 'nowrap',
                        }}
                      >
                        {item.evidence && item.evidence.length > 0
                          ? `${item.evidence[0].signal_category}: "${item.evidence[0].exact_quote}"`
                          : 'No hostile indicators detected'}
                      </td>
                      <td style={{ padding: '12px 12px', textAlign: 'right' }}>
                        {onSelectRecentAnalysis && (
                          <button
                            onClick={() => onSelectRecentAnalysis(item)}
                            className="btn-secondary"
                            style={{ fontSize: '0.78rem', padding: '4px 10px' }}
                          >
                            <span>View Findings</span>
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  );
};
