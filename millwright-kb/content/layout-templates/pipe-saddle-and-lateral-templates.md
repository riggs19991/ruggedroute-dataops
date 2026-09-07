---
title: "Pipe Saddle (Branch) and Lateral Templates: Ordinate Method for 90° Tees with Tables for 2\" to 8\" Branches, 45° Lateral Layout, Wrap-Around Marking, Cutting and Fitting the Branch, Header Hole Layout"
slug: pipe-saddle-and-lateral-templates
category: layout-templates
kind: procedure
tags: [pipe saddle, saddle template, branch template, fishmouth, pipe tee layout, ordinate method, pipe lateral, 45 degree lateral, lateral template, wrap around, pipe layout, branch connection, set on branch, set in branch, header hole, pipe fitting layout, pipe template, contour marker, pipe ordinates table, pipe circumference table]
source: "Ordinate formulas from the Pipe Fitter's and Pipe Welder's Handbook (Frankland) and the IPT Pipe Trades Handbook, computed here for ASME B36.10 pipe outside diameters; Curv-O-Mark/Flange Wizard marker instructions; general pipe-trades practice."
summary: "How to lay out the curved cut where a branch pipe meets a header (the saddle or fishmouth) by the ordinate method, with ready-computed ordinate tables for the common size combinations, the matching hole in the header, the 45° lateral variant, how to wrap the template and mark the pipe, cut with a torch or plasma, and grind to a fit with the right gap for welding."
---

## The idea

Unroll the branch pipe's circumference onto paper, divide it into 16 equal parts (element lines), and at each line mark how far back from a square cut the pipe must be cut so it sits down on the round header. Those distances are the **ordinates**. Wrap the paper on the branch, mark the curve through the points, cut, and the branch nests on the header.

```
   Ordinate at element line θ (measured around the branch from the side, 0° = the side of the branch that sits on the header's side, 90° = top/bottom centre):

       y(θ) = R − √( R² − (r · sin θ)² )        r = branch outside radius, R = header outside radius

   At the crotch (θ = 0, the sides of the branch) y = 0. At θ = 90° (the top and bottom of the branch, on the header's centreline) y is greatest.
```

Element lines run from the crotch (0°) to the centreline (90°) and back; the template is symmetrical, so you only need the 5 values for 0°, 22.5°, 45°, 67.5° and 90° and you repeat them.

## Ordinate tables (inches; branch OD on header OD, ASME B36.10 pipe)

Spacing of element lines around the branch = circumference ÷ 16.

| Branch (OD) | Circumference | Spacing (circ ÷ 16) |
|---|---|---|
| 2" (2.375) | 7.46" | 0.466" (15/32) |
| 3" (3.500) | 11.00" | 0.687" (11/16) |
| 4" (4.500) | 14.14" | 0.884" (7/8) |
| 6" (6.625) | 20.81" | 1.301" (1-5/16) |
| 8" (8.625) | 27.10" | 1.694" (1-11/16) |

Ordinates y at 0° / 22.5° / 45° / 67.5° / 90° (the 0° value is always 0; measure the others **back from a square line** at the branch end):

| Branch on header | 22.5° | 45° | 67.5° | **90°** (max) |
|---|---|---|---|---|
| **2" on 2"** | 0.090 | 0.348 | 0.733 | **1.188** |
| 2" on 3" | 0.060 | 0.215 | 0.387 | 0.465 |
| 2" on 4" | 0.046 | 0.163 | 0.286 | 0.339 |
| 2" on 6" | 0.031 | 0.108 | 0.187 | 0.220 |
| 2" on 8" | 0.024 | 0.083 | 0.142 | 0.167 |
| 2" on 10" | 0.019 | 0.066 | 0.113 | 0.133 |
| 2" on 12" | 0.016 | 0.056 | 0.095 | 0.112 |
| **3" on 3"** | 0.133 | 0.513 | 1.080 | **1.750** |
| 3" on 4" | 0.102 | 0.371 | 0.685 | 0.836 |
| 3" on 6" | 0.068 | 0.240 | 0.421 | 0.500 |
| 3" on 8" | 0.052 | 0.181 | 0.315 | 0.371 |
| 3" on 10" | 0.042 | 0.144 | 0.249 | 0.293 |
| 3" on 12" | 0.035 | 0.121 | 0.208 | 0.245 |
| **4" on 4"** | 0.171 | 0.659 | 1.389 | **2.250** |
| 4" on 6" | 0.114 | 0.407 | 0.733 | 0.881 |
| 4" on 8" | 0.087 | 0.304 | 0.534 | 0.633 |
| 4" on 10" | 0.069 | 0.241 | 0.418 | 0.494 |
| 4" on 12" | 0.058 | 0.202 | 0.348 | 0.410 |
| **6" on 6"** | 0.252 | 0.970 | 2.045 | **3.312** |
| 6" on 8" | 0.191 | 0.692 | 1.274 | 1.551 |
| 6" on 10" | 0.152 | 0.537 | 0.956 | 1.142 |
| 6" on 12" | 0.127 | 0.446 | 0.783 | 0.928 |
| **8" on 8"** | 0.328 | 1.263 | 2.662 | **4.312** |
| 8" on 10" | 0.260 | 0.949 | 1.767 | 2.167 |
| 8" on 12" | 0.217 | 0.777 | 1.398 | 1.680 |

Equal-size branches: the 90° ordinate is simply the pipe radius (a 6" on 6" saddle cuts back 3.312", half the OD). Any other combination: use the formula with a calculator; for a **set-in** branch (branch goes into a hole in the header, flush with the inside) use the header's **inside** radius for R and the branch OD for r. In practice set-on (branch sits on the header's outside) is what a millwright makes; set-in is a fabrication-shop detail.

## Making the template (set-on 90° branch)

1. Paper or thin cardboard (or a used gasket sheet, or a strip of roofing felt) at least the branch circumference plus 1" long and the max ordinate plus 2" wide. A "wrap-around" of 1/16" rubber is the pipefitter's straightedge for marking the square line.
2. Draw a **base line** along the length and mark 16 equal spaces (use the spacing table, or step off the circumference with dividers: measure the actual pipe with a tape and divide by 16).
3. Number the element lines 0 to 16; **0, 8 and 16 are the crotch (sides)** with ordinate 0; **4 and 12 are the centreline** (top and bottom, on the header's centreline) with the maximum ordinate. Lines 1-3 and 5-7 (and the mirror) get the 22.5°, 45°, 67.5° values.
4. Square up from each element line by its ordinate and mark a point; draw a fair curve through the points (a flexible batten or a French curve).
5. Cut along the curve. Wrap the template around the branch with the base line on a square line, the 0/8/16 lines on the **sides** of the branch (the plane of the header's axis), tape it, and mark the curve with soapstone or a silver pencil.
6. Mark the **centreline** of the branch on the pipe too, so you can orient it on the header.

## Laying out the hole in the header

For a set-on branch the hole is the branch's **inside** diameter projected onto the header: use a centre finder/contour marker to draw the header's longitudinal centreline, mark the branch centre point, and lay out the hole with the branch's ID as the width across the header (along the circumference) and, along the header's axis, the same ID (seen from above it is a circle of the branch ID; unrolled flat it becomes a slight ellipse). Practical method: set the cut branch on the header where it goes, scribe around the inside of it, and cut 1/8" inside the scribed line, then grind to the line. For **reinforced** or code branches, the hole and weld are per the drawing (weldolets and reinforcing pads are used above certain sizes and pressures).

## 45° lateral

For a branch entering the header at 45° the ordinates are no longer symmetrical: the **heel** side is long and the **throat** side is short. General formula for a branch at angle α measured around the branch from the heel line (θ):

```
   L(θ) = [ R − √( R² − (r · sin θ)² ) ] ÷ sin α  +  r · cos θ ÷ tan α
```

Take the smallest value as zero and measure the others from a square line. For a 45° lateral with the branch equal to the header, the throat point (θ = 180°) is 0, the heel (θ = 0) is about the pipe OD back from it, and the side points fall between. Computed examples (inches, 9 points from heel to throat, 22.5° apart): **2" on 2"**: 2.375, 2.412, 2.519, 2.679, 2.867, 1.770, 0.840, 0.218, 0; **4" on 6"**: 4.500, 4.490, 4.417, 4.148, 3.497, 2.426, 1.235, 0.332, 0; **6" on 8"**: 6.625, 6.642, 6.633, 6.382, 5.506, 3.847, 1.948, 0.522, 0. Notice the ordinate is not maximum at the heel on unequal sizes (the heel curls back a little); draw a fair curve and trust it. The hole in the header is an elongated (elliptical) opening; scribe it from the cut branch set in position.

Nowadays a **pipe layout app or a template program** prints these for any size and angle; the method above is what you do when the phone is dead.

## Cutting and fitting

1. Cut with a torch or plasma **on the waste side** of the line, torch tilted to follow the bevel: for a set-on branch the cut is bevelled **outward** on the top and bottom (centreline) where the branch meets the header at 90°, and nearly square at the crotch where it meets at a glancing angle: a varying bevel (the reason saddles are ground after cutting).
2. Grind to the line; try it on the header; mark the high spots with soapstone; grind again. Target **1/16-1/8" gap all round** for a fillet or a groove weld per the drawing; a gap over 3/16" at the crotch is a sign the ordinates were measured from the wrong reference.
3. Set the branch on its centreline mark (contour marker/centre finder on the header for the longitudinal line; a **level or a square across the header** for plumb), tack at the four quarter points, check square with a framing square against the header, then weld.
4. Weld sequence for a branch: quarters, alternating, starting at the crotches where the fit is tightest.

## Common mistakes

- Wrapping the template with the 0 line on the top of the branch instead of on the side: the saddle comes out rotated 90° and does not fit anything.
- Using the header's nominal size (6") instead of its OD (6.625) for R.
- Forgetting the cut is measured **back** from the square end: the branch is short.
- Cutting on the line instead of the waste side: no metal left to grind to a fit.
- Not allowing for the varying bevel: the branch fits at the crotch and gaps at the top.

## Related

- [Pipe miter layout and fitting take-outs](/article/pipe-miter-layout)
- [Layout tools and scribing](/article/layout-tools-and-scribing)
- [Trig and layout formulas](/article/trig-and-layout-formulas)
- [Oxy-fuel cutting technique](/article/oxy-fuel-cutting-technique)
- [Joint design and fit-up](/article/joint-design-and-fit-up)
