import { useState, type FormEvent } from 'react'
import { Navigate, useLocation } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'

type Mode = 'signin' | 'signup' | 'magic' | 'forgot'

const origin = () => window.location.origin + import.meta.env.BASE_URL.replace(/\/$/, '')

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
          options: { data: { display_name: name.trim(), school: school.trim() }, emailRedirectTo: origin() + '/auth/confirmed' },
        })
        if (error) throw error
        if (!data.session) {
          setMsg({ kind: 'info', text: `Account created. Now: 1) open the email we sent to ${email} and tap the link (it opens in your browser); 2) come back to this app; 3) sign in here with your password.` })
          setMode('signin')
        }
      } else if (mode === 'forgot') {
        const { error } = await supabase.auth.resetPasswordForEmail(email, { redirectTo: origin() + '/auth/reset' })
        if (error) throw error
        setMsg({ kind: 'ok', text: `Reset email sent to ${email}. Open the link, set a new password, then sign in here.` })
        setMode('signin')
      } else {
        const { error } = await supabase.auth.signInWithOtp({ email, options: { emailRedirectTo: origin() + '/auth/confirmed' } })
        if (error) throw error
        setMsg({ kind: 'ok', text: 'Link sent. It opens in your browser; if you use the installed app, come back here and sign in with your password.' })
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
      {mode === 'forgot' && <p className="hint small muted">Enter your email and we send a link to set a new password.</p>}
      {msg && <div className={`notice ${msg.kind}`}>{msg.text}</div>}
      {mode === 'signup' && (
        <>
          <div className="field"><label>Your name</label><input type="text" value={name} onChange={(e) => setName(e.target.value)} required placeholder="Shown on what you contribute" /></div>
          <div className="field"><label>School (optional)</label><input type="text" value={school} onChange={(e) => setSchool(e.target.value)} placeholder="e.g. Millwright School" /></div>
        </>
      )}
      <div className="field"><label>Email</label><input type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" /></div>
      {mode !== 'magic' && mode !== 'forgot' && (
        <div className="field"><label>Password</label><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} autoComplete={mode === 'signup' ? 'new-password' : 'current-password'} /></div>
      )}
      <button type="submit" className="btn primary" disabled={busy}>
        {busy ? 'Working…' : mode === 'signin' ? 'Sign in' : mode === 'signup' ? 'Create account' : mode === 'forgot' ? 'Send reset link' : 'Send link'}
      </button>
      {mode === 'signin' && <p className="hint small" style={{ marginTop: 10 }}><button type="button" className="linklike" onClick={() => { setMode('forgot'); setMsg(null) }}>Forgot password?</button></p>}
      <p className="hint small muted" style={{ marginTop: 12 }}>
        Students and teachers both start with a regular account. Teachers unlock the group and review tools with the teacher access code on their profile page.
        You can read everything without signing in; sign in to contribute, join a group, bookmark, or open attachments.
      </p>
    </form>
  )
}
