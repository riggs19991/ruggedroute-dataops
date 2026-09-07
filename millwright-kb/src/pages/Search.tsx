import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import type { Category, SearchHit } from '../lib/types'
import { ArticleCard } from '../components/ArticleCard'

export function Search() {
  const [params, setParams] = useSearchParams()
  const q = params.get('q') ?? ''
  const cat = params.get('cat') ?? ''
  const [hits, setHits] = useState<SearchHit[] | null>(null)
  const [cats, setCats] = useState<Category[]>([])
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    supabase.from('mw_categories').select('*').order('sort_order').then(({ data }) => setCats((data as Category[]) ?? []))
  }, [])

  useEffect(() => {
    if (!q.trim()) { setHits([]); return }
    let cancelled = false
    setHits(null); setError(null)
    supabase.rpc('mw_search', { q: q.trim(), cat: cat || null, lim: 40 }).then(({ data, error }) => {
      if (cancelled) return
      if (error) setError(error.message)
      setHits((data as SearchHit[]) ?? [])
    })
    return () => { cancelled = true }
  }, [q, cat])

  return (
    <>
      <div className="section-head">
        <h1>{q ? <>Results for “{q}”</> : 'Search'}</h1>
        <label className="small">
          Topic:{' '}
          <select value={cat} onChange={(e) => { const n = new URLSearchParams(params); if (e.target.value) n.set('cat', e.target.value); else n.delete('cat'); setParams(n) }}>
            <option value="">All topics</option>
            {cats.map((c) => <option key={c.slug} value={c.slug}>{c.name}</option>)}
          </select>
        </label>
      </div>
      {error && <div className="notice error">{error}</div>}
      {hits === null && <p className="loading">Searching…</p>}
      {hits && hits.length === 0 && q && (
        <div className="empty">
          Nothing matched. Try fewer words, a model number, or a different spelling.<br />
          Know the answer? <Link to={`/contribute?title=${encodeURIComponent(q)}`}>Write it up</Link> so the next student finds it.
        </div>
      )}
      {hits && hits.length > 0 && (
        <div className="list">
          {hits.map((h) => <ArticleCard key={h.id} item={h} />)}
        </div>
      )}
    </>
  )
}
