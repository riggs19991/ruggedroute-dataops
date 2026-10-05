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
               isotp.py     software ISO 15765-2 (SF/FF/CF/FC, BS, STmin, padding)
               j2534.py     ctypes binding; J2534RawCanTransport + J2534IsoTpLink
               socketcan.py python-can RawCanTransport (optional dep)
               fake.py      SimulatedEcu + FakeIsoTpLink  <- use this for ALL dev
  uds/         client.py    UdsClient: request(), services, 0x78 pending, keepalive
               services.py  SIDs/subfunctions/enums    exceptions.py  NRC decode
  vag/         modules.py   CAN IDs + ident DIDs       dtc.py        DTC decode/db
               sa2.py       SA2 seed/key VM            profiles.py   ECU families
               ecu.py       VagEcuSession (identify/dtc/unlock/read block)
  calibration/ image.py     FlashImage (bounds, diff, checksum regions)
               maps.py      Scaling/ScalarValue/Axis/Map  definition.py JSON defs
  cli.py       argparse front end; the GUI must call the same library, not the CLI
definitions/   JSON map definitions (simos18.1.example.json is DEMO addresses only)
tests/         pytest; 45 tests; all protocol logic must stay covered
```

Dependency direction: `calibration` and `vag` depend on `uds` depends on `transport`.
`fake.py` imports `vag.sa2` (so the sim answers seed/key with real math) — that is
the one allowed cross-reference.

## Commands

```
pip install -e ".[dev]"          # python-can path: pip install -e ".[dev,can]"
python -m pytest -q              # must be green before any commit
vagtune --help
vagtune identify                 # default --transport fake (no hardware)
vagtune identify --transport j2534 --dll "C:\...\op20pt32.dll"
vagtune dtc [--clear]
vagtune read-cal --profile simos18.1 --out stock.bin
vagtune show-map --def definitions/simos18.1.example.json --bin stock.bin --map boost_target
vagtune scale-map --def ... --bin stock.bin --map boost_target --multiplier 1.05 --clamp 300 --out tune.bin
vagtune sa2 --script <hex> --seed <hex>
```

## Conventions

- Python >= 3.10, type hints everywhere, `from __future__ import annotations`.
- No placeholder/stub code. If a feature can't be finished, raise a clear error
  (`NotImplementedError` with the reason) — never silently fake success.
- Every protocol change gets a test against `SimulatedEcu` or the ISO-TP loopback.
  Hardware classes (`j2534.py`, `socketcan.py`) must still *import* on Linux/macOS.
- Logging via `logging.getLogger(__name__)`; never `print()` outside `cli.py`.
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
  = 0x10 (both mean "nothing to read"). CLEAR_TX_BUFFER 0x07, CLEAR_RX_BUFFER 0x08.
  ISO15765_BS 0x1E / ISO15765_STMIN 0x1F are *our* FC parameters; STMIN_TX 0x23 is
  the optional transmit override.

## Gotchas already paid for

- `threading.Thread` has an internal `_stop()`; never name an attribute `_stop`
  on a Thread subclass (it broke the keepalive once).
- Most J2534 DLLs (Tactrix `op20pt32.dll`) are 32-bit → run **32-bit Python** on
  Windows, or the load fails with WinError 193. `j2534.py` reports this clearly.
- ISO-TP receiver must re-send FC after every `rx_block_size` CFs (fixed; tested).
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
