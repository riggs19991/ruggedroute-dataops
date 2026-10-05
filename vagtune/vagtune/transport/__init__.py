"""Transport layer: raw CAN links and ISO-TP links over different hardware."""

from __future__ import annotations

from typing import Optional

from .base import (
    CanFrame,
    IsoTpLink,
    RawCanTransport,
    TransportError,
    TransportNotOpen,
    TransportTimeout,
)
from .isotp import IsoTpConfig, SoftwareIsoTpLink

__all__ = [
    "CanFrame",
    "IsoTpLink",
    "RawCanTransport",
    "TransportError",
    "TransportNotOpen",
    "TransportTimeout",
    "IsoTpConfig",
    "SoftwareIsoTpLink",
    "make_isotp_link",
]


def make_isotp_link(
    kind: str,
    tx_id: int,
    rx_id: int,
    *,
    extended_id: bool = False,
    dll_path: Optional[str] = None,
    can_interface: str = "socketcan",
    can_channel: str = "can0",
    bitrate: int = 500_000,
) -> IsoTpLink:
    """Build an ISO-TP link from a short backend name.

    kind:
        "j2534"    -> J2534IsoTpLink (device-side segmentation, best for flashing)
        "can"      -> SoftwareIsoTpLink over python-can (SocketCAN/PCAN/etc.)
        "fake"     -> in-memory loopback for tests/offline development
    """
    kind = kind.lower()
    if kind == "j2534":
        from .j2534 import J2534IsoTpLink
        return J2534IsoTpLink(tx_id, rx_id, dll_path=dll_path,
                              extended_id=extended_id, bitrate=bitrate)
    if kind == "can":
        from .socketcan import PythonCanTransport
        transport = PythonCanTransport(interface=can_interface, channel=can_channel, bitrate=bitrate)
        return SoftwareIsoTpLink(transport, tx_id, rx_id, extended_id=extended_id)
    if kind == "fake":
        from .fake import make_fake_pair
        link, _ecu = make_fake_pair(tx_id, rx_id)
        return link
    raise TransportError(f"unknown transport kind {kind!r} (expected j2534/can/fake)")
