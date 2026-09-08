import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, hatchRect, leader, fig, C } from './lib.mjs'
const P = Math.PI / 180

// ---------- Vernier caliper parts ----------
fig('measurement/vernier-caliper-parts.svg', 'The four measurements a caliper makes: outside jaws, inside jaws, depth rod and step',
  svg(500, 250, [
    // beam
    rect(120, 90, 340, 26, { fill: C.steel }), ...Array.from({ length: 34 }, (_, i) => line(126 + i * 10, 90, 126 + i * 10, i % 5 === 0 ? 100 : 96, { width: 1 })),
    // fixed jaw (outside, below) and fixed inside jaw (above)
    poly([[120, 116], [120, 190], [140, 190], [150, 116]], { fill: C.steel }), poly([[120, 90], [120, 50], [132, 50], [140, 90]], { fill: C.steel }),
    // sliding head
    rect(170, 80, 70, 46, { fill: C.steelDark, rx: 3 }), poly([[170, 126], [160, 190], [180, 190], [200, 126]], { fill: C.steelDark }), poly([[176, 80], [166, 50], [178, 50], [186, 80]], { fill: C.steelDark }),
    circle(226, 103, 6, { fill: C.grey }),
    // depth rod
    rect(456, 98, 24, 8, { fill: C.steelDark }),
    // step
    line(170, 90, 170, 80, { width: 2, stroke: C.accentDark }),
    callout(1, 150, 200), callout(2, 154, 40), callout(3, 470, 122), callout(4, 190, 68),
    legend(250, 150, ['outside: jaws close on the part', 'inside: knife edges open into a bore', 'depth: rod from the beam end', 'step: head face to beam end'], { size: 11, gap: 17 }),
    caption(500, 250, 'Read all four on the same scale; zero the jaws closed before you start.'),
  ], { title: 'Vernier caliper parts' }))

// ---------- Vernier scale reading ----------
{
  const x0 = 40, px = 400 // 1.000 in = 400 px, main tick every 0.025 in = 10 px
  const vz = x0 + 0.436 * px
  const main = []
  for (let n = 0; n <= 40; n++) {
    const x = x0 + n * 10, tall = n % 10 === 0 ? 22 : n % 5 === 0 ? 14 : 8
    main.push(line(x, 70, x, 70 + tall, { width: n % 10 === 0 ? 1.5 : 1 }))
    if (n % 10 === 0) main.push(text(x, 62, String(n / 10), { size: 11, anchor: 'middle', weight: 700 }))
  }
  const vern = []
  for (let k = 0; k <= 25; k++) {
    const x = vz + k * 9.6, hit = k === 11
    vern.push(line(x, 120, x, k % 5 === 0 ? 100 : 108, { width: hit ? 2.5 : 1, stroke: hit ? C.red : C.ink }))
    if (k % 5 === 0) vern.push(text(x, 134, String(k), { size: 11, anchor: 'middle', weight: 700 }))
  }
  fig('measurement/vernier-scale-reading.svg', 'Reading an inch vernier: main scale to 0.025, then the vernier line that lines up gives thousandths',
    svg(500, 265, [
      text(40, 30, 'Main scale: each small line = 0.025 in, numbers = tenths', { size: 11, weight: 600 }),
      rect(30, 70, 420, 30, { fill: C.grey, stroke: C.line }), main,
      rect(vz - 6, 100, 260, 20, { fill: C.blueSoft, stroke: C.blue }), vern,
      text(vz, 152, 'vernier 0', { size: 10, anchor: 'middle', fill: C.blue }), line(vz, 100, vz, 70, { stroke: C.blue, width: 1, dash: '3 2' }),
      leader(vz + 11 * 9.6, 100, 400, 160, 'line 11 lines up', { size: 11, fill: C.red, anchor: 'middle' }),
      text(40, 190, 'main whole inches   1.000', { size: 12, family: 'ui-monospace, Menlo, Consolas, monospace' }),
      text(40, 207, 'main scale before 0  0.425  (4 tenths + one 0.025 line)', { size: 12, family: 'ui-monospace, Menlo, Consolas, monospace' }),
      text(40, 224, 'vernier line 11      0.011', { size: 12, family: 'ui-monospace, Menlo, Consolas, monospace', fill: C.red }),
      text(40, 243, 'reading             1.436 in', { size: 12, weight: 700, family: 'ui-monospace, Menlo, Consolas, monospace' }),
      caption(500, 265, 'Only one vernier line lines up; look for it with a light behind the scale.'),
    ], { title: 'Vernier scale reading' }))
}

// ---------- Telescoping gauge technique ----------
fig('measurement/telescoping-gauge-technique.svg', 'Telescoping gauge: lock it slightly over size, rock it through the true diameter, then read it with a micrometer',
  svg(500, 280, [
    text(120, 22, '1. Rock through the centre', { anchor: 'middle', weight: 700, size: 12 }),
    circle(120, 130, 80, { fill: C.grey, stroke: C.ink, width: 2 }), circle(120, 130, 66, { fill: C.paper }),
    line(120, 64, 120, 196, { width: 4, stroke: C.steelDark }), circle(120, 64, 5, { fill: C.steelDark }), circle(120, 196, 5, { fill: C.steelDark }),
    line(120, 130, 120, 230, { width: 3, stroke: C.steelDark }), rect(112, 226, 16, 14, { fill: C.accent, rx: 3 }),
    line(64, 96, 176, 164, { width: 1.2, stroke: C.blue, dash: '4 3' }), line(64, 164, 176, 96, { width: 1.2, stroke: C.blue, dash: '4 3' }),
    arc(120, 130, 94, 60, 120, { stroke: C.blue, width: 1.5, arrow: 'both' }),
    note(130, 250, 'lock lightly as you pass the centre', { anchor: 'middle', size: 10 }),
    text(370, 22, '2. Measure the gauge', { anchor: 'middle', weight: 700, size: 12 }),
    path('M300,90 L300,170 L330,190 L440,190 L440,150 L400,150 L400,110 L330,110 Z', { fill: C.steel }), rect(400, 118, 60, 24, { fill: C.steelDark }), rect(455, 116, 12, 28, { fill: C.grey }),
    line(330, 130, 400, 130, { width: 4, stroke: C.steelDark }), circle(330, 130, 5, { fill: C.steelDark }), circle(400, 130, 5, { fill: C.steelDark }),
    note(370, 215, 'same light feel as on the bore;\nrepeat three times, readings within 0.0005 in', { anchor: 'middle', size: 10 }),
    caption(500, 280, 'Rocking finds the shortest line across the bore: the true diameter.'),
  ], { title: 'Telescoping gauge technique' }))

// ---------- Feeler gauge technique ----------
fig('measurement/feeler-gauge-technique.svg', 'Feeler gauge: the blade that slides with a light drag is the gap; stack two blades for in-between sizes',
  svg(500, 230, [
    plate(40, 60, 200, 40), plate(40, 112, 200, 40), rect(100, 100, 200, 12, { fill: C.accent, rx: 2 }), rect(280, 92, 40, 28, { fill: C.steelDark, rx: 4 }),
    line(220, 106, 260, 106, { width: 2, arrow: 'both', stroke: C.blue }), note(240, 132, 'light drag both ways', { anchor: 'middle', size: 10, fill: C.blue }),
    line(140, 58, 140, 98, { width: 1, arrow: 'end', stroke: C.blue }), text(140, 50, 'gap 0.012 in (0.30 mm)', { size: 11, anchor: 'middle', fill: C.blue }),
    note(140, 175, 'too tight: blade bends or scrapes\ntoo loose: falls out, no drag', { anchor: 'middle', size: 10 }),
    text(410, 50, 'Stacking', { anchor: 'middle', weight: 700, size: 12 }),
    rect(370, 62, 80, 8, { fill: C.accent }), rect(370, 72, 80, 6, { fill: C.accentDark }), text(410, 96, '0.010 + 0.006 = 0.016', { anchor: 'middle', size: 11 }),
    note(410, 150, 'thickest blade first, thin\none next to it; wipe clean', { anchor: 'middle', size: 10 }),
    caption(500, 230, 'Insert flat and square; a blade at an angle reads a bigger gap.'),
  ], { title: 'Feeler gauge technique' }))

// ---------- Torque wrench extension ----------
fig('measurement/torque-wrench-extension.svg', 'A crowfoot or extension that lengthens the wrench changes the torque: set the wrench to Ts × L ÷ (L + E)',
  svg(500, 240, [
    rect(40, 90, 250, 18, { fill: C.steelDark, rx: 4 }), rect(40, 86, 60, 26, { fill: C.ink, rx: 6 }), rect(290, 84, 40, 30, { fill: C.steel, rx: 4 }),
    rect(330, 92, 60, 14, { fill: C.accent }), rect(390, 82, 30, 34, { fill: C.accentDark, rx: 4 }), circle(405, 99, 8, { fill: C.paper }),
    line(70, 99, 70, 40, { width: 1, stroke: C.muted }), line(310, 99, 310, 40, { width: 1, stroke: C.muted }), line(405, 99, 405, 40, { width: 1, stroke: C.muted }),
    line(70, 48, 310, 48, { width: 1, arrow: 'both', stroke: C.blue }), text(190, 42, 'L (hand centre to square drive)', { size: 11, anchor: 'middle', fill: C.blue }),
    line(310, 64, 405, 64, { width: 1, arrow: 'both', stroke: C.red }), text(357, 78, 'E', { size: 12, anchor: 'middle', fill: C.red, weight: 700 }),
    note(70, 130, 'pull here, slowly, one click', { size: 10 }),
    text(40, 165, 'wrench setting = target × L ÷ (L + E)', { size: 13, weight: 700 }),
    text(40, 185, 'example: target 100 ft·lb, L 18 in, E 3 in → set 100 × 18 ÷ 21 = 86 ft·lb', { size: 11 }),
    text(40, 205, 'crowfoot at 90° to the wrench: E = 0, no correction', { size: 11, fill: C.green }),
    caption(500, 240, 'Sockets add no length; only offsets in line with the wrench do.'),
  ], { title: 'Torque wrench extension correction' }))

// ---------- Height gauge and sine bar ----------
fig('measurement/height-gauge-and-sine-bar.svg', 'Surface plate work: a height gauge scribes or measures from the plate; a sine bar on gauge blocks sets an angle',
  svg(500, 270, [
    rect(20, 200, 460, 22, { fill: C.steelDark }), text(250, 216, 'granite surface plate (reference plane)', { anchor: 'middle', size: 11, fill: C.paper }),
    // height gauge
    rect(40, 180, 70, 20, { fill: C.steel }), rect(70, 50, 10, 130, { fill: C.steel }), ...Array.from({ length: 13 }, (_, i) => line(80, 60 + i * 10, i % 5 === 0 ? 90 : 86, 60 + i * 10, { width: 1 })),
    rect(80, 100, 30, 24, { fill: C.steelDark, rx: 3 }), rect(110, 108, 50, 6, { fill: C.ink }), poly([[160, 106], [176, 111], [160, 116]], { fill: C.ink }),
    plate(150, 150, 60, 50), line(176, 111, 176, 150, { width: 1, stroke: C.blue, dash: '3 2' }), dim(176, 200, 176, 111, 'H', { off: 16, size: 11, fill: C.blue }),
    text(100, 36, 'Height gauge', { anchor: 'middle', weight: 700, size: 12 }),
    note(180, 60, 'zero on the plate,\nthen scribe or read H', { anchor: 'middle', size: 10 }),
    // sine bar
    text(380, 36, 'Sine bar', { anchor: 'middle', weight: 700, size: 12 }),
    circle(290, 190, 10, { fill: C.steel }), rect(430, 120, 40, 80, { fill: C.grey, stroke: C.line }), circle(450, 110, 10, { fill: C.steel }),
    g([rect(280, 160, 180, 22, { fill: C.steel, rx: 2 })], { transform: 'rotate(-26.6 290 190)' }),
    angle(290, 190, 40, -26.6, 0, 'θ', { size: 12 }),
    dim(430, 200, 430, 120, 'h', { off: -14, side: 1, size: 11, fill: C.blue }),
    note(400, 240, 'gauge blocks, height h', { anchor: 'middle', size: 10, fill: C.blue }),
    text(260, 70, 'sin θ = h ÷ L  (L = 5 or 10 in)', { size: 12, weight: 700 }), text(260, 88, '30°, 5 in bar: h = 5 × 0.5 = 2.500 in', { size: 11 }),
    caption(500, 270, 'Everything on the plate is measured from one flat reference.'),
  ], { title: 'Height gauge and sine bar' }))

// ---------- Propane versus acetylene ----------
fig('oxy-fuel/propane-vs-acetylene.svg', 'Propane and propylene need a two-piece tip, more oxygen and a longer preheat; the flame looks different too',
  svg(500, 280, [
    text(130, 22, 'Acetylene, one-piece tip', { anchor: 'middle', weight: 700, size: 12 }),
    rect(40, 50, 60, 28, { fill: C.steelDark, rx: 3 }), ...[0, 1, 2, 3].map((i) => circle(100, 56 + i * 6, 1.5, { fill: C.paper })),
    path('M100,64 C130,40 150,88 100,64', { fill: C.blueSoft, stroke: C.blue, width: 1 }), path('M100,64 C118,52 128,76 100,64', { fill: '#bfdbfe', stroke: C.blue, width: 1 }),
    note(130, 100, 'short sharp inner cone,\nfast preheat, 5,600°F', { anchor: 'middle', size: 10 }),
    text(370, 22, 'Propane, two-piece tip', { anchor: 'middle', weight: 700, size: 12 }),
    rect(280, 50, 60, 28, { fill: C.steelDark, rx: 3 }), rect(332, 52, 8, 24, { fill: C.copper }), ...[0, 1, 2, 3].map((i) => circle(340, 56 + i * 6, 1.5, { fill: C.paper })),
    path('M340,64 C400,30 430,98 340,64', { fill: C.soft, stroke: C.accentDark, width: 1 }), path('M340,64 C365,50 380,78 340,64', { fill: '#fde68a', stroke: C.accentDark, width: 1 }),
    note(380, 100, 'longer, softer cone with recessed\nskirt; slower preheat, 5,100°F', { anchor: 'middle', size: 10 }),
    table(40, 125, [['', 'acetylene', 'propane / propylene'], ['tip', '1-101 (one piece)', 'GPN / GPP (two piece)'], ['fuel psi, 1/2 in', '3 to 5', '2 to 8 (propane)'], ['oxygen psi, 1/2 in', '30 to 35', '35 to 45'], ['oxygen used', 'x 1', 'about x 1.5'], ['preheat time', 'fast', 'slower; hold longer']], [120, 140, 160], { rowH: 20, size: 10.5 }),
    caption(500, 280, 'Same torch, different tip and pressures; grade T hose for propane.'),
  ], { title: 'Propane versus acetylene' }))

// ---------- Oxy-fuel welding and braze welding technique ----------
fig('oxy-fuel/oaw-braze-technique.svg', 'Forehand oxy-acetylene welding: torch at 45°, rod at 45° from the other side, puddle carried along the joint; bronze rod tins first',
  svg(500, 272, [
    plate(40, 150, 420, 22), line(250, 150, 250, 172, { width: 1, stroke: C.muted }),
    // torch from right, rod from left
    g([rect(0, -6, 110, 12, { fill: C.steelDark, rx: 4 }), rect(-16, -4, 16, 8, { fill: C.copper })], { transform: 'translate(300 110) rotate(-45)' }),
    g([rect(0, -2, 110, 4, { fill: C.accentDark })], { transform: 'translate(190 122) rotate(-135)' }),
    path('M240,150 C250,132 270,132 280,150 Z', { fill: C.weld, stroke: C.accentDark, width: 1 }), path('M284,150 C288,140 296,142 300,150', { fill: '#bfdbfe', stroke: C.blue, width: 1 }),
    angle(284, 150, 28, -45, 0, '45°', { size: 11 }), angle(190, 150, 28, 180, 225, '45°', { size: 11 }),
    line(200, 190, 280, 190, { width: 2, arrow: 'end', stroke: C.blue }), note(240, 206, 'travel (forehand: rod leads)', { anchor: 'middle', size: 10, fill: C.blue }),
    note(430, 90, 'inner cone 1/16 to 1/8 in\nfrom the puddle', { anchor: 'middle', size: 10 }),
    note(80, 200, 'dip the rod in the front\nof the puddle, do not\nmelt it in the flame', { anchor: 'middle', size: 10 }),
    box(330, 196, 150, 48, 'Braze welding:\nheat to dull red, tin with\nbronze, then build', { fill: C.soft, stroke: C.accentDark, size: 10 }),
    caption(500, 272, 'Neutral flame for steel; slightly oxidizing for braze welding.'),
  ], { title: 'Oxy-fuel welding and braze welding technique' }))
