---
title: "MIG Transfer Modes: Short-Circuit, Globular, Spray and Pulsed Spray, with Transition Currents, Gas Requirements and Settings"
slug: gmaw-transfer-modes
category: welding
kind: reference
tags: [transfer modes, short circuit transfer, globular transfer, spray transfer, pulsed spray, transition current, spray arc settings, 90/10, 98/2, argon oxygen, metal-cored wire, keyhole, burn through, GMAW-P, GMAW-S, synergic pulse]
source: "Hobart Brothers / Welding Journal, 'Selecting the Right Welding Transfer Modes' (Aug 2021); AWS Welding Handbook Vol. 2 (transition current table); Lincoln Electric GMAW guide; Miller pulsed MIG guides."
summary: "What each transfer mode is, when it happens, what gas and current it needs, what it is good and bad at, the transition currents where spray begins for each wire size, and starting settings for short-circuit, spray and pulse."
---

## The four modes at a glance

![Short-circuit, globular, spray and pulsed spray with the transition current](/img/welding/mig-transfer-modes.svg)

*Short-circuit, globular, spray and pulsed spray with the transition current*

| Mode | How metal crosses the arc | Current / voltage | Gas | Positions | Thickness | Spatter |
|---|---|---|---|---|---|---|
| **Short-circuit (GMAW-S)** | Wire touches the puddle 90-200 times/s; each short melts off a droplet | Low: roughly 40-200 A, 14-22 V | C25, 100% CO2, tri-mix for stainless | **All** | Sheet to 1/8" ideal; thicker with care (lack of fusion risk) | Some |
| **Globular** | Large irregular drops, bigger than the wire, fall by gravity | Medium-high, above short-circuit but below spray; CO2 or C25 above ~200 A | 100% CO2, C25 | Flat and horizontal | 1/8" and up | Heavy |
| **Spray (axial spray)** | Fine droplets smaller than the wire stream across a stiff, hissing arc | High: above the **transition current**, 24-32 V | **≥ 80% argon** (90/10, 95/5, 98/2) | Flat and horizontal only (puddle too fluid otherwise) | 1/8" and up; ideal 1/4" and thicker | Very little |
| **Pulsed spray (GMAW-P)** | Power source pulses 30-400 times/s between a peak (spray droplet) and a low background current | Average current below the transition current | ≥ 80% argon | **All** | 18 ga to heavy plate | Very little |

## Short-circuit transfer

![Short-circuit transfer is the mode for out-of-position work like this overhead weld](/photos/welding/mig-overhead.jpg)

*Short-circuit transfer is the mode for out-of-position work like this overhead weld. Photo: Prowelder87, CC BY-SA 4.0, via commons*

- The everyday shop mode with .030/.035 wire and C25. Low heat input, all positions, bridges gaps.
- Needs a tight consistent stickout (3/8-1/2") because it runs cold.
- Weakness: **lack of fusion** on thick plate. Many fabricators limit GMAW-S to 3/16" or require a qualified procedure above that. AWS D1.1 treats short-circuit GMAW as needing procedure qualification.
- Inductance/"arc control" knob: higher inductance = smoother, wetter, fewer shorts per second and less spatter; lower = crisper, colder, more shorts. Set for the least spatter with a flat bead.
- Settings: see the [MIG setup chart](/article/gmaw-mig-setup).

## Globular transfer

- Happens with CO2 (any current) and with C25 when you turn the WFS and voltage up past short-circuit without enough argon to spray. The drop wobbles, the arc pops, spatter flies.
- Used deliberately with gas-shielded flux-core (E71T-1 on CO2) and 100% CO2 solid wire for cheap, deep-penetrating flat and horizontal welds on 1/8" and thicker.
- Stickout 3/4-1". Expect cleanup.
- If you are getting globular on C25 by accident, you are in the no-man's-land between 180-220 A: go down into short-circuit or change to 90/10 and go up into spray.

## Spray transfer

Spray starts when the current exceeds the **transition current** for that wire and gas. Below it the arc is globular; above it the arc goes quiet and hisses, the puddle wets out, and the bead is smooth and flat.

Transition currents (AWS Welding Handbook typical values; confirm on your machine):

| Wire | Gas | Transition current |
|---|---|---|
| Mild steel .023" | 98% Ar / 2% O2 | ~135 A |
| Mild steel .030" | 98/2 | ~150 A |
| Mild steel **.035"** | 98/2 | **~165 A** (about 175-190 A in 90/10 Ar-CO2) |
| Mild steel **.045"** | 98/2 | **~220 A** (about 230-240 A in 90/10) |
| Mild steel 1/16" | 98/2 | ~275 A |
| Stainless .035" | Ar / 1-2% O2 | ~170 A |
| Stainless .045" | Ar / 1-2% O2 | ~225 A |
| Aluminium .030" | 100% Ar | ~95 A |
| Aluminium 3/64" | 100% Ar | ~135 A |
| Aluminium 1/16" | 100% Ar | ~180 A |

More CO2 in the mix raises the transition current; above ~20-25% CO2 spray does not happen at all, which is why C25 cannot spray.

**Starting settings, steel, 90/10 Ar-CO2, flat fillet**

| Wire | WFS (ipm) | Voltage | Approx. amps | Stickout |
|---|---|---|---|---|
| .035" | 380-500 | 24-28 V | 190-250 | 1/2-3/4" |
| **.045"** | **350-450** | **26-29 V** | **250-320** | 3/4" |
| .052" | 300-400 | 28-31 V | 300-380 | 3/4-1" |
| 1/16" | 250-350 | 29-32 V | 350-450 | 1" |

Technique: push 5-10°, tip recessed 1/8" in the nozzle, keep the arc on the leading edge, travel fast enough that the puddle does not pile up. Spray on 3/16" plate is fine for fillets; on thinner material it burns through. Not usable vertical or overhead (except very small fillets by expert hands); use pulse.

Metal-cored wire (E70C-6M) runs in spray at similar voltages with a wider, softer arc and higher deposition; it is the production choice for flat fillets.

## Pulsed spray (GMAW-P)

- Requires a pulse-capable inverter (Millermatic 350P, Power MIG 350MP, Fronius, etc.). You pick wire, gas and diameter; the machine runs a synergic program: one knob for WFS and a "trim"/arc length adjustment.
- Gives spray-quality welds **out of position** and on **thin material** because the average current is low while each peak still pinches off a spray droplet.
- Aluminium: pulse is the preferred MIG mode (less burn-through, better control). Stainless: less heat tint. Steel: 3/16"+ vertical-up with .045 at fast travel.
- Stickout 3/4". Same ≥ 80% argon gases as spray.
- Typical .045 steel pulse: 200-400 ipm, trim 1.0, arc length adjusted by the bead.

## Choosing quickly

| You are welding… | Use |
|---|---|
| 24 ga-1/8" sheet, any position | Short-circuit, .030/.035, C25 |
| 3/16"-1/4" fillets flat/horizontal | Spray .045 90/10, or short-circuit .035 hot with a qualified procedure |
| 1/4" and up, flat/horizontal, production | Spray or metal-cored, or FCAW-G |
| 3/16" and up, vertical/overhead | Pulse .045, or FCAW-G E71T-1, or 7018 |
| Aluminium 1/8" and up | Spray (spool gun, 100% Ar) or pulse |
| Aluminium under 1/8" | Pulse, or TIG |
| Stainless sheet | Short-circuit with tri-mix, or pulse with Ar-2% O2 |

## Keyholing and burn-through in MIG

"Keyhole" in the MIG sense means the arc has cut a hole through the joint that the puddle then fills as you move: it is a **fault** on sheet (burn-through) and a sign you are too hot, too slow, or the gap is too wide. On open-root plate welds a deliberate small keyhole with short-circuit or pulse gives full-penetration roots; keep it the size of the wire diameter and move steadily. (Keyholing as a **cutting** technique belongs to plasma: see [plasma keyholing and piercing](/article/plasma-keyholing-and-piercing).)

## Related

- [MIG setup and settings chart](/article/gmaw-mig-setup)
- [Shielding gas selection and flow](/article/gas-selection-and-flow)
- [Welding aluminium](/article/welding-aluminium)
- [Gas-shielded flux-core setup](/article/fcaw-gas-shielded-setup)
