---
title: "Leveling and Machine Setting: Installation Sequence from Crate to Coupling, Precision Levels (Sensitivity, Reversal Check, How to Read Them), Leveling a Baseplate on Jack Screws and Shims to API 686 Tolerances, Pad Flatness and Coplanarity, Sole Plates and Chocks, Setting the Machines, Doweling"
slug: leveling-and-machine-setting
category: installation
kind: procedure
manufacturer: "Starrett (levels), generic machinery"
model_numbers: ["Starrett 98", "Starrett 199", "Starrett 199Z", "Mitutoyo 960", "Wyler", "Federal precision level"]
tags: [leveling a machine, machine installation, machine setting, precision level, machinist level, Starrett 98, Starrett 199, master precision level, level sensitivity, reversal check, jack screws, leveling baseplate, API 686 level tolerance, 0.0002 in/ft, pad flatness, coplanar pads, sole plate, chock, epoxy chock, dowel pins, taper pin, doweling a pump, installation sequence, commissioning sequence]
source: "API RP 686 Recommended Practice for Machinery Installation and Installation Design (installation sequence, baseplate leveling and flatness, shim limits, doweling); Starrett 98 and 199 level specifications (0.005 in/ft per division; 0.0005 in/ft per division, 10 arc-seconds); Piotrowski, Shaft Alignment Handbook; manufacturer installation manuals (Goulds, Baldor)."
summary: "The order of operations for installing a machine on a foundation and why each step comes where it does, how to use a precision level correctly with the reversal check and the conversion from divisions to inches, how to level a baseplate on jack screws to the API 686 numbers before grouting, how to check the mounting pads for flatness and coplanarity, the sole-plate and chock alternatives, setting the driver and driven machines on the base, and doweling after the final hot alignment."
---

## The sequence

| Step | What | Why in this order |
|---|---|---|
| 1 | Receiving inspection: damage, rotation by hand, shaft runout, nameplate vs order, preservation | Claims before it is installed |
| 2 | Foundation check: elevation, position vs column lines, anchor bolts vs baseplate, cure | See [anchor bolts](/article/anchor-bolts-and-foundations) |
| 3 | Set the baseplate on jack screws/shims, **level it**, check pad flatness | Level before grout; grout locks it |
| 4 | **Grout**, cure, back off jack screws, torque anchors, re-check level | See [grouting](/article/grouting-baseplates) |
| 5 | Set the driven machine (pump) first with a **1/8" shim pack** under the driver; rough align | The pump is fixed by its piping; the motor moves |
| 6 | Correct **soft foot** on both machines | Before any alignment reading |
| 7 | **Rough alignment** (within 0.020") | Before piping, so pipe is fitted to a machine in its final place |
| 8 | Connect piping; **pipe strain check** | Piping must not move the pump |
| 9 | **Final cold alignment** with thermal growth targets | See the alignment articles |
| 10 | Rotation check (uncoupled), lube, guards, coupling | |
| 11 | Run-in, **hot alignment check**, then **dowel** | Dowels lock the final position |
| 12 | Baseline data (vibration, temperatures, alignment record) | For the PM program |

Break the order (piping before alignment, dowels before the hot check, grout before level) and every later step fights the earlier one.

## Precision levels

| Level | Sensitivity per division | Arc | Use |
|---|---|---|---|
| Carpenter's / torpedo level | about 0.03-0.05"/ft | 10-15 min | Rough placement only |
| **Machinist's level (Starrett 98)** | **0.005"/ft (0.42 mm/m)** | 80-90 s | General machinery, conveyors, gearboxes |
| **Master precision level (Starrett 199, Mitutoyo 960)** | **0.0005"/ft (0.04 mm/m)** | 10 s | Baseplates for API pumps, compressors, machine tools |
| Electronic level (Wyler, Federal) | 0.0001-0.0002"/ft | 1-2 s | Precision beds, long-span comparisons |

Reading: the bubble moves **toward the high end**. One division on a 199 = 0.0005" per foot of level length; across a 4 ft baseplate one division means the far end is 4 × 0.0005 = **0.002" high**. Sensitive levels take 20-30 seconds to settle; shield from drafts and sun, and do not hold the vial end with a warm hand (the bubble runs from the heat).

**Reversal (calibration) check**, every time before trusting a reading: set the level on the surface, note the bubble position; **rotate it 180°** on the same spot; note again. If both readings are the same, the level is true and the surface is at that reading. If they differ, the surface's true slope is the **average** and the difference ÷ 2 is the level's error: adjust the vial (the adjusting screw on a 98/199) until both readings match, or apply the correction.

Place the level on **machined surfaces only** (pads, a shaft, a ground parallel), cleaned, never on paint or a rough deck; use a ground parallel or a straightedge to bridge between pads; check each pad **in two directions** at 90°.

## Leveling a baseplate (before grout)

Tolerances (API 686 practice; use the drawing or the plant spec if it says otherwise):

![Precision level on the machined pads, jack bolts at each anchor](/img/installation/leveling-with-jack-bolts.svg)

*Precision level on the machined pads, jack bolts at each anchor*

| Item | Target |
|---|---|
| Level, longitudinal and transverse | **0.0002"/ft (0.017 mm/m)** for API-class pumps and compressors is the commonly applied API 686 target; **0.001-0.002"/ft** is typical for general industrial machinery (fans, gearboxes, conveyors drives) |
| Mounting pads flat | 0.002" over the pad (feeler gauge under a straightedge) |
| Pads of one machine **coplanar** (in one plane) | within **0.002"** of each other |
| Driver pads relative to driven pads | Driver pads at least the shim pack height (**1/8"**) **below** the line of the driven pads, and parallel to them |
| Elevation vs drawing | ± 1/8" (3 mm) |

Procedure:

1. Anchor bolts hanging loose in the sleeves; baseplate on its **jack screws** (API 686: one at each anchor bolt, minimum four, on steel pads) or on shim packs at the anchors, about 1-2" above the concrete.
2. Level with the **master level on the pump pads** (the machined surfaces) longitudinally, then transversely, adjusting the jack screws **in pairs** so you do not twist the plate; then the driver pads; then diagonally to check twist. Small turns: a 1/2-13 jack screw moves the plate **0.077" per turn**, so a sixth of a turn is 0.013".
3. Check pad flatness and coplanarity with a straightedge and feelers across all the pads; a plate that cannot be levelled without twisting has a warped deck: shim under the pads later, or send it back.
4. Bring the anchor bolt nuts to **finger tight plus a snug** (not torqued); recheck the level; a change means the plate is being pulled by a bolt that is not plumb or a sleeve full of concrete.
5. Record the readings; wax the jack screws; grout.
6. After the grout cures: back the jack screws off, torque the anchors in steps, **re-level**; the plate can move 0.002-0.005". If it is now outside tolerance, that is what shims under the machine feet are for; if it is way out, the grout was poured wrong.

## Sole plates and chocks

Big machines (large motors, compressors, mills) are not set on a one-piece baseplate but on **sole plates**: individual machined steel plates grouted to the foundation under each foot, levelled to each other with a precision level and a **transit or laser** across them, and doweled later. Alternatively **epoxy chocks** (Chockfast Orange poured in a dam under each foot, 1/2-2" thick) replace machined shims and sole plates: the chock takes the exact shape of the foot and the foundation, with no fitting, and is the marine and heavy-industry standard. Adjustable **steel chocks** (Vibracon, screw-adjusted wedges) allow re-levelling without re-grouting.

## Setting the machines

![Shim stacking rules under machine feet](/img/layout-templates/shim-stacking.svg)

*Shim stacking rules under machine feet*

1. Pump (the driven, fixed machine) goes on first, on its pads, **no shims or a thin equal pack** (the pump is the reference; the piping decides where it sits); feet bolted, soft foot checked and corrected (see [soft foot](/article/soft-foot-correction)).
2. Motor/driver on **shim packs of at least 1/8"** at every foot (API 686), the same thickness at each foot, so it can be lowered later; **maximum 5 shims per foot**, thick on the bottom; no more than 1/2" total stack, else machine a spacer.
3. Rough align: straightedge across the coupling rims and feeler at the faces to within about 0.020"; centre the motor in its bolt holes so you have movement both ways (bolt-bound is a day lost); lock the motor with the jack bolts on the base (API 686 wants horizontal jack bolts at the driver feet).
4. Connect piping to the pump (see [pipe strain](/article/pipe-strain-and-flange-alignment)); check the pump did not move.
5. Final alignment: [rim-and-face](/article/rim-and-face-alignment), [reverse dial](/article/reverse-dial-alignment) or [laser](/article/laser-alignment-procedure) with [thermal growth](/article/thermal-growth-alignment) targets; torque the hold-down bolts to spec in the sequence and re-check.
6. Guards, coupling per the coupling's own manual, lube.

## Doweling

After the machine has run at operating temperature and the **hot alignment** has been checked and accepted, dowels lock the position so it can be removed and replaced without re-aligning:

- **Two dowels per machine**, on **diagonally opposite feet** (some plants: the two outboard feet of the pump, and none on the motor if it must move for alignment); through the foot into the baseplate pad (not into grout).
- **Taper pins** (1:48 taper, ANSI B18.8.2): drill with the taper pin drill size, ream with the matching taper reamer until the pin's small end stands a set height above the foot, tap it home (large end up so it can be driven out from below or pulled with a slide hammer); or straight dowels with a reamed hole and a threaded end for extraction.
- Dowel diameter ≈ **1/2 to 2/3 of the hold-down bolt** size; length through the foot and 1-1.5 × diameter into the base.
- Never dowel a machine with large thermal growth on both feet ends (it cannot grow): dowel the fixed end only or use the maker's guidance.
- Mark the dowel positions on the alignment record; re-ream if the machine is ever re-aligned.

## Common mistakes

- Levelling on the painted deck of the baseplate instead of the machined pads.
- Trusting a level that has not been reversed: the baseplate is out by twice the vial error.
- Grouting a baseplate that is level but twisted: the pads are not coplanar and the motor has a permanent soft foot.
- No 1/8" shim pack under the motor: the pump wears in, the motor has to come down 0.005", and there is nowhere to go.
- Piping connected before alignment: the pump is aligned to a position the piping will not let it keep.
- Doweling before the hot check.
- Torquing anchor bolts on green grout, or torquing them with the jack screws still holding the plate.

## Related

- [Anchor bolts and foundations](/article/anchor-bolts-and-foundations)
- [Grouting baseplates](/article/grouting-baseplates)
- [Soft foot correction](/article/soft-foot-correction)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
- [Pipe strain and flange alignment](/article/pipe-strain-and-flange-alignment)
- [Optical and laser levels and piano wire](/article/optical-and-laser-levels-piano-wire)
- [Shim and gasket making (shim rules)](/article/shim-and-gasket-making)
