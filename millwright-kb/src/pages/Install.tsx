import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { isStandalone, type BeforeInstallPromptEvent } from '../lib/pwa'
import { Icon } from '../lib/icons'

const APK = 'https://github.com/riggs19991/ruggedroute-dataops/releases/download/android-latest/millwright-kb.apk'

export function InstallPage() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null)
  const standalone = isStandalone()
  useEffect(() => {
    const onPrompt = (e: Event) => { e.preventDefault(); setDeferred(e as BeforeInstallPromptEvent) }
    window.addEventListener('beforeinstallprompt', onPrompt)
    return () => window.removeEventListener('beforeinstallprompt', onPrompt)
  }, [])

  return (
    <div style={{ maxWidth: 720, display: 'flex', flexDirection: 'column', gap: 14 }}>
      <div>
        <h1>Install on your phone</h1>
        <p className="muted" style={{ margin: 0 }}>No app store needed. It opens from your home screen, works offline for anything you have opened, and updates itself.</p>
      </div>
      {standalone && <div className="notice ok" style={{ margin: 0 }}>You are already using the installed app.</div>}
      {deferred && <div><button type="button" className="btn primary" onClick={async () => { await deferred.prompt(); setDeferred(null) }}><Icon name="download" size={20} />Install app now</button></div>}

      <div className="card panel">
        <div className="head"><Icon name="download" size={22} /><h2>Android app (APK)</h2></div>
        <ol className="steps">
          <li><span className="n">1</span><span className="t">Tap <b>Download the app</b> below in Chrome.</span></li>
          <li><span className="n">2</span><span className="t">Open the file. When asked, allow installs from Chrome.</span></li>
          <li><span className="n">3</span><span className="t">Tap <b>Install</b>. Newer builds install over the old one from the same link.</span></li>
        </ol>
        <a className="btn primary" href={APK}><Icon name="download" size={20} />Download the app</a>
      </div>

      <div className="card panel">
        <div className="head"><Icon name="phone" size={22} /><h2>Add to home screen</h2></div>
        <ol className="steps">
          <li><span className="n">1</span><span className="t">Open this site in Chrome (Android) or Safari (iPhone and iPad; Apple only lets Safari install web apps).</span></li>
          <li><span className="n">2</span><span className="t">Android: menu <b>⋮</b> then <b>Add to Home screen</b> or <b>Install app</b>. iPhone: <b>Share</b> then <b>Add to Home Screen</b>, then <b>Add</b>.</span></li>
          <li><span className="n">3</span><span className="t">Open it from the icon like any app.</span></li>
        </ol>
        <p className="small muted" style={{ margin: 0 }}>Windows, Mac and Chromebook: in Chrome or Edge click the install icon at the right end of the address bar, or choose <b>Install Millwright KB</b> from the browser menu.</p>
      </div>

      <div className="card panel">
        <div className="head"><Icon name="user" size={22} /><h2>Sign in, offline, photos</h2></div>
        <ul style={{ margin: 0, paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 6 }}>
          <li>You can read everything without an account. Sign in to contribute, join a class group, bookmark, upvote or attach photos and manuals.</li>
          <li>Create your account once. The confirmation link opens in your browser; then come back to the app icon and sign in with your password. On iPhone the installed app keeps its own sign-in.</li>
          <li>Everything you have opened is kept on the phone. Search needs a connection; the A-Z index and read articles do not. When a new version is published the app offers to reload.</li>
          <li>On <Link to="/contribute">Contribute</Link> and in group posts you can take a photo with the camera or attach PDFs and documents up to 50 MB. Large photos are shrunk before upload.</li>
        </ul>
      </div>
    </div>
  )
}
