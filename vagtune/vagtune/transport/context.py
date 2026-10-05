"""
TransportContext: one object that opens the hardware and hands out links.

The CLI, the autoscan and the future GUI all need the same thing: "give me an
ISO-TP link to module X" and "give me a TP 2.0 channel to module Y" on whatever
hardware the user plugged in, without each caller knowing how that hardware is
shared. A :class:`TransportContext` owns the physical transport (behind a
:class:`~vagtune.transport.router.CanRouter`) and builds links on demand.

+------------+---------------------------------------------+------------+------------------+
| kind       | what it opens                               | ISO-TP     | TP 2.0           |
+============+=============================================+============+==================+
| ``fake``   | default :class:`SimulatedVehicle` + router  | software   | yes              |
| ``can``    | :class:`PythonCanTransport` + router        | software   | yes              |
| ``j2534``  | :class:`J2534RawCanTransport` + router      | software   | yes (universal)  |
| ``j2534-fw``| one shared :class:`J2534IsoTpChannel`       | firmware   | no (TransportError) |
+------------+---------------------------------------------+------------+------------------+

``j2534-fw`` uses the device's own ISO15765 channel, which is fastest for flashing
but cannot carry raw frames, so TP 2.0 (and sniffing) are refused with a clear
error pointing at ``j2534``. J2534-1 allows one ISO15765 channel per device, so the
context opens it once and every :meth:`TransportContext.isotp_link` joins it (one
flow-control filter per response id; a functional link with ``extra_rx_ids`` gets
one per responder). Two live links may not claim the same response id.
"""

from __future__ import annotations

import logging
from typing import Any, Iterable, Optional

from .base import IsoTpLink, RawCanTransport, TransportError
from .isotp import IsoTpConfig, SoftwareIsoTpLink
from .router import AcceptSpec, CanRouter

log = logging.getLogger(__name__)


class TransportContext:
    """Opens one piece of hardware (or the simulated vehicle) and hands out links."""

    KINDS = ("fake", "can", "j2534", "j2534-fw")

    def __init__(
        self,
        kind: str,
        *,
        dll_path: Optional[str] = None,
        can_interface: str = "socketcan",
        can_channel: str = "can0",
        bitrate: int = 500_000,
        vehicle_preset: Optional[str] = None,
        extended_id: bool = False,
    ) -> None:
        """``extended_id`` selects 29-bit CAN ids for the whole context: the J2534
        CAN/ISO15765 channel is connected with ``CAN_29BIT_ID`` and every link built
        here sends 29-bit frames. VAG diagnostics use 11-bit ids; this exists for
        ISO 15765-4 29-bit vehicles and must never be silently ignored."""
        kind = kind.lower()
        if kind not in self.KINDS:
            raise TransportError(f"unknown transport kind {kind!r} (expected one of {', '.join(self.KINDS)})")
        self.kind = kind
        self.dll_path = dll_path
        self.can_interface = can_interface
        self.can_channel = can_channel
        self.bitrate = bitrate
        self.vehicle_preset = vehicle_preset
        self.extended_id = extended_id
        self.vehicle: Any = None            # SimulatedVehicle for kind "fake"
        self._router: Optional[CanRouter] = None
        self._fw_device: Any = None         # J2534Device for kind "j2534-fw"
        self._fw_channel: Any = None        # J2534IsoTpChannel shared by every j2534-fw link
        self._closed = False
        self._link_counter = 0

        if kind == "fake":
            from .fakebus import get_default_vehicle
            self.vehicle = get_default_vehicle(vehicle_preset)
            transport = self.vehicle.bus.attach("tester")
            self._router = CanRouter(transport, name=f"fake:{self.vehicle.preset}")
        elif kind == "can":
            from .socketcan import PythonCanTransport
            transport = PythonCanTransport(interface=can_interface, channel=can_channel, bitrate=bitrate)
            self._router = CanRouter(transport, name=f"can:{can_interface}:{can_channel}")
        elif kind == "j2534":
            from .j2534 import J2534RawCanTransport
            transport = J2534RawCanTransport(dll_path=dll_path, bitrate=bitrate, extended=extended_id)
            self._router = CanRouter(transport, name="j2534")
        else:  # j2534-fw
            from .j2534 import J2534Device, J2534IsoTpChannel
            # Open device + channel here, not on the first link, so the CLI reports a
            # DLL/Windows/cable problem up front; the channel closes the device it owns.
            self._fw_device = J2534Device(dll_path)
            self._fw_channel = J2534IsoTpChannel(self._fw_device, bitrate=bitrate,
                                                 extended=extended_id, owns_device=True)
            self._fw_channel.open()
        log.debug("transport context %s opened", self.describe())

    # -- introspection -------------------------------------------------------------

    def describe(self) -> str:
        if self.kind == "fake":
            return f"fake (simulated vehicle {self.vehicle.preset!r})"
        if self.kind == "can":
            return f"can ({self.can_interface}:{self.can_channel} @ {self.bitrate})"
        if self.kind == "j2534":
            return f"j2534 raw CAN ({self._router.transport.dll_path})"
        return f"j2534-fw ({self._fw_device.dll_path})"

    @property
    def router(self) -> Optional[CanRouter]:
        """The frame router, or ``None`` for ``j2534-fw`` (no raw frame access)."""
        return self._router

    @property
    def fw_channel(self) -> Any:
        """The shared :class:`J2534IsoTpChannel` (``j2534-fw`` only), else ``None``."""
        return self._fw_channel

    @property
    def supports_raw_frames(self) -> bool:
        return self._router is not None

    def _require_open(self) -> None:
        if self._closed:
            raise TransportError("transport context is closed")

    def _next_name(self, prefix: str) -> str:
        self._link_counter += 1
        return f"{prefix}{self._link_counter}"

    # -- link factories ------------------------------------------------------------

    def isotp_link(self, tx_id: int, rx_id: int, *, extra_rx_ids: Iterable[int] = (),
                   config: Optional[IsoTpConfig] = None) -> IsoTpLink:
        """An ISO-TP link tester->``tx_id``, ECU->``rx_id`` (plus ``extra_rx_ids``).

        Router kinds get a :class:`SoftwareIsoTpLink` on a private router endpoint;
        closing the link unsubscribes the endpoint. ``j2534-fw`` gets a
        :class:`J2534IsoTpLink` on the context's shared ISO15765 channel (``config``
        does not apply there: BS/STmin live in the firmware). Functional links
        (``tx_id=0x7DF`` + ``extra_rx_ids``) work on every kind.
        """
        self._require_open()
        extra = frozenset(int(i) for i in extra_rx_ids)
        if self._router is not None:
            endpoint = self._router.endpoint({rx_id} | extra,
                                             name=self._next_name(f"isotp-{rx_id:03X}-"))
            return SoftwareIsoTpLink(endpoint, tx_id, rx_id, extra_rx_ids=extra, config=config,
                                     extended_id=self.extended_id, owns_transport=True)
        from .j2534 import J2534IsoTpLink
        if config is not None:
            log.debug("j2534-fw ignores IsoTpConfig: block size / STmin are set in the device firmware")
        return J2534IsoTpLink(tx_id, rx_id, channel=self._fw_channel, extra_rx_ids=extra,
                              extended_id=self.extended_id)

    def tp20_channel(self, logical_address: int, **kw: Any) -> Any:
        """A VW TP 2.0 channel to ``logical_address`` (KWP2000 modules).

        Needs raw frame access, so ``j2534-fw`` refuses. The TP 2.0 implementation
        lives in :mod:`vagtune.transport.tp20`; if that module is missing or broken
        the error says so rather than failing with an ImportError deep inside a
        command.
        """
        self._require_open()
        if self._router is None:
            raise TransportError(
                "TP 2.0 needs raw CAN frames; the j2534-fw kind only offers the device's "
                "ISO15765 channel. Use --transport j2534 (or can) for KWP2000 modules."
            )
        try:
            from .tp20 import Tp20Channel
        except ImportError as exc:
            raise TransportError(f"TP 2.0 transport not available: {exc}") from exc
        return Tp20Channel(self._router, logical_address, **kw)

    def raw_endpoint(self, accept: AcceptSpec = None, *, name: str = "",
                     queue_size: int = 4096) -> RawCanTransport:
        """A raw-frame endpoint for sniffing/probing (``accept=None`` sees everything)."""
        self._require_open()
        if self._router is None:
            raise TransportError(
                "raw frame access is not available on j2534-fw; use --transport j2534"
            )
        return self._router.endpoint(accept, name=name or self._next_name("raw"), queue_size=queue_size)

    # -- lifecycle -----------------------------------------------------------------

    def close(self) -> None:
        """Close the router (and its transport) / the shared device. Idempotent.

        For ``fake`` this detaches the tester from the simulated bus; the vehicle
        itself keeps running so the next context attaches instantly.
        """
        if self._closed:
            return
        self._closed = True
        if self._router is not None:
            self._router.close()
        if self._fw_channel is not None:
            self._fw_channel.close()       # also closes the device it owns
        elif self._fw_device is not None:
            self._fw_device.close()
        log.debug("transport context %s closed", self.kind)

    def __enter__(self) -> "TransportContext":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<TransportContext {self.describe()} closed={self._closed}>"
