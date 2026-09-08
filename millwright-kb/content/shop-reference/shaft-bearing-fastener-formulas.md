---
title: "Shaft, Bearing and Fastener Formulas: Torsional Stress, Shaft Sizing, Keys, Bearing L10 Life, Shrink Fits, Bolt Clamp Load and Stretch"
slug: shaft-bearing-fastener-formulas
category: shop-reference
kind: chart
tags: [formulas, shaft stress, torsional shear, shaft diameter, hollow shaft, polar moment, angle of twist, bending stress, key length, key shear, bearing life, L10, C/P, dynamic load rating, dn value, shrink fit, interference fit, heating temperature, thermal expansion, bolt clamp load, tensile stress area, proof load, bolt stretch, thread engagement, K factor]
source: "Machinery's Handbook; Shigley's Mechanical Engineering Design; SKF and Timken bearing catalogues (L10 method, ISO 281); SAE J429 / ISO 898 proof loads."
summary: "The strength-of-materials formulas behind millwright decisions: shear stress in a solid or hollow shaft, sizing a shaft for a torque, angle of twist, bending stress, key sizing, bearing L10 life and what doubling the load does, dn speed limits, how hot to heat a hub for a shrink fit, bolt clamp load from torque, tensile stress area, proof load and bolt stretch, with worked examples that tie back to the torque chart."
---

## Shafts in torsion

![Shaft torsion and key shear](/img/shop-reference/shaft-torsion-and-key-shear.svg)

*Shaft torsion and key shear*

```
Torque from power                 T (in-lb) = 63 025 × HP / rpm
Shear stress, solid shaft         τ = 16 T / (π d³) = 5.09 × T / d³            (psi, T in-lb, d in)
Shear stress, hollow shaft        τ = 16 T D / (π (D⁴ − d⁴))                  D = OD, d = ID
Polar moment of inertia, solid    J = π d⁴ / 32 = 0.0982 d⁴
Polar moment, hollow              J = π (D⁴ − d⁴) / 32
Diameter for an allowable stress  d = ∛( 5.09 × T / τ_allow )
Angle of twist                    θ (rad) = T L / (J G)      G steel = 11.5 × 10⁶ psi ; degrees = rad × 57.3
```

Allowable shear stress for ordinary steel line and machine shafts with keyways: **4 000-6 000 psi** for shafts carrying bending as well as torque (motors, conveyors, fans), up to 8 000 psi for pure-torque line shafts. These low numbers include stress concentration at keyways and fatigue. Twist limit rule of thumb: **no more than 1° per 20 diameters** of length (0.08° per foot for line shafts).

**Example - is this shaft big enough?** 50 hp at 1 750 rpm on a 1-1/2" keyed shaft. T = 63 025 × 50 / 1750 = 1 801 in-lb. τ = 5.09 × 1801 / 1.5³ = 5.09 × 1801 / 3.375 = **2 716 psi**. Comfortable (the same motor's own shaft is 1-7/8" because it must also carry belt pull bending).

**Example - minimum diameter:** same torque, allowable 6 000 psi: d = ∛(5.09 × 1801 / 6000) = ∛1.528 = **1.15"**. Round up to the next stock size that suits the bearings and keyway, usually 1-1/4" or 1-3/8". If a belt drive hangs on the shaft, bending adds to this: use the combined-stress formula or, in the field, go one size larger.

**Example - hollow vs solid:** 4" solid shaft J = 0.0982 × 256 = 25.1 in⁴. 4" OD × 2" ID tube: J = 0.0982 × (256 − 16) = 23.6 in⁴, i.e. **94% of the stiffness and strength with 75% of the weight**. Material near the centre does almost nothing in torsion.

**Example - twist:** 1 801 in-lb on a 1-1/2" shaft 10 ft (120") long. J = 0.0982 × 5.06 = 0.497 in⁴. θ = 1801 × 120 / (0.497 × 11.5 × 10⁶) = 0.0378 rad = **2.2°** over 10 ft (80 diameters), so 0.55° per 20 diameters: fine.

## Shafts in bending

```
Bending moment                    M = force × distance from the support (in-lb)
Bending stress, round shaft       σ = 32 M / (π d³) = 10.19 × M / d³
Moment of inertia, round          I = π d⁴ / 64 = 0.0491 d⁴
Deflection, cantilever, end load  y = F L³ / (3 E I)         E steel = 30 × 10⁶ psi
Deflection, simply supported, centre load   y = F L³ / (48 E I)
Combined torque + bending (max shear theory)   equivalent torque Te = √(M² + T²) ; then use the torsion formula with Te
```

**Example - overhung sheave:** belt pull 600 lb at 4" beyond the bearing on a 1-1/2" shaft. M = 2 400 in-lb; σ = 10.19 × 2400 / 3.375 = 7 250 psi. With the 1 801 in-lb torque from above, Te = √(2400² + 1801²) = 3 000 in-lb; τ = 5.09 × 3000 / 3.375 = 4 520 psi. Still under 6 000 psi, but the belt pull is doing more damage than the torque, which is why overhung loads are limited on gearbox and motor shafts (check the maker's OHL table).

Shaft runout limit at couplings: 0.002" TIR. A bent shaft is a bending load that rotates once per revolution: a fatigue machine.

## Keys and keyways

```
Standard square key size        ≈ shaft diameter / 4      (e.g. 1-1/2" shaft → 3/8" key ; see the ANSI B17.1 table)
Force on the key                F = T / (d / 2) = 2 T / d
Key shear stress                τ = F / (w × L) = 2 T / (d w L)          w = key width, L = key length
Key bearing (crushing) stress   σ = F / (h/2 × L) = 4 T / (d h L)        h = key height
Minimum key length              L = 2 T / (d × w × τ_allow)              τ_allow ≈ 8 000 psi for 1018 key stock
```

**Example:** 1 801 in-lb on a 1-1/2" shaft with a 3/8" square key. F = 2 × 1801 / 1.5 = 2 401 lb. L needed = 2401 / (0.375 × 8000) = 0.80". Any hub 1" or longer is fine; use a key the **full hub length** anyway, sized for the peak (starting or jam) torque, which can be 2-3× running torque.

ANSI square key sizes: shaft 1/2-9/16": 1/8" key; 5/8-7/8": 3/16"; 15/16-1-1/4": 1/4"; 1-5/16-1-3/8": 5/16"; 1-7/16-1-3/4": 3/8"; 1-13/16-2-1/4": 1/2"; 2-5/16-2-3/4": 5/8"; 2-13/16-3-1/4": 3/4"; 3-5/16-3-3/4": 7/8"; 3-13/16-4-1/2": 1". Keyway depth is half the key height in each member.

## Bearing life (L10)

The **basic dynamic load rating C** is on the bearing data sheet (the load at which 90% of a batch survives one million revolutions). **P** is the equivalent dynamic load on the bearing.

```
L10 (millions of revolutions)  = (C / P)^p         p = 3 for ball bearings, 10/3 for roller bearings
L10h (hours)                   = 1 000 000 / (60 × rpm) × (C / P)^p
                               = 16 667 / rpm × (C / P)^p
Equivalent load (radial + axial)   P = X × Fr + Y × Fa      (X, Y from the catalogue; if Fa is small, P ≈ Fr)
Load from a belt drive         belt pull ≈ 1.5-2.5 × the torque force (T / sheave radius), depending on tension
Load from a chain drive        ≈ 1.1 × T / (sprocket PD / 2)
Load from a gear               tangential T/(PD/2), plus separating force = tangential × tan(pressure angle)
```

**Example:** 6310 deep-groove ball bearing, C = 65 kN (14 600 lb). Radial load 6 kN (1 350 lb), 1 750 rpm. C/P = 10.8. L10 = 10.8³ = 1 270 million rev. L10h = 16 667 / 1750 × 1270 = **12 100 h** (about 1.4 years continuous, 5 years on one shift). Double the load to 12 kN: C/P = 5.4, L10 = 158, L10h = **1 500 h**. **Doubling the load cuts ball-bearing life by 8×**, and over-tensioned belts are the usual way to do it. Halving the load gives 8× the life.

Roller bearings: (C/P)^3.33, so they are slightly more sensitive to load than ball bearings.

Other life factors: lubricant film (viscosity too low at operating temperature can halve life), contamination (dirt can cut life by 5-10×), temperature (ratings fall above 120°C), misalignment (a 0.002 in/in tilt on a deep-groove ball bearing is already at its limit; spherical rollers take 1.5-2.5°).

### Speed limits: the dn value

```
dn = bore diameter (mm) × rpm
```

Rough limits: grease-lubricated ball bearings up to about **300 000-500 000** dn; oil bath up to 500 000-600 000; spherical roller bearings about 200 000-300 000 grease. Above these, use oil mist/circulation or a different bearing. A 100 mm bore bearing at 1 750 rpm = 175 000 dn, fine on grease; at 3 550 rpm = 355 000, check the catalogue limiting speed.

### Grease quantity and interval

```
Grease charge (grams)  G = 0.005 × D × B          D = outside diameter (mm), B = width (mm)   (SKF rule for regreasing)
Initial fill           30-50% of the free space in the bearing; housing 1/3 to 1/2 full
```

Relubrication intervals fall with speed, temperature and load; catalogues give charts. Halve the interval for every 15°C above 70°C bearing temperature.

## Fits and shrink fits

```
Thermal growth                      ΔL = L × C × ΔT       (steel C = 0.0000063 in/in/°F ; 0.0000113 mm/mm/°C)
Temperature rise to expand a bore   ΔT = (interference + assembly clearance) / (C × d)
Bore growth per 100°F               ≈ 0.00063 × d (in)
Cooling a shaft in dry ice (−110°F) shrinks a 4" shaft about 0.0045"; liquid nitrogen (−320°F) about 0.010"
```

**Example - heating a coupling hub:** 4.000" bore, shaft 4.004" (0.004" interference), you want 0.004" clearance to slide it on. ΔT = (0.004 + 0.004) / (0.0000063 × 4.0) = **317°F** rise, so heat the hub to about 390°F from a 70°F shop. Stay under 650°F for plain steel hubs (tempering) and far lower for anything with a rubber element or a hardened part. Bearings: max 250°F (120°C).

**Example - press fit force (estimate):** F ≈ μ × p × π × d × L, with contact pressure p ≈ (interference / d) × E / 2 for similar-size steel parts, μ ≈ 0.15 dry. 0.002" interference on a 2" shaft, 3" hub length: p ≈ (0.002/2) × 30×10⁶ / 2 = 15 000 psi; F ≈ 0.15 × 15 000 × π × 2 × 3 = **42 000 lb (21 tons)**. If your shop press is 20 tons, heat the hub instead.

Common fit classes (ISO): shaft **k5/k6/m6/n6** for interference on rotating inner rings (heavier letter = tighter); housing **H7** clearance for stationary outer rings, **J7/K7/M7/N7/P7** progressively tighter for rotating outer rings or heavy loads. Interference on a bearing ring uses up internal clearance: about 80% of the shaft interference reduces the radial clearance, which is why interference-fit bearings are ordered C3.

## Bolts and threads

```
Clamp load from torque             F = T / (K × d)              T in-lb, d nominal diameter in, K ≈ 0.20 dry, 0.15 oiled, 0.12 anti-seize
Torque for a clamp load            T = K × d × F
Tensile stress area (UN threads)   At = 0.7854 × (d − 0.9743 / n)²         n = threads per inch
Tensile stress area (metric)       At = 0.7854 × (d − 0.9382 × p)²         p = pitch (mm)
Proof load                         = At × proof strength   (Grade 5: 85 000 psi ; Grade 8: 120 000 psi ; 8.8: 600 MPa ; 10.9: 830 MPa)
Design preload                     = 75% of proof load (reusable), 90% (permanent)
Bolt stretch under load            δ = F × L / (At × E)          E = 30 × 10⁶ psi ; L = grip length
Stress in the bolt                 σ = F / At
Thread stripping length (rule)     engagement ≥ 1 × d in steel, 1.5 × d in cast iron, 2 × d in aluminium; a nut is 0.875 d
Number of bolts for a load         n = load × safety factor / (allowable per bolt)
```

**Example - where the torque chart comes from:** 1/2-13 Grade 5, dry. At = 0.7854 × (0.5 − 0.9743/13)² = 0.7854 × 0.4251² = **0.1419 in²**. Proof load = 0.1419 × 85 000 = 12 060 lb. Preload at 75% = 9 045 lb. T = 0.20 × 0.5 × 9045 = 904 in-lb = **75 ft-lb**, which is the chart value. Oiled (K = 0.15): 68 ft-lb → 56 ft-lb for the same clamp. Torque the oiled bolt to 75 ft-lb and the preload is 12 060 lb: exactly at proof, and it may yield.

**Example - bolt stretch (turn-of-nut and ultrasonic checks):** that 1/2" bolt with a 2" grip at 9 045 lb: δ = 9045 × 2 / (0.1419 × 30 × 10⁶) = **0.0042"**. On a 13-tpi thread one turn = 0.0769", so the stretch is 0.0042/0.0769 = 0.055 turn ≈ **20° of nut rotation past snug**. Turn-of-nut specs for structural bolts (1/3 to 2/3 turn) are larger because they aim for yield and have long grips.

**Example - flange bolting:** 8 bolts hold a 10" flange at 150 psi. Hydrostatic end force ≈ 0.7854 × 10² × 150 = 11 800 lb, plus gasket seating; with a safety factor of 2, each bolt needs ≈ 2 950 lb of clamp. Any 1/2" Grade 5 bolt at 9 000 lb preload is fine; the gasket, not the bolt, sets the real torque.

Thread pitch (inch) = 1 / TPI (1/2-13 → 0.0769"). Lead = pitch × number of starts.

## Cylinder walls and pressure (thin-wall)

```
Hoop stress in a pipe or tank     σ = P × D / (2 t)             P psi, D inside diameter, t wall
Longitudinal stress               σ = P × D / (4 t)
Burst pressure (approx.)          P = 2 × t × UTS / D
Force on a blank flange / end cap F = P × 0.7854 × D²
```

**Example:** 6" sch 40 pipe (6.065" ID, 0.280" wall) at 150 psi: hoop stress = 150 × 6.065 / (2 × 0.280) = **1 625 psi**. A 6" blind flange at 150 psi carries 150 × 0.7854 × 36 = 4 240 lb of end force, which is what the bolts see.

## Related

- [Bolt torque chart](/article/bolt-torque-chart-sae-metric)
- [Mounting bearings with heat](/article/bearing-mounting-with-heat)
- [Decoding bearing numbers](/article/bearing-designation-codes)
- [Thermal growth and alignment](/article/thermal-growth-alignment)
- [Power, torque, speed and drive formulas](/article/power-torque-speed-drive-formulas)
