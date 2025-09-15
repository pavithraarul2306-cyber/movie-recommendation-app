export type SuggestResponse = { suggestions: string[] };
export type RecommendItem = {
  title: string;
  year?: number | null;
  genres?: string | null;
  score: number;
};
export type RecommendResponse = { recommendations: RecommendItem[] };

const BASE = (import.meta.env.VITE_API_BASE as string | undefined) || 'http://localhost:5000';

export async function fetchSuggestions(q: string): Promise<string[]> {
  const url = `${BASE}/api/suggestions?q=${encodeURIComponent(q)}&limit=20`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch suggestions');
  const data: SuggestResponse = await res.json();
  return data.suggestions || [];
}

export async function fetchRecommendations(title: string, topK = 5): Promise<RecommendItem[]> {
  const url = `${BASE}/api/recommend?title=${encodeURIComponent(title)}&top_k=${topK}`;
  const res = await fetch(url);
  if (!res.ok) throw new Error('Failed to fetch recommendations');
  const data: RecommendResponse = await res.json();
  return data.recommendations || [];
}
