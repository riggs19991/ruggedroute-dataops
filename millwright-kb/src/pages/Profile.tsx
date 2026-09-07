import { useEffect, useState, type FormEvent } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'
import type { Article } from '../lib/types'
import { ArticleCard } from '../components/ArticleCard'

type Lite = Pick<Article, 'slug' | 'title' | 'summary' | 'kind' | 'tags' | 'manufacturer' | 'status'>

export function ProfilePage() {
  const { user, profile, isTeacher, refreshProfile } = useAuth()
  const [name, setName] = useState(profile?.display_name ?? '')
  const [school, setSchool] = useState(profile?.school ?? '')
  const [code, setCode] = useState('')
  const [msg, setMsg] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null)
  const [mine, setMine] = useState<Lite[]>([])
  const [bookmarks, setBookmarks] = useState<Lite[]>([])

  useEffect(() => { setName(profile?.display_name ?? ''); setSchool(profile?.school ?? '') }, [profile])

  useEffect(() => {
    if (!user) return
    supabase.from('mw_articles').select('slug, title, summary, kind, tags, manufacturer, status').eq('author_id', user.id).order('updated_at', { ascending: false })
      .then(({ data }) => setMine((data as Lite[]) ?? []))
    supabase.from('mw_bookmarks').select('article:mw_articles(slug, title, summary, kind, tags, manufacturer, status)').eq('user_id', user.id).order('created_at', { ascending: false })
      .then(({ data }) => setBookmarks(((data as unknown as { article: Lite | null }[]) ?? []).map((r) => r.article).filter((a): a is Lite => !!a)))
  }, [user])

  async function save(e: FormEvent) {
    e.preventDefault()
    if (!user) return
    const { error } = await supabase.from('mw_profiles').update({ display_name: name.trim(), school: school.trim() }).eq('id', user.id)
    setMsg(error ? { kind: 'error', text: error.message } : { kind: 'ok', text: 'Saved.' })
    await refreshProfile()
  }

  async function becomeTeacher(e: FormEvent) {
    e.preventDefault()
    const { error } = await supabase.rpc('mw_become_teacher', { code })
    if (error) { setMsg({ kind: 'error', text: error.message }); return }
    setMsg({ kind: 'ok', text: 'You are now a teacher. Group and review tools are unlocked.' })
    setCode('')
    await refreshProfile()
  }

  return (
    <>
      <h1>Your profile</h1>
      {msg && <div className={`notice ${msg.kind}`}>{msg.text}</div>}
      <div className="two-col">
        <form className="form" onSubmit={save}>
          <div className="field"><label>Display name</label><input type="text" value={name} onChange={(e) => setName(e.target.value)} required /></div>
          <div className="field"><label>School</label><input type="text" value={school} onChange={(e) => setSchool(e.target.value)} /></div>
          <div className="field"><label>Email</label><input type="text" value={user?.email ?? ''} readOnly /></div>
          <div className="field"><label>Role</label><input type="text" value={isTeacher ? 'Teacher' : 'Student'} readOnly /></div>
          <button type="submit" className="btn primary">Save</button>
        </form>
        {!isTeacher ? (
          <form className="form" onSubmit={becomeTeacher}>
            <h3>Are you an instructor?</h3>
            <p className="small muted">Enter the teacher access code from the app administrator to unlock groups, weekly sharing and submission review.</p>
            <div className="field"><label>Teacher access code</label><input type="text" value={code} onChange={(e) => setCode(e.target.value)} required /></div>
            <button type="submit" className="btn">Unlock teacher tools</button>
          </form>
        ) : (
          <div className="form">
            <h3>Teacher tools</h3>
            <ul>
              <li><Link to="/groups">Create a group</Link> and give students the join code.</li>
              <li>Post each week's material to the group feed.</li>
              <li><Link to="/review">Review student submissions</Link> before they go public.</li>
              <li>Edit or delete any article.</li>
            </ul>
          </div>
        )}
      </div>

      <section className="section">
        <div className="section-head"><h2>Your contributions</h2><Link to="/contribute" className="btn small">+ New</Link></div>
        {mine.length === 0 ? <div className="empty">Nothing yet. Found something the library is missing? <Link to="/contribute">Write it up.</Link></div>
          : <div className="list">{mine.map((a) => <ArticleCard key={a.slug} item={a} />)}</div>}
      </section>
      <section className="section">
        <div className="section-head"><h2>Bookmarks</h2></div>
        {bookmarks.length === 0 ? <div className="empty">Bookmark articles you use a lot and they show up here.</div>
          : <div className="list">{bookmarks.map((a) => <ArticleCard key={a.slug} item={a} />)}</div>}
      </section>
    </>
  )
}
