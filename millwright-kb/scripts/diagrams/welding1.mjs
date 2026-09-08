import { svg, text, line, rect, circle, path, poly, g, dim, leader, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'

// ---------- Polarity ----------
function machine(x, y) {
  return [rect(x, y, 100, 64, { rx: 6, fill: C.grey }), text(x + 50, y + 28, 'Welding\nmachine', { anchor: 'middle', weight: 600, size: 12, vcenter: true }),
    circle(x + 28, y + 52, 6, { fill: C.red }), text(x + 28, y + 56, '+', { anchor: 'middle', size: 11, fill: '#fff', weight: 700 }),
    circle(x + 72, y + 52, 6, { fill: C.ink }), text(x + 72, y + 56, '−', { anchor: 'middle', size: 11, fill: '#fff', weight: 700 })]
}
function polarityPanel(x, y, title, elecPos, note1, note2) {
  const ex = x + 170, wy = y + 118
  return [text(x + 110, y - 8, title, { anchor: 'middle', weight: 700, size: 14 }), ...machine(x, y),
    plate(x + 110, wy, 100, 14), text(x + 160, wy + 28, 'work', { anchor: 'middle', size: 12 }),
    line(ex, y + 46, ex, wy - 8, { width: 3 }), rect(ex - 8, y + 30, 16, 22, { fill: C.ink, rx: 3 }), text(ex, y + 20, 'electrode', { size: 11, anchor: 'middle' }),
    path(`M${x + (elecPos ? 28 : 72)},${y + 58} C${x + (elecPos ? 28 : 72)},${y + 95} ${ex},${y + 5} ${ex},${y + 30}`, { stroke: elecPos ? C.red : C.ink, width: 2.5 }),
    path(`M${x + (elecPos ? 72 : 28)},${y + 58} C${x + (elecPos ? 72 : 28)},${wy + 20} ${x + 110},${wy + 30} ${x + 114},${wy + 14}`, { stroke: elecPos ? C.ink : C.red, width: 2.5 }),
    note(x + 110, wy + 46, note1, { anchor: 'middle' }), note(x + 110, wy + 60, note2, { anchor: 'middle' })]
}
fig('welding/polarity.svg', 'DCEP, DCEN and AC: which terminal the electrode lead goes to and where the heat goes',
  svg(500, 400, [
    ...polarityPanel(20, 40, 'DCEP (reverse polarity)', true, 'electrode +, work −', 'about 2/3 of the heat at the electrode'),
    ...polarityPanel(260, 40, 'DCEN (straight polarity)', false, 'electrode −, work +', 'about 2/3 of the heat in the work'),
    table(20, 240, [['Process', 'Polarity'], ['Stick 7018 / 6010, MIG, gas-shielded flux-core', 'DCEP'], ['TIG on steel, stainless, copper, titanium', 'DCEN'], ['Self-shielded flux-core (E71T-11, T-8)', 'DCEN'], ['TIG aluminium; stick when arc blow is bad', 'AC']], [330, 130], { rowH: 22, size: 11.5 }),
    caption(500, 400, 'Wrong polarity is the first check on a spattery, porous weld.'),
  ], { title: 'Welding polarity' }))

// ---------- Stick angles ----------
fig('welding/smaw-angles.svg', 'Stick welding: arc length about the rod diameter, 10-15° drag travel angle, 45° work angle in a fillet',
  svg(500, 300, [
    text(130, 24, 'Side view: travel angle', { anchor: 'middle', weight: 700 }),
    plate(20, 200, 220, 16), note(130, 232, 'travel direction →', { anchor: 'middle', size: 12 }),
    g([rect(-4, -120, 8, 120, { fill: C.grey }), rect(-6, -40, 12, 40, { fill: C.ink, rx: 2 })], { transform: 'translate(150,196) rotate(15)' }),
    line(150, 196, 150, 90, { dash: '4 3', width: 1, stroke: C.muted }), angle(150, 196, 60, -90, -75, '10-15° drag'),
    circle(150, 196, 5, { fill: C.accent, stroke: C.accentDark }), path('M120,200 Q135,186 150,196', { stroke: C.weld, width: 4 }),
    line(150, 190, 150, 200, { width: 1, arrow: 'both', stroke: C.blue }), note(60, 176, 'arc length ≈ rod diameter', { fill: C.blue }),
    text(370, 24, 'End view: work angle (fillet)', { anchor: 'middle', weight: 700 }),
    plate(280, 200, 200, 16), plate(370, 90, 16, 110),
    g([rect(-4, -110, 8, 110, { fill: C.grey }), rect(-6, -40, 12, 40, { fill: C.ink, rx: 2 })], { transform: 'translate(378,192) rotate(45)' }),
    line(378, 192, 378, 100, { dash: '4 3', width: 1, stroke: C.muted }), line(378, 192, 470, 192, { dash: '4 3', width: 1, stroke: C.muted }),
    angle(378, 192, 50, -90, -45, '45°'), path('M370,200 L386,200 L386,184 Z', { fill: C.weld, stroke: C.accentDark }),
    caption(500, 300, 'Tight arc, drag the rod, split the fillet angle. Long arc = spatter.'),
  ], { title: 'Stick welding angles' }))

// ---------- Stick amperage chart ----------
{
  const rods = [['E6010', [[3, 40, 80], [4, 75, 130], [5, 90, 175], [6, 140, 225]]], ['E6013', [[3, 40, 90], [4, 80, 130], [5, 105, 180], [6, 150, 230]]], ['E7014', [[3, 80, 125], [4, 110, 160], [5, 150, 210], [6, 200, 275]]], ['E7018', [[3, 70, 100], [4, 90, 150], [5, 120, 200], [6, 200, 275]]], ['E7024', [[4, 140, 190], [5, 180, 250], [6, 230, 305]]], ['E308L', [[3, 50, 80], [4, 75, 110], [5, 100, 150]]]]
  const ch = chart({ x: 90, y: 30, w: 380, h: 330, xmin: 0, xmax: 320, ymin: 0, ymax: 1, xticks: [0, 50, 100, 150, 200, 250, 300], xlabel: 'Amperage (DCEP or AC per rod)', grid: true })
  const rows = []; let i = 0
  const dia = { 3: '3/32', 4: '1/8', 5: '5/32', 6: '3/16' }; const col = { 3: C.steelDark, 4: C.blue, 5: C.accent, 6: C.red }
  for (const [name, sizes] of rods) {
    rows.push(text(84, 30 + i * 12 + 22, name, { anchor: 'end', size: 12, weight: 600 }))
    for (const [d, lo, hi] of sizes) { const y = 30 + i * 12 + 6; rows.push(rect(ch.sx(lo), y, ch.sx(hi) - ch.sx(lo), 9, { fill: col[d], stroke: 'none', rx: 2 })); rows.push(text(ch.sx(hi) + 4, y + 8, dia[d], { size: 9, fill: C.muted })); i++ }
    i += 0.6
  }
  const lg = [3, 4, 5, 6].map((d, k) => [rect(110 + k * 90, 402, 12, 9, { fill: col[d], stroke: 'none' }), text(126 + k * 90, 410, dia[d] + ' in rod', { size: 11 })])
  fig('welding/smaw-amperage-chart.svg', 'Stick electrode amperage ranges by rod diameter (bars show the usable range; start in the middle)', svg(500, 420, [ch.el, rows, lg], { title: 'Stick electrode amperage chart' }))
}

// ---------- AWS decoder ----------
fig('welding/aws-electrode-decoder.svg', 'Decoding E7018-1 H4R',
  svg(500, 260, [
    text(250, 50, 'E 70 1 8 - 1  H4 R', { anchor: 'middle', size: 34, weight: 700, family: 'ui-monospace, Menlo, Consolas, monospace' }),
    ...[118, 163, 214, 246, 300, 356, 402].map((x, i) => [line(x, 58, x, 72, { width: 1, stroke: C.blue }), callout(i + 1, x, 82)]),
    legend(30, 110, ['E = electrode (stick); ER = wire or rod', '70 = tensile strength × 1,000 psi (70 ksi)', '1 = position: 1 all, 2 flat and horizontal, 4 vertical-down', '8 = coating and current: low-hydrogen iron powder, AC or DCEP', '-1 = improved impact toughness (optional)', 'H4 = diffusible hydrogen ≤ 4 mL per 100 g', 'R = moisture-resistant coating'], { size: 11.5, gap: 18 }),
    caption(500, 260, 'Wires read the same way: ER70S-6 = rod, 70 ksi, solid, chemistry 6.'),
  ], { title: 'AWS electrode classification' }))

// ---------- MIG stickout ----------
fig('welding/mig-stickout.svg', 'MIG gun: CTWD, stickout and push angle',
  svg(500, 330, [
    plate(30, 200, 300, 16), note(180, 232, 'travel direction →', { anchor: 'middle', size: 12 }),
    g([rect(-26, -170, 52, 120, { fill: C.grey, rx: 8 }), rect(-20, -60, 40, 50, { fill: C.copper, stroke: C.accentDark, rx: 4 }), rect(-5, -70, 10, 40, { fill: C.brass, stroke: C.accentDark }), line(0, -30, 0, 0, { stroke: C.ink, width: 2.5 })], { transform: 'translate(200,196) rotate(-12)' }),
    line(200, 196, 200, 40, { dash: '4 3', width: 1, stroke: C.muted }), arc(200, 196, 150, -90, -102, { stroke: C.blue, width: 1 }), text(150, 40, '10-15° push', { size: 12, fill: C.blue, anchor: 'end' }),
    circle(200, 196, 6, { fill: C.accent, stroke: C.accentDark }), path('M162,202 Q182,184 200,196', { stroke: C.weld, width: 5 }),
    dim(300, 196, 300, 148, 'CTWD', { off: 0, size: 12 }),
    callout(1, 232, 128), callout(2, 226, 160), callout(3, 212, 178), callout(4, 175, 60),
    legend(335, 40, ['nozzle: 1/2-5/8 in ID,\nkeep spatter out', 'contact tip sized to the\nwire; recessed 1/8 in\nfor spray, flush for\nshort-circuit', 'stickout (wire past tip)\n3/8-1/2 in short-circuit\n3/4-1 in spray or FCAW', 'gun body and liner'], { gap: 44, size: 10.5 }),
    note(180, 275, 'CTWD = contact tip to work distance.\nLonger = less current, more spatter; shorter = hotter.', { anchor: 'middle', size: 10.5 }),
    caption(500, 330, 'Push 10-15° on steel short-circuit and spray; drag on flux-core.'),
  ], { title: 'MIG stickout and gun angle' }))

// ---------- Transfer modes ----------
{
  const modes = [['Short-circuit', 'wire touches the puddle\n20-100 times per second', '16-22 V', 'thin, all positions', (x, y) => [line(x, y - 60, x, y + 4, { width: 4, stroke: C.steelDark }), path(`M${x - 22},${y + 8} Q${x},${y - 6} ${x + 22},${y + 8}`, { stroke: C.weld, width: 5 })]],
    ['Globular', 'big drops fall by\ngravity, spatter', '22-26 V (CO2)', 'flat only, avoid', (x, y) => [line(x, y - 60, x, y - 30, { width: 4, stroke: C.steelDark }), circle(x, y - 20, 9, { fill: C.accent, stroke: C.accentDark }), circle(x + 12, y - 4, 4, { fill: C.accent, stroke: C.accentDark }), path(`M${x - 22},${y + 8} Q${x},${y - 4} ${x + 22},${y + 8}`, { stroke: C.weld, width: 5 })]],
    ['Spray', 'fine droplets in a\ncone, no contact', '24-32 V, ≥ 80% Ar', 'flat/horizontal, thick', (x, y) => [line(x, y - 60, x, y - 36, { width: 4, stroke: C.steelDark }), poly([[x - 3, y - 36], [x + 3, y - 36], [x + 16, y], [x - 16, y]], { fill: C.soft, stroke: C.accent }), ...[0, 1, 2, 3, 4].map((i) => circle(x - 6 + (i * 7) % 14, y - 30 + i * 7, 1.8, { fill: C.accentDark, stroke: 'none' })), path(`M${x - 24},${y + 8} Q${x},${y - 2} ${x + 24},${y + 8}`, { stroke: C.weld, width: 5 })]],
    ['Pulsed spray', 'one drop per pulse,\nlower average heat', 'pulse program', 'all positions', (x, y) => [line(x, y - 60, x, y - 36, { width: 4, stroke: C.steelDark }), circle(x, y - 22, 4, { fill: C.accentDark, stroke: 'none' }), path(`M${x - 24},${y + 8} Q${x},${y - 2} ${x + 24},${y + 8}`, { stroke: C.weld, width: 5 }), path(`M${x - 22},${y + 30} l6,0 l0,-12 l6,0 l0,12 l8,0 l0,-12 l6,0 l0,12 l8,0`, { stroke: C.blue, width: 1.5 })]]]
  const el = modes.map(([n, d, v, u, draw], i) => { const x = 70 + i * 120, y = 110; return [text(x, 24, n, { anchor: 'middle', weight: 700, size: 12.5 }), plate(x - 40, y + 8, 80, 10), ...draw(x, y), note(x, y + 50, d, { anchor: 'middle', size: 10.5 }), text(x, y + 88, v, { anchor: 'middle', size: 11, weight: 600 }), text(x, y + 104, u, { anchor: 'middle', size: 11 })] })
  const ch = chart({ x: 70, y: 255, w: 400, h: 70, xmin: 0, xmax: 400, ymin: 0, ymax: 1, xticks: [0, 100, 200, 300, 400], xlabel: 'Amperage (.035 wire, 90/10 Ar-CO2)', grid: false })
  const bands = [[40, 160, 'short-circuit', C.blueSoft], [160, 215, 'globular', C.redSoft], [215, 400, 'spray', C.soft]].map(([a, b, n, c]) => [rect(ch.sx(a), 258, ch.sx(b) - ch.sx(a), 64, { fill: c, stroke: 'none' }), text((ch.sx(a) + ch.sx(b)) / 2, 294, n, { anchor: 'middle', size: 11 })])
  const tr = [line(ch.sx(165), 258, ch.sx(165), 322, { stroke: C.red, width: 1.5, dash: '4 3' }), note(250, 245, 'transition to spray ≈ 165-170 A for .035, ≈ 220 A for .045 (needs ≥ 80% argon)', { anchor: 'middle', size: 10.5, fill: C.red })]
  fig('welding/mig-transfer-modes.svg', 'MIG transfer modes and the transition current', svg(500, 365, [el, ch.el, bands, tr], { title: 'MIG transfer modes' }))
}

// ---------- Flux-core ----------
fig('welding/fcaw-drag-stickout.svg', 'Flux-core: drag angle and stickout',
  svg(500, 300, [
    plate(30, 230, 260, 16), note(160, 262, 'travel direction →', { anchor: 'middle', size: 12 }),
    g([rect(-24, -160, 48, 110, { fill: C.grey, rx: 8 }), rect(-18, -60, 36, 44, { fill: C.copper, stroke: C.accentDark, rx: 4 }), rect(-5, -70, 10, 36, { fill: C.brass, stroke: C.accentDark }), line(0, -34, 0, 0, { stroke: C.ink, width: 2.5 })], { transform: 'translate(190,226) rotate(15)' }),
    line(190, 226, 190, 70, { dash: '4 3', width: 1, stroke: C.muted }), angle(190, 226, 90, -90, -75, '10-20° drag'),
    circle(190, 226, 6, { fill: C.accent, stroke: C.accentDark }), path('M140,234 Q165,214 190,226', { stroke: C.weld, width: 6 }), rect(140, 224, 40, 6, { fill: C.steelDark, stroke: 'none' }), note(120, 218, 'slag', { anchor: 'end' }),
    dim(250, 226, 250, 192, 'stickout', { size: 12 }),
    table(310, 40, [['Wire', 'Stickout', 'Pol.'], ['E71T-1 gas', '3/4-1 in', 'DCEP'], ['E71T-11', '1/2-3/4 in', 'DCEN'], ['E71T-8', '3/4-1 in', 'DCEN']], [70, 68, 42], { rowH: 22, size: 11 }),
    note(400, 150, '"Drag if slag":\nthe arc rides the\nleading edge of\nthe puddle, slag\nfollows behind', { anchor: 'middle' }),
    caption(500, 300, 'Short stickout on self-shielded wire = porosity: the wire must preheat.'),
  ], { title: 'Flux-core gun angle and stickout' }))

// ---------- TIG torch setup ----------
fig('welding/tig-torch-setup.svg', 'TIG torch, tungsten and filler setup',
  svg(500, 360, [
    text(110, 24, 'Tungsten grind (DC)', { anchor: 'middle', weight: 700 }),
    poly([[30, 50], [150, 50], [150, 66], [30, 66]], { fill: C.grey }), poly([[150, 50], [200, 57], [200, 59], [150, 66]], { fill: C.steelDark }),
    dim(150, 74, 200, 74, '2-2.5 × d', { size: 11 }), dim(24, 50, 24, 66, 'd', { size: 11, side: -1 }),
    ...[0, 1, 2, 3, 4].map((i) => line(152 + i * 10, 52 + i * 1.5, 190, 55.5 + i * 0.5, { stroke: C.paper, width: 0.6 })),
    note(20, 100, 'grind marks lengthwise, tiny flat on the tip;\nAC inverter: same or truncated; transformer: ball'),
    text(360, 24, 'Torch and filler', { anchor: 'middle', weight: 700 }),
    plate(230, 250, 250, 16), note(355, 282, 'travel direction ←', { anchor: 'middle', size: 12 }),
    g([rect(-22, -190, 44, 120, { fill: C.grey, rx: 8 }), poly([[-16, -70], [16, -70], [13, -14], [-13, -14]], { fill: '#f5d0a9', stroke: C.accentDark }), line(0, -70, 0, 0, { stroke: C.steelDark, width: 3 })], { transform: 'translate(380,246) rotate(12)' }),
    line(380, 246, 380, 110, { dash: '4 3', width: 1, stroke: C.muted }), angle(380, 246, 90, -90, -78, '10-15°'),
    g([line(0, 0, 130, 0, { stroke: C.copper, width: 3 })], { transform: 'translate(372,242) rotate(-17)' }),
    line(372, 242, 240, 242, { dash: '4 3', width: 1, stroke: C.muted }), arc(372, 242, 60, 180, 163, { stroke: C.blue, width: 1 }), text(296, 228, '15-20°', { size: 12, fill: C.blue, anchor: 'end' }),
    circle(380, 246, 6, { fill: C.accent, stroke: C.accentDark }), path('M380,246 Q405,230 430,248', { stroke: C.weld, width: 5 }),
    callout(1, 395, 215), callout(2, 383, 190), callout(3, 300, 218), callout(4, 366, 110),
    legend(20, 140, ['stickout ≈ cup diameter (2× with a gas lens)', 'arc length ≈ tungsten diameter', 'filler into the front edge of the puddle', 'ceramic cup #6-#8, gas lens for stainless'], { size: 11 }),
    caption(500, 360, 'Never touch the tungsten to the puddle or rod: regrind if you do.'),
  ], { title: 'TIG torch setup' }))

// ---------- TIG amps ----------
{
  const ch = chart({ x: 60, y: 30, w: 400, h: 230, xmin: 0, xmax: 0.5, ymin: 0, ymax: 450, xticks: [0, 0.125, 0.25, 0.375, 0.5], yticks: [0, 100, 200, 300, 400], xfmt: (v) => v === 0 ? '0' : ({ 0.125: '1/8', 0.25: '1/4', 0.375: '3/8', 0.5: '1/2' }[v]), xlabel: 'Thickness (in)', ylabel: 'Amps (max set)' })
  const series = [['Aluminium (AC)', [[0.05, 60], [0.093, 105], [0.125, 130], [0.188, 180], [0.25, 245], [0.375, 340], [0.5, 400]], C.blue], ['Mild steel (DCEN)', [[0.03, 32], [0.06, 70], [0.093, 100], [0.125, 125], [0.188, 160], [0.25, 225], [0.375, 290], [0.5, 350]], C.accentDark], ['Stainless (DCEN)', [[0.03, 25], [0.06, 55], [0.093, 80], [0.125, 105], [0.188, 145], [0.25, 205], [0.375, 260]], C.green]]
  const el = series.map(([n, pts, c], i) => [path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5 }), rect(70, 300 + i * 16, 14, 4, { fill: c, stroke: 'none' }), text(90, 306 + i * 16, n, { size: 11 })])
  const rule = note(250, 306, 'Rule: 1 A per 0.001 in of steel;\naluminium +20-30%; stainless −10-20%')
  fig('welding/tig-amps-vs-thickness.svg', 'TIG amperage versus thickness', svg(500, 350, [ch.el, el, rule], { title: 'TIG amps by thickness' }))
}

// ---------- Flowmeter ----------
fig('welding/flowmeter-reading.svg', 'Flowmeter versus regulator gauge',
  svg(500, 260, [
    text(120, 24, 'Flowmeter (cfh)', { anchor: 'middle', weight: 700 }), rect(90, 40, 60, 170, { fill: C.grey, rx: 6 }), rect(105, 50, 30, 150, { fill: C.paper }),
    ...[0, 10, 20, 30, 40, 50, 60].map((v, i) => [line(135, 195 - i * 24, 145, 195 - i * 24, { width: 1 }), text(150, 199 - i * 24, String(v), { size: 10 })]),
    circle(120, 195 - 2.2 * 24, 8, { fill: C.steelDark }), line(60, 195 - 2.2 * 24, 112, 195 - 2.2 * 24, { stroke: C.red, width: 1, dash: '3 2' }), text(58, 199 - 2.2 * 24, 'read here\n= 22 cfh', { anchor: 'end', size: 11, fill: C.red }),
    note(120, 232, 'gas must be flowing (trigger or purge)', { anchor: 'middle', size: 10.5 }),
    text(360, 24, 'Regulator (psi): not a flow reading', { anchor: 'middle', weight: 700 }), circle(360, 120, 60, { fill: C.grey }), circle(360, 120, 50, { fill: C.paper }),
    ...[-140, -100, -60, -20, 20, 60].map((a, i) => [line(360 + 44 * Math.cos(a * Math.PI / 180), 120 + 44 * Math.sin(a * Math.PI / 180), 360 + 50 * Math.cos(a * Math.PI / 180), 120 + 50 * Math.sin(a * Math.PI / 180), { width: 1 }), text(360 + 36 * Math.cos(a * Math.PI / 180), 124 + 36 * Math.sin(a * Math.PI / 180), String(i * 10), { anchor: 'middle', size: 9 })]),
    line(360, 120, 360 + 40 * Math.cos(-60 * Math.PI / 180), 120 + 40 * Math.sin(-60 * Math.PI / 180), { stroke: C.red, width: 2 }), circle(360, 120, 4, { fill: C.ink }),
    note(360, 200, 'a "flow gauge" regulator is calibrated in\ncfh for one orifice: fine for MIG;\nuse a flowmeter for TIG', { anchor: 'middle', size: 10.5 }),
    caption(500, 260, 'MIG 20-25 cfh · flux-core 35-50 · TIG 10-20 (15-25 with a gas lens)'),
  ], { title: 'Flowmeter reading' }))

// ---------- Duty cycle ----------
{
  const ch = chart({ x: 70, y: 30, w: 380, h: 200, xmin: 100, xmax: 350, ymin: 0, ymax: 100, xticks: [100, 150, 200, 250, 300, 350], yticks: [0, 20, 40, 60, 80, 100], xlabel: 'Output amps', ylabel: 'Duty cycle %', yfmt: (v) => v + '%' })
  const pts = []; for (let a = 100; a <= 350; a += 5) pts.push([a, Math.min(100, 40 * (250 / a) ** 2)])
  const curve = path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: C.blue, width: 2.5 })
  const mk = [[250, 40, 'rated: 250 A at 40%', 'start'], [160, 98, '160 A: continuous', 'start'], [300, 28, '300 A: 28% = 2.8 min in 10', 'end']].map(([a, d, l, an]) => [circle(ch.sx(a), ch.sy(d), 4, { fill: C.red, stroke: 'none' }), text(ch.sx(a) + (an === 'end' ? -8 : 8), ch.sy(d) - 8, l, { size: 11, anchor: an })])
  fig('welding/duty-cycle.svg', 'Duty cycle curve for a 250 A at 40% machine', svg(500, 290, [ch.el, curve, mk, note(250, 275, 'duty at I ≈ rated duty × (I rated ÷ I)²', { anchor: 'middle', size: 12 })], { title: 'Duty cycle curve' }))
}

// ---------- Ground clamp ----------
fig('welding/ground-clamp-placement.svg', 'Ground clamp placement',
  svg(500, 290, [
    text(125, 24, 'Right', { anchor: 'middle', weight: 700, fill: C.green, size: 15 }), text(375, 24, 'Wrong', { anchor: 'middle', weight: 700, fill: C.red, size: 15 }),
    ...[0, 250].map((ox) => [rect(ox + 40, 150, 170, 40, { fill: C.grey }), circle(ox + 90, 170, 22, { fill: C.paper }), circle(ox + 90, 170, 12, { fill: C.steel }), note(ox + 90, 208, 'bearing', { anchor: 'middle' }), rect(ox + 140, 100, 12, 70, { fill: C.steel }), circle(ox + 146, 104, 5, { fill: C.accent, stroke: C.accentDark }), note(ox + 160, 96, 'weld')]),
    rect(160, 118, 22, 12, { fill: C.copper, stroke: C.accentDark }), path('M182,124 C215,124 215,60 240,60', { stroke: C.ink, width: 2.5 }), note(215, 52, 'to machine'),
    path('M164,116 L148,108', { stroke: C.green, width: 2.5, arrow: 'end' }),
    box(20, 225, 210, 40, 'clamp on the bracket being welded:\ncurrent stays in the part', { fill: C.greenSoft, stroke: C.green, size: 11 }),
    rect(300, 156, 22, 12, { fill: C.copper, stroke: C.accentDark }), path('M300,162 C270,162 270,60 250,60', { stroke: C.ink, width: 2.5 }),
    path('M322,162 L340,170 L360,150 L390,140 L396,108', { stroke: C.red, width: 2, dash: '5 3', arrow: 'end' }),
    box(270, 225, 210, 40, 'clamp on the housing: current crosses\nthe bearing and pits the races', { fill: C.redSoft, stroke: C.red, size: 11 }),
    caption(500, 290, 'Never across a bearing, gear mesh, hinge, cylinder rod or chain.'),
  ], { title: 'Ground clamp placement' }))

// ---------- Cable size ----------
fig('welding/cable-size-chart.svg', 'Welding cable size chart',
  svg(500, 250, [text(250, 24, 'Total lead length = electrode lead + work lead', { anchor: 'middle', weight: 700 }), table(40, 40, [['Output', '≤ 50 ft', '50-100', '100-150', '150-200'], ['100 A', '#4', '#4', '#2', '#2'], ['150 A', '#2', '#2', '#2', '1/0'], ['200 A', '#2', '1/0', '2/0', '4/0'], ['250 A', '1/0', '2/0', '3/0', '4/0'], ['300 A', '2/0', '3/0', '4/0', '4/0'], ['400 A', '3/0', '4/0', '4/0', '2 × 2/0']], [80, 85, 85, 85, 85], { rowH: 24 }), note(250, 222, 'Warm cable or a weak arc on long leads means the cable is too small.', { anchor: 'middle' }), caption(500, 250, 'Bigger is always fine. #2 ≈ 35 mm², 1/0 ≈ 50, 2/0 ≈ 70, 4/0 ≈ 120 mm².')], { title: 'Welding cable size chart' }))

// ---------- Process selector ----------
{
  const dia = (x, y, w, h, t) => [poly([[x + w / 2, y], [x + w, y + h / 2], [x + w / 2, y + h], [x, y + h / 2]], { fill: C.soft, stroke: C.accentDark }), text(x + w / 2, y + h / 2, t, { anchor: 'middle', size: 11, vcenter: true })]
  fig('welding/process-selector.svg', 'Choosing a welding process',
    svg(500, 440, [
      dia(190, 10, 120, 50, 'Material?'),
      box(20, 90, 110, 44, 'Aluminium'), box(140, 90, 110, 44, 'Stainless, thin,\nprecision'), box(260, 90, 110, 44, 'Steel outdoors,\nrusty, windy'), box(380, 90, 110, 44, 'Steel, shop'),
      line(250, 60, 75, 90, { width: 1, arrow: 'end' }), line(250, 60, 195, 90, { width: 1, arrow: 'end' }), line(250, 60, 315, 90, { width: 1, arrow: 'end' }), line(250, 60, 435, 90, { width: 1, arrow: 'end' }),
      box(20, 165, 110, 56, 'TIG (AC) thin;\nMIG spool gun\nover 1/8 in', { fill: C.blueSoft }), box(140, 165, 110, 56, 'TIG (DCEN),\nback-purge roots', { fill: C.blueSoft }), box(260, 165, 110, 56, 'Stick 6010 / 7018\nor E71T-11 / T-8', { fill: C.blueSoft }),
      dia(380, 165, 110, 56, 'Thickness?'),
      line(75, 134, 75, 165, { width: 1, arrow: 'end' }), line(195, 134, 195, 165, { width: 1, arrow: 'end' }), line(315, 134, 315, 165, { width: 1, arrow: 'end' }), line(435, 134, 435, 165, { width: 1, arrow: 'end' }),
      box(260, 260, 110, 60, 'under 1/4 in:\nMIG short-circuit\n.030-.035, C25', { fill: C.blueSoft }), box(380, 260, 110, 60, '1/4 in and up:\nspray or pulse MIG,\nE71T-1 flux-core', { fill: C.blueSoft }),
      line(410, 221, 315, 260, { width: 1, arrow: 'end' }), line(450, 221, 435, 260, { width: 1, arrow: 'end' }),
      box(20, 260, 230, 60, 'Cast iron: nickel stick rods or braze\nHardfacing: stick or open-arc wire', { fill: C.greenSoft }),
      box(20, 345, 470, 60, 'Any process: check code rules (D1.1 needs low-hydrogen), position, fit-up,\npreheat for thick or alloy steel, and the duty cycle of the machine you have.', { size: 11 }),
      caption(500, 440, 'Stick works anywhere; MIG is fastest in the shop; TIG is cleanest.'),
    ], { title: 'Welding process selector' }))
}
