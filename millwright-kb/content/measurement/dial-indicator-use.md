---
title: "Dial Indicators: Types, Setup, Reading Runout and Avoiding Cosine Error"
slug: dial-indicator-use
category: measurement
kind: procedure
tags: [dial indicator, test indicator, plunger indicator, magnetic base, runout, TIR, cosine error, preload, revolution counter, indicator sag]
source: "Starrett, Mitutoyo and Interapid instructions; general practice."
summary: "Plunger (AGD) versus lever (test) indicators, how to mount them so the reading is real, measuring shaft and hub runout, reading TIR and sign, and the cosine-error correction for tilted test indicators."
---

## Two kinds

| | Plunger (AGD dial indicator) | Lever (dial test indicator) |
|---|---|---|
| Movement | Plunger travels in a straight line, 0.25-1" range | Small stylus swings, 0.008-0.030" range |
| Resolution | 0.001" (or 0.0005", 0.0001") | 0.0005" or 0.0001" |
| Reads | Linear travel: alignment, soft foot, end float, runout on large surfaces | Fine runout in tight spots, bore checks, squaring a vise |
| Sign | Clockwise = plunger pushed in = **positive** (most makes) | Reversible lever; watch which way the needle moves when you push the stylus |

## Mounting

1. **Rigid** is everything. A magnetic base on a clean, flat, ferrous surface; the shortest arms you can use; every joint tight. A floppy setup reads its own wobble.
2. Plunger **square** to the surface you are measuring (within a few degrees). A tilted plunger reads less than the true movement.
3. **Preload** the plunger about a third of its travel so it can read both directions, then zero by turning the bezel. Lock the bezel.
4. Move the surface through its full travel once, watching that the plunger stays in range and does not bottom out.
5. Tap the base lightly and confirm the needle returns to zero: if it drifts, the setup is loose.

## Runout on a shaft

![Measuring runout and avoiding cosine error](/img/measurement/dial-indicator-runout.svg)

*Measuring runout and avoiding cosine error*

1. Support the shaft in its own bearings (or V-blocks for a loose shaft).
2. Plunger on a clean, unpainted part of the shaft, square to it.
3. Rotate the shaft slowly one full turn. The **total swing** of the needle (highest minus lowest) is the **TIR** (total indicator reading). A shaft that is bent 0.002" reads 0.004" TIR.
4. Mark the high spot. Check in two planes to tell a bend from an eccentric journal.
5. Typical limits: pump/motor shafts at the coupling **≤ 0.002" TIR**; coupling hub rim and face ≤ 0.002"; sheave/sprocket face ≤ 0.005" per foot of diameter.

## Face runout and squareness

Plunger axial on a face, sweep one revolution: TIR is the face runout (wobble). For a stuffing-box face, hold the indicator on the shaft and sweep the fixed face.

## End float

Indicator axial on the shaft end. Push the shaft fully one way, zero, push the other way, read. That is the end float. Compare to the bearing arrangement limits (sleeve-bearing motors have 1/4"; anti-friction bearings should be near 0.002").

## Cosine error (test indicators)

A lever indicator only reads true when the stylus is **parallel to the surface** (perpendicular to the movement being measured). If the stylus is tilted at angle θ to the surface, the needle reads **more** than the true movement. Correct it:

```
True movement = Reading × cos θ
```

| Stylus angle | Multiply reading by |
|---|---|
| 0° | 1.000 |
| 10° | 0.985 |
| 20° | 0.940 |
| 30° | 0.866 |
| 45° | 0.707 |

Keep the stylus under 10° and ignore it; over that, correct or re-mount.

## Care

- Do not drop it. A dropped indicator sticks and repeats badly; test on a gauge block stack before trusting it.
- Keep the plunger clean and dry; no oil on the rack.
- Store in the case, plunger free.
- Check zero repeatability and a known step (gauge blocks) periodically; replace an indicator that will not repeat within one division.

## Related

- [Reading a micrometer](/article/reading-a-micrometer)
- [Rim-and-face alignment](/article/rim-and-face-alignment)
- [Soft foot correction](/article/soft-foot-correction)
