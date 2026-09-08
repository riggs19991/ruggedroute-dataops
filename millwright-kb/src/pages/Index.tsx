import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import type { ArticleKind } from '../lib/types'

type Row = {
  slug: string
  title: string
  kind: ArticleKind
  tags: string[] | null
  category: { name: string; slug: string; icon: string | null; sort_order: number } | null
}

type Group = { name: string; slug: string; icon: string; items: Row[] }

export function IndexPage() {
  const [rows, setRows] = useState<Row[] | null>(null)
  const [q, setQ] = useState('')

  useEffect(() => {
    supabase.from('mw_articles')
      .select('slug, title, kind, tags, category:mw_categories(name, slug, icon, sort_order)')
      .eq('status', 'published').is('group_id', null).order('title').limit(2000)
      .then(({ data }) => setRows((data as unknown as Row[]) ?? []))
  }, [])

  const groups = useMemo<Group[]>(() => {
    if (!rows) return []
    const needle = q.trim().toLowerCase()
    const map = new Map<string, Group & { sort: number }>()
    for (const r of rows) {
      if (needle && !r.title.toLowerCase().includes(needle) && !(r.tags ?? []).some((t) => t.toLowerCase().includes(needle))) continue
      const c = r.category
      const key = c?.slug ?? 'other'
      if (!map.has(key)) map.set(key, { name: c?.name ?? 'Other', slug: key, icon: c?.icon ?? '📄', sort: c?.sort_order ?? 999, items: [] })
      map.get(key)!.items.push(r)
    }
    return [...map.values()].sort((a, b) => a.sort - b.sort || a.name.localeCompare(b.name))
  }, [rows, q])

  const total = rows?.length ?? 0
  const shown = groups.reduce((n, g) => n + g.items.length, 0)

  return (
    <>
      <div className="section-head">
        <h1>A-Z index</h1>
        <Link to="/article/set-me-up-for-a-task" className="btn small">Set me up for a task →</Link>
      </div>
      <p className="muted">Every published article by topic. {rows ? `${shown} of ${total} shown.` : ''}</p>
      <input
        className="index-filter"
        type="search"
        placeholder="Filter titles and tags (e.g. 7018, grease, plasma)"
        value={q}
        onChange={(e) => setQ(e.target.value)}
        aria-label="Filter the index"
      />
      {rows === null ? <p className="loading">Loading…</p> : (
        <>
          <div className="chips index-jump">
            {groups.map((g) => <a key={g.slug} className="chip" href={`#idx-${g.slug}`}>{g.icon} {g.name} ({g.items.length})</a>)}
          </div>
          {groups.map((g) => (
            <section key={g.slug} id={`idx-${g.slug}`} className="index-group">
              <h2><Link to={`/category/${g.slug}`}>{g.icon} {g.name}</Link></h2>
              <ul>
                {g.items.map((a) => (
                  <li key={a.slug}><Link to={`/article/${a.slug}`}>{a.title}</Link> <span className={`kind kind-${a.kind}`}>{a.kind}</span></li>
                ))}
              </ul>
            </section>
          ))}
          {groups.length === 0 && <div className="empty">Nothing matches. Try the <Link to={`/search?q=${encodeURIComponent(q)}`}>full-text search</Link>.</div>}
        </>
      )}
    </>
  )
}
