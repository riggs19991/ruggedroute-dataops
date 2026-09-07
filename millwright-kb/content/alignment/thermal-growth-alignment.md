---
title: "Thermal Growth: Calculating Cold-Alignment Targets"
slug: thermal-growth-alignment
category: alignment
kind: reference
tags: [thermal growth, thermal expansion, cold alignment, hot alignment, offset target, coefficient of expansion, centreline height]
source: "Standard thermal expansion formula; coefficients from engineering handbooks."
summary: "Machines change height as they warm up. This article gives the formula, expansion coefficients, a worked example, and how to enter the cold target into your alignment so the shafts are aligned at running temperature."
---

## Formula

```
Growth (ΔL) = L × C × ΔT

L  = distance from the base (where the machine is bolted) to the shaft centreline
C  = coefficient of linear thermal expansion of the machine casing material
ΔT = running temperature of the casing minus the temperature at alignment
```

| Material | C (in/in/°F) | C (mm/mm/°C) |
|---|---|---|
| Carbon steel | 0.0000063 | 0.0000113 |
| Cast iron | 0.0000059 | 0.0000106 |
| Stainless steel (304) | 0.0000096 | 0.0000173 |
| Aluminium | 0.0000128 | 0.0000231 |

## Worked example

Pump and motor. Aligned at 70°F. The motor frame runs at 130°F, the pump casing at 180°F (hot process fluid). Both cast iron.

| | Motor | Pump |
|---|---|---|
| Centreline height L | 14 in | 14 in |
| ΔT | 60°F | 110°F |
| Growth | 14 × 0.0000059 × 60 = **0.0050"** | 14 × 0.0000059 × 110 = **0.0091"** |

The pump grows 0.0041" more than the motor. To be aligned hot, set the motor **0.004" high** cold (or equivalently target the movable at +0.004" vertical offset). In a laser kit enter this as the thermal growth target; with dials, aim for a rim reading of about 0.008" TIR in the direction that puts the motor high.

Do the same for angularity when the inboard and outboard feet are at different heights or temperatures (common on gearboxes whose oil sump heats the bottom). And do it horizontally when there is asymmetric heating, for instance a pump with a hot suction line on one side.

## Where to get the numbers

1. **Equipment manual** first. Pump makers often specify "set motor 0.005" low" or give a hot/cold offset. That overrides the calculation.
2. Measure casing temperatures with an infrared thermometer at the bearing housings after the machine has run for at least an hour.
3. Measure L from the base plate to the shaft centre with a tape; the feet are where the growth starts.

## Verifying

The only proof is a **hot alignment check**: shut down, lock out, and take readings within a few minutes before the machine cools, or use permanent monitoring targets. If the hot readings are in tolerance, your cold target was right. Record both cold and hot readings for the next time.

## Related

- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
- [Laser alignment procedure](/article/laser-alignment-procedure)
