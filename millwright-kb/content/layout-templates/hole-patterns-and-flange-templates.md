---
title: "Bolt-Hole Patterns and Flange Templates: Chord Factor Table (3 to 24 Holes), Laying Out a Bolt Circle with Dividers or Coordinates, Straddling the Centrelines, Making and Using a Drilling Template, Transfer Punching, Hole Clearance Sizes, ASME B16.5 Class 150 Bolt Circles"
slug: hole-patterns-and-flange-templates
category: layout-templates
kind: chart
tags: [bolt circle, bolt hole pattern, chord factor, chord table, bolt circle layout, PCD, pitch circle diameter, flange template, drilling template, transfer punch, hole clearance, straddle centerlines, two hole rule, flange bolt holes, class 150 bolt circle, B16.5, motor mounting holes, coordinate layout, hole pattern coordinates, template plate]
source: "Chord factor mathematics (chord = D × sin(180°/N)); Machinery's Handbook jig-boring coordinate tables; ASME B16.5 Class 150 flange dimensions (bolt circle, number and size of bolts, hole diameter); standard clearance-hole practice (ASME B18.2.8)."
summary: "How to lay out any number of equally spaced holes on a bolt circle with a chord table or coordinates, why flange holes straddle the centrelines and how to orient a flange, how to make a reusable drilling template from a mating part or a drawing and use transfer punches, the clearance hole sizes to drill for bolts, and the Class 150 flange bolt-circle table for pipe sizes 1/2 to 12 inch."
---

## Chord factor table

Set the dividers to the **chord** between adjacent holes and step round the circle; if the last step lands on the first mark, the layout is good.

```
   chord = bolt circle diameter (D) × sin(180° ÷ N)         N = number of holes
```

| N holes | Chord factor (× D) | N holes | Chord factor (× D) |
|---|---|---|---|
| 3 | 0.8660 | 12 | 0.2588 |
| **4** | **0.7071** | 13 | 0.2393 |
| 5 | 0.5878 | 14 | 0.2225 |
| **6** | **0.5000** | 15 | 0.2079 |
| 7 | 0.4339 | **16** | **0.1951** |
| **8** | **0.3827** | 17 | 0.1838 |
| 9 | 0.3420 | 18 | 0.1736 |
| 10 | 0.3090 | 19 | 0.1646 |
| 11 | 0.2817 | **20** | **0.1564** |
| | | 24 | 0.1305 |

Example: 8 holes on a 7.50" bolt circle (4" Class 150 flange): chord = 7.50 × 0.3827 = **2.870"**.

## Laying out a bolt circle with dividers

1. Find and prick-punch the **centre** (diagonals on a plate; centre head on a round).
2. Scribe the **bolt circle** with dividers or trammels set to D/2.
3. Scribe the **two centrelines** at 90° through the centre (combination square on a plate edge, or the surface gauge method).
4. Decide whether holes go **on** the centrelines or **straddle** them (below). For straddling, the first hole is at 180°/N from the centreline (45° for 4 holes, 22.5° for 8): scribe that angle with a protractor head, or mark it as half a chord from the centreline along the circle.
5. Set dividers to the chord from the table; put one leg in the first hole's prick mark and step round, punching lightly at each step. Check that you close on the first mark within the width of a scribed line; if not, adjust the dividers by a fraction of the total error ÷ N and start again.
6. Centre-punch each mark, then drill with a pilot and the clearance drill.

For large circles (over about 2 ft) trammels replace dividers; for many holes, mark opposite pairs first (4 holes at 90°) to keep the error from accumulating, then subdivide.

## Coordinate method (no dividers, better for a drill press with a DRO or a mag drill from a straightedge)

Hole k of N on a bolt circle of radius R, with hole 1 at angle θ₁ from the X axis:

```
   angle_k = θ₁ + (k − 1) × 360°/N
   X_k = R × cos(angle_k)         Y_k = R × sin(angle_k)          (from the centre; add the centre's coordinates from the datum edges)
```

Example: 6 holes, R = 3", straddling the X axis (θ₁ = 30°): angles 30, 90, 150, 210, 270, 330; X = 2.598, 0, −2.598, −2.598, 0, 2.598; Y = 1.5, 3, 1.5, −1.5, −3, −1.5. Measure each hole from the two datum edges with a rule or the DRO.

## Straddling the centrelines

Pipe flanges, valve bodies, pump and motor flanges are drilled with the holes **straddling** the vertical and horizontal centrelines ("two-holing" a flange): no hole sits on the centreline. That way, every flange in the plant mates with every other in the same orientation and the top two holes are level. To set a flange:

1. Mark the top (12 o'clock) line on the pipe (contour marker / level).
2. Put a **level across the two top holes** (a "two-hole pin" set or a spirit level on two bolts): when level, the holes straddle the vertical centreline. Tack, recheck, weld.
3. Equipment nozzles that are drawn "holes on centreline" are the exception and are noted on the drawing.

## Clearance holes

| Bolt | Close fit | **Normal (standard)** | Loose fit |
|---|---|---|---|
| 1/4" | 17/64 (0.266) | **9/32 (0.281)** | 19/64 |
| 5/16" | 21/64 | **11/32 (0.344)** | 23/64 |
| 3/8" | 25/64 | **13/32 (0.406)** | 27/64 |
| 1/2" | 33/64 | **9/16 (0.562)** | 39/64 |
| 5/8" | 41/64 | **11/16 (0.688)** | 47/64 |
| 3/4" | 25/32 | **13/16 (0.812)** | 29/32 |
| 7/8" | 29/32 | **15/16 (0.938)** | 1-1/32 |
| 1" | 1-1/32 | **1-1/16 (1.062)** | 1-5/32 |
| M8 | 8.4 mm | **9 mm** | 10 mm |
| M10 | 10.5 | **11** | 12 |
| M12 | 13 | **13.5 (14)** | 15 |
| M16 | 17 | **17.5 (18)** | 19 |
| M20 | 21 | **22** | 24 |

Structural steel (AISC): standard holes are **bolt + 1/16"** (up to 7/8" bolts; bolt + 1/8" for 1" and over); ASME flanges have holes **1/8" larger than the bolt**; machine bases: bolt + 1/16 to 1/8". Oversize and slotted holes only where the drawing allows.

## Making a drilling template

From a mating part (a motor, a gearbox foot, a flange): the most reliable way to get holes that match.

1. Material: 1/8-1/4" plate for a template you will reuse or drill through; hardboard or plywood for a one-off you only mark from; clear acrylic when you need to see the layout underneath.
2. **Datum**: scribe centrelines on the template, and mark which side is "up" and which edge is the datum, before anything else.
3. Transfer the holes: either **clamp the template to the mating part and mark through the holes** with a transfer punch (a punch that fits the hole with a centre point) or a scriber run round the hole, or lay out from the drawing with the chord method above.
4. Drill the template holes **at bushing size** (the pilot drill size, e.g. 1/4") for a marking template, or at full clearance size with hardened **drill bushings** pressed in for a production template.
5. Deburr, stamp the template with the part number and the hole size, and hang it on a nail with the drawing number.
6. Use: clamp the template on the work at the datum, **transfer-punch** each hole (or spot with the pilot drill through the template), remove the template, centre-punch, drill the pilot then the clearance size.

For **anchor-bolt templates** (a frame that holds the anchor bolts in the wet concrete) see [anchor bolts and foundations](/article/anchor-bolts-and-foundations): plywood or steel, holes at the base's clearance size, diagonals checked, braced so it cannot move during the pour.

**Transfer punch set**: a set of punches in 1/64" steps from 3/32" to 1/2"; the punch fills the hole and the point marks the centre exactly. Transfer screws (screwed into tapped holes, with a point) do the same from a threaded part.

## ASME B16.5 Class 150 flanges (raised face)

| NPS | Flange OD | **Bolt circle** | Holes | Bolt size | Hole Ø |
|---|---|---|---|---|---|
| 1/2" | 3.50 | 2.38 | 4 | 1/2" | 5/8 |
| 3/4" | 3.88 | 2.75 | 4 | 1/2" | 5/8 |
| 1" | 4.25 | 3.12 | 4 | 1/2" | 5/8 |
| 1-1/4" | 4.62 | 3.50 | 4 | 1/2" | 5/8 |
| 1-1/2" | 5.00 | 3.88 | 4 | 1/2" | 5/8 |
| **2"** | 6.00 | **4.75** | 4 | 5/8" | 3/4 |
| 2-1/2" | 7.00 | 5.50 | 4 | 5/8" | 3/4 |
| **3"** | 7.50 | **6.00** | 4 | 5/8" | 3/4 |
| **4"** | 9.00 | **7.50** | 8 | 5/8" | 3/4 |
| 5" | 10.00 | 8.50 | 8 | 3/4" | 7/8 |
| **6"** | 11.00 | **9.50** | 8 | 3/4" | 7/8 |
| **8"** | 13.50 | **11.75** | 8 | 3/4" | 7/8 |
| 10" | 16.00 | 14.25 | 12 | 7/8" | 1 |
| 12" | 19.00 | 17.00 | 12 | 7/8" | 1 |

Class 300 flanges are larger with more/bigger bolts (a 4" Class 300 is 10.00" OD, 7.88" bolt circle, 8 × 3/4" bolts); full tables in [pipe schedule and flange tables](/article/pipe-schedule-and-flange-tables). Chord for a Class 150 4" (8 holes on 7.50): 2.870"; 6" (8 on 9.50): 3.636"; 8" (8 on 11.75): 4.497"; 3" (4 on 6.00): 4.243".

## Common mistakes

- Holes on the centreline instead of straddling: the flange goes on 22.5° off and the pipe is twisted.
- Stepping dividers round without checking the closure: the last space is 1/8" short.
- Drilling clearance holes at the bolt size: the bolts will not go in when the pattern is 1/32" off.
- Template with no datum mark: it gets used upside down and mirrored.
- Marking from a rusty flange's holes without cleaning them: the transfer punch centres on the rust.

## Related

- [Layout tools and scribing](/article/layout-tools-and-scribing)
- [Trig and layout formulas (bolt circles and coordinates)](/article/trig-and-layout-formulas)
- [Pipe schedule and flange tables](/article/pipe-schedule-and-flange-tables)
- [Hole making in the field](/article/hole-making-in-the-field)
- [Anchor bolts and foundations](/article/anchor-bolts-and-foundations)
