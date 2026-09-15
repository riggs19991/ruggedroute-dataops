---
title: "P&amp;ID Symbol Chart: Manual Valves (Gate, Globe, Ball, Butterfly, Plug, Needle, Diaphragm, Check, Three-Way, Angle, Relief, Rupture Disc), Control Valves, Actuators and Fail Positions, Pumps, Compressors and Drivers, Vessels, Tanks, Columns and Heat Exchangers, Filters, Strainers, Traps, Blinds and Inline Fittings, and Process, Utility and Signal Line Types"
slug: pid-symbols-valves-equipment-and-lines
category: drawings
kind: chart
tags: [P&amp;ID symbols, PID symbol chart, valve symbols, gate valve symbol, globe valve symbol, ball valve symbol, butterfly valve symbol, plug valve symbol, needle valve symbol, diaphragm valve symbol, check valve symbol, three-way valve symbol, relief valve symbol, PSV symbol, rupture disc symbol, control valve symbol, actuator symbol, diaphragm actuator, piston actuator, MOV symbol, solenoid valve symbol, fail closed, fail open, pump symbol, centrifugal pump symbol, PD pump symbol, compressor symbol, blower symbol, motor symbol, turbine symbol, vessel symbol, tank symbol, column symbol, heat exchanger symbol, strainer symbol, steam trap symbol, spectacle blind symbol, expansion joint symbol, orifice plate symbol, line types, pneumatic signal line, electric signal line, software link, ISA-5.1, PIP PIC001]
source: "ISA-5.1-2009 instrumentation symbols and identification (signal lines, final control elements, actuators, fail positions); ISA-5.3 shared display symbols; PIP PIC001 piping and instrumentation diagram documentation criteria and the PIP symbol set (valves, equipment, inline items); ISO 10628 flow diagrams and ISO 14617 graphical symbols for diagrams (ISO and Canadian variants); ASME B16.5, B16.9 and B16.11 for the fittings the symbols represent; company legend sheets."
summary: "A word chart of every symbol a millwright meets on a P&amp;ID, described in tables so it can be read without the drawn sheet: manual valve bodies, control valves with their actuators and fail positions, pumps, compressors and drivers, vessels, tanks, columns and exchangers, strainers, traps, blinds and the small inline fittings, and every process, utility and instrument signal line type, with notes on where ISA, PIP, ISO and company legends differ."
---

A P&amp;ID uses a few hundred symbols, most built from a handful of shapes: a bow tie is a valve, a circle is a pump or an instrument, a capsule is a vessel. This chart describes each symbol in words so you can read a sheet without the drawn legend beside you. How to read the drawing as a whole is in [PFD and P&amp;ID reading](/article/pfd-and-pid-reading).

## How to use this sheet

Each table gives the symbol name, how it is drawn, what it means and a note on variations. The base standard in the US and Canada is **ISA-5.1** for instruments and signal lines, with **PIP PIC001** supplying the valve and equipment set most EPC contractors use; ISO plants use **ISO 10628 / ISO 14617**. The legend sheet wins over this chart. A size is written on a valve only where it differs from the line; letters beside a valve give its normal position (**NC**, **NO**, **LO**, **LC**, **CSO**, **CSC**).

![A P&amp;ID drawn to the ISA symbol set: read it with the sheets below](/photos/drawings/pid-schema.jpg)

*A P&amp;ID drawn to the ISA symbol set: read it with the sheets below. Photo: Evinfo, CC BY-SA 3.0, via commons*

## Manual valves

![Manual valve symbols: gate, globe, ball, butterfly, plug, needle, check, relief and more](/img/drawings/pid-manual-valves-sheet.svg)

*Manual valve symbols: gate, globe, ball, butterfly, plug, needle, check, relief and more*

| Symbol name | How it is drawn | What it means | Notes |
|---|---|---|---|
| **Gate** | Two triangles point to point (a bow tie), open inside | Block valve, fully open or closed | The default isolation valve; not for throttling |
| **Globe** | Bow tie with a filled circle (dot) at the centre | Throttling or regulating valve | Flow direction matters; sometimes an arrow |
| **Ball** | Bow tie with an open circle at the centre | Quarter-turn block valve | Common under 2 in; full or reduced bore noted |
| **Butterfly** | Two short parallel lines across the line with a diagonal stroke between them; some legends use a bow tie with a diagonal | Quarter-turn valve on large low-pressure lines | Cooling water, air |
| **Plug** | Bow tie with a filled rectangle or bar at the centre | Quarter-turn block valve, lubricated or sleeved | Dirty and viscous service |
| **Needle** | Bow tie with a small filled triangle at the centre pointing to the seat | Fine regulation | Instrument and sample lines |
| **Diaphragm** | Bow tie with a small arc over the centre | Weir or straight-through diaphragm valve | Slurries, corrosive, sanitary |
| **Check, swing** | Bow tie with an arrow along the line or a hinged flap inside; ISO draws a small circle with a diagonal stroke | Flow in one direction only | The arrow gives the free direction |
| **Check, lift or piston** | Check symbol with a small circle or ball at the seat | One-way flow, vertical or small bore | Ball check on reciprocating pumps |
| **Three-way** | Three triangles meeting at a point (a T) with the ports labelled | Diverting or mixing | L-port or T-port noted |
| **Four-way** | Four triangles meeting at a point (a cross) | Switching or reversing duty | Reversing exchangers, filter changeover |
| **Angle** | Two triangles at 90 degrees to each other | Globe-type body with the outlet at a right angle | PSV inlets, blowdown |
| **Relief / safety valve (PSV, PRV, RV)** | Angle valve body with a spring (zigzag) on top, tag in a bubble, set pressure beside | Opens on overpressure and reseats | Outlet to flare, atmosphere or a header |
| **Rupture disc (PSE, RD)** | A short bar with a small dome inside a flange pair, tag beside | Bursts once at its rated pressure | Often under a PSV |

## Control valves, actuators and fail positions

A control valve is a valve body with an actuator on top of the stem and a tag bubble (**FV-201**). The body is usually the globe symbol; a butterfly or ball control valve uses its own body.

![Control valve actuators and fail positions FC, FO and FL](/img/drawings/pid-control-valves-sheet.svg)

*Control valve actuators and fail positions FC, FO and FL*

| Symbol name | How it is drawn | What it means | Notes |
|---|---|---|---|
| **Handwheel (manual)** | A short vertical stem with a bar or T across the top | Hand operated | Often omitted on ordinary manual valves |
| **Diaphragm, spring opposed** | A half-circle or dome on the stem | Pneumatic actuator, the common control valve | The spring sets the fail position |
| **Piston, single acting** | A rectangle on the stem with one signal connection and a spring | Pneumatic or hydraulic cylinder actuator | On/off valves, high thrust |
| **Piston, double acting** | Rectangle with two signal connections and no spring | Powered both ways | Fails in place |
| **Electric motor (MOV)** | A circle with **M** on the stem | Motor operated valve | Remote isolation on large lines; tag **HV** or **MOV** |
| **Solenoid** | A small square with **S** on the stem | Electric on/off, or a pilot on the air line to a bigger actuator | Tag **SV** or **XY**; on an actuator air line it is the trip |
| **Hydraulic** | Rectangle with **H** | Hydraulic actuator | Wellhead and turbine valves |
| **Spring return** | A small zigzag beside the actuator, or an arrow | Fails to the spring position on loss of power | Part of the fail-position marking |
| **Positioner** | A small square on the side of the actuator with the signal line entering it | Valve positioner (feedback) | Tag **ZY** or shown as part of the valve tag |

**Fail positions** are written under the valve, and ISA also draws an arrow: **FC** fail closed (arrow toward the seat), **FO** fail open (arrow away), **FL** fail locked in last position, **FI** fail indeterminate; some legends add **FAI** (fail as is). The fail position is what the valve does when air or power is lost, which is what happens on lockout: a fail-open valve opens when you isolate its air, so process isolation must be a manual valve, never the control valve.

## Pumps, compressors and drivers

![Pump, compressor, blower, driver, agitator, conveyor and gearbox symbols](/img/drawings/pid-equipment-sheet.svg)

*Pump, compressor, blower, driver, agitator, conveyor and gearbox symbols*

| Symbol name | How it is drawn | What it means | Notes |
|---|---|---|---|
| **Centrifugal pump** | A circle with the discharge leaving tangentially from the top and the suction entering the centre | Centrifugal pump | ISO draws a circle with a short arrow inside |
| **Vertical / submersible pump** | Pump circle drawn low with a long vertical column up to the motor, inside the sump outline | Vertical turbine, sump or submersible pump | |
| **Reciprocating PD pump** | A circle with a piston and cylinder drawn inside or beside it, or a rectangle with a piston | Plunger or piston pump | Needs a relief valve on the discharge |
| **Rotary PD pump (gear, screw, lobe)** | A circle with two small circles (gears), a helix (screw) or two lobes inside | Positive displacement rotary pump | Needs a relief |
| **Vacuum pump** | Pump circle with **VAC** or a liquid ring drawn inside | Vacuum service | |
| **Centrifugal compressor** | A trapezoid, wide at the suction and narrow at the discharge, or a circle with a tangent | Dynamic compressor | |
| **Reciprocating compressor** | A cylinder with a piston and a crank | PD compressor | Pulsation bottles as small capsules |
| **Rotary screw compressor** | A circle or rectangle with two meshing screws | Oil-flooded or dry screw | |
| **Blower** | A circle with a curved vane, or a trapezoid marked **B** | Low-pressure air or gas mover | Lobe blowers get the two-lobe symbol |
| **Fan** | A circle with two or three blades, or a propeller in a duct | Fan | Air coolers, cooling towers |
| **Motor** | A circle with **M** | Electric driver | |
| **Steam turbine** | A trapezoid with **T**, steam inlet and exhaust lines | Turbine driver | Trip valve on the inlet |
| **Engine** | A rectangle with **E** or **ENG** | Diesel or gas engine driver | Fire pumps |
| **Coupling** | Two short vertical bars between driver and driven shaft | Shaft coupling | |
| **Agitator / mixer** | A vertical shaft into a vessel ending in paddles, driver on top, tag **AG** | Vessel agitator | |

## Vessels, tanks and exchangers

![Vessel, tank and heat exchanger symbols](/img/drawings/pid-vessels-exchangers-sheet.svg)

*Vessel, tank and heat exchanger symbols*

| Symbol name | How it is drawn | What it means | Notes |
|---|---|---|---|
| **Vertical vessel / drum** | A tall capsule (rectangle with dished ends) with nozzles marked | Pressure vessel | A small capsule under it is a boot; a hatched band is a demister |
| **Horizontal vessel / drum** | A horizontal capsule on two saddles | Separator, knockout drum, receiver | Weir as a short line inside |
| **Column / tower** | A tall capsule with horizontal lines inside (numbered trays) or a hatched section (packing) | Distillation, absorber, stripper | |
| **Reactor** | A vessel with a catalyst bed (hatch) or an agitator, often with a jacket | Reactor | Jacket drawn as a second outline |
| **Tank, cone roof** | A rectangle with a peaked top | Atmospheric storage | Vent and overflow at the top |
| **Tank, floating roof** | Rectangle with a roof line drawn inside below the top edge | Floating roof storage | External or internal floater |
| **Tank, open top** | A rectangle with no top line | Open tank, sump, pit | |
| **Shell and tube exchanger** | A horizontal capsule with a straight or U line through it (the tube side) and nozzles at the ends and on the shell; ISO draws a circle with a line and a small cross | Shell and tube exchanger | Shell and tube side nozzles labelled |
| **Kettle reboiler** | A shell wider at one end with a weir and a vapour outlet on top | Kettle reboiler | |
| **Condenser** | A shell and tube symbol, often vertical, with the vapour inlet on top | Condenser | Vent for non-condensables |
| **Plate exchanger** | A rectangle with several vertical lines inside | Plate exchanger | |
| **Air cooled exchanger (fin fan)** | A wide rectangle (the bundle) with fan circles above or below it | Air cooler | |

## Filters, strainers, traps and inline fittings

![Strainers, filters, traps, blinds, orifice plates, vents and drains](/img/drawings/pid-fittings-sheet.svg)

*Strainers, filters, traps, blinds, orifice plates, vents and drains*

| Symbol name | How it is drawn | What it means | Notes |
|---|---|---|---|
| **Filter** | A rectangle or circle in the line with a diagonal or hatched band | Cartridge, bag or media filter | DP gauge usually across it |
| **Y strainer** | A short branch leaving the line at 45 degrees ending in a cap | Y-type strainer | Blow-off on the branch |
| **Basket strainer** | A can hanging under the line with a basket inside | Basket strainer | |
| **T strainer** | A T-shaped body on the line with the cap on the leg | T-type strainer | Large bore |
| **Steam trap** | A small square or circle with a **T** inside, or a box with **ST** | Steam trap | Type (float, thermodynamic, bucket) in the note |
| **Sight glass / flow indicator** | A circle with a line through it, or an open rectangle labelled **SG** | Visual flow check | Gauge glass on a vessel is **LG** |
| **Flame arrester** | A rectangle with a grid or hatching across the line | Flame arrester | Tank vents, flare lines |
| **Silencer** | A rectangle with horizontal lines inside on a vent | Silencer | Compressor intakes, steam vents |
| **Expansion joint (bellows)** | A zigzag or corrugated section in the line | Bellows expansion joint | Not a misalignment fixer |
| **Flexible hose** | A wavy or curly line between two flanges | Hose | Live length on the iso |
| **Reducer** | A small trapezoid in the line, symmetric (concentric) or with one flat side (eccentric) | Size change | The new size is written after it |
| **Flange pair** | Two short parallel lines across the line | Flanged joint | Where the joint can be broken |
| **Blind flange** | A single short bar closing the end of a line, sometimes with a filled end | Blanked end | Future connection, cleanout |
| **Spectacle blind** | A figure-eight beside the line, one loop open and one filled | Spectacle blind for positive isolation | Normal position noted |
| **Spade and spacer (paddle blinds)** | A filled circle with a handle (spade) or an open circle with a handle (spacer) at a flange pair | Removable blind or its spacer | Where a spectacle is too heavy |
| **Union** | A short bar across the line with a small circle at the centre | Threaded or socket union | Small bore |
| **Cap / plug** | A short arc (cap) or a filled square (plug) closing a small-bore end | Capped or plugged end | Every drain and vent ends in one |
| **Drain** | A short branch down with a small valve and a cap, labelled **D** | Low-point drain | To grade, funnel or closed drain |
| **Vent** | A short branch up with a small valve and a cap, labelled **V** | High-point vent | |
| **Sample point** | A branch with a valve and **SP** | Sample point | |
| **Flow orifice (FE)** | Two short parallel lines inside a flange pair, with the **FE** bubble | Orifice plate for flow measurement | |
| **Restriction orifice (RO)** | A single short bar with **RO** in a small circle beside it | Fixed restriction to limit flow | Not a measurement |

## Line and signal types

![Process line and instrument signal line types](/img/drawings/pid-lines-signals-sheet.svg)

*Process line and instrument signal line types*

| Symbol name | How it is drawn | What it means | Notes |
|---|---|---|---|
| **Major process line** | Heavy solid line with a flow arrow | Main process piping | Line number along it |
| **Minor process / utility line** | Lighter solid line | Utilities, drains, vents, small bore | |
| **Pneumatic signal** | Thin line with pairs of short diagonal slashes at intervals | 3-15 psi (0.2-1 bar) air signal | The commonest control valve signal |
| **Electric signal** | Thin dashed line (ISA-5.1-2009); older sheets use a solid line with three short slashes | 4-20 mA, discrete, thermocouple wiring | Both styles appear |
| **Hydraulic signal** | Thin solid line with small **L** marks | Hydraulic pilot or power | |
| **Capillary** | Thin line with **X** marks at intervals | Filled thermal system, remote seal | Do not cut |
| **Electromagnetic or sonic, guided** | Thin line with a sine wave at intervals | Guided wave radar, fibre, coax | |
| **Electromagnetic or sonic, unguided** | Dashed line with a sine wave | Radio, ultrasonic through air | |
| **Software or data link** | Thin line with small open circles at intervals | Internal system link, fieldbus | |
| **Mechanical link** | Thin line with small filled circles | Linkage or shaft | |
| **Jacketed line** | Two parallel lines around the process line with jacket inlet and outlet | Jacketed pipe | |
| **Traced line** | Thin line hugging the process line with **ET** or **ST**, or the code in the line number | Electric or steam tracing | Isolate the tracer before cutting |
| **Insulated line** | The code in the line number, or short marks across the line where insulation starts and stops | Insulation | |
| **Existing line** | Thin or dashed line, sometimes grey, marked **EXISTING** | Already installed | New work is heavy |
| **Future line** | Dotted or phantom line with a note | Not built yet | |
| **Underground line** | Dashed line marked **UG**, or a symbol at the entry and exit | Buried pipe | |

Where legends differ: ISA-5.1 governs signal lines and actuators in the US and Canada; PIP PIC001 supplies the valve and equipment shapes for most EPC contractors; ISO 14617 (many Canadian and European houses and vendor packages) draws the check valve, pump and exchanger differently. Company legends override all of them.

## Common mistakes

- Reading a bow tie as a gate valve without checking the centre: a dot is a globe, a circle is a ball, a bar is a plug.
- Missing the arrow on a check valve and assuming it blocks flow both ways.
- Treating a control valve as an isolation point; a fail-open valve opens when you isolate its air.
- Confusing a restriction orifice with a flow orifice: one limits flow, the other measures it.
- Taking a spectacle blind's drawn position as its present position without looking at it.
- Assuming a crossing of two lines is a connection when there is no dot.

## Related

- [PFD and P&amp;ID reading](/article/pfd-and-pid-reading)
- [ISA instrument tags, bubbles and letters](/article/isa-instrument-tags-bubbles-and-letters)
- [Piping isometrics and spool sheets](/article/piping-drawings-isometrics-and-spool-sheets)
- [Hydraulic symbols ISO 1219](/article/hydraulic-symbols-iso-1219-complete)
- [Pneumatic symbols and circuit reading](/article/pneumatic-symbols-and-circuit-reading)
- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [Quiz: drawings, schematics and P&amp;IDs](/article/quiz-drawings-schematics-and-pids)
