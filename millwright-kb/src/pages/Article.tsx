import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'
import { formatDate, type Article, type FileRow } from '../lib/types'
import { Markdown } from '../components/Markdown'
import { FileList } from '../components/FileList'

export function ArticlePage() {
  const { slug } = useParams()
  const { user, isTeacher } = useAuth()
  const navigate = useNavigate()
  const [article, setArticle] = useState<Article | null | undefined>(undefined)
  const [files, setFiles] = useState<FileRow[]>([])
  const [bookmarked, setBookmarked] = useState(false)
  const [note, setNote] = useState('')
  const [msg, setMsg] = useState<string | null>(null)

  useEffect(() => {
    if (!slug) return
    setArticle(undefined)
    supabase.from('mw_articles')
      .select('*, category:mw_categories(*), author:mw_profiles!mw_articles_author_id_fkey(display_name)')
      .eq('slug', slug).maybeSingle()
      .then(async ({ data }) => {
        const a = (data as unknown as Article) ?? null
        setArticle(a)
        if (!a) return
        supabase.rpc('mw_bump_view', { article_slug: slug }).then(() => {})
        const { data: f } = await supabase.from('mw_files').select('*').eq('article_id', a.id).order('created_at')
        setFiles((f as FileRow[]) ?? [])
        if (user) {
          const { data: b } = await supabase.from('mw_bookmarks').select('article_id').eq('user_id', user.id).eq('article_id', a.id).maybeSingle()
          setBookmarked(!!b)
        }
      })
  }, [slug, user])

  async function toggleBookmark() {
    if (!user || !article) return
    if (bookmarked) await supabase.from('mw_bookmarks').delete().eq('user_id', user.id).eq('article_id', article.id)
    else await supabase.from('mw_bookmarks').insert({ user_id: user.id, article_id: article.id })
    setBookmarked(!bookmarked)
  }

  async function setStatus(status: Article['status']) {
    if (!article) return
    const { error } = await supabase.from('mw_articles').update({ status, review_note: note, reviewed_by: user?.id ?? null }).eq('id', article.id)
    if (error) { setMsg(error.message); return }
    setArticle({ ...article, status, review_note: note })
    setMsg(status === 'published' ? 'Published to everyone.' : 'Sent back to the author.')
  }

  async function remove() {
    if (!article || !confirm('Delete this article? This cannot be undone.')) return
    const { error } = await supabase.from('mw_articles').delete().eq('id', article.id)
    if (error) { setMsg(error.message); return }
    navigate('/')
  }

  if (article === undefined) return <p className="loading">Loading…</p>
  if (article === null) return <div className="empty">Article not found, or it is not published yet.</div>

  const canEdit = !!user && (user.id === article.author_id || isTeacher)

  return (
    <article>
      <div className="article-head">
        <div className="meta">
          {article.category && <Link to={`/category/${article.category.slug}`}>{article.category.icon} {article.category.name}</Link>}
          <span className={`badge ${article.kind}`}>{article.kind}</span>
          {article.status !== 'published' && <span className={`badge ${article.status}`}>{article.status}</span>}
          {article.group_id && <span className="badge">group only</span>}
        </div>
        <h1>{article.title}</h1>
        {article.summary && <p className="muted">{article.summary}</p>}
        <div className="meta">
          {article.manufacturer && <span><strong>{article.manufacturer}</strong>{article.model_numbers.length > 0 && <> · {article.model_numbers.join(', ')}</>}</span>}
          <span>By {article.author?.display_name ?? 'Millwright KB'}</span>
          <span>Updated {formatDate(article.updated_at)}</span>
          <span>{article.view_count} views</span>
        </div>
        <div className="article-actions">
          {user && <button type="button" className="btn small" onClick={toggleBookmark}>{bookmarked ? '★ Bookmarked' : '☆ Bookmark'}</button>}
          {canEdit && <Link to={`/contribute/${article.slug}`} className="btn small">Edit</Link>}
          {canEdit && <button type="button" className="btn small danger" onClick={remove}>Delete</button>}
          <button type="button" className="btn small" onClick={() => window.print()}>Print</button>
        </div>
      </div>

      {article.status === 'pending' && (
        <div className="notice warn">
          This submission is waiting for a teacher to review it. Only the author and teachers can see it.
          {isTeacher && (
            <div style={{ marginTop: 8 }}>
              <input type="text" placeholder="Note to the author (optional)" value={note} onChange={(e) => setNote(e.target.value)} style={{ width: '100%', padding: 8, marginBottom: 8 }} />
              <div className="btn-row">
                <button type="button" className="btn primary small" onClick={() => setStatus('published')}>Approve and publish</button>
                <button type="button" className="btn small" onClick={() => setStatus('rejected')}>Send back</button>
              </div>
            </div>
          )}
        </div>
      )}
      {article.status === 'rejected' && <div className="notice error">Sent back by a teacher{article.review_note ? `: ${article.review_note}` : '.'} Edit it and resubmit.</div>}
      {article.status === 'draft' && <div className="notice info">Draft. Only you can see it. Edit and submit when ready.</div>}
      {msg && <div className="notice ok">{msg}</div>}

      <Markdown source={article.body} />

      {article.tags.length > 0 && (
        <p style={{ marginTop: 14 }}>
          {article.tags.map((t) => <Link key={t} className="tag" to={`/search?q=${encodeURIComponent(t)}`}>{t}</Link>)}
        </p>
      )}
      {article.source && <p className="small muted"><strong>Source:</strong> {article.source}</p>}

      <FileList files={files} canDelete={canEdit} onDeleted={(id) => setFiles(files.filter((f) => f.id !== id))} />
    </article>
  )
}
