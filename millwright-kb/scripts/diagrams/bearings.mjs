import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, hatchRect, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- Bearing parts and number ----------
fig('bearings/bearing-parts-and-number.svg', 'Deep-groove ball bearing parts and what 6205-2RS C3 means',
  svg(500, 300, [
    circle(130, 130, 100, { fill: C.steel }), circle(130, 130, 80, { fill: C.paper }), circle(130, 130, 55, { fill: C.steel }), circle(130, 130, 38, { fill: C.paper }),
    ...[0, 45, 90, 135, 180, 225, 270, 315].map((a) => circle(130 + 67 * Math.cos(a * P), 130 + 67 * Math.sin(a * P), 11, { fill: C.grey })),
    circle(130, 130, 67, { fill: 'none', stroke: C.accentDark, dash: '3 3', width: 1 }),
    callout(1, 130, 38), callout(2, 130, 88), callout(3, 178, 82), callout(4, 130, 130), callout(5, 40, 130),
    legend(250, 40, ['outer ring (housing fit)', 'inner ring (shaft fit)', 'balls or rollers', 'bore = the last two digits × 5 mm', 'cage (retainer), seals or shields'], { size: 11, gap: 17 }),
    text(250, 160, '6 2 05 - 2RS C3', { size: 24, weight: 700, family: 'ui-monospace, Menlo, Consolas, monospace' }),
    note(245, 185, '6 = deep-groove ball · 2 = light series\n05 = 25 mm bore (05 × 5)', { size: 10 }),
    note(245, 215, '2RS = two rubber seals (ZZ = shields)\nC3 = clearance larger than normal', { size: 10 }),
    note(245, 246, 'bore codes 00, 01, 02, 03 = 10, 12, 15, 17 mm', { size: 10 }),
    caption(500, 300, 'Same number from any maker fits the same shaft and housing.'),
  ], { title: 'Bearing parts and number' }))

// ---------- Induction heater mounting ----------
fig('bearings/induction-heater-mounting.svg', 'Heat the bearing to 230°F (110°C) max on an induction heater with the probe on the inner ring, then push it to the shoulder and hold',
  svg(500, 285, [
    rect(40, 200, 200, 30, { fill: C.grey, rx: 4 }), rect(60, 80, 30, 120, { fill: C.steelDark }), rect(60, 70, 160, 14, { fill: C.steelDark }),
    circle(140, 140, 44, { fill: C.steel }), circle(140, 140, 24, { fill: C.paper }), rect(130, 96, 20, 4, { fill: C.red }), line(140, 96, 140, 60, { stroke: C.red, width: 1.5 }), note(140, 52, 'probe on the inner ring', { anchor: 'middle', size: 10 }),
    box(250, 90, 220, 40, '230°F (110°C) max; 175°F for\nsealed and shielded bearings', { fill: C.redSoft, stroke: C.red, size: 10.5 }),
    rect(280, 160, 180, 26, { fill: C.steel }), rect(280, 150, 14, 46, { fill: C.steelDark }), circle(330, 173, 30, { fill: C.steel }), circle(330, 173, 14, { fill: C.paper }), line(380, 173, 300, 173, { width: 2, arrow: 'end', stroke: C.blue }),
    note(370, 215, 'push to the shoulder, hold against it\nuntil it grips (it shrinks as it cools)', { anchor: 'middle', size: 10 }),
    note(40, 262, 'demagnetise after; never a torch on the bearing', { size: 10 }),
    caption(500, 285, 'Rule: bearing bore grows 0.001 in per inch per 100°F rise.'),
  ], { title: 'Induction heater mounting' }))

// ---------- Fits: rotating load ----------
fig('bearings/fits-rotating-load.svg', 'Which ring gets the interference fit: the ring that rotates relative to the load direction is tight, the other can be a push fit',
  svg(500, 240, [
    text(130, 22, 'Rotating shaft, fixed load', { anchor: 'middle', weight: 700, size: 12 }),
    rect(40, 100, 180, 30, { fill: C.steel }), circle(130, 115, 50, { fill: C.paper, stroke: C.red, width: 3 }), circle(130, 115, 30, { fill: C.steel, stroke: C.green, width: 3 }), arc(130, 115, 62, -150, -30, { stroke: C.blue, width: 1, arrow: 'end' }),
    line(215, 115, 188, 115, { width: 3, arrow: 'end', stroke: C.red }), note(222, 119, 'load', { size: 10, fill: C.red }),
    note(40, 180, 'inner ring: tight (k5, m5)', { size: 10, fill: C.green }), note(40, 195, 'outer ring: push fit (H7)', { size: 10, fill: C.red }), note(130, 215, 'belt pull, gear load, weight', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Fixed shaft, rotating housing', { anchor: 'middle', weight: 700, size: 12 }),
    rect(280, 100, 180, 30, { fill: C.steel }), circle(370, 115, 50, { fill: C.paper, stroke: C.green, width: 3 }), circle(370, 115, 30, { fill: C.steel, stroke: C.red, width: 3 }), arc(370, 115, 62, -150, -30, { stroke: C.blue, width: 1, arrow: 'end' }),
    line(455, 115, 428, 115, { width: 3, arrow: 'end', stroke: C.red }), note(462, 119, 'load', { size: 10, fill: C.red }),
    note(280, 180, 'outer ring: tight (N7, P7)', { size: 10, fill: C.green }), note(280, 195, 'inner ring: push (g6, h6)', { size: 10, fill: C.red }), note(370, 215, 'idler pulley, wheel, sheave on an axle', { anchor: 'middle', size: 10 }),
    caption(500, 240, 'A ring that should be tight but is loose creeps, frets and turns blue.'),
  ], { title: 'Bearing fits by load' }))

// ---------- Pillow block anatomy ----------
fig('bearings/pillow-block-anatomy.svg', 'Pillow block: housing, insert with wide inner ring, locking (set screw or eccentric collar), fixed versus floating',
  svg(500, 260, [
    poly([[60, 190], [260, 190], [260, 160], [230, 140], [230, 100], [90, 100], [90, 140], [60, 160]], { fill: C.grey }), rect(40, 190, 240, 14, { fill: C.steel }),
    circle(160, 130, 44, { fill: C.steel }), circle(160, 130, 22, { fill: C.paper }), rect(40, 118, 240, 24, { fill: C.steel, opacity: 0.6 }), rect(224, 108, 16, 44, { fill: C.steelDark }),
    line(232, 104, 232, 90, { width: 3 }), circle(232, 84, 5, { fill: C.ink }),
    callout(1, 90, 70), callout(2, 160, 130), callout(3, 232, 70), callout(4, 70, 200),
    legend(300, 50, ['housing (cast iron); base\nflat and bolted', 'insert: spherical OD self-\naligns 2°; wide inner ring', 'set screws on the flat, both\ntorqued; or eccentric collar\nturned with rotation', 'fixed end: screws tight;\nfloating end lets it grow'], { size: 10.5, gap: 16 }),
    caption(500, 260, 'Shaft under 35 HRC, set-screw spot dimpled; housing 1/3 full of grease.'),
  ], { title: 'Pillow block anatomy' }))

// ---------- Coupling gap and families ----------
fig('power-transmission/coupling-gap-and-types.svg', 'Coupling gap: set hubs flush with the shaft ends unless the drawing says otherwise; DBSE for spacer couplings; the common families',
  svg(500, 300, [
    rect(20, 60, 130, 24, { fill: C.steel }), rect(120, 40, 50, 64, { fill: C.grey }), rect(195, 40, 50, 64, { fill: C.grey }), rect(215, 60, 130, 24, { fill: C.steel }),
    dim(170, 30, 195, 30, 'gap', { size: 11 }), note(250, 125, 'gap from the coupling table (grid: 1/8 in typical); hubs flush with shaft ends', { anchor: 'middle', size: 10 }),
    ...[['Jaw / spider', (x, y) => [rect(x - 30, y - 12, 20, 24, { fill: C.grey }), rect(x + 10, y - 12, 20, 24, { fill: C.grey }), rect(x - 10, y - 10, 20, 20, { fill: C.accent })]],
      ['Grid', (x, y) => [rect(x - 30, y - 12, 20, 24, { fill: C.grey }), rect(x + 10, y - 12, 20, 24, { fill: C.grey }), path(`M${x - 10},${y - 8} q10,4 20,0 M${x - 10},${y} q10,4 20,0 M${x - 10},${y + 8} q10,4 20,0`, { stroke: C.blue, width: 2 })]],
      ['Gear', (x, y) => [rect(x - 30, y - 12, 20, 24, { fill: C.grey }), rect(x + 10, y - 12, 20, 24, { fill: C.grey }), rect(x - 34, y - 16, 68, 6, { fill: C.steelDark }), rect(x - 34, y + 10, 68, 6, { fill: C.steelDark })]],
      ['Disc', (x, y) => [rect(x - 30, y - 12, 20, 24, { fill: C.grey }), rect(x + 10, y - 12, 20, 24, { fill: C.grey }), rect(x - 8, y - 16, 4, 32, { fill: C.steelDark }), rect(x + 4, y - 16, 4, 32, { fill: C.steelDark }), rect(x - 4, y - 4, 8, 8, { fill: C.grey })]]]
      .map(([n, d], i) => { const x = 75 + i * 118, y = 190; return [...d(x, y), text(x, 225, n, { anchor: 'middle', size: 11, weight: 600 })] }),
    note(250, 250, 'jaw: cheap, dusts when misaligned · grid: shock loads, greased\ngear: high torque, greased · disc: no lube, needs exact DBSE', { anchor: 'middle', size: 9.5 }),
    caption(500, 300, 'Heat or press hubs on; never hammer them (bearings brinell).'),
  ], { title: 'Coupling gap and types' }))

// ---------- QD vs Taper-Lock ----------
fig('power-transmission/qd-vs-taperlock.svg', 'QD bushings have a flange and cap screws through it; Taper-Lock bushings are flangeless with screws in half-holes between bushing and hub',
  svg(500, 240, [
    text(130, 22, 'QD (JA, SH, SDS, SK, SF, E)', { anchor: 'middle', weight: 700, size: 12 }),
    rect(40, 60, 180, 100, { fill: C.grey }), poly([[110, 60], [150, 60], [140, 160], [120, 160]], { fill: C.steelDark }), rect(80, 60, 100, 14, { fill: C.steelDark }), ...[92, 168].map((x) => line(x, 60, x, 100, { width: 3, stroke: C.ink })),
    note(130, 185, 'flange with 3 holes; pull-up screws\nfrom the flange side; split through', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Taper-Lock (1108, 1610, 2517...)', { anchor: 'middle', weight: 700, size: 12 }),
    rect(280, 60, 180, 100, { fill: C.grey }), poly([[350, 60], [390, 60], [380, 160], [360, 160]], { fill: C.steelDark }), ...[344, 396].map((x) => line(x, 60, x, 95, { width: 3, stroke: C.ink })),
    note(370, 185, 'no flange; 2-3 screws in half-holes;\nremoval screw in the third hole', { anchor: 'middle', size: 10 }),
    caption(500, 240, 'Torque screws in stages to the table; dry taper; recheck after run-in.'),
  ], { title: 'QD vs Taper-Lock' }))

// ---------- V-belt deflection ----------
fig('power-transmission/v-belt-deflection.svg', 'V-belt tension by deflection: 1/64 in per inch of span at the force from the belt table; sheaves aligned with a straightedge',
  svg(500, 260, [
    circle(90, 130, 50, { fill: C.grey }), circle(390, 130, 80, { fill: C.grey }), line(90, 80, 390, 50, { width: 6, stroke: C.ink }), line(90, 180, 390, 210, { width: 6, stroke: C.ink }),
    line(90, 80, 390, 50, { width: 1, dash: '4 3', stroke: C.muted }), line(240, 65, 240, 80, { width: 3, arrow: 'end', stroke: C.red }), circle(240, 80, 4, { fill: C.red, stroke: 'none' }),
    dim(90, 40, 390, 40, 'span', { size: 11 }), note(240, 105, 'deflection = span ÷ 64', { anchor: 'middle', size: 10.5, fill: C.red }), note(240, 120, '(32 in span → 1/2 in)', { anchor: 'middle', size: 10 }),
    line(40, 232, 470, 232, { stroke: C.blue, width: 1.5, dash: '5 3' }), note(250, 250, 'straightedge on both sheave faces: touches at four points; 1/16 in per foot max', { anchor: 'middle', size: 10 }),
    note(90, 200, 'motor', { anchor: 'middle', size: 10 }), note(390, 235, '', { anchor: 'middle' }),
  ], { title: 'V-belt deflection' }))

// ---------- Gear contact pattern ----------
fig('gearboxes/gear-contact-pattern.svg', 'Tooth contact pattern with bluing: centred and 60-80% of the face is right; toe, heel, tip or root contact tells you what is wrong',
  svg(500, 230, [
    ...[['Good: centred', 0.2, 0.6, 0.35, 0.3, C.green], ['Toe contact: shafts not parallel', 0.05, 0.35, 0.35, 0.3, C.red], ['Heel contact', 0.6, 0.35, 0.35, 0.3, C.red], ['Tip contact: centre distance', 0.2, 0.6, 0.05, 0.3, C.red], ['Root contance: too close', 0.2, 0.6, 0.65, 0.3, C.red]]
      .map(([n, x0, w, y0, h, c], i) => { const x = 30 + i * 95, y = 50; return [rect(x, y, 80, 60, { fill: C.grey }), rect(x + 80 * x0, y + 60 * y0, 80 * w, 60 * h, { fill: '#2b6cb0', stroke: 'none', opacity: 0.8 }), text(x + 40, y - 8, ['good', 'toe', 'heel', 'tip', 'root'][i], { anchor: 'middle', size: 11, weight: 600, fill: c }), note(x + 40, y + 78, n.split(':')[1] ?? 'centred, 60-80%', { anchor: 'middle', size: 9 })] }),
    note(250, 160, 'toe / heel: shafts not parallel (bearing seats, housing bore)', { anchor: 'middle', size: 10.5 }),
    note(250, 178, 'tip / root: centre distance or backlash wrong; check with a feeler or dial indicator', { anchor: 'middle', size: 10.5 }),
    caption(500, 230, 'Blue the driven gear, roll by hand under light load, read the flank.'),
  ], { title: 'Gear contact pattern' }))

// ---------- Oil level and breather ----------
fig('gearboxes/oil-level-and-breather.svg', 'Gearbox oil level at the sight glass mark with the box stopped and cool; breather clear; magnetic drain plug checked at each change',
  svg(500, 230, [
    rect(120, 60, 260, 130, { fill: C.grey, rx: 8 }), rect(130, 130, 240, 55, { fill: C.soft, stroke: 'none' }), circle(300, 150, 18, { fill: C.paper }), line(282, 150, 318, 150, { stroke: C.red, width: 1.5 }),
    rect(200, 40, 20, 24, { fill: C.steelDark }), circle(210, 34, 8, { fill: C.grey }), rect(140, 188, 20, 14, { fill: C.steelDark }),
    circle(250, 120, 40, { fill: 'none', stroke: C.steelDark, width: 3, dash: '4 4' }), circle(250, 120, 6, { fill: C.steelDark }),
    callout(1, 300, 110), callout(2, 210, 20), callout(3, 118, 205), callout(4, 250, 170),
    legend(392, 60, ['sight glass:\nlevel at line', 'breather:\nclean, open', 'magnetic plug:\ncheck swarf', 'gear dips 1-2\nteeth in oil'], { size: 10, gap: 15 }),
    caption(500, 230, 'Overfilled = churning heat and leaks; underfilled = starved bearings.'),
  ], { title: 'Oil level and breather' }))

// ---------- Worm and planetary ----------
fig('gearboxes/worm-and-planetary.svg', 'Worm gear set (right-angle, high ratio, low efficiency) and planetary set (sun, planets, ring; coaxial, high torque)',
  svg(500, 230, [
    text(130, 22, 'Worm and wheel', { anchor: 'middle', weight: 700 }), circle(130, 130, 55, { fill: C.grey }), ...Array.from({ length: 24 }, (_, i) => circle(130 + 55 * Math.cos(i * 15 * P), 130 + 55 * Math.sin(i * 15 * P), 3, { fill: C.steelDark, stroke: 'none' })),
    rect(40, 56, 180, 22, { fill: C.steel, rx: 6 }), ...Array.from({ length: 9 }, (_, i) => line(52 + i * 20, 58, 60 + i * 20, 76, { width: 1.5, stroke: C.steelDark })),
    note(130, 205, 'ratio = wheel teeth ÷ worm starts\n5:1 to 100:1; efficiency 50-90%', { anchor: 'middle', size: 9.5 }),
    text(370, 22, 'Planetary', { anchor: 'middle', weight: 700 }), circle(370, 120, 75, { fill: C.grey }), circle(370, 120, 62, { fill: C.paper }), circle(370, 120, 22, { fill: C.accent }),
    ...[90, 210, 330].map((a) => circle(370 + 42 * Math.cos(a * P), 120 + 42 * Math.sin(a * P), 20, { fill: C.steel })),
    text(370, 124, 'sun', { anchor: 'middle', size: 9 }), note(370, 205, 'ratio = 1 + ring ÷ sun teeth (ring fixed)\n3:1 to 10:1 per stage; efficiency 95%+', { anchor: 'middle', size: 9.5 }),
  ], { title: 'Worm and planetary' }))
