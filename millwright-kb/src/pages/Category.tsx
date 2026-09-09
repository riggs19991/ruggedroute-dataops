import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import type { Article, Category } from '../lib/types'
import { ArticleCard } from '../components/ArticleCard'
import { CategoryIcon, Icon } from '../lib/icons'

type Lite = Pick<Article, 'slug' | 'title' | 'summary' | 'kind' | 'tags' | 'manufacturer' | 'upvotes' | 'author_id' | 'view_count'>
type Sort = 'title' | 'views' | 'votes'

export function CategoryPage() {
  const { slug } = useParams()
  const [cat, setCat] = useState<Category | null | undefined>(undefined)
  const [items, setItems] = useState<Lite[]>([])
  const [sort, setSort] = useState<Sort>('title')

  useEffect(() => {
    if (!slug) return
    supabase.from('mw_categories').select('*').eq('slug', slug).maybeSingle().then(async ({ data }) => {
      setCat((data as Category) ?? null)
      if (!data) return
      const { data: rows } = await supabase.from('mw_articles')
        .select('slug, title, summary, kind, tags, manufacturer, upvotes, author_id, view_count')
        .eq('category_id', (data as Category).id).eq('status', 'published').is('group_id', null).order('title')
      setItems((rows as Lite[]) ?? [])
    })
  }, [slug])

  const sorted = [...items].sort((a, b) => sort === 'votes' ? (b.upvotes - a.upvotes) || a.title.localeCompare(b.title) : sort === 'views' ? (b.view_count - a.view_count) || a.title.localeCompare(b.title) : a.title.localeCompare(b.title))

  if (cat === undefined) return <p className="loading">Loading…</p>
  if (cat === null) return <div className="empty">No such topic.</div>

  return (
    <>
      <div className="page-head">
        <div className="tile" style={{ padding: 0 }}><div className="sq"><CategoryIcon slug={cat.slug} /></div></div>
        <h1 style={{ flex: 1 }}>{cat.name}</h1>
        <Link to={`/contribute?category=${cat.slug}`} className="btn primary small"><Icon name="plus" size={18} />Add</Link>
      </div>
      <p className="muted">{cat.description}</p>
      <div className="sort-row">
        <span>{items.length} article{items.length === 1 ? '' : 's'}</span>
        <span style={{ flex: 1 }} />
        {items.length > 1 && (
          <>
            <label htmlFor="sort">Sort</label>
            <select id="sort" value={sort} onChange={(e) => setSort(e.target.value as Sort)}>
              <option value="title">A to Z</option>
              <option value="views">Most used</option>
              <option value="votes">Top rated</option>
            </select>
          </>
        )}
      </div>
      {items.length === 0
        ? <div className="empty">No published articles here yet. <Link to={`/contribute?category=${cat.slug}`}>Be the first.</Link></div>
        : <div className="list">{sorted.map((a) => <ArticleCard key={a.slug} item={a} />)}</div>}
    </>
  )
}
