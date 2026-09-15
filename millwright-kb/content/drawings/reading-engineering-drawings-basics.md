---
title: "Reading Engineering Drawings: What a Drawing Set Is, Sheet Sizes, Zones and Scale, Every Field in the Title Block, Revision Blocks, Clouds and Status Stamps (IFR, IFC, As-Built, Hold, Void), General Notes vs Flag Notes, the Bill of Materials and Find Numbers, Drawing Number Structures and Cross-References, an Abbreviation Table and How to Confirm You Have the Right Revision"
slug: reading-engineering-drawings-basics
category: drawings
kind: reference
tags: [engineering drawings, drawing set, sheet size, ANSI D, ISO A1, drawing zones, drawing scale, NTS, not to scale, title block, drawing number, sheet x of y, revision letter, revision block, revision cloud, revision delta, IFR, IFC, IFA, as-built, hold, void, superseded, status stamp, document control, drawing register, general notes, flag notes, bill of materials, BOM, find number, item number, reference drawings, detail callout, section callout, drawing abbreviations, TYP, UNO, TOS, TOC, CSK, CBORE, PCD, tolerance block, CAGE code]
source: "ASME Y14.100 (engineering drawing practices), ASME Y14.1 and Y14.1M (decimal inch and metric sheet sizes and formats), ASME Y14.35 (revision of engineering drawings and documents), ASME Y14.34 (parts lists), ASME Y14.38 (abbreviations and acronyms); ISO 128 (technical drawings, general principles of presentation), ISO 5457 (sheet sizes and layout), ISO 7200 (title block data fields); AISC Steel Construction Manual and PIP (Process Industry Practices) drawing conventions; typical EPC and OEM document control procedures."
summary: "How a drawing set is organised and how to find your way round a single sheet before you read a dimension: sheet sizes and zones, scale, every field in the title block, the revision block and what the status stamps mean, general notes against flag notes, how the bill of materials and find numbers tie to balloons, how drawing numbers and cross-references are built, a table of the abbreviations you will meet, and the check that proves you are working from the current revision."
---

The [blueprint reading overview](/article/blueprint-reading-for-millwrights) covers views, lines and dimensions. This article goes deeper into the paperwork around the picture: the sheet, the title block, the revisions, the notes and the parts list. Most costly drawing mistakes are the right dimension read from the wrong sheet, the wrong revision or the wrong note.

## What a drawing set is

A part rarely comes on one sheet. A **drawing set** for a machine or plant area is a family of sheets that reference each other:

![A 1927 city engineering blueprint: the drawing set is the record of what was built](/photos/drawings/seattle-blueprint.jpg)

*A 1927 city engineering blueprint: the drawing set is the record of what was built. Photo: City of Seattle, Engineering Department, Public domain, via commons*

| Drawing type | What it shows |
|---|---|
| **General arrangement (GA)** | The whole machine or area: overall dimensions, equipment tags, clearances |
| **Assembly / sub-assembly** | Parts fitted together, balloons tied to a bill of materials |
| **Detail (part)** | One part, fully dimensioned and toleranced |
| **Foundation / anchor bolt** | Concrete, pedestals, bolt pattern and projection |
| **Piping isometric, P&ID, electrical schematic** | Systems, not parts |
| **OEM installation drawing** | Mounting dimensions, lifting points, service clearances |

The set is listed on a **drawing index** giving every number, title and current revision. On a new job start with the index, the GA and the OEM installation drawing. Canadian and ISO-based jobs call the structural GA an **erection drawing**.

## Sheet layout, zones and scale

US sizes follow ASME Y14.1; metric sizes follow Y14.1M and ISO 5457.

![Sheet layout: zones, revision block, notes, drawing area and title block](/img/drawings/sheet-layout-zones.svg)

*Sheet layout: zones, revision block, notes, drawing area and title block*

| ANSI | Inches | ISO | Millimetres | Typical use |
|---|---|---|---|---|
| A | 8.5 x 11 | A4 | 210 x 297 | Sketches, small parts |
| B | 11 x 17 | A3 | 297 x 420 | Details, field prints |
| C | 17 x 22 | A2 | 420 x 594 | Sub-assemblies |
| D | 22 x 34 | A1 | 594 x 841 | Assemblies, GAs, structural |
| E | 34 x 44 | A0 | 841 x 1189 | Plant layouts |

Most field prints are D or A1 sheets reduced to B or A3, which is the first reason the title block scale cannot be trusted with a ruler: a half-size print of a 1:2 drawing is 1:4.

**Zones.** The border of a C-size and larger sheet is divided into zones: numbers along the top and bottom (starting at the right on ASME sheets), letters up the sides, so "SEE DETAIL C, ZONE B4" points to a grid square.

**Scale.** US drawings write `1:1` or `FULL`, `1:2` or `HALF`, `1:4`, and for site work architectural scales such as `1/4"=1'-0"` (1:48). Metric drawings use 1:1, 1:2, 1:5, 1:10, 1:20, 1:50, 1:100; enlarged details 2:1, 4:1, 10:1. Each view or detail can carry its own scale, overriding the title block. **NTS** (not to scale), or a dimension underlined with a wavy line, tells you the picture and the number disagree: **the number wins, always**. Plant sheets also carry a **north arrow** (plant north, not true north) and the **projection symbol** (see [views and sections](/article/mechanical-drawings-views-sections-and-dimensions)).

## The title block

The title block sits in the lower right (ASME) so it reads when the sheet is folded to A size. The fields in bold decide whether you can use the drawing at all.

![Title block anatomy: number, sheet, revision, scale and default tolerances](/img/drawings/title-block-anatomy.svg)

*Title block anatomy: number, sheet, revision, scale and default tolerances*

| Field | What it holds | Why you read it |
|---|---|---|
| **Drawing number** | The unique document number | The only reliable identity; titles repeat, numbers do not |
| **Sheet x of y** | This sheet's place in the drawing | Sheet 2 of 5 without 3-5 is incomplete; the missing sheets often hold the notes |
| **Rev** | Current revision | Must match the register and the work order |
| Scale, size | Sheet scale and size letter | Size tells you if the print is reduced |
| Drawn / checked / approved, dates | Names and dates | No checker or approver means a draft |
| **CAGE code**, customer, project | The design owner (CAGE on US government and aerospace work) and the job | Ordering spares from the right vendor; identical machines on two jobs have different bolts |
| **Tolerance block** | Defaults by decimal places on inch drawings, by ISO 2768 class on metric | Governs every dimension not otherwise toleranced |
| Units | INCH, MM or DUAL | A 25 that should have been 25.4 |
| Material, finish | Spec (ASTM A36, 4140 HT), paint, plating | Substituting is a design change; dimensions may apply after plating |
| Standard, projection symbol | ASME Y14.5-2018 or ISO; third or first angle | How tolerances are read and where the views sit |

ISO 7200 blocks carry the same data under different labels; Canadian jobs often run ISO sheets with US units, so read the units field before assuming.

## Revisions, clouds and status stamps

Under ASME Y14.35, revisions are usually letters (skipping I, O, Q, S, X and Z), with pre-release revisions as numbers or dashes; many companies use numbers, with rev 0 as the first issue for construction.

![Revision block, revision cloud and flag, and the status stamps](/img/drawings/revision-block-and-cloud.svg)

*Revision block, revision cloud and flag, and the status stamps*

**Revision block** columns: Rev, Zone (where the change is), Description ("HOLE PATTERN WAS 4X 3/4 ON 12.000 BC", "ADDED NOTE 7"), Date, By/Chk/Appr, and the ECN or DCN number that authorised it.

**Clouds and deltas.** The changed area is ringed by a scalloped **cloud** with a small triangle (the **delta**) carrying the revision letter. Clouds show only the latest revision; a stale delta means check the register.

| Status | Meaning | What you may do |
|---|---|---|
| **IFR / IFA** (issued for review or approval) | Out for comment | Do not fabricate or set to it |
| **IFC** (issued for construction) | Approved to build from | Build from it |
| Certified / approved for construction | Vendor drawing accepted by the engineer | Use for foundation and interface dimensions |
| **HOLD** | A dimension, area or sheet frozen pending a decision | Do not build the held item |
| **As-built / record** | Marked up to what was installed | The only drawing to trust for tie-ins to existing plant |
| Void / cancelled | Withdrawn | Never use |

A drawing that is IFC at rev 2 and IFR at rev 3 is a trap: rev 3 is newer but rev 2 is still the construction issue. The document control register resolves it.

## Notes, symbols legend and the bill of materials

**General notes** apply to the whole drawing, in a numbered list: "ALL DIMENSIONS IN INCHES UNLESS NOTED", "BREAK ALL SHARP EDGES .015 MAX", "ALL WELDS 1/4 FILLET CONTINUOUS UNO", "MACHINED SURFACES 125 RA UNO", "ANCHOR BOLTS BY OTHERS". Read every one before a dimension: one note just set the finish on every surface without a symbol, another took the bolts out of your scope.

**Flag notes** apply only where they are pointed: a number in a triangle, hexagon or circle on the view with a leader, and the text under the same number in the notes list. A flag on the view without its text on the sheet means a missing sheet.

**Symbols legend.** Schematics carry a legend sheet and structural sets put weld, bolt and line-type legends on the general notes sheet; the legend beats a guess.

**Bill of materials (BOM)**, the parts list of ASME Y14.34, ties the balloons on the assembly view to real parts:

| Column | Holds | Note |
|---|---|---|
| Item / find number | The balloon number | Assigned per drawing: item 5 on one assembly is not item 5 on another |
| Qty | Per assembly | AR = as required; REF = shown but not supplied |
| Part / drawing number | What you order | Never order by item number |
| Description | Name and size: "HHCS 1/2-13 X 2 GR 5 ZN" | Read the whole string |
| Remarks | "MATCH DRILL AT ASSY", "SUPPLIED WITH ITEM 12" | The remark changes the job |

Compare BOM quantity with the balloons and with what arrived on the pallet.

## Drawing numbers and cross-references

There is no universal numbering system, but most follow a structure the drawing list decodes. A common EPC pattern:

![Drawing number decoder, section cut, detail bubble and match line](/img/drawings/drawing-number-and-callouts.svg)

*Drawing number decoder, section cut, detail bubble and match line*

```
   1234 - 620 - M - 0042 - 02
   proj.  area  disc.  seq.   sheet
```

Disciplines: **M** mechanical, **C** civil, **S** structural, **P** piping, **E** electrical, **I** instrumentation. OEMs use a part number family (SK-4471-100 assembly, -101 onward details) or type codes (**GA**, **DET**, **WD**, **FDN**, **AB**).

**Reference drawings.** A list in the title block names every drawing this one depends on: the foundation drawing references the equipment GA and the vendor certified print. When two disagree, the list tells you which were supposed to agree so you can raise the conflict with both numbers.

**Detail and section callouts.** A circle with a letter above and a sheet number below: "A / 3" is detail A drawn on sheet 3, labelled there "DETAIL A, FROM SHEET 1, SCALE 2:1". A cutting-plane line with arrows and letters gives a section: "SECTION B-B" is the view seen looking in the arrow direction, drawn where the callout says ("B-B / 4"). Follow every callout before deciding a feature is undefined; the dimension missing from the plan is nearly always on the section.

## Abbreviations you will meet

ASME Y14.38 lists the standard set; these are the ones a millwright sees most, with structural and site shorthand.

| Abbrev. | Meaning | Abbrev. | Meaning |
|---|---|---|---|
| TYP | Typical: applies to all identical features | REF | Reference, not inspected |
| NTS | Not to scale | UNO / UON | Unless noted otherwise |
| C/L, CL | Centreline | SYM | Symmetrical |
| TOS, T/S | Top of steel | TOC, T/C | Top of concrete |
| TOG | Top of grout | BOP | Bottom of pipe |
| EL | Elevation | FFL, FF | Finished floor level |
| FS | Far side | NS | Near side |
| BS | Both sides | BOM | Bill of materials |
| DIA, Ø | Diameter | R | Radius |
| SR | Spherical radius | SF | Square feet; spotface on some prints |
| CSK | Countersink | CBORE | Counterbore |
| THRU | Through | EQ SP | Equally spaced |
| MIN / MAX | Minimum / maximum | NOM | Nominal |
| PCD | Pitch circle diameter | BC, BCD | Bolt circle (diameter) |
| HOLD | Frozen, do not build | FW | Field weld |
| SW | Shop weld; socket weld on piping | BW | Butt weld |
| N.C. | Normally closed | N.O. | Normally open |
| ASSY | Assembly | DET | Detail |
| THD | Thread | TPI | Threads per inch |
| LH / RH | Left / right hand | AF | Across flats |
| HHCS | Hex head cap screw | SHCS | Socket head cap screw |
| AB | Anchor bolt | PL | Plate |
| GA | Gauge, or general arrangement | WP | Work point |
| ECN, ECO | Engineering change notice, order | IFC | Issued for construction |

Canadian drawings add **U/S** (underside), **T/O** and **B/O** (top and bottom of).

## Checking you have the right drawing

Before any fabrication, layout or setting:

![Reading a drawing at the bench: check the number, sheet and revision before you start](/photos/drawings/trade-school-drawing.jpg)

*Reading a drawing at the bench: check the number, sheet and revision before you start. Photo: Internet Archive Book Images, No restrictions, via commons*

1. **Number and sheet** match the work order, and you have every sheet ("SHEET 1 OF 4" means four).
2. **Revision** matches the **document control register** (master drawing list, EDMS, or the controlled-copy stamp). The print in the crib may be superseded; the register is the truth.
3. **Status stamp** reads IFC (or certified, or as-built, as the task requires). An uncontrolled copy is for reading only.
4. **No HOLD** on your area. A held anchor bolt dimension means the concrete waits.
5. **Revision description** read against the clouds, and any material already made checked against the old value.
6. **Reference drawings** are at the revisions this one expects.
7. A pencil **field mark-up** is a request, not an authorisation; changes come by revision or a signed field change attached to the print.

## Common mistakes

- Working from the print on the crib wall without checking the register: the classic wrong-revision part.
- Fabricating to an IFR or preliminary drawing because it arrived first.
- Missing a general note that sets a finish, a tolerance or a scope exclusion for the whole sheet.
- Applying a flag note everywhere, or a general note only where a flag happens to sit.
- Ordering by item number from the BOM instead of the part number.
- Building the held dimension because it looked finished.
- Not chasing a detail callout to another sheet and deciding the feature has no dimension.
- Trusting a field mark-up as authority for a change.

## Related

- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [Mechanical drawings: views, sections and dimensions](/article/mechanical-drawings-views-sections-and-dimensions)
- [GD&T symbols and feature control frames](/article/gdt-symbols-and-feature-control-frames)
- [Structural and machine installation drawings](/article/structural-and-machine-installation-drawings)
- [Piping drawings, isometrics and spool sheets](/article/piping-drawings-isometrics-and-spool-sheets)
- [Welding symbols](/article/welding-symbols)
- [Millwright glossary](/article/millwright-glossary)
- [Quiz: drawings, schematics and P&IDs](/article/quiz-drawings-schematics-and-pids)
