---
title: "Pneumatic Systems: FRL Setup (Filter, Regulator, Lubricator), Air Tool Consumption and Hose Sizing, Piping and Drip Legs, Quick Couplers, Pneumatic Cylinders and Valves, Solenoid Valve Basics, Air Cylinder Seal Repair, Leaks, and Compressed-Air Safety (Lockout, 30 psi Rule, Whip Checks)"
slug: pneumatic-systems-frl-and-cylinders
category: hydraulics
kind: procedure
manufacturer: "Parker / SMC / Festo / Norgren / Ingersoll Rand (generic)"
model_numbers: ["Parker P3", "SMC AC series", "Norgren Excelon", "Festo MS", "Bimba", "Milton M-style", "Industrial interchange", "ARO", "Chicago coupling"]
tags: [pneumatics, FRL, filter regulator lubricator, air regulator, air lubricator drops per minute, air filter bowl, auto drain, air tool cfm, air hose size, air pressure drop, drip leg, air piping, quick coupler, Milton coupler, industrial interchange, pneumatic cylinder, air cylinder, cylinder cushion, pneumatic valve, 5/2 valve, solenoid valve, air cylinder seal kit, air leaks, whip check, 30 psi cleaning rule, lockout air, pneumatic safety, compressed air safety]
source: "Parker and Norgren FRL installation and lubricator setting guidance; Ingersoll Rand and Chicago Pneumatic air tool consumption data; OSHA 1910.242(b) (compressed air for cleaning, 30 psi); OSHA 1910.147 (lockout of pneumatic energy); Compressed Air Challenge best practices (piping, leaks); SMC and Festo pneumatic component guidance."
summary: "The plant air side a millwright maintains: setting up a filter-regulator-lubricator so the tools and cylinders get clean, dry, regulated and (where needed) oiled air, how much air tools use and how to size hoses and pipe so the pressure arrives, the couplers that do and do not mate, how pneumatic cylinders and valves work and how to repair a cylinder, finding leaks, and the safety rules on stored air, blow-off and hoses."
---

## FRL: filter, regulator, lubricator

Installed **in that order** in the flow direction, close to the point of use (within 20 ft), bowls hanging down, at eye level where you can read them.

![Filter, regulator, lubricator in order of flow](/img/hydraulics/frl-unit.svg)

*Filter, regulator, lubricator in order of flow*

**Filter** (5-40 µm particulate with a centrifugal water separator; a 0.01 µm coalescing filter after it for paint, instruments and air bearings): the bowl collects water and dirt; **drain it** (manual petcock: daily; **auto drain**: check it dumps); replace the element when the ΔP indicator shows or annually; polycarbonate bowls crack with some solvents and oils (use a metal bowl guard); the flow arrow in the flow direction.

**Regulator** (relieving type for tools, non-relieving for some systems): set **with air flowing** (the downstream pressure drops under flow: set the tool running, not static); **90 psi at the tool** for most air tools (the tool's rating: 90 psi is standard, some 100), cylinders per the machine, blow guns 30 psi or a safety nozzle; lock the knob (push down or the lock nut); a regulator that creeps up with no flow is a damaged seat: rebuild kit. Do not use the regulator as a shut-off.

**Lubricator** (mist type for tools and cylinders; micro-fog for long runs and many cylinders): fill with **air tool oil** (ISO VG 32 turbine/air tool oil, or the tool maker's oil; never motor oil or hydraulic AW oil with additives that attack seals) through the fill plug **with the line depressurised** (or a pressurised fill cap); set the drip rate with the needle screw while air is flowing at the normal rate: rule of thumb **1 drop per minute per 10-20 cfm** of flow (an impact wrench at 5 cfm average: 1 drop every 2-3 minutes; a grinder at 20 cfm: 1-2 drops per minute); too much oil fogs the shop and fouls the tool. Tools marked "oil-free" or "lubed for life" and any line feeding paint, instruments, breathing air or food: **no lubricator**. Many modern cylinders are pre-lubricated and run dry; once a cylinder has been run with a lubricator it must stay lubricated (the oil washes out the factory grease).

Air lines with a lubricator run **downhill** toward the tool where possible, or the oil pools; keep the lubricator within 20-30 ft of the tool.

## Air tool consumption and hose sizing

**Consumption** (average cfm at 90 psi, 25% duty; peak is 3-4× while running):

| Tool | Average cfm | Peak cfm |
|---|---|---|
| Blow gun | 2-3 | 10 |
| 3/8" ratchet, 1/4" die grinder | 3-4 | 12-15 |
| **1/2" impact wrench** | **4-5** | 15-20 |
| 3/4" impact | 7-8 | 30 |
| 1" impact | 10-12 | 40+ |
| 4-1/2" angle grinder | 6-8 | 20-25 |
| 7" angle grinder | 8-10 | 30 |
| Needle scaler, chipping hammer | 3-4 | 15 |
| Air drill 3/8" | 4 | 15 |
| Orbital sander | 6-10 | 25 |
| Paint spray gun (HVLP) | 10-15 (continuous) | |
| Sandblast nozzle 1/4" | 80-100 (continuous) | |
| 1/2" air hoist (1 ton) | 40-60 (while running) | |

**Hose** (ID matters, not length alone): 1/4" hose is for blow guns and small tools; **3/8" ID is the shop minimum** for impact wrenches and grinders; **1/2" for 3/4" impacts, sanders and anything over 50 ft**; 3/4" for 1" impacts, sandblasting and hoists. Pressure drop through a 3/8" hose at 20 cfm is roughly 3-4 psi per 25 ft plus 2-4 psi per coupler; a 1/4" hose at the same flow loses 15+ psi in 25 ft: the impact wrench that "has no power" is on a 1/4" hose with three couplers. Check with a gauge at the tool while running.

## Piping

- Main loop sized for **under 3-5 psi drop** at full flow; **take-offs from the top** of the main (water stays in the bottom); **drip legs** (a tee pointing down with a drain valve) at every low point and at the end of every run; the main sloped 1" in 10 ft toward the drip legs.
- Materials: black iron (standard, rusts inside: a rust-scale filter before instruments), copper (clean, brazed), aluminium modular systems (clean, easy), stainless for clean air; **never PVC** (it shatters; OSHA prohibits it above ground for compressed air).
- Isolation valves at each branch, a drain at each drip leg, a pressure gauge at the end of the longest run.
- Cold rooms: the air dries in the dryer but condenses again where the pipe crosses a cold area: insulate or dry deeper.

## Quick couplers

They look alike and do not mate: **Industrial interchange (Milton M-style, 1/4" body: the common shop coupler)**, **Automotive (Tru-Flate / T-style)**, **ARO (A-style)**, **Lincoln**, **V-style high-flow (1/4" body, 3/8" flow)**, and the 3/8" and 1/2" body sizes of each; **universal** couplers accept industrial, automotive and ARO plugs. Standardise the shop on one style; check the plug's flow size matches the hose; couplers wear (leak, blow off): replace, do not tape. On hoses over 3/4" and on every hose at a sandblast or jackhammer: **Chicago (claw) couplings with safety pins and whip checks**.

## Pneumatic cylinders

- **Types**: double-acting (the standard), single-acting spring return, rodless (magnetic or band), compact, guided, rotary actuators; **NFPA interchange** tie-rod cylinders (bores 1-1/2 to 8", rod sizes standard) and ISO 15552 metric (32-320 mm bore).
- **Force** = pressure × piston area (a 2" bore at 80 psi: 3.14 × 80 = 251 lb extend, less on retract by the rod area); size for **50-70% of the theoretical force** so it moves briskly.
- **Cushions**: adjustable needle screws at each end that trap air to slow the piston before it hits the head; set so the piston decelerates without slamming and without bouncing; a slammed cylinder breaks its rod end and the machine's stop.
- **Speed control**: flow controls **meter-out** (an exhaust restriction with a free-flow check into the cylinder) for steady motion; meter-in only on single-acting; a quick-exhaust valve at the port for fast strokes.
- **Position sensors**: magnetic reed or solid-state switches on a band around the barrel (the piston carries a magnet); a switch that chatters is at the edge of the magnet's field: move it.
- **Mounting**: the load in line with the rod; side loads bend rods and wear glands; use guided cylinders or a linear bearing for offset loads; an alignment coupler on the rod end.
- **Lubrication**: dry-running unless the line has a lubricator; if it does, keep it.

**Seal repair**: same logic as [hydraulic cylinders](/article/cylinder-repair-and-seal-kits) at low pressure: kit by maker/series/bore; lockout and **exhaust both ports**; disassemble (tie-rod nuts cross pattern, or the snap ring on a round-body); rod condition (scored = replace); piston seals (often a single double-lip seal or two O-rings with wear bands), rod seal and wiper, tube O-rings, cushion seals (a small seal in each head); grease with a **silicone or the maker's cylinder grease** (not petroleum grease on NBR/urethane, which swells or hardens); reassemble with the seals protected from the threads and ports; test at 30 psi for smooth stroke, then at working pressure for leaks at the rod and the ports, and cushion adjustment.

## Valves

- **Directional valves**: 3/2 (single-acting cylinders, pilot signals), **5/2** (double-acting: one supply, two outlets, two exhausts; the common cylinder valve), 5/3 (with a centre: closed, exhaust, or pressure centre); operated by solenoid (with a manual override button: use it to test the mechanics with the electrical de-energised and everyone clear), pilot, lever, roller, foot; **spring return or double solenoid (detented)**; valve manifolds and islands with a fieldbus.
- **Solenoid basics**: 24 VDC is standard; check the LED; a solenoid that hums and does not shift: low voltage or a stuck spool (dirt, no lubrication, dried-out seals); most cylinder valves are **pilot-operated** and need a minimum supply pressure (about 30-45 psi) to shift: a valve that works at 90 and not at 20 psi is normal; an exhaust silencer plugged with oil and dirt slows or stops the valve: replace silencers.
- **Shut-off/dump valves** with lockout provisions at every machine (an OSHA lockout point): a **three-way lockable valve** that exhausts the machine when closed; an in-line soft-start valve on machines with big cylinders.
- Air-piloted check valves and **rod locks** hold vertical loads when the air is off; **do not** rely on a cylinder holding a load with the air exhausted.

## Leaks

A hissing plant leaks 20-30% of its air; a 1/16" hole at 100 psi costs about 6 cfm (1-1.5 hp). Walk the plant during a **quiet shift** with an ultrasonic detector (or soap): couplers, hose ends, push-in fittings (the worst: replace, do not push harder), FRL bowl seals, solenoid valve exhausts (a valve that leaks at the exhaust when idle has failed seals), cylinder rod seals, drain valves left cracked, thread joints; tag, fix, re-check; a leak log with the cfm saved.

## Safety

- **Lockout of pneumatic energy** (OSHA 1910.147): close and lock the machine's isolation/dump valve, **exhaust** the machine (the dump valve vents it), **verify** zero on the machine's gauge and by trying the controls, and **block or lower** any load held by air (a vertical cylinder falls when exhausted; a pressed part springs; a clamp releases); air in a closed cylinder with the valve centred is still stored energy: exhaust both ports.
- **Compressed air on people**: never blow off clothing or skin; **OSHA 1910.242(b): blow-off nozzles limited to 30 psi dead-ended, with chip guarding and eye protection**; 40 psi into the ear or the mouth injures; air into the skin or the rectum through clothing has killed workers (embolism).
- Hoses: whip checks and safety pins on claw couplings, hoses off the floor and away from sharp edges; a burst 3/4" hose at 100 psi is a whip that breaks bones; never carry a tool by its hose; on large hoses shut the supply and bleed the hose before uncoupling.
- Pressure vessels: air receivers and any air-over-oil tank are pressure vessels: no welding, no modifications.
- Tools: eye protection with every air tool, hearing protection (impacts and grinders 95-105 dBA), the correct sockets (impact-rated: chrome sockets shatter), no exceeding a grinder's wheel rpm with an air grinder that has a failed governor (check the free speed with a tachometer yearly).
- Never exceed a tool's, a hose's or a coupler's rated pressure; never use compressed air for breathing or to pressurise a container that is not rated.

## Common mistakes

- Regulator set static at 90, so the tool sees 60 running.
- Lubricator on a line that feeds the paint booth.
- 1/4" hose with three couplers on a 3/4" impact.
- PVC air line "because it is cheap": shrapnel.
- A cylinder held up only by air while someone reaches under it.
- Blow gun without the 30 psi safety nozzle cleaning a shirt.
- Push-in fitting leaking and "fixed" with PTFE tape.
- Silencers never replaced: the valve is slow and then stuck.

## Related

- [Air compressors and PM](/article/air-compressors-pm)
- [Cylinder repair and seal kits](/article/cylinder-repair-and-seal-kits)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [Hand and power tool safety](/article/hand-and-power-tool-safety)
- [PLC and instrumentation awareness (valves and sensors)](/article/plc-and-instrumentation-awareness)
