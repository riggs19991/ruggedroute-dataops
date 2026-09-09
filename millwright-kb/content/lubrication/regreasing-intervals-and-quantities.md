---
title: "Regreasing Intervals and Quantities: The SKF Quantity Formula (G = 0.005 × D × B) with Worked Examples and Grease-Gun Strokes, Initial Fill Rules, Interval Estimation from Speed Factor and Bearing Type with Correction Factors, the Baldor/ABB Motor Relubrication Tables (Interval by Frame and Speed, Volume by Frame), the Greasing Procedure, Over-Greasing Symptoms, Sealed and Shielded Bearings"
slug: regreasing-intervals-and-quantities
category: lubrication
kind: chart
manufacturer: "SKF / Baldor-ABB (generic)"
model_numbers: ["Baldor MN416", "Baldor MN400", "Polyrex EM", "SKF LGMT 2", "SKF SNL", "SAF"]
tags: [regreasing, relubrication, grease quantity, grease amount, how much grease, 0.005 D B, grease gun strokes, grease gun output, regrease interval, how often to grease, relubrication interval, motor greasing, Baldor lubrication table, motor grease interval, frame size grease, Polyrex EM amount, initial grease fill, over greasing, overgreasing, grease purge, grease relief, sealed bearing, shielded bearing, grease fitting, zerk, n dm speed factor, vertical shaft grease]
source: "SKF Rolling Bearings catalogue and Bearing Maintenance Handbook (relubrication quantity G = 0.005 D B, initial fill guidance, relubrication interval method with speed factor, bearing factors and correction factors); Baldor-Reliance/ABB manual MN416 Tables 1-4 (relubrication interval by frame and speed, service multipliers, grease volume by frame/bearing); Machinery Lubrication (Noria) grease gun calibration practice."
summary: "The two numbers every greaser needs: how much and how often. The SKF quantity formula turned into grease-gun strokes with a method to calibrate the gun, the initial fill for a new housing, the interval estimated from bearing type, size and speed with the temperature, contamination and orientation corrections, the Baldor/ABB motor tables that most plants use for motors, the right procedure (relief open, machine warm), the tell-tale signs of too much grease, and what not to grease at all."
---

## How much: the SKF formula

![The grease quantity formula from bearing OD and width](/img/lubrication/regrease-quantity.svg)

*The grease quantity formula from bearing OD and width*

```
   Relubrication quantity  G (grams) = 0.005 × D × B        D = bearing outside diameter (mm), B = bearing width (mm)
   (relubricating through the side of the bearing; from the centre through a W33 groove: G = 0.002 × D × B)
   in ounces: G (oz) = G (g) ÷ 28.35
   this fills roughly 30-40% of the bearing's free space each time; it is the amount to add at each interval, not a housing fill
```

**Worked examples**

| Bearing | D × B (mm) | G = 0.005 × D × B | Ounces |
|---|---|---|---|
| 6205 | 52 × 15 | **3.9 g** | 0.14 |
| 6210 | 90 × 20 | 9 g | 0.32 |
| 6310 | 110 × 27 | 14.9 g | 0.52 |
| 6316 | 170 × 39 | 33 g | 1.2 |
| 22216 E (spherical roller) | 140 × 33 | 23 g | 0.8 |
| 22220 E | 180 × 46 | 41 g | 1.5 |
| 22226 E | 230 × 64 | 74 g | 2.6 |
| 23036 (SAF housing) | 280 × 74 | 104 g | 3.7 |
| 1-1/2" pillow block insert (about 52 mm bore, 100 × 30 outer) | 100 × 30 | 15 g | 0.5 |

The bearing number gives D and B from any catalogue ([bearing designation codes](/article/bearing-designation-codes)); measure them if the number is gone.

**Turning grams into grease-gun strokes**: guns vary from **0.5 to 3 grams per stroke** (lever guns about 1.5-2 g; pistol grips less; battery guns are set per stroke or by volume). **Calibrate your gun**: pump 10 strokes into a cup on a kitchen scale, divide by 10, write the number on the gun. A 6310 (15 g) with a 1.5 g/stroke gun = **10 strokes**; a 6205 (4 g) = **2-3 strokes**, which is why small motor bearings die of over-greasing.

**Initial fill** (a new bearing in a clean housing): fill the **bearing** completely (work grease into the rolling elements) and the **housing 30-50%** of its free space (up to 50% for slow speeds, 30% at high; SKF's rule for standard housings with **n·dm under about 100,000**: up to 1/2; faster: 1/3); a rule of thumb for a housing fill is **G_initial = 0.01 × D × B** (twice the regrease quantity) plus the housing's own volume estimate. **Sealed** inserts and motors come filled.

## How often: estimating the interval

The relubrication interval is the time after which the grease still has enough oil left to protect the bearing; it depends on **bearing type, size, speed, temperature and contamination**. SKF's method: the **speed factor n·dm** (rpm × mean diameter (d + D)/2 in mm) and a **bearing factor** give a base interval from a chart, then corrections.

Base intervals for a **deep groove ball bearing** at **70°C (158°F) at the outer ring, clean, horizontal shaft, normal load** (read from the SKF chart; typical values):

| n·dm | Base interval (hours) |
|---|---|
| 50,000 | > 30,000 (practically the grease's oxidation life: 1-3 years) |
| 100,000 | about 20,000 |
| **200,000** | **about 10,000** |
| 300,000 | about 6,000 |
| 400,000 | about 4,000 |
| 500,000 | about 2,500 |
| 600,000 | about 1,500 |

**Bearing factor**: divide the ball-bearing interval by roughly **2 for cylindrical roller**, **5 for spherical roller and tapered roller bearings** (they churn and need more frequent relubrication; SKF uses factors up to 10 for thrust types).

**Corrections** (multiply the interval):

| Condition | Factor |
|---|---|
| Temperature: every **15°C (27°F) above 70°C** at the bearing | **× 0.5** per step (a bearing at 100°C gets a quarter of the interval); below 70°C no increase beyond the grease's life |
| Vertical shaft | × 0.5 |
| Heavy load (P/C over 0.1) | × 0.5 to 0.7 |
| Contamination (dust, water, washdown) | × 0.5 to 0.1 (grease more to purge) |
| Vibration, shock | × 0.5 to 0.7 |
| Outer ring rotating | × 0.5 |
| Grease with high-performance base oil (synthetic, polyurea in motors) | up to × 2 (per the grease maker) |

**Worked example**: a 22220 spherical roller bearing (bore 100, OD 180: dm = 140) in a fan at 1,500 rpm: n·dm = 210,000 → ball-bearing base about 9,000 h; ÷ 5 for the spherical roller = **1,800 h**; the fan runs at 85°C (one step above 70): × 0.5 = **900 h**; dusty: × 0.5 = **450 h**: about every **3 weeks** on continuous duty, **41 g** each time. A 6205 in a clean 1,750 rpm small motor: dm = 38.5, n·dm = 67,000 → base over 20,000 h; the motor maker's table is the practical answer (below).

Practical plant intervals when nobody has calculated: **motors per the maker's table**; **pillow blocks and fan bearings at 1,800 rpm: monthly to quarterly**, small amounts; **slow heavy pulleys: weekly to monthly**; **couplings: annually**; **washdown areas: after every wash**. Then adjust from the evidence: grease purging clean and the bearing cool = stretch it; grease coming out black or with water, or a warm bearing = shorten.

## Motors: the Baldor/ABB tables (MN416)

The motor makers publish the numbers; use theirs. Baldor-Reliance (ABB) Table 1, **relubrication interval, ball bearings, standard service** (8 h/day, up to 104°F, clean):

| NEMA frame (IEC) | 3,600 rpm | **1,800 rpm** | 1,200 rpm | 900 rpm |
|---|---|---|---|---|
| Up to 210 (132) | 5,500 h | **12,000 h** | 18,000 h | 22,000 h |
| Over 210 to 280 (180) | 3,600 h | **9,500 h** | 15,000 h | 18,000 h |
| Over 280 to 360 (225) | 2,200 h | **7,400 h** | 12,000 h | 15,000 h |
| Over 360 to 5800 (400) | 2,200 h | **3,500 h** | 7,400 h | 10,500 h |

Divide by 2 for **vertical motors and for roller bearings**. Multipliers (Table 3) for the service (Table 2): **standard × 1.0; severe (16+ h/day, 122°F, moderate dirt) × 0.5; extreme (over 122°F, severe dirt, shock) × 0.1**. A 100 hp 405T motor at 1,800 rpm running 24 h in a dusty plant: 3,500 × 0.5 = **1,750 h (about 10 weeks)**.

Table 4, **amount of grease to add** (the large, shaft-end bearing of each frame; the opposite end takes the same or less):

| Frame (IEC) | Bearing | Weight | Volume (in³) | Teaspoons |
|---|---|---|---|---|
| 56 to 140 (90) | 6203 | 0.08 oz (2.4 g) | 0.15 | 0.5 |
| 140 (90) | 6205 | 0.15 oz (3.9 g) | 0.2 | 0.8 |
| 180 (100-112) | 6206 | 0.19 oz (5.0 g) | 0.3 | 1.0 |
| 210 (132) | 6307 | 0.30 oz (8.4 g) | 0.6 | 2.0 |
| 250 (160) | 6309 | 0.47 oz (12.5 g) | 0.7 | 2.5 |
| 280 (180) | 6311 | 0.61 oz (17 g) | 1.2 | 3.9 |
| 320 (200) | 6312 | 0.76 oz (20.1 g) | 1.2 | 4.0 |
| 360 (225) | 6313 | 0.81 oz (23 g) | 1.5 | 5.2 |
| 400 (250) | 6316 | 1.25 oz (33 g) | 2.0 | 6.6 |
| 440 (280) | 6318 | 1.52 oz (40 g) | 2.5 | 8.2 |
| 440 (280) | 6319 | 2.12 oz (60 g) | 4.1 | 13.4 |
| 5000-5800 (315-400) | 6328 / NU328 | 4.70 oz (130 g) | 9.2 | 30.0 |
| 360-449 (225-280) | NU319 | 2.12 oz (60 g) | 4.1 | 13.4 |

(These match the SKF formula within rounding: 6309 = 100 × 25 × 0.005 = 12.5 g.) Grease: **Polyrex EM** (polyurea) for standard Baldor motors from 15°F to 120°F ambient; a high-temperature or low-temperature special where the sheet says; **do not mix grease types** (see [grease compatibility](/article/grease-types-and-compatibility)). Other makers (WEG, Siemens, Toshiba, Nidec/US Motors) publish equivalent tables on the motor's nameplate plate or manual: WEG stamps the interval and the grams on the nameplate.

## The procedure

![Wipe the fitting, pump slowly, watch the seal](/photos/lubrication/grease-gun-use.jpg)

*Wipe the fitting, pump slowly, watch the seal. Photo: U.S. Navy photo by Mass Communication Specialist Seaman Apprentice Kyle Steckler, Public domain, via commons*

1. Identify the bearing and the grease (the tag, the CMMS, the motor nameplate); the **right gun** (labelled), the nozzle **wiped**, the fitting **wiped** (dirt on the fitting goes straight into the bearing).
2. Machine **running** if it is safe (the grease distributes and purges) and **warm**; the Baldor manual says grease while stationary and warm and then run 15 minutes; either way not cold.
3. **Remove the drain (relief) plug** on housings and motors that have one (the plug opposite the fitting, at the bottom of the bearing cap); clean the drain of hardened grease with a wire; on motors with a **grease relief fitting** or a spring relief, check it is not plugged.
4. Pump the **calculated amount slowly** (one stroke every few seconds); watch the drain for old grease; on a sealed insert with a fitting, one to two strokes only.
5. Leave the drain open and the machine running **15-30 minutes** (motors: run with the drain out so the excess purges, then refit the plug); wipe the purge; on a pillow block, wipe the seal purge.
6. Refit the plug; record the date, the amount and the grease; feel the housing temperature at the next round (a rise of 10-20°F that settles in a day is normal after greasing; a rise that persists is over-greasing).
7. Do not grease: **sealed bearings (2RS)** (no path in; the grease blows the seal), bearings with **no fitting** (lubed for life), **shielded bearings with a fitting** only per the maker (the shield lets grease pass slowly), TEFC motor fans (no), variable-speed drives' bearings on the inverter's own schedule.

## Over-greasing

![A bearing packed by hand: fill the bearing, not the housing](/photos/lubrication/greased-bearing.jpg)

*A bearing packed by hand: fill the bearing, not the housing. Photo: User:SkyMWard, CC BY-SA 3.0, via commons*

| Sign | What is happening |
|---|---|
| Bearing housing runs **hotter** after greasing and stays hot | The full housing churns; the grease oxidises |
| Grease **inside the motor** (on the windings, out of the fan end) | The cavity behind the bearing cap is full and the grease has nowhere to go but through the inner seal into the motor: a winding failure waits |
| Grease squeezing out of the seals in fat rings, seals pushed out | Pressure |
| Grease **darkened/burnt** at the drain | Overheated from churning |
| The gun is hard to pump, the fitting balls up | The housing is full: stop |

Over-greasing kills more motor bearings than under-greasing; the right amount is small and the interval is long.

## Sealed, shielded and lubed-for-life

- **2RS / 2RSR (rubber seals)**: sealed; no regreasing; life = grease life (typically 3-5 years, less hot).
- **2Z / ZZ (metal shields)**: shielded, not sealed; on a motor with a fitting, grease can pass the shield's gap into the bearing slowly; the maker's table applies with reduced quantities.
- Open bearings in a greased housing: the tables above.
- Sealed pillow block inserts with a fitting: a purge of the seal cavity, 1-2 strokes.

## Related

- [Grease types and compatibility](/article/grease-types-and-compatibility)
- [Lube routes and single-point lubricators](/article/lube-routes-and-single-point-lubricators)
- [Bearing failure analysis (over-greasing, lubrication failure)](/article/bearing-failure-analysis)
- [Pillow blocks and insert bearings](/article/pillow-block-and-insert-bearings)
- [Bearing designation codes](/article/bearing-designation-codes)
- [Reading a motor nameplate](/article/reading-a-motor-nameplate)
