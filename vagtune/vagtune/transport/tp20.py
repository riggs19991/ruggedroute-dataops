"""
VW TP 2.0 (Transport Protocol 2.0, SAE J2819) over raw CAN - the tester side.

TP 2.0 is the VAG-proprietary transport that carries KWP2000 (ISO 14230-3) on the
PQ35-era CAN bus: every module of the 2008 R32 (ME7.1.1, DQ250, Haldex, ...) and
several modules of the 2012 Golf TDI (DSG, body/comfort, gateway, ...) speak it.
This module implements the *tester* state machine byte-exact to the facts verified
in the research sheet ``tp20.md`` (sources: jazdw.net/tp20, icanhack.nl, pq-flasher,
PyVCDS, VWTPLib, kwp2000-can, three real-car traces); the ECU side lives in
:mod:`vagtune.transport.tp20_sim`.

Wire protocol (all ids 11-bit, 500 kbit/s)::

    channel setup   tester -> 0x200          : dest C0 rxlo rxhi txlo txhi app
                    module -> 0x200 + dest   : 00   D0 rxlo rxhi txlo txhi app   (D6/D7/D8 = refused)
        rx/tx are *from the recipient's point of view*: in the request bytes 2-3 say
        where the module shall listen (we leave it "invalid" = 0x0010 so the module
        picks) and bytes 4-5 where it shall transmit (our ``tester_rx_id``, 0x300).
        In the reply bytes 2-3 are the id WE receive on (echo of 0x300) and bytes
        4-5 the id WE must transmit on, chosen by the module (0x740 engine, 0x7A8 EPS,
        0x764 Haldex Gen2 ... never assume it). Each id is a little-endian 16-bit
        value whose top nibble is the validity flag (0 valid, 1 invalid).
    parameters      tester -> tx id          : A0 BS T1 T2 T3 T4   (default A0 0F 8A FF 32 FF)
                    module -> rx id          : A1 BS T1 T2 T3 T4   (typically A1 0F 8A FF 4A FF)
        T bytes: bits 7-6 unit (0.1 / 1 / 10 / 100 ms), bits 5-0 multiplier.
        A3 = channel test (peer answers with its A1), A4 = break, A8 = disconnect
        (peer answers A8).
    data            byte 0 = (op << 4) | seq, then up to 7 payload bytes
        op 0 more frames + ACK wanted (block full), 1 last frame + ACK wanted,
        2 more frames, 3 last frame; the first frame of a message carries a 2-byte
        big-endian length of the application message. Each direction keeps a 4-bit
        sequence counter that persists across messages and wraps F -> 0.
        ACK = 0xB0 | ((seq of the acknowledged frame + 1) & 0xF); 0x9X = ACK but not
        ready for the next frame.

A :class:`Tp20Channel` is an :class:`~vagtune.transport.base.IsoTpLink`, so a KWP2000
client sits on it exactly as a UDS client sits on an ISO-TP link. It owns one
:class:`~vagtune.transport.router.RouterEndpoint` (0x200+dest during setup, then the
negotiated module-tx id only - our own tx id is never accepted, because a Tactrix raw
CAN channel hands our own frames back to us) and a daemon service thread that reads
the endpoint, ACKs inline (the module's T1 is 100 ms; the ACK must come from the
thread that sees the frame), answers the module's A3 with our A1, and sends an A3 of
our own when the channel has been idle for ``keepalive_idle`` seconds.

Every module transmits on the id the tester asked for, so two channels on one bus
must use distinct ``tester_rx_id`` values. The module keeps a per-router registry of
the ids in use: a second channel (or a probe) asking for an id that a live channel
holds is refused with :class:`Tp20Error` instead of silently sharing the frames, and
``tester_rx_id=None`` allocates the lowest free id in 0x300..0x30F (what PyVCDS does).

Facts marked ``UNVERIFIED`` below come from the Reported section of the research
sheet; each warns once per process when first relied upon. None of them drives a
write to a module - TP 2.0 is a transport.
"""

from __future__ import annotations

import logging
import threading
import time
import weakref
from collections import deque
from dataclasses import dataclass
from typing import Callable, Deque, Dict, Iterable, List, Optional, Set, Tuple

from .base import CanFrame, IsoTpLink, TransportError, TransportNotOpen, TransportTimeout
from .router import CanRouter, RouterEndpoint

log = logging.getLogger(__name__)

__all__ = [
    "SETUP_ID",
    "APP_DIAGNOSTICS",
    "APP_TYPE_TEXT",
    "OP_SETUP_REQUEST",
    "OP_SETUP_OK",
    "OP_SETUP_REFUSED",
    "REFUSAL_TEXT",
    "OP_PARAMS_REQUEST",
    "OP_PARAMS_RESPONSE",
    "OP_CHANNEL_TEST",
    "OP_BREAK",
    "OP_DISCONNECT",
    "DATA_MORE_ACK",
    "DATA_LAST_ACK",
    "DATA_MORE",
    "DATA_LAST",
    "DATA_ACK",
    "DATA_NAK",
    "MAX_MESSAGE_LENGTH",
    "TESTER_RX_ID_POOL",
    "Tp20Error",
    "Tp20ChannelRefused",
    "Tp20ChannelClosed",
    "Tp20Timeout",
    "Tp20Params",
    "SetupResponse",
    "decode_timing",
    "encode_timing",
    "encode_can_id",
    "decode_can_id",
    "build_setup_request",
    "parse_setup_response",
    "split_message",
    "frame_opcode",
    "tester_rx_ids_in_use",
    "Tp20Channel",
    "Tp20ProbeResult",
    "probe_tp20_addresses",
]

# ---- constants (verified, tp20.md VERIFIED sections 1-4) ----------------------------
SETUP_ID = 0x200                 # setup requests go here; replies on SETUP_ID + dest
APP_DIAGNOSTICS = 0x01           # application type byte: KWP2000 diagnostics
#: Application types of byte 6 of the setup frame (J2819 as transcribed by notyal).
APP_TYPE_TEXT: Dict[int, str] = {
    0x01: "diagnostics (KWP2000)",
    0x10: "infotainment communication",
    0x20: "application protocol",
    0x21: "WFS/WIV immobiliser",
}

OP_SETUP_REQUEST = 0xC0
OP_SETUP_OK = 0xD0
OP_SETUP_REFUSED = (0xD6, 0xD7, 0xD8)
REFUSAL_TEXT: Dict[int, str] = {
    0xD6: "application type not supported",
    0xD7: "application type temporarily not supported",
    0xD8: "temporarily no resources free",
}

OP_PARAMS_REQUEST = 0xA0
OP_PARAMS_RESPONSE = 0xA1
OP_CHANNEL_TEST = 0xA3
OP_BREAK = 0xA4
OP_DISCONNECT = 0xA8

DATA_MORE_ACK = 0x0              # more frames follow, ACK wanted (block size reached)
DATA_LAST_ACK = 0x1              # last frame of the message, ACK wanted
DATA_MORE = 0x2                  # more frames follow, no ACK
DATA_LAST = 0x3                  # last frame, no ACK
DATA_ACK = 0xB                   # ACK, ready for the next frame
DATA_NAK = 0x9                   # ACK, NOT ready for the next frame
_DATA_OPS = (DATA_MORE_ACK, DATA_LAST_ACK, DATA_MORE, DATA_LAST)
_ACK_WANTED_OPS = (DATA_MORE_ACK, DATA_LAST_ACK)
_LAST_OPS = (DATA_LAST_ACK, DATA_LAST)

FRAME_PAYLOAD = 7                # payload bytes per data frame after the PCI byte
MAX_MESSAGE_LENGTH = 0x7FFF      # the 16-bit length has its MSB masked on receive (jazdw)
TIMING_UNITS_MS = (0.1, 1.0, 10.0, 100.0)
#: ids a tester conventionally asks modules to transmit on (jazdw "0x300 to 0x310",
#: PyVCDS allocates 0x300..0x30F round-robin).
TESTER_RX_ID_POOL = range(0x300, 0x310)

_unverified_warned: Set[str] = set()


def _warn_unverified(key: str, message: str) -> None:
    """Emit ``UNVERIFIED mapping: ...`` once per process for ``key``."""
    if key in _unverified_warned:
        return
    _unverified_warned.add(key)
    log.warning("UNVERIFIED mapping: %s", message)


# ============================================================================= errors

class Tp20Error(TransportError):
    """A TP 2.0 protocol failure (refusal, sequence error, peer disconnect...)."""


class Tp20ChannelRefused(Tp20Error):
    """The module answered the channel setup with 0xD6 / 0xD7 / 0xD8.

    ``tester_tx_id`` is the id advertised in bytes 4-5 of the refusal when it was
    marked valid: a module that still holds a channel from an earlier unclosed
    session tells the tester where it listens, so a caller may send A8 there and
    retry (measured on a MED17.5; addresses sheet section D). ``app`` is the
    application type byte echoed in the refusal.
    """

    def __init__(self, code: int, text: str, *, logical_address: int,
                 tester_tx_id: Optional[int] = None, raw: bytes = b"",
                 app: Optional[int] = None) -> None:
        message = f"TP 2.0 channel to 0x{logical_address:02X} refused: 0x{code:02X} {text}"
        if app is not None and code in (0xD6, 0xD7):
            message += f" (application type 0x{app:02X} {APP_TYPE_TEXT.get(app, 'unknown')})"
        super().__init__(message)
        self.code = code
        self.text = text
        self.logical_address = logical_address
        self.tester_tx_id = tester_tx_id
        self.raw = raw
        self.app = app


class Tp20ChannelClosed(Tp20Error):
    """The channel is no longer open (peer sent A8/A4/A0, or keepalive failed)."""


class Tp20Timeout(Tp20Error, TransportTimeout):
    """No setup reply, no parameter reply or no ACK within the deadline."""


# ======================================================================== timing codec

def decode_timing(raw: int) -> float:
    """Decode a T1..T4 byte to **milliseconds**: unit (bits 7-6) x multiplier (bits 5-0).

    0x8A -> 100 ms, 0x4A -> 10 ms, 0x32 -> 5 ms, 0x0A -> 1 ms, 0xFF -> 6300 ms.
    """
    if not 0 <= raw <= 0xFF:
        raise ValueError(f"timing byte out of range: {raw!r}")
    return TIMING_UNITS_MS[(raw >> 6) & 0x3] * (raw & 0x3F)


def encode_timing(milliseconds: float) -> int:
    """Encode ``milliseconds`` with the smallest-error unit/multiplier pair.

    Values above 6300 ms (the maximum, 0xFF) saturate to 0xFF.
    """
    if milliseconds < 0:
        raise ValueError("timing value must be >= 0 ms")
    best: Optional[Tuple[float, int]] = None
    for unit_index, unit in enumerate(TIMING_UNITS_MS):
        n = round(milliseconds / unit)
        if 0 <= n <= 63:
            err = abs(milliseconds - n * unit)
            if best is None or err < best[0]:
                best = (err, (unit_index << 6) | n)
    return 0xFF if best is None else best[1]


@dataclass(frozen=True)
class Tp20Params:
    """Channel parameters as the raw ``BS T1 T2 T3 T4`` bytes of an A0/A1 frame.

    The raw bytes are the canonical representation so that what goes on the wire
    is exactly what the facts say (``A0 0F 8A FF 32 FF`` by default: block size 15,
    T1 100 ms, T2 unused, T3 5 ms, T4 unused - the registry's resolution of conflict
    C7: a MED17.5 degraded at T3 = 1 ms and ran stable at 5 ms, and OpenHaldex quotes
    ``0F 8A FF 32 FF`` from VW captures). The ``*_seconds`` properties decode the
    timing bytes for the state machine.

    Semantics (jazdw): T1 = time to wait for an ACK (should be > 4 x T3), T3 =
    minimum interval between two consecutive frames, T2/T4 always 0xFF.
    """

    block_size: int = 0x0F
    t1: int = 0x8A
    t2: int = 0xFF
    t3: int = 0x32
    t4: int = 0xFF

    def __post_init__(self) -> None:
        for name in ("block_size", "t1", "t2", "t3", "t4"):
            value = getattr(self, name)
            if not 0 <= int(value) <= 0xFF:
                raise ValueError(f"Tp20Params.{name} must be a byte, got {value!r}")

    @classmethod
    def make(cls, *, block_size: int = 0x0F, t1_ms: float = 100.0, t3_ms: float = 5.0) -> "Tp20Params":
        """Build parameters from engineering values (encoded with :func:`encode_timing`)."""
        return cls(block_size=block_size, t1=encode_timing(t1_ms), t3=encode_timing(t3_ms))

    @classmethod
    def from_bytes(cls, data: bytes) -> "Tp20Params":
        """Parse a 6-byte A0 or A1 frame."""
        if len(data) != 6 or data[0] not in (OP_PARAMS_REQUEST, OP_PARAMS_RESPONSE):
            raise Tp20Error(f"not a TP 2.0 parameter frame: {bytes(data).hex(' ')}")
        return cls(block_size=data[1], t1=data[2], t2=data[3], t3=data[4], t4=data[5])

    def to_bytes(self, opcode: int = OP_PARAMS_REQUEST) -> bytes:
        return bytes([opcode, self.block_size, self.t1, self.t2, self.t3, self.t4])

    @property
    def t1_ack_timeout(self) -> float:
        """T1 in seconds."""
        return decode_timing(self.t1) / 1000.0

    @property
    def t3_min_interframe(self) -> float:
        """T3 in seconds."""
        return decode_timing(self.t3) / 1000.0

    @property
    def effective_block_size(self) -> int:
        """Frames a sender may emit before it must ask for an ACK.

        Whether 0x0F means 15 or 16 frames is not settled (tp20.md REPORTED); every
        working implementation asks for the ACK on the 15th frame, which is safe under
        either reading, so values above 15 are clamped to 15 and 0 is treated as 1.
        """
        return max(1, min(int(self.block_size), 0x0F))

    def describe(self) -> str:
        return (f"BS {self.block_size} T1 {decode_timing(self.t1):g} ms "
                f"T3 {decode_timing(self.t3):g} ms")


# ========================================================================= setup codec

def encode_can_id(can_id: int, valid: bool = True) -> Tuple[int, int]:
    """11-bit id -> (low byte, validity nibble | high nibble) as used in setup frames."""
    if not 0 <= can_id <= 0x7FF:
        raise ValueError(f"TP 2.0 setup ids are 11-bit, got 0x{can_id:X}")
    return can_id & 0xFF, ((can_id >> 8) & 0x0F) | (0x00 if valid else 0x10)


def decode_can_id(low: int, high: int) -> Tuple[int, bool]:
    """(low, validity|high) bytes -> (id, valid)."""
    return low | ((high & 0x0F) << 8), (high & 0xF0) == 0


def build_setup_request(dest: int, *, tx_id: int = 0x300, rx_id: Optional[int] = None,
                        app: int = APP_DIAGNOSTICS) -> bytes:
    """The 7-byte 0xC0 frame for ``dest`` (sent on 0x200).

    ``tx_id`` is where the module shall transmit (our receive id, valid). ``rx_id``
    is where the module shall listen: ``None`` writes the canonical "invalid, you
    pick" marker ``00 10`` (what every open implementation and a real VAG tester
    send); a value writes it as valid - the alternate form a Bosch MED17.5 behind a
    J533 gateway required (``01 C0 00 03 00 03 01``; addresses sheet section D).
    ``app`` is the application type (see :data:`APP_TYPE_TEXT`).
    """
    if not 0 <= dest <= 0xFF:
        raise ValueError(f"logical address must be a byte, got {dest!r}")
    if rx_id is None:
        rx_lo, rx_hi = 0x00, 0x10
    else:
        rx_lo, rx_hi = encode_can_id(rx_id, True)
    tx_lo, tx_hi = encode_can_id(tx_id, True)
    return bytes([dest, OP_SETUP_REQUEST, rx_lo, rx_hi, tx_lo, tx_hi, app & 0xFF])


@dataclass(frozen=True)
class SetupResponse:
    """A parsed 7-byte setup reply (``00 D0 rxlo rxhi txlo txhi app`` or a refusal).

    ``rx_id``/``tx_id`` are from the *tester's* point of view: ``rx_id`` is the id the
    module will transmit on (we receive there), ``tx_id`` the id the module listens on
    (we transmit there).
    """

    opcode: int
    rx_id: int
    rx_valid: bool
    tx_id: int
    tx_valid: bool
    app: int
    raw: bytes

    @property
    def ok(self) -> bool:
        return self.opcode == OP_SETUP_OK


def parse_setup_response(data: bytes) -> SetupResponse:
    """Parse a 7-byte setup reply; raises :class:`Tp20Error` for other lengths.

    A 3-byte ``xx D0 A1`` reply is the older TP 1.6 (EDC15 era) and is reported as
    such so an autoscan never mistakes it for TP 2.0.
    """
    data = bytes(data)
    if len(data) == 3 and data[1] == OP_SETUP_OK:
        raise Tp20Error(f"TP 1.6 setup reply {data.hex(' ')} (fixed-parameter transport, not TP 2.0)")
    if len(data) != 7:
        raise Tp20Error(f"setup reply must be 7 bytes, got {data.hex(' ')}")
    rx_id, rx_valid = decode_can_id(data[2], data[3])
    tx_id, tx_valid = decode_can_id(data[4], data[5])
    return SetupResponse(opcode=data[1], rx_id=rx_id, rx_valid=rx_valid, tx_id=tx_id,
                         tx_valid=tx_valid, app=data[6], raw=data)


def split_message(payload: bytes) -> List[bytes]:
    """Prefix the 2-byte big-endian length and cut into 7-byte chunks (one per frame)."""
    if not payload:
        raise ValueError("TP 2.0 message must be at least one byte")
    if len(payload) > MAX_MESSAGE_LENGTH:
        raise Tp20Error(f"TP 2.0 message of {len(payload)} bytes exceeds {MAX_MESSAGE_LENGTH}")
    buf = len(payload).to_bytes(2, "big") + bytes(payload)
    return [buf[i:i + FRAME_PAYLOAD] for i in range(0, len(buf), FRAME_PAYLOAD)]


def frame_opcode(index: int, count: int, block_size: int) -> int:
    """The data opcode of frame ``index`` of a ``count``-frame message.

    The opcode is a function of the frame's position only (JAZDW-SRC ``i % bs == bs-1``,
    VWTPLib ``(current_frame + 1) % bs == 0``), so a retransmitted frame carries exactly
    the PCI it carried the first time: the last frame always asks for an ACK (op 1),
    every ``block_size``-th frame asks for an ACK and announces more (op 0), everything
    else is a plain consecutive frame (op 2).
    """
    if index == count - 1:
        return DATA_LAST_ACK
    if (index + 1) % max(1, block_size) == 0:
        return DATA_MORE_ACK
    return DATA_MORE


# ================================================================ tester-id registry

_claims_lock = threading.Lock()
# router -> {tester rx id: owner}; the router key is weak so a closed bus frees its table.
_claims: "weakref.WeakKeyDictionary[CanRouter, Dict[int, object]]" = weakref.WeakKeyDictionary()


def _owner_name(owner: object) -> str:
    return str(getattr(owner, "name", None) or repr(owner))


def _claim_tester_rx_id(router: CanRouter, wanted: Optional[int], owner: object) -> int:
    """Reserve ``wanted`` (or the lowest free id of :data:`TESTER_RX_ID_POOL`) on ``router``.

    Raises :class:`Tp20Error` when another live channel or probe already holds the id:
    every module transmits on the id the tester asked for, so two channels sharing an
    id would interleave on one endpoint and ACK each other's frames.
    """
    with _claims_lock:
        table = _claims.get(router)
        if table is None:
            table = {}
            _claims[router] = table
        if wanted is None:
            for candidate in TESTER_RX_ID_POOL:
                if candidate not in table:
                    wanted = candidate
                    break
            else:
                raise Tp20Error(
                    f"all tester receive ids 0x{TESTER_RX_ID_POOL.start:X}..0x{TESTER_RX_ID_POOL[-1]:X} "
                    f"are in use on this router by {', '.join(_owner_name(o) for o in table.values())}")
        elif wanted in table and table[wanted] is not owner:
            raise Tp20Error(
                f"tester_rx_id 0x{wanted:X} is already used by {_owner_name(table[wanted])} on this "
                f"router; pass a distinct tester_rx_id (0x{wanted + 1:X}, ...) or tester_rx_id=None "
                "to allocate a free one")
        table[wanted] = owner
        return wanted


def _release_tester_rx_id(router: CanRouter, rx_id: int, owner: object) -> None:
    with _claims_lock:
        table = _claims.get(router)
        if table is not None and table.get(rx_id) is owner:
            del table[rx_id]


def tester_rx_ids_in_use(router: CanRouter) -> Dict[int, str]:
    """The tester receive ids currently claimed on ``router`` -> owner name (for diagnostics)."""
    with _claims_lock:
        table = _claims.get(router) or {}
        return {rx_id: _owner_name(owner) for rx_id, owner in sorted(table.items())}


# ============================================================================ channel

class Tp20Channel(IsoTpLink):
    """A KWP2000 payload link over TP 2.0 to one module (tester side).

    Lifecycle: ``connect()`` (0xC0 -> 0xD0 -> A0 -> A1), then ``send()``/``recv()``;
    ``disconnect()`` sends A8; ``close()`` stops the service thread, disconnects
    (best effort) and unsubscribes the router endpoint. ``send()``/``recv()`` connect
    on first use when ``auto_connect`` is true, so ``KwpClient(ctx.tp20_channel(0x01))``
    works unchanged. ``connect()`` is serialised by a lock, so two threads that
    auto-connect the same channel run one handshake, not two.

    Threads: the caller's thread segments and sends messages (one at a time, under
    ``_send_lock``) and waits for ACKs; the daemon service thread reads the endpoint,
    reassembles incoming messages into an inbox, sends ACKs/A1 replies inline, and
    sends the A3 keepalive when idle. ``recv()`` only waits on the inbox, so a short
    polling timeout can never abort a message the service thread is mid-way through.

    Receiver policy (TP 2.0 data frames carry no first/consecutive marker, so the
    receiver must never lose its place in the module's stream): a message whose
    announced length is not met, or which announces length 0, is refused (logged,
    counted in ``stats["malformed_messages"]``, still ACKed so the module's counter
    stays in step) rather than delivered truncated; ``flush_rx()`` during a message
    keeps the reassembly running on the original length field and discards the
    message once it is complete; a message the module stops mid-way is prompted
    once after T1 of silence (VWTPLib recovery) and abandoned after
    ``PARTIAL_TIMEOUT_FACTOR`` x T1, so the module's next message cannot be glued to
    it. ``recv()`` therefore never returns an empty payload.

    Open several channels at once with distinct ``tester_rx_id`` values (0x300,
    0x301, ...) or ``tester_rx_id=None`` (lowest free id): every module transmits on
    the id it was asked to, and a second channel asking for an id a live channel
    holds on the same router is refused by :meth:`connect`.
    """

    #: seconds to wait after a 0x9X "not ready" before retransmitting.
    # UNVERIFIED: T_WAIT = 100 ms and the 5-NAK limit are the values two independent
    # implementations (SpeckMobil T_wait/MNTB, VWTPLib T_WAIT/NAK_counter) chose; the
    # sheet lists the spec origin of the numbers as Reported.
    T_WAIT = 0.1
    MAX_NAK = 5
    #: retransmissions (wrong-sequence ACKs) tolerated per message before giving up.
    MAX_RETRANSMIT = 5
    #: consecutive channel tests without an A1 before the channel counts as dead.
    # UNVERIFIED: 5 is SpeckMobil's MNCT ("Maximum Repeats of connection test"); no
    # trace shows a module's real tolerance.
    KEEPALIVE_MAX_MISSES = 5
    #: a partially received message is abandoned after this many T1 of silence
    #: (one stall prompt goes out at 1 x T1). A tester-side bound on our own buffer,
    #: not a claim about module behaviour: a module that is still sending keeps its
    #: frames T3 (<= 10 ms observed) apart and answers a prompt within T1.
    PARTIAL_TIMEOUT_FACTOR = 3
    DEFAULT_KEEPALIVE_IDLE = 0.5
    DISCONNECT_TIMEOUT = 0.5
    POLL_INTERVAL = 0.02

    def __init__(
        self,
        router: CanRouter,
        logical_address: int,
        *,
        tester_rx_id: Optional[int] = 0x300,
        params: Optional[Tp20Params] = None,
        keepalive: bool = True,
        setup_timeout: float = 0.3,
        setup_retries: int = 3,
        auto_connect: bool = True,
        keepalive_idle: float = DEFAULT_KEEPALIVE_IDLE,
        name: str = "",
    ) -> None:
        """
        ``logical_address`` is the TP 2.0 destination byte (0x01 engine, 0x09 EPS,
        0x0A Haldex Gen2, 0x1F gateway...), *not* the VCDS address word.
        ``tester_rx_id`` is the id we ask the module to transmit on; ``None`` takes
        the lowest id of 0x300..0x30F not held by another channel on this router at
        :meth:`connect` time. ``params`` are the A0 parameters we announce.
        ``setup_timeout``/``setup_retries`` bound the 0xC0 and A0 exchanges; a module
        silent on every retry of the standard setup form is tried again with the
        alternate "both ids valid" form before :class:`Tp20Timeout` is raised.
        """
        if not 0x01 <= int(logical_address) <= 0xEF:
            raise ValueError(f"TP 2.0 logical address must be 0x01..0xEF (0x200..0x2EF reply ids), "
                             f"got {logical_address!r}")
        if tester_rx_id is not None and not 0 <= int(tester_rx_id) <= 0x7FF:
            raise ValueError(f"tester_rx_id must be an 11-bit id or None, got {tester_rx_id!r}")
        if setup_retries < 1:
            raise ValueError("setup_retries must be >= 1")
        super().__init__(tx_id=0, rx_id=0 if tester_rx_id is None else int(tester_rx_id))
        self.router = router
        self.logical_address = int(logical_address)
        #: the id requested at construction (``None`` = allocate on connect); the
        #: effective id is ``rx_id`` once connected.
        self.tester_rx_id: Optional[int] = None if tester_rx_id is None else int(tester_rx_id)
        self.params = params or Tp20Params()
        if not 1 <= self.params.block_size <= 0x0F:
            raise ValueError("our block size must be 1..15 (0x0F)")
        self.keepalive = keepalive
        self.keepalive_idle = keepalive_idle
        self.setup_timeout = setup_timeout
        self.setup_retries = setup_retries
        self.auto_connect = auto_connect
        self.name = name or f"tp20-{self.logical_address:02X}"

        #: parameters the module announced in its A1 (None until connected).
        self.peer_params: Optional[Tp20Params] = None
        #: "standard" or "alternate": which 0xC0 form the module answered.
        self.setup_form: Optional[str] = None
        self.setup_response: Optional[SetupResponse] = None
        self.stats: Dict[str, int] = {
            "tx_messages": 0, "rx_messages": 0, "tx_frames": 0, "rx_frames": 0,
            "retransmissions": 0, "naks": 0, "keepalives": 0, "keepalive_misses": 0,
            "inline_a3": 0, "stall_prompts": 0, "sequence_errors": 0,
            "malformed_messages": 0, "discarded_messages": 0, "abandoned_partials": 0,
        }

        self._endpoint: Optional[RouterEndpoint] = None
        self._cond = threading.Condition()          # guards inbox/acks/rx state/flags
        self._connect_lock = threading.RLock()      # one handshake / teardown at a time
        self._send_lock = threading.Lock()          # one message (or keepalive) at a time
        self._tx_lock = threading.Lock()            # frame writes + _last_tx
        self._inbox: Deque[bytes] = deque()
        self._acks: Deque[int] = deque()
        self._a1_count = 0
        self._connected = False
        self._closed = False
        self._peer_closed_reason: Optional[str] = None
        self._disconnect_sent = False
        self._a8_received = False
        self._tx_seq = 0
        self._rx_seq = 0
        self._rx_buf = bytearray()
        self._rx_expected: Optional[int] = None
        self._rx_prompted = False
        self._rx_discard = False                    # drop the message in progress when complete
        self._rx_last_data = 0.0                    # monotonic time of the last data frame
        self._last_tx = 0.0
        self._last_rx = 0.0
        self._a3_deadline: Optional[float] = None
        self._keepalive_misses = 0
        self._thread: Optional[threading.Thread] = None
        self._stop_event = threading.Event()

    # -- introspection -------------------------------------------------------------

    @property
    def connected(self) -> bool:
        return self._connected

    @property
    def ecu_tx_id(self) -> int:
        """The id the module transmits on (= our receive id; 0 before an auto-allocated connect)."""
        return self.rx_id

    @property
    def ecu_rx_id(self) -> int:
        """The id the module listens on (= our transmit id, assigned by the module)."""
        return self.tx_id

    @property
    def t1(self) -> float:
        """Seconds we wait for the module's ACK (the module's announced T1)."""
        p = self.peer_params or self.params
        return p.t1_ack_timeout

    @property
    def t3(self) -> float:
        """Minimum gap in seconds between our consecutive frames (peer T3, >= 1 ms)."""
        p = self.peer_params or self.params
        return max(p.t3_min_interframe, 0.001)

    @property
    def block_size(self) -> int:
        """Frames we send before asking for an ACK (the module's announced BS, <= 15)."""
        p = self.peer_params or self.params
        return p.effective_block_size

    def __repr__(self) -> str:
        state = "closed" if self._closed else ("connected" if self._connected else "idle")
        return (f"<Tp20Channel 0x{self.logical_address:02X} {state} rx=0x{self.rx_id:X} "
                f"tx=0x{self.tx_id:X}>")

    # -- connect -------------------------------------------------------------------

    def connect(self) -> None:
        """Open the channel: 0xC0 setup, 0xD0 reply, A0/A1 parameters, start service thread.

        Raises :class:`Tp20ChannelRefused` on D6/D7/D8, :class:`Tp20Timeout` when the
        module stays silent on every retry of both setup forms (or never answers the
        A0), :class:`Tp20Error` on a malformed reply (including a TP 1.6 reply) or
        when the tester receive id is held by another channel on this router.
        Once a module has answered 0xD0 it holds a channel, so any failure after that
        point (bad ids, no A1) sends it an A8 on the id it assigned before raising -
        otherwise it would answer every retry with 0xD8 until its idle timeout.
        Reconnecting an already connected channel is a no-op; a channel the peer
        closed can be reconnected.
        """
        with self._connect_lock:
            if self._closed:
                raise TransportNotOpen(f"{self.name}: channel is closed")
            if self._connected:
                return
            self._stop_service_thread()
            rx_id = _claim_tester_rx_id(self.router, self.tester_rx_id, self)
            try:
                self._connect_locked(rx_id)
            except BaseException:
                _release_tester_rx_id(self.router, rx_id, self)
                raise

    def _connect_locked(self, rx_id: int) -> None:
        reply_id = SETUP_ID + self.logical_address
        if self._endpoint is None:
            self._endpoint = self.router.endpoint({reply_id}, name=self.name)
        else:
            self._endpoint.set_accept_ids({reply_id})
        ep = self._endpoint
        ep.flush_rx()
        self._reset_state()
        self.rx_id = rx_id

        form, resp = self._setup_handshake(ep, reply_id, rx_id)
        try:
            if not resp.rx_valid or not resp.tx_valid:
                raise Tp20Error(f"{self.name}: setup reply marks an id invalid: {resp.raw.hex(' ')}")
            if resp.rx_id != rx_id:
                raise Tp20Error(f"{self.name}: module wants to transmit on 0x{resp.rx_id:X}, "
                                f"we asked for 0x{rx_id:X} ({resp.raw.hex(' ')})")
            if resp.tx_id == rx_id:
                raise Tp20Error(f"{self.name}: module assigned our own receive id 0x{resp.tx_id:X} "
                                f"as transmit id ({resp.raw.hex(' ')})")
            self.setup_form = form
            self.setup_response = resp
            self.tx_id = resp.tx_id
            log.info("%s: channel open via %s setup; we transmit on 0x%03X, receive on 0x%03X",
                     self.name, form, self.tx_id, self.rx_id)

            # From here on only the module's transmit id matters; our own tx id must never
            # be accepted (Tactrix raw CAN echoes our frames back, j2534_can.md section 2.5).
            ep.set_accept_ids({self.rx_id})
            ep.flush_rx()
            self.peer_params = self._params_handshake(ep)
        except TransportError:
            self._release_half_open(ep, resp)
            raise
        log.info("%s: module parameters %s (ours %s)", self.name,
                 self.peer_params.describe(), self.params.describe())
        # UNVERIFIED: whether the module's T1/T3 describe *its* timing or the timing it
        # expects from us is not stated by any source; using them as our ACK timeout and
        # our minimum inter-frame gap is what VWTPLib/SpeckMobil do and is the safe reading.
        _warn_unverified(
            "tp20-peer-timing",
            f"TP 2.0 uses the module's announced T1 ({decode_timing(self.peer_params.t1):g} ms) as "
            f"our ACK timeout and its T3 ({decode_timing(self.peer_params.t3):g} ms) as our minimum "
            "inter-frame gap; the direction of T1/T3 is not confirmed on the target cars")

        with self._cond:
            self._tx_seq = 0
            self._rx_seq = 0
            self._connected = True
            self._peer_closed_reason = None
            now = time.monotonic()
            self._last_rx = now
            self._last_tx = now
        self._start_service_thread()

    def _release_half_open(self, ep: RouterEndpoint, resp: SetupResponse) -> None:
        """A8 the channel a module opened with 0xD0 when the rest of the handshake failed.

        Pitfall 9 of the sheet: "always send A8 before re-opening"; a module holding a
        half-open channel answers 0xD8 to the next setup until its idle timeout.
        """
        if not resp.tx_valid:
            log.warning("%s: cannot release the half-open channel: the module named an invalid "
                        "transmit id (%s)", self.name, resp.raw.hex(" "))
            return
        listen_id = resp.rx_id if resp.rx_valid else self.rx_id
        try:
            ep.set_accept_ids({listen_id})
            self._send_frame(resp.tx_id, bytes([OP_DISCONNECT]))
        except TransportError as exc:
            log.warning("%s: could not send A8 to release the half-open channel: %s", self.name, exc)
            return
        confirmed = False
        deadline = time.monotonic() + self.DISCONNECT_TIMEOUT
        while True:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                break
            try:
                frame = ep.recv(remaining)
            except TransportError:
                break
            if frame is None:
                break
            if frame.arbitration_id == listen_id and frame.data[:1] == bytes([OP_DISCONNECT]):
                confirmed = True
                break
        log.info("%s: released the half-open channel with A8 on 0x%03X (%s)", self.name,
                 resp.tx_id, "module confirmed" if confirmed else "no confirmation")

    def _reset_state(self) -> None:
        with self._cond:
            self._inbox.clear()
            self._acks.clear()
            self._rx_buf = bytearray()
            self._rx_expected = None
            self._rx_prompted = False
            self._rx_discard = False
            self._connected = False
            self._peer_closed_reason = None
            self._disconnect_sent = False
            self._a8_received = False
            self._a3_deadline = None
            self._keepalive_misses = 0
            self.peer_params = None
            self.setup_form = None
            self.setup_response = None

    def _setup_handshake(self, ep: RouterEndpoint, reply_id: int,
                         rx_id: int) -> Tuple[str, SetupResponse]:
        forms = (
            ("standard", build_setup_request(self.logical_address, tx_id=rx_id)),
            ("alternate", build_setup_request(self.logical_address, tx_id=rx_id, rx_id=rx_id)),
        )
        for form, request in forms:
            for attempt in range(1, self.setup_retries + 1):
                ep.flush_rx()
                self._send_frame(SETUP_ID, request)
                log.debug("%s: setup (%s form, try %d/%d): %s", self.name, form, attempt,
                          self.setup_retries, request.hex(" "))
                deadline = time.monotonic() + self.setup_timeout
                while True:
                    remaining = deadline - time.monotonic()
                    if remaining <= 0:
                        break
                    frame = ep.recv(remaining)
                    if frame is None:
                        break
                    if frame.arbitration_id != reply_id:
                        continue
                    data = frame.data
                    if len(data) == 3 and data[1] == OP_SETUP_OK:
                        raise Tp20Error(
                            f"{self.name}: module answered with a TP 1.6 setup reply "
                            f"{data.hex(' ')}; TP 1.6 (fixed parameters, EDC15 era) is not TP 2.0")
                    if len(data) != 7:
                        log.debug("%s: ignoring %d-byte frame on 0x%03X during setup: %s",
                                  self.name, len(data), reply_id, data.hex(" "))
                        continue
                    opcode = data[1]
                    if opcode == OP_SETUP_OK:
                        resp = parse_setup_response(data)
                        if data[0] != 0x00:
                            log.debug("%s: setup reply byte 0 is 0x%02X (expected 0x00 = tester)",
                                      self.name, data[0])
                        return form, resp
                    if opcode in OP_SETUP_REFUSED:
                        resp = parse_setup_response(data)
                        raise Tp20ChannelRefused(
                            opcode, REFUSAL_TEXT[opcode], logical_address=self.logical_address,
                            tester_tx_id=resp.tx_id if resp.tx_valid else None, raw=data,
                            app=resp.app)
                    log.debug("%s: unexpected opcode 0x%02X on 0x%03X during setup: %s",
                              self.name, opcode, reply_id, data.hex(" "))
                log.debug("%s: no setup reply within %.3f s", self.name, self.setup_timeout)
            log.info("%s: module 0x%02X silent on %d x %s setup form", self.name,
                     self.logical_address, self.setup_retries, form)
        raise Tp20Timeout(
            f"{self.name}: no reply on 0x{reply_id:03X} from logical address "
            f"0x{self.logical_address:02X} after {self.setup_retries} tries of each setup form")

    def _params_handshake(self, ep: RouterEndpoint) -> Tp20Params:
        request = self.params.to_bytes(OP_PARAMS_REQUEST)
        for attempt in range(1, self.setup_retries + 1):
            self._send_frame(self.tx_id, request)
            log.debug("%s: parameters (try %d): %s", self.name, attempt, request.hex(" "))
            deadline = time.monotonic() + self.setup_timeout
            while True:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    break
                frame = ep.recv(remaining)
                if frame is None:
                    break
                if frame.arbitration_id != self.rx_id or not frame.data:
                    continue
                data = frame.data
                if data[0] == OP_PARAMS_RESPONSE and len(data) == 6:
                    return Tp20Params.from_bytes(data)
                if data[0] in (OP_DISCONNECT, OP_BREAK):
                    raise Tp20ChannelClosed(f"{self.name}: module sent 0x{data[0]:02X} instead of A1")
                log.debug("%s: ignoring frame during parameter handshake: %s", self.name, data.hex(" "))
        raise Tp20Timeout(f"{self.name}: no A1 parameter reply on 0x{self.rx_id:03X} after "
                          f"{self.setup_retries} A0 requests")

    # -- frame output --------------------------------------------------------------

    def _send_frame(self, arbitration_id: int, data: bytes) -> None:
        ep = self._endpoint
        if ep is None:
            raise TransportNotOpen(f"{self.name}: no endpoint")
        with self._tx_lock:
            ep.send(CanFrame(arbitration_id, data))
            self._last_tx = time.monotonic()
            self.stats["tx_frames"] += 1

    def _send_data_frame(self, data: bytes) -> None:
        """Send one data frame honouring the peer's T3 gap since our last frame."""
        gap = self.t3
        while True:
            wait = self._last_tx + gap - time.monotonic()
            if wait <= 0:
                break
            time.sleep(wait)
        self._send_frame(self.tx_id, data)

    def _send_ack(self, next_seq: int) -> None:
        self._send_frame(self.tx_id, bytes([(DATA_ACK << 4) | (next_seq & 0xF)]))

    # -- send ------------------------------------------------------------------------

    def _ensure_connected(self) -> None:
        with self._connect_lock:
            if self._closed:
                raise TransportNotOpen(f"{self.name}: channel is closed")
            if self._connected:
                return
            if self._peer_closed_reason is not None:
                raise Tp20ChannelClosed(f"{self.name}: channel closed ({self._peer_closed_reason}); "
                                        "call connect() to reopen")
            if not self.auto_connect:
                raise Tp20Error(f"{self.name}: channel not connected; call connect()")
            self.connect()

    def send(self, payload: bytes) -> None:
        """Send one application message (segmented, ACK-paced, T3-spaced).

        An ACK is requested on the last frame and on every block-size boundary
        (:func:`frame_opcode`). A 0x9X "not ready" waits ``T_WAIT`` (still listening
        for the real ACK), then retransmits: the same frame again when the NAK
        acknowledged everything sent (SpeckMobil ``txSeq--``: the block-end frame goes
        out again with its ACK request and the tester waits again), or from the
        sequence the NAK carried (VWTPLib). An ACK with an unexpected sequence
        retransmits from that sequence; no ACK within the peer's T1 raises
        :class:`Tp20Timeout`; a peer disconnect raises :class:`Tp20ChannelClosed`.
        """
        chunks = split_message(payload)
        self._ensure_connected()
        with self._send_lock:
            with self._cond:
                self._acks.clear()
            start_seq = self._tx_seq
            n = len(chunks)
            bs = self.block_size
            i = 0
            naks = 0
            retransmissions = 0
            while i < n:
                if not self._connected:
                    raise Tp20ChannelClosed(f"{self.name}: channel closed ({self._peer_closed_reason})")
                seq = (start_seq + i) & 0xF
                op = frame_opcode(i, n, bs)
                self._send_data_frame(bytes([(op << 4) | seq]) + chunks[i])
                self._tx_seq = (seq + 1) & 0xF
                if op not in _ACK_WANTED_OPS:
                    i += 1
                    continue
                expected = (seq + 1) & 0xF
                pci = self._wait_ack(self.t1)
                if pci is None:
                    raise Tp20Timeout(f"{self.name}: no ACK for frame seq {seq:X} within "
                                      f"{self.t1 * 1000:.0f} ms (T1)")
                while True:
                    kind, value = pci >> 4, pci & 0xF
                    if kind == DATA_ACK:
                        if value == expected:
                            i += 1
                            break
                        retransmissions += 1
                        self.stats["retransmissions"] += 1
                        if retransmissions > self.MAX_RETRANSMIT:
                            raise Tp20Error(f"{self.name}: module keeps acknowledging the wrong "
                                            f"sequence (0x{pci:02X}, expected B{expected:X})")
                        j = self._index_for_seq(start_seq, i, value)
                        if j is None:
                            raise Tp20Error(f"{self.name}: ACK 0x{pci:02X} names a sequence not in "
                                            f"this message (expected B{expected:X})")
                        log.warning("%s: ACK 0x%02X (expected B%X); retransmitting from seq %X",
                                    self.name, pci, expected, value)
                        i = j
                        break
                    # 0x9X: acknowledged but not ready for the next frame.
                    _warn_unverified(
                        "tp20-not-ready",
                        f"TP 2.0 handles 0x9X (ACK not ready) by waiting {self.T_WAIT * 1000:.0f} ms "
                        f"and retransmitting from the NAK's sequence, giving up after {self.MAX_NAK}; "
                        "these values come from two implementations, not from a trace")
                    naks += 1
                    self.stats["naks"] += 1
                    if naks > self.MAX_NAK:
                        raise Tp20Error(f"{self.name}: module not ready after {self.MAX_NAK} "
                                        f"attempts (last 0x{pci:02X})")
                    log.info("%s: module not ready (0x%02X); waiting %.0f ms", self.name, pci,
                             self.T_WAIT * 1000)
                    later = self._wait_ack(self.T_WAIT)
                    if later is not None:
                        pci = later
                        continue
                    if value != expected:
                        j = self._index_for_seq(start_seq, i, value)
                        if j is not None:
                            i = j
                    # value == expected: everything is acknowledged but the module is not
                    # ready; re-send frame i unchanged (same PCI, ACK still requested) and
                    # wait for the B when it is ready.
                    self.stats["retransmissions"] += 1
                    break
            self.stats["tx_messages"] += 1

    @staticmethod
    def _index_for_seq(start_seq: int, current: int, seq: int) -> Optional[int]:
        """Index of the most recent frame (within the last 15 up to ``current``) whose
        sequence number is ``seq``; ``None`` if no such frame was sent."""
        for j in range(current, max(-1, current - 15), -1):
            if (start_seq + j) & 0xF == seq:
                return j
        return None

    def _wait_ack(self, timeout: float) -> Optional[int]:
        """Return the next ACK/NAK PCI byte, ``None`` on timeout; raise if the peer closed."""
        with self._cond:
            if not self._acks and self._connected:
                self._cond.wait_for(lambda: bool(self._acks) or not self._connected, timeout=timeout)
            if self._acks:
                return self._acks.popleft()
            if not self._connected:
                raise Tp20ChannelClosed(f"{self.name}: channel closed ({self._peer_closed_reason})")
            return None

    # -- receive -------------------------------------------------------------------

    def recv(self, timeout: float) -> Optional[bytes]:
        """Return the next complete application message, or ``None`` after ``timeout``.

        Messages are reassembled (and ACKed) by the service thread as frames arrive,
        so ``timeout`` only bounds this wait; a partially received message is never
        dropped by a short poll, and a returned message is never empty or shorter
        than its announced length (such frames are refused, see the class doc).
        Raises :class:`Tp20ChannelClosed` once the inbox is empty and the peer closed
        the channel, :class:`TransportNotOpen` after :meth:`close`.
        """
        with self._cond:
            if self._inbox:
                return self._inbox.popleft()
        self._ensure_connected()
        deadline = time.monotonic() + max(0.0, timeout)
        with self._cond:
            while True:
                if self._inbox:
                    return self._inbox.popleft()
                if self._closed:
                    raise TransportNotOpen(f"{self.name}: channel is closed")
                if not self._connected:
                    raise Tp20ChannelClosed(f"{self.name}: channel closed ({self._peer_closed_reason})")
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None
                self._cond.wait(remaining)

    def flush_rx(self) -> None:
        """Drop queued messages; a message in progress is discarded once it completes.

        The reassembly keeps running on the length field of the message's first
        frame (TP 2.0 frames carry no first/consecutive marker, so clearing the buffer
        mid-message would turn the rest of that message into phantom messages). A
        partial that has already gone silent for T1 is dropped outright, because the
        next data frame then starts a new message.
        """
        with self._cond:
            self._inbox.clear()
            if not self._rx_buf:
                return
            if time.monotonic() - self._rx_last_data < self.t1:
                self._rx_discard = True
                log.debug("%s: flush during a message; discarding it when complete", self.name)
            else:
                self._abandon_partial_locked("flushed")

    def _abandon_partial_locked(self, why: str) -> None:
        """Drop a partially received message (caller holds ``_cond``)."""
        buf = bytes(self._rx_buf)
        self._rx_buf = bytearray()
        self._rx_expected = None
        self._rx_prompted = False
        self._rx_discard = False
        self.stats["abandoned_partials"] += 1
        log.warning("%s: partial message abandoned (%s): %s", self.name, why, buf.hex(" "))

    # -- service thread --------------------------------------------------------------

    def _start_service_thread(self) -> None:
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._service_loop, name=f"{self.name}-service",
                                        daemon=True)
        self._thread.start()

    def _stop_service_thread(self) -> None:
        thread = self._thread
        self._stop_event.set()
        if thread is not None and thread.is_alive() and thread is not threading.current_thread():
            thread.join(timeout=max(1.0, self.POLL_INTERVAL * 10))
            if thread.is_alive():
                log.warning("%s: service thread did not stop in time", self.name)
        self._thread = None

    def _service_loop(self) -> None:
        ep = self._endpoint
        log.debug("%s: service thread started", self.name)
        while not self._stop_event.is_set() and ep is not None:
            try:
                frame = ep.recv(self.POLL_INTERVAL)
            except TransportNotOpen:
                if not self._stop_event.is_set():
                    self._peer_closed("endpoint closed underneath the channel")
                break
            except TransportError as exc:
                log.warning("%s: receive error: %s", self.name, exc)
                continue
            if frame is not None:
                try:
                    self._handle_frame(frame)
                except TransportError as exc:
                    log.warning("%s: could not answer frame %s: %s", self.name, frame, exc)
            try:
                self._housekeeping(time.monotonic())
            except TransportError as exc:
                log.debug("%s: housekeeping send failed: %s", self.name, exc)
        log.debug("%s: service thread stopped", self.name)

    def _handle_frame(self, frame: CanFrame) -> None:
        if frame.arbitration_id == self.tx_id:
            return                                   # our own frame echoed by the adapter
        if frame.arbitration_id != self.rx_id or not frame.data:
            return
        data = frame.data
        b0 = data[0]
        op = b0 >> 4
        self._last_rx = time.monotonic()
        self.stats["rx_frames"] += 1
        if op in _DATA_OPS:
            self._feed_data(b0, data[1:])
        elif op in (DATA_ACK, DATA_NAK):
            with self._cond:
                self._acks.append(b0)
                self._cond.notify_all()
        elif b0 == OP_CHANNEL_TEST:
            # The module tests the channel; answer with our parameters and keep it out
            # of the data stream.
            self.stats["inline_a3"] += 1
            self._send_frame(self.tx_id, self.params.to_bytes(OP_PARAMS_RESPONSE))
        elif b0 == OP_PARAMS_RESPONSE:
            if len(data) == 6:
                with self._cond:
                    self._a1_count += 1
                    self._a3_deadline = None
                    self._keepalive_misses = 0
                    self.peer_params = Tp20Params.from_bytes(data)
                    self._cond.notify_all()
            else:
                log.debug("%s: short A1 frame ignored: %s", self.name, data.hex(" "))
        elif b0 == OP_DISCONNECT:
            with self._cond:
                self._a8_received = True
                ours = self._disconnect_sent
                if ours:
                    # Confirmation of our own A8: disconnect() is waiting for it.
                    self._connected = False
                    if self._peer_closed_reason is None:
                        self._peer_closed_reason = "disconnected by tester"
                    self._cond.notify_all()
            if ours:
                log.debug("%s: module confirmed A8", self.name)
                return
            # Unsolicited disconnect: confirm it, then consider the channel gone.
            try:
                self._send_frame(self.tx_id, bytes([OP_DISCONNECT]))
            except TransportError as exc:
                log.debug("%s: could not confirm A8: %s", self.name, exc)
            self._peer_closed("module sent A8 (disconnect)")
        elif b0 == OP_BREAK:
            # UNVERIFIED: A4 "break" is only described as "receiver discards all data
            # since last ACK"; treating it as a channel close is what VAG Blocks does.
            _warn_unverified("tp20-break",
                             "TP 2.0 treats an incoming A4 (break) as a channel close; the real "
                             "semantics beyond 'discard data since the last ACK' are not documented")
            self._peer_closed("module sent A4 (break)")
        elif b0 == OP_PARAMS_REQUEST:
            self._peer_closed("module sent A0 (channel re-initialised by the peer)")
        else:
            log.warning("%s: unknown TP 2.0 frame on 0x%03X ignored: %s", self.name,
                        frame.arbitration_id, data.hex(" "))

    def _feed_data(self, pci: int, chunk: bytes) -> None:
        op, seq = pci >> 4, pci & 0xF
        if seq != self._rx_seq:
            # Duplicate (module retransmitted after a lost ACK) or a gap. Drop it and,
            # if the module is waiting for an ACK, tell it where to resume.
            self.stats["sequence_errors"] += 1
            log.warning("%s: data frame seq %X, expected %X; %s", self.name, seq, self._rx_seq,
                        "asking for retransmission" if op in _ACK_WANTED_OPS else "dropped")
            if op in _ACK_WANTED_OPS:
                self._send_ack(self._rx_seq)
            return
        with self._cond:
            self._rx_seq = (seq + 1) & 0xF
            self._rx_buf += chunk
            self._rx_prompted = False
            self._rx_last_data = time.monotonic()
            next_seq = self._rx_seq
        if op in _ACK_WANTED_OPS:
            self._send_ack(next_seq)
        with self._cond:
            if self._rx_expected is None and len(self._rx_buf) >= 2:
                self._rx_expected = int.from_bytes(self._rx_buf[:2], "big") & 0x7FFF
            expected = self._rx_expected
            complete = op in _LAST_OPS or (expected is not None and len(self._rx_buf) >= 2 + expected)
            if not complete:
                return
            buf = bytes(self._rx_buf)
            discard = self._rx_discard
            self._rx_buf = bytearray()
            self._rx_expected = None
            self._rx_discard = False
            if discard:
                self.stats["discarded_messages"] += 1
                log.debug("%s: discarded a message flushed while in progress: %s", self.name, buf.hex(" "))
                return
            if expected is None:
                self.stats["malformed_messages"] += 1
                log.warning("%s: message ended before its length field; refused: %s", self.name,
                            buf.hex(" "))
                return
            if expected == 0:
                self.stats["malformed_messages"] += 1
                log.warning("%s: message announces length 0; refused: %s", self.name, buf.hex(" "))
                return
            message = buf[2:2 + expected]
            if len(message) < expected:
                # pq-flasher asserts len(data) == length; kwp2000-can completes only on
                # len(buffer) >= length. Never hand a KWP client a truncated reply.
                self.stats["malformed_messages"] += 1
                log.warning("%s: message announced %d bytes but ended after %d; refused: %s",
                            self.name, expected, len(message), buf.hex(" "))
                return
            if len(buf) > 2 + expected:
                log.debug("%s: %d trailing byte(s) after a %d-byte message ignored", self.name,
                          len(buf) - 2 - expected, expected)
            self._inbox.append(message)
            self.stats["rx_messages"] += 1
            self._cond.notify_all()

    def _housekeeping(self, now: float) -> None:
        if not self._connected:
            return
        prompt_seq: Optional[int] = None
        with self._cond:
            if self._rx_buf:
                silence = now - self._rx_last_data
                if silence >= self.t1 * self.PARTIAL_TIMEOUT_FACTOR:
                    # The module neither continued nor answered the prompt: its message
                    # is gone; the next data frame starts a new one.
                    self._abandon_partial_locked(f"no frame for {silence * 1000:.0f} ms")
                elif not self._rx_prompted and silence >= self.t1:
                    # A module whose keepalive fired mid-block may not continue the block
                    # (VWTPLib observation); ACK the last frame we have once so it
                    # retransmits from there.
                    self._rx_prompted = True
                    self.stats["stall_prompts"] += 1
                    prompt_seq = self._rx_seq
        if prompt_seq is not None:
            log.info("%s: no frame for %.0f ms mid-message; prompting retransmission from seq %X",
                     self.name, self.t1 * 1000, prompt_seq)
            self._send_ack(prompt_seq)
        deadline = self._a3_deadline
        if deadline is not None and now >= deadline:
            with self._cond:
                self._a3_deadline = None
                self._keepalive_misses += 1
                misses = self._keepalive_misses
            self.stats["keepalive_misses"] += 1
            _warn_unverified("tp20-keepalive-misses",
                             f"TP 2.0 declares the channel dead after {self.KEEPALIVE_MAX_MISSES} "
                             "unanswered channel tests (SpeckMobil MNCT); a module's real tolerance "
                             "has not been measured")
            log.debug("%s: no A1 within T1 after channel test (%d consecutive)", self.name, misses)
            if misses >= self.KEEPALIVE_MAX_MISSES:
                self._peer_closed(f"no A1 to {misses} consecutive channel tests")
                return
        if not self.keepalive or self._a3_deadline is not None:
            return
        idle = now - max(self._last_tx, self._last_rx)
        if idle < self.keepalive_idle:
            return
        if not self._send_lock.acquire(blocking=False):
            return                                   # a message is in flight: not idle
        try:
            # Arm the deadline before sending so a fast A1 cannot be cleared first.
            self._a3_deadline = time.monotonic() + self.t1
            self._send_frame(self.tx_id, bytes([OP_CHANNEL_TEST]))
            self.stats["keepalives"] += 1
        finally:
            self._send_lock.release()

    def _peer_closed(self, reason: str) -> None:
        with self._cond:
            if not self._connected:
                return
            self._connected = False
            self._peer_closed_reason = reason
            self._cond.notify_all()
        log.warning("%s: channel closed: %s", self.name, reason)
        self._detach_from_bus()

    def _detach_from_bus(self) -> None:
        """Release the tester id and stop listening once the channel is no longer open.

        The module no longer transmits on our id, another channel may claim it, and a
        dead channel must not answer (ACK/A1) frames meant for that new channel. The
        service thread stops itself; :meth:`connect` starts a fresh one.
        """
        _release_tester_rx_id(self.router, self.rx_id, self)
        ep = self._endpoint
        if ep is not None:
            ep.set_accept_ids(())
        self._stop_event.set()

    # -- channel test / disconnect / close ------------------------------------------

    def channel_test(self) -> Tp20Params:
        """Send A3 and wait (peer T1) for the module's A1; returns its parameters."""
        self._ensure_connected()
        with self._send_lock:
            with self._cond:
                before = self._a1_count
            self._a3_deadline = time.monotonic() + self.t1
            self._send_frame(self.tx_id, bytes([OP_CHANNEL_TEST]))
            self.stats["keepalives"] += 1
            with self._cond:
                self._cond.wait_for(lambda: self._a1_count > before or not self._connected,
                                    timeout=self.t1)
                if self._a1_count > before and self.peer_params is not None:
                    return self.peer_params
                if not self._connected:
                    raise Tp20ChannelClosed(f"{self.name}: channel closed ({self._peer_closed_reason})")
        raise Tp20Timeout(f"{self.name}: no A1 to channel test within {self.t1 * 1000:.0f} ms")

    def disconnect(self) -> None:
        """Send A8 and wait up to ``DISCONNECT_TIMEOUT`` for the module's A8; stop the
        service thread and release the tester id. A channel that is not connected
        just stops its thread."""
        with self._connect_lock:
            if self._connected:
                with self._send_lock:
                    with self._cond:
                        self._disconnect_sent = True
                        self._a8_received = False
                    try:
                        self._send_frame(self.tx_id, bytes([OP_DISCONNECT]))
                    except TransportError as exc:
                        log.debug("%s: could not send A8: %s", self.name, exc)
                    with self._cond:
                        self._cond.wait_for(lambda: self._a8_received or not self._connected,
                                            timeout=self.DISCONNECT_TIMEOUT)
                        confirmed = self._a8_received
                        self._connected = False
                        if self._peer_closed_reason is None:
                            self._peer_closed_reason = "disconnected by tester"
                        self._cond.notify_all()
                if confirmed:
                    log.info("%s: disconnected (module confirmed A8)", self.name)
                else:
                    log.info("%s: disconnected (no A8 confirmation within %.1f s)", self.name,
                             self.DISCONNECT_TIMEOUT)
                self._detach_from_bus()
            self._stop_service_thread()

    def close(self) -> None:
        """Stop the keepalive/service thread, disconnect (best effort), release the endpoint."""
        with self._connect_lock:
            if self._closed:
                return
            try:
                self.disconnect()
            except TransportError as exc:
                log.debug("%s: disconnect during close failed: %s", self.name, exc)
            with self._cond:
                self._closed = True
                self._connected = False
                self._cond.notify_all()
            self._stop_service_thread()
            _release_tester_rx_id(self.router, self.rx_id, self)
            ep = self._endpoint
            self._endpoint = None
            if ep is not None:
                try:
                    ep.close()
                except TransportError as exc:
                    log.debug("%s: endpoint close reported %s", self.name, exc)
            log.debug("%s: closed", self.name)


# ============================================================================== probe

@dataclass(frozen=True)
class Tp20ProbeResult:
    """Outcome of one setup request in :func:`probe_tp20_addresses`.

    ``status``: ``open`` (0xD0; ``tester_tx_id`` = the id it assigned, ``None`` when
    the module marked it invalid - such a channel cannot be released with A8),
    ``refused-d6``, ``refused-d7``, ``busy-d8`` (``tester_tx_id`` carries the id from
    the refusal when marked valid), ``tp16`` (a 3-byte ``xx D0 A1`` reply: the older
    fixed-parameter transport) or ``silent``. ``setup_form`` names the 0xC0 form that
    was answered. ``released`` is true when the module confirmed our A8.
    """

    status: str
    tester_tx_id: Optional[int]
    raw: Optional[bytes]
    setup_form: Optional[str] = None
    released: bool = False


@dataclass
class _ProbeSlot:
    address: int
    rx_id: int
    form: str
    deadline: float
    phase: str = "setup"                     # "setup" (awaiting 0xD0) | "release" (awaiting A8)
    result: Optional[Tp20ProbeResult] = None


class _ProbeOwner:
    """Registry owner object for the ids a probe holds (so the refusal names it)."""

    def __init__(self, name: str) -> None:
        self.name = name


def probe_tp20_addresses(
    router: CanRouter,
    addresses: Iterable[int],
    *,
    gap: float = 0.01,
    settle: float = 0.5,
    tester_rx_id: int = 0x300,
    try_alternate: bool = True,
    concurrency: int = 1,
) -> Dict[int, Tp20ProbeResult]:
    """Discover which logical addresses answer a TP 2.0 channel setup.

    The default is the method of the sheet's open question 1, one module at a time:
    send ``addr C0 00 10 00 03 01`` on 0x200, wait up to ``settle`` seconds on
    0x200+addr, and when the module answered 0xD0 send A8 on the tx id it assigned and
    wait (up to ``DISCONNECT_TIMEOUT``) for its A8 before the next address. An address
    still silent after ``settle`` is tried once more with the alternate "both ids
    valid" setup form (``try_alternate``). ``gap`` is the pause after every frame we
    send. Nothing is negotiated (no A0) and nothing is written to any module.

    ``concurrency`` > 1 keeps that many addresses in flight at once, each on its own
    tester receive id ``tester_rx_id + k`` (k < concurrency <= 16), so their replies
    and A8 confirmations never share an id. UNVERIFIED: that several channels can be
    open at the same time (on distinct ids) is only *reported* - PyVCDS allocates
    0x300..0x30F and the VWTPLib emulator says "sessions with IDs 301, 302, etc. can be
    opened at the same time" - and whether a J533 gateway tolerates it is open
    question 6; the function warns once when first used this way.

    The tester ids are claimed in the per-router registry for the duration, so a
    probe never collides with a live :class:`Tp20Channel` (a clash raises
    :class:`Tp20Error` before anything is sent).
    """
    addrs = sorted({int(a) for a in addresses})
    for a in addrs:
        if not 0x01 <= a <= 0xEF:
            raise ValueError(f"logical address 0x{a:X} outside 0x01..0xEF")
    if not 1 <= int(concurrency) <= len(TESTER_RX_ID_POOL):
        raise ValueError(f"concurrency must be 1..{len(TESTER_RX_ID_POOL)}, got {concurrency!r}")
    rx_ids = [int(tester_rx_id) + k for k in range(int(concurrency))]
    if not 0 <= rx_ids[0] <= rx_ids[-1] <= 0x7FF:
        raise ValueError(f"tester_rx_id 0x{tester_rx_id:X} + {concurrency} ids exceeds 11 bits")
    if concurrency > 1:
        # UNVERIFIED: simultaneous channels on distinct tester ids (tp20.md REPORTED,
        # OPEN Q.6); the sequential default needs nothing beyond one channel at a time.
        _warn_unverified(
            "tp20-probe-concurrent",
            f"TP 2.0 probe keeps {concurrency} channels open at once on tester ids "
            f"0x{rx_ids[0]:X}..0x{rx_ids[-1]:X}; that modules/gateway accept several "
            "simultaneous channels is only reported (PyVCDS, VWTPLib), not traced on the target cars")
    results: Dict[int, Tp20ProbeResult] = {}
    owner = _ProbeOwner("tp20-probe")
    claimed: List[int] = []
    endpoint: Optional[RouterEndpoint] = None
    try:
        for rid in rx_ids:
            _claim_tester_rx_id(router, rid, owner)
            claimed.append(rid)
        endpoint = router.endpoint(set(range(SETUP_ID + 1, SETUP_ID + 0x100)) | set(rx_ids),
                                   name="tp20-probe")
        queue: Deque[int] = deque(addrs)
        free: Deque[int] = deque(rx_ids)
        slots: Dict[int, _ProbeSlot] = {}
        released = 0

        def finish(slot: _ProbeSlot) -> None:
            nonlocal released
            assert slot.result is not None
            results[slot.address] = slot.result
            if slot.result.released:
                released += 1
            del slots[slot.rx_id]
            free.append(slot.rx_id)

        def start(slot: _ProbeSlot) -> None:
            rx = slot.rx_id if slot.form == "alternate" else None
            endpoint.send(CanFrame(SETUP_ID, build_setup_request(slot.address, tx_id=slot.rx_id,
                                                                 rx_id=rx)))
            slot.deadline = time.monotonic() + settle
            log.debug("tp20 probe: 0x%02X (%s form) on tester id 0x%03X", slot.address, slot.form,
                      slot.rx_id)
            time.sleep(gap)

        while queue or slots:
            while queue and free:
                slot = _ProbeSlot(queue.popleft(), free.popleft(), "standard", 0.0)
                slots[slot.rx_id] = slot
                start(slot)
            if not slots:
                continue
            earliest = min(s.deadline for s in slots.values())
            frame = endpoint.recv(max(0.0, earliest - time.monotonic()))
            if frame is not None:
                _probe_handle_frame(endpoint, frame, slots, gap)
            now = time.monotonic()
            for slot in list(slots.values()):
                if now < slot.deadline:
                    continue
                if slot.result is None:                      # setup wait expired: silent so far
                    if slot.form == "standard" and try_alternate:
                        slot.form = "alternate"
                        start(slot)
                        continue
                    slot.result = Tp20ProbeResult("silent", None, None, None)
                elif slot.phase == "release" and not slot.result.released:
                    log.info("tp20 probe: no A8 confirmation from 0x%02X within %.1f s", slot.address,
                             Tp20Channel.DISCONNECT_TIMEOUT)
                finish(slot)
        opened = sum(1 for r in results.values() if r.status == "open")
        log.info("tp20 probe: %d of %d addresses answered 0xD0 (%d released with A8), %d refused, "
                 "%d TP 1.6, %d silent", opened, len(addrs), released,
                 sum(1 for r in results.values() if r.status.startswith(("refused", "busy"))),
                 sum(1 for r in results.values() if r.status == "tp16"),
                 sum(1 for r in results.values() if r.status == "silent"))
    finally:
        if endpoint is not None:
            endpoint.close()
        for rid in claimed:
            _release_tester_rx_id(router, rid, owner)
    return results


def _probe_handle_frame(endpoint: RouterEndpoint, frame: CanFrame, slots: Dict[int, _ProbeSlot],
                        gap: float) -> None:
    data = frame.data
    if frame.arbitration_id in slots:
        # A frame on one of our tester ids: only the A8 confirmation matters here.
        slot = slots[frame.arbitration_id]
        if slot.phase == "release" and data[:1] == bytes([OP_DISCONNECT]) and slot.result is not None:
            slot.result = Tp20ProbeResult(slot.result.status, slot.result.tester_tx_id,
                                          slot.result.raw, slot.result.setup_form, released=True)
            slot.deadline = 0.0                  # finish on the next pass
        return
    addr = frame.arbitration_id - SETUP_ID
    for slot in slots.values():
        if slot.address == addr and slot.phase == "setup":
            break
    else:
        return
    if len(data) == 3 and data[1] == OP_SETUP_OK:
        slot.result = Tp20ProbeResult("tp16", None, data, slot.form)
        log.info("tp20 probe: 0x%02X answered with TP 1.6 reply %s", addr, data.hex(" "))
        slot.deadline = 0.0
        return
    if len(data) != 7:
        return
    opcode = data[1]
    if opcode == OP_SETUP_OK:
        resp = parse_setup_response(data)
        if not resp.tx_valid:
            log.warning("tp20 probe: 0x%02X opened a channel but named an invalid transmit id (%s); "
                        "it cannot be released with A8", addr, data.hex(" "))
            slot.result = Tp20ProbeResult("open", None, data, slot.form)
            slot.deadline = 0.0
            return
        slot.result = Tp20ProbeResult("open", resp.tx_id, data, slot.form)
        endpoint.send(CanFrame(resp.tx_id, bytes([OP_DISCONNECT])))
        slot.phase = "release"
        slot.deadline = time.monotonic() + Tp20Channel.DISCONNECT_TIMEOUT
        time.sleep(gap)
    elif opcode in OP_SETUP_REFUSED:
        resp = parse_setup_response(data)
        status = {0xD6: "refused-d6", 0xD7: "refused-d7", 0xD8: "busy-d8"}[opcode]
        slot.result = Tp20ProbeResult(status, resp.tx_id if resp.tx_valid else None, data, slot.form)
        slot.deadline = 0.0
    else:
        log.debug("tp20 probe: unexpected opcode 0x%02X from 0x%02X: %s", opcode, addr, data.hex(" "))
