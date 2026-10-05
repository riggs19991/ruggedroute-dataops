"""
KWP2000 client (vagtune.kwp) against the simulated brains (vagtune.kwp.sim) over an
in-memory payload link - no TP 2.0 involved. Byte-exact against the research sheet
where it quotes real traffic (10 89 / 50 89, 1A 9B records, 31 B8 00 00 capability
reply, 58 n + 3-byte records, 54 FF 00, 63 data without a skipped byte).
"""

from __future__ import annotations

import logging
import queue
import threading
import time
from typing import List, Sequence

import pytest

from vagtune.kwp import services as S
from vagtune.kwp.client import KwpClient, KwpTiming, parse_dtc_list
from vagtune.kwp.exceptions import KwpError, KwpNegativeResponse, KwpTimeout, UnexpectedKwpResponse
from vagtune.kwp.sim import (
    BodyBrain,
    Dq250Brain,
    Edc17Brain,
    GatewayBrain,
    HaldexBrain,
    Me7Brain,
    SimulatedKwpEcu,
    build_ident_9b,
)

h = bytes.fromhex


# ----------------------------------------------------------------- test links

class FakePayloadLink:
    """A payload link answered synchronously by ``ecu.handle_all`` (so a ``7F xx 78``
    preamble and the final answer both land in the queue, like a TP 2.0 channel)."""

    def __init__(self, ecu: SimulatedKwpEcu) -> None:
        self.ecu = ecu
        self._q: "queue.Queue[bytes]" = queue.Queue()
        self.sent: List[bytes] = []
        self.closed = False

    def send(self, payload: bytes) -> None:
        self.sent.append(bytes(payload))
        for reply in self.ecu.handle_all(payload):
            self._q.put(reply)

    def recv(self, timeout: float):
        try:
            return self._q.get(timeout=max(0.0, timeout))
        except queue.Empty:
            return None

    def flush_rx(self) -> None:
        while not self._q.empty():
            self._q.get_nowait()

    def close(self) -> None:
        self.closed = True


class ScriptedLink:
    """Replies per ``send`` from a script: each entry is the list of messages the
    module emits for that request (``[]`` = silence)."""

    def __init__(self, script: Sequence[Sequence[bytes]]) -> None:
        self.script = [list(s) for s in script]
        self._q: "queue.Queue[bytes]" = queue.Queue()
        self.sent: List[bytes] = []

    def send(self, payload: bytes) -> None:
        self.sent.append(bytes(payload))
        replies = self.script.pop(0) if self.script else []
        for r in replies:
            self._q.put(r)

    def recv(self, timeout: float):
        try:
            return self._q.get(timeout=max(0.0, timeout))
        except queue.Empty:
            return None

    def flush_rx(self) -> None:
        while not self._q.empty():
            self._q.get_nowait()

    def close(self) -> None:
        pass


def me7_client(**timing):
    ecu = SimulatedKwpEcu(Me7Brain())
    link = FakePayloadLink(ecu)
    return KwpClient(link, KwpTiming(p2=0.5, p2_star=1.0, busy_delay=0.01, **timing)), ecu, link


FAST = KwpTiming(p2=0.2, p2_star=0.5, busy_delay=0.01, retry_on_busy=5, pending_limit=5)


# ----------------------------------------------------------------- services table

def test_nrc_table_is_iso_14230_3_without_uds_only_codes():
    expected = {0x10, 0x11, 0x12, 0x21, 0x22, 0x23, 0x31, 0x33, 0x35, 0x36, 0x37, 0x40, 0x41, 0x42, 0x43,
                0x50, 0x51, 0x52, 0x53, 0x71, 0x72, 0x74, 0x75, 0x76, 0x77, 0x78, 0x79}
    assert set(S.NRC_NAMES) == expected
    assert not (set(S.NRC_NAMES) & S.UDS_ONLY_NRCS)
    assert S.NRC_NAMES[0x78] == "reqCorrectlyRcvd-RspPending"
    assert S.NRC_NAMES[0x21] == "busy-RepeatRequest"
    assert S.nrc_name(0x7F).startswith("notAKwp2000Code")
    assert S.nrc_name(0x80).startswith("manufacturerSpecific")
    assert S.nrc_name(0xA5) == "manufacturerSpecific(0xA5)"
    assert S.nrc_name(0x15) == "reservedByDocument(0x15)"
    assert S.positive_sid(0x1A) == 0x5A and S.positive_sid(0x3E) == 0x7E


def test_session_and_ident_tables():
    assert S.SESSION_STANDARD_DIAGNOSTIC == 0x89
    assert S.SESSIONS[0x89].used_by_toolkit and not S.SESSIONS[0x85].used_by_toolkit
    assert S.session_name(0x86).startswith("engineering")
    assert S.SESSION_REQUEST_IMMO_CLUSTER == h("10 84 14")
    assert {o for o, i in S.IDENT_OPTIONS.items() if i.decoded} == {0x91, 0x9A, 0x9B, 0x9F}
    assert S.service_name(0x21) == "readDataByLocalIdentifier"
    assert S.capability_name(0x0103).endswith("(REPORTED)")
    assert S.capability_name(0x0118) == "HEX-coded fault codes supported"
    assert S.capability_name(0x0199).startswith("function 0x0199")
    assert S.CODING_TYPE_NAMES == {0x00: "no coding", 0x03: "short coding", 0x10: "long coding"}


def test_negative_response_exception_fields():
    exc = KwpNegativeResponse(0x21, 0x31)
    assert exc.sid == 0x21 and exc.nrc == 0x31 and exc.nrc_name == "requestOutOfRange"
    assert exc.is_not_supported and not exc.is_busy and not exc.is_response_pending
    assert "readDataByLocalIdentifier" in str(exc) and "0x31" in str(exc)
    assert isinstance(exc, KwpError)
    assert KwpNegativeResponse(0x31, 0x23).is_busy


# ----------------------------------------------------------------- request core

def test_pending_0x78_keeps_waiting_without_resend():
    final = h("5A 9B") + b"x" * 46
    link = ScriptedLink([[h("7F 1A 78"), h("7F 1A 78"), h("7F 1A 78"), final]])
    client = KwpClient(link, FAST)
    assert client.read_ecu_identification(0x9B) == b"x" * 46
    assert link.sent == [h("1A 9B")]          # never resent


def test_pending_limit_exceeded_is_a_timeout():
    link = ScriptedLink([[h("7F 1A 78")] * 7 + [h("5A 9B") + b"x" * 30]])
    client = KwpClient(link, FAST)
    with pytest.raises(KwpTimeout, match="responsePending"):
        client.read_ecu_identification(0x9B)
    assert len(link.sent) == 1


def test_pending_switches_to_p2_star_window():
    class SlowLink(ScriptedLink):
        def recv(self, timeout):
            r = super().recv(timeout)
            if r == h("7F 21 78"):
                time.sleep(0.3)   # the final answer arrives after P2 but within P2*
            return r
    link = SlowLink([[h("7F 21 78"), h("61 01 01 44 32")]])
    client = KwpClient(link, KwpTiming(p2=0.1, p2_star=2.0))
    assert client.read_data_by_local_id(1) == h("01 44 32")


def test_busy_repeat_resends_after_delay_and_is_bounded():
    link = ScriptedLink([[h("7F 21 21")], [h("7F 21 23")], [h("61 02 01 C8 00")]])
    client = KwpClient(link, KwpTiming(p2=0.2, busy_delay=0.02, retry_on_busy=5))
    t0 = time.monotonic()
    assert client.read_data_by_local_id(2) == h("01 C8 00")
    assert link.sent == [h("21 02")] * 3
    assert time.monotonic() - t0 >= 0.04
    link = ScriptedLink([[h("7F 21 21")]] * 10)
    client = KwpClient(link, KwpTiming(p2=0.2, busy_delay=0.001, retry_on_busy=2))
    with pytest.raises(KwpNegativeResponse) as ei:
        client.read_data_by_local_id(2)
    assert ei.value.nrc == 0x21 and len(link.sent) == 3


def test_other_nrc_raises_with_name():
    link = ScriptedLink([[h("7F 1A 11")]])
    with pytest.raises(KwpNegativeResponse) as ei:
        KwpClient(link, FAST).read_ecu_identification(0x86)
    assert (ei.value.sid, ei.value.nrc, ei.value.nrc_name) == (0x1A, 0x11, "serviceNotSupported")


def test_stray_and_foreign_replies_are_skipped():
    link = ScriptedLink([[h("7E"), h("7F 3E 11"), h("61 01 01 44 32")]])
    assert KwpClient(link, FAST).read_data_by_local_id(1) == h("01 44 32")


def test_silence_is_a_timeout_and_malformed_negative_is_unexpected():
    with pytest.raises(KwpTimeout):
        KwpClient(ScriptedLink([[]]), FAST).tester_present()
    with pytest.raises(UnexpectedKwpResponse):
        KwpClient(ScriptedLink([[h("7F 21")]]), FAST).read_data_by_local_id(1)
    with pytest.raises(ValueError):
        KwpClient(ScriptedLink([[]]), FAST).request(b"")


def test_raw_passthrough_returns_negative_bytes_unless_asked_to_raise():
    client, ecu, link = me7_client()
    assert client.raw(h("1A 86")) == h("7F 1A 11")
    assert client.last_exchange == (h("1A 86"), h("7F 1A 11"))
    assert client.raw(h("3E")) == h("7E")
    with pytest.raises(KwpNegativeResponse):
        client.raw(h("1A 86"), raise_negative=True)
    assert client.raw(h("1A 9B"))[:2] == h("5A 9B")    # the pending preamble is waited out


# ----------------------------------------------------------------- sessions

def test_start_session_0x89_repeatable_and_others_refused():
    client, ecu, link = me7_client()
    assert client.start_diagnostic_session() == b""
    assert client.start_diagnostic_session(0x89) == b""
    assert link.sent[-2:] == [h("10 89"), h("10 89")] and client.session == 0x89 and ecu.session == 0x89
    with pytest.raises(KwpNegativeResponse) as ei:
        client.start_diagnostic_session(0x86)
    assert ei.value.nrc == 0x11
    client.stop_diagnostic_session()
    assert link.sent[-1] == h("20") and client.session is None and ecu.session is None


def test_tester_present_bare_3e_and_echo_mismatch():
    client, ecu, link = me7_client()
    client.tester_present()
    assert link.sent[-1] == h("3E")
    bad = KwpClient(ScriptedLink([[h("50 85")]]), FAST)
    with pytest.raises(UnexpectedKwpResponse):
        bad.start_diagnostic_session(0x89)
    client.stop_communication()
    assert link.sent[-1] == h("82")


# ----------------------------------------------------------------- reads

def test_read_ecu_identification_record_and_unknown_option():
    client, ecu, link = me7_client()
    rec = client.read_ecu_identification(0x9B)
    assert rec[:11] == b"022906032KR" and rec[11] == 0x20 and rec[12:16] == b"1098"
    assert rec[16] == 0x03 and rec[17] == 0x00 and int.from_bytes(rec[18:20], "big") == 178
    assert rec[26:].rstrip() == b"R32-DQ-LEV2 G"
    assert link.sent[-1] == h("1A 9B")
    with pytest.raises(KwpNegativeResponse) as ei:
        client.read_ecu_identification(0x86)
    assert ei.value.nrc == 0x11 and ei.value.is_not_supported
    with pytest.raises(UnexpectedKwpResponse):
        KwpClient(ScriptedLink([[h("5A 91 05 41 42 43 44 FF")]]), FAST).read_ecu_identification(0x9B)


def test_read_data_by_local_id_and_unknown_group():
    client, ecu, link = me7_client()
    data = client.read_data_by_local_id(2)
    assert len(data) == 24 and data[0] == 0x01        # 8 fields like a real PQ35 engine
    assert link.sent[-1] == h("21 02")
    with pytest.raises(KwpNegativeResponse) as ei:
        client.read_data_by_local_id(0xFE)
    assert ei.value.nrc == 0x31


def test_read_dtc_by_status_records_and_fallback():
    client, ecu, link = me7_client()
    assert client.read_dtc_by_status() == [(0x4065, 0x68), (0x029C, 0x2C)]
    assert link.sent[-1] == h("18 02 FF 00")
    link2 = ScriptedLink([[h("7F 18 12")], [h("58 01 40 65 68")]])
    assert KwpClient(link2, FAST).read_dtc_by_status() == [(0x4065, 0x68)]
    assert link2.sent == [h("18 02 FF 00"), h("18 00 FF 00")]
    link3 = ScriptedLink([[h("7F 18 11")]])
    with pytest.raises(KwpNegativeResponse):
        KwpClient(link3, FAST).read_dtc_by_status()
    assert len(link3.sent) == 1


def test_parse_dtc_list_layout_checks():
    assert parse_dtc_list(h("58 00")) == []
    assert parse_dtc_list(h("58 02 40 65 68 02 9C 2C")) == [(0x4065, 0x68), (0x029C, 0x2C)]
    with pytest.raises(UnexpectedKwpResponse):
        parse_dtc_list(h("58 02 40 65 68"))
    with pytest.raises(UnexpectedKwpResponse):
        parse_dtc_list(h("61 00"))


def test_clear_diagnostic_information_echo_and_effect():
    client, ecu, link = me7_client()
    client.clear_diagnostic_information()
    assert link.sent[-1] == h("14 FF 00") and ecu.cleared == 1
    assert client.read_dtc_by_status() == []
    with pytest.raises(UnexpectedKwpResponse):
        KwpClient(ScriptedLink([[h("54 FF FF")]]), FAST).clear_diagnostic_information()


def test_read_memory_by_address_no_skipped_byte():
    client, ecu, link = me7_client()
    data = client.read_memory_by_address(0x00F888, 4)
    assert link.sent[-1] == h("23 00 F8 88 04")
    assert data == ecu.brain.ram[0xF888:0xF88C]
    assert len(client.read_memory_by_address(0, 254)) == 254
    for bad in (0, 255):
        with pytest.raises(ValueError):
            client.read_memory_by_address(0, bad)
    with pytest.raises(ValueError):
        client.read_memory_by_address(0x1000000, 1)
    with pytest.raises(KwpNegativeResponse) as ei:
        client.read_memory_by_address(0xFFFF, 2)
    assert ei.value.nrc == 0x31
    with pytest.raises(UnexpectedKwpResponse):
        KwpClient(ScriptedLink([[h("63 01 02")]]), FAST).read_memory_by_address(0, 4)


# ----------------------------------------------------------------- routines / writes

def test_capability_query_framing_matches_the_real_engine():
    client, ecu, link = me7_client()
    body = client.start_routine_by_local_id(0xB8, h("00 00"))
    assert link.sent[-1] == h("31 B8 00 00")
    assert body == h("01 01 01 03 01 02 01 06 01 07 01 08 01 0D 01 18")   # NefMoto 1K0907115L reply


def test_routine_stop_and_results_framing():
    link = ScriptedLink([[h("72 B8 01 03")], [h("73 C5 00 01")], [h("71 B9 01 03 02")]])
    client = KwpClient(link, FAST)
    assert client.stop_routine_by_local_id(0xB8, h("01 03")) == h("01 03")
    assert client.request_routine_results_by_local_id(0xC5) == h("00 01")
    assert client.start_routine_by_local_id(0xB9, h("01 03 02")) == h("01 03 02")
    assert link.sent == [h("32 B8 01 03"), h("33 C5"), h("31 B9 01 03 02")]
    with pytest.raises(UnexpectedKwpResponse):
        KwpClient(ScriptedLink([[h("71 B9")]]), FAST).start_routine_by_local_id(0xB8)


def test_write_and_io_control_framing_and_sim_refusal(caplog):
    caplog.set_level(logging.WARNING)
    link = ScriptedLink([[h("7B 9A")], [h("70 10 01")]])
    client = KwpClient(link, FAST)
    assert client.write_data_by_local_id(0x9A, h("AA BB")) == b""
    assert client.io_control_by_local_id(0x10, h("01")) == h("01")
    assert link.sent == [h("3B 9A AA BB"), h("30 10 01")]
    assert any("write to the module" in r.getMessage() for r in caplog.records)
    client2, ecu, _ = me7_client()
    with pytest.raises(KwpNegativeResponse) as ei:
        client2.write_data_by_local_id(0x9A, b"\x00")
    assert ei.value.nrc == 0x33
    with pytest.raises(KwpNegativeResponse) as ei:
        client2.io_control_by_local_id(0x10, b"\x01")
    assert ei.value.nrc == 0x31


# ----------------------------------------------------------------- keepalive

def test_tester_present_thread_shares_the_send_lock():
    client, ecu, link = me7_client()
    client.start_tester_present(0.01)
    assert client.tester_present_running
    for _ in range(40):
        assert client.read_data_by_local_id(1)[:3] == h("01 44 32")
    time.sleep(0.05)
    client.stop_tester_present()
    assert not client.tester_present_running
    assert client._tp_thread is None
    assert sum(1 for r in ecu.requests if r == h("3E")) >= 2
    # every reply matched its request: no 7E leaked into a 21 answer
    assert all(r[0] == 0x61 for r in [ecu.handle(h("21 01"))])


def test_tester_present_thread_survives_errors_and_close_stops_it():
    link = ScriptedLink([[h("7F 3E 11")]] * 50)
    client = KwpClient(link, KwpTiming(p2=0.02))
    client.start_tester_present(0.01)
    time.sleep(0.08)
    assert client._tp_thread.errors >= 1 and client.tester_present_running
    client.close()
    assert not client.tester_present_running


# ----------------------------------------------------------------- simulator

def test_sim_unsupported_services_get_nrc_never_silence():
    ecu = SimulatedKwpEcu(Me7Brain())
    assert ecu.handle(h("27 01")) == h("7F 27 11")
    assert ecu.handle(h("2C F0")) == h("7F 2C 11")
    assert ecu.handle(h("10 85")) == h("7F 10 11")
    assert ecu.handle(h("18 02 FF FF")) == h("7F 18 12")
    assert ecu.handle(h("18 03 FF 00")) == h("7F 18 12")
    assert ecu.handle(h("14 00 00")) == h("7F 14 31")
    assert ecu.handle(h("23 00 00")) == h("7F 23 12")
    assert ecu.handle(h("31 BB 01 03 00 00")) == h("7F 31 33")
    assert ecu.handle(h("31 B8 01 55")) == h("7F 31 31")
    assert ecu.handle(h("32 B8 01 03")) == h("7F 32 22")
    assert ecu.handle(h("1A")) == h("7F 1A 12")
    assert ecu.handle(h("1A 9F")) == h("7F 1A 11")       # only the gateway has a list
    assert ecu.handle(b"") is None and ecu.handle_all(b"") == []


def test_sim_pending_once_and_busy_hook():
    ecu = SimulatedKwpEcu(Me7Brain())
    replies = ecu.handle_all(h("1A 9B"))
    assert replies[0] == h("7F 1A 78") and replies[1][:2] == h("5A 9B")
    assert ecu.handle_all(h("1A 9B"))[0][:2] == h("5A 9B")        # only once
    ecu.busy_once = {0x21}
    assert ecu.handle(h("21 01")) == h("7F 21 21")
    assert ecu.handle(h("21 01"))[:2] == h("61 01")


def test_sim_brains_identities_match_the_scans():
    for brain, part, sw, comp, coding in [
        (Me7Brain(), "022906032KR", "1098", "R32-DQ-LEV2 G", 178),
        (Edc17Brain(), "03L906019EE", "1181", "R4 2,0L EDC G000SG", 50072),
        (Dq250Brain(), "02E927770AD", "1405", "GSG DSG 082", 20),
        (HaldexBrain(), "1K0907554L", "0116", "Haldex 4Motion", 1),
    ]:
        rec = SimulatedKwpEcu(brain).handle(h("1A 9B"))
        if rec[:3] == h("7F 1A 78"):
            rec = SimulatedKwpEcu(brain).handle_all(h("1A 9B"))[-1]
        body = rec[2:]
        assert body[:11].decode().rstrip() == part and body[12:16].decode() == sw
        assert body[16] == 0x03 and int.from_bytes(body[18:20], "big") == coding
        assert body[26:].decode().rstrip() == comp
    gw = SimulatedKwpEcu(GatewayBrain())
    body = gw.handle(h("1A 9B"))[2:]
    assert body[:11] == b"1K0907530L " and body[16] == 0x10 and body[18:20] == b"\x00\x00"
    rec9a = gw.handle(h("1A 9A"))[2:]
    assert rec9a[6:10] == b"0052" and rec9a[10] == 0x10 and rec9a[11] == 10
    assert rec9a[12:21] == h("ED831F075003020000") and rec9a[-1] == 0xFF
    assert gw.handle(h("1A 9F"))[:2] == h("5A 9F")
    assert gw.handle(h("21 01")) == h("7F 21 31")
    eps = SimulatedKwpEcu(BodyBrain("steering", "1K0909144E", "EPS_ZFLS", "2501"))
    body = eps.handle(h("1A 9B"))[2:]
    assert body[:16] == b"1K0909144E  2501" and body[16] == 0x00
    assert eps.handle(h("1A 91")) == h("5A 91 0E") + b"1K0909144E   " + b"\xFF"


def test_build_ident_9b_matches_the_nefmoto_record():
    body = build_ident_9b("1K0907115L", "0030", 0x10, 0, h("00 06 46 22 04 F5"), "2.0l R4/4V TFSI")
    assert body == h("31 4B 30 39 30 37 31 31 35 4C 20 20 30 30 33 30 10 00 00 00 00 06 46 22 04 F5"
                     "32 2E 30 6C 20 52 34 2F 34 56 20 54 46 53 49 20 20 20 20 20")
    assert len(h("5A 9B") + body) == 48
    with pytest.raises(ValueError):
        build_ident_9b("TOO-LONG-PART-NUMBER", "0030", 0, 0, bytes(6), "x")


def test_sim_group_tables_hold_the_registry_groups():
    assert {1, 2, 3, 4, 5, 20, 32, 33, 81, 100, 125} <= set(Me7Brain().groups)
    assert {2, 11, 20, 46, 86, 89, 99, 108, 240, 241} <= set(Edc17Brain().groups)
    assert {1, 13, 19} <= set(Dq250Brain().groups)
    assert {1, 2, 125} <= set(HaldexBrain().groups)
    assert all(len(v) == 24 for g, v in Me7Brain().groups.items() if g != 81)


def test_concurrent_clients_on_separate_brains_do_not_cross_talk():
    a, ecu_a, _ = me7_client()
    b_ecu = SimulatedKwpEcu(Dq250Brain())
    b = KwpClient(FakePayloadLink(b_ecu), FAST)
    errors: List[str] = []

    def hammer(client, expect):
        for _ in range(30):
            try:
                if client.read_ecu_identification(0x9B)[:11].rstrip() != expect:
                    errors.append("mismatch")
            except KwpError as exc:
                errors.append(str(exc))

    ta = threading.Thread(target=hammer, args=(a, b"022906032KR"))
    tb = threading.Thread(target=hammer, args=(b, b"02E927770AD"))
    ta.start(); tb.start(); ta.join(); tb.join()
    assert errors == []
