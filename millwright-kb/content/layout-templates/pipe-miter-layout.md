---
title: "Pipe Miter Layout and Fitting Take-Outs: 2-, 3-, 4- and 5-Piece Mitered Elbows with Cut-Back Tables, Miter Templates, Offsets by Angle (45°, 60°, 30°, 22.5°) with Constants, Rolling Offsets, Butt-Weld Elbow and Tee Take-Outs (ASME B16.9), Cut Length Math"
slug: pipe-miter-layout
category: layout-templates
kind: chart
tags: [pipe miter, mitered elbow, miter cut, cutback, 2 piece elbow, 3 piece elbow, 4 piece elbow, miter template, pipe offset, 45 degree offset, offset travel, rolling offset, fitting take out, take-out, elbow center to face, long radius elbow, 1.5 x NPS, ASME B16.9, weld gap, cut length, pipe fitting math, pipe circumference, lobster back]
source: "Miter geometry computed for ASME B36.10 outside diameters; ASME B16.9 butt-welding fitting centre-to-face dimensions; Pipe Fitter's and Pipe Welder's Handbook (Frankland) offset constants; IPT Pipe Trades Handbook."
summary: "How to lay out and cut mitered elbows of any number of pieces with the cut-back tables for common pipe sizes and a wrap-around template method, the standard offset constants for calculating travel and run at any angle including rolling offsets, and the butt-weld fitting take-out numbers you subtract to get cut lengths of pipe between fittings."
---

## Mitered elbows

A miter is an elbow made by cutting pipe at an angle and welding the pieces. For a total bend angle A made of n pieces there are (n − 1) joints and the two end pieces are half-segments:

![Two- and three-piece mitred elbows and the cut-angle rule](/img/layout-templates/miter-elbow-layout.svg)

*Two- and three-piece mitred elbows and the cut-angle rule*

```
   cut angle at each joint (measured from a square cut)  θ = A ÷ [2 × (n − 1)]
   cut-back at the outside of the pipe (from the square line to the long point)  C = (OD ÷ 2) × tan θ
   the cut runs from +C on the outside of the bend to −C on the inside: total difference between long and short sides = 2C = OD × tan θ
```

| Elbow | Pieces | Joints | θ (cut angle) | Segment angle |
|---|---|---|---|---|
| 2-piece 90° | 2 | 1 | **45°** | 90° at one joint |
| 3-piece 90° | 3 | 2 | **22.5°** | 45° per joint |
| 4-piece 90° | 4 | 3 | **15°** | 30° per joint |
| 5-piece 90° | 5 | 4 | 11.25° | 22.5° per joint |
| 2-piece 45° | 2 | 1 | 22.5° | |
| 3-piece 45° | 3 | 2 | 11.25° | |

Codes (ASME B31.3) limit miter angles by pressure: over about 22.5° per joint a miter is a "single miter" with reduced pressure rating; 3-piece and 4-piece 90s are the usual pressure-piping miters, 2-piece only on low-pressure and duct work.

### Cut-back table C (inches) at the pipe's outside surface

| Pipe (OD) | 2-piece (45°) | 3-piece (22.5°) | 4-piece (15°) | 5-piece (11.25°) |
|---|---|---|---|---|
| 2" (2.375) | 1.188 | 0.492 | 0.318 | 0.236 |
| 3" (3.500) | 1.750 | 0.725 | 0.469 | 0.348 |
| 4" (4.500) | 2.250 | 0.932 | 0.603 | 0.448 |
| 6" (6.625) | 3.312 | 1.372 | 0.888 | 0.659 |
| 8" (8.625) | 4.312 | 1.786 | 1.156 | 0.858 |
| 10" (10.75) | 5.375 | 2.226 | 1.440 | 1.069 |
| 12" (12.75) | 6.375 | 2.641 | 1.708 | 1.268 |

For any other size: C = OD/2 × tan θ.

### Laying out a miter cut on the pipe

**Method 1, two marks and a wrap-around**: square a line around the pipe with the wrap-around; on the **outside of the bend** measure C up from it and mark; on the **inside** measure C down and mark; on both sides (90° round) mark on the square line. Wrap the wrap-around through those four points: it lies along the elliptical cut line. Mark. (Works because a plane cut through a cylinder is an ellipse that a flat wrap follows.)

**Method 2, ordinate template** (for accurate large miters or thick wall): divide the circumference into 16, ordinate at element line k is `C × cos(k × 22.5°)`, i.e. +C, +0.924C, +0.707C, +0.383C, 0, −0.383C, −0.707C, −0.924C, −C and back; plot on paper, cut, wrap.

**Method 3, angle finder**: for a single piece cut, set a bevel protractor or a magnetic angle finder on the pipe and mark the two sides, then join with the wrap.

### Piece lengths for a miter elbow of centreline radius R

For an n-piece 90° elbow with centreline radius R (choose R ≈ 1.5 × NPS like a long-radius elbow, or whatever the drawing says), the developed centreline length is `π × R ÷ 2`, and each **middle piece** measures `2 × R × tan θ` on the centreline; each **end piece** measures `R × tan θ` plus the straight tangent you need. Lay out each piece with the miter on both ends (middle pieces) rotated so the long points are all on the outside of the bend, and mark **"top" and the centreline** on every piece before cutting or you will assemble a corkscrew.

### Fitting a miter

Bevel every cut 30-37.5° (the bevel angle changes as the cut turns: grind), leave a root gap of 1/16-3/32", tack the pieces on a flat surface with the centrelines aligned, check the total angle with a framing square or protractor against a straightedge on each end, then weld.

## Offsets

An offset moves a pipe run sideways using two equal fittings (elbows) at an angle. The three sides of the right triangle: **offset** (the sideways distance, centre to centre), **run** (the distance along the original direction), **travel** (the centre-to-centre length of the diagonal pipe plus fittings).

```
   travel = offset × (1 ÷ sin A)          run = offset × (1 ÷ tan A)
```

| Fitting angle A | travel = offset × | run = offset × | offset = travel × |
|---|---|---|---|
| **45°** | **1.414** | **1.000** | 0.707 |
| 60° | 1.155 | 0.577 | 0.866 |
| 30° | 2.000 | 1.732 | 0.500 |
| 22.5° | 2.613 | 2.414 | 0.383 |
| 11.25° | 5.126 | 5.027 | 0.195 |
| 90° | 1.000 (the offset is a straight leg) | 0 | |

**Cut length of the diagonal pipe** = travel − (take-out of the first fitting) − (take-out of the second fitting) − weld gaps (for butt-weld) or + thread engagements (threaded).

### Rolling offset

The pipe has to move sideways **and** up/down: the true offset is the diagonal of a box, `true offset = √(horizontal² + vertical²)`; then use the table with the true offset. The **rotation angle** of the fittings from the vertical is `tan⁻¹(horizontal ÷ vertical)`. Set the two elbows on the pipe at that roll angle using an angle finder or the box method (lay a framing square with the two offsets as its legs and measure the diagonal).

Worked example: 6" offset sideways and 8" up with 45° fittings: true offset = √(36 + 64) = 10"; travel = 10 × 1.414 = 14.14"; run = 10"; roll = tan⁻¹(6/8) = 36.9° from vertical.

## Butt-weld fitting take-outs (ASME B16.9, centre to face)

| Fitting | Take-out | 2" | 3" | 4" | 6" | 8" | 10" | 12" |
|---|---|---|---|---|---|---|---|---|
| **90° long radius elbow** | **1.5 × NPS** | 3" | 4-1/2" | 6" | 9" | 12" | 15" | 18" |
| 90° short radius elbow | 1.0 × NPS | 2" | 3" | 4" | 6" | 8" | 10" | 12" |
| **45° long radius elbow** | 0.625 × NPS (B16.9 rounds) | 1-3/8" | 2" | 2-1/2" | 3-3/4" | 5" | 6-1/4" | 7-1/2" |
| 180° return LR, centre to centre | 3 × NPS | 6" | 9" | 12" | 18" | 24" | 30" | 36" |
| Straight tee, centre to run end (C) | | 2-1/2" | 3-3/8" | 4-1/8" | 5-5/8" | 7" | 8-1/2" | 10" |
| Cap, length | | 1-1/2" | 2" | 2-1/2" | 3-1/2" | 4" | 5" | 6" |
| Concentric reducer, length | | 3" | 3-1/2" | 4" | 5-1/2" | 6" | 7" | 8" |

The 45° take-outs are the B16.9 values for the sizes shown (they are not exactly 0.625 × NPS at every size: 2" is 1-3/8", not 1-1/4"). Flanges: weld-neck flange length from the face to the weld end is in ASME B16.5 by class (a 4" class 150 WN is 3" long; 6" is 3-1/2"). Threaded and socket-weld fittings (B16.11) have their own centre-to-end dimensions and you add thread make-up (about 1/2" per end on 1", 3/4" on 2") or subtract socket depth minus the 1/16" gap.

### Cut-length math (butt weld)

```
   pipe cut length = centre-to-centre dimension − take-out(fitting 1) − take-out(fitting 2) − gap(1) − gap(2)
   gap = root opening, typically 1/8" (3/32-1/8") per weld
```

Example: two 6" LR 90s, 4'-0" centre to centre: 48 − 9 − 9 − 0.125 − 0.125 = **29-3/4"**.

For a run with a tee: subtract the tee's centre-to-end (C) on that side. Always mark the centrelines on the fittings and the pipe before tacking; **check the weld gap with a 1/8" rod or gap gauge**, square the fitting with a level or a framing square on the flange face or the fitting's opposite end, tack at the quarters.

## Common mistakes

- Using nominal size instead of OD in the miter cut-back.
- Miter long points not all on the outside of the bend: a snake instead of an elbow.
- Forgetting the weld gaps: every pipe comes up 1/4" short per pair of fittings.
- Mixing LR and SR elbows on the same run: the take-outs are not the same.
- Rolling offset done as two separate offsets: twice the fittings and a leak-prone mess.

## Related

- [Pipe saddle and lateral templates](/article/pipe-saddle-and-lateral-templates)
- [Trig and layout formulas (offsets, tapers, bolt circles)](/article/trig-and-layout-formulas)
- [Pipe schedule and flange tables](/article/pipe-schedule-and-flange-tables)
- [Layout tools and scribing](/article/layout-tools-and-scribing)
- [Blueprint reading (isometrics)](/article/blueprint-reading-for-millwrights)
