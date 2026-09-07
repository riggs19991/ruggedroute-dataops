---
title: "Which Welding Process for the Job: Stick, MIG, Flux-Core, TIG, SAW, Oxy-Fuel and Brazing Compared"
slug: welding-process-selector
category: welding
kind: reference
tags: [welding process, SMAW vs GMAW, stick vs MIG, flux core, TIG, submerged arc, which process, process selection, field welding, wind, galvanized, thin sheet, thick plate, aluminum welding, stainless welding, cast iron]
source: "AWS Welding Handbook Vol. 2; Lincoln Electric and Miller process guides; general shop practice."
summary: "A decision table for picking the process before you set anything up: material, thickness, position, indoors or outdoors, quality required, and what equipment you have. Links to the setup chart for each process."
---

## The one-minute decision

Ask these in order. The first row that fits usually decides it.

| Situation | Use | Why |
|---|---|---|
| Outdoors, windy, dirty or rusty steel, no gas bottle handy | **Stick (SMAW)** with E6010/E6011 or E7018, or **self-shielded flux-core (FCAW-S)** | No shielding gas to blow away; flux cleans through mill scale and light rust |
| Thin sheet steel (24 ga to 1/8") in the shop | **MIG short-circuit (GMAW-S)** .030/.035 wire, C25 | Low heat, easy to control, fast |
| Structural plate 3/16" and up, flat/horizontal, production | **MIG spray** (.045 wire, 90/10 Ar-CO2) or **gas-shielded flux-core (FCAW-G)** E71T-1 | Deposition rate, penetration, low spatter |
| Plate 1/4" and up, vertical or overhead | **FCAW-G E71T-1** or **E7018 stick** | Fast-freezing slag holds the puddle |
| Code work, pressure, low-hydrogen required | **E7018** stick, **FCAW-G** with H4/H8 wire, or **GMAW spray/pulse** | Hydrogen control and toughness |
| Stainless steel, thin, cosmetic | **TIG (GTAW)** DCEN with ER308L/316L | Clean, controllable, no spatter |
| Stainless, 1/8" and up, production | **MIG** ER308L with tri-mix or Ar-2% O2 spray, or **FCAW** E308LT | Speed |
| Aluminium, thin or precision | **TIG AC** | Cleans oxide, full control |
| Aluminium, 1/8" and up, long welds | **MIG spray/pulse** with spool gun or push-pull, ER4043/5356, 100% Ar | Deposition |
| Cast iron repair | **Stick** ENiFe-Cl / ENi-Cl with preheat and peening, or **braze** | Ductile nickel deposit tolerates the base metal |
| Very thick plate, long straight seams, flat | **Submerged arc (SAW)** | Highest deposition, no arc glare, but flat/horizontal only |
| Pipe root pass (open root) | **E6010 stick** DCEP or **TIG** ER70S-2 | Penetration control, keyhole root |
| Galvanised steel | Any of the above **after grinding the zinc back 1"** plus ventilation, or **braze** with bronze rod | Zinc fume; brazing avoids melting it |
| Dissimilar steels (carbon to stainless) | **E309L / ER309L** by any process | Ferrite balance absorbs dilution |
| Hard-facing wear parts | **Stick** or **FCAW-S** hardfacing rods, oxy-fuel for small parts | Controlled dilution |
| Thin sheet metal, copper, brass, attaching fittings | **Brazing / silver soldering** with oxy-fuel or air-acetylene | Below the melting point, no distortion |
| Field cutting/heating | **Oxy-fuel** or **plasma** (see Cutting & Gouging) | |

## Process character in one line each

| Process | Power source | Electrode | Shielding | Deposition | Skill | Best at |
|---|---|---|---|---|---|---|
| SMAW (stick) | CC, AC or DC | consumable coated rod | flux slag and gas from coating | 1-4 lb/h | medium | portable, all positions, wind, dirty steel |
| GMAW (MIG) | CV DC+ | solid wire | bottled gas | 3-12 lb/h | low to start, high to master spray/pulse | clean shop steel, sheet to plate, aluminium with spool gun |
| FCAW-G | CV DC+ | tubular wire, flux inside | bottled gas plus flux | 5-15 lb/h | medium | thick plate, out of position, structural |
| FCAW-S | CV **DC−** | tubular wire | flux only | 3-8 lb/h | medium | outdoors, field repair, galvanised (with prep) |
| GTAW (TIG) | CC DC− steel, AC aluminium | non-consumable tungsten, filler by hand | argon | 0.5-2 lb/h | high | stainless, aluminium, thin, cosmetic, root passes |
| SAW | CV/CC DC | solid wire under granular flux | flux | 10-40 lb/h | low (mechanised) | long flat seams, heavy plate |
| Oxy-fuel welding | gas | steel rod | flame | low | medium | thin steel, brazing, heating, cutting |
| Brazing | gas | bronze/silver rod | flux | low | medium | dissimilar and thin metals, cast iron |

## Thickness quick guide (mild steel)

| Thickness | Stick | MIG | FCAW | TIG |
|---|---|---|---|---|
| 22-16 ga (.030-.060") | E6013 3/32 with care | .023/.030 short circuit | not ideal (.030 E71T-11 possible) | 1/16 tungsten, 20-60 A |
| 14 ga - 1/8" | E6013/E6011 1/8 | .030/.035 short circuit | .035 E71T-11 or T-1 | 3/32 tungsten, 60-130 A |
| 3/16 - 1/4" | E7018 1/8 - 5/32 | .035 short circuit (multi-pass) or .045 spray | .045 E71T-1 | 1/8 tungsten, 130-200 A |
| 5/16 - 1/2" | E7018 5/32 - 3/16, multi-pass | .045 spray/pulse, bevel over 1/4" | .045-.052 E71T-1, bevel | multi-pass, slow; MIG/FCAW preferred |
| over 1/2" | E7018 3/16 - 1/4, bevel, preheat as required | .045/.052 spray, bevel | .052-1/16 E71T-1 | root only |

Bevel anything thicker than about 1/4" for a full-penetration groove weld; a square butt on 1/2" plate does not fuse through with any hand process.

## What decides quality, whatever the process

1. **Fit-up and cleanliness** (mill scale, oil, paint, moisture).
2. **Correct polarity and consumable** for the process.
3. **Amperage and voltage inside the chart range**, then adjusted by ear and by bead shape.
4. **Travel speed and angle** consistent.
5. **Preheat** where thickness or carbon equivalent demands it.
6. **Stopping and starting** cleanly (crater fill, restarts ground).

## Setup articles

- [Stick (SMAW) setup](/article/smaw-stick-setup) and the [electrode amperage chart](/article/smaw-electrode-chart)
- [MIG (GMAW) setup](/article/gmaw-mig-setup) and [transfer modes: short-circuit, globular, spray, pulse](/article/gmaw-transfer-modes)
- [Gas-shielded flux-core (E71T-1)](/article/fcaw-gas-shielded-setup) and [self-shielded flux-core (E71T-11 / NR-211)](/article/fcaw-self-shielded-setup)
- [TIG (GTAW) setup](/article/gtaw-tig-setup) and [TIG settings by material](/article/gtaw-settings-by-material)
- [Shielding gas selection and flow rates](/article/gas-selection-and-flow)
- [Machine setup, duty cycle, cables and input power](/article/machine-setup-and-duty-cycle)
- [Oxy-acetylene setup (Victor)](/article/oxy-acetylene-setup-victor)
- [Brazing and soldering](/article/brazing-and-soldering)
