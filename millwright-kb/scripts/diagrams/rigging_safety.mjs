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
