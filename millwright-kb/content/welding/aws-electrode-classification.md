---
title: "Decoding AWS Electrode and Wire Numbers: E7018-1 H4R, ER70S-6, E71T-1C, E308L-16, ER4043, E71T-11 and More"
slug: aws-electrode-classification
category: welding
kind: reference
tags: [AWS classification, electrode number, E7018 meaning, ER70S-6 meaning, E71T-1, E71T-11, E308L-16, ER4043, ER5356, H4R, filler metal, wire classification, A5.1, A5.18, A5.20, A5.4, A5.9, A5.10, CSA W48, E4918]
source: "AWS A5.1 (carbon steel covered electrodes), A5.5 (low-alloy covered), A5.18 (carbon steel solid wire), A5.20 (carbon steel flux-cored), A5.4 (stainless covered), A5.9 (stainless bare wire), A5.10 (aluminium), A5.15 (cast iron), A5.36; CSA W48."
summary: "How to read every filler-metal number you will meet on a box or a WPS: covered electrodes, solid MIG/TIG wire, flux-cored wire, stainless, aluminium and cast-iron rods, plus the Canadian CSA equivalents."
---

![Decoding E7018-1 H4R digit by digit](/img/welding/aws-electrode-decoder.svg)

*Decoding E7018-1 H4R digit by digit*

## Covered (stick) electrodes: AWS A5.1 and A5.5

![The classification is printed on every rod near the bare end](/photos/welding/electrode-types.jpg)

*The classification is printed on every rod near the bare end. Photo: Ghasemimoshref, CC BY-SA 4.0, via commons*

```
E 70 1 8 - 1  H4 R
│ │  │ │   │   │  └ R = moisture-resistant coating (9 h exposure instead of 4)
│ │  │ │   │   └── H4 = diffusible hydrogen ≤ 4 mL/100 g (H8 = ≤ 8, H16 = ≤ 16)
│ │  │ │   └────── -1 = improved toughness (Charpy at -50°F instead of -20°F)
│ │  │ └────────── 8 = coating/current type (see table)
│ │  └──────────── 1 = position: 1 all positions, 2 flat + horizontal fillet, 4 all incl. vertical-down
│ └─────────────── 70 = minimum tensile strength, ksi (60, 70, 80, 90, 100, 110, 120)
└───────────────── E = electrode (arc)
```

Last digit (coating and current):

| Digit | Coating | Current | Penetration | Examples |
|---|---|---|---|---|
| 0 | cellulose sodium | DC+ only | deep | E6010, E7010 |
| 1 | cellulose potassium | AC or DC+ | deep | E6011 |
| 2 | rutile sodium | AC or DC− | medium | E6012 |
| 3 | rutile potassium | AC or DC± | light | E6013 |
| 4 | rutile + iron powder | AC or DC± | light | E7014 |
| 5 | low-hydrogen sodium | DC+ | medium | E7015 |
| 6 | low-hydrogen potassium | AC or DC+ | medium | E7016 |
| 7 | iron oxide + iron powder | AC or DC− | medium | E6027, E7027 |
| 8 | low-hydrogen potassium + iron powder | AC or DC+ | medium | **E7018**, E7028 (flat/horizontal, 2 = position digit) |

Low-alloy suffixes (A5.5): **-A1** 1/2% Mo; **-B2** 1-1/4 Cr 1/2 Mo; **-B3** 2-1/4 Cr 1 Mo; **-C1** 2-1/2% Ni; **-C2** 3-1/4% Ni; **-C3** 1% Ni; **-D1/-D2** Mn-Mo; **-G** general (chemistry by agreement); **-M** military (high strength, e.g. E11018-M); **-W** weathering steel; **-P1** pipe (E7010-P1, E8010-P1).

## Solid wire for MIG and TIG: AWS A5.18 (carbon steel)

```
ER 70 S - 6
│  │  │   └ chemistry / deoxidiser level: 2, 3, 4, 6, 7, G
│  │  └──── S = solid wire (C = composite / metal-cored)
│  └─────── 70 = min tensile ksi (as welded)
└────────── ER = electrode or rod (usable as a MIG electrode or a TIG filler rod)
```

| Wire | Deoxidisers | Use it for |
|---|---|---|
| **ER70S-2** | triple-deoxidised (Al, Ti, Zr) | TIG root passes on pipe, dirty or rimmed steel, best for TIG on mild steel |
| **ER70S-3** | medium Si/Mn | Clean steel, general MIG |
| **ER70S-6** | high Si/Mn | **The default MIG wire**: tolerates mill scale and light rust, wets out well, CO2 or C25 |
| ER70S-7 | high Mn | Faster travel, stiffer puddle |
| ER80S-D2, ER80S-Ni1, ER90S-B3 | low-alloy (A5.28) | Higher strength, Cr-Mo, low-temperature toughness |
| E70C-6M | metal-cored (composite) | Spray-like high deposition, low slag, mixed gas only |

## Flux-cored wire: AWS A5.20 (carbon steel)

```
E 7 1 T - 1 C  H8
│ │ │ │   │ │   └ optional hydrogen designator
│ │ │ │   │ └──── shielding: C = 100% CO2, M = 75-80% Ar mixed gas; (none) = self-shielded
│ │ │ │   └────── usability number 1-14 (see table)
│ │ │ └────────── T = tubular (flux-cored)
│ │ └──────────── 1 = all positions (0 = flat and horizontal only)
│ └────────────── 7 = min tensile 70 ksi
└──────────────── E = electrode
```

| Usability | Shielding | Polarity | Character |
|---|---|---|---|
| **T-1** | gas (C or M) | DC+ | Rutile slag, spray-like arc, all positions, smooth: **E71T-1C/M** is the standard structural wire (Outershield 71M, Dual Shield 7100) |
| T-5 | gas | DC+ | Basic slag, tougher, more spatter, crack-resistant |
| T-6 | self-shielded | DC+ | Flat/horizontal, deep penetration, high deposition (Innershield NR-305) |
| T-8 | self-shielded | DC− | All positions, good impact toughness, structural field welding (NR-232) |
| T-9 | gas | DC+ | T-1 with better impacts |
| **T-11** | self-shielded | **DC−** | General-purpose all-position, single or limited multi-pass, thin to 1/2" (**NR-211-MP**, E71T-11) |
| T-14 | self-shielded | DC− | Galvanised and coated sheet, single pass |
| T-GS | self-shielded | DC− | Single-pass sheet metal (small-spool "gasless" wire) |

Self-shielded wires run **DC−** (electrode negative); gas-shielded run DC+. Getting this wrong is the most common flux-core setup mistake.

The newer AWS A5.36 combined spec writes the same wire as E71T-1C-J-H8 style codes; E71T-11-AZ-CS3 on a NR-211 box is the A5.36 form of E71T-11.

## Stainless electrodes and wires: A5.4 and A5.9

```
E 308 L - 16        ER 308 L        E 308L T1-1 (flux-cored, A5.22)
  │   │    └ coating: -15 basic DC+ only; -16 rutile AC/DC+; -17 rutile-silica AC/DC+, smoother, best for horizontal fillets
  │   └ L = low carbon (≤ 0.04% C) to resist carbide precipitation (sensitisation)
  └ AISI type of the deposit
```

| Filler | Welds | Notes |
|---|---|---|
| 308L | 304, 304L, 301, 302 | The everyday stainless filler |
| 309L | stainless to carbon steel, 309, cladding, buffer layers | Higher Cr/Ni tolerates dilution |
| 316L | 316, 316L (marine, chemical) | Mo for pitting resistance |
| 310 | 310, high temperature | Fully austenitic, crack-sensitive |
| 312 | dissimilar and hard-to-weld steels, spring steel repairs | Very high ferrite |
| 347 | 321, 347 (stabilised) | Nb-stabilised |
| 2209 | duplex 2205 | |
| 410, 410NiMo | martensitic stainless, pump impellers, turbine repair | Preheat and PWHT |

## Aluminium: A5.10

```
ER 4043      ER 5356
```

| Wire | Alloy family | Use |
|---|---|---|
| **ER4043** | 5% Si | 6061, 6063, castings (356, A356); fluid, low crack tendency, less strength, darkens on anodising |
| **ER5356** | 5% Mg | 5052, 5083, 5086, 6061 when strength or colour match after anodising matters; stiffer wire feeds better; not for service above 150°F (sensitisation) |
| ER4047 | 12% Si | Brazing-like flow, thin castings |
| ER5556, ER5183 | high Mg | 5083 marine plate, highest strength |
| ER1100 | pure Al | 1100, 3003, electrical bus |

## Cast iron: A5.15

| Rod | Deposit | Use |
|---|---|---|
| **ENi-Cl** | ~99% Ni | Machinable repairs on grey iron, thin sections |
| **ENiFe-Cl** | 55% Ni 45% Fe | Stronger, heavier sections, less expansion mismatch, most common |
| ENiCu | Ni-Cu (Monel) | Older; colour match |
| ESt (steel) | steel | Non-machinable filling, cheap |
| RCI / RCI-A | cast iron rod (oxy-fuel) | Colour-matched furnace-preheated repairs |

## Hardfacing (A5.13 / A5.21)

Named by deposit type rather than a tidy code: build-up (EFe1 low-alloy), work-hardening manganese (EFeMn), chromium carbide (EFeCr), tungsten carbide (WC composite), cobalt (ECoCr-A "Stellite 6"), Ni-based. Choose by the wear mode: abrasion, impact, metal-to-metal, heat, corrosion.

## Canadian (CSA W48) equivalents

CSA writes strength in **MPa/10**: E4918 = E7018 (490 MPa ≈ 70 ksi), E4911 = E6011, E4310 = E6010, E4818 ... ER49S-6 = ER70S-6, E491T-9 = E71T-9. Positions and coating digits are the same idea. CWB certifies the electrodes under W48 and the welders and shops under W47.1; a Red Seal test asks for the CSA number.

## On the WPS / drawing

A welding procedure lists the classification, diameter, polarity, amperage/voltage range, travel speed, gas and flow, preheat and interpass. If the box in your hand does not match the WPS classification (including the C/M gas designator or the L), stop and ask; substituting E6013 for E7018 on a structural weld is a rejection and a hazard.

## Related

- [Stick electrode amperage chart](/article/smaw-electrode-chart)
- [MIG (GMAW) setup](/article/gmaw-mig-setup)
- [Gas-shielded flux-core setup](/article/fcaw-gas-shielded-setup) and [self-shielded flux-core setup](/article/fcaw-self-shielded-setup)
- [Welding stainless and dissimilar metals](/article/welding-stainless-and-dissimilar) and [welding aluminium](/article/welding-aluminium)
