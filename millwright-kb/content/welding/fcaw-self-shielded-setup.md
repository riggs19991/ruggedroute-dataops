---
title: "Self-Shielded Flux-Core (FCAW-S) Setup: E71T-11 / Innershield NR-211-MP Procedure Chart, DC− Polarity, Stickout and Field Technique"
slug: fcaw-self-shielded-setup
category: welding
kind: chart
manufacturer: Lincoln Electric
model_numbers: ["Innershield NR-211-MP", "E71T-11", "NR-212", "NR-232", "E71T-8", "E71T-GS", "Hobart Fabshield 21B"]
tags: [self shielded flux core, gasless flux core, E71T-11, NR-211, Innershield, DCEN, DC negative, wire feed speed, voltage, stickout, outdoor welding, wind, field repair, galvanized, portable welder, flux core troubleshooting]
source: "Lincoln Electric Innershield NR-211-MP data sheet (rev. C-EN03, calculation data and optimum welding parameters); Lincoln NR-211-MP product page (US sizes, CTWD and plate limits)."
summary: "Lincoln's published parameters for Innershield NR-211-MP by wire size, converted to inch units, with the DC− polarity rule, stickout, maximum plate thickness per diameter, position settings, and the technique and troubleshooting that self-shielded flux-core needs in the field."
---

## What it is

Flux-cored wire whose core makes its **own shielding** as it burns; no gas bottle. Runs on any CV machine, including small 120 V units, and is the go-to for **outdoor, windy, rusty and portable** work. The trade-off: more spatter and smoke than gas-shielded wire, a colder-looking bead that needs correct technique, and single-pass or limited multi-pass ratings on the general-purpose wires.

## The three rules

![Self-shielded flux-core runs DCEN: gun lead to negative](/img/welding/polarity.svg)

*Self-shielded flux-core runs DCEN: gun lead to negative*

1. **Polarity: DC− (electrode negative).** Gun lead to **−**, ground to **+**. Run it on DC+ and you get a violent, porous, spattery mess. This is the first thing to check on any flux-core complaint.
2. **Stickout is long**: **1/2" for .030-.035, 5/8-3/4" for .045-.068, 3/4-1" for 5/64 and up**. The wire has to preheat in the long stickout for the flux to work. Short stickout = porosity.
3. **Drag, don't push**, 10-20°. "Drag if slag."

## NR-211-MP (E71T-11) typical parameters

Converted from Lincoln's metric calculation data (wire feed speed cm/min × 0.394 = in/min). Electrical stickout listed; CTWD is about 1/4" longer.

**.035" (0.9 mm), electrical stickout 3/8" (CTWD ≈ 1/2"), DC−**

| WFS (ipm) | Amps | Volts | Deposition (lb/h) | Use |
|---|---|---|---|---|
| 50 | 30 | 14 | 0.7 | 22-20 ga sheet |
| 90 | 90 | 16 | 1.3 | 14-12 ga |
| 110 | 120 | 16.5 | 1.8 | 3/16" |

Lincoln's US procedure sheet for .035 spans **50-300 ipm at 13-16 V**; the .030 size runs 40-200 ipm at 13-15 V on 120 V machines.

**.045" (1.1 mm), electrical stickout 9/16" (CTWD ≈ 3/4"), DC−**

| WFS (ipm) | Amps | Volts | Deposition (lb/h) |
|---|---|---|---|
| 70 | 120 | 15 | 1.1 |
| 110 | 160 | 17 | 2.2 |
| 130 | 170 | 18 | 2.6 |

**.068" (1.7 mm), electrical stickout 3/4", DC−**

| WFS (ipm) | Amps | Volts | Deposition (lb/h) |
|---|---|---|---|
| 40 | 120 | 15 | 1.8 |
| 75 | 190 | 18 | 3.3 |
| 175 | 320 | 23 | 7.7 |

**5/64" (2.0 mm), electrical stickout 3/4", DC−**

| WFS (ipm) | Amps | Volts | Deposition (lb/h) |
|---|---|---|---|
| 50 | 180 | 16 | 3.1 |
| 75 | 250 | 18 | 4.9 |
| 150 | 350 | 22 | 9.5 |

**3/32" (2.4 mm), electrical stickout 3/4", DC−**

| WFS (ipm) | Amps | Volts | Deposition (lb/h) |
|---|---|---|---|
| 50 | 235 | 16 | 4.4 |
| 55 | 250 | 18 | 5.1 |
| 100 | 370 | 20 | 9.3 |

**Optimum settings by position (Lincoln), fill passes**

| Wire | Flat / horizontal fillet | Horizontal groove | Vertical-up | Vertical-down / overhead |
|---|---|---|---|---|
| .035 | 70 ipm, 65 A, 15 V | 70 ipm, 65 A, 15 V | 60 ipm, 50 A, 14.5 V | 90 ipm, 85 A, 16 V |
| .045 | 90 ipm, 140 A, 16 V | 90 ipm, 140 A, 16 V | 80 ipm, 130 A, 16 V | 110 ipm, 160 A, 17 V |
| .068 | 175 ipm, 320 A, 23 V | 100 ipm, 230 A, 19.5 V | 75 ipm, 190 A, 18 V | 120 ipm, 280 A, 21 V |

**Maximum plate thickness**: .030 and .035 = 5/16"; .045 = 5/16" (single pass rated, 1/2" multi-pass with care); .068 and larger = 1/2" and up. NR-211-MP is a **general-purpose, non-code** wire: it is not low-hydrogen and is not for structural steel under AWS D1.1 seismic or high-restraint rules. For code-quality self-shielded work use **E71T-8** (NR-232, NR-233) which is DC− all-position with impact ratings, or E70T-6 (NR-305) for flat.

## Setup

![A small wire-feed machine set up for self-shielded flux-cored wire](/photos/welding/fcaw-feeder.jpg)

*A small wire-feed machine set up for self-shielded flux-cored wire. Photo: Mgschuler, CC BY 3.0, via commons*

1. CV machine, **DC−**. Small 120 V machines: use .030 or .035 wire only.
2. **Knurled** drive rolls; tension light (tube wire crushes).
3. Liner sized for the wire. Remove the gas nozzle if the gun has one and fit the flux-core **insulated nozzle** or run with the tip exposed as the maker recommends; a MIG nozzle traps spatter.
4. No gas connected; if the machine has a gas solenoid it does not matter.
5. Ground clamp on bare metal close to the weld.
6. Set WFS and voltage from the table. On a tapped-voltage machine, pick the tap then trim WFS for a steady crackle.

## Technique

![Drag angle and stickout by wire type](/img/welding/fcaw-drag-stickout.svg)

*Drag angle and stickout by wire type*

- Drag 10-20°, stickout per the rule, arc on the leading edge of the puddle.
- Stringers or a slight side-to-side. Vertical-up with a slow inverted-V weave at the low end of the range; NR-211 also runs **vertical-down** well on sheet.
- Slag is heavy and glassy: chip and wire-brush every pass; multi-pass welds are limited to about 3 layers on general-purpose wire because of manganese build-up in the deposit (data sheet limit).
- Fume is heavy: ventilation or a fume extractor, and never weld galvanised without grinding the zinc off 1" back and full ventilation.
- Wind up to about 20-25 mph is tolerated (the advantage over gas), but rain on the joint is still porosity.
- Wire spools rust: keep in a bag, and cut off the first foot of wire on a spool that has been open for weeks.

## Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Spatter everywhere, sooty, porous | **Polarity DC+** | Swap to DC− |
| Porosity | Stickout too short, voltage too high, rusty/damp wire, oily plate | Lengthen stickout, drop 1 V, new wire, clean |
| Wire stubs and pushes the gun back | Voltage too low or WFS too high | Up 1 V |
| Bead tall and ropy, slag hard to remove | Too cold, too fast | Raise WFS/V, slow down |
| Burn-through on sheet | Too hot | .030 wire, low tap, vertical-down fast |
| Erratic feeding | Smooth rolls slipping, tension too tight, liner dirty | Knurled rolls, reset, clean |
| Cracks in a multi-pass weld | Too many passes on general-purpose wire, high restraint | Use E71T-8 or 7018 for multi-pass structural |

## Related

- [Gas-shielded flux-core (E71T-1) setup](/article/fcaw-gas-shielded-setup)
- [MIG (GMAW) setup](/article/gmaw-mig-setup)
- [AWS wire classification decoder](/article/aws-electrode-classification)
- [Welding safety: fumes and PPE](/article/welding-safety-fumes-and-ppe)
