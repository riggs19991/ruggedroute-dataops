// Search many photo queries at once and build a contact sheet of the licence-OK candidates.
// Usage: node scripts/photos/batch-find.mjs queries.json out-dir   (queries.json: { key: "query" | ["q1","q2"] })
// Writes out-dir/<key>.json (candidates) and out-dir/sheet-N.png (4 keys per sheet, thumbnails embedded).
import { readFileSync, writeFileSync, mkdirSync } from 'node:fs'
import { join } from 'node:path'
import { searchCommons, searchOpenverse } from './find.mjs'
const [qfile, outDir] = process.argv.slice(2)
const queries = JSON.parse(readFileSync(qfile, 'utf8'))
mkdirSync(outDir, { recursive: true })
const UA = 'MillwrightKB/1.0 (https://millwright-kb.riggs1991.workers.dev; riggs1991@gmail.com)'
const seen = new Set()
async function thumb(url) {
  try { const r = await fetch(url, { headers: { 'User-Agent': UA } }); if (!r.ok) return ''; const b = Buffer.from(await r.arrayBuffer()); return `data:${r.headers.get('content-type') || 'image/jpeg'};base64,${b.toString('base64')}` } catch { return '' }
}
const keys = Object.keys(queries), results = {}
await Promise.all(keys.map(async (k) => {
  const qs = [].concat(queries[k]); let all = []
  for (const q of qs) { const [c, o] = await Promise.all([searchCommons(q, 14), searchOpenverse(q, 6)]); all = all.concat(c, o) }
  const ok = all.filter((x) => x.ok && !seen.has(x.url) && !/\.(svg|gif|png)$/i.test(x.url)).slice(0, 10)
  ok.forEach((x) => seen.add(x.url))
  writeFileSync(join(outDir, k + '.json'), JSON.stringify(ok, null, 1))
  results[k] = ok
}))
// thumbnails in parallel (limit 8)
const jobs = []; for (const k of keys) for (const x of results[k]) jobs.push(x)
let i = 0; await Promise.all(Array.from({ length: 8 }, async () => { while (i < jobs.length) { const x = jobs[i++]; x.data = await thumb(x.thumb || x.url) } }))
const { chromium } = await import('playwright')
const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' })
for (let s = 0; s < keys.length; s += 4) {
  const html = keys.slice(s, s + 4).map((k) => `<div style="margin:6px 0 2px;font:bold 13px monospace;background:#ffe">${k}: ${[].concat(queries[k]).join(' | ')} (${results[k].length})</div>` +
    results[k].map((x, j) => `<div style="display:inline-block;vertical-align:top;width:196px;margin:2px;background:#fff;border:1px solid #bbb"><div style="height:130px;background:#eee;display:flex;align-items:center;justify-content:center;overflow:hidden">${x.data ? `<img src="${x.data}" style="max-width:196px;max-height:130px">` : 'no thumb'}</div><div style="font:10px monospace;padding:2px;height:44px;overflow:hidden">#${j} ${x.width}x${x.height} ${x.license}<br>${(x.author || '').slice(0, 28)}<br>${x.title.slice(0, 40)}</div></div>`).join('')).join('')
  const page = await browser.newPage({ viewport: { width: 1030, height: 800 } })
  await page.setContent(`<html><body style="margin:4px;background:#ddd;width:1020px">${html}</body></html>`)
  await page.screenshot({ path: join(outDir, `sheet-${s / 4 + 1}.png`), fullPage: true }); await page.close()
}
await browser.close()
for (const k of keys) console.log(k, results[k].length)
