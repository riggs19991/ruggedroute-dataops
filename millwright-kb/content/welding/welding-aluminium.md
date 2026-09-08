---
title: "Welding Aluminium: Alloy Weldability, 4043 vs 5356 Filler, Oxide Removal and Cleaning, MIG with Spool Gun or Push-Pull, AC TIG, Preheat, Cracking and Porosity"
slug: welding-aluminium
category: welding
kind: procedure
tags: [aluminum welding, aluminium welding, 4043, 5356, 6061 welding, 5052 welding, spool gun, push pull gun, aluminum MIG settings, AC TIG aluminum, oxide removal, aluminum porosity, aluminum cracking, aluminum preheat, 7075 weldable, cast aluminum welding, U groove drive roll, teflon liner]
source: "AlcoTec/ESAB Aluminum Welding Guide and filler selection chart; Lincoln Electric SuperGlaze data and aluminium GMAW guide; Miller aluminium MIG and TIG guidance; AWS D1.2 Structural Welding Code, Aluminum; Aluminum Association Welding Aluminum Theory and Practice."
summary: "What makes aluminium different (oxide, conductivity, no colour change, hydrogen porosity), which alloys weld and which do not, how to choose 4043 or 5356, the MIG settings and gun hardware that make .035/3/64 wire feed, AC TIG basics, preheat limits and the cracking and porosity rules."
---

## What is different

| Property | Effect | What you do |
|---|---|---|
| Oxide skin melts at **3700°F**; the metal at **1220°F** | Oxide floats and stops fusion; looks like a dull skin on the puddle | Remove it mechanically just before welding; AC or DCEP arc blasts it (cleaning action) |
| Conducts heat 5× faster than steel | Heat runs away; big parts need preheat or high current; small parts overheat suddenly | Hotter start, then back off; preheat thick sections |
| No colour change before melting | You cannot see it coming; it drops out | Watch for the shine on the puddle; practise on scrap |
| Dissolves hydrogen when liquid, rejects it when solid | **Porosity** from moisture, oil, hydrated oxide | Clean, dry, degrease, brush, weld within the hour |
| Expands 2× steel | Distortion, crater cracks, hot cracks in the wrong alloys | Preset, clamp, fill craters, filler selection |
| Strength is from heat treatment or work hardening | HAZ loses 30-50% of strength in 6061-T6 (to about 24 ksi from 45) | Design for it; never rely on a weld having base-metal strength in 6xxx/7xxx |

## Which alloys weld

| Series | Examples | Weldable by arc | Filler |
|---|---|---|---|
| 1xxx (pure) | 1100 | Yes | 1100, 4043 |
| 3xxx | 3003 | Yes | 4043, 5356 |
| **5xxx (Mg, work-hardened)** | **5052, 5083, 5086, 5454** | Yes, best of all | **5356** (5183/5556 for 5083) |
| **6xxx (heat-treatable)** | **6061, 6063, 6005** | Yes, **crack-sensitive if welded without filler**: always add filler | **4043** (or 5356) |
| 4xxx | 4043 (castings) | Yes | 4043 |
| 2xxx | 2024, 2014 | **No** (2219 yes with 2319) | |
| **7xxx** | **7075, 7050** | **No**: hot cracks and loses strength | 7005/7039 only, with 5356 |
| Castings | A356, 356, 319 | Yes with 4043 (A356); die castings porous and hard to weld | 4043, 4047 |

Marked "no" means the joint cracks or has no strength; braze, bolt or replace.

## 4043 or 5356

| | **ER4043 (5% Si)** | **ER5356 (5% Mg)** |
|---|---|---|
| Use on | 6xxx, castings, 1xxx, 3xxx; anywhere colour match does not matter | 5xxx alloys, 6061 when strength matters, structural |
| Fluidity / crack resistance on 6061 | Very fluid, most crack-resistant | Less fluid, more prone to cracking on 6061 if diluted heavily |
| Strength and ductility | Lower | Higher (better for bending/impact) |
| Feeds | Softer wire, harder to push | Stiffer, feeds better |
| Anodising | Turns dark grey (mismatch) | Matches |
| Service temperature | Any | **Not above 150°F (65°C)** sustained: stress-corrosion cracking |
| Colour | Bright, smutty black soot on MIG | |

Default: 4043 on 6061 and castings, 5356 on 5052/5083 and anything anodised or cold-worked. Never 5356 for parts running hot (engine, exhaust brackets, hot tanks).

## Cleaning: the order matters

1. **Degrease first** with acetone or an alkaline cleaner; wipe with clean lint-free rag. (Brushing before degreasing drives oil into the oxide.)
2. **Remove the oxide** with a **dedicated stainless steel wire brush** used only on aluminium, one direction, light pressure, or scrape with a carbide scraper. Do not use grinding discs that load up (aluminium smears); if you must grind, use a disc rated for aluminium and follow with the brush.
3. Weld **within 1 hour**, ideally minutes; oxide regrows.
4. Store filler wire and rod clean and dry in its tube; wipe TIG rod with acetone before use; throw out MIG wire that has sat open for weeks (porosity).
5. Preheat also dries the joint; a torch pass drives off moisture on humid days.

## MIG (GMAW) on aluminium

Aluminium MIG runs in **spray or pulsed spray only**, DCEP, 100% argon (Ar/He for over 3/8"). The wire is soft and feeds badly through a long steel gun, so the hardware is the hard part.

**Feeding hardware**

| Item | Setting |
|---|---|
| Gun | **Spool gun** (4" spool at the gun; up to 3/64" wire) for occasional work; **push-pull gun** for production and 12" spools; a standard gun works only with ≤ 10 ft cable, straight, Teflon/nylon liner, and .047 (3/64) wire |
| Drive rolls | **U-groove**, tension as light as it will feed (test: it should slip in your gloved hand) |
| Liner | Teflon or nylon, cut to length, plastic inlet guide |
| Contact tip | Sized **one over** (aluminium expands: .035 wire → .039/.040 tip, or tips marked "AL") |
| Wire | **3/64" (0.047, 1.2 mm)** for anything over 1/8" and for a standard gun; .035 on sheet with a spool gun; .030 only on the thinnest |
| Gas | 100% argon **30-40 cfh**; Ar/He 75/25 on plate over 3/8" |
| Nozzle | Larger, clean; anti-spatter spray is not needed |
| Polarity | DCEP |

**Starting settings, 4043/5356, argon, spray**

| Thickness | Wire | WFS (ipm) | Volts | Amps |
|---|---|---|---|---|
| 1/16" (16 ga) | .030 | 300-400 | 18-20 | 70-100 |
| **1/8"** | **.035** | **350-450** | **21-23** | **110-150** |
| 3/16" | .035 / 3/64 | 450-550 / 250-320 | 23-25 | 150-190 |
| **1/4"** | **3/64** | **300-380** | **24-26** | **180-230** |
| 3/8" | 3/64 | 380-460 | 26-28 | 230-280 (preheat) |
| 1/2" | 1/16 | 250-300 | 27-30 | 300-350 (preheat, Ar/He) |

Pulsed MIG (synergic "aluminium 4043 .035" program) is the best way to weld 1/16-1/8" and out of position; set the program and trim ±. Technique: **push 10-15°**, stickout 1/2-3/4", travel **fast** (aluminium MIG moves 2-3× steel speed, 20-30 ipm), stringer beads, tie the arc into the leading edge of the puddle. Black soot beside the bead is normal with 4043 (magnesium oxide with 5356, more so with a drag angle or too long an arc); heavy soot means too long an arc or a drag angle. Fill craters with the crater-fill function or by pulling back briefly; **crater cracks** are the aluminium MIG signature defect.

## TIG on aluminium

AC, 2% lanthanated tungsten, argon 15-25 cfh, balance 65-75% EN, 100-150 Hz on inverters; amperage **1 A per 0.001" plus 20-30%**. Full settings in [TIG setup](/article/gtaw-tig-setup) and the [material tables](/article/gtaw-settings-by-material). Technique: torch 10-15° push, tight arc (1/16-1/8"), wait for the shiny puddle, dab filler generously into the leading edge, keep the rod inside the shield, taper off with the pedal while adding a last dab into the crater. Thick parts and castings: preheat 200-300°F, then the puddle forms in seconds instead of soaking.

![AC balance: EN penetrates, EP cleans](/img/welding/ac-balance.svg)

*AC balance: EN penetrates, EP cleans*

## Preheat

- Not needed under 1/4" on a warm day; on cold or thick parts **200-300°F (95-150°C)** to start the puddle and drive out moisture.
- **Never above 400°F (200°C)** on 6xxx or 5xxx: 6061 loses temper, 5xxx sensitise to stress corrosion; keep interpass under 250°F (5xxx under 150°F where service is warm).
- Castings: preheat 300-400°F, slow cool wrapped; a bad casting outgasses oil and porosity for the first pass: grind it out and weld again.

## Cracking and porosity rules

| Problem | Cause | Fix |
|---|---|---|
| **Porosity** (holes, worm tracks, grey grainy bead) | Moisture, oil, hydrated oxide, old wire, gas leak, draft, too low flow, too long stickout | Clean in the right order, new wire, 30-40 cfh, check the gun O-rings and hose, weld within the hour, preheat damp parts |
| **Hot (solidification) cracks** down the bead centre | 6061 welded with no filler or too little filler; 5356 on 6061 in thick restrained joints; wrong alloy (7075) | Add filler, use 4043, convex bead, preheat, do not weld 2xxx/7xxx |
| **Crater cracks** | Stopping abruptly | Crater fill, pull back, dab and taper |
| Weld fell through | No visible warning; too hot, too slow | Practise, faster, less amps, backing bar (aluminium or copper) |
| Lack of fusion, cold laps | Oxide not removed, arc too long, push angle too flat, too cold | Brush, tight arc, more amps, spray not short-circuit |
| Bird-nest at the drive rolls | Steel liner, tension too high, contact tip too small, cable coiled | Teflon liner, U-rolls, AL tip, straight cable |
| Black smut everywhere | Long arc, drag angle, dirty base | Shorter arc, push, clean; a little smut is normal |
| Wire burns back to the tip | WFS too low for the voltage, tip too small, stickout too short | Raise WFS, AL tip, 1/2-3/4" stickout |

## Common mistakes

- Brushing with the steel brush from the welding bench: iron contamination and porosity.
- Using C25 gas from the steel machine: gross porosity and a black weld.
- Welding 6061 tube with no filler "to keep it neat": centreline crack every time.
- Standing the 12" spool of .035 on a 15 ft gun with a steel liner: bird's nest within a foot.
- Heating a 5083 tank to 500°F to "get it going": it now cracks in service.

## Related

- [TIG (GTAW) setup](/article/gtaw-tig-setup) and [TIG settings by material](/article/gtaw-settings-by-material)
- [MIG (GMAW) setup](/article/gmaw-mig-setup), [transfer modes](/article/gmaw-transfer-modes)
- [Gas selection and flow](/article/gas-selection-and-flow)
- [Weld defects and inspection](/article/weld-defects-and-inspection)
- [Brazing and soldering](/article/brazing-and-soldering) (aluminium brazing alternative)
