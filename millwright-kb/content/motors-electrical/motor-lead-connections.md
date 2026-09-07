---
title: "Motor Lead Connections: 3-Lead, 9-Lead Wye and Delta Dual-Voltage (Low and High Connections), 12-Lead (Wye-Delta Start, Part-Winding), 6-Lead, Identifying Unmarked Leads with an Ohmmeter, Single-Phase Reversing, Checking and Changing Rotation, Connection Box Practice (Lugs, Tape, Grounding), and What a Wrong Connection Does"
slug: motor-lead-connections
category: motors-electrical
kind: procedure
tags: [motor lead connections, 9 lead motor, 9 lead wye, 9 lead delta, low voltage connection, high voltage connection, 230 460 motor wiring, 12 lead motor, wye delta start, part winding start, 6 lead motor, 3 lead motor, T1 T2 T3, motor rotation, reverse motor rotation, swap two leads, unmarked motor leads, identify motor leads ohmmeter, single phase motor reversing, motor junction box, motor lugs, motor connection tape, motor grounding, wrong connection motor smoke]
source: "NEMA MG 1 (lead marking and connection diagrams for 3-, 6-, 9- and 12-lead three-phase motors); Baldor-Reliance/ABB connection diagram sheets; EASA connection and lead-identification guidance; NEC Article 430 (motor circuits) for the wiring and grounding requirements."
summary: "The connection diagrams for the three-phase motors a millwright reconnects most, with the rule for which leads join at low and high voltage and why, how wye-delta and part-winding 12-lead motors are connected, a method to identify a 9-lead motor whose lead tags are gone, how to check and reverse rotation, how to make a connection that does not fail in the box, and what happens when the connection is wrong."
---

> The electrician's licence decides who makes the final connection in many jurisdictions; a millwright must still understand the diagrams to check a motor before it is bolted in, to bump for rotation, and to recognise a wrong connection. **Lockout and test for zero voltage** before opening any motor connection box; a motor on a VFD can have voltage on its leads with the drive "stopped".

## The windings

A three-phase motor has three winding groups (phases) that are connected internally or at the box in a **wye (star: all three joined at a common point)** or a **delta (each end joined to the next: a triangle)**. Dual-voltage motors have each phase in **two halves** brought out so the halves can be connected in **series** (high voltage: each half sees half the line voltage) or in **parallel** (low voltage: each half sees the full, lower voltage): the same winding current per half either way, which is why the FLA at 230 V is twice the FLA at 460 V.

## 9-lead dual-voltage, wye-connected (the commonest: 230/460 V)

Leads T1-T9 are brought out; inside the motor, T7, T8 and T9 are joined to form the star point of one set of winding halves:

```
   HIGH voltage (460 V): series
      L1 – T1        L2 – T2        L3 – T3
      join  T4–T7     T5–T8     T6–T9          (nothing else joined)

   LOW voltage (230 V): parallel
      L1 – T1 & T7   L2 – T2 & T8   L3 – T3 & T9
      join  T4–T5–T6 together (insulated, not to any line)
```

Memory aid: on a wye motor the numbers form a **spiral**: T1-T4-T7, T2-T5-T8, T3-T6-T9 are each one phase; high = join across the spiral (4-7, 5-8, 6-9); low = line to 1&7, 2&8, 3&9 and tie 4-5-6.

## 9-lead dual-voltage, delta-connected

```
   HIGH voltage: series
      L1 – T1   L2 – T2   L3 – T3
      join  T4–T7     T5–T8     T6–T9

   LOW voltage: parallel
      L1 – T1 & T6 & T7      L2 – T2 & T4 & T8      L3 – T3 & T5 & T9
```

High voltage is connected **the same way** for wye and delta 9-lead motors (line to 1-2-3, join 4-7, 5-8, 6-9); low voltage differs (wye: tie 4-5-6 together; delta: 1-6-7, 2-4-8, 3-5-9). The nameplate diagram says which the motor is: **always use the plate**.

## 12-lead motors

All six winding ends of both halves are out (T1-T12), so the motor can be connected wye or delta at either voltage: for **wye-delta (star-delta) reduced-voltage starting** (the starter connects the motor in wye to start at 58% current, then switches to delta to run) and for **part-winding starting** (half the winding first, then both).

```
   DELTA run, high voltage (the normal run connection on a wye-delta starter, 460 V):
      L1 – T1 & T12    L2 – T2 & T10    L3 – T3 & T11
      join  T4–T7     T5–T8     T6–T9
   DELTA run, low voltage (230 V):
      L1 – T1 & T6 & T7 & T12    L2 – T2 & T4 & T8 & T10    L3 – T3 & T5 & T9 & T11
   WYE, high voltage (across-the-line on a wye motor, or the start connection of a wye-delta starter at 460 V):
      L1 – T1   L2 – T2   L3 – T3
      join  T4–T7   T5–T8   T6–T9        and  T10–T11–T12 together
   WYE, low voltage:
      L1 – T1 & T7   L2 – T2 & T8   L3 – T3 & T9
      join  T4–T5–T6 together   and   T10–T11–T12 together
```

On a **wye-delta starter** the twelve (or six) leads run to the starter (six motor leads in a 6-lead motor: T1-T6), and the starter makes and breaks the wye point; a 12-lead motor on a plain starter or a VFD is connected **delta** for the voltage. **Part-winding** (9-lead wye motors designed for it, or 12-lead): the starter energises T1-T2-T3 (with 4-5-6 tied) first, then adds T7-T8-T9; the plate says "part winding".

## 6-lead and 3-lead motors

- **3-lead** (T1, T2, T3): single voltage, internally connected; line to the leads; reverse by swapping two.
- **6-lead, single voltage, wye-delta**: T1-T6; run: delta (L1 to T1&T6, L2 to T2&T4, L3 to T3&T5); wye start on the starter (T4-T5-T6 tied).
- **6-lead dual voltage** (some IEC motors: U1 V1 W1 / U2 V2 W2): **delta** for the lower voltage (bridge U1-W2, V1-U2, W1-V2: in the standard 6-terminal IEC box the three bars sit **vertical for delta (∆)** and one bar joins **U2-V2-W2 horizontally for star (Y)**; the plate's picture shows it), **star** for the higher (bars across U2-V2-W2). An IEC motor marked 230∆/400Y goes in **delta on 230 V** and **star on 400 V**; the same motor on 460/480 V is connected star; on 208-230 V, delta.

IEC lead marking: U1 V1 W1 (line ends), U2 V2 W2 (the other ends); dual-voltage IEC motors with more leads follow the plate diagram.

## Rotation

- NEMA motors connected L1-T1, L2-T2, L3-T3 to a supply with A-B-C phase sequence turn counter-clockwise viewed from the drive end (NEMA states rotation viewed from the opposite drive end, where it is clockwise). In practice the direction depends on the supply's phase sequence, which nobody knows for sure until the motor turns.
- **Check rotation with the load uncoupled** (see [commissioning](/article/machine-guarding-and-commissioning)): bump, watch. Pumps run backwards make 50-60% of the flow and can unscrew the impeller; a gearbox with a backstop breaks; a screw conveyor packs the end plate.
- **Reverse**: swap **any two line leads** (at the starter, not by reconnecting the motor's internal connections); on a VFD, swap two motor leads at the drive's output or change the drive's rotation parameter; on a single-phase motor, reverse the **start winding** leads (T5 and T8, or per the plate) relative to the run winding.
- After any motor change, rotation is checked again: a rewound motor comes back with the leads any way round.

## Identifying unmarked 9-lead motor leads (wye)

Tags fall off and rewinds come back with bare numbers; the ohmmeter method for a **wye** 9-lead motor (the commonest):

1. With the motor isolated and all leads separated, use an ohmmeter (or a continuity tester) to find **groups**: three leads that read continuity to each other form the internal wye (**T7-T8-T9**) and three **pairs** are the outer halves (T1-T4, T2-T5, T3-T6).
2. Mark the wye group temporarily A, B, C and the pairs 1a-1b, 2a-2b, 3a-3b.
3. Connect the wye group's three leads to the **low** line voltage (230 V) through the starter/overloads (the motor runs on the inner winding; it will turn); with the motor running, measure the voltage across each outer pair: it reads a definite induced voltage (roughly the line-to-neutral value).
4. For each outer pair: connect one end of the pair to one wye lead (say A) and measure the voltage between the pair's other end and the **next** wye lead (B and C in turn); the right pairing gives the **higher** reading (the voltages add: about 1.5× the line-to-neutral) in series-aiding; the wrong gives lower. The outer half whose series-aiding reading is highest to wye lead A is that phase's outer half: its lead attached to A is **T4** (with A = T7) and its free end **T1**. Repeat for B (T8: T5/T2) and C (T9: T6/T3).
5. Mark the leads with numbered tags and tape; verify by connecting for high voltage and running the motor: balanced currents and normal rpm confirm the identification; unbalanced currents mean a phase's polarity is reversed: swap that pair's ends.

A **delta** 9-lead has three groups of three (T1-T4-T9, T2-T5-T7, T3-T6-T8) and a different procedure; unmarked 12-lead or delta motors are best sent to a motor shop with the plate.

## Making the connection

- Lugs: crimped ring or compression lugs on the motor leads and the supply conductors, never twisted-and-taped bare copper; use the right connectors: split-bolt connectors or Polaris-type insulated connectors on large cables, crimp lugs bolted together with a flat washer, lock washer and nut torqued); the number tags visible on every lead.
- **Insulate** each joint: rubber (self-amalgamating) tape as the insulation, then vinyl tape over it, half-lapped, extended over the lead insulation; or insulated connectors; no bare copper anywhere; each phase joint separated from the others.
- **Ground**: the equipment grounding conductor to the motor frame's ground screw/lug in the box; the box gasket in place; the conduit connection tight; a motor on a VFD needs the shielded cable's shield terminated at both ends (360° gland) per the drive manual.
- Position the joints so they do not press against the box cover or each other; drain plugs in a TEFC box on the bottom.
- Record the connection made (high/low) on the work order; the diagram on the plate followed, not memory.

## What a wrong connection does

| Error | Result |
|---|---|
| 460 V motor connected low (230) on 460 V | **Draws 2× current, smokes in minutes** (the winding halves in parallel across double voltage) |
| Connected high (460) on 230 V | Runs, no torque, stalls under load, overheats slowly (half voltage) |
| One phase's pair reversed (polarity) | Runs rough, high and unbalanced currents, overheats |
| One lead not connected (open phase) | Will not start (hums), or if running, single-phases: 173% current in the other two, burns out fast |
| Two lines swapped | Reverse rotation only |
| Wye motor connected delta or the reverse (12-lead) | Wrong voltage across the windings: overheat or no torque |
| Star point (4-5-6) accidentally grounded or connected to a line | Trips, or destroys the winding |

Check the running currents on all three phases after any connection: balanced within 10% and below FLA.

## Common mistakes

- Connecting from the memory of the last motor: a wye and a delta 9-lead differ at low voltage.
- Tying T4-T5-T6 **and** connecting T7-T8-T9 to the line (mixing the low and high diagrams): the motor burns.
- Reversing rotation by reconnecting the motor leads instead of swapping two lines: a later "reconnection for high voltage" puts it back the wrong way.
- Tape only over a split-bolt: it cuts through and the box shorts.
- No ground on the frame: a winding fault makes the frame live.
- Skipping the uncoupled rotation check on a pump: the impeller unscrews on the first start.

## Related

- [Reading a motor nameplate](/article/reading-a-motor-nameplate)
- [Megger and basic motor testing](/article/megger-and-basic-motor-testing)
- [VFD basics for millwrights](/article/vfd-basics-for-millwrights)
- [Machine guarding and commissioning (rotation bump)](/article/machine-guarding-and-commissioning)
- [Electrical safety for mechanics](/article/electrical-safety-for-mechanics)
