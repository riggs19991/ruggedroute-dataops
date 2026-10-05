"""Calibration commands: ``read-cal``, ``show-map``, ``scale-map``, ``sa2``."""

from __future__ import annotations

ORDER = 20  # help ordering: after diagnostics

import argparse
import logging
from typing import Callable

from ..calibration.definition import CalibrationDefinition
from ..vag.profiles import get_profile
from ..vag.sa2 import Sa2Interpreter
from ._common import open_context, open_session

log = logging.getLogger(__name__)


def cmd_read_cal(args: argparse.Namespace) -> int:
    with open_context(args) as ctx:
        session = open_session(ctx, args.module, profile_key=args.profile)
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


def cmd_show_map(args: argparse.Namespace) -> int:
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


def cmd_scale_map(args: argparse.Namespace) -> int:
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


def cmd_sa2(args: argparse.Namespace) -> int:
    interp = Sa2Interpreter(bytes.fromhex(args.script.replace(" ", "")))
    seed = int(args.seed, 16) if isinstance(args.seed, str) else args.seed
    key = interp.compute_key(seed)
    print(f"seed = 0x{seed:08X}")
    print(f"key  = 0x{key:08X}")
    print(f"key bytes = {key.to_bytes(4, 'big').hex(' ').upper()}")
    return 0


def register(sub: argparse._SubParsersAction, add_common_args: Callable[[argparse.ArgumentParser], None]) -> None:
    sp = sub.add_parser("read-cal", help="read the calibration block to a file")
    add_common_args(sp)
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
