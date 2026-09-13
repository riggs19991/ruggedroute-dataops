---
title: "Hydraulic Fluids: Types and Compatibility, and Why an Oil Works in One Machine and Fails in Another: ISO 6743-4 and DIN 51524 Classes (HL, HLP, HVLP, HLPD), Zinc vs Zinc-Free Anti-Wear and the Pump Tests That Qualify an Oil, Viscosity Windows by Pump Type, VI Improvers and Shear, Engine Oils and Tractor Fluids with Wet-Brake Additives, Fire-Resistant HFA/HFB/HFC/HFDR/HFDU with Pump Derating, Biodegradable HETG/HEES/HEPG, Food Grade, Seal and Paint Compatibility, Foam, Air Release, Demulsibility, Varnish, Mixing and Fluid Conversion"
slug: hydraulic-fluids-types-and-compatibility
category: hydraulics
kind: reference
tags: [hydraulic fluid, hydraulic oil types, ISO 6743-4, HM, HV, HL, HG, DIN 51524, HLP, HVLP, HLPD, AW hydraulic oil, anti-wear additive, ZDDP, zinc free hydraulic oil, ashless hydraulic oil, Denison HF-0, HF-1, HF-2, Eaton 35VQ25, Vickers 35VQ25 pump test, Bosch Rexroth RD 90220, viscosity window, pump viscosity limits, cold start viscosity, viscosity index improver, shear stability, multigrade hydraulic oil, engine oil in hydraulics, 10W hydraulic, Cat HYDO, TO-4, UTTO, tractor hydraulic fluid, Hy-Gard, wet brake chatter, ATF hydraulic, Dexron, fire resistant hydraulic fluid, HFA, HFB, HFC, water glycol, HFDR, phosphate ester, HFDU, polyol ester, pump derating water glycol, biodegradable hydraulic fluid, HETG, HEES, HEPG, PAG hydraulic, food grade hydraulic oil H1, MIL-PRF-5606, brake fluid, seal compatibility, NBR, FKM, Viton, EPDM, polyurethane seals, PTFE, HNBR, paint compatibility, foaming hydraulic oil, air release, demulsibility, detergent hydraulic oil, varnish, servo valve sticking, oil oxidation, mixing hydraulic oils, fluid conversion, hydraulic oil data sheet]
source: "ISO 6743-4 and ISO 11158 (hydraulic fluid classes and specifications); DIN 51524 parts 1-3 (HL, HLP, HVLP) and the HLPD convention; ISO 12922 (fire-resistant fluids) and ISO 15380 (environmentally acceptable fluids); Parker Denison HF-0/HF-1/HF-2 specification, Eaton Vickers 35VQ25 (I-286-S, M-2950-S) and Bosch Rexroth RD 90220/90221 fluid requirements; Eaton Vickers and Parker pump viscosity limits; Caterpillar, John Deere and Case IH fluid specifications (HYDO Advanced, TO-4, Hy-Gard, Hy-Tran); Parker O-ring handbook and Trelleborg seal compatibility data; Noria/Machinery Lubrication guidance on varnish, air release and foam; ASTM D892, D3427, D1401, D2882 test methods."
summary: "The article to read before pouring anything into a reservoir: how hydraulic fluids are classed and what the letters on the drum promise, what the additive package does and which machines it hurts, why the pump maker's viscosity window and approval list matter more than the ISO grade, why a tractor fluid, an engine oil and an industrial AW oil are all called hydraulic oil and are not interchangeable, how fire-resistant and biodegradable fluids change the pump rating, the seals, the paint and the filters, how to read a seal compatibility chart before a fluid change, why one reservoir foams and another does not, what varnish is and why it stops servo valves, what happens when fluids are mixed, and how to convert a system from one fluid to another."
---

## Start with the machine, not the drum

Three things decide whether a fluid works in a machine: **viscosity at the running temperature** (inside the pump maker's window, at start-up as well as at full heat), **the additive chemistry** (matched to the metals, seals and duty of the system) and **the fluid's approvals** (the pump maker's list or a named specification the fluid has passed). A fluid can be excellent and still wrong: the classic failures are a good industrial AW oil in a tractor with wet brakes (brake chatter), a zinc AW oil in a pump with silver-plated parts (corrosion), a high-VI multigrade in a high-shear piston pump (it thins permanently), an engine oil in a servo system (detergents hold water, varnish sticks the valve), a water-glycol at 3,000 psi in a pump rated for it only at 2,000, a mineral oil topped into an ester system (foam, seals), a PAG topped into a mineral system (gel). Every one of these has been called "a bad pump".

![How the fluid families relate and where each belongs](/img/hydraulics/fluid-classes.svg)

*How the fluid families relate and where each belongs*

## Classes and what the letters mean

| Class (ISO 6743-4 / DIN 51524) | What it is | Where it belongs | Where it fails |
|---|---|---|---|
| **HH** | Plain mineral oil, no additives | Nowhere modern | Rust, oxidation, wear |
| **HL** (DIN 51524-1) | Mineral oil with rust and oxidation inhibitors (**R&O**), no anti-wear | Low-pressure systems, some old gear-pump units, systems with silver or where AW is banned; turbine-type duty | Vane and piston pumps above about 1,000-1,500 psi: scuffing |
| **HM** (DIN **HLP**, 51524-2) | HL plus **anti-wear** additives (usually zinc dialkyldithiophosphate, **ZDDP**): the standard **AW hydraulic oil** | Industrial and mobile systems with vane, gear and piston pumps, indoor or steady temperature | Very wide temperature swings (use HV); machines that forbid zinc; wet brakes |
| **HV** (DIN **HVLP**, 51524-3) | HM plus **viscosity index improvers** (VI 140-200) for a flatter viscosity-temperature curve | Mobile equipment outdoors, cold starts, machines that run cold and hot; "multigrade hydraulic" | High-shear piston pumps and servo valves can shear the VI improver permanently: check the **shear stability** (the viscosity after shear, DIN 51350-6 / ASTM D5621 or the 35VQ25 result) or the oil ends up two grades thin |
| **HLPD** (DIN convention) | HLP with **detergent/dispersant** additives that keep water and dirt suspended | Machine tools and presses with water or coolant ingress, mobile machines with cyclic condensation: the water is carried through the filters and out rather than pooling; also cleans varnish | Systems that rely on water **settling** to the tank bottom (large industrial units with a drain routine); systems with fine filters that the suspended sludge blinds; hydrostatic drives that specify HLP |
| **HG** | HM with anti-stick-slip (friction modifier) | Machine tool slideways fed from the hydraulic system | Elsewhere it is unnecessary |
| **HEES, HETG, HEPG, HEPR** (ISO 15380) | Environmentally acceptable: saturated/unsaturated synthetic esters, vegetable oils, PAG, PAO | Forestry, marine, waterways, municipal | See the biodegradable section: heat, water, seals, mixing |
| **HFAE, HFAS, HFB, HFC, HFDR, HFDU** (ISO 12922) | Fire-resistant | Foundries, steel mills, die-casting, mines, near furnaces | See the fire-resistant section: derating, temperature, seals |
| **Zinc-free / ashless HM** | AW from sulphur-phosphorus chemistry without zinc | Pumps with silver or yellow-metal parts, some servo systems, environmentally sensitive, some makers' lists | Fine everywhere else; some are less good with water |

The **ISO VG** number (32, 46, 68) is the viscosity at 40°C only: a fluid is named by its class **and** its grade: "HM 46", "HV 32", "HLPD 68". The grade answers the viscosity question; the class answers the chemistry question. Grade selection tables are in [oil viscosity and selection](/article/oil-viscosity-and-selection).

## Anti-wear chemistry: zinc, zinc-free, and the pump tests

**ZDDP** forms a sacrificial film on steel under boundary contact (vane tips on the cam ring, slippers on the swashplate). It also attacks **silver** (silver-plated bushings and bearing cages in some older piston pumps and certain servo valves), is aggressive to some **bronze** at high temperature and in the presence of water (the zinc compound hydrolyses to acids), and its ash forms deposits. **Zinc-free (ashless) AW** oils use sulphur-phosphorus or other chemistries: same or better wear protection in modern tests, kinder to yellow metals and silver, better filterability with water, and increasingly the default for servo and high-pressure piston systems. Neither is universally better: **the pump maker's specification** decides.

The real qualification of a hydraulic oil is a **pump test**, not the class letters:

| Specification | Test | What it guarantees |
|---|---|---|
| **Eaton Vickers 35VQ25** (M-2950-S mobile, I-286-S industrial) | A 35VQ25 vane pump run at 3,000 psi, 2,400 rpm, 200°F for 50 hours: cam ring and vane weight loss must be below the limits | The oil protects a vane pump at high pressure and temperature; the classic AW oil test |
| **Parker Denison HF-0** | Vane (T6C) and piston (P46) pump tests, dry and **with 1% water**; plus filterability with water; HF-1 (piston only) and HF-2 (vane only) are its subsets | Suitable for both vane and piston pumps, and tolerates water contamination without losing filterability: the most demanding common approval |
| **Bosch Rexroth RD 90220 / 90235** | Fluid rating for Rexroth pumps and motors; includes a piston pump test and requirements for cleanliness, air release, foam, filterability | Approved for Rexroth axial piston units |
| **DIN 51524-2/-3** | FZG gear test (stage 10 or better), vane pump test (DIN 51389 / ASTM D2882: ring and vane wear under 120 mg), demulsibility, air release, foam, oxidation | Minimum quality for HLP/HVLP; most quality oils exceed it |
| **ISO 11158 HM/HV**, ASTM D6158 | Similar minimums | |
| **Cincinnati Machine P-68/P-69/P-70** | Thermal stability with copper and steel rods | Machine tool systems: no sludge or copper attack |

A bargain "hydraulic oil" that lists none of these may be a re-refined HL with a little zinc: fine in a log splitter, a pump killer in a 4,000 psi piston system. If the machine's manual names a specification, buy a fluid that lists it on the data sheet.

## Viscosity: the window that matters

![Viscosity windows: each pump type has a cold-start limit and a running band](/img/hydraulics/viscosity-window-by-pump.svg)

*Viscosity windows: each pump type has a cold-start limit and a running band*

The pump sees the viscosity **at its own inlet temperature**, at start-up and at full heat. Typical limits (the maker's data sheet for the exact pump governs):

| Pump type | Maximum at cold start (cSt) | Optimum running range (cSt) | Minimum at full temperature (cSt) | Below the minimum | Above the maximum |
|---|---|---|---|---|---|
| **Gear** | 1,000-2,000 | 20-100 | 10-12 | Internal leakage, wear of plates and bushings, loss of flow | Cavitation on the inlet, noisy, seal blow-out |
| **Vane** | 850-1,000 | **16-40** (Eaton: 14-54) | **10-13** | Vane tip and ring scuffing, ring rippling, flow loss; vane pumps are the least tolerant of thin oil | Vanes fail to follow the ring (no oil film behind them), cavitation, chatter |
| **Axial piston** | 1,000 (some 1,600 with a warm-up procedure) | **16-36** | **10** (some 8) | Slipper and valve-plate scoring, high case drain | Cavitation, slipper lift-off, **dry start damage** at low temperature; a cold piston pump must be warmed slowly at low pressure |
| Servo and proportional valves | | 15-45 | 10 | Leakage and instability | Slow response, high pressure drop, sticking |
| Hydrostatic transmissions | 1,000-1,600 (Danfoss: 1,600 cold start, max continuous 100) | 12-60 | 7-9 | Charge pressure lost, hot | Cavitation, charge pump starved |

So: the reservoir temperature decides the grade. An indoor press at 120-130°F sump uses **HM 46** (about 28 cSt at 120°F); the same press running 160°F wants **HM 68**; a mobile machine started at 10°F and worked at 180°F wants **HV 46** (or HV 32 in the far north) because a straight HM 46 is 1,500 cSt at 10°F (over the piston pump's limit: cavitation and slipper damage until it warms) and an HM 68 is thicker still; a cold room forklift wants HV 32 or 22. The chart in [oil viscosity and selection](/article/oil-viscosity-and-selection) gives the temperature curves.

**Viscosity index improvers** are long polymer molecules that uncoil as the oil warms and hold the viscosity up. Two costs: **temporary shear thinning** (the oil is thinner in a high-shear gap than its rating) and **permanent shear loss** (the molecules are chopped up by piston pumps and servo valves: a "46" that measures 35 after 500 hours). Quality HV oils use shear-stable polymers and lose under 10-15%; cheap ones lose a third. Where a machine is hot all the time (a stationary press in a heated plant) a straight HM is better than an HV: nothing to shear, higher oxidation life.

## Engine oils, tractor fluids and ATF

| Fluid | What it is | Why it works where it is specified | Why it fails elsewhere |
|---|---|---|---|
| **Engine oil (SAE 10W, 10W-30, 15W-40)** in a hydraulic system | A detergent-dispersant crankcase oil with ZDDP | Specified by some makers (older Cat machines, some trucks, shared engine/hydraulic sumps) because the fleet carries one oil, the detergents suspend soot and water, and the ZDDP level is high; 10W ≈ ISO 32-46 | In industrial systems: detergents **emulsify water** (it will not settle and drain: rust, filter blinding), poor air release (foam), high ash forms varnish on hot servo valves, and the viscosity grade is a rough fit; multigrades shear |
| **Cat HYDO Advanced 10 / 30** | Cat's own hydraulic oil (a 10W or 30 with a defined additive pack) | Cat machines: matched to Cat pumps and a long drain | It is a mobile HV-type oil: fine in most mobile piston systems, not a servo or machine-tool oil |
| **Cat TO-4, Allison C-4** | Transmission and drive train oils (friction-modified for wet clutches and brakes) | Transmissions, final drives and hydraulics on machines that call for TO-4 in the hydraulic tank too | The friction modifiers and high additive levels are wasted or harmful in industrial systems |
| **UTTO / tractor hydraulic fluid** (John Deere Hy-Gard, Case Hy-Tran, New Holland Ambra, Kubota Super UDT, Massey Permatran) | Universal Tractor Transmission Oil: hydraulic oil plus gear oil plus **wet-brake and wet-clutch friction modifiers**, about ISO 46-68 viscosity with a multigrade curve | A tractor's hydraulics, transmission, differential and **oil-immersed brakes** share one sump; the friction modifiers stop the brakes **chattering and squealing** and give the PTO clutch its grip | Put an industrial HM 46 in the tractor: the pump is happy, the **brakes chatter** within days and the clutch packs glaze. Put UTTO in an industrial press: it works, but it is the wrong viscosity curve, the friction modifiers and EP additives are wasted, its demulsibility is poor and the maker's warranty is void |
| **"303" tractor fluid** | An obsolete 1960s John Deere spec still sold generically | Nothing modern; often low quality | Brake and pump wear in tractors that call for a current UTTO |
| **ATF (Dexron, Mercon)** | Automatic transmission fluid: low viscosity (ISO 32-ish), friction-modified, red dye, good cold flow | Power steering, some small power units, some snow-plough and tailgate pumps, machine tool circuits that specify it | In a 3,000 psi industrial system its viscosity is on the thin edge at temperature and its AW package is not tested for pumps |
| **MIL-PRF-5606 (red), 83282, 87257** | Aviation mineral and synthetic hydrocarbon fluids, very low viscosity (ISO 15) | Aircraft, ground support equipment and some test rigs at −65°F | Too thin for an industrial pump at temperature |
| **Brake fluid (DOT 3/4, glycol ether)** | Not a hydraulic oil at all | Automotive brakes with EPDM seals | Destroys nitrile seals, absorbs water, no lubricity: never in a hydraulic system |

## Fire-resistant fluids

Used where a spray from a burst hose would meet a furnace, molten metal, hot slag or a hot die. Each type changes the machine.

| Type | Composition | Max temperature | Pump derating (typical) | Seals | Paint | Notes |
|---|---|---|---|---|---|---|
| **HFAE / HFAS** | 95% water, 5% oil emulsion or synthetic concentrate | 120°F (50°C) | Special pumps only (water-hydraulics); 500-1,000 psi | NBR ok | | Mines, roof supports; bacteria, corrosion, freezing |
| **HFB** | Water-in-oil (invert) emulsion, 40% water | 120°F (50°C) | 30-50%, speed reduced | NBR | | Mining; water content must be checked (it evaporates) |
| **HFC** | **Water-glycol**: 35-50% water, glycol, thickener, additives | **120-140°F (50-60°C)**; above that the water boils off and the fluid thickens | Pressure to about **2,000-2,500 psi** and speed to 1,200-1,800 rpm on most pumps (about 30-50% derating), roller bearings' life cut by 50-80% (some makers require special pumps); higher specific gravity (1.08): inlet conditions tighter (max 3-5 in Hg vacuum) | NBR and FKM ok; **not polyurethane** (hydrolyses) and check leather | Most epoxy and two-pack paints ok; alkyd and ordinary enamels lift and clog filters; zinc and cadmium plating attacked (no galvanised fittings, no zinc-plated filter bowls, no zinc AW additive mixing) | Steel mills, die casting, foundries; monitor **water content** (refractometer) and top up with distilled water, monitor pH and reserve alkalinity; filters rated for it; no mineral oil above 0.5% |
| **HFDR** | **Phosphate ester** (synthetic) | 250°F (120°C) | None or little for pressure; some speed limits | **FKM (Viton), EPDM, PTFE, butyl only: destroys NBR and polyurethane in days** | Attacks most paints: epoxy-phenolic or unpainted inside | Steam turbine controls, some presses and aluminium die-casting; hydrolyses with water to acids (needs ion-exchange or Fuller's earth treatment), skin and eye irritant, denser than water (1.13) |
| **HFDU** | **Polyol ester** (or PAG) synthetic, water-free | 220-250°F (105-120°C) | Little (specific gravity 0.92, close to oil) | NBR usually ok (check), FKM ok, some polyurethane not | Most paints ok | The modern replacement for HFC in many plants: near-mineral-oil pump life, biodegradable versions; costs 5-10× mineral oil |

Converting a machine from mineral oil to HFC or HFDR is a **rebuild**: drain, flush, change seals (HFDR), change paint or strip the tank, change filters, check plating, derate the pump settings, retrain the operators for the water checks. A machine converted "by draining and filling" fails in the first month.

## Biodegradable and food-grade fluids

| Type | Base | Character | Compatibility |
|---|---|---|---|
| **HETG** | Vegetable (rapeseed, canola, soy) triglyceride | Cheap, very biodegradable, high VI, but poor oxidation stability (max 160°F), thickens and goes rancid, poor with water, low-temperature gelling | NBR ok, mixes with mineral oil (but then it is no longer biodegradable); short drain intervals |
| **HEES** (unsaturated) | Synthetic ester | Better oxidation, wider temperature | Some swelling of NBR; check |
| **HEES** (saturated) | Fully saturated synthetic ester | The good one: long life, 200°F+, high VI, excellent lubricity | NBR ok, FKM ok; some paint softening; mixes with mineral oil in small amounts; Panolin, Mobil EAL, Shell Naturelle class |
| **HEPG** | **Polyalkylene glycol** | High VI, clean, water-soluble grades exist | **Not miscible with mineral oil or esters**: forms sludge and gel; attacks some paints and polyurethane; a full flush and seal review for conversion |
| **HEPR** | PAO and related hydrocarbons | Mineral-like | Mixes with mineral oil; less biodegradable |
| **Food grade H1 hydraulic** (NSF H1) | White mineral oil or PAO with H1-approved additives | Incidental food contact allowed; weaker AW packages than industrial oils (check pump approvals: some are HF-0 approved) | Keep the whole system H1 including the grease on the hoses; label; never top up with an H2 or industrial oil |

Forestry and marine machines run HEES saturated esters with **the ester-rated filters and hoses** (ester swells some hose inner tubes and lifts some reservoir paints); the water limit is tighter (esters hydrolyse) and the drain interval set by oil analysis (acid number).

## Seals and paint

![Seal materials against fluid families: check before a fluid change](/img/hydraulics/fluid-seal-compatibility.svg)

*Seal materials against fluid families: check before a fluid change*

| Seal material | Mineral HM/HV | HFC water-glycol | HFDR phosphate ester | HFDU polyol ester | HEES ester | HEPG (PAG) | Brake fluid (glycol) | Temperature range |
|---|---|---|---|---|---|---|---|---|
| **NBR (Buna-N, nitrile)** | Yes | Yes | **No** (swells and softens in hours) | Usually (check) | Yes (check swell) | Check | No | −30 to 230°F (−35 to 110°C) |
| **HNBR** | Yes | Yes | No | Yes | Yes | Check | No | −20 to 300°F |
| **FKM (Viton, fluorocarbon)** | Yes | Yes (check grade) | **Yes** | Yes | Yes | Yes | No | 0 to 400°F (−20 to 200°C); poor at very low temperature |
| **EPDM** | **No** (swells and dissolves in mineral oil) | Yes | **Yes** | No | No | Yes | **Yes** | −60 to 300°F |
| **Polyurethane (AU/EU)** (rod and piston seals, wipers) | Yes, the standard | **No** (hydrolysis) | No | Check | Check | No | No | −30 to 200°F; hydrolyses with hot water in any fluid |
| **PTFE (with an energiser)** | Yes | Yes | Yes | Yes | Yes | Yes | Yes | −300 to 500°F; no elastic memory: needs a back-up O-ring |
| Leather, fabric-reinforced NBR | Yes | Check | No | | | | | Old cylinders |
| Silicone | Static only | | | | | | | Not a hydraulic seal (poor tear strength) |

Why a seal fails after a fluid change: the new fluid swells the compound (softens, extrudes, drags: EPDM in mineral oil grows 30-50% and turns to jelly), shrinks it (leaks), or leaches its plasticiser (hardens and cracks: NBR in phosphate ester). A **fluid conversion needs a seal list** for every cylinder, valve, pump shaft seal, accumulator bladder (NBR standard; FKM or EPDM for HFD and HFC respectively; check), hose inner tube (NBR standard; some hoses have polyurethane or thermoplastic tubes) and filter bowl seal. Ask the fluid supplier for the compatibility sheet for **their** fluid; charts differ by formulation.

**Paint**: the inside of a reservoir painted with an alkyd enamel and filled with water-glycol or phosphate ester sheds flakes into the strainer within weeks. Epoxy and epoxy-phenolic linings resist most fluids; the safest tank for HFD is unpainted, pickled steel or stainless. Zinc-rich primers, galvanising and cadmium plating react with water-glycols to form soaps that blind filters: remove or avoid them.

## Foam, air release, water and varnish: the fluid in the reservoir

- **Foam** (bubbles on the surface) and **entrained air** (bubbles inside the oil) are different problems. Foam collapses with an **anti-foam** additive (silicone); too much anti-foam **slows air release** (the small bubbles stay in the oil). An oil can pass the foam test (ASTM D892) and fail air release (ASTM D3427: good hydraulic oils release air in under 5-10 minutes at 50°C). The same oil foams in one reservoir and not another because the reservoir is different: a small tank with a short dwell time, a return line above the surface, a suction close to the return, a pump inlet leak, a badly placed baffle. Fix the tank before changing the oil.
- **Silicone contamination** (from a silicone sealant on a fitting or a hatch, a silicone grease, a silicone-based defoamer overdose) ruins an oil's air release across the whole system: foam that no new oil cures until the silicone is flushed out.
- **Demulsibility** (ASTM D1401): an industrial HM oil should separate from water in under 30 minutes at 54°C, so water sinks to the tank bottom and is drained; an HLPD or an engine oil holds it as an emulsion (milky) on purpose. Choose which behaviour the machine needs: a large tank with a bottom drain wants demulsibility; a machine tool with coolant splashing in and no drain routine wants HLPD. Water limits: **under 200-500 ppm** for servo and piston systems; visible cloud at about 0.1%.
- **Oxidation**: the oil's life halves for every 18°F (10°C) above about 140°F (60°C). Products: acids (rising acid number), sludge and **varnish** (a hard, thin, brown-to-black lacquer of oxidation products that come out of solution on cooler surfaces and in tight clearances). Varnish sticks **servo and proportional valve spools** (a machine that misbehaves first thing in the morning and cures itself when warm), blinds coolers, coats the tank walls and darkens sight glasses. Group II and III base oils (most modern oils) hold varnish precursors less well than old Group I oils, so hot systems now varnish sooner: keep the oil under 140°F, avoid micro-dieseling (air being compressed at the pump), fix electrostatic discharge (a crackling sound in fine filters on dry oil), test with **MPC (membrane patch colorimetry)** and RULER (remaining antioxidant), and clean with an electrostatic or resin varnish-removal loop before it becomes a valve problem.
- **Additive depletion**: the AW, antioxidant and anti-foam packages are consumed; a 10-year-old oil that "looks fine" has none of them left. Oil analysis (see [oil analysis and sampling](/article/oil-analysis-and-sampling)) tracks the additive metals (zinc, phosphorus, calcium), the acid number, viscosity and water.

## Mixing rules

| Mixing | Result |
|---|---|
| Two mineral HM oils of different brands, same grade | Usually acceptable in an emergency; different additive packages can react (foam, haze, sludge); do not make a habit of it; log it |
| HM 32 topped with HM 68 | A viscosity between: the pump gets an oil off its curve; drain and refill |
| HM and HV | Acceptable: the VI improver is diluted, the cold performance lost |
| Zinc AW into a zinc-free system | The silver or yellow-metal protection is lost; some servo makers void the warranty |
| Mineral into HFC water-glycol | Gel and sludge; the AW zinc reacts with the water; filters blind; keep under 0.5% |
| Mineral into HFDR phosphate ester | Foam, seal confusion, the fire resistance drops fast: keep under 1-2% |
| Mineral into HFDU polyol ester or HEES | Tolerated in small amounts (a few percent) but the fluid loses its rating and its biodegradability |
| Mineral, ester or PAO into HEPG (PAG) or PAG into any of them | **Not miscible**: gel, sludge, blocked filters, pump failure; full flush |
| Detergent oil into a demulsifying system | The water it was settling out becomes an emulsion |
| Anything into a food-grade H1 system | The whole charge is no longer H1 |

## Converting a system to a different fluid

![Used hydraulic fluid going to the waste drum: a conversion drains everything, and the old and new fluids never share a container](/photos/hydraulics/hydraulic-oil-drums.jpg)

*Used hydraulic fluid going to the waste drum: a conversion drains everything, and the old and new fluids never share a container. Photo: MCSN James E. Veal, Public domain, via commons*

1. Confirm with the pump, valve, cylinder, hose, filter and accumulator makers that every component is rated for the new fluid, and what derating and seal changes apply; get the fluid supplier's conversion procedure and compatibility sheet.
2. Drain completely at operating temperature: reservoir, cylinders (full stroke, both ends), accumulators (discharged), coolers, filter housings, low points in the pipework; blow out lines that can be opened.
3. Clean the reservoir by hand; strip incompatible paint; replace the breather and every filter element (with elements rated for the new fluid), the suction strainer, and the seals the makers list.
4. Fill with a **flushing charge** of the new fluid (or the supplier's flushing fluid) to the minimum level, run at low pressure with all actuators cycling and the filter cart on for 4-8 hours warm, drain again completely; change the elements.
5. Fill with the new fluid through a filter cart; run; sample after 24 hours and a week; test for the old fluid's residue (the supplier's test) and for water; re-set the relief and the compensator to the derated values if the new fluid requires it.
6. Relabel the reservoir, the fill point and the drum store; brief everyone who tops up.

## Reading a data sheet

Check, in order: the **specifications and approvals** (35VQ25, HF-0, RD 90220, DIN 51524 part 2 or 3, the OEM's own number); the **viscosity at 40°C and 100°C** and the **VI** (draw the line on the temperature chart against the pump window); the **pour point** (at least 15-20°F below the coldest start); the **flash point** (safety); the **air release** (under 10 minutes), **foam** (low) and **demulsibility** (per the system's need); the **shear stability** for HV; the **zinc content** (ppm; zero for zinc-free); the **seal compatibility statement**; and the **FZG** load stage for gear pumps and hydrostatic drives. A sheet that lists only "meets or exceeds industry standards" tells you nothing.

## Common mistakes

- Industrial HM 46 in a tractor with wet brakes: the brakes chatter in a week.
- Tractor UTTO in a press because "it is hydraulic oil".
- An HV multigrade in a hot stationary piston system: it shears to a 32 and the pump runs hot.
- A straight HM 68 in a mobile machine started at 10°F: cavitation and slippers every winter.
- Engine oil in a servo system: varnish and a sticking valve.
- Water-glycol at mineral-oil pressure and speed: pump bearings gone in months.
- Phosphate ester with nitrile seals: everything leaks within days.
- PAG topped up with mineral oil, or the reverse: gel in the filters.
- Silicone sealant on a tank hatch: permanent foam.
- Judging a fluid by its colour or its price instead of its approvals.
- Converting fluid by draining and filling, with the old paint, old seals and old elements.

## Related

- [Oil viscosity and selection](/article/oil-viscosity-and-selection)
- [Filters, fluid and contamination](/article/filters-fluid-and-contamination)
- [Oil analysis and sampling](/article/oil-analysis-and-sampling)
- [Hydraulic pumps: types, controls and testing](/article/hydraulic-pumps-types-controls-and-testing)
- [Cylinder repair and seal kits](/article/cylinder-repair-and-seal-kits)
- [Seal failure](/article/seal-failure)
- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Grease types and compatibility](/article/grease-types-and-compatibility)
