import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import type { Article, Category } from '../lib/types'
import { ArticleCard } from '../components/ArticleCard'

type Lite = Pick<Article, 'slug' | 'title' | 'summary' | 'kind' | 'tags' | 'manufacturer'>

export function CategoryPage() {
  const { slug } = useParams()
  const [cat, setCat] = useState<Category | null | undefined>(undefined)
  const [items, setItems] = useState<Lite[]>([])

  useEffect(() => {
    if (!slug) return
    supabase.from('mw_categories').select('*').eq('slug', slug).maybeSingle().then(async ({ data }) => {
      setCat((data as Category) ?? null)
      if (!data) return
      const { data: rows } = await supabase.from('mw_articles')
        .select('slug, title, summary, kind, tags, manufacturer')
        .eq('category_id', (data as Category).id).eq('status', 'published').is('group_id', null).order('title')
      setItems((rows as Lite[]) ?? [])
    })
  }, [slug])

  if (cat === undefined) return <p className="loading">Loading…</p>
  if (cat === null) return <div className="empty">No such topic.</div>

  return (
    <>
      <div className="section-head">
        <h1>{cat.icon} {cat.name}</h1>
        <Link to={`/contribute?category=${cat.slug}`} className="btn small">+ Add to this topic</Link>
      </div>
      <p className="muted">{cat.description}</p>
      {items.length === 0
        ? <div className="empty">No published articles here yet. <Link to={`/contribute?category=${cat.slug}`}>Be the first.</Link></div>
        : <div className="list">{items.map((a) => <ArticleCard key={a.slug} item={a} />)}</div>}
    </>
  )
}
