---
title: "MIG Welding (GMAW) Setup: Machine, Wire, Gas, Voltage and Wire-Feed Charts by Thickness, Drive Rolls, Liner, Tips, Stickout and Technique"
slug: gmaw-mig-setup
category: welding
kind: procedure
manufacturer: "Miller / Lincoln (generic)"
model_numbers: ["Millermatic 211", "Millermatic 252", "Multimatic 220", "Power MIG 210 MP", "Power MIG 256", "ER70S-6"]
tags: [MIG welding, GMAW setup, MIG settings chart, wire feed speed, voltage chart, C25, 75/25, .030 wire, .035 wire, .045 wire, stickout, contact tip, drive roll tension, liner, spool gun, short circuit, MIG troubleshooting, burn back, bird nest]
source: "Miller Electric 'MIG Welding: Setting the Correct Parameters' and Millermatic weld-parameter door charts (as reproduced on garagewelding.com); Lincoln Electric GMAW procedure sheets; AWS Welding Handbook Vol. 2."
summary: "A complete MIG setup walk-through with the chart most students want: voltage and wire feed speed for .023, .030, .035 and .045 ER70S-6 wire on C25 from 22 gauge to 1/4 inch, plus the amps-per-ipm rules, polarity, gas and flow, drive roll and liner checks, contact tip and stickout, gun angles, and a troubleshooting table."
---

> MIG is easy to start and easy to do badly. Nine out of ten weak MIG welds are **cold**: the setting was fine for the sound of it but the wire never fused the root. Set by the chart, then push the settings until the bead flattens and wets into the plate, and check a cut-and-etch or a bend test when it matters.

## 1. Machine and polarity

![MIG runs DCEP: gun lead to positive](/img/welding/polarity.svg)

![A MIG machine with the gun, work lead and shielding gas bottle](/photos/welding/mig-machine.jpg)

*A MIG machine with the gun, work lead and shielding gas bottle. Photo: Luke Haggart, CC BY-SA 4.0, via commons*

*MIG runs DCEP: gun lead to positive*

- **Constant-voltage (CV)** power source. You set **voltage** on the machine and **wire feed speed (WFS)**; the machine supplies whatever **amperage** the wire feed demands. WFS is the amperage knob; voltage is the arc length / bead width knob.
- **DCEP (DC+)** for solid wire and gas-shielded flux-core: gun lead on **+**, ground on **−**. (Self-shielded flux-core is the exception: DC−.)
- Synergic / "auto-set" machines: pick wire size, gas and thickness; the machine sets both. Fine-tune from there.

## 2. Wire

![A spool of solid MIG wire: keep it clean, dry and under a cover](/photos/welding/mig-wire-spool.jpg)

*A spool of solid MIG wire: keep it clean, dry and under a cover. Photo: AMPedNH, CC BY 2.0, via commons*

| Wire | Amperage range | Thickness sweet spot | WFS per amp (rule) |
|---|---|---|---|
| .023 / .024" | 30-130 A | 24-16 ga sheet, auto body | ~3.5 ipm per amp |
| **.030"** | 40-145 A | 22 ga to 3/16" (1/4" multi-pass) | **~2 ipm per amp** |
| **.035"** | 50-180 A short-circuit; to 250 A spray | 16 ga to 1/4" (thicker in spray) | **~1.6 ipm per amp** |
| **.045"** | 75-250 A short-circuit; to 350 A spray | 3/16" and up; spray on 1/4" and thicker | **~1 ipm per amp** |

ER70S-6 is the default steel wire (tolerates mill scale). Match **drive rolls** (V-groove for solid steel, U-groove for aluminium, knurled for flux-core), **liner** (steel liner for steel; PTFE/nylon for aluminium), and **contact tip** (stamped size; a worn oval tip causes erratic arc) to the wire diameter.

## 3. Gas

![Cylinder regulator with the flow gauge for a MIG setup](/photos/welding/mig-regulator.jpg)

*Cylinder regulator with the flow gauge for a MIG setup. Photo: Mimzy, CC0, via commons*

| Gas | Use | Flow |
|---|---|---|
| **C25 (75% Ar / 25% CO2)** | The shop default for steel short-circuit; also globular | 20-25 cfh; up to 30 outdoors or with a large nozzle |
| 100% CO2 | Cheap, deepest penetration, more spatter, globular above ~200 A | 20-30 cfh |
| 90/10 Ar-CO2, 92/8, 95/5, 98/2 Ar-O2 | **Spray and pulsed spray** on steel (≥ 80% Ar needed for spray) | 35-45 cfh |
| 100% Ar | Aluminium (all modes), copper | 30-40 cfh |
| Tri-mix (90 He / 7.5 Ar / 2.5 CO2) or Ar-2% O2 | Stainless short-circuit / spray | 25-35 cfh |
| Ar-1-2% O2 | Stainless spray | 30-40 |

Set flow with the **torch trigger held** (flow, not static). Too little: porosity. Too much (over ~50 cfh with a 5/8" nozzle): turbulence pulls air in, also porosity. Details in [gas selection and flow](/article/gas-selection-and-flow).

## 4. The settings chart: ER70S-6, C25, short-circuit transfer, flat/horizontal fillets

Values are the Miller door-chart starting points; they give roughly the amperage in the last column (WFS ÷ ipm-per-amp).

| Material thickness | .023" wire (V / ipm) | .030" wire (V / ipm) | .035" wire (V / ipm) | Approx. amps |
|---|---|---|---|---|
| 22 ga (.030") | 15.8 / 125 | 15.9 / 95 | 15.0 / 88 | 40-55 |
| 18 ga (.048") | 17.0 / 190 | 16.3 / 115 | 15.8 / 120 | 55-75 |
| 14 ga (.075") | 18.0 / 240 | 17.3 / 200 | 16.5 / 190 | 90-120 |
| 1/8" (.125") | 18.3 / 350 | **19.0 / 290** | 17.4 / 230 | 125-150 |
| 3/16" (.188") | 20.0 / 480 | 21.0 / 400 | 18.4 / 265 | 165-200 |
| 1/4" (.250") | - | 24.3 / 500 | 21.0 / 375 | 200-250 (multi-pass or spray preferred) |

**.045" wire, short-circuit, C25 (typical Lincoln procedure sheet values):** 1/8": 17-19 V / 150-175 ipm (≈150 A); 3/16": 19-20 V / 200 ipm (≈200 A); 1/4": 20-21 V / 240 ipm (≈240 A). Above 1/4" switch to spray with 90/10 gas: 26-29 V / 350-450 ipm (250-320 A), flat and horizontal only. See [transfer modes](/article/gmaw-transfer-modes).

Notes on using the chart:
- Charts assume a **fillet weld in the flat/horizontal position**. Vertical-up: about 10-15% less WFS and 1 V less. Vertical-down (sheet): keep it hot and move fast.
- Butt welds on thin sheet: one step colder than the chart.
- The chart WFS is often 5-10% hotter than a comfortable setting; many welders trim it.
- Miller's rule: **1 A per 0.001" of thickness** in short-circuit (1/8" ≈ 125 A). Convert to WFS with the ipm-per-amp factor: 125 A × 2 ipm/A = 250 ipm for .030 (chart says 290 with a hotter fillet setting; both work).
- Aluminium with a spool gun (.035 ER4043, 100% Ar): 22-24 V / 480-740 ipm (85-190 A) on 1/8-1/4"; stainless (.035 ER308L, tri-mix): 23-24 V / 265-335 ipm on 18 ga-1/8".

## 5. Physical setup

![Contact-tip-to-work distance, stickout and push angle](/img/welding/mig-stickout.svg)

*Contact-tip-to-work distance, stickout and push angle*

1. **Drive-roll tension**: just enough that the wire cannot be stopped by pinching it lightly at the tip with gloved fingers; too tight deforms the wire and flakes copper into the liner. Test: feed the wire against a block of wood; it should slip at the rolls, not buckle.
2. **Liner**: right size, not kinked, cut square, blown out with dry air when changing wire. Bird-nesting at the rolls = liner blocked or tip too small.
3. **Contact tip**: correct size, snug, replace when the hole ovals or spatter builds. Keep a handful in your pocket.
4. **Nozzle**: clean, anti-spatter gel or dip, recessed tip for spray (tip 1/8" inside nozzle) and flush-to-1/8"-proud for short-circuit.
5. **Stickout (CTWD, contact tip to work)**: **3/8-1/2" for short-circuit**, **1/2-3/4" for spray**, **3/4-1" for flux-core**. Longer stickout = less amperage at the same WFS (colder), more preheat of the wire.
6. **Ground** on clean metal near the weld; not through a rotating part.
7. **Gun cable** straight, not coiled around things; a tight coil makes feeding erratic.

## 6. Technique

![MIG welding: short stickout, steady gun angle, eyes on the puddle](/photos/welding/mig-welding.jpg)

*MIG welding: short stickout, steady gun angle, eyes on the puddle. Photo: William M. Plate Jr., Public domain, via commons*

- **Gun angle**: **push** 10-15° for solid wire with gas (cleaner, better shielding, flatter bead); drag for flux-core ("drag if slag"). Work angle 45° on fillets, 90° on butts.
- **Travel**: keep the arc on the **leading edge** of the puddle. If you are welding on top of the puddle you are laying cold metal.
- **Patterns**: stringer for most; small whip or "C" on gaps; triangle (upside-down V) on vertical-up 1/4" and up.
- **Sound**: short-circuit should crackle steadily like bacon. Popping = voltage too high or WFS too low; hissing = spray; loud slapping = too much WFS/too little voltage (wire stubbing).
- **Bead shape**: flat to slightly convex, toes wetted in. Ropy, tall bead sitting on top = cold: raise voltage and/or WFS. Wide flat bead with undercut = too hot or too slow.
- **Tack** every 4-6" on sheet, then weld in short runs alternating ends to control distortion.
- **Starts**: cut the wire to 3/8" with a fresh sharp end before each start; a ball on the end pops.
- **Stops**: fill the crater by pausing and backing up 1/4" (or use crater-fill on the machine).

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Porosity (holes, worms) | No/low gas, wind, leaking gun, wet/dirty base metal, too much stickout, nozzle clogged with spatter, wrong gas | Check flow with trigger, block wind, clean, shorten stickout, clean nozzle |
| Wire stubbing / burning back to tip | Voltage too high (burn-back) or WFS too high (stubbing); bad tip; tension wrong | Adjust, new tip |
| Bird-nest at the rolls | Tip clogged, liner blocked, tension too tight, wrong rolls | Clear tip/liner, reset tension |
| Cold lap / no penetration | Settings too cold, too fast, welding on the puddle, stickout too long | Raise V and WFS, slow down, lead the puddle |
| Burn-through on thin sheet | Too hot, too slow, gap | Smaller wire, lower settings, fast whip, backing bar |
| Excess spatter | Voltage too high or low for the WFS, 100% CO2, dirty plate, long stickout | Balance V to WFS, C25, clean |
| Undercut | Too hot, too fast, bad angle | Lower V, pause at toes |
| Erratic arc | Worn tip, wire rubbing, loose ground, ovaled liner, damp wire (rust) | Replace consumables, clean ground |
| Wire feeds but no arc | Ground, polarity, tip not touching wire | Check circuit |
| Black sooty weld on aluminium | Too little gas, wrong gas, dirty base | 100% Ar 30-40 cfh, stainless brush |

## 8. Shutdown

Trigger released, gas valve on the cylinder closed, bleed the line, wire retracted or spool covered (rust), gun hung with the nozzle clear of the table.

## Related

- [MIG transfer modes: short-circuit, globular, spray, pulsed](/article/gmaw-transfer-modes)
- [Shielding gas selection and flow rates](/article/gas-selection-and-flow)
- [Gas-shielded flux-core setup](/article/fcaw-gas-shielded-setup) and [self-shielded flux-core setup](/article/fcaw-self-shielded-setup)
- [Welding aluminium](/article/welding-aluminium) and [welding stainless](/article/welding-stainless-and-dissimilar)
- [Machine setup, duty cycle and cables](/article/machine-setup-and-duty-cycle)
- [Welder maintenance and consumables](/article/welder-maintenance-and-consumables)
