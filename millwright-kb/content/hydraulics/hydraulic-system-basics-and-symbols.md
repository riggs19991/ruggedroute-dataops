---
title: "Hydraulic System Basics and Schematic Symbols: Pressure, Flow and Power Rules, the Components (Pumps, Valves, Actuators, Reservoir, Filters, Accumulators), Reading an ISO 1219 Schematic Symbol by Symbol, Directional Valve Notation, Pilot and Drain Lines, Pressure Settings and the Order to Adjust Them, Basic Troubleshooting Logic and Injection-Injury Safety"
slug: hydraulic-system-basics-and-symbols
category: hydraulics
kind: reference
tags: [hydraulics basics, hydraulic schematic, hydraulic symbols, ISO 1219, reading hydraulic drawings, directional control valve, 4/3 valve, spool valve, relief valve, pressure reducing valve, sequence valve, counterbalance valve, check valve, pilot operated check, flow control, pressure compensated, gear pump, vane pump, piston pump, variable displacement, hydraulic cylinder, hydraulic motor, reservoir, hydraulic filter, accumulator symbol, pilot line, drain line, hydraulic pressure flow horsepower, relief valve setting, injection injury, hydraulic safety]
source: "ISO 1219-1 (fluid power symbols) and ISO 1219-2 (circuit diagrams); Parker, Eaton Vickers and Bosch Rexroth industrial hydraulics training manuals (component function and adjustment order); Fluid Power Safety Institute (injection injury and lockout of hydraulic energy); NFPA/T2 fluid power standards."
summary: "The working knowledge a millwright needs before touching a hydraulic system: the pressure, flow and power relationships, what each component does and how it fails, how to read every symbol on the schematic including the spool boxes and pilot lines, which pressure valves are set in which order, the logic for tracing a problem from the schematic to the machine, and the hard rules about stored energy and pinhole leaks."
---

## The rules

```
   Force (lb) = pressure (psi) × area (in²)              pressure is caused by resistance to flow, not by the pump
   Flow (gpm) makes speed: cylinder speed (in/min) = 231 × gpm ÷ area (in²)
   Hydraulic hp = gpm × psi ÷ 1714                        (÷ 1714 ÷ efficiency for the motor hp: about 0.85)
   Heat: every psi dropped across a valve or a relief with no work done turns into heat: 1 hp = 2,545 BTU/h
   Pascal: pressure acts equally in all directions; the load sets the pressure; the relief valve sets the ceiling
```

Full formulas (cylinder force, motor torque, pump displacement) in [pump and fluid-power formulas](/article/pump-and-fluid-power-formulas). A system that runs **hot (over 140°F / 60°C)** is wasting power somewhere: a relief valve dumping, a leaking cylinder, a pump compensator set above the relief, an undersized cooler.

## Components

| Component | What it does | Field notes |
|---|---|---|
| **Reservoir** | Holds, cools, deaerates, settles the oil; the breather and the level | Level checked with all cylinders **retracted** (or per the machine); the breather is a **filter** (replace it; a desiccant breather in damp plants); the suction strainer (100-mesh) inside; the baffle separates return from suction |
| **Pump** (gear: fixed, cheap, noisy, tolerant; vane: quieter, medium pressure; **piston**: high pressure, variable displacement, sensitive to contamination) | Makes flow | A pump does not make pressure; a worn pump makes less flow **at pressure** (case drain flow rises: over 10% of the pump's flow to the case drain = worn); cavitation from a restricted suction (a whine, foam) kills it in hours |
| **Relief valve** | Limits the maximum system pressure, dumping to tank | The system's fuse; set 10-15% above the working pressure and **above** the compensator on a pressure-compensated pump (or it dumps continuously and heats the oil); direct-acting for small flows, pilot-operated (with a vent port for remote/unloading) for the main relief |
| **Pressure-reducing valve** | Limits the pressure **downstream** of it (a branch at a lower pressure) | The only pressure valve that is normally **open**; has a drain |
| **Sequence valve** | Lets flow pass to a second circuit only when the pressure reaches its setting | External drain; a clamp-then-drill circuit |
| **Counterbalance (load-holding) valve** | Holds a load against gravity; opens on pilot pressure from the other line | On lifting cylinders and hydraulic motors on slopes; set 1.3× the load-induced pressure; **do not remove it to "fix" a slow lower**: the load will fall |
| **Unloading valve** | Dumps a pump to tank at low pressure when an accumulator or a high-pressure pump takes over | Hi-lo circuits |
| **Directional control valve (DCV)** | Routes flow: 4/3 (four ports, three positions), 4/2, 3/2, 2/2; spool centre conditions: **closed, open, tandem, float**; operated by lever, solenoid (DC/AC), pilot, cam, spring return, detent | The **spool centre condition** tells you what happens when the valve is de-energised: a **tandem centre** unloads the pump and locks the cylinder; an **open centre** lets the load drift; a **closed centre** blocks everything and the relief takes the flow (heat) unless the pump is compensated; **float** connects A and B to tank |
| **Check valve** | Flow one way | With a cracking-pressure spring; **pilot-operated check** (POC) locks a cylinder until pilot pressure opens it: on load-holding and locking circuits |
| **Flow control** | Meters flow: needle valve (not compensated: flow changes with pressure), **pressure-compensated** flow control (constant flow), with a bypass check for free flow the other way | **Meter-in** (into the actuator: pulling loads, precise), **meter-out** (out of the actuator: overrunning loads, the usual for cylinders), **bleed-off** (to tank, efficient); adjusting a flow control changes the speed, never the force |
| **Cylinder** | Linear actuator: single-acting (spring/gravity return), double-acting, differential (the rod side has less area: faster retract, less force), telescopic; **cushions** at the ends | Rod seals and wipers, piston seals (an internally bypassing piston: the cylinder drifts and the oil heats); see [cylinder repair](/article/cylinder-repair-and-seal-kits) |
| **Hydraulic motor** | Rotary actuator: gear, vane, piston (axial, radial); torque ∝ pressure × displacement | Needs a case drain (piston motors) and a load-holding valve on a hanging load; starting torque is less than running |
| **Accumulator** | Stores pressure (energy), absorbs shock, makes up leakage | Gas precharge with **nitrogen only**; see [accumulator precharge](/article/accumulator-precharge-and-safety); a bleed-down valve must be in the circuit |
| **Filters** | Pressure filter (protects a valve), return filter (catches wear debris), off-line (kidney loop), suction strainer | ΔP indicators; bypass valves; see [filters and contamination](/article/filters-fluid-and-contamination) |
| **Heat exchanger** | Air or water cooled | A dirty cooler = a hot system |
| **Gauges and test points** | Diagnostic connections (Minimess/Stauff) | Read the pressure **at the actuator**, not just at the pump |
| Pressure switch / transducer, temperature switch, level switch | Machine interlocks | |

## Reading the schematic (ISO 1219)

![The basic ISO 1219 schematic symbols](/img/hydraulics/schematic-symbols.svg)

*The basic ISO 1219 schematic symbols*

- **Lines**: solid = main working line; **dashed** = pilot (control) or drain line; double = mechanical connection; a dot at a junction = connected; lines crossing without a dot = not connected; an enclosure (dash-dot rectangle) = a manifold or a valve assembly.
- **Circles**: a circle with a **solid triangle pointing outward** = a **pump** (the triangle is the flow direction); pointing inward = a **motor**; two triangles = bidirectional; an **arrow through** the circle = variable displacement; a small dashed box with an arrow next to it = pressure-compensated; a hollow triangle = pneumatic.
- **Reservoir**: an open-top box (vented) or a closed box (pressurised); the line ending **below** the oil level = submerged return.
- **Squares (envelopes)**: valves. A directional valve is drawn as **one square per position** (a 4/3 has three); the arrows inside show the flow paths in each position; the ports (P pressure, T tank, A and B work) are drawn on the envelope that is active **at rest** (the centre position of a spring-centred 4/3); imagine sliding the boxes across the ports to see the other positions. Operators are drawn at the ends: a lever, a solenoid (a rectangle with a diagonal), a spring (zigzag), a pilot (dashed line to a small triangle), a detent (notches).
- **Pressure valves** are a single square with an arrow offset from the flow line and a **spring** with an adjustable arrow; the **pilot dashed line** shows what pressure operates it: from the **inlet** (relief, sequence, counterbalance from the other line) or from the **outlet** (pressure-reducing). A relief's outlet goes to tank; a reducing valve's outlet goes to the circuit.
- **Check valve**: a ball on a seat (a circle in a V); with a spring = cracking pressure; with a pilot line = pilot-operated.
- **Flow control**: a restriction (two curves like a narrowing) with an arrow across = adjustable; with a dashed pressure box = compensated; with a check in parallel = one-way.
- **Cylinder**: a rectangle with a piston and rod; a double-acting has ports at both ends; cushions are small boxes at the piston; a rectangular "T" on the rod end = a spring return.
- **Filter**: a square on its corner with a dashed line across; with a bypass check = filter with bypass; with an indicator = ΔP indicator.
- **Accumulator**: a tall rounded rectangle; a gas symbol (triangle) at the top = gas-charged.
- **Cooler**: a diamond with arrows; a heater with an arrow inward.
- Every valve's **setting** is written beside it on a good schematic (e.g. RV1 2,000 psi; SEQ 900 psi); the sequence of the machine's operation is often on the sheet as a table of which solenoids are energised for each step: **that table is the fault-finding tool**.

## Pressure settings and the order to set them

1. **Main relief** first, with everything else backed off: set it to the design pressure (with a gauge on the pump outlet, the actuators dead-headed or blocked; turn the adjuster in slowly while reading; **lock** it).
2. **Pump compensator** (pressure-compensated piston pump): set **below** the relief by 150-300 psi (the relief becomes a safety valve; the pump destrokes at the compensator pressure and makes no heat).
3. **Reducing valves** in the branches.
4. **Sequence, counterbalance and unloading** valves as the circuit requires (counterbalance: the load-induced pressure × 1.3; sequence: above the pressure needed by the first operation).
5. **Flow controls** for speed; **cushions** at the ends of stroke.
6. Record every setting on the schematic and the machine's log; never adjust a valve without a gauge and without knowing what it does.

## Troubleshooting logic

1. **What is the machine doing wrong?** (No motion, slow, weak, drifts, erratic, hot, noisy, leaking.) Which actuators, which step of the sequence.
2. **Electrical or hydraulic?** Is the solenoid energised at that step (the light, a test lamp, the PLC output; a solenoid that is energised but not shifting the spool: sticking from contamination or a burned coil; manual override pin on the valve shifts it by hand).
3. **Pressure at the point of work**: gauges at the pump outlet and at the actuator (test points): pump pressure good but the actuator low = a restriction or an internal leak between; pump pressure low = the pump, the relief, the compensator, or a valve dumping to tank.
4. **Flow**: a flow meter, or the cylinder's speed against the calculation; low flow at pressure = a worn pump (case drain check), a relief partly open, a bypassing cylinder.
5. **Temperature**: feel (carefully) or IR-gun the components: the **hot one is the one passing oil across a pressure drop**: a relief that is hot is dumping; a cylinder hot at the piston is bypassing; a hot tank is the sum.
6. **Noise**: pump whine/rattle = cavitation or aeration (the suction, the level, the breather, a suction leak); a relief chattering = set too close to the compensator or damaged; a valve hammering = an unstable counterbalance.
7. Fix the cause, then the symptom: a slow cylinder from a worn pump is not fixed by opening the flow control.

| Symptom | Likely causes |
|---|---|
| No pressure / no motion | Pump not turning or rotation wrong (new pump: check!), coupling, suction closed, relief stuck open or set to zero, DCV not shifting, a broken line |
| Low pressure | Relief set low or worn, compensator low, internal leaks (cylinder piston, valve spool, motor), worn pump |
| Slow | Low flow: worn pump, flow control, viscosity (cold oil), a restriction, a bypassing actuator, relief cracking early |
| Weak but fast at no load | Pressure limited: relief, reducing valve, a bypass at load |
| **Drift** (cylinder creeps under load) | Piston seals, a POC or counterbalance leaking, the DCV spool leakage with an open-centre spool (normal drift), the rod seal (external) |
| Erratic, jerky | Air in the oil (aeration: foam in the tank, a suction leak), a sticking spool, cushions, stick-slip from a worn cylinder |
| **Overheating** | Relief dumping (compensator above relief, relief set low, a stuck valve), internal leakage, a dirty cooler, low oil level, high ambient, wrong viscosity, a closed-centre spool with a fixed pump |
| Noisy pump | Cavitation (suction filter, viscosity, level, a collapsed suction hose), aeration (a leaking suction fitting, a low level, a return line above the oil), worn pump, misalignment |
| Foaming oil | Aeration, wrong oil, water |
| Milky oil | Water: a leaking cooler, condensation, a bad breather |

## Safety

- **Injection injury**: a pinhole leak at 2,000 psi cuts through skin painlessly and injects oil into the tissue: it looks like a small puncture and becomes amputation within hours unless surgeons debride it. **Never feel for a leak with your hand**; use cardboard or a mirror; **never tighten a fitting under pressure**; if injected, go to hospital **immediately** with the fluid's SDS, whatever it looks like.
- **Stored energy**: pressure remains after the pump stops: in accumulators, in loaded cylinders (a raised load, a clamped part, a spring), in lines blocked by check valves and POCs. Lockout is the electrical isolation **plus** bleeding the pressure to zero at every gauge, blocking or lowering every load, and discharging the accumulators (the bleed valve), then proving zero on the gauge; the [lockout basics](/article/lockout-tagout-basics) article has the sequence.
- **Hoses** whip and burst: inspect, route, and replace by age; never stand in line with a fitting being loosened.
- Hot oil (140-180°F) and hot components; oil on the floor; fire (mineral oil mist at 2,000 psi is a flame-thrower near a hot surface).
- Never operate the manual override on a valve unless you know what will move and everyone is clear.

## Related

- [Hydraulic hose assembly and fittings](/article/hydraulic-hose-assembly-and-fittings)
- [Cylinder repair and seal kits](/article/cylinder-repair-and-seal-kits)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
- [Accumulator precharge and safety](/article/accumulator-precharge-and-safety)
- [Pump and fluid-power formulas](/article/pump-and-fluid-power-formulas)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
