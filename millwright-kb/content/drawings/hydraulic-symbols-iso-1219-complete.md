---
title: "Hydraulic Symbols to ISO 1219, the Complete Chart: How the Symbols Work (Rest State, Envelopes, Ports, the Variable Arrow), Line Types and Reservoirs, Pumps and Motors, Cylinders and Rotary Actuators, Directional Valves and Centre Conditions, Valve Operators, Check and Shuttle Valves, Pressure and Flow Control Valves, Accumulators, Filters and Coolers, Gauges, Switches, Sensors and Connections, ISO 1219-2 Numbering and the Differences From Older ANSI/JIC Symbols"
slug: hydraulic-symbols-iso-1219-complete
category: drawings
kind: chart
tags: [hydraulic symbols, iso 1219, iso 1219-1, iso 1219-2, fluid power symbols, hydraulic schematic symbols, symbol chart, pilot line, drain line, enclosure line, reservoir symbol, pressure source, pump symbol, variable displacement symbol, pressure compensated pump symbol, load sensing symbol, hydraulic motor symbol, cylinder symbol, cushion symbol, telescopic cylinder, rotary actuator, directional valve symbol, 4/3 valve, centre condition, closed centre, open centre, tandem centre, float centre, regenerative centre, valve operators, solenoid symbol, detent, check valve symbol, pilot operated check, shuttle valve, relief valve symbol, reducing valve symbol, counterbalance valve, flow control symbol, flow divider, accumulator symbol, filter symbol, pressure switch symbol, cartridge valve symbol, jic symbols]
source: "ISO 1219-1:2012 (fluid power systems and components, graphical symbols and circuit diagrams, part 1: graphical symbols) and ISO 1219-2 (part 2: circuit diagrams and component identification); NFPA/T3.28 fluid power symbol practice; ANSI Y32.10 and JIC hydraulic standards (older US symbols); Parker, Eaton Vickers and Bosch Rexroth industrial hydraulics training manuals and valve catalogues (symbol usage, spool functions, pilot and drain conventions); SMC and Festo symbol references for the pneumatic variants."
summary: "A symbol-by-symbol chart of everything drawn on a hydraulic schematic, described in words so you can recognise it on any sheet: how the rules of ISO 1219 work, then the lines, reservoirs, pumps, motors, cylinders, directional valves and their centres, operators, checks, pressure and flow valves, conditioning gear, instruments and connections, with the ISO 1219-2 component numbering and the places where older ANSI and JIC drawings differ."
---

Every hydraulic schematic in North America is drawn to ISO 1219 or to its older US ancestors (JIC and ANSI Y32.10), and the two look alike enough that one chart covers both. This article describes each symbol in words, one row per symbol, so you can name what you see and know what it does to the machine. The method for whole circuits is in [reading hydraulic and pneumatic circuit diagrams](/article/reading-hydraulic-and-pneumatic-circuit-diagrams); the air-only symbols are in [pneumatic symbols and circuit reading](/article/pneumatic-symbols-and-circuit-reading).

## How ISO 1219 symbols work

![A hydraulic schematic on a machine plate, drawn in ISO 1219 symbols](/photos/drawings/load-sensing-schematic.jpg)

*A hydraulic schematic on a machine plate, drawn in ISO 1219 symbols. Photo: Christianhydraulique, Public domain, via commons*

- **Functional, not pictorial.** A symbol shows what a component does (ports, positions, flow directions, operator), never its size or shape. A 1/4 in cartridge relief and a 3 in pilot-operated relief share one symbol.
- **Drawn at rest.** Every valve is drawn **de-energised and unactuated**: solenoids off, no pilot pressure, springs in charge, pump stopped. The lines touch the envelope the valve sits in at rest.
- **Envelopes.** Valves are squares, one per position (a 4/3 has three; a pressure or flow valve has one). Pumps, motors and instruments are circles. Filters, coolers and heaters are a diamond. Cylinders and accumulators are rectangles.
- **Ports** are where lines touch the envelope; a short bar across a port means blocked. Hydraulic ports are lettered **P** (pressure), **T** (tank), **A** and **B** (work), **L** (leakage), **X** and **Y** (pilot supply and drain). Pneumatic sheets use numbers (1, 2, 3, 4, 5, 12, 14).
- **Arrows.** A solid triangle on a line is hydraulic fluid and its direction; hollow means air. An arrow inside an envelope is a flow path. A long **slanted arrow through** any symbol means **variable or adjustable**: through a pump, variable displacement; through a spring, an adjustable setting; through a throttle, an adjustable orifice.
- **Springs** are a zigzag and say which way a valve returns when its operator lets go.
- **Grid and numbers.** ISO 1219-1:2012 sizes every symbol on a module so CAD libraries match, and gives each symbol a registration number a legend sheet may quote. Composites (a two-stage valve, a valve stack, a power unit) sit inside a chain-line enclosure with the real ports on its boundary.

## Lines, sources and reservoirs

![Lines, junctions, plugged ports, reservoirs and energy sources](/img/drawings/hyd-lines-sources-sheet.svg)

*Lines, junctions, plugged ports, reservoirs and energy sources*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Working line | Continuous solid line | Supply, return and work lines | Width is not a size |
| Pilot line | Long dashes | Pressure that operates a valve or feeds a compensator | |
| Drain line | Short dashes | Case or spring-chamber drain to tank | A blocked drain stops a valve shifting |
| Enclosure line | Thin chain line (long dash, short dash) rectangle | Boundary of a manifold, stack or power unit | Lines crossing it are the real ports |
| Mechanical connection | Two parallel solid lines | Shaft, rod or lever | |
| Joined lines | Solid dot at the junction | Connected | ISO 1219-1:2012 requires the dot |
| Crossing lines | Cross with no dot | Not connected | Old JIC sheets drew a hop (loop) |
| Plugged port | Short bar across a line stub | Blanked with a plug | Spare manifold ports |
| Reservoir | Open-topped box (three sides): vented; fully closed box: pressurised | The tank | Vented is the plant standard |
| Return above fluid level | Line ends inside the box short of the bottom | Oil falls into the tank | Aerates the oil |
| Return or suction below fluid level | Line runs to the bottom of the box | Submerged return; the pump suction | |
| Pressure source | Small circle with a solid dot, on a stub | Pressure from off the sheet | Pneumatic: a hollow inner circle |
| Electric motor | Circle with M, double line to the pump | The prime mover | A square with M is an engine |

## Pumps and motors

![Pump and motor symbols: fixed, variable, compensated, load-sensing, bi-directional](/img/drawings/hyd-pumps-motors-sheet.svg)

*Pump and motor symbols: fixed, variable, compensated, load-sensing, bi-directional*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Fixed pump | Circle, one solid triangle pointing **out** at the outlet, shaft line on the side | Gear, vane or fixed piston pump | Triangle is the flow direction |
| Bi-directional pump | Two solid triangles pointing out, opposite | Reversible pump | Hydrostatic loops |
| Variable pump | Slanted arrow through the circle | Displacement can change | Says nothing about the control |
| Pressure-compensated pump | Variable pump plus a small control square with a spring, adjustment arrow and a dashed pilot from the outlet | Destrokes at the compensator setting | Relief set above it; see [hydraulic basics](/article/hydraulic-system-basics-and-symbols) |
| Load-sensing pump | Two stacked control squares: a flow compensator fed by a dashed LS line from the circuit, and a pressure compensator | Pressure follows the load plus 150-300 psi (10-20 bar) | See [load-sensing systems](/article/load-sensing-proportional-and-servo-systems) |
| Pump with drain | Short-dash line from the circle to a tank symbol | External case drain | Must run to tank unrestricted |
| Rotation | Curved arrow beside the shaft | Direction viewed on the shaft end | Wrong rotation kills a new pump |
| Fixed motor | Circle, one solid triangle pointing **in** | Rotary output | The mirror of the pump |
| Bi-directional motor | Two solid triangles pointing in | Runs either way | Winches, conveyors |
| Pump-motor unit | Circle with an in and an out triangle | Works as either | Four triangles for two flow directions |
| Rotary actuator | Half-circle or bow-tie, two ports, a double-headed curved arrow | Turns through a set angle (90, 180, 360 degrees) | Angle written beside it |

## Cylinders and actuators

![Cylinder symbols: single, double, double-rod, cushioned, telescopic, intensifier](/img/drawings/hyd-cylinders-sheet.svg)

*Cylinder symbols: single, double, double-rod, cushioned, telescopic, intensifier*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Single-acting, spring return | Rectangle, piston line, rod one end, one port at the cap end, zigzag inside the rod end | Pressure extends, spring retracts | Rod end vented or drained |
| Single-acting, load return | Same with no spring | Load pushes it back | Lifts, presses |
| Double-acting | Piston line, rod one end, a port each end | Powered both ways; retract faster and weaker | The standard cylinder |
| Double-rod | Rods out both ends | Equal area and speed both ways | Machine tables |
| Cushioned | Small rectangle on the piston toward the cushioned end | Slows before the head | One or both ends |
| Cushioned, adjustable | The cushion rectangle with a slanted arrow | Needle-adjustable | Set to not slam, not bounce |
| Telescopic | Nested rectangles with a stepped rod | Multi-stage extension | Dump bodies |

## Directional control valves and centre conditions

A directional valve is named by **ports/positions**: 2/2 shut-off, 3/2 single-acting cylinder or pilot signal, 4/2 two-position, 4/3 the industrial standard, 5/2 and 5/3 pneumatic with two exhausts. It is drawn as one square per position in a row, with the lines touching the square active at rest (the centre of a spring-centred 4/3, the spring end of a 4/2). Read the other positions by sliding the row across the fixed ports; each operator pushes the row toward its own end. Inside a square, an arrow between two ports is a flow path (arrowheads both ends: both ways), a bar across a port is blocked, a dot where paths meet is ports joined. Two parallel lines drawn along the top and bottom of the row mean a **proportional or servo** valve with infinitely variable positions. A **two-stage** valve is drawn simplified (solenoid-plus-pilot operators on the main squares) or in detail (the pilot 4/3 above the main 4/3 inside an enclosure, showing the internal or external X and Y plugs). Spools are covered in [directional control valves](/article/directional-control-valves-spools-and-solenoids).

![Directional valve envelopes and the common centre conditions](/img/drawings/hyd-dcv-sheet.svg)

*Directional valve envelopes and the common centre conditions*

Centre conditions of a 4/3, ports P T A B:

| Centre | Drawn as | Load at rest | Pump at rest |
|---|---|---|---|
| Closed | Four bars, every port blocked | Held by the spool, slow drift (a spool always leaks) | Dead-headed: over the relief on a fixed pump (heat), destroked on a compensated pump |
| Open | All four ports joined at a dot | Free: a hanging load drifts, a motor freewheels | Unloaded to tank, cool |
| Tandem | P joined to T, A and B blocked | Held by the spool | Unloaded through the centre; valves can run in series |
| Float | P blocked, A and B joined to T | Actuator floats, a motor coasts without cavitating | Dead-headed |
| Regenerative | P joined to A and B, T blocked | Extends fast at reduced force: rod-end oil rejoins the cap end | Working at pressure |
| Partly open | Read the arrows | Special sequences, motor brakes | Trust the maker's spool code |

## Valve operators

Operators touch the end of the row. A spring at the other end means the operator works against it; springs at both ends mean spring-centred.

![Valve operators: solenoid, lever, pedal, pilot, spring, detent, proportional](/img/drawings/hyd-operators-sheet.svg)

*Valve operators: solenoid, lever, pedal, pilot, spring, detent, proportional*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Solenoid | Rectangle with one corner-to-corner diagonal | Coil shifts the spool toward this end | One each end on a double-solenoid valve |
| Proportional solenoid | Diagonal plus a slanted arrow through the rectangle | Force varies with current | |
| Manual override | Small manual rectangle drawn on the solenoid | A pin shifts the valve by hand | Know what will move first |
| Lever | Line with a small circle at the pivot and a cross-bar handle | Hand lever | Mobile banks |
| Push button | Stem ending in a flat cap | Momentary button | |
| Pedal | Angled foot shape on a stem | Foot operated | Presses |
| Roller (cam) | Stem ending in a small circle | Cam or slide rolls over it, both directions | A roller on a pivoted arm works one way only |
| Spring | Zigzag on the envelope end | Returns the valve on release | |
| Detent | Saw-tooth notches along the envelope edge, one per position | Stays put with no power | Holds through a power loss |
| Pilot pressure | Small solid triangle on the end with a dashed line to the source | Pressure shifts the valve | Triangles both ends: pilot both sides; hollow for air |
| Solenoid plus pilot | Solenoid rectangle then a pilot triangle on the same end | Solenoid-controlled, pilot-operated | Needs 50-150 psi minimum pilot |

## Check, shuttle and pilot-operated check valves

![Check, spring check, pilot-operated check, shuttle and restrictor check](/img/drawings/hyd-check-valves-sheet.svg)

*Check, spring check, pilot-operated check, shuttle and restrictor check*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Check valve | Small circle (ball) in a V (seat) in the line | Free flow in the direction that lifts the ball off the seat (from the point of the V toward the ball); blocked the other way | No spring: opens at almost zero |
| Spring-loaded check | Zigzag spring behind the ball | Opens above its cracking pressure, 5-65 psi (0.35-4.5 bar) | A 65 psi check in a return line is a back-pressure valve |
| Pilot-operated check, pilot to open | Dashed pilot ending in a triangle pushing against the ball | Pressure from the other work line lifts the ball so the load can lower | Ratio 3:1 or 4:1 beside it; a short-dash drain if the return has back-pressure |
| Pilot-operated check, pilot to close | Dashed pilot pushes the ball onto the seat | Pilot blocks the free-flow direction | Less common |
| Dual POC (lock valve) | Two POCs in one enclosure, each piloted from the other line | Locks a cylinder both ways | Pressure stays trapped after shutdown |
| Shuttle valve | Rectangle, inlet each end, outlet in the middle, ball between two seats | Outlet sees the higher inlet (OR) | LS signals, brake circuits |

## Pressure control valves

All pressure valves share one convention: one square; an arrow inside for the flow path; a zigzag spring on one side (slanted arrow through it: adjustable); a dashed pilot on the other side showing **which pressure** works against the spring. Arrow drawn **offset** from the ports: **normally closed** (relief, sequence, counterbalance, unloading), pilot pressure pushes it into line to open. Arrow **in line** with the ports: **normally open** (reducing), pilot pushes it out of line to throttle. Where the pilot comes from and where the outlet goes is the whole difference. Settings are in [pressure and flow control valves in depth](/article/pressure-and-flow-control-valves-in-depth).

![Relief, reducing, sequence, counterbalance, unloading and brake valves](/img/drawings/hyd-pressure-valves-sheet.svg)

*Relief, reducing, sequence, counterbalance, unloading and brake valves*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Relief, direct-acting | Normally closed; pilot from the **inlet**; outlet to a tank symbol | Opens to tank at the setting | Set 10-15% above working pressure |
| Relief, pilot-operated | Main square with a small pilot relief square and a **vent port** (dashed, labelled V or X) | Pilot stage sets the pressure; venting the port drops the main stage to 25-75 psi (2-5 bar) | How a solenoid unloads a pump |
| Pressure reducing | Normally **open**; pilot from the **outlet**; short-dash drain from the spring chamber; outlet to the circuit | Holds downstream pressure whatever the upstream | The only normally open one; drain must be free |
| Sequence | Normally closed; pilot from the inlet; **external drain**; outlet to a second circuit; bypass check in parallel | Feeds the second operation when the first reaches pressure | Clamp then press |
| Counterbalance | Normally closed; dashed pilot from the **opposite work line**; reverse check in parallel; ratio (3:1, 4.5:1) beside it | Holds a hanging load, lets it down only under drive pressure | Never removed to cure a slow lower |
| Unloading | Normally closed; pilot from a **remote** line (accumulator, second pump); outlet to tank | Dumps a pump when the remote pressure is reached | Hi-lo circuits |
| Brake valve | Counterbalance with two pilots: internal from the inlet (high setting), external from the other line (low) | Holds and brakes a motor load, opens easily under drive | Winch and travel motors |

## Flow control valves

![Flow controls: fixed, adjustable, compensated, with bypass check, flow divider](/img/drawings/hyd-flow-valves-sheet.svg)

*Flow controls: fixed, adjustable, compensated, with bypass check, flow divider*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Fixed orifice | Two short arcs facing each other narrowing the line | Fixed restriction | Flow varies with pressure drop and viscosity |
| Adjustable throttle | The arcs with a slanted arrow | Needle valve; flow still changes with load | The cheap flow control |
| Pressure-compensated | Throttle inside a rectangle with a small normally open compensator square, spring and pilots before and after the throttle | Constant flow regardless of load | Set with the machine loaded |
| Temperature-compensated | Adds a small thermometer (stem and bulb) | Corrects for viscosity | Precision feeds |
| With reverse check | Check in parallel around the throttle | Metered one way, free the other | The standard cylinder speed control |
| Flow divider | One inlet, two outlets each through a throttle linked by a bar (spool) or two motor circles on one shaft (rotary) | Splits flow in a fixed ratio | Synchronising cylinders |

## Accumulators, filters, coolers and conditioning

![Accumulators, filters with bypass, water separator, cooler, heater, breather](/img/drawings/hyd-conditioning-sheet.svg)

*Accumulators, filters with bypass, water separator, cooler, heater, breather*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Gas-charged accumulator | Tall capsule, one port at the bottom, divided by a curved line (bladder) or a straight line (piston), a small hollow triangle in the gas half | Nitrogen precharge over a separator | Precharge beside it; see [accumulator precharge](/article/accumulator-precharge-and-safety) |
| Spring-loaded accumulator | Zigzag inside the capsule | Spring stores the energy | Rare |
| Weight-loaded accumulator | Rectangle (weight) inside the capsule | Constant pressure from a mass | Old presses |
| Filter | Diamond with a dashed line across it perpendicular to the flow | Removes particles | Suction, pressure, return, off-line |
| Filter with bypass | Diamond with a spring-loaded check in parallel | Bypasses when blocked, 25-50 psi (1.7-3.5 bar) | A bypassed filter passes dirt |
| Filter with clogging indicator | Diamond with a small gauge or pressure switch across it | Dirty-element signal | Change on the indicator, not the calendar |
| Breather | Small diamond with a dashed line on a stub open to air | Filters the air the tank breathes | Desiccant type in wet plants |
| Cooler | Diamond with two arrows pointing **out** | Removes heat | Water or fan lines added |
| Heater | Diamond with two arrows pointing **in** | Adds heat for cold starts | |
| Temperature controller | Diamond with arrows both ways | Heats or cools to a set point | |

## Gauges, switches, sensors and connections

![Gauges, flow meters, pressure switches, quick disconnects, rotary joints, enclosures](/img/drawings/hyd-instruments-sheet.svg)

*Gauges, flow meters, pressure switches, quick disconnects, rotary joints, enclosures*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Pressure gauge | Circle with a short pointer arrow, on a stub | Pressure at that point | A circle with a thermometer is a temperature gauge |
| Flow meter | Circle in the line with a small arrow inside | Flow rate | Totaliser adds a small box |
| Pressure switch | Square with a spring one side, dashed pilot the other, an electrical contact inside and a zigzag electric arrow | Contact changes at the set pressure | Set point and deadband beside it |
| Level switch | Float (circle on a stem) with a contact | Low-oil shutdown | |
| Temperature switch | Thermometer with a contact | Hot-oil trip, 140-160 F (60-70 C) | |
| Transducer | Square with a pilot in and a signal arrow leaving | 4-20 mA or 0-10 V out | See [PLC awareness](/article/plc-and-instrumentation-awareness) |
| Quick disconnect, uncoupled | Two facing open half-symbols drawn apart; a check ball in each half if self-sealing | Halves separated | Pressure trapped on the hose side |
| Quick disconnect, coupled | The halves joined with a small circle at the joint | Connected | |
| Rotary joint | Circle around the line with an arc arrow | Swivel | Hose reels, slewing rings |
| Test point | Short stub ending in a small circle with a cap | Minimess or Stauff port | Gauge on without opening the line |
| Cartridge (logic) valve | Rectangle cavity with a cone poppet in a seat, spring and pilot area at the top, ports A and B, an X pilot line | Two-way poppet controlled by a pilot valve | Area ratio beside it; see [cartridge and logic valves](/article/cartridge-and-logic-valves) |
| Manifold | Chain-line enclosure with port letters on the boundary | One block carries the valves | Block drawing is a separate sheet |

**ISO 1219-2 numbering.** Each component carries the circuit number, a letter and a running number: **1P1** pump 1 of circuit 1, **1A1** an actuator, **1V1**, **1V2** valves, **1S1** a sensor or switch, **1Z1** an accessory (filter, gauge, cooler). Circuit 0 is the supply unit (0P1 the main pump, 0Z1 the return filter). The component list uses the same codes with model numbers and settings. Older US sheets use tags (PMP-1, RV-1, DCV-3).

**Differences from older ANSI and JIC symbols.** ISO 1219 grew from the JIC and ANSI Y32.10 symbols, so a 1970 sheet reads much like a 2020 one. Watch for: a **loop at a crossing** (not connected) where ISO uses a plain crossing; pilot and drain drawn with the same dash; a reservoir under every return line instead of once; pneumatic ports lettered P, A, B, R, S where ISO numbers them 1, 2, 4, 3, 5; a solenoid drawn as a plain rectangle with no diagonal; and two-stage valves drawn in full where ISO allows a simplified symbol. Whichever family the sheet uses, its **legend sheet** governs: read it first.

## Common mistakes

- Reading a valve in its energised state; the lines are always drawn on the rest envelope.
- Taking the slanted arrow through a pump as a flow direction: it means variable, the triangle is the flow.
- Mixing up the pump triangle (points out) and the motor triangle (points in).
- Missing a short-dash drain line and plugging that manifold port: the valve will not shift.
- Reading relief and reducing valves as the same symbol: the reducing valve's arrow is in line with the ports and its pilot comes from downstream.
- Assuming a check flows in the direction the line runs on the page: the ball and seat decide.
- Looking for external ports on a manifold that the enclosure line says are internal.
- Treating an old JIC loop at a crossing as a junction.
- Trusting a closed-centre spool to hold a load: without a POC or counterbalance it drifts.

## Related

- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
- [Reading hydraulic and pneumatic circuit diagrams](/article/reading-hydraulic-and-pneumatic-circuit-diagrams)
- [Pneumatic symbols and circuit reading](/article/pneumatic-symbols-and-circuit-reading)
- [Directional control valves, spools and solenoids](/article/directional-control-valves-spools-and-solenoids)
- [Pressure and flow control valves in depth](/article/pressure-and-flow-control-valves-in-depth)
- [Cartridge and logic valves](/article/cartridge-and-logic-valves)
- [Accumulator precharge and safety](/article/accumulator-precharge-and-safety)
- [Quiz: drawings, schematics and P&IDs](/article/quiz-drawings-schematics-and-pids)
