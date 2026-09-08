---
title: "Welding and Repairing Cast Iron: Identifying Grey, Ductile and White Iron, Nickel Rods (99% Ni vs 55% Ni), Hot and Cold Methods, Peening, Crack Repair with Studs, and When to Braze Instead"
slug: welding-cast-iron-and-repairs
category: welding
kind: procedure
tags: [cast iron welding, cast iron repair, nickel rod, ENi-CI, ENiFe-CI, 99 nickel, 55 nickel, Ni-Rod, Softweld, cast iron preheat, peening, cracked casting, gearbox housing crack, pump housing repair, studding, brazing cast iron, grey iron, ductile iron, white iron, spark test cast iron, machinable weld]
source: "AWS A5.15 (welding electrodes and rods for cast iron); Lincoln Electric Softweld 99Ni and 55Ni data sheets and cast iron welding guide; Hobart / Harris cast iron guidance; Castolin Eutectic and Special Metals Ni-Rod procedures; Machinery's Handbook cast iron data."
summary: "How to tell which cast iron you have and whether it can be welded, which nickel electrode to use and at what amperage, the two schools of cast iron repair (hot with 500-1200°F preheat and slow cooling, or cold with short beads and immediate peening), the crack-repair sequence with drilled ends, studding for big repairs, and the cases where brazing or a mechanical repair is the better answer."
---

> A cracked gearbox housing, pump volute, motor end bell or machine base is the classic millwright cast iron job. It can usually be repaired, but the metal is unforgiving: it is hard, it does not stretch, and it cracks when a weld shrinks against it. Decide method **before** striking an arc.

## Identify the iron

| Type | Fracture | Spark test (grinder) | Machinability | Weldability |
|---|---|---|---|---|
| **Grey iron** (most housings, bases, brake drums) | Grey, grainy, graphite flakes | Short, dull red, many fine bursts | Easy, dusty grey chips | **Fair**: nickel rods, preheat or cold method |
| **Ductile (nodular) iron** (heavy-duty housings, crankshafts, pipe) | Silvery, tougher | Similar to grey, slightly brighter | Good | **Good**: nickel rods, preheat 300-600°F |
| Malleable iron (fittings, hardware) | White then grey rim | Between grey and steel | Good | Fair: brazing preferred; welding destroys the malleablising |
| **White iron** (chilled wear surfaces, mill liners) | White, glassy, very hard | Short, red, few sparks | Not machinable | **Not weldable**; replace |
| Cast steel (looks like a casting, rings when struck) | Bright, ductile | Long straw sparks like mild steel | Like steel | Weld like steel (7018) |

More in [metal identification and spark test](/article/metal-identification-and-spark-test). Oil-soaked castings (gearboxes, engine blocks) must be heated to **700°F+ for an hour** to burn out the oil or the weld will be porous no matter what you do.

## Electrodes

| Electrode (AWS A5.15) | Trade names | Deposit | Use |
|---|---|---|---|
| **ENi-CI (99% Ni)** | Lincoln Softweld 99Ni, Ni-Rod 99, Hobart Nickel 99 | Soft, **machinable**, lower strength (about 40 ksi) | Thin sections, machined surfaces that must be re-machined, low-restraint repairs, filling |
| **ENiFe-CI (55% Ni)** | Softweld 55Ni, Ni-Rod 55, Nickel 55 | Stronger (about 60 ksi), tougher, expands closer to iron, **less machinable** but still doable with carbide | Thick sections, ductile iron, restrained cracks, structural repairs; the default for heavy housings |
| ENiFe-CI-A / ENiFeMn-CI | | Higher-strength versions | Ductile iron, heavy repairs |
| ECI (cast iron rod) | | Grey iron deposit | Oxy-acetylene "hot" welding only, with full preheat and slow furnace cooling |
| ESt (steel electrode) | 7018 in a pinch | Steel, hard, brittle HAZ | Non-machinable, non-structural filling only; expect cracks |
| MIG: ERNi-CI / ERNiFe-CI wires, or 99% Ni "flux-core" | | | Production repairs with argon/argon-He |
| TIG: ERNi-CI, ERNiFe-CI | | | Small cosmetic repairs |

**Amperage (typical, DCEP or AC; confirm on the box)**: 3/32" **60-90 A**, 1/8" **80-120 A**, 5/32" **110-150 A**. Run at the **low end**: the aim is minimum heat into the casting. Store rods dry (they are low-hydrogen-type coatings).

## Choose the method

| | **Hot method (preheat)** | **Cold method (no preheat)** |
|---|---|---|
| When | Complex castings, thick sections, high restraint, machined parts that must stay flat, ductile iron | Simple shapes, thin to medium sections, field jobs where you cannot heat the whole casting, cosmetic and non-structural cracks |
| Preheat | **500-1200°F (260-650°C)** on the whole casting, evenly, held during welding; interpass same | None, or 100-200°F to dry it; **never let the casting get above hand-warm, about 150°F, 2" from the weld** |
| Beads | Longer beads allowed, still stringers | **1" (25 mm) beads maximum**, staggered around the repair so no area heats up |
| Peening | Helpful | **Mandatory, immediately** while the bead is red: light, fast blows with a ball-peen or air needle-scaler to stretch the weld as it shrinks |
| Cooling | **Slow**: wrap in ceramic blanket, bury in vermiculite, dry sand or lime; cool overnight; furnace-cool if possible | Air cool between beads; let it cool to touch before the next bead in the same area |
| Result | Lowest risk of cracking, softer HAZ, machinable with Ni rods | Some hard HAZ; high-nickel deposit is still machinable; cracks possible on restrained joints |

Preheat uneven = cracks. If you cannot heat the whole casting evenly to at least 500°F, use the cold method properly instead of a half-hearted hot method.

## Crack repair procedure

![Drill the crack ends, V it out, short stringers in sequence, peen](/img/welding/cast-iron-repair.svg)

*Drill the crack ends, V it out, short stringers in sequence, peen*

1. **Find the ends** of the crack: clean, then dye penetrant, or heat with a torch and watch for oil sweat along the crack line. Cracks run further than they look.
2. **Drill 1/8-1/4" holes at each end**, 1/4" beyond the visible end, to stop it running.
3. **V it out** with a carbide burr or a grinder (not a torch: local heat cracks it) to a 60-90° groove, **half to two-thirds** through on thin walls, full depth with a backing where possible on thick. Round the bottom; no sharp corners. Grinding a cast iron often smears graphite over the surface: finish with a burr, and wipe with acetone.
4. **Degrease and burn out oil**: torch the groove to a dull red and let the oil sweat and burn off, repeat until it stops smoking; brush.
5. Preheat per the method chosen; check with a temp stick 2" from the groove.
6. Weld with Ni rod, DCEP, low amps, **short arc, stringers**, 1" beads (cold method). **Start at the drilled ends and work toward the middle**, alternating ends, so shrinkage keeps closing the crack instead of pulling it open; **peen each bead immediately**; chip and brush before the next.
7. Multi-pass: **buttering** the groove faces first with 99Ni gives a soft layer that absorbs the shrinkage, then fill with 55Ni.
8. Finish: fill the drill holes last, grind flush if required, slow-cool per the method.
9. Inspect after cooling and again after 24 h with dye penetrant; a hairline crack beside the weld means the HAZ cracked (too much heat or too fast cooling): grind out and repeat with more preheat or shorter beads.

## Studding for large or loaded repairs

For thick, load-bearing sections, screw **steel studs** (1/4-3/8" NC, 3/8-1/2" into the iron, projecting 3/16-1/4") into the groove faces at 1/2-3/4" spacing, weld around each stud with Ni rod (the studs anchor the weld in the casting mechanically), then fill. Standard for broken teeth on big castings, cracked machine frames and press housings. The weld now hangs on steel, not on a brittle fusion line.

## Brazing instead

Braze welding with **low-fuming bronze (RBCuZn-C)** and an oxy-acetylene torch at about **1200-1600°F** (dull red) puts no fusion into the iron and rarely cracks it. Right for: thin sections, cracked pump housings not exposed to heat over 500°F, missing lugs, water jackets. Wrong for: parts running hot, parts that will be painted and must be colour-matched (bronze shows), and for high-load structural cracks. Procedure in [brazing and soldering](/article/brazing-and-soldering): the casting must be preheated to a dull red at the joint, tinned with bronze (the flux flows and the bronze wets grey iron only when the graphite has been burned off the surface), then filled.

## Other options

- **Cold stitching / metal stitching** (Lock-N-Stitch, Metalock): drilled and tapped locks and stitching pins across the crack; no heat at all; the professional repair for engine blocks and large frames.
- **Epoxy metal fillers** for non-structural leaks and cosmetic fills.
- **Replacement**: a cracked bearing housing on a critical machine is often cheaper to replace than to repair and re-machine.

## Common mistakes

- Using 7018 "because it is cheap": glass-hard HAZ, cracks in a day, and now the part cannot be machined.
- Long beads without peening: the weld pulls the casting apart behind it.
- Preheating one side with a torch and calling it hot method: differential expansion cracks the other side.
- Quenching to save time: the whole thing cracks.
- Not burning out the oil: porosity in every pass.
- Welding white iron wear plates: it just shatters; bolt on new plate.

## Related

- [Brazing and soldering](/article/brazing-and-soldering)
- [Preheat, interpass and carbon equivalent](/article/preheat-interpass-and-carbon-equivalent)
- [Metal identification and spark test](/article/metal-identification-and-spark-test)
- [Stick (SMAW) setup](/article/smaw-stick-setup)
- [Hardfacing and build-up](/article/hardfacing-and-buildup)
