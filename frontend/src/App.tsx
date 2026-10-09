import React, { useState, useEffect } from 'react';
import { Header } from './components/Header';
import type { NavTab } from './components/Header';
import { DashboardOverview } from './components/DashboardOverview';
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
  analyzeConversation,
  analyzeProgression,
} from './api';
import type { DemoScenario, RiskAssessment, UserPreferences, ProgressionResponse } from './types';
import { playRiskAlert } from './utils/audioAlert';
import { AlertCircle, ArrowLeft } from 'lucide-react';

const PREFS_STORAGE_KEY = 'eldershield_user_prefs_v1';
const HISTORY_STORAGE_KEY = 'eldershield_local_history_v1';

export const App: React.FC = () => {
  // Navigation tab state
  const [currentTab, setCurrentTab] = useState<NavTab>('dashboard');

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
      saveHistoryLocally: false, // Privacy default: session only
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
        // storage quota
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

  // Initial data loading
  useEffect(() => {
    async function init() {
      try {
        const [scenariosData, backendRecent] = await Promise.all([
          fetchDemoScenarios(),
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
              [...parsed, ...backendRecent].forEach(item => map.set(item.id, item));
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
        setErrorMsg('Unable to connect to ElderShield detection service. Ensure the FastAPI backend is running on port 8000.');
      }
    }
    init();
  }, [preferences.saveHistoryLocally]);

  // Persist to local storage if user preference enabled
  const saveToLocalHistoryIfEnabled = (newAssessment: RiskAssessment) => {
    if (!preferences.saveHistoryLocally) return;
    try {
      const existing = localStorage.getItem(HISTORY_STORAGE_KEY);
      const parsed: RiskAssessment[] = existing ? JSON.parse(existing) : [];
      const updated = [newAssessment, ...parsed.filter(p => p.id !== newAssessment.id)].slice(0, 30);
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
    setRecentAnalyses(prev => prev.filter(p => p.is_demo));
  };

  // Run demo scenario
  const handleSelectScenario = async (sc: DemoScenario) => {
    setSelectedDemoId(sc.id);
    setTranscript(sc.raw_transcript);
    setErrorMsg(null);
    setIsLoading(true);

    try {
      // Execute both analyze and progression endpoints concurrently
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

      // Switch to results tab
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

      // Switch to results tab
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
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Header with Navigation for all 6 required pages */}
      <Header
        currentTab={currentTab}
        onSelectTab={setCurrentTab}
        hasActiveResult={Boolean(currentAnalysis)}
      />

      {/* Main Content Area */}
      <main style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '28px 24px',
        flex: 1,
        width: '100%',
      }}>
        {/* Error notification banner if any */}
        {errorMsg && (
          <div style={{
            display: 'flex',
            alignItems: 'center',
            gap: '10px',
            padding: '14px 18px',
            backgroundColor: 'rgba(239, 68, 68, 0.15)',
            border: '1.5px solid #ef4444',
            borderRadius: 'var(--radius-md)',
            color: '#fca5a5',
            marginBottom: '24px',
          }}>
            <AlertCircle size={20} color="#ef4444" />
            <span style={{ fontSize: '0.92rem', fontWeight: 600 }}>{errorMsg}</span>
          </div>
        )}

        {/* PAGE 1: DASHBOARD */}
        {currentTab === 'dashboard' && (
          <div>
            <DashboardOverview
              recentAnalyses={recentAnalyses}
              onStartNewAnalysis={() => setCurrentTab('analyze')}
              onExploreScenarios={() => {
                const el = document.getElementById('demo-scenarios-section');
                el?.scrollIntoView({ behavior: 'smooth' });
              }}
            />

            <div id="demo-scenarios-section">
              <DemoScenarioSelector
                scenarios={scenarios}
                selectedScenarioId={selectedDemoId}
                onSelectScenario={handleSelectScenario}
                isLoading={isLoading}
              />
            </div>

            {currentAnalysis && (
              <div style={{ marginTop: '24px' }}>
                <div style={{ fontSize: '0.85rem', fontWeight: 700, textTransform: 'uppercase', color: 'var(--accent-cyan)', marginBottom: '10px' }}>
                  Latest Analysis Overview
                </div>
                <RiskOverviewCard result={currentAnalysis} />
              </div>
            )}

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

        {/* PAGE 2: ANALYZE CONVERSATION */}
        {currentTab === 'analyze' && (
          <div>
            <div style={{ marginBottom: '20px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Analyze Conversation Transcript
              </h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Paste or type any suspicious conversation to evaluate multi-vector behavioral fraud indicators.
              </p>
            </div>

            <DemoScenarioSelector
              scenarios={scenarios}
              selectedScenarioId={selectedDemoId}
              onSelectScenario={handleSelectScenario}
              isLoading={isLoading}
            />

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
        )}

        {/* PAGE 3: RISK RESULTS */}
        {currentTab === 'results' && currentAnalysis && (
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '20px',
              flexWrap: 'wrap',
              gap: '10px',
            }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Detailed Risk Assessment & Evidence Ledger
                </h2>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Scan #{currentAnalysis.id} • Decision: <strong>{currentAnalysis.decision}</strong> • {currentAnalysis.timestamp}
                </p>
              </div>

              <button
                onClick={() => setCurrentTab('analyze')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-secondary)',
                  fontSize: '0.86rem',
                }}
              >
                <ArrowLeft size={15} />
                <span>Analyze Another Conversation</span>
              </button>
            </div>

            {/* 1. Risk Overview Card with Score Semantics & Decision */}
            <RiskOverviewCard result={currentAnalysis} />

            {/* 2. Deterministic Evidence Ledger with exact phrases & turn numbers */}
            <EvidenceFindings evidence={currentAnalysis.evidence} />

            {/* 3. Actionable Senior Protection Recommendations & Report */}
            <ProtectionRecommendations result={currentAnalysis} />
          </div>
        )}

        {/* PAGE 4: CONVERSATION TIMELINE */}
        {currentTab === 'timeline' && currentAnalysis && (
          <div>
            <div style={{
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'space-between',
              marginBottom: '20px',
              flexWrap: 'wrap',
              gap: '10px',
            }}>
              <div>
                <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                  Incremental Turn-by-Turn Progression Timeline
                </h2>
                <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                  Shows incremental risk velocity calculated dynamically from actual backend evaluations (`/api/analyze/progression`).
                </p>
              </div>

              <button
                onClick={() => setCurrentTab('results')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px',
                  padding: '8px 14px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--bg-surface-elevated)',
                  border: '1px solid var(--border-subtle)',
                  color: 'var(--text-secondary)',
                  fontSize: '0.86rem',
                }}
              >
                <span>View Evidence Ledger</span>
              </button>
            </div>

            <ProgressiveTimeline progressions={activeProgression?.turns || currentAnalysis.turn_progression} />
          </div>
        )}

        {/* PAGE 5: RECENT ANALYSES */}
        {currentTab === 'recent' && (
          <div>
            <div style={{ marginBottom: '20px' }}>
              <h2 style={{ fontSize: '1.4rem', fontWeight: 700, color: 'var(--text-primary)' }}>
                Recent Conversation Evaluations
              </h2>
              <p style={{ fontSize: '0.9rem', color: 'var(--text-secondary)', marginTop: '4px' }}>
                Review past scan determinations, risk classifications, and evidence trails.
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

        {/* PAGE 6: SETTINGS */}
        {currentTab === 'settings' && (
          <div>
            <SettingsView
              preferences={preferences}
              onUpdatePreferences={updatePreferences}
              onClearLocalHistory={handleClearLocalHistory}
              localHistoryCount={recentAnalyses.filter(r => !r.is_demo).length}
            />
          </div>
        )}
      </main>

      {/* Accessible Footer */}
      <footer style={{
        backgroundColor: 'var(--bg-surface)',
        borderTop: '1px solid var(--border-subtle)',
        padding: '22px 24px',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.84rem',
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ color: 'var(--accent-cyan)' }}>ElderShield</span>
            <span>• Hack With Vizag 4.0 (HWV4-PS05)</span>
          </div>
          <div>
            Rule-Based Scam Detection • English • हिन्दी • తెలుగు • Multilingual
          </div>
          <div>
            National Cybercrime Helpline: <strong>1930</strong>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default App;
