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
MAX_PIDS_PER_REQUEST = 6          # ISO 15031-5 §7.1.1
MAX_FREEZE_PAIRS_PER_REQUEST = 3  # ISO 15031-5 Table 137


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
    """P2 = collection window for all responders; P2* = per-responder window after 0x78."""
    p2: float = 0.25
    p2_star: float = 5.0
    pending_limit: int = 30


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
        ``batch_bitmaps=True`` requests the supported-ID bitmaps six at a time
        (``01 00 20 40 60 80 A0``, legal per ISO 15031-5 Annex A); the default walks
        one bitmap per request, which every ECU since 1996 handles.
        """
        self.link = link
        self.timing = timing or ObdTiming()
        self.batch_bitmaps = batch_bitmaps
        self.functional = link.tx_id in FUNCTIONAL_IDS
        #: response ids seen answering positively; used to end the P2 window early.
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

    def request_all(self, payload: bytes, *, window: Optional[float] = None,
                    expect: Optional[Iterable[int]] = None) -> Dict[int, bytes]:
        """Send ``payload`` once and collect every responder's *final* reply.

        Returns ``{response_id: payload}`` with the raw payload (positive ``SID+0x40 ...``
        or final negative ``7F SID NRC``). ``7F SID 78`` extends that responder's
        deadline to P2* and is not returned. The window closes after ``window`` (P2)
        unless a responder is still pending, or earlier when every id in ``expect``
        (default: the known responders on a functional link, the ``rx_id`` on a
        physical one) has answered. Only the first final reply per id is kept; a
        duplicate (two simulated nodes on one id, a chatty gateway) is logged.
        """
        if not payload:
            raise ValueError("OBD request must carry at least the mode byte")
        sid = payload[0]
        window = self.timing.p2 if window is None else window
        if expect is None:
            expected: Set[int] = set(self.responders) if self.functional else {self.link.rx_id}
        else:
            expected = set(expect)
        results: Dict[int, bytes] = {}
        pending: Dict[int, float] = {}
        pending_count: Dict[int, int] = {}
        with self._lock:
            self.last_negatives = {}
            self.link.flush_rx()
            self.link.send(payload)
            deadline = time.monotonic() + window
            while True:
                now = time.monotonic()
                until = max([deadline] + list(pending.values()))
                remaining = until - now
                if remaining <= 0:
                    break
                if expected and not pending and expected <= set(results):
                    break
                try:
                    data = self.link.recv(min(remaining, 0.5))
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
                        log.warning("duplicate reply from 0x%X to mode %02X ignored: %s", rid, sid, data.hex(" "))
                        continue
                    results[rid] = bytes(data)
                    self.last_negatives[rid] = (sid, data[2])
                    continue
                if data[0] != sid + 0x40:
                    log.debug("ignoring stray payload %s while waiting for mode %02X", data.hex(" "), sid)
                    continue
                pending.pop(rid, None)
                if rid in results:
                    log.warning("duplicate reply from 0x%X to mode %02X ignored: %s", rid, sid, data.hex(" "))
                    continue
                results[rid] = bytes(data)
                if self.functional:
                    self.responders.add(rid)
        if pending:
            log.warning("mode %02X: responder(s) %s never completed after response-pending",
                        sid, ", ".join(f"0x{r:X}" for r in pending))
        return results

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
        """``01 00`` functionally (the ISO 15765-4 init / ping); returns the responder ids."""
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
        (same bitmap scheme, ISO 15031-5 Annex A). The bitmap ids themselves are
        excluded from the returned sets. Results are cached per (mode, responder).
        """
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
            absorb(self.query_all(self._bitmap_request(mode, P.SUPPORT_BASES[:6]), expect=()))
            if any(0xC0 in ids for ids in result.values()):
                absorb(self.query_all(self._bitmap_request(mode, P.SUPPORT_BASES[6:])))
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

    def _read_mode01_all(self, pids: Sequence[int]) -> Dict[int, Dict[int, ObdValue]]:
        out: Dict[int, Dict[int, ObdValue]] = {}
        for chunk in self._chunk_pids(list(pids)):
            for rid, data in self.query_all(bytes([MODE_CURRENT]) + bytes(chunk)).items():
                for pid, _frame, body in walk_records(data):
                    if pid not in chunk:
                        log.warning("0x%X answered with PID %02X that was not requested", rid, pid)
                    out.setdefault(rid, {})[pid] = self._make_value(MODE_CURRENT, pid, body, rid, None)
        return out

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

        ``pids=None`` reads every PID the ECU lists in its Mode 02 bitmaps (always
        including PID 02, the DTC that stored the frame). Three (PID, frame) pairs per
        request. An ECU without a stored frame answers only the bitmap PIDs and PID 02
        (= ``00 00``), so the result may hold just PID 02 -> ``None``.
        """
        if pids is None:
            per_ecu = self.supported_ids_all(MODE_FREEZE)
            wanted = sorted(set().union(*per_ecu.values()) | {0x02}) if per_ecu else [0x02]
        else:
            wanted = list(pids)
        data_pids = [p for p in wanted if not P.is_support_id(p)]
        out: Dict[int, Dict[int, ObdValue]] = {}
        for i in range(0, len(data_pids), MAX_FREEZE_PAIRS_PER_REQUEST):
            chunk = data_pids[i:i + MAX_FREEZE_PAIRS_PER_REQUEST]
            req = bytes([MODE_FREEZE]) + b"".join(bytes([p, frame & 0xFF]) for p in chunk)
            for rid, data in self.query_all(req).items():
                for pid, frno, body in walk_records(data, with_frame=True):
                    out.setdefault(rid, {})[pid] = self._make_value(MODE_FREEZE, pid, body, rid, frno)
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
            out[rid] = VehicleInfo(infotype, P.INFOTYPE_NAMES.get(infotype, f"InfoType {infotype:02X}"),
                                   nodi, bytes(data[2:]), decode_vehicle_info(infotype, nodi, data[2:]), rid)
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
