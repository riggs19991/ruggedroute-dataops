---
title: "Shielding Gas Selection and Flow Rates for MIG, Flux-Core, TIG and Plasma, with Cylinder Sizes, Regulators vs Flowmeters and Purging"
slug: gas-selection-and-flow
category: welding
kind: chart
tags: [shielding gas, argon, CO2, C25, 75/25, 90/10, 98/2, tri-mix, helium, flow rate cfh, flowmeter, regulator, cylinder size, gas cost, purge, back purge, nitrogen, plasma gas, gas leak]
source: "Praxair/Linde and Airgas shielding gas selection guides; AWS A5.32 (shielding gases); Miller and Lincoln gas guidance; CGA cylinder standards."
summary: "One table per process for which gas to buy and what flow to set, why each mix behaves the way it does, cylinder sizes and how long they last, regulator versus flowmeter, leak checks, and purging stainless and titanium roots."
---

## Gas by process

| Process | Material | Gas | Flow | Notes |
|---|---|---|---|---|
| MIG short-circuit | Mild steel | **75% Ar / 25% CO2 (C25)** | 20-25 cfh (10-12 L/min) | Cleanest general-purpose; C10-C15 also common in shops |
| MIG short-circuit | Mild steel, budget / deep penetration | 100% CO2 | 20-30 cfh | More spatter, colder look, cheaper, globular above ~200 A |
| MIG spray / pulse | Mild steel | **90/10 Ar-CO2**, 92/8, 95/5, 98/2 Ar-O2 | 35-45 cfh (17-21 L/min) | Needs ≥ 80% Ar; 98/2 gives the lowest transition current, 90/10 more penetration |
| MIG | Stainless short-circuit | Tri-mix 90 He / 7.5 Ar / 2.5 CO2 | 25-35 cfh | Flat wet bead; expensive |
| MIG | Stainless spray/pulse | Ar / 1-2% O2 or 98/2 Ar-CO2 | 30-40 cfh | Keep CO2 ≤ 2-3% to protect corrosion resistance |
| MIG | Aluminium | **100% Ar**; Ar/He 75/25 or 50/50 above 3/8" | 30-40 cfh (14-19 L/min) | Helium adds heat for thick plate |
| MIG | Copper, silicon bronze | 100% Ar (He mix for thick copper) | 30-40 | |
| FCAW-G | Steel E71T-1C | **100% CO2** | **40-50 cfh** | Wire classified "C" |
| FCAW-G | Steel E71T-1M | 75/25 Ar-CO2 | 35-45 cfh | Wire classified "M"; lower voltage by 1-2 V vs CO2 |
| FCAW-S | Any | none | - | Self-shielded |
| Metal-cored | Steel | 90/10 or 95/5 Ar-CO2 | 35-45 | |
| TIG | Steel, stainless, aluminium, copper, titanium | **100% Ar** | 10-20 cfh standard cup; 15-25 gas lens | Argon-helium 75/25 for aluminium/copper over 1/4" (adds heat, needs more flow) |
| TIG | Titanium, zirconium | 100% Ar, plus trailing shield and purge | 15-25 torch, 20-40 trailing, 5-10 purge | |
| Plasma cutting | Steel | Compressed air (dry, 90-120 psi at the machine, per cut chart) | per chart | Nitrogen for stainless/aluminium quality, Ar-H2 on some systems |
| Plasma gouging | Steel | Air | per chart | |
| Purge / back-purge | Stainless, titanium, nickel | 100% Ar (or nitrogen for some stainless) | 5-15 cfh after purge | |
| Oxy-fuel | | Oxygen + acetylene/propane/propylene | per tip chart | See [Victor tip chart](/article/victor-tip-chart-acetylene) |

## Why the mixes behave the way they do

- **Argon**: inert, low ionisation energy, stable arc, low penetration on its own. Pure argon on steel MIG gives a narrow finger-shaped penetration and erratic arc; it needs a little CO2 or O2.
- **CO2**: active (breaks down in the arc), adds heat and wide penetration, oxidises the puddle (more spatter, more silicon islands, loses some Mn/Si). Cannot spray.
- **Oxygen 1-5%**: stabilises the arc and wets the bead in spray mode with minimal oxidation.
- **Helium**: hotter arc, wider bead, needs more flow (lighter than air, escapes), expensive. Aluminium and copper thick sections, stainless tri-mix.
- **Nitrogen**: plasma cutting gas, some stainless purges; never as a MIG shielding gas on steel (porosity, nitrides).
- **Hydrogen**: added to argon (2-5%) for stainless and nickel TIG/plasma (hotter, cleaner); never on carbon steel or aluminium (cracking, porosity).

## Setting flow

![Read the flowmeter at the centre of the ball with gas flowing; a regulator gauge reads pressure, not flow](/img/welding/flowmeter-reading.svg)

*Read the flowmeter at the centre of the ball with gas flowing; a regulator gauge reads pressure, not flow*

- **Regulator** (two gauges, psi): reads pressure, not flow; the second gauge on a "regulator-flowgauge" is calibrated in cfh for one orifice: fine for MIG.
- **Flowmeter** (ball in a tube, cfh or L/min): reads actual flow. Read at the **centre of the ball**, with gas **flowing** (trigger held or TIG purge button). Required for TIG.
- Too little flow = porosity, grey welds. Too much = turbulence pulls in air = porosity, wasted gas. Bigger nozzle → more flow; draughts → more flow or a screen; overhead welding → slightly less flow (gas rises into the joint).
- A leak in the gun cable or hose often shows as **porosity at the start of welds** after the machine sits (air diffuses into the line). Check with leak fluid, replace O-rings.

## Cylinders

![Shielding gas cylinders capped and bundled for storage](/photos/welding/gas-cylinders.jpg)

*Shielding gas cylinders capped and bundled for storage. Photo: Ildar Sagdejev (Specious), CC BY-SA 4.0, via commons*

| Size (US common names) | Contents (ft³) | Height | Notes |
|---|---|---|---|
| 20 / 40 | 20-40 | 14-17" | Home shop |
| 80 | 80 | 27-33" | Small shop MIG |
| 125 / 150 | 125-150 | 43-48" | |
| **250 (K)** | 250-300 | 51-55" | Shop standard |
| 300 (T) | 300-330 | 55-60" | |
| Liquid dewar | 3 000-4 500 | | High-volume shops |

**Hours per bottle** ≈ contents ÷ flow. A 250 ft³ cylinder at 25 cfh gives 10 hours of arc-on time (about 25-30 hours of a real shift). CO2 is sold by weight (a 50 lb CO2 cylinder ≈ 435 ft³ of gas). Full pressure on argon and mixes ≈ 2 000-2 400 psi; CO2 sits at about 830 psi at 70°F regardless of how full it is (liquid inside), so gauge pressure does not tell you how much CO2 is left.

Cylinder handling: upright and chained, cap on when not connected, crack the valve to blow dust before fitting the regulator, open the valve **slowly** with the regulator backed out, stand to the side of the gauges, close the valve at the end of the shift and bleed the line. Argon and CO2 are asphyxiants in a confined space: they displace air without warning.

## Purging

1. Cap or tape the pipe ends; leave a small vent at the top of the far end.
2. Feed argon in at the **bottom**, vent at the top (argon is heavier than air). Nitrogen purges go the other way (lighter).
3. Purge **at least 5-6 volumes** of the pipe at 10-20 cfh, then reduce to 5-10 cfh while welding. Purge time (min) = pipe volume (ft³) × 6 ÷ flow (cfh). Oxygen meter target < 0.1% (1 000 ppm) for stainless, < 0.005% (50 ppm) for titanium.
4. Water-soluble purge paper dams reduce the volume. Keep the purge on until the root is below 800°F.
5. Tape the joint except a 2" window and move the tape as you go on open root welds.

## Related

- [MIG (GMAW) setup](/article/gmaw-mig-setup) and [transfer modes](/article/gmaw-transfer-modes)
- [TIG setup](/article/gtaw-tig-setup)
- [Gas-shielded flux-core setup](/article/fcaw-gas-shielded-setup)
- [Oxy-fuel safety and cylinder handling](/article/oxy-fuel-safety)
- [Plasma cutting setup](/article/plasma-cutting-setup)
