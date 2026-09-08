---
title: "Thermography, Ultrasound and Oil Analysis as Condition Monitoring: Infrared Camera Basics (Emissivity, Reflections, Distance), What to Scan (Bearings, Motors, Couplings, Electrical, Steam Traps, Refractory) and the Temperature Rules, Airborne and Contact Ultrasound (Leaks, Bearings, Greasing by Ultrasound, Electrical Discharge, Steam Traps), How the Three Fit with Vibration, Building a Route and a Decision Table"
slug: thermography-ultrasound-and-oil
category: condition-monitoring
kind: reference
tags: [thermography, infrared camera, IR camera, thermal imaging, emissivity, reflected temperature, IR gun, bearing temperature, motor temperature, electrical thermography, hot connection, delta T, steam trap thermography, refractory inspection, ultrasound, ultrasonic detector, airborne ultrasound, contact ultrasound, ultrasonic leak detection, ultrasound bearing, greasing by ultrasound, ultrasonic steam trap, ultrasonic electrical, corona, arcing, condition monitoring technologies, PdM route, predictive maintenance, decision table condition monitoring]
source: "FLIR and Fluke thermography guides (emissivity tables, measurement practice); Infraspection Institute and NETA guidance on electrical thermography temperature rules (delta T criteria); UE Systems and SDT ultrasound application guides (leak, bearing, greasing, electrical, steam trap); NFPA 70B (electrical maintenance thermography); the oil analysis article for the third technology."
summary: "The other two eyes of a condition-monitoring program beside vibration and oil analysis: how to use an infrared camera or gun so the temperature you read is real, what temperatures and temperature differences mean on bearings, motors, couplings, electrical gear, steam traps and refractory, what an ultrasonic detector hears and how it finds leaks, failing bearings, the right amount of grease and electrical faults, and a table of which technology finds which failure so a route uses the right one."
---

## Infrared thermography

![Thermal comparison of twin bearings and an ultrasound dB trend](/img/condition-monitoring/thermography-and-ultrasound.svg)

*Thermal comparison of twin bearings and an ultrasound dB trend*

### Getting a real temperature

An IR camera or gun measures the **infrared energy leaving a surface** and converts it to a temperature assuming an **emissivity** (how well the surface radiates: a matte black surface 0.95; painted or oxidised steel 0.8-0.95; **bare shiny metal 0.1-0.3**: it reflects the room and reads far too low, and it reflects you, the lights and the sun). Rules:

1. **Set the emissivity** for the surface (paint 0.95, oxidised steel 0.8, rubber 0.95, oil 0.9, concrete 0.9, shiny aluminium/stainless/copper 0.1-0.3: these cannot be measured reliably) or put a **known-emissivity target** on the object: a piece of black electrical tape or a spot of flat black paint on a bearing housing or a bus bar (with the power off), then read the tape (0.95).
2. **Reflected temperature**: shiny objects show the reflection of hot or cold things around them (a bus bar "hot spot" that is the reflection of the lamp); move, change the angle, and see if the spot moves: a reflection moves; set the camera's reflected temperature compensation.
3. **Distance and spot size**: an IR gun's spot grows with distance (a 12:1 gun reads a 1" spot at 12" and a 10" spot at 10 ft, averaging the bearing with the air around it); get close, or use a camera and read the pixel; a camera's smallest measurable spot is several pixels.
4. **Atmosphere and windows**: steam, dust, smoke and glass block IR (glass is opaque to long-wave IR: you cannot read through a window; IR-transparent inspection windows are made for panels); rain and wind cool surfaces.
5. **Load and time**: an electrical connection only heats **under load** (scan at peak load, at least 40% of rated); a bearing needs an hour to stabilise; compare like with like (the same load, the same ambient).
6. **Compare, do not just measure**: the useful number is usually the **difference** between similar components (three phases of a starter, two bearings of the same pump, the same bearing last month).

### What to scan and the rules

| Target | What you look for | Rule of thumb |
|---|---|---|
| **Rolling bearings** (housing surface near the bearing) | The absolute temperature and the difference from the other bearing/last time | Normal 100-160°F (40-70°C) housing; **alarm above about 180°F (80°C)** housing (the bearing itself is 10-20°F hotter) or a rise of 20-30°F over the trend; a sudden 30°F+ jump = lubrication or a defect: act |
| **Electric motors** | The frame temperature pattern (a hot spot on the frame = a winding or a blocked cooling path), the bearing ends, the terminal box | A TEFC frame at 80-100°C under load can be normal for a class F motor at full load; compare the two ends and the pattern; a **hot terminal box** = a bad lead connection |
| **Couplings** | A coupling warmer than the shafts | A grid or gear coupling running hot (30°F+ above the housings) = misalignment or dry; a disc coupling hot = misalignment |
| **Gearboxes** | The sump temperature and hot spots at bearings | Mineral oil sump under 180-200°F; a bearing position hotter than the case = a bearing; a hot spot at the mesh = gear trouble |
| **Belt drives** | The belt and sheave temperature | A belt over 140-160°F is slipping or over-tensioned; one sheave hotter = misalignment, slip on that sheave |
| **Pumps** | The seal chamber, bearing frame, the casing pattern | A seal chamber hot = a dry or flush-starved seal; a casing hot near the cutwater at low flow = recirculation |
| **Electrical (NFPA 70B / NETA delta T over a similar component under the same load)** | Hot connections, a hot fuse clip, a hot breaker pole, a hot conductor | **1-10°C (2-18°F) over similar**: possible deficiency, investigate; **11-20°C**: probable deficiency, repair at the next opportunity; **21-40°C**: deficiency, repair soon; **> 40°C (72°F)**: major, repair immediately; the absolute rule: a connection more than **40°C over ambient** is failing; a **hot phase in one phase only** = a connection; all three hot = load or an undersized conductor. Done by a qualified person with the panel open under load, in the arc-flash PPE, from outside the restricted boundary: usually the electrician with the millwright's camera, or through IR windows |
| **Steam traps** | The inlet and outlet temperatures | A working trap: inlet at steam temperature, outlet 10-30°F cooler and cycling; a **failed open** trap: outlet as hot as the inlet with no cycling (steam blowing through); a **failed closed** trap: cold outlet and a cold trap (condensate backing up) |
| **Insulation, refractory, ovens, kiln shells** | Hot spots and patterns | A hot spot on a kiln shell = refractory loss inside; insulation gaps on steam lines |
| **Hydraulic systems** | A hot relief valve, a hot cylinder (bypass), a hot pump case, the cooler ΔT | The hot component is the one passing oil across a pressure drop (see [hydraulic basics](/article/hydraulic-system-basics-and-symbols)) |
| **Conveyor idlers and pulleys** | A hot roll | A roll 20°F+ over its neighbours has a seized bearing (fire risk on combustible material) |
| **Tanks and vessels** | Level (the liquid line shows), sludge, insulation | |

### Cameras and guns

- **IR gun** (spot thermometer, 12:1 or 30:1 distance-to-spot, laser pointer): for bearing housings, motors, pipes; set the emissivity; get close; a contact probe (thermocouple) for shiny things.
- **IR camera** (a 160×120 to 640×480 detector, 8-14 µm long-wave): the image shows the pattern (the hot spot on a motor frame, the connection in a panel, the trap's outlet); save the image with the visible photo and the reading; a report with the delta T and the priority.
- Safety: IR does not see through covers; electrical scanning is the electrician's; a camera in a classified area must be rated.

## Ultrasound

An ultrasonic detector "hears" high-frequency sound (20-100 kHz) that people cannot: **turbulence** (gas escaping through a leak, a vacuum drawing air), **friction and impacts** (a bearing's rolling contact, a rubbing seal), and **electrical discharge** (corona, tracking, arcing); it translates them down to audible sound in the headphones and reads a level in **dB**. Two modes: **airborne** (a scanning module or a parabolic dish for distance: leaks, electrical, steam) and **contact** (a probe touched on the bearing housing, the trap, the valve: bearings, valves, traps).

| Use | Method | Reading it |
|---|---|---|
| **Compressed air / gas leaks** | Airborne, scan the fittings, couplers, hoses, drains, valve packings; the rushing sound peaks at the leak; a tag and the dB level (the software estimates the cfm and cost) | The single fastest payback in most plants (see [pneumatics](/article/pneumatic-systems-frl-and-cylinders)); vacuum leaks the same way |
| **Bearings** | Contact probe on the housing at the same spot each time; read the dB and listen: a good bearing is a smooth rushing sound; a **dry** bearing is louder and rough; a **damaged** bearing has clicks, crackles and rumbles; the dB trend against the baseline | **+8 dB** over baseline = lubrication needed; **+12 dB** = early failure (the bearing needs a look); **+16 dB** or more = failure; **+35 dB** = catastrophic. Combine with the vibration envelope |
| **Greasing by ultrasound** | Probe on the housing, grease gun on the fitting, listen: the level **drops** as grease reaches the bearing; add slowly until the drop stops and the level begins to **rise** again (over-greasing); stop | The way to grease the right amount without a calculation; a bearing whose level does not drop with grease is damaged, not dry |
| **Steam traps** | Contact probe downstream of the trap: a working trap cycles (a rush as it discharges, then quiet); a **failed open** trap is a continuous rush; a **failed closed** trap is silent and cold; combine with the IR reading | The two technologies together give a confident call |
| **Valves (leak-through)** | Contact on the valve body downstream: a closed valve that passes flow shows turbulence | Find the leaking isolation valve |
| **Electrical** (airborne, from outside the panel or through the vents, at a safe distance) | **Corona** (a steady buzz/frying at over 1,000 V), **tracking** (an erratic crackle: insulation breaking down), **arcing** (violent pops) | Any tracking or arcing = a fault to be fixed; corona in MV gear = insulation degrading; the ultrasound finds what IR cannot (no heat until it fails) |
| Pump cavitation, hydraulic valves | Contact on the casing/valve | A cavitating pump crackles; a bypassing hydraulic valve hisses |
| Gearboxes | Contact | Gear mesh sounds; a damaged tooth clicks once a revolution |

Contact readings need the same spot, the same probe pressure and the same instrument settings (frequency, sensitivity) to trend; baselines at commissioning; record the dB and a sound file for the analyst.

## Which technology finds what

| Failure | Vibration | Ultrasound | Thermography | Oil analysis |
|---|---|---|---|---|
| Rolling bearing early stage (months) | Envelope/HFD: **yes** | **Yes** (dB, sound) | No | Sometimes (wear metals in oil-lubricated) |
| Rolling bearing late stage | Overall: yes | Yes | **Yes** (heat) | Yes |
| Lubrication starvation / over-greasing | HF energy | **Best** | Yes (heat) | |
| Misalignment | **Best** (2×, axial) | No | Coupling heat | |
| Unbalance | **Best** (1×) | No | No | |
| Looseness / soft foot | **Best** | No | Sometimes (a distorted motor frame shows a heat pattern) | |
| Gear wear | GMF sidebands | Contact sounds | Hot spots | **Best early** (iron, PQ) |
| Motor winding/stator | 120 Hz | | **Yes** (frame pattern) | |
| Rotor bars | Pole-pass sidebands | | | (current analysis) |
| Electrical connections | No | Arcing/tracking | **Best** (delta T) | |
| MV corona/tracking | No | **Best** | No until late | |
| Belt problems | Belt frequency | Slip squeal | **Yes** (hot belt/sheave) | |
| Air/gas/vacuum leaks | No | **Best** | Sometimes (cooling) | |
| Steam traps | No | **Yes** | **Yes** | |
| Hydraulic internal leaks | | Contact | **Best** | |
| Coolant/water in oil, oxidation, wrong oil | No | No | No | **Only** |
| Cavitation | Broadband | Contact | Sometimes | |
| Refractory/insulation | No | No | **Only** | |

A route uses the cheap, fast technology for screening (IR gun and ultrasound on every bearing on the walk; a vibration pen overall) and the analyser or the lab for diagnosis; a finding in one is confirmed with another before the work order.

## Building the route

Points chosen from the machine list by criticality (the machines whose failure stops production or is dangerous get all the technologies monthly; the rest quarterly with the screening tools); each point with its baseline, alarm and the method (spot, emissivity, probe); the same order and settings each time; the readings into the software or the CMMS; a review the same week; the report with the priority (immediate / next shutdown / monitor) and the evidence (the image, the spectrum, the dB, the oil report); the feedback when the machine is opened (was the call right?).

## Common mistakes

- Reading a shiny stainless housing at 0.95 emissivity: it reads 60°F low and the bearing is "fine".
- A "hot spot" on a bus bar that was the lamp's reflection.
- Scanning the panel at 10% load: nothing shows.
- Greasing to a calculated amount into a bearing that ultrasound would have shown was already full.
- A trap called "failed" from the IR alone (it was cycling between readings).
- Ultrasound bearing readings taken with different probe pressure each month: the trend is the technician's hand.

## Related

- [Vibration basics and ISO severity](/article/vibration-basics-and-iso-severity)
- [Vibration signatures](/article/vibration-signatures)
- [Oil analysis and sampling](/article/oil-analysis-and-sampling)
- [Regreasing intervals and quantities](/article/regreasing-intervals-and-quantities)
- [Electrical safety for mechanics (thermography of panels)](/article/electrical-safety-for-mechanics)
- [PM checklists](/article/pm-checklists)
