// Writes public/logo.svg (the gear-and-wrench mark) and renders the PNG app icons from it with
// headless Chromium (Playwright). Run: node scripts/make-icons.mjs
// Playwright is not a project dependency: point NODE_PATH at a folder that has it, e.g.
//   NODE_PATH=/path/with/node_modules node scripts/make-icons.mjs
import { writeFileSync, mkdirSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
const NAVY = '#0f1b2d', AMBER = '#f4a11d'

function gearPath(cx, cy, ro, ri, teeth) {
  const pts = []
  const n = teeth * 4
  for (let i = 0; i < n; i++) {
    const a = (i / n) * Math.PI * 2
    const r = i % 4 === 0 || i % 4 === 1 ? ro : ri
    pts.push(`${(cx + r * Math.cos(a)).toFixed(2)},${(cy + r * Math.sin(a)).toFixed(2)}`)
  }
  return 'M' + pts.join(' L') + ' Z'
}
const GEAR = gearPath(24, 24, 22, 17, 8)
const mark = (bg) => `<path d="${GEAR}" fill="${AMBER}"/><circle cx="24" cy="24" r="13" fill="${bg}"/><path d="M14 34 L25 23" stroke="${AMBER}" stroke-width="5" stroke-linecap="round" fill="none"/><path d="M23 15 a7 7 0 1 1 10 10" stroke="${AMBER}" stroke-width="4.5" stroke-linecap="round" fill="none"/>`

/** Square icon: navy field, mark scaled to (1 - 2*pad) of the side. */
function iconSvg(size, { pad = 0.11, rounded = 0, bg = NAVY } = {}) {
  const inset = size * pad, scale = (size - inset * 2) / 48
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"><rect width="${size}" height="${size}" rx="${rounded}" fill="${bg}"/><g transform="translate(${inset} ${inset}) scale(${scale})">${mark(bg)}</g></svg>`
}

// Favicon / header logo: transparent background, navy hub so it reads on light and dark.
writeFileSync(join(root, 'public', 'logo.svg'), `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48">${mark(NAVY)}</svg>\n`)
console.log('wrote public/logo.svg')

const targets = [
  ['public/icon-180.png', 180, { pad: 0.12 }],
  ['public/icon-192.png', 192, { pad: 0.12 }],
  ['public/icon-512.png', 512, { pad: 0.12 }],
  ['public/icon-maskable-512.png', 512, { pad: 0.2 }],
  ['docs/store/icon-512.png', 512, { pad: 0.12 }],
  ['docs/store/icon-1024.png', 1024, { pad: 0.12 }],
]

let chromium
try { ({ chromium } = createRequire(import.meta.url)('playwright')) } catch { chromium = null }
if (!chromium) { console.log('playwright not found: SVG written, PNG icons left as they are'); process.exit(0) }

const browser = await chromium.launch({ executablePath: process.env.PW_CHROMIUM || undefined })
const page = await browser.newPage({ viewport: { width: 1024, height: 1024 }, deviceScaleFactor: 1 })
for (const [rel, size, opts] of targets) {
  const svg = iconSvg(size, opts)
  await page.setContent(`<body style="margin:0;background:transparent">${svg}</body>`)
  await page.setViewportSize({ width: size, height: size })
  mkdirSync(dirname(join(root, rel)), { recursive: true })
  await page.screenshot({ path: join(root, rel), clip: { x: 0, y: 0, width: size, height: size }, omitBackground: true })
  console.log('wrote', rel)
}
// Play feature graphic: 1024x500, mark + wordmark on navy.
await page.setViewportSize({ width: 1024, height: 500 })
await page.setContent(`<body style="margin:0;background:${NAVY};font-family:'Arial Narrow',Arial,sans-serif"><div style="display:flex;align-items:center;justify-content:center;gap:40px;height:500px;color:#f5f7fa"><svg width="260" height="260" viewBox="0 0 48 48">${mark(NAVY)}</svg><div><div style="font-size:84px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;line-height:1">Millwright <span style="color:${AMBER}">KB</span></div><div style="font-size:30px;color:rgba(245,247,250,0.75);margin-top:10px">The trade's reference, in your pocket.</div></div></div></body>`)
await page.screenshot({ path: join(root, 'docs/store/feature-graphic.png'), clip: { x: 0, y: 0, width: 1024, height: 500 } })
console.log('wrote docs/store/feature-graphic.png')
await browser.close()
