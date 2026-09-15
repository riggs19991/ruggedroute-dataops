---
title: "Electrical Symbols, NEMA/JIC and IEC Side by Side: the Two Symbol Families, Contacts and Coils (NO, NC, Timed, Overload), Pushbuttons, Selector Switches and Pilot Lights, Process-Driven Switches (Limit, Proximity, Photoelectric, Float, Pressure, Temperature, Flow, Speed), Power Devices (Contactors, Overloads, Fuses, Breakers, Disconnects), Transformers, Motors and Solenoids, Wires, Terminals and Grounds, PLC and Drive Symbols, and the 1CR / -K1 Device Designations"
slug: electrical-symbols-nema-and-iec
category: drawings
kind: chart
tags: [electrical symbols, nema symbols, jic symbols, iec 60617, ieee 315, control schematic symbols, ladder diagram symbols, normally open contact, normally closed contact, relay coil symbol, timed contact, on delay, off delay, overload contact, pushbutton symbol, emergency stop symbol, selector switch symbol, target table, pilot light symbol, push to test, limit switch symbol, held closed, proximity switch symbol, photoelectric symbol, float switch symbol, pressure switch symbol, temperature switch symbol, flow switch symbol, zero speed switch, contactor symbol, overload relay symbol, fuse symbol, circuit breaker symbol, disconnect symbol, control transformer symbol, motor symbol, solenoid symbol, wire junction dot, terminal symbol, ground symbol, shielded cable, plc input symbol, vfd symbol, safety relay symbol, device designations]
source: "NEMA ICS 19-2002 (industrial control and systems: diagrams, device designations and symbols); JIC EMP-1 electrical standards for industrial equipment; IEEE 315 / ANSI Y32.2 (graphic symbols for electrical and electronics diagrams); IEC 60617 (graphical symbols for diagrams); IEC 61346 and IEC 81346 (reference designation letter codes); NFPA 79 (electrical standard for industrial machinery, drawing and marking practice); Allen-Bradley, Square D and Siemens starter and control wiring publications."
summary: "One chart of the symbols on a machine's electrical schematic, with the North American NEMA/JIC drawing and the IEC 60617 drawing of each described side by side so you can read either sheet: contacts and coils including timed and overload contacts, the operator devices, the process switches, the power devices from disconnect to motor, wiring conventions, how PLC points, drives and safety relays appear, and the device designation systems (1CR, 2M, 1OL and -K1, -Q1, -F1). Reading the drawing is the millwright's job; testing it live is the electrician's."
---

A motor control schematic is a map of what has to be true for the machine to run, and a millwright who can read it walks up to a dead machine knowing which pushbutton, limit switch or overload to look at. Reading the sheet, and the mechanical checks it points you to, are yours. Opening an energised panel and putting a meter on it belongs to the qualified electrician: see [electrical safety for mechanics](/article/electrical-safety-for-mechanics) and [lockout basics](/article/lockout-tagout-basics). How the symbols assemble into starters is in [motor control schematics and wiring diagrams](/article/motor-control-schematics-and-wiring-diagrams).

## Two symbol families

- **NEMA / JIC** (NEMA ICS 19, JIC EMP-1, IEEE 315 / ANSI Y32.2): the North American style. Contacts are two short parallel lines, coils are circles, devices are named by number-and-letters (1CR, 2M, 1LS) and the schematic is drawn as a **ladder** between vertical L1 and L2 rails with rungs numbered down the left.
- **IEC 60617**: the European style, used on imported machines and increasingly on new North American ones. Contacts are a gate (a hinged line), coils are rectangles, devices are named by a letter code and a number with a hyphen (-K1, -Q1, -S1), contacts carry standard terminal numbers (13-14 NO, 21-22 NC, A1-A2 coil), and the sheet is drawn with horizontal power rails and vertical current paths numbered across the top.
- Canada and CSA-listed machines accept either; NFPA 79 and UL 508A (the US industrial machinery and panel standards) allow either family provided the sheet has a legend. The **legend sheet** is where you check any symbol you are not sure of.

Every row below describes the NEMA/JIC drawing first and the IEC drawing second.

## Contacts and coils

![Contacts, coils, timed contacts and overload contact in NEMA and IEC form](/img/drawings/elec-contacts-coils-sheet.svg)

*Contacts, coils, timed contacts and overload contact in NEMA and IEC form*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Normally open (NO) contact | NEMA: two short parallel vertical lines with a gap between them in the wire. IEC: the wire broken, with a short angled line (a gate) leaning toward but not touching the far side | Open with the coil de-energised, closes when energised | Drawn de-energised, as everything on the sheet |
| Normally closed (NC) contact | NEMA: the two parallel lines with a diagonal slash through them. IEC: the gate line crosses and overshoots the far side | Closed at rest, opens when energised | IEC terminals 21-22, 31-32; NEMA marks the device name beside it |
| Relay coil | NEMA: a circle with the designation inside (CR, M, TR). IEC: a rectangle with the designation beside it (-K1) and terminals A1, A2 | The electromagnet that operates the contacts | The rung's load; its contacts are elsewhere with a cross-reference |
| Contactor coil | NEMA: circle with M, F, R, 1M. IEC: rectangle -K1 or -Q1 | Operates power contacts | See power devices |
| On-delay timed contact (NOTC, NCTO) | NEMA: a contact with a small **arrow pointing up** (or an arc under it). IEC: the contact with a small half-circle (a parachute) on the moving part | Contact acts a set time **after** the coil is energised; releases at once when de-energised | Timer TR; NOTC = normally open, timed closed; NCTO = normally closed, timed open |
| Off-delay timed contact (NOTO, NCTC) | NEMA: contact with a small **arrow pointing down**. IEC: the parachute drawn the other way up | Contact acts at once on energising and releases a set time **after** de-energising | Check the parachute's direction against the legend; it is easy to reverse |
| Thermal overload contact | NEMA: an NC contact with a small rounded hump, marked OL. IEC: an NC contact next to a small rectangle with a bimetal symbol, -F1 terminals 95-96 | Opens when the overload heaters trip | The last thing in series before the starter coil; reset on the overload relay |

## Pushbuttons, selectors and pilot lights

![Pushbuttons, selectors, pilot lights and the target table](/img/drawings/elec-operators-sheet.svg)

![Pushbuttons, selector switches and pilot lights on a real panel door](/photos/drawings/pushbutton-panel.jpg)

*Pushbuttons, selector switches and pilot lights on a real panel door. Photo: Dietmar Rabich, CC BY-SA 4.0, via commons*

*Pushbuttons, selectors, pilot lights and the target table*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Momentary NO pushbutton | NEMA: two terminal dots with a bar **above** them not touching, and a button stem on the bar. IEC: the gate contact with a manual operator: a dashed link to a small T (the button) | Closes while pressed | START |
| Momentary NC pushbutton | NEMA: the bar **touching under** the dots, stem on top. IEC: NC gate with the button operator | Opens while pressed | STOP; always NC so a broken wire stops the machine |
| Maintained pushbutton | NEMA: two contacts joined by a dashed mechanical line with a detent mark. IEC: the operator with a latching symbol | Stays where it was pushed | |
| Mushroom head (emergency stop) | NEMA: the bar drawn with a downward-curved cap (a mushroom) on the stem, NC. IEC: NC gate with a mushroom head and a latch symbol, marked -S0 or E-STOP | Latches open when struck, twist or pull to reset | Usually two NC contacts to a safety relay |
| Illuminated pushbutton | The button symbol joined to a pilot light circle | Button with a lamp | |
| Two-position selector switch | NEMA: a pivot dot with a lever line to one of two contact positions, plus a **target table** under it: rows for each contact, columns for the positions (HAND, AUTO), an X where the contact is closed. IEC: a rotary operator (a line with a small knob) with contacts and a position table | Which contacts are closed in each position | The table, not the picture, tells you the state |
| Three-position selector | Same with three positions (HAND-OFF-AUTO) | | Spring-return positions marked with an arrow |
| Foot switch | NEMA: contact with a pedal (an angled shape) on a stem. IEC: gate with a foot-pedal operator | Foot operated, NO or NC | Presses, with a guard |
| Pilot light | NEMA: a circle with the colour letter inside: **R** red, **G** green, **A** amber, **W** white, **B** blue. IEC: a circle with an X and colour code RD, GN, YE, WH, BU | Indicator lamp | Red = fault or stop, amber = warning, green = running, blue = action required, white = power on |
| Push-to-test pilot light | The lamp circle with a pushbutton symbol attached | Pressing lights the lamp from the supply to prove the bulb | A dark lamp that lights on test is a real signal, not a bulb |

## Switches driven by the process

These are inputs the machine makes for itself; most of a millwright's sensor work (mounting, gap, alignment) is on them. Detail in [PLC and instrumentation awareness](/article/plc-and-instrumentation-awareness).

![Limit, pressure, temperature, flow, float, proximity, speed and foot switches](/img/drawings/elec-process-switches-sheet.svg)

*Limit, pressure, temperature, flow, float, proximity, speed and foot switches*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Limit switch, NO | NEMA: a terminal dot with an angled arm above it, not touching (a chair shape), marked LS. IEC: gate contact with a mechanical operator (a small triangle or a roller on a lever) | Closes when the machine part strikes it | |
| Limit switch, NC | NEMA: the arm touching the terminal, drawn with the contact through it | Opens when struck | Safety and over-travel use NC |
| Limit switch, NO held closed | NEMA: the NO symbol drawn with the arm pushed down onto the contact | An NO switch that the machine holds actuated at rest (e.g. a guard closed) | Drawn in its held state, with a note |
| Limit switch, NC held open | NEMA: the NC symbol drawn with the arm lifted off | An NC switch held actuated at rest | The two held symbols are the commonest misreads on a sheet |
| Proximity switch, inductive | NEMA: a contact with a diamond above it marked PRS or PROX, or a rectangle labelled PROX with the output. IEC: a rectangle with a small diamond and Fe (iron) inside, the contact beside it | Senses metal within a few mm | PNP/NPN and NO/NC written beside it |
| Proximity switch, capacitive | Same with a C or a capacitor mark in the diamond | Senses anything | |
| Photoelectric switch | NEMA: contact with two small arrows (light) pointing at it, marked PE or PEC; through-beam draws a source and a receiver. IEC: rectangle with a light-arrow symbol | Beam made or broken | Light-on / dark-on noted |
| Float (level) switch | NEMA: contact with a small circle (a ball float) on a lever, marked FS or LS. IEC: gate with a float operator | Level high or low | |
| Pressure switch | NEMA: contact with a half-circle (a diaphragm or bellows) under it, marked PS. IEC: gate with a pressure operator (a small bell or the letter p) | Pressure above or below set point | Set point on the sheet |
| Temperature switch | NEMA: contact with a bent line (a bimetal) or a thermometer under it, marked TS or TAS. IEC: gate with a temperature operator (a theta or a thermometer) | Temperature above or below set point | Motor winding thermostats are drawn here |
| Flow switch | NEMA: contact with a small flag (a paddle) under it, marked FLS. IEC: gate with a flow operator | Flow present or not | |
| Speed (zero-speed, plugging) switch | NEMA: contact with a small circle and the letters ZS or PLS, sometimes a centrifugal weight symbol. IEC: gate with an n (speed) operator | Shaft turning or stopped | Conveyor tail pulleys, plugging stops |

## Power devices: contactors, overloads, fuses, breakers, disconnects

![Contactor poles, overload heaters, fuses, breakers, disconnects, transformers, motors](/img/drawings/elec-power-devices-sheet.svg)

![An overload relay with its trip setting dial and reset button](/photos/drawings/overload-relay.jpg)

*An overload relay with its trip setting dial and reset button. Photo: Mik81, Public domain, via commons*

*Contactor poles, overload heaters, fuses, breakers, disconnects, transformers, motors*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Contactor (starter) | NEMA: three NO power contacts in L1, L2, L3, each marked M, and the coil M in the control circuit. IEC: three gate contacts with a dashed mechanical link, terminals 1-2, 3-4, 5-6, coil -K1 or -Q1 | Switches the motor | The auxiliary contacts (NEMA M, IEC 13-14, 21-22) are separate |
| Overload relay (heaters) | NEMA: three heater elements (a rounded hump or a small square with a wavy line) in T1, T2, T3, marked OL; electronic type as a rectangle with a current setting. IEC: rectangle -F with three bimetal symbols, terminals 1-6 through, 95-96 NC and 97-98 NO | Trips the NC OL contact on sustained overcurrent | Class 10, 20 or 30 and the FLA setting beside it |
| Fuse | NEMA: a rectangle with the wire passing through it lengthwise (older: an S-shaped wave), marked FU with the size. IEC: rectangle with the line through, -F | Overcurrent protection | Class and amps beside it (e.g. 2FU 3 A KLDR) |
| Circuit breaker, thermal-magnetic | NEMA: a contact drawn as an open switch with a small arc (hump) at the hinge and a hook, marked CB; thermal (a small square) and magnetic (a small curve) trip elements shown. IEC: gate contact with an X on the moving line, plus release symbols: a small rectangle (thermal) and a chevron (magnetic), -Q | Trips on overload and short circuit | Frame and trip rating beside it |
| Motor circuit protector (MCP) | Breaker with the magnetic element only, marked MCP with the instantaneous trip setting | Short-circuit protection only; the overload relay does the rest | Instantaneous trip set by the electrician |
| Disconnect switch | NEMA: three open knife-blade switches with a dashed link, marked DISC or DS. IEC: three gate contacts with a short bar at the tip (isolator), -Q | Isolates the circuit for lockout | The handle you lock |

## Transformers, motors and solenoids

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Control power transformer (CPT) | NEMA: two coils (rows of bumps) facing each other with two parallel lines (the core) between; primary terminals H1-H4, secondary X1, X2; a fuse on X1; X2 to a ground symbol. IEC: two overlapping circles, -T1 | Steps 480 or 600 V down to 120 V control | X2 grounded and X1 fused is the NFPA 79 arrangement |
| Motor | NEMA: a circle with MTR or M and the hp, T1-T2-T3 leads, marked 3 phase (or 1 phase). IEC: circle with M and 3 tilde (1 tilde single-phase), -M1 | The load | Nameplate data beside it; see [reading a motor nameplate](/article/reading-a-motor-nameplate) |
| Solenoid (valve coil) | NEMA: a zigzag coil (like a spring) or a rectangle, marked SOL. IEC: rectangle with a diagonal line, -Y1 | Operates a hydraulic or pneumatic valve | The same diagonal as the ISO 1219 solenoid symbol |
| Brake coil | NEMA: coil marked BR or BRK; IEC: -Y with a brake-shoe symbol | Spring-set brake released by the coil | Coil off = brake on |
| Heater (resistance) | NEMA: a rectangle or zigzag marked HTR. IEC: rectangle -E | Space heater, trace heating | |
| Horn, bell, beacon | NEMA: a horn (a trumpet shape), a bell (a half-circle), a lamp with rays. IEC: -H with the same shapes | Alarms | |

## Wires, terminals and grounds

![Junctions, crossings, terminals, wire numbers, grounds, shields and sources](/img/drawings/elec-wires-terminals-sheet.svg)

![Terminal blocks and relays on DIN rail, each with its wire numbers](/photos/drawings/din-rail-devices.jpg)

*Terminal blocks and relays on DIN rail, each with its wire numbers. Photo: Retired electrician, CC0, via commons*

*Junctions, crossings, terminals, wire numbers, grounds, shields and sources*

| Symbol | How it is drawn | Meaning | Notes |
|---|---|---|---|
| Junction | A solid dot where wires meet | Connected | |
| Crossing | Wires cross with no dot; old JIC sheets draw a small loop (hop) | Not connected | NEMA ICS 19 allows either style; never assume |
| Terminal | A small circle with the terminal number, on the wire; a terminal strip is a row of them marked TB1 | A screw terminal in the panel or a box | Field wiring lands here; the number is on the strip |
| Wire number | A number printed on the wire, changing at every device | The wire's identity on both ends | Ferrules on the real wire carry the same number |
| Ground (earth) | Three horizontal lines of decreasing length (NEMA and IEC) | Connected to the grounding electrode system | X2, the panel, motor frames |
| Chassis (frame) ground | A short line with three diagonal strokes (a rake) | Bonded to the enclosure | |
| Shielded cable | A dashed ellipse or a dashed line around the conductors, with the shield taken to ground at one end | Screened cable for analog and encoder signals | Ground the shield at one end only, usually the drive or PLC end |

## PLC and drive symbols on a schematic

![PLC input and output points, VFD block, safety relay and dual-channel E-stop](/img/drawings/elec-plc-drive-sheet.svg)

*PLC input and output points, VFD block, safety relay and dual-channel E-stop*

- **PLC input**: each point is a small square or a terminal on a rectangle labelled with the card and address. Allen-Bradley SLC and MicroLogix style: **I:1/0** (slot 1, point 0), outputs **O:2/3**; ControlLogix: **Local:1:I.Data.0**; IEC 61131 and Siemens style: **%I0.0** and **%Q0.0**. The field device is drawn on the rung feeding the point, with its wire number and the 24 V DC or 120 V AC common.
- **PLC output**: the point on the output card feeding a load (a relay coil CR, a solenoid, a pilot light), usually through an interposing relay for anything bigger than 2 A.
- **VFD**: a rectangle with power terminals L1-L3 (R, S, T) in, T1-T3 (U, V, W) to the motor, DC bus terminals (+, -), a braking resistor if fitted, and a control terminal strip: digital inputs (run/stop, forward/reverse, jog, preset speeds, fault reset), a common, an analog speed reference (0-10 V or 4-20 mA with a 10 V reference terminal), a relay output for RUN and FAULT, and two **STO** (safe torque off) terminals to the safety relay. See [VFD basics](/article/vfd-basics-for-millwrights).
- **Safety relay**: a rectangle marked SR or -K with A1/A2 power, two input channels (S11-S12, S21-S22) from the E-stop and guard NC contacts, a reset input (S33-S34) from the reset button, and safety outputs (13-14, 23-24) in series with the starter coils or the STO. Two channels and monitored reset are what make it a safety circuit.
- **E-stop circuit**: every E-stop drawn as a two-contact mushroom head in series on both channels; a light curtain or a safety mat appears as a rectangle with OSSD outputs into the same channels.
- **Encoder, transmitter**: a rectangle with the signal type (A, B, Z pulses; 4-20 mA) on a shielded cable.

**Device designations.** NEMA/JIC: a number and letters: **1CR** control relay 1, **2M** motor contactor 2, **1OL** overload relay, **1LS** limit switch, **1PB** pushbutton (STOP is often 1PB, START 2PB), **1SOL** solenoid, **1PL** pilot light, **1SS** selector switch, **1PS** pressure switch, **1FS** flow or float switch, **1TS** temperature switch, **1TR** timer, **1CPT** control transformer, **1FU** fuse, **1CB** breaker, **1DISC** disconnect, **F** and **R** forward and reverse. IEC 61346 / 81346: a class letter and a number with a hyphen: **-K1** relay or contactor, **-Q1** breaker or disconnect (a contactor on some sets), **-F1** fuse or overload, **-S1** switch or pushbutton, **-M1** motor, **-T1** transformer, **-H1** lamp or horn, **-Y1** solenoid or brake, **-B1** sensor, **-X1** terminal strip, **-U1** drive, **-G1** power supply, **-A1** PLC or assembly. IEC 81346 revised some letters, but the 61346 set is what most sheets use. The designation on the drawing must match the label on the device and the ferrule on the wire; if it does not, someone changed something without updating the sheet.

## Common mistakes

- Reading an IEC NC gate as an NO because the line is angled: NC crosses the far side, NO stops short.
- Taking a limit switch drawn held closed as an NC switch and looking for the wrong wire.
- Mistaking the up and down arrows on timed contacts: up is on-delay, down is off-delay on NEMA sheets; check the legend on IEC sheets.
- Treating a loop at a wire crossing on an old sheet as a junction, or a dotless crossing on a new sheet as unconnected when a junction dot was simply forgotten (check the wire numbers).
- Reading the selector switch picture instead of its target table.
- Assuming a red pilot light means running: on NFPA 79 and IEC sheets red is fault or stop, green is normal.
- Confusing the overload heaters in the power circuit with the OL contact in the control circuit: the contact is what stops the coil.
- Assuming -Q1 is always a breaker; on some sets it is the contactor. The legend decides.
- Reading the drawing correctly and then opening a live panel to check it: reading is yours, testing is the electrician's.

## Related

- [Motor control schematics and wiring diagrams](/article/motor-control-schematics-and-wiring-diagrams)
- [Electrical safety for mechanics](/article/electrical-safety-for-mechanics)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [PLC and instrumentation awareness](/article/plc-and-instrumentation-awareness)
- [VFD basics for millwrights](/article/vfd-basics-for-millwrights)
- [Reading a motor nameplate](/article/reading-a-motor-nameplate)
- [Hydraulic symbols, ISO 1219 complete chart](/article/hydraulic-symbols-iso-1219-complete)
- [Quiz: drawings, schematics and P&IDs](/article/quiz-drawings-schematics-and-pids)
