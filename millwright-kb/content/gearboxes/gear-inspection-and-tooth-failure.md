---
title: "Gear Inspection and Tooth Failure (AGMA 1010): Gear Types and Terms, Ratio and Speed Math, Checking Contact Pattern with Bluing, Measuring Backlash (Indicator, Feeler, Solder Wire) with Typical Values by Pitch, Bevel Gear Pattern Adjustment, Tooth Failure Modes (Wear, Scuffing, Micropitting, Pitting, Spalling, Bending Fatigue, Overload) and Their Causes"
slug: gear-inspection-and-tooth-failure
category: gearboxes
kind: reference
tags: [gear inspection, gear teeth, gear failure, tooth failure, AGMA 1010, pitting, macropitting, micropitting, spalling, scuffing, scoring, gear wear, tooth breakage, bending fatigue, contact pattern, bluing gears, backlash, measuring backlash, backlash by pitch, diametral pitch, module, pressure angle, gear ratio, bevel gear pattern, toe heel, spiral bevel adjustment, worm gear pattern, gear terms, pitch diameter, borescope gearbox]
source: "ANSI/AGMA 1010-F14 Appearance of Gear Teeth, Terminology of Wear and Failure; AGMA 2002 (backlash) and typical backlash-by-pitch practice; Rexnord Falk gear failure guide; Boston Gear gear theory and inspection guidance; Gleason bevel gear contact-pattern development guidance; Philadelphia Gear / Errichello (GEARTECH) failure analysis papers."
summary: "What a millwright checks inside a gearbox and on open gearing: the gear types and the words on the drawing, the ratio and speed calculations, how to blue the teeth and read the contact pattern and move it, how to measure backlash three ways and what number to expect, how to adjust a bevel set, and the AGMA 1010 catalogue of tooth damage with what each one looks like and what caused it."
---

## Gear types

| Type | Teeth | Notes for the millwright |
|---|---|---|
| **Spur** | Straight, parallel to the axis | No thrust; noisy at speed; the simplest |
| **Helical** | Angled | Smooth and quiet, carries more; **produces axial thrust** (a thrust bearing is required; the bearing arrangement matters on rebuild); single helical parallel-shaft reducers are the commonest industrial gearbox |
| Double helical / herringbone | Two opposed helixes | Thrust cancels; one shaft must float axially to let the teeth centre |
| **Bevel** (straight, spiral, Zerol) | On cones; shafts at 90° | **Mounting distance** sets the contact pattern; spiral bevels have thrust in both directions depending on rotation and hand |
| Hypoid | Offset bevel | Sliding action: needs EP oil (automotive rear axles, some industrial) |
| **Worm and wheel** | Screw driving a bronze wheel | High ratio in one stage, sliding contact (efficiency 50-90%), heat, **bronze wheel is the wear part**, may be self-locking; see [worm and planetary reducers](/article/planetary-and-worm-reducers) |
| Planetary (epicyclic) | Sun, planets, ring | Compact, high torque, coaxial |
| Rack and pinion | Linear | Backlash set by the mesh distance |

## Terms

- **Pitch circle / pitch diameter (PD)**: the imaginary rolling circle; gears mesh at their pitch circles. Centre distance = (PD₁ + PD₂) ÷ 2.
- **Diametral pitch (DP, inch)**: teeth per inch of pitch diameter (PD = N ÷ DP); **module (m, metric)**: mm of pitch diameter per tooth (PD = m × N); m = 25.4 ÷ DP. Two gears mesh only if they have the same DP or module **and** pressure angle.
- **Pressure angle**: 20° standard (14.5° on old gears): the angle of the tooth force; marked on the drawing.
- **Addendum** = 1/DP (tooth height above the pitch circle), **dedendum** = 1.25/DP; **outside diameter** = (N + 2) ÷ DP; whole depth = 2.25/DP (2.157/DP old standard). A gear's DP can be found from its OD and tooth count: DP = (N + 2) ÷ OD.
- **Backlash**: the play between meshing teeth measured at the pitch circle, needed for lubrication and expansion.
- **Face width**, **helix angle**, **hand** (right/left, for helical and spiral bevel), **AGMA quality number** (Q5-Q15: accuracy).

## Ratio and speed

```
   ratio i = N_driven ÷ N_driver = PD_driven ÷ PD_driver          output rpm = input rpm ÷ i
   multi-stage: total ratio = i₁ × i₂ × i₃
   output torque = input torque × i × efficiency (spur/helical stage ≈ 0.97-0.98; worm 0.5-0.9; bevel 0.97)
   pitch line velocity (ft/min) = π × PD (in) × rpm ÷ 12       (decides the oil: see [oil viscosity](/article/oil-viscosity-and-selection))
   gear mesh frequency (Hz) = teeth × rpm ÷ 60                  (the line to watch in a vibration spectrum)
   hunting tooth: ratio chosen so every tooth meets every other (N₁ and N₂ have no common factor); a 2:1 with 20/40 teeth wears in pairs
```

Example: a 3-stage helical reducer with 22/61, 19/58, 17/63: i = 2.773 × 3.053 × 3.706 = **31.4:1**; 1750 rpm in → 55.8 rpm out; 50 hp input torque 1,800 in-lb → output 1,800 × 31.4 × 0.94 = 53,100 in-lb.

## Inspection routine

1. **Listen and feel** before opening: whine (mesh frequency, normal), growl or knock (bearing, backlash, broken tooth), a periodic thump once per revolution of a shaft (one bad tooth); housing temperature (under 180-200°F for mineral oil).
2. **Oil**: level, colour, smell (burnt = overheated), water (milky), metal (magnetic plug: fine grey paste is normal wear, flakes and chips are pitting or breakage), oil analysis for a trend (see [oil analysis](/article/oil-analysis-and-sampling)).
3. **Open the inspection cover** (clean around it first); light and a mirror or a **borescope**; rotate the gears slowly through a full turn of the slowest gear.
4. Look at the **tooth contact pattern** (the polished or worn band): position across the face (centred / toward one end / diagonal), and along the height (pitch line / tip / root); then the **surface condition** per the failure table below; check the **root fillets** for cracks (a dye-penetrant check on suspect teeth), the tooth tips for chipping, the keyways and bores for fretting.
5. **Backlash** at several positions around each gear (below); **end play** of each shaft (dial indicator) and bearing condition (roughness on rotation, wear of the shafts through the seals).
6. Record with photos and a sketch: the contact pattern position and width, backlash, the worst tooth, the oil condition; compare to the last inspection: gear damage is judged by its **rate of progress** more than by its presence.

## Contact pattern with bluing

![Contact patterns: centred, toe, heel, tip and root](/img/gearboxes/gear-contact-pattern.svg)

*Contact patterns: centred, toe, heel, tip and root*

1. Clean the teeth of one gear (a few teeth) with solvent; brush a thin film of **marking compound** (Prussian blue, gear marking compound; not layout dye) on the driving gear's teeth (or on the wheel of a worm set).
2. Rotate the gears **under a light load** (drag on the output by hand, a brake, or the machine's load) through several revolutions in the running direction, then back; too much load spreads the pattern and lies; no load gives a thin pattern.
3. Read the transfer on the unblued gear: the ideal is a band **centred on the face width and on the pitch line, covering about 70-80% of the face** (not to the edges: the ends are relieved), even along the whole face.

| Pattern | Meaning | Fix |
|---|---|---|
| Centred, wide, even | Correct | |
| **Heavy at one end of the face** (toe or heel on bevels; one end on spur/helical) | **Misalignment**: shafts not parallel, housing bores out of line, bearing wear, a bent shaft, or the housing distorted by uneven foot bolting | Re-align the housings/bearings; shim the bearing carriers; on bevels adjust the mounting distance and offset |
| **Diagonal band** across the face | Shafts crossed (skewed): misalignment in two planes; a deflecting shaft | As above; check deflection under load |
| **Narrow band toward the tip** | Centre distance too large (or a bevel pinion too far out): teeth engage at the tip | Reduce the centre distance / move the pinion in |
| **Narrow band toward the root** | Centre distance too small / pinion too deep | Increase / move out |
| Band centred but short in the middle only | Crowned teeth (normal on crowned gears) or a light load reading | Load and re-check |
| Pattern differs tooth to tooth | Runout of a gear (eccentric bore or bent shaft), a damaged tooth | Check runout with an indicator on the OD |
| Full-width, edge to edge | Overloaded or tooth ends not relieved; watch for end loading | |

Bevel gears: move the **pinion** axially (shims behind its bearing carrier) to move the pattern along the tooth **height** (in: toward the root and the toe; out: toward the tip and the heel), and move the **gear (crown wheel)** axially to move the pattern along the **length** (toward toe or heel) and to set backlash; the two adjustments interact: adjust, re-blue, repeat until the pattern is centred with the backlash in range. Worm sets: shift the **wheel** axially to centre the pattern; the ideal on a worm wheel is a pattern slightly on the **leaving (exit) side** of the wheel's centre so the oil is drawn into the mesh.

## Measuring backlash

- **Dial indicator (the standard)**: lock the driver (a clamp on the input shaft or the brake), put the indicator plunger **tangent to the pitch circle** on a tooth flank of the driven gear (or on a lever fixed to its shaft at the pitch radius), rock the gear back and forth against the locked driver, read the total travel. Repeat at 4 positions around the gear (runout makes it vary) and report the minimum and maximum.
- **Feeler gauge**: between the non-driving flanks at the pitch line with the driving flanks in contact; fine on large-pitch open gears, rough on fine pitch.
- **Solder wire / lead wire**: a strip of soft solder laid across the tooth, rolled through the mesh, then measured with a micrometer: the flattened thickness = backlash (plus you can read the tooth contact position from the wire's shape); the method for big open gears (mills, kilns).
- Angular backlash from a linear measurement at radius R: angle (arc-min) = linear ÷ R × 3438.

**Typical backlash (new, per AGMA 2002 class and general practice)**:

| Diametral pitch (module) | Backlash (in) |
|---|---|
| 20 DP (1.25 m) | 0.003-0.005 |
| 12 DP (2 m) | 0.005-0.007 |
| **8 DP (3 m)** | **0.007-0.010** |
| 6 DP (4 m) | 0.009-0.013 |
| 4 DP (6 m) | 0.013-0.019 |
| 3 DP (8 m) | 0.018-0.024 |
| 2 DP (12 m) | 0.027-0.037 |
| 1 DP (25 m) | 0.050-0.070 |

Rule of thumb: **0.03 ÷ DP to 0.05 ÷ DP** (0.04 × module to 0.06 × module, mm). Worn gears show 2-3× the new value; backlash increasing over successive inspections is the wear rate; a gear with backlash at 3× new is at the end of its life or the centre distance has opened (bearing wear). **Too little** backlash (after a rebuild with the wrong shims) overheats and scores.

## Tooth failure modes (AGMA 1010)

| Mode | What it looks like | Cause | Action |
|---|---|---|---|
| **Normal (polishing) wear** | Smooth, mirror-like, the machining marks slowly disappearing | Running in; fine abrasives; a thin film | Acceptable; monitor; better oil filtration |
| **Moderate / abrasive wear** | Matte, scratched in the sliding direction, the profile still good | Contaminated oil (dirt, sand, wear debris), too thin an oil | Change/filter the oil, fix the breather and seals |
| **Excessive wear** | Profile changed: a **step at the pitch line**, tooth thinned, tip sharp | Long-term abrasive wear or lubrication starvation | Replace; find the contamination source |
| **Scuffing (scoring)** | Rough, torn, streaked in the sliding direction (tip and root, not at the pitch line where sliding is zero); dull grey to welded | **Lubricant film breakdown**: oil too thin, too hot, no EP additive under high load, overload, sudden load at start | Correct the oil (viscosity, EP), cooling, load; a scuffed gear that has stopped scuffing can sometimes stay in service |
| **Micropitting (frosting, grey staining)** | A dull grey, frosted band, usually below the pitch line; under a glass: a field of microscopic pits; the profile slowly wears | Thin film relative to roughness: too low a viscosity, rough surfaces, high load; common on case-hardened ground gears with the wrong oil | Higher viscosity or a micropitting-resistant oil (FZG test), better finish; monitor the profile |
| **Macropitting (initial / progressive / destructive)** | Pits 0.5-3 mm, first along the **pitch line** (initial: often stops when the load spreads), then spreading and joining (progressive), then craters over the whole flank (destructive) | Surface fatigue from the contact stress: **overload**, misalignment (pits at one end), the end of life, soft gears | Initial: monitor; progressive on one end: fix the alignment; destructive: replace |
| **Spalling** | Large, shallow, irregular flakes (bigger than pits), often from joined pits or from a case-hardened layer letting go | Overload, case too thin, hydrogen, pits joining | Replace |
| **Plastic deformation (rolling, ridging, rippling)** | Metal pushed over the tip or into a ridge at the pitch line; wave patterns | Overload on soft (through-hardened) gears, shock; slow heavily loaded gears | Load reduction; harder gears |
| **Bending fatigue (root crack, tooth breakage)** | A crack in the **root fillet**, then a tooth broken out with a **beach-marked** (smooth, curved lines) fracture face and a final rough zone | Cyclic overload, stress concentration (a nick, a sharp fillet, a grinding step, corrosion pit), misalignment loading one end, a case-hardening crack | Replace the gear **and** the mating gear (a broken tooth's pieces damage everything); find the overload or the notch |
| **Overload breakage** | One or more teeth snapped with a rough, crystalline fracture face, no beach marks | A single shock: a jam, a foreign object, a brake failure, a coupling failure | Replace; inspect everything downstream |
| **Case crushing / subcase fatigue** | Long cracks parallel to the surface, large flakes with the whole case gone | Case too thin for the load, soft core | Design issue; replace with correct heat treatment |
| **Electrical erosion (fluting)** | Regular fine lines across the flank | Current through the mesh (VFD, welding ground) | Grounding fixes as for [bearings](/article/bearing-failure-analysis) |
| **Corrosion** | Pits with rust, etched surfaces, often on the unloaded flanks too | Water in the oil, condensation, acidic oil, chemical fumes | Fix the water/breather; change oil |
| **Interference / tip contact** | Wear at the tips and a groove in the mating root | Wrong centre distance, wrong gears (pressure angle, DP mismatch) | Correct the mesh |

Pitting that appears at **one end of the face** = misalignment; along the whole pitch line = load/oil; on the **driver only** or on **one tooth only** = runout, a damaged tooth, or a hunting-tooth issue.

## Gear replacement rules

- Replace **mating pairs** unless the other gear is verified undamaged and the wear step is under 0.005"; a new pinion against a worn wheel wears out fast.
- Match DP/module, pressure angle, helix angle and hand, face width, material and hardness (the pinion is usually made a little harder than the wheel, on the order of 30-40 HB), and the AGMA quality.
- Set backlash and contact pattern per above after any bearing or shaft change: bearing end play and preload are what position the gears (see [tapered roller bearing setting](/article/tapered-roller-bearing-setting)).
- Run-in a new set: half load for several hours, oil change after the run-in (the fine wear debris), then inspection.

## Related

- [Gearbox lubrication and inspection](/article/gearbox-lubrication-and-inspection)
- [Planetary and worm reducers](/article/planetary-and-worm-reducers)
- [Dodge torque-arm shaft-mount reducer](/article/dodge-torque-arm-shaft-mount-reducer)
- [Tapered roller bearing setting](/article/tapered-roller-bearing-setting)
- [Oil viscosity and selection](/article/oil-viscosity-and-selection) and [oil analysis and sampling](/article/oil-analysis-and-sampling)
- [Vibration signatures (gear mesh)](/article/vibration-signatures)
