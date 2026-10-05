"""
vag.kwp_session / vag.kwp_recipes: byte-exact identification parsing against the
real dumps in the research sheet, VCDS-style DTC decoding, the read-only probes with
their UNVERIFIED flags, the gateway list, the recipe table, and the simulated brains
end to end (plus one optional TP 2.0 round trip through the simulated vehicle).
"""

from __future__ import annotations

import logging
import queue
from typing import List

import pytest

from vagtune.kwp import services as S
from vagtune.kwp.client import KwpClient, KwpTiming
from vagtune.kwp.exceptions import KwpNegativeResponse, UnexpectedKwpResponse
from vagtune.kwp.sim import (
    BCM_LONG_CODING_PLACEHOLDER,
    GOLF_ABS_CODING,
    GOLF_GATEWAY_CODING,
    GOLF_RADIO_CODING,
    GOLF_TDI_KWP_MODULES,
    R32_KWP_MODULES,
    BodyBrain,
    Dq250Brain,
    Edc17Brain,
    GatewayBrain,
    HaldexBrain,
    Me7Brain,
    R32_INSTALLATION,
    SimulatedKwpEcu,
    pack_wsc_block as sim_pack,
)
from vagtune.vag import dtc as V
from vagtune.vag import kwp_recipes as R
from vagtune.vag.kwp_session import (
    KWP2000_ELABORATION,
    AdaptationProbe,
    KwpFault,
    KwpIdentity,
    VagKwpSession,
    decode_kwp_fault,
    kwp1281_rows_for_nibble,
    parse_ident_9a,
    parse_ident_9b,
    parse_installation_list,
    parse_length_prefixed_records,
    unpack_wsc_block,
)

h = bytes.fromhex
FAST = KwpTiming(p2=0.3, p2_star=0.6, busy_delay=0.01)


@pytest.fixture(autouse=True)
def _fresh_warnings():
    V._reset_unverified_warnings()
    S._reset_unverified_warnings()
    yield
    V._reset_unverified_warnings()
    S._reset_unverified_warnings()


def _warnings(caplog, needle: str) -> List[str]:
    return [r.getMessage() for r in caplog.records if "UNVERIFIED" in r.getMessage() and needle in r.getMessage()]


class FakePayloadLink:
    def __init__(self, ecu: SimulatedKwpEcu) -> None:
        self.ecu = ecu
        self._q: "queue.Queue[bytes]" = queue.Queue()
        self.sent: List[bytes] = []

    def send(self, payload: bytes) -> None:
        self.sent.append(bytes(payload))
        for r in self.ecu.handle_all(payload):
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


class ScriptedLink(FakePayloadLink):
    def __init__(self, script):
        self.script = [list(s) for s in script]
        self._q = queue.Queue()
        self.sent = []

    def send(self, payload: bytes) -> None:
        self.sent.append(bytes(payload))
        for r in (self.script.pop(0) if self.script else []):
            self._q.put(r)


def session_for(brain) -> tuple:
    ecu = SimulatedKwpEcu(brain)
    link = FakePayloadLink(ecu)
    return VagKwpSession(KwpClient(link, FAST), module_name=brain.name), ecu, link


# ----------------------------------------------------------------- real 5A 9B dumps

NEFM_9B = h("31 4B 30 39 30 37 31 31 35 4C 20 20 30 30 33 30 10 00 00 00 00 06 46 22 04 F5"
            "32 2E 30 6C 20 52 34 2F 34 56 20 54 46 53 49 20 20 20 20 20")
BLAFUSEL_9B = h("30 32 32 39 30 36 30 33 32 47 4B 20 36 32 34 33 03 00 00 AC 00 00 00 00 19 23") \
    + b"MOTRONIC ME7.1.*G   "
VDS_9B = b"8P0907115AQ" + h("20") + b"0010" + h("10 00 00 00 01 DC 5A 10 00 BF") + b"2.0l R4/4V TFSI    "


def test_parse_9b_nefmoto_engine_byte_exact(caplog):
    caplog.set_level(logging.WARNING)
    i = parse_ident_9b(NEFM_9B)
    assert i.part_number == "1K0907115L" and i.software_version == "0030"
    assert i.coding_type == 0x10 and i.coding_type_name == "long coding" and i.short_coding == 0
    assert i.wsc_block == h("00 06 46 22 04 F5") and i.component == "2.0l R4/4V TFSI"
    assert i.component_line == "2.0l R4/4V TFSI 0030" and i.layout_ok and i.source == "9B"
    assert (i.wsc, i.importer, i.equipment) == (1269, 785, 200)      # Basano's logger printed 1269 / 785 / 200
    assert i.shop_line == "WSC 01269 785 00200"
    assert i.unverified_fields == ["wsc", "importer", "equipment"]
    assert len(_warnings(caplog, "WSC")) == 1
    parse_ident_9b(BLAFUSEL_9B)
    assert len(_warnings(caplog, "WSC")) == 1                       # once per process
    assert i.coding is None and "1A 9A" in i.coding_text


def test_parse_9b_blafusel_me7_and_vds_audi():
    i = parse_ident_9b(BLAFUSEL_9B)
    assert i.part_number == "022906032GK" and i.software_version == "6243"
    assert i.coding_type == 0x03 and i.short_coding == 172 and i.coding_text == "0000172"
    assert i.coding == h("00 AC") and i.component == "MOTRONIC ME7.1.*G"
    assert (i.wsc, i.importer, i.equipment) == (6435, 0, 0)
    i = parse_ident_9b(VDS_9B)
    assert i.part_number == "8P0907115AQ" and i.software_version == "0010" and i.coding_type == 0x10
    assert (i.wsc, i.importer, i.equipment) == (191, 264, 15243)
    assert i.identity_key() == {"part_number": "8P0907115AQ", "software_version": "0010"}
    d = i.to_dict()
    assert d["raw_9b"] == VDS_9B.hex() and d["wsc"] == 191 and d["coding_type_name"] == "long coding"


def test_parse_9b_eps_prefix_and_short_records():
    eps = b"1K0909144E  2501"
    i = parse_ident_9b(eps)
    assert i.part_number == "1K0909144E" and i.software_version == "2501"
    assert i.coding_type is None and i.short_coding is None and i.wsc is None and not i.layout_ok
    assert i.shop_line.startswith("WSC ?????") and i.source == "9B"
    short = parse_ident_9b(b"short")                       # kept as text, never refused
    assert short.part_number == "short" and short.software_version == "" and not short.layout_ok
    assert short.source == "9B-short" and short.raw_9b == b"short" and "shorter" in short.pretty()
    with pytest.raises(UnexpectedKwpResponse):
        parse_ident_9b(b"")
    i = parse_ident_9b(eps + h("00 00 00 00") + bytes(6) + b"EPS_ZFLS")
    assert i.coding_type == 0 and i.short_coding is None and i.coding_text == "-" and i.component == "EPS_ZFLS"


def test_r32_wsc_sample_and_packing_round_trip():
    block = sim_pack(1279, 785, 200)
    assert unpack_wsc_block(block) == (1279, 785, 200)
    assert unpack_wsc_block(h("00 00 04 50 10 34")) == (4148, 552, 0)        # bri3d save block
    for sample, expect in [(h("00 00 00 00 19 23"), (6435, 0, 0)), (h("00 06 46 22 04 F5"), (1269, 785, 200)),
                           (h("01 DC 5A 10 00 BF"), (191, 264, 15243))]:
        assert unpack_wsc_block(sample) == expect
        assert R.pack_wsc_block(*expect) == sample
    with pytest.raises(ValueError):
        unpack_wsc_block(b"\x00")
    with pytest.raises(ValueError):
        R.pack_wsc_block(200000, 0, 0)


def test_length_prefixed_records_and_91_fallback():
    assert parse_length_prefixed_records(h("0E") + b"8P0907115B   " + h("FF")) == [b"8P0907115B   "]
    assert parse_length_prefixed_records(h("0E") + b"HW000      " + h("20 20 FF")) == [b"HW000        "]
    assert parse_length_prefixed_records(h("03 41 42 03 43 44 FF")) == [b"AB", b"CD"]
    assert parse_length_prefixed_records(h("05 41 42")) == [b"AB"]       # overrun -> truncated record
    with pytest.raises(UnexpectedKwpResponse):
        parse_length_prefixed_records(h("00 41"))
    link = ScriptedLink([[h("7F 1A 11")], [h("5A 91 0E") + b"8P0907115B   " + h("FF")]])
    s = VagKwpSession(KwpClient(link, FAST))
    i = s.read_identification()
    assert i.source == "91" and i.part_number == "8P0907115B" and i.hardware_number == "8P0907115B"
    assert link.sent == [h("1A 9B"), h("1A 91")] and "fallback" in i.pretty()
    link = ScriptedLink([[h("7F 1A 11")], [h("5A 91 FF")]])
    with pytest.raises(UnexpectedKwpResponse):
        VagKwpSession(KwpClient(link, FAST)).read_identification()


ABS_EMULATOR_9B = b"1K0907379 0143"        # registry 7.5 Reported: pq35-abs-emulator's bare 1A 9B answer


def test_short_9b_record_is_identified_and_corroborated_by_91():
    i = parse_ident_9b(ABS_EMULATOR_9B)
    assert i.part_number == "1K0907379" and i.software_version == "0143" and i.source == "9B-short"
    assert not i.layout_ok and i.coding_type is None and i.wsc is None and i.raw_9b == ABS_EMULATOR_9B
    link = ScriptedLink([[h("5A 9B") + ABS_EMULATOR_9B], [h("5A 91 0F") + ABS_EMULATOR_9B + h("FF")]])
    s = VagKwpSession(KwpClient(link, FAST))
    ident = s.read_identification()
    assert "1K0907379" in ident.part_number and ident.hardware_number == "1K0907379 0143"
    assert ident.source == "9B-short" and ident.raw_91_records == [ABS_EMULATOR_9B]
    assert link.sent == [h("1A 9B"), h("1A 91")]
    assert ident.identity_key() == {"part_number": "1K0907379", "software_version": "0143"}
    # 91 refused: the short 9B identity still stands
    link = ScriptedLink([[h("5A 9B") + ABS_EMULATOR_9B], [h("7F 1A 11")]])
    ident = VagKwpSession(KwpClient(link, FAST)).read_identification()
    assert ident.part_number == "1K0907379" and ident.hardware_number is None and ident.source == "9B-short"
    # an empty 9B body falls back to 91
    link = ScriptedLink([[h("5A 9B")], [h("5A 91 0E") + b"8P0907115B   " + h("FF")]])
    ident = VagKwpSession(KwpClient(link, FAST)).read_identification()
    assert ident.source == "91" and ident.part_number == "8P0907115B" and link.sent == [h("1A 9B"), h("1A 91")]
    # only when both fail is the module unidentifiable
    link = ScriptedLink([[h("5A 9B")], [h("5A 91 FF")]])
    with pytest.raises(UnexpectedKwpResponse, match="1A 91 returned no records"):
        VagKwpSession(KwpClient(link, FAST)).read_identification()
    link = ScriptedLink([[h("5A 9B")], [h("7F 1A 11")]])
    with pytest.raises(KwpNegativeResponse):
        VagKwpSession(KwpClient(link, FAST)).read_identification()


def test_parse_9a_vds_sample_flagged(caplog):
    caplog.set_level(logging.WARNING)
    rec = parse_ident_9a(h("01 DC 5A 10 00 BF 30 30 31 30 10 09 01 03 00 0C 18 0F 01 60 FF"))
    assert rec.parsed and rec.unverified and rec.coding == h("01 03 00 0C 18 0F 01 60")
    assert rec.software_version == "0010" and rec.coding_type == 0x10 and rec.wsc_block == h("01 DC 5A 10 00 BF")
    assert len(_warnings(caplog, "9A")) == 1
    short = parse_ident_9a(h("01 02"))
    assert not short.parsed and short.raw == h("01 02")


def test_read_identification_with_long_coding_on_the_gateway():
    s, ecu, link = session_for(GatewayBrain())
    i = s.read_identification(with_long_coding=True, with_hardware_number=True)
    assert i.part_number == "1K0907530L" and i.component_line == "J533 Gateway H07 0052"
    assert i.coding_type == 0x10 and i.long_coding is not None and i.long_coding.parsed
    assert i.coding == h("ED831F075003020000") and i.coding_text == "ED831F075003020000"
    assert i.hardware_number == "1K0907951" and "long_coding" in i.unverified_fields
    assert link.sent == [h("1A 9B"), h("1A 91"), h("1A 9A")]
    assert s.read_coding()["coding"] == "ED831F075003020000"
    s2, _, _ = session_for(Me7Brain())
    c = s2.read_coding()
    assert c["short_coding"] == 178 and c["coding"] == "0000178" and c["long_coding_raw"] is None


# ----------------------------------------------------------------- DTC decode

def test_decode_known_pairs_5_digit_numbers():
    f = decode_kwp_fault(0x4065, 0b01101000)
    assert (f.sae_code, f.vag5, f.vag6) == ("P0101", "16485", "000257")
    assert f.elaboration == 8 and f.elaboration_text == "Implausible Signal" and f.elaboration_verified
    assert not f.intermittent and f.active and not f.mil and f.stored_bit
    assert f.text.startswith("Mass Air Flow Sensor (G70)")
    assert f.vcds_lines()[1] == "P0101 - 008 - Implausible Signal" and f.status_bits == "01101000"
    assert decode_kwp_fault(0x412B, 0x60).sae_code == "P0299" and decode_kwp_fault(0x412B, 0x60).vag5 == "16683"
    assert decode_kwp_fault(0x462C, 0x60).sae_code == "P1556" and decode_kwp_fault(0x462C, 0x60).vag5 == "17964"
    assert decode_kwp_fault(0x465A, 0x60).sae_code == "P1602" and int(decode_kwp_fault(0x465A, 0x60).vag5) == 18010
    assert decode_kwp_fault(0x4000, 0x60).sae_code == "P0000"
    assert decode_kwp_fault(0x7064, 0x60).sae_code == "U0100"


def test_decode_factory_only_number_below_16384():
    f = decode_kwp_fault(0x011F, 0b01101100)
    assert f.is_factory_only and f.sae_code == "" and f.vag5 == "00287" and f.vag6 is None
    assert "G44" in f.text and f.elaboration == 12 and f.elaboration_text == "Electrical Fault in Circuit"
    assert f.vcds_lines()[0] == "00287 - ABS Wheel Speed Sensor Rear Right (G44)"
    assert f.vcds_lines()[1] == "012 - Electrical Fault in Circuit"
    g = decode_kwp_fault(0x8355, 0x60)
    assert g.is_factory_only and g.vag5 == "33621" and "no description" in g.text
    assert f.raw == h("01 1F 6C") and f.number == 0x011F


def test_status_byte_pairs_from_real_autoscans():
    pairs = {0b01100000: (0, False), 0b00100000: (0, True), 0b01100100: (4, False), 0b01100111: (7, False),
             0b01101000: (8, False), 0b00101010: (10, True), 0b00111010: (10, True), 0b00101011: (11, True),
             0b01101100: (12, False), 0b01101101: (13, False), 0b01101110: (14, False), 0b00101110: (14, True)}
    texts = {0: "-", 4: "No Signal/Communication", 7: "Short to Ground", 8: "Implausible Signal",
             10: "Open or Short to Plus", 11: "Open Circuit", 12: "Electrical Fault in Circuit",
             13: "Check DTC Memory", 14: "Defective"}
    for status, (code, intermittent) in pairs.items():
        f = decode_kwp_fault(0x4065, status)
        assert (f.elaboration, f.intermittent) == (code, intermittent), f"{status:08b}"
        assert f.elaboration_text == texts[code] and f.elaboration_verified
    assert set(KWP2000_ELABORATION) == set(range(16))
    assert {c for c, e in KWP2000_ELABORATION.items() if not e.verified} == {2, 3, 5, 6, 9, 15}
    assert "Open Circuit" in kwp1281_rows_for_nibble(0xB) and "Short to Plus" in kwp1281_rows_for_nibble(6)


def test_unverified_status_bits_warn_once(caplog):
    caplog.set_level(logging.WARNING)
    f = decode_kwp_fault(0x4065, 0b11100000)
    assert f.mil and "mil" in f.unverified_fields and "MIL?" in f.status_text and "MIL?" in f.vcds_lines()[1]
    decode_kwp_fault(0x4065, 0b11100000)
    assert len(_warnings(caplog, "bit 7")) == 1
    g = decode_kwp_fault(0x0431, 0b00100010)
    assert g.elaboration_text == "Lower Limit Exceeded" and not g.elaboration_verified
    assert "elaboration_text" in g.unverified_fields and g.intermittent
    decode_kwp_fault(0x0431, 0b00100010)
    assert len(_warnings(caplog, "002")) == 1


def test_session_read_and_clear_dtcs_on_the_r32_engine():
    s, ecu, link = session_for(Me7Brain())
    faults = s.read_dtcs()
    assert [f.vag5 for f in faults] == ["16485", "00668"]
    assert faults[1].intermittent and faults[1].elaboration == 12
    assert str(faults[0]) == "16485 - Mass Air Flow Sensor (G70): Implausible Signal / P0101 - 008 - Implausible Signal"
    assert s.read_dtcs_raw() == [(0x4065, 0x68), (0x029C, 0x2C)]
    s.clear_dtcs()
    assert link.sent[-1] == h("14 FF 00") and s.read_dtcs() == []


def test_supported_codes_read_is_flagged_and_sim_refuses(caplog):
    caplog.set_level(logging.WARNING)
    s, ecu, link = session_for(Me7Brain())
    with pytest.raises(KwpNegativeResponse) as ei:
        s.read_supported_dtcs()
    assert ei.value.nrc == 0x12 and link.sent[-1] == h("18 03 FF 00") and len(_warnings(caplog, "18 03")) == 1


# ----------------------------------------------------------------- groups / RAM

def test_read_group_read_groups_and_scan():
    s, ecu, link = session_for(Me7Brain())
    vals = s.read_group(4)
    assert vals[1].value == pytest.approx(14.025) and vals[1].unit == "V" and vals[2].value == pytest.approx(90.0)
    assert len(vals) == 8 and vals[4].group is None
    with pytest.raises(KwpNegativeResponse):
        s.read_group(200)
    got = s.read_groups([1, 2, 200, 81])
    assert set(got) == {1, 2, 81} and got[81][0].value == "WVWKC71K18W108211"
    with pytest.raises(KwpNegativeResponse):
        s.read_groups([200], skip_refused=False)
    assert s.scan_groups(range(0, 10)) == [1, 2, 3, 4, 5]
    flagged = s.read_group(2, second_half_is_group_plus_128=True)
    assert flagged[4].group == 130
    s2, _, _ = session_for(Edc17Brain())
    g11 = s2.read_group(11)
    assert len(g11) == 8                                   # 26-byte reply like the real CJAA
    assert [v.text for v in g11[:4]] == ["820 rpm", "1010 mbar", "1000 mbar", "100 %"]
    assert all(v.formula_id == 0x25 for v in g11[4:])
    assert s2.read_group(11, second_half_is_group_plus_128=True)[4].group == 139
    g99 = s2.read_group(99)
    assert g99[1].value == pytest.approx(180.0) and g99[1].unit == "°C"
    s3, _, _ = session_for(Dq250Brain())
    g19 = s3.read_group(19)
    assert [v.value for v in g19[:3]] == [55, 57, 58] and all(v.unit == "°C" for v in g19[:3])
    s4, _, _ = session_for(HaldexBrain())
    g2 = s4.read_group(2)
    assert [v.text for v in g2] == ["27 bar", "2032 Nm", "40 %", "1.91 A"]


def test_read_ram_chunks_and_errors():
    s, ecu, link = session_for(Me7Brain())
    data = s.read_ram(0x100, 300)
    assert data == ecu.brain.ram[0x100:0x100 + 300]
    assert link.sent[-2:] == [h("23 00 01 00 FE"), h("23 00 01 FE 2E")]
    with pytest.raises(ValueError):
        s.read_ram(0, 0)
    with pytest.raises(ValueError):
        s.read_ram(0, 10, chunk=300)
    with pytest.raises(KwpNegativeResponse):
        s.read_ram(0x20000, 4)


# ----------------------------------------------------------------- probes

def test_capability_query_verified_reply():
    s, ecu, link = session_for(Me7Brain())
    caps = s.capability_query()
    assert link.sent[-1] == h("31 B8 00 00")
    assert caps.raw == h("71 B8 01 01 01 03 01 02 01 06 01 07 01 08 01 0D 01 18")
    assert caps.codes == [0x0101, 0x0103, 0x0102, 0x0106, 0x0107, 0x0108, 0x010D, 0x0118]
    assert caps.supports(0x0103) and not caps.supports(0x0105) and "adaptation (REPORTED)" in str(caps)
    assert caps.names[0] == "basic settings in KWP1281 mode"


def test_capability_list_names_warn_once_for_reported_codes(caplog):
    caplog.set_level(logging.WARNING)
    s, ecu, link = session_for(Me7Brain())
    caps = s.capability_query()
    str(caps); caps.names; str(caps)
    assert len(_warnings(caplog, "0103")) == 1


def test_adaptation_probe_sequence_flagged_and_never_saves(caplog):
    caplog.set_level(logging.WARNING)
    s, ecu, link = session_for(Me7Brain())
    probe = s.read_adaptation_probe(2)
    assert isinstance(probe, AdaptationProbe) and probe.unverified
    assert link.sent[-4:] == [h("31 B8 01 03"), h("31 B9 01 03 02"), h("31 BA 01 03"), h("32 B8 01 03")]
    assert probe.value == 100 and probe.echoed_channel == 2 and probe.decoded
    assert probe.replies["read"] == h("01 03 02 00 64") and probe.replies["stop"] == h("01 03")
    assert "UNVERIFIED" in str(probe)
    assert not any(r[:2] == h("31 BB") for r in link.sent) and not ecu.adaptation_open
    s.read_adaptation(1)
    assert len(_warnings(caplog, "adaptation")) == 1
    with pytest.raises(KwpNegativeResponse):           # unknown channel is refused, the probe still stops
        s.read_adaptation_probe(77)
    assert link.sent[-1] == h("32 B8 01 03") and not ecu.adaptation_open
    with pytest.raises(ValueError):
        s.read_adaptation_probe(300)
    s2, _, link2 = session_for(HaldexBrain())           # no 0103 capability -> refused at the start
    with pytest.raises(KwpNegativeResponse) as ei:
        s2.read_adaptation_probe(1)
    assert ei.value.nrc == 0x31 and link2.sent[-1] == h("31 B8 01 03")


def test_gateway_installation_list_parse_and_raw(caplog):
    caplog.set_level(logging.WARNING)
    s, ecu, link = session_for(GatewayBrain())
    gl = s.gateway_installation_list()
    assert link.sent[-1] == h("1A 9F") and gl.unverified and gl.raw == ecu.brain.installation_list
    assert len(gl.records) == 2 and gl.records[1] == h("ED831F075003020000")
    assert len(gl.entries) == 22 and {e.module_number for e in gl.entries} == {m for m, _, _ in R32_INSTALLATION}
    usable = gl.usable
    assert len(usable) == 21 and all(e.tp20_address != 0x13 for e in usable)
    gw = next(e for e in gl.entries if e.module_number == 0x19)
    assert gw.tp20_address == 0x1F and gw.present and gw.status == 0
    awd = next(e for e in gl.entries if e.module_number == 0x22)
    assert awd.tp20_address == 0x0A and awd.present and awd.status == 1
    assert "0x1F" in str(gw)
    s.gateway_installation_list()
    assert len(_warnings(caplog, "9F")) == 1
    bad = parse_installation_list(h("00 01"))
    assert bad.entries == [] and bad.raw == h("00 01")
    only_one = parse_installation_list(h("05 01 01 00 01 FF"))
    assert len(only_one.entries) == 1 and len(only_one.records) == 1
    s2, _, _ = session_for(Me7Brain())
    with pytest.raises(KwpNegativeResponse):
        s2.gateway_installation_list()


# ----------------------------------------------------------------- writes -> recipes

@pytest.mark.parametrize("method,args", [("login", (12233,)), ("write_coding", (b"\x00\xB2",)),
                                         ("write_adaptation", (2, 100)), ("basic_settings", (60,)),
                                         ("output_test", ())])
def test_write_functions_raise_not_implemented_and_point_to_recipes(method, args):
    s, ecu, link = session_for(Me7Brain())
    with pytest.raises(NotImplementedError) as ei:
        getattr(s, method)(*args)
    msg = str(ei.value)
    assert "kwp recipes" in msg and "kwp raw --yes" in msg and "VCDS capture" in msg
    for name in R.WRITE_FUNCTIONS[method]:
        assert name in msg
    assert link.sent == []                       # nothing was sent


def test_recipe_table_completeness():
    names = {r.name for r in R.RECIPES}
    for function, recipe_names in R.WRITE_FUNCTIONS.items():
        assert recipe_names and set(recipe_names) <= names, function
    assert {"login", "write_coding", "write_adaptation", "basic_settings", "output_test"} == set(R.WRITE_FUNCTIONS)
    for r in R.RECIPES:
        assert r.confidence and r.experiment and r.purpose and r.expected_reply and r.evidence
        assert r.confidence.split()[0] in ("low", "medium", "high")
        for step in r.steps:
            for tok in step.split():
                if not tok.startswith("<"):
                    int(tok, 16)
    writers = {r.name for r in R.RECIPES if r.writes}
    assert {"login", "coding-write-short", "coding-write-long", "adaptation-save", "basic-settings-start",
            "basic-settings-stop", "output-test-sequential", "output-test-selective"} == writers
    for name in ("login", "adaptation-save", "basic-settings-start", "output-test-sequential", "coding-write-short"):
        assert "VCDS (HEX-CAN)" in R.get_recipe(name).experiment      # IMPLEMENTATION_NOTES (d) item 8
    text = R.format_table()
    assert "MODELLED" in text and all(r.name in text for r in R.RECIPES) and "31 B9 01 05 <code:2>" in text
    with pytest.raises(KeyError):
        R.get_recipe("flash-ecu")
    assert R.get_recipe("login").placeholders == [("code", 2)]
    assert ("coding", 0) in R.get_recipe("coding-write-long").placeholders


def test_recipe_render_reproduces_bri3d_and_flags(caplog):
    caplog.set_level(logging.WARNING)
    assert R.render("login", {"code": 11463}, step=1) == h("31 B9 01 05 2C C7")
    assert R.render("login", step=0) == h("31 B8 01 05")
    wsc = R.pack_wsc_block(4148, 552, 0)
    assert R.render("adaptation-save", {"value": 0, "wsc": wsc}, step=3) == h("31 BB 01 03 00 00 00 00 04 50 10 34")
    assert R.render("basic-settings-start", {"group": 60}, step=1) == h("21 3C")
    assert R.render("security-access-27", {"level": 3}) == h("27 03")
    assert R.render("coding-write-long", {"wsc": bytes(6), "sw_version": b"0052", "len": 10,
                                          "coding": h("ED831F075003020000")}) == \
        h("3B 9A 00 00 00 00 00 00 30 30 35 32 10 0A ED 83 1F 07 50 03 02 00 00 FF")
    with pytest.raises(KeyError):
        R.render("login", step=1)
    with pytest.raises(IndexError):
        R.render("login", step=5)
    assert len(_warnings(caplog, "recipe 'login'")) == 1 and not _warnings(caplog, "security-access")


def test_render_rejects_bytes_of_the_wrong_width_for_fixed_width_placeholders():
    for bad in (b"\x01", bytes(5), bytes(7)):
        with pytest.raises(ValueError, match="<wsc:6>"):
            R.render("adaptation-save", {"value": 0, "wsc": bad}, step=3)
    assert len(R.render("adaptation-save", {"value": 0, "wsc": bytes(6)}, step=3)) == 12
    for bad in (b"\x2C\xC7\x00\x00", b"\x2C"):
        with pytest.raises(ValueError, match="<code:2>"):
            R.render("login", {"code": bad}, step=1)
    assert R.render("login", {"code": b"\x2C\xC7"}, step=1) == h("31 B9 01 05 2C C7")
    with pytest.raises(OverflowError):
        R.render("login", {"code": 70000}, step=1)
    with pytest.raises(ValueError):
        R.render("login", {"code": -1}, step=1)
    with pytest.raises(TypeError):
        R.render("login", {"code": "2CC7"}, step=1)
    with pytest.raises(TypeError):
        R.render("login", {"code": True}, step=1)


def test_render_ignores_template_comments():
    recipe = R.Recipe(name="t", vcds_function="", purpose="", request="31 B8 01 05 (or 27 <level>) ; 21 <group>",
                      expected_reply="", confidence="low", evidence="", experiment="", writes=False)
    assert recipe.steps == ["31 B8 01 05", "21 <group>"]
    assert R.render(recipe) == h("31 B8 01 05")
    assert R.render(recipe, {"group": 3}, step=1) == h("21 03")
    assert len(recipe.steps) == 2


# ----------------------------------------------------------------- end to end on brains

def test_full_report_r32_modules():
    for brain in (Me7Brain(), Dq250Brain(), HaldexBrain(), GatewayBrain(),
                  BodyBrain("abs", "1K0907379AB", "ESP 4MOTION MK60", "0102", coding=21128)):
        s, ecu, link = session_for(brain)
        s.open()
        report = s.full_report(groups=[1, 199])
        assert brain.part_number in report and ("No fault code found" in report or " - " in report)
        assert "refused" in report
    s, ecu, link = session_for(Me7Brain())
    s.open()
    i = s.read_identification()
    assert i.part_number == "022906032KR" and i.component_line == "R32-DQ-LEV2 G 1098"
    assert i.coding_text == "0000178" and i.shop_line == "WSC 01279 785 00200"
    assert ecu.requests[0] == h("10 89") and ecu.session == 0x89
    assert isinstance(s.identity, KwpIdentity)
    s.close()


def test_preset_brains_serve_the_scans_long_codings():
    expected = {
        ("golf-tdi-2012", 0x19): GOLF_GATEWAY_CODING.hex().upper(),       # 350002
        ("golf-tdi-2012", 0x03): GOLF_ABS_CODING.hex().upper(),           # 114B400C49240000880F02EA92200042B70000
        ("golf-tdi-2012", 0x56): GOLF_RADIO_CODING.hex().upper(),         # 01000400040005
        ("golf-tdi-2012", 0x09): BCM_LONG_CODING_PLACEHOLDER.hex().upper(),
        ("r32-2008", 0x09): BCM_LONG_CODING_PLACEHOLDER.hex().upper(),
        ("r32-2008", 0x19): "ED831F075003020000",
    }
    assert GOLF_GATEWAY_CODING.hex().upper() == "350002" and GOLF_RADIO_CODING.hex().upper() == "01000400040005"
    assert len(BCM_LONG_CODING_PLACEHOLDER) == 30
    for preset, specs in (("golf-tdi-2012", GOLF_TDI_KWP_MODULES), ("r32-2008", R32_KWP_MODULES)):
        for spec in specs:
            s, ecu, link = session_for(spec.brain())
            coding = s.read_coding()
            want = expected.get((preset, spec.address_word))
            if want is not None:
                assert coding["coding_type"] == "long coding", (preset, spec.label)
                assert coding["coding"] == want and coding["long_coding_parsed"], (preset, spec.label)
                assert h("1A 9A") in link.sent
            else:
                assert coding["coding_type"] != "long coding", (preset, spec.label)
    gw = session_for(GOLF_TDI_KWP_MODULES[4].brain())[0].read_identification(with_hardware_number=True)
    assert gw.part_number == "7N0907530H" and gw.hardware_number == "1K0907951"
    with pytest.raises(ValueError):
        BodyBrain("x", "1K0", "X", coding=1, long_coding=b"\x01")


def test_kwp_fault_dataclass_properties():
    f = KwpFault(0x4065, 0x68, "P0101", "desc", 8, "Implausible Signal", True, False, False, h("40 65 68"))
    assert f.factory_number == "16485" and f.vag6 == "000257" and f.text == "desc" and not f.is_factory_only
    assert f.vcds_lines()[2] == "Fault Status: 01101000"


# ----------------------------------------------------------------- optional: over TP 2.0

def test_r32_preset_over_tp20_through_the_simulated_vehicle():
    pytest.importorskip("vagtune.transport.tp20")
    from vagtune.transport.context import TransportContext
    from vagtune.transport.fakebus import reset_default_vehicle
    reset_default_vehicle()
    try:
        with TransportContext("fake", vehicle_preset="r32-2008") as ctx:
            names = ctx.vehicle.node_names()
            assert "kwp-01-engine" in names and "kwp-19-gateway" in names and "kwp-22-awd" in names
            ch = ctx.tp20_channel(0x01)
            ch.connect()
            assert ch.tx_id == 0x740
            client = KwpClient(ch, KwpTiming(p2=2.0, p2_star=3.0))
            s = VagKwpSession(client, module_name="engine")
            s.open()
            i = s.read_identification()             # exercises the 7F 1A 78 preamble over TP 2.0
            assert i.part_number == "022906032KR" and i.shop_line == "WSC 01279 785 00200"
            assert [f.vag5 for f in s.read_dtcs()] == ["16485", "00668"]
            assert s.read_group(2)[0].text == "680 rpm"
            assert s.capability_query().supports(0x0103)
            client.close()
            gw = ctx.tp20_channel(0x1F)
            gw.connect()
            g = VagKwpSession(KwpClient(gw, KwpTiming(p2=2.0)))
            g.open()
            assert len(g.gateway_installation_list().usable) == 21
            gw.close()
    finally:
        reset_default_vehicle()


def test_golf_preset_uds_hvac_traffic_does_not_disturb_an_open_abs_kwp_channel():
    """The regression behind the tester-TX id choice: with a UDS HVAC on the verified
    0x746 -> 0x7B0 ids, UDS reads must not break the open KWP channel to the ABS and
    vice versa (the ABS used to grant the tester 0x7B0)."""
    pytest.importorskip("vagtune.transport.tp20")
    from vagtune.transport.context import TransportContext
    from vagtune.transport.fake import SimulatedEcu
    from vagtune.transport.fakebus import UdsNode, reset_default_vehicle
    from vagtune.uds.client import UdsClient
    reset_default_vehicle()
    try:
        with TransportContext("fake", vehicle_preset="golf-tdi-2012") as ctx:
            vehicle = ctx.vehicle
            if not any(getattr(n, "response_id", None) == 0x7B0 for n in vehicle.nodes):
                hvac = SimulatedEcu()
                hvac.identifiers[0xF187] = b"7N0907426AN"
                vehicle.add_node(UdsNode(vehicle.bus, hvac, request_id=0x746, response_id=0x7B0, name="test-hvac"))
            abs_node = vehicle.node("kwp-03-abs")
            assert abs_node.tester_tx_id not in (0x746, 0x7B0)
            ch = ctx.tp20_channel(0x03)
            ch.connect()
            assert ch.tx_id == abs_node.tester_tx_id
            abs_ = VagKwpSession(KwpClient(ch, KwpTiming(p2=2.0, p2_star=3.0)), module_name="abs")
            abs_.open()
            assert abs_.read_identification().part_number == "1K0907379BJ"
            uds = UdsClient(ctx.isotp_link(0x746, 0x7B0))
            for _ in range(5):
                assert uds.read_data_by_identifier(0xF187) == b"7N0907426AN"
                assert abs_.read_identification().part_number == "1K0907379BJ"
                assert abs_.read_coding()["coding"] == GOLF_ABS_CODING.hex().upper()
            assert abs_node.responder.stats.get("sequence_errors", 0) == 0
            abs_.close()
    finally:
        reset_default_vehicle()
