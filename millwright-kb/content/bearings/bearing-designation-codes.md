---
title: "Decoding Bearing Numbers: Types, Series, Bore Codes and Suffixes (6205-2RS C3, 22220 EK, NU 210 ECP)"
slug: bearing-designation-codes
category: bearings
kind: reference
tags: [bearing number, bearing designation, bore code, suffix, 2RS, ZZ, C3, K, EK, CC, ECP, NU, NJ, dimension series, ISO 15, interchange]
source: "ISO 15 / ISO 104 designation system; SKF, FAG, NSK, Timken catalogues."
summary: "How to read any metric rolling-bearing designation: the type digit, dimension series, bore code (× 5 rule), and the common prefix and suffix codes for seals, shields, clearance, tapered bores and cage material."
---

## Basic layout

![Bearing parts and the meaning of 6205-2RS C3](/img/bearings/bearing-parts-and-number.svg)

*Bearing parts and the meaning of 6205-2RS C3*

```
[prefix]  TYPE  SERIES  BORE  [suffixes]

   6   2   05   -2RS  C3
   |   |   |     |     |
   |   |   |     |     +-- clearance class: C3 (more than Normal)
   |   |   |     +-------- two rubber contact seals
   |   |   +-------------- bore code 05 → 05 × 5 = 25 mm bore
   |   +------------------ dimension series 2 (light, "02")
   +---------------------- type 6 = single-row deep groove ball bearing
```

## Type (first digit or letters)

![Deep groove ball bearing (type 6) in section: inner ring, balls, cage, outer ring](/photos/bearings/ball-bearing-cutaway.jpg)

*Deep groove ball bearing (type 6) in section: inner ring, balls, cage, outer ring. Photo: Silberwolf, CC BY 2.5, via commons*

| Code | Bearing type |
|---|---|
| **1** | Self-aligning ball bearing (12xx, 13xx, 22xx, 23xx with "E") |
| **2** | Spherical roller bearing (22xxx, 23xxx, 21xxx, 24xxx) and spherical roller thrust (29xxx) |
| **3** | Tapered roller bearing, metric (30xxx, 32xxx, 33xxx) |
| **4** | Double-row deep groove ball |
| **5** | Thrust ball bearing (51xxx, 52xxx) |
| **6** | Single-row deep groove ball (60xx, 62xx, 63xx, 64xx, 160xx) |
| **7** | Single-row angular contact ball (72xx, 73xx) |
| **N, NU, NJ, NUP** | Cylindrical roller: N = ribs on inner ring only; NU = ribs on outer ring only (inner floats); NJ = NU plus one inner rib (locates one direction); NUP = NJ plus a loose rib (locates both) |
| **NA, NK, RNA** | Needle roller bearings |
| **QJ** | Four-point contact ball |
| **C** | CARB toroidal roller (SKF) |
| **UC, UCP, SA, YAR, YET** | Insert ("Y") bearings for pillow blocks |

## Dimension series

The digit(s) after the type give the **width series** and **diameter series** (ISO 15). For a given bore, a higher diameter series is a bigger, stronger bearing:

![Cylindrical roller bearing (type N/NU): same bore code, different series and load rating](/photos/bearings/cylindrical-roller-cutaway.jpg)

*Cylindrical roller bearing (type N/NU): same bore code, different series and load rating. Photo: Silberwolf, CC BY 2.5, via commons*

| Series | Example for 25 mm bore | Outside diameter | Width |
|---|---|---|---|
| 60 (extra light) | 6005 | 47 mm | 12 mm |
| 62 (light) | 6205 | 52 mm | 15 mm |
| 63 (medium) | 6305 | 62 mm | 17 mm |
| 64 (heavy) | 6405 | 80 mm | 21 mm |

Same rule applies across types: 6205, 7205, NU 205, 32005 all share the 25 mm bore and the 52 mm outside diameter of the "05" light series.

## Bore code (last two digits)

| Code | Bore |
|---|---|
| 00 | 10 mm |
| 01 | 12 mm |
| 02 | 15 mm |
| 03 | 17 mm |
| 04 to 96 | **code × 5 mm** (04 = 20, 05 = 25, 10 = 50, 20 = 100, 22 = 110, 44 = 220) |
| /500 and above | bore in mm written after a slash (e.g. 230/500) |
| Small bearings (bore < 10 mm) | bore in mm written directly (e.g. 608 = 8 mm, 625 = 5 mm) |

Spherical roller **22220**: type 2, series 22, bore 20 × 5 = 100 mm. Tapered roller **32210**: type 3, series 22, bore 50 mm.

## Common suffixes

| Suffix | Meaning |
|---|---|
| **2RS / 2RS1 / 2RSR / DDU / LLU** | Two contact rubber seals (grease for life) |
| **RS** | One rubber seal |
| **2Z / ZZ / 2ZR** | Two steel shields (non-contact) |
| **Z** | One shield |
| **C2** | Clearance less than Normal |
| **CN / (blank)** | Normal clearance |
| **C3** | Clearance greater than Normal (motors, hot applications, interference fits) |
| **C4 / C5** | Progressively more clearance (vibrating screens, high temperature) |
| **K** | Tapered bore, taper 1:12 |
| **K30** | Tapered bore, taper 1:30 |
| **E / EC / ECP / ECJ / EK** | Reinforced/optimised internal design (SKF): more or larger rollers; P = polyamide cage, J = pressed steel cage |
| **CC / CCK / CA / CAK / MB / MA** | Spherical roller internal design and cage: CC = pressed steel window cage (SKF), CA = machined brass cage, MB/MA = machined brass (FAG) |
| **M / MA / MB** | Machined brass cage |
| **TN / TNH / TVP / P** | Polyamide cage |
| **J / JR** | Pressed steel cage |
| **N** | Snap-ring groove in outer ring; **NR** = groove plus snap ring |
| **W33** | Lubrication groove and holes in the outer ring (spherical rollers) |
| **VA / HT / WT** | Special grease or high-temperature versions |
| **P5 / P6 / ABEC 5 / ABEC 7** | Precision class (tighter than normal) |
| **DB / DF / DT** | Angular-contact pairs: back-to-back, face-to-face, tandem |
| **-2RS1TN9/C3** style | Multiple suffixes strung together; read each in turn |

## Worked examples

| Designation | Read as |
|---|---|
| **6205-2RS C3** | Deep groove ball, light series, 25 mm bore, two contact seals, C3 clearance. Typical small-motor bearing. |
| **6309 ZZ** | Deep groove ball, medium series, 45 mm bore, two shields. |
| **22220 EK C3** | Spherical roller, series 22, 100 mm bore, SKF E design, tapered bore 1:12, C3 clearance. Needs an H 320 sleeve on a 90 mm shaft. |
| **23144 CCK/W33** | Spherical roller, series 231, 220 mm bore, steel cage, tapered bore, lubrication groove. Big fan or crusher bearing. |
| **NU 210 ECP** | Cylindrical roller, outer-ring ribs (floats axially), series 2, 50 mm bore, reinforced design, polyamide cage. Gearbox "free" position. |
| **32210** | Metric tapered roller, series 22, 50 mm bore. Set the axial clearance at installation. |
| **7210 BECBP** | Angular contact ball, 50 mm bore, 40° contact angle (B), single bearing for universal matching (CB), polyamide cage. |
| **UCP 210** | Pillow-block unit with a set-screw insert bearing, 50 mm bore. |

## Interchange

The number is standardised, so a 6205-2RS C3 from SKF, FAG, NSK, NTN, Koyo or Timken is dimensionally the same. Suffix spellings differ between makers (2RS1 vs 2RSR vs DDU vs LLU all mean two contact seals). Cage type and internal design codes are **not** interchangeable one-for-one; match the load rating and the clearance, and check with the maker's interchange guide for anything on a critical machine.

## Related

- [Mounting bearings with heat](/article/bearing-mounting-with-heat)
- [Tapered-bore bearing on an adapter sleeve](/article/taper-bore-bearing-adapter-sleeve-skf)
