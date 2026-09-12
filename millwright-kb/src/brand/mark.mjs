// The Millwright KB mark: a bold eight-tooth gear with a steel adjustable wrench across it (the
// 'crescent' variant chosen from the September 2026 candidates; the other three are kept here so
// they can be swapped in by name). One source of truth for src/components/Logo.tsx and
// scripts/make-icons.mjs. viewBox 0 0 100 100.
export const MARK_VARIANT = 'crescent'
export const NAVY = '#0f1b2d', AMBER = '#f4a11d', STEEL = '#e6ecf2'
const P = Math.PI / 180
const f2 = (n) => (Math.round(n * 100) / 100).toString()
export function gearPath(cx, cy, ro, rr, n, tipHalf = 8.5, baseHalf = 13.5) {
  const pts = []
  for (let i = 0; i < n; i++) {
    const a = i * 360 / n
    for (const [r, d] of [[rr, -baseHalf], [ro, -tipHalf], [ro, tipHalf], [rr, baseHalf]]) pts.push(`${f2(cx + r * Math.cos((a + d) * P))},${f2(cy + r * Math.sin((a + d) * P))}`)
  }
  return 'M' + pts.join(' L') + ' Z'
}
const circlePath = (cx, cy, r) => `M${cx - r},${cy} a${r},${r} 0 1,0 ${2 * r},0 a${r},${r} 0 1,0 ${-2 * r},0 Z`
const hexPath = (cx, cy, r) => 'M' + [0, 1, 2, 3, 4, 5].map((i) => `${f2(cx + r * Math.cos((i * 60 + 30) * P))},${f2(cy + r * Math.sin((i * 60 + 30) * P))}`).join(' L') + ' Z'
/** Combination wrench along the x axis, centred at 0,0: open end at +x, box end at -x. Filled body + hole paths (evenodd). */
function comboWrench(len = 104, w = 13) {
  const h = len / 2, ro = 16.5, rb = 14.5
  const body = `M${-h + rb},${-w / 2} L${h - ro},${-w / 2} L${h - ro},${w / 2} L${-h + rb},${w / 2} Z ` + circlePath(h - ro, 0, ro) + ' ' + circlePath(-h + rb, 0, rb)
  // open-end jaw: a U slot tilted 15°; box end: a 12-point hole drawn as a hexagon
  const jx = h - ro, slotW = 12, slotL = 22
  const jaw = `<path d="M${jx - 2},${-slotW / 2} L${jx + slotL},${-slotW / 2} L${jx + slotL},${slotW / 2} L${jx - 2},${slotW / 2} Z" transform="rotate(-15 ${jx} 0)"/>`
  return { body, jaw, hole: hexPath(-h + rb, 0, 7.2) }
}
/** Adjustable (crescent) wrench along +x: handle at -x, head at +x with the jaw opening upward. */
function adjustableWrench() {
  const body = 'M-56,-5.5 L10,-7.5 L18,-15 L30,-25 L41,-25 L47,-17 L47,-8.5 L33,-8.5 L33,0.5 L47,0.5 L47,10 L39,17 L22,17 L10,7.5 L-56,5.5 Z'
  const jaw = '<path d="M33,-8.5 L48,-8.5 L48,0.5 L33,0.5 Z"/>'
  return { body, jaw, hole: circlePath(25, 9, 3.6) }
}
/** variant: 'badge' | 'crescent' | 'cutout' | 'letters'. Colours: amber gear, steel wrench, navy field. */
/** The mark's inner markup (no <svg> wrapper) for a 0 0 100 100 viewBox. */
export function markInner({ variant = MARK_VARIANT, amber = AMBER, steel = STEEL, navy = NAVY, id = 'm' } = {}) {
  const gear = (ro, rr, bore) => `<path d="${gearPath(50, 50, ro, rr, 8)} ${circlePath(50, 50, bore)}" fill="${amber}" fill-rule="evenodd"/>`
  const wrenchGroup = (wr, transform, fill, outline) => `<mask id="${id}-w" maskUnits="userSpaceOnUse" x="-80" y="-40" width="160" height="80"><path d="${wr.body}" fill="#fff"/><g fill="#000">${wr.jaw}<path d="${wr.hole}"/></g></mask>` +
    `<g transform="${transform}"><rect x="-80" y="-40" width="160" height="80" fill="${fill}" mask="url(#${id}-w)"/>` +
    (outline ? `<g fill="none" stroke="${outline}" stroke-width="2.2" stroke-linejoin="round"><path d="${wr.body}"/>${wr.jaw}<path d="${wr.hole}"/></g>` : '') + '</g>'
  let inner = ''
  if (variant === 'badge') inner = `<circle cx="50" cy="50" r="49" fill="${navy}"/><circle cx="50" cy="50" r="49" fill="none" stroke="${amber}" stroke-width="2"/>` + gear(42, 34, 12) + wrenchGroup(comboWrench(96, 12), 'translate(50 50) rotate(-45)', steel, navy)
  if (variant === 'crescent') inner = gear(47, 38, 13) + wrenchGroup(adjustableWrench(), 'translate(50 50) rotate(-45) translate(4 0)', steel, navy)
  if (variant === 'cutout') { const wr = comboWrench(84, 13); inner = `<mask id="${id}-c"><rect width="100" height="100" fill="#fff"/><g transform="translate(50 50) rotate(-45)"><path d="${wr.body}" fill="#000"/><g fill="#fff">${wr.jaw}<path d="${wr.hole}"/></g></g></mask><g mask="url(#${id}-c)"><path d="${gearPath(50, 50, 47, 38, 8)}" fill="${amber}"/></g>` }
  if (variant === 'letters') inner = gear(46, 37, 12) + wrenchGroup(comboWrench(96, 12), 'translate(50 44) rotate(-45)', steel, navy) + `<rect x="18" y="66" width="64" height="18" rx="3" fill="${navy}"/><text x="50" y="80" text-anchor="middle" font-family="Barlow Semi Condensed, Arial Narrow, sans-serif" font-weight="800" font-size="15" letter-spacing="1" fill="${amber}">MKB</text>`
  return inner
}
/** Standalone SVG of the mark. `size` sets width/height; `outline` colours the wrench edge (the field it sits on). */
export function markSvg({ size, ...opts } = {}) {
  const sz = size ? ` width="${size}" height="${size}"` : ''
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"${sz}>${markInner(opts)}</svg>`
}
