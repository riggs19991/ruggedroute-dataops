---
title: "Reading a Motor Nameplate: HP and kW, Voltage and Dual Voltage, FLA and Service Factor, RPM and Slip, Frame Size (NEMA T-Frame Dimensions Table: Shaft Height and Diameter), Enclosure (ODP, TEFC, TENV, XP), Insulation Class and Temperature Rise, Duty, Design Letter (B, C, D), Code Letter, Efficiency, Bearings, Mounting, Inverter Duty"
slug: reading-a-motor-nameplate
category: motors-electrical
kind: reference
tags: [motor nameplate, motor data plate, FLA, full load amps, service factor, SF 1.15, motor rpm, slip, synchronous speed, NEMA frame, frame size, 143T, 182T, 213T, 254T, 284T, 324T, 364T, 405T, 444T, shaft height, shaft diameter motor, TEFC, ODP, TENV, explosion proof motor, insulation class F, temperature rise, NEMA design B, code letter, locked rotor, motor efficiency, premium efficiency, inverter duty, motor bearings nameplate, motor replacement, IEC frame]
source: "NEMA MG 1 Motors and Generators (nameplate requirements, design letters, frame dimensions, code letters, insulation classes); Baldor-Reliance/ABB and WEG motor catalogues (frame dimension tables, nameplate examples); IEC 60034 (IEC frame designations); EASA motor replacement guidance."
summary: "Every line on a three-phase motor nameplate and what it means to the millwright replacing or troubleshooting the motor: the power, voltage and current ratings and how the service factor is used, speed and slip, the NEMA frame number decoded into the shaft height and dimensions with a table of the T-frames, the enclosure types and where each belongs, insulation class and temperature rise, design and code letters, efficiency, bearing numbers and mounting, and what to match when you swap a motor."
---

## The lines and what they mean

![A typical nameplate with the lines to read first](/img/motors-electrical/motor-nameplate.svg)

*A typical nameplate with the lines to read first*

| Nameplate item | Meaning | What you do with it |
|---|---|---|
| **HP (or kW)** | Rated mechanical output at the shaft (1 hp = 0.746 kW) | The replacement must match or exceed; the driven load's need decides |
| **Volts** | Rated supply voltage; dual voltage motors show both (230/460, 208-230/460, 575) | Connect for the supply (see [lead connections](/article/motor-lead-connections)); a 460 V motor on 480 V is normal (the utilisation voltage tolerance is ±10%: 414-506 V) |
| **Amps (FLA)** | Full-load current at each voltage (twice as much at the low voltage) | Sets the overload relay (FLA × the SF allowance per the NEC), the wire size, the clamp-meter check: running amps vs FLA tells you the load; amps above FLA = overloaded or a problem |
| **Service factor (SF)** | The overload the motor can carry continuously at rated voltage and frequency without damage: **1.15** on most ODP and many TEFC motors, **1.0** on others | A 1.15 SF motor can run at 115% of nameplate hp (at reduced life and higher temperature); do **not** size a drive to use it; SFA (service factor amps) is the current at that load |
| **RPM** | Full-load speed (e.g. 1,765) | The synchronous speed is the next round number up (1,800 for a 4-pole 60 Hz motor); the difference is **slip** (35 rpm here); a motor running at synchronous speed is unloaded; a motor slipping more than the nameplate is overloaded or on low voltage. Poles = 120 × Hz ÷ sync rpm: 2-pole 3,600, **4-pole 1,800**, 6-pole 1,200, 8-pole 900 |
| **Hz** | 60 (North America) or 50; some plates give both | A 60 Hz motor on 50 Hz runs at 5/6 speed and must be derated |
| **Phase** | 3 or 1 | |
| **Frame** | NEMA frame number (143T, 256T, 405T...) or an IEC frame (IEC 132M, 160L) | The **mounting dimensions**: see the table below; a replacement must have the same frame (or an adapter base) |
| **Enclosure** | ODP, TEFC, TENV, TEAO, WPI/WPII, XP (explosion-proof, with the Class/Division/Group), IP code (IP55) | Match to the environment (below) |
| **Insulation class** | The winding's temperature rating: **A 105°C, B 130°C, F 155°C, H 180°C** (total temperature = 40°C ambient + rise + a hot-spot allowance) | Most industrial motors are **Class F**; the rise below tells you how hot it is designed to run |
| **Temperature rise / Amb** | The winding temperature rise at rated load (e.g. "80°C rise" or "Class B rise") above a **40°C ambient** | A Class F motor with a Class B rise (80°C) has a 25°C reserve: longer life, tolerates a VFD or a warm room; above 40°C ambient the motor is derated |
| **Duty** | CONT (continuous) or a time rating (30 min, 1 h) or a duty cycle (S1-S8 on IEC) | Intermittent-rated motors overheat on continuous loads |
| **Design** (NEMA design letter) | **B**: the standard (normal starting torque, low starting current, 3-5% slip); **A**: like B with higher starting current; **C**: high starting torque (conveyors loaded at start, compressors); **D**: very high starting torque, high slip 5-13% (punch presses, hoists, cranes) | A design D motor replaced by a B stalls the loaded conveyor at start; match |
| **Code letter** (kVA/hp locked rotor) | A-V: the locked-rotor kVA per hp (A: under 3.15; G: 5.6-6.3; **J: 7.1-8.0**; K: 8.0-9.0; L: 9.0-10; M: 10-11.2...) | Sets the starter's instantaneous trip and the starting current: LRA ≈ code kVA/hp × hp × 1000 ÷ (1.732 × V); a 50 hp code J at 460 V draws about 470 A at start (about 6-7× FLA) |
| **Efficiency (NEMA nominal)** | % at full load; "Premium Efficient" (NEMA Premium / IE3) | The energy label; a premium motor runs slightly faster (less slip) than the old one it replaces: a fan or pump draws more power on it (the affinity laws) |
| **Power factor** | | |
| **Bearings** (DE / ODE) | The bearing numbers (6309, 6311, NU 319) | Order spares; regrease amounts by bearing (see [regreasing](/article/regreasing-intervals-and-quantities)); a roller bearing (NU) on the drive end of belted motors |
| **Mounting / Type** | Foot (F1 = conduit box on the left viewed from the drive end, F2 right), C-face, D-flange, vertical P-base, IEC B3/B5/B14/V1 | |
| **Inverter duty / VFD rated** | "Inverter duty" with a speed range (e.g. 10:1 constant torque, 1000:1 with a blower) per NEMA MG 1 Part 31 | Required on VFDs for winding insulation (voltage spikes) and cooling at low speed; a standard motor on a VFD needs derating and a minimum speed |
| **Thermal protection** | "Thermally protected" (built-in), thermostats (P1/P2 leads), RTDs | Wire the thermostats into the control |
| **Serial number, date, weight, rotation arrow, connection diagram** | | The diagram on the plate is the lead connection for each voltage |
| **kVA code, LRA, max ambient, altitude (over 3,300 ft derate)** | | |

IEC plates: kW, the IEC frame (the number is the **shaft height in mm**: IEC 132 = 132 mm; the letter S/M/L is the frame length), the duty S1, the IP rating (IP55 = dust and jets), the connection ∆/Y with the voltages (e.g. 230∆/400Y), the cos φ, the efficiency class IE2/IE3.

## NEMA frame dimensions (T-frames, foot-mounted; inches)

The frame number encodes the **shaft height D**: the first two digits ÷ 4 for two-digit frames (143T: 14 ÷ 4 = 3.5"), the first two digits ÷ 4 for three-digit frames (405T: 40 ÷ 4 = 10"); the third digit and the T set the foot spacing; T = the 1964 standard; U = the older standard with different shaft and foot dimensions for the same D.

| Frame | D (shaft height) | 2E (foot width, centre to centre) | 2F (foot length, centre to centre) | BA (foot to shaft shoulder) | Shaft dia U | Shaft length N-W | Key | Typical hp at 1,800 rpm |
|---|---|---|---|---|---|---|---|---|
| **143T** | 3.50 | 5.50 | 4.00 | 2.25 | **0.875** | 2.25 | 3/16 | 1 |
| **145T** | 3.50 | 5.50 | 5.00 | 2.25 | 0.875 | 2.25 | 3/16 | 1.5-2 |
| **182T** | 4.50 | 7.50 | 4.50 | 2.75 | **1.125** | 2.75 | 1/4 | 3 |
| **184T** | 4.50 | 7.50 | 5.50 | 2.75 | 1.125 | 2.75 | 1/4 | 5 |
| **213T** | 5.25 | 8.50 | 5.50 | 3.50 | **1.375** | 3.38 | 5/16 | 7.5 |
| **215T** | 5.25 | 8.50 | 7.00 | 3.50 | 1.375 | 3.38 | 5/16 | 10 |
| **254T** | 6.25 | 10.00 | 8.25 | 4.25 | **1.625** | 4.00 | 3/8 | 15 |
| **256T** | 6.25 | 10.00 | 10.00 | 4.25 | 1.625 | 4.00 | 3/8 | 20 |
| **284T** | 7.00 | 11.00 | 9.50 | 4.75 | **1.875** | 4.63 | 1/2 | 25 |
| **286T** | 7.00 | 11.00 | 11.00 | 4.75 | 1.875 | 4.63 | 1/2 | 30 |
| **324T** | 8.00 | 12.50 | 10.50 | 5.25 | **2.125** | 5.25 | 1/2 | 40 |
| **326T** | 8.00 | 12.50 | 12.00 | 5.25 | 2.125 | 5.25 | 1/2 | 50 |
| **364T** | 9.00 | 14.00 | 11.25 | 5.88 | **2.375** | 5.88 | 5/8 | 60 |
| **365T** | 9.00 | 14.00 | 12.25 | 5.88 | 2.375 | 5.88 | 5/8 | 75 |
| **404T** | 10.00 | 16.00 | 12.25 | 6.62 | **2.875** | 7.25 | 3/4 | 100 |
| **405T** | 10.00 | 16.00 | 13.75 | 6.62 | 2.875 | 7.25 | 3/4 | 125 |
| **444T** | 11.00 | 18.00 | 14.50 | 7.50 | **3.375** | 8.50 | 7/8 | 150 |
| **445T** | 11.00 | 18.00 | 16.50 | 7.50 | 3.375 | 8.50 | 7/8 | 200 |
| 447T | 11.00 | 18.00 | 20.00 | 7.50 | 3.375 | 8.50 | 7/8 | 250 |
| 449T | 11.00 | 18.00 | 25.00 | 7.50 | 3.375 | 8.50 | 7/8 | 300 |

"TS" frames (e.g. 254TS) have a **shorter, smaller shaft** for direct coupling only (no belts): a 254TS shaft is 1.375" × 2.0" instead of 1.625" × 4.0". "U" frames (older, pre-1964) have different shaft diameters and foot spacings for the same D: a U-frame motor is replaced with a T-frame of the same D using an adapter base and a new coupling/sheave bore. Hp per frame varies with speed (a 3,600 rpm motor is one frame smaller for the same hp; 1,200 rpm one larger); the table's hp column is the usual 1,800 rpm assignment for standard-efficiency and many premium motors (premium and TEFC motors sometimes step up a frame).

## Enclosures

| Type | Meaning | Where |
|---|---|---|
| **ODP** (open drip-proof) | Openings for cooling air, drips from above cannot enter | Clean, dry indoor: the cheapest; dust and washdown kill it |
| **TEFC** (totally enclosed fan-cooled) | Sealed frame, an external fan on the ODE blows air over the fins | The industrial standard: dust, damp, outdoor (with a drain and a cover); the fan cover must be kept clear |
| **TENV** (totally enclosed non-ventilated) | Sealed, no fan; cools by its surface | Small motors, VFD low-speed duty |
| **TEAO** (totally enclosed air-over) | Cooled by the driven fan's air | Fan motors |
| TEBC (blower-cooled) | A separate constant-speed blower | Inverter duty at low speed |
| **Washdown / severe duty / IEEE 841** | TEFC with extra sealing, stainless hardware, epoxy paint, drains, IP56-66 | Food, chemical, mines, paper |
| **XP** (explosion-proof, Class I Div 1 Groups C/D; Class II Div 1 Groups F/G dust-ignition-proof) | Contains an internal explosion without igniting the outside; a T-code surface temperature | Classified areas; the conduit seals and the cover flame paths must be intact: never file or paint a flame path, never run with a missing bolt |
| WPI / WPII | Weather-protected (large motors, outdoors) | |
| IP | IP23 (open), IP54/55 (TEFC), IP56/66 (washdown), IP65+ | IEC |

## Matching a replacement motor

Same **frame** (or an adapter), **hp** (≥), **voltage** and connection, **speed** (poles) and design letter, **enclosure** for the environment, **mounting** (foot/face/flange, conduit box side: F1/F2 can be changed on many motors by rotating the end bells), **service factor**, **insulation/rise**, **inverter duty** if on a VFD, **bearings** (roller DE for belted loads), **rotation** (most are bi-directional; some fans are uni-directional), **thermostats/RTDs** if the control needs them, and the **shaft**: a TS shaft cannot carry a sheave. A premium-efficiency replacement on a fan or pump runs faster and draws more power: check the amps after the change.

## Reading the plate on the job

- Before lockout, record: hp, volts, FLA, rpm, frame, enclosure, SF, bearings, serial. Photograph the plate and the connection diagram.
- Check the running amps against FLA on all three phases with a clamp meter (imbalance under 10% between phases; a motor at 110% FLA is at its SF limit); the supply voltage between phases (imbalance under 1% per NEMA; voltage imbalance of 3.5% derates the motor to about 90%).
- The nameplate rpm against a tachometer under load: excessive slip = overload, low voltage, a bad rotor bar.

## Common mistakes

- Replacing a design C conveyor motor with a design B: it will not start loaded.
- A 1.0 SF TEFC motor sized to run at 115% "like the old ODP did".
- A 254T ordered for a 254U machine: the shaft is smaller and the feet are different.
- ODP motor in a washdown area: a month.
- Standard motor on a new VFD at 10 Hz for hours: the winding cooks with no fan speed.
- 208 V supply on a 230/460 motor connected for 230: it runs hot at 90% voltage; order a 200 V or a 208-230/460 motor.
- Reading FLA from the plate of a dual-voltage motor at the wrong voltage: the overload set at half the value.

## Related

- [Motor lead connections](/article/motor-lead-connections)
- [VFD basics for millwrights](/article/vfd-basics-for-millwrights)
- [Megger and basic motor testing](/article/megger-and-basic-motor-testing)
- [Regreasing intervals and quantities (motor tables)](/article/regreasing-intervals-and-quantities)
- [Power, torque, speed and drive formulas](/article/power-torque-speed-drive-formulas)
- [Electrical safety for mechanics](/article/electrical-safety-for-mechanics)
