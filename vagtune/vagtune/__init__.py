"""
vagtune - laptop-side toolkit for talking to Volkswagen Group ECUs over OBD2.

Layer cake (bottom to top):

    transport/   raw CAN + ISO-TP links (J2534 pass-thru, python-can, software ISO-TP)
    uds/         ISO 14229 UDS client (sessions, DIDs, DTCs, security access, download)
    vag/         VAG-specific knowledge: module CAN IDs, identification DIDs, DTC
                 decoding, SA2 seed/key interpreter, ECU profiles
    calibration/ flash-image handling and scaled map/table access
    cli.py       command-line front end (the GUI sits on top of the same library later)

Nothing in here flashes an ECU yet. Phase 1 is "talk to the car reliably and read
everything"; Phase 2 adds read/write of calibration blocks per ECU family.
"""

from __future__ import annotations

__version__ = "0.1.0"

from .transport.base import CanFrame, IsoTpLink, RawCanTransport, TransportError, TransportTimeout  # noqa: E402
from .uds.client import UdsClient  # noqa: E402
from .uds.exceptions import NegativeResponse, UdsError, UdsTimeout  # noqa: E402

__all__ = [
    "__version__",
    "CanFrame",
    "IsoTpLink",
    "RawCanTransport",
    "TransportError",
    "TransportTimeout",
    "UdsClient",
    "UdsError",
    "UdsTimeout",
    "NegativeResponse",
]
