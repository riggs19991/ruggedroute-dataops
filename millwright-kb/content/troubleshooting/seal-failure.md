---
title: "Seal Failure Analysis: Mechanical Seals, Lip Seals, O-Rings and Packing, Reading the Failed Seal Faces and Lips to Find the Cause"
slug: seal-failure
category: troubleshooting
kind: reference
tags: [seal failure, mechanical seal failure, seal face, heat checking, thermal cracking, dry running, seal leak, lip seal failure, shaft groove, lip seal hardened, O-ring failure, extrusion, nibbling, compression set, spiral failure, packing failure, stuffing box, flush plan, seal chamber, face wear, blistering, coking]
source: "John Crane, Flowserve and Chesterton mechanical seal failure guides; API 682 (seal piping plans); SKF and Freudenberg (Simrit) radial shaft seal failure catalogues; Parker O-Ring Handbook (failure modes); Fluid Sealing Association packing troubleshooting."
summary: "How to read a failed seal like an inspector: what heat-checked, chipped, worn, blistered or coked mechanical seal faces mean; why a lip seal leaks (hardened lip, grooved shaft, wrong installation, pressure); the seven O-ring failure patterns; and why packing scores shafts and leaks, each with the root cause and the fix that stops the repeat."
---

> A seal is the **witness**, not the culprit. Most seal failures come from something else: dry running, pipe strain, misalignment, vibration, a bad sleeve, a wrong flush, a dirty installation. Save the failed seal, wipe it gently, look at it under a light and a loupe, and match the pattern below before you order another one.

## Mechanical seals: reading the faces

Two lapped faces (usually a carbon rotating face against a silicon carbide or tungsten carbide stationary, or hard against hard for abrasive service) run on a film of the pumped liquid a few microns thick. Anything that breaks that film, tilts the faces, or attacks the parts shows up on the faces and the secondary seals.

![Seal face wear track patterns](/img/troubleshooting/seal-face-patterns.svg)

*Seal face wear track patterns*

| What you see | What it means | Root cause and fix |
|---|---|---|
| **Heat checking**: fine radial cracks across the hard face (ceramic, tungsten carbide); carbon face may be glazed | **Dry running or loss of face lubrication**: film broke, faces got hot fast | Pump run dry or lost suction, vapour in the seal chamber (product flashing), no flush, vent not opened on a vertical pump; install a flush plan (11, 13, 32), vent before starting, low-flow protection; see [mechanical seal replacement](/article/mechanical-seal-replacement-centrifugal-pump) |
| **Carbon face blistered, pitted, chunks broken out** | Blistering: oil or viscous product trapped in the pores expands with heat | Wrong carbon grade for the fluid; hot oil service needs a specific grade; stationary face material change |
| **Carbon face worn heavily but evenly, hard face fine** | Abrasives in the fluid, or long run | Flush plan with a cyclone separator (31) or clean external flush (32); hard-on-hard faces (SiC/SiC) |
| **Wear track wider than the narrow face** or offset | **Misalignment / shaft deflection / runout**: faces not square to the shaft, or shaft moving | Check shaft runout (< 0.002 in), sleeve runout, bearing condition, pipe strain, alignment, impeller balance; the seal cannot cure a bent shaft |
| **Wear track narrower than the face, or only on part of the circumference** | Faces not flat: distorted gland (uneven bolt torque), damaged seat, stationary cocked | Torque gland bolts evenly and lightly; check the seat sits square; check the seal chamber face is perpendicular |
| **Chips at the ID or OD of a face** | Mishandled at installation, or pressure over the rating, or "hydraulic hammer" | Careful handling; check pressure; balanced seal for higher pressure |
| **Coking / hard black build-up on the atmospheric side** of the faces or on the springs | Hot hydrocarbon leaking past and carbonising | Steam quench (plan 62) or a nitrogen quench; cooler seal chamber |
| **Springs clogged, corroded or fractured** | Product solidifying (polymers, slurries), corrosion (wrong metallurgy), fatigue from vibration | Metal bellows seal (no springs in the product), material upgrade, fix vibration |
| **Elastomer (O-ring, boot) swollen, hard, cracked, extruded** | Chemical attack, temperature over the elastomer limit, wrong material | Match the elastomer to the fluid and temperature (see O-rings below); Kalrez/FFKM for aggressive chemicals |
| **Fretting on the shaft or sleeve under the dynamic O-ring** | The seal is moving axially all the time (vibration, pressure pulsing, misalignment) and the O-ring is wearing a groove | Fix the vibration/alignment; hard-coated sleeve; a bellows seal has no dynamic O-ring |
| **Seal leaked from day one** | Installation: faces contaminated (touched with fingers, dirty), wrong working length (set screws not at the mark), damaged O-ring on a keyway or shoulder, faces not lubricated for start, gland not square | Clean install, protect keyways and threads with tape, set the length from the maker's dimension, check the faces before fitting |
| **Leaked after a few weeks, faces look fine, elastomer flattened** | Compression set from heat; seal ran too hot | Cooling flush, jacket, check temperature |
| Seal faces "welded" together / hard face has a full-circle burn | Massive dry run | Everything above; find why it ran dry |
| Leaks only at start-up, then stops | Vapour in the chamber before priming, faces opening momentarily, thermal shock | Vent the seal chamber; warm up; plan 13 on vertical pumps |
| Leaks only on shutdown / when hot | Thermal expansion, elastomer at its limit | Temperature check |

Rules of thumb: a mechanical seal needs the **seal chamber vented and full of liquid** before start-up; 0.002 in runout at the seal faces is the limit; a **balanced** seal for pressures above about 100-150 psi in the chamber; a **flush plan** whenever the product is hot, dirty, vaporising or crystallising. Life is set by the pump condition: a pump with 0.010 in of shaft deflection at the seal eats seals at any price.

## Lip (radial shaft) seals

| What you see | Cause | Fix |
|---|---|---|
| **Lip hardened, cracked, brittle** | Heat: shaft speed too high for the material, under-lubricated lip, elastomer wrong (NBR over 210°F) | Fluorocarbon (FKM) lip for heat; lubricate the lip at install; check that oil actually reaches the seal |
| **Lip worn wide and flat** | Long service, abrasives, rough shaft (over 20 µin Ra), over-speed, lack of lubrication | Shaft finish 10-20 µin Ra plunge-ground (no lead: a spiral lead pumps oil out); wear sleeve; dust lip |
| **Shaft grooved under the lip** | Normal wear over years, abrasives in the oil, lip too tight (wrong seal or a spring too strong), dry running | Wear sleeve (Speedi-Sleeve) or move the seal to a new track by shimming its depth; fix contamination |
| **Lip turned inside out, torn, nicked** | Installed over a keyway, thread or sharp shoulder without protection; pushed on dry; installed backwards then pushed the other way | Bullet/tape over keyways and threads; lubricate; use an installation sleeve |
| **Seal pushed out of the bore, or cocked** | Pressure behind the seal (plugged breather, gearbox pressurising), bore too big, installed cocked with a punch | Clean the breather; check the bore; press square with a driver of the right size |
| **Leak between the OD and the bore** | Bore scored, seal OD damaged, wrong size, no sealant on a metal-OD seal in a rough bore | Sealant on the OD, correct bore finish and size |
| **Garter spring gone or popped off** | Installed with the spring outward and it fell off; corrosion | Spring toward the oil (spring side faces the fluid being retained) |
| **Leak with a new seal, shaft and bore fine** | Wrong direction (spring side out), lip lubricated with grease that hardened, seal fine but the **bearing has clearance** and the shaft whips | Check bearing endplay and clearance; the seal cannot follow a shaft moving 0.010 in |
| Excessive heat at the seal | Too much interference, dry lip, high speed, wrong material | Correct seal; check lubrication reaches the lip |

Never reuse a lip seal; never install with a hammer directly on the seal; never let it ride over a keyway unprotected; **spring side toward the oil**.

## O-rings (Parker's seven failure modes)

| Failure | Looks like | Cause | Fix |
|---|---|---|---|
| **Abrasion** | Flat, worn surface on the dynamic side, grooves | Rough surface, contamination, poor lubrication | Surface finish 8-16 µin Ra on dynamic seals; filtration; harder compound |
| **Compression set** | Flat sides, no longer round, does not spring back | Heat over the limit, incomplete cure, too much squeeze, chemical swell | Higher-temperature material (FKM, silicone), correct groove |
| **Extrusion and nibbling** | Frayed, chewed edge on the low-pressure side | Pressure too high for the clearance/hardness, wrong groove, excessive clearance from wear | Back-up rings, harder compound (90 durometer), tighter clearance (see [cylinder repair](/article/cylinder-repair-and-seal-kits)) |
| **Explosive decompression** | Blisters, pits, cracks after depressurising | Gas absorbed under high pressure expanded on release | Slow depressurisation, ED-resistant compounds, harder materials |
| **Installation damage** | Small cuts, nicks, a piece missing; often a 45° cut | Sharp edges, threads, forcing over a bore edge, no lubricant, twisted | Chamfers, lubrication, tape over threads; do not stretch over 50% |
| **Spiral failure** | Deep spiral cuts around the ring (long-stroke dynamic seals) | The ring rolls and twists in the groove: uneven friction, wide groove, low speed, side loads | Correct groove, lubrication, X-ring or T-seal instead of O-ring |
| **Chemical attack / swell / hardening** | Swollen, soft, sticky, or hard and cracked; changed size | Wrong material for the fluid; phosphate-ester fluids destroy NBR; ozone cracks NBR | Match material: NBR for mineral oil, FKM for heat and fuels, EPDM for water/glycol/brake fluid/phosphate esters (never mineral oil), silicone for static high-temperature, FFKM for solvents and aggressive chemicals; see the [O-ring material rules](/article/cylinder-repair-and-seal-kits) |

Also: **heat hardening** (glazed, brittle, cracked when bent), **weather/ozone cracking** (stored near motors or in sunlight), **wrong size** (stretched more than 5% on its ID in a static groove, or a ring bought by eye). Shelf-life rules are in [spare parts storage](/article/spare-parts-and-bearing-storage).

## Compression packing

| What you see | Cause | Fix |
|---|---|---|
| **Shaft or sleeve scored under the packing** | Gland over-tightened (packing running dry), abrasive product, wrong packing (hard filament, aramid) on a soft sleeve, no lantern-ring flush | Adjust for 10-60 drops/min leakage: packing must leak to live; softer packing (PTFE/graphite); flush water; hardened sleeve; see [packing](/article/pump-packing-and-stuffing-box) |
| **Packing hard, charred, glazed** | Over-tightened, ran dry, no flush, temperature over the rating | As above; graphite packing for heat |
| **Leaks that cannot be stopped by tightening** | Packing worn out, extruded past the bottom ring, sleeve grooved, gland bottomed, rings cut short | Repack; check sleeve; cut rings to length with a mandrel; stagger joints 90° |
| **Packing extruded through the gland or bottom** | Excessive clearance (worn box or gland), wrong size, over-tightened | Correct size; anti-extrusion ring; new gland follower |
| **Rings worn only on one side** | Shaft off-centre in the box: bearings worn, shaft bent | Fix the pump |
| Excessive heat at the box | Over-tight, no leakage, no flush | Loosen and adjust with the pump running |
| Leak from day one after repacking | Rings not seated one at a time, joints in line, old packing left in the bottom, no break-in | Seat each ring with a tamping tool; joints staggered; tighten gradually over the first hour |

## Before you fit the replacement

1. Runout at the seal location (< 0.002 in mechanical seal, < 0.005 in lip seal), shaft and sleeve finish, bore condition.
2. Bearing endplay and clearance; a worn bearing fails every seal.
3. Alignment and pipe strain (see [pipe strain](/article/pipe-strain-and-flange-alignment)).
4. Seal chamber vent, flush and quench connections clean and working; breather clear on gearboxes.
5. The right elastomer and face materials for the fluid and temperature; the right seal type for the pressure and speed.
6. Cleanliness: clean hands, clean bench, no touching the faces.

## Related

- [Mechanical seal replacement on a centrifugal pump](/article/mechanical-seal-replacement-centrifugal-pump)
- [Pump packing and the stuffing box](/article/pump-packing-and-stuffing-box)
- [Cylinder repair and seal kits (O-ring and hydraulic seal rules)](/article/cylinder-repair-and-seal-kits)
- [Pump troubleshooting](/article/pump-troubleshooting)
- [Bearing failure analysis](/article/bearing-failure-analysis)
