---
title: "Plasma Cutting Setup and Cut Charts: Air Supply, Consumable Stack, Hypertherm Powermax45 XP / 65 / 85 / 105 Capacities, Mild Steel Cut Chart (Amps, Thickness, Speed, Voltage, Kerf), Hand Cutting Technique, Dross and Bevel Troubleshooting"
slug: plasma-cutting-setup
category: cutting-gouging
kind: chart
manufacturer: Hypertherm
model_numbers: ["Powermax45 XP", "Powermax65", "Powermax85", "Powermax105", "Powermax30 AIR", "Duramax", "Spectrum 625", "Spectrum 875", "Cutmaster 60i"]
tags: [plasma cutting, plasma cutter setup, plasma cut chart, Hypertherm cut chart, Powermax 45, Powermax 65, Powermax 85, plasma air pressure, plasma consumables, electrode, nozzle, swirl ring, shield, retaining cap, drag cutting, standoff, cut speed, arc voltage, kerf width, dross, bevel, plasma stainless, plasma aluminum, plasma CNC table, torch height]
source: "Hypertherm Powermax45 XP Operator Manual 809240 rev. 4 (specifications, recommended cut capacity, mild steel 45 A shielded cut chart, gouging tables); Hypertherm Powermax65/85 and Powermax105 published specifications; Hypertherm cutting-technique guidance."
summary: "How a plasma cutter is set up from the compressor to the tip: air quality and flow, the consumable stack and when to change each part, what the capacity numbers mean, the full Powermax45 XP mild steel cut chart with pierce heights, delays, speeds and arc voltages for hand and CNC use, capacity and air figures for the 65/85/105, and the technique and troubleshooting for clean square cuts."
---

## How it works, in one paragraph

A pilot arc inside the torch ionises the air; when the torch is near the plate the main arc transfers to the work and the swirl of compressed air through a small nozzle orifice constricts it to a 30,000°F jet that melts and blows the metal out of the kerf. It cuts **anything conductive** (steel, stainless, aluminium, copper, cast iron), needs only electricity and dry air, and leaves a narrow kerf with a small heat-affected zone. The consumables (electrode with a hafnium insert, nozzle) are the wear parts; the air quality decides how long they last.

## Air supply

| Item | Requirement |
|---|---|
| Pressure at the machine inlet | **85 psi minimum** while cutting (Powermax45 XP: 400 scfh / 6.7 scfm at 85 psi; do not exceed 135 psi); the machine regulates internally. Set the shop regulator to about **90-120 psi** so the inlet never drops below 85 with the hose losses |
| Flow | 6-7 scfm (400 scfh) for the 45/65/85 class, 7.5 scfm (450 scfh) for the 105 and for gouging on the 85; the compressor must supply this **continuously** at pressure, so a compressor rated 8-10 cfm at 90 psi or better with a 30+ gal receiver for a 45 A machine, larger for the 85/105 |
| Quality | **Clean, dry, oil-free** (ISO 8573-1 class 1.2.2 for Hypertherm). Water or oil in the air kills electrodes in minutes, causes spitting starts, ragged cuts and torch arcing. Fit a **particulate/coalescing filter** at the machine and a **refrigerated or desiccant dryer** on any compressor in a humid shop; drain the receiver daily |
| Hose | 3/8" ID minimum, short; a 1/4" hose from a long run starves the torch |
| Alternatives | Nitrogen cylinder (99.95%) for stainless/aluminium quality; F5 (95 N2 / 5 H2) for stainless on some systems; argon for marking. Air is right for 95% of millwright work |

Low air = the torch fires, then stutters and the "gas pressure" fault lights. Check the inlet gauge while cutting, not idle.

## Consumable stack

![Electrode, swirl ring, nozzle, retaining cap and shield; standoff and torch angle](/img/cutting-gouging/plasma-torch-consumables.svg)

*Electrode, swirl ring, nozzle, retaining cap and shield; standoff and torch angle*

```
   torch body → electrode (hafnium insert) → swirl ring → nozzle (tip, orifice by amperage) → retaining cap → shield (drag shield for hand, deflector for machine)
```

| Part | Job | Replace when |
|---|---|---|
| **Electrode** | Carries the arc from the hafnium insert | Pit in the insert deeper than about **1/16" (1.5 mm)**; heavy pitting = green-white arc, slow cuts, and it will blow through and destroy the torch |
| **Nozzle (tip)** | Constricts the arc; orifice matched to amperage (45 A, 65 A, 85 A, 105 A, FineCut) | Orifice out of round or oversize, gouged; symptoms: bevelled cut, wide kerf, dross, wandering arc |
| **Swirl ring** | Spins the gas | Cracked, holes blocked; rarely |
| **Retaining cap** | Holds the stack, carries air | Cracked or arced |
| **Shield / drag shield** | Protects the nozzle, lets you drag the torch on the plate; deflector for machine torches | Holes blocked with spatter, face arced, rounded |
| **O-rings** | Seal the torch | Dry, cracked: leaks and misfires |

**Change electrode and nozzle together** as a pair; keep a set in the box. Always match the consumable part numbers on the cut chart for the amperage (the Powermax45 XP 45 A shielded set in the manual is shield 220817, retaining cap 220854, nozzle 220941, swirl ring 220857, electrode 220842; check the chart for your model). FineCut consumables (narrow kerf, thin material) and gouging consumables are different parts. Use only the maker's or a known-equivalent brand: cheap copies burn fast and can arc inside the torch.

## What the capacity numbers mean

| System | Recommended (hand, good quality, ~20 ipm) | Maximum (10 ipm) | Severance (5 ipm, rough) | Pierce, hand | Air |
|---|---|---|---|---|---|
| **Powermax45 XP** (45 A) | **5/8" (16 mm)** | 7/8" (22 mm) | 1-1/8" (29 mm) | **1/2" (12 mm)** | 400 scfh at 85 psi |
| **Powermax65** (65 A) | **3/4" (20 mm)** | 1" (25 mm) | 1-1/4" (32 mm) | 5/8" (16 mm) | 400 scfh at 85 psi |
| **Powermax85** (85 A) | **1" (25 mm)** | 1-1/4" (32 mm) | 1-1/2" (38 mm) | 3/4" (19 mm) | 400 scfh at 85 psi (450 at 70 psi for gouging) |
| Powermax105 (105 A) | 1-1/4" (32 mm) | 1-1/2" (38 mm) | 2" (50 mm) | 7/8" (22 mm) | 450 scfh at 85 psi |
| Powermax30 AIR (built-in compressor) | 3/8" (10 mm) | 1/2" | 5/8" | 1/4" | internal |

"Recommended" is what you cut all day with a clean edge; "severance" is a hot ragged parting cut. **Pierce capacity is about half the recommended cut thickness**; above it, edge-start or drill a start hole.

Powermax45 XP maximum cut speeds on mild steel (hand, lab conditions): 1/4" 90 ipm, 3/8" 48 ipm, 1/2" 30 ipm, 5/8" 20 ipm, 3/4" 13 ipm, 1" 7 ipm.

## Powermax45 XP mild steel cut chart, 45 A, air, shielded consumables

Mechanized (CNC) data from the operator manual; hand cutting uses the same speeds as a guide with the drag shield on the plate. Torch-to-work (cut height) **0.06" (1.5 mm)**; pierce height **0.15" (3.8 mm), 250% of cut height**.

![Cut speed versus thickness for 45, 65 and 85 A air plasma](/img/cutting-gouging/plasma-cut-chart.svg)

*Cut speed versus thickness for 45, 65 and 85 A air plasma*

| Thickness | Pierce delay (s) | Best quality: speed (ipm) | Best quality: arc volts | Production: speed (ipm) | Production: arc volts | Kerf (in) |
|---|---|---|---|---|---|---|
| 16 ga (0.060") | 0.1 | 249 | 128 | 320 | 125 | 0.053 |
| 14 ga (0.075") | 0.2 | 225 | 128 | 320 | 125 | 0.054 |
| 10 ga (0.135") | 0.4 | 129 | 128 | 181 | 128 | 0.057 |
| **3/16"** | 0.5 | **85** | 129 | 122 | 127 | 0.059 |
| **1/4"** | 0.6 | **48** | 130 | 72 | 127 | 0.061 |
| **3/8"** | 0.8 | **33** | 136 | 38 | 133 | 0.069 |
| **1/2"** | 1.0 | **18** | 141 | 24 | 139 | 0.077 |
| 5/8" | edge start | 13 | 146 | 16 | 141 | 0.082 |
| 3/4" | edge start | 7 | 151 | 10 | 145 | 0.086 |
| 7/8" | edge start | 6 | 154 | 7 | 151 | 0.103 |
| 1" | edge start | 4 | 157 | 6 | 154 | 0.119 |

Metric (best quality): 2 mm 5560 mm/min at 128 V; 3 mm 3390 at 128; 4 mm 2800 at 128; 6 mm 1430 at 130; 8 mm 1020 at 133; 10 mm 780 at 136; 12 mm 540 at 140; 16 mm 310 at 146; 20 mm 170 at 152; 25 mm 110 at 157.

Stainless and aluminium have their own tables in the manual: roughly the same speeds on thin gauge, **20-30% slower on stainless** above 1/4" and slightly faster on aluminium, with more dross and a need for nitrogen for clean edges. Larger machines: the 65 cuts 1/2" at about 30-35 ipm and 3/4" at 15; the 85 cuts 1/2" at about 45 ipm, 3/4" at 25 and 1" at 12-15 (from the maker's charts; confirm on the chart for your consumables).

**Arc voltage** matters on a CNC table with torch height control: it rises as the consumables wear and as the torch lifts; set the THC to the chart voltage and it holds the cut height. By hand, ignore it.

## Setting up to cut

1. Ground: work clamp on **clean bare metal** on the piece being cut (not on the slats of the table alone, not across a hinge or bearing). A poor ground = no arc transfer, double-arcing, short consumable life.
2. Air: drain the receiver, check the filter bowl is dry, set the inlet pressure, confirm on the machine's gauge while pressing the trigger with the torch away from metal (gas test mode on most machines).
3. Consumables: correct set for the amperage and job (shielded drag for hand; FineCut for thin sheet; gouging for gouging); tight, O-rings lightly lubricated with the silicone that came with the torch (never petroleum).
4. Amperage: **max for the thickness** (45 A on a 45 machine for anything over 1/8"); lower amps (20-30 A) only for thin sheet with FineCut or to slow the melt on 20 ga. Amps do not fine-tune the cut; speed does.
5. Mode: cut / continuous pilot arc (for expanded metal and grating: pilot stays on across gaps, more consumable wear) / gouge.
6. Safety: **shade 8** (up to 300 A) per the table in [welding safety](/article/welding-safety-fumes-and-ppe), gloves, leathers, hearing protection (plasma is loud), fume extraction on stainless (hex chrome) and galvanised, fire watch (sparks go 20 ft), nothing flammable under the table.

## Hand cutting technique

- **Drag the shield on the plate** with shielded consumables; with unshielded, hold **1/16-1/8" standoff**. Torch **90° to the plate**; tilt only for bevels.
- Start on the edge: torch at the edge, trigger, wait for the arc to punch through, then move. Circles and inside cuts: **pierce** with the torch tilted 30-45° away from you so the blow-back does not hit the shield, rotate upright as it goes through (see [piercing and keyholing](/article/plasma-keyholing-and-piercing)).
- **Speed**: correct speed shows a **15-20° trailing arc** under the plate with sparks going down and slightly behind. Sparks straight down or forward = too slow (heavy dross, wide kerf); sparks spraying back at a shallow angle = too fast (the cut does not go through; the arc climbs the plate).
- Pull the torch toward you (dragging) is steadier than pushing. Use a straightedge, an angle-iron guide, a circle-cutting attachment or a roller guide for anything you want straight; the cut is only as good as your hand.
- The **square side of the kerf** is on the **right** of the direction of travel (looking from behind the torch, moving away), the bevelled side on the left, because of the arc swirl. Cut so the scrap is on the left.
- Finish the cut by slowing slightly at the end so the arc goes fully through the last bit; a lost arc at the end leaves a hanging tab.
- Post-flow: keep the torch on the machine's hanger until the air stops; the post-flow cools the consumables.

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| Will not fire / no pilot arc | No air, low air pressure, consumables loose or worn, cap not seated (safety switch), trigger safety | Air first, then consumables |
| Fires but will not transfer / cuts out | Bad ground, standoff too high, painted or rusty plate under the clamp | Clean clamp spot, drag the torch |
| Heavy **low-speed dross** (thick, easy to knock off, under the plate) | Too slow, amps too high for the thickness | Speed up |
| **High-speed dross** (thin, hard, welded to the bottom edge) | Too fast, worn nozzle, standoff too high | Slow down, new nozzle |
| Top-side dross / spatter | Standoff too high, worn shield, fast | Drag the shield |
| **Bevelled cut** (one side more than the usual 3-5°) | Worn nozzle/electrode, torch not vertical, too fast, wrong direction (bevel side toward the part) | New consumables, square the torch, cut the other way round |
| Wide kerf, wandering arc, green-white flame | Electrode pit too deep, nozzle oversize, wet air | Change the pair, dry the air |
| Short consumable life | **Water/oil in the air**, piercing too close, arc stretched at the end of cuts, continuous pilot arc on solid plate, cheap copies | Dryer and filter; pierce at height; cut off the arc promptly |
| Cut stops part way through thick plate | Beyond capacity, too fast, low input power (long extension cord, generator) | Slow to severance speed or use a bigger machine; 10 AWG cord max 50 ft |
| Double arcing (nozzle burns from the outside) | Standoff too small with unshielded tip, touching the plate, spatter bridging | Shielded consumables, clean the shield |
| Machine trips on duty cycle | Powermax45 XP is 50% at 45 A (5 minutes in 10) at 104°F | Let the fan run; lower amps for long thin cuts |

## Related

- [Plasma piercing, keyholing and gouging](/article/plasma-keyholing-and-piercing)
- [Carbon-arc gouging](/article/carbon-arc-gouging)
- [Oxy-fuel cutting technique](/article/oxy-fuel-cutting-technique)
- [Welding safety and PPE (shade table)](/article/welding-safety-fumes-and-ppe)
- [Machine input power and duty cycle](/article/machine-setup-and-duty-cycle)
