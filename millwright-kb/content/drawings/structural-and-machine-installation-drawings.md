---
title: "Structural and Machine Installation Drawings: the Installation Drawing Set (GA, Plot Plan, Equipment Layout, Foundation, Anchor Bolt, Structural, Platforms), Column Lines, Grids and Plant Coordinates, Elevations, Datums and Benchmarks (TOS, TOC, TOG, BOP, FFL), Reading a General Arrangement, Anchor-Bolt Plans and Foundation Details, Base Plates, Sole Plates and Grout Details, W-Shape and Connection Callouts, Conveyor and Drive Arrangement Drawings, and the Sequence for Setting a Machine from the Drawing with API 686 Tolerances"
slug: structural-and-machine-installation-drawings
category: drawings
kind: reference
tags: [installation drawing, general arrangement, GA drawing, plot plan, equipment layout, foundation drawing, anchor bolt plan, structural drawing, platform drawing, column lines, grid lines, plant north, plant coordinates, northing easting, elevation, TOS, top of steel, TOC, top of concrete, TOG, top of grout, BOP, FFL, benchmark, equipment tag, maintenance clearance, pull space, anchor bolt projection, anchor bolt sleeve, anchor bolt template, embed depth, edge distance, pedestal, rebar callout, grout pocket, leveling screw, base plate, sole plate, W shape callout, connection detail, A325 bolts, pretensioned, conveyor arrangement, take-up travel, API 686]
source: "API RP 686 (recommended practice for machinery installation and installation design), ASME Y14.100 and Y14.1 drawing practices; AISC Steel Construction Manual and AISC 303 Code of Standard Practice (member designations, erection tolerances), RCSC Specification for Structural Joints Using High-Strength Bolts (snug-tight and pretensioned joints), AWS D1.1 and A2.4 (welding symbols); ACI 318 Chapter 17 (anchoring to concrete) and ACI 351.3R (foundations for dynamic equipment); PIP STE05121 and PIP REIE686 (anchor bolt design and machinery installation practices); CEMA Belt Conveyors for Bulk Materials; manufacturer installation drawings and manuals (pumps, gearboxes, compressors, conveyors)."
summary: "How to read the drawings that put a machine on its foundation: which sheets make up an installation set, how column lines, plant north and plant coordinates locate anything on site, how elevations and benchmarks are given and transferred, what a general arrangement tells you about tags, centrelines and clearances, how to read anchor-bolt plans and foundation details, base plate, sole plate and grout details, structural member and connection callouts, conveyor and drive arrangement drawings, and the order in which you set equipment from the drawing with API 686 tolerances as the starting numbers."
---

A detail drawing tells you how to make a part; an installation set tells you where it goes, at what height, on what, and bolted to what. The millwright reads these more than any other drawing, and the first thing poured in concrete is the last thing that can be changed cheaply. This article covers the sheets the [blueprint reading overview](/article/blueprint-reading-for-millwrights) only lists.

## The installation drawing set

![A foundation drawing: the plan the concrete crew and the millwright both work from](/photos/drawings/foundation-drawing.jpg)

*A foundation drawing: the plan the concrete crew and the millwright both work from. Photo: Unknown authorUnknown author or not provided, Public domain, via commons*

| Drawing | What it gives you |
|---|---|
| **Plot plan** | Plant footprint, the grid origin, plant north against true north |
| **Equipment layout** | Every tagged machine on the column grid, with centrelines and coordinates |
| **General arrangement (GA)** | One machine or train: overall dimensions, shaft centreline elevation, connections, clearances |
| **Foundation drawing** | The concrete: pedestals, elevations, rebar, embedments, grout pockets |
| **Anchor bolt plan** | Bolt pattern by coordinate and column line, size, projection, sleeves, template |
| **Platform, stair and ladder drawings** | Access, handrail, grating |
| **Structural framing plans and details** | Members with marks and sizes, TOS elevations, connections |
| **Vendor certified installation drawing** | Mounting hole pattern, base outline, shaft height, weight, lifting points, service clearances |
| **Piping GA and isometrics** | What will be in the way, and nozzle loads; see [piping drawings](/article/piping-drawings-isometrics-and-spool-sheets) |

The vendor certified print and the foundation drawing must agree on bolt pattern, projection and shaft centreline height; the foundation drawing usually notes "ANCHOR BOLTS PER VENDOR CERTIFIED DWG" and the vendor print governs. Canadian and ISO sets use millimetres with elevations in metres, and call the GA an **erection drawing**.

## Column lines, grids and coordinates

Plant drawings hang everything on a **grid** of column lines: letters one way (A, B, C, skipping I and O) and numbers the other, with bay spacing given (typically 20-30 ft, 6-9 m). A column is named by its intersection (B-4); a machine centreline is an offset ("C/L PUMP 3'-6" WEST OF LINE 5"). Intermediate lines get suffixes (4.5, 4A).

![Equipment located from column lines, never from a wall](/img/drawings/column-line-grid.svg)

*Equipment located from column lines, never from a wall*

**Plant north** is an arrow on every plan, rarely true north; the plot plan gives the rotation. Directions on plant drawings always mean plant north. Never set anything by a compass.

**Plant coordinates** locate points independent of the grid: **N** (northing) and **E** (easting) from an origin, usually a large fictitious number (N 10000.000, E 5000.000) so values are never negative. Layouts carry a **coordinate table** per tag with N, E and centreline elevation; you check with a tape from the nearest column line using the drawing's offsets. Coordinates in feet are decimal feet (10023.75 ft is 10023 ft 9 in). Real columns are within erection tolerance (AISC 303 allows about 1/500 out of plumb), so measure from the **nearest** grid line, not a column face.

## Elevations, datums and benchmarks

Heights are **elevations (EL)** above a plant datum: a **benchmark** (a brass plug, a punched bolt, a mark on a column) assigned a value on the plot plan, commonly EL 100'-0" or EL 100.000 m so every plant elevation is positive.

![Elevations read up from the plant datum: floor, concrete, grout, steel, shaft](/img/drawings/elevation-datums.svg)

*Elevations read up from the plant datum: floor, concrete, grout, steel, shaft*

| Abbreviation | Means |
|---|---|
| **TOS, T/S** | Top of steel |
| **TOC, T/C** | Top of concrete, before grout |
| **TOG** | Top of grout: where the base plate sits |
| **BOP** | Bottom of pipe (not bottom of plate) |
| **C/L PUMP, C/L SHAFT** | Shaft centreline elevation, the key number for rotating equipment |
| **FFL, FF** | Finished floor level |

The chain that matters: the vendor print gives shaft centreline 18.000 in (457 mm) above the base bottom; the GA gives shaft centreline EL 104'-6"; so TOG is EL 103'-0", and with 1-1/2 in (38 mm) of grout the pour is to TOC EL 102'-10 1/2". Write the chain on the drawing before the pour.

**Transferring a benchmark.** Carry the plant benchmark with an optical or laser level and close back on it (within 1/32 in; over 1/16 in, redo), then establish a **local benchmark** on a column beside the machine; method in [optical and laser levels and piano wire](/article/optical-and-laser-levels-piano-wire).

## General arrangement drawings

Read the GA end to end before touching the machine.

![General arrangement of a conveyor drive with tags, centrelines and balloons](/img/drawings/arrangement-drawing-extract.svg)

*General arrangement of a conveyor drive with tags, centrelines and balloons*

- **Equipment tags**: P-1201A (pump), M-1201A (motor), G-1201 (gearbox). The tag ties the GA to the P&ID, the coordinate table and the vendor print.
- **Centrelines**: shaft C/L in plan and elevation is the reference for everything; nozzle C/Ls; coupling C/L and gap.
- **Clearances**, in phantom or dimensioned: **maintenance pull space** (rotor removal, tube bundle pull, motor removal), cover swing, walkway width (22 in minimum clear under OSHA and CSA), guard envelope. No pull space is a drawing error to raise before the steel goes up.
- **Connections**: nozzle sizes and ratings (4 in 150# RF), flange face elevations, drains, vents, seal flush, conduit entry.
- **Base type**: a common baseplate (API 686 style, with grout and vent holes), separate sole plates, a skid, or a pedestal.
- **Notes**: grout type, anchor bolt supply ("A/B BY OTHERS"), shim allowance, alignment tolerance.

## Foundation and anchor-bolt drawings

**Anchor bolt plan.** Every bolt located from the grid or the equipment centrelines, with a schedule:

![Formwork and anchor bolts set before the pour: the plan becomes concrete](/photos/drawings/foundation-formwork.jpg)

*Formwork and anchor bolts set before the pour: the plan becomes concrete. Photo: No machine-readable author provided. Fg2 assumed (based on copyright claims)., Public domain, via commons*

![Anchor bolt plan and bolt detail with sleeve, embedment and projection](/img/drawings/anchor-bolt-plan.svg)

*Anchor bolt plan and bolt detail with sleeve, embedment and projection*

| Item | Typical entry | Check |
|---|---|---|
| Mark and pattern | AB-1, 8 bolts, 36.000 x 20.000 in centres (914 x 508 mm) | Against the vendor print |
| Size and material | 1 in x 24 in, ASTM F1554 Gr 36 (Gr 55, 105 high strength) | Thread length and nut count |
| Projection | 3 in (76 mm) above TOC or TOG; the drawing says which | Room for grout, plate, washer, nut and 2-3 threads; short projection is the commonest field problem |
| Embed depth | 18 in (457 mm) below TOC, per ACI 318 | Against the pedestal depth |
| Sleeves | 3 in pipe sleeve, top 1 in below TOC | Let the bolt bend to fit; packed before the pour, grouted after alignment (API 686) |
| Edge distance | 6 in (150 mm) minimum | Bolts near an edge spall the concrete |
| Template and tolerance | "SET WITH STEEL TEMPLATE, HOLD +/- 1/16 in (1.5 mm)" | Hold the template to the forms, not the rebar; structural bolts get about 1/8 in (AISC 303) |

**Foundation drawing** details show: **pedestals** with TOC, plan size and edge chamfers (3/4-1 in, 20-25 mm); **rebar callouts** (`#5 @ 12 in EW T&B` is number 5 bar at 12 in each way, top and bottom; `10M @ 300` Canadian metric), which tell you where you can core-drill; the **grout pocket** with the note "ROUGHEN TO 1/4 in AMPLITUDE"; **leveling screw pads** cast in under each jack screw; and mass notes for dynamic equipment (ACI 351.3R: about three times the machine mass for rotating machines). Before the pour: bolts to the template, projection and plumb, sleeves packed. After: bolt centres re-measured (bolts move in a pour), TOC surveyed. Details in [anchor bolts and foundations](/article/anchor-bolts-and-foundations).

## Base plates, sole plates and grout details

A **baseplate** carries the whole train on one frame; a **sole plate** is a machined plate grouted under each foot or machine. The drawing details:

![Base plate, jackscrews, anchor bolt sleeve and grout in section](/img/drawings/baseplate-detail.svg)

*Base plate, jackscrews, anchor bolt sleeve and grout in section*

- **Thickness**: 1-2 in (25-50 mm) sole plates; 1/2-3/4 in top plate on a fabricated base.
- **Holes vs slots**: round holes with 1/8-1/4 in clearance for anchor bolts; **slots** on motor feet and slide bases, dimensioned length x width, with a direction note.
- **Jack bolt pads**: tapped bosses with 5/8 or 3/4 in screws and steel pads on the concrete; or leveling wedges.
- **Machined mounting surfaces**: pads machined after stress relief; API 686 wants them flat within .002 in/ft (0.17 mm/m) and coplanar within .005 in (0.13 mm), stated as flatness and parallelism frames (see [GD&T](/article/gdt-symbols-and-feature-control-frames)).
- **Grout holes** (4 in minimum, one per compartment), **vent holes** (1/2 in at the corners) and grout thickness (1-2 in, 25-50 mm cementitious; 1-3 in epoxy), all in section.
- **Sole plate installation**: levelled on jack screws within .0005 in/ft (0.04 mm/m) under API 686, grouted, then the machine set on shims.

Grout procedure and cure are in [grouting baseplates](/article/grouting-baseplates); leveling method in [leveling and machine setting](/article/leveling-and-machine-setting).

## Structural details and connection callouts

Framing plans mark each member with a **piece mark** (B12) and its size.

![Beam designation, bolt and weld callouts, TOS and BOS](/img/drawings/structural-connection-callouts.svg)

*Beam designation, bolt and weld callouts, TOS and BOS*

| Callout | Reads |
|---|---|
| `W12x26` | Wide-flange, 12 in nominal depth, 26 lb/ft (metric W310x39: 310 mm deep, 39 kg/m) |
| `C10x15.3`, `L4x4x3/8`, `HSS8x6x1/4`, `PL 3/4 x 12`, `WT6x13`, `TOS EL 112'-6"` | Channel; angle; hollow section; plate; tee cut from a W12x26; top of steel elevation |
| `3/4 in A325-N, 4 ROWS` | A325 bolts, threads not excluded from the shear plane (X = excluded); A490 is the higher grade, always pretensioned, never re-used |
| `SNUG TIGHT` (ST) | Firm contact with a spud wrench or a few impacts; the default for bearing connections |
| `PT`, `SC` (slip critical) | Pretensioned to 70 percent of minimum tensile by turn-of-nut, calibrated wrench, TC bolts or DTI washers; slotted holes under a machine mean pretensioned |
| `1/4 in fillet, 3-12`; `CJP`; `FW` | Intermittent 3 in fillets on 12 in centres; complete joint penetration; field weld. See [welding symbols](/article/welding-symbols) |

Structural bolt pretension is by method, not torque; the [bolt torque chart](/article/bolt-torque-chart-sae-metric) is for machinery fasteners, not A325 joints.

## Conveyor and drive arrangement drawings

A conveyor set is a GA in long sections plus a drive arrangement:

- **Pulley centres** (head to tail, the basis of belt length), pulley diameters, lagging and crown; the **belt line** (top of the carrying belt at head, tail and each change of grade) and the **stringer line** (top of stringers, 2-4 in below it); idler spacing.
- **Take-up**: type (screw, gravity, winch), **take-up travel** (CEMA guidance is roughly 2-4 percent of centre distance for fabric belts, under 1 percent for steel cord), counterweight mass, and the **initial position** of the take-up pulley at the start of travel so there is room for stretch.
- **Drive arrangement**: motor, coupling, reducer, the **motor slide base** with its adjustment travel, sheave sizes and belt section, backstop, and **guard envelopes** in phantom.
- **Loads on the structure**: head shaft load and belt tensions; do not move a drive without going back to that number.

Set head and tail shaft centrelines to coordinate and elevation, square to the conveyor centreline (diagonals equal within 1/8 in, 3 mm), then idlers to the stringer and belt lines, then the drive; see [belt conveyor components and tracking](/article/belt-conveyor-components-and-tracking).

## Setting equipment from the drawing

The order is the same for a pump, a gearbox or a compressor. API 686 numbers are the starting point; the vendor manual and the project specification override them.

| Step | From the drawing | Tolerance to work to |
|---|---|---|
| 1. Verify the foundation | Survey TOC from the local benchmark; bolt centres to the vendor pattern, projection, plumb | Centres within 1/16 in (1.5 mm); TOC 1/4 in low is fine |
| 2. Prepare the surface | Chip laitance, roughen, blow clean | Exposed aggregate, no oil |
| 3. Set to elevation | Baseplate or sole plates on jack screws to TOG, anchor nuts loose | Within 1/8 in (3 mm) unless a fixed flange demands better |
| 4. Level | Precision level on every machined pad, both directions, machines removed | .0005 in/ft (0.04 mm/m); pads coplanar within .005 in (0.13 mm); see [leveling and machine setting](/article/leveling-and-machine-setting) |
| 5. Pre-align | Machines on the pads with shim allowance; coupling gap; bolts centred in their holes | Bolts centred so the base can move |
| 6. Grout | Form, pour and cure per the grout detail | 24 h (epoxy) to 7 days (cementitious) before torquing |
| 7. Torque anchor bolts | Remove jack screws, fill the holes, torque | The drawing's number |
| 8. Align | Final alignment at the coupling, piping connected, pipe strain checked | About .002 in (0.05 mm) offset at 1800 rpm; see [shaft alignment fundamentals](/article/shaft-alignment-fundamentals) and [pipe strain and flange alignment](/article/pipe-strain-and-flange-alignment) |
| 9. Dowel | Ream for tapered dowels at two feet of the driven machine | Usually 1/2 or 5/8 in taper pins |

Record elevations, shims, alignment readings and torques on the as-built. Guarding follows in [machine guarding and commissioning](/article/machine-guarding-and-commissioning); rigging in [moving and setting heavy machinery](/article/moving-and-setting-heavy-machinery).

## Common mistakes

- Setting by a compass or the building's idea of north instead of plant north on the drawing.
- Not checking the anchor bolt pattern against the vendor certified print before the pour; the foundation drawing was drawn from an earlier vendor revision.
- Setting bolts to the rebar instead of the template, and leaving projection short for grout, plate, washer and nut.
- Leaving bolt sleeves unfilled, or grouting jack screws in place so they become hard points.
- Using a machinery torque chart on A325 connections, or leaving a slip-critical joint snug tight.
- Mounting a conveyor take-up mid-travel with no room for stretch.

## Related

- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [Reading engineering drawings: sheets, title blocks and revisions](/article/reading-engineering-drawings-basics)
- [GD&T symbols and feature control frames](/article/gdt-symbols-and-feature-control-frames)
- [Anchor bolts and foundations](/article/anchor-bolts-and-foundations)
- [Grouting baseplates](/article/grouting-baseplates)
- [Leveling and machine setting](/article/leveling-and-machine-setting)
- [Optical and laser levels, piano wire](/article/optical-and-laser-levels-piano-wire)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
