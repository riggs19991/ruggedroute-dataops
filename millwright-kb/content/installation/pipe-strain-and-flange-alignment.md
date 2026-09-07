---
title: "Pipe Strain and Flange Alignment: Why Pipe Strain Wrecks Pumps, API 686 Flange Fit-Up Limits (Parallelism, Offset, Bolt-Hole, Gap), the Dial-Indicator Pipe Strain Test (0.002\" Limit), Fixing Strain (Spring Hangers, Cutting and Rewelding, Expansion Joints), Thermal Growth of Piping, Supports and Hangers"
slug: pipe-strain-and-flange-alignment
category: installation
kind: procedure
tags: [pipe strain, pipe stress, flange alignment, flange parallel, flange offset, bolt hole alignment, flange gap, pipe strain test, dial indicator pipe strain, 0.002 pipe strain, API 686 pipe strain, pump nozzle loads, spring hanger, pipe support, pipe hanger, expansion joint, expansion loop, thermal growth piping, pipe anchor, pipe guide, flange bolting sequence, pump piping, suction piping, discharge piping, nozzle load]
source: "API RP 686 Chapter 6 (piping to machinery: flange fit-up tolerances and the shaft-movement test of 0.002 in / 0.05 mm); API 610 nozzle load criteria (Annex F); Hydraulic Institute ANSI/HI 9.6.2 (pump piping); pump manufacturer installation manuals (Goulds 3196, Flowserve); Piotrowski, Shaft Alignment Handbook; ASME B31.3 flange alignment guidance."
summary: "What pipe strain is and what it does to bearings, seals and alignment, the flange fit-up numbers you must meet before the bolts go in, how to run the dial-indicator test that proves the piping is not pulling the pump, what to do when it fails, how to support pipe with hangers, guides, anchors and spring supports so thermal growth does not load the machine, and the suction and discharge piping rules that keep a pump alive."
---

## What pipe strain is

A pipe flange that does not meet the pump's nozzle square, level and centred is **forced** to it with the bolts. The pump casing is now a spring: the bearing housing bends, the shaft is pulled out of line with the motor, the mechanical seal faces open, the impeller rubs the wear ring, and the coupling sees a misalignment that changes every time the pipe warms up. Pipe strain is the leading cause of "we aligned it last week and it moved" and of repeat seal failures on the same pump. API 610 limits the forces and moments a pump nozzle can take, and API 686 gives the field tests; the pump does not know or care what the piping designer intended.

Signs: a pump that will not stay aligned; alignment readings that change when the flange bolts are loosened; a bearing housing that moves when the pipe is unbolted; seals failing on one pump repeatedly; the coupling gap changing between cold and hot; cracked pump feet or a broken casing flange.

## Flange fit-up limits (API 686 practice, before bolting)

| Check | Limit |
|---|---|
| **Flange face parallelism** (gap difference across the diameter, measured with feelers at 4 points) | **≤ 0.001" per inch of flange OD** (a 10" OD flange: 0.010"), and never over about 1/32" total |
| **Flange face separation** (gap) | Gasket thickness ± 1/16" (about 1/32" per side): the pipe must not be pulled in to close a gap or pushed out |
| **Concentricity (offset of bore centres)** | ≤ 1/32" (0.8 mm) |
| **Bolt-hole alignment** | All bolts slide through **by hand** with the flange loose; rotational offset ≤ 1/16" |
| **Pipe-to-pump flange contact** | Faces flat and clean, no forcing with a spud wrench, no come-along to pull the pipe to the pump |
| Spring hangers | Pinned (locked) during fit-up, released before the strain test and start-up, set to the cold load |

The **cardinal rule**: the piping must fit the pump **with all bolts loose and no external force**. If a bolt has to be drawn in with a wrench, or a flange pulled with a chain fall, the fit is wrong.

## The pipe strain test

1. Pump on its base, aligned (rough or final), hold-down bolts torqued; piping flanged up loosely.
2. Mount **two dial indicators** (or the laser alignment heads) on the pump's **bearing housing or shaft**, reading against a fixed reference (the baseplate or the motor shaft), one in the **vertical** and one in the **horizontal**; zero them. Better: indicators on the pump shaft end reading vertical and horizontal, and a third indicator axial.
3. **Tighten the flange bolts** in the proper pattern to full torque (suction first, then discharge, or one at a time) while watching the indicators.
4. **Limit: 0.002" (0.05 mm)** movement in any direction (API 686). Movement above that = pipe strain; the fit-up must be corrected, not "aligned out" (the strain changes with temperature and the machine will not stay aligned).
5. Repeat after the piping is **hot** if the system runs hot: thermal growth of the piping loads the pump differently; a hot test is the real one on hot-oil, boiler-feed and steam-traced lines.
6. Also **loosen** a suspect existing installation's flanges with indicators on the shaft: if the shaft springs more than 0.002", you have found the reason the alignment never held.

Record the readings on the installation sheet.

## Fixing pipe strain

| Cause | Fix |
|---|---|
| Flange out of parallel (the pipe comes in at an angle) | Cut the pipe back and re-weld the flange square, using a flange-alignment tool or a level and a square; a **field-fit weld** left in the spool for this purpose |
| Offset (pipe centre not on the nozzle centre) | Cut and re-fit a spool; two 45° elbows to make up a small offset; **never** a tapered flange or a bent pipe |
| Gap too big or too small | Cut and re-fit the closing spool with the correct gasket space; **never** stack gaskets |
| Pipe too short, pulled to the pump | Re-cut a longer spool |
| Bolt holes misaligned (rotated) | Rotate a flange by cutting and re-welding (two-hole it); never oval the holes |
| Dead weight hanging on the nozzle (unsupported valves, strainers) | Add a **support** within 1-2 pipe diameters of the nozzle, adjustable, set to carry the pipe's weight |
| Thermal growth pushing on the pump | **Expansion loop**, expansion joint (with tie rods or anchors to take the pressure thrust), **spring hangers** set for the cold-to-hot travel, anchors and guides so the growth goes away from the pump |
| Vibrating piping loading the pump | Supports and snubbers; fix the source (cavitation, pulsation) |
| Piping settled after years | Re-support; re-check the strain |

## Thermal growth of piping

```
   growth ΔL = L × α × ΔT
   carbon steel  α ≈ 0.0000065 /°F  → 0.78" per 100 ft per 100°F
   stainless 304 α ≈ 0.0000096 /°F  → 1.15" per 100 ft per 100°F
   copper        α ≈ 0.0000094 /°F
   PVC/CPVC      α ≈ 0.00003-0.00004 /°F (5× steel)
```

A 50 ft carbon-steel discharge line going from 70°F to 250°F grows 50 × 0.0000065 × 180 = **0.059" (1/16")**: enough to load a pump nozzle heavily if the line is anchored at the far end and rigid at the pump. Steam and hot-oil lines at 400-600°F grow inches: they need loops or joints designed by an engineer, and the pump must be on the anchored side or the growth must be absorbed before it reaches the pump.

## Supports, hangers, guides and anchors

| Support | Function | Notes |
|---|---|---|
| **Rigid hanger / rest support** | Carries weight; allows small sliding | Within 1-2 diameters of the pump nozzle for valves and strainers; on both sides of heavy items; spacing from the code span table (about 7 ft for 1", 10 ft for 2", 14 ft for 4", 17 ft for 6", 19 ft for 8" water-filled steel; less for plastic) |
| **Adjustable support (screw, turnbuckle)** | Lets you set the pipe exactly to the nozzle | Set it to **just carry the pipe** with the flange bolts loose and the gap right, then lock the jam nut |
| **Spring hanger (variable)** | Carries weight while the pipe moves vertically with temperature | Cold and hot settings marked on the can; **pinned** during installation, pins pulled before the strain test/start-up; a spring "topped out" or "bottomed out" is a rigid support |
| Constant-load hanger | Large vertical travel | Engineered |
| **Guide** | Allows axial movement, stops lateral | Along expansion runs |
| **Anchor** | Fixes the pipe completely | Decides which way the growth goes: put it so growth goes **away** from the pump |
| Snubber / sway brace | Stops vibration and shock, allows slow thermal motion | Reciprocating compressor and pulsating lines |
| Expansion joint (bellows) | Absorbs axial/lateral movement | Must have **tie rods or external anchors**: the pressure thrust (pressure × bellows area) otherwise pushes the pump off its base |

Never let the pump be the anchor for the piping. Never leave the weight of a valve or a strainer on the nozzle. Never remove a support "temporarily".

## Suction and discharge piping rules (Hydraulic Institute / pump makers)

- Suction pipe **one or two sizes larger than the suction nozzle**; **eccentric reducer flat side up** (horizontal suction) so no air pocket forms at the pump; 5-10 diameters of straight pipe before the suction nozzle (3 minimum with a long-radius elbow; an elbow feeding a double-suction pump must be in the plane perpendicular to the shaft); no elbow bolted straight to the suction nozzle.
- Suction line continuously rising to the pump (no high points that trap air) on a lift; continuously falling from a flooded source; no valves on the suction except an isolation gate valve (full open); a strainer with a ΔP gauge during commissioning.
- Discharge: check valve then isolation valve; a concentric reducer/increaser at the nozzle; supports for both.
- Piping tied to the pump only after the [alignment](/article/shaft-alignment-fundamentals) rough-in, and checked with the strain test; **final alignment after the piping is connected and the strain test passed**.

## Common mistakes

- Pulling a 1/4" gap closed with the bolts "because the gasket will take it".
- Ovalling flange holes with a torch to make the bolts go in.
- Aligning the pump with the piping bolted and never testing whether the piping is holding it there.
- A spring hanger left pinned (rigid) for the life of the plant.
- Strainer and valve hanging on the suction nozzle with no support.
- Concentric reducer on a horizontal suction: air pocket, cavitation, the seal fails.
- An expansion joint with no tie rods on a 100 psi 8" line: 5,000 lb of thrust on the pump.

## Related

- [Leveling and machine setting](/article/leveling-and-machine-setting)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals) and [thermal growth in alignment](/article/thermal-growth-alignment)
- [Mechanical seal replacement](/article/mechanical-seal-replacement-centrifugal-pump)
- [Pump and fluid-power formulas (NPSH)](/article/pump-and-fluid-power-formulas)
- [Flange bolting and gaskets](/article/flange-bolting-and-gaskets)
- [Pipe miter layout and take-outs](/article/pipe-miter-layout)
