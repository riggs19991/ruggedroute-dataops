---
title: "Plasma Piercing, Keyholing Thick Plate and Plasma Gouging: Pierce Height and Delay, the Rolling Pierce, Keyhole Technique Beyond Pierce Capacity, Inside Cuts, Bolt-Hole Starts, and Gouging Settings and Profiles"
slug: plasma-keyholing-and-piercing
category: cutting-gouging
kind: procedure
manufacturer: Hypertherm
model_numbers: ["Powermax45 XP", "Powermax65", "Powermax85", "Powermax105"]
tags: [plasma pierce, piercing plasma, pierce height, pierce delay, rolling pierce, keyhole, keyholing, keyhole cut, thick plate plasma, inside cut, start hole, plasma gouging, gouging consumables, plasma gouge stainless, plasma gouge aluminum, remove weld plasma, back gouge plasma, spot weld removal, hole in plate, plasma blowback]
source: "Hypertherm Powermax45 XP Operator Manual 809240 rev. 4 (pierce procedure, pierce height 1.5-4× cut height, lead-in rule, gouging chapter tables 2-7: 45 A Maximum Control gouging profiles at 40°/50°, 10 A precision gouging); Hypertherm gouging application guidance."
summary: "The two ways to start a plasma cut in the middle of a plate (a straight pierce within pierce capacity, and the tilted rolling pierce), how to keyhole through plate thicker than the pierce rating by walking a hole open, how CNC tables set pierce height and delay, inside cuts and hole starts that keep the consumables alive, and plasma gouging: which consumables, what angle and standoff, and the depth-and-width profiles from Hypertherm's tables."
---

## Piercing rules

- **Pierce capacity ≈ half the recommended cut thickness** (Powermax45 XP: 1/2"; 65: 5/8"; 85: 3/4"; 105: 7/8"). Piercing above it burns the shield and nozzle with blow-back and often will not go through.
- **Pierce height 1.5-4× cut height** (Powermax45 XP: 0.15" / 3.8 mm, 250% of the 0.06" cut height) so the molten fountain does not land on the tip. By hand, that means **tilt the torch** so the metal blows away from you and the tip.
- **Pierce delay**: the arc must burn through before the torch moves: 0.1 s on 16 ga up to 1 s on 1/2" (table in [plasma cutting setup](/article/plasma-cutting-setup)). Moving early drags an unfinished pierce and the arc stretches and dies.
- **Lead-in ≈ material thickness** on CNC (pierce 1/2" away from the line on 1/2" plate), so the pierce crater is not on the finished edge.
- Never pierce on a spot where you can edge-start instead; every pierce costs consumable life.

## Straight pierce (thin material, within capacity)

1. Torch **90°** to the plate at pierce height (tip 1/8-3/16" off, or drag shield lifted).
2. Trigger; hold still until **sparks come out under the plate** and the sound changes.
3. Lower to cut height (drag the shield) and move off along the cut line.

## Rolling pierce (the hand-torch standard)

![Tilt, pierce, rotate upright, square and cut](/img/cutting-gouging/plasma-pierce-sequence.svg)

*Tilt, pierce, rotate upright, square and cut*

1. Hold the torch at about **30° to the plate** (Hypertherm) with the tip **within 1/16" (1.5 mm)** of the surface, pointed **away from you**.
2. Trigger. The molten metal blows out the far side of the puddle, away from the tip.
3. As the arc digs in, **roll the torch upright** to 90° (2-3 seconds on 3/8"), keeping the tip at height.
4. When sparks exit below, drag the shield down and start the cut.
5. On plate near the pierce limit, start the roll on the **scrap side** of the line, and give it the full delay before moving.

## Keyholing thick plate (beyond pierce capacity)

For 5/8-1" on a 45 A machine, or any thickness above the pierce rating, you open a **keyhole** rather than piercing straight down:

1. Rolling pierce start at 30-45° on the scrap side, roughly 1" from the cut line.
2. Instead of holding still, **walk the arc in a small circle or a short back-and-forth** (1/4-1/2" long), keeping the torch tilted so the slag fountain goes away from you. The circle lets the metal blow out sideways; the hole grows and the arc gets deeper each pass.
3. Increase the circle slightly and slowly bring the torch upright as the arc bottoms out; when sparks exit below, you have a hole the width of two kerfs.
4. Drag the shield down, move to the cut line at severance speed for the first inch, then at the chart speed.
5. Wear a face shield over the helmet and full leathers: keyholing throws molten metal several feet.

Alternative for repeated thick starts: **drill a 3/8-1/2" start hole**, or begin at the plate edge with an oxy-fuel or grinder notch. On a CNC table, thick plate uses a "pierce-and-lift" routine (higher pierce height, longer delay, torch retract) built into the controller; do not exceed the pierce chart.

## Inside cuts and holes

- Pierce **inside the scrap**, not on the line; lead in to the line with a curve so there is no notch on the finished edge; lead out the same way.
- Holes: the square side of the kerf is on the **right** of the direction of travel, so cut holes **clockwise** (viewed from above) to leave the square edge on the plate, and cut outside profiles **counter-clockwise**. Prove it on scrap with your own torch before a real part.
- Bolt holes under about **1.5× the plate thickness** in diameter come out tapered on plasma; drill them, or plasma-cut undersize and drill/ream. Hypertherm's rule for good holes on Powermax: diameter ≥ 1.5-2× thickness with FineCut consumables.
- Slots for cutting out a section: pierce in the middle, cut to the corners, do not try to turn sharp corners with a hand torch; overrun and come back.

## Plasma gouging

Plasma gouging uses **gouging consumables** (a wide-orifice nozzle and an open shield) so the arc sweeps metal out of a groove instead of cutting through. Advantages over carbon-arc: **no carbon pick-up**, far less noise and smoke, works on **stainless and aluminium**, controllable shallow grooves; disadvantage: much lower metal removal (7.5 lb/h at 45 A versus 20-30 lb/h with a 3/8" carbon).

Powermax45 XP has two processes: **Maximum Control gouging (26-45 A)** with its consumables, and **Precision gouging (10-25 A)** for spot-weld removal and light surface work.

| Setting | Maximum Control gouging, 45 A | Precision gouging, 10 A |
|---|---|---|
| Torch angle | **40-50°** from the plate | 40-45° |
| Standoff | **1/4" (6 mm)** | 0.01-0.05" (nearly touching; up to 1/8" for a very light gouge) |
| Speed | 10-40 ipm | slow |
| Air | 350 scfh at 60 psi | 350 scfh at 55 psi |
| Removal rate on mild steel | 7.5 lb/h | 0.5 lb/h |

**Gouge profile, 45 A on mild steel (Hypertherm Table 3)**

| Torch angle | Speed (ipm) | Depth (in) | Width (in) |
|---|---|---|---|
| 40° | 10 | 0.183 | 0.331 |
| 40° | 20 | 0.126 | 0.268 |
| 40° | 30 | 0.074 | 0.231 |
| 40° | 40 | 0.055 | 0.206 |
| 50° | 10 | 0.195 | 0.263 |
| 50° | 20 | 0.132 | 0.205 |
| 50° | 30 | 0.107 | 0.192 |
| 50° | 40 | 0.088 | 0.181 |

Stainless steel gouges slightly narrower and deeper at the same settings (Table 5: 40°, 10 ipm → 0.114" deep × 0.245" wide; 50°, 10 ipm → 0.210" × 0.224"). Steeper angle = deeper and narrower; faster = shallower. Multiple passes for deeper grooves; a weaving motion widens the groove.

**Technique**: hold the torch at the angle with the standoff, fire, and **push** the molten metal ahead of the arc away from you (the arc blows the puddle out the front of the groove). Keep a steady speed: a hiss with a continuous stream of sparks ahead. Do not let the nozzle touch the puddle (the standoff is what keeps the shield alive). For **back-gouging a weld root**, take two passes at 45° and check with a straightedge; for **removing a weld or a lug**, gouge along the fusion line, then grind. **Spot-weld removal** (Precision gouging, 10 A): torch at 40-45° on one side of the spot, lift and rotate around the weld until the sheet separates; the base sheet stays.

## Safety notes specific to piercing and gouging

- Blow-back and gouge spray travel 10-20 ft: clear the area, fire-resistant screens, no open flammables, fire watch.
- Face shield over the shade-8 helmet lens for gouging; hearing protection; leathers; gauntlets.
- Fumes: gouging aluminium and stainless makes dense fume: extraction or respirator.
- Do not pierce or gouge over a table water tray without knowing what it holds; hydrogen from aluminium dross in water tables can pop.

## Related

- [Plasma cutting setup and cut charts](/article/plasma-cutting-setup)
- [Carbon-arc gouging](/article/carbon-arc-gouging)
- [Joint design and fit-up (back-gouging)](/article/joint-design-and-fit-up)
- [Hole making in the field](/article/hole-making-in-the-field)
