"""Diagnostics commands: ``scan``, ``identify``, ``dtc`` (UDS modules)."""

from __future__ import annotations

ORDER = 10  # help ordering: diagnostics first

import argparse
import logging
from typing import Callable

from ..uds.client import UdsClient, UdsTiming
from ..vag import modules as vag_modules
from ._common import open_context, open_session

log = logging.getLogger(__name__)

# Probe timeout per module during `scan`. A present module answers well inside this;
# an absent one costs exactly this long.
SCAN_P2_TIMEOUT = 1.0


def cmd_scan(args: argparse.Namespace) -> int:
    """Probe each known module address for a response (identification DID F190)."""
    found = 0
    with open_context(args) as ctx:
        for name, mod in vag_modules.MODULES.items():
            link = ctx.isotp_link(mod.request_id, mod.response_id)
            client = UdsClient(link, UdsTiming(p2_timeout=SCAN_P2_TIMEOUT))
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


def cmd_identify(args: argparse.Namespace) -> int:
    with open_context(args) as ctx:
        session = open_session(ctx, args.module, profile_key=args.profile)
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


def cmd_dtc(args: argparse.Namespace) -> int:
    with open_context(args) as ctx:
        session = open_session(ctx, args.module)
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


def register(sub: argparse._SubParsersAction, add_common_args: Callable[[argparse.ArgumentParser], None]) -> None:
    sp = sub.add_parser("scan", help="probe all known module addresses")
    add_common_args(sp)
    sp.set_defaults(func=cmd_scan)

    sp = sub.add_parser("identify", help="read ECU identification block")
    add_common_args(sp)
    sp.add_argument("--profile", default=None, help="force an ECU profile key")
    sp.set_defaults(func=cmd_identify)

    sp = sub.add_parser("dtc", help="read or clear fault codes")
    add_common_args(sp)
    sp.add_argument("--clear", action="store_true", help="clear stored DTCs instead of reading")
    sp.set_defaults(func=cmd_dtc)
