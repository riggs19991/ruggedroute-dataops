import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'

// ---------- Joint types and groove terms ----------
fig('welding/joint-types.svg', 'The five basic joints and the groove terms',
  svg(500, 330, [
    ...[['Butt', (x, y) => [plate(x - 50, y, 46, 14), plate(x + 4, y, 46, 14), path(`M${x - 4},${y} Q${x},${y - 8} ${x + 4},${y}`, { stroke: C.weld, width: 5 })]],
      ['T (fillet)', (x, y) => [plate(x - 50, y, 100, 14), plate(x - 7, y - 50, 14, 50), path(`M${x - 7},${y} L${x - 22},${y} L${x - 7},${y - 15} Z`, { fill: C.weld, stroke: C.accentDark }), path(`M${x + 7},${y} L${x + 22},${y} L${x + 7},${y - 15} Z`, { fill: C.weld, stroke: C.accentDark })]],
      ['Lap', (x, y) => [plate(x - 50, y, 70, 14), plate(x - 20, y - 14, 70, 14), path(`M${x + 20},${y} L${x + 34},${y} L${x + 20},${y - 14} Z`, { fill: C.weld, stroke: C.accentDark })]],
      ['Corner', (x, y) => [plate(x - 40, y, 80, 14), plate(x + 26, y - 50, 14, 50), path(`M${x + 26},${y - 50} L${x + 40},${y - 50} L${x + 40},${y - 36} Z`, { fill: C.weld, stroke: C.accentDark })]],
      ['Edge', (x, y) => [plate(x - 12, y - 50, 12, 64), plate(x, y - 50, 12, 64), path(`M${x - 12},${y - 50} Q${x},${y - 58} ${x + 12},${y - 50}`, { stroke: C.weld, width: 5 })]]]
      .map(([n, draw], i) => { const x = 60 + i * 95, y = 90; return [text(x, 24, n, { anchor: 'middle', weight: 700, size: 12.5 }), ...draw(x, y)] }),
    // groove terms: single-V butt
    text(250, 150, 'Single-V groove terms', { anchor: 'middle', weight: 700 }),
    poly([[60, 190], [200, 190], [232, 260], [232, 275], [60, 275]], { fill: C.steel }), poly([[440, 190], [300, 190], [268, 260], [268, 275], [440, 275]], { fill: C.steel }),
    angle(250, 175, 40, 65, 115, ''), text(250, 172, '60° groove angle', { anchor: 'middle', size: 11, fill: C.blue }),
    dim(232, 292, 268, 292, 'root opening 1/16-1/8 in', { size: 11 }), line(268, 267, 300, 258, { width: 1, stroke: C.blue }), text(304, 262, 'root face 1/16-1/8 in', { size: 11, fill: C.blue }),
    angle(200, 190, 34, 90, 65, ''), text(178, 232, '30° bevel', { size: 11, fill: C.blue, anchor: 'end' }),
    dim(450, 190, 450, 275, 'T', { size: 11 }),
    note(250, 318, 'Root face stops burn-through; root opening lets the root fuse.', { anchor: 'middle' }),
  ], { title: 'Weld joint types' }))

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

// ---------- AC balance waveform ----------
{
  const ch = { x: 40, y: 40, w: 420, h: 120 }
  const wave = (bal, y0, label) => {
    const per = 140, out = []
    for (let k = 0; k < 3; k++) {
      const x0 = ch.x + k * per, en = per * bal
      out.push(rect(x0, y0, en, 40, { fill: C.blueSoft, stroke: C.blue })); out.push(rect(x0 + en, y0 - 40, per - en, 40, { fill: C.redSoft, stroke: C.red }))
    }
    out.push(text(ch.x + 6, y0 - 48, label, { size: 11, weight: 600 }))
    return out
  }
  fig('welding/ac-balance.svg', 'AC balance for aluminium TIG: EN half-cycle penetrates, EP half-cycle cleans',
    svg(500, 285, [
      text(250, 22, 'AC square wave: electrode negative (EN) vs electrode positive (EP)', { anchor: 'middle', weight: 700, size: 12.5 }),
      line(40, 90, 460, 90, { width: 1, stroke: C.muted }), wave(0.7, 90, '70% EN'),
      line(40, 200, 460, 200, { width: 1, stroke: C.muted }), wave(0.5, 200, '50% EN'),
      text(30, 70, 'EP', { size: 10, fill: C.red, anchor: 'end' }), text(30, 120, 'EN', { size: 10, fill: C.blue, anchor: 'end' }),
      note(250, 148, 'more EN = more penetration, cooler tungsten, narrower cleaning band (start here, 65-75%)', { anchor: 'middle', size: 10.5 }),
      note(250, 256, 'more EP = wider cleaning, hotter tungsten, wider bead (dirty or cast aluminium)', { anchor: 'middle', size: 10.5 }),
      caption(500, 285, 'Frequency 100-150 Hz tightens the arc; 60-80 Hz widens it.'),
    ], { title: 'AC balance' }))
}

// ---------- Cast iron repair ----------
fig('welding/cast-iron-repair.svg', 'Cast iron crack repair: drill the ends, V it out, short stringers, peen each one',
  svg(500, 250, [
    rect(40, 60, 420, 120, { fill: C.grey }), path('M120,90 Q220,140 340,110', { stroke: C.ink, width: 2 }),
    circle(120, 90, 7, { fill: C.paper }), circle(340, 110, 7, { fill: C.paper }),
    ...[0, 1, 2, 3, 4].map((i) => { const t = 0.12 + i * 0.19; const x = 120 + (340 - 120) * t, y = 90 + 2 * (140 - 90) * t * (1 - t) + (110 - 90) * t; return [rect(x - 14, y - 6, 28, 12, { fill: C.weld, stroke: C.accentDark, rx: 3 }), text(x, y + 4, String([1, 4, 2, 5, 3][i]), { anchor: 'middle', size: 10, weight: 700 })] }),
    callout(1, 120, 70), callout(2, 230, 150), callout(3, 340, 130),
    legend(40, 205, ['drill 1/8-3/16 in holes at each crack end (stops it running)', 'grind or gouge a V, weld 1 in stringers in the numbered order, peen each', 'hot method: preheat 500-1,200°F; cold method: keep it under 150°F'], { size: 10.5, gap: 15 }),
  ], { title: 'Cast iron crack repair' }))

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

// ---------- Blueprint views ----------
fig('welding/orthographic-views.svg', 'Third-angle projection: top view above the front view, right side view to the right',
  svg(500, 300, [
    text(250, 22, 'Third-angle projection (US): what you see from each side', { anchor: 'middle', weight: 700, size: 12.5 }),
    // top view
    rect(80, 40, 140, 60, { fill: C.grey }), circle(190, 70, 14, { fill: C.paper }), text(150, 118, 'TOP', { anchor: 'middle', size: 11, weight: 600 }),
    // front view
    poly([[80, 150], [220, 150], [220, 240], [150, 240], [150, 200], [80, 200]], { fill: C.grey }), line(176, 150, 176, 240, { dash: '5 3', width: 1 }), line(204, 150, 204, 240, { dash: '5 3', width: 1 }), text(150, 258, 'FRONT', { anchor: 'middle', size: 11, weight: 600 }),
    // right side
    poly([[260, 150], [320, 150], [320, 240], [300, 240], [300, 200], [260, 200]], { fill: C.grey }), text(290, 258, 'RIGHT SIDE', { anchor: 'middle', size: 11, weight: 600 }),
    line(80, 110, 80, 145, { dash: '3 3', width: 0.8, stroke: C.muted }), line(220, 110, 220, 145, { dash: '3 3', width: 0.8, stroke: C.muted }), line(230, 150, 255, 150, { dash: '3 3', width: 0.8, stroke: C.muted }), line(230, 240, 255, 240, { dash: '3 3', width: 0.8, stroke: C.muted }),
    table(340, 40, [['Line', 'Means'], ['solid thick', 'visible edge'], ['dashed', 'hidden edge'], ['thin chain', 'centre line'], ['thin + arrows', 'dimension'], ['zigzag', 'break'], ['thick chain', 'cutting plane']], [75, 85], { rowH: 22, size: 10.5 }),
    caption(500, 300, 'First-angle (ISO) puts the top view below the front view: check the symbol.'),
  ], { title: 'Orthographic views' }))

// ---------- MIG gun parts ----------
fig('welding/mig-gun-parts.svg', 'MIG gun consumables in order: liner, gas diffuser, contact tip, nozzle',
  svg(500, 215, [
    rect(20, 80, 150, 40, { fill: C.grey, rx: 10 }), text(95, 72, 'gun neck', { anchor: 'middle', size: 11 }),
    rect(170, 88, 70, 24, { fill: C.steelDark, rx: 3 }), rect(240, 84, 60, 32, { fill: C.copper, stroke: C.accentDark, rx: 3 }), rect(300, 92, 60, 16, { fill: C.brass, stroke: C.accentDark }), rect(365, 76, 110, 48, { fill: C.copper, stroke: C.accentDark, rx: 6 }),
    line(20, 100, 480, 100, { stroke: C.ink, width: 1.5, dash: '2 3' }),
    callout(1, 60, 60), callout(2, 205, 60), callout(3, 270, 60), callout(4, 330, 60), callout(5, 420, 60),
    legend(20, 140, ['liner: sized to the wire, cut square, replace when feeding drags', 'diffuser / retaining head: gas ports clear, threads tight', 'contact tip: replace when oval, burnt or feeding stutters', 'nozzle: 1/2-5/8 in ID, anti-spatter, tip recessed for spray', 'wire path: kinks, dirt or a worn liner cause bird-nests'], { size: 10.5, gap: 14 }),
  ], { title: 'MIG gun parts' }))

// ---------- Shade number chart ----------
{
  const rows = [['Process', 'Amps', 'Minimum shade', 'Suggested'], ['Stick', '60-160', '8', '10'], ['Stick', '160-250', '10', '12'], ['MIG / flux-core', '60-160', '10', '11'], ['MIG / flux-core', '160-250', '10', '12'], ['MIG / flux-core', '250-500', '10', '14'], ['TIG', '50-150', '8', '10'], ['TIG', '150-500', '10', '12'], ['Plasma cutting', 'under 300', '8', '9'], ['Carbon arc gouging', 'light / heavy', '10 / 11', '12 / 14'], ['Oxy-fuel cutting', 'up to 6 in', '3-4', '4-5'], ['Oxy-fuel welding', '', '4-5', '5-6']]
  fig('welding/lens-shade-chart.svg', 'Lens shade numbers by process and amperage (OSHA 1910.133 / ANSI Z49.1)', svg(500, 340, [text(250, 22, 'Filter lens shade by process (OSHA minimum, suggested comfort)', { anchor: 'middle', weight: 700, size: 12.5 }), table(30, 36, rows, [140, 100, 110, 90], { rowH: 22, size: 11 }), caption(500, 340, 'Start dark and go lighter until you see the puddle; never below minimum.')], { title: 'Lens shade chart' }))
}

// ---------- Brazing joint ----------
fig('welding/brazing-joint.svg', 'Silver brazing: capillary gap 0.002-0.005 in, heat the parts not the filler, overlap 3-4 × wall',
  svg(500, 230, [
    text(250, 22, 'Capillary joint: heat pulls the filler in; the torch does not push it', { anchor: 'middle', weight: 700, size: 11.5 }),
    rect(60, 90, 220, 50, { fill: C.copper, stroke: C.accentDark }), rect(60, 104, 220, 22, { fill: C.paper, stroke: 'none' }),
    rect(200, 82, 200, 66, { fill: C.copper, stroke: C.accentDark }), rect(200, 90, 200, 50, { fill: C.paper, stroke: 'none' }), rect(200, 104, 80, 22, { fill: C.copper, stroke: 'none' }),
    rect(200, 90, 80, 14, { fill: '#c0c0c0' }), rect(200, 126, 80, 14, { fill: '#c0c0c0' }),
    dim(200, 160, 280, 160, 'overlap 3-4 × wall', { size: 11 }),
    line(200, 84, 200, 56, { width: 1, stroke: C.muted }), note(200, 50, 'gap 0.002-0.005 in per side (silver); 0.003-0.01 bronze', { anchor: 'middle', size: 10.5 }),
    path('M330,40 L300,80', { stroke: C.red, width: 3, arrow: 'end' }), note(340, 40, 'flame on the heavy\nsection, moving; feed\nrod at the joint edge\nwhen the flux runs clear', { size: 10.5 }),
    rect(150, 92, 40, 10, { fill: '#c0c0c0', stroke: 'none' }), note(150, 76, 'filler flows toward the heat', { anchor: 'middle', size: 10.5 }),
    caption(500, 230, 'Clean, flux, fit, heat evenly, feed, let it cool, wash off the flux.'),
  ], { title: 'Brazing joint' }))
