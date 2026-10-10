import React, { useState, useEffect, useCallback } from 'react';
import { Header } from './components/Header';
import type { NavTab } from './components/Header';
import { Sidebar } from './components/Sidebar';
import { DashboardOverview } from './components/DashboardOverview';
import { LiveCallMonitor } from './components/LiveCallMonitor';
import { CallerLookupView } from './components/CallerLookupView';
import { DemoScenarioSelector } from './components/DemoScenarioSelector';
import { AnalysisInput } from './components/AnalysisInput';
import { RiskOverviewCard } from './components/RiskOverviewCard';
import { ProgressiveTimeline } from './components/ProgressiveTimeline';
import { EvidenceFindings } from './components/EvidenceFindings';
import { ProtectionRecommendations } from './components/ProtectionRecommendations';
import { RecentAnalysesDrawer } from './components/RecentAnalysesDrawer';
import { SettingsView } from './components/SettingsView';

import {
  fetchDemoScenarios,
  fetchRecentAnalyses,
  fetchReadyStatus,
  analyzeConversation,
  analyzeProgression,
} from './api';
import type { DemoScenario, RiskAssessment, UserPreferences, ProgressionResponse } from './types';
import { playRiskAlert } from './utils/audioAlert';
import { AlertCircle, ArrowLeft, History } from 'lucide-react';

const PREFS_STORAGE_KEY = 'eldershield_user_prefs_v1';
const HISTORY_STORAGE_KEY = 'eldershield_local_history_v1';

export const App: React.FC = () => {
  // Navigation tab state
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');
  const [isMobileSidebarOpen, setIsMobileSidebarOpen] = useState<boolean>(false);

  // Backend telemetry state
  const [isBackendHealthy, setIsBackendHealthy] = useState<boolean>(false);
  const [activeSessionsCount, setActiveSessionsCount] = useState<number>(0);

  // User preferences & accessibility state
  const [preferences, setPreferences] = useState<UserPreferences>(() => {
    try {
      const saved = localStorage.getItem(PREFS_STORAGE_KEY);
      if (saved) return JSON.parse(saved);
    } catch {
      // Fallback
    }
    return {
      fontSize: 'normal',
      highContrast: false,
      soundAlerts: true,
      saveHistoryLocally: false, // Default: zero-disk retention
    };
  });

  // Application data state
  const [scenarios, setScenarios] = useState<DemoScenario[]>([]);
  const [recentAnalyses, setRecentAnalyses] = useState<RiskAssessment[]>([]);
  const [selectedDemoId, setSelectedDemoId] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>('');
  const [currentAnalysis, setCurrentAnalysis] = useState<RiskAssessment | null>(null);
  const [activeProgression, setActiveProgression] = useState<ProgressionResponse | null>(null);

  // UI state
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  // Save preferences changes
  const updatePreferences = (newPrefs: Partial<UserPreferences>) => {
    setPreferences((prev) => {
      const updated = { ...prev, ...newPrefs };
      try {
        localStorage.setItem(PREFS_STORAGE_KEY, JSON.stringify(updated));
      } catch {
        // quota
      }
      return updated;
    });
  };

  // Sync accessibility classes with DOM body
  useEffect(() => {
    document.body.className = '';
    if (preferences.fontSize === 'large') document.body.classList.add('font-large');
    if (preferences.fontSize === 'xlarge') document.body.classList.add('font-xlarge');
    if (preferences.highContrast) document.body.classList.add('high-contrast');
  }, [preferences.fontSize, preferences.highContrast]);

  // Telemetry check
  const checkTelemetry = useCallback(async () => {
    try {
      const ready = await fetchReadyStatus();
      setIsBackendHealthy(ready.status === 'ready' || ready.status === 'ok');
      if (ready.services?.active_live_call_sessions !== undefined) {
        setActiveSessionsCount(ready.services.active_live_call_sessions);
      }
    } catch {
      setIsBackendHealthy(false);
    }
  }, []);

  // Initial data loading
  useEffect(() => {
    async function init() {
      try {
        checkTelemetry();
        const [scenariosData, backendRecent] = await Promise.all([
          fetchDemoScenarios().catch(() => []),
          fetchRecentAnalyses(15).catch(() => []),
        ]);
        setScenarios(scenariosData);

        // Check local storage if user opted-in to local retention
        let combinedRecent = backendRecent;
        if (preferences.saveHistoryLocally) {
          try {
            const savedLocal = localStorage.getItem(HISTORY_STORAGE_KEY);
            if (savedLocal) {
              const parsed: RiskAssessment[] = JSON.parse(savedLocal);
              const map = new Map<string, RiskAssessment>();
              [...parsed, ...backendRecent].forEach((item) => map.set(item.id, item));
              combinedRecent = Array.from(map.values());
            }
          } catch {
            // ignore
          }
        }

        setRecentAnalyses(combinedRecent);

        // Preload first scenario result if available
        if (combinedRecent && combinedRecent.length > 0) {
          setCurrentAnalysis(combinedRecent[0]);
          setSelectedDemoId(combinedRecent[0].demo_scenario_id || null);
          setTranscript(combinedRecent[0].raw_transcript || '');
        }
      } catch (err) {
        console.error('Initialization error:', err);
        setErrorMsg('Unable to connect to ElderShield detection service. Ensure FastAPI backend is running on 127.0.0.1:8000.');
      }
    }
    init();

    // Heartbeat every 20 seconds
    const interval = setInterval(checkTelemetry, 20000);
    return () => clearInterval(interval);
  }, [preferences.saveHistoryLocally, checkTelemetry]);

  // Persist to local storage if user preference enabled
  const saveToLocalHistoryIfEnabled = (newAssessment: RiskAssessment) => {
    if (!preferences.saveHistoryLocally) return;
    try {
      const existing = localStorage.getItem(HISTORY_STORAGE_KEY);
      const parsed: RiskAssessment[] = existing ? JSON.parse(existing) : [];
      const updated = [newAssessment, ...parsed.filter((p) => p.id !== newAssessment.id)].slice(0, 30);
      localStorage.setItem(HISTORY_STORAGE_KEY, JSON.stringify(updated));
    } catch {
      // quota
    }
  };

  const handleClearLocalHistory = () => {
    try {
      localStorage.removeItem(HISTORY_STORAGE_KEY);
    } catch {
      // ignore
    }
    setRecentAnalyses((prev) => prev.filter((p) => p.is_demo));
  };

  // Run demo scenario
  const handleSelectScenario = async (sc: DemoScenario) => {
    setSelectedDemoId(sc.id);
    setTranscript(sc.raw_transcript);
    setErrorMsg(null);
    setIsLoading(true);

    try {
      const [assessment, progression] = await Promise.all([
        analyzeConversation(sc.raw_transcript, sc.id),
        analyzeProgression(sc.raw_transcript, sc.id),
      ]);

      setCurrentAnalysis(assessment);
      setActiveProgression(progression);

      setRecentAnalyses((prev) => [assessment, ...prev.filter((r) => r.id !== assessment.id)]);
      saveToLocalHistoryIfEnabled(assessment);

      if (preferences.soundAlerts) {
        playRiskAlert(assessment.risk_level);
      }

      setCurrentTab('results');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setErrorMsg(message);
    } finally {
      setIsLoading(false);
    }
  };

  // Run custom transcript analysis
  const handleAnalyzeCustom = async () => {
    if (!transcript.trim()) return;
    setErrorMsg(null);
    setIsLoading(true);

    try {
      const [assessment, progression] = await Promise.all([
        analyzeConversation(transcript, selectedDemoId || undefined),
        analyzeProgression(transcript, selectedDemoId || undefined),
      ]);

      setCurrentAnalysis(assessment);
      setActiveProgression(progression);

      setRecentAnalyses((prev) => [assessment, ...prev.filter((r) => r.id !== assessment.id)]);
      saveToLocalHistoryIfEnabled(assessment);

      if (preferences.soundAlerts) {
        playRiskAlert(assessment.risk_level);
      }

      setCurrentTab('results');
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setErrorMsg(message);
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetToCustom = () => {
    setSelectedDemoId(null);
    setTranscript('');
    setCurrentAnalysis(null);
    setActiveProgression(null);
  };

  const currentDemo = scenarios.find((s) => s.id === selectedDemoId);

  return (
    <div className="app-layout">
      {/* 1. Desktop & Mobile Responsive Sidebar */}
      <Sidebar
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        hasActiveResult={Boolean(currentAnalysis)}
        isOpenMobile={isMobileSidebarOpen}
        onCloseMobile={() => setIsMobileSidebarOpen(false)}
        isBackendHealthy={isBackendHealthy}
        activeSessionsCount={activeSessionsCount}
      />

      {/* 2. Main Application Wrapper (offset by sidebar width on desktop) */}
      <div className="main-wrapper">
        {/* Header Bar */}
        <Header
          currentTab={currentTab}
          onOpenMobileSidebar={() => setIsMobileSidebarOpen(true)}
          isBackendHealthy={isBackendHealthy}
          hasActiveResult={Boolean(currentAnalysis)}
          onSelectTab={setCurrentTab}
        />

        {/* Primary Content Container */}
        <main
          style={{
            maxWidth: '1240px',
            margin: '0 auto',
            padding: '28px 24px 48px',
            flex: 1,
            width: '100%',
          }}
        >
          {/* Error notification banner if any */}
          {errorMsg && (
            <div
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '10px',
                padding: '14px 18px',
                backgroundColor: 'var(--risk-high-bg)',
                border: '1px solid var(--risk-high-border)',
                borderRadius: 'var(--radius-sm)',
                color: 'var(--risk-high)',
                marginBottom: '24px',
              }}
            >
              <AlertCircle size={20} color="var(--risk-high)" style={{ flexShrink: 0 }} />
              <span style={{ fontSize: '0.9rem', fontWeight: 600 }}>{errorMsg}</span>
            </div>
          )}

          {/* PAGE 1: DASHBOARD OVERVIEW */}
          {currentTab === 'dashboard' && (
            <div>
              <DashboardOverview
                recentAnalyses={recentAnalyses}
                onStartNewAnalysis={() => setCurrentTab('analyze')}
                onStartLiveMonitor={() => setCurrentTab('live')}
                onExploreScenarios={() => {
                  const el = document.getElementById('demo-scenarios-section');
                  el?.scrollIntoView({ behavior: 'smooth' });
                }}
              />

              <div id="demo-scenarios-section" style={{ marginTop: '28px' }}>
                <DemoScenarioSelector
                  scenarios={scenarios}
                  selectedScenarioId={selectedDemoId}
                  onSelectScenario={handleSelectScenario}
                  isLoading={isLoading}
                />
              </div>

              {currentAnalysis && (
                <div style={{ marginTop: '28px' }}>
                  <div
                    style={{
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'space-between',
                      marginBottom: '12px',
                    }}
                  >
                    <span
                      style={{
                        fontSize: '0.82rem',
                        fontWeight: 700,
                        textTransform: 'uppercase',
                        letterSpacing: '0.04em',
                        color: 'var(--brand-primary)',
                      }}
                    >
                      Latest Session Risk Determination
                    </span>
                    <button
                      onClick={() => setCurrentTab('results')}
                      style={{
                        background: 'none',
                        border: 'none',
                        color: 'var(--brand-primary)',
                        fontSize: '0.82rem',
                        fontWeight: 600,
                        cursor: 'pointer',
                        textDecoration: 'underline',
                      }}
                    >
                      View Full Evidence Ledger →
                    </button>
                  </div>
                  <RiskOverviewCard result={currentAnalysis} />
                </div>
              )}

              <div style={{ marginTop: '28px' }}>
                <RecentAnalysesDrawer
                  recentList={recentAnalyses}
                  onSelectAnalysis={(res) => {
                    setCurrentAnalysis(res);
                    setSelectedDemoId(res.demo_scenario_id || null);
                    setTranscript(res.raw_transcript || '');
                    setCurrentTab('results');
                  }}
                  activeId={currentAnalysis?.id}
                  isRetainingHistory={preferences.saveHistoryLocally}
                />
              </div>
            </div>
          )}

          {/* PAGE 2: LIVE AUDIO MONITOR */}
          {currentTab === 'live' && (
            <div>
              <LiveCallMonitor
                onLoadFullAnalysis={(res) => {
                  setCurrentAnalysis(res);
                  setTranscript(res.raw_transcript || '');
                  setSelectedDemoId(res.demo_scenario_id || null);
                  setRecentAnalyses((prev) => [res, ...prev.filter((r) => r.id !== res.id)]);
                  saveToLocalHistoryIfEnabled(res);
                  setCurrentTab('results');
                }}
                soundAlertsEnabled={preferences.soundAlerts}
                onOpenCallerLookup={() => setCurrentTab('caller')}
              />
            </div>
          )}

          {/* PAGE 3: CALLER INTELLIGENCE & SPOOF DEFENSE */}
          {currentTab === 'caller' && (
            <div>
              <CallerLookupView />
            </div>
          )}

          {/* PAGE 4: ANALYZE CONVERSATION */}
          {currentTab === 'analyze' && (
            <div>
              <div style={{ marginBottom: '22px' }}>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Analyze Conversation Transcript
                </h2>
                <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Evaluate speech dialogues, transcripts, or uploaded calls against multi-vector behavioral fraud indicators.
                </p>
              </div>

              <DemoScenarioSelector
                scenarios={scenarios}
                selectedScenarioId={selectedDemoId}
                onSelectScenario={handleSelectScenario}
                isLoading={isLoading}
              />

              <div style={{ marginTop: '24px' }}>
                <AnalysisInput
                  transcript={transcript}
                  setTranscript={setTranscript}
                  onAnalyze={handleAnalyzeCustom}
                  isLoading={isLoading}
                  isDemoLoaded={Boolean(selectedDemoId)}
                  demoScenarioTitle={currentDemo?.title}
                  onResetToCustom={handleResetToCustom}
                />
              </div>
            </div>
          )}

          {/* PAGE 5: RISK RESULTS & EVIDENCE LEDGER */}
          {currentTab === 'results' && currentAnalysis && (
            <div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '22px',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}
              >
                <div>
                  <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    Detailed Forensic Risk Assessment
                  </h2>
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                    Scan #{currentAnalysis.id} • Decision: <strong>{currentAnalysis.decision}</strong> • {currentAnalysis.timestamp}
                  </p>
                </div>

                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <button
                    onClick={() => setCurrentTab('timeline')}
                    className="btn-secondary"
                    style={{ padding: '8px 14px', fontSize: '0.84rem' }}
                  >
                    <span>View Risk Velocity Timeline</span>
                  </button>

                  <button
                    onClick={() => setCurrentTab('analyze')}
                    className="btn-primary"
                    style={{ padding: '8px 14px', fontSize: '0.84rem' }}
                  >
                    <ArrowLeft size={15} />
                    <span>Analyze Another Call</span>
                  </button>
                </div>
              </div>

              {/* 1. Risk Overview Card */}
              <RiskOverviewCard result={currentAnalysis} />

              {/* 2. Deterministic Evidence Ledger */}
              <EvidenceFindings evidence={currentAnalysis.evidence} />

              {/* 3. Actionable Protection Recommendations */}
              <ProtectionRecommendations result={currentAnalysis} />
            </div>
          )}

          {/* PAGE 6: RISK VELOCITY PROGRESSION TIMELINE */}
          {currentTab === 'timeline' && currentAnalysis && (
            <div>
              <div
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'space-between',
                  marginBottom: '22px',
                  flexWrap: 'wrap',
                  gap: '12px',
                }}
              >
                <div>
                  <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                    Turn-by-Turn Risk Velocity Timeline
                  </h2>
                  <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '3px' }}>
                    Incremental risk acceleration measured across each conversational exchange (`/api/analyze/progression`).
                  </p>
                </div>

                <button
                  onClick={() => setCurrentTab('results')}
                  className="btn-secondary"
                  style={{ padding: '8px 14px', fontSize: '0.84rem' }}
                >
                  <ArrowLeft size={15} />
                  <span>Return to Evidence Findings</span>
                </button>
              </div>

              <ProgressiveTimeline progressions={activeProgression?.turns || currentAnalysis.turn_progression} />
            </div>
          )}

          {/* PAGE 7: EVALUATION HISTORY */}
          {currentTab === 'recent' && (
            <div>
              <div style={{ marginBottom: '22px' }}>
                <h2 style={{ fontSize: '1.35rem', fontWeight: 700, color: 'var(--text-primary)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                  <History size={22} color="var(--brand-primary)" />
                  <span>Evaluation History & Forensic Logs</span>
                </h2>
                <p style={{ fontSize: '0.86rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Review past scan determinations, risk classifications, and verifiable evidence trails.
                </p>
              </div>

              <RecentAnalysesDrawer
                recentList={recentAnalyses}
                onSelectAnalysis={(res) => {
                  setCurrentAnalysis(res);
                  setSelectedDemoId(res.demo_scenario_id || null);
                  setTranscript(res.raw_transcript || '');
                  setCurrentTab('results');
                }}
                activeId={currentAnalysis?.id}
                isRetainingHistory={preferences.saveHistoryLocally}
              />
            </div>
          )}

          {/* PAGE 8: SETTINGS & PRIVACY */}
          {currentTab === 'settings' && (
            <div>
              <SettingsView
                preferences={preferences}
                onUpdatePreferences={updatePreferences}
                onClearLocalHistory={handleClearLocalHistory}
                localHistoryCount={recentAnalyses.filter((r) => !r.is_demo).length}
              />
            </div>
          )}
        </main>

        {/* Accessible Clinical Footer */}
        <footer
          style={{
            backgroundColor: 'var(--bg-surface)',
            borderTop: '1px solid var(--border-subtle)',
            padding: '20px 24px',
            color: 'var(--text-secondary)',
            fontSize: '0.82rem',
            marginTop: 'auto',
          }}
        >
          <div
            style={{
              maxWidth: '1240px',
              margin: '0 auto',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              flexWrap: 'wrap',
              gap: '14px',
            }}
          >
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ fontWeight: 700, color: 'var(--brand-primary)' }}>ElderShield</span>
              <span>• Hack With Vizag 4.0 (HWV4-PS05)</span>
            </div>
            <div>
              Multi-Vector Scam Intervention • English • हिन्दी • తెలుగు • Multilingual
            </div>
            <div>
              National Cybercrime Helpline: <a href="tel:1930" style={{ color: 'var(--risk-high)', fontWeight: 700 }}>1930</a>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
};

export default App;
