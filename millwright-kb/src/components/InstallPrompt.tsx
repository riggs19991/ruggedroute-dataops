import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { isAndroid, isIOS, isStandalone, type BeforeInstallPromptEvent } from '../lib/pwa'
import { Icon } from '../lib/icons'

const KEY = 'mw-install-dismissed'

/** Home-page card: an Install button where the browser supports it, iPhone steps otherwise. */
export function InstallPrompt() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null)
  const [hidden, setHidden] = useState(() => { try { return localStorage.getItem(KEY) === '1' } catch { return false } })
  const [installed, setInstalled] = useState(() => isStandalone())

  useEffect(() => {
    const onPrompt = (e: Event) => { e.preventDefault(); setDeferred(e as BeforeInstallPromptEvent) }
    const onInstalled = () => setInstalled(true)
    window.addEventListener('beforeinstallprompt', onPrompt)
    window.addEventListener('appinstalled', onInstalled)
    return () => { window.removeEventListener('beforeinstallprompt', onPrompt); window.removeEventListener('appinstalled', onInstalled) }
  }, [])

  if (installed || hidden) return null

  function dismiss() { setHidden(true); try { localStorage.setItem(KEY, '1') } catch { /* private mode */ } }

  async function install() {
    if (!deferred) return
    await deferred.prompt()
    const { outcome } = await deferred.userChoice
    if (outcome === 'accepted') setInstalled(true)
    setDeferred(null)
  }

  const ios = isIOS(), android = isAndroid()
  return (
    <div className="install-card" role="region" aria-label="Install the app">
      <div className="install-text">
        <Icon name="phone" size={24} />
        <span>
          <strong>Install on your phone.</strong>{' '}
          {ios
            ? <>In Safari tap <span className="share-icon" aria-label="Share">⎋</span> Share, then <b>Add to Home Screen</b>. Works offline and opens like an app.</>
            : deferred
              ? <>Works offline and opens like an app.</>
              : android
                ? <>In Chrome open the menu <b>⋮</b> and tap <b>Add to Home screen</b>, or get the Android app.</>
                : <>Install it from your browser's menu to open it like an app and keep articles offline.</>}
          {' '}<Link to="/install">How</Link>
        </span>
      </div>
      <div className="install-actions">
        {deferred ? <button type="button" className="btn primary small" onClick={install}>Install</button> : <Link to="/install" className="btn primary small">Install</Link>}
        <button type="button" className="btn small" onClick={dismiss} aria-label="Dismiss">Not now</button>
      </div>
    </div>
  )
}
