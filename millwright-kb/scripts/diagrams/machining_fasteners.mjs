import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- Broken bolt: weld a nut ----------
fig('machining/broken-bolt-nut-weld.svg', 'Broken bolt removal: weld a nut onto the stub through the nut bore, let it cool a minute, back it out; the weld heat also breaks the rust bond',
  svg(500, 230, [
    rect(40, 120, 420, 80, { fill: C.grey }), rect(120, 120, 30, 80, { fill: C.steelDark }), rect(120, 110, 30, 14, { fill: C.steelDark }),
    poly([[100, 70], [170, 70], [170, 112], [100, 112]], { fill: C.steel }), rect(120, 60, 30, 52, { fill: C.paper, stroke: 'none' }), rect(120, 70, 30, 42, { fill: C.steelDark }),
    path('M122,80 q13,-14 26,0 q-13,10 -26,0', { fill: C.weld, stroke: C.accentDark }), note(135, 52, 'MIG or 7018 fill\ninside the nut', { anchor: 'middle', size: 10 }),
    rect(280, 130, 40, 70, { fill: C.steelDark }), poly([[300, 40], [312, 46], [300, 130], [288, 46]], { fill: C.steel }), note(300, 30, 'left-hand drill:\ncuts and unscrews', { anchor: 'middle', size: 10 }), arc(300, 100, 30, 200, 340, { stroke: C.blue, width: 1.5, arrow: 'end' }),
    note(420, 80, 'penetrant, heat the\nboss (not the bolt),\nshock it, then turn', { anchor: 'middle', size: 10 }),
    caption(500, 230, 'Extractors snap: use them last, and only in a straight, centred hole.'),
  ], { title: 'Broken bolt removal' }))

// ---------- Drill rpm chart ----------
{
  const ch = chart({ x: 60, y: 30, w: 400, h: 200, xmin: 0, xmax: 1, ymin: 0, ymax: 3000, xticks: [0, 0.25, 0.5, 0.75, 1], yticks: [0, 500, 1000, 1500, 2000, 2500, 3000], xfmt: (v) => v === 0 ? '0' : ({ 0.25: '1/4', 0.5: '1/2', 0.75: '3/4', 1: '1' }[v]), xlabel: 'Drill diameter (in)', ylabel: 'rpm' })
  const ln = (sfm, c, n) => { const pts = []; for (let d = 0.11; d <= 1; d += 0.02) pts.push([d, Math.min(3000, 3.82 * sfm / d)]); return [path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5 }), text(ch.sx(0.5) + 4, ch.sy(3.82 * sfm / 0.5) - 6, n, { size: 10.5, fill: c, weight: 600 })] }
  fig('machining/drill-rpm-chart.svg', 'Drill rpm = 3.82 × SFM ÷ diameter: mild steel 90 SFM, stainless 50, aluminium 300 (HSS)', svg(500, 290, [ch.el, ln(50, C.green, 'stainless 50 SFM'), ln(90, C.blue, 'mild steel 90 SFM'), ln(300, C.accentDark, 'aluminium 300 SFM'), note(250, 275, '1/2 in drill in mild steel: 3.82 × 90 ÷ 0.5 = 690 rpm; halve it for carbon steel over 0.4% C', { anchor: 'middle', size: 10 })], { title: 'Drill rpm chart' }))
}

// ---------- Bench grinder rest gaps ----------
fig('machining/bench-grinder-gaps.svg', 'Bench grinder: tool rest within 1/8 in of the wheel, tongue guard within 1/4 in, guard covers all but 90° of the wheel',
  svg(500, 255, [
    circle(200, 120, 80, { fill: C.grey }), circle(200, 120, 15, { fill: C.steelDark }), arc(200, 120, 95, 60, 330, { stroke: C.ink, width: 10 }),
    rect(280, 116, 70, 10, { fill: C.steelDark }), line(280, 116, 280, 100, { width: 1, arrow: 'both', stroke: C.red }), note(292, 100, '1/8 in max', { size: 10, fill: C.red }),
    path('M200,40 L260,40 L262,52', { stroke: C.steelDark, width: 8 }), line(262, 52, 262, 62, { width: 1, arrow: 'both', stroke: C.red }), note(272, 60, '1/4 in max', { size: 10, fill: C.red }),
    note(250, 242, 'readjust the rest and tongue guard as the wheel wears; ring-test wheels first', { anchor: 'middle', size: 10 }),
    note(410, 150, 'exposure: 90° max\n(65° above the\nhorizontal)', { anchor: 'middle', size: 10 }),
  ], { title: 'Bench grinder gaps' }))

// ---------- Lathe parts ----------
fig('machining/lathe-parts.svg', 'Engine lathe: headstock and chuck, tool post on the compound and cross slide, carriage, tailstock, bed, lead screw and feed rod',
  svg(500, 270, [
    rect(30, 160, 440, 30, { fill: C.grey }), rect(30, 60, 110, 100, { fill: C.steelDark, rx: 6 }), circle(150, 110, 34, { fill: C.grey }), circle(150, 110, 8, { fill: C.steelDark }),
    rect(184, 100, 140, 20, { fill: C.steel }), rect(250, 130, 90, 30, { fill: C.grey }), rect(270, 118, 30, 14, { fill: C.grey }), rect(276, 96, 14, 24, { fill: C.ink }),
    rect(390, 90, 70, 70, { fill: C.grey, rx: 4 }), poly([[390, 110], [360, 110], [352, 110]], {}), rect(340, 106, 50, 8, { fill: C.steelDark }),
    line(30, 200, 470, 200, { width: 3, stroke: C.steelDark }), line(30, 212, 470, 212, { width: 3, stroke: C.line }),
    ...[[1, 85, 50], [2, 150, 66], [3, 283, 86], [4, 295, 175], [5, 425, 80], [6, 250, 210], [7, 250, 222]].map(([n, x, y]) => callout(n, x, y, { r: 8 })),
    legend(20, 244, [], {}),
    note(20, 240, '1 headstock · 2 chuck · 3 tool post on compound and cross slide · 4 carriage\n5 tailstock · 6 lead screw · 7 feed rod', { size: 9.5 }),
  ], { title: 'Lathe parts' }))

// ---------- Tramming and keyway ----------
fig('machining/tram-and-keyway.svg', 'Tramming the mill head: sweep an indicator on the table in a 10 in circle, both axes, to zero; cut a shaft keyway to depth W/2 centred with an edge finder',
  svg(500, 250, [
    text(130, 22, 'Tramming the head', { anchor: 'middle', weight: 700 }), rect(30, 170, 200, 16, { fill: C.grey }), rect(100, 60, 60, 60, { fill: C.steelDark, rx: 4 }), line(130, 120, 130, 150, { width: 3 }), path('M130,150 L180,150 L180,168', { width: 2 }), circle(180, 158, 8, { fill: C.paper }),
    arc(130, 170, 50, 180, 360, { stroke: C.blue, width: 1, dash: '4 3', arrow: 'end' }), note(130, 205, 'sweep 180° front-back and side-side;\nadjust the head until the reading repeats', { anchor: 'middle', size: 9.5 }),
    text(370, 22, 'Shaft keyway', { anchor: 'middle', weight: 700 }), circle(370, 120, 55, { fill: C.steel }), rect(352, 65, 36, 30, { fill: C.paper, stroke: C.ink }), dim(352, 58, 388, 58, 'W', { size: 10 }), dim(400, 65, 400, 95, 'W/2 + a hair', { size: 10 }),
    poly([[370, 20], [376, 30], [364, 30]], { fill: C.ink }), note(370, 205, 'edge-find both sides, centre = half the shaft\ndiameter; cut in 2-3 passes; deburr', { anchor: 'middle', size: 9.5 }),
  ], { title: 'Tramming and keyway' }))

// ---------- Tap drill and tap types ----------
fig('machining/tap-drill-and-tap-types.svg', 'Tap drill gives 75% thread (full strength, half the torque to tap); taper, plug and bottoming taps by chamfer length',
  svg(500, 250, [
    text(130, 22, 'Thread percentage', { anchor: 'middle', weight: 700 }),
    rect(40, 60, 180, 60, { fill: C.grey }), ...[0, 1, 2, 3, 4, 5].map((i) => poly([[50 + i * 28, 60], [64 + i * 28, 84], [78 + i * 28, 60]], { fill: C.paper, stroke: C.ink })), line(40, 84, 220, 84, { stroke: C.red, width: 1.5, dash: '4 3' }), text(130, 138, '75% thread: drill = major dia. − pitch', { anchor: 'middle', size: 10 }),
    note(130, 165, '1/2-13: 0.500 − 0.077 = 0.423 → 27/64 drill\nM10 × 1.5: 10 − 1.5 = 8.5 mm drill', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Tap types', { anchor: 'middle', weight: 700 }),
    ...[['taper (8-10 threads)', 40], ['plug (3-5)', 20], ['bottoming (1-2)', 8]].map(([n, ch], i) => { const y = 60 + i * 45; return [rect(290, y, 120, 18, { fill: C.steel }), poly([[410, y], [410 + ch, y + 9], [410, y + 18]], { fill: C.steel }), rect(280, y + 2, 12, 14, { fill: C.steelDark }), note(370, y + 32, n, { anchor: 'middle', size: 10 })] }),
    caption(500, 250, 'Taper or plug first, bottoming tap for blind holes; back off every half turn.'),
  ], { title: 'Tap drill and tap types' }))

// ---------- Galling and anti-seize ----------
fig('fasteners/galling-and-anti-seize.svg', 'Galling: stainless and aluminium threads cold-weld under pressure and speed; anti-seize lowers friction so torque must be reduced 20-30%',
  svg(500, 220, [
    text(130, 22, 'Galling', { anchor: 'middle', weight: 700 }), rect(40, 60, 180, 40, { fill: C.steel }), ...[0, 1, 2, 3, 4].map((i) => poly([[55 + i * 32, 100], [71 + i * 32, 76], [87 + i * 32, 100]], { fill: C.paper, stroke: C.ink })), rect(40, 100, 180, 30, { fill: C.grey }),
    ...[[103, 92], [135, 90]].map(([x, y]) => circle(x, y, 6, { fill: C.red, stroke: 'none' })), note(130, 150, 'high spots weld and tear: the nut seizes\nhalfway; cannot go on or come off', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Anti-seize and torque', { anchor: 'middle', weight: 700 }),
    table(280, 40, [['Condition', 'K', 'Torque'], ['dry, plain', '0.20', '100%'], ['zinc plated', '0.18', '90%'], ['oiled', '0.15', '75%'], ['anti-seize', '0.12-0.14', '60-70%']], [90, 60, 60], { rowH: 20, size: 10 }),
    note(385, 165, 'same torque + anti-seize = 30-40% more\nbolt stretch: yielded studs, cracked flanges', { anchor: 'middle', size: 9.5 }),
    caption(500, 220, 'Slow, clean, lubricated, no impact gun: that is how stainless stays free.'),
  ], { title: 'Galling and anti-seize' }))

// ---------- Bolt head markings ----------
fig('fasteners/bolt-head-markings.svg', 'Grade by head marking: SAE 2 plain, 5 three lines, 8 six lines; metric 8.8, 10.9, 12.9 stamped; stainless A2-70 / A4-80',
  svg(500, 200, [
    ...[['SAE 2', 0, '74 ksi', 'no marks'], ['SAE 5', 3, '120 ksi', '3 lines'], ['SAE 8', 6, '150 ksi', '6 lines'], ['8.8', -1, '116 ksi', 'stamped'], ['10.9', -2, '150 ksi', 'stamped'], ['A2-70', -3, '101 ksi', 'stainless']].map(([n, m, t, d], i) => { const x = 55 + i * 78, y = 80; return [poly(Array.from({ length: 6 }, (_, k) => [x + 30 * Math.cos((k * 60 + 30) * P), y + 30 * Math.sin((k * 60 + 30) * P)]), { fill: C.steel }), ...(m > 0 ? Array.from({ length: m }, (_, k) => line(x + 18 * Math.cos(k * 360 / m * P), y + 18 * Math.sin(k * 360 / m * P), x + 26 * Math.cos(k * 360 / m * P), y + 26 * Math.sin(k * 360 / m * P), { width: 2.5 })) : [text(x, y + 4, m === -1 ? '8.8' : m === -2 ? '10.9' : m === -3 ? 'A2-70' : '', { anchor: 'middle', size: 9, weight: 700 })]), text(x, 130, n, { anchor: 'middle', size: 11, weight: 700 }), note(x, 146, t, { anchor: 'middle', size: 10 }), note(x, 160, d, { anchor: 'middle', size: 9.5 })] }),
    caption(500, 200, 'No grade or maker’s mark = Grade 2 or unknown: not for lifting or structure.'),
  ], { title: 'Bolt head markings' }))

// ---------- Flange star pattern ----------
fig('fasteners/flange-star-pattern.svg', 'Flange bolting: number in a star, tighten in 30%, 60%, 100% passes in star order, then a final circular pass',
  svg(500, 240, [
    circle(130, 120, 85, { fill: C.grey }), circle(130, 120, 40, { fill: C.paper }), ...[1, 5, 3, 7, 2, 6, 4, 8].map((n, i) => { const a = -90 + i * 45; const x = 130 + 65 * Math.cos(a * P), y = 120 + 65 * Math.sin(a * P); return [circle(x, y, 9, { fill: C.paper }), text(x, y + 4, String(n), { anchor: 'middle', size: 10, weight: 700 })] }),
    path(`M${130},${55} L${130},${185} M${65},${120} L${195},${120} M${130 + 65 * Math.cos(-45 * P)},${120 + 65 * Math.sin(-45 * P)} L${130 + 65 * Math.cos(135 * P)},${120 + 65 * Math.sin(135 * P)} M${130 + 65 * Math.cos(45 * P)},${120 + 65 * Math.sin(45 * P)} L${130 + 65 * Math.cos(225 * P)},${120 + 65 * Math.sin(225 * P)}`, { stroke: C.blue, width: 1, dash: '3 3' }),
    table(260, 40, [['Pass', 'Torque', 'Order'], ['1', 'hand snug', 'star'], ['2', '30%', 'star'], ['3', '60%', 'star'], ['4', '100%', 'star'], ['5', '100%', 'circular'], ['retorque', '100%', 'after 4-24 h']], [60, 70, 100], { rowH: 20, size: 10 }),
    caption(500, 240, 'Lubricate threads and nut faces the same way every time.'),
  ], { title: 'Flange star pattern' }))

// ---------- Locking methods ----------
fig('fasteners/locking-methods.svg', 'Locking methods: prevailing torque (nylon insert, deformed thread), jam nut (thin nut first), castle nut and cotter, safety wire pulled in the tightening direction, threadlocker',
  svg(500, 250, [
    ...[['Nylon insert', (x, y) => [poly(Array.from({ length: 6 }, (_, k) => [x + 24 * Math.cos((k * 60 + 30) * P), y + 24 * Math.sin((k * 60 + 30) * P)]), { fill: C.steel }), circle(x, y, 9, { fill: C.blue })]],
      ['Jam nut', (x, y) => [rect(x - 22, y - 4, 44, 22, { fill: C.steel }), rect(x - 22, y - 18, 44, 12, { fill: C.steelDark }), note(x, y + 40, 'thin nut first,\nthen the full nut', { anchor: 'middle', size: 9 })]],
      ['Castle + cotter', (x, y) => [rect(x - 22, y - 10, 44, 24, { fill: C.steel }), ...[0, 1, 2].map((k) => rect(x - 18 + k * 14, y - 22, 8, 12, { fill: C.steel })), line(x - 30, y - 16, x + 30, y - 16, { stroke: C.red, width: 2 })]],
      ['Safety wire', (x, y) => [circle(x - 18, y, 12, { fill: C.steel }), circle(x + 18, y, 12, { fill: C.steel }), path(`M${x - 26},${y - 8} C${x - 5},${y - 20} ${x + 5},${y + 20} ${x + 26},${y + 8}`, { stroke: C.ink, width: 1.5 }), arc(x - 18, y, 16, 200, 320, { stroke: C.blue, width: 1, arrow: 'end' })]],
      ['Threadlocker', (x, y) => [rect(x - 8, y - 26, 16, 52, { fill: C.steel }), ...[0, 1, 2, 3].map((k) => rect(x - 8, y - 20 + k * 12, 16, 4, { fill: C.blue, stroke: 'none' })), note(x, y + 40, '242 blue: removable\n271 red: heat to remove', { anchor: 'middle', size: 9 })]]]
      .map(([n, d], i) => { const x = 60 + i * 95, y = 100; return [text(x, 40, n, { anchor: 'middle', size: 11, weight: 600 }), ...d(x, y)] }),
    note(250, 200, 'split lock washers do not lock hardened bolts; preload (correct torque) is the real lock', { anchor: 'middle', size: 10 }),
    caption(500, 250, 'Wire pulls toward tightening; nylon inserts are single-use in vibration.'),
  ], { title: 'Locking methods' }))

// ---------- Thread identification ----------
fig('fasteners/thread-identification.svg', 'Identify a thread: measure the major diameter with calipers, match the pitch gauge, note taper for NPT; UNC/UNF, metric coarse/fine and pipe threads look alike',
  svg(500, 240, [
    rect(40, 90, 200, 30, { fill: C.steel }), ...Array.from({ length: 12 }, (_, i) => poly([[48 + i * 16, 90], [56 + i * 16, 80], [64 + i * 16, 90]], { fill: C.steel, stroke: C.ink })), dim(48, 70, 64, 70, 'pitch', { size: 10 }), line(255, 80, 255, 120, { width: 1, arrow: 'both' }), text(255, 72, 'major dia.', { anchor: 'middle', size: 10 }),
    rect(60, 130, 120, 14, { fill: C.grey }), ...Array.from({ length: 10 }, (_, i) => poly([[66 + i * 12, 130], [72 + i * 12, 122], [78 + i * 12, 130]], { fill: C.grey, stroke: C.ink })), note(125, 160, 'pitch gauge blade: no light showing', { anchor: 'middle', size: 9.5 }),
    table(280, 40, [['Thread', 'Example', 'Tell-tale'], ['UNC', '1/2-13', '13 TPI'], ['UNF', '1/2-20', '20 TPI'], ['Metric', 'M12 × 1.75', 'pitch in mm'], ['NPT', '1/2-14 NPT', 'taper, 0.840 OD'], ['BSPP (G)', 'G 1/2', '55°, straight']], [55, 72, 85], { rowH: 20, size: 9.5 }),
    caption(500, 240, '1/2 NPT is 0.840 in OD, not 0.500: pipe sizes are nominal.'),
  ], { title: 'Thread identification' }))
