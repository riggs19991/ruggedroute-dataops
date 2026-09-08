---
title: "Weld Distortion Control: Why Steel Moves, Angular and Longitudinal Shrinkage Rules of Thumb, Presetting, Back-Stepping, Sequencing, Restraint, Peening and Straightening"
slug: distortion-control
category: welding
kind: procedure
tags: [distortion, warping, shrinkage, angular distortion, presetting, back step welding, skip welding, weld sequence, restraint, clamping, strongback, peening, flame straightening, heat straightening, transverse shrinkage, longitudinal shrinkage, buckling, thin plate warping]
source: "Lincoln Electric Procedure Handbook of Arc Welding (distortion chapter); The Welding Institute (TWI) distortion guidance; AWS D1.1 Clause 7 (heat straightening limits 1100°F for quenched-and-tempered, 1200°F for other steels)."
summary: "How much a weld shrinks and in which direction, the practical rules for predicting it, and the sequence of choices (joint design, presetting, restraint, welding order, heat input) that keep a fabrication square, plus how to straighten what still moved with heat."
---

## Why it moves

Weld metal and the plate next to it are put in at melting temperature and shrink as they cool; the cold plate around them resists, so the part bends toward the weld and gets shorter along it. Three things you can measure:

| Movement | What it looks like | Rule of thumb (steel) |
|---|---|---|
| **Transverse shrinkage** | Butt joint gets narrower across the weld | ≈ **1/16" per butt weld** in 1/4-1/2" plate (0.5-2.5 mm); more with bigger gaps and groove volume: shrinkage ≈ 0.2 × (weld cross-section area ÷ thickness) + 0.05 × gap |
| **Longitudinal shrinkage** | Part gets shorter along the weld | ≈ **1/32" per 10 ft of weld** for a single fillet (1 mm per 3 m); bows the part toward the weld if the weld is off the neutral axis |
| **Angular distortion** | Plate rotates about the weld (a V-groove closes on the wide side; a tee leans toward the fillet) | Single-V 1/2" plate, 60°: **3-5°**; single fillet on a tee: **1-3°**; double-sided balanced welds: near zero |
| **Buckling** | Thin sheet (< 1/4") waves between welds | Governed by heat input: fewer, smaller, intermittent welds |

More heat input (amps × volts ÷ travel speed) = more distortion. Bigger weld than needed = more distortion. One-sided welds = angular distortion. Welds away from the neutral axis = bowing.

## Control in order of effectiveness

![Back-step and skip sequences, presetting and balanced welds](/img/welding/distortion-sequences.svg)

*Back-step and skip sequences, presetting and balanced welds*

### 1. Design and prep (free)

- **Do not over-weld**: a 1/4" fillet where 3/16" is called for has 78% more metal and shrinkage. Intermittent fillets (e.g. 2-6, 3-12 stagger) where the code allows.
- **Balance the welds** about the neutral axis: double-V instead of single-V over 3/4"; fillets on both sides of a tee; symmetric stiffeners.
- **Fewer passes**: on thick sections a few large passes distort less than many small ones (the opposite of what people expect), within the heat-input limit of the procedure.
- **Minimum groove volume**: 60° V not 90°; U groove on thick plate; smallest root gap that still penetrates.
- Locate welds where shrinkage does not matter, and put the biggest welds first at the neutral axis.

### 2. Preset (bend it the wrong way first)

- Single-V butt, 1/2" plate: tack with the plates opened up **3-5°** away from the weld side; they close to flat.
- Tee with a single fillet: tilt the flange 1-3° away from the weld side.
- Long butt joints: fit with a slight taper (gap opens toward the free end) so it closes as you weld from the fixed end: the joint "walks" closed.
- Cambering beams: weld the flange to web on the side that will bow the beam the way you want.

### 3. Restraint (fix it so it cannot move)

- Clamps, dogs and wedges, **strongbacks** (a bar tacked across the joint on the back side with wedges under it), fixtures, tacking to a heavy table.
- Restraint stops distortion but locks in **residual stress**; it can crack high-carbon or thick joints (add preheat) and the part may spring when released. Balance it against presetting.
- Tack more and closer on thin material (every 2-3").

### 4. Sequence (the order of welding)

| Technique | How | Use |
|---|---|---|
| **Back-step** | Weld each 4-8" segment in the opposite direction to the overall progression | Long butt joints, thin plate |
| **Skip (wandering)** | Weld 1, 5, 3, 7, 2, 6... segments | Long fillets, sheet |
| **Alternate sides** | Weld a pass on side A, then side B, keep going | Double-V, double-fillet tees |
| **Weld toward the free end** | Start at the fixed/clamped end so shrinkage has somewhere to go | Frames, anything with one end trapped |
| **Balance about the axis** | Pair welds symmetrically (two welders opposite each other on a pipe or column) | Beams, columns, pipe |
| **Weld from the centre out** | On a plate with several stiffeners, do the middle one first | Decks, tank floors |
| **Root first, then balance** | On a big double-V, root and a couple of passes, back-gouge, then alternate | Heavy plate |

### 5. Heat control

- Preheat evenly (it reduces the temperature gradient, so less distortion, but it also softens thin sheet: use it for thick, not thin).
- Lower heat input where possible: smaller wire, short-circuit or pulse instead of spray on sheet, stringers.
- Let welds cool between passes on sheet (the opposite of interpass control on thick sections, which is about cracking).
- **Chill bars** (copper or aluminium bars clamped beside the joint) pull heat out of thin stainless and aluminium.

### 6. Peening

Hammering each intermediate bead (not the root or the cap on code work, and never with a needle scaler as a substitute for procedure) stretches it and relieves shrinkage. Allowed under D1.1 between passes; check the WPS. Light peening at the crater helps against crater cracks on heavy sections.

## Fixing it afterwards

### Mechanical

Press, jacks, dogs and wedges, a "come-along" on a frame: works on angular distortion of heavy parts. Do not hammer cold on quenched-and-tempered or high-carbon steel.

### Flame (heat) straightening

Heat a spot or a V-shaped wedge with a rosebud on the **convex** (long) side, let it try to expand, the cold surrounding metal stops it, and it shrinks on cooling, pulling the plate back. Rules:

- Temperature: **dull red, about 1100-1200°F (600-650°C)** for mild steel; D1.1 caps it at **1200°F for ordinary steels and 1100°F for quenched-and-tempered** (A514/A517, A709 HPS). Use a temp stick, never guess in daylight; over 1300°F you change the steel.
- Heat **quickly** with a large tip so the surface gets hot before the whole thickness does.
- Spot heats 1-2" diameter on plate buckles, **V heats** (apex at the compression side, base at the tension side) on flanges and bars, **line heats** along a fillet to pull a tee flange back.
- Let it air cool; water-quenching mild steel after the heat is done is common but never on Q&T or high-carbon steel.
- Expect to repeat: several small heats beat one big one.
- Compensating heats on the opposite side to the weld on a warped tee flange: heat the flange on the side away from the fillet in lines opposite the weld.

## Worked example

A 3/8" tee, 6 ft long, single 1/4" fillet. Expect the flange to lean about 2° toward the fillet: over a 6" wide flange that is about 0.2" out of flat at the edge. Options: weld both sides with 3/16" fillets (balanced, no lean, similar strength), preset the flange 2° the other way with wedges, or clamp it flat and expect to straighten with a line heat. A 1/4" fillet can also be run as 3-12 intermittent if the drawing allows, cutting shrinkage by half.

## Related

- [Joint design and fit-up](/article/joint-design-and-fit-up)
- [Positions and techniques](/article/positions-and-techniques)
- [Preheat, interpass and carbon equivalent](/article/preheat-interpass-and-carbon-equivalent)
- [Oxy-fuel heating with a rosebud](/article/oxy-fuel-heating-rosebud)
- [Steel grades and heat colours](/article/steel-grades-and-heat-colours)
