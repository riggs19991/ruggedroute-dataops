import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, hatchRect, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- Pump curve ----------
{
  const ch = chart({ x: 60, y: 30, w: 400, h: 200, xmin: 0, xmax: 1000, ymin: 0, ymax: 200, xticks: [0, 250, 500, 750, 1000], yticks: [0, 50, 100, 150, 200], xlabel: 'Flow (gpm)', ylabel: 'Head (ft)' })
  const hq = Array.from({ length: 21 }, (_, i) => { const q = i * 50; return [q, 180 - 0.00012 * q * q] })
  const sys = Array.from({ length: 21 }, (_, i) => { const q = i * 50; return [q, 40 + 0.00016 * q * q] })
  const ln = (pts, c, d) => path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5, dash: d })
  fig('pumps-seals/pump-curve.svg', 'Pump curve and system curve: the pump runs where they cross; keep it near the best efficiency point',
    svg(500, 290, [ch.el, ln(hq, C.blue), ln(sys, C.accentDark, '6 4'), circle(ch.sx(707), ch.sy(120), 5, { fill: C.red, stroke: 'none' }), text(ch.sx(707) + 10, ch.sy(120) + 16, 'operating point', { size: 11, fill: C.red }),
      text(ch.sx(120), ch.sy(178) - 6, 'pump H-Q curve', { size: 11, fill: C.blue, weight: 600 }), text(ch.sx(560), ch.sy(70), 'system curve', { size: 11, fill: C.accentDark, weight: 600, anchor: 'middle' }),
      rect(ch.sx(600), ch.y, ch.sx(800) - ch.sx(600), ch.h, { fill: C.greenSoft, stroke: 'none', opacity: 0.5 }), text(ch.sx(700), ch.y + 14, 'BEP zone', { anchor: 'middle', size: 10, fill: C.green }),
      note(250, 275, 'left of BEP: recirculation, heat, shaft deflection · right: cavitation, high power', { anchor: 'middle', size: 10 })], { title: 'Pump curve' }))
}

// ---------- Mechanical seal parts ----------
fig('pumps-seals/mechanical-seal-parts.svg', 'Component mechanical seal: rotary face and springs on the shaft, stationary face in the gland; set the working length before locking the set screws',
  svg(500, 260, [
    rect(20, 118, 300, 24, { fill: C.steel }), rect(300, 60, 40, 140, { fill: C.grey }), rect(340, 80, 60, 100, { fill: C.steelDark }),
    rect(160, 92, 60, 76, { fill: C.grey, rx: 3 }), ...[0, 1, 2].map((i) => path(`M${170 + i * 16},96 l4,-6 l4,6 l4,-6 l4,6`, { stroke: C.ink, width: 1.2 })), rect(226, 92, 16, 76, { fill: '#333' }), rect(244, 88, 18, 84, { fill: '#ddd', stroke: C.ink }), rect(262, 70, 40, 120, { fill: C.grey }),
    circle(232, 100, 3, { fill: C.accentDark, stroke: 'none' }), circle(232, 160, 3, { fill: C.accentDark, stroke: 'none' }), circle(180, 100, 3, { fill: C.accentDark, stroke: 'none' }),
    callout(1, 190, 60), callout(2, 234, 60), callout(3, 253, 60), callout(4, 282, 50), callout(5, 232, 184),
    legend(20, 30, [], {}), legend(330, 30, [], {}),
    note(20, 205, '1 rotary unit: springs, drive collar, set screws (mark the working length first)', { size: 10 }),
    note(20, 220, '2 carbon rotating face · 3 hard stationary face (SiC, ceramic) · 4 gland, flush port', { size: 9.5 }),
    note(20, 235, '5 O-rings: material matched to the fluid; faces never touched by hand', { size: 9.5 }),
    caption(500, 260, 'Vent the seal chamber and fill with liquid before the pump turns.'),
  ], { title: 'Mechanical seal parts' }))

// ---------- Packing box ----------
fig('pumps-seals/packing-box.svg', 'Stuffing box: rings cut on a mandrel, joints staggered 90°, lantern ring under the flush port, gland adjusted to a controlled drip',
  svg(500, 250, [
    rect(20, 110, 380, 24, { fill: C.steel }), rect(120, 60, 200, 124, { fill: C.grey }), rect(120, 82, 200, 80, { fill: C.paper, stroke: 'none' }),
    ...[0, 1].map((i) => rect(130 + i * 22, 82, 20, 26, { fill: '#5b5b5b' })), rect(174, 82, 22, 26, { fill: C.brass, stroke: C.accentDark }), ...[0, 1, 2].map((i) => rect(198 + i * 22, 82, 20, 26, { fill: '#5b5b5b' })),
    ...[0, 1].map((i) => rect(130 + i * 22, 136, 20, 26, { fill: '#5b5b5b' })), rect(174, 136, 22, 26, { fill: C.brass, stroke: C.accentDark }), ...[0, 1, 2].map((i) => rect(198 + i * 22, 136, 20, 26, { fill: '#5b5b5b' })),
    rect(264, 70, 24, 104, { fill: C.steelDark }), rect(288, 100, 60, 8, { fill: C.ink }), rect(288, 138, 60, 8, { fill: C.ink }),
    rect(180, 40, 10, 42, { fill: C.blue }), note(185, 32, 'flush', { anchor: 'middle', size: 10 }),
    ...[0, 1, 2, 3, 4].map((i) => text(140 + i * 22 + (i > 1 ? 22 : 0), 100, ['1', '2', '3', '4', '5'][i], { anchor: 'middle', size: 9, fill: '#fff', weight: 700 })),
    note(250, 205, 'joints staggered 90°; lantern ring lines up with the flush port after compression', { anchor: 'middle', size: 9.5 }),
    note(250, 222, 'gland: finger tight, run, then 1/6 turn at a time until 10-60 drops per minute', { anchor: 'middle', size: 10 }),
  ], { title: 'Packing box' }))

// ---------- Impeller clearance ----------
fig('pumps-seals/impeller-clearance.svg', 'Open impeller: set the vane-to-casing clearance with the bearing housing jack screws (typical 0.015 in cold); enclosed impeller: wear ring clearance',
  svg(500, 240, [
    text(130, 22, 'Open impeller', { anchor: 'middle', weight: 700 }), rect(40, 60, 180, 120, { fill: C.grey }), rect(60, 60, 140, 100, { fill: C.paper, stroke: 'none' }),
    rect(110, 60, 24, 100, { fill: C.steel }), ...[0, 1, 2].map((i) => rect(134, 70 + i * 30, 50, 12, { fill: C.steel })), line(184, 60, 184, 160, { stroke: C.red, width: 1, dash: '3 2' }),
    dim(184, 165, 200, 165, 'clearance', { size: 10 }), note(130, 205, 'measure with a feeler at 3-4 places;\nadjust at the bearing housing, then re-align', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Enclosed impeller wear rings', { anchor: 'middle', weight: 700, size: 12 }), rect(280, 60, 180, 120, { fill: C.grey }), rect(300, 70, 140, 100, { fill: C.paper, stroke: 'none' }),
    circle(370, 120, 45, { fill: C.steel }), circle(370, 120, 55, { fill: 'none', stroke: C.accentDark, width: 5 }), circle(370, 120, 49, { fill: 'none', stroke: C.brass, width: 5 }),
    note(370, 205, 'diametral clearance ≈ 0.010 + 0.001 per inch of\nring dia.; replace at 2× new; casing ring and\nimpeller ring as a pair', { anchor: 'middle', size: 9.5 }),
  ], { title: 'Impeller clearance' }))

// ---------- Compressor types ----------
fig('pumps-seals/compressor-types.svg', 'Reciprocating and rotary screw compressors with the receiver and drain: the checks that matter',
  svg(500, 250, [
    text(110, 22, 'Reciprocating', { anchor: 'middle', weight: 700 }), rect(60, 60, 100, 70, { fill: C.grey }), rect(80, 40, 60, 20, { fill: C.steelDark }), circle(110, 150, 30, { fill: C.grey }), line(110, 150, 110, 100, { width: 4 }), rect(90, 90, 40, 14, { fill: C.steel }),
    note(110, 200, 'valves, rings, cooling fins,\ncrankcase oil, belts; 60% duty', { anchor: 'middle', size: 10 }),
    text(300, 22, 'Rotary screw', { anchor: 'middle', weight: 700 }), rect(240, 60, 120, 90, { fill: C.grey, rx: 8 }), ...[275, 325].map((x, i) => [circle(x, 105, 28, { fill: C.steel }), ...[0, 1, 2, 3, 4, 5].map((k) => line(x, 105, x + 28 * Math.cos((k * 60 + i * 30) * P), 105 + 28 * Math.sin((k * 60 + i * 30) * P), { width: 2, stroke: C.paper }))]),
    note(300, 200, 'oil, separator, air filter, cooler;\ndischarge temp 170-210°F; 100% duty', { anchor: 'middle', size: 10 }),
    rect(400, 50, 70, 130, { fill: C.steel, rx: 12 }), rect(430, 180, 10, 20, { fill: C.steelDark }), circle(435, 205, 6, { fill: C.blue }), note(435, 228, 'drain daily', { anchor: 'middle', size: 10 }), note(435, 30, 'receiver', { anchor: 'middle', size: 10 }), rect(455, 40, 8, 14, { fill: C.red }), note(450, 68, 'relief', { size: 9, anchor: 'end' }),
  ], { title: 'Compressor types' }))

// ---------- Accumulator precharge ----------
fig('hydraulics/accumulator-precharge.svg', 'Bladder accumulator: nitrogen only, precharge to 80-90% of the minimum system pressure, check with the system isolated and bled to zero',
  svg(500, 280, [
    rect(80, 40, 100, 180, { fill: C.steel, rx: 40 }), path('M130,60 q40,20 40,80 q0,60 -40,80 q-40,-20 -40,-80 q0,-60 40,-80 z', { fill: '#cfe8ff', stroke: C.blue }), rect(122, 20, 16, 22, { fill: C.steelDark }), rect(122, 218, 16, 22, { fill: C.steelDark }),
    text(130, 130, 'N2', { anchor: 'middle', size: 14, weight: 700, fill: C.blue }), note(130, 12, 'gas valve (charging kit)', { anchor: 'middle', size: 9.5 }), note(130, 252, 'oil port (to system)', { anchor: 'middle', size: 9.5 }),
    box(220, 40, 260, 44, 'NITROGEN ONLY: never air or oxygen\n(oil + oxygen = explosion)', { fill: C.redSoft, stroke: C.red, size: 11 }),
    note(220, 110, 'precharge p0 = 0.8-0.9 × minimum working pressure', { size: 9.5 }),
    note(220, 128, 'e.g. 1,500-2,500 psi system → p0 ≈ 1,200-1,350 psi', { size: 9.5 }),
    note(220, 158, 'check: isolate, bleed the oil side to 0 psi, fit\nthe charging assembly, open the gas valve, read', { size: 10 }),
    note(220, 198, 'lost precharge: bladder works hard and fails;\ntoo high: bladder hits the poppet, no volume', { size: 10 }),
    caption(500, 280, 'Bleed-down valve before any hydraulic work; accumulator = stored energy.'),
  ], { title: 'Accumulator precharge' }))

// ---------- Cylinder seals ----------
fig('hydraulics/cylinder-seal-orientation.svg', 'Cylinder seals: wiper lip out, rod seal lip toward the pressure, wear rings each side of the piston seal, piston seals face their own pressure side',
  svg(500, 240, [
    rect(40, 70, 400, 100, { fill: C.grey }), rect(60, 84, 360, 72, { fill: C.soft, stroke: 'none' }), rect(200, 110, 300, 20, { fill: C.steel }), rect(250, 84, 40, 72, { fill: C.steelDark }),
    rect(400, 84, 40, 72, { fill: C.grey }), rect(400, 100, 40, 40, { fill: C.paper, stroke: 'none' }),
    ...[[406, 'wiper', '#333', 1], [418, 'rod seal', C.blue, -1], [430, 'bearing', C.brass, 0]].map(([x, n, c, d]) => [rect(x, 100, 8, 10, { fill: c }), rect(x, 130, 8, 10, { fill: c }), d ? line(x + 4, 96, x + 4 + d * 6, 92, { stroke: c, width: 2, arrow: 'end' }) : '']),
    rect(256, 84, 6, 72, { fill: C.brass }), rect(278, 84, 6, 72, { fill: C.brass }), rect(266, 84, 8, 6, { fill: C.blue }), rect(266, 150, 8, 6, { fill: C.blue }),
    callout(1, 410, 60), callout(2, 422, 180), callout(3, 434, 60), callout(4, 259, 60), callout(5, 270, 180),
    note(20, 205, '1 wiper: lip OUT · 2 rod seal: lip IN toward the oil · 3 gland bearing / wear ring', { size: 9.5 }),
    note(20, 222, '4 piston wear rings both sides  ·  5 piston seal: T-seal or two U-cups back to back', { size: 10 }),
  ], { title: 'Cylinder seal orientation' }))

// ---------- ISO cleanliness ----------
{
  const rows = [['ISO 4406 code', 'Particles/mL >4 µm / >6 µm / >14 µm', 'Typical target'], ['22/20/17', '20,000-40,000 / 5,000-10,000 / 640-1,300', 'new oil from the drum (dirty!)'], ['20/18/15', '5,000-10,000 / 1,300-2,500 / 160-320', 'gear pumps, low pressure'], ['18/16/13', '1,300-2,500 / 320-640 / 40-80', 'general hydraulics, piston'], ['16/14/11', '320-640 / 80-160 / 10-20', 'servo and proportional valves'], ['14/12/9', '80-160 / 20-40 / 2.5-5', 'high-pressure servo systems']]
  fig('hydraulics/iso-4406-codes.svg', 'ISO 4406 cleanliness codes: each step up doubles the particle count; new oil is often dirtier than the system needs',
    svg(500, 230, [text(250, 22, 'ISO 4406 cleanliness code: three numbers = counts at 4, 6 and 14 µm', { anchor: 'middle', weight: 700, size: 11.5 }), table(20, 36, rows, [78, 236, 166], { rowH: 24, size: 9.5 }), caption(500, 230, 'Filter new oil going in; sample from a live line at mid-level, running.')], { title: 'ISO 4406 codes' }))
}

// ---------- Hydraulic fittings ----------
fig('hydraulics/fitting-types.svg', 'Hydraulic fitting families: JIC 37° flare, O-ring face seal, O-ring boss, NPT tapered pipe and BSPP; the seat, not the thread, identifies them',
  svg(500, 240, [
    ...[['JIC 37°', (x) => [poly([[x - 20, 60], [x + 20, 60], [x + 20, 100], [x + 8, 112], [x - 8, 112], [x - 20, 100]], { fill: C.steel }), line(x - 20, 100, x - 8, 112, { stroke: C.red, width: 2.5 }), line(x + 20, 100, x + 8, 112, { stroke: C.red, width: 2.5 })], 'cone seat,\nno sealant'],
      ['ORFS', (x) => [rect(x - 20, 60, 40, 50, { fill: C.steel }), rect(x - 16, 108, 32, 6, { fill: '#333', rx: 3 })], 'O-ring on a\nflat face'],
      ['ORB (SAE)', (x) => [rect(x - 14, 60, 28, 40, { fill: C.steel }), rect(x - 22, 100, 44, 8, { fill: C.steelDark }), rect(x - 20, 96, 40, 4, { fill: '#333' })], 'straight thread,\nO-ring at boss'],
      ['NPT', (x) => [poly([[x - 16, 60], [x + 16, 60], [x + 12, 112], [x - 12, 112]], { fill: C.steel }), ...[0, 1, 2, 3, 4].map((i) => line(x - 15 + i * 0.7, 66 + i * 10, x + 15 - i * 0.7, 66 + i * 10, { width: 1, stroke: C.steelDark }))], 'tapered thread,\nsealant, 2-3 turns'],
      ['BSPP', (x) => [rect(x - 14, 60, 28, 46, { fill: C.steel }), ...[0, 1, 2, 3].map((i) => line(x - 14, 68 + i * 10, x + 14, 68 + i * 10, { width: 1, stroke: C.steelDark })), rect(x - 20, 106, 40, 6, { fill: '#333' })], '55° straight,\nbonded washer']]
      .map(([n, d, t], i) => { const x = 60 + i * 95; return [text(x, 44, n, { anchor: 'middle', size: 11.5, weight: 600 }), ...d(x), note(x, 135, t, { anchor: 'middle', size: 9 })] }),
    caption(500, 240, 'Never mix JIC and 45° flare, NPT and BSPT: they thread on and leak.'),
    note(250, 195, 'Bend radius: hose min. per the layline; no twist (follow the layline); clamp long runs', { anchor: 'middle', size: 10 }),
  ], { title: 'Hydraulic fitting types' }))

// ---------- Hydraulic symbols ----------
fig('hydraulics/schematic-symbols.svg', 'ISO 1219 symbols: pump, motor, cylinder, relief valve, 4/3 directional valve, filter, tank',
  svg(500, 260, [
    ...[['Pump (fixed)', (x, y) => [circle(x, y, 22), poly([[x, y - 22], [x + 7, y - 10], [x - 7, y - 10]], { fill: C.ink }), line(x, y + 22, x, y + 40, { width: 1.5 })]],
      ['Motor', (x, y) => [circle(x, y, 22), poly([[x, y + 22], [x + 7, y + 10], [x - 7, y + 10]], { fill: C.ink })]],
      ['Cylinder', (x, y) => [rect(x - 30, y - 12, 60, 24), rect(x - 12, y - 12, 4, 24, { fill: C.ink }), line(x - 10, y, x + 45, y, { width: 3 })]],
      ['Relief valve', (x, y) => [rect(x - 14, y - 14, 28, 28), line(x - 14, y + 14, x + 14, y - 14, { width: 1.5, arrow: 'end' }), path(`M${x + 14},${y} l10,0 l0,-20 l-6,0 m6,0 l6,0`, { width: 1 }), path(`M${x - 14},${y} l-10,0 l0,-6 l-4,0 l8,-4 l-8,-4 l4,0`, { width: 1 })]],
      ['4/3 valve', (x, y) => [rect(x - 36, y - 12, 72, 24), line(x - 12, y - 12, x - 12, y + 12), line(x + 12, y - 12, x + 12, y + 12), line(x - 30, y + 8, x - 18, y - 8, { width: 1.2, arrow: 'end' }), line(x - 18, y + 8, x - 30, y - 8, { width: 1.2, arrow: 'end' }), line(x + 18, y - 8, x + 30, y + 8, { width: 1.2, arrow: 'end' }), line(x + 30, y - 8, x + 18, y + 8, { width: 1.2, arrow: 'end' }), line(x - 6, y - 8, x - 6, y + 8, { width: 1 }), line(x + 6, y - 8, x + 6, y + 8, { width: 1 })]],
      ['Filter', (x, y) => [poly([[x, y - 16], [x + 16, y], [x, y + 16], [x - 16, y]]), line(x - 12, y, x + 12, y, { dash: '2 2', width: 1 })]],
      ['Tank', (x, y) => [path(`M${x - 16},${y - 10} L${x - 16},${y + 10} L${x + 16},${y + 10} L${x + 16},${y - 10}`, { width: 1.5 })]]]
      .map(([n, d], i) => { const x = 60 + (i % 4) * 120, y = 60 + Math.floor(i / 4) * 110; return [...d(x, y), text(x, y + 60, n, { anchor: 'middle', size: 11 })] }),
    note(420, 170, 'solid line: pressure\ndashed: pilot / drain', { anchor: 'middle', size: 10 }),
    caption(500, 260, 'Read a schematic from the pump outward; arrows show flow direction.'),
  ], { title: 'Hydraulic symbols' }))

// ---------- FRL ----------
fig('hydraulics/frl-unit.svg', 'FRL in order of flow: filter, regulator, lubricator; drain the filter bowl, set the regulator under flow, 1 drop per minute at the lubricator sight',
  svg(500, 200, [
    line(20, 90, 480, 90, { width: 6, stroke: C.blue }), ...[[120, 'Filter', 'bowl drain daily\n5-40 µm element'], [250, 'Regulator', 'set with air flowing\n90 psi typical'], [380, 'Lubricator', 'oil: ISO VG 32\n1 drop/min per 20 cfm']].map(([x, n, d]) => [rect(x - 30, 60, 60, 30, { fill: C.grey, rx: 4 }), rect(x - 22, 90, 44, 50, { fill: n === 'Regulator' ? C.grey : '#dbeafe', stroke: C.ink, rx: 6 }), n === 'Regulator' ? circle(x, 52, 10, { fill: C.steelDark }) : '', text(x, 32, n, { anchor: 'middle', size: 11.5, weight: 600 }), note(x, 158, d, { anchor: 'middle', size: 10 })]),
    text(30, 82, 'air in', { size: 10 }), text(470, 82, 'to tool', { size: 10, anchor: 'end' }),
    caption(500, 200, 'Lubricator only where the tool wants oil: never for paint or instruments.'),
  ], { title: 'FRL unit' }))

// ---------- Grease compatibility matrix ----------
{
  const th = ['Li', 'LiX', 'Ca', 'CaS', 'Al X', 'PU', 'Clay', 'Na']
  const M = [
    ['Y', 'Y', 'Y', 'B', 'B', 'N', 'N', 'N'], ['Y', 'Y', 'B', 'Y', 'Y', 'B', 'N', 'N'], ['Y', 'B', 'Y', 'B', 'B', 'N', 'B', 'N'], ['B', 'Y', 'B', 'Y', 'B', 'Y', 'N', 'N'],
    ['B', 'Y', 'B', 'B', 'Y', 'N', 'N', 'N'], ['N', 'B', 'N', 'Y', 'N', 'Y', 'N', 'N'], ['N', 'N', 'B', 'N', 'N', 'N', 'Y', 'N'], ['N', 'N', 'N', 'N', 'N', 'N', 'N', 'Y']]
  const col = { Y: C.greenSoft, B: C.soft, N: C.redSoft }
  const cells = M.flatMap((row, i) => row.map((v, j) => [rect(110 + j * 42, 50 + i * 26, 42, 26, { fill: col[v], stroke: C.line }), text(131 + j * 42, 67 + i * 26, v, { anchor: 'middle', size: 11, weight: 600 })]))
  fig('lubrication/grease-compatibility-matrix.svg', 'Grease thickener compatibility: Y compatible, B borderline (test), N incompatible; when in doubt purge the old grease out',
    svg(500, 300, [...th.map((t, j) => text(131 + j * 42, 42, t, { anchor: 'middle', size: 10.5, weight: 600 })), ...th.map((t, i) => text(104, 67 + i * 26, t, { anchor: 'end', size: 10.5, weight: 600 })), cells,
      note(20, 268, 'Li lithium · LiX lithium complex · Ca calcium · CaS calcium sulphonate\nAl X aluminium complex · PU polyurea · Na sodium (clay = bentonite)', { size: 9 }),
      caption(500, 300, 'Charts differ by maker: confirm with the supplier for critical machines.')], { title: 'Grease compatibility matrix' }))
}

// ---------- Regrease quantity ----------
fig('lubrication/regrease-quantity.svg', 'Regrease quantity: G (grams) = 0.005 × D × B (mm) or 0.114 × D × B (inches, oz); D = bearing OD, B = width',
  svg(500, 220, [
    rect(60, 60, 80, 110, { fill: C.steel, rx: 6 }), rect(60, 95, 80, 40, { fill: C.paper, stroke: 'none' }), rect(60, 60, 80, 110, { fill: 'none' }), dim(150, 60, 150, 170, 'D (OD)', { size: 11 }), dim(60, 185, 140, 185, 'B (width)', { size: 11 }),
    text(215, 60, 'G = 0.005 × D × B  (grams, mm)', { size: 13, weight: 700 }), text(215, 84, 'G = 0.114 × D × B  (ounces, inches)', { size: 13, weight: 700 }),
    note(215, 115, 'example: 6310 (D = 110 mm, B = 27 mm)\nG = 0.005 × 110 × 27 = 15 g ≈ 10-12 gun strokes', { size: 10.5 }),
    note(215, 160, 'weigh 10 strokes of your gun once to learn\nthe grams per stroke; relief plug out on motors', { size: 10 }),
    caption(500, 220, 'Over-greasing kills more motor bearings than under-greasing.'),
  ], { title: 'Regrease quantity' }))

// ---------- Viscosity vs temperature ----------
{
  const ch = chart({ x: 60, y: 30, w: 400, h: 190, xmin: 40, xmax: 210, ymin: 0.5, ymax: 3.2, xticks: [40, 100, 150, 210], yticks: [1, 1.5, 2, 2.5, 3], xlabel: 'Oil temperature (°F)', ylabel: 'viscosity cSt (log)', yfmt: (v) => Math.round(10 ** v) })
  const lines = [[32, C.blue], [68, C.green], [150, C.accentDark], [320, C.red]].map(([vg, c]) => { const pts = [[40, Math.log10(vg * 2.8)], [104, Math.log10(vg)], [150, Math.log10(vg * 0.42)], [210, Math.log10(vg * 0.15)]]; return [path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5 }), text(ch.sx(42), ch.sy(Math.log10(vg * 2.8)) - 6, 'VG ' + vg, { size: 10, fill: c, weight: 600 })] })
  fig('lubrication/viscosity-vs-temperature.svg', 'Viscosity falls fast with temperature: an ISO VG 150 gear oil at 150°F is thinner than VG 68 at 100°F', svg(500, 280, [ch.el, lines, rect(ch.sx(100), ch.sy(1.3), ch.sx(210) - ch.sx(100), ch.sy(1.0) - ch.sy(1.3), { fill: C.redSoft, stroke: 'none', opacity: 0.6 }), text(ch.sx(160), ch.sy(1.12), 'below 10-13 cSt: film too thin', { anchor: 'middle', size: 10, fill: C.red }), caption(500, 280, 'Pick the grade for the running temperature, not the room temperature.')], { title: 'Viscosity vs temperature' }))
}

// ---------- Oil sampling point ----------
fig('lubrication/oil-sampling-point.svg', 'Take oil samples from a live zone at mid-level while running, not from the drain; same point, same way, every time',
  svg(500, 220, [
    rect(120, 50, 260, 130, { fill: C.grey, rx: 8 }), rect(130, 100, 240, 75, { fill: C.soft, stroke: 'none' }), circle(250, 110, 30, { fill: 'none', stroke: C.steelDark, width: 3, dash: '4 4' }),
    rect(140, 170, 20, 14, { fill: C.steelDark }), text(150, 200, 'drain: sludge and water', { anchor: 'middle', size: 10, fill: C.red }), line(150, 168, 150, 150, { stroke: C.red, width: 2 }),
    rect(330, 120, 40, 8, { fill: C.blue }), line(370, 124, 420, 124, { stroke: C.blue, width: 2 }), circle(432, 124, 8, { fill: C.paper, stroke: C.blue }), text(435, 150, 'sample valve:\nmid-level, live\nzone, flush first', { anchor: 'middle', size: 10, fill: C.blue }),
    note(250, 40, 'gearbox or reservoir', { anchor: 'middle', size: 10 }),
    caption(500, 220, 'Clean bottle, label with asset, hours, date; send the same day.'),
  ], { title: 'Oil sampling point' }))

// ---------- Lube route tags ----------
fig('lubrication/lube-point-tags.svg', 'Tag every lube point: colour and shape coded by lubricant, with quantity and interval, so the route sheet and the fitting agree',
  svg(500, 200, [
    ...[['red circle', 'lithium complex EP2', C.red], ['blue square', 'polyurea (motors)', C.blue], ['green triangle', 'ISO VG 220 gear oil', C.green], ['yellow diamond', 'food-grade H1', C.accent]].map(([s, n, c], i) => { const x = 70 + i * 115; const shp = i === 0 ? circle(x, 70, 18, { fill: c, stroke: 'none' }) : i === 1 ? rect(x - 16, 54, 32, 32, { fill: c, stroke: 'none' }) : i === 2 ? poly([[x, 52], [x + 18, 86], [x - 18, 86]], { fill: c, stroke: 'none' }) : poly([[x, 50], [x + 20, 70], [x, 90], [x - 20, 70]], { fill: c, stroke: 'none' }); return [shp, text(x, 112, s, { anchor: 'middle', size: 10.5, weight: 600 }), note(x, 128, n, { anchor: 'middle', size: 10 })] }),
    note(250, 160, 'tag reads: point ID · lubricant · quantity (g or strokes) · interval · last done', { anchor: 'middle', size: 10.5 }),
    caption(500, 200, 'Grease guns labelled to match; one gun per grease.'),
  ], { title: 'Lube point tags' }))
