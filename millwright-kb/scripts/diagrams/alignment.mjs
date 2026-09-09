import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'

function shaftPair(x, y, off, ang, labelL, labelR) {
  const out = [rect(x, y - 10, 90, 20, { fill: C.steel }), rect(x + 90, y - 26, 30, 52, { fill: C.grey })]
  out.push(g([rect(0, -26, 30, 52, { fill: C.grey }), rect(30, -10, 90, 20, { fill: C.steel })], { transform: `translate(${x + 126},${y + off}) rotate(${ang})` }))
  out.push(line(x, y, x + 120, y, { dash: '6 4', width: 1, stroke: C.blue })); out.push(g([line(0, 0, 150, 0, { dash: '6 4', width: 1, stroke: C.red })], { transform: `translate(${x + 126},${y + off}) rotate(${ang})` }))
  if (labelL) out.push(note(x + 45, y + 30, labelL, { anchor: 'middle', size: 10 }))
  if (labelR) out.push(note(x + 200, y + 30, labelR, { anchor: 'middle', size: 10 }))
  return out
}

// ---------- Laser ----------
fig('alignment/laser-alignment-positions.svg', 'Laser alignment: heads on both shafts, rotate together through at least 3 positions, then live-move with shims and jack bolts',
  svg(500, 260, [
    rect(20, 120, 130, 24, { fill: C.steel }), rect(150, 100, 40, 64, { fill: C.grey }), rect(200, 100, 40, 64, { fill: C.grey }), rect(240, 120, 240, 24, { fill: C.steel }),
    ...[[100, 'S'], [290, 'M']].map(([x, n]) => [rect(x - 10, 108, 20, 24, { fill: C.ink }), rect(x - 22, 60, 44, 44, { fill: C.blue, rx: 5 }), text(x, 88, n, { anchor: 'middle', size: 14, fill: '#fff', weight: 700 }), line(x, 104, x, 108, { width: 3 })]),
    line(122, 82, 268, 82, { stroke: C.red, width: 1.5, dash: '3 3' }), line(268, 78, 122, 78, { stroke: C.red, width: 1.5, dash: '3 3' }),
    circle(410, 62, 32, { fill: C.paper, stroke: C.line }), ...[[-90, '12'], [0, '3'], [90, '6'], [180, '9']].map(([a, n]) => [circle(410 + 32 * Math.cos(a * Math.PI / 180), 62 + 32 * Math.sin(a * Math.PI / 180), 5, { fill: a === 90 ? C.light : C.blue }), text(410 + 44 * Math.cos(a * Math.PI / 180), 66 + 44 * Math.sin(a * Math.PI / 180), n, { anchor: 'middle', size: 9.5 })]),
    arc(410, 62, 22, -80, 100, { stroke: C.muted, width: 1, arrow: 'end' }), note(180, 40, 'rotate both shafts together: 9, 12 and 3 o’clock minimum', { anchor: 'middle', size: 10 }),
    note(250, 190, 'enter dimensions: S to M, M to front foot, front to rear foot, rpm', { anchor: 'middle', size: 10.5 }),
    note(250, 208, 'result: offset and angle in both planes, shim and move values at each foot', { anchor: 'middle', size: 10 }),
    caption(500, 260, 'Soft foot first, coupling bolts loose, no sunlight on the detectors.'),
  ], { title: 'Laser alignment positions' }))

// ---------- Thermal growth ----------
fig('alignment/thermal-growth.svg', 'Thermal growth: set the cold alignment low on the machine that grows more, so it is in line when hot',
  svg(500, 250, [
    text(250, 22, 'ΔL = L × α × ΔT     (steel α = 6.5 × 10⁻⁶ in per in per °F)', { anchor: 'middle', weight: 700, size: 12 }),
    rect(40, 160, 460, 16, { fill: C.grey }),
    rect(80, 90, 120, 70, { fill: C.blueSoft, stroke: C.blue }), text(140, 125, 'motor\ncool', { anchor: 'middle', size: 11, vcenter: true }),
    rect(300, 70, 120, 90, { fill: C.redSoft, stroke: C.red }), text(360, 115, 'pump\nhot: 180°F', { anchor: 'middle', size: 11, vcenter: true }),
    line(200, 110, 300, 110, { stroke: C.blue, width: 2 }), line(200, 100, 300, 100, { stroke: C.red, width: 2, dash: '5 3' }),
    dim(240, 100, 240, 110, 'growth', { size: 10, side: -1 }),
    note(250, 200, 'example: 12 in base to shaft, ΔT = 110°F: 12 × 6.5e-6 × 110 = 0.0086 in', { anchor: 'middle', size: 10.5 }),
    note(250, 218, 'so set the pump shaft 0.009 in LOW cold (or the motor 0.009 in high)', { anchor: 'middle', size: 10.5, fill: C.red }),
    caption(500, 250, 'Use the maker’s numbers where given; verify with a hot alignment check.'),
  ], { title: 'Thermal growth' }))

// ---------- Tolerance chart ----------
{
  const ch = chart({ x: 70, y: 30, w: 400, h: 170, xmin: 0, xmax: 4000, ymin: 0, ymax: 8, xticks: [0, 1000, 1800, 3600], yticks: [0, 2, 4, 6, 8], xlabel: 'Shaft speed (rpm)', ylabel: 'Offset (mils)' })
  const ex = [[600, 5], [900, 3], [1200, 2.5], [1800, 2], [3600, 1], [4000, 0.9]], ac = [[600, 9], [900, 6], [1200, 4], [1800, 3], [3600, 1.5], [4000, 1.3]]
  const ln = (pts, c) => path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(Math.min(p[1], 8))).join(' '), { stroke: c, width: 2.5 })
  fig('alignment/alignment-tolerances.svg', 'Alignment tolerance by speed: the faster the shaft, the tighter the offset and angle allowed',
    svg(500, 290, [ch.el, ln(ac, C.accentDark), ln(ex, C.green), text(ch.sx(1500), ch.sy(3.6) - 6, 'acceptable', { size: 11, fill: C.accentDark, weight: 600 }), text(ch.sx(2200), ch.sy(1.6) + 14, 'excellent', { size: 11, fill: C.green, weight: 600 }),
      note(250, 250, 'angle: excellent 0.3-0.5 mil/in at 1,800 rpm; acceptable 0.7-1.0 mil/in', { anchor: 'middle', size: 10.5 }),
      caption(500, 290, '1 mil = 0.001 in. Aim for excellent on anything over 1,800 rpm.')], { title: 'Alignment tolerances' }))
}

// ---------- Micrometer reading ----------
fig('measurement/micrometer-reading.svg', 'Reading an inch micrometer: sleeve 0.300 + 0.025 line + thimble 0.008 = 0.333 in',
  svg(500, 240, [
    rect(40, 90, 300, 40, { fill: C.grey, rx: 4 }), rect(40, 110, 300, 1, { fill: C.ink }),
    ...Array.from({ length: 14 }, (_, i) => [line(60 + i * 20, 110, 60 + i * 20, i % 4 === 0 ? 96 : 102, { width: 1 }), i % 4 === 0 ? text(60 + i * 20, 90, String(i / 4), { anchor: 'middle', size: 10 }) : '']),
    rect(320, 70, 140, 80, { fill: C.steel, rx: 6 }), rect(320, 70, 8, 80, { fill: C.steelDark }),
    ...[5, 6, 7, 8, 9, 10, 11].map((v, i) => [line(330, 80 + i * 10, 344, 80 + i * 10, { width: 1 }), text(350, 84 + i * 10, String(v), { size: 10 })]),
    line(320, 110, 300, 110, { stroke: C.red, width: 1.5 }), circle(330, 110, 3, { fill: C.red, stroke: 'none' }),
    callout(1, 110, 140), callout(2, 305, 140), callout(3, 380, 160),
    legend(30, 175, ['sleeve: last number showing = 3 → 0.300', 'extra lines past it: one line = 0.025 → 0.325', 'thimble line at the index: 8 → 0.008; total 0.333 in'], { size: 11, gap: 16 }),
    caption(500, 240, 'Metric: sleeve mm and half-mm, thimble 0.01 mm. Zero-check on the standard.'),
  ], { title: 'Micrometer reading' }))
