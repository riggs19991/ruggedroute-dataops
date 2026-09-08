import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- PM interval chart ----------
fig('maintenance/pm-interval-chart.svg', 'Typical PM intervals by equipment: what is looked at each shift, weekly, monthly and yearly',
  svg(500, 260, [table(20, 30, [['Equipment', 'Each shift', 'Weekly', 'Monthly / quarterly', 'Annual'], ['Pump', 'pressures, seal, temps', 'vibration, coupling', 'oil, alignment check', 'clearances, seal'], ['Motor', 'temp, noise', 'amps, fins clear', 'regrease, bolts', 'megger, bearings'], ['Gearbox', 'oil level, leaks, temp', '-', 'oil sample, vibration', 'open inspection'], ['Belt drive', 'noise, dust', 'sheave temp', 'tension, alignment', 'sheave wear'], ['Conveyor', 'tracking, idlers, e-stops', 'bearings, take-up', 'splice, lagging', 'structure, pulleys'], ['Compressor', 'oil, temp, drain receiver', 'coolers, leaks', 'filters, separator', 'relief, shutdowns'], ['Hydraulics', 'level, temp, filters, leaks', '-', 'oil sample, precharge', 'oil, cylinders']], [68, 118, 86, 106, 92], { rowH: 24, size: 8.5 }), caption(500, 260, 'Write the number down; a PM that produces no reading produces no trend.')], { title: 'PM interval chart' }))

// ---------- Route: look listen feel measure ----------
fig('maintenance/route-look-listen-feel.svg', 'At each machine on the route: look, listen, feel, measure, record; take readings at marked points the same way every time',
  svg(500, 200, [
    ...[['LOOK', 'leaks, levels,\nguards, dust', C.grey], ['LISTEN', 'growl, whine,\nknock, squeal', C.grey], ['FEEL', 'vibration, heat\n(outside guards)', C.grey], ['MEASURE', 'temp, vibration,\namps, pressure', C.blueSoft], ['RECORD', 'a number, not OK;\ncompare to last', C.greenSoft]].map(([n, d, c], i) => [box(20 + i * 94, 40, 86, 34, n, { fill: c, size: 11.5, weight: 700 }), note(63 + i * 94, 92, d, { anchor: 'middle', size: 8 })]),
    ...[0, 1, 2, 3].map((i) => line(106 + i * 94, 57, 114 + i * 94, 57, { width: 2, arrow: 'end' })),
    note(250, 145, 'alert at baseline + 20°F or 2× baseline vibration; act at 180°F on a bearing housing', { anchor: 'middle', size: 10 }),
    caption(500, 200, 'Paint the measuring points on the machine so every reading is comparable.'),
  ], { title: 'Route: look, listen, feel' }))

// ---------- MTBF timeline ----------
fig('maintenance/mtbf-timeline.svg', 'MTBF = operating hours ÷ failures; MTTR = repair hours ÷ failures; availability = MTBF ÷ (MTBF + MTTR)',
  svg(500, 200, [
    ...[[40, 160, C.greenSoft], [160, 180, C.redSoft], [180, 330, C.greenSoft], [330, 345, C.redSoft], [345, 460, C.greenSoft]].map(([a, b, c]) => rect(a, 60, b - a, 40, { fill: c, stroke: C.line })),
    text(100, 85, 'running', { anchor: 'middle', size: 10 }), text(255, 85, 'running', { anchor: 'middle', size: 10 }), text(402, 85, 'running', { anchor: 'middle', size: 10 }), text(170, 52, 'repair', { anchor: 'middle', size: 9, fill: C.red }), text(337, 52, 'repair', { anchor: 'middle', size: 9, fill: C.red }),
    dim(40, 120, 460, 120, 'one year: 6,000 h running, 4 failures, 32 h down', { size: 10 }),
    note(250, 155, 'MTBF = 6,000 ÷ 4 = 1,500 h · MTTR = 32 ÷ 4 = 8 h · availability = 1,500 ÷ 1,508 = 99.5%', { anchor: 'middle', size: 10 }),
    caption(500, 200, 'The trend and the comparison between twins matter more than the number.'),
  ], { title: 'MTBF timeline' }))

// ---------- Bearing storage ----------
fig('maintenance/bearing-storage-rules.svg', 'Bearing storage: sealed in the wrapper, flat, dry, cool, away from vibration, oldest used first; sealed bearings 3 years, open bearings longer',
  svg(500, 220, [
    rect(40, 50, 260, 130, { fill: C.grey, rx: 6 }), ...[0, 1, 2].map((i) => line(50, 90 + i * 40, 290, 90 + i * 40, { width: 3, stroke: C.steelDark })),
    ...[[60, 70, '2023-04'], [130, 70, '2024-01'], [200, 70, '2024-09'], [60, 110, 'wrapped'], [130, 110, 'flat'], [200, 110, 'boxed']].map(([x, y, l]) => [rect(x, y - 16, 60, 16, { fill: C.paper, stroke: C.ink }), text(x + 30, y - 4, l, { anchor: 'middle', size: 8.5 })]),
    line(60, 150, 260, 150, { width: 1, arrow: 'end', stroke: C.blue }), note(160, 165, 'first in, first out: date on the box', { anchor: 'middle', size: 9.5, fill: C.blue }),
    note(400, 60, 'dry: under 60% RH\ncool and steady\nno vibration nearby\nno solvents or dust', { anchor: 'middle', size: 10 }), note(400, 150, 'never unwrap to look;\nnever wash the\nfactory preservative off', { anchor: 'middle', size: 10, fill: C.red }),
    caption(500, 220, 'Shelf next to a running compressor = false brinelling before installation.'),
  ], { title: 'Bearing storage rules' }))

// ---------- Bearing load path patterns ----------
fig('troubleshooting/bearing-load-paths.svg', 'Running track on the races tells the story: normal centred band, misaligned diagonal band, excessive preload full-width band, axial load offset band',
  svg(500, 220, [
    ...[['Normal', (x) => rect(x - 40, 88, 80, 16, { fill: C.blue, stroke: 'none', opacity: 0.7 }), 'centred band, about\n1/3 of the race width'], ['Misaligned', (x) => poly([[x - 40, 100], [x + 40, 78], [x + 40, 94], [x - 40, 116]], { fill: C.red, stroke: 'none', opacity: 0.7 }), 'diagonal band on the\nouter race, opposite\non the inner'], ['Preloaded', (x) => rect(x - 40, 70, 80, 50, { fill: C.accentDark, stroke: 'none', opacity: 0.6 }), 'full 360° full-width\nband on both races'], ['Axial load', (x) => rect(x - 40, 72, 80, 16, { fill: C.green, stroke: 'none', opacity: 0.7 }), 'band pushed to one\nside of the race']]
      .map(([n, d, t], i) => { const x = 65 + i * 122; return [text(x, 30, n, { anchor: 'middle', size: 11.5, weight: 600 }), rect(x - 45, 60, 90, 70, { fill: C.steel }), rect(x - 45, 70, 90, 50, { fill: C.grey, stroke: 'none' }), d(x), note(x, 150, t, { anchor: 'middle', size: 9.5 })] }),
    caption(500, 220, 'Race unrolled: the band shows where the load ran; then look for damage.'),
  ], { title: 'Bearing load paths' }))

// ---------- V-belt wear patterns ----------
fig('troubleshooting/v-belt-wear-patterns.svg', 'Belt wear patterns: glazed sidewalls (slip), bottoming in a worn groove, one-side wear (misalignment), underside cracks (heat, small sheaves), turned over (loose, misaligned)',
  svg(500, 220, [
    ...[['Glazed sidewalls', (x, y) => [poly([[x - 22, y - 16], [x + 22, y - 16], [x + 14, y + 16], [x - 14, y + 16]], { fill: '#8a8a8a' }), line(x - 20, y - 12, x - 13, y + 12, { stroke: '#fff', width: 2, opacity: 0.8 })], 'slipping: tension'], ['Bottoming', (x, y) => [poly([[x - 30, y - 20], [x + 30, y - 20], [x + 30, y + 22], [x - 30, y + 22]], { fill: C.steelDark }), poly([[x - 20, y - 6], [x + 20, y - 6], [x + 12, y + 20], [x - 12, y + 20]], { fill: '#333' })], 'worn groove: sheave'], ['One side worn', (x, y) => [poly([[x - 22, y - 16], [x + 22, y - 16], [x + 14, y + 16], [x - 6, y + 16]], { fill: '#333' })], 'misalignment'], ['Cracked base', (x, y) => [poly([[x - 22, y - 16], [x + 22, y - 16], [x + 14, y + 16], [x - 14, y + 16]], { fill: '#333' }), ...[-8, 0, 8].map((dx) => line(x + dx, y + 16, x + dx, y + 6, { stroke: C.red, width: 1.5 }))], 'heat, small sheaves'], ['Turned over', (x, y) => [g([poly([[-22, -16], [22, -16], [14, 16], [-14, 16]], { fill: '#333' })], { transform: `translate(${x},${y}) rotate(180)` })], 'loose, pried on']]
      .map(([n, d, t], i) => { const x = 60 + i * 95, y = 90; return [text(x, 40, n, { anchor: 'middle', size: 10.5, weight: 600 }), ...d(x, y), note(x, 140, t, { anchor: 'middle', size: 9.5 })] }),
    caption(500, 220, 'Check the sheaves with a groove gauge before fitting the new set.'),
  ], { title: 'V-belt wear patterns' }))

// ---------- Coupling wear signs ----------
fig('troubleshooting/coupling-wear-signs.svg', 'What is under the guard: rubber dust (misaligned jaw), broken grid ends (misaligned) or centre (overload), worn gear teeth (dry), cracked discs (misaligned or wrong DBSE)',
  svg(500, 220, [
    ...[['Jaw: dust', (x, y) => [rect(x - 26, y - 14, 18, 28, { fill: C.grey }), rect(x + 8, y - 14, 18, 28, { fill: C.grey }), rect(x - 8, y - 12, 16, 24, { fill: C.accent }), ...[0, 1, 2, 3, 4].map((k) => circle(x - 20 + k * 10, y + 28, 2, { fill: C.ink }))], 'misalignment'], ['Grid: broken ends', (x, y) => [rect(x - 26, y - 14, 18, 28, { fill: C.grey }), rect(x + 8, y - 14, 18, 28, { fill: C.grey }), path(`M${x - 8},${y - 8} q8,4 16,0 M${x - 8},${y} q8,4 16,0 M${x - 8},${y + 8} q8,4 16,0`, { stroke: C.blue, width: 2 }), circle(x - 8, y - 8, 3, { fill: C.red, stroke: 'none' }), circle(x + 8, y + 8, 3, { fill: C.red, stroke: 'none' })], 'misalignment;\nmid-span = overload'], ['Gear: worn teeth', (x, y) => [rect(x - 26, y - 14, 18, 28, { fill: C.grey }), rect(x + 8, y - 14, 18, 28, { fill: C.grey }), rect(x - 30, y - 18, 60, 6, { fill: C.steelDark }), rect(x - 30, y + 12, 60, 6, { fill: C.steelDark }), ...[0, 1, 2].map((k) => line(x - 20 + k * 20, y - 18, x - 16 + k * 20, y - 12, { stroke: C.red, width: 1.5 }))], 'dry: lubrication'], ['Disc: cracked', (x, y) => [rect(x - 26, y - 14, 18, 28, { fill: C.grey }), rect(x + 8, y - 14, 18, 28, { fill: C.grey }), rect(x - 6, y - 18, 4, 36, { fill: C.steelDark }), rect(x + 2, y - 18, 4, 36, { fill: C.steelDark }), path(`M${x - 4},${y - 10} l2,6 l-2,6`, { stroke: C.red, width: 1.5 })], 'misalignment or\nwrong DBSE']]
      .map(([n, d, t], i) => { const x = 65 + i * 122, y = 90; return [text(x, 40, n, { anchor: 'middle', size: 10.5, weight: 600 }), ...d(x, y), note(x, 145, t, { anchor: 'middle', size: 9.5 })] }),
    caption(500, 220, 'Measure the alignment as found before you replace the element.'),
  ], { title: 'Coupling wear signs' }))

// ---------- Decision tree ----------
fig('troubleshooting/machine-trouble-tree.svg', 'Machine trouble tree: take readings, then branch on vibrating, noisy or hot to the likely causes',
  svg(500, 320, [
    box(150, 10, 200, 40, '10-minute running check:\ntemps, vibration, listen, amps', { fill: C.grey, size: 10.5 }),
    ...[['VIBRATING', 20, ['1× radial: unbalance', '2× / axial: misalignment', 'harmonics: looseness', 'random high: bearing', 'stops with power: electrical']], ['NOISY', 180, ['squeal: belt slip', 'growl: bearing', 'whine: gears, oil', 'knock: loose, key', 'gravel: cavitation']], ['HOT', 340, ['one bearing: grease, fit', 'motor: load, cooling', 'gearbox: oil level, grade', 'coupling: alignment', 'pump: dead-headed']]]
      .map(([n, x, items]) => [line(250, 50, x + 70, 80, { width: 1.5, arrow: 'end' }), box(x, 80, 140, 30, n, { fill: C.blueSoft, size: 11.5, weight: 700 }), ...items.map((t, k) => text(x + 6, 132 + k * 17, '· ' + t, { size: 10 }))]),
    box(20, 226, 460, 40, 'Write the readings and the finding on the work order;\nset a new baseline after the repair', { fill: C.greenSoft, size: 10.5 }),
    caption(500, 320, 'Stop it first if a bearing is over 220°F, vibration doubled, or smoke.'),
  ], { title: 'Machine trouble tree' }))

// ---------- Seal face patterns ----------
fig('troubleshooting/seal-face-patterns.svg', 'Mechanical seal face wear track: even and narrow (normal), wide (shaft deflection or runout), off-centre (cocked gland), heat-checked (dry running)',
  svg(500, 220, [
    ...[['Normal', (x, y) => [circle(x, y, 40, { fill: C.steel }), circle(x, y, 22, { fill: C.paper }), circle(x, y, 31, { fill: 'none', stroke: C.ink, width: 6, opacity: 0.6 })], 'narrow, even'], ['Wide track', (x, y) => [circle(x, y, 40, { fill: C.steel }), circle(x, y, 22, { fill: C.paper }), circle(x, y, 31, { fill: 'none', stroke: C.ink, width: 16, opacity: 0.6 })], 'runout, deflection,\nvibration'], ['Off-centre', (x, y) => [circle(x, y, 40, { fill: C.steel }), circle(x, y, 22, { fill: C.paper }), circle(x + 5, y - 3, 31, { fill: 'none', stroke: C.ink, width: 8, opacity: 0.6 })], 'cocked stationary,\nuneven gland bolts'], ['Heat checked', (x, y) => [circle(x, y, 40, { fill: C.steel }), circle(x, y, 22, { fill: C.paper }), ...[0, 40, 80, 120, 160, 200, 240, 280, 320].map((a) => line(x + 24 * Math.cos(a * P), y + 24 * Math.sin(a * P), x + 38 * Math.cos(a * P), y + 38 * Math.sin(a * P), { stroke: C.red, width: 1.2 }))], 'dry running,\nvapour, no flush']]
      .map(([n, d, t], i) => { const x = 65 + i * 122, y = 95; return [text(x, 36, n, { anchor: 'middle', size: 11, weight: 600 }), ...d(x, y), note(x, 158, t, { anchor: 'middle', size: 9.5 })] }),
    caption(500, 220, 'The seal is the witness: fix the pump condition it reports.'),
  ], { title: 'Seal face patterns' }))

// ---------- Circle and annulus areas ----------
fig('shop-reference/shaft-bore-annulus-areas.svg', 'Areas: solid shaft π D² ÷ 4, bore the same with the bore diameter, annulus (rod side of a cylinder) is bore area minus rod area',
  svg(500, 200, [
    ...[['Shaft', (x) => [circle(x, 90, 45, { fill: C.steel })], 'A = 0.7854 × D²'], ['Bore', (x) => [rect(x - 55, 40, 110, 100, { fill: C.grey }), circle(x, 90, 45, { fill: C.paper })], 'A = 0.7854 × D²'], ['Annulus (rod side)', (x) => [circle(x, 90, 45, { fill: C.blueSoft }), circle(x, 90, 20, { fill: C.steel })], 'A = 0.7854 × (D² − d²)']]
      .map(([n, d, f], i) => { const x = 85 + i * 165; return [text(x, 24, n, { anchor: 'middle', size: 11.5, weight: 600 }), ...d(x), text(x, 160, f, { anchor: 'middle', size: 11, weight: 600, fill: C.blue })] }),
    caption(500, 200, '4 in bore, 2 in rod: cap side 12.57 in², rod side 12.57 − 3.14 = 9.42 in².'),
  ], { title: 'Shaft, bore and annulus areas' }))

// ---------- Hardness scale bar ----------
fig('shop-reference/hardness-scale-bar.svg', 'Hardness scales side by side: Rockwell C, Brinell and approximate tensile strength, with where common parts sit',
  svg(500, 240, [
    rect(60, 40, 380, 24, { fill: 'url(#hatch)', stroke: C.ink }), ...[[20, '20'], [30, '30'], [40, '40'], [50, '50'], [60, '60'], [65, '65']].map(([v, l]) => [line(60 + (v - 20) * 8.44, 64, 60 + (v - 20) * 8.44, 72, { width: 1 }), text(60 + (v - 20) * 8.44, 84, l, { anchor: 'middle', size: 10 })]), text(30, 56, 'HRC', { size: 10.5, weight: 700, anchor: 'end' }),
    ...[[226, 20], [286, 30], [371, 40], [481, 50], [654, 60]].map(([hb, v]) => text(60 + (v - 20) * 8.44, 106, String(hb), { anchor: 'middle', size: 10 })), text(30, 106, 'HB', { size: 10.5, weight: 700, anchor: 'end' }),
    ...[[107, 20], [138, 30], [182, 40], [246, 50]].map(([t, v]) => text(60 + (v - 20) * 8.44, 126, t + ' ksi', { anchor: 'middle', size: 10 })), text(30, 126, 'ksi', { size: 10.5, weight: 700, anchor: 'end' }),
    ...[[22, 'A36 (HB 140) is below this scale', -1], [30, '4140 pre-hard', 1], [38, 'Grade 8 bolt, AR400', 1], [50, 'flame-hardened journal', 1], [60, 'bearing race', 1]].map(([v, l, s], i) => { const x = 60 + (v - 20) * 8.44; return [line(x, 40, x, 150 + i * 16, { width: 1, stroke: C.blue, dash: '2 2' }), text(x + 4, 154 + i * 16, l, { size: 9.5, fill: C.blue })] }),
    caption(500, 240, 'Tensile (ksi) ≈ 0.5 × HB. Files skate at about 60 HRC.'),
  ], { title: 'Hardness scale bar' }))

// ---------- Spark patterns ----------
fig('shop-reference/spark-test-patterns.svg', 'Spark test patterns: low carbon long straw streams with few forks, high carbon bright bushy bursts, cast iron short red sprays, stainless no bursts',
  svg(500, 290, [
    ...[['Low carbon (1018)', C.accent, 150, 2, 0.6], ['High carbon (1095)', '#fff2a8', 110, 12, 1], ['Grey cast iron', C.red, 60, 8, 0.5], ['Stainless 304', '#e8a54b', 100, 0, 0.7]].map(([n, c, len, bursts, vol], i) => {
      const x0 = 40 + (i % 2) * 240, y0 = 70 + Math.floor(i / 2) * 110
      const out = [text(x0 + 100, y0 - 30, n, { anchor: 'middle', size: 11.5, weight: 600 }), rect(x0, y0 - 10, 200, 70, { fill: '#1a1a2e', rx: 6 }), circle(x0 + 12, y0 + 25, 8, { fill: C.steelDark })]
      for (let k = 0; k < 7; k++) { const dy = (k - 3) * 6 * vol; out.push(line(x0 + 18, y0 + 25, x0 + 18 + len * (0.7 + 0.3 * Math.abs(Math.sin(k * 1.7))), y0 + 25 + dy, { stroke: c, width: 1.2, opacity: 0.9 })) }
      for (let b = 0; b < bursts; b++) { const bx = x0 + 30 + (b * 37) % (len - 10), by = y0 + 25 + ((b * 13) % 30) - 15; for (let s = 0; s < 5; s++) out.push(line(bx, by, bx + 7 * Math.cos(s * 72 * P), by + 7 * Math.sin(s * 72 * P), { stroke: c === C.red ? C.accent : '#fff', width: 1 })) }
      return out
    }),
    caption(500, 290, 'Compare against a known sample on the same wheel in dim light.'),
  ], { title: 'Spark test patterns' }))

// ---------- Pipe schedule wall ----------
fig('shop-reference/pipe-schedule-walls.svg', 'Same nominal size, same OD, different wall: schedule 40, 80 and 160 on a 4 in pipe (OD 4.500 in always)',
  svg(500, 220, [
    ...[['Sch 40', 0.237, '4.026 in ID'], ['Sch 80', 0.337, '3.826 in ID'], ['Sch 160', 0.531, '3.438 in ID']].map(([n, w, id], i) => { const x = 90 + i * 160, r = 60, ri = r * (1 - 2 * w / 4.5); return [text(x, 30, n, { anchor: 'middle', size: 12, weight: 700 }), circle(x, 110, r, { fill: C.steel }), circle(x, 110, ri, { fill: C.paper }), note(x, 190, `wall ${w} in · ${id}`, { anchor: 'middle', size: 10 })] }),
    caption(500, 220, 'Above NPS 12 the OD equals the nominal size; below it does not.'),
  ], { title: 'Pipe schedule walls' }))

// ---------- Torque speed power ----------
{
  const ch = chart({ x: 60, y: 30, w: 400, h: 150, xmin: 0, xmax: 3600, ymin: 0, ymax: 300, xticks: [0, 900, 1800, 3600], yticks: [0, 100, 200, 300], xlabel: 'rpm', ylabel: 'torque (ft-lb)' })
  const hp = (h, c) => { const pts = []; for (let n = 300; n <= 3600; n += 50) { const t = h * 5252 / n; if (t <= 300) pts.push([n, t]) } return [path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5 }), text(ch.sx(pts[pts.length - 1][0]) - 4, ch.sy(pts[pts.length - 1][1]) - 6, h + ' hp', { size: 10, fill: c, weight: 600, anchor: 'end' })] }
  fig('shop-reference/torque-speed-power.svg', 'hp = torque × rpm ÷ 5,252: at the same power, halving the speed doubles the torque', svg(500, 240, [ch.el, hp(10, C.blue), hp(25, C.accentDark), hp(50, C.red), note(250, 225, '25 hp at 1,800 rpm = 73 ft-lb; through a 4:1 reducer at 450 rpm = 292 ft-lb (less losses)', { anchor: 'middle', size: 10 })], { title: 'Torque, speed, power' }))
}

// ---------- Head vs pressure ----------
fig('shop-reference/head-vs-pressure.svg', 'Head and pressure: a column of water 2.31 ft high makes 1 psi; psi = head × SG ÷ 2.31',
  svg(500, 220, [
    rect(80, 30, 40, 160, { fill: '#cfe8ff', stroke: C.blue }), dim(140, 30, 140, 190, '2.31 ft of water', { size: 11 }), rect(60, 190, 80, 12, { fill: C.grey }), circle(100, 205, 0, {}), text(100, 214, '1.0 psi', { anchor: 'middle', size: 12, weight: 700, fill: C.blue }),
    table(262, 40, [['Head', 'Water psi', 'Oil (SG 0.9)'], ['10 ft', '4.3', '3.9'], ['50 ft', '21.6', '19.5'], ['100 ft', '43.3', '39.0'], ['231 ft', '100', '90']], [70, 80, 90], { rowH: 22, size: 10.5 }),
    note(370, 170, 'a pump gauge reads psi; the curve is in feet:\nconvert with the fluid’s specific gravity', { anchor: 'middle', size: 9.5 }),
  ], { title: 'Head vs pressure' }))

// ---------- Task workflow ----------
fig('shop-reference/task-workflow.svg', 'Every job in the same order: isolate and permit, gather the setup data, do the procedure, check and record',
  svg(500, 170, [
    ...[['1 Safety\nlockout, permit, PPE', C.redSoft], ['2 Setup data\ncharts, torque, settings', C.blueSoft], ['3 Procedure\nstep by step', C.grey], ['4 Check + record\nreadings, work order', C.greenSoft]].map(([n, c], i) => box(20 + i * 118, 40, 108, 60, n, { fill: c, size: 9.5 })),
    ...[0, 1, 2].map((i) => line(128 + i * 118, 70, 138 + i * 118, 70, { width: 2, arrow: 'end' })),
    caption(500, 170, 'The task index lists the articles for each step of the common jobs.'),
  ], { title: 'Task workflow' }))

// ---------- Shaft torsion ----------
fig('shop-reference/shaft-torsion-and-key-shear.svg', 'Shaft in torsion: stress = 16 T ÷ (π d³); key in shear carries F = 2 T ÷ d over its side area',
  svg(500, 220, [
    rect(40, 90, 240, 40, { fill: C.steel, rx: 4 }), arc(280, 110, 30, -60, 60, { stroke: C.red, width: 2, arrow: 'end' }), text(320, 114, 'T', { size: 14, weight: 700, fill: C.red }), dim(30, 90, 30, 130, 'd', { size: 11, side: -1 }),
    text(160, 60, 'τ = 16 T ÷ (π d³)', { anchor: 'middle', size: 13, weight: 700 }), note(160, 160, 'T in in-lb, d in inches, τ in psi;\nkeep τ under about 6,000-8,000 psi for 1045 shafting', { anchor: 'middle', size: 10 }),
    rect(380, 80, 80, 60, { fill: C.grey }), rect(410, 70, 20, 20, { fill: C.accent, stroke: C.accentDark }), line(400, 60, 440, 60, { width: 2, arrow: 'end', stroke: C.red }), text(420, 52, 'F = 2 T ÷ d', { anchor: 'middle', size: 11, weight: 700, fill: C.red }),
    note(420, 160, 'key shear area = W × L;\nτ = F ÷ (W × L)', { anchor: 'middle', size: 10 }),
    caption(500, 220, 'Double the diameter: eight times the torque capacity.'),
  ], { title: 'Shaft torsion and key shear' }))

// ---------- Fraction ruler ----------
fig('shop-reference/fraction-decimal-ruler.svg', 'One inch in sixteenths with the decimal and millimetre equivalents',
  svg(500, 170, [
    rect(40, 50, 420, 40, { fill: '#f7e9c4', stroke: C.accentDark }), ...Array.from({ length: 17 }, (_, i) => { const x = 40 + i * 26.25; const h = i % 16 === 0 ? 40 : i % 8 === 0 ? 30 : i % 4 === 0 ? 22 : i % 2 === 0 ? 15 : 9; return line(x, 50, x, 50 + h, { width: i % 4 === 0 ? 1.5 : 1 }) }),
    ...[[4, '1/4', '0.250', '6.35'], [8, '1/2', '0.500', '12.70'], [12, '3/4', '0.750', '19.05'], [16, '1', '1.000', '25.40']].map(([i, f, d, m]) => { const x = 40 + i * 26.25; return [text(x, 108, f, { anchor: 'middle', size: 11, weight: 700 }), text(x, 122, d, { anchor: 'middle', size: 9.5, fill: C.muted }), text(x, 134, m + ' mm', { anchor: 'middle', size: 9.5, fill: C.muted })] }),
    ...[[1, '1/16'], [2, '1/8'], [6, '3/8'], [10, '5/8'], [14, '7/8']].map(([i, f]) => text(40 + i * 26.25, 108, f, { anchor: 'middle', size: 9, fill: C.blue })),
    caption(500, 170, '1/16 = 0.0625 in = 1.59 mm; 1/64 = 0.0156 in = 0.40 mm.'),
  ], { title: 'Fraction decimal ruler' }))

// ---------- Temper and heat colour bars ----------
fig('shop-reference/temper-and-heat-colours.svg', 'Temper colours on bright steel (400-640°F) and incandescent heat colours (900-2,200°F)',
  svg(500, 230, [
    text(250, 22, 'Temper colours (oxide film on polished steel)', { anchor: 'middle', weight: 700, size: 12 }),
    ...[['#f5f0c8', 'faint straw', '400'], ['#efdc8a', 'light straw', '440'], ['#d9a94a', 'dark straw', '465'], ['#a8683a', 'brown', '500'], ['#7a4a7a', 'purple', '540'], ['#2f4a8a', 'dark blue', '560'], ['#6f9ec9', 'light blue', '600'], ['#9a9a9a', 'grey', '640']].map(([c, n, t], i) => [rect(30 + i * 55, 34, 55, 34, { fill: c, stroke: C.line }), text(57 + i * 55, 84, n, { anchor: 'middle', size: 9 }), text(57 + i * 55, 97, t + '°F', { anchor: 'middle', size: 9, fill: C.muted })]),
    text(250, 128, 'Heat colours (in dim light)', { anchor: 'middle', weight: 700, size: 12 }),
    ...[['#4a1a1a', 'faint red', '930'], ['#7a1a1a', 'blood red', '1,075'], ['#a52a2a', 'dark cherry', '1,175'], ['#d23b2a', 'cherry', '1,375'], ['#e8572a', 'bright cherry', '1,450'], ['#f0862a', 'orange', '1,650'], ['#f5c23a', 'yellow', '1,830'], ['#fff5c8', 'white', '2,200']].map(([c, n, t], i) => [rect(30 + i * 55, 140, 55, 34, { fill: c, stroke: C.line }), text(57 + i * 55, 190, n, { anchor: 'middle', size: 9 }), text(57 + i * 55, 203, t + '°F', { anchor: 'middle', size: 9, fill: C.muted })]),
    caption(500, 230, 'Magnet stops sticking at 1,414°F: the hardening heat for carbon steel.'),
  ], { title: 'Temper and heat colours' }))

// ---------- Right triangle ----------
fig('shop-reference/right-triangle-and-offset.svg', 'Right triangle: sin = opposite ÷ hypotenuse, cos = adjacent ÷ hypotenuse, tan = opposite ÷ adjacent; a 45° offset travel = offset × 1.414',
  svg(500, 230, [
    poly([[60, 180], [260, 180], [260, 60]], { fill: C.blueSoft, stroke: C.blue }), rect(246, 166, 14, 14, { fill: 'none', stroke: C.blue, width: 1 }), angle(60, 180, 40, -31, 0, 'θ'),
    text(160, 198, 'adjacent (run)', { anchor: 'middle', size: 11 }), text(268, 124, 'opposite\n(rise)', { size: 11 }), text(140, 108, 'hypotenuse (travel)', { anchor: 'middle', size: 11, angle: -31 }),
    note(400, 70, 'sin θ = opp ÷ hyp\ncos θ = adj ÷ hyp\ntan θ = opp ÷ adj\nhyp² = adj² + opp²', { anchor: 'middle', size: 11, fill: C.ink }),
    note(400, 160, '45° offset: travel = offset × 1.414\n30° offset: travel = offset × 2.0\n22.5°: × 2.613  ·  60°: × 1.155', { anchor: 'middle', size: 10 }),
    caption(500, 230, 'Offset 12 in at 45°: travel 16.97 in, run 12 in.'),
  ], { title: 'Right triangle and offset' }))

// ---------- Conversion ladders ----------
fig('shop-reference/conversion-ladders.svg', 'Pressure and torque side by side: psi, bar and kPa; ft-lb and N·m',
  svg(500, 220, [
    text(130, 22, 'Pressure', { anchor: 'middle', weight: 700 }), ...[['psi', [0, 50, 100, 150, 200]], ['bar', [0, 3.4, 6.9, 10.3, 13.8]], ['kPa', [0, 345, 690, 1034, 1379]]].map(([u, v], j) => [text(50 + j * 60, 44, u, { anchor: 'middle', size: 10.5, weight: 600 }), line(50 + j * 60, 50, 50 + j * 60, 190, { width: 2 }), ...v.map((n, k) => [line(44 + j * 60, 190 - k * 35, 56 + j * 60, 190 - k * 35, { width: 1.5 }), text(60 + j * 60, 194 - k * 35, String(n), { size: 9.5 })])]),
    text(370, 22, 'Torque', { anchor: 'middle', weight: 700 }), ...[['ft-lb', [0, 50, 100, 150, 200]], ['N·m', [0, 68, 136, 203, 271]]].map(([u, v], j) => [text(320 + j * 80, 44, u, { anchor: 'middle', size: 10.5, weight: 600 }), line(320 + j * 80, 50, 320 + j * 80, 190, { width: 2 }), ...v.map((n, k) => [line(314 + j * 80, 190 - k * 35, 326 + j * 80, 190 - k * 35, { width: 1.5 }), text(330 + j * 80, 194 - k * 35, String(n), { size: 9.5 })])]),
    caption(500, 220, '1 psi = 0.0689 bar = 6.895 kPa · 1 ft-lb = 1.356 N·m'),
  ], { title: 'Conversion ladders' }))

// ---------- Gauge thickness bars ----------
{
  const g = [[10, 0.1345], [11, 0.1196], [12, 0.1046], [14, 0.0747], [16, 0.0598], [18, 0.0478], [20, 0.0359], [22, 0.0299], [24, 0.0239]]
  fig('shop-reference/gauge-thickness-bars.svg', 'Steel sheet gauge to thickness: each step is about 10-12% thinner; 10 gauge is just over 1/8 in', svg(500, 255, [text(250, 22, 'Manufacturers’ standard gauge, steel sheet', { anchor: 'middle', weight: 700, size: 12 }), ...g.map(([n, t], i) => { const w = t * 2300; return [text(70, 52 + i * 20, n + ' ga', { anchor: 'end', size: 10.5, weight: 600 }), rect(80, 42 + i * 20, w, 14, { fill: C.steelDark, stroke: 'none' }), text(86 + w, 53 + i * 20, t.toFixed(4) + ' in / ' + (t * 25.4).toFixed(2) + ' mm', { size: 9 })] }), caption(500, 255, 'Galvanised, stainless and aluminium gauges differ: measure in inches.')], { title: 'Gauge thickness bars' }))
}

// ---------- Add a manual flow ----------
fig('manuals/add-a-manual-flow.svg', 'Adding a manual: Contribute, fill the title, manufacturer and model numbers, attach the PDF, submit; a teacher reviews and publishes',
  svg(500, 170, [
    ...[['Contribute\nbutton', C.grey], ['Title, maker,\nmodel, tags', C.blueSoft], ['Attach PDF\n(50 MB max)', C.blueSoft], ['Submit for\nreview', C.soft], ['Teacher\npublishes', C.greenSoft]].map(([n, c], i) => box(20 + i * 94, 40, 86, 60, n, { fill: c, size: 10.5 })),
    ...[0, 1, 2, 3].map((i) => line(106 + i * 94, 70, 114 + i * 94, 70, { width: 2, arrow: 'end' })),
    caption(500, 170, 'Model numbers in the fields make the manual searchable by part number.'),
  ], { title: 'Add a manual flow' }))
