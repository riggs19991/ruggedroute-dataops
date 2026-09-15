---
title: "PFD and P&ID Reading for Millwrights: Process Flow Diagram versus P&ID, the Legend Sheet, Anatomy of a P&ID Sheet, Line Numbers, Spec Breaks and Insulation Codes, Equipment Tags and the Equipment List, Tracing a Line End to End, Reading a Pump Loop in Order, Instrument Bubbles and Control Loops, Off-Page Connectors, Tie-Ins and Holds, and What a Millwright Pulls off a P&ID for Isolation and Equipment Work"
slug: pfd-and-pid-reading
category: drawings
kind: reference
tags: [P&ID, PID reading, piping and instrumentation diagram, PFD, process flow diagram, legend sheet, lead sheet, line number, spec break, insulation code, tracing code, equipment tag, equipment list, pump tag, tracing a line, pump loop, suction strainer, check valve, minimum flow, recirculation, seal flush plan, spare pump, instrument bubble, control loop, off-page connector, tie-in point, hold, cloud, by others, double block and bleed, spectacle blind, drain, vent, bypass, normally closed, normally open, locked open, car seal, LOTO isolation, walk-down, redline, as-built, stream number]
source: "ISA-5.1-2009 instrumentation symbols and identification; ISA-5.3 graphic symbols for distributed control and shared display instrumentation; ISA-5.4 instrument loop diagrams; PIP PIC001 piping and instrumentation diagram documentation criteria (line numbering, equipment tagging, P&ID content); ISO 10628 diagrams for the chemical and petrochemical industry (flow diagram content); ISO 14617 graphical symbols for diagrams; ASME B31.3 process piping; company legend sheets and equipment lists."
summary: "What a process flow diagram shows and what only the P&ID shows, why the legend sheet is read first, how a P&ID sheet is laid out, how to break down line numbers, spec breaks and insulation codes, how equipment tags are built, a method for tracing a line from nozzle to nozzle, a pump loop read valve by valve in order, instrument bubbles and loops at overview level, off-page connectors, tie-ins, holds and clouds, and the isolation, drain, vent, bypass, valve-position and nozzle information a millwright takes off the sheet before opening anything."
---

The P&ID is the drawing you read before you isolate a pump, open a flange or ask what a line carries. It has no dimensions and no scale; it shows every pipe, valve and instrument in a system and how they connect, which is exactly what a millwright needs for lockout, drain-down and pulling equipment. The symbols themselves are charted in [P&ID symbols](/article/pid-symbols-valves-equipment-and-lines) and the instrument letters in [ISA instrument tags](/article/isa-instrument-tags-bubbles-and-letters).

## PFD versus P&ID

The **process flow diagram (PFD)** is the overview a process engineer draws first. The **piping and instrumentation diagram (P&ID)** is the detailed sheet everyone else works from.

![A P&ID sheet: equipment, lines, valves and instrument bubbles on one page](/photos/drawings/pid-sheet.jpg)

*A P&ID sheet: equipment, lines, valves and instrument bubbles on one page. Photo: Ub, CC BY-SA 3.0, via commons*

![The same pump on a PFD and on a P&ID](/img/drawings/pfd-vs-pid.svg)

*The same pump on a PFD and on a P&ID*

| | PFD | P&ID |
|---|---|---|
| Purpose | Explains the process | Defines every piece of hardware |
| Equipment | Major items only (pumps, vessels, exchangers, columns), with duty and size | Every item including spares, with tag and nozzles |
| Lines | Main process streams, each with a **stream number** in a diamond or box | Every line: process, utility, drain, vent, relief, sample; with full line number |
| Valves | None, or control valves only | Every valve, with type, size and normal position |
| Instruments | Main control loops only | Every instrument, switch, alarm and interlock |
| Data | **Heat and material balance** table: flow, temperature, pressure, composition per stream; operating conditions on equipment | Line size, spec, insulation, set pressures, notes |

Use the PFD to understand what the plant does: stream 12 at 180 F (82 C) and 60 psig (4 bar) tells you what to expect when the flange opens. Use the P&ID for everything you actually touch. Canadian and ISO plants draw both to ISO 10628 and ISO 14617 with the same content and a few different symbols.

## The legend sheet

Every P&ID set opens with one or more **legend sheets** (lead sheets): the key that says how this company draws a gate valve, what its line number means and what every abbreviation stands for. Read it first on any new site; a symbol you know from the last plant may mean something else here.

![Legend sheet extract: lines, valves, instrument locations and abbreviations](/img/drawings/pid-legend-extract.svg)

*Legend sheet extract: lines, valves, instrument locations and abbreviations*

On the legend you will find: valve, equipment and instrument symbols; line types; line number format and service codes; spec class list; insulation and tracing codes; equipment tag prefixes; abbreviations (**NC**, **NO**, **LO**, **LC**, **CSO**, **CSC**, **FC**, **FO**); the off-page connector format; note and hold conventions; and the status stamps (**IFR** issued for review, **IFC** for construction, **AB** as-built).

## Anatomy of a P&ID

A P&ID sheet has a title block like any other drawing (number, sheet, revision, unit, title). Inside:

![Sample P&ID of a feed pump loop with tank, pumps, header, control valve and min-flow line](/img/drawings/sample-pid-pump-loop.svg)

*Sample P&ID of a feed pump loop with tank, pumps, header, control valve and min-flow line*

- **Flow runs left to right** where possible; inlets enter at the left border, outlets leave at the right, utilities from the top or bottom.
- **Equipment** is drawn in outline, roughly to relative elevation (a pump low, a tank high), with its tag and a **title line** (name, size or duty, design conditions) in the top or bottom margin.
- **Lines** are heavy for the main process, lighter for utilities, with the line number beside each and an arrow for flow. Lines cross without connecting unless there is a junction dot or a jump loop.
- **Valves** are drawn in the line at roughly their real position with their size if it differs from the line, and their tag if they have one.
- **Instruments** are bubbles connected to the process by a thin line, with signal lines between them; **notes** are numbered in the margin and referenced by a number in a triangle.

## Line numbers, spec breaks and insulation

A line number on the P&ID has the same parts as on the isometric: **6"-CWS-1501-A1A-IH** is size, service, sequence, spec class and insulation code (worked through in [piping isometrics](/article/piping-drawings-isometrics-and-spool-sheets)). On the P&ID the number is written along the line and changes whenever the size, service or spec changes; a **reducer** symbol (a small trapezoid) marks a size change and the new size appears after it.

![Line number decoder: size, service, sequence, spec and insulation](/img/drawings/line-number-decoder.svg)

*Line number decoder: size, service, sequence, spec and insulation*

A **spec break** is drawn as a short bar across the line, sometimes as a small vertical bar with a dot, with the spec class written on each side (**A1A / D2A**). It marks where the material or rating changes (a valve between a Class 150 utility and a Class 300 process line, a vendor package boundary, the first flange downstream of a control valve) and tells you which class of flange, gasket and bolts sits at that joint.

Insulation and tracing codes sit at the end of the line number or in a separate box on the line: **IH** heat conservation, **IC** cold insulation, **IP** personnel protection (usually to 7 ft, 2.1 m, above grade), **IS** safety, **N** or blank none; **ET** or **ST** electric or steam tracing, sometimes drawn as a thin line hugging the pipe with the tracer number; **J** for a jacketed line. A line marked IP is hot enough to burn, a line marked IC may be badly corroded under the insulation, and a traced line cannot be cut without isolating the tracer.

## Equipment tags

Every piece of equipment has a **tag** made of a letter code, a number and sometimes a suffix: **P-101A**. The letters vary by company but a common set is:

![Equipment tag decoder and common equipment letters](/img/drawings/equipment-tag-decoder.svg)

*Equipment tag decoder and common equipment letters*

| Prefix | Equipment | Prefix | Equipment |
|---|---|---|---|
| **P** | Pump | **K** or **C** | Compressor (K also blower, fan) |
| **T** or **TK** | Tank | **D** or **V** | Drum or vessel |
| **E** or **HE** | Heat exchanger | **F** or **H** | Fired heater or furnace |
| **C** or **T** | Column or tower (check the legend: C and T clash) | **M** | Motor, mixer or mill |
| **AG** or **A** | Agitator | **CV** or **CE** | Conveyor |
| **R** | Reactor | **FL** or **S** | Filter, strainer, separator |
| **PK** or **PKG** | Vendor package | **X** or **Z** | Miscellaneous |

The number carries the unit (**1**) and a sequence, so P-101 is pump 01 in unit 1 and E-301 is exchanger 01 in unit 3. Suffixes **A/B** mark duplicate machines, usually a running pump and an installed spare on the same headers. The **equipment list** is the table behind the tags (description, P&ID number, duty, driver power, materials, design conditions, weight, vendor and model): where you look up the motor horsepower and the weight before rigging a pump out.

## Tracing a line end to end

Reading a P&ID is done one line at a time, with a finger or a highlighter. The method:

![A process diagram with its stream numbers and equipment tags](/photos/drawings/process-diagram-sample.jpg)

*A process diagram with its stream numbers and equipment tags. Photo: Geichler, Public domain, via commons*

![Tracing one line end to end and listing every branch](/img/drawings/tracing-a-line.svg)

*Tracing one line end to end and listing every branch*

1. **Start at a nozzle.** Find the equipment you are working on, pick the nozzle and read the line number leaving it. Write the number down.
2. **Follow the arrows.** Move along the line in the direction of flow (or backwards for a suction line), and at every junction confirm by the line number that you are still on the same line.
3. **Note every item in order**: each valve with its type, size, tag and normal position; each instrument; each reducer, spec break, drain, vent and blind. This is your isolation and drain list.
4. **Handle branches.** At a tee, note the branch line number and whether it is a small-bore drain, a bypass or another process line; come back to it after the main line is done.
5. **Follow off-page connectors.** When the line leaves the sheet, the connector gives the next sheet number and line number; go there and keep going until you reach the far nozzle or the battery limit.
6. **Trace it back** from the far end; any valve you missed will show up. Then confirm it in the field: the pipe wins until the drawing is fixed.

## Reading a pump loop

A pump is read from suction to discharge, and the items are nearly always the same. Take **P-101A/B** taking suction from tank T-101:

![A P&ID on the control room wall: operators and millwrights read the same sheet](/photos/drawings/control-room-pid.jpg)

*A P&ID on the control room wall: operators and millwrights read the same sheet. Photo: PEO ACWA, CC BY 2.0, via commons*

1. **Suction line** from the tank nozzle, larger than the discharge (8 in suction, 6 in discharge is typical), with its own line number.
2. **Suction block valve** (a gate or butterfly, normally open, sometimes locked open, **LO**).
3. **Temporary or permanent strainer** (a Y, T or cone strainer symbol, often with a differential pressure gauge or **PDI** across it).
4. **Eccentric reducer** into the pump suction nozzle, flat side up.
5. **Suction pressure gauge** (**PI**) or transmitter, on a small-bore branch with its own root valve.
6. **The pump**, with its driver (motor **M**, turbine **T**), casing drain and vent, and the **seal flush plan** drawn as a small loop around the seal (**API Plan 11**, **Plan 53**).
7. **Discharge pressure gauge / transmitter** (**PI** / **PT**) close to the nozzle.
8. **Check valve** (swing or lift, arrow for flow direction) to stop backflow through the idle pump.
9. **Discharge block valve** (gate, globe for throttling on small pumps).
10. **Minimum-flow recirculation** teed off between the check valve and the block valve, back to the tank through a restriction orifice (**RO**) or a control valve, so the pump is never dead-headed.
11. **Vents and drains** at the high and low points, each a small valve with a capped end.
12. **The spare pump** drawn as a mirror image on the same headers with its own block and check valves; its suction valve is often left open so it stays full.
13. **Instrumentation**: low suction pressure switch (**PSL**), flow transmitter (**FT**), bearing temperature (**TE**), vibration (**VT**) and the motor start interlock (**HS**).

With that list you know what to close to isolate the pump (suction, discharge, recirculation, seal flush supply, any warm-up line), what to open to drain and vent it, and what to blind if the isolation must be positive.

## Instruments and control loops on the P&ID

Instruments appear as **bubbles** (circles) with a tag inside: letters for the function (**PIT** pressure indicating transmitter, **TIC** temperature indicating controller, **LSH** level switch high) and a **loop number** shared by every instrument in that loop. A bare circle is a field instrument, a circle with a horizontal line through it is on the control room panel, a circle in a square is a DCS point. Thin lines connect them: double slashes for a pneumatic signal, dashed for electrical, small circles for a software link.

![One flow control loop read on the P&ID from orifice to control valve](/img/drawings/isa-loop-on-pid.svg)

*One flow control loop read on the P&ID from orifice to control valve*

A **control loop** reads element, transmitter, controller, final element: **FE-201** (orifice plate) to **FT-201** (transmitter) to **FIC-201** (controller) to **FY-201** (converter) to **FV-201** (control valve). The control valve carries a **fail position** (**FC** fail closed, **FO** fail open, **FL** locked in place) and often a handwheel symbol. **Interlocks** appear as a diamond or a box with an interlock number (**I-5**) and a reference to the cause and effect chart. The full letter table, bubble shapes, signal lines and worked loops are in [ISA instrument tags, bubbles and letters](/article/isa-instrument-tags-bubbles-and-letters).

## Off-page connectors, tie-ins and holds

A line leaving a sheet ends in an **off-page connector**: an arrow-shaped box carrying the destination drawing number, with a matching box on the other sheet pointing back. Chasing connectors is how you find that a drain header runs to a sump three sheets away.

![Off-page connectors, tie-in points, holds and package boundaries](/img/drawings/off-page-connectors-tie-ins.svg)

*Off-page connectors, tie-in points, holds and package boundaries*

- **Battery limit** or **by others** boundary: a dashed line with a label where the drawing responsibility changes, for example between a vendor package and the plant piping; anything inside is on the vendor P&ID.
- **Tie-in point**: a numbered symbol (**TP-14** in a circle or hexagon) where new piping meets existing; the tie-in list gives the location, the method (hot tap, flange, cut and weld) and what must be isolated.
- **Existing vs new**: existing lines light or dashed, new lines heavy, **future** dotted, **demolished** crossed out.
- **Hold**: a cloud or box labelled **HOLD** with a number where the design is not final. Do not fabricate or install anything inside a hold.
- **Notes**: a number in a triangle refers to the numbered notes; the note is often the instruction that matters (slope, no pockets, car seal).

## What a millwright pulls off a P&ID

The P&ID is the isolation drawing. Before any work on a line or machine, take from it:

![The pump loop marked up with isolation points for a P-101A job](/img/drawings/pump-loop-isolation-points.svg)

*The pump loop marked up with isolation points for a P-101A job*

| What you need | Where it is on the P&ID |
|---|---|
| **Isolation points** for LOTO: every valve between the job and any energy source, including bypasses, recirculation, seal flush and drains to other systems | The traced line list |
| **Positive isolation**: double block and bleed (two block valves with a bleed between), spectacle blinds, spades and spacers, removable spools | Figure-eight and paddle symbols; the DBB arrangement |
| **Drains and vents** to empty and depressure, and where the drain goes (open, closed, sewer, flare) | Small-bore branches with a valve and a cap; the drain header line number |
| **Bypass lines** around a control valve or a machine that can feed the job from the other side | Lines with a globe or gate valve parallel to the item |
| **Valve normal positions**: **NC** normally closed, **NO** normally open, **LO/LC** locked open or closed, **CSO/CSC** car-sealed open or closed, **FC/FO** fail closed or open on control valves | Letters beside each valve, per the legend |
| **Spare equipment** and what changes when you take one machine out | A/B suffixes, common headers, the interlock that starts the spare |
| **Nozzle sizes and ratings** to pull a pump or exchanger: which gaskets and bolts to have ready | Line sizes and spec classes at the equipment; the vendor drawing |

Then **walk the line down** with the P&ID in hand and mark every difference (a valve not on the drawing, a drain added, a blind missing) in red: those **redlines** become the **as-built**. The isolation register lists each valve by tag, and the P&ID marked up with those numbers is the record. If the drawing and the pipe disagree, isolate what is really there and get the drawing corrected.

## Common mistakes

- Trusting an unmarked, out-of-date P&ID as the isolation drawing instead of walking the line down.
- Isolating the suction and discharge and forgetting the minimum-flow recirculation, the seal flush supply or the warm-up line that still feeds the pump.
- Reading a line that crosses another as connected when there is no junction dot.
- Assuming a service code (FW, PW, SW) from the last site.
- Mixing up PFD stream numbers with P&ID line numbers, or reading a PFD as if it showed every valve.
- Ignoring the notes and the holds: the note is often the instruction, and the hold means the design is not done.
- Forgetting that a spec break means different flanges, gaskets and bolts on each side of the joint.

## Related

- [P&ID symbols: valves, equipment and lines](/article/pid-symbols-valves-equipment-and-lines)
- [ISA instrument tags, bubbles and letters](/article/isa-instrument-tags-bubbles-and-letters)
- [Piping isometrics and spool sheets](/article/piping-drawings-isometrics-and-spool-sheets)
- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [Lockout tagout basics](/article/lockout-tagout-basics)
- [Pump troubleshooting](/article/pump-troubleshooting)
- [Mechanical seal replacement on a centrifugal pump](/article/mechanical-seal-replacement-centrifugal-pump)
- [PLC and instrumentation awareness](/article/plc-and-instrumentation-awareness)
