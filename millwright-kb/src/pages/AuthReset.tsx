import { useEffect, useState, type FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { supabase } from '../lib/supabase'

/** Landing page for the password-reset email: the link signs the user in, then they set a new password. */
export function AuthReset() {
  const navigate = useNavigate()
  const [ready, setReady] = useState(false)
  const [password, setPassword] = useState('')
  const [msg, setMsg] = useState<{ kind: 'ok' | 'error'; text: string } | null>(null)
  const [busy, setBusy] = useState(false)

  useEffect(() => {
    let tries = 0
    const check = async () => {
      const { data } = await supabase.auth.getSession()
      if (data.session) { setReady(true); return }
      if (++tries < 8) setTimeout(check, 500); else setMsg({ kind: 'error', text: 'This reset link has expired or was already used. Request a new one from the sign-in page.' })
    }
    check()
  }, [])

  async function submit(e: FormEvent) {
    e.preventDefault(); setBusy(true); setMsg(null)
    const { error } = await supabase.auth.updateUser({ password })
    setBusy(false)
    if (error) { setMsg({ kind: 'error', text: error.message }); return }
    setMsg({ kind: 'ok', text: 'Password changed. You are signed in.' })
    setTimeout(() => navigate('/'), 1200)
  }

  return (
    <form className="form narrow" onSubmit={submit}>
      <h1>Set a new password</h1>
      {msg && <div className={`notice ${msg.kind}`}>{msg.text}</div>}
      <div className="field"><label>New password</label><input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required minLength={6} autoComplete="new-password" disabled={!ready} /></div>
      <button type="submit" className="btn primary" disabled={!ready || busy}>{busy ? 'Saving…' : 'Save password'}</button>
    </form>
  )
}
