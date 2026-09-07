---
title: "Preheat, Interpass Temperature and Carbon Equivalent: CE and Pcm Formulas, AWS D1.1 Minimum Preheat Table by Steel and Thickness, Temp Sticks, Hydrogen Control and Post-Heat"
slug: preheat-interpass-and-carbon-equivalent
category: welding
kind: chart
tags: [preheat, preheat temperature, interpass temperature, carbon equivalent, CE formula, Pcm, hydrogen cracking, cold cracking, delayed cracking, underbead crack, temp stick, tempilstik, temperature crayon, post heat, hydrogen bakeout, D1.1 preheat table, A36 preheat, A514 preheat, 4140 preheat, thick plate welding, cold weather welding]
source: "AWS D1.1 Structural Welding Code, Table 5.8 (minimum preheat and interpass, prequalified) as reproduced in the Lincoln Electric Stick Electrode Welding Guide pp. 35-36; IIW carbon-equivalent formula; AWS D1.1 Annex H (Pcm and hydrogen-control method); Tempil temperature-indicator data."
summary: "Why steel cracks hours after welding and the three things that stop it (preheat, low-hydrogen consumables, controlled cooling): the carbon equivalent formulas with a lookup table, the code minimum preheat table by steel group and thickness, how to measure it with a temp stick, maximum interpass, and post-heat for the steels that need it."
---

## What preheat is for

Hydrogen cracking (cold cracking, delayed cracking, underbead cracking) needs three things at once: **hydrogen** in the weld (moisture in the flux, oil, rust, paint), a **hard microstructure** (martensite, from fast cooling of a steel with enough carbon and alloy), and **stress** (restraint, thickness, residual stress). It shows up **hours to days** after welding, in the heat-affected zone or the weld toe, and is the reason code welds sit 48 hours before final inspection on Q&T steel.

Preheat attacks two of the three: it slows the cooling rate (softer HAZ) and drives hydrogen out while the steel is still hot and ductile. It also dries the joint and reduces distortion on thick sections.

## Carbon equivalent

**IIW formula (for steels with C > 0.12%)**

```
CE = C + Mn/6 + (Cr + Mo + V)/5 + (Ni + Cu)/15
```

**Pcm (Ito-Bessyo, for low-carbon microalloyed steels, C ≤ 0.12%)**

```
Pcm = C + Si/30 + (Mn + Cu + Cr)/20 + Ni/60 + Mo/15 + V/10 + 5B
```

Use the mill certificate; if there is none, use the maximum from the spec.

| CE (IIW) | Weldability | Typical action |
|---|---|---|
| **< 0.35** | Excellent | No preheat below 1" except to remove moisture and above freezing; any electrode |
| 0.35-0.45 | Good | Low-hydrogen consumables; preheat 100-300°F (40-150°C) as thickness and restraint rise |
| 0.45-0.55 | Fair | Preheat 300-500°F (150-260°C), low-hydrogen, interpass control, slow cool |
| > 0.55 | Poor | Preheat 400-600°F+, low-hydrogen, post-heat or PWHT, consider a Ni-based filler and a buttered joint |

Typical values: A36 ≈ 0.25-0.40 (often quoted as ≤ 0.40 max); A572 Gr 50 ≈ 0.40-0.45; A514 ≈ 0.55-0.65 (but designed to be welded with preheat/heat-input control); 1045 ≈ 0.60; 4140 ≈ 0.80 (preheat 500-600°F, PWHT); 4340 ≈ 0.95; cast iron off the chart (see [cast iron repairs](/article/welding-cast-iron-and-repairs)).

## Minimum preheat and interpass (AWS D1.1 Table 5.8, prequalified, stick electrodes)

Thickness T is the thickest part at the point of welding. Temperatures are minimums at the joint, measured **3" (75 mm) from the joint** in all directions on the thickest part, held through the whole weld (interpass never falls below it).

| T (thickest part) | Col. 1: A36 and similar (A53 B, A106 B, A500, A501, A516, A570, A709 Gr 36 ≤ 3/4") with **non-low-hydrogen** electrodes | Col. 2: same steels plus A572 Gr 42/50/55, A588, A529, A537, A633 A-D, A710 Cl 1 etc. with **low-hydrogen** electrodes | Col. 3: A572 Gr 60/65, A633 E, API 5L X52, A913 Gr 60/65, A709 Gr 70W, A852, API 2W/2Y Gr 60, **low-hydrogen** | Col. 4: A710 Gr A (all classes), A913 Gr 50/60/65 with **H8** low-hydrogen electrodes |
|---|---|---|---|---|
| 1/8" through 3/4" (3-20 mm) | 32°F (0°C) | 32°F (0°C) | 50°F (10°C) | 32°F (0°C) |
| Over 3/4" through 1-1/2" (20-38 mm) | 150°F (65°C) | 50°F (10°C) | 150°F (65°C) | 32°F (0°C) |
| Over 1-1/2" through 2-1/2" (38-65 mm) | 225°F (110°C) | 150°F (65°C) | 225°F (110°C) | 32°F (0°C) |
| Over 2-1/2" (> 65 mm) | 300°F (150°C) | 225°F (110°C) | 300°F (150°C) | 32°F (0°C) |

Footnote: "32°F" means the steel must be at or above freezing; when the base metal is below 32°F, preheat to at least 70°F (20°C) and hold it during welding. Column 1 only applies to the listed mild steels; **A572 and the higher-strength steels are never welded with non-low-hydrogen rods** under the code.

Quenched-and-tempered A514/A517: D1.1 gives its own row (about 50°F ≤ 3/4", 125°F to 1-1/2", 175°F to 2-1/2", 225°F above) **with a maximum** preheat/interpass and a maximum heat input from the mill; over-heating A514 destroys its properties. Check the steel producer's sheet.

## Interpass maximum

- Carbon and low-alloy structural: no code maximum under D1.1 for ordinary steels; practical **≤ 500°F (260°C)** to keep toughness. Q&T steels: **max 400°F (200°C)** typically, per producer.
- Stainless austenitic (304/316): **max 300°F (150°C)**, 350°F at most, to limit sensitisation and distortion.
- Aluminium: max 250°F (120°C); 5xxx alloys **keep under 150°F** after the first passes if service is warm.
- Duplex stainless: max 300°F (150°C) strictly.
- Nickel alloys: max 350°F (175°C).

## Measuring it

- **Temperature-indicating crayons (Tempilstik and similar)**: melt at a rated temperature (±1%). Stroke the plate **near the joint, 3" out**: a mark that melts and goes liquid means the plate is **above** that temperature; a chalky mark means below. Use two sticks to bracket (e.g. 200°F melts, 250°F does not → 200-250°F). Do not mark inside the groove; residue contaminates the weld.
- **Contact pyrometer / thermocouple probe**: best for interpass; hold it on the plate until it stabilises.
- **Infrared gun**: fast but reads low on shiny steel and reads the scale not the metal; set emissivity 0.9-0.95 on a black oxide surface, or paint a spot flat black. Use it only for checking uniformity, not for the code reading.
- Preheat **through the thickness**: with a torch, heat from the side opposite the weld where possible and wait 1 minute per inch of thickness after the surface reaches temperature before checking (heat soaks in). Electric resistance blankets or induction for anything thick or long.
- Check **before every pass** on preheat-required joints; heavy sections lose heat fast when you stop to chip.

## Hydrogen control

1. Low-hydrogen electrodes from a **rod oven** (250°F ± 25°F for 7018; H4R rods allow 9 hours out); rebake once at 700-800°F for 1 hour. Details in the [electrode chart](/article/smaw-electrode-chart).
2. Solid MIG wire and metal-core wire are low-hydrogen by nature (keep dry, no oil). Flux-core gas-shielded E71T-1 with H8 designator for code work; self-shielded general-purpose wires are not low-hydrogen.
3. Clean the joint: no oil, water, paint, galvanising, cutting fluid; grind rust. Moisture from a cold plate brought into a warm shop condenses; preheat drives it off.
4. No welding on wet steel, in rain, or below 0°F (−18°C) per D1.1 without shelter.
5. **Post-heat (hydrogen bake-out)** for CE > 0.5, thick or restrained Q&T and alloy steels: immediately after welding, before cooling, hold at **400-500°F (200-260°C) for 1 hour per inch of thickness (2 h minimum)**, then cool slowly under a blanket. Different from PWHT (stress relief at 1100-1250°F) which is a separate engineering requirement.
6. Slow cooling: insulating blanket (ceramic fibre) over thick welds; never a fan or a draught on a preheated joint.

## Cold-weather rule set

- Below 32°F: preheat everything to 70°F minimum and keep it there.
- Windbreaks for gas-shielded processes above 5 mph.
- Rods and wire stored inside; an open 7018 can at 10°F is a hydrogen sponge.
- Extra preheat 50-100°F on top of the table for thick restrained joints in the cold.

## Worked example

Welding a 1-1/4" A572 Gr 50 baseplate to a 1" column with 7018: column 2 (low-hydrogen), T = 1-1/4" → **50°F minimum preheat**. It is 20°F in the yard, so preheat to 70°F minimum (in practice 150°F), check 3" from the joint with a 150°F stick, weld, and keep the interpass at or above 150°F and below 500°F. With 6010 root passes instead, column 1 would demand 150°F, and the code would not allow 6010 on A572 anyway.

## Related

- [Stick electrode chart and storage](/article/smaw-electrode-chart)
- [Welding cast iron and repairs](/article/welding-cast-iron-and-repairs)
- [Weld defects and inspection](/article/weld-defects-and-inspection)
- [Distortion control](/article/distortion-control)
- [Steel grades and heat colours](/article/steel-grades-and-heat-colours)
- [Oxy-fuel heating with a rosebud](/article/oxy-fuel-heating-rosebud)
