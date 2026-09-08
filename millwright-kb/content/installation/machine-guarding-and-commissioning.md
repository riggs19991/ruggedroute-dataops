---
title: "Machine Guarding and Commissioning: Guard Types and OSHA Opening Rules, Coupling and Drive Guards, Pre-Start Checklist, Rotation Bump, First Run and Run-In, Bearing Temperature and Vibration Acceptance (ISO 20816 Zones), Hot Alignment Check, Baseline Data and Handover"
slug: machine-guarding-and-commissioning
category: installation
kind: procedure
tags: [machine guarding, guards, OSHA 1910.212, OSHA 1910.219, coupling guard, belt guard, guard opening, point of operation, commissioning, pre start checklist, bump test, rotation check, first start, run in, bearing temperature limit, vibration acceptance, ISO 10816, ISO 20816, vibration zones, hot alignment, baseline data, commissioning report, handover, mechanical completion, pre commissioning]
source: "OSHA 29 CFR 1910.212 and 1910.219 (machine guarding and mechanical power transmission apparatus; 7 ft rule; guard openings); ANSI B11.19 and ASME B15.1 (guard design and opening-distance tables); ISO 20816-3 / ISO 10816-3 vibration severity zones for industrial machines; API RP 686 (run-in and hot alignment); manufacturer IOMs (bearing temperature limits); NEMA MG 1 (motor temperature)."
summary: "The two things that finish an installation: guards that meet the OSHA rules for every rotating and nip point, and a commissioning run that proves the machine is right before the plant takes it: the pre-start checklist, checking rotation uncoupled, the first run with vibration and temperature limits, the hot alignment check and doweling, and the baseline data package that becomes the PM reference."
---

## Guarding rules

![Maximum guard opening by distance from the nip point](/img/installation/guard-opening-chart.svg)

*Maximum guard opening by distance from the nip point*

- **Every** rotating shaft, coupling, sheave, belt, chain, sprocket, gear, flywheel, projecting key or set screw within **7 ft (2.1 m) of the floor or a working platform** must be guarded (OSHA 1910.219); points of operation, nip points and flying-chip hazards under 1910.212. Over 7 ft still needs guarding where people can reach from ladders or during maintenance if not locked out.
- Guards are **fixed** (bolted, needs a tool to remove: the default for couplings and drives), **interlocked** (the machine stops when the guard opens: for access needed during operation), **adjustable** or **self-adjusting** (saws, grinders).
- Guard openings: the allowed opening size depends on the **distance from the opening to the hazard** (OSHA Table O-10 / ANSI B11.19): within 1/2" of the hazard: opening ≤ 1/4"; at 1-1/2 to 2-1/2": ≤ 3/8"; at 2-1/2 to 3-1/2": ≤ 1/2"; at 3-1/2 to 5-1/2": ≤ 5/8"; at 5-1/2 to 6-1/2": ≤ 3/4"; at 6-1/2 to 7-1/2": ≤ 7/8"; at 7-1/2 to 12-1/2": ≤ 1-1/4"; at 12-1/2 to 15-1/2": ≤ 1-1/2"; over 31-1/2": up to 6". A finger fits through anything over 1/4"; **expanded metal guards must be at least 4" from the hazard** for the usual 1/2-3/4" mesh.
- Guard must **not itself create a hazard** (sharp edges, pinch points, a guard that can contact the coupling), must be strong enough to withstand contact and a thrown coupling piece (1/8" plate or 12 ga expanded metal on a frame for couplings), and must not need removal for routine lubrication (grease fittings extended through the guard, inspection ports with a cover).
- **Coupling guards**: enclose the coupling and the exposed shaft ends completely, fixed to the baseplate, **non-sparking** (aluminium or brass, or a stainless mesh) in classified areas per API 610/671; clearance to the coupling so a failed element does not hit the guard; a hinged or split design so alignment can be checked without unbolting the machine.
- **Belt and chain guards**: cover the nip points at both sheaves/sprockets and the belt run within reach; a bottom open only if over 7 ft from anything.
- **Fan and blower inlets** with mesh; **shaft ends** that project past a bearing get a cap; **set screws and keys** on collars and couplings must be flush or covered.
- Guards go back on **before** the lockout is removed, every time; a missing guard is a stop-work item.

Canadian note: CSA Z432 (Safeguarding of Machinery) and the provincial OHS regulations use the same principles with their own opening tables.

## Pre-start checklist (mechanical completion)

Tick every line; sign it.

1. Installation records complete: level, grout sound, anchors torqued, [pipe strain test](/article/pipe-strain-and-flange-alignment) passed, final cold alignment record with thermal targets, soft foot corrected, hold-down bolts torqued, dowel plan (after hot check).
2. **Lockout** in place on the electrical and process isolations while the following is done.
3. Rotation by hand: free, no rubs, no noise, seals not binding; coupling **disconnected** (spacer out or element removed).
4. **Lubrication**: bearings greased or oil at the correct level (constant-level oiler set and primed; sight glass at the mark), gearbox oil to the mark with the right oil, coupling greased if it is a grease type, oil mist or circulating lube systems running and proven before the machine can start.
5. Cooling water, seal flush, seal pot filled and vented, quench, barrier fluid pressurised.
6. Piping: strainers in, valves in the start-up position (suction open, discharge closed or cracked for a centrifugal, **open** for a PD pump with a relief valve), vents open then closed, pump **primed** and vented.
7. Instruments: pressure gauges, temperature points, vibration probes, level switches, all connected and reading; alarms and trips set and **tested** (low oil pressure trip, high vibration trip, overspeed on turbines).
8. Electrical: motor megger tested, connections per the nameplate voltage, overloads set to FLA × service factor, VFD parameters, emergency stops and interlocks tested, rotation checked (below).
9. **Guards on**, area clean, tools removed, no loose items on the machine, drains closed, fire protection in service, lighting.
10. People: operator briefed, permit signed, lockout removed by the lockout owner in the proper sequence, everyone clear.

## Rotation check ("bump")

With the coupling **disconnected** (never bump a coupled pump backwards: some impellers unscrew, and a gearbox may be one-way), give the motor a short **bump** (a second) and watch the fan or the shaft end: rotation must match the arrow on the pump/gearbox. Wrong: swap any two leads on a 3-phase motor (T1 and T2) at the starter, lockout on, and re-bump. Then connect the coupling per its manual (gap, bolt torque, grid or element in, guard).

## First run and run-in

1. Start with the discharge valve **cracked open** (centrifugal), bring it up to the operating point over a few minutes; watch for prime loss, seal leaks, noise. Listen with a stethoscope or a screwdriver at the bearing housings.
2. Readings at **start, 15 min, 30 min, 1 h, 2 h, 4 h**, then each shift for the first day and daily for a week:
   - Bearing housing temperature (contact thermometer or IR on a painted spot): rising then **stabilising** within 1-2 hours; typical stable **140-180°F (60-80°C)**; alarm at about **180°F (82°C)** housing / 200°F (95°C) oil, per the maker; a bearing that keeps climbing is over-greased, misaligned, preloaded or running dry: **shut down** and find out.
   - Motor frame temperature and current vs FLA on all three phases (imbalance under 10%).
   - **Vibration** at each bearing, horizontal/vertical/axial (see zones below).
   - Suction and discharge pressure, flow, seal leakage (drips per minute for packing, dry for a mechanical seal after a few minutes), oil level, coupling temperature.
   - Noise, smell, leaks at every flange.
3. New bearings and gears run in: temperature may run 10-20°F higher for the first hours; grease-packed bearings purge and cool. A gearbox's first oil change comes early (per the maker: often 500 h or 2-4 weeks) to remove run-in debris.
4. Stop and investigate at: vibration in Zone C/D, temperature still climbing after 2 h or above the alarm, seal spraying, unusual noise, current above FLA × SF, oil level falling.

### Vibration acceptance (ISO 20816-3 / ISO 10816-3, overall velocity, mm/s RMS, 10-1000 Hz)

| Machine group | Zone A (new, good) | Zone B (acceptable, unrestricted) | Zone C (restricted; plan repair) | Zone D (damage) |
|---|---|---|---|---|
| Group 1: large machines 300 kW-50 MW, rigid foundation | ≤ 2.3 | 2.3-4.5 | 4.5-7.1 | > 7.1 |
| Group 1, flexible foundation | ≤ 3.5 | 3.5-7.1 | 7.1-11 | > 11 |
| **Group 2: medium machines 15-300 kW (most pumps, fans, motors), rigid foundation** | **≤ 1.4** | **1.4-2.8** | **2.8-4.5** | **> 4.5** |
| Group 2, flexible foundation | ≤ 2.3 | 2.3-4.5 | 4.5-7.1 | > 7.1 |
| Pumps > 15 kW, integrated impeller (ISO 20816-3 group 3/4) | ≤ 2.3-3.2 | to 4.5-7.1 | to 7.1-11 | above |

(1 mm/s = 0.0394 in/s; Zone B upper for a Group 2 rigid machine = **0.11 in/s**.) A new installation should be **Zone A** or low Zone B; anything in C at start-up is an installation problem (alignment, unbalance, looseness, resonance, pipe strain), not "running in". Full signature interpretation in [vibration basics](/article/vibration-basics-and-iso-severity).

## Hot alignment check and doweling

After **at least 4 hours** at operating temperature (or until the bearing temperatures and the casing are stable), shut down and **immediately** take alignment readings (laser is fastest; within 10-15 minutes the machine has cooled measurably): compare with the cold targets and the predicted thermal growth; if the hot alignment is outside tolerance, re-set the cold targets (the [thermal growth](/article/thermal-growth-alignment) article covers the math) and re-align cold; run again and re-check. When the hot alignment is accepted, **dowel** (see [leveling and machine setting](/article/leveling-and-machine-setting)) and record the final cold offsets that produce it.

## Baseline data and handover

The **commissioning report** becomes the PM baseline: without it, nobody knows what "normal" is.

- Equipment tag, nameplate data (motor and driven), coupling type and gap, belt/sheave sizes, lubricant names and quantities, filter part numbers.
- Installation records: level readings, grout date and product, anchor torque, pipe strain test result, cold alignment (as-found and final), hot alignment, thermal targets, shim packs per foot, dowel positions.
- Run data: vibration spectra (not just overall) at each bearing in 3 axes, bearing and motor temperatures at stable condition, motor current per phase, pressures/flows at the duty point, seal condition, noise notes, first oil-change date.
- Settings: overload, VFD parameters, alarm and trip set points, relief valve setting, spring hanger settings.
- Drawings marked as-built; spare parts list; the manual filed and a copy at the machine.
- Signatures: installer, commissioning lead, operations, maintenance.

## Common mistakes

- A coupling guard fabricated 3/8" from the coupling: it rings and rubs, and the crew removes it.
- Expanded metal guard right over the belt nip: fingers go through.
- Bumping a coupled pump: the impeller unscrews (some ANSI pumps) or the gearbox thrust bearing is loaded backwards.
- Starting a PD pump against a closed discharge.
- Accepting 0.25 in/s vibration on a new pump as "run-in".
- Doweling before the hot check, then spending a week re-reaming when the hot alignment is off.
- No baseline: a year later the vibration "increase" cannot be evaluated because nobody knows the start point.

## Related

- [Leveling and machine setting](/article/leveling-and-machine-setting)
- [Pipe strain and flange alignment](/article/pipe-strain-and-flange-alignment)
- [Thermal growth in alignment](/article/thermal-growth-alignment)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [Vibration basics and ISO severity](/article/vibration-basics-and-iso-severity)
- [PM checklists](/article/pm-checklists)
- [Reading a motor nameplate](/article/reading-a-motor-nameplate)
