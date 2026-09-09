// Search Wikimedia Commons (and Openverse) for free-licensed photos.
// Usage: node scripts/photos/find.mjs "<query>" [--limit 12] [--out candidates.json]
// Prints candidates with licence, author, size and a thumbnail URL. Only permissive licences are kept.
import { writeFileSync } from 'node:fs'
const args = process.argv.slice(2)
const q = args.find((a) => !a.startsWith('--'))
const limit = +(args[args.indexOf('--limit') + 1] || 12)
const outIdx = args.indexOf('--out')
const UA = 'MillwrightKB/1.0 (https://millwright-kb.riggs1991.workers.dev; riggs1991@gmail.com)'
export const OK_LICENSES = [/^cc0/i, /^public domain/i, /^pd/i, /^cc by(-sa)?( \d(\.\d)?)?$/i, /^cc-by(-sa)?/i, /^attribution/i, /no restrictions/i]
export function licenseOk(s) { return OK_LICENSES.some((r) => r.test(String(s || '').trim())) }
export function strip(html) { return String(html || '').replace(/<[^>]+>/g, '').replace(/\s+/g, ' ').trim() }

export async function searchCommons(query, n = 12) {
  const url = `https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrsearch=${encodeURIComponent(query + ' filetype:bitmap')}&gsrnamespace=6&gsrlimit=${n}&prop=imageinfo&iiprop=url|size|extmetadata&iiurlwidth=640&format=json`
  const r = await fetch(url, { headers: { 'User-Agent': UA } })
  const d = await r.json()
  const out = []
  for (const p of Object.values(d.query?.pages ?? {})) {
    const ii = p.imageinfo?.[0]; if (!ii) continue
    const m = ii.extmetadata ?? {}
    const lic = m.LicenseShortName?.value ?? ''
    out.push({ source: 'commons', title: p.title.replace(/^File:/, ''), pageUrl: `https://commons.wikimedia.org/wiki/${encodeURIComponent(p.title)}`, url: ii.url, thumb: ii.thumburl, width: ii.width, height: ii.height, license: lic, licenseUrl: m.LicenseUrl?.value ?? '', author: strip(m.Artist?.value), credit: strip(m.Credit?.value), description: strip(m.ImageDescription?.value).slice(0, 160), ok: licenseOk(lic) && ii.width >= 600 })
  }
  return out
}
export async function searchOpenverse(query, n = 12) {
  const url = `https://api.openverse.org/v1/images/?q=${encodeURIComponent(query)}&license=cc0,pdm,by,by-sa&page_size=${n}`
  try {
    const r = await fetch(url, { headers: { 'User-Agent': UA } }); if (!r.ok) return []
    const d = await r.json()
    return (d.results ?? []).map((x) => ({ source: 'openverse:' + x.source, title: x.title, pageUrl: x.foreign_landing_url, url: x.url, thumb: x.thumbnail, width: x.width, height: x.height, license: `${x.license.toUpperCase()} ${x.license_version ?? ''}`.trim(), licenseUrl: x.license_url, author: x.creator ?? '', credit: x.creator ?? '', description: x.title, ok: (x.width ?? 0) >= 600 }))
  } catch { return [] }
}
if (import.meta.url === `file://${process.argv[1]}`) {
  if (!q) { console.error('usage: find.mjs "<query>"'); process.exit(1) }
  const [c, o] = await Promise.all([searchCommons(q, limit), searchOpenverse(q, Math.ceil(limit / 2))])
  const all = [...c, ...o]
  for (const x of all) console.log(`${x.ok ? 'OK ' : '-- '} ${x.width}x${x.height} | ${x.license} | ${x.author.slice(0, 30)} | ${x.title.slice(0, 70)}`)
  if (outIdx !== -1) writeFileSync(args[outIdx + 1], JSON.stringify(all, null, 1))
}
