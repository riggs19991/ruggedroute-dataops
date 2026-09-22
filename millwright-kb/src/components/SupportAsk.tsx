import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { donateHref } from '../lib/site'
import { supabase } from '../lib/supabase'

/** Small, polite ask shown at the end of articles: leads to the donate page and the supporters wall. */
export function SupportAsk({ compact = false }: { compact?: boolean }) {
  const [count, setCount] = useState<number | null>(null)
  useEffect(() => {
    if (compact) return
    supabase.from('mw_donations').select('id', { count: 'exact', head: true }).then(({ count: n }) => setCount(n ?? null))
  }, [compact])
  const button = <Link className="btn primary small donate" to={donateHref}>☕ Support the creator</Link>
  if (compact) return <span className="support-inline">{button}</span>
  return (
    <aside className="support-card">
      <div className="head"><span className="glyph" aria-hidden="true">☕</span><h3>Was this useful on the job?</h3></div>
      <p>Millwright KB is free, has no ads, and is built and paid for by one person. If it saved you time, a small donation keeps it online and growing{count ? <>: join <b>{count}</b> {count === 1 ? 'supporter' : 'supporters'} on the wall</> : null}.</p>
      <div className="btn-row">{button}<Link className="btn small" to="/support">See the supporters</Link></div>
    </aside>
  )
}
