import { useCallback, useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'
import { uploadFile } from '../lib/files'
import { currentWeek, formatDate, type FileRow, type Group, type GroupPost, type Profile } from '../lib/types'
import { Markdown } from '../components/Markdown'
import { FileList } from '../components/FileList'
import { ArticlePicker, type PickedArticle } from '../components/ArticlePicker'

interface Member { user_id: string; joined_at: string; profile: Pick<Profile, 'display_name' | 'school'> | null }

export function GroupPage() {
  const { id } = useParams()
  const { user } = useAuth()
  const navigate = useNavigate()
  const [group, setGroup] = useState<Group | null | undefined>(undefined)
  const [posts, setPosts] = useState<GroupPost[]>([])
  const [members, setMembers] = useState<Member[]>([])
  const [showMembers, setShowMembers] = useState(false)
  const [msg, setMsg] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null)

  // new post form
  const [week, setWeek] = useState(1)
  const [title, setTitle] = useState('')
  const [body, setBody] = useState('')
  const [picked, setPicked] = useState<PickedArticle | null>(null)
  const [newFiles, setNewFiles] = useState<File[]>([])
  const [busy, setBusy] = useState(false)
  const [showForm, setShowForm] = useState(false)

  const isTeacher = !!group && group.teacher_id === user?.id
  const thisWeek = currentWeek(group?.term_start ?? null)

  const load = useCallback(async () => {
    if (!id) return
    const { data: g } = await supabase.from('mw_groups').select('*').eq('id', id).maybeSingle()
    setGroup((g as Group) ?? null)
    if (!g) return
    const { data: p } = await supabase.from('mw_group_posts')
      .select('*, article:mw_articles!mw_group_posts_article_id_fkey(slug, title), files:mw_files(*)')
      .eq('group_id', id).order('week_number', { ascending: false }).order('pinned', { ascending: false }).order('created_at', { ascending: false })
    setPosts((p as unknown as GroupPost[]) ?? [])
    const { data: m } = await supabase.from('mw_group_members').select('user_id, joined_at, profile:mw_profiles(display_name, school)').eq('group_id', id).order('joined_at')
    setMembers((m as unknown as Member[]) ?? [])
  }, [id])

  useEffect(() => { load() }, [load])
  useEffect(() => { if (thisWeek) setWeek(thisWeek) }, [thisWeek])

  async function createPost(e: FormEvent) {
    e.preventDefault()
    if (!group || !user) return
    setBusy(true); setMsg(null)
    try {
      const { data, error } = await supabase.from('mw_group_posts').insert({
        group_id: group.id, week_number: week, title: title.trim(), body, article_id: picked?.id ?? null, posted_by: user.id,
      }).select('id').single()
      if (error) throw error
      const postId = (data as { id: string }).id
      for (const f of newFiles) {
        const meta = await uploadFile(user.id, f)
        const { error: fe } = await supabase.from('mw_files').insert({ ...meta, group_post_id: postId })
        if (fe) throw fe
      }
      setTitle(''); setBody(''); setPicked(null); setNewFiles([]); setShowForm(false)
      await load()
      setMsg({ kind: 'ok', text: `Posted to week ${week}.` })
    } catch (err) { setMsg({ kind: 'error', text: (err as Error).message }) } finally { setBusy(false) }
  }

  async function deletePost(p: GroupPost) {
    if (!confirm(`Delete "${p.title}"?`)) return
    const { error } = await supabase.from('mw_group_posts').delete().eq('id', p.id)
    if (error) setMsg({ kind: 'error', text: error.message }); else load()
  }

  async function togglePin(p: GroupPost) {
    await supabase.from('mw_group_posts').update({ pinned: !p.pinned }).eq('id', p.id)
    load()
  }

  async function removeMember(m: Member) {
    if (!group || !confirm(`Remove ${m.profile?.display_name ?? 'this student'} from the group?`)) return
    await supabase.from('mw_group_members').delete().eq('group_id', group.id).eq('user_id', m.user_id)
    load()
  }

  async function leave() {
    if (!group || !user || !confirm('Leave this group?')) return
    await supabase.from('mw_group_members').delete().eq('group_id', group.id).eq('user_id', user.id)
    navigate('/groups')
  }

  async function deleteGroup() {
    if (!group || !confirm('Delete this group and all of its posts? This cannot be undone.')) return
    await supabase.from('mw_groups').delete().eq('id', group.id)
    navigate('/groups')
  }

  if (group === undefined) return <p className="loading">Loading…</p>
  if (group === null) return <div className="empty">Group not found, or you are not a member. <Link to="/groups">Join with a code.</Link></div>

  const weeks = Array.from(new Set(posts.map((p) => p.week_number))).sort((a, b) => b - a)

  return (
    <>
      <div className="group-head">
        <div>
          <h1 style={{ marginBottom: 2 }}>{group.name}</h1>
          <div className="muted small">{group.school}{group.term_start ? ` · term started ${formatDate(group.term_start)}` : ''}{thisWeek ? ` · week ${thisWeek}` : ''} · {members.length} student{members.length === 1 ? '' : 's'}</div>
        </div>
        {isTeacher ? (
          <div className="btn-row">
            <span className="small muted">Join code</span>
            <span className="join-code">{group.join_code}</span>
            <button type="button" className="btn small" onClick={() => navigator.clipboard?.writeText(group.join_code)}>Copy</button>
            <button type="button" className="btn small" onClick={() => setShowMembers(!showMembers)}>Students</button>
            <button type="button" className="btn small danger" onClick={deleteGroup}>Delete group</button>
          </div>
        ) : (
          <div className="btn-row">
            <Link to={`/contribute?group=${group.id}`} className="btn small">Share something with the group</Link>
            <button type="button" className="btn small" onClick={leave}>Leave group</button>
          </div>
        )}
      </div>
      {msg && <div className={`notice ${msg.kind}`}>{msg.text}</div>}

      {isTeacher && showMembers && (
        <div className="form" style={{ marginBottom: 16 }}>
          <h3>Students ({members.length})</h3>
          {members.length === 0 && <p className="muted small">Nobody yet. Share the join code <strong>{group.join_code}</strong>.</p>}
          {members.map((m) => (
            <div className="member" key={m.user_id}>
              <span>{m.profile?.display_name ?? 'Student'} <span className="muted small">{m.profile?.school} · joined {formatDate(m.joined_at)}</span></span>
              <button type="button" className="btn small danger" onClick={() => removeMember(m)}>Remove</button>
            </div>
          ))}
        </div>
      )}

      {isTeacher && (
        <div style={{ marginBottom: 16 }}>
          {!showForm ? (
            <button type="button" className="btn primary" onClick={() => setShowForm(true)}>+ Post to the group</button>
          ) : (
            <form className="form" onSubmit={createPost}>
              <h3>New post</h3>
              <div className="row cols-2">
                <div className="field"><label>Week</label><input type="number" min={1} max={60} value={week} onChange={(e) => setWeek(Number(e.target.value))} required /></div>
                <div className="field"><label>Title</label><input type="text" value={title} onChange={(e) => setTitle(e.target.value)} placeholder="Week 3: rim-and-face alignment lab" required /></div>
              </div>
              <div className="field"><label>Message (markdown)</label><textarea value={body} onChange={(e) => setBody(e.target.value)} placeholder="What to read, what to bring, what the lab covers…" /></div>
              <div className="field"><label>Link an article from the library</label><ArticlePicker value={picked} onChange={setPicked} /></div>
              <div className="field"><label>Attach files (handouts, slides, manuals)</label><input type="file" multiple onChange={(e) => setNewFiles(Array.from(e.target.files ?? []))} /></div>
              <div className="btn-row">
                <button type="submit" className="btn primary" disabled={busy}>{busy ? 'Posting…' : 'Post'}</button>
                <button type="button" className="btn" onClick={() => setShowForm(false)}>Cancel</button>
              </div>
            </form>
          )}
        </div>
      )}

      {posts.length === 0 && <div className="empty">{isTeacher ? 'No posts yet. Post this week\'s reading, handouts or lab sheet.' : 'Your teacher has not posted anything yet.'}</div>}

      {weeks.map((w) => (
        <section className="week" key={w}>
          <h2>Week {w} {thisWeek === w && <span className="now">this week</span>}</h2>
          {posts.filter((p) => p.week_number === w).map((p) => (
            <div className="card post" key={p.id}>
              <div className="title">{p.pinned && <span title="Pinned">📌</span>}{p.title}</div>
              {p.body && <Markdown source={p.body} />}
              {p.article && <p><Link to={`/article/${p.article.slug}`} className="btn small">📖 Read: {p.article.title}</Link></p>}
              <FileList files={(p.files ?? []) as FileRow[]} canDelete={isTeacher} onDeleted={() => load()} />
              <div className="foot">
                <span>{formatDate(p.created_at)}</span>
                {isTeacher && <button type="button" className="btn small" onClick={() => togglePin(p)}>{p.pinned ? 'Unpin' : 'Pin'}</button>}
                {isTeacher && <button type="button" className="btn small danger" onClick={() => deletePost(p)}>Delete</button>}
              </div>
            </div>
          ))}
        </section>
      ))}
    </>
  )
}
