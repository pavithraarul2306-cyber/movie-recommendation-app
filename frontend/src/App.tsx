import { useEffect, useState } from 'react'
import './App.css'
import { fetchRecommendations, fetchSuggestions } from './api'
import type { RecommendItem } from './api'

function App() {
	const [query, setQuery] = useState('')
	const [suggestions, setSuggestions] = useState<string[]>([])
	const [selected, setSelected] = useState<string>('')
	const [topK, setTopK] = useState<number>(5)
	const [recs, setRecs] = useState<RecommendItem[] | null>(null)
	const [loading, setLoading] = useState(false)
	const [error, setError] = useState<string>('')

	useEffect(() => {
		let active = true
		if (query.trim().length === 0) {
			setSuggestions([])
			return
		}
		const t = setTimeout(async () => {
			try {
				const s = await fetchSuggestions(query)
				if (active) setSuggestions(s)
			} catch (e) {
				if (active) setSuggestions([])
			}
		}, 200)
		return () => { active = false; clearTimeout(t) }
	}, [query])

	async function handleRecommend() {
		if (!selected) return
		setLoading(true)
		setError('')
		try {
			const r = await fetchRecommendations(selected, topK)
			setRecs(r)
		} catch (e: any) {
			setError(e?.message || 'Failed to fetch recommendations')
			setRecs(null)
		} finally {
			setLoading(false)
		}
	}

	return (
		<div style={{ maxWidth: 1000, margin: '0 auto', padding: 16 }}>
			<h1>🎬 Movie Recommender</h1>
			<p>Type a movie, pick one, and get similar recommendations.</p>
			<div style={{ display: 'flex', gap: 12, alignItems: 'center', flexWrap: 'wrap' }}>
				<input
					type="text"
					placeholder="e.g., Toy Story (1995)"
					value={query}
					onChange={(e) => setQuery(e.target.value)}
					style={{ flex: '1 1 320px', padding: 8 }}
				/>
				<select value={selected} onChange={(e) => setSelected(e.target.value)} style={{ padding: 8, minWidth: 280 }}>
					<option value="">Select a movie</option>
					{suggestions.map((s) => (
						<option key={s} value={s}>{s}</option>
					))}
				</select>
				<label>Top K:</label>
				<input type="number" min={1} max={15} value={topK} onChange={(e) => setTopK(parseInt(e.target.value || '5', 10))} style={{ width: 80, padding: 6 }} />
				<button onClick={handleRecommend} disabled={!selected || loading} style={{ padding: '8px 12px' }}>
					{loading ? 'Loading…' : 'Recommend'}
				</button>
			</div>
			{error && <div style={{ color: 'red', marginTop: 8 }}>{error}</div>}
			{recs && recs.length > 0 && (
				<div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: 16, marginTop: 24 }}>
					{recs.map((r) => (
						<div key={r.title} style={{ border: '1px solid #eee', borderRadius: 8, padding: 12 }}>
							<div style={{ fontWeight: 600 }}>{r.title}</div>
							<div style={{ color: '#666', fontSize: 12 }}>{r.genres || ''}</div>
							<div style={{ marginTop: 8, fontSize: 12 }}>Similarity: {r.score.toFixed(2)}</div>
						</div>
					))}
				</div>
			)}
		</div>
	)
}

export default App
