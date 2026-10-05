"""
VAG DTC knowledge and the VagEcuSession extensions: numbering vectors (5-/6-digit),
FTB and KWP elaboration tables with their UNVERIFIED warnings, the packaged
database, VCDS-style rendering, detailed DTC reads, coding write safety, login and
measuring-value DIDs - all against the simulated ECU.
"""

from __future__ import annotations

import json
import logging

import pytest

from vagtune import data as vdata
from vagtune.transport.fake import SIM_EXTENDED_RECORD_SIZES, SIM_SNAPSHOT_DID_SIZES, make_fake_pair
from vagtune.uds import dtc as D
from vagtune.uds.client import UdsClient
from vagtune.uds.exceptions import NegativeResponse
from vagtune.vag import dtc as V
from vagtune.vag.ecu import (
    CodingSafetyError,
    EcuIdentity,
    VagEcuSession,
    login_seed_key_fn,
)


@pytest.fixture(autouse=True)
def _fresh_warnings():
    V._reset_unverified_warnings()
    yield
    V._reset_unverified_warnings()


def _session():
    link, ecu = make_fake_pair(0x7E0, 0x7E8)
    client = UdsClient(link)
    return VagEcuSession(client), ecu, link


def _unverified_messages(caplog, needle: str):
    return [r.getMessage() for r in caplog.records
            if "UNVERIFIED mapping" in r.getMessage() and needle in r.getMessage()]


# ----------------------------------------------------------------- numbering

@pytest.mark.parametrize("code,five", [
    ("P0000", 16384), ("P0101", 16485), ("P0299", 16683), ("P1556", 17964), ("P1602", 18010),
    ("P1296", 17704), ("P0506", 16890), ("U0103", 28775), ("U1100", 29796), ("U1101", 29797),
    ("P3101", 19557), ("C0035", 20515), ("B0001", 24577),
])
def test_vag5_rule(code, five):
    assert V.vag5_from_code(code) == five
    assert V.legacy_number(code) == five
    assert V.code_from_vag5(five) == code


def test_vag5_undefined_for_hex_letter_codes_and_factory_numbers():
    assert V.vag5_from_code("P17BF") is None and V.vag5_from_code("P00AF") is None
    assert V.code_from_vag5(287) is None and V.code_from_vag5(32768) is None
    assert V.code_from_vag5(0x4000 + 1000) is None     # last-three field 1000 is not decimal
    assert V.is_factory_only(287) and not V.is_factory_only(16683)


@pytest.mark.parametrize("code,six", [
    ("P0101", 257), ("P0299", 665), ("P1556", 5462), ("P1602", 5634), ("P173C", 5948),
    ("P00AF", 175), ("P2404", 9220), ("U1013", 53267), ("P2002", 8194), ("P0401", 1025),
    ("P1296", 4758),
])
def test_vag6_rule(code, six):
    assert V.vag6_from_code(code) == six
    assert V.code_from_vag6(six) == code
    assert f"{six:06d}" == V.decode_uds_dtc(V.sae_bytes_from_code(code) + b"\x00", 0).vag6


def test_sae_byte_packing():
    assert V.sae_bytes_from_code("P0299") == b"\x02\x99"
    assert V.sae_code_from_bytes(0xC1, 0x58) == "U0158"
    assert V.decode_dtc_number(0x4035FF) == "C0035"
    assert D.sae_code(0x80, 0x01) == "B0001"
    with pytest.raises(ValueError):
        V.sae_bytes_from_code("P4000")


# ----------------------------------------------------------------- FTB / KWP tables

def test_ftb_table_verified_rows_and_categories(caplog):
    caplog.set_level(logging.WARNING)
    row = V.describe_ftb(0x11)
    assert row.text == "Circuit Short to Ground" and row.verified and row.category == "General Electrical Failures"
    assert V.describe_ftb(0x96).text == "Component Internal Failure"
    assert V.describe_ftb(0x87).text == "Missing Message" and V.ftb_category(0x87) == "Bus Signal/Message Failures"
    assert V.describe_ftb(0x54).text == "Missing Calibration"
    assert V.describe_ftb(0x00).text == "No Subtype Information"
    assert V.FTB_CATEGORIES[0xF].startswith("Vehicle Manufacturer")
    assert not _unverified_messages(caplog, "failure-type")
    verified = sorted(c for c, r in V.FTB_TABLE.items() if r.verified)
    assert 0x18 in verified and 0x19 in verified and 0x1C not in verified and 0x72 not in verified


def test_ftb_unverified_row_warns_once(caplog):
    caplog.set_level(logging.WARNING)
    row = V.describe_ftb(0x1C)
    assert row.unverified and row.text == "Circuit Voltage Out of Range"
    V.describe_ftb(0x1C)
    assert len(_unverified_messages(caplog, "0x1C")) == 1
    unknown = V.describe_ftb(0xA5)
    assert unknown.unverified and "ISO/SAE reserved" in unknown.text


def test_kwp_elaboration_table_and_intermittent_bit(caplog):
    caplog.set_level(logging.WARNING)
    assert len(V.KWP_ELABORATION) == 83
    assert V.KWP_ELABORATION[0x10] == "Signal Outside Specifications"
    assert V.KWP_ELABORATION[0x1B] == "Implausible Signal" and V.KWP_ELABORATION[0x52] == "Activated"
    assert V.describe_kwp_elaboration(0x35) == ("Supply Voltage Too Low", False)
    assert V.describe_kwp_elaboration(0xB5) == ("Supply Voltage Too Low", True)
    assert len(_unverified_messages(caplog, "KWP")) == 1


# ----------------------------------------------------------------- database

def test_database_loads_once_from_package_data():
    V._reset_db_cache()
    db = V.load_db()
    assert db is not None and db is V.load_db()
    assert db.size < 1_000_000 and vdata.data_size(vdata.DTC_DB_FILENAME) == db.size
    assert "dtc_db.json" in vdata.list_data()
    assert len(db) > 10_000 and db.stats["codes"] == len(db)
    raw = vdata.read_json(vdata.DTC_DB_FILENAME)
    assert set(raw) == {"source_notes", "stats", "codes", "vag_wording", "vag_5digit_only", "vag_fault_variants"}
    assert "provenance" not in raw and "vag_legacy" not in raw
    assert "lntake" not in json.dumps(raw["codes"])
    assert "P0000" not in db.codes and "U0074" not in db.codes      # placeholders dropped


@pytest.mark.parametrize("code,generic,vag", [
    ("P0299", "Turbo/Super Charger Underboost", "Boost Pressure Regulation: Control Range Not Reached"),
    ("P17BF", "Hydraulic Pump System Overload Protection (DSG mechatronic)", None),
    ("U0100", "Lost Communication With ECM/PCM A", "No Communication with Engine Control Module (SAE ECM/PCM)"),
    ("B0001", "Driver Frontal Stage 1 Deployment Control", None),
    ("C0001", "TCS Control Channel A Valve 1", None),
    ("P0101", "Mass or Volume Air Flow Circuit Range/Performance", "Mass Air Flow Sensor (G70): Implausible Signal"),
    ("P1556", "Charge Pressure Control: Negative Deviation", "Charge Pressure Control: Negative Deviation"),
    ("P173C", "Position Sensor 3 for Gear Selector: Implausible Signal", None),
    ("B100D", "Driver's Safety Belt Tensioner Igniter 2", "Driver's Safety Belt Tensioner Igniter 2"),
    ("C10E2", "Control Module for Electronic Parking Brake", None),
])
def test_database_lookups(code, generic, vag):
    info = V.lookup(code)
    assert info.found and info.description == generic and info.vag_wording == vag
    assert info.text(prefer_vag=True) == (vag or generic)
    assert info.text(prefer_vag=False) == generic


def test_database_factory_codes_and_variants():
    assert V.lookup_factory(287) == "ABS Wheel Speed Sensor Rear Right (G44)"
    assert V.lookup_factory(1324) == "Control Module for All Wheel Drive (J492)"
    assert V.lookup_factory(448) == "Haldex Clutch Pump (V181)"
    assert V.lookup_factory(543) == "Maximum Engine Speed Exceeded"
    assert V.lookup_factory(99999) is None
    db = V.load_db()
    assert "Signal Outside Specifications" in db.factory_variants(287)
    assert V.lookup("ZZZZZ").found is False


def test_describe_dtc_keeps_curated_wording_and_can_prefer_vag():
    assert V.describe_dtc("P0112") == "Intake Air Temperature Sensor Circuit Low"
    assert V.describe_dtc("P0299", prefer_vag=True) == "Boost Pressure Regulation: Control Range Not Reached"
    assert V.describe_dtc("P0299") == "Turbocharger/Supercharger Underboost Condition"
    assert V.describe_dtc("P1FFF").startswith("Manufacturer-specific powertrain")


# ----------------------------------------------------------------- VagDtc decode

def test_decode_uds_dtc_vcds_style_p0299():
    d = V.decode_uds_dtc(b"\x02\x99\x00", 0x60)
    assert d.sae_code == "P0299" and d.ftb == 0 and d.status == 0x60
    assert d.vag6 == "000665" and d.vag5 == 16683 and d.number == 0x029900
    assert d.ftb_text == "No Subtype Information" and d.ftb_verified
    assert d.status_text == "testFailedSinceLastClear, testNotCompletedThisOperationCycle"
    assert d.intermittent and not d.active
    assert d.vag_wording == "Boost Pressure Regulation: Control Range Not Reached"
    assert V.vcds_style(d) == "P0299 00 [096] - Boost Pressure Regulation: Control Range Not Reached"
    assert str(d) == V.vcds_style(d)
    d2 = V.decode_uds_dtc(0x200211, 0xE7)
    assert d2.sae_code == "P2002" and d2.vag6 == "008194" and d2.ftb_text == "Circuit Short to Ground"
    assert d2.active and V.vcds_style(d2).startswith("P2002 11 [231] - ")
    hexcode = V.decode_uds_dtc(b"\x17\xBF\x00", 0x08)
    assert hexcode.sae_code == "P17BF" and hexcode.vag5 is None and hexcode.factory_number is None


def test_decode_kwp_dtc_sae_and_factory(caplog):
    caplog.set_level(logging.WARNING)
    d = V.decode_kwp_dtc(16683, 0x10)
    assert d.sae_code == "P0299" and d.vag5 == 16683 and d.vag6 == "000665" and d.source == "kwp"
    assert d.ftb_text == "Signal Outside Specifications" and not d.intermittent and d.active
    assert V.vcds_style(d) == ("16683 - P0299 - Boost Pressure Regulation: Control Range Not Reached"
                               " - Signal Outside Specifications")
    inter = V.decode_kwp_dtc(b"\x41\x2B", 0x90)
    assert inter.intermittent and V.vcds_style(inter).endswith("- Intermittent")
    f = V.decode_kwp_dtc(287, 0x39)
    assert f.is_factory_only and f.sae_code == "" and f.vag5 == 287 and f.vag6 is None
    assert f.factory_number == "00287" and f.number == 287
    assert f.text == "ABS Wheel Speed Sensor Rear Right (G44)"
    assert "Signal Outside Specifications" in f.variants
    assert V.vcds_style(f) == "00287 - ABS Wheel Speed Sensor Rear Right (G44) - Electric Circuit Failure"
    assert len(_unverified_messages(caplog, "KWP")) == 1     # warned once for three decodes
    nothing = V.decode_kwp_dtc(0x8355, 0x00)
    assert nothing.is_factory_only and nothing.vag5 == 0x8355 and "no description" in nothing.text


# ----------------------------------------------------------------- VagEcuSession

def test_read_identity_full_did_list_and_to_dict():
    session, ecu, link = _session()
    ident = session.read_identity()
    assert ident.vin == "WVWZZZAUZLW000001" and ident.part_number == "8V0906259H"
    assert ident.engine_code == "DGUA" and ident.fazit == "ZSC-86415.07.18784303 20"
    assert ident.bootloader_id.startswith("MDG1") and ident.odx_id.startswith("EV_ECM18TFS")
    assert ident.coding == bytes.fromhex("091900122426000E3004")
    assert ident.coding_fingerprint == bytes.fromhex("000003781FD7")
    assert ident.vehicle_mileage_km == 123456 and ident.module_mileage_km == 123456
    assert ident.active_session == 1
    assert ident.values[0xF199] == "200717" and ident.values[0x0405] == "00"
    d = ident.to_dict()
    assert d["vin"] == ident.vin and d["coding"] == "09 19 00 12 24 26 00 0E 30 04"
    assert d["dids"]["F190"] == {"name": "VIN", "value": ident.vin, "raw": b"WVWZZZAUZLW000001".hex()}
    assert d["dids"]["295A"]["value"] == "123456"
    assert ident.identity_key() == {"F187": "8V0906259H", "F189": "0001", "F191": "03C906016AB"}
    assert "VW FAZIT Identification String" in ident.pretty()
    assert 0x12FC not in ident.values     # locked DID skipped (NRC), not an error
    assert EcuIdentity({}).vin is None and EcuIdentity({}).to_dict() == {"dids": {}}


def test_read_dtcs_detailed_with_and_without_sizes():
    session, ecu, link = _session()
    details = session.read_dtcs_detailed(did_sizes=SIM_SNAPSHOT_DID_SIZES,
                                         record_sizes=SIM_EXTENDED_RECORD_SIZES)
    assert [d.dtc.sae_code for d in details] == ["P0112", "P0561"]
    first = details[0]
    # VagDtc.text prefers the VW wording (what VCDS prints) over the SAE wording.
    assert str(first) == "P0112 00 [047] - Intake Air Temperature Sensor (G42): Signal too Low"
    assert first.dtc.description == "Intake Air Temperature Sensor 1 Circuit Low"
    assert first.snapshots[0].complete and first.snapshots[0].value(0x295A) == (123456).to_bytes(3, "big")
    assert [r.record for r in first.extended] == [1, 2, 3, 4, 5] and first.extended[0].data == b"\x02"
    raw = session.read_dtcs_detailed()
    assert not raw[0].snapshots[0].complete and raw[0].snapshots[0].raw
    assert raw[0].extended[0].data == b"" and raw[0].extended[0].raw
    only = session.read_dtcs_detailed(with_snapshot=False, with_extended=False)
    assert only[0].snapshots == [] and only[0].extended == []
    decoded = session.read_dtcs_decoded()
    assert decoded[1].sae_code == "P0561" and decoded[1].vag5 == 16384 + 561
    assert "P0112 00 [047]" in session.full_report()
    ecu.custom_handlers[0x19] = lambda req: b"\x7F\x19\x12" if req[1] == 0x06 else ecu._svc_read_dtc(req)
    partial = session.read_dtcs_detailed(did_sizes=SIM_SNAPSHOT_DID_SIZES)
    assert partial[0].extended == [] and "NRC 0x12" in partial[0].extended_error


def test_coding_backup_dry_run_confirm_and_identity_mismatch(caplog):
    caplog.set_level(logging.WARNING)
    session, ecu, link = _session()
    backup = session.make_coding_backup(module="engine")
    assert backup["coding"] == "091900122426000e3004" and backup["identity"]["F187"] == "8V0906259H"
    assert backup["identity_full"]["vin"] == "WVWZZZAUZLW000001"
    new = bytes.fromhex("091900122426000E3005")

    dry = session.write_coding(new, backup=backup)              # dry run is the default
    assert dry.dry_run and not dry.written and ecu.identifiers[0x0600] != new
    assert "DRY RUN" in str(dry)
    with pytest.raises(CodingSafetyError, match="confirm=True"):
        session.write_coding(new, backup=backup, dry_run=False)
    with pytest.raises(CodingSafetyError, match="backup dict"):
        session.write_coding(new, backup={"coding": "00"})
    with pytest.raises(CodingSafetyError, match="bytes"):
        session.write_coding(new[:-1], backup=backup)
    assert not _unverified_messages(caplog, "coding")           # nothing written yet

    # Real write: needs the extended session and the login, then verifies by read-back.
    session.enter_extended_session()
    session.login(ecu.login_code)
    res = session.write_coding(new, backup=backup, confirm=True, dry_run=False)
    assert res.written and res.verified and ecu.identifiers[0x0600] == new
    assert "WRITTEN+VERIFIED" in str(res)
    assert len(_unverified_messages(caplog, "coding write")) == 1
    # Stale backup (coding changed since) is refused.
    with pytest.raises(CodingSafetyError, match="differs from the backup"):
        session.write_coding(backup and bytes.fromhex(backup["coding"]), backup=backup, confirm=True, dry_run=False)
    # Identity mismatch: module was swapped / reflashed since the backup.
    fresh = session.make_coding_backup()
    ecu.identifiers[0xF189] = b"0002"
    with pytest.raises(CodingSafetyError, match="identity mismatch for DID F189"):
        session.write_coding(new, backup=fresh)
    # Unchanged value with confirm is a no-op write.
    ecu.identifiers[0xF189] = b"0001"
    fresh = session.make_coding_backup()
    same = session.write_coding(new, backup=fresh, confirm=True, dry_run=False)
    assert not same.written and same.verified


def test_coding_write_refused_by_module_without_login():
    session, ecu, link = _session()
    backup = session.make_coding_backup()
    session.enter_extended_session()
    with pytest.raises(NegativeResponse) as exc:
        session.write_coding(bytes.fromhex("091900122426000E3005"), backup=backup, confirm=True, dry_run=False)
    assert exc.value.nrc == 0x33


def test_login_warns_unverified_once_and_unlocks_sim(caplog):
    caplog.set_level(logging.WARNING)
    session, ecu, link = _session()
    session.enter_extended_session()
    session.login(ecu.login_code)
    assert 0x03 in ecu.unlocked_levels
    assert link.sent[-2] == b"\x27\x03"
    session2, ecu2, link2 = _session()
    session2.enter_extended_session()
    session2.login(ecu2.login_code)
    assert len(_unverified_messages(caplog, "5-digit login sent as SecurityAccess level 0x03/0x04")) == 1
    assert len(_unverified_messages(caplog, "candidate rule")) == 1
    session3, ecu3, link3 = _session()
    session3.enter_extended_session()
    with pytest.raises(NegativeResponse) as exc:
        session3.login(ecu3.login_code + 7)
    assert exc.value.nrc == 0x35
    # A caller-supplied key function replaces the candidate rule (no key warning for it).
    V._reset_unverified_warnings()
    caplog.clear()
    session4, ecu4, link4 = _session()
    session4.enter_extended_session()
    session4.login(ecu4.login_code, seed_key_fn=login_seed_key_fn(ecu4.login_code))
    assert not _unverified_messages(caplog, "candidate rule")
    with pytest.raises(ValueError):
        session4.login(1, level=0x04)
    with pytest.raises(ValueError):
        login_seed_key_fn(70000)


def test_unlock_default_level_warns_once(caplog):
    caplog.set_level(logging.WARNING)
    session, ecu, link = _session()
    session.enter_extended_session()
    session.unlock(sa2_script=ecu.sa2_script)
    assert ecu.security_unlocked
    session.unlock(sa2_script=ecu.sa2_script)
    assert len(_unverified_messages(caplog, "level 0x11/0x12")) == 1
    with pytest.raises(ValueError):
        VagEcuSession(session.client).unlock()


def test_read_write_scan_dids_and_measuring_values():
    session, ecu, link = _session()
    assert session.read_did(0xF187) == b"8V0906259H"
    out = session.read_dids([0xF187, 0xF189, 0xABCD])
    assert out == {0xF187: b"8V0906259H", 0xF189: b"0001"}
    out2 = session.read_dids([0xF187, 0xF189])
    assert out2 == out and link.sent[-1] == bytes.fromhex("22F187F189")   # sizes learned -> batched
    with pytest.raises(CodingSafetyError):
        session.write_did(0xF198, b"\x00\x00\x00\x00\x01")
    with pytest.raises(CodingSafetyError):
        session.write_did(0x0600, b"\x00" * 10, confirm=True)
    session.enter_extended_session()
    session.login(ecu.login_code)
    old = session.write_did(0xF198, b"\x00\x00\x00\x00\x01", confirm=True)
    assert old == b"\x00\x00\x00\x00\x00" and ecu.identifiers[0xF198] == b"\x00\x00\x00\x00\x01"
    scan = session.scan_dids(0xF186, 0xF192)
    assert 0xF190 in scan and 0xF188 not in scan
    speed = session.read_measuring_did(0xF40D)
    assert speed.decoded and speed.value == 0 and speed.unit == "km/h" and "speed" in speed.name.lower()
    volt = session.read_measuring_did(0xF442)
    assert volt.decoded and volt.value == pytest.approx(14.2)
    coding = session.read_measuring_did(0x0600)
    assert not coding.decoded and coding.value == coding.raw and "Coding" in coding.name
    assert session.routine(0x0203) == b"" and session.routine(0x0203, "results") == b"\x01\x00\x64"
    with pytest.raises(ValueError):
        session.routine(0x0203, "bogus")
    assert session.io_control(0x1100, data=b"\x40") == b"\x40" and session.return_control(0x1100) == b"\x00"
