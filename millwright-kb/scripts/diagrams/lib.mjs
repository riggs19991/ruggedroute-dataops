// Tiny SVG drawing helpers for the knowledge-base diagrams.
// Diagrams are authored at 480-520 px wide with 13-14 px text so they stay legible on a phone.
import { mkdirSync, writeFileSync } from 'node:fs'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

export const OUT = join(dirname(fileURLToPath(import.meta.url)), '..', '..', 'public', 'img')

export const C = {
  ink: '#1a2233', muted: '#5b6577', line: '#94a3b8', light: '#e2e8f0',
  accent: '#f59e0b', accentDark: '#b45309', soft: '#fff4d6',
  blue: '#0b5fa5', blueSoft: '#dbeafe', red: '#b91c1c', redSoft: '#fee2e2',
  green: '#166534', greenSoft: '#dcfce7', steel: '#cbd5e1', steelDark: '#64748b',
  paper: '#ffffff', grey: '#f1f5f9', brass: '#d4a017', copper: '#b87333', weld: '#f8b878',
}

const esc = (s) => String(s).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')

const attrs = (o) => Object.entries(o).filter(([, v]) => v !== undefined && v !== null && v !== false)
  .map(([k, v]) => ` ${k.replace(/[A-Z]/g, (m) => '-' + m.toLowerCase())}="${esc(v)}"`).join('')

export function svg(w, h, body, { title = '' } = {}) {
  const over = pending.filter((t) => t.x0 < 2 || t.x1 > w - 2 || t.y0 < 0 || t.y1 > h)
  if (over.length) console.warn(`  overflow in "${title}": ` + over.map((t) => JSON.stringify(t.s.slice(0, 40)) + ` [${Math.round(t.x0)}..${Math.round(t.x1)}, y ${Math.round(t.y0)}..${Math.round(t.y1)}]`).join('; '))
  pending.length = 0
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" width="${w}" height="${h}" font-family="system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, sans-serif" font-size="13" fill="${C.ink}">
<title>${esc(title)}</title>
<defs>
<marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker>
<marker id="dot" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="5" markerHeight="5"><circle cx="5" cy="5" r="4" fill="context-stroke"/></marker>
<pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><line x1="0" y1="0" x2="0" y2="7" stroke="${C.steelDark}" stroke-width="1.2"/></pattern>
<pattern id="hatch2" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(-45)"><line x1="0" y1="0" x2="0" y2="7" stroke="${C.blue}" stroke-width="1.2"/></pattern>
<pattern id="dots" width="6" height="6" patternUnits="userSpaceOnUse"><circle cx="3" cy="3" r="1" fill="${C.steelDark}"/></pattern>
</defs>
<rect width="${w}" height="${h}" fill="${C.paper}"/>
${Array.isArray(body) ? body.flat(Infinity).join('\n') : body}
</svg>`
}

const pending = []
const estW = (str, size, weight) => String(str).length * size * (weight && weight >= 600 ? 0.6 : 0.53)

export function text(x, y, s, { size = 13, anchor = 'start', weight, fill = C.ink, angle, italic, family, baseline, vcenter } = {}) {
  const lines = String(s).split('\n')
  const lh = size * 1.25
  const y0 = vcenter ? y - (lines.length - 1) * lh / 2 + size * 0.35 : y
  if (!angle) for (let i = 0; i < lines.length; i++) {
    const w = estW(lines[i], size, weight)
    const x0 = anchor === 'middle' ? x - w / 2 : anchor === 'end' ? x - w : x
    pending.push({ s: lines[i], x0, x1: x0 + w, y0: y0 + i * lh - size, y1: y0 + i * lh + 3 })
  }
  const t = attrs({ x, y: y0, fontSize: size, textAnchor: anchor, fontWeight: weight, fill, fontStyle: italic ? 'italic' : undefined, fontFamily: family, dominantBaseline: baseline, transform: angle ? `rotate(${angle} ${x} ${y0})` : undefined })
  if (lines.length === 1) return `<text${t}>${esc(s)}</text>`
  return `<text${t}>` + lines.map((l, i) => `<tspan x="${x}" dy="${i === 0 ? 0 : lh}">${esc(l)}</tspan>`).join('') + '</text>'
}

/** Rounded box with centred (multi-line) label. */
export function box(x, y, w, h, s, { fill = C.grey, stroke = C.ink, size = 11.5, weight, rx = 6, color = C.ink, dash } = {}) {
  return rect(x, y, w, h, { fill, stroke, rx, dash }) + text(x + w / 2, y + h / 2, s, { anchor: 'middle', size, weight, fill: color, vcenter: true })
}

/** Numbered callout marker at a point; pair with legend(). */
export function callout(n, x, y, { r = 9, fill = C.blue } = {}) {
  return circle(x, y, r, { fill, stroke: C.paper, width: 1.5 }) + text(x, y + 4, String(n), { anchor: 'middle', size: 11, weight: 700, fill: '#fff' })
}

/** Legend list of numbered callouts: items = ['text', ...] starting at 1. */
export function legend(x, y, items, { size = 11.5, gap = 17, fill = C.blue, start = 1 } = {}) {
  let yy = y
  return items.map((s, i) => { const n = String(s).split('\n').length; const out = callout(i + start, x + 9, yy - 4, { r: 8, fill }) + text(x + 24, yy, s, { size }); yy += gap + (n - 1) * size * 1.25; return out }).join('\n')
}

export function note(x, y, s, opts = {}) { return text(x, y, s, { size: 11, fill: C.muted, ...opts }) }

export function line(x1, y1, x2, y2, { stroke = C.ink, width = 1.5, dash, arrow, cap = 'round', opacity } = {}) {
  return `<line${attrs({ x1, y1, x2, y2, stroke, strokeWidth: width, strokeDasharray: dash, strokeLinecap: cap, opacity, markerEnd: arrow === 'end' || arrow === 'both' ? 'url(#arr)' : undefined, markerStart: arrow === 'start' || arrow === 'both' ? 'url(#arr)' : undefined })}/>`
}

export function rect(x, y, w, h, { fill = C.paper, stroke = C.ink, width = 1.5, rx, dash, opacity } = {}) {
  return `<rect${attrs({ x, y, width: w, height: h, fill, stroke, strokeWidth: width, rx, strokeDasharray: dash, opacity })}/>`
}

export function circle(cx, cy, r, { fill = C.paper, stroke = C.ink, width = 1.5, dash, opacity } = {}) {
  return `<circle${attrs({ cx, cy, r, fill, stroke, strokeWidth: width, strokeDasharray: dash, opacity })}/>`
}

export function ellipse(cx, cy, rx, ry, { fill = C.paper, stroke = C.ink, width = 1.5, dash } = {}) {
  return `<ellipse${attrs({ cx, cy, rx, ry, fill, stroke, strokeWidth: width, strokeDasharray: dash })}/>`
}

export function path(d, { fill = 'none', stroke = C.ink, width = 1.5, dash, arrow, join = 'round', cap = 'round', opacity } = {}) {
  return `<path${attrs({ d, fill, stroke, strokeWidth: width, strokeDasharray: dash, strokeLinejoin: join, strokeLinecap: cap, opacity, markerEnd: arrow === 'end' || arrow === 'both' ? 'url(#arr)' : undefined, markerStart: arrow === 'start' || arrow === 'both' ? 'url(#arr)' : undefined })}/>`
}

export function poly(points, opts = {}) {
  const d = points.map((p, i) => (i ? 'L' : 'M') + p[0] + ',' + p[1]).join(' ') + (opts.open ? '' : ' Z')
  return path(d, { fill: C.paper, ...opts })
}

export function g(children, { transform, opacity } = {}) {
  return `<g${attrs({ transform, opacity })}>${(Array.isArray(children) ? children.flat(Infinity) : [children]).join('\n')}</g>`
}

/** Dimension line between two points with arrowheads and a label, offset perpendicular by `off`. */
export function dim(x1, y1, x2, y2, label, { off = 0, size = 12, ext = true, fill = C.ink, side = 1 } = {}) {
  const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy) || 1
  const nx = -dy / L * off * side, ny = dx / L * off * side
  const ax = x1 + nx, ay = y1 + ny, bx = x2 + nx, by = y2 + ny
  const out = []
  if (ext && off) { out.push(line(x1, y1, ax + nx / Math.abs(off || 1) * 4, ay + ny / Math.abs(off || 1) * 4, { width: 0.8, stroke: C.muted })); out.push(line(x2, y2, bx + nx / Math.abs(off || 1) * 4, by + ny / Math.abs(off || 1) * 4, { width: 0.8, stroke: C.muted })) }
  out.push(line(ax, ay, bx, by, { width: 1, arrow: 'both', stroke: fill }))
  const mx = (ax + bx) / 2, my = (ay + by) / 2
  const horizontal = Math.abs(dx) >= Math.abs(dy)
  out.push(text(mx + (horizontal ? 0 : 6 * (side)), my + (horizontal ? -4 : 4), label, { size, anchor: horizontal ? 'middle' : (side > 0 ? 'start' : 'end'), fill }))
  return out.join('\n')
}

/** Leader: text at (tx,ty) with an arrow pointing to (x,y). */
export function leader(x, y, tx, ty, label, { size = 12, anchor, fill = C.ink, weight } = {}) {
  const a = anchor ?? (tx < x ? 'end' : 'start')
  const sx = a === 'end' ? tx + 3 : (a === 'start' ? tx - 3 : tx)
  return line(sx, ty - 4, x, y, { width: 1, arrow: 'end', stroke: fill }) + text(tx, ty, label, { size, anchor: a, fill, weight })
}

export function arc(cx, cy, r, a1, a2, opts = {}) {
  const p = (a) => [cx + r * Math.cos(a * Math.PI / 180), cy + r * Math.sin(a * Math.PI / 180)]
  const [x1, y1] = p(a1), [x2, y2] = p(a2)
  const large = Math.abs(a2 - a1) > 180 ? 1 : 0, sweep = a2 > a1 ? 1 : 0
  return path(`M${x1},${y1} A${r},${r} 0 ${large} ${sweep} ${x2},${y2}`, opts)
}

/** Angle annotation: arc between two directions from vertex, with label. */
export function angle(cx, cy, r, a1, a2, label, { size = 12, fill = C.blue } = {}) {
  const mid = (a1 + a2) / 2 * Math.PI / 180
  return arc(cx, cy, r, a1, a2, { stroke: fill, width: 1 }) + text(cx + (r + 12) * Math.cos(mid), cy + (r + 12) * Math.sin(mid) + 4, label, { size, anchor: 'middle', fill })
}

export function hatchRect(x, y, w, h, opts = {}) { return rect(x, y, w, h, { fill: 'url(#hatch)', ...opts }) }

export function plate(x, y, w, h, opts = {}) { return rect(x, y, w, h, { fill: C.steel, ...opts }) }

/** Simple table drawn in SVG: rows = [[cells]], colWidths, rowH. */
export function table(x, y, rows, colW, { rowH = 22, size = 12, head = true, stroke = C.line } = {}) {
  const out = []
  const W = colW.reduce((a, b) => a + b, 0)
  rows.forEach((r, i) => {
    const yy = y + i * rowH
    if (head && i === 0) out.push(rect(x, yy, W, rowH, { fill: C.grey, stroke }))
    else out.push(rect(x, yy, W, rowH, { fill: C.paper, stroke }))
    let xx = x
    r.forEach((c, j) => { out.push(text(xx + 6, yy + rowH * 0.68, c, { size, weight: head && i === 0 ? 600 : undefined })); xx += colW[j] })
  })
  return out.join('\n')
}

/** Caption strip at the bottom of a figure. */
export function caption(w, h, s, { size = 12 } = {}) { return text(w / 2, h - 8, s, { size, anchor: 'middle', fill: C.muted, italic: true }) }

/** Axis helpers for simple charts. */
export function chart({ x, y, w, h, xmin, xmax, ymin, ymax, xlabel, ylabel, xticks = [], yticks = [], xfmt = (v) => v, yfmt = (v) => v, grid = true }) {
  const sx = (v) => x + (v - xmin) / (xmax - xmin) * w
  const sy = (v) => y + h - (v - ymin) / (ymax - ymin) * h
  const out = [rect(x, y, w, h, { fill: C.paper, stroke: C.line, width: 1 })]
  for (const t of yticks) { if (grid) out.push(line(x, sy(t), x + w, sy(t), { stroke: C.light, width: 1 })); out.push(text(x - 6, sy(t) + 4, yfmt(t), { size: 11, anchor: 'end', fill: C.muted })) }
  for (const t of xticks) { if (grid) out.push(line(sx(t), y, sx(t), y + h, { stroke: C.light, width: 1 })); out.push(text(sx(t), y + h + 14, xfmt(t), { size: 11, anchor: 'middle', fill: C.muted })) }
  if (xlabel) out.push(text(x + w / 2, y + h + 30, xlabel, { size: 12, anchor: 'middle', fill: C.muted }))
  if (ylabel) out.push(text(x - 34, y + h / 2, ylabel, { size: 12, anchor: 'middle', fill: C.muted, angle: -90 }))
  return { sx, sy, el: out.join('\n') }
}

export function write(rel, content) {
  const p = join(OUT, rel)
  mkdirSync(dirname(p), { recursive: true })
  writeFileSync(p, content)
  return rel
}

/** Register figures: modules push {file, alt, svg} and the runner writes them. */
export const registry = []
export function fig(file, alt, svgString) { registry.push({ file, alt }); write(file, svgString); return file }
