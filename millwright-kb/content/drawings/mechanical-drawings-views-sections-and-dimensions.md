---
title: "Mechanical Drawings: Third and First Angle Projection, Every Line Type, Full, Half, Offset, Revolved, Broken-Out, Removed and Aligned Sections with Hatch Patterns, Auxiliary and Detail Views, Dimensioning Rules and Hole Symbols, Limit and Plus-Minus Tolerances, ISO 286 Fits (H7/g6 to H7/s6 and N7) with Inch Equivalents, Thread Callouts, Surface Finish Symbols, Assembly Drawings and Parts Lists, and Weldment Drawings"
slug: mechanical-drawings-views-sections-and-dimensions
category: drawings
kind: reference
tags: [mechanical drawing, orthographic projection, third angle projection, first angle projection, projection symbol, alphabet of lines, hidden line, centre line, phantom line, cutting plane line, section view, full section, half section, offset section, revolved section, broken-out section, removed section, aligned section, hatching, auxiliary view, detail view, dimensioning, chain dimensioning, baseline dimensioning, reference dimension, basic dimension, counterbore symbol, countersink symbol, limit dimension, block tolerance, ISO 286, ISO 2768, fits, H7 g6, H7 k6, H7 p6, N7 housing, press fit, thread callout, UNC, metric thread, NPT, surface finish symbol, Ra roughness, weldment drawing]
source: "ASME Y14.3 (orthographic and pictorial views), ASME Y14.2 (line conventions), ASME Y14.5-2018 (dimensioning and tolerancing), ASME Y14.36 (surface texture symbols), ASME Y14.100 (engineering drawing practices), ASME B1.1 and B1.13M (unified and metric screw threads), ASME B1.20.1 (pipe threads), ASME B46.1 (surface texture); ISO 128 (presentation), ISO 286-1 and 286-2 (limits and fits), ISO 2768-1 and 2768-2 (general tolerances), ISO 1302 (surface texture indication); Machinery's Handbook fit and thread tables; AWS A2.4 welding symbols."
summary: "The picture part of a mechanical drawing, read at the bench: how the views sit on the sheet under third and first angle projection, what every line style means, how each kind of section is cut and hatched, when a drafter uses auxiliary and detail views, the rules of dimensioning and the hole and thread symbols, how tolerances are stated and what the common ISO fits mean when a shaft goes into a bore, surface finish symbols and the values that matter on seals and bearing seats, and how assembly and weldment drawings are put together."
---

A detail drawing is a set of agreed conventions, and once you know them you can read a part the drafter never met you to explain. This article takes the [blueprint reading overview](/article/blueprint-reading-for-millwrights) deeper; the paperwork side is in [reading engineering drawings](/article/reading-engineering-drawings-basics).

## Views and projection angle

An orthographic drawing shows the object in flat views at 90 degrees to each other. Where each view sits depends on the **projection angle**, and getting it wrong flips left for right on every part you make.

![Third-angle and first-angle projection symbols and view placement](/img/drawings/projection-angle-symbols.svg)

*Third-angle and first-angle projection symbols and view placement*

| | Third angle (ASME, US and Canada) | First angle (ISO, Europe, much of Asia) |
|---|---|---|
| Top view | Above the front view | Below the front view |
| Right side view | Right of the front view | Left of the front view |
| Symbol | A truncated cone (trapezoid) beside its end view (two concentric circles); the circles sit on the side the **small end points to** | Same shapes, but the circles sit on the **wide-end side** |

The symbol lives beside the title block; if it is missing, find a feature visibly on one side in the front view and check which side view shows it. Expect first angle from European machine builders; Canadian Red Seal training covers both. **Isometric** views are never dimensioned from.

## The alphabet of lines

ASME Y14.2 uses two weights, **thick** (about 0.024 in, 0.6 mm) and **thin** (0.012 in, 0.3 mm). On a reduced print the weights blur; the pattern still tells you what the line is.

![The alphabet of lines: visible, hidden, centre, dimension, section, break and phantom](/img/drawings/line-types-sheet.svg)

*The alphabet of lines: visible, hidden, centre, dimension, section, break and phantom*

| Line | Weight and pattern | Means |
|---|---|---|
| Visible | Thick, continuous | Edges you can see |
| Hidden | Thin, short dashes | Edges behind the surface, hole bottoms |
| Centre | Thin, long-short | Axis of a round feature, symmetry, bolt circles |
| Dimension | Thin, arrowheads each end, broken for the number (ASME) or number above (ISO) | The size or location |
| Extension | Thin, small gap from the object | Carries the measured point out |
| Leader | Thin, arrowhead on an edge or a dot on a surface | Links a note, symbol or balloon to its feature |
| Cutting plane | Thick, long-short-short or thick dashes, 90 degree arrows and letters | Where a section is cut and which way you look |
| Viewing plane | As cutting plane, no cut | A partial view from that direction |
| Section (hatch) | Thin, 45 degree, evenly spaced | Material cut by the plane |
| Break | Thick freehand (short); thin with zigzags (long) | The part is shortened; the dimension across the break is real |
| Phantom | Thin, long-short-short | Alternate positions, adjacent parts, repeated detail |
| Stitch | Thin dots | Stitching; intermittent welds on old prints |

## Sections and hatching

A section removes the material in front of a plane so the inside can be seen. The cutting-plane arrows point in the direction of sight; the section carries the same letters (SECTION A-A).

![Full, half, offset, revolved and broken-out sections with their cutting planes](/img/drawings/section-types.svg)

*Full, half, offset, revolved and broken-out sections with their cutting planes*

| Section | How it is cut | Where you see it |
|---|---|---|
| **Full** | One plane straight through | Housings, valves, cylinders |
| **Half** | Cut to the centreline; one half sectioned, the other shown outside | Pulleys, pistons, glands |
| **Offset** | The plane steps at 90 degrees through features not in one line | A cover with scattered holes |
| **Revolved** | The cross-section rotated 90 degrees and drawn on the view at the cut | Spokes, ribs, structural members |
| **Removed** | As revolved but drawn elsewhere, often enlarged | Shaft keyways, splines |
| **Broken-out** | A small area broken away with a freehand line | One bore or keyway on an external view |
| **Aligned** | An angled rib or hole is swung into the plane to show true distance | Flanges with odd bolt counts |

**Hatching** is thin 45 degree lines, at different angles for adjacent parts. The plain hatch means any material; older patterns still appear: pairs and singles for steel, dashed-and-solid for bronze, double lines for aluminium, wavy for rubber, dots and triangles for concrete. **Shafts, bolts, nuts, keys, pins, ribs, webs and spokes are not hatched** even when the plane passes through them; gaskets are shown solid black.

## Auxiliary and detail views

A face that slants to the principal planes is foreshortened in every regular view. An **auxiliary view** is projected perpendicular to that face so it appears at true size; dimension the slanted face from it, never from the foreshortened view.

![An 1867 machine drawing: views, sections and details laid out the way they still are](/photos/drawings/machine-drawing-1867.jpg)

*An 1867 machine drawing: views, sections and details laid out the way they still are. Photo: Griffin, Charles Lewis, 1867-; Adams, Charles Clyde, 1882- joint author, No restrictions, via commons*

A **detail view** enlarges a small area: a circle on the main view labelled with a letter, and the enlargement elsewhere labelled DETAIL A, SCALE 4:1. The detail's scale overrides the sheet scale, and a feature you cannot find dimensioned is probably in a detail.

## Dimensions and how to read them

![A plate dimensioned from a datum corner with hole, thread, radius and chamfer callouts](/img/drawings/dimensioning-example.svg)

*A plate dimensioned from a datum corner with hole, thread, radius and chamfer callouts*

- **Placement.** ASME uses **unidirectional** dimensions (all read horizontally); ISO and older drawings use **aligned** (read along the dimension line).
- **Decimals.** An inch dimension carries as many decimals as its tolerance, so `2.50` and `2.500` are different statements; metric omits trailing zeros (`63.5`).
- **Chain dimensioning** runs feature to feature and the tolerances add up: five holes at plus or minus .005 in can end .025 in out. **Baseline** dimensioning runs everything from one edge and does not accumulate. Measure the way the drawing dimensions.
- **Reference dimension** in parentheses `(4.000)`: for information, not inspected.
- **Basic dimension** in a box: theoretically exact, toleranced by a geometric control (see [GD&T](/article/gdt-symbols-and-feature-control-frames)).

| Symbol | Reads | Example |
|---|---|---|
| Ø, R, SR | Diameter, radius, spherical radius | `Ø1.250`, `R.125`, `SR2.00` |
| Counterbore (open-topped rectangle) then Ø, then depth | Counterbore diameter and depth | counterbore Ø.875, depth .375 |
| Countersink (a V) then Ø and an angle | Countersink diameter at the surface and included angle | countersink Ø.750 x 82° |
| Depth (a down arrow with a bar) | Depth of a hole, thread or counterbore | depth .75 |

Depth is measured to the full diameter, not the drill point.

## Tolerances, limits and fits

![Fit callout decoder: Ø50 H7/g6, its limits and the fit families](/img/drawings/fit-callout-decoder.svg)

*Fit callout decoder: Ø50 H7/g6, its limits and the fit families*

| Form | Example | Meaning |
|---|---|---|
| Limit | `1.502` over `1.500` | The two limits, larger on top |
| Plus-minus | `1.501 ± .001`; `1.500 +.002 / -.001`; `1.500 +.002 / -.000` | Equal, unequal, unilateral |
| Block | `.XX ± .01`, `.XXX ± .005`, angles ± 30', fractions ± 1/32 | Where no tolerance is shown, by decimal places |
| ISO general | ISO 2768-mK | m = medium linear (± 0.3 mm from 30 to 120 mm), K = geometric class |

ISO 286 (ANSI B4.2 uses the same tables) writes a **hole** class with a capital letter (H: lower limit at nominal) and a **shaft** class in lower case, each with an IT grade (6 and 7 ordinary machining, 5 grinding); the **hole basis** system varies the shaft because reamers are fixed sizes. The fits a millwright meets, for Ø50 mm (about 2 in):

| Fit | Type | Ø50 limits and result | At the bench |
|---|---|---|---|
| **H7/g6** | Close running (sliding) | Hole +0/+0.025, shaft -0.009/-0.025; clearance 0.009-0.050 mm (.0004-.0020 in) | Slides by hand, no shake: spigots, guide bushings, wear rings |
| **H7/h6** | Locational clearance | Shaft 0/-0.016; clearance 0-0.041 mm (0-.0016 in) | Hand push, may stick at zero: pilots, light-duty keyed hubs |
| **H7/k6** | Locational transition | Shaft +0.018/+0.002; -0.023 to +0.018 mm | Light push to light press: ball bearing inner rings, keyed gears |
| **H7/p6** | Locational interference | Shaft +0.042/+0.026; interference 0.001-0.042 mm (to .0017 in) | Press or heat: bushings in housings, dowel pins |
| **H7/s6** | Medium drive (heavy press) | Shaft +0.059/+0.043; interference 0.018-0.059 mm (.0007-.0023 in) | Hydraulic press or shrink, permanent: coupling hubs, gear rims |
| **N7 housing** | Light interference on a bearing OD | Ø90 housing -0.010/-0.045; 0.005 mm clearance to 0.045 mm interference on an OD toleranced 0/-0.015 | Outer ring pressed or heated in, where the outer ring rotates relative to the load; fixed housings are H7 or J7 |

Inch rule of thumb: a press fit is about .001 in per inch of diameter. Bearing seats use the maker's table in [bearing fits and clearances](/article/bearing-clearance-and-fits-tables); whatever a fit is called, the limits on the drawing are what the [micrometer](/article/reading-a-micrometer) and bore gauge decide against.

## Threads and fasteners on drawings

Threads are never drawn to shape: an internal thread is a drilled circle with a thin outer circle in the end view; an external thread shows the major diameter as an object line and the minor as a thin line. The callout carries everything.

![Thread callouts decoded and how threads are drawn](/img/drawings/thread-callout.svg)

*Thread callouts decoded and how threads are drawn*

| Callout | Reads |
|---|---|
| `1/2-13 UNC-2A`, depth `.75` | 1/2 in nominal, 13 TPI, Unified Coarse, class 2 (1 loose, 3 close), A external (B internal); full thread .75 in deep, the drill goes deeper |
| `M12 x 1.75 - 6g` | Metric, 12 mm, 1.75 mm pitch (coarse, may be omitted), class 6g external; 6H internal; 6g/6H is the standard fit |
| `... LH` | Left hand; everything else is right hand |
| `1/2-14 NPT` | Tapered pipe thread, 1/2 in nominal pipe size, 14 TPI; NPTF dryseal, NPSM straight |

Fastener notes give grade and finish: `HHCS 1/2-13 X 2 GR 5 ZN`, `SHCS M12 X 40 CL 12.9`, `A325 3/4 X 2-1/2`. A torque on the drawing overrides the [generic chart](/article/bolt-torque-chart-sae-metric); identifying an unknown thread is in [thread identification](/article/thread-identification-and-gauges).

## Surface finish symbols

The surface texture symbol (ASME Y14.36, ISO 1302) is a check mark with its long leg on the right. A **bare check** allows any process; a **bar across the top** means machining required; a **circle in the vee** prohibits material removal (as cast); the **number** beside it is **Ra**, in **microinches on inch drawings and micrometres on metric**; a **machining allowance** in mm may sit left of the vee (ISO); a **lay symbol** under the bar gives the tool-mark direction (`=` parallel, a perpendicular mark, `X` crossed, `M` multidirectional, `C` circular, `R` radial). Shafts under lip seals want no spiral lead, so they carry C or a "no lead" note.

![Surface finish symbol anatomy and common Ra values by process](/img/drawings/surface-finish-symbol.svg)

*Surface finish symbol anatomy and common Ra values by process*

| Ra μin | Ra μm | Process | Where it matters |
|---|---|---|---|
| **125** | **3.2** | Ordinary milling and turning | General machined faces, bolted joints, keyways |
| **63** | **1.6** | Fine turning, boring | Bearing housing bores, baseplate pads, gasket faces, pump feet |
| **32** | **0.8** | Finish turning, grinding | Bearing seats on shafts, coupling bores, flange raised faces (125-250 μin serrated under ASME B16.5) |
| **16** | **0.4** | Grinding, honing | Lip seal surfaces (10-20 μin, plunge ground), cylinder rods and bores, seal sleeves |

ISO drawings may state `Rz` (peak to valley), roughly four to seven times Ra; never read one as the other.

## Assembly drawings, balloons and parts lists

An assembly drawing shows the parts in working position with enough views (often one section) to show how they fit, and few size dimensions. It adds **balloons** (circles with the item or find number), the **parts list** (item, quantity, part or drawing number, description, material), **assembly dimensions** (overall size, mounting dimensions, shaft height, coupling gap) and **assembly notes** such as "MATCH DRILL ITEMS 3 AND 7 AT ASSY" or "SHIM ITEM 9 FOR .010-.015 END FLOAT". A sub-assembly is one item pointing to its own drawing; **exploded views** in manuals show the order of disassembly, and their item numbers match the spare-parts list.

![Assembly drawing with balloons and the parts list they point to](/img/drawings/assembly-balloons-parts-list.svg)

*Assembly drawing with balloons and the parts list they point to*

## Weldment drawings

A **weldment** is several pieces welded together and treated as one part, often machined afterwards. The drawing gives a cut list per piece and **welding symbols** on the joints; the full reading is in [welding symbols](/article/welding-symbols), and the general note sets the default where a joint has no symbol.

**Machined-after-welding** surfaces carry the finish symbol and a note ("MACHINE AFTER WELDING AND STRESS RELIEF, FLAT WITHIN .005"). They are dimensioned from the finished surface, so the fabricator leaves stock (often 1/8 in, 3 mm per face); the order is weld, stress relieve, then machine, because machining first loses the flatness. Datums sit on the machined pads so the GD&T frames can be checked. Larger jobs use a separate machining drawing; never machine to the weldment drawing. When a weldment arrives, check pad flatness and bore positions before it is set.

## Common mistakes

- Reading a first-angle drawing as third angle and mirroring the part.
- Measuring a foreshortened face in a principal view instead of the auxiliary view.
- Adding chain dimensions without adding their tolerances.
- Assuming a fit from its name instead of the limits on the drawing.
- Ordering a spare by balloon number instead of part number.
- Machining a weldment before stress relief, or to the weldment drawing instead of the machining drawing.

## Related

- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [Reading engineering drawings: sheets, title blocks and revisions](/article/reading-engineering-drawings-basics)
- [GD&T symbols and feature control frames](/article/gdt-symbols-and-feature-control-frames)
- [Bearing fits and clearance tables](/article/bearing-clearance-and-fits-tables)
- [Thread identification and gauges](/article/thread-identification-and-gauges)
- [Welding symbols](/article/welding-symbols)
- [Reading a micrometer](/article/reading-a-micrometer)
- [Structural and machine installation drawings](/article/structural-and-machine-installation-drawings)
