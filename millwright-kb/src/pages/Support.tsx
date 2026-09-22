import { useState } from 'react'
import { Link } from 'react-router-dom'
import { COMPANY, COMPANY_LOCATION, CONTACT_EMAIL, DONATE_URL } from '../lib/site'
import { postJson } from '../lib/api'
import { AmpLockup } from '../components/AmpLockup'
import { DonorWall } from '../components/DonorWall'
import { Capacitor } from '@capacitor/core'

const PRESETS = [5, 10, 25, 50]

export function SupportPage() {
  const [dollars, setDollars] = useState<number>(10)
  const [custom, setCustom] = useState('')
  const [busy, setBusy] = useState(false)
  const [msg, setMsg] = useState<string | null>(null)
  const amount = custom ? Number(custom) : dollars
  const valid = Number.isFinite(amount) && amount >= 1 && amount <= 10000

  const donate = async () => {
    if (!valid) { setMsg('Enter an amount from $1 to $10,000.'); return }
    setBusy(true); setMsg(null)
    const r = await postJson<{ url: string }>('/api/donate/checkout', { amount_cents: Math.round(amount * 100) })
    setBusy(false)
    if (r.ok && r.data?.url) {
      if (Capacitor.isNativePlatform()) window.open(r.data.url, '_blank'); else window.location.assign(r.data.url)
      return
    }
    if (r.status === 503 && DONATE_URL) {
      // The in-app checkout is not configured yet: the payment link still works, without the wall entry.
      window.open(DONATE_URL, '_blank', 'noopener,noreferrer')
      return
    }
    setMsg(r.error === 'offline' ? 'You are offline. Try again when you have a connection.' : 'Could not start the donation. Please try again in a minute.')
  }

  return (
    <div style={{ maxWidth: 720 }}>
      <div className="page-head"><span className="glyph big" aria-hidden="true">☕</span><h1>Support the creator</h1></div>
      <p>
        Millwright Knowledge Base is free to use, free of ads and free of tracking. One person writes the reference
        material, draws the diagrams and pays for the hosting and the time it takes to keep it going.
      </p>
      <p>
        If it saved you time on a job or got you through a test, a small donation is a real help and is genuinely
        appreciated. There is no pressure and nothing is locked behind it: everything stays free for every millwright
        and apprentice.
      </p>
      <div className="card donate-box">
        <div className="amounts" role="group" aria-label="Amount">
          {PRESETS.map((d) => (
            <button key={d} type="button" className={`chip${!custom && dollars === d ? ' selected' : ''}`} onClick={() => { setDollars(d); setCustom('') }}>${d}</button>
          ))}
          <label className="chip chip-input">
            <span>$</span>
            <input type="number" inputMode="decimal" min={1} max={10000} step={1} placeholder="other" value={custom} onChange={(e) => setCustom(e.target.value)} aria-label="Other amount in dollars" />
          </label>
        </div>
        <button type="button" className="btn primary" onClick={donate} disabled={busy || !valid}>
          {busy ? 'Opening Stripe…' : `☕ Donate ${valid ? `$${amount}` : ''} with Stripe`}
        </button>
        {msg && <div className="notice error" style={{ margin: 0 }}>{msg}</div>}
        <div className="small muted">
          Processed by Stripe; card details never touch the app. After you donate you choose how you appear on the
          wall below: your name, your business, your profile name, or anonymous. Donations are gifts to {COMPANY} and
          are not tax deductible.
        </div>
      </div>

      <h2 style={{ marginTop: 24 }}>Supporters</h2>
      <p className="muted small" style={{ marginTop: 0 }}>Every entry is a verified donation. Names are the donor's own choice.</p>
      <DonorWall />

      <AmpLockup text={<>Millwright KB is made by <b>{COMPANY}</b>, {COMPANY_LOCATION}.</>} />
      <h2 style={{ marginTop: 20 }}>Other ways to help</h2>
      <ol className="steps">
        <li><span className="n">1</span><span className="t">Add a procedure, chart or manual you wish had existed when you started. <Link to="/contribute">Contribute</Link></span></li>
        <li><span className="n">2</span><span className="t">Upvote articles that are well done so others find them.</span></li>
        <li><span className="n">3</span><span className="t">Tell an apprentice or an instructor about the app. <Link to="/install">Install page</Link></span></li>
        <li><span className="n">4</span><span className="t">Report mistakes to <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.</span></li>
      </ol>
    </div>
  )
}
