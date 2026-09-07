---
title: "Hardfacing and Build-Up: Alloy Families by Wear Type, Buffer Layers, Chromium Carbide Check-Cracking, Manganese Steel Rules, Electrode and Wire Selection, Preheat and Bead Patterns"
slug: hardfacing-and-buildup
category: welding
kind: procedure
tags: [hardfacing, hard facing, hardsurfacing, build up, buildup, chromium carbide, tungsten carbide, manganese steel, austenitic manganese, buffer layer, check cracking, wear resistance, abrasion, impact, Stoody, Wearshield, Lincore, Hardalloy, McKay, bucket teeth, screw conveyor flights, hammer mill, crusher, waffle pattern, hardfacing amperage]
source: "Lincoln Electric Hardfacing Product and Procedures Selection Guide; ESAB/Stoody Hardfacing Guide; Hobart Hardalloy data sheets; AWS A5.13 / A5.21 (surfacing electrodes and rods); Postle Industries hardfacing guidance."
summary: "How to match a hardfacing alloy to the kind of wear a part sees (abrasion, impact, metal-to-metal, heat, corrosion), the difference between build-up and the hard overlay, why chromium carbide cracks on purpose and manganese steel must stay cool, layer limits, preheat by base metal, bead patterns for different service, and the settings for common rods and wires."
---

## Wear types decide the alloy

| Wear | Looks like | Examples | Alloy family |
|---|---|---|---|
| **Abrasion, low stress** (sliding grit) | Polished, scratched | Chutes, hoppers, screw flights, dozer blades, fan blades in dusty air | **Chromium carbide** (highest abrasion resistance), tungsten carbide for extreme |
| **Abrasion, high stress** (grit crushed against the surface) | Gouged and scratched | Crusher rolls, mill liners, ball mill scoops | Martensitic alloys with carbides, complex carbides |
| **Impact** | Battered, peened, deformed | Hammer mill hammers, crusher jaws, bucket lips, impact plates | **Austenitic manganese** (work-hardens from HRC 20 to 50+ under impact) |
| Abrasion + impact | Both | Bucket teeth, ripper shanks, dragline | Martensitic (medium), or manganese base with carbide top |
| **Metal-to-metal** (rolling/sliding, lubricated or not) | Scored, galled | Shafts, tractor rollers, idlers, trunnions, cranes wheels, gear teeth | **Martensitic build-up / semi-austenitic**, machinable grades; cobalt for hot |
| Heat + wear | Heat checking, scale | Hot shear blades, forging dies, furnace rolls | Cobalt (Stellite), Ni-based, tool-steel types |
| Corrosion + wear | Pitted | Valve seats, pump parts, agitators | Stainless (308/309/410), cobalt, Ni-Cr |
| Cavitation | Spongy pitting | Pump impellers, turbine runners | 309L/312 stainless, cobalt |

## Layers: build-up, buffer, hardfacing

```
   hardfacing (1-2 layers, HRC 40-65, may be non-machinable, may check-crack)
   ─────────────────────────────────────────────
   buffer / buttering (1 layer, tough, ductile; catches cracks, absorbs dilution)
   ─────────────────────────────────────────────
   build-up (as many layers as needed to restore dimension; machinable, HRC 25-40)
   ─────────────────────────────────────────────
   base metal (carbon steel, low alloy, manganese steel, cast iron...)
```

- **Build-up** electrodes/wires (e.g. Lincoln Wearshield BU / Lincore BU, Stoody Build-Up, Hardalloy 32) restore worn parts to size; tough, crack-free, unlimited layers, machinable. Base for any hardfacing thicker than 2 layers.
- **Buffer** on hard-to-weld bases: 7018 or 309L on carbon/low-alloy, a manganese-type buffer (Wearshield Mangjet, Stoody Nicromang) on **manganese steel**, nickel electrodes on cast iron.
- **Hardfacing** is the last **1-2 layers only** on chromium-carbide types; the third layer spalls off. Martensitic types can go 3-4 layers; manganese and cobalt types more.

## Alloy families and products

| Family | Deposit hardness | Layers max | Machinable | Cracking | Products (stick / open-arc or gas-shielded wire) |
|---|---|---|---|---|---|
| Build-up (low-alloy steel) | HRC 25-35 | unlimited | Yes | No | Wearshield BU / Lincore BU-G; Stoody Build-Up; Hardalloy 32 |
| Martensitic, medium hard | HRC 35-45 | 3-4 | With carbide, or anneal | Rare with preheat | Wearshield MM, Lincore 40-O; Stoody 105B/Super Build-Up; Hardalloy 40/48; McKay Hardalloy 118 |
| Martensitic, hard | HRC 50-60 | 2-3 | Grinding only | Possible; preheat | Wearshield 60, Lincore 55/60-O; Stoody 2110/Self-Hardening; Hardalloy 55/58 |
| **Austenitic manganese** | HRC 18-22 as welded, **50+ work-hardened** | unlimited | Difficult (work-hardens as you cut) | No, but the base overheats | Wearshield Mangjet, Lincore M; Stoody Nicromang; Hardalloy 8 |
| Austenitic Cr-Mn stainless-type (joining/buffer) | HRC 20-25 → 45 | unlimited | Yes | No | Wearshield 15CrMn; Stoody 2110 "Dynamang"; Hardalloy 8 |
| **Chromium carbide** | HRC 55-65 | **2** | No | **Check-cracks by design** (relief cracks every 1/2-2") | Wearshield ME / ABR / 70; Lincore 50/55/60-O; Stoody 100HC / 101HC / 121; Hardalloy 140 / Postalloy 2830 |
| Complex carbide (Cr + Nb/Mo/W/B) | HRC 60-70 | 1-2 | No | Check-cracks | Wearshield 70; Stoody 130/143; Postalloy 2836 |
| Tungsten carbide (composite rod / tube) | HRC 60+ matrix with WC particles ~HRC 90 | 1 | No | Check-cracks | Stoody Tube Borium, Lincoln Toughtung; oxy-fuel or low-amp stick to keep the carbides unmelted |
| Cobalt (Stellite 6/12/21) | HRC 38-48 hot-hard | 2-3 | Grinding | Preheat 500°F+ | Stoody 6, Stellite 6 rods (TIG/oxy/stick/PTA) |
| Ni-Cr-B-Si (Colmonoy) | HRC 40-60 | | | | Spray-and-fuse or TIG; pump sleeves, valve seats |

**Check-cracking**: chromium carbide deposits are so hard they cannot shrink without cracking, so they crack every inch or so across the bead; that is normal and prevents the whole layer from lifting. Cracks must **not** run into the base metal (buffer layer, preheat, do not overlap more than 2 layers). Parts loaded in bending or fatigue (shafts) never get chromium carbide.

**Manganese steel rules** (crusher jaws, hammers, frogs): the base metal embrittles above **500°F (260°C)**. Keep the part **cool to the touch 2-3" away**, short beads, skip sequence, water-cool between passes (quenching is allowed on manganese, the opposite of carbon steel), no preheat, use a manganese or Cr-Mn type electrode as the first layer. Check with a temp stick; never use a torch on it.

## Base metal and preheat

| Base metal | Preheat for build-up / hardfacing |
|---|---|
| Low-carbon steel (A36, 1020) | None to 100°F (dry) |
| Medium-carbon (1045 shafts, forgings) | 300-500°F (150-260°C), slow cool |
| Low-alloy (4140, 4340, 8620) | 500-600°F (260-315°C), buffer, slow cool; PWHT if machined afterwards |
| **Manganese steel (Hadfield, 11-14% Mn)** | **None; keep under 500°F** |
| Cast iron | Nickel buffer, 500°F+ or cold method (see [cast iron](/article/welding-cast-iron-and-repairs)) |
| Stainless | 309L/312 buffer if cracking; interpass ≤ 300°F |
| Unknown | Spark test; if it sparks like high-carbon or high-alloy, preheat 400°F and buffer |

Rule of thumb: carbon-equivalent based, same as [preheat article](/article/preheat-interpass-and-carbon-equivalent); a build-up layer on a preheated base then the hardfacing on the still-warm part.

## Bead pattern by service

| Pattern | Use |
|---|---|
| **Stringers, parallel to flow** | Coarse material sliding: material flows over the beads (chutes, flights) |
| **Stringers, across the flow** | Fine abrasive: the grooves fill with the material and it wears on itself (dozer blades, bucket sides) |
| **Waffle / cross-hatch** (1-2" squares) | Rock and mixed material in buckets and hoppers: the material packs the squares and protects the base; saves rod |
| Dots / studs | Loose rock on plates where you want a rough surface |
| Full coverage, overlapped 1/3 | Rollers, shafts, metal-to-metal, anything machined afterward |
| Edge beads only | Cutting edges: hard on the wear side, soft steel behind so it self-sharpens |

## Settings

| Consumable | Diameter | Polarity | Amps / settings |
|---|---|---|---|
| Stick build-up and martensitic (Wearshield BU, MM, 60; Hardalloy 32/40/55) | 1/8" | DCEP or AC | 110-150 A |
| | 5/32" | | 140-200 A |
| | 3/16" | | 180-260 A |
| Stick chromium carbide (Wearshield ME/70; Stoody 100HC) | 5/32" | DCEP or AC | 130-190 A (long arc, keep dilution low) |
| | 3/16" | | 170-250 A |
| Stick manganese (Mangjet, Nicromang) | 5/32" | DCEP or AC | 130-180 A, short beads |
| Open-arc hardfacing wire (Lincore 50-O/55-O/60-O, Stoody 100HC-O) | 1/16" | **DCEP** | 200-300 A, 24-30 V, stickout **1-1.5"** |
| | 7/64" | DCEP | 300-450 A, 26-32 V, stickout 1.5-2.5" |
| Build-up wire Lincore BU-G / metal-cored | .045 | DCEP, 90/10 or 100% CO2 | 180-280 A, 24-30 V |
| Tungsten carbide tube rod | 3/16-1/4" | oxy-acetylene (carburising flame) or DCEN low amps | Keep the carbides from melting: sweat the matrix, do not stir |
| Cobalt (Stellite 6) | 1/8" stick / 3/32" TIG | DCEP / DCEN | 90-140 A / 100-150 A, preheat 500°F |

Open-arc self-shielded hardfacing wires run long stickout and high voltage on purpose: more deposit, less dilution. Deposit efficiency is 60-70%. Dilution from the base metal reduces hardness in the first layer; the **second layer is the hard one**.

## Procedure

1. Identify the base metal (spark test, drawings, magnet); identify the wear type from the surface.
2. Remove the old hardfacing if it is cracked, spalled or a third layer would result: grind, gouge (carbon-arc works on carbide overlay; grind the carbon off), or machine.
3. Clean to bright metal; preheat per the table.
4. Build up to within 1/8-3/16" of final size with build-up alloy; peen martensitic layers if the part is restrained.
5. Buffer if needed (alloy base, manganese base, cast iron).
6. Hardface: **1-2 layers**, pattern per service, keep the part within the interpass window (or cool, on manganese).
7. Slow-cool carbon/alloy steel parts (blanket, sand); air- or water-cool manganese.
8. Check: look for cracks running into the base (bad) vs check-cracks across the bead (normal on carbide), measure hardness with a file (a new file skates on HRC 60), verify dimensions, grind if it must be smooth.

## Worked example: bucket lip

1/2" A36 bucket lip, worn back 1/4", hauling sand and gravel (abrasion with some impact). Preheat 200°F (dry). Build-up with 5/32" Wearshield BU at 170 A to size; then one layer of Wearshield ME (chromium carbide) 3/16" at 200 A in **stringers across the flow** on the top face and a second layer on the cutting edge only. Expect check cracks every inch. Cool under a blanket. Life is typically 3-5× bare A36; re-face when the carbide is gone, never let it wear into the build-up and the parent metal.

## Common mistakes

- Three or four layers of chromium carbide: the top spalls in slabs and takes the second layer with it.
- Hardfacing a 4140 shaft with no preheat and no buffer: cracks under the overlay and a broken shaft.
- Torch-preheating manganese steel jaws: the whole casting cracks on the first blow.
- Hardfacing without build-up: 1/2" of carbide is $$$ and cracks; build up cheap, face hard.
- Using 7018 as "hardfacing": it is softer than the part.
- Grinding carbide overlay with a hard wheel: use a soft-bond wheel or a carbide-rated flap disc; it barely touches HRC 60.

## Related

- [Welding cast iron and repairs](/article/welding-cast-iron-and-repairs)
- [Preheat, interpass and carbon equivalent](/article/preheat-interpass-and-carbon-equivalent)
- [Stick setup](/article/smaw-stick-setup), [self-shielded flux-core](/article/fcaw-self-shielded-setup)
- [Metal identification and spark test](/article/metal-identification-and-spark-test)
- [Hardness conversion](/article/hardness-conversion)
