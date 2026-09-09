import { svg, text, line, rect, circle, path, poly, g, dim, angle, arc, plate, chart, table, caption, box, callout, legend, note, fig, C } from './lib.mjs'

// ---------- Plasma cut chart ----------
{
  const ch = chart({ x: 60, y: 30, w: 400, h: 200, xmin: 0, xmax: 1, ymin: 0, ymax: 350, xticks: [0, 0.25, 0.5, 0.75, 1], yticks: [0, 50, 100, 150, 200, 250, 300, 350], xfmt: (v) => v === 0 ? '0' : ({ 0.25: '1/4', 0.5: '1/2', 0.75: '3/4', 1: '1' }[v]), xlabel: 'Mild steel thickness (in)', ylabel: 'Cut speed (in/min)' })
  const s45 = [[0.075, 340], [0.135, 200], [0.25, 100], [0.375, 55], [0.5, 30], [0.625, 18], [0.75, 12], [0.875, 8]]
  const s65 = [[0.135, 320], [0.25, 175], [0.375, 100], [0.5, 60], [0.625, 40], [0.75, 28], [1, 15]]
  const s85 = [[0.25, 260], [0.375, 150], [0.5, 100], [0.625, 68], [0.75, 45], [1, 25]]
  const ln = (pts, c) => path(pts.map((p, k) => (k ? 'L' : 'M') + ch.sx(p[0]) + ',' + ch.sy(p[1])).join(' '), { stroke: c, width: 2.5 })
  fig('cutting-gouging/plasma-cut-chart.svg', 'Plasma cut speed versus thickness for 45, 65 and 85 A air plasma (typical Hypertherm Powermax values)',
    svg(500, 310, [ch.el, ln(s45, C.blue), ln(s65, C.accentDark), ln(s85, C.red), text(ch.sx(0.075) + 6, ch.sy(340) + 4, '45 A', { size: 11, fill: C.blue, weight: 600 }), text(ch.sx(0.22), ch.sy(230) - 8, '65 A', { size: 11, fill: C.accentDark, weight: 600 }), text(ch.sx(0.55), ch.sy(100) - 10, '85 A', { size: 11, fill: C.red, weight: 600 }), note(250, 292, 'Read your machine’s own cut chart for the exact number; speeds fall fast with thickness.', { anchor: 'middle', size: 10.5 })], { title: 'Plasma cut chart' }))
}

// ---------- Piercing and keyholing ----------
fig('cutting-gouging/plasma-pierce-sequence.svg', 'Piercing: start tilted so molten metal blows away from the torch, then square up and cut',
  svg(500, 280, [
    ...[['1. Tilt 45°, pierce', -45], ['2. Rotate upright as it blows through', -20], ['3. Square, move into the cut', 0]].map(([n, rot], i) => { const x = 90 + i * 160; return [plate(x - 60, 160, 120, 16), g([rect(-14, -110, 28, 90, { fill: C.grey, rx: 6 }), rect(-10, -22, 20, 22, { fill: C.copper, stroke: C.accentDark }), line(0, 0, 0, 20, { stroke: C.blue, width: 4 })], { transform: `translate(${x},${150}) rotate(${rot})` }), i < 2 ? path(`M${x + 4},${162} q20,-18 40,-30`, { stroke: C.accent, width: 2, dash: '2 2' }) : line(x, 166, x, 176, { stroke: C.blue, width: 4 }), i === 2 ? line(x - 30, 186, x + 30, 186, { width: 1, arrow: 'end', stroke: C.muted }) : '', text(x, 210, n.split(',')[0], { anchor: 'middle', size: 11, weight: 600 }), note(x, 226, n.split(',')[1] ?? '', { anchor: 'middle', size: 10.5 })] }),
    note(250, 22, 'Pierce height 1.5-2 × cut height; pierce limit ≈ half the severance rating', { anchor: 'middle', size: 10.5 }),
    note(250, 250, 'Thick plate: start at the plate edge or a drilled hole instead of piercing', { anchor: 'middle', size: 10.5 }),
    caption(500, 280, 'Molten metal splashes back up the kerf until the pierce breaks through.'),
  ], { title: 'Plasma pierce sequence' }))

// ---------- Carbon-arc gouging ----------
fig('cutting-gouging/carbon-arc-gouging.svg', 'Carbon-arc gouging: air jet under the electrode, 35-45° angle, DCEP, 5-7 in of electrode past the holder',
  svg(500, 280, [
    plate(30, 210, 440, 20), path('M120,210 Q200,238 300,212', { fill: C.paper, stroke: C.accentDark, width: 1.5 }),
    g([rect(-70, -14, 140, 28, { fill: C.grey, rx: 6 }), rect(-90, -8, 20, 16, { fill: C.steelDark }), line(-90, 0, -200, 0, { stroke: '#333', width: 8, cap: 'butt' }), ...[-84, -76].map((x) => circle(x, 10, 3, { fill: C.blue, stroke: 'none' }))], { transform: 'translate(364,93) rotate(-35)' }),
    ...[0, 1, 2].map((i) => path(`M${292 - i * 6},${150 + i * 6} l-50,32`, { stroke: C.blue, width: 1.2, arrow: 'end', opacity: 0.8 })),
    line(200, 210, 340, 210, { dash: '4 3', width: 1, stroke: C.muted }), arc(200, 210, 70, -35, 0, { stroke: C.blue, width: 1 }), text(282, 196, '35-45°', { size: 12, fill: C.blue }),
    circle(200, 208, 6, { fill: C.accent, stroke: C.accentDark }),
    callout(1, 262, 150), callout(2, 300, 110), callout(3, 372, 70),
    legend(20, 30, ['air jet (80-100 psi) comes out UNDER the electrode, behind the arc', 'electrode extension 5-7 in max (more = it burns off and wanders)', 'holder: DCEP for copper-clad DC electrodes', 'steeper angle = deeper groove; push along, away from you'], { size: 10.5, gap: 13 }),
    line(60, 190, 120, 190, { width: 2, arrow: 'end' }), note(60, 180, 'travel'),
    caption(500, 280, 'Muffs plus plugs, full leathers, shade 12-14: the loudest job in the shop.'),
  ], { title: 'Carbon-arc gouging' }))

// ---------- Band saw TPI ----------
fig('cutting-gouging/bandsaw-tpi-rule.svg', 'Band saw blade selection: at least 3 teeth in the cut, no more than 24',
  svg(500, 240, [
    text(250, 22, 'Teeth per inch (TPI) versus material thickness', { anchor: 'middle', weight: 700 }),
    ...[['Too coarse', 20, 1, C.red, 'teeth straddle the work,\nstrip teeth'], ['Right: 3-24 teeth in the cut', 14, 3, C.green, '6-10 TPI for 1/2-1 in steel;\n14 for 1/4; 4-6 for 2 in+'], ['Too fine', 6, 8, C.red, 'gullets clog,\nslow and hot']].map(([n, pitch, teeth, c, d], i) => {
      const x = 40 + i * 155, y = 120
      const w = 130
      const tooth = Array.from({ length: Math.floor(w / pitch) }, (_, k) => `L${x + k * pitch + pitch / 2},${y - 10} L${x + (k + 1) * pitch},${y}`).join(' ')
      return [text(x + w / 2, 50, n, { anchor: 'middle', size: 11.5, weight: 600, fill: c }), path(`M${x},${y + 20} L${x},${y} ${tooth} L${x + w},${y + 20} Z`, { fill: C.grey }), rect(x + 40, y - 34, 50, 22, { fill: C.steel }), note(x + w / 2, 165, d, { anchor: 'middle', size: 10 })]
    }),
    caption(500, 240, 'Speed: 150-250 fpm mild steel, 60-100 stainless, 1,000+ aluminium.'),
  ], { title: 'Band saw TPI rule' }))

// ---------- Annular cutter vs twist drill ----------
fig('cutting-gouging/mag-drill-annular-cutter.svg', 'Mag drill with an annular cutter: cuts only the ring, ejects a slug, needs the safety strap and pilot',
  svg(500, 260, [
    text(130, 22, 'Annular cutter', { anchor: 'middle', weight: 700 }), text(370, 22, 'Twist drill', { anchor: 'middle', weight: 700 }),
    plate(40, 150, 180, 30), rect(100, 60, 60, 90, { fill: C.grey }), rect(112, 60, 36, 100, { fill: C.paper, stroke: 'none' }), rect(100, 60, 12, 90, { fill: C.steelDark }), rect(148, 60, 12, 90, { fill: C.steelDark }), line(130, 50, 130, 168, { stroke: C.ink, width: 2 }),
    circle(130, 168, 3, { fill: C.ink }), note(130, 200, 'removes only the ring (fast, low\nfeed force); pilot centres and\nejects the slug: keep feet clear', { anchor: 'middle', size: 10.5 }),
    plate(280, 150, 180, 30), poly([[350, 60], [390, 60], [390, 140], [370, 165], [350, 140]], { fill: C.steelDark }), note(370, 200, 'removes the whole hole as chips;\n3-4 × the feed force; step\ndrill for holes over 1/2 in', { anchor: 'middle', size: 10.5 }),
    caption(500, 260, 'Magnet needs flat, clean, thick steel: strap the drill on verticals.'),
  ], { title: 'Annular cutter vs twist drill' }))

// ---------- Oxy-acetylene hookup ----------
fig('oxy-fuel/oxy-acetylene-hookup.svg', 'Oxy-acetylene outfit: cylinders, regulators, check valves, flashback arrestors, hoses, torch',
  svg(500, 320, [
    rect(40, 60, 50, 220, { fill: '#2f7a3a', rx: 8 }), text(65, 300, 'oxygen', { anchor: 'middle', size: 11, weight: 600 }), rect(110, 100, 44, 180, { fill: '#8b1a1a', rx: 8 }), text(132, 300, 'acetylene', { anchor: 'middle', size: 11, weight: 600 }),
    rect(55, 44, 20, 16, { fill: C.steelDark }), rect(122, 84, 20, 16, { fill: C.steelDark }),
    rect(80, 30, 40, 30, { fill: C.grey, rx: 4 }), circle(90, 40, 8, { fill: C.paper }), circle(110, 40, 8, { fill: C.paper }), rect(150, 70, 40, 30, { fill: C.grey, rx: 4 }), circle(160, 80, 8, { fill: C.paper }), circle(180, 80, 8, { fill: C.paper }),
    path('M120,50 C200,50 220,150 330,150', { stroke: '#2f7a3a', width: 4 }), path('M190,90 C250,90 260,160 330,160', { stroke: '#8b1a1a', width: 4 }),
    rect(330, 140, 90, 30, { fill: C.grey, rx: 6 }), path('M420,155 L470,155 L478,140', { stroke: C.copper, width: 6 }), path('M478,140 q6,-14 0,-24', { stroke: C.blue, width: 3 }),
    ...[[124, 50], [194, 90]].map(([x, y]) => rect(x - 4, y - 6, 12, 12, { fill: C.accent, stroke: C.accentDark })), ...[[320, 150], [320, 160]].map(([x, y]) => rect(x - 6, y - 4, 12, 8, { fill: C.blue, stroke: 'none' })),
    callout(1, 100, 20), callout(2, 170, 60), callout(3, 130, 30), callout(4, 260, 105), callout(5, 300, 200), callout(6, 375, 190), callout(7, 65, 180),
    legend(190, 220, ['oxygen regulator (CGA 540, right-hand)', 'acetylene regulator (CGA 510, left-hand, 15 psi max)', 'flashback arrestors at the regulators', 'green oxygen hose, red fuel hose (B fittings)', 'check valves at the torch inlets', 'torch: cutting attachment or welding tip', 'cylinders upright and chained, caps off only in use'], { size: 9.5, gap: 13 }),
  ], { title: 'Oxy-acetylene hookup' }))

// ---------- Victor tip chart bars ----------
{
  const rows = [['Tip', 'Cuts (in)', 'Oxygen psi', 'Acetylene psi', 'Speed ipm'], ['000', '1/8', '20-25', '3-5', '20-30'], ['00', '1/4', '20-25', '3-5', '20-28'], ['0', '3/8', '25-30', '3-5', '18-26'], ['1', '1/2', '30-35', '3-5', '16-22'], ['2', '3/4', '30-35', '3-6', '15-20'], ['3', '1', '35-40', '3-6', '12-18'], ['4', '2', '40-45', '4-8', '8-12'], ['5', '3', '45-50', '5-11', '6-8'], ['6', '4-5', '50-60', '6-13', '4-6']]
  fig('oxy-fuel/victor-tip-chart.svg', 'Victor 1-101 / 3-101 cutting tip sizes by plate thickness with pressures and speeds', svg(500, 320, [text(250, 22, 'Victor 1-101 cutting tip quick chart (acetylene)', { anchor: 'middle', weight: 700 }), table(40, 36, rows, [60, 80, 100, 110, 90], { rowH: 24, size: 11 }), caption(500, 320, 'Full chart in the article. Pressures at the regulator with 25 ft hose.')], { title: 'Victor tip chart' }))
}
