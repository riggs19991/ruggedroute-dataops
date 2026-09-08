---
title: "Roller Chain Drives: Chain Numbers, Sprocket Alignment, Sag, Wear Limits and Lubrication"
slug: roller-chain-drives
category: power-transmission
kind: procedure
tags: [roller chain, ANSI chain, chain pitch, sprocket alignment, chain sag, chain elongation, chain wear, master link, offset link, chain lubrication, chain breaker]
source: "ANSI B29.1; chain manufacturer (Tsubaki, Diamond, Renold) maintenance guides."
summary: "Reading ANSI chain numbers, aligning sprockets, setting chain sag to 2-4% of span, measuring elongation against the 3% (1.5%) wear limit, connecting-link and offset-link rules, and the four ANSI lubrication types."
---

## ANSI chain numbers

The number tells you the pitch. **Divide the first digit(s) by 8 for pitch in inches.**

| Chain no. | Pitch | Roller diameter | Notes |
|---|---|---|---|
| 25 | 1/4" | rollerless | |
| 35 | 3/8" | rollerless | |
| 40 | 1/2" | 5/16" | Common on small drives |
| 41 | 1/2" | 0.306" | Narrow, light-duty |
| 50 | 5/8" | 0.400" | |
| 60 | 3/4" | 15/32" | |
| 80 | 1" | 5/8" | |
| 100 | 1 1/4" | 3/4" | |
| 120 | 1 1/2" | 7/8" | |
| 140 | 1 3/4" | 1" | |
| 160 | 2" | 1 1/8" | |

Last digit: **0** = standard roller chain, **1** = lightweight, **5** = rollerless (bushed). Suffix **H** = heavy series (thicker plates, e.g. 80H). **-2, -3** = double or triple strand (80-2). Metric ISO chains use "B" numbers (08B = 1/2" pitch, 16B = 1").

## Sprockets

- Tooth count and pitch must match the chain. Hardened teeth for high speed or abrasive service.
- Worn sprocket teeth look **hooked** (undercut on the driving side). Replace chain and sprockets together; a new chain on hooked sprockets wears out in weeks.
- Minimum 17 teeth on the small sprocket for smooth running at speed; odd tooth counts spread wear.

## Alignment

![Chain sag, sprocket alignment and wear measurement](/img/power-transmission/chain-sag-and-wear.svg)

*Chain sag, sprocket alignment and wear measurement*

1. Shafts **parallel**: check with a rule or feeler between shafts at two points, or a level on each.
2. Sprockets **in the same plane**: straightedge across the machined faces of both sprockets should touch at four points. For long centres use a string or a laser.
3. Lock the sprockets with the correct key, set screws (on flats) or bushing.

## Chain length and connection

- Use an **even number of pitches** whenever possible so a standard connecting (master) link fits. An odd number requires an **offset link**, which is weaker (about 30% derating); avoid it on hard-working drives.
- Cut chain with a chain breaker or a grinder on the pin heads, never by hammering a pin through a riveted plate.
- Connecting link: spring clip **closed end faces the direction of travel** so the open end cannot be peeled off. On heavy chain use a cotter-pin or riveted connecting link.

## Sag (tension)

Chain is not tensioned like a belt. It needs slack on the return side.

- Horizontal or slightly inclined drives: sag at mid-span on the slack side = **2 to 4% of the span length** (some makers allow up to 6% on slow drives). A 40" span: 0.8" to 1.6" sag.
- Vertical or steep drives (over 60°): sag **1 to 2%**, and use an idler or tensioner because gravity works against you.
- Measure by pulling the chain taut on the slack side and then letting it drop, reading the total movement with a rule against a straightedge.
- Adjust with the motor slide base or an idler sprocket on the slack side, **outside** of the chain (idler on the back of the chain) where possible, and re-check alignment.

## Wear (elongation) limit

Chain "stretches" because pins and bushings wear. Measure over a length of chain under light tension:

```
Elongation % = (measured length - nominal length) / nominal length × 100
Nominal length = number of pitches × pitch
```

- Replace at **3% elongation** for normal sprockets.
- Replace at **1.5%** when the large sprocket has **more than 67 teeth** (the chain rides out on the teeth sooner).
- Example: 24 pitches of #80 = 24" nominal. Measured 24.72" → 3% → replace.
- Chain wear gauges (go/no-go) do this in one step.

Do not tension a drive to take up wear elongation. The pitch no longer matches the sprocket and both wear out fast.

## Lubrication (ANSI types)

| Type | Method | Typical chain speed |
|---|---|---|
| A | Manual (brush or oil can) every 8 hours | slow |
| B | Drip lubricator | moderate |
| C | Oil bath or slinger disc in a case | fast |
| D | Pump/forced stream | very fast or high hp |

Oil must reach the **pin-bushing joint**: apply on the inside edge of the link plates on the slack side, just before the chain enters the sprocket. A dry, red-brown chain has already lost most of its life. Grease does not penetrate the joint; use oil (ISO VG 68-150 depending on temperature) unless the chain is a lube-free type.

## Installation checklist

1. Lockout/tagout, guard off.
2. Inspect sprockets, align shafts and sprockets.
3. Fit chain, connect with the right link, clip closed end forward.
4. Set sag 2-4%.
5. Lubricate.
6. Rotate by hand, check nothing binds.
7. Guard on, run, listen. A tight-then-slack "whip" means misalignment or a bent shaft.

## Related

- [V-belt drives](/article/v-belt-drive-installation-and-tensioning)
- [Couplings: types, gap and installation](/article/coupling-types-gap-and-installation)
