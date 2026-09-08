---
title: "Rigging Basics: Sling Angles, Hitches, Load Calculation and Sling Inspection"
slug: rigging-basics-sling-angles-and-hitches
category: rigging
kind: reference
tags: [rigging, sling angle, sling angle factor, choker hitch, basket hitch, vertical hitch, wire rope sling, synthetic sling, chain sling, shackle, WLL, load calculation, hand signals, D/d ratio]
source: "ASME B30.9 (slings), B30.26 (rigging hardware), B30.10 (hooks); OSHA 1910.184; manufacturer capacity charts."
summary: "The math and rules behind safe lifts: estimating load weight, sling-angle load factors (never below 30 degrees), how each hitch changes capacity, D/d ratio, shackle and hook rules, pre-use sling rejection criteria, and basic crane hand signals."
---

## Estimate the load

Read the nameplate or drawing. If you must calculate:

```
Weight = Volume × Density
Steel   = 490 lb/ft³ (0.283 lb/in³)
Concrete = 150 lb/ft³
Water   = 62.4 lb/ft³ (8.34 lb/US gal)
```

A steel plate 4 ft × 8 ft × 1 in: 4 × 8 × (1/12) ft³ × 490 = **1 307 lb**. Round up. Add the weight of rigging.

## Centre of gravity

The hook must be directly above the CG or the load will swing and tilt when it leaves the ground. Lift an inch, stop, look, adjust.

## Sling angle factor

When sling legs are not vertical, each leg carries **more** than its share. The angle is measured **from the horizontal**.

![Sling angle factors and the three hitches](/img/rigging/sling-angles-and-hitches.svg)

*Sling angle factors and the three hitches*

| Horizontal sling angle | Load factor (multiply per-leg share by this) |
|---|---|
| 90° (vertical) | 1.000 |
| 60° | 1.155 |
| 45° | 1.414 |
| 30° | 2.000 |
| below 30° | **do not rig** |

```
Tension per leg = (Load ÷ number of legs sharing) × load factor
```

Two-leg bridle, 2 000 lb load, legs at 45° from horizontal:
tension per leg = (2 000 ÷ 2) × 1.414 = **1 414 lb**. Each leg (and each shackle and each lifting lug) must be rated for at least that.

Rule of thumb: if each sling leg (hook to pick point) is as long as the distance between the pick points, the legs sit at 60°. Shorter legs give shallower angles. Use longer slings or a spreader bar to keep angles at 60° or steeper.

## Hitches

| Hitch | Capacity relative to the sling's vertical rating |
|---|---|
| **Vertical** (straight) | 100% |
| **Choker** | about **75-80%** (less as the choke angle tightens below 120°); use a shackle in the choke for synthetic slings |
| **Basket** (legs vertical) | **200%** |
| Basket at 60° | 200% × 1.155 factor per leg → check the chart |
| Basket at 45° | 141% (approx.) |
| Basket at 30° | 100% |

Read the capacity from the **sling tag** for the hitch you are using. A sling with no legible tag is out of service.

## D/d ratio (wire rope and synthetic)

Bending a sling around a small diameter cuts its strength. **D** = diameter of the object the sling bends around; **d** = sling diameter. Wire rope: keep D/d at **25 or more** for full rating; at D/d = 1 (a sling around a shackle pin of its own size) the rope is at roughly 50%. Synthetic round slings have similar limits; use their chart.

## Hardware

![Correct shackle loading and side-load derating](/img/rigging/shackle-loading.svg)

*Correct shackle loading and side-load derating*

- **Shackles**: use the WLL stamped on the bow. Screw-pin shackles for temporary rigging, bolt-type (with nut and cotter) if the pin could rotate. Never replace the pin with a bolt. Side-loading a shackle derates it (45° ≈ 70%, 90° ≈ 50%). Pin in the hook or the fixed eye; the running sling goes in the bow.
- **Hooks**: load in the bowl, never on the tip. Latch working. Throat opening stretched more than 5% = scrap.
- **Eyebolts**: shoulder type for angular pulls, and only to 45° with a big derating; plain eyebolts vertical only.
- **Turnbuckles, spreader bars, lifting beams**: rated and tagged.

## Sling inspection - remove from service if

**Wire rope slings**
- 10 randomly distributed broken wires in one rope lay, or 5 broken wires in one strand in one lay
- Kinks, crushing, birdcaging, core protrusion
- Corrosion pitting, heat damage (discoloured), cracked or deformed end fittings
- Diameter reduced by 1/3 of the outer wire diameter

**Synthetic web slings**
- Missing or illegible tag
- Acid/caustic burns, melting, charring, holes, cuts, snags, broken stitching
- **Red core (warning) yarns visible**
- Knots

**Alloy chain slings**
- Stretched links (measure a reach against the tag), cracks, gouges, nicks over 10% of the link diameter
- Bent, twisted or elongated links or hooks
- Never repair chain by welding; only the maker replaces links

## Lift plan (every time)

1. Weight and CG known. Rigging capacity ≥ tension per leg with the angle factor applied.
2. Sling protection at all edges (corner pads); never let a sling run over a sharp edge.
3. Tag lines on anything that can spin.
4. Nobody under the load. Clear the swing path.
5. One signal person. Standard hand signals: **hoist** = forearm vertical, index finger up, small circle; **lower** = arm down, finger down, small circle; **stop** = arm out, palm down; **emergency stop** = both arms out, palms down, swing; **boom up/down** = arm extended, thumb up/down.
6. Trial lift an inch; check balance and rigging; then proceed.

## Related

- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [SAE and metric bolt torque chart](/article/bolt-torque-chart-sae-metric)
