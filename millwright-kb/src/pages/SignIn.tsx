import { useState, type FormEvent } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'

type Mode = 'signin' | 'signup' | 'magic'

export function SignIn() {
  const { user } = useAuth()
  const location = useLocation()
  const from = (location.state as { from?: string } | null)?.from ?? '/'
  const [mode, setMode] = useState<Mode>('signin')
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [name, setName] = useState('')
  const [school, setSchool] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<{ kind: 'ok' | 'error' | 'info'; text: string } | null>(null)

  if (user) return <Navigate to={from} replace />

  async function submit(e: FormEvent) {
    e.preventDefault()
    setBusy(true); setMsg(null)
    try {
      if (mode === 'signin') {
        const { error } = await supabase.auth.signInWithPassword({ email, password })
        if (error) throw error
      } else if (mode === 'signup') {
        const { data, error } = await supabase.auth.signUp({
          email, password,
          options: { data: { display_name: name.trim(), school: school.trim() }, emailRedirectTo: window.location.origin + import.meta.env.BASE_URL },
        })
        if (error) throw error
        if (!data.session) setMsg({ kind: 'info', text: 'Account created. Open the confirmation email and tap its link (the page it opens may look blank). Then come back here and sign in with your password.' })
      } else {
        const { error } = await supabase.auth.signInWithOtp({ email, options: { emailRedirectTo: window.location.origin + import.meta.env.BASE_URL } })
        if (error) throw error
        setMsg({ kind: 'ok', text: 'Link sent. If the link does not bring you back to this app, return here and use your password instead.' })
      }
    } catch (err) {
      setMsg({ kind: 'error', text: (err as Error).message })
    } finally { setBusy(false) }
  }

  return (
    <form className="form narrow" onSubmit={submit}>
      <div className="tabs">
        <button type="button" className={mode === 'signin' ? 'active' : ''} onClick={() => setMode('signin')}>Sign in</button>
        <button type="button" className={mode === 'signup' ? 'active' : ''} onClick={() => setMode('signup')}>Create account</button>
        <button type="button" className={mode === 'magic' ? 'active' : ''} onClick={() => setMode('magic')}>Email link</button>
      </div>
      {msg && <div className={`notice ${msg.kind}`}>{msg.text}</div>}
      {mode === 'signup' && (
        <>
          <div className="field"><label>Your name</label><input type="text" value={name} onChange={(e) => setName(e.target.value)} required placeholder="Shown on what you contribute" /></div>
          <div className="field"><label>School (optional)</label><input type="text" value={school} onChange={(e) => setSchool(e.target.value)} placeholder="e.g. Millwright School" /></div>
        </>
      )}
      <div className="field"><label>Email</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" /></div>
      {mode !== 'magic' && (
        <div className="field"><label>Password</label><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} /></div>
      )}
      <button type="submit" className="btn primary" disabled={busy}>
        {busy ? 'Working…' : mode === 'signin' ? 'Sign in' : mode === 'signup' ? 'Create account' : 'Send link'}
      </button>
      <p className="hint small muted" style={{ marginTop: 12 }}>
        Students and teachers both start with a regular account. Teachers unlock the group and review tools with the teacher access code on their profile page.
        You can read everything without signing in; sign in to contribute, join a group, bookmark, or open attachments.
      </p>
    </form>
  )
}
