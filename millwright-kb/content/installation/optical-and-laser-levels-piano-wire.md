---
title: "Optical and Laser Levels, Transits and Piano Wire: Builder's Level and Transit Setup, Two-Peg Test, Reading a Rod, Rotary Laser and Receiver, Transferring Elevations and Centrelines, Piano-Wire Alignment with the Sag Formula and Table, Bore Alignment of Multi-Bearing Housings, Plumb Bobs"
slug: optical-and-laser-levels-piano-wire
category: installation
kind: procedure
tags: [builders level, dumpy level, transit, theodolite, two peg test, leveling rod, grade rod, rotary laser, laser receiver, laser level, elevation transfer, benchmark, centerline transfer, piano wire, music wire alignment, wire sag, sag formula, wire alignment conveyor, bore alignment, bore sighting, line boring alignment, mandrel alignment, plumb bob, plumb line, optical tooling, jig transit, laser tracker, conveyor structure alignment, roll alignment]
source: "Builder's level and transit manuals (Topcon, Leica, David White) and the two-peg test; rotary laser operating guidance (Spectra, Leica); Brunson optical tooling and jig transit guidance; piano-wire sag derivation (catenary approximated by a parabola: sag = wL²/8T) with music-wire weights; Easy-Laser / Pruftechnik bore alignment guidance; millwright program manuals."
summary: "The tools for long-distance and multi-machine alignment where a spirit level and a straightedge cannot reach: setting up and checking an optical level or transit, reading a rod, using a rotary laser to carry an elevation around a plant or along a conveyor, stretching a piano wire as a straight-line reference with a computed sag correction, aligning bearing bores in line with a wire or a laser, and plumbing columns and vertical shafts with a plumb bob."
---

## Which tool

| Job | Tool |
|---|---|
| Carry one elevation around a room or along 200 ft of conveyor | **Rotary laser + receiver** (or an optical level and rod) |
| Set a line of bearings, rolls or idlers on a straight line and level | **Piano wire** (centreline and straightness), optical level (elevation), transit (straight line and square) |
| Establish a machine centreline and a 90° cross line on a floor | **Transit** (or a laser square / total station) |
| Check a long shaft or a line of bores for straightness | **Optical (jig) transit with targets**, laser bore alignment, or a wire with an inside micrometer |
| Plumb a column, a vertical shaft, a hanger line | **Plumb bob** (in oil), transit, laser plumb |
| Roll parallelism (paper machines, converting lines) | Optical tooling, laser roll alignment, or a wire and a **square** off the wire |
| Precision level of a single base | Master precision level (see [leveling](/article/leveling-and-machine-setting)) |

## Optical level (builder's / dumpy / automatic level)

![Optical level staff readings and piano wire sag](/img/installation/optical-level-and-wire.svg)

*Optical level staff readings and piano wire sag*

1. **Tripod**: legs spread, points pushed into the floor or on the concrete, head roughly level by eye, at a comfortable eye height; instrument screwed on snug.
2. **Level the instrument**: with the three (or four) levelling screws, centre the circular bubble; on an automatic level the compensator does the rest; on a dumpy level, align the tube vial over two screws, centre, rotate 90°, centre with the third, repeat until the bubble stays centred through a full rotation.
3. **Focus**: eyepiece on the crosshairs first (against a white card), then the objective on the rod. Parallax check: move your eye; the crosshair must not shift on the rod.
4. **Reading a rod**: the horizontal crosshair reads the rod (feet and hundredths on an engineer's rod: "4.32" = 4.32 ft; feet-inches-eighths on a builder's rod). The rod must be **plumb** (rod level, or the rodman rocks it slowly and you take the **lowest** reading). Stadia hairs give distance: (upper − lower) × 100 = distance in the rod's units.
5. **Height of instrument (HI)** = benchmark elevation + rod reading on the benchmark (the backsight). **Elevation of any point** = HI − rod reading on that point (the foresight). To set a mark at a required elevation, raise or lower a target until the reading = HI − required elevation.
6. Keep foresight and backsight distances similar to cancel instrument error; **do not touch the tripod**; re-check the backsight at the end of every setup (the reading must repeat within 0.01 ft or 1/16").

**Two-peg test** (checks the line of sight is level; do it monthly and after a knock): drive two pegs 100 ft apart; set up **midway** and read both (the difference is the true difference in elevation, whatever the instrument error); set up **close to peg A** (within 10 ft), read A and B; the difference now should match the first within 1/16" per 100 ft (0.005 ft); if not, the instrument needs adjustment (crosshair or compensator).

## Transit / theodolite

Same setup and levelling, plus a vertical circle and a horizontal circle. Uses: a **straight line** (sight a far target, lock the horizontal motion, plunge the scope up and down: every point on that vertical plane is on the line; lay out a machine centreline this way and mark it on the floor and on the wall), a **90° line** (turn exactly 90° on the circle: better than 3-4-5 over long distances), **plumbing** a column (sight the base, elevate the scope: the crosshair should stay on the column's edge; check from two directions 90° apart), and elevations like a level when the scope is levelled. A **jig transit** (optical tooling) has a telescope that can be aligned to a wire or a target line and an optical micrometer to read offsets to 0.001": the tool for long-line shaft and roll alignment in paper mills, though laser trackers have taken over.

## Rotary laser and receiver

1. Tripod or a stand on solid ground away from traffic and vibration; self-levelling lasers need to be within their range (±5°) or they blink an error; check the **out-of-level alarm** is on (if the tripod is bumped the laser stops rather than lying).
2. **Calibration check** (like the two-peg): mark the beam on a wall at 50-100 ft, rotate the laser 180° and mark again; the marks should be within the accuracy spec (**±1/16" at 100 ft** for good construction lasers, ±1/8" for cheap ones); check both axes.
3. Receiver on a **grade rod** or held against the steel; move it up and down until it beeps "on grade"; the receiver's mark is at the beam height. Read the rod, or mark the steel.
4. To carry an elevation: put the receiver on the benchmark, note the rod reading (the beam height above the benchmark); at the target point, set the receiver so it reads the same, and the mark is at the benchmark elevation; add or subtract the required difference.
5. For a long conveyor: the laser at one end, the receiver on every stringer at every bent; mark, and compare with the drawing's grade (a 1% grade rises 1.2" per 10 ft).
6. Sun and heat shimmer widen the beam at long range; the beam's accuracy degrades over 300 ft; re-set up halfway.

Laser levels in **line mode** (a static line) and **laser squares** put an accurate 90° on a floor for layout; a **laser plumb** (5-point laser) transfers a floor point to the ceiling or a beam above.

## Piano wire

A stretched steel wire is a straight line to within the sag, which you can calculate and correct for. Used for: conveyor structure centrelines, lines of pillow blocks and hanger bearings, kiln and dryer roller alignment, checking a long bed or way for straightness, and centring a shaft in a line of bores.

**Setup**

1. Wire: **music (piano) wire 0.015-0.025"** (0.4-0.6 mm), new, unkinked; anchored at one end to a fixed bracket or clamp with the wire wrapped on a small drum, and tensioned at the other end over a **pulley with a weight**, or with a turnbuckle and a spring scale. Tension to about **60-70% of the wire's breaking strength** (0.020" music wire breaks at about 100-110 lb; use **40-60 lb**); a wire at low tension sags too much and swings.
2. Keep the wire away from anything it might touch; **the wire is straight in the horizontal plane and sags in the vertical plane**: use it for horizontal (side-to-side) alignment directly, and correct for sag when using it vertically.
3. Measure from the wire with an **inside micrometer or a depth micrometer with a light-contact indicator**: a battery, a buzzer or a small light in series with the wire and the micrometer tells you when the tip just touches (you cannot feel it, and pushing the wire moves it). Or use a dial indicator with a fork that straddles the wire on a mag base.
4. Set the wire on the **design centreline**: measure from two fixed reference points (columns, the head shaft's bearing centres) at each end and adjust the end brackets; read intermediate points as offsets from the wire.

**Sag**

```
   sag at mid-span  S = w × L² ÷ (8 × T)        w = wire weight per unit length, L = span, T = tension  (consistent units)
   sag at distance x from one end  s(x) = 4 × S × x × (L − x) ÷ L²     (parabola)
   music wire weight w (lb/in) = 0.283 × π/4 × d²   (d in inches)
```

| Wire Ø | w (lb/ft) | Span 50 ft, T 40 lb | Span 100 ft, T 40 lb | Span 100 ft, T 60 lb | Span 200 ft, T 60 lb |
|---|---|---|---|---|---|
| 0.015" | 0.00060 | 0.056" | 0.225" | 0.150" | 0.60" |
| **0.020"** | **0.00107** | **0.100"** | **0.400"** | **0.267"** | 1.07" |
| 0.025" | 0.00167 | 0.156" | 0.625" | 0.417" | 1.67" |
| 0.031" | 0.00256 | 0.240" | 0.961" | 0.641" | 2.56" |

(Inches of sag at mid-span; S = w L² / 8T with w in lb/ft, L in ft, T in lb gives feet; ×12 for inches.) Halve the span or double the tension to reduce sag; thinner wire sags less at the same tension. The sag correction at any point is s(x) above; note that the **weight on the pulley end is the tension** (minus pulley friction: use a good ball-bearing pulley, or a calibrated spring scale on a turnbuckle).

**Worked example**: a line of 6 pillow blocks over 60 ft, 0.020" wire at 50 lb. S = 0.00107 × 60² ÷ (8 × 50) = 3.852 ÷ 400 = 0.00963 ft = **0.116"** at mid-span. At a bearing 15 ft from the end: s = 4 × 0.116 × 15 × 45 ÷ 3600 = **0.087"**. If you set the wire at the bearing-centre height at both ends, that bearing's centre must be 0.087" **below** the wire height reading, or, easier, use the wire only for horizontal position and a level or laser for elevation.

## Aligning bearing bores in line (line boring, multi-bearing housings)

1. **Wire method**: wire through all the bores, centred in the two end bores with an inside micrometer (measure 4 points at each end: top, bottom, left, right; adjust until equal); then at each intermediate bore measure the 4 points: the bore's offset from the line = half the difference of opposite readings, corrected for sag vertically. Bores are shimmed or re-bored to bring the offsets to zero (typical target ± 0.002-0.005"; the bearing maker's misalignment limit for the bearing type decides).
2. **Mandrel / dummy shaft** with dial indicators for short lines (3 bores): a ground bar through the bores, indicators at each bore.
3. **Laser bore alignment** (Easy-Laser, Pruftechnik): a laser in one end bore, a detector on a self-centring fixture in each other bore; reads offset and angle directly and handles sag-free; the modern answer for engine blocks, stern tubes, extruder barrels, kiln trunnions.
4. **Optical**: jig transit sighted through targets centred in each bore; 0.001" over 50 ft.

## Plumb bob

For a vertical shaft, a column, a hoist rope line, a vertical pump: hang a plumb bob on a fine line from the top point, **damp it in a can of oil** (it swings for minutes otherwise), let it settle, measure from the line to the object at top and bottom with a rule; the difference over the height is the out-of-plumb. Wind ruins it: use a laser plumb or a transit outdoors. Vertical shafts on long pumps and agitators: the plumb bob from the top bearing centre through the bottom bearing centre, inside micrometer to the line.

## Common mistakes

- Reading a rod that is not plumb: every reading is high.
- Moving the tripod (or leaning on it) between backsight and foresight.
- Laser used beyond its range or in shimmer: 1/4" errors at 300 ft.
- Wire touching something along the way (a guard, a chip): the line has a kink.
- Ignoring sag on a 100 ft wire used for elevation: the middle bearing is set 3/8" low.
- Pushing the micrometer into the wire until you "feel" it: the wire has moved 0.010" by then.
- Plumb bob in wind or not damped: 1/8" guesses.

## Related

- [Leveling and machine setting](/article/leveling-and-machine-setting)
- [Belt conveyor components and tracking](/article/belt-conveyor-components-and-tracking)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
- [Dial indicator use](/article/dial-indicator-use)
- [Trig and layout formulas](/article/trig-and-layout-formulas)
