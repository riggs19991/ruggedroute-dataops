---
title: "Electrical Safety for Mechanics: Shock and Arc Flash, the Qualified-Person Line, NFPA 70E Boundaries (Limited, Restricted, Arc Flash) and PPE Categories with the Table for Common Equipment, Reading an Arc-Flash Label, Lockout and Verifying Zero Energy with a Meter, Working Near Panels and MCCs, Cord and Tool Safety, GFCI, Temporary Power, Welding Machines and Extension Cords, Electrical Fires and Shock Response"
slug: electrical-safety-for-mechanics
category: motors-electrical
kind: safety
tags: [electrical safety, arc flash, arc flash boundary, limited approach boundary, restricted approach boundary, NFPA 70E, PPE category, arc flash label, cal/cm2, qualified person, unqualified person, electrical lockout, verify zero energy, test before touch, live dead live, GFCI, extension cord safety, temporary power, cord inspection, double insulated, portable tool grounding, MCC bucket, panel cover, electrical shock response, electrical fire, class C extinguisher, 50 volts, OSHA 1910.333, OSHA 1910.334]
source: "NFPA 70E-2024 Standard for Electrical Safety in the Workplace (Article 130: shock protection boundaries Table 130.4(E)(a), arc flash PPE categories Table 130.7(C)(15)(a) and (b), PPE table 130.7(C)(15)(c), Article 110 qualified persons); OSHA 29 CFR 1910.331-335 (electrical safety-related work practices) and 1910.147; OSHA 1926.405/1910.304 (GFCI and cords); IEEE 1584 (arc flash calculation basis)."
summary: "Where the millwright's work stops and the electrician's begins, and how to stay safe up to that line: the two electrical hazards, the boundaries NFPA 70E draws around exposed live parts and what each means for an unqualified person, the arc-flash PPE categories and the boundaries for the panels and MCCs you stand near, how to read the label on the equipment, the correct way to lock out electrical energy and prove it dead, the everyday cord, tool, GFCI and welding-machine rules, and what to do when someone is shocked or a panel arcs."
---

## Two hazards

- **Shock**: current through the body; above **50 V** (NFPA 70E's threshold for shock hazard) any exposed conductor can kill; the current, not the voltage, does the damage (10 mA cannot let go; 50-100 mA fibrillates the heart); wet skin and metal contact lower the resistance.
- **Arc flash**: an arc between conductors or to ground (a dropped tool, a slipped screwdriver, a failed component, a rat) releases a blast of heat (35,000°F plasma), molten copper, pressure and sound: burns through clothing at several feet, blinds, deafens. The **incident energy** at the working distance is measured in **cal/cm²**; **1.2 cal/cm²** causes a second-degree burn; the **arc flash boundary** is where the energy has fallen to 1.2.

Both are governed by NFPA 70E (the standard OSHA enforces through 1910.333) and the plant's electrical safety program; Canada uses CSA Z462, the same structure.

## Qualified or not

A **qualified person** has training in the construction and operation of the equipment, the hazards, the boundaries, the PPE, and how to test for voltage; most millwrights are **unqualified** for electrical work and **qualified only for specific tasks** they have been trained on (typically: operating disconnects and lockout, reading meters from outside the boundary, replacing a motor's leads with the circuit proven dead, bumping motors with the electrician). The rule for an unqualified person: **never cross the limited approach boundary** of exposed energised parts, never open an energised enclosure, never do energised work. Reading LEDs through a closed door, operating a disconnect handle with the door closed and the PPE the label requires, and working on a machine that has been locked out and verified are within reach; anything with an open panel and live parts is not.

## Shock protection boundaries (NFPA 70E Table 130.4(E)(a), AC)

![Arc flash, limited and restricted approach boundaries](/img/motors-electrical/approach-boundaries.svg)

*Arc flash, limited and restricted approach boundaries*

| Nominal voltage | **Limited approach boundary** (unqualified persons stay outside; qualified escort to enter) | **Restricted approach boundary** (qualified persons only, with shock PPE and a plan) |
|---|---|---|
| 50-150 V (120 V control, 120/208 receptacles) | 3 ft 6 in (1.0 m) (exposed movable conductors: 10 ft) | Avoid contact |
| **151-750 V (480 V, 600 V: MCCs, panels, motors)** | **3 ft 6 in (1.0 m)** | **1 ft 0 in (0.3 m)** |
| 751 V-15 kV (2,300/4,160 V motors, 13.8 kV switchgear) | 5 ft (1.5 m) | 2 ft 2 in (0.7 m) |
| 15.1-36 kV | 6 ft | 2 ft 9 in |

Values from the 2024 edition; older editions listed slightly different restricted distances. "Exposed" means the cover is off or the door is open with live parts uncovered: a closed MCC door has no exposed parts, but **operating** it (racking, opening a breaker) is an arc-flash task.

## Arc flash: categories and the equipment table

**PPE categories** (NFPA 70E Table 130.7(C)(15)(c)): the arc-rated (AR) clothing's rating in cal/cm² and what goes with it:

| Category | Minimum arc rating | Clothing and PPE |
|---|---|---|
| **1** | **4 cal/cm²** | AR long-sleeve shirt and pants (or coverall), AR face shield with a wrap-around or a hood, hard hat, safety glasses, hearing protection, leather gloves (or rubber insulating gloves with leather protectors for shock), leather footwear |
| **2** | **8 cal/cm²** | AR shirt and pants/coverall, **AR flash suit hood** or AR face shield with a balaclava, hard hat, glasses, hearing, gloves, leather footwear |
| **3** | **25 cal/cm²** | AR **flash suit** (jacket, pants, hood) over AR clothing, gloves, hard hat, glasses, hearing, leather footwear |
| **4** | **40 cal/cm²** | 40 cal flash suit, hood, gloves, etc. |

Ordinary cotton is not arc-rated (it burns); **synthetics melt into the skin**: no polyester or nylon under an arc-flash task, ever; a welder's FR cotton is not AR-rated unless it says so.

**Table 130.7(C)(15)(a), AC equipment (the table method; the label from an engineering study overrides it)**

| Equipment | Conditions the table assumes | Arc flash PPE category | Arc flash boundary |
|---|---|---|---|
| Panelboards and other equipment **≤ 240 V** | ≤ 25 kA fault, ≤ 0.03 s clearing, 18" working distance | **1** | **19 in** |
| Panelboards **> 240 V to 600 V** | ≤ 25 kA, ≤ 0.03 s, 18" | **2** | **3 ft** |
| **600 V class MCCs** | ≤ 65 kA, ≤ 0.03 s, 18" | **2** | **5 ft** |
| 600 V class MCCs | ≤ 42 kA, ≤ 0.33 s (slow clearing), 18" | **4** | **14 ft** |
| 600 V class switchgear (with power circuit breakers or fused switches) and switchboards | ≤ 35 kA, ≤ 0.5 s, 18" | **4** | **20 ft** |
| Other 600 V class equipment (277-600 V: disconnects, drives, starters not in an MCC) | ≤ 65 kA, ≤ 0.03 s, 18" | **2** | **5 ft** |
| NEMA E2 (fused contactor) motor starters 2.3-7.2 kV | ≤ 35 kA, ≤ 0.24 s, 36" | 4 | 40 ft |
| Metal-clad switchgear 1-15 kV | ≤ 35 kA, ≤ 0.24 s, 36" | 4 | 40 ft |
| Arc-resistant switchgear 1-15 kV, doors closed and latched | | N/A | N/A (40 ft with doors open) |

The table applies only when the fault current and the clearing time are within its limits (the electrical engineer confirms); if the label on the equipment gives an **incident energy** (e.g. "12.4 cal/cm² at 18 in, arc flash boundary 62 in"), the PPE is chosen to exceed that number, and the label governs. NFPA 70E's task table (130.5(C)) says which operations even need arc-flash PPE: **operating a breaker or a disconnect with the door closed and the equipment properly installed and maintained: no arc-flash PPE required** (normal operation); opening a door, racking a breaker, working on control circuits inside the enclosure, removing covers: PPE per the category. Many plants require Category 2 (8 cal) daily wear for anyone who operates 480 V disconnects: follow the plant's program.

## Reading the arc-flash label

The label on the MCC bucket, the panel, the disconnect: **nominal voltage**; **arc flash boundary** (e.g. 4 ft 3 in); **incident energy at the working distance** (e.g. 6.2 cal/cm² at 18 in) **or** the **PPE category**; the **limited and restricted approach boundaries**; the study date. What it means to you: stay outside the arc flash boundary when someone operates or opens it unless you wear the PPE; operate the handle only in the PPE the plant requires; if the label is missing or old (studies are redone every 5 years or when the system changes), ask.

## Locking out electrical energy

The [lockout basics](/article/lockout-tagout-basics) article has the full procedure; the electrical specifics:

1. **Identify** the disconnect(s) that feed the machine (the drawing, the label on the disconnect, the motor tag: a machine can have more than one source: the motor's 480 V, a 120 V control circuit from another panel, a heater circuit, a VFD with a separate control power supply, a UPS-fed PLC).
2. **Shut down** the machine at its controls (stop), then **open the disconnect** (the handle to OFF; on an MCC bucket, the door-mounted handle; stand to the **side**, face away, in the PPE, and do not stand in front of the door when operating: this is the moment an arc happens on a failed device).
3. **Lock** the handle with your lock and tag (a hasp for multiple locks; each person their own lock); **try** the machine's start button (the "try" step); on a VFD wait the bus discharge time.
4. **Verify zero energy**: for a millwright's mechanical work on a locked-out machine, the try step and the drive's display are the usual verification; **opening the enclosure to test the terminals with a meter is electrical work for a qualified person** (in the shock and arc PPE, with a meter rated CAT III/IV for the voltage, using the **live-dead-live** method: test the meter on a known live source, test the circuit phase-to-phase and phase-to-ground, test the meter again on the live source). If the work is on the motor's leads (reconnection, a motor change) the circuit **must** be tested dead at the motor box by a qualified person before anyone touches the leads; a disconnect handle in the OFF position is not proof (a welded contact, a mislabelled disconnect, a backfeed from a second source).
5. **Stored electrical energy**: capacitors (drives, power-factor correction, soft starters), batteries/UPS, generators on auto-start, control transformers fed from elsewhere; the electrician bleeds and verifies.
6. Restore: the reverse, with everyone clear, guards on, and the disconnect closed from the side in the PPE.

**Never** work on a machine that someone else locked out without your own lock; never remove another's lock; never assume a disconnect "off" without the try.

## Around panels and MCCs

- Keep **3 ft clear** in front of every panel and MCC (NEC working space: the electrician needs it and it is the escape route); nothing stored against them; no leaning tools on them.
- Doors closed and latched, covers on, **knockouts filled**, no missing bucket doors or filler plates: an open hole is an exposed-parts boundary question.
- **Water**: a panel with water dripping on it or standing water in front of it is a de-energise-before-approach situation; do not operate wet electrical equipment.
- Report: a **hot smell**, buzzing, discoloured or warm covers (IR thermography on the route: see [thermography](/article/thermography-ultrasound-and-oil)), a breaker that trips repeatedly (never hold a breaker closed or replace a fuse with a bigger one), a disconnect handle that is hard to operate, exposed wires, damaged conduit.
- When a breaker trips on a motor: reset **once** after the mechanical cause is understood (a locked rotor, a jammed conveyor); a second trip is the electrician's.
- Do not operate **medium-voltage** (2,300 V+) switchgear; that is a qualified-person, permit task.

## Cords, tools, GFCI and temporary power

- **Extension cords**: 3-wire grounded, **12 AWG or heavier** for tools over 10 A and runs over 50 ft (a 16 AWG cord on a 15 A grinder drops voltage and heats), SJ/SO jacket rated for the environment (outdoor, oil), inspected **every use** (cuts, exposed conductors, a missing ground pin, a crushed jacket: out of service, no tape repairs), not run through doorways, water, or over sharp edges, not stapled, not under a load; unplugged by the plug.
- **GFCI** (ground-fault circuit interrupter) on every receptacle in wet/damp locations, outdoors, and for temporary power on construction (OSHA 1926.404 and 1910.304); a portable GFCI adapter on any cord you use in a wet area; **test** the GFCI (the button) before use.
- **Tools**: double-insulated (the square-in-a-square symbol) or grounded (a 3-prong plug with the ground pin present); a damaged cord or a cracked housing is out of service; cordless tools in wet areas; **no tools with the guard or the trigger lock defeated**.
- **Temporary power** (a spider box, a generator, a welding machine's auxiliary outlets): rated, GFCI-protected, the generator's frame grounded or the neutral bonded per its manual, cords sized for the load.
- **Welding machines**: the primary cord and plug (240/480 V) inspected, the frame grounded, cables and holders per [welding safety](/article/welding-safety-fumes-and-ppe); the work clamp never on the plant's electrical ground, a conduit or a cable tray.
- **Lighting** in tanks and wet areas: 12 V or GFCI-protected, guarded lamps.

## When it happens

- **Someone is being shocked**: **do not touch them**; kill the power (the disconnect, the plug) if you can do it instantly and safely; otherwise use a non-conductive object (a dry wooden broom handle, a fibreglass pole) to separate them; call for help; once clear, check breathing and pulse; **CPR/AED** if none; electrical burns are deeper than they look and the heart can stop later: **hospital for any significant shock**, even if they feel fine.
- **Arc flash / panel fire**: get away from it (the pressure and the burning gases); the disconnect **upstream** if it can be reached safely (not the one that is arcing); a **Class C (or ABC) extinguisher** on electrical fires: never water, never a hose; evacuate and call; treat burns with cool water, no ointments; eye injuries from the flash: medical.
- Downed or exposed live conductors: keep everyone 30 ft away, do not approach, call the electrical crew.
- Report every near miss with a panel or a cord; the next one is the injury.

## Common mistakes

- Opening a starter's door to "look at the overload" while it is energised: category 2 exposure in a T-shirt.
- Assuming the disconnect off is proof: the motor was fed from a second panel.
- Standing in front of the MCC bucket while pulling the handle.
- A 100 ft 16-gauge cord on a 13 A drill: brown-out, a hot cord, a dead drill.
- Taping a cut cord.
- Grabbing a co-worker who is frozen on a live circuit.
- Fighting a panel fire with water.

## Related

- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [Megger and basic motor testing](/article/megger-and-basic-motor-testing)
- [VFD basics (DC bus, stopped is not off)](/article/vfd-basics-for-millwrights)
- [Motor lead connections](/article/motor-lead-connections)
- [PPE selection](/article/ppe-selection)
- [Welding safety, fumes and PPE (electric shock)](/article/welding-safety-fumes-and-ppe)
- [First aid for shop injuries](/article/first-aid-for-shop-injuries)
