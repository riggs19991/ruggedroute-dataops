---
title: "Bearing Defect Frequencies and Enveloping: BPFO, BPFI, BSF and FTF Formulas, the Quick Estimates, What Each Looks Like in a Spectrum, and Judging How Far Gone a Bearing Is"
slug: bearing-defect-frequencies-and-envelope
category: condition-monitoring
kind: reference
tags: [bearing defect frequencies, BPFO, BPFI, BSF, FTF, ball pass frequency, cage frequency, envelope spectrum, demodulation, gSE, HFD, spike energy, bearing fault stages, bearing vibration, non synchronous peaks, sidebands, bearing frequency calculator]
source: "SKF and Timken bearing frequency calculation guidance; Mobius Institute and Technical Associates vibration analysis references; ISO 13373."
summary: "The four bearing defect frequencies with the formula and the rules of thumb that get within a few percent without the bearing geometry, how outer race, inner race, roller and cage faults each appear in the velocity and envelope spectra, the four stages of bearing failure and the actions for each, and the pitfalls (wrong shaft speed, wrong bearing, sidebands mistaken for harmonics)."
---

> Bearing faults do not appear at multiples of shaft speed. They show up at **non-synchronous** frequencies (like 3.58× or 5.42× rpm) that are fixed by the bearing's geometry. Find those numbers for the bearing on the machine and the spectrum tells you which part of the bearing is damaged and how far along it is.

## The four frequencies

With **n** = number of rolling elements, **d** = ball or roller diameter, **D** = pitch diameter (average of bore and OD, roughly), **θ** = contact angle, and shaft speed **S** in Hz (rpm ÷ 60), for a rotating inner ring and a fixed outer ring:

![BPFO, BPFI, BSF and FTF with rule-of-thumb multiples](/img/condition-monitoring/bearing-defect-frequencies.svg)

*BPFO, BPFI, BSF and FTF with rule-of-thumb multiples*

| Fault | Name | Formula (multiples of S) | Quick estimate |
|---|---|---|---|
| Outer race defect | **BPFO** ball pass frequency, outer | (n ÷ 2) × (1 − d/D cos θ) | ≈ **0.4 × n** × rpm |
| Inner race defect | **BPFI** ball pass frequency, inner | (n ÷ 2) × (1 + d/D cos θ) | ≈ **0.6 × n** × rpm |
| Rolling element defect | **BSF** ball spin frequency | (D ÷ 2d) × (1 − (d/D cos θ)²) | ≈ 0.2 × n × rpm (2 × BSF is what usually shows) |
| Cage defect / cage rotation | **FTF** fundamental train frequency | (1 ÷ 2) × (1 − d/D cos θ) | ≈ **0.4** × rpm (0.38-0.45) |

BPFO + BPFI = n × S exactly. Example: 6310 (8 balls), shaft 1,780 rpm (29.67 Hz): BPFO ≈ 0.4 × 8 × 29.67 = **95 Hz** (3.2×); BPFI ≈ 0.6 × 8 × 29.67 = **142 Hz** (4.8×); FTF ≈ 12 Hz (0.4×). Exact values from the maker's calculator or the geometry: 6310 BPFO 3.05×, BPFI 4.95× (the estimate is within 5%). Roller bearings with many rollers (22220: 18 rollers) push BPFO up to about 7.5×.

Rules: if the **outer ring rotates** (wheel bearings, idlers on fixed shafts) swap the estimates (BPFO becomes the 0.6 one). Always confirm the bearing number on the machine or the drawing: the wrong bearing gives frequencies that fit nothing.

## What each fault looks like

| Fault | Velocity spectrum | Envelope (demodulated) spectrum | Time waveform |
|---|---|---|---|
| **Outer race** | Peaks at BPFO and its harmonics (2×, 3× BPFO); little sideband structure because the defect stays in the load zone | Clear BPFO harmonics; the earliest to show | Regular impacts at BPFO |
| **Inner race** | BPFI harmonics with **1× rpm sidebands** (the defect passes in and out of the load zone once per turn) | BPFI with 1× sidebands | Impacts modulated once per revolution (bursts) |
| **Roller / ball** | 2 × BSF (the flaw hits both races per spin) with **FTF sidebands** | 2 × BSF with FTF sidebands | Irregular impacts |
| **Cage** | FTF (0.4×) and its harmonics, often with looseness signs; fast failure | FTF | Erratic |
| **Lubrication starvation** | Broadband hash 1-20 kHz, no discrete peaks | Raised noise floor, no harmonics | Random |

**Enveloping** (also called demodulation, gSE, HFD, spike energy, PeakVue depending on the instrument) filters out the low-frequency running vibration and turns the tiny high-frequency impacts of an early bearing defect into a spectrum where BPFO or BPFI harmonics stand out months before the velocity spectrum shows anything. It is the tool for stage 1-2 detection; velocity is the tool for judging severity later.

## Stages of failure

| Stage | Signs | Time to failure (typical) | Action |
|---|---|---|---|
| **1** | Ultrasonic and envelope only; no change in overall velocity; bearing temperature normal | months (10-20% of remaining life) | Check lubrication; trend more often |
| **2** | Envelope harmonics clear; small defect peaks in velocity; slight rise in noise | weeks to months (5-10%) | Plan the replacement; order the bearing; check alignment and fits |
| **3** | Defect frequencies and harmonics with sidebands in velocity; overall rising; audible; temperature rising | days to weeks (1-5%) | Replace at the next opportunity; watch daily |
| **4** | Discrete peaks blur into a broadband "haystack"; 1× and harmonics rise (looseness as clearance opens); noise floor rises; temperature climbs; then the peaks may **drop** as the bearing smooths itself just before seizing | hours to days | Stop it before it seizes; a bearing that suddenly goes quiet after being noisy is about to fail |

## Reading tips

- Measure on the bearing housing in the load zone, radial direction, with the sensor stud- or magnet-mounted on clean metal; envelope readings need a high-frequency-capable sensor mount (a magnet on paint filters the impacts away).
- Same point, same speed, same load every time; a VFD-driven machine at a different speed moves every frequency: note the rpm and work in orders.
- Sidebands spaced at 1× rpm around a non-synchronous peak = inner race; spaced at FTF = rolling element; harmonics of a peak = the same defect, worse.
- Gear mesh and vane pass frequencies are synchronous (integer × rpm) and are not bearings; blade pass = number of blades × rpm.
- Confirm with temperature, ultrasound and, at replacement, [bearing failure analysis](/article/bearing-failure-analysis) so the cause is fixed.

## Common mistakes

- Wrong rpm (belt-driven fan speed is not motor speed: measure it with a strobe or tach).
- Wrong bearing number; two bearings of different types on one shaft (calculate both).
- Calling a 3× peak "misalignment" when it is BPFO at 3.05×: zoom in and check whether it is exactly synchronous.
- Ignoring stage 1 envelope warnings because the overall level is "fine".
- Re-greasing a stage 3 bearing and calling it fixed because the noise dropped for a day.

## Related

- [Vibration signatures](/article/vibration-signatures)
- [Vibration basics and ISO severity](/article/vibration-basics-and-iso-severity)
- [Thermography, ultrasound and oil analysis](/article/thermography-ultrasound-and-oil)
- [Bearing failure analysis (ISO 15243)](/article/bearing-failure-analysis)
- [Bearing designation codes](/article/bearing-designation-codes)
