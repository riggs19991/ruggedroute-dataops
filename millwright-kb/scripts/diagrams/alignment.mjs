import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'

function shaftPair(x, y, off, ang, labelL, labelR) {
  const out = [rect(x, y - 10, 90, 20, { fill: C.steel }), rect(x + 90, y - 26, 30, 52, { fill: C.grey })]
  out.push(g([rect(0, -26, 30, 52, { fill: C.grey }), rect(30, -10, 90, 20, { fill: C.steel })], { transform: `translate(${x + 126},${y + off}) rotate(${ang})` }))
  out.push(line(x, y, x + 120, y, { dash: '6 4', width: 1, stroke: C.blue })); out.push(g([line(0, 0, 150, 0, { dash: '6 4', width: 1, stroke: C.red })], { transform: `translate(${x + 126},${y + off}) rotate(${ang})` }))
  if (labelL) out.push(note(x + 45, y + 30, labelL, { anchor: 'middle', size: 10 }))
  if (labelR) out.push(note(x + 200, y + 30, labelR, { anchor: 'middle', size: 10 }))
  return out
}

// ---------- Offset and angularity ----------
fig('alignment/offset-and-angularity.svg', 'Parallel offset and angular misalignment, each in the vertical and horizontal plane: four numbers describe any misalignment',
  svg(500, 300, [
    text(130, 22, 'Parallel offset', { anchor: 'middle', weight: 700 }), ...shaftPair(20, 80, 14, 0, 'stationary', 'movable'), line(146, 80, 146, 94, { width: 1, arrow: 'both', stroke: C.red }), text(156, 108, 'offset', { size: 10, fill: C.red }),
    text(370, 22, 'Angular', { anchor: 'middle', weight: 700 }), ...shaftPair(260, 80, 0, -6, 'stationary', 'movable'), text(470, 62, 'angle', { size: 10, fill: C.red, anchor: 'end' }),
    text(250, 150, 'Two planes: side view (vertical) and top view (horizontal)', { anchor: 'middle', weight: 700, size: 12 }),
    box(30, 170, 210, 90, 'Vertical plane\n(side view)\ncorrected with shims\noffset + angle', { size: 11 }), box(260, 170, 210, 90, 'Horizontal plane\n(top view)\ncorrected with jack bolts\noffset + angle', { size: 11 }),
    caption(500, 300, 'Offset at the coupling centre; angle as gap difference across the face.'),
  ], { title: 'Offset and angularity' }))

// ---------- Rim and face setup ----------
fig('alignment/rim-and-face-setup.svg', 'Rim-and-face: bracket on the stationary hub; the rim indicator reads offset on the movable hub, the face indicator reads angle on its face; record A, B and C',
  svg(500, 318, [
    rect(20, 120, 100, 24, { fill: C.steel }), rect(120, 96, 45, 72, { fill: C.grey }), rect(215, 96, 45, 72, { fill: C.grey }), rect(260, 120, 220, 24, { fill: C.steel }),
    rect(290, 144, 20, 40, { fill: C.grey }), rect(410, 144, 20, 40, { fill: C.grey }), line(20, 184, 480, 184, { width: 2 }),
    text(70, 108, 'stationary', { size: 10, anchor: 'middle', fill: C.muted }), text(370, 108, 'movable', { size: 10, anchor: 'middle', fill: C.muted }), note(300, 200, 'front foot', { anchor: 'middle', size: 9.5 }), note(420, 200, 'rear foot', { anchor: 'middle', size: 9.5 }),
    rect(130, 82, 26, 14, { fill: C.ink }), path('M143,82 L143,40 L240,40 L240,66', { width: 3, stroke: C.ink }),
    circle(240, 76, 10, { fill: C.paper }), line(240, 86, 240, 96, { width: 1.5 }), text(258, 72, 'rim', { size: 10.5, weight: 600 }),
    path('M190,40 L190,66', { width: 3, stroke: C.ink }), circle(190, 76, 10, { fill: C.paper }), line(190, 86, 190, 104, { width: 1.5 }), line(190, 104, 213, 104, { width: 1.5 }), text(172, 72, 'face', { size: 10.5, weight: 600, anchor: 'end' }),
    dim(190, 222, 240, 222, 'A', { size: 11 }), dim(240, 242, 300, 242, 'B', { size: 11 }), dim(240, 262, 420, 262, 'C', { size: 11 }),
    note(250, 283, 'A: face to rim indicator · B: rim indicator to front foot · C: to rear foot', { anchor: 'middle', size: 10 }),
    caption(500, 318, 'Turn both shafts together; zero at 12; read 3, 6, 9; check 3 + 9 = 6.'),
  ], { title: 'Rim and face setup' }))

// ---------- Reverse dial ----------
fig('alignment/reverse-dial-setup.svg', 'Reverse dial: two brackets, each indicator reads the rim of the other shaft; plot both on a graph to the foot positions',
  svg(500, 300, [
    rect(20, 120, 130, 24, { fill: C.steel }), rect(150, 100, 40, 64, { fill: C.grey }), rect(200, 100, 40, 64, { fill: C.grey }), rect(240, 120, 240, 24, { fill: C.steel }),
    path('M130,72 L130,40 L215,40 L215,70', { width: 3, stroke: C.ink }), rect(124, 72, 12, 28, { fill: C.ink }), circle(215, 80, 11, { fill: C.paper }), line(215, 91, 215, 100, { width: 1.5 }),
    path('M260,190 L260,220 L175,220 L175,190', { width: 3, stroke: C.ink }), rect(254, 164, 12, 26, { fill: C.ink }), circle(175, 180, 11, { fill: C.paper }), line(175, 169, 175, 164, { width: 1.5 }),
    text(150, 62, 'indicator S reads M', { size: 10 }), text(120, 245, 'indicator M reads S', { size: 10 }),
    rect(300, 40, 180, 100, { fill: C.paper, stroke: C.line }), line(300, 90, 480, 90, { width: 1, stroke: C.muted }), line(320, 90, 460, 62, { stroke: C.red, width: 2 }), line(320, 90, 400, 90, { stroke: C.blue, width: 2 }),
    ...[320, 360, 400, 440].map((x, i) => [line(x, 86, x, 94, { width: 1 }), text(x, 106, ['S', 'M', 'front', 'rear'][i], { anchor: 'middle', size: 9 })]),
    note(390, 156, 'graph: plot the movable shaft line,\nread the shim at each foot', { anchor: 'middle', size: 9.5 }),
    note(390, 200, 'no face reading, no axial float error,\nfits tight couplings', { anchor: 'middle', size: 10 }),
    caption(500, 300, 'Sag-correct both indicators; readings at 3-9 give horizontal, 12-6 vertical.'),
  ], { title: 'Reverse dial setup' }))

// ---------- Laser ----------
fig('alignment/laser-alignment-positions.svg', 'Laser alignment: heads on both shafts, rotate together through at least 3 positions, then live-move with shims and jack bolts',
  svg(500, 260, [
    rect(20, 120, 130, 24, { fill: C.steel }), rect(150, 100, 40, 64, { fill: C.grey }), rect(200, 100, 40, 64, { fill: C.grey }), rect(240, 120, 240, 24, { fill: C.steel }),
    ...[[100, 'S'], [290, 'M']].map(([x, n]) => [rect(x - 10, 108, 20, 24, { fill: C.ink }), rect(x - 22, 60, 44, 44, { fill: C.blue, rx: 5 }), text(x, 88, n, { anchor: 'middle', size: 14, fill: '#fff', weight: 700 }), line(x, 104, x, 108, { width: 3 })]),
    line(122, 82, 268, 82, { stroke: C.red, width: 1.5, dash: '3 3' }), line(268, 78, 122, 78, { stroke: C.red, width: 1.5, dash: '3 3' }),
    circle(410, 62, 32, { fill: C.paper, stroke: C.line }), ...[[-90, '12'], [0, '3'], [90, '6'], [180, '9']].map(([a, n]) => [circle(410 + 32 * Math.cos(a * Math.PI / 180), 62 + 32 * Math.sin(a * Math.PI / 180), 5, { fill: a === 90 ? C.light : C.blue }), text(410 + 44 * Math.cos(a * Math.PI / 180), 66 + 44 * Math.sin(a * Math.PI / 180), n, { anchor: 'middle', size: 9.5 })]),
    arc(410, 62, 22, -80, 100, { stroke: C.muted, width: 1, arrow: 'end' }), note(250, 40, 'rotate both shafts together: 9, 12 and 3 o’clock minimum', { anchor: 'middle', size: 10 }),
    note(250, 190, 'enter dimensions: S to M, M to front foot, front to rear foot, rpm', { anchor: 'middle', size: 10.5 }),
    note(250, 208, 'result: offset and angle in both planes, shim and move values at each foot', { anchor: 'middle', size: 10 }),
    caption(500, 260, 'Soft foot first, coupling bolts loose, no sunlight on the detectors.'),
  ], { title: 'Laser alignment positions' }))

// ---------- Soft foot types ----------
fig('alignment/soft-foot-types.svg', 'Soft foot types: parallel (short leg), angular (bent foot), squishy (bad shims) and induced (pipe strain)',
  svg(500, 240, [
    ...[['Parallel', (x) => [rect(x - 30, 130, 60, 12, { fill: C.grey }), rect(x - 30, 100, 60, 20, { fill: C.steel }), line(x + 36, 120, x + 36, 130, { width: 1, arrow: 'both', stroke: C.red }), text(x + 42, 128, 'gap', { size: 9.5, fill: C.red })]],
      ['Angular', (x) => [rect(x - 30, 130, 60, 12, { fill: C.grey }), poly([[x - 30, 100], [x + 30, 100], [x + 30, 130], [x - 30, 120]], { fill: C.steel }), line(x - 36, 120, x - 36, 130, { width: 1, arrow: 'both', stroke: C.red }), text(x - 42, 128, 'gap', { size: 9.5, fill: C.red, anchor: 'end' })]],
      ['Squishy', (x) => [rect(x - 30, 130, 60, 12, { fill: C.grey }), rect(x - 30, 100, 60, 20, { fill: C.steel }), ...[0, 1, 2, 3, 4].map((i) => rect(x - 28 + (i % 2) * 4, 120 + i * 2, 50, 1.5, { fill: C.steelDark, stroke: 'none' }))]],
      ['Induced', (x) => [rect(x - 30, 130, 60, 12, { fill: C.grey }), rect(x - 30, 100, 60, 20, { fill: C.steel }), line(x + 30, 110, x + 70, 90, { stroke: C.red, width: 3, arrow: 'end' }), note(x + 10, 84, 'pipe pull', { size: 9 })]]]
      .map(([n, d], i) => { const x = 70 + i * 120; return [text(x, 40, n, { anchor: 'middle', weight: 700, size: 12 }), ...d(x), line(x, 60, x, 100, { width: 4, stroke: C.ink })] }),
    table(30, 165, [['Type', 'Fix']], [100, 340], { rowH: 20, size: 10.5 }).replace(/<[^>]+>/g, '') ,
    note(250, 175, 'parallel: shim the gap · angular: taper shim · squishy: clean, fewer thicker shims', { anchor: 'middle', size: 10 }),
    note(250, 192, 'induced: fix the pipe or base, the machine is being pulled, not resting', { anchor: 'middle', size: 10 }),
    caption(500, 240, 'Check one bolt at a time with an indicator on the foot; over 0.002 in = soft.'),
  ], { title: 'Soft foot types' }))

// ---------- Thermal growth ----------
fig('alignment/thermal-growth.svg', 'Thermal growth: set the cold alignment low on the machine that grows more, so it is in line when hot',
  svg(500, 250, [
    text(250, 22, 'ΔL = L × α × ΔT     (steel α = 6.5 × 10⁻⁶ in per in per °F)', { anchor: 'middle', weight: 700, size: 12 }),
    rect(40, 160, 460, 16, { fill: C.grey }),
    rect(80, 90, 120, 70, { fill: C.blueSoft, stroke: C.blue }), text(140, 125, 'motor\ncool', { anchor: 'middle', size: 11, vcenter: true }),
    rect(300, 70, 120, 90, { fill: C.redSoft, stroke: C.red }), text(360, 115, 'pump\nhot: 180°F', { anchor: 'middle', size: 11, vcenter: true }),
    line(200, 110, 300, 110, { stroke: C.blue, width: 2 }), line(200, 100, 300, 100, { stroke: C.red, width: 2, dash: '5 3' }),
    dim(260, 100, 260, 110, 'growth', { size: 10 }),
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

// ---------- Dial indicator runout ----------
fig('measurement/dial-indicator-runout.svg', 'Runout: indicator square to the shaft, rotate one full turn, TIR = highest minus lowest; keep test indicators near parallel to the surface',
  svg(500, 250, [
    text(130, 22, 'Shaft runout (TIR)', { anchor: 'middle', weight: 700 }), rect(30, 120, 200, 30, { fill: C.steel }), circle(130, 60, 24, { fill: C.paper }), line(130, 84, 130, 120, { width: 2 }), line(130, 60, 140, 46, { width: 1.5 }),
    rect(60, 40, 12, 80, { fill: C.grey }), path('M72,50 L118,50', { width: 3, stroke: C.ink }), arc(130, 135, 40, 200, 340, { stroke: C.blue, width: 1, arrow: 'end' }),
    note(130, 175, 'zero at the high spot, turn 360°;\nTIR = total needle travel', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Cosine error (test indicator)', { anchor: 'middle', weight: 700 }), rect(290, 120, 180, 20, { fill: C.steel }),
    ...[[320, 0, '0°: reads true'], [400, 30, '30°: ×0.87']].map(([x, a, l]) => [g([line(0, 0, 40, 0, { width: 3 }), circle(40, 0, 3, { fill: C.red })], { transform: `translate(${x},${118}) rotate(${-a})` }), note(x + 20, 160, l, { anchor: 'middle', size: 10 })]),
    note(380, 190, 'over 15° tilt, multiply by cos(angle),\nor keep the lever nearly parallel', { anchor: 'middle', size: 10 }),
    caption(500, 250, 'Rigid mount, no overhang, plunger square, read the same graduation each turn.'),
  ], { title: 'Dial indicator runout' }))

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
