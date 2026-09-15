---
title: "ISA Instrument Tags Chart: The Tag (Letters plus Loop Number), First Letters for the Measured Variable, Modifiers and Succeeding Letters, Bubble Shapes and Location Lines (Field, Panel, Behind Panel, Local Panel, DCS, PLC), Signal Line Types, Worked Tags (PIT-101, TIC-203, FSL-310, LAHH-405, ZSC-512, PSV-120), Reading One Control Loop, Transmitters versus Switches, Indicators and Controllers, and the Instrument Index"
slug: isa-instrument-tags-bubbles-and-letters
category: drawings
kind: chart
tags: [ISA 5.1, ISA-5.1-2009, instrument tag, instrument bubble, instrument letters, tag letters, loop number, first letter, succeeding letter, modifier letter, PIT, TIC, FSL, LAHH, ZSC, PSV, TE, TT, FT, FIC, FY, FV, transmitter, switch, indicator, controller, converter, primary element, control valve tag, bubble shapes, shared display, DCS symbol, PLC symbol, field mounted, panel mounted, behind panel, local panel, signal lines, pneumatic signal, electric signal, control loop, loop diagram, instrument index, I/O address]
source: "ISA-5.1-2009 instrumentation symbols and identification (identification letters table, functional designations, instrument line symbols, general instrument or function symbols); ISA-5.3 graphic symbols for distributed control / shared display instrumentation; ISA-5.4 instrument loop diagrams; PIP PIC001 piping and instrumentation diagram documentation criteria (tagging and loop numbering practice); ISO 14617 and ISO 3511 for the ISO variants; company legend sheets and instrument indexes."
summary: "A word chart of the ISA-5.1 tagging system: how a tag is built from function letters and a loop number, the full first-letter table for the measured variable, the modifiers and the succeeding letters for readout and output functions, the bubble shapes and location lines that say where the instrument lives, the signal line types, a set of worked tags decoded letter by letter, one temperature loop read end to end, the difference between a transmitter, a switch, an indicator, a controller and a converter, and what each column of the instrument index tells you."
---

Every instrument on a P&amp;ID is a bubble with a code inside, and the code follows one rule set, ISA-5.1, on almost every plant in the US and Canada. Learn the letter table once and you can read the tag on any transmitter, switch or control valve, know what it measures, what it does and where its readout is. The P&amp;ID context is in [PFD and P&amp;ID reading](/article/pfd-and-pid-reading).

## The tag: letters plus loop number

A tag has two parts separated by a hyphen: the **functional identification** (letters) and the **loop identification** (a number, sometimes with a suffix). In **PIT-101A**:

![ISA tag decoder: PIT-101A letter by letter](/img/drawings/isa-tag-decoder.svg)

*ISA tag decoder: PIT-101A letter by letter*

| Part | Example | Rule |
|---|---|---|
| **First letter** | P | The measured or initiating variable (pressure) |
| **Modifier** (optional) | D in PDT, F in FFC | Changes the meaning of the first letter (differential, ratio) |
| **Succeeding letters** | I, T | The functions the instrument performs, in order: readout or passive functions first (I indicate), output functions after (T transmit) |
| **Function modifiers** (optional) | H, L, HH, LL | High, low, high-high, low-low, on alarms and switches |
| **Loop number** | 101 | Shared by every instrument in the same loop; often the first digit is the unit or P&amp;ID number |
| **Suffix** (optional) | A, B | Duplicate instruments in one loop, or parts of one loop |

The letters read in order and rarely exceed four. The loop number ties **FE-201, FT-201, FIC-201 and FV-201** together: same number, same loop. Some plants number loops per P&amp;ID sheet (sheet 10 carries 1001 to 1099), some per unit, some in a single series. Suffix letters distinguish parallel instruments (**PT-101A** and **PT-101B** voting on the same trip) and parts of one loop (**TV-203A** and **TV-203B** split-range valves). Canadian plants use ISA-5.1 as written; European vendor packages sometimes use ISO 3511 / ISO 14617, where a few letters differ.

## First letters: what is measured

The first letter names the measured or initiating variable. ISA-5.1-2009 assigns:

![ISA first letters: the measured variable for each letter](/img/drawings/isa-first-letters-table.svg)

*ISA first letters: the measured variable for each letter*

| Letter | Measured or initiating variable | Notes |
|---|---|---|
| **A** | Analysis | pH, oxygen, conductivity; the property is written beside the bubble |
| **B** | Burner, combustion | Flame detectors, burner management |
| **C** | User choice | Often conductivity on old sheets; the legend defines it |
| **D** | User choice | Often density; **D as a modifier** means differential (PDT) |
| **E** | Voltage | Electrical |
| **F** | Flow rate | **F as a modifier** means ratio (FFC) |
| **G** | User choice | Often gauging or gap; older sheets used G for glass |
| **H** | Hand | Manually initiated: hand switch HS, hand valve HV, hand controller HC |
| **I** | Current | Electrical current (motor amps: II) |
| **J** | Power | Electrical power; **J as a modifier** means scan |
| **K** | Time, time schedule | Timers, sequences; **K as a modifier** means time rate of change |
| **L** | Level | |
| **M** | User choice | Often moisture or humidity; older sheets used M as a momentary modifier |
| **N** | User choice | Legend defined |
| **O** | User choice | Legend defined |
| **P** | Pressure | Includes vacuum |
| **Q** | Quantity | Totalised or integrated quantity; **Q as a modifier** means integrate or totalise (FQI) |
| **R** | Radiation | Nuclear gauges |
| **S** | Speed, frequency | Machine speed; **S as a modifier** means safety (PSV) |
| **T** | Temperature | |
| **U** | Multivariable | One instrument handling several variables |
| **V** | Vibration, mechanical analysis | Vibration and shaft position monitors on machines |
| **W** | Weight, force | Load cells |
| **X** | Unclassified | Anything else; defined beside the bubble; **X as a modifier** is the X axis |
| **Y** | Event, state, presence | Events and on/off states; **Y as a modifier** is the Y axis |
| **Z** | Position, dimension | Valve position, actuator position; **Z as a modifier** is the Z axis |

The user-choice letters (C, D, G, M, N, O) mean whatever the company legend says, and the meaning must be the same throughout that plant. Where a first letter has a modifier, the modifier is the second letter of the tag and the pair is read together: **PD** differential pressure, **FF** flow ratio, **FQ** flow quantity, **TD** temperature difference, **PS** in PSV is pressure-safety.

## Modifiers and succeeding letters

The letters after the variable say what the device does. ISA sorts them into readout or passive functions, output or active functions, and function modifiers.

![ISA succeeding letters: readout, output and modifier meanings](/img/drawings/isa-succeeding-letters-table.svg)

*ISA succeeding letters: readout, output and modifier meanings*

| Letter | As a readout or passive function | As an output or active function | As a function modifier |
|---|---|---|---|
| **A** | Alarm | | |
| **B** | User choice | User choice | User choice |
| **C** | | Control | |
| **E** | Sensor, primary element (the thing in the pipe) | | |
| **G** | Glass, gauge, viewing device | | |
| **H** | | | High |
| **I** | Indicate | | |
| **K** | | Control station (manual loading station) | |
| **L** | Light (pilot light) | | Low |
| **M** | | | Middle, intermediate |
| **N** | User choice | User choice | User choice |
| **O** | Orifice, restriction | | |
| **P** | Point (test connection) | | |
| **R** | Record | | |
| **S** | | Switch | |
| **T** | | Transmit | |
| **U** | Multifunction | Multifunction | |
| **V** | | Valve, damper, louver (the final control element) | |
| **W** | Well, probe | | |
| **X** | Unclassified | Unclassified | Unclassified |
| **Y** | | Auxiliary device: relay, compute, convert | |
| **Z** | | Driver, actuator, unclassified final control element | |

**Variable modifiers** that sit right after the first letter: **D** differential, **F** ratio, **Q** integrate or totalise, **S** safety, **K** time rate of change, **J** scan, and on old sheets **M** momentary. **Function modifiers** at the end: **H** high, **L** low, **HH** high-high, **LL** low-low, **M** middle; so **LAHH** is a level alarm high-high and **PSLL** a pressure switch low-low. When one bubble both indicates and transmits, the passive letter comes first (**PIT**, not PTI). **Y** is the letter to watch: it is any relay, converter or computing function (I/P converter, square-root extractor, solenoid on an actuator, signal selector), and the actual function is written in a small box beside the bubble.

## Bubbles and where the instrument lives

The shape of the symbol says what kind of device it is; the line across it says where it is mounted.

![Bubble shapes and location lines: field, panel, behind panel, DCS, PLC](/img/drawings/isa-bubbles-sheet.svg)

*Bubble shapes and location lines: field, panel, behind panel, DCS, PLC*

| Shape | Drawn | Means |
|---|---|---|
| **Circle** | A plain circle with the tag inside | Discrete (stand-alone) instrument: a transmitter, gauge, switch, single-loop controller |
| **Circle in a square** | A circle inside a square | Shared display and shared control: a point on the DCS or a shared HMI |
| **Hexagon** | Six-sided figure | Computer function: a calculation or a point in a plant computer |
| **Diamond in a square** | A diamond inside a square | Programmable logic controller (PLC) function |
| **Interlock** | Diamond or hexagon with **I** and a number, no loop letters | Interlock logic reference |

| Location line | Drawn | Means |
|---|---|---|
| **No line** | Plain shape | Field mounted, at the equipment or on the pipe |
| **Single solid horizontal line** | One line through the middle | Primary location, normally accessible to the operator: the main control room panel or console |
| **Single dashed horizontal line** | One dashed line through the middle | Primary location, normally inaccessible: behind the panel, in a cabinet, a rack room |
| **Double solid horizontal line** | Two lines through the middle | Auxiliary location, accessible: a local panel or field console |
| **Double dashed horizontal line** | Two dashed lines | Auxiliary location, inaccessible: inside a local cabinet |

For a millwright: a bare circle **PI-101** is a gauge on the pipe, a lined **PIC-101** is a face in the control room, and a dashed **PY-101** is a converter in a cabinet. Field instruments are what you isolate and protect when you open a line.

## Signal lines

![Signal line types: pneumatic, electric, hydraulic, capillary, software](/img/drawings/pid-lines-signals-sheet.svg)

*Signal line types: pneumatic, electric, hydraulic, capillary, software*

| Line | Drawn | Carries |
|---|---|---|
| **Process connection** | Thin solid line from the pipe to the bubble | Impulse line, thermowell, tubing |
| **Pneumatic** | Thin line with pairs of short diagonal slashes | 3-15 psi (0.2-1 bar) air signal |
| **Electric** | Thin dashed line (older sheets: solid with three slashes) | 4-20 mA, discrete contact, thermocouple or RTD wiring |
| **Hydraulic** | Thin line with **L** marks | Hydraulic signal |
| **Capillary** | Thin line with **X** marks | Filled system to a remote seal or thermal bulb |
| **Electromagnetic or sonic** | Sine wave on the line (guided), on a dashed line (unguided) | Radar, ultrasonic, radio |
| **Software or data link** | Thin line with small open circles | Internal DCS or PLC link, fieldbus |
| **Mechanical link** | Thin line with small filled circles | Linkage or shaft |
| **Undefined** | Thin solid line with no marks | Any signal, type not stated |

The signal line direction is shown by arrows where it matters; a signal that leaves the sheet ends in the same off-page connector as a pipe.

## Worked tags

![Six worked tags drawn as they appear on a P&amp;ID](/img/drawings/isa-worked-tags.svg)

*Six worked tags drawn as they appear on a P&amp;ID*

| Tag | Read as | What it is | Where it lives |
|---|---|---|---|
| **PIT-101** | Pressure, indicating, transmitter, loop 101 | A pressure transmitter with a local display, sending 4-20 mA to the DCS | Field, on the pipe |
| **TIC-203** | Temperature, indicating, controller, loop 203 | The controller that holds a temperature setpoint and drives TV-203 | DCS face (circle in a square with a line) |
| **FSL-310** | Flow, switch, low, loop 310 | A contact that closes when flow drops below its setting, usually tripping the pump or raising an alarm | Field, or a software switch from FT-310 |
| **LAHH-405** | Level, alarm, high-high, loop 405 | The high-high level alarm, normally the trip level above the LAH | DCS or annunciator |
| **ZSC-512** | Position, switch, closed, loop 512 | A limit switch proving a valve is closed | On the actuator |
| **PSV-120** | Pressure, safety, valve, loop 120 | A relief valve; the loop number is its own | On the vessel or line |
| **TE / TT / TIC / TV-203** | Temperature element, transmitter, controller, valve | One temperature loop: thermocouple in the well, transmitter on its head, controller in the DCS, control valve in the line | Field, field, DCS, field |
| **FE / FT / FIC / FY / FV-201** | Flow element, transmitter, controller, converter, valve | One flow loop: orifice plate, DP transmitter, controller, I/P converter, control valve | Field, field, DCS, on the valve, field |

## Reading one control loop on the P&amp;ID

Take temperature loop 203 on a heat exchanger outlet. Start at the pipe: a small bubble **TE-203** on the outlet line is the **element**, a thermocouple or RTD in a thermowell (**TW-203** may be tagged separately). A thin solid line runs from it to **TT-203**, the **transmitter**, drawn as a bare circle beside the pipe: it turns the millivolts into 4-20 mA. A dashed electric signal line leaves TT-203 and goes to **TIC-203**, drawn as a circle inside a square with a solid line through it: the **controller**, a DCS point on the operator's screen, which compares the measurement with the setpoint. From TIC-203 a dashed line runs to **TY-203**, a small circle beside the control valve with **I/P** in a box: the **converter** that turns 4-20 mA into 3-15 psi air. A pneumatic line with double slashes runs from TY-203 to the diaphragm on **TV-203**, the **control valve** on the cooling water to the exchanger, marked **FO** (fail open: on loss of air it opens and keeps cooling). A **TAH-203** bubble on the DCS shares the loop number and sounds when the outlet runs hot. Follow the loop number and you have read the whole thing: element, transmitter, controller, converter, valve, alarm. The loop diagram (ISA-5.4) for TIC-203 then gives every wire, terminal and tubing run between them.

![One control loop on the P&amp;ID from orifice to control valve](/img/drawings/isa-loop-on-pid.svg)

*One control loop on the P&amp;ID from orifice to control valve*

## Transmitters, switches, indicators and controllers

![Transmitter, switch, indicator and controller compared](/img/drawings/isa-transmitter-vs-switch.svg)

*Transmitter, switch, indicator and controller compared*

| Device | Letters | What it does | What you see in the field |
|---|---|---|---|
| **Primary element** | E (FE, TE, LE) | Senses the variable: orifice plate, thermocouple, float, probe | The thing in or on the pipe; often removable for a job |
| **Transmitter** | T (PT, PIT, FT) | Converts the measurement into a continuous signal (4-20 mA, digital) to the control system | A head with a display, tubing or a thermowell, a cable |
| **Switch** | S (PSL, FSH, LSHH, ZSC) | A contact that changes state at one setting: alarm, trip, permissive | A small box with a setpoint screw, or a software switch from a transmitter |
| **Indicator** | I (PI, TI, FI) | Shows the value: a gauge, a thermometer, a rotameter, or the number on the screen | Gauge on the pipe or a face on the panel |
| **Controller** | C (PIC, TIC, FIC, LC) | Compares the measurement with a setpoint and drives an output | DCS point, single-loop controller, or a self-contained field controller |
| **Converter / relay / compute** | Y (FY, TY, XY) | Changes the signal: I/P, P/I, square root, high select, solenoid on an actuator | Small box on or near the valve |
| **Final control element** | V, Z (FV, TV, XV, ZY) | The control valve, damper, on/off valve or actuator | The valve in the line |
| **Alarm** | A (PAH, LALL) | Announces a limit | Annunciator or screen |

The distinction that matters on a job: a **transmitter** sends a continuous value and the trip point lives in the control system; a **switch** trips at its own setting and can be hard-wired independent of the DCS, so bumping a PSL while working on a pump can shut it down. A **controller** moves something; an **indicator** only shows. Disconnect anything with a T, S or C in its tag and the control system sees it: somebody must know.

## The instrument index

The **instrument index** (instrument list) is the database behind the bubbles, one row per tag. Typical columns:

| Column | Says |
|---|---|
| **Tag** | PIT-101 |
| **Service** | What it measures: P-101A discharge pressure |
| **P&amp;ID** | Drawing and sheet where the bubble is |
| **Loop** | Loop number and loop diagram reference |
| **Type** | Instrument type: gauge pressure transmitter, RTD, magnetic flowmeter, limit switch |
| **Range and setpoint** | 0-300 psig (0-20 bar); trip at 25 psig |
| **Signal** | 4-20 mA, HART, fieldbus, pneumatic, discrete |
| **Location** | Field, panel, DCS, PLC; mounting details |
| **Data sheet** | The specification sheet (ISA-20 form) number |
| **I/O address** | The controller, card and channel it lands on |

Use it to find the range of a gauge before you trust it, the I/O address when you ask the technician to force a point, and the loop diagram when a wire must come off.

## Common mistakes

- Reading PSV as a pressure switch: S after P is the safety modifier, and PSV is a relief valve.
- Reading FSL as a flow switch that acts on low, then finding the trip is software in the DCS from FT-310: check the index for what is hard-wired.
- Treating a bare circle and a lined circle as the same: one is on the pipe, the other is in the control room.
- Assuming a user-choice letter (C, D, G, M) from the last plant instead of this legend.
- Reading a two-letter modifier the wrong way: PDT is differential pressure, not a pressure controller.
- Forgetting that Y bubbles (I/P converters, solenoids) sit on the valve and lose the valve when their air or power is pulled.
- Disconnecting an element or transmitter for a job without telling the control room that the loop and its alarms will go bad.
- Ignoring the suffix: PT-101A and PT-101B may be two of three voting transmitters, and pulling one changes the trip logic.

## Related

- [PFD and P&amp;ID reading](/article/pfd-and-pid-reading)
- [P&amp;ID symbols: valves, equipment and lines](/article/pid-symbols-valves-equipment-and-lines)
- [PLC and instrumentation awareness](/article/plc-and-instrumentation-awareness)
- [Motor control schematics and wiring diagrams](/article/motor-control-schematics-and-wiring-diagrams)
- [Electrical symbols NEMA and IEC](/article/electrical-symbols-nema-and-iec)
- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [Quiz: drawings, schematics and P&amp;IDs](/article/quiz-drawings-schematics-and-pids)
