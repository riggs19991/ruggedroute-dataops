"""
Raw CAN transport backed by python-can.

This is the portable adapter path. On Linux it typically drives SocketCAN
(``interface="socketcan", channel="can0"``); on Windows it drives whatever
python-can backend matches your hardware (PCAN, Kvaser, Vector, SLCAN, etc.).

For a laptop + OBD2 cable on a VAG car you have two realistic hardware routes:

1. A J2534 pass-thru (Tactrix OpenPort 2.0, etc.) -> use
   :mod:`vagtune.transport.j2534` instead; it is the right tool for flashing.
2. A plain USB-CAN dongle wired to OBD2 pins 6 (CAN-H) and 14 (CAN-L) -> this
   module, paired with :class:`vagtune.transport.isotp.SoftwareIsoTpLink`.

python-can is an optional dependency; importing this module without it raises a
clear error rather than failing deep in a call.
"""

from __future__ import annotations

import logging
from typing import Iterable, Optional

from .base import CanFrame, RawCanTransport, TransportError, TransportNotOpen

log = logging.getLogger(__name__)

try:
    import can as _python_can  # type: ignore
    _HAVE_CAN = True
except Exception:  # pragma: no cover - exercised only when python-can is absent
    _python_can = None
    _HAVE_CAN = False


class PythonCanTransport(RawCanTransport):
    """Classic-CAN frame transport over a python-can ``BusABC``."""

    def __init__(
        self,
        interface: str = "socketcan",
        channel: str = "can0",
        bitrate: int = 500_000,
        **bus_kwargs,
    ) -> None:
        super().__init__(bitrate=bitrate)
        if not _HAVE_CAN:
            raise TransportError(
                "python-can is not installed. Install the optional dependency with "
                "`pip install vagtune[can]` to use the CAN adapter path."
            )
        self.interface = interface
        self.channel = channel
        self.bus_kwargs = bus_kwargs
        self._bus = None

    def open(self) -> None:
        if self._open:
            return
        self._bus = _python_can.Bus(
            interface=self.interface,
            channel=self.channel,
            bitrate=self.bitrate,
            **self.bus_kwargs,
        )
        self._open = True
        log.info("opened CAN bus %s:%s @ %d bit/s", self.interface, self.channel, self.bitrate)

    def close(self) -> None:
        if not self._open:
            return
        try:
            self._bus.shutdown()
        finally:
            self._bus = None
            self._open = False
            log.info("closed CAN bus %s:%s", self.interface, self.channel)

    def send(self, frame: CanFrame) -> None:
        if not self._open:
            raise TransportNotOpen("CAN bus is not open")
        msg = _python_can.Message(
            arbitration_id=frame.arbitration_id,
            data=frame.data,
            is_extended_id=frame.is_extended_id,
        )
        try:
            self._bus.send(msg, timeout=1.0)
        except _python_can.CanError as exc:  # pragma: no cover - hardware dependent
            raise TransportError(f"CAN send failed: {exc}") from exc

    def recv(self, timeout: float) -> Optional[CanFrame]:
        if not self._open:
            raise TransportNotOpen("CAN bus is not open")
        msg = self._bus.recv(timeout=max(0.0, timeout))
        if msg is None:
            return None
        return CanFrame(
            arbitration_id=msg.arbitration_id,
            data=bytes(msg.data),
            is_extended_id=bool(msg.is_extended_id),
        )

    def set_accept_ids(self, arbitration_ids: Iterable[int]) -> None:
        if not self._open or self._bus is None:
            return
        ids = list(arbitration_ids)
        if not ids:
            return
        try:
            self._bus.set_filters([{"can_id": i, "can_mask": 0x7FF, "extended": False} for i in ids])
        except Exception:  # pragma: no cover - some backends lack filtering
            log.debug("backend %s does not support hardware filters; filtering in software",
                      self.interface)
