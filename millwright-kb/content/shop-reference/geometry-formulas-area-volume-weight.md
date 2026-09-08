---
title: "Geometry Formulas for Millwrights: Area of Shafts and Bores, Volumes, Tank Capacity and Steel Weights"
slug: geometry-formulas-area-volume-weight
category: shop-reference
kind: chart
tags: [formulas, area of a circle, area of shaft, area of bore, cylinder volume, tank volume, gallons, annulus, hollow shaft, cone, sphere, weight of steel, round bar weight, pipe weight, plate weight, circumference, arc, chord, sector, hexagon]
source: "Machinery's Handbook; standard geometry. Densities: steel 0.2833 lb/in³ (490 lb/ft³), water 62.4 lb/ft³ (8.34 lb/gal)."
summary: "Every area and volume formula a millwright reaches for: circle and shaft cross-section, annulus for hollow shafts and cylinder rod side, cylinder and bore volume in cubic inches and gallons, cones, spheres, tanks (including a part-full horizontal tank), and quick weights of round bar, plate and pipe, each with a worked example."
---

## Constants you will use constantly

| Constant | Value |
|---|---|
| π | 3.1416 |
| π/4 (circle area factor) | **0.7854** |
| Cubic inches per US gallon | **231** |
| Gallons per cubic foot | **7.48** |
| Cubic inches per cubic foot | 1 728 |
| Weight of water | 62.4 lb/ft³ · **8.34 lb/gal** · 0.0361 lb/in³ |
| Density of steel | **0.2833 lb/in³** · 490 lb/ft³ |
| Density of cast iron | 0.26 lb/in³ · 450 lb/ft³ |
| Density of aluminium | 0.098 lb/in³ · 169 lb/ft³ |
| Density of concrete | 150 lb/ft³ |
| 1 inch | 25.4 mm |

## Circles, shafts and bores

![Shaft, bore and annulus areas](/img/shop-reference/shaft-bore-annulus-areas.svg)

*Shaft, bore and annulus areas*

```
Area of a circle (solid shaft cross-section)      A = π r² = π d² / 4 = 0.7854 × d²
Circumference                                     C = π d = 2 π r
Diameter from circumference                       d = C / π
Diameter from area                                d = √(A / 0.7854) = 1.128 √A
```

| d (in) | Area (in²) | | d (in) | Area (in²) |
|---|---|---|---|---|
| 1/2 | 0.196 | | 2 | 3.142 |
| 3/4 | 0.442 | | 2-1/2 | 4.909 |
| 1 | 0.785 | | 3 | 7.069 |
| 1-1/4 | 1.227 | | 4 | 12.566 |
| 1-1/2 | 1.767 | | 5 | 19.635 |
| 1-3/4 | 2.405 | | 6 | 28.274 |

**Example:** area of a 2-3/8" shaft. 0.7854 × 2.375² = 0.7854 × 5.641 = **4.43 in²**.

### Hollow shaft, pipe wall, or cylinder rod-side (annulus)

```
A = 0.7854 × (D² − d²)        D = outside diameter, d = inside (or rod) diameter
```

**Example:** hydraulic cylinder, 4" bore, 2" rod. Full-bore (extend) area = 0.7854 × 16 = **12.57 in²**. Rod-side (retract) area = 0.7854 × (16 − 4) = **9.42 in²**. The cylinder pushes harder than it pulls by the ratio 12.57 / 9.42 = 1.33.

### Arcs, chords, sectors, segments

```
Arc length                    s = (θ / 360) × π d              θ in degrees
Chord                         c = d × sin(θ / 2)               (= 2 r sin(θ/2))
Sector area (pie slice)       A = (θ / 360) × 0.7854 d²
Sagitta (height of arc)       h = r − √(r² − (c/2)²)
Radius from chord and sagitta r = c² / (8 h) + h / 2
Segment area (arc + chord)    A = r² × (θ_rad − sin θ) / 2      θ_rad in radians = θ × 0.01745
```

**Example:** a broken wheel rim shows a chord of 24" and the arc rises 2" above it. r = 24² / (8 × 2) + 2 / 2 = 36 + 1 = **37"**, so the wheel was 74" in diameter.

## Straight-sided shapes

```
Rectangle / square       A = L × W
Triangle                 A = ½ × base × height
Triangle from 3 sides    s = (a + b + c)/2 ;  A = √( s (s−a)(s−b)(s−c) )      (Heron)
Trapezoid                A = (a + b) / 2 × h          a, b = parallel sides
Parallelogram            A = base × height
Ellipse                  A = 0.7854 × D × d           D, d = long and short diameters
Regular hexagon          A = 2.598 × s²   (s = side)  = 0.866 × AF²   (AF = across flats)
Regular polygon          A = ½ × perimeter × apothem (centre to mid-side)
```

Hexagon across corners = across flats × **1.1547**. Square across corners = across flats × **1.4142**.

## Surface area

```
Cylinder, side only        A = π d h
Cylinder, closed both ends A = π d h + 2 × 0.7854 d²
Sphere                     A = π d²  = 4 π r²
Cone, side only            A = π r × slant height ;  slant = √(r² + h²)
Rectangular box            A = 2 (LW + LH + WH)
```

Use these for paint, insulation and heat-transfer estimates.

## Volumes

```
Cylinder / cylinder bore / tank on end   V = 0.7854 × d² × h
Hollow cylinder (pipe wall, sleeve)      V = 0.7854 × (D² − d²) × L
Rectangular tank / block                 V = L × W × H
Cone                                     V = ⅓ × 0.7854 × d² × h
Frustum of a cone (hopper)               V = (π h / 3) × (R² + R r + r²)
Sphere                                   V = 0.5236 × d³   (= 4/3 π r³)
Hemisphere (dished head, rough)          V = 0.2618 × d³
Pyramid                                  V = ⅓ × base area × h
```

Convert to liquid: **gallons = in³ ÷ 231** or **gallons = ft³ × 7.48**. Litres = cm³ ÷ 1 000.

**Example - vertical tank:** 36" diameter, 60" tall. V = 0.7854 × 36² × 60 = 0.7854 × 1296 × 60 = 61 073 in³. Gallons = 61 073 / 231 = **264 gal**. Weight of water = 264 × 8.34 = **2 204 lb**.

**Example - cylinder bore displacement:** 4" bore, 24" stroke. V = 0.7854 × 16 × 24 = 301.6 in³ = **1.31 gal** per full extend stroke. At 10 gpm the extend takes 1.31 / 10 = 0.131 min = **7.8 s**.

**Example - hopper (frustum):** 48" top diameter, 12" bottom, 36" tall. R = 24, r = 6. V = (π × 36 / 3) × (576 + 144 + 36) = 37.70 × 756 = 28 500 in³ = 16.5 ft³.

### Horizontal cylindrical tank, part full

The one everybody looks up. r = radius, h = liquid depth measured from the bottom, L = tank length, all in the same unit.

```
Segment area  A = r² × acos( (r − h) / r ) − (r − h) × √(2 r h − h²)      acos in radians
Volume        V = A × L
```

**Example:** 48" diameter × 120" long tank, dipstick shows 12" of oil. r = 24, h = 12.
acos((24 − 12)/24) = acos(0.5) = 1.0472 rad. r² × 1.0472 = 576 × 1.0472 = 603.2. (r − h) × √(2rh − h²) = 12 × √(576 − 144) = 12 × 20.78 = 249.4. A = 603.2 − 249.4 = 353.8 in². V = 353.8 × 120 = 42 456 in³ = **184 gal**. (A full tank holds 0.7854 × 48² × 120 / 231 = 940 gal; 12" of 48" is a quarter of the depth but only 19.6% of the volume.)

Quick fractions for a horizontal tank: depth 25% of diameter ≈ **19.6%** of volume, 50% ≈ 50%, 75% ≈ 80.4%.

## Weight

```
Weight = volume × density
Round steel bar         lb per ft = 2.67 × d²        (d in inches)      lb per in = 0.2225 × d²
Square steel bar        lb per ft = 3.40 × s²
Steel plate             lb per ft² = 40.8 × thickness (in)
Steel pipe / tube       lb per ft = 10.69 × (OD − wall) × wall        (inches)
Hex steel bar           lb per ft = 2.945 × AF²
Water inside a pipe     lb per ft = 0.34 × ID²      gal per ft = 0.0408 × ID²
```

For aluminium multiply the steel figures by 0.35; for cast iron by 0.92; for brass by 1.09; for stainless by 1.02.

**Example - shaft weight for rigging:** 3" steel shaft, 10 ft long. 2.67 × 9 = 24 lb/ft → **240 lb**. Long way: 0.7854 × 9 × 120 = 848 in³ × 0.2833 = 240 lb.

**Example - plate:** 4 ft × 8 ft × 3/4" plate. 40.8 × 0.75 = 30.6 lb/ft² × 32 ft² = **979 lb**.

**Example - pipe:** 6" sch 40 (6.625" OD, 0.280" wall), 20 ft. 10.69 × (6.625 − 0.280) × 0.280 = 19.0 lb/ft → 380 lb empty; water in it adds 0.34 × 6.065² = 12.5 lb/ft → **630 lb full**.

**Example - hollow shaft vs solid:** 4" OD × 2" ID tube vs 4" solid, per foot. Solid 2.67 × 16 = 42.7 lb. Tube 2.67 × (16 − 4) = 32.0 lb. The tube is 25% lighter but keeps about 94% of the torsional strength (see the [shaft formulas](/article/shaft-bearing-fastener-formulas)).

## Metric versions

Same formulas; keep every length in **mm** and you get mm² and mm³. 1 000 mm³ = 1 cm³ = 1 mL. Steel = 7.85 g/cm³, so a round bar weighs **0.00617 × d² kg per metre** (d in mm). Water = 1 kg per litre.

## Related

- [Shop reference: decimal equivalents, tap drills, conversions](/article/shop-reference-tables)
- [Pump and fluid-power formulas](/article/pump-and-fluid-power-formulas)
- [Trig and layout formulas](/article/trig-and-layout-formulas)
- [Rigging basics](/article/rigging-basics-sling-angles-and-hitches) (uses these weights)
