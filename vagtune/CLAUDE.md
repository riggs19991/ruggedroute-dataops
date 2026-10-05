# CLAUDE.md — vagtune project context

Read this before touching anything. It is the ground truth for architecture,
conventions, verified protocol facts, and the roadmap.

## What this is

`vagtune` is a laptop-side toolkit for Volkswagen Group ECUs over OBD2: diagnostics
(identify, DTCs), security unlock (SA2 seed/key), calibration read, and map editing.
Owner: Jeff / Addictive Media Productions, LLC. Scope: **off-road / track-only
vehicles** (trailered, not street-driven). Nothing here may add emissions-defeat
features (cat/EGR/DPF/O2-monitor deletes, readiness spoofing). See README "Scope".

## Layer map (keep it layered — no upward imports)

```
vagtune/
  transport/   base.py      CanFrame, RawCanTransport, IsoTpLink (ABCs + errors)
               isotp.py     software ISO 15765-2 (SF/FF/CF/FC, BS, STmin, padding,
                            extra_rx_ids + last_rx_id for functional/multi-responder use;
                            one reassembly per responder, FC sent to physical_request_id())
               router.py    CanRouter (one reader thread per bus, fan-out) + RouterEndpoint
                            (a RawCanTransport view: own bounded queue, id-set/predicate/monitor)
               context.py   TransportContext(kind) -> isotp_link()/tp20_channel()/raw_endpoint();
                            kinds fake | can | j2534 (raw CAN + router) | j2534-fw (device ISO-TP)
               j2534.py     ctypes binding; J2534Device (one handle) -> J2534Channel (CAN and
                            ISO15765 on the same device); J2534RawCanTransport; J2534IsoTpChannel
                            (ONE shared ISO15765 channel, routes by response id) + J2534IsoTpLink
               socketcan.py python-can RawCanTransport (optional dep)
               fakebus.py   FakeCanBus/FakeCanTransport, UdsNode (SimulatedEcu behind ECU-side
                            ISO-TP), SimulatedVehicle presets + register_preset_hook,
                            get_default_vehicle()  <- what --transport fake talks to
               fake.py      SimulatedEcu (the UDS brain) + FakeIsoTpLink/make_fake_pair (unit tests)
  uds/         client.py    UdsClient: request(), services, 0x78 pending, keepalive
               services.py  SIDs/subfunctions/enums    exceptions.py  NRC decode
  vag/         modules.py   CAN IDs + ident DIDs       dtc.py        DTC decode/db
               sa2.py       SA2 seed/key VM            profiles.py   ECU families
               ecu.py       VagEcuSession (identify/dtc/unlock/read block)
  calibration/ image.py     FlashImage (bounds, diff, checksum regions)
               maps.py      Scaling/ScalarValue/Axis/Map  definition.py JSON defs
  commands/    _common.py   add_common_args (--transport/--dll/--can-*/--vehicle/--module),
                            open_context(args), resolve_module(token: name or address word)
               diag.py      scan, identify, dtc        calibration.py read-cal, show-map, scale-map, sa2
               __init__.py  REGISTRARS: each area exposes register(sub, add_common_args)
  cli.py       build_parser()/main() only; iterates commands.REGISTRARS. GUI calls the library.
definitions/   JSON map definitions (simos18.1.example.json is DEMO addresses only)
docs/          DESIGN_0.2.md (binding 0.2.0 structure spec)
tests/         pytest; 133 tests (132 run + 1 skipped without python-can); all protocol logic must stay covered
```

Dependency direction: `commands` -> everything; `calibration` and `vag` depend on `uds`
depends on `transport`. Inside `transport`: `context` -> `router`/`isotp`/`fakebus`/hardware;
`fakebus` -> `fake` -> `vag.sa2` (so the sim answers seed/key with real math) — that is the
one allowed cross-reference. `context.tp20_channel()` imports `transport.tp20` lazily and
raises `TransportError` while that module is absent. Other slices add simulated modules via
`SimulatedVehicle.register_preset_hook(preset, hook)`, never by editing `fakebus.py`.

## Commands

```
pip install -e ".[dev]"          # python-can path: pip install -e ".[dev,can]"
python -m pytest -q              # must be green before any commit
vagtune --help
vagtune identify                 # default --transport fake (simulated vehicle, real ISO-TP framing)
vagtune identify --module 19     # --module takes names (engine, gateway, ...) or address words (01, 19)
vagtune identify --transport j2534 --dll "C:\...\op20pt32.dll"      # raw CAN via pass-thru (universal)
vagtune read-cal --transport j2534-fw --profile simos18.1 --out stock.bin   # device-side ISO-TP, fast
vagtune scan [--vehicle demo]    # --vehicle picks the fake preset: demo | golf-tdi-2012 | r32-2008
vagtune dtc [--clear] [--module abs]
vagtune read-cal --profile simos18.1 --out stock.bin
vagtune show-map --def definitions/simos18.1.example.json --bin stock.bin --map boost_target
vagtune scale-map --def ... --bin stock.bin --map boost_target --multiplier 1.05 --clamp 300 --out tune.bin
vagtune sa2 --script <hex> --seed <hex>
```

Library entry point for anything that needs several links on one cable:
`with TransportContext("j2534") as ctx: link = ctx.isotp_link(0x7E0, 0x7E8)`.
`make_isotp_link(kind, tx, rx)` stays for the one-link case and releases the hardware on close.
A functional OBD link on any kind: `ctx.isotp_link(0x7DF, 0x7E8, extra_rx_ids=range(0x7E9, 0x7F0))`
(single-frame requests only; `link.last_rx_id` names the responder of each payload).

## Conventions

- Python >= 3.10, type hints everywhere, `from __future__ import annotations`.
- No placeholder/stub code. If a feature can't be finished, raise a clear error
  (`NotImplementedError` with the reason) — never silently fake success.
- Every protocol change gets a test against `SimulatedEcu` or the ISO-TP loopback.
  Hardware classes (`j2534.py`, `socketcan.py`) must still *import* on Linux/macOS.
- Logging via `logging.getLogger(__name__)`; never `print()` outside `commands/`.
- Big-endian is the default for VAG Tricore calibration data (`Scaling.endian`).
- `FlashImage` keeps `_original`; any write path must be able to `diff()` and `reset()`.
- Safety invariants (do not relax): backup stock before any write; checksums
  recomputed before any write; a write path must refuse a block whose identity
  (F187/F189) doesn't match the backup's.

## Verified protocol facts (sources in README)

- Bus: 500 kbps, 11-bit IDs. Engine 0x7E0→0x7E8, TCU 0x7E1→0x7E9, Haldex 0x70F→0x779,
  ABS 0x713→0x77D, gateway 0x710→0x77A. Functional broadcast 0x7DF.
- Sessions: 0x03 extended for diag/unlock, 0x02 programming for flash.
- Security level for calibration on SIMOS/MED17: requestSeed **0x11** / sendKey 0x12.
- VAG ident DIDs: F190 VIN, F187 part no, F189 sw ver, F191 hw no, F1A3 hw ver,
  F197 system name, F1AD engine code, F19E ODX id, F1A2 ODX ver, F18C serial,
  F1DF prog info, F1F4 bootloader, F17C FAZIT, F186 active session, F15A workshop log.
- SA2 VM opcodes: 81 RSL, 82 RSR, 93 ADD u32, 84 SUB u32, 87 EOR u32, 68 FOR u8,
  49 NEXT, 4A BCC u8, 6B BRA u8, 4C FIN. Verified bit-exact vs reference (2000-seed fuzz).
- SIMOS18.1 SA2 script and CAL block (0x80A80000, 0x80000) are in `vag/profiles.py`.
- J2534: ISO15765 channel + FLOW_CONTROL filter (mask FFFFFFFF, pattern rx_id, flow
  tx_id), TxFlags ISO15765_FRAME_PAD (0x40). **ERR_TIMEOUT = 0x09**, ERR_BUFFER_EMPTY
  = 0x10. CLEAR_TX_BUFFER 0x07, CLEAR_RX_BUFFER 0x08. ISO15765_BS 0x1E / ISO15765_STMIN
  0x1F are *our* FC parameters; STMIN_TX 0x23 is the optional transmit override.
  J2534-1 allows **one channel per protocol per device**; PassThruReadMsgs with
  Timeout > 0 **blocks** until pNumMsgs messages arrived or the timeout expired and then
  returns ERR_TIMEOUT with pNumMsgs = the partial count (that partial batch is data).
  RxStatus: TX_MSG_TYPE 0x01 = loopback, START_OF_MESSAGE 0x02 = FF indication (DataSize 4),
  TX_INDICATION 0x08 = transmit done, PADDING_ERROR 0x10, CAN_29BIT_ID 0x100.
- ISO 15765-4 functional addressing: requests to 0x7DF must fit a single frame; the FC
  for a multi-frame *response* goes to the responder's **physical** request id
  (0x7E8 -> 0x7E0; VAG extended range 0x76A..0x77F -> id - 0x6A, e.g. 0x77A -> 0x710);
  an ECU ignores FC on 0x7DF. `isotp.physical_request_id()` is the table.

## Gotchas already paid for

- `threading.Thread` has an internal `_stop()`; never name an attribute `_stop`
  on a Thread subclass (it broke the keepalive once).
- Most J2534 DLLs (Tactrix `op20pt32.dll`) are 32-bit → run **32-bit Python** on
  Windows, or the load fails with WinError 193. `j2534.py` reports this clearly.
- ISO-TP receiver must re-send FC after every `rx_block_size` CFs (fixed; tested).
- ISO-TP `recv(timeout)` bounds the wait for a payload to *start*; once a FF is in, each
  CF gets its own N_Cr window. A short polling timeout must never abort a transfer the
  receiver already acknowledged (bit the simulated ECU; fixed; tested).
- A simulated vehicle preset must be *started* before a tester can get answers;
  `get_default_vehicle()` does that. `--vehicle golf-tdi-2012`/`r32-2008` have no nodes
  until the UDS/KWP/OBD slices register their preset hooks. `stop()` detaches a node's
  transport and `start()` re-attaches it (`SimulatedNode.on_starting`), so a vehicle can
  be restarted; a node whose transport dies underneath it logs a warning, never `break`s
  silently (fixed; tested).
- Functional (0x7DF) multi-frame: the simulator used to accept FC on 0x7DF and the link
  used to send it there, which a real ECU ignores. Now FC goes to `physical_request_id()`,
  an ECU-side link accepts FC only from its physical rx id, and a functional link keeps
  one reassembly per responder so concurrent FFs are not dropped (fixed; tested).
- Never hold `J2534Device.lock` across a wait: `J2534Channel.read()` always calls
  PassThruReadMsgs with Timeout 0 and sleeps `read_poll_interval` (1 ms) *outside* the
  lock. Holding it inside a blocking 50 ms read stalled every send() behind the router
  reader by seconds (fixed; tested with a FakeLibrary that blocks like a real DLL).
- `J2534Channel.read()` returns a partial batch on ERR_TIMEOUT/ERR_BUFFER_EMPTY; the old
  `return []` lost the one response a spec-conforming DLL had already handed over.
- `J2534RawCanTransport.open()` closes the device it owns when PassThruConnect fails
  (otherwise the Tactrix driver reports ERR_DEVICE_IN_USE until the process exits).
- `j2534-fw` opens ONE ISO15765 channel (`TransportContext.fw_channel`); every link joins
  it with its own FLOW_CONTROL filter(s). Two live links may not claim the same response id.
- Closing a RouterEndpoint / CanRouter / TransportContext wakes a thread blocked in
  `endpoint.recv()` immediately (deque + Condition, not queue.Queue).
- `extended_id` must reach the hardware: `TransportContext(extended_id=True)` connects the
  J2534 channel with CAN_29BIT_ID; silently sending 29-bit ids on an 11-bit channel was a bug.
- The sim ECU serves a pattern, not real maps; `simos18.1.example.json` addresses
  are demo-only. Real addresses must be reverse-engineered or imported from a
  community definition (XDF/A2L import is on the roadmap).

## Roadmap

**Phase 1 (done):** transport (software ISO-TP, J2534, python-can), UDS client,
VAG ident/DTC/SA2/profiles, calibration read, map read/edit, CLI, sim ECU, 45 tests.

**Phase 2 — first real car (next):**
1. Bench-test `--transport j2534` on a live car: `scan`, `identify`, `dtc`.
2. Confirm `read-cal` on the actual ECU family; add its profile if not SIMOS18.1
   (ask the owner for the F197/F187 strings and ECU family before guessing).
3. XDF (TunerPro) and A2L import into `CalibrationDefinition`.
4. Per-ECU checksum correction (SIMOS18 uses CRC32 regions + a block checksum;
   MED17 differs) — implement `calibration/checksum_<family>.py` with tests.
5. Write path: `UdsClient.download()` (RequestDownload/TransferData/TransferExit),
   `VagEcuSession.write_block()` with: programming session, SA2 unlock, erase
   routine (0x31 0xFF00), checksum verify routine (0x31 0x0202), reset, re-identify.
   Must include a dry-run mode and a mandatory stock-backup check.
6. Logging/live-data: ReadDataByIdentifier polling of measuring blocks to CSV.

**Phase 3 — product:** PySide6 GUI over `VagEcuSession` + `CalibrationDefinition`;
per-VIN license; definition catalogue; SEMA/CARB compliance path before any sale.

## What to ask the owner before guessing

- Which exact cars/ECUs (year, engine code, F187 part number) are on the track cars.
- Which J2534 interface (Tactrix OpenPort 2.0 assumed) and Python bitness installed.
- Whether a stock bin / FRF for the ECU is available (it unlocks the SA2 script and
  real map addresses).
