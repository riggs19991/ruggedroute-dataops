---
title: "Timing Belts and Synchronous Drives: Pitch Families (XL/L/H, HTD 3M-14M, GT, Poly Chain), Reading a Belt Number, Sprocket Flanges, Installation Without Prying, Tensioning by Deflection and Sonic Meter, Alignment Tolerances and Laser Sheave Alignment, Failure Signs"
slug: timing-belts-and-synchronous-drives
category: power-transmission
kind: procedure
manufacturer: Gates / Goodyear (Continental) / Optibelt (generic)
model_numbers: ["PowerGrip GT4", "PowerGrip HTD", "Poly Chain GT Carbon", "Gates 507C", "Gates Sonic Tension Meter", "Eagle Pd", "Falcon Pd", "Optibelt Omega"]
tags: [timing belt, synchronous belt, toothed belt, HTD belt, 8M belt, 14M belt, GT belt, Poly Chain, timing belt pitch, belt number decoder, timing belt tension, deflection method, sonic tension meter, timing belt alignment, sprocket alignment, laser sheave alignment, belt tracking on sprocket, flanged sprocket, timing belt failure, tooth shear, ratcheting, belt install, timing pulley]
source: "Gates PowerGrip GT and HTD drive design manuals (belt designations, tensioning, installation tension force-deflection tables and the sonic method); Gates Belt Preventive Maintenance and Safety Manual (alignment tolerances, failure analysis); Continental ContiTech synchronous belt guidance."
summary: "The belts that drive with teeth instead of friction: the pitch families and how to read the numbers on a belt and a sprocket, why flanges and alignment matter more than on a V-belt, how to install without damaging the tensile cords, how to tension (the deflection method with the span formula and the sonic meter that most plants now use), the alignment tolerance and how to hit it with a laser, and how to read a failed belt."
---

## Why they are different from V-belts

A synchronous belt **cannot slip**: the teeth engage sprocket grooves, so the ratio is exact (timing, positioning, indexing, and no speed loss), it needs **less tension** than a V-belt (less bearing load), does not stretch or need re-tensioning after run-in, and runs at 98% efficiency. In return it is **intolerant of misalignment** (it tracks off and shears teeth), of debris in the grooves, of shock overload (it **ratchets**: jumps teeth), and of prying (the fibreglass or carbon tensile cords crack and the belt fails later with no warning).

## Pitch families

| Family | Tooth profile | Pitches | Use |
|---|---|---|---|
| **Classical trapezoidal** (MXL, XL, L, H, XH, XXH) | Trapezoid | MXL 0.080", XL 1/5", **L 3/8", H 1/2"**, XH 7/8", XXH 1-1/4" | Older machines, light drives, positioning; being replaced |
| **HTD (curvilinear)** | Rounded tooth | **3M, 5M, 8M, 14M**, 20M (mm pitch) | General industrial; the common one on conveyors, fans, blowers |
| **GT (PowerGrip GT2/GT3/GT4, modified curvilinear)** | Deeper, rounded | 2M, 3M, 5M, **8M, 14M** | Higher capacity than HTD in the same pitch, quieter; **GT belts fit HTD sprockets** (8M, 14M) with the maker's blessing, not the reverse |
| **Poly Chain GT Carbon** | Curvilinear with carbon cords, polyurethane | **8M, 14M** | Replaces roller chain: very high torque, long life; needs its own sprockets |
| Metric T and AT (T5, T10, AT10) | Trapezoid | 5, 10 mm | European machinery, linear motion |
| Double-sided (DD, DH) | Teeth both sides | | Serpentine and reversing drives |

Sprockets must match the belt's pitch **and** profile (an HTD 8M belt on a GT 8M sprocket runs; an L belt on an H sprocket does not fit).

## Reading the numbers

- **Belt**: `1440-8M-30` = **1440 mm pitch length** (the number of teeth = 1440 ÷ 8 = 180), **8 mm pitch**, **30 mm wide**. Inch families: `480H100` = 48.0" pitch length, H (1/2") pitch, 1.00" wide (the width code is in 1/100"). `8MGT3-1440-30` adds the profile and generation. Poly Chain: `8MGT-1440-36`.
- **Sprocket**: `P34-8M-30` or `34-8M-30` = **34 teeth**, 8M pitch, 30 mm belt width; `P34-8M-30-2517` adds the Taper-Lock bushing size; inch: `30H100` = 30 teeth, H pitch, 1" belt. `F` or a flange note = flanged.
- Pitch diameter (for ratios, speeds): PD = teeth × pitch ÷ π (34 teeth × 8 mm ÷ π = 86.6 mm); the outside diameter is PD minus twice the belt's pitch-line distance (about 0.69 mm for 8M; the catalogue gives the OD).
- Ratio = driven teeth ÷ driver teeth, exactly.
- Centre distance from belt length: use the V-belt formula in [power, torque and drive formulas](/article/power-torque-speed-drive-formulas) with pitch diameters, or the maker's table; there is no adjustment for stretch, so the drive needs an adjustable centre or an idler to install and tension the belt.

## Flanges and alignment

A synchronous belt tracks toward one side (they all do, because of cord twist and slight misalignment), so **at least one sprocket must be flanged**: both flanges on one sprocket, or one flange on each sprocket on opposite sides; on a drive with a centre distance over 8× the small sprocket's diameter, **both** sprockets flanged. Belts that ride hard against a flange wear the edge and shed cords: the drive is misaligned.

**Alignment tolerance**: much tighter than V-belts: **≤ 1/4° (0.25°) combined angular and parallel** (Gates: 1/16" per foot of centre distance as the practical limit, tighter, 1/32" per foot, on drives over 5 m/s and on Poly Chain). Check:

1. **Parallel (offset)**: a straightedge across both sprocket faces (touching at 4 points) or a **laser sheave alignment tool** (magnetic laser on one sprocket, target on the other: reads offset and angle in one shot). Correct by moving the sprocket on its bushing or the motor on its slots.
2. **Angular (twist)**: the straightedge touches on one side only; a laser shows it as a line off the target's centre at each end. Shim the motor feet.
3. **Sprocket runout**: a dial indicator on the sprocket face and OD: ≤ 0.005" plus 0.0005" per inch of diameter; a bushing not seated or a bent shaft shows here.
4. After tensioning, run and check the belt sits with a small even gap to the flange; adjust while running is not allowed: stop, adjust, restart.

## Installation

1. Lockout. Never **pry, roll or force** a synchronous belt over a flange: the cords break. Loosen the motor / idler to reduce the centre distance until the belt goes on **by hand** with no force; on drives with flanges both sides, one sprocket may have to come off its bushing to fit the belt (or a removable flange).
2. Clean the sprocket grooves: rust, paint, debris, worn tooth tips (a sprocket with hooked or thin teeth, or shiny worn groove bottoms, is scrap: it will shear the new belt's teeth).
3. Sprockets aligned as above; bushings torqued (see [QD and Taper-Lock](/article/qd-and-taper-lock-bushings)).
4. Belt on, teeth fully in the grooves on both sprockets; take up the centre distance until the belt just tightens; align again.
5. Tension (below); lock the motor base; rotate by hand 2-3 turns, re-check tension and tracking; guard on.
6. Synchronous belts need **no run-in re-tension** (no stretch), but check after the first day for tracking and for a sprocket that has settled on its bushing.

## Tensioning

Too loose: the belt **ratchets** (jumps teeth) under load, the teeth shear, it flaps and wears. Too tight: bearing and shaft loads, cord fatigue, noise, sprocket wear. The correct tension depends on the belt section, width and the drive load; the maker's design program gives a **static tension** in pounds (or a deflection force). Two field methods:

**Force-deflection (Gates method)**

```
   deflection distance = span length ÷ 64        (1/64" per inch of span; span = √(C² − ((D − d)/2)²))
   push the belt at mid-span with a spring scale (belt tension tester) and read the force at that deflection;
   compare with the maker's minimum/maximum deflection force for that belt (from the drive design or the table).
```

Typical **deflection forces** at span ÷ 64 for PowerGrip GT/HTD (per the Gates tables; the exact value comes from the design's static tension, these are the usual ranges for a new belt):

| Belt | 20 mm wide | 30 mm | 50 mm | 85 mm |
|---|---|---|---|---|
| 5M | 3-4 lb | 4-6 lb | | |
| **8M** | 5-8 lb | **8-12 lb** | 14-20 lb | 24-34 lb |
| **14M** | | | 30-45 lb | 50-75 lb |
| Poly Chain 8M | 7-10 lb | 10-16 lb | 18-27 lb | 30-45 lb |

If the drive's calculated tension is not known, tension to the **lower** end of the range, run under load, and increase only if it ratchets; small sprockets (under about 24 teeth) and shock drives need the upper end.

**Sonic tension meter** (Gates 507C, ContiTech): the belt's natural vibration frequency at a known span, width and mass per length gives the tension: enter the belt data, pluck the belt, hold the sensor 1/2" from the span, read the tension in lb or the frequency, compare with the design value (or the target frequency the maker's app gives). It is the standard on wide belts and high-speed drives, repeatable to a few percent, and takes seconds. Rule: measure at the **middle of the longest span**, belt static, three readings.

Idlers: a fixed **inside** idler on the slack side is normal for tensioning drives with fixed centres; an idler on the **back** (smooth side) must be large (≥ the small sprocket's OD) and never on the teeth side unless it is a grooved idler. Spring-loaded auto-tensioners on drives with load variation.

## Failure signs

| Sign | Cause |
|---|---|
| **Teeth sheared** off the belt (the cords intact) | Ratcheting from under-tension, shock overload, a sprocket with worn/hooked teeth, misalignment loading one edge, debris in the grooves |
| **Edge wear / frayed edge, cords showing on one side** | Misalignment; belt tracking hard against a flange; a bent flange |
| **Cracks across the back** | Heat (over 185°F for standard belts), a back idler too small, ozone/chemicals, age |
| Belt broken cleanly, cords snapped | Belt **pried on** at installation (crimped cords), shock load, sprocket damage |
| **Excessive tooth wear, teeth shiny and thin** | Over-tension, worn sprocket, abrasive dust |
| Belt jumps teeth at start-up only | Under-tension; too small a sprocket for the torque |
| **Noise (whine)** | Normal at high speed; louder = over-tension or misalignment; a chirp = a belt edge rubbing the flange |
| Sprocket teeth hooked, groove bottoms polished | Sprocket worn out: replace with the belt (never a new belt on a worn sprocket) |
| Belt rides up on the flange or climbs off | Severe misalignment, a bent shaft, the wrong flange side |

Storage: hang or lay flat, no tight coils (kinks crack cords), dry, out of sunlight, under 85°F; a belt's shelf life is 5-8 years.

## Common mistakes

- Prying the belt over the flange with a screwdriver.
- Using the V-belt "thumb push" rule for tension: far too tight.
- Aligning with a piece of string on a 14M drive: 1° off, teeth gone in a month.
- New belt, old sprocket.
- Idler on the back with a 2" diameter: the belt back cracks.
- Belt number 1440-8M-30 replaced by 1440-8M-20 because "it was in stock": ratchets at half the load.

## Related

- [V-belt drive installation and tension](/article/v-belt-drive-installation-and-tensioning)
- [Roller chain drives](/article/roller-chain-drives)
- [QD and Taper-Lock bushings](/article/qd-and-taper-lock-bushings)
- [Power, torque and drive formulas](/article/power-torque-speed-drive-formulas)
- [Belt failure patterns](/article/belt-failure)
