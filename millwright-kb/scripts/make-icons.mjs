// Writes public/logo.svg (the gear-and-wrench mark from src/brand/mark.mjs) and renders the PNG app icons with
// headless Chromium (Playwright). Run: node scripts/make-icons.mjs
// Playwright is not a project dependency: point NODE_PATH at a folder that has it, e.g.
//   NODE_PATH=/path/with/node_modules node scripts/make-icons.mjs
import { writeFileSync, mkdirSync } from 'node:fs'
import { createRequire } from 'node:module'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = join(dirname(fileURLToPath(import.meta.url)), '..')
import { markInner, markSvg, NAVY, AMBER } from '../src/brand/mark.mjs'

/** Square icon: navy field, mark scaled to (1 - 2*pad) of the side. */
function iconSvg(size, { pad = 0.11, rounded = 0, bg = NAVY } = {}) {
  const inset = size * pad, w = size - inset * 2
  return `<svg xmlns="http://www.w3.org/2000/svg" width="${size}" height="${size}" viewBox="0 0 ${size} ${size}"><rect width="${size}" height="${size}" rx="${rounded}" fill="${bg}"/><svg x="${inset}" y="${inset}" width="${w}" height="${w}" viewBox="0 0 100 100">${markInner({ navy: bg })}</svg></svg>`
}

// Favicon / header logo: transparent background; the wrench keeps its navy edge so it reads on light and dark.
writeFileSync(join(root, 'public', 'logo.svg'), markSvg() + '\n')
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
await page.setContent(`<body style="margin:0;background:${NAVY};font-family:'Arial Narrow',Arial,sans-serif"><div style="display:flex;align-items:center;justify-content:center;gap:40px;height:500px;color:#f5f7fa">${markSvg({ size: 260 })}<div><div style="font-size:84px;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;line-height:1">Millwright <span style="color:${AMBER}">KB</span></div><div style="font-size:30px;color:rgba(245,247,250,0.75);margin-top:10px">The trade's reference, in your pocket.</div></div></div></body>`)
await page.screenshot({ path: join(root, 'docs/store/feature-graphic.png'), clip: { x: 0, y: 0, width: 1024, height: 500 } })
console.log('wrote docs/store/feature-graphic.png')
await browser.close()
