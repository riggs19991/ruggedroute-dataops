// Advanced hydraulics: pumps, valves, cartridges and logic elements, fittings, fluids, diagnostics, LS/servo, hydrostatic drives.
import { svg, text, line, rect, circle, path, poly, dim, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'

// ---- small symbol helpers ----
const tank = (x, y, w = 24) => path(`M${x - w / 2},${y} L${x - w / 2},${y + 12} L${x + w / 2},${y + 12} L${x + w / 2},${y}`, { width: 1.5 })
const pump = (x, y, r = 18, { variable = false } = {}) => [circle(x, y, r), poly([[x, y - r], [x + 6, y - r + 11], [x - 6, y - r + 11]], { fill: C.ink }), variable ? line(x - r - 4, y + r + 4, x + r + 4, y - r - 4, { width: 1.2, arrow: 'end' }) : '']
const motor = (x, y, r = 18, { variable = false } = {}) => [circle(x, y, r), poly([[x, y + r], [x + 6, y + r - 11], [x - 6, y + r - 11]], { fill: C.ink }), variable ? line(x - r - 4, y + r + 4, x + r + 4, y - r - 4, { width: 1.2, arrow: 'end' }) : '']
const gauge = (x, y, label, { r = 10, fill = C.ink } = {}) => [circle(x, y, r, { fill: C.paper, stroke: fill }), line(x - 3, y + 3, x + 4, y - 4, { width: 1.5, stroke: fill }), label ? text(x, y + r + 11, label, { anchor: 'middle', size: 9, fill }) : '']
const checkV = (x, y, dir = 'up', s = 7) => dir === 'up' ? [circle(x, y, s / 2 + 1, { fill: C.paper }), path(`M${x - s},${y + s} L${x},${y - s * 0.2} L${x + s},${y + s}`, { width: 1.5 })] : dir === 'right' ? [circle(x, y, s / 2 + 1, { fill: C.paper }), path(`M${x - s},${y - s} L${x + s * 0.2},${y} L${x - s},${y + s}`, { width: 1.5 })] : [circle(x, y, s / 2 + 1, { fill: C.paper }), path(`M${x + s},${y - s} L${x - s * 0.2},${y} L${x + s},${y + s}`, { width: 1.5 })]
const relief = (x, y, { size = 26, vent = false } = {}) => { const h = size / 2; return [rect(x - h, y - h, size, size), line(x - h + 3, y + h - 3, x + h - 3, y - h + 3, { width: 1.5, arrow: 'end' }), path(`M${x + h},${y} l6,0 l0,-${h + 4} l-3,0 m3,0 l3,0`, { width: 1 }), path(`M${x - h},${y} l-6,0 l0,-5 l-3,0 l6,-3 l-6,-3 l3,0`, { width: 1 }), vent ? line(x + h + 6, y - h - 4, x + h + 6, y - h - 14, { width: 1, dash: '2 2' }) : ''] }
const envelope = (x, y, w, h, inside) => [rect(x, y, w, h), ...inside]
const flowCtl = (x, y, vertical = true) => vertical ? [path(`M${x - 8},${y - 8} q8,8 0,16`, { width: 1.5 }), path(`M${x + 8},${y - 8} q-8,8 0,16`, { width: 1.5 }), line(x - 10, y + 9, x + 10, y - 9, { width: 1, arrow: 'end' })] : [path(`M${x - 8},${y - 8} q8,8 16,0`, { width: 1.5 }), path(`M${x - 8},${y + 8} q8,-8 16,0`, { width: 1.5 }), line(x - 9, y + 10, x + 9, y - 10, { width: 1, arrow: 'end' })]
const cyl = (x, y, w, h, { rodRight = true, pistonAt = 0.45 } = {}) => [rect(x, y, w, h), rect(x + w * pistonAt, y, 5, h, { fill: C.ink }), line(x + w * pistonAt + 5, y + h / 2, rodRight ? x + w + 26 : x - 26, y + h / 2, { width: 3 })]

// ---------- Pump controls ----------
fig('hydraulics/pump-controls.svg', 'Variable pump controls: the compensator holds a maximum, load sensing holds a margin above the load, the torque limiter caps the power; set relief, then compensator, then margin',
  svg(500, 250, [
    ...pump(80, 120, 34, { variable: true }), line(80, 154, 80, 190, { width: 1.5 }), tank(80, 190), line(80, 86, 80, 40, { width: 2 }), line(80, 40, 180, 40, { width: 2, arrow: 'end' }), text(186, 44, 'P out', { size: 10 }),
    rect(122, 96, 44, 30, { fill: C.grey }), text(144, 108, 'control', { anchor: 'middle', size: 9 }), text(144, 120, 'spool', { anchor: 'middle', size: 9 }),
    line(144, 96, 144, 40, { width: 1, dash: '3 3' }), rect(122, 136, 44, 22, { fill: C.steel }), text(144, 150, 'stroker', { anchor: 'middle', size: 9 }), line(114, 147, 122, 147, { width: 1, dash: '3 3' }), line(114, 147, 114, 128, { width: 1, dash: '3 3' }),
    line(166, 111, 200, 111, { width: 1, dash: '3 3' }), text(203, 114, 'LS in', { size: 9 }),
    note(84, 222, 'swashplate = displacement', { anchor: 'middle', size: 9.5 }),
    table(232, 34, [['Control', 'Holds', 'Set to'], ['Compensator', 'max. pressure', 'relief −200 psi'], ['Load sense', 'load + margin', '200-350 psi'], ['Torque limiter', 'p × Q ≤ hp', 'maker curve'], ['Remote comp.', 'remote relief', 'below local']], [80, 84, 96], { rowH: 24, size: 9.5 }),
    note(232, 172, 'Order: relief → compensator → LS margin → branches', { size: 9.5 }),
    note(232, 188, 'Compensator above the relief = full flow', { size: 9.5 }), note(232, 202, 'over the relief and a boiling tank', { size: 9.5 }),
    caption(500, 250, 'Lock both screws and write both values on the pump.'),
  ], { title: 'Pump controls' }))

// ---------- Case drain flow test ----------
fig('hydraulics/case-drain-flow-test.svg', 'Case drain test: run at working pressure and temperature, collect the drain flow for one minute; over 10% of rated flow means a worn pump; keep the case full and the drain unrestricted',
  svg(500, 252, [
    rect(60, 90, 90, 70, { fill: C.grey, rx: 6 }), text(105, 118, 'piston', { anchor: 'middle', size: 11, weight: 600 }), text(105, 132, 'pump', { anchor: 'middle', size: 11, weight: 600 }),
    line(150, 110, 250, 110, { width: 2.5 }), ...gauge(250, 80, ''), text(268, 84, '3,000 psi', { size: 9 }), line(250, 110, 250, 90, { width: 1.5 }), rect(250, 100, 60, 20, { fill: C.grey }), text(280, 114, 'load', { anchor: 'middle', size: 9 }), line(310, 110, 340, 110, { width: 2.5 }), tank(340, 110),
    line(105, 90, 105, 50, { width: 1.5, stroke: C.blue }), line(105, 50, 400, 50, { width: 1.5, stroke: C.blue }), line(400, 50, 400, 150, { width: 1.5, stroke: C.blue, arrow: 'end' }), text(200, 44, 'case drain from the TOP port, no restriction', { size: 9.5, fill: C.blue }),
    rect(370, 150, 60, 60, { fill: C.blueSoft, rx: 4 }), ...[165, 180, 195].map((y) => line(372, y, 380, y, { width: 1, stroke: C.blue })), text(400, 185, '1 min', { anchor: 'middle', size: 10, weight: 600 }), note(400, 224, 'measure or flow meter', { anchor: 'middle', size: 9 }),
    line(60, 130, 30, 130, { width: 2.5 }), line(30, 130, 30, 160, { width: 2.5 }), tank(30, 160), text(20, 124, 'in', { size: 9 }),
    note(60, 182, 'rated 20 gpm: new 0.2-0.6 gpm to case', { size: 9.5 }), note(60, 196, 'worn: over 2-3 gpm (10-15%)', { size: 9.5, fill: C.red }), note(60, 210, 'ηv = (rated − drain) ÷ rated', { size: 9.5 }),
    caption(500, 252, 'Cold oil halves the leakage: test hot. A hot case is a leaking pump.'),
  ], { title: 'Case drain flow test' }))

// ---------- Pump flow vs pressure ----------
{
  const ch = chart({ x: 60, y: 30, w: 400, h: 190, xmin: 0, xmax: 3000, ymin: 0, ymax: 25, xticks: [0, 1000, 2000, 3000], yticks: [0, 5, 10, 15, 20, 25], xlabel: 'Pressure (psi)', ylabel: 'Flow (gpm)' })
  const ln = (pts, c, d) => path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5, dash: d })
  fig('hydraulics/pump-flow-vs-pressure.svg', 'Flow at pressure: a healthy pump loses a few percent from zero to full pressure; a worn pump falls away steeply; below about 80-85% of theoretical at working pressure it is done',
    svg(500, 280, [ch.el, line(ch.sx(0), ch.sy(21.4), ch.sx(3000), ch.sy(21.4), { stroke: C.muted, width: 1, dash: '4 3' }), text(ch.sx(1500), ch.sy(21.4) - 5, 'theoretical 21.4 gpm', { anchor: 'middle', size: 10, fill: C.muted }),
      ln([[0, 21.2], [1000, 20.9], [2000, 20.5], [3000, 20.0]], C.green), text(ch.sx(2400), ch.sy(20) - 8, 'new: ηv 0.93', { size: 10.5, fill: C.green, weight: 600 }),
      ln([[0, 20.6], [1000, 19.0], [2000, 16.5], [3000, 13.5]], C.red), text(ch.sx(2300), ch.sy(13.5) + 16, 'worn: ηv 0.63', { size: 10.5, fill: C.red, weight: 600 }),
      rect(ch.sx(0), ch.sy(18.2), ch.sx(3000) - ch.sx(0), ch.sy(17) - ch.sy(18.2), { fill: C.redSoft, stroke: 'none', opacity: 0.7 }), text(ch.sx(700), ch.sy(17.5), 'replace line: 80-85%', { anchor: 'middle', size: 9.5, fill: C.red }),
      caption(500, 280, 'Same rpm, same oil temperature, flow meter in the pump outlet.')], { title: 'Pump flow vs pressure' }))
}

// ---------- Spool centre conditions ----------
{
  const env = (x, y, name, inner, what) => {
    const w = 72, h = 40
    const P = [x + 18, y + h], T = [x + 54, y + h], A = [x + 18, y], B = [x + 54, y]
    const stub = (p, up) => line(p[0], p[1], p[0], p[1] + (up ? -9 : 9), { width: 1.5 })
    const blockT = (p, up) => line(p[0] - 5, p[1] + (up ? -2 : 2), p[0] + 5, p[1] + (up ? -2 : 2), { width: 2 })
    return [rect(x, y, w, h), stub(P, false), stub(T, false), stub(A, true), stub(B, true), text(P[0], y + h + 20, 'P', { anchor: 'middle', size: 9 }), text(T[0], y + h + 20, 'T', { anchor: 'middle', size: 9 }), text(A[0], y - 11, 'A', { anchor: 'middle', size: 9 }), text(B[0], y - 11, 'B', { anchor: 'middle', size: 9 }),
      ...inner({ P, T, A, B, x, y, w, h, blockT }), text(x + w / 2, y + h + 34, name, { anchor: 'middle', size: 10.5, weight: 700 }), text(x + w / 2, y + h + 47, what, { anchor: 'middle', size: 8.5, fill: C.muted })]
  }
  const closed = ({ P, T, A, B, blockT }) => [blockT(P, true), blockT(T, true), blockT(A, false), blockT(B, false)]
  const open = ({ P, T, A, B, x, y, w, h }) => [line(P[0], P[1], A[0], A[1], { width: 1.5 }), line(T[0], T[1], B[0], B[1], { width: 1.5 }), line(P[0], y + h - 12, T[0], y + 12, { width: 1.5 }), line(T[0], y + h - 12, P[0], y + 12, { width: 1.5 })]
  const tandem = ({ P, T, A, B, x, y, h, blockT }) => [path(`M${P[0]},${P[1]} L${P[0]},${y + h / 2} L${T[0]},${y + h / 2} L${T[0]},${T[1]}`, { width: 1.5 }), blockT(A, false), blockT(B, false)]
  const float_ = ({ P, T, A, B, x, y, h, blockT }) => [blockT(P, true), path(`M${A[0]},${A[1]} L${A[0]},${y + h / 2} L${T[0]},${y + h / 2} L${T[0]},${T[1]}`, { width: 1.5 }), line(B[0], B[1], B[0], y + h / 2, { width: 1.5 })]
  const regen = ({ P, T, A, B, x, y, h, blockT }) => [blockT(T, true), path(`M${P[0]},${P[1]} L${P[0]},${y + h / 2} L${B[0]},${y + h / 2} L${B[0]},${B[1]}`, { width: 1.5 }), line(A[0], A[1], A[0], y + h / 2, { width: 1.5 })]
  const pat = ({ P, T, A, B, x, y, h, blockT }) => [path(`M${P[0]},${P[1]} L${P[0]},${y + h / 2} L${T[0]},${y + h / 2} L${T[0]},${T[1]}`, { width: 1.5 }), line(A[0], A[1], A[0], y + h / 2, { width: 1.5 }), blockT(B, false)]
  fig('hydraulics/spool-center-conditions.svg', 'Spool centre conditions: closed dead-heads a fixed pump, open and tandem unload it, float and open let the load move, regenerative extends fast at low force',
    svg(500, 270, [
      ...env(30, 26, 'Closed', closed, 'pump over relief · load held'), ...env(180, 26, 'Open', open, 'pump unloaded · load drifts'), ...env(330, 26, 'Tandem', tandem, 'pump unloaded · load held'),
      ...env(30, 150, 'Float', float_, 'A, B to tank · motor coasts'), ...env(180, 150, 'Regenerative', regen, 'fast extend · low force'), ...env(330, 150, 'P-A-T, B blocked', pat, 'one-sided variants: read the code'),
      text(440, 78, '"held" = slow', { anchor: 'middle', size: 8.5, fill: C.muted }), text(440, 89, 'spool leakage', { anchor: 'middle', size: 8.5, fill: C.muted }),
      caption(500, 270, 'The centre box is the valve at rest: read it before chasing drift or heat.'),
    ], { title: 'Spool centre conditions' }))
}

// ---------- DCV mounting patterns ----------
fig('hydraulics/dcv-mounting-patterns.svg', 'ISO 4401 mounting faces: D03/NG6 to about 20 gpm, D05/NG10 30-40, D07/NG16 80, D08/NG25 120-160 gpm; the pattern is common across makers, the spool and coil are not',
  svg(500, 230, [
    ...[['D03 · CETOP 3 · NG6', 46, 32, 4, '20 gpm', 'M5 · 6-7 ft-lb', 4], ['D05 · CETOP 5 · NG10', 62, 44, 4, '30-40 gpm', 'M6 · 11-13 ft-lb', 4], ['D07 · CETOP 7 · NG16', 84, 58, 6, '80 gpm', 'M10 · 40-45 ft-lb', 6], ['D08 · CETOP 8 · NG25', 100, 70, 6, '120-160 gpm', 'M12 · 70-80 ft-lb', 6]].map(([n, w, h, np, fl, bolt, nb], i) => {
      const cx = 70 + i * 120, cy = 90; const x = cx - w / 2, y = cy - h / 2
      const bolts = nb === 4 ? [[x + 5, y + 5], [x + w - 5, y + 5], [x + 5, y + h - 5], [x + w - 5, y + h - 5]] : [[x + 5, y + 5], [x + w - 5, y + 5], [x + 5, y + h - 5], [x + w - 5, y + h - 5], [x + w / 2, y + 5], [x + w / 2, y + h - 5]]
      const ports = [[cx - w * 0.22, cy + h * 0.18, 'P'], [cx + w * 0.22, cy + h * 0.18, 'T'], [cx - w * 0.22, cy - h * 0.2, 'A'], [cx + w * 0.22, cy - h * 0.2, 'B']]
      return [rect(x, y, w, h, { fill: C.grey, rx: 3 }), ...bolts.map(([bx, by]) => circle(bx, by, 2.2, { fill: C.steelDark, stroke: 'none' })), ...ports.map(([px, py, l]) => [circle(px, py, w / 14, { fill: C.blueSoft, stroke: C.blue }), text(px, py + 3, l, { anchor: 'middle', size: 7.5, fill: C.blue })]),
        text(cx, 148, n, { anchor: 'middle', size: 9.5, weight: 600 }), text(cx, 164, fl, { anchor: 'middle', size: 10 }), text(cx, 178, bolt, { anchor: 'middle', size: 9, fill: C.muted })]
    }),
    note(250, 200, 'D07 and D08 are always pilot-operated: X (pilot supply) and Y (pilot drain) appear in the face', { anchor: 'middle', size: 9.5 }),
    caption(500, 230, 'Check spool code, voltage and connector: the face fitting proves nothing.'),
  ], { title: 'DCV mounting patterns' }))

// ---------- Solenoid checks ----------
fig('hydraulics/solenoid-checks.svg', 'Wet-armature solenoid: check voltage at the plug under load, coil resistance with the plug off, and push the manual override pin; DC half-shifts, AC burns',
  svg(500, 246, [
    rect(40, 80, 60, 60, { fill: C.grey }), text(70, 106, 'valve', { anchor: 'middle', size: 10 }), text(70, 120, 'body', { anchor: 'middle', size: 10 }),
    rect(100, 96, 130, 28, { fill: C.steel, rx: 4 }), rect(140, 84, 70, 52, { fill: C.accent, stroke: C.accentDark, opacity: 0.9, rx: 3 }), ...[0, 1, 2, 3, 4].map((i) => line(146 + i * 13, 88, 146 + i * 13, 132, { width: 1, stroke: C.accentDark })),
    rect(110, 104, 26, 12, { fill: C.ink }), line(100, 110, 110, 110, { width: 3 }), rect(226, 100, 18, 20, { fill: C.steelDark, rx: 2 }), line(244, 110, 258, 110, { width: 3 }), text(262, 114, 'override pin', { size: 9 }),
    rect(150, 56, 40, 28, { fill: C.grey, rx: 3 }), text(170, 74, 'plug', { anchor: 'middle', size: 9 }), line(190, 70, 250, 70, { width: 1.5 }), text(254, 74, 'to PLC', { size: 9 }),
    callout(1, 210, 56), callout(2, 123, 148), callout(3, 250, 128), callout(4, 106, 74),
    legend(40, 176, ['voltage at the pins, coil connected, output on: ±10% of rated', 'coil Ω with plug off: 24 V DC 30 W ≈ 19 Ω; open = burned, low = shorted', 'override pin shifts the spool by hand: moves = electrical fault', 'tube nut hand-tight + 1/4 turn; gasket in the plug'], { size: 9.2, gap: 14 }),
    text(340, 100, 'AC: inrush stays high if', { size: 9.5, fill: C.red }), text(340, 112, 'the spool does not stroke', { size: 9.5, fill: C.red }), text(340, 124, '→ coil burns in minutes', { size: 9.5, fill: C.red }),
    text(340, 144, 'DC: runs warm, half-shifts', { size: 9.5, fill: C.blue }),
    caption(500, 246, 'A lit LED proves power at the plug, not that the spool moved.'),
  ], { title: 'Solenoid checks' }))

// ---------- Pilot-operated DCV ----------
fig('hydraulics/pilot-operated-dcv.svg', 'Two-stage directional valve: a D03 pilot valve on top shifts the main spool with pilot pressure from X (internal from P or external) and drains through Y (internal to T or external)',
  svg(500, 250, [
    rect(120, 40, 120, 34, { fill: C.grey }), text(180, 61, 'pilot valve (D03)', { anchor: 'middle', size: 10, weight: 600 }), rect(100, 46, 20, 22, { fill: C.accent, stroke: C.accentDark }), rect(240, 46, 20, 22, { fill: C.accent, stroke: C.accentDark }),
    rect(120, 78, 120, 26, { fill: C.soft, stroke: C.accentDark }), text(180, 95, 'pilot choke plate (optional)', { anchor: 'middle', size: 9 }),
    rect(80, 108, 200, 60, { fill: C.grey }), rect(96, 128, 168, 20, { fill: C.steel }), ...[120, 160, 200, 240].map((x) => rect(x - 8, 128, 16, 20, { fill: C.steelDark })), text(180, 162, 'main stage (D05-D10)', { anchor: 'middle', size: 9.5, weight: 600 }),
    ...[[100, 'A'], [140, 'P'], [180, 'T'], [220, 'B']].map(([x, l]) => [line(x, 168, x, 190, { width: 1.5 }), text(x, 202, l, { anchor: 'middle', size: 9.5 })]),
    line(300, 118, 280, 118, { width: 1.2, dash: '3 3' }), text(304, 121, 'X pilot supply', { size: 9.5 }), text(304, 133, '50-150 psi min.', { size: 9, fill: C.muted }),
    line(300, 150, 280, 150, { width: 1.2, dash: '3 3' }), text(304, 153, 'Y pilot drain', { size: 9.5 }), text(304, 165, 'external if T > 100-150 psi', { size: 9, fill: C.muted }),
    text(12, 121, 'plug selects', { size: 8.5, anchor: 'start', fill: C.muted }), text(12, 133, 'internal or', { size: 8.5, fill: C.muted }), text(12, 145, 'external pilot', { size: 8.5, fill: C.muted }),
    note(250, 222, 'open or tandem centre: P is near zero at rest → external pilot or a 75 psi check in T', { anchor: 'middle', size: 9.2 }),
    caption(500, 250, 'Will not shift: LED, override, then a gauge at X, then back-pressure at Y.'),
  ], { title: 'Pilot-operated DCV' }))

// ---------- Stack valve order ----------
fig('hydraulics/stack-valve-order.svg', 'A D03 stack from the manifold up: reducing valve, load check, pilot-operated check nearest the load, flow controls above it, gauge plate, directional valve on top; tie rods torqued in a cross pattern',
  svg(500, 314, [
    ...[[1, 'subplate / bar manifold', 'P T A B', C.steel], [2, 'pressure reducing (P)', 'P · drain to T', C.grey], [3, 'load check (P)', 'P', C.grey], [4, 'pilot-operated check (A, B)', 'A B · holds the load', C.blueSoft], [5, 'flow control meter-out (A, B)', 'A B · speed', C.grey], [6, 'gauge / pressure switch plate', 'P or A/B', C.grey], [7, 'directional valve (D03)', 'on top', C.soft]].map(([n, name, port, fill], i) => {
      const y = 262 - i * 34; const h = i === 0 ? 22 : 28; const x = i === 0 ? 60 : 80; const w = i === 0 ? 220 : 180
      return [rect(x, y, w, h, { fill, rx: 3 }), text(x + w / 2, y + h / 2 + 4, name, { anchor: 'middle', size: 9.5, weight: i === 6 ? 700 : undefined }), callout(n, x - 12, y + h / 2), text(x + w + 8, y + h / 2 + 4, port, { size: 9, fill: C.muted })]
    }),
    ...[95, 245].map((x) => line(x, 44, x, 292, { width: 2, stroke: C.accentDark, dash: '6 3' })), text(170, 36, 'tie rods (4)', { anchor: 'middle', size: 9, fill: C.accentDark }),
    text(372, 60, 'From the manifold up:', { size: 9.2, weight: 700 }), note(372, 76, 'each module sees only what', { size: 8.6 }), note(372, 88, 'the ones below pass up', { size: 8.6 }),
    note(372, 112, 'POC under the flow control:', { size: 8.6 }), note(372, 124, 'full pilot, smooth lowering', { size: 8.6 }),
    note(372, 148, 'Reducing valve lowest:', { size: 8.6 }), note(372, 160, 'everything above sees it', { size: 8.6 }),
    note(372, 184, 'Torque D03 M5: 6-7 ft-lb', { size: 8.6 }), note(372, 196, 'D05 M6: 11-13 ft-lb', { size: 8.6 }), note(372, 208, 'cross pattern, two stages', { size: 8.6 }),
    note(372, 232, 'new O-rings on every face', { size: 8.6 }), note(372, 244, 'read the A/B stamping', { size: 8.6 }),
    caption(500, 314, 'Uneven torque bows the stack and the spool on top sticks.'),
  ], { title: 'Stack valve order' }))

// ---------- Sectional valve bank ----------
fig('hydraulics/sectional-valve-bank.svg', 'Mobile sectional valve: inlet with the main relief, work sections with spool, load check, port reliefs and anti-cavitation checks, outlet with power beyond; the LS gallery collects the highest load through shuttles',
  svg(500, 240, [
    rect(30, 70, 60, 110, { fill: C.steel, rx: 3 }), text(60, 96, 'inlet', { anchor: 'middle', size: 10, weight: 600 }), ...relief(60, 130, { size: 20 }), text(60, 164, 'main', { anchor: 'middle', size: 8.5 }), text(60, 174, 'relief', { anchor: 'middle', size: 8.5 }),
    ...[0, 1, 2].map((i) => { const x = 100 + i * 100; return [rect(x, 70, 90, 110, { fill: C.grey, rx: 3 }), text(x + 45, 86, `section ${i + 1}`, { anchor: 'middle', size: 9.5, weight: 600 }), rect(x + 10, 96, 70, 12, { fill: C.steel }), ...[x + 22, x + 45, x + 68].map((sx) => rect(sx - 5, 96, 10, 12, { fill: C.steelDark })), line(x + 80, 102, x + 96, 102, { width: 2 }), text(x + 45, 122, 'spool', { anchor: 'middle', size: 8.5, fill: C.muted }),
      ...checkV(x + 45, 138, 'up', 5), text(x + 45, 152, 'load check', { anchor: 'middle', size: 8, fill: C.muted }),
      poly([[x + 14, 168], [x + 24, 158], [x + 24, 178]], { fill: C.redSoft, stroke: C.red }), text(x + 19, 188, 'port', { anchor: 'middle', size: 7.5, fill: C.red }), text(x + 19, 197, 'reliefs', { anchor: 'middle', size: 7.5, fill: C.red }),
      poly([[x + 76, 168], [x + 66, 158], [x + 66, 178]], { fill: C.greenSoft, stroke: C.green }), text(x + 71, 188, 'anti-cav', { anchor: 'middle', size: 7.5, fill: C.green }), text(x + 71, 197, 'checks', { anchor: 'middle', size: 7.5, fill: C.green }),
      line(x + 30, 60, x + 30, 70, { width: 1.5 }), line(x + 60, 60, x + 60, 70, { width: 1.5 }), text(x + 30, 56, 'A', { anchor: 'middle', size: 8.5 }), text(x + 60, 56, 'B', { anchor: 'middle', size: 8.5 }),
      circle(x + 45, 66, 3, { fill: C.paper, stroke: C.blue, width: 1 })] }),
    rect(400, 70, 60, 110, { fill: C.steel, rx: 3 }), text(430, 96, 'outlet', { anchor: 'middle', size: 10, weight: 600 }), text(430, 130, 'T', { anchor: 'middle', size: 10 }), text(430, 150, 'power', { anchor: 'middle', size: 8.5 }), text(430, 160, 'beyond', { anchor: 'middle', size: 8.5 }),
    line(60, 40, 445, 40, { width: 1.2, stroke: C.blue, dash: '4 3' }), ...[145, 245, 345].map((x) => line(x, 40, x, 63, { width: 1, stroke: C.blue, dash: '3 2' })), text(250, 34, 'LS gallery: shuttles pass the highest of A/B in each section', { anchor: 'middle', size: 9, fill: C.blue }),
    ...[80, 190].map((y) => line(22, y, 468, y, { width: 2.5, stroke: C.accentDark, opacity: 0.5 })), text(250, 216, 'tie rods: torque in stages, cross pattern, valve on a flat surface', { anchor: 'middle', size: 9.2, fill: C.accentDark }),
    line(60, 190, 60, 205, { width: 2 }), text(60, 216, 'P', { anchor: 'middle', size: 9 }),
    caption(500, 240, 'Port relief below the main relief: weak in one direction only.'),
  ], { title: 'Sectional valve bank' }))

// ---------- Logic valve cross-section ----------
fig('hydraulics/logic-valve-cross-section.svg', 'ISO 7368 logic element: the poppet opens when pressure at A on the nose area plus pressure at B on the annulus beats pressure at X on the full top area plus the spring; the cover decides what X sees',
  svg(500, 310, [
    rect(150, 60, 140, 190, { fill: C.grey }), rect(180, 90, 80, 160, { fill: C.paper, stroke: C.ink }), rect(150, 40, 140, 22, { fill: C.steelDark }), text(220, 55, 'cover: pilot circuit, X port', { anchor: 'middle', size: 9.5, fill: '#fff' }),
    poly([[192, 100], [248, 100], [248, 190], [232, 222], [208, 222], [192, 190]], { fill: C.steel, stroke: C.ink }), text(220, 150, 'poppet', { anchor: 'middle', size: 10, weight: 600 }),
    ...[0, 1, 2].map((i) => path(`M${206 + i * 10},72 l4,-6 l4,6`, { width: 1.2 })), text(262, 72, 'spring', { size: 8.5, fill: C.muted }),
    rect(180, 222, 80, 28, { fill: '#dbeafe', stroke: 'none' }), rect(180, 190, 12, 32, { fill: C.grey, stroke: 'none' }), rect(248, 190, 12, 32, { fill: C.grey, stroke: 'none' }),
    line(220, 250, 220, 280, { width: 2.5, stroke: C.blue }), text(220, 292, 'A (nose, axial)', { anchor: 'middle', size: 9.5, fill: C.blue }),
    line(290, 205, 330, 205, { width: 2.5, stroke: C.blue }), text(334, 209, 'B (side, radial)', { size: 9.5, fill: C.blue }),
    line(220, 40, 220, 20, { width: 1.5, dash: '3 3' }), text(228, 24, 'X (spring chamber)', { size: 9.5 }),
    dim(192, 236, 248, 236, 'A_A', { size: 9, fill: C.red }), dim(260, 196, 290, 196, 'A_B', { size: 9, fill: C.red, ext: false }), dim(192, 92, 248, 92, 'A_X = A_A + A_B', { size: 9, fill: C.red }),
    text(20, 120, 'opens when', { size: 10, weight: 700 }), text(20, 136, 'pA·A_A + pB·A_B', { size: 10 }), text(20, 150, '> pX·A_X + spring', { size: 10 }),
    text(20, 176, 'X to tank: open', { size: 9.5 }), text(20, 190, 'X to max(A,B):', { size: 9.5 }), text(20, 202, 'closed, leak-free', { size: 9.5 }), text(20, 216, 'X via a pilot relief:', { size: 9.5 }), text(20, 228, 'big relief valve', { size: 9.5 }),
    text(340, 120, 'area ratio A_A : A_X', { size: 9.5, weight: 700 }), text(340, 136, '1:1   no annulus, pressure duty', { size: 9 }), text(340, 150, '1:1.1  directional, check', { size: 9 }), text(340, 164, '1:1.5, 1:2  check B→A,', { size: 9 }), text(340, 176, 'throttle', { size: 9 }),
    caption(500, 310, 'Drift = a leaking pilot or seat; will not open = X never vented.'),
  ], { title: 'Logic valve cross-section' }))

// ---------- Cartridge valve cavity ----------
fig('hydraulics/cartridge-valve-cavity.svg', 'Screw-in cartridge: the threads hold it, the O-rings and back-up rings seal each port on a step of the cavity; install straight, new seals, torque by size',
  svg(500, 256, [
    rect(60, 60, 170, 170, { fill: C.grey }), path('M120,60 L120,90 L110,90 L110,130 L118,130 L118,170 L126,170 L126,210 L164,210 L164,170 L172,170 L172,130 L180,130 L180,90 L170,90 L170,60', { fill: C.paper, stroke: C.ink }),
    rect(112, 28, 66, 30, { fill: C.steelDark }), text(145, 47, 'hex', { anchor: 'middle', size: 9.5, fill: '#fff' }), rect(122, 58, 46, 34, { fill: C.steel }), ...[0, 1, 2, 3].map((i) => line(122, 64 + i * 8, 168, 64 + i * 8, { width: 0.8, stroke: C.steelDark })),
    rect(128, 92, 34, 116, { fill: C.steel }), ...[[100, 'tank 4'], [136, '3'], [176, '2']].map(([y]) => [rect(126, y, 38, 6, { fill: '#333', rx: 3 }), rect(126, y + 6, 38, 3, { fill: C.blue, rx: 1 })]),
    ...[[118, 120, '2'], [126, 160, '3']].map(([x, y, l]) => [line(60, y, x, y, { width: 2, stroke: C.blue }), text(50, y + 4, l, { anchor: 'end', size: 9, fill: C.blue })]), line(145, 210, 145, 240, { width: 2, stroke: C.blue }), text(154, 238, '1', { size: 9, fill: C.blue }),
    text(190, 140, 'back-up ring', { size: 8.5, fill: C.blue }), text(190, 152, 'away from', { size: 8.5, fill: C.blue }), text(190, 164, 'pressure', { size: 8.5, fill: C.blue }),
    text(290, 44, 'Install', { size: 10.5, weight: 700 }), legend(290, 62, ['clean and inspect every cavity step', 'new seal kit, oiled, right material', 'start by hand: feel each step seat', 'torque wrench, six-point socket', 'coil nut hand-tight + 1/4 turn'], { size: 9.2, gap: 14 }),
    table(290, 140, [['size', 'thread', 'torque'], ['08', '3/4-16', '20-25 ft-lb'], ['10', '7/8-14', '30-35'], ['12', '1-1/16-12', '45-55'], ['16', '1-5/16-12', '100-150']], [36, 70, 84], { rowH: 17, size: 8.8 }),
    caption(500, 256, 'A cocked cartridge cuts an O-ring on a step and leaks port to port.'),
  ], { title: 'Cartridge valve cavity' }))

// ---------- Pilot-operated relief ----------
{
  const ch = chart({ x: 318, y: 40, w: 162, h: 120, xmin: 0, xmax: 100, ymin: 0, ymax: 120, xticks: [0, 50, 100], yticks: [], xlabel: 'flow (% rated)', ylabel: 'pressure' })
  fig('hydraulics/pilot-operated-relief.svg', 'Pilot-operated relief: the pilot poppet sets the pressure, the main poppet passes the flow with a small override; the vent port unloads it or hands control to a remote valve',
    svg(500, 270, [
      rect(40, 60, 200, 150, { fill: C.grey }), rect(70, 90, 60, 100, { fill: C.paper, stroke: C.ink }), poly([[76, 100], [124, 100], [124, 150], [110, 170], [90, 170], [76, 150]], { fill: C.steel, stroke: C.ink }), line(100, 100, 100, 150, { width: 1, dash: '2 2', stroke: C.blue }), text(100, 146, 'orifice', { anchor: 'middle', size: 7.5, fill: C.blue }),
      ...[0, 1].map((i) => path(`M${92 + i * 8},96 l4,-5 l4,5`, { width: 1 })), rect(70, 170, 60, 20, { fill: '#dbeafe', stroke: 'none' }), line(100, 190, 100, 224, { width: 2.5, stroke: C.blue }), text(100, 236, 'inlet (P)', { anchor: 'middle', size: 9.5, fill: C.blue }),
      line(130, 180, 175, 180, { width: 2.5, stroke: C.blue }), text(178, 184, 'to tank', { size: 9.5, fill: C.blue }),
      rect(150, 70, 70, 60, { fill: C.paper, stroke: C.ink }), poly([[165, 100], [185, 90], [185, 110]], { fill: C.steel, stroke: C.ink }), ...[0, 1, 2].map((i) => path(`M${188 + i * 8},92 l4,8 l4,-8`, { width: 1 })), rect(212, 86, 10, 28, { fill: C.steelDark }), line(222, 100, 236, 100, { width: 3 }), text(240, 104, 'adjust', { size: 9 }),
      line(100, 100, 100, 82, { width: 1, dash: '2 2', stroke: C.blue }), line(100, 82, 165, 82, { width: 1, dash: '2 2', stroke: C.blue }), line(165, 82, 165, 100, { width: 1, dash: '2 2', stroke: C.blue }),
      line(185, 100, 185, 130, { width: 1, dash: '2 2', stroke: C.blue }), line(185, 130, 130, 180, { width: 1, dash: '2 2', stroke: C.blue }),
      line(140, 82, 140, 44, { width: 1.5 }), text(140, 38, 'vent port', { anchor: 'middle', size: 9.5, weight: 600 }), text(172, 46, 'to tank = unload', { size: 8.5, fill: C.muted }), text(172, 56, 'to a remote = remote set', { size: 8.5, fill: C.muted }),
      text(155, 148, 'pilot poppet', { size: 8.5, fill: C.muted }), text(76, 200, 'main poppet', { size: 8.5, fill: C.muted }),
      ch.el, path(`M${ch.sx(0)},${ch.sy(70)} L${ch.sx(100)},${ch.sy(100)}`, { stroke: C.red, width: 2.5 }), path(`M${ch.sx(0)},${ch.sy(95)} L${ch.sx(100)},${ch.sy(100)}`, { stroke: C.green, width: 2.5 }),
      text(ch.sx(50), ch.sy(78), 'direct-acting', { anchor: 'middle', size: 9, fill: C.red }), text(ch.sx(50), ch.sy(104), 'pilot-operated', { anchor: 'middle', size: 9, fill: C.green }),
      text(ch.sx(2), ch.sy(63), 'cracking', { size: 8, fill: C.red }), text(ch.sx(58), ch.sy(112), 'full flow', { size: 8 }),
      note(390, 200, 'override: 20-40% vs 3-8%', { anchor: 'middle', size: 9.5 }),
      caption(500, 270, 'Blocked pilot orifice = the relief never opens: unprotected.'),
    ], { title: 'Pilot-operated relief' }))
}

// ---------- Counterbalance pilot ratio ----------
fig('hydraulics/counterbalance-pilot-ratio.svg', 'Counterbalance valve in the load line: set 1.3× the load pressure; the external pilot from the other line opens it as far as the pump asks; 3:1 is stable, 10:1 efficient',
  svg(500, 282, [
    rect(60, 30, 40, 110), rect(60, 84, 40, 6, { fill: C.ink }), line(80, 30, 80, 12, { width: 3 }), rect(64, 4, 32, 10, { fill: C.steelDark }), text(112, 12, 'load', { size: 9.5 }),
    line(80, 140, 80, 170, { width: 2, stroke: C.blue }), text(56, 160, 'cap end', { size: 8.5, fill: C.muted, anchor: 'end' }), text(56, 172, '(load side)', { size: 8.5, fill: C.muted, anchor: 'end' }),
    ...relief(80, 196, { size: 28 }), ...checkV(120, 196, 'up', 6), line(80, 210, 80, 236, { width: 2, stroke: C.blue }), path('M120,182 L120,170 L80,170', { width: 1.5, stroke: C.blue }), path('M120,210 L120,236 L80,236', { width: 1.5, stroke: C.blue }),
    line(100, 60, 160, 60, { width: 2, stroke: C.blue }), line(160, 60, 160, 236, { width: 2, stroke: C.blue }), line(160, 150, 112, 150, { width: 1, dash: '3 3', stroke: C.red }), line(112, 150, 112, 186, { width: 1, dash: '3 3', stroke: C.red }), text(166, 146, 'ext. pilot from', { size: 8.4, fill: C.red }), text(166, 157, 'the raise line', { size: 8.4, fill: C.red }),
    rect(60, 236, 100, 20, { fill: C.grey }), text(110, 250, 'DCV', { anchor: 'middle', size: 9.5 }),
    text(250, 40, 'Setting', { size: 10.5, weight: 700 }), text(250, 56, 'load pressure 1,200 psi (gauge, DCV centred)', { size: 9.5 }), text(250, 70, 'set ≈ 1.3 × 1,200 = 1,560 psi', { size: 10, weight: 600 }),
    text(250, 90, 'pilot needed ≈ (setting − load) ÷ ratio', { size: 9.5 }),
    table(240, 104, [['ratio', 'character', 'use'], ['3:1', 'most stable, hot', 'motors, springy booms'], ['4.5:1', 'compromise', 'most cylinders'], ['10:1', 'efficient, twitchy', 'rigid loads, short lines']], [40, 96, 118], { rowH: 22, size: 8.6 }),
    note(250, 208, 'shudder: ratio too high, air, a meter-out', { size: 9.2 }), note(250, 220, 'between DCV and this valve, back-pressure', { size: 9.2 }),
    caption(500, 282, 'A safety device: never removed or re-rated without the designer.'),
  ], { title: 'Counterbalance pilot ratio' }))

// ---------- Flow control placement ----------
fig('hydraulics/flow-control-placement.svg', 'Meter-in feeds a resistive load, meter-out holds an over-running load (watch rod-end intensification), bleed-off is efficient but least accurate',
  svg(500, 236, [
    ...[['Meter-in', (x) => [...flowCtl(x - 20, 96), line(x - 20, 60, x - 20, 88, { width: 1.5 }), line(x - 20, 104, x - 20, 130, { width: 1.5 })], 'resistive loads · precise'], ['Meter-out', (x) => [...flowCtl(x + 20, 96), line(x + 20, 60, x + 20, 88, { width: 1.5 }), line(x + 20, 104, x + 20, 130, { width: 1.5 }), line(x - 20, 60, x - 20, 130, { width: 1.5 })], 'over-running loads · usual'], ['Bleed-off', (x) => [line(x - 20, 60, x - 20, 130, { width: 1.5 }), line(x + 20, 60, x + 20, 130, { width: 1.5 }), line(x - 20, 118, x - 60, 118, { width: 1.5 }), ...flowCtl(x - 60, 100), line(x - 60, 92, x - 60, 80, { width: 1.5 }), tank(x - 60, 68, 16)], 'efficient · least accurate']].map(([n, d, t], i) => {
      const x = 90 + i * 165
      return [text(x, 24, n, { anchor: 'middle', size: 11, weight: 700 }), ...cyl(x - 40, 36, 80, 24, { pistonAt: 0.4 }), ...(n === 'Meter-in' ? [line(x + 20, 60, x + 20, 130, { width: 1.5 })] : []), ...d(x), rect(x - 36, 130, 72, 24, { fill: C.grey }), text(x, 146, 'DCV', { anchor: 'middle', size: 9 }), line(x, 154, x, 170, { width: 1.5 }), ...pump(x, 184, 12), note(x, 210, t, { anchor: 'middle', size: 9 })]
    }),
    caption(500, 236, 'A flow control changes speed, never force.'),
  ], { title: 'Flow control placement' }))

// ---------- Fitting identification steps ----------
fig('hydraulics/fitting-identification-steps.svg', 'Identify a fitting in five steps: measure the thread, count the pitch, check for taper, look at the seat, gauge the cone angle, then read the table',
  svg(500, 306, [
    box(20, 20, 130, 34, '1 measure OD (male)\nor ID (female)', { size: 9.5 }), line(150, 37, 178, 37, { width: 1.5, arrow: 'end' }),
    box(180, 20, 130, 34, '2 pitch: tpi or mm', { size: 9.5 }), line(310, 37, 338, 37, { width: 1.5, arrow: 'end' }),
    box(340, 20, 140, 34, '3 tapered or parallel?', { size: 9.5, fill: C.soft }),
    line(410, 54, 410, 76, { width: 1.5, arrow: 'end' }), text(420, 68, 'tapered', { size: 9, fill: C.red }), box(340, 78, 140, 34, 'pipe thread:\nNPT 60° · BSPT 55°', { size: 9.5, fill: C.redSoft }),
    line(340, 37, 250, 37, { width: 0 }), line(245, 54, 245, 76, { width: 1.5, arrow: 'end' }), text(252, 68, 'parallel', { size: 9, fill: C.green }),
    box(180, 78, 130, 34, '4 look at the seat', { size: 9.5, fill: C.soft }),
    ...[['cone / flare', 'cone angle (5): 37° JIC · 45° SAE\n30° JIS, Komatsu · 24° DIN · 60° BSP'], ['flat face + O-ring', 'ORFS'], ['O-ring at the shoulder', 'ORB (SAE) · ISO 6149 · BSPP washer'], ['4-bolt flange head', 'Code 61 / Code 62 (bolt spacing)'], ['bite ring / captive ring', 'DIN 24° L or S (tube OD)']].map(([seat, res], i) => {
      const y = 130 + i * 32; const two = res.includes('\n')
      return [text(20, y + 15, seat, { size: 9.5, weight: 600 }), line(150, y + 11, 176, y + 11, { width: 1, arrow: 'end', stroke: C.muted }), rect(180, y - 2, 300, 26, { fill: i === 0 ? C.greenSoft : C.grey, stroke: C.line, rx: 4 }), two ? [text(190, y + 8, res.split('\n')[0], { size: 8.4 }), text(190, y + 19, res.split('\n')[1], { size: 8.4 })] : text(190, y + 14, res, { size: 8.8 })]
    }),
    caption(500, 306, 'Then identify the port the same way: a fitting and its mate are two jobs.'),
  ], { title: 'Fitting identification steps' }))

// ---------- Thread OD look-up ----------
{
  const rows = [['measured OD', 'tpi / pitch', 'form', 'it is (or could be)'],
    ['0.437" · 11.1 mm', '20', 'parallel', 'JIC/ORB −4 · SAE 45° −4'], ['0.518" · 13.2', '19', 'parallel', 'G 1/4 BSPP · JIS 30° 1/4'], ['0.540" · 13.7', '18', 'tapered', '1/4 NPT'], ['0.562" · 14.3', '18', 'parallel', 'JIC/ORB −6 · ORFS −4'],
    ['0.675" · 17.1', '18', 'tapered', '3/8 NPT'], ['0.687" · 17.5', '16', 'parallel', 'ORFS −6'], ['0.750" · 19.0', '16', 'parallel', 'JIC/ORB −8 · SAE 45° −8 (1/2")'], ['0.825" · 20.9', '14', 'parallel', 'G 1/2 BSPP · JIS 30° 1/2'], ['0.840" · 21.3', '14', 'tapered', '1/2 NPT'],
    ['0.875" · 22.2', '14', 'parallel', 'JIC/ORB −10 (M22×1.5 is 0.866")'], ['1.000" · 25.4', '14', 'parallel', 'ORFS −10'], ['1.062" · 27.0', '12', 'parallel', 'JIC/ORB −12'], ['1.187" · 30.2', '12', 'parallel', 'JIC −14 · ORFS −12'], ['1.312" · 33.3', '12', 'parallel', 'JIC/ORB −16'],
    ['0.472" · M12', '1.5 mm', 'parallel', 'DIN 6L · ISO 6149 M12'], ['0.630" · M16', '1.5 mm', 'parallel', 'DIN 10L or 8S · ISO 6149 M16'], ['0.709" · M18', '1.5 mm', 'parallel', 'DIN 12L or 10S · ISO 6149 M18'], ['0.866" · M22', '1.5 mm', 'parallel', 'DIN 15L or 14S · ISO 6149 M22']]
  fig('hydraulics/thread-od-lookup.svg', 'Thread look-up: the caliper reading and the pitch narrow a male thread to a family; the seat then decides between the candidates on one line',
    svg(500, 400, [text(250, 20, 'Male thread major diameter and pitch → candidates (the seat decides)', { anchor: 'middle', size: 11, weight: 700 }), table(14, 30, rows, [104, 62, 54, 252], { rowH: 18, size: 8.8 }), caption(500, 400, 'Diameters ±0.010"; pitch 1.5 mm ≈ 17 tpi, 2 mm ≈ 12.7 tpi.')], { title: 'Thread OD look-up' }))
}

// ---------- Code 61 vs 62 flange ----------
fig('hydraulics/code-61-62-flange.svg', 'SAE 4-bolt flanges for a 1 inch port: Code 61 (3,000 psi) and Code 62 (6,000 psi) have different bolt spacings and head thickness; measure centre to centre before ordering',
  svg(500, 254, [
    ...[['Code 61 · 3,000 psi', 52.4, 26.2, '2.062" × 1.031"', '3/8-16 / M10', 120], ['Code 62 · 6,000 psi', 57.2, 27.8, '2.250" × 1.094"', '7/16-14 / M12', 360]].map(([n, a, b, dims, bolt, cx]) => {
      const k = 2.4, w = a * k, h = b * k, x = cx - w / 2, y = 100 - h / 2
      return [text(cx, 30, n, { anchor: 'middle', size: 11, weight: 700 }), rect(x - 22, y - 22, w + 44, h + 44, { fill: C.grey, rx: 8 }), circle(cx, 100, 22, { fill: C.blueSoft, stroke: C.blue }), circle(cx, 100, 27, { fill: 'none', stroke: '#333', width: 3 }),
        ...[[x, y], [x + w, y], [x, y + h], [x + w, y + h]].map(([bx, by]) => circle(bx, by, 5, { fill: C.steelDark, stroke: 'none' })),
        dim(x, y + h + 30, x + w, y + h + 30, dims.split(' × ')[0], { size: 9 }), dim(x + w + 30, y, x + w + 30, y + h, dims.split(' × ')[1], { size: 9 }),
        text(cx, 190, `bolts ${bolt}`, { anchor: 'middle', size: 9.5 }), text(cx, 204, 'O-ring −219', { anchor: 'middle', size: 9.5, fill: C.muted })]
    }),
    note(250, 226, 'Code 62 head is thicker: a 61 head in a 62 clamp seats, holds at idle, blows under load', { anchor: 'middle', size: 9 }),
    caption(500, 254, 'Cross pattern, three stages, halves parallel to the face.'),
  ], { title: 'Code 61 vs 62 flange' }))

// ---------- DIN bite ring assembly ----------
fig('hydraulics/din-bite-ring-assembly.svg', 'DIN 2353 24° fitting: tube bottomed in the cone, ring cutting edge toward the body; pre-assemble 1-1/4 to 1-1/2 turns past resistance, final 1/4 to 1/2 turn; L and S series share threads but not cones',
  svg(500, 250, [
    poly([[40, 70], [150, 70], [150, 92], [176, 104], [176, 136], [150, 148], [150, 170], [40, 170]], { fill: C.steel, stroke: C.ink }), text(90, 124, 'body', { anchor: 'middle', size: 10, weight: 600 }), text(163, 88, '24°', { size: 9, fill: C.blue }),
    rect(176, 96, 140, 48, { fill: C.grey, stroke: C.ink }), text(246, 124, 'nut', { anchor: 'middle', size: 10, weight: 600 }),
    rect(150, 108, 180, 24, { fill: C.paper, stroke: C.ink }), rect(150, 108, 180, 24, { fill: 'none' }), text(300, 124, 'tube', { anchor: 'middle', size: 9.5 }), line(150, 108, 150, 132, { width: 2.5, stroke: C.red }), text(150, 158, 'bottomed', { anchor: 'middle', size: 8.5, fill: C.red }), text(150, 168, 'in the cone', { anchor: 'middle', size: 8.5, fill: C.red }),
    poly([[164, 104], [184, 100], [184, 140], [164, 136]], { fill: C.brass, stroke: C.accentDark }), text(190, 92, 'ring', { size: 8.5, fill: C.accentDark }), line(168, 108, 160, 112, { width: 1.5, stroke: C.red }), text(206, 156, 'cutting edge toward the body', { size: 8.5, fill: C.accentDark }),
    text(330, 40, 'Assembly', { size: 10.5, weight: 700 }), legend(330, 58, ['cut square, deburr, mark depth', 'nut, then ring (edge forward)', 'tube bottomed; hold it there', 'pre-assemble 1¼-1½ turns past\nresistance (collar 80%+)', 'final: hand-tight + 1/4-1/2 turn', 're-assembly: 1/4 turn only'], { size: 8.4, gap: 13 }),
    text(40, 200, 'Same thread, two cones:', { size: 9.5, weight: 700 }), note(40, 214, 'M14: 8L or 6S · M16: 10L or 8S · M18: 12L or 10S', { size: 9 }), note(40, 226, 'M22: 15L or 14S · M30: 22L or 20S · M36: 28L or 25S', { size: 9 }),
    caption(500, 250, 'Identify by tube OD and the L or S stamping on the nut.'),
  ], { title: 'DIN bite ring assembly' }))

// ---------- Viscosity window by pump ----------
{
  // ASTM D341 (Walther) fit through v40 = VG and a v100 typical of VI ~100 mineral oil
  const K = (F) => (F - 32) * 5 / 9 + 273.15
  const fit = (v40, v100) => { const W = (v) => Math.log10(Math.log10(v + 0.7)); const B = (W(v40) - W(v100)) / (Math.log10(K(212)) - Math.log10(K(104))); const A = W(v40) + B * Math.log10(K(104)); return (F) => 10 ** (10 ** (A - B * Math.log10(K(F)))) - 0.7 }
  const grades = [[32, 5.4, C.blue], [46, 6.8, C.green], [68, 8.7, C.accentDark]]
  const ch = chart({ x: 60, y: 30, w: 400, h: 200, xmin: 0, xmax: 200, ymin: 0.7, ymax: 3.3, xticks: [0, 40, 80, 120, 160, 200], yticks: [1, 1.5, 2, 2.5, 3], xlabel: 'Oil temperature (°F)', ylabel: 'viscosity cSt (log)', yfmt: (v) => Math.round(10 ** v) })
  const lines = grades.map(([vg, v100, c], i) => { const f = fit(vg, v100); const pts = []; for (let F = 0; F <= 200; F += 5) { const v = Math.log10(f(F)); if (v <= 3.3) pts.push([F, v]) } return [path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5 }), line(ch.sx(140), ch.sy(2.85 - i * 0.17), ch.sx(152), ch.sy(2.85 - i * 0.17), { stroke: c, width: 3 }), text(ch.sx(156), ch.sy(2.85 - i * 0.17) + 4, 'ISO VG ' + vg, { size: 10, fill: c, weight: 600 })] })
  fig('hydraulics/viscosity-window-by-pump.svg', 'Viscosity against temperature for VG 32, 46 and 68 with the pump windows: below about 10-13 cSt the film fails, 16-36 cSt is the optimum for piston and vane pumps, above 850-1,000 cSt a cold start cavitates',
    svg(500, 290, [ch.el,
      rect(ch.x, ch.sy(3.3), ch.w, ch.sy(3.0) - ch.sy(3.3), { fill: C.redSoft, stroke: 'none', opacity: 0.7 }), text(ch.sx(100), ch.sy(3.16), 'cold-start limit: 850-1,000 cSt (piston, vane)', { anchor: 'middle', size: 9, fill: C.red }),
      rect(ch.x, ch.sy(Math.log10(36)), ch.w, ch.sy(Math.log10(16)) - ch.sy(Math.log10(36)), { fill: C.greenSoft, stroke: 'none', opacity: 0.7 }), text(ch.sx(3), ch.sy(Math.log10(23)), 'optimum 16-36 cSt (piston, vane)', { size: 9.5, fill: C.green }),
      rect(ch.x, ch.sy(Math.log10(10)), ch.w, ch.sy(0.7) - ch.sy(Math.log10(10)), { fill: C.redSoft, stroke: 'none', opacity: 0.7 }), text(ch.sx(3), ch.sy(0.84), 'below 10-13 cSt: film fails, vane tips scuff', { size: 9, fill: C.red }),
      lines, caption(500, 290, 'Reservoir temperature picks the grade; HV grades flatten the line.')], { title: 'Viscosity window by pump' }))
}

// ---------- Fluid seal compatibility ----------
{
  const cols = ['Mineral', 'HFC', 'HFDR', 'HFDU', 'HEES', 'HEPG', 'Brake fl.']
  const rows = [['NBR', 'Y', 'Y', 'N', 'C', 'C', 'C', 'N'], ['HNBR', 'Y', 'Y', 'N', 'Y', 'Y', 'C', 'N'], ['FKM', 'Y', 'C', 'Y', 'Y', 'Y', 'Y', 'N'], ['EPDM', 'N', 'Y', 'Y', 'N', 'N', 'Y', 'Y'], ['PU', 'Y', 'N', 'N', 'C', 'C', 'N', 'N'], ['PTFE', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y', 'Y']]
  const col = { Y: C.greenSoft, C: C.soft, N: C.redSoft }
  fig('hydraulics/fluid-seal-compatibility.svg', 'Seal material against fluid family: Y compatible, C check the grade with the supplier, N fails; a fluid conversion is a seal change',
    svg(500, 274, [text(250, 22, 'Seal compatibility by fluid family', { anchor: 'middle', size: 11.5, weight: 700 }),
      ...cols.map((c, j) => text(131 + j * 52, 46, c, { anchor: 'middle', size: 9.5, weight: 600 })),
      ...rows.map((r, i) => [text(96, 72 + i * 26, r[0], { anchor: 'end', size: 10, weight: 600 }), ...r.slice(1).map((v, j) => [rect(105 + j * 52, 55 + i * 26, 52, 26, { fill: col[v], stroke: C.line }), text(131 + j * 52, 72 + i * 26, v, { anchor: 'middle', size: 11, weight: 600 })])]),
      note(20, 228, 'NBR nitrile · HNBR hydrogenated nitrile · FKM Viton · EPDM ethylene-propylene · PU polyurethane', { size: 8.8 }),
      note(20, 241, 'HFC water-glycol · HFDR phosphate ester · HFDU polyol ester · HEES synthetic ester · HEPG polyglycol', { size: 8.8 }),
      caption(500, 274, 'Formulations differ: the fluid supplier sheet for that fluid governs.')], { title: 'Fluid seal compatibility' }))
}

// ---------- Fluid classes ----------
fig('hydraulics/fluid-classes.svg', 'Hydraulic fluid families: mineral classes by additive package, fire-resistant by water or synthetic base, biodegradable by base oil, and the machine-specific fluids that are not interchangeable',
  svg(500, 250, [
    box(180, 14, 140, 28, 'Hydraulic fluids', { size: 11, weight: 700, fill: C.soft }),
    ...[[70, 'Mineral', ['HL: R&O, no AW', 'HM / HLP: AW (zinc)', 'HV / HVLP: + VI improver', 'HLPD: + detergent', 'zinc-free HM: ashless']], [190, 'Fire-resistant', ['HFAE/S: 95% water', 'HFB: invert emulsion', 'HFC: water-glycol', 'HFDR: phosphate ester', 'HFDU: polyol ester']], [310, 'Biodegradable', ['HETG: vegetable', 'HEES: synthetic ester', 'HEPG: PAG (no mixing)', 'HEPR: PAO']], [430, 'Machine-specific', ['UTTO / tractor fluid', 'engine oil, HYDO, TO-4', 'ATF (Dexron)', 'aviation 5606 / 83282', 'food grade H1']]].map(([x, n, items]) => [line(250, 42, x, 64, { width: 1 }), box(x - 55, 64, 110, 24, n, { size: 10, weight: 700 }), ...items.map((s, i) => text(x, 106 + i * 15, s, { anchor: 'middle', size: 8.6 }))]),
    caption(500, 250, 'Grade = viscosity; class = chemistry; approvals = the pump.'),
  ], { title: 'Fluid classes' }))

// ---------- Troubleshooting decision tree ----------
fig('hydraulics/troubleshooting-decision-tree.svg', 'Diagnostic tree: define the symptom, gauge the actuator and the pump, then the test that splits the circuit: pump flow, relief, cylinder bypass, holding-valve decay, heat map',
  svg(500, 300, [
    box(170, 12, 160, 28, 'symptom at which step?', { size: 10, weight: 700, fill: C.soft }), line(250, 40, 250, 56, { width: 1.5, arrow: 'end' }),
    box(150, 58, 200, 28, 'gauge at the actuator port', { size: 10 }),
    ...[[70, 'low'], [250, 'ok but slow'], [430, 'ok but drifts / hot']].map(([x, l]) => [line(250, 86, x, 108, { width: 1.2, arrow: 'end' }), text(x, 104 + (x === 250 ? -8 : 0), l, { anchor: 'middle', size: 8.5, fill: C.muted })]),
    box(10, 110, 120, 28, 'gauge at the pump', { size: 9.5 }), box(190, 110, 120, 28, 'flow test: pump (1)', { size: 9.5 }), box(370, 110, 120, 28, 'heat map (12)', { size: 9.5 }),
    line(40, 138, 40, 160, { width: 1.2, arrow: 'end' }), text(48, 154, 'low', { size: 8.5, fill: C.muted }), line(100, 138, 100, 160, { width: 1.2, arrow: 'end' }), text(106, 154, 'ok', { size: 8.5, fill: C.muted }),
    box(4, 162, 68, 40, 'relief (2)\ncompensator\npump (1)', { size: 8.5, fill: C.grey }), box(76, 162, 60, 40, 'restriction\nor leak\nbetween', { size: 8.5, fill: C.grey }),
    line(220, 138, 220, 160, { width: 1.2, arrow: 'end' }), text(226, 154, 'pump ok', { size: 8.5, fill: C.muted }), line(290, 138, 290, 160, { width: 1.2, arrow: 'end' }), text(296, 154, 'low', { size: 8.5, fill: C.muted }),
    box(160, 162, 110, 40, 'cylinder bypass (3)\nmotor drain (5)\nflow control, POC', { size: 8.5, fill: C.grey }), box(276, 162, 74, 40, 'worn pump\nsuction (9)\nrpm, oil', { size: 8.5, fill: C.grey }),
    line(400, 138, 400, 160, { width: 1.2, arrow: 'end' }), text(406, 154, 'hot part', { size: 8.5, fill: C.muted }), line(460, 138, 460, 160, { width: 1.2, arrow: 'end' }), text(466, 154, 'drift', { size: 8.5, fill: C.muted }),
    box(360, 162, 72, 40, 'relief dumping\ncheck leaking\ncylinder bypass', { size: 8.2, fill: C.grey }), box(436, 162, 60, 40, 'decay test\n(6), then\nbypass (3)', { size: 8.5, fill: C.grey }),
    box(60, 222, 380, 26, 'shifts on override only = electrical · shifts on neither = pilot pressure or stuck spool', { size: 9 }),
    box(60, 254, 380, 26, 'erratic = air first · intermittent = log coil voltage and pressure through the fault', { size: 9 }),
    caption(500, 300, 'Numbers = the tests in the article; change one thing, retest.'),
  ], { title: 'Troubleshooting decision tree' }))

// ---------- Cylinder bypass test ----------
fig('hydraulics/cylinder-bypass-test.svg', 'Piston bypass test: cylinder fully extended against its stop, rod-end line off and capped, cap end pressurised, measure what comes out of the rod-end port in a minute',
  svg(500, 242, [
    rect(80, 70, 220, 50), rect(268, 70, 6, 50, { fill: C.ink }), line(274, 95, 360, 95, { width: 4 }), rect(360, 80, 14, 30, { fill: C.steelDark }), text(367, 128, 'stop', { anchor: 'middle', size: 9 }),
    rect(80, 70, 188, 50, { fill: '#dbeafe', stroke: 'none' }), rect(80, 70, 220, 50, { fill: 'none' }), text(174, 99, 'cap end at working pressure', { anchor: 'middle', size: 9.5, fill: C.blue }),
    line(100, 120, 100, 160, { width: 2.5, stroke: C.blue }), ...gauge(150, 140, ''), text(166, 144, '3,000 psi', { size: 9 }), line(100, 140, 140, 140, { width: 1.5 }), rect(70, 160, 60, 22, { fill: C.grey }), text(100, 175, 'DCV', { anchor: 'middle', size: 9 }),
    line(290, 70, 290, 40, { width: 2 }), rect(284, 30, 12, 10, { fill: C.red }), text(310, 40, 'rod-end line off,', { size: 9 }), text(310, 52, 'line capped', { size: 9 }),
    line(290, 120, 290, 150, { width: 2, stroke: C.blue }), ...[158, 168, 178].map((y) => circle(290, y, 2, { fill: C.blue, stroke: 'none' })), rect(270, 184, 40, 30, { fill: C.blueSoft, rx: 3 }), text(290, 203, '1 min', { anchor: 'middle', size: 9, weight: 600 }),
    text(330, 175, 'drops: seals ok', { size: 9.5, fill: C.green }), text(330, 189, 'stream: piston seals', { size: 9.5, fill: C.red }), text(330, 203, 'or a scored bore', { size: 9.5, fill: C.red }),
    note(20, 40, 'lockout first · hot oil · rod cannot move', { size: 9 }),
    caption(500, 242, 'Repeat retracted with the ports swapped; test hot: cold seals pass.'),
  ], { title: 'Cylinder bypass test' }))

// ---------- Heat balance ----------
fig('hydraulics/heat-balance.svg', 'Heat balance: every horsepower in that is not work out is heat, 2,545 BTU/h each; the reservoir sheds almost none of it, the cooler must take the rest',
  svg(500, 230, [
    text(20, 30, 'Input 50 hp', { size: 11, weight: 700 }),
    rect(20, 40, 440, 30, { fill: C.grey, stroke: C.line }), rect(20, 40, 308, 30, { fill: C.greenSoft, stroke: C.green }), text(174, 60, 'useful work 35 hp', { anchor: 'middle', size: 10.5, weight: 600, fill: C.green }),
    rect(328, 40, 35, 30, { fill: C.soft, stroke: C.accentDark }), rect(363, 40, 44, 30, { fill: C.soft, stroke: C.accentDark }), rect(407, 40, 53, 30, { fill: C.redSoft, stroke: C.red }),
    text(345, 86, 'pump', { anchor: 'middle', size: 8.5 }), text(345, 96, '4 hp', { anchor: 'middle', size: 8.5 }), text(385, 86, 'valves', { anchor: 'middle', size: 8.5 }), text(385, 96, '5 hp', { anchor: 'middle', size: 8.5 }), text(433, 86, 'relief', { anchor: 'middle', size: 8.5, fill: C.red }), text(433, 96, '6 hp', { anchor: 'middle', size: 8.5, fill: C.red }),
    line(328, 110, 460, 110, { width: 1, arrow: 'both' }), text(394, 124, 'heat 15 hp = 38,000 BTU/h', { anchor: 'middle', size: 9.5, weight: 600, fill: C.red }),
    text(20, 150, 'heat (BTU/h) = (input hp − work hp) × 2,545', { size: 10 }), text(20, 166, 'hp lost across a drop = gpm × psi ÷ 1714   (10 gpm over a relief at 2,000 psi = 11.7 hp)', { size: 9.5 }),
    text(20, 182, 'bare tank sheds ≈ 0.001 hp per ft² per °F above ambient: a 100 gal tank ≈ 1-1.5 hp', { size: 9.5 }),
    text(20, 198, 'target tank 110-130°F; every +18°F above 140°F halves the oil life', { size: 9.5 }),
    caption(500, 230, 'A cooler bought to fix a dumping relief cools the symptom forever.'),
  ], { title: 'Heat balance' }))

// ---------- Load-sense margin ----------
fig('hydraulics/load-sense-margin.svg', 'Load-sense circuit: the valve sends the highest load pressure back on the LS line; the pump holds its outlet a fixed margin (200-350 psi) above it and makes only the flow the spools pass',
  svg(500, 262, [
    ...pump(70, 130, 30, { variable: true }), line(70, 160, 70, 190, { width: 1.5 }), tank(70, 190), rect(110, 96, 40, 24, { fill: C.grey }), text(130, 111, 'LS ctl', { anchor: 'middle', size: 8.5 }),
    line(70, 100, 70, 50, { width: 2.5 }), line(70, 50, 300, 50, { width: 2.5, arrow: 'end' }), ...gauge(180, 50, '', { r: 10 }), text(180, 30, 'pump 1,450 psi', { anchor: 'middle', size: 9.5, weight: 600 }),
    rect(300, 34, 120, 130, { fill: C.grey, rx: 4 }), text(360, 52, 'valve section', { anchor: 'middle', size: 9.5, weight: 600 }), rect(316, 66, 88, 12, { fill: C.steel }), ...[330, 360, 390].map((x) => rect(x - 5, 66, 10, 12, { fill: C.steelDark })), text(360, 94, 'spool opening', { anchor: 'middle', size: 8.5, fill: C.muted }), text(360, 106, '= flow at fixed ΔP', { anchor: 'middle', size: 8.5, fill: C.muted }),
    circle(360, 128, 5, { fill: C.paper, stroke: C.blue }), text(360, 148, 'shuttle', { anchor: 'middle', size: 8.5, fill: C.blue }),
    line(420, 72, 460, 72, { width: 2.5 }), ...cyl(420, 96, 50, 20), text(470, 130, 'load', { anchor: 'middle', size: 9 }), text(470, 142, '1,200 psi', { anchor: 'middle', size: 9, weight: 600 }),
    line(360, 133, 360, 200, { width: 1.2, dash: '4 3', stroke: C.blue }), line(360, 200, 130, 200, { width: 1.2, dash: '4 3', stroke: C.blue }), line(130, 200, 130, 120, { width: 1.2, dash: '4 3', stroke: C.blue, arrow: 'end' }), text(245, 214, 'LS line: 1,200 psi', { anchor: 'middle', size: 9.5, fill: C.blue, weight: 600 }),
    ...relief(230, 176, { size: 20 }), text(230, 158, 'LS relief', { anchor: 'middle', size: 8.5 }), line(230, 186, 230, 200, { width: 1, stroke: C.blue, dash: '3 2' }),
    box(150, 84, 90, 26, 'margin 250 psi', { size: 9.5, fill: C.greenSoft, stroke: C.green }),
    note(360, 234, 'idle: LS at 0 → pump at margin, cool', { anchor: 'middle', size: 9 }),
    caption(500, 262, 'Nothing moves and the pump sits at 250 psi: the LS signal is lost.'),
  ], { title: 'Load-sense margin' }))

// ---------- Proportional valve loop ----------
fig('hydraulics/proportional-valve-loop.svg', 'Closed-loop proportional valve: the amplifier turns the command into a PWM current with ramps, deadband step, gain and dither; the LVDT reports the spool position back',
  svg(500, 200, [
    box(20, 40, 80, 40, 'command\n±10 V, 4-20 mA', { size: 9 }), line(100, 60, 128, 60, { width: 1.5, arrow: 'end' }),
    box(130, 30, 120, 60, 'amplifier / OBE\nramp · deadband\ngain · Imin · dither', { size: 9, fill: C.soft }), line(250, 60, 278, 60, { width: 1.5, arrow: 'end' }), text(264, 52, 'PWM', { anchor: 'middle', size: 8, fill: C.muted }), text(264, 76, 'current', { anchor: 'middle', size: 8, fill: C.muted }),
    box(280, 40, 80, 40, 'proportional\nsolenoid', { size: 9 }), line(360, 60, 388, 60, { width: 1.5, arrow: 'end' }),
    box(390, 40, 90, 40, 'spool\n(flow ∝ position)', { size: 9 }),
    rect(390, 100, 90, 24, { fill: C.grey }), text(435, 116, 'LVDT', { anchor: 'middle', size: 9.5, weight: 600 }), line(435, 80, 435, 100, { width: 1.2 }),
    path('M390,112 L190,112 L190,90', { width: 1.5, arrow: 'end', stroke: C.blue }), text(290, 126, 'position feedback (closed loop: hysteresis < 1%)', { anchor: 'middle', size: 9, fill: C.blue }),
    note(250, 156, 'check: command at the card → current at the test point → feedback follows → pilot pressure at X', { anchor: 'middle', size: 9 }),
    note(250, 172, 'dither to zero = sticking · gain too high = buzzing · no enable = dead valve', { anchor: 'middle', size: 9 }),
    caption(500, 200, 'Swap a card-driven valve and the settings go with the card, not the valve.'),
  ], { title: 'Proportional valve loop' }))

// ---------- Servo valve stages ----------
fig('hydraulics/servo-valve-stages.svg', 'Two-stage servo valve: the torque motor tilts a flapper between two nozzles, the pressure difference drives the spool, and the feedback wire balances the spool against the coil current',
  svg(500, 272, [
    rect(180, 20, 140, 40, { fill: C.grey, rx: 4 }), text(250, 36, 'torque motor', { anchor: 'middle', size: 10, weight: 600 }), text(250, 50, 'coils ±8 to ±40 mA', { anchor: 'middle', size: 8.5, fill: C.muted }),
    line(250, 60, 250, 140, { width: 3, stroke: C.ink }), text(258, 128, 'flapper', { size: 9 }),
    poly([[210, 96], [236, 100], [210, 104]], { fill: C.steel, stroke: C.ink }), poly([[290, 96], [264, 100], [290, 104]], { fill: C.steel, stroke: C.ink }), text(200, 90, 'nozzle', { anchor: 'end', size: 8.5, fill: C.muted }), text(300, 90, 'nozzle', { size: 8.5, fill: C.muted }),
    line(210, 100, 170, 100, { width: 1.5, stroke: C.blue }), line(290, 100, 330, 100, { width: 1.5, stroke: C.blue }), circle(170, 100, 4, { fill: C.paper, stroke: C.blue }), circle(330, 100, 4, { fill: C.paper, stroke: C.blue }), text(150, 84, 'fixed', { anchor: 'middle', size: 8, fill: C.blue }), text(150, 94, 'orifice', { anchor: 'middle', size: 8, fill: C.blue }), text(350, 84, 'fixed', { anchor: 'middle', size: 8, fill: C.blue }), text(350, 94, 'orifice', { anchor: 'middle', size: 8, fill: C.blue }),
    line(170, 104, 170, 160, { width: 1.5, stroke: C.blue }), line(330, 104, 330, 160, { width: 1.5, stroke: C.blue }), line(150, 100, 130, 100, { width: 1.5, stroke: C.blue }), line(350, 100, 370, 100, { width: 1.5, stroke: C.blue }), text(122, 104, 'Ps', { anchor: 'end', size: 9, fill: C.blue }), text(378, 104, 'Ps', { size: 9, fill: C.blue }),
    rect(140, 160, 220, 40, { fill: C.grey }), rect(156, 168, 188, 24, { fill: C.steel }), ...[190, 250, 310].map((x) => rect(x - 12, 168, 24, 24, { fill: C.steelDark })), text(250, 244, 'spool: the pressure difference from the nozzles drives it', { anchor: 'middle', size: 9 }),
    path('M250,140 q-40,20 -10,44', { width: 1.5, stroke: C.red }), text(258, 158, 'feedback wire', { size: 8.5, fill: C.red }),
    ...[[170, 'P'], [210, 'A'], [290, 'B'], [330, 'T']].map(([x, l]) => [line(x, 200, x, 214, { width: 1.5 }), text(x, 228, l, { anchor: 'middle', size: 9 })]),
    text(30, 140, 'clearances 25-50 µm', { size: 9 }), text(30, 154, '3 µm β₃ ≥ 200 filter', { size: 9, weight: 600 }), text(30, 168, 'ISO 16/14/11 or better', { size: 9 }),
    caption(500, 272, 'A particle in one nozzle sends the spool hard over: filtration is its life.'),
  ], { title: 'Servo valve stages' }))

// ---------- Hydrostatic drive loop ----------
fig('hydraulics/hydrostatic-drive-loop.svg', 'Closed-loop hydrostatic transmission: variable pump and motor joined by two loop lines, the charge pump makes up leakage through the loop checks, cross-port reliefs protect the loop, the flushing valve exchanges hot oil through the cooler',
  svg(500, 302, [
    ...pump(90, 110, 30, { variable: true }), text(90, 156, 'variable pump', { anchor: 'middle', size: 9.5, weight: 600 }), text(90, 168, 'over-centre', { anchor: 'middle', size: 8.5, fill: C.muted }),
    ...motor(400, 110, 30), text(400, 156, 'motor', { anchor: 'middle', size: 9.5, weight: 600 }), line(430, 110, 460, 110, { width: 4 }), text(470, 114, 'wheel', { size: 8.5 }),
    line(90, 80, 400, 80, { width: 3, stroke: C.red }), text(245, 74, 'high side: 4,000-6,000 psi', { anchor: 'middle', size: 9, fill: C.red }),
    line(90, 140, 400, 140, { width: 3, stroke: C.blue }), text(245, 154, 'low side: charge pressure 200-350 psi', { anchor: 'middle', size: 9, fill: C.blue }),
    ...relief(200, 110, { size: 18 }), line(200, 80, 200, 101, { width: 1, stroke: C.red }), line(200, 119, 200, 140, { width: 1, stroke: C.blue }), text(200, 46, 'cross-port', { anchor: 'middle', size: 8, fill: C.muted }), text(200, 56, 'reliefs', { anchor: 'middle', size: 8, fill: C.muted }),
    ...pump(160, 210, 14), text(160, 236, 'charge pump', { anchor: 'middle', size: 8.5 }), line(160, 196, 160, 176, { width: 1.5 }), line(160, 176, 260, 176, { width: 1.5 }), ...checkV(260, 158, 'up', 5), line(260, 176, 260, 164, { width: 1.5 }), line(260, 152, 260, 140, { width: 1.5 }), ...checkV(290, 158, 'up', 5), line(290, 176, 290, 164, { width: 1.5 }), line(290, 152, 290, 80, { width: 1, stroke: C.line }), line(260, 176, 290, 176, { width: 1.5 }), text(275, 190, 'loop checks', { anchor: 'middle', size: 8, fill: C.muted }),
    ...relief(110, 190, { size: 16 }), line(160, 190, 118, 190, { width: 1 }), line(102, 190, 60, 190, { width: 1 }), text(110, 214, 'charge relief', { anchor: 'middle', size: 8 }), text(60, 204, 'to case', { anchor: 'middle', size: 8, fill: C.muted }),
    line(160, 224, 160, 250, { width: 1.5 }), rect(140, 250, 40, 14, { fill: C.grey }), text(160, 260, 'filter', { anchor: 'middle', size: 8 }), tank(160, 268, 20),
    rect(330, 190, 60, 22, { fill: C.grey }), text(360, 204, 'flushing', { anchor: 'middle', size: 8.5 }), line(360, 140, 360, 190, { width: 1, dash: '3 2' }), line(360, 212, 360, 240, { width: 1, dash: '3 2' }), rect(330, 240, 60, 20, { fill: C.blueSoft, stroke: C.blue }), text(360, 253, 'cooler', { anchor: 'middle', size: 8.5, fill: C.blue }), line(390, 250, 420, 250, { width: 1 }), tank(430, 244, 18),
    text(440, 200, 'case drains', { anchor: 'middle', size: 8, fill: C.muted }), text(440, 210, '< 40 psi', { anchor: 'middle', size: 8, fill: C.muted }),
    text(20, 30, 'first reading: charge pressure', { size: 9.5, weight: 700, fill: C.blue }),
    caption(500, 302, 'Charge good in neutral but collapsing under load: the loop leaks.'),
  ], { title: 'Hydrostatic drive loop' }))
