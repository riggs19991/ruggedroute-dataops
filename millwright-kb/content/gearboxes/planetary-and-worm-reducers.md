---
title: "Worm, Planetary and Cycloidal Reducers: How Each Works, Ratio and Efficiency, Self-Locking, Worm Gear Oils (Compounded, PAG, Synthetic) and Compatibility, Mounting Positions and Vents, Thermal Rating, Bronze Wheel Run-In and Wear, Planetary Ratio Math and Maintenance, Cycloidal (Sumitomo) Basics, Service Factors"
slug: planetary-and-worm-reducers
category: gearboxes
kind: reference
manufacturer: "Boston Gear / Dodge Tigear / Sumitomo Cyclo / Bonfiglioli / Brevini (generic)"
model_numbers: ["Boston Gear 700 series", "Dodge Tigear-2", "Winsmith", "Sumitomo Cyclo 6000", "Bonfiglioli 300 series", "Brevini", "Falk Quadrive", "Grove Gear"]
tags: [worm gear reducer, worm gearbox, worm gear oil, worm gear efficiency, self locking, worm gear ratio, bronze worm wheel, worm gear wear, compounded gear oil, PAG oil worm, mounting position gearbox, gearbox vent, breather, thermal rating, planetary gearbox, planetary ratio, sun planet ring, cycloidal reducer, Sumitomo Cyclo, service factor gearbox, gearbox selection, gearbox overheating]
source: "Boston Gear worm gear reducer manuals and engineering data (efficiency by ratio, lubrication, mounting positions); Dodge Tigear-2 installation manual; AGMA 9005 (lubricants for worm gears: compounded and synthetic); Sumitomo Cyclo 6000 operating manual; Bonfiglioli and Brevini planetary gearbox manuals; AGMA service factor tables."
summary: "The three reducer types a millwright meets after the ordinary helical box: worm reducers (why they run hot, why the oil is special, when they hold a load without a brake, and how the bronze wheel wears), planetary reducers (the ratio math, why they are compact, what to check), and the cycloidal drive (how it takes shock), with the mounting, venting, oil and service-factor rules common to all."
---

## Worm gear reducers

A steel **worm** (a screw, usually hardened and ground) drives a **bronze wheel** (phosphor bronze or aluminium bronze) at 90°. The contact is **sliding**, not rolling, so:

- **Efficiency depends on the ratio** (the lead angle of the worm): roughly **90% at 5:1, 85% at 10:1, 75-80% at 20:1, 65-70% at 40:1, 50-60% at 60:1 and above**. The lost power is heat in the oil: a 10 hp input at 50:1 puts 3-4 hp into the oil, so the box is **thermally rated** (a maximum input hp for continuous duty, lower than its mechanical rating) and runs hot (200°F on the housing is not unusual and up to about 220°F is allowed by most makers with synthetic oil; over that the bronze wears fast).
- **Self-locking**: a ratio above about **30:1 to 40:1** (lead angle under 5-6°) cannot be back-driven from the output at rest: the load will not run back down when the motor stops. This is a **design property, not a brake**: vibration, a warm box and a large overhauling load can let it creep; hoists need a brake regardless.
- Ratio = wheel teeth ÷ worm starts (a single-start worm and a 40-tooth wheel = 40:1; double start = 20:1); a single stage does 5:1 to 100:1; double reduction (helical-worm or worm-worm) to 3600:1.
- The bronze wheel is the **wear part**: it is designed to wear (the soft member protects the worm); its wear shows as backlash growth and bronze in the oil. A worm that has wear grooves or is pitted needs replacing with the wheel.
- Thrust: the worm shaft carries a heavy axial thrust; its bearings (often tapered rollers set with end play or preload per the manual) are the first mechanical failure after the oil.

### Worm gear oil

Sliding contact under high pressure with a bronze surface: **EP additives of the sulphur-phosphorus type used in helical gear oils attack bronze** (they are "active" sulphur), so worm boxes use either:

| Oil | Notes |
|---|---|
| **Compounded mineral gear oil** (ISO 460 or 680 with 3-10% fatty oil, "AGMA 7 Comp / 8 Comp", such as Mobil 600W Cylinder Oil) | The classic; the fatty additive lubricates the bronze; change every 2,500 h / 6 months |
| **Synthetic PAO** (ISO 460-680) | Better at temperature, longer life (5,000-8,000 h / 2 years); most makers' factory fill today |
| **Synthetic PAG (polyglycol, e.g. Mobil Glygoyle, Shell Omala S4 WE)** | Lowest friction on worm gears (runs 10-20°F cooler, efficiency up several %), longest life; **not miscible with mineral or PAO oil** and attacks some paints and seals: **never mix**; flush thoroughly if changing to or from PAG |
| Food grade H1 synthetic (ISO 460) | Where required |
| Helical gear EP oil (ISO 220 EP) | **Not for worm boxes** with bronze wheels unless the maker approves an "inactive sulphur" EP grade |

Viscosity: **ISO 460 for most, 680 for slow/hot**, 320 for high-speed worms in cool locations, per the maker's chart by input speed and ambient. Level: to the plug at the mounting position (a worm box has a different fill for each position: the worm-over, worm-under and vertical arrangements each need the oil to reach the mesh and the bearings; the manual's chart by position gives ounces); the wrong level for the position starves the upper bearings or churns.

### Mounting positions and venting

- Boxes are built (or converted) for a **specific mounting position**: worm over, worm under, vertical output up/down, wall mount; the position decides which plug is the fill, level and drain, where the vent goes (the highest point, and not where oil splashes into it), and sometimes the bearing arrangement (grease packs on the upper bearings). **Re-plug** per the manual when the position changes; a box mounted sideways with the vent on the side pumps oil out of it.
- Vent (breather): clear, at the top, replaced when clogged or when the box pushes oil past the seals (pressure from a blocked vent is the commonest cause of seal leaks); a **desiccant breather** in damp or dusty plants.
- Solid mounting on a flat surface; **do not** clamp a small worm box to a warped bracket: the housing distorts and the worm binds.

### Run-in and inspection

- New or re-wheeled boxes: **run in at reduced load** (50% for 24 h, or per the maker) so the bronze wears into the worm's shape; efficiency improves over the first 100 hours; change the oil after run-in (bronze fines).
- Check: housing temperature (a hand cannot stay on a 140°F+ housing; use a thermometer; the maker's limit is typically **200-220°F**), oil level and colour (bronze in the oil turns it golden-green, then dark), backlash at the output shaft (rock it by hand; growth = wheel wear), seal leaks, the worm shaft end play, the vent, mounting bolts.
- Overheating causes, in order: overload beyond the thermal rating, wrong or old oil, wrong level, a blocked vent, a hot location with no airflow, a fan missing from the input shaft (worm boxes over about 5 hp carry a fan), tight bearings.

## Planetary reducers

A **sun** gear in the centre, several **planet** gears on a **carrier**, all inside a **ring** (annulus) gear; one of the three is held, one is the input, one the output. Load is shared by 3-5 planets, so the box is small for its torque, coaxial (input and output on one axis) and stiff; used on winches, slewing drives, wheel drives, mixers, conveyors (Brevini, Bonfiglioli, Falk, Rexnord Planetgear), and in multi-stage stacks for big ratios.

```
   ring held, sun in, carrier out (the usual):    i = 1 + N_ring ÷ N_sun         (e.g. 72-tooth ring, 24-tooth sun: i = 4)
   carrier held (star arrangement):               i = − N_ring ÷ N_sun          (reverses)
   sun held, ring in, carrier out:                i = 1 + N_sun ÷ N_ring   (close to 1; rare)
   stages multiply: three 4:1 stages = 64:1
```

Efficiency about 97-98% per stage. Maintenance: **oil level** at the plug for the mounting position (planetaries are often mounted vertically or on wheel hubs where the fill is a fraction of the volume); **oil change** per hours (typically 500 h first, then 2,500-5,000 h mineral / 8,000-10,000 h synthetic); listen for **planet bearing** roughness (needle bearings in the planets are the common failure; the oil debris tells you); check the **output bearing preload** on wheel drives and slewing units (they carry the load), the seals, and the torque of the ring-gear bolts (a slipped ring gear = a ratio surprise and broken teeth). Never run a planetary without oil even briefly: the planet bearings have no reservoir.

## Cycloidal reducers (Sumitomo Cyclo and similar)

An eccentric on the input drives a **cycloid disc** with lobes that roll on **pins/rollers** in the housing; the disc's slow rotation is taken off by pins to the output. **Rolling contact** (no gear teeth), so the drive takes **500% momentary shock**, is compact, single-stage ratios 6:1 to 119:1, efficiency 90-95%. Lubrication: grease in small sizes (repack per the manual, e.g. every 3-6 months of grease or the maker's hours), oil in larger (level to the sight glass for the mounting position); eccentric bearing is the wear item; the drive is noisy compared with a helical box and that is normal. Inspect for lube and for backlash at the output (cycloids have very little: growth = worn pins/rollers).

## Service factors and selection (all types)

The reducer's catalogue rating is for uniform load, 10 h/day (AGMA class I); the required rating is the motor hp × the **service factor** for the driven machine and the duty:

| Driven load | 3 h/day | 10 h/day | 24 h/day |
|---|---|---|---|
| Uniform (centrifugal pumps, fans, light conveyors) | 0.8-1.0 | 1.0 | 1.25 |
| Moderate shock (heavy-duty conveyors, mixers, screw conveyors) | 1.0 | 1.25 | 1.5 |
| Heavy shock (crushers, reciprocating pumps, hammer mills, reversing) | 1.5 | 1.75 | 2.0 |

A worm box also needs its **thermal** rating checked separately (input hp continuous without an external fan/cooler). Overhung load (a sprocket or sheave on the output shaft) is rated separately: a big sheave on a small box breaks the output shaft; put the sheave as close to the housing as the guard allows or use a shaft-mount design.

## Replacing a reducer

Match: ratio (or the output speed), input hp and thermal rating, output torque and service factor, shaft sizes and directions (the worm box's output can be left, right or both), mounting position and base dimensions, the direction of rotation (the output turns opposite to the input on a single-stage worm and on a single-stage spur; same on a double), and the oil. Fill to the level for the **new** position; a box shipped with oil is usually shipped **without** its vent (a shipping plug): fit the vent before starting or the seals blow.

## Common mistakes

- Helical EP oil in a worm box: the bronze wheel dissolves into the oil in a year.
- PAG topped up with mineral oil: gel and a burned wheel.
- Vent left as the shipping plug: oil out of every seal.
- Worm box mounted in a new position with the old plug arrangement: the top bearing runs dry.
- Counting on self-locking as the hoist brake.
- A 10 hp motor on a worm box with a 7.5 hp thermal rating "because the mechanical rating is 12": the oil cooks.
- Planetary wheel drive run 200 hours with the oil level right for horizontal mounting when it is vertical: the top stage starved.

## Related

- [Gearbox lubrication and inspection](/article/gearbox-lubrication-and-inspection)
- [Gear inspection and tooth failure](/article/gear-inspection-and-tooth-failure)
- [Dodge torque-arm shaft-mount reducer](/article/dodge-torque-arm-shaft-mount-reducer)
- [Oil viscosity and selection](/article/oil-viscosity-and-selection)
- [Power, torque and drive formulas](/article/power-torque-speed-drive-formulas)
