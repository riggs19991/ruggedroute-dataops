---
title: "Milling Basics and Keyway Cutting: The Vertical Mill (Bridgeport Type) and Its Controls, Tramming the Head, Work Holding in a Vise and on the Table, Edge Finding and Setting Zero, Cutters (End Mills, Face Mills, Woodruff and Keyseat Cutters) and Speeds and Feeds, Climb vs Conventional, Squaring a Block, Slotting, Cutting a Shaft Keyway and a Hub Keyway (Broaching), Drilling and Boring on the Mill, Portable Keyway Cutters"
slug: milling-basics-and-keyway-cutting
category: machining
kind: procedure
tags: [milling, vertical mill, Bridgeport, milling basics, tramming the head, tram, mill vise, edge finder, setting zero, DRO, end mill, 2 flute, 4 flute, roughing end mill, face mill, fly cutter, Woodruff cutter, keyseat cutter, milling speeds and feeds, chip load, climb milling, conventional milling, squaring a block, slotting, keyway cutting, cutting a keyway on a mill, shaft keyway, hub keyway, broaching a keyway, keyway broach, bushing broach, portable keyway cutter, boring head, milling safety]
source: "Machinery's Handbook (milling speeds, feeds, chip loads; keyseat dimensions); Bridgeport Series I manual; Technology of Machine Tools (Krar); duMONT keyway broach instructions; end-mill manufacturer data (Niagara, OSG); ANSI B17.1 keyseat depths."
summary: "The vertical milling work a millwright needs: setting up a Bridgeport-type mill and tramming it, holding and finding the work, choosing an end mill and running it at the right chip load, squaring a block and milling a slot, cutting a keyway in a shaft with an end mill or a Woodruff cutter to the ANSI depth, broaching a keyway in a hub or sprocket with a bushing set and an arbor press, boring an accurate hole with a boring head, and the safety rules for a machine whose cutter is always exposed."
---

## The machine

A **vertical knee mill** (Bridgeport and clones): the **head** (a variable-speed or step-pulley spindle with an R8 (or 40-taper) spindle, a **quill** that feeds down like a drill press with a fine-feed handwheel and a depth stop, a head that tilts and swivels), the **ram**, the **table** (X longitudinal, Y cross) on the **saddle** and the **knee** (Z: the table rises to the cutter), **table locks** for each axis, a **power feed** on X, and often a **DRO** (digital readout) on X-Y(-Z). Dials read 0.001" (0.200" per turn on most); backlash in the leadscrews means you approach a dimension from the **same direction** every time (or trust the DRO).

## Tramming the head

The spindle must be **square to the table** or a face-milled surface is dished, a bored hole is tapered and a slot is wider at the top:

![Tramming the head and cutting a shaft keyway](/img/machining/tram-and-keyway.svg)

*Tramming the head and cutting a shaft keyway*

1. A **dial indicator on an arm in the spindle** (a tramming bar or an indicator holder in a collet), the tip on the table (or on a parallel/ground plate on the table, or a ring gauge) at about a 6-10" radius.
2. Rotate the spindle by hand: read at **front and back** (the head's tilt about the X axis: the nod) and at **left and right** (the swivel about Y).
3. Adjust: loosen the head's bolts a little, tap or turn the adjusting worm until the front/back reads within **0.001" over the sweep** (and left/right), tighten in sequence, re-check (tightening moves it).
4. Tram after any head tilt, after a crash, and on a new job that matters.

## Work holding

- **Milling vise** (a 6" Kurt type): bolted to the table with its **fixed jaw trammed parallel to X** (an indicator along the jaw while traversing: within 0.001" over the jaw); the work on **parallels** so it sits above the jaws, tapped down with a dead-blow until the parallels are tight (no rock); a round part in a **V-block** or in the vise's V; soft jaws for finished surfaces; the work held on enough of its height (at least 1/3) to not lift under the cutter.
- **Table clamps** (T-slot clamps, step blocks, strap clamps: the clamp bar level or slightly higher at the bolt end, the bolt near the work): for plates and castings; **stops** against the work's edge on the side the cutter pushes; a **fixture plate** for repeat parts.
- **Angle plate**, **rotary table**, **indexing head** (dividing for bolt circles and gears), a **sine bar** for angles.
- Long shafts for keyways: in the vise's V (or two V-blocks clamped to the table) with the shaft **parallel to X** (an indicator along its top and its side), the shaft supported at the ends, and clamped so it cannot rotate (a clamp over the shaft, or a V-block with a strap).

## Finding the edge and setting zero

- **Edge finder** (a spring-loaded cylinder in a collet, 0.200" tip): at 800-1,000 rpm, bring it to the work's edge until it runs true, then **kicks** sideways: at that instant the spindle centre is **half the tip's diameter** (0.100") from the edge; set the DRO to −0.100" (or +) for that axis; repeat on the other axis; a **wiggler** or a coaxial indicator for holes; an electronic edge finder lights up on touch.
- **Centre of a shaft**: edge-find both sides and halve, or an indicator swept on the shaft's top with the spindle centred over the highest point (touch a dial indicator on the shaft from the side: the reading is symmetrical when centred).
- **Z zero**: touch the cutter to the work's top on a paper shim (0.003") or a feeler, set the quill's depth stop or the knee dial.
- Cutter **diameter compensation**: the centre-line zero plus or minus the cutter's radius for an edge cut.

## Cutters and speeds

| Cutter | Use |
|---|---|
| **2-flute end mill** | Aluminium, slotting (chips clear), plunging (centre-cutting) |
| **4-flute end mill** | Steel, side milling, finishing (a stiffer core, more teeth); most 4-flutes plunge poorly |
| **Roughing (corn-cob) end mill** | Fast stock removal in steel, less chatter |
| **Ball-nose** | Radii, fillets |
| **Face mill / fly cutter** (a single HSS bit in a holder) | Facing wide surfaces; the fly cutter is cheap and gives a fine finish on a Bridgeport |
| **Woodruff (keyseat) cutter** | Woodruff key pockets: sized by the key number |
| **Keyseat cutter / side mill on an arbor** (horizontal mill) | Long keyways on a horizontal mill |
| **Slitting saw** | Thin slots, cutting off |
| Boring head | Accurate holes of any size |
| Materials: HSS (general), cobalt (stainless, alloy), **carbide** (speed, hard materials, rigid machines) with TiN/TiAlN coatings | |

```
   rpm = (SFM × 3.82) ÷ cutter diameter
   feed (in/min) = rpm × number of flutes × chip load (in/tooth)
```

| Material | HSS SFM | Carbide SFM | Chip load (in/tooth): 1/4" cutter / 1/2" / 3/4"-1" |
|---|---|---|---|
| **Mild steel** | **70-100** | 300-500 | 0.001-0.002 / 0.002-0.004 / 0.004-0.006 |
| Alloy steel 4140 | 50-70 | 250-400 | slightly less |
| Stainless 304 | 40-60 | 200-300 | 0.001 / 0.002-0.003 / 0.003-0.005 (never light) |
| Cast iron | 60-80 | 250-400 | 0.002 / 0.003-0.005 / 0.005-0.008 |
| Aluminium | 250-400 | 800-1,500 | 0.002-0.003 / 0.004-0.006 / 0.006-0.010 |
| Brass/bronze | 150-250 | 500-800 | 0.002 / 0.003-0.005 / 0.005 |

Example: a 1/2" 4-flute HSS end mill in mild steel: rpm = 90 × 3.82 ÷ 0.5 = **690**; feed = 690 × 4 × 0.003 = **8 in/min** (a slow steady crank by hand, or the power feed); depth of cut per pass: up to 1/2 the diameter for slotting in steel (1/4" deep), full width; side cuts 1/4-1/2 × D deep radially and up to 1-1.5 × D axially. Aluminium at 2,000 rpm and 20 in/min with a 2-flute. Too slow a feed **rubs** (the cutter dulls and squeals); too fast breaks flutes; the chips should be small curled commas, not dust and not blue.

**Climb vs conventional**: **conventional** (the cutter's teeth enter the cut thin and leave thick, rotating **against** the table's feed direction) is safe on a manual mill with backlash; **climb** (the teeth enter thick, the cutter pulls the work along the feed) gives a better finish and longer tool life but on a mill with leadscrew backlash the cutter can **grab the table and pull it in** (a broken cutter, a ruined part); on a Bridgeport, climb only in light finish cuts with the table gibs snug and the backlash taken up, or with a ball-screw/CNC. Rule for hand milling: conventional for roughing; a light climb pass for the finish on the side of a slot.

## Squaring a block

1. Face the largest surface (surface 1) with a face mill or fly cutter (the work on parallels, clamped; one pass, a light finish pass).
2. Surface 1 against the **fixed jaw** (on a round bar between the work and the movable jaw so the work seats flat on the fixed jaw), an adjacent side up: mill it (surface 2: square to 1).
3. Surface 2 down on parallels, 1 against the fixed jaw: mill 3 (parallel to 2).
4. Surface 1 down, 2 against the fixed jaw: mill 4.
5. Ends: the block on end in the vise against the fixed jaw with a square, or on an angle plate: mill 5 and 6 to length.
6. Check with a square and a micrometer at the corners.

## Slots and keyways in a shaft

**Keyway sizes**: width and depth from [keys and keyways](/article/keys-and-keyways) (1" shaft: 1/4" wide, 1/8" deep in the shaft; 2" shaft: 1/2" wide, 1/4" deep; the shaft's "M" dimension from the keyseat bottom to the opposite side = D − depth − the chord correction).

**End-milled keyway (a closed keyseat with round ends, the common one):**

1. Shaft in V-blocks/the vise V, parallel to X (indicator on the top: within 0.001" over the keyway's length; and on the side), clamped against rotation; the keyway position marked (the shaft's top centre line found with the indicator: the spindle over the shaft's centre in Y).
2. Cutter: a **2-flute end mill of the keyway's width** (a 1/4" keyway: a 1/4" 2-flute, which cuts slightly over: measure the slot; a 4-flute wanders); an end mill cuts about 0.001-0.002" over its nominal size, so oversize key stock or an undersize end mill gives the fit you want: test on scrap.
3. **Centre the cutter over the shaft** in Y (edge-find both sides of the shaft and split, or the indicator method); lock the Y axis and the knee.
4. **Plunge** at the keyway's start to the depth (a 2-flute plunges; go in stages with the quill, or the knee), then feed along X at the chip-load feed to the keyway's end; a keyway to a shoulder: stop the feed at the end minus the cutter's radius.
5. Depth check: a depth micrometer from the shaft's top at the keyway's edge (the chord correction), or the key stock in the slot with a straightedge across the shaft (the key stands proud of the shaft's top by half its height less the chord correction; use the formula in the keys article); the width with a gauge block or the key: a **sliding fit** with no rock.
6. Deburr the edges; the end radius equals the cutter's radius: the key's ends are rounded to match.

**Woodruff keyseat**: the Woodruff cutter of the key's number (the number gives the width in 1/32" and the diameter in 1/8": a #808 is 8/32 = 1/4" wide, 8/8 = 1" diameter), centred over the shaft, fed in radially (the knee up) to the depth (the key's height minus its projection; the cutter's slow speed, about 60-80 SFM in steel); one plunge.

**Open keyway to the shaft's end** (for a sled-runner key): the same end-milling, run off the end; or a side-milling cutter on a horizontal mill.

**Long keyways on a large shaft** that will not fit the mill: a **portable keyseat cutter / keyway milling machine** (clamped on the shaft, a small motor and an end mill riding a rail along the shaft), or a **hand-held keyway cutter** (a die grinder with a cutter in a guide) for rough work; a **shaper** in an old shop; a machine shop with a horizontal mill for big shafts.

## Hub keyways: broaching

A keyway in a **bore** (a sprocket, a sheave, a coupling hub, a gear) is cut with a **keyway broach**: a bar with progressively taller teeth, pushed through the bore in a **bushing** (a sleeve sized to the bore with a slot for the broach) with an **arbor press** (or a hydraulic press), with **shims** behind the broach to take successive cuts:

1. Choose the **bushing** for the bore diameter (the broach set has bushings for standard bores: a 1" bushing with a slot for the 1/4" broach) and the **broach** for the keyway width (Style A/B/C by size; each broach cuts one width); the depth is reached with the set's **shims** (a 1/4" broach set: 2-3 passes: no shim, then one shim, then two).
2. Bushing in the bore (a collar type sits on the hub's face; the hub must sit **square** on the press table, on parallels over the hole so the broach can pass through); the broach in the bushing's slot, its teeth toward the hub, oiled (cutting oil on every pass).
3. **Press** the broach through **squarely** with steady pressure (the ram on the broach's end; a **broach follower/guide** if the broach could bow); the chips clear; the first pass cuts about a third of the depth.
4. Add a **shim** behind the broach, second pass; the second shim, third pass; check the keyway's depth with the key stock and the width for a **push fit**; some sets need a fourth pass for the full depth on bigger keys.
5. Deburr the keyway's edges; a **step key** or an **offset** if the shaft's and hub's keyways are different widths.
6. Rules: the broach and the bushing matched (a 1/4" broach in a 3/8" bushing slot cuts a crooked keyway); never hammer a broach; never press a bowed broach (it breaks: hardened, expensive); a hub that is not square on the table breaks it too; cast iron hubs broach dry; bronze and aluminium with oil; hardened hubs cannot be broached (EDM or a keyway shaper); a long hub (over about 2× the broach's cutting length) is broached from both sides or with a longer broach.

## Drilling and boring on the mill

- Drilling: the mill is a rigid drill press with a DRO: spot, drill, chamfer at the coordinates; the quill's fine feed for control; the [speeds](/article/drill-press-speeds-and-feeds).
- **Boring head**: an adjustable head with a boring bar, dialled in 0.001" steps on its diameter (or radius: read the head's scale); bore a drilled hole to size with light finish cuts (the head at the slow speed for its swing), measure with a bore gauge; the way to make a hole to a fit (a bearing housing bore, a bushing seat) on the mill.
- Tapping: a tapping head, or hand-tapped with the tap guided by a spring centre in the spindle.

## Safety

- The cutter is exposed and fast: **no gloves**, sleeves tight, hair, jewellery, lanyards off; safety glasses; a chip shield on aluminium.
- The work **clamped** so the cutter cannot lift or pull it; the vise on a trammed and cleaned table; parallels tight.
- The **drawbar** tight on the collet (a loose collet lets the end mill pull out and dive into the work); the spindle brake to hold while tightening; the wrench off before starting.
- Hands away from the cutter while it turns; chips cleared with a brush after it stops; never reach behind the cutter to clear a chip.
- Table feeds: know the limits and the stops; a power feed running into the column or the head.
- Speed changes on a variable-speed head **only with the spindle running** (the varidrive sheaves); on a step-pulley head, with the spindle stopped.
- Climb-milling grab on a manual machine; the quill locked when milling with the quill extended.
- The knee's crank removed after use (it swings into a knee); the table's ways clean.

## Common mistakes

- Milling a slot with a 4-flute end mill plunged in the centre: it drifts and the slot is 0.005" wide.
- A keyway cut with the shaft not indicated parallel: 0.010" deeper at one end.
- A hub broached sitting on a chip: the keyway is crooked and the broach is bent.
- The head out of tram after tilting for a chamfer; every face milled after is concave.
- Climb-milling a heavy cut on a worn Bridgeport: the table lurches and the end mill snaps.
- The DRO zeroed on the wrong side of the edge finder's tip.

## Related

- [Keys and keyways (sizes and depths)](/article/keys-and-keyways)
- [Lathe basics for millwrights](/article/lathe-basics-for-millwrights)
- [Drill press speeds and feeds](/article/drill-press-speeds-and-feeds)
- [Layout tools and scribing (keyway layout)](/article/layout-tools-and-scribing)
- [Grinding and abrasives safety](/article/grinding-and-abrasives-safety)
