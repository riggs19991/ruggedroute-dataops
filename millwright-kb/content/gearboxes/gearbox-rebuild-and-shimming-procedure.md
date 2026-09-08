---
title: "Gearbox Rebuild and Shimming Procedure: Teardown Records, Bearing Replacement, Setting Bevel and Tapered Bearing Preload with Shim Packs, Backlash and Contact Pattern Checks, Seals, Reassembly and Run-In"
slug: gearbox-rebuild-and-shimming-procedure
category: gearboxes
kind: procedure
manufacturer: "Falk / Dodge / Rexnord / SEW / Nord (generic)"
model_numbers: ["Falk Enclosed Drive", "Dodge Quantis", "SEW-Eurodrive K series", "Nord Unicase", "Rexnord Planetgear"]
tags: [gearbox rebuild, gearbox overhaul, reducer rebuild, shim pack, bearing preload, tapered roller preload, bevel gear shimming, backlash adjustment, contact pattern, gear mesh pattern, gearbox seal replacement, gearbox teardown, end play gearbox, run in gearbox, gearbox inspection, bevel gearbox]
source: "Falk enclosed gear drive service manuals (bearing adjustment and shim procedure); SEW-Eurodrive K-series bevel gearbox assembly instructions; Timken tapered roller bearing setting guide (shim-set preload); AGMA 6013 (gear drive rating and inspection); Rexnord and Dodge Quantis rebuild manuals."
summary: "Step-by-step rebuild of an industrial gear reducer: recording everything before teardown, getting the bearings and gears out without damage, deciding what to replace, then the part most people get wrong: setting tapered-bearing preload and bevel-gear position with shim packs, checking backlash and the contact pattern, fitting seals and running it in."
---

## Before you open it

1. **Record**: nameplate (model, ratio, serial, mounting position), oil type and quantity, shaft direction, coupling and sheave positions (measure hub face to shaft end), and all the outside shim thicknesses under the feet.
2. **Photograph** every side, the breather location, and the oil level plug.
3. **Drain hot** if possible; keep a sample of the oil and look at the drain plug magnet. Metal on the magnet before you open the box tells you what you will find.
4. **Get the manual**: shim procedures, preload values, backlash and torque values are specific to the model. The values here are typical, not universal.

## Teardown, in an order you can reverse

1. Clean the outside. Grit in an open gearbox ruins the rebuild.
2. Remove the cover (split housing) or end caps (unicase). **Note which cap came from which bore** and keep every shim pack together with its cap, labelled. Shims are measured, not guessed.
3. Measure and record before disturbing:
   - **backlash** of each mesh with a dial indicator on a tooth (typical 0.004 to 0.012 in for medium industrial boxes, more on big low-speed sets),
   - **shaft end play** or preload of each shaft (indicator on shaft end, pry gently both ways),
   - **contact pattern** with marking compound (see below).
4. Lift shafts out as assemblies. Support gears so they do not hang on a bearing.
5. Pull bearings with a puller or press on the **inner ring only**. Cut the cage and heat the inner ring if it fights. A bearing pulled by its outer ring goes in the scrap bin.
6. Inspect gears: pitting, scuffing, spalling, tooth-root cracks, broken tips, wear steps. Inspect bores and housing seats for fretting and score marks. Check the housing joint face for nicks.

## What to replace

- **Every bearing** the shaft was on, unless the box is newly rebuilt and the failure was elsewhere. Bearings are cheap against a second teardown.
- **All seals, gaskets, and O-rings.**
- **Gears in pairs.** A new pinion against a worn gear wears the pinion in weeks.
- **Shafts** with fretted or undersized seats (measure with a micrometer against the drawing; typical interference seat is 0.0005 to 0.0015 in above nominal on a 2 in shaft).

## Assembly of shafts

1. Heat bearings on an induction heater or in oil to 80 to 110 °C and slide them on to the shoulder. Hold with pressure until they grip.
2. Press gears on to keyed or splined seats; check runout of the pitch line against a V-block or between centres (target under 0.002 in TIR for medium boxes).
3. Do not fit seals yet. They are the last thing in.

## Setting tapered roller bearing preload with shims

This is the step that decides bearing life. Tapered rollers are set by moving the cap in or out with a **shim pack** between the cap and the housing.

![Shim pack under the bearing cap sets the tapered bearing end play](/img/gearboxes/shim-pack-preload.svg)

*Shim pack under the bearing cap sets the tapered bearing end play*

1. Fit the shaft with its bearings and the cap **without shims** or with a thick trial pack.
2. Torque the cap bolts in stages.
3. Measure axial movement with an indicator on the shaft end: push and pull the shaft (rotate while pushing to seat the rollers). This is the **trial end play**.
4. Required shim pack = trial pack + trial end play − target setting.
   - Target for most industrial reducers: **0.001 to 0.003 in end play** cold (the manual may specify a light preload of 0.000 to 0.002 in on high-speed pinions).
   - The box grows when hot; a cold end play becomes a light preload at temperature.
5. Fit the calculated pack, retorque, re-measure. Rotate the shaft: it should turn freely with no lash you can feel by hand.
6. Split packs so the thick shims are in the middle and the thin ones outside: they seal better and tear less.

## Setting bevel gear position

Spiral bevel sets are positioned in two directions: the **pinion mounting distance** (how deep the pinion sits) and the **gear axial position** (which sets backlash). Both are shim adjustments and they interact.

![Reading the bevel gear contact pattern](/img/gearboxes/bevel-contact-pattern.svg)

*Reading the bevel gear contact pattern*

1. Read the **mounting distance** etched on the pinion (an MD number, for example "MD 3.125"). Set pinion shims so the measured distance from the pinion back face to the gear axis equals it. A pinion depth gauge or a machinist's height gauge from the housing face does this.
2. Move the **gear** with its shims until backlash is in range (typical 0.004 to 0.008 in for sets to 12 in diameter). Adding shims on one side means removing the same amount from the other so the preload is unchanged.
3. Paint three or four teeth on the gear with marking compound and roll the pinion through under a light hand load. Read the pattern:
   - Centred and about 60 to 80 percent of the face width: correct.
   - Toward the toe (small end) or heel (large end): move the gear.
   - Too deep (root) or too shallow (tip): move the pinion.
   - Pattern moves opposite ways on drive and coast: expected; set for the drive side.
4. Re-check preload after every move.

## Reassembly

1. New gasket or anaerobic sealant on the joint face (cured RTV squeezed into the oil is a classic filter blocker; use it thinly).
2. Torque cover bolts in a crossing pattern to the manual values.
3. Fit seals last, with a sleeve over keyways and a thin film of oil on the lip. Set new seals a little deeper or shallower than the old wear track.
4. Rotate by hand through several turns; no tight spots, no noise.
5. Fill with the specified oil to the level plug for the **mounting position**. Fit the breather.

## Run-in

- Run unloaded 15 to 30 minutes; watch temperature and listen.
- Apply load in steps to full over a shift where the process allows.
- Log bearing housing temperatures every 15 minutes for the first two hours. Steady under about 80 °C at the bearings and 90 °C oil sump is normal for a mineral-oil industrial reducer; a steady climb is not.
- Change the oil after 200 to 500 hours to flush assembly debris, then follow the normal interval.

## Common rebuild mistakes

- Shims lost or mixed between caps: preload is wrong on every shaft.
- Setting preload by feel without an indicator.
- Pinion mounting distance ignored: pattern at the toe or heel, gear noise, and a new set gone in months.
- Seal lip pushed over a sharp keyway: leaks on the first day.
- Breather left off or blocked: pressure pushes oil past the seals.

## Related

- [Tapered Roller Bearing Setting](/article/tapered-roller-bearing-setting)
- [Gear Inspection and Tooth Failure (AGMA 1010)](/article/gear-inspection-and-tooth-failure)
- [Gearbox Lubrication, Oil Levels, Breathers and Routine Inspection](/article/gearbox-lubrication-and-inspection)
- [Mounting Bearings with Heat](/article/bearing-mounting-with-heat)
