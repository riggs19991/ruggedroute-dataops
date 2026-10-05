"""
Simulated OBD-II ECU brains for the frame-level simulated vehicle.

:class:`SimulatedObdEcu` answers SAE J1979 Modes 01, 02, 03, 04, 06, 07, 09 (and 0A
on profiles that support permanent DTCs) exactly as ISO 15031-5 prescribes on CAN:
bitmap chains, multi-PID records, ``43 <count>`` DTC lists, ``7F 04 22`` while the
engine runs, 9-byte Mode 06 records, NODI-prefixed Mode 09 items, and *silence* for an
unsupported PID/OBDMID/InfoType (Table 7) unless ``nrc_on_unsupported`` is set to
mimic the UDS habit (``7F 01 12``) some VW ECUs are reported to have. Unsupported
services get ``7F SID 11``.

A brain only returns bytes; the ISO-TP framing is done by :class:`ObdNode` (a
:class:`~vagtune.transport.fakebus.UdsNode`). Where the standard allows a
``7F SID 78`` before the final reply (Mode 04 clear, Mode 09 CVN), the brain's
:meth:`SimulatedObdEcu.handle_all` returns the whole sequence and :class:`ObdNode`
sends the preambles first; :meth:`SimulatedObdEcu.handle` returns just the final
reply for links that deliver one response per request.

:class:`CompositeEcu` glues an OBD brain to a UDS brain on one node (Modes 01..0A to
OBD, everything else to UDS, or silence when there is no UDS brain - the R32's
ME7.1.1 speaks KWP over TP 2.0, not UDS, on 0x7E0).

Profiles mirror the owner's cars: ``r32-2008`` (BUB VR6, spark ignition, PID 13 =
0x33, six misfire OBDMIDs), ``golf-tdi-2012`` (CJAA, compression ignition with the
NMHC / NOx / boost / exhaust-gas-sensor / PM / EGR monitors, rail pressure, DPF
PIDs 7A/7C, permanent DTCs) and ``dq250-tcm`` (a DSG that answers a few PIDs,
CALID/CVN/ECU name and its own DTC list). The PID *sets* and values are plausible
fixtures, not captures of the real cars (the fact sheet lists them as Reported; the
real bitmaps are OPEN QUESTIONS 1-3 to be read with a trace).
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Set

from ..transport.fakebus import SimulatedVehicle, UdsNode
from . import pids as P

log = logging.getLogger(__name__)

NRC_SERVICE_NOT_SUPPORTED = 0x11
NRC_SUBFUNCTION_NOT_SUPPORTED = 0x12
NRC_CONDITIONS_NOT_CORRECT = 0x22
NRC_RESPONSE_PENDING = 0x78

OBD_SIDS = frozenset(range(0x01, 0x0B))


@dataclass
class Mode06Record:
    """One test result: ``tid``, ``uasid`` and raw 16-bit value / min / max."""
    tid: int
    uasid: int
    value: int
    min: int
    max: int

    def encode(self, obdmid: int) -> bytes:
        return bytes([obdmid, self.tid, self.uasid]) + b"".join(
            (v & 0xFFFF).to_bytes(2, "big") for v in (self.value, self.min, self.max))


def _negative(sid: int, nrc: int) -> bytes:
    return bytes([0x7F, sid, nrc])


# ==================================================================== profiles

def _profile_r32(ecu: "SimulatedObdEcu") -> None:
    """2008 R32 (BUB 3.2 VR6, ME7.1.1): spark ignition, two banks (PID 13 = 0x33)."""
    ecu.compression_ignition = False
    ecu.values = {
        0x03: b"\x02\x00", 0x04: b"\x33", 0x05: b"\x82", 0x06: b"\x80", 0x07: b"\x7E",
        0x08: b"\x81", 0x09: b"\x7F", 0x0B: b"\x21", 0x0C: b"\x0C\x80", 0x0D: b"\x00",
        0x0E: b"\x8E", 0x0F: b"\x4A", 0x10: b"\x01\x2C", 0x11: b"\x1A", 0x13: b"\x33",
        0x15: b"\x6E\x80", 0x19: b"\x70\x80", 0x1C: b"\x01", 0x1F: b"\x00\x78",
        0x21: b"\x00\x00", 0x2E: b"\x40", 0x30: b"\x05", 0x31: b"\x01\x2C", 0x33: b"\x63",
        0x34: b"\x80\x00\x80\x00", 0x38: b"\x80\x00\x80\x00",
        0x42: b"\x38\x40", 0x43: b"\x00\x33", 0x44: b"\x80\x00", 0x45: b"\x1A", 0x46: b"\x3C",
        0x47: b"\x1A", 0x49: b"\x0C", 0x4A: b"\x0C", 0x4C: b"\x1A", 0x4D: b"\x00\x00",
        0x4E: b"\x00\xF0", 0x51: b"\x01",
    }
    ecu.monitors_supported = {"misfire": True, "fuel_system": True, "components": True,
                              "catalyst": True, "evap": True, "o2_sensor": True, "o2_heater": True,
                              "egr_vvt": True}
    ecu.monitors_complete = {"catalyst": False, "evap": False}
    o2 = [Mode06Record(0x01, 0x0A, 0x0BB0, 0x0BB0, 0x0BB0), Mode06Record(0x05, 0x10, 0x48, 0x00, 0x64)]
    heater = [Mode06Record(0x80, 0x14, 12, 2, 20)]
    ecu.mode06 = {
        0x01: list(o2), 0x02: [Mode06Record(0x07, 0x0A, 0x0100, 0x0000, 0x0BB0)],
        0x05: list(o2), 0x06: [Mode06Record(0x07, 0x0A, 0x0120, 0x0000, 0x0BB0)],
        0x21: [Mode06Record(0x80, 0x24, 150, 75, 65535)], 0x22: [Mode06Record(0x80, 0x24, 0, 0, 0)],
        0x41: list(heater), 0x42: list(heater), 0x45: list(heater), 0x46: list(heater),
        0x81: [Mode06Record(0x80, 0xAF, 0x0010, 0xF830, 0x07D0)],
        0x82: [Mode06Record(0x80, 0xAF, 0xFFF0, 0xF830, 0x07D0)],
        0xA1: [Mode06Record(0x0B, 0x24, 0, 0, 0xFFFF), Mode06Record(0x0C, 0x24, 0, 0, 0xFFFF)],
    }
    for cyl in range(1, 7):
        ecu.mode06[0xA1 + cyl] = [Mode06Record(0x0B, 0x24, 0, 0, 25), Mode06Record(0x0C, 0x24, 0, 0, 25)]
    ecu.vin = "WVWKD71K58W000001"
    ecu.calids = ["022906032GR 0006"]
    ecu.cvns = [b"\x5A\x3C\x18\xF0"]
    ecu.ipt_infotype = 0x08
    ecu.ipt = [150, 300, 120, 150, 118, 150, 140, 150, 138, 150, 0, 0, 90, 150, 60, 150]
    ecu.ecu_name = "ECM-EngineControl"
    ecu.supports_permanent_dtcs = False
    ecu.cvn_pending_replies = 0
    ecu.clear_pending_replies = 0


def _profile_golf_tdi(ecu: "SimulatedObdEcu") -> None:
    """2012 Golf TDI (CJAA, EDC17CP14): compression ignition, DOC + DPF + LNT, no SCR."""
    ecu.compression_ignition = True
    ecu.values = {
        0x04: b"\x40", 0x05: b"\x7E", 0x0B: b"\x65", 0x0C: b"\x0D\x48", 0x0D: b"\x00",
        0x0F: b"\x3E", 0x10: b"\x03\x20", 0x11: b"\x0E", 0x13: b"\x03", 0x1C: b"\x01",
        0x1F: b"\x00\x3C", 0x21: b"\x00\x00", 0x23: b"\x00\xFA", 0x2C: b"\x66", 0x2D: b"\x80",
        0x30: b"\x08", 0x31: b"\x03\xE8", 0x33: b"\x64", 0x34: b"\xC0\x00\x80\x00",
        0x3C: b"\x03\xE8", 0x42: b"\x36\xB0", 0x43: b"\x00\x66", 0x45: b"\x0E", 0x46: b"\x3C",
        0x49: b"\x0E", 0x4A: b"\x0E", 0x4C: b"\x0E", 0x4D: b"\x00\x00", 0x4E: b"\x02\x58",
        0x51: b"\x04", 0x5C: b"\x80", 0x5E: b"\x00\x28",
        0x61: b"\x7D", 0x62: b"\x85", 0x63: b"\x01\x40",
        0x6B: b"\x01\x32\x00\x00\x00",
        0x6D: b"\x03\x00\xFA\x00\xF8\x50\x00\x00\x00\x00\x00",
        0x70: b"\x07\x0C\xA0\x0C\xB0\x00\x00\x00\x00\x02",
        0x71: b"\x07\x80\x80\x00\x00\x02",
        0x73: b"\x01\x29\x04\x00\x00",
        0x74: b"\x01\x0B\xB8\x00\x00",
        0x78: b"\x03\x0B\xB8\x0D\xAC\x00\x00\x00\x00",
        0x7A: b"\x07\x00\x32\x29\x04\x28\xD2",
        0x7C: b"\x03\x0D\xAC\x0D\x48\x00\x00\x00\x00",
        0x7F: b"\x03\x00\x01\xE2\x40\x00\x00\x3A\x98\x00\x00\x00\x00",
        0x83: b"\x01\x00\x50\x00\x00\x00\x00\x00\x00",
        0x8B: b"\x7F\x00\x80\x01\xE0\x01\x90",
        0x92: b"\x07\x07",
    }
    ecu.monitors_supported = {"misfire": True, "components": True,
                              "nmhc_catalyst": True, "nox_scr_aftertreatment": True, "boost_pressure": True,
                              "exhaust_gas_sensor": True, "pm_filter": True, "egr_vvt": True}
    ecu.monitors_complete = {"nox_scr_aftertreatment": False}
    ecu.mode06 = {
        0x01: [Mode06Record(0x80, 0x1E, 0x8013, 0x7000, 0x9000)],
        0x31: [Mode06Record(0x80, 0xAF, 0x0064, 0xF830, 0x07D0)],
        0x85: [Mode06Record(0x80, 0xAF, 0x0032, 0xF830, 0x07D0)],
        0x90: [Mode06Record(0x80, 0x30, 0xC000, 0x4000, 0xFFFF)],
        0xA1: [Mode06Record(0x0B, 0x24, 0, 0, 0xFFFF)],
        0xB0: [Mode06Record(0x80, 0xFC, 0x0032, 0xFFCE, 0x07D0)],
    }
    ecu.vin = "WVWDM7AJ4CW000002"
    ecu.calids = ["03L906018MK 9978"]
    ecu.cvns = [b"\x12\x34\x56\x78"]
    ecu.ipt_infotype = 0x0B
    ecu.ipt = [400, 520, 200, 400, 210, 400, 180, 400, 150, 400, 300, 400, 390, 400, 380, 400, 0, 0]
    ecu.ecu_name = "ECM-EngineControl"
    ecu.supports_permanent_dtcs = True
    ecu.cvn_pending_replies = 1
    ecu.clear_pending_replies = 1


def _profile_dq250_tcm(ecu: "SimulatedObdEcu") -> None:
    """A DQ250 (02E) DSG that answers OBD on 0x7E1/0x7E9.

    Whether the real DSG answers functional OBD requests is *Reported* (medium
    confidence) in the fact sheet; this fixture exists so multi-responder handling is
    exercised, not as a claim about the car.
    """
    ecu.compression_ignition = False
    ecu.values = {0x0D: b"\x00", 0x1C: b"\x01", 0x42: b"\x38\x40"}
    ecu.monitors_supported = {"components": True}
    ecu.monitors_complete = {}
    ecu.mode06 = {}
    ecu.supports_mode06 = False
    ecu.vin = None
    ecu.calids = ["02E300053E 1211"]
    ecu.cvns = [b"\x00\xA1\xB2\xC3"]
    ecu.ipt_infotype = None
    ecu.ipt = []
    ecu.ecu_name = "TCM-TransmissionCtl"
    ecu.supports_permanent_dtcs = False
    ecu.cvn_pending_replies = 0
    ecu.clear_pending_replies = 0


PROFILES: Dict[str, Callable[["SimulatedObdEcu"], None]] = {
    "r32-2008": _profile_r32,
    "golf-tdi-2012": _profile_golf_tdi,
    "dq250-tcm": _profile_dq250_tcm,
}


# ======================================================================= brain

class SimulatedObdEcu:
    """A scriptable SAE J1979 responder (bytes in, bytes out; no framing)."""

    def __init__(self, profile: str = "r32-2008") -> None:
        if profile not in PROFILES:
            raise KeyError(f"unknown OBD profile {profile!r}; known: {', '.join(sorted(PROFILES))}")
        self.profile = profile
        self.compression_ignition = False
        #: Mode 01 raw data bytes per PID (bitmaps, 01 and 41 are computed).
        self.values: Dict[int, bytes] = {}
        self.monitors_supported: Dict[str, bool] = {}
        self.monitors_complete: Dict[str, bool] = {}
        #: monitors *disabled* this cycle (PID 41 "enabled" = supported and not disabled)
        self.monitors_disabled_this_cycle: Set[str] = set()
        self.dtcs: List[str] = []
        self.pending_dtcs: List[str] = []
        self.permanent_dtcs: List[str] = []
        self.mil: Optional[bool] = None            # None -> derived from the confirmed list
        self.engine_running = False
        self.freeze_dtc: Optional[str] = None      # None -> first confirmed DTC, or none
        #: frame number -> {pid: data}; frame 0 defaults to a snapshot of ``values``
        self.freeze_frames: Dict[int, Dict[int, bytes]] = {}
        self.mode06: Dict[int, List[Mode06Record]] = {}
        self.supports_mode06 = True
        self.vin: Optional[str] = None
        self.calids: List[str] = []
        self.cvns: List[bytes] = []
        self.ipt_infotype: Optional[int] = None
        self.ipt: List[int] = []
        self.ecu_name: Optional[str] = None
        self.supports_permanent_dtcs = False
        self.cvn_pending_replies = 0
        self.clear_pending_replies = 0
        #: answer ``7F SID 12`` for an unsupported PID/OBDMID/InfoType instead of silence
        self.nrc_on_unsupported = False
        self.requests: List[bytes] = []
        self.clears = 0
        PROFILES[profile](self)

    # ----------------------------------------------------------- derived

    @property
    def mil_on(self) -> bool:
        return bool(self.dtcs) if self.mil is None else self.mil

    def supported_pids(self) -> Set[int]:
        return {0x01, 0x41} | set(self.values)

    def freeze_frame(self, frame: int) -> Optional[Dict[int, bytes]]:
        if frame in self.freeze_frames:
            return self.freeze_frames[frame]
        if frame == 0 and (self.freeze_dtc or self.dtcs):
            return {pid: data for pid, data in self.values.items() if pid <= 0x60}
        return None

    def freeze_dtc_bytes(self) -> bytes:
        code = self.freeze_dtc or (self.dtcs[0] if self.dtcs else None)
        return P.encode_dtc(code) if code else b"\x00\x00"

    def supported_freeze_pids(self) -> Set[int]:
        """The Mode 02 bitmap is constant: it lists what a frame *would* hold (ISO Table 7
        e/f: without a stored frame the ECU still answers the bitmap PIDs and PID 02)."""
        return {0x02} | {pid for pid in self.values if pid <= 0x60}

    def supported_obdmids(self) -> Set[int]:
        return set(self.mode06) if self.supports_mode06 else set()

    def supported_infotypes(self) -> Set[int]:
        ids: Set[int] = set()
        if self.vin: ids.add(0x02)
        if self.calids: ids.add(0x04)
        if self.cvns: ids.add(0x06)
        if self.ipt_infotype and self.ipt: ids.add(self.ipt_infotype)
        if self.ecu_name: ids.add(0x0A)
        return ids

    # ---------------------------------------------------------- dispatch

    def handle(self, request: bytes) -> Optional[bytes]:
        """Final reply only (``None`` = stay silent)."""
        replies = self.handle_all(request)
        return replies[-1] if replies else None

    def handle_all(self, request: bytes) -> List[bytes]:
        """Every reply in order: ``7F SID 78`` preambles first, then the final one."""
        if not request:
            return []
        self.requests.append(bytes(request))
        sid = request[0]
        if sid == 0x01:
            return self._wrap(self._mode01(request))
        if sid == 0x02:
            return self._wrap(self._mode02(request))
        if sid in (0x03, 0x07):
            codes = self.dtcs if sid == 0x03 else self.pending_dtcs
            return [self._dtc_list(sid, codes)]
        if sid == 0x0A:
            if not self.supports_permanent_dtcs:
                return [_negative(sid, NRC_SERVICE_NOT_SUPPORTED)]
            return [self._dtc_list(sid, self.permanent_dtcs)]
        if sid == 0x04:
            return self._mode04()
        if sid == 0x06:
            if not self.supports_mode06:
                return [_negative(sid, NRC_SERVICE_NOT_SUPPORTED)]
            return self._wrap(self._mode06(request))
        if sid == 0x09:
            return self._mode09(request)
        return [_negative(sid, NRC_SERVICE_NOT_SUPPORTED)]

    @staticmethod
    def _wrap(reply: Optional[bytes]) -> List[bytes]:
        return [] if reply is None else [reply]

    def _unsupported(self, sid: int) -> Optional[bytes]:
        return _negative(sid, NRC_SUBFUNCTION_NOT_SUPPORTED) if self.nrc_on_unsupported else None

    # --------------------------------------------------------- bitmaps

    @staticmethod
    def _bitmap_record(base: int, supported: Set[int]) -> Optional[bytes]:
        """``[base][A B C D]`` for ``base`` or ``None`` when nothing lies at/after it
        (Annex A: no response for an unsupported range unless a later range is used)."""
        chained = set(supported)
        for b in P.SUPPORT_BASES[1:]:
            if any(i > b for i in supported):
                chained.add(b)
        if base != 0x00 and base not in chained:
            return None
        return bytes([base]) + P.build_supported(base, sorted(chained))

    # --------------------------------------------------------- Mode 01

    def _monitor_status(self, this_cycle: bool) -> bytes:
        if this_cycle:
            supported = {n: v and n not in self.monitors_disabled_this_cycle
                         for n, v in self.monitors_supported.items()}
        else:
            supported = dict(self.monitors_supported)
        complete = {n: self.monitors_complete.get(n, True) for n in supported}
        return P.encode_monitor_status(mil=self.mil_on, dtc_count=len(self.dtcs),
                                       compression_ignition=self.compression_ignition,
                                       supported=supported, complete=complete, this_cycle=this_cycle)

    def _pid_data(self, pid: int) -> Optional[bytes]:
        if P.is_support_id(pid):
            return self._bitmap_record(pid, self.supported_pids())
        if pid == 0x01:
            return bytes([pid]) + self._monitor_status(False)
        if pid == 0x41:
            return bytes([pid]) + self._monitor_status(True)
        if pid in self.values:
            return bytes([pid]) + self.values[pid]
        return None

    def _mode01(self, request: bytes) -> Optional[bytes]:
        if not 2 <= len(request) <= 7:
            return _negative(0x01, NRC_SUBFUNCTION_NOT_SUPPORTED)
        body = b"".join(r for r in (self._pid_data(pid) for pid in request[1:]) if r is not None)
        if not body:
            return self._unsupported(0x01)
        return b"\x41" + body

    # --------------------------------------------------------- Mode 02

    def _mode02(self, request: bytes) -> Optional[bytes]:
        """ISO 15031-5 §7.2.4.2 / Table 7 e-h, strictly: without a stored frame the ECU
        answers only the bitmap PIDs and PID 02 (``00 00``) and is *silent* for any
        request naming another PID - even when PID 02 is in the same request."""
        pairs = request[1:]
        if len(pairs) == 0 or len(pairs) % 2 or len(pairs) > 6:
            return _negative(0x02, NRC_SUBFUNCTION_NOT_SUPPORTED)
        for i in range(0, len(pairs), 2):
            pid, frame = pairs[i], pairs[i + 1]
            if not P.is_support_id(pid) and pid != 0x02 and self.freeze_frame(frame) is None:
                return None
        body = b""
        for i in range(0, len(pairs), 2):
            pid, frame = pairs[i], pairs[i + 1]
            if P.is_support_id(pid):
                rec = self._bitmap_record(pid, self.supported_freeze_pids())
                if rec is not None:
                    body += rec[:1] + bytes([frame]) + rec[1:]
                continue
            if pid == 0x02:
                has_frame = self.freeze_frame(frame) is not None
                body += bytes([pid, frame]) + (self.freeze_dtc_bytes() if has_frame else b"\x00\x00")
                continue
            stored = self.freeze_frame(frame)
            if stored and pid in stored:
                body += bytes([pid, frame]) + stored[pid]
        if not body:
            return self._unsupported(0x02)
        return b"\x42" + body

    # ------------------------------------------------------ Modes 03/07/0A

    @staticmethod
    def _dtc_list(sid: int, codes: Sequence[str]) -> bytes:
        return bytes([sid + 0x40, len(codes)]) + b"".join(P.encode_dtc(c) for c in codes)

    # --------------------------------------------------------- Mode 04

    def _mode04(self) -> List[bytes]:
        if self.engine_running:
            return [_negative(0x04, NRC_CONDITIONS_NOT_CORRECT)]
        out = [_negative(0x04, NRC_RESPONSE_PENDING)] * self.clear_pending_replies
        self.dtcs.clear()
        self.pending_dtcs.clear()
        self.mil = None
        self.freeze_dtc = None
        self.freeze_frames.clear()
        self.monitors_complete = {n: False for n in self.monitors_supported
                                  if n not in P.CONTINUOUS_MONITORS}
        for records in self.mode06.values():
            for r in records:
                r.value = r.min = r.max = 0
        for pid in (0x21, 0x30, 0x31, 0x4D, 0x4E):
            if pid in self.values:
                self.values[pid] = bytes(len(self.values[pid]))
        self.clears += 1
        return out + [b"\x44"]

    # --------------------------------------------------------- Mode 06

    def _mode06(self, request: bytes) -> Optional[bytes]:
        mids = request[1:]
        if not 1 <= len(mids) <= 6:
            return _negative(0x06, NRC_SUBFUNCTION_NOT_SUPPORTED)
        if all(P.is_support_id(m) for m in mids):
            body = b"".join(r for r in (self._bitmap_record(m, self.supported_obdmids()) for m in mids)
                            if r is not None)
            return b"\x46" + body if body else self._unsupported(0x06)
        if len(mids) != 1:
            return _negative(0x06, NRC_SUBFUNCTION_NOT_SUPPORTED)
        mid = mids[0]
        if mid not in self.mode06:
            return self._unsupported(0x06)
        return b"\x46" + b"".join(r.encode(mid) for r in self.mode06[mid])

    # --------------------------------------------------------- Mode 09

    def _mode09(self, request: bytes) -> List[bytes]:
        its = request[1:]
        if not 1 <= len(its) <= 6:
            return [_negative(0x09, NRC_SUBFUNCTION_NOT_SUPPORTED)]
        if all(P.is_support_id(i) for i in its):
            body = b"".join(r for r in (self._bitmap_record(i, self.supported_infotypes()) for i in its)
                            if r is not None)
            return [b"\x49" + body] if body else self._wrap(self._unsupported(0x09))
        if len(its) != 1:
            return [_negative(0x09, NRC_SUBFUNCTION_NOT_SUPPORTED)]
        it = its[0]
        if it not in self.supported_infotypes():
            return self._wrap(self._unsupported(0x09))
        if it == 0x02:
            assert self.vin is not None
            return [b"\x49\x02\x01" + self.vin.encode("ascii")[:17].ljust(17, b"\0")]
        if it == 0x04:
            items = b"".join(c.encode("ascii")[:16].ljust(16, b"\0") for c in self.calids)
            return [bytes([0x49, 0x04, len(self.calids)]) + items]
        if it == 0x06:
            pre = [_negative(0x09, NRC_RESPONSE_PENDING)] * self.cvn_pending_replies
            self.cvn_pending_replies = 0          # method #1: computed once, then immediate
            return pre + [bytes([0x49, 0x06, len(self.cvns)]) + b"".join(c[-4:].rjust(4, b"\0") for c in self.cvns)]
        if it == self.ipt_infotype:
            return [bytes([0x49, it, len(self.ipt)]) + b"".join(v.to_bytes(2, "big") for v in self.ipt)]
        if it == 0x0A:
            assert self.ecu_name is not None
            acronym, _, text = self.ecu_name.partition("-")
            data = acronym.encode("ascii")[:4].ljust(4, b"\0") + b"-" + text.encode("ascii")[:15].ljust(15, b"\0")
            return [b"\x49\x0A\x01" + data]
        return self._wrap(self._unsupported(0x09))


# =================================================================== composite

class CompositeEcu:
    """One node brain that answers OBD (SIDs 01..0A) *and* UDS (everything else).

    ``uds_brain=None`` makes the node silent for non-OBD services, which is what a
    KWP-only engine ECU (the R32's ME7.1.1) does on 0x7E0.
    """

    def __init__(self, obd_brain: Any, uds_brain: Any = None) -> None:
        if not hasattr(obd_brain, "handle"):
            raise TypeError("obd_brain must expose handle(bytes) -> bytes | None")
        if uds_brain is not None and not hasattr(uds_brain, "handle"):
            raise TypeError("uds_brain must expose handle(bytes) -> bytes | None")
        self.obd = obd_brain
        self.uds = uds_brain

    def _is_obd(self, request: bytes) -> bool:
        return bool(request) and request[0] in OBD_SIDS

    def handle(self, request: bytes) -> Optional[bytes]:
        if self._is_obd(request):
            return self.obd.handle(request)
        if self.uds is None:
            return None
        return self.uds.handle(request)

    def handle_all(self, request: bytes) -> List[bytes]:
        if self._is_obd(request):
            if hasattr(self.obd, "handle_all"):
                return list(self.obd.handle_all(request))
            r = self.obd.handle(request)
            return [] if r is None else [r]
        if self.uds is None:
            return []
        if hasattr(self.uds, "handle_all"):
            return list(self.uds.handle_all(request))
        r = self.uds.handle(request)
        return [] if r is None else [r]


# ======================================================================= node

class ObdNode(UdsNode):
    """A :class:`UdsNode` that also sends the ``7F SID 78`` preambles a brain's
    ``handle_all()`` returns before the final reply (Mode 04 clear, Mode 09 CVN)."""

    def _handle(self, request: bytes) -> Optional[bytes]:
        self.requests_served += 1
        try:
            if hasattr(self.ecu, "handle_all"):
                replies = list(self.ecu.handle_all(request))
            else:
                r = self.ecu.handle(request)
                replies = [] if r is None else [r]
        except Exception:
            self.handler_errors += 1
            log.exception("node %s: handler raised on request %s; answering generalReject",
                          self.name, request.hex(" "))
            return bytes([0x7F, request[0], 0x10]) if request else None
        if not replies:
            return None
        for preamble in replies[:-1]:
            self.link.send(preamble)
        return replies[-1]


def add_obd_nodes(vehicle: SimulatedVehicle, *, engine_profile: str, tcm_profile: Optional[str] = "dq250-tcm",
                  engine_uds: Any = None, tcm_uds: Any = None,
                  engine_name: str = "obd-engine", tcm_name: str = "obd-tcm") -> Dict[str, SimulatedObdEcu]:
    """Put an engine (0x7E0/0x7E8) and optionally a TCM (0x7E1/0x7E9) OBD node on ``vehicle``.

    If another slice already placed a node on one of those request ids, that node's
    brain is wrapped in a :class:`CompositeEcu` instead of adding a second responder
    (two nodes answering one id would double every reply). Returns the OBD brains by
    role (``"engine"``, ``"tcm"``) so tests can script them.
    """
    brains: Dict[str, SimulatedObdEcu] = {}
    plan = [("engine", engine_profile, engine_uds, 0x7E0, 0x7E8, engine_name)]
    if tcm_profile is not None:
        plan.append(("tcm", tcm_profile, tcm_uds, 0x7E1, 0x7E9, tcm_name))
    for role, profile, uds_brain, req, resp, name in plan:
        brain = SimulatedObdEcu(profile)
        existing = next((n for n in vehicle.nodes
                         if isinstance(n, UdsNode) and n.request_id == req), None)
        if existing is not None:
            log.debug("preset %s: wrapping existing node %s with OBD profile %s", vehicle.preset,
                      existing.name, profile)
            existing.ecu = CompositeEcu(brain, existing.ecu)
        else:
            vehicle.add_node(ObdNode(vehicle.bus, CompositeEcu(brain, uds_brain),
                                     request_id=req, response_id=resp, name=name))
        brains[role] = brain
    return brains


def _hook_r32(vehicle: SimulatedVehicle) -> None:
    add_obd_nodes(vehicle, engine_profile="r32-2008", tcm_profile="dq250-tcm")


def _hook_golf_tdi(vehicle: SimulatedVehicle) -> None:
    add_obd_nodes(vehicle, engine_profile="golf-tdi-2012", tcm_profile="dq250-tcm")


SimulatedVehicle.register_preset_hook("r32-2008", _hook_r32)
SimulatedVehicle.register_preset_hook("golf-tdi-2012", _hook_golf_tdi)
