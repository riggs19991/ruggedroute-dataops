---
title: "Lube Routes and Single-Point Lubricators: Building a Lubrication Route (Survey, Tagging, Colour Codes, Route Sheets), Grease Gun Care and Calibration, Grease Fitting Types and Repairs, Automatic Single-Point Lubricators (Gas, Spring, Electromechanical: Setting the Rate), Centralised Grease Systems Basics, Oil Level Devices (Sight Glasses, Constant-Level Oilers) and Setting Them, Record-Keeping"
slug: lube-routes-and-single-point-lubricators
category: lubrication
kind: procedure
manufacturer: "Perma / SKF SYSTEM 24 / Trico / Lincoln (generic)"
model_numbers: ["Perma Classic", "Perma Star", "SKF SYSTEM 24 LAGD 125", "SKF TLSD", "Trico Opto-Matic oiler", "Lincoln Quicklub", "Graco", "Bijur"]
tags: [lube route, lubrication route, lubrication survey, lube tags, lube color code, grease gun, grease gun calibration, grease fitting, zerk fitting, grease fitting types, broken grease fitting, single point lubricator, automatic lubricator, Perma, SKF SYSTEM 24, lubricator setting, centralized lubrication, progressive divider, constant level oiler, Trico oiler, setting a constant level oiler, sight glass, oil level, lube records, CMMS lubrication, lubrication PM]
source: "Perma and SKF SYSTEM 24 single-point lubricator instructions (setting the discharge period, temperature effects, capacities); Trico constant-level oiler installation and setting instructions; Lincoln/Graco centralised lubrication system guidance; Noria/ICML lubrication program best practices (route design, tagging, colour coding, grease gun calibration); SKF Bearing Maintenance Handbook."
summary: "The routine side of lubrication that decides whether the right grease gets to the right point in the right amount every time: surveying and tagging every lube point, designing routes and route sheets, keeping and calibrating grease guns, fixing fittings, when and how to use automatic single-point lubricators and how to set their rate, how centralised systems work and fail, and how to set the oil level devices on bearing housings so the level is actually right."
---

## Survey and tag every point

![Colour and shape coded lube point tags](/img/lubrication/lube-point-tags.svg)

*Colour and shape coded lube point tags*

1. Walk every machine with the drawings and the manuals: list every **lube point** (grease fittings, oil fills, oilers, sight glasses, drains, centralised system reservoirs, chain oilers, coupling plugs), the **bearing or component** at each, the **lubricant** (from the maker's manual or the [selection rules](/article/grease-types-and-compatibility)), the **quantity** ([regreasing quantities](/article/regreasing-intervals-and-quantities)) and the **interval**.
2. **Tag** the point: a durable tag or a colour-coded disc/label at the fitting or the fill with the **lubricant code** (a colour and a symbol from the plant's lube chart: e.g. a red circle = polyurea motor grease, a blue square = EP 2, a green triangle = ISO 220 gear oil), the quantity and the interval; the same code on the grease gun, the drum and the transfer container. Nobody should have to remember which grease a point takes.
3. Mark **do-not-grease** points (sealed bearings, points that are on the centralised system, motors greased by the electrical crew) so a keen greaser does not blow the seals.
4. Add **sampling valves** and **relief fittings** where missing; replace broken fittings; bring hard-to-reach fittings out on **extension lines** (a hose or tube from the bearing to a fitting block at a safe height: a fitting you cannot reach safely is a fitting that is never greased; keep extension lines short and the same grease in them).

## Routes and route sheets

- Group points by **interval** (daily/weekly/monthly/quarterly) and by **area** so a route is a walk, not a hunt; a route sheet (or the CMMS task) lists each point in walking order with the tag code, lubricant, quantity (strokes for **that** gun), interval, and a box for "done / abnormal (temperature, purge condition, leak, noise)".
- Typical: a **daily** route (oil levels, sight glasses, auto-lubricator checks, drains, leaks), a **weekly** route (fast/dirty/wet bearings, chains), a **monthly** route (most pillow blocks, fans), a **quarterly** route (motors, gearboxes' levels and breathers), an **annual** (couplings, gearbox oil changes, breather changes, sample points).
- One person **owns** each route; the route is a PM work order with the sheet attached; abnormal findings become work orders (a bearing running hot on the route is the best early warning a plant gets).
- Review the routes yearly: intervals adjusted from the evidence (purge condition, temperatures, oil analysis, failures).

## Grease guns

- **One gun per grease**, labelled and colour-coded, loaded from **cartridges** (bulk loading takes in dirt and air unless from a filtered bulk loader); the coupler wiped and **capped** between points; a gun kept in a clean box, not the truck bed.
- **Calibrate** each gun: 10 strokes into a cup on a scale → grams per stroke, written on the gun; re-check when a gun is serviced or the grease changes; battery/pneumatic guns per stroke as well (they vary from 0.5 to 2 g).
- Guns develop 3,000-10,000 psi: enough to blow a seal or inject grease into a hand: never hold a fitting with a bare hand while pumping; a gun that will not pump (a plugged fitting) is not "pumped harder".
- Fittings: **standard 1/4-28 or 1/8 NPT hex-head (zerks)**, straight, 45°, 90°; **button-head** (large, on heavy equipment: their own coupler); **flush** (recessed); **pin/needle** (on small joints); metric M6/M8/M10; a **ball-check** inside each: a fitting that leaks grease back out or will not take grease (the check stuck or the fitting plugged with hardened grease) gets replaced (they are pennies). A **broken-off fitting**: an extractor (EZ-out) for the stub, or drill and re-tap; **relief fittings** (a spring-loaded vent, e.g. 1-5 psi) on the drain side of motors and blocks let the excess out instead of into the winding or through the seal.
- Couplers wear: a coupler that leaks at the fitting sprays grease and wastes the shot; replace it.

## Automatic single-point lubricators

A cartridge (30-500 mL) screwed onto the fitting that dispenses grease continuously over a set period (1-12 months): for points that are **hard or dangerous to reach**, need **frequent small amounts** (fans, conveyors, pumps in dirty/wet areas), or where a route is unreliable.

| Type | Drive | Setting | Notes |
|---|---|---|---|
| **Gas-driven (Perma Classic/Futura, SKF LAGD 125/60)** | An electrochemical or gas generator pushes a piston | Turn the dial/screw to the discharge period (1, 3, 6, 12 months) and **activate** (screw in the activator/pull the tab); mark the date | **Temperature-dependent**: the rate roughly doubles for each 10°C above 20°C and halves below: set a longer period on a hot bearing; not adjustable after activation; will keep pushing even if the fitting is blocked; **not for points that must not be over-greased at any time** |
| **Spring-driven (mechanical)** | A spring on a piston with a flow restrictor | Fixed rate by the orifice | Simple, cheap; rate changes with grease viscosity and temperature |
| **Electromechanical (Perma Star, SKF TLSD, Perma Pro)** | A motor/pump on a battery with electronics | Set the period on the dial (1-12 months) or the volume; a **status LED**; some are remote-monitored | **Temperature-independent**, accurate; can feed several points through a distributor; batteries and cartridges replaced; the choice for critical points |
| Pump-fed (Perma Pro MP, Lincoln) | A small electric pump with a reservoir | Programmed | Several points from one unit |

Setting the rate: quantity needed per interval from the [regreasing calculation](/article/regreasing-intervals-and-quantities) (e.g. 15 g every 4 weeks = 180 g/year): a **125 mL (about 110 g) cartridge** set to **6 months** gives about 18 g/month: right; a 60 mL set to 12 months gives 4.5 g/month: for a small motor bearing. Match the grease in the cartridge to the bearing (the lubricators are sold pre-filled with a few greases, or refillable); never a different thickener than the bearing has. Install: the lubricator **above** the fitting where possible, a short extension line (1/4" ID, under 3 ft for gas types, longer for electromechanical), the fitting and line **pre-filled** with grease so the first months' output goes into the bearing not the hose, the **date and setting written on the unit**, and a check on the daily route (the piston position/level window, the LED, grease at the seal). A lubricator that has run empty for a month is worse than a greaser.

## Centralised (automatic) lubrication systems

A pump (electric, air or hand) feeds a network of **metering valves** (progressive dividers: each piston moves the next, so one blocked outlet stops the whole block; or injectors on a single-line parallel system) to dozens of points on a timer. Millwright duties: keep the **reservoir filled** with the specified grease (NLGI 0-1 usually; a wrong grease plugs the dividers), check the **cycle indicator pin** on progressive systems moves each cycle (a stalled pin = a blocked line or bearing somewhere downstream, found by disconnecting outlets one at a time; a progressive system with one blocked outlet delivers nothing to any point), check the **pressure** and the **relief/vent** (a relief spitting grease = a blockage), inspect the lines for leaks and crushed tubing (a leak starves everything after it on a progressive block), confirm grease actually arrives at the far points (a purge at the seal), and replace the **filter** on the fill line. Adjust the timer from the evidence, not the default.

## Oil level devices

- **Sight glass / level window**: read with the machine **stopped** (unless the plate says running: circulating and some splash boxes) and **level**; the mark or the centre of the glass; a glass **darkened with varnish** or **fogged** is not a level: replace it (bull's-eye glasses fail slowly and lie).
- **Dipstick**: as marked; wipe, insert without screwing (or screwed, per the stick), read.
- **Constant-level oiler (Trico Opto-Matic, Oil-Rite)**: a bottle that feeds oil into the housing as the level drops, holding the housing level at the height set by the oiler's adjustable stem: it is only right if it was **set** to the housing's correct level. Setting: fill the housing to the correct level through the fill plug (the sight glass mark or the plug hole per the manual), then adjust the oiler's **body height (the stem/collar)** until the oil in the housing just meets the level in the oiler's lower cup (the level line on the oiler body), lock it; then fill the bottle. An oiler set too high overfills (hot, churning bearings); too low starves; a bottle that never needs topping up on a pump is an oiler that is not feeding (the vent plugged, the stem above the level) or a level too high. Keep the bottle **vented** per its type (closed systems need the vented cap or a vent line) and the bottle **full** (an empty bottle means the level is dropping: find the leak).
- **Oil rings / slingers, oil mist**: check the ring turns (a stopped ring = a starved sleeve bearing); the mist system's pressure and reclassifiers.
- Breathers on oil-lubricated housings: clean, desiccant where wet; a plugged breather pushes oil out of the seals.

## Records

Every route completion, every abnormal finding, every top-up (how much: a pump that takes a litre a month has a leak), every oil change (date, product, quantity, filter), every sample result, in the CMMS against the equipment; lubricant consumption per machine trended (a step change is a leak or a wrong setting); the lube chart (product, code, colour, where used) posted in the lube room and on the trucks; a lube-room audit yearly (labels, containers, drums, guns, sample bottles).

## Common mistakes

- Six unlabelled grease guns in the truck: the motor gets the EP moly.
- A fitting nobody can reach: never greased in ten years; the bearing ran dry and "nobody knew".
- Single-point lubricator on a 180°F bearing set to 12 months: empty in three.
- Progressive divider system "working" because the pump runs, while the cycle pin has been stalled for a month.
- Constant-level oiler bolted on at whatever height the last person left it.
- Grease added on the route "because the sheet says so" while the seal is already purging thick black grease and the housing is hot: the route sheet needs an "abnormal" box and someone who reads it.

## Related

- [Regreasing intervals and quantities](/article/regreasing-intervals-and-quantities)
- [Grease types and compatibility](/article/grease-types-and-compatibility)
- [Oil analysis and sampling](/article/oil-analysis-and-sampling)
- [PM checklists](/article/pm-checklists)
- [Pillow blocks and insert bearings](/article/pillow-block-and-insert-bearings)
