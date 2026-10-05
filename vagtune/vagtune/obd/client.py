"""
Generic OBD-II client (SAE J1979 / ISO 15031-5 over ISO 15765-4).

Works on any :class:`~vagtune.transport.base.IsoTpLink`:

* **functional**: ``tx 0x7DF`` with ``extra_rx_ids`` 0x7E8..0x7EF (what
  ``TransportContext.isotp_link(0x7DF, 0x7E8, extra_rx_ids=range(0x7E9, 0x7F0))``
  returns). Every request is a broadcast; :meth:`ObdClient.request_all` collects the
  reply of every ECU that answers within the P2 window and returns ``{response_id:
  payload}``. ``link.last_rx_id`` names the responder of each payload.
* **physical**: ``tx 0x7E0 / rx 0x7E8`` (or any pair); the same code path with a
  single expected responder, so it returns as soon as that ECU has answered.

Timing follows ISO 15031-5 Table 5: P2CAN max is 50 ms for every unsegmented
response / first frame, so the collection window defaults to a generous 250 ms (USB
pass-thru latency, Python). A responder that answers ``7F <SID> 78``
(requestCorrectlyReceived-ResponsePending, allowed for Mode 04 clear and Mode 09 CVN,
*not* for Mode 01) gets its own P2* window (5 s) while the other responders are still
collected within P2. A final negative response is kept per responder; the single-ECU
helpers raise :class:`ObdNegativeResponse` for it, the ``*_all`` helpers skip the ECU
with a log line (``7F xx 11/12`` from a VW ECU means "not supported", exactly like
the ISO-prescribed silence).

A positive reply is only accepted as the answer to a request when its echo matches
what was asked (Mode 01/02: the first PID (and frame#) is one of the requested ones;
Mode 06: the OBDMID; Mode 09: the InfoType). A reply that arrived too late for the
previous request of the same mode therefore cannot be mistaken for the answer to the
next one. Modes 03/04/07/0A carry no echo, so they cannot be checked that way.

A final ``7F <SID> 21`` (busyRepeatRequest) is retried after
:attr:`ObdTiming.busy_delay` (ISO 15765-4 §4.2.1: at least 200 ms) up to
:attr:`ObdTiming.busy_retries` times (the standard's six sequences) before it is
reported as that ECU's final answer.

Scope: 11-bit identifiers only (both of the owner's cars). The 29-bit fallback of the
ISO 15765-4 initialisation (0x18DB33F1 / 0x18DAF1xx after an 11-bit P2 timeout) is not
implemented; :meth:`ObdClient.discover` on a 29-bit-only vehicle simply finds nothing.

Every helper comes in two flavours: ``x()`` picks the engine (the link's ``rx_id``,
normally 0x7E8) or, failing that, the first responder; ``x_all()`` returns a dict
keyed by response id so the CLI can print one block per ECU.
"""

from __future__ import annotations

import logging
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Set, Tuple

from ..transport.base import IsoTpLink, TransportError, TransportNotOpen
from ..transport.isotp import FUNCTIONAL_IDS
from ..uds.exceptions import NRC_NAMES
from . import pids as P
from .pids import (
    DEFAULT_SCALING,
    LAMBDA_PIDS,
    MonitorStatus,
    PidDef,
    ScalingOverrides,
    decode_monitor_status,
    decode_pid,
    decode_vehicle_info,
    parse_dtc_list,
    parse_supported,
    uas_apply,
    uas_raw,
    walk_records,
    warn_unverified,
)

log = logging.getLogger(__name__)

NEGATIVE_RESPONSE_SID = 0x7F
NRC_RESPONSE_PENDING = 0x78
NRC_BUSY_REPEAT = 0x21
NRC_SERVICE_NOT_SUPPORTED = 0x11
NRC_SUBFUNCTION_NOT_SUPPORTED = 0x12
NRC_CONDITIONS_NOT_CORRECT = 0x22

MODE_CURRENT = 0x01
MODE_FREEZE = 0x02
MODE_DTC_CONFIRMED = 0x03
MODE_CLEAR = 0x04
MODE_MONITOR_RESULTS = 0x06
MODE_DTC_PENDING = 0x07
MODE_CONTROL = 0x08
MODE_VEHICLE_INFO = 0x09
MODE_DTC_PERMANENT = 0x0A

DTC_MODES = (MODE_DTC_CONFIRMED, MODE_DTC_PENDING, MODE_DTC_PERMANENT)
#: services whose sub-parameters are enumerated by Annex A bitmaps (00, 20, 40, ...)
BITMAP_MODES = (MODE_CURRENT, MODE_FREEZE, MODE_MONITOR_RESULTS, MODE_CONTROL, MODE_VEHICLE_INFO)
#: services whose positive reply echoes the sub-parameter in its second byte
ECHO_MODES = (MODE_CURRENT, MODE_FREEZE, MODE_MONITOR_RESULTS, MODE_CONTROL, MODE_VEHICLE_INFO)
MAX_PIDS_PER_REQUEST = 6          # ISO 15031-5 §7.1.1
MAX_FREEZE_PAIRS_PER_REQUEST = 3  # ISO 15031-5 Table 137
MAX_REQUEST_BYTES = 7             # every OBD request fits one ISO-TP single frame (ISO 15765-4)
#: bitmap ids per batched request: 6 (one byte each) except Mode 02 (PID + frame# pairs)
BITMAPS_PER_REQUEST = {MODE_FREEZE: MAX_FREEZE_PAIRS_PER_REQUEST}


# ===================================================================== errors

class ObdError(Exception):
    """Base class for OBD-layer failures."""


class ObdTimeout(ObdError):
    """No ECU answered (or the requested ECU did not answer) within the window."""


class ObdProtocolError(ObdError):
    """A response arrived but is malformed for the service."""


class ObdNegativeResponse(ObdError):
    """An ECU answered ``7F <SID> <NRC>``."""

    def __init__(self, sid: int, nrc: int, response_id: Optional[int] = None) -> None:
        self.sid = sid
        self.nrc = nrc
        self.response_id = response_id
        self.nrc_name = NRC_NAMES.get(nrc, f"0x{nrc:02X}")
        who = f" from 0x{response_id:X}" if response_id is not None else ""
        super().__init__(f"OBD mode 0x{sid:02X} rejected{who}: {self.nrc_name} (NRC 0x{nrc:02X})")

    @property
    def unsupported(self) -> bool:
        return self.nrc in (NRC_SERVICE_NOT_SUPPORTED, NRC_SUBFUNCTION_NOT_SUPPORTED)


# ==================================================================== results

@dataclass
class ObdTiming:
    """P2 = collection window for all responders; P2* = per-responder window after 0x78.

    ``busy_delay`` / ``busy_retries``: how long to wait before repeating a request that
    an ECU answered with ``7F SID 21`` (busyRepeatRequest) and how many times (ISO
    15765-4 §4.2.1: at least 200 ms, give up after six sequences = five retries).
    The link is always polled at least once, so ``p2=0`` still takes a reply that is
    already buffered; negative values are rejected.
    """
    p2: float = 0.25
    p2_star: float = 5.0
    pending_limit: int = 30
    busy_delay: float = 0.2
    busy_retries: int = 5

    def __post_init__(self) -> None:
        for name in ("p2", "p2_star", "busy_delay"):
            if getattr(self, name) < 0:
                raise ValueError(f"ObdTiming.{name} must not be negative")
        if self.pending_limit < 0 or self.busy_retries < 0:
            raise ValueError("ObdTiming.pending_limit / busy_retries must not be negative")


@dataclass
class ObdValue:
    """One decoded PID from one ECU (``frame`` is set for Mode 02 values)."""
    mode: int
    pid: int
    name: str
    raw: bytes
    value: Any
    unit: str = ""
    units: Mapping[str, str] = field(default_factory=dict)
    response_id: Optional[int] = None
    frame: Optional[int] = None

    def pretty(self, precision: int = 2) -> str:
        return P.format_value(self.value, self.unit, self.units, precision)

    def __str__(self) -> str:
        return f"{self.pid:02X} {self.name}: {self.pretty()}"


@dataclass
class Mode06Result:
    """One 9-byte Mode 06 record, scaled through its UASID."""
    obdmid: int
    tid: int
    uasid: int
    value: Any
    min: Any
    max: Any
    unit: str
    passed: bool
    raw_value: int
    raw_min: int
    raw_max: int
    response_id: Optional[int] = None
    uas_known: bool = True

    @property
    def completed(self) -> bool:
        """False when TV = MIN = MAX = 0 (monitor not run since clear / battery disconnect)."""
        return not (self.raw_value == 0 and self.raw_min == 0 and self.raw_max == 0)

    @property
    def obdmid_name(self) -> str:
        return P.obdmid_name(self.obdmid)

    @property
    def tid_name(self) -> str:
        return P.tid_name(self.tid)


@dataclass
class VehicleInfo:
    """One Mode 09 InfoType from one ECU (``value`` type depends on the InfoType)."""
    infotype: int
    name: str
    nodi: int
    raw: bytes
    value: Any
    response_id: Optional[int] = None


def parse_mode06_records(payload: bytes, response_id: Optional[int] = None) -> List[Mode06Result]:
    """Parse the bytes after ``46`` as 9-byte records ``[MID][TID][UASID][TV][MIN][MAX]``.

    ISO example ``01 01 0A 0B B0 0B B0 0B B0 01 05 10 00 48 00 00 00 64 01 85 24 00 96
    00 4B FF FF`` -> three results (0.365 V constant; 0.072 s within 0..0.1 s; 150 counts
    within 75..65535). A trailing fragment shorter than 9 bytes is logged and dropped.
    """
    out: List[Mode06Result] = []
    whole = len(payload) - len(payload) % 9
    if whole != len(payload):
        log.warning("Mode 06 payload has %d trailing byte(s) that do not form a record", len(payload) - whole)
    for i in range(0, whole, 9):
        mid, tid, uas = payload[i], payload[i + 1], payload[i + 2]
        tv, mn, mx = (int.from_bytes(payload[i + 3 + 2 * k:i + 5 + 2 * k], "big") for k in range(3))
        value, unit, known = uas_apply(uas, tv)
        vmin, _, _ = uas_apply(uas, mn)
        vmax, _, _ = uas_apply(uas, mx)
        passed = uas_raw(uas, mn) <= uas_raw(uas, tv) <= uas_raw(uas, mx)
        if not known:
            log.info("Mode 06 OBDMID %02X TID %02X uses unknown UASID 0x%02X; values left raw", mid, tid, uas)
        out.append(Mode06Result(mid, tid, uas, value, vmin, vmax, unit, passed, tv, mn, mx,
                                response_id, known))
    return out


# ===================================================================== client

class ObdClient:
    """SAE J1979 services on one ISO-TP link (functional or physical)."""

    def __init__(self, link: IsoTpLink, *, timing: Optional[ObdTiming] = None,
                 batch_bitmaps: bool = False) -> None:
        """
        ``batch_bitmaps=True`` requests the supported-ID bitmaps several per message
        (``01 00 20 40 60 80 A0``, legal per ISO 15031-5 Annex A; Mode 02 takes three
        ``PID frame#`` pairs, ``02 00 00 20 00 40 00``, so the request stays within one
        frame); the default walks one bitmap per request, which every ECU since 1996
        handles.
        """
        self.link = link
        self.timing = timing or ObdTiming()
        self.batch_bitmaps = batch_bitmaps
        self.functional = link.tx_id in FUNCTIONAL_IDS
        #: response ids seen answering at all (positively or negatively) on a functional
        #: link; the P2 window ends early once every one of them has replied positively.
        self.responders: Set[int] = set()
        self._lock = threading.RLock()
        self._supported: Dict[Tuple[int, int], Set[int]] = {}
        self._scaling: Dict[int, ScalingOverrides] = {}
        self._pid01_cache: Dict[int, MonitorStatus] = {}
        #: final negative replies to the most recent request: {response_id: (sid, nrc)}
        self.last_negatives: Dict[int, Tuple[int, int]] = {}

    # ------------------------------------------------------------- raw I/O

    def _responder_of(self) -> int:
        rid = getattr(self.link, "last_rx_id", None)
        return self.link.rx_id if rid is None else int(rid)

    @staticmethod
    def _echo_matches(payload: bytes, data: bytes) -> bool:
        """Does positive reply ``data`` echo a sub-parameter of request ``payload``?

        Mode 01/06/08/09: ``data[1]`` must be one of the requested ids; Mode 02:
        ``(data[1], data[2])`` one of the requested (PID, frame#) pairs. Other modes
        carry no echo and always match. A positive reply too short to hold the echo
        does not match (ISO requires at least the sub-parameter byte).
        """
        sid = payload[0]
        if sid not in ECHO_MODES:
            return True
        if sid == MODE_FREEZE:
            pairs = {(payload[i], payload[i + 1]) for i in range(1, len(payload) - 1, 2)}
            return len(data) >= 3 and (data[1], data[2]) in pairs
        return len(data) >= 2 and data[1] in set(payload[1:])

    def request_all(self, payload: bytes, *, window: Optional[float] = None,
                    expect: Optional[Iterable[int]] = None) -> Dict[int, bytes]:
        """Send ``payload`` once and collect every responder's *final* reply.

        Returns ``{response_id: payload}`` with the raw payload (positive ``SID+0x40 ...``
        or final negative ``7F SID NRC``). ``7F SID 78`` extends that responder's
        deadline to P2* and is not returned. The window closes after ``window`` (P2)
        unless a responder is still pending, or earlier when every id in ``expect``
        (default: the known responders on a functional link, the ``rx_id`` on a
        physical one) has answered *positively*; a negative reply carries no echo, so
        it may be a late ``7F`` to an earlier request and does not end the window (the
        genuine positive reply, if one follows, replaces it). The link is polled at
        least once even when the window is 0.

        A positive reply must echo one of the requested sub-parameters
        (:meth:`_echo_matches`); a late reply to an *earlier* request of the same mode
        is logged and dropped instead of being attributed to this one. Only the first
        matching positive reply per id is kept (a second one - two simulated nodes on
        one id, a chatty gateway - is logged as a duplicate); a matching positive reply
        replaces a negative one recorded earlier for the same id.

        Every ECU that answers at all, positively or negatively, is remembered in
        :attr:`responders` on a functional link: presence is what the early-exit rule
        (ISO 15031-5 §5.2.4.2, "all expected servers have responded") needs.

        ``7F SID 21`` (busyRepeatRequest) is retried after :attr:`ObdTiming.busy_delay`
        up to :attr:`ObdTiming.busy_retries` times, keeping the replies already
        collected from the other ECUs; only when the retries are exhausted is the 0x21
        returned as that ECU's final reply.

        Raises ``ValueError`` for an empty payload or one longer than 7 bytes: every
        OBD request fits one single frame (functional requests cannot be segmented).
        """
        if not payload:
            raise ValueError("OBD request must carry at least the mode byte")
        if len(payload) > MAX_REQUEST_BYTES:
            raise ValueError(f"OBD request of {len(payload)} bytes does not fit one ISO-TP frame "
                             f"({payload.hex(' ')}); ISO 15031-5 limits requests to 7 bytes")
        sid = payload[0]
        window = self.timing.p2 if window is None else window
        if expect is None:
            expected: Set[int] = set(self.responders) if self.functional else {self.link.rx_id}
        else:
            expected = set(expect)
        results: Dict[int, bytes] = {}
        with self._lock:
            self.last_negatives = {}
            pending = self._collect(payload, window, expected, results, set())
            for attempt in range(self.timing.busy_retries):
                busy = {rid for rid, d in results.items()
                        if d[0] == NEGATIVE_RESPONSE_SID and d[2] == NRC_BUSY_REPEAT}
                if not busy:
                    break
                log.info("mode %02X: %s busy (NRC 0x21); repeating after %.0f ms (retry %d of %d)", sid,
                         ", ".join(f"0x{r:X}" for r in sorted(busy)), self.timing.busy_delay * 1000,
                         attempt + 1, self.timing.busy_retries)
                time.sleep(self.timing.busy_delay)
                for rid in busy:
                    results.pop(rid)
                    self.last_negatives.pop(rid, None)
                pending |= self._collect(payload, window, busy, results, set(results))
            for rid, data in results.items():
                if data[0] == NEGATIVE_RESPONSE_SID:
                    self.last_negatives[rid] = (sid, data[2])
        if pending:
            log.warning("mode %02X: responder(s) %s never completed after response-pending",
                        sid, ", ".join(f"0x{r:X}" for r in pending))
        return results

    def _collect(self, payload: bytes, window: float, expected: Set[int], results: Dict[int, bytes],
                 quiet: Set[int]) -> Set[int]:
        """One send + one P2 collection round into ``results``; returns the ids that
        were still response-pending when the round ended. Replies from ids in ``quiet``
        (already answered in an earlier round) are dropped silently."""
        sid = payload[0]
        pending: Dict[int, float] = {}
        pending_count: Dict[int, int] = {}
        self.link.flush_rx()
        self.link.send(payload)
        deadline = time.monotonic() + window
        first_poll = True
        while True:
            now = time.monotonic()
            until = max([deadline] + list(pending.values()))
            remaining = until - now
            if remaining <= 0 and not first_poll:
                break
            positive = {r for r, d in results.items() if d[0] != NEGATIVE_RESPONSE_SID}
            if expected and not pending and expected <= positive:
                break
            first_poll = False
            try:
                data = self.link.recv(min(max(remaining, 0.0), 0.5))
            except TransportNotOpen:
                raise
            except TransportError as exc:
                log.warning("OBD mode %02X: inbound transfer failed (%s); continuing", sid, exc)
                continue
            if not data:
                continue
            rid = self._responder_of()
            if data[0] == NEGATIVE_RESPONSE_SID:
                if len(data) < 3 or data[1] != sid:
                    log.debug("ignoring negative response %s for another service", data.hex(" "))
                    continue
                if data[2] == NRC_RESPONSE_PENDING:
                    n = pending_count.get(rid, 0) + 1
                    pending_count[rid] = n
                    if n > self.timing.pending_limit:
                        log.warning("0x%X exceeded %d response-pending replies to mode %02X",
                                    rid, self.timing.pending_limit, sid)
                        pending.pop(rid, None)
                        continue
                    pending[rid] = time.monotonic() + self.timing.p2_star
                    log.debug("0x%X: response pending for mode %02X (%d)", rid, sid, n)
                    continue
                pending.pop(rid, None)
                if rid in results:
                    if rid not in quiet:
                        log.warning("duplicate reply from 0x%X to mode %02X ignored: %s", rid, sid, data.hex(" "))
                    continue
                results[rid] = bytes(data)
                if self.functional:
                    self.responders.add(rid)
                continue
            if data[0] != sid + 0x40:
                log.debug("ignoring stray payload %s while waiting for mode %02X", data.hex(" "), sid)
                continue
            if not self._echo_matches(payload, data):
                log.warning("0x%X: reply %s does not answer request %s (late reply to an earlier "
                            "request?); ignored", rid, data.hex(" "), payload.hex(" "))
                continue
            pending.pop(rid, None)
            if rid in results:
                if results[rid][0] == NEGATIVE_RESPONSE_SID:
                    log.warning("0x%X: positive reply %s replaces the earlier negative %s to mode %02X",
                                rid, data.hex(" "), results[rid].hex(" "), sid)
                    results[rid] = bytes(data)
                elif rid not in quiet:
                    log.warning("duplicate reply from 0x%X to mode %02X ignored: %s", rid, sid, data.hex(" "))
                continue
            results[rid] = bytes(data)
            if self.functional:
                self.responders.add(rid)
        return set(pending)

    def query_all(self, payload: bytes, **kw: Any) -> Dict[int, bytes]:
        """Like :meth:`request_all` but only positive replies, with the SID stripped;
        negative replies are logged (``11``/``12`` at debug: "not supported")."""
        out: Dict[int, bytes] = {}
        for rid, data in self.request_all(payload, **kw).items():
            if data[0] == NEGATIVE_RESPONSE_SID:
                nrc = data[2]
                level = logging.DEBUG if nrc in (NRC_SERVICE_NOT_SUPPORTED, NRC_SUBFUNCTION_NOT_SUPPORTED) \
                    else logging.INFO
                log.log(level, "0x%X rejected mode %02X: %s (NRC 0x%02X)", rid, payload[0],
                        NRC_NAMES.get(nrc, "?"), nrc)
                continue
            out[rid] = data[1:]
        return out

    def _pick(self, responses: Mapping[int, bytes], response_id: Optional[int], sid: int) -> Tuple[int, bytes]:
        """Choose one responder's entry: ``response_id`` if given, else the engine
        (``rx_id``), else the lowest id. With no positive entry at all, a final negative
        reply to the last request (from that ECU) is raised as :class:`ObdNegativeResponse`
        so "not supported" is distinguishable from silence; otherwise :class:`ObdTimeout`."""
        if not responses:
            neg = self.last_negatives
            if neg:
                rid = response_id if response_id in neg else (self.link.rx_id if self.link.rx_id in neg else min(neg))
                if response_id is None or rid == response_id:
                    neg_sid, nrc = neg[rid]
                    raise ObdNegativeResponse(neg_sid, nrc, rid)
            where = f"0x{self.link.tx_id:X}"
            raise ObdTimeout(f"no ECU answered OBD mode 0x{sid:02X} on {where} within "
                             f"{self.timing.p2 * 1000:.0f} ms")
        if response_id is not None:
            if response_id not in responses:
                raise ObdTimeout(f"ECU 0x{response_id:X} did not answer OBD mode 0x{sid:02X}")
            rid = response_id
        elif self.link.rx_id in responses:
            rid = self.link.rx_id
        else:
            rid = min(responses)
        return rid, responses[rid]

    def request(self, payload: bytes, *, response_id: Optional[int] = None, **kw: Any) -> bytes:
        """Send once; return the positive payload (SID stripped) of ``response_id``,
        else of the engine (``rx_id``), else of the lowest responder.

        Raises :class:`ObdTimeout` when nobody (or not that ECU) answered and
        :class:`ObdNegativeResponse` for a final negative reply.
        """
        rid, data = self._pick(self.request_all(payload, **kw), response_id, payload[0])
        if data[0] == NEGATIVE_RESPONSE_SID:
            raise ObdNegativeResponse(payload[0], data[2], rid)
        return data[1:]

    def discover(self) -> Set[int]:
        """``01 00`` functionally (the ISO 15765-4 init / ping); returns the responder ids.

        An ECU answering ``7F 01 21`` (busy) is re-asked after ``busy_delay`` up to
        ``busy_retries`` times by :meth:`request_all`; one that stays busy through every
        sequence is treated as absent (ISO 15765-4 §4.2.1: "not compliant"). 29-bit
        addressing is not attempted (see the module docstring).
        """
        found = self.query_all(bytes([MODE_CURRENT, 0x00]), expect=())
        for rid, data in found.items():
            if len(data) >= 5 and data[0] == 0x00:
                log.debug("0x%X answers 01 00 with %s", rid, data[1:5].hex(" "))
        return set(found)

    # ------------------------------------------------------ supported bitmaps

    @staticmethod
    def _bitmap_request(mode: int, bases: Sequence[int]) -> bytes:
        if mode == MODE_FREEZE:
            body = b"".join(bytes([b, 0x00]) for b in bases)
        else:
            body = bytes(bases)
        return bytes([mode]) + body

    def _parse_bitmap_records(self, mode: int, data: bytes) -> Dict[int, Set[int]]:
        """``data`` = payload after the positive SID; returns ``{base: ids}``."""
        hdr = 2 if mode == MODE_FREEZE else 1
        out: Dict[int, Set[int]] = {}
        i = 0
        while i + hdr + 4 <= len(data):
            base = data[i]
            if not P.is_support_id(base):
                log.warning("mode %02X bitmap response contains non-bitmap id %02X; stopping", mode, base)
                break
            out[base] = parse_supported(base, data[i + hdr:i + hdr + 4])
            i += hdr + 4
        return out

    def supported_ids_all(self, mode: int, *, refresh: bool = False) -> Dict[int, Set[int]]:
        """Walk the supported-ID bitmaps (0x00, 0x20, ... 0xE0) for ``mode`` on every responder.

        Works for Mode 01/02 PIDs, Mode 06 OBDMIDs, Mode 08 TIDs and Mode 09 InfoTypes
        (same bitmap scheme, ISO 15031-5 Annex A); any other mode raises ``ValueError``
        (Modes 03/04/07/0A take no sub-parameter, so ``03 00`` would be a malformed
        request). The bitmap ids themselves are excluded from the returned sets.
        Results are cached per (mode, responder).

        With ``batch_bitmaps`` the bases go out :data:`BITMAPS_PER_REQUEST` at a time
        (six, or three for Mode 02) and the next batch is only sent when some ECU
        flagged its first base as supported.
        """
        if mode not in BITMAP_MODES:
            raise ValueError(f"mode 0x{mode:02X} has no supported-ID bitmaps (only "
                             + ", ".join(f"{m:02X}" for m in BITMAP_MODES) + ")")
        if not refresh:
            cached = {rid: set(ids) for (m, rid), ids in self._supported.items() if m == mode}
            if cached and (not self.functional or set(cached) >= self.responders):
                return cached
        result: Dict[int, Set[int]] = {}
        todo: Dict[int, List[int]] = {}       # per responder: bases still to request

        def absorb(responses: Mapping[int, bytes]) -> None:
            for rid, data in responses.items():
                for base, ids in self._parse_bitmap_records(mode, data).items():
                    result.setdefault(rid, set()).update(ids)
                    nxt = P.next_support_id(base)
                    if nxt is not None and nxt in ids:
                        todo.setdefault(rid, []).append(nxt)

        if self.batch_bitmaps:
            per = BITMAPS_PER_REQUEST.get(mode, MAX_PIDS_PER_REQUEST)
            groups = [list(P.SUPPORT_BASES[i:i + per]) for i in range(0, len(P.SUPPORT_BASES), per)]
            absorb(self.query_all(self._bitmap_request(mode, groups[0]), expect=()))
            for group in groups[1:]:
                if not any(group[0] in ids for ids in result.values()):
                    break
                absorb(self.query_all(self._bitmap_request(mode, group)))
        else:
            absorb(self.query_all(self._bitmap_request(mode, [0x00]), expect=()))
            done: Set[int] = {0x00}
            while True:
                wanted = sorted({b for bs in todo.values() for b in bs if b not in done})
                if not wanted:
                    break
                base = wanted[0]
                done.add(base)
                absorb(self.query_all(self._bitmap_request(mode, [base])))
        for rid, ids in result.items():
            ids.difference_update(P.SUPPORT_BASES)
            self._supported[(mode, rid)] = set(ids)
        return result

    def supported_ids(self, mode: int, *, response_id: Optional[int] = None) -> Set[int]:
        per_ecu = self.supported_ids_all(mode)
        rid, _ = self._pick({r: b"" for r in per_ecu}, response_id, mode)
        return set(per_ecu[rid])

    def supported_pids(self, mode: int = MODE_CURRENT, *, response_id: Optional[int] = None) -> Set[int]:
        return self.supported_ids(mode, response_id=response_id)

    def supported_pids_all(self, mode: int = MODE_CURRENT) -> Dict[int, Set[int]]:
        return self.supported_ids_all(mode)

    def supported_infotypes(self, *, response_id: Optional[int] = None) -> Set[int]:
        return self.supported_ids(MODE_VEHICLE_INFO, response_id=response_id)

    def supported_infotypes_all(self) -> Dict[int, Set[int]]:
        return self.supported_ids_all(MODE_VEHICLE_INFO)

    def supported_obdmids(self, *, response_id: Optional[int] = None) -> Set[int]:
        return self.supported_ids(MODE_MONITOR_RESULTS, response_id=response_id)

    def supported_obdmids_all(self) -> Dict[int, Set[int]]:
        return self.supported_ids_all(MODE_MONITOR_RESULTS)

    # ------------------------------------------------------------- scaling

    def scaling_for(self, response_id: int) -> ScalingOverrides:
        """PID 4F/50 overrides for one ECU (read once, cached; default when unsupported)."""
        if response_id in self._scaling:
            return self._scaling[response_id]
        supported = self._supported.get((MODE_CURRENT, response_id))
        if supported is None:
            supported = self.supported_ids_all(MODE_CURRENT).get(response_id, set())
        want = [pid for pid in (0x4F, 0x50) if pid in supported]
        pid4f_a = pid50_a = 0
        if want:
            values = self._read_mode01_all(want).get(response_id, {})
            if 0x4F in values:
                raw = values[0x4F].raw
                pid4f_a = raw[0]
                if any(raw[1:4]):
                    log.info("0x%X PID 4F maxima B/C/D = %s (O2 V, O2 mA, MAP/10): not applied as "
                             "scaling, only Data A (lambda) is", response_id, raw[1:4].hex(" "))
            if 0x50 in values:
                pid50_a = values[0x50].raw[0]
        sc = ScalingOverrides(pid4f_a, pid50_a)
        if pid4f_a or pid50_a:
            log.info("0x%X scaling overrides: lambda %.7f/bit, MAF %.5f g/s/bit",
                     response_id, sc.lambda_scale, sc.maf_scale)
        self._scaling[response_id] = sc
        return sc

    def set_scaling(self, response_id: int, scaling: ScalingOverrides) -> None:
        self._scaling[response_id] = scaling

    # ------------------------------------------------------------- Mode 01

    def _make_value(self, mode: int, pid: int, data: bytes, rid: int, frame: Optional[int]) -> ObdValue:
        d: Optional[PidDef] = P.pid_def(pid)
        scaling = DEFAULT_SCALING
        if pid == 0x10 or pid in LAMBDA_PIDS:
            scaling = self.scaling_for(rid)
        if d is not None and d.unverified:
            warn_unverified(f"pid{pid:02X}", f"PID {pid:02X} ({d.name}): {d.notes}")
        try:
            value = decode_pid(pid, data, scaling)
        except (IndexError, ValueError) as exc:
            log.warning("0x%X PID %02X: %d byte(s) could not be decoded (%s); raw", rid, pid, len(data), exc)
            value = data.hex(" ").upper()
        return ObdValue(mode, pid, P.pid_name(pid), bytes(data), value,
                        d.unit if d else "", d.units if d else {}, rid, frame)

    @staticmethod
    def _chunk_pids(pids: Sequence[int]) -> List[List[int]]:
        """Split data PIDs into requests: up to 6 per message, variable-length PIDs alone,
        bitmap PIDs never mixed with data PIDs (ISO 15031-5 §7.1.1)."""
        chunks: List[List[int]] = []
        fixed: List[int] = []
        for pid in pids:
            if P.is_support_id(pid):
                chunks.append([pid])
            elif P.pid_length(pid) is None:
                chunks.append([pid])
            else:
                fixed.append(pid)
        for i in range(0, len(fixed), MAX_PIDS_PER_REQUEST):
            chunks.append(fixed[i:i + MAX_PIDS_PER_REQUEST])
        return chunks

    @staticmethod
    def _split_records(mode: int, rid: int, data: bytes, chunk: Sequence[int]
                       ) -> Optional[List[Tuple[int, Optional[int], bytes]]]:
        """Split one ECU's reply ``data`` (after the positive SID) to a request for
        ``chunk`` into ``(pid, frame, body)`` records, using the ISO-TP payload length
        as the truth.

        * One requested PID: the whole remainder is that PID's data, whatever the table
          says (an ECU's own length wins; a difference is logged once per reply). This
          is how the unconfirmed lengths of PIDs >= 0x60 on the EDC17 are tolerated.
        * Several PIDs: the table-driven walk must consume the payload exactly, every
          record must be one of the requested PIDs and have its full length; otherwise
          the reply is *misaligned* (an ECU whose length for one PID differs from the
          table) and ``None`` is returned so the caller re-reads those PIDs one by one.
        """
        hdr = 2 if mode == MODE_FREEZE else 1
        if len(chunk) == 1:
            pid = data[0]
            frame = data[1] if mode == MODE_FREEZE else None
            body = bytes(data[hdr:])
            n = P.pid_length(pid)
            if n is not None and len(body) != n:
                log.warning("0x%X PID %02X: ECU sent %d data byte(s), table says %d; using the ECU's length",
                            rid, pid, len(body), n)
            return [(pid, frame, body)]
        records = walk_records(data, with_frame=(mode == MODE_FREEZE))
        consumed = sum(hdr + len(body) for _, _, body in records)
        aligned = consumed == len(data) and all(
            pid in chunk and (P.pid_length(pid) is None or len(body) == P.pid_length(pid))
            for pid, _, body in records)
        if not aligned:
            log.warning("0x%X: record walk of %s misaligned for PIDs %s (ECU byte counts differ from the "
                        "table); re-reading them one at a time", rid, data.hex(" "),
                        " ".join(f"{p:02X}" for p in chunk))
            return None
        return records

    def _read_records_all(self, mode: int, chunks: Sequence[Sequence[int]], frame: Optional[int]
                          ) -> Dict[int, Dict[int, ObdValue]]:
        """Mode 01 (``frame=None``) or Mode 02 records for ``chunks`` from every responder."""
        out: Dict[int, Dict[int, ObdValue]] = {}
        retry: Dict[int, Set[int]] = {}             # pid -> responders whose reply was misaligned

        def absorb(rid: int, data: bytes, chunk: Sequence[int]) -> None:
            records = self._split_records(mode, rid, data, chunk)
            if records is None:
                for pid in chunk:
                    retry.setdefault(pid, set()).add(rid)
                return
            for pid, frno, body in records:
                out.setdefault(rid, {})[pid] = self._make_value(mode, pid, body, rid, frno)

        for chunk in chunks:
            for rid, data in self.query_all(self._record_request(mode, chunk, frame)).items():
                absorb(rid, data, chunk)
        for pid in sorted(retry):
            for rid, data in self.query_all(self._record_request(mode, [pid], frame)).items():
                if rid in retry[pid]:
                    absorb(rid, data, [pid])
        return out

    @staticmethod
    def _record_request(mode: int, chunk: Sequence[int], frame: Optional[int]) -> bytes:
        if mode == MODE_FREEZE:
            return bytes([MODE_FREEZE]) + b"".join(bytes([p, (frame or 0) & 0xFF]) for p in chunk)
        return bytes([mode]) + bytes(chunk)

    def _read_mode01_all(self, pids: Sequence[int]) -> Dict[int, Dict[int, ObdValue]]:
        return self._read_records_all(MODE_CURRENT, self._chunk_pids(list(pids)), None)

    def read_pids_all(self, pids: Iterable[int]) -> Dict[int, Dict[int, ObdValue]]:
        """Mode 01 for several PIDs, every responder: ``{response_id: {pid: ObdValue}}``."""
        return self._read_mode01_all(list(pids))

    def read_pids(self, pids: Iterable[int], *, response_id: Optional[int] = None) -> Dict[int, ObdValue]:
        wanted = list(pids)
        per_ecu = self.read_pids_all(wanted)
        rid, _ = self._pick({r: b"" for r in per_ecu}, response_id, MODE_CURRENT)
        return per_ecu[rid]

    def read_pid(self, pid: int, *, response_id: Optional[int] = None) -> ObdValue:
        values = self.read_pids([pid], response_id=response_id)
        if pid not in values:
            raise ObdProtocolError(f"ECU answered mode 01 without a record for PID {pid:02X}")
        return values[pid]

    def monitor_status_all(self, *, this_cycle: bool = False) -> Dict[int, MonitorStatus]:
        """PID 01 (or 41 with ``this_cycle``) from every responder, decoded."""
        pid = 0x41 if this_cycle else 0x01
        out: Dict[int, MonitorStatus] = {}
        for rid, values in self.read_pids_all([pid]).items():
            if pid in values:
                ci = None
                if this_cycle:
                    # Ignition type comes from PID 01 when we know it; PID 41 byte B bit 3
                    # is the same bit in the same layout, so the fallback is harmless.
                    known = self._pid01_cache.get(rid)
                    ci = known.compression_ignition if known else None
                status = decode_monitor_status(values[pid].raw, this_cycle=this_cycle, compression_ignition=ci)
                if not this_cycle:
                    self._pid01_cache[rid] = status
                out[rid] = status
        return out

    def monitor_status(self, *, this_cycle: bool = False, response_id: Optional[int] = None) -> MonitorStatus:
        per_ecu = self.monitor_status_all(this_cycle=this_cycle)
        rid, _ = self._pick({r: b"" for r in per_ecu}, response_id, MODE_CURRENT)
        return per_ecu[rid]

    # ------------------------------------------------------------- Mode 02

    def freeze_frame_all(self, pids: Optional[Iterable[int]] = None, frame: int = 0) -> Dict[int, Dict[int, ObdValue]]:
        """Mode 02 records ``[PID][frame][data]`` for every responder.

        PID 02 (the DTC that stored the frame) is always read first, *alone*
        (``02 02 <frame>``): ISO 15031-5 §7.2.4.2 / Table 7 e-f say an ECU without a
        stored frame answers ``00 00`` for PID 02 and stays silent for any request that
        names another data PID, so mixing PID 02 with data PIDs would hide the "no
        frame" answer. When no responder reports a stored frame the data PIDs are not
        requested at all and the result holds just ``{0x02: None}`` per ECU.

        ``pids=None`` then reads every PID the ECU lists in its Mode 02 bitmaps, three
        (PID, frame) pairs per request; an explicit list is read as given (bitmap PIDs
        are skipped, PID 02 is not repeated).
        """
        out = self._read_records_all(MODE_FREEZE, [[0x02]], frame)
        stored = {rid for rid, values in out.items() if 0x02 in values and values[0x02].value is not None}
        if not stored:
            return out
        if pids is None:
            per_ecu = self.supported_ids_all(MODE_FREEZE)
            wanted = sorted(set().union(*per_ecu.values())) if per_ecu else []
        else:
            wanted = list(pids)
        data_pids = [p for p in wanted if not P.is_support_id(p) and p != 0x02]
        chunks = [data_pids[i:i + MAX_FREEZE_PAIRS_PER_REQUEST]
                  for i in range(0, len(data_pids), MAX_FREEZE_PAIRS_PER_REQUEST)]
        for rid, values in self._read_records_all(MODE_FREEZE, chunks, frame).items():
            out.setdefault(rid, {}).update(values)
        return out

    def freeze_frame(self, pids: Optional[Iterable[int]] = None, frame: int = 0, *,
                     response_id: Optional[int] = None) -> Dict[int, ObdValue]:
        per_ecu = self.freeze_frame_all(pids, frame)
        rid, _ = self._pick({r: b"" for r in per_ecu}, response_id, MODE_FREEZE)
        return per_ecu[rid]

    # ------------------------------------------------------- Modes 03/07/0A

    def read_dtcs_all(self, mode: int = MODE_DTC_CONFIRMED) -> Dict[int, List[str]]:
        """``{response_id: [codes]}``; ECUs that reject the mode (unsupported) are left out."""
        if mode not in DTC_MODES:
            raise ValueError(f"mode 0x{mode:02X} is not a DTC read mode (03, 07 or 0A)")
        if mode == MODE_DTC_PERMANENT:
            # UNVERIFIED: the 4A payload layout (<count> + 2-byte DTCs like 43/47) is reported,
            # not read from a standard text.
            warn_unverified("mode0a-layout", "Mode 0A (permanent DTCs) parsed as '4A <count> <DTC pairs>' "
                                             "like Mode 03/07; confirm with a trace")
        out: Dict[int, List[str]] = {}
        for rid, data in self.query_all(bytes([mode])).items():
            out[rid] = parse_dtc_list(data)
        return out

    def read_dtcs(self, mode: int = MODE_DTC_CONFIRMED) -> List[str]:
        """Codes from every ECU, lowest response id first (duplicates kept per ECU)."""
        per_ecu = self.read_dtcs_all(mode)
        codes: List[str] = []
        for rid in sorted(per_ecu):
            codes.extend(per_ecu[rid])
        return codes

    def clear_dtcs(self) -> Dict[int, Optional[int]]:
        """Mode 04 (functional when the link is): ``{response_id: None | NRC}``.

        ``None`` = that ECU answered ``44`` (cleared); an NRC (``0x22`` with the engine
        running) = refused. Raises :class:`ObdTimeout` when no ECU answered at all.
        This is a *write* to every emissions ECU: the CLI requires ``--yes``.
        """
        responses = self.request_all(bytes([MODE_CLEAR]))
        if not responses:
            raise ObdTimeout(f"no ECU answered OBD mode 0x04 (clear) on 0x{self.link.tx_id:X}")
        out: Dict[int, Optional[int]] = {}
        for rid, data in responses.items():
            out[rid] = data[2] if data[0] == NEGATIVE_RESPONSE_SID else None
        self._pid01_cache.clear()
        return out

    # ------------------------------------------------------------- Mode 06

    def monitor_test_results_all(self, obdmids: Optional[Iterable[int]] = None) -> Dict[int, List[Mode06Result]]:
        """Mode 06 records per responder. ``obdmids=None`` walks each ECU's supported list.

        One OBDMID per request (ISO 15031-5 §7.6.1). Each id is requested once
        functionally, so two ECUs sharing an OBDMID both answer that request.
        """
        if obdmids is None:
            per_ecu = self.supported_ids_all(MODE_MONITOR_RESULTS)
            wanted = sorted(set().union(*per_ecu.values())) if per_ecu else []
        else:
            wanted = [m for m in obdmids if not P.is_support_id(m)]
        out: Dict[int, List[Mode06Result]] = {}
        for mid in wanted:
            for rid, data in self.query_all(bytes([MODE_MONITOR_RESULTS, mid])).items():
                out.setdefault(rid, []).extend(parse_mode06_records(data, rid))
        return out

    def monitor_test_results(self, obdmids: Optional[Iterable[int]] = None, *,
                             response_id: Optional[int] = None) -> List[Mode06Result]:
        per_ecu = self.monitor_test_results_all(obdmids)
        rid, _ = self._pick({r: b"" for r in per_ecu}, response_id, MODE_MONITOR_RESULTS)
        return per_ecu[rid]

    # ------------------------------------------------------------- Mode 09

    def vehicle_info_all(self, infotype: int) -> Dict[int, VehicleInfo]:
        """``09 <infotype>`` -> ``{response_id: VehicleInfo}`` (handles ``7F 09 78`` for CVN)."""
        if P.is_support_id(infotype):
            raise ValueError("use supported_infotypes_all() for the bitmap InfoTypes")
        out: Dict[int, VehicleInfo] = {}
        for rid, data in self.query_all(bytes([MODE_VEHICLE_INFO, infotype])).items():
            if len(data) < 2 or data[0] != infotype:
                log.warning("0x%X: malformed mode 09 reply %s", rid, data.hex(" "))
                continue
            nodi = data[1]
            out[rid] = VehicleInfo(infotype, P.infotype_name(infotype), nodi, bytes(data[2:]),
                                   decode_vehicle_info(infotype, nodi, data[2:]), rid)
        return out

    def vehicle_info(self, infotype: int, *, response_id: Optional[int] = None) -> VehicleInfo:
        per_ecu = self.vehicle_info_all(infotype)
        rid, _ = self._pick({r: b"" for r in per_ecu}, response_id, MODE_VEHICLE_INFO)
        return per_ecu[rid]

    def vin(self) -> str:
        return str(self.vehicle_info(0x02).value)

    # ------------------------------------------------------------ lifecycle

    def close(self) -> None:
        self.link.close()

    def __enter__(self) -> "ObdClient":
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()
