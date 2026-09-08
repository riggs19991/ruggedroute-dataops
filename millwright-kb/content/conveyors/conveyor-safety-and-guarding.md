---
title: "Conveyor Safety and Guarding: Nip Points and Where They Are, Guarding Rules (ASME B20.1, OSHA 1910.212/219), Pull-Cord and Safety Switches, Lockout of Conveyors Including the Gravity Take-Up and Inclines, Working Around Running Belts, Crossing and Riding Rules, Transfer Points and Dust, Start-Up Warnings and Inspection Checklist"
slug: conveyor-safety-and-guarding
category: conveyors
kind: safety
tags: [conveyor safety, nip point, pinch point conveyor, conveyor guarding, ASME B20.1, OSHA 1910.212, OSHA 1910.219, pull cord switch, emergency stop conveyor, belt drift switch, speed switch, plugged chute switch, conveyor lockout, gravity take up lockout, counterweight lockout, incline conveyor lockout, belt clamp, crossing a conveyor, crossover, riding a conveyor, cleaning a running conveyor, conveyor start warning, conveyor inspection, transfer point dust, conveyor fatalities]
source: "ASME B20.1 Safety Standard for Conveyors and Related Equipment; OSHA 29 CFR 1910.212 (machine guarding), 1910.219 (mechanical power transmission), 1910.147 (lockout/tagout); MSHA 30 CFR 56/57 conveyor rules and fatality reports (belt conveyor nip points); CEMA Safety Program guidance and safety labels; Martin Engineering Foundations (transfer points and dust)."
summary: "Conveyors kill more maintenance people than any other machine in bulk-handling plants, almost always at a nip point on a belt that was running: this covers where the nip points are, what must be guarded and how, the safety switches and what they do and do not protect, a lockout procedure that includes the stored energy in take-ups and inclined belts, the rules for working near, crossing and never riding a belt, transfer-point hazards, and a pre-start and inspection checklist."
---

## Where people get hurt

![In-running nip points on a belt conveyor](/img/conveyors/conveyor-nip-points.svg)

*In-running nip points on a belt conveyor*

- **Nip points**: where the belt meets a **pulley** (head, tail, snub, bend, take-up: the belt runs **into** the pulley on one side), where the belt runs onto a **return roll** or a carrying idler (the in-running side), the **drive** (chain, sheave, coupling), and **cleaners, plows and skirt seals** against the belt. A glove, a sleeve, a shovel or a rag drawn into a pulley nip pulls the arm in faster than anyone can react; MSHA's fatality reports are mostly people **cleaning a running belt** near the tail pulley or **freeing a stuck roll** on a running belt.
- **Falls** from conveyor walkways and while crossing belts; **being struck** by material from a transfer point or a tripper; **caught** between a carriage (tripper, take-up) and the structure; **crushed** by a gravity take-up counterweight; **fire and dust explosions**.
- The common thread: the belt was running, or was locked out but still had stored energy, or restarted on a remote signal.

## Guarding

- Every **nip point within reach** (under 7 ft from the floor or a platform, or reachable from a walkway) is **guarded** (ASME B20.1, OSHA 1910.212/219): the head pulley (both sides, the return strand where it enters), the tail pulley (the most common unguarded nip: a full guard around the pulley and the return belt for 3-4 ft, with a mesh small enough to stop a hand: **1/2" mesh at 4"+ from the nip**, finer closer), take-up and bend pulleys (the gravity take-up loop fully enclosed, with the counterweight travel guarded so nothing can be under it), snub pulleys, **return rolls over walkways and along working aisles** (a "return roll guard": a basket under the roll, or a full-length guard on the walkway side), the drive (chain/belt guards, couplings), and the carrying idlers along any walkway where people work close (side guards or a spacing that keeps hands out).
- Guards are **fixed** (tools to remove), strong, and do not themselves create a nip; **interlocked** guards where access is frequent; inspection **windows** so rolls can be checked without removing guards.
- Guards go **back on before the lockout comes off**; a conveyor with a guard off is out of service.
- **Walkways** on at least one side of long conveyors (B20.1 and most plant standards: a walkway with handrails, toe boards, and clearance), crossovers at intervals, no gaps between the walkway and the guard that a leg can go through.

## Safety switches

| Device | What it does | What it does not do |
|---|---|---|
| **Pull-cord (rope) emergency stop** | A cord along the walkway that trips a switch when pulled; latches; must be reset | It stops the drive: the belt **coasts** (seconds on a flat belt, and an inclined belt can run **back** unless the backstop holds); it is **not** a lockout |
| **Belt drift/misalignment switches** | Trip when the belt edge pushes a lever | Only at the switch positions |
| **Speed (slip) switch / zero-speed** | Trips when the belt (or tail pulley) is not turning at speed: a slipping drive, a broken belt, a jam | Nothing about people |
| **Plugged-chute switch** | Trips when a transfer chute fills | |
| **Belt rip detector** | Stops on a longitudinal tear | |
| **Pre-start alarm** (horn/strobe, 10-30 s before start) | Warns people along a remotely started conveyor | Only if people can hear it and it works |
| **Backstop / brake** | Holds an inclined belt from running back | Not a lockout: the belt is still under tension |

The pull cord is the **first** thing to find on any conveyor you approach: know where it is, test it on the pre-start checks, never tie it back, and never work with a cord that is slack or broken. An e-stop **does not** make a conveyor safe to work on.

## Lockout of a conveyor

Conveyors have more stored energy than the motor: the belt's **tension** (the take-up pulls the belt with hundreds to thousands of pounds), the **gravity take-up counterweight** (a ton hanging in a loop), an **inclined belt with material on it** (it runs back when the belt is cut or the drive is released), a **tripper carriage** on a slope, hydraulic or pneumatic take-ups and brakes, and **remote/automatic starts** (a PLC that restarts the line when the upstream conveyor runs).

1. **Electrical**: the drive's disconnect **and** any separate control power; verify by trying the local and the remote start; lock and tag; for a line of conveyors interlocked to each other, lock out the ones that can feed onto or run into your work (a stopped conveyor with a loaded feeder above it).
2. **Take-up**: block or chain the **gravity take-up carriage** in its position (**never** stand under the counterweight; a take-up blocking procedure with rated chains/pins is part of the conveyor's lockout), or back off a screw take-up as the job needs; note that releasing tension on a belt that is being spliced can let the belt slide.
3. **Belt**: on an incline or a loaded belt, **clamp/chain the belt to the structure** on both sides of the work (belt clamps rated for the belt tension) before cutting or unbolting anything; a belt cut without clamps shoots up the loop or down the incline.
4. **Material**: empty the belt where practical; a chute full of material above the work is a stored load: block it or empty it.
5. **Hydraulic/pneumatic**: brakes, take-ups, cleaner tensioners bled and locked.
6. **Verify**: the belt does not move when the drive is pushed (the pull cord reset and a start attempted from the control room with everyone clear), the take-up is blocked, the belt is clamped; then the guards come off.
7. Restoring: guards on, clamps and blocks off in the right order (the take-up freed last, the belt tension restored slowly), people clear, the pre-start alarm, a start from the local control with a watch on the whole length.

See [lockout/tagout basics](/article/lockout-tagout-basics) for the general procedure.

## Working near running belts

- **Nothing** is done on a running belt: no cleaning of rolls or pulleys, no shovelling under a tail pulley, no freeing a stuck roll, no adjusting a cleaner or a skirt seal within reach of the belt, no lubricating a bearing on the pulley side without a remote fitting, no putting a hand through a guard; **tracking adjustments** on a running belt are done only on the idler bracket bolts from outside the guard on the walkway side, with no reach toward the belt or the roll.
- Loose clothing, long hair, drawstrings, lanyards, gloves near a moving belt are how people are caught: leathers tucked, no loose items.
- **Crossing**: only at **crossovers** (bridges with handrails) or where the conveyor is locked out; never step over or under a running belt, never through the structure; never on the belt.
- **Riding** a conveyor is prohibited everywhere (B20.1); people have been carried into transfer chutes and crushers.
- Shovelling spillage: from the walkway side, with the belt stopped where the spillage is within 3 ft of a pulley or a roll; a shovel drawn into a nip takes the arm.
- Tools and parts kept off the belt and the structure; a dropped wrench on a running belt goes into the crusher or comes back at you at a transfer.
- Cleaning **under** a running belt (the return strand overhead): only where there is a return roll guard and no reach to the belt; better locked out.

## Transfer points and dust

Falling material, rebounding lumps, blinding dust; head-pulley transfer chutes are an enclosed nip and a fall hazard when the cover is open. Chute inspection doors with guards; **plugged chute** detection; skirtboards and dust curtains; dust collection or suppression; on combustible dusts (coal, grain, sugar, wood, sulphur) the housekeeping, ignition-control and bearing-monitoring rules of NFPA 652/61/120 and the site's dust hazard analysis; a hot idler bearing under a coal belt starts the fire.

## Pre-start and inspection checklist

**Before starting (after work, or each shift)**: guards all on and secured; the pull cord intact, taut and tested; no tools, rags, or people on or under the belt; the belt clear of the structure; take-up free and its blocking removed; belt clamps off; chutes clear; the tracking check ready (a person at the tail and one at the head on a long belt); the pre-start alarm sounded; start locally with a stop at hand.

**Running inspection (from the walkway)**: rolls turning, no hot bearings (IR gun), the belt tracked within its edge limits, no belt damage or splice problems passing, no material build-up on pulleys, cleaners working, skirt seals not cutting the belt, no unusual noise, drift switches not tripped, the take-up in the middle of its travel, no spillage building up under the tail.

**Periodic**: guards' condition (bent, missing mesh, gaps), switch function tests (pull cords, drift, speed, plugged chute: monthly), walkway and handrail condition, lighting, the lockout points labelled, the take-up blocking devices present and rated, backstop function (on an incline: a watch when the belt is stopped loaded).

## Common mistakes

- "Just clearing the build-up off the tail pulley with a shovel while it runs": the most common conveyor fatality.
- Cutting a belt without clamps on an incline.
- Locking out the drive but not the upstream conveyor that feeds it; a start signal fills the chute over your head.
- A tail-pulley guard removed for a belt change and not put back for a month.
- Tying back a pull cord "because it keeps tripping".
- Crossing the belt at a low spot "just this once".
- Freeing a stuck return roll by hitting it with a bar while the belt runs: the bar goes into the nip and the roll comes out with it.

## Related

- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [Machine guarding and commissioning](/article/machine-guarding-and-commissioning)
- [Belt conveyor components and tracking](/article/belt-conveyor-components-and-tracking)
- [Belt splicing (blocking the take-up)](/article/belt-splicing)
- [Idlers, pulleys and lagging (roll changes)](/article/idlers-pulleys-and-lagging)
- [Fall protection, ladders and scaffolds](/article/fall-protection-ladders-scaffolds)
