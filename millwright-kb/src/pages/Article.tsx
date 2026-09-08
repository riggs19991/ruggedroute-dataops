import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'
import { formatDate, type Article, type FileRow } from '../lib/types'
import { Markdown } from '../components/Markdown'
import { FileList } from '../components/FileList'
import { SupportAsk } from '../components/SupportAsk'

export function ArticlePage() {
  const { slug } = useParams()
  const { user, isAdmin } = useAuth()
  const navigate = useNavigate()
  const [article, setArticle] = useState<Article | null | undefined>(undefined)
  const [files, setFiles] = useState<FileRow[]>([])
  const [bookmarked, setBookmarked] = useState(false)
  const [voted, setVoted] = useState(false)
  const [votes, setVotes] = useState(0)
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
        setVotes(a.upvotes ?? 0)
        setVoted(false)
        supabase.rpc('mw_bump_view', { article_slug: slug }).then(() => {})
        const { data: f } = await supabase.from('mw_files').select('*').eq('article_id', a.id).order('created_at')
        setFiles((f as FileRow[]) ?? [])
        if (user) {
          const { data: b } = await supabase.from('mw_bookmarks').select('article_id').eq('user_id', user.id).eq('article_id', a.id).maybeSingle()
          setBookmarked(!!b)
          const { data: v } = await supabase.from('mw_votes').select('article_id').eq('user_id', user.id).eq('article_id', a.id).maybeSingle()
          setVoted(!!v)
        }
      })
  }, [slug, user])

  async function toggleBookmark() {
    if (!user || !article) return
    if (bookmarked) await supabase.from('mw_bookmarks').delete().eq('user_id', user.id).eq('article_id', article.id)
    else await supabase.from('mw_bookmarks').insert({ user_id: user.id, article_id: article.id })
    setBookmarked(!bookmarked)
  }

  async function toggleVote() {
    if (!user || !article) return
    if (voted) {
      const { error } = await supabase.from('mw_votes').delete().eq('user_id', user.id).eq('article_id', article.id)
      if (error) { setMsg(error.message); return }
      setVoted(false); setVotes(Math.max(0, votes - 1))
    } else {
      const { error } = await supabase.from('mw_votes').insert({ user_id: user.id, article_id: article.id })
      if (error) { setMsg(error.message); return }
      setVoted(true); setVotes(votes + 1)
    }
  }

  async function remove() {
    if (!article || !confirm('Delete this article? This cannot be undone.')) return
    const { error } = await supabase.from('mw_articles').delete().eq('id', article.id)
    if (error) { setMsg(error.message); return }
    navigate('/')
  }

  if (article === undefined) return <p className="loading">Loading…</p>
  if (article === null) return <div className="empty">Article not found, or it is not published yet.</div>

  const canEdit = !!user && (user.id === article.author_id || isAdmin)
  const community = !!article.author_id

  return (
    <article>
      <div className="article-head">
        <div className="meta">
          {article.category && <Link to={`/category/${article.category.slug}`}>{article.category.icon} {article.category.name}</Link>}
          <span className={`badge ${article.kind}`}>{article.kind}</span>
          {article.status !== 'published' && <span className={`badge ${article.status}`}>{article.status}</span>}
          {community && <span className="badge community">community</span>}
          {article.group_id && <span className="badge">group only</span>}
        </div>
        <h1>{article.title}</h1>
        {article.summary && <p className="muted">{article.summary}</p>}
        <div className="meta">
          {article.manufacturer && <span><strong>{article.manufacturer}</strong>{article.model_numbers.length > 0 && <> · {article.model_numbers.join(', ')}</>}</span>}
          <span>By {article.author?.display_name ?? 'Millwright KB'}</span>
          <span>Updated {formatDate(article.updated_at)}</span>
          <span>{article.view_count} views</span>
          <span>▲ {votes} upvote{votes === 1 ? '' : 's'}</span>
        </div>
        <div className="article-actions">
          {user
            ? <button type="button" className={`btn small vote-btn${voted ? ' active' : ''}`} onClick={toggleVote} title={voted ? 'Remove your upvote' : 'Well done and useful? Upvote it'}>{voted ? '▲ Upvoted' : '▲ Upvote'} {votes}</button>
            : <Link to="/signin" className="btn small vote-btn" title="Sign in to upvote">▲ {votes}</Link>}
          {user && <button type="button" className="btn small" onClick={toggleBookmark}>{bookmarked ? '★ Bookmarked' : '☆ Bookmark'}</button>}
          {canEdit && <Link to={`/contribute/${article.slug}`} className="btn small">Edit</Link>}
          {canEdit && <button type="button" className="btn small danger" onClick={remove}>Delete</button>}
          <button type="button" className="btn small" onClick={() => window.print()}>Print</button>
        </div>
      </div>

      {article.status === 'draft' && <div className="notice info">Draft. Only you can see it. Edit and publish when ready.</div>}
      {community && article.status === 'published' && (
        <div className="disclaimer">
          <strong>Community contribution</strong> by {article.author?.display_name ?? 'a member'}, {formatDate(article.created_at)}.
          It has not been reviewed by the app. Verify it against the manufacturer's manual and your site rules before relying on it, and upvote it if it helped you.
        </div>
      )}
      {msg && <div className="notice ok">{msg}</div>}

      <Markdown source={article.body} />

      {article.tags.length > 0 && (
        <p style={{ marginTop: 14 }}>
          {article.tags.map((t) => <Link key={t} className="tag" to={`/search?q=${encodeURIComponent(t)}`}>{t}</Link>)}
        </p>
      )}
      {article.source && <p className="small muted"><strong>Source:</strong> {article.source}</p>}

      <FileList files={files} canDelete={canEdit} onDeleted={(id) => setFiles(files.filter((f) => f.id !== id))} />

      <SupportAsk />
    </article>
  )
}
