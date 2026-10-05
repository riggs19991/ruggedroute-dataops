"""
Simulated KWP2000 modules ("brains") for tests and the simulated vehicle.

:class:`SimulatedKwpEcu` is the service state machine: ``handle(request) ->
response | None`` (the module's *final* answer) and ``handle_all(request) ->
[preambles..., final]`` for links that deliver several messages per request (a
``7F xx 78`` responsePending followed by the real reply, which a
:class:`~vagtune.transport.tp20_sim.Tp20Node` sends one after the other). The wire
behaviour is the verified KWP2000-over-TP 2.0 dialect of ``docs/PROTOCOL_FACTS.md``
§4 / §7.5 / §7.7 / §7.8 / §7.10: ``10 89`` only, ``1A 9B/91/9A/9F`` records built
byte-exact, ``21 <group>`` with 3-byte fields (8 fields = 26-byte replies on both
engines, like the real PQ35 engine replies), ``18 02/00 FF 00`` -> ``58 n`` + 3-byte records, ``14 FF 00``
-> ``54 FF 00``, ``23 addr(3) n`` -> ``63 data``, ``31 B8 00 00`` capability list,
and the right negative response for everything else (``7F 1A 11`` unknown ident
option, ``7F 21 31`` unknown group, ``7F 10 11`` any session but 0x89, ``7F 27 11``
seed/key, ``7F 3B 33`` / ``7F 31 33`` for writes without a login, ``7F SID 11``
unsupported service) - never silent success.

The brains mirror the owner's cars with the strings VCDS printed (registry §8 A,
IMPLEMENTATION_NOTES (a)): :class:`Me7Brain` (R32 engine 022 906 032 KR),
:class:`Edc17Brain` (Golf TDI engine 03L 906 019 EE), :class:`Dq250Brain` (02E),
:class:`HaldexBrain` (1K0 907 554 L), :class:`GatewayBrain` (1K0 907 530 L, long
coding ``ED831F075003020000`` = the R32's 22-module installation list) and a generic
:class:`BodyBrain`. Group *contents* follow the verified group layouts where the
registry has them (standardized gasoline groups, CJAA 011/099/108/240/241/086/089,
DQ250 019) with plausible values; where the registry only reports a layout (Haldex
groups, the ``71 BA`` adaptation reply, the ``5A 9A`` / ``5A 9F`` records, the WSC
packing) the simulator follows the reported form and says so - the *client* side
flags those as UNVERIFIED, the simulator just has to be consistent with the facts.

Preset hooks put the brains behind TP 2.0 responders on the ``r32-2008`` and
``golf-tdi-2012`` vehicles (lazy import of :mod:`vagtune.transport.tp20_sim`; a
missing TP 2.0 simulator is logged, not fatal). The tester-TX id each responder
grants is the registry's value where a capture exists (0x740 engine, 0x760 DSG,
0x7A8 EPS, 0x764 Haldex, 0x32E gateway prediction); every *simulator-chosen* id
lives in 0x7F0..0x7FF, outside the ODIS UDS table (0x700..0x7DD), legislated OBD
(0x7DF..0x7EF), the TP 2.0 setup replies (0x200..0x2FF) and the tester RX pool
(0x300..0x30F), so a KWP responder never swallows another simulated module's
ISO-TP frames (a Golf HVAC on 0x746/0x7B0 once killed the ABS channel that way).
:func:`add_kwp_nodes` also refuses an id already used by a node on the vehicle.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Optional, Sequence, Set, Tuple, Union

from ..transport.fakebus import SimulatedVehicle
from . import services as S

log = logging.getLogger(__name__)

Response = Union[bytes, Sequence[bytes], None]


# ================================================================= record builders

def pack_wsc_block(wsc: int, importer: int, equipment: int) -> bytes:
    """The REPORTED 48-bit packing (``wsc | importer << 17 | equipment << 27``, big
    endian). The simulator uses it so its ``5A 9B`` bytes decode to the VCDS "Shop #"
    lines of the real scans under that rule; the client flags the rule UNVERIFIED."""
    v = (wsc & 0x1FFFF) | ((importer & 0x3FF) << 17) | ((equipment & 0x1FFFFF) << 27)
    return v.to_bytes(6, "big")


def build_ident_9b(part_number: str, sw_version: str, coding_type: int, short_coding: int,
                   wsc_block: bytes, component: str, *, component_width: int = 20) -> bytes:
    """Byte-exact ``5A 9B`` body (verified offsets): 11-char part number, 0x20, 4-digit
    software version, coding type, 0x00, short coding BE, 6-byte WSC block, component
    text space-padded (the real records pad to 20 characters)."""
    if len(part_number) > 11:
        raise ValueError("part number is at most 11 characters")
    if len(sw_version) != 4:
        raise ValueError("software version is 4 ASCII digits")
    if len(wsc_block) != 6:
        raise ValueError("WSC block is 6 bytes")
    body = part_number.ljust(11).encode("ascii") + b"\x20" + sw_version.encode("ascii")
    body += bytes([coding_type, 0x00]) + (short_coding & 0xFFFF).to_bytes(2, "big") + bytes(wsc_block)
    body += component.ljust(component_width).encode("latin-1")
    return body


def build_length_prefixed(records: Sequence[bytes]) -> bytes:
    """``len data ... FF`` with ``len`` counting itself (``5A 91`` / ``5A 9F`` form)."""
    out = bytearray()
    for rec in records:
        if len(rec) + 1 > 0xFE:
            raise ValueError("record too long for a length byte")
        out.append(len(rec) + 1)
        out += bytes(rec)
    out.append(0xFF)
    return bytes(out)


def build_ident_9a(wsc_block: bytes, sw_version: str, coding: bytes) -> bytes:
    """``5A 9A`` body in the REPORTED single-sample layout: ``[wsc6][sw4][10][len
    counting itself][coding][FF]`` (VDS sample ``... 10 09 01 03 00 0C 18 0F 01 60 FF``)."""
    return bytes(wsc_block) + sw_version.encode("ascii") + bytes([S.CODING_TYPE_LONG, len(coding) + 1]) \
        + bytes(coding) + b"\xFF"


def fields(*triplets: Tuple[int, int, int]) -> bytes:
    """``(formula, A, B)`` triplets -> field bytes."""
    out = bytearray()
    for f, a, b in triplets:
        out += bytes([f & 0xFF, a & 0xFF, b & 0xFF])
    return bytes(out)


def text_field(text: str) -> bytes:
    """A ``5F <len> <ASCII>`` field."""
    data = text.encode("latin-1")
    return bytes([0x5F, len(data)]) + data


FILLER = (0x25, 0x00, 0x00)   # the ``25 00 00`` empty field real engines send


# ================================================================= brain data

@dataclass
class KwpBrain:
    """Everything a :class:`SimulatedKwpEcu` needs to answer like one module."""
    name: str
    part_number: str
    sw_version: str
    component: str
    coding_type: int = S.CODING_TYPE_NONE
    short_coding: int = 0
    long_coding: bytes = b""
    wsc: Tuple[int, int, int] = (0, 0, 0)
    hardware_number: str = ""
    groups: Dict[int, bytes] = field(default_factory=dict)
    dtcs: List[Tuple[int, int]] = field(default_factory=list)
    capabilities: List[int] = field(default_factory=list)
    adaptation: Dict[int, int] = field(default_factory=dict)
    ram: bytes = b""
    ram_base: int = 0
    installation_list: Optional[bytes] = None    # ``5A 9F`` body (gateway only)
    pending_once_on: Set[int] = field(default_factory=set)   # ident options answered 7F 1A 78 first
    extra_ident: Dict[int, bytes] = field(default_factory=dict)

    @property
    def wsc_block(self) -> bytes:
        return pack_wsc_block(*self.wsc)

    @property
    def ident_9b(self) -> bytes:
        return build_ident_9b(self.part_number, self.sw_version, self.coding_type, self.short_coding,
                              self.wsc_block, self.component)

    @property
    def ident_91(self) -> bytes:
        hw = (self.hardware_number or self.part_number).ljust(13)
        return build_length_prefixed([hw.encode("ascii")])

    @property
    def ident_9a(self) -> Optional[bytes]:
        if self.coding_type != S.CODING_TYPE_LONG:
            return None
        return build_ident_9a(self.wsc_block, self.sw_version, self.long_coding)


# ================================================================= the ECU

class SimulatedKwpEcu:
    """KWP2000 service machine around a :class:`KwpBrain`.

    Test hooks: ``busy_once`` - SIDs answered ``7F SID 21`` the first time they are
    seen; ``pending_count`` - how many ``7F 1A 78`` preambles ``handle_all`` emits
    before a pending-flagged ident option (default 1).
    """

    def __init__(self, brain: KwpBrain) -> None:
        self.brain = brain
        self.session: Optional[int] = None
        self.busy_once: Set[int] = set()
        self.pending_count = 1
        self.requests: List[bytes] = []
        self.adaptation_open = False
        self.adaptation_channel: Optional[int] = None
        self.basic_settings_open = False
        self.logged_in = False
        self.cleared = 0

    # -- entry points ----------------------------------------------------------

    def handle(self, request: bytes) -> Optional[bytes]:
        """The module's final answer to ``request`` (``None`` for an empty request)."""
        replies = self.handle_all(request)
        return replies[-1] if replies else None

    def handle_all(self, request: bytes) -> List[bytes]:
        """``[7F xx 78, ..., final]`` for requests the brain answers with a pending
        first; ``[final]`` otherwise; ``[]`` for an empty request."""
        request = bytes(request)
        if not request:
            return []
        self.requests.append(request)
        sid = request[0]
        if sid in self.busy_once:
            self.busy_once.discard(sid)
            return [_nrc(sid, S.NRC_BUSY_REPEAT_REQUEST)]
        preambles: List[bytes] = []
        if sid == S.Service.READ_ECU_IDENTIFICATION and len(request) >= 2 \
                and request[1] in self.brain.pending_once_on:
            self.brain.pending_once_on.discard(request[1])
            preambles = [_nrc(sid, S.NRC_RESPONSE_PENDING)] * max(1, self.pending_count)
        return preambles + [self._dispatch(request)]

    # -- dispatch --------------------------------------------------------------

    def _dispatch(self, req: bytes) -> bytes:
        sid = req[0]
        b = self.brain
        if sid == S.Service.START_DIAGNOSTIC_SESSION:
            if len(req) == 2 and req[1] == S.SESSION_STANDARD_DIAGNOSTIC:
                self.session = req[1]
                return bytes([0x50, req[1]])
            return _nrc(sid, S.NRC_SERVICE_NOT_SUPPORTED)     # Bosch ABS: 7F 10 11 for anything but 0x89
        if sid == S.Service.STOP_DIAGNOSTIC_SESSION:
            self.session = None
            self.adaptation_open = self.basic_settings_open = False
            return bytes([0x60])
        if sid == S.Service.TESTER_PRESENT:
            return bytes([0x7E])
        if sid == S.Service.STOP_COMMUNICATION:
            self.session = None
            return bytes([0xC2])
        if sid == S.Service.READ_ECU_IDENTIFICATION:
            return self._ident(req)
        if sid == S.Service.READ_DATA_BY_LOCAL_ID:
            if len(req) < 2:
                return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)
            data = b.groups.get(req[1])
            if data is None:
                return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)
            return bytes([0x61, req[1]]) + data
        if sid == S.Service.READ_DTC_BY_STATUS:
            return self._read_dtcs(req)
        if sid == S.Service.CLEAR_DIAGNOSTIC_INFORMATION:
            if len(req) != 3 or req[1] != 0xFF:
                return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)
            b.dtcs.clear()
            self.cleared += 1
            return bytes([0x54, req[1], req[2]])
        if sid == S.Service.READ_MEMORY_BY_ADDRESS:
            return self._read_memory(req)
        if sid == S.Service.START_ROUTINE_BY_LOCAL_ID:
            return self._start_routine(req)
        if sid == S.Service.STOP_ROUTINE_BY_LOCAL_ID:
            return self._stop_routine(req)
        if sid == S.Service.REQUEST_ROUTINE_RESULTS_BY_LOCAL_ID:
            return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)
        if sid == S.Service.WRITE_DATA_BY_LOCAL_ID:
            return _nrc(sid, S.NRC_SECURITY_ACCESS_DENIED)   # a write without a login
        if sid == S.Service.IO_CONTROL_BY_LOCAL_ID:
            return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)     # no actuator local ids known
        if sid == S.Service.SECURITY_ACCESS:
            return _nrc(sid, S.NRC_SERVICE_NOT_SUPPORTED)    # Bosch ABS: 7F 27 11 to every 27 xx
        return _nrc(sid, S.NRC_SERVICE_NOT_SUPPORTED)

    def _ident(self, req: bytes) -> bytes:
        sid = req[0]
        if len(req) != 2:
            return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)
        opt = req[1]
        b = self.brain
        if opt == S.IDENT_STANDARD:
            return bytes([0x5A, opt]) + b.ident_9b
        if opt == S.IDENT_HARDWARE_NUMBER:
            return bytes([0x5A, opt]) + b.ident_91
        if opt == S.IDENT_LONG_CODING and b.ident_9a is not None:
            return bytes([0x5A, opt]) + b.ident_9a
        if opt == S.IDENT_INSTALLATION_LIST and b.installation_list is not None:
            return bytes([0x5A, opt]) + b.installation_list
        if opt in b.extra_ident:
            return bytes([0x5A, opt]) + b.extra_ident[opt]
        return _nrc(sid, S.NRC_SERVICE_NOT_SUPPORTED)        # DV: 7F 1A 11 for unknown options

    def _read_dtcs(self, req: bytes) -> bytes:
        sid = req[0]
        if len(req) != 4 or (req[2], req[3]) != (0xFF, 0x00):
            return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)   # NefMoto: 18 02 FF FF -> 7F 18 12
        status = req[1]
        if status not in (S.DTC_STATUS_VAG, S.DTC_STATUS_ALL):
            return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)   # DV refuses 18 03 (supported codes)
        out = bytearray([0x58, len(self.brain.dtcs)])
        for number, st in self.brain.dtcs:
            out += number.to_bytes(2, "big") + bytes([st & 0xFF])
        return bytes(out)

    def _read_memory(self, req: bytes) -> bytes:
        sid = req[0]
        if len(req) != 5:
            return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)
        addr = int.from_bytes(req[1:4], "big")
        n = req[4]
        if not 1 <= n <= 254:
            return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)
        b = self.brain
        off = addr - b.ram_base
        if not b.ram or off < 0 or off + n > len(b.ram):
            return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)
        return bytes([0x63]) + b.ram[off:off + n]

    def _start_routine(self, req: bytes) -> bytes:
        sid = req[0]
        if len(req) < 2:
            return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)
        lid, args = req[1], req[2:]
        b = self.brain
        if lid == S.ROUTINE_FUNCTION_START:
            if args == b"\x00\x00":
                out = bytearray([0x71, lid])
                for code in b.capabilities:
                    out += code.to_bytes(2, "big")
                return bytes(out)
            if len(args) != 2:
                return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)
            func = int.from_bytes(args, "big")
            if func not in b.capabilities:
                return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)
            if func == 0x0103:
                self.adaptation_open = True
                self.adaptation_channel = None
                return bytes([0x71, lid]) + args
            if func == 0x0101:
                self.basic_settings_open = True
                return bytes([0x71, lid]) + args
            # login / coding / output tests: the simulator refuses like a module that
            # needs a login it never got (the real byte forms are unknown anyway)
            return _nrc(sid, S.NRC_SECURITY_ACCESS_DENIED)
        if lid == S.ROUTINE_FUNCTION_SELECT:
            if args[:2] == b"\x01\x03" and self.adaptation_open and len(args) == 3:
                self.adaptation_channel = args[2]
                if args[2] not in b.adaptation:
                    return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)
                return bytes([0x71, lid]) + args
            return _nrc(sid, S.NRC_CONDITIONS_NOT_CORRECT)
        if lid == S.ROUTINE_FUNCTION_READ:
            if args == b"\x01\x03" and self.adaptation_open and self.adaptation_channel is not None:
                # simulator's own 71 BA layout: 01 03 <channel> <value hi> <value lo>
                value = b.adaptation.get(self.adaptation_channel, 0)
                return bytes([0x71, lid]) + args + bytes([self.adaptation_channel]) + value.to_bytes(2, "big")
            return _nrc(sid, S.NRC_CONDITIONS_NOT_CORRECT)
        if lid == S.ROUTINE_FUNCTION_SAVE:
            return _nrc(sid, S.NRC_SECURITY_ACCESS_DENIED)       # saves need a login the sim never grants
        return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)

    def _stop_routine(self, req: bytes) -> bytes:
        sid = req[0]
        if len(req) < 2:
            return _nrc(sid, S.NRC_SUBFUNCTION_NOT_SUPPORTED)
        lid, args = req[1], req[2:]
        if lid == S.ROUTINE_FUNCTION_START and args == b"\x01\x03":
            if not self.adaptation_open:
                return _nrc(sid, S.NRC_CONDITIONS_NOT_CORRECT)
            self.adaptation_open = False
            return bytes([0x72, lid]) + args
        if lid == S.ROUTINE_FUNCTION_START and args == b"\x01\x01":
            if not self.basic_settings_open:
                return _nrc(sid, S.NRC_CONDITIONS_NOT_CORRECT)
            self.basic_settings_open = False
            return bytes([0x72, lid]) + args
        return _nrc(sid, S.NRC_REQUEST_OUT_OF_RANGE)


def _nrc(sid: int, nrc: int) -> bytes:
    return bytes([S.NEGATIVE_RESPONSE_SID, sid, nrc])


# ================================================================= brains

def _ram_image(size: int = 0x10000) -> bytes:
    return bytes(((i * 31) + 7) & 0xFF for i in range(size))


class Me7Brain(KwpBrain):
    """2008 R32 engine: ``022 906 032 KR`` / ``R32-DQ-LEV2 G 1098``, coding 0000178,
    WSC 01279 785 00200 (VTX-R32F scan). Groups follow the standardized gasoline
    layout (registry §9 D1) with 8 fields like the real PQ35 engine replies; the
    second four are ``25 00 00`` fillers. Two stored faults: ``16485/P0101`` (0x4065,
    status ``01101000`` = 008 Implausible Signal, not intermittent) and the factory
    code ``00668`` Supply Voltage Terminal 30 (0x029C, status ``00101100`` = 012
    Electrical Fault in Circuit, Intermittent). ``1A 9B`` is answered with one
    ``7F 1A 78`` first (exercises the pending loop)."""

    def __init__(self) -> None:
        super().__init__(
            name="engine", part_number="022906032KR", sw_version="1098", component="R32-DQ-LEV2 G",
            coding_type=S.CODING_TYPE_SHORT, short_coding=178, wsc=(1279, 785, 200),
            hardware_number="022906032GP",
            capabilities=[0x0101, 0x0103, 0x0102, 0x0106, 0x0107, 0x0108, 0x010D, 0x0118],
            adaptation={0: 0, 1: 128, 2: 100},
            ram=_ram_image(), ram_base=0x000000,
            pending_once_on={S.IDENT_STANDARD},
        )
        rpm = (0x01, 0x44, 0x32)            # 680 rpm
        load = (0x21, 0x85, 0x1A)           # 19.5 %
        cool = (0x05, 0x0A, 0xBE)           # 90 C
        self.groups = {
            1: fields(rpm, cool, (0x14, 0x80, 0x82), (0x14, 0x80, 0x7F), FILLER, FILLER, FILLER, FILLER),
            2: fields(rpm, load, (0x16, 0xFF, 0x0D), (0x19, 0x46, 0x03), FILLER, FILLER, FILLER, FILLER),
            3: fields(rpm, (0x19, 0x46, 0x03), (0x21, 0xFA, 0x0C), (0x1B, 0x64, 0x8A),
                      FILLER, FILLER, FILLER, FILLER),
            4: fields(rpm, (0x06, 0x37, 0xFF), cool, (0x05, 0x0A, 0x82), FILLER, FILLER, FILLER, FILLER),
            5: fields(rpm, load, (0x07, 0x64, 0x00), (0x25, 0x00, 0x01), FILLER, FILLER, FILLER, FILLER),
            20: fields((0x22, 0x64, 0x80), (0x22, 0x64, 0x80), (0x22, 0x64, 0x80), (0x22, 0x64, 0x80),
                       FILLER, FILLER, FILLER, FILLER),
            32: fields((0x14, 0x80, 0x83), (0x14, 0x80, 0x7D), (0x14, 0x80, 0x82), (0x14, 0x80, 0x7E),
                       FILLER, FILLER, FILLER, FILLER),
            33: fields((0x14, 0x80, 0x82), (0x15, 0x64, 0x05), (0x14, 0x80, 0x7F), (0x15, 0x64, 0x07),
                       FILLER, FILLER, FILLER, FILLER),
            81: text_field("WVWKC71K18W108211") + text_field("VWX7Z0G43N98XU") + text_field("1QH02---"),
            100: fields((0x10, 0xFF, 0x00), cool, (0x36, 0x00, 0x2A), (0x10, 0xFF, 0x02),
                        FILLER, FILLER, FILLER, FILLER),
            125: fields((0x10, 0x01, 0x01), (0x10, 0x01, 0x01), (0x10, 0x01, 0x01), (0x10, 0x01, 0x01),
                        FILLER, FILLER, FILLER, FILLER),
        }
        self.dtcs = [(0x4065, 0b01101000), (0x029C, 0b00101100)]


class Edc17Brain(KwpBrain):
    """2012 Golf TDI engine: ``03L 906 019 EE`` / ``R4 2,0L EDC G000SG 1181``, coding
    0050072 (scan B). Groups per registry §9 F2: 002.4 coolant, 011 rpm / boost
    specified / boost actual / N75 duty, 020 rail pressure, 099 EGT x3, 108 / 241
    soot, 240 since-regen, 086 / 089 readiness bits, 046.2 coolant. Formula ids are
    the simulator's plausible choices (the real CJAA ids are OPEN QUESTION 12).
    Every reply carries 8 fields (26 bytes) like the real EDC17CP14 replies (registry
    7.7: seishuku's 2013 Jetta ``21 72`` is 0x1A bytes / 8 fields), the second four
    being ``25 00 00`` fillers, so the 8-field walk and N+128 labelling are exercised
    on this engine too."""

    def __init__(self) -> None:
        super().__init__(
            name="engine", part_number="03L906019EE", sw_version="1181", component="R4 2,0L EDC G000SG",
            coding_type=S.CODING_TYPE_SHORT, short_coding=50072, wsc=(2191, 444, 90205),
            hardware_number="03L907309AA",
            capabilities=[0x0101, 0x0103, 0x0102, 0x0105, 0x0106, 0x0107, 0x0118],
            adaptation={0: 0, 118: 0, 123: 0},
            ram=_ram_image(0x4000), ram_base=0xD00000,
        )
        rpm = (0x01, 0x52, 0x32)            # 820 rpm
        cool = (0x05, 0x0A, 0xC1)           # 93 C
        pad = (FILLER,) * 4
        self.groups = {
            2: fields(rpm, (0x21, 0x85, 0x1A), (0x16, 0xFF, 0x0D), cool, *pad),
            11: fields(rpm, (0x12, 0xFA, 0x65), (0x12, 0xFA, 0x64), (0x21, 0x64, 0x64), *pad),
            20: fields((0x53, 0x75, 0x30), (0x53, 0x75, 0x28), rpm, FILLER, *pad),
            46: fields(rpm, cool, FILLER, FILLER, *pad),
            86: fields((0x10, 0xFF, 0xC8), (0x10, 0xFF, 0xF0), (0x10, 0xFF, 0x3F), (0x10, 0xFF, 0x3F), *pad),
            89: fields((0x10, 0xFF, 0x00), (0x10, 0xFF, 0x00), (0x10, 0xFF, 0x00), (0x10, 0xFF, 0x00), *pad),
            99: fields(rpm, (0x9F, 0x08, 0x86), (0x9F, 0x96, 0x85), (0x9F, 0x2C, 0x85), *pad),
            100: fields((0x9F, 0x2C, 0x85), (0x9F, 0x96, 0x85), FILLER, FILLER, *pad),
            108: fields((0x68, 0x05, 0xB2), (0x7E, 0x05, 0x19), (0x7E, 0x05, 0x1A), FILLER, *pad),
            240: fields((0x13, 0x64, 0x1B), (0x5C, 0x32, 0x0B), (0x36, 0x01, 0xB0), FILLER, *pad),
            241: fields((0x68, 0x05, 0xB2), (0x7E, 0x05, 0x19), (0x7E, 0x05, 0x1A), FILLER, *pad),
        }
        # 16683/P0299 Boost Pressure Regulation: Control Range Not Reached, 001 Upper Limit Exceeded
        self.dtcs = [(0x412B, 0b01100001)]


class Dq250Brain(KwpBrain):
    """DQ250 02E mechatronic: ``1A 9B`` part number = the *software* number ``02E 300
    011 CC`` (scan A "Part No SW"; IMPLEMENTATION_NOTES (d) item 13 expects
    ``02E300011CC ... GSG DSG 082 1405`` from dest 0x02), ``1A 91`` = the hardware
    number ``02E 927 770 AD``, component ``GSG DSG 082 1405``, coding 0000020, WSC
    04940 001 00001 (R32 scan). Same convention as the engine brains (9B = SW, 91 =
    HW). Group 019 = three temperatures (G510 / G509 / G93) + idle info; 013 = clutch
    valve 1 current and duties; 001 field 1 = ``25 hi lo`` speed (raw/3 km/h per the
    speedPulserPro capture)."""

    def __init__(self, *, part_number: str = "02E300011CC", hardware_number: str = "02E927770AD",
                 sw_version: str = "1405", component: str = "GSG DSG 082",
                 wsc: Tuple[int, int, int] = (4940, 1, 1)) -> None:
        super().__init__(
            name="transmission", part_number=part_number, sw_version=sw_version, component=component,
            coding_type=S.CODING_TYPE_SHORT, short_coding=20, wsc=wsc, hardware_number=hardware_number,
            capabilities=[0x0101, 0x0102, 0x0103, 0x0106, 0x0118],
            adaptation={0: 0},
        )
        self.groups = {
            1: fields((0x25, 0x00, 0x00), (0x25, 0x00, 0x00), (0x25, 0x00, 0x01), (0x07, 0x64, 0x00)),
            6: fields((0x25, 0x00, 0x00), (0x18, 0x0A, 0x54), (0x21, 0x64, 0x00), (0x18, 0x0A, 0x54)),
            13: fields((0x18, 0x0A, 0xBF), (0x21, 0x64, 0x00), (0x21, 0x64, 0x0A), (0x21, 0x64, 0x00)),
            19: fields((0x1A, 0x00, 0x37), (0x1A, 0x00, 0x39), (0x1A, 0x00, 0x3A), (0x25, 0x00, 0x01)),
            125: fields((0x10, 0x01, 0x01), (0x10, 0x01, 0x01), (0x10, 0x01, 0x01), (0x10, 0x01, 0x01)),
        }
        # 17150/P0766 Shift Solenoid 4 (N91), 000, intermittent (MTD-DSG scan line)
        self.dtcs = [(0x42FE, 0b00100000)]


class HaldexBrain(KwpBrain):
    """Haldex Gen2: ``1K0 907 554 L`` / ``Haldex 4Motion 0116``, coding 0000001, WSC
    00000 000 00000 (R32 scan). Groups 001 / 002 / 125 exist (OpenHaldex); their
    *contents* are only reported, so the fixture uses OpenHaldex's own field
    examples: supply voltage 0x06, oil temperature 0x1A, oil pressure 0x0E (a=27,
    b=200 -> 27 bar), est. torque 0x5E (a=160, b=255 -> 2032 Nm), clutch duty 0x21
    (a=100, b=40 -> 40 %), clutch valve current 0x18 (a=10, b=191 -> 1.910 A)."""

    def __init__(self) -> None:
        super().__init__(
            name="awd", part_number="1K0907554L", sw_version="0116", component="Haldex 4Motion",
            coding_type=S.CODING_TYPE_SHORT, short_coding=1, wsc=(0, 0, 0),
            capabilities=[0x0102, 0x0106, 0x0118],
        )
        self.groups = {
            1: fields((0x06, 0x37, 0xE4), (0x1A, 0x00, 0x23), (0x25, 0x00, 0x01), (0x25, 0x00, 0x00)),
            2: fields((0x0E, 0x1B, 0xC8), (0x5E, 0xA0, 0xFF), (0x21, 0x64, 0x28), (0x18, 0x0A, 0xBF)),
            125: fields((0x10, 0x01, 0x01), (0x10, 0x01, 0x01), (0x10, 0x01, 0x00), (0x10, 0x01, 0x00)),
        }
        # 01073 Clutch Pressure System, 002 Lower Limit Exceeded, intermittent (R32 scans)
        self.dtcs = [(0x0431, 0b00100010)]


#: The R32's installed modules decoded from gateway coding ED831F075003020000
#: (layout 3, bit-exact 22/22 in the registry): (address word, TP 2.0 address used
#: by the simulator, flags). Addresses: 01/09/0A/1F verified, 02/03/07 reported
#: (medium), 05/20/21/22/52 converter-table (low), the rest simulator choices; 04
#: (G85) carries the phantom 0x13 address vag-blocks skips.
R32_INSTALLATION: Tuple[Tuple[int, int, int], ...] = (
    (0x01, 0x01, 0x01), (0x02, 0x02, 0x01), (0x03, 0x03, 0x01), (0x04, 0x13, 0x00),
    (0x44, 0x09, 0x01), (0x15, 0x05, 0x01), (0x55, 0x30, 0x01), (0x22, 0x0A, 0x03),
    (0x17, 0x07, 0x01), (0x25, 0x07, 0x01), (0x09, 0x20, 0x01), (0x46, 0x21, 0x01),
    (0x42, 0x22, 0x01), (0x52, 0x23, 0x01), (0x65, 0x21, 0x01), (0x16, 0x31, 0x01),
    (0x08, 0x32, 0x01), (0x47, 0x33, 0x01), (0x37, 0x34, 0x01), (0x0F, 0x35, 0x01),
    (0x56, 0x52, 0x01), (0x19, 0x1F, 0x01),
)
R32_GATEWAY_CODING = bytes.fromhex("ED831F075003020000")


class GatewayBrain(KwpBrain):
    """J533 gateway ``1K0 907 530 L`` / ``J533 Gateway H07 0052``, long coding
    ``ED831F075003020000``. Answers ``1A 9A`` (reported record layout) and ``1A 9F``
    in vag-blocks' layout: record 0 = 4-byte entries ``[module, tp20 address, 00,
    flags]`` for :data:`R32_INSTALLATION`, record 1 = the coding bytes (the real
    second record is unknown)."""

    def __init__(self, installation: Sequence[Tuple[int, int, int]] = R32_INSTALLATION,
                 coding: bytes = R32_GATEWAY_CODING) -> None:
        super().__init__(
            name="gateway", part_number="1K0907530L", sw_version="0052", component="J533 Gateway H07",
            coding_type=S.CODING_TYPE_LONG, long_coding=bytes(coding), wsc=(1279, 785, 200),
            hardware_number="1K0907951",
            capabilities=[0x0104, 0x0118],
        )
        entries = bytearray()
        for module, address, flags in installation:
            entries += bytes([module, address, 0x00, flags])
        self.installation_list = build_length_prefixed([bytes(entries), bytes(coding)])
        self.dtcs = []


class BodyBrain(KwpBrain):
    """Any other KWP module: name, part number, component text, software version and
    its coding - ``coding=<int>`` for a 7-digit short coding (type 03),
    ``long_coding=<bytes>`` for a long coding (type 10, read with ``1A 9A`` in the
    reported record layout), neither = no coding (type 00). ``hardware_number`` is
    the ``1A 91`` record (defaults to the part number, as on modules whose scan
    prints the same number for SW and HW)."""

    def __init__(self, name: str, part_number: str, component: str, sw_version: str = "0000", *,
                 coding: Optional[int] = None, long_coding: Optional[bytes] = None,
                 wsc: Tuple[int, int, int] = (0, 0, 0), hardware_number: str = "",
                 groups: Optional[Dict[int, bytes]] = None, dtcs: Optional[List[Tuple[int, int]]] = None,
                 capabilities: Optional[List[int]] = None) -> None:
        if coding is not None and long_coding is not None:
            raise ValueError("a module has either a short coding or a long coding, not both")
        if long_coding is not None:
            coding_type = S.CODING_TYPE_LONG
        elif coding is not None:
            coding_type = S.CODING_TYPE_SHORT
        else:
            coding_type = S.CODING_TYPE_NONE
        super().__init__(
            name=name, part_number=part_number, sw_version=sw_version, component=component,
            coding_type=coding_type, short_coding=coding or 0, long_coding=bytes(long_coding or b""),
            wsc=wsc, hardware_number=hardware_number,
            capabilities=list(capabilities) if capabilities is not None else [0x0102, 0x0106, 0x0118],
        )
        self.groups = dict(groups or {1: fields((0x06, 0x37, 0xE4), FILLER, FILLER, FILLER)})
        self.dtcs = list(dtcs or [])


#: The scans print a 30-byte long coding for the R32's central electrics (3C0 937
#: 049 AJ) and the Golf's BCM (1K0 937 086 P) but not its value; the simulator
#: serves 30 zero bytes so the ``1A 9A`` path is exercised on those modules. Not
#: the real coding of either car.
BCM_LONG_CODING_PLACEHOLDER = bytes(30)
#: Scan B values (IMPLEMENTATION_NOTES (a), 2012 Golf TDI).
GOLF_GATEWAY_CODING = bytes.fromhex("350002")
GOLF_ABS_CODING = bytes.fromhex("114B400C49240000880F02EA92200042B70000")
GOLF_RADIO_CODING = bytes.fromhex("01000400040005")


# ================================================================= simulated vehicle

@dataclass(frozen=True)
class KwpModuleSpec:
    """A KWP module on a simulated car: VCDS address word, the brain factory, the TP
    2.0 logical address and tester-TX id the responder uses, and how sure the
    registry is about them: ``verified`` = the logical address was sniffed on a real
    PQ35 car; ``tester_tx_from_registry`` = the tester-TX id is what a capture (or
    the registry's prediction) says the real module grants - when False the id is
    the simulator's own choice and must lie outside :data:`RESERVED_TESTER_TX_RANGES`."""
    address_word: int
    label: str
    brain: Callable[[], KwpBrain]
    logical_address: int
    tester_tx_id: int
    verified: bool
    evidence: str
    tester_tx_from_registry: bool = False

    @property
    def reply_id(self) -> int:
        """``0x200 + logical address``: where the module answers the setup frame."""
        return 0x200 + self.logical_address


#: 11-bit ids a simulator-chosen tester-TX id must stay out of: the TP 2.0 setup
#: replies (0x200+addr), the tester RX pool 0x300..0x30F, the whole ODIS UDS block
#: (requests 0x70A..0x773 / responses 0x774..0x7DD, registry 7.2, rounded out to
#: 0x700..0x7DD) and legislated OBD 0x7DF..0x7EF. Real modules do grant ids inside
#: these ranges (0x740, 0x760, 0x764, 0x7A8 are captures) - those come from the
#: registry and are marked ``tester_tx_from_registry``.
RESERVED_TESTER_TX_RANGES: Tuple[range, ...] = (range(0x200, 0x300), range(0x300, 0x310),
                                                range(0x700, 0x7DE), range(0x7DF, 0x7F0))


def tester_tx_id_is_reserved(can_id: int) -> bool:
    return any(can_id in r for r in RESERVED_TESTER_TX_RANGES)


def _sim_tester_tx(logical_address: int) -> int:
    """Simulator-chosen tester-TX id: ``0x7F0 | (logical address & 0xF)`` - outside
    every reserved range; the presets keep the low nibbles distinct."""
    return 0x7F0 | (logical_address & 0x0F)


R32_KWP_MODULES: Tuple[KwpModuleSpec, ...] = (
    KwpModuleSpec(0x01, "engine", Me7Brain, 0x01, 0x740, True, "three PQ35 engine captures",
                  tester_tx_from_registry=True),
    KwpModuleSpec(0x02, "transmission", Dq250Brain, 0x02, 0x760, False,
                  "speedPulserPro 'confirmed from VCDS SavvyCAN capture' (medium-high)",
                  tester_tx_from_registry=True),
    KwpModuleSpec(0x03, "abs", lambda: BodyBrain("abs", "1K0907379AB", "ESP 4MOTION MK60", "0102",
                                                 coding=21128, wsc=(1279, 785, 200)),
                  0x03, _sim_tester_tx(0x03), False, "PQ35 ABS emulator's choice (medium); tester id = simulator choice"),
    KwpModuleSpec(0x17, "instruments", lambda: BodyBrain("instruments", "1K6920974D", "KOMBIINSTRUMENT VDD",
                                                         "1216", coding=7203, wsc=(1279, 785, 200)),
                  0x07, _sim_tester_tx(0x07), False, "one forum assertion (medium); tester id = simulator choice"),
    KwpModuleSpec(0x44, "steering", lambda: BodyBrain("steering", "1K1909144M", "EPS_ZFLS Kl.141 H08", "1901"),
                  0x09, 0x7A8, True, "bench 1K0 909 144 E capture (ICH)", tester_tx_from_registry=True),
    KwpModuleSpec(0x22, "awd", HaldexBrain, 0x0A, 0x764, True, "OpenHaldex-C6 capture", tester_tx_from_registry=True),
    KwpModuleSpec(0x19, "gateway", GatewayBrain, 0x1F, 0x32E, True,
                  "sniff + reproduction, two posters (address); tester id predicted 0x32E (medium)",
                  tester_tx_from_registry=True),
    KwpModuleSpec(0x09, "central-electrics", lambda: BodyBrain("central-electrics", "3C0937049AJ",
                                                               "Bordnetz-SG H54", "2202",
                                                               long_coding=BCM_LONG_CODING_PLACEHOLDER,
                                                               wsc=(1279, 785, 200)),
                  0x20, _sim_tester_tx(0x20), False, "converter table only (low); tester id = simulator choice"),
    KwpModuleSpec(0x15, "airbag", lambda: BodyBrain("airbag", "1K0909605AB", "6T AIRBAG VW8R 034", "8000",
                                                    coding=13908),
                  0x05, _sim_tester_tx(0x05), False, "converter table only (low); tester id = simulator choice"),
)

GOLF_TDI_KWP_MODULES: Tuple[KwpModuleSpec, ...] = (
    KwpModuleSpec(0x01, "engine", Edc17Brain, 0x01, 0x740, True,
                  "PQ35 engine family (three captures); CJAA = KWP/TP 2.0 per scans B/C and Ross-Tech",
                  tester_tx_from_registry=True),
    KwpModuleSpec(0x02, "transmission", lambda: Dq250Brain(part_number="02E300052", hardware_number="02E927770AJ",
                                                            sw_version="1920", component="GSG DSG AG6 440",
                                                            wsc=(2191, 444, 90205)),
                  0x02, 0x760, False, "sibling scan C; address medium-high", tester_tx_from_registry=True),
    KwpModuleSpec(0x03, "abs", lambda: BodyBrain("abs", "1K0907379BJ", "ESP MK60EC1 H31", "0121",
                                                 long_coding=GOLF_ABS_CODING, wsc=(2191, 444, 90205)),
                  0x03, _sim_tester_tx(0x03), False, "medium; tester id = simulator choice"),
    KwpModuleSpec(0x44, "steering", lambda: BodyBrain("steering", "1K0909144M", "EPS_ZFLS Kl. 70", "3201"),
                  0x09, 0x7A8, True, "bench capture of the 1K0 909 144 family", tester_tx_from_registry=True),
    KwpModuleSpec(0x19, "gateway", lambda: BodyBrain("gateway", "7N0907530H", "J533 Gateway H42", "1620",
                                                     long_coding=GOLF_GATEWAY_CODING, hardware_number="1K0907951"),
                  0x1F, 0x32E, False, "0x1F verified only for 1K0 907 530; 7N0 untested", tester_tx_from_registry=True),
    KwpModuleSpec(0x09, "central-electrics", lambda: BodyBrain("central-electrics", "1K0937086P",
                                                               "BCM PQ35 M 110", "0651",
                                                               long_coding=BCM_LONG_CODING_PLACEHOLDER),
                  0x20, _sim_tester_tx(0x20), False, "converter table only (low); tester id = simulator choice"),
    KwpModuleSpec(0x56, "radio", lambda: BodyBrain("radio", "1K0035180AE", "Radio Prem-8 H02", "0016",
                                                   long_coding=GOLF_RADIO_CODING),
                  0x52, _sim_tester_tx(0x52), False, "converter table only (low); tester id = simulator choice"),
)


def _ids_in_use(vehicle: SimulatedVehicle) -> Dict[int, str]:
    """Every 11-bit id a node already on ``vehicle`` transmits or listens on
    (UDS request/response/functional ids, TP 2.0 tester-TX and setup-reply ids)."""
    used: Dict[int, str] = {}
    for node in vehicle.nodes:
        for attr in ("request_id", "response_id", "functional_id", "tester_tx_id"):
            value = getattr(node, attr, None)
            if isinstance(value, int):
                used.setdefault(value, f"{node.name}.{attr}")
        logical = getattr(node, "logical_address", None)
        if isinstance(logical, int):
            used.setdefault(0x200 + logical, f"{node.name} setup reply")
    return used


def add_kwp_nodes(vehicle: SimulatedVehicle, specs: Sequence[KwpModuleSpec], *,
                  prefix: str = "kwp") -> Dict[int, SimulatedKwpEcu]:
    """Put one TP 2.0 responder per spec on ``vehicle``; returns ``{address_word:
    ecu}`` so tests can script the brains. Needs :mod:`vagtune.transport.tp20_sim`
    (imported lazily; without it the vehicle simply gets no KWP modules).

    Refuses (``ValueError``) a spec whose tester-TX id or ``0x200 + logical
    address`` is already used by a node on the vehicle (a UDS node's request,
    response or functional id, another TP 2.0 node's ids), and a simulator-chosen
    tester-TX id inside :data:`RESERVED_TESTER_TX_RANGES`: a KWP responder treats
    every frame on its tester-TX id as TP 2.0 data, so sharing it with an ISO-TP
    module breaks both. Nodes added *after* this call are the other slice's
    responsibility; the preset tests check both presets as a whole.
    """
    try:
        from ..transport.tp20_sim import Tp20Node
    except ImportError as exc:  # pragma: no cover - the TP 2.0 slice ships it
        log.warning("TP 2.0 simulator unavailable (%s); preset %r gets no KWP modules", exc, vehicle.preset)
        return {}
    used = _ids_in_use(vehicle)
    ecus: Dict[int, SimulatedKwpEcu] = {}
    for spec in specs:
        if not spec.tester_tx_from_registry and tester_tx_id_is_reserved(spec.tester_tx_id):
            raise ValueError(f"{spec.label}: simulator-chosen tester-TX id 0x{spec.tester_tx_id:03X} lies in a "
                             "reserved UDS/OBD/TP 2.0 id range")
        for can_id, what in ((spec.tester_tx_id, "tester-TX id"), (spec.reply_id, "setup reply id")):
            if can_id in used:
                raise ValueError(f"{spec.label}: {what} 0x{can_id:03X} is already used by {used[can_id]} on "
                                 f"preset {vehicle.preset!r}")
        ecu = SimulatedKwpEcu(spec.brain())
        name = f"{prefix}-{spec.address_word:02X}-{spec.label}"
        vehicle.add_node(Tp20Node(vehicle.bus, ecu.handle_all, logical_address=spec.logical_address,
                                  tester_tx_id=spec.tester_tx_id, name=name))
        used[spec.tester_tx_id] = f"{name}.tester_tx_id"
        used[spec.reply_id] = f"{name} setup reply"
        ecus[spec.address_word] = ecu
    return ecus


def _hook_r32(vehicle: SimulatedVehicle) -> None:
    add_kwp_nodes(vehicle, R32_KWP_MODULES)


def _hook_golf_tdi(vehicle: SimulatedVehicle) -> None:
    add_kwp_nodes(vehicle, GOLF_TDI_KWP_MODULES)


SimulatedVehicle.register_preset_hook("r32-2008", _hook_r32)
SimulatedVehicle.register_preset_hook("golf-tdi-2012", _hook_golf_tdi)


__all__ = [
    "SimulatedKwpEcu", "KwpBrain", "Me7Brain", "Edc17Brain", "Dq250Brain", "HaldexBrain", "GatewayBrain",
    "BodyBrain", "KwpModuleSpec", "R32_KWP_MODULES", "GOLF_TDI_KWP_MODULES", "R32_INSTALLATION",
    "R32_GATEWAY_CODING", "GOLF_GATEWAY_CODING", "GOLF_ABS_CODING", "GOLF_RADIO_CODING",
    "BCM_LONG_CODING_PLACEHOLDER", "RESERVED_TESTER_TX_RANGES", "tester_tx_id_is_reserved", "add_kwp_nodes",
    "build_ident_9b", "build_ident_9a", "build_length_prefixed", "pack_wsc_block", "fields", "text_field", "FILLER",
]
