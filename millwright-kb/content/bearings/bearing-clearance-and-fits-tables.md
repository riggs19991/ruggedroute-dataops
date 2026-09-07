---
title: "Bearing Fits, Internal Clearance and Shaft/Housing Tolerances: ISO Fit Codes Explained (h6, j5, k5, m5, n6, p6; H7, J7, K7, M7, N7, P7), Fit Selection by Load Type, Tolerance Tables for Common Sizes in Inches, C3 and Radial Internal Clearance Values, Measuring Seats, Repairing Worn Seats"
slug: bearing-clearance-and-fits-tables
category: bearings
kind: chart
tags: [bearing fits, shaft fit bearing, housing fit bearing, interference fit, press fit bearing, k5, m5, n6, j6, h6, H7, J7, K7, M7, N7, P7, ISO 286, tolerance table, bearing clearance, radial internal clearance, C3 clearance, CN clearance, C4, bearing seat tolerance, measuring shaft for bearing, worn bearing seat repair, rotating load, stationary load, circumferential load]
source: "ISO 286-1/-2 tolerance grades and fundamental deviations (values computed for the size ranges shown); SKF and Timken fit recommendation tables (shaft and housing fits by load condition and bearing type); ISO 5753-1 radial internal clearance classes for deep groove ball and spherical roller bearings (representative values); SKF Bearing Maintenance Handbook (seat measurement and repair guidance)."
summary: "Why a bearing ring must be tight on the member that carries the rotating load and can be loose on the other, how to read the ISO fit codes on a drawing, which fit to use for each load and bearing type, ready tables of the actual shaft and housing limits for common inch and millimetre sizes, the internal clearance classes and typical values including what a press fit does to them, and how to measure and repair the seats."
---

## The rule that decides everything

A bearing ring that turns relative to the direction of the load (**rotating load**) will **creep** on its seat unless it has an **interference fit**; a ring that does not (**stationary load**) can have a loose fit and often must, to allow axial float or thermal expansion.

| Case | Inner ring | Outer ring |
|---|---|---|
| **Rotating shaft, stationary housing, fixed-direction load** (motor, pump, gearbox, fan): the commonest | **Interference** (k5/k6/m5/m6/n6 by size and load) | Loose to transition (H7/J7/K7); tight only if the load is heavy or the housing is thin/aluminium |
| Stationary shaft, rotating housing (wheel hubs, idler pulleys, conveyor rollers) | Loose to transition (g6/h6/j6) | **Interference** (M7/N7/P7) |
| Unbalanced rotating load (vibrating screens, eccentric drives) | Interference | Interference |
| Indeterminate load direction, shock | Interference | Interference (M7/N7) |

Too loose: the ring creeps, frets (red-brown powder), wears the seat, the shaft turns in the ring and heats. Too tight: the interference removes the bearing's internal clearance, the bearing runs hot and preloaded, the ring cracks (thin-section and ceramic), the seat is ruined on removal.

## Reading a fit code

`Ø50 k5` on a shaft, `Ø90 H7` in a housing: the number is the nominal size, the letter is the **position** of the tolerance zone relative to nominal (**lower case = shaft**, **upper case = hole**), the number is the **grade** (IT5 fine, IT6, IT7 coarser: the width of the zone).

- Shafts: **g** and **h** are at or below nominal (clearance with an H hole); **j** and **js** straddle nominal (transition); **k, m, n** are above nominal (increasing interference); **p, r, s** heavy interference.
- Holes: **H** starts at nominal and goes up (clearance); **J/JS** straddle; **K, M, N** go below nominal (interference with an h shaft); **P** heavier.
- Bearing inner ring bores and outer ring ODs have their **own** tolerance (bore: nominal to **minus** a few tenths, e.g. 0 / −0.0005" for a 50 mm bore in normal class); so an h6 shaft with the bore's minus tolerance gives a slight interference to slight clearance, and a k5 shaft gives a reliable light interference. That is why bearing fits use k/m/n on shafts and H/J/K/M on housings rather than the "press fit" letters a machinist would expect.

## Fit selection (rotating inner ring load; SKF/Timken practice for solid steel shafts)

| Bearing type | Shaft diameter | Light and variable loads (P ≤ 0.05C) | Normal loads (0.05-0.1C) | Heavy and shock loads (> 0.1C) |
|---|---|---|---|---|
| **Ball bearings** | up to 18 mm (3/4") | h5 / j5 | j5 | |
| | 18-100 mm (3/4-4") | j6 | **k5** (k6 over 40) | m6 (> 100: m6/n6) |
| | 100-200 mm | k6 | m5/m6 | n6 |
| **Cylindrical and tapered roller** | up to 40 mm | j6 | **k6** | |
| | 40-140 mm | k6 | **m6** (m5) | n6 |
| | 140-200 mm | m6 | m6/n6 | p6 |
| **Spherical roller** | up to 65 mm | | k5/k6 | |
| | 65-100 | | m5/m6 | n6 |
| | 100-140 | | m6 | n6/p6 |
| | over 140 | | n6 | p6/r6 |
| Stationary inner ring load, any | | g6 (needs to slide) / h6 (does not) | h6 | j6 |

Housings (stationary outer ring load): **H7** for most split housings and where the outer ring must float; **J7** (JS7) for one-piece housings, general; **K7** for accuracy and quiet running with float not needed; **M7** for heavy loads and thin-walled or light-alloy housings; **N7/P7** for rotating outer ring loads (wheel hubs).

Special cases: **hollow shafts** and thin-section bearings need tighter fits than the table (the hollow shaft gives more); **aluminium housings** grow away from the ring when hot and need a tighter housing fit (K7/M7) than the table for steel; **stainless or ceramic-coated** seats: consult the maker; motor bearings: the maker's fits (often j5/k5 and H6/H7).

## Tolerance tables (ISO 286; values in **inches**, deviation from nominal)

### Shafts

| Nominal Ø | h6 | j6 | j5 | k5 | k6 | m5 | m6 | n6 | p6 |
|---|---|---|---|---|---|---|---|---|---|
| **18-30 mm (0.709-1.181")** | 0 / -0.0005 | +0.0004 / -0.0002 | +0.0002 / -0.0002 | **+0.0004 / +0.0001** | +0.0006 / +0.0001 | +0.0007 / +0.0003 | +0.0008 / +0.0003 | +0.0011 / +0.0006 | +0.0014 / +0.0009 |
| **30-50 mm (1.181-1.969")** | 0 / -0.0006 | +0.0004 / -0.0002 | +0.0002 / -0.0002 | **+0.0005 / +0.0001** | +0.0007 / +0.0001 | +0.0008 / +0.0004 | +0.0010 / +0.0004 | +0.0013 / +0.0007 | +0.0017 / +0.0010 |
| **50-80 mm (1.969-3.150")** | 0 / -0.0007 | +0.0005 / -0.0003 | +0.0002 / -0.0003 | **+0.0006 / +0.0001** | +0.0008 / +0.0001 | +0.0009 / +0.0004 | +0.0012 / +0.0004 | +0.0015 / +0.0008 | +0.0020 / +0.0013 |
| **80-120 mm (3.150-4.724")** | 0 / -0.0009 | +0.0005 / -0.0004 | +0.0002 / -0.0004 | **+0.0007 / +0.0001** | +0.0010 / +0.0001 | +0.0011 / +0.0005 | +0.0014 / +0.0005 | +0.0018 / +0.0009 | +0.0023 / +0.0015 |
| 120-180 mm (4.724-7.087") | 0 / -0.0010 | +0.0006 / -0.0004 | +0.0003 / -0.0004 | **+0.0008 / +0.0001** | +0.0011 / +0.0001 | +0.0013 / +0.0006 | +0.0016 / +0.0006 | +0.0020 / +0.0011 | +0.0027 / +0.0017 |

### Housings

| Nominal Ø | H7 | J7 (JS7) | K7 | M7 | N7 | P7 |
|---|---|---|---|---|---|---|
| **50-80 mm (1.969-3.150")** | +0.0012 / 0 | +0.0007 / -0.0005 | +0.0004 / -0.0008 | 0 / -0.0012 | -0.0004 / -0.0015 | -0.0008 / -0.0020 |
| **80-120 mm (3.150-4.724")** | +0.0014 / 0 | +0.0009 / -0.0005 | +0.0004 / -0.0010 | 0 / -0.0014 | -0.0004 / -0.0018 | -0.0009 / -0.0023 |
| **120-180 mm (4.724-7.087")** | +0.0016 / 0 | +0.0010 / -0.0006 | +0.0005 / -0.0011 | 0 / -0.0016 | -0.0005 / -0.0020 | -0.0011 / -0.0027 |
| 180-250 mm (7.087-9.843") | +0.0018 / 0 | +0.0012 / -0.0006 | +0.0005 / -0.0013 | 0 / -0.0018 | -0.0006 / -0.0024 | -0.0013 / -0.0031 |
| 250-315 mm (9.843-12.402") | +0.0020 / 0 | +0.0014 / -0.0006 | +0.0006 / -0.0014 | 0 / -0.0020 | -0.0006 / -0.0026 | -0.0014 / -0.0035 |

Bearing bore tolerance (normal class, PN): 18-30 mm: 0 / −0.0004"; 30-50: 0 / −0.0005"; 50-80: 0 / −0.0006"; 80-120: 0 / −0.0008"; 120-180: 0 / −0.0010". Outer ring OD: 50-80 mm: 0 / −0.0005"; 80-120: 0 / −0.0006"; 120-150: 0 / −0.0007"; 150-180: 0 / −0.0010"; 180-250: 0 / −0.0012".

**Worked example**: 50 mm bore ball bearing (bore 1.9685 to 1.9680") on a k5 shaft (1.9686 to 1.9690"): interference from **0.0001" to 0.0010"**, typically 0.0005". About 80% of the interference reduces the bearing's radial clearance: a 0.0005" fit takes about 0.0004" out of it.

## Internal clearance

Radial internal clearance (RIC) is the total play between the rings measured on the unmounted bearing; the **mounted** clearance is less by the fit reductions, and the **operating** clearance is less again by the temperature difference between the rings (the inner runs hotter and expands). The target is a **small positive operating clearance**.

| Class | Meaning | Use |
|---|---|---|
| C2 | Less than normal | Precision, preloaded pairs |
| **CN (normal, no suffix)** | Normal | Normal fits, small temperature difference |
| **C3** | Greater than normal | **Interference fit on the shaft (k5/m5 and tighter), hot-running (motors, fans, dryers), roller bearings in general; the usual choice for electric motors** |
| C4 | Greater than C3 | Both rings tight, high temperature (over 250°F), vibrating machinery |
| C5 | Greater than C4 | Extreme temperature |

Typical radial internal clearance (deep groove ball bearings, ISO 5753, in inches):

| Bore | CN | C3 | C4 |
|---|---|---|---|
| 18-24 mm | 0.0002-0.0008 | 0.0005-0.0011 | 0.0009-0.0016 |
| 30-40 mm | 0.0002-0.0009 | 0.0006-0.0013 | 0.0011-0.0020 |
| **40-50 mm** | 0.0002-0.0011 | **0.0007-0.0016** | 0.0013-0.0024 |
| 50-65 mm | 0.0004-0.0013 | 0.0009-0.0019 | 0.0016-0.0028 |
| 80-100 mm | 0.0005-0.0016 | 0.0012-0.0024 | 0.0020-0.0035 |
| 120-140 mm | 0.0006-0.0020 | 0.0015-0.0030 | 0.0026-0.0044 |

Spherical roller bearings have much larger clearances (a 100 mm bore C3 spherical roller: about 0.0055-0.0071"), which is why they are mounted by **measuring the clearance reduction** with a feeler gauge on a taper ([SKF drive-up card](/article/skf-drive-up-card)).

Suffix on the bearing number: `6310-C3`, `22220 E/C3`; the box says it, the ring is often etched. Replacing a C3 motor bearing with a CN one gives a bearing that runs hot and fails early.

## Measuring seats

- **Shaft**: outside micrometer (0.0001" graduations), at **two planes** along the seat and **three angles** (0°, 60°, 120°) at each plane: taper (difference between planes) and out-of-round (difference between angles) each **≤ 25% of the fit tolerance** (about 0.0002" on a 2" seat); compare the average with the table. A seat that is undersize or scored more than a polish will remove: repair.
- **Housing bore**: dial bore gauge or inside micrometer, same pattern; a split housing is measured with the cap torqued.
- **Shoulder**: square to the seat (dial indicator), height per the bearing's chamfer (the shoulder must contact the ring face, not the chamfer, and must not touch the cage or seal).
- Surface finish: 32 µin or better on bearing seats; radius at the shoulder smaller than the bearing's chamfer.

## Repairing worn seats

| Damage | Repair |
|---|---|
| Light fretting, minor scoring | Polish with fine emery on a strap, re-measure; if still in tolerance, use it |
| Shaft seat undersize by up to 0.001-0.002" | **Bearing-mount retaining compound** (Loctite 638/660/680-type) to fill and lock: for light loads, stationary or moderate speed; not a substitute for a proper fit on a heavily loaded bearing |
| Undersize more, or a spun bearing | **Metal spray or weld build-up and machine** to size; or sleeve the shaft (a shrink-fit sleeve machined to size); or a new shaft |
| Housing bore worn/ovalled | Bore and sleeve (a steel liner pressed and locked), or bore oversize and fit a special outer ring/cartridge; retaining compound for slight wear |
| Damaged shoulder | Machine it square, fit a hardened spacer ring against a re-cut shoulder |
| Keyway or set-screw burrs | File flush; a raised burr next to a seat is a bearing that will not go on or come off |

Retaining compounds: clean and degrease both parts, apply to the shaft seat, install the bearing quickly, do not disturb for the cure (fixture time 5-30 minutes, full cure 24 h), and remember that heat (over 300°F) is needed to release it later.

## Common mistakes

- "It slid on, so the fit is fine": a rotating inner ring that slides on with hand pressure will creep and fret.
- Pressing a k5-fit bearing on with a hammer on the outer ring.
- CN bearing in a hot motor or with a tight shaft: no operating clearance.
- Measuring the seat once, in one place, with a caliper.
- Filing a shaft "to make the bearing fit" (now it is 0.003" undersize).
- Bearing-mount compound on a 300 hp motor's spun seat as the permanent fix.
- Aluminium housing with an H7 bore for a hot-running bearing: the outer ring creeps when warm.

## Related

- [Bearing designation codes](/article/bearing-designation-codes)
- [Bearing mounting with heat](/article/bearing-mounting-with-heat)
- [Tapered roller bearing setting](/article/tapered-roller-bearing-setting)
- [Reading a micrometer](/article/reading-a-micrometer)
- [Shaft, bearing and fastener formulas (shrink fits)](/article/shaft-bearing-fastener-formulas)
- [Bearing failure analysis](/article/bearing-failure-analysis)
