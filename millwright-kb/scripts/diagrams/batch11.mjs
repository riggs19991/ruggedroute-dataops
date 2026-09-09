import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, hatchRect, leader, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- Single-plane balancing vectors ----------
{
  const cx = 115, cy = 155, sc = 8 // px per mil
  const pt = (m, a) => [cx + m * sc * Math.cos(-a * P), cy + m * sc * Math.sin(-a * P)]
  const O = pt(8, 40), OT = pt(11, 100)
  fig('condition-monitoring/single-plane-balancing-vectors.svg', 'Single-plane vector method: original O, original plus trial O+T, the trial effect T; move the trial weight by the angle from T to −O and scale it by O ÷ T',
    svg(500, 300, [
      circle(cx, cy, 98, { fill: C.grey, stroke: C.line, width: 1 }), line(cx - 102, cy, cx + 102, cy, { stroke: C.line, width: 1 }), line(cx, cy - 102, cx, cy + 102, { stroke: C.line, width: 1 }),
      text(cx + 105, cy + 4, '0°', { size: 10, fill: C.muted }), text(cx + 8, cy - 104, '90°', { size: 10, fill: C.muted }),
      line(cx, cy, O[0], O[1], { width: 2.5, arrow: 'end', stroke: C.ink }), text(O[0] - 44, O[1] + 42, 'O = 8 at 40°', { size: 11, weight: 700, anchor: 'middle' }),
      line(cx, cy, OT[0], OT[1], { width: 2.5, arrow: 'end', stroke: C.blue }), text(14, 30, 'O+T = 11 mils at 100°', { size: 11, weight: 700, fill: C.blue }),
      line(O[0], O[1], OT[0], OT[1], { width: 2.5, arrow: 'end', stroke: C.red }), text((O[0] + OT[0]) / 2 + 8, (O[1] + OT[1]) / 2 + 2, 'T', { size: 13, weight: 700, fill: C.red }),
      text(240, 50, '1. Run: read O (amplitude, phase)', { size: 10.5 }),
      text(240, 68, '2. Add trial weight W at 0°, run: read O+T', { size: 10.5 }),
      text(240, 86, '3. Draw both from centre; T joins O to O+T', { size: 10.5 }),
      text(240, 112, 'correction weight = W × O ÷ T', { size: 12, weight: 700 }),
      text(240, 130, 'move it from the trial position by the', { size: 10.5 }),
      text(240, 146, 'angle that turns T to point opposite O', { size: 10.5 }),
      text(240, 176, 'example: W = 10 g, O = 8, T = 11.6', { size: 10.5, fill: C.muted }),
      text(240, 192, '→ 6.9 g, shifted 108° against rotation', { size: 10.5, fill: C.muted }),
      note(240, 222, 'same phase reference (tape mark and\ntach) for every run; remove the trial\nweight before fitting the correction', { size: 10 }),
      caption(500, 300, 'Angles are measured against rotation on most analyzers; check yours.'),
    ], { title: 'Single-plane balancing vectors' }))
}

// ---------- Bearing defect frequencies ----------
fig('condition-monitoring/bearing-defect-frequencies.svg', 'The four bearing defect frequencies and the rule-of-thumb multiples of shaft speed; a defect shows as a family of harmonics, not a single peak',
  svg(500, 300, [
    circle(110, 110, 80, { fill: C.steel }), circle(110, 110, 62, { fill: C.paper }), circle(110, 110, 44, { fill: C.steel }), circle(110, 110, 30, { fill: C.paper }),
    ...[0, 45, 90, 135, 180, 225, 270, 315].map((a) => circle(110 + 53 * Math.cos(a * P), 110 + 53 * Math.sin(a * P), 9, { fill: C.grey })),
    circle(110, 110, 53, { fill: 'none', stroke: C.accentDark, dash: '3 3', width: 1 }),
    leader(110, 32, 200, 26, 'BPFO outer race', { size: 11, fill: C.red }), leader(146, 84, 200, 60, 'BPFI inner race', { size: 11, fill: C.blue }),
    leader(163, 110, 200, 94, 'BSF ball spin', { size: 11, fill: C.green }), leader(110, 163, 200, 128, 'FTF cage', { size: 11, fill: C.accentDark }),
    table(230, 140, [['fault', 'rule of thumb (n balls)', 'sidebands'], ['BPFO', 'n × rpm × 0.4', 'none'], ['BPFI', 'n × rpm × 0.6', '± 1× rpm'], ['BSF', '(rpm × 1.7 to 2.4) ÷ 2', '± FTF'], ['FTF', 'rpm × 0.38 to 0.42', 'none']], [50, 130, 80], { rowH: 19, size: 10 }),
    // spectrum sketch
    rect(40, 210, 190, 70, { fill: C.paper, stroke: C.line }), line(40, 270, 230, 270, { width: 1 }),
    line(60, 270, 60, 232, { width: 2, stroke: C.ink }), text(60, 226, '1×', { size: 9, anchor: 'middle' }),
    ...[0, 1, 2, 3].map((i) => line(92 + i * 34, 270, 92 + i * 34, 258 - i * 0 + i * 4, { width: 2, stroke: C.red })),
    text(160, 226, 'BPFO harmonics', { size: 9, anchor: 'middle', fill: C.red }),
    note(250, 250, 'defect frequencies are not whole\nmultiples of shaft speed: that is\nhow you tell them from looseness', { size: 10 }),
    caption(500, 300, 'Use the bearing number and the analyzer database for exact values.'),
  ], { title: 'Bearing defect frequencies' }))

// ---------- Bevel contact pattern ----------
{
  const tooth = (x, y, label, px, py, pw, ph, fix) => [
    rect(x, y, 120, 50, { fill: C.steel, stroke: C.ink }), text(x + 8, y + 12, 'toe', { size: 9, fill: C.muted }), text(x + 112, y + 12, 'heel', { size: 9, fill: C.muted, anchor: 'end' }),
    rect(x + px, y + py, pw, ph, { fill: C.accent, rx: 6, opacity: 0.9 }),
    text(x + 60, y + 66, label, { size: 11, anchor: 'middle', weight: 700 }), text(x + 60, y + 80, fix, { size: 10, anchor: 'middle', fill: C.blue }),
  ]
  fig('gearboxes/bevel-contact-pattern.svg', 'Reading a bevel gear contact pattern: centred is correct; toe or heel means move the gear; tip or root means move the pinion',
    svg(500, 300, [
      text(250, 22, 'Marking compound on the gear teeth, pinion rolled through under light load', { size: 11, anchor: 'middle', fill: C.muted }),
      ...tooth(30, 40, 'correct', 24, 14, 70, 22, 'centred, 60 to 80% of face'),
      ...tooth(190, 40, 'toward toe', 4, 14, 60, 22, 'move gear away'),
      ...tooth(350, 40, 'toward heel', 56, 14, 60, 22, 'move gear in'),
      ...tooth(30, 150, 'high (tip)', 24, 4, 70, 18, 'pinion in (deeper)'),
      ...tooth(190, 150, 'low (root)', 24, 28, 70, 18, 'pinion out'),
      ...tooth(350, 150, 'crossed (bias)', 10, 8, 100, 34, 'check housing bores'),
      caption(500, 300, 'Each move changes backlash and preload: re-check both after every shim.'),
    ], { title: 'Bevel contact pattern' }))
}

// ---------- Service factor selection flow ----------
fig('gearboxes/service-factor-selection.svg', 'Reducer selection in five checks: motor power × service factor, mechanical rating, thermal rating, ratio and overhung load',
  svg(500, 320, [
    box(30, 30, 200, 44, 'motor hp × service factor\n= required rating', { fill: C.blueSoft, stroke: C.blue, size: 11, weight: 700 }),
    table(250, 30, [['load', '≤ 10 h', '> 10 h'], ['uniform', '1.00', '1.25'], ['moderate', '1.25', '1.50'], ['heavy shock', '1.50', '1.75']], [90, 55, 55], { rowH: 18, size: 10 }),
    line(130, 74, 130, 96, { width: 1.5, arrow: 'end' }),
    box(30, 96, 200, 36, 'mechanical rating ≥ required?', { size: 11 }), line(130, 132, 130, 152, { width: 1.5, arrow: 'end' }),
    box(30, 152, 200, 36, 'thermal rating ≥ motor hp?', { size: 11 }), line(130, 188, 130, 208, { width: 1.5, arrow: 'end' }),
    box(30, 208, 200, 36, 'ratio = input ÷ output rpm', { size: 11 }), line(130, 244, 130, 264, { width: 1.5, arrow: 'end' }),
    box(30, 264, 200, 30, 'overhung load ≤ allowable', { size: 11 }),
    note(250, 130, 'no → next size up\n(gears and bearings)', { size: 10 }),
    note(250, 178, 'no → fan, cooler, bigger box\n(worm boxes fail here first)', { size: 10 }),
    note(250, 234, 'pick nearest catalogue ratio;\ntrim with the belt drive', { size: 10 }),
    note(250, 278, 'OHL = 126,000 × hp × K ÷ (rpm × PD)', { size: 10 }),
    caption(500, 320, 'Select on whichever of mechanical and thermal rating is smaller.'),
  ], { title: 'Service factor selection' }))

// ---------- Pump curve sheet anatomy ----------
{
  const ch = chart({ x: 60, y: 40, w: 330, h: 190, xmin: 0, xmax: 1200, ymin: 0, ymax: 300, xticks: [0, 400, 800, 1200], yticks: [0, 100, 200, 300], xlabel: 'Flow (US gpm)', ylabel: 'Head (ft)' })
  const curve = (h0, k, end) => { const pts = []; for (let q = 0; q <= end; q += 50) pts.push(`${ch.sx(q)},${ch.sy(h0 - k * q * q)}`); return 'M' + pts.join(' L') }
  const eff = (r, dx, dy) => `M${ch.sx(650 + dx)},${ch.sy(150 + dy)} m-${r},0 a${r},${r * 0.55} 0 1,0 ${2 * r},0 a${r},${r * 0.55} 0 1,0 -${2 * r},0`
  fig('manuals/pump-curve-sheet-anatomy.svg', 'A manufacturer curve sheet: head-capacity curves per impeller diameter, efficiency islands, BEP, power lines and the NPSHr curve along the bottom',
    svg(500, 300, [
      ch.el,
      path(curve(280, 0.00012, 1150), { width: 2 }), path(curve(235, 0.00011, 1050), { width: 2 }), path(curve(190, 0.0001, 950), { width: 2 }),
      text(ch.sx(30), ch.sy(280) + 13, '13 in', { size: 9 }), text(ch.sx(30), ch.sy(235) + 13, '12 in', { size: 9 }), text(ch.sx(30), ch.sy(190) + 13, '11 in', { size: 9 }),
      path(eff(70, 0, 40), { stroke: C.green, width: 1 }), path(eff(40, 0, 40), { stroke: C.green, width: 1 }), text(ch.sx(650), ch.sy(190) + 4, '78%', { size: 9, anchor: 'middle', fill: C.green }),
      circle(ch.sx(700), ch.sy(280 - 0.00012 * 700 * 700), 5, { fill: C.red, stroke: C.red }),
      path(`M${ch.sx(0)},${ch.sy(20)} Q${ch.sx(800)},${ch.sy(25)} ${ch.sx(1150)},${ch.sy(75)}`, { stroke: C.accentDark, width: 1.5, dash: '5 3' }),
      line(ch.sx(200), ch.sy(35), ch.sx(1100), ch.sy(110), { stroke: C.blue, width: 1, dash: '2 3' }), line(ch.sx(200), ch.sy(20), ch.sx(1100), ch.sy(80), { stroke: C.blue, width: 1, dash: '2 3' }),
      callout(1, ch.sx(300), ch.sy(269)), callout(2, ch.sx(650), ch.sy(150)), callout(3, ch.sx(700) + 14, ch.sy(220) - 14), callout(4, ch.sx(1000), ch.sy(60)), callout(5, ch.sx(950), ch.sy(105)),
      legend(372, 48, ['shut-off head', 'efficiency islands', 'BEP: 70 to 120%', 'NPSHr curve', 'power (bhp) lines'], { size: 9.5, gap: 16 }),
      note(392, 214, 'header: 3x4-13,\n1750 rpm, curve no.,\nwater at 20 °C', { size: 9.5 }),
      caption(500, 300, 'Find your head on the gauges, cross to your impeller diameter, read the flow.'),
    ], { title: 'Pump curve sheet anatomy' }))
}

// ---------- Bearing catalogue row ----------
fig('manuals/bearing-catalogue-row.svg', 'One row of a bearing catalogue table: dimensions, dynamic and static ratings, fatigue limit, speeds, mass and the designations',
  svg(500, 250, [
    table(20, 40, [['d', 'D', 'B', 'C', 'C0', 'Pu', 'ref.', 'limit', 'kg', 'designation'], ['25', '52', '15', '14.8', '7.8', '0.335', '28000', '18000', '0.13', '6205 · -2RS1 · -2Z']], [34, 34, 30, 42, 40, 44, 50, 46, 34, 106], { rowH: 22, size: 10 }),
    callout(1, 60, 100), callout(2, 160, 100), callout(3, 215, 100), callout(4, 320, 100), callout(5, 380, 100), callout(6, 440, 100),
    legend(20, 130, ['bore, OD, width in mm (ISO: any brand fits)', 'C: dynamic rating, kN; C0: static rating, kN', 'Pu: fatigue load limit', 'reference and limiting speed, rpm', 'mass', 'open, sealed (2RS), shielded (2Z) variants'], { size: 10.5, gap: 16 }),
    caption(500, 250, 'L10 = (C ÷ P)³ million rev for balls; exponent 10/3 for rollers.'),
  ], { title: 'Bearing catalogue row' }))

// ---------- Belt drive selection steps ----------
fig('manuals/belt-selection-steps.svg', 'V-belt drive selection from the catalogue: design hp, belt section, sheave diameters, belt length, hp per belt with arc and length corrections, belt count',
  svg(500, 320, [
    ...[
      ['1. design hp = motor hp × SF', '30 × 1.3 = 39'],
      ['2. section chart (hp vs rpm)', '5V'],
      ['3. sheave diameters, ratio', '7.1 and 14.0 in'],
      ['4. belt length at centres', '36 in → 5V850'],
      ['5. hp per belt + ratio add', '10.5 + 0.8 = 11.3'],
      ['6. × arc × length factors', '× 0.97 × 0.98 = 10.7'],
      ['7. belts = design ÷ per belt', '39 ÷ 10.7 → 4 belts'],
    ].flatMap(([a, b], i) => [box(20, 24 + i * 34, 230, 28, a, { size: 10.5, fill: i === 6 ? C.greenSoft : C.grey, stroke: i === 6 ? C.green : C.ink }), text(262, 42 + i * 34, b, { size: 11, weight: 700, fill: C.blue })]),
    // arc of contact sketch
    circle(400, 110, 22, { fill: C.steel }), circle(460, 110, 40, { fill: C.steel }),
    line(392, 89, 445, 72, { width: 2.5 }), line(392, 131, 445, 148, { width: 2.5 }), arc(400, 110, 22, 110, 250, { width: 2.5 }), arc(460, 110, 40, -70, 70, { width: 2.5 }),
    arc(400, 110, 30, 110, 250, { stroke: C.red, width: 1.5 }), text(362, 182, 'arc < 180° on small sheave', { size: 9.5, anchor: 'start', fill: C.red }),
    note(420, 198, 'factor 0.99 at 170°,\n0.95 at 150°, 0.89 at 130°', { size: 9, anchor: 'middle' }),
    note(400, 282, 'matched belt set,\nsame groove count sheaves', { size: 9.5, anchor: 'middle' }),
    caption(500, 320, 'Round belt count up; one belt short overloads the whole set.'),
  ], { title: 'Belt selection steps' }))

// ---------- Glossary lookup ----------
fig('study/glossary-lookup.svg', 'How to use the glossary: find the term, read the one-line definition, then search the app for the full article',
  svg(500, 150, [
    box(20, 40, 130, 60, 'hear a term\non the floor', { size: 11 }), line(150, 70, 180, 70, { width: 1.5, arrow: 'end' }),
    box(180, 40, 140, 60, 'glossary: one-line\ndefinition', { size: 11, fill: C.blueSoft, stroke: C.blue }), line(320, 70, 350, 70, { width: 1.5, arrow: 'end' }),
    box(350, 40, 130, 60, 'search box →\nfull article', { size: 11, fill: C.greenSoft, stroke: C.green }),
    caption(500, 150, 'Use your browser find (Ctrl+F) to jump to a word on this page.'),
  ], { title: 'Glossary lookup' }))
