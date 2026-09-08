---
title: "Welding Positions and Techniques: 1G-6G and 1F-4F Explained, Travel and Work Angles, Stringer vs Weave, Vertical-Up and Vertical-Down, Overhead, Restarts and Tie-Ins"
slug: positions-and-techniques
category: welding
kind: procedure
tags: [welding positions, 1G, 2G, 3G, 4G, 5G, 6G, 1F, 2F, 3F, 4F, flat, horizontal, vertical up, vertical down, overhead, travel angle, work angle, drag angle, push angle, stringer bead, weave, whip and pause, restart, tie in, multi pass, cover pass, root pass, hot pass]
source: "AWS A3.0 and D1.1 position definitions; ASME IX QW-461 position figures; Lincoln Electric Stick Electrode Welding Guide (out-of-position section); Hobart and Miller technique guides."
summary: "What each position code means for plate and pipe, the angles and bead types that work in each one for stick, MIG, flux-core and TIG, how to lay multi-pass welds, and how to restart and tie in without defects."
---

## Position codes

**Groove welds (G)** and **fillet welds (F)**; the number is the position.

![1G to 4G and 1F to 4F on plate; 1G, 2G, 5G and 6G on pipe](/img/welding/positions.svg)

*1G to 4G and 1F to 4F on plate; 1G, 2G, 5G and 6G on pipe*

| Code | Plate | Pipe | The weld runs |
|---|---|---|---|
| **1G / 1F** | Flat | Pipe rolled, weld on top | Flat, puddle sits on top of the joint; easiest, hottest settings |
| **2G / 2F** | Horizontal | Pipe vertical, weld horizontal around it | Horizontal: gravity pulls the puddle down onto the lower plate |
| **3G / 3F** | Vertical | - | Vertical-up (structural) or vertical-down (sheet, pipeline root) |
| **4G / 4F** | Overhead | - | Overhead: gravity pulls the puddle off the plate |
| **5G** | - | Pipe horizontal, **fixed**; weld goes flat → vertical → overhead | All positions in one joint |
| **6G** | - | Pipe fixed at **45°** | All positions plus an angle; the all-position qualification test |
| 6GR | - | 6G with a restriction ring | Tests reach and access |

Qualifying in a harder position qualifies the easier ones: 3G+4G plate qualifies all plate positions; 6G pipe qualifies everything for that diameter range and process.

**Which side of the plate the weld runs on and where the plate is** define position; a fillet in a corner that is flat but on a tilted structure counts as whatever the joint angle makes it (D1.1 Figure 5.4 position diagram; ±15° of flat still counts as flat).

## The two angles

![Travel angle and work angle](/img/welding/smaw-angles.svg)

*Travel angle and work angle*

- **Work angle**: the angle between the electrode and the plate surface, measured across the joint. Fillet: split the corner, **45°** (bias toward the thicker plate); butt: **90°**.
- **Travel angle**: the tilt along the direction of travel. **Drag (pull)**: electrode points back at the finished weld: stick, flux-core, "drag if slag". **Push**: electrode points ahead into the unwelded joint: MIG with solid wire, TIG.

| Process | Travel angle | Work angle (fillet) |
|---|---|---|
| Stick | 5-15° drag | 45°, 30° from the vertical plate on horizontal fillets |
| MIG solid wire, short-circuit | 5-15° push (drag allowed on thick, more penetration) | 45° |
| MIG spray | 5-10° push | 45° |
| FCAW (gas and self-shielded) | 5-20° drag | 45° |
| TIG | 10-15° push, filler 15-20° from the plate | 45° |
| Overhead, any process | Keep 0-10°, more angle drips | 45° |

## Bead types

- **Stringer**: straight, no or minimal oscillation. Standard for root passes, flux-core, spray MIG, stainless and anything under a code that limits weave width. Low heat input, more passes.
- **Weave**: side-to-side, pausing at the toes, straight across the middle. Vertical-up fills and caps, wide gaps. Max width: about **3/8-5/8" with stick** (most WPSs limit it to a multiple of the electrode diameter); D1.1 limits vertical weaves through the WPS. Wider weaves = more heat input, slower, undercut at the toes if you do not pause.
- **Whip and pause** (E6010/6011 only): push the arc ahead 1/4-1/2" to let the puddle freeze, come back and pause. For open roots and vertical-up with fast-freeze rods; never with 7018.
- **Triangle / inverted-V weave**: vertical-up on fillets and open grooves: a shelf builds under the puddle.
- **Keyhole**: on open-root pipe, the root is welded by keeping a small hole open ahead of the puddle; the hole size is the gap plus about a rod diameter. See [plasma keyholing and piercing](/article/plasma-keyholing-and-piercing) for the cutting meaning.

## Position by position

### Flat (1G/1F)

Hottest settings from the charts; the puddle supports itself. Fillet: 45° work angle, 10-15° drag or push, stringer or slight weave. Big single-pass fillets (5/16") are fine here. Put the arc on the leading edge of the puddle and let the puddle size set the travel speed.

### Horizontal (2G/2F)

Gravity sags the puddle onto the bottom plate: undercut on the top toe and overlap on the bottom.

- Work angle **30-45° up from the bottom plate** on fillets (aim the arc slightly at the lower plate, it needs less heat), electrode tilted 5-15° drag.
- Grooves: stringers only, **start at the bottom of the groove and work up**, each bead overlapping the one below by half; keep the last bead on the top bevel tight to avoid undercut.
- Drop amperage 5-10% from flat with stick.

### Vertical-up (3G/3F)

Structural standard: full penetration, slow, hot enough to fuse but cool enough to hold.

- Amps **10-15% below flat**; 7018 3/32" ≈ 80-100 A, 1/8" ≈ 100-125 A; MIG short-circuit drop 1-2 V and WFS 10-20%; FCAW at the low end of the chart.
- Work angle 90° to the plate, travel angle **0-10° up** (rod pointing slightly up, never down).
- Root: stringer or tight triangle weave with a short pause each side to build the shelf. Fill: weave, pausing at the toes and moving fast across the centre. Cap: a wider weave, pausing to fill the toes, keeping the puddle ahead of the slag.
- If the puddle sags, you are too hot or too slow at the centre; if it looks ropey and cold, more heat or a shorter arc.

### Vertical-down (3G/3F down)

Sheet metal and pipeline root passes (E6010 on API 1104 pipe). Fast, shallow, needs a **fast-freeze** electrode (E6010/6011/6013) or short-circuit MIG/self-shielded FCAW. Point the electrode **5-15° up**, keep the arc on the leading edge so the slag stays behind. Not allowed on structural fills with low-hydrogen stick (slag runs ahead and gets trapped).

### Overhead (4G/4F)

- Amps like vertical or a touch higher; **short arc**, stringers or tight weaves, 0-10° travel angle. Keep the puddle small; if it starts to drip, move on and come back.
- 7018 overhead: hold a very short arc and a steady rhythm. MIG: short-circuit, lower voltage, a gas nozzle that is clean, flow 5 cfh above flat if drafts.
- Wear leathers, a cap, and no open pockets: sparks fall on you.

### Pipe 5G and 6G

Root (E6010 open root or TIG), hot pass, fill and cap, each pass **around the pipe in halves** from bottom (6 o'clock) to top (12 o'clock) so the whole weld is vertical-up, or downhill root then uphill fill on some pipeline procedures. Change your angle continuously to keep the electrode perpendicular to the pipe surface at every clock position. Grind the start and stop of each half to a taper so the next tie-in fuses.

## Multi-pass welds

1. **Root**: penetration and fusion at the root, nothing else. 1/8" 6010 or 3/32" TIG on pipe; 3/32 or 1/8" 7018 in a backed groove.
2. **Hot pass** (pipe): right after the root, hotter, to burn out root wagon tracks and reinforce a thin root before it cracks.
3. **Fill**: stringers or weaves, each bead **overlapping the previous by 1/3 to 1/2**, never leaving a deep valley between beads. Keep the fill about 1/16" below the plate surface for the cap. Clean every pass (chip, wire brush, needle scale if needed).
4. **Cap / cover**: one wide weave or multiple stringers that stand **1/16-1/8" high**, toes fused, no undercut. A cap wider than the groove by 1/16-1/8" each side is right.
5. Watch **interpass temperature**: check with a temp stick before each pass (see [preheat and interpass](/article/preheat-interpass-and-carbon-equivalent)).

## Starts, stops and tie-ins

- **Stick restart**: strike **1/2" ahead** of the crater, move back into the crater, fill it, then carry on. Chip the crater first on 7018.
- **MIG/FCAW restart**: start on the crater itself with a slightly longer stickout, then normal.
- **Ending**: fill the crater: reverse the travel briefly (stick), let the machine's crater-fill do it (MIG), or pedal down slowly (TIG). Craters left open crack, especially on stainless and aluminium.
- Tie-ins on pipe halves: grind the previous stop to a taper, start 1/2" back on the taper, pause a beat at the low spot.
- Arc strikes outside the weld are defects on code work: strike inside the joint or on a run-on tab.

## Common mistakes

- Travel angle too steep (over 20°): shielding is lost, spatter, porosity, undercut.
- Weaving with 6010/6011 like it was 7018: it works, but pause at the toes or you undercut everything.
- Vertical-down with 7018: slag inclusions in every bead.
- Not tapering the tacks and stops: cold laps at every tie-in.
- Changing the angle at the end of a bead to "wash it in": undercut and overlap.

## Related

- [Joint design and fit-up](/article/joint-design-and-fit-up)
- [Stick setup](/article/smaw-stick-setup), [MIG setup](/article/gmaw-mig-setup), [flux-core](/article/fcaw-gas-shielded-setup), [TIG](/article/gtaw-tig-setup)
- [Weld defects and inspection](/article/weld-defects-and-inspection)
