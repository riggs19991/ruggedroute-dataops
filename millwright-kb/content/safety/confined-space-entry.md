---
title: "Confined Space Entry for Millwrights: Identifying Permit Spaces, Atmospheric Testing Limits, Ventilation, Attendant and Rescue, and the Entry Permit"
slug: confined-space-entry
category: safety
kind: safety
tags: [confined space, permit required confined space, PRCS, atmospheric testing, gas monitor, 4 gas meter, oxygen deficient, LEL, H2S, carbon monoxide, ventilation, attendant, entry supervisor, rescue, tank entry, vessel entry, pit, sump, tripod, retrieval, OSHA 1910.146, argon asphyxiation]
source: "OSHA 29 CFR 1910.146 (permit-required confined spaces) and 1926 Subpart AA; ANSI/ASSP Z117.1; NIOSH confined space guidance; OSHA 1910.1000 PELs; CSA Z1006 (Canada)."
summary: "How to recognise a confined space and decide whether it needs a permit, the atmosphere limits (oxygen 19.5-23.5%, LEL under 10%, H2S and CO limits) and the order of testing, ventilation practice, the roles of entrant, attendant and entry supervisor, rescue arrangements, what the permit must say, and the special hazards of welding and inert gas inside vessels."
---

> More than **60% of confined-space deaths are would-be rescuers**. Nobody goes in after a collapsed entrant without breathing apparatus and a retrieval system. The attendant's job is to call for rescue and keep others out, not to enter.

## Is it a confined space?

A space is **confined** if all three are true (OSHA 1910.146):

![Looking down into a permit space: one way in, one way out](/photos/safety/confined-space-manway.jpg)

*Looking down into a permit space: one way in, one way out. Photo: U.S. Air Force photo by Karen Abeyasekere, Public domain, via commons*

1. Large enough to enter and do work.
2. **Limited or restricted** means of entry or exit (manway, ladder, hatch, crawl).
3. **Not designed for continuous occupancy**.

It is a **permit-required confined space (PRCS)** if it also has any one of:

- A hazardous atmosphere, or the potential for one (oxygen deficiency or enrichment, flammables, toxics, dust).
- A material that could **engulf** the entrant (grain, sand, sawdust, liquids, cement).
- An internal shape that could **trap or asphyxiate** (converging walls, sloping floor to a small outlet: hoppers, silos, cyclones).
- Any other serious hazard: unguarded machinery, moving parts, live electrical, heat, noise, falling objects.

Millwright examples: tanks, vessels, boilers, reactors, mixers, dryers, kilns, silos, hoppers, bins, cyclones, ductwork, chutes, crushers, ball mills, pump pits, sumps, valve vaults, trenches over 4 ft, pipe over about 24", crawlspaces, gearbox and turbine casings large enough to enter, degreasers, paint booth pits, dust collectors, conveyor tunnels.

**Any equipment with an agitator, auger, screw, ram, mixer blade, conveyor or drive inside it is a permit space until it is locked out and, where possible, physically blocked or de-energised (stored energy)**. Lockout is a condition of entry, not a substitute for the permit. See [lockout/tagout](/article/lockout-tagout-basics).

## Atmosphere: test before entry and continuously

| Gas | Acceptable entry range | Instrument | Notes |
|---|---|---|---|
| **Oxygen** | **19.5-23.5%** | O2 cell | Below 19.5%: impaired judgement; below 16%: unconsciousness fast; below 10%: death in minutes. Above 23.5%: fire and explosion (oxygen leak from a torch) |
| **Flammable (LEL)** | **< 10% of LEL** for entry; **< 0%** for hot work in most programs | Catalytic bead / IR combustible sensor | Catalytic sensors need at least ~10-12% O2 to read correctly; a low-O2 space can show 0% LEL and be explosive |
| **Hydrogen sulphide (H2S)** | < 10 ppm (OSHA ceiling 20 ppm; NIOSH REL 10 ppm) | Electrochemical | Rotten-egg smell at low ppm, **no smell above ~100 ppm** (olfactory fatigue); sewers, pits, sumps, pulp mills |
| **Carbon monoxide (CO)** | < 25-35 ppm (OSHA PEL 50 ppm 8 h TWA; NIOSH 35 ppm) | Electrochemical | Engine exhaust, welding, heaters |
| Other toxics as the space dictates | Below PEL | Tubes, PID | Solvents, ammonia (25 ppm), chlorine (0.5 ppm), argon/nitrogen (no sensor: watch O2) |

**Test in this order**: oxygen first (the LEL cell needs oxygen), then flammables, then toxics. Test at **top, middle and bottom** of the space (gases stratify: methane, hydrogen and ammonia rise; propane, CO2, H2S and argon sink) and at every level an entrant will be at. **Continuous monitoring** on the entrant's body during the job; alarms mean everyone out. Bump-test the meter before the shift and calibrate on its schedule; a meter that was not bump-tested that day is a decoration.

## Ventilation

- **Forced-air (blower) ventilation** with the intake in clean air, not next to a running engine, the crane exhaust or the welding fume from the next job. Duct to the bottom of the space and to where the entrant works.
- Purge before entry: **at least 7-10 air changes** (typical program rule) and then re-test. Volume ÷ blower cfm × 7 = minutes. A 1,500 ft³ tank with a 1,000 cfm blower: about 10-15 min.
- Keep it running the whole job; test again after any interruption.
- Ventilation does **not** make a space non-permit; only reclassification by the entry supervisor after eliminating the hazards does (alternate entry, 1910.146(c)(5)).
- Welding, cutting or gouging inside: local exhaust at the arc **plus** general ventilation; the entrant may still need respiratory protection. **Never** use oxygen to ventilate or "freshen" a space, and never leave a torch or gas hose inside a space unattended: leaking acetylene or propane from an idle torch has killed entrants; shut off at the cylinder and take the torch out at every break.
- **Inert gas**: argon (TIG/MIG shielding, purge gas) and nitrogen are heavier than or equal to air, odourless, and displace oxygen without any sensation. Purged pipe and tanks, and any space below where argon has been used, is a no-go until tested.

## Roles (every entry has all three)

![Entry setup: tripod, blower, entrant, attendant, monitor](/img/safety/confined-space-setup.svg)

*Entry setup: tripod, blower, entrant, attendant, monitor*

| Role | Must |
|---|---|
| **Entry supervisor** | Verify tests, permit, rescue availability; authorise entry; cancel the permit when done or when conditions change |
| **Attendant** (outside, full time) | Know the hazards; count entrants in and out; maintain contact (voice, radio, rope signals); monitor conditions; order evacuation; **summon rescue; never enter**; keep unauthorised people out |
| **Entrants** | Know the hazards and symptoms (dizziness, headache, euphoria, shortness of breath, watery eyes); use the equipment; communicate; exit on any alarm or order |

The attendant may not do other work that distracts from the space. One attendant may cover more than one space only if the program allows and they can respond to all.

## Rescue

![Tripod and winch rigged over the entry for retrieval](/photos/safety/confined-space-tripod.jpg)

*Tripod and winch rigged over the entry for retrieval. Photo: Georgia National Guard from United States, CC BY 2.0, via commons*

- **Non-entry retrieval**: full-body harness with a dorsal or shoulder D-ring, lifeline to a **tripod and winch** (or davit) at the opening for vertical spaces up to 5 ft deep or any space where the line will not snag. Chest or shoulder attachment for a straight vertical pull through a manway.
- **Entry rescue**: a trained team with SCBA or supplied air, on-site or with a verified response time (the fire department is only an acceptable plan if they have confirmed capability and time; many cannot do vessel rescue).
- Rescue equipment set up **before** entry; a practice rescue at least annually.
- Any entrant who feels dizzy, hot, confused or "fine, just a bit sleepy" comes out immediately.

## The permit (posted at the entry)

Space identity; purpose; date and duration; names of entrants, attendant, supervisor; hazards; isolation done (lockout, blanks, blinds, disconnects, purging, inerting); test results with time, instrument and tester; acceptable conditions; rescue and emergency services with the phone or radio call; communication method; equipment (PPE, ventilation, retrieval, lighting, hot-work permit if welding); other permits; the supervisor's signature. Cancelled and kept on file (1 year in the US).

## Practical millwright rules

- **Isolate first**: lockout every drive; blank or blind lines that could bring in product, steam, water, gas or nitrogen (a closed valve is not isolation; a locked closed valve is not isolation of a liquid line: blind it or double-block-and-bleed).
- Cool it: a dryer, kiln or boiler that was at temperature yesterday may be over 120°F inside today; heat stress limits the work period.
- Lighting: low-voltage or GFCI-protected, explosion-proof where flammables are possible.
- Tools and cords at the opening on a lanyard so nothing has to be thrown; no gas cylinders inside; hoses leak-checked and shut off at the cylinder at every break.
- **Grain, sand, sawdust, cement**: no walking on the surface; engulfment takes seconds.
- Ladders secured; nobody climbs with tools in hand.
- Canada: CSA Z1006 and provincial regulations use the same three-part definition; "confined space entry" training and a written code of practice are required, and Alberta/BC/Ontario each specify permit contents. Red Seal exam questions follow the OSHA/CSA limits above.

## Related

- [Lockout/tagout basics](/article/lockout-tagout-basics)
- [Hot work permits and fire watch](/article/hot-work-permits-and-fire-watch)
- [Welding safety: fumes, ventilation and PPE](/article/welding-safety-fumes-and-ppe)
- [Compressed gas cylinder handling](/article/compressed-gas-cylinder-handling)
- [PPE selection](/article/ppe-selection)
- [First aid for shop injuries](/article/first-aid-for-shop-injuries)
