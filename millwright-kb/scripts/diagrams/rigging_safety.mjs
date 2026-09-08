import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- Hoist inspection points ----------
fig('rigging/hoist-inspection-points.svg', 'Chain hoist inspection: capacity plate, top and bottom hooks with latches, load chain links, hand chain, brake test, hook throat opening',
  svg(500, 320, [
    path('M250,20 q-14,14 -6,30 q10,14 22,0 q8,-16 -6,-30', { fill: C.steelDark }), rect(200, 60, 100, 70, { fill: C.grey, rx: 10 }), rect(215, 130, 70, 12, { fill: C.steelDark }),
    ...Array.from({ length: 7 }, (_, i) => rect(236, 142 + i * 14, 12, 12, { fill: 'none', stroke: C.ink, rx: 4 })), path('M242,240 q-14,14 -6,30 q10,14 22,0 q8,-16 -6,-30', { fill: C.steelDark }), line(250, 258, 262, 268, { stroke: C.red, width: 2 }),
    ...Array.from({ length: 12 }, (_, i) => circle(300, 140 + i * 12, 4, { fill: 'none', stroke: C.muted })),
    ...[[1, 250, 90], [2, 250, 40], [3, 242, 200], [4, 300, 120], [5, 260, 285], [6, 200, 60]].map(([n, x, y]) => callout(n, x, y, { r: 8 })),
    legend(20, 40, ['capacity plate legible;\nrating ≥ the load', 'top hook: latch works,\nno twist, no stretch', 'load chain: no stretch,\nnicks, twist; oiled', 'hand chain and gears\nrun free both ways', 'bottom hook throat:\nscrap if opened > 5%', 'brake: lift, stop,\nno creep'], { size: 10, gap: 14 }),
    caption(500, 320, 'Two-fall hoists: check the bottom block is not capsized (chain twisted).'),
  ], { title: 'Hoist inspection points' }))

// ---------- Crane hand signals ----------
{
  const fig1 = (x, y, pose) => {
    const out = [circle(x, y - 40, 9, { fill: C.grey }), line(x, y - 31, x, y + 5, { width: 3 }), line(x, y + 5, x - 12, y + 35, { width: 3 }), line(x, y + 5, x + 12, y + 35, { width: 3 })]
    for (const [ax, ay, bx, by] of pose) out.push(line(x + ax, y + ay, x + bx, y + by, { width: 3 }))
    return out
  }
  const signals = [['Hoist', [[0, -25, 18, -55]], (x, y) => [circle(x + 18, y - 62, 8, { fill: 'none', stroke: C.blue, dash: '3 2' }), text(x + 32, y - 60, '☝', { size: 10 })]],
    ['Lower', [[0, -25, 18, 5]], (x, y) => [circle(x + 18, y + 12, 8, { fill: 'none', stroke: C.blue, dash: '3 2' })]],
    ['Raise boom', [[0, -25, 28, -25]], (x, y) => [text(x + 34, y - 22, '👍', { size: 12 })]],
    ['Lower boom', [[0, -25, 28, -25]], (x, y) => [text(x + 34, y - 22, '👎', { size: 12 })]],
    ['Stop', [[0, -25, 28, -25]], (x, y) => [line(x + 20, y - 34, x + 36, y - 34, { stroke: C.blue, width: 1, arrow: 'both' })]],
    ['Emergency stop', [[0, -25, 28, -25], [0, -25, -28, -25]], (x, y) => [line(x + 20, y - 34, x + 36, y - 34, { stroke: C.red, width: 1, arrow: 'both' }), line(x - 36, y - 34, x - 20, y - 34, { stroke: C.red, width: 1, arrow: 'both' })]],
    ['Swing', [[0, -25, 30, -30]], (x, y) => [line(x + 30, y - 30, x + 42, y - 30, { width: 1.5, arrow: 'end', stroke: C.blue })]],
    ['Dog everything', [[0, -25, 10, -10], [0, -25, -10, -10]], (x, y) => [circle(x, y - 10, 5, { fill: C.steelDark })]]]
  fig('rigging/crane-hand-signals.svg', 'Standard crane hand signals: hoist, lower, raise boom, lower boom, stop, emergency stop, swing, dog everything',
    svg(500, 300, [...signals.map(([n, pose, extra], i) => { const x = 65 + (i % 4) * 122, y = 80 + Math.floor(i / 4) * 135; return [...fig1(x, y, pose), ...extra(x, y), text(x, y + 52, n, { anchor: 'middle', size: 11, weight: 600 })] }),
      caption(500, 300, 'Hoist: finger up, circles. Lower: finger down. Stop: palm down, arm swept.')], { title: 'Crane hand signals' }))
}

// ---------- Box crib ----------
fig('rigging/box-crib.svg', 'Box crib: two or three timbers per layer at the outside edges, layers crossed 90°, height no more than three times the base width',
  svg(500, 240, [
    text(110, 22, '2 × 2 crib (top view)', { anchor: 'middle', weight: 700, size: 12 }), ...[0, 1].map((i) => rect(40, 50 + i * 100, 140, 24, { fill: '#c9a46b', stroke: '#8b5a2b' })), ...[0, 1].map((i) => rect(50 + i * 100, 40, 24, 140, { fill: '#e8d3a3', stroke: '#8b5a2b' })),
    note(110, 200, '4 crossing points\n4x4: 24,000 lb · 6x6: 60,000 lb', { anchor: 'middle', size: 10 }),
    text(300, 22, '3 × 3 crib', { anchor: 'middle', weight: 700, size: 12 }), ...[0, 1, 2].map((i) => rect(230, 50 + i * 50, 140, 24, { fill: '#c9a46b', stroke: '#8b5a2b' })), ...[0, 1, 2].map((i) => rect(240 + i * 50, 40, 24, 140, { fill: '#e8d3a3', stroke: '#8b5a2b' })),
    note(300, 200, '9 crossing points\n4x4: 55,000 lb · 6x6: 136,000 lb', { anchor: 'middle', size: 10 }),
    text(440, 22, 'Side', { anchor: 'middle', weight: 700, size: 12 }), ...[0, 1, 2, 3, 4, 5].map((i) => rect(410, 160 - i * 20, 60, 18, { fill: i % 2 ? '#c9a46b' : '#e8d3a3', stroke: '#8b5a2b' })), dim(478, 40, 478, 178, 'H ≤ 3W', { size: 9.5, side: -1 }), dim(410, 190, 470, 190, 'W', { size: 10 }),
    caption(500, 240, 'Timbers at the edges, full contact, no overhang, wedges in pairs on top.'),
  ], { title: 'Box crib' }))

// ---------- Sling angles and hitches ----------
fig('rigging/sling-angles-and-hitches.svg', 'Sling angle multiplies leg tension: 60° × 1.15, 45° × 1.41, 30° × 2.0; vertical, choker (80%) and basket (200%) hitches',
  svg(500, 300, [
    text(130, 22, 'Sling angle (from horizontal)', { anchor: 'middle', weight: 700, size: 12 }), rect(40, 150, 180, 30, { fill: C.grey }),
    ...[[60, C.green, '60°: × 1.15'], [45, C.accentDark, '45°: × 1.41'], [30, C.red, '30°: × 2.00']].map(([a, c, l], i) => { const h = 60 * Math.tan(a * P); return [line(70, 150, 130, 150 - h, { stroke: c, width: 2 }), line(190, 150, 130, 150 - h, { stroke: c, width: 2 }), note(196, 150 - h + 4, l, { size: 10, fill: c, anchor: 'start' })] }),
    line(40, 150, 220, 150, { dash: '3 3', width: 1, stroke: C.muted }), note(130, 200, 'leg tension = (load ÷ legs) × factor\n2,000 lb on two legs at 30° = 2,000 lb per leg', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Hitches', { anchor: 'middle', weight: 700, size: 12 }),
    ...[['Vertical\n100%', (x) => [line(x, 50, x, 110, { width: 3 }), rect(x - 20, 110, 40, 30, { fill: C.grey })]], ['Choker\n80%', (x) => [line(x + 6, 50, x + 6, 100, { width: 3 }), path(`M${x + 6},100 L${x - 22},112 L${x - 22},140 L${x + 22},140 L${x + 22},112 L${x + 6},100`, { width: 3, fill: 'none' }), rect(x - 20, 110, 40, 30, { fill: C.grey })]], ['Basket\n200%', (x) => [line(x - 14, 50, x - 14, 140, { width: 3 }), line(x + 14, 50, x + 14, 140, { width: 3 }), line(x - 14, 140, x + 14, 140, { width: 3 }), rect(x - 20, 110, 40, 30, { fill: C.grey })]]]
      .map(([n, d], i) => { const x = 300 + i * 70; return [...d(x), text(x, 170, n, { anchor: 'middle', size: 10, weight: 600 })] }),
    note(370, 215, 'choker angle under 120° derates further;\nbasket needs D/d ≥ 25 for full rating', { anchor: 'middle', size: 9.5 }),
    caption(500, 300, 'Nothing is rated below 30°. Read the tag for the hitch you are using.'),
  ], { title: 'Sling angles and hitches' }))

// ---------- Shackle loading ----------
fig('rigging/shackle-loading.svg', 'Shackle loading: the running sling in the bow, the fixed eye or hook on the pin; side loads derate 45° to 70% and 90° to 50%; mouse the pin',
  svg(500, 230, [
    ...[['Right', C.green, 0], ['Side load 45°: 70%', C.accentDark, 45], ['Side load 90°: 50%', C.red, 90]].map(([n, c, a], i) => { const x = 90 + i * 160, y = 120; return [path(`M${x - 25},${y + 20} L${x - 25},${y - 10} A25,25 0 0 1 ${x + 25},${y - 10} L${x + 25},${y + 20}`, { width: 8, stroke: C.steelDark }), rect(x - 32, y + 16, 64, 8, { fill: C.ink }), g([line(0, 0, 0, -70, { stroke: c, width: 4 })], { transform: `translate(${x},${y - 30}) rotate(${-a})` }), text(x, 190, n, { anchor: 'middle', size: 10.5, weight: 600, fill: c })] }),
    note(250, 40, 'sling bears on the bow, load pulls along the shackle axis', { anchor: 'middle', size: 10 }),
    caption(500, 230, 'WLL forged on the bow; two slings in one bow: 120° included angle max.'),
  ], { title: 'Shackle loading' }))

// ---------- Confined space roles ----------
fig('safety/confined-space-setup.svg', 'Confined space entry: tested atmosphere, blower ducted to the bottom, entrant on a harness and retrieval line, attendant at the opening, supervisor with the permit, rescue on call',
  svg(500, 300, [
    rect(120, 100, 260, 160, { fill: C.grey }), rect(220, 80, 60, 20, { fill: C.steelDark }), rect(228, 60, 44, 20, { fill: C.paper, stroke: C.ink }),
    path('M250,20 L250,62', { width: 2 }), path('M200,20 L300,20 L250,62 Z', { fill: 'none', width: 2 }), circle(250, 30, 6, { fill: C.steelDark }), line(250, 62, 250, 170, { width: 1.5, stroke: C.blue }),
    circle(250, 180, 10, { fill: C.grey }), line(250, 190, 250, 225, { width: 3 }), line(250, 205, 232, 220, { width: 3 }), line(250, 205, 268, 220, { width: 3 }), rect(244, 192, 12, 20, { fill: C.accent }),
    rect(40, 120, 50, 40, { fill: C.blueSoft, stroke: C.blue, rx: 4 }), path('M90,140 L120,140 L130,250', { stroke: C.blue, width: 6, fill: 'none' }), line(135, 250, 160, 250, { stroke: C.blue, width: 3, arrow: 'end' }),
    circle(320, 50, 8, { fill: C.grey }), line(320, 58, 320, 80, { width: 3 }), rect(340, 40, 30, 20, { fill: C.greenSoft, stroke: C.green }), text(355, 54, '20.9', { anchor: 'middle', size: 8 }),
    ...[[1, 250, 22 - 12], [2, 65, 105], [3, 250, 235], [4, 320, 30], [5, 410, 120]].map(([n, x, y]) => callout(n, x, y, { r: 8 })),
    legend(392, 140, ['tripod + winch', 'blower to bottom', 'entrant: harness,\nmonitor', 'attendant: never\nenters', 'permit, rescue'], { size: 9, gap: 13 }),
    caption(500, 300, 'Oxygen 19.5-23.5%, LEL under 10%, H2S under 10 ppm, CO under 25 ppm.'),
  ], { title: 'Confined space setup' }))

// ---------- Fall clearance ----------
fig('safety/fall-clearance-and-ladder.svg', 'Fall clearance with a 6 ft lanyard: lanyard 6 + deceleration 3.5 + harness stretch 1 + worker below D-ring 5 + safety 3 = 18.5 ft below the anchor; ladder at 4:1',
  svg(500, 300, [
    text(130, 22, 'Fall clearance', { anchor: 'middle', weight: 700 }), rect(40, 40, 200, 12, { fill: C.steelDark }), circle(70, 46, 5, { fill: C.accent }),
    ...[[52, 100, '6 ft lanyard', C.ink], [100, 128, '3.5 ft deceleration', C.red], [128, 136, '1 ft stretch', C.accentDark], [136, 176, '5 ft to feet', C.blue], [176, 200, '3 ft safety', C.green]].map(([y1, y2, l, c]) => [line(70, y1, 70, y2, { stroke: c, width: 4 }), line(90, y1, 90, y2, { width: 1, arrow: 'both', stroke: c }), text(98, (y1 + y2) / 2 + 4, l, { size: 10, fill: c })]),
    line(40, 200, 240, 200, { width: 2 }), text(130, 222, '18.5 ft anchor to obstruction', { anchor: 'middle', size: 11, weight: 700 }), note(130, 240, 'anchor at the feet adds up to 6 ft more;\nuse an overhead anchor or an SRL', { anchor: 'middle', size: 9.5 }),
    text(380, 22, 'Ladder angle 4:1', { anchor: 'middle', weight: 700 }), rect(430, 40, 12, 200, { fill: C.grey }), line(310, 240, 430, 40, { width: 4, stroke: '#8b5a2b' }), line(322, 246, 442, 46, { width: 4, stroke: '#8b5a2b' }), ...[0, 1, 2, 3, 4, 5, 6].map((i) => line(310 + i * 17.1 + 3, 240 - i * 28.6, 322 + i * 17.1 + 3, 246 - i * 28.6, { width: 3, stroke: '#8b5a2b' })),
    dim(310, 262, 430, 262, '1 out', { size: 10 }), dim(470, 40, 470, 240, '4 up', { size: 10 }), note(380, 288, '3 ft above the landing; tie off the top', { anchor: 'middle', size: 9.5 }),
  ], { title: 'Fall clearance and ladder' }))

// ---------- First aid priorities ----------
fig('safety/first-aid-priorities.svg', 'First minute: make the scene safe, call, stop severe bleeding, start CPR and get the AED, then treat and keep warm',
  svg(500, 200, [
    ...[['1 Scene safe:\nisolate, lockout', C.grey], ['2 Call 911 /\nsite number', C.redSoft], ['3 Bleeding: press,\ntourniquet', C.redSoft], ['4 Not breathing\nCPR + AED', C.redSoft], ['5 Treat, warm,\nmonitor, record', C.greenSoft]].map(([n, c], i) => box(12 + i * 96, 50, 90, 60, n, { fill: c, size: 9.5 })),
    ...[0, 1, 2, 3].map((i) => line(102 + i * 96, 80, 108 + i * 96, 80, { width: 2, arrow: 'end' })),
    note(250, 140, 'tourniquet: 2-3 in above the wound, not on a joint, tight until it stops; note the time', { anchor: 'middle', size: 9.5 }),
    note(250, 158, 'eyes: flush 15 min; burns: cool water 20 min; injection injury and electric shock: hospital', { anchor: 'middle', size: 10 }),
    caption(500, 200, 'Amputated part: moist gauze, sealed bag, on ice, never in water.'),
  ], { title: 'First aid priorities' }))

// ---------- Grinder guard and kickback ----------
fig('safety/grinder-guard-and-kickback.svg', 'Angle grinder: guard between the wheel and you, side handle on, wheel rated above the grinder rpm; cut so the kerf opens and the grinder cannot kick into your body',
  svg(500, 240, [
    rect(60, 90, 180, 40, { fill: C.grey, rx: 12 }), rect(40, 96, 30, 28, { fill: C.steelDark, rx: 4 }), circle(280, 110, 45, { fill: C.steel, stroke: C.steelDark, width: 3 }), path('M235,110 A45,45 0 0 1 325,110', { stroke: C.ink, width: 10, fill: 'none' }), rect(150, 60, 10, 30, { fill: C.steelDark }),
    note(280, 40, 'guard covers the top half,\nrotated toward you', { anchor: 'middle', size: 10 }), note(155, 50, 'side handle', { anchor: 'middle', size: 10 }),
    arc(280, 110, 55, 20, 120, { stroke: C.red, width: 2, arrow: 'end' }), note(340, 180, 'kickback direction:\nstand out of it', { anchor: 'middle', size: 10, fill: C.red }),
    note(120, 175, 'wheel rpm rating ≥ grinder rpm;\nType 1 cut-off wheel = closed guard;\nno lock-on trigger for cutting', { anchor: 'middle', size: 10 }),
    caption(500, 240, 'Sparks go down and away from you, gas bottles and rags.'),
  ], { title: 'Grinder guard and kickback' }))

// ---------- Hot work zone ----------
fig('safety/hot-work-zone.svg', 'Hot work zone: 35 ft (11 m) radius cleared or covered, openings sealed, extinguisher and fire watch present, other side of walls checked',
  svg(500, 260, [
    circle(220, 130, 105, { fill: C.soft, stroke: C.accentDark, dash: '6 4' }), circle(220, 130, 8, { fill: C.accent, stroke: C.accentDark }), dim(220, 130, 325, 130, '35 ft', { size: 11 }),
    rect(150, 60, 30, 20, { fill: C.grey }), line(148, 58, 182, 82, { stroke: C.red, width: 2 }), note(165, 52, 'combustibles out', { anchor: 'middle', size: 9 }),
    rect(260, 180, 40, 14, { fill: C.steelDark }), note(280, 210, 'floor opening covered', { anchor: 'middle', size: 9 }),
    circle(330, 200, 8, { fill: C.grey }), line(330, 208, 330, 235, { width: 3 }), rect(342, 212, 10, 20, { fill: C.red }), note(340, 250, 'fire watch + extinguisher, 30-60 min after', { anchor: 'middle', size: 9.5 }),
    rect(50, 60, 12, 140, { fill: C.steelDark }), note(70, 215, 'wall: check the far side', { anchor: 'middle', size: 9 }), rect(380, 40, 100, 200, { fill: C.grey }), note(430, 140, 'welding blankets\non what cannot\nbe moved', { anchor: 'middle', size: 9.5 }),
  ], { title: 'Hot work zone' }))

// ---------- Lockout steps ----------
fig('safety/lockout-steps.svg', 'Lockout in order: notify, identify every energy source, shut down, isolate, lock and tag, release stored energy, verify zero energy, then work',
  svg(500, 220, [
    ...[['1 Notify', C.grey], ['2 Identify all\nenergy sources', C.grey], ['3 Shut down', C.grey], ['4 Isolate', C.blueSoft], ['5 Lock + tag', C.blueSoft], ['6 Release stored\nenergy', C.soft], ['7 Verify: try\nto start', C.redSoft], ['8 Work', C.greenSoft]].map(([n, c], i) => box(20 + (i % 4) * 118, 40 + Math.floor(i / 4) * 80, 108, 56, n, { fill: c, size: 10.5 })),
    ...[0, 1, 2].map((i) => [line(128 + i * 118, 68, 138 + i * 118, 68, { width: 2, arrow: 'end' }), line(128 + i * 118, 148, 138 + i * 118, 148, { width: 2, arrow: 'end' })]), path('M428,96 L428,110 L74,110 L74,120', { width: 2, arrow: 'end', fill: 'none' }),
    caption(500, 220, 'Electrical, hydraulic, pneumatic, gravity, springs, thermal: all of them.'),
  ], { title: 'Lockout steps' }))

// ---------- PPE by task ----------
fig('safety/ppe-by-task.svg', 'PPE by task at a glance',
  svg(500, 250, [table(20, 30, [['Task', 'Eyes / face', 'Ears', 'Hands', 'Lungs', 'Other'], ['Grinding', 'glasses + shield', 'yes', 'A4 cut', 'P100 long jobs', 'no loose clothes'], ['Arc welding', 'helmet + glasses', 'plugs', 'gauntlets', 'fume: P100 / PAPR', 'leathers, boots'], ['Rigging', 'glasses', '-', 'leather', '-', 'hard hat, Mt boot'], ['Hydraulics', 'shield when opening', '-', 'nitrile', '-', 'no hands on leaks'], ['Machining', 'glasses / shield', '-', 'NONE', '-', 'no rings, sleeves'], ['Chemicals', 'goggles + shield', '-', 'per SDS', 'per SDS', 'apron, eyewash']], [75, 100, 40, 60, 95, 100], { rowH: 24, size: 9 }), caption(500, 250, 'Z87+ glasses under every shield and helmet; no gloves on rotating tools.')], { title: 'PPE by task' }))
