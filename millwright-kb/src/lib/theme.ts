// Light/dark theme: follows the phone by default, overridable with a stored choice.
export type Theme = 'light' | 'dark' | 'system'
const KEY = 'mw-theme'

export function getTheme(): Theme {
  try { const v = localStorage.getItem(KEY); if (v === 'light' || v === 'dark') return v } catch { /* private mode */ }
  return 'system'
}
export function resolvedTheme(t: Theme = getTheme()): 'light' | 'dark' {
  if (t !== 'system') return t
  return typeof matchMedia !== 'undefined' && matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light'
}
export function applyTheme(t: Theme) {
  const root = document.documentElement
  if (t === 'system') root.removeAttribute('data-theme'); else root.setAttribute('data-theme', t)
  const meta = document.querySelector('meta[name="theme-color"]:not([media])') as HTMLMetaElement | null
  if (meta) meta.content = resolvedTheme(t) === 'dark' ? '#080d17' : '#0f1b2d'
}
export function setTheme(t: Theme) {
  try { if (t === 'system') localStorage.removeItem(KEY); else localStorage.setItem(KEY, t) } catch { /* private mode */ }
  applyTheme(t)
}
/** Toggle between light and dark relative to what is showing now. */
export function toggleTheme(): 'light' | 'dark' {
  const next = resolvedTheme() === 'dark' ? 'light' : 'dark'
  setTheme(next)
  return next
}
export function initTheme() { applyTheme(getTheme()) }
