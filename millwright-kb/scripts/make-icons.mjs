// Generates the PWA / app icons (PNG) without any image library: navy square, amber ring, dark hub.
// Run: node scripts/make-icons.mjs
import { writeFileSync } from 'node:fs'
import { deflateSync } from 'node:zlib'

function crc32(buf) {
  let c, crc = 0xffffffff
  for (let n = 0; n < buf.length; n++) {
    c = (crc ^ buf[n]) & 0xff
    for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1
    crc = (crc >>> 8) ^ c
  }
  return (crc ^ 0xffffffff) >>> 0
}
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length)
  const td = Buffer.concat([Buffer.from(type), data])
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td))
  return Buffer.concat([len, td, crc])
}
function png(size, pixel) {
  const raw = Buffer.alloc((size * 4 + 1) * size)
  for (let y = 0; y < size; y++) {
    raw[y * (size * 4 + 1)] = 0
    for (let x = 0; x < size; x++) {
      const [r, g, b] = pixel(x, y)
      const o = y * (size * 4 + 1) + 1 + x * 4
      raw[o] = r; raw[o + 1] = g; raw[o + 2] = b; raw[o + 3] = 255
    }
  }
  const ihdr = Buffer.alloc(13)
  ihdr.writeUInt32BE(size, 0); ihdr.writeUInt32BE(size, 4)
  ihdr[8] = 8; ihdr[9] = 6; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk('IHDR', ihdr), chunk('IDAT', deflateSync(raw)), chunk('IEND', Buffer.alloc(0)),
  ])
}

const NAVY = [15, 23, 42], AMBER = [245, 158, 11], LIGHT = [248, 250, 252]
function gear(size) {
  const c = size / 2
  return (x, y) => {
    const dx = x + 0.5 - c, dy = y + 0.5 - c
    const r = Math.hypot(dx, dy) / size
    const a = Math.atan2(dy, dx)
    const tooth = Math.cos(a * 8) > 0.2   // 8 teeth
    if (r < 0.11) return NAVY              // bore
    if (r < 0.16) return LIGHT             // hub ring
    if (r < 0.30) return AMBER             // body
    if (r < 0.38 && tooth) return AMBER    // teeth
    return NAVY
  }
}
for (const size of [180, 192, 512]) writeFileSync(new URL(`../public/icon-${size}.png`, import.meta.url), png(size, gear(size)))
// Maskable icon: the platform may crop to a circle or rounded square inside the centre 80%,
// so draw the gear smaller on a solid navy field.
function maskable(size) {
  const inner = gear(size * 0.8), off = size * 0.1
  return (x, y) => (x < off || y < off || x >= size - off || y >= size - off) ? NAVY : inner(x - off, y - off)
}
writeFileSync(new URL('../public/icon-maskable-512.png', import.meta.url), png(512, maskable(512)))
console.log('wrote public/icon-180.png, icon-192.png, icon-512.png, icon-maskable-512.png')
