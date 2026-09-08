import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import type { Article, Category } from '../lib/types'
import { SearchBox } from '../components/SearchBox'
import { ArticleCard } from '../components/ArticleCard'
import { InstallPrompt } from '../components/InstallPrompt'

const EXAMPLES = ['7018 amperage', 'MIG settings 1/4 plate', 'TIG aluminum', 'plasma cut chart', 'bearing heater', 'laser alignment', 'grease compatibility', 'belt tracking', 'sling capacity', 'megger test', 'tap drill', 'Victor tip chart']

type Lite = Pick<Article, 'slug' | 'title' | 'summary' | 'kind' | 'tags' | 'manufacturer' | 'view_count' | 'created_at'> & { category: Pick<Category, 'name'> | null }

export function Home() {
  const [cats, setCats] = useState<Category[]>([])
  const [counts, setCounts] = useState<Record<string, number>>({})
  const [popular, setPopular] = useState<Lite[]>([])
  const [recent, setRecent] = useState<Lite[]>([])

  useEffect(() => {
    supabase.from('mw_categories').select('*').order('sort_order').then(({ data }) => setCats((data as Category[]) ?? []))
    supabase.from('mw_articles').select('category_id').eq('status', 'published').is('group_id', null).then(({ data }) => {
      const c: Record<string, number> = {}
      for (const r of (data as { category_id: string | null }[]) ?? []) if (r.category_id) c[r.category_id] = (c[r.category_id] ?? 0) + 1
      setCounts(c)
    })
    const sel = 'slug, title, summary, kind, tags, manufacturer, view_count, created_at, category:mw_categories(name)'
    supabase.from('mw_articles').select(sel).eq('status', 'published').is('group_id', null).order('view_count', { ascending: false }).limit(5)
      .then(({ data }) => setPopular((data as unknown as Lite[]) ?? []))
    supabase.from('mw_articles').select(sel).eq('status', 'published').is('group_id', null).order('created_at', { ascending: false }).limit(5)
      .then(({ data }) => setRecent((data as unknown as Lite[]) ?? []))
  }, [])

  return (
    <>
      <section className="hero">
        <h1>Millwright Knowledge Base</h1>
        <p>Procedures, charts and manuals for the trade: welding and cutting setup, alignment, bearings, drives, hydraulics, rigging, installation, troubleshooting and safety. Search it, use it in the shop, add what is missing.</p>
        <SearchBox big autoFocus />
        <div className="chips">
          {EXAMPLES.map((e) => <Link key={e} className="chip" to={`/search?q=${encodeURIComponent(e)}`}>{e}</Link>)}
        </div>
        <p className="hero-links">
          <Link to="/article/set-me-up-for-a-task">Set me up for a task</Link> · <Link to="/a-z">A-Z index of every article</Link>
        </p>
      </section>

      <InstallPrompt />

      <section className="section">
        <div className="section-head"><h2>Browse by topic</h2></div>
        <div className="grid">
          {cats.map((c) => (
            <Link key={c.id} to={`/category/${c.slug}`} className="card cat-card">
              <div className="icon">{c.icon}</div>
              <h3>{c.name}</h3>
              <p className="desc">{c.description}</p>
              <div className="count">{counts[c.id] ?? 0} article{(counts[c.id] ?? 0) === 1 ? '' : 's'}</div>
            </Link>
          ))}
        </div>
      </section>

      <section className="section two-col">
        <div>
          <div className="section-head"><h2>Most used</h2></div>
          <div className="list">
            {popular.map((a) => <ArticleCard key={a.slug} item={{ ...a, category_name: a.category?.name }} />)}
          </div>
        </div>
        <div>
          <div className="section-head"><h2>Recently added</h2><Link to="/contribute" className="small">Add yours →</Link></div>
          <div className="list">
            {recent.map((a) => <ArticleCard key={a.slug} item={{ ...a, category_name: a.category?.name }} />)}
          </div>
        </div>
      </section>
    </>
  )
}
