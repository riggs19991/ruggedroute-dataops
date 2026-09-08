---
title: "Air Compressors: Reciprocating, Rotary Screw and Vane Types, Controls, Oil and Filters, Dryers and Dew Point, Receiver and Safety Valve Rules, the PM Schedule by Interval, Condensate and Leak Surveys, Troubleshooting and Safety"
slug: air-compressors-pm
category: pumps-seals
kind: procedure
manufacturer: "Ingersoll Rand / Quincy / Sullair / Atlas Copco / Kaeser (generic)"
model_numbers: ["Ingersoll Rand T30", "IR 2545", "Quincy QT", "Quincy QGS", "Sullair ES", "Atlas Copco GA", "Kaeser SK", "Gardner Denver"]
tags: [air compressor, compressor maintenance, compressor PM, reciprocating compressor, rotary screw compressor, screw compressor, compressor oil, compressor oil change, air filter compressor, separator element, air dryer, refrigerated dryer, desiccant dryer, dew point, receiver tank, receiver drain, safety valve compressor, pressure switch, load unload, compressor belts, compressor overheating, air leaks, leak survey, condensate, compressor troubleshooting, compressed air safety, cfm psi]
source: "Ingersoll Rand, Quincy and Sullair operator and maintenance manuals (PM intervals, oil types and change hours, separator and filter service); Atlas Copco Compressed Air Manual; Compressed Air Challenge (US DOE) best practices; ASME Section VIII / National Board (receiver inspection and safety valve rules); OSHA 1910.169 (air receivers) and 1910.242(b) (30 psi cleaning rule)."
summary: "What each compressor type is and how it is controlled, the oil and filter rules that decide its life, how dryers and receivers work and how they fail, the PM schedule by daily, weekly, monthly, quarterly and annual items with the typical hours, the condensate and leak surveys that save the most money, the troubleshooting table, and the safety rules for receivers, safety valves and compressed air on people."
---

## Types

![Reciprocating and screw compressors with the receiver](/img/pumps-seals/compressor-types.svg)

*Reciprocating and screw compressors with the receiver*

| Type | How | Where | Character |
|---|---|---|---|
| **Reciprocating (piston), single-stage** | One or more cylinders compress to about 125-135 psi | Small shops, 1-15 hp, intermittent | Cheap, noisy, hot; duty cycle **50-60%**: needs rest; oil carryover |
| **Reciprocating, two-stage** | First stage to 30-50 psi, intercooler, second stage to 175 psi | 5-30 hp shop compressors (IR T30, Quincy QT), high pressure | Cooler, efficient at 175 psi; duty cycle to 75-100% on industrial models |
| **Rotary screw, oil-flooded** | Two meshing rotors in an oil-flooded chamber; oil seals, cools and lubricates; a **separator** removes the oil from the air | 10-500 hp plant air, 100-125 psi, **100% duty** | Continuous, quiet, needs its oil and separator cared for; controls (load/unload, modulation, VSD) decide the energy use |
| Rotary screw, oil-free | Timing gears keep the rotors apart; two stages | Food, pharma, electronics | Expensive, hot, oil-free air |
| Rotary vane | Vanes in an eccentric rotor, oil-flooded | 5-50 hp | Simple, low speed, long life |
| Centrifugal | Turbo impellers | 300+ hp | Plant-scale, oil-free |
| Scroll | Orbiting scroll, oil-free | Small, lab | Quiet |

Ratings: **cfm** (delivered air, at 100 psi typically; about 4-5 cfm per hp for screws, 3-4 for pistons), **psi**, and the tank size. Air tools want **90 psi at the tool**; every 2 psi above the needed pressure costs about 1% of the compressor's power, and every 10°F of hotter intake air raises the power about 2%.

## Controls

- **Pressure switch (start/stop)**: pistons; cut-in/cut-out (e.g. 100/125 psi); the differential and the receiver size decide the starts per hour (motors want under 6-10 starts/h).
- **Load/unload**: screws run continuously, an inlet valve closes and the sump blows down to unload (the compressor idles at about 25-30% of full power); a timer stops it after an unloaded period ("auto dual").
- **Modulation (inlet throttling)**: the inlet valve throttles to match demand; simple but wasteful below 70% load.
- **VSD (variable speed)**: the motor speed follows demand; the most efficient for a variable load; needs the air-end's minimum speed respected.
- **Sequencers** on multiple compressors; a **pressure/flow controller** and a large receiver let the compressors run at a lower pressure.

## Oil and filters

| Item | Reciprocating | Rotary screw |
|---|---|---|
| Oil | Compressor oil (non-detergent mineral ISO 100 / SAE 30, or a synthetic diester/PAO compressor oil); **never automotive engine oil** (detergents foam and carbonise the valves) | The maker's screw compressor fluid (synthetic PAO/diester/PAG blends; food grade H1 where needed); **do not mix types** (varnish) |
| Oil change | **500 h mineral / 1,000-2,000 h synthetic**, or 3-6 months; more often in dust or heat | **2,000 h mineral, 4,000-8,000 h synthetic** (the maker's hours; oil analysis extends); or annually |
| Oil level | Sight glass, midpoint, checked **stopped** | Sight glass, checked at the maker's condition (some running unloaded, some stopped after 5 min) |
| Air filter | Every 500 h or when the indicator shows; blow out from the inside weekly in dust; never run without one (dust scores the cylinders) | Element per the differential indicator or every 1,000-2,000 h; **never** run without it (the air-end is scrap in hours) |
| Oil filter | (Splash-lubricated pistons have none; pressure-lubricated: with the oil) | Every oil change or per the ΔP indicator (1,000-2,000 h) |
| **Separator element** (screw) | | Every **4,000-8,000 h** or when the ΔP across it exceeds about 10-15 psi, or when oil carryover appears downstream; a plugged separator raises the discharge temperature and the power; a torn one puts oil in the plant air |
| Valves (piston) | Inspect **annually** or 2,000 h: broken reeds/plates, carbon; a compressor that takes longer to fill has a valve problem | |
| Intake and discharge temperature | Piston discharge 250-350°F normal at the head | Screw discharge (air-end) **170-200°F** normal; **trips at about 225-235°F**; high temperature = dirty cooler, low oil, plugged separator, hot room, a thermostatic valve stuck |

## Dryers and air treatment

Compressed air at 100 psi holds water: a 100 cfm compressor in a warm humid shop makes **10-20 gallons of water a day**. The chain: aftercooler (cools the air to near ambient, condenses most of the water) → **moisture separator with an automatic drain** → receiver (drain) → **dryer** → filters (particulate, coalescing for oil, activated carbon for odour) → distribution with drip legs.

| Dryer | Dew point | Notes |
|---|---|---|
| **Refrigerated** | **35-40°F (2-4°C) pressure dew point** | The plant standard; cannot go below freezing; needs its condenser coil cleaned monthly and its drain working; a dryer that ices up is undersized or has a control fault |
| Regenerative desiccant (heatless, heated, blower) | −40°F to −100°F | Instrument air, outdoor lines, paint; uses **10-15% of the air** to purge (heatless); desiccant replaced every 2-5 years; needs a pre-filter (oil kills desiccant) and an after-filter (dust) |
| Membrane | 35°F to −40°F | Point of use |
| Deliquescent | 20°F below inlet | Cheap, tablets consumed |

Filters: **particulate (5 µm) → coalescing (0.01 µm oil aerosol) → carbon** (vapour); change elements at the ΔP indicator or annually; **auto drains** on every filter bowl and separator: check them daily (a stuck drain is a bowl full of water into the line).

## Receiver and safety valve

- The **receiver** (ASME Section VIII stamped, the nameplate says MAWP and the National Board number) is a pressure vessel: it must have a **safety valve set at or below the MAWP**, a **pressure gauge**, a **drain** at the bottom, and it must be **inspected** (external visually every year, internal/ultrasonic thickness per the jurisdiction, typically 3-5 years); a receiver that shows rust streaks at the seams, has a corroded bottom head, or has been welded on by anyone is a hazard: it is the biggest energy store in the shop. OSHA 1910.169 covers it. Wet (before the dryer) and dry (after) receivers: a receiver of 1-2 gallons per cfm smooths the demand and reduces cycling.
- **Drain the receiver daily** (manual) or fit an **automatic drain** (timer or zero-loss) and **check it works** weekly; a receiver with a foot of water in it has lost capacity and is rusting from the inside.
- **Safety valve**: **never adjust, plug, or "fix" it**; test by lifting the ring **monthly** (the maker's manuals and many insurers say monthly or quarterly; some plants trip-test annually with a gauge); it must reseat; replace with the same set pressure and capacity if it weeps or does not reseat; a safety valve that has never been lifted in five years is likely stuck: replace it.
- Pressure switch and the compressor's own unloader/relief are **not** substitutes for the receiver's safety valve.

## PM schedule (typical; the compressor's manual governs)

| Interval | Reciprocating | Rotary screw | Both |
|---|---|---|---|
| **Daily** | Oil level; drain the receiver; listen (knocks, valve clatter) | Oil level; discharge temperature and pressure on the display; drains; listen | Check the auto drains, dryer dew point/temperature, filter bowls, any leaks, the fault log |
| **Weekly** | Air filter check; belts (tension, cracks); clean the cylinder fins and the intercooler; check the unloader operation | Air filter indicator; separator ΔP; cooler face clean; the cabinet filter mats; belts on belt-drive units | Leak walk-round; safety valve visual; condensate handling |
| **Monthly** | Safety valve lift; check the head and fittings for leaks; check the pressure switch settings; oil for water/colour | Safety valve lift; cooler cleaning (blow out with air, opposite to the flow); check the minimum pressure valve and the blowdown; oil sample for large units | Dryer condenser cleaned; filter elements per indicator; motor greasing per the [motor table](/article/regreasing-intervals-and-quantities); belt tension |
| **Quarterly (500 h)** | **Oil change** (mineral); air filter; belt tension; valve check by fill-time test | Air filter element; oil sample; check the inlet valve and blowdown valve; tighten electrical connections | Receiver drain valve exercised; check-valve function (the receiver holds pressure with the compressor off) |
| **Annual (2,000-4,000 h)** | Valves inspected/replaced; piston rings on high-hour units; gaskets; motor bearings; pressure switch calibration; receiver inspection | **Oil change** (mineral at 2,000, synthetic at 4,000-8,000); oil filter; **separator**; air-end bearing check by vibration; thermostatic valve; shaft seal; motor bearings; cooler chemical cleaning; safety valve test/replace; **receiver inspection** | Dryer: refrigerant charge, drains, desiccant; the whole air system leak survey with an ultrasonic detector; controls calibration |
| 20,000-40,000 h | Complete overhaul | Air-end rebuild or exchange (bearings) | |

## Leak and condensate surveys

- A **1/8" hole at 100 psi leaks about 26 cfm** (about 6 hp of compressor, several thousand dollars a year); typical plants leak **20-30%** of their air. Survey with an **ultrasonic leak detector** (or soapy water) at every fitting, coupling, hose, drain, and at the tool ends; tag, fix, re-survey; quick-connect couplers and old hoses are the usual offenders.
- Condensate from oil-flooded compressors is **oily water**: it goes through an **oil/water separator** and the oil to waste oil; never down the drain.
- Piping: a loop main, drip legs at low points with drains, take-offs from the **top** of the main, sized for under 3-5 psi drop (as a guide, at 100 psi over 100 ft with a small drop: 3/4" pipe about 20-30 cfm, 1" about 50, 1-1/2" about 120, 2" about 250 cfm; use a piping chart for real design).

## Troubleshooting

| Symptom | Causes |
|---|---|
| Compressor runs but pressure builds slowly / never reaches cut-out | Leaks (the biggest), intake filter plugged, **valves** (piston) broken or carboned, worn rings, the unloader stuck open, a screw's inlet valve not opening, the minimum pressure valve, wrong belt speed, demand higher than the supply |
| Runs continuously | Demand ≥ capacity, leaks, the pressure switch/controller setting, the unloader |
| Cycles too often (short cycling) | Receiver too small, water in the receiver, the differential set too narrow, a leak |
| **High discharge temperature / trips on temperature** (screw) | Dirty cooler, low oil, wrong oil, plugged separator or oil filter, thermostatic valve, hot room (over 104°F), fan failure, a restricted intake |
| **Oil in the air lines** (screw) | Separator element torn or plugged, scavenge line plugged, oil level too high, wrong oil (foaming), the minimum pressure valve |
| Oil consumption (piston) | Rings and cylinder worn, over-filled, crankcase breather, running too hot, the wrong oil |
| Water in the lines | Drains stuck, aftercooler dirty, dryer overloaded or failed (check the dew point), no dryer, intake in a humid spot |
| Knocking (piston) | Loose flywheel or pulley, bearing, wrist pin, a broken valve, carbon on the piston top |
| Safety valve popping | Pressure switch failed closed, the unloader failed, wrong set point; **never** answer it by changing the valve |
| Motor overloads | Low voltage, belts too tight, pressure too high, the unloader not unloading at start, a seized air-end/cylinder, the wrong oil in cold weather |
| Noisy screw, vibration | Air-end bearings (vibration monitoring on the air-end; 40,000 h life), coupling, mounts |

## Safety

- **Never use compressed air to clean clothing or blow off skin**: 100 psi injects air under the skin (embolism, death); OSHA 1910.242(b) limits cleaning nozzles to **30 psi dead-ended** with chip guarding and PPE.
- Lockout: the electrical supply **and** the stored air: isolate and **bleed the receiver and the lines to zero** on the gauge before opening anything; the screw compressor's sump holds pressure after stopping (wait for the blowdown, check the sump gauge reads zero before opening the oil fill).
- Hot surfaces (cylinder heads 300°F, screw air-end 200°F); guards on belts and couplings; hearing protection (85-95 dBA).
- Receiver rules above; a receiver with a **welded-on bracket or a patch** is condemned; never move a receiver under pressure.
- Hoses: whip checks on 3/4" and larger, claw couplings pinned; a burst hose is a whip.
- Breathing air is **not** plant air (CO, oil): only from a breathing-air system with a CO monitor.

## Related

- [Pneumatic systems, FRL and air tools](/article/pneumatic-systems-frl-and-cylinders)
- [Regreasing intervals and motor greasing](/article/regreasing-intervals-and-quantities)
- [V-belt drive installation and tensioning](/article/v-belt-drive-installation-and-tensioning)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [PM checklists](/article/pm-checklists)
