import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { useAuth } from '../lib/auth'
import { postJson } from '../lib/api'
import { checkDisplayName, NAME_MAX } from '../lib/moderation'
import { DonorWall, money } from '../components/DonorWall'

type Donation = { id: string; amount_cents: number; currency: string; display_mode: string; display_name: string; created_at: string }
type Mode = 'anonymous' | 'name' | 'business' | 'profile'
const SESSION_KEY = 'mw-donation-session'

/** Landing page after Stripe Checkout: confirm the payment, then let the donor choose how to appear. */
export function SupportThanksPage() {
  const [params] = useSearchParams()
  const { profile } = useAuth()
  const sessionId = useMemo(() => {
    const fromUrl = params.get('session_id')
    if (fromUrl) { try { localStorage.setItem(SESSION_KEY, fromUrl) } catch { /* private mode */ } return fromUrl }
    try { return localStorage.getItem(SESSION_KEY) } catch { return null }
  }, [params])
  const [donation, setDonation] = useState<Donation | null>(null)
  const [state, setState] = useState<'loading' | 'ready' | 'unpaid' | 'error'>('loading')
  const [mode, setMode] = useState<Mode>('anonymous')
  const [name, setName] = useState('')
  const [saving, setSaving] = useState(false)
  const [saved, setSaved] = useState<string | null>(null)
  const [refresh, setRefresh] = useState(0)

  useEffect(() => {
    if (!sessionId) { setState('error'); return }
    postJson<Donation>('/api/donate/confirm', { session_id: sessionId }).then((r) => {
      if (r.ok && r.data) {
        setDonation(r.data); setState('ready')
        setMode((r.data.display_mode as Mode) || 'anonymous')
        if (r.data.display_mode !== 'anonymous') setName(r.data.display_name)
      } else setState(r.status === 402 ? 'unpaid' : 'error')
    })
  }, [sessionId])

  const profileName = profile?.display_name?.trim() || ''
  const effectiveName = mode === 'profile' ? profileName : name
  const check = mode === 'anonymous' ? null : checkDisplayName(effectiveName)
  const canSave = mode === 'anonymous' || (check?.ok ?? false)

  const save = async () => {
    if (!sessionId || !canSave) return
    setSaving(true); setSaved(null)
    const r = await postJson<Donation & { reason?: string }>('/api/donate/display', { session_id: sessionId, mode, name: effectiveName })
    setSaving(false)
    if (r.ok && r.data) { setDonation(r.data); setSaved('Saved. Thank you again!'); setRefresh((n) => n + 1) }
    else setSaved(r.error === 'name' ? 'That name was not accepted. Try another, or stay anonymous.' : 'Could not save right now. Your donation went through; try again in a minute.')
  }

  return (
    <div style={{ maxWidth: 720 }}>
      <div className="page-head"><span className="glyph big" aria-hidden="true">🎉</span><h1>Thank you</h1></div>
      {state === 'loading' && <p className="loading">Confirming your donation with Stripe…</p>}
      {state === 'unpaid' && <div className="notice warn">Stripe has not confirmed this payment yet. If you completed it, reload this page in a minute.</div>}
      {state === 'error' && <div className="notice info">We could not find a donation to confirm. If you just donated, open the link Stripe sent you back to, or reload. <Link to="/support">Back to Support</Link></div>}
      {state === 'ready' && donation && (
        <>
          <p>Your <b>{money(donation.amount_cents, donation.currency)}</b> donation is confirmed. It keeps Millwright KB free, ad-free and growing.</p>
          <div className="card donate-box">
            <h2 style={{ margin: 0, fontSize: '1.1rem' }}>How should you appear on the supporters wall?</h2>
            <div className="choice-list" role="radiogroup" aria-label="Display as">
              {([['anonymous', 'Anonymous', 'shown as "Anonymous"'], ['name', 'My name', 'the name you type'], ['business', 'My business', 'a company or shop name'], ['profile', 'My profile name', profileName ? `"${profileName}" from your account` : 'sign in to use this']] as [Mode, string, string][]).map(([m, label, hint]) => (
                <label key={m} className={`choice${mode === m ? ' selected' : ''}${m === 'profile' && !profileName ? ' disabled' : ''}`}>
                  <input type="radio" name="mode" value={m} checked={mode === m} disabled={m === 'profile' && !profileName} onChange={() => { setMode(m); setSaved(null) }} />
                  <span><b>{label}</b><br /><span className="small muted">{hint}</span></span>
                </label>
              ))}
            </div>
            {(mode === 'name' || mode === 'business') && (
              <div className="field">
                <label htmlFor="wall-name">{mode === 'business' ? 'Business name' : 'Name'}</label>
                <input id="wall-name" value={name} maxLength={NAME_MAX} onChange={(e) => { setName(e.target.value); setSaved(null) }} placeholder={mode === 'business' ? 'Acme Millwrights' : 'Pat Riggs'} autoComplete={mode === 'business' ? 'organization' : 'name'} />
                {name && check && !check.ok && <div className="hint" style={{ color: 'var(--danger)' }}>{check.reason}</div>}
              </div>
            )}
            <div className="btn-row">
              <button type="button" className="btn primary" onClick={save} disabled={saving || !canSave}>{saving ? 'Saving…' : 'Save'}</button>
              <Link className="btn" to="/support">Back to Support</Link>
            </div>
            {saved && <div className={`notice ${saved.startsWith('Saved') ? 'ok' : 'error'}`} style={{ margin: 0 }}>{saved}</div>}
            <div className="small muted">Currently shown as <b>{donation.display_mode === 'anonymous' || !donation.display_name ? 'Anonymous' : donation.display_name}</b>. You can change this for 30 days from this page.</div>
          </div>
        </>
      )}
      <h2 style={{ marginTop: 24 }}>Supporters</h2>
      <DonorWall refreshKey={refresh} />
    </div>
  )
}
