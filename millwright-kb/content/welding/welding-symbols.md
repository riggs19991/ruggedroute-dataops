---
title: "Welding Symbols (AWS A2.4): Reference Line, Arrow Side and Other Side, Fillet and Groove Symbols, Size, Length and Pitch, Contour and Finish, Weld-All-Around, Field Weld, Backing, Melt-Through, with Worked Examples"
slug: welding-symbols
category: welding
kind: chart
tags: [welding symbols, weld symbol, AWS A2.4, reference line, arrow side, other side, fillet symbol, groove symbol, bevel symbol, weld size, pitch, intermittent weld, staggered, weld all around, field weld, contour symbol, finish symbol, backing symbol, melt through, plug weld, slot weld, spot weld, tail, blueprint welding, reading welding symbols, ISO 2553]
source: "AWS A2.4:2020 Standard Symbols for Welding, Brazing and Nondestructive Examination; AWS welding symbol chart; ISO 2553 (for the differences)."
summary: "How to read every part of a welding symbol on a drawing, with the rules that trip people up (which side of the line is the arrow side, where size and length go, what a break in the arrow means, groove depth versus effective throat) and twelve worked examples read out in plain English. Includes the Canadian/ISO differences."
---

## Anatomy

```
                    finish symbol ─┐
                  contour symbol ──┤     ┌── groove angle
                root opening ──┐   │     │   ┌── length - pitch
                               │   │     │   │
              other side ──►  S(E) ▽  ... L - P
   ─────────────────────────────────────────────────────────◄───── arrow
              arrow side ──►  S(E) ▷  ... L - P
                               ▲  ▲
                 size / depth ─┘  └── weld symbol (this one: fillet)
   ┌───┐
   │tail│ ◄── process, spec, WPS, "typ", notes (omitted if nothing to say)
   └───┘
   Circle at the junction = weld all around;  flag at the junction = field weld
```

- **Reference line**: horizontal. Everything **below** the line is the **arrow side** of the joint (the side the arrow touches). Everything **above** is the **other side**. Symbols on both = both sides.
- **Arrow**: points to the joint. A **broken (bent) arrow** on a bevel or J symbol points to the member that gets the bevel.
- **Weld symbol** (the little picture) sits on the line. **Welding symbol** = the whole assembly.
- Multiple reference lines stacked from the arrow show the **sequence** (first operation nearest the arrow).
- Symbols are drawn the same regardless of which way the arrow points: the fillet triangle always has its vertical leg on the **left**.

## Weld symbols

| Symbol | Name | Notes |
|---|---|---|
| ▷ (right triangle, vertical leg left) | **Fillet** | Most common |
| ‖ | **Square groove** | |
| V | **V-groove** | Both members bevelled |
| ⊾ (one vertical, one slanted leg) | **Bevel groove** | One member bevelled; broken arrow shows which |
| U | **U-groove** | |
| J | **J-groove** | Broken arrow shows which member |
| flare-V, flare-bevel | Rounds/tubes to plate | |
| ▭ (rectangle) | **Plug or slot** | Fill a hole/slot in the arrow-side member |
| ○ on the line | **Spot / projection** | Resistance or arc spot |
| ⊖ | **Seam** | |
| ⌒ half-circle on the opposite side | **Back / backing weld** | Back weld = after the groove; backing weld = before |
| ▭ with "backing" | Backing bar (with R if to be removed) | |
| ⌒⌒ (two half circles) | **Surfacing** (build-up, hardfacing) | Size = thickness of deposit |
| ⊗ | **Stud** | |
| ⌢ black on the opposite side | **Melt-through** | Full penetration with visible root reinforcement |
| ⧗ small flag at junction | **Field weld** | Made on site, not in the shop |
| ○ at junction | **Weld all around** | |
| ─ ⊂ (flush/flat), ⌒ (convex), ⌣ (concave) | **Contour** | Above/below the weld symbol |
| G, M, C, H, R, U | **Finish** method: grind, machine, chip, hammer, roll, unspecified | With the contour symbol |

## Where the numbers go

| Position (relative to the weld symbol) | Fillet | Groove |
|---|---|---|
| **Left** | **Size** (leg length): `1/4 ▷` = 1/4" fillet; unequal legs `1/4 x 3/8 ▷` (orientation given on the drawing) | **Depth of preparation S**, and **effective throat (E)** in parentheses: `1/2 (5/8) V` = 1/2" deep bevel giving 5/8" throat; nothing = full penetration (CJP) |
| **Right** | **Length** and **pitch**: `▷ 6-12` = 6" long fillets, 12" centre to centre; `▷ 6` = 6" long, once; nothing = full length | Same for intermittent groove welds (rare) |
| **Inside the symbol** | | **Root opening**: `V` with `1/8` inside = 1/8" gap |
| **Outside the opening of the symbol** | | **Groove angle**: `60°` above a V; `45°` beside a bevel |
| **Above the symbol (arrow side: below the line)** | Contour and finish | Contour and finish |
| Plug/slot | Size of hole left, depth of fill inside, angle of countersink, pitch right | |
| Spot/seam | Size or strength left, number of spots in parentheses, pitch right | |
| Tail | Process (SMAW, GMAW, FCAW, GTAW), spec, "see note 3", "typ" | |

**Intermittent fillets on both sides**: symbols aligned = chain intermittent (welds opposite each other); symbols **staggered** along the line = **staggered** intermittent. `▷ 3-12` both sides staggered means 3" welds every 12" alternating sides, so a weld every 6" if you count both sides.

**Dimensions in the tail or a note override symbols** only when the note says so; "typ" means the same symbol applies to all similar joints on the drawing.

## Worked examples

1. `1/4 ▷` below the line, nothing above: **1/4" fillet, arrow side, full length.**
2. `▷ 1/4` above and `▷ 1/4` below: **1/4" fillets both sides, full length.**
3. `5/16 ▷ 2-6` below: **5/16" fillet, arrow side, 2" long every 6" (2" weld, 4" gap).**
4. `1/4 ▷ 3-12` below and `1/4 ▷ 3-12` above, staggered: **1/4" staggered intermittent fillets both sides, 3" welds on 12" centres, offset.**
5. `▷` with a **circle** at the junction: **fillet all around** the member (e.g. a pipe stub to plate).
6. `▷` with a **flag**: **field weld**.
7. `V` with `60°` above it and `1/8` inside, nothing left: **full-penetration single-V groove, 60° included, 1/8" root opening, arrow side** (both members bevelled 30°).
8. `⊾` with a **broken arrow** to the vertical plate, `45°`, `1/4` inside, and a `backing` rectangle above: **single-bevel groove on the vertical member, 45°, 1/4" gap, with a backing bar on the other side.** Add `R` in the backing rectangle = remove the bar after welding.
9. `3/8 (1/2) V` below: **partial-penetration V-groove, 3/8" deep preparation, effective throat 1/2"** (the extra 1/8" comes from penetration past the bevel).
10. `V` below and `⌒` (back weld) above with a flush contour and `G`: **V-groove arrow side, then back-weld the other side and grind flush.**
11. `‖` with `1/16` inside, both sides: **square groove welded both sides with a 1/16" gap.**
12. `▭ 3/4` below with `1/2` inside and `6` right: **plug welds in 3/4" holes in the arrow-side plate, filled 1/2" deep, 6" apart.**
13. `⌒⌒ 1/8` below: **surfacing (build-up) 1/8" thick on the arrow side.** Direction or pattern in the tail.
14. `▷` below with a concave contour `⌣` and `M`: **fillet, machined to a concave face** (e.g. a shaft fillet).
15. Two reference lines from one arrow: nearest `V` (arrow side), second `⌒`: **weld the groove first, then the back weld.**
16. Melt-through `⌢` black symbol above a `‖` square groove below: **full penetration from one side with root reinforcement showing on the other side** (thin material, TIG on sheet, pipe roots).

## Red Seal / Canadian and ISO notes

CSA W59 uses the same AWS A2.4 symbols. **ISO 2553** (European drawings, some equipment manuals) differs: the fillet symbol is an isosceles triangle, the reference line has a **dashed identification line** for the other side (symbol on the dashed line = other side), size is written `a5` (throat) or `z7` (leg) before the symbol, and the field weld flag looks the same. If a drawing has a dashed line under the reference line, read it as ISO; "a" size is **throat**, not leg (leg ≈ 1.4 × a).

## Common mistakes

- Reading "below the line" as "below the joint": it is the **arrow side**, wherever the arrow points.
- Taking `1/4 ▷ 6-12` as 6" gap, 12" weld: it is a 6" **weld** on 12" **centres**.
- Assuming a bevel symbol means "either side can be bevelled": the broken arrow says which one.
- Missing the weld-all-around circle on a pipe support and welding only the top.
- Treating the size as the throat on a fillet: it is the **leg**. Throat = 0.707 × leg.
- Full-length weld where the symbol had a length: extra cost and distortion; or intermittent where full length was called: rejected.

## Related

- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [Joint design and fit-up](/article/joint-design-and-fit-up)
- [Weld defects and inspection](/article/weld-defects-and-inspection)
- [Positions and techniques](/article/positions-and-techniques)
