"""
vagtune command-line interface.

The GUI you build later will sit on exactly the same library calls; this CLI is both
the first usable front end and the reference for how the pieces fit together.

Transport selection is shared by most commands:
    --transport {j2534,can,fake}   (default: fake, so everything runs with no hardware)
    --dll PATH                     J2534 DLL path (or set VAGTUNE_J2534_DLL)
    --can-interface / --can-channel  for the python-can path
    --module {engine,transmission,abs,haldex,gateway}  which ECU to talk to

Examples:
    vagtune identify --transport j2534
    vagtune dtc --transport j2534 --module engine
    vagtune read-cal --transport j2534 --profile simos18.1 --out stock.bin
    vagtune show-map --def definitions/simos18.1.example.json --bin stock.bin --map boost_target
    vagtune sa2 --script 6802814A... --seed 1A2B3C4D
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from . import __version__
from .calibration.definition import CalibrationDefinition
from .transport import make_isotp_link
from .uds.client import UdsClient
from .vag import modules as vag_modules
from .vag.ecu import VagEcuSession
from .vag.profiles import get_profile
from .vag.sa2 import Sa2Interpreter


def _add_transport_args(p: argparse.ArgumentParser) -> None:
    p.add_argument("--transport", choices=["j2534", "can", "fake"], default="fake",
                   help="backend (default: fake, no hardware required)")
    p.add_argument("--dll", default=None, help="J2534 DLL path (or VAGTUNE_J2534_DLL)")
    p.add_argument("--can-interface", default="socketcan", help="python-can interface")
    p.add_argument("--can-channel", default="can0", help="python-can channel")
    p.add_argument("--module", default="engine",
                   choices=sorted(vag_modules.MODULES.keys()),
                   help="which control module to address (default: engine)")


def _open_session(args) -> VagEcuSession:
    mod = vag_modules.MODULES[args.module]
    link = make_isotp_link(
        args.transport,
        tx_id=mod.request_id,
        rx_id=mod.response_id,
        dll_path=args.dll,
        can_interface=args.can_interface,
        can_channel=args.can_channel,
    )
    client = UdsClient(link)
    profile = get_profile(args.profile) if getattr(args, "profile", None) else None
    return VagEcuSession(client, profile)


# ---- commands ------------------------------------------------------------------

def cmd_identify(args) -> int:
    session = _open_session(args)
    try:
        session.client.diagnostic_session_control(0x03)  # extended, harmless
        identity = session.read_identity()
        print("ECU Identification")
        print("==================")
        print(identity.pretty() or "  (no identification DIDs responded)")
        prof = session.detect_profile(identity)
        if prof:
            print(f"\nDetected profile: {prof.display_name}  (key: {prof.key})")
        return 0
    finally:
        session.client.close()


def cmd_dtc(args) -> int:
    session = _open_session(args)
    try:
        session.client.diagnostic_session_control(0x03)
        if args.clear:
            session.clear_dtcs()
            print("Cleared diagnostic information.")
            return 0
        dtcs = session.read_dtcs()
        if not dtcs:
            print("No stored fault codes.")
            return 0
        print(f"{len(dtcs)} fault code(s):")
        for d in dtcs:
            print(f"  {d}")
        return 0
    finally:
        session.client.close()


def cmd_read_cal(args) -> int:
    session = _open_session(args)
    try:
        session.client.diagnostic_session_control(0x03)
        session.detect_profile()
        if session.profile is None and args.profile:
            session.profile = get_profile(args.profile)

        session.client.start_tester_present(interval=2.0)
        session.enter_extended_session()
        session.unlock()  # uses profile SA2 script

        total_hint = {"last": 0}

        def progress(done: int, total: int) -> None:
            pct = int(done * 100 / total) if total else 0
            if pct != total_hint["last"]:
                total_hint["last"] = pct
                print(f"\r  reading calibration... {pct:3d}%  ({done}/{total} bytes)",
                      end="", flush=True)

        data = session.read_calibration(progress=progress)
        print()
        with open(args.out, "wb") as fh:
            fh.write(data)
        print(f"Wrote {len(data)} bytes to {args.out}")
        return 0
    finally:
        session.client.stop_tester_present()
        session.client.close()


def cmd_show_map(args) -> int:
    definition = CalibrationDefinition.from_file(args.definition)
    with open(args.binary, "rb") as fh:
        image = definition.open_image(fh.read(), name=args.binary)
    if args.map == "*":
        print(f"Maps in {definition.name}:")
        for name in definition.list_maps():
            print(f"  {name}")
        return 0
    mp = definition.get_map(args.map)
    print(mp.as_text(image))
    return 0


def cmd_scale_map(args) -> int:
    definition = CalibrationDefinition.from_file(args.definition)
    with open(args.binary, "rb") as fh:
        image = definition.open_image(fh.read(), name=args.binary)
    mp = definition.get_map(args.map)
    print("Before:")
    print(mp.as_text(image))
    mp.scale_all(image, args.multiplier, clamp_phys=args.clamp)
    print(f"\nApplied x{args.multiplier}"
          + (f" (clamped at {args.clamp})" if args.clamp is not None else ""))
    print("\nAfter:")
    print(mp.as_text(image))
    print("\n" + image.diff_summary())
    if args.out:
        image.to_file(args.out)
        print(f"Wrote modified image to {args.out}")
    else:
        print("(no --out given; changes not saved)")
    return 0


def cmd_sa2(args) -> int:
    interp = Sa2Interpreter(bytes.fromhex(args.script.replace(" ", "")))
    seed = int(args.seed, 16) if isinstance(args.seed, str) else args.seed
    key = interp.compute_key(seed)
    print(f"seed = 0x{seed:08X}")
    print(f"key  = 0x{key:08X}")
    print(f"key bytes = {key.to_bytes(4, 'big').hex(' ').upper()}")
    return 0


def cmd_scan(args) -> int:
    """Probe each known module address for a response (identification DID F190)."""
    found = 0
    for name, mod in vag_modules.MODULES.items():
        link = make_isotp_link(
            args.transport, tx_id=mod.request_id, rx_id=mod.response_id,
            dll_path=args.dll, can_interface=args.can_interface, can_channel=args.can_channel,
        )
        client = UdsClient(link)
        try:
            try:
                client.diagnostic_session_control(0x03)
                raw = client.read_data_by_identifier(0xF190)
                vin = raw.split(b"\x00", 1)[0].decode("latin-1", errors="replace")
                print(f"  [{name:<12}] tx=0x{mod.request_id:03X} rx=0x{mod.response_id:03X}  "
                      f"responded (VIN: {vin})")
                found += 1
            except Exception as exc:
                print(f"  [{name:<12}] tx=0x{mod.request_id:03X} rx=0x{mod.response_id:03X}  "
                      f"no response ({type(exc).__name__})")
        finally:
            client.close()
    print(f"\n{found} module(s) responded.")
    return 0


# ---- argument parser -----------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vagtune",
                                description="VAG ECU diagnostic & calibration toolkit over OBD2")
    p.add_argument("--version", action="version", version=f"vagtune {__version__}")
    p.add_argument("-v", "--verbose", action="count", default=0, help="-v info, -vv debug")
    sub = p.add_subparsers(dest="command", required=True)

    sp = sub.add_parser("scan", help="probe all known module addresses")
    _add_transport_args(sp)
    sp.set_defaults(func=cmd_scan)

    sp = sub.add_parser("identify", help="read ECU identification block")
    _add_transport_args(sp)
    sp.add_argument("--profile", default=None, help="force an ECU profile key")
    sp.set_defaults(func=cmd_identify)

    sp = sub.add_parser("dtc", help="read or clear fault codes")
    _add_transport_args(sp)
    sp.add_argument("--clear", action="store_true", help="clear stored DTCs instead of reading")
    sp.set_defaults(func=cmd_dtc)

    sp = sub.add_parser("read-cal", help="read the calibration block to a file")
    _add_transport_args(sp)
    sp.add_argument("--profile", default=None, help="ECU profile key (else auto-detect)")
    sp.add_argument("--out", required=True, help="output .bin path")
    sp.set_defaults(func=cmd_read_cal)

    sp = sub.add_parser("show-map", help="print a map from a bin using a definition")
    sp.add_argument("--def", dest="definition", required=True, help="definition JSON path")
    sp.add_argument("--bin", dest="binary", required=True, help="calibration .bin path")
    sp.add_argument("--map", default="*", help="map name, or * to list all")
    sp.set_defaults(func=cmd_show_map)

    sp = sub.add_parser("scale-map", help="multiply every cell of a map by a factor")
    sp.add_argument("--def", dest="definition", required=True, help="definition JSON path")
    sp.add_argument("--bin", dest="binary", required=True, help="calibration .bin path")
    sp.add_argument("--map", required=True, help="map name")
    sp.add_argument("--multiplier", type=float, required=True, help="e.g. 1.10 for +10%%")
    sp.add_argument("--clamp", type=float, default=None, help="ceiling in physical units")
    sp.add_argument("--out", default=None, help="write modified bin here")
    sp.set_defaults(func=cmd_scale_map)

    sp = sub.add_parser("sa2", help="compute an SA2 seed->key offline")
    sp.add_argument("--script", required=True, help="SA2 script as hex")
    sp.add_argument("--seed", required=True, help="seed as hex (e.g. 1A2B3C4D)")
    sp.set_defaults(func=cmd_sa2)

    return p


def main(argv: Optional[list] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    level = logging.WARNING
    if args.verbose == 1:
        level = logging.INFO
    elif args.verbose >= 2:
        level = logging.DEBUG
    logging.basicConfig(level=level, format="%(levelname)s %(name)s: %(message)s")

    try:
        return args.func(args)
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130
    except Exception as exc:
        if args.verbose >= 2:
            raise
        print(f"error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
