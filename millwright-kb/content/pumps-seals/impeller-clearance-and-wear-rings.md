---
title: "Impeller Clearance and Wear Rings: Setting Open-Impeller Clearance on an ANSI Pump (Goulds 3196 Dial-Indicator and Feeler Methods, Temperature Correction Table), Reverse-Vane Impellers, Enclosed-Impeller Wear Ring Clearances (API 610 Table) and When to Renew Them, Effects of Clearance on Flow and Power, Re-Checking After Seal Work"
slug: impeller-clearance-and-wear-rings
category: pumps-seals
kind: procedure
manufacturer: "ITT Goulds / Flowserve Durco (generic ANSI B73.1)"
model_numbers: ["Goulds 3196", "Goulds 3196 i-FRAME", "Goulds 3175", "Durco Mark III", "Flowserve Mark 3", "Griswold 811", "Sulzer CPT"]
tags: [impeller clearance, impeller setting, open impeller, Goulds 3196 clearance, 0.015 impeller clearance, impeller clearance temperature, jack bolts bearing frame, dial indicator impeller, feeler gauge impeller, reverse vane impeller, Durco Mark 3, wear ring, wear ring clearance, API 610 wear ring, renew wear rings, enclosed impeller, pump efficiency clearance, pump vibration clearance, ANSI pump, B73.1]
source: "ITT Goulds Pumps Model 3196 i-FRAME IOM (impeller clearance setting: 0.015 in cold setting for ambient service with the temperature correction table, dial-indicator and feeler-gauge methods using the bearing housing jack bolts); Flowserve Durco Mark 3 IOM (reverse-vane impeller clearance set at the rear cover); API 610 (minimum running clearances for wear rings, Table 6); Hydraulic Institute pump efficiency guidance."
summary: "The clearance between an open impeller and the casing (or the wear rings of an enclosed impeller) is what keeps a centrifugal pump making its head: this covers how to set it on the standard ANSI pump with the bearing-frame jack bolts and a dial indicator, the cold setting and how much to add for hot liquid, the feeler-gauge method, the reverse-vane pump where it is done at the cover, the API 610 wear-ring clearance table and the rule for renewing rings, and why the clearance must be re-set after every seal change."
---

## Why it matters

In an **open-impeller** pump (ANSI B73.1 process pumps: Goulds 3196, Durco Mark 3 and their copies) the front of the impeller vanes runs a few thousandths from the casing (or the suction cover); liquid that slips back across that gap from the discharge side to the suction is lost work. As a rule of thumb, **doubling the design clearance drops the efficiency several points and the head a few percent**, raises the power, and moves the pump off its curve; too little clearance rubs when the pump warms up (galling, seizure, a broken shaft on start). The clearance wears open with abrasives and corrosion and is **re-set** (the impeller is moved forward) two or three times in its life before it needs replacing.

![Open impeller clearance and enclosed impeller wear rings](/img/pumps-seals/impeller-clearance.svg)

*Open impeller clearance and enclosed impeller wear rings*

In an **enclosed-impeller** pump (most API 610 and many water pumps) the same leakage path is sealed by **wear rings** (a replaceable ring on the impeller and/or the casing) running with a small radial clearance; you do not adjust it, you **renew the rings** when the clearance has grown.

## Goulds 3196-type: setting the impeller clearance

The bearing housing (frame) sits in the frame adapter on **jack bolts** (three or four, with lock nuts) that move the whole rotating assembly axially; the impeller clearance is set by moving the rotating element **toward the casing** until the impeller touches, then backing off by the setting.

**Cold settings (Goulds 3196 i-FRAME table, electric-motor driven, standard cast iron/ductile/steel/alloy casing)**:

| Pumped liquid temperature | Clearance (in) |
|---|---|
| −20 to 200°F (−29 to 93°C) | **0.015"** (0.38 mm) |
| 200 to 250°F (93-121°C) | 0.017" |
| 250 to 300°F (121-149°C) | 0.019" |
| 300 to 350°F (149-177°C) | 0.021" |
| 350 to 400°F (177-204°C) | 0.023" |
| 400 to 450°F (204-232°C) | 0.025" |
| 450 to 500°F (232-260°C) | 0.027" |
| 500 to 550°F (260-288°C) | 0.029" |
| 550 to 600°F (288-316°C) | 0.031" |

(About 0.002" per 50°F above 200°F. Larger frames and some materials in the IOM have a different table: the **XLT-X / X17** frames and CV/LF variants differ, and the 3196 sizes 1x1.5-4 and the CV 3196 use the feeler method or a different procedure; confirm on the table for your pump. Turbine-driven and high-speed pumps: see the IOM.)

**Dial-indicator method (all except the CV 3196, CV 3198 and LF 3196 1x1.5-4)**

1. Lockout; coupling disconnected (spacer out), the pump drained if hot work; **loosen the bearing-housing hold-down bolts** (the bolts that clamp the frame to the adapter, or the cap screws of the frame adapter, per the IOM; the frame must be free to move) and the jack-bolt **lock nuts**.
2. Mount a **dial indicator** on the frame adapter (or the casing) with the plunger on the **bearing housing** (or the shaft end), reading axial movement; zero it.
3. Back off the jack bolts a turn or two so the housing can move forward; **turn the shaft by hand** while **tightening the hold-down bolts / drawing the housing forward evenly** (the IOM: tighten the housing bolts in stages) until the **impeller just touches the casing** (you feel the drag in the shaft, and the indicator stops moving); zero the indicator here.
4. **Back the housing off with the jack bolts** by the clearance from the table (0.015" cold on ambient service), turning them **evenly** (a sixth of a turn each, round and round, or the indicator lies), until the indicator reads the setting; turn the shaft by hand: it should turn freely with no rub.
5. Tighten the **hold-down bolts** evenly, then the jack-bolt **lock nuts**, watching the indicator so the setting does not move (it will try to: tighten in a cross pattern and correct with the jacks); the final reading must be the table value ± 0.001-0.002".
6. Turn the shaft again; **re-check the shaft runout at the seal** (the seal's setting has just moved axially by the amount you moved the housing: a component seal must be re-set; a cartridge seal's setting clips go in only after this step). Reconnect the coupling, check alignment (the housing moved with respect to the motor by the same amount: usually inside tolerance, but check).

**Feeler-gauge method (casing removed, or through the suction on small pumps)**: with the rotating element free, push it toward the casing until it touches, then set the gap with a feeler gauge between the impeller vanes and the casing at several points while adjusting the jack bolts; lock as above. Used when the indicator cannot be mounted and on the sizes the IOM lists.

**When to re-set**: after every mechanical seal change (the housing is moved during seal work: set the impeller **first**, then set the seal); when the flow/head has dropped; after any bearing frame rebuild; when an impeller or casing is replaced; after the pump has run hot; on a PM, measure the clearance (touch and back off, read the indicator) and record it: 0.030" on a pump set at 0.015" a year ago is the wear rate.

## Reverse-vane impellers (Durco Mark 3 type)

The vanes are on the **back** of the impeller and run against the **rear cover (stuffing box cover)**, so the clearance is set between the impeller and the cover, from the **back** of the pump: the bearing frame is moved **away** from the casing to close the clearance, or the cover is shimmed, per the Flowserve IOM; the usual setting is also about **0.015"** cold with a similar temperature correction, and the seal is unaffected by wear adjustment on some designs because the cover moves with it: read the IOM, the direction is opposite to the Goulds and the numbers differ.

## Enclosed impellers: wear rings

Clearance is **diametral** (the difference in diameters between the ring on the impeller and the ring in the casing), measured with a micrometer on the impeller ring OD and a bore gauge on the casing ring ID (not with feelers in place, which read the radial gap on one side).

**API 610 minimum running clearance (new; diametral, for rings of the same material with a galling tendency, e.g. cast iron/bronze at ≤ 500°F)**:

| Ring diameter (in) | Minimum clearance (in) |
|---|---|
| < 2.000 | 0.010 |
| 2.000-2.499 | 0.011 |
| 2.500-2.999 | 0.012 |
| **3.000-3.499** | **0.014** |
| 3.500-3.999 | 0.016 |
| **4.000-4.499** | **0.016** |
| 4.500-4.999 | 0.016 |
| 5.000-5.999 | 0.017 |
| 6.000-6.999 | 0.018 |
| 7.000-7.999 | 0.019 |
| 8.000-8.999 | 0.020 |
| 9.000-9.999 | 0.021 |
| 10.000-10.999 | 0.022 |
| 11.000-11.999 | 0.023 |
| 12.000-12.999 | 0.024 |
| 13.000-13.999 | 0.025 |
| for each additional inch | +0.001 |

Add **0.005"** to these for materials that gall (stainless on stainless, hardened alloys), for temperatures over 500°F, and for services with solids; non-galling combinations (bronze/steel, PEEK or composite rings) can run **half** these values with the maker's approval. Water pumps and ANSI enclosed impellers typically run 0.010-0.020" on rings under 6".

**Renew the rings when the clearance reaches about twice the new value** (or the IOM's limit): performance falls (head down 5-10%), the pump vibrates (the rings damp the rotor: a worn ring set on a multistage pump raises vibration and can let the rotor rub), and power rises. Rings are pressed/shrunk and **locked** (set screws, tack welds, or grub screws at 120°), machined to size after fitting where the design says, and the impeller is re-balanced if a ring is replaced. Order rings by the pump's part number, or machine a bronze ring to the casing bore with the table clearance; the casing ring is fitted first, measured, then the impeller ring turned to suit.

## Effect of clearance on performance (the numbers you see on the gauges)

| Clearance | Head | Flow at the same head | Power | Notes |
|---|---|---|---|---|
| Design (0.015" open impeller) | 100% | 100% | 100% | |
| 2× design | 95-97% | 90-95% | 102-105% | Re-set / renew rings |
| 3× design | 90-93% | 80-90% | 105-110% | The pump has moved left on its curve; recirculation, heat, vibration |
| Rubbing (too little) | | | Spikes at start | Galling, seizure, broken shaft or coupling |

A pump "not making pressure" with no cavitation, correct rotation and a clean impeller is usually a clearance problem.

## Common mistakes

- Setting the clearance with the hold-down bolts loose and then torquing them: the setting moved 0.005".
- Jack bolts turned unevenly: the housing cocks, the impeller rubs on one side and the seal faces are cocked.
- Setting the seal before the impeller.
- Hot-service pump set at 0.015" cold: it rubs at temperature.
- Wear ring clearance measured with a feeler on one side (radial) and reported as diametral.
- New impeller ring on an old casing ring "to save a day": the clearance is still 0.030".
- Forgetting to re-check the coupling alignment after moving the housing 0.030" toward the casing during a wear adjustment.

## Related

- [Mechanical seal replacement (centrifugal pump)](/article/mechanical-seal-replacement-centrifugal-pump)
- [Pump packing and stuffing box](/article/pump-packing-and-stuffing-box)
- [Pump troubleshooting](/article/pump-troubleshooting)
- [Pump and fluid-power formulas (head, affinity laws)](/article/pump-and-fluid-power-formulas)
- [Dial indicator use](/article/dial-indicator-use)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
