---
title: "Bolt Torque Chart: SAE Grade 5 and 8, Metric 8.8 and 10.9, with Grade Markings and Lubrication Factors"
slug: bolt-torque-chart-sae-metric
category: fasteners
kind: chart
tags: [torque chart, bolt torque, grade 5, grade 8, 8.8, 10.9, head markings, torque wrench, lubricated torque, anti-seize, K factor, torque sequence]
source: "Standard published torque tables (Fastenal, Portland Bolt, ARP) based on 75% of proof load, K = 0.20 dry; SAE J429; ISO 898-1."
summary: "Reference tightening torques for common UNC and metric fasteners, how to recognise the grade from the head, why lubricated bolts need less torque, and the cross-pattern sequence for flanges and machine feet."
---

> Equipment manuals override this chart. These values are for **plain (unplated), dry** steel bolts in clean steel threads, torqued to about 75% of proof load. Zinc plating, oil, anti-seize or thread locker changes the friction and therefore the torque needed for the same clamp load.

## SAE (inch) fasteners - torque in **ft-lb**, dry

| Size - TPI | Grade 2 | **Grade 5** | **Grade 8** |
|---|---|---|---|
| 1/4-20 | 5 | 8 | 12 |
| 5/16-18 | 11 | 17 | 25 |
| 3/8-16 | 19 | 31 | 44 |
| 7/16-14 | 30 | 49 | 70 |
| 1/2-13 | 46 | 75 | 107 |
| 9/16-12 | 66 | 110 | 154 |
| 5/8-11 | 92 | 150 | 212 |
| 3/4-10 | 164 | 266 | 376 |
| 7/8-9 | 160 | 429 | 606 |
| 1-8 | 240 | 644 | 909 |

Fine-thread (UNF) bolts of the same size take roughly 10% more.

## Metric fasteners - torque in **N·m** (ft-lb in brackets), dry

| Size × pitch | Class 8.8 | Class 10.9 | Class 12.9 |
|---|---|---|---|
| M6 × 1.0 | 10 (7) | 14 (10) | 17 (12) |
| M8 × 1.25 | 25 (18) | 35 (26) | 41 (30) |
| M10 × 1.5 | 49 (36) | 70 (52) | 82 (60) |
| M12 × 1.75 | 86 (63) | 120 (89) | 145 (107) |
| M14 × 2.0 | 135 (100) | 190 (140) | 230 (170) |
| M16 × 2.0 | 210 (155) | 295 (218) | 350 (258) |
| M20 × 2.5 | 410 (302) | 580 (428) | 690 (509) |
| M24 × 3.0 | 710 (524) | 1 000 (738) | 1 200 (885) |

## Head markings

![Grade by head marking](/img/fasteners/bolt-head-markings.svg)

*Grade by head marking*

| Marking | Grade / class | Min tensile |
|---|---|---|
| No marks | SAE Grade 2 (low carbon) | 74 ksi (small sizes) |
| **3 radial lines** | SAE **Grade 5** (medium carbon, Q&T) | 120 ksi |
| **6 radial lines** | SAE **Grade 8** (alloy, Q&T) | 150 ksi |
| "8.8" | Metric class 8.8 | 800 MPa |
| "10.9" | Metric class 10.9 | 1 040 MPa |
| "12.9" | Metric class 12.9 (socket head cap screws) | 1 220 MPa |
| "A2" / "A4" + "-70" | Stainless 304 / 316, 700 MPa | Torque as Grade 5 with anti-seize (stainless galls) |

Nuts: Grade 5 nuts carry two dashes or none, Grade 8 nuts six dashes or "8". Match the nut grade to the bolt.

## Lubrication factor

Torque only controls clamp load through friction. Rule of thumb multipliers applied to the dry value:

| Condition | Multiply dry torque by |
|---|---|
| Plain dry | 1.00 |
| Zinc plated, dry | 0.90 |
| Light oil on threads | 0.75-0.80 |
| Moly or copper anti-seize | 0.60-0.70 |
| Loctite (wet) | about 0.80 |

Using dry torque on an anti-seize-coated bolt can stretch it past yield. When in doubt use the fastener maker's K-factor and the formula:

```
T = K × d × F      (T in in-lb, d = nominal diameter in, F = clamp load lb)
K ≈ 0.20 dry steel, 0.15 lubricated, 0.12 anti-seize
```

## Tightening sequence

- **Circular flanges (4, 8, 12 bolts)**: criss-cross (star) pattern in three passes: 30%, 70%, 100% of final torque, then one more pass at 100% going around in order.
- **Rectangular (machine feet, gearbox split lines)**: start in the middle and work outward in a spiral/alternating pattern, again in passes.
- Re-torque gasketed joints after warm-up where the gasket maker says so.

## Torque wrench rules

- Use a wrench whose range puts the target between 20% and 90% of full scale.
- Pull smoothly; stop at the click. Do not keep pulling after the click.
- Wind a click wrench back to its lowest setting for storage.
- Calibrate yearly (or after a drop).
- Extensions change the torque: with an offset extension of length **L** on a wrench of length **W**, set the wrench to Target × W ÷ (W + L).

## Related

- [Decimal equivalents, tap drills and conversions](/article/shop-reference-tables)
- [Rigging basics](/article/rigging-basics-sling-angles-and-hitches)
