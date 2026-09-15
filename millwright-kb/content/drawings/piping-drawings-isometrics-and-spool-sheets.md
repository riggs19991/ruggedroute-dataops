---
title: "Piping Drawings for Millwrights: The Piping Drawing Set, General Arrangement Plans and Elevations, Isometrics (30-Degree Axes, North Arrow, Not to Scale), Line Number Anatomy and Pipe Spec Classes, Fitting and Joint Symbols, Valves on an Iso, Shop and Field Welds, Spool Numbers and Match Lines, Supports and Elevations, the Bill of Material, and Cut Lengths from Take-Outs and Fit-Up"
slug: piping-drawings-isometrics-and-spool-sheets
category: drawings
kind: reference
tags: [piping isometric, iso drawing, piping drawing, spool sheet, spool drawing, piping plan, general arrangement, GA drawing, line number, line list, pipe spec, pipe class, line class sheet, service code, insulation code, butt weld symbol, socket weld symbol, threaded joint symbol, flanged joint symbol, weld dot, field weld, field fit weld, weld map, spool number, spool break, match line, north arrow, pipe support, anchor, guide, pipe shoe, spring hanger, trunnion, bill of material, material take-off, take-out, cut length, face of flange, root gap, two-hole flange, fit-up, PFI ES-3]
source: "ASME B31.3 process piping (fabrication, assembly and erection); ASME B16.5 pipe flanges and flanged fittings, B16.9 factory-made butt-welding fittings and B16.11 forged socket-welding and threaded fittings (dimensions and take-outs); PFI ES-3 fabricating tolerances for piping spools and typical EPC isometric and spool drawing conventions; ASME Y14.100 engineering drawing practices; PIP PIC001 piping and instrumentation diagram documentation criteria (line numbering); company line class sheets and legend sheets."
summary: "How the piping drawing set fits together, how to read a general arrangement plan and an isometric, how to break a line number into size, service, sequence, spec class and insulation and follow the spec class to the line class sheet, the joint and fitting symbols on an iso, how shop welds, field welds, spool numbers and match lines work, what support tags and elevations tell you, what is in the bill of material, and how to turn centre-to-centre dimensions into cut lengths and check the fit-up."
---

A piping isometric is the sheet a fitter builds from and a millwright reads to find where a pump nozzle, a spec break or a field weld really is. It carries everything about one line that the P&ID leaves out: route, dimensions, material, joints, supports and welds. It expands the short isometric paragraph in [blueprint reading for millwrights](/article/blueprint-reading-for-millwrights) into a full treatment.

## The piping drawing set

The documents that describe a line, each answering a different question:

![A piping isometric as issued: one line, its fittings, welds and dimensions on one sheet](/photos/drawings/piping-isometric.jpg)

*A piping isometric as issued: one line, its fittings, welds and dimensions on one sheet. Photo: Uhsambara, CC BY-SA 3.0, via commons*

- **P&ID**: what is in the line (every valve, instrument, size and spec); no dimensions. Isolation, drains and vents come from here ([PFD and P&ID reading](/article/pfd-and-pid-reading)).
- **Pipe spec (line class sheets)**: material, schedule, flange rating, gaskets, bolts, valve types and branch table for each class.
- **GA piping plans and sections**: to scale; where the line runs relative to columns, equipment and other lines.
- **Isometric (iso)**: not to scale; route, dimensions, joints, welds, supports and material of one line. The fabrication and erection drawing.
- **Spool sheets**: one shop-welded piece cut out of the iso with its own bill of material and cut lengths.
- **Support standards, stress iso, vendor drawings**: support details and spring settings; nozzle sizes and bolt-hole orientation on equipment.

Cutting from rev B when the field is on rev C is the commonest cause of a spool that does not fit: check the revision block first.

## Plans and elevations

The **GA plan** is a scaled plan view (3/8 in = 1 ft-0 in is common; 1:50 or 1:33 on Canadian and ISO jobs), one sheet per area and elevation band, drawn on the plant **column grid**. Equipment is in outline; large-bore pipe (usually 14 in and up) is double line, small bore single line. Each pipe carries its line number and an elevation: **CL EL 104'-6"** at the centreline, **BOP** (bottom of pipe) on steel, **TOP** at a clearance. Plant datum is usually **EL 100'-0" = finished grade** (Canadian plants often use the metric survey elevation). **Sections** (A-A, B-B) show the vertical arrangement in racks and pump rows, and the north arrow shows **plant north**, which is often not true north.

Use the plan to find the line and to check that a handwheel is reachable and a rigging path exists to pull a pump; never take a cut length from it.

## Isometrics: the grid and the north arrow

An iso shows one line on three axes: **vertical stays vertical**, and the two horizontal directions are drawn at **30 degrees** each side of horizontal. The **north arrow** in the corner fixes which 30-degree axis is north-south; turn the sheet so its north matches the plant before you picture the run.

![Worked isometric: north arrow, line number, elbows, riser, valve, field weld and spools](/img/drawings/piping-iso-worked.svg)

*Worked isometric: north arrow, line number, elbows, riser, valve, field weld and spools*

The iso is **not to scale**: a 40 ft (12 m) run and a 4 in (100 mm) stub can look the same. Everything is fixed by the dimensions, which run **centreline to centreline** between changes of direction and fitting centres, **to the face of flange** at any flanged end (nozzle, valve, blind), to the **centreline elevation** (EL) at every change of level, and to **coordinates** (N/E) at the ends and tie-ins. An **offset** that leaves the main axes sits inside a hatched triangle (the **offset box**) showing its plane; a **rolled offset** gets two triangles and the roll angle. US isos dimension in feet and inches, Canadian and ISO isos in millimetres (NPS 6 = DN 150). The border carries the line number, sheet number, P&ID reference, design conditions, test pressure, **PWHT**, **NDE** percentage and the revision block.

## Line numbers decoded

Every company writes its line number to its own legend, but the parts are the same. Take **6"-CWS-1501-A1A-IH**:

![Line number decoder: size, service, sequence, spec and insulation](/img/drawings/line-number-decoder.svg)

*Line number decoder: size, service, sequence, spec and insulation*

| Part | Example | Means |
|---|---|---|
| Size | 6" | NPS 6 (DN 150) of the main run; the number usually survives a reducer |
| Service code | CWS | Cooling water supply |
| Sequence | 1501 | Unique number; often unit or area (15) plus a running number (01) |
| Spec class | A1A | The line class: material, schedule, rating and every fitting rule |
| Insulation | IH | Heat conservation (others: IC cold, IP personnel protection, N none) |

Some companies order the parts differently or add a tracing code (**-ET** electric, **-ST** steam). Service codes vary more than anything else, and two are dangerous to assume: **FW** is fire water on one site and boiler feedwater on another; **PW** is process water or potable water. Typical codes: **CWS / CWR** cooling water supply and return, **HPS / LPS** high and low pressure steam, **CA** or **PA** plant air, **IA** instrument air, **SW** service water, **D** drain, **V** vent, **P** process.

The **spec class** is what a millwright follows up. The **line class sheet** for A1A says, for example: Class 150 carbon steel to 300 F (149 C); pipe A106 Gr B, Sch 80 to 1-1/2 in and Sch 40 from 2 in; socket-weld A105 fittings (B16.11) under 2 in, butt-weld A234 WPB (B16.9) above; weld neck raised-face flanges (B16.5); spiral-wound gaskets; A193 B7 studs; gate valves for isolation; a branch table; 1/16 in (1.5 mm) corrosion allowance. That one code gives you the wall thickness, the bolt count and size from [pipe schedule and flange tables](/article/pipe-schedule-and-flange-tables), the gasket, and whether a small branch is socket or butt welded. Where two classes meet the iso shows a **spec break** (a short bar across the line with both classes labelled); the joint at the break is built to the higher class unless noted.

## Fitting and joint symbols

An iso draws pipe as one thin line and shows the joint type by the mark at the joint. Learn the four marks first: a **butt weld** is a **dot** on the line (B16.9 fittings, 2 in and up); a **socket weld** is a **single short tick** across the line (B16.11 fittings, 1-1/2 in and under); a **threaded** joint is **two short ticks** close together; a **flanged** joint is **two parallel bars** across the line, one per flange. Fittings hang on those marks:

![Fitting and joint symbols: butt-weld, socket-weld, threaded and flanged](/img/drawings/pipe-fitting-symbols.svg)

*Fitting and joint symbols: butt-weld, socket-weld, threaded and flanged*

| Fitting | Drawn | Notes |
|---|---|---|
| 90 elbow **LR** | A sharp corner with the joint mark each side | Default in B16.9 specs; take-out 1.5 x NPS |
| 90 elbow **SR** | Same corner, labelled **SR** | Take-out 1.0 x NPS; only where the iso says |
| 45 elbow | A 45-degree bend on the iso axes | LR take-out 0.625 x NPS |
| Tee, equal or reducing | A branch with joint marks on all three ends; **6 x 6 x 4** | Run x run x branch |
| Reducer, concentric or eccentric | A trapezoid, symmetric (**CONC**) or with one flat side (**ECC FOT** or **FOB**) | Flat on top on pump suction (no air pocket); flat on bottom to hold BOP on a rack |
| **Weldolet / sockolet / threadolet** | A small saddle at the branch with the olet name | Branch fitting welded onto the run; the run is not cut |
| Union, coupling, cap | Two bars with a circle or **U**; two socket ticks for a coupling; a rounded end for a cap | Small bore; half couplings for instrument and drain connections |
| Flange **WN**, **SO**, **BL**, **LJ**, **SW** | The double bars; a blind is a bar with a filled end | **RF** default; **FF** on cast iron; **RTJ** on high pressure |

Canadian and ISO isos use the same marks with DN sizes and millimetre take-outs; some European isos draw a butt weld as a short bar. The legend sheet says which.

## Valves and inline items on an iso

Valves use the P&ID body symbols (bow tie for gate, with a solid disc for globe, with a circle for ball, a flapper for check; the full set is in [P&ID symbols](/article/pid-symbols-valves-equipment-and-lines)) with the joint marks at each end. Each valve carries its **tag** (V-1501, HV-203, XV-105) and its **face-to-face** length appears in the dimensions.

![Valves, control valve, strainer, spec break and insulation on an iso](/img/drawings/iso-valves-inline.svg)

*Valves, control valve, strainer, spec break and insulation on an iso*

The **stem** is drawn as a line from the body ending in a **handwheel** (a short bar or small circle) in the direction the stem actually points: up, horizontal north, 45 degrees down. That is an erection instruction: the plan put the handwheel where it clears a beam and can be reached. A control valve shows its actuator dome and tag (FV-310) with its bypass, block valves and drain. Strainers, orifice flanges (**FE-201**), thermowells, gauge connections, sight glasses, expansion joints and hoses are drawn the same way with their tags; the fitter supplies the connection and the instrument crew fits the instrument.

## Welds, field welds and spools

Each weld is numbered on a **weld map** (**W1, W2**) tied to the weld log. A **shop weld** is a plain dot, made in the fabrication shop as part of a spool. A **field weld (FW)** is a dot with a small **flag** and **FW**, made on site to join spools, to a nozzle or across a rack. A **field fit weld (FFW)** is trimmed on site: the shop leaves **extra length**, usually 4 to 6 in (100 to 150 mm) and stated on the iso (**FFW, 6" EXTRA**), and any dimension running to it is nominal.

![Shop welds, field welds and spool numbers on an isometric](/img/drawings/weld-numbers-and-spools.svg)

*Shop welds, field welds and spool numbers on an isometric*

The iso is split into **spools** (**1501-A1A-01**, **SP-3**), each welded in the shop and shipped as one. The designer breaks spools by rules that predict the field welds: a spool must fit the shop, the truck and the crane (typically under about 40 ft, 12 m); every flanged joint is a natural break and flanged valves ship loose; at least one FFW goes in any closed loop between fixed points such as two nozzles; spools do not cross a spec break or PWHT boundary. A **match line** is a heavy broken line where one sheet ends: **MATCH LINE, CONT ON ISO 1501 SHT 2**. The dimension across it is repeated on both sheets and must agree.

## Supports, hangers and elevations

Each support has a symbol and a **support tag** (**PS-1501-01**) leading to a detail drawing or the company standard; the type says which way the pipe may move.

![Pipe support symbols: shoe, anchor, guide, hangers and the support tag](/img/drawings/pipe-supports-symbols.svg)

*Pipe support symbols: shoe, anchor, guide, hangers and the support tag*

| Support | Symbol | What it does |
|---|---|---|
| **Anchor** (A) | Solid box or cross at the support | Stops all movement; welded plate or bolted clamp |
| **Guide** (G) | Two short lines either side of the pipe | Slides along its axis, no sideways movement |
| **Rest / shoe** (S, PS) | A short line under the pipe; a block for the shoe under insulated pipe | Weight only; the pipe slides |
| **Spring hanger** (VS variable, CS constant) | A spring in a box hung from steel | Weight through vertical travel; cold and hot loads on the hanger drawing |

The elevation at a support is given as **BOP EL** or **TOS** (top of steel). Spring hangers arrive with a **travel stop** pinned at the cold setting; the pin comes out after hydrotest and before start-up. A hanger still pinned, or a guide bolted down as an anchor, ends as a pump flange that will not line up ([pipe strain and flange alignment](/article/pipe-strain-and-flange-alignment)).

## Spool sheets and the bill of material

The **BOM** (bill of material, material take-off, MTO) sits on the iso or spool sheet, split into **fabrication material** (in the spool) and **erection material** (gaskets, bolts, loose valves, supports). Each line has an **item number** ballooned on the drawing.

![Spools fabricated in the shop, waiting for the field welds that join them](/photos/drawings/pipe-spool-shop.jpg)

*Spools fabricated in the shop, waiting for the field welds that join them. Photo: Belle Tong, CC BY-SA 4.0, via commons*

![A spool sheet with its small isometric and bill of material](/img/drawings/spool-sheet.svg)

*A spool sheet with its small isometric and bill of material*

| Item | Qty | Description | Size | Sch / rating | Material |
|---|---|---|---|---|---|
| 1 | 24'-3" | Pipe, seamless, bevelled ends | 6 in | Sch 40 | A106 Gr B |
| 2 | 3 | Elbow 90 LR, butt weld | 6 in | Sch 40 | A234 WPB |
| 3 | 2 | Flange, weld neck, RF | 6 in | Class 150 | A105 |
| 4 | 16 | Stud bolt, two heavy hex nuts | 3/4 x 3-1/2 in | | A193 B7 / A194 2H |

Pipe is listed by total length; the spool sheet gives each **cut piece** a mark and length. Check the BOM against the spec class: a slip-on where the spec says weld neck is an error to raise, not to build. The spool sheet also carries weld numbers, bolt-hole orientation and the spool weight.

## Take-outs and fit-up from the drawing

A fitting's **take-out** is its centre-to-face or end-to-end dimension from B16.9, B16.11 or B16.5; the full table is in [pipe miter layout and take-outs](/article/pipe-miter-layout).

![Cut length from an iso: centre-to-centre minus take-outs and root gaps](/img/drawings/take-out-from-iso.svg)

*Cut length from an iso: centre-to-centre minus take-outs and root gaps*

```
   Cut length = centre-to-centre dimension
                minus the take-out of the fitting at each end
                minus the root gap at each butt weld
```

| Fitting | Rule | NPS 6 |
|---|---|---|
| 90 LR elbow | 1.5 x NPS | 9 in (229 mm) |
| 45 LR elbow | 0.625 x NPS | 3-3/4 in (95 mm) |
| Weld neck flange Class 150, through hub (B16.5) | Table | 3-1/2 in (89 mm), raised face included |
| Root gap, butt weld | Per WPS | Typically 1/8 in (3 mm) |

Worked example: two LR elbows 4'-6" (54 in, 1372 mm) centre to centre on 6 in pipe. Cut length = 54 minus 9 minus 9 minus 1/8 minus 1/8 = **35-3/4 in (908 mm)**. Elbow to flange face at 3'-0": 36 minus 9 minus 3-1/2 minus 1/8 minus 1/8 = **23-1/4 in (591 mm)**.

Flanges follow the **two-hole rule**: bolt holes **straddle the natural centrelines** (vertical and horizontal on a horizontal pipe, plant north-south on a vertical one) with no hole on a centreline, unless the iso calls a rotation or **ONE-HOLE**. Read the facing and rating on both sides of the joint ([flange bolting and gaskets](/article/flange-bolting-and-gaskets)).

Fit-up checks before the tack: **bevel and land** per the WPS (37.5 degrees, 1/16 in land is typical); **root gap** as the WPS; **hi-lo** within about 1/16 in (1.5 mm), shared by rotating the fitting; **level, plumb and roll** to the drawn slope and offset angle; **flange faces parallel** within about 1/16 in with no come-along needed; and the **overall spool dimension** within the PFI ES-3 tolerance, typically plus or minus 1/8 in (3 mm).

## Common mistakes

- Reading an iso as if it were to scale and estimating a length from the picture.
- Taking a centre-to-centre dimension as the cut length and forgetting take-outs and root gaps.
- Building with an SR elbow when the iso says LR: the take-out changes by half the pipe size.
- Fitting an eccentric reducer FOB on a pump suction drawn FOT, trapping air at the impeller eye.
- Ignoring the spec break and using the lower-class flange, gasket and bolts at the joint.
- Cutting the extra length off a field fit weld before the mating spool is in place.
- Leaving spring hanger travel stops in, or bolting a guide down as an anchor, then blaming the pump.

## Related

- [Blueprint reading for millwrights](/article/blueprint-reading-for-millwrights)
- [PFD and P&ID reading](/article/pfd-and-pid-reading)
- [P&ID symbols: valves, equipment and lines](/article/pid-symbols-valves-equipment-and-lines)
- [Pipe miter layout and fitting take-outs](/article/pipe-miter-layout)
- [Pipe schedule and flange tables](/article/pipe-schedule-and-flange-tables)
- [Flange bolting and gaskets](/article/flange-bolting-and-gaskets)
- [Pipe strain and flange alignment](/article/pipe-strain-and-flange-alignment)
- [Welding symbols](/article/welding-symbols)
