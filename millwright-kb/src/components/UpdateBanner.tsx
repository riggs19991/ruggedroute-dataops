import { useSyncExternalStore } from 'react'
import { applyUpdate, dismissUpdate, getUpdateState, subscribeUpdates } from '../lib/updates'

/** Bar under the header: shows when a newer build is published, until the reader updates. */
export function UpdateBanner() {
  const s = useSyncExternalStore(subscribeUpdates, getUpdateState, getUpdateState)
  if (!s.available || s.dismissed) return null
  const build = s.latestBuild ? ` (build ${s.latestBuild})` : ''
  return (
    <div className="update-bar" role="status" aria-live="polite">
      <span className="update-text">
        {s.native
          ? <>A newer version of Millwright KB is out{build}. Get the latest app for the newest articles and diagrams; the download installs over this one.</>
          : <>A newer version of Millwright KB is ready{build}. Update for the latest articles and diagrams.</>}
      </span>
      <span className="update-actions">
        <button type="button" className="btn primary small" onClick={() => applyUpdate()} disabled={s.applying}>
          {s.applying ? 'Updating…' : s.native ? 'Get the latest app' : 'Update now'}
        </button>
        <button type="button" className="btn small" onClick={dismissUpdate}>Later</button>
      </span>
    </div>
  )
}
