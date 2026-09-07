---
title: "Shop Reference: Decimal Equivalents, Tap Drill Sizes, Conversions and Drive Formulas"
slug: shop-reference-tables
category: shop-reference
kind: chart
tags: [decimal equivalents, tap drill, conversion, inch to mm, ft-lb to Nm, psi to kPa, hp to kW, pulley ratio, rpm formula, belt length, 3-4-5, offset, trig]
source: "Machinery's Handbook; standard tables."
summary: "One-page shop math for millwrights: fraction-decimal-mm equivalents, UNC/UNF and metric tap drills, unit conversions, pulley and sprocket speed ratios, belt length, and the 3-4-5 square and offset formulas."
---

## Fraction - decimal - millimetre

| Fraction | Decimal | mm | | Fraction | Decimal | mm |
|---|---|---|---|---|---|---|
| 1/64 | .0156 | 0.397 | | 33/64 | .5156 | 13.097 |
| 1/32 | .0313 | 0.794 | | 17/32 | .5313 | 13.494 |
| 1/16 | .0625 | 1.588 | | 9/16 | .5625 | 14.288 |
| 3/32 | .0938 | 2.381 | | 19/32 | .5938 | 15.081 |
| 1/8 | .1250 | 3.175 | | 5/8 | .6250 | 15.875 |
| 5/32 | .1563 | 3.969 | | 21/32 | .6563 | 16.669 |
| 3/16 | .1875 | 4.763 | | 11/16 | .6875 | 17.463 |
| 7/32 | .2188 | 5.556 | | 23/32 | .7188 | 18.256 |
| 1/4 | .2500 | 6.350 | | 3/4 | .7500 | 19.050 |
| 9/32 | .2813 | 7.144 | | 25/32 | .7813 | 19.844 |
| 5/16 | .3125 | 7.938 | | 13/16 | .8125 | 20.638 |
| 11/32 | .3438 | 8.731 | | 27/32 | .8438 | 21.431 |
| 3/8 | .3750 | 9.525 | | 7/8 | .8750 | 22.225 |
| 13/32 | .4063 | 10.319 | | 29/32 | .9063 | 23.019 |
| 7/16 | .4375 | 11.113 | | 15/16 | .9375 | 23.813 |
| 15/32 | .4688 | 11.906 | | 31/32 | .9688 | 24.606 |
| 1/2 | .5000 | 12.700 | | 1 | 1.0000 | 25.400 |

## Tap drill sizes (75% thread)

| UNC | Tap drill | | UNF | Tap drill | | Metric coarse | Tap drill |
|---|---|---|---|---|---|---|---|
| #10-24 | #25 (.1495) | | #10-32 | #21 (.159) | | M4 × 0.7 | 3.3 mm |
| 1/4-20 | #7 (.201) | | 1/4-28 | #3 (.213) | | M5 × 0.8 | 4.2 mm |
| 5/16-18 | F (.257) | | 5/16-24 | I (.272) | | M6 × 1.0 | 5.0 mm |
| 3/8-16 | 5/16 (.3125) | | 3/8-24 | Q (.332) | | M8 × 1.25 | 6.8 mm |
| 7/16-14 | U (.368) | | 7/16-20 | 25/64 (.3906) | | M10 × 1.5 | 8.5 mm |
| 1/2-13 | 27/64 (.4219) | | 1/2-20 | 29/64 (.4531) | | M12 × 1.75 | 10.2 mm |
| 9/16-12 | 31/64 (.4844) | | 9/16-18 | 33/64 (.5156) | | M14 × 2.0 | 12.0 mm |
| 5/8-11 | 17/32 (.5313) | | 5/8-18 | 37/64 (.5781) | | M16 × 2.0 | 14.0 mm |
| 3/4-10 | 21/32 (.6563) | | 3/4-16 | 11/16 (.6875) | | M20 × 2.5 | 17.5 mm |
| 7/8-9 | 49/64 (.7656) | | 7/8-14 | 13/16 (.8125) | | M24 × 3.0 | 21.0 mm |
| 1-8 | 7/8 (.875) | | 1-12 | 59/64 (.9219) | | M30 × 3.5 | 26.5 mm |

Rule of thumb for metric: tap drill = major diameter minus pitch.

## Conversions

| From | To | Multiply by |
|---|---|---|
| inch | mm | 25.4 |
| mm | inch | 0.03937 |
| mil (0.001") | mm | 0.0254 |
| ft-lb | N·m | 1.356 |
| N·m | ft-lb | 0.7376 |
| in-lb | ft-lb | 0.0833 |
| psi | kPa | 6.895 |
| psi | bar | 0.0689 |
| hp | kW | 0.746 |
| kW | hp | 1.341 |
| lb | kg | 0.4536 |
| °F | °C | (°F - 32) × 5/9 |
| °C | °F | °C × 9/5 + 32 |
| US gal | litre | 3.785 |

## Speed ratio (pulleys, sprockets, gears)

```
D1 × N1 = D2 × N2          (D = diameter or tooth count, N = rpm)

Driven rpm = Driver rpm × Driver diameter ÷ Driven diameter
```

Motor 1 750 rpm, 4" motor sheave, 12" driven sheave → 1 750 × 4 ÷ 12 = **583 rpm**.

Use **pitch diameters** for belts and **tooth counts** for chains and gears.

## Belt length (approximate)

```
L = 2C + 1.57 (D + d) + (D - d)² ÷ (4C)
C = centre distance, D = large sheave PD, d = small sheave PD
```

## Belt speed and rpm

```
Belt speed (ft/min) = PD (in) × rpm × 0.262
Torque (ft-lb) = hp × 5 252 ÷ rpm
Horsepower = torque (ft-lb) × rpm ÷ 5 252
```

## Squaring and offsets

- **3-4-5**: measure 3 units along one line and 4 along the other; the diagonal is 5 when they are square (scale up: 6-8-10, 9-12-15).
- **Diagonals** of a rectangle are equal when it is square.
- **Offset (parallel shift) with two equal bends at angle θ**:
  `travel = offset ÷ sin θ`, `run = offset ÷ tan θ`. At 45°: travel = offset × 1.414, run = offset.
- Right-triangle basics: `sin = opposite ÷ hypotenuse`, `cos = adjacent ÷ hypotenuse`, `tan = opposite ÷ adjacent`.

## Circles

```
Circumference = π × D
Area = π × D² ÷ 4
Bolt circle chord (spacing between adjacent holes) = BCD × sin(180° ÷ number of holes)
```

Eight holes on a 12" bolt circle: 12 × sin 22.5° = 12 × 0.3827 = **4.592"** between hole centres.

## Related

- [Reading a micrometer](/article/reading-a-micrometer)
- [Bolt torque chart](/article/bolt-torque-chart-sae-metric)
