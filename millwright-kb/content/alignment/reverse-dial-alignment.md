---
title: "Reverse-Dial Indicator Alignment: Two-Bracket Method with Graph and Formula"
slug: reverse-dial-alignment
category: alignment
kind: procedure
tags: [reverse dial, reverse indicator, two bracket, shaft alignment, graphing alignment, plotting, offset, slope, shim calculation, pump motor]
source: "Standard millwright practice; Piotrowski, Shaft Alignment Handbook; trade curricula."
summary: "Reverse-dial alignment reads the centreline of each shaft relative to the other at two planes, so face runout and axial float do not matter. This article covers bracket setup, readings, sag, plotting the shafts on graph paper, and the formula method for shim and jack-bolt moves."
---

## Why reverse dial

Two brackets, one on each shaft, each carrying a rim indicator that reads the **other** shaft. Because you never read a face, **end float and face runout do not affect the result**, and the two rim readings define the position of the movable centreline at two known planes. Draw the line through those two points, extend it to the feet, and the shim values fall out.

Both shafts must rotate together (coupling connected or hubs pinned).

## Setup

1. Pre-alignment checklist, soft foot done, rough alignment within 0.020".
2. Bracket **S** clamps to the stationary shaft; its indicator reads the movable shaft (or hub) at plane **P1**, the plane closest to the movable machine.
3. Bracket **M** clamps to the movable shaft; its indicator reads the stationary shaft at plane **P2**, the plane closest to the stationary machine.
4. Measure and record:

| Symbol | Measurement |
|---|---|
| **L** | Distance between the two indicator planes P1 and P2 |
| **A** | Distance from P1 to the movable machine's **inboard** feet |
| **B** | Distance from P1 to the movable machine's **outboard** feet |

5. Measure **bar sag** for each bracket on a rigid pipe exactly as in the rim-and-face procedure. Sag values may differ; record both.

## Readings

1. Both indicators at 12 o'clock, zeroed.
2. Rotate together to 3, 6, 9, back to 12. Record both indicators at each stop with sign (plunger in = positive). Check return to zero.
3. Validity: 6 o'clock ≈ 3 + 9 for each indicator.
4. Correct each 6 o'clock reading for its bracket's sag (add the absolute sag).

## Interpreting

Using the rule *positive at 6 o'clock means the shaft being read is low relative to the shaft the bracket is on*:

- **Indicator on S reading M at P1**: R1 positive → **M is low** at P1 by R1/2.
- **Indicator on M reading S at P2**: R2 positive → **S is low relative to M** at P2, which means **M is high** relative to S at P2 by R2/2.

Convert both to "position of M relative to S, positive = M low":

```
Offset at P1 (near movable)     = + R1 / 2
Offset at P2 (near stationary)  = - R2 / 2
```

## Graph method (recommended for students)

1. Graph paper. Horizontal axis = distance along the shafts, 1 square = 1 inch. Vertical axis = mils, 1 square = 1 mil (or 0.5 mil for fine work).
2. Draw a horizontal line: this is the stationary shaft centreline extended.
3. Mark P2 and P1 on the horizontal axis L inches apart, then A and B inches from P1 for the movable feet.
4. At P2 plot the point "Offset at P2" (below the line if M is low, i.e. positive by our convention means plot **below**; pick one convention and write it on the sheet).
5. At P1 plot "Offset at P1".
6. Draw a straight line through the two points and extend it past both feet positions.
7. Read the vertical distance from the stationary line to the movable line at each foot. That is the shim change: if the movable line is below the stationary line at a foot, **add** that many mils of shims there.

The picture shows immediately whether the movable is tilted up or down, and whether the feet moves have the same sign.

## Formula method

```
Slope (mils per inch, positive = M gets lower toward its outboard end)
    m = (Offset at P1 - Offset at P2) / L

Inboard feet move   = Offset at P1 + m × A
Outboard feet move  = Offset at P1 + m × B
```

Positive = add shims (raise). Negative = remove shims.

### Worked example

| Item | Value |
|---|---|
| L | 6 in |
| A | 8 in |
| B | 20 in |
| R1 (S reads M, 6 o'clock, sag-corrected) | +0.010" |
| R2 (M reads S, 6 o'clock, sag-corrected) | -0.004" |

```
Offset at P1 = +0.010 / 2  = +0.005"  (M low here)
Offset at P2 = -(-0.004)/2 = +0.002"  (M low here too)
Slope m      = (0.005 - 0.002) / 6 = 0.0005 in/in

Inboard feet   = 0.005 + 0.0005 × 8  = +0.009"  → add 0.009"
Outboard feet  = 0.005 + 0.0005 × 20 = +0.015"  → add 0.015"
```

The movable is low and drooping toward its outboard end; both feet come up, outboard more.

## Horizontal

Same math with the 3 and 9 o'clock readings. Use (reading at 3 minus reading at 9) in place of the 6 o'clock reading. A positive result means the movable is displaced toward 3 o'clock at that foot; move it toward 9 o'clock by that amount with the jack bolts, watching a live indicator.

## Finish

1. Torque hold-down bolts in sequence.
2. Repeat the full reading set. Compare to tolerance.
3. Remove brackets, install coupling guard, record readings and shims.

## Tips

- Keep L as large as the coupling allows; a longer baseline makes the slope more accurate.
- Put indicators on machined shaft surfaces, not on painted or rusty hubs.
- If the coupling must be disconnected, pin or clamp the hubs so both shafts turn together.
- If you can only turn one shaft, use rim-and-face instead.

## Related

- [Rim-and-face alignment](/article/rim-and-face-alignment)
- [Shaft alignment fundamentals and tolerances](/article/shaft-alignment-fundamentals)
- [Laser alignment procedure](/article/laser-alignment-procedure)
