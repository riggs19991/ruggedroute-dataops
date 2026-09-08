---
title: "Belt Conveyor Components and Belt Tracking: Pulleys, Idlers (CEMA Classes and Types), Take-Ups, Belt Construction and Specs, the Tracking Rules (Which Way to Move an Idler), the Tracking Sequence from Structure to Training Idlers, Symptom-Cause-Fix Table, Empty vs Loaded Tracking, Reversing and Crowned Pulleys"
slug: belt-conveyor-components-and-tracking
category: conveyors
kind: procedure
tags: [belt conveyor, conveyor components, head pulley, tail pulley, snub pulley, bend pulley, take up pulley, gravity take up, screw take up, troughing idler, return idler, impact idler, training idler, self aligning idler, CEMA idler class, belt construction, PIW, belt specification, belt tracking, belt training, belt drifting, belt running off, tracking rules, idler adjustment, crowned pulley, lagging, belt tracking loaded, reversing conveyor, conveyor structure square, conveyor alignment]
source: "CEMA Belt Conveyors for Bulk Materials (7th ed.) component definitions and idler classes; Fenner Dunlop Conveyor Handbook (belt construction, tracking rules and sequence); Martin Engineering Foundations (belt tracking and transfer points); Continental ContiTech and Goodyear conveyor belt training guidance; PPI and Precision Pulley idler and pulley catalogues."
summary: "The parts of a belt conveyor a millwright maintains and how each affects the belt, how to read a belt specification, and the discipline of tracking: the two rules that decide which way to move an idler, the sequence that starts with the structure and pulleys and ends with training idlers only as a last resort, a symptom table for a belt that runs off in one place or everywhere, and the special cases of loaded tracking, reversing belts and crowned pulleys."
---

## Components

![Troughing idler set, return idler and lagged drive pulley](/img/conveyors/idler-set-and-pulley.svg)

*Troughing idler set, return idler and lagged drive pulley*

| Component | Function | Maintenance notes |
|---|---|---|
| **Head (drive) pulley** | Drives the belt; usually at the discharge | **Lagging** (rubber, ceramic, diamond-grooved) for traction and wear; crowned on short belts; the drive is a motor/reducer with a backstop on inclines |
| **Tail pulley** | Turns the belt back at the loading end | Often a **wing pulley** (self-cleaning) or a plain pulley with a plow; crowned; where the belt is most often damaged by carryback |
| **Snub pulley** | Increases the wrap on the drive pulley (to 200-240°) | Small, close to the head pulley; runs on the dirty side |
| **Bend pulley** | Changes the belt's direction (take-up loops, tripper) | |
| **Take-up pulley** | Tensions the belt: **screw take-up** (manual, short belts under about 150 ft), **gravity take-up** (a counterweighted pulley in a vertical loop: constant tension, the standard over 150 ft), **hydraulic/winch take-up** | Gravity take-up travel: allow 1.5-2% of the belt length (plus splice allowance); the counterweight sized by the design, **never adjusted to fix tracking** |
| **Troughing (carrying) idlers** | Three rolls at 20°, **35°** (the common one) or 45° trough carrying the loaded belt; spacing 3-5 ft (closer at the loading point) | Rolls must **turn freely**: a stuck roll wears a flat and heats; bearing seals; a missing roll lets the belt sag and spill |
| **Impact idlers** | Rubber-disc rolls under the loading point | Absorb the drop; replace crushed discs |
| **Return idlers** | Flat rolls (or V-return, rubber-disc for sticky material) under the return strand, spacing 8-10 ft | Run on the dirty side: carryback builds up and tracks the belt off; clean and replace |
| **Training (self-aligning) idlers** | A troughing or return idler on a pivot that swings when the belt drifts and steers it back | One per 100-150 ft of belt, **never at the pulleys**; a band-aid if the structure is out; they also wear the belt edge if they are the only thing tracking it |
| **Transition idlers** | Half-angle idlers between the flat pulley and the full trough | Wrong transition distance = edge stress and belt damage |
| **Belt cleaners (scrapers)** | Primary (pre-cleaner at the head pulley face) and secondary (under the head pulley) | Blade tension and wear; carryback is the enemy of tracking |
| **Plows** | V-plow or diagonal plow on the return before the tail pulley | Keeps material off the tail pulley |
| **Skirtboard and skirt seals** | Contain the load at the loading point | Seal rubber wears; adjust so it does not cut the belt |
| **Pulley lagging, bushings (XT/QD), bearings (SAF/pillow blocks), shafts** | | See [pillow blocks](/article/pillow-block-and-insert-bearings), [bushings](/article/qd-and-taper-lock-bushings) |
| **Safety devices** | Pull-cord switches, belt-drift switches, speed switch (slip), plugged-chute switch, backstop/brake, guards | See [conveyor safety and guarding](/article/conveyor-safety-and-guarding) |

**CEMA idler classes** (by roll diameter and load): **B** (4-5" rolls, light: 18-48" belts), **C** (5-6", medium: the commonest industrial), **D** (5-6", heavier), **E** (6-7", heavy: mining), F (7-8", extra heavy). Replace like with like (the frame, roll diameter, trough angle, spacing).

## Belt construction and specification

A **carcass** (plies of polyester/nylon fabric, or steel cords) between **covers** (rubber, thick on the top/carrying side). Reading a spec: **"3-ply 330 PIW, 3/16 × 1/16, Grade 2, 36" wide"** = 3 plies, **330 lb per inch of width working tension** (PIW; also quoted as the total tension rating), top cover 3/16", bottom cover 1/16", RMA Grade 2 cover (Grade 1 is more abrasion-resistant; special: oil-resistant, heat-resistant, fire-resistant MSHA), width 36". Steel-cord belts are rated **ST-1000** etc. (N/mm). Replacement belt must match the tension rating (the take-up weight and the pulleys are sized for it), the width, the cover grade for the material, the trough-ability (a stiff belt will not sit in a 45° trough), and the **minimum pulley diameter** for the carcass (a 3-ply 330 needs about 16-24" head pulley; using a smaller pulley cracks the plies and the splice).

## Why belts drift

A belt runs toward the side it is **pulled** to by: idlers or pulleys not square to the belt's centreline (the belt moves **toward the end of the roll it touches first**), a pulley that is not level (the belt walks toward the tighter, higher side), off-centre loading (the belt runs **away from** the side the load is on), material build-up on a pulley or idler (a local crown that steers it), a belt with a **camber** (a bow built into it, from manufacture or from a bad splice: it runs one way on a straight structure), a splice cut out of square, structure out of line or twisted, and idlers that do not turn.

## The two rules

![How a tilted idler steers the belt](/img/conveyors/belt-tracking-rules.svg)

*How a tilted idler steers the belt*

1. **A belt moves toward the end of an idler roll it contacts first.** Skew a flat return roll or a troughing idler so that the side the belt is running **to** is **forward** (in the belt's direction of travel): the belt climbs back toward the centre. Memory aid: "**knock it in the direction of travel** on the side the belt runs to" (move the bracket on the drift side forward, or the opposite side back).
2. **Pulleys are set square and level, never skewed to steer.** A pulley that is not square to the belt (one end forward) steers the belt toward the end that is back, and a tilted pulley walks it to the high side; a crowned pulley centres a short flat belt. Correct pulleys for **squareness and level** only, and never use them as training devices.

Every adjustment is **small** (an eighth of a turn on the idler bracket bolt, a 1/8" shift of an idler foot), followed by **2-3 full belt revolutions** to see the result, and **written down** on the idler (a paint mark or a tag) so the next person can see what has been done. An idler that has been knocked all the way is a sign the problem is somewhere else: put it back square and find the cause.

## The tracking sequence

1. **Structure first**: the conveyor's stringers must be **straight, level and square**; check with a piano wire or a laser along the centreline (see [piano wire and lasers](/article/optical-and-laser-levels-piano-wire)), a level across, and diagonals at each bent; a twisted structure (one side higher at one end) is the classic cause of a belt that runs off at one point. Fix the structure before touching an idler.
2. **Pulleys**: each pulley **square to the centreline** (measure from the centreline wire to each pulley face, or diagonals from pulley to pulley: equal within 1/8") and **level** (a precision level across the shaft or the pulley face); the head, tail, snub, bend and take-up pulleys all; lagging worn evenly; **no material build-up** (a 1/4" build-up in the middle of a tail pulley is a crown that tracks the belt off).
3. **Idlers**: every idler **square to the centreline** (a square off the stringer, or a measurement from the centreline wire to each end of the idler frame) and **level**; all rolls turning; the correct trough angle and no missing rolls; idler frames all facing the same way (they are not symmetric).
4. **Loading**: material must land **centred** on the belt and in the direction of travel (chute design, skirtboards): an off-centre load cannot be tracked out.
5. **Belt and splice**: the splice square (a mechanical splice cut crooked by 1/8" steers the belt every revolution: the belt jumps over at the splice), the belt's camber (lay a length out flat and sight along the edge; a belt with a built-in bow of more than about 1/2" in 10 ft runs off no matter what you do: replace it), edge damage.
6. **Run the belt empty** and watch several revolutions: does it run off **everywhere** (a pulley, the structure, the belt) or **at one point** (the idlers/structure at that point, or a build-up)? Mark where and which direction.
7. Adjust **idlers** by rule 1, starting on the **return** side at the tail and working toward the head, then the carrying side, small moves, a few at a time, watching the belt; the idlers just ahead of the pulleys are the most effective for a belt drifting at a pulley.
8. **Load** the belt and watch again (below).
9. Training idlers last, and only for the small residual drift a well-set-up belt has (wind, moisture, load variation).

## Symptom table

| Symptom | Likely cause | Fix |
|---|---|---|
| Belt runs off **at one point** on the carrying side | The idlers at and just before that point out of square; structure twisted/high there; a stuck or missing roll; material build-up on an idler | Square the idlers there and just before; check the structure; free/replace rolls; clean |
| Runs off at **one point on the return** | Return idlers there; carryback build-up on the rolls | Clean, square, replace |
| Runs off **along the whole length** on the same side | A pulley out of square or not level (head or tail); structure out of line; the belt cambered | Square the pulleys, check the structure, then the belt |
| Runs off **at the head pulley** | Head pulley out of square/level, lagging worn on one side, snub pulley out, build-up | Square and level the head and snub, re-lag, clean |
| Runs off **at the tail pulley** | Tail pulley out of square/level, build-up, the return idlers before it, the take-up out of square | Square the tail and take-up, clean, plow |
| **Alternates** from side to side | A cambered or twisted belt; a bad splice; skirt seals pushing; over-tension | Replace the belt or splice; check seals; correct tension |
| Runs off only when **loaded** | Off-centre loading; the load shifting on inclines; the belt sagging between idlers (too little tension or too wide a spacing) | Centre the chute; skirts; idler spacing/tension |
| Runs off only when **empty** | The belt does not sit in the trough (too stiff, or the wrong belt), a slight camber; idlers slightly off | Track empty first, then load and re-check; the empty condition is the reference |
| Jumps sideways at the **splice** each revolution | Splice out of square | Re-splice square |
| Runs off in **wet weather** | Material sticking to pulleys and rolls, slipping on the drive, wet belt cambering | Cleaners, plows, lagging; training idlers for the residual |
| A **reversing** belt runs off in both directions | Anything that is skewed; training idlers of the wrong type | Reversing conveyors need everything dead square and **reversing-type** training idlers; no skewed idlers |
| The belt tracks fine, then off after a belt change | The new belt's camber, splice, or a different belt stiffness | Check the belt; trough-ability |

## Tension

The take-up must be right before tracking: too little tension = the belt slips on the drive and sags between idlers (mistracking, spillage); too much = belt and splice damage, bearing loads, and a belt that runs to the tight edge. Gravity take-up: the counterweight is by design (do not add plates to stop slip: fix the lagging or the wrap); check it floats in the middle of its travel with the belt running loaded, and does not bottom out or top out. Screw take-up: equal turns each side (measure the pulley position from the frame each side: equal within 1/16"), tensioned to remove sag and stop slip, then re-checked after the belt seats.

## Crowned pulleys

A crown (a slightly larger diameter in the middle, about 1/8" per foot of face width) self-centres a belt on **short, flat, lightly tensioned** belts (package conveyors, short transfer belts); on troughed bulk belts crowns are used on tail and take-up pulleys sometimes; crowning the **head** pulley of a high-tension belt damages the belt's centre and is not done. A crowned pulley only centres the belt if the belt has enough **free span** before it to be steered (about 1.5-2× the belt width).

## Common mistakes

- Knocking idlers before checking the structure and pulleys: after a week every idler is skewed and the belt still runs off.
- Training idlers doing all the work, wearing the belt edge to fringe.
- Adding weight to the gravity take-up to stop the belt running off.
- Crowning or shimming a pulley to steer the belt.
- Cleaning the belt but not the return idlers and the tail pulley.
- Cutting a new splice with a tape and a marker instead of squaring from the centreline (see [belt splicing](/article/belt-splicing)).
- Reaching in to clean a roll on a running belt: the nip point takes the arm.

## Related

- [Belt splicing](/article/belt-splicing)
- [Idlers, pulleys and lagging](/article/idlers-pulleys-and-lagging)
- [Conveyor safety and guarding](/article/conveyor-safety-and-guarding)
- [Optical and laser levels and piano wire (structure alignment)](/article/optical-and-laser-levels-piano-wire)
- [Pillow blocks and insert bearings](/article/pillow-block-and-insert-bearings)
- [Power, torque and drive formulas (conveyor horsepower)](/article/power-torque-speed-drive-formulas)
