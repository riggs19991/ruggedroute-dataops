---
title: "How to Read a Coupling and Sheave Selection Table: Coupling Service Factors and Torque Ratings, Bore and Keyway Limits, Sheave Datum Diameter and Belt Section, Belt Length Tables, Arc of Contact and Belt Count from Rated Horsepower"
slug: how-to-read-a-coupling-and-sheave-selection-table
category: manuals
kind: reference
manufacturer: "Lovejoy / Rexnord Falk / TB Wood's / Gates / Dodge / Martin (generic)"
model_numbers: ["Lovejoy L-series jaw", "Falk Steelflex T", "Rexnord Omega", "TB Wood's Sure-Flex", "Gates Super HC", "Dodge QD sheaves", "Martin sheaves"]
tags: [coupling selection, coupling service factor, coupling torque rating, jaw coupling size chart, grid coupling selection, sheave selection, V belt selection, belt horsepower table, belt length table, datum diameter, pitch diameter, arc of contact, belt count, number of belts, QD bushing bore, max bore coupling, coupling catalogue, how to read selection table]
source: "Lovejoy jaw coupling catalogue (selection procedure, service factors, nominal torque, maximum bore); Rexnord Falk Steelflex selection guide; Gates Heavy Duty V-belt drive design manual (rated hp per belt, arc of contact and length correction factors); TB Wood's and Dodge sheave and QD bushing catalogues."
summary: "Manufacturer catalogues size couplings and V-belt drives through tables, and the tables only work if you use the right service factor, the right diameter definition and the correction factors printed in small type. This article explains the coupling selection page (torque rating, service factor, bore and keyway) and the belt drive page (rated hp per belt, arc and length corrections, belt count) with a worked example of each."
---

## Coupling selection page

1. **Service factor table** near the front lists applications (centrifugal pump 1.0, screw conveyor 1.5, reciprocating compressor 2.0 to 3.0, crusher 2.5 to 3.0). Pick the factor for the driven machine; add 0.25 for reversing duty on some brands.
2. **Design torque** (lb·in) = 63,025 × hp × SF ÷ rpm.
3. **Size table**: one row per coupling size with nominal torque (lb·in or Nm), maximum bore (in), maximum speed (rpm), misalignment capacity (parallel in, angular degrees), overall dimensions, and the elastomer or grid options. Choose the smallest size whose **nominal torque exceeds the design torque**, then check:
   - **maximum bore** takes both shafts (a coupling can fail selection on bore alone; go up a size),
   - **maximum speed** is above running speed (important for elastomeric couplings on 3550 rpm pumps),
   - **misalignment capacity** covers the installed alignment tolerance,
   - **keyway**: standard square keyways per ANSI B17.1 for the bore; a step-bore or a set-screw-only hub is not for interference fits.
4. Some tables list **hp per 100 rpm** instead of torque; multiply by rpm ÷ 100 and compare with hp × SF.

**Example**: 25 hp, 1750 rpm, screw conveyor, SF 1.5. Design torque = 63,025 × 25 × 1.5 ÷ 1750 = 1,351 lb·in. In the L-series jaw table, an L-150 (nominal 1,240 lb·in) is too small; an L-190 (1,728 lb·in, max bore 1.75 in) is the pick if both shafts are 1.75 in or smaller; a 1.875 in motor shaft forces an L-225.

## Elastomer inserts

The insert material has its own torque rating in the same table: NBR (Buna) baseline, urethane about 1.5 times, Hytrel about 3 times, bronze for slow high-torque duty. The coupling torque rating is the **lower** of the hub and the insert rating; changing spider material changes the selection.

## Sheave and belt selection page

V-belt catalogues follow a fixed order:

![V-belt drive selection steps with a worked example](/img/manuals/belt-selection-steps.svg)

*V-belt drive selection steps with a worked example*

1. **Service factor** (1.0 to 1.6 for electric motor drives, higher for engines and intermittent duty) → **design hp** = motor hp × SF.
2. **Belt section selection chart**: design hp against faster shaft rpm gives the section (3V, 5V, 8V for narrow belts; A, B, C, D for classical; 3VX/5VX and AX/BX for notched).
3. **Sheave diameter**: catalogues list **datum** (classical belts, formerly pitch) or **outside** diameter (narrow belts). Speed ratio uses datum diameters: ratio = driven datum ÷ driver datum. Keep the small sheave above the belt minimum (for example 5V: 4.4 in minimum; B: 5.4 in datum) and the belt speed under 6,500 ft/min for cast iron.
4. **Belt length table**: for the sheave pair and centre distance, read the belt number (5V1000 = 100 in outside length). The table also gives the exact centre distance for a standard belt; centres must allow about 1.5 percent shorter for installation and 3 percent longer for take-up.
5. **Rated hp per belt** table: enter with the small sheave rpm and diameter; read basic hp, then add the **speed ratio additional hp** column.
6. **Correction factors**: arc of contact (below 180° on the small sheave: 0.99 at 170°, 0.95 at 150°, 0.89 at 130°) and belt length (short belts below 1.00, long belts above). Corrected hp per belt = rated × arc × length.
7. **Belt count** = design hp ÷ corrected hp per belt, rounded up.

**Example**: 30 hp motor, 1750 rpm, driving a fan at 900 rpm, 16 hours a day, SF 1.3 → design 39 hp. Section 5V. Driver 7.1 in, driven 14.0 in outside (ratio 1.97). Centre distance 36 in → belt 5V850. Rated hp per belt at 1750 rpm and 7.1 in: about 10.5 plus 0.8 for ratio = 11.3; arc factor 0.97, length factor 0.98 → 10.7 per belt. 39 ÷ 10.7 = 3.6 → **4 belts**, so a 4-groove 5V sheave pair, matched set.

## Bushings

QD and taper-lock sheaves are listed with the **bushing size** (SH, SD, SK, SF, E, F, J, M for QD; 1108, 1610, 2517, 3020 for taper-lock) and the bushing table gives the maximum bore and the keyway. Bore the bushing, not the sheave. Bushing screws have their own torque table (QD SK: 15 ft·lb; SF: 30 ft·lb; E: 60 ft·lb), and a bushing overtightened past its rated torque splits the hub.

## Checking what was installed

Catalogues also let you audit an existing drive: count belts, read the sheave part numbers (they encode groove count, section and OD: 4/5V14.0 is four grooves, 5V, 14.0 in) and work backward to the hp the drive can carry. An undersized drive that keeps throwing belts is cheaper to fix by adding a groove than by replacing belts monthly.
