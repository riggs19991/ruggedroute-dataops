# Diagram audit (September 2026)

Every SVG was reviewed against one question: would a millwright recognise this as the real thing?
Verdicts: KEEP (correct and legible), REDRAW (geometry or recognisability wrong; redrawn in
`zz_redraw.mjs`, which runs last and overrides the original), PHOTO (a real photograph teaches
it better; a free-licensed photo is added next to the schematic where one exists).

## Redrawn
alignment: offset-and-angularity, reverse-dial-setup, rim-and-face-setup, soft-foot-types, dial-indicator-runout (measurement)
bearings: adapter-sleeve-drive-up, puller-types, tapered-roller-end-play
conveyors: idler-set-and-pulley, screw-and-bucket-elevator
cutting-gouging: oxy-cut-technique, plasma-torch-consumables
gearboxes: shim-pack-preload, torque-arm-reducer
hydraulics: cylinder-seal-orientation
installation: pipe-strain-check
layout-templates: centre-finding, miter-elbow-layout
machining: tram-and-keyway
measurement: vernier-scale-reading
oxy-fuel: flame-types, propane-vs-acetylene, oaw-braze-technique, cylinder-storage
power-transmission: chain-sag-and-wear, key-and-keyway, timing-belt-tension
rigging: shackle-loading, sling-angles-and-hitches
safety: confined-space-setup, fall-clearance-and-ladder, hot-work-zone
shop-reference: hardness-scale-bar
welding: ac-balance, brazing-joint, cast-iron-repair, joint-types, mig-gun-parts, mig-stickout, orthographic-views, smaw-angles, tig-torch-setup

## Text collisions fixed in place
alignment/laser-alignment-positions, thermal-growth; condition-monitoring/bearing-defect-frequencies, single-plane-balancing-vectors, thermography-and-ultrasound; conveyors/belt-end-squaring; cutting-gouging/plasma-cut-chart; fasteners/thread-identification; gearboxes/oil-level-and-breather; hydraulics/iso-4406-codes; installation/anchor-types, leveling-with-jack-bolts; layout-templates/cone-development; lubrication/viscosity-vs-temperature; machining/bench-grinder-gaps, drill-rpm-chart; maintenance/mtbf-timeline; manuals/add-a-manual-flow, belt-selection-steps, pump-curve-sheet-anatomy; measurement/feeler-gauge-technique, height-gauge-and-sine-bar; motors-electrical/nine-lead-wye; power-transmission/v-belt-deflection; shop-reference/pipe-schedule-walls, task-workflow, torque-speed-power; welding/duty-cycle, fcaw-drag-stickout, ground-clamp-placement

## Photo added beside the schematic
bearings/induction-heater-mounting; condition-monitoring/thermography-and-ultrasound; fasteners/locking-methods; hydraulics/fitting-types; machining/broken-bolt-nut-weld, lathe-parts; motors-electrical/vfd-bearing-currents; oxy-fuel/flame-types, propane-vs-acetylene; power-transmission/coupling-gap-and-types, qd-vs-taperlock; pumps-seals/compressor-types, impeller-clearance, mechanical-seal-parts; rigging/hoist-inspection-points; safety/grinder-guard-and-kickback; shop-reference/spark-test-patterns; troubleshooting/coupling-wear-signs, seal-face-patterns, v-belt-wear-patterns; welding/flowmeter-reading, weld-defects

## Advanced hydraulics batch (hydraulics2.mjs, September 2026)
All 28 rendered through headless Chromium and checked at 2× on a 500 px canvas; every overflow
warning cleared; captions kept under 70 characters. Verdict KEEP for: pump-controls,
case-drain-flow-test, pump-flow-vs-pressure, spool-center-conditions, dcv-mounting-patterns,
solenoid-checks, pilot-operated-dcv, stack-valve-order, sectional-valve-bank,
logic-valve-cross-section, cartridge-valve-cavity, pilot-operated-relief, counterbalance-pilot-ratio,
flow-control-placement, fitting-identification-steps, thread-od-lookup, code-61-62-flange,
din-bite-ring-assembly, viscosity-window-by-pump (ASTM D341 fit through VG 32/46/68),
fluid-seal-compatibility, fluid-classes, troubleshooting-decision-tree, cylinder-bypass-test,
heat-balance, load-sense-margin, proportional-valve-loop, servo-valve-stages, hydrostatic-drive-loop.
PHOTO added beside: pump types (bent-axis cutaway, vane rotor), solenoid valves, valve stack and
sectional bank, cartridge manifold and pressure cartridges, JIC fitting, test gauge, IR thermometer,
servo valve disassembled, orbital motor, hydrostatic drive unit, fluid handling.
