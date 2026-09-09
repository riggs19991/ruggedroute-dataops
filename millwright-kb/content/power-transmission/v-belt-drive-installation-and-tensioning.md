---
title: "V-Belt Drives: Sheave Alignment, Installation and Tensioning (Deflection Method)"
slug: v-belt-drive-installation-and-tensioning
category: power-transmission
kind: procedure
manufacturer: "Gates / Dodge / Browning (generic)"
model_numbers: ["A", "B", "C", "D", "3V", "5V", "8V", "AX", "BX", "5VX", "3VX"]
tags: [v-belt, belt tension, deflection, sheave alignment, pulley, belt drive, matched set, QD bushing, taper lock, belt slip, run-in]
source: "Gates Belt Drive Preventive Maintenance and Safety Manual; Dodge and Browning drive guides; general practice."
summary: "How to identify belts, check and align sheaves, install a matched set without prying, tension by the 1/64 inch per inch of span deflection method, and re-tension after run-in."
---

## Identify the belt

![A multiple V-belt drive: replace the whole set as a matched group](/photos/power-transmission/multi-v-belt-drive.jpg)

*A multiple V-belt drive: replace the whole set as a matched group. Photo: Three-quarter-ten, CC BY-SA 3.0, via commons*

| Section | Top width | Typical use |
|---|---|---|
| A / AX | 1/2" | Fractional to 10 hp |
| B / BX | 21/32" | 3 to 50 hp |
| C / CX | 7/8" | 15 to 200 hp |
| D | 1 1/4" | 50 hp and up |
| 3V / 3VX | 3/8" (narrow, wedge) | High speed, compact |
| 5V / 5VX | 5/8" | General industrial |
| 8V | 1" | Heavy industrial |

The number after the letter is the belt length: **A48** is an A-section belt about 48" long (inside length for classical; effective/outside length for narrow sections). **X** = cogged (notched) belt, runs cooler on small sheaves. Always replace multi-belt drives with a **matched set** (same maker, same batch code); a mixed set makes one belt carry the load.

## Inspect the sheaves

1. Run a **sheave groove gauge** in each groove. Any gap between the gauge and the groove wall over 1/32" means the groove is worn: the belt bottoms out and slips. Replace the sheave.
2. Check for cracks, rust, and burrs. A shiny groove bottom means belts have been bottoming.
3. Check the bushing (QD, Taper-Lock) is tight and the sheave runs true. Radial and axial runout under 0.005" per foot of diameter is a good target.

## Align the sheaves

Three kinds of misalignment: **angular** (shafts not parallel), **parallel/offset** (sheaves in different planes), **twist** (sheave tilted on its shaft).

- Straightedge (or a string) across both sheave faces should touch at **four points**: both edges of each sheave. Adjust by moving the motor or the sheave on its shaft.
- Laser sheave-alignment tools clip on and show all three errors at once.
- Target: **within 1/2°**, roughly **1/10" per foot** of centre distance. Misalignment wears one side of the belt and throws it.

## Install belts

1. Lockout/tagout. Remove the guard.
2. **Shorten the centre distance** by moving the motor on its slide rails or loosening the idler. **Never pry a belt over a sheave** with a screwdriver; it breaks the tensile cords and the belt fails early.
3. Slip the belts on by hand. Check each belt sits at the same depth in its groove.
4. Move the motor back to take up the slack, keeping the sheaves aligned. Snug the motor bolts.

## Tension - deflection method

![Deflection method: 1/64 in per inch of span, sheaves aligned with a straightedge](/img/power-transmission/v-belt-deflection.svg)

*Deflection method: 1/64 in per inch of span, sheaves aligned with a straightedge*

1. Measure the **span length** (the straight belt length between the two sheaves where they leave the groove), in inches.
2. Deflection target = **span ÷ 64**, i.e. **1/64" per inch of span**. A 32" span deflects 1/2".
3. Use a spring-scale belt tension tester (Gates Krikit or a pencil-style tester) at the **middle of the span**, pressing square to the belt. Read the force needed to reach the deflection.
4. Compare with the drive maker's table for the belt section and small sheave diameter. The table gives a **min** and **max** force. New belts are set to the **higher** (run-in) value. Example order of magnitude only, check your table: A-section on a 3-4" sheave ≈ 3-4 lb; B ≈ 5-7 lb; 5V ≈ 10-14 lb.
5. Tension until the force lands in the range. Too loose = slip, squeal, glazing, heat. Too tight = bearing overload, shaft deflection.
6. Rule of thumb when no table exists: the belt should feel like the tightest setting at which it does not slip under load, then a little more.

## Run-in and re-tension

- New belts seat into the grooves and stretch in the first **24 to 48 hours**. Re-check tension after the first day, then at the normal PM interval.
- Rotate the drive by hand a few turns after tensioning to seat the belts, then re-measure.

## Finishing

1. Re-check alignment after final tightening.
2. Torque motor bolts.
3. Replace the guard. Never run a belt drive unguarded.
4. Record belt part number, set size, tension force and date.

## Troubleshooting

| Symptom | Cause |
|---|---|
| Squeal on start | Low tension, or overloaded drive |
| Belts turn over in the groove | Misalignment, worn grooves, foreign material, excessive vibration |
| One belt slack in a set | Mismatched belts or a worn groove |
| Belt bottom cracked | Sheave too small, belt too hot, belt aged |
| Sidewall glazed/burnt | Slip: low tension, worn sheaves |
| Belt broken cleanly | Pried on, or shock load |
| Hot bearings on motor | Over-tensioned |

## Related

- [Roller chain drives](/article/roller-chain-drives)
- [Couplings: types, gap and installation](/article/coupling-types-gap-and-installation)
