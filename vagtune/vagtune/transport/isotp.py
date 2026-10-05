"""
Software ISO 15765-2 (ISO-TP) implementation.

This runs the whole segmentation protocol in Python on top of a
:class:`~vagtune.transport.base.RawCanTransport`. It is the fallback used with raw
CAN adapters (python-can / SocketCAN). When you move to a J2534 pass-thru for real
flashing, use :class:`vagtune.transport.j2534.J2534IsoTpLink` instead, which lets the
device firmware do segmentation and hits far higher throughput.

Protocol summary (single-frame and multi-frame, classic 8-byte CAN):

    PCI nibble (high nibble of byte 0):
        0x0  Single Frame (SF)      low nibble = length (1..7)
        0x1  First Frame (FF)       12-bit length across byte0 low nibble + byte1
        0x2  Consecutive Frame (CF) low nibble = sequence number (wraps 0..15)
        0x3  Flow Control (FC)      low nibble = flow status (0 CTS, 1 WAIT, 2 OVFLW)
                                    byte1 = block size, byte2 = STmin

Only "normal addressing" is implemented (the 11-bit or 29-bit CAN ID *is* the
address, no extra address byte inside the payload). That is what every VAG engine
and transmission module uses on the OBD2 diagnostic bus.
"""

from __future__ import annotations

import logging
import time
from typing import Optional

from .base import CanFrame, IsoTpLink, RawCanTransport, TransportError, TransportTimeout

log = logging.getLogger(__name__)

# ---- PCI types -----------------------------------------------------------------
PCI_SF = 0x0
PCI_FF = 0x1
PCI_CF = 0x2
PCI_FC = 0x3

# ---- Flow-control status -------------------------------------------------------
FC_CONTINUE = 0x0   # Clear To Send
FC_WAIT = 0x1       # receiver asks sender to wait for another FC
FC_OVERFLOW = 0x2   # receiver buffer too small; abort

# Largest payload a classic single frame can hold, and the FF first-chunk size.
SF_MAX = 7
FF_FIRST = 6

# STmin encodings (ISO 15765-2 table):
#   0x00..0x7F  -> that many milliseconds
#   0xF1..0xF9  -> 100..900 microseconds
# We convert both to seconds for the sender's inter-frame delay.
def decode_stmin(raw: int) -> float:
    if raw <= 0x7F:
        return raw / 1000.0
    if 0xF1 <= raw <= 0xF9:
        return (raw - 0xF0) / 10_000.0
    # Reserved values: spec says treat as the maximum (127 ms) to be safe.
    return 0x7F / 1000.0


def encode_stmin(seconds: float) -> int:
    if seconds <= 0:
        return 0x00
    ms = seconds * 1000.0
    if ms < 1.0:
        hundreds_us = max(1, min(9, round(ms * 10)))
        return 0xF0 + hundreds_us
    return min(0x7F, round(ms))


class IsoTpConfig:
    """Tunable timing/flow parameters.

    Defaults follow common VAG tester behaviour: we (the tester) advertise block
    size 0 (send everything, no further FC) and STmin 0 when *receiving*, and we
    honour whatever the ECU asks for when *sending*.
    """

    def __init__(
        self,
        *,
        tx_padding: Optional[int] = 0x55,     # VAG expects 8-byte frames padded with 0x55
        rx_block_size: int = 0,               # 0 = no block limit on frames we receive
        rx_stmin: float = 0.0,                # STmin we request from the ECU (seconds)
        n_as: float = 1.0,                    # sender: max time for a frame to be sent
        n_bs: float = 1.0,                    # sender: max wait for a flow-control frame
        n_cr: float = 1.0,                    # receiver: max wait for a consecutive frame
        wait_frame_limit: int = 8,            # max consecutive FC.WAIT before giving up
    ) -> None:
        self.tx_padding = tx_padding
        self.rx_block_size = rx_block_size
        self.rx_stmin = rx_stmin
        self.n_as = n_as
        self.n_bs = n_bs
        self.n_cr = n_cr
        self.wait_frame_limit = wait_frame_limit


class SoftwareIsoTpLink(IsoTpLink):
    """ISO-TP over a raw-CAN transport, segmentation performed here."""

    def __init__(
        self,
        transport: RawCanTransport,
        tx_id: int,
        rx_id: int,
        *,
        extended_id: bool = False,
        config: Optional[IsoTpConfig] = None,
    ) -> None:
        super().__init__(tx_id, rx_id, extended_id=extended_id)
        self.transport = transport
        self.cfg = config or IsoTpConfig()
        if not self.transport.is_open:
            self.transport.open()
        self.transport.set_accept_ids([rx_id])

    # -- helpers -----------------------------------------------------------------

    def _pad(self, data: bytes) -> bytes:
        if self.cfg.tx_padding is None:
            return data
        if len(data) >= 8:
            return data[:8]
        return data + bytes([self.cfg.tx_padding]) * (8 - len(data))

    def _send_frame(self, data: bytes) -> None:
        self.transport.send(
            CanFrame(self.tx_id, self._pad(data), is_extended_id=self.extended_id)
        )

    def _recv_matching(self, timeout: float) -> Optional[CanFrame]:
        """Receive the next frame addressed to us (rx_id), dropping everything else."""
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            frame = self.transport.recv(remaining)
            if frame is None:
                return None
            if frame.arbitration_id == self.rx_id:
                return frame
            # Frame for some other module; ignore and keep waiting.

    # -- transmit path -----------------------------------------------------------

    def send(self, payload: bytes) -> None:
        if not payload:
            raise ValueError("ISO-TP payload must be at least one byte")
        if len(payload) <= SF_MAX:
            self._send_single_frame(payload)
        else:
            self._send_multi_frame(payload)

    def _send_single_frame(self, payload: bytes) -> None:
        pci = bytes([(PCI_SF << 4) | len(payload)])
        self._send_frame(pci + payload)

    def _send_multi_frame(self, payload: bytes) -> None:
        total = len(payload)
        if total > 0xFFF:
            # Length escape (FF with low nibble+byte1 = 0, then 32-bit length) exists,
            # but no VAG calibration transfer needs a single payload this large: the
            # UDS TransferData service chunks data itself. Guard rather than mis-send.
            raise TransportError(
                f"ISO-TP payload {total} bytes exceeds 4095; chunk at the UDS layer instead"
            )

        # --- First Frame ---
        ff = bytes([(PCI_FF << 4) | ((total >> 8) & 0x0F), total & 0xFF]) + payload[:FF_FIRST]
        self._send_frame(ff)
        offset = FF_FIRST

        # --- Wait for the ECU's first Flow Control ---
        block_size, stmin = self._await_flow_control()
        seq = 1
        frames_in_block = 0

        while offset < total:
            chunk = payload[offset:offset + 7]
            cf = bytes([(PCI_CF << 4) | (seq & 0x0F)]) + chunk
            self._send_frame(cf)
            offset += len(chunk)
            seq = (seq + 1) & 0x0F
            frames_in_block += 1

            if offset >= total:
                break

            if block_size != 0 and frames_in_block >= block_size:
                # Block finished; ECU must send another FC before we continue.
                block_size, stmin = self._await_flow_control()
                frames_in_block = 0
            elif stmin > 0:
                time.sleep(stmin)

    def _await_flow_control(self) -> tuple[int, float]:
        """Block until a usable FC frame arrives; return (block_size, stmin_seconds)."""
        waits = 0
        while True:
            frame = self._recv_matching(self.cfg.n_bs)
            if frame is None:
                raise TransportTimeout("timed out waiting for ISO-TP flow control (N_Bs)")
            if len(frame.data) < 3:
                continue
            if (frame.data[0] >> 4) != PCI_FC:
                # Not a flow-control frame (could be stray) - ignore.
                continue
            status = frame.data[0] & 0x0F
            if status == FC_CONTINUE:
                return frame.data[1], decode_stmin(frame.data[2])
            if status == FC_WAIT:
                waits += 1
                if waits > self.cfg.wait_frame_limit:
                    raise TransportError("ECU sent too many FC.WAIT frames")
                continue
            if status == FC_OVERFLOW:
                raise TransportError("ECU reported ISO-TP buffer overflow (FC.OVFLW)")
            # Unknown flow status - treat as protocol error.
            raise TransportError(f"invalid ISO-TP flow status 0x{status:X}")

    # -- receive path ------------------------------------------------------------

    def recv(self, timeout: float) -> Optional[bytes]:
        deadline = time.monotonic() + timeout
        frame = self._recv_matching(timeout)
        if frame is None:
            return None
        if len(frame.data) == 0:
            return None

        pci_type = frame.data[0] >> 4

        if pci_type == PCI_SF:
            length = frame.data[0] & 0x0F
            return bytes(frame.data[1:1 + length])

        if pci_type == PCI_FF:
            return self._recv_multi_frame(frame, deadline)

        if pci_type == PCI_FC:
            # A lone flow-control frame with no transfer in progress - ignore and
            # keep looking until the deadline.
            remaining = deadline - time.monotonic()
            return self.recv(remaining) if remaining > 0 else None

        if pci_type == PCI_CF:
            # Orphan consecutive frame (we missed the FF) - cannot reassemble.
            log.debug("dropping orphan consecutive frame: %s", frame)
            remaining = deadline - time.monotonic()
            return self.recv(remaining) if remaining > 0 else None

        return None

    def _send_flow_control(self) -> None:
        """Send FC.CTS advertising our receive block size and STmin."""
        fc = bytes([(PCI_FC << 4) | FC_CONTINUE,
                    self.cfg.rx_block_size & 0xFF,
                    encode_stmin(self.cfg.rx_stmin)])
        self._send_frame(fc)

    def _recv_multi_frame(self, first: CanFrame, deadline: float) -> bytes:
        total = ((first.data[0] & 0x0F) << 8) | first.data[1]
        buf = bytearray(first.data[2:2 + min(FF_FIRST, total)])

        # Clear To Send after the First Frame.
        self._send_flow_control()

        expected_seq = 1
        frames_in_block = 0
        block_size = self.cfg.rx_block_size

        while len(buf) < total:
            # Each consecutive frame gets its own N_Cr window, bounded by the caller's
            # overall deadline.
            remaining = min(self.cfg.n_cr, max(0.0, deadline - time.monotonic()))
            if remaining <= 0:
                raise TransportTimeout("timed out waiting for ISO-TP consecutive frame (N_Cr)")
            frame = self._recv_matching(remaining)
            if frame is None:
                raise TransportTimeout("timed out waiting for ISO-TP consecutive frame (N_Cr)")
            if (frame.data[0] >> 4) != PCI_CF:
                continue
            seq = frame.data[0] & 0x0F
            if seq != expected_seq:
                raise TransportError(
                    f"ISO-TP sequence error: expected {expected_seq}, got {seq}"
                )
            need = total - len(buf)
            buf.extend(frame.data[1:1 + min(7, need)])
            expected_seq = (expected_seq + 1) & 0x0F
            frames_in_block += 1

            # If we advertised a block size, the sender stops after that many CFs and
            # waits for us to say "go on" with another Flow Control frame.
            if block_size != 0 and frames_in_block >= block_size and len(buf) < total:
                self._send_flow_control()
                frames_in_block = 0

        return bytes(buf)

    def flush_rx(self) -> None:
        self.transport.flush_rx()

    def close(self) -> None:
        # The link does not own the transport's lifecycle by default; closing the
        # transport is the caller's choice. We only drop buffered data.
        self.flush_rx()
