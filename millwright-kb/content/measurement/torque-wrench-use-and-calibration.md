---
title: "Torque Wrench Use and Calibration: Click, Beam, Dial and Digital Types, Correct Pull, Extensions and Crowfoot Math, Accuracy and the Checks That Keep a Wrench Honest"
slug: torque-wrench-use-and-calibration
category: measurement
kind: procedure
tags: [torque wrench, click torque wrench, beam torque wrench, dial torque wrench, digital torque wrench, torque wrench calibration, crowfoot torque, extension torque formula, torque angle, torque wrench accuracy, ISO 6789, hydraulic torque wrench, torque multiplier, impact wrench torque]
source: "ISO 6789 (hand torque tools); ASME B107.300; Snap-on, CDI and Norbar torque wrench instructions; Bolt Science and Fastenal torque-tension guidance."
summary: "How to get the torque the chart asks for onto the bolt: the right wrench type and range, the smooth pull at the handle centre, why you never use a click wrench past its click or as a breaker bar, the formula for a crowfoot or extension that changes the lever arm, torque-plus-angle methods, and how to check calibration with a simple weight-and-arm test or a tester."
---

> A torque wrench controls **friction plus stretch**, not stretch alone: the same torque on a dry bolt, an oiled bolt and an anti-seized bolt gives three different clamp loads. Use the chart's condition (see [bolt torque chart](/article/bolt-torque-chart-sae-metric) and [anti-seize](/article/anti-seize-and-galling)), and make the wrench itself repeatable with the habits below.

## Types

![Beam torque wrench: read the pointer on the scale while pulling](/photos/measurement/beam-torque-wrench.jpg)

*Beam torque wrench: read the pointer on the scale while pulling. Photo: EncMstr, CC BY-SA 3.0, via commons*

| Type | Accuracy (new) | Notes |
|---|---|---|
| **Click (micrometer adjust)** | ±4% clockwise, often ±6% counter-clockwise | The shop standard; set, pull until the click, stop. Wind back to the lowest setting for storage (spring relaxes) |
| **Beam** | ±4% | No spring to wear; read the pointer while pulling; cheap and honest; awkward in tight spots |
| **Dial** | ±2-4% | Reads peak or live torque; used for checking and for prevailing torque (running torque of a locknut) |
| **Digital (electronic)** | ±1-2% | Peak hold, angle mode, presets, audible/vibrating signal; needs batteries and a gentle life |
| **Preset / production** | ±4-6% | Fixed torque, no scale; for one repeated job |
| **Hydraulic** | ±3% of gauge | Flange and structural bolting over about 1,000 ft-lb; pressure-to-torque chart per tool; see [flange bolting](/article/flange-bolting-and-gaskets) |
| **Torque multiplier** (gearbox) | depends on input | 4:1 to 25:1; input torque × ratio × efficiency (about 0.9-0.95); reaction arm needs a solid stop |
| Impact wrench "torque sticks" | ±20-30% at best | Not a torque wrench: final tightening by a real wrench |

## Using a click wrench

![Click torque wrench: set the scale, pull smoothly, stop at the click](/photos/measurement/click-torque-wrench.jpg)

*Click torque wrench: set the scale, pull smoothly, stop at the click. Photo: J.C. Fields (Talk) (Uploads), CC BY-SA 3.0, via commons*

1. Pick a wrench whose range covers the target in its **middle 20-80%**: a 250 ft-lb wrench is wrong for 25 ft-lb.
2. Set the value: unlock, turn the handle to the main scale + the vernier on the handle (e.g. 90 + 5 = 95 ft-lb), lock.
3. Socket square on the fastener; hand on the **centre of the handle grip** (the wrench is calibrated for that point); no extensions on the handle.
4. Pull **smoothly and slowly** in the plane of the wrench until it clicks: one click, then stop. A second click adds torque. Do not jerk, do not use it to break bolts loose, do not drop it.
5. For multi-bolt joints follow the sequence and stages: see [flange bolting](/article/flange-bolting-and-gaskets).
6. After the job set it back to the minimum, keep it in its case.

Counter-clockwise use only if the wrench is rated for it (many click wrenches are not, or are less accurate).

## Extensions and crowfoot adapters

An extension **along the wrench axis** (straight socket extension, downward) changes nothing. An adapter that **lengthens the lever** (crowfoot, dog-bone, spanner adapter in line with the handle) makes the wrench apply more torque than it reads:

![Correcting the wrench setting for a crowfoot or extension](/img/measurement/torque-wrench-extension.svg)

*Correcting the wrench setting for a crowfoot or extension*

```
Setting on the wrench = Target × L ÷ (L + E)

L = wrench length from the centre of the handle grip to the square drive
E = extra length from the square drive to the centre of the adapter (in line with the wrench)
```

Example: target 100 ft-lb, wrench L = 18 in, crowfoot E = 2 in: set 100 × 18 ÷ 20 = **90 ft-lb**. If the crowfoot is put on at **90°** to the wrench, E = 0 and the setting stays 100 ft-lb: the easy way when there is room.

## Torque plus angle

Some joints (head bolts, torque-to-yield bolts, some coupling and structural bolts) specify a snug torque **then an angle** (e.g. 30 ft-lb + 90°). The angle controls stretch directly and is insensitive to friction. Mark the socket and the part, or use an angle gauge or a digital wrench's angle mode; do not reuse torque-to-yield bolts.

## Checking calibration

Every 5,000 cycles or 12 months (ISO 6789), after a drop, or whenever readings feel wrong:

**Weight and arm check** (good to about ±3%):
1. Clamp the square drive horizontally in a vice (a socket on a bolt held in the vice).
2. Measure the distance from the drive centre to the centre of the handle grip (L, in feet or inches).
3. Hang a known weight (W) at the grip centre from a cord: torque = W × L (lb × ft = ft-lb). A 25 lb weight at 18 in = 25 × 1.5 = 37.5 ft-lb.
4. Set the click wrench slightly below and above that value and confirm it clicks only at or above. Test at 20%, 60% and 100% of range.
5. Out by more than 4%: send it for calibration (a calibration lab adjusts and certifies it) or replace it.

A bench torque tester (electronic) does the same faster and gives a certificate.

## Common mistakes

- Using a click wrench as a breaker bar or past the click.
- Pulling from the end of the handle or with two hands at different points.
- Leaving it wound up to 200 ft-lb in the drawer for a year.
- Forgetting to correct for a crowfoot in line with the handle.
- Torquing over a lubricated thread with a dry-torque value (30-40% over-stretched bolts).
- Chrome sockets on impact wrenches to "get close first": the impact strips the thread and lies about torque.

## Related

- [Bolt torque chart](/article/bolt-torque-chart-sae-metric)
- [Flange bolting and gaskets](/article/flange-bolting-and-gaskets)
- [Anti-seize and galling](/article/anti-seize-and-galling)
- [Fastener locking methods](/article/locking-methods)
- [Hand and power tool safety](/article/hand-and-power-tool-safety)
