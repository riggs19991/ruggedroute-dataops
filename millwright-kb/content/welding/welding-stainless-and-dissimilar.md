---
title: "Welding Stainless Steel and Dissimilar Metals: 308L/309L/316L Filler Selection, Sensitisation and Carbide Precipitation, Heat Input, Purging, Cleaning, Duplex and Stainless-to-Carbon Steel"
slug: welding-stainless-and-dissimilar
category: welding
kind: procedure
tags: [stainless steel welding, 308L, 309L, 316L, 347, filler selection stainless, dissimilar metal welding, stainless to carbon steel, sensitization, carbide precipitation, ferrite number, back purge, sugaring, heat tint, passivation, pickling, duplex stainless, 410 stainless, 17-4, interpass stainless, stainless MIG settings, stainless stick]
source: "AWS A5.4 / A5.9 (stainless electrodes and wires); AWS D1.6 Structural Welding Code, Stainless Steel; Lincoln Electric stainless steel welding guide; ESAB and Sandvik filler selection tables; Nickel Institute and Outokumpu welding handbooks."
summary: "Which filler for which stainless grade and for stainless-to-carbon-steel joints, why stainless needs low heat input and a maximum interpass, how to purge and judge the colour, cleaning and contamination rules, and the settings differences from carbon steel for stick, MIG, flux-core and TIG."
---

## Families you will meet

| Family | Grades | Magnetic | Notes |
|---|---|---|---|
| **Austenitic (300 series)** | 304/304L, 316/316L, 321, 347, 309, 310 | No (slightly after cold work) | 90% of stainless welding; not hardenable; expands 50% more than carbon steel and conducts heat 40% as well → distortion |
| Ferritic (400 series, low carbon) | 409, 430 | Yes | Exhausts, trim; grain growth in HAZ, keep heat low; filler 409/430 or 308L/309L |
| Martensitic | 410, 420, 440 | Yes | Hardens on cooling: **preheat 400-600°F**, matching or 309L filler, temper after |
| Precipitation-hardening | 17-4PH, 15-5PH | Yes | Weld with 17-4 filler in the solution-annealed condition, re-age after |
| Duplex | 2205, 2507 | Yes | Half austenite, half ferrite; filler 2209; **strict heat-input window and interpass ≤ 300°F** |

## Filler selection

| Base metal | Stick (AWS A5.4) | MIG/TIG wire (A5.9) | FCAW |
|---|---|---|---|
| **304, 304L, 321, 347 (general)** | **E308L-16** | **ER308L**, ER308LSi (MIG, wets better) | E308LT1-1/-4 |
| 321, 347 (stabilised, high-temp) | E347-16 | ER347 | E347T1 |
| **316, 316L** | **E316L-16** | **ER316L**, ER316LSi | E316LT1-1/-4 |
| 309, 310 | E309L / E310 | ER309L / ER310 | E309LT1 |
| **Stainless to carbon or low-alloy steel** | **E309L-16** | **ER309L**, ER309LSi | E309LT1-1/-4 |
| Stainless to stainless of unknown grade | E309L | ER309L | |
| 410 (martensitic) | E410-16 (preheat) or E309L (soft, no PWHT) | ER410 / ER309L | |
| 430 (ferritic) | E430 or E308L/E309L | ER430 / ER309L | |
| Duplex 2205 | E2209-16 | ER2209 | E2209T1 |
| Buffer layer / dissimilar high-restraint | ENiCrFe-3 (Inconel 182) | ERNiCr-3 (Inconel 82) | |
| Nickel to stainless, cryogenic, or clad plate | ENiCrMo-3 | ERNiCrMo-3 (625) | |

Rules: **"L" (≤ 0.03% C) always** unless the drawing says otherwise; 309L for anything joined to carbon steel; ER308LSi/316LSi on MIG (silicon makes the puddle wet out, but do not use Si grades where the weld will be nitric-acid service). Stick electrode suffix -16 (all position, AC/DC), -15 (DC+ only, lime, tougher), -17 (spray-like, smooth, flat/horizontal).

## Why heat input matters: sensitisation

Between roughly **800 and 1500°F (425-815°C)** chromium in austenitic stainless combines with carbon to form chromium carbides at the grain boundaries, stripping chromium from the metal next to them: the weld looks fine and then rusts or cracks in a line beside the weld (weld decay). Defences:

1. **Low-carbon grades (L)** and low-carbon filler.
2. **Low heat input**: stringer beads, smaller electrodes, faster travel, no wide weaves.
3. **Interpass ≤ 300°F (150°C)**: check with a temp stick; let it cool, use chill bars.
4. Stabilised grades (321, 347) for high-temperature service.
5. Solution annealing (1900-2050°F and quench) if the fabrication allows; rarely available in the field.

**Hot cracking** in fully austenitic welds is avoided by filler with a few percent ferrite (308L and 316L have FN 5-10; 310 and 330 have none and crack easily on restrained joints), by convex beads and by filling craters.

## Settings compared with carbon steel

| Process | Change from carbon steel |
|---|---|
| Stick | Same amps or **5-10% lower** for the diameter (see [electrode chart](/article/smaw-electrode-chart)); short arc; the slag is glassy and self-lifting; DCEP or AC on -16 |
| MIG short-circuit | **Tri-mix (90 He / 7.5 Ar / 2.5 CO2)** for flat wet beads, or 98/2 Ar-CO2; .035 at 60-140 A, 17-21 V; never straight CO2 or C25 (carbon pick-up, ugly oxide) |
| MIG spray | 98/2 Ar-O2 or Ar-CO2; .035 at 180-220 A, 24-27 V; **pulse** is the best all-round mode on stainless |
| FCAW | E308LT1-1 with 100% CO2 or E308LT1-4 with 75/25; .045 at 150-220 A, 24-28 V; light slag, all position |
| TIG | DCEN, **10-20% less amps** than steel, gas lens, argon 15-20 cfh, long post-flow, back-purge | See [TIG settings](/article/gtaw-settings-by-material) |

Stainless does not conduct heat away: the puddle forms fast and stays. Move faster than you would on carbon steel and expect more distortion: tack every 2-3", clamp, chill bars, back-step.

## Purging and colour

Any open root (pipe, tanks, box sections) exposed to air while hot oxidises into a black crust ("sugaring") that has no corrosion resistance and cracks. Purge with argon (procedure in [gas selection and flow](/article/gas-selection-and-flow)) until oxygen < 0.1% and keep the purge on until the root is below about 800°F.

![Heat tint colours from silver to black and what each means](/img/welding/heat-tint-scale.svg)

*Heat tint colours from silver to black and what each means*

| Heat tint colour on the weld and HAZ | Meaning |
|---|---|
| Silver, pale straw | Correct shielding; acceptable for all services |
| Gold, light blue | Thin oxide; acceptable for non-corrosive service; pickle for corrosive |
| Dark blue, purple | Thicker oxide; poor shielding or too hot; pickle or grind on corrosive service |
| Grey, black, crusty | Oxidised, no protection; cut out on the root, grind and re-weld on the cap |

Post-weld cleaning restores the passive layer: **pickling paste** (nitric-hydrofluoric, follow the SDS, neutralise and rinse), electrochemical weld cleaning, or mechanical (dedicated stainless flap disc, then passivation with citric or nitric acid). Wire brushing alone leaves oxide and rubs iron into the surface if the brush was ever used on carbon steel.

## Contamination rules

- **Dedicated tools**: stainless wire brushes, grinding discs, files and clamps marked and kept apart. Carbon steel grinding dust on stainless rusts ("rust spots") within days.
- No carbon steel spatter, no carbon-steel table without a stainless sheet or wood under the part, no steel hammers on the surface.
- Degrease with acetone or alcohol; no chlorinated solvents (they leave chlorides, and chlorides cause stress-corrosion cracking); no marker pens with chloride content on chemical-service parts.
- Temperature sticks: use chloride-free ones on stainless.
- Store stainless filler in its own tube; a 308L rod that has been on a carbon steel bench picks up iron.

## Stainless to carbon steel

Use **309L**: its extra chromium and nickel absorb dilution from the carbon steel side without forming brittle martensite. Steps: settings for the stainless side, arc favouring the carbon steel side (it needs more heat and it melts faster into the puddle, so keep the dilution low with a shallow puddle), preheat per the carbon steel if it is thick or alloyed (7018 rules), interpass under 300°F for the stainless side. For clad plate: carbon steel side with 7018, back-gouge, one 309L buffer layer, then 308L/316L to match the cladding.

For high-restraint dissimilar joints in service above 600°F (thermal cycling), and for joints to alloy steel like 4140 or to nickel alloys, use a nickel-based filler (ERNiCr-3 / ENiCrFe-3): its expansion sits between the two and it tolerates dilution.

## Duplex quick rules

Heat input window **0.5-2.5 kJ/mm (13-63 kJ/in)**, interpass **≤ 300°F (150°C)**, filler **2209** (over-alloyed with nickel to keep the austenite balance), no preheat, argon (or Ar + 2% N2) shielding and purge, no autogenous welds. Too cold gives too much ferrite (brittle); too hot forms intermetallics (brittle and corrodes). Follow the WPS exactly.

## Common mistakes

- 308L on stainless-to-carbon joints: cracks along the fusion line months later. Use 309L.
- Weaving 1/8" 308L in one wide cap: sensitised HAZ and a rusty line by summer.
- C25 gas on stainless MIG "because it was on the machine": carbon pick-up and a dull oxide skin.
- Grinding with the shop's carbon steel discs: rust spots on a stainless food tank.
- Skipping the purge on a pipe root "just this once": the root sugars and the seam leaks after the first cleaning cycle.
- Leaving heat tint on chemical-service welds: pitting starts in the blue band.

## Related

- [Stick electrode chart](/article/smaw-electrode-chart), [AWS classification decoder](/article/aws-electrode-classification)
- [TIG settings by material](/article/gtaw-settings-by-material)
- [Gas selection and flow (purging)](/article/gas-selection-and-flow)
- [Weld defects and inspection](/article/weld-defects-and-inspection)
- [Metal identification and spark test](/article/metal-identification-and-spark-test)
