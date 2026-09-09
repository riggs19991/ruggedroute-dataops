---
title: "Oil Analysis and Sampling: Why and When to Sample, Taking a Representative Sample (Live Zone, Sampling Valves, Vacuum Pump Method, Bottle Cleanliness), Reading the Report (Viscosity, Wear Metals, Additive Metals, Contaminants, Water, Acid Number, Particle Count, Ferrous Density), Typical Alarm Limits for Gearboxes, Hydraulics and Bearings, Trending and Actions, Field Tests"
slug: oil-analysis-and-sampling
category: lubrication
kind: procedure
tags: [oil analysis, oil sampling, oil sample, sampling valve, vacuum sampling pump, oil analysis report, wear metals, iron ppm, copper ppm, viscosity change, TAN, acid number, water in oil, Karl Fischer, particle count, ISO code, ferrous density, PQ index, ferrography, oil analysis limits, gearbox oil analysis, hydraulic oil analysis, trending oil analysis, crackle test, blotter spot test, oil condition monitoring]
source: "ASTM D445 (viscosity), D664/D974 (acid number), D6304 (Karl Fischer water), D5185 (elements by ICP), D7416/D7690 (ferrous debris, ferrography); ISO 4406 (particle count); Noria/Machinery Lubrication sampling best practices; SKF, Timken and gearbox makers' condition-monitoring guidance; commercial lab (Polaris, ALS, Bureau Veritas) report interpretation guides."
summary: "Oil analysis tells you the condition of the oil and the machine before either fails, if the sample is taken properly and someone reads the report: this covers what to sample and how often, the sampling technique that gives a representative sample every time, each line of a standard report and what a change in it means, typical alarm limits for the machines a millwright looks after, how to trend and what action each finding calls for, and the quick field tests you can do at the machine."
---

## What it does

A sample every 1-3 months from a gearbox, hydraulic unit or oil-lubricated bearing gives three things: **the oil's condition** (can it stay in service: viscosity, oxidation, additives), **contamination** (dirt, water, coolant, wrong oil), and **machine wear** (which metals are increasing and how fast). A rising iron trend in a gearbox shows up months before the vibration does; water in a hydraulic unit shows up before the pump fails. The **trend** is the value; a single sample without history is a guess.

## What to sample and how often

| Equipment | Interval | Notes |
|---|---|---|
| Critical gearboxes (large, expensive, slow) | Monthly to quarterly | Plus after any event (overheating, a new gear set) |
| General gearboxes | Quarterly to semi-annually | At least at every oil change decision |
| Hydraulic units (industrial) | Quarterly; monthly on servo systems | Particle count and water are the key lines |
| Oil-lubricated pump and fan bearings | Quarterly | Small sumps: the sample is a large share of the oil; top up |
| Compressors (screw) | Quarterly; per the maker for extending fluid life | |
| Turbines, large motors (sleeve bearings) | Quarterly | |
| Engines (mobile equipment) | Every 250-500 h | |
| New oil (each delivery) | Per batch | Baseline: the reference for the trend |

Sample **more often** after a change of oil or a repair (baseline again), during a developing problem (weekly), and when the machine's duty changes.

## Taking the sample

The rule: **from the same point, in the same way, with the machine at operating temperature and running (or just stopped), from a live zone of the oil**, into a **clean** bottle.

![Sample from a live zone at mid-level, not the drain](/img/lubrication/oil-sampling-point.svg)

*Sample from a live zone at mid-level, not the drain*

1. **Point**: a **sampling valve** (a pitot tube or a valve on the return line before the filter on hydraulics; a valve in the side of the sump at mid-level, away from the bottom sludge and the drain, on gearboxes; on the drain line of a bearing housing before the reservoir on circulating systems). Install proper sampling valves (Minimess-type test points with a probe, or a ball valve with a dust cap) on every machine in the program; the **drain plug** gives sludge, and the **fill port** gives the top layer: neither is representative.
2. **Timing**: the machine at operating temperature after at least an hour of running; hydraulic and circulating systems **running**; splash gearboxes and bearing sumps **within minutes of stopping** (the wear debris is still suspended).
3. **Flush**: open the valve and run **5-10× the dead volume** (a few hundred mL) into a waste container so the sample is not the stagnant oil in the valve; wipe the valve.
4. **Bottle**: a new, clean, capped sample bottle (the lab's, certified for particle counting if a count is wanted); **open it only at the moment of filling**; fill to about **3/4**, cap immediately; never touch the inside of the cap or the neck.
5. **Vacuum pump method** (no valve: a dipstick tube, a fill port on a sump): a hand vacuum pump with a new length of tube cut for each sample; insert the tube to **mid-depth of the oil** (never the bottom); draw the sample; discard the tube.
6. **Label** at once: machine, sampling point, date, hours since the last change, oil type and grade, any top-ups (how much), any event (a filter change, a repair, a temperature excursion). The lab's form asks the same; incomplete forms give useless reports.
7. Send within a day or two; keep the bottle out of the sun.

Consistency beats perfection: the same valve, flush, temperature and bottle every time gives a trend; a different method each time gives noise.

## Reading the report

![An oil analysis report: wear metals, contaminants, viscosity and the trend](/photos/lubrication/oil-analysis-report.jpg)

*An oil analysis report: wear metals, contaminants, viscosity and the trend. Photo: Oil lab &amp; --Hermannk (talk) 11:37, 13 November 2020 (UTC), Public domain, via commons*

| Line | What it measures | What a change means |
|---|---|---|
| **Viscosity at 40°C (and 100°C)** | The oil's thickness vs the grade's nominal | **Up** (+10-15%): oxidation, a thicker oil added, soot, water emulsion; **down** (−10-15%): a thinner oil or fuel/solvent added, shear-down of a VI improver, coolant |
| **Acid number (AN, TAN)** | Acidic oxidation products (mgKOH/g) | Rising: oxidation from heat/air/water/age; alarm at about **+0.5 to +1.0 above new** for gear oils, 0.2-0.3 above new for turbine/hydraulic R&O oils; base number (BN) is the engine-oil equivalent going down |
| **Oxidation / nitration (FTIR)** | Infrared absorbance | Rising with AN: the oil is ageing; a varnish warning on turbine and hydraulic oils |
| **Water** (Karl Fischer, ppm or %) | Dissolved + free water | Alarm: **> 500 ppm (0.05%)** hydraulics and bearings, **> 1,000 ppm (0.1%)** most gearboxes, any free water is bad; sources: condensation through the breather, a cooler leak, washdown, a wrong seal |
| **Particle count (ISO 4406 code)** | Solid particles ≥ 4/6/14 µm | Against the target code for the machine ([contamination control](/article/filters-fluid-and-contamination)); rising = ingress or wear |
| **Wear metals (ICP, ppm)**: **iron** (gears, bearings races, shafts, housings), **copper** (bronze bushings/worm wheels, brass cages, coolers), **lead** (babbitt bearings, some bronze), **tin** (babbitt, bronze), **chromium** (rings, some bearings, plating), **aluminium** (pistons, housings, some cages), **nickel** (alloy gears, bearings) | Wear particles under about 8 µm (ICP sees small particles only) | The **trend and the rate** matter: a gearbox at 100 ppm iron steady is different from one going 20 → 60 → 150 in three samples; copper rising in a worm box = the wheel wearing; iron + chromium together = a bearing; lead/tin = babbitt |
| **Contaminant metals**: **silicon** (dirt/dust; also silicone sealant and antifoam), **sodium/potassium/boron** (coolant, salt, some additives), **calcium/magnesium** (detergent additives, hard water, lime dust) | | Silicon **and** aluminium rising together = dust; silicon with iron rising = dirt causing wear; sodium/potassium = coolant leak or seawater |
| **Additive metals**: **zinc/phosphorus** (AW/EP additives), **calcium/magnesium** (detergents), **barium**, **molybdenum** (friction modifier), **boron** | | Falling = additive depletion or dilution with the wrong oil; a jump = the wrong oil added (an EP gear oil into a turbine oil shows zinc/phosphorus appearing) |
| **Ferrous density (PQ index / DR ferrography)** | The total ferrous debris including **large** particles | A rising PQ with a flat ICP iron = **large** particles = a serious wear mode (pitting, spalling); the most important gearbox line |
| **Analytical ferrography** (on request) | Particle shapes under a microscope | Cutting wear (sliding), fatigue chunks (bearings/gears), spheres (bearing fatigue), oxides, non-metallic |
| Foam, air release, demulsibility | Oil properties | Contamination or additive depletion |
| Appearance, odour, colour | | Dark = oxidation; milky = water; a burnt smell = overheating |

Labs flag each line **normal / marginal / abnormal / critical** against their limits for the oil type and the machine type; ask them to set limits for your machines (the same iron number is normal in a big kiln drive and critical in a small hydraulic unit).

## Typical alarm limits (starting points; adjust to your trends)

| Machine | Iron (ppm) | Copper | Silicon | Water | Viscosity change | AN change | ISO code |
|---|---|---|---|---|---|---|---|
| **Industrial gearbox, helical** | caution 100-150, alarm 250-300 (larger boxes higher) | 25-50 | 25-30 | 500-1,000 ppm | ± 10-15% | +0.5-1.0 | 19/17/14 or better |
| **Worm gearbox** | 100 | **100-200 (bronze wheel wear)** | 25 | 500 | ± 15% | +1.0 | |
| **Hydraulic unit** | 30-50 | 20-30 | 15-20 | **200-500 ppm** | ± 10% | +0.3 | target per components (18/16/13 typical) |
| **Turbine / R&O bearing oil** | 20-30 | 10-20 | 15 | 200-500 | ± 5-10% | +0.2-0.3 | 17/15/12 |
| **Pump / fan bearing sump** | 30-50 | 10-20 | 15 | 500 | ± 10% | +0.5 | |
| **Screw compressor fluid** | 30-50 | 20 | 20 | 500 | ± 10% (varnish watch) | +0.5-1.0 | |

A **rate** rule: an increase of more than **50% between consecutive samples** on any wear metal deserves a re-sample within two weeks whatever the absolute level.

## Actions by finding

| Finding | Action |
|---|---|
| Iron rising steadily, PQ rising, other metals normal | Gear/bearing wear starting: shorten the interval, inspect the gearbox (contact pattern, [gear inspection](/article/gear-inspection-and-tooth-failure)), check alignment and load, filter the oil; plan the repair on the trend |
| Iron and chromium/nickel rising | Rolling bearing wear: vibration check, plan a bearing change |
| Copper rising (gearbox) | Bronze wear (worm wheel, bushings, a cage), or a cooler; check the oil (EP on bronze?), the load, the wheel backlash |
| Silicon rising | Dust ingress: the breather, seals, the fill practice; filter/change the oil |
| Water | Find the source (cooler pressure test, breather, seals, washdown practice); dehydrate or change the oil; check bearings for rust |
| Viscosity up, AN up, dark | The oil is oxidised (heat, age): change it, check the temperature and the breather, consider synthetic |
| Viscosity off, additives odd | Wrong oil added: identify, drain and refill, fix the labelling |
| Particle count above target | Ingress or wear: filter cart, check the breather and seals, look for the wear source |
| Sodium/potassium/boron | Coolant: fix the cooler; a coolant leak in a gearbox ruins the oil and the gears quickly |
| Everything normal | Extend the interval or the drain, within the maker's limits; keep sampling |

## Field tests at the machine

- **Crackle test**: a drop of oil on a hot plate at about 300°F (150°C): **crackling/popping = water** (roughly > 500 ppm); a bubble that does not pop = dissolved water; nothing = dry.
- **Blotter spot**: a drop on blotting paper or a filter paper, dry an hour: a dark centre with a sharp edge = soot/insoluble sludge; a wide yellow-brown ring = oxidation; a wet spreading ring = fuel/solvent; a clean uniform spot = healthy.
- **Visual**: in a clear bottle against the light: milky = water, dark = oxidation, sparkles = metal, sediment after settling = dirt/wear; smell: burnt, sour (oxidised), sweet (glycol).
- **Magnetic plug**: fine grey paste is normal wear; flakes, chips or a "fur" of long particles are gear or bearing damage; photograph and keep them.
- **Viscosity comparator** (a two-tube drop-ball or a portable viscometer) for a quick grade check on a suspected wrong oil.
- **Patch test kit**: a measured volume through a membrane, compared with a chart: an ISO code estimate at the machine.

## Building the program

Sampling valves on every machine in the program (one-time cost), the same lab, a spreadsheet or the CMMS with the results trended per machine, limits agreed for each machine class, a person who reads the reports **the week they arrive** and writes the action on a work order, and a feedback loop (when a gearbox is opened, compare what is found with what the oil said). Programs that only file reports find nothing.

## Common mistakes

- Sampling from the drain plug (sludge) and changing good oil, or from the fill hole and missing a problem.
- Cold, stopped machine: the debris has settled.
- Bottle opened in a dusty plant and filled from an open bucket: the particle count is the shop's dust.
- No hours since change on the form: the lab cannot judge the trend.
- Reading only the "overall" flag; a critical iron rate hides behind a "marginal".
- A lab set to "diesel engine" limits reporting on a kiln gearbox.

## Related

- [Filters, fluid and contamination (ISO 4406)](/article/filters-fluid-and-contamination)
- [Oil viscosity and selection](/article/oil-viscosity-and-selection)
- [Gearbox lubrication and inspection](/article/gearbox-lubrication-and-inspection)
- [Gear inspection and tooth failure](/article/gear-inspection-and-tooth-failure)
- [Bearing failure analysis](/article/bearing-failure-analysis)
- [Thermography, ultrasound and oil (condition monitoring)](/article/thermography-ultrasound-and-oil)
