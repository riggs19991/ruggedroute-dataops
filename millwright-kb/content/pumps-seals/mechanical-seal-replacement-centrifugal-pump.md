---
title: "Replacing a Mechanical Seal on a Centrifugal Pump (Component and Cartridge Seals)"
slug: mechanical-seal-replacement-centrifugal-pump
category: pumps-seals
kind: procedure
manufacturer: "Goulds / Flowserve / John Crane / Chesterton (generic)"
model_numbers: ["3196", "Type 21", "Type 1", "Type 2", "Chesterton 155", "Chesterton 180", "Flowserve ISC2"]
tags: [mechanical seal, centrifugal pump, seal replacement, cartridge seal, component seal, seal setting, stuffing box, shaft runout, impeller clearance, back pull-out, ANSI pump]
source: "Seal manufacturer installation sheets (John Crane, Chesterton, Flowserve); Goulds 3196 IOM."
summary: "Step-by-step seal replacement on a typical back pull-out ANSI process pump: disassembly, the shaft and stuffing-box checks that decide whether the new seal survives, component-seal setting dimension, cartridge-seal clips, impeller clearance and start-up."
---

## Why seals fail

Most seals do not wear out; they are killed. Dry running (no flush, pump not vented), shaft runout, pipe strain, misalignment, cavitation, wrong setting dimension, and elastomers damaged during installation account for nearly all early failures. Fix the cause or you will be back in a month.

## Before you start

1. Lockout/tagout motor. Close suction and discharge valves, **vent and drain** the pump. Confirm the fluid is safe to handle; wear the right gloves and face shield.
2. Get the seal drawing/installation sheet. Note the **setting dimension** (component seals) or confirm the cartridge is complete with its setting clips.
3. Mark coupling hub positions and note the impeller clearance setting if the pump has one (ANSI 3196 style: typically 0.015" cold, more for hot service; check the IOM).

## Disassembly (back pull-out pump)

1. Remove the coupling guard and coupling spacer/element.
2. Unbolt the bearing frame from the casing and pull the **rotating assembly** back on the frame adapter. The casing stays in the piping.
3. Remove the impeller (right-hand or left-hand thread; use the impeller wrench, never a chisel on the vanes).
4. Remove the seal gland and the old seal. Note where the rotary unit sat on the sleeve.
5. Remove the shaft sleeve if fitted.

## The checks that matter (write the numbers down)

| Check | Limit (typical ANSI pump) |
|---|---|
| Shaft or sleeve runout at the seal area | **≤ 0.002" TIR** |
| Shaft end float (axial) | ≤ 0.002" |
| Stuffing-box face squareness to the shaft | ≤ 0.002" TIR (dial indicator on shaft, sweeping the box face) |
| Stuffing-box bore concentricity to the shaft | ≤ 0.005" TIR |
| Sleeve surface where the seal O-ring/wedge sits | No grooves, scratches or corrosion; 32 µin finish or better |
| Bearings | Smooth, no play; replace while apart if in doubt |

Exceed these and the seal faces open and close every revolution. Fix (new sleeve, new bearings, machine the box face) before fitting the seal.

## Installing a component seal (rotary + stationary)

![Rotary unit, faces, gland and O-rings of a component seal](/img/pumps-seals/mechanical-seal-parts.svg)

*Rotary unit, faces, gland and O-rings of a component seal*

1. Clean everything. New gaskets and O-rings. Deburr keyways and shaft steps; **cover the keyway and threads with tape** so the O-ring cannot be cut sliding over them.
2. Fit the **stationary seat** into the gland with its O-ring or cup gasket. Lubricate the elastomer with **water, soapy water or the seal maker's lubricant**. Do not use petroleum oil on EPDM (it swells). Press in square with a clean, soft tool; never touch the lapped face with bare fingers. Wipe the face with a lint-free tissue and alcohol.
3. Slide the gland (with seat) onto the shaft, face inward.
4. **Set the rotary unit.** Measure from the stuffing-box face (or the reference the drawing uses) to the seal-setting mark and position the rotary unit on the sleeve at the **setting dimension** from the sheet. Too short = faces not loaded, leaks. Too long = faces overloaded, overheats. Tighten set screws (on hardened sleeves use the special cup-point screws or a clamp ring) evenly.
5. Install the impeller, set the impeller clearance per the IOM (adjust with the bearing-housing jack bolts and a dial indicator on the shaft), then confirm the seal setting dimension is still correct: on many pumps setting the impeller **moves the shaft** and must be done **before** the rotary unit is locked. Follow the IOM order for your pump.
6. Bolt the gland to the box evenly in a cross pattern. Check the gland is square (gap even all round).
7. Turn the shaft by hand; it must turn freely with a little drag from the faces.

## Installing a cartridge seal

1. Slide the complete cartridge onto the shaft/sleeve with the **setting clips in place**. Lubricate the sleeve O-ring with water or the maker's lube.
2. Bolt the gland to the box evenly.
3. Set the impeller clearance.
4. Tighten the cartridge set screws (the drive collar) to the shaft.
5. **Remove the setting clips** and store them on the gland for the next removal. Leaving clips in destroys the seal on start-up.
6. Turn by hand.

## Reassembly and start-up

1. Slide the rotating assembly back into the casing with a new casing gasket. Torque casing bolts in a cross pattern to the IOM value.
2. Connect the seal **flush**/quench lines (API plan 11, 13, 32 etc.). Confirm the flush orifice is clear.
3. Re-install the coupling, **align** the pump and motor, guard on.
4. Open the suction valve, **vent the seal chamber and the casing** until liquid runs out. Never start a pump with a dry seal.
5. Crack the discharge valve, start, bring to duty point. Check seal for leakage (a few drops in the first minutes is normal while faces bed in; continuous dripping is not), bearing temperature, vibration.
6. Record the seal type, setting dimension, impeller clearance and date.

## Troubleshooting seal leaks

| Sign | Cause |
|---|---|
| Leaks immediately on start | Faces damaged, wrong setting, O-ring cut on keyway, gland not square |
| Leaks after running hot | Dry run (no vent), flush blocked, overloaded faces |
| Faces cracked/heat-checked | Dry run, thermal shock |
| Sleeve fretted under O-ring | Shaft runout, vibration, misalignment |
| Elastomer swollen/soft | Wrong material for the fluid or lubricant |

## Related

- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
- [Dial indicator use and care](/article/dial-indicator-use)
