---
title: "Hydraulic Motors and Hydrostatic Drives: Gear, Gerotor and Orbital, Vane, Axial and Radial Piston Motors, Case Drains, Freewheeling and Shaft-Seal Limits, Torque and Speed Math, Closed-Loop Hydrostatic Transmissions (Charge Pump and Charge Pressure, Charge Relief, Cross-Port Reliefs, Flushing Valve, Neutral and Displacement Adjustment, Tow Bypass), the Diagnostic Sequence (Charge Pressure First) and the Symptoms of a Dying Hydrostat"
slug: hydraulic-motors-and-hydrostatic-drives
category: hydraulics
kind: reference
tags: [hydraulic motor, gear motor, gerotor motor, orbital motor, Char-Lynn, Danfoss OMP, vane motor, axial piston motor, bent axis motor, radial piston motor, LSHT motor, low speed high torque, cam lobe motor, motor case drain, motor freewheeling, motor back pressure, motor shaft seal, hydraulic motor torque, motor displacement, motor speed calculation, motor volumetric efficiency, hydrostatic transmission, hydrostatic drive, closed loop hydraulic, HST, charge pump, charge pressure, charge relief, charge filter, cross port relief, high pressure relief, multi-function valve, flushing valve, hot oil shuttle, loop flushing, neutral adjustment, hydrostatic creep, displacement control, servo control, tow valve, bypass valve, hydrostatic troubleshooting, skid steer hydrostat, zero turn mower hydrostat, combine hydrostatic, wheel motor, track drive motor, two speed motor]
source: "Danfoss (Sauer-Danfoss) Series 90, Series 40 and H1 service manuals and Hydrostatic Transmission Troubleshooting Guide (charge pressure, case drain, adjustment and test procedures); Danfoss OMP/OMR/OMS orbital motor technical information; Eaton Vickers Mobile Hydraulics Manual (motor types, closed-loop circuits); Eaton (Char-Lynn) motor service data; Parker and Bosch Rexroth motor catalogues (case drain and shaft seal limits); Hydro-Gear and Tuff Torq service manuals (small hydrostats); Fluid Power Society technician manuals."
summary: "The rotary half of hydraulics: how each motor type makes torque, what its case drain, back-pressure and shaft-seal limits are and why motors die of a plugged drain, how to calculate torque and speed and check them against a flow meter, and the closed-loop hydrostatic transmission that drives loaders, skid steers, combines, mowers and rollers: what every valve in the loop does, why the charge pressure is the first reading in any hydrostatic diagnosis, how to adjust neutral and displacement, and the symptom list that separates a tired pump from a tired motor from a leaking loop."
---

## Motor types

![Orbital (gerotor) motor on a machine: the nameplate gives displacement, pressure and the case-drain requirement](/photos/hydraulics/hydraulic-motor.jpg)

*Orbital (gerotor) motor on a machine: the nameplate gives displacement, pressure and the case-drain requirement. Photo: Simiprof, CC0, via commons*

| Type | How | Speed range | Torque | Pressure | Efficiency | Notes |
|---|---|---|---|---|---|---|
| **Gear** | An external gear pump run backwards | 500-3,000 rpm | Low | 2,000-3,000 psi | 80-85% overall | Cheap, tolerant, poor at low speed (cogging, low starting torque: about 70% of running); fans, conveyors, augers |
| **Gerotor / geroler (orbital, LSHT)** (Char-Lynn, Danfoss OMP/OMR/OMS, White) | An inner rotor orbits inside a fixed outer ring with rollers; a valve (spool or disc) commutates the flow; the orbiting motion is taken out through a **dogbone (drive link)** | 10-800 rpm | High at low speed | 2,000-3,000 psi; to 4,500 on heavy series | 75-85% | The universal wheel, auger, conveyor and winch motor; 1-40 in³/rev; a spline or a splined dogbone that strips is the classic failure; needs a case drain above about 100-300 psi return pressure (a **drain port** on most) |
| **Vane** | Vanes held out by springs (a motor cannot rely on centrifugal force at start) | 100-2,500 rpm | Medium | 2,000-2,500 psi | 80-85% | Quiet, smooth; machine tools, winches; contamination-sensitive |
| **Axial piston, swashplate** (fixed or variable) | The pump in reverse; a variable motor changes its displacement to give a two-speed or stepless output (small displacement = high speed, low torque) | 50-5,000 rpm | High | 4,000-6,000 psi | 90-95% | Hydrostatic drive motors, winches, mixers, presses' rotary tables; always a case drain; contamination-sensitive |
| **Bent axis piston** (fixed or variable) | Barrel angled to the shaft; the most efficient motor | 50-8,000 rpm | Very high | 5,000-6,500 psi | 92-96% | Track drives, excavator swing and travel, winches, two-speed wheel motors |
| **Radial piston (cam lobe, multi-lobe) LSHT** (Poclain, Hägglunds, Rexroth MCR, Black Bruin) | Pistons push rollers against a multi-lobe cam ring; enormous torque at a few rpm, often direct-drive onto a wheel or a drum | 0.5-300 rpm | Enormous (to 100,000+ ft-lb) | 4,000-6,500 psi | 90-95% | Wheel motors on rollers and harvesters, mill drives, conveyor pulleys, winches; two-speed by disabling half the pistons; a **freewheel** position for towing |
| **Wheel motor / track drive** (a motor with an integral planetary gearbox and a parking brake) | A piston or orbital motor plus a 20:1-100:1 reduction and a spring-applied, pressure-released **brake** | | | | | The brake needs 200-400 psi to release: no charge pressure = a locked wheel; the gearbox has its own oil |

**Torque and speed**:

```
   Torque (in-lb) = displacement (in³/rev) × ΔP (psi) ÷ (2π) × ηm       (ηm mechanical efficiency 0.85-0.95; divide by 12 for ft-lb)
   Speed (rpm) = flow (gpm) × 231 ÷ displacement (in³/rev) × ηv          (ηv volumetric efficiency 0.90-0.97)
   Output hp = torque (ft-lb) × rpm ÷ 5,252
   Metric: T (N·m) = V (cm³/rev) × Δp (bar) ÷ 62.8 × ηm;   n (rpm) = Q (L/min) × 1000 ÷ V × ηv
```

Example: an orbital motor of 12.2 in³/rev (200 cm³) fed 10 gpm at a 2,000 psi drop, ηv 0.92, ηm 0.88: speed = 10 × 231 ÷ 12.2 × 0.92 = **174 rpm**; torque = 12.2 × 2,000 ÷ 6.28 × 0.88 = **3,420 in-lb (285 ft-lb)**; 9.4 hp. If the flow meter shows 10 gpm going in and the motor turns at 120 rpm, ηv is 0.63: the motor is worn (or the case drain will show it: over 10% of the inlet flow).

**Starting torque** is lower than running torque (50-70% for gear and gerotor motors, 80-90% for piston motors): a load that just moves at speed may not start; a motor that has to start under load is sized on its starting torque.

## Case drain, back-pressure and the shaft seal

- Piston motors and most orbital motors have a **case drain** (a port marked L, T1, or a small hose to tank) because their internal leakage collects in the case and their **shaft seal is rated for only 15-150 psi (1-10 bar)** depending on the type. The drain must go **straight to tank, unrestricted, not into the return line** (a return line carries back-pressure from filters and coolers: 50-150 psi, spikes to 300; that pressure sits on the shaft seal). A **blown shaft seal** (oil pouring from the shaft) is almost always a case pressure problem: a plugged, kinked, undersized or wrongly connected drain, a motor run with the return blocked, or a drain line frozen or filled with a return pulse.
- **Back-pressure** at the motor outlet reduces the ΔP (and so the torque) one-for-one, and on orbital motors without a drain (some small ones drain internally to the low-pressure port) it acts on the shaft seal: check the maker's limit (often 75-300 psi with a drain, less without).
- **Freewheeling**: a motor driven by its load (a fan coasting, a vehicle rolling) becomes a pump; if the inlet is blocked it cavitates and destroys itself, and if the outlet is blocked it stalls with a pressure spike. Motor circuits need a **motor spool** (both ports to tank at centre) or **cross-port reliefs with anti-cavitation checks**, and a **make-up** supply. A fan motor that screams when the valve centres is cavitating.
- **Case drain flow** as a wear test: same as pumps, at working pressure and speed; under about 5-10% of the inlet flow is healthy (the maker's number governs); a hot case is a leaking motor.
- **Shaft loads**: a sprocket or pulley overhung on a motor shaft not rated for side load kills the bearing in months; check the catalogue's radial load at the shaft position; use an outboard bearing.
- **Speed limits**: orbital motors have a maximum (the commutator valve's), and a minimum for smooth running (under about 10 rpm the leakage makes them jerky: cogging); a two-speed piston motor must not be shifted at full speed under load unless designed for it.

## Hydrostatic transmissions (closed loop)

![Closed-loop hydrostatic transmission: every valve in the loop](/img/hydraulics/hydrostatic-drive-loop.svg)

*Closed-loop hydrostatic transmission: every valve in the loop*

An **HST** connects a variable-displacement over-centre piston pump to one or more motors in a **closed loop**: the motor's return goes straight back to the pump inlet, not to tank. The pump's swashplate angle sets speed and direction (over centre = reverse), so there is no directional valve, no relief dumping to tank, and the machine has stepless speed, dynamic braking and reversing with one lever. Everything else in the circuit exists to keep the loop full, cool and protected:

| Component | Job | Typical value | Fault |
|---|---|---|---|
| **Charge pump** (a small gear or gerotor pump on the back of the main pump, 10-20% of main flow) | Replaces the loop's leakage (the pump's and the motor's case drain), keeps the low-pressure side full (no cavitation), supplies the **servo control** that moves the swashplate, releases the brakes, feeds the flushing valve | | Worn charge pump = low charge pressure = everything below |
| **Charge pressure** (measured at the charge gauge port with the loop in neutral and at full stroke under load) | The pressure of the low side of the loop | **200-350 psi (14-24 bar)** in neutral for most machines (Danfoss 90: 320-370; small mowers 60-150; check the manual), dropping no more than 10-15% under full load | **Low charge pressure**: no drive, weak, cavitation, sluggish response, brakes dragging; **the first reading in any hydrostatic fault** |
| **Charge relief** | Sets the charge pressure, dumping the excess into the pump case (to flush and cool it) | As above | Stuck open: low charge; stuck shut: high case pressure, blown seals |
| **Charge (suction) filter** and the **reservoir** | The charge pump's inlet from the tank (a 10 µm filter, often with a bypass and an indicator or a vacuum gauge) | Vacuum under 5-10 in Hg | A blinded charge filter starves the charge pump: low charge pressure hot, fine after a filter change: the classic |
| **Loop check valves (make-up checks)** | Let charge oil into whichever side of the loop is low | | Stuck or leaking: one direction weak or charge pressure falls in one direction only |
| **High-pressure (cross-port) reliefs** (often combined with the checks as **multi-function valves**) | Limit the loop pressure by passing oil from the high side to the low side (a short circuit, not to tank): protects against shock and stall, and **make heat fast** if held open | 4,000-6,500 psi (280-450 bar) | A stalled machine sits on the reliefs: the oil temperature climbs 10°F a minute; a relief that leaks = weak in that direction and hot |
| **Pressure limiter / pressure override** (on the pump control) | Destrokes the pump before the reliefs open: efficient stall | Set 200-500 psi below the reliefs | Set above the reliefs: heat at stall |
| **Bypass (tow) valve** | Opens the loop across so the machine can be pushed or towed with the engine dead | A screw or a lever on the pump or the multi-function valves | Left open: no drive; towing without it: the motors pump and cavitate |
| **Loop flushing (hot oil shuttle) valve** in the motor (or the pump) | A shuttle picks the low-pressure side and bleeds a set flow (1-3 gpm) through a small **flushing relief** (set slightly below the charge relief) into the motor case and back to the cooler: exchanges the hot loop oil for cool charge oil | Flushing relief about 20-40 psi below charge | Stuck shuttle: no flushing, the loop overheats; the flushing relief set above charge: same; set too low: it steals charge pressure |
| **Case drains** on the pump and motors | Back to the cooler and tank; the case pressure limit 40-70 psi | | A restricted drain: shaft seal blown, charge relief cannot dump |
| **Cooler** on the case drain and charge return | The only place heat leaves a closed loop | Oil under 180°F (80°C) at the case drain; the reservoir under 160°F | A fouled cooler on a hydrostatic machine shows first as loss of power hot |
| **Servo control / displacement control** (manual, hydraulic pilot, electric proportional, EDC) with a **neutral (centring) mechanism** | Moves the swashplate; springs return it to neutral | | Neutral out of adjustment: **creep** (the machine moves with the lever centred); a servo piston leaking: sluggish, drifts |
| **Displacement (stroke) limiters** | Set the maximum swashplate angle each way | | Screwed in: top speed lost |
| **Speed sensors, pressure sensors, EDC coils** | On electronic controls | | A failed sensor puts the control in limp mode |

Two-motor and multi-motor loops (skid steers: two pumps and two motors; combines: one pump, one motor; rollers: one pump, two wheel motors in parallel with a flow divider or an anti-spin valve) follow the same rules.

### The diagnostic sequence

![Hydrostatic drive unit on a compactor drum: the hoses are the loop, the small ones the case drain and charge](/photos/hydraulics/hydrostatic-transmission.jpg)

*Hydrostatic drive unit on a compactor drum: the hoses are the loop, the small ones the case drain and charge. Photo: Vivan755, CC BY-SA 3.0, via commons*

1. **Oil level, filter indicator, cooler condition, oil temperature, the tow valve position**, and whether anyone has adjusted anything.
2. **Charge pressure** at the charge gauge port: in neutral at low idle and at high idle (it should be at the manual's value, and steady); then with the machine driving against a load or stalled against a bank at full stroke (it should drop no more than about 10-15%). Low in neutral = the charge pump, the charge relief, the charge filter, the suction line, the level, or a leak somewhere the charge pump cannot keep up with (a pump case drain running high). Good in neutral but **collapsing under load** = the loop is leaking faster than the charge pump can make up: a worn pump or motor (go to step 4), a leaking multi-function valve or flushing valve, a stuck loop check.
3. **High pressure** at the loop gauge ports (one each side; system pressure gauges 0-6,000 psi): stall the machine gently against a solid object (brakes on) in forward and reverse: the pressure should reach the relief/limiter setting and hold. Low in one direction only = that side's relief or check; low both = the pump's limiter or a worn pump; reaches setting but the machine is weak = the motor or the brakes or the mechanical drive.
4. **Case drain flow** of the pump and the motor separately, at working pressure and temperature, into a measure (the case must remain full: keep the outlet high). More than about 10% of the rated flow (or the manual's number: for a Series 90 pump roughly 2-3 gpm at stall is the limit for the smaller frames) = worn. A motor case drain that rises with pressure is a worn motor; a pump whose charge pressure falls under load with a low motor drain is a worn pump.
5. **Neutral and creep**: with the wheels off the ground (or the machine chocked and the drive disconnected), engine at idle, lever centred, the loop gauges should read equal (both at charge pressure); if one side is higher the pump is off neutral: adjust per the manual (the neutral adjustment screw or eccentric on the control, with the linkage disconnected so you are adjusting the pump and not the linkage; then set the linkage). Creep that appears only hot = a servo piston or control valve leaking.
6. **Response and top speed**: slow to respond = low charge pressure, a servo control problem, air in the servo lines, an EDC coil or its current; low top speed = stroke limiters, the engine speed, the motor's displacement (a two-speed motor stuck in slow), a worn pump.
7. **Heat**: over 180°F at the case drain: the flushing valve, the cooler, the reliefs (a machine that works against its reliefs all day, e.g. a stalled auger), the oil viscosity, the charge relief dumping too much.
8. Write the numbers on the job card: charge in neutral, charge under load, high pressure each direction, case drain, temperatures.

### Symptoms

| Symptom | Likely | Test |
|---|---|---|
| No drive either direction, engine fine | Tow valve open, charge pressure zero (charge pump, coupling, a sheared key or spline between the engine and the pump, the charge filter), the control linkage disconnected, brakes not releasing (charge pressure) | Charge gauge |
| No drive in one direction | That side's multi-function valve (relief or check) stuck or leaking, a servo pilot line for that direction, the control valve | Loop gauges each direction |
| Weak, slow, gets worse hot | Worn pump or motor (case drain), low charge hot (filter, thin oil), the cooler | Case drain hot; charge under load |
| Creeps in neutral | Neutral adjustment, linkage, a servo leak, a control valve worn, a stuck shuttle in the flushing valve pushing the loop pressures apart | Loop gauges equal in neutral? |
| Jerky, surging, oscillating | Air in the servo lines or the loop (after a repair: bleed), low charge pressure, an EDC fault, a sticking control spool, a flushing valve hunting | Charge gauge needle steady? |
| Loses power at temperature, recovers cool | Charge filter blinding hot, the cooler, internal leakage rising with thin oil (worn parts), the wrong viscosity | Charge under load hot vs cold |
| Overheats | Flushing valve, cooler, relief operation, viscosity, a leaking multi-function valve circulating oil across the loop, the machine worked at stall | Case drain temperature; the flushing relief setting |
| Oil from the pump or motor shaft | Case pressure: drain restricted, charge relief dumping into a blocked case line, a return connected to the case | Case pressure gauge (should be under about 40 psi) |
| Noise: whine | Charge pump cavitating (filter, suction, level, cold thick oil) | Vacuum at the charge inlet |
| Noise: knock or growl under load | Pump or motor failing internally, a spline or dogbone worn | Case drain; metal in the filter |
| One wheel slips, the other stalls | The anti-spin / flow divider, or one motor worn (its case drain) | Compare motor case drains |
| Brakes drag, machine sluggish and hot | Brake release pressure (from charge) low, a brake valve, a brake stuck | Pressure at the brake port |

### Repair notes

- **Cleanliness**: a closed loop cannot filter its own oil (the loop oil only passes the filter through the flushing and case-drain path); ISO 18/16/13 or better; a failed pump or motor spreads metal through the loop, the cooler and the other unit: **flush the cooler and lines, change the filters, and inspect the other unit** (often replaced as a pair on small machines).
- **Start-up after a pump or motor change**: fill the cases through the top drain ports, fill the loop lines and the charge filter, bleed the servo lines, start at low idle with the machine on stands or chocked and the tow valve closed, check charge pressure within seconds (stop if it is not there in 10-15 seconds), run in neutral 5-10 minutes, then slowly stroke each way with no load, watch the charge pressure, then load gradually; check the neutral; change the filter after the first hours.
- **Adjustments** (neutral, charge relief, high-pressure reliefs, displacement limiters, pressure limiter, flushing relief) are all interdependent and all in the manual with a specified sequence; never turn a relief up to cure weakness.
- Small **integrated hydrostats** (mowers, garden tractors: Hydro-Gear, Tuff Torq) are sealed units with a shared oil sump and an internal filter or screen; they die of old oil, air, a slipping input pulley, and towing without the bypass; purge air after any oil change exactly per the maker (a lever-and-wheel procedure), or they will not drive.

## Common mistakes

- Motor case drain teed into the return line: shaft seal blown.
- A fan or vehicle motor on a spool that blocks its ports: cavitation on every stop.
- A hydrostatic fault chased for a day without reading the charge pressure.
- Turning up the high-pressure reliefs to "get more power": the loop cooks.
- Towing a hydrostatic machine without opening the bypass.
- Neutral adjusted at the linkage with the pump off neutral.
- A new pump fitted to a loop full of the old motor's metal.
- Air left in the servo lines after a repair, then a "control fault".
- A sprocket overhung on a motor shaft rated for no side load.

## Related

- [Hydraulic pumps: types, controls and testing](/article/hydraulic-pumps-types-controls-and-testing)
- [Pressure and flow control valves in depth](/article/pressure-and-flow-control-valves-in-depth)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Load-sensing, proportional and servo systems](/article/load-sensing-proportional-and-servo-systems)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
- [Hydraulic fluids: types and compatibility](/article/hydraulic-fluids-types-and-compatibility)
- [Pump and fluid-power formulas](/article/pump-and-fluid-power-formulas)
- [Hydraulic symbols (ISO 1219), complete](/article/hydraulic-symbols-iso-1219-complete)
