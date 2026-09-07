---
title: "Work Orders and Equipment History: Writing a Work Order That Gets the Job Done, Recording the Repair, Failure Codes, MTBF and Using History to Stop Repeat Failures"
slug: work-order-and-history-records
category: maintenance
kind: reference
tags: [work order, CMMS, maintenance history, equipment history, failure code, MTBF, MTTR, root cause, RCA, 5 whys, repair report, as found as left, parts used, labor hours, backlog, priority, planning and scheduling, bad actor list, repeat failure]
source: "SMRP metrics (MTBF, MTTR, PM compliance); ISO 14224 (failure data collection); Doc Palmer, Maintenance Planning and Scheduling Handbook; common CMMS practice (SAP PM, Maximo, Fiix, Limble, eMaint)."
summary: "What goes in a good work order request and a good repair record, the as-found / as-left convention that makes history useful, failure codes and the simplest way to calculate MTBF and MTTR, how to run a quick root cause on a repeat failure, and the paperwork rules (parts, hours, lockout, permits) that protect the millwright as much as the machine."
---

> The repair you did not write down did not happen. Six months from now, when the same bearing fails again, the only thing that tells the next person (or you) what was found last time is the history. Fill it in like the reader is a stranger who has to fix it alone at 2 a.m.

## The work order request (what to write so the planner can plan it)

| Field | What good looks like |
|---|---|
| **Asset / tag number** | The equipment ID from the nameplate or tag ("P-2104 slurry pump B"), not "the pump by the stairs" |
| **Problem** | What you observed, with numbers: "DE bearing housing 195°F, was 150°F last route; growl audible; vibration 0.45 in/s (baseline 0.12)" |
| **Priority** | Safety / production down / production at risk / routine, per the site scale; not everything is a 1 |
| **Suspected cause** (optional) | "Bearing, possibly under-greased: fitting was dry" |
| **What is needed** | Lockout, permit (hot work, confined space), crane, scaffold, shutdown window, specialist |
| Photo | A picture of the leak, the reading or the damage saves a paragraph |
| Reporter and date/time | |

Planners turn this into a planned job: parts, tools, drawings, hours, safety plan. A request that says "pump noisy" gets a planner walking out to look, and a repair a week later.

## The repair record (closing the work order)

**As found / as left** is the convention that makes history useful:

```
As found:  DE bearing 6310 failed, outer race spalled 1/3 of circumference, grease hard
           and dark, seal lip worn. Shaft journal 1.9680" (nominal 1.9685-1.9690):
           0.0005" undersize, acceptable. Housing bore in spec. Alignment as found:
           0.012" offset vertical, 0.004"/in angular (out of tolerance).
Work done: Replaced both bearings (6310 2RS C3, SKF), new lip seals, cleaned housing,
           regreased 25 g Mobil Polyrex EM. Laser aligned to 0.001" offset / 0.0005"/in.
           Soft foot corrected with 0.010" shim under motor front left.
As left:   Ran 30 min: DE housing 128°F, vibration 0.09 in/s, no leaks. Guard refitted.
Parts:     2 x 6310 2RS C3; 2 x seal 45x62x8; 1 x shim pack.
Labour:    2 x 4.5 h. Downtime 6 h.
Failure code: Bearing / fatigue / lubrication (hard grease, over-interval).
Follow-up:  Regrease interval for P-2104 changed from 6 to 3 months (WO 44821 to update PM).
```

Rules:

- Record **measurements** (clearances, alignment readings, torques, temperatures, runout) with the units. "Aligned" is useless; "0.001 in offset" can be compared next time.
- Name the **part numbers and brands** actually fitted, and any substitution.
- Write what you **found**, not only what you did. The found condition is the failure evidence.
- Note anything left undone or that needs watching ("coupling insert worn, will need replacing at next shutdown").
- Attach photos of the failed part and the alignment report.
- Fill in labour hours and downtime honestly: they drive the budget for spares, training and the next overhaul.

## Failure codes

Most CMMS use a three-level code: **component** (bearing, seal, coupling, belt, gear, impeller, motor winding, hose) / **failure mode** (worn, fatigued, corroded, cracked, seized, leaking, loose, contaminated, overheated) / **cause** (lubrication, misalignment, unbalance, contamination, overload, installation error, age, design, operator). Picking the codes takes 20 seconds and lets someone sort the whole plant's history to find that 40% of bearing failures are "lubrication". Free text alone cannot be sorted. If your site has no codes, use those three words at the start of the free text.

## MTBF, MTTR and availability (the simple version)

```
MTBF (mean time between failures) = operating hours in the period ÷ number of failures
MTTR (mean time to repair)         = total repair (downtime) hours ÷ number of failures
Availability                        = MTBF ÷ (MTBF + MTTR)
```

Example: a conveyor drive runs 6,000 h in a year, fails 4 times, total downtime 32 h. MTBF = 1,500 h; MTTR = 8 h; availability = 1,500 / 1,508 = 99.5%. The number by itself means little; the **trend** (MTBF falling from 3,000 to 1,500 h) and the **comparison** between identical machines (pump A at 4,000 h, pump B at 900 h: what is different?) is where the work is. A "bad actor" list is simply the ten assets with the most work orders or downtime in the last year; fix the top three properly and the backlog shrinks.

## Repeat failures: a 20-minute root cause

When the same component fails a second time in a short period, do not just replace it again.

1. **Keep the failed part** and look at it with the failure-pattern guides: [bearings](/article/bearing-failure-analysis), [belts](/article/belt-failure), [seals](/article/seal-failure), [couplings](/article/coupling-failure), [gears](/article/gear-inspection-and-tooth-failure).
2. **Pull the history**: how long did the last one last, what was found, what was done, who did it, what changed (product, speed, a new motor, a VFD, a pipe rerouted).
3. **5 whys**: the bearing failed → why: the grease was hard → why: the interval was 6 months at 180°F → why: the interval came from the default, not the temperature → why: nobody recalculated it → fix: recalculate all hot-running motors' intervals, not just this one.
4. Check the **installation evidence**: was it aligned, was the fit measured, was the bearing heated correctly, was the torque right? Most "bad bearings" are installation or lubrication.
5. Write the finding into the work order and raise the **change**: a PM interval, a spec change, a spare, a training note, a modification. A root cause that changes nothing was a story.

## Paperwork that protects you

- Lockout: the lock, the tag and the verification are recorded on the permit or the work order (who, which energy sources, test-before-touch); see [lockout/tagout](/article/lockout-tagout-basics).
- Permits (hot work, confined space, work at height) attached to or referenced in the work order.
- Torque values and alignment reports attached for critical machines: they are the evidence that the job was done right when the machine later fails for a different reason.
- Parts issued against the work order (not "from the shelf"): it keeps the spares accurate and the cost against the right asset.
- Sign and date; if you were interrupted and the job is not finished, **say so on the machine (tag) and on the work order**.

## Building history on a plant that has none

Start with the critical assets: for each, one page with the nameplate data, bearing and seal numbers, belt sizes, oil type and quantity, alignment tolerance, coupling gap, spare part numbers, the last overhaul date, and a photo of the nameplate. Keep it in the CMMS or a shared folder named by the tag number. Every work order afterwards adds a line. In a year the millwright who wrote it will be the person everyone calls.

## Related

- [PM checklists](/article/pm-checklists)
- [Inspection routes](/article/inspection-routes)
- [Spare parts and bearing storage](/article/spare-parts-and-bearing-storage)
- [Bearing failure analysis](/article/bearing-failure-analysis)
- [Machine vibration, noise and heat decision tree](/article/machine-vibration-noise-heat-decision-tree)
