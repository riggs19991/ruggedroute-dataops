"""vag.measuring_blocks: every formula id, the named alternates, the variable-length
fields, the real 26-byte replies quoted in the research sheet, and the N/N+128 rule."""

from __future__ import annotations

import logging
import math

import pytest

from vagtune.vag import dtc as V
from vagtune.vag import measuring_blocks as M

h = bytes.fromhex


@pytest.fixture(autouse=True)
def _fresh_warnings():
    V._reset_unverified_warnings()
    yield
    V._reset_unverified_warnings()


def _warnings(caplog, needle: str):
    return [r.getMessage() for r in caplog.records if "UNVERIFIED" in r.getMessage() and needle in r.getMessage()]


# ----------------------------------------------------------------- table coverage

def test_every_formula_id_01_to_b5_is_in_the_table():
    assert set(M.FORMULAS) == set(range(0x01, 0xB6))
    assert M.LAST_VALID_FORMULA == 0xB5
    assert all(f.id == fid for fid, f in M.FORMULAS.items())


def test_every_formula_id_decodes_a_numeric_vector_without_error(caplog):
    caplog.set_level(logging.WARNING)
    for fid, f in M.FORMULAS.items():
        for a, b in ((0, 0), (100, 200), (255, 255), (1, 128), (0x80, 0x7F)):
            mv = M.decode_field(fid, a, b)
            assert mv.formula_id == fid and mv.raw == bytes([fid, a, b])
            if f.kind == M.KIND_UNDECODABLE:
                assert mv.undecodable and mv.value == ((a << 8) | b)
            elif f.kind in (M.KIND_LENGTH_TEXT, M.KIND_LENGTH_HEX, M.KIND_REST_TEXT, M.KIND_VARIABLE_UNITS):
                # these are only meaningful through decode_group; decode_field keeps them raw
                assert mv.undecodable
            elif f.kind in (M.KIND_TEXT, M.KIND_TIME, M.KIND_DATE):
                assert isinstance(mv.value, str) and mv.text == mv.value
            elif f.kind == M.KIND_BITS:
                assert isinstance(mv.value, str)
            else:
                assert isinstance(mv.value, (int, float)) and not (isinstance(mv.value, float) and math.isnan(mv.value))
                assert not mv.unverified and mv.variant == "consensus"
    assert not _warnings(caplog, "formula")      # consensus rows never warn


EXACT = [
    # (id, A, B, expected) - consensus column of the registry table
    (0x01, 0xC8, 0x00, 0.0), (0x01, 0x44, 0x32, 680.0), (0x01, 0x73, 0x00, 0.0),
    (0x02, 100, 250, 50.0), (0x03, 100, 250, 50.0),
    (0x04, 100, 137, 10.0), (0x04, 100, 117, -10.0),
    (0x05, 10, 190, 90.0), (0x05, 0x09, 0x80, 25.2),
    (0x06, 55, 228, 12.54), (0x07, 100, 50, 50.0), (0x08, 10, 10, 10.0),
    (0x09, 100, 177, 100.0), (0x0B, 100, 138, 1.1), (0x0C, 100, 100, 10.0), (0x0D, 100, 227, 10.0),
    (0x0E, 27, 200, 27.0), (0x0F, 100, 100, 100.0),
    (0x12, 0xFA, 0x1C, 280.0), (0x12, 250, 101, 1010.0), (0x13, 100, 100, 100.0),
    (0x14, 0x80, 0x83, 3.0), (0x14, 0x80, 0x7D, -3.0),
    (0x15, 100, 5, 0.5), (0x16, 255, 13, 3.315), (0x17, 128, 128, 64.0), (0x18, 10, 191, 1.91),
    (0x19, 0x46, 0x03, (768 + 70) / 180), (0x1A, 0, 35, 35), (0x1B, 100, 138, 10.0), (0x1C, 5, 20, 15),
    (0x1E, 12, 24, 24.0), (0x1F, 10, 128, 0.5), (0x20, 1, 255, -1), (0x20, 1, 128, 128),
    (0x21, 0x85, 0x85, 100.0), (0x21, 0, 5, 500), (0x21, 250, 12, 4.8),
    (0x22, 100, 138, 10.0), (0x23, 100, 50, 50.0), (0x24, 1, 1, 2570), (0x25, 0x04, 0x1D, 0x041D),
    (0x26, 100, 138, 1.0), (0x27, 128, 128, 64.0), (0x28, 16, 0, 8.0), (0x29, 1, 1, 256),
    (0x2A, 16, 0, 8.0), (0x2B, 1, 1, 25.6), (0x2D, 10, 10, 10.0),
    (0x2E, 128, 0, 0.0), (0x2F, 100, 129, 100), (0x30, 1, 1, 256), (0x31, 40, 100, 100.0),
    (0x32, 100, 138, 10.0), (0x32, 0, 138, 100000.0), (0x33, 255, 129, 1.0), (0x34, 50, 100, 50.0),
    (0x35, 0, 129, 256 / 180), (0x36, 0x14, 0xA9, 5289), (0x37, 200, 1, 1.0),
    (0x38, 1, 0, 256), (0x39, 1, 0, 65792), (0x3A, 0, 255, -1.023), (0x3B, 0x80, 0, 1.0),
    (0x3C, 1, 0, 2.56), (0x3D, 2, 138, 5.0), (0x3D, 0, 138, 10), (0x3E, 1, 1, 0.256),
    (0x40, 1, 2, 3), (0x41, 100, 227, 100.0), (0x42, 2, 256 // 2, 0.5), (0x43, 0xFF, 0xFF, -2.5),
    (0x44, 0x00, 0x0A, 1.358), (0x45, 0, 2, 0.651), (0x46, 0, 10, 1.92), (0x47, 2, 3, 6),
    (0x48, 255, 0, 255 * 255 / 4080), (0x49, 10, 10, 1.0), (0x4A, 10, 10, 10.0), (0x4B, 0x40, 0x65, 0x4065),
    (0x4C, 1, 1, 256), (0x4D, 16, 0, 1.0), (0x4E, 0, 255, -1.819), (0x4F, 7, 9, 9), (0x50, 1, 0, 2.56),
    (0x51, 0, 100, 4.375), (0x52, 0, 100, 0.981), (0x53, 0x75, 0x30, 300.0), (0x54, 0, 10, 0.973),
    (0x55, 0, 1000 & 0xFF, 232 * 0.002865), (0x56, 10, 10, 10.0), (0x57, 10, 138, 10.0), (0x58, 10, 10, 1.0),
    (0x59, 1, 0, 256), (0x5A, 10, 10, 10.0), (0x5B, 10, 138, 10.0), (0x5C, 50, 11, 550), (0x5D, 100, 138, 1.0),
    (0x5E, 160, 255, 2032.0), (0x60, 0x64, 0x65, 1010.0), (0x61, 10, 20, 50), (0x62, 10, 10, 10.0),
    (0x63, 0xFF, 0xFE, -2), (0x64, 10, 10, 10.0), (0x65, 100, 10, 1.0), (0x66, 10, 10, 10.0),
    (0x67, 1, 20, 2.0), (0x68, 5, 178, 50.0), (0x69, 100, 138, 10.0), (0x6A, 10, 138, 10.0),
    (0x6F, 1, 2, 0x6F0102), (0x70, 100, 138, 1.0), (0x71, 0x0A, 0x80, 0.0), (0x72, 10, 138, 100),
    (0x73, 0x00, 0x05, 5), (0x74, 0xFF, 0xFF, -1), (0x75, 100, 74, 10.0), (0x77, 10, 10, 1.0),
    (0x78, 1, 1, 1.41), (0x79, 2, 1, 129.0), (0x7A, 0, 0x80, 0.0), (0x7B, 1, 2, 0x0102),
    (0x7C, 10, 10, 10.0), (0x7D, 10, 3, 7), (0x7E, 3, 0x39, 17.1), (0x80, 10, 10, 100), (0x81, 128, 128, 64.0),
    (0x82, 128, 20, 1.0), (0x83, 2, 60, 30.0), (0x84, 2, 60, 60.0), (0x85, 128, 128, 64.0), (0x86, 10, 10, 100),
    (0x87, 3, 3, 9), (0x89, 10, 10, 1.0), (0x8A, 100, 10, 1.0), (0x8F, 100, 138, 10.0), (0x90, 10, 10, 1.0),
    (0x91, 10, 10, 1.0), (0x92, 100, 138, 1.1), (0x94, 4, 138, 10.0), (0x95, 10, 190, 90.0),
    (0x96, 0x46, 0x03, (768 + 70) / 180), (0x97, 100, 138, 10.0), (0x98, 40, 100, 100.0), (0x99, 255, 129, 1.0),
    (0x9A, 3, 3, 9), (0x9B, 100, 100, 10.0), (0x9C, 1, 0, 256), (0x9D, 0xFF, 0xFF, -1), (0x9E, 1, 0, 2.56),
    (0x9F, 0x08, 0x86, 180.0), (0xA2, 1, 1, 0.448), (0xA4, 1, 50, 50), (0xA4, 1, 150, 50), (0xA4, 1, 250, 250),
    (0xA5, 0, 0x80, 0), (0xA6, 0, 2, 5.0), (0xA7, 10, 10, 0.1), (0xA8, 1, 0, 2.56), (0xA9, 2, 2, 204),
    (0xAA, 128, 20, 1.0), (0xAB, 128, 20, 1.0), (0xAC, 2, 3, 6), (0xAD, 10, 10, 10.0), (0xAE, 10, 10, 1.0),
    (0xAF, 200, 1, 1.0), (0xB0, 10, 10, 10.0), (0xB1, 129, 1, 257), (0xB2, 129, 0, 256 * 6 / 51),
    (0xB3, 1, 0, 2560), (0xB4, 128, 128, 64.0), (0xB5, 10, 10, 0.1),
]


@pytest.mark.parametrize("fid,a,b,expected", EXACT, ids=[f"{t[0]:02X}-{t[1]}-{t[2]}" for t in EXACT])
def test_exact_numeric_vectors(fid, a, b, expected):
    mv = M.decode_field(fid, a, b)
    assert mv.value == pytest.approx(expected, abs=1e-6), mv


def test_text_time_date_and_bit_formulas():
    assert M.decode_field(0x0A, 0, 0).text == "COLD" and M.decode_field(0x0A, 0, 1).text == "WARM"
    assert M.decode_field(0x11, 0x41, 0x42).text == "AB" and M.decode_field(0x8E, 0x41, 0x42).text == "AB"
    assert M.decode_field(0x1D, 10, 5).text == "Map 1" and M.decode_field(0x1D, 5, 10).text == "Map 2"
    assert M.decode_field(0x10, 0xFF, 0x05).value == "00000101" and M.decode_field(0x10, 0x0F, 0xF5).value == "00000101"
    assert M.decode_field(0x88, 0xFF, 0x02).value == "00000010"
    assert M.decode_field(0xA1, 0x05, 0x80).value == "00000101 10000000"
    assert M.decode_field(0x2C, 7, 5).text == "7:05" and M.decode_field(0xA3, 12, 30).text == "12:30"
    assert M.decode_field(0x6B, 0xAB, 0x01).text == "AB01"
    # 0x7F: year = 2000 + (B & 0x7F), month = (A&7)<<1 | B>>7, day = (A & 0xF8) >> 3
    a = (12 << 3) | (5 >> 1)          # day 12, month 5 -> A bits 2..0 = 2, B bit 7 = 1
    b = 0x80 | 7
    assert M.decode_field(0x7F, a, b).text == "2007.05.12"
    assert M.decode_field(0x25, 0x02, 0x7A).text == "text #634 (label file)"


def test_named_alternates_exist_for_every_disputed_id_and_warn_once(caplog):
    caplog.set_level(logging.WARNING)
    assert M.DISPUTED_IDS == {0x04, 0x08, 0x0E, 0x12, 0x14, 0x19, 0x21, 0x27, 0x2D, 0x2E, 0x51, 0x5E}
    expected = {
        (0x04, "kl-btdc-positive", 100, 137): -10.0,
        (0x08, "vb-raw16", 0x12, 0x34): 0x1234,
        (0x0E, "openhaldex", 27, 200): 27.0,
        (0x0E, "openhaldex", 27, 150): 13.5,
        (0x12, "pyvcds-x25-bug", 2, 3): 150,
        (0x14, "vb-py", 0x80, 0x83): 128 * 131 / 128 - 1,
        (0x14, "sc-fitted", 0x80, 0x83): 3.84,
        (0x19, "pyvcds", 50, 3): 6.0,
        (0x19, "blafusel", 0x46, 0x03): 3 * 1.421 + 70 / 182,
        (0x21, "openhaldex", 100, 40): 40.0,
        (0x27, "kl-255", 255, 1): 1.0,
        (0x2D, "blafusel", 10, 10): 0.1,
        (0x2E, "blafusel", 16, 200): (16 * 200 - 3200) * 0.0027,
        (0x51, "vag-blocks", 1, 0): 112.0,
        (0x51, "pyvcds", 1, 0): 11.2,
        (0x5E, "vag-blocks", 160, 255): 160 * (255 / 50 - 1),
    }
    seen = set()
    for (fid, name, a, b), value in expected.items():
        mv = M.decode_field(fid, a, b, variant=name)
        assert mv.value == pytest.approx(value, abs=1e-6), (fid, name, mv)
        assert mv.unverified and mv.variant == name and M.formula(fid, name).unverified
        seen.add((fid, name))
    assert seen == {(fid, name) for fid, d in M.FORMULA_VARIANTS.items() for name in d}
    for fid, d in M.FORMULA_VARIANTS.items():
        for name in d:
            M.decode_field(fid, 1, 1, variant=name)
    assert len(_warnings(caplog, "formula 0x")) == len(seen)       # once per variant
    assert M.formula(0x01) is M.FORMULAS[0x01] and M.formula(0x01, "consensus") is M.FORMULAS[0x01]
    with pytest.raises(KeyError):
        M.formula(0x01, "nope")
    assert M.formula(0xC0) is None


# ----------------------------------------------------------------- real replies

def test_nefmoto_group_002_reply_26_bytes():
    data = h("01 C8 00 21 85 85 16 FF 00 19 00 00 25 00 00 25 04 1D 25 02 7A 25 00 00")
    vals = M.decode_group(data, group=2)
    assert len(vals) == 8
    assert [v.formula_id for v in vals] == [0x01, 0x21, 0x16, 0x19, 0x25, 0x25, 0x25, 0x25]
    assert vals[0].value == 0.0 and vals[0].unit == "rpm" and vals[0].group == 2 and vals[0].field == 1
    assert vals[1].value == pytest.approx(100.0) and vals[1].unit == "%"
    assert vals[2].value == pytest.approx(0.0) and vals[2].unit == "ms"
    assert vals[3].value == pytest.approx(0.0) and vals[3].unit == "g/s"
    assert vals[5].value == 0x041D and vals[6].value == 0x027A
    assert all(v.group is None and v.field == i + 5 for i, v in enumerate(vals[4:]))
    assert "second half" in vals[4].note


def test_basano_group_115_reply_boost_fields():
    data = h("01 C8 00 21 85 85 12 FA 1C 60 64 65 36 14 A9 36 0D 9B 36 10 E9 36 0E C3")
    vals = M.decode_group(data, group=0x73)
    assert vals[2].value == pytest.approx(280.0) and vals[2].unit == "mbar"
    assert vals[3].value == pytest.approx(1010.0) and vals[3].unit == "mbar"
    assert [v.value for v in vals[4:]] == [5289, 3483, 4329, 3779]


def test_nefmoto_group_113_and_seishuku_group_001_and_teensy_group_114():
    g71 = M.decode_group(h("01 C8 00 21 85 85 21 FF 13 12 7D CA 25 00 00 25 00 00 25 00 00 25 00 00"), group=0x71)
    assert g71[2].value == pytest.approx(100 * 0x13 / 0xFF) and g71[3].value == pytest.approx(0x7D * 0xCA * 0.04)
    g01 = M.decode_group(h("01 73 00 27 46 00 64 50 00 05 09 80 25 02 7A 25 00 00 25 00 00 25 00 00"), group=1)
    assert [v.formula_id for v in g01] == [0x01, 0x27, 0x64, 0x05, 0x25, 0x25, 0x25, 0x25]
    assert g01[0].value == 0.0 and g01[3].value == pytest.approx(9 * 28 * 0.1) and g01[3].unit == "°C"
    g72 = M.decode_group(h("08 0A FF 08 0A FF 71 0A 80 71 0A 80 68 0F 8F 7E 03 39 7E 03 39 25 00 00"), group=0x72)
    assert g72[0].value == pytest.approx(255.0) and g72[2].value == pytest.approx(0.0)
    assert g72[4].value == pytest.approx(15 * 15 * 0.2) and g72[5].value == pytest.approx(17.1)
    assert len(g72) == 8


# ----------------------------------------------------------------- variable-length fields

def test_length_prefixed_text_and_hex_fields():
    data = h("5F 03 41 42 43 76 02 DE AD 01 44 32")
    vals = M.decode_group(data, group=81)
    assert [v.formula_id for v in vals] == [0x5F, 0x76, 0x01]
    assert vals[0].value == "ABC" and vals[0].raw == h("5F 03 41 42 43")
    assert vals[1].value == h("DE AD") and vals[1].text == "de ad"
    assert vals[2].value == 680.0 and vals[2].field == 3
    cut = M.decode_group(h("5F 05 41 42"), group=81)
    assert len(cut) == 1 and cut[0].undecodable and cut[0].value == "AB"


def test_rest_of_message_text_and_truncated_trailer():
    vals = M.decode_group(h("01 44 32 3F 48 65 6C 6C 6F 20 20"), group=9)
    assert len(vals) == 2 and vals[1].value == "Hello" and vals[1].raw == h("3F 48 65 6C 6C 6F 20 20")
    vals = M.decode_group(h("01 44 32 05 0A"), group=9)
    assert len(vals) == 2 and vals[1].undecodable and vals[1].raw == h("05 0A")


def test_a0_variable_units_five_data_bytes():
    # NW=1, WORD_BC=300, D: dl=1, dh=1 -> 30.0; E=0x1D pressure
    vals = M.decode_group(h("A0 01 01 2C 11 1D 01 44 32"), group=5)
    assert len(vals) == 2 and vals[0].raw == h("A0 01 01 2C 11 1D")
    assert vals[0].value == pytest.approx(30.0) and vals[0].unit == "pressure"
    assert vals[1].value == 680.0
    v, unit, text = M.decode_a0(2, 0x00, 0x0A, 0x91, 0x23)       # sign bit + ignition angle -> BTDC, positive
    assert v == pytest.approx(2.0) and unit == "° ignition" and text.endswith("BTDC")
    v, unit, text = M.decode_a0(2, 0x00, 0x0A, 0x91, 0x41)       # sign bit, other unit -> negative, prefix k
    assert v == pytest.approx(-2.0) and unit == "kV"
    v, unit, _ = M.decode_a0(1, 0, 1, 0x01, 0xC3)
    assert unit == "uA"
    assert len(M.decode_group(h("A0 01 02"), group=5)) == 1 and M.decode_group(h("A0 01 02"), group=5)[0].undecodable


def test_table_mapped_and_unknown_ids_are_raw_but_walked():
    data = h("8B 10 20 8C 10 20 93 10 20 8D 00 02 00 11 22 6C 01 02 C0 03 04 01 44 32")
    vals = M.decode_group(data, group=7)
    assert [v.formula_id for v in vals] == [0x8B, 0x8C, 0x93, 0x8D, 0x00, 0x6C, 0xC0, 0x01]
    assert all(v.undecodable and v.unverified for v in vals[:-1])
    assert vals[0].value == 0x1020 and vals[0].raw == h("8B 10 20") and "17-byte table" in vals[0].label
    assert vals[4].label.startswith("not a formula")
    assert vals[6].label.endswith("not in the table")
    assert vals[7].value == 680.0 and vals[7].decoded
    assert M.UNDECODABLE_IDS == {0x00, 0x6C, 0x6D, 0x6E, 0x8B, 0x8C, 0x8D, 0x93}


# ----------------------------------------------------------------- N / N+128

def test_eight_field_reply_second_half_labelled_only_with_the_flag(caplog):
    caplog.set_level(logging.WARNING)
    data = h("01 44 32") * 8
    plain = M.decode_group(data, group=2)
    assert [v.group for v in plain] == [2, 2, 2, 2, None, None, None, None]
    assert [v.field for v in plain] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert not any(v.unverified for v in plain) and not _warnings(caplog, "N+128")
    flagged = M.decode_group(data, group=2, second_half_is_group_plus_128=True)
    assert [v.group for v in flagged] == [2, 2, 2, 2, 130, 130, 130, 130]
    assert [v.field for v in flagged] == [1, 2, 3, 4, 1, 2, 3, 4]
    assert all(v.unverified for v in flagged[4:]) and not any(v.unverified for v in flagged[:4])
    M.decode_group(data, group=3, second_half_is_group_plus_128=True)
    assert len(_warnings(caplog, "N+128")) == 1
    four = M.decode_group(h("01 44 32") * 4, group=2, second_half_is_group_plus_128=True)
    assert [v.group for v in four] == [2, 2, 2, 2]


def test_decode_group_variants_selection_and_str():
    vals = M.decode_group(h("08 12 34 08 12 34"), group=1, variants={0x08: "vb-raw16"})
    assert vals[0].value == 0x1234 and vals[0].unverified and "[unverified]" in str(vals[0])
    assert str(M.decode_group(h("01 44 32"), group=1)[0]) == "001.1 680 rpm"
    assert "[raw]" in str(M.decode_group(h("8B 01 02"), group=1)[0])
    assert M.format_group(vals).count("\n") == 1


# ----------------------------------------------------------------- misc

def test_obd_mirror_did_decoder_and_group_labels(caplog):
    caplog.set_level(logging.WARNING)
    dec = M.obd_mirror_did_decoder(0xF40C)
    assert dec is not None and dec(h("0C 80")) == 800.0
    assert M.obd_mirror_did_decoder(0xF190) is None
    assert M.obd_mirror_did_decoder(0xF4FF) is None
    assert M.group_label("me7-gasoline-standard", 2).fields[3] == "air mass [g/s]"
    assert M.group_label("edc17-cjaa", 11).fields[1].startswith("boost pressure specified")
    assert M.group_label("dq250-02e", 19).fields[0].startswith("control module temp")
    assert not _warnings(caplog, "group")
    row = M.group_label("haldex-gen2", 1)
    assert row is not None and not row.verified and len(_warnings(caplog, "group 001")) == 1
    assert M.group_label("me7-gasoline-standard", 999) is None
