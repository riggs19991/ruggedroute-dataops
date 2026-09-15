// Drawings, schematics and P&IDs (part 2): hydraulic and pneumatic symbol sheets, circuit diagrams,
// electrical symbols, motor-control schematics, installation drawings. Symbols come from lib-symbols.mjs.
import { svg, text, line, rect, circle, path, poly, g, dim, leader, table, caption, box, callout, legend, note, fig, C, hatchRect, plate } from './lib.mjs'
import * as S from './lib-symbols.mjs'

const cell = (name, draw, note) => ({ name, draw, note })
const sheetFig = (file, alt, title, cells, opts = {}, cap) => {
  const h = S.sheetHeight(cells.length, opts)
  fig(file, alt, svg(500, h, [...S.sheet(cells, opts), cap ? caption(500, h, cap) : ''], { title }))
}
const vline = (x, y1, y2, kind = 'work') => S.fl(x, y1, x, y2, kind)

// ---------- Hydraulic sheet 1: lines, sources, reservoirs ----------
sheetFig('drawings/hyd-lines-sources-sheet.svg', 'ISO 1219 lines and sources: working, pilot and drain lines, crossings and junctions, plugged ports, vented and pressurised reservoirs, pressure source, electric motor and engine', 'Hydraulic lines and sources', [
  cell('working line', (x, y) => [S.fl(x - 30, y, x + 30, y, 'work')], 'solid: supply, return'),
  cell('pilot line', (x, y) => [S.fl(x - 30, y, x + 30, y, 'pilot')], 'long dashes: control'),
  cell('drain line', (x, y) => [S.fl(x - 30, y, x + 30, y, 'drain')], 'short dashes: leakage'),
  cell('enclosure', (x, y) => [rect(x - 26, y - 14, 52, 28, { ...S.LINE.enclosure })], 'chain: one assembly'),
  cell('crossing', (x, y) => [S.fl(x - 22, y, x + 22, y), S.fl(x, y - 16, x, y + 16)], 'no dot: not joined'),
  cell('junction', (x, y) => [S.fl(x - 22, y, x + 22, y), S.fl(x, y - 16, x, y + 16), S.junction(x, y)], 'dot: connected'),
  cell('plugged port', (x, y) => [S.fl(x - 22, y, x, y), path(`M${x - 5},${y - 5} l10,10 M${x - 5},${y + 5} l10,-10`, { width: 1.6 })], 'X on the port'),
  cell('flexible hose', (x, y) => [path(`M${x - 24},${y} q8,-12 16,0 t16,0 t16,0`, { width: 1.5 })], 'arc = hose'),
  cell('vented reservoir', (x, y) => [...S.tank(x, y - 4, { stub: 16 })], 'open top: atmospheric'),
  cell('pressurised reservoir', (x, y) => [...S.tank(x, y - 4, { pressurised: true, stub: 16 })], 'closed box'),
  cell('return above level', (x, y) => [...S.tank(x, y - 4, { aboveLevel: true, stub: 16 })], 'line stops short'),
  cell('return below level', (x, y) => [...S.tank(x, y - 4, { stub: 16 })], 'line to the bottom'),
  cell('pressure source', (x, y) => [...S.pressureSource(x, y)], 'circle and dot'),
  cell('electric motor', (x, y) => [...S.electricMotor(x, y)], 'prime mover'),
  cell('engine', (x, y) => [rect(x - 12, y - 10, 24, 20), text(x, y + 4, 'M', { size: 10, anchor: 'middle', weight: 700 }), poly([[x - 12, y - 10], [x - 4, y - 10], [x - 12, y - 4]], { fill: C.ink })], 'square: combustion'),
  cell('pump + motor set', (x, y) => [...S.electricMotor(x - 18, y, 9), line(x - 9, y, x - 2, y, { width: 2 }), ...S.pump(x + 12, y, { r: 13 })], 'shaft = double line'),
], { cols: 4 }, 'Every line is one of four kinds; a dot is the only way two lines join.')

// ---------- Hydraulic sheet 2: pumps and motors ----------
sheetFig('drawings/hyd-pumps-motors-sheet.svg', 'ISO 1219 pumps and motors: fixed, variable, bi-directional, pressure-compensated and load-sensing pumps, case drain, fixed and variable motors, pump-motor unit, rotary actuator', 'Hydraulic pumps and motors', [
  cell('fixed pump', (x, y) => [...S.pump(x, y), vline(x, y + 16, y + 26)], 'triangle out = flow out'),
  cell('variable pump', (x, y) => [...S.pump(x, y, { variable: true }), vline(x, y + 16, y + 26)], 'arrow through = variable'),
  cell('bi-directional pump', (x, y) => [...S.pump(x, y, { bidir: true })], 'two triangles'),
  cell('pressure-compensated', (x, y) => [...S.pump(x - 10, y, { variable: true, comp: true })], 'compensator box'),
  cell('load-sensing pump', (x, y) => [...S.pump(x - 10, y, { variable: true, comp: true, ls: true })], 'LS pilot to control'),
  cell('pump with case drain', (x, y) => [...S.pump(x, y, { drain: true }), vline(x, y + 16, y + 26)], 'drain to tank'),
  cell('fixed motor', (x, y) => [...S.hmotor(x, y)], 'triangle in = flow in'),
  cell('variable motor', (x, y) => [...S.hmotor(x, y, { variable: true })], 'arrow through'),
  cell('bi-directional motor', (x, y) => [...S.hmotor(x, y, { bidir: true })], 'runs either way'),
  cell('pump-motor unit', (x, y) => [...S.pumpMotor(x, y)], 'hydrostatic transmission'),
  cell('rotary actuator', (x, y) => [rect(x - 16, y - 9, 32, 18), path(`M${x - 8},${y - 16} a12,12 0 0 1 16,0`, { width: 1.3, arrow: 'both' })], 'limited rotation'),
  cell('pneumatic pump', (x, y) => [...S.pump(x, y, { pneumatic: true })], 'open triangle = air'),
], { cols: 4 }, 'Filled triangle = oil, open = air; the point shows flow direction.')

// ---------- Hydraulic sheet 3: cylinders ----------
sheetFig('drawings/hyd-cylinders-sheet.svg', 'ISO 1219 cylinders: single-acting spring return, single-acting gravity return, double-acting, double-rod, adjustable cushions, telescopic, pressure intensifier', 'Hydraulic cylinders', [
  cell('spring return', (x, y) => [...S.cylinder(x - 8, y, { single: true, spring: true, w: 54 })], 'single-acting, one port'),
  cell('load return', (x, y) => [...S.cylinder(x - 8, y, { single: true, w: 54 })], 'single-acting, vented end'),
  cell('double-acting', (x, y) => [...S.cylinder(x - 8, y, { w: 54 })], 'ports both ends'),
  cell('double-rod', (x, y) => [...S.cylinder(x, y, { doubleRod: true, w: 46, rodLen: 16 })], 'equal areas both ways'),
  cell('adjustable cushions', (x, y) => [...S.cylinder(x - 8, y, { cushion: true, w: 58 })], 'boxes at the ends'),
  cell('telescopic', (x, y) => [...S.cylinder(x - 8, y, { telescopic: true, w: 54 })], 'nested stages'),
  cell('intensifier', (x, y) => [rect(x - 26, y - 10, 30, 20), rect(x + 4, y - 6, 20, 12), line(x - 26, y, x - 34, y, { width: 1.5 }), line(x + 24, y, x + 32, y, { width: 1.5 }), text(x - 11, y + 3, 'p', { size: 8, anchor: 'middle' }), text(x + 14, y + 3, 'P', { size: 8, anchor: 'middle' })], 'small to big pressure'),
  cell('semi-rotary actuator', (x, y) => [rect(x - 18, y - 8, 36, 16), path(`M${x - 10},${y - 15} a14,14 0 0 1 20,0`, { width: 1.3, arrow: 'both' }), line(x - 12, y + 8, x - 12, y + 16, { width: 1.5 }), line(x + 12, y + 8, x + 12, y + 16, { width: 1.5 })], 'vane or rack type'),
], { cols: 4 }, 'Piston drawn where it sits at rest; rod leaves on the rod-end side.')

// ---------- Hydraulic sheet 4: directional valves and centre conditions ----------
sheetFig('drawings/hyd-dcv-sheet.svg', 'ISO 1219 directional control valves by ports and positions: 2/2, 3/2, 4/2 and the 4/3 centre conditions closed, open, tandem, float and regenerative', 'Directional valves and centres', [
  cell('2/2 normally closed', (x, y) => [...S.dcv(x, y, { positions: ['blocked', 'pass'], ports: 2, w: 30, h: 26, rest: 0 })], 'solenoid opens it'),
  cell('2/2 normally open', (x, y) => [...S.dcv(x, y, { positions: ['pass', 'blocked'], ports: 2, w: 30, h: 26, rest: 0 })], 'solenoid closes it'),
  cell('3/2', (x, y) => [...S.dcv(x, y, { positions: ['exhaust', 'pass'], ports: 3, w: 30, h: 26, rest: 0 })], '2 to tank at rest'),
  cell('4/2', (x, y) => [...S.dcv(x, y, { positions: ['cross', 'parallel'], ports: 4, w: 32, h: 28, rest: 0 })], 'two positions, no centre'),
  cell('4/3 closed centre', (x, y) => [...S.dcv(x, y, { positions: ['parallel', 'closed', 'cross'], w: 30, h: 28 })], 'all ports blocked'),
  cell('4/3 open centre', (x, y) => [...S.dcv(x, y, { positions: ['parallel', 'open', 'cross'], w: 30, h: 28 })], 'all ports to tank'),
  cell('4/3 tandem centre', (x, y) => [...S.dcv(x, y, { positions: ['parallel', 'tandem', 'cross'], w: 30, h: 28 })], 'P to T, A and B held'),
  cell('4/3 float centre', (x, y) => [...S.dcv(x, y, { positions: ['parallel', 'float', 'cross'], w: 30, h: 28 })], 'A and B to T, P blocked'),
  cell('4/3 regenerative', (x, y) => [...S.dcv(x, y, { positions: ['parallel', 'regen', 'cross'], w: 30, h: 28 })], 'P to A and B, T blocked'),
], { cols: 3, cellW: 158, cellH: 104, symH: 56 }, 'Ports sit on the rest box; slide the other boxes over to read states.')

// ---------- Hydraulic sheet 5: operators ----------
sheetFig('drawings/hyd-operators-sheet.svg', 'ISO 1219 valve operators: solenoid, proportional solenoid, spring, lever, push button, pedal, roller, pilot pressure, detent, manual override, two-stage pilot', 'Valve operators', [
  cell('solenoid', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('solenoid', x - 12, y, 'left')], 'diagonal in a box'),
  cell('proportional solenoid', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('proportional', x - 12, y, 'left')], 'arrow: variable pull'),
  cell('spring return', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('spring', x + 12, y, 'right')], 'zigzag pushes back'),
  cell('lever', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('lever', x - 12, y, 'left')], 'hand lever'),
  cell('push button', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('pushbutton', x - 12, y, 'left')], ''),
  cell('pedal', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('pedal', x - 12, y, 'left')], 'foot'),
  cell('roller / cam', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('roller', x - 12, y, 'left')], 'mechanical limit'),
  cell('pilot pressure', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('pilot', x - 12, y, 'left')], 'dashed line pushes'),
  cell('detent', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('detent', x + 12, y, 'right')], 'stays put'),
  cell('manual override', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('override', x - 12, y, 'left')], 'pin in the solenoid'),
  cell('solenoid, pilot-operated', (x, y) => [rect(x - 8, y - 14, 24, 28), ...S.operator('solenoid', x - 32, y, 'left'), rect(x - 32, y - 10, 12, 20, { fill: C.paper }), ...S.operator('pilot', x - 8, y, 'left')], 'two-stage valve'),
  cell('double pilot', (x, y) => [rect(x - 12, y - 14, 24, 28), ...S.operator('pilot', x - 12, y, 'left'), ...S.operator('pilot', x + 12, y, 'right')], 'pressure both sides'),
], { cols: 4, cellH: 100 }, 'The operator that wins at rest (usually the spring) sets the drawn box.')

// ---------- Hydraulic sheet 6: check and shuttle valves ----------
sheetFig('drawings/hyd-check-valves-sheet.svg', 'ISO 1219 check valves: plain, spring-loaded with cracking pressure, pilot-operated to open and to close, shuttle valve, restrictor check', 'Check and shuttle valves', [
  cell('check valve', (x, y) => [vline(x, y - 24, y - 8), ...S.check(x, y), vline(x, y + 8, y + 24)], 'free flow up, blocks down'),
  cell('spring check', (x, y) => [vline(x, y - 24, y - 8), ...S.check(x, y, { spring: true }), vline(x, y + 8, y + 24)], 'cracking pressure'),
  cell('pilot-operated (to open)', (x, y) => [vline(x, y - 26, y - 12), ...S.check(x, y, { pilot: 'open' }), vline(x, y + 12, y + 26)], 'pilot pressure unseats it'),
  cell('pilot-operated (to close)', (x, y) => [vline(x, y - 26, y - 12), ...S.check(x, y, { pilot: 'close' }), vline(x, y + 12, y + 26), path(`M${x - 12},${y - 12} l-4,-4`, { width: 0 })], 'pilot holds it shut'),
  cell('shuttle valve', (x, y) => [...S.shuttle(x, y + 4)], 'higher pressure wins'),
  cell('restrictor check', (x, y) => [vline(x, y - 30, y - 22), ...S.flowControl(x, y, { bypass: true }), vline(x, y + 22, y + 30)], 'free one way, metered the other'),
], { cols: 3, cellW: 158, cellH: 100, symH: 58 }, 'Flow that lifts the ball off the seat passes; flow onto it is blocked.')

// ---------- Hydraulic sheet 7: pressure valves ----------
sheetFig('drawings/hyd-pressure-valves-sheet.svg', 'ISO 1219 pressure valves: direct relief, pilot-operated relief with vent, reducing, sequence, counterbalance and unloading, and how the arrow and pilot line tell them apart', 'Pressure control valves', [
  cell('relief (direct)', (x, y) => [vline(x, y - 34, y - 23), ...S.pressureValve(x, y, 'relief'), vline(x, y + 23, y + 30), ...S.tank(x, y + 30, { w: 12, h: 7, stub: 0 })], 'in below, tank above'),
  cell('relief, vented', (x, y) => [vline(x, y - 34, y - 23), ...S.pressureValve(x, y, 'relief', { vent: true }), vline(x, y + 23, y + 30), ...S.tank(x, y + 30, { w: 12, h: 7, stub: 0 })], 'vent port unloads it'),
  cell('reducing', (x, y) => [vline(x, y - 34, y - 21), ...S.pressureValve(x, y, 'reducing'), vline(x, y + 15, y + 34)], 'open at rest, senses out'),
  cell('sequence', (x, y) => [vline(x, y - 34, y - 23), ...S.pressureValve(x, y, 'sequence'), vline(x, y + 23, y + 34)], 'closed until set pressure'),
  cell('counterbalance', (x, y) => [vline(x, y - 34, y - 23), ...S.pressureValve(x, y, 'counterbalance'), vline(x, y + 23, y + 34)], 'external pilot, holds a load'),
  cell('unloading', (x, y) => [vline(x, y - 34, y - 23), ...S.pressureValve(x, y, 'unloading'), vline(x, y + 23, y + 30), ...S.tank(x, y + 30, { w: 12, h: 7, stub: 0 })], 'remote pilot dumps pump'),
], { cols: 3, cellW: 158, cellH: 120, symH: 78 }, 'Arrow offset = normally closed, arrow through = normally open.')

// ---------- Hydraulic sheet 8: flow valves ----------
sheetFig('drawings/hyd-flow-valves-sheet.svg', 'ISO 1219 flow control: fixed orifice, adjustable, pressure-compensated, temperature-compensated, with reverse-flow check, flow divider', 'Flow control valves', [
  cell('fixed orifice', (x, y) => [vline(x, y - 26, y - 8), ...S.orifice(x, y), vline(x, y + 8, y + 26)], 'hourglass'),
  cell('adjustable', (x, y) => [vline(x, y - 26, y - 8), ...S.flowControl(x, y), vline(x, y + 8, y + 26)], 'needle valve'),
  cell('pressure-compensated', (x, y) => [vline(x, y - 30, y - 16), ...S.flowControl(x, y, { compensated: true }), vline(x, y + 16, y + 30)], 'flow steady as load changes'),
  cell('temperature-compensated', (x, y) => [vline(x, y - 30, y - 16), ...S.flowControl(x, y, { compensated: true, tempComp: true }), vline(x, y + 16, y + 30)], 'thermometer mark'),
  cell('with bypass check', (x, y) => [vline(x, y - 32, y - 22), ...S.flowControl(x, y, { bypass: true }), vline(x, y + 22, y + 32)], 'metered one way'),
  cell('flow divider', (x, y) => [rect(x - 24, y - 12, 48, 24), vline(x, y - 24, y - 12), ...S.orifice(x - 12, y).map((s) => s), ...S.orifice(x + 12, y), vline(x - 12, y + 12, y + 24), vline(x + 12, y + 12, y + 24)], 'splits flow in ratio'),
], { cols: 3, cellW: 158, cellH: 108, symH: 66 }, 'Diagonal arrow = adjustable; boxed orifice = pressure-compensated.')

// ---------- Hydraulic sheet 9: conditioning ----------
sheetFig('drawings/hyd-conditioning-sheet.svg', 'ISO 1219 conditioning: gas, spring and weighted accumulators, filters with bypass and clogging indicator, water separator, cooler, heater, temperature controller, breather', 'Accumulators, filters, coolers', [
  cell('gas accumulator', (x, y) => [...S.accumulator(x, y - 6, 'gas')], 'bladder or piston'),
  cell('spring accumulator', (x, y) => [...S.accumulator(x, y - 6, 'spring')], ''),
  cell('weighted accumulator', (x, y) => [...S.accumulator(x, y - 6, 'weight')], ''),
  cell('filter', (x, y) => [vline(x, y - 26, y - 14), ...S.filter(x, y), vline(x, y + 14, y + 26)], 'dashed line = element'),
  cell('filter + bypass', (x, y) => [vline(x, y - 30, y - 22), ...S.filter(x, y, { bypass: true, indicator: true }), vline(x, y + 22, y + 30)], 'check opens when blocked'),
  cell('water separator', (x, y) => [vline(x, y - 26, y - 14), ...S.filter(x, y, { water: true }), vline(x, y + 14, y + 26), line(x, y + 14, x, y + 22, { width: 0 })], 'drop = drain'),
  cell('cooler', (x, y) => [vline(x, y - 26, y - 14), ...S.cooler(x, y), vline(x, y + 14, y + 26)], 'arrows out = heat out'),
  cell('heater', (x, y) => [vline(x, y - 26, y - 14), ...S.heater(x, y), vline(x, y + 14, y + 26)], 'arrows in = heat in'),
  cell('temp. controller', (x, y) => [vline(x, y - 26, y - 14), poly([[x, y - 14], [x + 14, y], [x, y + 14], [x - 14, y]], { width: 1.5 }), line(x - 6, y - 4, x - 6, y + 4, { width: 1.3, arrow: 'both' }), line(x + 6, y - 4, x + 6, y + 4, { width: 1.3, arrow: 'both' }), vline(x, y + 14, y + 26)], 'heats or cools'),
  cell('breather', (x, y) => [poly([[x, y - 12], [x + 12, y], [x, y + 12], [x - 12, y]], { width: 1.5 }), line(x - 9, y, x + 9, y, { width: 1.2, dash: '3 2' }), vline(x, y + 12, y + 24), text(x, y - 16, 'air', { size: 8, anchor: 'middle' })], 'on the reservoir'),
], { cols: 4 }, 'A check beside a filter is the bypass: dirty oil passes when blocked.')

// ---------- Hydraulic sheet 10: instruments and connections ----------
sheetFig('drawings/hyd-instruments-sheet.svg', 'ISO 1219 instruments and connections: pressure and temperature gauges, flow meter, pressure switch, level and temperature switches, transducer, quick disconnects, rotary joint, test point, manifold and cartridge envelope', 'Gauges, switches and connections', [
  cell('pressure gauge', (x, y) => [...S.gaugeP(x, y), vline(x, y + 10, y + 22)], 'needle in a circle'),
  cell('temperature gauge', (x, y) => [...S.gaugeT(x, y), vline(x, y + 10, y + 22)], 'thermometer in a circle'),
  cell('flow meter', (x, y) => [S.fl(x - 26, y, x - 10, y), ...S.flowMeter(x, y), S.fl(x + 10, y, x + 26, y)], 'arrow in a circle'),
  cell('pressure switch', (x, y) => [...S.pressureSwitch(x + 6, y)], 'contact in a box'),
  cell('level switch', (x, y) => [rect(x - 12, y - 10, 24, 20), line(x - 8, y + 4, x + 4, y - 4, { width: 1.5 }), circle(x + 6, y - 4, 1.8, { fill: C.ink }), line(x + 6, y - 4, x + 12, y - 4, { width: 1.2 }), circle(x - 16, y + 10, 4), line(x - 16, y + 6, x - 16, y, { width: 1 })], 'float actuates it'),
  cell('temperature switch', (x, y) => [rect(x - 12, y - 10, 24, 20), line(x - 8, y + 4, x + 4, y - 4, { width: 1.5 }), circle(x + 6, y - 4, 1.8, { fill: C.ink }), line(x + 6, y - 4, x + 12, y - 4, { width: 1.2 }), line(x - 16, y + 10, x - 16, y - 4, { width: 1.2 }), circle(x - 16, y + 10, 2.5, { fill: C.ink })], 'thermometer actuates it'),
  cell('pressure transducer', (x, y) => [circle(x, y, 10), text(x, y + 3.5, 'P', { size: 9, anchor: 'middle', weight: 700 }), vline(x, y + 10, y + 22), line(x + 10, y, x + 24, y, { width: 1, dash: '4 2' }), path(`M${x + 24},${y - 4} l0,8`, { width: 1 })], 'electrical output'),
  cell('quick disconnect, coupled', (x, y) => [...S.quickDisconnect(x, y, { coupled: true })], 'with checks both halves'),
  cell('quick disconnect, open', (x, y) => [...S.quickDisconnect(x, y, { coupled: false })], 'checks closed'),
  cell('rotary joint', (x, y) => [...S.rotaryJoint(x, y)], 'swivel'),
  cell('test point', (x, y) => [vline(x, y - 20, y), circle(x, y + 4, 4), line(x - 4, y + 4, x + 4, y + 4, { width: 0 }), path(`M${x + 4},${y + 4} l10,0 m-3,-3 l3,3 l-3,3`, { width: 1 })], 'gauge connection'),
  cell('manifold / cartridge', (x, y) => [rect(x - 26, y - 16, 52, 32, { ...S.LINE.enclosure }), rect(x - 8, y - 8, 16, 16), line(x - 8, y + 8, x + 8, y - 8, { width: 1.2, arrow: 'end' }), vline(x, y - 26, y - 8), vline(x, y + 8, y + 26)], 'chain line = one block'),
], { cols: 4 }, 'A chain-line box is one physical assembly: manifold, unit, cartridge.')

// ---------- Pneumatic sheet 1: air preparation ----------
sheetFig('drawings/pneu-frl-sheet.svg', 'Pneumatic air preparation symbols: filter with manual and automatic drain, regulator with gauge, lubricator, combined FRL, dryer, soft-start dump valve, lockout valve, compressor', 'Air preparation (FRL)', [
  cell('filter, manual drain', (x, y) => [S.fl(x - 26, y - 4, x - 12, y - 4), ...S.airFilter(x, y - 4), S.fl(x + 12, y - 4, x + 26, y - 4)], 'diamond, drain below'),
  cell('filter, auto drain', (x, y) => [S.fl(x - 26, y - 4, x - 12, y - 4), ...S.airFilter(x, y - 4, { autoDrain: true }), S.fl(x + 12, y - 4, x + 26, y - 4)], 'box on the drain'),
  cell('regulator with gauge', (x, y) => [S.fl(x - 28, y, x - 12, y), ...S.regulator(x, y), S.fl(x + 12, y, x + 28, y)], 'arrow, spring, pilot'),
  cell('lubricator', (x, y) => [S.fl(x - 26, y, x - 12, y), ...S.lubricator(x, y), S.fl(x + 12, y, x + 26, y)], 'drop in the diamond'),
  cell('FRL, simplified', (x, y) => [...S.frlSimple(x, y)], 'one dashed box'),
  cell('air dryer', (x, y) => [S.fl(x - 26, y, x - 12, y), poly([[x, y - 12], [x + 12, y], [x, y + 12], [x - 12, y]], { width: 1.5 }), ...[-4, 0, 4].map((d) => circle(x + d, y + d * 0.5, 1.4, { fill: C.ink, stroke: 'none' })), S.fl(x + 12, y, x + 26, y)], 'dots = desiccant'),
  cell('soft-start / dump', (x, y) => [...S.dcv(x, y, { positions: ['exhaust', 'pass'], ports: 3, w: 26, h: 24, rest: 0, labels: false }), ...S.exhaust(x - 20, y + 14)], 'exhausts on power loss'),
  cell('lockout valve', (x, y) => [...S.dcv(x, y, { positions: ['exhaust', 'pass'], ports: 3, w: 26, h: 24, rest: 0, left: 'lever', right: 'detent', labels: false }), text(x, y + 26, 'LOTO', { size: 8, anchor: 'middle', weight: 700 })], 'padlockable, vents down'),
  cell('compressor', (x, y) => [circle(x, y, 14), poly([[x, y - 14], [x + 6, y - 3], [x - 6, y - 3]], { fill: C.paper, width: 1.2 }), vline(x, y - 24, y - 14), ...S.electricMotor(x + 24, y + 12, 7)], 'open triangle = air'),
], { cols: 3, cellW: 158, cellH: 104, symH: 60 }, 'Read air prep in the order the air meets it: filter, regulator, lube.')

// ---------- Pneumatic sheet 2: valves ----------
sheetFig('drawings/pneu-valves-sheet.svg', 'Pneumatic valves: 3/2 NC and NO, 5/2 single and double solenoid, 5/3 closed, exhaust and pressure centres, 2/2, exhaust and silencer, quick exhaust, shuttle (OR) and two-pressure (AND)', 'Pneumatic valves', [
  cell('3/2 NC, solenoid/spring', (x, y) => [...S.dcv(x, y, { positions: ['exhaust', 'pass'], ports: 3, w: 30, h: 26, rest: 0 })], 'port 2 exhausted at rest'),
  cell('3/2 NO', (x, y) => [...S.dcv(x, y, { positions: ['pass', 'exhaust'], ports: 3, w: 30, h: 26, rest: 0 })], 'port 2 pressurised at rest'),
  cell('5/2, single solenoid', (x, y) => [...S.dcv(x, y, { positions: ['b', 'a'], ports: 5, w: 34, h: 26, rest: 0 })], 'spring returns it'),
  cell('5/2, double solenoid', (x, y) => [...S.dcv(x, y, { positions: ['b', 'a'], ports: 5, w: 34, h: 26, rest: 0, right: 'solenoid' })], 'memory: stays put'),
  cell('5/3 closed centre', (x, y) => [...S.dcv(x, y, { positions: ['a', 'closed', 'b'], ports: 5, w: 32, h: 26 })], 'holds the cylinder'),
  cell('5/3 exhaust centre', (x, y) => [...S.dcv(x, y, { positions: ['a', 'exhaust', 'b'], ports: 5, w: 32, h: 26 })], 'cylinder goes limp'),
  cell('5/3 pressure centre', (x, y) => [...S.dcv(x, y, { positions: ['a', 'pressure', 'b'], ports: 5, w: 32, h: 26 })], 'both ends pressurised'),
  cell('2/2 NC', (x, y) => [...S.dcv(x, y, { positions: ['blocked', 'pass'], ports: 2, w: 30, h: 26, rest: 0 })], 'on-off'),
  cell('exhaust / silencer', (x, y) => [vline(x - 20, y - 14, y - 2), ...S.exhaust(x - 20, y - 2), vline(x + 16, y - 14, y - 2), ...S.exhaust(x + 16, y - 2, { silencer: true })], 'triangle out to air'),
  cell('quick exhaust', (x, y) => [...S.quickExhaust(x, y - 4)], 'dumps at the cylinder'),
  cell('shuttle (OR)', (x, y) => [...S.shuttle(x, y + 4)], 'either input passes'),
  cell('two-pressure (AND)', (x, y) => [rect(x - 18, y - 8, 36, 16), line(x - 24, y, x - 18, y, { width: 1.5 }), line(x + 18, y, x + 24, y, { width: 1.5 }), line(x, y - 8, x, y - 16, { width: 1.5 }), path(`M${x - 8},${y - 8} l0,16 M${x + 8},${y - 8} l0,16`, { width: 1.2 }), circle(x, y, 3, { fill: C.ink })], 'both inputs needed'),
], { cols: 3, cellW: 158, cellH: 104, symH: 58 }, 'Ports: 1 supply, 2 and 4 outlets, 3 and 5 exhausts, 12/14 pilots.')

// ---------- Pneumatic sheet 3: actuators and controls ----------
sheetFig('drawings/pneu-actuators-sheet.svg', 'Pneumatic actuators and controls: single- and double-acting cylinders, cushioned, rodless, rotary actuator, air motor, gripper, vacuum generator and cup, vacuum switch, meter-out flow control, pressure switch', 'Pneumatic actuators and controls', [
  cell('single-acting, spring', (x, y) => [...S.cylinder(x - 8, y, { single: true, spring: true, w: 54 })], 'one air line'),
  cell('double-acting', (x, y) => [...S.cylinder(x - 8, y, { w: 54 })], 'two air lines'),
  cell('cushioned both ends', (x, y) => [...S.cylinder(x - 8, y, { cushion: true, w: 58 })], 'adjustable'),
  cell('rodless', (x, y) => [rect(x - 28, y - 9, 56, 18), rect(x - 6, y - 9, 12, 18, { fill: C.ink }), rect(x - 8, y - 16, 16, 7, { fill: C.paper })], 'carriage on the barrel'),
  cell('rotary actuator', (x, y) => [rect(x - 16, y - 9, 32, 18), path(`M${x - 8},${y - 16} a12,12 0 0 1 16,0`, { width: 1.3, arrow: 'both' })], '90 or 180 degrees'),
  cell('air motor', (x, y) => [...S.hmotor(x, y, { pneumatic: true, r: 14 })], 'open triangle in'),
  cell('gripper', (x, y) => [rect(x - 14, y - 12, 28, 14), path(`M${x - 10},${y + 2} l0,10 l6,0 M${x + 10},${y + 2} l0,10 l-6,0`, { width: 1.6 })], 'parallel jaws'),
  cell('vacuum generator', (x, y) => [...S.vacuumGen(x, y)], 'ejector, exhaust up'),
  cell('vacuum cup', (x, y) => [...S.vacuumCup(x, y + 4)], 'suction pad'),
  cell('vacuum switch', (x, y) => [rect(x - 12, y - 10, 24, 20), line(x - 8, y + 4, x + 4, y - 4, { width: 1.5 }), circle(x + 6, y - 4, 1.8, { fill: C.ink }), line(x + 6, y - 4, x + 12, y - 4, { width: 1.2 }), line(x - 12, y, x - 22, y, { width: 1.5 }), text(x - 26, y + 3, '-p', { size: 7.5, anchor: 'end' })], 'closes on vacuum'),
  cell('flow control, meter-out', (x, y) => [S.fl(x - 30, y, x - 22, y), ...S.flowControl(x, y, { bypass: true, vertical: false }), S.fl(x + 22, y, x + 30, y)], 'free in, metered out'),
  cell('pressure switch', (x, y) => [...S.pressureSwitch(x + 6, y)], 'confirms clamp pressure'),
], { cols: 4 }, 'Meter-out is the rule for cylinders: the piston stays loaded, no lunge.')

// ================= Circuit diagrams =================
const src = (x, y) => [...S.pump(x, y, { r: 13 }), ...S.electricMotor(x - 30, y, 8), line(x - 22, y, x - 13, y, { width: 2 }), vline(x, y + 13, y + 24), ...S.tank(x, y + 24, { w: 16, h: 9, stub: 0 })]
const reliefToTank = (x, y) => [...S.pressureValve(x, y, 'relief', { size: 22 }), vline(x, y + 17, y + 26), ...S.tank(x, y + 26, { w: 14, h: 8, stub: 0 })]

// ---------- Open vs closed centre ----------
fig('drawings/circuit-open-vs-closed-centre.svg', 'Open-centre circuit with a fixed pump: at idle the pump flow returns to tank through the valve and the gauge reads near zero. Closed-centre with a pressure-compensated pump: at idle the pump de-strokes and the gauge holds the compensator setting',
  svg(500, 300, [
    text(125, 20, 'Open centre, fixed pump', { anchor: 'middle', weight: 700, size: 12 }), text(375, 20, 'Closed centre, compensated pump', { anchor: 'middle', weight: 700, size: 12 }),
    ...[[60, false], [310, true]].map(([x0, comp]) => [
      ...src(x0 + 30, 220), vline(x0 + 30, 207, 150), ...(comp ? [line(x0 + 30 + 18, 205, x0 + 30 + 18, 205, { width: 0 }), ...S.pump(x0 + 30, 220, { r: 13, variable: true, comp: true })] : []),
      ...S.gaugeP(x0 - 4, 176, { r: 9 }), line(x0 + 5, 176, x0 + 30, 176, { width: 1.2 }), S.junction(x0 + 30, 176),
      line(x0 + 30, 150, x0 + 30, 140, { width: 1.6 }), ...reliefToTank(x0 + 100, 176), line(x0 + 30, 160, x0 + 100, 160, { width: 1.6 }), vline(x0 + 100, 160, 165), S.junction(x0 + 30, 160),
      ...S.dcv(x0 + 96, 108, { positions: comp ? ['parallel', 'closed', 'cross'] : ['parallel', 'open', 'cross'], w: 30, h: 28, left: 'lever', right: 'spring', labels: false }),
      line(x0 + 30, 140, x0 + 30, 132, { width: 1.6 }), line(x0 + 30, 132, x0 + 104, 132, { width: 1.6 }), vline(x0 + 104, 132, 130),
      vline(x0 + 118, 130, 140), line(x0 + 118, 140, x0 + 150, 140, { width: 1.6 }), vline(x0 + 150, 140, 150), ...S.tank(x0 + 150, 150, { w: 14, h: 8, stub: 0 }),
      vline(x0 + 104, 86, 60), vline(x0 + 118, 86, 60), ...S.cylinder(x0 + 111, 44, { w: 52, h: 18, rodLen: 18, piston: 0.4 }), line(x0 + 92, 60, x0 + 92, 53, { width: 0 }),
      line(x0 + 104, 60, x0 + 92, 60, { width: 1.6 }), line(x0 + 92, 60, x0 + 92, 53, { width: 1.6 }), line(x0 + 118, 60, x0 + 130, 60, { width: 1.6 }), line(x0 + 130, 60, x0 + 130, 53, { width: 1.6 }),
      text(x0 - 4, 196, 'idle', { size: 9, anchor: 'middle', fill: comp ? C.red : C.green, weight: 600 }), text(x0 - 4, 207, comp ? '2,800 psi' : '~50 psi', { size: 9, anchor: 'middle', fill: comp ? C.red : C.green, weight: 600 }),
    ]),
    note(125, 258, 'pump flow crosses the valve to tank at idle:\ncool, cheap, one actuator at a time', { anchor: 'middle', size: 9.5 }),
    note(375, 258, 'valve blocks P at idle; the pump strokes\nback to zero flow and holds pressure', { anchor: 'middle', size: 9.5 }),
    caption(500, 300, 'Same valve family, opposite idle behaviour: read the centre box first.'),
  ], { title: 'Open vs closed centre' }))

// ---------- Meter-in, meter-out, bleed-off ----------
{
  const mini = (x0, title, place) => {
    const out = [text(x0 + 70, 20, title, { anchor: 'middle', weight: 700, size: 11.5 }),
      ...S.pressureSource(x0 + 40, 190, 8), vline(x0 + 40, 182, 150), line(x0 + 40, 150, x0 + 62, 150, { width: 1.6 }), vline(x0 + 62, 150, 140),
      ...S.dcv(x0 + 70, 118, { positions: ['parallel', 'cross'], w: 30, h: 28, left: 'solenoid', right: 'spring', labels: false, rest: 0 }),
      vline(x0 + 78, 140, 150), line(x0 + 78, 150, x0 + 100, 150, { width: 1.6 }), vline(x0 + 100, 150, 170), ...S.tank(x0 + 100, 170, { w: 14, h: 8, stub: 0 }),
      ...S.cylinder(x0 + 70, 48, { w: 52, h: 18, rodLen: 16, piston: 0.4 })]
    // A line: x0+62 up to cap end (left), B line: x0+78 up to rod end (right)
    const capX = x0 + 50, rodX = x0 + 90
    out.push(line(x0 + 62, 96, x0 + 62, 88, { width: 1.6 }), line(x0 + 62, 88, capX, 88, { width: 1.6 }), line(x0 + 78, 96, x0 + 78, 88, { width: 1.6 }), line(x0 + 78, 88, rodX, 88, { width: 1.6 }))
    if (place === 'in') out.push(line(capX, 88, capX, 78, { width: 1.6 }), ...S.flowControl(capX, 72, { bypass: true }).map((s) => s), line(capX, 60, capX, 57, { width: 1.6 }), line(rodX, 88, rodX, 57, { width: 1.6 }))
    else if (place === 'out') out.push(line(rodX, 88, rodX, 78, { width: 1.6 }), ...S.flowControl(rodX, 72, { bypass: true }), line(rodX, 60, rodX, 57, { width: 1.6 }), line(capX, 88, capX, 57, { width: 1.6 }))
    else out.push(line(capX, 88, capX, 57, { width: 1.6 }), line(rodX, 88, rodX, 57, { width: 1.6 }), line(x0 + 40, 165, x0 + 14, 165, { width: 1.6 }), S.junction(x0 + 40, 165), ...S.flowControl(x0 + 14, 165, { vertical: false }).map((s) => s), line(x0 + 14, 165, x0 + 14, 185, { width: 0 }), vline(x0 + 14, 173, 186), ...S.tank(x0 + 14, 186, { w: 12, h: 7, stub: 0 }))
    return out
  }
  fig('drawings/circuit-meter-in-out.svg', 'Where the flow control sits changes what it does: meter-in restricts the oil going to the cylinder, meter-out restricts the oil leaving it and holds an overrunning load, bleed-off sends part of the pump flow to tank',
    svg(500, 262, [
      ...mini(10, 'Meter-in', 'in'), ...mini(180, 'Meter-out', 'out'), ...mini(350, 'Bleed-off', 'bleed'),
      note(80, 220, 'controls speed into the\ncylinder; load can run away', { anchor: 'middle', size: 9 }), note(250, 220, 'back-pressure holds the load;\nthe usual choice', { anchor: 'middle', size: 9 }), note(420, 220, 'pump works at load pressure,\nless heat; not for overrunning', { anchor: 'middle', size: 9 }),
      caption(500, 262, 'Dashed box with a check = restrictor check: metered one way, free back.'),
    ], { title: 'Meter-in, meter-out, bleed-off' }))
}

// ---------- Regenerative circuit ----------
fig('drawings/circuit-regenerative.svg', 'Regenerative extend: the 4/3 regenerative centre joins the rod-end oil to the cap end, so the cylinder extends fast on the annulus difference; force drops to the rod-area force until the valve shifts to normal extend',
  svg(500, 250, [
    ...src(60, 190), vline(60, 177, 150), line(60, 150, 150, 150, { width: 1.6 }), vline(150, 150, 134), ...reliefToTank(110, 200), line(60, 200, 99, 200, { width: 0 }), S.junction(60, 160), line(60, 160, 110, 160, { width: 1.6 }), vline(110, 160, 189),
    ...S.dcv(158, 112, { positions: ['parallel', 'regen', 'cross'], w: 34, h: 30, left: 'solenoid', right: 'solenoid', labels: true }),
    vline(160, 137, 150), line(160, 150, 200, 150, { width: 1.6 }), vline(200, 150, 170), ...S.tank(200, 170, { w: 14, h: 8, stub: 0 }),
    vline(149, 87, 60), vline(167, 87, 60), line(149, 60, 120, 60, { width: 1.6 }), line(120, 60, 120, 46, { width: 1.6 }), line(167, 60, 214, 60, { width: 1.6 }), line(214, 60, 214, 46, { width: 1.6 }),
    ...S.cylinder(168, 36, { w: 96, h: 22, rodLen: 30, piston: 0.35 }),
    line(140, 36, 200, 36, { width: 2, stroke: C.red, arrow: 'end' }), text(300, 40, 'fast extend', { size: 10, fill: C.red, weight: 600 }),
    line(214, 58, 190, 88, { width: 1.5, stroke: C.blue, arrow: 'end', dash: '3 2' }), text(226, 80, 'rod-end oil rejoins the pump flow', { size: 9, fill: C.blue }),
    table(268, 100, [['Extend', 'Speed', 'Force'], ['regen', 'Q ÷ rod area', 'p × rod area'], ['normal', 'Q ÷ cap area', 'p × cap area']], [50, 78, 78], { rowH: 20, size: 9.5 }),
    note(388, 176, 'a 2:1 cylinder doubles its speed and\nhalves its force in regen', { anchor: 'middle', size: 9.5 }),
    caption(500, 250, 'Regen is for the rapid approach; the press stroke shifts to full cap area.'),
  ], { title: 'Regenerative circuit' }))

// ---------- Sequence and counterbalance ----------
fig('drawings/circuit-sequence-counterbalance.svg', 'Sequence valve: the press cylinder cannot move until the clamp cylinder has built pressure. Counterbalance valve: the vertical load is held and lowered under control, opened by pilot pressure from the other side of the cylinder',
  svg(500, 290, [
    text(125, 20, 'Sequence: clamp, then press', { anchor: 'middle', weight: 700, size: 11.5 }), text(375, 20, 'Counterbalance, vertical load', { anchor: 'middle', weight: 700, size: 11.5 }),
    // sequence circuit
    ...S.pressureSource(40, 200, 8), vline(40, 192, 160), line(40, 160, 120, 160, { width: 1.6 }), S.junction(40, 160), vline(40, 160, 140), line(40, 140, 54, 140, { width: 1.6 }),
    ...S.dcv(62, 120, { positions: ['parallel', 'cross'], w: 30, h: 26, left: 'solenoid', right: 'spring', labels: false, rest: 0 }), vline(70, 133, 150), line(70, 150, 100, 150, { width: 1.6 }), vline(100, 150, 176), ...S.tank(100, 176, { w: 14, h: 8, stub: 0 }),
    vline(55, 107, 70), vline(69, 107, 70), line(55, 70, 46, 70, { width: 1.6 }), line(69, 70, 78, 70, { width: 1.6 }), ...S.cylinder(62, 52, { w: 40, h: 16, rodLen: 14, piston: 0.4 }), text(62, 38, 'clamp', { size: 9, anchor: 'middle' }),
    vline(120, 160, 150), ...S.pressureValve(120, 130, 'sequence', { size: 24 }), vline(120, 112, 100), line(120, 100, 150, 100, { width: 1.6 }), vline(150, 100, 70), line(150, 70, 158, 70, { width: 1.6 }),
    ...S.cylinder(174, 52, { w: 40, h: 16, rodLen: 14, piston: 0.4 }), text(174, 38, 'press', { size: 9, anchor: 'middle' }), line(190, 70, 200, 70, { width: 1.6 }), vline(200, 70, 180), ...S.tank(200, 180, { w: 14, h: 8, stub: 0 }),
    note(125, 236, 'sequence valve set above clamp pressure:\npress oil waits until the clamp is tight', { anchor: 'middle', size: 9.5 }),
    // counterbalance circuit (vertical cylinder, rod down, load hanging on the rod end)
    ...S.pressureSource(300, 216, 8), line(300, 208, 340, 208, { width: 1.6 }), vline(340, 208, 182),
    ...S.dcv(348, 160, { positions: ['parallel', 'closed', 'cross'], w: 30, h: 26, left: 'solenoid', right: 'solenoid', labels: false }), vline(356, 173, 208), line(356, 208, 380, 208, { width: 1.6 }), vline(380, 208, 226), ...S.tank(380, 226, { w: 14, h: 8, stub: 0 }),
    // A port to the cap end (top of the cylinder); B port through the counterbalance valve to the rod end
    vline(341, 147, 40), line(341, 40, 478, 40, { width: 1.6 }), vline(478, 40, 46), S.junction(390, 40),
    vline(355, 147, 118), line(355, 118, 405, 118, { width: 1.6 }), vline(405, 118, 108), S.junction(405, 118),
    ...S.pressureValve(405, 96, 'counterbalance', { size: 22 }), vline(405, 85, 70), line(405, 70, 458, 70, { width: 1.6 }), vline(458, 70, 96), line(458, 96, 470, 96, { width: 1.6 }), S.junction(440, 70),
    // bypass check beside the valve: free flow toward the rod end when raising
    line(405, 118, 440, 118, { width: 1.6 }), vline(440, 118, 104), ...S.check(440, 97, { dir: 'up', size: 6 }), vline(440, 90, 70),
    g([...S.cylinder(0, 0, { w: 56, h: 16, rodLen: 20, piston: 0.6 })], { transform: 'translate(478 74) rotate(90)' }),
    rect(468, 104, 20, 14, { fill: C.steelDark }), text(478, 114, 'load', { size: 8.5, anchor: 'middle', fill: C.paper }),
    S.fl(390, 40, 390, 60, 'pilot'), S.fl(390, 60, 378, 60, 'pilot'), S.fl(378, 60, 378, 96, 'pilot'), S.fl(378, 96, 394, 96, 'pilot'), text(334, 64, 'pilot from the\ncap-end line', { size: 8.5, anchor: 'end' }),
    text(334, 108, 'valve in the rod-end\nline holds the load', { size: 8.5, anchor: 'end' }),
    note(375, 250, 'the valve holds the load until the cap side\nis pressurised, then opens in proportion', { anchor: 'middle', size: 9.5 }),
    caption(500, 290, 'Both valves are closed at rest: the arrow is offset from the ports.'),
  ], { title: 'Sequence and counterbalance' }))

// ---------- Accumulator and hi-lo ----------
fig('drawings/circuit-accumulator-hilo.svg', 'Accumulator circuit: pump charges through a check, isolation and bleed-down valves let it be worked on safely; hi-lo circuit: a large pump unloads at low pressure while the small pump finishes the stroke at high pressure',
  svg(500, 290, [
    text(125, 20, 'Accumulator circuit', { anchor: 'middle', weight: 700, size: 11.5 }), text(375, 20, 'Hi-lo two-pump circuit', { anchor: 'middle', weight: 700, size: 11.5 }),
    ...src(60, 214), vline(60, 201, 170), ...S.check(60, 160, { dir: 'up', size: 7 }), vline(60, 152, 110), S.junction(60, 130),
    line(60, 130, 130, 130, { width: 1.6 }), ...S.dcv(140, 130, { positions: ['blocked', 'pass'], ports: 2, w: 22, h: 22, left: 'lever', right: 'detent', labels: false, rest: 0 }).map((s) => s),
    line(140, 119, 140, 100, { width: 1.6 }), ...S.accumulator(140, 74, 'gas'), text(166, 86, 'isolate', { size: 8.5 }), text(166, 120, 'bleed-down', { size: 8.5 }),
    line(140, 141, 140, 160, { width: 1.6 }), ...S.flowControl(140, 172), vline(140, 184, 200), ...S.tank(140, 200, { w: 14, h: 8, stub: 0 }),
    ...S.gaugeP(96, 100, { r: 8 }), line(96, 108, 96, 130, { width: 1 }), line(60, 110, 60, 60, { width: 1.6, arrow: 'end' }), text(64, 56, 'to system', { size: 9 }),
    ...reliefToTank(20, 170), line(60, 140, 20, 140, { width: 1.6 }), line(20, 140, 20, 159, { width: 1.6 }), S.junction(60, 140),
    note(125, 264, 'bleed to zero on the gauge before opening', { anchor: 'middle', size: 9.5 }),
    // hi-lo
    ...S.electricMotor(300, 220, 9), line(309, 220, 320, 220, { width: 2 }), ...S.pump(334, 220, { r: 13 }), line(347, 220, 356, 220, { width: 2 }), ...S.pump(370, 220, { r: 10 }),
    vline(334, 233, 244), ...S.tank(334, 244, { w: 14, h: 8, stub: 0 }), vline(370, 230, 244), ...S.tank(370, 244, { w: 12, h: 7, stub: 0 }), text(334, 264, 'high volume', { size: 8.5, anchor: 'middle' }), text(384, 236, 'high pressure', { size: 8.5 }),
    vline(334, 207, 176), ...S.check(334, 166, { dir: 'up', size: 6 }), vline(334, 160, 120), vline(370, 210, 120), line(334, 120, 370, 120, { width: 1.6 }), S.junction(370, 120), line(370, 120, 370, 70, { width: 1.6, arrow: 'end' }), text(376, 66, 'to system', { size: 9 }),
    ...S.pressureValve(300, 176, 'unloading', { size: 22 }), line(334, 190, 300, 190, { width: 1.6 }), S.junction(334, 190), vline(300, 190, 187), vline(300, 165, 152), ...S.tank(300, 152, { w: 12, h: 7, stub: 0 }).map((s) => s.replace('', '')),
    S.fl(300, 176, 262, 176, 'pilot'), S.fl(262, 176, 262, 96, 'pilot'), S.fl(262, 96, 370, 96, 'pilot'), S.junction(370, 96),
    ...S.pressureValve(420, 150, 'relief', { size: 22 }), line(370, 140, 420, 140, { width: 1.6 }), S.junction(370, 140), vline(420, 140, 161), vline(420, 139, 128), ...S.tank(420, 128, { w: 12, h: 7, stub: 0 }),
    text(440, 176, 'relief', { size: 8.5 }), text(256, 148, 'unloading valve:\ndumps the big pump\nabove its setting', { size: 8.5, anchor: 'end' }),
    caption(500, 290, 'Hi-lo: fast approach on both pumps, full pressure on the small one alone.'),
  ], { title: 'Accumulator and hi-lo circuits' }))

// ---------- Test points ----------
fig('drawings/circuit-test-points.svg', 'Where to put test gauges on a circuit: pump outlet, after the reducing valve, at each actuator port and on the case drain, then compare each reading with the settings table',
  svg(500, 290, [
    ...src(60, 230), vline(60, 217, 170), ...reliefToTank(20, 176), line(60, 176, 20, 176, { width: 0 }), line(60, 186, 20, 186, { width: 1.6 }), vline(20, 186, 165), S.junction(60, 186),
    line(60, 170, 60, 150, { width: 1.6 }), line(60, 150, 140, 150, { width: 1.6 }), vline(140, 150, 134),
    ...S.dcv(148, 112, { positions: ['parallel', 'closed', 'cross'], w: 30, h: 26, left: 'solenoid', right: 'solenoid', labels: false }),
    vline(155, 125, 150), line(155, 150, 200, 150, { width: 1.6 }), vline(200, 150, 176), ...S.tank(200, 176, { w: 14, h: 8, stub: 0 }),
    vline(141, 99, 60), vline(155, 99, 80), ...S.pressureValve(190, 80, 'reducing', { size: 22 }), line(155, 80, 179, 80, { width: 0 }), line(155, 80, 190, 80, { width: 1.6 }), vline(190, 80, 69),
    line(190, 91, 190, 100, { width: 0 }), line(190, 69, 190, 60, { width: 0 }), line(190, 60, 220, 60, { width: 1.6 }), line(141, 60, 120, 60, { width: 1.6 }), line(120, 60, 120, 50, { width: 1.6 }), line(220, 60, 220, 50, { width: 1.6 }),
    ...S.cylinder(170, 40, { w: 104, h: 20, rodLen: 28, piston: 0.4 }),
    ...[[60, 160, 'G1', 'pump outlet'], [200, 100, 'G2', 'after reducer'], [120, 60, 'G3', 'cap end'], [220, 60, 'G4', 'rod end'], [50, 250, 'G5', 'case drain']].map(([x, y, g, l]) => [circle(x + 14, y - 10, 8, { fill: C.soft, stroke: C.accentDark }), text(x + 14, y - 6.5, g, { size: 8, anchor: 'middle', weight: 700, fill: C.accentDark }), line(x, y, x + 8, y - 6, { width: 1, stroke: C.accentDark })]),
    S.fl(52, 240, 52, 262, 'drain'), ...S.tank(52, 262, { w: 12, h: 7, stub: 0 }),
    table(290, 40, [['Gauge', 'Should read', 'If not'], ['G1 idle', 'relief 2,000', 'relief, pump'], ['G1 load', 'holds 2,000', 'pump worn'], ['G2', 'reducer 800', 'reducer, drain'], ['G3 extend', 'load pressure', 'bypass, load'], ['G4 hold', 'near 0', 'valve leak'], ['G5', 'under 50', 'pump seals']], [56, 76, 76], { rowH: 22, size: 9.2 }),
    note(394, 215, 'write the settings table first;\na gauge without a target is a guess', { anchor: 'middle', size: 9.5 }),
    caption(500, 290, 'Five gauges show which block is wrong before you lift a wrench.'),
  ], { title: 'Test points on a circuit' }))

// ================= Electrical symbol sheets =================
const both = (name, nema, iec, note) => cell(name, (x, y) => [...nema(x - 24, y), ...iec(x + 24, y), text(x - 24, y + 22, 'NEMA', { size: 7, anchor: 'middle', fill: C.muted }), text(x + 24, y + 22, 'IEC', { size: 7, anchor: 'middle', fill: C.muted })], note)

sheetFig('drawings/elec-contacts-coils-sheet.svg', 'Electrical contacts and coils in NEMA/JIC and IEC 60617 form: normally open, normally closed, relay coil, on-delay and off-delay timed contacts, overload contact, and how a relay and its contacts share a name', 'Contacts and coils', [
  both('normally open', (x, y) => S.contactNO(x, y), (x, y) => S.contactNO(x, y, { iec: true }), 'open until the coil pulls'),
  both('normally closed', (x, y) => S.contactNC(x, y), (x, y) => S.contactNC(x, y, { iec: true }), 'closed until the coil pulls'),
  both('coil', (x, y) => S.coil(x, y, 'CR'), (x, y) => S.coil(x, y, 'K1', { iec: true }), 'circle vs rectangle'),
  cell('on-delay NO (TON)', (x, y) => [...S.timedContact(x, y - 4)], 'closes after the delay'),
  cell('on-delay NC (TON)', (x, y) => [...S.timedContact(x, y - 4, { nc: true })], 'opens after the delay'),
  cell('off-delay NO (TOF)', (x, y) => [...S.timedContact(x, y - 4, { delay: 'off' })], 'opens after coil drops'),
  cell('off-delay NC (TOF)', (x, y) => [...S.timedContact(x, y - 4, { nc: true, delay: 'off' })], 'closes after coil drops'),
  cell('overload contact', (x, y) => [...S.overloadContact(x, y - 4)], 'NC, opens on trip'),
  cell('relay + contacts', (x, y) => [...S.coil(x - 20, y - 8, '1CR'), text(x - 20, y + 10, 'rung 4', { size: 7, anchor: 'middle', fill: C.muted }), ...S.contactNO(x + 22, y - 12), text(x + 22, y - 18, '1CR', { size: 7, anchor: 'middle' }), ...S.contactNC(x + 22, y + 8), text(x + 22, y + 20, '1CR', { size: 7, anchor: 'middle' })], 'same name = same device'),
  cell('linked contact', (x, y) => [...S.contactNO(x - 4, y - 4), line(x - 4, y - 12, x - 4, y - 22, { width: 1, dash: '2 2' }), line(x - 12, y - 22, x + 4, y - 22, { width: 1.4 })], 'dashed = mechanical link'),
  cell('latching relay', (x, y) => [...S.coil(x, y - 4, 'L'), line(x - 8, y + 8, x + 8, y + 8, { width: 1 }), text(x, y + 18, 'latch coil', { size: 7, anchor: 'middle', fill: C.muted })], 'holds with power off'),
  cell('wire numbers', (x, y) => [line(x - 30, y, x + 30, y, { width: 1.4 }), ...S.contactNO(x, y), text(x - 22, y - 5, '3', { size: 8, anchor: 'middle', weight: 700 }), text(x + 22, y - 5, '4', { size: 8, anchor: 'middle', weight: 700 })], 'changes across a device'),
], { cols: 4, cellH: 100 }, 'Contacts are drawn de-energised; the coil that moves one shares its label.')

sheetFig('drawings/elec-operators-sheet.svg', 'Operator devices: momentary NO and NC pushbuttons, mushroom emergency stop, maintained pushbutton, two- and three-position selector switches, pilot lights with colour letters, push-to-test light, foot switch', 'Pushbuttons, selectors, lights', [
  cell('pushbutton NO', (x, y) => [...S.pushbutton(x, y)], 'momentary, start'),
  cell('pushbutton NC', (x, y) => [...S.pushbutton(x, y, { nc: true })], 'momentary, stop'),
  cell('emergency stop', (x, y) => [...S.pushbutton(x, y, { nc: true, mushroom: true })], 'mushroom head, NC'),
  cell('maintained PB', (x, y) => [...S.pushbutton(x, y), line(x, y - 12, x + 10, y - 16, { width: 1 }), text(x + 14, y - 14, 'M', { size: 7 })], 'push-pull, stays'),
  cell('selector, 2-position', (x, y) => [...S.selector(x, y)], 'HAND-AUTO'),
  cell('selector, 3-position', (x, y) => [...S.selector(x, y, { positions: 3 })], 'HAND-OFF-AUTO'),
  cell('pilot light', (x, y) => [...S.pilotLight(x, y, 'R')], 'letter = colour (R G A W)'),
  cell('push-to-test light', (x, y) => [...S.pilotLight(x, y + 4, 'G', { pushToTest: true })], 'press to check the lamp'),
  cell('illuminated PB', (x, y) => [...S.pushbutton(x - 10, y), circle(x + 18, y - 10, 6), path(`M${x + 14},${y - 14} l8,8 M${x + 14},${y - 6} l8,-8`, { width: 0.8 })], 'button and lamp'),
  cell('foot switch', (x, y) => [...S.processSwitch(x, y - 6, 'foot')], ''),
  cell('key switch', (x, y) => [...S.selector(x, y), circle(x - 12, y - 12, 4), line(x - 12, y - 8, x - 12, y, { width: 1 })], 'key operated'),
  cell('target table', (x, y) => [...table(x - 42, y - 22, [['pos', 'HAND', 'OFF', 'AUTO'], ['A', 'X', '', ''], ['B', '', '', 'X']], [22, 24, 20, 24], { rowH: 13, size: 6.5 })], 'X = contact closed'),
], { cols: 4, cellH: 100 }, 'Stops are NC and wired in series; starts are NO and wired in parallel.')

sheetFig('drawings/elec-process-switches-sheet.svg', 'Switches driven by the process: limit switches NO and NC plus held-open and held-closed, pressure, temperature, flow and float switches, proximity and speed switches', 'Process switches', [
  cell('limit switch NO', (x, y) => [...S.processSwitch(x, y, 'limit')], 'opens at rest'),
  cell('limit switch NC', (x, y) => [...S.processSwitch(x, y, 'limit', { nc: true })], 'closed at rest'),
  cell('limit NO, held closed', (x, y) => [...S.processSwitch(x, y, 'limit', { held: true }), line(x - 6, y, x + 6, y - 8, { width: 0 }), line(x - 6, y, x + 6, y + 0.5, { width: 1.4 })], 'actuated when drawn'),
  cell('limit NC, held open', (x, y) => [...S.processSwitch(x, y, 'limit', { nc: true, held: true }), line(x - 6, y, x + 6, y - 8, { width: 1.4 })], 'actuated when drawn'),
  cell('pressure switch NO', (x, y) => [...S.processSwitch(x, y - 6, 'pressure')], 'closes on rising pressure'),
  cell('pressure switch NC', (x, y) => [...S.processSwitch(x, y - 6, 'pressure', { nc: true })], 'opens on rising pressure'),
  cell('temperature switch', (x, y) => [...S.processSwitch(x, y - 6, 'temp')], 'thermostat'),
  cell('flow switch', (x, y) => [...S.processSwitch(x, y - 6, 'flow')], 'paddle or thermal'),
  cell('float switch', (x, y) => [...S.processSwitch(x, y - 6, 'float')], 'level'),
  cell('proximity switch', (x, y) => [...S.processSwitch(x, y - 6, 'prox')], 'inductive or capacitive'),
  cell('speed switch', (x, y) => [...S.processSwitch(x, y - 6, 'speed')], 'zero-speed, overspeed'),
  cell('foot switch', (x, y) => [...S.processSwitch(x, y - 6, 'foot')], ''),
], { cols: 4, cellH: 100 }, 'Drawn with the process at rest: no pressure, no flow, tank empty.')

sheetFig('drawings/elec-power-devices-sheet.svg', 'Power devices: contactor power contact, overload heater, fuse, circuit breaker, disconnect switch, motor circuit protector, control transformer with fused and grounded secondary, three-phase and single-phase motors, solenoid, brake, heater, horn', 'Power devices', [
  cell('contactor pole', (x, y) => [...S.contactorPole(x, y, 'M')], 'one per phase'),
  cell('overload heater', (x, y) => [...S.overloadHeater(x, y)], 'one per phase'),
  cell('fuse', (x, y) => [...S.fuse(x, y)], ''),
  cell('circuit breaker', (x, y) => [...S.breaker(x, y)], 'thermal-magnetic'),
  cell('disconnect switch', (x, y) => [...S.disconnect(x, y)], 'knife, non-fused'),
  cell('motor circuit protector', (x, y) => [...S.breaker(x, y), text(x + 8, y + 3, 'MCP', { size: 7 })], 'magnetic only'),
  cell('control transformer', (x, y) => [...S.transformerSym(x, y - 6), text(x - 20, y - 12, 'H1', { size: 6.5 }), text(x + 14, y - 12, 'H2', { size: 6.5 }), text(x - 20, y + 16, 'X1', { size: 6.5 }), text(x + 14, y + 16, 'X2', { size: 6.5 }), ...S.groundSym(x + 18, y + 8).map((s) => s)], 'X2 grounded, X1 fused'),
  cell('three-phase motor', (x, y) => [...S.motorSym(x, y), ...[-6, 0, 6].map((d) => line(x + d, y - 10, x + d, y - 20, { width: 1.2 }))], 'T1 T2 T3'),
  cell('single-phase motor', (x, y) => [...S.motorSym(x, y, { phases: 1 }), ...[-4, 4].map((d) => line(x + d, y - 10, x + d, y - 20, { width: 1.2 }))], ''),
  cell('solenoid', (x, y) => [...S.solenoidSym(x, y)], 'valve coil'),
  cell('brake', (x, y) => [line(x - 16, y, x - 8, y, { width: 1.4 }), rect(x - 8, y - 6, 16, 12), text(x, y + 3.5, 'BR', { size: 7, anchor: 'middle', weight: 700 }), line(x + 8, y, x + 16, y, { width: 1.4 })], 'motor brake coil'),
  cell('heater / horn', (x, y) => [line(x - 30, y, x - 22, y, { width: 1.4 }), rect(x - 22, y - 5, 16, 10), path(`M${x - 20},${y} l3,-3 l3,6 l3,-6 l3,3`, { width: 0.8 }), line(x - 6, y, x, y, { width: 1.4 }), line(x + 6, y, x + 12, y, { width: 1.4 }), path(`M${x + 12},${y - 6} l0,12 l12,6 l0,-24 z`, { width: 1.2 })], 'resistance, alarm'),
], { cols: 4, cellH: 100 }, 'Power devices carry motor current; control devices switch coils.')

sheetFig('drawings/elec-wires-terminals-sheet.svg', 'Wires and terminals: junction dot, crossing without a dot, terminal, wire number, ground and chassis, shielded cable, plug and receptacle, DC and AC sources', 'Wires, terminals, grounds', [
  cell('junction', (x, y) => [line(x - 20, y, x + 20, y, { width: 1.4 }), line(x, y - 16, x, y + 16, { width: 1.4 }), S.junctionDot(x, y)], 'dot = connected'),
  cell('crossing', (x, y) => [line(x - 20, y, x + 20, y, { width: 1.4 }), line(x, y - 16, x, y + 16, { width: 1.4 })], 'no dot = not connected'),
  cell('crossing (hop)', (x, y) => [line(x - 20, y, x - 5, y, { width: 1.4 }), path(`M${x - 5},${y} a5,5 0 0 1 10,0`, { width: 1.4 }), line(x + 5, y, x + 20, y, { width: 1.4 }), line(x, y - 16, x, y + 16, { width: 1.4 })], 'older drawings'),
  cell('terminal', (x, y) => [line(x - 22, y, x - 4, y, { width: 1.4 }), ...S.terminal(x, y, 'TB1-7'), line(x + 4, y, x + 22, y, { width: 1.4 })], 'strip and point number'),
  cell('wire number', (x, y) => [line(x - 28, y, x + 28, y, { width: 1.4 }), rect(x - 8, y - 12, 16, 10, { fill: C.paper, stroke: 'none' }), text(x, y - 4, '104', { size: 8, anchor: 'middle', weight: 700 })], 'same number end to end'),
  cell('ground', (x, y) => [...S.groundSym(x, y - 10)], 'earth'),
  cell('chassis', (x, y) => [line(x, y - 10, x, y, { width: 1.4 }), line(x - 8, y, x + 8, y, { width: 1.4 }), ...[-8, -2, 4].map((d) => line(x + d, y, x + d - 4, y + 5, { width: 1.2 }))], 'frame, not earth'),
  cell('shielded cable', (x, y) => [line(x - 24, y - 4, x + 24, y - 4, { width: 1.2 }), line(x - 24, y + 4, x + 24, y + 4, { width: 1.2 }), path(`M${x - 18},${y - 12} q18,-6 36,0`, { width: 1, dash: '3 2' }), line(x + 18, y - 12, x + 18, y - 18, { width: 1 }), ...S.groundSym(x + 18, y - 32).map((s) => s)], 'shield to ground one end'),
  cell('plug and receptacle', (x, y) => [line(x - 24, y, x - 8, y, { width: 1.4 }), path(`M${x - 8},${y - 6} l0,12`, { width: 1.6 }), path(`M${x - 4},${y - 6} a6,6 0 0 1 0,12`, { width: 1.4 }), line(x + 2, y, x + 24, y, { width: 1.4 })], 'cord connection'),
  cell('DC source', (x, y) => [line(x - 12, y - 8, x - 12, y + 8, { width: 2 }), line(x - 6, y - 4, x - 6, y + 4, { width: 1.2 }), line(x, y - 8, x, y + 8, { width: 2 }), line(x + 6, y - 4, x + 6, y + 4, { width: 1.2 }), text(x - 20, y - 10, '+', { size: 9 }), text(x + 12, y - 10, '−', { size: 9 })], 'battery / 24 V DC'),
  cell('AC source', (x, y) => [circle(x, y, 10), path(`M${x - 6},${y} q3,-6 6,0 t6,0`, { width: 1.2 })], ''),
  cell('cable / conduit', (x, y) => [rect(x - 26, y - 6, 52, 12, { rx: 6 }), text(x, y + 3.5, 'C-12  3/4"C', { size: 7, anchor: 'middle' })], 'cable schedule number'),
], { cols: 4 }, 'A wire number changes only when the wire passes through a device.')

sheetFig('drawings/elec-plc-drive-sheet.svg', 'PLC and drive symbols on a control schematic: input point with its field device, output point driving a coil, IEC and Allen-Bradley address styles, a VFD block with its control terminals, an E-stop safety relay', 'PLC and drive symbols', [
  cell('PLC input (AB style)', (x, y) => [line(x - 44, y, x - 34, y, { width: 1.4 }), ...S.pushbutton(x - 26, y), ...S.plcPoint(x + 12, y, 'I:1/0')], 'device feeds the input'),
  cell('PLC output (AB style)', (x, y) => [...S.plcPoint(x - 14, y, 'O:2/3', { output: true }), ...S.coil(x + 32, y, 'M')], 'output drives a coil'),
  cell('IEC addresses', (x, y) => [...S.plcPoint(x, y - 10, '%I0.0'), ...S.plcPoint(x, y + 12, '%Q0.1', { output: true })], 'I input, Q output'),
  cell('common / 24 V', (x, y) => [line(x - 20, y - 12, x + 20, y - 12, { width: 1.4 }), text(x, y - 16, '+24 V DC', { size: 7, anchor: 'middle' }), line(x - 20, y + 12, x + 20, y + 12, { width: 1.4 }), text(x, y + 22, '0 V (COM)', { size: 7, anchor: 'middle' })], 'input card common'),
  cell('VFD block', (x, y) => [rect(x - 24, y - 20, 48, 40, { rx: 3 }), text(x, y - 6, 'VFD', { size: 9, anchor: 'middle', weight: 700 }), ...['L1 L2 L3', 'T1 T2 T3'].map((t, i) => text(x, y + 6 + i * 9, t, { size: 6.5, anchor: 'middle' })), line(x - 34, y - 14, x - 24, y - 14, { width: 1 }), text(x - 36, y - 11, 'RUN', { size: 6, anchor: 'end' }), line(x - 34, y - 4, x - 24, y - 4, { width: 1 }), text(x - 36, y - 1, 'FWD', { size: 6, anchor: 'end' }), line(x - 34, y + 6, x - 24, y + 6, { width: 1 }), text(x - 36, y + 9, '0-10V', { size: 6, anchor: 'end' })], 'control terminals on the left'),
  cell('drive fault contact', (x, y) => [...S.contactNO(x, y), text(x, y - 12, 'VFD FLT', { size: 7, anchor: 'middle' })], 'relay inside the drive'),
  cell('safety relay', (x, y) => [rect(x - 22, y - 14, 44, 28, { rx: 3 }), text(x, y - 2, 'SR', { size: 9, anchor: 'middle', weight: 700 }), text(x, y + 8, 'S11 S12 S21', { size: 6, anchor: 'middle' }), line(x - 32, y - 8, x - 22, y - 8, { width: 1 }), line(x - 32, y + 8, x - 22, y + 8, { width: 1 })], 'monitored E-stop'),
  cell('E-stop, dual channel', (x, y) => [...S.pushbutton(x, y - 8, { nc: true, mushroom: true }), ...S.pushbutton(x, y + 10, { nc: true }), line(x, y - 4, x, y + 6, { width: 1, dash: '2 2' })], 'two NC contacts, one head'),
], { cols: 4, cellH: 104 }, 'The PLC page shows wiring to the card; the logic lives in the program.')

// ================= Pneumatic worked circuit and sequence chart =================
const pneuValve52 = (vx, vy, { left = 'solenoid', tag = '' } = {}) => [
  ...S.dcv(vx, vy, { positions: ['b', 'a'], ports: 5, w: 30, h: 26, left, right: 'spring', rest: 0, labels: false }),
  text(vx - 19.5, vy - 24, '4', { size: 7.5, anchor: 'middle' }), text(vx - 10.5, vy - 24, '2', { size: 7.5, anchor: 'middle' }),
  text(vx - 32, vy + 27, '5', { size: 7.5, anchor: 'middle' }), text(vx - 15, vy + 34, '1', { size: 7.5, anchor: 'middle' }), text(vx + 2, vy + 27, '3', { size: 7.5, anchor: 'middle' }),
  ...S.exhaust(vx - 24, vy + 21), ...S.exhaust(vx - 6, vy + 21),
  ...(tag ? [text(vx - 15, vy + 46, tag, { size: 8.5, anchor: 'middle', weight: 700 })] : []),
]
const pneuCyl = (vx, cy, tag) => [
  ...S.cylinder(vx - 5, cy, { w: 60, h: 18, rodLen: 22, piston: 0.15 }),
  text(vx - 5, cy - 14, tag, { size: 8.5, anchor: 'middle', weight: 700 }),
  // port 4 to the cap end, port 2 to the rod end (rod end pressurised at rest = retracted)
  line(vx - 19.5, 169, vx - 19.5, 120, { width: 1.5 }), line(vx - 19.5, 120, vx - 31, 120, { width: 1.5 }), line(vx - 31, 120, vx - 31, cy + 9, { width: 1.5 }),
  line(vx - 10.5, 169, vx - 10.5, 130, { width: 1.5 }), line(vx - 10.5, 130, vx + 21, 130, { width: 1.5 }), line(vx + 21, 130, vx + 21, cy + 9, { width: 1.5 }),
]
fig('drawings/pneu-clamp-press-circuit.svg', 'Pneumatic clamp-and-press circuit: FRL, a solenoid 5/2 valve driving the clamp cylinder 1A, a roller limit valve 1S2 struck by the clamp rod, and its pilot signal shifting the second 5/2 valve so the press cylinder 2A extends only after the clamp is home',
  svg(500, 310, [
    text(250, 18, 'Clamp, then press: the schematic as drawn at rest', { anchor: 'middle', weight: 700, size: 12 }),
    // supply
    ...S.airSource(30, 262, 8), line(38, 262, 46, 262, { width: 1.5 }), ...S.frlSimple(80, 262), text(80, 290, '0Z1 FRL, 80 psi', { size: 8.5, anchor: 'middle' }),
    line(114, 262, 330, 262, { width: 1.5 }), S.junction(135, 262), S.junction(240.7, 262),
    // valve 1V1 (solenoid) and clamp cylinder 1A
    ...pneuValve52(150, 190, { tag: '1V1' }), line(135, 211, 135, 262, { width: 1.5 }), text(108, 172, 'Y1', { size: 8.5, anchor: 'middle', weight: 700 }),
    ...pneuCyl(150, 70, '1A clamp'),
    // roller limit valve 1S2 at the clamp rod's extended position
    ...S.dcv(258, 70, { positions: ['exhaust', 'pass'], ports: 3, w: 24, h: 22, left: 'roller', right: 'spring', rest: 0, labels: false }),
    text(284, 100, '1S2', { size: 8.5, weight: 700 }), text(246, 42, '2', { size: 7.5, anchor: 'middle' }), text(233, 97, '1', { size: 7.5 }), text(255, 105, '3', { size: 7.5 }),
    line(240.7, 89, 240.7, 262, { width: 1.5 }), ...S.exhaust(251.3, 89),
    line(197, 72, 214, 72, { width: 1, dash: '2 2' }),
    // pilot from 1S2 port 2 to valve 2V1
    S.fl(246, 51, 246, 36, 'pilot'), S.fl(246, 36, 289, 36, 'pilot'), S.fl(289, 36, 289, 190, 'pilot'), text(284, 150, 'pilot 14', { size: 7.5, anchor: 'end' }),
    // valve 2V1 (pilot) and press cylinder 2A
    ...pneuValve52(345, 190, { left: 'pilot', tag: '2V1' }), line(330, 211, 330, 262, { width: 1.5 }),
    ...pneuCyl(345, 70, '2A press'),
    // reading notes
    note(420, 120, 'read at rest:\nboth rods in,\nports 2 live', { size: 9, anchor: 'start' }),
    note(420, 200, 'Y1 on: 1A out;\n1A hits 1S2;\n2V1 shifts;\n2A out', { size: 9, anchor: 'start' }),
    caption(500, 310, 'Number the parts, find the supply, then follow one signal at a time.'),
  ], { title: 'Pneumatic clamp and press circuit' }))

fig('drawings/pneu-sequence-chart.svg', 'Step-displacement (sequence) chart for the clamp-and-press circuit: cylinder 1A extends in step 1, 2A extends in step 2 and retracts in step 3, 1A retracts in step 4, with the signal that starts each step named under the chart',
  svg(500, 250, [
    text(250, 18, 'Sequence chart: 1A+  2A+  2A-  1A-', { anchor: 'middle', weight: 700, size: 12 }),
    ...[['1A clamp', 50], ['2A press', 120]].map(([lab, y]) => [
      text(22, y + 24, lab, { size: 9.5, weight: 600 }), rect(100, y, 340, 40, { fill: C.grey, stroke: C.line }),
      text(94, y + 8, '1', { size: 8, anchor: 'end', fill: C.muted }), text(94, y + 40, '0', { size: 8, anchor: 'end', fill: C.muted }),
      ...[1, 2, 3, 4].map((i) => line(100 + i * 85, y, 100 + i * 85, y + 40, { width: 0.8, stroke: C.line, dash: '3 3' })),
    ]),
    // 1A: out in step 1, back in step 4
    path('M100,90 L185,50 L355,50 L440,90', { width: 2, stroke: C.blue }),
    // 2A: out in step 2, back in step 3
    path('M100,160 L185,160 L270,120 L355,160 L440,160', { width: 2, stroke: C.red }),
    ...[1, 2, 3, 4, 5].map((i) => text(100 + (i - 1) * 85, 178, i === 5 ? '5 = 1' : String(i), { size: 9, anchor: 'middle', weight: 700 })),
    text(270, 192, 'step', { size: 9, anchor: 'middle', fill: C.muted }),
    ...[['Y1 (start)', 100], ['1S2', 185], ['2S2', 270], ['2S1', 355]].map(([s, x]) => text(x + 2, 208, s, { size: 8.5, fill: C.muted })),
    text(22, 208, 'signal:', { size: 8.5, fill: C.muted }),
    caption(500, 250, 'A rising line is a rod going out; the signal under each step starts it.'),
  ], { title: 'Sequence chart' }))

// ================= Motor control schematics =================
const rung = (y, n, x1 = 60) => [text(x1 - 18, y + 4, String(n), { size: 9, anchor: 'middle', fill: C.muted, weight: 700 })]
const wireNo = (x, y, n) => text(x, y - 6, String(n), { size: 8.5, anchor: 'middle', weight: 700, fill: C.blue })
const cpt = (x, y) => [
  // control power transformer with fused X1 and grounded X2, primary from L1/L2 above
  line(x - 14, y - 30, x - 14, y - 4, { width: 1.4 }), line(x + 14, y - 30, x + 14, y - 4, { width: 1.4 }), text(x - 14, y - 34, 'L1', { size: 8.5, anchor: 'middle', weight: 700 }), text(x + 14, y - 34, 'L2', { size: 8.5, anchor: 'middle', weight: 700 }),
  text(x - 22, y - 8, 'H1', { size: 7, anchor: 'end' }), text(x + 22, y - 8, 'H2', { size: 7 }),
  ...S.transformerSym(x, y), text(x + 40, y + 4, 'CPT 480:120 V', { size: 7.5, fill: C.muted }),
  text(x - 22, y + 12, 'X1', { size: 7, anchor: 'end' }), text(x + 22, y + 12, 'X2', { size: 7 }),
]
fig('drawings/three-wire-start-stop.svg', 'Three-wire start-stop motor control schematic in ladder format: control transformer with fused X1 and grounded X2, rung 1 with the NC stop button, NO start button, seal-in contact M in parallel with start, overload contact and coil M, rung 2 with an M contact and run light, rung 3 with a stopped light, wire numbers, rung numbers and the contact cross-reference under the coil',
  svg(500, 330, [
    ...cpt(250, 44),
    // X1 through fuse to the left rail; X2 through ground to the right rail
    line(236, 48, 236, 70, { width: 1.4 }), line(236, 70, 60, 70, { width: 2 }), ...S.fuse(150, 70, { vertical: false }), text(150, 58, 'FU 2 A', { size: 7.5, anchor: 'middle', fill: C.muted }),
    line(264, 48, 264, 70, { width: 1.4 }), line(264, 70, 440, 70, { width: 2 }), ...S.groundSym(350, 70), S.junctionDot(350, 70),
    ...S.rails(60, 440, 70, 290, { l1: 'X1', l2: 'X2' }),
    // rung 1: stop, start (seal-in below), OL, coil M
    ...rung(120, 1),
    line(60, 120, 100, 120, { width: 1.4 }), ...S.pushbutton(114, 120, { nc: true }), text(114, 138, '1PB STOP', { size: 7.5, anchor: 'middle' }),
    line(128, 120, 176, 120, { width: 1.4 }), ...S.pushbutton(190, 120), text(190, 138, '2PB START', { size: 7.5, anchor: 'middle' }),
    line(204, 120, 300, 120, { width: 1.4 }), ...S.overloadContact(316, 120), line(332, 120, 350, 120, { width: 1.4 }),
    ...S.coil(366, 120, 'M'), line(382, 120, 440, 120, { width: 1.4 }), text(366, 138, '1M', { size: 8, anchor: 'middle', weight: 700 }), text(366, 149, '2, 3, PWR', { size: 7.5, anchor: 'middle', fill: C.blue }),
    // seal-in
    S.junctionDot(160, 120), S.junctionDot(220, 120), line(160, 120, 160, 152, { width: 1.4 }), line(160, 152, 176, 152, { width: 1.4 }), ...S.contactNO(190, 152), line(204, 152, 220, 152, { width: 1.4 }), line(220, 152, 220, 120, { width: 1.4 }),
    text(190, 168, '1M seal-in', { size: 7.5, anchor: 'middle' }),
    wireNo(80, 120, 1), wireNo(150, 120, 2), wireNo(250, 120, 3), wireNo(342, 120, 4), wireNo(410, 120, 'X2'),
    // rung 2: M aux contact, run light
    ...rung(200, 2), line(60, 200, 176, 200, { width: 1.4 }), ...S.contactNO(190, 200), text(190, 218, '1M', { size: 7.5, anchor: 'middle' }), line(204, 200, 350, 200, { width: 1.4 }), ...S.pilotLight(366, 200, 'G'), line(382, 200, 440, 200, { width: 1.4 }), text(366, 222, 'RUN', { size: 7.5, anchor: 'middle' }),
    wireNo(120, 200, 1), wireNo(250, 200, 5),
    // rung 3: M NC contact, stopped light
    ...rung(250, 3), line(60, 250, 176, 250, { width: 1.4 }), ...S.contactNC(190, 250), text(190, 268, '1M', { size: 7.5, anchor: 'middle' }), line(204, 250, 350, 250, { width: 1.4 }), ...S.pilotLight(366, 250, 'R'), line(382, 250, 440, 250, { width: 1.4 }), text(366, 272, 'STOPPED', { size: 7.5, anchor: 'middle' }),
    wireNo(120, 250, 1), wireNo(250, 250, 6),
    // margin descriptions
    text(470, 124, 'PUMP\nSTART', { size: 7, fill: C.muted }), text(470, 204, 'RUN\nLIGHT', { size: 7, fill: C.muted }), text(470, 254, 'STOP\nLIGHT', { size: 7, fill: C.muted }),
    caption(500, 330, 'Stop opens the rung, start closes it, M seals in until stop or OL opens.'),
  ], { title: 'Three-wire start-stop schematic' }))

fig('drawings/wire-and-rung-numbering.svg', 'Decoder for the numbering on a control schematic: rung (line) numbers down the left margin, wire numbers on every conductor that change only across a device, device designations built from a number and a letter code, the coil cross-reference listing the rungs where its contacts appear, and the rung description in the right margin',
  svg(500, 290, [
    ...S.rails(60, 400, 30, 195, { l1: 'X1', l2: 'X2' }),
    ...rung(80, 4), line(60, 80, 100, 80, { width: 1.4 }), ...S.pushbutton(114, 80, { nc: true }), line(128, 80, 176, 80, { width: 1.4 }), ...S.processSwitch(192, 80, 'pressure'), line(208, 80, 300, 80, { width: 1.4 }), ...S.coil(316, 80, 'CR'), line(332, 80, 400, 80, { width: 1.4 }),
    wireNo(80, 80, 1), wireNo(152, 80, 12), wireNo(254, 80, 13),
    text(114, 96, '1PB', { size: 7.5, anchor: 'middle' }), text(192, 108, '1PS', { size: 7.5, anchor: 'middle' }), text(316, 98, '2CR', { size: 8, anchor: 'middle', weight: 700 }), text(316, 109, '6, 9, 11', { size: 7.5, anchor: 'middle', fill: C.blue }),
    ...rung(160, 6), line(60, 160, 176, 160, { width: 1.4 }), ...S.contactNO(190, 160), text(190, 178, '2CR', { size: 7.5, anchor: 'middle' }), line(204, 160, 300, 160, { width: 1.4 }), ...S.solenoidSym(316, 160), text(316, 178, '1SOL', { size: 7.5, anchor: 'middle' }), line(332, 160, 400, 160, { width: 1.4 }),
    wireNo(120, 160, 1), wireNo(254, 160, 14),
    text(430, 84, 'LOW OIL\nRELAY', { size: 7, fill: C.muted }), text(430, 164, 'DUMP\nVALVE', { size: 7, fill: C.muted }),
    // callouts
    callout(1, 30, 60), callout(2, 152, 102), callout(3, 192, 122), callout(4, 350, 105), callout(5, 455, 60),
    legend(60, 212, ['rung (line) number, top to bottom', 'wire number: same on every end of that wire', 'device: number + letters (PS = pressure switch)', 'cross-reference: rungs holding 2CR contacts', 'margin note says what the rung does'], { size: 8.5, gap: 12, start: 1 }),
  ], { title: 'Wire and rung numbering' }))

fig('drawings/forward-reverse-interlocks.svg', 'Forward-reverse motor control schematic: one stop button, forward and reverse start buttons each with a seal-in contact, an NC contact of the opposite coil in each rung as the electrical interlock, and the dashed mechanical interlock drawn between the F and R coils',
  svg(500, 300, [
    ...S.rails(60, 440, 30, 270, { l1: 'X1', l2: 'X2' }),
    // stop common to both rungs
    ...rung(80, 1), line(60, 80, 86, 80, { width: 1.4 }), ...S.pushbutton(100, 80, { nc: true }), text(100, 98, 'STOP', { size: 7.5, anchor: 'middle' }), line(114, 80, 130, 80, { width: 1.4 }), S.junctionDot(130, 80),
    // forward rung
    line(130, 80, 146, 80, { width: 1.4 }), ...S.pushbutton(160, 80), text(160, 98, 'FWD', { size: 7.5, anchor: 'middle' }), line(174, 80, 190, 80, { width: 1.4 }), S.junctionDot(190, 80),
    line(190, 80, 236, 80, { width: 1.4 }), ...S.contactNC(250, 80), text(250, 98, 'R', { size: 7.5, anchor: 'middle' }), line(264, 80, 300, 80, { width: 1.4 }), ...S.overloadContact(316, 80), line(332, 80, 350, 80, { width: 1.4 }), ...S.coil(366, 80, 'F'), line(382, 80, 440, 80, { width: 1.4 }),
    line(130, 80, 130, 110, { width: 1.4 }), line(130, 110, 146, 110, { width: 1.4 }), ...S.contactNO(160, 110), text(160, 126, 'F', { size: 7.5, anchor: 'middle' }), line(174, 110, 190, 110, { width: 1.4 }), line(190, 110, 190, 80, { width: 1.4 }),
    // reverse rung
    ...rung(170, 2), line(130, 110, 130, 170, { width: 1.4 }), line(130, 170, 146, 170, { width: 1.4 }), ...S.pushbutton(160, 170), text(160, 188, 'REV', { size: 7.5, anchor: 'middle' }), line(174, 170, 190, 170, { width: 1.4 }), S.junctionDot(190, 170),
    line(190, 170, 236, 170, { width: 1.4 }), ...S.contactNC(250, 170), text(250, 188, 'F', { size: 7.5, anchor: 'middle' }), line(264, 170, 300, 170, { width: 1.4 }), ...S.overloadContact(316, 170), line(332, 170, 350, 170, { width: 1.4 }), ...S.coil(366, 170, 'R'), line(382, 170, 440, 170, { width: 1.4 }),
    line(130, 170, 130, 200, { width: 1.4 }), line(130, 200, 146, 200, { width: 1.4 }), ...S.contactNO(160, 200), text(160, 216, 'R', { size: 7.5, anchor: 'middle' }), line(174, 200, 190, 200, { width: 1.4 }), line(190, 200, 190, 170, { width: 1.4 }),
    // mechanical interlock between the coils
    line(366, 88, 366, 162, { width: 1.2, dash: '4 3' }), text(378, 128, 'mechanical\ninterlock', { size: 7.5, fill: C.muted }),
    wireNo(76, 80, 1), wireNo(122, 80, 2), wireNo(200, 80, 3), wireNo(282, 80, 4), wireNo(200, 170, 5), wireNo(282, 170, 6),
    // legend
    callout(1, 250, 60), callout(2, 340, 128), callout(3, 160, 60),
    legend(60, 244, ['electrical interlock: NC contact of the other coil', 'mechanical interlock: the bar that stops both closing', 'pushbutton interlock (NC of the other button) is often added'], { size: 8.5, gap: 12 }),
    caption(500, 300, 'R cannot pull in while F is in, on paper and on the starter.'),
  ], { title: 'Forward-reverse with interlocks' }))

fig('drawings/schematic-vs-wiring-diagram.svg', 'The same start-stop starter drawn two ways: on the left the schematic in ladder form showing how it works, on the right the wiring (connection) diagram showing where each wire lands, with the remote pushbutton station, the terminal strip 1 2 3, the starter coil terminals A1 A2 and the overload contact 95 96',
  svg(500, 300, [
    text(125, 18, 'Schematic (how it works)', { anchor: 'middle', weight: 700, size: 11.5 }), text(375, 18, 'Wiring diagram (where it lands)', { anchor: 'middle', weight: 700, size: 11.5 }),
    // schematic
    ...S.rails(30, 230, 40, 130, { l1: 'X1', l2: 'X2' }),
    line(30, 70, 50, 70, { width: 1.4 }), ...S.pushbutton(64, 70, { nc: true }), line(78, 70, 96, 70, { width: 1.4 }), ...S.pushbutton(110, 70), line(124, 70, 160, 70, { width: 1.4 }), ...S.overloadContact(174, 70), line(190, 70, 196, 70, { width: 1.4 }), ...S.coil(212, 70, 'M'), line(228, 70, 230, 70, { width: 1.4 }),
    S.junctionDot(88, 70), S.junctionDot(132, 70), line(88, 70, 88, 100, { width: 1.4 }), line(88, 100, 96, 100, { width: 1.4 }), ...S.contactNO(110, 100), line(124, 100, 132, 100, { width: 1.4 }), line(132, 100, 132, 70, { width: 1.4 }),
    wireNo(42, 70, 1), wireNo(88, 70, 2), wireNo(146, 70, 3), text(64, 86, 'STOP', { size: 7, anchor: 'middle' }), text(110, 86, 'START', { size: 7, anchor: 'middle' }), text(110, 116, 'M', { size: 7, anchor: 'middle' }),
    note(125, 156, 'devices placed for reading, not for where they sit', { anchor: 'middle', size: 8.5 }),
    // wiring diagram: pushbutton station (remote), cable, starter panel with terminal strip
    rect(262, 40, 92, 100, { rx: 4, dash: '4 3', width: 1 }), text(308, 52, 'PB STATION', { size: 7.5, anchor: 'middle', weight: 700 }),
    rect(272, 62, 44, 20, { rx: 3 }), text(294, 75, 'STOP', { size: 7.5, anchor: 'middle' }), rect(272, 102, 44, 20, { rx: 3 }), text(294, 115, 'START', { size: 7.5, anchor: 'middle' }),
    ...[[342, 66, '1'], [342, 92, '2'], [342, 118, '3']].map(([x, y, n]) => [circle(x, y, 3.5, { fill: C.paper }), text(x, y - 6, n, { size: 6.5, anchor: 'middle', fill: C.blue, weight: 700 })]),
    line(316, 66, 338, 66, { width: 1, stroke: C.blue }), line(316, 78, 330, 78, { width: 1, stroke: C.blue }), line(330, 78, 330, 106, { width: 1, stroke: C.blue }), line(330, 92, 338, 92, { width: 1, stroke: C.blue }), S.junctionDot(330, 92), line(316, 106, 330, 106, { width: 1, stroke: C.blue }), line(316, 118, 338, 118, { width: 1, stroke: C.blue }),
    // cable to the panel
    ...[66, 92, 118].map((y) => line(346, y, 384, y, { width: 1, stroke: C.blue })), text(365, 150, 'C-14, 3 cond', { size: 6.5, anchor: 'middle', fill: C.muted }),
    rect(372, 40, 116, 240, { rx: 4, width: 1 }), text(430, 52, 'STARTER PANEL', { size: 7.5, anchor: 'middle', weight: 700 }),
    rect(380, 56, 16, 72, { fill: C.grey }), text(388, 138, 'TB1', { size: 6.5, anchor: 'middle', fill: C.muted }),
    ...[[66, '1'], [92, '2'], [118, '3']].map(([y, n]) => [circle(388, y, 3.5, { fill: C.paper }), text(388, y - 6, n, { size: 6.5, anchor: 'middle', fill: C.blue, weight: 700 })]),
    rect(410, 100, 70, 80, { fill: C.grey }), text(445, 112, 'M starter', { size: 8, anchor: 'middle', weight: 700 }),
    ...[['A1', 420, 124], ['A2', 470, 124], ['13', 420, 152], ['14', 445, 152], ['95', 445, 172], ['96', 470, 172]].map(([l, x, y]) => [circle(x, y, 3.5, { fill: C.paper }), text(x, y - 6, l, { size: 6.5, anchor: 'middle' })]),
    rect(410, 200, 70, 40, { fill: C.grey }), text(445, 214, 'CPT', { size: 8, anchor: 'middle', weight: 700 }), ...[['X1', 420], ['X2', 470]].map(([l, x]) => [circle(x, 230, 3.5, { fill: C.paper }), text(x, 224, l, { size: 6.5, anchor: 'middle' })]),
    // panel wiring: 1 to X1; 2 to 13; 3 to A1 and 14; A2 to 96; 95 to X2
    line(392, 66, 402, 66, { width: 1, stroke: C.blue }), line(402, 66, 402, 246, { width: 1, stroke: C.blue }), line(402, 246, 420, 246, { width: 1, stroke: C.blue }), line(420, 246, 420, 234, { width: 1, stroke: C.blue }),
    line(392, 92, 406, 92, { width: 1, stroke: C.blue }), line(406, 92, 406, 160, { width: 1, stroke: C.blue }), line(406, 160, 420, 160, { width: 1, stroke: C.blue }), line(420, 160, 420, 156, { width: 1, stroke: C.blue }),
    line(392, 118, 420, 118, { width: 1, stroke: C.blue }), line(420, 118, 420, 120, { width: 1, stroke: C.blue }), line(420, 118, 445, 118, { width: 1, stroke: C.blue }), line(445, 118, 445, 148, { width: 1, stroke: C.blue }), S.junctionDot(420, 118),
    line(470, 128, 470, 168, { width: 1, stroke: C.blue }), line(445, 176, 445, 188, { width: 1, stroke: C.blue }), line(445, 188, 484, 188, { width: 1, stroke: C.blue }), line(484, 188, 484, 230, { width: 1, stroke: C.blue }), line(484, 230, 474, 230, { width: 1, stroke: C.blue }),
    note(375, 262, 'same wire numbers on both drawings', { anchor: 'middle', size: 8.5 }),
    caption(500, 300, 'Trace by wire number: the schematic explains, the wiring diagram locates.'),
  ], { title: 'Schematic versus wiring diagram' }))

fig('drawings/mcc-bucket-sheet.svg', 'MCC bucket sheet: elevation of a combination starter bucket showing the door handle for the disconnect, fuses or breaker, contactor, overload relay, control transformer and terminal block, beside the bucket schedule that lists motor, horsepower, full-load amps, starter size, breaker and overload settings, cable size and drawing references',
  svg(500, 300, [
    text(110, 18, 'Bucket 3B (elevation)', { anchor: 'middle', weight: 700, size: 11 }), text(340, 18, 'Bucket schedule', { anchor: 'middle', weight: 700, size: 11 }),
    rect(30, 30, 160, 250, { fill: C.grey, rx: 3 }),
    // disconnect handle on the door
    rect(40, 40, 30, 60, { fill: C.paper }), rect(50, 46, 10, 40, { fill: C.steelDark }), text(55, 112, 'handle', { size: 7, anchor: 'middle', fill: C.muted }),
    // breaker / fuses
    ...[0, 1, 2].map((i) => [line(100 + i * 18, 40, 100 + i * 18, 52, { width: 1.4 }), ...S.fuse(100 + i * 18, 68, {}), line(100 + i * 18, 84, 100 + i * 18, 96, { width: 1.4 })]), text(158, 70, 'FU', { size: 7.5, fill: C.muted }),
    // contactor
    ...[0, 1, 2].map((i) => S.contactorPole(100 + i * 18, 112, '')), text(158, 115, 'M', { size: 7.5, fill: C.muted }),
    // overload heaters
    ...[0, 1, 2].map((i) => [line(100 + i * 18, 128, 100 + i * 18, 136, { width: 1.4 }), rect(95 + i * 18, 136, 10, 16), line(100 + i * 18, 152, 100 + i * 18, 166, { width: 1.4 })]), text(158, 148, 'OL', { size: 7.5, fill: C.muted }),
    // CPT and terminal block
    rect(150, 176, 34, 24, { fill: C.paper }), text(167, 191, 'CPT', { size: 8, anchor: 'middle', weight: 700 }),
    rect(150, 212, 34, 18, { fill: C.paper }), ...[0, 1, 2].map((i) => circle(158 + i * 9, 221, 3, { fill: C.grey })), text(167, 244, 'TB', { size: 7.5, anchor: 'middle', fill: C.muted }),
    // motor leads out the bottom
    ...[0, 1, 2].map((i) => [line(100 + i * 18, 166, 100 + i * 18, 244, { width: 1.4 }), text(100 + i * 18, 256, `T${i + 1}`, { size: 7, anchor: 'middle' })]),
    // pilot devices on the door
    circle(55, 150, 6), text(55, 168, 'RUN', { size: 6.5, anchor: 'middle' }), circle(55, 190, 6, { fill: C.redSoft }), text(55, 208, 'STOP', { size: 6.5, anchor: 'middle' }), circle(55, 230, 6, { fill: C.greenSoft }), text(55, 248, 'START', { size: 6.5, anchor: 'middle' }),
    table(200, 30, [['Field', 'Bucket 3B'], ['Load', 'P-101 cooling pump'], ['HP / FLA', '25 hp / 32 A'], ['Voltage', '480 V, 3 ph'], ['Starter', 'NEMA size 2, FVNR'], ['Disconnect', '60 A fused, FU 45 A'], ['OL setting', '32 A (class 10)'], ['CPT', '480:120 V, 150 VA'], ['Cable', '3 #8 + #10 gnd, C-12'], ['Schematic', 'E-201 sh 4, lines 12-19']], [66, 220], { rowH: 22, size: 8.5 }),
    note(343, 272, 'the schedule is the settings sheet: check OL and fuse against it', { anchor: 'middle', size: 8.5 }),
    caption(500, 300, 'One bucket, one motor: elevation shows the parts, schedule the settings.'),
  ], { title: 'MCC bucket sheet' }))

fig('drawings/one-line-extract.svg', 'Extract from a plant one-line diagram: utility feed through the main breaker into a 13.8 kV to 480 V transformer, the 480 V switchgear bus, a feeder breaker to MCC-1, and the MCC buckets shown as breaker, starter and motor symbols with the ratings a millwright reads to find the right bucket for a motor',
  svg(500, 320, [
    text(250, 18, 'Plant one-line (extract)', { anchor: 'middle', weight: 700, size: 12 }),
    text(60, 42, 'utility 13.8 kV', { size: 9 }), line(60, 46, 60, 60, { width: 1.6 }), ...S.breaker(60, 76), text(72, 78, '52-M main', { size: 8 }),
    line(60, 92, 60, 104, { width: 1.6 }), circle(60, 114, 10), circle(60, 128, 10), text(76, 118, 'T-1 2000 kVA', { size: 8 }), text(76, 129, '13.8 kV : 480 V', { size: 8 }),
    line(60, 138, 60, 156, { width: 1.6 }), line(30, 156, 470, 156, { width: 4 }), text(80, 150, '480 V bus, SWGR-1', { size: 8.5, weight: 700 }),
    // feeders
    ...[[120, 'MCC-1', '400 A'], [250, 'MCC-2', '400 A'], [380, 'lighting T-2', '100 A']].map(([x, lab, amps]) => [line(x, 156, x, 170, { width: 1.6 }), ...S.breaker(x, 186), text(x + 10, 188, amps, { size: 8 }), line(x, 202, x, 214, { width: 1.6 }), text(x, 226, lab, { size: 8.5, anchor: 'middle', weight: 700 })]),
    // MCC-1 detail: two buckets
    line(80, 232, 240, 232, { width: 3 }), text(76, 244, 'MCC-1 bus', { size: 7.5, fill: C.muted, anchor: 'end' }),
    ...[[100, '3B', 'P-101', '25 hp'], [185, '3C', 'P-102', '25 hp']].map(([x, b, tag, hp]) => [line(x, 232, x, 240, { width: 1.4 }), ...S.breaker(x, 256).map((s) => s), line(x, 272, x, 276, { width: 0 }), text(x + 8, 252, b, { size: 7, fill: C.muted }), ...S.motorSym(x, 282, { r: 6 }).slice(0, 2), text(x + 10, 285, `${tag} ${hp}`, { size: 7 })]),
    note(330, 250, 'read down from the bus: breaker, MCC,\nbucket number, then the motor tag', { size: 8.5 }),
    caption(500, 320, 'The one-line names the bucket and breaker that feed the motor you are on.'),
  ], { title: 'One-line diagram extract' }))

// ================= Installation drawings =================
const gridBubble = (x, y, lab) => [circle(x, y, 10, { fill: C.paper }), text(x, y + 3.5, lab, { size: 9, anchor: 'middle', weight: 700 })]
const colSym = (x, y) => [rect(x - 5, y - 6, 10, 12, { fill: C.steel, width: 1 }), line(x - 5, y - 6, x + 5, y - 6, { width: 2 }), line(x - 5, y + 6, x + 5, y + 6, { width: 2 })]
const cl = (x1, y1, x2, y2) => line(x1, y1, x2, y2, { width: 0.8, dash: '12 3 2 3', stroke: C.muted })
fig('drawings/column-line-grid.svg', 'Equipment layout plan with column lines: lettered column lines A to D across the top, numbered lines 1 to 3 down the side, column symbols at the intersections, plant north arrow, and a pump base located by dimensions from column line B and column line 1',
  svg(500, 300, [
    ...[80, 190, 300, 410].map((x, i) => [line(x, 50, x, 262, { width: 0.8, stroke: C.line, dash: '10 4' }), ...gridBubble(x, 38, 'ABCD'[i])]),
    ...[80, 160, 240].map((y, i) => [line(60, y, 440, y, { width: 0.8, stroke: C.line, dash: '10 4' }), ...gridBubble(46, y, String(i + 1))]),
    ...[80, 190, 300, 410].flatMap((x) => [80, 160, 240].map((y) => colSym(x, y))).flat(),
    // pump base P-101 between B and C, 1 and 2
    rect(215, 96, 70, 44, { fill: C.grey }), text(250, 114, 'P-101', { size: 9, anchor: 'middle', weight: 700 }), text(250, 126, 'pump base', { size: 7.5, anchor: 'middle', fill: C.muted }),
    cl(205, 118, 295, 118), cl(250, 86, 250, 150),
    dim(190, 118, 250, 118, "5'-0\"", { off: 44, size: 9, side: -1 }), dim(250, 80, 250, 118, "3'-6\"", { off: 100, size: 9 }),
    // plant north
    line(455, 80, 455, 48, { width: 1.5, arrow: 'end' }), text(455, 42, 'N', { size: 10, anchor: 'middle', weight: 700 }), text(455, 92, 'plant', { size: 7.5, anchor: 'middle', fill: C.muted }),
    note(250, 282, 'locate every base from column lines, never from a wall or another machine', { anchor: 'middle', size: 9 }),
  ], { title: 'Column lines and equipment location' }))

const elMark = (x, y, lab, ly = y, jx = 50) => [line(x, y, x + jx, y, { width: 0.8, stroke: C.muted }), line(x + jx, y, x + jx, ly, { width: 0.8, stroke: C.muted }), line(x + jx, ly, x + 60, ly, { width: 0.8, stroke: C.muted }), path(`M${x + 60},${ly} l-6,-5 l0,10 z`, { fill: C.ink, width: 0.8 }), text(x + 64, ly + 3.5, lab, { size: 8.5 })]
fig('drawings/elevation-datums.svg', 'Section through a pump installation with the elevation callouts a millwright reads: benchmark and finished floor at the datum EL 100 ft 0 in, top of concrete, top of grout, top of baseplate steel and the shaft centreline, each with its elevation and abbreviation',
  svg(500, 280, [
    text(250, 18, 'Elevations read up from the plant datum', { anchor: 'middle', weight: 700, size: 12 }),
    // ground and floor
    hatchRect(30, 200, 300, 50, { stroke: 'none' }), line(30, 200, 330, 200, { width: 1.5 }),
    // foundation block, grout, baseplate, pump and motor
    hatchRect(100, 150, 180, 50), line(100, 150, 280, 150, { width: 1.5 }), line(100, 150, 100, 200, { width: 1.5 }), line(280, 150, 280, 200, { width: 1.5 }),
    rect(110, 138, 160, 12, { fill: C.soft, width: 1 }), plate(110, 128, 160, 10),
    rect(120, 92, 56, 36, { fill: C.grey }), text(148, 114, 'pump', { size: 8.5, anchor: 'middle' }), rect(196, 88, 64, 40, { fill: C.grey }), text(228, 112, 'motor', { size: 8.5, anchor: 'middle' }),
    cl(112, 100, 268, 100), text(108, 103, 'C/L shaft', { size: 7, anchor: 'end', fill: C.muted }),
    // benchmark
    poly([[52, 200], [64, 200], [58, 188]], { fill: C.ink, width: 0.8 }), text(58, 214, 'BM-1', { size: 8, anchor: 'middle', weight: 700 }),
    // elevation callouts on the right
    ...elMark(330, 200, "FIN FLR EL 100'-0\""), ...elMark(330, 150, "T/CONC EL 101'-8\"", 160, 56), ...elMark(330, 138, "T/GROUT EL 101'-9 1/2\"", 140, 48), ...elMark(330, 128, "T/STEEL EL 101'-10 1/2\"", 120, 40), ...elMark(330, 100, "C/L SHAFT EL 103'-2\""),
    dim(60, 200, 60, 100, "3'-2\"", { off: -20, size: 8.5, side: 1 }),
    note(250, 268, 'EL 100 is a convention, not a height above sea level; the benchmark carries it to the job', { anchor: 'middle', size: 8.5 }),
  ], { title: 'Elevation datums on a section' }))

fig('drawings/anchor-bolt-plan.svg', 'Anchor bolt plan and detail: plan of a pump foundation with four anchor bolts located from the pump centrelines and dimensioned bolt to bolt, plus a section detail of one bolt showing the pipe sleeve, embedment, projection above top of concrete and the anchor plate at the bottom',
  svg(500, 300, [
    text(120, 18, 'Anchor bolt plan', { anchor: 'middle', weight: 700, size: 11 }), text(370, 18, 'Bolt detail (section)', { anchor: 'middle', weight: 700, size: 11 }),
    rect(40, 40, 170, 200, { fill: C.grey, width: 1.2 }), text(125, 232, 'FDN F-101', { size: 7.5, anchor: 'middle', fill: C.muted }),
    cl(30, 140, 220, 140), cl(125, 30, 125, 250), text(222, 144, 'C/L pump', { size: 7, fill: C.muted }),
    ...[[75, 90], [175, 90], [75, 190], [175, 190]].map(([x, y]) => [circle(x, y, 6, { fill: C.paper }), circle(x, y, 2, { fill: C.ink }), line(x - 12, y, x + 12, y, { width: 0.6, stroke: C.muted }), line(x, y - 12, x, y + 12, { width: 0.6, stroke: C.muted })]),
    dim(75, 90, 175, 90, "4'-2\"", { off: -34, size: 8.5 }), line(197, 90, 197, 190, { width: 1, arrow: 'both' }), text(201, 124, "3'-4\"", { size: 8.5 }),
    dim(75, 190, 125, 190, "2'-1\"", { off: 30, size: 8.5, side: -1 }),
    text(125, 268, '4 x 1" dia x 30" AB, 4" proj., in 3" pipe sleeves', { size: 8.5, anchor: 'middle' }),
    // detail
    hatchRect(290, 120, 160, 130), line(290, 120, 450, 120, { width: 1.5 }), text(456, 124, 'T/CONC', { size: 7.5 }),
    rect(354, 120, 32, 70, { fill: C.paper, width: 1 }), text(392, 160, 'sleeve', { size: 7.5 }),
    rect(366, 60, 8, 180, { fill: C.steel, width: 1 }), rect(350, 236, 40, 6, { fill: C.steel, width: 1 }), text(396, 242, 'anchor plate', { size: 7.5 }),
    dim(330, 120, 330, 60, '4" proj.', { off: -16, size: 8, side: 1 }), dim(300, 120, 300, 240, '30" embed', { off: -8, size: 8, side: 1 }),
    note(370, 276, 'sleeve lets the bolt bend to the base hole, then gets grouted', { anchor: 'middle', size: 7.5 }),
  ], { title: 'Anchor bolt plan and detail' }))

fig('drawings/arrangement-drawing-extract.svg', 'General arrangement drawing extract of a conveyor drive: plan view of motor, coupling, gearbox and head pulley on a common base with equipment tags, centrelines, overall and setting dimensions, a shaft centreline elevation note and balloon numbers tied to a parts list',
  svg(500, 300, [
    text(250, 18, 'Drive arrangement CV-201 (plan)', { anchor: 'middle', weight: 700, size: 12 }),
    rect(60, 90, 250, 80, { fill: C.grey }), text(300, 182, 'base B-201', { size: 7.5, anchor: 'end', fill: C.muted }),
    rect(80, 105, 70, 50, { fill: C.paper }), text(115, 128, 'M-201', { size: 9, anchor: 'middle', weight: 700 }), text(115, 140, '30 hp 1780', { size: 7, anchor: 'middle', fill: C.muted }),
    rect(150, 122, 22, 16, { fill: C.steel, width: 1 }), rect(172, 100, 90, 60, { fill: C.paper }), text(217, 128, 'GB-201', { size: 9, anchor: 'middle', weight: 700 }), text(217, 140, '25:1', { size: 7, anchor: 'middle', fill: C.muted }),
    line(262, 130, 330, 130, { width: 4, stroke: C.steelDark }), rect(330, 60, 26, 140, { fill: C.paper }), text(343, 214, 'head pulley', { size: 7.5, anchor: 'middle' }),
    cl(70, 130, 370, 130), text(376, 133, 'C/L drive', { size: 7, fill: C.muted }),
    dim(60, 90, 310, 90, "8'-2\"", { off: -22, size: 8.5 }), dim(80, 155, 150, 155, "2'-4\"", { off: 30, size: 8.5 }), leader(320, 128, 322, 112, '3/16" gap', { size: 7.5, anchor: 'end' }),
    dim(330, 60, 356, 60, '', { off: 0, size: 1 }), text(343, 52, 'Ø24" x 42"', { size: 7.5, anchor: 'middle' }),
    callout(1, 90, 100), callout(2, 161, 112), callout(3, 182, 96), callout(4, 350, 190),
    legend(400, 80, ['motor', 'coupling', 'gearbox', 'pulley'], { size: 8.5, gap: 14 }),
    text(400, 150, 'C/L shaft EL 104\'-6"', { size: 8, weight: 700 }), text(400, 162, 'see F-201 for AB', { size: 7.5, fill: C.muted }),
    note(250, 246, 'set the gearbox first (it fixes the pulley), then bring the motor to it', { anchor: 'middle', size: 8.5 }),
    caption(500, 300, 'Tags, centrelines and balloons tie the plan to parts list and foundation.'),
  ], { title: 'General arrangement extract' }))

fig('drawings/baseplate-detail.svg', 'Baseplate and grout detail in section: concrete foundation with chipped top, anchor bolt in its sleeve, leveling jackscrew on a leveling plate, steel baseplate, the grout poured after alignment to the chamfered edge, and the dimensions usually shown',
  svg(500, 270, [
    text(250, 18, 'Base plate and grout detail', { anchor: 'middle', weight: 700, size: 12 }),
    hatchRect(60, 150, 380, 90), path('M60,150 l20,-3 l20,4 l20,-4 l20,3 l20,-4 l20,4 l20,-3 l20,4 l20,-4 l20,3 l20,-4 l20,4 l20,-3 l20,4 l20,-4 l20,3 l20,-4 l20,3', { width: 1.2 }), text(70, 234, 'chipped to sound concrete', { size: 7.5, fill: C.muted }),
    // grout with chamfer
    path('M90,150 L90,120 L100,110 L400,110 L410,120 L410,150 Z', { fill: C.soft, width: 1 }), text(250, 134, 'non-shrink grout', { size: 8.5, anchor: 'middle' }),
    // baseplate
    plate(100, 96, 300, 14), text(250, 106, 'baseplate', { size: 8, anchor: 'middle' }),
    rect(180, 60, 140, 36, { fill: C.grey }), text(250, 82, 'pump foot', { size: 8.5, anchor: 'middle' }),
    // anchor bolt with sleeve
    rect(140, 150, 24, 60, { fill: C.paper, width: 1 }), rect(148, 60, 8, 160, { fill: C.steel, width: 1 }), rect(140, 80, 24, 8, { fill: C.steelDark, width: 0.8 }), rect(142, 88, 20, 8, { fill: C.steel, width: 0.8 }),
    text(152, 54, 'AB', { size: 7.5, anchor: 'middle' }), text(168, 190, 'sleeve', { size: 7.5 }),
    // jackscrew and leveling plate
    rect(346, 96, 6, 44, { fill: C.steelDark, width: 0.8 }), rect(336, 140, 26, 6, { fill: C.steel, width: 0.8 }), rect(340, 88, 18, 8, { fill: C.steelDark, width: 0.8 }), text(372, 118, 'jackscrew on\nleveling plate', { size: 7.5 }),
    dim(420, 150, 420, 110, '1.5-2"', { off: 16, size: 8, side: 1 }), dim(420, 110, 420, 96, '3/4"', { off: 16, size: 8, side: 1 }), text(86, 108, '45° chamfer', { size: 7, fill: C.muted, anchor: 'end' }),
    note(250, 258, 'level and align on the jackscrews, grout, then back the screws off: the grout carries the load', { anchor: 'middle', size: 8.5 }),
  ], { title: 'Baseplate and grout detail' }))
