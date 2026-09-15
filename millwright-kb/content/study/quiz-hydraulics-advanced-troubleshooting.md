---
title: "Test Yourself: Advanced Hydraulics (20 Questions with Answers on Pump Testing, Spool Centres, Stack and Sectional Valves, Cartridge and Logic Valves, Counterbalance Ratios, Fitting Identification, Fluid Types, Load Sensing, Servo Valves, Hydrostatic Drives and Diagnostics)"
slug: quiz-hydraulics-advanced-troubleshooting
category: study
kind: reference
tags: [quiz, practice questions, hydraulics quiz, advanced hydraulics questions, hydraulic troubleshooting quiz, load sensing questions, counterbalance valve questions, logic valve questions, fitting identification quiz, hydraulic fluid questions, hydrostatic transmission questions, servo valve questions, Red Seal practice, IFPS practice, apprenticeship exam, self test, study questions]
source: "Questions written against the advanced hydraulics articles in this knowledge base (Eaton Vickers, Parker, Bosch Rexroth, Danfoss and Sun Hydraulics training and service data; ISO 7368, SAE J514/J518/J1453, DIN 2353; Denison HF-0 and Eaton 35VQ25 fluid specifications)."
summary: "Twenty practice questions for the technician level: pump flow and case-drain tests, what each spool centre does, stack order and sectional valve faults, cartridge cavities and logic element area ratios, counterbalance pilot ratios and settings, identifying fittings by measurement, choosing and converting fluids, load-sense margin, servo valve filtration, hydrostatic charge pressure, and the diagnostic method. Tap each answer after you decide."
---

How to use this: read the question, decide on your answer, then tap **Answer**. Score yourself out of 20.

![Review figure: from the symptom to the test to the cause](/img/hydraulics/troubleshooting-decision-tree.svg)

*Review figure: from the symptom to the test to the cause*

## Questions

**1.** A 2.75 in³/rev piston pump at 1,800 rpm delivers 15 gpm at 3,000 psi on the flow meter. What is its volumetric efficiency, and what do you conclude?

<details><summary>Answer</summary>Theoretical flow = 2.75 × 1,800 ÷ 231 = 21.4 gpm; 15 ÷ 21.4 = 0.70. Below about 0.80-0.85 at working pressure the pump is worn: replace or rebuild, and flush the system before the new pump goes in. Review: hydraulic pumps, types, controls and testing.</details>

**2.** Why can a badly worn pump still show full system pressure on the gauge?

<details><summary>Answer</summary>Pressure comes from resistance to flow, not from the pump. Against a dead-headed cylinder even a trickle of flow holds the relief or compensator pressure on the gauge; the wear shows only as lost flow at pressure, so the machine is slow. Judge a pump by flow at pressure or by case drain flow, never by the gauge alone. Review: hydraulic pumps, types, controls and testing.</details>

**3.** What is the case-drain rule of thumb for a piston pump, and what precaution protects the shaft seal during the test?

<details><summary>Answer</summary>New pumps leak 1-3% of rated flow to the case; over about 10-15% at working pressure and temperature means worn. Keep the drain outlet above the pump's top port so the case stays full, and never restrict the drain: the case and shaft seal are rated for only about 15-30 psi. Review: hydraulic pumps, types, controls and testing.</details>

**4.** A machine has a fixed-displacement pump and a directional valve with a closed centre. What happens at rest, and which centre would unload the pump while still blocking the cylinder ports?

<details><summary>Answer</summary>With all ports blocked the pump flow goes over the relief valve at full pressure and turns to heat. A tandem centre (P to T, A and B blocked) unloads the pump to tank and still holds the cylinder against slow spool leakage. Review: directional control valves, spools and solenoids.</details>

**5.** An AC-solenoid valve keeps burning coils every few weeks. What is the most likely cause?

<details><summary>Answer</summary>The spool is not completing its stroke (contamination, silting, a bent stack, low pilot pressure on a two-stage valve), so the AC inrush current never falls to the holding value and the coil overheats. Find out why the spool sticks before fitting another coil; a DC coil would just run warm and half-shift. Review: directional control valves, spools and solenoids.</details>

**6.** A D03 stack has a meter-out flow control sandwiched under a pilot-operated check. The load lowers in jerks. Why, and what is the fix?

<details><summary>Answer</summary>The flow control throttles the pilot pressure that opens the pilot-operated check, so the check opens and closes as the pressure builds and drops. Put the pilot-operated check (or counterbalance) closest to the manifold and the flow control above it, under the directional valve. Review: stack valves and sectional valve banks.</details>

**7.** On a mobile sectional valve one function is weak when lifting but normal when lowering; the main relief tests correctly. Where do you look?

<details><summary>Answer</summary>That section's port relief on the lifting side (set or leaking below the main relief), or its load check. A port relief set below the main relief makes one function weak in one direction only. Gauge on the work port while the function stalls. Review: stack valves and sectional valve banks.</details>

**8.** What decides whether an ISO 7368 logic element is open or closed, and what does a 1:1 area ratio mean?

<details><summary>Answer</summary>The force balance: it opens when pressure at A times the nose area plus pressure at B times the annulus exceeds pressure at X (the spring chamber) times the full top area plus the spring. A 1:1 ratio has no B annulus, so port B pressure has no effect: a pure pressure or relief element. Review: cartridge and logic valves.</details>

**9.** A screw-in cartridge leaks between two ports right after installation. Name three likely causes.

<details><summary>Answer</summary>The cartridge was cocked on entry and an O-ring was cut on a cavity step; a back-up ring was fitted on the wrong side or a seal was left out; a scored step in the cavity; or a seal left in the cavity from the old cartridge stopping the new one from seating. Review: cartridge and logic valves.</details>

**10.** A boom cylinder holds a load at 1,200 psi load-induced pressure. What setting do you give the counterbalance valve, and which pilot ratio would you avoid on a long springy boom?

<details><summary>Answer</summary>About 1.3 × 1,200 = 1,560 psi, set with a gauge on the load line. Avoid the 10:1 ratio on a springy structure: it opens with little pilot pressure and hunts; 3:1 is the stable choice, 4.5:1 the usual compromise. Review: pressure and flow control valves in depth.</details>

**11.** A pilot-operated relief valve's pilot orifice becomes blocked. Is the system over-protected or unprotected, and why?

<details><summary>Answer</summary>Unprotected. The main poppet is held shut by equal pressure on both sides and only lifts when the pilot flow through the orifice lowers the pressure above it; with the orifice blocked the pilot stage cannot sense, the main poppet never opens, and the pressure can rise until something bursts. Review: pressure and flow control valves in depth.</details>

**12.** You measure a male fitting: 0.750 in major diameter, 16 threads per inch, parallel, with a 37° cone. A second fitting has the same thread with a flat shoulder and an O-ring. Name both.

<details><summary>Answer</summary>The first is a −8 JIC 37° flare (3/4-16 UNF). The second is a −8 SAE O-ring boss port fitting on the same 3/4-16 thread. A JIC will screw into an ORB port and leak because it has no O-ring and the cone lands on the chamfer. Review: hydraulic fitting identification and thread tables.</details>

**13.** A 1/2 in NPT fitting is started in a G 1/2 BSPP port. Both are 14 threads per inch. What happens and how do you tell them apart?

<details><summary>Answer</summary>The 60° tapered NPT form cross-cuts the 55° parallel BSPP port; it may seem to tighten but leaks and the port is ruined. Tell them apart by the taper (NPT tapers, G is parallel), the diameter (0.840 vs 0.825 in) and the G port's chamfer or spot face for a washer or O-ring. Review: hydraulic fitting identification and thread tables.</details>

**14.** A tractor's oil-immersed brakes start chattering a week after the hydraulic and transmission sump was topped up with an industrial ISO 46 anti-wear oil. Explain.

<details><summary>Answer</summary>Tractor fluid (UTTO) carries friction modifiers for wet brakes and clutches that industrial AW oil lacks; diluting it changes the friction characteristic so the brakes grab and chatter. Drain and refill with the maker's UTTO. The pump was never the problem. Review: hydraulic fluids, types and compatibility.</details>

**15.** A plant converts a press from mineral oil to a phosphate ester fire-resistant fluid by draining and refilling. What fails first?

<details><summary>Answer</summary>The nitrile and polyurethane seals: phosphate ester (HFDR) swells and softens NBR in days; the machine needs FKM, EPDM or PTFE seals throughout, compatible paint in the reservoir, new filters and a full flush. Review: hydraulic fluids, types and compatibility.</details>

**16.** On a load-sensing machine the pump outlet sits at 250 psi and nothing moves when a lever is pulled. Where is the fault most likely?

<details><summary>Answer</summary>The load-sense signal is not reaching the pump: a broken or leaking LS line, a missing or stuck shuttle in a valve section, or the LS relief stuck open. The pump is idling at its margin pressure because it has been told there is no load. Gauge the LS line while the function is commanded. Review: load-sensing, proportional and servo systems.</details>

**17.** Why does a servo valve need a 3 µm non-bypass pressure filter directly upstream, and what is the typical failure when it does not have one?

<details><summary>Answer</summary>The flapper-nozzle clearances are 25-50 µm and the fixed orifices 100-200 µm; a particle in an orifice or on a nozzle unbalances the pilot stage and the spool goes hard over, driving the actuator to one end at full force. Contamination lock also shows as rising hysteresis and a wandering null. Review: load-sensing, proportional and servo systems.</details>

**18.** What is the first measurement in any hydrostatic transmission fault, what should it read, and what does a value that collapses under load tell you?

<details><summary>Answer</summary>Charge pressure at the charge gauge port: typically 200-350 psi in neutral (the manual's figure), dropping no more than 10-15% at full stroke under load. Good in neutral but collapsing under load means the loop is leaking faster than the charge pump can make up: a worn pump or motor (measure the case drains), a leaking multi-function valve or flushing valve. Review: hydraulic motors and hydrostatic drives.</details>

**19.** A hydraulic motor's shaft seal blows out repeatedly. What is the usual cause?

<details><summary>Answer</summary>Case pressure above the seal's rating (often only 15-150 psi): the case drain is restricted, kinked, undersized, or teed into the return line where filter and cooler back-pressure sits on it. Run the drain straight to tank, unrestricted. Review: hydraulic motors and hydrostatic drives.</details>

**20.** A press ram is slow only after an hour of running; the tank reaches 165°F. Describe the test sequence that separates a worn pump from a bypassing cylinder from a dumping relief.

<details><summary>Answer</summary>Heat-map the components (the hottest one is passing oil across a pressure drop); flow-test the pump at working pressure when hot (a steep fall means the pump); run the cylinder bypass test hot (rod-end line off, cap end pressurised, measure the leakage); check the relief's cracking against its full-flow setting and its temperature. Fix the cause before touching the cooler. Review: advanced hydraulic troubleshooting and diagnostics.</details>

## Scoring

- 18 to 20: ready for the technician-level hydraulics section.
- 14 to 17: review the articles named in the answers you missed.
- Under 14: work through the hydraulics category from the basics article to the diagnostics article.

## Related

- [Advanced hydraulic troubleshooting and diagnostics](/article/hydraulic-troubleshooting-advanced-diagnostics)
- [Hydraulic pumps: types, controls and testing](/article/hydraulic-pumps-types-controls-and-testing)
- [Directional control valves, spools and solenoids](/article/directional-control-valves-spools-and-solenoids)
- [Cartridge and logic valves](/article/cartridge-and-logic-valves)
- [Hydraulic fitting identification and thread tables](/article/hydraulic-fitting-identification-and-thread-tables)
- [Hydraulic fluids: types and compatibility](/article/hydraulic-fluids-types-and-compatibility)
- [Test yourself: hydraulics, pneumatics and lubrication](/article/quiz-hydraulics-and-lubrication)
- [Millwright glossary A to Z](/article/millwright-glossary)
- [Test yourself: drawings, schematics and P&amp;IDs](/article/quiz-drawings-schematics-and-pids)
