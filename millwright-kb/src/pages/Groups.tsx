import { useEffect, useState, type FormEvent } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'
import { currentWeek, type Group } from '../lib/types'

export function Groups() {
  const { user } = useAuth()
  const navigate = useNavigate()
  const [groups, setGroups] = useState<Group[] | null>(null)
  const [code, setCode] = useState('')
  const [name, setName] = useState('')
  const [school, setSchool] = useState('')
  const [termStart, setTermStart] = useState('')
  const [msg, setMsg] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null)

  async function load() {
    const { data } = await supabase.from('mw_groups').select('*, teacher:mw_profiles!mw_groups_teacher_id_fkey(display_name)').order('created_at', { ascending: false })
    setGroups((data as unknown as Group[]) ?? [])
  }
  useEffect(() => { load() }, [])

  async function join(e: FormEvent) {
    e.preventDefault()
    const { data, error } = await supabase.rpc('mw_join_group', { code: code.trim() })
    if (error) { setMsg({ kind: 'error', text: error.message }); return }
    setCode('')
    navigate(`/groups/${(data as Group).id}`)
  }

  async function create(e: FormEvent) {
    e.preventDefault()
    if (!user) return
    const { data: jc, error: e1 } = await supabase.rpc('mw_new_join_code')
    if (e1) { setMsg({ kind: 'error', text: e1.message }); return }
    const { data, error } = await supabase.from('mw_groups').insert({
      name: name.trim(), school: school.trim(), teacher_id: user.id, join_code: jc as string, term_start: termStart || null,
    }).select('id').single()
    if (error) { setMsg({ kind: 'error', text: error.message }); return }
    navigate(`/groups/${(data as { id: string }).id}`)
  }

  return (
    <>
      <h1>Groups</h1>
      <p className="muted">A group is one class. Whoever creates it is the instructor: they post each week's material and share files, and students join with the code.</p>
      {msg && <div className={`notice ${msg.kind}`}>{msg.text}</div>}

      <div className="two-col">
        <form className="form" onSubmit={join}>
          <h3>Join a group</h3>
          <div className="field"><label>Join code from your instructor</label><input type="text" value={code} onChange={(e) => setCode(e.target.value.toUpperCase())} placeholder="e.g. K7M2PX" required style={{ fontFamily: 'var(--mono)', letterSpacing: '0.1em' }} /></div>
          <button type="submit" className="btn primary">Join</button>
        </form>
        <form className="form" onSubmit={create}>
            <h3>Create a group</h3>
            <p className="small muted">You will be its instructor. No code needed: just share the join code with your class.</p>
            <div className="field"><label>Group name</label><input type="text" value={name} onChange={(e) => setName(e.target.value)} placeholder="Millwright Level 2 - Fall 2026" required /></div>
            <div className="row cols-2">
              <div className="field"><label>School</label><input type="text" value={school} onChange={(e) => setSchool(e.target.value)} /></div>
              <div className="field"><label>First day of term</label><input type="date" value={termStart} onChange={(e) => setTermStart(e.target.value)} /><div className="hint">Used to show which week you are on.</div></div>
            </div>
            <button type="submit" className="btn primary">Create group</button>
          </form>
      </div>

      <section className="section">
        <div className="section-head"><h2>Your groups</h2></div>
        {groups === null ? <p className="loading">Loading…</p> : groups.length === 0 ? (
          <div className="empty">You are not in a group yet. Ask your instructor for the join code, or create a group for your class above.</div>
        ) : (
          <div className="grid">
            {groups.map((g) => {
              const wk = currentWeek(g.term_start)
              return (
                <Link key={g.id} to={`/groups/${g.id}`} className="card">
                  <h3>{g.name}</h3>
                  <p className="desc">{g.school}{g.school && g.teacher ? ' · ' : ''}{g.teacher?.display_name}</p>
                  <p className="desc">{wk ? `Week ${wk}` : 'No term dates set'}{g.teacher_id === user?.id ? ' · you teach this group' : ''}</p>
                </Link>
              )
            })}
          </div>
        )}
      </section>
    </>
  )
}
