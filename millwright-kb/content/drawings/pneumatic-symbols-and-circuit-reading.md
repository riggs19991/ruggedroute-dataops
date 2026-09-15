---
title: "Pneumatic Symbols and Circuit Reading: What Differs From Hydraulics (Open System, Exhausts, Compressibility), the FRL and Air Preparation Symbols, Sources, Exhausts and Silencers, 3/2, 5/2 and 5/3 Valves and Port Numbering, Normally Open and Normally Closed at Rest, Cylinders, Rodless and Guided Types, Grippers, Air Motors and Vacuum, Meter-Out Speed Control, Quick Exhaust, Shuttle and Two-Pressure Valves, a Clamp-and-Press Circuit Read Step by Step, the A+ B+ B- A- Sequence Chart and Pneumatic Stored-Energy Safety"
slug: pneumatic-symbols-and-circuit-reading
category: drawings
kind: chart
tags: [pneumatic symbols, pneumatic schematic, iso 1219 pneumatic, air circuit diagram, frl symbol, filter regulator lubricator symbol, auto drain, regulator with gauge, air dryer symbol, soft start valve, dump valve, lockout valve, air source symbol, exhaust symbol, silencer, 3/2 valve, 5/2 valve, 5/3 valve, port numbering 12 14, normally open, normally closed, rest position, double solenoid, pilot assisted solenoid, manual override, single acting cylinder, double acting cylinder, rodless cylinder, guided cylinder, gripper symbol, air motor symbol, vacuum generator, vacuum cup, vacuum switch, meter out, meter in, quick exhaust valve, shuttle valve, two pressure valve, pressure sequence valve, clamp and press circuit, sequence chart, step displacement diagram, signal overlap, pneumatic safety]
source: "ISO 1219-1:2012 and ISO 1219-2 (fluid power symbols and circuit diagrams, pneumatic port numbering); SMC and Festo Didactic pneumatics training manuals (valve functions, sequence circuits, displacement-step diagrams); Parker and Norgren air preparation and valve catalogues; NFPA/T3.28 symbol practice; OSHA 1910.147 (control of hazardous energy, pneumatic stored energy)."
summary: "How to read an air circuit: the symbols that only appear on pneumatic sheets (FRL, exhausts, silencers, vacuum), the 3/2, 5/2 and 5/3 valves with their numbered ports and how to tell normally open from normally closed at rest, the cylinders, motors and vacuum gear, why speed control is meter-out, then a clamp-and-press circuit traced step by step and the sequence chart that describes it, ending with the stored-energy rules before you touch an air machine."
---

Pneumatic schematics use the same ISO 1219 language as hydraulics, so the [hydraulic symbol chart](/article/hydraulic-symbols-iso-1219-complete) covers most of what you will see. Air adds a handful of its own symbols and one big difference in the way the circuit is drawn: nothing comes back. This article covers the extra symbols, the valves that dominate air circuits, and how to trace a two-cylinder sequence from the sheet. Setting up the hardware is in [pneumatic systems, FRL and cylinders](/article/pneumatic-systems-frl-and-cylinders).

## What is different from hydraulics

- **Open system.** Air is used once and exhausted to atmosphere through a **hollow triangle** on the valve or cylinder port. There are no return lines and no tank symbol, so an air sheet looks sparse: supply in, exhausts out.
- **Hollow triangles.** Every flow direction, pilot and source is drawn with an open (hollow) triangle instead of a solid one.
- **Compressibility.** A cylinder fed with air does not move at a controlled speed just because you meter the inlet; it lurches. That is why speed control is on the exhaust side (meter-out) and why a load can run away when the air is dumped.
- **Low pressure.** Plant air is 80-120 psi (5.5-8 bar), so the sheet carries regulator settings, not relief settings; a pneumatic circuit rarely has a relief valve, the compressor and receiver have one.
- **Pilot-operated valves need a minimum supply**, usually 30-45 psi (2-3 bar), to shift; the valve catalogue says so, the sheet does not.
- **Port numbers, not letters**: 1 supply, 2 and 4 outlets, 3 and 5 exhausts, 12 and 14 pilot ports. Older sheets and some US makers still use P, A, B, R, S (or EA, EB).

## Air preparation: the FRL

![Air preparation symbols: filter, regulator, lubricator and the combined FRL](/img/drawings/pneu-frl-sheet.svg)

*Air preparation symbols: filter, regulator, lubricator and the combined FRL*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Filter | Diamond with a dashed line across it | Removes particles and water | Element size (5, 40 micron) beside it |
| Filter with manual drain | The diamond with a drain stub ending in a small tap (a T on a stem) | Bowl drained by hand | Daily |
| Filter with automatic drain | Drain stub with a float (small circle on a stem) | Bowl dumps itself | Check it actually dumps |
| Regulator | Square with a straight-through arrow, a spring with a slanted adjustment arrow above, a dashed pilot from the outlet below; a **relieving** regulator adds a small exhaust triangle | Holds downstream pressure at the setting | The setting in psi/bar is written beside it |
| Regulator with gauge | The regulator with a gauge circle on its outlet | Same, with a reading | Set it with air flowing |
| Lubricator | Diamond with a drip (a small drop shape) inside, or a reservoir drawn below | Adds oil mist | Only where the tools or cylinders need it |
| Combined FRL, simplified | A rectangle with a single diagonal across it and one port each side, labelled FRL | Filter, regulator, lubricator in one unit | The simplified symbol hides the settings: look for a note |
| Dryer | Diamond with a dashed line and a hatched or crossed element | Refrigerated or desiccant dryer | Dew point beside it |
| Soft-start (dump) valve | A 3/2 valve with a throttle in parallel, solenoid or pilot operated, exhaust triangle | Fills the machine slowly on start-up, exhausts it on stop | Prevents a cylinder slamming on the first stroke |
| Lockout (isolation) valve | A 3/2 manual valve with a lever or a rotary knob and an exhaust triangle, marked with a padlock or LO | Shuts off supply **and exhausts** the machine downstream | The OSHA lockout point; a plain ball valve does not exhaust |

## Sources, exhausts and silencers

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Air source | Small circle with a hollow inner circle, on a stub | Plant air, the receiver or a compressor | The supply pressure is written beside it |
| Exhaust, unthreaded | Small hollow triangle on the port | Vents straight to atmosphere | |
| Exhaust, threaded | Hollow triangle with a short line across its base | Port can take a silencer or a pipe | The common valve exhaust |
| Silencer | Rectangle with hatching (or a series of short lines) on the exhaust | Muffler | A plugged silencer slows the valve and the cylinder |
| Exhaust with throttle | Triangle behind a throttle symbol | Speed control at the exhaust | The meter-out control on a valve |

## Pneumatic valves: 3/2, 5/2 and 5/3

Air directional valves are drawn like hydraulic ones: one square per position, lines on the rest square, operators at the ends. The differences are two exhausts on a 5-port valve (one per work port), numbered ports, and the fact that most solenoid valves are **pilot-assisted**: a tiny solenoid switches supply air onto the end of the main spool, so the operator symbol is a solenoid rectangle beside a hollow pilot triangle.

![Pneumatic valves: 3/2, 5/2, 5/3, exhausts, quick exhaust, shuttle and two-pressure](/img/drawings/pneu-valves-sheet.svg)

*Pneumatic valves: 3/2, 5/2, 5/3, exhausts, quick exhaust, shuttle and two-pressure*

| Valve | How it is drawn | What it does | Where used |
|---|---|---|---|
| 3/2, spring return | Two squares; ports 1, 2, 3 on the rest square; operator one end, spring the other | Connects 2 to 1 (pressure) or 2 to 3 (exhaust) | Single-acting cylinders, pilot signals, blow-off, dump valves |
| 5/2, single solenoid, spring return | Two squares; ports 1 (centre bottom), 2 and 4 (top), 3 and 5 (bottom corners); solenoid-plus-pilot one end, spring the other | Rest: 1 to 2, 4 to 5. Energised: 1 to 4, 2 to 3 | Double-acting cylinders that must return when power fails |
| 5/2, double solenoid (memory) | Two squares, a solenoid-plus-pilot at each end, no spring (sometimes a detent) | Stays in the last position when both coils are off; a pulse on 14 shifts to 1-4, a pulse on 12 shifts to 1-2 | Double-acting cylinders that must stay put on power loss; sequence circuits |
| 5/3, closed centre | Three squares, centre with all five ports blocked | Cylinder stops mid-stroke and holds (leaks and compressibility let it creep) | Positioning with care |
| 5/3, exhaust centre | Centre: 2 and 4 joined to 3 and 5, 1 blocked | Both cylinder ports vented: the rod is free to be pushed | Manual positioning, safe stop on horizontal loads |
| 5/3, pressure centre | Centre: 1 joined to 2 and 4, exhausts blocked | Both sides pressurised: the rod is held stiff (moves slowly to extend on the area difference) | Clamping, holding against a light load |

**Port numbering**: 1 supply; 2 the outlet on the 12 side; 4 the outlet on the 14 side; 3 exhausts 2; 5 exhausts 4; **12** is the pilot that connects 1 to 2; **14** the pilot that connects 1 to 4; 10 is a pilot that closes all ports on some valves. The numbers alone tell you which solenoid does what without reading the arrows.

**Operators** as on hydraulic sheets: solenoid (rectangle with a diagonal), pilot (hollow triangle), spring (zigzag), detent (notches), lever, roller, one-way roller, push button, pedal. **Manual override** on a solenoid is a small manual symbol on the solenoid; on the valve body it is the button you push with a pen to test the mechanics with the electrics off.

## Normally open, normally closed and reading the rest position

A pneumatic valve is drawn with everything relaxed: coils off, pilot ports vented, springs in charge. The square the lines touch is what the valve does with the machine stopped.

- A **3/2 normally closed (NC)**: at rest port 1 is blocked and 2 is connected to 3 (the outlet is exhausted). Actuate: 1 to 2. A single-acting cylinder on an NC 3/2 is retracted at rest.
- A **3/2 normally open (NO)**: at rest 1 is connected to 2 (the outlet is pressurised) and 3 is blocked. Actuate: 2 to 3. The cylinder is extended at rest, or a brake is released at rest. Read the arrows, not the label: the same body with the ports piped differently is the other type.
- On a **5/2 spring-return** the rest square is the one at the spring end. Whether the cylinder is extended or retracted at rest depends on which cylinder port is on 2 and which on 4: the sheet shows it, the valve does not.
- A **double-solenoid 5/2** has no defined rest state: it is wherever it was last put, so the sheet usually draws it in the position the machine starts in and adds a note. On power-up the PLC must pulse one coil to be sure.
- A **detented** valve, mechanical or pilot, likewise stays put; the notches tell you.
- Reading a sensor's state: a roller-operated 3/2 limit valve drawn NC is closed until the cylinder hits it; a **held** valve at rest (the cam is on the roller when the machine is stopped) is drawn actuated, sometimes with a note. This matters in sequence circuits, below.

## Cylinders, motors and vacuum

![Pneumatic cylinders, air motor, vacuum generator and cup, speed controls](/img/drawings/pneu-actuators-sheet.svg)

*Pneumatic cylinders, air motor, vacuum generator and cup, speed controls*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Single-acting, spring return | Rectangle, piston, rod, one port at the cap end, a spring in the rod end, an exhaust triangle or a breather at the rod end | Air out, spring back | Clamps, small strokes |
| Double-acting | Rectangle, piston, rod, a port each end | Air both ways | The standard; cushions and adjustable cushions as hydraulic |
| Double-acting, magnetic piston | The cylinder with a small rectangle on the piston, sensors drawn as small squares on the barrel | Reed or solid-state position switches | Switches tagged to the electrical sheet |
| Rodless (band or magnetic) | A long rectangle with a carriage drawn on top, ports each end, no rod | Long strokes in a short space | Magnetic type: two pistons and a coupling drawn |
| Guided (slide) | The cylinder with two parallel guide rods drawn beside the rod | Takes side loads | |
| Gripper | Two jaws (angled lines) on a body with one or two ports; parallel or angular | Opens and closes on air | Single-acting grippers hold on a spring when air is lost |
| Rotary actuator | Half-circle with two ports and a double-headed curved arrow | Rack-and-pinion or vane, 90 or 180 degrees | |
| Air motor | Circle with a hollow triangle pointing in; two triangles for reversible | Rotary output | Hoists, mixers, tools |
| Vacuum generator (ejector) | A venturi shape: a supply port, a narrow throat, an exhaust triangle, a vacuum port with a hollow triangle pointing **into** the body | Compressed air makes vacuum | Often with a blow-off valve drawn in |
| Vacuum cup | A cup shape (a semicircle open downward) on a stub | The suction pad | Several cups on one ejector |
| Vacuum switch | Square with a pilot line and a contact, with the pilot triangle pointing into the square | Confirms the part is held | The PLC permissive before the arm moves |

## Speed and exhaust control

![Meter-in, meter-out and bleed-off speed control](/img/drawings/circuit-meter-in-out.svg)

*Meter-in, meter-out and bleed-off speed control*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Flow control with check (meter-out) | Adjustable throttle with a check in parallel, mounted at the cylinder port, arranged so the check is **free into** the cylinder and the throttle meters the **exhaust** out of it | Controls speed by holding back the exhaust; the piston runs against a cushion of air | The rule for double-acting cylinders: smooth, no lurching, holds an overrunning load |
| Meter-in | The same valve turned round: throttled into the cylinder, free out | Feeds air slowly; the cylinder lurches when the load drops | Only for single-acting cylinders (there is no exhaust to meter on the spring side) and some vacuum work |
| Quick exhaust valve | A three-port body at the cylinder port: inlet from the valve, outlet to the cylinder, a large exhaust triangle; a shuttle-type element inside | Dumps the cylinder straight to atmosphere instead of back through the valve and its silencer | Fast strokes; noisy |
| Shuttle valve (OR) | Rectangle, an inlet each end, an outlet in the middle, a ball between two seats | Output if **either** input has pressure | Two start buttons, either of two sensors |
| Two-pressure valve (AND) | The same rectangle, but the element blocks the outlet unless both inlets are pressurised | Output only if **both** inputs are on | Two-hand controls, a safety and a start together |
| Pressure switch | Square with a pilot line and an electrical contact | Electrical signal at a set pressure | Low-air permissive, clamp-pressure proof |
| Pressure sequence valve | Square with a spring and an adjustment arrow, a pilot line from a sensing port, an output to a pilot line; normally closed | Passes a pilot signal only when the sensed pressure reaches the setting | Proves a clamp is tight before the press moves |

## Reading a clamp-and-press circuit

The commonest two-cylinder machine: cylinder **A** clamps a part, cylinder **B** presses (or drills, stamps, marks), B retracts, then A releases. On the sheet you will find: an FRL, two 5/2 double-solenoid (or double-pilot) valves 1V1 and 1V2 feeding cylinders 1A and 2A, meter-out flow controls at each cylinder port, and four position signals: limit valves or sensors **a0** (A retracted), **a1** (A extended), **b0** (B retracted), **b1** (B extended). Read it in this order:

![Clamp-and-press pneumatic circuit drawn at rest](/img/drawings/pneu-clamp-press-circuit.svg)

*Clamp-and-press pneumatic circuit drawn at rest*

1. **Rest state.** Both cylinders retracted; a0 and b0 are made (their rollers are held down), a1 and b1 are not. Valve 1V1 is drawn with 1 to 2 feeding A's rod end, so A is held retracted; the same for B.
2. **Start.** The start button (a 3/2 push button) and b0 are in series (a two-pressure valve or two contacts): B must be home before A can clamp. The signal goes to pilot 14 of 1V1: 1V1 shifts, 1 to 4, air into A's cap end; A's rod-end air leaves through its meter-out throttle and exhaust 5. **A+**.
3. **A extended.** The roller of a1 is struck; a1 passes a pilot signal to 14 of 1V2. B extends, **B+**. On a press, a pressure sequence valve on A's cap line often replaces a1: B does not move until A is actually clamping at, say, 60 psi (4 bar).
4. **B extended.** b1 (or a time delay for dwell) signals 12 of 1V2: 1V2 returns, **B-**.
5. **B home.** b0 signals 12 of 1V1: A releases, **A-**. The machine is back at rest, waiting for the start button.

Now the trap: at step 4, a1 is still held down (A is still clamped), so pilot 14 of 1V2 is still pressurised when b1 tries to push 12. A double-pilot valve with air on both ends does not move: **signal overlap**, and B never retracts. The sheet shows the cure: a1 drawn as a **one-way roller** (it gives a pulse as A passes, not a held signal), or a cascade of memory valves, or the whole logic moved into the PLC where a1 is just an input. When you replace a limit valve, fit the same type; a standard roller in place of a one-way roller stalls the machine at step 4 and the fault looks like a bad valve.

## The sequence chart

The sheet, or the manual, describes the cycle as a **displacement-step diagram** (sequence chart). Time or step number runs left to right; each cylinder has a band with two lines: 0 (retracted) and 1 (extended). Diagonal lines show the movement in each step, horizontal lines show a cylinder holding. The notation under it is the cycle in letters: **A+ B+ B- A-** for the clamp-and-press above (plus = extend, minus = retract). Some sheets write it as a sequence table with the solenoid energised at each step:

![Step-displacement chart for the clamp-and-press sequence](/img/drawings/pneu-sequence-chart.svg)

*Step-displacement chart for the clamp-and-press sequence*

| Step | Motion | Started by | Solenoid on | End of step signal |
|---|---|---|---|---|
| 1 | A+ | Start and b0 | 1V1 sol 14 (1Y1) | a1 |
| 2 | B+ | a1 (or sequence valve) | 1V2 sol 14 (1Y3) | b1 |
| 3 | B- | b1 (or timer) | 1V2 sol 12 (1Y4) | b0 |
| 4 | A- | b0 | 1V1 sol 12 (1Y2) | a0 |

Read it against the machine: if the cycle stops with A clamped and B out, you are between steps 2 and 3, so the thing to check is b1 (is it struck, is its LED on, does its pilot line reach 12) and the flow control on B's cap-end exhaust. A chart with brackets like (A+ B+) means both move at once; a chart with a dwell shows a horizontal line with a time.

**Safety before you touch an air machine.** A stopped machine is full of stored energy: cylinders held against a load by trapped air, a vertical cylinder that will fall when exhausted, a gripper that will open, a spring that will fire. The lockout point is the **lockout valve that exhausts** the machine, not a ball valve; lock it, watch the machine's gauge fall to zero, exhaust both ends of every cylinder (a 5/3 closed-centre valve traps air on both sides), block or lower anything that can drop, and try the controls. See [lockout basics](/article/lockout-tagout-basics).

## Common mistakes

- Reading a 3/2 as NC because the label says so, when the arrows show 1 to 2 at rest.
- Assuming a double-solenoid valve returns when power is lost: it stays where it was.
- Fitting meter-in flow controls on a double-acting cylinder and chasing a lurching stroke for a week.
- Replacing a one-way roller limit valve with a standard roller: signal overlap stalls the sequence.
- Expecting a pilot-assisted solenoid valve to shift at 15 psi during a low-air test.
- Locking out a ball valve that does not exhaust the machine, then working under a cylinder held up by trapped air.
- Reading the 5/3 exhaust centre as a safe hold on a vertical load: it drops.
- Ignoring the settings written beside the regulator and the sequence valve, then wondering why the press starts before the clamp is tight.

## Related

- [Hydraulic symbols, ISO 1219 complete chart](/article/hydraulic-symbols-iso-1219-complete)
- [Reading hydraulic and pneumatic circuit diagrams](/article/reading-hydraulic-and-pneumatic-circuit-diagrams)
- [Pneumatic systems, FRL and cylinders](/article/pneumatic-systems-frl-and-cylinders)
- [Directional control valves, spools and solenoids](/article/directional-control-valves-spools-and-solenoids)
- [Cylinder repair and seal kits](/article/cylinder-repair-and-seal-kits)
- [PLC and instrumentation awareness](/article/plc-and-instrumentation-awareness)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
