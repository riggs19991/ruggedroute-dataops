---
title: "PLC and Instrumentation Awareness for Millwrights: How a Control System Is Built (PLC, I/O, HMI, Drives, Safety Relays), Digital and Analog Signals (24 VDC, 4-20 mA), the Sensors on Machinery (Proximity, Photo-Eye, Limit Switch, Encoder, Pressure, Temperature, Level, Flow, Vibration), Mounting and Adjusting Sensors, What to Check When a Machine Will Not Run, Reading I/O Lights and the HMI, What Not to Touch, and Working With the Controls Tech"
slug: plc-and-instrumentation-awareness
category: motors-electrical
kind: reference
tags: [PLC, programmable logic controller, PLC basics, I/O, inputs outputs, 24 VDC, 4-20 mA, digital input, analog input, HMI, proximity sensor, inductive prox, capacitive sensor, photo eye, photoelectric sensor, retroreflective, limit switch, encoder, pressure transmitter, RTD, thermocouple, level switch, flow switch, vibration transmitter, safety relay, safety PLC, light curtain, interlock switch, machine will not start, permissive, I/O lights, forcing I/O, sensor gap, sensor alignment, instrument tag, ISA tag]
source: "Allen-Bradley/Rockwell and Siemens PLC and I/O documentation; sensor manufacturer application guides (Turck, Banner, Pepperl+Fuchs, ifm: sensing ranges, mounting, alignment); ISA 5.1 (instrument tagging); ISO 13849 / IEC 62061 and OSHA machine guarding rules on safety circuits; plant controls practice."
summary: "A millwright meets the control system every time a machine will not start: this explains what the pieces are and how a machine's permissives, interlocks and sensors decide whether it runs, the signals and sensors bolted to the machinery and how to mount and set them correctly, a method for finding why a machine stopped using the I/O lights and the HMI before calling the controls tech, and the things a millwright does not touch."
---

## The parts

| Part | What it is | Millwright's interest |
|---|---|---|
| **PLC** (Allen-Bradley ControlLogix/CompactLogix/MicroLogix, Siemens S7, Omron, Automation Direct) | The computer that runs the machine's logic program: it reads inputs, decides, and sets outputs, scanning many times a second | The program's **permissives** (what must be true to start) and **interlocks** (what stops it) are what you are fighting when it will not run |
| **I/O modules** (in the PLC rack or remote on a network) | **Digital inputs** (24 VDC or 120 VAC on/off from switches and sensors), **digital outputs** (to starters, solenoids, lights), **analog inputs** (4-20 mA / 0-10 V from transmitters), **analog outputs** (speed references to drives, valve positioners) | Each point has an **LED**: the fastest diagnostic in the plant |
| **HMI** (the touchscreen or the SCADA screen) | Shows status, alarms, faults, values; lets the operator start/stop and set points | The **alarm/fault screen** tells you which interlock stopped the machine; the **status/diagnostic screen** often shows the permissives as a list with green/red |
| **Field devices** | Sensors (inputs) and actuators (outputs: motor starters, VFDs, solenoid valves, relays) | Mounted on the machine: yours to install, align and protect |
| **Safety system** (safety relays, a safety PLC, e-stops, light curtains, guard interlock switches, safety mats, two-hand controls) | A separate, redundant circuit (categories per ISO 13849) that removes power/torque when a guard opens or an e-stop is pressed | Never bypassed, jumpered or "temporarily" defeated; a guard switch that is out of adjustment stops the machine: fix the alignment, not the circuit |
| **Networks** (Ethernet/IP, Profinet, DeviceNet, AS-i, IO-Link) | Connect remote I/O, drives, HMIs | A network cable crushed in a door stops a whole section |
| **Control power** (24 VDC supplies, 120 VAC control transformers, fuses, breakers) | Powers the sensors, relays and I/O | A blown 24 V fuse kills a bank of sensors: the first thing to check when many things fail at once |

## Signals

- **Digital (discrete)**: on or off. **24 VDC** is the standard (PNP "sourcing" sensors switch +24 V to the input; NPN "sinking" switch to 0 V: a PNP sensor on an NPN input does nothing: match the type); **120 VAC** on older machines. **NO** (normally open: closes when the sensor sees the target) and **NC** (normally closed: opens when it sees it); **safety and stop circuits use NC** so a broken wire looks like a stop, not a run.
- **Analog**: **4-20 mA** (the industrial standard: 4 mA = 0% of the range, 20 mA = 100%; 0 mA = a broken wire, which is why 4 is the zero: "live zero"), **0-10 V**, RTD (a resistance), thermocouple (millivolts). A 4-20 mA loop is checked with a **milliammeter in series** (or a loop calibrator): 12 mA = 50% of the transmitter's range.
- **Pulse/frequency**: encoders (quadrature A/B pulses for speed and direction), flow meters (pulses per gallon).
- The wiring: a **wiring diagram/schematic** with wire numbers and terminal numbers; each device has a **tag** (the ISA tag: **PT-101** pressure transmitter, **LSH-202** level switch high, **ZS-303** position switch, **SE/ST** speed element/transmitter, **VT** vibration transmitter, **TE/TT** temperature; see [blueprint reading](/article/blueprint-reading-for-millwrights) for the letters) that matches the drawing, the HMI and the label on the device.

## Sensors on machinery

| Sensor | Senses | Range / rules | Mounting and adjustment |
|---|---|---|---|
| **Inductive proximity** (the barrel with an LED) | Metal (ferrous best) within a few mm | Sensing range by size: M8: 1-2 mm, M12: 2-4 mm, **M18: 5-8 mm**, M30: 10-15 mm (flush-mount shorter, non-flush longer; non-ferrous targets at 30-50% of the range) | Set the gap at **50-80% of the rated range** (a prox set at its limit drops out with vibration); flush types can be mounted flush in steel, non-flush need clearance around the face; the LED shows the state; a target (a bolt head, a cam, a gear tooth) passing at speed needs the sensor's switching frequency checked; do not use a prox as a mechanical stop |
| **Capacitive proximity** | Anything (plastic, liquid, grain) within a few mm-25 mm; through a non-metal wall | Sensitivity adjustable | Set with the potentiometer to see the product and not the hopper wall; drifts with humidity and build-up |
| **Photoelectric** (photo-eye): **through-beam** (emitter and receiver opposite), **retroreflective** (a reflector; polarised for shiny objects), **diffuse** (reflects off the object) | Presence of anything that breaks or reflects the beam; ranges from inches to 100+ ft (through-beam) | Through-beam is the most reliable for dust and distance; diffuse is the fussiest | Align with the alignment LED/the signal-strength indicator (the beam centred, the margin high), lock the bracket, keep lenses and reflectors clean (a wipe on the route), shield from sun and other eyes, a **light-on / dark-on** selector sets the output sense; a reflector that is bumped 5° kills a retroreflective eye |
| **Limit switch** (mechanical arm/roller/plunger) | Position by physical contact | | Mount so the actuator is hit within its travel and not driven past it (a stop elsewhere); roller arms set to the cam; the arm not used as a stop; watch for water in the head; NC for safety functions |
| **Safety interlock switch** (tongue, coded magnetic/RFID, hinge) on guards | Guard closed | | Aligned per the maker (RFID coded switches have a sensing distance and a misalignment tolerance); mounted with tamper-proof screws; never replaced by a plain sensor |
| **Encoder** (incremental or absolute) on a shaft | Speed, position, direction | Pulses per revolution (e.g. 1024) | Coupled with a **flexible** coupling to the shaft (side load kills the encoder's bearing), the coupling aligned; shielded cable; a hollow-shaft encoder with its anti-rotation arm free to float |
| **Speed switch / zero-speed** (a prox counting a target, or a shaft-mounted unit) | Rotation of a conveyor tail pulley, a screw, an elevator | | The target gap set; the time delay in the PLC lets the belt come up to speed |
| **Pressure switch / transmitter** | Pressure (on/off, or 4-20 mA) | Set point and differential (deadband) on a switch; range on a transmitter | Mounted with an isolation valve and a snubber on pulsating lines; not on the pump's discharge nozzle where it shakes; the transmitter's range matched to the process (a 0-100 psi transmitter on a 500 psi line is destroyed) |
| **Temperature**: **RTD** (Pt100, a resistance) and **thermocouple** (J, K), thermostats, bearing temperature detectors | Temperature | RTD: accurate, 3-wire; thermocouple: wider range, polarity matters (the coloured lead is negative on US thermocouples: red is negative) | Installed in a thermowell or against the bearing housing with thermal paste; the extension wire of the same type; a bearing RTD in the housing's drilled hole with a spring clip |
| **Level**: float switches, capacitance, ultrasonic, radar, rotating paddle (bins), vibrating fork, tilt switch, tuning fork | Level in tanks, bins, sumps | | Paddles and forks mounted where the material will not bury or bridge; ultrasonics need a clear cone and no foam; floats free to move and the right density |
| **Flow**: switches (paddle, thermal), meters (magnetic, turbine, vortex, Coriolis, ultrasonic) | | | Straight pipe before and after (5-10 diameters), orientation, full pipe |
| **Vibration transmitter / accelerometer** (4-20 mA velocity, or a 100 mV/g sensor to a monitor) | Machine vibration | | Mounted on a **flat, clean, stud or adhesive pad** on the bearing housing in the load direction; a magnet mount on a curved, painted surface reads garbage; the cable strain-relieved |
| **Current sensor / power monitor** on a motor | Load | | |
| **Plugged chute / tilt switch, belt rip, misalignment switches** on conveyors | | | See [conveyor safety](/article/conveyor-safety-and-guarding) |

Sensor mounting rules: **rigid** brackets (a bracket that vibrates gives a chattering input), **protected** from impact and washdown (guards, cable glands, IP rating), **cable** strain-relieved and away from motor cables, **connectors** (M12) tight with the seal, the **tag** on the sensor, and the **gap/alignment** written on the drawing or the bracket so it can be re-set after a change. When you replace a sensor: same type (PNP/NPN, NO/NC, range, connector), same position, and tell the controls tech (some sensors are configured in IO-Link or the safety controller and need a teach/reset).

## Why the machine will not run: a method

1. **Read the HMI**: the active alarm or fault (e-stop pressed, guard open, drive fault, high temperature, low level, a permissive not made); acknowledge/reset if it is cleared. The alarm text usually names the device (the tag) and the location.
2. **Check the physical thing named**: the guard actually closed and the interlock aligned (the switch's LED); the e-stop **released** (turn to reset; all of them on the line: one pressed in a remote spot stops everything); the level/pressure actually there; the drive not faulted (its display).
3. **The permissive list** on the HMI's diagnostic screen (green/red) or in the sequence table; the first red item from the top is the one to fix (the logic usually stops at the first missing condition).
4. **I/O lights**: at the PLC rack or the remote I/O, find the input for the sensor (from the drawing's wire number/point address): LED **on** = the PLC sees 24 V on that input; a sensor whose own LED is on but the input LED is off = the wire/terminal/fuse between them; both off with the target present = the sensor or its supply; a **24 VDC fuse or breaker** feeding a group of sensors tripped = many inputs dead at once. On the output side: an output LED on but the starter not pulling in = the wiring, the coil, the overload relay's contact (**the overload tripped** on a starter is the classic: reset it and find out why the motor overloaded).
5. **Control power**: the control transformer fuse, the 24 V power supply's LED, the emergency-stop relay's LEDs (a safety relay shows which channel is open).
6. Mechanical: is the machine free to move (a jammed conveyor trips the drive; a seized shaft trips the overload)?
7. If the logic itself is in question (an interlock that does not make sense, a timer, a sequence stuck), **call the controls tech**: the program is theirs; do not force I/O or bypass an input.

## What not to touch

- **Never jumper, force, or bypass** a safety device (an interlock, a light curtain, an e-stop, a safety relay input) to run a machine, even to test; the people killed in guarded machines were mostly working with a bypassed interlock.
- **Forcing I/O** in the PLC (making the program see an input as on) is a controls-tech tool with its own rules; a forced input that is forgotten runs the machine with a guard open.
- **Program changes**: not yours; a "small change" without the backup and the change control is how a plant loses a line for a day.
- Terminals in a **live** panel: qualified persons only, with the PPE in [electrical safety](/article/electrical-safety-for-mechanics); reading LEDs from outside the arc-flash boundary is fine; landing a wire is not.
- Network cables and switches: do not unplug "to see".
- Instrument calibration (a transmitter's zero and span) is the instrument tech's; report a reading that disagrees with your gauge.
- Analog loops: do not break a 4-20 mA loop without knowing what else is in series (a chart recorder, a controller input).

## Working with the controls tech

Give them: the machine and the tag, what the HMI says, which LEDs you saw on and off, what you checked mechanically, what changed (a new sensor, a moved bracket, a motor replaced, a drive replaced: the parameters), and the wire/terminal numbers you looked at. Ask for: the permissive list, the sensor types and set gaps on the drawings, and a copy of the sensor settings for the machine's file. A sensor that is replaced and works "sometimes" is a gap or an alignment or a PNP/NPN mix: sort it with them before the machine is handed over.

## Common mistakes

- Bending the prox bracket "closer" until the target hits it: a broken sensor and a stopped line.
- Replacing an NC safety switch with a NO general-purpose one because "it's the same size".
- A photo-eye's reflector cleaned once a year.
- Diagnosing "the PLC is dead" when a 24 V fuse blew.
- Jumpering the guard switch to run the machine for a bearing check.
- A bearing vibration sensor on a magnet on a painted, curved housing: the alarm never sees the failure.
- Landing the thermocouple wires backwards: the bearing reads 20°C cooler than it is.

## Related

- [VFD basics for millwrights](/article/vfd-basics-for-millwrights)
- [Electrical safety for mechanics](/article/electrical-safety-for-mechanics)
- [Machine guarding and commissioning](/article/machine-guarding-and-commissioning)
- [Conveyor safety and guarding (safety switches)](/article/conveyor-safety-and-guarding)
- [Blueprint reading (P&ID and instrument tags)](/article/blueprint-reading-for-millwrights)
- [Vibration basics and ISO severity (vibration transmitters)](/article/vibration-basics-and-iso-severity)
