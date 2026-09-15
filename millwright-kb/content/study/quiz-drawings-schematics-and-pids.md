---
title: "Test Yourself: Drawings, Schematics and P&amp;IDs (20 Questions with Answers on Title Blocks and Revisions, Projection and Line Types, Fits and GD&amp;T, Piping Isometrics and Spools, P&amp;ID Symbols and ISA Tags, Hydraulic and Pneumatic Symbols, Circuit Reading and Motor Control Schematics)"
slug: quiz-drawings-schematics-and-pids
category: study
kind: reference
tags: [quiz, practice questions, drawing reading quiz, blueprint quiz, P&amp;ID quiz, ISA tag questions, GD&amp;T questions, isometric questions, hydraulic symbol quiz, pneumatic symbol quiz, ladder diagram quiz, motor control questions, title block, revision, third angle, line types, fits, feature control frame, spool sheet, line number, off-page connector, fail closed, seal-in, wire numbers, MCC bucket, Red Seal practice, apprenticeship exam, self test, study questions]
source: "Questions written against the drawings, schematics and P&amp;ID articles in this knowledge base (ASME Y14.5 and Y14.100, ISO 1219-1, ISA-5.1, NEMA ICS 19, IEC 60617, ASME B31.3 and PIP piping practice)."
summary: "Twenty practice questions on reading the documents a millwright is handed: which revision to build to, projection angle, line types, fit callouts, feature control frames, isometric welds and spools, line numbers, P&amp;ID symbols and fail positions, ISA tags and bubbles, hydraulic centre conditions, pneumatic port numbers, meter-out, the three-wire start-stop rung, wire numbers and the MCC bucket schedule. Tap each answer after you decide."
---

How to use this: read the question, decide on your answer, then tap **Answer**. Several questions refer to the pump loop P&amp;ID in the review figure. Score yourself out of 20.

![Review figure: the feed pump loop P&amp;ID used in several questions](/img/drawings/sample-pid-pump-loop.svg)

*Review figure: the feed pump loop P&amp;ID used in several questions*

## Questions

**1.** You are handed drawing M-102-004 marked REV B. The revision block on the copy in the planner's office shows a REV C dated last month. Which one do you build to, and what do you do first?

<details><summary>Answer</summary>Neither, until you have the current issued sheet: get REV C (the newest revision at the top of the block), check its status stamp says issued for construction, and look for the cloud and flag that show what changed. Review: reading engineering drawings, the basics.</details>

**2.** A drawing symbol shows a truncated cone with the two concentric circles on the same side as the cone's small end. Which projection is it, and where is the top view placed?

<details><summary>Answer</summary>Third-angle projection (the North American default): the top view sits above the front view and the right-side view sits on the right. In first angle the circles sit on the large-end side and the views swap sides. Review: mechanical drawings, views, sections and dimensions.</details>

**3.** Name the line type: thin, long dash, short dash, long dash, running through the middle of a hole.

<details><summary>Answer</summary>A centre line. Hidden edges are thin short dashes; a cutting plane is a thick dash pattern with arrows; a phantom line is long-short-short. Review: mechanical drawings, views, sections and dimensions.</details>

**4.** Decode Ø50 H7/g6. Is the shaft ever larger than the hole?

<details><summary>Answer</summary>A 50 mm hole-basis fit: H7 is the hole (zero line, grade 7), g6 the shaft (below zero, grade 6). It is a clearance fit, about 0.009 to 0.050 mm, so the shaft is always smaller than the hole. Review: mechanical drawings, views, sections and dimensions.</details>

**5.** A feature control frame reads position, Ø.014, circle-M, A, B, C. Read it as a sentence, and say what happens to the .014 if the hole is made larger than its minimum size.

<details><summary>Answer</summary>The axis of the hole must lie inside a Ø.014 cylinder located from datum A, then B, then C, with the tolerance applying at maximum material condition. As the hole grows from MMC the allowed zone grows by the same amount: that is bonus tolerance. Review: GD&amp;T symbols and feature control frames.</details>

**6.** What does the filled triangle on a leader from a square boxed letter A mean, and why does the order A, B, C in a frame matter?

<details><summary>Answer</summary>It is a datum feature symbol: surface A is what the part is rested on for measurement. The order sets up the part: A first (three points, a plane), then B (two points), then C (one point); set up in a different order and you measure something else. Review: GD&amp;T symbols and feature control frames.</details>

**7.** On an isometric, one joint is a dot with a small flag and the rest are plain dots. What is the difference, and which welds will you make on site?

<details><summary>Answer</summary>Plain dots are shop welds inside a spool; the flagged dot is a field weld (FW) made on site to join spools or to connect to equipment. Count the flags: that is the site welding. Review: piping drawings, isometrics and spool sheets.</details>

**8.** Decode 6"-P-1012-A1A-IH. Which part tells you the flange rating and gasket?

<details><summary>Answer</summary>6 inch nominal size, P process service, line 1012, pipe class A1A, insulated for heat conservation. The pipe class (spec) A1A sets material, rating, gaskets and bolting: look it up in the piping specification. Review: piping drawings, isometrics and spool sheets.</details>

**9.** An iso shows a centre-to-centre dimension of 10 ft 0 in between two 6 inch long-radius 90° elbows. What length of pipe do you cut, allowing 1/8 inch root gaps?

<details><summary>Answer</summary>Take-out for a 6 inch LR 90° is 1.5 x 6 = 9 inches each; 10 ft 0 in minus 18 inches minus two 1/8 inch gaps = 8 ft 5 3/4 in. Review: piping drawings, isometrics and spool sheets.</details>

**10.** On the review figure, which two valves isolate pump P-101A, and why is the check valve not one of them?

<details><summary>Answer</summary>The gate valve on the suction line and the gate valve on the discharge after the check valve. A check valve only stops reverse flow when it seats; it leaks, cannot be locked and is never an isolation. Also isolate the minimum-flow line, which can feed back into the header. Review: PFD and P&amp;ID reading.</details>

**11.** What is the difference between what a PFD and a P&amp;ID show, and which one do you use for a lockout?

<details><summary>Answer</summary>The PFD shows equipment, main flow paths, stream numbers and conditions; the P&amp;ID adds every valve, line number, instrument, drain, vent and connection. Lockout is planned from the P&amp;ID because the isolation valves and bleeds only appear there. Review: PFD and P&amp;ID reading.</details>

**12.** A control valve on the P&amp;ID has a diaphragm actuator and the letters FC beside it. What happens when the instrument air fails?

<details><summary>Answer</summary>FC is fail closed: the spring in the actuator shuts the valve when the air signal is lost. FO would open it and FL would leave it where it was. Review: P&amp;ID symbols, valves, equipment and lines.</details>

**13.** Read the tag LAHH-405 and say whether it lives in the field or the control room if it is drawn as a circle inside a square with a solid line across it.

<details><summary>Answer</summary>Level alarm, high-high, loop 405. A circle in a square with a solid line is a shared-display (DCS) function on the main panel, so it is in the control room; a plain circle with no line would be a field device. Review: ISA instrument tags, bubbles and letters.</details>

**14.** PIT-101, PIC-101 and PCV-101 appear on one sheet. What do they have in common and what does each do?

<details><summary>Answer</summary>They share loop number 101: PIT-101 is the pressure indicating transmitter that measures, PIC-101 the pressure indicating controller that compares to set point, PCV-101 the pressure control valve it drives. Review: ISA instrument tags, bubbles and letters.</details>

**15.** A hydraulic 4/3 valve symbol shows its centre box with all four ports blocked by T marks. What does the pump do at idle with a fixed-displacement pump, and which centre would unload it while still holding the cylinder?

<details><summary>Answer</summary>Closed centre: the pump flow goes over the relief valve at full pressure and heats the oil. A tandem centre (P to T, A and B blocked) unloads the pump and still holds the cylinder. Review: hydraulic symbols, ISO 1219, complete.</details>

**16.** On a 5/2 pneumatic valve, what are ports 1, 2, 4, 3 and 5, and what do 12 and 14 mean?

<details><summary>Answer</summary>1 is supply, 2 and 4 are the outlets to the cylinder, 3 and 5 are their exhausts. 12 is the pilot that connects 1 to 2, 14 the pilot that connects 1 to 4. Review: pneumatic symbols and circuit reading.</details>

**17.** Where does a restrictor check go to give a cylinder meter-out speed control, and why is meter-out preferred on a cylinder?

<details><summary>Answer</summary>In the line leaving the cylinder, with the check arranged to pass free flow into the cylinder and to throttle flow out. Meter-out keeps the piston loaded on both sides so an overrunning load cannot lunge ahead of the pump. Review: reading hydraulic and pneumatic circuit diagrams.</details>

**18.** In a three-wire start-stop circuit, what does the contact wired in parallel with the start button do, and what happens when the overload contact opens?

<details><summary>Answer</summary>It is the seal-in (holding) contact of coil M: it closes when M pulls in so the rung stays made after the start button is released. When the OL contact opens the rung breaks, M drops out, the seal-in opens, and the motor will not restart until reset and start are pressed. Review: motor control schematics and wiring diagrams.</details>

**19.** Two wires on a schematic both carry the number 3, one at the start button and one at the coil side of the panel. Are they the same wire, and what does the number 2, 3, PWR under a coil mean?

<details><summary>Answer</summary>Yes: a wire number stays the same on every end of that conductor and only changes when it passes through a device. The cross-reference under the coil lists the rungs holding its contacts (rungs 2 and 3) plus the power contacts, so you can find every contact that coil moves. Review: motor control schematics and wiring diagrams.</details>

**20.** A general arrangement drawing locates a pump base 5 ft 0 in from column line B and gives TOS EL 101 ft 10 1/2 in. What do you measure from, and what is TOS?

<details><summary>Answer</summary>From column line B, never from a wall or another machine; the elevation is read up from the plant datum (EL 100 ft 0 in at the benchmark). TOS is top of steel, here the top of the base plate after grout. Review: structural and machine installation drawings.</details>

## How did you do?

- 18 to 20: you can read the sheet you are handed; go on to the advanced hydraulics and PLC articles.
- 14 to 17: re-read the articles named in the answers you missed.
- Under 14: work through the drawings category from the basics article to the motor control article, then retake this quiz.

## Related

- [Reading engineering drawings: the basics](/article/reading-engineering-drawings-basics)
- [Mechanical drawings: views, sections and dimensions](/article/mechanical-drawings-views-sections-and-dimensions)
- [GD&amp;T symbols and feature control frames](/article/gdt-symbols-and-feature-control-frames)
- [Piping drawings, isometrics and spool sheets](/article/piping-drawings-isometrics-and-spool-sheets)
- [PFD and P&amp;ID reading](/article/pfd-and-pid-reading)
- [ISA instrument tags, bubbles and letters](/article/isa-instrument-tags-bubbles-and-letters)
- [Hydraulic symbols (ISO 1219), complete](/article/hydraulic-symbols-iso-1219-complete)
- [Reading hydraulic and pneumatic circuit diagrams](/article/reading-hydraulic-and-pneumatic-circuit-diagrams)
- [Motor control schematics and wiring diagrams](/article/motor-control-schematics-and-wiring-diagrams)
- [Millwright glossary A to Z](/article/millwright-glossary)
