---
title: "Cartridge and Logic Valves: Screw-In Cartridge Valves (Cavity Sizes, 2/3/4-Way and Solenoid Types, Reading the Code, Installation Torque, O-Ring and Back-Up Kits, Cavity Damage) and Slip-In Logic Elements (ISO 7368 Poppet, Sleeve and Cover, Area Ratios and the Force Balance, How the Cover Makes a Directional, Check, Relief or Throttle Function, Diagnosing Drift, Stuck Poppets and Instability)"
slug: cartridge-and-logic-valves
category: hydraulics
kind: reference
tags: [cartridge valve, screw-in cartridge, hydraulic cartridge valve, cartridge cavity, 08 cavity, 10 cavity, 12 cavity, 16 cavity, SAE cavity, ISO 7789, Sun Hydraulics, HydraForce, cartridge torque, cartridge O-ring kit, back-up ring, cavity damage, solenoid cartridge, poppet cartridge, spool cartridge, cartridge relief valve, cartridge counterbalance, cartridge flow control, manifold block, hydraulic manifold, logic valve, logic element, slip-in cartridge, ISO 7368, DIN 24342, two way cartridge valve, poppet area ratio, logic valve cover, pilot control cover, logic valve drift, stuck poppet, damping nose, stroke limiter, cartridge valve troubleshooting]
source: "Sun Hydraulics and HydraForce cartridge valve catalogues and technical tips (cavity families, torque, seal kits, installation); Parker, Eaton Vickers and Bosch Rexroth cartridge valve data; ISO 7368 / DIN 24342 (two-way slip-in cartridge valves: sizes 16-100, area ratios); Bosch Rexroth Hydraulic Trainer volume 4 (logic elements: function, pilot control, applications); Fluid Power Society technician study manuals."
summary: "The two kinds of valve that live inside a manifold block: the screw-in cartridge (how to read what it is from the code and the cavity, how to install one without cutting the seals or cracking the block, and the faults each type produces) and the slip-in logic element used for high flows (what the poppet, sleeve and cover do, how the area ratio and the pilot pressure at X decide whether it opens, how one element becomes a check, a directional valve, a relief or a throttle depending on its cover, and how to find the leaking pilot or the stuck poppet behind a drifting press or an unstable pressure)."
---

## Why valves live in blocks

A **manifold** (a drilled aluminium or ductile-iron block) replaces pipes, fittings and subplates with internal passages; the valves screw or slip into machined **cavities** in it. Fewer leak points, less space, and the machine's whole logic is in one block with a drawing. The cost: nothing is visible; every diagnosis starts from the **manifold drawing** (the circuit with each cavity numbered) and the **cavity stamping** on the block. Never pull a cartridge without the drawing: the same-looking valve in the next cavity does something else.

![Aluminium manifold with screw-in solenoid cartridge valves on a small power unit](/photos/hydraulics/cartridge-manifold.jpg)

*Aluminium manifold with screw-in solenoid cartridge valves on a small power unit. Photo: Simon Speed, CC0, via commons*

## Screw-in cartridge valves

![Screw-in cartridge in its cavity: seals, ports, torque](/img/hydraulics/cartridge-valve-cavity.svg)

*Screw-in cartridge in its cavity: seals, ports, torque*

A screw-in cartridge is a complete valve (a poppet or spool, a spring, a seat, an adjuster or a solenoid tube) in a threaded steel body with **O-rings and back-up rings** separating the ports along its length. The cavity is a stepped bore: each step is a port. The threads only hold it in; the O-rings do the sealing.

### Cavities

Cavities are standardised **within a maker's family** and not always across makers: a Sun Hydraulics T-11A, a HydraForce VC10-2, a Parker C10-2 and an ISO 7789 10-size 2-way cavity are similar but not interchangeable in every case. Know the family before ordering.

| Common family | Thread (typical) | Nominal flow | Ports (ways) | Typical uses |
|---|---|---|---|---|
| **08 size** (SAE-08, Sun T-8A, HF 08) | 3/4-16 UNF | 5-8 gpm (20-30 L/min) | 2, 3, 4 | Small solenoid valves, pilot reliefs, checks, orifices |
| **10 size** (SAE-10, Sun T-10A/T-11A, HF 10) | 7/8-14 UNF | 12-25 gpm (45-95 L/min) | 2, 3, 4 | The workhorse: reliefs, counterbalance, solenoid poppets, flow controls |
| **12 size** (Sun T-13A/T-3A, HF 12) | 1-1/16-12 UN | 25-40 gpm (95-150 L/min) | 2, 3, 4 | Main reliefs, larger solenoid valves, counterbalance on cranes |
| **16 size** (Sun T-17A/T-5A, HF 16) | 1-5/16-12 UN | 40-80 gpm (150-300 L/min) | 2, 3 | Main reliefs, unloading, large checks |
| **20 / 24 size** | 1-5/8-12, 1-7/8-12 UN | 80-150 gpm | 2, 3 | Large checks and reliefs (logic elements take over above this) |
| **M-series metric** (ISO 7789, Rexroth, Hydac) | M20×1.5, M27×2, M33×2, M42×2 | | | European manifolds |

The cavity is identified by the maker's tool stamping on the block face or the drawing; the number of **O-ring grooves** on the cartridge tells you the number of ports (a 2-way has two seals, a 3-way three, a 4-way four). The port numbering on the cartridge drawing (1 at the nose, 2 the first side port, 3 the next, 4 the top) matches the cavity's steps from the bottom up.

### Types and what goes wrong

![Screw-in pressure cartridges: relief and load-holding valves, and a solenoid pressure valve on a block](/photos/hydraulics/relief-valve.jpg)

*Screw-in pressure cartridges: relief and load-holding valves, and a solenoid pressure valve on a block. Photo: HAWE Hydraulik, CC BY-SA 4.0, via commons*

| Type | Element | Function | Typical faults |
|---|---|---|---|
| **Check** | Ball or poppet, spring | One-way; cracking 5-75 psi | Debris on the seat: leaks (a load drifts); a broken spring: chatter |
| **Pilot-operated check** | Poppet with a pilot piston | Leak-free load holding, opens on pilot pressure (ratio 3:1 to 4:1) | Pilot piston stuck, seat damage, pilot ratio too low for the load |
| **Relief** (direct or pilot-operated) | Poppet and spring, adjuster | Limits pressure; a pilot-operated cartridge relief has a small pilot poppet and a main poppet | Adjuster backed out by vibration (no lock nut), seat wear (creeping setting), pilot orifice blocked (relief will not open: dangerous), chatter when set near a compensator |
| **Pressure reducing / reducing-relieving** | Spool, spring, adjuster | Lower pressure downstream; the relieving version also vents downstream over-pressure | Drain blocked: will not regulate; spool stuck: full pressure downstream |
| **Sequence, unloading** | Spool or poppet with a pilot port | Sequencing; unloading a pump on a pressure signal | Drain plugged, pilot line leaking |
| **Counterbalance (motion control)** | Poppet, spring, pilot piston, adjuster | Load holding plus controlled lowering; pilot ratio 3:1, 4.5:1 or 10:1 | Set too low: load creeps; too high: heat and slow lowering; wrong ratio: instability (a shuddering boom) |
| **Flow control** (needle, pressure-compensated, priority, proportional) | Needle or spool with a compensator | Speed | Compensator spool stuck (speed varies with load), needle damaged by over-tightening |
| **Flow divider / combiner** | Spool | Splits flow to two motors | Spool stuck: one wheel spins |
| **Solenoid, 2-way poppet** (NO or NC) | Poppet pushed by a wet-armature solenoid | Leak-free on/off; blocking one direction only unless a bidirectional type | Poppet seat contamination, coil failures, **flow direction** (many block in one direction only: check the arrow), reverse flow pushing the poppet open |
| **Solenoid, 2/3/4-way spool** | Spool | Directional, small flows | Spool leakage (never leak-free), silting |
| **Proportional (solenoid) cartridges** | Spool or poppet with a proportional solenoid | Pressure or flow from a current signal | Contamination, coil drift, needs its amplifier settings |
| **Shuttle, orifice, plug** | | Logic; fixed restriction; a blank | An orifice fitted the wrong size or in the wrong cavity |
| **Pressure switch / transducer cartridges** | | | |

### Reading a cartridge

The body is stamped (or laser-marked) with the maker's model code, and often a date code and the pressure adjust range. Decode it in the catalogue: for example a Sun code such as `CBCA-LHN` reads as a counterbalance (CB), size (C = T-11A cavity), pilot ratio (A = 3:1), adjust range and seals; a HydraForce `SV10-24` is a 10-size 2-way solenoid valve, NC, and its coil is a separate part number. **Never** identify a cartridge by shape and colour alone: the same body machined with a different poppet is a different valve. Photograph the marking before it goes back in.

### Installation

1. Lockout, bleed; know what the cavity feeds. Clean the block face around the cavity before removing anything; cap open cavities at once.
2. Remove with a six-point socket or the correct hex, straight; a stuck cartridge: back and forth gently, never pry; count the seals that come out (a seal left in the cavity blocks the next cartridge from seating).
3. Inspect the cavity with a light: the seats between steps must be **smooth and unscored** (a nick across a step = a leak from one port to the next; cavities can be re-machined with the maker's tool, or the block replaced); flush the cavity and the passages with clean solvent and blow dry; no rags that shed.
4. **Seals**: a new kit every time (O-rings with PTFE **back-up rings** on the pressure side of each O-ring: the back-up goes **away** from the pressure, so it supports the O-ring against extrusion into the gap; the kit drawing shows the order); the right material for the fluid (Buna-N standard, FKM for high temperature and phosphate ester, EPDM for some water glycols and brake fluids: see [hydraulic fluids](/article/hydraulic-fluids-types-and-compatibility)); lubricate with the system oil.
5. **Install straight**: start it by hand, feel it seat through each step (a cocked cartridge cuts the O-ring on a step edge and leaks between ports), then torque with a torque wrench to the maker's number: as a guide **08 size: 20-25 ft-lb (27-34 N·m); 10 size: 30-35 ft-lb (40-47 N·m); 12 size: 45-55 ft-lb (60-75 N·m); 16 size: 100-150 ft-lb (135-200 N·m); 20 size: 150-200 ft-lb**; steel blocks slightly higher, aluminium blocks at the low end. Over-torque distorts the body and binds the spool or poppet; under-torque and the cartridge backs out under pressure pulses.
6. Solenoid coils: slide on, the retaining nut **hand-tight plus a quarter turn (about 4-6 ft-lb / 5-8 N·m)**: an over-tightened nut crushes the tube and the armature sticks. Plug gasket in.
7. Set adjustable cartridges with a gauge on the right port, record the setting, and tighten the lock nut (or fit the tamper cap).
8. Pressure up slowly and look for leaks at the hex and between ports (an internal port-to-port leak shows as a hot block, a function that drifts or a pressure that will not build).

### Manifold diagnosis

- Get the **drawing**: cavity numbers, the valve in each, the port each passage connects to, the test points. Identify the block by its part number stamping.
- **Temperature mapping** with an IR gun: a hot cartridge is passing oil across a pressure drop (a relief dumping, a check leaking, a reducing valve relieving).
- Use the **test points** (a gauge at each) to see the pressure at each stage; no test point = fit one at a spare port.
- Swap identical cartridges between two similar circuits to see whether the fault follows the valve.
- A drift or leak that persists after a new cartridge is a **cavity** fault (a scored step) or a **passage** fault (a cross-drilled hole not plugged, a plug leaking: expansion plugs and set-screw plugs in the block ends are sealed passages too).
- A cartridge that works on the bench and not in the block: wrong cavity family (it screws in and the ports do not line up), wrong seal kit thickness, or debris lying at the bottom of the cavity.

## Slip-in logic valves (ISO 7368 two-way cartridges)

![Logic element: poppet, sleeve, cover and the areas that decide it](/img/hydraulics/logic-valve-cross-section.svg)

*Logic element: poppet, sleeve, cover and the areas that decide it*

Above about 80-100 gpm a spool valve becomes huge; a **logic element** does the job. It is a **poppet** in a **sleeve**, pushed into a standard cavity (ISO 7368 / DIN 24342 sizes **16, 25, 32, 40, 50, 63, 80, 100** mm nominal) in a manifold and held down by a **cover** (control cover) that carries the pilot circuit. Each element is only ever a **2-way valve**: open or closed between port **A** (the nose, on the axis) and port **B** (the side, radial). What makes it a directional valve, a check, a relief or a throttle is **what the cover does with the pilot pressure on top of the poppet** (the spring chamber, port **X**).

### The force balance

The poppet has three areas: **A_A** (the nose seat area, facing port A), **A_B** (the annulus facing port B) and **A_X** (the full top area facing the spring chamber, = A_A + A_B). With p_A, p_B and p_X the pressures at each:

```
   opens when   p_A × A_A  +  p_B × A_B   >   p_X × A_X  +  spring
   closes when  p_X × A_X  +  spring       >   p_A × A_A  +  p_B × A_B
```

- **Pilot chamber connected to tank** (p_X = 0): the element opens whenever A or B has more pressure than the light spring needs (typically 15-60 psi / 1-4 bar cracking): it is an **open valve** in both directions.
- **Pilot chamber connected to the higher of A or B** (through a shuttle in the cover): p_X equals the highest port pressure, and because A_X is the largest area the element is held **closed** against flow from either side: a **leak-free directional element**. A small pilot valve (a D03 solenoid valve on the cover) switches X between the shuttle and tank: energise it and the element opens.
- **Pilot chamber connected to port B** (p_X = p_B): the B terms cancel and the poppet lifts when p_A exceeds p_B by the spring's cracking pressure: a **check valve that passes A to B and blocks B to A**. Connect X to port A instead and it passes B to A and blocks A to B, but now only the small annulus A_B works against the spring, so the cracking pressure is higher: that is why check elements for B-to-A duty use the 1:1.5 or 1:2 area ratios.
- **Pilot chamber controlled by a small relief valve** on the cover (X vented through the relief): the element becomes a **pilot-operated relief valve** of very high capacity: p_X is held at the pilot setting, and the poppet opens to dump A to B (tank) when p_A exceeds it; the same cover with a solenoid vent makes an **unloading** valve.
- **Cover with a stroke limiter** (a screw that stops the poppet short): the element becomes a **throttle** (a flow control at high flow); with a proportional pilot, a proportional throttle.
- **Cover with an orifice** in the X line: slows the opening or closing (damping) to avoid shock.

### Area ratios

The **area ratio** A_A : A_X is stamped on the poppet or sleeve and listed in the drawing: **1:1** (A_B is zero: a pure pressure/relief element; the poppet is a piston with no annulus, pressure at B does nothing), **1:1.1** or **1:1.07** (a small annulus: directional and check duty where B pressure should barely influence it), **1:1.5** and **1:2** (a large annulus: B pressure helps open it; used for check functions from B to A with low pressure drop and for throttle elements). Fit a poppet with the wrong ratio in a rebuild and a directional element leaks open when B pressure rises, or a relief element's setting changes with the tank pressure. The poppet nose is either a **sharp seat** (leak-free, directional and check) or has a **damping nose** (a tapered spigot that enters the seat bore before the seat closes: soft closing for relief and throttle duty; the nose also delays opening slightly).

### Reading a logic manifold

A press manifold may hold ten elements: two for the pump-to-cylinder directions, two for the return paths, one as the main relief, one as a decompression valve, one as a pre-fill for the big cylinder, one for a regeneration path. The drawing shows each as a poppet symbol with its cover's pilot circuit in a dashed enclosure; the small pilot valves on the covers are the only things that move with a solenoid. To follow a fault: **which elements should be open at this step of the sequence** (from the sequence table), and **what pilot pressure is at each X** (test points on the covers, or a gauge at the pilot valve's ports).

### Faults and diagnosis

| Symptom | Cause | Check |
|---|---|---|
| Cylinder or press ram **drifts** with the pump off | An element that should be closed is leaking: **debris on the seat**, a scored seat or poppet, a **leaking pilot** (the X chamber loses pressure through a leaking pilot valve, a leaking cover O-ring or a cracked pilot line, so the poppet lifts), a wrong area ratio, a broken spring | Feel the element's cover and the B line for warmth; gauge at X: it should equal the higher port pressure; isolate the pilot valve; pull the element and look at the seat under a glass |
| Element **will not open** | No pilot switching (pilot solenoid dead, pilot supply lost, the shuttle stuck sending the high pressure to X), an orifice in the X line blocked, a poppet stuck in the sleeve (contamination, varnish, a burr), a stroke limiter screwed down | Gauge at X while commanding: it must drop to tank; manual override on the pilot valve; pull the element: does the poppet slide freely by hand? |
| Element **will not close**, function will not hold or pressure will not build | Poppet stuck open, debris, the shuttle stuck feeding X to the low side, pilot valve stuck open to tank, the X orifice open too far | As above |
| **Relief function unstable** (hunts, screams, hammers) | Wrong or missing damping nose, a missing or wrong X orifice, the pilot relief too close to another pressure setting, air in the pilot lines, a poppet ratio wrong | Compare with the drawing's ratio and orifice sizes; bleed |
| Shock on switching | X orifice missing (the element slams), stroke limiter too open, no decompression step in the sequence | |
| Element **leaks between A and B when new** | Seat damaged in installation (a poppet dropped into the cavity), sleeve O-rings wrong or cut, the cover bolts not torqued evenly so the sleeve is not seated | |
| Oil at the cover | Cover O-rings, the cover bolts (torque: size 16: M8 about 25 ft-lb; 25: M12 about 75 ft-lb; 32: M16 about 200 ft-lb; per the drawing), a cracked cover from over-torque | |

### Servicing an element

1. Lockout, bleed the press circuit **including the accumulators and the cylinder** (a press ram must be blocked or at bottom); decompress: the trapped oil in a big cylinder at 4,000 psi is a bomb.
2. Remove the pilot valve and the cover (bolts in a cross pattern); lift the cover straight (the poppet spring is under it; some covers have a dowel and an orifice plug that falls out).
3. Draw the sleeve and poppet out with the maker's puller or a suitable bolt in the threaded top; keep each element with its own cover and cavity number.
4. Inspect the poppet seat and the sleeve seat under magnification (a bright line or a nick = leak), the poppet's sliding surface for scoring, the damping nose for chips, the spring for length against a new one, the sleeve O-rings and back-ups, the cavity for scoring.
5. Replace the poppet and sleeve **as a matched pair** with the same area ratio and nose type; lap only per the maker; new seals; oil everything; install the sleeve square until it seats, the poppet, the spring, the cover with its O-rings and any orifice plugs; torque the cover bolts in stages.
6. Refit the pilot valve, bleed the pilot lines, and re-set any pilot relief with a gauge.

## Common mistakes

- Pulling a cartridge without the manifold drawing and putting it back in the wrong cavity.
- Cocking a cartridge on the way in and cutting an O-ring on a step.
- Old seals reused, or the back-up ring on the wrong side of the O-ring.
- Torquing an aluminium block to a steel-block value: cracked cavity.
- Coil nut tightened with pliers: the tube is crushed, the armature sticks.
- Assuming a 2-way solenoid poppet blocks in both directions.
- Rebuilding a logic element with a poppet of a different area ratio because "it fitted".
- Forgetting the X-line orifice plug: the element slams and the press shakes.
- Working on a press manifold with the accumulator still charged.

## Related

- [Directional control valves, spools and solenoids](/article/directional-control-valves-spools-and-solenoids)
- [Pressure and flow control valves in depth](/article/pressure-and-flow-control-valves-in-depth)
- [Stack valves and sectional valve banks](/article/stack-valves-and-sectional-valve-banks)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Accumulator precharge and safety](/article/accumulator-precharge-and-safety)
- [Hydraulic fluids: types and compatibility (seal materials)](/article/hydraulic-fluids-types-and-compatibility)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
- [Hydraulic symbols (ISO 1219), complete](/article/hydraulic-symbols-iso-1219-complete)
