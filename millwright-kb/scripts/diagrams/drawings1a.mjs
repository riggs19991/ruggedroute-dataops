// Drawings, schematics and P&IDs (part 1a): drawing basics, mechanical views and sections, dimensions, fits,
// threads, surface finish, assembly drawings, GD&T, structural callouts.
import { svg, text, line, rect, circle, path, poly, g, dim, leader, table, caption, box, callout, legend, note, fig, C, hatchRect, plate, arc, angle } from './lib.mjs'
import * as S from './lib-symbols.mjs'

const cell = (name, draw, note) => ({ name, draw, note })
const sheetFig = (file, alt, title, cells, opts = {}, cap) => {
  const h = S.sheetHeight(cells.length, opts)
  fig(file, alt, svg(500, h, [...S.sheet(cells, opts), cap ? caption(500, h, cap) : ''], { title }))
}
const cl = (x1, y1, x2, y2) => line(x1, y1, x2, y2, { width: 0.8, dash: '12 3 2 3', stroke: C.muted })
const hidden = (x1, y1, x2, y2) => line(x1, y1, x2, y2, { width: 1.1, dash: '5 3' })
const thin = (x1, y1, x2, y2, o = {}) => line(x1, y1, x2, y2, { width: 0.8, stroke: C.muted, ...o })

// ================= Drawing basics =================
fig('drawings/sheet-layout-zones.svg', 'Layout of a drawing sheet: border with zone letters down the sides and numbers across the top and bottom, revision block top right, general notes, the drawing area with a section cut and detail bubble, and the title block in the bottom right corner',
  svg(500, 380, [
    rect(30, 30, 440, 252, { width: 1.2 }), rect(42, 42, 416, 228, { width: 1.8 }),
    ...[1, 2, 3, 4, 5, 6].map((n, i) => [text(42 + 34 + i * 69, 39, String(n), { size: 8, anchor: 'middle', fill: C.muted }), text(42 + 34 + i * 69, 279, String(n), { size: 8, anchor: 'middle', fill: C.muted }), ...(i < 5 ? [thin(42 + (i + 1) * 69, 30, 42 + (i + 1) * 69, 42), thin(42 + (i + 1) * 69, 270, 42 + (i + 1) * 69, 282)] : [])]),
    ...['A', 'B', 'C', 'D'].map((l, i) => [text(36, 42 + 28.5 + i * 57 + 3, l, { size: 8, anchor: 'middle', fill: C.muted }), text(464, 42 + 28.5 + i * 57 + 3, l, { size: 8, anchor: 'middle', fill: C.muted }), ...(i < 3 ? [thin(30, 42 + (i + 1) * 57, 42, 42 + (i + 1) * 57), thin(458, 42 + (i + 1) * 57, 470, 42 + (i + 1) * 57)] : [])]),
    // revision block top right
    rect(348, 46, 106, 34, { fill: C.grey, width: 1 }), text(401, 58, 'REV  DESCRIPTION  DATE  BY', { size: 6.5, anchor: 'middle', weight: 700 }), text(401, 70, 'C   BORE Ø CHANGED   09/15/26   RJ', { size: 6, anchor: 'middle' }),
    // general notes
    rect(348, 88, 106, 60, { width: 0.8, dash: '3 2' }), text(401, 100, 'GENERAL NOTES', { size: 6.5, anchor: 'middle', weight: 700 }), text(354, 112, '1. DIMENSIONS IN INCHES', { size: 5.5 }), text(354, 122, '2. BREAK SHARP EDGES', { size: 5.5 }), text(354, 132, '3. SEE M-104 FOR SECTION A-A', { size: 5.5 }),
    // drawing area: a bracket in plan with a section cut and detail circle
    rect(80, 90, 150, 100, { width: 1.5 }), circle(120, 140, 14), circle(190, 140, 14), circle(120, 140, 4), circle(190, 140, 4),
    line(155, 70, 155, 210, { width: 2, dash: '10 3 2 3' }), line(155, 70, 140, 70, { width: 2, arrow: 'end' }), line(155, 210, 140, 210, { width: 2, arrow: 'end' }), text(160, 74, 'A', { size: 10, weight: 700 }), text(160, 214, 'A', { size: 10, weight: 700 }),
    circle(190, 140, 24, { width: 1, dash: '3 2' }), line(207, 123, 250, 105, { width: 0.8 }), circle(262, 100, 12), line(250, 100, 274, 100, { width: 0.8 }), text(262, 97, 'B', { size: 7, anchor: 'middle', weight: 700 }), text(262, 108, '5', { size: 6.5, anchor: 'middle' }),
    text(155, 232, 'SECTION A-A ON SHT 3, ZONE C4', { size: 7, anchor: 'middle', fill: C.muted }),
    // title block bottom right
    rect(280, 204, 174, 62, { fill: C.grey, width: 1 }), line(280, 224, 454, 224, { width: 0.8 }), line(280, 246, 454, 246, { width: 0.8 }), line(380, 224, 380, 266, { width: 0.8 }),
    text(284, 218, 'AMP MILLWRIGHT KB', { size: 7, weight: 700 }), text(284, 238, 'TITLE: PUMP BASE, P-101', { size: 6.5 }), text(284, 260, 'DWG M-102   SHT 2 OF 6', { size: 6.5, weight: 700 }), text(386, 238, 'SCALE 1:10  SIZE D', { size: 6.5 }), text(386, 260, 'REV C', { size: 7, weight: 700 }),
    callout(1, 46, 46), callout(2, 340, 52), callout(3, 340, 94), callout(4, 236, 130), callout(5, 300, 198),
    legend(30, 302, ['zones: letter + number locate anything on the sheet', 'revision block, newest change at the top', 'general notes apply to the whole sheet', 'detail B is on sheet 5; section A-A on sheet 3', 'title block: number, sheet, revision, scale'], { size: 8, gap: 11 }),
    caption(500, 380, 'Find the sheet number and revision first, then the zone the note points to.'),
  ], { title: 'Sheet layout and zones' }))

fig('drawings/title-block-anatomy.svg', 'Anatomy of a title block: company, drawing title, drawing number, sheet of, revision letter, scale, sheet size, projection symbol, default tolerances unless otherwise noted, drawn checked and approved names and dates, and the CAD file reference',
  svg(500, 250, [
    rect(30, 40, 440, 150, { fill: C.grey, width: 1.2 }),
    line(30, 80, 470, 80, { width: 0.8 }), line(30, 120, 470, 120, { width: 0.8 }), line(30, 155, 470, 155, { width: 0.8 }), line(300, 40, 300, 190, { width: 0.8 }), line(380, 120, 380, 190, { width: 0.8 }), line(380, 40, 380, 80, { width: 0.8 }), line(150, 120, 150, 155, { width: 0.8 }),
    text(36, 54, 'COMPANY / PLANT', { size: 6.5, fill: C.muted }), text(36, 70, 'ACME PULP MILL, LINE 3', { size: 9, weight: 700 }),
    text(306, 54, 'PROJECT', { size: 6.5, fill: C.muted }), text(306, 70, 'PJ-2026-014', { size: 9 }), text(386, 54, 'SIZE', { size: 6.5, fill: C.muted }), text(386, 70, 'D (22 x 34)', { size: 9 }),
    text(36, 94, 'TITLE', { size: 6.5, fill: C.muted }), text(36, 110, 'STOCK PUMP P-101 BASE AND ANCHOR BOLTS', { size: 9.5, weight: 700 }),
    text(306, 94, 'DRAWING NUMBER', { size: 6.5, fill: C.muted }), text(306, 110, 'M-102-004', { size: 11, weight: 700 }),
    text(36, 134, 'DRAWN  RJ  08/02/26', { size: 7 }), text(36, 148, 'CHECKED  TL  08/09/26', { size: 7 }), text(156, 134, 'APPROVED  DM  08/12/26', { size: 7 }), text(156, 148, 'ENG. STAMP', { size: 7, fill: C.muted }),
    text(306, 134, 'SCALE 1:10', { size: 8 }), text(306, 148, 'NTS ON DETAILS', { size: 6.5, fill: C.muted }), text(386, 134, 'SHEET 2 OF 6', { size: 8 }), text(386, 148, 'REV  C', { size: 9, weight: 700 }),
    text(36, 168, 'TOLERANCES UNLESS NOTED:  .X ±.1   .XX ±.03   .XXX ±.010', { size: 6.5 }),
    text(36, 181, 'ANGLES ±0.5°   BREAK EDGES .02 MAX   FILE: M-102-004_C.dwg', { size: 6.5 }), text(306, 172, 'THIRD ANGLE', { size: 6.5, fill: C.muted }),
    // third-angle projection symbol
    g([path('M0,0 L22,-6 L22,6 Z', { width: 1 }), line(22, -6, 22, 6, { width: 1 }), circle(-16, 0, 6), circle(-16, 0, 3)], { transform: 'translate(410 175)' }),
    callout(1, 300, 100), callout(2, 462, 160), callout(3, 30, 172), callout(4, 462, 40),
    legend(30, 210, ['drawing number and revision: the two you check', 'sheet x of y: are all the sheets in hand?', 'default tolerances cover every dimension without one', 'size and scale: never scale a print to get a dimension'], { size: 8, gap: 10 }),
  ], { title: 'Title block anatomy' }))

fig('drawings/revision-block-and-cloud.svg', 'Revision block with revision letters, descriptions, dates and initials, a revision cloud around a changed dimension with its triangle flag, and the issue status stamps IFR, IFC and AS-BUILT',
  svg(500, 260, [
    text(120, 22, 'Revision block', { anchor: 'middle', weight: 700, size: 11 }),
    table(20, 32, [['REV', 'DESCRIPTION', 'DATE', 'BY'], ['A', 'ISSUED FOR REVIEW', '06/10/26', 'RJ'], ['B', 'ISSUED FOR CONSTRUCTION', '07/22/26', 'RJ'], ['C', 'BOLT PROJ. 4 TO 5 IN, ZONE C3', '09/15/26', 'TL']], [30, 132, 46, 24], { rowH: 18, size: 7 }),
    text(120, 126, 'newest revision on top; the description says where to look', { size: 7.5, anchor: 'middle', fill: C.muted }),
    // cloud around a changed dimension
    text(370, 22, 'Revision cloud and flag', { anchor: 'middle', weight: 700, size: 11 }),
    rect(300, 60, 140, 40, { fill: C.grey }), line(300, 110, 440, 110, { width: 1, arrow: 'both' }), thin(300, 100, 300, 114), thin(440, 100, 440, 114),
    text(370, 108, '5.00', { size: 9, anchor: 'middle', weight: 700, fill: C.red }),
    ...(() => { const pts = []; const cx = 372, cy = 108, rx = 52, ry = 16; for (let i = 0; i < 20; i++) { const a = (i / 20) * Math.PI * 2; pts.push([cx + rx * Math.cos(a), cy + ry * Math.sin(a)]) } return [path(pts.map((p, i) => (i ? 'A7,7 0 0 1 ' : 'M') + p[0].toFixed(1) + ',' + p[1].toFixed(1)).join(' ') + ' A7,7 0 0 1 ' + pts[0][0].toFixed(1) + ',' + pts[0][1].toFixed(1), { width: 1.2, stroke: C.red })] })(),
    poly([[440, 118], [452, 138], [428, 138]], { width: 1.2, stroke: C.red }), text(440, 135, 'C', { size: 8, anchor: 'middle', weight: 700, fill: C.red }),
    // status stamps
    text(250, 172, 'Status stamps', { anchor: 'middle', weight: 700, size: 11 }),
    ...[['ISSUED FOR REVIEW', 60, C.muted, 'do not build'], ['ISSUED FOR CONSTRUCTION', 190, C.green, 'build to this'], ['AS-BUILT', 330, C.blue, 'what was built'], ['HOLD', 420, C.red, 'stop: question open']].map(([s, x, col, n]) => [rect(x, 182, s === 'ISSUED FOR CONSTRUCTION' ? 120 : s === 'AS-BUILT' ? 70 : s === 'HOLD' ? 50 : 110, 26, { fill: C.paper, stroke: col, width: 1.6, rx: 3 }), text(x + (s === 'ISSUED FOR CONSTRUCTION' ? 60 : s === 'AS-BUILT' ? 35 : s === 'HOLD' ? 25 : 55), 199, s, { size: 6.5, anchor: 'middle', weight: 700, fill: col }), text(x + (s === 'ISSUED FOR CONSTRUCTION' ? 60 : s === 'AS-BUILT' ? 35 : s === 'HOLD' ? 25 : 55), 222, n, { size: 7, anchor: 'middle', fill: C.muted })]),
    caption(500, 260, 'A cloud marks what changed; the flag says which revision changed it.'),
  ], { title: 'Revisions, clouds and stamps' }))

fig('drawings/drawing-number-and-callouts.svg', 'Decoder for a drawing number and the callouts that send you to other sheets: discipline letter, area, sequence and revision in the number; section cut symbol with section letter and sheet; detail bubble with detail letter and sheet; match line and continuation reference',
  svg(500, 260, [
    text(250, 22, 'M-102-004 REV C', { anchor: 'middle', weight: 700, size: 18 }),
    leader(182, 34, 40, 66, 'M = mechanical\n(P piping, E electrical,\nS structural, C civil)', { size: 7.5, fill: C.muted, anchor: 'start' }), leader(218, 34, 150, 110, '102 = area or unit', { size: 7.5, fill: C.muted }),
    leader(258, 34, 300, 66, '004 = sheet or sequence', { size: 7.5, fill: C.muted }), leader(305, 34, 380, 110, 'REV C = third issued change', { size: 7.5, fill: C.muted }),
    // section cut symbol
    text(90, 150, 'Section cut', { anchor: 'middle', weight: 700, size: 9.5 }),
    line(60, 165, 60, 215, { width: 2, dash: '10 3 2 3' }), line(60, 165, 44, 165, { width: 2, arrow: 'end' }), line(60, 215, 44, 215, { width: 2, arrow: 'end' }),
    circle(78, 165, 11), line(67, 165, 89, 165, { width: 0.8 }), text(78, 162, 'A', { size: 7, anchor: 'middle', weight: 700 }), text(78, 172, 'M-104', { size: 5.5, anchor: 'middle' }),
    text(100, 190, 'look toward\nthe arrows; the\nsection is on M-104', { size: 7.5, fill: C.muted }),
    // detail bubble
    text(255, 150, 'Detail bubble', { anchor: 'middle', weight: 700, size: 9.5 }),
    circle(240, 190, 20, { width: 1, dash: '3 2' }), line(254, 176, 280, 166, { width: 0.8 }), circle(292, 162, 11), line(281, 162, 303, 162, { width: 0.8 }), text(292, 159, '2', { size: 7, anchor: 'middle', weight: 700 }), text(292, 169, 'M-105', { size: 5.5, anchor: 'middle' }),
    text(215, 226, 'top: detail number; bottom: the sheet it is drawn on', { size: 7.5, fill: C.muted }),
    // match line
    text(420, 150, 'Match line', { anchor: 'middle', weight: 700, size: 9.5 }),
    line(380, 170, 380, 220, { width: 1.5, dash: '14 4' }), text(384, 182, 'MATCH LINE', { size: 6.5 }), text(384, 192, 'SEE P-103', { size: 6.5, weight: 700 }), text(376, 182, 'CONT.', { size: 6.5, anchor: 'end' }), text(376, 192, 'FROM P-101', { size: 6.5, anchor: 'end', weight: 700 }),
    caption(500, 260, 'Every callout has two halves: what it is, and which sheet holds it.'),
  ], { title: 'Drawing numbers and callouts' }))

// ================= Mechanical drawings =================
const cone = (x, y, third) => {
  // truncated cone seen from the side (frustum) and from the small end (two circles); the circles sit on the side the viewer stands
  const frustum = [path(`M${x - 10},${y - 10} L${x + 10},${y - 5} L${x + 10},${y + 5} L${x - 10},${y + 10} Z`, { width: 1.3 }), line(x + 10, y - 5, x + 10, y + 5, { width: 1.3 })]
  const circles = [circle(x, y, 9), circle(x, y, 4)]
  return third ? [...frustum.map((s) => s.replace(`M${x - 10}`, `M${x - 10}`)), ...circles.map((s) => s.replace(`cx="${x}"`, `cx="${x + 34}"`))] : [...frustum.map((s) => s.replace(`M${x - 10},${y - 10} L${x + 10},${y - 5} L${x + 10},${y + 5} L${x - 10},${y + 10} Z`, `M${x + 10},${y - 10} L${x - 10},${y - 5} L${x - 10},${y + 5} L${x + 10},${y + 10} Z`).replace(`x1="${x + 10}" y1="${y - 5}" x2="${x + 10}"`, `x1="${x - 10}" y1="${y - 5}" x2="${x - 10}"`)), ...circles.map((s) => s.replace(`cx="${x}"`, `cx="${x + 34}"`))]
}
fig('drawings/projection-angle-symbols.svg', 'Third-angle and first-angle projection: the truncated cone symbol for each, and the same L-shaped block with its top and right side views placed where each system puts them',
  svg(500, 300, [
    text(125, 22, 'Third angle (US, Canada)', { anchor: 'middle', weight: 700, size: 11.5 }), text(375, 22, 'First angle (ISO, Europe)', { anchor: 'middle', weight: 700, size: 11.5 }),
    ...cone(108, 44, true), ...cone(358, 44, false),
    text(125, 70, 'symbol: circles on the small-end side', { size: 7.5, anchor: 'middle', fill: C.muted }), text(375, 70, 'symbol: circles on the large-end side', { size: 7.5, anchor: 'middle', fill: C.muted }),
    ...[[60, true], [310, false]].map(([x0, third]) => {
      const fx = x0 + 20, fy = 150 // front view: L block
      const front = [path(`M${fx},${fy} l0,60 l60,0 l0,-24 l-36,0 l0,-36 z`, { width: 1.5, fill: C.grey })]
      const top = [rect(fx, third ? fy - 46 : fy + 76, 60, 36, { fill: C.grey }), line(fx + 24, third ? fy - 46 : fy + 76, fx + 24, third ? fy - 10 : fy + 112, { width: 1.5 })]
      const right = [rect(third ? fx + 76 : fx - 50, fy, 36, 60, { fill: C.grey }), line(third ? fx + 76 : fx - 50, fy + 36, third ? fx + 112 : fx - 14, fy + 36, { width: 1.5 })]
      return [...front, ...top, ...right, text(fx + 30, fy + 74, 'FRONT', { size: 7, anchor: 'middle', fill: C.muted }), text(fx + 30, third ? fy - 52 : fy + 124, 'TOP', { size: 7, anchor: 'middle', fill: C.muted }), text(third ? fx + 94 : fx - 32, fy + 74, 'RIGHT', { size: 7, anchor: 'middle', fill: C.muted })]
    }),
    note(125, 282, 'top view above, right view on the right', { anchor: 'middle', size: 8.5 }), note(375, 282, 'top view below, right view on the left', { anchor: 'middle', size: 8.5 }),
  ], { title: 'Third-angle and first-angle projection' }))

sheetFig('drawings/line-types-sheet.svg', 'The alphabet of lines: visible, hidden, centre, dimension and extension, leader, section (cutting plane), viewing plane, break lines short and long, phantom, stitch, chain, and the hatch (section) line, each drawn with its weight and pattern', 'The alphabet of lines', [
  cell('visible (object)', (x, y) => [line(x - 40, y, x + 40, y, { width: 2.2 })], 'thick, continuous'),
  cell('hidden', (x, y) => [hidden(x - 40, y, x + 40, y)], 'thin dashes'),
  cell('centre', (x, y) => [cl(x - 40, y, x + 40, y)], 'long-short-long'),
  cell('dimension lines', (x, y) => [thin(x - 30, y - 12, x - 30, y + 8), thin(x + 30, y - 12, x + 30, y + 8), line(x - 30, y + 4, x + 30, y + 4, { width: 0.9, arrow: 'both' }), text(x, y - 1, '2.50', { size: 7.5, anchor: 'middle' })], 'thin; arrows touch'),
  cell('leader', (x, y) => [line(x + 30, y - 10, x - 4, y + 6, { width: 0.9, arrow: 'end' }), line(x + 30, y - 10, x + 42, y - 10, { width: 0.9 }), text(x + 32, y - 13, 'Ø.50', { size: 7 })], 'thin, one arrow'),
  cell('cutting plane', (x, y) => [line(x - 34, y, x + 34, y, { width: 2.2, dash: '12 3 3 3' }), line(x - 34, y, x - 34, y - 14, { width: 2.2, arrow: 'end' }), line(x + 34, y, x + 34, y - 14, { width: 2.2, arrow: 'end' }), text(x - 34, y + 12, 'A', { size: 8, anchor: 'middle', weight: 700 }), text(x + 34, y + 12, 'A', { size: 8, anchor: 'middle', weight: 700 })], 'thick; arrows = view direction'),
  cell('viewing plane', (x, y) => [line(x - 34, y, x + 34, y, { width: 2.2, dash: '12 3 3 3' }), line(x - 34, y, x - 34, y - 14, { width: 2.2, arrow: 'end' }), line(x + 34, y, x + 34, y - 14, { width: 2.2, arrow: 'end' }), text(x, y + 12, 'VIEW B-B', { size: 7, anchor: 'middle' })], 'like a cut, no section'),
  cell('short break', (x, y) => [rect(x - 40, y - 10, 60, 20, { fill: C.grey, stroke: 'none' }), line(x - 40, y - 10, x + 14, y - 10, { width: 2 }), line(x - 40, y + 10, x + 14, y + 10, { width: 2 }), path(`M${x + 14},${y - 12} l4,6 l-8,6 l8,6 l-4,6`, { width: 1.5 })], 'thick freehand zigzag'),
  cell('long break', (x, y) => [line(x - 40, y - 10, x + 40, y - 10, { width: 2 }), line(x - 40, y + 10, x + 40, y + 10, { width: 2 }), path(`M${x - 6},${y - 14} l0,8 l-3,4 l6,4 l-3,4 l0,8`, { width: 0.9 }), path(`M${x + 8},${y - 14} l0,8 l-3,4 l6,4 l-3,4 l0,8`, { width: 0.9 })], 'thin with the zigzag'),
  cell('phantom', (x, y) => [line(x - 40, y, x + 40, y, { width: 0.9, dash: '14 3 3 3 3 3' })], 'long-short-short'),
  cell('stitch', (x, y) => [line(x - 40, y, x + 40, y, { width: 0.9, dash: '2 3' })], 'sewing, folds'),
  cell('chain (thick)', (x, y) => [line(x - 40, y, x + 40, y, { width: 2.2, dash: '14 3 3 3' })], 'surface treatment zone'),
  cell('section (hatch)', (x, y) => [rect(x - 30, y - 12, 60, 24, { width: 1.5 }), ...[-24, -12, 0, 12, 24].map((d) => line(x + d - 12, y + 12, x + d + 12, y - 12, { width: 0.7 }))], 'thin 45° lines'),
  cell('symmetry', (x, y) => [cl(x, y - 16, x, y + 16), line(x - 6, y - 14, x + 6, y - 14, { width: 0.9 }), line(x - 6, y - 18, x + 6, y - 18, { width: 0.9 }), line(x - 6, y + 14, x + 6, y + 14, { width: 0.9 }), line(x - 6, y + 18, x + 6, y + 18, { width: 0.9 }), rect(x - 30, y - 10, 30, 20, { fill: C.grey })], 'half drawn, mirror it'),
  cell('break in a round bar', (x, y) => [line(x - 34, y - 10, x - 6, y - 10, { width: 2 }), line(x - 34, y + 10, x - 6, y + 10, { width: 2 }), path(`M${x - 6},${y - 10} c-8,6 8,14 0,20`, { width: 1.5 }), line(x + 6, y - 10, x + 34, y - 10, { width: 2 }), line(x + 6, y + 10, x + 34, y + 10, { width: 2 }), path(`M${x + 6},${y - 10} c-8,6 8,14 0,20`, { width: 1.5 })], 'S-break, solid stock'),
  cell('adjacent part', (x, y) => [rect(x - 30, y - 8, 60, 16, { width: 1.5 }), line(x - 30, y - 16, x + 30, y - 16, { width: 0.9, dash: '14 3 3 3 3 3' }), line(x - 30, y - 24, x + 30, y - 24, { width: 0.9, dash: '14 3 3 3 3 3' })], 'phantom, not this part'),
], { cols: 4, cellH: 84, symH: 40 }, 'Thick = the object; thin = everything that explains it.')

fig('drawings/section-types.svg', 'Section views: full section, half section, offset section, revolved section and broken-out section, each with its cutting-plane line on the parent view and the hatching that shows cut material',
  svg(500, 300, [
    ...[['Full section', 20], ['Half section', 180], ['Offset section', 340]].map(([t, x]) => text(x + 70, 22, t, { anchor: 'middle', weight: 700, size: 10 })),
    // full: a bushing cut through
    circle(90, 74, 34), circle(90, 74, 12), line(40, 74, 140, 74, { width: 2, dash: '10 3 2 3' }), line(40, 74, 40, 60, { width: 2, arrow: 'end' }), line(140, 74, 140, 60, { width: 2, arrow: 'end' }), text(40, 88, 'A', { size: 8, anchor: 'middle', weight: 700 }), text(140, 88, 'A', { size: 8, anchor: 'middle', weight: 700 }),
    rect(56, 120, 68, 40, { width: 1.5 }), ...[-20, -8, 4, 16].map((d) => [line(56 + d + 8, 160, 56 + d + 8 + 12, 120, { width: 0.7 }).replace('x1="', 'x1="')]).flat(),
    hatchRect(56, 120, 22, 40), hatchRect(102, 120, 22, 40), rect(78, 120, 24, 40, { fill: C.paper, stroke: 'none' }), line(78, 120, 78, 160, { width: 1.5 }), line(102, 120, 102, 160, { width: 1.5 }),
    text(90, 176, 'SECTION A-A', { size: 7, anchor: 'middle', weight: 700 }),
    // half: one quarter removed
    circle(250, 74, 34), circle(250, 74, 12), line(250, 74, 250, 120, { width: 2, dash: '10 3 2 3' }), line(250, 74, 296, 74, { width: 2, dash: '10 3 2 3' }), line(296, 74, 296, 60, { width: 2, arrow: 'end' }), line(250, 120, 236, 120, { width: 2, arrow: 'end' }), text(296, 88, 'B', { size: 8, anchor: 'middle', weight: 700 }), text(230, 116, 'B', { size: 8, anchor: 'middle', weight: 700 }),
    rect(216, 120, 68, 40, { width: 1.5 }), hatchRect(216, 120, 22, 40), cl(250, 116, 250, 164), hidden(262, 120, 262, 160), hidden(278, 120, 278, 160), line(238, 120, 238, 160, { width: 1.5 }),
    text(250, 176, 'HALF SECTION B-B', { size: 7, anchor: 'middle', weight: 700 }), text(250, 186, 'outside one side, inside the other', { size: 6.5, anchor: 'middle', fill: C.muted }),
    // offset: cutting plane jogs through two holes
    rect(356, 44, 108, 60, { width: 1.5 }), circle(378, 60, 7), circle(440, 88, 7), circle(410, 74, 5),
    path('M346,60 L410,60 L410,88 L470,88', { width: 2, dash: '10 3 2 3' }), line(346, 60, 346, 46, { width: 2, arrow: 'end' }), line(470, 88, 470, 74, { width: 2, arrow: 'end' }), text(346, 74, 'C', { size: 8, anchor: 'middle', weight: 700 }), text(470, 102, 'C', { size: 8, anchor: 'middle', weight: 700 }),
    hatchRect(356, 120, 108, 40), rect(372, 120, 12, 40, { fill: C.paper, stroke: 'none' }), rect(434, 120, 12, 40, { fill: C.paper, stroke: 'none' }), line(372, 120, 372, 160, { width: 1.2 }), line(384, 120, 384, 160, { width: 1.2 }), line(434, 120, 434, 160, { width: 1.2 }), line(446, 120, 446, 160, { width: 1.2 }),
    text(410, 176, 'SECTION C-C', { size: 7, anchor: 'middle', weight: 700 }), text(410, 186, 'the jog is never drawn in the section', { size: 6.5, anchor: 'middle', fill: C.muted }),
    // revolved and broken-out
    text(120, 214, 'Revolved section', { anchor: 'middle', weight: 700, size: 10 }), text(360, 214, 'Broken-out section', { anchor: 'middle', weight: 700, size: 10 }),
    rect(40, 236, 160, 20, { width: 1.5, fill: C.grey }), poly([[120, 226], [134, 246], [120, 266], [106, 246]], { width: 1.2, fill: 'url(#hatch)' }), text(120, 282, 'cross-section spun 90° onto the view', { size: 6.5, anchor: 'middle', fill: C.muted }),
    rect(290, 232, 140, 30, { width: 1.5, fill: C.grey }), path('M330,232 c6,8 -4,16 4,22 c6,6 12,-2 18,8 L352,262 L330,262 Z', { width: 1.2, fill: 'url(#hatch)' }), path('M330,232 c6,8 -4,16 4,22 c6,6 12,-2 18,8', { width: 1.2 }), circle(341, 247, 4, { fill: C.paper }),
    text(360, 282, 'freehand break line, no cutting plane needed', { size: 6.5, anchor: 'middle', fill: C.muted }),
  ], { title: 'Section types' }))

fig('drawings/dimensioning-example.svg', 'A machined plate dimensioned the way a print does it: overall size, baseline dimensions from a datum corner, hole callout with diameter, depth and counterbore, thread callout, radius, chamfer note, TYP and the reference dimension in parentheses',
  svg(500, 320, [
    path('M100,60 L360,60 L360,200 L140,200 A40,40 0 0 1 100,160 Z', { width: 1.8, fill: C.grey }),
    circle(150, 100, 10), circle(150, 100, 15, { width: 0.8, dash: '2 2' }), circle(310, 100, 10), circle(310, 100, 15, { width: 0.8, dash: '2 2' }), circle(310, 160, 7), circle(230, 130, 12), cl(216, 130, 244, 130), cl(230, 116, 230, 144),
    cl(138, 100, 162, 100), cl(150, 88, 150, 112), cl(298, 100, 322, 100), cl(310, 88, 310, 112),
    // dimensions
    dim(100, 60, 150, 60, '2.00', { off: 24, size: 8, side: -1 }), dim(100, 60, 310, 60, '8.00', { off: 42, size: 8, side: -1 }), dim(360, 60, 360, 200, '5.50', { off: 30, size: 9, side: -1 }),
    dim(100, 60, 100, 100, '1.50', { off: 26, size: 8, side: 1 }), dim(100, 60, 100, 130, '2.75', { off: 44, size: 8, side: 1 }),
    dim(100, 200, 360, 200, '10.00', { off: 24, size: 9 }), dim(150, 200, 310, 200, '(6.00)', { off: 44, size: 8 }),
    leader(142, 108, 20, 178, '2X Ø.53 THRU\n⌴ Ø.81 ⬇ .38', { size: 8, anchor: 'start' }),
    leader(240, 122, 300, 44, 'Ø1.000 +.002/-.000', { size: 8 }),
    leader(315, 165, 380, 270, '1/2-13 UNC-2B ⬇ .75', { size: 8 }),
    leader(112, 172, 40, 240, 'R1.50', { size: 8 }), text(366, 236, '.06 X 45° CHAMFER\nTYP 4 CORNERS', { size: 7, fill: C.muted }),
    callout(1, 90, 52), callout(2, 372, 100),
    legend(20, 292, ['baseline dimensioning: every length from the datum corner, so errors do not stack', 'a dimension in parentheses is reference only: do not inspect to it'], { size: 8, gap: 12 }),
  ], { title: 'Dimensioning a part' }))

fig('drawings/fit-callout-decoder.svg', 'Decoder for an ISO fit callout Ø50 H7/g6: the hole letter and grade, the shaft letter and grade, the resulting limits, and a bar showing clearance, transition and interference fit families with common examples',
  svg(500, 300, [
    text(250, 30, 'Ø50 H7/g6', { anchor: 'middle', weight: 700, size: 22 }),
    ...[[212, 'Ø50 = basic size, mm'], [252, 'H7 = hole: H (zero line), IT7 grade'], [292, 'g6 = shaft: g (below zero), IT6']].map(([x, t], i) => [line(x, 36, x, 54 + i * 14, { width: 0.8, stroke: C.muted }), text(x + 4, 58 + i * 14, t, { size: 8, fill: C.muted })]),
    table(30, 110, [['Feature', 'Limits (mm)', 'Limits (in)'], ['hole H7', '50.000 to 50.025', '1.9685 to 1.9695'], ['shaft g6', '49.975 to 49.991', '1.9675 to 1.9681'], ['clearance', '0.009 to 0.050', '.0004 to .0020']], [70, 116, 116], { rowH: 18, size: 8 }),
    // fit families bar
    text(400, 120, 'Fit families', { anchor: 'middle', weight: 700, size: 9.5 }),
    rect(346, 128, 108, 60, { fill: C.greenSoft, stroke: 'none' }), text(400, 143, 'clearance', { size: 8, anchor: 'middle', weight: 700, fill: C.green }), text(400, 156, 'H7/g6, H7/f7, H8/e8', { size: 7, anchor: 'middle' }), text(400, 168, 'shaft always smaller', { size: 7, anchor: 'middle', fill: C.muted }), text(400, 180, 'slide, rotate, locate', { size: 7, anchor: 'middle', fill: C.muted }),
    rect(346, 192, 108, 42, { fill: C.soft, stroke: 'none' }), text(400, 206, 'transition', { size: 8, anchor: 'middle', weight: 700, fill: C.accentDark }), text(400, 218, 'H7/k6, H7/n6', { size: 7, anchor: 'middle' }), text(400, 229, 'bearing seats, light press', { size: 7, anchor: 'middle', fill: C.muted }),
    rect(346, 238, 108, 42, { fill: C.redSoft, stroke: 'none' }), text(400, 252, 'interference', { size: 8, anchor: 'middle', weight: 700, fill: C.red }), text(400, 264, 'H7/p6, H7/s6, H7/u6', { size: 7, anchor: 'middle' }), text(400, 275, 'press or shrink fit', { size: 7, anchor: 'middle', fill: C.muted }),
    note(30, 210, 'capital letter = hole, lower case = shaft;\nthe number is the tolerance grade\n(smaller number = tighter).\nH hole with a lettered shaft is the\nhole-basis system: bore stays, shaft moves.', { size: 8.5 }),
    caption(500, 300, 'Read letter then number: where the zone sits, then how wide it is.'),
  ], { title: 'Fit callout decoder' }))

fig('drawings/thread-callout.svg', 'Thread callouts decoded: a unified thread 1/2-13 UNC-2A x 1.50 LG and a metric thread M12 x 1.75-6g, with the schematic and simplified ways threads are drawn on external and internal features',
  svg(500, 280, [
    text(130, 30, '1/2-13 UNC-2A x 1.50 LG', { anchor: 'middle', weight: 700, size: 13 }),
    ...[[46, 'major dia'], [80, 'threads/inch'], [118, 'coarse series'], [154, 'class 2, A = ext'], [200, 'thread length']].map(([x, t], i) => [line(x, 36, x, 50 + (i % 2) * 14, { width: 0.8, stroke: C.muted }), text(x, 62 + (i % 2) * 14, t, { size: 7, anchor: 'middle', fill: C.muted })]),
    text(370, 30, 'M12 x 1.75 - 6g', { anchor: 'middle', weight: 700, size: 13 }),
    ...[[326, 'metric, 12 mm'], [368, 'pitch, mm'], [406, 'tolerance class'], [420, 'g = ext, H = int']].map(([x, t], i) => [line(x, 36, x, 50 + (i % 2) * 14, { width: 0.8, stroke: C.muted }), text(x, 62 + (i % 2) * 14, t, { size: 7, anchor: 'middle', fill: C.muted })]),
    // external thread drawn: simplified (dashed minor lines) and schematic
    text(130, 110, 'External thread, simplified', { anchor: 'middle', weight: 700, size: 9 }),
    rect(60, 120, 140, 30, { width: 1.5, fill: C.grey }), hidden(60, 125, 200, 125), hidden(60, 145, 200, 145), line(120, 120, 120, 150, { width: 0.9 }), line(120, 120, 128, 116, { width: 0.9 }), text(118, 112, 'chamfer', { size: 6.5, anchor: 'end', fill: C.muted }),
    dim(60, 150, 120, 150, '1.50', { off: 16, size: 8 }),
    text(130, 190, 'Schematic (older prints)', { anchor: 'middle', weight: 700, size: 9 }),
    rect(60, 200, 140, 30, { width: 1.5, fill: C.grey }), ...[0, 1, 2, 3, 4, 5].map((i) => [line(70 + i * 10, 200, 70 + i * 10, 230, { width: 1.6 }), line(75 + i * 10, 204, 75 + i * 10, 226, { width: 0.8 })]),
    // internal thread: tapped hole in section
    text(370, 110, 'Tapped hole, in section', { anchor: 'middle', weight: 700, size: 9 }),
    hatchRect(300, 120, 140, 70), rect(356, 120, 28, 50, { fill: C.paper, stroke: 'none' }), line(356, 120, 356, 170, { width: 1.5 }), line(384, 120, 384, 170, { width: 1.5 }), hidden(352, 120, 352, 170), hidden(388, 120, 388, 170),
    path('M356,170 L370,182 L384,170', { width: 1.5 }), rect(362, 170, 16, 0, { width: 0 }), line(356, 170, 384, 170, { width: 1.5 }),
    text(370, 208, 'drill point 118°: the tap drill goes deeper than the thread', { size: 6.5, anchor: 'middle', fill: C.muted }),
    leader(388, 140, 452, 130, 'THD', { size: 7.5 }), leader(352, 155, 452, 165, 'tap drill', { size: 7.5 }),
    note(250, 252, 'A = external (bolt), B = internal (nut); 2 is the everyday class, 3 is precision.\nLH after the callout means left-hand: everything else is right-hand.', { anchor: 'middle', size: 8.5 }),
  ], { title: 'Thread callouts' }))

fig('drawings/surface-finish-symbol.svg', 'Surface finish symbol anatomy: the check mark with roughness value in microinches or micrometres, the horizontal bar for machining required, the circle for machining prohibited, lay direction symbol, machining allowance, and a table of common Ra values by process',
  svg(500, 290, [
    // big symbol
    path('M60,110 L74,146 L104,70', { width: 2 }), line(84, 98, 120, 98, { width: 1.6 }), text(94, 108, '63', { size: 12, weight: 700 }), text(90, 84, 'a', { size: 8, fill: C.muted }), text(110, 84, 'b', { size: 8, fill: C.muted }), text(122, 120, '=', { size: 12, weight: 700 }), text(68, 130, '.010', { size: 9, weight: 700 }),
    ...[[100, 104, 'Ra 63 µin (1.6 µm) max', 150, 60], [116, 96, 'bar over: method (a),\nother requirements (b)', 170, 84], [126, 118, 'lay: = parallel, ⊥ perpendicular,\nX crossed, M multi, C circular', 170, 122], [80, 128, 'machining allowance .010 in', 150, 160]].map(([x, y, t, tx, ty]) => leader(x, y, tx, ty, t, { size: 7.5 })),
    // variants
    text(60, 190, 'Variants', { weight: 700, size: 9.5 }),
    ...[[40, 'basic: any process'], [150, 'bar: material must be removed'], [270, 'circle: no machining allowed'], [380, 'all surfaces this finish']].map(([x, t], i) => [path(`M${x},214 L${x + 7},232 L${x + 22},194`, { width: 1.6 }), ...(i === 1 ? [line(x + 7, 204, x + 22, 204, { width: 1.4 })] : []), ...(i === 2 ? [circle(x + 9, 220, 5)] : []), ...(i === 3 ? [circle(x - 6, 228, 3), text(x + 28, 218, '125', { size: 8 })] : []), text(x + 12, 250, t, { size: 7, anchor: 'middle', fill: C.muted })]),
    table(300, 60, [['Ra µin', 'µm', 'process'], ['500', '12.5', 'flame cut, rough cast'], ['250', '6.3', 'rough machining'], ['125', '3.2', 'milling, drilling'], ['63', '1.6', 'good turning, shaft OD'], ['32', '0.8', 'fine turn, grind, seals'], ['16', '0.4', 'grinding, bearing journals'], ['8', '0.2', 'honing, lapping']], [40, 34, 116], { rowH: 15, size: 7 }),
    caption(500, 290, 'Lower Ra number = smoother; 63 is a good turned finish, 16 a bearing journal.'),
  ], { title: 'Surface finish symbol' }))

fig('drawings/assembly-balloons-parts-list.svg', 'Assembly drawing of a pillow block with balloon numbers on leaders pointing at each part and the parts list that ties the balloons to item number, quantity, part number, description and material',
  svg(500, 300, [
    // pillow block section: base, cap, bearing, shaft, bolts
    plate(60, 170, 200, 30), path('M90,170 a70,70 0 0 1 140,0 Z', { width: 1.5, fill: C.steel }), line(90, 170, 230, 170, { width: 1.5 }),
    circle(160, 150, 36, { fill: C.paper }), circle(160, 150, 26, { fill: C.grey }), circle(160, 150, 16, { fill: C.steelDark }),
    rect(96, 100, 12, 20, { fill: C.steelDark }), rect(212, 100, 12, 20, { fill: C.steelDark }), rect(94, 96, 16, 5, { fill: C.ink }), rect(210, 96, 16, 5, { fill: C.ink }),
    circle(80, 185, 5, { fill: C.paper }), circle(240, 185, 5, { fill: C.paper }),
    text(160, 226, 'PILLOW BLOCK, 2 IN BORE', { size: 8, anchor: 'middle', weight: 700 }),
    ...[[1, 70, 192, 30, 236], [2, 150, 104, 120, 50], [3, 160, 150, 250, 100], [4, 160, 130, 250, 60], [5, 218, 100, 280, 140]].map(([n, x, y, tx, ty]) => [line(x, y, tx, ty, { width: 0.8, arrow: 'end' }).replace(`x1="${x}"`, `x1="${x}"`), circle(tx, ty, 10, { fill: C.paper }), text(tx, ty + 3.5, String(n), { size: 9, anchor: 'middle', weight: 700 })]),
    table(300, 40, [['ITEM', 'QTY', 'PART NO', 'DESCRIPTION'], ['1', '1', 'PB-200-B', 'base, cast iron'], ['2', '1', 'PB-200-C', 'cap, cast iron'], ['3', '1', '22212 EK', 'spherical roller brg'], ['4', '1', 'H-312', 'adapter sleeve'], ['5', '2', '1/2-13 x 2', 'cap bolt, gr 5']], [30, 26, 60, 70], { rowH: 18, size: 7 }),
    note(300, 172, 'balloon = item number, not part number;\nthe list gives the part number to order', { size: 8 }),
    caption(500, 300, 'Read the balloon, find the row: item, quantity, part number, material.'),
  ], { title: 'Assembly drawing with balloons' }))

// ================= GD&T =================
fig('drawings/gdt-why.svg', 'Why GD&T exists: a hole located with plus-minus coordinate tolerances gets a square tolerance zone, while a position tolerance gives a round zone of the same corner-to-corner size with 57 percent more usable area, and the zone can grow with bonus tolerance',
  svg(500, 250, [
    text(125, 24, 'Plus-minus: square zone', { anchor: 'middle', weight: 700, size: 11 }), text(375, 24, 'Position: round zone', { anchor: 'middle', weight: 700, size: 11 }),
    rect(75, 70, 100, 100, { fill: C.redSoft, stroke: C.red, width: 1.2 }), cl(55, 120, 195, 120), cl(125, 50, 125, 190), circle(125, 120, 3, { fill: C.ink }),
    dim(75, 170, 175, 170, '±.005 = .010', { off: 20, size: 8 }), dim(175, 70, 175, 170, '.010', { off: 18, size: 8, side: -1 }),
    circle(375, 120, 70, { fill: C.greenSoft, stroke: C.green, width: 1.2 }), cl(295, 120, 455, 120), cl(375, 40, 375, 200), circle(375, 120, 3, { fill: C.ink }),
    dim(305, 120, 445, 120, 'Ø.014', { off: 78, size: 8 }), line(325, 70, 425, 170, { width: 0.8, stroke: C.muted, dash: '3 2' }),
    text(125, 210, 'the corners are as far off as .007\nbut a point .006 off on the axis fails', { size: 8, anchor: 'middle', fill: C.muted }),
    text(375, 226, 'same corner distance, 57% more area, and the\nzone grows with bonus at MMC', { size: 8, anchor: 'middle', fill: C.muted }),
  ], { title: 'Square versus round tolerance zone' }))

const posSym = (x, y, r) => [circle(x, y, r), line(x - r * 1.6, y, x + r * 1.6, y, { width: 1.3 }), line(x, y - r * 1.6, x, y + r * 1.6, { width: 1.3 })]
const fcf = (x, y, cells, { h = 22, size = 11 } = {}) => {
  let cx = x; const out = []
  cells.forEach(([s, w]) => { out.push(rect(cx, y, w, h, { width: 1.4 })); if (s === '⌖') out.push(...posSym(cx + w / 2, y + h / 2, h * 0.22)); else out.push(text(cx + w / 2, y + h / 2 + 4, s, { size, anchor: 'middle', weight: 600 })); cx += w })
  return out
}
fig('drawings/feature-control-frame-anatomy.svg', 'Anatomy of a feature control frame: geometric characteristic symbol, diameter symbol, tolerance value, material condition modifier, then the primary, secondary and tertiary datum references, read left to right',
  svg(500, 250, [
    ...fcf(60, 80, [['⌖', 40], ['Ø .014 Ⓜ', 110], ['A', 40], ['B Ⓜ', 60], ['C', 40]], { h: 36, size: 15 }),
    ...[[80, 116, 'characteristic:\nposition', 80, 150], [150, 116, 'Ø = cylindrical zone', 150, 172], [200, 116, 'tolerance .014 at MMC', 220, 194], [270, 116, 'primary datum A\n(3 points, plane)', 300, 150], [320, 116, 'secondary B at MMC\n(2 points)', 360, 172], [370, 116, 'tertiary C\n(1 point)', 420, 194]].map(([x, y, t, tx, ty], i) => leader(x, y, tx, ty, t, { size: 8, anchor: 'middle' })),
    text(60, 62, 'read it as a sentence:', { size: 9, fill: C.muted }),
    note(250, 230, 'the axis of this hole must lie in a Ø.014 cylinder (bigger if the hole\nis bigger than MMC), located from A, then B, then C', { anchor: 'middle', size: 8.5 }),
  ], { title: 'Feature control frame anatomy' }))

fig('drawings/datum-symbols.svg', 'Datum symbols: the datum feature symbol (letter in a square on a leader with a filled triangle) applied to a surface, to a size feature and to a feature control frame, datum targets, and the 3-2-1 datum reference frame of three mutually perpendicular planes',
  svg(500, 300, [
    text(110, 22, 'Datum feature symbol', { anchor: 'middle', weight: 700, size: 10 }),
    rect(40, 50, 120, 70, { fill: C.grey }), poly([[80, 120], [88, 132], [72, 132]], { fill: C.ink }), line(80, 132, 80, 146, { width: 1.2 }), rect(70, 146, 20, 20, { width: 1.4 }), text(80, 161, 'A', { size: 11, anchor: 'middle', weight: 700 }),
    text(96, 158, 'on the surface', { size: 7.5, fill: C.muted }),
    // on a size feature: aligned with the dimension
    text(110, 190, 'On a size feature (axis)', { anchor: 'middle', weight: 700, size: 10 }),
    rect(40, 206, 120, 40, { fill: C.grey }), dim(40, 206, 40, 246, 'Ø2.000', { off: -24, size: 8, side: 1 }), poly([[16, 226], [8, 220], [8, 232]], { fill: C.ink }), line(8, 226, 0, 226, { width: 0 }), rect(12, 250, 20, 20, { width: 1.4 }), text(22, 265, 'B', { size: 11, anchor: 'middle', weight: 700 }), line(16, 232, 22, 250, { width: 1.2 }),
    text(60, 266, 'in line with the size dim = the axis is the datum', { size: 7, fill: C.muted }),
    // datum target
    text(300, 22, 'Datum target', { anchor: 'middle', weight: 700, size: 10 }),
    circle(300, 70, 16), line(284, 70, 316, 70, { width: 1.2 }), text(300, 66, 'Ø.50', { size: 7, anchor: 'middle' }), text(300, 80, 'A1', { size: 8, anchor: 'middle', weight: 700 }), line(300, 86, 300, 110, { width: 1 }), path('M296,110 l8,0 l-4,-6 z', { fill: C.ink }),
    text(300, 128, 'a specified point, line or area\nfor touching a cast surface', { size: 7.5, anchor: 'middle', fill: C.muted }),
    // datum reference frame
    text(410, 22, '3-2-1 frame', { anchor: 'middle', weight: 700, size: 10 }),
    poly([[360, 120], [460, 120], [480, 100], [380, 100]], { fill: C.grey, width: 1.2 }), poly([[360, 50], [360, 120], [380, 100], [380, 30]], { fill: C.light, width: 1.2 }), poly([[360, 50], [460, 50], [460, 120], [360, 120]], { fill: C.paper, width: 1.2, opacity: 0.85 }),
    text(410, 90, 'A: 3 pts', { size: 8, anchor: 'middle', weight: 700 }), text(368, 132, 'B: 2 pts', { size: 8, weight: 700 }), text(388, 40, 'C: 1 pt', { size: 8, weight: 700 }),
    text(420, 160, 'three perpendicular planes\nlock all six degrees of\nfreedom in the order A, B, C', { size: 7.5, anchor: 'middle', fill: C.muted }),
    caption(500, 300, 'The triangle points at what you rest the part on; the letter names it.'),
  ], { title: 'Datum symbols and the datum frame' }))

const sym = {
  flatness: (x, y) => [poly([[x - 12, y + 6], [x - 4, y - 6], [x + 12, y - 6], [x + 4, y + 6]], { width: 1.6 })],
  straightness: (x, y) => [line(x - 12, y, x + 12, y, { width: 1.8 })],
  circularity: (x, y) => [circle(x, y, 9)],
  cylindricity: (x, y) => [circle(x, y, 8), line(x - 14, y + 10, x - 8, y - 10, { width: 1.6 }), line(x + 8, y + 10, x + 14, y - 10, { width: 1.6 })],
  profileLine: (x, y) => [path(`M${x - 12},${y + 6} a12,12 0 0 1 24,0`, { width: 1.8 })],
  profileSurface: (x, y) => [path(`M${x - 12},${y + 6} a12,12 0 0 1 24,0 z`, { width: 1.8 })],
  perpendicularity: (x, y) => [line(x - 12, y + 8, x + 12, y + 8, { width: 1.8 }), line(x, y + 8, x, y - 10, { width: 1.8 })],
  angularity: (x, y) => [line(x - 12, y + 8, x + 12, y + 8, { width: 1.8 }), line(x - 12, y + 8, x + 8, y - 8, { width: 1.8 })],
  parallelism: (x, y) => [line(x - 8, y + 10, x - 2, y - 10, { width: 1.8 }), line(x + 2, y + 10, x + 8, y - 10, { width: 1.8 })],
  position: (x, y) => [circle(x, y, 8), line(x - 13, y, x + 13, y, { width: 1.6 }), line(x, y - 13, x, y + 13, { width: 1.6 })],
  concentricity: (x, y) => [circle(x, y, 9), circle(x, y, 4)],
  symmetry: (x, y) => [line(x - 10, y - 6, x + 10, y - 6, { width: 1.8 }), line(x - 6, y, x + 6, y, { width: 1.8 }), line(x - 10, y + 6, x + 10, y + 6, { width: 1.8 })],
  runout: (x, y) => [line(x - 10, y + 8, x + 4, y - 8, { width: 1.6, arrow: 'end' })],
  totalRunout: (x, y) => [line(x - 10, y + 8, x + 4, y - 8, { width: 1.6, arrow: 'end' }), line(x - 4, y + 8, x + 10, y - 8, { width: 1.6, arrow: 'end' }), line(x - 10, y + 8, x - 4, y + 8, { width: 1.6 })],
}
sheetFig('drawings/gdt-symbol-sheet.svg', 'The fourteen geometric characteristic symbols of ASME Y14.5 grouped by type: form (flatness, straightness, circularity, cylindricity), profile (line, surface), orientation (perpendicularity, angularity, parallelism), location (position, concentricity, symmetry) and runout (circular, total), with whether each needs a datum', 'GD&T characteristic symbols', [
  cell('flatness', (x, y) => sym.flatness(x, y), 'form, no datum'),
  cell('straightness', (x, y) => sym.straightness(x, y), 'form, no datum'),
  cell('circularity', (x, y) => sym.circularity(x, y), 'form, no datum'),
  cell('cylindricity', (x, y) => sym.cylindricity(x, y), 'form, no datum'),
  cell('profile of a line', (x, y) => sym.profileLine(x, y), 'profile, datum optional'),
  cell('profile of a surface', (x, y) => sym.profileSurface(x, y), 'profile, datum optional'),
  cell('perpendicularity', (x, y) => sym.perpendicularity(x, y), 'orientation, datum'),
  cell('angularity', (x, y) => sym.angularity(x, y), 'orientation, datum'),
  cell('parallelism', (x, y) => sym.parallelism(x, y), 'orientation, datum'),
  cell('position', (x, y) => sym.position(x, y), 'location, datums'),
  cell('concentricity', (x, y) => sym.concentricity(x, y), 'location (dropped 2018)'),
  cell('symmetry', (x, y) => sym.symmetry(x, y), 'location (dropped 2018)'),
  cell('circular runout', (x, y) => sym.runout(x, y), 'runout, datum axis'),
  cell('total runout', (x, y) => sym.totalRunout(x, y), 'runout, datum axis'),
  cell('modifiers', (x, y) => [circle(x - 24, y, 8), text(x - 24, y + 3.5, 'M', { size: 9, anchor: 'middle', weight: 700 }), circle(x, y, 8), text(x, y + 3.5, 'L', { size: 9, anchor: 'middle', weight: 700 }), circle(x + 24, y, 8), text(x + 24, y + 3.5, 'P', { size: 9, anchor: 'middle', weight: 700 })], 'MMC, LMC, projected'),
  cell('other symbols', (x, y) => [text(x - 30, y + 4, 'Ø', { size: 12, anchor: 'middle', weight: 700 }), text(x - 10, y + 4, 'SØ', { size: 10, anchor: 'middle', weight: 700 }), text(x + 12, y + 4, 'R', { size: 12, anchor: 'middle', weight: 700 }), text(x + 32, y + 4, '(  )', { size: 11, anchor: 'middle', weight: 700 })], 'dia, sphere, radius, ref'),
], { cols: 4, cellH: 84, symH: 40 }, 'Form needs no datum; orientation, location and runout are measured from one.')

fig('drawings/bonus-tolerance.svg', 'Bonus tolerance at MMC: a hole toleranced Ø.014 at MMC on a Ø.500 to .520 hole, showing how the allowed position tolerance grows as the actual hole gets larger, with the table of actual size against total allowed tolerance',
  svg(500, 250, [
    ...fcf(40, 30, [['⌖', 30], ['Ø .014 Ⓜ', 90], ['A', 30], ['B', 30], ['C', 30]], { h: 26, size: 12 }),
    text(40, 76, 'Ø.500 to .520 hole (MMC = .500, the smallest hole)', { size: 9 }),
    table(40, 90, [['actual hole', 'bonus', 'total position tol'], ['.500 (MMC)', '.000', 'Ø.014'], ['.505', '.005', 'Ø.019'], ['.510', '.010', 'Ø.024'], ['.520 (LMC)', '.020', 'Ø.034']], [80, 50, 110], { rowH: 18, size: 8.5 }),
    // zone growing
    ...[[320, .014], [370, .019], [420, .024], [470, .034]].map(([x, t], i) => [circle(x, 140, 8 + i * 6, { fill: C.greenSoft, stroke: C.green, width: 1 }), text(x, 190, `Ø${t.toFixed(3)}`, { size: 7.5, anchor: 'middle' }), text(x, 202, ['.500', '.505', '.510', '.520'][i], { size: 7, anchor: 'middle', fill: C.muted })]),
    text(395, 104, 'zone grows with the hole', { size: 8.5, anchor: 'middle', weight: 700 }),
    note(250, 236, 'a bigger hole has more room for the bolt, so the standard lets its axis wander more: that is the bonus', { anchor: 'middle', size: 8 }),
  ], { title: 'Bonus tolerance at MMC' }))

fig('drawings/tolerance-zones.svg', 'Tolerance zones you can picture: flatness as two parallel planes the surface must stay between, perpendicularity of a bore as a cylinder the axis must stay inside, position of a hole as a cylinder about the true position, and circular runout as the dial movement in one revolution',
  svg(500, 300, [
    ...[['Flatness .002', 20], ['Perpendicularity Ø.003 | A', 260]].map(([t, x]) => text(x + 110, 22, t, { anchor: 'middle', weight: 700, size: 10 })),
    // flatness
    path('M40,90 q40,-10 80,0 t80,0', { width: 2 }), line(40, 80, 200, 80, { width: 0.9, dash: '4 3', stroke: C.red }), line(40, 100, 200, 100, { width: 0.9, dash: '4 3', stroke: C.red }), rect(40, 90, 160, 40, { fill: C.grey, stroke: 'none' }), path('M40,90 q40,-10 80,0 t80,0 L200,130 L40,130 Z', { fill: C.grey, width: 0 }), path('M40,90 q40,-10 80,0 t80,0', { width: 2 }),
    dim(210, 80, 210, 100, '.002', { off: -8, size: 8 }), text(120, 148, 'every point of the surface between two planes .002 apart', { size: 7.5, anchor: 'middle', fill: C.muted }),
    // perpendicularity of a bore
    plate(280, 100, 160, 30), rect(345, 50, 30, 80, { fill: C.paper }), line(345, 50, 345, 130, { width: 1.5 }), line(375, 50, 375, 130, { width: 1.5 }), poly([[300, 130], [308, 142], [292, 142]], { fill: C.ink }), rect(290, 146, 20, 18, { width: 1.2 }), text(300, 159, 'A', { size: 9, anchor: 'middle', weight: 700 }),
    rect(357, 44, 6, 92, { fill: C.greenSoft, stroke: C.green, width: 0.8 }), cl(360, 40, 360, 140), text(420, 66, 'axis inside a\nØ.003 cylinder\nsquare to A', { size: 7.5, fill: C.muted }),
    // position
    text(130, 190, 'Position Ø.014 | A B C', { anchor: 'middle', weight: 700, size: 10 }),
    rect(40, 200, 150, 80, { fill: C.grey }), cl(110, 210, 110, 270), cl(80, 240, 140, 240), circle(110, 240, 22), circle(110, 240, 8, { fill: C.greenSoft, stroke: C.green, width: 1 }), circle(110, 240, 2, { fill: C.ink }),
    dim(40, 240, 110, 240, '2.000', { off: 30, size: 8 }), dim(110, 200, 110, 240, '1.000', { off: -50, size: 8, side: 1 }),
    text(196, 226, 'basic dims (boxed)\nlocate the true\ncentre; the axis\nstays in the Ø.014\ncylinder', { size: 7, fill: C.muted }),
    // runout
    text(370, 190, 'Circular runout .002 | A', { anchor: 'middle', weight: 700, size: 10 }),
    rect(290, 220, 160, 40, { fill: C.steel }), cl(280, 240, 460, 240), text(380, 274, 'A', { size: 8, weight: 700, anchor: 'middle' }), poly([[380, 268], [386, 262], [374, 262]], { fill: C.ink }).replace('points="380,268 386,262 374,262"', 'points="380,262 386,270 374,270"'),
    circle(330, 205, 7), line(330, 212, 330, 220, { width: 1.5 }), path('M327,205 l3,-4 l2,4', { width: 1 }), text(392, 206, 'dial: total movement\nin one turn under .002', { size: 7.5, fill: C.muted }),
  ], { title: 'Tolerance zones illustrated' }))

fig('drawings/gdt-housing-example.svg', 'Worked example of a bearing housing drawn with GD&T: the mounting face is datum A, the pilot diameter datum B, the bearing bore carries a position tolerance to A and B and a perpendicularity to A, the bore face has runout to the bore axis, and each callout is translated into what to measure',
  svg(500, 320, [
    // housing in section: flange with pilot, bore
    hatchRect(120, 60, 200, 40), hatchRect(180, 100, 80, 120), rect(200, 60, 40, 160, { fill: C.paper, stroke: 'none' }), line(200, 60, 200, 220, { width: 1.5 }), line(240, 60, 240, 220, { width: 1.5 }), line(120, 60, 320, 60, { width: 1.5 }), line(120, 100, 180, 100, { width: 1.5 }), line(260, 100, 320, 100, { width: 1.5 }), line(180, 100, 180, 220, { width: 1.5 }), line(260, 100, 260, 220, { width: 1.5 }), line(180, 220, 260, 220, { width: 1.5 }), line(120, 60, 120, 100, { width: 1.5 }), line(320, 60, 320, 100, { width: 1.5 }),
    cl(220, 40, 220, 240),
    // datum A: mounting face (top of flange)
    poly([[150, 60], [156, 50], [144, 50]], { fill: C.ink }), line(150, 50, 150, 40, { width: 1.2 }), rect(140, 22, 20, 18, { width: 1.2 }), text(150, 35, 'A', { size: 9, anchor: 'middle', weight: 700 }),
    // datum B: pilot OD at the flange bottom (drawn as size dim on the boss)
    dim(180, 226, 260, 226, 'Ø4.000 -.001', { off: 26, size: 8 }), rect(210, 262, 20, 18, { width: 1.2 }), text(220, 275, 'B', { size: 9, anchor: 'middle', weight: 700 }), poly([[220, 262], [226, 254], [214, 254]], { fill: C.ink }),
    // bore callout with frames
    leader(240, 140, 300, 130, '', { size: 1 }), text(300, 126, 'Ø3.5433 +.0008/-0', { size: 8.5, weight: 700 }),
    ...fcf(300, 132, [['⌖', 18], ['Ø.004', 42], ['A', 18], ['B', 18]], { h: 16, size: 8 }), ...fcf(300, 150, [['⊥', 18], ['Ø.002', 42], ['A', 18]], { h: 16, size: 8 }),
    // face runout
    leader(200, 110, 60, 130, '', { size: 1 }), ...fcf(20, 136, [['↗', 18], ['.003', 34], ['B', 18]], { h: 16, size: 8 }), text(24, 128, 'bore face', { size: 7, fill: C.muted }),
    // translation table
    table(20, 236, [['callout', 'what you measure'], ['position Ø.004 A B', 'bore centre vs pilot centre: dial indicate both, difference x2 under .004'], ['perp. Ø.002 A', 'bore square to the face: indicator sweep in the bore, top vs bottom'], ['runout .003 B', 'face wobble: dial on the face while turning about the pilot']], [80, 400], { rowH: 15, size: 7 }),
    caption(500, 320, 'Set up on A and B the way the frame lists them, then measure the bore.'),
  ], { title: 'GD&T on a bearing housing' }))

// ================= Structural callouts =================
fig('drawings/structural-connection-callouts.svg', 'Structural detail callouts a millwright meets: beam designation W12x26, a bolted connection callout with bolt size, grade and count, a fillet weld symbol, a column with base plate and the abbreviations TOS and BOS for top and bottom of steel',
  svg(500, 280, [
    // beam to column connection in elevation
    rect(60, 40, 30, 200, { fill: C.steel }), text(75, 270, 'COL C-3', { size: 7.5, anchor: 'middle', weight: 700 }),
    rect(90, 100, 200, 14, { fill: C.steel }), rect(90, 150, 200, 14, { fill: C.steel }), rect(90, 114, 200, 36, { fill: C.light, stroke: C.ink, width: 1 }),
    text(190, 136, 'W12x26', { size: 10, anchor: 'middle', weight: 700 }),
    rect(90, 106, 12, 54, { fill: C.steelDark }), ...[116, 130, 144].map((y) => circle(96, y, 3, { fill: C.paper })),
    leader(96, 130, 150, 32, '3 - 3/4" Ø A325-N bolts\nsnug tight, double angle', { size: 8 }),
    leader(190, 100, 250, 66, 'W12x26: W shape, 12 in deep, 26 lb/ft', { size: 8 }),
    // TOS / BOS
    line(290, 100, 340, 100, { width: 0.8, stroke: C.muted }), text(344, 103, 'TOS EL 112\'-6"', { size: 8 }), line(290, 164, 340, 164, { width: 0.8, stroke: C.muted }), text(344, 167, 'BOS EL 111\'-6"', { size: 8 }),
    // weld symbol on a stiffener
    rect(102, 200, 8, 40, { fill: C.steelDark }), line(110, 210, 150, 196, { width: 0.9 }), line(150, 196, 190, 196, { width: 0.9 }), path('M156,196 l0,-8 l10,8', { width: 1.2 }), text(170, 192, '1/4', { size: 7 }),
    text(160, 226, 'fillet weld 1/4 in, arrow side', { size: 7.5, fill: C.muted }),
    // base plate
    plate(40, 240, 70, 8), rect(30, 248, 90, 6, { fill: C.soft, width: 1 }), text(140, 246, 'PL 1" x 14 x 14 base plate, 4 - 1" AB', { size: 7.5 }), text(140, 258, 'grout 1 1/2" (see F-201)', { size: 7.5, fill: C.muted }),
    note(400, 220, 'bolted or welded is the\nconnection detail; the\nmillwright checks it was\ndone before loading it', { size: 8, anchor: 'middle' }),
  ], { title: 'Structural connection callouts' }))
