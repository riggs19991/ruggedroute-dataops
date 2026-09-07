---
title: "Stick Welding (SMAW) Setup: Machine, Polarity, Rod Choice, Striking, Arc Length, Angles, Restarts and Troubleshooting"
slug: smaw-stick-setup
category: welding
kind: procedure
tags: [stick welding, SMAW, arc welding setup, polarity, DCEP, striking an arc, arc length, travel angle, work angle, whipping, weave, restart, crater, slag, arc blow, undercut, porosity, buzz box, engine drive, arc force, hot start]
source: "Lincoln Electric Stick Electrode Welding Guide (C2.410); Miller Stick welding guides; AWS Welding Handbook Vol. 2."
summary: "Everything between plugging in the machine and laying a sound stick bead: constant-current machines and their controls, polarity, ground placement, choosing and setting the rod, the strike, arc length, travel and work angles by position, whip and weave techniques, restarts and crater fills, and a symptom-based troubleshooting table."
---

> Stick welding is the field millwright's process: one cable, one clamp, a box of rods, and it works on rusty steel in the wind. Setup is simple, which is why most bad stick welds come from the three things you control: **arc length, angle and speed**.

## 1. The machine

Stick needs a **constant-current (CC)** power source: the amperage stays where you set it while the voltage swings with arc length. A MIG-only machine (constant voltage) will not stick weld well; a multi-process machine must be switched to "Stick / CC".

| Control | What it does | Typical setting |
|---|---|---|
| Amperage (output) | The one knob that matters | From the [electrode chart](/article/smaw-electrode-chart); mid-range to start |
| Polarity switch or cable swap | DC+ / DC− / AC | DC+ for E6010, E7018; DC− for E6012/E7014 on sheet; AC for AC rods and arc blow |
| Arc force / "dig" (inverters, engine drives) | Adds current when the arc shortens; stops the rod sticking on E6010, helps roots | 30-50% for 6010, 10-20% for 7018 |
| Hot start | Extra amps for the first fraction of a second | On for 7018 starts |
| Duty cycle | How long you can weld per 10 minutes at that amperage | Check the nameplate; see [machine setup](/article/machine-setup-and-duty-cycle) |

Engine drives (Bobcat, Ranger, Trailblazer): set to CC-Stick, check the fuel, run at high idle before striking, keep the exhaust downwind of you.

## 2. Cables and ground

- Cable size for the amperage and total length: [cable chart](/article/machine-setup-and-duty-cycle).
- **Ground clamp** on clean bare metal, as close to the weld as practical, on the same piece (not through a bearing, a hinge, a chain or a machine table with a rotating part between clamp and weld: welding current through a bearing pits the raceways).
- Electrode holder jaws clean and tight; a hot holder handle means a loose cable lug.

## 3. Pick the rod

1. Steel type and strength → class (E60XX for mild steel general; E70XX for structural; low-alloy for special steels).
2. Position → E6010/E6011/E7018 for vertical and overhead; E7024/E7028 only flat and horizontal.
3. Condition → cellulose (6010/6011) for rust, paint, mill scale and open roots; low-hydrogen (7018) for thick, restrained or high-strength.
4. Diameter → about the plate thickness for 1/8-3/16" plate; one size down for thinner; 5/32 or 3/16 for fill on thick plate. Never a rod bigger than the plate.
5. Low-hydrogen rods come **from the oven**, not the truck floor. See storage rules in the chart article.

## 4. Set the amperage

- Chart mid-range for the diameter. Example: 1/8" E7018 DC+ → about 120 A flat, 110 A vertical/overhead.
- Rule of thumb: 1 A per 0.001" of core wire diameter (1/8" ≈ 125 A), 6010 20% less.
- **Too cold**: rod sticks, arc stutters, tall narrow bead sitting on top with slag trapped at the toes.
- **Too hot**: wide flat bead, heavy spatter, undercut along the edges, coating glows red and burns back, crater porosity.
- Adjust in 5-10 A steps and listen: a good arc sounds like frying bacon; 7018 hums.

## 5. Strike and run

1. **Position yourself** so you can see the puddle and move the whole bead length without shifting your feet. Brace the rod hand against the work or your other hand.
2. **Strike**: scratch (like a match, then lift to arc length) or tap (touch and lift). Strike in the joint where the weld will cover the mark; stray arc strikes are defects on code work.
3. **Arc length** ≈ the rod core diameter (1/8" rod → 1/8" arc). 7018 short and tight; too long an arc on 7018 gives porosity and a wide, ropy bead. 6010 tolerates a longer arc when whipping.
4. **Angles**:
   - **Work angle**: fillet welds 45° between the plates (aim at the root); groove welds 90° to the plate.
   - **Travel angle**: **drag** 5-15° (rod tips back toward the finished weld) for stick on steel. "Drag if there's slag."
5. **Travel speed**: watch the puddle, not the arc. The slag should trail behind the puddle, never run ahead. Bead width about 2-2.5× rod diameter for a stringer.
6. **Techniques**:
   - **Stringer**: straight line, no side motion. Default for 7018 and for all root passes.
   - **Whip** (6010/6011 only): move the rod ahead 1/2-3/4" out of the puddle for an instant to let it freeze, then back. Used vertical-up and on open roots.
   - **Weave**: side-to-side, pause at each toe, never wider than 2.5× rod diameter (code limit) and never on 7018 vertical without a pause at the edges (undercut).
   - **Vertical up** (plate over 3/16"): 6010 whip on the root, then box/straight weave; 7018 slight side-to-side "Z" or upside-down "V", 10° drag, 10-15% less amperage.
   - **Vertical down** (sheet up to 3/16"): 6010/6011/6013, fast, 30-60° drag, keep the arc on the leading edge ahead of the slag.
   - **Overhead**: short arc, stringers only, rod angled 10-15° drag, amperage at the low end. Weave beads sag.
7. **Crater**: at the end of a bead, pause and back up a fraction, then lift the rod straight up. A hollow crater cracks.
8. **Restart**: chip and brush the crater, strike 1/2" ahead of the crater, bring the arc back into the crater, fill it, then move on. On 7018 grind the end of the previous bead to bright metal before restarting for code work.
9. **Clean** every pass: chip, wire brush, look. Slag left in the toes is inclusion in the next pass.

## 6. Multi-pass rules

- Root, hot pass, fill, cap. Each pass cleaned.
- Keep the plate within the **interpass temperature** limits (see [preheat and interpass](/article/preheat-interpass-and-carbon-equivalent)).
- Fillet leg size: one pass of 1/8" 7018 gives about a 3/16" fillet; 5/32" gives 1/4"; larger fillets are multi-pass, with the first pass in the root and the next ones stacked from the bottom plate up.

## 7. Troubleshooting

| Symptom | Cause | Fix |
|---|---|---|
| Rod sticks on start | Amps too low, damp 7018, long rod stub bent, wrong polarity | Raise amps 10%, hot start/arc force on, fresh rod |
| Arc wanders, blows toward the end of the joint | Arc blow (DC on magnetised steel) | Move ground, weld toward the ground, AC, wrap ground cable around part |
| Porosity (holes in the bead) | Damp rod, long arc, rust/paint/oil/moisture, wind on a cellulose puddle | Oven-dry 7018, tight arc, grind the joint, block wind |
| Undercut at the toes | Too hot, arc too long, weave too fast at the edges, wrong angle | Lower amps 10%, pause at toes, correct work angle |
| Slag inclusions | Slag ran ahead (too slow/wrong angle), poor cleaning, cold lap | Steeper drag, faster travel, chip and brush every pass |
| Cold lap / lack of fusion | Amps too low, travel too fast, bead rolled onto plate | Raise amps, aim the arc at the root |
| Cracks in the centreline | Deep narrow bead (too hot/too fast), high carbon, restraint, hydrogen | Preheat, 7018 from the oven, flatter bead, slower cooling |
| Crater cracks | Pulled out fast | Fill the crater |
| Spatter everywhere | Too hot, long arc, wrong polarity, damp rod | Lower amps, short arc, check DC+ |
| Rod coating burns back unevenly / one side | Rod eccentric or damp | Change rod |
| Bead too narrow and tall | Too cold or too fast | Raise amps, slow down |

## 8. Shutting down

Rods back in the oven, holder hung where the rod cannot touch ground, machine off, cables coiled, hot work area checked 30 minutes later.

## Related

- [Stick electrode amperage chart and rod storage](/article/smaw-electrode-chart)
- [Welding positions and techniques](/article/positions-and-techniques)
- [Joint design and fit-up](/article/joint-design-and-fit-up)
- [Weld defects and inspection](/article/weld-defects-and-inspection)
- [Welding safety: lens shades, fumes, PPE](/article/welding-safety-fumes-and-ppe)
