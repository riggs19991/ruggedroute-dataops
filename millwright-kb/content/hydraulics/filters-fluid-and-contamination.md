---
title: "Hydraulic Filters, Fluid and Contamination Control: ISO 4406 Cleanliness Codes Explained with Target Codes by Component, Beta Ratio and Micron Ratings, Filter Locations and Bypass Indicators, Changing a Filter Element, Breathers and Reservoir Care, Fluid Selection (ISO VG, Type), Taking a Sample, Flushing After a Failure, Water and Air in the Oil"
slug: filters-fluid-and-contamination
category: hydraulics
kind: reference
tags: [hydraulic filter, ISO 4406, cleanliness code, 18/16/13, 16/14/11, beta ratio, micron rating, absolute vs nominal, filter bypass, filter indicator, return filter, pressure filter, suction strainer, offline filter, kidney loop, desiccant breather, reservoir cleaning, hydraulic fluid, ISO VG 32 46 68, AW hydraulic oil, water in hydraulic oil, aeration, foaming, hydraulic oil sample, particle count, flushing hydraulic system, filter cart, contamination control]
source: "ISO 4406:2021 (solid contamination code) and ISO 11171 (particle counter calibration); ISO 16889 (multi-pass test, beta ratio); Parker, Donaldson, Hydac and Pall filtration guides (target cleanliness codes by component, filter placement); Noria/Machinery Lubrication contamination control guidance; Eaton Vickers system cleanliness recommendations."
summary: "Most hydraulic failures are contamination: this explains how cleanliness is measured and what code each component needs, how a filter is rated and where each type sits, the routine of changing elements and reading indicators, keeping the reservoir and the breather doing their job, choosing the fluid, sampling for a particle count, how to flush after a pump failure, and the signs and cures for water and air in the oil."
---

## ISO 4406 codes

A particle counter reports the number of particles per millilitre larger than **4 µm, 6 µm and 14 µm** (ISO 11171 calibration; the old code used 5 and 15 µm); each count is converted to a **range number**: each step **doubles** the count.

| Range number | Particles per mL (more than) | up to |
|---|---|---|
| 12 | 20 | 40 |
| 13 | 40 | 80 |
| **14** | **80** | 160 |
| 15 | 160 | 320 |
| **16** | **320** | 640 |
| 17 | 640 | 1,300 |
| **18** | **1,300** | 2,500 |
| 19 | 2,500 | 5,000 |
| 20 | 5,000 | 10,000 |
| 21 | 10,000 | 20,000 |
| 22 | 20,000 | 40,000 |

So **18/16/13** means 1,300-2,500 particles/mL over 4 µm, 320-640 over 6 µm, 40-80 over 14 µm. **One code number lower = half the dirt.** New oil from the drum is typically 20/18/15 to 22/20/17: **dirtier than most systems need**; it must be filtered going in.

**Target cleanliness by the most sensitive component in the system** (industry practice; the component maker's number governs):

| Component | Target ISO code (system pressure < 2,000 psi) | (2,000-3,000 psi) | (> 3,000 psi) |
|---|---|---|---|
| **Servo valves** | **16/14/11** | 15/13/10 | 14/12/9 |
| **Proportional valves** | 17/15/12 | 16/14/11 | 15/13/10 |
| **Variable-displacement piston pumps and motors** | **18/16/13** | 17/15/12 | 16/14/11 |
| Fixed piston pumps | 19/17/14 | 18/16/13 | 17/15/12 |
| Vane pumps | 19/17/14 | 18/16/13 | 18/16/13 |
| **Gear pumps** | **20/18/15** | 19/17/14 | 18/16/13 |
| Directional (solenoid) valves, cylinders | 20/18/15 | 19/17/14 | 18/16/13 |
| Ball bearings, roller bearings (in the same oil) | 15/13/10 to 16/14/11 | | |
| Industrial gearboxes (oil) | 17/15/12 to 19/17/14 | | |

The Eaton/Vickers rule: going from 22/20/17 to 18/16/13 roughly **doubles to quadruples** pump and valve life.

## Filter ratings

- **Beta ratio** (ISO 16889 multi-pass test): β₁₀ = (particles ≥ 10 µm upstream) ÷ (particles ≥ 10 µm downstream). **β = 2 is 50% efficiency; β = 75 is 98.7%; β = 200 is 99.5%; β = 1000 is 99.9%**. A filter is described as e.g. "β₁₀(c) ≥ 1000" (the "(c)" means the ISO 11171 calibration). Ask for the beta ratio at the size you care about, not the "micron rating".
- **Absolute rating** = the size at which β ≥ 75-200 (99% efficient): meaningful. **Nominal rating** = a marketing number (often only 50% efficient at that size): meaningless.
- Typical elements: **3 µm (β₃ ≥ 200)** for servo systems, **5-6 µm** for piston pumps and proportional valves, **10 µm** for general industrial, **25 µm** for gear pump systems and return lines on mobile equipment, **100-150 µm (mesh)** for suction strainers. Cellulose media: cheap, lower beta, absorbs water; **glass fibre (microglass)**: high beta, more dirt-holding, the standard; stainless mesh: cleanable, coarse.
- **Dirt-holding capacity** decides the change interval; a bigger housing is cheaper than frequent elements.

## Where the filters go

| Location | Job | Rating | Notes |
|---|---|---|---|
| **Suction strainer** (in the tank) | Keeps big trash out of the pump | 100-150 µm mesh | Never fine: a fine suction filter **starves the pump** (cavitation); many makers omit it on piston pumps; clean it at every oil change |
| **Pressure filter** (after the pump, before the valves) | Protects the servo/proportional valves from pump debris | 3-10 µm, high-pressure housing, β high | The one with the **bypass valve removed** or set high on servo systems (a bypassing pressure filter is no filter); an indicator you can see |
| **Return filter** (before the tank) | Catches the wear debris from the whole system; the workhorse | 10-25 µm | Sized for the return surge (cylinder differential); with a bypass and an indicator; in the tank-top or in-line |
| **Off-line / kidney-loop** (its own small pump, tank to tank) | Continuous polishing; the only way to hold 16/14/11 on a dirty machine | 3-5 µm, plus a water-absorbing element if needed | Runs 24/7 regardless of the main pump; a **filter cart** does the same job on wheels for topping up and for flushing |
| **Breather** (tank vent) | Stops airborne dust and moisture entering the tank as the level breathes | 3-10 µm, **desiccant** where humid | Replace when the desiccant changes colour or the ΔP rises; the cheapest and most neglected filter |
| Fill port screen / fill through a filter | New oil is dirty | Fill only through the filter cart or a fill filter | |
| Case drain filter | Piston pump case drain | 10 µm, low pressure | |
| Bypass valve | Opens at 25-50 psi ΔP so the system keeps running when the element is blocked; the oil then bypasses **unfiltered** | | Change the element **before** the bypass opens |

**Indicators**: mechanical (pop-up), gauge (ΔP), or electrical switch to the PLC; read them **at operating temperature** (cold oil shows a high ΔP that is viscosity, not dirt). An indicator that never moves is either a good sign or a stuck indicator: change the element on hours anyway.

## Changing an element

1. Lockout: pump off, pressure bled, the filter housing's own bleed/drain opened; on a pressure filter confirm zero on its gauge; on a return filter the housing may hold oil above the tank level: catch it.
2. Clean the outside of the housing before opening (dirt on the lid falls in).
3. Open (the bowl unscrews, or the lid bolts off); note how the element sits (bypass valve on top, seal side); remove the old element into a bag; **look at it** (metal glitter = a pump or a cylinder dying; black sludge = oxidised oil; water gel = water; fibres = a breather failing).
4. Clean the bowl and the seat with a lint-free wipe (no rags that shed); inspect the bowl O-ring/seal and replace it (most kits include it); lubricate it with clean system oil.
5. **New element**: keep it in its bag until the moment of installation; check the part number and rating; seat it fully; do not touch the media with dirty gloves; the bypass/seal end the right way.
6. Close, torque the bowl by hand plus a quarter turn (or the bolts to spec); bleed the housing on start-up (the bleed screw until oil, no foam); check for leaks under pressure from a distance.
7. Reset the indicator; write the date and hours on the housing tag and the log.

Intervals: by the **indicator**, with a maximum of **6-12 months** or the machine's hours (often 500-1,000 h on mobile, annually on industrial), and **immediately** after any component failure. Fresh elements after a pump failure: run 24 hours and change again.

## Reservoir, breather and level

- **Level**: at the mark with the cylinders in the position the plate says; low level = aeration and heat; too high = spills and foaming against the return.
- **Breather**: the tank breathes in air every time a cylinder extends; in a wet plant that air carries water: a **desiccant breather** with a check valve (or a sealed reservoir with a bladder); replace on colour change.
- **Cleaning**: annually or at the oil change: drain, open the clean-out cover, wipe the bottom and the baffles (sludge, water, metal), check the suction strainer and the return diffuser; never wash the tank with rags that shed; a light film of the system oil on the walls, not solvent.
- Return line **below** the oil level (splashing above it aerates); the baffle between return and suction; the tank sized for 2-3× the pump's gpm on industrial units (dwell time to cool and settle).
- **Temperature**: 110-140°F normal; over 160°F the oil oxidises fast (halves its life every 18°F), seals harden; check the cooler.

## Fluid selection

| Type | Use | Notes |
|---|---|---|
| **AW (anti-wear) mineral hydraulic oil**, ISO VG 32 / **46** / 68 | Industrial and mobile, general | The default; zinc (ZDDP) anti-wear; VG by the pump maker's viscosity window at the operating temperature (vane pumps: 15-70 cSt; piston: 10-160; gear: 10-300) |
| High-VI / multigrade (HVI, HM) | Outdoor, wide temperature range | Keeps viscosity in range from −20 to 200°F |
| **R&O (rust and oxidation), no AW** | Some old systems, turbines | Not for vane pumps at high pressure |
| Zinc-free (ashless) AW | Silver-plated components, some servo valves, environmental | |
| Water-glycol (HFC) | Fire-resistant (foundries, steel) | Different pump ratings (derated), no zinc, EPDM/Viton seals, water content monitored |
| Phosphate ester (HFD) | Fire-resistant (turbines, some presses) | Viton/PTFE seals only, special paints; skin irritant |
| Biodegradable (HETG vegetable, HEES synthetic ester) | Environmentally sensitive | Water and temperature sensitive (vegetable); seal compatibility |
| Food grade H1 | Food plants | |
| Engine oil (SAE 10W, 15W-40) | Mobile equipment specified for it (Cat HYDO, some tractors) | Only where the maker says |

Never mix types (AW and water-glycol gel; ester and mineral foam); when changing, drain, flush and change the filters. The viscosity index and the pour point matter on cold starts (a piston pump starting on ISO 68 at 20°F cavitates: heaters, or a lower VG/HVI oil).

## Sampling for a particle count

1. **Where**: from a live line (a sampling valve or test point on the return line before the filter, or the pressure line) with the system **running at temperature**; never from the drain plug (the sludge) or the fill port (settled top oil).
2. Flush the sampling valve (5-10 times the dead volume into a waste bottle), then fill the **clean sample bottle** (certified clean, ISO 3722) to 3/4, cap immediately; never open the bottle until the moment of filling; no hoses lying on the floor.
3. Label: machine, point, date, hours, oil type, filter changes, any event. Same point, same way every time: a trend is worth more than one number.
4. Lab or a portable counter (in-line or bottle): read the ISO code, water (ppm or %), viscosity, wear metals, additive levels (see [oil analysis and sampling](/article/oil-analysis-and-sampling)).
5. Act: a code two steps above target = find the ingress (breather, wiper seals, a failing component) and polish with the cart; a rising iron/copper trend = a pump or a valve wearing.

## Flushing after a failure

A failed pump or motor spreads metal through the whole system; a new pump installed into it fails in weeks.

1. Drain the reservoir completely; **clean it by hand**; drain every cylinder, accumulator (bleed first), cooler and low point; remove and clean or replace every filter element and the suction strainer; blow out lines that can be disconnected (from the component end back to the tank).
2. Inspect valves for debris (remove the spools of the directional valves near the failed pump; flush the manifolds); replace any servo/proportional valve that has ingested metal, or send it for service.
3. Fill with **filtered** oil (through the cart at 3-5 µm) to the level; install flushing elements (coarser, high-capacity) or use the normal ones and expect to change them 2-3 times.
4. **Flush**: run the system at low pressure (the relief backed off, or with the actuators bypassed with jumper hoses) at full flow, warm, with the filter cart in the kidney loop, **turbulent flow** for 2-4 hours; cycle the actuators with no load; change elements when the indicators show; repeat until a particle count meets the target (typically two or three element changes).
5. Restore the settings, refit the filters with new elements, sample after 24 hours of normal running and again at a week.

## Water and air

| Sign | Water | Air (aeration) |
|---|---|---|
| Oil looks | Milky/cloudy (free water over about 0.1%), or dark with varnish (dissolved water speeds oxidation) | Foam on the tank, oil looks light and bubbly, spongy actuators |
| Sound | Pump noise, corrosion later | A pump **whine/rattle** (like cavitation), erratic motion |
| Cause | A cooler leak (water-cooled), condensation through the breather, washdown, rain into the fill cap, a hydraulic press with water contact | A suction leak (a loose fitting sucks air without leaking oil), low level, a return above the oil, a leaking shaft seal on the pump, the wrong oil (poor air release), too small a tank |
| Limit | **< 200-500 ppm (0.02-0.05%)** for most systems; < 0.1% is visible | Air release under 10 minutes for the oil |
| Cure | Find the source; **vacuum dehydration** or a water-absorbing element or a centrifuge for free water; a drain of the tank bottom (water sinks) weekly; a desiccant breather; the oil replaced if it has emulsified | Tighten/replace suction fittings (test with a smear of grease on the joint: the noise stops), raise the level, submerge the return, replace the pump's shaft seal, check the breather is not plugged (a vacuum in the tank pulls air past seals) |
| Crackle test | A drop of oil on a hot plate at 300°F: crackling = water | |

## Common mistakes

- Filling from a drum with a dirty pump and a bucket: the new oil is dirtier than the old.
- A 10 µm suction filter "for extra protection": the pump cavitates and dies.
- Running with the bypass indicator red for six months.
- The breather cap replaced with a bolt, or a rag in the fill hole.
- Sampling from the drain plug and concluding the system is filthy.
- New pump straight into a system full of the old pump's metal.
- Topping up with the wrong oil type.

## Related

- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
- [Oil analysis and sampling](/article/oil-analysis-and-sampling)
- [Oil viscosity and selection](/article/oil-viscosity-and-selection)
- [Hydraulic hose assembly and fittings](/article/hydraulic-hose-assembly-and-fittings)
- [Cylinder repair and seal kits](/article/cylinder-repair-and-seal-kits)
