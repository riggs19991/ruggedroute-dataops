---
title: "Rim-and-Face Dial Indicator Alignment: Setup, Readings, Sag Correction and Shim Math"
slug: rim-and-face-alignment
category: alignment
kind: procedure
tags: [rim and face, dial indicator alignment, face reading, rim reading, bar sag, shim calculation, angularity, offset, coupling alignment, two indicator method]
source: "Standard millwright practice; formulas as taught in trade curricula (e.g. Red Seal Industrial Mechanic / Millwright) and in Piotrowski, Shaft Alignment Handbook."
summary: "How to mount the bracket, measure bar sag, take rim and face readings at 12-3-6-9, validate them, and calculate shim and jacking-bolt moves for the movable machine using A, B and D dimensions."
---

## The idea

One bracket clamped to the **stationary** shaft (or hub) carries two dial indicators that touch the **movable** machine's coupling hub:

- the **rim** indicator reads the outside diameter of the hub: it sees **offset**;
- the **face** indicator reads the flat face of the hub: it sees **angularity**.

Rotate both shafts together (or, if the movable cannot be turned, rotate only the stationary with the bracket and read a hub that has been checked for runout). Readings at 12, 3, 6 and 9 o'clock give the vertical and horizontal picture.

## Tools

![Rim and face indicator setup with the A, B and C dimensions](/img/alignment/rim-and-face-setup.svg)

![A plunger dial indicator: 0.001 in graduations, one inch of travel](/photos/alignment/dial-indicator.jpg)

*A plunger dial indicator: 0.001 in graduations, one inch of travel. Photo: Solaris2006, CC BY-SA 3.0, via commons*

*Rim and face indicator setup with the A, B and C dimensions*

- Rim-and-face bracket (chain or clamp type) with rigid rods; the shorter the rods, the less sag
- Two dial indicators, 0.001" (or 0.01 mm), with a 1" range
- Pre-cut shim pack, feeler gauges, straightedge
- Tape measure or rule for the A, B, D dimensions
- Marker to mark 12-3-6-9 on the hub
- Alignment worksheet

## Dimensions you must record

| Symbol | Measurement |
|---|---|
| **D** | Diameter of the circle the **face** indicator tip sweeps on the hub face |
| **A** | Distance from the face-indicator contact plane to the centre of the movable machine's **inboard (front)** hold-down bolts |
| **B** | Distance from the face-indicator contact plane to the centre of the movable machine's **outboard (rear)** hold-down bolts |

Make the face indicator sweep the largest diameter possible; a bigger D makes angularity easier to see.

## Step 1 - Measure bar sag

1. Clamp the bracket with its rods and rim indicator on a piece of rigid pipe or bar held in a vise, set up exactly as it will be on the machine (same rod length, same indicator).
2. Zero the rim indicator at 12 o'clock. Rotate the pipe to 6 o'clock. The reading (always negative) is the **sag**. A typical short bracket sags 0.002-0.005".
3. Write it down. On the machine, the true 6 o'clock rim reading = measured reading **plus** the absolute sag value. (Sag makes the bottom reading read *more negative* than reality, so you add it back.) Face readings need no sag correction.

## Step 2 - Mount on the machine

1. Complete the pre-alignment checklist and soft-foot correction.
2. Clamp the bracket to the **stationary** shaft/hub. Rim indicator plunger radial, square to the hub OD, roughly mid-travel with a little preload. Face indicator plunger axial, square to the face, mid-travel.
3. Mark 12, 3, 6, 9 on the movable hub. Looking from the movable machine toward the stationary, 3 o'clock is on your right.
4. Rotate to 12 o'clock. Zero both indicators. Rotate **slowly** through 3, 6, 9 and back to 12. It must return to zero (within 0.001"); if not, something moved.

## Step 3 - Take readings

Record rim and face at 3, 6 and 9 with the sign the needle shows (clockwise = plus = plunger pushed in).

**Validity rule:** for both rim and face, the 6 o'clock reading should equal 3 o'clock + 9 o'clock (within about 0.002"). If it does not, look for a loose bracket, a slipping indicator, or a hub that is not round. Re-take.

Apply sag to the 6 o'clock rim reading. Use the corrected value from here on.

Rotate the shafts only in one direction. Take a second full set to confirm repeatability before you shim anything.

## Step 4 - Understand the signs

With the bracket on the stationary and indicators reading the movable hub:

- **Rim**: a **positive reading at a clock position means the movable shaft is displaced toward that position** by half the reading. Positive at 6 o'clock = movable is **low** by (rim reading ÷ 2). Positive at 3 o'clock = movable is shifted toward 3 o'clock by half the reading.
- **Face**: a positive reading at 6 o'clock means the bottom of the movable's face is closer to the stationary than the top, so the movable shaft tilts with its **outboard end low**. Angularity = face reading ÷ D (mils per inch).

Reasoning check for the rim: the plunger is only compressed at the bottom if the hub's bottom surface has moved toward the indicator body, which only happens when the hub sits low.

## Step 5 - Vertical shim calculation

Let **R** = sag-corrected rim reading at 6 o'clock and **F** = face reading at 6 o'clock (both signed).

```
Offset at coupling         = R / 2
Angularity (mils per inch) = F / D

Inboard (front) feet move  = R/2 + F × (A / D)
Outboard (rear) feet move  = R/2 + F × (B / D)
```

Positive result = **add** shims (raise). Negative result = **remove** shims (lower).

### Worked example

| Item | Value |
|---|---|
| D | 6 in |
| A | 9 in |
| B | 21 in |
| Rim at 6 (measured) | +0.006" |
| Sag | -0.002" |
| Rim at 6 (corrected) | +0.008" |
| Face at 6 | +0.004" |

```
Offset      = 0.008 / 2            = 0.004" (movable low)
Angularity  = 0.004 / 6            = 0.00067 in/in = 0.67 mils/in
Front feet  = 0.004 + 0.004 × 9/6  = 0.004 + 0.006 = +0.010"  → add 0.010" shims
Rear feet   = 0.004 + 0.004 × 21/6 = 0.004 + 0.014 = +0.018"  → add 0.018" shims
```

Both feet go up, rear more than front, which lifts the low outboard end and raises the whole shaft to close the offset.

## Step 6 - Horizontal move

Use the same formulas with the **3 and 9 o'clock** readings. Zero at 9 o'clock, read at 3 o'clock (or subtract: reading at 3 minus reading at 9, halved for the offset). A positive result means move the movable machine **toward 9 o'clock** by that amount at that foot (the movable is displaced toward 3, so it comes back toward 9). Move with jacking bolts and watch a rim indicator set horizontally at the coupling so you can see the shaft move live.

## Step 7 - Tighten and verify

1. Snug all four bolts evenly, then torque in a cross pattern to the specified value.
2. Re-take a full set of readings. Compare to the [tolerance table](/article/shaft-alignment-fundamentals).
3. If still out, repeat. Shim calculations converge in two or three passes.
4. Record final readings, shim thicknesses per foot, and the date on the equipment history.

## Common errors

- Face indicator not square to the face: reads sideways motion as angularity.
- Axial float: if the movable shaft can slide, the face reading is garbage. Push the shaft one way and hold it, or use the reverse-dial method.
- Forgetting that the rim TIR is **twice** the offset.
- Using the hub OD (rim) diameter as D. D is the **face indicator sweep** diameter.
- Rotating the two shafts separately with the coupling disconnected: rim runout on the hub then adds to the readings. Rotate together or check runout first.

## Related

- [Reverse-dial alignment](/article/reverse-dial-alignment)
- [Soft foot correction](/article/soft-foot-correction)
- [Dial indicator use and care](/article/dial-indicator-use)
