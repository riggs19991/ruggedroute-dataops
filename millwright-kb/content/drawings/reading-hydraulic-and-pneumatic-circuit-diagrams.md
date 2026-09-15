---
title: "Reading Hydraulic and Pneumatic Circuit Diagrams: the Five-Step Tracing Method, Rest-State Conventions, Open-Centre vs Closed-Centre Circuits and What the Gauge Shows at Idle, Meter-In, Meter-Out and Bleed-Off Placement, Regenerative Extend Circuits, Sequence and Counterbalance Circuits, Accumulator and Hi-Lo Two-Pump Circuits, the Component List and Settings Table, and Placing Test Gauges From the Schematic"
slug: reading-hydraulic-and-pneumatic-circuit-diagrams
category: drawings
kind: procedure
tags: [reading hydraulic schematic, hydraulic circuit diagram, pneumatic circuit diagram, tracing a circuit, five step method, rest state, de-energised state, open centre circuit, closed centre circuit, fixed displacement pump, pressure compensated pump, idle pressure, meter in, meter out, bleed off, overrunning load, flow control placement, regenerative circuit, rapid advance, sequence valve circuit, clamp then press, counterbalance circuit, pilot ratio, brake valve, motor circuit, accumulator circuit, bleed down valve, isolation valve, hi lo circuit, two pump circuit, unloading valve, component list, bill of materials, settings table, relief setting, compensator setting, reducing valve setting, accumulator precharge, test gauge placement, case drain, gauge port, hydraulic troubleshooting from schematic, sequence table, solenoid table]
source: "ISO 1219-2 (fluid power circuit diagrams, component identification and the component list); Eaton Vickers Industrial Hydraulics Manual and Parker industrial hydraulic technology training manuals (circuit types, flow control placement, regenerative, sequence, counterbalance and accumulator circuits); Bosch Rexroth Hydraulic Trainer volumes 1 and 3; Festo Didactic pneumatics circuit reading; Fluid Power Society (IFPS) mechanic and technician study manuals (schematic tracing and test gauge placement)."
summary: "A working method for turning a fluid-power schematic into a picture of what the machine does: five steps to trace any circuit, the rest-state rules, how to tell an open-centre from a closed-centre system and what the gauge should read at idle in each, where flow controls sit and why, how regenerative, sequence, counterbalance, accumulator and hi-lo circuits are drawn and behave, how to use the component list and settings table, and how to choose test-gauge points from the sheet before you walk to the machine."
---

A schematic is not a picture of the machine; it is a statement of what the oil or air is allowed to do. Read it properly and it tells you what the machine must do at rest, in each step, and at what pressure, before you open a single cover. This article is the method. The symbols themselves are in the [hydraulic symbol chart](/article/hydraulic-symbols-iso-1219-complete) and the [pneumatic symbol chart](/article/pneumatic-symbols-and-circuit-reading); the fault-finding that follows is in [advanced hydraulic troubleshooting](/article/hydraulic-troubleshooting-advanced-diagnostics).

## The five-step method

![Number the parts, find the supply, follow one signal at a time](/img/drawings/pneu-clamp-press-circuit.svg)

*Number the parts, find the supply, follow one signal at a time*

1. **Find the prime mover and the pump.** The circle with M and the circle with the outward triangle, usually bottom left. Note fixed or variable, the control on it (compensator, load sense) and the case drain; on an air sheet, the source circle and the FRL. Write down the pump flow and supply pressure from the component list.
2. **Trace the supply to tank.** Follow the solid line from the pump outlet through the relief, the filter and every valve until it reaches a tank symbol or an exhaust. On a **fixed pump** there must be a path to tank at rest (an open or tandem centre, an unloading valve, a vented relief); if you cannot find one, the pump sits on the relief and the system heats. On a **compensated pump** there is often no path at rest: the pump destrokes instead.
3. **Identify the actuators.** Every cylinder, motor and rotary actuator, and what each one moves on the machine (the machine's name for it: clamp, lift, index, traverse). Note single- or double-acting, cushions, rod size, and the load direction (is gravity pulling on it?).
4. **Work back from each actuator to the supply**, naming each valve you pass: the directional valve and its centre, any counterbalance, POC or brake valve on the load side, the flow controls and which way they meter, any reducing or sequence valve in the branch. Number each component against the parts list as you go (1V3, RV-2).
5. **Read each operating state by sliding the envelopes.** For each step in the solenoid table or sequence chart, decide which solenoids are on, slide each directional valve's row of squares to the energised position, and follow the flow from pump to actuator to tank. Write down what moves, which way, and what pressure the pump sees. Done for every step, you know the machine.

Take a highlighter to a copy: one colour for pressure, one for return, one for pilot and drain, per state.

## Everything is drawn at rest

The sheet shows the machine **stopped, de-energised, at zero pressure**: pump off, solenoids off, springs in charge, accumulators (usually) discharged, cylinders wherever the note says (normally retracted, or as-drawn). Consequences:

![Every valve is drawn in its rest position: read the box with the ports](/img/drawings/hyd-dcv-sheet.svg)

*Every valve is drawn in its rest position: read the box with the ports*

- The lines touch the rest envelope of every valve. A spring-centred 4/3 is in its centre; a spring-offset 4/2 is at the spring end; a detented valve is wherever the drawing shows it with a note.
- A normally closed pressure valve is drawn closed; a reducing valve is drawn open.
- Limit switches and limit valves are drawn **not actuated**, unless a note says "held" (the cam is on the roller at rest).
- A pilot-operated check is drawn closed; a counterbalance closed; the load, if any, is drawn held.
- Sensors report the rest state: a pressure switch on the supply is open, a level switch made.

If the drawing was made with the machine in a different rest state (a press with the ram up, a lift at the bottom), the title block or a general note says so. Read the notes before the symbols.

## Open-centre and closed-centre circuits

![Open-centre with a fixed pump beside closed-centre with a compensated pump](/img/drawings/circuit-open-vs-closed-centre.svg)

*Open-centre with a fixed pump beside closed-centre with a compensated pump*

| | Open-centre circuit | Closed-centre circuit |
|---|---|---|
| Pump | **Fixed displacement** (gear, vane); flow is constant | **Pressure-compensated** or load-sensing variable pump; flow varies |
| Directional valves | Open or tandem centre; often several in series (the mobile valve bank) | Closed centre; several in parallel off one pressure line |
| At idle, no solenoids | Pump flow passes through the valve centres to tank at 50-150 psi (3-10 bar) | Pump destrokes to near-zero flow and holds the compensator setting, e.g. 2,500 psi (170 bar) |
| The gauge at the pump outlet, idle | **Low**: the sum of the pressure drops through the centres, filter and cooler; a high reading means a blocked path or a stuck valve | **High**: the compensator setting; a low reading means the compensator, a leak or a valve open to tank |
| Relief valve | Sets the working maximum; passes full flow when a cylinder stalls | Set 150-300 psi (10-20 bar) **above** the compensator; should never pass flow in normal use |
| Heat | From the pressure drop through the centres at idle, and from the relief when stalled | Little at idle; from spool leakage and the compensator margin |

The first thing the schematic tells you is which of these you have. A fixed-pump, closed-centre combination with no unloading path is a mistake on the sheet or a system that overheats. A compensated pump with open-centre valves runs at low pressure and the compensator never works: usually a valve swap gone wrong.

## Meter-in, meter-out and bleed-off

A flow control's **position** on the sheet tells you what it can and cannot do:

![Meter-in, meter-out and bleed-off](/img/drawings/circuit-meter-in-out.svg)

*Meter-in, meter-out and bleed-off*

| Placement | Drawn where | What it does | Use it for | Weakness |
|---|---|---|---|---|
| **Meter-in** | In the line **into** the actuator, check free for the return | Meters the oil entering; the excess goes over the relief (fixed pump) or the pump destrokes | Loads that **resist** motion; precise feeds | An **overrunning** load runs away from the oil and cavitates the actuator; heat on a fixed pump |
| **Meter-out** | In the line **out of** the actuator, check free into it | Meters the oil leaving; the actuator is held back by the restriction | **Overrunning loads**, vertical cylinders going down, motors, every pneumatic cylinder | Intensification: a 2:1 cylinder extending at 2,000 psi supply can show 4,000 psi on the rod side; seals and valve must stand it |
| **Bleed-off** | A branch from the pressure line **to tank** through the throttle | Diverts part of the pump flow; the actuator gets the rest at load pressure, not relief pressure | Efficient speed control on fixed pumps where accuracy is not critical | Speed changes with load; useless on overrunning loads |

On an air sheet the rule is simple: meter-out on every double-acting cylinder, meter-in only on single-acting. On a hydraulic sheet, a meter-out on a vertical cylinder together with a counterbalance is normal; a meter-in alone on a hanging load is a fault waiting to happen.

## Regenerative circuits

A regenerative extend circuit joins the rod end to the cap end while extending, so the oil leaving the rod side is added to the pump flow going into the cap side. Drawn as a 4/3 with a **regenerative centre** (P to A and B, T blocked), or as a normal 4/3 with a separate 2/2 or check valve path from the rod line into the cap line, or with the rod line teed into the pressure line and a check valve so the return cannot go to tank. The effect: extend speed rises to pump flow divided by the **rod area** instead of the piston area (a 2:1 cylinder doubles its speed), and force falls to pressure times the rod area. Pressure is the same on both sides of the piston; the net force comes only from the rod. So the sheet shows a regenerative rapid advance followed by a switch to full-force pressing: the transition is a pressure-operated valve (a sequence valve set below the pressing pressure) or a limit switch that shifts to a standard 4/3 position. Never regenerate a motor, and remember that retract in a regenerative valve position is not possible: the sheet always has a second position for it.

![Regenerative circuit for a fast approach](/img/drawings/circuit-regenerative.svg)

*Regenerative circuit for a fast approach*

## Sequence and counterbalance circuits

**Sequence (clamp then press).** Two cylinders on one directional valve. The clamp is fed directly; the press is fed through a **sequence valve** (normally closed, pilot from its own inlet, external drain, bypass check for the return). When the clamp stalls, pressure rises to the sequence setting (say 700 psi / 48 bar, set above the clamp's working pressure and below the relief) and the press moves. Reading it: the setting decides the order, so a press that starts before the clamp is tight has a sequence valve set too low or a clamp leaking so it never builds pressure. On the return stroke both retract together through the bypass check.

![Sequence valve for clamp-then-press and counterbalance on a vertical load](/img/drawings/circuit-sequence-counterbalance.svg)

*Sequence valve for clamp-then-press and counterbalance on a vertical load*

**Counterbalance (vertical loads).** On the tank-side line of a cylinder that lowers a load, a normally closed valve piloted from the **opposite** line, with a reverse check for lifting. Set at about 1.3 times the load-induced pressure (a load making 1,000 psi on the rod side: set 1,300 psi / 90 bar). The **pilot ratio** (3:1, 4.5:1, 10:1) is written beside it: the pilot pressure needed to open it fully is the setting divided by the ratio, so a 3:1 valve set at 1,300 psi opens with about 430 psi from the other line. A high ratio is efficient but unstable with a bouncy load; a low ratio is stable and hot. Reading the circuit: a slow lower is a counterbalance set high or a low pilot pressure (a flow control ahead of the pilot line); a load that creeps is the counterbalance leaking or a POC missing.

**Brake valves on motors.** A winch or travel motor uses a brake valve (two pilots) so the motor is held, released by drive pressure, and braked when the load overruns, often paired with a spring-applied brake drawn as a spring-return cylinder with a pilot triangle. Read which pressure releases the brake; if it does not release, that pilot line is where the gauge goes.

## Accumulator and hi-lo circuits

**Accumulator circuits** appear for three reasons and look slightly different for each: **energy storage** (a small pump charges a large accumulator so a big cylinder can move fast: an unloading valve dumps the pump when the accumulator is full and reconnects at a lower pressure), **shock absorption** (a small accumulator teed into a line near a fast-closing valve, no unloading valve), and **leakage make-up** (holding a clamp for hours with the pump off). Every accumulator on a good sheet has three things next to it: an **isolation valve** between it and the system, a **bleed-down valve** (manual or a solenoid 2/2 normally open to tank that dumps it when the machine stops), and its **precharge** pressure written beside it (typically 80-90 percent of the minimum working pressure for energy storage, 60-70 percent for shock). A check valve stops the accumulator emptying back through the pump. Reading it for safety: the accumulator is charged whenever the isolation valve is open and the bleed valve is closed, pump running or not. See [accumulator precharge and safety](/article/accumulator-precharge-and-safety).

![Accumulator circuit with isolation and bleed-down; hi-lo two-pump circuit](/img/drawings/circuit-accumulator-hilo.svg)

*Accumulator circuit with isolation and bleed-down; hi-lo two-pump circuit*

**Hi-lo (two-pump) circuits.** A large low-pressure pump and a small high-pressure pump on one shaft. At low pressure both feed the circuit (rapid advance, say 30 gpm at 500 psi); when pressure reaches the **unloading valve** setting (piloted from the high-pressure line, set below the relief) the large pump is dumped to tank through the unloading valve, a check valve isolates it, and only the small pump continues (pressing, 5 gpm at 3,000 psi). The sheet shows two pump circles on one shaft, a check in the big pump's line, the unloading valve teed off the big pump's line with its pilot from the small pump's line, and a relief on the small pump. Reading it: a press that is slow to advance has the unloading valve dumping too early (set low or worn); a press that stalls the motor has the unloading valve not dumping (stuck, pilot line blocked).

## The component list and settings table

Every ISO 1219-2 sheet carries a **component list**: item code (1P1, 1V2), description, maker and model, size, and the **setting**. The settings table is the most valuable half-page in the machine's file. It should give:

![The schematic plate on a machine: the component list and settings live beside it](/photos/drawings/load-sensing-schematic.jpg)

*The schematic plate on a machine: the component list and settings live beside it. Photo: Christianhydraulique, Public domain, via commons*

| Item | Setting | Where it comes from |
|---|---|---|
| Main relief | e.g. 2,800 psi (193 bar) | 10-15 percent above the highest working pressure; below the weakest component's rating |
| Pump compensator | e.g. 2,500 psi (172 bar) | 150-300 psi below the relief |
| Reducing valve(s) | e.g. 800 psi (55 bar) branch | The force the branch needs, plus margin |
| Sequence valve | e.g. 700 psi (48 bar) | Above the first operation's working pressure, below the relief |
| Counterbalance | e.g. 1,300 psi (90 bar), 3:1 | 1.3 times load-induced pressure |
| Unloading valve | e.g. 600 psi (41 bar) | The point where the low-pressure pump is no longer useful |
| Flow controls | e.g. 4 gpm (15 L/min) or turns open | Cycle time; recorded as turns from closed if there is no scale |
| Accumulator precharge | e.g. 1,000 psi (69 bar) nitrogen at 70 F (21 C) | 80-90 percent of minimum working pressure; temperature-corrected |

If the sheet has no settings, the machine manual or the commissioning report has them; if nothing does, the values are set by the rules above and then written on the sheet. Never adjust a valve without a gauge and without knowing which setting it is.

## Using the schematic to place test gauges

The sheet tells you where a reading means something. Before walking to the machine, mark the gauge points:

![Five test gauges on a circuit and the settings table they are read against](/img/drawings/circuit-test-points.svg)

*Five test gauges on a circuit and the settings table they are read against*

| Gauge point | Drawn where | What the reading proves |
|---|---|---|
| **Pump outlet** (before the relief tee) | The first gauge symbol after the pump circle, or the P port of the first valve | Whether the pump and relief/compensator are doing their job: compare with the relief and compensator settings at stall and at idle |
| **Downstream of each reducing valve** | The branch line after the reducing square | The branch pressure against its setting; a reading that follows the supply means the reducing valve is stuck open |
| **Each actuator port** (cap and rod) | Test points on the cylinder lines, drawn as Minimess stubs | Where pressure is lost between pump and work: full at P but low at the cap end is a valve or line; full at the cap end with no movement is the cylinder or the load |
| **Case drain** (pump or motor) | The short-dash line to tank | A flow meter here proves pump wear: over about 10 percent of pump flow is worn; pressure should stay under 15-30 psi (1-2 bar) or the shaft seal blows |
| **Pilot lines** (X, counterbalance pilot, brake release) | The dashed lines | Whether the pilot pressure a valve needs is actually there (a two-stage valve needs 50-150 psi at X; a counterbalance needs its setting divided by the ratio) |
| **Accumulator side of the isolation valve** | The gauge on the accumulator manifold | Charged or bled; the precharge shows as the point where the gauge falls suddenly to zero on bleed-down |

Read each gauge against the settings table in the state the sheet describes: pump idle, function stalled, function moving. Take the readings in order along the flow; the point where the number goes wrong is where the fault is. The full sequence with flow-meter and temperature checks is in [advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics).

## Common mistakes

- Reading the sheet with the valves in their energised positions and deciding the machine cannot hold a load at rest.
- Finding no path to tank on a compensated-pump sheet and calling it a drawing error: the pump destrokes.
- Reading an idle gauge of 2,500 psi on a closed-centre system as a stuck relief; it is the compensator.
- Putting a meter-in flow control on a hanging load and chasing cavitation and a runaway cylinder.
- Setting a sequence valve above the relief so the second operation never starts.
- Removing a counterbalance to cure a slow lower.
- Missing the bleed-down valve on the accumulator and opening a line that is still at full pressure.
- Adjusting a valve to a number from memory instead of the settings table, then adjusting three others to compensate.
- Putting the test gauge on the pump and concluding the system is fine while the actuator port shows half the pressure.

## Related

- [Hydraulic symbols, ISO 1219 complete chart](/article/hydraulic-symbols-iso-1219-complete)
- [Pneumatic symbols and circuit reading](/article/pneumatic-symbols-and-circuit-reading)
- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
- [Pressure and flow control valves in depth](/article/pressure-and-flow-control-valves-in-depth)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Accumulator precharge and safety](/article/accumulator-precharge-and-safety)
- [Stack valves and sectional valve banks](/article/stack-valves-and-sectional-valve-banks)
- [Load-sensing, proportional and servo systems](/article/load-sensing-proportional-and-servo-systems)
