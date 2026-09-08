import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- Belt tracking rules ----------
fig('conveyors/belt-tracking-rules.svg', 'Tracking rules: the belt runs toward the end of the idler it touches first; shift the idler in the direction of travel on the side the belt runs to',
  svg(500, 300, [
    text(250, 22, 'Top view of the carrying side', { anchor: 'middle', weight: 700 }),
    rect(60, 60, 380, 90, { fill: C.soft, stroke: C.accentDark }), line(60, 105, 440, 105, { dash: '6 4', width: 1, stroke: C.muted }), line(200, 40, 300, 40, { width: 2, arrow: 'end' }), note(250, 34, 'belt travel', { anchor: 'middle', size: 10 }),
    ...[120, 200, 360].map((x) => rect(x - 4, 55, 8, 100, { fill: C.steelDark })), g([rect(-4, -50, 8, 100, { fill: C.red })], { transform: 'translate(280,105) rotate(8)' }),
    line(284, 150, 330, 172, { stroke: C.red, width: 1.5, arrow: 'end' }), note(335, 170, 'idler end moved forward\non the side the belt\nruns toward', { size: 10, fill: C.red }),
    path('M60,105 Q200,105 300,80 Q380,64 440,70', { stroke: C.blue, width: 2, dash: '4 3' }), note(60, 172, 'belt steers back to centre', { size: 10, fill: C.blue }),
    note(250, 205, 'rule 1: an idler end moved forward (in the travel direction) steers the belt away', { anchor: 'middle', size: 10 }),
    note(250, 222, 'rule 2: fix the cause first: square pulleys, level structure, build-up, loading off-centre', { anchor: 'middle', size: 10 }),
    note(250, 239, 'adjust one idler a little, run 5 minutes, look again; work from tail to head', { anchor: 'middle', size: 10 }),
    caption(500, 300, 'Never adjust more than 1/8 in at a time; return idlers steer the return side.'),
  ], { title: 'Belt tracking rules' }))

// ---------- Belt end squaring ----------
fig('conveyors/belt-end-squaring.svg', 'Squaring a belt end by the centreline method: average of several width measurements gives the centreline; square across it, never off an edge',
  svg(500, 240, [
    rect(40, 60, 420, 120, { fill: C.soft, stroke: C.accentDark }), line(40, 120, 460, 120, { dash: '6 4', width: 1.5, stroke: C.blue }), note(250, 112, 'centreline from 5 width measurements', { anchor: 'middle', size: 10, fill: C.blue }),
    ...[100, 180, 260, 340, 420].map((x) => [line(x, 60, x, 180, { width: 0.8, stroke: C.muted }), circle(x, 120, 2.5, { fill: C.blue, stroke: 'none' })]),
    line(400, 58, 400, 182, { stroke: C.red, width: 2 }), note(400, 200, 'cut line square to the centreline', { anchor: 'middle', size: 10, fill: C.red }),
    rect(388, 100, 60, 40, { fill: 'none', stroke: C.ink, width: 1.5 }), note(418, 96, 'square', { anchor: 'middle', size: 9 }),
    caption(500, 240, 'Edges are never straight: a splice squared from an edge mistracks forever.'),
  ], { title: 'Belt end squaring' }))

// ---------- Nip points ----------
fig('conveyors/conveyor-nip-points.svg', 'Conveyor nip points: where the belt meets the head and tail pulleys, snub and bend pulleys, and every return idler',
  svg(500, 240, [
    circle(80, 120, 40, { fill: C.grey }), circle(420, 120, 40, { fill: C.grey }), line(80, 80, 420, 80, { width: 6 }), line(80, 160, 420, 160, { width: 6 }),
    ...[180, 250, 320].map((x) => circle(x, 168, 8, { fill: C.steelDark })), circle(140, 150, 12, { fill: C.steelDark }),
    ...[[68, 82], [432, 82], [68, 158], [432, 158], [140, 162], [180, 162], [250, 162], [320, 162]].map(([x, y]) => circle(x, y, 7, { fill: C.red, stroke: C.paper })),
    note(80, 200, 'tail pulley', { anchor: 'middle', size: 10 }), note(420, 200, 'head pulley', { anchor: 'middle', size: 10 }), note(140, 214, 'snub', { anchor: 'middle', size: 10 }), note(250, 214, 'return idlers', { anchor: 'middle', size: 10 }),
    line(200, 60, 300, 60, { width: 2, arrow: 'end' }), note(250, 52, 'travel', { anchor: 'middle', size: 10 }),
    caption(500, 240, 'Red = in-running nip: guard it or fence it; pull cord along the whole run.'),
  ], { title: 'Conveyor nip points' }))

// ---------- Idler set and pulley ----------
fig('conveyors/idler-set-and-pulley.svg', 'Troughing idler set (20°, 35° or 45°), return idler and a lagged drive pulley',
  svg(500, 230, [
    text(140, 22, 'Troughing idler', { anchor: 'middle', weight: 700 }), rect(40, 130, 200, 10, { fill: C.steelDark }),
    rect(100, 100, 80, 16, { fill: C.grey }), g([rect(0, -8, 62, 16, { fill: C.grey })], { transform: 'translate(40,120) rotate(-35)' }), g([rect(-62, -8, 62, 16, { fill: C.grey })], { transform: 'translate(240,120) rotate(35)' }),
    path('M50,88 L100,100 L180,100 L230,88', { stroke: C.accentDark, width: 4 }), angle(240, 120, 40, 180, 215, ''), note(200, 150, '35° trough', { size: 10, fill: C.blue }),
    note(140, 175, 'return idler: single flat roll under the return belt', { anchor: 'middle', size: 10 }), rect(90, 185, 100, 12, { fill: C.grey }),
    text(380, 22, 'Drive pulley with lagging', { anchor: 'middle', weight: 700 }), circle(380, 120, 60, { fill: C.grey }), circle(380, 120, 60, { fill: 'none', stroke: '#333', width: 8 }), ...[0, 45, 90, 135].map((a) => line(380 - 60 * Math.cos(a * P), 120 - 60 * Math.sin(a * P), 380 + 60 * Math.cos(a * P), 120 + 60 * Math.sin(a * P), { stroke: C.paper, width: 1, dash: '3 6' })),
    circle(380, 120, 10, { fill: C.steelDark }), note(380, 200, 'rubber or ceramic lagging; crowned tail\npulley for tracking; worn smooth = slip', { anchor: 'middle', size: 9.5 }),
  ], { title: 'Idler set and pulley' }))

// ---------- Screw conveyor and bucket elevator ----------
fig('conveyors/screw-and-bucket-elevator.svg', 'Screw conveyor (hand of the flight sets the direction) and a centrifugal-discharge bucket elevator',
  svg(500, 250, [
    text(140, 22, 'Screw conveyor', { anchor: 'middle', weight: 700 }), rect(30, 80, 220, 70, { fill: C.grey, rx: 6 }), line(30, 115, 250, 115, { width: 4 }),
    ...[0, 1, 2, 3, 4, 5].map((i) => path(`M${45 + i * 34},88 q17,27 34,54`, { stroke: C.steelDark, width: 3 })), line(60, 60, 200, 60, { width: 2, arrow: 'end' }), note(130, 52, 'flow (right-hand flight, clockwise)', { anchor: 'middle', size: 9.5 }),
    note(140, 175, 'trough 30-45% full; hanger bearings mid-span;\nnever reach in: it is a permit space', { anchor: 'middle', size: 9.5 }),
    text(385, 22, 'Bucket elevator', { anchor: 'middle', weight: 700 }), rect(340, 40, 90, 190, { fill: C.grey, rx: 6 }), circle(385, 60, 18, { fill: C.steelDark }), circle(385, 205, 18, { fill: C.steelDark }), line(367, 60, 367, 205, { width: 4 }), line(403, 60, 403, 205, { width: 4 }),
    ...[90, 130, 170].map((y) => [rect(354, y, 14, 12, { fill: C.accent }), rect(403, y + 20, 14, 12, { fill: C.accent })]), path('M395,48 q30,-20 50,10', { stroke: C.accentDark, width: 2, arrow: 'end' }), note(455, 90, 'discharge', { anchor: 'middle', size: 9.5 }),
    note(385, 245, 'tension, tracking, boot clean-out, lagging', { anchor: 'middle', size: 9 }),
  ], { title: 'Screw conveyor and bucket elevator' }))

// ---------- Approach boundaries ----------
fig('motors-electrical/approach-boundaries.svg', 'NFPA 70E boundaries around exposed energised parts: arc flash boundary, limited, restricted; only qualified persons with PPE inside',
  svg(500, 300, [
    ...[[125, C.soft, 'arc flash boundary'], [85, C.blueSoft, 'limited approach'], [48, C.redSoft, 'restricted']].map(([r, c, n]) => [circle(170, 150, r, { fill: c, stroke: C.line }), text(170, 150 - r + 16, n, { anchor: 'middle', size: 10.5, weight: 600 })]),
    rect(150, 130, 40, 40, { fill: C.steelDark }), text(170, 154, '480 V', { anchor: 'middle', size: 9, fill: '#fff', weight: 700 }),
    table(320, 40, [['480 V (AC)', 'Distance'], ['limited', '3 ft 6 in'], ['restricted', '1 ft 0 in'], ['arc flash', 'from label']], [95, 75], { rowH: 22, size: 10.5 }),
    note(405, 150, 'unqualified: stay outside\nthe limited boundary\nunless escorted', { anchor: 'middle', size: 10 }),
    note(405, 205, 'inside the arc flash boundary:\narc-rated PPE per the label', { anchor: 'middle', size: 10 }),
    caption(500, 300, 'A millwright is not qualified for live work: lockout, verify, then work.'),
  ], { title: 'Approach boundaries' }))

// ---------- Megger connections ----------
fig('motors-electrical/megger-test.svg', 'Insulation resistance test: megger between each lead (or all leads tied) and the frame ground, 1 minute at 500 or 1,000 V; IEEE 43 minimums',
  svg(500, 275, [
    rect(60, 90, 160, 110, { fill: C.grey, rx: 10 }), circle(140, 145, 40, { fill: C.steel }), rect(90, 60, 100, 30, { fill: C.steelDark }), ...[105, 140, 175].map((x) => line(x, 60, x, 40, { width: 3, stroke: C.copper })),
    rect(280, 60, 120, 80, { fill: C.blueSoft, stroke: C.blue, rx: 6 }), text(340, 90, 'MEGGER', { anchor: 'middle', size: 13, weight: 700, fill: C.blue }), text(340, 110, '500 / 1,000 V', { anchor: 'middle', size: 11 }),
    path('M290,140 C290,170 140,20 140,40', { stroke: C.red, width: 2 }), path('M390,140 C390,168 260,190 220,180', { stroke: C.ink, width: 2 }), note(345, 155, 'L', { size: 10, fill: C.red }), note(392, 155, 'E', { size: 10 }),
    rect(214, 176, 12, 8, { fill: C.ink }), note(120, 222, 'frame ground (clean spot)', { anchor: 'middle', size: 10 }),
    table(270, 175, [['Motor', 'Minimum'], ['pre-1970 / random', '1 MΩ + 1 per kV'], ['modern form wound', '100 MΩ'], ['modern random', '5 MΩ']], [110, 100], { rowH: 18, size: 9.5 }),
    caption(500, 275, 'Disconnect from the drive and starter first; discharge the winding after.'),
  ], { title: 'Megger test' }))

// ---------- 9-lead wye connections ----------
fig('motors-electrical/nine-lead-wye.svg', '9-lead wye-connected dual-voltage motor: low voltage joins 4-7, 5-8, 6-9 and lines to 1-7, 2-8, 3-9; high voltage joins 4-7, 5-8, 6-9 in series pairs with lines to 1, 2, 3',
  svg(500, 280, [
    ...[[130, 'Low voltage (230 V)', [['L1', '1, 7'], ['L2', '2, 8'], ['L3', '3, 9'], ['join', '4, 5, 6']]], [370, 'High voltage (460 V)', [['L1', '1'], ['L2', '2'], ['L3', '3'], ['join', '4-7, 5-8, 6-9']]]].map(([cx, n, rows]) => [
      text(cx, 22, n, { anchor: 'middle', weight: 700, size: 12 }),
      ...[90, 210, 330].map((a, i) => [line(cx, 110, cx + 60 * Math.cos(a * P), 110 + 60 * Math.sin(a * P), { width: 3, stroke: C.copper }), circle(cx + 30 * Math.cos(a * P), 110 + 30 * Math.sin(a * P), 4, { fill: C.ink }), text(cx + 72 * Math.cos(a * P), 114 + 72 * Math.sin(a * P), String(i + 1), { anchor: 'middle', size: 10, weight: 700 }), text(cx + 22 * Math.cos(a * P) + (a === 90 ? 10 : 0), 114 + 22 * Math.sin(a * P), String(i + 4), { anchor: 'middle', size: 9, fill: C.blue }), text(cx + 44 * Math.cos(a * P) + (a === 90 ? 10 : 0), 114 + 44 * Math.sin(a * P), String(i + 7), { anchor: 'middle', size: 9, fill: C.blue })]),
      table(cx - 80, 185, rows, [50, 110], { rowH: 18, size: 10, head: false }),
    ]),
    caption(500, 280, 'Delta-connected 9-lead motors differ: read the plate; megger first.'),
  ], { title: '9-lead wye connections' }))

// ---------- PLC signal chain ----------
fig('motors-electrical/plc-signal-chain.svg', 'From sensor to motor: sensor, input card, PLC program, output card, contactor or drive; check the LEDs at each step',
  svg(500, 200, [
    ...[['sensor\n(prox, eye)', C.soft], ['input card\nLED on?', C.blueSoft], ['PLC\nprogram', C.grey], ['output card\nLED on?', C.blueSoft], ['contactor\nor VFD', C.grey], ['motor', C.greenSoft]].map(([n, c], i) => box(20 + i * 80, 60, 70, 60, n, { fill: c, size: 10.5 })),
    ...[0, 1, 2, 3, 4].map((i) => line(90 + i * 80, 90, 100 + i * 80, 90, { width: 2, arrow: 'end' })),
    note(250, 150, 'check in order: target in range, sensor LED, input LED, output LED, contactor in, motor free', { anchor: 'middle', size: 9.5 }),
    caption(500, 200, 'Never force an output or bypass a safety input: call the controls tech.'),
  ], { title: 'PLC signal chain' }))

// ---------- Motor nameplate ----------
fig('motors-electrical/motor-nameplate.svg', 'A typical NEMA nameplate and what to read first: HP, volts, FLA, rpm, frame, service factor, insulation class, enclosure',
  svg(500, 260, [
    rect(40, 30, 300, 200, { fill: C.grey, stroke: C.ink, rx: 6 }), text(190, 52, 'INDUCTION MOTOR', { anchor: 'middle', size: 12, weight: 700 }),
    ...[['HP 25', 'kW 18.6'], ['VOLTS 230/460', 'AMPS 62/31'], ['RPM 1770', 'HZ 60  PH 3'], ['FRAME 284T', 'S.F. 1.15'], ['INSUL CLASS F', 'AMB 40°C'], ['ENCL TEFC', 'CODE G'], ['DUTY CONT', 'NEMA DESIGN B']].map(([a, b], i) => [text(52, 78 + i * 22, a, { size: 11, family: 'ui-monospace, Menlo, Consolas, monospace' }), text(200, 78 + i * 22, b, { size: 11, family: 'ui-monospace, Menlo, Consolas, monospace' })]),
    ...[[1, 118, 74], [2, 300, 96], [3, 124, 118], [4, 136, 140], [5, 278, 140], [6, 152, 162]].map(([n, x, y]) => callout(n, x, y, { r: 8 })),
    legend(350, 40, ['HP and kW', 'FLA at each voltage', 'rpm: 1770 = 4 pole', 'frame: shaft height\nand foot spacing', 'service factor 1.15', 'Class F: 155°C max'], { size: 10, gap: 15 }),
    caption(500, 260, 'Replacement must match frame, voltage, rpm, enclosure and mounting.'),
  ], { title: 'Motor nameplate' }))

// ---------- VFD bearing currents ----------
fig('motors-electrical/vfd-bearing-currents.svg', 'VFD bearing currents: common-mode voltage discharges through the bearings and flutes the races; shielded cable, shaft grounding ring and an insulated opposite-drive-end bearing stop it',
  svg(500, 240, [
    rect(30, 80, 90, 80, { fill: C.blueSoft, stroke: C.blue, rx: 6 }), text(75, 124, 'VFD', { anchor: 'middle', size: 14, weight: 700, fill: C.blue }),
    rect(200, 70, 180, 100, { fill: C.grey, rx: 10 }), rect(380, 108, 80, 24, { fill: C.steel }), circle(210, 120, 22, { fill: C.steel }), circle(370, 120, 22, { fill: C.steel }),
    path('M120,120 L200,120', { stroke: C.ink, width: 4 }), path('M120,112 L200,112', { stroke: C.steelDark, width: 1, dash: '3 2' }), note(160, 78, 'shielded VFD cable,\nshield bonded both ends', { anchor: 'middle', size: 9.5 }),
    rect(388, 100, 8, 40, { fill: C.accent, stroke: C.accentDark }), note(400, 176, 'shaft grounding\nring (DE)', { anchor: 'middle', size: 9.5 }), circle(210, 120, 26, { fill: 'none', stroke: C.red, width: 3 }), note(210, 182, 'insulated bearing\n(ODE)', { anchor: 'middle', size: 9.5 }),
    ...[0, 1, 2, 3].map((i) => line(300 + i * 12, 40, 306 + i * 12, 56, { stroke: C.red, width: 1.5 })), note(320, 32, 'discharge → fluting', { anchor: 'middle', size: 9.5, fill: C.red }),
    caption(500, 240, 'Fluting shows as a washboard pattern and a whine that rises with speed.'),
  ], { title: 'VFD bearing currents' }))

// ---------- ISO severity chart ----------
{
  const zones = [[0, 1.4, 'A  new machine', C.greenSoft], [1.4, 2.8, 'B  unrestricted', C.blueSoft], [2.8, 4.5, 'C  restricted, plan repair', C.soft], [4.5, 8, 'D  damage likely', C.redSoft]]
  const rows = [['Group 1 (>300 kW / large)', [0, 2.3, 4.5, 7.1, 11]], ['Group 2 (15-300 kW)', [0, 1.4, 2.8, 4.5, 7.1]]]
  const sx = (v) => 150 + v * 28
  fig('condition-monitoring/iso-severity-zones.svg', 'ISO 20816-3 zones for rigid-mounted machines: velocity mm/s RMS on the bearing housing',
    svg(500, 230, [text(250, 22, 'ISO 20816-3 zones, rigid foundation, mm/s RMS', { anchor: 'middle', weight: 700, size: 12 }),
      ...rows.map(([n, b], r) => { const y = 50 + r * 60; return [text(140, y + 28, n, { anchor: 'end', size: 10 }), ...[0, 1, 2, 3].map((i) => [rect(sx(b[i]), y, sx(b[i + 1]) - sx(b[i]), 40, { fill: [C.greenSoft, C.blueSoft, C.soft, C.redSoft][i], stroke: C.line }), text((sx(b[i]) + sx(b[i + 1])) / 2, y + 25, ['A', 'B', 'C', 'D'][i], { anchor: 'middle', size: 12, weight: 700 }), text(sx(b[i + 1]), y + 52, String(b[i + 1]), { anchor: 'middle', size: 9.5, fill: C.muted })]), text(sx(0), y + 52, '0', { anchor: 'middle', size: 9.5, fill: C.muted })] }),
      note(250, 185, 'A new · B unrestricted long-term · C restricted, plan a repair · D damage likely', { anchor: 'middle', size: 10 }),
      caption(500, 230, 'Flexible mounts allow about 1.5× these values. 1 in/s pk ≈ 18 mm/s RMS.')], { title: 'ISO severity zones' }))
}

// ---------- Vibration signatures ----------
fig('condition-monitoring/vibration-signatures.svg', 'Spectrum shapes: unbalance at 1×, misalignment at 2× with high axial, looseness as a comb of harmonics, bearing defects non-synchronous with haystacks',
  svg(500, 280, [
    ...[['Unbalance', [[1, 1]], 'high 1×, radial', C.blue], ['Misalignment', [[1, 0.6], [2, 1], [3, 0.3]], '2× (and 3×), axial high', C.accentDark], ['Looseness', [[0.5, 0.3], [1, 1], [1.5, 0.3], [2, 0.7], [2.5, 0.25], [3, 0.6], [4, 0.5], [5, 0.4]], 'many harmonics, 0.5× orders', C.red], ['Bearing defect', [[1, 0.4], [3.2, 0.6], [6.4, 0.5], [9.6, 0.35]], 'non-integer orders, haystack', C.green]]
      .map(([n, peaks, d, c], i) => { const x0 = 30 + (i % 2) * 240, y0 = 50 + Math.floor(i / 2) * 115; const w = 200, h = 60; return [text(x0 + w / 2, y0 - 8, n, { anchor: 'middle', size: 11.5, weight: 600, fill: c }), rect(x0, y0, w, h, { fill: C.paper, stroke: C.line }), line(x0, y0 + h, x0 + w, y0 + h, { width: 1 }), ...peaks.map(([o, a]) => line(x0 + o * 18, y0 + h, x0 + o * 18, y0 + h - a * 52, { stroke: c, width: 3 })), i === 3 ? path(`M${x0 + 40},${y0 + h} q30,-20 60,-6 q30,-8 60,6`, { stroke: c, width: 1, dash: '2 2' }) : '', ...[1, 2, 3, 4, 5].map((o) => text(x0 + o * 18, y0 + h + 12, o + '×', { anchor: 'middle', size: 8, fill: C.muted })), note(x0 + w / 2, y0 + h + 28, d, { anchor: 'middle', size: 9.5 })] }),
    caption(500, 280, 'Orders = multiples of shaft speed. Compare radial and axial, both bearings.'),
  ], { title: 'Vibration signatures' }))

// ---------- IR and ultrasound ----------
fig('condition-monitoring/thermography-and-ultrasound.svg', 'Thermography compares like with like (a bearing 20°F above its twin); ultrasound trends bearing noise in dB and finds air leaks and arcing',
  svg(500, 230, [
    text(130, 22, 'Thermal image', { anchor: 'middle', weight: 700 }), rect(30, 40, 200, 120, { fill: '#1a1a4a' }), rect(50, 90, 160, 30, { fill: '#3a3a9a' }), circle(80, 105, 26, { fill: '#e8b400' }), circle(80, 105, 12, { fill: '#ff2a00' }), circle(180, 105, 26, { fill: '#6a5acd' }),
    text(80, 150, '198°F', { anchor: 'middle', size: 11, fill: '#fff', weight: 700 }), text(180, 150, '126°F', { anchor: 'middle', size: 11, fill: '#fff', weight: 700 }), note(130, 180, 'DE bearing 72°F hotter than the NDE:\nlubrication or damage, act now', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Ultrasound trend (dB)', { anchor: 'middle', weight: 700 }), rect(280, 40, 190, 120, { fill: C.paper, stroke: C.line }), path('M290,140 L330,138 L370,135 L400,125 L430,105 L460,70', { stroke: C.red, width: 2.5 }), line(280, 132, 470, 132, { stroke: C.green, width: 1, dash: '4 3' }), line(280, 116, 470, 116, { stroke: C.accentDark, width: 1, dash: '4 3' }),
    text(465, 128, 'baseline', { anchor: 'end', size: 9, fill: C.green }), text(465, 112, '+8 dB: lubricate', { anchor: 'end', size: 9, fill: C.accentDark }), text(440, 60, '+16 dB: failing', { anchor: 'end', size: 9, fill: C.red }), note(375, 180, 'grease while listening: dB drops then\nsettles = right amount', { anchor: 'middle', size: 10 }),
  ], { title: 'Thermography and ultrasound' }))
