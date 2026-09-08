---
title: "TIG Welding (GTAW) Setup: Polarity, Tungsten Type and Size, Grinding, Cups and Gas Lens, Argon Flow, AC Balance and Frequency, Pulse, Pedal, Pre- and Post-Flow"
slug: gtaw-tig-setup
category: welding
kind: procedure
manufacturer: "Miller / Lincoln / CK Worldwide (generic)"
model_numbers: ["Dynasty 210", "Dynasty 280", "Syncrowave 210", "Diversion 180", "Aspect 375", "Square Wave TIG 200", "Precision TIG 225", "CK17", "CK26", "WP-17", "WP-26"]
tags: [TIG welding, GTAW setup, tungsten, 2% lanthanated, thoriated, ceriated, tungsten diameter amps, tungsten grinding, cup size, gas lens, argon flow, AC balance, AC frequency, DCEN, high frequency, lift arc, post flow, foot pedal, TIG torch, aluminum TIG]
source: "Miller TIG handbook and weld-setting calculator; CK Worldwide tungsten guide; AWS C5.5 Recommended Practices for GTAW; welders-supply.com TIG settings chart."
summary: "How to set up a TIG machine and torch from the cylinder to the arc: polarity by material, tungsten selection with the diameter-vs-amperage table, how to grind it, cup and gas-lens sizes with matching flow rates, AC balance and frequency for aluminium, pulse basics, arc starting methods, pedal use, pre-flow and post-flow, and torch technique."
---

> TIG is a **CC** process: you set the maximum amperage and control the actual amperage with the foot pedal or torch switch. The tungsten does not melt; filler is added by hand. Everything must be clean: the plate, the filler, the tungsten and the gas path.

## 1. Polarity and current type

![DCEN for steel and stainless, AC for aluminium](/img/welding/polarity.svg)

*DCEN for steel and stainless, AC for aluminium*

| Material | Current | Why |
|---|---|---|
| Mild steel, stainless, chrome-moly, copper, titanium, nickel | **DCEN (DC−, straight)**: torch on −, ground on + | 2/3 of the heat goes into the work; tungsten stays cool and pointed |
| Aluminium, magnesium | **AC** (with high-frequency or square-wave) | The EP half-cycle blasts the oxide off; the EN half-cycle does the melting |
| Aluminium on a DC-only machine | DCEN with 100% **helium** (rare, thick plate) or use MIG | |
| DCEP on TIG | never for welding; it melts the tungsten | |

## 2. Tungsten

**Types**

![Tungsten grind, stickout, torch angle and filler angle](/img/welding/tig-torch-setup.svg)

*Tungsten grind, stickout, torch angle and filler angle*

| Tungsten | Colour band | Use |
|---|---|---|
| **2% lanthanated (EWLa-2)** | blue | The all-rounder: DC and AC, inverters and transformers, long life, no radioactivity. **Default choice.** |
| 2% ceriated (EWCe-2) | grey (orange in older codes) | Low-amperage DC, thin stainless and steel, easy starts |
| 2% thoriated (EWTh-2) | red | Classic DC steel/stainless tungsten; slightly radioactive dust when grinding (use extraction); not for AC on inverters (splits) |
| 1.5% lanthanated | gold | Same as 2% La for most uses |
| Zirconiated (EWZr) | white/brown | AC on transformer machines, balls nicely |
| Pure (EWP) | green | AC on old transformer machines only; balls; never on DC or inverters |
| Rare-earth "tri-mix" (E3, LaYMo) | purple | Good all-rounder on inverters |

**Diameter vs amperage (approximate, argon)**

| Tungsten | DCEN (steel/stainless) | AC on inverter (aluminium) | AC on transformer (balled) |
|---|---|---|---|
| 0.040" (1.0 mm) | 5-40 A | 10-30 A | 10-25 A |
| **1/16" (1.6 mm)** | **15-90 A** | 20-80 A | 20-60 A |
| **3/32" (2.4 mm)** | **60-200 A** | 60-160 A | 50-140 A |
| **1/8" (3.2 mm)** | **150-350 A** | 120-250 A | 100-220 A |
| 5/32" (4.0 mm) | 250-450 A | 200-350 A | 180-300 A |
| 3/16" (4.8 mm) | 400-600 A | 300-450 A | 250-400 A |

Rule of thumb: 1/16" up to about 90 A, 3/32" for 90-200 A, 1/8" above that. Undersized tungsten melts and balls; oversized wanders and starts poorly.

**Grinding**

- Grind **lengthwise** on a dedicated fine wheel or a tungsten grinder (never a wheel used for steel; contamination). Radial grind marks make the arc spiral.
- **DC**: sharp point, taper length 2-2.5 × diameter (about 30° included angle). A tiny flat (0.010-0.020") on the tip at higher amps stops the point melting off.
- **AC on an inverter**: same point with a small flat, or a truncated cone; do not ball.
- **AC on a transformer (Syncrowave 250/350 class)**: grind a point, then form a hemispherical **ball** ≈ 1-1.5× diameter by running DCEP briefly on a scrap or just starting on AC.
- Stickout past the cup: **1× cup ID** with a standard collet body, up to 2× or more with a **gas lens**. Set the tungsten so you can see the puddle.
- If you dip it in the puddle or touch the filler to it: stop, break off or regrind. A contaminated tungsten throws tungsten into the weld and the arc goes purple and erratic.

## 3. Cups, collet bodies and gas flow

Cup number = orifice diameter in **1/16"**: #4 = 1/4", #5 = 5/16", #6 = 3/8", #7 = 7/16", #8 = 1/2", #10 = 5/8", #12 = 3/4".

| Setup | Cup | Argon flow | Notes |
|---|---|---|---|
| Standard collet body, thin work, tight corners | #4-#5 | 10-12 cfh | |
| Standard collet body, general | #6-#7 | 12-18 cfh | The everyday setup |
| Standard collet body, high amps / aluminium | #8 | 15-20 cfh | |
| **Gas lens** (screen inside the collet body) | #8-#12 | 15-25 cfh | Laminar flow: longer stickout, better coverage, needed for stainless, titanium and any joint where you must reach in |
| Large gas lens / titanium trailing shield | #12-#16, trailing cup | 25-40 cfh | |

Too much flow is as bad as too little: above about 25-30 cfh through a #7 cup the gas goes turbulent and pulls air in. Use a **flowmeter** (ball-in-tube), not a pressure-gauge regulator, for TIG. **Pre-flow** 0.2-0.5 s; **post-flow** long enough to shield the tungsten and the crater until they are dark: about **1 second per 10 amps** (150 A → 15 s), more for stainless and titanium.

Back-purge stainless and titanium roots: see [gas selection and flow](/article/gas-selection-and-flow).

## 4. Torch

| Torch | Cooling | Rated | Use |
|---|---|---|---|
| #17 (WP-17) | air | 150 A DC / 115 A AC | Light, everyday steel and stainless |
| #26 (WP-26) | air | 200 A DC / 160 A AC | Heavier steel |
| #9 | air | 125 A DC | Small, tight spots |
| #18, #20 | water | 350 A / 250 A | Aluminium, production, any long run above 150 A |

Air-cooled torches get too hot to hold above about 150 A for more than a couple of minutes: that is what water coolers are for. Flexible heads and short back caps get you into corners.

## 5. Machine settings

| Control | Setting |
|---|---|
| Process | TIG (not stick); HF start or lift-arc |
| Polarity | DCEN for steel/stainless; AC for aluminium |
| Amperage (max) | From the [material table](/article/gtaw-settings-by-material); roughly **1 A per 0.001"** of steel thickness (1/8" → 125 A); aluminium **+20-30%**; stainless **−10-20%** |
| Pedal / remote | On; set max amps so full pedal is a little more than you need |
| **AC balance** | **65-75% EN** on inverters (more EN = more penetration and less tungsten heating; less EN = more cleaning). Start at 70% EN; use 60-65% on dirty or cast aluminium |
| **AC frequency** | **100-150 Hz** for most aluminium fillets and thin work (tight, focused arc); 60-80 Hz for wide beads on thick plate; transformer machines are fixed at 60 Hz |
| AC amplitude / independent EN-EP amps (advanced) | Leave at default until comfortable |
| Pulse (DC) | Off to learn. Typical thin stainless: 1-2 pulses/s, peak = set amps, background 30-40%, 40-50% peak time. High-speed pulse (100+ Hz) stiffens the arc on thin steel |
| Start amps / upslope | Start 10-20 A, upslope 0.5-1 s for aluminium to avoid tungsten spitting |
| Downslope / crater | 1-3 s downslope on aluminium and stainless to avoid crater cracks (or pedal off slowly) |
| Pre-flow / post-flow | 0.3 s / 1 s per 10 A |
| Spot/weld timer | Off |

**Arc starting**: **HF start** (high frequency jumps the gap, no touching) is best; **lift-arc** (touch, hold, lift) is for machines without HF or near electronics; **scratch start** on stick-only machines with a valve torch contaminates the tungsten and the plate and is a last resort.

## 6. Filler

Match the base metal: ER70S-2 for steel, ER308L/316L/309L for stainless, ER4043/5356 for aluminium, ERCuSi-A for copper/braze-welding. Diameter ≈ tungsten diameter, one size smaller on thin sheet. Keep it clean (wipe with acetone), cut off the oxidised end, and keep the hot end **inside the gas shield** between dabs.

## 7. Technique

1. Clean: grind steel bright; stainless brush (dedicated) and acetone; aluminium: degrease, then stainless-brush to break the oxide, weld within an hour.
2. Torch angle **10-15° push**, tungsten 1/8" from the plate (arc length ≈ tungsten diameter). Filler enters at 15-20° low from the front, into the leading edge of the puddle, not into the arc.
3. Form the puddle, dab, move, dab: "walk" the puddle at a steady rhythm. Let the puddle size (about 2× tungsten diameter on steel) set your travel.
4. Aluminium: wait for the shiny puddle to form (the oxide clears), dab generously and often, expect to add power as the part heats and then back off the pedal.
5. Finish: ease off the pedal (or downslope) while adding a last dab, hold the torch over the crater through post-flow.

## 8. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Arc wanders, purple/blue arc, black weld | Contaminated tungsten, wrong type, poor grind | Regrind, lanthanated, lengthwise grind |
| Tungsten balls or melts on DC | Amps too high for the size, DCEP by mistake | Larger tungsten, check polarity |
| Tungsten spits on AC start | Too much EP (balance), start amps too high, cheap pure tungsten on inverter | 70-75% EN, lower start amps, lanthanated |
| Grey/black oxidised bead | Gas: low flow, post-flow too short, leak, draft, cup too small, stickout too long | Check flow, 1 s/10 A post-flow, gas lens |
| Porosity | Dirty base/filler, gas turbulence (too much flow), leaking torch hose, moisture | Clean, 15-20 cfh, check hoses |
| Sugaring (crusty root) on stainless | No back purge | Purge |
| Cannot start the arc | HF off, tungsten too far, ground poor, wet plate | HF on, 1/8" gap, clean ground |
| Aluminium will not wet / dull puddle | Oxide not cleaned, balance too far EN, dirty filler | Brush, 65-70% EN, clean rod |
| Grey smoky deposit on the cup | Nozzle too small or too close on aluminium | Larger cup, more flow |

## Related

- [TIG settings by material: steel, stainless, aluminium, copper, titanium](/article/gtaw-settings-by-material)
- [Shielding gas selection and flow rates](/article/gas-selection-and-flow)
- [Welding aluminium](/article/welding-aluminium) and [welding stainless](/article/welding-stainless-and-dissimilar)
- [Machine setup, duty cycle and cables](/article/machine-setup-and-duty-cycle)
