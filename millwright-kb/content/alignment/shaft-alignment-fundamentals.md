---
title: "Shaft-to-Shaft Alignment Fundamentals: Offset, Angularity, Pre-Checks and Tolerances"
slug: shaft-alignment-fundamentals
category: alignment
kind: reference
tags: [shaft alignment, coupling alignment, offset, angularity, misalignment, tolerances, pre-alignment, rough alignment, straightedge, shim, MTBM, stationary machine, pump motor alignment]
source: "General industry practice; tolerance table per Ludeca / Pruftechnik general alignment tolerances (widely reproduced); ANSI/ASA S2.75-2017 for context."
summary: "What misalignment is, how it is described (vertical and horizontal offset and angularity), the pre-alignment checklist every job starts with, and the standard RPM-based tolerance table used to decide when a shaft-to-shaft alignment is good enough."
---

## Why we align

A flexible coupling tolerates *some* misalignment. It does not remove the forces. Misaligned shafts push a bending load into the bearings and seals once per revolution. Typical results of poor alignment: hot bearings, seal leaks, coupling wear and rubber dust, foundation bolt loosening, and vibration at 1× and 2× running speed. Good alignment is the cheapest reliability improvement a millwright can make.

## Describing misalignment

Two shafts can be out in four independent ways. You correct all four.

![Parallel offset and angular misalignment in two planes](/img/alignment/offset-and-angularity.svg)

*Parallel offset and angular misalignment in two planes*

| Term | What it means | Corrected by |
|---|---|---|
| **Vertical offset** | Movable shaft centreline is parallel but higher/lower than the stationary | Shims under all four feet equally |
| **Vertical angularity** | Movable shaft tilts up or down relative to the stationary (feet at different heights) | Different shim thickness front vs rear feet |
| **Horizontal offset** | Movable shaft is parallel but shifted sideways | Jacking bolts, move all four feet equally |
| **Horizontal angularity** | Movable shaft is skewed sideways | Move front and rear feet different amounts |

Offset is stated in **mils** (0.001") or mm **at the coupling centre**. Angularity is stated as a **slope**, mils per inch (or mm per 100 mm), which is the same as the coupling face gap difference divided by the face diameter.

## Words

- **Stationary machine (S)**: the one you do not move. Usually the pump, gearbox, fan or compressor, because piping and ducting anchor it.
- **Movable machine (MTBM, M)**: usually the motor.
- **Inboard feet**: the feet nearest the coupling. **Outboard feet**: farthest from the coupling.
- **TIR**: total indicator reading, the full swing of a dial indicator.
- **Bar sag**: the droop of the indicator bracket under its own weight; it corrupts rim readings and must be measured and corrected.

## Pre-alignment checklist (do these before touching an indicator)

1. **Lockout/tagout** both machines. Verify zero energy. Try-start.
2. Read the coupling and equipment manual for the required gap and the alignment tolerance, if one is given. Equipment specs override the general table below.
3. Inspect the coupling: worn elements, loose hubs, keys. Replace before aligning.
4. Check foundation and baseplate: cracked grout, loose anchor bolts, corroded hold-down bolts. Fix first.
5. Clean under every foot. Rust scale under a foot is a shim you did not choose.
6. **Check for pipe strain**: with the pump bolted down and the coupling disconnected, loosen the pump feet and see if the pump moves. Any movement over 0.002" means piping is pulling the pump. Fix the piping.
7. **Check runout** of both shafts and hub rims/faces with an indicator (target under 0.002" TIR). A bent shaft or eccentric hub cannot be aligned out.
8. **Rough align** with a straightedge across the rims and a taper gauge or feelers in the face gap. Get within about 0.020" so the fine method has room to work.
9. **Correct soft foot** (see the [soft foot article](/article/soft-foot-correction)). Nothing else is valid until soft foot is under 0.002".
10. Set the **coupling gap** to the manufacturer's spec (see [couplings](/article/coupling-types-gap-and-installation)).
11. Have the right shims: pre-cut stainless shims, all sizes, clean and flat. Never more than 4 or 5 shims under a foot; use one thick shim instead of a stack of thin ones.

## Order of correction

1. Soft foot
2. Vertical angularity, then vertical offset (shims)
3. Horizontal angularity, then horizontal offset (jack bolts)
4. Re-check vertical after horizontal moves; torque bolts to spec and re-check
5. Record final readings

Vertical always comes first because shim changes disturb horizontal readings, but horizontal moves rarely disturb vertical.

## General alignment tolerances

Use these when the equipment manual gives none. Values are for short flexible couplings with the coupling as the measurement plane. "Excellent" is the target for new installations and critical machines; "Acceptable" is the outer limit for continued running.

![Offset tolerance falls as speed rises](/img/alignment/alignment-tolerances.svg)

*Offset tolerance falls as speed rises*

| Speed (rpm) | Offset - Excellent (mils) | Offset - Acceptable (mils) | Angularity - Excellent (mils/in) | Angularity - Acceptable (mils/in) |
|---|---|---|---|---|
| 600 | 5.0 | 9.0 | 1.0 | 1.5 |
| 900 | 3.0 | 6.0 | 0.7 | 1.0 |
| 1 200 | 2.5 | 4.0 | 0.5 | 0.8 |
| 1 800 | 2.0 | 3.0 | 0.3 | 0.5 |
| 3 600 | 1.0 | 1.5 | 0.2 | 0.3 |
| 7 200 | 0.5 | 1.0 | 0.1 | 0.2 |

Metric conversion: 1 mil = 0.0254 mm; 1 mil/in = 0.1 mm per 100 mm.

For **spacer (jackshaft) couplings** the angularity limit applies to each flex plane and the offset limit is effectively the angularity times the spacer length; laser systems handle this automatically.

## Which method?

| Method | Accuracy | Needs | Best for |
|---|---|---|---|
| Straightedge and feeler | ±0.010-0.020" | 5 minutes, a straightedge | Rough alignment, low-speed belt/fan drives |
| [Rim and face (dial)](/article/rim-and-face-alignment) | ±0.001-0.002" | one bracket, two indicators, can be done with one shaft turning | Short couplings, when the shafts cannot both be rotated, large-diameter hubs |
| [Reverse dial](/article/reverse-dial-alignment) | ±0.001" | two brackets, two indicators, both shafts rotate together | Most pump/motor sets; unaffected by face runout or axial float |
| [Laser](/article/laser-alignment-procedure) | ±0.0005" or better | laser kit | Everything; fastest; handles thermal growth and spacer couplings |

Whatever the method, the readings are only as good as the pre-checks.

## Related

- [Soft foot correction](/article/soft-foot-correction)
- [Thermal growth and cold-alignment targets](/article/thermal-growth-alignment)
- [Dial indicator use and care](/article/dial-indicator-use)
