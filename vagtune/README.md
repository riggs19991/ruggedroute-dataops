# vagtune

Laptop-side toolkit for Volkswagen Group ECUs over OBD2: identification, fault codes,
security unlock (SA2 seed/key), calibration read, and scaled map editing. Built as the
engine for a future tuning product; today it is a library + CLI with a simulated ECU
so the whole stack can be developed and tested with no car attached.

## Scope and legal note

This toolkit is intended for **off-road / track-only vehicles** that are trailered to
and from the track and are not operated on public roads. It deliberately contains no
emissions-defeat functionality (catalyst, EGR, DPF, or O2-monitor deletes; readiness
spoofing) and none should be added.

In the United States, modifying the emission-control behaviour of a vehicle that was
originally certified for road use is regulated under the Clean Air Act regardless of
how the vehicle is used afterwards, and the EPA has enforced against sellers of ECU
tuning software. **Do not sell or distribute tunes without legal advice.** This is a
development tool, not legal advice.

## Hardware

| Path | Hardware | Transport class | Notes |
|------|----------|-----------------|-------|
| J2534 (recommended) | Tactrix OpenPort 2.0 or any J2534-1 pass-thru | `J2534IsoTpLink` | Segmentation done in device firmware; best for flashing. Windows only. |
| Raw CAN | Any python-can adapter (PCAN, Kvaser, SLCAN, SocketCAN) wired to OBD2 pins 6/14 | `PythonCanTransport` + `SoftwareIsoTpLink` | Portable; Python does ISO-TP. |
| None | — | `FakeIsoTpLink` + `SimulatedEcu` | Default for development and tests. |

Bus is 500 kbps classic CAN with 11-bit IDs. Engine ECU answers at 0x7E0 → 0x7E8.

## Install (Windows, Tactrix)

1. Install the Tactrix OpenPort driver (it registers `op20pt32.dll`).
2. Most J2534 DLLs are **32-bit**. Install a 32-bit Python 3.11+ (the `python.org`
   installer offers it) or confirm your vendor ships a 64-bit DLL.
3. In the project folder:

```powershell
py -3.11-32 -m venv .venv
.\.venv\Scripts\activate
pip install -e ".[dev]"
python -m pytest -q          # 45 tests should pass
vagtune --help
```

Optional: `pip install -e ".[dev,can]"` for the python-can path. Set
`VAGTUNE_J2534_DLL` to your DLL path, or pass `--dll`.

## Quick start

Everything defaults to the simulated ECU, so these work immediately:

```
vagtune identify
vagtune dtc
vagtune read-cal --profile simos18.1 --out stock.bin
vagtune show-map --def definitions/simos18.1.example.json --bin stock.bin --map boost_target
vagtune scale-map --def definitions/simos18.1.example.json --bin stock.bin \
    --map boost_target --multiplier 1.05 --clamp 300 --out tune.bin
vagtune sa2 --script <hex> --seed <hex>
```

On a real car, add `--transport j2534` (and `--dll` if needed). Start with
`scan`, then `identify`, then `dtc`. Do **not** run `read-cal` until the ECU
family has been confirmed from the `identify` output (F197 / F187 strings).

## Library usage

```python
from vagtune.transport import make_isotp_link
from vagtune.uds import UdsClient
from vagtune.vag import VagEcuSession, get_profile

link = make_isotp_link("j2534", tx_id=0x7E0, rx_id=0x7E8)
with UdsClient(link) as client:
    ecu = VagEcuSession(client, get_profile("simos18.1"))
    ecu.enter_extended_session()
    print(ecu.read_identity().pretty())
    for d in ecu.read_dtcs():
        print(d)
    client.start_tester_present()
    ecu.unlock()                       # SA2 seed/key, level 0x11
    cal = ecu.read_calibration()       # bytes of the CAL block
```

## Architecture

```
cli.py  ─────────────────────────────┐
vag/     VagEcuSession, profiles, SA2, DTC decode, module IDs
uds/     UdsClient (ISO 14229): sessions, DIDs, DTCs, security, upload/download
transport/  IsoTpLink  ← J2534IsoTpLink | SoftwareIsoTpLink(RawCanTransport) | FakeIsoTpLink
calibration/  FlashImage, Scaling/Map/Axis, CalibrationDefinition (JSON), checksums
```

See `CLAUDE.md` for conventions, verified protocol facts, and the detailed roadmap.

## Roadmap

- **Phase 1 (this release):** full read-side stack + sim ECU + CLI + tests.
- **Phase 2:** first live car; XDF/A2L definition import; per-family checksum
  correction; UDS download (write) path with stock backup + dry-run; live data logging.
- **Phase 3:** desktop GUI (PySide6) over the same library; license/catalogue;
  compliance path before any commercial release.

## Sources and attribution

Protocol facts in this project were checked against:

- **bri3d/VW_Flash** (BSD-2-Clause, Brian Ledbetter and contributors) — reference for
  VAG CAN IDs, identification DIDs, the SIMOS18 SA2 script and block map, security
  level 0x11, and the J2534 ISO15765 flow-control filter setup.
  https://github.com/bri3d/VW_Flash
- **sa2_seed_key** (MIT, Brian Ledbetter) — SA2 opcode semantics. `vagtune/vag/sa2.py`
  is an independent implementation; the test suite verifies it bit-exact against the
  documented semantics over 2,000 random seeds.
- SAE J2534-1 v04.04 — PassThru function signatures, Ioctl IDs, config parameters,
  return codes.
- ISO 14229-1 (UDS) and ISO 15765-2 (ISO-TP) — service and transport behaviour.

No code was copied from the referenced projects; they were read to confirm facts.
