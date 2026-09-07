---
title: "Oil Viscosity and Selection: ISO VG, SAE Engine and Gear Grades, AGMA Numbers Compared in One Chart, Viscosity Index and Temperature, Choosing Gearbox Oil (AGMA 9005 by Speed and Ambient), Hydraulic Oil (32/46/68), Bearing Oil by Speed and Temperature, Compressor and Chain Oils, Mineral vs PAO vs PAG vs Ester, Food Grade, Storage and Labelling"
slug: oil-viscosity-and-selection
category: lubrication
kind: chart
tags: [oil viscosity, ISO VG, ISO 220, ISO 320, ISO 460, ISO 68, SAE 90, SAE 30, AGMA number, viscosity comparison chart, viscosity index, cSt, SUS, gear oil selection, AGMA 9005, gearbox oil, hydraulic oil 46, bearing oil viscosity, compressor oil, chain oil, synthetic oil, PAO, PAG, ester oil, food grade oil, H1, oil storage, oil labeling, lubricant consolidation, EP gear oil, R&O oil, turbine oil]
source: "ISO 3448 (ISO VG grades); SAE J300 (engine) and J306 (automotive gear) grade definitions; AGMA 9005-F16 (industrial gear lubrication: viscosity by pitch-line velocity and ambient) and the AGMA lubricant number cross-reference; SKF bearing oil viscosity selection (minimum viscosity at operating temperature by speed and size); Noria/Machinery Lubrication viscosity comparison chart; pump and compressor maker guidance."
summary: "One chart to convert between the viscosity systems on the drums (ISO VG, SAE engine, SAE gear, AGMA), what viscosity index means when the oil warms up, and the selection rules a millwright applies: gearbox oil by speed and ambient per AGMA 9005, hydraulic oil by pump type, bearing oil by speed and temperature, the special cases (worm gears, compressors, chains, high temperature), the synthetic base oils and which mix with mineral oil, food-grade requirements, and how to store, label and consolidate lubricants so the wrong oil never goes in."
---

## Viscosity: what the number is

Viscosity is resistance to flow; for lubricants it is quoted in **centistokes (cSt, mm²/s) at 40°C** (ISO VG numbers are the cSt at 40°C) and at 100°C. It **falls as the oil warms**: an ISO 220 gear oil is 220 cSt at 40°C (104°F), about 19 cSt at 100°C, and only 10 cSt at 130°C; the oil in a gearbox running at 180°F is nowhere near "220". Old units: **SUS** (Saybolt universal seconds: cSt ≈ SUS × 0.22 above 100 SUS) and the SAE grades.

**Viscosity index (VI)**: how little the viscosity changes with temperature: mineral oils 90-100, high-VI/hydraulic HVI 130-150, PAO synthetics 130-160, PAG 150-250. A high-VI oil stays thicker when hot and thinner when cold: fewer grade changes with the seasons.

## Comparison chart (approximate; the grades overlap, not equal)

| ISO VG (cSt at 40°C) | AGMA number (gear) | SAE engine grade | SAE gear grade | Typical use |
|---|---|---|---|---|
| 22 | | 5W | | Spindles, hydraulic (cold), air tools |
| **32** | | 10W | | Hydraulics (cold/high speed), turbines, spindles |
| **46** | 1 | 10W / 20 | 75W | **Hydraulics (standard)**, turbines, compressors |
| **68** | 2 | 20 | 75W-80W | Hydraulics (hot), bearings, compressors, light gears |
| **100** | 3 | 30 | 80W | Bearings, high-speed gears, compressors |
| **150** | 4 | 40 | 80W-85W | Bearings, gears, chains |
| **220** | 5 | 50 | 90 | **Industrial gearboxes (the commonest)**, chains |
| **320** | 6 | 60 | 90 | Gearboxes (slow/hot), mill gears |
| **460** | 7 (7 Comp) | | 140 | Slow heavy gears, **worm gears**, open-gear spray |
| **680** | 8 (8 Comp) | | 140-250 | Very slow, hot, kiln drives, worm |
| 1000 | 8A | | 250 | Open gears |
| 1500 | 9 | | | Open gears, girth gears |

"Comp" = compounded (with fatty oil for worm gears); "EP" after the AGMA number = extreme pressure additives; "S" = synthetic. Multigrade engine oils (15W-40) span two rows.

## Gearbox oil (AGMA 9005 approach)

The grade depends on the **pitch-line velocity** (or the low-speed shaft rpm for a simple rule) and the **ambient/operating temperature**; enclosed helical, spur and bevel gearboxes:

| Low-speed shaft or pitch-line velocity | Ambient 15-50°F (−10 to 10°C) | **Ambient 50-95°F (10-35°C)** | Ambient 95-130°F (35-55°C) |
|---|---|---|---|
| High speed, > 3,000 ft/min (15 m/s) or > 1,500 rpm low-speed shaft | ISO 68-100 | **ISO 100-150** | ISO 150-220 |
| Medium, 1,000-3,000 ft/min or 300-1,500 rpm | ISO 100-150 | **ISO 150-220** | ISO 220-320 |
| **Slow, < 1,000 ft/min or < 300 rpm** | ISO 150-220 | **ISO 220-320** | ISO 320-460 |
| Very slow / heavily loaded (mill, kiln, crusher) | 220-320 | 320-460 | 460-680 |
| **Worm gears** | 320-460 (compounded/synthetic) | **460** | 680 |

Then: **EP** (sulphur-phosphorus) oil where the drive sees shock or heavy loads (most industrial gear oils sold are EP: Mobilgear 600 XP, Shell Omala S2 G); **R&O (no EP)** for gearboxes with bronze or silver parts, and for turbines and bearings; **compounded or synthetic PAG/PAO** for worm gears (EP attacks the bronze: see [worm reducers](/article/planetary-and-worm-reducers)); **synthetic PAO** (Mobil SHC 630 series, Omala S4 GX) for wide temperature swings, hot boxes, extended drains; the gearbox maker's plate governs where it gives a grade. A gearbox's oil should hold **at least about 20-25 cSt at the operating sump temperature**: check the oil's temperature-viscosity data at your sump temperature (a 220 at 180°F is roughly 25 cSt; at 200°F it is 18: go to 320 or synthetic).

Change intervals: mineral **2,500 h or 6 months** (many makers: first change at 500 h), synthetic **5,000-8,000 h or 2 years**, or by [oil analysis](/article/oil-analysis-and-sampling).

## Hydraulic oil

| System | Oil |
|---|---|
| Industrial, indoor, 100-140°F operating | **AW ISO 46** (32 for high-speed vane/piston pumps and cold rooms; 68 for hot or heavily loaded gear pumps) |
| Mobile equipment, outdoor | HVI AW 46 or 68, or the maker's engine-oil spec (10W, 15W-40 on some) |
| Servo and proportional systems | AW 32/46 with high cleanliness; zinc-free where the maker says |
| Water-glycol / fire-resistant | HFC/HFD per the system |
| Cold starts below 20°F | ISO 32 HVI, or heaters |

The pump maker's viscosity window (typically 16-40 cSt ideal, 10-100 limits at operating temperature) is the deciding rule; the reservoir temperature decides the grade more than the ambient.

## Bearing oil (oil-lubricated pillow blocks, pump bearing frames, spindles)

Minimum required viscosity at the **operating temperature** depends on speed and bearing size (SKF): a 50-100 mm bearing at 1,800 rpm needs about **12-15 cSt at operating temperature** (a ball bearing) to 20+ cSt (roller); to have that at 160°F you need an **ISO 68** oil; at 200°F an ISO 100. Typical: **pump bearing frames (ANSI pumps): ISO 68 turbine/R&O oil** (Goulds: ISO VG 68, or 100 for hot services); electric motor sleeve bearings: ISO 32-68 turbine oil; high-speed spindles: 10-32; slow heavy trunnions: 220-460; oil mist systems: ISO 68-100 designed for mist. Rule: **the faster, the thinner; the hotter and slower and heavier, the thicker**, then check the minimum at temperature.

## Special cases

| Application | Oil | Notes |
|---|---|---|
| Reciprocating compressor | Compressor oil ISO 100 (SAE 30) non-detergent, or a synthetic diester | Never engine oil (carbon on the valves) |
| Rotary screw compressor | The maker's synthetic fluid (PAO/diester blend) | Do not mix with mineral: varnish |
| Refrigeration compressor | POE (HFC refrigerants), mineral (R-22, ammonia), PAG | Per refrigerant |
| **Roller chains** | ISO 100-220 chain oil (with tackifier), or a penetrating chain lube; SAE 30 in a pinch | Must penetrate to the pins: oil, not grease (grease seals the outside and starves the pin) |
| Air tools | ISO 32 air tool oil | Through the lubricator |
| Steam turbines, turbo blowers | ISO 32-46 turbine oil (R&O, high oxidation stability) | |
| Machine tool ways | Way oil ISO 68-220 (tacky, anti-stick-slip) | |
| Open gears, wire rope | Asphaltic compounds, semi-fluid greases, rope dressing | |
| Chain in ovens/dryers | Synthetic high-temperature chain oil (ester, PAG) | Mineral cokes |
| Vacuum pumps | Vacuum pump oil (low vapour pressure) | |
| Food contact | **NSF H1** (white mineral or PAO/PAG H1) in ISO 32-460 | H2 for no-contact; keep separate |

## Base oils and mixing

| Base | Character | Mixes with mineral? |
|---|---|---|
| **Mineral (Group I-III)** | The standard; Group II/III are cleaner and longer-lived | Yes |
| **PAO (polyalphaolefin)** | Wide temperature range, high VI, long life, low deposits; the common "synthetic" | **Yes** (compatible; seals may need a little ester in the blend) |
| **PAG (polyalkylene glycol)** | Low friction on worms, very high VI, clean; attacks some paints and seals | **No**: not miscible with mineral or PAO; flush completely |
| Ester (diester, polyol ester) | Compressors, high temperature, biodegradable | Mostly yes; seal swelling |
| Silicone | Extreme temperature, low lubricity | No; contaminates everything |
| PFPE | Oxygen, chemical | No |

## Storage, labelling and consolidation

- Drums **indoors, on their side or under cover, bungs at 3 and 9 o'clock** (a drum standing outside breathes rain in through the bungs); a **desiccant breather and a filter** on bulk tanks; **filter new oil into the system** (drum oil is ISO 20/18/15 or dirtier).
- **Label everything**: the drum, the transfer container, the pump, the grease gun, the machine's fill point, with the same **colour and code** (a plant lube chart: e.g. blue triangle = ISO 220 EP gear oil): the ISO 46 hydraulic in the gearbox and the 220 in the hydraulic unit both happen when containers are unlabelled.
- **Dedicated transfer containers** (sealed, with a spout and a filter) per oil; no open buckets, no funnels shared; wipe fill caps before opening.
- **Consolidate**: most plants can run on about 8-12 lubricants (an AW 46, an R&O 68, EP gear oils 220 and 320/460, a worm/synthetic 460, a compressor fluid, a chain oil, a turbine oil, two or three greases, a food grade set); fewer products = fewer mix-ups; but never consolidate an oil out that a machine specifically needs (worm gears, screw compressors, PAG systems).
- Shelf life: mineral oils 3-5 years sealed; additive-heavy oils and greases 2-3; rotate stock.
- Oil sample bottles, sampling valves and the lab's schedule belong with the lube program: [oil analysis and sampling](/article/oil-analysis-and-sampling).

## Common mistakes

- ISO 220 gear oil in a hydraulic unit (it will not flow through the filter; the pump cavitates) or ISO 46 in a slow gearbox (metal-to-metal).
- EP 220 in a worm gearbox with a bronze wheel.
- PAG topped up with mineral.
- SAE 30 engine oil in a compressor.
- Grease on a roller chain.
- "Synthetic is better, so ISO 68 synthetic will do in the 220 box": viscosity first, base oil second.
- Drums stored upright outdoors with a puddle on the top.

## Related

- [Grease types and compatibility](/article/grease-types-and-compatibility)
- [Oil analysis and sampling](/article/oil-analysis-and-sampling)
- [Gearbox lubrication and inspection](/article/gearbox-lubrication-and-inspection)
- [Planetary and worm reducers (worm gear oils)](/article/planetary-and-worm-reducers)
- [Filters, fluid and contamination (hydraulic fluid)](/article/filters-fluid-and-contamination)
- [Roller chain drives](/article/roller-chain-drives)
