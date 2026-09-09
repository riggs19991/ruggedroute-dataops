// Redrawn diagrams from the September 2026 audit (scripts/diagrams/audit.md). This module runs last
// (alphabetical) so its figures override the originals with the same file name.
import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- shared drawing helpers ----------
/** Flame drawn along +x from (x,y). kind: 'neutral' | 'carb' | 'oxid' | 'acet' (acetylene only, sooty). */
export function flame(x, y, kind, scale = 1) {
  const s = scale
  const env = (len, w, op = 0.34) => path(`M${x},${y - w * s} C${x + len * s * 0.35},${y - w * s * 1.1} ${x + len * s * 0.8},${y - w * s * 0.5} ${x + len * s},${y} C${x + len * s * 0.8},${y + w * s * 0.5} ${x + len * s * 0.35},${y + w * s * 1.1} ${x},${y + w * s}Z`, { fill: `rgba(120,175,255,${op})`, stroke: 'rgba(160,200,255,0.7)', width: 0.8 })
  const cone = (len, w, fill, stroke) => path(`M${x},${y - w * s} C${x + len * s * 0.5},${y - w * s * 0.7} ${x + len * s * 0.85},${y - w * s * 0.25} ${x + len * s},${y} C${x + len * s * 0.85},${y + w * s * 0.25} ${x + len * s * 0.5},${y + w * s * 0.7} ${x},${y + w * s}Z`, { fill, stroke, width: 0.8 })
  if (kind === 'acet') return [path(`M${x},${y - 9 * s} C${x + 40 * s},${y - 26 * s} ${x + 120 * s},${y - 30 * s} ${x + 150 * s},${y - 6 * s} C${x + 130 * s},${y + 10 * s} ${x + 60 * s},${y + 14 * s} ${x},${y + 9 * s}Z`, { fill: '#f7b733', stroke: '#e08a00', width: 0.8 }), ...[0, 1, 2, 3].map((i) => circle(x + (110 + i * 18) * s, y - (22 + (i % 2) * 8) * s, 2.2 * s, { fill: '#333', stroke: 'none' }))]
  if (kind === 'carb') return [env(200, 13), cone(85, 9, 'rgba(255,250,235,0.8)', 'rgba(255,240,200,0.95)'), cone(30, 6, '#eaf6ff', '#8ec5ff')]
  if (kind === 'oxid') return [env(120, 9, 0.28), cone(20, 5, '#f0f4ff', '#a8b8ff')]
  return [env(170, 11), cone(28, 6, '#eaf6ff', '#8ec5ff')]
}
/** Welding/heating tip: brass body ending at (x,y), pointing +x. */
export function tip(x, y, len = 60, r = 7) {
  return [rect(x - len, y - r, len, r * 2, { fill: C.brass, stroke: C.accentDark, rx: 2 }), rect(x - len - 14, y - r - 3, 14, r * 2 + 6, { fill: C.copper, stroke: C.accentDark, rx: 2 }), rect(x - 6, y - r + 2, 6, r * 2 - 4, { fill: '#8a5a1a', stroke: 'none' })]
}
/** Cutting torch: handle at an angle, 90° head, tip pointing down to (x,y) with preheat cones and cutting stream. */
export function cutTorch(x, y, { tilt = 0, stream = true, cones = true } = {}) {
  return g([
    rect(-9, -170, 18, 70, { fill: C.grey, stroke: C.steelDark, rx: 5 }),                    // handle
    rect(-7, -100, 14, 40, { fill: C.steelDark, stroke: C.ink, rx: 3 }),                       // head block
    rect(-24, -96, 48, 12, { fill: C.steelDark, stroke: C.ink, rx: 3 }),                       // cross head
    rect(-8, -84, 16, 58, { fill: C.copper, stroke: C.accentDark, rx: 2 }),                    // tip
    ...(cones ? [-5, 0, 5].map((dx) => poly([[dx - 2.5, -26], [dx + 2.5, -26], [dx, -4]], { fill: '#eaf6ff', stroke: '#8ec5ff', width: 0.8 })) : []),
    ...(stream ? [line(0, -26, 0, 26, { stroke: 'rgba(70,130,255,0.55)', width: 5 })] : []),
  ], { transform: `translate(${x},${y}) rotate(${tilt})` })
}

// ---------- layout-templates/miter-elbow-layout ----------
{
  // Build pipe pieces from a polyline axis; each joint plane bisects the bend.
  const r = 28
  const pieces = (axis) => {
    const out = []
    const dir = (a, b) => { const dx = b[0] - a[0], dy = b[1] - a[1], L = Math.hypot(dx, dy); return [dx / L, dy / L] }
    const planes = axis.map((p, i) => { // unit direction of the joint line at each axis point
      if (i === 0) { const d = dir(axis[0], axis[1]); return [-d[1], d[0]] }
      if (i === axis.length - 1) { const d = dir(axis[i - 1], axis[i]); return [-d[1], d[0]] }
      const d1 = dir(axis[i - 1], axis[i]), d2 = dir(axis[i], axis[i + 1]); const bx = d1[0] + d2[0], by = d1[1] + d2[1], L = Math.hypot(bx, by); return [-by / L, bx / L]
    })
    for (let i = 0; i < axis.length - 1; i++) {
      const A = axis[i], B = axis[i + 1], d = dir(A, B), n = [-d[1], d[0]]
      const corner = (Pt, u, side) => { const cross = (p, q) => p[0] * q[1] - p[1] * q[0]; const t = -side * r * cross(n, u) / cross(d, u); return [Pt[0] + side * r * n[0] + t * d[0], Pt[1] + side * r * n[1] + t * d[1]] }
      out.push([corner(A, planes[i], 1), corner(B, planes[i + 1], 1), corner(B, planes[i + 1], -1), corner(A, planes[i], -1)])
    }
    return out
  }
  const shade = [C.steel, '#b9c4d2', C.steel, '#b9c4d2']
  const draw = (axis, ox) => { const ps = pieces(axis); return [...ps.map((p, i) => poly(p, { fill: shade[i], stroke: C.ink, width: 1.5 })), path('M' + axis.map((p) => p.join(',')).join(' L'), { stroke: C.muted, width: 1, dash: '6 4' })] }
  const two = [[20, 200], [150, 200], [150, 60]]
  const three = [[290, 200], [372, 200], [420, 152], [420, 60]]
  fig('layout-templates/miter-elbow-layout.svg', 'Mitered elbows: the joint line bisects the bend, so a 2-piece 90° has one 45° cut and a 3-piece has 22.5° end cuts with a 45° gore',
    svg(500, 400, [
      text(120, 24, '2-piece 90°: one weld, 45° cut', { anchor: 'middle', weight: 700, size: 12 }),
      ...draw(two), angle(150, 200, 40, 180, 225, '45°'),
      note(100, 258, 'cut both legs at 45°;\nthe joint runs corner to corner', { anchor: 'middle', size: 10 }),
      text(390, 24, '3-piece 90° (two welds)', { anchor: 'middle', weight: 700, size: 12 }),
      ...draw(three), angle(372, 200, 34, 180, 202.5, '22.5°', { size: 10.5 }),
      leader(396, 176, 300, 118, 'gore: 45° included\n(22.5° each end)', { size: 10.5, anchor: 'end' }),
      table(60, 272, [['Elbow', 'Pieces', 'Welds', 'End cut', 'Gore (middle) angle'], ['90°', '2', '1', '45°', '-'], ['90°', '3', '2', '22.5°', '45°'], ['90°', '4', '3', '15°', '30°'], ['45°', '2', '1', '22.5°', '-']], [60, 60, 60, 80, 140], { rowH: 19, size: 10.5 }),
      note(250, 380, 'end cut = elbow angle ÷ (2 × welds); gore = elbow angle ÷ welds', { anchor: 'middle', size: 11 }),
      caption(500, 400, 'More pieces: smoother flow, less pressure drop, more welds.'),
    ], { title: 'Miter elbow layout' }))
}
function leader(x, y, tx, ty, label, o = {}) { const { size = 12, anchor = 'start', fill = C.ink } = o; const sx = anchor === 'end' ? tx + 3 : tx - 3; return line(sx, ty - 4, x, y, { width: 1, arrow: 'end', stroke: fill }) + text(tx, ty, label, { size, anchor, fill }) }

// ---------- oxy-fuel/flame-types ----------
fig('oxy-fuel/flame-types.svg', 'The three oxy-acetylene flames as they really look, and the four steps to dial in a neutral flame',
  svg(500, 420, [
    rect(20, 12, 460, 220, { fill: '#0f1b2d', rx: 8 }),
    ...[['Carburising (extra acetylene)', 'white feather around the cone;\nhardfacing, bronze, aluminium', 'carb'],
      ['Neutral (1:1)', 'sharp bright inner cone, no feather;\ncutting, welding, heating', 'neutral'],
      ['Oxidising (excess oxygen)', 'short pointed cone, harsh hiss;\nbrass only, it burns steel', 'oxid']]
      .map(([n, d, k], i) => { const y = 50 + i * 68; return [...tip(70, y, 40, 6), ...flame(70, y, k, 0.95), text(290, y - 12, n, { size: 11, weight: 700, fill: '#f5f7fa' }), text(292, y + 4, d, { size: 9.5, fill: '#c9d3e0' })] }),
    text(250, 258, 'Dialing in a neutral flame', { anchor: 'middle', weight: 700, size: 12.5 }),
    ...[['1', 'Open acetylene 1/4 turn\nand light it: yellow,\nsmoky, soot in the air', 'acet'], ['2', 'Add acetylene until\nthe soot clears and the\nflame lifts off the tip', 'acet2'], ['3', 'Open the oxygen: an\ninner cone and a white\nfeather appear', 'carb'], ['4', 'Add oxygen until the\nfeather just disappears:\nneutral flame', 'neutral']]
      .map(([n, t, k], i) => { const x = 22 + i * 115, y = 302; return [rect(x, 272, 110, 108, { fill: '#0f1b2d', rx: 6 }), callout(+n, x + 12, 284), ...tip(x + 24, y + 4, 16, 4), ...flame(x + 24, y + 4, k === 'acet2' ? 'acet' : k, k === 'acet' ? 0.4 : k === 'acet2' ? 0.5 : 0.36), note(x + 55, y + 40, t, { anchor: 'middle', size: 8.4, fill: '#e7ebf1' })] }),
    caption(500, 420, 'Neutral is the reference: less oxygen carburises, more oxidises.'),
  ], { title: 'Oxy-fuel flame types' }))

// ---------- oxy-fuel/propane-vs-acetylene ----------
fig('oxy-fuel/propane-vs-acetylene.svg', 'Propane and propylene need a two-piece tip, more oxygen and a longer preheat; the flames look different too',
  svg(500, 300, [
    rect(20, 12, 460, 118, { fill: '#0f1b2d', rx: 8 }),
    text(130, 32, 'Acetylene: one-piece tip (1-101)', { anchor: 'middle', weight: 700, size: 11.5, fill: '#f5f7fa' }),
    rect(40, 62, 64, 20, { fill: C.copper, stroke: C.accentDark, rx: 2 }), rect(104, 60, 10, 24, { fill: C.brass, stroke: C.accentDark }), ...[0, 1, 2, 3, 4, 5].map((i) => circle(114, 63 + i * 3.6, 0.9, { fill: '#333', stroke: 'none' })),
    ...flame(114, 72, 'neutral', 0.7),
    note(130, 112, 'short sharp cones, fast preheat, 5,600°F', { anchor: 'middle', size: 9, fill: '#c9d3e0' }),
    text(370, 32, 'Propane: two-piece tip (GPN)', { anchor: 'middle', weight: 700, size: 11.5, fill: '#f5f7fa' }),
    rect(280, 62, 54, 20, { fill: C.copper, stroke: C.accentDark, rx: 2 }), rect(334, 58, 20, 28, { fill: C.brass, stroke: C.accentDark }), rect(348, 61, 6, 22, { fill: '#0f1b2d', stroke: C.accentDark }), ...[0, 1, 2, 3, 4, 5].map((i) => circle(351, 63 + i * 3.6, 0.9, { fill: '#8a5a1a', stroke: 'none' })),
    ...flame(354, 72, 'carb', 0.55),
    note(370, 112, 'recessed skirt, long soft cone, 5,100°F', { anchor: 'middle', size: 9, fill: '#c9d3e0' }),
    table(40, 142, [['', 'acetylene', 'propane / propylene'], ['tip', '1-101 (one piece)', 'GPN / GPP (two piece)'], ['fuel psi, 1/2 in', '3 to 5', '2 to 8'], ['oxygen psi, 1/2 in', '30 to 35', '35 to 45'], ['oxygen used', 'x 1', 'about x 1.5'], ['preheat', 'fast', 'slower; hold longer']], [120, 140, 160], { rowH: 20, size: 10.5 }),
    caption(500, 300, 'Same torch, different tip and pressures; grade T hose for propane.'),
  ], { title: 'Propane versus acetylene' }))

// ---------- oxy-fuel/oaw-braze-technique ----------
fig('oxy-fuel/oaw-braze-technique.svg', 'Forehand oxy-acetylene welding: torch at 45° with the inner cone just off the puddle, rod at 45° from the other side; bronze rod tins first',
  svg(500, 280, [
    plate(40, 160, 200, 18), plate(260, 160, 200, 18), rect(240, 160, 20, 18, { fill: C.paper, stroke: 'none' }),
    path('M236,160 C246,142 262,142 272,160 Z', { fill: C.weld, stroke: C.accentDark, width: 1 }),
    g([rect(-170, -9, 120, 18, { fill: C.steelDark, stroke: C.ink, rx: 5 }), ...tip(0, 0, 50, 6), ...flame(0, 0, 'neutral', 0.42)], { transform: 'translate(296 134) rotate(135)' }),
    g([rect(0, -2.5, 130, 5, { fill: C.copper, stroke: C.accentDark })], { transform: 'translate(232 150) rotate(-135)' }),
    angle(268, 160, 30, -45, 0, '45°', { size: 11 }), angle(232, 160, 30, 180, 225, '45°', { size: 11 }),
    line(200, 190, 280, 190, { width: 2, arrow: 'end', stroke: C.blue }), note(240, 204, 'travel: forehand, rod leads the torch', { anchor: 'middle', size: 10, fill: C.blue }),
    note(420, 108, 'inner cone 1/16 to 1/8 in\nabove the puddle, never in it', { anchor: 'middle', size: 10 }),
    note(96, 222, 'dip the rod in the leading\nedge of the puddle; do not\nmelt it in the flame', { anchor: 'middle', size: 10 }),
    box(330, 214, 150, 48, 'Braze welding:\nheat to dull red, tin with\nbronze, then build', { fill: C.soft, stroke: C.accentDark, size: 10 }),
    caption(500, 280, 'Neutral flame for steel; slightly oxidizing for braze welding.'),
  ], { title: 'Oxy-fuel welding and braze welding technique' }))

// ---------- oxy-fuel/cylinder-storage ----------
fig('oxy-fuel/cylinder-storage.svg', 'Cylinder storage: oxygen 20 ft from fuel gas or behind a 5 ft half-hour fire wall, upright, chained, capped',
  svg(500, 300, [
    ...[0, 1, 2].map((i) => [rect(40 + i * 30, 80, 24, 120, { fill: '#2f7a3a', rx: 6 }), rect(46 + i * 30, 66, 12, 14, { fill: C.steelDark, rx: 3 })]),
    text(77, 220, 'oxygen', { anchor: 'middle', size: 11, weight: 600 }),
    ...[0, 1, 2].map((i) => [rect(370 + i * 30, 80, 24, 120, { fill: '#8b1a1a', rx: 6 }), rect(376 + i * 30, 66, 12, 14, { fill: C.steelDark, rx: 3 })]),
    text(407, 220, 'acetylene / propane', { anchor: 'middle', size: 11, weight: 600 }),
    line(30, 140, 130, 140, { stroke: C.ink, width: 3 }), line(360, 140, 460, 140, { stroke: C.ink, width: 3 }),
    dim(135, 60, 365, 60, '20 ft (6.1 m) minimum', { size: 12 }),
    rect(244, 70, 12, 130, { fill: C.steelDark }), note(250, 216, 'or a 5 ft wall with\na 1/2-hour fire rating', { anchor: 'middle', size: 10 }),
    line(20, 200, 480, 200, { width: 2 }),
    legend(30, 248, ['chain or strap at 2/3 height, upright, caps on when not in use', 'empties marked and kept separate; away from heat, oil, grease and exits'], { size: 10.5, gap: 18 }),
  ], { title: 'Cylinder storage' }))

// ---------- cutting-gouging/oxy-cut-technique ----------
fig('cutting-gouging/oxy-cut-technique.svg', 'Oxy-fuel cutting: preheat cones 1/8 in above the plate, tip square, cutting oxygen through the kerf; the drag lines on the cut face tell you the speed',
  svg(500, 345, [
    text(30, 22, 'Straight cut', { weight: 700 }), plate(30, 180, 180, 26), rect(118, 180, 5, 26, { fill: C.paper, stroke: 'none' }),
    cutTorch(120, 176), dim(150, 154, 150, 176, '1/8 in', { size: 10.5, ext: false }),
    line(50, 160, 90, 160, { width: 1.5, arrow: 'end', stroke: C.blue }), note(70, 152, 'travel', { anchor: 'middle', size: 10, fill: C.blue }),
    note(120, 228, 'tip square, preheat cones 1/8 in above the\nplate; edge cherry red, then cutting oxygen', { anchor: 'middle', size: 10 }),
    text(470, 22, 'Bevel cut', { anchor: 'end', weight: 700 }), plate(280, 180, 190, 26),
    cutTorch(372, 176, { tilt: -30 }), line(372, 176, 372, 96, { dash: '4 3', width: 1, stroke: C.muted }), angle(372, 176, 46, -90, -120, '30°'),
    note(372, 228, 'tilt the whole torch on a guide bar or\nangle attachment; larger tip, slower', { anchor: 'middle', size: 10 }),
    text(250, 262, 'Reading the cut face (drag lines)', { anchor: 'middle', weight: 700, size: 12 }),
    ...[[60, 'straight and fine: right speed', 0], [200, 'swept back: too fast', 18], [340, 'gouged, top edge melted: too slow', -8]].map(([x, t, sk]) => [rect(x, 272, 90, 26, { fill: C.steel }), ...[0, 1, 2, 3, 4].map((i) => line(x + 12 + i * 16, 274, x + 12 + i * 16 + sk, 296, { width: 1, stroke: C.steelDark })), note(x + 45, 312, t, { anchor: 'middle', size: 9.5 })]),
    caption(500, 345, 'A clean kerf needs a clean tip: ream the orifices when the cones go crooked.'),
  ], { title: 'Oxy-fuel cutting technique' }))

// ---------- cutting-gouging/plasma-torch-consumables ----------
fig('cutting-gouging/plasma-torch-consumables.svg', 'Plasma torch consumables in order from the torch head: electrode, swirl ring, nozzle, retaining cap, shield; and the standoff',
  svg(500, 410, [
    text(150, 22, 'Consumable stack, exploded', { anchor: 'middle', weight: 700 }),
    // torch head
    rect(110, 34, 80, 26, { fill: C.grey, stroke: C.steelDark, rx: 6 }), rect(140, 60, 20, 8, { fill: C.steelDark }),
    // electrode: copper rod with silver hafnium tip
    rect(144, 76, 12, 44, { fill: C.copper, stroke: C.accentDark, rx: 2 }), rect(147, 120, 6, 5, { fill: '#c0c0c0', stroke: C.steelDark }),
    // swirl ring: white ceramic ring with holes
    rect(128, 134, 44, 14, { fill: '#f3f0e8', stroke: C.steelDark, rx: 3 }), ...[0, 1, 2, 3].map((i) => circle(136 + i * 9.5, 141, 1.6, { fill: C.steelDark, stroke: 'none' })),
    // nozzle: copper cone with orifice
    poly([[128, 158], [172, 158], [172, 176], [160, 194], [140, 194], [128, 176]], { fill: C.copper, stroke: C.accentDark }), rect(148, 190, 4, 6, { fill: '#333' }),
    // retaining cap: larger brass cup with threads
    poly([[118, 206], [182, 206], [182, 224], [166, 244], [134, 244], [118, 224]], { fill: C.brass, stroke: C.accentDark }), ...[0, 1, 2].map((i) => line(120, 210 + i * 5, 180, 210 + i * 5, { width: 0.6, stroke: C.accentDark })), rect(142, 240, 16, 6, { fill: C.paper, stroke: C.accentDark }),
    // shield: outer cup with centre hole and vent holes
    poly([[114, 256], [186, 256], [186, 270], [170, 292], [130, 292], [114, 270]], { fill: '#8a5a1a', stroke: C.accentDark }), rect(143, 286, 14, 8, { fill: C.paper, stroke: C.accentDark }), ...[0, 1, 2, 3].map((i) => circle(124 + i * 17, 276, 1.8, { fill: C.paper, stroke: 'none' })),
    ...[[47, 1, 'torch head'], [98, 2, 'electrode: copper, hafnium insert;\nreplace when the pit is over 1/16 in'], [141, 3, 'swirl ring (ceramic): spins the\ngas around the electrode'], [176, 4, 'nozzle: orifice sized to the amps;\nreplace when oval or gouged'], [225, 5, 'retaining cap: holds the stack,\nhand tight'], [274, 6, 'shield: takes the spatter; a drag\nshield can touch the plate']].map(([y, n, t]) => [line(190, y, 210, y, { width: 1, stroke: C.muted }), callout(n, 220, y), note(234, y + 4, t, { size: 9.6 })]),
    text(250, 322, 'Standoff', { anchor: 'middle', weight: 700, size: 12 }), plate(150, 382, 200, 12),
    g([rect(-10, -50, 20, 34, { fill: C.grey, rx: 4 }), poly([[-9, -16], [9, -16], [6, -4], [-6, -4]], { fill: '#8a5a1a', stroke: C.accentDark })], { transform: 'translate(250,376)' }), line(250, 376, 250, 394, { stroke: 'rgba(70,130,255,0.6)', width: 4 }),
    dim(300, 376, 300, 382, '1/16-1/8 in', { size: 10, ext: false }), note(330, 372, '(0 with a drag shield)', { size: 9.5 }),
    caption(500, 410, 'Clean dry air at the chart pressure; check the stack every start-up.'),
  ], { title: 'Plasma consumables' }))

// ---------- welding/smaw-angles ----------
fig('welding/smaw-angles.svg', 'Stick welding: arc length about the rod diameter, 10-15° drag travel angle, 45° work angle in a fillet',
  svg(500, 310, [
    text(130, 24, 'Side view: travel angle', { anchor: 'middle', weight: 700 }),
    plate(20, 210, 220, 16), line(60, 236, 110, 236, { width: 1.5, arrow: 'end', stroke: C.blue }), note(85, 252, 'travel', { anchor: 'middle', size: 10.5, fill: C.blue }),
    g([rect(-4.5, -150, 9, 130, { fill: '#c8c0b0', stroke: '#8a8070' }), rect(-2, -150, 4, 22, { fill: C.steelDark }), rect(-2, -22, 4, 22, { fill: C.steelDark }), rect(-8, -170, 16, 22, { fill: C.ink, rx: 3 })], { transform: 'translate(150,206) rotate(15)' }),
    line(150, 206, 150, 100, { dash: '4 3', width: 1, stroke: C.muted }), angle(150, 206, 70, -90, -75, ''), text(174, 130, '10-15° drag', { size: 11, fill: C.blue }),
    path('M147,206 q3,-5 6,0', { stroke: '#fff3b0', width: 5 }), path('M110,210 Q130,196 150,206', { stroke: C.weld, width: 4 }),
    note(22, 188, 'arc length ≈ rod dia.', { fill: C.blue, size: 10 }), line(110, 192, 146, 205, { width: 1, stroke: C.blue }),
    text(370, 24, 'End view: work angle (fillet)', { anchor: 'middle', weight: 700 }),
    plate(280, 210, 200, 16), plate(370, 100, 16, 110),
    g([rect(-4.5, -140, 9, 118, { fill: '#c8c0b0', stroke: '#8a8070' }), rect(-2, -22, 4, 22, { fill: C.steelDark }), rect(-8, -160, 16, 22, { fill: C.ink, rx: 3 })], { transform: 'translate(388,202) rotate(45)' }),
    line(386, 210, 386, 120, { dash: '4 3', width: 1, stroke: C.muted }), line(386, 210, 470, 210, { dash: '4 3', width: 1, stroke: C.muted }),
    angle(386, 210, 50, -90, -45, '45°'), path('M386,210 L404,210 L386,192 Z', { fill: C.weld, stroke: C.accentDark }),
    caption(500, 310, 'Tight arc, drag the rod, split the fillet angle. Long arc = spatter.'),
  ], { title: 'Stick welding angles' }))

// ---------- welding/mig-stickout ----------
function migGun(x, y, rot) { return g([path('M-40,-190 L-40,-150 Q-40,-120 -18,-104 L-8,-98', { stroke: C.grey, width: 30, cap: 'round', fill: 'none' }), path('M-40,-190 L-40,-150 Q-40,-120 -18,-104 L-8,-98', { stroke: C.steelDark, width: 1, fill: 'none' }), rect(-20, -104, 40, 74, { fill: C.copper, stroke: C.accentDark, rx: 5 }), rect(-5, -60, 10, 42, { fill: C.brass, stroke: C.accentDark }), line(0, -18, 0, 0, { stroke: C.ink, width: 2.5 })], { transform: `translate(${x},${y}) rotate(${rot})` }) }
fig('welding/mig-stickout.svg', 'MIG gun: contact-tip-to-work distance, stickout and a 10-15° push angle',
  svg(500, 330, [
    plate(30, 210, 300, 16), line(60, 236, 110, 236, { width: 1.5, arrow: 'end', stroke: C.blue }), note(85, 252, 'travel', { anchor: 'middle', size: 10.5, fill: C.blue }),
    migGun(200, 206, -12),
    line(200, 206, 200, 60, { dash: '4 3', width: 1, stroke: C.muted }), arc(200, 206, 120, -90, -102, { stroke: C.blue, width: 1 }), text(170, 78, '10-15° push', { size: 11, fill: C.blue, anchor: 'end' }),
    circle(200, 206, 6, { fill: C.accent, stroke: C.accentDark }), path('M160,212 Q180,194 200,206', { stroke: C.weld, width: 5 }),
    dim(262, 206, 262, 150, 'CTWD', { off: 0, size: 11, ext: false }),
    callout(1, 236, 128), callout(2, 224, 166), callout(3, 214, 190), callout(4, 155, 40),
    legend(335, 40, ['nozzle: 1/2-5/8 in ID,\nkeep spatter out', 'contact tip sized to the\nwire; recessed 1/8 in\nfor spray, flush for\nshort-circuit', 'stickout (wire past tip)\n3/8-1/2 in short-circuit\n3/4-1 in spray or FCAW', 'gun body and liner'], { gap: 44, size: 10.5 }),
    note(180, 282, 'CTWD = contact tip to work distance.\nLonger = less current, more spatter; shorter = hotter.', { anchor: 'middle', size: 10.5 }),
    caption(500, 330, 'Push 10-15° on steel short-circuit and spray; drag on flux-core.'),
  ], { title: 'MIG stickout and gun angle' }))

// ---------- welding/tig-torch-setup ----------
fig('welding/tig-torch-setup.svg', 'TIG: tungsten ground lengthwise to 2-2.5 diameters, torch pushed 10-15°, filler fed into the leading edge of the puddle at 15-20°',
  svg(500, 360, [
    text(110, 24, 'Tungsten grind (DC)', { anchor: 'middle', weight: 700 }),
    poly([[30, 50], [150, 50], [150, 66], [30, 66]], { fill: C.grey }), poly([[150, 50], [200, 57], [200, 59], [150, 66]], { fill: C.steelDark }),
    dim(150, 74, 200, 74, '2-2.5 × d', { size: 11 }), dim(24, 50, 24, 66, 'd', { size: 11, side: -1 }),
    ...[0, 1, 2, 3, 4].map((i) => line(152 + i * 10, 52 + i * 1.5, 190, 55.5 + i * 0.5, { stroke: C.paper, width: 0.6 })),
    note(20, 100, 'grind marks lengthwise, tiny flat on the tip;\nAC inverter: same or truncated; transformer: ball'),
    legend(20, 140, ['stickout ≈ cup diameter (2× with a gas lens)', 'arc length ≈ tungsten diameter', 'filler into the front edge of the puddle', 'ceramic cup #6-#8, gas lens for stainless'], { size: 11 }),
    text(360, 24, 'Torch and filler', { anchor: 'middle', weight: 700 }),
    plate(230, 250, 250, 16), line(430, 276, 380, 276, { width: 1.5, arrow: 'end', stroke: C.blue }), note(405, 292, 'travel', { anchor: 'middle', size: 10.5, fill: C.blue }),
    g([rect(-22, -190, 44, 110, { fill: C.grey, rx: 8 }), rect(-16, -82, 32, 10, { fill: C.copper, stroke: C.accentDark }), poly([[-15, -72], [15, -72], [12, -16], [-12, -16]], { fill: '#f5d0a9', stroke: C.accentDark }), line(0, -40, 0, 0, { stroke: C.steelDark, width: 3 })], { transform: 'translate(400,246) rotate(-12)' }),
    line(400, 246, 400, 120, { dash: '4 3', width: 1, stroke: C.muted }), angle(400, 246, 100, -90, -102, ''), text(378, 136, '10-15° push', { size: 11, fill: C.blue, anchor: 'end' }),
    g([line(0, 0, 120, 0, { stroke: C.copper, width: 3 })], { transform: 'translate(370,244) rotate(-162)' }),
    line(370, 244, 250, 244, { dash: '4 3', width: 1, stroke: C.muted }), arc(370, 244, 70, 180, 198, { stroke: C.blue, width: 1 }), text(292, 264, '15-20°', { size: 11, fill: C.blue, anchor: 'end' }),
    circle(392, 246, 6, { fill: C.accent, stroke: C.accentDark }), path('M370,248 Q392,232 414,248', { stroke: C.weld, width: 5 }),
    callout(1, 442, 200), callout(2, 428, 232), callout(3, 340, 210), callout(4, 452, 160),
    line(430, 200, 407, 208, { width: 1, stroke: C.muted }), line(418, 232, 402, 240, { width: 1, stroke: C.muted }), line(350, 210, 366, 236, { width: 1, stroke: C.muted }), line(442, 160, 412, 176, { width: 1, stroke: C.muted }),
    caption(500, 360, 'Never touch the tungsten to the puddle or rod: regrind if you do.'),
  ], { title: 'TIG torch setup' }))

// ---------- welding/mig-gun-parts ----------
fig('welding/mig-gun-parts.svg', 'MIG gun front end, exploded: liner, gas diffuser, contact tip and nozzle in the order they go together',
  svg(500, 240, [
    text(250, 22, 'Front end of the gun, exploded (left to right = inside to outside)', { anchor: 'middle', weight: 700, size: 12 }),
    // neck
    path('M20,90 Q20,120 60,120 L120,120', { stroke: C.grey, width: 26, cap: 'round', fill: 'none' }), path('M20,90 Q20,120 60,120 L120,120', { stroke: C.steelDark, width: 1, fill: 'none' }),
    // liner (coiled)
    ...[0, 1, 2, 3, 4, 5, 6, 7, 8, 9].map((i) => path(`M${30 + i * 9},116 q4,-6 8,0 q-4,6 -8,0`, { stroke: C.steelDark, width: 1, fill: 'none' })), line(28, 116, 118, 116, { stroke: C.steelDark, width: 0.8 }),
    // diffuser: brass with gas holes and threads
    rect(150, 104, 70, 32, { fill: C.brass, stroke: C.accentDark, rx: 3 }), ...[0, 1, 2].map((i) => line(152, 110 + i * 8, 172, 110 + i * 8, { width: 0.7, stroke: C.accentDark })), ...[0, 1, 2, 3].map((i) => circle(190 + i * 7, 108, 1.6, { fill: C.ink, stroke: 'none' })), ...[0, 1, 2, 3].map((i) => circle(190 + i * 7, 132, 1.6, { fill: C.ink, stroke: 'none' })),
    // contact tip: slender copper, threaded end
    rect(250, 112, 60, 16, { fill: C.copper, stroke: C.accentDark, rx: 2 }), ...[0, 1, 2].map((i) => line(252, 115 + i * 5, 264, 115 + i * 5, { width: 0.7, stroke: C.accentDark })), line(310, 120, 322, 120, { stroke: C.ink, width: 1.5 }),
    // nozzle: cup
    path('M350,96 L440,96 Q452,96 452,108 L452,132 Q452,144 440,144 L350,144 Z', { fill: C.copper, stroke: C.accentDark }), rect(356, 102, 88, 36, { fill: '#e8b98a', stroke: 'none' }), line(452, 104, 452, 136, { stroke: C.accentDark, width: 1 }),
    line(20, 120, 480, 120, { stroke: C.ink, width: 1, dash: '2 4' }),
    callout(1, 70, 70), callout(2, 185, 80), callout(3, 280, 90), callout(4, 400, 74),
    legend(20, 160, ['liner: sized to the wire, cut square; replace when feeding drags', 'gas diffuser / retaining head: holes clear, threads tight', 'contact tip: replace when oval, burnt or the wire stutters', 'nozzle cup: 1/2-5/8 in ID, anti-spatter, tip recessed 1/8 in for spray'], { size: 10.5, gap: 15 }),
  ], { title: 'MIG gun parts' }))

// ---------- welding/joint-types ----------
fig('welding/joint-types.svg', 'The five basic joints and the single-V groove terms drawn to angle: 60° included, 30° bevels',
  svg(500, 340, [
    ...[['Butt', (x, y) => [plate(x - 50, y, 46, 14), plate(x + 4, y, 46, 14), path(`M${x - 4},${y} Q${x},${y - 8} ${x + 4},${y}`, { stroke: C.weld, width: 5 })]],
      ['T (fillet)', (x, y) => [plate(x - 50, y, 100, 14), plate(x - 7, y - 50, 14, 50), path(`M${x - 7},${y} L${x - 22},${y} L${x - 7},${y - 15} Z`, { fill: C.weld, stroke: C.accentDark }), path(`M${x + 7},${y} L${x + 22},${y} L${x + 7},${y - 15} Z`, { fill: C.weld, stroke: C.accentDark })]],
      ['Lap', (x, y) => [plate(x - 50, y, 70, 14), plate(x - 20, y - 14, 70, 14), path(`M${x + 20},${y} L${x + 34},${y} L${x + 20},${y - 14} Z`, { fill: C.weld, stroke: C.accentDark })]],
      ['Corner', (x, y) => [plate(x - 40, y, 80, 14), plate(x + 26, y - 50, 14, 50), path(`M${x + 26},${y - 50} L${x + 40},${y - 50} L${x + 40},${y - 36} Z`, { fill: C.weld, stroke: C.accentDark })]],
      ['Edge', (x, y) => [plate(x - 12, y - 50, 12, 64), plate(x, y - 50, 12, 64), path(`M${x - 12},${y - 50} Q${x},${y - 58} ${x + 12},${y - 50}`, { stroke: C.weld, width: 5 })]]]
      .map(([n, draw], i) => { const x = 60 + i * 95, y = 90; return [text(x, 24, n, { anchor: 'middle', weight: 700, size: 12.5 }), ...draw(x, y)] }),
    text(250, 150, 'Single-V groove terms', { anchor: 'middle', weight: 700 }),
    // plates 80 tall, root face 12, bevel height 68 -> horizontal run 68*tan30 = 39
    poly([[60, 190], [201, 190], [240, 258], [240, 270], [60, 270]], { fill: C.steel }), poly([[440, 190], [299, 190], [260, 258], [260, 270], [440, 270]], { fill: C.steel }),
    line(250, 178, 250, 262, { dash: '3 3', width: 0.8, stroke: C.muted }),
    angle(250, 262, 60, -120, -60, ''), text(250, 178, '60° groove angle', { anchor: 'middle', size: 11, fill: C.blue }),
    line(201, 190, 201, 258, { dash: '3 3', width: 0.8, stroke: C.muted }), angle(201, 190, 34, 90, 60, ''), text(175, 236, '30° bevel', { size: 11, fill: C.blue, anchor: 'end' }),
    dim(240, 286, 260, 286, 'root opening 1/16-1/8 in', { size: 11 }), line(260, 264, 300, 258, { width: 1, stroke: C.blue }), text(304, 262, 'root face 1/16-1/8 in', { size: 11, fill: C.blue }),
    dim(456, 190, 456, 270, 'T', { size: 11 }),
    note(250, 322, 'Root face stops burn-through; root opening lets the root fuse.', { anchor: 'middle' }),
  ], { title: 'Weld joint types' }))

// ---------- welding/brazing-joint ----------
fig('welding/brazing-joint.svg', 'Silver brazing a tube into a socket: a capillary gap of 0.002-0.005 in per side that the filler is drawn into; heat the parts, not the rod',
  svg(500, 250, [
    text(250, 22, 'Section through a socket joint: heat pulls the filler into the gap', { anchor: 'middle', weight: 700, size: 11.5 }),
    // socket (fitting) walls: top and bottom, tube enters from the left
    rect(180, 90, 190, 16, { fill: C.copper, stroke: C.accentDark }), rect(180, 162, 190, 16, { fill: C.copper, stroke: C.accentDark }), rect(350, 106, 20, 56, { fill: C.copper, stroke: C.accentDark }),
    // tube walls inside the socket, thin silver gap between
    rect(30, 110, 230, 12, { fill: C.copper, stroke: C.accentDark }), rect(30, 146, 230, 12, { fill: C.copper, stroke: C.accentDark }),
    rect(180, 106, 80, 4, { fill: '#d9d9d9', stroke: '#9a9a9a', width: 0.5 }), rect(180, 158, 80, 4, { fill: '#d9d9d9', stroke: '#9a9a9a', width: 0.5 }),
    rect(260, 108, 12, 4, { fill: '#d9d9d9', stroke: 'none' }), rect(260, 156, 12, 4, { fill: '#d9d9d9', stroke: 'none' }),
    dim(180, 194, 260, 194, 'overlap 3-4 × wall', { size: 11 }),
    leader(220, 108, 30, 62, 'capillary gap 0.002-0.005 in per side (silver),\n0.003-0.010 in (bronze)', { size: 9.8, anchor: 'start' }),
    path('M430,58 L372,90', { stroke: C.red, width: 3, arrow: 'end' }), note(372, 108, 'flame on the heavy side,\nkeep it moving; rod at\nthe joint edge once\nthe flux runs clear', { size: 9.5 }),
    rect(150, 114, 18, 4, { fill: '#c0c0c0', stroke: 'none' }), line(168, 116, 186, 116, { width: 1, arrow: 'end', stroke: C.muted }), note(60, 136, 'filler flows toward the heat', { size: 10 }),
    caption(500, 250, 'Clean, flux, fit, heat evenly, feed, let it cool, wash off the flux.'),
  ], { title: 'Brazing joint' }))

// ---------- shared: dial indicators, machine trains ----------
/** Plunger dial indicator. Contact point at (x,y); the plunger runs up (-y) into the dial. rot turns the whole thing about the contact point. */
export function dialInd(x, y, { rot = 0, stem = 30, r = 15, needle = -70 } = {}) {
  const cy = -stem - r
  return g([
    rect(-3.5, -stem, 7, stem - 6, { fill: C.steelDark, stroke: C.ink, width: 1 }),
    rect(-1.5, -7, 3, 7, { fill: C.ink, stroke: 'none' }), circle(0, 0, 2.4, { fill: C.ink }),
    rect(-7, cy + r - 3, 14, 7, { fill: C.grey, stroke: C.ink, width: 1, rx: 1 }),
    circle(0, cy, r, { fill: C.paper, stroke: C.ink, width: 1.8 }), circle(0, cy, r - 2.5, { fill: 'none', stroke: C.line, width: 0.6 }),
    ...Array.from({ length: 12 }, (_, i) => { const a = i * 30 * P, R = r - 2.5; return line(Math.cos(a) * (R - 2.5), cy + Math.sin(a) * (R - 2.5), Math.cos(a) * R, cy + Math.sin(a) * R, { width: 0.8 }) }),
    line(0, cy, Math.cos(needle * P) * (r - 4), cy + Math.sin(needle * P) * (r - 4), { stroke: C.red, width: 1.4 }), circle(0, cy, 1.5, { fill: C.ink }),
  ], { transform: `translate(${x},${y}) rotate(${rot})` })
}
/** Lever (test) dial indicator. Dial centre at (x,y); lever tip lands at angle `lever` (deg, 0 = +x) and length len. */
export function testInd(x, y, { r = 13, lever = 20, len = 30, rot = 0 } = {}) {
  const tx = Math.cos(lever * P) * len, ty = Math.sin(lever * P) * len
  return g([
    rect(-6, r - 2, 12, 8, { fill: C.grey, stroke: C.ink, width: 1 }),
    circle(0, 0, r, { fill: C.paper, stroke: C.ink, width: 1.8 }), ...Array.from({ length: 8 }, (_, i) => { const a = i * 45 * P, R = r - 2; return line(Math.cos(a) * (R - 2.5), Math.sin(a) * (R - 2.5), Math.cos(a) * R, Math.sin(a) * R, { width: 0.8 }) }),
    line(0, 0, Math.cos(-60 * P) * (r - 4), Math.sin(-60 * P) * (r - 4), { stroke: C.red, width: 1.3 }),
    line(0, r + 6, tx, r + 6 + ty, { width: 2.5, stroke: C.ink }), circle(tx, r + 6 + ty, 2.4, { fill: C.red, stroke: 'none' }),
  ], { transform: `translate(${x},${y}) rotate(${rot})` })
}
/** Coupling hub, side view: bore on shaft centreline cy, face at x (hub extends toward dir). */
export function hub(x, cy, w, h, dir = 1) { const x0 = dir > 0 ? x : x - w; return [rect(x0, cy - h / 2, w, h, { fill: '#b9c4d2', stroke: C.ink, rx: 2 }), rect(x0 + 2, cy - h / 2 + 2, w - 4, 6, { fill: 'rgba(255,255,255,0.45)', stroke: 'none' })] }
/** Motor, side view: body with end bells, two feet on a base line at baseY, shaft to the left. */
export function motor(x, baseY, { w = 170, h = 90, feet = true, tag = 'motor' } = {}) {
  const top = baseY - h, cy = top + h * 0.5
  return [
    ...(feet ? [rect(x + 12, baseY - 10, 34, 10, { fill: C.steel, stroke: C.ink }), rect(x + w - 46, baseY - 10, 34, 10, { fill: C.steel, stroke: C.ink })] : []),
    rect(x, top + 10, w, h - 20, { fill: C.grey, stroke: C.ink, rx: 8 }), ...[0, 1, 2, 3, 4, 5].map((i) => line(x + 30 + i * 22, top + 12, x + 30 + i * 22, top + h - 12, { stroke: C.line, width: 1 })),
    rect(x + 60, top - 2, 50, 12, { fill: C.grey, stroke: C.ink, rx: 3 }), rect(x - 10, cy - 11, 12, 22, { fill: C.steel, stroke: C.ink }),
    text(x + w / 2, top + h - 22, tag, { anchor: 'middle', size: 10, fill: C.muted }),
  ]
}
/** Pump (stationary machine), side view, shaft to the right. */
export function pump(x, baseY, { w = 90, h = 90, tag = 'pump' } = {}) {
  const top = baseY - h, cy = top + h * 0.5
  return [rect(x + 10, baseY - 10, w - 20, 10, { fill: C.steel, stroke: C.ink }), circle(x + w / 2, cy, h * 0.42, { fill: C.grey, stroke: C.ink }), circle(x + w / 2, cy, h * 0.2, { fill: C.steel, stroke: C.ink }), rect(x + w / 2 - 8, top - 4, 16, 12, { fill: C.grey, stroke: C.ink }), rect(x + w - 8, cy - 11, 14, 22, { fill: C.steel, stroke: C.ink }), text(x + w / 2, baseY - 14, tag, { anchor: 'middle', size: 10, fill: C.muted })]
}

// ---------- alignment/offset-and-angularity ----------
{
  const pair = (x, cy, off, ang) => [
    rect(x, cy - 9, 70, 18, { fill: C.steel, stroke: C.ink }), ...hub(x + 70, cy, 34, 60, 1),
    g([...hub(0, 0, 34, 60, 1), rect(34, -9, 70, 18, { fill: C.steel, stroke: C.ink })], { transform: `translate(${x + 118},${cy + off}) rotate(${ang})` }),
    line(x - 10, cy, x + 118, cy, { stroke: C.blue, width: 1, dash: '6 3' }),
    g([line(-18, 0, 120, 0, { stroke: C.red, width: 1, dash: '6 3' })], { transform: `translate(${x + 118},${cy + off}) rotate(${ang})` }),
    note(x + 50, cy + 48, 'stationary', { anchor: 'middle', size: 10 }), note(x + 160, cy + 48, 'movable', { anchor: 'middle', size: 10 }),
  ]
  fig('alignment/offset-and-angularity.svg', 'Parallel offset and angular misalignment, each in the vertical and horizontal plane: four numbers describe any misalignment',
    svg(500, 310, [
      text(125, 22, 'Parallel offset', { anchor: 'middle', weight: 700 }), ...pair(14, 84, 14, 0),
      line(112, 84, 112, 98, { width: 1.2, arrow: 'both', stroke: C.red }), text(112, 40, 'offset (mils)', { size: 10, fill: C.red, anchor: 'middle' }), line(112, 44, 112, 82, { width: 0.8, stroke: C.red, dash: '2 2' }),
      text(375, 22, 'Angular', { anchor: 'middle', weight: 700 }), ...pair(264, 84, 0, -7),
      line(382, 52, 382, 116, { width: 1, stroke: C.red, dash: '2 2' }), note(388, 40, 'gap wider at top', { size: 9.5, fill: C.red }), note(388, 148, 'closes at bottom', { size: 9.5, fill: C.red }),
      note(300, 160, 'angle = gap difference ÷ hub diameter', { size: 9.5, anchor: 'start' }),
      text(250, 180, 'Each one is measured in two planes', { anchor: 'middle', weight: 700, size: 12 }),
      // side view: shims under the feet
      text(125, 198, 'vertical (side view): shims', { anchor: 'middle', size: 10.5, weight: 600 }),
      rect(30, 270, 190, 10, { fill: C.steel, stroke: C.ink }), rect(60, 208, 130, 50, { fill: C.grey, stroke: C.ink, rx: 5 }), text(125, 236, 'motor', { anchor: 'middle', size: 10, fill: C.muted }),
      ...[70, 160].map((x) => [rect(x, 258, 26, 6, { fill: C.steel, stroke: C.ink }), ...[0, 1, 2].map((i) => rect(x - 4, 264 + i * 2, 34, 1.4, { fill: C.accent, stroke: 'none' })), line(x + 13, 200, x + 13, 262, { stroke: C.ink, width: 2 })]),
      note(125, 296, 'raise a foot: add shims', { anchor: 'middle', size: 9.5 }),
      // top view: jack bolts
      text(375, 198, 'horizontal (top view): jack bolts', { anchor: 'middle', size: 10.5, weight: 600 }),
      rect(300, 205, 150, 76, { fill: C.grey, stroke: C.ink, rx: 4 }), rect(318, 216, 114, 54, { fill: C.steel, stroke: C.ink, rx: 10 }), text(375, 247, 'motor', { anchor: 'middle', size: 10, fill: C.muted }),
      ...[[318, 226], [318, 260], [432, 226], [432, 260]].map(([x, y]) => circle(x, y, 4, { fill: C.ink })),
      ...[[292, 226, 1], [292, 260, 1], [458, 226, -1], [458, 260, -1]].map(([x, y, d]) => [rect(x - 6, y - 5, 12, 10, { fill: C.steelDark, stroke: C.ink }), line(x, y, x + d * 20, y, { width: 3, stroke: C.accentDark }), ...(d > 0 && y === 226 ? [line(x - 22, y, x - 8, y, { width: 2, arrow: 'end', stroke: C.red })] : [])]),
      note(375, 296, 'push the frame sideways, then snug the bolts', { anchor: 'middle', size: 9.5 }),
    ], { title: 'Offset and angularity' }))
}

// ---------- alignment/rim-and-face-setup ----------
{
  const base = 208, cy = 140
  fig('alignment/rim-and-face-setup.svg', 'Rim-and-face: bracket on the stationary hub; the rim indicator reads offset on the movable hub, the face indicator reads angle on its face; record A, B and C',
    svg(500, 330, [
      rect(10, base, 480, 8, { fill: C.steel, stroke: C.ink }),
      ...pump(20, base, { tag: 'pump\n(stationary)'.split('\n')[0] }), rect(104, cy - 10, 30, 20, { fill: C.steel, stroke: C.ink }),
      ...hub(134, cy, 40, 78, 1), ...hub(216, cy, 40, 78, 1), rect(256, cy - 10, 30, 20, { fill: C.steel, stroke: C.ink }),
      ...motor(286, base, { w: 190, h: 100, tag: 'motor (movable)' }),
      // bracket: clamp on the stationary hub, post, arm over the gap
      rect(138, cy - 47, 32, 10, { fill: C.ink }), rect(138, cy + 37, 32, 10, { fill: C.ink }), rect(148, cy - 44, 12, 88, { fill: 'none', stroke: C.ink, width: 2 }),
      rect(150, 48, 8, cy - 47 - 48, { fill: C.steelDark, stroke: C.ink }), rect(150, 44, 110, 8, { fill: C.steelDark, stroke: C.ink }),
      // rim indicator: plunger down on the movable hub OD at 12 o'clock
      rect(232, 52, 8, 22, { fill: C.steelDark, stroke: C.ink }), dialInd(236, cy - 39, { stem: 12, r: 14, needle: -100 }),
      // face indicator: lever type reading the movable hub face inside the gap
      rect(196, 52, 8, 16, { fill: C.steelDark, stroke: C.ink }), testInd(200, 82, { r: 12, lever: 40, len: 22 }),
      text(258, 84, 'rim', { size: 10.5, weight: 700, fill: C.blue }), text(190, 84, 'face', { size: 10.5, weight: 700, fill: C.blue, anchor: 'end' }),
      // dimensions
      line(216, base + 14, 216, base + 42, { width: 0.8, stroke: C.muted }), line(236, base + 14, 236, base + 64, { width: 0.8, stroke: C.muted }), line(315, base + 12, 315, base + 84, { width: 0.8, stroke: C.muted }), line(447, base + 12, 447, base + 84, { width: 0.8, stroke: C.muted }),
      dim(216, base + 38, 236, base + 38, 'A', { size: 11, ext: false }), dim(236, base + 58, 315, base + 58, 'B', { size: 11, ext: false }), dim(236, base + 78, 447, base + 78, 'C', { size: 11, ext: false }),
      note(250, base + 100, 'A: face plane to rim plunger · B: rim plunger to front foot · C: to rear foot', { anchor: 'middle', size: 9.8 }),
      caption(500, 330, 'Turn both shafts together; zero at 12; read 3, 6, 9; check 3 + 9 = 6.'),
    ], { title: 'Rim and face setup' }))
}

// ---------- alignment/reverse-dial-setup ----------
{
  const base = 196, cy = 128
  const gx = [90, 250, 300, 432] // S plunger, M plunger, front foot, rear foot
  const gy = 264, sy = (v) => gy - v * 3, rd = (x) => -4 + (x - 90) * 0.0375 // graph baseline, 3 px per mil, movable line through the two readings
  fig('alignment/reverse-dial-setup.svg', 'Reverse dial: two brackets, each indicator reads the rim of the other shaft; plot both on a graph to the foot positions',
    svg(500, 330, [
      rect(10, base, 480, 8, { fill: C.steel, stroke: C.ink }),
      rect(20, base - 10, 50, 10, { fill: C.steel, stroke: C.ink }), rect(10, cy - 40, 60, 80, { fill: C.grey, stroke: C.ink, rx: 5 }), text(40, cy + 32, 'pump', { anchor: 'middle', size: 9.5, fill: C.muted }),
      rect(70, cy - 10, 84, 20, { fill: C.steel, stroke: C.ink }), ...hub(154, cy, 32, 60, 1), ...hub(200, cy, 32, 60, 1), rect(232, cy - 10, 54, 20, { fill: C.steel, stroke: C.ink }),
      ...motor(286, base, { w: 190, h: 92, tag: 'motor' }),
      // bracket S: clamped on the stationary shaft, reaches over to the movable shaft
      rect(84, cy - 22, 30, 44, { fill: 'none', stroke: C.ink, width: 3 }), rect(94, 40, 8, cy - 62, { fill: C.steelDark, stroke: C.ink }), rect(94, 36, 156, 8, { fill: C.steelDark, stroke: C.ink }), rect(246, 44, 8, 26, { fill: C.steelDark, stroke: C.ink }),
      dialInd(250, cy - 10, { stem: 16, r: 14, needle: -110 }),
      // bracket M: clamped on the movable shaft, reaches back under to the stationary shaft
      rect(240, cy - 22, 30, 44, { fill: 'none', stroke: C.ink, width: 3 }), rect(256, cy + 22, 8, 36, { fill: C.steelDark, stroke: C.ink }), rect(86, cy + 54, 178, 7, { fill: C.steelDark, stroke: C.ink }), rect(86, cy + 40, 8, 16, { fill: C.steelDark, stroke: C.ink }),
      dialInd(90, cy + 10, { stem: 4, r: 13, needle: -70, rot: 180 }),
      text(268, 100, 'S bracket reads the M shaft', { size: 9.5, fill: C.blue }), text(150, cy + 76, 'M bracket reads the S shaft', { size: 9.5, fill: C.blue }),
      text(110, 30, 'S', { size: 11, weight: 700 }), text(250, cy + 68, 'M', { size: 11, weight: 700, anchor: 'middle' }),
      // graph aligned under the train
      line(60, gy, 480, gy, { width: 1.2, stroke: C.muted }), ...gx.map((x, i) => [line(x, gy - 4, x, gy + 4, { width: 1 }), text(x, gy + 16, ['S', 'M', 'front foot', 'rear foot'][i], { anchor: 'middle', size: 9 })]), ...[2, 3].map((i) => line(gx[i], base + 8, gx[i], gy - 30, { width: 0.6, stroke: C.line, dash: '2 3' })),
      line(gx[0], sy(0), 470, sy(0), { width: 2, stroke: C.blue }),
      line(gx[0], sy(rd(gx[0])), 462, sy(rd(462)), { width: 2, stroke: C.red }),
      ...[0, 1].map((i) => circle(gx[i], sy(rd(gx[i])), 3, { fill: C.red, stroke: 'none' })),
      ...[2, 3].map((i) => { const v = rd(gx[i]); return [line(gx[i], sy(0), gx[i], sy(v), { width: 1.5, stroke: C.red, dash: '3 2' }), text(gx[i] + 4, sy(v) - 3, '+' + v.toFixed(1) + ' mils', { size: 9, fill: C.red })] }),
      note(62, gy - 5, 'stationary centreline', { size: 9, fill: C.blue }), note(300, gy - 34, 'movable shaft line through the S and M readings', { size: 9, fill: C.red, anchor: 'middle' }),
      note(250, gy + 32, 'the red line height at each foot is the shim change; no face reading, no axial float error', { anchor: 'middle', size: 9.5 }),
      caption(500, 330, 'Sag-correct both indicators; readings at 3-9 give horizontal, 12-6 vertical.'),
    ], { title: 'Reverse dial setup' }))
}

// ---------- alignment/soft-foot-types ----------
{
  const foot = (x, y, opts) => [ // machine corner: body block, foot pad, bolt
    rect(x - 34, y - 62, 80, 44, { fill: C.grey, stroke: C.ink, rx: 4 }),
    ...(opts.pad || [rect(x - 30, y - 18, 60, 18, { fill: C.steel, stroke: C.ink })]),
    line(x, y - 74, x, y - 4, { width: 4, stroke: C.ink }), rect(x - 8, y - 82, 16, 8, { fill: C.ink }),
  ]
  const base = (x, y) => rect(x - 50, y, 110, 14, { fill: '#b9c4d2', stroke: C.ink })
  const panel = (i, name, body, why) => { const x = 60 + i * 122, y = 150; return [text(x, 24, name, { anchor: 'middle', weight: 700, size: 12 }), base(x, y), ...body(x, y), text(x, y + 30, why, { anchor: 'middle', size: 9.5, fill: C.red })] }
  fig('alignment/soft-foot-types.svg', 'Soft foot types: parallel (short leg), angular (bent foot), squishy (bad shims) and induced (pipe strain)',
    svg(500, 270, [
      ...panel(0, 'Parallel', (x, y) => [...foot(x, y - 8, {}), line(x + 36, y - 8, x + 36, y, { width: 1, arrow: 'both', stroke: C.red })], 'even gap: shim it'),
      ...panel(1, 'Angular', (x, y) => [...foot(x, y, { pad: [poly([[x - 30, y - 18], [x + 30, y - 18], [x + 30, y], [x - 30, y - 9]], { fill: C.steel, stroke: C.ink })] }), line(x - 36, y - 9, x - 36, y, { width: 1, arrow: 'both', stroke: C.red })], 'tapered gap: taper shim'),
      ...panel(2, 'Squishy', (x, y) => [...foot(x, y - 10, {}), ...[0, 1, 2, 3].map((k) => path(`M${x - 32 + (k % 2) * 3},${y - 9 + k * 2.6} q10,-2.5 20,0 t20,0 t20,0`, { stroke: C.accentDark, width: 1.4 })), ], 'bent or dirty shims'),
      ...panel(3, 'Induced', (x, y) => [...foot(x, y, {}), rect(x + 18, y - 90, 20, 28, { fill: C.grey, stroke: C.ink }), path(`M${x + 28},${y - 90} L${x + 28},${y - 104} L${x + 52},${y - 104}`, { stroke: C.steelDark, width: 9 }), path(`M${x + 28},${y - 90} L${x + 28},${y - 104} L${x + 52},${y - 104}`, { stroke: C.steel, width: 5 }), line(x + 52, y - 104, x + 66, y - 104, { stroke: C.red, width: 3, arrow: 'end' }), line(x - 30, y - 6, x - 30, y, { width: 1, arrow: 'both', stroke: C.red })], 'pipe pulls a foot up'),
      note(250, 206, 'angular: taper shim or machine the foot · squishy: clean it, use fewer thicker shims', { anchor: 'middle', size: 10 }),
      note(250, 222, 'induced: fix the pipe or base; the machine is being pulled, not resting', { anchor: 'middle', size: 10 }),
      note(250, 240, 'check: indicator on the foot, loosen one bolt at a time; over 0.002 in lift = soft', { anchor: 'middle', size: 10, fill: C.blue }),
      caption(500, 270, 'Fix soft foot before any alignment reading, or it moves when torqued.'),
    ], { title: 'Soft foot types' }))
}

// ---------- measurement/dial-indicator-runout ----------
fig('measurement/dial-indicator-runout.svg', 'Runout: indicator square to the shaft, rotate one full turn, TIR = highest minus lowest; keep test indicators near parallel to the surface',
  svg(500, 262, [
    text(130, 22, 'Shaft runout (TIR)', { anchor: 'middle', weight: 700 }),
    rect(20, 176, 220, 10, { fill: C.steel, stroke: C.ink }),
    ...[70, 190].map((x) => poly([[x - 26, 176], [x + 26, 176], [x + 26, 148], [x + 10, 148], [x, 160], [x - 10, 148], [x - 26, 148]], { fill: C.grey, stroke: C.ink })),
    rect(40, 128, 180, 32, { fill: C.steel, stroke: C.ink, rx: 3 }), rect(40, 132, 180, 6, { fill: 'rgba(255,255,255,0.5)', stroke: 'none' }),
    rect(228, 154, 36, 22, { fill: C.ink, rx: 2 }), rect(238, 62, 8, 92, { fill: C.steelDark, stroke: C.ink }), rect(126, 58, 120, 8, { fill: C.steelDark, stroke: C.ink }),
    dialInd(130, 128, { stem: 20, r: 16, needle: -80 }), rect(126, 66, 8, 12, { fill: C.steelDark, stroke: C.ink }),
    arc(130, 144, 44, 200, 340, { stroke: C.blue, width: 1.2, arrow: 'end' }), note(130, 208, 'plunger square to the shaft, on the high spot;\nturn 360°: TIR = total needle travel', { anchor: 'middle', size: 9.5 }),
    note(246, 196, 'mag base', { size: 9, anchor: 'middle' }), note(70, 196, 'V-blocks', { size: 9, anchor: 'middle' }),
    text(370, 22, 'Cosine error (lever indicator)', { anchor: 'middle', weight: 700 }), rect(290, 150, 190, 14, { fill: C.steel, stroke: C.ink }),
    testInd(322, 106, { r: 12, lever: 12, len: 40 }), testInd(430, 100, { r: 12, lever: 50, len: 38 }),
    note(330, 180, '0-10°: reads true', { anchor: 'middle', size: 10, fill: C.green }), note(440, 180, '30°: reads ×0.87', { anchor: 'middle', size: 10, fill: C.red }),
    note(385, 208, 'keep the lever nearly parallel;\nover 15° multiply by cos(angle)', { anchor: 'middle', size: 9.5 }),
    caption(500, 262, 'Rigid mount, short overhang, plunger square, same graduation each turn.'),
  ], { title: 'Dial indicator runout' }))

// ---------- measurement/vernier-scale-reading ----------
{
  const x0 = 30, px = 400, y = 96 // 1.000 in = 400 px; main line every 0.025 in = 10 px
  const vz = x0 + 0.436 * px, vd = 9.6 // 25 vernier divisions over 24 main divisions
  fig('measurement/vernier-scale-reading.svg', 'Reading an inch vernier: main scale to 0.025, then the vernier line that lines up gives thousandths',
    svg(500, 284, [
      rect(x0 - 10, y - 40, 470, 40, { fill: C.grey, stroke: C.ink }), text(x0 + 8, y - 26, 'beam', { size: 9, fill: C.muted }),
      ...Array.from({ length: 41 }, (_, n) => { const x = x0 + n * 10, t = n % 10 === 0 ? 22 : n % 5 === 0 ? 14 : 8; return [line(x, y, x, y - t, { width: n % 10 === 0 ? 1.6 : 1 }), n % 10 === 0 ? text(x, y - 26, String(n / 10), { size: 11, anchor: 'middle', weight: 700 }) : ''] }),
      text(x0 - 4, y - 14, '1', { size: 12, weight: 700, anchor: 'end' }), text(x0 - 20, y - 26, 'in', { size: 9, fill: C.muted }),
      rect(vz - 12, y, 262, 30, { fill: C.blueSoft, stroke: C.blue }), text(vz + 125, y + 56, 'sliding jaw (vernier plate)', { size: 9.5, anchor: 'middle', fill: C.blue }),
      ...Array.from({ length: 26 }, (_, k) => { const x = vz + k * vd, hit = k === 11; return [line(x, y, x, y + (k % 5 === 0 ? 20 : 12), { width: hit ? 2.4 : 1, stroke: hit ? C.red : C.ink }), k % 5 === 0 ? text(x, y + 30 + 10, String(k), { size: 10, anchor: 'middle', weight: 700, fill: C.blue }) : ''] }),
      line(vz, y - 34, vz, y + 22, { stroke: C.blue, width: 1, dash: '3 2' }), text(vz, y - 46, 'vernier 0', { size: 9.5, anchor: 'middle', fill: C.blue }),
      circle(vz + 11 * vd, y, 7, { fill: 'none', stroke: C.red, width: 1.5 }), text(vz + 11 * vd, y + 72, 'only line 11 is exactly in line', { size: 10, fill: C.red, anchor: 'middle' }),
      text(40, 196, 'main scale before vernier 0: 1 + 0.4 + 0.025 = 1.425', { size: 11.5, family: 'ui-monospace, Menlo, Consolas, monospace' }),
      text(40, 216, 'vernier line that lines up:  11  = 0.011', { size: 11.5, family: 'ui-monospace, Menlo, Consolas, monospace', fill: C.red }),
      text(40, 238, 'reading:  1.425 + 0.011 = 1.436 in', { size: 12.5, weight: 700, family: 'ui-monospace, Menlo, Consolas, monospace' }),
      caption(500, 284, 'Hold it to the light: one vernier line lines up, its neighbours are just off.'),
    ], { title: 'Vernier scale reading' }))
}

// ---------- bearings/puller-types ----------
{
  const brg = (x, cy) => [rect(x, cy - 34, 30, 68, { fill: C.steel, stroke: C.ink, rx: 2 }), rect(x + 3, cy - 20, 24, 40, { fill: C.paper, stroke: C.ink }), rect(x + 6, cy - 14, 18, 28, { fill: '#b9c4d2', stroke: C.ink }), ...[-26, 26].map((d) => circle(x + 15, cy + d, 5, { fill: C.grey, stroke: C.ink }))]
  fig('bearings/puller-types.svg', 'Pull on the ring that is tight: jaws or a separator behind the inner ring, never through the balls',
    svg(500, 300, [
      text(125, 22, 'Jaw puller (right)', { anchor: 'middle', weight: 700, size: 12, fill: C.green }),
      rect(150, 118, 100, 24, { fill: C.steel, stroke: C.ink }), ...brg(170, 130),
      // yoke, forcing screw, two arms with hooked jaws behind the inner ring
      rect(60, 60, 14, 140, { fill: C.steelDark, stroke: C.ink, rx: 3 }), rect(48, 122, 20, 16, { fill: C.ink, rx: 2 }), rect(68, 124, 82, 12, { fill: C.grey, stroke: C.ink }),
      ...[0, 1, 2, 3, 4, 5, 6].map((i) => line(74 + i * 10, 124, 78 + i * 10, 136, { stroke: C.ink, width: 1 })), rect(146, 120, 6, 20, { fill: C.ink }),
      ...[[60, 1], [200, -1]].map(([y, s]) => [path(`M67,${y} L110,${y + s * 6} L176,${y + s * 30} L176,${y + s * 44} L190,${y + s * 44} L190,${y + s * 20}`, { stroke: C.ink, width: 6 }), path(`M67,${y} L110,${y + s * 6} L176,${y + s * 30} L176,${y + s * 44} L190,${y + s * 44} L190,${y + s * 20}`, { stroke: C.steel, width: 3 })]),
      note(120, 250, 'jaw tips hook behind the inner ring;\nscrew on the shaft centre, arms parallel', { anchor: 'middle', size: 9.5 }),
      text(375, 22, 'Separator + push-puller', { anchor: 'middle', weight: 700, size: 12, fill: C.green }),
      rect(390, 118, 100, 24, { fill: C.steel, stroke: C.ink }), ...brg(410, 130),
      // separator plates (two halves) with knife edges behind the inner ring, tightened by two bolts
      ...[[-1], [1]].map(([s]) => poly([[404, 130 + s * 36], [408, 130 + s * 14], [396, 130 + s * 14], [396, 130 + s * 78], [404, 130 + s * 78]], { fill: C.steelDark, stroke: C.ink })),
      ...[52, -52].map((d) => [rect(392, 130 + d - 3, 16, 6, { fill: C.ink }), line(392, 130 + d, 380, 130 + d, { width: 3 })]),
      // push-puller: yoke with two long legs bolted to the separator, forcing screw on the shaft end
      rect(300, 44, 14, 172, { fill: C.steelDark, stroke: C.ink, rx: 3 }), ...[52, -52].map((d) => [rect(312, 130 + d - 4, 84, 8, { fill: C.grey, stroke: C.ink }), rect(388, 130 + d - 5, 8, 10, { fill: C.ink })]),
      rect(288, 122, 20, 16, { fill: C.ink, rx: 2 }), rect(308, 124, 82, 12, { fill: C.grey, stroke: C.ink }), ...[0, 1, 2, 3, 4, 5, 6].map((i) => line(314 + i * 10, 124, 318 + i * 10, 136, { stroke: C.ink, width: 1 })),
      note(390, 250, 'knife edges close behind the inner ring\nwhere jaws will not fit; legs pull them', { anchor: 'middle', size: 9.5 }),
      caption(500, 300, 'Pulling on the outer ring loads the balls: the bearing is scrap after that.'),
    ], { title: 'Puller types' }))
}

// ---------- bearings/adapter-sleeve-drive-up ----------
{
  // Half-section above the shaft: everything measured as height d above the shaft surface (y = T - d).
  const T = 262, Y = (d) => T - d
  fig('bearings/adapter-sleeve-drive-up.svg', 'Tapered bore on an adapter sleeve: measure clearance over the top roller, tighten the lock nut until the clearance drops by the table value',
    svg(500, 340, [
      rect(20, T, 460, 56, { fill: C.steel, stroke: C.ink }), line(20, T + 28, 480, T + 28, { width: 0.8, stroke: C.muted, dash: '10 4 2 4' }), text(250, T + 34, 'shaft', { size: 10, anchor: 'middle', fill: C.muted }),
      // adapter sleeve: taper 1:12 (exaggerated), thin at the nut end, slit, thread at the nut end
      poly([[130, Y(0)], [330, Y(0)], [330, Y(12)], [130, Y(30)]], { fill: '#b9c4d2', stroke: C.ink }), poly([[330, Y(0)], [402, Y(0)], [402, Y(12)], [330, Y(12)]], { fill: '#b9c4d2', stroke: C.ink }),
      ...Array.from({ length: 17 }, (_, i) => line(334 + i * 4, Y(12), 336 + i * 4, Y(15), { width: 1 })),
      // inner ring: tapered bore on the sleeve, two shallow raceways on top
      path(`M180,${Y(25.5)} L300,${Y(14.7)} L300,${Y(64)} Q285,${Y(58)} 270,${Y(64)} L250,${Y(66)} L230,${Y(64)} Q215,${Y(58)} 200,${Y(64)} L180,${Y(64)}Z`, { fill: C.steel, stroke: C.ink }),
      // two rows of barrel rollers and a cage bar
      ...[210, 270].map((x) => path(`M${x - 15},${Y(66)} Q${x},${Y(58)} ${x + 15},${Y(66)} L${x + 15},${Y(96)} Q${x},${Y(106)} ${x - 15},${Y(96)}Z`, { fill: C.grey, stroke: C.ink, width: 1.2 })),
      rect(233, Y(92), 14, 20, { fill: C.paper, stroke: C.ink, width: 0.8 }),
      // outer ring with one spherical raceway (bulges away from the axis in the middle)
      path(`M172,${Y(98)} Q240,${Y(114)} 308,${Y(98)} L308,${Y(128)} L172,${Y(128)}Z`, { fill: C.steel, stroke: C.ink }),
      // lock washer (tab bent into a nut notch) and lock nut with notches
      rect(330, Y(56), 6, 56, { fill: C.accentDark, stroke: C.ink, width: 1 }), path(`M333,${Y(56)} L333,${Y(60)} L346,${Y(60)} L346,${Y(52)}`, { stroke: C.accentDark, width: 2.5 }),
      rect(336, Y(52), 32, 40, { fill: '#b9c4d2', stroke: C.ink }), ...[0, 1, 2].map((i) => rect(340 + i * 10, Y(52), 6, 8, { fill: C.grey, stroke: C.ink, width: 0.8 })),
      // hook spanner engaging a notch
      path(`M363,${Y(50)} L363,${Y(62)} Q400,${Y(80)} 440,${Y(140)}`, { stroke: C.ink, width: 7 }), path(`M363,${Y(50)} L363,${Y(62)} Q400,${Y(80)} 440,${Y(140)}`, { stroke: C.steel, width: 3.5 }),
      arc(372, Y(78), 40, -130, -80, { stroke: C.red, width: 1.5, arrow: 'end' }), text(432, Y(150), 'hook spanner:\ntighten the nut', { size: 9.5, anchor: 'middle' }),
      // feeler gauge between the outer ring and the top roller
      path(`M210,${Y(97)} L210,${Y(150)} L150,${Y(190)}`, { stroke: C.accent, width: 3 }), text(150, Y(198), 'feeler gauge: outer ring to top roller', { size: 10, fill: C.accentDark, anchor: 'middle' }),
      // leaders
      line(172, Y(112), 128, Y(112), { width: 0.8, stroke: C.muted }), text(124, Y(109), 'outer ring', { size: 9.5, anchor: 'end', fill: C.muted }),
      line(195, Y(84), 128, Y(84), { width: 0.8, stroke: C.muted }), text(124, Y(81), 'barrel rollers, 2 rows', { size: 9.5, anchor: 'end', fill: C.muted }),
      line(180, Y(45), 128, Y(45), { width: 0.8, stroke: C.muted }), text(124, Y(42), 'inner ring, tapered bore', { size: 9.5, anchor: 'end', fill: C.muted }),
      line(140, Y(18), 128, Y(18), { width: 0.8, stroke: C.muted }), text(124, Y(15), 'adapter sleeve', { size: 9.5, anchor: 'end', fill: C.muted }),
      line(368, Y(30), 412, Y(30), { width: 0.8, stroke: C.muted }), text(416, Y(27), 'lock nut', { size: 9.5, fill: C.muted }),
      line(336, Y(58), 336, Y(70), { width: 0.8, stroke: C.muted }), line(336, Y(70), 412, Y(70), { width: 0.8, stroke: C.muted }), text(416, Y(67), 'lock washer', { size: 9.5, fill: C.muted }),
      line(380, Y(6), 412, Y(6), { width: 0.8, stroke: C.muted }), text(416, Y(3), 'thread', { size: 9.5, fill: C.muted }),
      text(250, 26, 'Spherical roller bearing on an adapter sleeve (half-section)', { size: 11.5, weight: 700, anchor: 'middle' }),
      caption(500, 340, 'The nut drives the ring up the taper; stop at the table clearance drop.'),
    ], { title: 'Adapter sleeve drive-up' }))
}

// ---------- shared: tapered roller bearing (section), sprockets, stick figure ----------
/** Tapered roller bearing in section on a shaft whose top surface is at y = top and bottom at y = bot; x = bearing centre;
 *  big = +1 puts the roller large end (and cone rib) to the right, -1 to the left. h = radial height available (bore to housing). */
export function trb(x, top, bot, { big = 1, w = 36, h = 44 } = {}) {
  const half = (sgn, base) => { // sgn -1 above (y decreases with d), +1 below
    const Y = (d) => base + sgn * d, s = big
    const cone = poly([[x - 18, Y(0)], [x + 18, Y(0)], [x + 18, Y(h * 0.34 + (s > 0 ? 8 : 0))], [x + 18 * s, Y(h * 0.5)], [x + 18 * s, Y(h * 0.34 + 6)], [x - 18 * s, Y(h * 0.24)], [x - 18, Y(h * 0.24 - (s > 0 ? 0 : 0))]], { fill: C.steel, stroke: C.ink })
    const roller = poly([[x - 16 * s, Y(h * 0.25)], [x + 15 * s, Y(h * 0.36)], [x + 15 * s, Y(h * 0.70)], [x - 16 * s, Y(h * 0.54)]], { fill: C.grey, stroke: C.ink })
    const cup = poly([[x - 18 * s, Y(h * 0.56)], [x + 18 * s, Y(h * 0.72)], [x + 18 * s, Y(h)], [x - 18 * s, Y(h)]], { fill: C.steel, stroke: C.ink })
    return [rect(x - 18, Y(0), 36, sgn * h, { fill: C.paper, stroke: 'none' }).replace(/height="-?([\d.]+)"/, (m, v) => `height="${v}"`).replace(/y="([\d.]+)"/, (m, v) => `y="${sgn < 0 ? base - h : base}"`), cone, roller, cup]
  }
  return [...half(-1, top), ...half(1, bot)]
}
/** Sprocket, side view, centred (cx,cy), pitch radius r, n teeth. */
export function sprocket(cx, cy, r, n, opts = {}) {
  const pts = []
  for (let i = 0; i < n; i++) { const a = i * 360 / n, a2 = a + 180 / n; pts.push([cx + (r + 5) * Math.cos((a - 4) * P), cy + (r + 5) * Math.sin((a - 4) * P)], [cx + (r + 5) * Math.cos((a + 4) * P), cy + (r + 5) * Math.sin((a + 4) * P)], [cx + (r - 3) * Math.cos(a2 * P), cy + (r - 3) * Math.sin(a2 * P)]) }
  return [poly(pts, { fill: C.grey, stroke: C.ink, width: 1.2, ...opts }), circle(cx, cy, r * 0.28, { fill: C.steel, stroke: C.ink }), circle(cx, cy, 3, { fill: C.ink })]
}
/** Roller chain run along a path given by a sampling function p(t) -> [x,y], t in 0..1, with a pitch in px. */
export function chainRun(p, length, pitch = 11) {
  const n = Math.round(length / pitch), out = []
  for (let i = 0; i <= n; i++) { const [x, y] = p(i / n); out.push(circle(x, y, 3, { fill: C.steel, stroke: C.ink, width: 1 })) }
  for (let i = 0; i < n; i++) { const [x1, y1] = p(i / n), [x2, y2] = p((i + 1) / n); out.unshift(line(x1, y1, x2, y2, { width: 5, stroke: C.steelDark })) }
  return out
}
/** Stick person, head centre at (x,y), height h; colour c. */
export function person(x, y, h = 60, c = C.ink, { arms = [200, -20], legs = [100, 80] } = {}) {
  const r = h * 0.11, hip = y + h * 0.55
  return g([circle(x, y, r, { fill: C.paper, stroke: c, width: 2 }), line(x, y + r, x, hip, { stroke: c, width: 3 }),
    ...arms.map((a) => line(x, y + h * 0.25, x + Math.cos(a * P) * h * 0.3, y + h * 0.25 + Math.sin(a * P) * h * 0.3, { stroke: c, width: 2.5 })),
    ...legs.map((a) => line(x, hip, x + Math.cos(a * P) * h * 0.4, hip + Math.sin(a * P) * h * 0.4, { stroke: c, width: 2.5 }))])
}

// ---------- bearings/tapered-roller-end-play ----------
fig('bearings/tapered-roller-end-play.svg', 'Tapered roller bearing setting: cup in the housing, cone on the shaft; measure end play with an indicator on the shaft end while pushing and pulling',
  svg(500, 270, [
    rect(60, 56, 300, 148, { fill: '#b9c4d2', stroke: C.ink }), rect(130, 68, 160, 124, { fill: C.paper, stroke: C.ink }), // housing with its bore
    rect(40, 112, 400, 36, { fill: C.steel, stroke: C.ink }), line(40, 130, 440, 130, { width: 0.8, stroke: C.muted, dash: '10 4 2 4' }),
    ...trb(110, 112, 148, { big: -1 }), ...trb(310, 112, 148, { big: 1 }),
    rect(342, 100, 26, 60, { fill: '#b9c4d2', stroke: C.ink }), ...[0, 1, 2, 3].map((i) => line(345 + i * 6, 100, 349 + i * 6, 160, { width: 0.8 })), // adjusting nut
    dialInd(442, 130, { rot: 90, stem: 12, r: 14, needle: -100 }),
    line(22, 104, 56, 104, { width: 2.5, arrow: 'both', stroke: C.blue }), text(40, 96, 'push / pull', { size: 9.5, anchor: 'middle', fill: C.blue }),
    line(96, 48, 96, 36, { width: 0.8, stroke: C.muted }), text(96, 30, 'cup (outer race) pressed in the housing', { size: 9.5, fill: C.muted, anchor: 'start' }),
    line(300, 116, 300, 108, { width: 0.8, stroke: C.muted }), text(210, 42, 'cone (inner) with rollers and cage on the shaft', { size: 9.5, fill: C.muted }), line(230, 46, 292, 100, { width: 0.8, stroke: C.muted }),
    text(355, 176, 'adjusting nut', { size: 9.5, fill: C.muted, anchor: 'middle' }), text(462, 96, 'end play', { size: 9.5, fill: C.muted, anchor: 'middle' }),
    note(250, 222, 'cups face each other here (indirect mounting): the rollers take thrust both ways', { anchor: 'middle', size: 9.5 }),
    note(250, 240, 'adjust by nut or shims to 0.001-0.005 in end play cold; preload only where specified', { anchor: 'middle', size: 9.5 }),
    caption(500, 270, 'Rotate the shaft while seating; hot running end play is less than cold.'),
  ], { title: 'Tapered roller end play' }))

// ---------- gearboxes/shim-pack-preload ----------
fig('gearboxes/shim-pack-preload.svg', 'Tapered roller bearings are set by the shim pack under the cap: measure end play with a trial pack, then shim = trial pack + end play − target',
  svg(500, 280, [
    rect(40, 56, 280, 148, { fill: '#b9c4d2', stroke: C.ink }), rect(60, 68, 216, 124, { fill: C.paper, stroke: C.ink }),
    rect(20, 112, 380, 36, { fill: C.steel, stroke: C.ink }), line(20, 130, 400, 130, { width: 0.8, stroke: C.muted, dash: '10 4 2 4' }),
    ...trb(256, 112, 148, { big: 1 }),
    ...[0, 1, 2, 3, 4].map((i) => rect(320 + i * 2.4, 60, 2.4, 140, { fill: i % 2 ? C.accent : C.paper, stroke: C.accentDark, width: 0.6 })), // shim pack
    rect(332, 52, 22, 156, { fill: '#b9c4d2', stroke: C.ink }), rect(276, 96, 56, 68, { fill: '#b9c4d2', stroke: C.ink }), rect(276, 112, 56, 36, { fill: C.steel, stroke: C.ink }), // cap with nose bearing on the cup
    ...[64, 196].map((y) => [line(300, y, 354, y, { width: 1.2 }), rect(354, y - 5, 10, 10, { fill: C.ink })]), // cap bolts
    dialInd(402, 130, { rot: 90, stem: 12, r: 14, needle: -100 }),
    line(12, 104, 36, 104, { width: 2.5, arrow: 'both', stroke: C.blue }), text(30, 96, 'push / pull', { size: 9.5, anchor: 'middle', fill: C.blue }),
    line(326, 58, 326, 40, { width: 0.8, stroke: C.accentDark }), text(326, 34, 'shim pack under the cap flange', { size: 10, fill: C.accentDark, anchor: 'middle' }),
    text(343, 224, 'cap', { size: 9.5, anchor: 'middle', fill: C.muted }), text(420, 96, 'end play', { size: 9.5, anchor: 'middle', fill: C.muted }), text(250, 46, 'outer bearing: cup seats on the cap nose', { size: 9.5, fill: C.muted, anchor: 'middle' }), line(262, 50, 262, 66, { width: 0.8, stroke: C.muted }),
    note(250, 236, 'shims = trial pack + measured end play − target (0.001-0.003 in cold)', { anchor: 'middle', size: 10, fill: C.ink, weight: 600 }),
    note(250, 254, 'rotate the shaft while pushing to seat the rollers; check both directions', { anchor: 'middle', size: 9.5 }),
    caption(500, 280, 'Thick shims mid-pack, thin outside; keep each pack with its cap.'),
  ], { title: 'Shim pack preload' }))

// ---------- gearboxes/torque-arm-reducer ----------
fig('gearboxes/torque-arm-reducer.svg', 'Shaft-mount reducer on the driven shaft with a torque arm to the frame; belt drive from the motor',
  svg(500, 262, [
    rect(30, 214, 440, 12, { fill: '#b9c4d2', stroke: C.ink }),
    // motor on a pedestal, sheave on its shaft end (we look along the shafts)
    rect(70, 150, 70, 64, { fill: C.grey, stroke: C.ink }), rect(60, 64, 100, 76, { fill: C.grey, stroke: C.ink, rx: 8 }), rect(56, 140, 108, 10, { fill: C.steel, stroke: C.ink }),
    circle(110, 102, 22, { fill: C.steelDark, stroke: C.ink }), circle(110, 102, 14, { fill: C.grey, stroke: C.ink }), circle(110, 102, 4, { fill: C.ink }),
    // reducer housing: rounded, input sheave up-left, hollow output bore on the driven shaft
    path('M250,60 Q225,60 222,90 L222,120 Q222,150 262,170 L300,190 Q345,205 380,190 Q420,170 420,140 Q420,100 380,92 L300,66 Q280,60 250,60Z', { fill: C.grey, stroke: C.ink }),
    circle(285, 102, 34, { fill: C.steelDark, stroke: C.ink }), circle(285, 102, 24, { fill: C.grey, stroke: C.ink }), circle(285, 102, 5, { fill: C.ink }),
    circle(372, 150, 30, { fill: '#b9c4d2', stroke: C.ink }), circle(372, 150, 22, { fill: C.steelDark, stroke: C.ink }), circle(372, 150, 14, { fill: C.steel, stroke: C.ink }), rect(369, 132, 6, 6, { fill: C.ink, stroke: 'none' }),
    // belts
    line(110, 80, 285, 68, { width: 4, stroke: C.ink }), line(110, 124, 285, 136, { width: 4, stroke: C.ink }),
    // torque arm: lug on the housing at shaft height, turnbuckle rod straight down to the frame bracket
    rect(414, 144, 16, 12, { fill: C.ink, rx: 2 }), circle(422, 150, 3, { fill: C.paper, stroke: 'none' }),
    line(422, 156, 422, 214, { width: 5, stroke: C.accentDark }), rect(416, 172, 12, 26, { fill: C.accent, stroke: C.accentDark, rx: 3 }), poly([[408, 214], [436, 214], [430, 202], [414, 202]], { fill: C.ink }),
    line(372, 150, 422, 150, { width: 1, stroke: C.red, dash: '3 2' }), arc(422, 150, 26, 90, 180, { stroke: C.blue, width: 1 }), text(396, 182, '90°', { size: 9.5, fill: C.blue }),
    // labels
    text(110, 50, 'motor', { size: 10, anchor: 'middle', fill: C.muted }), text(198, 62, 'V-belts', { size: 10, anchor: 'middle', fill: C.muted }),
    text(300, 46, 'input sheave', { size: 10, fill: C.muted }), line(298, 50, 290, 66, { width: 0.8, stroke: C.muted }),
    text(448, 108, 'driven shaft', { size: 9.5, anchor: 'middle', fill: C.muted }), text(448, 119, 'in the hollow bore', { size: 9.5, anchor: 'middle', fill: C.muted }), line(394, 136, 430, 122, { width: 0.8, stroke: C.muted }),
    text(464, 182, 'torque', { size: 10, anchor: 'middle', fill: C.accentDark }), text(464, 193, 'arm', { size: 10, anchor: 'middle', fill: C.accentDark }),
    note(250, 246, 'the arm holds the housing still: keep it within 30° of a right angle to the shaft line', { anchor: 'middle', size: 9.5 }),
  ], { title: 'Torque arm reducer' }))

// ---------- power-transmission/chain-sag-and-wear ----------
{
  const A = [80, 82], B = [340, 82], rA = 30, rB = 54
  const top = (t) => [A[0] + (B[0] - A[0]) * t, A[1] - rA - 3 + ((B[1] - rB - 3) - (A[1] - rA - 3)) * t]
  const bot = (t) => { const x = A[0] + (B[0] - A[0]) * t, y0 = A[1] + rA + 3, y1 = B[1] + rB + 3; return [x, (1 - t) * (1 - t) * y0 + 2 * (1 - t) * t * ((y0 + y1) / 2 + 40) + t * t * y1] }
  fig('power-transmission/chain-sag-and-wear.svg', 'Roller chain: sag 2-4% of the span on the slack side, sprockets aligned with a straightedge, wear measured over 12 pitches',
    svg(500, 300, [
      ...sprocket(A[0], A[1], rA, 12), ...sprocket(B[0], B[1], rB, 21),
      ...chainRun(top, 262), ...chainRun(bot, 300),
      line(210, 124, 210, 140, { width: 1, arrow: 'both', stroke: C.blue }), line(80, 116, 340, 140, { width: 0.8, stroke: C.blue, dash: '3 3' }),
      text(210, 164, 'sag 2-4% of span: 10 in span = 1/4 in', { anchor: 'middle', size: 10, fill: C.blue }),
      text(210, 66, 'tight side on top', { anchor: 'middle', size: 10, fill: C.muted }), text(430, 82, 'driven', { size: 10, fill: C.muted }), text(30, 82, 'motor', { size: 10, fill: C.muted, anchor: 'end' }),
      // plan view: straightedge across both sprocket faces
      text(120, 196, 'Alignment (top view)', { anchor: 'middle', size: 11, weight: 700 }),
      line(60, 200, 60, 244, { width: 3, stroke: C.steelDark }), line(180, 200, 180, 244, { width: 3, stroke: C.steelDark }),
      rect(60 - 30, 218, 60, 9, { fill: C.grey, stroke: C.ink }), rect(180 - 54, 218, 108, 9, { fill: C.grey, stroke: C.ink }),
      rect(20, 212, 224, 5, { fill: C.accent, stroke: C.accentDark }), text(120, 258, 'straightedge touches both faces', { anchor: 'middle', size: 9.5, fill: C.muted }),
      // wear over 12 pitches
      text(370, 196, 'Wear (12 pitches)', { anchor: 'middle', size: 11, weight: 700 }),
      ...chainRun((t) => [286 + t * 168, 226], 168, 14), dim(286, 212, 454, 212, '12 pitches', { size: 9.5, ext: false }),
      text(370, 248, '#40 new: 6.000 in · replace at 3% = 6.180 in', { anchor: 'middle', size: 9.5, fill: C.muted }), text(370, 260, '(1.5% on sprockets over 67 teeth)', { anchor: 'middle', size: 9, fill: C.muted }),
      caption(500, 300, 'Measure the chain under light tension; a stretched chain rides up the teeth.'),
    ], { title: 'Chain sag and wear' }))
}

// ---------- power-transmission/key-and-keyway ----------
fig('power-transmission/key-and-keyway.svg', 'Square key: half in the shaft, half in the hub, sized from the shaft diameter; measure the keyway width with a gauge block',
  svg(500, 250, [
    circle(150, 138, 96, { fill: '#b9c4d2', stroke: C.ink }), circle(150, 138, 60, { fill: C.steel, stroke: C.ink }),
    rect(136, 64, 28, 28, { fill: C.accent, stroke: C.accentDark }), line(136, 78, 164, 78, { width: 0.8, stroke: C.accentDark, dash: '3 2' }),
    dim(136, 50, 164, 50, 'W', { size: 11, ext: false }), dim(126, 64, 126, 78, 'W/2', { size: 9, side: -1, ext: false }), dim(126, 78, 126, 92, 'W/2', { size: 9, side: -1, ext: false }),
    text(94, 70, 'in the hub', { size: 9.5, anchor: 'end', fill: C.muted }), text(94, 90, 'in the shaft', { size: 9.5, anchor: 'end', fill: C.muted }),
    text(150, 142, 'shaft', { size: 10, anchor: 'middle', fill: C.muted }), text(150, 222, 'hub', { size: 10, anchor: 'middle', fill: C.muted }), text(150, 84, '', { size: 1 }),
    table(290, 30, [['Shaft dia. (in)', 'Square key'], ['1/2 - 9/16', '1/8'], ['5/8 - 7/8', '3/16'], ['15/16 - 1-1/4', '1/4'], ['1-5/16 - 1-3/8', '5/16'], ['1-7/16 - 1-3/4', '3/8'], ['1-13/16 - 2-1/4', '1/2'], ['2-5/16 - 2-3/4', '5/8'], ['2-13/16 - 3-1/4', '3/4']], [110, 80], { rowH: 20, size: 10.5 }),
    caption(500, 250, 'Key length ≈ 1.5 × shaft dia.; snug sides, slight top clearance.'),
  ], { title: 'Key and keyway' }))

// ---------- power-transmission/timing-belt-tension ----------
{
  const toothed = (cx, cy, r, n) => [circle(cx, cy, r, { fill: C.grey, stroke: C.ink }), ...Array.from({ length: n }, (_, i) => { const a = i * 360 / n * P; return g([rect(r - 4, -2.2, 6, 4.4, { fill: C.steelDark, stroke: 'none' })], { transform: `translate(${cx},${cy}) rotate(${i * 360 / n})` }) }), circle(cx, cy, r * 0.3, { fill: C.steel, stroke: C.ink }), circle(cx, cy, 3, { fill: C.ink })]
  fig('power-transmission/timing-belt-tension.svg', 'Synchronous belt: tension by deflection force or frequency meter; flanges on at least one sprocket; alignment within 1/4°',
    svg(500, 240, [
      circle(400, 120, 70, { fill: '#e8edf3', stroke: C.steelDark, width: 1.2 }), // flange disc behind the big sprocket
      ...toothed(90, 120, 40, 16), ...toothed(400, 120, 62, 26),
      line(90, 78, 400, 56, { width: 7, stroke: C.ink }), line(90, 162, 400, 184, { width: 7, stroke: C.ink }),
      ...Array.from({ length: 26 }, (_, i) => { const t = i / 25, x = 96 + t * 298; return [line(x, 81 + t * -22 + 1, x, 86 + t * -22, { stroke: C.paper, width: 1.5 }), line(x, 159 + t * 22 - 1, x, 154 + t * 22, { stroke: C.paper, width: 1.5 })] }),
      line(245, 42, 245, 62, { width: 3, arrow: 'end', stroke: C.red }), text(245, 34, 'deflection force from the belt chart (or a sonic tension meter)', { anchor: 'middle', size: 10, fill: C.red }),
      line(470, 92, 486, 70, { width: 0.8, stroke: C.muted }), text(486, 66, 'flange', { size: 9.5, fill: C.muted, anchor: 'end' }),
      text(370, 208, 'flange: a thin disc on each face keeps the belt on', { anchor: 'middle', size: 9.5, fill: C.muted }),
      note(20, 228, 'too loose = tooth jump; too tight = bearing load, whine', { size: 10 }),
    ], { title: 'Timing belt tension' }))
}

// ---------- conveyors/idler-set-and-pulley ----------
fig('conveyors/idler-set-and-pulley.svg', 'Troughing idler set (20°, 35° or 45°), return idler and a lagged drive pulley',
  svg(500, 250, [
    text(140, 22, 'Troughing idler set (end view)', { anchor: 'middle', weight: 700, size: 12 }),
    rect(20, 176, 244, 10, { fill: '#b9c4d2', stroke: C.ink }), rect(26, 104, 8, 72, { fill: C.steelDark, stroke: C.ink }), rect(250, 104, 8, 72, { fill: C.steelDark, stroke: C.ink }),
    rect(96, 142, 88, 20, { fill: C.grey, stroke: C.ink, rx: 10 }),
    g([rect(0, -10, 74, 20, { fill: C.grey, stroke: C.ink, rx: 10 })], { transform: 'translate(184,152) rotate(-35)' }), g([rect(-74, -10, 74, 20, { fill: C.grey, stroke: C.ink, rx: 10 })], { transform: 'translate(96,152) rotate(35)' }),
    path('M36,100 L94,140 L186,140 L244,100', { stroke: C.accentDark, width: 5 }), path('M62,118 Q140,66 218,118 Q140,132 62,118Z', { fill: '#c9a27a', stroke: '#8a6a45', width: 1 }),
    angle(186, 140, 30, 180, 215, '35°', { size: 10 }), text(140, 204, 'centre roll + two wing rolls; the belt troughs', { anchor: 'middle', size: 9.5, fill: C.muted }),
    text(140, 232, 'return idler: single flat roll under the return belt', { anchor: 'middle', size: 9.5, fill: C.muted }), rect(90, 214, 100, 12, { fill: C.grey, stroke: C.ink, rx: 6 }), line(60, 212, 220, 212, { stroke: C.accentDark, width: 4 }),
    text(380, 22, 'Drive pulley with lagging', { anchor: 'middle', weight: 700, size: 12 }),
    circle(380, 110, 60, { fill: C.grey, stroke: C.ink }), circle(380, 110, 50, { fill: '#3b3b3b', stroke: C.ink }), ...[-30, -10, 10, 30].map((d) => g([line(-46, 0, 46, 0, { stroke: '#666', width: 2 })], { transform: `translate(380,${110 + d}) rotate(${d * 0.9})` })), circle(380, 110, 12, { fill: C.steel, stroke: C.ink }),
    path('M300,50 L380,50 A60,60 0 0 1 380,170 L300,170', { stroke: C.accentDark, width: 5 }),
    text(380, 196, 'rubber or ceramic lagging grips the belt;', { anchor: 'middle', size: 9.5, fill: C.muted }), text(380, 208, 'worn smooth = slip; crowned tail pulley tracks', { anchor: 'middle', size: 9.5, fill: C.muted }),
  ], { title: 'Idler set and pulley' }))

// ---------- conveyors/screw-and-bucket-elevator ----------
{
  const screw = (x0, cy, n, pitch, r) => { const out = []; for (let i = 0; i < n; i++) { const x = x0 + i * pitch; out.push(path(`M${x},${cy - r} C${x + pitch * 0.5},${cy - r} ${x + pitch * 0.5},${cy + r} ${x + pitch},${cy + r}`, { stroke: C.steelDark, width: 4 }), path(`M${x},${cy + r} C${x + pitch * 0.5},${cy + r} ${x + pitch * 0.5},${cy - r} ${x + pitch},${cy - r}`, { stroke: C.steel, width: 2.5 })) } return out }
  fig('conveyors/screw-and-bucket-elevator.svg', 'Screw conveyor (hand of the flight sets the direction) and a centrifugal-discharge bucket elevator',
    svg(500, 262, [
      text(130, 22, 'Screw conveyor', { anchor: 'middle', weight: 700, size: 12 }),
      path('M20,60 L20,120 Q20,150 50,150 L210,150 Q240,150 240,120 L240,60', { fill: C.grey, stroke: C.ink }), rect(10, 56, 240, 6, { fill: C.steel, stroke: C.ink }),
      line(20, 105, 240, 105, { width: 6, stroke: C.steelDark }), ...screw(24, 105, 6, 36, 34), rect(120, 96, 20, 18, { fill: C.ink, rx: 2 }),
      line(60, 168, 200, 168, { width: 2.5, arrow: 'end', stroke: C.blue }), text(130, 184, 'flow (right-hand flight, clockwise)', { anchor: 'middle', size: 10, fill: C.blue }),
      note(130, 206, 'trough 30-45% full; hanger bearings mid-span;\nnever reach in: it is a permit space', { anchor: 'middle', size: 9.5 }),
      text(375, 22, 'Bucket elevator', { anchor: 'middle', weight: 700, size: 12 }),
      rect(340, 34, 70, 200, { fill: C.grey, stroke: C.ink }), rect(320, 210, 110, 34, { fill: C.grey, stroke: C.ink, rx: 4 }), rect(330, 28, 90, 28, { fill: C.grey, stroke: C.ink, rx: 4 }),
      circle(375, 50, 18, { fill: C.steel, stroke: C.ink }), circle(375, 222, 14, { fill: C.steel, stroke: C.ink }),
      line(357, 50, 357, 222, { width: 4, stroke: C.ink }), line(393, 50, 393, 222, { width: 4, stroke: C.ink }),
      ...[70, 100, 130, 160, 190].map((y) => [path(`M393,${y} L410,${y} L406,${y + 14} L393,${y + 14}Z`, { fill: C.accent, stroke: C.accentDark }), path(`M357,${y + 15} L340,${y + 15} L344,${y + 29} L357,${y + 29}Z`, { fill: C.accent, stroke: C.accentDark })]),
      arc(375, 50, 26, 200, 340, { stroke: C.blue, width: 1.5, arrow: 'end' }), path('M400,40 L440,44 L440,70', { stroke: C.ink, width: 1.5 }), line(422, 46, 434, 62, { width: 2, arrow: 'end', stroke: C.blue }), text(456, 64, 'discharge', { size: 9.5, fill: C.blue, anchor: 'middle' }),
      path('M300,200 L322,214', { stroke: C.blue, width: 2, arrow: 'end' }), text(296, 196, 'feed', { size: 9.5, fill: C.blue, anchor: 'end' }),
      text(410, 106, 'up', { size: 9, fill: C.muted }), text(330, 128, 'down', { size: 9, fill: C.muted, anchor: 'end' }),
      note(375, 254, 'tension, tracking, boot clean-out, lagging', { anchor: 'middle', size: 9.5 }),
    ], { title: 'Screw conveyor and bucket elevator' }))
}

// ---------- hydraulics/cylinder-seal-orientation ----------
fig('hydraulics/cylinder-seal-orientation.svg', 'Cylinder seals: wiper lip out, rod seal lip toward the pressure, wear rings each side of the piston seal, piston seals face their own pressure side',
  svg(500, 250, [
    rect(30, 52, 350, 12, { fill: '#b9c4d2', stroke: C.ink }), rect(30, 176, 350, 12, { fill: '#b9c4d2', stroke: C.ink }), rect(30, 64, 40, 112, { fill: '#dbeafe', stroke: 'none' }), // barrel, oil on the cap side
    rect(150, 108, 330, 24, { fill: C.steel, stroke: C.ink }), // rod
    rect(80, 66, 70, 108, { fill: C.grey, stroke: C.ink }), // piston
    ...[[88, 'wear'], [134, 'wear']].map(([x]) => [rect(x, 66, 8, 6, { fill: '#7c5cff', stroke: C.ink, width: 0.8 }), rect(x, 168, 8, 6, { fill: '#7c5cff', stroke: C.ink, width: 0.8 })]),
    ...[66, 168].map((y) => [rect(108, y, 14, 6, { fill: C.ink, rx: 1 }), rect(105, y + (y === 66 ? 6 : -4), 20, 4, { fill: C.red, stroke: 'none' })]), // T-seal: elastomer T with backup rings
    rect(380, 56, 80, 128, { fill: C.grey, stroke: C.ink }), rect(380, 108, 80, 24, { fill: C.steel, stroke: C.ink }), // gland
    rect(388, 98, 12, 10, { fill: '#7c5cff', stroke: C.ink, width: 0.8 }), rect(388, 132, 12, 10, { fill: '#7c5cff', stroke: C.ink, width: 0.8 }), // gland bearing
    path('M414,108 L414,98 L428,98 L428,108 L424,108 L424,102 L418,102 L418,108Z', { fill: C.red, stroke: C.ink, width: 0.8 }), path('M414,132 L414,142 L428,142 L428,132 L424,132 L424,138 L418,138 L418,132Z', { fill: C.red, stroke: C.ink, width: 0.8 }), // rod seal U-cup, lips open toward the oil (left)
    path('M446,108 L446,100 L456,100 L456,108 L452,108 L452,104Z', { fill: C.ink }), path('M446,132 L446,140 L456,140 L456,132 L452,132 L452,136Z', { fill: C.ink }), // wiper, lip out (right)
    callout(1, 452, 82), callout(2, 421, 82), callout(3, 394, 82), callout(4, 92, 44), callout(5, 115, 44),
    line(70, 120, 120, 120, { width: 2, arrow: 'end', stroke: C.blue }), text(52, 100, 'oil', { size: 9.5, fill: C.blue, anchor: 'middle' }),
    text(472, 100, 'dirt side', { size: 9, fill: C.muted, anchor: 'middle' }),
    note(250, 206, '1 wiper: lip OUT · 2 rod seal: U-cup lips IN toward the oil · 3 gland bearing / wear ring', { anchor: 'middle', size: 9.8 }),
    note(250, 223, '4 piston wear rings both sides · 5 piston seal: T-seal, or two U-cups back to back', { anchor: 'middle', size: 9.8 }),
    caption(500, 250, 'A seal in backwards leaks on the first stroke: check the lip first.'),
  ], { title: 'Cylinder seal orientation' }))

// ---------- installation/pipe-strain-check ----------
fig('installation/pipe-strain-check.svg', 'Pipe strain test: indicators on the pump shaft (vertical and horizontal); loosen the flange bolts; more than 0.002 in movement is pipe strain',
  svg(500, 305, [
    text(120, 22, 'Shaft end view: two indicators', { anchor: 'middle', weight: 700, size: 12 }),
    rect(20, 200, 210, 10, { fill: C.steel, stroke: C.ink }), rect(40, 190, 170, 10, { fill: C.grey, stroke: C.ink }),
    circle(120, 120, 46, { fill: C.grey, stroke: C.ink }), circle(120, 120, 22, { fill: C.steel, stroke: C.ink }), rect(117, 98, 6, 8, { fill: C.ink, stroke: 'none' }),
    dialInd(120, 98, { stem: 14, r: 14, needle: -90 }), rect(116, 46, 8, 12, { fill: C.steelDark, stroke: C.ink }), rect(116, 40, 92, 7, { fill: C.steelDark, stroke: C.ink }),
    dialInd(142, 120, { rot: 90, stem: 12, r: 13, needle: -90 }), rect(180, 117, 26, 6, { fill: C.steelDark, stroke: C.ink }), rect(204, 100, 8, 90, { fill: C.steelDark, stroke: C.ink }), rect(198, 176, 30, 14, { fill: C.ink, rx: 2 }),
    text(100, 36, 'vertical', { size: 9.5, anchor: 'middle', fill: C.blue }), text(172, 150, 'horizontal', { size: 9.5, fill: C.blue, anchor: 'middle' }),
    note(120, 228, 'mag bases on the pump base, not the pipe;\nzero both, then loosen the flange bolts', { anchor: 'middle', size: 9.5 }),
    text(370, 22, 'Side view: flange bolts loosened', { anchor: 'middle', weight: 700, size: 12 }),
    rect(260, 200, 220, 10, { fill: C.steel, stroke: C.ink }), rect(300, 190, 80, 10, { fill: C.grey, stroke: C.ink }),
    circle(340, 140, 44, { fill: C.grey, stroke: C.ink }), circle(340, 140, 16, { fill: C.steel, stroke: C.ink }), rect(270, 130, 30, 20, { fill: C.steel, stroke: C.ink }),
    rect(332, 76, 16, 22, { fill: C.grey, stroke: C.ink }), rect(322, 66, 36, 10, { fill: C.grey, stroke: C.ink }), // discharge flange on the pump
    g([rect(322, 60, 36, 10, { fill: C.steel, stroke: C.ink }), path('M340,60 L340,52 L470,52', { stroke: C.ink, width: 18 }), path('M340,60 L340,52 L470,52', { stroke: C.steel, width: 15 })], { transform: 'rotate(-4 340 70)' }), // pipe flange, springs away when loose
    ...[326, 354].map((x) => [line(x, 58, x, 80, { width: 2, stroke: C.ink }), rect(x - 4, 80, 8, 5, { fill: C.ink })]),
    line(304, 70, 320, 70, { width: 1.5, arrow: 'both', stroke: C.red }), text(300, 74, 'gap opens: strain', { size: 9.5, fill: C.red, anchor: 'end' }),
    text(432, 78, 'piping', { size: 9.5, fill: C.muted }), text(340, 210 + 12, 'pump', { size: 9.5, fill: C.muted, anchor: 'middle' }),
    note(370, 244, 'limits before bolting: faces parallel within\n0.010 in, offset 0.030 in, gap within the gasket', { anchor: 'middle', size: 9.5 }),
    note(250, 282, 'more than 0.002 in shaft movement when the bolts come loose = pipe strain', { anchor: 'middle', size: 10, fill: C.red }),
    caption(500, 305, 'Fix the pipe, not the pump: never pull a flange in with the bolts.'),
  ], { title: 'Pipe strain check' }))

// ---------- layout-templates/centre-finding ----------
fig('layout-templates/centre-finding.svg', 'Finding the centre of round stock: two scribed lines with a centre head, or three with a surface gauge on V-blocks',
  svg(500, 260, [
    text(125, 22, 'Centre head', { anchor: 'middle', weight: 700, size: 12 }),
    circle(125, 120, 66, { fill: C.steel, stroke: C.ink, width: 2 }),
    // centre head: a 90° V straddling the bar, rule along the bisector through the centre
    g([poly([[0, 0], [-70, 70], [-58, 82], [0, 24], [58, 82], [70, 70]], { fill: C.grey, stroke: C.ink }), rect(-9, -24, 18, 114, { fill: '#e9d9a8', stroke: C.accentDark }), ...Array.from({ length: 11 }, (_, i) => line(-9, -20 + i * 10, i % 2 ? -4 : -1, -20 + i * 10, { width: 0.8 }))], { transform: 'translate(125,120) rotate(-30) translate(0,-93)' }),
    g([line(0, -80, 0, 80, { stroke: C.red, width: 1.2 })], { transform: 'translate(125,120) rotate(-30)' }), g([line(0, -80, 0, 80, { stroke: C.red, width: 1.2, dash: '5 3' })], { transform: 'translate(125,120) rotate(60)' }),
    circle(125, 120, 3, { fill: C.red, stroke: 'none' }),
    note(125, 212, 'V on the rim, scribe along the rule;\nturn 90°, scribe again: they cross at centre', { anchor: 'middle', size: 9.5 }),
    text(375, 22, 'Surface gauge on V-blocks', { anchor: 'middle', weight: 700, size: 12 }),
    rect(280, 190, 190, 10, { fill: '#b9c4d2', stroke: C.ink }), poly([[300, 190], [300, 150], [330, 150], [356, 176], [382, 150], [412, 150], [412, 190]], { fill: C.grey, stroke: C.ink }),
    circle(356, 128, 44, { fill: C.steel, stroke: C.ink, width: 2 }),
    rect(430, 178, 40, 12, { fill: C.steelDark, stroke: C.ink, rx: 2 }), line(450, 178, 450, 110, { width: 4, stroke: C.ink }), line(450, 128, 402, 128, { width: 2.5, stroke: C.ink }), circle(450, 128, 4, { fill: C.grey, stroke: C.ink }),
    ...[0, 120, 240].map((a, i) => g([line(-46, 0, 46, 0, { stroke: C.red, width: 1.2, dash: i ? '5 3' : undefined })], { transform: `translate(356,${128 + 4}) rotate(${a})` })),
    note(375, 212, 'scriber at half height, turn the bar 120°,\ntwice: the small triangle is the centre', { anchor: 'middle', size: 9.5 }),
    caption(500, 260, 'Punch the centre lightly, then check it with dividers before drilling.'),
  ], { title: 'Finding centre of round stock' }))

// ---------- machining/tram-and-keyway ----------
fig('machining/tram-and-keyway.svg', 'Tramming the mill head: sweep an indicator on the table in a 10 in circle, both axes, to zero; cut a shaft keyway to depth W/2 centred with an edge finder',
  svg(500, 262, [
    text(125, 22, 'Tramming the head', { anchor: 'middle', weight: 700, size: 12 }),
    rect(30, 170, 200, 16, { fill: '#b9c4d2', stroke: C.ink }), ...[0, 1, 2].map((i) => rect(44 + i * 64, 174, 40, 8, { fill: C.grey, stroke: C.ink })), // table with T-slots
    rect(96, 40, 58, 50, { fill: C.grey, stroke: C.ink, rx: 4 }), rect(112, 90, 26, 24, { fill: C.steel, stroke: C.ink }), rect(118, 114, 14, 14, { fill: C.steelDark, stroke: C.ink }), // head, quill, collet
    rect(122, 128, 6, 14, { fill: C.ink }), line(125, 140, 190, 140, { width: 4, stroke: C.ink }), // holder bar
    dialInd(190, 170, { stem: 10, r: 12, needle: -80 }), path('M60,170 A65,10 0 0 0 190,170', { stroke: C.blue, width: 1.2, dash: '4 3' }), path('M60,170 A65,10 0 0 1 190,170', { stroke: C.blue, width: 1.2, dash: '4 3' }),
    arc(125, 150, 30, 200, 340, { stroke: C.blue, width: 1.2, arrow: 'end' }), text(125, 200, '10 in circle', { anchor: 'middle', size: 9.5, fill: C.blue }),
    note(125, 226, 'sweep front-back, then side-side;\ntilt the head until the reading repeats', { anchor: 'middle', size: 9.5 }),
    text(375, 22, 'Shaft keyway', { anchor: 'middle', weight: 700, size: 12 }),
    rect(280, 150, 190, 24, { fill: '#b9c4d2', stroke: C.ink }), poly([[300, 150], [300, 128], [330, 128], [330, 150]], { fill: C.grey, stroke: C.ink }), poly([[420, 150], [420, 128], [450, 128], [450, 150]], { fill: C.grey, stroke: C.ink }), // vise jaws
    rect(300, 100, 150, 40, { fill: C.steel, stroke: C.ink, rx: 4 }), rect(350, 100, 60, 10, { fill: C.paper, stroke: C.ink }), // shaft with a keyway cut
    rect(392, 40, 16, 46, { fill: C.steelDark, stroke: C.ink }), rect(388, 86, 24, 18, { fill: C.grey, stroke: C.ink }), ...[0, 1, 2, 3].map((i) => line(390 + i * 6, 88, 393 + i * 6, 104, { width: 1 })), // end mill
    line(400, 60, 400, 76, { width: 1, stroke: C.blue, dash: '3 2' }), text(300, 60, 'W/2 + a hair deep', { size: 9.5, fill: C.blue }),
    dim(348, 122, 412, 122, 'W', { size: 9.5, ext: false }), dim(432, 100, 432, 110, 'W/2', { size: 9, ext: false }),
    note(375, 226, 'edge-find both sides, centre = half the shaft\ndiameter; cut in 2-3 passes; deburr', { anchor: 'middle', size: 9.5 }),
    caption(500, 262, 'Tram before any keyway: a nodding head cuts a tapered slot.'),
  ], { title: 'Tramming and keyway' }))

// ---------- rigging/shackle-loading ----------
{
  const shackle = (x, y, rot, { pull = 90, label, pct, ok } = {}) => { // bow at the bottom, pin across the top
    const body = g([
      path('M-22,-30 L-22,0 A22,22 0 0 0 22,0 L22,-30', { stroke: C.ink, width: 10 }), path('M-22,-30 L-22,0 A22,22 0 0 0 22,0 L22,-30', { stroke: C.steel, width: 6 }),
      rect(-30, -38, 60, 9, { fill: C.steelDark, stroke: C.ink, rx: 3 }), rect(30, -41, 8, 15, { fill: C.ink, rx: 2 }), circle(-24, -33.5, 3, { fill: C.grey, stroke: C.ink, width: 0.8 }),
      // sling eye in the bow
      path('M-12,4 Q0,26 12,4', { stroke: '#2d6a4f', width: 7 }), path('M-12,4 Q0,26 12,4', { stroke: '#52b788', width: 4 }),
      // hook on the pin
      path('M0,-38 L0,-60 Q-10,-70 0,-78', { stroke: C.ink, width: 5 }),
    ], { transform: `translate(${x},${y}) rotate(${rot})` })
    const a = pull * P
    return [body, line(x + Math.cos(a) * 16, y + Math.sin(a) * 16, x + Math.cos(a) * 60, y + Math.sin(a) * 60, { stroke: C.red, width: 3, arrow: 'end' }), text(x, y - 92, label, { anchor: 'middle', size: 11.5, weight: 700, fill: ok ? C.green : C.red }), text(x, y + 82, pct, { anchor: 'middle', size: 10.5, fill: ok ? C.green : C.red })]
  }
  fig('rigging/shackle-loading.svg', 'Shackle loading: the running sling in the bow, the fixed eye or hook on the pin; side loads derate 45° to 70% and 90° to 50%; mouse the pin',
    svg(500, 240, [
      ...shackle(90, 120, 0, { pull: 90, label: 'Right: in line', pct: '100% of WLL', ok: true }),
      ...shackle(250, 120, 0, { pull: 45, label: 'Side load 45°', pct: '70% of WLL' }),
      ...shackle(410, 120, 0, { pull: 0, label: 'Side load 90°', pct: '50% of WLL' }),
      note(250, 216, 'sling eye rides in the bow, hook or fixed eye on the pin; the pull runs along the shackle axis', { anchor: 'middle', size: 9.5 }),
      caption(500, 240, 'WLL forged on the bow; two slings in one bow: 120° included angle max.'),
    ], { title: 'Shackle loading' }))
}

// ---------- rigging/sling-angles-and-hitches ----------
{
  const hookAt = (x, y) => [path(`M${x},${y - 20} L${x},${y - 6} Q${x - 12},${y + 8} ${x},${y + 12} Q${x + 10},${y + 6} ${x + 6},${y}`, { stroke: C.ink, width: 5 }), circle(x, y - 24, 5, { fill: C.grey, stroke: C.ink })]
  const load = (x, y, w, h) => [rect(x - w / 2, y, w, h, { fill: '#b9c4d2', stroke: C.ink }), ...[-1, 1].map((s) => circle(x + s * (w / 2 - 10), y - 2, 4, { fill: C.ink }))]
  const legs = (x, y, w, ang, label, mult) => { // two legs from the hook to the lift points, at angle from horizontal
    const half = w / 2 - 10, hy = y - Math.tan(ang * P) * half
    return [...hookAt(x, hy - 12), ...[-1, 1].map((s) => line(x, hy, x + s * half, y - 2, { stroke: '#2d6a4f', width: 4 })), ...load(x, y, w, 26),
      angle(x - half, y - 2, 22, -ang, 0, `${ang}°`, { size: 9 }), text(x, y + 42, label, { anchor: 'middle', size: 10.5, weight: 700 }), text(x, y + 56, mult, { anchor: 'middle', size: 10, fill: C.red })]
  }
  fig('rigging/sling-angles-and-hitches.svg', 'Sling angle multiplies leg tension: 60° × 1.15, 45° × 1.41, 30° × 2.0; vertical, choker (80%) and basket (200%) hitches',
    svg(500, 320, [
      text(250, 20, 'Sling angle (from horizontal)', { anchor: 'middle', weight: 700, size: 12 }),
      ...legs(85, 120, 100, 60, '60°', 'tension × 1.15'), ...legs(250, 120, 110, 45, '45°', 'tension × 1.41'), ...legs(415, 120, 130, 30, '30°', 'tension × 2.00'),
      note(250, 196, 'leg tension = (load ÷ legs) × factor: 2,000 lb on two legs at 30° = 2,000 lb per leg', { anchor: 'middle', size: 9.5 }),
      text(250, 220, 'Hitches', { anchor: 'middle', weight: 700, size: 12 }),
      // vertical
      ...hookAt(85, 240), line(85, 252, 85, 276, { stroke: '#2d6a4f', width: 4 }), ...load(85, 278, 60, 18), text(85, 312, 'Vertical 100%', { anchor: 'middle', size: 10 }),
      // choker: sling goes around the load and back through its own eye
      ...hookAt(250, 240), path('M250,252 L262,268 L280,268 L280,292 L220,292 L220,268 L262,268', { stroke: '#2d6a4f', width: 4, fill: 'none' }), circle(262, 268, 4, { fill: C.paper, stroke: '#2d6a4f', width: 2 }), rect(222, 270, 56, 20, { fill: '#b9c4d2', stroke: C.ink }), text(250, 312, 'Choker 80%', { anchor: 'middle', size: 10 }),
      // basket: sling under the load, both eyes on the hook
      ...hookAt(415, 240), path('M415,252 L392,268 L385,296 L445,296 L438,268 L415,252', { stroke: '#2d6a4f', width: 4, fill: 'none' }), rect(388, 270, 54, 22, { fill: '#b9c4d2', stroke: C.ink }), text(415, 312, 'Basket 200%', { anchor: 'middle', size: 10 }),
      note(250, 300, '', { size: 1 }),
    ], { title: 'Sling angles and hitches' }))
}

// ---------- safety/confined-space-setup ----------
fig('safety/confined-space-setup.svg', 'Confined space entry: tested atmosphere, blower ducted to the bottom, entrant on a harness and retrieval line, attendant at the opening, supervisor with the permit, rescue on call',
  svg(500, 310, [
    rect(0, 150, 500, 150, { fill: C.grey, stroke: 'none' }), line(0, 150, 500, 150, { width: 2 }), // ground line, tank below grade
    path('M120,150 L120,200 Q120,290 210,290 L330,290 Q420,290 420,200 L420,150', { fill: C.paper, stroke: C.ink, width: 2 }), rect(120, 150, 300, 12, { fill: C.paper, stroke: 'none' }), line(120, 150, 232, 150, { width: 2 }), line(308, 150, 420, 150, { width: 2 }),
    rect(232, 140, 76, 10, { fill: C.steelDark, stroke: C.ink }), text(312, 176, 'manway', { size: 9, fill: C.muted }),
    // tripod with winch and retrieval line to the entrant
    line(270, 40, 220, 140, { width: 3 }), line(270, 40, 320, 140, { width: 3 }), line(270, 40, 270, 100, { width: 3, dash: '4 3' }), circle(270, 40, 5, { fill: C.ink }), rect(224, 90, 14, 12, { fill: C.accent, stroke: C.accentDark }), line(270, 40, 270, 205, { stroke: C.red, width: 1.5 }),
    person(270, 215, 56, C.ink), rect(263, 225, 14, 14, { fill: 'none', stroke: C.accent, width: 2 }), // entrant with harness
    // blower and duct to the bottom
    rect(30, 116, 44, 34, { fill: C.grey, stroke: C.ink, rx: 4 }), circle(52, 133, 11, { fill: C.paper, stroke: C.ink }), path('M74,133 L100,133 Q116,133 116,150 L116,275 Q116,282 124,282 L180,282', { stroke: C.blue, width: 8, fill: 'none' }), line(182, 282, 200, 282, { stroke: C.blue, width: 2, arrow: 'end' }),
    text(52, 108, 'blower', { size: 9.5, anchor: 'middle', fill: C.muted }), text(150, 270, 'duct to the bottom', { size: 9, fill: C.blue }),
    // attendant at the opening with a monitor, supervisor with the permit, rescue
    person(360, 78, 62, C.ink, { arms: [200, 320] }), rect(330, 96, 14, 10, { fill: C.green, stroke: C.ink }), text(338, 92, '20.9', { size: 6.5, fill: C.paper, anchor: 'middle' }), text(340, 147, 'attendant: never enters', { size: 8.5, anchor: 'middle', fill: C.muted }),
    person(450, 72, 62, C.ink, { arms: [160, 340] }), rect(428, 84, 16, 22, { fill: C.paper, stroke: C.ink }), text(455, 147, 'supervisor: permit', { size: 8.5, anchor: 'middle', fill: C.muted }),
    text(14, 30, 'gas test before entry, then continuously:', { size: 9.5, weight: 600 }), text(14, 44, 'O₂ 19.5-23.5%, LEL under 10%,', { size: 9.5 }), text(14, 58, 'H₂S under 10 ppm, CO under 25 ppm', { size: 9.5 }),
    text(14, 78, 'rescue team on call before entry', { size: 9.5, fill: C.red }),
    caption(500, 310, 'Entrant: harness on the retrieval line, monitor on, radio to the attendant.'),
  ], { title: 'Confined space setup' }))

// ---------- safety/fall-clearance-and-ladder ----------
fig('safety/fall-clearance-and-ladder.svg', 'Fall clearance with a 6 ft lanyard: lanyard 6 + deceleration 3.5 + harness stretch 1 + worker below D-ring 5 + safety 3 = 18.5 ft below the anchor; ladder at 4:1',
  svg(500, 320, [
    text(130, 20, 'Fall clearance (6 ft lanyard)', { anchor: 'middle', weight: 700, size: 12 }),
    rect(40, 30, 180, 8, { fill: C.steelDark, stroke: C.ink }), circle(130, 42, 5, { fill: C.ink }), // beam anchor
    rect(20, 290, 220, 8, { fill: C.grey, stroke: C.ink }), text(130, 286, 'obstruction / lower level', { size: 8.5, anchor: 'middle', fill: C.muted }),
    // segments stacked from the anchor
    ...[[42, 6, '6 ft lanyard', C.ink], [6 * 12.6 + 42, 3.5, '3.5 ft deceleration', C.red], [9.5 * 12.6 + 42, 1, '1 ft harness stretch', C.accentDark], [10.5 * 12.6 + 42, 5, '5 ft D-ring to feet', C.blue], [15.5 * 12.6 + 42, 3, '3 ft safety', C.green]]
      .map(([y0, ft, l, c]) => [line(130, y0, 130, y0 + ft * 12.6, { stroke: c, width: 3 }), line(124, y0 + ft * 12.6, 136, y0 + ft * 12.6, { stroke: c, width: 1.5 }), text(146, y0 + ft * 6.3 + 4, l, { size: 9.5, fill: c })]),
    person(90, 186, 70, C.blue, { arms: [-60, 240], legs: [80, 100] }), line(130, 42 + 6 * 12.6 + 12, 100, 190, { stroke: C.ink, width: 2 }), // worker hanging under the lanyard end
    dim(52, 42, 52, 42 + 18.5 * 12.6, '18.5 ft', { size: 10, side: -1, ext: false }),
    note(130, 306, 'foot-level anchor adds 6 ft: use overhead or an SRL', { anchor: 'middle', size: 8.8 }),
    text(375, 20, 'Ladder angle 4:1', { anchor: 'middle', weight: 700, size: 12 }),
    rect(440, 30, 30, 260, { fill: '#b9c4d2', stroke: C.ink }), rect(280, 290, 200, 8, { fill: C.grey, stroke: C.ink }), rect(400, 100, 40, 8, { fill: C.steelDark, stroke: C.ink }), text(420, 96, 'landing', { size: 8.5, anchor: 'middle', fill: C.muted }),
    ...[-7, 7].map((d) => g([line(0, 0, 0, -246, { width: 4, stroke: C.accentDark })], { transform: `translate(${375 + d},290) rotate(-14)` })), ...Array.from({ length: 11 }, (_, i) => g([line(-7, -18 - i * 21, 7, -18 - i * 21, { width: 3, stroke: C.accentDark })], { transform: 'translate(375,290) rotate(-14)' })),
    dim(375, 290 + 0, 436, 290, '1 out', { size: 9.5, ext: false }), dim(470, 108, 470, 290, '4 up', { size: 9.5, ext: false }), dim(316, 46, 316, 108, '3 ft above', { size: 9, ext: false, side: -1 }), line(320, 46, 420, 46, { width: 0.6, stroke: C.line, dash: '2 2' }), line(320, 108, 400, 108, { width: 0.6, stroke: C.line, dash: '2 2' }),
    note(375, 306, 'tie off the top; firm footing; 3 points of contact', { anchor: 'middle', size: 8.8 }),
  ], { title: 'Fall clearance and ladder' }))

// ---------- safety/hot-work-zone ----------
fig('safety/hot-work-zone.svg', 'Hot work zone: 35 ft (11 m) radius cleared or covered, openings sealed, extinguisher and fire watch present, other side of walls checked',
  svg(500, 270, [
    text(250, 20, 'Plan view of the work area', { anchor: 'middle', weight: 700, size: 12 }),
    circle(230, 140, 100, { fill: 'rgba(245,158,11,0.10)', stroke: C.accentDark, width: 1.5, dash: '6 4' }), line(230, 140, 330, 140, { stroke: C.accentDark, width: 1, arrow: 'end' }), text(280, 134, '35 ft (11 m)', { size: 10, anchor: 'middle', fill: C.accentDark, weight: 600 }),
    // welder at centre, work piece, sparks
    rect(214, 146, 32, 14, { fill: C.steel, stroke: C.ink }), person(230, 118, 34, C.ink), ...[[-14, -10], [10, -12], [16, 4], [-18, 6]].map(([dx, dy]) => circle(240 + dx, 150 + dy, 1.6, { fill: C.accent, stroke: 'none' })),
    // wall through the zone
    rect(340, 40, 8, 200, { fill: C.steelDark, stroke: C.ink }), text(350, 56, 'wall: check the far side', { size: 9.5, fill: C.muted }), person(390, 118, 34, C.muted), text(392, 160, 'far side', { size: 8.5, anchor: 'middle', fill: C.muted }),
    // floor opening covered
    rect(160, 190, 38, 20, { fill: C.paper, stroke: C.ink }), ...[0, 1, 2, 3].map((i) => line(162 + i * 10, 192, 172 + i * 10, 208, { width: 1, stroke: C.ink })), text(179, 224, 'opening covered', { size: 9, anchor: 'middle', fill: C.muted }),
    // combustibles moved out (drums outside the circle)
    ...[[60, 70], [60, 100]].map(([x, y]) => [rect(x - 12, y - 10, 24, 20, { fill: C.grey, stroke: C.ink, rx: 3 }), line(x - 12, y - 4, x + 12, y - 4, { width: 1 })]), line(120, 92, 92, 88, { stroke: C.red, width: 2.5, arrow: 'end' }), text(60, 124, 'combustibles out', { size: 9, anchor: 'middle', fill: C.red }),
    // blanket over what cannot move
    rect(250, 200, 40, 24, { fill: '#c9a27a', stroke: '#8a6a45' }), ...[0, 1, 2].map((i) => line(254, 206 + i * 6, 286, 206 + i * 6, { stroke: '#8a6a45', width: 0.8 })), text(270, 238, 'blanket on what\ncannot be moved', { size: 8.8, anchor: 'middle', fill: C.muted }),
    // fire watch with extinguisher
    person(272, 58, 34, C.red), rect(284, 64, 8, 16, { fill: C.red, stroke: C.ink, rx: 2 }), text(272, 98, 'fire watch + extinguisher,', { size: 9, anchor: 'middle', fill: C.red }), text(272, 109, '30-60 min after', { size: 9, anchor: 'middle', fill: C.red }),
    caption(500, 270, 'Permit posted; sprinklers in service; seal ducts and drains first.'),
  ], { title: 'Hot work zone' }))

// ---------- shop-reference/hardness-scale-bar ----------
{
  const x0 = 64, x1 = 470, hrc = (v) => x0 + (v - 20) / (70 - 20) * (x1 - x0)
  const hb = [[20, 226], [25, 253], [30, 286], [35, 327], [40, 371], [45, 421], [50, 481], [55, 560], [60, 654]]
  fig('shop-reference/hardness-scale-bar.svg', 'Hardness scales side by side: Rockwell C, Brinell and approximate tensile strength, with where common parts sit',
    svg(500, 250, [
      text(250, 22, 'Rockwell C ↔ Brinell ↔ tensile (approx.)', { anchor: 'middle', weight: 700, size: 12 }),
      ...Array.from({ length: 10 }, (_, i) => rect(x0 + i * (x1 - x0) / 10, 60, (x1 - x0) / 10, 22, { fill: `hsl(${210 - i * 20}, 70%, ${88 - i * 5}%)`, stroke: 'none' })), rect(x0, 60, x1 - x0, 22, { fill: 'none', stroke: C.ink }),
      ...[20, 30, 40, 50, 60, 70].map((v) => [line(hrc(v), 54, hrc(v), 60, { width: 1.2 }), text(hrc(v), 50, String(v), { anchor: 'middle', size: 10.5, weight: 700 })]), text(x0 - 6, 50, 'HRC', { anchor: 'end', size: 9.5, fill: C.muted }),
      ...hb.map(([v, b]) => [line(hrc(v), 82, hrc(v), 88, { width: 1 }), text(hrc(v), 100, String(b), { anchor: 'middle', size: 9.5 })]), text(x0 - 6, 100, 'HB', { anchor: 'end', size: 9.5, fill: C.muted }),
      ...hb.filter((_, i) => i % 2 === 0).map(([v, b]) => text(hrc(v), 116, String(Math.round(b / 2)), { anchor: 'middle', size: 9.5, fill: C.muted })), text(x0 - 6, 116, 'ksi', { anchor: 'end', size: 9.5, fill: C.muted }),
      ...[[22, '4140 pre-hard', 1], [33, 'Grade 8 bolt', 2], [40, 'AR400 plate', 1], [55, 'flame-hardened journal', 2], [62, 'bearing race', 1], [66, 'HSS drill', 2]].map(([v, l, row]) => [line(hrc(v), 82, hrc(v), 126 + row * 18, { width: 1, stroke: C.blue, dash: '2 2' }), text(hrc(v), 136 + row * 18, l, { anchor: 'middle', size: 9.5, fill: C.blue })]),
      note(250, 200, 'A36 (HB 140, about 65 ksi) is below the left end of this bar', { anchor: 'middle', size: 9.5 }),
      note(250, 216, 'a file (about 62 HRC) skates on anything harder than 60 HRC', { anchor: 'middle', size: 9.5 }),
      caption(500, 250, 'Tensile (ksi) ≈ 0.5 × HB. Conversions are approximate: test the part.'),
    ], { title: 'Hardness scale bar' }))
}

// ---------- welding/ac-balance ----------
{
  const wave = (x, y, w, en, label) => { // one full cycle drawn twice; EN below the line
    const per = w / 2, out = []
    for (let k = 0; k < 2; k++) { const s = x + k * per, e = s + per * en / 100; out.push(rect(s, y, e - s, 30, { fill: C.blueSoft, stroke: 'none' }), rect(e, y - 30, s + per - e, 30, { fill: C.redSoft, stroke: 'none' }), path(`M${s},${y} L${s},${y + 30} L${e},${y + 30} L${e},${y - 30} L${s + per},${y - 30} L${s + per},${y}`, { stroke: C.ink, width: 2 })) }
    return [...out, line(x, y, x + w, y, { width: 1, stroke: C.muted }), text(x + w / 2, y + 50, label, { anchor: 'middle', size: 11, weight: 700 }), text(x + per * en / 200, y + 22, 'EN', { anchor: 'middle', size: 9.5, fill: C.blue, weight: 700 }), text(x + per * (en + 100) / 200, y - 14, 'EP', { anchor: 'middle', size: 9.5, fill: C.red, weight: 700 })]
  }
  const bead = (x, y, depth, band, label) => [rect(x - 60, y, 120, 26, { fill: C.steel, stroke: C.ink }), path(`M${x - 22},${y} Q${x},${y + depth * 2} ${x + 22},${y}`, { fill: C.weld, stroke: C.accentDark }), path(`M${x - 22},${y} Q${x},${y - 12} ${x + 22},${y}`, { fill: C.weld, stroke: C.accentDark }), rect(x - 22 - band, y - 2, band, 2, { fill: '#e9e9e9', stroke: 'none' }), rect(x + 22, y - 2, band, 2, { fill: '#e9e9e9', stroke: 'none' }), line(x - 22 - band, y + 34, x + 22 + band, y + 34, { width: 1, arrow: 'both', stroke: C.muted }), text(x, y + 48, label, { anchor: 'middle', size: 9, fill: C.muted })]
  fig('welding/ac-balance.svg', 'AC balance for aluminium TIG: EN half-cycle penetrates, EP half-cycle cleans',
    svg(500, 300, [
      text(250, 20, 'AC square wave: EN heats the work, EP cleans the oxide', { anchor: 'middle', size: 11, weight: 600 }),
      ...wave(40, 80, 190, 70, '70% EN'), ...wave(270, 80, 190, 50, '50% EN'),
      ...bead(135, 170, 9, 8, 'deeper, narrow cleaning band'), ...bead(365, 170, 5, 20, 'shallower, wide cleaning band'),
      note(250, 240, 'more EN = more penetration, cooler tungsten, narrower etched band (start at 65-75% EN)', { anchor: 'middle', size: 9.5 }),
      note(250, 256, 'more EP = wider cleaning, hotter tungsten, wider bead (dirty or cast aluminium)', { anchor: 'middle', size: 9.5 }),
      caption(500, 300, 'Frequency 100-150 Hz tightens the arc; 60-80 Hz widens it.'),
    ], { title: 'AC balance' }))
}

// ---------- welding/cast-iron-repair ----------
fig('welding/cast-iron-repair.svg', 'Cast iron crack repair: drill the ends, V it out, short stringers, peen each one',
  svg(500, 262, [
    text(125, 20, '1. Stop the crack, V it out', { anchor: 'middle', weight: 700, size: 11.5 }),
    rect(30, 40, 190, 120, { fill: '#9aa5b4', stroke: C.ink, rx: 4 }), path('M60,110 L82,96 L100,104 L124,84 L146,90 L168,70 L190,62', { stroke: C.ink, width: 1.8 }),
    circle(60, 110, 6, { fill: C.paper, stroke: C.ink }), circle(190, 62, 6, { fill: C.paper, stroke: C.ink }),
    path('M66,112 L84,98 L102,106 L126,86 L146,92 L166,74 L184,66', { stroke: C.paper, width: 12, opacity: 0.85 }), path('M66,112 L84,98 L102,106 L126,86 L146,92 L166,74 L184,66', { stroke: C.steelDark, width: 6, dash: '2 3' }),
    text(60, 132, 'drill 1/8-3/16 in', { size: 8.8, anchor: 'middle' }), text(190, 48, 'drill', { size: 8.8, anchor: 'middle' }), text(125, 148, 'grind a 60-90° V to the root', { size: 9, anchor: 'middle', fill: C.muted }),
    text(375, 20, '2. Short stringers, skip, peen', { anchor: 'middle', weight: 700, size: 11.5 }),
    rect(280, 40, 190, 120, { fill: '#9aa5b4', stroke: C.ink, rx: 4 }), path('M310,110 L334,96 L352,104 L376,84 L398,90 L420,70 L440,62', { stroke: C.paper, width: 12, opacity: 0.85 }),
    ...[[310, 110, 334, 96, 1], [420, 70, 440, 62, 2], [334, 96, 352, 104, 3], [398, 90, 420, 70, 4], [352, 104, 376, 84, 5], [376, 84, 398, 90, 6]].map(([x1, y1, x2, y2, n]) => [line(x1, y1, x2, y2, { stroke: C.weld, width: 9 }), line(x1, y1, x2, y2, { stroke: C.accentDark, width: 1, dash: '2 2' }), callout(n, (x1 + x2) / 2, (y1 + y2) / 2 - 16, { r: 7 })]),
    rect(440, 100, 10, 34, { fill: C.steelDark, stroke: C.ink, rx: 2 }), rect(432, 92, 26, 12, { fill: C.ink, rx: 2 }), text(445, 146, 'peen each bead\nwhile it is hot', { size: 8.8, anchor: 'middle' }),
    note(250, 192, 'weld 1 in (25 mm) stringers, jumping end to end so no spot gets hot; peen each one at once', { anchor: 'middle', size: 9.5 }),
    note(250, 210, 'Ni-rod (ENi-CI / ENiFe-CI) with low amps; let each bead cool to hand-warm before the next', { anchor: 'middle', size: 9.5 }),
    note(250, 228, 'hot method: preheat 500-1,200°F and cool slowly · cold method: keep the casting under 150°F', { anchor: 'middle', size: 9.5 }),
    caption(500, 262, 'Cast iron cracks from heat stress: short beads, peen, cool slowly.'),
  ], { title: 'Cast iron crack repair' }))

// ---------- welding/orthographic-views ----------
{
  // object: stepped block 100 wide x 60 deep x 70 high with a through hole in the low step
  const F = [60, 150], T = [60, 40], R = [200, 150] // origins (top-left) of front, top, right views
  fig('welding/orthographic-views.svg', 'Third-angle projection: top view above the front view, right side view to the right',
    svg(500, 300, [
      text(250, 18, 'Third-angle projection (US): each view is what you see from that side', { anchor: 'middle', weight: 700, size: 11 }),
      // top view: outline with the step line and the hole (circle)
      rect(T[0], T[1], 100, 60, { fill: C.paper, stroke: C.ink, width: 2 }), line(T[0] + 50, T[1], T[0] + 50, T[1] + 60, { width: 2 }), circle(T[0] + 75, T[1] + 30, 12, { fill: 'none', stroke: C.ink, width: 2 }), line(T[0] + 75, T[1] + 12, T[0] + 75, T[1] + 48, { width: 0.8, stroke: C.muted, dash: '8 3 2 3' }), line(T[0] + 57, T[1] + 30, T[0] + 93, T[1] + 30, { width: 0.8, stroke: C.muted, dash: '8 3 2 3' }),
      text(T[0] + 50, T[1] - 8, 'TOP', { anchor: 'middle', size: 10, weight: 700 }),
      // front view: step profile, hidden hole as dashed lines
      poly([[F[0], F[1] + 70], [F[0], F[1]], [F[0] + 50, F[1]], [F[0] + 50, F[1] + 35], [F[0] + 100, F[1] + 35], [F[0] + 100, F[1] + 70]], { fill: C.paper, stroke: C.ink, width: 2 }),
      line(F[0] + 63, F[1] + 35, F[0] + 63, F[1] + 70, { width: 1.5, dash: '5 3' }), line(F[0] + 87, F[1] + 35, F[0] + 87, F[1] + 70, { width: 1.5, dash: '5 3' }), line(F[0] + 75, F[1] + 30, F[0] + 75, F[1] + 75, { width: 0.8, stroke: C.muted, dash: '8 3 2 3' }),
      text(F[0] + 50, F[1] + 90, 'FRONT', { anchor: 'middle', size: 10, weight: 700 }),
      // right side view: tall part behind, low step in front with the hole hidden
      rect(R[0], R[1], 60, 70, { fill: C.paper, stroke: C.ink, width: 2 }), line(R[0], R[1] + 35, R[0] + 60, R[1] + 35, { width: 2 }), line(R[0] + 18, R[1] + 35, R[0] + 18, R[1] + 70, { width: 1.5, dash: '5 3' }), line(R[0] + 42, R[1] + 35, R[0] + 42, R[1] + 70, { width: 1.5, dash: '5 3' }),
      text(R[0] + 30, R[1] + 90, 'RIGHT SIDE', { anchor: 'middle', size: 10, weight: 700 }),
      // projection lines
      ...[0, 50, 100].map((dx) => line(F[0] + dx, T[1] + 60, F[0] + dx, F[1], { width: 0.6, stroke: C.line, dash: '3 3' })), ...[0, 35, 70].map((dy) => line(F[0] + 100, F[1] + dy, R[0], F[1] + dy, { width: 0.6, stroke: C.line, dash: '3 3' })),
      // isometric thumbnail of the same stepped block with its hole
      ...(() => { const c = Math.cos(30 * P), sn = Math.sin(30 * P), o = [345, 68], k = 0.55, I = (x, y, z) => [o[0] + (x - y) * c * k, o[1] + (x + y) * sn * k - z * k]
        const f = (pts, fill) => poly(pts.map((p) => I(...p)), { fill, stroke: C.ink, width: 1 })
        const [hx, hy, hz] = I(75, 30, 35)
        return [f([[0, 0, 70], [50, 0, 70], [50, 60, 70], [0, 60, 70]], C.grey), f([[0, 60, 0], [50, 60, 0], [50, 60, 70], [0, 60, 70]], C.steel), f([[50, 0, 35], [50, 60, 35], [50, 60, 70], [50, 0, 70]], '#b9c4d2'),
          f([[50, 0, 35], [100, 0, 35], [100, 60, 35], [50, 60, 35]], C.grey), f([[50, 60, 0], [100, 60, 0], [100, 60, 35], [50, 60, 35]], C.steel), f([[100, 0, 0], [100, 60, 0], [100, 60, 35], [100, 0, 35]], '#b9c4d2'),
          `<ellipse cx="${hx}" cy="${hy}" rx="${12 * k * 1.22}" ry="${12 * k * 0.71}" fill="${C.paper}" stroke="${C.ink}" stroke-width="1"/>`] })(),
      text(345, 110, 'the part', { anchor: 'middle', size: 9.5, fill: C.muted }),
      // line types
      table(300, 130, [['Line', 'Means'], ['solid thick', 'visible edge'], ['dashed', 'hidden edge'], ['thin chain', 'centre line'], ['thin + arrows', 'dimension'], ['thick chain', 'cutting plane']], [90, 100], { rowH: 18, size: 9.5 }),
      caption(500, 300, 'First-angle (ISO) puts the top view below the front view: check the symbol.'),
    ], { title: 'Orthographic views' }))
}
