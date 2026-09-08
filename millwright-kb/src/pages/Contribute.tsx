import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams, useSearchParams } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'
import { uploadFile } from '../lib/files'
import { FilePicker } from '../components/FilePicker'
import { KINDS, type Article, type ArticleKind, type Category, type FileRow, type Group } from '../lib/types'
import { FileList } from '../components/FileList'
import { Markdown } from '../components/Markdown'

function slugify(title: string): string {
  const base = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '').slice(0, 60)
  return `${base || 'article'}-${Math.random().toString(36).slice(2, 6)}`
}
const splitList = (s: string) => s.split(',').map((x) => x.trim()).filter(Boolean)

const TEMPLATE = `## What you need

-

## Steps

1.
2.
3.

## Values / settings

| Item | Value |
|---|---|
|  |  |

## Common mistakes

-
`

export function Contribute() {
  const { slug } = useParams()
  const [params] = useSearchParams()
  const { user } = useAuth()
  const navigate = useNavigate()

  const [cats, setCats] = useState<Category[]>([])
  const [groups, setGroups] = useState<Group[]>([])
  const [existing, setExisting] = useState<Article | null>(null)
  const [files, setFiles] = useState<FileRow[]>([])
  const [newFiles, setNewFiles] = useState<File[]>([])

  const [title, setTitle] = useState(params.get('title') ?? '')
  const [category, setCategory] = useState('')
  const [kind, setKind] = useState<ArticleKind>('procedure')
  const [summary, setSummary] = useState('')
  const [body, setBody] = useState(TEMPLATE)
  const [tags, setTags] = useState('')
  const [manufacturer, setManufacturer] = useState('')
  const [models, setModels] = useState('')
  const [source, setSource] = useState('')
  const [shareWith, setShareWith] = useState<string>(params.get('group') ?? '')
  const [agreed, setAgreed] = useState(false)
  const [preview, setPreview] = useState(false)
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    supabase.from('mw_categories').select('*').order('sort_order').then(({ data }) => {
      const list = (data as Category[]) ?? []
      setCats(list)
      const wanted = params.get('category')
      const found = wanted ? list.find((c) => c.slug === wanted) : undefined
      if (found && !slug) setCategory(found.id)
    })
    supabase.from('mw_groups').select('*').order('name').then(({ data }) => setGroups((data as Group[]) ?? []))
  }, [params, slug])

  useEffect(() => {
    if (!slug) return
    supabase.from('mw_articles').select('*').eq('slug', slug).maybeSingle().then(async ({ data }) => {
      const a = data as Article | null
      if (!a) { setError('Article not found or you cannot edit it.'); return }
      setExisting(a)
      setTitle(a.title); setCategory(a.category_id ?? ''); setKind(a.kind); setSummary(a.summary); setBody(a.body)
      setTags(a.tags.join(', ')); setManufacturer(a.manufacturer); setModels(a.model_numbers.join(', ')); setSource(a.source)
      setShareWith(a.group_id ?? ''); setAgreed(true)
      const { data: f } = await supabase.from('mw_files').select('*').eq('article_id', a.id)
      setFiles((f as FileRow[]) ?? [])
    })
  }, [slug])

  async function submit(e: FormEvent, asDraft = false) {
    e.preventDefault()
    if (!user) return
    if (!title.trim() || !body.trim()) { setError('Title and body are required.'); return }
    if (!asDraft && !agreed) { setError('Please confirm the contribution statement before publishing.'); return }
    setBusy(true); setError(null)
    try {
      const status: Article['status'] = asDraft ? 'draft' : 'published'
      const row = {
        title: title.trim(),
        summary: summary.trim(),
        body,
        kind,
        category_id: category || null,
        tags: splitList(tags),
        manufacturer: manufacturer.trim(),
        model_numbers: splitList(models),
        source: source.trim(),
        group_id: shareWith || null,
        status,
      }
      let articleId = existing?.id
      let articleSlug = existing?.slug
      if (existing) {
        const { error } = await supabase.from('mw_articles').update(row).eq('id', existing.id)
        if (error) throw error
      } else {
        articleSlug = slugify(title)
        const { data, error } = await supabase.from('mw_articles').insert({ ...row, slug: articleSlug, author_id: user.id }).select('id').single()
        if (error) throw error
        articleId = (data as { id: string }).id
      }
      for (const f of newFiles) {
        const meta = await uploadFile(user.id, f)
        const { error } = await supabase.from('mw_files').insert({ ...meta, article_id: articleId })
        if (error) throw error
      }
      navigate(`/article/${articleSlug}`)
    } catch (err) {
      setError((err as Error).message)
    } finally { setBusy(false) }
  }

  if (slug && !existing && !error) return <p className="loading">Loading…</p>

  return (
    <>
      <h1>{existing ? 'Edit article' : 'Contribute to the knowledge base'}</h1>
      {!existing && (
        <p className="muted">
          Write a procedure, a chart, a tip, or attach a manufacturer manual. It goes live as soon as you publish, marked as a community contribution, and other millwrights can upvote it.{' '}
          <Link to="/article/how-to-add-a-manual">How to add a manual →</Link>
        </p>
      )}
      {error && <div className="notice error">{error}</div>}

      <form className="form" onSubmit={(e) => submit(e)}>
        <div className="field">
          <label>Title</label>
          <input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="e.g. Dodge Torque-Arm II TA4207H - installation manual" required />
        </div>
        <div className="row cols-2">
          <div className="field">
            <label>Topic</label>
            <select value={category} onChange={(e) => setCategory(e.target.value)} required>
              <option value="">Choose a topic…</option>
              {cats.map((c) => <option key={c.id} value={c.id}>{c.icon} {c.name}</option>)}
            </select>
          </div>
          <div className="field">
            <label>Kind</label>
            <select value={kind} onChange={(e) => setKind(e.target.value as ArticleKind)}>
              {KINDS.map((k) => <option key={k.value} value={k.value}>{k.label}</option>)}
            </select>
          </div>
        </div>
        <div className="field">
          <label>Summary</label>
          <textarea value={summary} onChange={(e) => setSummary(e.target.value)} style={{ minHeight: 70 }} placeholder="One or two sentences. Shows in search results." />
        </div>
        <div className="row cols-2">
          <div className="field">
            <label>Manufacturer</label>
            <input type="text" value={manufacturer} onChange={(e) => setManufacturer(e.target.value)} placeholder="Dodge, SKF, Victor…" />
          </div>
          <div className="field">
            <label>Model numbers</label>
            <input type="text" value={models} onChange={(e) => setModels(e.target.value)} placeholder="TA4207H, TXT415 (comma separated)" />
            <div className="hint">Exactly as on the nameplate. Search matches these exactly.</div>
          </div>
        </div>
        <div className="field">
          <label>Tags</label>
          <input type="text" value={tags} onChange={(e) => setTags(e.target.value)} placeholder="shaft mount reducer, bushing torque, oil quantity (comma separated)" />
        </div>
        <div className="field">
          <div className="tabs" style={{ marginBottom: 8 }}>
            <button type="button" className={!preview ? 'active' : ''} onClick={() => setPreview(false)}>Write</button>
            <button type="button" className={preview ? 'active' : ''} onClick={() => setPreview(true)}>Preview</button>
          </div>
          {preview
            ? <Markdown source={body} />
            : <textarea className="body" value={body} onChange={(e) => setBody(e.target.value)} required />}
          <div className="hint">
            Markdown. <code>## Heading</code>, <code>1.</code> numbered steps, <code>| a | b |</code> tables, <code>**bold**</code>. Link to other articles with <code>[text](/article/slug)</code>.
          </div>
        </div>
        <div className="field">
          <label>Source</label>
          <input type="text" value={source} onChange={(e) => setSource(e.target.value)} placeholder="Where this came from: manual number, URL, instructor, own experience" />
        </div>
        <FilePicker files={newFiles} onChange={setNewFiles} />
        <FileList files={files} canDelete onDeleted={(id) => setFiles(files.filter((f) => f.id !== id))} />
        <div className="row cols-2">
          <div className="field">
            <label>Share with</label>
            <select value={shareWith} onChange={(e) => setShareWith(e.target.value)}>
              <option value="">Everyone (public knowledge base)</option>
              {groups.map((g) => <option key={g.id} value={g.id}>Only my group: {g.name}</option>)}
            </select>
            <div className="hint">Group-only articles are visible to that group right away.</div>
          </div>
        </div>
        <div className="field disclaimer-check">
          <label style={{ fontWeight: 400 }}>
            <input type="checkbox" checked={agreed} onChange={(e) => setAgreed(e.target.checked)} />{' '}
            I confirm this is my own work or properly credited, is accurate to the best of my knowledge, and I understand that readers will verify it against the manufacturer's manual and their site rules before relying on it. Contributions are not reviewed before they appear.
          </label>
        </div>
        <div className="btn-row">
          <button type="submit" className="btn primary" disabled={busy}>{busy ? 'Saving…' : existing ? 'Save changes' : shareWith ? 'Share with group' : 'Publish'}</button>
          <button type="button" className="btn" disabled={busy} onClick={(e) => submit(e, true)}>Save as draft</button>
          {existing && <Link to={`/article/${existing.slug}`} className="btn">Cancel</Link>}
        </div>
      </form>
    </>
  )
}
