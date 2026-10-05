"""
ReadDTCInformation (0x19) response parsing.

Every layout here is the one udsoncan's ``interpret_response`` implements, re-read
byte for byte for PROTOCOL_FACTS (uds_vag.md §C):

* ``59 01 <availabilityMask> <formatIdentifier> <count_hi> <count_lo>``
* ``59 02 <availabilityMask>`` then 4-byte records ``<DTC(3)> <status>`` — the same
  shape for 0x0A/0x0B/0x0C/0x0D/0x0E/0x0F/0x13/0x15/0x17
* ``59 03`` then 4-byte records ``<DTC(3)> <snapshotRecordNumber>``
* ``59 04 <DTC(3)> <status>`` then per record ``<recordNumber> <numberOfDIDs>`` and
  that many ``<DID(2)> <data>`` pairs — **the data length per DID is not in the
  message**; the parser needs each DID's size a priori
* ``59 06 <DTC(3)> <status>`` then per record ``<recordNumber> <data>`` — the record
  size is not in the message either
* ``59 14`` then 4-byte records ``<DTC(3)> <faultDetectionCounter>``

Sizes are therefore never guessed: when a snapshot DID or an extended-data record has
no known size, parsing stops there and the unparsed bytes are returned in ``.raw`` of
the record being parsed, with ``.complete == False``. The caller can inspect the raw
tail, learn the sizes from a label file / ODX, and parse again.

A VAG 3-byte DTC is 2 SAE bytes + 1 failure-type byte (FTB): ``P0299`` with FTB 0x00
is ``02 99 00`` (verified).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Mapping, Optional, Sequence, Tuple, Union

from . import services as S
from .exceptions import UnexpectedResponse

_LETTERS = "PCBU"


def sae_code(b0: int, b1: int) -> str:
    """Two SAE bytes -> ``P0299`` (letter from bits 7-6, first digit bits 5-4, then hex)."""
    return f"{_LETTERS[b0 >> 6]}{(b0 >> 4) & 3}{b0 & 0xF:X}{(b1 >> 4) & 0xF:X}{b1 & 0xF:X}"


def dtc_to_bytes(dtc: int) -> bytes:
    """3-byte DTC packed as an int (high byte first) -> its 3 wire bytes."""
    if not 0 <= dtc <= 0xFFFFFF:
        raise ValueError(f"DTC 0x{dtc:X} does not fit in 3 bytes")
    return dtc.to_bytes(3, "big")


def dtc_from_bytes(b: bytes) -> int:
    if len(b) != 3:
        raise ValueError(f"a DTC is 3 bytes, got {len(b)}")
    return int.from_bytes(b, "big")


def status_names(status: int) -> List[str]:
    """ISO 14229 Annex D bit names set in a status byte, lowest bit first."""
    return [name for bit, name in sorted(S.DTC_STATUS_NAMES.items()) if status & bit]


@dataclass
class UdsDtc:
    """One 3-byte UDS DTC with its status byte.

    ``dtc`` is the 3-byte value as an int (``0x029900`` for P0299 FTB 00),
    ``sae_code`` the 5-character code, ``ftb`` the failure-type byte, ``status`` the
    ISO 14229 status byte; ``fault_counter`` is only filled by subfunction 0x14.
    """
    dtc: int
    sae_code: str
    ftb: int
    status: int
    fault_counter: Optional[int] = None

    @classmethod
    def from_bytes(cls, b: bytes, status: int, fault_counter: Optional[int] = None) -> "UdsDtc":
        if len(b) != 3:
            raise ValueError(f"a DTC is 3 bytes, got {len(b)}")
        return cls(int.from_bytes(b, "big"), sae_code(b[0], b[1]), b[2], status, fault_counter)

    @classmethod
    def from_int(cls, dtc: int, status: int = 0) -> "UdsDtc":
        return cls.from_bytes(dtc_to_bytes(dtc), status)

    @property
    def bytes(self) -> bytes:
        return dtc_to_bytes(self.dtc)

    @property
    def sae_bytes(self) -> bytes:
        return self.bytes[:2]

    @property
    def sae_value(self) -> int:
        """Decimal value of the 2 SAE bytes (the VAG 6-digit number, e.g. 665 for P0299)."""
        return self.dtc >> 8

    # -- status bit helpers (ISO 14229 Annex D, verified) ---------------------------
    @property
    def test_failed(self) -> bool:
        return bool(self.status & S.DtcStatus.TEST_FAILED)

    @property
    def test_failed_this_cycle(self) -> bool:
        return bool(self.status & S.DtcStatus.TEST_FAILED_THIS_CYCLE)

    @property
    def pending(self) -> bool:
        return bool(self.status & S.DtcStatus.PENDING)

    @property
    def confirmed(self) -> bool:
        return bool(self.status & S.DtcStatus.CONFIRMED)

    @property
    def test_not_completed_since_clear(self) -> bool:
        return bool(self.status & S.DtcStatus.TEST_NOT_COMPLETE_SINCE_CLEAR)

    @property
    def test_failed_since_clear(self) -> bool:
        return bool(self.status & S.DtcStatus.TEST_FAILED_SINCE_CLEAR)

    @property
    def test_not_completed_this_cycle(self) -> bool:
        return bool(self.status & S.DtcStatus.TEST_NOT_COMPLETE_THIS_CYCLE)

    @property
    def warning_indicator_requested(self) -> bool:
        return bool(self.status & S.DtcStatus.WARNING_INDICATOR_REQUESTED)

    @property
    def active(self) -> bool:
        """Currently failing (testFailed) — VCDS "active"; a confirmed-but-not-failing
        DTC is "intermittent"/"stored"."""
        return self.test_failed

    @property
    def intermittent(self) -> bool:
        """Failed since the last clear but not failing right now (e.g. status [096])."""
        return self.test_failed_since_clear and not self.test_failed

    def status_names(self) -> List[str]:
        return status_names(self.status)

    def status_text(self) -> str:
        names = self.status_names()
        return ", ".join(names) if names else "no status bits set"

    def vcds_bracket(self) -> str:
        """VCDS prints the status byte in decimal in brackets, e.g. ``[096]`` for 0x60
        (convention; see uds_vag.md §H)."""
        return f"[{self.status:03d}]"

    def __str__(self) -> str:
        return f"{self.sae_code} {self.ftb:02X} {self.vcds_bracket()}"


@dataclass
class DtcCount:
    """Decoded ``59 01`` response."""
    availability_mask: int
    dtc_format: int
    count: int

    @property
    def format_name(self) -> str:
        try:
            return S.DtcFormat(self.dtc_format).name
        except ValueError:
            return f"format 0x{self.dtc_format:02X}"


@dataclass
class DtcSnapshot:
    """One snapshot (freeze-frame) record of a DTC.

    ``dids`` holds the ``(did, data)`` pairs that could be parsed with known sizes;
    ``raw`` is the unparsed tail that follows them (empty when ``complete``).
    ``did_count`` is the count the ECU announced.
    """
    record: int
    did_count: int
    dids: List[Tuple[int, bytes]] = field(default_factory=list)
    raw: bytes = b""

    @property
    def complete(self) -> bool:
        return not self.raw and len(self.dids) == self.did_count

    def value(self, did: int) -> Optional[bytes]:
        for d, v in self.dids:
            if d == did:
                return v
        return None


@dataclass
class DtcSnapshotReport:
    """``59 04`` decoded: the DTC + status echo and its snapshot records."""
    dtc: UdsDtc
    records: List[DtcSnapshot]

    @property
    def complete(self) -> bool:
        return all(r.complete for r in self.records)


@dataclass
class DtcExtendedData:
    """One extended-data record of a DTC.

    ``data`` is the record payload when its size was known; otherwise it is empty and
    ``raw`` carries everything from the first byte after the record number to the end
    of the message (which may contain further records — the boundary is unknowable
    without the size).
    """
    record: int
    data: bytes = b""
    raw: bytes = b""

    @property
    def complete(self) -> bool:
        return not self.raw


@dataclass
class DtcExtendedReport:
    """``59 06`` decoded: the DTC + status echo and its extended-data records."""
    dtc: UdsDtc
    records: List[DtcExtendedData]

    @property
    def complete(self) -> bool:
        return all(r.complete for r in self.records)

    def record(self, number: int) -> Optional[DtcExtendedData]:
        for r in self.records:
            if r.record == number:
                return r
        return None


SizeOracle = Union[Mapping[int, int], None]


def _check_header(data: bytes, subfunction: int, min_len: int) -> None:
    if len(data) < min_len:
        raise UnexpectedResponse(
            f"ReadDTCInformation 0x{subfunction:02X} response too short ({len(data)} bytes)")
    if data[0] != S.Service.READ_DTC_INFORMATION + S.POSITIVE_RESPONSE_OFFSET:
        raise UnexpectedResponse(f"not a ReadDTCInformation response (SID 0x{data[0]:02X})")
    if (data[1] & 0x7F) != subfunction:
        raise UnexpectedResponse(
            f"ReadDTCInformation subfunction echo 0x{data[1]:02X} != 0x{subfunction:02X}")


def parse_dtc_count(data: bytes) -> DtcCount:
    """Parse ``59 01 <availability> <format> <count16>`` (also 0x07/0x11/0x12 shapes)."""
    _check_header(data, data[1] & 0x7F if len(data) > 1 else 0x01, 6)
    return DtcCount(data[2], data[3], int.from_bytes(data[4:6], "big"))


def parse_dtc_records(data: bytes, subfunction: int = 0x02) -> Tuple[int, List[UdsDtc]]:
    """Parse ``59 <sub> <availabilityMask>`` + 4-byte ``DTC(3) status`` records.

    Returns ``(availability_mask, dtcs)``. A trailing partial record (ECU bug) is
    dropped, not guessed.
    """
    _check_header(data, subfunction, 3)
    mask = data[2]
    body = data[3:]
    out: List[UdsDtc] = []
    for i in range(0, len(body) - 3, 4):
        out.append(UdsDtc.from_bytes(body[i:i + 3], body[i + 3]))
    return mask, out


def parse_snapshot_identification(data: bytes) -> List[Tuple[UdsDtc, int]]:
    """Parse ``59 03`` + ``DTC(3) recordNumber`` pairs -> ``[(dtc, record), ...]``."""
    _check_header(data, 0x03, 2)
    body = data[2:]
    out: List[Tuple[UdsDtc, int]] = []
    for i in range(0, len(body) - 3, 4):
        out.append((UdsDtc.from_bytes(body[i:i + 3], 0), body[i + 3]))
    return out


def parse_fault_detection_counters(data: bytes) -> List[UdsDtc]:
    """Parse ``59 14`` + ``DTC(3) counter`` records; ``status`` is 0, counter filled."""
    _check_header(data, 0x14, 2)
    body = data[2:]
    out: List[UdsDtc] = []
    for i in range(0, len(body) - 3, 4):
        out.append(UdsDtc.from_bytes(body[i:i + 3], 0, fault_counter=body[i + 3]))
    return out


def parse_snapshot_records(data: bytes, did_sizes: SizeOracle = None) -> DtcSnapshotReport:
    """Parse ``59 04 <DTC(3)> <status>`` + records ``<rec> <nDIDs> (<DID(2)> <data>)*``.

    ``did_sizes`` maps DID -> byte length. Parsing proceeds record by record and DID by
    DID; at the first DID without a known size the rest of the message goes into that
    record's ``raw`` and parsing stops (``complete`` is False). With no sizes at all
    the first record is returned with its header parsed and all data raw.
    """
    _check_header(data, 0x04, 6)
    dtc = UdsDtc.from_bytes(data[2:5], data[5])
    sizes = did_sizes or {}
    records: List[DtcSnapshot] = []
    p = 6
    n = len(data)
    while p < n:
        if p + 2 > n:
            # A lone trailing byte cannot be a record header.
            records.append(DtcSnapshot(record=data[p], did_count=0, raw=data[p + 1:]))
            break
        rec = DtcSnapshot(record=data[p], did_count=data[p + 1])
        p += 2
        stopped = False
        for _ in range(rec.did_count):
            if p + 2 > n:
                rec.raw = data[p:]
                stopped = True
                break
            did = (data[p] << 8) | data[p + 1]
            size = sizes.get(did)
            if size is None or p + 2 + size > n:
                rec.raw = data[p:]          # unparsed from this DID onwards
                stopped = True
                break
            rec.dids.append((did, data[p + 2:p + 2 + size]))
            p += 2 + size
        records.append(rec)
        if stopped:
            break
    return DtcSnapshotReport(dtc, records)


def parse_extended_data(data: bytes, record_sizes: SizeOracle = None) -> DtcExtendedReport:
    """Parse ``59 06 <DTC(3)> <status>`` + records ``<rec> <data(size)>``.

    ``record_sizes`` maps record number -> byte length (udsoncan's
    ``extended_data_size``). A record with unknown size swallows the rest of the
    message into ``raw`` and parsing stops. Record number 0 is reserved/illegal and
    reported as :class:`UnexpectedResponse`.
    """
    _check_header(data, 0x06, 6)
    dtc = UdsDtc.from_bytes(data[2:5], data[5])
    sizes = record_sizes or {}
    records: List[DtcExtendedData] = []
    p = 6
    n = len(data)
    while p < n:
        rec_no = data[p]
        if rec_no == 0:
            raise UnexpectedResponse("extended data record number 0 is reserved")
        size = sizes.get(rec_no)
        if size is None or p + 1 + size > n:
            records.append(DtcExtendedData(record=rec_no, raw=data[p + 1:]))
            break
        records.append(DtcExtendedData(record=rec_no, data=data[p + 1:p + 1 + size]))
        p += 1 + size
    return DtcExtendedReport(dtc, records)


def build_dtc_records(mask: int, dtcs: Sequence[Tuple[bytes, int]], subfunction: int = 0x02) -> bytes:
    """Inverse of :func:`parse_dtc_records`, for simulators and tests."""
    body = bytearray([0x59, subfunction, mask])
    for dtc, status in dtcs:
        body += bytes(dtc) + bytes([status])
    return bytes(body)


def build_snapshot_response(dtc: bytes, status: int,
                            records: Mapping[int, Sequence[Tuple[int, bytes]]]) -> bytes:
    """Build a ``59 04`` response from ``{record: [(did, data), ...]}``."""
    out = bytearray([0x59, 0x04]) + bytes(dtc) + bytes([status])
    for rec_no in sorted(records):
        dids = records[rec_no]
        out += bytes([rec_no, len(dids)])
        for did, value in dids:
            out += bytes([(did >> 8) & 0xFF, did & 0xFF]) + bytes(value)
    return bytes(out)


def build_extended_response(dtc: bytes, status: int, records: Mapping[int, bytes]) -> bytes:
    """Build a ``59 06`` response from ``{record: data}``."""
    out = bytearray([0x59, 0x06]) + bytes(dtc) + bytes([status])
    for rec_no in sorted(records):
        out += bytes([rec_no]) + bytes(records[rec_no])
    return bytes(out)


def snapshot_did_sizes_from(records: Mapping[int, Sequence[Tuple[int, bytes]]]) -> Dict[int, int]:
    """Size oracle derived from a known snapshot layout (simulator / label file)."""
    sizes: Dict[int, int] = {}
    for dids in records.values():
        for did, value in dids:
            sizes[did] = len(value)
    return sizes
