---
title: "How to Read a Pump Curve Sheet: Head-Capacity Curve, Impeller Trim Lines, Efficiency Islands, Power and NPSHr Curves, Best Efficiency Point, Finding the Operating Point on a Manufacturer Data Sheet"
slug: how-to-read-a-pump-curve-sheet
category: manuals
kind: reference
manufacturer: "Goulds / Flowserve / Grundfos / KSB / Sulzer (generic)"
model_numbers: ["Goulds 3196", "Goulds 3656", "Flowserve Durco Mark 3", "Grundfos CR", "KSB Etanorm", "Sulzer CPT"]
tags: [pump curve, how to read pump curve, head capacity curve, impeller trim, efficiency curve, BEP, best efficiency point, NPSHr, NPSH required, pump power curve, brake horsepower pump, system curve, operating point, pump data sheet, pump performance curve, Goulds 3196 curve, shut off head, run out]
source: "Goulds Pumps 3196 performance curve booklets and data sheet layout; Hydraulic Institute ANSI/HI 14.6 (rotodynamic pump test) and HI curve conventions; Flowserve Durco Mark 3 curve sheets; Grundfos CR curve booklet."
summary: "A manufacturer pump curve sheet holds five things: the head-capacity curves for each impeller diameter, the efficiency lines, the power curves, the NPSH required curve and the best efficiency point. This article walks through a typical ANSI end-suction sheet line by line, then shows how to find where your pump is actually running and whether that is a safe place."
---

## What is on the sheet

The header identifies the pump: model and size (for example 3x4-13 means 3 in discharge, 4 in suction, 13 in maximum impeller), speed (1750 or 3550 rpm for 60 Hz), curve number and the impeller pattern. The curves are drawn for water at 20 °C; viscous or dense liquids need correction.

![An annotated manufacturer pump curve sheet](/img/manuals/pump-curve-sheet-anatomy.svg)

*An annotated manufacturer pump curve sheet*

The plot has **flow** (US gpm or m³/h) along the bottom and **total head** (ft or m) up the side. Head is the energy per unit weight and does not depend on the liquid density, which is why pump curves use head and not pressure.

## Head-capacity curves

Several curves fan out from the top left, one per **impeller diameter** (13 in, 12 in, 11 in, down to the minimum trim). At zero flow each meets the axis at **shut-off head**; head falls as flow rises toward **run-out** at the right end.

- A steady, continuously falling curve is a **stable** curve. A curve that rises before it falls (a hump) is unstable near shut-off and should not be run there.
- Trimming the impeller lowers the whole curve: head falls roughly with the square of diameter, flow with the diameter, power with the cube.
- The pump delivers the head where its curve crosses the **system curve** (static lift plus friction, which rises with the square of flow). Closing a valve steepens the system curve and moves the point left and up.

## Efficiency

Efficiency is drawn either as islands (closed contours labelled 60, 65, 70 percent) or as lines sweeping up across the diameter curves. The peak of efficiency for each diameter is the **best efficiency point (BEP)**. The Hydraulic Institute preferred operating region is **70 to 120 percent of BEP flow**, and the allowable region about 50 to 120 percent.

Running far left of BEP (throttled) gives high radial load on the shaft, recirculation, vibration and seal problems; running far right gives cavitation risk and motor overload on an end-suction pump. Most bearing and seal failures on process pumps come from running far off BEP, not from the bearings.

## Power

Brake horsepower is drawn either as separate curves per diameter (usually lower on the sheet) or as slanted lines across the head curves. On an end-suction radial pump, power rises with flow, so the motor must cover the power at the **end of curve** (run-out) or you risk overloading it if the discharge is ever wide open. A **non-overloading** selection picks a motor larger than the run-out power.

BHP = flow (gpm) × head (ft) × specific gravity ÷ (3960 × efficiency).

## NPSH required

A separate curve near the bottom gives **NPSHr** in feet against flow. It rises steeply toward run-out. Your system must supply more than this: **NPSHa should exceed NPSHr by at least 3 ft or 10 percent, whichever is larger** (some services require more). NPSHr on the sheet is the 3 percent head-drop value, which means cavitation has already started at that point; the margin is not optional.

## Finding your operating point

1. Read the suction and discharge gauges with the pump running; correct for gauge elevation relative to the pump centreline and for velocity head if the pipe sizes differ.
2. Total head (ft) = (Pd − Ps in psi) × 2.31 ÷ specific gravity (plus the elevation and velocity corrections).
3. Draw a horizontal line at that head to the curve for your impeller diameter (from the nameplate or the last rebuild record); read the flow below it.
4. Compare with BEP. Check the power at that point against the motor amps.
5. If the point does not land on any diameter curve the impeller is worn, the speed is wrong, or the liquid is not water-like.

## Using the sheet for a rebuild or a change

- **New impeller diameter**: choose the trim whose curve passes through the required duty with a small margin; do not trim below the minimum diameter on the sheet.
- **Speed change** with a VFD: flow scales with speed, head with speed squared, power with speed cubed (affinity laws). Slowing a pump 20 percent saves about half the power.
- **Viscous liquids**: use the HI viscosity correction charts; efficiency drops fast above about 100 cSt.

## Where to file it

Attach the curve sheet, the data sheet and the sectional drawing to the pump's article under Manuals so the next person can find the impeller diameter, the clearances and the bearing numbers in one place.

## Related

- [Centrifugal Pump Troubleshooting](/article/pump-troubleshooting)
- [Pump and Fluid-Power Formulas](/article/pump-and-fluid-power-formulas)
- [Impeller Clearance and Wear Rings](/article/impeller-clearance-and-wear-rings)
- [How to Add a Manufacturer Manual or Datasheet to This Library](/article/how-to-add-a-manual)
