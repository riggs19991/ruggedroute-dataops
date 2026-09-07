---
title: "Machine Trouble Decision Tree: A Machine Is Vibrating, Noisy or Hot, What to Check First, in Order, and Which Article to Open"
slug: machine-vibration-noise-heat-decision-tree
category: troubleshooting
kind: reference
tags: [troubleshooting, decision tree, machine vibrating, machine noisy, bearing hot, motor hot, gearbox hot, pump noisy, what to check, diagnosis, symptom, cause, quick check, first steps, noise diagnosis, heat diagnosis, vibration diagnosis]
source: "Synthesis of the guides referenced in the linked articles: ISO 20816, vibration analysis charts (Technical Associates), SKF and Timken bearing damage guides, Gates belt guides, coupling and pump troubleshooting references, NEMA MG 1 motor guidance."
summary: "A symptom-first checklist for the call every millwright gets: something is shaking, screaming or too hot. Work down the tree with a thermometer, a vibration pen, a stethoscope and your eyes to sort the problem into bearing, alignment, unbalance, looseness, belt, gear, lubrication, electrical, flow or structural, then open the article that fixes it."
---

> Before anything else: **is anyone in danger, and is the machine about to fail?** A bearing over 220°F, a vibration that has doubled since this morning, a knocking that gets louder, smoke, or a belt on fire means **stop it now**. Otherwise take 10 minutes of readings while it runs; the readings are the diagnosis.

## The 10-minute running check

1. **Where is it worst?** Walk around with a hand on the housings (or the vibration pen): which bearing, which machine (driver or driven), which direction (horizontal, vertical, axial)?
2. **Temperatures** by IR: every bearing housing, motor frame, gearbox, coupling guard, belt sheaves; compare ends and compare to the baseline.
3. **Listen** with a stethoscope or screwdriver at each bearing and at the gear mesh: smooth hiss (fine), rough growl (bearing), whine rising with speed (gear or misalignment), knock once per revolution (looseness, damaged tooth, bent shaft), rattle at random (loose part), squeal (belt), gravel (cavitation).
4. **Amps** on the panel vs nameplate.
5. **Look**: leaks, belt dust, rubber crumbs under the coupling, oil level, breather, guard contact, loose bolts, cracked base, pipe hangers, build-up on the fan.
6. **Speed**: is it running at its normal speed (VFD setting, belt slip via a strobe)?
7. **What changed?** New product, new belt, recent alignment, motor swapped, VFD parameters, a valve throttled, ambient heat.

## Branch A: it is VIBRATING

| Ask | If yes | Open |
|---|---|---|
| Is the vibration **highest horizontally at 1× rpm**, similar on both bearings of the same machine, and steady? | **Unbalance** (build-up on a fan or impeller, lost balance weight, eroded blades, bent shaft if axial is also high) | [Vibration signatures](/article/vibration-signatures); clean the fan; balance |
| Is it **highest axially**, or high at **2× rpm**, worst at the coupling ends of both machines, with a 180° phase difference across the coupling? | **Misalignment** (or a coupling problem, soft foot, pipe strain, thermal growth) | [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals), [soft foot](/article/soft-foot-correction), [thermal growth](/article/thermal-growth-alignment), [coupling failure](/article/coupling-failure) |
| Does it get worse when you push on the base, or show at **0.5×, 1×, 2×, 3×** with a knock, or change with load direction? | **Looseness** (base bolts, cracked grout, bearing loose in housing or on the shaft, hub loose on shaft, worn keyway) | Tighten and check every bolt; [grouting and baseplates](/article/grouting-baseplates); [keys and keyways](/article/keys-and-keyways); [bearing clearance and fits](/article/bearing-clearance-and-fits-tables) |
| Is there a **rough, random, high-frequency** vibration or a growl at one bearing, its temperature rising, ultrasound loud? | **Bearing damage** (or lubrication starvation: check the last grease date first) | [Bearing failure analysis](/article/bearing-failure-analysis); [regreasing](/article/regreasing-intervals-and-quantities); if it is starved, grease it now and watch; if damaged, plan the change |
| Is it a **belt drive** with a flap or beat, belt dust, and the vibration changes with belt tension? | **Belt/sheave**: mismatched set, sheave runout, misaligned sheaves, worn grooves | [V-belt installation](/article/v-belt-drive-installation-and-tensioning); [belt failure](/article/belt-failure) |
| **Gearbox** with a whine at gear-mesh frequency (teeth × rpm), sidebands, or a knock once per rev of one shaft? | **Gear wear, damaged tooth, backlash, worn bearing letting the mesh move** | [Gear inspection](/article/gear-inspection-and-tooth-failure); [gearbox lubrication](/article/gearbox-lubrication-and-inspection) |
| **Motor** vibration that **stops instantly when power is cut** (not coasting down with it)? | **Electrical** (rotor bar, eccentric air gap, unbalanced supply, VFD) | [Megger and motor testing](/article/megger-and-basic-motor-testing); [VFD basics](/article/vfd-basics-for-millwrights); electrician |
| **Pump** with a gravel/rumble noise, vibration and falling pressure? | **Cavitation / suction problem / recirculation** (throttled suction, low level, blocked strainer, running far off the curve) | [Pump troubleshooting](/article/pump-troubleshooting) |
| Did it start after a **speed change** (VFD) and does it go away at other speeds? | **Resonance** (structure or piping natural frequency) | Skip the speed on the VFD; stiffen or brace; get a bump test |
| Vibration in the **piping or structure** more than the machine? | Pipe strain, missing hangers, flow pulsation, unsupported spans | [Pipe strain and flange alignment](/article/pipe-strain-and-flange-alignment) |

Severity reference: [ISO severity chart](/article/vibration-basics-and-iso-severity). A jump of 2× the baseline is an alarm whatever the number.

## Branch B: it is NOISY

| Noise | Likely | Check / open |
|---|---|---|
| **Squeal on start or under load** (belt drive) | Belt slipping (loose, glazed, worn grooves, overloaded) | [V-belt tensioning](/article/v-belt-drive-installation-and-tensioning), [belt failure](/article/belt-failure) |
| **Continuous squeal or chirp at a bearing** | Dry bearing (grease gone, or the seal let it out), or a lip seal running dry | Grease it (correct type and amount); [seal failure](/article/seal-failure) |
| **Growl / rumble at a bearing** that gets worse with speed | Rolling element damage | [Bearing failure analysis](/article/bearing-failure-analysis) |
| **Whine that rises with speed**, from a gearbox | Gear wear, misalignment, low oil, wrong oil | [Gear inspection](/article/gear-inspection-and-tooth-failure) |
| **Knock once per revolution** | Loose coupling/hub, damaged gear tooth, bent shaft, loose impeller, key sheared | [Coupling failure](/article/coupling-failure), [gear inspection](/article/gear-inspection-and-tooth-failure) |
| **Rattle, random** | Loose guard, loose bolt, broken spring in a coupling grid, foreign object | Look; [coupling failure](/article/coupling-failure) |
| **Gravel / marbles in a pump** | Cavitation, air entrainment | [Pump troubleshooting](/article/pump-troubleshooting) |
| **Hammering in piping** | Water hammer, check valve slam, air pockets, trapped condensate in steam lines | Valve closing speed, air vents, traps |
| **Hiss** | Air or gas leak, steam trap blowing | Soap or ultrasound; [pneumatic systems](/article/pneumatic-systems-frl-and-cylinders) |
| **Motor hum louder than normal, with heat** | Single-phasing, unbalanced voltage, VFD carrier noise, loose laminations | Electrician; [electrical safety](/article/electrical-safety-for-mechanics) |
| **Screech from a chain drive** | Dry chain, worn sprockets, misaligned | [Roller chain drives](/article/roller-chain-drives) |
| **Clunk at start and stop** | Backlash in coupling or gears, loose key, soft foot | [Coupling types and gap](/article/coupling-types-gap-and-installation), [soft foot](/article/soft-foot-correction) |
| Conveyor: **squeal that moves along the belt** | Stuck idler | [Idlers, pulleys and lagging](/article/idlers-pulleys-and-lagging) |

## Branch C: it is HOT

| Where | Likely | Check / open |
|---|---|---|
| **One bearing housing** hot, the other end fine | Over-greased (very common right after a PM: temperature rises for a few hours then falls; if it keeps rising it is packed solid), under-greased, wrong grease, bearing damage, misalignment loading it, too much interference or preload, seal rubbing, thrust from the coupling gap being wrong | [Regreasing](/article/regreasing-intervals-and-quantities), [grease compatibility](/article/grease-types-and-compatibility), [bearing clearance and fits](/article/bearing-clearance-and-fits-tables), [tapered roller setting](/article/tapered-roller-bearing-setting) |
| **Motor frame** hot all over | Overload (amps), high ambient, blocked cooling fins or fan, low voltage, unbalanced voltage, VFD at low speed with full torque, too many starts, wrong connection (wye instead of delta) | [Motor nameplate](/article/reading-a-motor-nameplate), [motor lead connections](/article/motor-lead-connections), [VFD basics](/article/vfd-basics-for-millwrights) |
| **Gearbox** hot (over 200°F mineral, 220°F synthetic) | Low or high oil level, wrong viscosity, wrong oil, overload, blocked breather (pressurised), misalignment, worn bearings, cooler/fan fault | [Gearbox lubrication](/article/gearbox-lubrication-and-inspection), [oil viscosity selection](/article/oil-viscosity-and-selection) |
| **Coupling** hot (guard vents hot, smell of rubber) | Misalignment working the element; dry gear/grid coupling | [Coupling failure](/article/coupling-failure); align |
| **Belt sheaves** hot, belt smell | Slipping | [V-belt tensioning](/article/v-belt-drive-installation-and-tensioning) |
| **Pump** casing hot, low flow | Running at or near shut-off (dead-headed), recirculation, closed discharge valve, blocked line | [Pump troubleshooting](/article/pump-troubleshooting): open a bypass or minimum-flow line **now**, pumps dead-headed boil in minutes |
| **Hydraulic** oil over 140°F | Relief valve dumping (set too low or system over-pressuring), pump wear, cooler fouled or no water/air flow, low oil, wrong viscosity, cylinder bypassing | [Filters, fluid and contamination](/article/filters-fluid-and-contamination), [hydraulic basics](/article/hydraulic-system-basics-and-symbols) |
| **Compressor** discharge over 225°F | Low oil, cooler blocked, thermostatic valve, wrong oil, high ambient, low airflow | [Air compressor PM](/article/air-compressors-pm) |
| **Electrical connection or terminal** hot on a thermal camera | Loose connection, corrosion | Electrician; [thermography](/article/thermography-ultrasound-and-oil) |
| **Chain** hot | Dry, overloaded, misaligned | [Roller chain drives](/article/roller-chain-drives) |
| Packing box hot | Gland too tight, no leakage/flush | [Pump packing](/article/pump-packing-and-stuffing-box) |

Bearing temperature limits (typical): alarm at baseline + 20°F; **180°F (82°C)** housing is the general "act" point for grease-lubed ball and roller bearings (grease breaks down fast above it); 200°F on oil-lubed pump bearings; motor bearings up to 200°F can be normal on Class F motors: know the baseline.

## Branch D: it LEAKS, SMELLS or is SLOW

- **Oil leak**: level, breather, seal (see [seal failure](/article/seal-failure)), overfilled, pressurised housing, cracked casing, loose plug; grease leak at a motor: over-greased past the inner cap into the winding.
- **Smell**: hot varnish = motor winding (stop and megger); hot rubber = belt or coupling; burnt oil = gearbox or hydraulic overheating; sulphur/rotten egg = EP oil overheated or bacteria in coolant.
- **Slow / low output**: belt slip, VFD limit, pump wear ring clearance ([impeller clearance](/article/impeller-clearance-and-wear-rings)), hydraulic pump wear or relief bypass, filter blocked, air leaks in pneumatics, closed or throttled valve, wrong rotation after a motor change (**check rotation first** on any pump or fan that is "weak" after electrical work).

## Write it down

Whatever you find, the readings, the cause and the fix go on the work order (see [work orders and history](/article/work-order-and-history-records)), and the machine's route sheet gets a new baseline after the repair.

## Related

- [Vibration basics and ISO severity](/article/vibration-basics-and-iso-severity)
- [Vibration signatures](/article/vibration-signatures)
- [Bearing failure analysis](/article/bearing-failure-analysis)
- [Pump troubleshooting](/article/pump-troubleshooting)
- [Inspection routes](/article/inspection-routes)
- [PM checklists](/article/pm-checklists)
