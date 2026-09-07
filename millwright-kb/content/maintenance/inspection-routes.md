---
title: "Inspection Routes: Building and Walking a Plant Route, What to Carry, How to Take and Record Readings, and Turning Observations into Work Orders"
slug: inspection-routes
category: maintenance
kind: procedure
tags: [inspection route, operator rounds, maintenance rounds, walkdown, route based inspection, look listen feel, IR thermometer, vibration pen, ultrasound, stethoscope, strobe, route sheet, readings log, baseline, trending, alarm limits, condition based maintenance]
source: "SMRP body of knowledge; Reliabilityweb and Plant Engineering route-based inspection guidance; ISO 17359 (condition monitoring guidelines); manufacturer maintenance manuals; ISO 20816 vibration severity zones."
summary: "How to set up an inspection route that catches failures early: deciding what goes on the route and how often, the tool kit to carry, the look-listen-feel-measure method at each machine, how to establish baselines and alarm limits, recording readings so trends are visible, and the rules for what gets fixed on the spot versus written up."
---

> A route is the cheapest condition monitoring there is: a trained person with an IR thermometer, a vibration pen and a notebook finds most bearing, belt, alignment and lubrication problems weeks before they stop production. The route only works if it is walked **on schedule, the same way, and written down**.

## Building the route

1. **List the assets** in a physical walking order (minimise backtracking; group by area and by lockout requirement).
2. **Rank by criticality**: A = stops the plant or is a safety issue with no spare (daily or each-shift checks); B = affects production, spare available (weekly); C = minor, run-to-failure acceptable (monthly).
3. For each asset write the **check points** (what, where, limit): "pump P-101 DE bearing housing: temperature < 180°F and < baseline + 20°F; vibration < 0.3 in/s; seal: no visible leak". Use the [PM checklists](/article/pm-checklists) as the starting list and cut it down to what you can actually do in the time.
4. **Mark the measuring points** on the machine (paint dot, stick-on target) so readings are repeatable: horizontal, vertical and axial on each bearing housing for vibration; a fixed spot on the housing for temperature.
5. Decide **how long** it takes (a realistic route is 1-2 hours; longer ones get skipped) and put it on the schedule with a name against it.
6. Print or load the route sheet with the **last three readings** shown beside each point so the walker sees the trend on the spot.

## What to carry

| Tool | Use | Notes |
|---|---|---|
| **IR thermometer** (or a thermal camera) | Bearings, motors, couplings, belts, gearboxes, electrical connections, steam traps | Emissivity: painted or oxidised surfaces read fine; shiny metal reads low; aim at the same spot, 1:1 spot ratio at close range (a 12:1 gun at 12 in sees a 1 in spot) |
| **Vibration pen / meter** (overall velocity in/s or mm/s) | Bearing housings, motor frames, fans | Same point, same direction, machine at normal load; see [ISO severity](/article/vibration-basics-and-iso-severity) |
| **Mechanic's stethoscope** or a long screwdriver to the ear | Bearings, gear mesh, valve chatter, cavitation | Compare ends of the same machine |
| **Ultrasonic gun** (if available) | Bearings (grease condition), air and gas leaks, steam traps, electrical arcing/corona | Ultrasound catches bearing lubrication problems earliest of all |
| Flashlight, mirror, magnet | Leaks, cracks, under guards | |
| Strobe (tachometer) | Belt slip (sheave rpm vs motor rpm), rotating parts "frozen" for a look | |
| Grease gun (labelled with the grease) and rag | Route lubrication points | Quantity by the table, not by feel |
| Tape, marker, tags | Mark findings on the machine; tag defects | |
| Route sheet / tablet, pen | The readings | |
| PPE for the area, lockout locks if any guard opens | | |

## At each machine: look, listen, feel, measure

**Look**: leaks (oil, grease, water, product: where from, how much, new or old), oil level and colour in sight glasses, breathers, guards on and secure, belt dust, rust streaks (fretting) at flanges and bolted joints, cracked welds or paint at the base, loose bolts (paint witness lines broken), foundation cracks, misaligned or rubbing parts, wet insulation, build-up on fans and pulleys, condition of hoses and cables, gauge readings versus normal, sight-glass flow, e-stops and pull cords accessible.

**Listen**: pitch and rhythm compared to last week (a rising whine, a knock at shaft speed, a grinding or hiss, chain slap, belt squeal, cavitation gravel, relief valve chatter, air leaks).

**Feel** (outside the guard, only where it is safe): vibration by hand on the housing and base (a buzz vs a shake), temperature by the back of a hand near (not on) the surface, air flow at the motor fan, pipe pulsation.

**Measure**: temperature at the marked point; vibration at the marked points; amps if a meter is on the panel; pressures and flows from the gauges; oil level; anything the route sheet asks for. Write the number, not "OK".

**Smell**: hot insulation (varnish), burning rubber (belt), overheated oil (gearbox), hydraulic oil (leak), product.

## Baselines and limits

- Take **baseline** readings on a healthy machine (after commissioning, after an overhaul, or the average of the first few readings), at normal load and temperature.
- Alarm limits: use the maker's numbers where they exist; otherwise **temperature**: alert at baseline + 20°F (11°C), act at + 40°F or an absolute 180°F on bearing housings (200°F on gearboxes); **vibration**: alert at 2× baseline or the ISO 20816 zone B/C boundary for the machine class, act at zone C/D (see the chart); **amps**: alert at 10% over baseline or unbalance over 10% between phases; **oil level**: any drop needing a top-up between routes is a leak to find.
- Rate of change matters more than the number: a bearing at 160°F that was 120°F last week is the one to watch, not the one that has run at 170°F for three years.

## Recording

- **One line per point, one column per date**: the sheet itself becomes the trend chart. Digital (CMMS route module, spreadsheet, or a photo of the sheet) is fine; a pile of unread paper is not.
- Note the **condition at the time**: load, product, ambient, speed (readings at half load are not comparable to full load).
- Anything off-limit or new: photo, tag on the machine, and a **work order** with the reading, the limit and what you think it is (see [work orders and history](/article/work-order-and-history-records)).
- Fix on the spot only what the route allows (top up oil, tighten a guard bolt, clean a breather, regrease at the scheduled quantity); anything needing lockout, parts or more than a few minutes is written up so it is tracked and the history is kept.

## Frequency by failure speed

| Failure mode | How fast it develops | Route interval |
|---|---|---|
| Lubrication starvation (bearing) | Days to weeks after the grease runs out | Weekly with ultrasound / temperature |
| Rolling element bearing fatigue | Weeks to months from first vibration sign to failure | Weekly to monthly vibration |
| Belt wear, tension loss | Weeks | Weekly listen/look, monthly measure |
| Misalignment | Seen at once by vibration; damage over months | Monthly vibration, annually check |
| Gear tooth wear | Months to years; pitting to breakage can be fast | Monthly oil/magnetic plug, quarterly vibration |
| Coupling element wear | Weeks to months; dust or rubber crumbs under the guard | Monthly look |
| Seal leak | Sudden or gradual | Each shift look |
| Structural cracks, loose bolts | Weeks | Monthly look |

## Common mistakes

- Readings taken at different points, or with the machine in a different condition, so trends are noise.
- "OK" instead of a number.
- The route done by whoever is free rather than a named person who knows what normal sounds like.
- Findings fixed quietly and not recorded, so the history never shows the repeat problem.
- Over-greasing on the route because the gun is in the hand.
- Ignoring the small stuff (a broken sight glass, a missing guard bolt, a weeping fitting) that becomes the big stuff.

## Related

- [PM checklists by equipment](/article/pm-checklists)
- [Work orders and history records](/article/work-order-and-history-records)
- [Vibration basics and ISO severity](/article/vibration-basics-and-iso-severity)
- [Thermography, ultrasound and oil analysis](/article/thermography-ultrasound-and-oil)
- [Machine vibration, noise and heat decision tree](/article/machine-vibration-noise-heat-decision-tree)
- [Lube routes and single-point lubricators](/article/lube-routes-and-single-point-lubricators)
