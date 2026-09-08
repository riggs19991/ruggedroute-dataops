---
title: "Anti-Seize and Galling: What Galling Is and Which Metals Do It (Stainless, Aluminium, Titanium), the Anti-Seize Types (Copper, Nickel, Aluminium, Moly, Ceramic, Food Grade) with Temperature Limits and Where Each Belongs and Does Not, How Anti-Seize Changes Torque (K-Factor and the Reduction), Applying It, Preventing Galling in Stainless Assemblies, and the Dissimilar-Metal Corrosion It Prevents"
slug: anti-seize-and-galling
category: fasteners
kind: chart
tags: [anti-seize, anti seize, antiseize, Never-Seez, copper anti-seize, nickel anti-seize, aluminum anti-seize, moly anti-seize, ceramic anti-seize, food grade anti-seize, galling, thread galling, stainless galling, stainless bolts seize, cold welding, K factor, nut factor, torque reduction anti-seize, lubricated torque, anti-seize torque chart, dissimilar metals, galvanic corrosion, steel bolt aluminum, exhaust bolts, spark plug anti-seize, anti-seize where not to use, brake anti-seize, high temperature bolts, anti-seize application]
source: "Bostik Never-Seez and Henkel Loctite anti-seize product data (compositions, temperature ratings, torque reduction guidance); Fastenal Technical Reference Guide (K-factors: dry 0.20, lubricated 0.15, anti-seize about 0.12-0.13); Nickel Institute and ASSDA guidance on stainless steel galling; ASTM F2329 / galvanic series references."
summary: "Galling is the cold-welding of threads that turns a stainless bolt into a rivet; anti-seize stops it and also stops corrosion locking and heat locking, but it changes the torque a bolt needs and belongs only in some places. This covers who galls and why, the anti-seize compounds and their limits, the K-factor math and a torque-reduction table, how to apply it, the assembly practice that prevents galling when you cannot use it, and the galvanic pairs that anti-seize separates."
---

## Galling

When two metal surfaces slide under pressure with no film between them, the microscopic peaks **weld** (adhesive wear); on threads the welded spots tear, the torn metal drags and welds again, and within a turn the nut is **seized solid**: it will not go on or come off, and the fastener is cut off. Metals that gall: **stainless steel** (300 series worst: it work-hardens and its oxide film is thin), **aluminium, titanium, nickel alloys**, and soft or unplated steel on itself under heavy load. It is worse with: **stainless on stainless of the same grade**, fine threads, high tightening speed (an impact wrench: the heat of friction), high preload, rough or damaged threads, a dry assembly, and high temperature.

![How galling starts and how anti-seize changes torque](/img/fasteners/galling-and-anti-seize.svg)

*How galling starts and how anti-seize changes torque*

Prevent galling by: **lubricating the threads** (anti-seize is the lubricant of choice), **slow** tightening (hand tools, no impacts on stainless), **dissimilar hardness or grade** (a 304 bolt with a 316 nut, or a stainless bolt with a bronze or a coated/plated nut), rolled (not cut) threads, coarse threads over fine, a lower preload where the design allows, and **not** forcing a fastener that starts to bind (stop, back off, lubricate).

## Anti-seize types

| Type | Base | Temperature | Use | Do not use |
|---|---|---|---|---|
| **Copper (copper-graphite)** (Never-Seez Regular, Loctite C5-A) | Copper flakes and graphite in a grease | to **1,800°F (980°C)** | The general purpose: steel bolts, exhaust and manifold studs, pipe threads, spark plugs (older practice), chain and pins, slow slides | **Not on stainless in corrosive or high-temperature service** where copper can cause stress corrosion (chlorides) or in nuclear/some chemical plants; not near oxygen systems; not on aluminium in salt water (galvanic) |
| **Nickel** (Never-Seez Pure Nickel Special, Loctite N-5000/N-7000) | Nickel flakes and graphite | to **2,400°F (1,315°C)** | **Stainless steel, nickel alloys, titanium**, high-temperature bolting (turbines, furnaces), where copper is prohibited; the safe choice on stainless | Where a copper-free/nickel-free spec applies (some chemical) |
| **Aluminium (aluminium-graphite)** | Aluminium flakes | to 1,600°F | General purpose, some marine (no copper), aluminium fittings | |
| **Moly (molybdenum disulphide)** | MoS₂ in a grease | to 750°F (dry film higher) | Heavy-loaded threads and sliding surfaces, press fits, splines; automotive "moly assembly lube" | High temperature (it oxidises and abrades above 750°F) |
| **Ceramic / metal-free (Never-Seez Mariner, Loctite LB 8009 metal-free, ceramic paste)** | Ceramic/graphite/other | to 2,600°F (some) | Brakes and wheel studs (no metal to promote corrosion or conduct), stainless in marine, where any metal is prohibited (nuclear, chemical, aerospace), spark plugs (modern practice: metal-free) | |
| **Zinc** | Zinc | to 750°F | Galvanised and aluminium fittings | |
| **Food grade (NSF H1)** (Never-Seez Food Grade, Loctite LB 8014) | White/PTFE/aluminium in H1 base | to 1,500°F | Food plants | |
| **Graphite / dry film** | | | Threads in extreme heat, oxygen (special oxygen-compatible products only) | |
| Marine grade / anti-corrosion (Tef-Gel, Lanocote, Never-Seez Mariner) | PTFE/lanolin | to 300-500°F | Stainless bolts in aluminium on boats and washdown equipment (galvanic separation) | Hot |

Read the label for the **temperature** and the **"do not use with"** list; in doubt on stainless: **nickel**.

## What anti-seize does to torque

Torque tables assume a **friction (K, nut) factor**: **dry, plain steel about 0.20**; lubricated with oil about 0.15-0.18; **anti-seize about 0.12-0.15** (some products 0.10). The same torque with a lower K stretches the bolt **more**: a bolt torqued to a dry chart value with anti-seize on it is over-loaded by 30-50% and can yield or strip the thread.

```
   T = K × D × F           T = torque, D = bolt diameter, F = clamp (preload)
   for the same F:  T_antiseize = T_dry × (K_antiseize ÷ K_dry) = T_dry × (0.13 ÷ 0.20) ≈ 0.65 × T_dry
```

So **reduce the dry torque by about 25-35%** with anti-seize (the maker's guidance: Never-Seez says "reduce the torque by up to 30%"; Loctite gives a K of 0.13-0.15 for its products), unless the chart you use is already a lubricated chart. If the specification says "lubricated", it means with the specified lubricant and its K: read it.

| Bolt (grade 5, coarse) | Dry torque (K = 0.20) | With anti-seize (K = 0.13-0.15): about 65-75% |
|---|---|---|
| 1/4-20 | 8 ft-lb | 5-6 |
| 5/16-18 | 17 | 11-13 |
| 3/8-16 | 30 | 20-22 |
| 7/16-14 | 50 | 32-37 |
| **1/2-13** | **75** | **50-56** |
| 9/16-12 | 110 | 72-82 |
| 5/8-11 | 150 | 100-112 |
| **3/4-10** | **260** | **170-195** |
| 7/8-9 | 430 | 280-320 |
| 1-8 | 640 | 415-480 |
| Grade 8 | 1.4 × the grade 5 values | The same reduction |

(Full dry tables in [bolt torque chart](/article/bolt-torque-chart-sae-metric).) Where the preload matters (flanges, couplings, structural, machinery hold-downs), use the **lubricated** column of the applicable chart or the maker's K; a torque-angle or a stretch method removes the friction guesswork.

## Applying it

1. Threads **clean** (a wire brush, solvent, dry) and undamaged (chase them); anti-seize on dirt is a grinding paste.
2. A **thin, even film** on the **male threads** that will be engaged (a brush from the can; the brush-top cans are the right tool), and a film **under the nut face / bolt head** if the torque spec is for a lubricated head (usually it is: the head friction is half the total); a dab on a stud's coarse end going into a casting; on pipe threads a film around the male thread (anti-seize is a thread **lubricant and anti-corrosion** compound, not a rated sealant; pipe threads that must hold pressure still get a sealant, though plants often use anti-seize alone on low-pressure, high-temperature joints that must come apart).
3. **Not on the first thread** into a blind hole full of it (the hydraulic lock cracks castings); not gobbed (it squeezes out and attracts dirt; excess wiped).
4. Torque per the reduced/lubricated value; note "anti-seize" on the work order.
5. Keep it off brake friction surfaces, electrical contacts (some are conductive, some are not: use a conductive grease where continuity matters), O-rings and seals (petroleum base), and the gasket faces.
6. Hands: it stains and it is a nuisance-to-hazardous mix (copper, nickel are skin sensitisers): gloves.

## Where anti-seize belongs

| Use | Why |
|---|---|
| **Stainless bolts and nuts** (all of them, every time) | Galling |
| **Steel bolts into aluminium** (motor end bells, pump housings, gearbox covers), and stainless into aluminium | Galvanic corrosion locks them; the aluminium thread strips on removal |
| **Exhaust, furnace, boiler, dryer bolting; anything over 400°F** | Heat welds and scales the threads |
| Studs into castings (the nut end), pipe threads in high-temperature lines, gland bolts on valves | Removal years later |
| **Wheel studs** (lightly, per the vehicle maker: many say no; torque adjusted) and brake caliper slide pins/pads (metal-free) | Corrosion |
| Pins, clevis pins, hinge pins, slides, jack screws, levelling bolts, guard bolts outdoors, conveyor idler and guard bolts | Rust seizure |
| Bearing housing bolts, coupling bolts, bushing cap screws | **Only** if the maker's torque allows a lubricated value (bushing cap screws are usually specified dry or "lightly oiled": read the sheet) |
| Spark plugs in aluminium heads | Some makers say yes (metal-free), some no: the plug's maker |
| Set screws, small machine screws | No (a threadlocker instead) |
| **Threadlocked joints** | Never both: anti-seize stops the threadlocker curing |
| Structural high-strength bolts (A325/A490) | Only the lubricant the spec allows (the bolt's own wax/oil; TC bolts as supplied); anti-seize changes the tension and is not allowed unless specified |
| Torque-critical joints without a lubricated spec | Ask; use the lubricated chart |
| Oxygen service | Only oxygen-compatible products (most anti-seize is petroleum-based and a fire hazard in oxygen) |

## Preventing galling without anti-seize (stainless assemblies where nothing is allowed)

- Slow hand tightening, no impact tools; the nut started by hand and turned steadily without stopping and restarting under load.
- Different grades or hardness for the nut and the bolt (a 316 nut on a 304 bolt, a nitronic 60 or a bronze nut, a **silver-plated** nut in high-temperature nuclear/chemical service, a PTFE-coated (xylan) bolt).
- Coarse threads, rolled threads, a lower class fit, chamfered ends, no burrs.
- A dry-film lubricant approved for the service (a PTFE dry film, a molybdenum film, a wax) where a paste is not permitted.
- Never re-use a stainless fastener that has started to gall; the surface is torn.

## Galvanic corrosion (dissimilar metals)

Two metals in contact with an electrolyte (water, salt, chemicals): the more **active** one corrodes (the anode) and the more **noble** one is protected; the further apart in the galvanic series, the faster. Active → noble (roughly): magnesium, zinc/galvanising, aluminium, mild steel, cast iron, lead, tin, brass/bronze, copper, stainless (passive), nickel, titanium, graphite. **A steel bolt in aluminium** corrodes the aluminium around it (the anode is the big part: slow but destructive: the white crust); **a stainless bolt in aluminium** in a wet place corrodes the aluminium faster; **a small aluminium part bolted with steel** corrodes fast (the anode is small). Prevention: **anti-seize (a barrier film)** on the threads and under the head, a **coating** on the bolt (zinc, cadmium, PTFE), an **insulating washer/sleeve**, sealant to keep the electrolyte out, choosing compatible metals (aluminium fasteners in aluminium, stainless with stainless where galling is managed), and drainage.

## Common mistakes

- Stainless bolts assembled dry with an impact wrench: every one galled and cut off.
- A 3/4" grade 8 bolt torqued to the dry chart's 380 ft-lb with copper anti-seize on it: stretched past yield.
- Copper anti-seize on stainless in a chloride wash: cracks.
- Anti-seize and Loctite on the same bolt.
- Anti-seize on a Taper-Lock bushing's taper: the bushing bottoms and the hub splits.
- A blind hole filled with anti-seize and the bolt driven in: the casting cracks from the hydraulic lock.
- Petroleum anti-seize on an oxygen regulator's fitting.

## Related

- [Bolt torque chart (SAE and metric)](/article/bolt-torque-chart-sae-metric)
- [Locking methods and threadlockers](/article/locking-methods)
- [Broken bolt and stud removal](/article/broken-bolt-and-stud-removal)
- [Thread identification and gauges](/article/thread-identification-and-gauges)
- [Welding stainless (contamination rules)](/article/welding-stainless-and-dissimilar)
- [Oxy-fuel safety (oxygen and oil)](/article/oxy-fuel-safety)
