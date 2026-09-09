---
title: "Reducer Selection and Service Factor: AGMA Service Factor Tables by Application and Duty, Mechanical versus Thermal Rating, Ratio and Output Speed, Overhung Load, Choosing a Replacement from the Catalogue"
slug: reducer-selection-and-service-factor
category: gearboxes
kind: reference
manufacturer: "AGMA / Dodge / Falk / SEW / Nord (generic)"
model_numbers: ["Dodge Torque-Arm II", "Dodge Quantis", "Falk Enclosed Drive", "SEW-Eurodrive R/F/K series", "Nord SK series", "Boston Gear"]
tags: [service factor, AGMA service factor, gearbox selection, reducer selection, reducer sizing, thermal rating, mechanical rating, overhung load, OHL, gearbox ratio, output speed, load classification, uniform moderate heavy shock, gear reducer catalogue, gearmotor selection, gearbox replacement, duty cycle hours per day]
source: "AGMA 6013 and ANSI/AGMA 9005 service factor and lubrication standards; Dodge Torque-Arm II and Quantis selection guides (service factor tables, overhung load formulas); Falk enclosed drive catalogue (thermal ratings); SEW-Eurodrive gearmotor catalogue (fB service factor and load classification)."
summary: "How to size or replace a gear reducer from the catalogue: turn the motor power and the application into a required rating with the AGMA service factor, check the box against both its mechanical and its thermal rating, get the ratio from the speeds, and check overhung load on the output shaft before you order."
---

## The idea

A reducer is rated for a **uniform** load over 10 hours a day. Real machines are not uniform. The **service factor** (SF) is the multiplier that turns the motor's power into the reducer rating you must buy:

![Five checks for selecting a reducer](/img/gearboxes/service-factor-selection.svg)

*Five checks for selecting a reducer*

**Required reducer rating = motor power × service factor**

A 10 hp motor on a bucket elevator running 24 hours (SF 1.75) needs a box rated for at least 17.5 hp at the output speed. Buying a "10 hp" box gives short bearing and gear life, which is the usual reason a replacement box fails again.

## Load classification (AGMA)

| Class | Meaning | Examples |
|---|---|---|
| Uniform (U) | steady, no shock | centrifugal pumps and fans, belt conveyors uniformly loaded, agitators for liquids |
| Moderate shock (M) | variable load, some shock | bucket elevators, screw conveyors, mixers with solids, reciprocating compressors (multi-cylinder), hoists |
| Heavy shock (H) | frequent heavy shock or reversals | crushers, hammer mills, reciprocating feeders, car dumpers, single-cylinder compressors |

## Typical service factors (electric motor drive)

| Load class | up to 3 h/day | 3 to 10 h/day | over 10 h/day |
|---|---|---|---|
| Uniform | 1.00 | 1.00 | 1.25 |
| Moderate shock | 1.00 | 1.25 | 1.50 |
| Heavy shock | 1.25 | 1.50 | 1.75 |

Add about 0.25 for internal-combustion engine drives with multiple cylinders and 0.50 for single-cylinder engines. Manufacturers publish their own tables listing hundreds of applications; use the manufacturer's table when you have it, because the box rating was derived against it.

Frequent starts (more than 10 an hour) and reversing duty push the factor up a step. Brake motors or plugging count as heavy shock.

## Mechanical rating versus thermal rating

A catalogue box has two ratings at each ratio and input speed:

- **Mechanical rating**: the power the gears and bearings carry for their design life (typically 25,000 hours L10 for bearings under uniform load).
- **Thermal rating**: the power the box can shed as heat continuously without the oil going over about 93 °C (200 °F) in a 25 °C ambient with no fan.

Select on the smaller of the two. Small boxes at high ratio are mechanically limited; large boxes at high input speed and low ratio are thermally limited. Options for a thermally limited box: shaft fan, cooling coil, a larger box, or accepting a lower continuous duty (the thermal rating is for continuous running; intermittent duty tables allow more).

Worm reducers are almost always thermally limited because of sliding friction; check the thermal column first.

## Ratio and output speed

Ratio = input rpm ÷ required output rpm. A 1750 rpm motor and a 35 rpm conveyor head shaft need 50:1; you would pick the nearest catalogue ratio (say 50.6:1) and live with 34.6 rpm, or change the belt drive between motor and reducer to correct it. Check the catalogue output speed, not the nominal ratio, when speed matters.

Output torque (lb·in) = 63,025 × hp ÷ output rpm. That torque must be within the box rating, and the coupling, sprocket and shaft downstream must take it.

## Overhung load

When the output shaft carries a sprocket, sheave or pinion, the belt or chain pull is a bending load on the output bearings. The catalogue gives an allowable **overhung load (OHL)** at the shaft midpoint.

OHL (lb) = 126,000 × hp × K ÷ (rpm × pitch diameter in inches)

with K = 1.00 for chain sprockets, 1.25 for gears, 1.50 for V-belt sheaves, 2.50 for flat belts. If the calculated OHL exceeds the allowable, use a larger pitch diameter, move the sheave closer to the bearing, or use an outboard bearing. Shaft-mount reducers (Torque-Arm type) avoid the problem because the output is the driven shaft itself.

## Choosing a replacement

![Reducers of the same frame size come in many ratios: read the nameplate, not the housing](/photos/gearboxes/industrial-gearboxes.jpg)

*Reducers of the same frame size come in many ratios: read the nameplate, not the housing. Photo: Yuexin indonesia, CC BY-SA 4.0, via commons*

1. Read the nameplate: model, ratio, input hp, mounting position, and the **frame size** (the catalogue family).
2. Confirm it was not undersized: work out the SF from the application and check the old box rating. If it failed early, upsize now.
3. Match: ratio (nearest, or a different ratio with a belt change), shaft sizes and centre distance (or plan new couplings and base), mounting position, output rotation, and thermal rating.
4. Check the input: direct coupled motor, C-face gearmotor, or belt drive; C-face requires the same NEMA flange and shaft.
5. Order oil and breather orientation for the mounting position at the same time.

## Worked example

Screw conveyor, 7.5 hp motor at 1750 rpm, screw at 60 rpm, 16 hours a day, chain drive from the reducer.

- Class: moderate shock; over 10 h: SF 1.50.
- Required rating: 7.5 × 1.5 = 11.25 hp.
- Ratio: 1750 ÷ 60 = 29:1; nearest catalogue 30:1 gives 58 rpm.
- Output torque at 7.5 hp: 63,025 × 7.5 ÷ 58 = 8,150 lb·in.
- Pick the box whose 30:1 mechanical rating at 1750 rpm input is at least 11.25 hp and whose thermal rating is at least 7.5 hp (the actual motor power, since heat depends on transmitted power).
- OHL with an 8 in pitch sprocket: 126,000 × 7.5 × 1.0 ÷ (58 × 8) = 2,037 lb; check against the catalogue OHL.

## Related

- [Worm, Planetary and Cycloidal Reducers](/article/planetary-and-worm-reducers)
- [Dodge Torque-Arm Shaft-Mount Reducer](/article/dodge-torque-arm-shaft-mount-reducer)
- [Power, Torque, Speed and Drive Formulas](/article/power-torque-speed-drive-formulas)
- [How to Read a Coupling and Sheave Selection Table](/article/how-to-read-a-coupling-and-sheave-selection-table)
