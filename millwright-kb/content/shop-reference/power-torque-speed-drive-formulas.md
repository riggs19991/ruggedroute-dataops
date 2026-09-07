---
title: "Power, Torque, Speed and Drive Formulas: Horsepower, Motors, Ratios, Belts, Chains, Gears, Conveyors and Mechanical Advantage"
slug: power-torque-speed-drive-formulas
category: shop-reference
kind: chart
tags: [formulas, horsepower, torque, 5252, 63025, motor amps, 746, synchronous speed, slip, gear ratio, compound gear train, diametral pitch, pitch diameter, sprocket pitch diameter, belt speed, conveyor speed, conveyor capacity, WK2, accelerating torque, mechanical advantage, lever, block and tackle, screw jack, inclined plane, work, energy, efficiency, service factor]
source: "Standard mechanical engineering references; NEMA MG-1 motor data; Machinery's Handbook."
summary: "How power, torque and speed relate, how to get horsepower from motor nameplate data or amps, synchronous speed and slip, gear and sprocket geometry, belt and conveyor speed and capacity, torque to accelerate a load, and the simple machines (lever, pulley system, screw, hydraulic press), each with a worked example."
---

## Power, torque, speed

```
HP  = T (ft-lb) × rpm / 5 252
HP  = T (in-lb) × rpm / 63 025
T (ft-lb) = 5 252 × HP / rpm
T (in-lb) = 63 025 × HP / rpm
kW  = T (N·m) × rpm / 9 549   ;   T (N·m) = 9 549 × kW / rpm
1 hp = 746 W = 0.746 kW = 33 000 ft-lb/min = 550 ft-lb/s
1 ft-lb = 12 in-lb = 1.356 N·m
```

Where 5 252 comes from: 33 000 ÷ 2π. Torque and speed trade off at constant power: a gearbox that cuts speed by 10 multiplies torque by 10 (less losses).

**Example:** 30 hp motor at 1 750 rpm. T = 5252 × 30 / 1750 = **90 ft-lb** (1 080 in-lb). Through a 20:1 reducer at 95% efficiency the output shaft turns 87.5 rpm and delivers 90 × 20 × 0.95 = **1 710 ft-lb**. The output shaft, keys and coupling are sized for that torque, not for 30 hp in the abstract.

## Work, energy, efficiency

```
Work (ft-lb)      = force (lb) × distance (ft)
Power             = work / time
HP to lift        = weight (lb) × lift speed (ft/min) / 33 000
Efficiency        = output power / input power   (multiply efficiencies of stages in series)
Kinetic energy    = ½ m v²   ;   rotating: ½ I ω²
Potential energy  = weight × height
```

**Example - hoist:** lift 4 000 lb at 20 ft/min through a hoist with 75% overall efficiency. HP = 4000 × 20 / 33 000 / 0.75 = **3.2 hp** → 5 hp motor.

**Example - efficiency chain:** motor 92% × V-belt 95% × gearbox 96% × chain 93% = 0.78. A 10 hp motor delivers about 7.8 hp to the conveyor shaft.

## Electric motors

```
Synchronous speed (rpm)   Ns = 120 × frequency / number of poles
Slip (%)                  = (Ns − actual rpm) / Ns × 100
Three-phase HP output     = 1.732 × V × I × PF × efficiency / 746
Three-phase kW input      = 1.732 × V × I × PF / 1 000
Single-phase HP output    = V × I × PF × efficiency / 746
Full-load current (rough) ≈ 1.25 A per hp at 460 V ;  2.5 A/hp at 230 V ;  1 A/hp at 575 V   (three-phase)
Full-load torque          T = 5 252 × HP / full-load rpm
Starting (locked-rotor) current ≈ 6-8 × full-load amps ;  starting torque 150-275% of full-load (design B)
Service factor            the motor may run continuously at HP × SF (usually 1.15) at reduced life; do not size to it
Motor speed on a VFD      rpm = 120 × f / poles × (1 − slip) ;  constant torque below base speed, constant hp above it
```

| Poles (60 Hz) | Synchronous rpm | Typical full-load rpm |
|---|---|---|
| 2 | 3 600 | 3 450-3 550 |
| 4 | 1 800 | 1 725-1 780 |
| 6 | 1 200 | 1 150-1 175 |
| 8 | 900 | 850-875 |

50 Hz: multiply synchronous speeds by 5/6 (3 000, 1 500, 1 000, 750).

**Example - amps to horsepower:** 460 V motor drawing 30 A, PF 0.85, efficiency 92%. HP = 1.732 × 460 × 30 × 0.85 × 0.92 / 746 = **25 hp** of shaft output. If the nameplate says 30 hp, the machine is at about 83% load. Clamp-on ammeter readings are the quickest load check there is; compare against nameplate FLA.

**Example - slip:** nameplate 1 765 rpm, measured 1 790 rpm with a strobe: slip = (1800 − 1790)/1800 = 0.55% versus 1.9% at full load, so the motor is lightly loaded.

## Speed ratios

```
Belts and pulleys      driver rpm × driver PD = driven rpm × driven PD
Chains and gears       driver rpm × driver teeth = driven rpm × driven teeth
Ratio                  = driven teeth / driver teeth = driver rpm / driven rpm  (> 1 is a reduction)
Compound train         total ratio = product of all driven teeth ÷ product of all driver teeth
                       output rpm = input rpm × (product of drivers) / (product of drivens)
Idler gears            change direction only, not ratio
Torque out             = torque in × ratio × efficiency
```

**Example - compound:** motor 1 750 rpm → 20 T pinion drives 60 T gear on a jackshaft; on the same shaft a 15 T sprocket drives a 45 T sprocket. Ratio = (60 × 45) / (20 × 15) = 2700 / 300 = **9:1**. Output = 1750 / 9 = **194 rpm**. Torque at the output = 9 × input torque × (0.97 × 0.93).

**Example - pick a sheave:** fan must run 1 150 rpm from a 1 750 rpm motor with a 6" motor sheave. Fan sheave PD = 1750 × 6 / 1150 = **9.13"**; nearest stock 9.0" gives 1 167 rpm (fan laws say the hp changes by (1167/1150)³ = +4.5%).

## Gear geometry (inch, diametral pitch)

```
Diametral pitch     DP = teeth / pitch diameter        (teeth per inch of PD; 8 DP is coarser than 16 DP)
Pitch diameter      PD = N / DP
Outside diameter    OD = (N + 2) / DP
Circular pitch      CP = π / DP
Whole tooth depth   ≈ 2.25 / DP  (2.157 / DP for older 14.5° teeth)
Centre distance     C = (N1 + N2) / (2 × DP)
Metric module       m = PD (mm) / N ;  OD = m (N + 2) ;  C = m (N1 + N2) / 2 ;  module ≈ 25.4 / DP
Backlash            measured at the pitch line; typical 0.03-0.05 / DP inch
```

Two gears only mesh if they have the **same DP (or module) and the same pressure angle** (14.5° or 20°). Count teeth and measure OD to find DP: DP = (N + 2) / OD.

**Example:** gear has 40 teeth, OD measures 5.25". DP = 42 / 5.25 = **8**. PD = 40 / 8 = 5.000". It meshes with a 16-tooth 8 DP pinion (PD 2.0") at a centre distance of (40 + 16)/(2 × 8) = **3.500"**.

## Sprockets and chain

```
Sprocket pitch diameter    PD = P / sin(180° / N)          P = chain pitch, N = teeth
Sprocket outside diameter  OD ≈ P × (0.6 + 1 / tan(180° / N))
Chain speed (ft/min)       = P (in) × N × rpm / 12
Chain length (pitches)     L = 2C/P + (N1 + N2)/2 + (N2 − N1)² × P / (39.5 × C)     C = centre distance (in); round UP to an even number
Centre distance from a chain length: solve the above, or lay it out
```

**Example:** #60 chain (P = 0.75"), 24-tooth sprocket. PD = 0.75 / sin 7.5° = 0.75 / 0.1305 = **5.747"**. At 194 rpm the chain speed = 0.75 × 24 × 194 / 12 = **291 ft/min** (type A manual lubrication is fine below about 350 fpm for #60).

**Example - chain length:** 15 T and 45 T #60 sprockets on 24" centres. 2C/P = 64 pitches; (15 + 45)/2 = 30; (30)² × 0.75 / (39.5 × 24) = 675 / 948 = 0.7. L = 94.7 → **96 pitches** (even, connecting link, no offset), then move the motor to take up the slack.

## Belts, pulleys, conveyors

```
Belt / rim speed (ft/min)  = π × D (in) × rpm / 12 = 0.2618 × D × rpm
Belt speed (m/s)           = π × D (m) × rpm / 60
Conveyor belt speed        same formula with the drive pulley diameter (add belt thickness to D for accuracy)
Belt length (open drive)   L = 2C + 1.57 (D + d) + (D − d)² / (4C)
Conveyor capacity (tons/h) = load (lb per ft of belt) × belt speed (ft/min) × 60 / 2 000
Bulk load per foot         = cross-section area (ft²) × material density (lb/ft³)
Conveyor drive HP (flat, rough) = (belt pull lb × fpm) / 33 000 / efficiency ;  belt pull = friction × total moving weight + lift
```

V-belt drives should run between about 1 000 and 6 000 ft/min; above 6 500 fpm sheaves need dynamic balancing; below 1 000 fpm the belt is doing very little work per belt.

**Example:** 24" head pulley at 60 rpm: belt speed = 0.2618 × 24 × 60 = **377 ft/min**. Carrying 40 lb per foot of gravel: 40 × 377 × 60 / 2000 = **452 tons/h**.

## Torque to accelerate a load (starting, braking, flywheels)

```
Accelerating torque  T (ft-lb) = WK² × Δrpm / (308 × t)        WK² in lb-ft², t in seconds
WK² of a solid cylinder      = W × r² / 2   (W lb, r ft)     ; thin rim = W × r²
WK² reflected to the motor   = WK²_load / ratio²             (a 10:1 reducer makes the load look 100× lighter)
Time to accelerate           t = WK² × Δrpm / (308 × T_available)
```

**Example:** a fan wheel with WK² = 500 lb-ft² must reach 1 750 rpm in 5 s. T = 500 × 1750 / (308 × 5) = **568 ft-lb** of accelerating torque, on top of the running torque. A 30 hp motor (90 ft-lb full load, maybe 200 ft-lb pull-up) cannot do that in 5 s; it will take 500 × 1750 / (308 × 200) ≈ 14 s of near-locked-rotor current, which is why big fans get soft starters or VFDs, and why repeated starts overheat motors.

## Simple machines and mechanical advantage

```
Lever                       F1 × L1 = F2 × L2   (distances from the fulcrum)
Wheel and axle              MA = wheel radius / axle radius
Block and tackle            MA = number of rope parts supporting the moving block ;  actual ≈ MA × (0.9)^sheaves
Inclined plane              MA = length of slope / height ;  force to push up = W × (sin θ + μ cos θ)
Screw jack / threaded rod   MA = 2 π R / lead    (R = handle radius; lead = pitch × starts) ;  real efficiency 20-40%
Wedge                       MA = length / thickness
Hydraulic press             F2 = F1 × (A2 / A1)   ; the small piston travels A2/A1 times farther
Gear / sprocket / pulley    MA = ratio (torque multiplication) at the cost of speed
Torque wrench extension     wrench setting = target × L_wrench / (L_wrench + L_extension)
```

**Example - lever:** a 6 ft bar with the fulcrum 6" from the load. MA = 66 / 6 = 11. A 150 lb push lifts 1 650 lb (minus friction). Pry bars, gear pullers and hook spanners all live on this formula.

**Example - chain hoist:** 4 parts of load chain, 3 sheaves. Ideal MA 4; actual about 4 × 0.9³ = 2.9, so a 1-ton lift needs about 690 lb of pull if it were a simple tackle. Real chain hoists add a gear train, which is why one hand lifts a ton.

**Example - hydraulic press:** hand pump piston 0.5" dia (0.196 in²), ram 4" dia (12.57 in²). MA = 64. A 100 lb push makes 6 400 lb of ram force, and the ram moves 1/64 as far as the pump piston.

## Sizing checklist

1. Get the **load torque** at the driven shaft (from process or from amps on the existing motor).
2. Divide by ratio and efficiencies back to the motor: T_motor = T_load / (ratio × η).
3. HP = T_motor × rpm / 5252. Add accelerating torque if starts are frequent or the inertia is large.
4. Choose the next standard motor size, without relying on the service factor.
5. Check every element between motor and load for the **torque at its own shaft**, at the **lowest speed** it runs (VFD-driven machines at low speed are torque-limited, not hp-limited).
6. Check belt speed, chain speed and bearing speed limits.

## Related

- [Pump and fluid-power formulas](/article/pump-and-fluid-power-formulas)
- [Shaft, bearing and fastener formulas](/article/shaft-bearing-fastener-formulas)
- [V-belt drives](/article/v-belt-drive-installation-and-tensioning)
- [Roller chain drives](/article/roller-chain-drives)
- [Shop reference tables](/article/shop-reference-tables)
