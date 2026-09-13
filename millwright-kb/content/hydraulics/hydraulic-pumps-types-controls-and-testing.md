---
title: "Hydraulic Pumps: Gear, Vane and Piston Types Compared, Variable-Displacement Controls (Pressure Compensator, Load Sensing, Torque Limiter), Reading the Nameplate and Displacement Math, the Case-Drain and Flow-Meter Tests That Prove a Pump Is Worn, Cavitation vs Aeration, Start-Up After a Pump Change and Pump Failure Analysis"
slug: hydraulic-pumps-types-controls-and-testing
category: hydraulics
kind: reference
tags: [hydraulic pump, gear pump, internal gear pump, gerotor, vane pump, intra-vane, vane cartridge, piston pump, axial piston, swashplate, bent axis, radial piston, variable displacement, pressure compensator, load sensing pump, torque limiter, power limiter, horsepower limiter, pump displacement, pump nameplate, volumetric efficiency, case drain test, case drain flow, flow meter test, hydraulic tester, pump wear, cavitation, aeration, inlet vacuum, pump start-up, pump priming, pump rotation, pump failure analysis, scored side plates, slipper wear, valve plate, pump shaft seal]
source: "Eaton Vickers Industrial Hydraulics Manual and Mobile Hydraulics Manual (pump types, efficiencies, inlet conditions, compensator setting); Parker and Bosch Rexroth axial piston pump service manuals (case drain limits, start-up and commissioning); Danfoss and Sauer hydrostatic service literature; Fluid Power Society (IFPS) mechanic and technician study manuals (pump testing procedure); Noria and Machinery Lubrication pump failure analysis guidance."
summary: "How each pump type works, wears and fails, what the controls on a variable-displacement pump actually do and in what order they are set, how to read a nameplate and calculate what the pump should deliver, the two tests that separate a worn pump from a circuit problem (case drain flow and flow at pressure), the difference between cavitation and aeration by sound and damage, the start-up sequence that keeps a new pump alive, and what the wear pattern on a dead pump tells you."
---

## The rule that governs every pump test

A pump makes **flow**. Resistance makes pressure. So a pump is judged by **how much flow it still delivers at working pressure**, never by the gauge reading alone: a badly worn pump can still show full pressure against a dead-headed cylinder because a trickle of flow is enough to hold a gauge, and the machine is slow. The whole of this article comes back to that one test.

```
   Theoretical flow (gpm) = displacement (in³/rev) × rpm ÷ 231
   Volumetric efficiency ηv = actual flow at pressure ÷ theoretical flow      (new: 0.90-0.97; replace at about 0.80-0.85)
   Input hp = gpm × psi ÷ (1714 × overall efficiency)                          (overall 0.80-0.90 new)
   Metric: L/min = cm³/rev × rpm ÷ 1000
```

## Pump types

![Bent-axis piston pump sectioned: the pistons stroke in the barrel because it sits at an angle to the shaft](/photos/hydraulics/piston-pump-cutaway.jpg)

*Bent-axis piston pump sectioned: the pistons stroke in the barrel because it sits at an angle to the shaft. Photo: StromBer, CC BY 3.0, via commons*

| Type | How it works | Pressure (continuous) | Efficiency (new) | Tolerates | Typical use | How it fails |
|---|---|---|---|---|---|---|
| **External gear** | Two meshing gears carry oil round the outside of the teeth from inlet to outlet; the mesh seals it | 2,500-3,500 psi (170-240 bar); some to 4,000 | ηv 0.85-0.92 | Dirt best of all, aeration moderately, cheap to replace | Mobile equipment, log splitters, power units, lube pumps | Wear plates (side plates) score, then the gears cut into the housing on the inlet side ("track"); flow falls gradually; noisy at the end |
| **Internal gear / crescent** | Pinion inside a ring gear, a crescent separates inlet from outlet | 3,000-4,500 psi | 0.90-0.95 | Dirt fairly well | Quiet industrial units, presses, machine tools, injection moulding | Crescent and side plates wear; quiet until suddenly weak |
| **Gerotor** | Inner rotor one tooth fewer than the outer, no crescent | To about 2,000 psi | 0.80-0.90 | | Charge pumps, lube, low-pressure circuits | Rotor tips score |
| **Vane (fixed)** | Vanes in a slotted rotor slide against a cam ring; a **cartridge** (ring, rotor, vanes, port plates) is the wear kit | 2,000-3,000 psi (intra-vane to 3,000-4,000) | 0.90-0.95 | Dirt poorly (vane tips and ring), aeration badly | Industrial power units, machine tools, injection moulding | Ring scores or ripples, vane tips wear, port plates score; whines; replace the cartridge (1-2 hours) |
| **Vane (pressure-compensated variable)** | The ring is moved off-centre by a spring; system pressure pushes it back to reduce displacement at the set pressure | To about 2,000-2,500 psi | 0.85-0.92 | | Small industrial units where a fixed pump would overheat | Compensator spring, ring pivot; hunting |
| **Axial piston, swashplate** | Pistons in a rotating barrel ride shoes (slippers) on an angled plate; the angle sets the stroke, so the displacement can be varied by tilting the plate | 3,000-5,000 psi (210-350 bar); some to 6,000 | 0.93-0.97 | Dirt badly (slippers, valve plate, control spool); aeration badly | Presses, mobile main pumps, hydrostatic drives, injection moulding | Slipper faces and swashplate score, valve plate and barrel face score, piston-to-bore wear; case drain rises; hot case; failure spreads metal everywhere |
| **Axial piston, bent axis** | The barrel is angled to the shaft; pistons stroke by the angle | 5,000-6,500 psi | 0.95-0.97 | | Mobile motors and high-pressure pumps (winches, excavator travel) | Same as above; tapered pistons and rings |
| **Radial piston** | Pistons stroke radially against a cam or eccentric | 6,000-10,000 psi (400-700 bar) and above | 0.95+ | | Presses, clamping, test rigs, low flow at very high pressure | Cam wear; individual piston check valves |
| **Hand pump** | Single or two-stage piston | To 10,000 psi | | | Jacks, test, emergency | Check valves |

**Screw pumps** (two or three meshing screws) are the quiet, pulse-free choice for lube oil and fuel; low pressure. **Multiple pumps** on one shaft (a **tandem** or **double** pump: two gear stages, or a piston main pump with a gear charge pump on the back) are common on mobile machines; each section has its own outlet and often its own circuit.

## Displacement controls on a variable pump

![Pressure-compensated and load-sensing pump controls](/img/hydraulics/pump-controls.svg)

*Pressure-compensated and load-sensing pump controls*

A variable-displacement pump has a **control** (a small spool valve bolted on the side) that ports oil to a **stroking piston** against a **bias spring** to move the swashplate. Read the control from its schematic box; the adjusting screws are usually under caps and each one has a different job.

| Control | What it does | How to set it | Symptom when wrong |
|---|---|---|---|
| **Pressure compensator** (the standard control) | Destrokes the pump to near zero flow when the outlet reaches the set pressure; holds that pressure with only the leakage flow; makes almost no heat at stand-by | With the outlet dead-headed (a valve closed) and a gauge on the outlet, turn the compensator screw to the design pressure; the relief valve is set **150-300 psi (10-20 bar) higher** as a backup | Compensator above the relief: the relief dumps full flow, the tank boils in an hour. Compensator too low: weak machine. Compensator stuck: full flow over the relief (hot) or no pressure |
| **Load sensing (LS)** | A second spool holds the pump outlet a fixed **margin** (typically 200-350 psi / 14-24 bar) above the highest load pressure fed back by the LS line; the pump only makes the flow the valves ask for | Set the **margin** with the LS port vented to tank (the outlet then reads the margin), then the compensator (the maximum) with the LS port blocked or the function stalled; see [load-sensing and proportional systems](/article/load-sensing-proportional-and-servo-systems) | Lost LS signal (leak, blocked orifice): the pump idles at margin pressure and nothing moves, or it goes to full pressure. Margin too low: slow, sluggish under multiple functions |
| **Torque / power (horsepower) limiter** | Reduces displacement as pressure rises so pressure × flow stays under the prime mover's power; a curve, often two springs | Per the maker's curve; usually left alone | Engine stalls under load (limiter set too high or springs wrong); machine slow at high pressure (set too low) |
| **Remote compensator** | The compensator pilot is vented through an external port to a remote relief or a proportional valve: several pressure settings from the console | The remote valve sets the pressure; the pump's own compensator must be **higher** than any remote setting | Remote line leak: pump goes to the local compensator setting |
| **Electro-proportional displacement control** | A solenoid sets the swashplate angle (or the pressure) from a current signal, with a swashplate feedback | Card or PLC parameters; a null and a max adjustment | Feedback sensor drift: wrong flow for the command |
| **Manual / servo displacement (hydrostatic pumps)** | A lever or pilot pressure sets the swashplate both sides of centre (over-centre pumps reverse flow) | Neutral adjustment with the machine on stands; see [hydrostatic drives](/article/hydraulic-motors-and-hydrostatic-drives) | Creep in neutral |

Order of adjustment on a system with a compensated pump: **relief valve first** (the pump destroked or the compensator screwed in fully so it does not interfere), then **the compensator 150-300 psi below the relief**, then the LS margin, then the branch valves. Both screws locked, both values written on the pump.

## The nameplate

A pump plate carries the maker's model code (which encodes the type, displacement, control, rotation, shaft, ports and seals), the **displacement** (cm³/rev or in³/rev), the **maximum speed**, the **rated and peak pressure**, the **rotation** (viewed from the shaft end: CW or CCW, or an arrow on the housing), a serial number and often the date. Decode it against the maker's catalogue before ordering anything: a model with the wrong rotation, control or shaft spline bolts up and does not work.

Worked example: an axial piston pump, 45 cm³/rev (2.75 in³/rev) at 1,800 rpm. Theoretical flow = 2.75 × 1,800 ÷ 231 = **21.4 gpm** (81 L/min). New at 3,000 psi with ηv 0.95: 20.3 gpm. If the flow meter reads 16 gpm at 3,000 psi the pump is at 75% volumetric efficiency: **worn out**. Input power at 3,000 psi and 20 gpm: 20 × 3,000 ÷ (1714 × 0.85) = **41 hp**; the 40 hp motor on it is at its limit, and a compensator set above design overloads it.

## Test 1: case drain flow (piston and some vane pumps)

![Case drain flow test: measure the leakage from the pump case](/img/hydraulics/case-drain-flow-test.svg)

*Case drain flow test: measure the leakage from the pump case*

Internal leakage past the pistons, slippers and valve plate collects in the pump case and returns to tank through the **case drain line**. That flow is a direct measure of internal wear.

1. Warm the system to operating temperature (cold oil halves the leakage and hides a worn pump).
2. Lockout and bleed; disconnect the case drain line at the tank end (or fit a tee with a flow meter or a hose into a calibrated container). The case must stay **full**: keep the drain outlet above the pump's top port, and never restrict it (a restricted case drain blows the shaft seal: the case is rated for about 15-30 psi / 1-2 bar).
3. Run the pump at working pressure against a load or a dead-headed function (the compensator holding pressure), and time the flow for 30-60 seconds. Repeat at low pressure for comparison.
4. Judge: **new pump 1-3% of rated flow; up to about 10% acceptable; over 10-15% at working pressure: replace or rebuild**. The maker's service manual gives the exact number for that model (for a 20 gpm pump: new about 0.5 gpm, worn at 2-3 gpm). A leak that rises quickly across a few weeks is a pump dying, whatever the absolute number.
5. Feel the case: a case drain hotter than the outlet by 20°F or more (10°C) means high internal leakage.

## Test 2: flow at pressure (any pump)

The definitive test, with a **hydraulic tester** (flow meter, load valve and gauge in one body) or a flow meter plus the machine's own load.

1. Tee the tester into the pump outlet line (after the relief if you want the delivered flow, before it to test the pump alone), the tester's load valve fully open, the return to tank in a full-size hose.
2. Run at rated rpm, oil at operating temperature; read the flow at near-zero pressure: that is the pump's maximum delivery (compare with theoretical: a low number here at no pressure is a **suction** problem or wrong rpm, not wear).
3. Close the load valve slowly to raise the pressure in steps (500, 1,000, 1,500 psi, up to working pressure but **never above the relief setting**); record the flow at each step.
4. Plot or table it: a healthy pump loses only a few percent of flow from zero to full pressure; a worn pump's flow drops steeply as pressure rises. Below **about 80-85% of theoretical at working pressure, the pump is worn**. If the flow at the pump is good but the machine is slow, the loss is downstream (a bypassing cylinder, a relief cracking early, a valve leak): go to [advanced diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics).

![Flow against pressure: a worn pump falls away as the pressure rises](/img/hydraulics/pump-flow-vs-pressure.svg)

*Flow against pressure: a worn pump falls away as the pressure rises*

A cheaper version without a flow meter: time a cylinder of known bore through its stroke at no load and at full load; flow = area × stroke ÷ time (in³/min ÷ 231 = gpm). A flow that halves under load points at the pump or a bypassing actuator; the case drain test then separates them.

## Cavitation vs aeration

| | Cavitation | Aeration |
|---|---|---|
| What it is | The inlet pressure falls below the oil's vapour pressure; vapour bubbles form and **implode** at the outlet | Air bubbles drawn in or mixed in and **compressed** at the outlet |
| Sound | A steady high-pitched **whine or scream** that changes with rpm and inlet restriction | An irregular **rattle, crackle, knocking**; like gravel |
| Oil | Looks normal in the tank | **Foam** on the tank, milky or bubbly oil, spongy actuators |
| Pressure gauge | Steady or slightly low | Needle flickers, erratic |
| Cause | Restricted suction (a clogged strainer, a collapsed hose, a closed valve, a kinked line), oil too thick (cold, wrong grade), pump too high above the tank, rpm too high, a plugged breather (vacuum in the tank), a suction line too small or too long | A leaking suction joint (sucks air, does not drip oil), low oil level, a return line above the oil, a worn pump shaft seal, a cylinder rod seal drawing air on the return stroke, a whirlpool at the suction, oil with poor air release |
| Damage | **Pitting** on the outlet side of the port plate, cam ring or gear housing: a frosted, sand-blasted look with sharp-edged craters; flow loss | Pitting too but milder, **oil oxidation and varnish** (compressed air heats to hundreds of degrees: micro-dieseling), burned seals, noise |
| Test | A **vacuum gauge on the inlet**: most pumps want no more than **5 in Hg (127 mm Hg) for piston, 5-7 for vane, 7-10 for gear** at operating temperature; over that is a restriction (check the strainer first) | Spray a little oil or smear grease on each suction joint while running: the noise stops for a moment when the leak is sealed; check the level and the return-line position |

Either one destroys a pump in weeks: find the cause on the day you hear it.

## Start-up after a pump change

![Industrial power unit: reservoir, motor-pump sets, return filters and gauges; the case drains and suction are the start-up checks](/photos/hydraulics/power-unit.jpg)

*Industrial power unit: reservoir, motor-pump sets, return filters and gauges; the case drains and suction are the start-up checks. Photo: Sensenschmied, CC BY-SA 3.0, via commons*

1. **Confirm the pump**: model, displacement, rotation (the arrow on the housing; an electric motor's rotation checked with a bump before the coupling is fitted), shaft and seal type, port sizes. Running a pump backwards for seconds can destroy the shaft seal and the vanes.
2. **Flush the system first** if the old pump failed (its metal is in every line): see [flushing after a failure](/article/filters-fluid-and-contamination). New filter elements everywhere. A new pump into a dirty system dies in weeks; that is the commonest "the new pump was faulty" story.
3. **Fill the case** through the highest case port with clean filtered oil (piston pumps and many vane pumps: a dry case burns the slippers in the first minute). Connect the case drain to the **top** port so the case stays full, the drain running to tank **below** the oil level with no restriction.
4. Fill the suction line and prime; open the suction valve (a lockable valve with a switch on many units: closed = pump death); check the breather and the level.
5. **Back the relief valve out** or set the compensator low, so the pump starts unloaded; open the directional valves to tank if possible (an open-centre spool, or a manual bypass).
6. **Jog** the motor for one second, check rotation, then run for a few seconds and stop: listen. Repeat while the pump primes (a gear pump primes in seconds; a piston pump may need the outlet cracked to bleed the air). Never run a dry, screaming pump more than a few seconds.
7. Run unloaded 10-15 minutes, bleed the air at the highest points and at the actuators (cylinders cycled slowly, full stroke, several times), watch the tank for foam and the level dropping as the lines fill: top up.
8. Raise the relief to the design setting, then the compensator 150-300 psi below it, then any remaining valves; load the machine in stages; check case drain temperature and flow, noise, leaks; change the filters again after 24-50 hours, and sample the oil.
9. Write the settings, the date, the hours and the pump serial number on the machine log.

## Failure analysis: reading a dead pump

![Vane rotor and sliding vanes opened up (a vane compressor, same principle): vane tips and the ring are the wear parts](/photos/hydraulics/vane-pump.jpg)

*Vane rotor and sliding vanes opened up (a vane compressor, same principle): vane tips and the ring are the wear parts. Photo: Original uploader was Xlory at fr.wikipedia, CC BY-SA 3.0, via commons*

| What you see | Cause |
|---|---|
| Side plates / port plate **scored with fine circular grooves**, gears or barrel face scored to match | **Contamination** (hard particles): filters bypassing, dirty new oil, a failed component upstream, a breather missing |
| **Frosted, pitted** surfaces on the outlet side of the housing, cam ring, port plate | **Cavitation** |
| Pitting plus dark varnish, burned or hardened seals, dark oil | **Aeration** and overheating |
| Gear housing cut deeply on the inlet side (a track), shaft bushings worn | Normal long-life wear, or high pressure beyond rating, or misalignment loading the shaft |
| Vane tips rounded and chipped, cam ring rippled (washboard) | Thin oil (hot, wrong grade), pressure beyond rating, cavitation |
| Vanes broken, rotor slots wallowed | Contamination lock, running the vane pump backwards, aeration pounding |
| Slippers (piston shoes) torn off or their faces galled, swashplate scored | **Dry start** (case not filled), cavitation, low oil viscosity, over-speed, a blocked case drain |
| Barrel face and valve plate deeply scored, bronze smeared | Contamination; oil too thin; over-pressure |
| Piston bores scored, pistons seized | Contamination; oil breakdown; extreme heat |
| **Shaft seal blown** out, oil from the shaft | Case pressure too high: a restricted or too-small case drain line, a case drain connected to a pressurised return, or a worn pump pumping into its own case |
| Shaft broken at the keyway or spline, spline fretted (red dust) | Misalignment, coupling loose or wrong, torsional shock; no grease on the spline |
| Shaft sheared cleanly with a smooth fatigue face | Reversing shock loads, coupling misalignment; check the coupling gap and alignment |
| Bearing failed, shaft blue | Side load from a belt drive on a pump not rated for it, misalignment, no lubrication (case not full) |
| Housing cracked at a port | Over-torqued fitting, water freezing, a pressure spike (a valve slamming shut with no accumulator or relief close by) |

Keep the failed parts and photograph them; the analysis decides whether the fix is a pump or a system change.

## Common mistakes

- Judging the pump by the pressure gauge: full pressure against a stalled cylinder proves nothing about flow.
- Replacing a pump that was cavitating because the strainer was blocked: the new one screams too.
- Not filling the case of a piston pump: it lasts one minute.
- Running a new pump in the old pump's metal.
- Compensator set above the relief: full flow over the relief, the tank at 180°F, everyone blaming the cooler.
- Testing a "weak pump" on cold oil: it passes; at temperature it fails.
- Restricting the case drain (a small fitting, a long thin hose, a filter with no bypass) and blowing the shaft seal.
- Ordering by "a 20 gpm pump" without the rotation, shaft and control code.

## Related

- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Load-sensing, proportional and servo systems](/article/load-sensing-proportional-and-servo-systems)
- [Hydraulic motors and hydrostatic drives](/article/hydraulic-motors-and-hydrostatic-drives)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
- [Hydraulic fluids: types and compatibility](/article/hydraulic-fluids-types-and-compatibility)
- [Pump and fluid-power formulas](/article/pump-and-fluid-power-formulas)
