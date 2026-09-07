import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import type { SearchHit } from '../lib/types'

export interface PickedArticle { id: string; slug: string; title: string }

/** Type-ahead search that returns an article id, used when attaching an article to a group post. */
export function ArticlePicker({ value, onChange }: { value: PickedArticle | null; onChange: (a: PickedArticle | null) => void }) {
  const [q, setQ] = useState('')
  const [hits, setHits] = useState<SearchHit[]>([])
  const [open, setOpen] = useState(false)

  useEffect(() => {
    const query = q.trim()
    if (query.length < 2) { setHits([]); return }
    const t = setTimeout(async () => {
      const { data } = await supabase.rpc('mw_search', { q: query, cat: null, lim: 8 })
      setHits((data as SearchHit[]) ?? [])
      setOpen(true)
    }, 250)
    return () => clearTimeout(t)
  }, [q])

  if (value) {
    return (
      <div className="btn-row">
        <span>📎 <strong>{value.title}</strong></span>
        <button type="button" className="btn small" onClick={() => onChange(null)}>Change</button>
      </div>
    )
  }

  return (
    <div className="picker">
      <input type="text" value={q} onChange={(e) => setQ(e.target.value)} onFocus={() => hits.length && setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)} placeholder="Type to search articles…" />
      {open && hits.length > 0 && (
        <div className="options">
          {hits.map((h) => (
            <button type="button" key={h.id} onMouseDown={() => { onChange({ id: h.id, slug: h.slug, title: h.title }); setQ('') }}>
              {h.title} <span className="muted small">· {h.category_name}</span>
            </button>
          ))}
        </div>
      )}
    </div>
  )
}
