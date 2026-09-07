---
title: "Hydraulic Accumulator Precharge and Safety: Bladder, Piston and Diaphragm Types, What the Precharge Does, Precharge Rules by Application (90% Energy Storage, 75% Shock, 70% Pulsation), Temperature Correction, the Nitrogen Charging Procedure Step by Step, Checking Precharge Without a Gauge, Bleed-Down Before Any Work, Signs of Lost Precharge and Bladder Replacement"
slug: accumulator-precharge-and-safety
category: hydraulics
kind: procedure
manufacturer: "Parker / Hydac / Tobul / Bosch Rexroth (generic)"
model_numbers: ["Parker ACP", "Parker A2", "Hydac SB330", "Hydac SK", "Tobul", "Bosch Rexroth HAB", "Greer"]
tags: [accumulator, hydraulic accumulator, precharge, pre-charge, nitrogen precharge, accumulator charging, charging kit, bladder accumulator, piston accumulator, diaphragm accumulator, precharge pressure, 90 percent rule, accumulator temperature correction, accumulator bleed down, accumulator safety, accumulator dump valve, gas valve core, bladder replacement, lost precharge, accumulator stored energy, lockout accumulator, nitrogen bottle CGA 580]
source: "Tobul (FST) nitrogen pre-charging instructions (precharge 90% energy storage, 75% shock, 70% pulsation; piston 100 psi below minimum, bladder 175 psi below minimum; hose ratings CGA 580 to 3,000 psi, CGA 677 to 5,000 psi; stabilise 10-15 min); Parker accumulator catalogue (temperature correction factor method); Hydac accumulator operating manuals; Fluid Power Safety Institute guidance on accumulator lockout."
summary: "The accumulator is the most dangerous stored energy in a hydraulic system and the most neglected: this covers the three types, why the nitrogen precharge sets how the accumulator works, the precharge rules for each job and how to correct for temperature, the full charging procedure with the kit and the nitrogen bottle, how to check the precharge quickly, the bleed-down every lockout needs, how to recognise a lost precharge or a failed bladder, and how a bladder is replaced."
---

## Types

| Type | Construction | Notes |
|---|---|---|
| **Bladder** | A rubber bladder (nitrile, Viton, Hydrin, butyl) in a forged shell; gas inside the bladder, oil outside; a poppet valve at the oil port stops the bladder extruding | The commonest; fast response; **mount vertically, gas valve up**; ratio (max working : precharge) about 4:1; sizes 1 pint to 15+ gallons; 3,000-6,000 psi |
| **Piston** | A free piston with seals in a honed cylinder; gas above, oil below | Any orientation (vertical preferred); high compression ratios; big sizes; the piston seals wear and let gas leak slowly, so the precharge is checked more often; dirty oil scores the bore |
| **Diaphragm** | A diaphragm clamped in a small welded or screwed shell | Small volumes (to about 1 gal); mobile equipment, suspension, pulsation |
| Spring / weight-loaded | | Old and special |

What they do: **energy storage** (a pump charges the accumulator, it supplies flow bursts bigger than the pump: presses, clamping), **shock absorption** (water hammer, pressure spikes), **pulsation damping** (piston pumps), **leakage make-up / pressure holding** (clamping and load-holding circuits: the pump can stop), **thermal expansion**, **emergency power** (to lower a load or release a brake when the pump fails).

## Precharge

The gas precharge (**dry nitrogen only**, P₀) sets the pressure at which the accumulator starts to take oil and how much oil it can give back between the system's maximum (P₂) and minimum (P₁) pressures.

| Application | Precharge P₀ | Why |
|---|---|---|
| **Energy storage** (the usual) | **90% of the minimum system pressure P₁** (or 100 psi below P₁ on a piston type, 175 psi below on a bladder type: Tobul) | The bladder stays slightly off the poppet at P₁ so it never bottoms; below 80% the bladder folds and fatigues; above P₁ the accumulator gives no oil until the system pressure passes the precharge |
| **Shock absorption** | **about 75%** of the minimum working pressure | Softer response |
| **Pulsation damping** | **about 70%** of the system operating pressure | |
| Thermal expansion | Set at the system's normal pressure | |
| Emergency power | Per the circuit design | |

Never over 90% of P₁ on energy storage (the gas volume is what stores the energy: too high and there is little usable oil, and the bladder hits the poppet on every cycle); never above the accumulator's or the system's rating. The **design sheet or the accumulator's tag** gives the P₀; write it on the accumulator with a paint marker if it is missing.

**Temperature correction**: the gas pressure changes with temperature (a closed volume: P₁/T₁ = P₂/T₂ in **absolute** units). Charge in a cold shop and the precharge is higher when the system is at 140°F:

```
   P₀ at charging temperature = P₀ (wanted at operating temperature) × (T_charging + 460) ÷ (T_operating + 460)     (°F; use K for °C)
   Example: wanted 1,000 psi at 140°F, charging at 70°F: 1,000 × 530 ÷ 600 = 883 psi      (Parker's chart gives the same factor, about 0.88)
```

So charge to the corrected (lower) value when the system will run hot, and when **checking** a running system's precharge, convert the reading to the operating temperature before comparing. Check with the system **cold** and the oil side bled for a clean reading; the Parker/Tobul instructions say to let the gas stabilise **10-15 minutes** after charging before the final reading (compression heats the gas).

## Safety rules (before anything)

- **Nitrogen only**. Oxygen or air with oil = an explosion; CO₂ or other gases damage the bladder and give wrong pressures. Cylinders marked **nitrogen, CGA 580** (up to 3,000 psi) or **CGA 677** (up to 5,000/6,000 psi) outlets; the charging kit must match.
- The nitrogen bottle is at **2,200-6,000 psi**: the charging assembly's hose must be rated for it (kits are marked 3,000 / 5,000 / 10,000 psi), and the accumulator's gas side must never see more than its rating: a **regulator** on the bottle when the bottle pressure exceeds the accumulator's rating (a 6,000 psi bottle on a 3,000 psi accumulator without a regulator will burst the accumulator's gas valve or shell).
- **Bleed the oil side to zero** (the system's accumulator dump valve, or the bleed at the accumulator) and prove it on the gauge before touching the gas valve; the gas valve cap and the core are the only barrier.
- Never unscrew the gas valve assembly, the bladder plug, or a shell fitting with gas in it; never weld on, drill, or heat an accumulator; never exceed the nameplate pressure; a dented or corroded shell is condemned.
- Expanding nitrogen is **cold**: freeze burns; gloves; eye protection; the bottle chained.
- **Lockout** of any hydraulic system with an accumulator includes **discharging it** (the dump valve, an automatic unloading valve that opens when the pump stops, or a manual bleed) and **verifying zero** on the accumulator's oil-side gauge; a machine with a charged accumulator can move after the pump is locked out. See [hydraulic basics](/article/hydraulic-system-basics-and-symbols).

## Charging procedure (bladder type; piston and diaphragm the same at the gas valve)

1. Shut down the pump; **open the dump/bleed valve** and drain the oil side of the accumulator to the tank until the pressure gauge on the accumulator's oil side reads **zero** and stays there; lock out the pump. The bladder is now fully expanded against the poppet (a bladder accumulator "clicks" as it seats).
2. Remove the gas valve **protective cap** and the **valve core cover** (the small cap over the core; some valves have a sealing cap that must be loosened slowly: a hiss means the core is leaking or the cap was the seal: stop and check).
3. Fit the **charging and gauging assembly**: the swivel nut onto the gas valve (hand tight, then a light wrench pull), the gas chuck's T-handle **backed all the way out** (counter-clockwise: it depresses the core when turned in), the bleed valve on the assembly **closed**, the hose to the nitrogen bottle **not yet connected** or the bottle valve closed.
4. **Read the existing precharge**: turn the T-handle in (clockwise) until the gauge shows pressure (the core is depressed); this is the current precharge: compare with the tag (corrected for temperature). If it is right, back the T-handle out, remove the assembly, refit the caps; done.
5. To **add** gas: connect the hose to the bottle (regulator set if needed), **crack the bottle valve slowly** and let the accumulator fill **slowly** to about **100 psi above** the wanted precharge; close the bottle valve; **wait 10-15 minutes** for the gas to cool and the reading to settle; then **crack the assembly's bleed valve** to bring the reading down to the exact precharge; close the bleed.
6. To **reduce** gas: the bleed valve on the assembly, slowly, watching the gauge; wait and re-read.
7. Back the T-handle **all the way out** (the core closes), close the bottle valve and bleed the hose (the assembly's bleed), remove the assembly, **check the core for leaks** with soapy water or leak fluid, refit the valve cover and cap (hand tight plus a light pull; the cover seals the core).
8. Record the date, the temperature, the precharge on the accumulator's tag and in the log. Re-check **after one week** on a newly installed or repaired accumulator, then **monthly for the first few months and every 3-6 months** after (the FST guide: weekly at first, then monthly); piston accumulators more often than bladders.

## Checking without a gauge assembly (the quick check)

With the pump running and the system at pressure, watch the accumulator's oil-side gauge while the pump is stopped or the dump valve opened slowly: the pressure falls **steadily** as the accumulator gives oil, then **drops suddenly** to zero when the bladder seats: the pressure at which it drops **is the precharge**. No sudden drop (it falls smoothly to zero) = **no precharge** (a ruptured bladder or a leaked-off gas charge). This is also how you find a bladder that has failed: the accumulator gives no oil and the system hammers.

## Signs of lost precharge or a failed bladder

- The pump cycles much more often, or runs continuously on a clamping circuit (no stored oil).
- **Hammering/pressure spikes** on a shock-absorbing accumulator.
- Slow or weak machine motions that used the accumulator's flow.
- The gas side reads zero, or the gauge shows **oil** at the gas valve (a ruptured bladder puts oil in the gas side: the core spits oil when depressed).
- A bladder accumulator that reads a precharge but the system behaves badly: the bladder may be leaking slowly (weekly checks show a loss).
- Piston accumulator: the gas pressure slowly falling and oil leaking past the piston into the gas side.

Bladder life: 5-10 years, less with high cycle rates, high temperature, or a wrong precharge (a low precharge lets the bladder slam the poppet and tear; a high precharge extrudes it into the port).

## Bladder replacement (outline; the maker's procedure governs)

1. Bleed both sides completely (oil to zero, gas released fully through the core with the T-handle in and the bleed open until the gauge is at zero and no hiss); remove the accumulator from the system if possible; clamp the shell in a fixture (not a pipe vise on the shell).
2. Remove the gas valve assembly (the nut that holds the bladder's stem in the shell), push the stem into the shell.
3. Remove the **poppet (fluid port) assembly**: the lock nut, the spacer, the anti-extrusion ring (it collapses to come out through the port), the poppet and spring.
4. Pull the old bladder out through the fluid port (collapse it); inspect the shell interior for scoring and corrosion (a corroded shell is scrap).
5. New bladder of the **correct material** for the oil and temperature; **lubricate** it with the system oil; collapse it (a vacuum on the stem helps), insert it through the fluid port with the stem to the gas end, pull the stem through and fit the gas valve nut loosely; **inflate slightly** (5-10 psi) to shape the bladder; refit the poppet assembly and the anti-extrusion ring (it snaps back into shape inside the port), the spacer and the lock nut to torque; tighten the gas valve nut.
6. Precharge per the procedure; leak test the gas valve and the port; install; re-check in a week.

## Common mistakes

- Charging from a shop air line (oil + oxygen + heat).
- A 6,000 psi bottle straight onto a 3,000 psi accumulator.
- Checking the precharge with the oil side still pressurised: the reading is the oil pressure.
- Precharge set to the system's maximum pressure "for more power": no usable oil, bladder dead.
- Lockout of the pump only; the press comes down on the accumulator.
- Cold-shop precharge with no temperature correction on a hot press: 15% high.
- Tightening the gas valve core cover with a big wrench: the core cracks.

## Related

- [Hydraulic system basics and symbols](/article/hydraulic-system-basics-and-symbols)
- [Lockout / tagout basics](/article/lockout-tagout-basics)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
- [Compressed gas cylinder handling](/article/compressed-gas-cylinder-handling)
- [Hydraulic hose assembly and fittings](/article/hydraulic-hose-assembly-and-fittings)
