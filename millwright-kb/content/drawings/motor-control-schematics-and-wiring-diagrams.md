---
title: "Motor Control Schematics and Wiring Diagrams: Schematic, Wiring Diagram and One-Line Compared, Ladder Format and Reading Order, the Three-Wire Start-Stop Rung by Rung, Wire Numbers, Rung Numbers and Cross-References, Device Designations, Control Power Transformer Fusing and Grounding, Interlocks, Jog and Forward-Reverse, Two-Speed and Reduced-Voltage Starters, VFD Control Wiring, the Wiring Diagram and Panel Layout, the MCC Bucket Sheet, and Using the Schematic When a Motor Will Not Start"
slug: motor-control-schematics-and-wiring-diagrams
category: drawings
kind: reference
tags: [motor control schematic, ladder diagram, wiring diagram, connection diagram, one line diagram, three wire control, two wire control, start stop circuit, seal in contact, auxiliary contact, restart hazard, wire numbers, rung numbers, contact cross reference, device designations, control power transformer, x2 grounded, control fuse, nfpa 79, ul 508a, electrical interlock, mechanical interlock, jog circuit, jog relay, forward reverse starter, two speed starter, consequent pole, reduced voltage starter, wye delta, open transition, closed transition, autotransformer starter, part winding starter, soft starter, vfd control wiring, speed reference, 4-20 ma, safe torque off, terminal strip, cable schedule, panel layout, mcc bucket, nema starter size, overload setting, motor will not start]
source: "NEMA ICS 19-2002 (industrial control diagrams and device designations); JIC EMP-1; NFPA 79 (electrical standard for industrial machinery: control circuits, transformer grounding and fusing, wire colours and marking); NFPA 70 (NEC) Article 430 (motor circuits, controllers and overload protection); UL 508A (industrial control panels); NEMA ICS 2 (contactor and starter sizes); Allen-Bradley (Rockwell) Bulletin 509 and 709 starter wiring diagrams and PowerFlex drive manuals; Square D (Schneider) Class 8536 starter and Model 6 MCC publications; Siemens SIRIUS starter and SINAMICS drive wiring publications."
summary: "How a motor starter is drawn three ways and how to read each: the ladder schematic rung by rung from the plain start-stop circuit through interlocked, jogged, reversing, two-speed, reduced-voltage and drive-controlled starters, the numbering and cross-reference systems that let you follow a wire across sheets, the control transformer and its fusing, the wiring diagram and MCC bucket sheet that tie the schematic to real terminals, and the millwright's method for a motor that will not start: mechanical checks, reading the rung, and handing the electrician the rung number instead of opening a live door."
---

A starter is drawn three times in a machine's electrical package, and each drawing answers a different question: the **one-line** says what feeds it, the **schematic** says how it works, and the **wiring diagram** says where the wires physically go. A millwright reads all three: to find the disconnect to lock, to understand why a motor stopped, and to point the electrician at the right terminal. The symbols are in [electrical symbols, NEMA and IEC](/article/electrical-symbols-nema-and-iec). What this article does not license is live testing: opening an energised panel and putting a meter on it is qualified-person work under [electrical safety for mechanics](/article/electrical-safety-for-mechanics) and [lockout basics](/article/lockout-tagout-basics).

## Schematic, wiring diagram, one-line: three drawings of one starter

![The same starter as a schematic and as a wiring diagram](/img/drawings/schematic-vs-wiring-diagram.svg)

![Plant one-line extract down to the MCC bucket and motor](/img/drawings/one-line-extract.svg)

*Plant one-line extract down to the MCC bucket and motor*

*The same starter as a schematic and as a wiring diagram*

| Drawing | What it shows | What it is for | What it does not show |
|---|---|---|---|
| **One-line (single-line)** | One line per circuit from the MCC bus through breaker, starter and cable to the motor, with sizes (30 A MCP, NEMA size 2, 15 hp, 3 AWG) | Finding what feeds the motor and where the disconnect is | How the control works |
| **Schematic (elementary, ladder)** | Every device drawn by function in the order the circuit works, power section on top, control ladder below | What must be true for the coil to pull in | Where anything is physically |
| **Wiring (connection) diagram** | Devices drawn where they sit in the panel with every wire, terminal number and cable | Landing and tracing real wires | The logic, which cannot be read from it |

The drawing index says which sheet is which; the schematic page (E-3) and its wiring page (E-13) carry the same device designations.

## Ladder format: lines, rungs and reading order

The control schematic is a ladder. **L1** is the left rail (the hot, fused side of the control transformer secondary, wire 1); **L2** is the right rail (the grounded side, wire 2). Each **rung** runs left to right: **contacts on the left, one load on the right**, connected straight to L2. Rungs are numbered down the left margin (1, 2, 3, or 101, 102 on sheet 1). Read a rung as a sentence: for the load to be powered, every contact in series from L1 must be closed, and a parallel branch is an alternative path. Wire numbers change at every device; the same number means the same electrical point wherever it appears. Loads in parallel on one rung (a coil and its pilot light) are drawn stacked. IEC sheets turn the ladder on its side, rails horizontal and current paths vertical, numbered across the top; the reading rule is the same.

## The three-wire start-stop rung by rung

The circuit under every NEMA starter door:

![Three-wire start-stop schematic in ladder format, rung by rung](/img/drawings/three-wire-start-stop.svg)

*Three-wire start-stop schematic in ladder format, rung by rung*

```
   L1 ---1---[ STOP NC (1PB) ]---3---[ START NO (2PB) ]---4---[ OL NC ]---5---( M coil )---2--- L2
                                   |                     |
                                   +------[ M aux NO ]---+
```

- **Wire 1 to 3**: the STOP button, normally closed. Pressing it breaks the rung. It is NC so a broken wire or a loose terminal stops the machine instead of preventing a stop.
- **Wire 3 to 4**: the START button, normally open, in parallel with the **M auxiliary contact** (the seal-in or holding contact, an NO contact on the contactor itself).
- **Wire 4 to 5**: the **overload contact**, NC, opened by the overload relay when the motor draws too much current for too long.
- **Wire 5 to 2**: the **M coil**, the load, straight to L2.

Press START: current flows 1-3-4-5 through the coil; the contactor pulls in, closing the three power contacts to the motor and the M auxiliary. Release START: the auxiliary contact now carries the current from 3 to 4, so the coil stays in. Press STOP, or trip the overload, or lose control power: the coil drops out, the auxiliary opens, and the circuit is back at rest. When power returns the motor **does not restart**, because the seal-in is open and nobody is pressing START. That is **low-voltage protection**, and it is the reason a three-wire circuit is required wherever an unexpected restart could hurt someone.

**Two-wire control** replaces the buttons with one maintained contact (a selector switch, a float switch, a thermostat): L1, contact, OL, coil, L2. It restarts the instant power comes back. Right for a sump pump, wrong for a conveyor with a man clearing a jam: a two-wire circuit on a machine with an operator is a finding to raise.

Older sheets put the OL contact between the coil and L2. NFPA 79 practice now puts one side of every coil directly on the grounded conductor and the OL contact on the L1 side, so a ground fault on the coil wiring cannot hold the starter in.

## Wire numbers, rung numbers and cross-references

![Wire numbers, rung numbers, device designations and cross-references decoded](/img/drawings/wire-and-rung-numbering.svg)

*Wire numbers, rung numbers, device designations and cross-references decoded*

- **Wire numbers** are assigned sequentially through the drawing (1, 2, 3, 4, 5 as above, 1 and 2 reserved for the rails) or by rung (rung 3 uses 301, 302, 303). Either way the number changes at every device and stays the same through terminals and splices. Wire 1 is the control hot everywhere, wire 2 the grounded side everywhere; DC sections often use a 100 or 200 series.
- **Rung numbers** run down the left margin. Multi-sheet sets use sheet-and-rung (3.12 or 312) so a cross-reference is unambiguous.
- **Contact cross-references** sit under or beside every coil: a list of the rungs where that coil's contacts appear, with **NC contacts underlined** (or shown with a bar or in parentheses). A coil 1CR on rung 4 with the note "6, 9, 14" has NO contacts on rungs 6 and 9 and an NC contact on rung 14. Next to each contact, the rung of its coil is written. IEC sheets do the same with a **contact mirror**: a small table under the coil listing each contact's terminal numbers (13-14, 21-22) and the path where it is used (4.6).
- **Terminal numbers** appear as small circles on the wire with the strip and terminal (TB1-7) so the schematic and the wiring diagram meet.

To follow a signal: find the coil, read its cross-reference list, go to each rung and read what that contact enables or blocks.

## Device designations

| Designation | Device | Designation | Device |
|---|---|---|---|
| 1M, 2M | Motor contactor (starter) 1, 2 | F, R | Forward and reverse contactors |
| 1CR, 2CR | Control relay | 1TR | Timing relay |
| 1OL | Overload relay (and its contact) | 1CPT | Control power transformer |
| 1PB, 2PB | Pushbutton (STOP usually 1PB, START 2PB) | 1FU, 2FU | Fuse (primary, secondary) |
| 1SS | Selector switch (HAND-OFF-AUTO) | 1CB, 1MCP | Circuit breaker, motor circuit protector |
| 1LS | Limit switch | 1DISC | Disconnect |
| 1PL | Pilot light | 1SOL | Solenoid |
| 1PS, 1FS, 1TS | Pressure, flow/float, temperature switch | 1JR | Jog relay |
| S, 1A, 2A | Wye-delta or autotransformer starting contactors | 1SR | Safety relay |

IEC sets use -K1 (contactor or relay), -Q1 (breaker or disconnect), -F1 (fuse or overload), -S1 (switch), -M1 (motor), -T1 (transformer), -H1 (lamp), -Y1 (solenoid or brake), -U1 (drive), -X1 (terminal strip). The number is the instance, not a sequence: -K7 is simply the seventh contactor on the set.

## Control power: transformer, fusing and grounding

The **control power transformer (CPT)** takes 480 V (600 V in Canada) from two of the motor lines after the disconnect and delivers 120 V for the ladder. On the schematic: primary terminals **H1-H4** with jumpers (H2-H3 for 480 V), **fuses on both primary lines** (both ungrounded), secondary **X1 fused** with a small time-delay fuse, and **X2 grounded** at the panel and connected to L2. The grounded X2 is why every switch, the STOP button and the OL contact sit on the L1 side and the coil goes straight to L2. The secondary fuse follows the VA: a 150 VA CPT delivers 1.25 A at 120 V and carries about a 1.6-2 A fuse; 500 VA, 4.2 A and a 5-6 A fuse. Blown control fuse: the ladder is dead, the power section is live, the motor stops. A 24 V DC supply for the PLC side is drawn as a rectangle (-G1) with its own fuse. NFPA 79 wire colours on the sheet: **black** ungrounded power, **red** AC control, **blue** DC control, **yellow** control fed from outside that stays live when the disconnect is off, **white** grounded conductor, **green** ground. A yellow wire is a warning: locking out the machine disconnect does not kill it.

## Interlocks, jog and forward-reverse

**Forward-reverse** uses two contactors, F and R, on one overload. F connects L1-L2-L3 to T1-T2-T3; R swaps two lines (L1 to T3, L3 to T1). Both in together is a line-to-line short, so the schematic shows three layers of protection: an **electrical interlock** (an NC R auxiliary in the F coil rung and an NC F auxiliary in the R rung), a **mechanical interlock** (a dashed line between the two contactor symbols: a lever that stops both armatures closing), and often **pushbutton interlocks** (the FWD button carries an NC contact in the REV rung and vice versa). Reading the rungs: FWD is STOP, FWD NO in parallel with F aux, REV NC button, R NC aux, OL, F coil; REV mirrors it. Some sheets add a **time delay** or a **zero-speed switch** so the motor coasts before reversing.

![Forward-reverse schematic with electrical and mechanical interlocks](/img/drawings/forward-reverse-interlocks.svg)

*Forward-reverse schematic with electrical and mechanical interlocks*

**Jog** inches the machine: the motor runs only while the button is held, so the seal-in must not work in jog. The proper circuit uses a **jog relay** (1JR): START energises 1JR, whose NO contact is in series with the M seal-in; JOG energises M directly, bypassing 1JR, so M cannot seal. The cheap version uses a JOG button with an NC contact that opens the seal-in path and an NO contact that energises M; release it quickly and the seal-in can make before the NC contact closes, and the motor runs on. A jog-run **selector switch** in series with the seal-in is the other common arrangement. The cheap circuit on a machine where a run-on could hurt someone is a finding.

## Two-speed and reduced-voltage starters on paper

- **Two-speed, separate winding**: two contactors (L for low, H for high), each with its own overload, feeding two independent windings brought out as T1-T3 and T11-T13. Electrical and mechanical interlocks as for reversing. Simple to read: two starters side by side.
- **Two-speed, consequent pole**: one winding with six leads T1-T6; low speed connects T1-T3 with T4-T6 open (or shorted); high speed shorts T1-T3 together and feeds T4-T6, so a third contactor **S** (the shorting contactor) appears with H. The sheet notes constant torque, variable torque or constant horsepower, which changes which leads get shorted. Overloads sized for each speed.
- **Wye-delta (star-delta)**: a six-lead motor started in wye at 58 percent voltage (about a third of the locked-rotor current and torque), then reconnected in delta. Contactors 1M (line), S (the wye point) and 2M (delta), a timer 1TR (typically 5-15 s), and interlocks between S and 2M. **Open transition** drops the motor for a fraction of a second during the changeover (a current spike, a jolt); **closed transition** adds resistors and a fourth contactor (2A) so the motor is never disconnected. The line schematic shows six motor leads T1-T6, which is how you recognise it.
- **Autotransformer**: a three-coil autotransformer with 50, 65 and 80 percent taps, start, run and shorting contactors, a timer; closed transition. The tap in use is written on the sheet.
- **Part-winding**: a nine- or twelve-lead motor with two contactors, 1M on half the winding and 2M on the other half 1-3 s later; two overloads.
- **Soft starter**: a rectangle with L1-L3 in, T1-T3 out, a bypass contactor drawn around it (closed at full speed), a run input, ramp time and current limit written beside it, and a fault contact in the ladder.

Whichever it is, read the **timer setting** and the **interlocks**: a reduced-voltage starter that trips on start has usually lost its timer setting or has a stuck transition contactor.

## VFD control wiring

A drive replaces the starter but keeps a control ladder. On the sheet: a rectangle with L1-L3 in through a disconnect and fuses or a breaker, U-V-W (T1-T3) to the motor in shielded VFD cable, DC bus terminals and a braking resistor if fitted, and a **control terminal strip**:

| Terminal group | What lands there | Notes |
|---|---|---|
| Digital inputs | Run/stop (two-wire or three-wire mode set by parameter), forward/reverse, jog, preset speed selects, fault reset, external fault | 24 V DC from the drive, sourcing or sinking by a jumper; a stop wired NC |
| Speed reference | 0-10 V from a potentiometer (three wires: 10 V, wiper, common) or 4-20 mA from the PLC; a jumper or switch selects V or mA | 4-20 mA survives long runs; 0 mA means a broken wire |
| Relay outputs | RUN and FAULT contacts into the ladder (a fault contact in series with a system-ready relay) | Dry contacts; the fault light on the door |
| Safe torque off (STO) | Two channels from the safety relay; opening them removes gate power to the transistors | Not an isolation: the bus stays live; see [VFD basics](/article/vfd-basics-for-millwrights) |
| Drive enable | An input that must be made before any run command works | Often the E-stop chain |
| Network | Ethernet/IP, Profinet, Modbus to the PLC | Run commands may come over the network with no wire to see |

The drive's own manual gives the terminal numbers; they differ between makes and series. A drive can be running from the network with nothing on the digital inputs, so an empty terminal strip does not mean no run command.

## The wiring diagram: terminals, cables and panel layout

The wiring (connection) diagram draws the panel as built: the back-plate with the disconnect, breaker, CPT, contactors, overloads, relays, terminal strips and power supply, each with its designation label as it reads on the real nameplate, and the door with its buttons and lights. Every wire carries its number at **both ends** (matching the ferrules); terminal strips are numbered rows, commonly **TB1** power and motor leads, **TB2** 120 V control and field devices, **TB3** 24 V DC PLC I/O, but the sheet defines it. Field devices sit outside the panel outline with their cable numbers. Beside it: the **cable schedule** (number, from, to, type, conductors, size) and **conduit schedule** (number, size, route, cables in it), and the **panel layout** with mounting dimensions and door clearance. Use it to find the terminal a limit switch lands on so you can tell the electrician TB2-14 and 15, wire 31; to match a device label to the schematic; and to see which conduit a damaged cable runs in.

![Inside a control panel: the wiring diagram tells you where each of these wires lands](/photos/drawings/electricians-panel.jpg)

*Inside a control panel: the wiring diagram tells you where each of these wires lands. Photo: PEO ACWA, CC BY 2.0, via commons*

## The MCC bucket sheet

Each **motor control centre bucket** has a sheet or a line in the MCC schedule giving: section and position, **unit size** in space factors (a space is 6 in / 152 mm; a size 1 starter takes 1 space, a size 3 about 2.5), the **disconnect** (MCP with its instantaneous trip setting, or a fused switch with fuse class and size), the **starter NEMA size** and type (FVNR non-reversing, FVR reversing, 2S two-speed, RVSS soft start, VFD), the **overload** heater number or electronic FLA setting and trip class (10, 20, 30), the **control transformer** VA, the **door devices** (HOA, START/STOP, run light, reset), the **terminal list** to the field, the motor hp, FLA and cable size, and the wiring class (NEMA Class I Type B: each bucket wired to its own terminal block).

![A motor protective circuit breaker in a starter bucket](/photos/drawings/motor-protective-breaker.jpg)

*A motor protective circuit breaker in a starter bucket. Photo: Dmitry G, CC BY-SA 3.0, via commons*

![MCC bucket elevation and its schedule of settings](/img/drawings/mcc-bucket-sheet.svg)

*MCC bucket elevation and its schedule of settings*

| NEMA starter size | Continuous amps | Max hp at 460 V, 3-phase |
|---|---|---|
| 00 | 9 | 2 |
| 0 | 18 | 5 |
| 1 | 27 | 10 |
| 2 | 45 | 25 |
| 3 | 90 | 50 |
| 4 | 135 | 100 |
| 5 | 270 | 200 |
| 6 | 540 | 400 |

IEC contactors are rated by AC-3 amps instead (9, 12, 18, 25, 32, 40, 50, 65, 80, 95 A and up). The bucket sheet is where you check a replacement motor: a 20 hp motor going into a size 1 bucket, or an FLA above the overload's adjustment range, is a stop.

## Using the schematic when the motor will not start

1. **Mechanical first**, with the disconnect locked and tried: is the motor coupled, the brake released, the driven machine free to turn by hand, a belt or chain jammed, a guard or hatch open? A jam is the commonest cause of an overload trip.
2. **Is everything in?** The disconnect handle on, the MCC bucket's breaker not tripped (a tripped handle sits midway), every E-stop on the line released, the HOA in the right position, guards closed on their interlock switches.
3. **What are the lights saying?** Power-on, run and fault lights, the drive's fault code, the overload relay's **trip indicator** or popped reset button, the safety relay's channel LEDs, the PLC output LED for the starter. Reset a tripped overload **once** after the mechanical cause is found; a second trip is the electrician's.
4. **Read the rung.** Find the M coil (or the drive run command) and read every contact in series from L1: STOP, each E-stop, the guard switches, the PLC permissives, the OL contact, the drive fault contact. Each is a thing you can look at without opening the panel: the button, the switch actuator, the sensor LED, the HMI permissive list.
5. **Hand it over precisely.** Rung 14, the M coil; guard switch 3LS on wire 27 looks made, overload not tripped, PLC output O:2/3 on, contactor does not pull in: that is a five-minute repair for the electrician. It does not work is an hour.

What you do not do: open a live door to look at the overload, put a meter on the terminal strip, jumper a contact to see if that is the one, or push the contactor in by hand. Those are energised-work tasks behind an arc-flash boundary for a qualified person; see [electrical safety for mechanics](/article/electrical-safety-for-mechanics), and anything that needs the panel open starts with [lockout](/article/lockout-tagout-basics).

## Common mistakes

- Reading a two-wire circuit as three-wire and being surprised when the motor restarts after a power dip.
- Confusing the OL heaters in the power section with the OL contact in the ladder; only the contact is in the coil's rung.
- Losing the wire number across a terminal strip: the number does not change at a terminal, only at a device.
- Missing the underline on a cross-reference and looking for an NO contact that is really NC.
- Assuming the disconnect kills everything: yellow wires and drive network commands survive it.
- Reading the wiring diagram to understand the logic; it cannot be done.
- Replacing a motor without checking the bucket sheet's starter size and overload range.
- Resetting an overload repeatedly without finding the jam.
- Opening the panel door to check the overload with the bucket live.

## Related

- [Electrical symbols, NEMA and IEC](/article/electrical-symbols-nema-and-iec)
- [Electrical safety for mechanics](/article/electrical-safety-for-mechanics)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [VFD basics for millwrights](/article/vfd-basics-for-millwrights)
- [Motor lead connections](/article/motor-lead-connections)
- [Reading a motor nameplate](/article/reading-a-motor-nameplate)
- [Megger and basic motor testing](/article/megger-and-basic-motor-testing)
- [PLC and instrumentation awareness](/article/plc-and-instrumentation-awareness)
