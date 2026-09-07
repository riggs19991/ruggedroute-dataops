---
title: "Blueprint Reading for Millwrights: Views and Projection, Line Types, Sections, Title Block and Revisions, Dimensions and Tolerances, Surface Finish, GD&T Essentials, Structural Shapes, Piping Isometrics and P&IDs"
slug: blueprint-reading-for-millwrights
category: welding
kind: reference
tags: [blueprint reading, reading drawings, mechanical drawings, orthographic projection, third angle, first angle, line types, hidden line, center line, section view, title block, revision block, bill of materials, tolerances, block tolerance, surface finish, Ra, GD&T, feature control frame, flatness, perpendicularity, position, runout, structural shapes, W12x26, HSS, piping isometric, P&ID, ISA symbols, assembly drawing, detail drawing]
source: "ASME Y14.100 (engineering drawing practices), Y14.3 (orthographic and pictorial views), Y14.5-2018 (GD&T), Y14.36 (surface texture); AISC Steel Construction Manual shape designations; ISA 5.1 instrumentation symbols; ASME B16.9 fitting dimensions."
summary: "The parts of a drawing a millwright reads to install, fabricate or check a part: how views relate, what each line style means, how to read sections and details, the title block and revision level, dimensions and the tolerance rules, surface finish marks, the GD&T symbols that appear on baseplates and shafts, how structural steel and piping drawings label their members, and the P&ID symbols you need to trace a system."
---

## Views and projection

- **Orthographic projection**: the object is shown in flat views at 90° to each other. **Third-angle** (US and Canada): the top view is above the front view, the right side view is to the right (as if the object were unfolded toward you). **First-angle** (Europe, some equipment manuals): views are on the opposite sides (the right-side view appears on the left). The projection symbol in the title block (a truncated cone, small end left for third angle) tells you which.
- Six possible views; drawings show as many as needed, usually front, top, right. Curved surfaces and holes look the same in one view and different in another: always read at least two.
- **Section views** (A-A, B-B): the part is cut along the cutting-plane line (thick line with arrows; the arrows point in the direction you look) and the cut material is **hatched**. Full, half, offset, broken-out, revolved and removed sections. Shafts, bolts, keys, ribs and webs are conventionally **not** hatched even when the plane cuts them.
- **Detail views**: a circle on the main view, enlarged elsewhere with a scale (e.g. DETAIL B, SCALE 2:1).
- **Auxiliary views**: a view perpendicular to an inclined face so it shows true size.
- **Assembly drawing**: shows parts fitted together with balloons (item numbers) tied to a **bill of materials (BOM)**; **detail drawing**: one part, fully dimensioned; **exploded** view for order of assembly.
- **Isometric / pictorial**: 3D look, 30° axes; not to scale for measuring.

## Line types (alphabet of lines)

| Line | Appearance | Means |
|---|---|---|
| Visible (object) | Thick solid | Edges you can see |
| **Hidden** | Medium dashed | Edges behind the surface |
| **Centre** | Thin, long-short-long | Axis of a hole, shaft, symmetry; bolt circles |
| Dimension | Thin solid with arrowheads | The measurement |
| Extension | Thin solid, gap from the object | Carries the dimension out from the part |
| Leader | Thin with an arrow or dot | Points a note to a feature |
| Cutting plane | Thick, dashed or phantom, arrows at the ends | Where a section is taken |
| Section (hatch) | Thin diagonal | Cut material; pattern can show the material |
| Break | Thin zigzag (short) or wavy (long) | Part shortened on the drawing |
| Phantom | Thin, long-short-short-long | Alternate positions, adjacent parts, motion limits, repeated detail |
| Stitch | Thin dotted | Sewing/stitching, sometimes stitch welds |
| Chain | Thick, long-short | Surface requiring special treatment |

## Title block and revisions

Read **before** measuring anything: **drawing number and sheet**, **revision letter** (compare with the revision block and with the version on the work order: an old print is the classic cause of a wrong part), **scale** (never scale a print with a ruler; "NTS" = not to scale), **units** (inches or mm; dual dimensions show both), **material**, **finish**, **block (general) tolerances**, **projection symbol**, **drawn/checked/approved** names and dates, the standard the drawing follows (ASME Y14.5, ISO), and **general notes** (e.g. "break all sharp edges .015", "all welds 1/4 fillet unless noted", "dimensions apply after plating").

## Dimensions and tolerances

- **Basic dimension** (boxed): theoretically exact, toleranced by a geometric control.
- **Reference dimension** (in parentheses): for information; not inspected.
- **Limit dimensions**: 1.500-1.502; **plus/minus**: 1.501 ± .001; **unilateral**: 1.500 +.002/−.000.
- **Block tolerances** in the title block apply where no tolerance is shown, usually by decimal places: `.X ± .1`, `.XX ± .01`, `.XXX ± .005`, angles ± 0.5°, fractions ± 1/16". So a "2.50" dimension is ± .01 and a "2.500" is ± .005: the number of decimals is a tolerance statement.
- Metric: `50 h7` and `50 H7` use the ISO fit tables (see [bearing fits](/article/bearing-clearance-and-fits-tables)); unspecified metric tolerances follow ISO 2768 (m, f, c classes) named in the title block.
- **Chain vs baseline dimensioning**: chain dimensions accumulate tolerance; baseline (all from one datum) does not. Fabricate from the datum the drawing uses.
- Thread callouts: `1/2-13 UNC-2B` (nominal, TPI, series, class, B = internal), `M12 x 1.75-6H`; depth `↓ .75`; `1/2-14 NPT`. Hole callouts: `Ø .531 THRU`, `⌴ Ø .875 ↓ .375` (counterbore), `⌵ Ø .750 x 82°` (countersink), `4X Ø .406` (four places).

## Surface finish

The check-mark symbol with a number is the **roughness average Ra** in **microinches** (μin) on US drawings, **micrometres** (μm) on metric (1 μm = 40 μin).

| Ra μin (μm) | Process | Typical |
|---|---|---|
| 250 (6.3) | Saw, flame cut, rough machining | Non-contact surfaces |
| 125 (3.2) | Standard machining | General parts, bolted faces |
| **63 (1.6)** | Fine turning, milling | Bearing housings, mating faces, baseplate pads |
| **32 (0.8)** | Fine grind, finish turn | Shaft seats for bearings, seal faces |
| 16 (0.4) | Grinding, honing | Seal sleeves, hydraulic rods, lip seal surfaces (10-20 μin) |
| 8 (0.2) and below | Lapping, polishing | Mechanical seal faces, gauge blocks |

A bar under the symbol = machining required; a circle = machining prohibited (as-cast). A lay symbol (=, ⊥, X, M, C, R) shows the direction of the tool marks: lip seals want **no lead** (plunge grind), hence "C" or "no lay" callouts on shafts.

## GD&T essentials

A **feature control frame** reads: `| symbol | tolerance | datum A | datum B | datum C |`. Datums are lettered surfaces/axes marked with a triangle. Symbols a millwright meets:

| Symbol | Name | What it controls | Where you see it |
|---|---|---|---|
| ⏥ | **Flatness** | Surface within two parallel planes, no datum | Baseplate pads, sole plates, sealing faces |
| ⏤ | Straightness | Line elements / axis | Shafts |
| ○ | Circularity (roundness) | | Sleeves, seats |
| ⌭ | Cylindricity | | Hydraulic rods |
| ∥ | Parallelism | Surface/axis parallel to a datum | Pads to a base, bores to each other |
| ⊥ | **Perpendicularity** | Square to a datum | Flange face to bore, pump feet |
| ∠ | Angularity | | |
| ⌖ | **Position** | Location of holes/features from datums, usually with a **cylindrical** tolerance zone and often **Ⓜ (MMC)** | Bolt patterns |
| ◎ | Concentricity (withdrawn in 2018, still on old prints) | | |
| ⌯ | Symmetry (withdrawn 2018) | | |
| ↗ | **Circular runout** | Wobble of a surface as it rotates about a datum axis, one revolution | Shaft seats, coupling faces |
| ⌰ | **Total runout** | Same, over the whole surface | Shaft bearing seats, rotor faces |
| ⌒ | Profile of a line | | |
| ⌓ | Profile of a surface | The all-purpose 3D tolerance | Castings, machined contours |

Modifiers: **Ⓜ** maximum material condition (bonus tolerance as the feature departs from MMC: bigger holes get more position tolerance), **Ⓛ** least material, **Ⓟ** projected tolerance zone (for studs). Reading a frame: `⌖ Ø.010 Ⓜ A B C` = position of the hole axis within a Ø.010 cylinder when the hole is at its smallest, relative to datums A (primary, usually the mounting face), B, C. What it means for you: measure from the datums the frame names, in the order named, and expect the flatness or runout number to be an inspection you may have to prove with a straightedge, feeler, level or dial indicator (see [dial indicator basics](/article/dial-indicator-use)).

## Structural steel drawings

| Designation | Shape | Reads |
|---|---|---|
| **W12×26** | Wide flange | 12" nominal depth, 26 lb/ft |
| S8×18.4 | American standard I-beam | |
| **C8×11.5** / MC | Channel | 8" deep, 11.5 lb/ft |
| **L4×4×3/8** | Angle | Legs 4" and 4", 3/8" thick (L4×3×1/4 unequal) |
| **HSS6×6×1/4** | Hollow structural section (tube) | 6×6 outside, 1/4" wall (design wall 0.233) |
| HSS6.625×0.280 | Round HSS | OD × wall |
| **PL 1/2×12×1'-6"** | Plate | Thickness × width × length |
| WT6×13 / ST / MT | Tees cut from W/S/M | |
| Pipe 4 STD / XS / XXS | Pipe by schedule | |
| BAR 2×1/2, RD 1-1/2 | Flat bar, round bar | |

Structural drawings use **grid lines** (A, B, 1, 2) and **elevations** ("T/S EL. 112'-6"" = top of steel), **member marks** (B12, C3), **bolt callouts** (`3/4" Ø A325-N` = 3/4" high-strength bolts, threads not excluded; `SC` slip-critical; `TC` tension-control), "**typ**" and "**UNO**" (unless noted otherwise), "**NS/FS**" (near side/far side), "**GA**" gauge (bolt line offset), "**CTR**" centre, "**FIELD**" for field bolts/welds. Feet-inches format: `12'-6 1/2"`. Camber and "**hold**" dimensions (do not change) appear on erection drawings.

## Piping isometrics

- Drawn on 30° isometric axes, not to scale; north arrow; the line number carries the service, size, spec and insulation (e.g. `6"-CW-1501-A1-HC`).
- Symbols: butt-weld fittings as thin lines with **weld dots**; flanges as double lines; valves by type (gate, globe, check, ball, butterfly) with tag numbers; reducers (concentric/eccentric, **FOT** flat on top / **FOB** flat on bottom); elbows LR (radius 1.5 × NPS) or SR; tees, olets; **field weld** (FW) and **field fit weld** (FFW) with extra length to cut on site; spool numbers and material take-off (MTO) table.
- Dimensions run **centreline to centreline** and to flange faces; you subtract fitting **take-outs** (LR 90° elbow centre-to-face = 1.5 × NPS: 6" pipe → 9"; 45° LR = 0.625 × NPS: 6" pipe → 3-3/4") and the weld gap to get cut lengths. Take-out tables in [pipe fitting take-outs](/article/pipe-miter-layout).
- **P&ID (piping and instrumentation diagram)**: schematic, no dimensions; every line, valve and instrument tagged. Instrument bubbles use **ISA 5.1** letters: first letter = variable (**P** pressure, **T** temperature, **F** flow, **L** level, **V** vibration, **S** speed, **Z** position), following letters = function (**I** indicator, **T** transmitter, **C** controller, **S** switch, **A** alarm, **E** element, **V** valve; **H/L** high/low). `PIT-101` = pressure indicating transmitter, loop 101; `TSH-203` = temperature switch high; `PSV` pressure safety valve; `FE` orifice plate. A line through the bubble = board-mounted, none = field-mounted, dashed = behind the panel. Line types: solid = process, dashed = electrical signal, `-o-o-` pneumatic signal, `---//---` software link. Use the P&ID to find isolation valves and drains **before** you open anything.

## Reading a drawing: a checklist

1. Title block: number, rev, units, scale, material, standard, notes.
2. Find the front view and work out the projection; identify every hidden and centre line.
3. Locate the datums and the largest features; then the detail.
4. List every dimension you need with its tolerance (block or stated) and every finish.
5. Note every weld symbol, hole callout and thread.
6. Check the BOM quantity and material against what is in the shop.
7. Question anything that does not add up (overall vs sum of parts, a hole that appears in one view only) **before** cutting.

## Related

- [Welding symbols](/article/welding-symbols)
- [Bearing fits and tolerances](/article/bearing-clearance-and-fits-tables)
- [Dial indicator basics](/article/dial-indicator-use)
- [Pipe miter layout and take-outs](/article/pipe-miter-layout)
- [Layout tools and scribing](/article/layout-tools-and-scribing)
