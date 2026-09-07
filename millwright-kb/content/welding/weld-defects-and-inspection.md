---
title: "Weld Defects and Visual Inspection: Porosity, Undercut, Overlap, Lack of Fusion, Cracks, Arc Strikes; AWS D1.1 Visual Acceptance Numbers, Fillet Gauges, Dye Penetrant and Mag Particle Basics, NDT Overview"
slug: weld-defects-and-inspection
category: welding
kind: reference
tags: [weld defects, weld discontinuities, porosity, undercut, overlap, cold lap, lack of fusion, incomplete penetration, slag inclusion, crater crack, hot crack, cold crack, arc strike, spatter, convexity, reinforcement, visual inspection, VT, fillet gauge, undercut gauge, hi-lo gauge, bridge cam gauge, dye penetrant, PT, magnetic particle, MT, ultrasonic, UT, radiography, RT, D1.1 acceptance, bend test]
source: "AWS D1.1/D1.1M Structural Welding Code, Steel, Table 8.1 (visual inspection acceptance criteria) and Clause 7 weld profiles; AWS B1.11 Guide for the Visual Examination of Welds; AWS D1.1 Clause 6 bend test criteria; G.A.L. Gage Company gauge instructions; ASTM E165 (PT) and E709 (MT)."
summary: "Each common weld discontinuity with its causes and fix, the D1.1 visual acceptance limits you can measure with a gauge (undercut, porosity, reinforcement, convexity, undersize), how to use fillet, undercut and hi-lo gauges, what dye penetrant and mag particle testing can find and how to run them, what UT and RT add, and the bend test that qualifies a welder."
---

## Discontinuity vs defect

A **discontinuity** is any interruption in the weld; it becomes a **defect** only when it exceeds the acceptance criteria of the code, drawing or WPS you are working to. Visual inspection (VT) is the first and cheapest test and finds most surface problems if it is done before the weld is painted.

## The defects and their causes

| Defect | What it looks like | Main causes | Fix |
|---|---|---|---|
| **Porosity** (surface, cluster, linear, piping/wormhole) | Round holes, elongated holes at the surface, "worm tracks" | Gas shielding lost (low/high flow, wind, leak, clogged nozzle, wrong gas), contaminated base (rust, oil, paint, galvanising, moisture), damp electrodes, long arc, wrong polarity on flux-core, too fast travel | Fix the gas and the cleaning first; rods from the oven; polarity check; shorten arc |
| **Undercut** | Groove melted into the base metal at the toe, not filled | Amps/volts too high, travel too fast, wrong angle (too steep), too long an arc, weaving without pausing at the toes, wrong electrode for the position | Lower heat, slower, pause at toes, shorter arc, correct work angle (horizontal fillet: aim at the bottom plate) |
| **Overlap (cold lap)** | Weld metal lying on the plate without fusing at the toe | Too cold, too slow, too much wire for the heat, wrong angle, oxide on aluminium | More heat, faster, correct angle, clean |
| **Incomplete (lack of) fusion** | Weld not fused to the sidewall or the previous bead; shows as a fine line, often only on cutting or UT | Too cold, arc not on the leading edge, oxide/scale, too big a puddle rolling ahead (MIG short-circuit on thick plate), wrong push angle, mill scale | More heat/spray mode, correct arc position, clean, smaller puddle |
| **Incomplete penetration** | Root not fused through on a full-pen joint; visible as a gap or unfused edge on the back side | Root gap too small, land too thick, electrode too big for the gap, too cold, wrong angle | Fix fit-up, smaller electrode, more heat, back-gouge and re-weld |
| **Slag inclusion** | Dark non-metallic pockets, usually between passes or at the toes | Not cleaning between passes, welding over slag, too cold, undercut in the previous pass trapping slag, wrong angle letting slag run ahead (vertical-down with 7018) | Chip and brush every pass, hotter, fill undercut, correct angle |
| **Cracks** (crater, longitudinal, transverse, toe, root, underbead/HAZ) | Line, often only visible with penetrant | Crater: stopping without filling. Hot/solidification: high restraint, deep narrow bead, sulphur/phosphorus, wrong filler (aluminium, stainless 310). Cold/hydrogen: see [preheat](/article/preheat-interpass-and-carbon-equivalent). Toe: stress concentration + hardness | Fill craters, convex beads, preheat, low-hydrogen, correct filler, grind toes; **all cracks are rejectable in every code**: remove completely and re-weld |
| **Arc strikes** | Small melted spots outside the weld | Striking outside the joint, ground clamp arcing | Grind out to sound metal, check for cracks (they are hard spots that crack under fatigue); rejectable on code work |
| **Spatter** | Balls stuck to the plate | Long arc, wrong voltage, globular transfer, damp rods, wrong polarity, CO2 | Not a defect by itself but must be removed for inspection and coating |
| **Excessive convexity / reinforcement** | Weld standing too high; ropey | Too cold, too slow, too much wire | Hotter, faster, less WFS; grind flush if the drawing says |
| **Concavity / undersize** | Fillet throat too thin, groove face below plate | Too hot and fast on a fillet, vertical-down, wrong size electrode | Add a pass |
| **Burn-through** | Hole | Too hot, gap too wide, thin material | Lower heat, backing, smaller wire, weave the edges |
| **Distortion / misalignment** | Out of square, hi-lo | See [distortion](/article/distortion-control) | |
| **Tungsten inclusion** (TIG) | Bright white spot on RT; dipped tungsten | Touching the tungsten to the puddle or filler, too much current for the tungsten | Regrind, larger tungsten |

## D1.1 visual acceptance criteria (Table 8.1, the numbers you can gauge)

| Item | Statically loaded (buildings) | Cyclically loaded (bridges, cranes) |
|---|---|---|
| Cracks | **None** | None |
| Fusion | Complete between weld and base metal and between passes | Same |
| Craters | Filled to the full cross-section, except ends of intermittent fillets outside the effective length | Same |
| **Undercut** | Material < 1" thick: ≤ **1/32" (1 mm)**, except ≤ 1/16" for any accumulated 2" in any 12". Material ≥ 1": ≤ **1/16" (2 mm)** any length | Primary members transverse to tensile stress: ≤ 0.01" (0.25 mm); others ≤ 1/32" |
| **Porosity** | Fillet welds: visible piping porosity ≤ 3/8" total diameter in any linear inch and ≤ 3/4" in any 12". CJP groove butt welds transverse to tensile stress: **no visible piping porosity**. Other groove welds: as fillets | Fillet in stiffeners to web: ≤ 3/8" per inch, 3/4" per 12"; CJP groove: none |
| Reinforcement (groove face) | ≤ **1/8" (3 mm)** above the plate, gradual transition | Same |
| Fillet convexity | Face width ≤ 5/16": max convexity 1/16"; 5/16" to 1": 1/8"; > 1": 3/16" | Same |
| Undersize fillet (D1.1 7.23) | Allowed 1/16" under for ≤ 3/16" fillets, 3/32" under for 1/4", 1/8" under for ≥ 5/16", on **≤ 10% of the weld length**; never at the ends of web-to-flange welds | Same |
| Weld profiles | No overlap; toes blend | |
| Time of inspection | Any time; **A514/A517 and other Q&T steel: not less than 48 hours after completion** | |

Other codes differ: ASME B31.3 normal fluid service allows undercut ≤ 1/32" or T/4 whichever less and reinforcement by wall thickness; API 1104 has its own pipe tables. Use the drawing's governing code.

## Gauges

| Gauge | Measures | How |
|---|---|---|
| **Fillet weld gauge** (set of 7-12 blades, or the "multi" gauge) | Leg length and throat of a fillet | Set the leg blade in the corner: both edges must touch the plates with the tip touching the weld face for the leg size marked. The concave/throat side of the blade checks a flat/concave weld's throat |
| **Bridge cam (multipurpose) gauge** | Reinforcement height, fillet leg, throat, undercut depth, misalignment, bevel angle 0-60° | Rest the two feet on the plate, rotate the pointer to touch the weld; read the scale in the window |
| **V-WAC / undercut gauge** | Undercut depth, porosity size, crown height | Pin depth reads in 1/32" or mm; the porosity holes are 1/16-1/8" comparators |
| **Hi-lo gauge** | Internal and external pipe misalignment, root gap | Put the two blades inside the pipe and pull them against the wall each side; read the difference. Also has wall-thickness and gap scales |
| **Automatic weld size (AWS) gauge** | Fillet leg and throat | Slide the pointer until it touches the weld face |
| Taper gauge | Root gap | Push into the gap until it stops |
| Bevel protractor / angle gauge | Bevel angle | Before welding |
| Pit gauge | Depth of corrosion/undercut | |
| Straightedge and feeler | Flatness, hi-lo on plate | |
| Temp sticks / contact pyrometer | Preheat, interpass | Before every pass |

A fillet gauge reads **the smaller leg**. A 1/4" fillet with one leg 1/4" and the other 3/16" is a 3/16" fillet.

## Inspection sequence

1. **Before welding**: material ID, fit-up (gap, bevel, land, hi-lo), cleanliness, tack quality, preheat, consumable class and storage, machine settings against the WPS.
2. **During**: interpass temperature, interpass cleaning, bead placement, root pass before it is covered (this is the only time you will see it), travel and technique.
3. **After**: clean (chip, brush, no paint), lighting (flashlight at a low angle shows undercut and cold lap), magnification 2-5× for cracks, gauges on size and profile, mark defects with paint stick, record.
4. Delayed inspection on crack-sensitive steel: 48 h.

## Dye penetrant (PT) for surface cracks

Works on any non-porous material (steel, stainless, aluminium, cast iron), finds only **surface-breaking** defects.

1. Clean: solvent (cleaner/remover), no paint, no rust, no oil; let it dry fully. Do not sandblast or heavily grind first (it smears metal over cracks); if you grinded, etch or wait.
2. Apply **penetrant** (red, visible type): spray or brush a thin film; **dwell 5-10 minutes** (10-30 on aluminium and castings; longer when cold; 50-125°F surface range for most kits).
3. Remove excess: wipe with a **dry** lint-free rag, then a rag **dampened** with cleaner. Never spray cleaner on the surface (it washes the penetrant out of the crack).
4. Apply **developer** (white): a thin, even, translucent coat from 8-12"; heavy coats hide indications.
5. Read at **1 minute to 10 minutes** under good light: a red line is a crack; red dots are porosity; a diffuse bleed is a wide shallow discontinuity. Re-read after 10-30 minutes for tight cracks.
6. Clean off developer before welding repairs (it contaminates the weld) and before painting.

## Magnetic particle (MT) for ferrous surfaces

Finds surface and slightly subsurface (to about 1/8") cracks in **ferromagnetic** steel only (not austenitic stainless or aluminium). A **yoke** (AC for surface, DC/HWDC for subsurface) is placed across the area; with the legs 3-8" apart the field runs between them, so cracks **perpendicular to the leg line** show; do it twice at 90°. Dust dry powder (visible, grey/red) while the yoke is energised and blow off the excess gently, or use wet fluorescent particles under UV. A crack collects a tight line of particles. Check the yoke lifts a **10 lb** weight (AC) or 40 lb (DC) as the daily calibration.

## UT and RT

- **Ultrasonic (UT)**: a probe sends sound into the plate; reflections from planar defects (lack of fusion, cracks) and their depth are read on the screen. Best for thick welds, finds planar defects RT misses, needs a certified operator and access to one side.
- **Radiography (RT)**: X-ray or gamma film/digital image through the weld; finds volumetric defects (porosity, slag, incomplete penetration) as dark spots; cracks and lack of fusion only if aligned with the beam. Radiation exclusion zone: leave when the technician says.
- **Phased-array UT** replaces RT on much pipe and plate work.
- Millwright's job: cleanliness, access, surface finish (grind the cap flush if the drawing says "UT" or "RT"), and marking the weld ID and datum.

## Welder qualification bend test (what the coupon must do)

Guided bend of root and face (or side bends on thick plate) around a 1.5" radius mandrel for mild steel: **no open discontinuity over 1/8" (3 mm)** in any direction on the convex surface, and the sum of all discontinuities between 1/32" and 1/8" not over 3/8"; corner cracks up to 1/4" ignored unless they come from slag or fusion defects (D1.1 Clause 6). Cut the coupon: remove reinforcement flush, grind marks lengthwise, radius the corners 1/16", and never quench the coupon.

## Common mistakes

- Painting or grinding before inspection.
- Reading a fillet gauge on the larger leg.
- Accepting a "little crater crack" on stainless: it opens up in service.
- Spraying penetrant cleaner directly on the test area during removal.
- Yoke placed parallel to the expected crack: no indication.
- Calling porosity "surface only" without checking with a gauge; piping porosity goes to the root.

## Related

- [Positions and techniques](/article/positions-and-techniques)
- [Joint design and fit-up](/article/joint-design-and-fit-up)
- [Preheat, interpass and carbon equivalent](/article/preheat-interpass-and-carbon-equivalent)
- [Welding symbols](/article/welding-symbols)
- [MIG setup](/article/gmaw-mig-setup) and [stick setup](/article/smaw-stick-setup) troubleshooting tables
