import { useEffect, useState } from 'react'
import { isStandalone, type BeforeInstallPromptEvent } from '../lib/pwa'

export function InstallPage() {
  const [deferred, setDeferred] = useState<BeforeInstallPromptEvent | null>(null)
  const standalone = isStandalone()
  useEffect(() => {
    const onPrompt = (e: Event) => { e.preventDefault(); setDeferred(e as BeforeInstallPromptEvent) }
    window.addEventListener('beforeinstallprompt', onPrompt)
    return () => window.removeEventListener('beforeinstallprompt', onPrompt)
  }, [])

  return (
    <div className="md" style={{ maxWidth: 720 }}>
      <h1>Install Millwright KB on your phone</h1>
      {standalone && <div className="notice ok">You are already using the installed app.</div>}
      <p>The knowledge base installs straight from the website: no app store, no download, and it updates itself. Once installed it opens full screen from its own icon and keeps every article and diagram you have opened available with no signal.</p>
      {deferred && <p><button type="button" className="btn primary" onClick={async () => { await deferred.prompt(); setDeferred(null) }}>Install app</button></p>}
      <h2>iPhone and iPad (Safari)</h2>
      <ol>
        <li>Open <b>millwright-kb.riggs1991.workers.dev</b> in <b>Safari</b> (not Chrome: Apple only allows Safari to install web apps).</li>
        <li>Tap the <b>Share</b> button (the square with an arrow, at the bottom of the screen).</li>
        <li>Scroll the list and tap <b>Add to Home Screen</b>, then <b>Add</b>.</li>
        <li>Open <b>Millwright KB</b> from the home screen and sign in with your email and password.</li>
      </ol>
      <h2>Android (Chrome)</h2>
      <ol>
        <li>Open the site in <b>Chrome</b>.</li>
        <li>Tap <b>Install app</b> on the home page, or open the <b>⋮</b> menu and tap <b>Add to Home screen</b> / <b>Install app</b>.</li>
        <li>Tap <b>Install</b>. The icon appears with your other apps.</li>
      </ol>
      <h2>Android app file (APK)</h2>
      <p>There is also a real Android app, built automatically from the same content. It is the same app as the home-screen install, in a package you can share and install without a browser.</p>
      <ol>
        <li>On the phone open <a href="https://github.com/riggs19991/ruggedroute-dataops/releases/download/android-latest/millwright-kb.apk">millwright-kb.apk</a> (latest build).</li>
        <li>When the download finishes, tap it. If Android asks, allow Chrome to install apps from this source.</li>
        <li>Tap <b>Install</b>. Newer builds install over the old one from the same link.</li>
      </ol>
      <h2>Windows, Mac and Chromebook</h2>
      <p>In Chrome or Edge, click the install icon at the right end of the address bar, or use the browser menu and choose <b>Install Millwright KB</b>.</p>
      <h2>Signing in from the installed app</h2>
      <ul>
        <li>Create your account once (in the app or on the website). The confirmation link in the email opens in your <b>browser</b>: that is normal. Come back to the app icon and sign in with your <b>password</b>.</li>
        <li>The installed app and the browser keep separate sign-ins on iPhone, so sign in inside the app itself.</li>
        <li>Forgot your password? Use <b>Forgot password</b> on the sign-in page.</li>
      </ul>
      <h2>Offline</h2>
      <p>Everything you have opened is kept on the phone. Search needs a connection; the A-Z index and the articles you have read do not. When a new version is published the app tells you and reloads.</p>
      <h2>Photos and files</h2>
      <p>On the Contribute page and in group posts you can take a photo with the camera or attach PDFs and documents up to 50 MB. Large photos are shrunk before upload so they go quickly on mobile data.</p>
    </div>
  )
}
