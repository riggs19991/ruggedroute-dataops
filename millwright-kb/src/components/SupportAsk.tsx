import { Link } from 'react-router-dom'
import { DONATE_URL, donateHref } from '../lib/site'
import { Icon } from '../lib/icons'

/** Small, polite ask shown at the end of articles and on the support page. */
export function SupportAsk({ compact = false }: { compact?: boolean }) {
  const button = DONATE_URL
    ? <a className="btn primary small donate" href={DONATE_URL} target="_blank" rel="noopener noreferrer"><Icon name="heart" size={18} />Support the creator</a>
    : <Link className="btn primary small donate" to={donateHref}><Icon name="heart" size={18} />Support the creator</Link>
  if (compact) return <span className="support-inline">{button}</span>
  return (
    <aside className="support-card">
      <div className="head"><Icon name="heart" size={20} /><h3>Was this useful on the job?</h3></div>
      <p>Millwright KB is free, has no ads, and is built and paid for by one person. If it saved you time, a small donation keeps it online and growing.</p>
      <div className="btn-row">{button}<Link className="btn small" to="/support">Other ways to help</Link></div>
    </aside>
  )
}
