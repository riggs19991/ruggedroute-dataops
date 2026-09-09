// Download a free-licensed photo, downscale it with headless Chromium, and record its credit.
// Usage: node scripts/photos/fetch.mjs <candidates.json> <index> <category/name> [--crop x,y,w,h (fractions)]
// or:    node scripts/photos/fetch.mjs --commons "File:Name.jpg" <category/name>
// Writes public/photos/<category>/<name>.jpg and updates public/photos/credits.json. Needs playwright on NODE_PATH.
import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'
import { licenseOk, strip } from './find.mjs'
const root = join(dirname(fileURLToPath(import.meta.url)), '..', '..')
const UA = 'MillwrightKB/1.0 (https://millwright-kb.riggs1991.workers.dev; riggs1991@gmail.com)'
const creditsPath = join(root, 'public', 'photos', 'credits.json')
const credits = existsSync(creditsPath) ? JSON.parse(readFileSync(creditsPath, 'utf8')) : {}

async function commonsInfo(title) {
  const url = `https://commons.wikimedia.org/w/api.php?action=query&titles=${encodeURIComponent(title)}&prop=imageinfo&iiprop=url|size|extmetadata&format=json`
  const d = await (await fetch(url, { headers: { 'User-Agent': UA } })).json()
  const p = Object.values(d.query.pages)[0]; const ii = p.imageinfo[0]; const m = ii.extmetadata ?? {}
  return { source: 'commons', title: p.title.replace(/^File:/, ''), pageUrl: `https://commons.wikimedia.org/wiki/${encodeURIComponent(p.title)}`, url: ii.url, width: ii.width, height: ii.height, license: m.LicenseShortName?.value ?? '', licenseUrl: m.LicenseUrl?.value ?? '', author: strip(m.Artist?.value), credit: strip(m.Credit?.value) }
}

export async function fetchPhoto(cand, rel, { crop, maxW = 1200, quality = 82 } = {}) {
  if (!licenseOk(cand.license)) throw new Error(`licence not allowed: ${cand.license}`)
  const { chromium } = await import('playwright')
  const res = await fetch(cand.url, { headers: { 'User-Agent': UA } })
  if (!res.ok) throw new Error(`download failed ${res.status}`)
  const buf = Buffer.from(await res.arrayBuffer())
  const mime = res.headers.get('content-type') || 'image/jpeg'
  const browser = await chromium.launch({ executablePath: process.env.CHROMIUM || '/opt/pw-browsers/chromium' })
  const page = await browser.newPage()
  await page.setContent(`<img id="i" src="data:${mime};base64,${buf.toString('base64')}"><canvas id="c"></canvas>`)
  await page.waitForFunction(() => document.getElementById('i').complete && document.getElementById('i').naturalWidth > 0)
  const dataUrl = await page.evaluate(({ crop, maxW, quality }) => {
    const img = document.getElementById('i'), c = document.getElementById('c')
    let sx = 0, sy = 0, sw = img.naturalWidth, sh = img.naturalHeight
    if (crop) { sx = Math.round(crop[0] * sw); sy = Math.round(crop[1] * sh); sw = Math.round(crop[2] * img.naturalWidth); sh = Math.round(crop[3] * img.naturalHeight) }
    const scale = Math.min(1, maxW / sw); c.width = Math.round(sw * scale); c.height = Math.round(sh * scale)
    const g = c.getContext('2d'); g.imageSmoothingQuality = 'high'; g.drawImage(img, sx, sy, sw, sh, 0, 0, c.width, c.height)
    return c.toDataURL('image/jpeg', quality / 100)
  }, { crop, maxW, quality })
  await browser.close()
  const out = join(root, 'public', 'photos', rel + '.jpg')
  mkdirSync(dirname(out), { recursive: true })
  writeFileSync(out, Buffer.from(dataUrl.split(',')[1], 'base64'))
  credits[rel + '.jpg'] = { title: cand.title, author: cand.author || cand.credit || 'unknown', license: cand.license, licenseUrl: cand.licenseUrl, source: cand.source, sourceUrl: cand.pageUrl }
  writeFileSync(creditsPath, JSON.stringify(credits, null, 1))
  return out
}

if (import.meta.url === `file://${process.argv[1]}`) {
  const a = process.argv.slice(2)
  const cropIdx = a.indexOf('--crop'); const crop = cropIdx !== -1 ? a[cropIdx + 1].split(',').map(Number) : undefined
  let cand, rel
  if (a[0] === '--commons') { cand = await commonsInfo(a[1]); rel = a[2] }
  else { const list = JSON.parse(readFileSync(a[0], 'utf8')); cand = list[+a[1]]; rel = a[2] }
  const out = await fetchPhoto(cand, rel, { crop })
  console.log('wrote', out, '|', cand.license, '|', cand.author)
}
