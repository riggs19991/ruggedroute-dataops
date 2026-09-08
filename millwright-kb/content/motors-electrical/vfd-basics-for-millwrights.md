---
title: "VFD Basics for Millwrights: What a Drive Does and the Affinity Laws, the Parameters That Matter (Min/Max Frequency, Accel/Decel, V/Hz vs Vector, Motor Nameplate Entry, Overload, Carrier Frequency), Why Motors on Drives Overheat at Low Speed, Bearing Currents and Shaft Grounding, Cable and Grounding Rules, Reading the Display and Fault Codes, Safety with Drives (DC Bus, Stopped Is Not Off)"
slug: vfd-basics-for-millwrights
category: motors-electrical
kind: reference
tags: [VFD, variable frequency drive, inverter, drive parameters, minimum frequency, maximum frequency, accel time, decel time, V/Hz, vector control, sensorless vector, carrier frequency, switching frequency, motor overload VFD, VFD low speed cooling, inverter duty motor, bearing currents, shaft grounding ring, AEGIS, insulated bearing, fluting, VFD cable, VFD grounding, drive fault codes, overvoltage fault, overcurrent fault, DC bus, VFD safety, VFD stopped not off, affinity laws VFD]
source: "Allen-Bradley PowerFlex, ABB ACS, Yaskawa and Danfoss drive manuals (parameter groups, fault codes, installation and cable requirements); NEMA MG 1 Part 30/31 (inverter-fed motors); AEGIS shaft grounding handbook and EASA guidance on bearing currents; Rockwell and ABB application notes on carrier frequency and low-speed cooling."
summary: "Enough about variable frequency drives to work safely around them and to understand what they do to the motors and bearings a millwright maintains: how a drive changes speed and what that does to a pump or fan, the handful of parameters that decide whether the machine works, why a motor at 15 Hz cooks, the shaft-current bearing damage a drive causes and the fixes, the cabling rules that stop noise and bearing damage, how to read the display and the common faults, and the rules for a drive that is 'stopped' but live."
---

## What a drive does

A VFD rectifies the incoming AC to a **DC bus** (about 650 V DC on a 460 V drive), then switches it into a variable-frequency, variable-voltage output with transistors (IGBTs) using **pulse-width modulation**: the motor sees a synthesised AC whose frequency sets the speed and whose voltage keeps the **volts-per-hertz ratio** (460 V ÷ 60 Hz = 7.67 V/Hz) constant so the motor's flux and torque stay normal. Speed = the frequency the drive makes: 30 Hz on a 4-pole motor = about 880 rpm.

For **fans and pumps** the affinity laws make a drive the biggest energy saver in a plant: **flow ∝ speed, head/pressure ∝ speed², power ∝ speed³**: a fan at 80% speed uses about **51%** of the power; a pump at 50% speed uses 12.5% (if the system has little static head; see [pump formulas](/article/pump-and-fluid-power-formulas)). For conveyors and constant-torque loads, the drive gives speed control and soft starting; the power falls in proportion to speed.

Other things a drive gives: soft start (no inrush, no belt squeal, the ratio of start current set by the accel time), controlled deceleration (with a braking resistor or a regenerative drive to absorb an overhauling load), reversing by a parameter, built-in motor overload protection, run/fault contacts and analog speed inputs for the PLC, and a display of current, speed and faults that is useful for troubleshooting.

## Parameters a millwright should know

The electrician or the controls tech programs the drive; the millwright needs to know what these do because they decide how the machine behaves and whether the motor survives:

| Parameter | What it sets | Why it matters |
|---|---|---|
| **Motor nameplate data** (rated volts, amps, Hz, rpm, hp/kW, power factor) | The drive's motor model and the overload protection | Entered wrong (the 230 V amps on a 460 V motor) and the drive's overload trips or never trips; after a motor change the **new** nameplate must be entered and an autotune done |
| **Maximum frequency / speed** | The top speed (60 Hz standard; 50 Hz for IEC motors on 60 Hz drives; over 60 Hz possible with the maker's blessing for the motor **and** the driven machine: a fan at 70 Hz draws 1.6× power and may overspeed the impeller) | Overspeeding a pump, a fan, a gearbox or a shaft-mount bearing is a mechanical failure |
| **Minimum frequency / speed** | The lowest speed the drive will run | **Cooling** (below); pumps need a minimum to make head; a conveyor's minimum for the material |
| **Accel and decel time** | Seconds from 0 to max speed and back | Too fast an accel: overcurrent trips, belt slip, shock to the load; too fast a decel: **overvoltage trips** (the load pushes energy back into the DC bus; a braking resistor or a longer decel fixes it); a long decel on a conveyor is a safety issue at the e-stop (a coast-to-stop or a brake is separate) |
| **Control mode**: **V/Hz** (the simple mode, fine for fans and pumps), **sensorless vector** (better low-speed torque and speed holding: conveyors, mixers, positive-displacement pumps), **closed-loop vector with an encoder** (precise speed/torque: hoists, winders) | | A V/Hz drive on a screw conveyor stalls at low speed; a vector drive needs an **autotune** with the motor connected (and often uncoupled) |
| **V/Hz pattern and torque boost** | Variable torque (fans/pumps: the voltage falls faster at low speed: less heat) vs constant torque; a voltage boost at low speed for starting torque | Too much boost overheats the motor at low speed |
| **Motor overload (thermal) setting** | The drive's electronic overload, from the entered FLA and a service factor % | The only overload protection the motor has on most drive circuits; it must match the motor, and a motor with a thermostat should have it wired to the drive's input |
| **Carrier (switching) frequency** | The PWM frequency, 2-16 kHz | Higher = quieter motor, more drive heating and **more bearing current**; lower (2-4 kHz) = audible whine, cooler drive, less common-mode current: the usual compromise is 4 kHz on industrial motors |
| **Stop mode**: ramp, coast, DC brake | How it stops | A ramp stop needs a resistor for a high-inertia load; a coast stop on an incline needs a mechanical brake |
| **Skip frequencies** | Bands the drive will not run in | Set to jump over a **resonance** (a speed where the machine or the piping shakes): the millwright finds the speed, the tech programs the skip |
| **Reverse enable, run permissives, speed reference source, PID** | Control logic | The reason a drive "will not run" is usually a permissive or the reference source, not the drive |
| **Flying start / catch a spinning load** | Lets the drive pick up a coasting fan | Without it, starting into a spinning fan trips overcurrent |
| Parameter **lock and the backup** | | Record the parameter set before a drive is replaced; a "factory reset" wipes the motor data |

## Why motors on drives overheat

- **Cooling**: a TEFC motor's fan is on the shaft: at **half speed it moves a quarter of the air**; a standard motor running a constant-torque load below about **50% speed (30 Hz) for long periods** overheats; **inverter-duty motors** are rated for a **speed range** (e.g. 10:1 CT means 6-60 Hz at full torque with their own cooling margin, or 1000:1 with a separate blower); fans and pumps (variable torque) are fine at low speed because the load falls faster than the cooling.
- **Waveform**: the PWM output has voltage spikes (up to 2× the bus, 1,300 V+) that stress the insulation, especially on **long motor cables** (over about 50-100 ft: reflected waves), and harmonics that add heating; inverter-duty motors (NEMA MG 1 Part 31) have insulation rated for the spikes; a standard motor on a long cable wants an output reactor or a dV/dt filter.
- **Torque boost too high**, a wrong V/Hz, an overload setting that is wrong, a blocked fan cover: the same as any motor.
- Check: the motor's frame temperature at its running speed; the drive's displayed current; the speed range it actually runs in.

## Bearing currents (the millwright's VFD problem)

The PWM output has a **common-mode voltage** that couples through the motor's capacitances to the shaft; the shaft voltage discharges through the **bearing's oil film** thousands of times a second: **EDM pitting → fluting** (the washboard raceway), grease turned black, a bearing that fails in months (see [bearing failure analysis](/article/bearing-failure-analysis)). Signs: a bearing failure pattern of fluting on a VFD-driven motor, often the **non-drive end** first, repeated failures after replacement, a rising vibration at bearing frequencies, and a shaft voltage measurable with a brush and an oscilloscope (over about 5-10 V peak is trouble).

![Bearing currents and the fixes: shielded cable, grounding ring, insulated bearing](/img/motors-electrical/vfd-bearing-currents.svg)

*Bearing currents and the fixes: shielded cable, grounding ring, insulated bearing*

Fixes (the drive and the motor together):

1. **Shaft grounding ring** (AEGIS SGR or similar carbon-fibre brush ring, or a maintenance-free brush) on the motor shaft, usually at the drive end, giving the current a path to the frame instead of through the bearing; a **conductive** grease under it; install per the ring's instructions (the shaft area cleaned to bare metal and coated with the conductive epoxy where specified; the ring's fibres on a clean shaft, not painted or rusted).
2. **Insulated bearing** (a ceramic-coated outer ring or a hybrid ceramic-ball bearing) at the **opposite drive end** (with the grounding ring at the drive end on motors over about 100 hp or on 575 V); insulating both ends and none of the shaft pushes the current down the coupling into the driven machine's bearings: a grounding ring plus one insulated bearing is the standard.
3. **Cable and grounding**: **VFD-rated shielded cable** (symmetrical grounds and a shield) from the drive to the motor, with the shield terminated **360°** at both ends (a gland/clamp, not a pigtail), the motor frame bonded to the drive's ground bar with a short, wide conductor; the driven machine bonded to the motor frame (a bonding strap across the coupling insulator or the base) so the current has a path other than the coupling.
4. **Lower the carrier frequency** where the noise is tolerable (2-4 kHz).
5. Common-mode chokes/filters at the drive output; a dV/dt filter or a sine filter on long cables.
6. Insulated couplings do **not** protect the motor bearing; they protect the driven machine.

## Cable and installation rules (why the drive "faults for no reason")

- Motor cable: VFD-rated, shielded, in its own conduit/tray **separated** from control and signal cables (at least 8-12", crossing at 90°); the shield to the drive's ground bar and the motor's frame at both ends; the cable as short as practical.
- Input: a line reactor or DC choke where the supply is stiff or the drive is large (harmonics, drive protection); the drive's ground to the panel ground bar.
- Control wiring (start, speed reference 4-20 mA / 0-10 V) in shielded twisted pair, the shield grounded at **one** end (the drive).
- Drive cooling: the enclosure's fan filters clean; a drive that runs hot derates and faults; ambient under 40°C (104°F) inside the enclosure.
- **Never megger a motor with the drive connected**; disconnect the motor leads at the drive's output terminals (see [megger testing](/article/megger-and-basic-motor-testing)); never switch a contactor on the output while running (a disconnect on the motor side needs an interlock to stop the drive first).
- Motors under 1 hp on a 460 V drive, or motors with a shorter insulation life, want an output reactor.

## Reading the display

The keypad shows a **status** (Ready, Running, Faulted, Stopped, At Speed), the **output frequency** (Hz) or speed (rpm), **output current** (A: compare with the motor's FLA and watch the trend), **DC bus voltage** (about 1.35 × the line: 620-680 V on 480 V), **output voltage**, torque %, and the **fault history** (the last several faults with the values at the time: the first thing to read on a "the drive tripped" call). Typical faults:

| Fault | Usual cause |
|---|---|
| **Overcurrent (OC)** | Accel too fast, a jammed load, a shorted motor/cable, too high a boost, a bad autotune; ground fault |
| **Overvoltage (OV) on the bus** | Decel too fast (regeneration), an overhauling load, a high line voltage; add a braking resistor or lengthen the decel |
| **Undervoltage (UV)** | Supply dip, a lost phase, a blown input fuse |
| **Motor overload (OL1)** | The motor is running above its FLA setting for too long: a mechanical overload, a wrong parameter, low speed at full torque |
| **Drive overload / overtemperature (OH)** | Drive cooling (filters, fan), ambient, carrier frequency too high, oversized load |
| **Ground fault (GF)** | Insulation failure in the motor or cable, water in the box |
| **Output phase loss** | A motor lead open, a bad contactor on the output |
| **Input phase loss** | A supply phase gone |
| **Motor stall / speed deviation** | A vector drive that cannot hold speed: overload, a wrong autotune |
| **External fault / safe torque off (STO)** | The safety circuit or an external interlock opened: the e-stop, a guard switch, a motor thermostat |

"The drive says it's running but the motor is not turning": the drive is running at 0 Hz (the reference is 0), or the motor is disconnected (output phase loss not enabled), or the load is seized (the current will show it).

## Safety around drives

- **Stopped is not off**: a drive in "Stop" has full line voltage inside and can have voltage on the motor terminals (some modes hold DC on the motor); the motor can start on a remote signal or an auto-restart-after-fault parameter. **Lockout is the upstream disconnect**, verified at the drive's input terminals with a meter, **and then a wait**: the **DC bus capacitors hold 650 V for minutes** after power-off (the manual's discharge time, typically **5-15 minutes**; the charge LED must be out and the bus measured below 50 V before touching anything inside).
- STO (safe torque off) inputs are a safety function for machine guarding, not a lockout for maintenance work inside the motor or the machine.
- Drives can **auto-restart** after a fault or a power dip if the parameter is set: a locked-out motor is the only safe motor.
- Do not open a drive's cover to "look" while it runs; the bus bars are exposed; a drive's fan can start any time.
- The millwright's interface with the drive is the display, the run/stop station, and the mechanical results; parameter changes are the controls person's job and are recorded.

## Common mistakes

- A standard TEFC motor at 12 Hz on a screw conveyor all day: burned in a season.
- A new motor installed and the old motor's data left in the drive.
- Bearings replaced three times on a VFD-driven fan motor before anyone measured the shaft voltage.
- Unshielded THHN in a tray with the control wiring: the PLC inputs flicker and the bearings flute.
- A decel time shortened to 2 s to "stop it faster": overvoltage trips every stop.
- Working in the motor box with the drive "stopped".
- Meggering the motor from the drive terminals: a dead drive.

## Related

- [Reading a motor nameplate (inverter duty)](/article/reading-a-motor-nameplate)
- [Megger and basic motor testing](/article/megger-and-basic-motor-testing)
- [Bearing failure analysis (fluting)](/article/bearing-failure-analysis)
- [Electrical safety for mechanics](/article/electrical-safety-for-mechanics)
- [PLC and instrumentation awareness](/article/plc-and-instrumentation-awareness)
- [Pump and fluid-power formulas (affinity laws)](/article/pump-and-fluid-power-formulas)
