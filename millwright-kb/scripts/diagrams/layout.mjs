import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, hatchRect, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- Bolt circle with chord factor ----------
{
  const cx = 150, cy = 150, R = 100, n = 6
  const holes = Array.from({ length: n }, (_, i) => { const a = -90 + 30 + i * 60; return [cx + R * Math.cos(a * P), cy + R * Math.sin(a * P)] })
  fig('layout-templates/bolt-circle-chord.svg', 'Bolt circle layout: step the chord with dividers; holes straddle the centrelines',
    svg(500, 300, [
      circle(cx, cy, R, { dash: '5 4', stroke: C.blue, width: 1 }), circle(cx, cy, 130, { stroke: C.line }), line(cx - 140, cy, cx + 140, cy, { width: 0.8, dash: '8 4', stroke: C.muted }), line(cx, cy - 140, cx, cy + 140, { width: 0.8, dash: '8 4', stroke: C.muted }),
      ...holes.map(([x, y]) => circle(x, y, 9, { fill: C.paper })),
      line(holes[0][0], holes[0][1], holes[1][0], holes[1][1], { stroke: C.red, width: 2 }), text((holes[0][0] + holes[1][0]) / 2 + 8, (holes[0][1] + holes[1][1]) / 2 - 4, 'chord', { size: 11, fill: C.red, weight: 600 }),
      note(cx, cy + 6, 'BC dia.', { anchor: 'middle', fill: C.blue }),
      table(300, 40, [['Holes', 'Chord ÷ BC dia.'], ['4', '0.7071'], ['5', '0.5878'], ['6', '0.5000'], ['8', '0.3827'], ['10', '0.3090'], ['12', '0.2588'], ['16', '0.1951']], [70, 120], { rowH: 21, size: 11 }),
      note(300, 225, 'chord = factor × bolt circle dia.\n6 holes on a 12 in BC:\nchord = 0.5 × 12 = 6.000 in', { size: 10.5 }),
      caption(500, 300, 'Straddle: no hole on the vertical or horizontal centreline (flanges).'),
    ], { title: 'Bolt circle chord layout' }))
}

// ---------- Pipe saddle template ----------
{
  const pts = Array.from({ length: 17 }, (_, i) => { const a = i * 22.5 * P; const y = 30 * (1 - Math.cos(a)); return [60 + i * 22, 215 - 24 * Math.abs(Math.sin(a)) ** 1 - 0.5 * y] })
  fig('layout-templates/saddle-template-ordinates.svg', 'Saddle template by ordinates: 16 divisions around the branch, heights from the table, wrap around the branch pipe',
    svg(500, 300, [
      // header and branch
      rect(310, 30, 170, 50, { fill: C.steel, rx: 6 }), rect(375, 80, 40, 80, { fill: C.steel }), path('M375,80 q20,-28 40,0', { stroke: C.accentDark, width: 2, fill: C.paper }),
      note(395, 176, 'branch cut to fit the header', { anchor: 'middle', size: 10 }),
      text(150, 24, 'Template unrolled (branch circumference)', { anchor: 'middle', weight: 700, size: 11.5 }),
      line(60, 215, 412, 215, { width: 1 }), ...pts.map(([x, y], i) => [line(x, 215, x, y, { width: 1, stroke: C.blue }), text(x, 230, String(i), { anchor: 'middle', size: 8.5, fill: C.muted })]),
      path(pts.map((p, i) => (i ? 'L' : 'M') + p[0] + ',' + p[1]).join(' '), { stroke: C.red, width: 2 }),
      dim(60, 250, 412, 250, 'circumference = π × branch OD, in 16 equal parts', { size: 10.5 }),
      text(30, 190, 'ordinate', { size: 10, fill: C.blue, angle: -90, anchor: 'middle' }),
      caption(500, 300, 'Cut on the curve, wrap the template on the branch, scribe, cut, grind to fit.'),
    ], { title: 'Saddle template ordinates' }))
}

// ---------- Cone development ----------
{
  const R = 110, r = 40, h = 100
  const slant = Math.hypot(h, R - r)
  const ang = 360 * R / slant
  fig('layout-templates/cone-development.svg', 'Radial-line development of a cone: the pattern is a sector with radius = slant height and angle = 360 × (base radius ÷ slant)',
    svg(500, 300, [
      text(110, 24, 'Elevation', { anchor: 'middle', weight: 700 }), poly([[40, 200], [180, 200], [140, 90], [80, 90]], { fill: C.steel }), line(40, 200, 110, 8, { width: 0.8, dash: '4 3', stroke: C.muted }), line(180, 200, 110, 8, { width: 0.8, dash: '4 3', stroke: C.muted }),
      dim(40, 215, 180, 215, 'base dia. D', { size: 11 }), dim(80, 80, 140, 80, 'top dia. d', { size: 11 }), dim(200, 90, 200, 200, 'h', { size: 11 }),
      line(180, 200, 140, 90, { stroke: C.red, width: 2 }), text(150, 150, 'S', { size: 12, fill: C.red, weight: 700, anchor: 'end' }),
      text(370, 24, 'Pattern (sector)', { anchor: 'middle', weight: 700 }),
      path(`M370,60 L${370 - 110 * Math.sin(50 * P)},${60 + 110 * Math.cos(50 * P)} A110,110 0 0 0 ${370 + 110 * Math.sin(50 * P)},${60 + 110 * Math.cos(50 * P)} Z`, { fill: C.steel }),
      path(`M${370 - 45 * Math.sin(50 * P)},${60 + 45 * Math.cos(50 * P)} A45,45 0 0 0 ${370 + 45 * Math.sin(50 * P)},${60 + 45 * Math.cos(50 * P)}`, { stroke: C.paper, width: 3 }),
      note(370, 200, 'outer radius = S (full cone slant)\ninner radius = S − slant of the frustum\nsector angle = 360 × (D ÷ 2) ÷ S', { anchor: 'middle', size: 10.5 }),
      caption(500, 300, 'Add a seam lap; check the pattern by rolling paper first.'),
    ], { title: 'Cone development' }))
}

// ---------- Shim stacking ----------
fig('layout-templates/shim-stacking.svg', 'Shim rules: thick shims on the bottom, no more than 3-4 per foot, slotted shim fully under the foot',
  svg(500, 230, [
    text(120, 24, 'Right', { anchor: 'middle', weight: 700, fill: C.green }), text(370, 24, 'Wrong', { anchor: 'middle', weight: 700, fill: C.red }),
    ...[0, 250].map((ox, k) => [rect(ox + 40, 150, 170, 14, { fill: C.grey }), rect(ox + 80, 60, 90, 60, { fill: C.steel }), line(ox + 125, 60, ox + 125, 175, { stroke: C.ink, width: 3 })]),
    rect(80, 136, 90, 10, { fill: C.steelDark }), rect(80, 128, 90, 8, { fill: C.steelDark }), rect(80, 123, 90, 5, { fill: C.steel }), rect(80, 120, 90, 3, { fill: C.line }),
    note(125, 190, '0.125 + 0.050 + 0.020 + 0.005\nfour shims, thick to thin, full contact', { anchor: 'middle', size: 10 }),
    ...[0, 1, 2, 3, 4, 5, 6, 7].map((i) => rect(330 + (i % 2) * 6, 143 - i * 3.2, 80 - (i % 3) * 6, 3, { fill: C.steelDark })),
    note(375, 190, 'eight thin shims, misaligned, rust between:\nthey squash and the foot goes soft', { anchor: 'middle', size: 10 }),
    caption(500, 230, 'Burrs off, shims clean and dry, slot centred on the bolt, no overhang.'),
  ], { title: 'Shim stacking rules' }))

// ---------- Story pole ----------
fig('layout-templates/story-pole.svg', 'Story pole: one stick carries every elevation or spacing, so every part is marked from the same reference',
  svg(500, 220, [
    rect(40, 60, 420, 22, { fill: '#e8d3a3', stroke: C.accentDark }),
    ...[[60, 'datum'], [130, 'bolt 1'], [200, 'bolt 2'], [290, 'bolt 3'], [380, 'bolt 4'], [440, 'end']].map(([x, l]) => [line(x, 60, x, 82, { stroke: C.red, width: 2 }), text(x, 100, l, { anchor: 'middle', size: 10.5 })]),
    text(60, 52, '0', { anchor: 'middle', size: 10, fill: C.muted }), text(130, 52, '3.500', { anchor: 'middle', size: 10, fill: C.muted }), text(200, 52, '7.000', { anchor: 'middle', size: 10, fill: C.muted }), text(290, 52, '11.500', { anchor: 'middle', size: 10, fill: C.muted }), text(380, 52, '16.000', { anchor: 'middle', size: 10, fill: C.muted }),
    note(250, 130, 'lay the pole on each part with the datum mark on the datum edge; transfer with a square', { anchor: 'middle', size: 10.5 }),
    note(250, 150, 'no adding up of tape readings, no accumulated error, every part identical', { anchor: 'middle', size: 10.5 }),
    caption(500, 220, 'Label it with the job, the datum and the date; keep it with the drawing.'),
  ], { title: 'Story pole' }))

// ---------- Anchor types ----------
fig('installation/anchor-types.svg', 'Anchor types: cast-in J or L bolt, wedge, sleeve and adhesive, with embedment and edge distance',
  svg(500, 300, [
    rect(20, 120, 460, 140, { fill: '#d9d4c7' }), rect(20, 120, 460, 140, { fill: 'url(#dots)', stroke: C.steelDark }), rect(20, 100, 460, 20, { fill: C.steel }),
    ...[['Cast-in J bolt', (x) => [line(x, 60, x, 230, { width: 5 }), path(`M${x},230 q0,18 -18,16`, { width: 5, fill: 'none' }), rect(x - 14, 92, 28, 8, { fill: C.ink }), circle(x, 82, 0, {}), rect(x - 12, 70, 24, 10, { fill: C.steelDark }), rect(x - 30, 60, 60, 4, { fill: C.grey })]],
      ['Wedge (KB-TZ)', (x) => [line(x, 60, x, 210, { width: 5 }), poly([[x - 6, 200], [x + 6, 200], [x + 9, 214], [x - 9, 214]], { fill: C.steelDark }), rect(x - 12, 70, 24, 10, { fill: C.steelDark }), rect(x - 30, 60, 60, 4, { fill: C.grey })]],
      ['Sleeve', (x) => [line(x, 60, x, 200, { width: 5 }), rect(x - 8, 120, 16, 80, { fill: C.steel, stroke: C.steelDark }), poly([[x - 6, 195], [x + 6, 195], [x + 10, 208], [x - 10, 208]], { fill: C.steelDark }), rect(x - 12, 70, 24, 10, { fill: C.steelDark }), rect(x - 30, 60, 60, 4, { fill: C.grey })]],
      ['Adhesive (epoxy)', (x) => [rect(x - 9, 120, 18, 110, { fill: C.soft, stroke: C.accentDark }), line(x, 60, x, 226, { width: 5 }), rect(x - 12, 70, 24, 10, { fill: C.steelDark }), rect(x - 30, 60, 60, 4, { fill: C.grey })]]]
      .map(([n, d], i) => { const x = 80 + i * 115; return [...d(x), text(x, 48, n, { anchor: 'middle', size: 11, weight: 600 })] }),
    dim(455, 120, 455, 226, 'embed.', { size: 10, side: -1 }), dim(20, 275, 80, 275, 'edge dist.', { size: 10.5 }),
    caption(500, 300, 'Wedge: 8-10 × dia. from an edge; adhesive: clean, dry, brushed hole.'),
  ], { title: 'Anchor types' }))

// ---------- Grout pour ----------
fig('installation/grout-pour.svg', 'Grouting a baseplate: chamfered forms, head box on one side, grout flows under and out the far side, jack bolts wrapped',
  svg(500, 290, [
    rect(20, 200, 460, 50, { fill: '#d9d4c7' }), rect(20, 200, 460, 50, { fill: 'url(#dots)', stroke: C.steelDark }),
    rect(80, 140, 340, 60, { fill: C.soft, stroke: C.accentDark }), rect(80, 120, 340, 20, { fill: C.steel }), rect(120, 60, 260, 60, { fill: C.grey }),
    poly([[60, 200], [80, 200], [80, 140], [60, 150]], { fill: '#8b5a2b' }), poly([[420, 200], [440, 200], [440, 150], [420, 140]], { fill: '#8b5a2b' }),
    rect(40, 100, 40, 40, { fill: 'none', stroke: '#8b5a2b', width: 3 }), path('M60,100 L60,150', { stroke: C.accent, width: 6 }),
    ...[130, 370].map((x) => [line(x, 90, x, 200, { width: 4 }), rect(x - 8, 128, 16, 72, { fill: C.paper, stroke: C.muted, dash: '2 2' })]),
    ...[250].map((x) => line(x, 100, x, 240, { width: 5 })),
    callout(1, 60, 90), callout(2, 130, 90), callout(3, 250, 90), callout(4, 430, 130), callout(5, 300, 170),
    legend(20, 230 + 0, [], {}),
    note(20, 18, '1 head box: pour from one side only  ·  2 jack bolts wrapped or waxed, removed after cure', { size: 10 }),
    note(20, 33, '3 anchor bolts sleeved · 4 chamfered forms above the plate underside · 5 grout 1-2 in', { size: 9.5 }),
    caption(500, 290, 'Vent holes in the plate; strap the flow, never vibrate epoxy; cure first.'),
  ], { title: 'Grout pour' }))

// ---------- Leveling sequence ----------
fig('installation/leveling-with-jack-bolts.svg', 'Leveling a baseplate: precision level on the machined pads, jack bolts at each anchor, level both directions before grout',
  svg(500, 285, [
    rect(20, 190, 460, 50, { fill: '#d9d4c7' }), rect(20, 190, 460, 50, { fill: 'url(#dots)', stroke: C.steelDark }),
    rect(80, 120, 340, 18, { fill: C.steel }), rect(120, 100, 100, 20, { fill: C.grey }), rect(280, 100, 100, 20, { fill: C.grey }),
    ...[100, 400].map((x) => [line(x, 138, x, 190, { width: 4, stroke: C.blue }), rect(x - 10, 176, 20, 14, { fill: C.steelDark }), rect(x - 14, 120, 28, 8, { fill: C.ink })]),
    rect(150, 80, 40, 20, { fill: '#2b6cb0', rx: 3 }), rect(160, 84, 20, 8, { fill: '#cfe8ff' }), circle(170, 88, 3, { fill: C.paper }),
    line(150, 70, 250, 70, { width: 1, arrow: 'both', stroke: C.muted }), note(250, 60, 'level each pad, both directions, then diagonally', { size: 9.5 }),
    note(250, 163, 'target: 0.001-0.002 in/ft', { anchor: 'middle', size: 10, fill: C.ink, weight: 600 }), note(250, 177, '(0.005 in/ft is fine for general machines)', { anchor: 'middle', size: 9.5 }),
    callout(1, 100, 205), callout(2, 170, 50),
    legend(20, 258, ['jack bolts on a landing plate; back them out after the grout cures', 'precision level (0.0005 in/ft per division) on a clean machined pad'], { size: 10, gap: 13 }).replace('</text>', '</text>'),
  ], { title: 'Leveling with jack bolts' }))

// ---------- Guard opening chart ----------
{
  const rows = [['Distance from nip point', 'Max opening'], ['1/2 to 1-1/2 in', '1/4 in'], ['1-1/2 to 2-1/2 in', '3/8 in'], ['2-1/2 to 3-1/2 in', '1/2 in'], ['3-1/2 to 5-1/2 in', '5/8 in'], ['5-1/2 to 6-1/2 in', '3/4 in'], ['6-1/2 to 7-1/2 in', '7/8 in'], ['7-1/2 to 12-1/2 in', '1-1/4 in'], ['12-1/2 to 15-1/2 in', '1-1/2 in'], ['15-1/2 to 17-1/2 in', '1-7/8 in'], ['17-1/2 to 31-1/2 in', '2-1/8 in']]
  fig('installation/guard-opening-chart.svg', 'Guard openings: the further the guard is from the nip point, the larger the opening may be (OSHA 1910.217 Table O-10)',
    svg(500, 320, [text(250, 22, 'Maximum guard opening by distance from the hazard', { anchor: 'middle', weight: 700, size: 12.5 }), table(40, 36, rows, [180, 110], { rowH: 22, size: 11 }),
      rect(350, 60, 120, 100, { fill: C.paper, stroke: C.ink }), ...[0, 1, 2, 3].map((i) => rect(360 + i * 28, 70, 18, 80, { fill: C.grey })), circle(410, 200, 25, { fill: C.steel }), line(350, 165, 470, 165, { stroke: C.red, dash: '4 3', width: 1 }), dim(478, 160, 478, 200, 'dist.', { size: 10, side: -1 }), note(410, 250, 'opening', { anchor: 'middle', size: 10 }),
      caption(500, 320, 'Rule of thumb: a finger reaches 1/2 in; a hand 4 in; an arm 30 in.')], { title: 'Guard opening chart' }))
}

// ---------- CG and skates ----------
fig('installation/cg-and-skates.svg', 'Moving on skates: find the centre of gravity, keep it inside the skate footprint, push low and steer with a bar',
  svg(500, 250, [
    rect(80, 60, 300, 120, { fill: C.grey }), rect(80, 60, 140, 120, { fill: C.steel }), circle(170, 130, 10, { fill: C.paper, stroke: C.red, width: 2 }), text(170, 134, 'CG', { anchor: 'middle', size: 9, weight: 700, fill: C.red }),
    ...[110, 350].map((x) => [rect(x - 30, 180, 60, 16, { fill: C.steelDark, rx: 3 }), circle(x - 18, 200, 5, { fill: C.ink }), circle(x + 18, 200, 5, { fill: C.ink })]),
    line(80, 210, 380, 210, { width: 1, arrow: 'both', stroke: C.blue }), text(230, 226, 'skate footprint: CG must stay inside it, on slopes too', { anchor: 'middle', size: 10.5, fill: C.blue }),
    line(170, 60, 170, 180, { dash: '4 3', width: 1, stroke: C.red }),
    line(400, 170, 460, 170, { width: 3, arrow: 'end' }), note(430, 160, 'push low', { anchor: 'middle', size: 10 }),
    note(170, 48, 'heavy end: motor, gearbox, castings', { anchor: 'middle', size: 10 }),
    caption(500, 250, 'Chock before anyone puts a hand near; never ride a skate; watch the toes.'),
  ], { title: 'Centre of gravity on skates' }))

// ---------- Optical level ----------
fig('installation/optical-level-and-wire.svg', 'Optical level: one line of sight, staff readings give the elevation difference; piano wire sags by a known amount at mid-span',
  svg(500, 260, [
    text(130, 22, 'Optical level', { anchor: 'middle', weight: 700 }),
    rect(20, 150, 230, 12, { fill: C.grey }), poly([[60, 150], [80, 110], [100, 150]], { fill: C.steelDark }), rect(66, 100, 28, 12, { fill: C.blue, rx: 2 }),
    line(94, 106, 240, 106, { stroke: C.red, width: 1, dash: '5 3' }), rect(160, 60, 6, 90, { fill: C.paper, stroke: C.ink }), rect(225, 40, 6, 110, { fill: C.paper, stroke: C.ink }),
    ...[0, 1, 2, 3, 4].map((i) => [line(160, 70 + i * 18, 166, 70 + i * 18, { width: 1 }), line(225, 50 + i * 22, 231, 50 + i * 22, { width: 1 })]),
    note(163, 180, 'reads 4.20', { anchor: 'middle', size: 10 }), note(228, 180, 'reads 4.26', { anchor: 'middle', size: 10 }), note(130, 205, 'pad B is 0.06 lower than pad A', { anchor: 'middle', size: 10.5 }),
    text(375, 22, 'Piano wire', { anchor: 'middle', weight: 700 }),
    ...[290, 460].map((x) => rect(x - 6, 80, 12, 90, { fill: C.grey })), path('M290,90 Q375,118 460,90', { stroke: C.ink, width: 1.2 }), line(290, 90, 460, 90, { dash: '4 3', width: 0.8, stroke: C.muted }),
    dim(375, 90, 375, 104, 'sag', { size: 10, side: -1 }), note(375, 190, 'sag = w L² ÷ (8 T): known from tables\nfor the wire size, span and weight;\nmeasure to the wire with a mic, add the sag', { anchor: 'middle', size: 10 }),
    caption(500, 260, 'Both need a steady instrument, no heat shimmer and the same reader each time.'),
  ], { title: 'Optical level and piano wire' }))
