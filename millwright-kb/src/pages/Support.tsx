import { Link } from 'react-router-dom'
import { COMPANY, COMPANY_LOCATION, CONTACT_EMAIL, DONATE_URL } from '../lib/site'
import { AmpLockup } from '../components/AmpLockup'

export function SupportPage() {
  const amounts = ['$3', '$5', '$10', 'Any amount']
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
        {DONATE_URL ? (
          <>
            <div className="amounts">{amounts.map((a, i) => <a key={a} className={`chip${i === 1 ? ' primary' : ''}`} href={DONATE_URL} target="_blank" rel="noopener noreferrer" style={i === 1 ? { background: 'var(--accent)', color: 'var(--accent-ink)', borderColor: 'var(--accent)' } : undefined}>{a}</a>)}</div>
            <a className="btn primary" href={DONATE_URL} target="_blank" rel="noopener noreferrer">☕ Donate securely with Stripe</a>
          </>
        ) : (
          <div className="notice info" style={{ margin: 0 }}>The donation page is being set up. In the meantime you can reach the creator at <a href={`mailto:${CONTACT_EMAIL}`}>{CONTACT_EMAIL}</a>.</div>
        )}
        <div className="small muted">Processed by Stripe; card details never touch the app. Donations are gifts to {COMPANY} and are not tax deductible.</div>
      </div>
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
