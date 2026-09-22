import { useEffect, useState } from 'react'
import { supabase } from '../lib/supabase'
import { useAuth } from '../lib/auth'

export type WallEntry = { id: string; amount_cents: number; currency: string; display_mode: string; display_name: string; created_at: string }

export const money = (cents: number, currency = 'usd') =>
  new Intl.NumberFormat('en-US', { style: 'currency', currency: currency.toUpperCase(), minimumFractionDigits: cents % 100 ? 2 : 0 }).format(cents / 100)

const when = (iso: string) => {
  const days = Math.floor((Date.now() - new Date(iso).getTime()) / 86_400_000)
  if (days <= 0) return 'today'
  if (days === 1) return 'yesterday'
  if (days < 30) return `${days} days ago`
  return new Date(iso).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })
}

export const wallLabel = (e: WallEntry) => (e.display_mode === 'anonymous' || !e.display_name ? 'Anonymous' : e.display_name)

/** Public list of verified donations, newest first, with the running total. */
export function DonorWall({ refreshKey = 0, pageSize = 50 }: { refreshKey?: number; pageSize?: number }) {
  const { isAdmin } = useAuth()
  const [rows, setRows] = useState<WallEntry[] | null>(null)
  const [shown, setShown] = useState(pageSize)
  const [failed, setFailed] = useState(false)

  useEffect(() => {
    let live = true
    supabase.from('mw_donations').select('id, amount_cents, currency, display_mode, display_name, created_at').order('created_at', { ascending: false }).limit(500)
      .then(({ data, error }) => { if (!live) return; if (error) setFailed(true); else setRows((data as WallEntry[]) || []) })
    return () => { live = false }
  }, [refreshKey])

  const hide = async (id: string) => {
    if (!confirm('Hide this entry from the wall?')) return
    const { error } = await supabase.rpc('mw_hide_donation', { p_id: id })
    if (!error) setRows((r) => (r || []).filter((e) => e.id !== id))
  }

  if (failed) return <p className="muted small">The supporters list needs a connection.</p>
  if (!rows) return <p className="loading">Loading supporters…</p>
  const total = rows.reduce((s, e) => s + e.amount_cents, 0)
  return (
    <section className="wall" aria-label="Supporters">
      <div className="wall-total">
        {rows.length === 0
          ? <span>No donations yet. Yours would be the first on the wall.</span>
          : <span><b>{rows.length}</b> {rows.length === 1 ? 'donation' : 'donations'}, <b>{money(total)}</b> given so far</span>}
      </div>
      {rows.length > 0 && (
        <ul className="wall-list">
          {rows.slice(0, shown).map((e) => (
            <li key={e.id} className="wall-row">
              <span className="wall-name">{wallLabel(e)}{e.display_mode === 'business' && <span className="wall-tag">business</span>}</span>
              <span className="wall-amount">{money(e.amount_cents, e.currency)}</span>
              <span className="wall-when">{when(e.created_at)}</span>
              {isAdmin && <button type="button" className="linklike small" onClick={() => hide(e.id)}>hide</button>}
            </li>
          ))}
        </ul>
      )}
      {rows.length > shown && <button type="button" className="btn small" onClick={() => setShown((n) => n + pageSize)}>Show more</button>}
    </section>
  )
}
