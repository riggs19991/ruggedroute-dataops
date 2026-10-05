"""
High-level VAG ECU session (UDS modules).

Wraps a :class:`~vagtune.uds.client.UdsClient` with the VAG-specific flows you run
all the time: read the identification block, read/clear fault codes (with VCDS-style
decoding, snapshots and extended data), read/write coding with the safety wrapper,
the VCDS-style 5-digit login, DID scans, output tests, routines (basic settings),
unlock calibration security with the right SA2 script, and read a calibration block
out of flash.

This is the object a GUI or the CLI drives. It owns the tester-present keepalive
during security-sensitive work.

Safety invariants (binding, see CLAUDE.md / DESIGN_0.2 §8): every DID write (coding
0x0600 via :meth:`VagEcuSession.write_coding`, any other DID - adaptation, workshop
code - via :meth:`VagEcuSession.write_did`) needs a backup taken *before* the write,
refuses when the module's identity (F187/F189/F191) differs from the backup's, is a
dry run by default, needs ``confirm=True`` to touch the module and verifies by
read-back. Mappings PROTOCOL_FACTS lists as Reported (the login level/key rule, the
``2E 0600`` coding write, adaptation DIDs written with 0x2E) are flagged UNVERIFIED
and warn once.
"""

from __future__ import annotations

import datetime as _dt
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Mapping, Optional, Sequence, Union

from ..uds import dtc as udsdtc
from ..uds import services as S
from ..uds.client import SeedKeyFn, UdsClient
from ..uds.exceptions import NegativeResponse, UdsTimeout, UnexpectedResponse
from .dtc import VagDtc, decode_dtc_number, decode_uds_dtc, describe_dtc, warn_unverified
from .profiles import EcuProfile, FlashBlock, guess_profile
from .sa2 import make_seed_key_fn

log = logging.getLogger(__name__)


class CodingSafetyError(RuntimeError):
    """A coding/DID write was refused by the safety wrapper (no backup, identity
    mismatch, missing confirmation, read-back mismatch)."""


# --------------------------------------------------------------------- identity

@dataclass(frozen=True)
class IdentDidSpec:
    did: int
    key: str          # attribute-style name used in to_dict()
    name: str         # human label
    decode: str = "ascii"   # ascii | hex | u8 | u24 | bcd


# Every identification DID the session reads, in display order. The 0.1.0 list in
# vag/modules.py (IDENT_DIDS) is a subset; it is consulted for its labels so the two
# never disagree.
IDENT_DID_SPECS: List[IdentDidSpec] = [
    IdentDidSpec(0xF190, "vin", "VIN"),
    IdentDidSpec(0xF187, "part_number", "VW Spare Part Number"),
    IdentDidSpec(0xF189, "software_version", "VW Application Software Version"),
    IdentDidSpec(0xF191, "hardware_number", "VW ECU Hardware Number"),
    IdentDidSpec(0xF1A3, "hardware_version", "VW ECU Hardware Version"),
    IdentDidSpec(0xF197, "system_name", "VW System Name / Engine Type"),
    IdentDidSpec(0xF1AD, "engine_code", "Engine Code Letters"),
    IdentDidSpec(0xF17C, "fazit", "VW FAZIT Identification String"),
    IdentDidSpec(0xF18C, "serial_number", "ECU Serial Number"),
    IdentDidSpec(0xF19E, "odx_id", "ASAM/ODX File Identifier"),
    IdentDidSpec(0xF1A2, "odx_version", "ASAM/ODX File Version"),
    IdentDidSpec(0xF1DF, "programming_info", "ECU Programming Information", "hex"),
    IdentDidSpec(0xF1F4, "bootloader_id", "Boot Loader Identification"),
    IdentDidSpec(0xF186, "active_session", "Active Diagnostic Session", "u8"),
    IdentDidSpec(0x0600, "coding", "VW Coding Value (long coding)", "hex"),
    IdentDidSpec(0xF1A5, "coding_fingerprint", "VW Coding Fingerprint (WSC/serial)", "hex"),
    IdentDidSpec(0xF15B, "programming_log", "Fingerprint and Programming Date", "hex"),
    IdentDidSpec(0xF198, "repair_shop_code", "Repair Shop Code / Tester Serial", "hex"),
    IdentDidSpec(0xF199, "programming_date", "Programming Date", "bcd"),
    IdentDidSpec(0xF1AA, "workshop_system_name", "VW Workshop System Name"),
    IdentDidSpec(0xF1AB, "block_versions", "VW Logical Software Block Version"),
    IdentDidSpec(0xF17E, "production_change_number", "ECU Production Change Number"),
    IdentDidSpec(0x0405, "flash_state", "State Of Flash Memory", "hex"),
    IdentDidSpec(0x0407, "programming_attempts", "Programming Attempts (per block)", "hex"),
    IdentDidSpec(0x0408, "successful_programming", "Successful Programming Attempts", "hex"),
    IdentDidSpec(0x295A, "vehicle_mileage", "Vehicle Mileage (km)", "u24"),
    IdentDidSpec(0x295B, "module_mileage", "Control Module Mileage (km)", "u24"),
    IdentDidSpec(0xF804, "calibration_id", "Calibration ID"),
    IdentDidSpec(0xF806, "cvn", "Calibration Verification Numbers", "hex"),
    IdentDidSpec(0xF18A, "supplier_id", "System Supplier Identifier"),
    IdentDidSpec(0xF18B, "manufacturing_date", "ECU Manufacturing Date", "bcd"),
    IdentDidSpec(0xF192, "supplier_hw_number", "Supplier ECU Hardware Number"),
    IdentDidSpec(0xF194, "supplier_sw_number", "Supplier ECU Software Number"),
]
IDENT_DID_BY_NUMBER: Dict[int, IdentDidSpec] = {s.did: s for s in IDENT_DID_SPECS}
IDENT_DID_BY_KEY: Dict[str, IdentDidSpec] = {s.key: s for s in IDENT_DID_SPECS}

# Identity DIDs a backup must match before any write (CLAUDE.md invariant: F187/F189;
# the hardware number is added because coding depends on it).
IDENTITY_CHECK_DIDS = (0xF187, 0xF189, 0xF191)


def decode_ident(spec: IdentDidSpec, raw: bytes) -> str:
    if spec.decode == "hex":
        return raw.hex(" ").upper()
    if spec.decode == "u8":
        return str(raw[0]) if raw else ""
    if spec.decode == "u24":
        return str(int.from_bytes(raw, "big")) if raw else ""
    if spec.decode == "bcd":
        return "".join(f"{b:02X}" for b in raw)
    text = raw.split(b"\x00", 1)[0].decode("latin-1", errors="replace").rstrip()
    return text or raw.hex(" ").upper()


@dataclass
class EcuIdentity:
    """Decoded identification DIDs (``values``) plus their raw bytes (``raw``)."""
    values: Dict[int, str]
    raw: Dict[int, bytes] = field(default_factory=dict)

    def get(self, did: int) -> Optional[str]:
        return self.values.get(did)

    @property
    def vin(self) -> Optional[str]:
        return self.values.get(0xF190)

    @property
    def part_number(self) -> Optional[str]:
        return self.values.get(0xF187)

    @property
    def software_version(self) -> Optional[str]:
        return self.values.get(0xF189)

    @property
    def hardware_number(self) -> Optional[str]:
        return self.values.get(0xF191)

    @property
    def hardware_version(self) -> Optional[str]:
        return self.values.get(0xF1A3)

    @property
    def system_name(self) -> Optional[str]:
        return self.values.get(0xF197)

    @property
    def engine_code(self) -> Optional[str]:
        return self.values.get(0xF1AD)

    @property
    def fazit(self) -> Optional[str]:
        return self.values.get(0xF17C)

    @property
    def serial_number(self) -> Optional[str]:
        return self.values.get(0xF18C)

    @property
    def odx_id(self) -> Optional[str]:
        return self.values.get(0xF19E)

    @property
    def odx_version(self) -> Optional[str]:
        return self.values.get(0xF1A2)

    @property
    def bootloader_id(self) -> Optional[str]:
        return self.values.get(0xF1F4)

    @property
    def coding(self) -> Optional[bytes]:
        return self.raw.get(0x0600)

    @property
    def coding_fingerprint(self) -> Optional[bytes]:
        return self.raw.get(0xF1A5)

    @property
    def vehicle_mileage_km(self) -> Optional[int]:
        raw = self.raw.get(0x295A)
        return int.from_bytes(raw, "big") if raw else None

    @property
    def module_mileage_km(self) -> Optional[int]:
        raw = self.raw.get(0x295B)
        return int.from_bytes(raw, "big") if raw else None

    @property
    def active_session(self) -> Optional[int]:
        raw = self.raw.get(0xF186)
        return raw[0] if raw else None

    def identity_key(self) -> Dict[str, Optional[str]]:
        """The DIDs that must match a backup (F187/F189/F191)."""
        return {f"{did:04X}": self.values.get(did) for did in IDENTITY_CHECK_DIDS}

    def to_dict(self) -> Dict[str, Any]:
        """JSON-friendly form: named fields plus every DID by hex number."""
        out: Dict[str, Any] = {}
        for spec in IDENT_DID_SPECS:
            if spec.did in self.values:
                out[spec.key] = self.values[spec.did]
        out["dids"] = {f"{did:04X}": {"name": IDENT_DID_BY_NUMBER[did].name if did in IDENT_DID_BY_NUMBER
                                      else S.did_name(did),
                                      "value": self.values[did],
                                      "raw": self.raw[did].hex() if did in self.raw else None}
                       for did in sorted(self.values)}
        return out

    def pretty(self) -> str:
        lines = []
        for spec in IDENT_DID_SPECS:
            v = self.values.get(spec.did)
            if v:
                lines.append(f"  {spec.name:<36} {v}")
        return "\n".join(lines)


# --------------------------------------------------------------------- DTC views

@dataclass
class DtcEntry:
    """0.1.0 view of a fault (kept for the ``dtc`` command and tests)."""
    number: int
    status: int
    code: str
    description: str

    def __str__(self) -> str:
        return f"{self.code}  (0x{self.number:06X}, status 0x{self.status:02X})  {self.description}"


@dataclass
class VagDtcDetail:
    """A decoded fault with its snapshot and extended-data records.

    Record contents stay raw bytes: PROTOCOL_FACTS verifies only the *field names*
    VCDS shows (priority, frequency, reset counter, mileage, time), not their byte
    offsets inside the 0x06 records, so nothing here pretends to decode them.
    """
    dtc: VagDtc
    snapshots: List[udsdtc.DtcSnapshot] = field(default_factory=list)
    extended: List[udsdtc.DtcExtendedData] = field(default_factory=list)
    snapshot_error: Optional[str] = None
    extended_error: Optional[str] = None

    def __str__(self) -> str:
        return str(self.dtc)


@dataclass
class MeasuringDid:
    did: int
    raw: bytes
    name: str
    value: Any
    unit: str = ""
    decoded: bool = False


@dataclass
class CodingWriteResult:
    did: int
    old: bytes
    new: bytes
    dry_run: bool
    written: bool
    verified: bool
    backup_identity: Dict[str, Optional[str]]

    def __str__(self) -> str:
        mode = "DRY RUN" if self.dry_run else ("WRITTEN+VERIFIED" if self.verified else "WRITTEN (unverified)")
        return f"coding DID 0x{self.did:04X}: {self.old.hex()} -> {self.new.hex()} [{mode}]"


# --------------------------------------------------------------------- login rule

def login_seed_key_fn(code: int) -> SeedKeyFn:
    """Seed -> key for the VCDS-style 5-digit login on a UDS module.

    UNVERIFIED (PROTOCOL_FACTS uds_vag.md §O / REPORTED): the real derivation is not
    known from any fetched source, and the facts say explicitly *not* to assume
    ``key = seed + 0x11170`` or ``key == code``. This candidate — ``key = u32(seed) +
    code`` — is the rule the simulator accepts so the flow can be exercised offline;
    on a real module a wrong key is answered with NRC 0x35 and nothing is written.
    Pass your own ``seed_key_fn`` to :meth:`VagEcuSession.login` once the rule for a
    module is known from a trace.
    """
    if not 0 <= code <= 65535:
        raise ValueError("a VAG login code is 0..65535 (5 digits)")

    def fn(level: int, seed: bytes) -> bytes:
        n = len(seed) or 4
        value = (int.from_bytes(seed, "big") + (code & 0xFFFF)) & ((1 << (8 * n)) - 1)
        return value.to_bytes(n, "big")

    return fn


# --------------------------------------------------------------------- session

class VagEcuSession:
    CODING_DID = 0x0600

    def __init__(self, client: UdsClient, profile: Optional[EcuProfile] = None) -> None:
        self.client = client
        self.profile = profile
        self._did_sizes: Dict[int, int] = {}   # learned sizes, feed the multi-DID oracle

    # -- identification ----------------------------------------------------------

    def read_identity(self, *, dids: Optional[Sequence[int]] = None) -> EcuIdentity:
        """Read every identification DID (single 0x22 each; a DID the module does not
        have answers NRC 0x31 and is skipped). Sizes seen are remembered so later
        multi-DID reads can batch."""
        values: Dict[int, str] = {}
        raw: Dict[int, bytes] = {}
        wanted = list(dids) if dids is not None else [s.did for s in IDENT_DID_SPECS]
        for did in wanted:
            try:
                data = self.client.read_data_by_identifier(did)
            except NegativeResponse as exc:
                log.debug("DID 0x%04X not available: %s", did, exc)
                continue
            raw[did] = data
            self._did_sizes[did] = len(data)
            spec = IDENT_DID_BY_NUMBER.get(did)
            if spec is not None:
                values[did] = decode_ident(spec, data)
            else:
                values[did] = decode_ident(IdentDidSpec(did, f"did_{did:04X}", S.did_name(did),
                                                        "ascii" if did in S.DID_COMMON_DECODE_ASCII else "hex"),
                                           data)
        return EcuIdentity(values, raw)

    def detect_profile(self, identity: Optional[EcuIdentity] = None) -> Optional[EcuProfile]:
        identity = identity or self.read_identity()
        name = identity.system_name or ""
        prof = guess_profile(name)
        if prof is not None:
            self.profile = prof
            log.info("detected ECU profile: %s", prof.display_name)
        else:
            log.info("could not auto-detect ECU profile from system name %r", name)
        return prof

    # -- DIDs ----------------------------------------------------------------------

    def read_did(self, did: int) -> bytes:
        data = self.client.read_data_by_identifier(did)
        self._did_sizes[did] = len(data)
        return data

    def read_dids(self, dids: Sequence[int], *, size_of: Optional[Mapping[int, int]] = None,
                  skip_unsupported: bool = True) -> Dict[int, bytes]:
        """Multi-DID read using the sizes learned so far (plus ``size_of``)."""
        oracle: Dict[int, int] = dict(self._did_sizes)
        if size_of:
            oracle.update(size_of)
        out = self.client.read_data_by_identifiers(dids, size_of=oracle, skip_unsupported=skip_unsupported)
        for did, data in out.items():
            self._did_sizes[did] = len(data)
        return out

    def make_did_backup(self, did: int, *, module: str = "") -> Dict[str, Any]:
        """The backup dict :meth:`write_did` requires: module identity (F187/F189/F191
        plus the full identification), the DID's current value and a UTC timestamp.
        Persist it (JSON) *before* writing. For DID 0x0600 this is
        :meth:`make_coding_backup`. A write-only DID (NRC on read) is recorded with
        ``value = None``; the write then cannot be verified by read-back."""
        if did == self.CODING_DID:
            return self.make_coding_backup(module=module)
        identity = self.read_identity()
        try:
            value: Optional[str] = self.read_did(did).hex()
        except NegativeResponse as exc:
            log.warning("DID 0x%04X cannot be read before writing (%s); backup holds no value",
                        did, exc)
            value = None
        return {
            "module": module,
            "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "identity": identity.identity_key(),
            "identity_full": identity.to_dict(),
            "did": f"{did:04X}",
            "value": value,
        }

    def write_did(self, did: int, data: bytes, *, backup: Mapping[str, Any],
                  confirm: bool = False, dry_run: bool = True) -> CodingWriteResult:
        """WriteDataByIdentifier (``2E <DID> <data>``) behind the same safety wrapper as
        :meth:`write_coding` (DESIGN_0.2 §8.5: dry-run is the default for coding and
        adaptation; backup before any write; identity must match the backup).

        Order of checks (each raises :class:`CodingSafetyError`):

        1. ``backup`` must come from :meth:`make_did_backup` for this DID;
        2. the module's current F187/F189/F191 must equal the backup's;
        3. the DID's current value must equal the backup's (unless the DID is
           write-only and the backup recorded no value);
        4. ``dry_run=True`` (default) stops here and reports what would happen;
        5. ``confirm=True`` is required to write.

        UNVERIFIED mapping (PROTOCOL_FACTS §7.6 Reported, medium): on UDS modules a
        VCDS adaptation channel is a DID written with 0x2E after login - the DID
        numbers live in the ODX and no write was captured on a real module, so the
        write warns once and is gated behind the explicit confirmation. After writing,
        the DID is read back and compared (a write-only DID is reported
        ``verified=False``, never as verified). DID 0x0600 is redirected to
        :meth:`write_coding`.
        """
        if did == self.CODING_DID:
            raise CodingSafetyError("use write_coding() for the coding DID (backup + identity check)")
        if not isinstance(backup, Mapping) or "identity" not in backup or "value" not in backup:
            raise CodingSafetyError("write_did needs the backup dict from make_did_backup()")
        if str(backup.get("did", "")).upper() != f"{did:04X}":
            raise CodingSafetyError(
                f"backup is for DID {backup.get('did')!r}, not 0x{did:04X}; take a backup of this DID")
        self._check_identity_against_backup(backup)
        new = bytes(data)
        if not new:
            raise CodingSafetyError("refusing to write an empty value")
        backup_value = backup["value"]
        readable = backup_value is not None
        if readable:
            old = self.read_did(did)
            if old.hex() != str(backup_value).lower():
                raise CodingSafetyError(
                    f"current value of DID 0x{did:04X} ({old.hex()}) differs from the backup "
                    f"({backup_value}); take a fresh backup first")
        else:
            old = b""
        result = CodingWriteResult(did, old, new, dry_run, False, False, dict(backup["identity"]))
        if dry_run:
            log.info("dry run: would write DID 0x%04X %s -> %s", did, old.hex() or "(write-only)", new.hex())
            return result
        if not confirm:
            raise CodingSafetyError(f"writing DID 0x{did:04X} needs confirm=True (and dry_run=False)")
        if readable and new == old:
            log.info("DID 0x%04X unchanged; nothing written", did)
            result.verified = True
            return result
        # UNVERIFIED: adaptation/workshop DIDs are written with 2E after login (Reported, medium).
        warn_unverified("adaptation-did-write-2e",
                        "DID write uses WriteDataByIdentifier 0x2E after login (UDS adaptation "
                        "channels are DIDs per PROTOCOL_FACTS §7.6 Reported); no VCDS trace "
                        "of such a write was captured")
        log.warning("writing DID 0x%04X: %s -> %s", did, old.hex() or "(write-only)", new.hex())
        self.client.write_data_by_identifier(did, new)
        result.written = True
        if not readable:
            log.warning("DID 0x%04X is write-only; the write could not be verified by read-back", did)
            return result
        readback = self.read_did(did)
        result.verified = readback == new
        if not result.verified:
            raise CodingSafetyError(
                f"read-back of DID 0x{did:04X} after write is {readback.hex()}, expected "
                f"{new.hex()}; restore from the backup ({old.hex()})")
        return result

    def _check_identity_against_backup(self, backup: Mapping[str, Any]) -> Dict[str, Optional[str]]:
        """Refuse (CodingSafetyError) unless the module's F187/F189/F191 equal the
        backup's ``identity``; returns the current identity key."""
        identity = self.read_identity(dids=list(IDENTITY_CHECK_DIDS))
        current_key = identity.identity_key()
        backup_key = {str(k).upper(): v for k, v in dict(backup["identity"]).items()}
        for did_hex, value in current_key.items():
            if backup_key.get(did_hex) != value:
                raise CodingSafetyError(
                    f"identity mismatch for DID {did_hex}: module reports {value!r}, "
                    f"backup has {backup_key.get(did_hex)!r}; refusing to write")
        return current_key

    def scan_dids(self, start: int = 0x0000, stop: int = 0x10000, *,
                  on_progress: Optional[Callable[[int, Any], None]] = None
                  ) -> Dict[int, Union[bytes, NegativeResponse]]:
        """Probe ``range(start, stop)``; see :meth:`UdsClient.scan_dids` for the
        0x31 vs 0x13/0x22/0x33/0x7F classification."""
        result = self.client.scan_dids(start, stop, on_progress=on_progress)
        for did, outcome in result.items():
            if isinstance(outcome, (bytes, bytearray)):
                self._did_sizes[did] = len(outcome)
        return result

    def read_measuring_did(self, did: int) -> MeasuringDid:
        """Read a measuring value DID. For the OBD mirror range 0xF400..0xF4FF the
        value is decoded with the J1979 PID table (``vagtune.obd.pids``, imported
        lazily; raw bytes when that package or the PID is unknown). Other DIDs are
        returned raw with their catalogue name (the IDE mapping lives in the ODX)."""
        raw = self.read_did(did)
        pid = S.obd_mirror_pid(did)
        if pid is not None:
            try:
                from ..obd import pids as obd_pids   # optional at runtime
            except ImportError:
                obd_pids = None
            if obd_pids is not None:
                d = obd_pids.pid_def(pid)
                if d is not None:
                    try:
                        value = obd_pids.decode_pid(pid, raw)
                        return MeasuringDid(did, raw, d.name, value, d.unit, decoded=True)
                    except (ValueError, IndexError) as exc:
                        log.debug("DID 0x%04X: PID %02X decode failed (%s); raw", did, pid, exc)
        return MeasuringDid(did, raw, S.did_name(did), raw, "", decoded=False)

    # -- fault codes -------------------------------------------------------------

    def read_dtcs(self, status_mask: int = 0xFF) -> List[DtcEntry]:
        raw = self.client.read_dtc_by_status_mask(status_mask)
        out: List[DtcEntry] = []
        for number, status in raw:
            code = decode_dtc_number(number)
            out.append(DtcEntry(number, status, code, describe_dtc(code)))
        return out

    def read_dtcs_decoded(self, status_mask: int = 0xFF) -> List[VagDtc]:
        return [decode_uds_dtc(d.bytes, d.status) for d in self.client.read_dtcs(status_mask)]

    def read_dtcs_detailed(self, with_snapshot: bool = True, with_extended: bool = True, *,
                           status_mask: int = 0xFF,
                           did_sizes: Optional[Mapping[int, int]] = None,
                           record_sizes: Optional[Mapping[int, int]] = None) -> List[VagDtcDetail]:
        """Every stored fault decoded VCDS-style, plus its 0x19 0x04 snapshots and
        0x19 0x06 extended data (raw where sizes are unknown).

        Neither a module that refuses a subfunction (NRC) nor a parser error aborts
        the list: the error text is kept per fault in ``snapshot_error`` /
        ``extended_error``. Record sizes are per module, so a ``record_sizes`` table
        from the wrong module misaligns the 0x06 walk (the parser then raises
        :class:`UnexpectedResponse`); in that case the extended data is re-read with
        no sizes so the raw bytes are still available for inspection."""
        sizes: Dict[int, int] = dict(self._did_sizes)
        if did_sizes:
            sizes.update(did_sizes)
        out: List[VagDtcDetail] = []
        for d in self.client.read_dtcs(status_mask):
            detail = VagDtcDetail(decode_uds_dtc(d.bytes, d.status))
            if with_snapshot:
                try:
                    detail.snapshots = self.client.read_dtc_snapshot(d.dtc, 0xFF, sizes).records
                except (NegativeResponse, UnexpectedResponse) as exc:
                    detail.snapshot_error = str(exc)
                    log.warning("snapshot of %s not decoded: %s", detail.dtc.sae_code, exc)
            if with_extended:
                try:
                    detail.extended = self.client.read_dtc_extended_data(d.dtc, 0xFF, record_sizes).records
                except NegativeResponse as exc:
                    detail.extended_error = str(exc)
                except UnexpectedResponse as exc:
                    detail.extended_error = str(exc)
                    log.warning("extended data of %s not decoded with the given record sizes (%s); "
                                "keeping it raw", detail.dtc.sae_code, exc)
                    try:
                        detail.extended = self.client.read_dtc_extended_data(d.dtc, 0xFF, None).records
                    except (NegativeResponse, UnexpectedResponse) as exc2:
                        detail.extended_error = f"{exc}; raw re-read failed: {exc2}"
            out.append(detail)
        return out

    def clear_dtcs(self, group: int = S.CLEAR_ALL_DTC_GROUPS) -> None:
        self.client.clear_diagnostic_information(group)

    # -- coding --------------------------------------------------------------------

    def read_coding(self) -> bytes:
        """``22 06 00`` -> the long coding bytes (length is module dependent; verified)."""
        return self.read_did(self.CODING_DID)

    def make_coding_backup(self, *, module: str = "") -> Dict[str, Any]:
        """The backup dict :meth:`write_coding` requires: identity, current coding,
        timestamp. Persist it (JSON) *before* writing."""
        identity = self.read_identity()
        coding = self.read_coding()
        return {
            "module": module,
            "timestamp": _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds"),
            "identity": identity.identity_key(),
            "identity_full": identity.to_dict(),
            "did": f"{self.CODING_DID:04X}",
            "coding": coding.hex(),
        }

    def write_coding(self, new_bytes: bytes, *, backup: Mapping[str, Any],
                     confirm: bool = False, dry_run: bool = True) -> CodingWriteResult:
        """Write DID 0x0600 with the safety wrapper.

        Order of checks (each raises :class:`CodingSafetyError`):

        1. ``backup`` must carry ``identity`` and ``coding`` (from :meth:`make_coding_backup`);
        2. the module's current F187/F189/F191 must equal the backup's;
        3. the current coding must equal the backup's (someone else wrote in between);
        4. the new value must have the module's coding length;
        5. ``dry_run=True`` (default) stops here and reports what would happen;
        6. ``confirm=True`` is required to write.

        The write itself (``2E 06 00 <bytes>``) is UNVERIFIED on real modules
        (VW_Flash only reads 0x0600; VCDS traces were not captured), so it warns once
        and is gated behind the explicit confirmation. The module must be in the
        extended session and logged in (:meth:`login`) first, or it answers NRC
        0x7F/0x33. After writing, the coding is read back and compared.
        """
        if not isinstance(backup, Mapping) or "identity" not in backup or "coding" not in backup:
            raise CodingSafetyError("write_coding needs the backup dict from make_coding_backup()")
        current_key = self._check_identity_against_backup(backup)
        old = self.read_coding()
        if old.hex() != str(backup["coding"]).lower():
            raise CodingSafetyError(
                f"current coding {old.hex()} differs from the backup {backup['coding']}; "
                "take a fresh backup first")
        new = bytes(new_bytes)
        if len(new) != len(old):
            raise CodingSafetyError(f"new coding is {len(new)} bytes, module coding is {len(old)}")
        result = CodingWriteResult(self.CODING_DID, old, new, dry_run, False, False, current_key)
        if dry_run:
            log.info("dry run: would write coding %s -> %s", old.hex(), new.hex())
            return result
        if not confirm:
            raise CodingSafetyError("writing coding needs confirm=True (and dry_run=False)")
        if new == old:
            log.info("coding unchanged; nothing written")
            result.verified = True
            return result
        # UNVERIFIED: 2E 0600 is the symmetric WriteDataByIdentifier; not captured on a VAG trace.
        warn_unverified("coding-write-2e-0600",
                        "coding write uses WriteDataByIdentifier 0x2E on DID 0x0600 "
                        "(symmetric to the verified read; confirm with a VCDS recode trace)")
        log.warning("writing coding DID 0x0600: %s -> %s", old.hex(), new.hex())
        self.client.write_data_by_identifier(self.CODING_DID, new)
        result.written = True
        readback = self.read_coding()
        result.verified = readback == new
        if not result.verified:
            raise CodingSafetyError(
                f"read-back after write is {readback.hex()}, expected {new.hex()}; "
                f"restore from the backup ({old.hex()})")
        return result

    # -- security ----------------------------------------------------------------

    def enter_extended_session(self) -> None:
        self.client.diagnostic_session_control(S.Session.EXTENDED_DIAGNOSTIC)

    def enter_programming_session(self) -> None:
        self.client.diagnostic_session_control(S.Session.PROGRAMMING)

    def login(self, code: int, *, level: int = S.SECURITY_LEVEL_VAG_LOGIN,
              seed_key_fn: Optional[SeedKeyFn] = None) -> None:
        """VCDS-style "Security Access (16)" login with a 5-digit code.

        UNVERIFIED mapping (PROTOCOL_FACTS uds_vag.md REPORTED): the login is sent as
        SecurityAccess requestSeed ``27 03`` / sendKey ``27 04`` (the level VW_Flash's
        fake data and secondary sources use for coding), and the key is derived with
        :func:`login_seed_key_fn` unless you pass ``seed_key_fn``. Both warn once.
        Real modules lock the level after a few wrong keys, so this never retries.
        """
        if level % 2 == 0 or not 0 < level < 0x80:
            raise ValueError("level must be the odd requestSeed subfunction")
        warn_unverified("vag-login-level",
                        f"5-digit login sent as SecurityAccess level 0x{level:02X}/0x{level + 1:02X}; "
                        "the real coding level per module is unconfirmed (trace a VCDS recode)")
        if seed_key_fn is None:
            warn_unverified("vag-login-key",
                            "login key derived with the candidate rule key = u32(seed) + code; "
                            "no real module is known to accept it (the simulator does)")
            seed_key_fn = login_seed_key_fn(code)
        self.client.security_access(level, seed_key_fn)

    def unlock(self, sa2_script: Optional[bytes] = None, level: Optional[int] = None) -> None:
        """Unlock calibration security using an SA2 script.

        Resolution order for the script:
          1. explicit ``sa2_script`` argument,
          2. the active profile's ``sa2_script``.
        If neither is available, raises - you must supply or extract the script.
        The default level 0x11 is recorded in CLAUDE.md but UNVERIFIED by any fetched
        source (uds_vag.md §O), so it warns once when used implicitly.
        """
        script = sa2_script
        if script is None and self.profile is not None:
            script = self.profile.sa2_script
        if script is None:
            raise ValueError(
                "No SA2 script available for this ECU. Supply sa2_script=... "
                "(extract it from the ECU's ODX/FRF container)."
            )

        if level is None:
            sec_level = self.profile.security_level if self.profile else S.SECURITY_LEVEL_VAG_FLASH
            if sec_level == S.SECURITY_LEVEL_VAG_FLASH:
                warn_unverified("flash-security-level-11",
                                "calibration security level 0x11/0x12 comes from CLAUDE.md, "
                                "not from a fetched source; confirm with a trace")
        else:
            sec_level = level
        self.client.security_access(sec_level, make_seed_key_fn(script))

    # -- outputs / routines ------------------------------------------------------

    def io_control(self, did: int, option: int = S.IoControlOption.SHORT_TERM_ADJUSTMENT,
                   data: bytes = b"") -> bytes:
        """Output test on a manufacturer DID (``2F <DID> 03 <value>``); the DID numbers
        are per-module (ODX). Returns the status bytes the module echoes."""
        return self.client.io_control(did, option, data)

    def return_control(self, did: int) -> bytes:
        return self.client.return_control(did)

    def routine(self, rid: int, action: str = "start", data: bytes = b"") -> bytes:
        """RoutineControl helper: ``action`` is ``start`` | ``stop`` | ``results``
        (VCDS "Basic Settings" on UDS modules are routines; ids live in the ODX)."""
        if action == "start":
            return self.client.routine_start(rid, data)
        if action == "stop":
            return self.client.routine_stop(rid, data)
        if action in ("results", "result"):
            return self.client.routine_results(rid, data)
        raise ValueError("action must be start, stop or results")

    # -- calibration read --------------------------------------------------------

    def read_block(
        self,
        block: FlashBlock,
        progress: Optional[Callable[[int, int], None]] = None,
    ) -> bytes:
        """Read a flash block via UDS upload (RequestUpload + TransferData loop)."""
        log.info("reading block %s: 0x%X bytes at 0x%08X", block.name, block.length, block.start)
        return self.client.upload(block.start, block.length, progress=progress)

    def read_calibration(self, progress: Optional[Callable[[int, int], None]] = None) -> bytes:
        if self.profile is None:
            raise ValueError("No ECU profile set; call detect_profile() or pass one in.")
        cal = self.profile.calibration_block()
        if cal is None or cal.length == 0:
            raise ValueError(f"profile {self.profile.key} has no CAL block defined")
        return self.read_block(cal, progress=progress)

    # -- convenience -------------------------------------------------------------

    def full_report(self) -> str:
        identity = self.read_identity()
        lines = ["ECU Identification:", identity.pretty(), "", "Fault codes:"]
        try:
            dtcs = self.read_dtcs_decoded()
            if dtcs:
                lines += [f"  {d}" for d in dtcs]
            else:
                lines.append("  (none stored)")
        except (NegativeResponse, UdsTimeout) as exc:
            lines.append(f"  (could not read DTCs: {exc})")
        return "\n".join(lines)
