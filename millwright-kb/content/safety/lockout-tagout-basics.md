---
title: "Lockout / Tagout Basics for Millwrights (OSHA 1910.147)"
slug: lockout-tagout-basics
category: safety
kind: safety
tags: [lockout, tagout, LOTO, energy isolation, zero energy, try start, stored energy, group lockout, hasp, 1910.147, electrical, hydraulic, pneumatic, gravity]
source: "OSHA 29 CFR 1910.147 The Control of Hazardous Energy; ANSI/ASSP Z244.1."
summary: "The eight steps of a lockout, the energy sources millwrights forget (springs, gravity, hydraulic accumulators, trapped pressure), group lockout with hasps, and the restart sequence."
---

## Energy sources to isolate

| Source | Isolation | Stored energy to release |
|---|---|---|
| Electrical | Disconnect switch / breaker, **locked open** (not the stop button, not the VFD keypad) | Capacitors (VFDs need 5+ minutes), motors coasting |
| Hydraulic | Pump off and locked, isolation valves locked | **Accumulators**, cylinders under load, trapped line pressure - bleed down |
| Pneumatic | Supply valve locked, line vented | Receivers, cylinders - vent and confirm 0 psi |
| Mechanical / gravity | Block, pin or crib raised parts, counterweights, flywheels | Springs, tensioned belts/chains, rotating inertia |
| Steam / hot water / chemical | Valves locked, lines drained, blinded if required | Thermal, pressure |
| Conveyors | Electrical plus mechanical block if on an incline (backstop can fail) | Gravity |

A machine can have five or six points. The machine-specific **LOTO procedure** lists them. If one does not exist, do not guess; write one and get it approved.

## The eight steps

![The eight lockout steps in order](/img/safety/lockout-steps.svg)

![A personal lock on an isolation point](/photos/safety/lockout-hoist-brake.jpg)

*A personal lock on an isolation point. Photo: Wtshymanski, CC BY-SA 4.0, via commons*

*The eight lockout steps in order*

1. **Prepare**: identify every energy source and the isolation device for each. Get the locks, tags, hasps, valve covers, plug locks you need. Only **your** personal lock, one key, in your pocket.
2. **Notify** affected employees (operators, other trades) that the machine is coming down.
3. **Shut down** using the normal stop procedure (do not open a disconnect under load if it can be avoided).
4. **Isolate**: open disconnects, close valves, pull plugs, set blocks.
5. **Apply locks and tags** to every isolation device. The tag says who, why, and when. A tag alone is only allowed if the device cannot take a lock, and then extra measures are required.
6. **Release stored energy**: bleed hydraulic and pneumatic pressure, discharge capacitors, block or lower raised parts, release spring tension, let rotating parts stop, drain lines.
7. **Verify** ("try-start"): press the start button, jog, or otherwise attempt to operate; check gauges read zero; test electrical circuits with a meter (live-dead-live) when working on the conductors. **Return the controls to off.**
8. **Work**, and re-verify if you leave and come back.

## Group lockout

Each worker puts their **own lock** on the hasp or lock box. The last person off removes the last lock. Never remove another person's lock. If someone leaves with their lock on, the supervisor follows the written **lock-removal procedure** (confirm the person is clear, document, then cut). Shift change: the incoming crew locks on before the outgoing crew locks off.

![Multi-lock hasp: every worker adds a lock, nobody removes another person's](/photos/safety/lockout-hasp.jpg)

*Multi-lock hasp: every worker adds a lock, nobody removes another person's. Photo: Wtshymanski, CC BY-SA 4.0, via commons*

## Restart

![Lockout board: every lock and tag accounted for before restart](/photos/safety/lockout-board.jpg)

*Lockout board: every lock and tag accounted for before restart. Photo: NAVFAC, Public domain, via commons*

1. Inspect the work area: tools out, guards on, blocks removed, personnel clear.
2. Notify affected employees.
3. Remove your lock and tag (only yours).
4. Re-energise in the correct order; test run; hand back to operations.

## Common millwright mistakes

- Locking a control-circuit switch (E-stop, HOA) instead of the power disconnect.
- Forgetting the second feed on a machine with two motors or a separate control transformer.
- Not bleeding an accumulator, then loosening a fitting.
- Trusting a conveyor backstop instead of blocking.
- Removing a "temporary" lock to "just bump it" for alignment: use the plant's **energised-work / test procedure** instead (usually all workers clear, one person energises, then re-lock).
- Working under a suspended load or an unblocked raised platen.

## Related

- [Oxy-fuel safety](/article/oxy-fuel-safety)
- [Rigging basics](/article/rigging-basics-sling-angles-and-hitches)
