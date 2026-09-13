---
title: "Directional Control Valves: D03/D05/D07/D08 (CETOP 3/5/7/8, NG6/10/16/25) Sizes and Port Patterns, Spool Centre Conditions and What Each Does to the Machine, Solenoids (DC and AC, Coil Checks, Burnout, Manual Override), Two-Stage Pilot-Operated Valves and Their X and Y Ports, Silting and Stiction, Spool Leakage Testing and Valve Replacement"
slug: directional-control-valves-spools-and-solenoids
category: hydraulics
kind: reference
tags: [directional control valve, DCV, D03, D05, D07, D08, CETOP 3, CETOP 5, NG6, NG10, NG16, NG25, ISO 4401, subplate mounting, valve mounting pattern, spool center, closed center, open center, tandem center, float center, regenerative center, 4/3 valve, 4/2 valve, spool type, solenoid valve, wet armature solenoid, DC solenoid, AC solenoid, coil burnout, solenoid inrush, coil resistance, manual override, DIN 43650 connector, pilot operated directional valve, two stage valve, X port, Y port, pilot choke, internal pilot, external drain, spring centered, pressure centered, spool stiction, silting, valve leakage test, spool leakage, valve bolt torque, valve replacement]
source: "ISO 4401 and NFPA T3.5.1 (mounting surfaces D03-D10); Eaton Vickers, Parker and Bosch Rexroth directional valve catalogues and service data (flow ratings, spool types, solenoid data, pilot pressure limits, leakage figures); Fluid Power Society technician manuals (solenoid testing); Rexroth Hydraulic Trainer volume 1 (spool functions and two-stage valve operation)."
summary: "Everything about the valve that decides where the oil goes: the standard sizes and what flow each carries, how to read a mounting face, the centre conditions and the machine behaviour each one produces (pump loading, load holding, drift, regeneration), how solenoids work and fail and how to test a coil and a plug in a minute, how a two-stage valve is piloted and drained and what happens when the X or Y port is wrong, why spools stick and how to free and prevent it, how to test a valve for internal leakage, and how to change one so it does not leak or shift wrong."
---

## Naming a valve

A **4/3 valve** has four ports (P pressure, T tank, A and B to the actuator) and three positions; a **4/2** has two positions, a **3/2** three ports (single-acting cylinder, pilot signal), a **2/2** is a shut-off. The **spool** is the sliding piece inside; the **operator** shifts it (solenoid, lever, pilot pressure, cam, air); the **return** is a spring (spring-centred to the middle, spring-offset to one end) or a **detent** (stays where it was put). The schematic box for each position shows the flow paths; the ports are drawn on the box the valve sits in with no operator energised (the centre of a spring-centred 4/3). Basics are in [hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols).

![Directional valves: a sectional bank, a lever valve and a double-solenoid subplate valve with DIN plugs](/photos/hydraulics/solenoid-valve.jpg)

*Directional valves: a sectional bank, a lever valve and a double-solenoid subplate valve with DIN plugs. Photo: HAWE Hydraulik, CC BY-SA 4.0, via commons*

## Sizes and mounting patterns (ISO 4401 / NFPA)

![Subplate mounting patterns and flow capacity by size](/img/hydraulics/dcv-mounting-patterns.svg)

*Subplate mounting patterns and flow capacity by size*

| NFPA | CETOP | Rexroth NG | Port dia. | Typical rated flow | Bolts | Bolt torque (dry, grade 10.9 / 12.9) | Notes |
|---|---|---|---|---|---|---|---|
| **D03** | 3 | NG6 | 0.30" (7.5 mm) | **20 gpm** (75 L/min); direct solenoid | 4 × M5 (10-24 on some US) | 6-7 ft-lb (8-9 N·m) | The commonest industrial valve; stack (sandwich) valves fit under it |
| **D05** | 5 | NG10 | 0.44" (11 mm) | **30-40 gpm** (120-160 L/min); direct solenoid up to about 30 gpm, pilot-operated above | 4 × M6 | 11-13 ft-lb (15 N·m) | D05H (high flow) has a fifth bolt |
| **D07** | 7 | NG16 | 0.75" (19 mm) | **80 gpm** (300 L/min); always pilot-operated | 4 × M10 + 2 × M6 | 40-45 ft-lb (55-60 N·m) for M10 | X and Y ports appear in the pattern |
| **D08** | 8 | NG25 | 1.0" (25 mm) | **120-160 gpm** (450-650 L/min); pilot-operated | 6 × M12 | 70-80 ft-lb (100 N·m) | |
| D10 | 10 | NG32 | 1.25"-1.5" | 260 gpm (1,000 L/min) | 6 × M20 | 250 ft-lb | Presses, large machines; logic valves often replace these |

The pattern is the same across makers, so a Parker D03 valve fits a Rexroth NG6 subplate: check the **spool function, solenoid voltage and connector**, not just the face. Look at the face before fitting: the O-rings sit in the valve's face grooves (five for a D03: P, T, A, B and a blank, sometimes a sixth), the subplate face must be clean and unscratched, and the pattern has an **orientation** (the odd bolt hole or the port layout: A and B swapped puts the cylinder in reverse).

## Spool centre conditions

![Spool centre conditions: what each does to the pump and the load](/img/hydraulics/spool-center-conditions.svg)

*Spool centre conditions: what each does to the pump and the load*

The centre (de-energised) position decides what the machine does at rest, so it is the first thing to read when a machine drifts, overheats or will not hold.

| Centre | Symbol (P T A B) | Pump at rest | Load at rest | Where used | Watch for |
|---|---|---|---|---|---|
| **Closed** (all ports blocked) | P, T, A, B all blocked | Dead-headed: goes over the **relief** (heat) unless the pump is pressure-compensated or unloaded elsewhere | Held by the spool (but a spool always leaks a little: **slow drift** is normal, use a pilot-operated check or counterbalance for true holding) | Multiple valves in parallel off one compensated pump, accumulator circuits | Heat on a fixed pump; pressure trapped in the lines (thermal expansion can crack a gauge; a relief or a bleed path is needed) |
| **Open** (all ports to tank) | P, T, A, B connected | Unloaded: pump flow to tank at low pressure, cool | **Free to move**: a cylinder under a load drifts down; a motor freewheels | Single-valve circuits where the load is not held | Cannot run two valves in series or parallel; no load holding |
| **Tandem** (P to T, A and B blocked) | P-T, A and B blocked | Unloaded through the centre | Held by the spool (slow drift) | The classic single-pump, series-connected mobile valve and many machine circuits | Valves in **series**: the downstream valve is fed through the upstream one's tandem centre; back-pressure at T; cannot run functions at once |
| **Float** (P blocked, A and B to T) | P blocked, A-B-T | Dead-headed (relief or compensator) | Actuator **floats**: a blade follows the ground, a motor coasts to a stop without cavitating | Dozer blades, hydraulic motors (avoids cavitation on stopping), any function that must go limp | Pilot-operated checks needed if the load must also hold |
| **Regenerative** (P to A and B, T blocked) | P-A-B, T blocked | Pressure on both sides of the piston | The cylinder **extends fast** at reduced force (rod-side oil is added to the cap side); the force is only pressure × rod area | Rapid-advance on presses and cylinders | Never for a motor; the retract force is tiny |
| P blocked, A and B blocked, T open (open T) | | Dead-headed | Held | Some valve stacks | |
| **Partially open centres** (P-A-T with B blocked, A-T with P and B blocked, etc.) | | | | Special machine sequences, brakes, motor circuits | Read the box; the maker's spool code letter (Vickers 0, 1, 2, 3, 6, 7, 8, 9, 11, 33; Rexroth E, F, G, H, J, L, M, P, Q, R, U, V, W) is the only reliable name |

**Transient (crossover) conditions**: as the spool travels between positions it passes through an intermediate state that is either **open crossover** (all ports briefly connected: smooth, no pressure spike, but a load can drop a fraction) or **closed crossover** (all blocked: no drop, but a pressure spike and shock in a fast circuit). The maker's catalogue shows it as a dotted box between the positions. A valve replaced with the same centre but the other crossover can shake a press or let a load dip.

**Spool leakage** is inherent: a new D03 spool leaks about 0.5-5 in³/min (10-80 mL/min) per land at 1,000-3,000 psi, more when worn and hot. That is why a spool valve never holds a load overnight and a **poppet** or a pilot-operated check does. A cylinder that creeps 1/4 inch over an hour with a closed-centre spool is behaving normally; creeping inches in minutes is a worn spool or a bypassing piston.

## Solenoids

![Wet-armature solenoid: what to check with a meter](/img/hydraulics/solenoid-checks.svg)

*Wet-armature solenoid: what to check with a meter*

Modern valves use a **wet-armature (wet-pin) solenoid**: the armature and push pin run in oil inside a sealed tube, the coil slips over the tube and is held by a nut. The coil can be changed without opening the hydraulics. Older and some mobile valves have dry (air-gap) solenoids with a seal on the pin.

| | DC (12 V, 24 V the standard) | AC (110/120 V, 220/240 V) |
|---|---|---|
| Force and speed | Softer, slower shift (40-60 ms), no inrush | Strong pull-in, fast (15-25 ms); a large **inrush** current (3-5× holding) until the armature seats |
| Failure when the spool does not fully shift | The coil just runs warm at its normal current; the valve **half-shifts** | The inrush never falls: the coil **burns out** in minutes (a burned coil smell and a discoloured coil = the spool did not stroke: find out why before fitting the new coil) |
| Failure when energised with the spool blocked | Coil survives | Coil burns |
| Coil resistance (cold, a rough guide) | 24 V DC, 30 W: about **18-25 Ω**; 12 V DC: 4-6 Ω | 120 V AC: about 20-40 Ω DC resistance (the impedance in operation is much higher); 240 V: 80-150 Ω |
| Power | 20-40 W continuous | 40-70 VA inrush 150-300 VA |
| Extras | A **surge suppression diode** or varistor in the plug protects the PLC output; **LED plugs** show the coil is powered (a lit LED with no shift = hydraulic problem, not electrical) | Rectified-AC coils (a DC coil with a bridge in the plug) are common on newer valves: AC in, DC behaviour |

**Checks with a meter**: (1) voltage at the coil terminals while the PLC commands it: no voltage = wiring, fuse, output, interlock; (2) voltage present but low under load (a 24 V coil at 17 V from a long thin cable or a tired supply will not shift a spool against high flow forces; check the PLC card's own rating); (3) coil resistance with the plug off: open = burned; far below the rated value = shorted turns; compare with the twin coil on the same valve; (4) a **magnetic field tester** (a pocket screwdriver held to the coil nut, or a proper solenoid tester that lights up) shows the coil is magnetised; (5) the **manual override**: the pin in the end of the solenoid tube pushed in with a small tool shifts the spool by hand: **if the machine moves on the override but not on the solenoid, the fault is electrical; if it does not move on the override either, the fault is hydraulic (or the spool is stuck)**. Know what will move before you push it, and keep hands clear.

Connectors: the square **DIN 43650 form A** plug (three pins plus earth, a screw in the middle, a gasket that must be there or the coil corrodes), the smaller form B and C, Deutsch DT plugs on mobile equipment, and M12 on newer machines. A loose plug screw and a missing gasket cause more "intermittent valve" calls than the coils do.

## Two-stage pilot-operated valves

![Two-stage valve: pilot valve on top, X and Y ports, pilot choke](/img/hydraulics/pilot-operated-dcv.svg)

*Two-stage valve: pilot valve on top, X and Y ports, pilot choke*

Above about 30 gpm the flow forces are too high for a solenoid, so a small **pilot valve** (a D03 solenoid valve) sits on top of the **main stage** and uses hydraulic pressure to push the big spool. The pilot valve needs a **pilot supply** (X) and a **pilot drain** (Y):

- **Internal pilot**: the pilot supply comes from the main valve's own P port. Only works if P always has pressure: with an **open or tandem centre** the P pressure at rest is near zero, so the main spool cannot shift. Then a **back-pressure check (about 75 psi / 5 bar) in the T line** or an **external pilot** supply is used. The plug in the main body (a small screw plug or an orifice plug under the pilot valve) selects internal or external: the commonest mistake after a rebuild is the plug in the wrong hole.
- **External pilot** (X port on the mounting face or the body): a separate line from a constant pressure source (the pump outlet, a reducing valve at 150-300 psi, or a pilot pump); needed on open-centre systems and load-sense systems where P can be low.
- **Internal drain**: the pilot exhaust returns through the main valve's T port; any back-pressure in T (a return filter, a cooler, other valves) acts against the pilot and can prevent shifting or cause a slow shift. **External drain** (Y port) runs the pilot exhaust straight to tank, and is required when the T line carries back-pressure above about 100-150 psi or surges.
- **Minimum pilot pressure**: usually **50-150 psi (4-10 bar)**; maximum 3,000-4,500 psi (some need a reducing plate above about 3,000 psi). No pilot pressure = the main spool never moves however loud the solenoid clicks.
- **Pilot choke (throttle) plate** between the pilot and the main stage: two needle valves meter the pilot flow to slow the main spool's shift (soft starts and stops on a big cylinder). Meter-out is the usual type; they are also the first thing someone screws shut and "fixes" a fast machine into a dead one.
- **Spring-centred vs pressure-centred**: a pressure-centred main stage uses pilot pressure on both ends to hold centre; it needs pilot pressure even at rest, so the X supply matters.
- **Stroke limiters** (screws in the end caps) limit the main spool travel to meter flow; **spool position switches** or LVDTs report the position to the PLC.

When a two-stage valve will not shift: check the pilot solenoid (LED, override on the pilot valve), then the **pilot pressure at X** with a gauge, then the drain at Y (back-pressure), then the choke plate settings, then pull the pilot valve and look for a stuck main spool (push it with a brass drift, with the system locked out and bled).

## Silting, stiction and a stuck spool

A spool is a precision fit (0.0002-0.0004" / 5-10 µm clearance). Fine particles pack into the clearance (**silting**) when the spool sits still under pressure, and the spool needs more force to break away than the solenoid has. Symptoms: a valve that works after the machine has been cycling but sticks on the first shift of the morning, or sticks in one direction, or shifts only with the override. Causes: dirty oil (a valve is a filter for particles about the size of its clearance), **varnish** from hot or oxidised oil (a brown lacquer in the bore, worst on servo and proportional valves), a burr from a pressure spike, a bent spool from over-torqued mounting bolts on an uneven subplate, thermal lock (a hot spool in a cold body), or a coil too weak (low voltage).

Freeing one: lock out and bleed, remove the coil and solenoid tube, push the spool through with a brass or plastic drift and feel for the tight spot; clean the spool and bore with solvent and lint-free wipes (never abrasives, never a wire brush; a fingernail catches a burr), lubricate with clean oil, refit. **Lapping** a spool is a specialist job. Prevention: cleanliness (ISO 18/16/13 or better for solenoid valves, 16/14/11 for proportional), oil below 140°F, a **dither** or periodic cycling on valves that sit for months, and correct bolt torque on a flat subplate.

## Testing a valve for internal leakage

1. Lock out; block the A and B ports (or disconnect the cylinder lines and cap them with rated caps), pressurise P with the spool centred, and measure the flow from T with a measuring cylinder over a minute at working pressure and temperature: compare with the maker's leakage figure (a D03: typically under 10 in³/min / 150 mL/min total at 3,000 psi; a D05 up to 20-30 in³/min). Much more = worn spool or body.
2. In place: with a load held on a closed-centre spool and the pump running, feel the T line and the A/B lines for temperature (a leaking land warms the T line); watch the cylinder drift rate with the pilot-operated checks (if any) bypassed.
3. Swap test: exchange the valve with an identical one from a working function; if the fault moves, the valve is the fault.

## Replacing a valve

1. Lockout, bleed to zero at the gauge, block or lower loads; note the **orientation** (photograph it), the plug positions and the solenoid wiring (A solenoid, B solenoid: the solenoid at the A end usually connects P to **B** on a spring-centred spool, but conventions differ: check the schematic).
2. Remove the bolts in a cross pattern; lift the valve straight up; catch the oil; cover the subplate face at once (a clean cap or clean lint-free cloth).
3. Clean the subplate face; inspect for scratches across a port land (a scratch = a leak: lap or replace the plate); check that all O-rings came off with the old valve (an O-ring left behind doubles up and splits).
4. New valve: verify model code, spool, voltage, connector; fit **new O-rings** (in the valve's grooves, a smear of clean oil, never grease that traps dirt); check the internal/external pilot and drain plugs on a two-stage valve against the schematic.
5. Set it down square, bolts finger-tight in a cross pattern, torque in two stages to the table; over-torque distorts the body and binds the spool; under-torque blows the O-rings out at pressure.
6. Reconnect plugs (gaskets in, screws tight, cable strain relieved); restore pressure slowly; check for shift (the LED and the machine), leaks, and the sequence; re-check the bolt torque after the first warm cycle.

## Common mistakes

- Fitting a new coil to a valve with a stuck spool: the second coil burns too (AC).
- Reversing the A and B lines or the valve orientation so the machine runs backwards on the first cycle.
- A two-stage valve replaced with the pilot plug in the internal position on an open-centre system: it never shifts.
- Screwing the pilot choke shut to "fix" a shock, then the valve will not shift at all.
- Tightening the four bolts with an impact gun: bent body, sticking spool.
- Assuming a lit LED means the valve shifted.
- Grease on the O-rings, which then holds every particle that passes.
- Expecting a spool valve to hold a load: it never will.

## Related

- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
- [Stack valves and sectional valve banks](/article/stack-valves-and-sectional-valve-banks)
- [Cartridge and logic valves](/article/cartridge-and-logic-valves)
- [Pressure and flow control valves in depth](/article/pressure-and-flow-control-valves-in-depth)
- [Load-sensing, proportional and servo systems](/article/load-sensing-proportional-and-servo-systems)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
