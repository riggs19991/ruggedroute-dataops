"""
Transport abstractions.

Two levels exist on purpose:

* :class:`RawCanTransport` moves individual classic-CAN frames (<= 8 data bytes).
  Implementations: :mod:`vagtune.transport.socketcan` (python-can) and
  :class:`vagtune.transport.j2534.J2534RawCanTransport`.

* :class:`IsoTpLink` moves whole ISO 15765-2 payloads (up to 4095 bytes, or more
  with the length-escape) between a tester CAN ID and an ECU CAN ID.
  Implementations: :class:`vagtune.transport.isotp.SoftwareIsoTpLink` (segmentation
  done in Python on top of a RawCanTransport) and
  :class:`vagtune.transport.j2534.J2534IsoTpLink` (segmentation done inside the
  pass-thru device firmware, which is what you want for flashing throughput).

The UDS client only ever sees an :class:`IsoTpLink`, so the hardware can be swapped
without touching protocol code.
"""

from __future__ import annotations

import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Iterable, Optional, Sequence

log = logging.getLogger(__name__)

CAN_MAX_DLC = 8
CAN_STD_ID_MAX = 0x7FF
CAN_EXT_ID_MAX = 0x1FFFFFFF


class TransportError(Exception):
    """Base class for everything that goes wrong below the UDS layer."""


class TransportTimeout(TransportError):
    """No frame / payload arrived before the deadline."""


class TransportNotOpen(TransportError):
    """Operation attempted on a transport that was never opened or was closed."""


@dataclass(frozen=True)
class CanFrame:
    """One classic CAN 2.0 frame.

    ``timestamp`` is a monotonic clock reading taken when the frame was created on
    this side (receive time for RX frames, build time for TX frames). It is excluded
    from equality so frames with identical content compare equal in tests.
    """

    arbitration_id: int
    data: bytes
    is_extended_id: bool = False
    timestamp: float = field(default_factory=time.monotonic, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.data, (bytes, bytearray)):
            object.__setattr__(self, "data", bytes(self.data))
        if len(self.data) > CAN_MAX_DLC:
            raise ValueError(f"classic CAN frame cannot carry {len(self.data)} bytes (max {CAN_MAX_DLC})")
        limit = CAN_EXT_ID_MAX if self.is_extended_id else CAN_STD_ID_MAX
        if not 0 <= self.arbitration_id <= limit:
            raise ValueError(f"arbitration id 0x{self.arbitration_id:X} out of range for "
                             f"{'extended' if self.is_extended_id else 'standard'} CAN id")

    @property
    def dlc(self) -> int:
        return len(self.data)

    def __str__(self) -> str:
        width = 8 if self.is_extended_id else 3
        return f"{self.arbitration_id:0{width}X} [{self.dlc}] {self.data.hex(' ').upper()}"


class RawCanTransport(ABC):
    """Frame-level CAN access.

    Implementations must be safe to call ``recv`` from one thread while ``send`` is
    called from another (the UDS tester-present keepalive relies on this).
    """

    def __init__(self, bitrate: int = 500_000) -> None:
        self.bitrate = bitrate
        self._open = False

    # -- lifecycle ---------------------------------------------------------------

    @abstractmethod
    def open(self) -> None:
        """Bring the interface up. Idempotent."""

    @abstractmethod
    def close(self) -> None:
        """Tear the interface down. Idempotent."""

    @property
    def is_open(self) -> bool:
        return self._open

    def __enter__(self) -> "RawCanTransport":
        self.open()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    # -- data path ---------------------------------------------------------------

    @abstractmethod
    def send(self, frame: CanFrame) -> None:
        """Queue one frame for transmission (blocking until accepted by the driver)."""

    def send_many(self, frames: Sequence[CanFrame]) -> None:
        """Send several frames back-to-back.

        The default implementation loops; drivers that can batch (J2534
        ``PassThruWriteMsgs`` takes an array) override this to cut USB round trips,
        which matters for consecutive-frame bursts with STmin = 0.
        """
        for frame in frames:
            self.send(frame)

    @abstractmethod
    def recv(self, timeout: float) -> Optional[CanFrame]:
        """Return the next received frame, or ``None`` if ``timeout`` seconds elapse."""

    def set_accept_ids(self, arbitration_ids: Iterable[int]) -> None:  # pragma: no cover - optional
        """Optionally narrow the hardware acceptance filter to these IDs.

        Transports that cannot filter in hardware simply ignore this; the ISO-TP layer
        filters by ID in software anyway.
        """
        return None

    def flush_rx(self) -> None:
        """Discard anything sitting in the receive buffer."""
        while self.recv(0.0) is not None:
            pass


class IsoTpLink(ABC):
    """Payload-level link between one tester ID and one ECU ID."""

    def __init__(self, tx_id: int, rx_id: int, *, extended_id: bool = False) -> None:
        self.tx_id = tx_id
        self.rx_id = rx_id
        self.extended_id = extended_id

    @abstractmethod
    def send(self, payload: bytes) -> None:
        """Transmit a complete ISO-TP payload (handles segmentation)."""

    @abstractmethod
    def recv(self, timeout: float) -> Optional[bytes]:
        """Receive one complete payload, or ``None`` after ``timeout`` seconds."""

    @abstractmethod
    def flush_rx(self) -> None:
        """Discard any buffered inbound payloads/frames."""

    @abstractmethod
    def close(self) -> None:
        """Release the channel. Idempotent."""

    def __enter__(self) -> "IsoTpLink":
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<{type(self).__name__} tx=0x{self.tx_id:X} rx=0x{self.rx_id:X}>"
