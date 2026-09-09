---
title: "Welding Machine Setup: CC vs CV, Duty Cycle Math, Input Power and Breakers, Welding Cable Size Chart, Ground Clamp Placement and Arc Blow"
slug: machine-setup-and-duty-cycle
category: welding
kind: reference
tags: [duty cycle, welding cable size, cable chart, 1/0 cable, 2/0 cable, welder breaker size, input amps, engine drive welder, generator welding, constant current, constant voltage, ground clamp, work clamp, arc blow, extension cord welder, 240V welder, multi process]
source: "Manufacturer nameplates and manuals (Miller, Lincoln, ESAB); NEC Article 630 (arc welders); welders-supply.com welding cable size chart (60% duty cycle, 4 V drop basis); IEWC/TPC ampacity tables."
summary: "The electrical side of setting up any welder: which output type each process needs, how to read and use the duty-cycle rating, what input circuit and breaker a machine wants, the cable size chart by amperage and total lead length, where to put the ground and how to beat arc blow."
---

## Output type by process

| Process | Output | What you set | What the machine holds |
|---|---|---|---|
| Stick (SMAW), TIG (GTAW), carbon-arc gouging | **Constant current (CC)** | Amperage | Amperage roughly constant as arc length changes |
| MIG (GMAW), flux-core (FCAW), metal-cored, SAW (most) | **Constant voltage (CV)** | Voltage and wire feed speed | Voltage constant; amperage follows wire feed speed |

Multi-process machines switch between them; welding MIG on CC or stick on CV works badly. A CC engine drive can run a **voltage-sensing suitcase feeder** for flux-core in the field with reduced arc quality; a CV/CC engine drive (Bobcat, Ranger, Trailblazer) does both properly.

## Duty cycle

The nameplate rates output at a **duty cycle**: the percentage of a **10-minute** period the machine can weld at that amperage before it must cool.

![Duty cycle falls with the square of the current ratio](/img/welding/duty-cycle.svg)

*Duty cycle falls with the square of the current ratio*

```
Allowed arc time per 10 min = duty cycle × 10 min
Example: 200 A at 60% → 6 minutes welding, 4 minutes resting, repeating
```

At a different amperage the duty cycle changes roughly with the square of the current ratio:

```
Duty cycle at I₂ ≈ rated duty cycle × (I_rated ÷ I₂)²
Example: rated 250 A at 40%. At 160 A: 40% × (250/160)² = 40% × 2.44 = 98% → continuous.
At 300 A: 40% × (250/300)² = 28% → under 3 minutes in 10.
```

Thermal overload lights mean you exceeded it; let the fan run (do not switch off) until it clears. Ratings are at 104°F (40°C) ambient; a hot shed or sun on the machine shortens it.

## Input power

Read the nameplate: **I1max** (maximum input amps) and **I1eff** (effective, for wiring). NEC Article 630 lets a dedicated welder circuit breaker be sized up to 200% of the rated primary current because the load is intermittent; the conductor is sized from I1eff × duty-cycle multiplier. Typical, but always check the manual:

| Machine class | Input | Typical circuit |
|---|---|---|
| 120 V 140 A MIG / 90 A stick inverter | 120 V 1-phase, 20 A | Dedicated 20 A circuit; extension cords 12 AWG max 25 ft |
| 200-250 A MIG (Millermatic 211/252, Power MIG 210/256) on 240 V | 240 V 1-phase, 20-50 A | 30-50 A breaker, 10-8 AWG, NEMA 6-50 receptacle |
| 200 A stick/TIG inverter (Maxstar 210, Dynasty 210) | 120/240 V | 30 A at 240 V |
| 300-350 A TIG (Dynasty 280/350, Syncrowave 250) | 240 V 1-ph or 3-ph | 50-100 A |
| 350-450 A industrial MIG (Deltaweld 350, Power Wave) | 230/460 V 3-phase | 50-60 A at 460 V |
| Engine drives (Bobcat 225/250, Ranger 225) | Gasoline/diesel | Provide 8-12 kW auxiliary; use the welder's own outlets for grinders |

Generator welding: a stick/TIG inverter needs a **clean** generator with ≥ 1.5× the welder's kVA rating; small "contractor" generators with poor waveform can damage inverters. Extension cords on 240 V: 8 AWG for 50 ft on a 50 A machine; voltage drop shows up as a weak arc and tripping.

## Welding cable size chart

Total circuit length = electrode lead **plus** work lead. Copper welding cable, 60% duty cycle, about 4 V drop (welders-supply chart). Bigger is always fine.

![Cable size by output and total lead length](/img/welding/cable-size-chart.svg)

*Cable size by output and total lead length*

| Machine output | Up to 50 ft total | 50-100 ft | 100-150 ft | 150-200 ft |
|---|---|---|---|---|
| 100 A | #4 | #4 | #2 | #2 |
| 150 A | #2 | #2 | #2 | 1/0 |
| **200 A** | #2 | 1/0 | 2/0 | 4/0 |
| **250 A** | 1/0 | 2/0 | 3/0 | 4/0 |
| **300 A** | 2/0 | 3/0 | 4/0 | 4/0 |
| 400 A | 3/0 | 4/0 | 4/0 | two 2/0 in parallel |

Ampacity of copper welding cable, continuous-ish: #4 ≈ 85-160 A, #2 ≈ 115-200, 1/0 ≈ 150-300, 2/0 ≈ 200-400, 3/0 ≈ 250-500, 4/0 ≈ 300-600 (ranges reflect 30-100% duty cycle in different makers' tables).

Signs your cable is too small or too long: cable warm to the touch, arc weaker at the end of long leads, machine set higher than the chart to get the same result, dinged lugs getting hot. Check lug crimps and the ground clamp spring; a loose lug is a resistor.

Metric: #2 ≈ 35 mm², 1/0 ≈ 50 mm², 2/0 ≈ 70 mm², 3/0 ≈ 95 mm², 4/0 ≈ 120 mm².

## Ground (work) clamp

![Ground clamp on the part being welded, never across a bearing](/img/welding/ground-clamp-placement.svg)

*Ground clamp on the part being welded, never across a bearing*

- On **clean bare metal** on the piece being welded, as close to the arc as practical.
- Never let welding current cross a **bearing, bushing, gear mesh, chain, hinge, slewing ring or hydraulic cylinder rod**: it arcs across the contact points and pits them (fluting). On rotating machinery clamp to the shaft or the same casting you are welding; on a vehicle disconnect the battery and clamp near the weld.
- Never through the machine table's grounded frame, threaded rod or a C-clamp with paint on it.
- Aluminium and stainless: dedicated clean clamp face.
- Check: if the clamp or the cable gets warm, or the arc improves when you move the clamp, the connection was bad.

## Arc blow

On DC the magnetic field around the arc gets pushed by the field in the plate: the arc leans, wanders, spatters and blows out near the ends of joints, in corners, on magnetised steel and with the ground far away.

| Fix | How |
|---|---|
| Move the ground | To the other end, or to the middle of the joint; weld **away** from the ground |
| Change angle | Tilt the electrode against the blow direction |
| Shorten the arc | Tight arc, faster travel, smaller electrode |
| Run-off tabs | On plate ends |
| Switch to AC | AC cancels the effect; use an AC-rated rod (E6011, E7018 AC) |
| Demagnetise | Wrap the ground cable around the part several turns; magnetised shafts need a demagnetiser |
| Steel blocks | Place a steel bar at the end of the joint to carry the flux |

## Daily checks before striking an arc

![Daily checks: leads, clamps, gas, feeder, fan intake](/photos/welding/mig-machine.jpg)

*Daily checks: leads, clamps, gas, feeder, fan intake. Photo: Luke Haggart, CC BY-SA 4.0, via commons*

1. Cables: cuts, exposed copper, warm lugs.
2. Ground clamp jaws clean and spring strong.
3. Electrode holder insulation intact; MIG gun trigger and nozzle.
4. Gas: cylinder chained, flow set while flowing, no leaks.
5. Machine vents clear; blow out dust monthly (compressed air, machine off).
6. Water-cooled torches: coolant level and flow before the arc.
7. Fire watch, extinguisher, fumes, PPE: see [welding safety](/article/welding-safety-fumes-and-ppe).

## Related

- [Stick (SMAW) setup](/article/smaw-stick-setup)
- [MIG (GMAW) setup](/article/gmaw-mig-setup)
- [TIG (GTAW) setup](/article/gtaw-tig-setup)
- [Welder maintenance and consumables](/article/welder-maintenance-and-consumables)
- [Electrical safety for mechanics](/article/electrical-safety-for-mechanics)
