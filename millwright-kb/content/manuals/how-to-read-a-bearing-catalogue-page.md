---
title: "How to Read a Bearing Catalogue Page: Designation Codes, Dimensions and Chamfers, Dynamic and Static Load Ratings, Limiting Speeds, Fatigue Load Limit, Suffixes and Prefixes, Mass, and How to Cross-Reference Brands"
slug: how-to-read-a-bearing-catalogue-page
category: manuals
kind: reference
manufacturer: "SKF / FAG (Schaeffler) / NSK / NTN / Timken (generic)"
model_numbers: ["SKF 6205-2RS1", "SKF 22220 E", "FAG 6205-2RSR", "NSK 6205DDU", "NTN 6205LLU", "Timken 6205-2RS"]
tags: [bearing catalogue, bearing catalog, how to read bearing catalogue, bearing designation, bearing number, dynamic load rating, C rating, static load rating, C0, limiting speed, reference speed, bearing suffix, bearing prefix, 2RS, ZZ, C3, bearing dimensions, bearing cross reference, interchange, bearing mass, fatigue load limit]
source: "SKF Rolling Bearings catalogue (product table layout and designation system); Schaeffler FAG catalogue HR1; NSK and NTN ball and roller bearing catalogues; ISO 15 (boundary dimensions), ISO 281 (dynamic load ratings and life)."
summary: "The catalogue page for a bearing series is a table of numbers that answers most questions a millwright asks: will it fit, how much load can it take, how fast can it run, and what do the letters on the end mean. This article walks a standard deep-groove and spherical roller page column by column and explains how to cross-reference between brands."
---

## The page layout

A catalogue page for a series (for example deep groove ball bearings, 60 series) has a drawing at the top with dimension letters, then a table with one row per bearing size. Columns run in this order on most brands:

![One row of a bearing catalogue table explained](/img/manuals/bearing-catalogue-row.svg)

*One row of a bearing catalogue table explained*

1. **Principal dimensions**: d (bore), D (outside diameter), B (width), all in mm.
2. **Basic load ratings**: C (dynamic), C0 (static), in kN.
3. **Fatigue load limit** Pu (kN) on SKF and FAG pages.
4. **Speed ratings**: reference speed and limiting speed, rpm.
5. **Mass**, kg.
6. **Designations**: the open bearing, then sealed and shielded variants.
7. A second table of **abutment and fillet dimensions**: da, Da (shoulder diameters), ra (max fillet radius the bearing chamfer will clear).

## Designation codes

A basic designation is series + bore code: **6205** is series 62 (deep groove, medium-light) and bore code 05. Bore codes: 00 = 10 mm, 01 = 12, 02 = 15, 03 = 17; from 04 upward multiply by 5 (04 = 20 mm, 05 = 25, 12 = 60, 20 = 100).

The first digit(s) give the type: 6 deep groove ball, 7 angular contact ball, 1 self-aligning ball, 2 spherical roller (22, 23), N/NU/NJ cylindrical roller, 3 tapered roller (metric), 5 thrust ball, K needle. The next digit is the dimension series (width and diameter series): 60 lighter, 62 medium, 63 heavy, 64 heaviest for the same bore.

## Prefixes and suffixes

Suffixes carry the details you must match when ordering:

| Suffix | Meaning |
|---|---|
| 2RS1 / 2RSR / DDU / LLU / 2RS | contact rubber seal both sides (SKF / FAG / NSK / NTN / Timken) |
| RS1 (one side) | seal one side |
| 2Z / ZZ / 2ZR | metal shield both sides |
| C3, C4 | internal clearance larger than normal (C3 for most hot or interference-fit motor applications); C2 smaller |
| CN | normal clearance (often not marked) |
| E | reinforced design (larger rollers, higher rating) |
| K | tapered bore 1:12 for adapter sleeves; K30 = 1:30 |
| M, MA, MB | machined brass cage, guided by rollers or by outer/inner ring |
| J, TN9, TVP | pressed steel cage; glass-fibre polyamide cage |
| P5, P6 | precision class (ABEC 5, ABEC 3) |
| W33 | lubrication groove and holes in the outer ring (spherical rollers) |
| /C3, /W64 | slash suffixes: clearance, grease type (SKF) |
| VA405, HT | special heat-stabilized or high-temperature variant |

A prefix such as **W** (stainless) or **E2.** (energy efficient, SKF) modifies the whole bearing.

## Load ratings

- **C, basic dynamic load rating**: the constant radial load a group of identical bearings can take for one million revolutions with 90 percent surviving. It is a comparison number, not a working load.
- **C0, basic static load rating**: the load that produces a permanent indentation of 0.0001 times the rolling element diameter. Stationary or slow oscillating bearings are selected against C0; shock loads at rest also.
- **Pu, fatigue load limit**: loads below this, with clean oil and good lubrication, give theoretically unlimited life.

Life estimate: **L10 (millions of revolutions) = (C ÷ P)^p** with p = 3 for ball bearings and 10/3 for roller bearings, P the equivalent dynamic load. In hours: L10h = 1,000,000 ÷ (60 × rpm) × (C ÷ P)^p. A 6205 (C = 14.8 kN) under 1.5 kN at 1750 rpm: (14.8 ÷ 1.5)³ = 961 million rev = 9,150 hours. That is why a lightly loaded motor bearing outlasts a heavily loaded pump bearing many times over.

## Speed ratings

- **Reference speed**: the speed at which the bearing reaches a stable 70 °C under a standard light load with oil bath or normal grease. Above it you need to check the thermal limit.
- **Limiting speed**: the mechanical maximum for the cage and seals. Contact seals (2RS) cut the limit sharply; shields (2Z) barely change it.

## Dimensions that bite

- **Chamfer r (rs min)**: the housing and shaft fillet radius must be **smaller** than this or the bearing sits on the fillet and runs out of square.
- **Shoulder diameters da, Da**: the minimum shaft shoulder and maximum housing shoulder so the rings, not the cage, are supported.
- Sealed bearings can be a fraction wider than the open version on some series; check B.

## Cross-referencing brands

Boundary dimensions are ISO standard, so a 6205 from any brand fits the same seat. What changes is suffix spelling and the load rating (an E design may rate higher). Match:

1. Basic number (6205, 22220).
2. Seal or shield type (2RS1 = 2RSR = DDU = LLU).
3. Clearance (C3 in all brands).
4. Cage material for high speed or high temperature.
5. Tapered bore (K) and any W33 groove on sphericals.

Then confirm the ratings in the new catalogue are equal or better. A bearing interchange is a mechanical statement and belongs on the work order.

## Related

- [Decoding Bearing Numbers](/article/bearing-designation-codes)
- [Bearing Fits, Internal Clearance and Shaft/Housing Tolerances](/article/bearing-clearance-and-fits-tables)
- [Shaft, Bearing and Fastener Formulas](/article/shaft-bearing-fastener-formulas)
- [How to Add a Manufacturer Manual or Datasheet to This Library](/article/how-to-add-a-manual)
