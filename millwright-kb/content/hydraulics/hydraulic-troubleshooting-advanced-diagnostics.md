---
title: "Advanced Hydraulic Troubleshooting and Diagnostics: the Method (Define, Split the Circuit, Test with Instruments), the Instruments (Gauges and Test Points, Flow Meters and Testers, Infrared Heat Mapping, Transducers and Loggers, Ultrasonic, Meters for Solenoids), the Standard Tests with Pass/Fail Numbers (Pump Flow, Relief, Cylinder Bypass, Spool Leakage, Motor Case Drain, Holding-Valve Decay, Cooler ΔT, Suction Vacuum), Symptom Trees, Heat Balance and Cooler Sizing, Electrical Checks and Start-Up After Repair"
slug: hydraulic-troubleshooting-advanced-diagnostics
category: hydraulics
kind: reference
tags: [hydraulic troubleshooting, hydraulic diagnostics, hydraulic fault finding, hydraulic test point, Minimess, Stauff test point, hydraulic flow meter, hydraulic tester, flow pressure temperature tester, infrared thermometer hydraulics, heat mapping, thermal imaging hydraulic, pressure transducer, data logger hydraulic, pressure trace, ultrasonic leak detection internal, hydraulic multimeter, solenoid coil test, pump flow test, relief valve test, cylinder bypass test, piston seal leakage test, spool leakage test, motor case drain test, pressure decay test, counterbalance leak test, cooler delta T, suction vacuum gauge, hydraulic symptom chart, slow hydraulic, weak hydraulic, cylinder drift, erratic hydraulic, hydraulic overheating, noisy pump, intermittent hydraulic fault, one function slow, heat balance, cooler sizing, hydraulic heat load, BTU per hp, reservoir cooling, start-up after repair, hydraulic commissioning, hydraulic troubleshooting checklist]
source: "Eaton Vickers Industrial Hydraulics Manual (troubleshooting logic, testing procedures); Parker Hannifin Hydraulic Troubleshooting Guide and test point practice; Fluid Power Society (IFPS) mechanic and technician certification study manuals (system testing); Webtec and Hedland flow tester application guides; Bosch Rexroth commissioning and troubleshooting notes; Fluke infrared thermography application notes; Brendan Casey (Hydraulics Pro Club) diagnostic method publications; NFPA/T2 fluid power practice."
summary: "The method a hydraulic troubleshooter uses instead of parts-swapping: define the symptom at the step it happens, read the schematic and split the circuit at a test point, and test with instruments that give numbers. It covers the instruments and where to connect them, each standard test step by step with its pass and fail values, a symptom-by-symptom tree from no pressure to intermittent faults, the heat balance that tells you whether a hot system has a cooler problem or a leakage problem, the electrical checks that separate the PLC from the valve, and the start-up sequence after a repair that keeps the fix alive."
---

## The method

1. **Define the symptom precisely**: which actuator, which direction, at which step of the sequence, under what load, hot or cold, always or sometimes, since when, what changed (a repair, a new oil, a new operator, the weather). "The press is slow" becomes "the ram's pressing stroke takes 9 seconds instead of 4 after the machine has run an hour; rapid advance is normal; the tank is at 165°F".
2. **Read the schematic and the sequence table** before touching the machine: what should be energised and what pressure should be where at that step. If there is no schematic, sketch one from the machine: the diagnosis is worth it.
3. **Look, listen, feel** (the ten-minute walk-around in the [machine decision tree](/article/machine-vibration-noise-heat-decision-tree)): level, temperature, filter indicators, noise, leaks, gauge readings, solenoid LEDs, the smell of hot oil, the colour of the oil.
4. **Split the circuit**: find the point where you can prove one half is good. The pump is good if it delivers full flow at pressure (Test 1); the pressure controls are good if the pressure at the valve inlet is right (Test 2); the actuator is good if it does not bypass (Test 3); the valve is good if it shifts and does not leak (Tests 4 and 5). Each test halves the problem.
5. **Measure with instruments**: a gauge at a test point, a flow meter, a thermometer, a stopwatch on a cylinder stroke, a meter on a coil. Numbers, compared with the design values on the schematic and the maker's data.
6. **Change one thing**, retest, and write down what you found and what you changed. Parts swapped without a test are a cost, not a diagnosis.

![Decision tree: from the symptom to the test to the cause](/img/hydraulics/troubleshooting-decision-tree.svg)

*Decision tree: from the symptom to the test to the cause*

## Instruments

![A high-pressure test gauge: pick a range 1.5 to 2 times the working pressure and read it at the test point](/photos/hydraulics/pressure-gauges.jpg)

*A high-pressure test gauge: pick a range 1.5 to 2 times the working pressure and read it at the test point. Photo: CEphoto, Uwe Aranas, CC BY-SA 3.0, via commons*

| Instrument | What it tells you | Where |
|---|---|---|
| **Pressure gauges** (glycerine-filled, a range 1.5-2× the working pressure; a **test gauge** of 0.5% class for setting valves) and **test points** (Minimess/Stauff M16×2 quick-test couplings with a captive ball: connect under pressure without leaks) | Pressure at that point at that moment | Pump outlet, before and after every pressure valve, both actuator ports, the LS line, the pilot supply, the case drain, the return line, the accumulator; fit test points permanently at the design stage: a machine with test points at every branch is diagnosed in an hour, one without in a day |
| **Vacuum/compound gauge** (30 in Hg to 30 psi) | Inlet condition | Pump suction: the strainer, the line, the oil |
| **Flow meter** (turbine or variable-area, sized for the flow) and the **hydraulic tester** (flow meter, load valve, pressure gauge and thermometer in one body, often with a pressure relief for protection) | Flow **at pressure**: the health of a pump, a motor, a valve, a cylinder | In the pump outlet, in a work line, in the case drain, in a motor return |
| **Infrared thermometer / thermal camera** | Which component is dropping pressure across itself (turning power into heat) | Every valve, cylinder, motor, line, the cooler in and out; a 20°F difference from its neighbours is a lead |
| **Stopwatch and a tape** | Cylinder speed = flow; drift rate = leakage | Any cylinder |
| **Pressure transducers and a data logger / hydraulic multimeter** | Pressure against time in milliseconds: spikes, decay, the sequence timing, pump ripple, two pressures compared (LS margin, pilot vs main) | Fast circuits, intermittent faults, servo and proportional systems, load-sense systems |
| **Ultrasonic detector** (contact probe) | Turbulence from internal leakage: a bypassing relief, a leaking check, a cylinder piston passing oil, a cavitating pump | On the valve body or cylinder while the load is held |
| **Multimeter, clamp meter, a solenoid tester, LED plugs** | Voltage at the coil, current, coil resistance, the PLC output | Every solenoid |
| **Particle counter, water test, viscosity comparator** | The oil | Sample point |
| **Oil sample bottles, a clean container and a measuring jug** | Case drain volume, leakage volumes | |
| **A gauge with a snubber**, a hose for the accumulator charging kit, blanking caps and plugs for every fitting family, jumper hoses rated for the pressure | | |

**Reading a gauge properly**: at operating temperature; watch it during the whole cycle (a needle that dips as the actuator starts to move is a pump or a supply problem; one that climbs slowly is a flow problem); note the pressure at **which the function moves** (the load-induced pressure) as well as the maximum; compare the pump outlet with the actuator port at the same moment (the difference is the pressure drop through the valves and lines: more than 150-300 psi is a restriction, a bypassing valve or an undersized line).

## The standard tests

![Cylinder bypass test: prove the piston seals before condemning the pump](/img/hydraulics/cylinder-bypass-test.svg)

*Cylinder bypass test: prove the piston seals before condemning the pump*

| # | Test | How | Pass | Fail means |
|---|---|---|---|---|
| **1** | **Pump flow at pressure** | Flow meter or tester in the pump outlet; record flow at 0, 25, 50, 75, 100% of working pressure at operating temperature and rated rpm | Within about 10-15% of theoretical at working pressure (ηv > 0.85); a nearly flat line | A steep fall = worn pump; low at zero pressure = suction problem or rpm; see [pumps](/article/hydraulic-pumps-types-controls-and-testing) |
| **1b** | **Case drain flow** | Case drain into a measure or a flow meter at working pressure | Under about 10% of rated flow (the maker's number) | A worn piston or vane pump/motor |
| **2** | **Relief valve** | Gauge at the pump outlet; dead-head the flow (block the actuator or close the tester's load valve) with the compensator screwed in above the relief; read where the pressure stops climbing; then open the load valve slowly and read the pressure at which flow begins to pass (the cracking pressure) | Full-flow pressure at the setting on the schematic; cracking within 5-10% below it for a pilot-operated valve (20-30% for a direct-acting) | Setting drifted, seat worn (a large cracking-to-full-flow gap: heat and slow), stuck, vent open |
| **3** | **Cylinder piston bypass** | Lockout; extend the cylinder fully (rod out, against its stop, so the piston seals see pressure but the cylinder cannot move); disconnect the **rod-end** line at the cylinder and cap the line (the cylinder port open into a container); pressurise the **cap end** to working pressure with the DCV; measure what comes out of the rod-end port over a minute; repeat retracted with the ports swapped | A few drops to a thin trickle (new: under 1-3 in³/min; tolerable in service: a few in³/min depending on bore) | A steady stream = piston seals or a scored bore: [cylinder repair](/article/cylinder-repair-and-seal-kits). The test with the cylinder mid-stroke against a block is valid only with the DCV centred and both lines gauged |
| **3b** | **Cylinder drift** | Load held, DCV centred, pump off, holding valves in circuit; measure the rod movement in 10 minutes; then bypass or isolate the holding valve to separate the cylinder from the valve | Per the machine spec; typically under 1/16-1/8 in (2-3 mm) per 10 min with a poppet-type holding valve | Drift with the holding valve isolated = piston seals (or the rod seal if oil appears outside); drift only with it in circuit = the holding valve or its pilot |
| **4** | **DCV spool leakage** | A and B lines disconnected and capped; P at working pressure, spool centred; measure the flow from T | Per the maker; a D03 about under 10 in³/min (150 mL/min) total at 3,000 psi; a D05 20-30 | Worn spool or body, or a scored subplate face |
| **4b** | **Valve shift** | LED and voltage at the coil while commanding; then the manual override | Shifts on the solenoid | Shifts on the override only = electrical; shifts on neither = hydraulic (pilot pressure, stuck spool): [directional valves](/article/directional-control-valves-spools-and-solenoids) |
| **5** | **Motor case drain and leakage** | Case drain flow at working pressure and speed, or with the shaft stalled against a brake | Under 5-10% of the motor's rated flow (the maker's number) | Worn motor: low torque, slow, hot; see [motors](/article/hydraulic-motors-and-hydrostatic-drives) |
| **6** | **Holding valve (POC, counterbalance, logic element) pressure decay** | Gauge on the held line, pump off; read the pressure every minute for 10 minutes | A poppet-type valve holds within a few percent | A steady decay = a leaking seat or pilot; check the cylinder separately (Test 3) |
| **7** | **Accumulator precharge** | Pump off, system bled, watch the gauge fall as the accumulator empties: the sudden drop to zero happens at the precharge pressure; or a charging kit on the gas valve | 80-90% of the minimum working pressure (energy storage) or per the drawing | Lost precharge or a failed bladder: [accumulators](/article/accumulator-precharge-and-safety) |
| **8** | **Cooler ΔT** | IR thermometer on the oil in and out of the cooler and on the water or air in and out | Oil out 10-25°F (5-15°C) below oil in at full flow through it; the water or air side warming correspondingly | Little ΔT with the cooler hot = a bypass open or oil not flowing through it; little ΔT with the cooler cold = the oil side blocked or the thermostat closed; both sides hot = fouled or too small |
| **9** | **Suction vacuum** | Compound gauge on the pump inlet, at temperature and full flow | Under 5 in Hg (piston), 5-7 (vane), 7-10 (gear) | A blocked strainer, a collapsed hose, thick oil, a plugged breather |
| **10** | **Pressure drop across a filter, a valve, a line** | Gauges each side at full flow | Filter: under the bypass setting (25-50 psi) at temperature; a DCV: 50-150 psi per path at rated flow; a line: a few psi per foot | A blocked element, an undersized valve or hose, a collapsed hose liner, a kinked line |
| **11** | **LS margin** | Gauges on the pump outlet and the LS line while a function moves | Margin per the pump setting (200-350 psi) | See [load-sensing systems](/article/load-sensing-proportional-and-servo-systems) |
| **12** | **Heat mapping** | IR on every component 20 minutes after a warm start | Everything within about 10-20°F of the tank, the cooler outlet cooler | The hottest component is passing oil across a pressure drop: a dumping relief, a bypassing cylinder, a leaking check, a compensator fighting a relief |

## Symptom trees

![Infrared thermometer with a contact probe: the hot component is the one passing oil across a pressure drop](/photos/hydraulics/hot-oil-thermal.jpg)

*Infrared thermometer with a contact probe: the hot component is the one passing oil across a pressure drop. Photo: KalWadin, CC BY-SA 4.0, via commons*

| Symptom | Order of checks |
|---|---|
| **No pressure, no motion, pump running** | Rotation (a new pump!); coupling and key; suction valve open, level, strainer; relief set to zero, stuck open or vent open; a DCV not shifting (Test 4b); an open-centre or tandem spool with the pump unloading normally (read the schematic: the "no pressure" may be normal at rest); a burst line; compensator screwed out |
| **Low maximum pressure** | Relief (Test 2); compensator; a second relief or a reducing valve in the branch; internal leakage somewhere big (heat map); a worn pump (Test 1: a worn pump makes pressure only against a small leak) |
| **Slow, all functions, full pressure available** | Pump flow (Test 1); rpm (a VFD, a belt, an engine at low idle); oil too thick (cold) or too thin (hot, sheared); a flow control in the main line; a partly open relief or unloading valve (heat); a bypassing actuator in a series circuit |
| **Slow, one function** | That function's flow control, its counterbalance (set too high), its POC pilot, a blocked orifice in its sandwich, a port relief cracking, that cylinder bypassing (Test 3) or that motor worn (Test 5), a kinked hose, a valve section's spool not fully shifting (low pilot pressure, a stroke limiter) |
| **Slow when hot, fine when cold** | Internal leakage that grows with thin oil: a worn pump (Test 1 hot), a bypassing cylinder, a worn valve; oil grade too light or sheared; a cooler that is not cooling |
| **Slow when cold, fine when hot** | Viscosity too high for the pump (an HV grade or heaters), cavitation on the inlet when cold, a cold-sticking spool, a cold PLC ramp |
| **Weak (stalls under load) but full speed at no load** | A pressure problem: a relief or port relief cracking early, a reducing valve, a compensator low, a load check or POC restricting, a cylinder bypassing under load only (Test 3), a motor leaking under load (Test 5); the gauge at the actuator port while it stalls tells you where the pressure is lost |
| **Cylinder drifts (creeps) under load** | Test 3b: holding valve or cylinder; a DCV spool centre that is not meant to hold (open or float); a POC held open by pilot pressure from a closed-centre spool; a leaking port relief or anti-cav check; thermal contraction of the oil (a hot cylinder cooling drifts a little: normal) |
| **Erratic, jerky, spongy** | **Air**: foam in the tank, a suction leak, a low level, a cylinder not bled after repair, a pump seal drawing air; then a sticking spool, a hunting counterbalance or compensator, a flow control fighting a counterbalance, a stick-slip cylinder (rod bent, seals dry), a cavitating pump, a failing accumulator |
| **Shock, hammer, bang** | A fast valve with a closed crossover, no cushion or the cushion screw out, a counterbalance too fast (10:1 on a springy load), a relief too slow, an accumulator with no precharge, a check valve slamming, a long line with no accumulator, a pilot choke missing |
| **Overheating** | The heat balance below; the heat map: a relief dumping (compensator above relief, relief low, stuck), a compensator fighting an LS signal, a bypassing cylinder or valve, a POC held open, a reducing-relieving valve relieving, a closed-centre valve on a fixed pump, an unloading valve not unloading, a cooler fouled or bypassed, water off, a fan reversed, low oil, a tank too small, the wrong viscosity, a hydrostatic flushing valve stuck |
| **Noisy pump** | Cavitation vs aeration (the [pump article](/article/hydraulic-pumps-types-controls-and-testing)); a worn pump; a coupling or alignment; a relief chattering near the compensator; a resonating line (a clamp) |
| **Foaming, milky oil** | Air or water: [filters and fluid](/article/filters-fluid-and-contamination) |
| **Will not hold pressure with the pump off** (an accumulator circuit, a clamp) | A leaking check or POC (Test 6), a leaking relief (the tank line warm), a bypassing cylinder, a lost precharge, an internal leak in a valve stack |
| **Intermittent** | Electrical first (a loose plug, a chafed wire, a marginal voltage, a PLC output going soft under load, a proximity switch): monitor the coil voltage with the meter's min/max or a logger through the fault; then thermal (a spool that sticks only hot or only cold, a coil that opens when hot), then contamination (a particle that moves), then air, then a failing accumulator; a **data logger on the pressure and the coil voltage** catches what a gauge and eyes miss |
| **Works on the manual override, not on the solenoid** | Electrical: voltage at the coil, the coil, the plug, the output |
| **Works after a filter change, then slows again in a week** | A component shedding metal (find it: a pump or a cylinder) or a fluid problem (varnish, water); check the old element |
| **Machine fine, but the operator says it is slow** | Measure the cycle against the design time before chasing anything |

## Heat balance

![Heat balance: where the horsepower goes and what the cooler must remove](/img/hydraulics/heat-balance.svg)

*Heat balance: where the horsepower goes and what the cooler must remove*

Every horsepower the pump takes that does not come out as work becomes heat: **1 hp = 2,545 BTU/h = 0.746 kW**. A typical industrial system turns **20-30% of its input power into heat** in normal operation (pump and motor inefficiency, valve pressure drops, relief and compensator losses); a badly set or leaking system turns most of it into heat.

```
   Heat load (BTU/h) = (input hp − useful hp) × 2,545
   Pressure drop heat: hp lost = gpm × psi dropped ÷ 1714           (10 gpm over a relief at 2,000 psi = 11.7 hp = 30,000 BTU/h)
   Reservoir dissipation (bare steel tank, still air, 40°F above ambient): about 0.001 hp per ft² per °F,
        i.e. a 100 gal tank (about 30 ft² of wetted wall) sheds roughly 1-1.5 hp: almost nothing on a 50 hp system
   Oil temperature rise across a leak: ΔT (°F) = psi dropped ÷ 900 (approx.)  (3,000 psi across a relief warms the oil about 3.3°F per pass; through a small orifice the local temperature is far higher)
   Cooler sizing: heat load ÷ (cooler's rating in BTU/h per °F of approach) with the approach = oil in − water (or air) in
```

Use it two ways. **Diagnosis**: if the tank runs at 170°F and the cooler is clean and flowing, calculate the heat you can account for; a system that should make 10 hp of heat and needs 30 hp of cooling has 20 hp of leakage or dumping somewhere: go to the heat map. **Sizing**: after a relief was "fixed" by adding a bigger cooler, the power bill and the pump wear continue; the cooler was never the fault. Target oil temperature: **110-130°F (45-55°C)** in the tank; every 18°F (10°C) above 140°F halves the oil life and softens the seals.

## Electrical-side checks

| Check | How | Reading |
|---|---|---|
| Is the output on? | The PLC output LED or the HMI's I/O screen at the step | On = go to the wiring; off = the logic, an interlock, a sensor |
| Voltage at the coil under load | Meter across the coil pins with the plug connected (back-probe) while commanded | Within 10% of rated (24 V DC: 21.6-26.4; 120 V AC: 108-132); a large drop from the panel to the coil = an undersized or corroded cable, a shared common |
| Current | Clamp meter (DC clamp for DC) | Near the rated (24 V, 30 W: about 1.2 A); AC: the inrush falling to holding within 100 ms; a steady high AC current = a spool not stroking |
| Coil resistance | Plug off, ohms | Per the nameplate (24 V DC 30 W: about 19 Ω); open = burned; low = shorted; compare with its twin |
| Connector | Pull, look, wiggle: the gasket, the screw, corrosion, a broken conductor at the strain relief | |
| Surge diode | A diode across the coil (in the plug) tested with the meter's diode range | Shorted diode = the coil never energises and the output fuse blows |
| Proportional / servo | Command signal (V or mA) and the feedback at the amplifier while commanding; the card's LEDs; the enable signal | See [proportional and servo systems](/article/load-sensing-proportional-and-servo-systems) |
| Sensors | Pressure switches against a gauge; a proximity switch's LED; a level or temperature switch bypassed for a test only with the permit | |
| Grounding and noise | A proportional valve that twitches: the shield, the ground loop, a VFD nearby | |

## Start-up after a repair

1. Clean the outside of everything opened; every open port capped until the moment of connection; new elements; the reservoir level right, the oil the correct type (label).
2. Bleed the pump case and the suction; relief backed off or compensator low; DCVs in a position that passes flow to tank if possible.
3. Jog: rotation, noise; run unloaded; bleed the cylinders at the ports (rod up, low pressure, full strokes, the bleed screws or a cracked fitting into a rag), bleed the pilot lines and the accumulators' oil side; fill and bleed motor cases.
4. Set the pressures in order (relief, compensator, LS margin, reducing, sequence, counterbalance, port reliefs), then the flow controls and cushions; check the pressure switches.
5. Run the sequence at low speed and pressure, then normal; watch the temperature settle (it should level under 130°F within an hour); heat map; listen.
6. Re-check the filter indicators and change the elements after the first day; sample the oil at a week; record the settings and the test numbers so the next troubleshooter has a baseline.

## Common mistakes

- Replacing the pump because the pressure was low, without a flow test.
- Turning the relief up to fix a weak machine (the relief was fine: something else was leaking).
- Reading the pressure at the pump and never at the actuator.
- Diagnosing a hot system by buying a cooler.
- Feeling for a leak with a hand.
- Testing a bypassing cylinder cold: it passes.
- Swapping parts with no record of what was tried.
- Believing the sight glass on a tank that has cylinders extended.
- Starting a rebuilt system at full pressure with the relief where it was.
- No test points on the machine, so every test starts with a wrench.

## Related

- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
- [Hydraulic pumps: types, controls and testing](/article/hydraulic-pumps-types-controls-and-testing)
- [Directional control valves, spools and solenoids](/article/directional-control-valves-spools-and-solenoids)
- [Pressure and flow control valves in depth](/article/pressure-and-flow-control-valves-in-depth)
- [Cartridge and logic valves](/article/cartridge-and-logic-valves)
- [Load-sensing, proportional and servo systems](/article/load-sensing-proportional-and-servo-systems)
- [Hydraulic motors and hydrostatic drives](/article/hydraulic-motors-and-hydrostatic-drives)
- [Cylinder repair and seal kits](/article/cylinder-repair-and-seal-kits)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
- [Hydraulic fluids: types and compatibility](/article/hydraulic-fluids-types-and-compatibility)
- [Machine vibration, noise and heat decision tree](/article/machine-vibration-noise-heat-decision-tree)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [Reading hydraulic and pneumatic circuit diagrams](/article/reading-hydraulic-and-pneumatic-circuit-diagrams)
- [Hydraulic symbols (ISO 1219), complete](/article/hydraulic-symbols-iso-1219-complete)
