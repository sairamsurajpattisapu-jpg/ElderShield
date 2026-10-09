import React, { useState, useEffect, useRef } from 'react';
import { Header } from './components/Header';
import { DashboardOverview } from './components/DashboardOverview';
import { DemoScenarioSelector } from './components/DemoScenarioSelector';
import { AnalysisInput } from './components/AnalysisInput';
import { RiskOverviewCard } from './components/RiskOverviewCard';
import { ProgressiveTimeline } from './components/ProgressiveTimeline';
import { EvidenceFindings } from './components/EvidenceFindings';
import { ProtectionRecommendations } from './components/ProtectionRecommendations';
import { RecentAnalysesDrawer } from './components/RecentAnalysesDrawer';

import {
  fetchScenarios,
  fetchRecentAnalyses,
  analyzeTranscript,
} from './api';
import type { ScenarioMetadata, AnalysisResult } from './types';
import { playRiskAlert } from './utils/audioAlert';
import { AlertCircle, Shield } from 'lucide-react';

export const App: React.FC = () => {
  // Accessibility state
  const [fontSize, setFontSize] = useState<'normal' | 'large' | 'xlarge'>('normal');
  const [highContrast, setHighContrast] = useState<boolean>(false);
  const [soundEnabled, setSoundEnabled] = useState<boolean>(true);

  // Application data state
  const [scenarios, setScenarios] = useState<ScenarioMetadata[]>([]);
  const [recentAnalyses, setRecentAnalyses] = useState<AnalysisResult[]>([]);
  const [selectedDemoId, setSelectedDemoId] = useState<string | null>(null);
  const [transcript, setTranscript] = useState<string>('');
  const [currentAnalysis, setCurrentAnalysis] = useState<AnalysisResult | null>(null);
  
  // UI states
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [errorMsg, setErrorMsg] = useState<string | null>(null);

  const inputSectionRef = useRef<HTMLDivElement>(null);
  const resultsSectionRef = useRef<HTMLDivElement>(null);

  // Sync accessibility classes with DOM body
  useEffect(() => {
    document.body.className = '';
    if (fontSize === 'large') document.body.classList.add('font-large');
    if (fontSize === 'xlarge') document.body.classList.add('font-xlarge');
    if (highContrast) document.body.classList.add('high-contrast');
  }, [fontSize, highContrast]);

  // Initial data loading
  useEffect(() => {
    async function init() {
      try {
        const [scenariosData, recentData] = await Promise.all([
          fetchScenarios(),
          fetchRecentAnalyses(15),
        ]);
        setScenarios(scenariosData);
        setRecentAnalyses(recentData);
        
        // If there's already a recent analysis, display the top one
        if (recentData && recentData.length > 0) {
          setCurrentAnalysis(recentData[0]);
          setSelectedDemoId(recentData[0].demo_scenario_id || null);
          setTranscript(recentData[0].raw_transcript);
        }
      } catch (err) {
        console.error('Initialization error:', err);
        setErrorMsg('Unable to connect to ElderShield detection service. Ensure backend is running.');
      }
    }
    init();
  }, []);

  // Handle running demo scenario
  const handleSelectScenario = async (sc: ScenarioMetadata) => {
    setSelectedDemoId(sc.id);
    const formattedTranscript = sc.turns
      .map((t) => `${t.speaker}: ${t.text}`)
      .join('\n');
    setTranscript(formattedTranscript);
    setErrorMsg(null);

    setIsLoading(true);
    try {
      const result = await analyzeTranscript(formattedTranscript, sc.id);
      setCurrentAnalysis(result);
      
      // Update recent analyses list
      setRecentAnalyses((prev) => [result, ...prev.filter((r) => r.id !== result.id)]);

      // Audio feedback
      if (soundEnabled) {
        playRiskAlert(result.overall_risk_level);
      }

      // Smooth scroll to results
      setTimeout(() => {
        resultsSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    } catch (err: unknown) {
      const message = err instanceof Error ? err.message : 'Analysis failed';
      setErrorMsg(message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle custom transcript analysis
  const handleAnalyzeCustom = async () => {
    if (!transcript.trim()) return;
    setErrorMsg(null);
    setIsLoading(true);

    try {
      const result = await analyzeTranscript(transcript, selectedDemoId || undefined);
      setCurrentAnalysis(result);

      setRecentAnalyses((prev) => [result, ...prev.filter((r) => r.id !== result.id)]);

      if (soundEnabled) {
        playRiskAlert(result.overall_risk_level);
      }

      setTimeout(() => {
        resultsSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
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
    inputSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleStartNewAnalysis = () => {
    inputSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const currentDemo = scenarios.find((s) => s.id === selectedDemoId);

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
      {/* Accessible Header */}
      <Header
        fontSize={fontSize}
        setFontSize={setFontSize}
        highContrast={highContrast}
        setHighContrast={setHighContrast}
        soundEnabled={soundEnabled}
        setSoundEnabled={setSoundEnabled}
      />

      {/* Main Container */}
      <main style={{
        maxWidth: '1280px',
        margin: '0 auto',
        padding: '32px 24px',
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
            border: '1px solid #ef4444',
            borderRadius: 'var(--radius-md)',
            color: '#fca5a5',
            marginBottom: '24px',
          }}>
            <AlertCircle size={20} color="#ef4444" />
            <span style={{ fontSize: '0.92rem', fontWeight: 600 }}>{errorMsg}</span>
          </div>
        )}

        {/* Dashboard Overview Section */}
        <DashboardOverview
          recentAnalyses={recentAnalyses}
          onStartNewAnalysis={handleStartNewAnalysis}
        />

        {/* Benchmark Demo Scenarios */}
        <DemoScenarioSelector
          scenarios={scenarios}
          selectedScenarioId={selectedDemoId}
          onSelectScenario={handleSelectScenario}
          isLoading={isLoading}
        />

        {/* Conversation Transcript Input */}
        <div ref={inputSectionRef}>
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

        {/* Active Analysis Results Display */}
        {currentAnalysis && (
          <div ref={resultsSectionRef}>
            {/* 1. Overall Risk Banner & Score Semantics */}
            <RiskOverviewCard result={currentAnalysis} />

            {/* 2. Turn-by-Turn Progressive Risk Evolution Timeline */}
            <ProgressiveTimeline progressions={currentAnalysis.turn_progression} />

            {/* 3. Deterministic Evidence Ledger */}
            <EvidenceFindings findings={currentAnalysis.evidence_findings} />

            {/* 4. Actionable Senior Protection Recommendations */}
            <ProtectionRecommendations result={currentAnalysis} />
          </div>
        )}

        {/* Recent Analyses History Drawer */}
        <RecentAnalysesDrawer
          recentList={recentAnalyses}
          onSelectAnalysis={(res) => {
            setCurrentAnalysis(res);
            setSelectedDemoId(res.demo_scenario_id || null);
            setTranscript(res.raw_transcript);
            resultsSectionRef.current?.scrollIntoView({ behavior: 'smooth' });
          }}
          activeId={currentAnalysis?.id}
        />
      </main>

      {/* Footer */}
      <footer style={{
        backgroundColor: 'var(--bg-surface)',
        borderTop: '1px solid var(--border-subtle)',
        padding: '24px',
        textAlign: 'center',
        color: 'var(--text-muted)',
        fontSize: '0.84rem',
      }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto', display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Shield size={16} color="var(--accent-cyan)" />
            <span>ElderShield • Hack With Vizag 4.0 (HWV4-PS05)</span>
          </div>
          <div>
            Built for elderly fraud prevention • English • हिन्दी • తెలుగు • Multilingual
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
