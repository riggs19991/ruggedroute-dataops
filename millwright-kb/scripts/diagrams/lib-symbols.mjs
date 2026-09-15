// Standard drawing symbols shared by the drawings modules: ISO 1219 fluid power, ISA 5.1 P&ID,
// NEMA ICS 19 / IEC 60617 electrical, and piping-isometric fittings. Every symbol is drawn once here
// so a symbol sheet and a circuit diagram show exactly the same shape. Not a figure module (run.mjs
// skips lib*.mjs). Coordinates: symbols are centred on (x, y) unless noted; sizes are in px on the
// 500 px canvas.
import { text, line, rect, circle, path, poly, g, C } from './lib.mjs'

const P = Math.PI / 180
export const ink = C.ink

// ================= ISO 1219 fluid power =================
export const LINE = {
  work: { width: 1.6 }, pilot: { width: 1.2, dash: '9 4' }, drain: { width: 1.1, dash: '3 3' }, enclosure: { width: 1, dash: '10 3 2 3' },
}
export const fl = (x1, y1, x2, y2, kind = 'work', extra = {}) => line(x1, y1, x2, y2, { ...LINE[kind], ...extra })
export const junction = (x, y) => circle(x, y, 2.6, { fill: C.ink, stroke: 'none' })
/** Reservoir: vented (open top), pressurised (closed box), return above or below the fluid line. */
export function tank(x, y, { w = 22, h = 12, pressurised = false, aboveLevel = false, stub = 10 } = {}) {
  const out = [line(x, y - stub, x, aboveLevel ? y + 3 : y + h - 3, { width: 1.6 })]
  if (pressurised) out.push(rect(x - w / 2, y, w, h, { rx: 2 }))
  else out.push(path(`M${x - w / 2},${y} L${x - w / 2},${y + h} L${x + w / 2},${y + h} L${x + w / 2},${y}`, { width: 1.5 }))
  return out
}
export const pressureSource = (x, y, r = 8) => [circle(x, y, r), circle(x, y, 2.5, { fill: C.ink, stroke: 'none' })]
export const electricMotor = (x, y, r = 10) => [circle(x, y, r), text(x, y + 4, 'M', { anchor: 'middle', size: 11, weight: 700 })]
export const airSource = (x, y, r = 8) => [circle(x, y, r), poly([[x - 4, y - 4], [x + 4, y - 4], [x, y + 4]], { fill: 'none', width: 1.2 })]
const tri = (x, y, r, dirDeg, filled) => { const a = dirDeg * P; const tip = [x + r * Math.cos(a), y + r * Math.sin(a)]; const bx = x + (r - 11) * Math.cos(a), by = y + (r - 11) * Math.sin(a); const nx = -Math.sin(a) * 6, ny = Math.cos(a) * 6; return poly([tip, [bx + nx, by + ny], [bx - nx, by - ny]], { fill: filled ? C.ink : C.paper, width: 1.2 }) }
/** Pump: triangle points out of the circle. hydraulic = filled triangle, pneumatic = open. */
export function pump(x, y, { r = 16, variable = false, bidir = false, comp = false, drain = false, pneumatic = false, ls = false } = {}) {
  const out = [circle(x, y, r), tri(x, y, r, -90, !pneumatic)]
  if (bidir) out.push(tri(x, y, r, 90, !pneumatic))
  if (variable) out.push(line(x - r - 5, y + r + 5, x + r + 5, y - r - 5, { width: 1.2, arrow: 'end' }))
  if (comp) out.push(line(x + r + 5, y - r - 5, x + r + 16, y - r - 5, { width: 1, dash: '4 2' }), rect(x + r + 16, y - r - 12, 12, 14), line(x + r + 18, y - r + 1, x + r + 26, y - r - 11, { width: 1.2, arrow: 'end' }))
  if (ls) out.push(fl(x + r + 22, y - r - 5, x + r + 22, y + 6, 'pilot'), text(x + r + 26, y + 10, 'LS', { size: 8.5 }))
  if (drain) out.push(fl(x - r * 0.6, y + r * 0.8, x - r * 0.6, y + r + 14, 'drain'))
  return out
}
/** Motor: triangle points into the circle. */
export function hmotor(x, y, { r = 16, variable = false, bidir = false, pneumatic = false, drain = false } = {}) {
  const out = [circle(x, y, r), tri(x, y, r, 90, !pneumatic).replace('points', 'points')]
  // inward triangle: draw with tip at centre side
  out[1] = poly([[x, y - r + 11], [x - 6, y - r], [x + 6, y - r]], { fill: pneumatic ? C.paper : C.ink, width: 1.2 })
  if (bidir) out.push(poly([[x, y + r - 11], [x - 6, y + r], [x + 6, y + r]], { fill: pneumatic ? C.paper : C.ink, width: 1.2 }))
  if (variable) out.push(line(x - r - 5, y + r + 5, x + r + 5, y - r - 5, { width: 1.2, arrow: 'end' }))
  if (drain) out.push(fl(x - r * 0.6, y + r * 0.8, x - r * 0.6, y + r + 14, 'drain'))
  return out
}
export const pumpMotor = (x, y, r = 16) => [circle(x, y, r), tri(x, y, r, -90, true), poly([[x, y + r - 11], [x - 6, y + r], [x + 6, y + r]], { fill: C.ink, width: 1.2 })]
/** Cylinder: barrel with piston and rod. single = spring return, doubleRod, cushion (adjustable), telescopic. */
export function cylinder(x, y, { w = 56, h = 22, single = false, spring = false, doubleRod = false, cushion = false, telescopic = false, rodLen = 22, piston = 0.4 } = {}) {
  const x0 = x - w / 2, y0 = y - h / 2
  const out = [rect(x0, y0, w, h)]
  if (telescopic) { out.push(rect(x0 + w * 0.3, y0 + 4, w * 0.5, h - 8), rect(x0 + w * 0.6, y0 + 7, w * 0.3, h - 14), line(x0 + w * 0.9, y, x0 + w + rodLen, y, { width: 3 })); return out }
  const px = x0 + w * piston
  out.push(rect(px, y0, 5, h, { fill: C.ink }))
  out.push(line(px + 5, y, x0 + w + rodLen, y, { width: 3 }))
  if (doubleRod) out.push(line(x0 - rodLen, y, px, y, { width: 3 }))
  if (single) { out.push(line(x0 + w - 4, y0 + 2, x0 + w - 4, y0 + h - 2, { width: 1.6 })); if (spring) out.push(path(`M${px + 6},${y} l4,-6 l4,12 l4,-12 l4,12 l4,-12 l4,12 l4,-6`, { width: 1.1 })) }
  if (cushion) out.push(rect(px - 9, y0 + 5, 7, h - 10, { fill: C.paper }), rect(px + 7, y0 + 5, 7, h - 10, { fill: C.paper }), line(px - 14, y0 + h + 6, px - 2, y0 - 6, { width: 1, arrow: 'end' }))
  if (!single && !doubleRod) out.push(line(x0 - 6, y0 + 6, x0 - 6, y0 + h - 6, { width: 0 }))
  return out
}
/** One directional-valve position box with its flow pattern. Ports left-to-right at the bottom: P T (2-port), 1 2 3, P T A B ... */
const arrowIn = (x1, y1, x2, y2) => line(x1, y1, x2, y2, { width: 1.5, arrow: 'end' })
const blockT = (x, y, up) => line(x - 5, y + (up ? -8 : 8), x + 5, y + (up ? -8 : 8), { width: 2 })
/** Draws the inside of a position box of width w, height h, top-left (x,y), for a 4-port (P T bottom, A B top) valve. */
export function pos4(x, y, w, h, kind) {
  const P_ = [x + w * 0.28, y + h], T_ = [x + w * 0.72, y + h], A_ = [x + w * 0.28, y], B_ = [x + w * 0.72, y]
  const stubs = [P_, T_].map((p) => line(p[0], p[1], p[0], p[1] + 8, { width: 1.5 })).concat([A_, B_].map((p) => line(p[0], p[1], p[0], p[1] - 8, { width: 1.5 })))
  const box = rect(x, y, w, h)
  const c = [x + w / 2, y + h / 2]
  const map = {
    parallel: [arrowIn(P_[0], P_[1], A_[0], A_[1]), arrowIn(B_[0], B_[1], T_[0], T_[1])],
    cross: [arrowIn(P_[0], P_[1], B_[0], B_[1]), arrowIn(A_[0], A_[1], T_[0], T_[1])],
    closed: [blockT(P_[0], P_[1], true), blockT(T_[0], T_[1], true), blockT(A_[0], A_[1], false), blockT(B_[0], B_[1], false)],
    open: [line(A_[0], A_[1], c[0], c[1], { width: 1.5 }), line(B_[0], B_[1], c[0], c[1], { width: 1.5 }), line(P_[0], P_[1], c[0], c[1], { width: 1.5 }), arrowIn(c[0], c[1], T_[0], T_[1]), junction(c[0], c[1])],
    tandem: [arrowIn(P_[0], P_[1], T_[0], T_[1] - 0.01).replace('', ''), blockT(A_[0], A_[1], false), blockT(B_[0], B_[1], false)],
    float: [blockT(P_[0], P_[1], true), line(A_[0], A_[1], c[0], c[1] + 4, { width: 1.5 }), line(B_[0], B_[1], c[0], c[1] + 4, { width: 1.5 }), arrowIn(c[0], c[1] + 4, T_[0], T_[1]), junction(c[0], c[1] + 4)],
    regen: [blockT(T_[0], T_[1], true), line(P_[0], P_[1], c[0], c[1] - 4, { width: 1.5 }), arrowIn(c[0], c[1] - 4, A_[0], A_[1]), arrowIn(c[0], c[1] - 4, B_[0], B_[1]), junction(c[0], c[1] - 4)],
  }
  if (kind === 'tandem') map.tandem = [path(`M${P_[0]},${P_[1]} L${P_[0]},${y + h * 0.55} L${T_[0]},${y + h * 0.45} L${T_[0]},${T_[1]}`, { width: 1.5, arrow: 'end' }), blockT(A_[0], A_[1], false), blockT(B_[0], B_[1], false)]
  return [box, ...stubs, ...(map[kind] || [])]
}
/** 2- and 3-port position boxes (pneumatic 3/2 or hydraulic 2/2). ports: 2 -> bottom 1 (P), top 2 (A); 3 -> bottom 1 and 3, top 2. */
export function posN(x, y, w, h, ports, kind) {
  const bot = ports === 2 ? [[x + w / 2, y + h]] : [[x + w * 0.28, y + h], [x + w * 0.72, y + h]]
  const top = [[x + w / 2, y]]
  const stubs = [...bot.map((p) => line(p[0], p[1], p[0], p[1] + 8, { width: 1.5 })), ...top.map((p) => line(p[0], p[1], p[0], p[1] - 8, { width: 1.5 }))]
  const out = [rect(x, y, w, h), ...stubs]
  if (kind === 'pass') out.push(arrowIn(bot[0][0], bot[0][1], top[0][0], top[0][1]), ...(ports === 3 ? [blockT(bot[1][0], bot[1][1], true)] : []))
  if (kind === 'blocked') out.push(...bot.map((p) => blockT(p[0], p[1], true)), blockT(top[0][0], top[0][1], false))
  if (kind === 'exhaust') out.push(blockT(bot[0][0], bot[0][1], true), arrowIn(top[0][0], top[0][1], bot[1][0], bot[1][1]))
  return out
}
/** 5-port pneumatic position: bottom 5 1 3, top 4 2. */
export function pos5(x, y, w, h, kind) {
  const b = [[x + w * 0.2, y + h], [x + w * 0.5, y + h], [x + w * 0.8, y + h]], t = [[x + w * 0.35, y], [x + w * 0.65, y]]
  const out = [rect(x, y, w, h), ...b.map((p) => line(p[0], p[1], p[0], p[1] + 8, { width: 1.5 })), ...t.map((p) => line(p[0], p[1], p[0], p[1] - 8, { width: 1.5 }))]
  if (kind === 'a') out.push(arrowIn(b[1][0], b[1][1], t[0][0], t[0][1]), arrowIn(t[1][0], t[1][1], b[2][0], b[2][1]), blockT(b[0][0], b[0][1], true))
  if (kind === 'b') out.push(arrowIn(b[1][0], b[1][1], t[1][0], t[1][1]), arrowIn(t[0][0], t[0][1], b[0][0], b[0][1]), blockT(b[2][0], b[2][1], true))
  if (kind === 'closed') out.push(...b.map((p) => blockT(p[0], p[1], true)), ...t.map((p) => blockT(p[0], p[1], false)))
  if (kind === 'exhaust') out.push(blockT(b[1][0], b[1][1], true), arrowIn(t[0][0], t[0][1], b[0][0], b[0][1]), arrowIn(t[1][0], t[1][1], b[2][0], b[2][1]))
  if (kind === 'pressure') out.push(...t.map((p) => arrowIn(b[1][0], b[1][1], p[0], p[1])), blockT(b[0][0], b[0][1], true), blockT(b[2][0], b[2][1], true))
  return out
}
/** Operators attached to a valve stack. side: 'left' | 'right'; x is the envelope edge, y the vertical centre. */
export function operator(kind, x, y, side = 'left', { label } = {}) {
  const s = side === 'left' ? -1 : 1, x0 = x + s * 2
  const out = []
  switch (kind) {
    case 'solenoid': out.push(rect(x0 + (s < 0 ? -16 : 0), y - 8, 16, 16), line(x0 + (s < 0 ? -16 : 0), y + 8, x0 + (s < 0 ? 0 : 16), y - 8, { width: 1.2 })); break
    case 'proportional': out.push(rect(x0 + (s < 0 ? -16 : 0), y - 8, 16, 16), line(x0 + (s < 0 ? -16 : 0), y + 8, x0 + (s < 0 ? 0 : 16), y - 8, { width: 1.2 }), line(x0 + (s < 0 ? -20 : 4), y + 12, x0 + (s < 0 ? -4 : 20), y - 12, { width: 1, arrow: 'end' })); break
    case 'spring': out.push(path(`M${x0},${y} l${s * 3},-6 l${s * 3},12 l${s * 3},-12 l${s * 3},12 l${s * 3},-12 l${s * 3},6`, { width: 1.2 })); break
    case 'lever': out.push(line(x0, y, x0 + s * 6, y, { width: 1.5 }), line(x0 + s * 6, y, x0 + s * 16, y - 14, { width: 2 }), circle(x0 + s * 6, y, 2.2, { fill: C.ink })); break
    case 'pushbutton': out.push(line(x0, y, x0 + s * 8, y, { width: 1.5 }), rect(x0 + (s < 0 ? -14 : 8), y - 7, 6, 14)); break
    case 'pedal': out.push(line(x0, y, x0 + s * 8, y, { width: 1.5 }), path(`M${x0 + s * 8},${y - 7} L${x0 + s * 8},${y + 7} L${x0 + s * 20},${y + 3}`, { width: 1.8 })); break
    case 'roller': out.push(line(x0, y, x0 + s * 8, y, { width: 1.5 }), line(x0 + s * 8, y - 8, x0 + s * 8, y + 8, { width: 1.8 }), circle(x0 + s * 12, y, 4)); break
    case 'pilot': out.push(line(x0, y - 8, x0 + s * 12, y - 8, { width: 1.2 }), line(x0 + s * 12, y - 8, x0 + s * 12, y + 8, { width: 1.2 }), line(x0 + s * 12, y + 8, x0, y + 8, { width: 1.2 }), fl(x0 + s * 12, y, x0 + s * 24, y, 'pilot')); break
    case 'detent': out.push(path(`M${x0},${y - 8} l${s * 10},0 l0,16 l${s * -10},0`, { width: 1.2 }), path(`M${x0 + s * 3},${y + 8} l0,-4 l${s * 4},0 l0,4`, { width: 1.2 })); break
    case 'manual': out.push(line(x0, y, x0 + s * 8, y, { width: 1.5 }), line(x0 + s * 8, y - 6, x0 + s * 8, y + 6, { width: 2 })); break
    case 'override': out.push(rect(x0 + (s < 0 ? -16 : 0), y - 8, 16, 16), line(x0 + (s < 0 ? -16 : 0), y + 8, x0 + (s < 0 ? 0 : 16), y - 8, { width: 1.2 }), line(x0 + s * 16, y, x0 + s * 24, y, { width: 1.5 }), rect(x0 + (s < 0 ? -30 : 24), y - 5, 6, 10)); break
  }
  if (label) out.push(text(x0 + s * 20, y + 20, label, { size: 8.5, anchor: 'middle' }))
  return out
}
/** Full directional valve: positions drawn left-to-right, ports on the rest (drawn) position. */
export function dcv(x, y, { positions = ['parallel', 'closed', 'cross'], ports = 4, w = 34, h = 30, left = 'solenoid', right = 'spring', rest = null, labels = true } = {}) {
  const n = positions.length, x0 = x - (n * w) / 2, y0 = y - h / 2
  const out = []
  positions.forEach((k, i) => { const bx = x0 + i * w; out.push(...(ports === 4 ? pos4(bx, y0, w, h, k) : ports === 5 ? pos5(bx, y0, w, h, k) : posN(bx, y0, w, h, ports, k))) })
  // the drawn (rest) position keeps its stubs; hide stubs on the others by covering them (ISO shows ports only on the rest box)
  const restI = rest ?? (n === 3 ? 1 : n === 2 ? 1 : 0)
  positions.forEach((k, i) => { if (i === restI) return; const bx = x0 + i * w; out.push(rect(bx - 1, y0 - 10, w + 2, 9, { fill: C.paper, stroke: 'none' }), rect(bx - 1, y0 + h + 1, w + 2, 9, { fill: C.paper, stroke: 'none' })) })
  if (left) out.push(...operator(left, x0, y, 'left'))
  if (right) out.push(...operator(right, x0 + n * w, y, 'right'))
  if (labels) {
    const bx = x0 + restI * w
    if (ports === 4) out.push(text(bx + w * 0.28, y0 + h + 19, 'P', { size: 8.5, anchor: 'middle' }), text(bx + w * 0.72, y0 + h + 19, 'T', { size: 8.5, anchor: 'middle' }), text(bx + w * 0.28, y0 - 12, 'A', { size: 8.5, anchor: 'middle' }), text(bx + w * 0.72, y0 - 12, 'B', { size: 8.5, anchor: 'middle' }))
    if (ports === 3) out.push(text(bx + w * 0.28, y0 + h + 19, '1', { size: 8.5, anchor: 'middle' }), text(bx + w * 0.72, y0 + h + 19, '3', { size: 8.5, anchor: 'middle' }), text(bx + w * 0.5, y0 - 12, '2', { size: 8.5, anchor: 'middle' }))
    if (ports === 2) out.push(text(bx + w * 0.5, y0 + h + 19, '1', { size: 8.5, anchor: 'middle' }), text(bx + w * 0.5, y0 - 12, '2', { size: 8.5, anchor: 'middle' }))
    if (ports === 5) out.push(...[['5', 0.2], ['1', 0.5], ['3', 0.8]].map(([l, f]) => text(bx + w * f, y0 + h + 19, l, { size: 8.5, anchor: 'middle' })), text(bx + w * 0.35, y0 - 12, '4', { size: 8.5, anchor: 'middle' }), text(bx + w * 0.65, y0 - 12, '2', { size: 8.5, anchor: 'middle' }))
  }
  return out
}
/** Check valve on a vertical line through (x,y), free flow upward. spring: cracking pressure; pilot: 'open' | 'close'. */
export function check(x, y, { dir = 'up', spring = false, pilot = null, size = 8 } = {}) {
  const rot = { up: 0, down: 180, right: 90, left: 270 }[dir]
  const body = [circle(0, 0, size * 0.5), path(`M${-size},${size} L0,${-size * 0.2} L${size},${size}`, { width: 1.6 })]
  if (spring) body.push(path(`M0,${-size * 0.5} l-4,-4 l8,-4 l-8,-4 l8,-4`, { width: 1.1 }))
  const out = [g(body, { transform: `translate(${x},${y}) rotate(${rot})` })]
  if (pilot) {
    // pilot-to-open: the pilot line pushes the ball off its seat from the seat side (arrow toward the ball);
    // pilot-to-close: the pilot line acts on the ball from behind, holding it onto the seat.
    const py = pilot === 'open' ? y + size * 0.55 : y - size * 0.55
    out.push(rect(x - size - 4, y - size - 4, size * 2 + 8, size * 2 + 8, { dash: '3 2', width: 1 }), fl(x - size - 22, py, x - size - 4, py, 'pilot'),
      line(x - size - 4, py, x - size + 1, py, { width: 1.2, arrow: 'end' }))
  }
  return out
}
export const shuttle = (x, y) => [rect(x - 18, y - 8, 36, 16), circle(x - 4, y, 4, { fill: C.ink }), line(x - 18, y, x + 18, y, { width: 0 }), line(x - 24, y, x - 18, y, { width: 1.5 }), line(x + 18, y, x + 24, y, { width: 1.5 }), line(x, y - 8, x, y - 16, { width: 1.5 })]
/** Pressure valve envelope: 'relief' (NC, in to tank), 'reducing' (NO, downstream sensing), 'sequence', 'counterbalance', 'unloading'. Flow is bottom (in) to top (out) unless noted. */
export function pressureValve(x, y, kind = 'relief', { size = 30, vent = false, drain = false, remote = false } = {}) {
  const h = size / 2, out = [rect(x - h, y - h, size, size)]
  const no = kind === 'reducing'
  // arrow: NC valves show the arrow offset from the ports (blocked at rest); NO valves show it in line
  if (no) out.push(line(x, y + h, x, y - h, { width: 1.5, arrow: 'end' }))
  else out.push(line(x - h + 5, y + h - 3, x - h + 5, y - h + 3, { width: 1.5, arrow: 'end' }).replace(`M${x - h + 5}`, `M${x - h + 5}`), line(x, y + h, x, y + h + 8, { width: 1.5 }), line(x, y - h, x, y - h - 8, { width: 1.5 }))
  // spring on top with adjustment arrow, pilot line to the bottom face
  out.push(path(`M${x + h},${y} l6,0 l0,-${h + 6} l4,-4 l-8,-4 l8,-4 l-8,-4 l4,-4`, { width: 1.1 }), line(x + h + 2, y - h - 20, x + h + 14, y - h - 32, { width: 1, arrow: 'end' }))
  const pilotFrom = kind === 'reducing' ? [x, y - h - 6] : kind === 'counterbalance' || remote ? [x + h + 30, y + h + 6] : [x, y + h + 6]
  out.push(fl(pilotFrom[0], pilotFrom[1], x - h - 6, pilotFrom[1], 'pilot'), fl(x - h - 6, pilotFrom[1], x - h - 6, y, 'pilot'), fl(x - h - 6, y, x - h, y, 'pilot'))
  if (kind === 'counterbalance') out.push(fl(x, y + h + 6, x - h - 6, y + h + 6, 'pilot'))
  if (drain || kind === 'reducing' || kind === 'sequence') out.push(fl(x + 4, y + h, x + 4, y + h + 6, 'drain'), fl(x + 4, y + h + 6, x + h + 18, y + h + 6, 'drain'), ...tank(x + h + 18, y + h + 6, { w: 10, h: 6, stub: 0 }))
  if (vent) out.push(fl(x + h, y - 6, x + h + 20, y - 6, 'pilot'), text(x + h + 22, y - 3, 'vent', { size: 8 }))
  if (kind === 'unloading') out.push(fl(x - h - 6, y, x - h - 24, y, 'pilot'), text(x - h - 26, y + 3, 'remote', { size: 8, anchor: 'end' }))
  return out
}
/** Flow control on a vertical line. */
export function flowControl(x, y, { adjustable = true, compensated = false, tempComp = false, bypass = false, vertical = true } = {}) {
  const out = vertical ? [path(`M${x - 8},${y - 8} q8,8 0,16`, { width: 1.5 }), path(`M${x + 8},${y - 8} q-8,8 0,16`, { width: 1.5 })] : [path(`M${x - 8},${y - 8} q8,8 16,0`, { width: 1.5 }), path(`M${x - 8},${y + 8} q8,-8 16,0`, { width: 1.5 })]
  if (adjustable) out.push(line(x - 11, y + 11, x + 11, y - 11, { width: 1, arrow: 'end' }))
  if (compensated) out.unshift(rect(x - 16, y - 16, 32, 32), line(x - 14, y + 14, x - 14 + 1, y + 14, { width: 0 }), line(x + 12, y + 14, x + 16, y + 16, { width: 0 }), path(`M${x - 16},${y + 4} l-4,0 l0,10 l20,0 l0,-2`, { width: 1, dash: '3 2' }))
  if (tempComp) out.push(path(`M${x - 22},${y + 14} l0,-10 m-3,0 l6,0`, { width: 1.2 }), circle(x - 22, y + 16, 2.5, { fill: C.ink }))
  if (bypass) out.push(rect(x - 30, y - 22, 60, 44, { dash: '3 2', width: 1 }), ...check(x + 20, y, { dir: 'down', size: 6 }), line(x + 20, y - 22, x + 20, y - 6, { width: 1.2 }), line(x + 20, y + 6, x + 20, y + 22, { width: 1.2 }))
  return out
}
export const orifice = (x, y) => [path(`M${x - 8},${y - 8} q8,8 0,16`, { width: 1.5 }), path(`M${x + 8},${y - 8} q-8,8 0,16`, { width: 1.5 })]
export function accumulator(x, y, kind = 'gas') {
  const out = [path(`M${x - 10},${y + 14} L${x - 10},${y - 8} a10,10 0 0 1 20,0 L${x + 10},${y + 14} a10,8 0 0 1 -20,0 Z`, { width: 1.5 }), line(x, y + 22, x, y + 30, { width: 1.5 })]
  if (kind === 'gas') out.push(line(x - 10, y + 2, x + 10, y + 2, { width: 1.2 }), poly([[x - 4, y - 4], [x + 4, y - 4], [x, y - 10]], { fill: C.ink }))
  if (kind === 'spring') out.push(path(`M${x - 6},${y - 8} l12,3 l-12,3 l12,3 l-12,3 l12,3`, { width: 1 }), line(x - 10, y + 6, x + 10, y + 6, { width: 1.2 }))
  if (kind === 'weight') out.push(rect(x - 7, y - 6, 14, 10, { fill: C.ink }), line(x - 10, y + 6, x + 10, y + 6, { width: 1.2 }))
  return out
}
export function filter(x, y, { bypass = false, indicator = false, water = false } = {}) {
  const out = [poly([[x, y - 14], [x + 14, y], [x, y + 14], [x - 14, y]], { width: 1.5 }), line(x - 10, y, x + 10, y, { width: 1.2, dash: '3 2' })]
  if (water) out.push(circle(x, y + 8, 2, { fill: C.ink }))
  if (bypass) out.push(rect(x - 26, y - 22, 52, 44, { dash: '3 2', width: 1 }), ...check(x + 18, y, { dir: 'up', size: 5, spring: true }))
  if (indicator) out.push(circle(x + 22, y - 18, 5), line(x + 19, y - 15, x + 25, y - 21, { width: 1.2 }))
  return out
}
export const cooler = (x, y) => [poly([[x, y - 14], [x + 14, y], [x, y + 14], [x - 14, y]], { width: 1.5 }), line(x, y - 9, x, y - 3, { width: 1.5, arrow: 'end' }), line(x, y + 9, x, y + 3, { width: 1.5, arrow: 'end' })]
export const heater = (x, y) => [poly([[x, y - 14], [x + 14, y], [x, y + 14], [x - 14, y]], { width: 1.5 }), line(x, y - 3, x, y - 10, { width: 1.5, arrow: 'end' }), line(x, y + 3, x, y + 10, { width: 1.5, arrow: 'end' })]
export const gaugeP = (x, y, { r = 10 } = {}) => [circle(x, y, r), line(x - 3, y + 3, x + 4, y - 4, { width: 1.5 })]
export const gaugeT = (x, y, { r = 10 } = {}) => [circle(x, y, r), line(x, y + 6, x, y - 3, { width: 1.5 }), circle(x, y + 6, 2, { fill: C.ink })]
export const flowMeter = (x, y) => [circle(x, y, 10), line(x - 10, y, x + 10, y, { width: 0 }), path(`M${x - 6},${y} l12,0 m-4,-4 l4,4 l-4,4`, { width: 1.5 })]
export const pressureSwitch = (x, y) => [rect(x - 12, y - 10, 24, 20), line(x - 12, y, x - 22, y, { width: 1.5 }), line(x - 8, y + 4, x + 4, y - 4, { width: 1.5 }), circle(x + 6, y - 4, 1.8, { fill: C.ink }), line(x + 6, y - 4, x + 12, y - 4, { width: 1.2 }), path(`M${x - 6},${y + 10} l0,4 l-3,-2 l6,-4`, { width: 1 })]
export const quickDisconnect = (x, y, { coupled = true } = {}) => coupled ? [line(x - 16, y, x - 4, y, { width: 1.5 }), path(`M${x - 4},${y - 6} l0,12 M${x + 4},${y - 6} l0,12`, { width: 1.5 }), circle(x - 4, y, 3, { fill: C.paper }), circle(x + 4, y, 3, { fill: C.paper }), line(x + 4, y, x + 16, y, { width: 1.5 })] : [line(x - 20, y, x - 8, y, { width: 1.5 }), path(`M${x - 8},${y - 6} l0,12`, { width: 1.5 }), circle(x - 8, y, 3), path(`M${x + 8},${y - 6} l0,12`, { width: 1.5 }), circle(x + 8, y, 3), line(x + 8, y, x + 20, y, { width: 1.5 })]
export const rotaryJoint = (x, y) => [line(x - 14, y, x + 14, y, { width: 1.5 }), circle(x, y, 5), path(`M${x - 8},${y - 8} a8,8 0 0 1 16,0`, { width: 1.2, arrow: 'end' })]
export const exhaust = (x, y, { silencer = false } = {}) => [poly([[x - 5, y], [x + 5, y], [x, y + 9]], { fill: C.paper, width: 1.2 }), ...(silencer ? [rect(x - 6, y + 9, 12, 8), line(x - 4, y + 13, x + 4, y + 13, { width: 0.8 })] : [])]
export const airFilter = (x, y, { autoDrain = false } = {}) => [poly([[x, y - 12], [x + 12, y], [x, y + 12], [x - 12, y]], { width: 1.5 }), line(x - 9, y, x + 9, y, { width: 1.2, dash: '3 2' }), line(x, y + 12, x, y + 20, { width: 1.2 }), ...(autoDrain ? [rect(x - 4, y + 20, 8, 6), line(x, y + 26, x, y + 30, { width: 1 })] : [path(`M${x - 4},${y + 24} l8,0 m-4,-4 l0,8`, { width: 1 })])]
export const regulator = (x, y, { gauge = true } = {}) => [rect(x - 12, y - 12, 24, 24), line(x, y + 12, x, y - 12, { width: 1.5, arrow: 'end' }), path(`M${x - 6},${y - 12} l0,-6 l4,-3 l-8,-3 l8,-3 l-4,-3`, { width: 1 }), line(x - 12, y - 4, x - 6, y - 4, { width: 0 }), fl(x, y + 12, x - 18, y + 12, 'pilot'), fl(x - 18, y + 12, x - 18, y - 4, 'pilot'), fl(x - 18, y - 4, x - 12, y - 4, 'pilot'), ...(gauge ? gaugeP(x + 22, y - 18, { r: 6 }) : []), ...(gauge ? [line(x + 12, y - 6, x + 22, y - 12, { width: 1 })] : [])]
export const lubricator = (x, y) => [poly([[x, y - 12], [x + 12, y], [x, y + 12], [x - 12, y]], { width: 1.5 }), path(`M${x},${y - 8} l-3,5 a3,3 0 0 0 6,0 z`, { fill: C.ink, width: 0.8 })]
export const frlSimple = (x, y) => [rect(x - 24, y - 16, 48, 32, { dash: '4 3', width: 1 }), line(x - 24, y, x - 34, y, { width: 1.5 }), line(x + 24, y, x + 34, y, { width: 1.5 }), poly([[x - 12, y - 10], [x, y], [x - 12, y + 10], [x - 24, y]], { width: 1.3 }), line(x, y + 8, x, y - 8, { width: 1.2, arrow: 'end' }), path(`M${x + 12},${y - 10} L${x + 24},${y} L${x + 12},${y + 10} L${x},${y} Z`, { width: 1.3 })]
export const quickExhaust = (x, y) => [rect(x - 14, y - 10, 28, 20), line(x - 24, y, x - 14, y, { width: 1.5 }), line(x + 14, y, x + 24, y, { width: 1.5 }), line(x, y + 10, x, y + 16, { width: 1.5 }), ...exhaust(x, y + 16), circle(x - 4, y - 3, 3, { fill: C.ink }), path(`M${x - 12},${y + 5} l8,-4 m0,0 l8,4`, { width: 1.2 })]
export const vacuumCup = (x, y) => [path(`M${x - 12},${y + 6} a12,10 0 0 1 24,0 Z`, { width: 1.5 }), line(x, y - 4, x, y - 14, { width: 1.5 })]
export const vacuumGen = (x, y) => [rect(x - 16, y - 8, 32, 16), path(`M${x - 16},${y} l10,0 m0,-5 l6,5 l-6,5 M${x + 16},${y} l-10,0`, { width: 1.3 }), line(x, y + 8, x, y + 16, { width: 1.5 }), ...exhaust(x + 10, y - 16)]

// ================= ISA 5.1 P&ID =================
/** Manual valve body on a horizontal line through (x,y). */
export function pvalve(x, y, kind = 'gate', { s = 9 } = {}) {
  const bow = poly([[x - s, y - s * 0.7], [x + s, y + s * 0.7], [x + s, y - s * 0.7], [x - s, y + s * 0.7]], { width: 1.4 })
  const out = [bow]
  if (kind === 'globe') out.push(circle(x, y, 2.4, { fill: C.ink, stroke: 'none' }))
  if (kind === 'ball') out.push(circle(x, y, 4.2, { fill: C.paper }))
  if (kind === 'butterfly') { out.length = 0; out.push(line(x - s, y - s * 0.7, x - s, y + s * 0.7, { width: 1.4 }), line(x + s, y - s * 0.7, x + s, y + s * 0.7, { width: 1.4 }), line(x - s, y - s * 0.7, x + s, y + s * 0.7, { width: 1.4 }), circle(x, y, 3, { fill: C.paper })) }
  if (kind === 'plug') out.push(poly([[x - 4, y - 3], [x + 4, y - 3], [x + 3, y + 3], [x - 3, y + 3]], { fill: C.ink }))
  if (kind === 'needle') out.push(poly([[x - 3, y - 7], [x + 3, y - 7], [x, y]], { fill: C.ink }))
  if (kind === 'diaphragm') out.push(path(`M${x - 6},${y - 3} a6,6 0 0 1 12,0`, { width: 1.4 }))
  if (kind === 'check') { out.length = 0; out.push(poly([[x - s, y - s * 0.7], [x + s * 0.6, y], [x - s, y + s * 0.7]], { width: 1.4 }), line(x + s * 0.6, y - s * 0.8, x + s * 0.6, y + s * 0.8, { width: 2 })) }
  if (kind === 'threeway') out.push(poly([[x - s * 0.7, y - s], [x + s * 0.7, y - s], [x, y]], { width: 1.4 }))
  if (kind === 'angle') { out.length = 0; out.push(poly([[x - s, y - s * 0.7], [x, y], [x - s, y + s * 0.7]], { width: 1.4 }), poly([[x - s * 0.7, y - s * 1.6], [x + s * 0.7, y - s * 1.6], [x, y]], { width: 1.4 })) }
  if (kind === 'relief') out.push(path(`M${x},${y} l0,-8 l4,-3 l-8,-3 l8,-3 l-4,-3`, { width: 1.1 }))
  if (kind === 'rupture') { out.length = 0; out.push(line(x - 8, y - 6, x + 8, y - 6, { width: 1.2 }), path(`M${x - 8},${y} a8,6 0 0 1 16,0`, { width: 1.4 })) }
  return out
}
/** Actuator on top of a valve at (x, y-8): 'hand' T, 'diaphragm', 'piston', 'motor' M, 'solenoid' S, 'hydraulic' H; fail = 'FC' | 'FO' | 'FL'. */
export function actuator(x, y, kind = 'diaphragm', { fail } = {}) {
  const top = y - 7, out = [line(x, y, x, top - 8, { width: 1.4 })]
  if (kind === 'hand') out.push(line(x - 7, top - 8, x + 7, top - 8, { width: 2 }))
  if (kind === 'diaphragm') out.push(path(`M${x - 12},${top - 8} a12,9 0 0 1 24,0 Z`, { width: 1.4 }))
  if (kind === 'piston') out.push(rect(x - 9, top - 20, 18, 12), line(x - 9, top - 14, x + 9, top - 14, { width: 1 }))
  if (kind === 'motor') out.push(circle(x, top - 15, 7), text(x, top - 11.5, 'M', { size: 8, anchor: 'middle', weight: 700 }))
  if (kind === 'solenoid') out.push(rect(x - 7, top - 20, 14, 12), text(x, top - 10.5, 'S', { size: 8, anchor: 'middle', weight: 700 }))
  if (kind === 'hydraulic') out.push(rect(x - 7, top - 20, 14, 12), text(x, top - 10.5, 'H', { size: 8, anchor: 'middle', weight: 700 }))
  if (kind === 'springDiaphragm') out.push(path(`M${x - 12},${top - 8} a12,9 0 0 1 24,0 Z`, { width: 1.4 }), path(`M${x},${top - 17} l-3,-3 l6,-3 l-6,-3 l6,-3`, { width: 1 }))
  if (fail) out.push(text(x + 15, top - 10, fail, { size: 8.5, weight: 700 }))
  return out
}
export const pumpCentrifugal = (x, y, r = 12) => [circle(x, y, r), line(x, y - r, x + r + 6, y - r, { width: 1.5 }), line(x + r, y - 2, x + r + 6, y - r, { width: 0 }), path(`M${x + r},${y} L${x + r + 6},${y - r}`, { width: 1.5 })]
export const pumpPD = (x, y, r = 12) => [circle(x, y, r), poly([[x - 6, y + 4], [x + 6, y + 4], [x, y - 6]], { fill: C.ink })]
export const compressor = (x, y, r = 14) => [circle(x, y, r), poly([[x - 8, y + 6], [x + 8, y + 6], [x + 3, y - 7], [x - 3, y - 7]], { width: 1.2 })]
export const blower = (x, y, r = 12) => [circle(x, y, r), circle(x, y, 3, { fill: C.ink }), path(`M${x - 8},${y - 8} q8,8 16,0 M${x - 8},${y + 8} q8,-8 16,0`, { width: 1 })]
export const driver = (x, y, letter = 'M', r = 8) => [circle(x, y, r), text(x, y + 3.5, letter, { size: 9, anchor: 'middle', weight: 700 })]
export const vesselV = (x, y, w = 22, h = 50) => [path(`M${x - w / 2},${y - h / 2 + 8} a${w / 2},8 0 0 1 ${w},0 L${x + w / 2},${y + h / 2 - 8} a${w / 2},8 0 0 1 -${w},0 Z`, { width: 1.5 })]
export const vesselH = (x, y, w = 50, h = 22) => [path(`M${x - w / 2 + 8},${y - h / 2} L${x + w / 2 - 8},${y - h / 2} a8,${h / 2} 0 0 1 0,${h} L${x - w / 2 + 8},${y + h / 2} a8,${h / 2} 0 0 1 0,-${h} Z`, { width: 1.5 })]
export const tankCone = (x, y, w = 30, h = 26) => [rect(x - w / 2, y - h / 2 + 6, w, h - 6), poly([[x - w / 2, y - h / 2 + 6], [x + w / 2, y - h / 2 + 6], [x, y - h / 2 - 2]], { width: 1.4 })]
export const tankOpen = (x, y, w = 30, h = 24) => [path(`M${x - w / 2},${y - h / 2} L${x - w / 2},${y + h / 2} L${x + w / 2},${y + h / 2} L${x + w / 2},${y - h / 2}`, { width: 1.5 })]
export const exchangerST = (x, y, r = 13) => [circle(x, y, r), path(`M${x - r},${y} l6,-6 l6,12 l6,-12 l6,12 l6,-6`, { width: 1.3 }), line(x - r - 8, y, x - r, y, { width: 1.3 }), line(x + r, y, x + r + 8, y, { width: 1.3 })]
export const exchangerPlate = (x, y) => [rect(x - 14, y - 12, 28, 24), ...[-7, -2, 3, 8].map((d) => line(x + d, y - 12, x + d, y + 12, { width: 1 }))]
export const exchangerAir = (x, y) => [rect(x - 18, y - 10, 36, 20), ...[-10, 0, 10].map((d) => path(`M${x + d - 4},${y - 4} l8,8 M${x + d - 4},${y + 4} l8,-8`, { width: 1 }))]
export const filterBox = (x, y) => [rect(x - 12, y - 12, 24, 24), ...[-8, -2, 4].map((d) => line(x + d, y + 12, x + d + 8, y - 12, { width: 1 }))]
export const strainerY = (x, y) => [line(x - 14, y, x + 14, y, { width: 1.4 }), path(`M${x - 4},${y} l-8,10`, { width: 1.4 }), rect(x - 16, y + 9, 8, 5, { fill: C.paper })]
export const strainerT = (x, y) => [line(x - 14, y, x + 14, y, { width: 1.4 }), rect(x - 6, y - 12, 12, 12), line(x - 4, y - 2, x + 4, y - 10, { width: 1 })]
export const agitatorTank = (x, y) => [...tankOpen(x, y + 4, 34, 30), line(x, y - 22, x, y + 12, { width: 1.5 }), line(x - 8, y + 12, x + 8, y + 12, { width: 2 }), ...driver(x, y - 26, 'M', 6)]
export const conveyorSym = (x, y, w = 50) => [circle(x - w / 2, y, 6), circle(x + w / 2, y, 6), line(x - w / 2, y - 6, x + w / 2, y - 6, { width: 1.4 }), line(x - w / 2, y + 6, x + w / 2, y + 6, { width: 1.4 })]
export const steamTrap = (x, y) => [circle(x, y, 8), text(x, y + 3.5, 'T', { size: 9, anchor: 'middle', weight: 700 })]
export const reducerSym = (x, y, { eccentric = false } = {}) => eccentric ? [poly([[x - 8, y - 7], [x + 8, y - 7], [x + 8, y], [x - 8, y + 7]], { width: 1.4 })] : [poly([[x - 8, y - 7], [x + 8, y - 4], [x + 8, y + 4], [x - 8, y + 7]], { width: 1.4 })]
export const flangeSym = (x, y) => [line(x - 2, y - 7, x - 2, y + 7, { width: 1.6 }), line(x + 2, y - 7, x + 2, y + 7, { width: 1.6 })]
export const spectacleBlind = (x, y, { open = true } = {}) => [circle(x - 5, y - 12, 4, { fill: open ? C.paper : C.ink }), circle(x - 5, y - 21, 4, { fill: open ? C.ink : C.paper }), line(x - 5, y - 8, x - 5, y, { width: 1.4 }), line(x - 2, y - 7, x - 2, y + 7, { width: 1.6 }), line(x + 2, y - 7, x + 2, y + 7, { width: 1.6 })]
export const blindFlange = (x, y) => [line(x, y - 7, x, y + 7, { width: 1.6 }), line(x + 4, y - 7, x + 4, y + 7, { width: 3 })]
export const orificePlate = (x, y) => [line(x - 2, y - 7, x - 2, y + 7, { width: 1.6 }), line(x + 2, y - 7, x + 2, y + 7, { width: 1.6 }), line(x, y - 7, x, y - 14, { width: 1 })]
export const sightGlass = (x, y) => [rect(x - 8, y - 6, 16, 12), circle(x, y, 3)]
export const expansionJoint = (x, y) => [path(`M${x - 12},${y - 6} l4,0 l0,12 l4,0 l0,-12 l4,0 l0,12 l4,0 l0,-12 l4,0`, { width: 1.3 }), line(x - 12, y, x - 18, y, { width: 1.4 }), line(x + 12, y, x + 18, y, { width: 1.4 })]
export const hoseSym = (x, y) => [path(`M${x - 16},${y} q4,-8 8,0 t8,0 t8,0 t8,0`, { width: 1.4 })]
export const capSym = (x, y) => [path(`M${x - 4},${y - 6} l6,0 a6,6 0 0 1 0,12 l-6,0`, { width: 1.4 })]
export const ventSym = (x, y) => [line(x, y, x, y - 12, { width: 1.3 }), line(x - 5, y - 12, x + 5, y - 12, { width: 1.3 }), text(x, y - 15, 'ATM', { size: 7, anchor: 'middle' })]
export const drainSym = (x, y) => [line(x, y, x, y + 10, { width: 1.3 }), ...pvalve(x, y + 16, 'gate', { s: 5 }).map((s) => s), line(x, y + 22, x, y + 30, { width: 1.3 }), line(x - 6, y + 30, x + 6, y + 30, { width: 1.3 })]
/** P&ID line styles between (x1,y1) and (x2,y2). */
export function pline(x1, y1, x2, y2, kind = 'process') {
  const dx = x2 - x1, dy = y2 - y1, L = Math.hypot(dx, dy), ux = dx / L, uy = dy / L, nx = -uy, ny = ux
  const marks = (every, fn) => { const out = []; for (let d = every; d < L - 2; d += every) out.push(fn(x1 + ux * d, y1 + uy * d)); return out }
  switch (kind) {
    case 'process': return [line(x1, y1, x2, y2, { width: 2.4 })]
    case 'utility': return [line(x1, y1, x2, y2, { width: 1.4 })]
    case 'electric': return [line(x1, y1, x2, y2, { width: 1.1, dash: '5 3' })]
    case 'pneumatic': return [line(x1, y1, x2, y2, { width: 1.1 }), ...marks(14, (x, y) => line(x - ux * 3 - nx * 4, y - uy * 3 - ny * 4, x + ux * 3 + nx * 4, y + uy * 3 + ny * 4, { width: 1 }))]
    case 'hydraulic': return [line(x1, y1, x2, y2, { width: 1.1 }), ...marks(16, (x, y) => path(`M${x},${y} l${-nx * 5},${-ny * 5} l${ux * 4},${uy * 4}`, { width: 1 }))]
    case 'capillary': return [line(x1, y1, x2, y2, { width: 1.1 }), ...marks(14, (x, y) => path(`M${x - 3},${y - 3} l6,6 M${x - 3},${y + 3} l6,-6`, { width: 1 }))]
    case 'software': return [line(x1, y1, x2, y2, { width: 1 }), ...marks(14, (x, y) => circle(x, y, 2.4, { fill: C.paper }))]
    case 'mechanical': return [line(x1, y1, x2, y2, { width: 1.1 }), ...marks(12, (x, y) => circle(x, y, 1.6, { fill: C.ink, stroke: 'none' }))]
    case 'sonic': return [path(Array.from({ length: Math.floor(L / 8) }, (_, i) => (i ? 'L' : 'M') + (x1 + ux * i * 8 + nx * (i % 2 ? 3 : -3)) + ',' + (y1 + uy * i * 8 + ny * (i % 2 ? 3 : -3))).join(' '), { width: 1 })]
    case 'jacketed': return [line(x1, y1, x2, y2, { width: 2.4 }), line(x1 + nx * 4, y1 + ny * 4, x2 + nx * 4, y2 + ny * 4, { width: 1 }), line(x1 - nx * 4, y1 - ny * 4, x2 - nx * 4, y2 - ny * 4, { width: 1 })]
    case 'insulated': return [line(x1, y1, x2, y2, { width: 2.4 }), ...marks(24, (x, y) => path(`M${x - 3},${y - 5} l6,0 l0,10 l-6,0 z`, { width: 0.8 }))]
    case 'traced': return [line(x1, y1, x2, y2, { width: 2.4 }), line(x1 + nx * 4, y1 + ny * 4, x2 + nx * 4, y2 + ny * 4, { width: 1, dash: '4 2' })]
    case 'existing': return [line(x1, y1, x2, y2, { width: 1, opacity: 0.55 })]
    case 'underground': return [line(x1, y1, x2, y2, { width: 2.4 }), line(x1 - nx * 5, y1 - ny * 5, x2 - nx * 5, y2 - ny * 5, { width: 1, dash: '6 3' })]
  }
  return [line(x1, y1, x2, y2, { width: 1.4 })]
}
/** Instrument bubble. shape: 'discrete' | 'shared' | 'computer' | 'plc'; loc: 'field' | 'panel' | 'behind' | 'local'. */
export function bubble(x, y, letters, num, { shape = 'discrete', loc = 'field', r = 13 } = {}) {
  const out = []
  if (shape === 'shared' || shape === 'plc') out.push(rect(x - r - 2, y - r - 2, 2 * r + 4, 2 * r + 4))
  if (shape === 'computer') out.push(poly([[x - r, y], [x - r / 2, y - r], [x + r / 2, y - r], [x + r, y], [x + r / 2, y + r], [x - r / 2, y + r]], { width: 1.4 }))
  else if (shape === 'plc') out.push(poly([[x, y - r], [x + r, y], [x, y + r], [x - r, y]], { width: 1.4 }))
  else out.push(circle(x, y, r))
  if (loc === 'panel') out.push(line(x - r, y, x + r, y, { width: 1.4 }))
  if (loc === 'behind') out.push(line(x - r, y, x + r, y, { width: 1.2, dash: '3 2' }))
  if (loc === 'local') out.push(line(x - r, y - 1.5, x + r, y - 1.5, { width: 1.1 }), line(x - r, y + 1.5, x + r, y + 1.5, { width: 1.1 }))
  const two = loc !== 'field'
  out.push(text(x, two ? y - 3 : y - 1, letters, { size: two ? 8 : 8.5, anchor: 'middle', weight: 700 }), text(x, two ? y + 9 : y + 9, String(num), { size: 7.5, anchor: 'middle' }))
  return out
}

// ================= NEMA ICS 19 / IEC 60617 electrical =================
/** Contacts on a horizontal wire through (x,y). */
export const contactNO = (x, y, { iec = false } = {}) => iec ? [line(x - 14, y, x - 4, y, { width: 1.4 }), line(x - 4, y, x + 6, y - 8, { width: 1.4 }), line(x + 6, y, x + 14, y, { width: 1.4 })] : [line(x - 14, y, x - 5, y, { width: 1.4 }), line(x - 5, y - 7, x - 5, y + 7, { width: 1.6 }), line(x + 5, y - 7, x + 5, y + 7, { width: 1.6 }), line(x + 5, y, x + 14, y, { width: 1.4 })]
export const contactNC = (x, y, { iec = false } = {}) => iec ? [line(x - 14, y, x - 4, y, { width: 1.4 }), line(x - 4, y, x + 6, y - 8, { width: 1.4 }), line(x + 6, y, x + 14, y, { width: 1.4 }), line(x + 6, y - 9, x + 6, y, { width: 1.4 })] : [line(x - 14, y, x - 5, y, { width: 1.4 }), line(x - 5, y - 7, x - 5, y + 7, { width: 1.6 }), line(x + 5, y - 7, x + 5, y + 7, { width: 1.6 }), line(x - 7, y + 6, x + 7, y - 6, { width: 1.4 }), line(x + 5, y, x + 14, y, { width: 1.4 })]
export const coil = (x, y, label = 'M', { iec = false } = {}) => iec ? [line(x - 16, y, x - 8, y, { width: 1.4 }), rect(x - 8, y - 6, 16, 12), text(x, y - 9, label, { size: 8, anchor: 'middle', weight: 700 }), line(x + 8, y, x + 16, y, { width: 1.4 })] : [line(x - 16, y, x - 8, y, { width: 1.4 }), circle(x, y, 8), text(x, y + 3.5, label, { size: 8, anchor: 'middle', weight: 700 }), line(x + 8, y, x + 16, y, { width: 1.4 })]
export const timedContact = (x, y, { nc = false, delay = 'on' } = {}) => [...(nc ? contactNC(x, y) : contactNO(x, y)), path(delay === 'on' ? `M${x - 6},${y + 14} a6,6 0 0 0 12,0` : `M${x - 6},${y + 10} a6,6 0 0 1 12,0`, { width: 1.2 })]
export const pushbutton = (x, y, { nc = false, mushroom = false } = {}) => [line(x - 14, y, x - 6, y, { width: 1.4 }), line(x + 6, y, x + 14, y, { width: 1.4 }), circle(x - 6, y, 1.8, { fill: C.ink }), circle(x + 6, y, 1.8, { fill: C.ink }), nc ? line(x - 9, y + 4, x + 9, y + 4, { width: 1.6 }) : line(x - 9, y - 5, x + 9, y - 5, { width: 1.6 }), line(x, nc ? y + 4 : y - 5, x, y - 12, { width: 1.2 }), mushroom ? path(`M${x - 8},${y - 12} a8,5 0 0 1 16,0`, { width: 1.6, fill: C.paper }) : line(x - 5, y - 12, x + 5, y - 12, { width: 1.6 })]
export const selector = (x, y, { positions = 2 } = {}) => [line(x - 16, y, x - 6, y, { width: 1.4 }), circle(x - 6, y, 1.8, { fill: C.ink }), line(x - 6, y, x + 6, y - 8, { width: 1.4 }), circle(x + 6, y - 8, 1.8, { fill: C.ink }), circle(x + 6, y + 6, 1.8, { fill: C.ink }), line(x + 6, y - 8, x + 16, y - 8, { width: 1.4 }), line(x + 6, y + 6, x + 16, y + 6, { width: 1.4 }), ...(positions === 3 ? [circle(x + 6, y - 1, 1.8, { fill: C.ink })] : [])]
export const pilotLight = (x, y, letter = 'R', { pushToTest = false } = {}) => [line(x - 16, y, x - 8, y, { width: 1.4 }), circle(x, y, 8), path(`M${x - 5.5},${y - 5.5} l11,11 M${x - 5.5},${y + 5.5} l11,-11`, { width: 1 }), text(x, y - 11, letter, { size: 8, anchor: 'middle', weight: 700 }), line(x + 8, y, x + 16, y, { width: 1.4 }), ...(pushToTest ? [line(x, y - 8, x, y - 20, { width: 1 }), line(x - 4, y - 20, x + 4, y - 20, { width: 1.4 })] : [])]
/** Process-driven switches: the contact plus the actuator drawn below. kind: limit | pressure | temp | flow | float | prox | speed | foot. */
export function processSwitch(x, y, kind, { nc = false, held = false } = {}) {
  const out = [line(x - 16, y, x - 6, y, { width: 1.4 }), circle(x - 6, y, 1.8, { fill: C.ink }), circle(x + 6, y, 1.8, { fill: C.ink }), line(x + 6, y, x + 16, y, { width: 1.4 })]
  if (kind === 'limit') { out.push(nc ? line(x - 8, y - 8, x + 6, y + 0.5, { width: 1.4 }) : line(x - 6, y, x + 6, y - 8, { width: 1.4 })); if (nc) out.push(line(x - 6, y, x - 8, y - 8, { width: 0 })); out.push(held ? line(x - 12, y - 4, x - 12, y - 14, { width: 1.2 }) : path(`M${x - 6},${y} l-6,4`, { width: 1.2 })); return out }
  const arm = nc ? line(x - 6, y, x + 7, y + 5, { width: 1.4 }) : line(x - 6, y, x + 6, y - 8, { width: 1.4 })
  out.push(arm)
  const b = y + 12
  if (kind === 'pressure') out.push(line(x - 6, y, x - 6, b, { width: 1 }), path(`M${x - 12},${b} a6,6 0 0 0 12,0 z`, { width: 1.2 }))
  if (kind === 'temp') out.push(line(x - 6, y, x - 6, b, { width: 1 }), path(`M${x - 6},${b} l-6,-4 M${x - 6},${b} l-6,4`, { width: 0 }), circle(x - 6, b + 4, 3.5), line(x - 6, b + 0.5, x - 6, b + 4, { width: 1.2 }))
  if (kind === 'flow') out.push(line(x - 6, y, x - 6, b, { width: 1 }), path(`M${x - 12},${b} l12,0 m-4,-4 l4,4 l-4,4`, { width: 1.2 }))
  if (kind === 'float') out.push(line(x - 6, y, x - 6, b, { width: 1 }), circle(x - 6, b + 4, 4))
  if (kind === 'prox') out.push(line(x - 6, y, x - 6, b, { width: 1 }), poly([[x - 12, b], [x, b], [x - 6, b + 7]], { width: 1.2 }), line(x - 14, b + 10, x + 2, b + 10, { width: 1, dash: '2 2' }))
  if (kind === 'speed') out.push(line(x - 6, y, x - 6, b, { width: 1 }), circle(x - 6, b + 4, 4), path(`M${x - 10},${b + 4} a4,4 0 0 1 8,0`, { width: 1, arrow: 'end' }))
  if (kind === 'foot') out.push(line(x - 6, y, x - 6, b, { width: 1 }), path(`M${x - 12},${b} L${x - 12},${b + 8} L${x + 2},${b + 4}`, { width: 1.4 }))
  return out
}
export const overloadContact = (x, y) => [line(x - 16, y, x - 6, y, { width: 1.4 }), path(`M${x - 6},${y} l3,-4 l6,8 l3,-4`, { width: 1.4 }), line(x + 6, y, x + 16, y, { width: 1.4 }), text(x, y + 12, 'OL', { size: 7.5, anchor: 'middle' })]
export const overloadHeater = (x, y) => [line(x, y - 16, x, y - 8, { width: 1.4 }), rect(x - 5, y - 8, 10, 16), text(x + 8, y + 3, 'OL', { size: 7.5 }), line(x, y + 8, x, y + 16, { width: 1.4 })]
export const contactorPole = (x, y, label = 'M') => [line(x, y - 16, x, y - 6, { width: 1.4 }), line(x - 6, y - 6, x + 6, y - 6, { width: 1.6 }), line(x - 6, y + 6, x + 6, y + 6, { width: 1.6 }), line(x, y + 6, x, y + 16, { width: 1.4 }), text(x + 9, y + 3, label, { size: 7.5 })]
export const fuse = (x, y, { vertical = true } = {}) => vertical ? [line(x, y - 16, x, y - 8, { width: 1.4 }), rect(x - 4, y - 8, 8, 16), line(x, y - 8, x, y + 8, { width: 1 }), line(x, y + 8, x, y + 16, { width: 1.4 })] : [line(x - 16, y, x - 8, y, { width: 1.4 }), rect(x - 8, y - 4, 16, 8), line(x - 8, y, x + 8, y, { width: 1 }), line(x + 8, y, x + 16, y, { width: 1.4 })]
export const breaker = (x, y) => [line(x, y - 16, x, y - 6, { width: 1.4 }), path(`M${x},${y - 6} a4,4 0 0 1 0,8`, { width: 1.4 }), line(x, y + 2, x, y + 16, { width: 1.4 }), line(x - 4, y - 2, x + 4, y + 2, { width: 0 })]
export const disconnect = (x, y) => [line(x, y - 16, x, y - 6, { width: 1.4 }), circle(x, y - 6, 1.8, { fill: C.ink }), line(x, y - 6, x + 8, y + 6, { width: 1.4 }), circle(x, y + 6, 1.8, { fill: C.ink }), line(x, y + 6, x, y + 16, { width: 1.4 })]
export const transformerSym = (x, y) => [path(`M${x - 14},${y - 4} a4,4 0 0 1 8,0 a4,4 0 0 1 8,0 a4,4 0 0 1 8,0`, { width: 1.3 }), line(x - 14, y, x + 14, y, { width: 1 }), line(x - 14, y + 2, x + 14, y + 2, { width: 1 }), path(`M${x - 14},${y + 6} a4,4 0 0 0 8,0 a4,4 0 0 0 8,0 a4,4 0 0 0 8,0`, { width: 1.3 })]
export const motorSym = (x, y, { phases = 3, r = 10 } = {}) => [circle(x, y, r), text(x, y + 3.5, phases === 3 ? 'M' : 'M', { size: 9, anchor: 'middle', weight: 700 }), text(x + r + 2, y - 4, phases === 3 ? '3~' : '1~', { size: 7 })]
export const solenoidSym = (x, y) => [line(x - 16, y, x - 8, y, { width: 1.4 }), rect(x - 8, y - 6, 16, 12), path(`M${x - 6},${y} l3,-4 l3,8 l3,-8 l3,4`, { width: 1 }), line(x + 8, y, x + 16, y, { width: 1.4 })]
export const terminal = (x, y, n) => [circle(x, y, 4), text(x, y - 7, String(n), { size: 7.5, anchor: 'middle' })]
export const groundSym = (x, y) => [line(x, y, x, y + 8, { width: 1.4 }), line(x - 8, y + 8, x + 8, y + 8, { width: 1.6 }), line(x - 5, y + 12, x + 5, y + 12, { width: 1.4 }), line(x - 2, y + 16, x + 2, y + 16, { width: 1.2 })]
export const junctionDot = (x, y) => circle(x, y, 2.4, { fill: C.ink, stroke: 'none' })
export const plcPoint = (x, y, label, { output = false } = {}) => [rect(x - 22, y - 7, 44, 14, { rx: 2 }), text(x, y + 3.5, label, { size: 7.5, anchor: 'middle' }), line(output ? x + 22 : x - 22, y, output ? x + 34 : x - 34, y, { width: 1.4 })]
/** Ladder rails and a rung with a number on the left. */
export const rails = (x1, x2, y1, y2, { l1 = 'L1', l2 = 'L2' } = {}) => [line(x1, y1, x1, y2, { width: 2 }), line(x2, y1, x2, y2, { width: 2 }), text(x1, y1 - 6, l1, { size: 10, anchor: 'middle', weight: 700 }), text(x2, y1 - 6, l2, { size: 10, anchor: 'middle', weight: 700 })]

// ================= Piping isometric fittings =================
export const ISO = { ax: [Math.cos(30 * P), Math.sin(30 * P)] }
/** Isometric point: e (east) along +30°, n (north) along +150°, up = -y. */
export const iso = (ox, oy, e, n, u, k = 1) => [ox + (e - n) * ISO.ax[0] * k, oy + (e + n) * ISO.ax[1] * k - u * k]
export const weldDot = (x, y) => circle(x, y, 2.6, { fill: C.ink, stroke: 'none' })
export const fieldWeld = (x, y) => [circle(x, y, 2.6, { fill: C.ink, stroke: 'none' }), path(`M${x},${y - 3} l0,-10 l8,3 l-8,3`, { fill: C.ink, width: 0.8 })]
export const swTick = (x, y, dx, dy) => line(x - dy * 5, y + dx * 5, x + dy * 5, y - dx * 5, { width: 1.6 })
export const thrTicks = (x, y, dx, dy) => [line(x - dy * 5 - dx * 2, y + dx * 5 - dy * 2, x + dy * 5 - dx * 2, y - dx * 5 - dy * 2, { width: 1.4 }), line(x - dy * 5 + dx * 2, y + dx * 5 + dy * 2, x + dy * 5 + dx * 2, y - dx * 5 + dy * 2, { width: 1.4 })]
export const flangePair = (x, y, dx, dy) => [line(x - dy * 6 - dx * 2.5, y + dx * 6 - dy * 2.5, x + dy * 6 - dx * 2.5, y - dx * 6 - dy * 2.5, { width: 1.8 }), line(x - dy * 6 + dx * 2.5, y + dx * 6 + dy * 2.5, x + dy * 6 + dx * 2.5, y - dx * 6 + dy * 2.5, { width: 1.8 })]
export const isoValve = (x, y, dx, dy, { s = 7 } = {}) => [poly([[x - dx * s - dy * s * 0.6, y - dy * s + dx * s * 0.6], [x + dx * s + dy * s * 0.6, y + dy * s - dx * s * 0.6], [x + dx * s - dy * s * 0.6, y + dy * s + dx * s * 0.6], [x - dx * s + dy * s * 0.6, y - dy * s - dx * s * 0.6]], { width: 1.3 }), line(x, y, x - dy * 12, y + dx * 12, { width: 1.2 }), line(x - dy * 12 - dx * 4, y + dx * 12 - dy * 4, x - dy * 12 + dx * 4, y + dx * 12 + dy * 4, { width: 1.8 })]

// ================= Symbol sheet layout =================
/** Grid of symbol cells: each cell = { draw: (cx, cy) => [...svg], name, note? }. Returns the svg body; height via sheetHeight. */
export function sheet(cells, { cols = 4, cellW = 118, cellH = 96, x0 = 14, y0 = 30, symH = 50 } = {}) {
  const out = []
  cells.forEach((c, i) => {
    const col = i % cols, row = Math.floor(i / cols)
    const x = x0 + col * cellW, y = y0 + row * cellH
    out.push(rect(x, y, cellW - 6, cellH - 6, { fill: C.grey, stroke: 'none', rx: 6 }))
    out.push(...c.draw(x + (cellW - 6) / 2, y + symH / 2 + 4))
    out.push(text(x + (cellW - 6) / 2, y + symH + 16, c.name, { size: 9.5, anchor: 'middle', weight: 600 }))
    if (c.note) out.push(text(x + (cellW - 6) / 2, y + symH + 28, c.note, { size: 8.2, anchor: 'middle', fill: C.muted }))
  })
  return out
}
export const sheetHeight = (n, { cols = 4, cellH = 96, y0 = 30 } = {}) => y0 + Math.ceil(n / cols) * cellH + 18
