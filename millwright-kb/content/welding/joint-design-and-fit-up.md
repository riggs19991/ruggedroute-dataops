---
title: "Weld Joint Design and Fit-Up: Groove Types, Bevel Angles, Root Opening and Land, Prequalified Joint Dimensions, Tacking Sequence and Fit-Up Tolerances"
slug: joint-design-and-fit-up
category: welding
kind: reference
tags: [joint design, weld joint, butt joint, V groove, bevel angle, root opening, root face, land, fillet weld, tee joint, lap joint, corner joint, fit up, tack weld, tacking sequence, backing bar, prequalified joint, D1.1 joint, gap, misalignment, hi-lo]
source: "AWS D1.1 Structural Welding Code, Clause 5 prequalified joint details and fit-up tolerances (Figures 5.1/5.2, Tables 5.4-5.5); AWS A3.0 terms; Lincoln Electric Procedure Handbook of Arc Welding."
summary: "The five joint types and the groove shapes cut into them, the dimensions that matter (bevel angle, root opening, root face), the standard prequalified numbers for stick, MIG and flux-core, how much fit-up error is allowed, and the tacking sequence that keeps a joint from pulling out of square before you weld it."
---

## The five joints

| Joint | Where the parts meet | Typical welds |
|---|---|---|
| **Butt** | Edge to edge in the same plane | Square, V, bevel, U, J grooves |
| **Tee** | One part ends against the face of another at ~90° | Fillet, bevel or J groove for full penetration |
| **Lap** | Parts overlap | Fillet each side, plug or slot welds |
| **Corner** | Edges meet at ~90° forming an L | Fillet inside, bevel/V groove outside |
| **Edge** | Parallel faces, edges flush | Edge weld (sheet metal only) |

## Groove geometry words

```
        bevel angle ──┐      groove angle = both bevels added
                  ╲   │   ╱
   plate ─────────╲   │  ╱──────── plate
                   ╲  │ ╱
                    ╲ │╱   ← root face (land): the flat left at the bottom
      root opening →  ├──┤  (gap between the parts)
```

- **Bevel angle**: cut on one plate (e.g. 30°). **Groove angle**: the total included angle (two 30° bevels = 60° V).
- **Root opening (gap)**: space between the parts at the root. More gap = easier penetration, more filler, more distortion.
- **Root face (land)**: flat left unbevelled at the bottom. Too thin melts through; too thick does not fuse.
- **Backing**: a bar or ring behind the root that lets you run hot without burn-through; steel backing stays in place (or is removed and back-gouged), ceramic backing is removed.
- **Back-gouge**: grinding or arc-gouging the root from the second side down to sound metal before welding the second side.

## Which groove for which thickness (steel)

| Thickness | Joint | Notes |
|---|---|---|
| ≤ 3/16" (5 mm) | **Square groove**, gap 0 to 1/16-1/8" | Full penetration from one side with a gap and MIG/stick; from two sides with no gap up to 1/4" |
| 3/16-3/4" (5-20 mm) | **Single V**, 60° included, 1/8" gap, 0-1/8" land | The everyday plate joint; single side with backing or open root |
| 3/4-1.5" | **Double V** (both sides) | Halves the filler, balances distortion; needs access to both sides |
| > 1" thick, expensive filler or restricted access | **U or J groove**, 1/4" radius, 20° bevel | Less filler than V; needs machining or careful gouging |
| Tee, full penetration | **Single or double bevel**, 45° each, 1/4" gap with backing, or 3/16" open root | Bevel only the branch member |
| Pipe | **37.5° bevel** (75° included), 1/16-1/8" land, 1/8" gap (3/32" for TIG root) | Standard API/ASME pipe prep |

## Prequalified numbers (AWS D1.1, stick / MIG spray / FCAW)

Use these when no procedure tells you otherwise; they are the joints that codes have already proven.

| Joint (D1.1 designation) | Groove angle | Root opening | Root face | Notes |
|---|---|---|---|---|
| Square groove, welded both sides (B-P1c) | - | ≤ T/2 | - | Up to 1/4" for SMAW |
| Single V, backing (B-U2a) | 30° with 1/4" gap; **45° with 1/4" gap**; 20° with 1/2" gap | as listed | 0 | With steel backing |
| Single V, no backing, back-gouged (B-U2) | 60° | 0-1/8" | 0-1/8" | Weld side 1, gouge, weld side 2 |
| Single V open root, stick (B-U2 "open root") | 60° | 1/8-3/16" | 0-1/8" | E6010 root, 7018 fill typical |
| Double V (B-U3b) | 60° both | 0-1/8" | 0-1/8" | Alternate sides to control distortion |
| Single bevel tee, backing (TC-U4a) | 45° | 1/4" | 0 | |
| Single bevel tee, back-gouged (TC-U4b) | 45° | 0-1/8" | 0-1/8" | |
| U groove (B-U6) | 20° bevel, 1/4" radius | 0-1/8" | 1/8" | |

**Fit-up tolerances (D1.1 prequalified, as fit)**: root opening **±1/16"** without backing, +1/4"/−1/16" with backing; root face ±1/16"; groove angle +10°/−5°. Gaps up to 3/16" over the drawing can be **buttered** (built up on one face) and then welded; bigger gaps need a backing or a splice strip, never just "fill it".

**Misalignment (hi-lo)**: butt joints of equal thickness, offset ≤ 10% of thickness, max 1/8" (D1.1). Pipe: usually ≤ 1/16" for TIG roots, 3/32" for stick. Offsets over that get a taper of 1 in 2.5 (2.5:1) ground on the thicker part.

## Fillet welds

- **Size** = leg length. Minimum fillet size by the **thicker** part (D1.1 Table 5.7): up to 1/4" → 1/8"; over 1/4" to 1/2" → 3/16"; over 1/2" to 3/4" → 1/4"; over 3/4" → 5/16".
- Maximum single-pass fillet: about **5/16" with 7018 or MIG spray, 3/8" with FCAW** in the flat position; bigger fillets are multi-pass.
- Fillet gap: fit the parts tight. **Each 1/16" of gap adds 1/16" to the required leg** (up to a 3/16" max gap allowed by D1.1); over 3/16" needs a backing or a repair of the fit.
- Throat = 0.707 × leg for an equal-leg fillet; strength comes from the throat.

## Edge preparation

| Method | Use | Watch |
|---|---|---|
| Oxy-fuel bevel (track burner or bevel tip) | Carbon steel plate, any thickness | Grind off scale and the 1/32" hardened skin on high-carbon steel |
| Plasma bevel | Steel, stainless, aluminium | Remove dross, grind nitrided face on stainless if a code job |
| Grinder | Small jobs, root faces, cleaning | Consistent angle with a bevel gauge |
| Plate beveller / pipe beveller | Production and pipe | |
| Machining | U/J grooves, precision | |

Clean **1" back from the joint** on both faces: mill scale, rust, paint, oil, galvanising. Check the bevel with a **fillet/bevel gauge**, mark the root face with a scribe, and dry-fit before tacking.

## Tacking

1. Tack size: tacks about **2 × plate thickness long** at spacing **6-12"** (sheet: 1" tacks every 2-3"). Undersized tacks crack when the plate pulls.
2. Sequence on a long butt: **ends first, then the middle, then halve the spaces**; on a square frame, tack opposite corners.
3. Tack with the same electrode/wire family as the root (7018 tacks in a 7018 joint; never 6013 tacks in a code joint). Grind tack ends to a feather so the root pass fuses over them.
4. Set the root gap with a **spacer** (a piece of 1/8" wire or a gap gauge) and pull it before welding.
5. Check square and level **after** tacking and again after the root; a preset of 2-3° opposite to the expected pull on a single-V is normal (see [distortion control](/article/distortion-control)).
6. Tacks that crack, are porous or have arc strikes beside them get ground out, not welded over.

## Common mistakes

- Beveling both sides of a tee (only the branch is bevelled).
- Root face ground to nothing: the root falls through; 1/16-1/8" land carries the root.
- Welding a fillet over a 1/4" gap at the drawing size: the throat is gone.
- Backing bar not tight to the plate: slag traps and root cracks. Clamp it hard; on pipe, use the right ID backing ring.
- Beveling 45° each side (90° included) "to be safe": twice the filler and twice the distortion of a 60° groove.

## Related

- [Weld positions and techniques](/article/positions-and-techniques)
- [Distortion control](/article/distortion-control)
- [Welding symbols](/article/welding-symbols)
- [Weld defects and inspection](/article/weld-defects-and-inspection)
- [Stick setup](/article/smaw-stick-setup), [MIG setup](/article/gmaw-mig-setup)
