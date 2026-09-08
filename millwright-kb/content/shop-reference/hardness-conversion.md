---
title: "Hardness Conversion Chart: Rockwell C and B, Brinell, Vickers and Approximate Tensile Strength for Steel, with the File Test, Portable Testers and What Hardness Numbers Mean on Drawings"
slug: hardness-conversion
category: shop-reference
kind: chart
tags: [hardness conversion, Rockwell C, HRC, Rockwell B, HRB, Brinell, HB, BHN, Vickers, HV, tensile from hardness, hardness to tensile, file hardness test, hardness files, Leeb tester, portable hardness tester, shaft hardness, HRC to HB, HB to HRC, surface hardness, case depth]
source: "ASTM E140 (Standard Hardness Conversion Tables for Metals, non-austenitic steels) and ASTM A370 (hardness-tensile relationship); ISO 18265; SAE J417; Machinery's Handbook; file hardness test set data (Flexbar / Tsubosan)."
summary: "One table to convert between Rockwell C, Rockwell B, Brinell, Vickers and approximate tensile strength for carbon and alloy steel, the rules for when the conversion is valid, how to test hardness in the field with a file set, a Leeb tester or a portable Rockwell, and how to read hardness call-outs on drawings and bearing specs."
---

> Conversions are **approximate** and only for non-austenitic steels (carbon, alloy, tool, martensitic stainless). Aluminium, brass, austenitic stainless and cast iron have their own tables. A number converted twice is a guess. The tensile column is a rule of thumb, not a substitute for a test certificate.

## Steel: HRC, HB, HV, HRB and tensile (ASTM E140 / A370)

| HRC | Vickers HV | Brinell HB (3,000 kg, 10 mm ball) | HRB | Approx. tensile (ksi) | Approx. tensile (MPa) | Typical of |
|---|---|---|---|---|---|---|
| 68 | 940 | – | – | – | – | Files, HSS at maximum |
| 65 | 832 | – | – | – | – | HSS cutters, 52100 bearings, carbide-tipped |
| 62 | 746 | (688 W) | – | – | – | O1/W1 knives and punches, bearing races (58-64) |
| 60 | 697 | (654 W) | – | – | – | Hardened tool steel, ball bearings, hardfacing (chromium carbide) |
| 58 | 653 | (615 W) | – | – | – | Case-hardened gears (58-62), induction-hardened shafts |
| 55 | 595 | 560 | – | – | – | Shear blades, hard chrome plate (65-70 HRC) sits above this |
| 52 | 544 | 512 | – | (270) | (1,860) | Springs, hardened 4140 (54-57 as quenched) |
| 50 | 513 | 481 | – | 246 | 1,700 | Flame-hardened 1045 journals (50-58), S7 chisels |
| 48 | 484 | 455 | – | 232 | 1,600 | |
| 46 | 458 | 432 | – | 220 | 1,520 | Hardened bolts (Grade 8 tops at 39), hardfacing (martensitic) |
| 45 | 446 | 421 | – | 212 | 1,460 | |
| 44 | 434 | 409 | – | 204 | 1,410 | H13 hot-work tooling (44-52) |
| 42 | 412 | 390 | – | 196 | 1,350 | |
| 40 | 392 | 371 | – | 182 | 1,260 | 4340 Q&T high-strength shafts (36-40), 410 stainless hardened |
| 38 | 372 | 353 | – | 171 | 1,180 | AR400 plate (360-440 HB), Grade 8 bolts (33-39) |
| 36 | 354 | 336 | – | 162 | 1,120 | |
| 34 | 336 | 319 | – | 152 | 1,050 | |
| 32 | 318 | 301 | – | 146 | 1,010 | **4140 pre-hard (28-32)**, Grade 8 bolts low end, P20 |
| 30 | 302 | 286 | – | 138 | 950 | Grade 5 bolts (25-34), 17-4 H1150 |
| 28 | 286 | 271 | – | 131 | 900 | 4140 Q&T low end |
| 26 | 272 | 258 | – | 124 | 850 | Ductile iron 80-55-06 (about 240-300 HB) |
| 24 | 260 | 247 | (101) | 118 | 815 | 1144 Stressproof (250 HB) |
| 22 | 248 | 237 | 100 | 112 | 770 | Weld deposit E7018 (about 200-240 HB) |
| 20 | 238 | 226 | 98 | 107 | 740 | 4140 annealed (197 HB) is just below |
| (18) | 228 | 217 | 96 | 105 | 725 | Ductile 65-45-12 (170-230 HB), grey iron class 40 |
| (15) | 210 | 200 | 93 | 95 | 655 | Grey iron class 30 (180-220 HB), 1045 HR (163 HB) is below |
| (12) | 190 | 180 | 89 | 87 | 600 | |
| (8) | 170 | 163 | 85 | 80 | 550 | 1045 hot-rolled, A572-50 |
| (3) | 155 | 149 | 80 | 73 | 500 | |
| – | 143 | 137 | 76 | 67 | 460 | A36 plate (about 120-160 HB), 1018 CR (126 HB) |
| – | 127 | 121 | 70 | 60 | 415 | 1018 HR, 1020 |
| – | 117 | 111 | 65 | 55 | 380 | Low-carbon, annealed |
| – | 105 | 100 | 58 | 50 | 345 | Dead-soft steel |

Notes: "W" = tungsten carbide ball (the steel ball is not valid above 444 HB / 47 HRC). HRB is used below about 20 HRC (HRB 100 ≈ 20-22 HRC); the scales overlap between HRB 90 and 100 but neither is accurate there, which is why drawings for soft parts call out HB. Bracketed HRC values below 20 are extrapolations and not a real Rockwell C reading.

**Rule of thumb for steel**: **tensile (ksi) ≈ 0.5 × HB** (more exactly 0.485-0.5 up to about 400 HB); **tensile (MPa) ≈ 3.45 × HB**. Yield is roughly 0.75-0.85 of tensile for Q&T steels, 0.5-0.6 for hot-rolled mild steel. 1 HRC point ≈ 8-10 HB in the 20-40 HRC range.

## Other scales you will see

| Scale | Indenter / load | Used for |
|---|---|---|
| **HRC** (Rockwell C) | 120° diamond cone, 150 kg | Hardened steel, 20-70 HRC; the shop standard |
| **HRB** (Rockwell B) | 1/16 in ball, 100 kg | Soft steel, brass, aluminium, 0-100 HRB |
| **HRA** | Diamond, 60 kg | Carbides (85-93 HRA), thin case-hardened layers |
| **HR15N / 30N / 45N** (superficial) | Diamond, 15/30/45 kg | Thin cases, nitrided surfaces, sheet; HR15N 90 ≈ 60 HRC |
| **HB** (Brinell) | 10 mm ball, 3,000 kg (500 kg for aluminium/soft metals) | Castings, forgings, plate, structural, AR plate (large indent averages a coarse structure) |
| **HV** (Vickers) | Diamond pyramid, 1-120 kg | Labs, welds (HV10 across a HAZ), thin layers; single continuous scale |
| **HK** (Knoop) | Elongated diamond, light loads | Micro-hardness, coatings |
| **HL** (Leeb) | Rebound of a tungsten-carbide ball | Portable testers (Equotip type); converts to HRC/HB by the instrument, only accurate on heavy (over about 10 lb), rigid, clean, finished parts |
| **Shore scleroscope** | Drop hammer rebound | Old drawings; Shore 90 ≈ 65 HRC |
| **Mohs** | Scratch | Minerals, not metals |
| **Shore A / D durometer** | Rubber and plastics | O-rings (70 A typical), urethane (90 A), Hytrel (55 D); not comparable to metal scales |

Aluminium: 6061-T6 ≈ 95 HB (500 kg) ≈ 60 HRB; 7075-T6 ≈ 150 HB; cast 356-T6 ≈ 80 HB. Copper alloys: C932 bronze ≈ 65 HB; C954 aluminium bronze ≈ 170 HB; brass 360 ≈ 60 HRB. Austenitic stainless: 304 annealed ≈ 150-200 HB (up to 300+ cold-worked); no HRC (they are in HRB or HB).

## Field testing

**File test (hardness file set)**: six files hardened to **40, 45, 50, 55, 60 and 65 HRC**, colour-coded. Draw each file across an edge with firm pressure starting from the softest: the first file that **skates** (will not bite) means the part is at or above that file's hardness; the last that bites is below it. Accuracy about ±3 HRC on a clean, unscaled corner. Without a set: a new mill file (about 62-64 HRC) bites into anything under about 55-58 HRC and skates on hardened bearing races and tool steel; a scratch awl (55-60) tells you soft from hard. Test on a ground spot, not on scale or a case that may be thin.

**Portable Leeb (rebound) tester**: quick and non-marking; needs a mass over about 10 lb (or coupling to a block), a smooth ground spot (under 1.6 µm Ra for the D probe), thickness over 3/16 in (or coupled), and a reading taken as the average of 5 impacts at least 1/8 in apart; reads high on thin sections and on parts that ring. Calibrate on the test block that comes with it before a job that matters.

**Portable Rockwell or Brinell (clamp-on)**: accurate on the part when the anvil and indenter are square and the surface is prepared; the King portable Brinell is the standard for plate and castings in the field.

**Bench Rockwell** rules: flat, clean, scale-free surface, ground both sides for thin parts; part thickness at least 10× the indent depth (about 1/16 in for 20 HRC, thinner for harder); indents at least 3 diameters apart and from the edge; the first reading after changing the anvil or indenter is discarded; verify on the test block daily.

## Reading hardness on drawings and specs

- **"HRC 58-62"** on a shaft journal or gear tooth: surface hardness, usually with a case depth call-out: "**effective case depth 0.030-0.040 in at 50 HRC**" means the depth at which hardness has dropped to 50 HRC. Total case depth is deeper. A regrind that takes 0.020 in off a 0.030 in case leaves nothing.
- **"Through-hardened 28-32 HRC"**: pre-hard 4140 or Q&T; the whole section. Machinable with carbide.
- **"Induction-hardened 0.060 in min, 55 HRC min"**: the hardened zone is local (a journal, a tooth flank); the rest of the shaft is the base hardness (about 20 HRC for 1045).
- **"250-300 HB"** on a plate or casting: Brinell, because it is soft or coarse.
- **"Hard chrome 0.002-0.003 in, 65-70 HRC"**: a plated layer; the substrate is whatever the base was.
- **Bearing steel** (52100 rings and rollers) is 58-64 HRC; a shaft seat should be **over 300 HB (about 32 HRC)** for heavy interference fits on rotating shafts to avoid fretting, and a set-screw insert bearing wants a shaft under about 35 HRC so the screw can bite.
- **Weld deposits**: E7018 about 200-240 HB; hardfacing 45-62 HRC; a HAZ over 350 HV on a carbon steel means it hardened and may crack (that number is why preheat exists; see [preheat and CE](/article/preheat-interpass-and-carbon-equivalent)).
- **Bolts**: Grade 5 25-34 HRC, Grade 8 33-39 HRC, 8.8 22-32, 10.9 32-39, 12.9 39-44.

## Worked example

A drawing says a sprocket tooth is "58 HRC min, case 0.040 in". You have a file set: the 55 file skates, the 60 file bites lightly. Result: about 55-60 HRC at the surface: borderline; a Leeb tester on the hub face (the hub is soft: 20 HRC, that is normal) and on a ground flat on the tooth reads 59 HRC: accept. A worn tooth reground 0.045 in deep is below the case: the tooth is now 20 HRC and will wear in weeks.

## Related

- [Steel grades and heat colours (tempering hardness table)](/article/steel-grades-and-heat-colours)
- [Metal identification and spark test](/article/metal-identification-and-spark-test)
- [Bolt torque chart and bolt grades](/article/bolt-torque-chart-sae-metric)
- [Bearing clearance and fits](/article/bearing-clearance-and-fits-tables)
- [Hardfacing and build-up](/article/hardfacing-and-buildup)
