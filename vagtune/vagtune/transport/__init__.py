"""Transport layer: raw CAN links, ISO-TP links, the frame router and the simulated vehicle."""

from __future__ import annotations

from typing import Iterable, Optional

from .base import (
    CanFrame,
    IsoTpLink,
    RawCanTransport,
    TransportError,
    TransportNotOpen,
    TransportTimeout,
)
from .isotp import IsoTpConfig, SoftwareIsoTpLink, physical_request_id
from .router import CanRouter, RouterEndpoint
from .context import TransportContext
from .fakebus import (
    FakeCanBus,
    FakeCanTransport,
    SimulatedNode,
    SimulatedVehicle,
    UdsNode,
    get_default_vehicle,
    reset_default_vehicle,
)
from .fake import FakeIsoTpLink, SimulatedEcu, make_fake_pair

__all__ = [
    "CanFrame",
    "IsoTpLink",
    "RawCanTransport",
    "TransportError",
    "TransportNotOpen",
    "TransportTimeout",
    "IsoTpConfig",
    "SoftwareIsoTpLink",
    "physical_request_id",
    "CanRouter",
    "RouterEndpoint",
    "TransportContext",
    "FakeCanBus",
    "FakeCanTransport",
    "SimulatedNode",
    "SimulatedVehicle",
    "UdsNode",
    "get_default_vehicle",
    "reset_default_vehicle",
    "FakeIsoTpLink",
    "SimulatedEcu",
    "make_fake_pair",
    "make_isotp_link",
]


class _StandaloneIsoTpLink(SoftwareIsoTpLink):
    """A SoftwareIsoTpLink that owns the TransportContext it was built from.

    :func:`make_isotp_link` hands out exactly one link per piece of hardware, so
    closing that link must also release the router and the transport underneath.
    """

    def __init__(self, context: TransportContext, endpoint: RawCanTransport, tx_id: int, rx_id: int,
                 **kw) -> None:
        super().__init__(endpoint, tx_id, rx_id, owns_transport=True, **kw)
        self.context = context

    def close(self) -> None:
        try:
            super().close()
        finally:
            self.context.close()


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
    vehicle_preset: Optional[str] = None,
    extra_rx_ids: Iterable[int] = (),
) -> IsoTpLink:
    """Build a single ISO-TP link from a short backend name.

    kind:
        "fake"      -> software ISO-TP over the simulated vehicle (real framing offline)
        "can"       -> software ISO-TP over python-can (SocketCAN/PCAN/etc.)
        "j2534"     -> software ISO-TP over a J2534 raw CAN channel
        "j2534-fw"  -> J2534IsoTpLink (device-side segmentation, best for flashing)

    This is a convenience for "one link, one ECU"; closing the link releases the
    hardware. Anything that needs several links on one cable (scan, autoscan, a
    keepalive next to a TP 2.0 channel) should build a :class:`TransportContext`
    and ask it for links instead.
    """
    kind = kind.lower()
    if kind == "j2534-fw":
        from .j2534 import J2534IsoTpLink
        return J2534IsoTpLink(tx_id, rx_id, dll_path=dll_path, extended_id=extended_id,
                              bitrate=bitrate, extra_rx_ids=extra_rx_ids)
    if kind not in TransportContext.KINDS:
        raise TransportError(
            f"unknown transport kind {kind!r} (expected one of {', '.join(TransportContext.KINDS)})"
        )
    context = TransportContext(kind, dll_path=dll_path, can_interface=can_interface,
                               can_channel=can_channel, bitrate=bitrate, vehicle_preset=vehicle_preset,
                               extended_id=extended_id)
    try:
        extra = frozenset(int(i) for i in extra_rx_ids)
        endpoint = context.router.endpoint({rx_id} | extra, name=f"isotp-{rx_id:03X}")
        return _StandaloneIsoTpLink(context, endpoint, tx_id, rx_id,
                                    extended_id=extended_id, extra_rx_ids=extra)
    except Exception:
        context.close()
        raise
