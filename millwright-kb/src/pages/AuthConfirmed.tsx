import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { supabase } from '../lib/supabase'
import { isStandalone } from '../lib/pwa'

/** Landing page for the email confirmation and magic links. supabase-js reads the session from the URL. */
export function AuthConfirmed() {
  const [state, setState] = useState<'checking' | 'signed-in' | 'confirmed' | 'error'>('checking')
  const [detail, setDetail] = useState('')

  useEffect(() => {
    const hash = new URLSearchParams(window.location.hash.replace(/^#/, ''))
    const err = hash.get('error_description') || new URLSearchParams(window.location.search).get('error_description')
    if (err) { setState('error'); setDetail(err); return }
    let tries = 0
    const check = async () => {
      const { data } = await supabase.auth.getSession()
      if (data.session) { setState('signed-in'); return }
      if (++tries < 6) setTimeout(check, 500); else setState('confirmed')
    }
    check()
  }, [])

  const standalone = isStandalone()
  return (
    <div className="form narrow">
      {state === 'checking' && <p className="loading">Checking your link…</p>}
      {state === 'error' && <div className="notice error">This link did not work: {detail}. Links expire after a while. Go back to the app and request a new one, or sign in with your password.</div>}
      {(state === 'signed-in' || state === 'confirmed') && (
        <>
          <div className="notice ok">Your email is confirmed{state === 'signed-in' ? ' and you are signed in here' : ''}.</div>
          {!standalone && (
            <p>If you installed <b>Millwright KB</b> on your home screen, open it from the icon and sign in there with your <b>email and password</b>. The installed app and this browser keep separate sign-ins.</p>
          )}
          <p><Link to="/" className="btn primary">Continue</Link></p>
        </>
      )}
    </div>
  )
}
