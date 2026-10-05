"""
Software ISO 15765-2 (ISO-TP) implementation.

This runs the whole segmentation protocol in Python on top of a
:class:`~vagtune.transport.base.RawCanTransport`. It is the fallback used with raw
CAN adapters (python-can / SocketCAN) and the universal ``j2534`` mode. When you move
to a J2534 pass-thru for real flashing, use :class:`vagtune.transport.j2534.J2534IsoTpLink`
instead, which lets the device firmware do segmentation and hits far higher throughput.

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

Functional addressing (ISO 15765-4): a tester may *send* to the functional id
(0x7DF, or 0x18DB33F1 with 29-bit ids) and several ECUs answer on their own physical
response ids. Two consequences that this implementation honours:

* The Flow Control for a multi-frame *response* must be sent to that responder's
  **physical request id** (0x7E0 for a response on 0x7E8), never to the functional
  id - an ECU does not accept FC on 0x7DF. :func:`physical_request_id` holds the
  ISO 15765-4 pairing rule (and the VAG extended-id pairing used by the chassis/
  body modules); a link can override it with ``flow_control_ids``.
* Several responders may be mid-transfer at once, so the receiver keeps one
  reassembly state *per arbitration id* and returns payloads as each completes.
* Conversely an ECU (or our simulated one) only accepts Flow Control from the
  tester's physical id (its ``rx_id``); a FC arriving on the functional id is ignored.
"""

from __future__ import annotations

import logging
import time
from typing import Callable, Dict, FrozenSet, Iterable, Mapping, Optional, Union

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

# ISO 15765-4 functional request ids (11-bit and 29-bit normal fixed addressing).
FUNCTIONAL_ID_11BIT = 0x7DF
FUNCTIONAL_ID_29BIT = 0x18DB33F1
FUNCTIONAL_IDS = frozenset({FUNCTIONAL_ID_11BIT, FUNCTIONAL_ID_29BIT})

# Policy that maps a responder's arbitration id to the id our Flow Control goes to.
FlowControlPolicy = Union[Mapping[int, int], Callable[[int], Optional[int]], None]


def physical_request_id(response_id: int) -> Optional[int]:
    """The physical request id paired with ``response_id``, or ``None`` if unknown.

    * ISO 15765-4 11-bit: responses 0x7E8..0x7EF belong to requests 0x7E0..0x7E7.
    * VAG extended diagnostic range (PQ35/MQB chassis, body and gateway modules;
      verified pairs in CLAUDE.md: 0x710->0x77A, 0x713->0x77D, 0x70F->0x779):
      the response id is the request id + 0x6A, so 0x76A..0x77F map back by -0x6A.
    * ISO 15765-4 29-bit normal fixed addressing: a response ``18 DA F1 xx`` (target
      F1 = tester, source xx = ECU) is answered on ``18 DA xx F1``.
    """
    if 0x7E8 <= response_id <= 0x7EF:
        return response_id - 8
    if 0x76A <= response_id <= 0x77F:
        return response_id - 0x6A
    if (response_id >> 16) == 0x18DA and ((response_id >> 8) & 0xFF) == 0xF1:
        return 0x18DA00F1 | ((response_id & 0xFF) << 8)
    return None


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


class _Reassembly:
    """Receive state for one in-progress multi-frame transfer from one responder."""

    __slots__ = ("arbitration_id", "total", "buf", "expected_seq", "frames_in_block", "deadline")

    def __init__(self, arbitration_id: int, total: int, first_chunk: bytes, deadline: float) -> None:
        self.arbitration_id = arbitration_id
        self.total = total
        self.buf = bytearray(first_chunk)
        self.expected_seq = 1
        self.frames_in_block = 0
        self.deadline = deadline

    @property
    def complete(self) -> bool:
        return len(self.buf) >= self.total


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
        extra_rx_ids: Iterable[int] = (),
        owns_transport: bool = False,
        flow_control_ids: FlowControlPolicy = None,
    ) -> None:
        """
        ``extra_rx_ids`` widens the receive filter: frames from any id in
        ``{rx_id} | extra_rx_ids`` are accepted. Two uses:

        * a simulated ECU listens on its physical request id *and* the functional
          broadcast id (0x7DF);
        * a functional OBD tester sends to 0x7DF and collects answers from
          0x7E8..0x7EF. :attr:`last_rx_id` tells the caller which responder a
          payload returned by :meth:`recv` came from.

        ``flow_control_ids`` decides where the Flow Control for a multi-frame payload
        from responder ``r`` is sent: a mapping ``{r: fc_id}``, a callable
        ``r -> fc_id | None``, or ``None`` for the default policy - ``tx_id`` for a
        plain physical link, otherwise :func:`physical_request_id` (ISO 15765-4
        pairing), falling back to ``tx_id``. :attr:`flow_control_ids` exposes the
        resolved table.

        ``owns_transport=True`` makes :meth:`close` also close the transport (used
        for router endpoints handed out by a :class:`~vagtune.transport.context.TransportContext`,
        so closing the link unsubscribes it from the router).
        """
        super().__init__(tx_id, rx_id, extended_id=extended_id)
        self.transport = transport
        self.cfg = config or IsoTpConfig()
        self.extra_rx_ids: FrozenSet[int] = frozenset(int(i) for i in extra_rx_ids)
        self._accept_ids: FrozenSet[int] = frozenset({rx_id}) | self.extra_rx_ids
        self.owns_transport = owns_transport
        self.is_functional = tx_id in FUNCTIONAL_IDS
        self.flow_control_ids: Dict[int, int] = self._resolve_flow_control_ids(flow_control_ids)
        #: arbitration id of the frame that started the last payload :meth:`recv` returned.
        self.last_rx_id: Optional[int] = None
        # In-progress multi-frame receptions, one per responder arbitration id. They
        # survive across recv() calls so a functional request answered by several
        # modules at once yields every payload, in completion order.
        self._partials: Dict[int, _Reassembly] = {}
        if not self.transport.is_open:
            self.transport.open()
        self.transport.set_accept_ids(sorted(self._accept_ids))

    @property
    def accept_ids(self) -> FrozenSet[int]:
        """All arbitration ids this link accepts frames from."""
        return self._accept_ids

    def _resolve_flow_control_ids(self, policy: FlowControlPolicy) -> Dict[int, int]:
        table: Dict[int, int] = {}
        for rid in sorted(self._accept_ids):
            target: Optional[int] = None
            if policy is not None:
                target = policy.get(rid) if isinstance(policy, Mapping) else policy(rid)
            if target is None:
                if rid == self.rx_id and not self.is_functional:
                    target = self.tx_id
                else:
                    target = physical_request_id(rid)
                    if target is None:
                        log.debug("no physical request id known for responder 0x%X; "
                                  "flow control will use tx id 0x%X", rid, self.tx_id)
                        target = self.tx_id
            table[rid] = int(target)
        return table

    # -- helpers -----------------------------------------------------------------

    def _pad(self, data: bytes) -> bytes:
        if self.cfg.tx_padding is None:
            return data
        if len(data) >= 8:
            return data[:8]
        return data + bytes([self.cfg.tx_padding]) * (8 - len(data))

    def _send_frame(self, data: bytes, arbitration_id: Optional[int] = None) -> None:
        self.transport.send(
            CanFrame(self.tx_id if arbitration_id is None else arbitration_id,
                     self._pad(data), is_extended_id=self.extended_id)
        )

    def _recv_matching(self, timeout: float) -> Optional[CanFrame]:
        """Receive the next frame addressed to us (``accept_ids``), dropping everything else.

        Always polls the transport at least once, so ``timeout=0`` means "take what is
        already buffered" rather than "never look".
        """
        deadline = time.monotonic() + timeout
        while True:
            remaining = max(0.0, deadline - time.monotonic())
            frame = self.transport.recv(remaining)
            if frame is None:
                return None
            if frame.arbitration_id in self._accept_ids:
                return frame
            # Frame for some other module; ignore and keep waiting until the deadline.
            if remaining <= 0:
                return None

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
        if self.is_functional:
            # ISO 15765-4 7.3: functionally addressed requests must fit a single
            # frame; no ECU will flow-control a FF it received on 0x7DF.
            raise TransportError(
                f"ISO-TP payload of {total} bytes cannot be sent to the functional id "
                f"0x{self.tx_id:X}; functional requests must fit one frame (<= {SF_MAX} bytes)"
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
        """Block until a usable FC frame arrives; return (block_size, stmin_seconds).

        Only a Flow Control from the peer's physical id (``rx_id``) counts. One that
        arrives on another accepted id - in particular the functional id a simulated
        ECU also listens on - is ignored exactly as a real ECU ignores FC on 0x7DF.
        """
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
            if frame.arbitration_id != self.rx_id:
                log.debug("ignoring flow control on 0x%X (only accepted from physical id 0x%X)",
                          frame.arbitration_id, self.rx_id)
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

    @property
    def receiving(self) -> FrozenSet[int]:
        """Arbitration ids with a multi-frame transfer currently in progress."""
        return frozenset(self._partials)

    def recv(self, timeout: float) -> Optional[bytes]:
        """Receive one complete payload, or ``None`` after ``timeout`` seconds.

        ``timeout`` bounds the wait for a payload to *start* (its SF or FF). Once a
        First Frame has arrived, each Consecutive Frame gets its own ``n_cr`` window
        regardless of how much of ``timeout`` is left - a receiver polling with a
        short timeout (a simulated ECU, a keepalive-aware client) must not abort a
        transfer that it has already acknowledged with a Flow Control. An N_Cr
        expiry drops that transfer and raises :class:`TransportTimeout`; a sequence
        error drops it and raises :class:`TransportError`.

        Several responders may be transferring at once (functional request); each has
        its own reassembly state and Flow Control target (:attr:`flow_control_ids`),
        and payloads are returned in the order they complete, :attr:`last_rx_id`
        naming the responder. Unfinished transfers carry over to the next call.

        Frames that cannot start a payload are skipped and the wait continues: stray
        Flow Controls, orphan Consecutive Frames (we missed their FF), Single Frames
        with an invalid length nibble, First Frames announcing <= 7 bytes (ISO 15765-2
        requires FF_DL >= 8; a sender must use a SF for that) and First Frames using
        the 32-bit length escape (FF_DL == 0), which no VAG diagnostic payload needs.
        """
        deadline = time.monotonic() + timeout
        first_poll = True
        while True:
            now = time.monotonic()
            if self._partials:
                # Bounded by the nearest N_Cr deadline, not by the caller's timeout.
                wait = max(0.0, min(p.deadline for p in self._partials.values()) - now)
            else:
                wait = deadline - now
                if wait <= 0 and not first_poll:
                    return None
                wait = max(0.0, wait)
            first_poll = False
            frame = self._recv_matching(wait)
            if frame is None:
                if self._partials:
                    self._expire_partials()
                    continue
                return None
            payload = self._process_frame(frame)
            if payload is not None:
                return payload

    def _expire_partials(self) -> None:
        now = time.monotonic()
        expired = [rid for rid, p in self._partials.items() if p.deadline <= now]
        for rid in expired:
            p = self._partials.pop(rid)
            log.warning("ISO-TP N_Cr timeout: dropped %d/%d bytes from 0x%X",
                        len(p.buf), p.total, rid)
        if expired:
            raise TransportTimeout(
                "timed out waiting for ISO-TP consecutive frame (N_Cr) from "
                + ", ".join(f"0x{rid:X}" for rid in expired)
            )

    def _process_frame(self, frame: CanFrame) -> Optional[bytes]:
        """Feed one accepted frame into the receive state machine.

        Returns a completed payload, or ``None`` when more frames are needed.
        """
        if len(frame.data) == 0:
            return None
        pci_type = frame.data[0] >> 4

        if pci_type == PCI_SF:
            length = frame.data[0] & 0x0F
            if length == 0 or length > SF_MAX or length > len(frame.data) - 1:
                log.debug("dropping single frame with invalid length nibble: %s", frame)
                return None
            self.last_rx_id = frame.arbitration_id
            return bytes(frame.data[1:1 + length])

        if pci_type == PCI_FF:
            if len(frame.data) < 2:
                log.debug("dropping truncated first frame: %s", frame)
                return None
            total = ((frame.data[0] & 0x0F) << 8) | frame.data[1]
            if total == 0:
                log.warning("ISO-TP first frame uses the 32-bit length escape (FF_DL > 4095); "
                            "unsupported, frame ignored: %s", frame)
                return None
            if total <= SF_MAX:
                log.debug("dropping first frame announcing %d bytes (FF_DL must be >= 8): %s",
                          total, frame)
                return None
            rid = frame.arbitration_id
            if rid in self._partials:
                log.debug("new first frame from 0x%X while a transfer was in progress; restarting", rid)
            self._partials[rid] = _Reassembly(rid, total, bytes(frame.data[2:2 + FF_FIRST]),
                                              time.monotonic() + self.cfg.n_cr)
            # Clear To Send, addressed to this responder's physical request id.
            self._send_flow_control(rid)
            return None

        if pci_type == PCI_CF:
            partial = self._partials.get(frame.arbitration_id)
            if partial is None:
                # Orphan consecutive frame (we missed the FF) - cannot reassemble.
                log.debug("dropping orphan consecutive frame: %s", frame)
                return None
            return self._feed_consecutive(partial, frame)

        if pci_type == PCI_FC:
            # A lone flow-control frame with no transfer in progress (e.g. the ECU
            # answered a FF we already gave up on). Ignore and keep looking.
            log.debug("dropping stray flow-control frame: %s", frame)
            return None

        log.debug("dropping frame with unknown PCI type 0x%X: %s", pci_type, frame)
        return None

    def _feed_consecutive(self, partial: _Reassembly, frame: CanFrame) -> Optional[bytes]:
        seq = frame.data[0] & 0x0F
        if seq != partial.expected_seq:
            self._partials.pop(partial.arbitration_id, None)
            raise TransportError(
                f"ISO-TP sequence error from 0x{partial.arbitration_id:X}: "
                f"expected {partial.expected_seq}, got {seq}"
            )
        need = partial.total - len(partial.buf)
        partial.buf.extend(frame.data[1:1 + min(7, need)])
        partial.expected_seq = (partial.expected_seq + 1) & 0x0F
        partial.frames_in_block += 1
        partial.deadline = time.monotonic() + self.cfg.n_cr

        if partial.complete:
            self._partials.pop(partial.arbitration_id, None)
            self.last_rx_id = partial.arbitration_id
            return bytes(partial.buf)

        # If we advertised a block size, the sender stops after that many CFs and
        # waits for us to say "go on" with another Flow Control frame.
        block_size = self.cfg.rx_block_size
        if block_size != 0 and partial.frames_in_block >= block_size:
            self._send_flow_control(partial.arbitration_id)
            partial.frames_in_block = 0
        return None

    def _send_flow_control(self, responder_id: int) -> None:
        """Send FC.CTS for ``responder_id`` advertising our receive block size and STmin."""
        fc = bytes([(PCI_FC << 4) | FC_CONTINUE,
                    self.cfg.rx_block_size & 0xFF,
                    encode_stmin(self.cfg.rx_stmin)])
        self._send_frame(fc, self.flow_control_ids.get(responder_id, self.tx_id))

    def flush_rx(self) -> None:
        self._partials.clear()
        self.transport.flush_rx()

    def close(self) -> None:
        """Drop buffered data; close the transport too when ``owns_transport`` is set.

        By default the link does not own the transport's lifecycle (a raw CAN adapter
        may be shared); the caller closes it. A link built on a router endpoint owns
        that endpoint and closing it unsubscribes from the router.
        """
        self._partials.clear()
        try:
            if self.transport.is_open:
                self.flush_rx()
        except TransportError:
            pass
        if self.owns_transport:
            self.transport.close()
