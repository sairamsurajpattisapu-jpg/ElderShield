import type { AnalysisResult, ScenarioMetadata } from './types';

const API_BASE = '/api';

export async function fetchHealth(): Promise<{ status: string; service: string }> {
  const res = await fetch(`${API_BASE}/health`);
  if (!res.ok) throw new Error('Failed to reach backend health endpoint');
  return res.json();
}

export async function fetchScenarios(): Promise<ScenarioMetadata[]> {
  const res = await fetch(`${API_BASE}/scenarios`);
  if (!res.ok) throw new Error('Failed to fetch demo scenarios');
  return res.json();
}

export async function fetchRecentAnalyses(limit = 10): Promise<AnalysisResult[]> {
  const res = await fetch(`${API_BASE}/recent?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch recent analyses');
  return res.json();
}

export async function analyzeTranscript(
  transcript: string,
  demoScenarioId?: string
): Promise<AnalysisResult> {
  const res = await fetch(`${API_BASE}/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      transcript: transcript || undefined,
      demo_scenario_id: demoScenarioId || undefined,
    }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: 'Analysis failed' }));
    throw new Error(err.detail || 'Analysis service returned an error');
  }
  return res.json();
}
