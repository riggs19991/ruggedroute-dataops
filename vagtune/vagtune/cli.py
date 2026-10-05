"""
vagtune command-line interface.

The GUI you build later will sit on exactly the same library calls; this CLI is both
the first usable front end and the reference for how the pieces fit together.

Subcommands live in :mod:`vagtune.commands` (one module per area, each exposing
``register(sub, add_common_args)``); this file only builds the parser and runs the
selected command.

Transport selection is shared by every car-facing command:
    --transport {fake,can,j2534,j2534-fw}   (default: fake, so everything runs with no hardware)
    --dll PATH                              J2534 DLL path (or set VAGTUNE_J2534_DLL)
    --can-interface / --can-channel         for the python-can path
    --vehicle PRESET                        simulated vehicle for --transport fake
    --module TOKEN                          module name (engine, gateway, ...) or address word (01, 19, ...)

Examples:
    vagtune identify --transport j2534
    vagtune dtc --transport j2534 --module 19
    vagtune read-cal --transport j2534-fw --profile simos18.1 --out stock.bin
    vagtune show-map --def definitions/simos18.1.example.json --bin stock.bin --map boost_target
    vagtune sa2 --script 6802814A... --seed 1A2B3C4D
"""

from __future__ import annotations

import argparse
import logging
import sys
from typing import Optional

from . import __version__
from .commands import REGISTRARS
from .commands._common import add_common_args


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="vagtune",
                                description="VAG ECU diagnostic & calibration toolkit over OBD2")
    p.add_argument("--version", action="version", version=f"vagtune {__version__}")
    p.add_argument("-v", "--verbose", action="count", default=0, help="-v info, -vv debug")
    sub = p.add_subparsers(dest="command", required=True)
    for register in REGISTRARS:
        register(sub, add_common_args)
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
