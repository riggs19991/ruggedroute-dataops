---
title: "Shaft Couplings: Types, Setting the Gap, and Hub Installation"
slug: coupling-types-gap-and-installation
category: power-transmission
kind: reference
manufacturer: "Lovejoy / Falk / Rexnord / Dodge / TB Wood's (generic)"
model_numbers: ["L-Jaw", "Steelflex", "Omega", "Thomas disc", "Sure-Flex", "Para-Flex", "Grid 1020T", "Gear F", "Chain 4012"]
tags: [coupling, jaw coupling, grid coupling, gear coupling, disc coupling, tire coupling, chain coupling, coupling gap, hub installation, spider, spacer coupling]
source: "Manufacturer installation sheets; general practice."
summary: "The main coupling families millwrights meet, what each tolerates, how to set the gap between hubs, and how to install hubs without hammering them onto the shaft."
---

## Families

![Coupling gap and the four common families](/img/power-transmission/coupling-gap-and-types.svg)

*Coupling gap and the four common families*

| Type | Example | Misalignment tolerance | Lubrication | Notes |
|---|---|---|---|---|
| **Jaw (elastomer spider)** | Lovejoy L/AL, Martin ML | Low: about 0.015" offset, 1° angular | None | Cheap, fail-safe (runs jaw-on-jaw if spider dies). Spider hardness (SOX rubber, Hytrel, urethane) sets torque and stiffness. |
| **Tire (elastomer)** | Dodge Para-Flex, Fenner Tyre | High: 1/8" offset, 4° angular | None | Split tire replaced without moving hubs. Absorbs shock and vibration. |
| **Sleeve (elastomer)** | TB Wood's Sure-Flex, Rexnord Omega | Medium | None | Rubber/EPDM/Hytrel sleeve. |
| **Grid (steel spring)** | Falk Steelflex T10/T20, Dodge D-Flex | Medium: ~0.012-0.030" offset, 1/4-1/3° angular | **Grease** | Serpentine spring in hub slots; cover holds grease. Gap set by a table per size. |
| **Gear** | Falk G, Kop-Flex, Sier-Bath | Low angular per mesh (1/4-1½°) but handles high torque | **Grease** or oil | Needs alignment; lubrication failure is the #1 killer. Spacer versions common on pumps. |
| **Disc (metallic flex)** | Thomas, Rexnord Thomas XTSR, Lovejoy DI | Medium, precise, zero backlash | None | Stainless disc packs; **must** be aligned to tight tolerances; spacer type lets you pull the pump without moving the motor. |
| **Chain** | Dodge/Rexnord 4012-6022 | Medium | Grease, with cover | Two sprockets and a double chain. Cheap for slow shafts. |
| **Rigid** | Sleeve or flanged rigid | None | None | Only for shafts that are truly in line (vertical pumps, line shafts). |

A flexible coupling is there to accept **residual** misalignment, thermal growth and small end float; it is not an excuse to skip alignment.

## Setting the gap

The gap is the distance between the two hub faces (or the spider/element length for jaw types). It matters because it controls how much axial float the coupling has and whether the element is compressed or stretched.

1. Get the number from the **manufacturer's sheet for the size**, not from memory. Example order of magnitude: Falk 1050T grid ≈ 1/8"; a Lovejoy L-100 spider needs the hubs spaced so the spider is not crushed (nominal gap on the sheet).
2. Slide hubs on to give the gap; use a **gap gauge** or feeler stack, measured at four points around the hubs to check angularity as well.
3. For spacer couplings, the **DBSE** (distance between shaft ends) is fixed by the spacer length; set the shafts to that first.
4. Motors with sleeve bearings need the coupling gap set at the **magnetic centre** (mark on the motor shaft); otherwise the rotor hunts axially.

## Hub installation

- **Clearance fit with key and set screw** (small jaw/sleeve types): slide on, key seated, set screw on the key, Loctite. Set screw torque per sheet.
- **Interference fit** (most grid, gear, disc, large jaw): **heat the hub** to about 150-200°C (300-400°F) in an oven or with an induction heater, slide on quickly to the shaft mark, hold. **Never hammer a hub on**; you drive the shaft into the bearings and brinell them. Never heat with a torch on a hub with an elastomer element installed.
- Pulling hubs off: use a puller on the hub, never on the coupling element or the shaft end; heat if the fit is heavy.
- Keys: full-length, fitted, with the correct clearance on top. A loose key wallows the keyway.

## Element installation notes

- **Jaw spider**: choose by torque and temperature; the hardness is marked. Check that the spider legs are not cracked.
- **Grid**: pack the hub teeth with the specified coupling grease, seat the grid with a soft hammer **starting at the cover seal side and working around**, cover seals flat, bolts torqued, grease fitting used.
- **Gear**: fill the specified grease quantity (coupling grease, not bearing grease, because ordinary grease separates under centrifugal force).
- **Disc**: bolt torque and disc pack orientation matter; follow the sheet. Do not bend the discs during installation.

## Inspection during PM

- Rubber dust under a jaw/tire coupling = misalignment or a failing element.
- Grease on the guard = grid/gear cover seal leaking; re-lubricate and align.
- Backlash you can feel by hand on a gear coupling = worn teeth.
- Cracked disc packs = misalignment; align and replace.

## Related

- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
- [V-belt drives](/article/v-belt-drive-installation-and-tensioning)
