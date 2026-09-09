---
title: "Bearing Failure Analysis (ISO 15243): Reading the Load Path, Fatigue Spalling, Wear, Corrosion and Fretting, False and True Brinelling, Electrical Fluting from VFDs, Overheating and Lubrication Failure, Cage Failure and Fracture, with the Cause and the Fix for Each"
slug: bearing-failure-analysis
category: troubleshooting
kind: reference
tags: [bearing failure, bearing failure analysis, ISO 15243, spalling, flaking, fatigue, brinelling, false brinelling, fluting, electrical erosion, VFD bearing damage, fretting corrosion, bearing overheating, blue bearing, lubrication failure, contamination, cage failure, load zone, load path, misalignment pattern, bearing damage, why did the bearing fail, root cause bearing]
source: "ISO 15243:2017 Rolling bearings, damage and failures, terms, characteristics and causes; SKF Bearing Damage and Failure Analysis (PUB BU/I3 14219); Timken Bearing Damage Analysis reference guide; NSK and Schaeffler damage catalogues; EASA/AEGIS guidance on shaft currents."
summary: "How to look at a failed bearing and say what killed it: first the load path (where the rings are worn tells you about the fit, alignment and load), then the ISO 15243 damage modes with what each looks like to the eye, its usual cause, and the corrective action, so the replacement does not fail the same way. Includes the fluting signature of VFD shaft currents, the difference between true and false brinelling, and the temperature colours."
---

## Before you look

- Collect the evidence as in [bearing removal](/article/bearing-removal-pullers-and-heating): not cleaned, orientation marked, the grease or oil sampled, the shaft and housing measured, the history (hours, load, speed, temperature trend, vibration trend, last greasing, what was done at the last rebuild).
- Only about one bearing in ten reaches its calculated L10 fatigue life; the rest die of **lubrication (about 40-50%), contamination (about 15-20%), mounting and handling (about 15-20%)** and misapplication. The analysis is about finding which.
- Look at the whole set: **both rings, the rolling elements, the cage, the seals, and the seats** (shaft and housing). The rings' running tracks are the first thing to read.

## Reading the load path (running track)

The rolling elements polish a **track** on each raceway where the load passes. Its position and width tell the story before you find any damage.

![Running track patterns on the races](/img/troubleshooting/bearing-load-paths.svg)

*Running track patterns on the races*

| Track pattern | Meaning |
|---|---|
| **Inner ring: track all round, centred and uniform; outer ring: track over ~1/3 of the circumference in the load direction, centred** | Normal for a rotating inner ring with a fixed-direction radial load: the correct picture |
| Outer ring track all round (rotating outer ring load) with the inner track short | Normal for a rotating housing / stationary shaft |
| Tracks **wider than normal on both rings, all round** | **Excessive preload**: too much interference, C-clearance too small, thermal, both rings tight |
| Track **offset to one side** on both rings (one side of the raceway) | **Axial load** (thrust): normal on an angular-contact or where thrust is intended; on a deep groove ball bearing, a large offset = excessive axial load or both bearings fixed with no float |
| Track **diagonal** on the inner ring, or running from one side to the other on the outer ring | **Misalignment**: shaft deflection, cocked housing, bent shaft, housing bores not in line |
| Outer ring track in **two zones 180° apart** | **Ovalised (pinched) housing** or a housing bolted to a warped base; the ring is squeezed |
| Track **wider at one point** on a stationary ring | Local load from a distorted housing or shaft seat (a burr, a high spot) |
| Inner ring track **wider than the outer ring's** on a stationary shaft | Wrong fit: the inner ring is creeping (see fretting) |
| No track at all | Bearing never carried load (not the failed one) or brand new |

## Damage modes (ISO 15243)

![False brinelling on test bearings: polished depressions at ball spacing](/photos/bearings/false-brinelling.jpg)

*False brinelling on test bearings: polished depressions at ball spacing. Photo: DirkDrees, CC BY-SA 4.0, via commons*

### 1. Fatigue (spalling / flaking)

- **Subsurface-initiated**: flakes with a smooth crater and a coarse bottom, starting in the load zone in the middle of the track, spreading in the rolling direction; the end of the design life, or a heavily overloaded bearing. Cause: load higher than expected (belt over-tension, misalignment, unbalance), the end of life. Fix: correct the load; bigger bearing; check the L10 calculation.
- **Surface-initiated**: fine cracks and micro-spalls starting at the surface, often with a grey, frosted look first (micro-pitting), in a track that shows a pattern of dents: from **inadequate lubrication film** (too thin an oil, too hot, too little) and **contamination** dents acting as crack starters. Fix: the right viscosity at operating temperature, clean grease, better sealing.

### 2. Wear

- **Abrasive**: dull, matte raceways and rollers, the track looks sand-blasted; the cage pockets worn; rolling elements undersize; ends of rollers worn. Cause: **dirt** (grit in the grease, failed seals, dirty handling, dirty grease gun nozzle). Fix: sealing, clean lubrication practice, filtration on oil systems.
- **Adhesive (smearing, skidding)**: streaks and torn metal on rollers and raceways where they slid instead of rolled: rollers skidding under too light a load at high speed (an unloaded roller bearing), sudden acceleration, too thick a grease at start-up. Smearing of roller ends on ribs: thrust overload or lube starvation.

### 3. Corrosion

- **Moisture corrosion**: rust pits, etch marks, often at the roller pitch (a **stationary** bearing with water in it: the rollers' contact points etch): water in the grease, washdown, condensation in storage, a machine parked in the weather. Fix: seals, water-resistant grease, purge greasing, storage.
- **Fretting corrosion (fit rust)**: **reddish-brown or black powder** on the **bore or the OD**, sometimes rubbed bright spots: the ring **creeping** on a loose fit or the seat flexing under a heavy load; a bore that has fretted is also often oversize. Fix: correct fit (see [fits](/article/bearing-clearance-and-fits-tables)), repair the seat; retaining compound only for light loads.
- **False brinelling**: **shallow depressions at roller/ball pitch with a polished or rusty bottom, no raised edges**, on a bearing that **did not rotate** while it vibrated: shipped on a truck, standby machines next to running ones, a spare motor stored on a vibrating floor; the oil film is squeezed out and the surfaces fret. Fix: rotate standby machines' shafts weekly (a quarter turn plus a bit), ship with shafts locked, isolate stored equipment from vibration.

### 4. Electrical erosion

- **Excessive current (spark)**: craters, welded spots, pitting like arc strikes: **welding current through the bearing** (the ground clamp on the wrong place), or a lightning strike.
- **Current leakage (VFD shaft currents)**: **fluting**: a regular **washboard** of grey lines across the raceway, evenly spaced (the outer ring looks like a record); under magnification the surface is a field of microscopic craters; the grease is **blackened** and the bearing noisy. Cause: common-mode voltage from a **VFD** discharging through the bearing's oil film (thousands of tiny arcs per second); also stray currents from bad motor grounding. Fix: **shaft grounding ring** (AEGIS type) or brush at the drive end, an **insulated bearing** (ceramic-coated or hybrid ceramic) at the non-drive end, proper VFD cable and grounding (shielded cable, 360° terminations), lower the carrier frequency; details in [VFD basics](/article/vfd-basics-for-millwrights). Plain replacement lasts weeks.

### 5. Plastic deformation (dents)

- **True brinelling**: **dents at the rolling element pitch with raised edges** (the metal was pushed), from a **static overload or an impact**: dropping the bearing, pressing the bearing on through the rolling elements (a hammer on the outer ring to mount it on a shaft), a shock load, a jammed conveyor. Every dent becomes a noise and later a spall. Fix: mount on the ring with the fit, use a press/heater, protect from impact; check that the machine did not see a shock.
- **Indentation by debris**: random dents of various sizes (with raised edges) from hard particles rolled over: contamination (weld spatter, casting sand, grit from the housing). Fix: cleanliness, filtration.
- **Overload deformation**: rolling elements and raceways flattened; heavy static load on a stationary bearing.

### 6. Fracture and cracking

- **Forced fracture**: an inner ring **split across** (axial crack) from **too much interference** (driven up a taper too far, a shaft oversize, or a seat with a burr), or a ring cracked by a hammer or a puller jaw.
- **Fatigue fracture**: a ring cracked through after long running from a cyclic load or a ring flexing on a soft or loose seat.
- **Thermal cracking**: crack patterns from a **spun ring** (the ring rotated on the seat and frictional heat cracked it); look for bluing and smearing on the bore or OD.

## Overheating and lubrication failure (the everyday one)

| Sign | Meaning |
|---|---|
| **Discoloured rings: straw (400°F), brown, blue (550-600°F), black** | Overheating: lubrication failure, over-greasing (churning), preload, excessive speed, misalignment, heat from the process; a **blue bearing is scrap and the shaft's hardness next to it is gone** |
| Grease **hard, dry, caked, or oxidised black** | Too hot for too long, wrong grease, never regreased, or over-greased and churned |
| Grease **milky / watery** | Water contamination |
| Grease looks like it has **grit** (rub it between two fingers) | Dirt |
| Cage **bronze coloured (from a steel cage)** or deformed | Heat, lubrication starvation, misalignment, contact with a housing |
| Rollers **blue at the ends, ribs smeared** | Lubrication failure at the roller-rib contact: thrust without enough oil film |
| Raceways **glazed, mirror bright** | Running with metal-to-metal contact: too thin a film |
| Rolling elements **welded/skidded** | Total lube failure: the bearing seized |

Over-greasing kills as many bearings as under-greasing: a full housing churns, the temperature climbs, the grease oxidises and the seals blow; quantities and intervals in [regreasing intervals](/article/regreasing-intervals-and-quantities).

## Cage failure

Cage breakage is usually the **last** event, not the first: it follows misalignment (the cage is forced to steer), excessive speed, lubrication failure (cage-to-roller friction), contamination (worn pockets), or vibration with a stationary bearing. A broken cage with clean raceways and a blue tint points to lubrication; a broken cage with a diagonal track points to misalignment.

## Putting it together

| What you found | Most likely root cause | Corrective action |
|---|---|---|
| Wide tracks both rings + blue rings + hard grease | Preload from a too-tight fit or C-clearance too small; heat | Correct the fit, C3, check the mounting method |
| Diagonal track + cage broken | Misalignment / bent shaft / housing bores out of line | Align the housings, check the shaft runout, self-aligning bearing if the misalignment is inherent |
| Fretting powder on the bore + track wider on the inner ring | Loose shaft fit; ring creeping | Repair the seat to size, correct fit |
| Dents at roller pitch with raised edges + noise from day one | Brinelling from mounting or impact | Mount with heat / press on the correct ring; handling |
| Dents at pitch **without** raised edges, rusty, on a spare or a standby | False brinelling | Rotate stored/standby shafts; vibration isolation |
| Washboard fluting + black grease + VFD on the motor | Shaft current | Grounding ring / insulated bearing / cable and grounding fix |
| Sand-blasted raceways + worn cage + dirty grease | Contamination | Seals, clean grease practice, purge |
| Water etch at pitch + rust | Water in the bearing | Seals, water-resistant grease, purge after washdown |
| Spalling in the centre of a normal track after long life | Fatigue: end of life, or overload | Check the load, belt tension, unbalance; accept if life was reached |
| Micro-pitting / frosting + spalls, oil too thin or hot | Lubrication film too thin | Correct the viscosity for the temperature; cooler running |
| Split inner ring on a taper mount | Driven up too far | Follow the drive-up chart |
| Smearing on rollers, light load, high speed | Skidding | Correct preload/minimum load, lighter grease |

Write the finding on the work order with the corrective action; the same bearing failing twice with the same evidence means the corrective action was not done.

## Related

- [Bearing removal (preserving evidence)](/article/bearing-removal-pullers-and-heating)
- [Bearing clearance and fits tables](/article/bearing-clearance-and-fits-tables)
- [Bearing mounting with heat](/article/bearing-mounting-with-heat)
- [Regreasing intervals and quantities](/article/regreasing-intervals-and-quantities)
- [Grease types and compatibility](/article/grease-types-and-compatibility)
- [VFD basics for millwrights (shaft currents)](/article/vfd-basics-for-millwrights)
- [Vibration signatures](/article/vibration-signatures)
