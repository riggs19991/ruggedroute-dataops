// Drawings, schematics and P&IDs (part 1b): piping isometrics and spool sheets, PFD and P&ID reading,
// P&ID symbol sheets, ISA instrument tags and bubbles.
import { svg, text, line, rect, circle, path, poly, g, dim, leader, table, caption, box, callout, legend, note, fig, C, hatchRect, plate } from './lib.mjs'
import * as S from './lib-symbols.mjs'

const cell = (name, draw, note) => ({ name, draw, note })
const sheetFig = (file, alt, title, cells, opts = {}, cap) => {
  const h = S.sheetHeight(cells.length, opts)
  fig(file, alt, svg(500, h, [...S.sheet(cells, opts), cap ? caption(500, h, cap) : ''], { title }))
}
const thin = (x1, y1, x2, y2, o = {}) => line(x1, y1, x2, y2, { width: 0.8, stroke: C.muted, ...o })
const P = (x1, y1, x2, y2) => line(x1, y1, x2, y2, { width: 2.2 })
const hand = (x, y) => [line(x, y, x, y - 12, { width: 1.3 }), line(x - 6, y - 12, x + 6, y - 12, { width: 2 })]

// ================= Piping isometrics =================
const CS = Math.cos(Math.PI / 6), SN = 0.5
const isoPt = (ox, oy, e, n, u, k = 1) => [ox + (e + n) * CS * k, oy + (e - n) * SN * k - u * k]
const ip = (e, n, u) => isoPt(40, 130, e, n, u)
const iline = (a, b, w = 2) => line(a[0], a[1], b[0], b[1], { width: w })
fig('drawings/piping-iso-worked.svg', 'Worked piping isometric: north arrow, line number, a run east with butt-weld elbows, a riser, a run north with a gate valve between flanges, a field weld flag, weld numbers, spool numbers, coordinates and elevation callouts, and dimensions along each leg',
  (() => {
    const A = ip(0, 0, 0), B = ip(140, 0, 0), Cc = ip(140, 0, 70), D = ip(140, 110, 70), E = ip(240, 110, 70)
    const v1 = ip(140, 44, 70), f1 = ip(140, 30, 70), f2 = ip(140, 58, 70), w1 = ip(60, 0, 0), fw = ip(140, 90, 70)
    const dE = [CS, SN], dN = [CS, -SN]
    return svg(500, 330, [
      // north arrow: north runs up-right on this grid
      line(420, 60, 450, 43, { width: 1.5, arrow: 'end' }), text(456, 42, 'N', { size: 11, weight: 700 }), text(436, 74, 'plant north', { size: 7, fill: C.muted, anchor: 'middle' }),
      // pipe runs
      iline(A, B), iline(B, Cc), iline(Cc, D), iline(D, E),
      // elbows: BW dots at each fitting end
      S.weldDot(...ip(130, 0, 0)), S.weldDot(...ip(140, 0, 10)), S.weldDot(...ip(140, 0, 60)), S.weldDot(...ip(140, 10, 70)), S.weldDot(...ip(140, 100, 70)), S.weldDot(...ip(150, 110, 70)), S.weldDot(...w1), ...S.fieldWeld(...fw),
      // flanged gate valve on the north leg
      ...S.flangePair(f1[0], f1[1], dN[0], dN[1]), ...S.flangePair(f2[0], f2[1], dN[0], dN[1]), ...S.isoValve(v1[0], v1[1], dN[0], dN[1]),
      // nozzle at the end
      ...S.flangePair(E[0], E[1], dE[0], dE[1]), text(E[0] + 8, E[1] + 4, 'N2 on T-101', { size: 7.5 }),
      // dimensions along legs (iso dims sit parallel to the leg)
      text((A[0] + B[0]) / 2 - 8, (A[1] + B[1]) / 2 + 22, "12'-0\"", { size: 8.5, anchor: 'middle', angle: 30 }), text(B[0] + 8, (B[1] + Cc[1]) / 2 + 3, "7'-0\"", { size: 8.5 }), text((Cc[0] + D[0]) / 2 - 14, (Cc[1] + D[1]) / 2 - 10, "11'-0\"", { size: 8.5, anchor: 'middle', angle: -30 }), text((D[0] + E[0]) / 2 + 10, (D[1] + E[1]) / 2 - 12, "8'-0\"", { size: 8.5, anchor: 'middle', angle: 30 }),
      // callouts
      text(A[0] - 10, A[1] + 16, 'N 1250.0\nE 480.5\nEL 100\'-6" C/L', { size: 7, anchor: 'start', fill: C.muted }),
      leader(Cc[0], Cc[1], Cc[0] - 40, Cc[1] - 30, 'EL 107\'-6" C/L', { size: 7.5, anchor: 'end' }),
      leader(fw[0], fw[1], fw[0] + 24, fw[1] + 36, 'FW = field weld', { size: 7.5, anchor: 'start' }),
      leader(w1[0], w1[1], w1[0] + 10, w1[1] - 40, 'W3 shop weld', { size: 7.5, anchor: 'start' }),
      // spool boxes
      rect(60, 230, 40, 14, { fill: C.soft, width: 1 }), text(80, 240, 'SP-1', { size: 7.5, anchor: 'middle', weight: 700 }), thin(80, 230, B[0] - 20, B[1] + 6),
      rect(330, 160, 40, 14, { fill: C.soft, width: 1 }), text(350, 170, 'SP-2', { size: 7.5, anchor: 'middle', weight: 700 }), thin(350, 160, E[0] - 30, E[1] - 12),
      text(250, 300, '6"-P-1012-A1A-IH', { size: 10, anchor: 'middle', weight: 700 }), text(250, 314, 'line number: size - service - number - spec - insulation', { size: 7.5, anchor: 'middle', fill: C.muted }),
      text(20, 30, 'ISO 1012-01   scale NTS', { size: 8, weight: 700 }), text(20, 42, 'bent lines are drawn straight: read the dimensions, never scale', { size: 7, fill: C.muted }),
    ], { title: 'Piping isometric' })
  })())

fig('drawings/line-number-decoder.svg', 'Decoder for a piping line number 6 inch P 1012 A1A IH: nominal size, service code, sequence number, pipe class or spec, insulation code, with a table of common service codes and what the spec letters carry',
  svg(500, 280, [
    text(250, 34, '6"-P-1012-A1A-IH', { anchor: 'middle', weight: 700, size: 22 }),
    leader(165, 40, 40, 74, '6" = nominal pipe size', { size: 8, anchor: 'start' }), leader(198, 40, 130, 100, 'P = service (process)', { size: 8, anchor: 'start' }),
    leader(250, 40, 250, 74, '1012 = line sequence number', { size: 8, anchor: 'middle' }), leader(318, 40, 330, 100, 'A1A = pipe class (spec)', { size: 8 }), leader(350, 40, 360, 74, 'IH = insulation (heat)', { size: 8 }),
    table(20, 120, [['service', 'means'], ['P', 'process'], ['CW / CWR', 'cooling water supply / return'], ['S / C', 'steam / condensate'], ['IA / PA', 'instrument / plant air'], ['HO', 'hydraulic oil'], ['LO', 'lube oil']], [60, 150], { rowH: 16, size: 7.5 }),
    table(250, 120, [['spec letter', 'carries'], ['class A1A', 'material CS, 150 lb'], ['class B1A', 'material CS, 300 lb'], ['class D1S', 'stainless, 150 lb'], ['IH / IC / IP', 'heat / cold / personnel'], ['ET / ST', 'electric / steam traced']], [70, 150], { rowH: 16, size: 7.5 }),
    caption(500, 280, 'The spec letter is the one to check: it sets gasket, bolting and rating.'),
  ], { title: 'Line number decoder' }))

sheetFig('drawings/pipe-fitting-symbols.svg', 'Piping fitting and joint symbols as drawn on isometrics and orthographic piping drawings: butt-weld, socket-weld, threaded and flanged elbows, tee, concentric and eccentric reducers, cap, weldolet, union, coupling, plus flange and blind flange',
  'Fitting and joint symbols', [
  cell('butt-weld elbow', (x, y) => [P(x - 26, y + 8, x, y + 8), P(x, y + 8, x, y - 18), S.weldDot(x - 8, y + 8), S.weldDot(x, y)], 'dot = shop weld'),
  cell('socket-weld elbow', (x, y) => [P(x - 26, y + 8, x, y + 8), P(x, y + 8, x, y - 18), S.swTick(x - 8, y + 8, 1, 0), S.swTick(x, y, 0, 1)], 'one tick each joint'),
  cell('threaded elbow', (x, y) => [P(x - 26, y + 8, x, y + 8), P(x, y + 8, x, y - 18), ...S.thrTicks(x - 8, y + 8, 1, 0), ...S.thrTicks(x, y, 0, 1)], 'two ticks each joint'),
  cell('flanged elbow', (x, y) => [P(x - 26, y + 8, x, y + 8), P(x, y + 8, x, y - 18), ...S.flangePair(x - 10, y + 8, 1, 0), ...S.flangePair(x, y - 2, 0, 1)], 'two bars = flange pair'),
  cell('tee (BW)', (x, y) => [P(x - 26, y, x + 26, y), P(x, y, x, y - 20), S.weldDot(x - 12, y), S.weldDot(x + 12, y), S.weldDot(x, y - 12)], 'three welds'),
  cell('concentric reducer', (x, y) => [P(x - 26, y, x - 10, y), poly([[x - 10, y - 8], [x + 10, y - 4], [x + 10, y + 4], [x - 10, y + 8]], { width: 1.5 }), P(x + 10, y, x + 26, y)], '6 x 4 CONC'),
  cell('eccentric reducer', (x, y) => [P(x - 26, y, x - 10, y), poly([[x - 10, y - 8], [x + 10, y - 2], [x + 10, y + 8], [x - 10, y + 8]], { width: 1.5 }), P(x + 10, y + 3, x + 26, y + 3)], 'flat side up or down'),
  cell('cap', (x, y) => [P(x - 26, y, x - 4, y), path(`M${x - 4},${y - 8} l6,0 a8,8 0 0 1 0,16 l-6,0`, { width: 1.5 }), S.weldDot(x - 6, y)], 'BW cap'),
  cell('weldolet / sockolet', (x, y) => [P(x - 26, y + 6, x + 26, y + 6), path(`M${x - 8},${y + 6} a8,8 0 0 1 16,0`, { width: 1.5 }), P(x, y - 2, x, y - 20), S.weldDot(x, y - 10)], 'branch on the run'),
  cell('union', (x, y) => [P(x - 26, y, x - 6, y), line(x - 4, y - 8, x - 4, y + 8, { width: 1.6 }), line(x, y - 8, x, y + 8, { width: 1.6 }), line(x + 4, y - 8, x + 4, y + 8, { width: 1.6 }), P(x + 6, y, x + 26, y)], 'threaded, take-apart'),
  cell('coupling (THD)', (x, y) => [P(x - 26, y, x + 26, y), ...S.thrTicks(x - 6, y, 1, 0), ...S.thrTicks(x + 6, y, 1, 0)], 'two threaded joints'),
  cell('flange and blind', (x, y) => [P(x - 30, y, x - 12, y), ...S.flangePair(x - 8, y, 1, 0), P(x - 4, y, x + 10, y), line(x + 12, y - 7, x + 12, y + 7, { width: 1.6 }), line(x + 16, y - 7, x + 16, y + 7, { width: 3.2 })], 'blind = thick bar'),
], { cols: 4, cellH: 84, symH: 44 }, 'Dot = butt weld, one tick = socket, two = threaded, two bars = flanged.')

fig('drawings/iso-valves-inline.svg', 'Valves and inline items on an isometric: gate, globe, ball and check valves drawn on the pipe direction with the handwheel orientation shown, a control valve with its actuator, a strainer, a spec break and an insulation symbol',
  svg(500, 260, [
    ...[['gate', 60], ['globe', 150], ['ball', 240], ['check', 330]].map(([k, x]) => [P(x - 40, 80, x - 12, 80), ...S.pvalve(x, 80, k, { s: 11 }), P(x + 12, 80, x + 40, 80), text(x, 112, k, { size: 9, anchor: 'middle', weight: 600 })]),
    ...hand(60, 72), ...hand(150, 72), line(240, 72, 240, 60, { width: 1.3 }), line(234, 60, 246, 60, { width: 2 }), text(240, 54, 'lever', { size: 6.5, anchor: 'middle', fill: C.muted }),
    text(60, 124, 'handwheel drawn\nwhere it points', { size: 7, anchor: 'middle', fill: C.muted }), text(330, 124, 'arrow = flow\ndirection', { size: 7, anchor: 'middle', fill: C.muted }),
    // control valve with diaphragm
    P(380, 80, 408, 80), ...S.pvalve(420, 80, 'globe', { s: 11 }), ...S.actuator(420, 72, 'diaphragm', { fail: 'FC' }), P(432, 80, 460, 80), text(420, 112, 'control valve', { size: 9, anchor: 'middle', weight: 600 }), text(420, 124, 'FCV-104, fails closed', { size: 7, anchor: 'middle', fill: C.muted }),
    // strainer, spec break, insulation
    P(40, 190, 70, 190), ...S.strainerY(84, 190), P(98, 190, 130, 190), text(84, 216, 'Y strainer', { size: 9, anchor: 'middle', weight: 600 }),
    P(170, 190, 260, 190), line(215, 178, 215, 202, { width: 1.4 }), line(219, 178, 219, 202, { width: 1.4 }), text(212, 172, 'A1A', { size: 7.5, anchor: 'end' }), text(222, 172, 'B1A', { size: 7.5 }), text(217, 216, 'spec break', { size: 9, anchor: 'middle', weight: 600 }), text(217, 228, 'class changes here', { size: 7, anchor: 'middle', fill: C.muted }),
    ...S.pline(300, 190, 400, 190, 'insulated'), text(350, 216, 'insulated line', { size: 9, anchor: 'middle', weight: 600 }), text(350, 228, 'IH: hot, do not lean on it', { size: 7, anchor: 'middle', fill: C.muted }),
    caption(500, 260, 'A valve on an iso keeps its direction: the stem shows the handwheel side.'),
  ], { title: 'Valves and inline items on an iso' }))

fig('drawings/weld-numbers-and-spools.svg', 'Isometric extract showing shop welds as dots with weld numbers, field welds as flagged dots, spool break points and boxed spool numbers, so the fabricator knows what to build in the shop and the millwright what gets welded in the field',
  (() => {
    const ipw = (e, n, u) => isoPt(40, 150, e, n, u)
    const A = ipw(0, 0, 40), B = ipw(140, 0, 40), Cc = ipw(140, 90, 40), D = ipw(140, 90, 110)
    const w = (e, n, u, lab, dy = -8) => { const p = ipw(e, n, u); return [S.weldDot(p[0], p[1]), text(p[0] + 6, p[1] + dy, lab, { size: 7, weight: 700 })] }
    const fw = ipw(140, 45, 40)
    return svg(500, 280, [
      iline(A, B), iline(B, Cc), iline(Cc, D),
      ...w(30, 0, 40, 'W1'), ...w(70, 0, 40, 'W2'), ...w(132, 0, 40, 'W3'), ...w(140, 8, 40, 'W4'), ...w(140, 82, 40, 'W6', 14), ...w(140, 90, 48, 'W7', -6),
      ...S.fieldWeld(fw[0], fw[1]), text(fw[0] + 8, fw[1] + 4, 'FW5', { size: 7.5, weight: 700, fill: C.red }),
      ...S.flangePair(D[0], D[1], 0, 1),
      rect(60, 220, 44, 14, { fill: C.soft, width: 1 }), text(82, 230, 'SP-1', { size: 7.5, anchor: 'middle', weight: 700 }), rect(300, 200, 44, 14, { fill: C.soft, width: 1 }), text(322, 210, 'SP-2', { size: 7.5, anchor: 'middle', weight: 700 }),
      thin(82, 220, A[0] + 40, A[1] + 26), thin(322, 200, Cc[0] + 30, Cc[1] - 20),
      legend(290, 40, ['shop weld: dot, numbered W1, W2 ...', 'field weld: dot with a flag, FW', 'spool = what arrives from the shop;\nthe field weld joins spools'], { size: 8, gap: 12 }),
      caption(500, 280, 'Count the field welds on the iso: that is the welding you will do on site.'),
    ], { title: 'Weld numbers and spools' })
  })())

sheetFig('drawings/pipe-supports-symbols.svg', 'Pipe support symbols on piping drawings: shoe, anchor, guide, rest support, rod hanger, spring hanger and trunnion, each with its support tag format',
  'Pipe support symbols', [
  cell('rest / shoe', (x, y) => [P(x - 26, y - 6, x + 26, y - 6), rect(x - 8, y - 3, 16, 8, { fill: C.steel, width: 1 }), line(x - 20, y + 10, x + 20, y + 10, { width: 2 })], 'weight only, slides'),
  cell('anchor', (x, y) => [P(x - 26, y - 6, x + 26, y - 6), rect(x - 8, y - 3, 16, 8, { fill: C.steel, width: 1 }), line(x - 20, y + 10, x + 20, y + 10, { width: 2 }), path(`M${x - 8},${y + 5} l-6,5 M${x + 8},${y + 5} l6,5`, { width: 1.4 }), text(x + 22, y + 4, 'A', { size: 8, weight: 700 })], 'fixed: no movement'),
  cell('guide', (x, y) => [P(x - 26, y - 6, x + 26, y - 6), rect(x - 12, y - 14, 4, 16, { fill: C.steel, width: 1 }), rect(x + 8, y - 14, 4, 16, { fill: C.steel, width: 1 }), line(x - 20, y + 10, x + 20, y + 10, { width: 2 }), text(x + 22, y + 4, 'G', { size: 8, weight: 700 })], 'slides axially only'),
  cell('rod hanger', (x, y) => [P(x - 26, y + 8, x + 26, y + 8), line(x, y + 8, x, y - 18, { width: 1.4 }), line(x - 12, y - 18, x + 12, y - 18, { width: 2 }), path(`M${x - 10},${y + 4} a10,8 0 0 0 20,0`, { width: 1.2 })], 'from steel above'),
  cell('spring hanger', (x, y) => [P(x - 26, y + 10, x + 26, y + 10), line(x, y + 10, x, y - 2, { width: 1.4 }), rect(x - 7, y - 20, 14, 18), path(`M${x},${y - 18} l-4,3 l8,3 l-8,3 l8,3 l-4,3`, { width: 1 }), line(x, y - 20, x, y - 26, { width: 1.4 }), line(x - 12, y - 26, x + 12, y - 26, { width: 2 })], 'V variable, C constant'),
  cell('trunnion', (x, y) => [P(x - 26, y - 8, x + 26, y - 8), rect(x - 5, y - 8, 10, 16, { fill: C.steel, width: 1 }), line(x - 20, y + 10, x + 20, y + 10, { width: 2 })], 'welded dummy leg'),
  cell('support tag', (x, y) => [rect(x - 30, y - 10, 60, 20, { fill: C.soft, width: 1 }), text(x, y + 4, 'PS-1012-03', { size: 8, anchor: 'middle', weight: 700 })], 'type-line-sequence'),
  cell('elevation on iso', (x, y) => [P(x - 26, y + 8, x + 26, y + 8), text(x, y - 6, 'BOP EL 103\'-2"', { size: 7.5, anchor: 'middle' }), text(x, y - 18, 'C/L EL 103\'-5 1/4"', { size: 7.5, anchor: 'middle' })], 'BOP = bottom of pipe'),
], { cols: 4, cellH: 84, symH: 44 }, 'An anchor fixes, a guide steers, a shoe only carries the weight.')

fig('drawings/spool-sheet.svg', 'A spool sheet: the spool drawn as its own small isometric with weld numbers, the bill of material listing pipe, fittings and flanges by item with size, description, material and quantity, and the header with spool number, line number, paint and test data',
  (() => {
    const q = (e, n, u) => isoPt(40, 118, e, n, u, 1.3)
    const A = q(0, 0, 0), B = q(100, 0, 0), Cc = q(100, 0, 60)
    return svg(500, 300, [
      rect(20, 20, 460, 262, { width: 1 }), line(20, 44, 480, 44, { width: 0.8 }),
      text(26, 36, 'SPOOL SP-1   LINE 6"-P-1012-A1A   ISO 1012-01   PAINT SYS 2   HYDRO 225 PSI', { size: 7.5, weight: 700 }),
      iline(A, B), iline(B, Cc), S.weldDot(...q(20, 0, 0)), S.weldDot(...q(92, 0, 0)), S.weldDot(...q(100, 0, 8)), S.weldDot(...q(100, 0, 52)), ...S.flangePair(Cc[0], Cc[1], 0, 1),
      text(q(20, 0, 0)[0] + 4, q(20, 0, 0)[1] - 8, 'W1', { size: 7, weight: 700 }), text(q(92, 0, 0)[0] + 4, q(92, 0, 0)[1] - 8, 'W2', { size: 7, weight: 700 }), text(q(100, 0, 8)[0] + 8, q(100, 0, 8)[1], 'W3', { size: 7, weight: 700 }), text(q(100, 0, 52)[0] + 8, q(100, 0, 52)[1], 'W4', { size: 7, weight: 700 }),
      text((A[0] + B[0]) / 2, (A[1] + B[1]) / 2 + 20, "8'-2\"", { size: 8, anchor: 'middle', angle: 30 }), text(Cc[0] + 12, (B[1] + Cc[1]) / 2 + 4, "3'-6\"", { size: 8 }),
      text(A[0] + 2, A[1] + 30, 'FW to SP-2', { size: 7, fill: C.red }), text(Cc[0] - 10, Cc[1] - 12, 'FLG to N2', { size: 7, fill: C.muted, anchor: 'end' }),
      table(240, 54, [['ITEM', 'QTY', 'DESCRIPTION', 'MATL'], ['1', "9'-8\"", '6" SCH 40 PIPE', 'A106-B'], ['2', '1', '6" 90° LR ELL BW', 'A234 WPB'], ['3', '1', '6" 150# RFWN FLG', 'A105'], ['4', '1', '6" x 4" CONC RED', 'A234 WPB'], ['5', '4', 'WELD, BW', 'E7018']], [30, 34, 110, 54], { rowH: 17, size: 7 }),
      text(240, 176, 'cut length = c/c dims minus take-outs (see fit-up article)', { size: 7, fill: C.muted }),
      note(250, 270, 'one sheet per spool: what to cut, what to weld, what to send', { anchor: 'middle', size: 8.5 }),
    ], { title: 'Spool sheet' })
  })())

fig('drawings/take-out-from-iso.svg', 'Working a cut length from an isometric dimension: the centre-to-centre dimension between two elbows, the take-out of each 6 inch long-radius elbow, the root gaps, and the resulting pipe cut length',
  svg(500, 240, [
    P(60, 120, 400, 120), path('M60,120 a30,30 0 0 0 -30,-30', { width: 2.2 }), path('M400,120 a30,30 0 0 1 30,-30', { width: 2.2 }),
    S.weldDot(90, 120), S.weldDot(370, 120), thin(30, 90, 30, 60), thin(430, 90, 430, 60),
    dim(30, 70, 430, 70, "c/c 10'-0\"", { off: 0, size: 9 }),
    dim(30, 120, 90, 120, '9"', { off: 40, size: 8 }), dim(370, 120, 430, 120, '9"', { off: 40, size: 8 }), dim(90, 120, 370, 120, "cut 8'-5 3/4\"", { off: 64, size: 9, fill: C.blue }),
    text(60, 100, 'take-out', { size: 7, anchor: 'middle', fill: C.muted }), text(400, 100, 'take-out', { size: 7, anchor: 'middle', fill: C.muted }),
    table(300, 150, [['step', 'value'], ["c/c", "10'-0\""], ['less 2 take-outs', "2 x 9\" = 1'-6\""], ['less 2 root gaps', '2 x 1/8" = 1/4"'], ['cut length', "8'-5 3/4\""]], [80, 100], { rowH: 15, size: 7.5 }),
    note(20, 200, 'take-out for a 6" LR 90° = 1.5 x NPS = 9"; the dimension\non the iso is always centreline to centreline', { size: 8 }),
  ], { title: 'Take-out from an iso dimension' }))

// ================= PFD and P&ID =================
const opc = (x, y, lab, dir = 'out') => [poly(dir === 'out' ? [[x - 20, y - 8], [x + 10, y - 8], [x + 20, y], [x + 10, y + 8], [x - 20, y + 8]] : [[x - 10, y - 8], [x + 20, y - 8], [x + 20, y + 8], [x - 10, y + 8], [x - 20, y]], { width: 1.3, fill: C.paper }), text(x + (dir === 'out' ? -3 : 3), y + 3, lab, { size: 6.5, anchor: 'middle', weight: 700 })]
const sig = (x1, y1, x2, y2, kind) => S.pline(x1, y1, x2, y2, kind)
fig('drawings/pfd-vs-pid.svg', 'The same feed pump drawn on a process flow diagram and on a piping and instrumentation diagram: the PFD shows only the equipment, main flow path, stream numbers and key conditions, while the P&ID adds every valve, line number, instrument, control loop and connection',
  svg(500, 300, [
    text(125, 20, 'PFD', { anchor: 'middle', weight: 700, size: 12 }), text(375, 20, 'P&ID', { anchor: 'middle', weight: 700, size: 12 }),
    // PFD
    ...S.vesselV(60, 90, 30, 70), text(60, 44, 'T-101', { size: 8, anchor: 'middle', weight: 700 }), P(60, 125, 60, 160), P(60, 160, 120, 160), ...S.pumpCentrifugal(134, 160, 12), text(134, 186, 'P-101', { size: 8, anchor: 'middle', weight: 700 }),
    P(152, 148, 210, 148), line(210, 148, 222, 148, { width: 2.2, arrow: 'end' }), poly([[110, 140], [122, 130], [134, 140], [122, 150]], { fill: C.paper, width: 1.2 }), text(122, 143, '3', { size: 7, anchor: 'middle', weight: 700 }),
    poly([[184, 128], [196, 118], [208, 128], [196, 138]], { fill: C.paper, width: 1.2 }), text(196, 131, '4', { size: 7, anchor: 'middle', weight: 700 }),
    table(20, 200, [['stream', '3', '4'], ['flow gpm', '250', '250'], ['press psig', '5', '95'], ['temp °F', '140', '141']], [60, 40, 40], { rowH: 14, size: 7 }),
    text(125, 278, 'what flows, how much, at what conditions', { size: 7.5, anchor: 'middle', fill: C.muted }),
    // P&ID
    ...S.vesselV(300, 90, 30, 70), text(300, 44, 'T-101', { size: 8, anchor: 'middle', weight: 700 }), P(300, 125, 300, 160), P(300, 160, 318, 160), ...S.pvalve(326, 160, 'gate', { s: 6 }), P(334, 160, 348, 160), ...S.strainerY(356, 160), P(364, 160, 376, 160), ...S.pumpCentrifugal(390, 160, 12), text(390, 186, 'P-101A', { size: 7.5, anchor: 'middle', weight: 700 }),
    P(408, 148, 418, 148), ...S.pvalve(426, 148, 'check', { s: 6 }), P(434, 148, 442, 148), ...S.pvalve(450, 148, 'gate', { s: 6 }), P(458, 148, 462, 148), ...opc(478, 148, 'E-2', 'out'),
    ...S.bubble(330, 100, 'LT', '101', { r: 10 }), thin(320, 100, 315, 100), ...S.bubble(370, 70, 'LIC', '101', { shape: 'shared', loc: 'panel', r: 10 }), ...sig(340, 100, 360, 78, 'electric'),
    ...S.bubble(440, 110, 'PI', '102', { r: 10 }), thin(440, 120, 440, 148),
    text(300, 172, '6"-P-1012-A1A', { size: 6, anchor: 'start', fill: C.muted }),
    ...S.drainSym(300, 160), text(300, 202, 'drain', { size: 6, anchor: 'middle', fill: C.muted }),
    text(375, 244, 'every valve, instrument, line number,\nconnection and drain', { size: 7.5, anchor: 'middle', fill: C.muted }),
    caption(500, 300, 'PFD for the process story; P&ID for what is actually bolted to the floor.'),
  ], { title: 'PFD versus P&ID' }))

fig('drawings/pid-legend-extract.svg', 'Extract of a P&ID legend sheet: the project-specific symbols for lines, valves, instruments and equipment, the line number format, the instrument bubble location convention and the abbreviations block',
  svg(500, 330, [
    text(250, 20, 'LEGEND SHEET P-000 (extract)', { anchor: 'middle', weight: 700, size: 11 }),
    text(30, 44, 'LINES', { size: 8, weight: 700 }),
    ...[['process', 'process'], ['utility', 'utility'], ['pneumatic signal', 'pneumatic'], ['electric signal', 'electric'], ['software link', 'software'], ['capillary', 'capillary']].map(([lab, k], i) => [...S.pline(30, 60 + i * 20, 90, 60 + i * 20, k), text(98, 63 + i * 20, lab, { size: 7.5 })]),
    text(200, 44, 'VALVES', { size: 8, weight: 700 }),
    ...[['gate', 'gate'], ['globe', 'globe'], ['ball', 'ball'], ['butterfly', 'butterfly'], ['check', 'check'], ['relief', 'relief']].map(([lab, k], i) => [...S.pvalve(214, 62 + i * 20, k, { s: 7 }), text(232, 65 + i * 20, lab, { size: 7.5 })]),
    text(320, 44, 'INSTRUMENT LOCATION', { size: 8, weight: 700 }),
    ...[['field', 'field'], ['main panel', 'panel'], ['behind panel', 'behind'], ['local panel', 'local']].map(([lab, k], i) => [...S.bubble(334, 66 + i * 26, 'XX', '', { loc: k, r: 10 }), text(352, 69 + i * 26, lab, { size: 7.5 })]),
    ...S.bubble(334, 176, 'XX', '', { shape: 'shared', loc: 'panel', r: 10 }), text(352, 179, 'shared display (DCS)', { size: 7.5 }), ...S.bubble(334, 202, 'XX', '', { shape: 'plc', r: 10 }), text(352, 205, 'PLC function', { size: 7.5 }),
    text(30, 200, 'LINE NUMBER', { size: 8, weight: 700 }), text(30, 214, 'SIZE - SERVICE - NUMBER - SPEC - INSUL', { size: 7.5 }), text(30, 226, 'e.g. 6"-P-1012-A1A-IH', { size: 7.5, fill: C.muted }),
    text(30, 250, 'ABBREVIATIONS', { size: 8, weight: 700 }),
    text(30, 264, 'FC fail closed   FO fail open   FL fail last   LO locked open   LC locked closed', { size: 6.8 }), text(30, 276, 'NC normally closed   CSO car-sealed open   SP set point   RO restriction orifice   SC sample point', { size: 6.8 }),
    text(30, 296, 'NOTE: symbols not shown are per ISA-5.1 and PIP PIC001', { size: 7.5, fill: C.muted }),
    caption(500, 330, 'The legend sheet is sheet one for a reason: read it before the P&ID.'),
  ], { title: 'P&ID legend extract' }))

// ---------- the sample P&ID (pump loop), reused by the quiz ----------
const pidPumpLoop = () => [
  // tank T-101 with level instruments
  ...S.vesselV(70, 130, 44, 100), text(100, 196, 'T-101 FEED TANK', { size: 7.5, weight: 700 }), line(52, 140, 92, 140, { width: 0.8, dash: '3 2' }),
  ...S.bubble(120, 112, 'LT', '101', { r: 12 }), thin(108, 112, 92, 112), ...S.bubble(160, 62, 'LIC', '101', { shape: 'shared', loc: 'panel', r: 12 }), ...sig(128, 102, 152, 74, 'electric'),
  // suction line to the pumps
  P(70, 180, 70, 215), P(70, 215, 112, 215), ...S.strainerY(120, 215), P(128, 215, 150, 215), ...S.pvalve(160, 215, 'gate', { s: 8 }), ...hand(160, 209), P(168, 215, 236, 215), S.junction(200, 215),
  text(80, 230, '6"-P-1012-A1A', { size: 6.5, fill: C.muted }),
  // pump A
  ...S.pumpCentrifugal(250, 215, 14), ...S.driver(250, 244, 'M', 7), line(250, 229, 250, 237, { width: 1 }), text(275, 246, 'P-101A', { size: 7.5, weight: 700 }),
  P(270, 201, 292, 201), ...S.pvalve(300, 201, 'check', { s: 8 }), P(308, 201, 342, 201), ...S.pvalve(350, 201, 'gate', { s: 8 }), ...hand(350, 195), P(358, 201, 380, 201),
  // pump B (spare) in parallel
  P(200, 215, 200, 270), P(200, 270, 236, 270), ...S.pumpCentrifugal(250, 270, 14), ...S.driver(250, 298, 'M', 7), line(250, 284, 250, 291, { width: 1 }), text(275, 300, 'P-101B (spare)', { size: 7.5, weight: 700 }),
  P(270, 256, 292, 256), ...S.pvalve(300, 256, 'check', { s: 8 }), P(308, 256, 342, 256), ...S.pvalve(350, 256, 'gate', { s: 8 }), ...hand(350, 250), P(358, 256, 380, 256),
  ...S.drainSym(215, 270), text(215, 306, 'drain', { size: 6, anchor: 'middle', fill: C.muted }),
  // riser and header
  P(380, 256, 380, 120), S.junction(380, 201), P(380, 120, 460, 120), ...S.ventSym(392, 120), text(372, 180, '4"-P-1013-A1A', { size: 6.5, anchor: 'end', fill: C.muted }),
  ...S.bubble(412, 160, 'PI', '102', { r: 12 }), thin(400, 160, 380, 160), S.junction(380, 160),
  ...S.orificePlate(408, 120), ...S.bubble(408, 84, 'FT', '104', { r: 12 }), thin(408, 96, 408, 112),
  ...S.bubble(450, 50, 'FIC', '104', { shape: 'shared', loc: 'panel', r: 12 }), ...sig(420, 84, 438, 58, 'electric'), ...sig(450, 62, 450, 88, 'pneumatic'),
  ...S.pvalve(450, 120, 'globe', { s: 8 }), ...S.actuator(450, 112, 'diaphragm', { fail: 'FC' }), text(450, 140, 'FCV-104', { size: 6.5, anchor: 'middle' }),
  line(424, 112, 424, 128, { width: 1.2 }), line(428, 112, 428, 128, { width: 1.2 }), text(426, 106, 'A1A|B1A', { size: 5.5, anchor: 'middle' }),
  ...opc(480, 120, 'E-201', 'out'), text(480, 140, 'TO E-201', { size: 6, anchor: 'middle', fill: C.muted }),
  // minimum-flow line back to the tank
  S.junction(380, 140), P(380, 140, 210, 140), ...S.pvalve(300, 140, 'globe', { s: 7 }), ...S.orificePlate(250, 140), text(250, 132, 'RO', { size: 6.5, anchor: 'middle' }), P(210, 140, 210, 40), P(210, 40, 70, 40), P(70, 40, 70, 80), text(215, 60, '2"-P-1014-A1A min flow', { size: 6.5, fill: C.muted }),
]
fig('drawings/sample-pid-pump-loop.svg', 'Sample P&ID of a feed pump loop: feed tank T-101 with level transmitter and controller, suction strainer and isolation valve, duty pump P-101A and spare P-101B each with check valve and discharge isolation, drain, riser with vent and pressure gauge, discharge header with orifice flow transmitter, flow controller and fail-closed control valve, spec break and off-page connector, and a minimum-flow line with restriction orifice back to the tank',
  svg(500, 330, [...pidPumpLoop(), caption(500, 330, 'Trace it: tank, strainer, valve, pump, check, valve, header, FCV, off-page.')], { title: 'Sample P&ID: feed pump loop' }))

fig('drawings/pump-loop-isolation-points.svg', 'The same pump loop marked up for a maintenance isolation of P-101A: numbered isolation points for suction valve, discharge valve, the check valve that is not an isolation, the drain and vent used to prove zero energy, the minimum-flow line that can feed back, the spare pump that stays in service and the motor disconnect',
  svg(500, 360, [...pidPumpLoop(),
    callout(1, 160, 236), callout(2, 350, 178), callout(3, 300, 178), callout(4, 215, 322), callout(5, 392, 100), callout(6, 300, 158), callout(7, 250, 264),
    legend(20, 318, ['suction isolation: close, tag', 'discharge isolation: close, tag', 'check valve: NOT an isolation', 'drain: open to prove zero energy'], { size: 7.5, gap: 10 }),
    legend(260, 318, ['vent: bleed the riser', 'min-flow can feed back: isolate it', 'spare P-101B stays live behind valve 2'], { size: 7.5, gap: 10, start: 5 }),
  ], { title: 'Isolation points from the P&ID' }))

fig('drawings/tracing-a-line.svg', 'Tracing a line end to end on a P&ID: start at the line number, follow the heavy line through every valve and instrument, note every branch, and follow off-page connectors to the sheet that continues it, with the route highlighted and the branches listed',
  svg(500, 300, [
    ...opc(30, 100, 'P-101', 'in'), P(54, 100, 130, 100), ...S.pvalve(140, 100, 'gate', { s: 8 }), P(150, 100, 200, 100), S.junction(200, 100), P(200, 100, 200, 170), ...S.pvalve(200, 180, 'gate', { s: 7 }), P(200, 188, 200, 220), text(208, 224, 'to drain header', { size: 7, fill: C.muted }),
    P(200, 100, 260, 100), ...S.pvalve(270, 100, 'globe', { s: 8 }), ...S.actuator(270, 92, 'diaphragm', { fail: 'FO' }), text(270, 122, 'TCV-210', { size: 6.5, anchor: 'middle' }), P(280, 100, 340, 100), ...S.exchangerST(360, 100, 14), P(382, 100, 440, 100), ...opc(462, 100, 'P-104', 'out'),
    ...S.bubble(320, 60, 'TI', '211', { r: 11 }), thin(320, 71, 320, 100),
    text(60, 90, '3"-CW-2101-A1A', { size: 7, fill: C.muted }),
    // highlight route
    line(54, 100, 440, 100, { width: 8, stroke: C.accent, opacity: 0.3 }),
    table(30, 150, [['step', 'what you found'], ['1', 'line 3"-CW-2101 arrives from sheet P-101'], ['2', 'gate valve, hand, no tag: isolation'], ['3', 'branch down: drain to header, valved'], ['4', 'TCV-210 control valve, fails open'], ['5', 'TI-211 local thermometer, then E-301 shell side'], ['6', 'leaves to sheet P-104: keep tracing there']], [30, 240], { rowH: 15, size: 7.5 }),
    note(370, 170, 'a branch you did not\nnotice is the one that\nrefills the line you\njust drained', { size: 8 }),
    caption(500, 300, 'One line, one finger, every branch written down before you touch a valve.'),
  ], { title: 'Tracing a line end to end' }))

fig('drawings/equipment-tag-decoder.svg', 'Decoder for equipment tags on P&IDs: the letter code for the equipment type, the area or unit number, the sequence and the A B suffix for duplicated units, with a table of common equipment letters',
  svg(500, 250, [
    text(250, 34, 'P-101A', { anchor: 'middle', weight: 700, size: 24 }),
    leader(216, 40, 30, 74, 'P = pump (equipment type)', { size: 8, anchor: 'start' }), leader(250, 40, 250, 88, '1 = area or unit, 01 = sequence', { size: 8, anchor: 'middle' }), leader(284, 40, 340, 74, 'A = first of two (B is the spare)', { size: 8 }),
    table(30, 100, [['letter', 'equipment'], ['P', 'pump'], ['C / K', 'compressor'], ['B', 'blower / fan'], ['T / TK', 'tank'], ['V / D', 'vessel / drum'], ['E / HX', 'heat exchanger']], [50, 120], { rowH: 15, size: 7.5 }),
    table(260, 100, [['letter', 'equipment'], ['F', 'filter'], ['A / M', 'agitator / mixer'], ['CV', 'conveyor'], ['GB / R', 'gearbox / reducer'], ['M / MTR', 'motor'], ['H', 'hoist / heater (check legend)']], [50, 160], { rowH: 15, size: 7.5 }),
    note(250, 236, 'letters vary by owner: the legend sheet wins over this table', { anchor: 'middle', size: 8.5 }),
  ], { title: 'Equipment tag decoder' }))

fig('drawings/off-page-connectors-tie-ins.svg', 'Off-page connectors, tie-ins and holds: the arrow-shaped connector with the sheet it continues on, an incoming connector, a tie-in point symbol with its number for a connection to existing piping, existing equipment shown in a lighter line, a hold cloud, and a by-others boundary',
  svg(500, 270, [
    text(120, 22, 'Off-page connectors', { anchor: 'middle', weight: 700, size: 10 }),
    ...opc(50, 60, 'P-104', 'in'), P(74, 60, 180, 60), ...opc(206, 60, 'P-106', 'out'), text(50, 82, 'from sheet P-104', { size: 7, anchor: 'middle', fill: C.muted }), text(206, 82, 'to sheet P-106', { size: 7, anchor: 'middle', fill: C.muted }),
    text(120, 110, 'the connector names the sheet; the same line\nnumber appears at both ends', { size: 7.5, anchor: 'middle', fill: C.muted }),
    text(370, 22, 'Tie-in and existing', { anchor: 'middle', weight: 700, size: 10 }),
    ...S.pline(290, 60, 360, 60, 'existing'), text(325, 50, 'EXISTING', { size: 6.5, anchor: 'middle', fill: C.muted }), P(360, 60, 460, 60), poly([[360, 48], [372, 60], [360, 72], [348, 60]], { fill: C.soft, width: 1.2 }), text(360, 63, 'TP', { size: 6, anchor: 'middle', weight: 700 }), text(360, 86, 'TP-14: tie-in point 14,\nsee tie-in list for the method', { size: 7, anchor: 'middle', fill: C.muted }),
    text(120, 150, 'Hold', { anchor: 'middle', weight: 700, size: 10 }),
    ...(() => { const pts = []; const cx = 120, cy = 190, rx = 60, ry = 22; for (let i = 0; i < 18; i++) { const a = (i / 18) * Math.PI * 2; pts.push([cx + rx * Math.cos(a), cy + ry * Math.sin(a)]) } return [path(pts.map((p, i) => (i ? 'A9,9 0 0 1 ' : 'M') + p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ') + ' A9,9 0 0 1 ' + pts[0][0].toFixed(1) + ',' + pts[0][1].toFixed(1), { width: 1.2, stroke: C.red })] })(),
    text(120, 187, 'HOLD 3', { size: 9, anchor: 'middle', weight: 700, fill: C.red }), text(120, 198, 'valve type TBD', { size: 6.5, anchor: 'middle', fill: C.red }),
    text(120, 232, 'a hold means the design is not final here:\ndo not build or order against it', { size: 7.5, anchor: 'middle', fill: C.muted }),
    text(370, 150, 'By others / package boundary', { anchor: 'middle', weight: 700, size: 10 }),
    rect(300, 166, 140, 60, { dash: '6 3', width: 1 }), text(370, 180, 'PACKAGE VENDOR SCOPE', { size: 6.5, anchor: 'middle', weight: 700 }), text(370, 196, 'see vendor P&ID V-2201', { size: 7, anchor: 'middle' }), P(260, 210, 300, 210), P(440, 210, 480, 210),
    text(370, 244, 'inside the dashed box the vendor drawing rules;\nthe plant P&ID stops at the boundary', { size: 7.5, anchor: 'middle', fill: C.muted }),
  ], { title: 'Off-page connectors, tie-ins and holds' }))

// ================= P&ID symbol sheets =================
const mv = (k, o = {}) => (x, y) => [P(x - 26, y, x - 10, y), ...S.pvalve(x, y, k, { s: 10, ...o }), P(x + 10, y, x + 26, y)]
sheetFig('drawings/pid-manual-valves-sheet.svg', 'ISA and PIP manual valve symbols on a P&ID: gate, globe, ball, butterfly, plug, needle, diaphragm, check, three-way, angle, relief or safety valve, rupture disc, with the handwheel and locked or car-sealed markings',
  'Manual valves', [
  cell('gate', (x, y) => [...mv('gate')(x, y), ...hand(x, y - 7)], 'isolation, full open/closed'),
  cell('globe', (x, y) => [...mv('globe')(x, y), ...hand(x, y - 7)], 'throttling, dot in the middle'),
  cell('ball', (x, y) => [...mv('ball')(x, y)], 'circle in the middle'),
  cell('butterfly', (x, y) => [...mv('butterfly')(x, y)], 'two bars + diagonal'),
  cell('plug', (x, y) => [...mv('plug')(x, y)], 'filled wedge'),
  cell('needle', (x, y) => [...mv('needle')(x, y)], 'fine control, small lines'),
  cell('diaphragm', (x, y) => [...mv('diaphragm')(x, y)], 'arc over the body'),
  cell('check', (x, y) => [...mv('check')(x, y)], 'flow toward the bar'),
  cell('three-way', (x, y) => [...mv('threeway')(x, y), P(x, y - 10, x, y - 24)], 'diverting or mixing'),
  cell('angle', (x, y) => [P(x - 26, y + 6, x - 10, y + 6), ...S.pvalve(x, y + 6, 'angle', { s: 10 }), P(x, y - 10, x, y - 24)], '90° body'),
  cell('relief / safety', (x, y) => [P(x - 26, y + 6, x - 10, y + 6), ...S.pvalve(x, y + 6, 'angle', { s: 10 }), path(`M${x},${y - 4} l0,-4 l4,-3 l-8,-3 l8,-3 l-4,-3`, { width: 1.1 }), P(x, y - 10, x, y - 10)], 'spring on top: PSV'),
  cell('rupture disc', (x, y) => [P(x - 26, y + 6, x, y + 6), ...S.pvalve(x, y + 4, 'rupture', { s: 10 })], 'one-shot burst'),
  cell('locked / sealed', (x, y) => [...mv('gate')(x, y), text(x, y - 14, 'LO', { size: 8, anchor: 'middle', weight: 700 }), text(x, y + 22, 'CSC', { size: 8, anchor: 'middle', weight: 700 })], 'LO, LC, CSO, CSC'),
  cell('normally closed', (x, y) => [P(x - 26, y, x - 10, y), ...S.pvalve(x, y, 'gate', { s: 10 }), poly([[x - 10, y - 7], [x, y], [x - 10, y + 7]], { fill: C.ink }), poly([[x + 10, y - 7], [x, y], [x + 10, y + 7]], { fill: C.ink }), P(x + 10, y, x + 26, y)], 'filled = NC on many legends'),
  cell('valve with tag', (x, y) => [...mv('gate')(x, y), text(x, y + 22, 'HV-1012', { size: 8, anchor: 'middle', weight: 700 })], 'HV = hand valve'),
  cell('size or spec change', (x, y) => [P(x - 26, y, x - 8, y), poly([[x - 8, y - 7], [x + 8, y - 3], [x + 8, y + 3], [x - 8, y + 7]], { width: 1.4 }), P(x + 8, y, x + 26, y), text(x, y + 20, '6" x 4"', { size: 8, anchor: 'middle' })], 'reducer on the line'),
], { cols: 4, cellH: 84, symH: 44 }, 'The bow-tie is a valve; what sits inside or on top says which kind.')

const cv = (act, fail) => (x, y) => [P(x - 26, y + 8, x - 10, y + 8), ...S.pvalve(x, y + 8, 'globe', { s: 10 }), ...S.actuator(x, y, act, { fail }), P(x + 10, y + 8, x + 26, y + 8)]
sheetFig('drawings/pid-control-valves-sheet.svg', 'Control valve actuators and fail positions on a P&ID: diaphragm, spring-diaphragm, piston, motor operated, solenoid, hydraulic and hand actuators, and the FC FO FL fail-position letters',
  'Control valves and actuators', [
  cell('diaphragm', cv('diaphragm', ''), 'pneumatic, most common'),
  cell('fails closed (FC)', cv('diaphragm', 'FC'), 'FC: spring shuts it'),
  cell('fails open (FO)', cv('diaphragm', 'FO'), 'FO: spring opens it'),
  cell('fails last', cv('diaphragm', 'FL'), 'FL: stays where it was'),
  cell('piston', cv('piston', ''), 'air or hydraulic cylinder'),
  cell('motor operated', cv('motor', ''), 'MOV, electric'),
  cell('solenoid', cv('solenoid', ''), 'on-off, SOV'),
  cell('hydraulic', cv('hydraulic', ''), 'oil piston'),
  cell('hand operated', cv('hand', ''), 'T bar = handwheel'),
  cell('with positioner', (x, y) => [...cv('diaphragm', '')(x, y), rect(x + 14, y - 22, 12, 10, { width: 1 }), line(x + 14, y - 17, x + 4, y - 17, { width: 1 })], 'box beside the actuator'),
  cell('signal to actuator', (x, y) => [...cv('diaphragm', '')(x, y), ...S.pline(x, y - 22, x, y - 40, 'pneumatic')], 'ticked line = air signal'),
  cell('self-regulating', (x, y) => [P(x - 26, y + 8, x - 10, y + 8), ...S.pvalve(x, y + 8, 'globe', { s: 10 }), ...S.actuator(x, y, 'springDiaphragm'), P(x + 10, y + 8, x + 26, y + 8), ...S.pline(x + 20, y + 8, x + 20, y - 8, 'capillary'), ...S.pline(x + 20, y - 8, x + 4, y - 8, 'capillary')], 'PCV sensing downstream'),
], { cols: 4, cellH: 92, symH: 52 }, 'Fail position is the one that matters when the air goes: FC shuts, FO opens.')

sheetFig('drawings/pid-equipment-sheet.svg', 'P&ID equipment symbols: centrifugal pump, positive displacement pump, vacuum pump, compressor, blower or fan, electric motor and turbine drivers, agitator, conveyor, hoist and a gearbox',
  'Pumps, compressors, drivers', [
  cell('centrifugal pump', (x, y) => [...S.pumpCentrifugal(x, y + 4, 12)], 'circle, discharge tangent'),
  cell('PD pump', (x, y) => [...S.pumpPD(x, y, 12)], 'triangle inside'),
  cell('vacuum pump', (x, y) => [circle(x, y, 12), text(x, y + 4, 'VAC', { size: 7, anchor: 'middle', weight: 700 })], 'labelled circle'),
  cell('compressor', (x, y) => [...S.compressor(x, y, 14)], 'trapezoid inside'),
  cell('blower / fan', (x, y) => [...S.blower(x, y, 12)], 'curved blades'),
  cell('motor driver', (x, y) => [...S.driver(x - 14, y, 'M', 9), line(x - 5, y, x + 4, y, { width: 1.2 }), ...S.pumpCentrifugal(x + 16, y + 2, 10)], 'M attached to the pump'),
  cell('turbine driver', (x, y) => [...S.driver(x, y, 'T', 10)], 'T = steam turbine'),
  cell('agitator', (x, y) => [...S.agitatorTank(x, y)], 'shaft and impeller'),
  cell('conveyor', (x, y) => [...S.conveyorSym(x, y, 44)], 'two pulleys and belt'),
  cell('hoist / crane', (x, y) => [line(x - 20, y - 14, x + 20, y - 14, { width: 2 }), line(x, y - 14, x, y + 2, { width: 1.2 }), path(`M${x - 4},${y + 2} a4,4 0 0 0 8,0 l-8,0 M${x},${y + 6} l0,4 a3,3 0 0 1 -5,3`, { width: 1.2 })], 'hook under a beam'),
  cell('gearbox', (x, y) => [rect(x - 16, y - 10, 32, 20), circle(x - 6, y, 5), circle(x + 6, y, 5), line(x - 26, y, x - 16, y, { width: 2 }), line(x + 16, y, x + 26, y, { width: 2 })], 'two gears in a box'),
  cell('drive train', (x, y) => [...S.driver(x - 24, y, 'M', 7), line(x - 17, y, x - 12, y, { width: 1.5 }), rect(x - 12, y - 7, 18, 14), text(x - 3, y + 3, 'GB', { size: 6.5, anchor: 'middle' }), line(x + 6, y, x + 12, y, { width: 1.5 }), ...S.conveyorSym(x + 22, y, 18)], 'motor, gearbox, load'),
], { cols: 4, cellH: 84, symH: 44 }, 'The tag beside the symbol (P-101A) is what you write on the work order.')

sheetFig('drawings/pid-vessels-exchangers-sheet.svg', 'P&ID vessel and exchanger symbols: vertical vessel, horizontal drum, cone-bottom tank, open tank, tank with agitator, shell-and-tube exchanger, plate exchanger, air cooler, jacketed vessel, and the nozzle and manway marks',
  'Vessels, tanks, exchangers', [
  cell('vertical vessel', (x, y) => [...S.vesselV(x, y, 22, 46)], 'dished ends'),
  cell('horizontal drum', (x, y) => [...S.vesselH(x, y, 48, 22)], 'lying down'),
  cell('cone-bottom tank', (x, y) => [...S.tankCone(x, y + 2, 30, 30).map((s) => s)], 'hopper'),
  cell('open tank', (x, y) => [...S.tankOpen(x, y, 34, 26)], 'no top line = open'),
  cell('agitated tank', (x, y) => [...S.agitatorTank(x, y)], 'mixer on top'),
  cell('shell and tube', (x, y) => [...S.exchangerST(x, y, 13)], 'zigzag = tubes'),
  cell('plate exchanger', (x, y) => [...S.exchangerPlate(x, y)], 'stacked plates'),
  cell('air cooler', (x, y) => [...S.exchangerAir(x, y)], 'fin fan'),
  cell('jacketed vessel', (x, y) => [...S.vesselV(x, y, 22, 46), path(`M${x - 15},${y - 12} L${x - 15},${y + 12} M${x + 15},${y - 12} L${x + 15},${y + 12}`, { width: 1.2 })], 'outer lines = jacket'),
  cell('nozzle / manway', (x, y) => [...S.vesselV(x, y, 22, 46), line(x + 11, y - 8, x + 22, y - 8, { width: 2 }), text(x + 24, y - 5, 'N3', { size: 7 }), circle(x - 16, y + 6, 5), text(x - 16, y + 20, 'MW', { size: 6.5, anchor: 'middle' })], 'N = nozzle, MW = manway'),
  cell('level in a tank', (x, y) => [...S.tankOpen(x, y, 34, 26), line(x - 17, y, x + 17, y, { width: 0.8, dash: '3 2' }), text(x, y - 4, 'NLL', { size: 6, anchor: 'middle' })], 'HLL, NLL, LLL lines'),
  cell('trim heater / coil', (x, y) => [...S.vesselV(x, y, 26, 46), path(`M${x - 8},${y - 8} l16,0 l0,4 l-16,0 l0,4 l16,0 l0,4 l-16,0 l0,4 l16,0`, { width: 1 })], 'internal coil'),
], { cols: 4, cellH: 88, symH: 48 }, 'Equipment symbols are pictures: the tag and the data sheet carry the numbers.')

sheetFig('drawings/pid-fittings-sheet.svg', 'P&ID inline fittings and specialties: basket and Y strainer, filter, steam trap, spectacle blind open and closed, spacer and blind flange, orifice plate, sight glass, expansion joint, flexible hose, reducer, cap, vent and drain',
  'Filters, traps and inline fittings', [
  cell('Y strainer', (x, y) => [...S.strainerY(x, y)], 'suction protection'),
  cell('T / basket strainer', (x, y) => [...S.strainerT(x, y + 4)], 'removable basket'),
  cell('filter', (x, y) => [P(x - 26, y, x - 12, y), ...S.filterBox(x, y), P(x + 12, y, x + 26, y)], 'box with diagonal'),
  cell('steam trap', (x, y) => [P(x - 26, y, x - 8, y), ...S.steamTrap(x, y), P(x + 8, y, x + 26, y)], 'T in a circle'),
  cell('spectacle, open', (x, y) => [P(x - 26, y + 4, x - 4, y + 4), ...S.spectacleBlind(x, y + 4, { open: true }), P(x + 4, y + 4, x + 26, y + 4)], 'open ring in the line'),
  cell('spectacle, closed', (x, y) => [P(x - 26, y + 4, x - 4, y + 4), ...S.spectacleBlind(x, y + 4, { open: false }), P(x + 4, y + 4, x + 26, y + 4)], 'solid disc in the line'),
  cell('blind flange', (x, y) => [P(x - 26, y, x - 2, y), ...S.blindFlange(x, y)], 'dead end'),
  cell('orifice plate', (x, y) => [P(x - 26, y, x - 4, y), ...S.orificePlate(x, y), P(x + 4, y, x + 26, y)], 'FE or RO'),
  cell('sight glass', (x, y) => [P(x - 26, y, x - 8, y), ...S.sightGlass(x, y), P(x + 8, y, x + 26, y)], 'flow indicator'),
  cell('expansion joint', (x, y) => [P(x - 26, y, x - 12, y), ...S.expansionJoint(x, y), P(x + 12, y, x + 26, y)], 'bellows'),
  cell('flexible hose', (x, y) => [P(x - 28, y, x - 16, y), ...S.hoseSym(x, y), P(x + 16, y, x + 28, y)], 'wavy line'),
  cell('reducer', (x, y) => [P(x - 26, y, x - 8, y), ...S.reducerSym(x, y), P(x + 8, y, x + 26, y)], 'conc; flat top = ecc'),
  cell('cap / plug', (x, y) => [P(x - 26, y, x - 4, y), ...S.capSym(x, y)], 'closed end'),
  cell('vent', (x, y) => [P(x - 20, y + 8, x + 20, y + 8), line(x, y + 8, x, y - 2, { width: 1.3 }), ...S.ventSym(x, y - 2)], 'high point, to atmosphere'),
  cell('drain', (x, y) => [P(x - 20, y - 12, x + 20, y - 12), ...S.drainSym(x, y - 12)], 'low point, valved + capped'),
  cell('sample point', (x, y) => [P(x - 20, y - 8, x + 20, y - 8), line(x, y - 8, x, y + 2, { width: 1.3 }), ...S.pvalve(x, y + 8, 'gate', { s: 5 }), line(x, y + 14, x, y + 20, { width: 1.3 }), text(x + 8, y + 22, 'SC', { size: 7 })], 'SC'),
], { cols: 4, cellH: 84, symH: 44 }, 'Blinds and spectacle blinds are positive isolation: find them before LOTO.')

sheetFig('drawings/pid-lines-signals-sheet.svg', 'P&ID line and signal types: main process, utility, insulated, jacketed, traced, existing and underground process lines, and the pneumatic, electric, hydraulic, capillary, software, mechanical and sonic signal lines used between instruments',
  'Line and signal types', [
  cell('process (main)', (x, y) => S.pline(x - 40, y, x + 40, y, 'process'), 'heavy solid'),
  cell('utility / secondary', (x, y) => S.pline(x - 40, y, x + 40, y, 'utility'), 'thin solid'),
  cell('insulated', (x, y) => S.pline(x - 40, y, x + 40, y, 'insulated'), 'boxes on the line'),
  cell('jacketed', (x, y) => S.pline(x - 40, y, x + 40, y, 'jacketed'), 'parallel lines'),
  cell('traced', (x, y) => S.pline(x - 40, y, x + 40, y, 'traced'), 'dashed beside = tracing'),
  cell('existing', (x, y) => S.pline(x - 40, y, x + 40, y, 'existing'), 'light: already there'),
  cell('underground', (x, y) => S.pline(x - 40, y, x + 40, y, 'underground'), 'dashed below'),
  cell('pneumatic signal', (x, y) => S.pline(x - 40, y, x + 40, y, 'pneumatic'), 'double ticks: air'),
  cell('electric signal', (x, y) => S.pline(x - 40, y, x + 40, y, 'electric'), 'dashed: 4-20 mA, wires'),
  cell('hydraulic signal', (x, y) => S.pline(x - 40, y, x + 40, y, 'hydraulic'), 'L ticks: oil'),
  cell('capillary', (x, y) => S.pline(x - 40, y, x + 40, y, 'capillary'), 'X marks: filled tube'),
  cell('software / data', (x, y) => S.pline(x - 40, y, x + 40, y, 'software'), 'circles: inside the DCS'),
  cell('mechanical link', (x, y) => S.pline(x - 40, y, x + 40, y, 'mechanical'), 'dots: a rod or cable'),
  cell('sonic / radio', (x, y) => S.pline(x - 40, y, x + 40, y, 'sonic'), 'wavy: wireless'),
  cell('flow direction', (x, y) => [...S.pline(x - 40, y, x + 40, y, 'process'), poly([[x - 4, y - 5], [x + 6, y], [x - 4, y + 5]], { fill: C.ink })], 'arrow on the line'),
  cell('line crossing', (x, y) => [...S.pline(x - 40, y, x + 40, y, 'process'), path(`M${x},${y + 14} L${x},${y + 6} a6,6 0 0 1 0,-12 L${x},${y - 14}`, { width: 1.4 })], 'hop = not connected'),
], { cols: 4, cellH: 76, symH: 36 }, 'Heavy is pipe, thin is a wire or tube: a dashed line never carries fluid.')

// ================= ISA tags =================
fig('drawings/isa-tag-decoder.svg', 'Decoder for an ISA-5.1 instrument tag PIT-101A: first letter for the measured variable, modifier letters, succeeding letters for the function, the loop number shared by every instrument in the loop and the optional suffix',
  svg(500, 250, [
    text(250, 40, 'PIT - 101 A', { anchor: 'middle', weight: 700, size: 26 }),
    leader(196, 48, 30, 90, 'P = pressure (measured variable)', { size: 8, anchor: 'start' }), leader(212, 48, 90, 120, 'I = indicating (it has a display)', { size: 8, anchor: 'start' }),
    leader(228, 48, 250, 90, 'T = transmitter (sends a signal)', { size: 8, anchor: 'start' }), leader(280, 48, 290, 120, '101 = loop number shared by PIT, PIC, PCV', { size: 8 }), leader(312, 48, 400, 70, 'A = A/B suffix', { size: 8 }),
    table(40, 140, [['tag', 'reads as'], ['PIT-101', 'pressure indicating transmitter'], ['TIC-203', 'temperature indicating controller'], ['FSL-310', 'flow switch, low'], ['LAHH-405', 'level alarm, high-high'], ['ZSC-512', 'position switch, closed'], ['PSV-120', 'pressure safety valve']], [70, 200], { rowH: 14, size: 7.5 }),
    note(360, 160, 'read letters left to right:\nwhat is measured,\nany modifier,\nthen what it does', { size: 8.5 }),
  ], { title: 'ISA tag decoder' }))

fig('drawings/isa-first-letters-table.svg', 'ISA-5.1 first-letter table: the measured or initiating variable for each letter A to Z, with the modifier meaning where the letter has one',
  svg(500, 380, [
    table(20, 20, [['letter', 'first letter: measured variable', 'modifier'], ['A', 'analysis', ''], ['B', 'burner, combustion', ''], ['C', "user's choice (often conductivity)", ''], ['D', "user's choice (often density)", 'differential'], ['E', 'voltage', ''], ['F', 'flow rate', 'ratio (fraction)'], ['G', "user's choice (gauging)", ''], ['H', 'hand', ''], ['I', 'current', ''], ['J', 'power', 'scan'], ['K', 'time, schedule', 'time rate of change'], ['L', 'level', ''], ['M', "user's choice (moisture)", 'momentary']], [46, 210, 110], { rowH: 15, size: 7.5 }),
    table(260, 20, [['letter', 'first letter: measured variable', 'modifier'], ['N', "user's choice", ''], ['O', "user's choice", ''], ['P', 'pressure, vacuum', ''], ['Q', 'quantity', 'integrate'], ['R', 'radiation', ''], ['S', 'speed, frequency', 'safety'], ['T', 'temperature', ''], ['U', 'multivariable', ''], ['V', 'vibration, mechanical analysis', ''], ['W', 'weight, force', ''], ['X', 'unclassified', 'X axis'], ['Y', 'event, state, presence', 'Y axis'], ['Z', 'position, dimension', 'Z axis']], [46, 130, 60], { rowH: 15, size: 7.5 }),
    note(250, 262, 'PDT = pressure differential transmitter: D is a modifier of P, not a second variable', { anchor: 'middle', size: 8.5 }),
    note(250, 290, 'a "user\'s choice" letter means: read the legend sheet, the plant decided what it means', { anchor: 'middle', size: 8.5 }),
    caption(500, 380, 'First letter = what it measures; the rest = what it does with that.'),
  ], { title: 'ISA first letters' }))

fig('drawings/isa-succeeding-letters-table.svg', 'ISA-5.1 succeeding letters: readout or passive function, output function and modifier for each letter, so a tag like FSHH or TAL can be read',
  svg(500, 340, [
    table(20, 20, [['letter', 'readout / passive', 'output function', 'modifier'], ['A', 'alarm', '', ''], ['B', "user's choice", "user's choice", "user's choice"], ['C', '', 'control', ''], ['E', 'sensor, primary element', '', ''], ['G', 'glass, gauge, viewing', '', ''], ['H', '', '', 'high'], ['I', 'indicate', '', ''], ['K', '', 'control station', ''], ['L', 'light', '', 'low'], ['M', '', '', 'middle, intermediate'], ['N', "user's choice", "user's choice", "user's choice"], ['O', 'orifice, restriction', '', ''], ['P', 'point (test connection)', '', ''], ['R', 'record', '', ''], ['S', '', 'switch', ''], ['T', '', 'transmit', ''], ['V', '', 'valve, damper, louver', ''], ['W', 'well, probe', '', ''], ['Y', '', 'relay, compute, convert', ''], ['Z', '', 'driver, actuator, final element', '']], [40, 150, 170, 100], { rowH: 13, size: 7 }),
    caption(500, 340, 'HH and LL are two modifiers: LAHH is a level alarm that trips at high-high.'),
  ], { title: 'ISA succeeding letters' }))

sheetFig('drawings/isa-bubbles-sheet.svg', 'ISA-5.1 instrument bubble shapes and location lines: discrete field instrument, panel-mounted, behind the panel, local panel, shared display or DCS function, computer function, PLC function, and the interlock diamond',
  'Bubbles and where the instrument lives', [
  cell('field mounted', (x, y) => S.bubble(x, y, 'PI', '102', { r: 14 }), 'plain circle, no line'),
  cell('main panel', (x, y) => S.bubble(x, y, 'PIC', '102', { loc: 'panel', r: 14 }), 'one solid line'),
  cell('behind the panel', (x, y) => S.bubble(x, y, 'PY', '102', { loc: 'behind', r: 14 }), 'dashed line: not visible'),
  cell('local panel', (x, y) => S.bubble(x, y, 'PI', '102', { loc: 'local', r: 14 }), 'two lines: field panel'),
  cell('shared display (DCS)', (x, y) => S.bubble(x, y, 'FIC', '104', { shape: 'shared', loc: 'panel', r: 13 }), 'circle in a square'),
  cell('computer function', (x, y) => S.bubble(x, y, 'FY', '104', { shape: 'computer', r: 13 }), 'hexagon'),
  cell('PLC function', (x, y) => S.bubble(x, y, 'FSL', '104', { shape: 'plc', r: 13 }), 'diamond in a square'),
  cell('interlock', (x, y) => [poly([[x, y - 14], [x + 14, y], [x, y + 14], [x - 14, y]], { width: 1.4 }), text(x, y + 4, 'I-3', { size: 8, anchor: 'middle', weight: 700 })], 'diamond alone: logic I-3'),
  cell('primary element', (x, y) => [P(x - 30, y + 8, x + 30, y + 8), ...S.orificePlate(x, y + 8), ...S.bubble(x, y - 18, 'FE', '104', { r: 11 })], 'FE on the line'),
  cell('one loop, two bubbles', (x, y) => [...S.bubble(x - 22, y, 'FT', '104', { r: 12 }), ...S.bubble(x + 22, y, 'FIC', '104', { shape: 'shared', loc: 'panel', r: 12 }), ...S.pline(x - 10, y, x + 8, y, 'electric')], 'same number = same loop'),
  cell('valve tag', (x, y) => [P(x - 30, y + 10, x - 10, y + 10), ...S.pvalve(x, y + 10, 'globe', { s: 9 }), ...S.actuator(x, y + 2, 'diaphragm'), P(x + 10, y + 10, x + 30, y + 10), text(x + 18, y - 6, 'FCV\n104', { size: 6.5 })], 'FCV: valve of loop 104'),
  cell('multi-point (shared)', (x, y) => [...S.bubble(x, y, 'TI', '210', { shape: 'shared', loc: 'panel', r: 13 }), text(x, y + 26, '1-8', { size: 7, anchor: 'middle' })], 'suffix or range: 8 points'),
], { cols: 4, cellH: 90, symH: 50 }, 'No line = out in the field with you; a line = in the control room.')

fig('drawings/isa-worked-tags.svg', 'Six worked instrument tags drawn as they appear on a P&ID with their bubbles, locations and signal lines: PIT-101 field transmitter to PIC-101 on the DCS, TIC-203, FSL-310 tripping an interlock, LAHH-405 alarm, ZSC-512 valve closed switch and PSV-120 relief valve',
  svg(500, 300, [
    ...[[60, 'PIT', '101', {}], [180, 'TIC', '203', { shape: 'shared', loc: 'panel' }], [300, 'FSL', '310', { shape: 'plc' }], [420, 'LAHH', '405', { shape: 'shared', loc: 'panel' }]].map(([x, l, n, o]) => S.bubble(x, 60, l, n, { r: 15, ...o })),
    text(60, 96, 'pressure indicating\ntransmitter, field', { size: 7.5, anchor: 'middle', fill: C.muted }), text(180, 96, 'temperature indicating\ncontroller, on the DCS', { size: 7.5, anchor: 'middle', fill: C.muted }), text(300, 96, 'flow switch low,\nin the PLC', { size: 7.5, anchor: 'middle', fill: C.muted }), text(420, 96, 'level alarm high-high,\non the DCS', { size: 7.5, anchor: 'middle', fill: C.muted }),
    ...S.bubble(120, 200, 'ZSC', '512', { r: 15 }), text(120, 236, 'position switch, closed:\nproves the valve shut', { size: 7.5, anchor: 'middle', fill: C.muted }),
    P(200, 214, 220, 214), ...S.pvalve(230, 214, 'angle', { s: 10 }), path('M230,204 l0,-4 l4,-3 l-8,-3 l8,-3 l-4,-3', { width: 1.1 }), P(230, 204, 230, 180), text(240, 178, 'to flare', { size: 7 }), text(230, 244, 'PSV-120: pressure safety\nvalve, set 150 psig', { size: 7.5, anchor: 'middle', fill: C.muted }),
    ...S.bubble(360, 200, 'PIT', '101', { r: 13 }), ...S.pline(373, 200, 420, 200, 'electric'), ...S.bubble(436, 200, 'PIC', '101', { shape: 'shared', loc: 'panel', r: 13 }), text(400, 236, 'same loop number 101:\ntransmitter feeds the controller', { size: 7.5, anchor: 'middle', fill: C.muted }),
    caption(500, 300, 'Letters say what it does, shape says where it is, number ties the loop.'),
  ], { title: 'Worked instrument tags' }))

fig('drawings/isa-loop-on-pid.svg', 'One control loop read on the P&ID: orifice FE-104 in the line, flow transmitter FT-104 in the field, electric signal to the flow indicating controller FIC-104 on the DCS, pneumatic signal through I/P converter FY-104 to the diaphragm control valve FCV-104 that fails closed, with the loop numbered in reading order',
  svg(500, 260, [
    P(40, 170, 180, 170), ...S.orificePlate(120, 170), P(180, 170, 300, 170), ...S.pvalve(310, 170, 'globe', { s: 10 }), ...S.actuator(310, 162, 'diaphragm', { fail: 'FC' }), P(320, 170, 460, 170), line(460, 170, 472, 170, { width: 2.2, arrow: 'end' }),
    ...S.bubble(120, 120, 'FE', '104', { r: 11 }), thin(120, 131, 120, 162),
    ...S.bubble(180, 100, 'FT', '104', { r: 13 }), thin(120, 140, 168, 108), ...S.pline(190, 90, 232, 62, 'electric'),
    ...S.bubble(250, 50, 'FIC', '104', { shape: 'shared', loc: 'panel', r: 13 }), ...S.pline(263, 50, 296, 50, 'electric'), ...S.bubble(310, 50, 'FY', '104', { r: 11 }), ...S.pline(310, 61, 310, 138, 'pneumatic'),
    text(310, 196, 'FCV-104', { size: 7, anchor: 'middle' }),
    callout(1, 100, 150), callout(2, 206, 116), callout(3, 250, 20), callout(4, 336, 40), callout(5, 340, 148),
    legend(20, 216, ['FE: orifice plate makes a pressure drop', 'FT: measures it, sends 4-20 mA (dashed)', 'FIC: compares to set point, in the control room'], { size: 7.5, gap: 11 }),
    legend(270, 216, ['FY: I/P converts mA to 3-15 psi air (ticked)', 'FCV: air moves the diaphragm; spring closes it'], { size: 7.5, gap: 11, start: 4 }),
  ], { title: 'One control loop on the P&ID' }))

fig('drawings/isa-transmitter-vs-switch.svg', 'Transmitter, switch, indicator and controller compared: what each does with the measurement, the signal it produces, where its tag letters come from and what a millwright can expect to see on it in the field',
  svg(500, 260, [
    table(20, 24, [['device', 'tag ends in', 'what it does', 'signal out', 'in the field'], ['gauge / indicator', 'I or G', 'shows the value locally', 'none', 'dial or digital readout'], ['transmitter', 'T', 'measures, sends a continuous value', '4-20 mA or HART', 'head with display, 2 wires'], ['switch', 'S', 'closes or opens a contact at a set point', 'contact (on/off)', 'small box, set screw'], ['controller', 'C', 'compares to set point, drives an output', '4-20 mA to the valve', 'usually in the DCS'], ['element', 'E', 'the sensing part only (orifice, RTD)', 'raw signal to a T', 'orifice flanges, well']], [76, 52, 140, 84, 108], { rowH: 30, size: 7 }),
    note(250, 236, 'a switch trips at one point and cannot tell you the value; a transmitter tells you the value all the time', { anchor: 'middle', size: 8.5 }),
  ], { title: 'Transmitter versus switch' }))
