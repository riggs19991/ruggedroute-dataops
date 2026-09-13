---
title: "Stack (Sandwich) Valves and Sectional Valve Banks: What Each Modular Valve Does and Which Port It Acts On, the Order of a D03/D05 Stack and Why It Matters, Tie-Rod Length and Torque, Reading a Stack from the Schematic, Fault-Finding by Module Swap, and Mobile Sectional and Monoblock Valves (Inlet, Work Sections, Port Reliefs, Anti-Cavitation Checks, Power Beyond, Load-Sense Shuttles)"
slug: stack-valves-and-sectional-valve-banks
category: hydraulics
kind: reference
tags: [stack valve, sandwich valve, modular valve, D03 stack, D05 stack, NG6 modular, sandwich flow control, sandwich check valve, sandwich counterbalance, sandwich reducing valve, sandwich pilot operated check, stack order, tie rod length, tie rod torque, manifold subplate, bar manifold, section O-rings, valve stack leak, sectional valve, sectional control valve, monoblock valve, mobile directional valve, inlet section, work section, outlet section, port relief, anti-cavitation check, power beyond, load check, load sense shuttle, valve bank tie rod, spool types mobile valve, open center valve bank, closed center valve bank]
source: "Parker, Eaton Vickers, Bosch Rexroth, Daikin and Continental Hydraulics modular (sandwich) valve catalogues (functions, stack heights, bolt kits, torque); Danfoss PVG, Parker P70/VDP, Walvoil SD, Prince and Gresen sectional valve service manuals (section functions, tie-rod torque, spool options, relief settings); Fluid Power Society technician manuals; Rexroth Hydraulic Trainer volume 1."
summary: "How to read, service and fault-find the two commonest ways of packaging several valves in one assembly: the industrial stack of sandwich valves under a D03 or D05 directional valve (which module does what, to which port, in what order, with what bolts) and the mobile sectional valve bank (inlet, work sections, outlet, the reliefs and checks hidden in each section, the load-sense and power-beyond connections), with the leak, drift and no-flow faults each one produces."
---

## Industrial stack (sandwich) valves

![A D03 stack from the manifold up: each module acts on named ports](/img/hydraulics/stack-valve-order.svg)

*A D03 stack from the manifold up: each module acts on named ports*

A **stack** is a directional control valve (DCV) mounted on top of one or more **sandwich (modular) valves**, all with the same ISO 4401 face pattern (D03 or D05; D07 sandwiches exist but are rare), bolted through with long **tie rods (stud bolts)** to a **subplate** or a **bar manifold** that carries P, T, A and B for each station. Each sandwich passes P, T, A and B straight through and performs one function on one or two of them. The whole stack is one station; a bar manifold carries four or six stations side by side sharing P and T.

### What each module does and which port it acts on

| Sandwich module | Acts on | Function | Adjust / notes |
|---|---|---|---|
| **Check valve, P line** | P | Stops the load driving oil back into the pump line when the pump unloads or another function drops the pressure; **load check** | Cracking 5-75 psi; none adjustable |
| **Check, A or B, or T line** | A, B or T | One-way flow; a T-line check makes **back-pressure** (about 75 psi) to supply an internal pilot | |
| **Pilot-operated check (POC)** | A, B or both | **Locks the cylinder** leak-free until pilot pressure from the opposite line opens it; the true load-holding module | Pilot ratio typically 3:1-4:1; needs a spool centre that vents A and B to tank (float or an open-centre spool: a closed centre traps pressure and the POC will not open, or opens with a bang) |
| **Flow control, meter-in** | A, B or both (marked by arrows on the body) | Sets the speed **into** the actuator; for resistive loads | Needle (not compensated) or pressure-compensated; each side its own screw |
| **Flow control, meter-out** | A, B or both | Sets the speed **out** of the actuator; the usual choice for cylinders and over-running loads | The commonest sandwich; the arrow on the body shows the metered direction; a free-flow check the other way |
| **Flow control, P line** | P | Meters total flow to the station (both directions equally) | |
| **Pressure-reducing valve** | P (or A or B) | A lower pressure for this station only (a clamp at 500 psi off a 2,000 psi system) | Has a drain: external through T or a separate port; the reducing valve is normally **open** |
| **Pressure relief, A or B (port relief, cross-port relief)** | A, B | Limits the pressure in one work line (shock from a motor stopping, an over-running load); cross-port dumps A to B | Set above the working pressure of that line |
| **Sequence valve** | A or B | Allows the second stage of a sequence to move only when the first has stalled at pressure | External drain |
| **Counterbalance (load-holding with pilot assist)** | A or B (the line from the load side of the cylinder) | Holds a load against gravity **and** controls the lowering speed without cavitation; opens on pilot pressure from the other line | Set 1.3× load-induced pressure; pilot ratio decides stability: see [pressure and flow control valves](/article/pressure-and-flow-control-valves-in-depth) |
| **Pressure switch plate / gauge plate** | P, A or B | A gauge port or a pressure switch for the PLC | |
| **Blanking plate** | | Fills the space of a removed module | |
| **Sandwich accumulator / shock module** | P or A/B | | |
| **Orifice plate** | P, A, B or T | A fixed restriction (a slow-down, a pilot orifice) | Not adjustable; easily forgotten in a rebuild |

Each module is stamped with the port it acts on (an arrow and A, B, P or T) and often has a letter code on the plate; **the same body machined for A or B looks identical from the outside**, so read the stamping, not the shape. The direction arrow on a flow control is the metered direction of flow, not the actuator's direction.

### The order of the stack

Order matters because each module sees only what the modules below it pass up. Reading from the **subplate up to the DCV**, a common, correct order is:

![Power pack with double-solenoid valves stacked on modular sandwiches over a bar manifold](/photos/hydraulics/valve-stack.jpg)

*Power pack with double-solenoid valves stacked on modular sandwiches over a bar manifold. Photo: Vedantengg, CC BY-SA 3.0, via commons*

1. **Pressure-reducing valve** (P) at the bottom, so everything above it sees the reduced pressure, and its drain goes straight to the subplate T.
2. **Check valve in P** (load check) above it.
3. **Counterbalance or pilot-operated check** (A/B) next: closest to the actuator lines in the manifold, so what it holds is the actual load, not a flow control's back-pressure.
4. **Flow controls** (meter-out A/B) above that, so the flow control meters the flow the DCV commands and the POC below still sees full pilot pressure.
5. **Pressure switch or gauge plate** wherever it must read.
6. **Directional valve** on top.

Put the flow control **below** the POC and the pilot pressure to open the POC is throttled: the load lowers in jerks. Put the reducing valve **above** a POC and the pilot signal is at reduced pressure and may not open the check. The machine schematic shows the order as a column of symbols; when in doubt, draw the flow path for each spool position through each module and see what each one does to the port it acts on.

### Tie rods, torque and seals

- The **tie-rod kit** length is set by the number and height of modules: a D03 DCV is about 1.8" (46 mm) tall, each D03 sandwich 1.6" (40 mm); the maker's catalogue lists the bolt kit for one, two, three modules. A rod too short engages three threads and strips; too long bottoms out in a blind manifold hole and the stack is never clamped (it leaks at pressure and the spool binds). Threads engaged: at least 1× the diameter.
- Torque **in a cross pattern in two or three stages**: D03 (M5): 6-7 ft-lb (8-9 N·m); D05 (M6): 11-13 ft-lb (15 N·m); D07 (M10): 40-45 ft-lb (55-60 N·m). Uneven torque bows the stack: a sticking spool in the DCV on top is often a bent stack, not a dirty spool.
- **O-rings**: five (or four) on every face, in the groove of the module above, all replaced together; a stack leaks between modules when one O-ring is missing, pinched, cut on a sharp port edge, swollen by the wrong fluid or nicked by a face scratch. The face must be **flat and unmarked**: a scratch across a port land is a leak path at 3,000 psi.
- A **stack that leaks externally** at pressure only: bolts stretched or under-torqued, or a rod bottomed. Leaks all the time: a damaged O-ring or face.

### Reading and fault-finding a stack

- Identify each module from its **plate code and stamping**, write the stack down top to bottom against the schematic, and note every adjusting screw and its lock nut position (mark them with paint before touching).
- **Drift** at a station with a POC: the POC seat (a particle, a scored poppet), the wrong spool centre (closed centre keeps the pilot pressurised: the check opens and the load drifts), the POC fitted on the wrong port, or a bypassing cylinder (test the cylinder first: [cylinder repair](/article/cylinder-repair-and-seal-kits)).
- **Slow in one direction only**: the meter-out screw on that side, a blocked check in the flow control, the counterbalance set too high or its pilot too weak.
- **Will not move in one direction, moves in the other**: a POC that will not open (pilot pressure too low: a reducing valve above it, a flow control throttling the pilot, a ratio too low for a very high load pressure), a port relief stuck open, a stuck sandwich check.
- **No flow at all, pump at relief**: a load check backwards, an orifice plate blocked, a reducing valve set to zero or its drain blocked (a reducing valve with no drain path stays shut).
- **Overheats at rest**: a reducing valve's relief function dumping, a cross-port relief set too low, a POC held open.
- **Module swap**: sandwiches are cheap and identical between stations: swap the suspect module with the same module from a working station (same port marking!) and see whether the fault moves. Clean the faces, new O-rings, correct torque; each swap is a chance to introduce dirt.
- After any change, re-set the pressure modules with a gauge on the gauge plate and record the settings on the schematic.

## Mobile sectional and monoblock valves

![Sectional valve bank: inlet, work sections, outlet and the LS line](/img/hydraulics/sectional-valve-bank.svg)

*Sectional valve bank: inlet, work sections, outlet and the LS line*

The valve on a loader, crane, excavator or forestry machine is a bank of **work sections** (one spool per function) between an **inlet section** and an **outlet (end) section**, clamped by three or four **tie rods**. A **monoblock** is the same thing cast in one body (cheaper, no inter-section leaks, not expandable). Each section is a small hydraulic circuit on its own.

| Part | What is in it | Typical settings and faults |
|---|---|---|
| **Inlet section** | The **main relief** (the whole valve's maximum), the P and T ports, on load-sense valves the **LS relief** and the **unloader/pressure compensator** for a fixed pump, on some a **priority** valve for steering | Main relief 2,000-3,500 psi (140-240 bar) on typical mobile machines; a main relief stuck partly open: everything weak and the tank hot |
| **Work section** | The **spool** (open-centre, closed-centre, motor spool, float spool, regenerative), a **load check** (stops the load falling back when the spool opens before the pressure builds), **port reliefs** on A and/or B (limit the pressure trapped in a cylinder or motor line when the spool is centred: shock, boom hitting the stop), **anti-cavitation (make-up) checks** (let oil from T into a work port when the load runs faster than the pump feeds it, e.g. a boom dropping, a motor coasting), on LS valves a **pressure compensator** and an **LS shuttle**, spool centring spring and detent, spool seals and wipers, a lever or a pilot/solenoid actuator | Port reliefs usually 10-20% **above** the main relief on holding functions (so the main relief governs while working and the port relief only catches shock); a port relief set below the main relief makes that function weak in one direction only; an anti-cav check stuck open = that port bleeds to tank and the load drifts |
| **Outlet section** | T port, sometimes a **power-beyond** sleeve (carries the unused open-centre flow on to another valve downstream rather than to tank: a separate high-pressure port), an LS return or bleed orifice | Power beyond plug fitted in place of the sleeve (or the reverse): the downstream valve gets nothing, or the T port sees full pressure and the section seals blow |
| **Tie rods** | Three or four long studs | Torque per the maker (typically 15-25 ft-lb for 3/8" rods on small valves, 40-60 ft-lb for 1/2" and M12, up to 100+ ft-lb on large valves), cross pattern, in stages, with the valve on a flat surface and the sections aligned on their dowels; **over-torque bows the sections and the spools stick**; under-torque = leaks between sections at pressure and a valve that "creeps" all functions |

**Open-centre banks** (fixed pump): flow passes through the centre of every spool in series to tank; moving a spool blocks the centre path progressively and diverts flow to the work port; the pressure is whatever the load needs; the functions interact (the highest-load function starves when another moves first, the order of sections matters: usually the most important function nearest the inlet). **Closed-centre banks** (pressure-compensated or LS pumps): the centre is blocked; each section gets flow on demand; LS valves add a compensator per section so several functions share flow in proportion (**flow sharing**, e.g. Danfoss PVG, Rexroth M4). See [load-sensing systems](/article/load-sensing-proportional-and-servo-systems).

### Spool types in a section

![Mobile sectional valve bank with hand levers: one work section per function between the inlet and outlet](/photos/hydraulics/valve-bank.jpg)

*Mobile sectional valve bank with hand levers: one work section per function between the inlet and outlet. Photo: Kleuske, CC BY-SA 3.0, via commons*

| Spool | Centre | Use |
|---|---|---|
| **Double-acting cylinder** (4-way, A and B blocked at centre) | Holds both ports | Most cylinders |
| **Motor spool** (A and B to T at centre, or via checks) | Motor can coast, no cavitation, no trapped pressure | Hydraulic motors, winches with a separate brake |
| **Float** (fourth position, A and B to T) | Blade follows the ground | Dozer blades, snow plough |
| **Single-acting** (3-way, only A used) | | Dump bodies, single-acting rams |
| **Regenerative** | P to A and B for fast extend | Log splitters, clam shells |
| **Detented spool** | Stays in position | Motor functions, augers; a detent that releases on pressure (kick-out) for bucket return-to-dig |

### Identifying and servicing a section

- The casting number and the spool code are stamped on the section and on the spool end; the assembly drawing lists them by position. Sections of the same family but different spool codes look identical: order by the code, and write the position on each section before splitting a bank.
- **Splitting a bank**: clean it outside, mark the order and orientation of every section, lay them out on a clean bench in order as the tie rods come out, keep the O-rings and the load-check poppets and springs with their sections (they fall out), inspect the faces for scoring, replace **every** inter-section O-ring (a kit), lubricate, align on the dowels, torque the rods in stages, then set the reliefs.
- **Spool seals** (the O-ring and wiper at each spool end) are the commonest leak: replaceable in place with the spool cap off; a **bent spool** or a scored bore leaks at the seal forever: replace the section.
- **Port relief and anti-cav cartridges** screw into the section: identify by the stamping; a relief cartridge dropped into an anti-cav cavity (or the reverse) bolts in and does something else entirely.
- **Setting port reliefs**: gauge on the work port, spool held with the cylinder stalled (or a gauge and a needle valve on a test port), turn the adjuster; record; lock. A port relief that opens **below** the main relief makes the machine weak in that direction only: a classic hard-to-find fault.
- **Section leak diagnosis**: oil weeping between sections at pressure = tie rods; from a spool end = spool seals; all functions weak and hot with a good pump = main relief; one function weak one way = port relief or a load check; one function drifting = the anti-cav check, the port relief seat, a bypassing cylinder, or the load check seat; all functions drift together = spool wear from contamination (the whole valve).

## Common mistakes

- Meter-out sandwich under the POC: the POC pilot is throttled, the load lowers in jerks.
- Sandwich for port A fitted where the schematic says B.
- Tie rods torqued unevenly or with an impact gun: the DCV on top sticks.
- An orifice plate left out at reassembly.
- Port relief set below the main relief.
- Anti-cav and relief cartridges swapped.
- Power-beyond plug and sleeve confused.
- Sections reassembled in the wrong order: the functions swap.

## Related

- [Directional control valves, spools and solenoids](/article/directional-control-valves-spools-and-solenoids)
- [Pressure and flow control valves in depth](/article/pressure-and-flow-control-valves-in-depth)
- [Cartridge and logic valves](/article/cartridge-and-logic-valves)
- [Load-sensing, proportional and servo systems](/article/load-sensing-proportional-and-servo-systems)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
