---
title: "Vibration Basics and ISO Severity: What Vibration Is and the Three Units (Displacement, Velocity, Acceleration), Overall vs Spectrum, Where and How to Take a Reading (Bearing Housing, Three Directions, Mounting), the ISO 20816-3 / 10816-3 Severity Zones Table with Machine Groups and Foundation Types, Bearing Condition Indicators (Enveloping, HFD, Spike Energy), Trending and Alarm Setting, Meters and Pens"
slug: vibration-basics-and-iso-severity
category: condition-monitoring
kind: chart
tags: [vibration, vibration analysis, vibration basics, vibration units, displacement mils, velocity in/s, velocity mm/s, acceleration g, overall vibration, vibration spectrum, FFT, vibration meter, vibration pen, ISO 10816, ISO 20816, vibration severity chart, vibration zones, zone A B C D, 0.1 in/s, 0.3 in/s, 2.8 mm/s, 4.5 mm/s, bearing housing measurement, horizontal vertical axial, accelerometer mounting, magnet mount, stud mount, enveloping, gSE, HFD, spike energy, bearing condition, vibration trending, vibration alarm, condition monitoring route]
source: "ISO 20816-3:2022 (superseding ISO 10816-3): vibration severity zones for industrial machines 15 kW-50 MW, groups 1-2, rigid and flexible supports, and the pump group values; ISO 10816-7 (pumps); Mobius Institute and Vibration Institute training material (units, measurement practice, bearing condition indicators); SKF, Emerson/CSI and Fluke vibration meter documentation."
summary: "The measurements a millwright takes with a vibration meter or a route collector and what the numbers mean: the three units and when each is used, why overall velocity is the severity number and the spectrum is the diagnosis, how to take a repeatable reading on a bearing housing, the ISO zone table that says whether a machine is good, acceptable, marginal or in trouble, the high-frequency indicators that catch bearing damage months before the overall moves, and how to set alarms and trend."
---

## What you are measuring

A rotating machine shakes at the frequencies of the things that are wrong with it: unbalance at the shaft speed (1×), misalignment at 2×, a bearing defect at the defect's frequency, gear mesh at teeth × rpm. A sensor on the bearing housing measures the housing's motion; the meter reports it as an **overall** (one number: the total vibration in a frequency band) or as a **spectrum** (FFT: the vibration at each frequency, which is where the diagnosis is: see [vibration signatures](/article/vibration-signatures)).

| Unit | What it is | Best for | Typical values |
|---|---|---|---|
| **Displacement** (mils peak-to-peak, µm) | How far it moves | Low speeds (under 600 rpm), shaft proximity probes on sleeve-bearing machines (turbines, compressors), structural motion | A 1,800 rpm pump at 0.15 in/s ≈ 1.6 mils p-p |
| **Velocity** (in/s peak or mm/s RMS) | How fast it moves | **The severity unit for 600-60,000 cpm (10-1,000 Hz)**: the ISO standards use **mm/s RMS** (1 in/s peak = 25.4 mm/s peak = **18 mm/s RMS**); most US meters read in/s peak, most standards in mm/s RMS: convert | Good machine: under 0.1 in/s pk (1.8 mm/s RMS); trouble: over 0.3 in/s pk (5.4 mm/s RMS) |
| **Acceleration** (g's RMS or peak) | The rate of change of velocity | High frequencies (bearings, gear mesh, cavitation), over 1,000 Hz | Bearing indicators |

Velocity is used for severity because it relates to the fatigue energy in the machine roughly equally across the speed range. **Peak vs RMS**: RMS is 0.707 × peak for a pure sine; meters and standards must be compared in the same convention (a reading of 0.2 in/s peak is 0.14 in/s RMS = 3.6 mm/s RMS).

## Taking the reading

- **Where**: on the **bearing housing**, as close to the bearing as possible, on a **rigid** part of the housing (not a cover, a fin, a guard, or the motor's sheet-metal fan shroud); the same spot every time (a paint dot, a stud, or a marked pad); on a motor: both bearings; on a pump: both bearings of the bearing frame; on a gearbox: each bearing position on the case; on a fan: the bearing pedestals.
- **Directions**: **horizontal (H)**, **vertical (V)** and **axial (A)** at each bearing (radial readings for unbalance and looseness, axial for misalignment and bent shafts); the H/V ratio itself tells things (a horizontal reading much higher than vertical is normal on a foot-mounted machine: the base is stiffer vertically; equal or higher vertical hints at looseness or a base problem).
- **Mounting**: a **stud** on a machined pad (the best, to 10 kHz+), a **magnet** on a flat clean steel spot (good to 2-5 kHz on a strong flat magnet; a curved or painted surface halves the useful range and ruins bearing readings), a **hand-held probe** (only for overall readings under 1,000 Hz; presses vary, the reading varies ±20%); a **vibration pen** is a hand-held probe with a display. For bearing indicators (enveloping, HFD) use a magnet or a stud on a flat spot, never a probe.
- **Conditions**: the machine at its normal load and speed and warmed up; note the speed and load (a pump at low flow vibrates more: it is not a machine fault); the reading taken after the sensor settles (a few seconds); the same meter settings each time (the frequency range, RMS/peak, the averaging).
- **Safety**: from outside guards; never a probe near a coupling or a belt; a route with clip-on sensors on inaccessible or hot points; hearing and eye protection as for the plant.

## ISO 20816-3 severity zones (industrial machines 15 kW to 50 MW, measured on bearing housings, velocity mm/s RMS, 10-1,000 Hz)

**Zones**: **A** = new-machine condition; **B** = acceptable for unrestricted long-term operation; **C** = unsatisfactory for continuous long-term operation, run for a limited time until repair; **D** = severe enough to cause damage.

| Machine group and support | Zone A/B boundary | Zone B/C boundary | Zone C/D boundary |
|---|---|---|---|
| **Group 1: large machines, 300 kW to 50 MW (motors with shaft height over 315 mm), rigid foundation** | 2.3 mm/s (0.09 in/s RMS) | **4.5 (0.18)** | 7.1 (0.28) |
| Group 1, flexible foundation | 3.5 (0.14) | 7.1 (0.28) | 11.0 (0.43) |
| **Group 2: medium machines, 15 to 300 kW (motors with shaft height 160-315 mm: most plant pumps, fans, blowers, compressors), rigid foundation** | **1.4 (0.055)** | **2.8 (0.11)** | **4.5 (0.18)** |
| Group 2, flexible foundation | 2.3 (0.09) | 4.5 (0.18) | 7.1 (0.28) |
| Pumps over 15 kW with a separate driver (ISO 20816-3 group 3/ISO 10816-7 category), rigid | 2.3 | 4.5 | 7.1 |
| Pumps with an integrated driver (close-coupled), rigid | 3.2 | 6.3 | 10.0 |
| Pumps, flexible support | 3.2-4.5 | 7.1-9.0 | 11.0-14.0 |

(In/s **peak** ≈ mm/s RMS × 0.056; so Group 2 rigid: A/B 0.08, B/C **0.16**, C/D **0.25 in/s peak**. Many US plants use a simpler rule from the old general severity chart: **under 0.1 in/s pk good, 0.1-0.2 fair, 0.2-0.4 rough, over 0.4 in/s pk very rough**; a new installation should be under 0.1 in/s pk / 1.8 mm/s RMS.)

**Rigid vs flexible support**: rigid = the machine's mounting natural frequency is above its running speed (a machine bolted to a heavy grouted base); flexible = the natural frequency is below (a machine on isolators, a light steel frame, a tall pedestal); most plant pumps and motors on grouted baseplates are rigid; fans on spring isolators and machines on mezzanines are flexible. When in doubt, use the rigid (stricter) limits.

The standard adds: an **increase** in vibration of more than 25% of the zone B upper limit between readings is an alarm even if the machine is still in zone B; the zones are guidance, and the machine's own baseline and history matter.

Small machines (under 15 kW) and special machines (reciprocating compressors, hammer mills, crushers) have other standards or the maker's limits; a reciprocating compressor at 10 mm/s can be normal.

## Bearing condition indicators (the early warning)

A rolling-element bearing defect is a tiny impact at a high frequency long before it shows in the overall velocity; the meters give a separate number for it:

| Indicator | What it measures | Reading it |
|---|---|---|
| **Enveloping / demodulation (gE, gSE, HFE, PeakVue (Emerson), BCU, SEE (SKF))** | The repetitive impacts in a high-frequency band, demodulated so the bearing's defect frequency appears | Trend: the number rises as the defect grows, then can **fall** near the end (the defect smooths) while the overall velocity rises; compare with the same meter's guidance (e.g. gE: under 1 good, 1-3 watch, over 3 damage, on a stud/magnet mount at typical speeds; the values depend on speed, mount and the meter: **trend the machine against itself**) |
| **HFD / spike energy (gSE), Shock Pulse (SPM dBm/dBc)** | High-frequency acceleration bursts | Same use; SPM's dBm scale has fixed condition zones (green/yellow/red) after entering the bearing and speed |
| **Crest factor** (peak ÷ RMS of acceleration) | Impulsiveness | Rises in the early bearing stage (3-4 normal, 6+ impacts), falls late |
| **Acceleration overall (g RMS, 1-10 kHz)** | Total high-frequency energy | Rises with bearing wear, lubrication starvation (a dry bearing is very noisy at high frequency and falls when greased: the greasing-by-vibration/ultrasound method), gear wear, cavitation |
| **Temperature** at the housing | | Confirms; a late indicator |

A bearing with a rising envelope reading and a flat overall is in the **early** stage (weeks to months); when the overall velocity rises and bearing frequencies with harmonics and sidebands appear in the spectrum, it is **late** (days to weeks); noise, heat and a falling envelope with high overall: **replace now**.

## Alarms and trending

- **Baseline** every machine at commissioning (see [commissioning](/article/machine-guarding-and-commissioning)) and after every repair: overall in 3 directions per bearing, the bearing indicator, and a spectrum saved.
- **Alert** at about **2× the baseline** or the zone B/C boundary, whichever is lower; **alarm** at the zone C/D boundary or 3-4× baseline; and a **rate-of-change** alert (a 25-50% rise since the last reading).
- Route frequency: critical machines monthly (or online), general monthly-quarterly, a machine on alert weekly; the route is a list of the same points in the same order with the same settings; the CMMS or the vibration software trends each point.
- Report: the machine, the point and direction, the overall now vs baseline vs alarm, the bearing indicator, what the spectrum shows (from [signatures](/article/vibration-signatures)), and the recommended action with the urgency (a zone C machine is planned; a zone D machine is scheduled now or stopped).
- Correlate: temperature, oil analysis, ultrasound, the process (flow, load), recent work (alignment, a belt change).

## Meters

- **Vibration pen / simple meter**: overall velocity (and sometimes acceleration/bearing) in a fixed band; for go/no-go on the route, the commissioning check, and confirming a hunch; the readings must be taken the same way every time to trend.
- **Route data collector / analyser** (Emerson CSI, SKF Microlog, Pruftechnik, Fluke 810, Adash): spectra, enveloping, time waveforms, phase (with a tach), the route database; the vibration technician's tool; a millwright with training can run routes.
- **Online systems** (wireless sensors, permanent monitors) on critical machines with alarms to the control room.
- Care: the sensor's cable strain-relieved, the magnet clean, the calibration checked annually, the battery.

## Worked example

A 75 hp (56 kW) 1,800 rpm end-suction pump on a grouted baseplate (Group 2, rigid): baseline at commissioning 0.06 in/s pk (1.1 mm/s RMS) horizontal at the pump inboard bearing. Six months later the route reads 0.14 in/s pk (2.5 mm/s RMS): still zone B, but 2.3× the baseline: alert; the spectrum shows a 2× running speed peak and a high axial reading: misalignment (the pipe was changed last month); action: check the pipe strain and re-align before it reaches zone C (0.16 in/s pk). The bearing envelope reading at 0.8 gE, unchanged: the bearings are still fine.

## Common mistakes

- Comparing a peak reading from one meter with an RMS limit from the standard: a factor of 1.4.
- A magnet on the motor's fan cover: the reading is the cover's rattle.
- Readings at different loads and speeds trended as one line.
- Alarms set only on the overall: the bearing is gone before the overall moves.
- "It's in zone B, leave it" on a machine that tripled since last month.
- Greasing a bearing because it is noisy on the ultrasound, without knowing whether it is starved or damaged (a damaged bearing quiets briefly when greased too).

## Related

- [Vibration signatures (unbalance, misalignment, looseness, bearings, gears, electrical)](/article/vibration-signatures)
- [Thermography, ultrasound and oil](/article/thermography-ultrasound-and-oil)
- [Machine guarding and commissioning (acceptance)](/article/machine-guarding-and-commissioning)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals)
- [Bearing failure analysis](/article/bearing-failure-analysis)
- [PLC and instrumentation awareness (vibration transmitters)](/article/plc-and-instrumentation-awareness)
