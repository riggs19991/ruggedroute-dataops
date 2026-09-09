---
title: "Megger and Basic Motor Testing: Insulation Resistance to Ground (IEEE 43 Test Voltages, Minimum Values, Temperature Correction, Polarization Index), Winding Resistance Balance, Continuity and Phase Checks, Running Checks (Voltage and Current Balance, Temperature, Speed), Bearing and Mechanical Checks, Single-Phase Motor Checks, and When to Send It to the Shop"
slug: megger-and-basic-motor-testing
category: motors-electrical
kind: procedure
tags: [megger, megger test, insulation resistance, IEEE 43, insulation resistance minimum, 1 kV plus 1 megohm, 100 megohm, 5 megohm, polarization index, PI test, dielectric absorption, megger voltage 500V 1000V, winding resistance, winding balance, ohms balance, motor continuity test, motor troubleshooting meter, current imbalance, voltage imbalance, motor overheating, motor hums won't start, motor trips overload, single phase motor test, capacitor test, centrifugal switch, motor shop, surge test]
source: "IEEE 43-2013 Recommended Practice for Testing Insulation Resistance of Electric Machinery (test voltages, minimum values, temperature correction, polarization index); EASA AR100 and EASA motor testing guidance; NEMA MG 1 (voltage and current unbalance); Fluke and Megger application notes on motor testing."
summary: "The tests a millwright or maintenance tech can do with a megger and a multimeter to decide whether a motor is fit to run, to find why it trips or hums, and to catch a winding going to ground before it fails: the insulation resistance test with the right voltage and the IEEE 43 pass values, the polarization index, winding resistance balance, the running voltage, current and temperature checks, single-phase motor specifics, mechanical checks, and the line between field testing and the motor shop."
---

> Lockout, and **test for zero voltage** before touching leads; a megger applies 500-1,000 V DC to the winding and the winding **stores** that charge: **discharge** the winding to ground for at least as long as the test (the megger's discharge function, or a grounding stick) before touching it. Disconnect the motor from the VFD and from any surge capacitors, RTDs and instruments before meggering (a megger destroys drive electronics).

## Insulation resistance (megger) to ground

Measures the resistance of the winding insulation to the frame (ground) in megohms; low or falling values mean moisture, dirt, oil, a cracked or overheated insulation, and a fault coming.

![Insulation resistance tester: 500 or 1,000 V DC, read at one minute](/photos/motors-electrical/insulation-tester.jpg)

*Insulation resistance tester: 500 or 1,000 V DC, read at one minute. Photo: HIOKI E.E. Corporation, CC BY-SA 4.0, via commons*

![Megger connections and IEEE 43 minimums](/img/motors-electrical/megger-test.svg)

*Megger connections and IEEE 43 minimums*

**Test voltage (IEEE 43)**

| Winding rated voltage | DC test voltage |
|---|---|
| Below 1,000 V (230/460/575 V motors) | **500 V** (1,000 V acceptable on 460-575 V motors in good condition) |
| 1,000-2,500 V | 500-1,000 V |
| 2,501-5,000 V (2,300/4,160 V motors) | 1,000-2,500 V |
| Above 5,000 V | 2,500-5,000 V |

**Procedure**

1. Motor isolated and locked out, leads disconnected from the supply/starter/VFD (test the motor **alone** first; the cable can be added later to find a cable fault); the leads' tags noted.
2. Clean the connection box; note the winding temperature (a thermometer on the frame or the RTD; the test is temperature-sensitive).
3. Connect the megger: one lead to **all three motor leads tied together** (or each phase in turn on a motor with separated phases), the other to a clean, bare spot on the **frame** (a ground screw, a bolt with the paint scraped), the guard terminal (if any) to the shaft or a lead surface for surface-leakage cancelling on damp motors.
4. Apply the voltage for **1 minute** (the reading falls at first as the insulation charges, then steadies); record the **1-minute value (IR₁)** and the temperature. For a PI test, keep the voltage on for **10 minutes** and record IR₁₀.
5. Discharge; reconnect; record on the motor's history card.

**Minimum values (IEEE 43-2013, corrected to 40°C, 1-minute reading)**

| Winding type | Minimum insulation resistance |
|---|---|
| **Random-wound stators (most motors under about 500 hp at ≤ 600 V)**, and form-wound below 1 kV | **5 MΩ** |
| Form-wound coils made after about 1970 (larger, medium-voltage motors) | **100 MΩ** |
| Older windings (pre-1970), DC armatures, field windings | **kV + 1 MΩ** (a 460 V motor: 1.46 → about 1.5 MΩ; a 4,160 V motor: 5 MΩ) |

In practice a **healthy low-voltage motor reads hundreds to thousands of MΩ** (often over the megger's range); a reading in the **tens** of MΩ is a wet or dirty motor to be dried and cleaned; **under 5 MΩ do not energise**; a reading in the kΩ or ohms is a ground fault. The **trend** on a motor's record matters more than a single pass: a motor that read 2,000 MΩ last year and 50 MΩ now is on its way out.

**Temperature correction**: insulation resistance roughly **halves for every 10°C rise** (IEEE 43 corrects readings to 40°C: multiply the reading at temperature T by the factor K = 0.5^((40 − T)/10) to get the 40°C value; a reading of 100 MΩ at 20°C is 25 MΩ at 40°C; a reading at 60°C is doubled twice to compare). A cold motor in a damp shop reads low because of **surface moisture**; a motor just stopped reads low because it is warm: compare like with like, and always note the temperature.

**Polarization index (PI)** = IR₁₀ ÷ IR₁ (the 10-minute reading over the 1-minute reading): a good insulation keeps charging (the reading keeps rising); a wet or dirty one does not.

| PI | Condition |
|---|---|
| < 1.0 | Dangerous: do not run |
| 1.0-1.5 | Poor (Class A minimum 1.5) |
| 1.5-2.0 | Questionable |
| **≥ 2.0** | Acceptable for Class B, F and H insulation (IEEE 43 minimum) |
| 2-4 | Good |
| > 8 or a reading over 5,000 MΩ at 1 minute | The PI is not meaningful (very dry, high-resistance modern insulation); use the IR value alone |

A quick version is the **dielectric absorption ratio** (60 s ÷ 30 s): ≥ 1.25 acceptable, ≥ 1.6 good.

**Drying a wet motor**: warm air (a lamp, a heater, the space heaters energised), or run at a low current (locked rotor at reduced voltage, or with the rotor removed a low-voltage current through the winding: a motor shop job); megger every few hours: the reading rises as it dries; stop when it plateaus above the minimum.

## Winding resistance and continuity

With a **low-ohms meter** (a milliohm meter or a good multimeter on its lowest range; a standard multimeter reads small motors only roughly), measure between each pair of leads (T1-T2, T2-T3, T1-T3 on a 3-lead motor; each winding half on 9-lead motors with the leads separated):

![Stator and rotor of an induction motor](/photos/motors-electrical/stator-rotor.jpg)

*Stator and rotor of an induction motor. Photo: Zureks, CC BY-SA 3.0, via commons*

- **Balance**: the three readings should be **within about 1-3% of each other** (larger motors read fractions of an ohm: a milliohm meter or the shop's Kelvin bridge); a phase reading **open** (infinite) = a broken lead or coil; **higher** than the others = a bad joint, a burned turn; **lower** = a **shorted turn** (a turn-to-turn short: the motor runs hot, hums, trips, and it will fail; a surge test at the shop confirms).
- Compare with the previous record or with an identical motor; a 9-lead motor's halves should match each other (T1-T4 = T2-T5 = T3-T6 and T7-T8 = T8-T9 = T7-T9 on the wye group).
- Phase-to-phase on a wye motor reads twice the phase resistance; on a delta, two-thirds of it: the value itself does not matter, the balance does.
- Continuity from each lead to ground: **infinite** on the multimeter (the megger is the real test).

## Running checks (the meter and the eye)

| Check | Tool | Normal | Abnormal means |
|---|---|---|---|
| **Supply voltage, each phase pair** | Multimeter at the starter (qualified person, PPE) | Nameplate ± 10%; **imbalance under 1%** (NEMA: derate at 1-5%) | Low voltage: slip and heat; imbalance from a bad connection, a fuse, a single-phase load on the feeder: a 3.5% voltage imbalance gives a 25% current imbalance and derates the motor to 90% |
| **Current, each phase** | Clamp meter | Under FLA; **imbalance under 10%** (the largest deviation from the average ÷ the average); ideally under 5% | Overload (current above FLA on all phases: the load or the voltage), imbalance (the supply, a bad connection, a winding fault), one phase at 0 (open) |
| **Motor frame/bearing temperature** | IR gun / contact | Frame: warm to hot depending on the class (a Class F motor's frame can run 90-100°C in places; a TEFC frame at 70-80°C is normal); **bearing housings under about 80-90°C (180°F)** | A hot frame with high current: overload, blocked cooling (fan cover, fins full of dust), high ambient, voltage; a hot bearing: lubrication, misalignment, belt tension |
| **Speed** | Strobe / tachometer | Nameplate rpm ± a little at load | Excess slip: overload, low voltage, a rotor bar fault (a broken rotor bar also shows as a current that **swings** at the slip frequency) |
| **Noise and vibration** | Ear, hand, a vibration pen | Smooth hum | Growl at 120 Hz (electrical: unbalanced voltage, a winding, a loose lamination), a bearing noise, rubbing; a noise that **disappears the instant power is cut** is electrical; one that continues while coasting is mechanical |
| **Starting** | | Comes up to speed in seconds | Slow acceleration: low voltage, a design B on a high-inertia load, a mechanical drag; hums and will not start: a single-phased supply, a seized load, a bad capacitor (single-phase), a wrong connection |
| **Trips on overload** | The overload relay's setting vs FLA × the allowance (NEC 430.32: 125% of FLA for SF 1.15 motors) | | Set too low, or a genuine overload/imbalance |

## Single-phase motors

- **Capacitor**: a start capacitor (electrolytic, 100-800 µF, in a plastic can) and/or a run capacitor (oil-filled, 5-50 µF): test with a capacitance meter after **discharging it** (a resistor across the terminals; a screwdriver short is the old way and pits the terminals); a start capacitor that is bulged, leaking, or reads open or far from its µF (± 10%) is replaced; a motor that hums and does not start, or starts by hand-spinning, has a bad start capacitor or a bad **centrifugal switch**.
- **Centrifugal switch**: contacts burned or the mechanism stuck (the motor starts but runs hot and noisy with the start winding still in, or does not start); clean or replace.
- Windings: the run winding (low resistance) and the start winding (higher resistance) each read continuity; meggered to ground like a three-phase motor.
- Reversing: swap the start winding leads (T5/T8) as the plate shows.

## Mechanical checks (before blaming the electrical)

- Turn the shaft by hand (locked out): free, no rough spots (bearings), no rub (a rotor touching the stator: bearing wear); end float normal.
- Fan cover clear, fins clean; a TEFC motor with an inch of dust on it runs 20°C hotter.
- Alignment, belt tension (an over-tensioned belt loads the DE bearing and raises current), the coupling, the load's own drag (a pump with a rubbing impeller, a gearbox with a seized bearing).
- Mounting bolts and soft foot (a distorted frame rubs the rotor).
- Shaft currents on a VFD (fluting in the bearing: see [bearing failure analysis](/article/bearing-failure-analysis)).

## When it goes to the shop

![Motor opened: windings, bearings and air gap all inspected](/photos/motors-electrical/motor-opened.jpg)

*Motor opened: windings, bearings and air gap all inspected. Photo: Moteuralioth, CC BY-SA 3.0, via commons*

- Insulation resistance below the minimum after drying; a PI under 1.5; a ground fault; a shorted turn (unbalanced resistance, a surge test needed); a broken rotor bar suspected (current swing, high slip); a burned winding smell; a bearing failure that has let the rotor rub the stator (a scored rotor and stator: a rewind or a replacement); explosion-proof motors (the flame paths must be checked and the repair certified).
- The shop's tests: surge comparison (turn-to-turn), hipot, core loss, rotor bar tests, dynamic balancing; the repair per EASA AR100 with the winding data recorded.
- Economics: a rewind on a motor under about 40-50 hp usually costs more than a new premium-efficiency motor and gives a less efficient motor; above that, rewinds are normal; keep the nameplate data and the failure evidence for the shop.

## Recording

A card per motor (or the CMMS): date, temperature, IR₁ (at temperature and corrected), PI when done, winding resistances, running currents and voltages, bearing temperatures, vibration; the trend decides the next action.

## Common mistakes

- Meggering with the VFD or a capacitor still connected: the drive is destroyed or the reading is meaningless.
- Reading 20 MΩ on a warm motor in a damp plant and condemning it, or reading 20 MΩ on a cold motor and running it: correct for temperature and trend it.
- Touching the leads after the test without discharging.
- Using a 5,000 V megger on a 460 V motor.
- Blaming the motor for tripping when one supply phase is 8% low.
- Testing to a painted frame: a high reading that means nothing.

## Related

- [Reading a motor nameplate](/article/reading-a-motor-nameplate)
- [Motor lead connections](/article/motor-lead-connections)
- [VFD basics for millwrights](/article/vfd-basics-for-millwrights)
- [Electrical safety for mechanics](/article/electrical-safety-for-mechanics)
- [Bearing failure analysis](/article/bearing-failure-analysis)
- [Vibration signatures (electrical vs mechanical)](/article/vibration-signatures)
