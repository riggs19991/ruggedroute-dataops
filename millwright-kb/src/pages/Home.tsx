import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import type { Article, Category } from '../lib/types'
import { SearchBox } from '../components/SearchBox'
import { ArticleCard } from '../components/ArticleCard'
import { InstallPrompt } from '../components/InstallPrompt'
import { CategoryIcon } from '../lib/icons'

const EXAMPLES = ['7018 amps', 'MIG settings 1/4 plate', 'TIG aluminum', 'plasma cut chart', 'laser alignment', 'grease compatibility', 'belt tracking', 'sling capacity', 'Victor tip chart']

type Lite = Pick<Article, 'slug' | 'title' | 'summary' | 'kind' | 'tags' | 'manufacturer' | 'view_count' | 'upvotes' | 'author_id' | 'created_at'> & { category: Pick<Category, 'name'> | null }

export function Home() {
  const [cats, setCats] = useState<Category[]>([])
  const [counts, setCounts] = useState<Record<string, number>>({})
  const [popular, setPopular] = useState<Lite[]>([])
  const [recent, setRecent] = useState<Lite[]>([])
  const [top, setTop] = useState<Lite[]>([])
  const [showAll, setShowAll] = useState(false)

  useEffect(() => {
    supabase.from('mw_categories').select('*').order('sort_order').then(({ data }) => setCats((data as Category[]) ?? []))
    supabase.from('mw_articles').select('category_id').eq('status', 'published').is('group_id', null).then(({ data }) => {
      const c: Record<string, number> = {}
      for (const r of (data as { category_id: string | null }[]) ?? []) if (r.category_id) c[r.category_id] = (c[r.category_id] ?? 0) + 1
      setCounts(c)
    })
    const sel = 'slug, title, summary, kind, tags, manufacturer, view_count, upvotes, author_id, created_at, category:mw_categories(name)'
    supabase.from('mw_articles').select(sel).eq('status', 'published').is('group_id', null).order('view_count', { ascending: false }).limit(4)
      .then(({ data }) => setPopular((data as unknown as Lite[]) ?? []))
    supabase.from('mw_articles').select(sel).eq('status', 'published').is('group_id', null).order('created_at', { ascending: false }).limit(4)
      .then(({ data }) => setRecent((data as unknown as Lite[]) ?? []))
    supabase.from('mw_articles').select(sel).eq('status', 'published').is('group_id', null).not('author_id', 'is', null).gt('upvotes', 0).order('upvotes', { ascending: false }).limit(4)
      .then(({ data }) => setTop((data as unknown as Lite[]) ?? []))
  }, [])

  const total = Object.values(counts).reduce((a, b) => a + b, 0)

  return (
    <>
      <section className="hero">
        <div className="inner">
          <h1>The trade's reference, in your pocket.</h1>
          <p>Welding and cutting setup, alignment, bearings, drives, hydraulics, rigging and safety. {total ? `${total} articles` : 'Hundreds of articles'}, every one with a diagram. Works offline.</p>
          <SearchBox big autoFocus />
          <div className="chips">
            {EXAMPLES.map((e) => <Link key={e} className="chip" to={`/search?q=${encodeURIComponent(e)}`}>{e}</Link>)}
          </div>
          <div className="hero-links">
            <Link to="/article/set-me-up-for-a-task">Set me up for a task</Link>
            <Link to="/a-z">A-Z index</Link>
            <Link to="/support">Support the creator</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="section-head"><h2>Browse by topic</h2><Link to="/a-z">All {cats.length || 25} topics</Link></div>
        <div className="grid">
          {(showAll ? cats : cats.slice(0, 9)).map((c) => (
            <Link key={c.id} to={`/category/${c.slug}`} className="card tile">
              <div className="sq"><CategoryIcon slug={c.slug} size={22} /></div>
              <h3>{c.name}</h3>
              <p className="desc">{c.description}</p>
              <div className="count">{counts[c.id] ?? 0} article{(counts[c.id] ?? 0) === 1 ? '' : 's'}</div>
            </Link>
          ))}
          {!showAll && cats.length > 9 && (
            <button type="button" className="card tile more" onClick={() => setShowAll(true)}>Show all {cats.length} topics</button>
          )}
        </div>
      </section>

      <InstallPrompt />

      <section className="section three-col">
        <div>
          <div className="section-head"><h2>Most used</h2></div>
          <div className="list">
            {popular.map((a) => <ArticleCard key={a.slug} item={{ ...a, category_name: a.category?.name }} />)}
          </div>
        </div>
        <div>
          <div className="section-head"><h2>Recently added</h2><Link to="/contribute">Add yours</Link></div>
          <div className="list">
            {recent.map((a) => <ArticleCard key={a.slug} item={{ ...a, category_name: a.category?.name }} />)}
          </div>
        </div>
        <div>
          <div className="section-head"><h2>Top rated by the community</h2><Link to="/contribute">Share what you know</Link></div>
          {top.length === 0
            ? <div className="empty">Nothing upvoted yet. Member contributions appear here once other millwrights upvote them.</div>
            : <div className="list">{top.map((a) => <ArticleCard key={a.slug} item={{ ...a, category_name: a.category?.name }} />)}</div>}
        </div>
      </section>
    </>
  )
}
