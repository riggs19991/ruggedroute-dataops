import { Link } from 'react-router-dom'
import { DONATE_URL, donateHref } from '../lib/site'

/** Small, polite ask shown at the end of articles and on the support page. */
export function SupportAsk({ compact = false }: { compact?: boolean }) {
  const button = DONATE_URL
    ? <a className="btn small donate" href={DONATE_URL} target="_blank" rel="noopener noreferrer">☕ Support the creator</a>
    : <Link className="btn small donate" to={donateHref}>☕ Support the creator</Link>
  if (compact) return <span className="support-inline">{button}</span>
  return (
    <aside className="support-card">
      <p>
        <strong>Was this useful on the job?</strong> Millwright KB is free, has no ads, and is built and paid for by one person.
        If it saved you time, a small donation helps keep it online and growing.
      </p>
      {button}
    </aside>
  )
}
