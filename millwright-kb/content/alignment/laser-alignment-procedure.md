---
title: "Laser Shaft Alignment: General Procedure for Any Laser Kit"
slug: laser-alignment-procedure
category: alignment
kind: procedure
manufacturer: "Various (Pruftechnik, Fixturlaser, SKF TKSA, Easy-Laser)"
model_numbers: ["OPTALIGN", "ROTALIGN", "TKSA 11", "TKSA 31", "TKSA 51", "Fixturlaser NXA", "Easy-Laser XT"]
tags: [laser alignment, laser kit, TKSA, Optalign, Fixturlaser, Easy-Laser, live move, soft foot, thermal growth, coupling alignment]
source: "Manufacturer quick-start guides; general practice."
summary: "A brand-independent walk-through for a two-head laser alignment system: mounting, dimensions, sweep, result screen, live move, and the checks that laser systems do not do for you."
---

## What the laser does and does not do

A laser kit replaces the indicators and the arithmetic. It **does not** replace the pre-alignment checklist. Pipe strain, bent shafts, worn couplings, dirt under feet and soft foot still ruin the job. The kit will happily tell you to shim 0.045" when the real problem is a cracked grout pad.

## Procedure

### 1. Prepare

1. Lockout/tagout. Pre-alignment checklist complete.
2. Rough align with a straightedge so the laser beams will stay on the detectors through the rotation.
3. Charge the heads, clean the lenses, check the chain/V-block brackets.

### 2. Mount the heads

1. **S head (stationary)** on the stationary shaft, **M head (movable)** on the movable shaft. Most kits label them and colour-code.
2. Mount on the shaft or on the coupling hub, as close to the coupling as practical, with the brackets tight and the heads at the same height and rotational position (12 o'clock).
3. Aim: adjust the thumbwheels until each beam hits the centre of the opposite detector. Some kits show a target on screen.

### 3. Enter dimensions

Measure with a tape and enter (the kit draws a picture):

- S head to M head (or coupling centre) distance
- M head to movable inboard feet
- Inboard feet to outboard feet
- Coupling diameter (for angularity display) and **rpm** (for tolerance)
- Any **thermal growth** targets from the equipment manual (see [thermal growth](/article/thermal-growth-alignment))

### 4. Measure

Rotate both shafts together. Depending on the kit:

- **Continuous sweep**: rotate through at least 60-70° (more is better) and the kit records.
- **Three-point (clock) method**: stop at three positions, for example 9, 12, 3, and press "take reading".

Watch for the beam falling off a detector (rough align again) and for readings that jump (loose bracket, someone bumped the shaft).

### 5. Read the result

The screen shows vertical and horizontal **offset** and **angularity** at the coupling, and the **foot corrections**: shim values for the inboard and outboard feet, and horizontal moves. Compare with the tolerance table; most kits show a smiley or colour code.

### 6. Soft-foot check

Most kits have a soft-foot function: with the machine bolted down, loosen one foot at a time and the kit reports the movement. Correct anything over 0.002" before continuing. If your kit lacks it, do the [dial indicator soft-foot check](/article/soft-foot-correction).

### 7. Vertical correction

1. Loosen the movable's bolts, add/remove the shims the screen calls for at each pair of feet.
2. Re-torque and **re-measure**. Do not trust a single shim pass.

### 8. Horizontal correction - live move

1. Select "live move" / "horizontal move" and rotate the heads to the position the kit asks for (usually 3 or 9 o'clock).
2. Loosen bolts slightly. Use jacking bolts to push the movable while watching the live numbers move toward zero at both feet.
3. Tighten in sequence while watching the screen; the numbers will shift as bolts pull the frame. Adjust and repeat until it stays in tolerance **after** final torque.

### 9. Final measurement and report

Take a fresh measurement, save the report (most kits export a PDF), and record shims per foot. Fit the coupling guard.

## Kit-specific notes worth knowing

- **SKF TKSA 11/31/51**: phone or tablet app; "guided" mode walks through the steps above. Soft foot is built in on the 31 and 51.
- **Pruftechnik OPTALIGN/ROTALIGN**: continuous sweep; "Move simulator" lets you plan a shim change before you touch a bolt.
- **Fixturlaser NXA / Easy-Laser XT**: touchscreen, dual-detector heads; both support sweeping and three-point.

Always read the quick-start card for the kit in the toolbox; they differ in how they name the heads and which rotation direction they expect.

## When the laser lies

| Symptom | Cause |
|---|---|
| Readings not repeatable | Loose bracket, coupling backlash (rotate in one direction only), shaft end float |
| Huge angularity but shafts look fine | Wrong dimensions entered, heads not at the same clock position |
| Cannot get both feet in tolerance | Soft foot, bolt-bound (foot hits a bolt), pipe strain, base is bowing |
| Good cold, bad hot | Thermal growth not entered; see thermal growth article |

## Related

- [Shaft alignment fundamentals and tolerances](/article/shaft-alignment-fundamentals)
- [Soft foot correction](/article/soft-foot-correction)
- [Thermal growth and cold-alignment targets](/article/thermal-growth-alignment)
