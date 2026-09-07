---
title: "Pump and Fluid-Power Formulas: Head, Pressure, Flow, Horsepower, Affinity Laws, NPSH, Friction Loss and Hydraulic Cylinders"
slug: pump-and-fluid-power-formulas
category: shop-reference
kind: chart
tags: [formulas, pump formulas, head to psi, 2.31, specific gravity, flow velocity, water horsepower, brake horsepower, 3960, affinity laws, pump laws, NPSH, NPSHa, cavitation, total dynamic head, TDH, friction loss, Hazen-Williams, equivalent length, vapor pressure, pump curve, BEP, specific speed, hydraulic cylinder force, 1714, hydraulic horsepower, positive displacement, cylinder speed, hydraulic motor torque, compressed air, fan laws]
source: "Hydraulic Institute standards; Cameron Hydraulic Data; Crane Technical Paper 410 (fitting losses); Goulds Pump Selection guide; standard fluid-power references."
summary: "The pump math millwrights actually use, with the constants (2.31, 0.433, 3960, 1714, 231) explained and worked examples: converting head and pressure, velocity in pipe, water and brake horsepower, motor sizing, the affinity laws for VFDs and impeller trims, total dynamic head, NPSH available with vapor-pressure and altitude tables, friction loss and fitting equivalent lengths, reading a pump curve, plus positive-displacement pumps, hydraulic cylinders and motors, compressed air and fan laws."
---

## The constants and where they come from

| Constant | Meaning | Comes from |
|---|---|---|
| **2.31 ft per psi** | height of a column of water that makes 1 psi | 144 in²/ft² ÷ 62.4 lb/ft³ |
| **0.433 psi per ft** | pressure at the bottom of 1 ft of water | 1 / 2.31 |
| **3 960** | gpm × ft ÷ 3960 = water horsepower | 33 000 ft-lb/min ÷ 8.34 lb/gal |
| **1 714** | psi × gpm ÷ 1714 = hydraulic horsepower | 33 000 ÷ (231 ÷ 12) |
| **231** | cubic inches in a US gallon | definition |
| **0.4085** | ft/s = 0.4085 × gpm ÷ d² | 231 ÷ (60 × 0.7854 × 12) |
| **33.9 ft** | atmospheric pressure at sea level as water head | 14.7 psi × 2.31 |
| **32.2 ft/s²** | g, for velocity head V²/2g | gravity |

**Specific gravity (SG)** is the fluid's density relative to water (water = 1.0). Gasoline ≈ 0.72, diesel ≈ 0.85, lube oil ≈ 0.88-0.92, seawater 1.03, 50% caustic 1.53, brine up to 1.2. Every pressure ↔ head conversion carries SG; horsepower carries SG; head itself does **not** change with SG (a centrifugal pump makes the same feet of head on any liquid, but a different pressure).

## Head, pressure and velocity

```
Head (ft)      = psi × 2.31 / SG
psi            = head (ft) × SG / 2.31  = head × 0.433 × SG
Head (m)       = kPa × 0.102 / SG ;  bar = head (m) × SG / 10.2

Velocity (ft/s)      V = 0.4085 × gpm / d²          d = pipe inside diameter, inches
Flow (gpm)           Q = 2.448 × d² × V
Velocity head (ft)   hv = V² / (2 g) = V² / 64.4
Pressure at depth    psi = 0.433 × depth (ft) × SG
```

**Example:** a gauge on a pump discharge reads 60 psi pumping water. Head = 60 × 2.31 = **139 ft**. Same gauge on a 0.85 SG oil pump = 60 × 2.31 / 0.85 = 163 ft of oil. Same pump, same impeller, same speed will show only 60 × 0.85 = 51 psi on that oil.

**Example - velocity:** 200 gpm through 3" schedule 40 pipe (ID 3.068"). V = 0.4085 × 200 / 3.068² = 0.4085 × 200 / 9.41 = **8.7 ft/s**. That is fast for a suction line. Through 4" sch 40 (ID 4.026"): 0.4085 × 200 / 16.2 = **5.0 ft/s**.

Recommended velocities: suction lines **2-5 ft/s** (never over about 7), discharge **5-10 ft/s**, hydraulic pressure lines 15-20 ft/s, hydraulic return 10-15 ft/s, hydraulic suction 2-4 ft/s.

## Horsepower

```
Water (hydraulic) horsepower   WHP = gpm × TDH (ft) × SG / 3960
Brake horsepower (at pump shaft) BHP = WHP / pump efficiency
Motor horsepower needed          = BHP / motor efficiency, rounded up to the next motor size, with service factor in mind
Pump efficiency                  η = WHP / BHP

Metric: shaft power (kW) = Q (m³/h) × H (m) × SG / (367 × η)
```

**Example:** 200 gpm at 120 ft TDH, water, pump efficiency 70%. WHP = 200 × 120 × 1.0 / 3960 = **6.06 hp**. BHP = 6.06 / 0.70 = **8.66 hp**. Choose a **10 hp** motor (a 7.5 hp with 1.15 service factor would run at 8.66/7.5 = 115%, right at the SF limit, so do not). Pumping 1.2 SG brine instead: BHP = 8.66 × 1.2 = 10.4 hp → 15 hp motor.

**Reading BHP from the motor:** three-phase, BHP ≈ (1.732 × V × I × PF × motor eff) / 746. See the [power formulas](/article/power-torque-speed-drive-formulas).

## Affinity (pump) laws

For a given impeller when speed changes, or (approximately) for a given speed when impeller diameter is trimmed:

```
Flow      Q2 = Q1 × (N2 / N1)          or × (D2 / D1)
Head      H2 = H1 × (N2 / N1)²         or × (D2 / D1)²
Power     P2 = P1 × (N2 / N1)³         or × (D2 / D1)³
NPSHr changes roughly with (N2/N1)²
```

**Example - VFD:** pump at 1 750 rpm delivers 300 gpm at 100 ft using 10 bhp. Slowed to 1 400 rpm (ratio 0.8): Q = 300 × 0.8 = **240 gpm**, H = 100 × 0.64 = **64 ft**, P = 10 × 0.512 = **5.1 bhp**. Cutting flow 20% saved 49% of the power. That is why VFDs pay for themselves on throttled pumps.

**Example - impeller trim:** 13" impeller makes 150 ft; you need 130 ft. D2 = 13 × √(130/150) = 13 × 0.931 = **12.1"**. Trims beyond about 25% of the maximum diameter fall off the affinity laws; check the pump curve for the trimmed line, and stay above the minimum diameter the maker allows.

The same three laws are the **fan laws** (cfm, static pressure, hp) for centrifugal fans.

## Total dynamic head (TDH)

TDH is what the pump must produce. Build it from the system, always in feet of the liquid pumped:

```
TDH = static head + pressure head + friction head + velocity head

static head    = discharge liquid level (or outlet) elevation − suction liquid level elevation
                 (a suction LIFT adds to the head; a flooded suction subtracts)
pressure head  = (discharge vessel psi − suction vessel psi) × 2.31 / SG   (zero for open tanks)
friction head  = pipe friction + fitting/valve losses, suction side + discharge side, at the design flow
velocity head  = V² / 64.4 at the discharge (usually small; often ignored below 8 ft/s)
```

**Example:** water from a sump 10 ft below the pump to an open tank whose inlet is 45 ft above the pump; 200 gpm; suction friction 2 ft; discharge friction 14 ft; discharge velocity 8.7 ft/s. Static = 45 + 10 = 55 ft. Pressure = 0. Friction = 16 ft. Velocity head = 8.7² / 64.4 = 1.2 ft. **TDH = 72 ft.** Pick a pump whose curve passes through 200 gpm at 72 ft near its best efficiency point.

## NPSH: will it cavitate?

**NPSHa** (available) is set by the system. **NPSHr** (required) is on the pump curve. You need **NPSHa ≥ NPSHr + margin** (at least 3 ft, or 1.2 × NPSHr for hot or hydrocarbon service, more for large or high-energy pumps).

```
NPSHa = Ha + Hs − Hvp − Hf

Ha  = atmospheric pressure on the suction liquid surface, as head (33.9 ft at sea level; less at altitude;
      for a closed vessel use its absolute pressure × 2.31 / SG)
Hs  = static height of the liquid surface above the pump centreline (NEGATIVE for a suction lift)
Hvp = vapor pressure of the liquid at pumping temperature, as head
Hf  = friction loss in the suction pipe, valves, strainer and fittings at the design flow
```

### Water vapor pressure

| Temperature | Vapor pressure (psia) | As head (ft) | SG |
|---|---|---|---|
| 40°F (4°C) | 0.12 | 0.3 | 1.000 |
| 60°F (16°C) | 0.26 | 0.6 | 0.999 |
| 80°F (27°C) | 0.51 | 1.2 | 0.997 |
| 100°F (38°C) | 0.95 | 2.2 | 0.993 |
| 120°F (49°C) | 1.69 | 4.0 | 0.989 |
| 140°F (60°C) | 2.89 | 6.8 | 0.985 |
| 160°F (71°C) | 4.74 | 11.2 | 0.979 |
| 180°F (82°C) | 7.51 | 17.8 | 0.972 |
| 200°F (93°C) | 11.53 | 27.7 | 0.963 |
| 212°F (100°C) | 14.70 | 35.4 | 0.959 |

Hot water is the classic cavitation case: at 200°F almost all of the atmosphere is eaten by vapor pressure, so the pump needs a **flooded** suction of several feet.

### Atmospheric pressure vs altitude

| Altitude (ft) | psia | Water head (ft) |
|---|---|---|
| 0 | 14.7 | 33.9 |
| 1 000 | 14.2 | 32.8 |
| 2 000 | 13.7 | 31.6 |
| 3 000 | 13.2 | 30.5 |
| 5 000 | 12.2 | 28.2 |
| 7 000 | 11.3 | 26.2 |
| 10 000 | 10.1 | 23.4 |

**Example:** sea level, water at 140°F, pump takes suction with an 8 ft lift, suction friction and strainer 3 ft. NPSHa = 33.9 − 8 − 6.8 − 3 = **16.1 ft**. Pump curve shows NPSHr = 12 ft at the duty flow. Margin 4.1 ft: acceptable. At 180°F the same setup gives 33.9 − 8 − 17.8 − 3 = 5.1 ft: it will cavitate. Fixes, in order of cost: cool the liquid, raise the tank or lower the pump (flooded suction), bigger suction pipe, shorter suction pipe, larger/slower pump with lower NPSHr, inducer.

### Signs of cavitation

Sound like pumping gravel, vibration, pitted impeller vanes on the low-pressure (back) side near the eye, falling head and flow, seal and bearing failures. Also check for the other "cavitation": air entrainment from a vortexing sump or a suction leak (bubbles, not vapor).

## Friction loss

### Hazen-Williams (water, turbulent flow)

```
hf (ft per 100 ft of pipe) = 0.2083 × (100 / C)^1.852 × Q^1.852 / d^4.8655
Q = gpm, d = inside diameter (in), C = pipe roughness coefficient
```

| Pipe | C |
|---|---|
| New steel, new cast iron | 130 |
| Steel/cast iron, 10-20 years in service | 100 (use this for design) |
| Old, tuberculated steel | 60-80 |
| PVC, HDPE, copper, stainless | 140-150 |

**Example:** 100 gpm in 3" sch 40 steel (3.068"), C = 100. 100^1.852 = 5 060. 3.068^4.8655 = 234. hf = 0.2083 × 5 060 / 234 = **4.5 ft per 100 ft**. Doubling the flow to 200 gpm raises it 2^1.852 = 3.6× to about 16 ft per 100 ft: friction grows almost with the square of flow.

### Fittings and valves as equivalent length

Add these to the straight pipe length before multiplying by the ft-per-100-ft figure (Crane TP-410 L/D ratios, turbulent flow):

| Fitting | Equivalent length in pipe diameters (L/D) | 3" pipe example (ft) |
|---|---|---|
| 90° standard elbow | 30 | 7.7 |
| 90° long-radius elbow | 16 | 4.1 |
| 45° elbow | 16 | 4.1 |
| Tee, flow straight through | 20 | 5.1 |
| Tee, flow through the branch | 60 | 15.3 |
| Gate valve, fully open | 8 | 2.0 |
| Globe valve, fully open | 340 | 87 |
| Angle valve, open | 150 | 38 |
| Swing check valve | 100 | 26 |
| Lift check valve | 600 | 153 |
| Butterfly valve (6-12") | 45 | 11.5 |
| Ball valve, full port | 3 | 0.8 |
| Pipe entrance, sharp | K = 0.5 (≈ 25 L/D) | 6.4 |
| Pipe exit | K = 1.0 (≈ 50 L/D) | 12.8 |

Equivalent length (ft) = (L/D) × d (in) / 12. A globe valve costs the same as 87 ft of 3" pipe; that is why a discharge throttle valve is a globe valve and the isolation valves are gates or balls.

### Head loss from a K factor

```
h = K × V² / 64.4        (ft)
```

Strainers: basket type ≈ K 1-2 clean, far higher fouled; always include the strainer in NPSHa and check its ΔP gauge.

## Reading a pump curve

- **H-Q curve**: head falls as flow rises. The **shutoff head** (zero flow) is the left end; **run-out** is the right end. Never run a centrifugal pump at either for long.
- **BEP**: best efficiency point. Aim for a duty between about **70% and 120% of BEP flow**. Left of that, recirculation, heat and radial thrust; right of it, cavitation and overload.
- **Power curve**: for radial-flow pumps, power rises with flow; a non-overloading motor is sized for the end of the curve. Axial-flow pumps are the opposite.
- **NPSHr curve**: rises steeply toward run-out.
- **Impeller trims**: several H-Q lines for different diameters; efficiency islands drawn across them.
- **System curve**: static head (flat) plus friction (rising with Q²). The pump operates where the two cross. Throttling the discharge steepens the system curve and moves the point left; a VFD lowers the pump curve instead.

Specific speed (tells you the impeller type): Ns = N × √Q / H^0.75 (rpm, gpm, ft at BEP, per stage). Under 1 500 radial (high head), 1 500-4 500 Francis/mixed, over 8 000 axial. Suction specific speed Nss = N × √Q / NPSHr^0.75; keep it below about 9 000-11 000 for reliable operation.

Minimum continuous flow is on the data sheet; protect with a bypass or recirculation line if the process can go below it.

## Positive-displacement pumps

Flow is set by displacement and speed, not by head. Pressure is set by the system, so a **relief valve is mandatory**.

```
Flow (gpm)   = displacement (in³ per rev) × rpm / 231 × volumetric efficiency
Flow (gpm)   = displacement (gal per rev) × rpm × ηv
Torque (in-lb) at the shaft = displacement (in³/rev) × psi / (6.28 × mechanical efficiency)
```

**Example:** gear pump, 2.5 in³/rev, 1 800 rpm, ηv 0.95. Q = 2.5 × 1800 / 231 × 0.95 = **18.5 gpm**. At 2 000 psi with 90% mechanical efficiency, shaft torque = 2.5 × 2000 / (6.28 × 0.9) = 885 in-lb, and hp = 885 × 1800 / 63 025 = 25.3 hp. Check: hydraulic hp = 2000 × 18.5 / 1714 = 21.6 hp, divided by overall efficiency 0.855 = 25.3 hp. Same answer.

Reciprocating pumps: displacement per stroke = 0.7854 × bore² × stroke (single acting); double acting subtract the rod area on the return stroke.

## Hydraulics: cylinders, motors, horsepower

```
Cylinder force (lb)          F = psi × area (in²)
   extend area = 0.7854 × bore² ;  retract area = 0.7854 × (bore² − rod²)
Cylinder speed (in/min)      = gpm × 231 / area (in²)      in/s = in/min ÷ 60
Cylinder flow needed (gpm)   = area × speed (in/min) / 231
Hydraulic horsepower         HP = psi × gpm / 1714
Electric motor for the pump  HP = psi × gpm / (1714 × overall pump efficiency)   (≈ 0.85 for piston pumps, 0.75-0.8 gear)
Hydraulic motor torque       T (in-lb) = displacement (in³/rev) × psi / 6.28 × ηm
Hydraulic motor speed        rpm = gpm × 231 / displacement × ηv
Torque ↔ HP                  HP = T (in-lb) × rpm / 63 025
Pressure drop across an orifice   Q ∝ √ΔP  (double the flow → four times the ΔP)
Fluid compressibility        about 0.5% per 1 000 psi (why accumulators are needed for stored energy)
```

**Example - press cylinder:** 4" bore, 2" rod, 2 000 psi. Extend force = 2000 × 12.57 = **25 100 lb (12.6 tons)**. Retract = 2000 × 9.42 = 18 800 lb. At 10 gpm: extend speed = 10 × 231 / 12.57 = 184 in/min = **3.1 in/s**; retract = 10 × 231 / 9.42 = 245 in/min (faster because less volume to fill). Hydraulic hp = 2000 × 10 / 1714 = **11.7 hp**; motor ≈ 11.7 / 0.85 = 13.7 → 15 hp.

**Example - hydraulic motor:** 5 in³/rev at 2 500 psi, 90% mechanical efficiency. T = 5 × 2500 / 6.28 × 0.9 = **1 790 in-lb** (149 ft-lb). Fed 12 gpm at 95% volumetric efficiency: rpm = 12 × 231 / 5 × 0.95 = 527 rpm. HP = 1790 × 527 / 63 025 = 15 hp.

**Accumulator sizing (rule):** usable volume ≈ V_acc × (P_precharge / P_min − P_precharge / P_max) for slow (isothermal) use; precharge ≈ 90% of minimum system pressure.

Cleanliness: ISO 4406 codes such as 18/16/13 (servo valves need cleaner, e.g. 16/14/11). Most hydraulic failures are contamination.

## Compressed air

```
Cylinder force              F = psi × area (same as hydraulic; 80-100 psi typical)
Boyle's law (constant T)    P1 × V1 = P2 × V2          absolute pressures (psig + 14.7)
Free air from a receiver    ft³ free air = receiver ft³ × (psig / 14.7)
Receiver pump-down/up time  t (min) = V (ft³) × (P2 − P1) / (14.7 × compressor cfm)
Compressor power            roughly 4-5 cfm per hp at 100 psig
Receiver size (rule)        1 gal per cfm of compressor capacity, minimum
```

SCFM is free air at standard conditions; the volume inside the line at 100 psig is SCFM ÷ (114.7/14.7) = SCFM ÷ 7.8.

**Example:** 120-gal (16 ft³) receiver, compressor 25 cfm, from 90 to 125 psig: t = 16 × 35 / (14.7 × 25) = **1.5 min**.

## Fans (same laws as pumps)

```
Air horsepower       AHP = cfm × static pressure (in. w.c.) / 6 356
Brake horsepower     BHP = AHP / fan efficiency
Fan laws             cfm ∝ rpm ;  SP ∝ rpm² ;  hp ∝ rpm³
Duct velocity        fpm = cfm / duct area (ft²)
```

**Example:** 10 000 cfm at 2.5" w.c., 65% efficient fan: AHP = 25 000 / 6356 = 3.9 hp; BHP = 6.1 hp → 7.5 hp motor. Speed it up 10% and the motor needs 6.1 × 1.331 = 8.1 hp, so it overloads.

## Troubleshooting with the formulas

| Symptom | Formula that explains it |
|---|---|
| Discharge pressure low, flow high, motor overloaded | Operating right of BEP; system head lower than designed (open valve, broken pipe); power ∝ Q on radial pumps |
| Pressure gauge fine but no flow | Air-bound or blocked discharge; head is there, flow is not; check with the H-Q curve |
| Amps up after a fluid change | BHP ∝ SG |
| Pump lost 15% flow after speed dropped 5% on the VFD | Q ∝ N but system static head unchanged, so the operating point slides down the curve faster than the affinity law alone |
| Gravel noise at high flow | NPSHr rises with Q²; NPSHa falls as suction friction rises with Q² |
| PD pump relief valve chattering | Relief set too close to operating pressure; pressure is set by the system, flow by the pump |

## Related

- [Geometry formulas: areas, volumes, weights](/article/geometry-formulas-area-volume-weight)
- [Power, torque, speed and drive formulas](/article/power-torque-speed-drive-formulas)
- [Mechanical seal replacement on a centrifugal pump](/article/mechanical-seal-replacement-centrifugal-pump)
- [Shop reference tables](/article/shop-reference-tables)
