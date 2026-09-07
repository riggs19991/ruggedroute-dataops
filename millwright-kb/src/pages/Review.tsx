import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { formatDate, type Article, type Category } from '../lib/types'
import { ArticleCard } from '../components/ArticleCard'

type Row = Pick<Article, 'id' | 'slug' | 'title' | 'summary' | 'kind' | 'tags' | 'manufacturer' | 'status' | 'created_at'> & {
  category: Pick<Category, 'name'> | null
  author: { display_name: string } | null
}

export function Review() {
  const [status, setStatus] = useState<'pending' | 'rejected' | 'draft'>('pending')
  const [rows, setRows] = useState<Row[] | null>(null)

  useEffect(() => {
    setRows(null)
    supabase.from('mw_articles')
      .select('id, slug, title, summary, kind, tags, manufacturer, status, created_at, category:mw_categories(name), author:mw_profiles!mw_articles_author_id_fkey(display_name)')
      .eq('status', status).is('group_id', null).order('created_at')
      .then(({ data }) => setRows((data as unknown as Row[]) ?? []))
  }, [status])

  return (
    <>
      <h1>Review submissions</h1>
      <p className="muted">Open a submission to read it, then approve or send it back from the article page. Check the numbers against a manual before you publish.</p>
      <div className="tabs">
        <button type="button" className={status === 'pending' ? 'active' : ''} onClick={() => setStatus('pending')}>Waiting for review</button>
        <button type="button" className={status === 'rejected' ? 'active' : ''} onClick={() => setStatus('rejected')}>Sent back</button>
      </div>
      {rows === null ? <p className="loading">Loading…</p> : rows.length === 0 ? <div className="empty">Nothing here. Nice.</div> : (
        <div className="list">
          {rows.map((r) => (
            <div key={r.id}>
              <ArticleCard item={{ ...r, category_name: r.category?.name }} />
              <div className="small muted" style={{ padding: '2px 4px 6px' }}>Submitted by {r.author?.display_name ?? 'unknown'} on {formatDate(r.created_at)}</div>
            </div>
          ))}
        </div>
      )}
    </>
  )
}
