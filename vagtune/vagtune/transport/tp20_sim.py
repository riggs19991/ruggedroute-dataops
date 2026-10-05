"""
VW TP 2.0 - the module (ECU) side, for the simulated vehicle and unit tests.

:class:`Tp20Responder` is the passive state machine of one TP 2.0 module; it reads
frames from any :class:`~vagtune.transport.base.RawCanTransport` (a
:class:`~vagtune.transport.fakebus.FakeCanTransport` or a router endpoint) and
behaves like the real modules in the traces behind :mod:`vagtune.transport.tp20`:

* listens on 0x200 for a 0xC0 whose byte 0 is its logical address; answers
  ``00 D0 <id it will transmit on> <id it assigns the tester> app`` on 0x200+address
  (the tester's requested transmit id - 0x300 - is honoured, the tester's transmit id
  is *chosen by the module*: 0x740 for an engine, 0x7A8 for an EPS...); 0xD8 while a
  channel is already open; 0xD6 for an application type other than 0x01;
* A0 -> A1 (its own parameters, ``A1 0F 8A FF 4A FF`` by default), A3 -> A1,
  A8 -> A8 + close, A4 -> discards the partial message;
* reassembles requests (ACKing after op 0/1 frames, asking for retransmission on a
  sequence error), hands each complete message to ``handler(bytes) -> bytes | None``
  (or a sequence of messages, e.g. ``7F xx 78`` followed by the real answer) and
  segments the response honouring the tester's block size (ACK requested every BS
  frames and on the last) and T3; keeps its own 4-bit sequence counter across
  messages;
* on a wrong ACK retransmits from the acknowledged sequence and, like the real engine
  ECU in the NefMoto trace, gives up with A8 after three retransmissions;
* closes the channel with A8 after ``idle_timeout`` seconds without any frame.

Test hooks (``drop_once``, ``not_ready_count``/``not_ready_release``,
``inject_a3_before_frame``, ``stop_block_after_a3``, ``length_msb``,
``require_valid_rx_id``) make the tester's error paths reproducible; they are off by
default.

:class:`Tp20Node` runs a responder on its own thread as a
:class:`~vagtune.transport.fakebus.SimulatedNode`, so a preset hook can add KWP2000
modules to a :class:`~vagtune.transport.fakebus.SimulatedVehicle`.
"""

from __future__ import annotations

import logging
import time
from typing import Callable, Dict, List, Optional, Sequence, Set, Union

from .base import CanFrame, RawCanTransport, TransportError, TransportNotOpen
from .fakebus import FakeCanBus, SimulatedNode
from .tp20 import (
    APP_DIAGNOSTICS,
    DATA_ACK,
    DATA_LAST,
    DATA_LAST_ACK,
    DATA_MORE,
    DATA_MORE_ACK,
    DATA_NAK,
    OP_BREAK,
    OP_CHANNEL_TEST,
    OP_DISCONNECT,
    OP_PARAMS_REQUEST,
    OP_PARAMS_RESPONSE,
    OP_SETUP_OK,
    OP_SETUP_REQUEST,
    SETUP_ID,
    Tp20Params,
    decode_can_id,
    encode_can_id,
    split_message,
)

log = logging.getLogger(__name__)

__all__ = ["Tp20Responder", "Tp20Node", "DEFAULT_TESTER_RX_ID"]

#: the id a module transmits on when the tester marks its own request invalid.
DEFAULT_TESTER_RX_ID = 0x300

Handler = Union[Callable[[bytes], Union[bytes, Sequence[bytes], None]], object]

_DATA_OPS = (DATA_MORE_ACK, DATA_LAST_ACK, DATA_MORE, DATA_LAST)
_ACK_WANTED_OPS = (DATA_MORE_ACK, DATA_LAST_ACK)
_LAST_OPS = (DATA_LAST_ACK, DATA_LAST)


class Tp20Responder:
    """ECU-side TP 2.0 state machine on top of a raw CAN transport (see module doc).

    ``tester_tx_id`` is the id this module assigns the tester to transmit on (and
    listens on while the channel is open). ``params`` are announced in A1 replies.
    ``ack_timeout`` defaults to the module's own T1. ``idle_timeout`` is the silence
    after which the module drops the channel with A8 (``None`` disables it).
    """

    #: retransmissions after wrong ACKs before the module gives up with A8 (NefMoto trace).
    MAX_RETRANSMISSIONS = 3
    #: wait after a 0x9X we received before retransmitting (same constant as the tester).
    T_WAIT = 0.1
    # UNVERIFIED: the real idle timeout of a module is not measured in any source
    # ("roughly a second" per one author); 3 s is a simulator choice that is lenient
    # enough for tests and still exercises the tester's keepalive.
    DEFAULT_IDLE_TIMEOUT = 3.0

    def __init__(
        self,
        transport: RawCanTransport,
        logical_address: int,
        handler: Handler,
        *,
        tester_tx_id: int,
        params: Optional[Tp20Params] = None,
        idle_timeout: Optional[float] = DEFAULT_IDLE_TIMEOUT,
        ack_timeout: Optional[float] = None,
        require_valid_rx_id: bool = False,
        name: str = "",
    ) -> None:
        if not 0x01 <= int(logical_address) <= 0xEF:
            raise ValueError(f"logical address must be 0x01..0xEF, got {logical_address!r}")
        if not 0 <= int(tester_tx_id) <= 0x7FF:
            raise ValueError(f"tester_tx_id must be an 11-bit id, got {tester_tx_id!r}")
        if callable(handler):
            self._handle: Callable[[bytes], Union[bytes, Sequence[bytes], None]] = handler
        elif hasattr(handler, "handle"):
            self._handle = handler.handle
        else:
            raise TypeError("handler must be callable or expose handle(bytes) -> bytes | None")
        self.transport = transport
        self.logical_address = int(logical_address)
        self.tester_tx_id = int(tester_tx_id)
        self.params = params or Tp20Params()
        self.idle_timeout = idle_timeout
        self.ack_timeout = ack_timeout if ack_timeout is not None else self.params.t1_ack_timeout
        #: MED17.5 quirk: ignore a 0xC0 whose RX field carries the "invalid" marker.
        self.require_valid_rx_id = require_valid_rx_id
        self.name = name or f"tp20-module-{self.logical_address:02X}"

        # -- test hooks ---------------------------------------------------------
        #: incoming data-frame sequence numbers to drop once (simulates lost frames).
        self.drop_once: Set[int] = set()
        #: answer the next N ACK requests with 0x9X ("not ready") instead of 0xBX.
        self.not_ready_count = 0
        #: if set, send the real 0xBX this many seconds after a 0x9X without waiting
        #: for a retransmission (the "keep waiting" behaviour kwp2000-can expects).
        self.not_ready_release: Optional[float] = None
        #: send an A3 before response frame index N (keepalive firing mid-block).
        self.inject_a3_before_frame: Optional[int] = None
        #: after that A3, stop the block and wait for the tester's ACK before resuming
        #: from the acknowledged sequence (the real-module behaviour VWTPLib describes).
        self.stop_block_after_a3 = False
        #: set bit 15 of the length field in response first frames (some modules do).
        self.length_msb = False

        # -- channel state --------------------------------------------------------
        self.channel_open = False
        self.tx_id = DEFAULT_TESTER_RX_ID          # where this module transmits
        self.tester_params: Optional[Tp20Params] = None
        self.tx_seq = 0
        self.rx_seq = 0
        self._rx_buf = bytearray()
        self._rx_expected: Optional[int] = None
        self._last_activity = time.monotonic()
        self._deferred_ack: Optional[tuple] = None  # (due time, next seq)
        self._nak_outstanding = False               # last ACK request got a 0x9X
        self._held_request: Optional[bytes] = None  # completed while not ready
        self.last_close_reason: Optional[str] = None
        self.stats: Dict[str, int] = {
            "setups": 0, "refused": 0, "closes": 0, "requests": 0, "responses": 0,
            "handler_errors": 0, "retransmissions": 0, "sequence_errors": 0,
            "channel_tests": 0, "a1_received": 0, "ignored_setups": 0,
        }

    # -- lifecycle -------------------------------------------------------------------

    def reset(self) -> None:
        """Forget any open channel (used when a node restarts)."""
        self.channel_open = False
        self.tester_params = None
        self.tx_seq = 0
        self.rx_seq = 0
        self._rx_buf = bytearray()
        self._rx_expected = None
        self._deferred_ack = None
        self._nak_outstanding = False
        self._held_request = None
        self._last_activity = time.monotonic()

    def service(self, timeout: float) -> None:
        """Receive at most one frame (waiting up to ``timeout``) and run housekeeping."""
        frame = self.transport.recv(timeout)
        if frame is not None:
            self.handle_frame(frame)
        self._housekeeping()

    def _housekeeping(self) -> None:
        now = time.monotonic()
        if self._deferred_ack is not None and now >= self._deferred_ack[0]:
            _, next_seq = self._deferred_ack
            self._deferred_ack = None
            self._send(bytes([(DATA_ACK << 4) | next_seq]))
            self._nak_outstanding = False
            self._release_held()
        if (self.channel_open and self.idle_timeout is not None
                and now - self._last_activity >= self.idle_timeout):
            log.info("%s: no frame for %.1f s; disconnecting", self.name, self.idle_timeout)
            self._send(bytes([OP_DISCONNECT]))
            self._close("idle timeout")

    def _close(self, reason: str) -> None:
        if self.channel_open:
            self.stats["closes"] += 1
        self.channel_open = False
        self.last_close_reason = reason
        self.tester_params = None
        self._rx_buf = bytearray()
        self._rx_expected = None
        self._deferred_ack = None
        self._nak_outstanding = False
        self._held_request = None
        self.tx_seq = 0
        self.rx_seq = 0
        log.debug("%s: channel closed (%s)", self.name, reason)

    # -- frame output ----------------------------------------------------------------

    def _send(self, data: bytes, arbitration_id: Optional[int] = None) -> None:
        self.transport.send(CanFrame(self.tx_id if arbitration_id is None else arbitration_id, data))

    def _send_a1(self) -> None:
        self._send(self.params.to_bytes(OP_PARAMS_RESPONSE))

    # -- frame input -----------------------------------------------------------------

    def handle_frame(self, frame: CanFrame) -> None:
        """Process one frame from the bus (anything not addressed to us is ignored)."""
        data = frame.data
        if frame.arbitration_id == SETUP_ID:
            if len(data) == 7 and data[0] == self.logical_address and data[1] == OP_SETUP_REQUEST:
                self._on_setup(data)
            return
        if not self.channel_open or frame.arbitration_id != self.tester_tx_id or not data:
            return
        self._last_activity = time.monotonic()
        b0 = data[0]
        op = b0 >> 4
        if op in _DATA_OPS:
            self._on_data(b0, data[1:])
        elif op in (DATA_ACK, DATA_NAK):
            log.debug("%s: stray ACK 0x%02X outside a transmission", self.name, b0)
        elif b0 == OP_PARAMS_REQUEST:
            if len(data) == 6:
                self.tester_params = Tp20Params.from_bytes(data)
                self._send_a1()
            else:
                log.debug("%s: short A0 ignored: %s", self.name, data.hex(" "))
        elif b0 == OP_CHANNEL_TEST:
            self.stats["channel_tests"] += 1
            self._send_a1()
        elif b0 == OP_PARAMS_RESPONSE:
            self.stats["a1_received"] += 1            # the tester answered our A3
        elif b0 == OP_DISCONNECT:
            self._send(bytes([OP_DISCONNECT]))
            self._close("tester sent A8")
        elif b0 == OP_BREAK:
            self._rx_buf = bytearray()
            self._rx_expected = None
        else:
            log.debug("%s: unknown frame ignored: %s", self.name, data.hex(" "))

    def _on_setup(self, data: bytes) -> None:
        reply_id = SETUP_ID + self.logical_address
        rx_id, rx_valid = decode_can_id(data[2], data[3])     # where the tester wants me to listen
        tx_id, tx_valid = decode_can_id(data[4], data[5])     # where the tester wants me to transmit
        app = data[6]
        if self.require_valid_rx_id and not rx_valid:
            # Bosch MED17.5 quirk: the canonical "00 10" request gets no reply at all.
            self.stats["ignored_setups"] += 1
            log.debug("%s: ignoring setup with invalid RX id (module requires a valid one)", self.name)
            return
        my_tx = tx_id if tx_valid else DEFAULT_TESTER_RX_ID
        if self.channel_open:
            self.stats["refused"] += 1
            self._send(bytes([0x00, 0xD8]) + bytes(encode_can_id(self.tx_id, True))
                       + bytes(encode_can_id(self.tester_tx_id, True)) + bytes([app]), reply_id)
            log.info("%s: setup while channel open -> D8", self.name)
            return
        if app != APP_DIAGNOSTICS:
            self.stats["refused"] += 1
            self._send(bytes([0x00, 0xD6]) + bytes(encode_can_id(my_tx, True))
                       + bytes(encode_can_id(self.tester_tx_id, True)) + bytes([app]), reply_id)
            log.info("%s: application type 0x%02X not supported -> D6", self.name, app)
            return
        self.tx_id = my_tx
        self.channel_open = True
        self.tester_params = None
        self.tx_seq = 0
        self.rx_seq = 0
        self._rx_buf = bytearray()
        self._rx_expected = None
        self._deferred_ack = None
        self._last_activity = time.monotonic()
        self.stats["setups"] += 1
        self._send(bytes([0x00, OP_SETUP_OK]) + bytes(encode_can_id(self.tx_id, True))
                   + bytes(encode_can_id(self.tester_tx_id, True)) + bytes([app]), reply_id)
        log.debug("%s: channel open; I transmit on 0x%03X, tester transmits on 0x%03X",
                  self.name, self.tx_id, self.tester_tx_id)

    def _ack_or_nak(self, next_seq: int) -> None:
        """Send the ACK for ``next_seq`` - or a 0x9X while the not-ready hook is armed.

        A request that completed under a NAK is held back and dispatched only once
        the real ACK has gone out (a module that is 'not ready' does not answer yet).
        """
        if self.not_ready_count > 0:
            self.not_ready_count -= 1
            self._nak_outstanding = True
            self._send(bytes([(DATA_NAK << 4) | next_seq]))
            if self.not_ready_release is not None:
                self._deferred_ack = (time.monotonic() + self.not_ready_release, next_seq)
            return
        self._deferred_ack = None
        self._nak_outstanding = False
        self._send(bytes([(DATA_ACK << 4) | next_seq]))
        self._release_held()

    def _release_held(self) -> None:
        held = self._held_request
        self._held_request = None
        if held is not None:
            self._dispatch(held)

    def _on_data(self, pci: int, chunk: bytes) -> None:
        op, seq = pci >> 4, pci & 0xF
        if seq in self.drop_once:
            self.drop_once.discard(seq)
            log.debug("%s: dropping data frame seq %X (test hook)", self.name, seq)
            return
        if seq != self.rx_seq:
            self.stats["sequence_errors"] += 1
            log.debug("%s: data seq %X, expected %X", self.name, seq, self.rx_seq)
            if op in _ACK_WANTED_OPS:
                self._ack_or_nak(self.rx_seq)       # resume from what we have
            return
        self.rx_seq = (seq + 1) & 0xF
        self._rx_buf += chunk
        if op in _ACK_WANTED_OPS:
            self._ack_or_nak(self.rx_seq)
        if self._rx_expected is None and len(self._rx_buf) >= 2:
            self._rx_expected = int.from_bytes(self._rx_buf[:2], "big") & 0x7FFF
        expected = self._rx_expected
        complete = op in _LAST_OPS or (expected is not None and len(self._rx_buf) >= 2 + expected)
        if not complete:
            return
        buf = bytes(self._rx_buf)
        self._rx_buf = bytearray()
        self._rx_expected = None
        if expected is None:
            log.warning("%s: request ended before its length field: %s", self.name, buf.hex(" "))
            return
        request = buf[2:2 + expected]
        if len(request) != expected:
            log.warning("%s: request announced %d bytes, got %d", self.name, expected, len(request))
        if self._nak_outstanding:
            self._held_request = request
        else:
            self._dispatch(request)

    def _dispatch(self, request: bytes) -> None:
        self.stats["requests"] += 1
        try:
            result = self._handle(request)
        except Exception:
            self.stats["handler_errors"] += 1
            log.exception("%s: handler raised on %s; answering generalReject", self.name,
                          request.hex(" "))
            result = bytes([0x7F, request[0], 0x10]) if request else None
        if result is None:
            return
        responses: List[bytes] = [bytes(result)] if isinstance(result, (bytes, bytearray)) \
            else [bytes(r) for r in result]
        for response in responses:
            if not self.channel_open:
                return
            if not response:
                continue
            self.send_message(response)

    # -- sending ---------------------------------------------------------------------

    def send_message(self, payload: bytes) -> bool:
        """Segment and send ``payload`` to the tester; ``False`` if the channel died."""
        if not self.channel_open:
            return False
        chunks = split_message(payload)
        if self.length_msb:
            first = bytearray(chunks[0])
            first[0] |= 0x80
            chunks[0] = bytes(first)
        tester = self.tester_params or Tp20Params()
        bs = tester.effective_block_size
        t3 = max(tester.t3_min_interframe, 0.001)
        n = len(chunks)
        start_seq = self.tx_seq
        i = 0
        block = 0
        retransmissions = 0
        last_tx = 0.0
        while i < n:
            if self.inject_a3_before_frame is not None and i == self.inject_a3_before_frame:
                self.inject_a3_before_frame = None
                self._send(bytes([OP_CHANNEL_TEST]))
                if self.stop_block_after_a3:
                    # The real module did not continue its block after the keepalive;
                    # it resumed only from the sequence the tester acknowledged.
                    pci = self._wait_for_ack(self.ack_timeout * 10)
                    if pci is None:
                        self._send(bytes([OP_DISCONNECT]))
                        self._close("no ACK after mid-block channel test")
                        return False
                    j = self._index_for_seq(start_seq, i, pci & 0xF, n)
                    i = j if j is not None else i
                    block = 0
            seq = (start_seq + i) & 0xF
            last = i == n - 1
            block += 1
            if last:
                op = DATA_LAST_ACK
            elif block >= bs:
                op = DATA_MORE_ACK
            else:
                op = DATA_MORE
            wait = last_tx + t3 - time.monotonic()
            if wait > 0:
                time.sleep(wait)
            self._send(bytes([(op << 4) | seq]) + chunks[i])
            last_tx = time.monotonic()
            self.tx_seq = (seq + 1) & 0xF
            if op not in _ACK_WANTED_OPS:
                i += 1
                continue
            expected = (seq + 1) & 0xF
            block = 0
            pci = self._wait_for_ack(self.ack_timeout)
            if pci is None:
                if not self.channel_open:
                    return False
                retransmissions += 1
                self.stats["retransmissions"] += 1
                if retransmissions > self.MAX_RETRANSMISSIONS:
                    log.info("%s: no ACK after %d retransmissions; disconnecting", self.name,
                             self.MAX_RETRANSMISSIONS)
                    self._send(bytes([OP_DISCONNECT]))
                    self._close("no ACK from tester")
                    return False
                continue                                  # resend the same frame
            kind, value = pci >> 4, pci & 0xF
            if kind == DATA_ACK and value == expected:
                i += 1
                continue
            if kind == DATA_NAK:
                time.sleep(self.T_WAIT)
            retransmissions += 1
            self.stats["retransmissions"] += 1
            if retransmissions > self.MAX_RETRANSMISSIONS:
                log.info("%s: %d wrong ACKs (last 0x%02X); disconnecting like a real ECU",
                         self.name, retransmissions, pci)
                self._send(bytes([OP_DISCONNECT]))
                self._close("tester kept acknowledging the wrong sequence")
                return False
            j = self._index_for_seq(start_seq, i, value, n)
            if j is None:
                continue                                  # unknown sequence: resend this frame
            i = j
        self.stats["responses"] += 1
        return True

    @staticmethod
    def _index_for_seq(start_seq: int, current: int, seq: int, n: int) -> Optional[int]:
        for j in range(min(current, n - 1), max(-1, current - 15), -1):
            if (start_seq + j) & 0xF == seq:
                return j
        return None

    def _wait_for_ack(self, timeout: float) -> Optional[int]:
        """Read frames until an ACK/NAK for us arrives; control frames are serviced inline."""
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return None
            frame = self.transport.recv(remaining)
            if frame is None:
                return None
            data = frame.data
            if frame.arbitration_id == SETUP_ID:
                if len(data) == 7 and data[0] == self.logical_address and data[1] == OP_SETUP_REQUEST:
                    self._on_setup(data)
                continue
            if frame.arbitration_id != self.tester_tx_id or not data:
                continue
            self._last_activity = time.monotonic()
            b0 = data[0]
            op = b0 >> 4
            if op in (DATA_ACK, DATA_NAK):
                return b0
            if b0 == OP_CHANNEL_TEST:
                self.stats["channel_tests"] += 1
                self._send_a1()
            elif b0 == OP_PARAMS_RESPONSE:
                self.stats["a1_received"] += 1
            elif b0 == OP_DISCONNECT:
                self._send(bytes([OP_DISCONNECT]))
                self._close("tester sent A8 mid-transmission")
                return None
            elif b0 == OP_PARAMS_REQUEST and len(data) == 6:
                self.tester_params = Tp20Params.from_bytes(data)
                self._send_a1()
            elif op in _DATA_OPS:
                log.warning("%s: tester sent data while a response is in flight; ignored: %s",
                            self.name, data.hex(" "))
            else:
                log.debug("%s: frame ignored while waiting for ACK: %s", self.name, data.hex(" "))

    def __repr__(self) -> str:
        return (f"<Tp20Responder {self.name} addr=0x{self.logical_address:02X} "
                f"open={self.channel_open} tester_tx=0x{self.tester_tx_id:03X}>")


class Tp20Node(SimulatedNode):
    """A KWP2000-over-TP 2.0 module on a :class:`FakeCanBus`, driven by its own thread.

    ``handler`` is a callable ``bytes -> bytes | Sequence[bytes] | None`` or an object
    with ``handle(bytes)``. Handler exceptions are logged and answered with the KWP
    negative response ``7F <SID> 10`` (generalReject); transport errors are logged and
    the node keeps serving; ``stop()`` joins promptly (the thread polls with a short
    timeout) and detaches the transport, ``start()`` re-attaches it with a clean
    channel state, so a vehicle can be restarted.
    """

    POLL_TIMEOUT = 0.05

    def __init__(
        self,
        bus: FakeCanBus,
        handler: Handler,
        *,
        logical_address: int,
        tester_tx_id: int,
        params: Optional[Tp20Params] = None,
        idle_timeout: Optional[float] = Tp20Responder.DEFAULT_IDLE_TIMEOUT,
        ack_timeout: Optional[float] = None,
        require_valid_rx_id: bool = False,
        name: str = "",
    ) -> None:
        super().__init__(name or f"tp20-{logical_address:02X}")
        self.bus = bus
        self.transport = bus.attach(self.name)
        self.responder = Tp20Responder(
            self.transport, logical_address, handler, tester_tx_id=tester_tx_id, params=params,
            idle_timeout=idle_timeout, ack_timeout=ack_timeout,
            require_valid_rx_id=require_valid_rx_id, name=self.name)
        self.logical_address = int(logical_address)
        self.tester_tx_id = int(tester_tx_id)

    def run(self) -> None:
        while not self.should_stop:
            try:
                self.responder.service(self.POLL_TIMEOUT)
            except TransportNotOpen:
                if not self.should_stop:
                    log.warning("node %s: transport closed underneath it; node is dead until "
                                "start() is called again", self.name)
                break
            except TransportError as exc:
                log.warning("node %s: transport error: %s", self.name, exc)
                continue

    def on_starting(self) -> None:
        if not self.transport.is_open:
            self.transport.open()
        self.transport.flush_rx()
        self.responder.reset()

    def on_stopped(self) -> None:
        self.transport.close()
