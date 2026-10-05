"""
UDS extensions against the extended SimulatedEcu: NRC/service tables, session
timing and gating, ECU reset, multi-DID reads, every 0x19 subfunction the client
offers, IO control, routines, dynamic DIDs, communication control, DTC setting,
DID scanning, download, login and coding writes. Framing is checked byte for byte
through ``FakeIsoTpLink.sent``.
"""

from __future__ import annotations

import pytest

from vagtune.transport.fake import (
    SIM_EXTENDED_RECORD_SIZES,
    SIM_IO_DID_DEMO,
    SIM_ROUTINE_BASIC_SETTING_A,
    SIM_ROUTINE_ERASE,
    SIM_SNAPSHOT_DID_SIZES,
    SimulatedEcu,
    SimulatedFault,
    make_fake_pair,
)
from vagtune.uds import dtc as D
from vagtune.uds import services as S
from vagtune.uds.client import UdsClient
from vagtune.uds.exceptions import (
    NRC_NAMES,
    NRC_NAMES_UDSONCAN,
    NegativeResponse,
    UnexpectedResponse,
    nrc_name,
)
from vagtune.vag.ecu import login_seed_key_fn
from vagtune.vag.sa2 import make_seed_key_fn


def _session():
    link, ecu = make_fake_pair(0x7E0, 0x7E8)
    return UdsClient(link), ecu, link


def _extended(client):
    client.diagnostic_session_control(0x03)


def _programming_unlocked(client, ecu):
    client.diagnostic_session_control(0x03)
    client.diagnostic_session_control(0x02)
    client.security_access(0x11, make_seed_key_fn(ecu.sa2_script))


# ----------------------------------------------------------------- tables

def test_nrc_table_is_complete_with_fact_names():
    expected = {
        0x10: "GeneralReject", 0x14: "ResponseTooLong", 0x25: "NoResponseFromSubnetComponent",
        0x26: "FailurePreventsExecutionOfRequestedAction", 0x34: "AuthenticationRequired",
        0x3A: "SecureDataVerificationFailed", 0x50: "CertificateVerificationFailed_InvalidTimePeriod",
        0x5D: "DeAuthenticationFailed", 0x73: "WrongBlockSequenceCounter",
        0x78: "RequestCorrectlyReceived_ResponsePending", 0x7E: "SubFunctionNotSupportedInActiveSession",
        0x8C: "TransmissionRangeNotInNeutral", 0x8F: "BrakeSwitchNotClosed", 0x91: "TorqueConverterClutchLocked",
        0x94: "ResourceTemporarilyNotAvailable",
    }
    for nrc, name in expected.items():
        assert NRC_NAMES_UDSONCAN[nrc] == name
        assert NRC_NAMES[nrc] == name[0].lower() + name[1:]
    assert len(NRC_NAMES) == 59
    assert 0x8E not in NRC_NAMES
    assert nrc_name(0x16) == "ISOSAEReserved(0x16)"
    assert nrc_name(0xF5) == "vehicleManufacturerSpecific(0xF5)"
    assert nrc_name(0x3C, secured=True) == "AccessDenied"
    exc = NegativeResponse(0x22, 0x31)
    assert exc.is_not_supported and not exc.is_refused
    assert NegativeResponse(0x22, 0x33).is_refused and NegativeResponse(0x27, 0x36).is_security_related


def test_service_tables():
    assert S.DtcReportType.REPORT_DTC_FAULT_DETECTION_COUNTER == 0x14
    assert S.DtcReportType.REPORT_WWH_OBD_DTC_WITH_PERMANENT_STATUS == 0x55
    assert S.DTC_REPORT_NAMES[0x1A] == "reportSupportedDTCExtDataRecord"
    assert S.IoControlOption.SHORT_TERM_ADJUSTMENT == 3
    assert S.CommunicationControlType.DISABLE_RX_AND_TX == 3
    assert S.communication_type(normal=True, subnet=S.COMM_SUBNET_ALL) == 0xF1
    assert S.communication_type(normal=False, network_management=True) == 0x02
    with pytest.raises(ValueError):
        S.communication_type(normal=False)
    assert S.ResetType.DISABLE_RAPID_POWER_SHUTDOWN == 5
    assert S.DynamicDefineType.CLEAR == 3
    assert S.Session.VAG_4F == 0x4F
    assert S.Service.ACCESS_TIMING_PARAMETER == 0x83
    assert S.routine_id_range(0xFF00) == "eraseMemory"
    assert S.routine_id_range(0xE200) == "ExecuteSPL"
    assert S.routine_id_range(0xE202) == "SafetySystemRoutineIDs"
    assert S.routine_id_range(0xFF02) == "ISOSAEReserved"
    assert S.ISO_DID_NAMES[0xF19F] == "EntityDataIdentifier"
    assert S.did_name(0x0600).startswith("VW Coding Value")
    assert S.did_name(0xF188) == "vehicleManufacturerECUSoftwareNumber"
    assert S.obd_mirror_pid(0xF40D) == 0x0D and S.obd_mirror_pid(0xF442) == 0x42
    assert S.obd_mirror_pid(0xF500) is None and S.obd_mirror_pid(0xF190) is None
    assert S.DtcFormat.ISO14229_1 == 1 and S.FunctionalGroup.VOBD_SYSTEM == 0xFE


# ----------------------------------------------------------------- sessions / reset

def test_session_timing_decoded_from_10_response():
    client, ecu, link = _session()
    record = client.diagnostic_session_control(0x03)
    assert record == bytes([0x00, 0x32, 0x01, 0xF4])
    t = client.last_session_timing
    assert t.session == 0x03 and t.p2_ms == 50 and t.p2_star_ms == 5000
    assert link.sent[-1] == b"\x10\x03"


def test_programming_session_needs_extended_first_and_relocks():
    client, ecu, link = _session()
    with pytest.raises(NegativeResponse) as exc:
        client.diagnostic_session_control(0x02)
    assert exc.value.nrc == 0x7E
    _extended(client)
    client.security_access(0x11, make_seed_key_fn(ecu.sa2_script))
    assert ecu.security_unlocked
    client.diagnostic_session_control(0x02)      # session transition resets security
    assert ecu.session == 0x02 and not ecu.security_unlocked
    with pytest.raises(NegativeResponse) as exc:
        client.diagnostic_session_control(0x05)
    assert exc.value.nrc == 0x12


def test_session_gated_service_answers_7f_in_default_session():
    client, ecu, link = _session()
    with pytest.raises(NegativeResponse) as exc:
        client.io_control(SIM_IO_DID_DEMO, data=b"\x10")
    assert exc.value.nrc == 0x7F
    _extended(client)
    assert client.io_control(SIM_IO_DID_DEMO, data=b"\x10") == b"\x10"


def test_ecu_reset_variants():
    client, ecu, link = _session()
    _extended(client)
    client.security_access(0x11, make_seed_key_fn(ecu.sa2_script))
    assert client.ecu_reset(S.ResetType.HARD_RESET) is None
    assert link.sent[-1] == b"\x11\x01"
    assert ecu.session == 0x01 and not ecu.security_unlocked and ecu.reset_count == 1
    with pytest.raises(NegativeResponse) as exc:
        client.ecu_reset(S.ResetType.ENABLE_RAPID_POWER_SHUTDOWN)
    assert exc.value.nrc == 0x7E
    _extended(client)
    assert client.ecu_reset(S.ResetType.ENABLE_RAPID_POWER_SHUTDOWN) == 0x0A
    with pytest.raises(NegativeResponse) as exc:
        client.ecu_reset(0x06)
    assert exc.value.nrc == 0x12


def test_suppress_bit_keeps_ecu_silent():
    ecu = SimulatedEcu()
    assert ecu.handle(b"\x10\x83") is None and ecu.session == 0x03
    assert ecu.handle(b"\x85\x82") is None and ecu.dtc_setting_on is False
    assert ecu.handle(b"\x28\x83\x01") is None and ecu.comm_control == 3


# ----------------------------------------------------------------- multi-DID 0x22

def test_multi_did_read_single_request_with_size_oracle():
    client, ecu, link = _session()
    dids = [0xF187, 0xF189, 0xF190]
    out = client.read_data_by_identifiers(dids, size_of=ecu.did_sizes())
    assert list(out) == dids
    assert out[0xF190] == b"WVWZZZAUZLW000001" and out[0xF189] == b"0001"
    assert link.sent[-1] == bytes.fromhex("22 F187 F189 F190".replace(" ", ""))
    assert len(link.sent) == 1


def test_multi_did_read_falls_back_to_single_reads_without_sizes():
    client, ecu, link = _session()
    out = client.read_data_by_identifiers([0xF187, 0xF189], size_of=None)
    assert out == {0xF187: b"8V0906259H", 0xF189: b"0001"}
    assert link.sent == [b"\x22\xF1\x87", b"\x22\xF1\x89"]


def test_multi_did_mixed_known_unknown_and_skip_unsupported():
    client, ecu, link = _session()
    sizes = ecu.did_sizes()
    out = client.read_data_by_identifiers([0xF187, 0xABCD, 0xF197, 0xF1A3], size_of=sizes,
                                          skip_unsupported=True)
    # 0xABCD has no size -> single read -> NRC 0x31 -> skipped; the batch carried the rest.
    assert set(out) == {0xF187, 0xF197, 0xF1A3}
    assert link.sent[0] == bytes.fromhex("22F187F197F1A3") and link.sent[1] == b"\x22\xAB\xCD"
    with pytest.raises(NegativeResponse):
        client.read_data_by_identifiers([0xABCD], size_of=sizes)


def test_multi_did_wrong_oracle_size_degrades_to_single_reads():
    client, ecu, link = _session()
    wrong = {0xF187: 3, 0xF189: 4}
    out = client.read_data_by_identifiers([0xF187, 0xF189], size_of=wrong)
    assert out[0xF187] == b"8V0906259H" and out[0xF189] == b"0001"
    assert len(link.sent) == 3   # one failed batch + two singles


def test_multi_did_with_callable_oracle_and_batching():
    client, ecu, link = _session()
    sizes = ecu.did_sizes()
    dids = [0xF187, 0xF189, 0xF190, 0xF191, 0xF197]
    out = client.read_data_by_identifiers(dids, size_of=sizes.get, max_per_request=2)
    assert list(out) == dids
    assert len(link.sent) == 3   # 2 + 2 + 1(single)


def test_sim_rejects_malformed_multi_did_request():
    ecu = SimulatedEcu()
    assert ecu.handle(b"\x22\xF1") == b"\x7F\x22\x13"
    assert ecu.handle(b"\x22\xAB\xCD\xAB\xCE") == b"\x7F\x22\x31"


def test_multi_did_omitted_did_is_never_dropped_silently():
    """ISO lets the ECU answer a multi-DID read with only the DIDs it supports; the
    client must then surface the real NRC for the missing one (or skip it only when
    asked), never pretend the batch answered everything."""
    client, ecu, link = _session()
    sizes = ecu.did_sizes()
    sizes[0xABCD] = 4                                   # a label file claims a DID the module lacks
    with pytest.raises(NegativeResponse) as exc:
        client.read_data_by_identifiers([0xF187, 0xABCD], size_of=sizes, skip_unsupported=False)
    assert exc.value.nrc == 0x31
    assert link.sent == [b"\x22\xF1\x87\xAB\xCD", b"\x22\xF1\x87", b"\x22\xAB\xCD"]
    link.sent.clear()
    out = client.read_data_by_identifiers([0xF187, 0xABCD, 0xF189], size_of=sizes, skip_unsupported=True)
    assert out == {0xF187: b"8V0906259H", 0xF189: b"0001"}


def test_multi_did_secured_did_refuses_whole_request_and_surfaces_0x33():
    """ISO 14229-1: securityAccessDenied applies to the whole 0x22 request when any DID
    is secured (the simulator does that now); the client degrades to single reads and
    the locked DID raises 0x33 - skip_unsupported only hides 0x31."""
    ecu = SimulatedEcu()
    assert ecu.handle(b"\x22\xF1\x87\x12\xFC") == b"\x7F\x22\x33"
    client, ecu, link = _session()
    sizes = ecu.did_sizes()
    for skip in (False, True):
        with pytest.raises(NegativeResponse) as exc:
            client.read_data_by_identifiers([0xF187, 0x12FC], size_of=sizes, skip_unsupported=skip)
        assert exc.value.nrc == 0x33
    _extended(client)
    client.security_access(0x03, login_seed_key_fn(ecu.login_code))
    out = client.read_data_by_identifiers([0xF187, 0x12FC], size_of=sizes)
    assert out == {0xF187: b"8V0906259H", 0x12FC: b"\x00\x00\x00\x00"} and link.sent[-1] == b"\x22\xF1\x87\x12\xFC"


def test_multi_did_oversized_oracle_entry_does_not_corrupt_data():
    """F189 is 4 bytes; a stale oracle says 23 (= 4 + the whole 2+17 F190 field). The
    batch answer then lacks F190, which must trigger the single-read fallback so F189
    comes back as its true 4 bytes rather than 23 bytes with the VIN glued on."""
    client, ecu, link = _session()
    wrong = {0xF189: 4 + 2 + 17, 0xF190: 17}
    out = client.read_data_by_identifiers([0xF189, 0xF190], size_of=wrong)
    assert out == {0xF189: b"0001", 0xF190: b"WVWZZZAUZLW000001"}
    assert link.sent == [b"\x22\xF1\x89\xF1\x90", b"\x22\xF1\x89", b"\x22\xF1\x90"]
    # An undersized entry that happens to re-align on a requested DID is caught too.
    ecu.custom_handlers[0x22] = lambda req: b"\x62\xF1\x89\x00\xF1\x89\x00\x01"   # F189 twice
    with pytest.raises(UnexpectedResponse, match="twice"):
        client._read_batch([0xF189, 0xF190], {0xF189: 1, 0xF190: 17}.get)


# ----------------------------------------------------------------- 0x19

def test_read_dtc_count_and_records():
    client, ecu, link = _session()
    count = client.read_dtc_count(0xFF)
    assert link.sent[-1] == b"\x19\x01\xFF"
    assert count.count == 2 and count.dtc_format == 1 and count.format_name == "ISO14229_1"
    assert client.read_dtc_count(0x20).count == 1
    dtcs = client.read_dtcs(0xFF)
    assert link.sent[-1] == b"\x19\x02\xFF"
    assert [d.sae_code for d in dtcs] == ["P0112", "P0561"]
    p0112 = dtcs[0]
    assert p0112.dtc == 0x011200 and p0112.ftb == 0 and p0112.status == 0x2F
    assert p0112.test_failed and p0112.confirmed and p0112.pending and p0112.active
    assert p0112.vcds_bracket() == "[047]"
    assert "confirmedDTC" in p0112.status_names()
    assert client.read_dtc_by_status_mask() == [(0x011200, 0x2F), (0x056100, 0x09)]


def test_read_supported_dtcs_and_fault_counters():
    client, ecu, link = _session()
    supported = client.read_supported_dtcs()
    assert link.sent[-1] == b"\x19\x0A"
    codes = {d.sae_code: d.status for d in supported}
    assert codes["P0112"] == 0x2F and codes["P0299"] == 0x50 and "U0100" in codes
    counters = client.read_dtc_fault_detection_counters()
    assert link.sent[-1] == b"\x19\x14"
    assert len(counters) == 1 and counters[0].sae_code == "P0299" and counters[0].fault_counter == 0x40
    ident = client.read_dtc_snapshot_identification()
    assert [(d.sae_code, r) for d, r in ident] == [("P0112", 1), ("P0561", 1)]
    with pytest.raises(ValueError):
        client.read_dtc_records(0x04)


def test_snapshot_with_known_sizes_is_complete():
    client, ecu, link = _session()
    report = client.read_dtc_snapshot(0x011200, 0xFF, SIM_SNAPSHOT_DID_SIZES)
    assert link.sent[-1] == b"\x19\x04\x01\x12\x00\xFF"
    assert report.dtc.sae_code == "P0112" and report.dtc.status == 0x2F
    assert report.complete and len(report.records) == 1
    rec = report.records[0]
    assert rec.record == 1 and rec.did_count == 3
    assert rec.value(0x295A) == (123456).to_bytes(3, "big")
    assert rec.value(0xF442) == (14200).to_bytes(2, "big")
    assert rec.raw == b""


def test_snapshot_without_sizes_returns_raw_tail_never_guesses():
    client, ecu, link = _session()
    report = client.read_dtc_snapshot(0x011200)
    assert not report.complete
    rec = report.records[0]
    assert rec.record == 1 and rec.did_count == 3 and rec.dids == []
    assert rec.raw.startswith(b"\xF4\x0D")
    # Partial oracle: first DID known, second unknown -> stops at the second.
    report = client.read_dtc_snapshot(0x011200, did_sizes={0xF40D: 1})
    rec = report.records[0]
    assert rec.dids == [(0xF40D, b"\x00")] and rec.raw.startswith(b"\xF4\x42")
    with pytest.raises(NegativeResponse) as exc:
        client.read_dtc_snapshot(0x029900)   # not stored
    assert exc.value.nrc == 0x31


def test_extended_data_with_and_without_sizes():
    client, ecu, link = _session()
    report = client.read_dtc_extended_data(0x056100, 0xFF, SIM_EXTENDED_RECORD_SIZES)
    assert link.sent[-1] == b"\x19\x06\x05\x61\x00\xFF"
    assert report.complete and [r.record for r in report.records] == [1, 2, 3, 4, 5]
    assert report.record(1).data == b"\x03" and report.record(2).data == b"\x04"   # priority 3, freq 4
    assert report.record(4).data == (123456).to_bytes(3, "big")
    assert len(report.record(5).data) == 5
    raw = client.read_dtc_extended_data(0x056100)
    assert not raw.complete and len(raw.records) == 1
    assert raw.records[0].record == 1 and raw.records[0].data == b""
    assert raw.records[0].raw == b"\x03" + b"\x02\x04" + b"\x03\x28" + b"\x04" + (123456).to_bytes(3, "big") + b"\x05" + bytes((24, 7, 17, 10, 42))
    single = client.read_dtc_extended_data(0x056100, 2, {2: 1})
    assert single.complete and single.records[0].data == b"\x04"


def test_unsupported_dtc_subfunction_and_clear_group_length():
    ecu = SimulatedEcu()
    assert ecu.handle(b"\x19\x42\xFF") == b"\x7F\x19\x12"
    assert ecu.handle(b"\x14\xFF\xFF") == b"\x7F\x14\x13"
    assert ecu.handle(b"\x14\xFF\xFF\xFF") == b"\x54" and ecu.dtcs == []


def test_fault_model_setter_keeps_compat_view():
    ecu = SimulatedEcu()
    ecu.dtcs = [(b"\x40\x35\x00", 0x28)]
    assert ecu.dtcs == [(b"\x40\x35\x00", 0x28)]
    assert ecu.fault(b"\x40\x35\x00").snapshots[1][2][0] == 0x295A
    ecu.fault_dtcs.append(SimulatedFault(b"\x02\x99\x00", 0x60))
    assert ecu.handle(b"\x19\x04\x02\x99\x00\xFF") == b"\x59\x04\x02\x99\x00\x60"


# ----------------------------------------------------------------- 0x2F / 0x31

def test_io_control_output_test_and_return_control():
    client, ecu, link = _session()
    _extended(client)
    assert client.io_control(SIM_IO_DID_DEMO, S.IoControlOption.SHORT_TERM_ADJUSTMENT, b"\x55") == b"\x55"
    assert link.sent[-1] == b"\x2F\x11\x00\x03\x55"
    ch = ecu.io_channels[SIM_IO_DID_DEMO]
    assert ch.controlled and ch.state == b"\x55"
    assert client.io_control(SIM_IO_DID_DEMO, S.IoControlOption.FREEZE_CURRENT_STATE) == b"\x55" and ch.frozen
    assert client.return_control(SIM_IO_DID_DEMO) == b"\x00"
    assert link.sent[-1] == b"\x2F\x11\x00\x00"
    assert not ch.controlled and not ch.frozen
    with pytest.raises(NegativeResponse) as exc:
        client.io_control(SIM_IO_DID_DEMO, data=b"\x01\x02")
    assert exc.value.nrc == 0x13
    with pytest.raises(NegativeResponse) as exc:
        client.io_control(0x2222, data=b"\x01")
    assert exc.value.nrc == 0x31


def test_routine_start_results_stop_sequence():
    client, ecu, link = _session()
    _extended(client)
    assert client.routine_start(SIM_ROUTINE_BASIC_SETTING_A) == b""
    assert link.sent[-1] == b"\x31\x01\x02\x03"           # the VW_Flash capture framing
    assert client.routine_results(SIM_ROUTINE_BASIC_SETTING_A) == b"\x01\x00\x64"
    assert client.routine_stop(SIM_ROUTINE_BASIC_SETTING_A) == b""
    assert ecu.routines[SIM_ROUTINE_BASIC_SETTING_A].state == "done"
    with pytest.raises(NegativeResponse) as exc:
        client.routine_stop(SIM_ROUTINE_BASIC_SETTING_A)   # not running any more
    assert exc.value.nrc == 0x24
    with pytest.raises(NegativeResponse) as exc:
        client.routine_results(0x0A1F)                      # never started
    assert exc.value.nrc == 0x24
    with pytest.raises(NegativeResponse) as exc:
        client.routine_start(0x1234)
    assert exc.value.nrc == 0x31
    with pytest.raises(NegativeResponse) as exc:
        client.routine_start(SIM_ROUTINE_ERASE)            # programming session only
    assert exc.value.nrc == 0x7E


def test_erase_routine_needs_programming_session_and_unlock():
    client, ecu, link = _session()
    client.diagnostic_session_control(0x03)
    client.diagnostic_session_control(0x02)
    with pytest.raises(NegativeResponse) as exc:
        client.routine_start(SIM_ROUTINE_ERASE)
    assert exc.value.nrc == 0x33
    client.security_access(0x11, make_seed_key_fn(ecu.sa2_script))
    assert client.routine_start(SIM_ROUTINE_ERASE) == b"\x00"
    assert bytes(ecu.cal_memory[:16]) == b"\xFF" * 16


# ----------------------------------------------------------------- 0x2C / 0x28 / 0x85

def test_dynamic_did_by_memory_address_fast_logging():
    client, ecu, link = _session()
    _extended(client)
    client.dynamically_define_did_by_memory(0xF200, [(0x0010, 4), (0x0020, 2)])
    assert link.sent[-1] == bytes.fromhex("2C02F20014 00000010 04 00000020 02".replace(" ", ""))
    assert client.read_data_by_identifier(0xF200) == ecu.memory[0x10:0x14] + ecu.memory[0x20:0x22]
    # The dynamic DID also joins multi-DID reads with its size.
    out = client.read_data_by_identifiers([0xF200, 0xF189], size_of=ecu.did_sizes())
    assert out[0xF200] == ecu.memory[0x10:0x14] + ecu.memory[0x20:0x22]
    client.clear_dynamic_did(0xF200)
    assert link.sent[-1] == b"\x2C\x03\xF2\x00"
    with pytest.raises(NegativeResponse) as exc:
        client.read_data_by_identifier(0xF200)
    assert exc.value.nrc == 0x31
    with pytest.raises(NegativeResponse) as exc:
        client.dynamically_define_did_by_memory(0xF201, [(0xFFFF_FF00, 4)])
    assert exc.value.nrc == 0x31
    with pytest.raises(NegativeResponse) as exc:
        client.dynamically_define_did_by_memory(0x1234, [(0x10, 1)])
    assert exc.value.nrc == 0x31


def test_dynamic_did_by_identifier_and_clear_all():
    client, ecu, link = _session()
    _extended(client)
    client.dynamically_define_did_by_identifier(0xF210, [(0xF190, 1, 3), (0xF189, 3, 2)])
    assert link.sent[-1] == bytes.fromhex("2C01F210 F1900103 F1890302".replace(" ", ""))
    assert client.read_data_by_identifier(0xF210) == b"WVW" + b"01"
    client.clear_dynamic_did()
    assert link.sent[-1] == b"\x2C\x03"
    assert ecu.dynamic_dids == {}
    with pytest.raises(ValueError):
        client.dynamically_define_did_by_identifier(0xF210, [(0xF190, 0, 3)])


def test_communication_control_and_dtc_setting():
    client, ecu, link = _session()
    _extended(client)
    client.communication_control(S.CommunicationControlType.DISABLE_RX_AND_TX, S.COMM_NORMAL_MESSAGES)
    assert link.sent[-1] == b"\x28\x03\x01" and ecu.comm_control == 3
    client.communication_control(S.CommunicationControlType.ENABLE_RX_AND_TX)
    assert ecu.comm_control == 0
    client.communication_control(5, 0x01, node_id=0x0102)
    assert link.sent[-1] == b"\x28\x05\x01\x01\x02"
    with pytest.raises(ValueError):
        client.communication_control(0, node_id=1)
    with pytest.raises(NegativeResponse) as exc:
        client.communication_control(6)
    assert exc.value.nrc == 0x12
    client.control_dtc_setting(False)
    assert link.sent[-1] == b"\x85\x02" and ecu.dtc_setting_on is False     # echo validated
    client.control_dtc_setting(True)
    assert link.sent[-1] == b"\x85\x01" and ecu.dtc_setting_on is True
    client.control_dtc_setting(False, suppress=True)
    assert link.sent[-1] == b"\x85\x82" and ecu.dtc_setting_on is False
    ecu.custom_handlers[0x85] = lambda req: b"\xC5\x01"                     # wrong echo
    with pytest.raises(UnexpectedResponse):
        client.control_dtc_setting(False)


def test_control_dtc_setting_refused_by_ecu_is_raised_not_faked():
    """Default session: the simulator (like a VAG module) answers 7F 85 7F. Both the
    plain and the suppressed form must raise, leave logging on and leave no stale
    NRC in the inbox for the next request to swallow."""
    client, ecu, link = _session()
    with pytest.raises(NegativeResponse) as exc:
        client.control_dtc_setting(False)
    assert exc.value.nrc == 0x7F and ecu.dtc_setting_on is True
    with pytest.raises(NegativeResponse) as exc:
        client.control_dtc_setting(False, suppress=True)
    assert exc.value.nrc == 0x7F and ecu.dtc_setting_on is True
    assert link.sent[-1] == b"\x85\x82" and link.recv(0) is None


def test_suppressed_request_negative_response_is_reported():
    client, ecu, link = _session()
    ecu.custom_handlers[0x3E] = lambda req: b"\x7F\x3E\x11"          # module without 0x3E
    with pytest.raises(NegativeResponse) as exc:
        client.tester_present(suppress=True)
    assert exc.value.nrc == 0x11 and link.sent[-1] == b"\x3E\x80"
    # Silence within the window means accepted; a positive answer to a suppressed
    # request (ECU ignoring the bit) is accepted too; a 0x78 keeps the client waiting.
    del ecu.custom_handlers[0x3E]
    client.timing.suppressed_nrc_window = 0.02
    client.tester_present(suppress=True)
    ecu.custom_handlers[0x3E] = lambda req: b"\x7E\x00"
    client.tester_present(suppress=True)
    # 7F 3E 78 (pending) first, then the final 7F 3E 22: the window stretches to P2*.
    ecu.custom_handlers[0x3E] = lambda req: link._inbox.put(b"\x7F\x3E\x78") or b"\x7F\x3E\x22"
    with pytest.raises(NegativeResponse) as exc:
        client.tester_present(suppress=True)
    assert exc.value.nrc == 0x22
    # The ECU-announced P2 widens the window (never beyond P2 timeout).
    client.last_session_timing = None
    assert client._suppressed_window() == pytest.approx(0.02)
    client.diagnostic_session_control(0x03)       # announces P2 = 50 ms
    assert client._suppressed_window() == pytest.approx(0.05)
    client.timing.p2_timeout = 0.03
    assert client._suppressed_window() == pytest.approx(0.03)


# ----------------------------------------------------------------- scan_dids

def test_scan_dids_classifies_absent_refused_and_present():
    client, ecu, link = _session()
    seen = []
    result = client.scan_dids(0xF186, 0xF192, on_progress=lambda did, o: seen.append(did))
    assert seen == list(range(0xF186, 0xF192))
    assert set(result) == {0xF186, 0xF187, 0xF189, 0xF18C, 0xF190, 0xF191}
    assert result[0xF187] == b"8V0906259H" and result[0xF186] == b"\x01"
    locked = client.scan_dids(0x12FC, 0x12FD)
    assert isinstance(locked[0x12FC], NegativeResponse) and locked[0x12FC].nrc == 0x33
    _extended(client)
    client.security_access(0x03, login_seed_key_fn(ecu.login_code))
    assert client.scan_dids(0x12FC, 0x12FD)[0x12FC] == b"\x00\x00\x00\x00"


def test_scan_dids_stops_on_service_not_supported():
    client, ecu, link = _session()
    ecu.custom_handlers[0x22] = lambda req: b"\x7F\x22\x11"
    with pytest.raises(NegativeResponse) as exc:
        client.scan_dids(0xF190, 0xF192)
    assert exc.value.nrc == 0x11
    assert client.scan_dids(0xF190, 0xF192, stop_on_service_unsupported=False) == {}


# ----------------------------------------------------------------- download / login / coding

def test_download_writes_calibration_after_unlock():
    client, ecu, link = _session()
    payload = bytes(range(256)) * 3
    with pytest.raises(NegativeResponse) as exc:
        client.download(ecu.cal_base, payload)
    assert exc.value.nrc == 0x7F          # programming session only
    _programming_unlocked(client, ecu)
    seen = []
    client.download(ecu.cal_base + 0x100, payload, progress=lambda d, t: seen.append((d, t)))
    assert bytes(ecu.cal_memory[0x100:0x100 + len(payload)]) == payload
    assert seen[-1] == (len(payload), len(payload)) and len(seen) == 3
    assert link.sent[-1] == b"\x37"
    # Read it back through the verified upload path.
    assert client.upload(ecu.cal_base + 0x100, len(payload)) == payload
    with pytest.raises(NegativeResponse) as exc:
        client.download(0x0000, b"\x01")   # the demo region is read-only
    assert exc.value.nrc == 0x72


def test_login_level_3_seed_key_and_lockout():
    client, ecu, link = _session()
    _extended(client)
    client.security_access(0x03, login_seed_key_fn(ecu.login_code))
    assert 0x03 in ecu.unlocked_levels and not ecu.security_unlocked
    assert link.sent[-2] == b"\x27\x03" and link.sent[-1][:2] == b"\x27\x04"
    client, ecu, link = _session()
    _extended(client)
    for attempt in range(3):
        with pytest.raises(NegativeResponse) as exc:
            client.security_access(0x03, login_seed_key_fn(ecu.login_code + 1))
        assert exc.value.nrc == (0x35 if attempt < 2 else 0x36)
    with pytest.raises(NegativeResponse) as exc:
        client.security_access(0x03, login_seed_key_fn(ecu.login_code))
    assert exc.value.nrc == 0x37
    with pytest.raises(ValueError):
        client.security_access(0x04, login_seed_key_fn(1))


def test_security_access_empty_seed_and_bad_key_echo_are_errors():
    client, ecu, link = _session()
    ecu.custom_handlers[0x27] = lambda req: b"\x67" + req[1:2]           # bare "67 11": no seed
    calls = []
    with pytest.raises(UnexpectedResponse, match="no seed bytes"):
        client.security_access(0x11, lambda level, seed: calls.append(seed) or b"\x00" * 4)
    assert not calls and link.sent == [b"\x27\x11"]
    # sendKey answered with the wrong subfunction echo is not an unlock either.
    ecu.custom_handlers[0x27] = lambda req: (b"\x67\x11\x01\x02\x03\x04" if req[1] == 0x11 else b"\x67\x13")
    with pytest.raises(UnexpectedResponse, match="sendKey echo"):
        client.security_access(0x11, lambda level, seed: b"\x00" * 4)
    # The all-zero convention still means "already unlocked" when a seed is present.
    ecu.custom_handlers[0x27] = lambda req: b"\x67\x11\x00\x00\x00\x00"
    client.security_access(0x11, lambda level, seed: pytest.fail("no key expected"))


@pytest.mark.parametrize("sid,method", [(0x34, "request_download"), (0x35, "request_upload")])
def test_truncated_transfer_setup_response_is_a_uds_error(sid, method):
    client, ecu, link = _session()
    for bad, needle in ((bytes([sid + 0x40]), "too short"),
                        (bytes([sid + 0x40, 0x00]), "zero-length"),
                        (bytes([sid + 0x40, 0x20, 0x01]), "truncated"),
                        (bytes([sid + 0x40, 0x10, 0x02]), "cannot carry data")):
        ecu.custom_handlers[sid] = lambda req, bad=bad: bad
        with pytest.raises(UnexpectedResponse, match=needle):
            getattr(client, method)(0x80A80000, 0x100)
    ecu.custom_handlers[sid] = lambda req: bytes([sid + 0x40, 0x20, 0x01, 0x02])
    assert getattr(client, method)(0x80A80000, 0x100) == 0x0102


def test_coding_write_gated_on_login_and_length():
    client, ecu, link = _session()
    _extended(client)
    new = bytes.fromhex("09190012242600 0E3005".replace(" ", ""))
    with pytest.raises(NegativeResponse) as exc:
        client.write_data_by_identifier(0x0600, new)
    assert exc.value.nrc == 0x33
    client.security_access(0x03, login_seed_key_fn(ecu.login_code))
    with pytest.raises(NegativeResponse) as exc:
        client.write_data_by_identifier(0x0600, new[:-1])
    assert exc.value.nrc == 0x13
    client.write_data_by_identifier(0x0600, new)
    assert link.sent[-1] == b"\x2E\x06\x00" + new
    assert client.read_data_by_identifier(0x0600) == new
    with pytest.raises(NegativeResponse) as exc:
        client.write_data_by_identifier(0xF190, b"X" * 17)   # not writable
    assert exc.value.nrc == 0x31


def test_custom_handlers_take_precedence_over_builtins():
    ecu = SimulatedEcu()
    ecu.custom_handlers[0x22] = lambda req: b"\x62" + req[1:3] + b"custom"
    assert ecu.handle(b"\x22\xF1\x90") == b"\x62\xF1\x90custom"


def test_parser_builders_round_trip():
    recs = {1: [(0xF40D, b"\x10"), (0xF442, b"\x37\x78")], 2: [(0x295A, b"\x01\x02\x03")]}
    resp = D.build_snapshot_response(b"\x02\x99\x00", 0x60, recs)
    rep = D.parse_snapshot_records(resp, D.snapshot_did_sizes_from(recs))
    assert rep.complete and [r.record for r in rep.records] == [1, 2]
    assert rep.records[1].dids == [(0x295A, b"\x01\x02\x03")]
    ext = D.build_extended_response(b"\x02\x99\x00", 0x60, {1: b"\x02", 2: b"\x05"})
    assert D.parse_extended_data(ext, {1: 1, 2: 1}).record(2).data == b"\x05"
    with pytest.raises(UnexpectedResponse):
        D.parse_extended_data(b"\x59\x06\x02\x99\x00\x60\x00\x01", {})
    with pytest.raises(UnexpectedResponse):
        D.parse_dtc_records(b"\x59\x0A\xFF", 0x02)
    mask, dtcs = D.parse_dtc_records(D.build_dtc_records(0xFF, [(b"\x02\x99\x00", 0x60)]))
    assert mask == 0xFF and dtcs[0].intermittent and not dtcs[0].active


def test_snapshot_truncated_message_is_never_reported_complete():
    good = D.build_snapshot_response(b"\x02\x99\x00", 0x60, {1: [(0xF40D, b"\x10")]})
    # A lone trailing byte where a "<record> <nDIDs>" header should be.
    rep = D.parse_snapshot_records(good + b"\x02", {0xF40D: 1})
    assert rep.records[0].complete and not rep.complete
    stray = rep.records[1]
    assert stray.truncated and stray.raw == b"\x02" and not stray.complete and stray.dids == []
    assert not D.parse_snapshot_records(b"\x59\x04\x01\x12\x00\x2F" + b"\x01", {}).complete
    # A DID field cut short with a *known* size is truncated; an unknown size is not.
    rep = D.parse_snapshot_records(good[:-1], {0xF40D: 1})
    assert rep.records[0].truncated and rep.records[0].raw == b"\xF4\x0D" and not rep.complete
    rep = D.parse_snapshot_records(good, {})
    assert not rep.records[0].truncated and not rep.records[0].complete
    rep = D.parse_snapshot_records(good[:-2], {})          # ends inside the DID number
    assert rep.records[0].truncated and rep.records[0].raw == b"\xF4"


def test_sim_dynamic_did_chain_resolves_to_leaves_and_never_recurses():
    ecu = SimulatedEcu()
    ecu.session = 0x03
    assert ecu.handle(bytes.fromhex("2C01F200F1900103")) == b"\x6C\x01\xF2\x00"       # F200 = VIN[0:3]
    assert ecu.handle(bytes.fromhex("2C01F201F2000202")) == b"\x6C\x01\xF2\x01"       # F201 = F200[1:3]
    assert ecu.dynamic_dids[0xF201] == [("did", 0xF190, 2, 2)]                        # stored as a leaf
    assert ecu.handle(b"\x22\xF2\x01") == b"\x62\xF2\x01VW"
    assert ecu.handle(bytes.fromhex("2C01F200F2010102")) == b"\x6C\x01\xF2\x00"       # "cycle" -> leaves
    assert ecu.handle(b"\x22\xF2\x00") == b"\x62\xF2\x00VW"
    # A window across a memory leaf and a DID leaf splits correctly.
    assert ecu.handle(bytes.fromhex("2C02F21014 00000010 04".replace(" ", ""))) == b"\x6C\x02\xF2\x10"
    assert ecu.handle(bytes.fromhex("2C01F211F2100103F1900102")) == b"\x6C\x01\xF2\x11"
    assert ecu.handle(bytes.fromhex("2C01F212F2110303")) == b"\x6C\x01\xF2\x12"       # F211[2:5] = mem[0x12] + "WV"
    assert ecu.dynamic_dids[0xF212] == [("mem", 0x12, 0, 1), ("did", 0xF190, 1, 2)]
    assert ecu.handle(b"\x22\xF2\x12") == b"\x62\xF2\x12" + ecu.memory[0x12:0x13] + b"WV"
    # A cycle injected straight into the table answers 0x31 instead of recursing.
    ecu.dynamic_dids[0xF220] = [("did", 0xF221, 1, 1)]
    ecu.dynamic_dids[0xF221] = [("did", 0xF220, 1, 1)]
    assert ecu.handle(b"\x22\xF2\x20") == b"\x7F\x22\x31"
    assert ecu.handle(b"\x22\xF2\x20\xF1\x89") == b"\x62\xF1\x890001"
