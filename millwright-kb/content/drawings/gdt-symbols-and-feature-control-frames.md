---
title: "GD&T Symbols and Feature Control Frames: Why Geometric Tolerancing Exists, Reading the Frame Compartments, Datums and Datum Targets, the Fourteen Characteristics (Form, Orientation, Location, Profile, Runout) per ASME Y14.5-2018, MMC, LMC, RFS and Bonus Tolerance, Picturing the Tolerance Zones, a Worked Bearing Housing Example, and Checking Flatness, Perpendicularity, Position and Runout on the Shop Floor with Indicators, Surface Plate and CMM"
slug: gdt-symbols-and-feature-control-frames
category: drawings
kind: chart
tags: [GD&T, geometric dimensioning and tolerancing, ASME Y14.5, Y14.5-2018, ISO 1101, feature control frame, datum, datum feature symbol, datum target, datum reference frame, flatness, straightness, circularity, roundness, cylindricity, parallelism, perpendicularity, squareness, angularity, position tolerance, true position, bolt pattern position, profile of a surface, profile of a line, circular runout, total runout, concentricity, symmetry, MMC, maximum material condition, LMC, RFS, bonus tolerance, projected tolerance zone, tolerance zone, basic dimension, bearing housing tolerance, runout check, flatness check, V-blocks, CMM, geometric tolerance inspection]
source: "ASME Y14.5-2018 (dimensioning and tolerancing), ASME Y14.5.1 (mathematical definition of dimensioning and tolerancing principles), ASME Y14.43 (dimensioning and tolerancing principles for gages and fixtures); ISO 1101 (geometrical tolerancing), ISO 5459 (datums), ISO 2692 (maximum material requirement), ISO 8015 (fundamental tolerancing principles); Machinery's Handbook GD&T chapter; Alex Krulikowski, Fundamentals of GD&T; SKF and Timken bearing housing and shaft geometric tolerance recommendations."
summary: "A chart-style reference to geometric dimensioning and tolerancing as it appears on the shafts, housings, baseplates and bolt patterns a millwright fabricates, checks and installs: what the feature control frame compartments mean, how datums set the order of measurement, each of the fourteen characteristics described in words with its zone and typical use, material condition modifiers and the bonus tolerance they give, a worked bearing housing with position and total runout, and how each control is actually checked with a dial indicator, surface plate, V-blocks or a CMM."
---

Plus-minus tolerances describe size. They cannot say whether a face is flat, a bore is square to a face, or a hole pattern is in the right place as a group; geometric dimensioning and tolerancing (GD&T) does that with a small set of symbols. The [overview article](/article/blueprint-reading-for-millwrights) lists them; this one explains how to read a frame and how to check the part.

## Why GD&T exists

Take four 1/2 in bolt holes located plus or minus .005 in: each centre may lie anywhere in a .010 in square. But the bolt fits as long as the centre is within a **circle** through that square's corners, which has 57 percent more area, so the plus-minus scheme rejects good holes; and it says nothing about which face the holes are measured from.

![Square plus-minus tolerance zone versus the round position zone](/img/drawings/gdt-why.svg)

*Square plus-minus tolerance zone versus the round position zone*

GD&T states three things plus-minus cannot: **which surfaces are the reference** (datums) and in what order; **the shape of the tolerance zone** (a cylinder for a hole axis, two parallel planes for a face, a band for a profile); and **how the tolerance interacts with size**, so a hole bigger than minimum is allowed more position error because the bolt still fits. A frame tells you what to indicate, from what, and how much error is allowed. The US standard is ASME Y14.5-2018; Canadian drawings follow it or ISO 1101.

## The feature control frame

The frame is a rectangle read left to right:

![Feature control frame anatomy read left to right](/img/drawings/feature-control-frame-anatomy.svg)

*Feature control frame anatomy read left to right*

```
   | symbol | Ø  tolerance  (M) | A | B (M) | C |
```

| Compartment | Holds | Notes |
|---|---|---|
| 1 | The **geometric characteristic symbol** | Which of the fourteen controls applies |
| 2 | The **tolerance**, with a **diameter symbol** before it if the zone is a cylinder and a **material condition modifier** after it | No diameter symbol means two parallel planes that far apart; inch .010, metric 0.25 |
| 3 to 5 | **Datum references**: primary, secondary, tertiary, each with an optional modifier | The order is the order the part is fixtured and measured; form tolerances have no datums |

Also found in a frame: a **projected tolerance zone** (circled P with a height) for tapped holes, where the tolerance applies to the bolt standing above the surface, and modifiers such as free state (circled F), tangent plane (circled T) and unequally disposed profile (circled U). A frame on a leader or extension line controls a surface; a frame hung under a size dimension controls that feature's axis or centre plane.

## Datums

A **datum** is a theoretically perfect plane, axis or point established from a real, imperfect surface, the **datum feature**, which is what you set up on.

![Datum feature symbol, datum target and the 3-2-1 datum frame](/img/drawings/datum-symbols.svg)

*Datum feature symbol, datum target and the 3-2-1 datum frame*

- **Datum feature symbol**: a letter in a square, tied to a triangle on the surface, on an extension line, or on a size dimension (then the datum is that feature's axis). Letters skip I, O and Q.
- **Primary datum** (first in the frame): on a machine base, the mounting face, established by three points of contact; the **secondary** by two points while the primary stays in full contact; the **tertiary** by one. That 3-2-1 rule is why the order matters: hold the part on B first and you get a different answer.
- **Datum targets** (a split circle with the target number and size) say where to touch a rough casting or weldment; a fabricated base shows A1, A2, A3 on the underside pads.
- A **compound datum** A-B is two bearing journals that together make one axis, with every other diameter toleranced with runout to A-B; at the bench it is V-blocks or centres on those two journals.

## The fourteen characteristics

![The fourteen geometric characteristic symbols grouped by type](/img/drawings/gdt-symbol-sheet.svg)

*The fourteen geometric characteristic symbols grouped by type*

| Group | Characteristic | Symbol | Datums | Zone | Millwright relevance |
|---|---|---|---|---|---|
| **Form** | Flatness | A parallelogram | None | Two parallel planes | Baseplate and sole plate pads, gasket and seal faces |
| Form | Straightness | A short horizontal line | None | Two parallel lines, or a cylinder for an axis | Long shafts, guide rails, conveyor stringers |
| Form | Circularity (roundness) | A circle | None | Two concentric circles at each section | Bearing seats, seal sleeves; does not control taper |
| Form | Cylindricity | A circle between two slanted lines | None | Two coaxial cylinders | Hydraulic rods and bores (roundness, straightness and taper together) |
| **Orientation** | Perpendicularity | An inverted T | Yes | Two planes or a cylinder square to the datum | Pump feet to shaft axis, housing face to bore |
| Orientation | Parallelism | Two slanted parallel lines | Yes | Two planes or a cylinder parallel to the datum | Base pads, two gearbox bores |
| Orientation | Angularity | A line at an angle from a base line | Yes | Planes or a cylinder at the basic angle | Angled bosses, dovetails |
| **Location** | Position | A circle with a cross through it | Usually three | A cylinder (holes) or two planes (slots) centred on the basic location | Bolt patterns, dowel holes, bores to mounting faces; the commonest control |
| Location | Concentricity | Two concentric circles | One | A cylinder about the datum axis | **Removed in Y14.5-2018**; use runout or position |
| Location | Symmetry | Three horizontal lines | One | Two planes about the datum centre plane | **Removed in 2018**; use position |
| **Profile** | Profile of a surface | A closed half circle | Optional | A band each side of the true profile | Castings, contours; the all-purpose 3D tolerance |
| Profile | Profile of a line | An open half circle | Optional | The same at each cross-section | Extrusions, cam profiles |
| **Runout** | Circular runout | One angled arrow | Always | Full indicator movement in one revolution | Coupling faces and rims, seal surfaces |
| Runout | Total runout | Two angled arrows with a line under them | Always | Full indicator movement across the whole surface | Shaft bearing seats, rotor faces, housing shoulders |

In 2018, position on a surface of revolution replaces concentricity and position on a slot replaces symmetry.

## Material condition modifiers and bonus tolerance

A size feature has a **maximum material condition (MMC)**, the smallest hole or largest pin, and a **least material condition (LMC)**. **Regardless of feature size (RFS)** is the default when no modifier is shown.

![Bonus tolerance: the position zone grows as the hole grows from MMC](/img/drawings/bonus-tolerance.svg)

*Bonus tolerance: the position zone grows as the hole grows from MMC*

| Modifier | Symbol | Meaning | Used for |
|---|---|---|---|
| MMC | Circled M | The tolerance applies at MMC; as the feature departs toward LMC the difference is added as **bonus tolerance** | Clearance holes: fit and assembly |
| LMC | Circled L | Applies at LMC; bonus as the feature grows toward MMC | Minimum wall, edge distance |
| RFS | No symbol (circled S on old prints) | Fixed tolerance | Press fits, bearing bores |

Worked example. A hole `Ø.531 +.010 / -.000` has position `Ø.010 (M) A B C`. The hole measures .537, a departure of .006 from MMC, so the allowed zone is Ø.010 + .006 = **Ø.016 in**; at the largest hole (.541) it is Ø.020. A modifier on a **datum** reference (B at MMC) lets the datum feature shift within its own clearance: a little rock on B is allowed. Bonus never applies to form tolerances, to runout, or to any RFS frame.

ASME Rule 1 (the **envelope rule**) says a size feature at MMC must be perfectly formed; ISO 8015 defaults to **independence**, size and form separate unless the circled E is added.

## Tolerance zones you can picture

![Flatness, perpendicularity, position and runout zones illustrated](/img/drawings/tolerance-zones.svg)

*Flatness, perpendicularity, position and runout zones illustrated*

| Frame | Zone to picture | How to think about it |
|---|---|---|
| Flatness .002 | Two planes .002 apart at any angle; the surface fits between | A straightedge and a .002 feeler that will not enter anywhere; or an indicator sweep on a surface plate |
| Perpendicularity Ø.005 to A (under a bore) | A cylinder Ø.005, square to A, the bore axis inside it | A close pin in the bore, indicator run along the pin |
| Position Ø.014 (M) A B C | A cylinder Ø.014 plus bonus on the basic location, square to A | Hole centre measured from B and C with the part on A; error = 2 x the square root of (X error squared + Y error squared) |
| Circular runout .002 to A-B | At each section, a ring .002 wide about the A-B axis | On V-blocks or centres on the two journals, one turn: full indicator movement |
| Total runout .003 to A-B | A cylinder .003 thick about A-B along the whole length | Same, with the indicator traversing; largest reading minus smallest |

## Worked example: a bearing housing

A replacement pillow-block housing for a Ø90 mm (3.543 in) bearing outer ring carries:

![A bearing housing with datums, position, perpendicularity and runout callouts](/img/drawings/gdt-housing-example.svg)

*A bearing housing with datums, position, perpendicularity and runout callouts*

- **Datum A**, the mounting face: **flatness 0.02 mm** (.0008 in).
- **Datum B**, the bore `Ø90 H7` (90.000-90.035 mm): **perpendicularity Ø0.03 mm to A** under the diameter.
- **Datum C**, one machined end face; four mounting slots with **position 0.5 (M) A B C**, basic 300 mm between centres and 60 mm from C.
- The shoulder inside the bore: **total runout 0.03 mm to B**.

Reading it as a job:

1. **Flatness of A** decides whether the housing sits without rocking: an indicator sweep on the surface plate, 0.02 mm total, or a straightedge and a 0.02 mm (.001 in) feeler.
2. **Bore size** is a bore gauge check; RFS, so no bonus.
3. **Perpendicularity of the bore to A**: housing on A, a close mandrel through the bore, indicate along the mandrel. Ø0.03 over a 60 mm bore is 0.0005 mm per mm, so over a 300 mm mandrel the allowed difference is 0.15 mm (.006 in).
4. **Position of the slots** at MMC: measure slot centres from C and the bore axis, with bonus for a slot wider than minimum. A 0.5 mm zone on 14 mm slots for M12 bolts is lenient.
5. **Total runout of the shoulder to B**: mandrel in the bore held in V-blocks, rotate the housing, indicator on the shoulder traversed radially, 0.03 mm total. A shoulder out of square skews the outer ring.

If the housing fails 1 or 3, the shaft is forced out of alignment when the caps are torqued; if it fails 4, you file the slots. Shaft controls are in [bearing fits and clearance tables](/article/bearing-clearance-and-fits-tables).

## Measuring against GD&T on the shop floor

![A coordinate measuring machine checks GD&T callouts that a bench cannot](/photos/drawings/cmm-inspection.jpg)

*A coordinate measuring machine checks GD&T callouts that a bench cannot. Photo: AB Technology (Newark) Ltd., CC BY-SA 4.0, via commons*

| Control | Tool | Setup and reading |
|---|---|---|
| Flatness | Surface plate and indicator on a stand; straightedge and feelers; a precision level on a large base | Part levelled on three spots, sweep the rest. See [surface plate, height gauge and squares](/article/surface-plate-height-gauge-and-squares) |
| Perpendicularity of a face | Cylinder square or precision square with feelers | Part on the datum, square against the face |
| Perpendicularity or parallelism of a bore or face | Mandrel, surface plate, indicator on a height stand | Indicate along the mandrel or across the face, both directions |
| Position of holes | Gauge pins, height gauge on the plate; a CMM for many holes | Each pin centre from the datums in X and Y, converted to a diameter; technique in [dial indicator use](/article/dial-indicator-use) |
| Circular and total runout | V-blocks or centres on the datum journals, dial indicator on a magnetic base | Full indicator movement (FIM, TIR); circular at several positions, total while traversing |

A **CMM** does all of this from a probed datum setup; ask the vendor for the CMM report on a critical housing. Deburr the datum feature (a burr under A tips the whole setup) and put the V-blocks on the journals the frame names.

**ISO 1101 differences.** The symbols are the same; ISO keeps concentricity and symmetry, defaults to independence, handles material condition through ISO 2692, and adds modifiers such as CZ (common zone). Canadian drawings under CSA B78.2 follow ASME Y14.5 in practice.

## Common mistakes

- Ignoring the datum order and measuring from whichever surface is handy.
- Reading a position tolerance as plus-minus per axis instead of a diameter zone.
- Forgetting the bonus on an MMC frame, or applying bonus to an RFS one.
- Treating runout as a size check: a round shaft with an eccentric seat has runout and passes a micrometer.
- Measuring a concentricity symbol on a 2018 drawing as runout without asking; it should not be there.
- Assuming flat means parallel: a base can be flat and still not parallel to its top pads.
- Applying the envelope rule to an ISO drawing, or independence to an ASME one.

## Related

- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [Mechanical drawings: views, sections and dimensions](/article/mechanical-drawings-views-sections-and-dimensions)
- [Reading engineering drawings: sheets, title blocks and revisions](/article/reading-engineering-drawings-basics)
- [Dial indicator use](/article/dial-indicator-use)
- [Surface plate, height gauge and squares](/article/surface-plate-height-gauge-and-squares)
- [Bearing fits and clearance tables](/article/bearing-clearance-and-fits-tables)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
- [Structural and machine installation drawings](/article/structural-and-machine-installation-drawings)
