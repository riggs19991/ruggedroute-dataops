---
title: "Tapered Roller Bearing Setting: End Play vs Preload, Timken Setting Methods Compared (Manual, Preset, Set-Right, Acro-Set, Projecta-Set, Torque-Set, Clamp-Set), Manual Setting with a Dial Indicator, Shim and Spacer Adjustment, Nut-Adjusted Wheel Hubs, Typical Ranges and Hot Running Changes"
slug: tapered-roller-bearing-setting
category: bearings
kind: procedure
manufacturer: Timken
model_numbers: ["Set-Right", "Acro-Set", "Projecta-Set", "Torque-Set", "Clamp-Set", "TDO", "TDI", "2TS-IM"]
tags: [tapered roller bearing, tapered roller bearing setting, end play, endplay, preload, bearing setting, Timken setting, Set-Right, Torque-Set, dial indicator end play, shim adjustment, spacer adjustment, adjusting nut, wheel bearing adjustment, gearbox end play, bench end play, mounted setting, cup and cone, direct mounting, indirect mounting, hot end play, rolling torque]
source: "Timken 'Setting Techniques for Tapered Roller Bearings' (form 5556): definitions, Table 1 comparison of methods and typical mounted setting ranges (manual 0.004-0.010 in etc.), manual setting description (adjusting nut backed off 1/6 to 1/4 turn), preset assemblies and bench end play; Timken Engineering Manual guidance on end play vs life; gearbox and axle manufacturer service manuals."
summary: "A tapered roller bearing does not have a built-in clearance: you set it when you assemble the machine. This covers what end play and preload are and which one the machine wants, Timken's table of setting methods with the ranges each achieves, the manual method with a dial indicator that a millwright uses on gearboxes, pumps and rolls, shim, spacer and nut adjustment, why the hot setting differs from the cold, and the checks after assembly."
---

## What "setting" means

A tapered roller bearing is two separable parts: the **cone** (inner ring with rollers and cage) and the **cup** (outer ring). Mounted in **pairs** facing each other (direct or indirect mounting), the axial position of one cup or cone relative to the other decides the internal clearance of both bearings at once:

- **End play**: an axial clearance; the shaft can be moved end to end a measurable amount. Rollers are not all loaded; the bearing runs cool and tolerates thermal expansion.
- **Preload**: an axial interference; the rollers are all loaded and the shaft has zero end play plus a set force. Stiffer, more accurate, higher load capacity from more rollers sharing, but heat and life fall sharply if the preload is too high.
- **Zero (line-to-line)**: the transition. Timken's life curve peaks at **near-zero to slight preload**; because you cannot hit zero exactly and because hot running changes the setting, most industrial machinery is set with **a small end play cold** that closes toward zero when hot.

Which the machine wants: **the manual decides**. Typical: gearbox shafts, conveyor pulleys, pumps, rolls: **end play 0.001-0.005"** (larger shafts 0.005-0.010"); pinions and spiral bevel gear sets, machine-tool spindles, wheel hubs with unitised seals: **preload**, specified as rolling torque (in-lb) or as a nut torque; truck wheel ends: end play 0.001-0.005" set by the nut method.

## Timken's setting methods (Table 1 of form 5556)

| Method | How the setting is obtained | Typical mounted setting range achieved | Region |
|---|---|---|---|
| **Manual** | Adjust a nut, shims or a spacer with a dial indicator or by feel | **0.004-0.010"** (wide; skill-dependent) | End play |
| Preset assembly (2TS-IM etc.) | Matched cones/cups with a factory spacer giving a bench end play (BEP) | 0.006-0.012" | End play or preload |
| **Set-Right** | Controlled tolerances on the shaft, housing and bearing; no adjustment at assembly; statistics keep it in range | 0.008-0.014" (probable) | End play or preload |
| Acro-Set | Measures deflection under a known load to compute the spacer/shim | 0.004-0.006" | End play or preload |
| Projecta-Set | Gauges the projected position of the cone under load to size the spacer | 0.002-0.004" | End play or preload |
| **Torque-Set** | Adjusting nut tightened to a specified torque (which seats and preloads), then backed off a set amount or left | 0.005-0.007" | End play or preload |
| Clamp-Set | Clamping force through a spacer with a deflection-controlled fastener | 0.003-0.005" | End play |

In the field you do the **manual** method most of the time and the **torque** method on wheel ends and where a manual says "tighten to X ft-lb, back off Y".

## Manual setting with a dial indicator (gearbox, pulley, pump)

1. Assembly clean, cones pressed or heated on to their seats against the shoulders (see [mounting with heat](/article/bearing-mounting-with-heat)), cups seated fully in the housing (a dull sound when tapped, or measured). **Cups and cones must be fully seated before any setting**: a cup 0.005" out of its bore reads as 0.005" of end play that disappears when it seats in service.
2. Assemble with the adjusting element (shims under the end cap, a threaded nut or cup carrier, a spacer) set for an obvious clearance.
3. **Rotate the shaft several turns while pushing it toward one end** to seat the rollers against the cup ribs (rollers that are not seated give a false large end play); then rotate while pulling to the other end.
4. Dial indicator on the shaft end (a magnetic base on the housing, plunger on the shaft's end face, parallel to the axis). Push the shaft firmly one way while rotating slightly, zero the indicator; pull it the other way while rotating; the reading is the **end play**. Repeat three times; readings must agree within 0.001".
5. Adjust: remove or add shims (shim change = end play change, one to one, for a shim under the cup carrier or end cap), turn the nut, or change the spacer; re-seat the rollers (step 3) after every change; re-measure.
6. Target the cold end play the manual gives; when it gives none, use 0.001-0.003" for shafts under 2", 0.003-0.005" to 4", 0.005-0.008" above (rules of thumb; the correct number depends on the housing material, shaft length between bearings and running temperature: see below).
7. Lock: bend the lock washer tab, stake or wire the nut, torque the end-cap bolts to spec, re-measure the end play **after** torquing (it changes), and record it.
8. Rotate by hand: smooth, no rough spots, no drag beyond seal drag. Spin check: a shaft with end play spins on; with preload it stops within a turn.

## Preload settings

- **Rolling torque method**: with the seals out (or their drag measured first), turn the shaft with a torque wrench or a spring scale on a string around a known radius; the manual gives the range (e.g. a differential pinion: 15-25 in-lb new bearings, 5-10 in-lb used). Tighten the nut or remove shims until the rolling torque is in range. Torque = force × radius.
- **Torque-Set (nut method)**: tighten the adjusting nut to the specified torque while rotating (seats everything and preloads), then **back off** the specified amount (a fraction of a turn to a locking position, or to a measured end play) and lock. The Timken truck wheel-end example: tighten to a slight bind while rotating, back off 1/6 to 1/4 turn to the nearest lock, giving a small end play.
- **Shim/spacer preload**: measure the gap with the bearings seated line-to-line under a light load (feeler gauge or depth micrometer), and fit a spacer shorter than the gap by the preload amount the manual gives (typically 0.001-0.003").
- Preload is very sensitive to fits: a cone pressed onto a shaft 0.001" tighter than designed loses 0.0005-0.001" of internal clearance. That is what Set-Right controls with tolerances.

## Hot running: why cold end play is not the running end play

The shaft grows longer than the housing when it runs warmer (gearbox shafts run 20-50°F hotter than the case; a steel shaft in an aluminium housing is the reverse: the housing grows more). Between two bearings L apart:

```
   change in end play ≈ L × (α_shaft × ΔT_shaft − α_housing × ΔT_housing)      α_steel = 6.5 × 10⁻⁶ /°F, α_aluminium = 12.5 × 10⁻⁶ /°F
```

Example: steel shaft, steel housing, bearings 20" apart, shaft 40°F hotter than the housing: 20 × 6.5 × 10⁻⁶ × 40 = **0.0052" reduction** in end play. If you set 0.003" cold, it runs 0.002" preloaded: fine for a gearbox, but a longer shaft or a bigger ΔT can turn a "safe" cold end play into heavy preload and a hot bearing. Indirect (X) mounting and direct (O) mounting respond in opposite directions to radial expansion; the manual's cold number already accounts for it. Do not "improve" the manual's number.

## Cups, cones and fits

- Rotating cone (most shafts): **tight** on the shaft (interference fit per the fit tables); cup stationary in a housing: slip fit for the adjustable cup, tight where it is the fixed one. The **adjustable member must be the loose-fitted one** or you cannot adjust it (Timken's "loose fitted member for adjustment").
- Seat the cup: press or drive with a driver on the cup's face, never on the rib; a cup carrier lets you shim behind it.
- Cone back face against the shoulder: check with a feeler; a gap here is end play you will lose in service.
- Matching: cups and cones are interchangeable within a part number (not with other numbers); a 2TS-IM preset pair with its spacer is a matched set.

## Checks after setting

- End play measured after the end cap is torqued, and again after the first heat run when possible (shut down, measure hot).
- Temperature at the bearing housing after 1-2 hours: stabilised below about 180°F; a rising temperature on a freshly set taper bearing = preload from thermal growth or a mis-seated cup.
- Rolling smoothness, no axial knock; on gearboxes the tooth contact pattern (see [gear inspection](/article/gear-inspection-and-tooth-failure)) confirms the pinion setting.
- Record end play, shim thickness, nut position, rolling torque and the date.

## Common mistakes

- Measuring end play without seating the rollers by rotating under load: the "0.008" you measured is really 0.003.
- Cup not fully seated in the bore: the setting vanishes on the first run.
- Setting a long steel shaft in a steel housing to zero cold: it preloads hot and burns.
- Torquing the adjusting nut to the bearing's ruin because the manual said "tight".
- Mixing a used cone with a new cup, or a cone and cup from different part numbers.
- Adjusting the tight-fitted member (it will not move without a puller, and the shoulder gets damaged).
- Forgetting the seal drag when measuring rolling torque for a preload.

## Related

- [Bearing mounting with heat](/article/bearing-mounting-with-heat)
- [Bearing removal, pullers and heating](/article/bearing-removal-pullers-and-heating)
- [Bearing clearance and fits tables](/article/bearing-clearance-and-fits-tables)
- [Dial indicator use](/article/dial-indicator-use)
- [Gear inspection and tooth failure](/article/gear-inspection-and-tooth-failure)
