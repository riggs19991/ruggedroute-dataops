// Version checks and the update prompt state.
//
// Every time the app is opened or comes back to the foreground it (1) asks the service worker to
// look for a new build and (2) fetches /version.json (written at build time, never cached) and
// compares its build id with the one baked into this bundle. When either finds something newer the
// UpdateBanner offers to update: on the web that swaps in the waiting service worker and reloads;
// in the Android app (which embeds its own copy of the site) it opens the latest APK download.
import { registerSW } from 'virtual:pwa-register'
import { Capacitor } from '@capacitor/core'
import { BUILD_ID } from './site'

export const APK_URL = 'https://github.com/riggs19991/ruggedroute-dataops/releases/download/android-latest/millwright-kb.apk'
const LIVE_SITE = 'https://millwright-kb.riggs1991.workers.dev'
const HOUR = 60 * 60 * 1000

export type UpdateState = {
  /** A newer build exists (from the service worker or version.json). */
  available: boolean
  /** Build id of the newest published version, when version.json could be read. */
  latestBuild: string | null
  /** Running inside the Capacitor app: the update is a new APK, not a reload. */
  native: boolean
  /** The new service worker is installed and waiting; Update can swap it in at once. */
  swWaiting: boolean
  /** The reader tapped Update and the swap or download is under way. */
  applying: boolean
  /** The reader tapped Later: hidden until the app is opened again. */
  dismissed: boolean
}

const native = typeof window !== 'undefined' && Capacitor.isNativePlatform()
let state: UpdateState = { available: false, latestBuild: null, native, swWaiting: false, applying: false, dismissed: false }
const listeners = new Set<() => void>()
function set(patch: Partial<UpdateState>) {
  state = { ...state, ...patch }
  listeners.forEach((l) => l())
}
export const getUpdateState = () => state
export function subscribeUpdates(fn: () => void) {
  listeners.add(fn)
  return () => { listeners.delete(fn) }
}

let registration: ServiceWorkerRegistration | undefined
let updateSW: ((reloadPage?: boolean) => Promise<void>) | undefined
let lastCheck = 0
let started = false

/** Ask for the newest version now: service worker update plus the version.json marker. */
export async function checkForUpdate(force = false) {
  if (!force && Date.now() - lastCheck < 15_000) return
  lastCheck = Date.now()
  if (registration) { try { await registration.update() } catch { /* offline or blocked: the marker fetch below still runs */ } }
  try {
    const base = native ? LIVE_SITE + '/' : import.meta.env.BASE_URL
    const r = await fetch(`${base}version.json?t=${Date.now()}`, { cache: 'no-store' })
    if (!r.ok) return
    const v = (await r.json()) as { build?: string }
    if (typeof v.build === 'string' && v.build && v.build !== BUILD_ID) {
      set({ available: true, latestBuild: v.build })
      if (registration && !state.swWaiting) registration.update().catch(() => {})
    }
  } catch { /* offline: nothing to report */ }
}

/** Apply the update the reader asked for. */
export async function applyUpdate() {
  if (native) {
    // The Android app cannot replace itself: hand the reader the newest APK and keep the banner up.
    window.open(APK_URL, '_blank')
    return
  }
  set({ applying: true })
  if (updateSW && state.swWaiting) { await updateSW(true); return }
  // The marker says a build exists but the worker has not seen it yet: look once more, then reload.
  if (registration) {
    try { await registration.update() } catch { /* fall through to the reload */ }
    for (let i = 0; i < 20 && !state.swWaiting; i++) await new Promise((res) => setTimeout(res, 250))
    if (updateSW && state.swWaiting) { await updateSW(true); return }
  }
  window.location.reload()
}

/** Later: hide the bar for this page view only. The next open of the app asks again. */
export function dismissUpdate() { set({ dismissed: true }) }

/** Register the service worker and start checking on open, on return to the foreground and hourly. */
export function startUpdateChecks() {
  if (started || typeof window === 'undefined') return
  started = true
  if ('serviceWorker' in navigator) {
    updateSW = registerSW({
      immediate: true,
      onNeedRefresh() { set({ available: true, swWaiting: true }) },
      onRegisteredSW(_url, reg) {
        registration = reg ?? undefined
        setInterval(() => checkForUpdate(true), HOUR)
        checkForUpdate(true)
      },
      onRegisterError() { checkForUpdate(true) },
    })
  } else {
    checkForUpdate(true)
  }
  document.addEventListener('visibilitychange', () => { if (document.visibilityState === 'visible') checkForUpdate() })
  window.addEventListener('focus', () => checkForUpdate())
  if (native) {
    import('@capacitor/app').then(({ App }) => { App.addListener('appStateChange', ({ isActive }) => { if (isActive) checkForUpdate() }) }).catch(() => {})
  }
}
