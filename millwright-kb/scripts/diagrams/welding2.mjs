import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'

// ---------- Positions ----------
fig('welding/positions.svg', 'Welding positions for plate and pipe',
  svg(500, 330, [
    text(250, 22, 'Plate: groove (G) and fillet (F)', { anchor: 'middle', weight: 700 }),
    ...[['1G / 1F flat', (x, y) => [plate(x - 40, y, 80, 12), path(`M${x - 10},${y} Q${x},${y - 10} ${x + 10},${y}`, { stroke: C.weld, width: 5 }), line(x, y - 45, x, y - 15, { width: 3, stroke: C.ink })]],
      ['2G / 2F horizontal', (x, y) => [plate(x - 6, y - 45, 12, 80), path(`M${x + 6},${y - 10} Q${x + 16},${y} ${x + 6},${y + 10}`, { stroke: C.weld, width: 5 }), line(x + 45, y, x + 16, y, { width: 3 })]],
      ['3G / 3F vertical', (x, y) => [plate(x - 6, y - 45, 12, 80), path(`M${x + 6},${y - 35} L${x + 6},${y + 30}`, { stroke: C.weld, width: 6 }), line(x + 40, y + 20, x + 14, y - 5, { width: 3, arrow: 'end' }), note(x + 26, y + 34, 'up', { size: 10 })]],
      ['4G / 4F overhead', (x, y) => [plate(x - 40, y - 40, 80, 12), path(`M${x - 10},${y - 28} Q${x},${y - 18} ${x + 10},${y - 28}`, { stroke: C.weld, width: 5 }), line(x, y + 20, x, y - 12, { width: 3 })]]]
      .map(([n, draw], i) => { const x = 65 + i * 123, y = 100; return [...draw(x, y), text(x, 150, n, { anchor: 'middle', size: 11.5 })] }),
    text(250, 185, 'Pipe', { anchor: 'middle', weight: 700 }),
    ...[['1G rolled, weld at top', 0, true], ['2G axis vertical, weld horizontal', 90, false], ['5G axis horizontal, fixed', 0, false], ['6G axis at 45°, fixed', 45, false]]
      .map(([n, rot, roll], i) => { const x = 65 + i * 123, y = 240; return [g([rect(-40, -14, 80, 28, { fill: C.steel, rx: 3 }), line(0, -14, 0, 14, { stroke: C.weld, width: 5 })], { transform: `translate(${x},${y}) rotate(${rot})` }), roll ? arc(x, y - 24, 20, -160, -20, { stroke: C.blue, width: 1, arrow: 'end' }) : '', text(x, 300, n.split(',')[0], { anchor: 'middle', size: 11 }), note(x, 314, n.split(',')[1] ?? '', { anchor: 'middle', size: 10 })] }),
  ], { title: 'Welding positions' }))

// ---------- Distortion: sequences ----------
fig('welding/distortion-sequences.svg', 'Back-step and skip sequences, presetting and balancing',
  svg(500, 300, [
    text(120, 24, 'Back-step', { anchor: 'middle', weight: 700 }), plate(20, 40, 200, 12),
    ...[0, 1, 2, 3, 4].map((i) => [line(60 + i * 40, 46, 22 + i * 40, 46, { stroke: C.weld, width: 5, arrow: 'end' }), text(41 + i * 40, 70, String(i + 1), { anchor: 'middle', size: 11, weight: 600 })]),
    note(120, 88, 'progress →, each segment welded backwards', { anchor: 'middle', size: 10 }),
    text(370, 24, 'Skip (wandering)', { anchor: 'middle', weight: 700 }), plate(270, 40, 210, 12),
    ...[1, 5, 3, 7, 2, 6, 4].map((n, i) => [rect(272 + i * 30, 42, 26, 8, { fill: C.weld, stroke: 'none' }), text(285 + i * 30, 70, String(n), { anchor: 'middle', size: 11, weight: 600 })]),
    note(375, 88, 'weld 1, 5, 3, 7, 2, 6, 4: spreads the heat', { anchor: 'middle', size: 10.5 }),
    text(120, 130, 'Presetting a T', { anchor: 'middle', weight: 700 }),
    plate(30, 200, 180, 12), g([plate(-6, -60, 12, 60)], { transform: 'translate(120,200) rotate(-6)' }), line(120, 200, 120, 140, { dash: '4 3', width: 1, stroke: C.muted }), angle(120, 200, 45, -90, -96, ''), note(150, 160, 'tilt 2-3° away\nfrom the weld side;\nshrinkage pulls it square', { size: 10.5 }),
    path('M114,200 L98,200 L114,184 Z', { fill: C.weld, stroke: C.accentDark }),
    text(370, 130, 'Balance the welds', { anchor: 'middle', weight: 700 }),
    plate(290, 200, 170, 12), plate(368, 140, 12, 60), path('M368,200 L352,200 L368,184 Z', { fill: C.weld, stroke: C.accentDark }), path('M380,200 L396,200 L380,184 Z', { fill: C.weld, stroke: C.accentDark }),
    note(374, 232, 'weld both sides alternately,\nsmallest fillet that meets the drawing', { anchor: 'middle', size: 10.5 }),
    caption(500, 300, 'Less weld metal, spread out, both sides, clamped: that is distortion control.'),
  ], { title: 'Distortion control sequences' }))

// ---------- Preheat vs thickness ----------
{
  const ch = chart({ x: 70, y: 30, w: 400, h: 220, xmin: 0, xmax: 3, ymin: 0, ymax: 500, xticks: [0, 0.5, 1, 1.5, 2, 2.5, 3], yticks: [0, 100, 200, 300, 400, 500], xlabel: 'Thickest part at the joint (in)', ylabel: 'Minimum preheat °F' })
  const series = [['A36 / low CE ≤ 0.40 (7018)', [[0, 50], [0.75, 50], [0.76, 50], [1.5, 50], [1.51, 150], [2.5, 150], [2.51, 225], [3, 225]], C.green], ['CE 0.40-0.50 (1045, A572)', [[0, 150], [0.75, 150], [0.76, 225], [1.5, 225], [1.51, 300], [3, 300]], C.accentDark], ['CE over 0.50 (4140, 4340)', [[0, 300], [0.75, 300], [0.76, 400], [1.5, 400], [1.51, 500], [3, 500]], C.red]]
  const el = series.map(([n, pts, c], i) => [path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5 }), rect(80, 290 + i * 16, 14, 4, { fill: c, stroke: 'none' }), text(100, 296 + i * 16, n, { size: 11 })])
  fig('welding/preheat-chart.svg', 'Typical minimum preheat by thickness and carbon equivalent', svg(500, 350, [ch.el, el, note(300, 296, 'bands after AWS D1.1 Table 3.3\nCE = C + Mn/6 + (Cr+Mo+V)/5\n     + (Ni+Cu)/15', { size: 10 }), caption(500, 350, 'Higher restraint, hydrogen or cold steel: go up a band. Check the WPS.')], { title: 'Preheat chart' }))
}

// ---------- Stainless heat tint ----------
fig('welding/heat-tint-scale.svg', 'Stainless heat tint: what the colour of the weld tells you about shielding',
  svg(500, 200, [
    text(250, 24, 'Heat tint on stainless and titanium', { anchor: 'middle', weight: 700 }),
    ...[['#e8e8e8', 'silver', 'perfect'], ['#f3e0a0', 'straw', 'good'], ['#d8a24a', 'gold', 'acceptable'], ['#8a5a2a', 'brown', 'marginal'], ['#3b5fa8', 'blue', 'poor'], ['#4a4a4a', 'grey / black', 'reject']]
      .map(([c, n, v], i) => [rect(30 + i * 74, 50, 70, 50, { fill: c, stroke: C.line }), text(65 + i * 74, 118, n, { anchor: 'middle', size: 11.5, weight: 600 }), text(65 + i * 74, 134, v, { anchor: 'middle', size: 11, fill: i > 3 ? C.red : C.muted })]),
    line(30, 150, 470, 150, { width: 1, arrow: 'end', stroke: C.muted }), note(250, 166, 'more oxygen reached the hot metal: gas flow, post-flow, purge, cup size, draughts →', { anchor: 'middle', size: 10.5 }),
    caption(500, 200, 'Titanium: silver only. Corrosive service: remove blue and darker.'),
  ], { title: 'Heat tint scale' }))

// ---------- Hardfacing layers ----------
fig('welding/hardfacing-layers.svg', 'Hardfacing build-up: base metal, buffer layer, build-up, hardfacing (2 layers max)',
  svg(500, 220, [
    text(250, 22, 'Section through a rebuilt wear part', { anchor: 'middle', weight: 700 }),
    rect(60, 140, 380, 40, { fill: C.steel }), rect(60, 120, 380, 20, { fill: C.blueSoft }), rect(60, 90, 380, 30, { fill: C.grey }), rect(60, 60, 380, 30, { fill: C.soft }),
    ...[[160, 'base metal (worn part, cleaned to bright metal)'], [130, 'buffer: 309L, 312 or ENiFe on cast, manganese or high-carbon base'], [105, 'build-up: 7018 or ER70S, unlimited layers'], [75, 'hardfacing: 1-2 layers only; check cracks are normal on carbide alloys']]
      .map(([y, t]) => text(70, y + 4, t, { size: 10.5 })),
    caption(500, 220, 'Match the alloy to the wear: abrasion, impact, metal-to-metal, heat.'),
  ], { title: 'Hardfacing layers' }))

// ---------- Weld defects cross-sections ----------
{
  const cell = (x, y, n, draw) => [rect(x, y, 150, 100, { fill: C.paper, stroke: C.line }), text(x + 75, y + 16, n, { anchor: 'middle', size: 11.5, weight: 700 }), ...draw(x + 75, y + 70)]
  const tee = (cx, cy) => [plate(cx - 60, cy, 120, 14), plate(cx - 7, cy - 45, 14, 45)]
  const items = [
    ['Good fillet', (cx, cy) => [...tee(cx, cy), path(`M${cx - 7},${cy} L${cx - 30},${cy} L${cx - 7},${cy - 23} Z`, { fill: C.weld, stroke: C.accentDark })]],
    ['Undercut', (cx, cy) => [...tee(cx, cy), path(`M${cx - 7},${cy} L${cx - 30},${cy} L${cx - 7},${cy - 23} Z`, { fill: C.weld, stroke: C.accentDark }), path(`M${cx - 7},${cy - 23} q-4,-6 0,-9`, { stroke: C.red, width: 2 }), circle(cx - 9, cy - 28, 7, { stroke: C.red, fill: 'none' })]],
    ['Overlap', (cx, cy) => [...tee(cx, cy), path(`M${cx - 7},${cy} L${cx - 30},${cy} L${cx - 7},${cy - 23} Z`, { fill: C.weld, stroke: C.accentDark }), path(`M${cx - 30},${cy} q-8,-2 -6,-8 q6,-6 12,2`, { fill: C.weld, stroke: C.red, width: 1.5 })]],
    ['Porosity', (cx, cy) => [...tee(cx, cy), path(`M${cx - 7},${cy} L${cx - 30},${cy} L${cx - 7},${cy - 23} Z`, { fill: C.weld, stroke: C.accentDark }), ...[[-18, -5], [-13, -10], [-20, -12], [-12, -4]].map(([dx, dy]) => circle(cx + dx, cy + dy, 2, { fill: C.paper, stroke: C.red, width: 1 }))]],
    ['Lack of fusion', (cx, cy) => [...tee(cx, cy), path(`M${cx - 7},${cy} L${cx - 30},${cy} L${cx - 7},${cy - 23} Z`, { fill: C.weld, stroke: C.accentDark }), line(cx - 7, cy - 23, cx - 7, cy - 2, { stroke: C.red, width: 2.5 })]],
    ['Incomplete penetr.', (cx, cy) => [poly([[cx - 60, cy - 10], [cx - 14, cy - 10], [cx - 3, cy + 6], [cx - 3, cy + 12], [cx - 60, cy + 12]], { fill: C.steel }), poly([[cx + 60, cy - 10], [cx + 14, cy - 10], [cx + 3, cy + 6], [cx + 3, cy + 12], [cx + 60, cy + 12]], { fill: C.steel }), path(`M${cx - 14},${cy - 10} Q${cx},${cy - 18} ${cx + 14},${cy - 10} L${cx + 6},${cy + 2} L${cx - 6},${cy + 2} Z`, { fill: C.weld, stroke: C.accentDark }), line(cx - 3, cy + 4, cx + 3, cy + 4, { stroke: C.red, width: 3 })]],
  ]
  fig('welding/weld-defects.svg', 'Common weld defects in cross-section', svg(500, 250, [items.map(([n, d], i) => cell(20 + (i % 3) * 155, 15 + Math.floor(i / 3) * 110, n, d)), caption(500, 250, 'Undercut, overlap: technique. Porosity: gas or dirt. Fusion: heat.')], { title: 'Weld defects' }))
}

// ---------- Welding symbol anatomy ----------
fig('welding/welding-symbol-anatomy.svg', 'The parts of a welding symbol',
  svg(500, 300, [
    line(120, 140, 380, 140, { width: 2 }), line(380, 140, 440, 90, { width: 2, arrow: 'end' }),
    path('M120,140 L60,110 L60,170 Z', { fill: C.paper, width: 2 }),
    // fillet symbol on arrow side (below line)
    path('M240,140 L240,160 L260,160 Z', { fill: C.ink }), text(215, 158, '1/4', { size: 12, anchor: 'end' }), text(275, 158, '6-12', { size: 12 }),
    path('M240,140 L240,120 L260,120 Z', { fill: 'none', width: 1.5 }), text(215, 132, '5/16', { size: 12, anchor: 'end' }),
    circle(380, 140, 6, { fill: 'none' }), rect(374, 128, 12, 6, { fill: C.ink, stroke: 'none' }),
    callout(1, 440, 70), callout(2, 250, 175), callout(3, 250, 105), callout(4, 60, 90), callout(5, 380, 165), callout(6, 300, 175), callout(7, 200, 175),
    legend(20, 200, ['arrow points to the joint', 'below the line = arrow side (this fillet 1/4 in)', 'above the line = other side (this fillet 5/16 in)', 'tail: process, spec or note (omit if none)', 'circle = weld all around; flag = field weld', 'length-pitch: 6 in welds every 12 in', 'size to the left of the symbol'], { size: 10.5, gap: 14 }),
    text(250, 24, 'Reference line, arrow, symbols, dimensions', { anchor: 'middle', weight: 700 }),
  ], { title: 'Welding symbol anatomy' }))

// ---------- Shade number chart ----------
{
  const rows = [['Process', 'Amps', 'Minimum shade', 'Suggested'], ['Stick', '60-160', '8', '10'], ['Stick', '160-250', '10', '12'], ['MIG / flux-core', '60-160', '10', '11'], ['MIG / flux-core', '160-250', '10', '12'], ['MIG / flux-core', '250-500', '10', '14'], ['TIG', '50-150', '8', '10'], ['TIG', '150-500', '10', '12'], ['Plasma cutting', 'under 300', '8', '9'], ['Carbon arc gouging', 'light / heavy', '10 / 11', '12 / 14'], ['Oxy-fuel cutting', 'up to 6 in', '3-4', '4-5'], ['Oxy-fuel welding', '', '4-5', '5-6']]
  fig('welding/lens-shade-chart.svg', 'Lens shade numbers by process and amperage (OSHA 1910.133 / ANSI Z49.1)', svg(500, 340, [text(250, 22, 'Filter lens shade by process (OSHA minimum, suggested comfort)', { anchor: 'middle', weight: 700, size: 12.5 }), table(30, 36, rows, [140, 100, 110, 90], { rowH: 22, size: 11 }), caption(500, 340, 'Start dark and go lighter until you see the puddle; never below minimum.')], { title: 'Lens shade chart' }))
}
