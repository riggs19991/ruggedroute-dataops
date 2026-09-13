---
title: "Load-Sensing, Proportional and Servo Systems: How a Load-Sense Pump and Valve Work Together, Margin Pressure, LS Lines and Shuttle Networks, Pre- and Post-Compensated Sections and Flow Sharing, Priority Valves, the Faults of a Lost or Blocked LS Signal, Electro-Hydraulic Proportional Valves (LVDT Spool Feedback, Amplifier Cards, Ramps, Deadband, Gain, Dither), Servo Valves (Torque Motor, Flapper-Nozzle and Jet-Pipe Pilots, Null, 3 µm Filtration), Checks with a Meter and When to Swap or Send Out"
slug: load-sensing-proportional-and-servo-systems
category: hydraulics
kind: reference
tags: [load sensing, load sense pump, LS pump, margin pressure, standby pressure, LS line, load sense signal, LS shuttle, shuttle network, LS orifice, LS relief, pre-compensated, post-compensated, flow sharing, LUDV, priority valve, steering priority, load sense troubleshooting, LS signal lost, proportional valve, proportional directional valve, electro-hydraulic proportional, LVDT, spool position feedback, amplifier card, proportional amplifier, ramp time, deadband compensation, gain adjustment, dither, PWM solenoid, proportional solenoid, command signal, 4-20 mA, 0-10 V, servo valve, servovalve, torque motor, flapper nozzle, jet pipe, feedback wire, servo valve null, null adjust, servo valve filtration, 3 micron filter, contamination lock, servo valve troubleshooting, proportional valve troubleshooting, hydraulic control systems]
source: "Bosch Rexroth Hydraulic Trainer volume 2 (proportional and servo valve technology) and volume 3 (mobile load-sensing systems, LUDV); Danfoss PVG 32 technical information and PVG service manual (LS, flow sharing, LS relief, shuttle network); Eaton Vickers Mobile Hydraulics Manual (load sensing pumps and valves, priority valves); Moog servovalve technical bulletins (nozzle-flapper operation, null, filtration, contamination); Parker proportional valve and amplifier card manuals; Fluid Power Society technician study manuals."
summary: "The systems where the hydraulics are told what to do by a signal rather than a lever: how a load-sensing pump keeps a fixed margin above the highest load, how the valve bank feeds that signal back through shuttles, why pre- and post-compensation behave differently when several functions move, what a priority valve protects, and the faults that lost, leaking or blocked LS signals produce; then the proportional valve (what the amplifier does with the command, why the spool has a position sensor, what ramps, deadband, gain and dither adjust, and how to check command against feedback with a meter) and the servo valve (how a milliamp signal becomes hundreds of horsepower, why null and 3 µm filtration decide its life, and how to test one before deciding to send it out)."
---

## Load sensing

![Load-sense circuit: the pump holds a margin above the highest load](/img/hydraulics/load-sense-margin.svg)

*Load-sense circuit: the pump holds a margin above the highest load*

A fixed pump makes full flow always; a pressure-compensated pump makes full pressure always. A **load-sensing (LS) system** makes only the pressure and the flow the work needs: the pump is a variable-displacement unit with an **LS control** (a second spool on the compensator) that holds the pump outlet at a fixed **margin (standby, differential) pressure**, typically **200-350 psi (14-24 bar)**, above the pressure in the **LS line**. The LS line carries the **highest load pressure** among the working functions back to the pump. With no function operating the LS line is vented to tank and the pump idles at the margin pressure (a few hundred psi at almost no flow: cool and quiet). Move a function and the LS line reports its load pressure; the pump strokes up until the outlet is load plus margin; the flow is set by the spool opening in the valve because the pressure drop across that opening is always the margin.

- **Margin** too low: functions are slow and sluggish, several functions starve each other. Too high: heat and harsh response. It is set on the pump's LS spool with the LS port vented (the outlet then reads the margin) or by reading outlet minus LS line while a function moves.
- The pump's **pressure compensator** (the maximum) still exists and is set above the LS relief in the valve (which limits the LS signal, and so the system pressure, to the working maximum).
- **LS relief** (in the valve inlet) is small and cheap: it only vents the LS signal, and the pump then holds LS relief setting plus the margin. The pump compensator is the backup. Order: LS relief (working pressure minus margin), then pump compensator 150-300 psi above the resulting pressure.
- **LS line orifice and bleed**: a small orifice (0.6-1.0 mm) damps the signal and a bleed to tank lets it decay when the valves centre; blocked bleed = the pump stays at pressure after the lever is released (heat, harsh).
- **Shuttle network**: each work section has a **shuttle** (a ball between the A-side and B-side pressure and the LS gallery) that passes the higher of its own two ports; the sections' shuttles compare in a chain so the gallery carries the highest of all. On many valves the shuttle balls are the first thing to stick or drop out during a rebuild.

**Pre-compensated** sections (a compensator before the metering spool) hold a fixed drop across each spool independently; when the pump runs out of flow (several functions moving), the highest-pressure function loses out (it slows or stops while the others run). **Post-compensated / flow-sharing** sections (Danfoss PVG, Rexroth LUDV, Parker L90LS: the compensator after the spool, referenced to the LS gallery) share the available flow in proportion to the spool openings, so all functions slow together: better for an operator running boom and swing at once. A machine that "loses the boom when I swing" with a pre-compensated valve is behaving as designed.

**Priority valves**: a compensated flow control that gives a critical function (steering, brakes) its flow first and passes the rest ("EF", excess flow) to the main valve; its LS port from the steering unit tells it how much steering is demanded. A priority valve stuck in the excess position = no steering when the loader digs; stuck in the priority position = the loader is dead while steering is fine.

### LS faults

| Symptom | Cause | Test |
|---|---|---|
| Nothing moves (or everything is very slow); pump outlet stays at margin (200-300 psi) | **LS signal lost**: a broken or leaking LS line, a shuttle missing after a rebuild, the LS relief stuck open, the LS bleed too large | Gauges on the pump outlet and the LS port; move a function: the LS should rise to the load pressure and the outlet to load plus margin. If the LS stays at zero: the valve side. Tee a gauge into the LS line at the valve |
| Pump goes to full compensator pressure at idle; hot | LS line **blocked** or the LS bleed/orifice plugged (the signal cannot decay), the LS spool on the pump stuck, an LS line pressurised by a leaking shuttle from a held load | LS pressure at idle should be near zero |
| One function slow, others fine | That section's compensator stuck, its shuttle stuck low, its spool not stroking (pilot pressure, a stroke limiter) | Compare the section's port pressure with the LS gallery |
| Slow when several functions move | Margin too low, pump flow limit reached (normal), pre-compensated valve behaving normally, a worn pump that cannot make the flow | Flow test on the pump; margin reading |
| Harsh, jerky, oscillating | Margin too high, the LS damping orifice missing, air, a leaking LS line making the pump hunt, a compensator spring broken | Log the LS and outlet pressure together |
| Pressure will not reach maximum | LS relief set low or leaking, pump compensator low | Gauge at the LS gallery while a function stalls |
| Steering slow or dead when working | Priority valve, its LS line from the steering unit | Gauge on the priority valve's CF and EF ports |
| Fine cold, loses functions hot | A leaking LS line or shuttle that seals when cold; thin oil past the compensators | |

## Proportional valves

![Proportional valve loop: command, amplifier, solenoid, spool, LVDT feedback](/img/hydraulics/proportional-valve-loop.svg)

*Proportional valve loop: command, amplifier, solenoid, spool, LVDT feedback*

A **proportional solenoid** produces a force proportional to its current over a working stroke (unlike an on-off solenoid, which slams). Against a spring, that positions a spool **in proportion to the command**: a proportional directional valve meters flow smoothly, a proportional relief sets pressure from a signal, a proportional flow control sets speed. Two grades:

- **Open-loop (no feedback)**: the spool position depends on the solenoid force against the spring, so flow forces, friction and temperature shift it; hysteresis 3-7%; fine for ramps and softer motion.
- **Closed-loop (with an LVDT)**: a **linear variable differential transformer** on the spool reports its position to the amplifier, which corrects the current until the spool is where the command says: hysteresis under 1%, repeatable; "high-response proportional" valves close the gap to servo valves. Pilot-operated proportional valves (large flows) have an LVDT on the main spool too, or on both.

The **amplifier** (a card in the panel, or integrated on the valve as **OBE, on-board electronics**) takes the **command** (±10 V, 0-10 V or 4-20 mA from the PLC, or a joystick), and drives the solenoid with a **PWM current** (pulse-width modulated; the current, not the voltage, is what the solenoid feels), with these adjustments:

| Adjustment | What it does | Symptom when wrong |
|---|---|---|
| **Ramp up / ramp down** | Limits how fast the output follows a step in the command: soft starts and stops | Too long: sluggish, the operator over-commands; too short: shock |
| **Deadband compensation (jump, step)** | Adds a current step at the start so the spool jumps its overlap (the dead zone where the spool moves but no flow passes) at once | Too little: a dead zone at low command; too much: a jerk at the start |
| **Gain (max current, Imax)** | Sets the current at full command | Too high: the solenoid saturates and overheats, no control at the top; too low: the valve never fully opens |
| **Min current (Imin, offset)** | The current at zero command (holds the spool at the edge of the overlap) | Too high: the function creeps at zero command |
| **Dither** | A small AC ripple (100-500 Hz) on the current keeps the spool micro-moving so it never sticks: overcomes static friction | Too little: hysteresis, sticking; too much: audible buzz, wear, a visible tremor in the actuator |
| **Feedback gain / P-I-D** (closed-loop) | How hard the loop corrects the spool position error | Too high: oscillation (a buzzing spool, an unstable actuator); too low: slow |
| **Enable** | A digital input that must be present or the output is zero | Missing enable = a dead valve with a good command |

### Proportional faults and checks

1. **Command**: measure the signal at the card's input while the PLC commands (0-10 V or ±10 V on a meter; 4-20 mA in series or across the card's shunt): a missing or wrong command is a PLC problem.
2. **Enable and supply**: the card's enable input and its 24 V supply; the card's LEDs (power, enable, fault, cable break).
3. **Output current**: the card's test points (usually 1 V per amp) or a clamp meter on the solenoid lead: should follow the command; a good command and no current = the card (or a shorted or open solenoid tripping its protection: measure the coil, typically 5-25 Ω, and compare with the twin).
4. **Feedback**: the LVDT signal at the card's test point should follow the command; a feedback that does not move with a moving current = a stuck spool or a broken LVDT; one that moves with no flow result = the hydraulics (pilot pressure, a blocked line).
5. **Pilot pressure** (pilot-operated proportional valves): 100-300 psi minimum at X; external or internal, drain at Y; no pilot = no main spool motion however good the electrics.
6. **Hydraulic**: filtration (ISO **17/15/12 to 16/14/11**), varnish (a valve that is sticky first thing in the morning), oil temperature (the electronics and the coil derate above 140°F), a return line back-pressure into the drain.
7. **Swap**: a proportional valve of the same code swapped from a twin axis, with its own OBE (an integrated valve carries its calibration; a card-driven valve needs the card's settings re-done: photograph the pots or read out the parameters first).
8. **Grounding and noise**: shielded cables grounded at one end, separated from VFD cables; a twitching valve is often a wiring problem.

## Servo valves

![Servo valve: torque motor, flapper and nozzles, spool with feedback wire](/img/hydraulics/servo-valve-stages.svg)

*Servo valve: torque motor, flapper and nozzles, spool with feedback wire*

A **servo valve** positions its spool to within a fraction of a micron in a few milliseconds from a signal of a few milliamps, and is used with position, force or velocity feedback from the load (a closed loop around the actuator: injection moulding, flight simulators, test rigs, rolling mills, paper machines, turbine governors). Two-stage construction:

1. **Torque motor** (the first stage): coils around an armature between permanent magnets; the coil current (typically ±8 to ±40 mA, or ±10 to ±200 mA for larger valves) tilts the armature a few thousandths of an inch.
2. **Pilot stage**: **flapper-nozzle** (the armature carries a flapper between two opposed nozzles fed through fixed orifices; tilting it restricts one nozzle and raises that side's pressure) or **jet pipe** (the armature swings a jet across two receiver holes; more contamination-tolerant, fails toward centre). The pressure difference (up to hundreds of psi) drives the spool.
3. **Spool** (second stage) with **mechanical feedback**: a feedback wire (cantilever spring) from the flapper to the spool, so the spool moves until the wire's force balances the torque motor's: spool position proportional to current. Electrical-feedback (LVDT) servo valves and three-stage valves exist for large flows.

**Null**: the current at which the spool is exactly centred and the actuator does not move. Null drifts with temperature, supply pressure and contamination; a servo system that drifts one way at zero command has a null offset: adjusted with the null screw on the valve (a small hex under a plug, a fraction of a turn) or a bias in the controller; the maker's procedure with the load disconnected or safe.

**Filtration is the servo valve's life**: the flapper-nozzle clearances are 25-50 µm and the fixed orifices 100-200 µm; a particle in an orifice or a chip on a nozzle sends the spool hard over (a "hard-over" failure on a flapper valve, a runaway actuator): a **3 µm (β₃ ≥ 200) non-bypass pressure filter right before the valve** and an ISO **16/14/11 to 14/12/9** system, with a last-chance screen in the valve. **Contamination lock** (silt around the spool) shows first as rising hysteresis and a wandering null.

### Servo faults and checks

![A servo valve disassembled: the block, the spool, the torque-motor parts and the springs; nothing here is a field repair](/photos/hydraulics/servo-valve.jpg)

*A servo valve disassembled: the block, the spool, the torque-motor parts and the springs; nothing here is a field repair. Photo: Unknown authorUnknown author or not provided, Public domain, via commons*

| Symptom | Cause | Check |
|---|---|---|
| Actuator drifts one way at zero command | Null shift (temperature, contamination, a bent feedback wire), a leaking cylinder biasing the loop, the controller's offset | Measure the current at which the actuator stops; adjust null per the manual; check the cylinder bypass (a leaking piston makes the loop push one way constantly) |
| Sluggish, slow response, poor repeatability | Contamination (partially blocked orifice or nozzle), rising hysteresis, low supply pressure, a fouled 3 µm filter (check its indicator), low oil temperature (thick oil), a torque motor coil degraded | Command a small square wave and watch the response on the controller or a logger; compare with the twin axis; the filter |
| Oscillation, hum, hunting | Loop gain too high (after a mechanical change: a lighter load, a stiffer mount), air in the cylinder, a loose feedback transducer, a resonating hose | Reduce the gain; bleed; check the transducer mounting |
| Hard-over (runs to one end) | A blocked nozzle or orifice, a broken feedback wire, a coil open, a broken cable, a controller fault | Coil resistance (typically 20-1,000 Ω per coil depending on the valve; compare both coils), cable continuity; no adjustment fixes a blocked nozzle: send out |
| Dead, no response | No supply, no enable, no pilot pressure (some valves need 200+ psi at P before the pilot works), coils open, the controller's output disabled | Current at the coils; pressure at P |
| Erratic under load | Electrical noise, a failing transducer, low supply, air | Shielding and grounds; logger on command and feedback |

**Swap or send out**: a servo valve is not a field-repair item. In the field you can measure coil resistance and insulation, check the null, check the filter, flush the manifold, and swap the valve with a spare (**cap every port instantly**; a valve carried across the shop open collects the particle that kills it). Anything internal (a nozzle, an orifice, the feedback wire, the spool) goes to the maker or a certified shop for cleaning, re-nulling and a flow-gain test on a bench. Before installing a new or repaired valve, **flush the line with a flushing plate** in place of the valve until a particle count meets the target, then fit the valve; run in at low gain.

## Working safely on controlled systems

A proportional or servo system with feedback will do exactly what the loop demands: disconnecting a transducer, swapping a valve or a cable with the system live can send an axis hard-over at full force. Isolate, block the load, and bring it up with the controller in manual or at low gain and the pressure reduced. Every adjustment on a card or a null screw is written down before and after.

## Common mistakes

- "The pump is weak" on an LS machine with a leaking LS line: the pump never got the signal.
- Setting the pump's compensator below the LS relief: the LS relief never governs, the machine is slow.
- A shuttle ball left out of one section: that function dead, the others fine.
- A proportional valve replaced without the card re-set or the OBE parameters transferred.
- Screwing dither to zero to stop the buzz: the valve now sticks.
- A 10 µm bypass filter feeding a servo valve.
- Adjusting null with the load connected and the pressure up.
- A swapped servo valve carried across the shop with open ports.
- Chasing a "hydraulic" fault that is a grounding or shield problem on the command cable.

## Related

- [Hydraulic pumps: types, controls and testing](/article/hydraulic-pumps-types-controls-and-testing)
- [Directional control valves, spools and solenoids](/article/directional-control-valves-spools-and-solenoids)
- [Stack valves and sectional valve banks](/article/stack-valves-and-sectional-valve-banks)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
- [Hydraulic fluids: types and compatibility (varnish)](/article/hydraulic-fluids-types-and-compatibility)
- [PLC and instrumentation awareness](/article/plc-and-instrumentation-awareness)
