---
title: "Centrifugal Pump Troubleshooting: Cavitation vs Air Entrainment vs Recirculation, Reading the Pump Curve (BEP, NPSHr, Running Off-Curve), the Symptom Table (No Flow, Low Flow or Head, High Power, Vibration, Seal and Bearing Failures, Noise), Field Checks with Gauges, and Start-Up, Priming and Shutdown"
slug: pump-troubleshooting
category: pumps-seals
kind: reference
tags: [pump troubleshooting, centrifugal pump problems, pump not pumping, low flow, low head, cavitation, cavitation sound, air entrainment, recirculation, NPSH, NPSHa, NPSHr, pump curve, BEP, best efficiency point, running off curve, dead head, minimum flow, pump vibration, seal failure repeat, bearing failure pump, pump noise, priming a pump, pump startup, pump shutdown, rotation check, suction strainer, pump gauges]
source: "Goulds Pumps (ITT) Pump Handbook and troubleshooting tables; Hydraulic Institute ANSI/HI 9.6.3 (allowable operating region) and troubleshooting guidance; Grundfos Pump Handbook; pump manufacturer IOMs (Goulds 3196, Flowserve); Karassik, Pump Handbook."
summary: "How to find out why a centrifugal pump is not doing its job before pulling it apart: the three noises that get called cavitation and how to tell them apart, what the pump curve tells you about where the pump is running, a symptom-to-cause table ordered by likelihood, the gauge readings and quick checks that decide between a pump problem and a system problem, and the correct way to prime, start and stop a centrifugal and a PD pump."
---

## Start with the gauges

A pump complaint is a **system** complaint until the gauges say otherwise. Fit or read: **suction pressure** (or vacuum), **discharge pressure**, motor **amps** (all three phases), and if possible flow; note the liquid temperature and the tank level. Then:

```
   differential head (ft) = (P_discharge − P_suction, psi) × 2.31 ÷ SG        (correct the gauges to the pump centreline)
   compare with the curve at the flow you think you have; the amps tell you the power and therefore roughly the flow
   NPSHa = (P_atm + P_suction gauge − P_vapour) × 2.31 ÷ SG + velocity head    (formulas in [pump formulas](/article/pump-and-fluid-power-formulas))
```

- **High differential head, low flow, low amps**: the pump is fine and the system is **throttled or blocked** (a closed valve, a plugged strainer downstream, a stuck check valve, a plugged line).
- **Low head, high amps, high flow**: running far out on the curve (a broken line, a wide-open system, the wrong impeller or speed).
- **Low head, low flow, low amps**: the pump is not developing head: **wrong rotation**, an impeller worn or plugged, excessive clearance, **air in the pump**, speed low (VFD), a broken coupling/key.
- **Suction gauge bouncing / high vacuum**: suction problem: cavitation, a plugged suction strainer, a vortex at the tank.

## The three noises

| | **Cavitation** | **Air entrainment (aeration)** | **Recirculation** |
|---|---|---|---|
| Sound | Rattling gravel, marbles, a crackle, loudest at the suction; worse as the discharge valve opens (more flow) | Similar crackle but softer, steadier, often with **surging** flow and a spitting discharge; the pump loses prime | A random knock or bang at the impeller, worse as the discharge valve **closes** (less flow) |
| Cause | Vapour bubbles form at the impeller inlet because **NPSHa < NPSHr** (suction lift too high, liquid too hot, tank too low, strainer plugged, suction line too small/long, pump running out too far on its curve) | Air drawn in: a leaking suction flange or packing (on lift), a vortex at a low tank level, a submerged return line entraining air, a leaking pump seal on vacuum | Running at **low flow** (below the minimum continuous stable flow, typically 30-50% of BEP on ANSI pumps): the liquid recirculates at the impeller eye or discharge and pounds |
| Damage | Pitting on the impeller vanes **near the inlet edge**, on the low-pressure side; seal and bearing failure from the shaking | Rarely damages the metal; loses prime, gas-locks the seal | Pitting on the **pressure side of the vane** near the inlet (suction recirculation) or at the vane tips (discharge recirculation); shaft deflection, seal and bearing failures |
| Fix | Raise NPSHa: raise the tank level, lower the pump, bigger/shorter suction line, clean the strainer, cool the liquid, reduce the flow (throttle the discharge: it works because NPSHr falls with flow), a slower pump or an inducer; check the NPSH margin (HI: at least 3-5 ft or a ratio 1.1-1.3 NPSHa/NPSHr) | Find the leak (soap the suction joints under vacuum, fix the packing/seal, submerge the tank return, raise the level, a vortex breaker) | Open the flow: a minimum-flow bypass, a smaller impeller or pump, a VFD; never run a pump on the shut-off line for long |

Do not mistake **bearing noise** (a whine or growl at the bearing housing, felt with a screwdriver at the housing) or **coupling noise** for any of these.

## The pump curve

- **Head vs flow**: the pump's own line; **BEP** (best efficiency point) is where it should run; **allowable operating region** (HI 9.6.3) is roughly **70-120% of BEP** for most pumps; outside it the radial thrust rises (shaft deflection → seal and bearing failure), recirculation and cavitation begin.
- **NPSHr line** rises with flow; the system must supply more than it (with margin).
- **Power line** rises with flow on radial pumps (a pump running far out on its curve overloads the motor).
- **The system curve** (static head + friction that rises with the square of flow) crosses the pump curve at the operating point; **opening a valve** moves the point right (more flow, less head, more power, more NPSHr); closing it moves left.
- **Speed change** (VFD): flow ∝ speed, head ∝ speed², power ∝ speed³ (the affinity laws): at 80% speed the head is 64%: on a system with mostly **static** head the pump may not reach the lift at all; minimum speed limits.
- **Impeller trim**: the same laws approximately; a trimmed impeller is how a pump that was oversized gets put on its curve.
- **Worn pump**: the curve drops (lower head at the same flow) and the power line stays: efficiency loss; the sign of clearance/wear ring wear.

## Symptom table (most likely first)

| Symptom | Causes to check, in order |
|---|---|
| **No flow, no pressure at start** | Not primed / air-bound (vent it); **wrong rotation** (bump uncoupled: motor leads swapped); suction valve closed or strainer blocked; suction lift too high or foot valve stuck; speed low; coupling/key/impeller loose or broken; discharge valve closed with a bypass open |
| **No flow after running a while** | Loss of prime (air leak on suction, tank empty, vortex); vapour lock (hot liquid); strainer plugging |
| **Low flow** | Air leaks; partly blocked suction or impeller (rags, scale); worn impeller / excessive clearance / worn wear rings; system head higher than designed (a valve partly closed, a fouled line, a higher tank); wrong impeller diameter or speed; cavitation (NPSH); viscosity higher than designed; the wrong rotation (a backwards pump gives about half the flow and head: it does pump) |
| **Low head (pressure)** | Same as low flow; air in the liquid; impeller diameter too small; VFD speed |
| **Head/flow fine but too much power (amps high)** | Running out on the curve (open system, low head); SG or viscosity higher than the design; rubbing (impeller clearance too small, packing too tight, misalignment, bent shaft); wrong (larger) impeller or speed; the wrong rotation on some designs |
| **Loses prime repeatedly** | Air leaks in the suction line, packing, seal, gaskets; a foot valve leaking; a vortex; a submerged return aerating the tank; too much lift; gas coming out of solution (hot) |
| **Seal fails repeatedly (weeks)** | Running off-curve (low flow: deflection; dry-running on loss of prime); cavitation; **pipe strain**; misalignment; shaft runout, bent shaft, worn bearings; wrong seal flush or a plugged flush line; no seal setting done after an impeller adjustment; a bad seal installation (see [seal replacement](/article/mechanical-seal-replacement-centrifugal-pump)) |
| **Bearing fails repeatedly** | Misalignment; pipe strain; running off-curve (radial thrust); wrong oil level (constant-level oiler set wrong, or over-filled), water in the oil (a bad breather, washdown); over-greasing; cavitation/recirculation vibration; a bent shaft; unbalance |
| **Vibration** | Misalignment (2× running speed), unbalance (1×; a plugged or eroded impeller), cavitation/recirculation (random, broadband), bearings (high-frequency), looseness (foot bolts, base, coupling), a bent shaft (1× axial), resonance of the base/piping, running off-curve, wear rings gone (rotor rub); see [vibration signatures](/article/vibration-signatures) |
| **Noise** | Cavitation/recirculation (above); bearings; a coupling rubbing the guard; the motor (fan, bearings); a resonant pipe |
| **Overheating pump** | Running at or near shut-off (dead-headed: the liquid boils in minutes on a hot service); low flow; rubbing; bearing oil |
| **Leak at the casing gasket** | Gasket, bolts uneven, casing corroded, pressure too high, thermal cycling |
| **Motor overloaded / trips** | Power causes above; the motor itself (voltage, single-phasing, overload setting); a jammed impeller |
| **Discharge pressure pulsing** | Air entrainment; cavitation; a check valve fluttering; two pumps in parallel fighting; a VFD hunting |

## Field checks in order

1. Gauges and amps (above); tank level and temperature; valve positions on suction and discharge, including any bypass and the recirculation line.
2. **Rotation** (bump uncoupled if in doubt; arrows on the casing).
3. Strainer ΔP or pull the basket; the suction line for air leaks (soap on a suction under vacuum shows nothing: **pressurise** the suction line or watch for bubbles in a sight glass; a vacuum gauge that reads high with the strainer clean = restriction).
4. Vent the casing at the top (a pump that spits air was air-bound).
5. Speed (a VFD display, a tachometer on the shaft).
6. Turn the shaft by hand (coupled, with lockout): free, no rub, no play.
7. Impeller clearance (the touch-and-indicator check, see [impeller clearance](/article/impeller-clearance-and-wear-rings)); impeller condition through the suction on small pumps.
8. Alignment, soft foot, pipe strain (indicators on the shaft while loosening flange bolts); the base and foot bolts.
9. Only then pull the pump: impeller (erosion, plugging, cracks, eye damage from cavitation), wear rings, shaft runout, bearings, seal faces.

## Priming, start-up and shutdown

**Centrifugal**

1. Rotation confirmed uncoupled; bearings lubricated (oil to the sight glass, the constant-level oiler primed); seal flush/quench lines open; guards on.
2. **Prime**: flooded suction: open the suction valve fully and **vent** the casing at the highest point until liquid runs solid (open the discharge valve slightly to let air move if the check valve traps it). Suction lift: fill through the priming connection with the foot valve holding, vent, or use the priming pump/eductor; self-priming pumps need the casing full to the priming line.
3. **Start against a closed or nearly closed discharge valve** (5-10% open) for a radial-flow pump (lowest power, no water hammer), then **open the discharge over 30-60 seconds** to the operating point; never run more than a minute or two dead-headed (heat), and never with the **suction** valve throttled (cavitation). Axial-flow and high specific speed pumps start with the discharge **open**.
4. Watch: pressures settle, amps within FLA, no cavitation noise, seal not spraying (a few drops from a new seal for a minute is normal), bearing housings warming slowly, vibration by feel.
5. **Shutdown**: close the discharge valve slowly (or let the check valve do it on a small pump), stop the motor, then close the suction if isolating; on hot services keep the seal flush on until cool; on freezing weather drain the casing.

**Positive displacement (gear, screw, lobe, piston, diaphragm)**

- **Never start against a closed discharge**: the pressure rises until something breaks; the **relief valve** on the pump or the line must be proven, and the discharge valve **open** at start.
- Prime; many PD pumps self-prime but not dry-running ones (gear pumps with mechanical seals: a few seconds dry ruins the seal): fill the casing.
- Check rotation (many PD pumps pump only one way, and some reverse their relief valve with rotation).
- Viscosity and temperature govern the speed and the suction line size; cold thick oil cavitates a PD pump like water cavitates a centrifugal (a rattle and a fluctuating discharge).

## Common mistakes

- Calling every noise cavitation and raising the tank when the pump was running at 20% of BEP and recirculating.
- Throttling the **suction** to "reduce flow".
- Running a pump backwards for a week because it "pumped a bit".
- Replacing three seals before checking pipe strain.
- Starting a centrifugal with the discharge wide open into an empty line (water hammer and a tripped motor), or a PD pump with it closed (a burst gauge).
- Never venting: the pump "primed" with a bubble in the eye.

## Related

- [Pump and fluid-power formulas (NPSH, affinity laws)](/article/pump-and-fluid-power-formulas)
- [Impeller clearance and wear rings](/article/impeller-clearance-and-wear-rings)
- [Mechanical seal replacement](/article/mechanical-seal-replacement-centrifugal-pump)
- [Pump packing and stuffing box](/article/pump-packing-and-stuffing-box)
- [Pipe strain and flange alignment](/article/pipe-strain-and-flange-alignment)
- [Vibration signatures](/article/vibration-signatures)
- [Seal failure patterns](/article/seal-failure)
