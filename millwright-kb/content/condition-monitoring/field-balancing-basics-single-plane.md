---
title: "Field Balancing Basics: When Unbalance Is the Problem, Single-Plane Balancing with a Trial Weight and a Vibration Meter, the Vector Method Step by Step, and Balance Grade Limits"
slug: field-balancing-basics-single-plane
category: condition-monitoring
kind: procedure
tags: [field balancing, single plane balancing, trial weight, balancing a fan, balancing an impeller, unbalance, 1x vibration, phase, vector balancing, four run method, balance grade, ISO 21940, G6.3, G2.5, balance weight, residual unbalance, fan build-up]
source: "ISO 21940-11 (balance quality requirements, formerly ISO 1940-1); vibration analyst training material (Technical Associates, Mobius Institute); Ludeca and IRD field balancing procedures."
summary: "How to confirm unbalance before you balance anything, the safe trial weight from the rotor weight and speed, the single-plane vector method (original run, trial run, calculate the correction), the four-run method that needs no phase reading, where to put and how to fix weights, and how to check the result against the ISO balance grades."
---

> Most "unbalance" on a fan is **build-up** on the blades or a **lost weight**: clean the wheel and look for the clip before you balance. Balancing a dirty fan puts the correction in the wrong place as soon as the dirt falls off.

## Confirm it is unbalance

Unbalance shows as a **steady 1× rpm** vibration, highest in the radial direction, with an amplitude that rises with the square of speed and a phase that stays fixed run to run; both bearings of the rotor read in phase for a single-plane (disc) rotor. Rule out misalignment (2×, axial), looseness (harmonics), resonance (amplitude changes sharply with a small speed change) and a bent shaft (1× with 180° phase across the coupling) first: see [vibration signatures](/article/vibration-signatures). Also check the wheel is tight on the shaft and the bearings are sound.

Single-plane balancing is enough when the rotor is a narrow disc (length under about a quarter of the diameter: fan wheels, pulleys, impellers, flywheels). Long rotors need two-plane balancing (an analyst with a two-channel instrument).

## Equipment

Vibration meter with **phase** (a tachometer or strobe referenced to a piece of reflective tape on the shaft) is the standard tool; a plain overall meter can use the four-run method below. Trial weights: washers, clamp-on weights, tape-on test weights (removed after), a scale for weighing them, chalk and a protractor for marking the rotor, lockout for every stop.

![Field balancing a decanter centrifuge](/photos/condition-monitoring/balancing-centrifuge.jpg)

*Field balancing a decanter centrifuge. Photo: NotecA, CC BY-SA 4.0, via commons*

![A portable balancer kit: two accelerometers, a tach and the analyzer](/photos/condition-monitoring/portable-balancer.jpg)

*A portable balancer kit: two accelerometers, a tach and the analyzer. Photo: NotecA, CC BY-SA 4.0, via commons*

## Trial weight size

Start with a weight that produces a centrifugal force of about **10% of the rotor weight** (some use 5-10% of rotor weight in force, or a rule of thumb of 30 g at the rim per 100 lb of rotor at 1,800 rpm):

```
Trial weight (oz) = 56,375 × W ÷ (r × N²)
W = rotor weight (lb), r = radius where the weight goes (in), N = rpm
Example: 300 lb fan wheel, 18 in radius, 1,200 rpm:
56,375 × 300 ÷ (18 × 1,440,000) = 0.65 oz  (about 18 g)
```

Too small a trial weight and the vibration barely changes (bad math); too big and the machine can be damaged: if the trial run vibration doubles, stop and halve the weight.

## Single-plane vector method (with phase)

![Vector diagram: original, original plus trial, and the trial effect](/img/condition-monitoring/single-plane-balancing-vectors.svg)

*Vector diagram: original, original plus trial, and the trial effect*

1. **Original run (O)**: run at operating speed, record amplitude and phase at the bearing nearest the rotor: e.g. 0.30 in/s at 60°.
2. Stop, lock out. Mark the rotor 0° at the reflective tape; add the **trial weight (T)** at a known angle and radius (say 0°), note its mass.
3. **Trial run (O+T)**: record again: e.g. 0.45 in/s at 110°.
4. On polar paper (or a balancing app): draw vector O (0.30 at 60°) and vector O+T (0.45 at 110°). The **effect of the trial weight** is the vector T = (O+T) − O: draw from the tip of O to the tip of O+T and measure its length and direction: say 0.38 in/s at 145°.
5. The correction weight must produce a vector equal and opposite to O:
   - **Size**: correction = trial weight × |O| ÷ |T| = trial × 0.30 ÷ 0.38 = 0.79 × trial.
   - **Angle**: move the weight from the trial position by the angle between T and −O (that is, between T and O plus 180°). Direction convention (with or against rotation) is what most beginners get wrong: try it, and if the second run gets worse, the weight went the wrong way: move it the other direction by twice the angle.
6. Remove the trial weight, fit the correction weight (or keep the trial weight and add the difference), run, and read the residual. Repeat the vector step with the new reading as the "original" if it is not within the target; two iterations normally reach it.

## Four-run method (no phase reading)

For a meter with amplitude only:

1. Run 1: original amplitude O.
2. Mark three positions 120° apart (A, B, C). Same trial weight at A: read amplitude a. Move to B: read b. Move to C: read c.
3. On paper draw a circle of radius O. From three points on it at 0°, 120°, 240° draw circles of radius a, b and c. The three circles intersect (nearly) at one point; the line from the centre to that point has length T (the trial effect) and points at the angle, measured from the same marks, where the trial weight was heaviest in its effect.
4. Correction weight = trial × O ÷ T, placed **opposite** the direction found (or at the angle the intersection indicates, per the construction). Confirm with a run.

Slower (four starts) but no phase instrument.

## Fixing weights

![A motor rotor balanced by drilling: material removed, not added](/photos/condition-monitoring/rotor-balance-drill.jpg)

*A motor rotor balanced by drilling: material removed, not added. Photo: Raimond Spekking, CC BY-SA 4.0, via commons*

- Fans: clip-on balance clips on the wheel's back plate rim, or a welded washer (weld on the back, away from the airstream; a weld adds its own weight: weigh a test weld first). Never drill blades unless the maker allows.
- Pulleys and flywheels: drill a hole at the light spot to remove weight (mass removed = same effect as adding opposite); keep the hole shallow and off the rim edge.
- Impellers: grind the shroud at the heavy spot lightly and evenly; do not grind vanes.
- Record the correction (mass, radius, angle) on the work order.

## How good is good enough

ISO 21940-11 balance grades give the permissible residual unbalance per kilogram of rotor: **G6.3** for fans, pumps, general machinery; **G2.5** for turbines, compressors, machine tool spindles; G16 for agricultural and crushing machinery. Field acceptance is usually on vibration instead: below the [ISO severity](/article/vibration-basics-and-iso-severity) zone B limit (about 2.8 mm/s RMS for a mid-size machine) or under about 0.1 in/s peak on a good fan; going below 0.05 in/s is diminishing returns unless the bearings or the process demand it.

## Common mistakes

- Balancing dirt, a bent shaft, a loose hub or a resonance.
- Trial weight lost during the run (use a positive clamp or tape well; note the direction of the airstream).
- Phase reference tape moved between runs.
- Mixing up the angle convention and chasing the weight around the wheel.
- Reading vibration at a different point or a different speed in the trial run.
- Skipping the lockout for a "quick" weight change.

## Related

- [Vibration basics and ISO severity](/article/vibration-basics-and-iso-severity)
- [Vibration signatures](/article/vibration-signatures)
- [Bearing defect frequencies and enveloping](/article/bearing-defect-frequencies-and-envelope)
- [Idlers, pulleys and lagging (fan and pulley build-up)](/article/idlers-pulleys-and-lagging)
- [Lockout/tagout basics](/article/lockout-tagout-basics)
