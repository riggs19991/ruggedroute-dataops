---
title: "Trig and Layout Formulas: Right Triangles, Offsets, Bolt Circles, Tapers, Sine Bars, Slopes and Leveling"
slug: trig-and-layout-formulas
category: shop-reference
kind: chart
tags: [formulas, trigonometry, right triangle, sine, cosine, tangent, pythagorean, law of sines, law of cosines, offset, travel, run, bolt circle, hole coordinates, chord, taper per foot, taper angle, sine bar, slope, grade, rise over run, level, shim by slope, hexagon, square, 3-4-5, centre of a circle, degrees to radians]
source: "Machinery's Handbook; standard trigonometry."
summary: "The trig a millwright uses in the field: solving right triangles, laws of sines and cosines for any triangle, offsets and rolling offsets, bolt-circle chord and coordinate formulas with a table, taper per foot and taper angle, sine-bar heights, converting slope to degrees and percent, shimming from a level reading, squaring with 3-4-5 and diagonals, and finding the centre of a circle, all with worked examples."
---

## Right triangles

![Right triangle functions and offset factors](/img/shop-reference/right-triangle-and-offset.svg)

*Right triangle functions and offset factors*

```
Pythagoras      c² = a² + b²        c = hypotenuse
sin θ = opposite / hypotenuse       cos θ = adjacent / hypotenuse       tan θ = opposite / adjacent
opposite = hyp × sin θ              adjacent = hyp × cos θ              opposite = adjacent × tan θ
hypotenuse = opposite / sin θ       hypotenuse = adjacent / cos θ       θ = atan(opposite / adjacent)
The two acute angles add to 90°.
```

| θ | sin | cos | tan | | θ | sin | cos | tan |
|---|---|---|---|---|---|---|---|---|
| 5° | 0.0872 | 0.9962 | 0.0875 | | 45° | 0.7071 | 0.7071 | 1.0000 |
| 10° | 0.1736 | 0.9848 | 0.1763 | | 50° | 0.7660 | 0.6428 | 1.1918 |
| 15° | 0.2588 | 0.9659 | 0.2679 | | 60° | 0.8660 | 0.5000 | 1.7321 |
| 20° | 0.3420 | 0.9397 | 0.3640 | | 67.5° | 0.9239 | 0.3827 | 2.4142 |
| 22.5° | 0.3827 | 0.9239 | 0.4142 | | 70° | 0.9397 | 0.3420 | 2.7475 |
| 30° | 0.5000 | 0.8660 | 0.5774 | | 75° | 0.9659 | 0.2588 | 3.7321 |
| 36° | 0.5878 | 0.8090 | 0.7265 | | 80° | 0.9848 | 0.1736 | 5.6713 |
| 40° | 0.6428 | 0.7660 | 0.8391 | | 90° | 1.0000 | 0 | ∞ |

**Example:** a conveyor rises 12 ft over a horizontal run of 40 ft. Length of the incline = √(12² + 40²) = √1744 = **41.8 ft**. Angle = atan(12/40) = atan(0.30) = **16.7°**. Belt loads on an incline: the belt tension needed to lift the material is W × sin θ; the component pressing on the idlers is W × cos θ.

**Example - guy wire:** anchor 15 ft from the base of a 20 ft mast: wire length = √(15² + 20²) = 25 ft (a 3-4-5 triangle scaled by 5), angle at the ground = atan(20/15) = 53.1°.

## Any triangle

```
Angles sum to 180°
Law of sines      a / sin A = b / sin B = c / sin C
Law of cosines    c² = a² + b² − 2 a b cos C          (finds the third side from two sides and the included angle)
                  cos C = (a² + b² − c²) / (2 a b)     (finds an angle from three sides)
Area              ½ a b sin C
```

**Example - two-leg sling check:** legs 8 ft and 8 ft, pick points 10 ft apart. Angle at the hook: cos C = (64 + 64 − 100)/(2 × 64) = 0.2188 → C = 77.4°. Each leg to the horizontal = (180 − 77.4)/2 = **51.3°**, above the 45° minimum-comfortable, load factor = 1/sin 51.3° = 1.28.

**Example - pipe changes direction 30°:** two pipes of 5 ft and 7 ft meet at 150° (the inside angle). Straight-line distance between the far ends: c² = 25 + 49 − 2 × 35 × cos 150° = 74 + 60.6 = 134.6 → **11.6 ft**.

## Offsets (pipe, conduit, shafting, duct)

Two equal bends of angle θ shift a run sideways by the **offset**.

```
Travel (length of the diagonal piece)     = offset / sin θ = offset × multiplier
Run (horizontal distance used up)         = offset / tan θ
Shrink (how much shorter the overall run gets) = travel − run
Rolling offset (up AND sideways)          true offset = √(rise² + side²), then use the formulas above
```

| Bend angle | Multiplier (travel/offset) | Run per inch of offset | Shrink per inch of offset |
|---|---|---|---|
| 10° | 5.76 | 5.67 | 0.09 |
| 22.5° | 2.613 | 2.414 | 0.199 |
| 30° | 2.000 | 1.732 | 0.268 |
| 45° | 1.414 | 1.000 | 0.414 |
| 60° | 1.155 | 0.577 | 0.577 |

**Example:** a lube line must jog 9" sideways with 45° fittings. Travel = 9 × 1.414 = **12.7"** centre to centre; run = 9"; the overall length shortens by 9 × 0.414 = 3.7" (add that back into the straight pieces). Rolling offset of 9" up and 6" over: true offset = √(81 + 36) = 10.8"; travel at 45° = 15.3".

## Bolt circles and hole patterns

```
Chord between adjacent holes    c = BCD × sin(180° / N)          BCD = bolt-circle diameter, N = holes
Angle between holes             = 360° / N
Coordinates of hole k (k = 0,1,2…), measured from the centre, first hole at angle φ:
    x = R × cos(φ + k × 360°/N)          y = R × sin(φ + k × 360°/N)          R = BCD / 2
Bolt circle from a measured chord       BCD = c / sin(180° / N)
Bolt circle from two opposite holes     BCD = centre-to-centre distance (even N only)
```

| Holes N | Chord factor (× BCD) | Holes N | Chord factor |
|---|---|---|---|
| 3 | 0.8660 | 8 | 0.3827 |
| 4 | 0.7071 | 10 | 0.3090 |
| 5 | 0.5878 | 12 | 0.2588 |
| 6 | 0.5000 | 16 | 0.1951 |
| 7 | 0.4339 | 20 | 0.1564 |

**Example:** 6 holes on a 10" BCD. Chord = 10 × 0.5 = **5.000"** exactly (a hexagon's side equals its circumscribed radius: set dividers to the radius and walk around). Coordinates with hole 0 at 0°: hole 1 at 60° → x = 5 cos 60° = 2.500, y = 5 sin 60° = **4.330**; hole 2 at 120° → (−2.500, 4.330); and so on.

**Example - identify a flange:** 8 holes, adjacent holes measure 3.64" centre to centre. BCD = 3.64 / 0.3827 = **9.5"** → an ANSI 6" class 150 flange (8 × 3/4" bolts on a 9.5" circle). Always confirm against the flange tables; 8-hole patterns exist in several sizes.

## Tapers

```
Taper per foot (TPF)      = (D − d) × 12 / L         D, d = large and small diameter, L = length (in)
Taper per inch            = (D − d) / L
Included angle            tan(θ/2) = (D − d) / (2 L)          θ = 2 × atan((D − d)/(2L))
Angle from TPF            tan(θ/2) = TPF / 24
Taper ratio 1:n           D − d = L / n   (e.g. 1:12 → 1" of diameter change per 12" of length)
```

| Taper | TPF | Included angle | Where you meet it |
|---|---|---|---|
| 1:12 | 1.000"/ft | 4.77° | SKF/FAG "K" bearing bores, adapter sleeves |
| 1:30 | 0.400"/ft | 1.91° | "K30" large spherical roller bearings |
| Morse taper | ≈ 0.600-0.630"/ft | ≈ 2.9° | Drill and lathe spindles |
| Jarno | 0.600"/ft | 2.86° | Older machine spindles |
| Brown & Sharpe | 0.500"/ft | 2.39° | Milling spindles (old) |
| Pipe thread NPT | 0.750"/ft (1:16 on diameter) | 3.58° | Every pipe thread; hand-tight plus 1.5-3 turns |
| QD / Taper-Lock bushings | see bushing sheet | | Sheaves and sprockets |

**Example:** an adapter sleeve is 1:12. Driving the bearing 0.79 mm along the sleeve (100-120 mm bore, SKF card) expands the inner ring by 0.79 / 12 = 0.066 mm on diameter; about three-quarters of that shows up as clearance reduction (the card says 0.050-0.060 mm for that drive-up), the rest is absorbed by the ring stretching.

**Example - measure an unknown taper:** diameters 2.250" and 2.000" over a 4" length: TPF = 0.25 × 12 / 4 = **0.750"/ft**; half-angle = atan(0.25 / 8) = 1.79°, included 3.58°: it is a pipe-thread taper.

## Sine bar and sine plate

```
Gauge-block height   h = L × sin θ         L = sine bar length (5" or 10" between roll centres)
Angle from a height  θ = asin(h / L)
```

**Example:** set 12°30' on a 5" sine bar: h = 5 × sin 12.5° = 5 × 0.2164 = **1.082"** of gauge blocks. Keep sine bars under 45°; above that the error blows up, so measure the complement instead.

## Slopes, grades and leveling

```
Slope as a ratio     rise / run
Percent grade        = rise / run × 100
Degrees              = atan(rise / run)
Inches per foot      = rise / run × 12
Shim to level        shim = span between the feet × (rise / run read on the level)
Precision level      each division = its sensitivity (e.g. 0.0005" per ft = 0.0005" per 12" per division)
```

| Slope | Degrees | Percent | in/ft |
|---|---|---|---|
| 1:100 | 0.57° | 1% | 0.12 |
| 1:20 | 2.86° | 5% | 0.60 |
| 1:12 | 4.76° | 8.3% | 1.00 |
| 1:8 | 7.13° | 12.5% | 1.50 |
| 1:4 | 14.0° | 25% | 3.00 |
| 1:2 | 26.6° | 50% | 6.00 |
| 1:1 | 45° | 100% | 12.00 |

**Example - leveling a base:** a machinist level reads 3 divisions of 0.0005"/ft high toward the outboard end. The feet are 30" apart. Shim under the low end = 30/12 × 0.0015 = **0.0037"**, so add a 0.004" shim (or 0.003" + 0.001"). Recheck at 90° for cross-level.

**Example - drainage:** a gravity drain must fall 1/4" per foot over 32 ft: total drop = 8". As a percent: 0.25/12 = 2.1%.

## Squaring and layout

```
3-4-5 (or 6-8-10, 9-12-15, 30-40-50)     square corner when the diagonal is exactly 5 units
Equal diagonals                          a rectangle is square when both diagonals measure the same
Diagonal of a rectangle                  = √(L² + W²)
Diagonal (across corners) of a square    = side × 1.4142
Hexagon across corners                   = across flats × 1.1547 ;  side = AF × 0.5774
Octagon across corners                   = across flats × 1.0824
Centre of a circle                       draw any two chords, erect their perpendicular bisectors; they cross at the centre.
                                         Or: centre finder / combination-square centre head on a shaft end.
Divide a circle into N parts             chord = D × sin(180°/N)  (table above), step it with dividers
Degrees ↔ radians                        rad = deg × 0.01745 ;  deg = rad × 57.30 ;  arc = r × rad
Degrees, minutes, seconds                12°30'15" = 12 + 30/60 + 15/3600 = 12.504°
```

**Example - baseplate anchor bolts:** a 60" × 40" bolt pattern. Diagonal must measure √(3600 + 1600) = √5200 = **72.11"** both ways. If one diagonal is 72.3" and the other 71.9", the pattern is a parallelogram, off by about 0.2" at the corners; pull it square before the grout goes in.

**Example - shaft centre on a big pulley face:** 3-point method: scribe three arcs from three spots on the rim with dividers set the same; the centre is where the arcs meet. Or measure any chord, drop a perpendicular from its midpoint, repeat with a second chord.

## Related

- [Geometry formulas: areas, volumes, weights](/article/geometry-formulas-area-volume-weight)
- [Shop reference tables](/article/shop-reference-tables)
- [Rigging basics: sling angles](/article/rigging-basics-sling-angles-and-hitches)
- [Tapered-bore bearing on an adapter sleeve](/article/taper-bore-bearing-adapter-sleeve-skf)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
