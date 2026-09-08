---
title: "Vibration Signatures: Reading a Spectrum for Unbalance, Misalignment, Bent Shaft, Looseness (Three Types), Rolling Bearing Defects and Their Frequencies, Sleeve Bearing Oil Whirl, Gear Mesh and Gear Faults, Belt Drives, Electrical Faults (Rotor Bars, Stator, VFD), Resonance, Cavitation and Flow, Soft Foot and Pipe Strain, with a Symptom-to-Cause Table and the Confirming Tests"
slug: vibration-signatures
category: condition-monitoring
kind: reference
tags: [vibration signatures, vibration spectrum, vibration diagnosis, unbalance vibration, 1x, misalignment vibration, 2x, axial vibration, bent shaft, looseness vibration, harmonics, half harmonics, bearing defect frequency, BPFO, BPFI, BSF, FTF, bearing vibration, oil whirl, gear mesh frequency, sidebands, belt vibration, belt frequency, electrical vibration, 120 Hz, rotor bar, pole pass frequency, 2x line frequency, resonance, natural frequency, bump test, cavitation vibration, blade pass frequency, vane pass, soft foot vibration, phase analysis, vibration troubleshooting chart]
source: "Vibration Institute and Mobius Institute (ISO 18436 Category I/II) course material; Technical Associates of Charlotte 'Illustrated Vibration Diagnostic Chart'; SKF and Emerson/CSI application notes on bearing defect frequencies and enveloping; EASA guidance on electrically induced vibration; ISO 20816-3."
summary: "The patterns in a vibration spectrum that point to each machine fault, with the frequencies, the directions and the shape to look for, the confirming test that separates look-alikes (unbalance from misalignment from resonance, mechanical from electrical), the bearing defect frequency formulas, and a table from the symptom to the cause that a millwright can use with a route analyser or a good vibration meter with a spectrum display."
---

## Reading a spectrum

The spectrum shows amplitude (velocity, mm/s or in/s) against frequency (Hz, or cpm, or **orders**: multiples of the shaft speed, 1× = running speed). Faults are recognised by **which orders** are present, their **relative size**, the **direction** (horizontal, vertical, axial), the **harmonics** (2×, 3×...), the **sidebands** (peaks spaced at another frequency around a main peak: modulation), the **noise floor** (a raised floor = randomness: looseness, cavitation, late bearing damage), and the **phase** (the timing of the 1× vibration between points, measured with a tachometer reference or a two-channel analyser: the tie-breaker between unbalance, misalignment, bent shaft and looseness).

Set the spectrum's maximum frequency to cover what you look for: **10× running speed** for the mechanical faults (unbalance to looseness), **higher** (to 3-10 kHz or a high-frequency band) for bearings and gear mesh; resolution fine enough (1,600-3,200 lines) to separate 2× running speed from 2× line frequency on a 2-pole motor (3,580 rpm × 2 = 7,160 cpm vs 7,200 cpm: 40 cpm apart).

## The signatures

![Spectrum shapes for unbalance, misalignment, looseness and bearing defects](/img/condition-monitoring/vibration-signatures.svg)

*Spectrum shapes for unbalance, misalignment, looseness and bearing defects*

### Unbalance

- **1× dominant**, radial (horizontal usually higher than vertical on a foot-mounted machine), **low axial**, a clean single peak, amplitude rising with the **square of the speed** (a VFD-driven fan doubles its 1× four times going from half to full speed).
- Phase: horizontal and vertical at the same bearing **90° apart**; the two bearings **in phase** for static unbalance (a heavy spot: a fan with build-up), **out of phase** for couple unbalance (a long rotor).
- Causes: build-up (fans, impellers), erosion, a lost balance weight, a bent blade, a key too long or missing, an eccentric sheave.
- Confirm: the fan/impeller cleaned and the reading repeated; a field balance (a two-plane balance with the analyser).
- Not unbalance if: axial is high (misalignment or bent shaft), it does not change with speed squared (resonance), there are harmonics (looseness).

### Misalignment

- **Angular**: high **axial** 1× (and 2×), the axial at the two sides of the coupling **180° out of phase**.
- **Parallel (offset)**: high **radial 2×** (often 2× larger than 1×), the radial readings across the coupling 180° out of phase.
- Usually both: **1×, 2× and sometimes 3×** with a strong 2× and a high axial; the 2× shows on both machines; a **coupling** with a worn element or a locked gear/grid coupling adds harmonics to 4× or more.
- Causes: alignment, **thermal growth** not allowed for (the machine aligned cold and running hot), **pipe strain**, **soft foot**, a bearing housing moved, a coupling worn.
- Confirm: alignment check hot and cold; loosening the pipe flanges with indicators on the shaft ([pipe strain](/article/pipe-strain-and-flange-alignment)); a coupling inspection.

### Bent shaft

- High **axial 1×** (and 2× if bent near the coupling), radial 1×; the axial phase at the two ends of the same machine **180° out of phase** (one bearing pushes while the other pulls); like unbalance in the radial and misalignment in the axial.
- Confirm: dial indicator runout on the shaft (see [bearing removal](/article/bearing-removal-pullers-and-heating) for the shaft check) and on the coupling hub.

### Looseness

| Type | Signature | Cause |
|---|---|---|
| **Structural / base (type A)** | High **1×**, mostly **vertical** (V equal to or higher than H, unusual), sometimes 2×; the phase between the foot and the base differs (a foot that lifts) | Loose hold-down bolts, a cracked base or grout, **soft foot**, a broken weld on a pedestal, a rotten foundation |
| **Mechanical looseness at the machine (type B)** | 1×, 2× and higher, with **sub-harmonics (0.5×, 1.5×)** and the harmonics **directional** | A loose bearing housing cap, loose pillow block bolts, a cracked frame, a rocking pedestal |
| **Rotating looseness (type C)** | **Many harmonics** of 1× (up to 10× and more), often with **half-orders (0.5×, 1.5×, 2.5×)**, a raised noise floor; the phase unstable | A bearing loose in its housing or on the shaft (the fit gone), excessive bearing clearance, a loose impeller or rotor on the shaft, a loose coupling hub or sheave |

Confirm: a bolt check with a wrench, the fits (see [bearing fits](/article/bearing-clearance-and-fits-tables)), a look at the base, a soft-foot check with the indicator.

### Rolling-element bearing defects

A defect on a race or a roller generates impacts at a **defect frequency** that is not a whole multiple of the shaft speed (the give-away: non-synchronous peaks):

```
   n = number of rolling elements, d = element diameter, D = pitch diameter, θ = contact angle, f = shaft speed
   BPFO (outer race, ball pass frequency outer) ≈ (n/2) × f × (1 − (d/D) cos θ)      ≈ 0.4 × n × f
   BPFI (inner race)                            ≈ (n/2) × f × (1 + (d/D) cos θ)      ≈ 0.6 × n × f
   BSF  (ball/roller spin)                      = (D/2d) × f × (1 − ((d/D) cos θ)²)
   FTF  (cage, fundamental train)               ≈ (f/2) × (1 − (d/D) cos θ)          ≈ 0.4 × f
```

A 6309 (8 balls) at 1,800 rpm (30 Hz): BPFO ≈ 0.4 × 8 × 30 = **96 Hz (3.2×)**, BPFI ≈ 0.6 × 8 × 30 = **144 Hz (4.8×)**; the bearing makers publish exact frequencies for each bearing number; the analyser's database has them.

**Stages**: (1) ultrasonic/high-frequency only (enveloping, HFD, gE rise); (2) the defect frequencies appear in the envelope spectrum and the acceleration spectrum with harmonics; (3) the defect frequencies and their harmonics in the **velocity** spectrum, with **sidebands at 1×** (an inner race defect: it passes through the load zone once a revolution) or at FTF (a cage/roller defect); the overall rises; (4) the discrete peaks smear into a raised **noise floor** with random broadband vibration and the envelope falls: replace immediately.

Confirm: the envelope spectrum shows the defect frequency; temperature; the grease condition; the history (see [bearing failure analysis](/article/bearing-failure-analysis)). Electrical fluting shows as the bearing frequencies plus a "haystack" at high frequency.

### Sleeve (journal) bearings

- **Oil whirl**: a sub-synchronous peak at **0.42-0.48×** (the oil wedge spinning the shaft in the clearance), on pressure-lubricated sleeve bearings at high speed (turbines, compressors, large motors): unstable, changes with load and oil temperature; **oil whip** locks it at the rotor's natural frequency: dangerous. Fix: bearing clearance, oil viscosity/temperature, preload, a different bearing design.
- Excessive clearance: 1× with harmonics and 0.5× (like looseness).
- Rubs: harmonics, sub-harmonics (1/2×, 1/3×), a truncated time waveform.

### Gears

- **Gear mesh frequency (GMF) = teeth × rpm** of that gear (the same for both gears in the mesh), with its harmonics, always present at some level; the amplitude rises with load and wear.
- **Sidebands** around the GMF spaced at the **rpm of the damaged gear** tell which gear (the pinion's speed spacing = the pinion); many sidebands with growing amplitude = a worn or eccentric gear, a cracked or broken tooth (the tooth also shows as a 1× of that gear and an impact in the time waveform once per revolution).
- **Gear natural frequency** excited by wear: a hump with sidebands.
- **Hunting tooth frequency** (very low: the frequency at which the same two teeth meet) = a pair of damaged teeth.
- Misaligned gears: GMF harmonics (2×, 3× GMF) higher than the fundamental; the pattern across the face confirms ([gear inspection](/article/gear-inspection-and-tooth-failure)).
- Backlash/looseness in a gear train: a 1× of the gear with GMF sidebands and a high noise floor at low load.

### Belt drives

- **Belt frequency** = belt speed ÷ belt length (below the shaft speeds: a sub-synchronous peak, and its harmonics; a worn or defective belt shows at 2×, 3× and 4× belt frequency, with the 2× often highest); belt frequency (Hz) = π × sheave PD (in) × sheave rpm ÷ (60 × belt length (in)).
- **Sheave misalignment**: high **axial 1×** of the driver or the driven sheave.
- **Eccentric sheave**: 1× of that sheave, radial, in line with the belts (measure in the direction of the belt tension).
- Belt resonance: a belt flapping at its natural frequency (change the tension).
- **Over-tension**: high bearing loads and bearing frequencies.
- Confirm: a strobe on the belt (the belt frequency and the flapping), a straightedge on the sheaves, a tension check.

### Electrical (induction motors)

- **2× line frequency (120 Hz at 60 Hz)**: stator problems (a soft foot distorting the stator, loose laminations, an eccentric air gap, a shorted stator winding), unbalanced supply voltage; it **disappears the instant the power is cut** (the test: take a reading, kill the motor, watch the peak vanish; mechanical vibration decays with speed).
- **Pole-pass sidebands** (the slip frequency × the number of poles, a few Hz) around 1× and its harmonics: **broken/cracked rotor bars** or a bad rotor joint (also a **beating** sound and a current swing under load); worse under load.
- **Rotor bar pass frequency** (bars × rpm) with 2× line-frequency sidebands: loose rotor bars, a rotor eccentricity.
- **Eccentric rotor** (an air gap that varies): 2× line frequency with pole-pass sidebands; a bent motor shaft or worn bearings.
- **VFD-driven motors**: peaks at the drive's switching/carrier frequency and its harmonics (normal, high frequency), and the 2× line-frequency signatures at 2× the drive's output frequency (not 120 Hz); plus the bearing fluting signatures.
- Confirm: the power-off test; a current analysis (MCSA) for rotor bars; the motor shop.

### Resonance

- A peak that does not follow the rules: a 1× that is huge in **one direction only**, an amplitude that changes drastically with a small speed change (the VFD), a machine that vibrates at a speed during coast-down; the structure or the piping has a **natural frequency** near the running speed (or the blade pass, or the mesh); the phase shifts 180° through the resonance.
- Confirm: a **bump test** (the machine stopped, hit the structure with a soft hammer and read the frequency it rings at with the analyser in a peak-hold mode), a **coast-down** (peak-hold during the run-down: the peaks at the natural frequencies), a run-up.
- Fix: change the stiffness (a brace, a gusset, a thicker base), the mass, or the speed (a skip frequency on the VFD); detune the piping (supports).

### Flow, cavitation and aerodynamic

- **Blade/vane pass frequency (BPF) = blades × rpm** (an impeller with 5 vanes at 1,750 rpm: 146 Hz) with harmonics: normal at a low level; high with a **wrong impeller-to-cutwater gap**, running far off BEP, a partly blocked impeller passage, a damaged vane.
- **Cavitation**: a random, broadband **raised noise floor** at high frequencies (often 1-20 kHz), sometimes with BPF harmonics, and the sound of gravel; changes with the suction condition (see [pump troubleshooting](/article/pump-troubleshooting)).
- **Recirculation**: low-frequency random and sub-synchronous energy at low flow.
- **Turbulence / flow noise**: random low-frequency energy (below 1×) in fans and pumps with bad inlet conditions.

### Soft foot and pipe strain

- Soft foot: a **distorted frame** gives 2× line frequency (motors), or 1× and 2× that change when a bolt is loosened (the test: loosen one foot at a time with the machine running and watch the spectrum, then re-torque: a foot whose loosening drops the vibration is the soft foot; do it safely, with the machine coupled, small changes).
- Pipe strain: misalignment signatures that change with temperature or when a flange is loosened.

## From the symptom to the cause

| Spectrum shows | Direction | First suspect | Also consider | Confirm by |
|---|---|---|---|---|
| **1× only, clean** | Radial, H > V | Unbalance | Eccentric sheave/rotor, bent shaft (if axial), resonance | Clean, balance; speed change |
| 1× with **high axial** | Axial | Angular misalignment, bent shaft | Sheave misalignment, a cocked bearing | Alignment, runout, phase |
| **2× > 1×** radial | Radial and axial | Parallel misalignment | Looseness, a cracked shaft (2× with a 1×), a worn coupling | Alignment hot/cold, pipe strain, coupling |
| 1× high **vertical** ≥ horizontal | Vertical | Structural looseness, soft foot | Base/grout failure, resonance | Bolts, base, soft foot check |
| **Many harmonics** and half-orders, raised floor | Radial | Rotating looseness (bearing fit, loose rotor) | Rub, severe bearing damage | Fits, clearances |
| **Non-synchronous** peaks (3.2×, 4.8×...) with 1× sidebands, envelope high | Radial | Rolling bearing defect | Gear sidebands (check GMF) | Bearing frequency match, envelope, temperature |
| 0.42-0.48× | Radial | Oil whirl (sleeve bearing) | Rub, belt frequency (calculate it) | Speed/oil change |
| GMF with sidebands at a gear's rpm | Radial (helical: axial) | Gear wear/damage on that gear | Misalignment of the gears | Inspection, oil analysis |
| **120 Hz (2× line)** that vanishes at power-off | Radial | Stator/air gap/voltage unbalance/soft foot | | Power-off test, voltage check |
| 1× with pole-pass sidebands, beating | Radial | Rotor bar | | Current analysis, load test |
| Sub-synchronous peak and multiples below 1× | Radial | Belt defect | Oil whirl | Strobe, belt frequency |
| One huge direction, speed-sensitive | One direction | Resonance | | Bump test, coast-down |
| BPF high | Radial | Pump/fan hydraulic (gap, off-BEP) | Blocked passage | Process check, inspection |
| Broadband high-frequency floor | Any | Cavitation, late bearing, lubrication starvation | Rub | Suction check, envelope, grease |

Two or more faults at once are normal (misalignment **causes** bearing damage; looseness **amplifies** unbalance): fix the primary one (the alignment, the base) first and re-read.

## Common mistakes

- Balancing a fan that had a resonance: the vibration returns at the next speed.
- Calling 2× line frequency "misalignment" on a 2-pole motor without the power-off test.
- Chasing a 3.2× peak as "a harmonic" when it is a bearing.
- Reading the spectrum without knowing the running speed, the bearing numbers and the gear teeth: the frequencies mean nothing.
- Fixing the symptom (a bearing) three times without the cause (the misalignment that killed it).

## Related

- [Vibration basics and ISO severity](/article/vibration-basics-and-iso-severity)
- [Shaft alignment fundamentals](/article/shaft-alignment-fundamentals) and [soft foot correction](/article/soft-foot-correction)
- [Bearing failure analysis](/article/bearing-failure-analysis)
- [Gear inspection and tooth failure](/article/gear-inspection-and-tooth-failure)
- [Pump troubleshooting](/article/pump-troubleshooting)
- [Megger and basic motor testing](/article/megger-and-basic-motor-testing)
- [Machine vibration, noise and heat decision tree](/article/machine-vibration-noise-heat-decision-tree)
