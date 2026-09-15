---
title: "Pressure and Flow Control Valves in Depth: Direct-Acting vs Pilot-Operated Relief (Cracking, Full-Flow and Override, the Vent Port, Remote and Unloading Control), Reducing and Reducing-Relieving Valves, Sequence and Unloading Valves, Counterbalance and Brake Valves (Pilot Ratios 3:1, 4.5:1, 10:1 and Setting to 1.3× Load), Pressure Switches, Needle vs Pressure- and Temperature-Compensated Flow Controls, Meter-In, Meter-Out and Bleed-Off, Flow Dividers, Regeneration and Cushions"
slug: pressure-and-flow-control-valves-in-depth
category: hydraulics
kind: reference
tags: [relief valve, direct acting relief, pilot operated relief, balanced piston relief, cracking pressure, full flow pressure, pressure override, relief valve vent port, remote relief, unloading relief, solenoid vent, pressure reducing valve, reducing relieving valve, sequence valve, unloading valve, hi-lo circuit, accumulator unloading, counterbalance valve, load holding valve, motion control valve, pilot ratio, 3:1 pilot ratio, 4.5:1, 10:1, counterbalance setting, brake valve, overcenter valve, pressure switch, pressure transducer, flow control valve, needle valve, pressure compensated flow control, temperature compensated, hydrostat, priority flow control, bypass flow control, meter-in, meter-out, bleed-off, flow divider, spool flow divider, gear flow divider, pressure intensification, regenerative circuit, cylinder cushion, deceleration valve, setting hydraulic valves]
source: "Eaton Vickers Industrial Hydraulics Manual (pressure and flow control valve operation, override, setting order); Sun Hydraulics counterbalance technical tips (pilot ratio selection and setting procedure); Parker and Bosch Rexroth pressure valve catalogues (override curves, vent and remote control, drain requirements); Rexroth Hydraulic Trainer volume 1 (flow control and flow divider theory); Fluid Power Society technician manuals; NFPA/T2 fluid power practice."
summary: "The valves that decide how hard and how fast a machine works, at the level a troubleshooter needs: what happens inside a relief valve between cracking and full flow and why a direct-acting one overrides so much more, what the vent port is for and how a remote or a solenoid uses it, how reducing, sequence and unloading valves differ in what they sense and where they drain, how a counterbalance valve holds and lowers a load and how the pilot ratio decides whether it is stable or efficient, the exact setting procedures with the gauge in the right place, how a compensated flow control keeps speed constant and where meter-in, meter-out and bleed-off each belong, flow dividers and their intensification trap, regeneration, cushions and the symptoms each valve gives when it fails."
---

## The four questions for any pressure valve

![Pressure valves as cartridges: relief, load-holding and a solenoid-controlled pressure valve](/photos/hydraulics/relief-valve.jpg)

*Pressure valves as cartridges: relief, load-holding and a solenoid-controlled pressure valve. Photo: HAWE Hydraulik, CC BY-SA 4.0, via commons*

1. **Normally open or closed?** Relief, sequence, unloading and counterbalance valves are normally **closed**; a pressure-**reducing** valve is the only one normally **open**.
2. **What does it sense?** Its own inlet (relief, sequence, counterbalance's internal pilot), its own outlet (reducing), or a remote line (unloading, counterbalance's external pilot, brake valves).
3. **Where does it drain?** A valve whose outlet goes to tank drains internally (relief); a valve whose outlet is pressurised (reducing, sequence, unloading) needs an **external drain** to tank or it cannot move. A blocked drain is the commonest "valve failed" that is not the valve.
4. **Direct-acting or pilot-operated?** Direct-acting: the spring works on the poppet directly; small flows, fast, large override. Pilot-operated: a small pilot valve controls a big main stage; large flows, small override, a vent port, slower.

## Relief valves

![Pilot-operated relief: main stage, pilot poppet and the vent port](/img/hydraulics/pilot-operated-relief.svg)

*Pilot-operated relief: main stage, pilot poppet and the vent port*

**Direct-acting**: a poppet or ball on a seat, a spring, an adjusting screw. Pressure lifts the poppet against the spring. As flow increases the poppet must open further, compressing the spring more, so the pressure rises with flow: from the **cracking pressure** (the first drop passes) to the **full-flow pressure** (rated flow passes) can be a **20-40% rise**: that is the **pressure override**. Fast (no pilot delay), good for shock and small flows (pilot stages, port reliefs, cross-port reliefs on motors), prone to **chatter** at low flows. A machine with a direct-acting main relief set "at 2,000 psi" may crack at 1,500 and waste power all day.

**Pilot-operated (balanced piston)**: a main poppet or spool with a small **orifice** through it, so the same pressure sits on both sides and a light spring holds it shut; a small direct-acting **pilot poppet** on the spring side, set by the adjusting screw. When the inlet pressure reaches the pilot setting, the pilot poppet opens, a small pilot flow passes through the orifice, the pressure above the main poppet falls, and the main poppet lifts against its light spring and passes full flow at only a few percent above the pilot setting: **override 3-8%**. The space above the main poppet is brought out as the **vent port**:

- **Vent to tank** (a solenoid valve opens the vent): the main poppet opens at the light spring pressure (**50-150 psi**): the pump is **unloaded** at almost no power; the standard way to idle a fixed pump between cycles.
- **Vent through a remote small relief** (a direct-acting valve at the operator's console or a proportional relief): the system pressure follows the remote setting, which must be **below** the main valve's own setting; a solenoid selector between two or three remotes gives several pressures.
- **Vent blocked** (plug) = normal operation at the local setting.

Behaviour and faults:

| Symptom | Cause |
|---|---|
| Pressure will not rise above a low value, system hot | Relief stuck open (debris under the pilot or main poppet), vent line open or leaking (a vent solenoid stuck, a cracked vent line: the relief thinks it is being told to unload), spring broken, setting turned out, main orifice enlarged by erosion |
| Pressure rises **above** the setting or the relief never opens | **Pilot orifice blocked**: the main poppet cannot sense and stays shut: a dangerous fault, the system is unprotected; also a jammed main spool |
| Setting creeps down over months, oil hot | Pilot poppet seat worn (wire-drawing from constant leakage), setting screw backing out (lock nut) |
| Screaming or chatter | Direct-acting valve at low flow; a pilot-operated valve set within 100-200 psi of a compensator or another relief; air in the pilot; a damaged seat; too little back-pressure damping; vent line resonating |
| Sudden pressure spikes on a fast circuit | Relief too slow (a pilot-operated valve responds in 20-50 ms; a shock needs a direct-acting relief or an accumulator close to the source) |

**Setting a relief**: gauge on the pump outlet (or the valve's inlet port), a way to dead-head the flow (block the actuator, close a valve, stall a cylinder against its end **only if the cylinder is rated for it**), the compensator (if any) screwed in above the target or the pump on full stroke, the vent plugged; back the screw out, start, turn the screw in slowly while watching the gauge until it reads the design pressure with the pump at full flow; lock the nut and re-read; write it on the valve. On a compensated-pump system the relief is set **150-300 psi (10-20 bar) above** the compensator, so the relief only acts as a safety valve and never runs hot.

## Pressure-reducing valves

A spool held **open** by a spring; the **downstream** pressure is fed to the spool's end and pushes it toward closed. When the downstream reaches the setting the spool throttles to hold it there, whatever the upstream does. The spring chamber must **drain to tank** (external drain port, or through the T line on a sandwich) or the spool cannot move: a blocked drain = full upstream pressure downstream. Because a plain reducing valve cannot relieve pressure that builds downstream (thermal expansion, an over-running load), a **reducing-relieving** valve adds a relief function: the spool over-travels and vents downstream to the drain.

Uses: a clamp circuit at 500 psi on a 3,000 psi machine, a pilot supply at 200-300 psi, a second lower pressure on one function of a manifold. Faults: downstream at full pressure (drain blocked, spool stuck open, seat damaged); downstream too low or nothing (set too low, spool stuck closed, upstream too low); heat (the relieving function dumping continuously because the downstream is being fed from elsewhere, a check leaking back).

Setting: gauge **downstream** (on the reduced-pressure branch), the branch loaded or dead-headed, turn to the setting; check that the upstream is at least 150 psi higher than the setting.

## Sequence valves

Normally closed, sensing its **inlet**, opening to pass flow to a **second** circuit only when the inlet reaches the setting: clamp first, then drill; extend cylinder 1 to its stop, then cylinder 2. The outlet is pressurised, so the spring chamber needs an **external drain**. A **bypass check** lets the return flow pass backwards. Set it above the pressure the first operation needs to complete (clamp pressure plus a margin of 150-300 psi) and below the relief. Faults: the second stage starts early (set too low, spool leaking, worn seat) or never starts (drain blocked, set above the relief, first operation never reaches the setting because it is bypassing).

## Unloading valves

Normally closed, opened fully by a **remote pilot** signal (not its own inlet), dumping a pump to tank at near-zero pressure once another part of the system holds the pressure. Two classic circuits:

- **Hi-lo (two-pump) circuit**: a large low-pressure pump for rapid traverse and a small high-pressure pump for the work stroke; when the pressure rises to the unloading setting (say 500 psi) the big pump dumps to tank and the small one continues to 3,000 psi. Symptom of a failed unloading valve: the big pump goes over the relief at high pressure and the motor overloads, or the machine crawls in rapid traverse.
- **Accumulator charging**: an unloading valve with a **differential** (unloads at the set pressure, re-loads when the pressure falls 10-20% below); the check between pump and accumulator holds the charge. A valve that cycles constantly = a leaking check or a lost precharge.

## Counterbalance and brake valves

![Counterbalance valve: pilot ratio, setting and the stable choice](/img/hydraulics/counterbalance-pilot-ratio.svg)

*Counterbalance valve: pilot ratio, setting and the stable choice*

A **counterbalance (over-centre, motion control, load-holding) valve** sits in the line from the load side of a cylinder or motor. It is a relief valve with two pilots: the **internal pilot** (its own inlet, the load pressure) and an **external pilot** from the **opposite** actuator line (the pressure the directional valve is applying to lower the load), plus a free-flow **check** for raising. Set **above** the load-induced pressure, it holds the load leak-free (poppet type) with the directional valve centred; to lower, the DCV pressurises the other side of the cylinder, the external pilot pressure adds to the internal, and the valve opens **only as far as the pilot pressure demands**, so the load never runs away faster than the pump feeds the other side: no cavitation, no free fall, no over-speed.

**Pilot ratio** = how much more effective the external pilot is than the internal: at a ratio R, the pilot pressure needed to open is roughly (setting − load pressure) ÷ R.

| Ratio | Character | Where |
|---|---|---|
| **3:1** | Needs the most pilot pressure to open, so the valve stays partly closed and throttles: **most stable**, most heat, slowest lowering | Hydraulic motors, long booms and springy structures, long hoses, anything that shudders with a higher ratio |
| **4.5:1** | The general-purpose compromise | Most cylinders on cranes, loaders, presses |
| **10:1** | Opens with little pilot pressure: **most efficient**, least heat, fastest; the least stable (a small change in pilot pressure swings it wide open: with a springy load it hunts) | Rigid loads, short lines, machines with a stiff frame |

**Setting**: measure the **load-induced pressure** with the load held and the DCV centred (gauge on the load line): say 1,200 psi. Set the counterbalance to about **1.3 × 1,200 = 1,560 psi**: with the load raised and the gauge on the load line, screw the adjuster in until the load cannot be lowered even with the DCV shifted, then back it out until the load just starts to lower, then turn it back in about 1/2-1 turn (or set by the gauge to 1.3×); lock. Too low: the load creeps down and cannot be held at the maximum reach. Too high: lowering needs high pilot pressure (the pump works against the valve: heat, slow lowering, the relief may open before the valve does and the load will not come down at all).

**Instability** (a boom that shudders or hammers on lowering): a pilot ratio too high for the load, the setting too close to the load pressure, air in the lines, a **meter-out flow control between the DCV and the counterbalance** (the flow control's back-pressure feeds into the pilot line and the two fight: put speed control on the pilot side or in the DCV), a long pilot line, or back-pressure at the valve's outlet (an **internally vented** valve adds outlet pressure to its setting one-for-one; an **externally vented** version to tank avoids that when the return has back-pressure).

**Brake valves** are counterbalance valves for hydraulic motors with a low pilot ratio and a large **internal pilot area** so the valve is fully open while driving (no back-pressure, no heat) and closes only when the pilot pressure falls: the motor brakes hydraulically when the operator centres the valve. A **cross-port relief pair plus anti-cavitation checks** across the motor completes the circuit.

Counterbalance valves are **safety devices**: on a crane or a lift they may be certified with the machine. Never remove one to "fix a slow lower", never replace one with a different ratio without the designer's say, and never adjust one without a gauge.

## Pressure switches and transducers

A **pressure switch** (piston or diaphragm against a spring, with a micro-switch) has a **set point** and a **differential** (dead band) of typically 5-15% of the setting; a switch that chatters is set within its differential of the working pressure. Check it with a gauge on the same line and a meter on the contacts. A **transducer** gives 4-20 mA or 0-10 V; check the zero at atmospheric pressure and one point against a calibrated gauge; a transducer on a line with shock needs a snubber (an orifice) or it dies early. Both must be fitted with a **test point** beside them or you will never know which one is lying.

## Flow controls

![Meter-in, meter-out and bleed-off: where the flow control goes](/img/hydraulics/flow-control-placement.svg)

*Meter-in, meter-out and bleed-off: where the flow control goes*

- **Needle valve** (non-compensated): flow through an orifice varies with the **square root of the pressure drop** across it: double the ΔP and the flow rises about 41%. So a cylinder speed set with a needle valve changes when the load changes (slower under load, faster when the load runs away). Fine for constant loads, bleed lines, gauge snubbers and pilot damping.
- **Pressure-compensated flow control**: a needle (or a fixed orifice) plus a **hydrostat** (a spring-biased spool) that holds a constant pressure drop across the needle (typically 50-100 psi / 3-7 bar) by throttling the excess: constant flow whatever the load, so long as the inlet pressure is at least the compensator's spring plus the load. **Restrictor type** (in-line; the excess flow goes over the relief: heat) or **bypass / priority type** (three ports; the excess goes to tank or to a second circuit at low pressure: efficient; used for steering priority on tractors). A compensated valve also has a **free-flow check** for the reverse direction on cylinder lines.
- **Temperature compensation**: a sharp-edged orifice (flow nearly independent of viscosity) or a bimetal-adjusted needle, for machines whose speed must not change from a cold morning to a hot afternoon.
- **Where it goes**:

| Method | Position | Good for | Watch for |
|---|---|---|---|
| **Meter-in** | Between the DCV and the actuator inlet | Resistive loads that always push back (pressing, clamping, lifting), precise feed | Cannot control an **over-running** load (the cylinder runs ahead of the oil and cavitates); the excess pump flow goes over the relief (heat) with a fixed pump |
| **Meter-out** | In the actuator's return line | The usual choice for cylinders and for **over-running** loads (a load lowering, a drill breaking through); holds the load back | **Pressure intensification**: with the rod end metered on a differential cylinder, the trapped rod-end pressure can reach the cap-end pressure × the area ratio (a 2:1 cylinder at 3,000 psi cap makes 6,000 psi rod-end: rod seals and hoses must take it); heat over the relief with a fixed pump |
| **Bleed-off** | From the pressure line to tank, in parallel with the actuator | Efficient (only the metered flow is bled; the pump sees the load pressure, not the relief) | Least accurate (the actuator gets the pump flow minus the bleed, so pump wear changes the speed); no over-running control |

- A flow control **never changes force**; it changes speed. A weak function with the flow control wide open is a pressure problem; a slow function at full pressure is a flow problem.

**Flow dividers**: a **spool divider** (two compensated orifices sharing one spool) splits one flow 50/50 or another ratio to two actuators regardless of their loads, with 5-10% error, and often **combines** the return; a **gear (rotary) divider** (two or more gear sections on one shaft) splits more accurately and to several outlets, and **intensifies pressure**: if one outlet stalls, the sections driving it are turned by the others and can push its pressure far above the pump's (fit a relief on each outlet). Symptoms: one side runs ahead (a spool divider's compensator stuck, a gear section worn), or a blown hose on a stalled branch (no branch relief).

**Regenerative circuits**: connecting the rod end to the cap end while extending (a regenerative spool centre, or a valve that switches the rod-end oil across) makes the cylinder extend fast (speed = pump flow ÷ rod area) at reduced force (force = pressure × **rod** area only); a second valve switches to normal extension for the work stroke. A press that advances fast but will not build tonnage is stuck in regeneration; one that advances slowly has lost it.

**Cushions and deceleration**: a cylinder cushion is a spear or sleeve that enters a pocket near the end of stroke and forces the last of the return oil through an adjustable **needle** (the cushion screw, often with a check for a fast start out of the cushion). Set it so the piston decelerates without banging and without stalling short; a cushion screw fully in stalls the cylinder before the end; fully out gives a bang at each stroke. A **deceleration valve** is a cam-operated flow control on the machine slide that slows a fast traverse before the stop; a **shock (pressure) spike at the end of a fast stroke** wants a cushion, a deceleration valve, a ramp on a proportional valve or an accumulator, not a higher relief setting.

## Setting order on a whole machine

1. Main relief (everything else backed off or blocked).
2. Pump compensator (150-300 psi below the relief), LS margin.
3. Reducing valves.
4. Sequence, unloading, counterbalance (1.3× load).
5. Port and cross-port reliefs (10-20% above the main relief on holding functions, or per the drawing).
6. Flow controls and cushions.
7. Pressure switches and transducers checked against a gauge.
8. Every value written on the schematic with the date.

## Common mistakes

- A direct-acting relief chosen for the main relief: it cracks 500 psi low and the tank runs hot.
- The vent port left open (a fitting removed, a vent solenoid failed) and the "relief is stuck open".
- A pilot orifice blocked and the relief never opens: a burst hose at 5,000 psi on a 3,000 psi machine.
- A reducing valve with its drain plugged: full pressure downstream, a crushed part.
- A counterbalance removed to speed up lowering; a 10:1 valve fitted to a springy boom.
- A meter-out flow control fitted between the DCV and the counterbalance: the boom shudders.
- Intensified rod-end pressure with meter-out on a 2:1 cylinder blowing the rod seal.
- Opening the flow control to fix a weak function.
- A gear flow divider with no branch reliefs: the stalled branch's hose bursts.
- Setting valves without a gauge, or with the gauge at the pump when the valve is at the actuator.

## Related

- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
- [Directional control valves, spools and solenoids](/article/directional-control-valves-spools-and-solenoids)
- [Cartridge and logic valves](/article/cartridge-and-logic-valves)
- [Stack valves and sectional valve banks](/article/stack-valves-and-sectional-valve-banks)
- [Hydraulic pumps: types, controls and testing](/article/hydraulic-pumps-types-controls-and-testing)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Accumulator precharge and safety](/article/accumulator-precharge-and-safety)
- [Hydraulic symbols (ISO 1219), complete](/article/hydraulic-symbols-iso-1219-complete)
- [Reading hydraulic and pneumatic circuit diagrams](/article/reading-hydraulic-and-pneumatic-circuit-diagrams)
