---
title: "Sheet-Metal Developments: Parallel-Line (Truncated Cylinders, Elbows), Radial-Line (Cones, Truncated Cones, Hoppers), Triangulation (Square-to-Round Transitions), Bend Allowance and Setback with K-Factor, Minimum Bend Radius, Seam and Hem Allowances"
slug: sheet-metal-developments
category: layout-templates
kind: procedure
tags: [sheet metal layout, pattern development, development, parallel line development, radial line development, triangulation, cone layout, truncated cone, cone pattern, square to round, transition piece, hopper layout, chute layout, duct elbow, bend allowance, bend deduction, K factor, setback, flat pattern, minimum bend radius, press brake, hem allowance, seam allowance, Pittsburgh lock, stretchout]
source: "Sheet Metal Technology and standard pattern-development texts (parallel, radial, triangulation methods); Machinery's Handbook bend allowance and K-factor; press-brake maker guidance on minimum inside radius by material; NAVEDTRA Steelworker manual."
summary: "The three classical ways to draw a flat pattern that folds or rolls into a 3-D sheet part, with step lists for the shapes a millwright makes (chute sections, cylinder cut at an angle, duct elbows, cones and hopper sections, square-to-round transitions), the bend allowance formula and K-factors for press-brake work with a worked example, minimum inside bend radii by material, and the allowances for seams and hems."
---

## Which method

| Shape | Surfaces | Method |
|---|---|---|
| Cylinders and prisms cut square or at an angle, pipe-style elbows, tees on cylinders | Parallel edges (elements are parallel) | **Parallel-line** |
| Cones, truncated cones, pyramids, hoppers with a common apex | Elements meet at a point | **Radial-line** |
| Square-to-round, rectangle-to-round, offset transitions, anything twisted | No common apex, no parallel elements | **Triangulation** |
| Flat parts with bends (brackets, boxes, guards) | Flat with bend lines | **Bend allowance** flat pattern |

Draw the developments at full size on paper, hardboard or directly on the sheet with dye; keep the drawing's **seam** where it does the least harm (the shortest element, the back, away from the wear side).

## Parallel-line development: a cylinder cut at an angle (chute elbow, 2-piece duct elbow)

1. Draw the **elevation** (side view) showing the cylinder and the angled cut, and the **plan** (end view): a circle of the cylinder's diameter (use the **mean** diameter for thick material: ID + t).
2. Divide the circle into **12 equal parts** (16 for accuracy on big work) and number them 1-12; project each division point up into the elevation as a vertical **element line** to the cut line.
3. Draw the **stretch-out line**: a horizontal line whose length is the circumference (π × mean diameter); mark the 12 (or 16) equal spaces along it and number them to match, starting and ending at the seam element.
4. At each numbered point, square up a line and project across from the elevation the **height** of the same-numbered element (where it meets the angled cut). Transfer with dividers or a straight projection line.
5. Join the tops with a fair curve: that is the pattern; add seam and hem allowances (below). The bottom is straight (a square cut).

**2-piece elbow**: the same pattern cut twice from one stretch-out, nested (one inverted) so nothing is wasted. **3- and 4-piece elbows**: the middle pieces have the angled cut on both ends (draw both curves). **Tee on a cylinder**: the branch is a parallel-line development of the branch cut to the header's curve (same as the pipe saddle, see [pipe saddle templates](/article/pipe-saddle-and-lateral-templates)).

## Radial-line development: a cone and a truncated cone (hopper, reducer, funnel)

Full cone with base diameter D and slant height S (the distance from the apex to the base edge along the surface):

```
   S = √( (D/2)² + H² )                       H = vertical height
   pattern: a sector of a circle of radius S, with an included angle  A = 360° × (D/2) ÷ S  = 180° × D ÷ S
   arc length of the sector = π × D (the base circumference)
```

Truncated cone (big diameter D, small diameter d, height H):

1. Draw the elevation; extend the sides to the apex. Slant height to the big end S = √((D/2)² + H_total²) where H_total is the height from the apex to the big base; slant to the small end s = S × d ÷ D.
2. From a centre point swing an arc of radius S and one of radius s.
3. Sector angle A = 180° × D ÷ S. Lay it out with a protractor, or step the big-end circumference (π × D) along the big arc with dividers set to 1/12 of it.
4. Join the ends of the arcs to the centre; the ring-sector between the arcs is the pattern. Add seam allowance on one radial edge and any flange/hem on the arcs.

**Worked example**: reducer 24" to 12" diameter, 18" tall. Apex height H_total: by similar triangles, H_total = 18 × 24 ÷ (24 − 12) = 36". S = √(12² + 36²) = 37.95"; s = 37.95 × 12/24 = 18.97"; A = 180 × 24 ÷ 37.95 = **113.8°**. Big arc length = π × 24 = 75.4"; check by measuring. A cone too big for one sheet is made in two or three sectors of A/2 or A/3 each with seams.

For a cone with an **off-centre apex** (an oblique cone) or a truncated cone **cut at an angle**, the elements are no longer equal: divide the base into 12, draw each element in the elevation, find its true length (rotate into the plane of the drawing), and lay the pattern out element by element from the apex with dividers: that is radial-line development with true lengths, and it shades into triangulation.

## Triangulation: square-to-round transition

Divide the surface into triangles, find the **true length** of every edge, and lay the triangles out flat one after the other.

1. Draw the **plan** (top view): the square (side s) and the circle (diameter D) concentric (or offset, if the transition is offset); divide the circle into 12 points (3 per quarter), number them; letter the square's corners A, B, C, D.
2. Draw lines from each corner of the square to the four nearest circle points. The surface is now 4 flat triangles (each square side joined to the circle point in front of it) and 4 curved sections made of triangles fanning from each corner to the circle points.
3. Each line in the plan is a **plan length**; the **true length** = √(plan length² + height²). Draw a **true-length diagram**: a vertical line of the transition's height H, and from its base measure each plan length horizontally; the hypotenuse is the true length. Label them.
4. Lay out: start with a square side (true size, it is horizontal), swing arcs from its ends with the true lengths of the lines to the first circle point to locate that point; from that point swing the circle's chord (the distance between adjacent circle points in plan, which is true because it is horizontal) and from the corner swing the true length of the next line; their intersection is the next point. Continue around the whole surface.
5. Join the circle points with a fair curve and the square points with straight lines; add seam allowance. Fold on the corner lines; roll the curved sections gently over a pipe or in the rolls.

Rectangle-to-round and offset transitions work the same with more distinct triangles (no symmetry, so every line is found). This is the method for hopper transitions, dust-collection connections and chute mouths.

## Bend allowance for press-brake and hand-brake work

When sheet bends, the outside stretches and the inside compresses; the **neutral axis** (that keeps its length) sits at K × T from the inside, where K ≈ 0.33 for tight bends (R < T), 0.40-0.45 typical, 0.50 for large-radius bends. The flat pattern length is the sum of the flat legs plus the arc length at the neutral axis.

```
   Bend allowance  BA = (π ÷ 180) × angle × (R + K × T)          angle = bend angle in degrees, R = inside radius, T = thickness
   Outside setback (for 90°)  OSSB = R + T
   Bend deduction  BD = 2 × OSSB − BA                             (subtract from the sum of the outside leg lengths)
   Flat length = leg1 + leg2 − BD   (legs measured to the outside intersection of the faces)
             = (leg1 − OSSB) + (leg2 − OSSB) + BA
```

**Worked example**: 90° bend in 1/4" (0.25") plate, inside radius 1/4", K = 0.42 (mild steel, R = T). BA = 1.5708 × (0.25 + 0.42 × 0.25) = 1.5708 × 0.355 = **0.558"**. OSSB = 0.5". BD = 1.0 − 0.558 = **0.442"**. A bracket with 4" and 6" outside legs cuts from a flat **10.00 − 0.44 = 9.56"** long. For 90° bends in thin sheet (16 ga, R = T), a rule of thumb is BD ≈ 1.6-1.7 × T, but check with a test bend on scrap and measure; every brake and die set is a little different.

**Minimum inside bend radius** (to avoid cracking; bend **across** the grain of the sheet where possible):

| Material | Minimum inside radius |
|---|---|
| Mild steel (A36, 1008-1018, 3003 aluminium) | 1 × T (0.5 T on thin gauges with good tooling) |
| A572 Gr 50, higher-strength | 1.5-2 × T |
| Stainless 304 annealed | 1-1.5 × T |
| Aluminium 5052-H32 | 1-1.5 × T |
| **Aluminium 6061-T6** | **3-4 × T (cracks otherwise; anneal or use 6061-O)** |
| 7075-T6 | Do not bend |
| Plate over 1/2" | Per the mill; hot forming above 1" |

Press-brake V-die opening ≈ **8 × T** (6 T for thin, 10-12 T for thick or high-strength); inside radius from an air bend is about the die opening ÷ 6 to 8 in mild steel. Springback: bend 2-5° past 90° on mild steel, more on stainless and aluminium alloys.

## Seams, hems and allowances

| Item | Allowance |
|---|---|
| Butt-weld seam (steel plate) | None; add nothing |
| **Lap seam** (riveted, spot-welded, bolted) | Add the lap width (3 × rivet diameter minimum) to one edge |
| Grooved seam (light gauge) | 3 × the groove width in total, 1.5 each edge |
| Pittsburgh lock (duct) | Pocket edge: about 1-1/8" for a 1/4" pocket; flange edge: 1/4" |
| Single hem (edge stiffening) | Hem width (1/4-1/2") |
| Double hem | 2 × hem width |
| Wired edge | 2.5 × wire diameter |
| Flange (90°) | Flange width + bend allowance |
| Rolled cylinder from plate | Circumference at the **mean** diameter (ID + T); the ends cut square |

Mark on the pattern: bend lines (dashed), the inside or outside of the bend (an "up"/"down" note), seam side, grain direction, part number and quantity. Number the elements on the sheet as on the drawing before cutting: after cutting, it is just a curve.

## Common mistakes

- Circumference at the inside or outside diameter on thick plate: a rolled cylinder ends up a half-inch short or long.
- Forgetting the seam allowance on one edge only (adding it to both makes it too long).
- Triangulation with plan lengths instead of true lengths: the transition twists and will not close.
- Bending 6061-T6 at a tight radius: cracks along the bend.
- Bend deduction applied per leg instead of per bend.
- Cone sector angle from D and the vertical height instead of the slant height.

## Related

- [Pipe saddle and lateral templates](/article/pipe-saddle-and-lateral-templates)
- [Pipe miter layout](/article/pipe-miter-layout)
- [Layout tools and scribing](/article/layout-tools-and-scribing)
- [Trig and layout formulas](/article/trig-and-layout-formulas)
- [Geometry formulas: areas and volumes](/article/geometry-formulas-area-volume-weight)
- [Wire gauge and sheet thickness](/article/wire-gauge-and-sheet-thickness)
