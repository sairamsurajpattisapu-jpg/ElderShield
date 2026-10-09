import type { RiskAssessment, ProgressionResponse, DemoScenario, AudioAnalysisResponse } from './types';

// Support VITE_API_BASE_URL environment variable, falling back to empty string for relative proxy
const API_BASE = import.meta.env.VITE_API_BASE_URL || '';

export async function fetchHealth(): Promise<{ status: string; service: string; analysis_method: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Health check failed: ElderShield backend unreachable');
  return res.json();
}

export async function fetchDemoScenarios(): Promise<DemoScenario[]> {
  const res = await fetch(`${API_BASE}/api/demo-scenarios`);
  if (!res.ok) throw new Error('Failed to fetch benchmark demo scenarios');
  return res.json();
}

export async function analyzeConversation(
  transcript?: string,
  demoScenarioId?: string
): Promise<RiskAssessment> {
  const res = await fetch(`${API_BASE}/api/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      transcript: transcript || undefined,
      demo_scenario_id: demoScenarioId || undefined,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail || 'ElderShield detection engine returned an error');
  }
  return res.json();
}

export async function analyzeProgression(
  transcript?: string,
  demoScenarioId?: string
): Promise<ProgressionResponse> {
  const res = await fetch(`${API_BASE}/api/analyze/progression`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      transcript: transcript || undefined,
      demo_scenario_id: demoScenarioId || undefined,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Progression analysis failed' }));
    throw new Error(err.detail || 'ElderShield progression service returned an error');
  }
  return res.json();
}

export async function analyzeAudioFile(
  file: File | Blob,
  languageHint = 'auto'
): Promise<AudioAnalysisResponse> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('language_hint', languageHint);

  const res = await fetch(`${API_BASE}/api/analyze/audio`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Audio speech recognition failed' }));
    throw new Error(err.detail || 'ElderShield audio analysis failed');
  }
  return res.json();
}

export function getLiveCallWsUrl(): string {
  if (API_BASE) {
    try {
      const url = new URL(API_BASE);
      const wsProto = url.protocol === 'https:' ? 'wss:' : 'ws:';
      return `${wsProto}//${url.host}/ws/live-call`;
    } catch {
      // fallback
    }
  }
  const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
  return `${protocol}//${window.location.host}/ws/live-call`;
}

export async function fetchRecentAnalyses(limit = 15): Promise<RiskAssessment[]> {
  const res = await fetch(`${API_BASE}/api/recent?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to retrieve recent session evaluations');
  return res.json();
}
