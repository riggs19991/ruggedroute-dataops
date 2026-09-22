// Calls to the site's own Worker routes (/api/*). Inside the Android app the shell is served from
// https://localhost, so the calls go to the live site instead.
import { Capacitor } from '@capacitor/core'
import { LIVE_SITE } from './site'

export const apiBase = () => (Capacitor.isNativePlatform() ? LIVE_SITE : '')

export type ApiResult<T> = { ok: boolean; status: number; data: T | null; error: string | null }

export async function postJson<T>(path: string, body: unknown): Promise<ApiResult<T>> {
  try {
    const r = await fetch(apiBase() + path, { method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body) })
    const text = await r.text()
    let data: (T & { error?: string }) | null = null
    try { data = text ? JSON.parse(text) : null } catch { data = null }
    return { ok: r.ok, status: r.status, data: r.ok ? data : null, error: r.ok ? null : (data?.error || `HTTP ${r.status}`) }
  } catch {
    return { ok: false, status: 0, data: null, error: 'offline' }
  }
}
