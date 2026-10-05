"""
Calibration layer tests: image guardrails, scaled map read/write, definition load,
and a full round trip reading the demo image out of the simulated ECU and decoding a
map with the example definition.
"""

from __future__ import annotations

import json
import os

import pytest

from vagtune.calibration.definition import CalibrationDefinition, compute_checksum
from vagtune.calibration.image import ChecksumRegion, FlashImage
from vagtune.calibration.maps import Axis, Map, Scaling, ScalarValue
from vagtune.transport.fake import make_fake_pair
from vagtune.uds.client import UdsClient
from vagtune.vag.sa2 import make_seed_key_fn

DEF_PATH = os.path.join(os.path.dirname(__file__), "..", "definitions", "simos18.1.example.json")


def test_scaling_roundtrip():
    s = Scaling(dtype="u16", factor=0.1, offset=0.0, endian="big", unit="kPa")
    raw = s.phys_to_raw(250.0)        # 250 kPa / 0.1 = 2500
    assert raw == 2500
    assert s.raw_to_phys(raw) == pytest.approx(250.0)
    assert s.unpack(s.pack(raw)) == raw


def test_scaling_clamps_to_storage_range():
    s = Scaling(dtype="u8", factor=1.0)
    assert s.phys_to_raw(9999) == 0xFF
    assert s.phys_to_raw(-50) == 0


def test_image_write_and_diff():
    img = FlashImage(bytes(32), base_address=0x1000)
    assert not img.is_modified
    img.write_at_address(0x1004, b"\xDE\xAD")
    assert img.is_modified
    assert img.read_at_address(0x1004, 2) == b"\xDE\xAD"
    changes = img.diff()
    assert (4, 0x00, 0xDE) in changes
    img.reset()
    assert not img.is_modified


def test_image_address_bounds():
    img = FlashImage(bytes(16), base_address=0x8000)
    with pytest.raises(IndexError):
        img.read_at_address(0x9000, 1)


def test_scalar_read_write():
    img = FlashImage(bytes(0x200))
    scalar = ScalarValue("rev_limit", 0x100, Scaling(dtype="u16", factor=1.0, unit="rpm"))
    scalar.write(img, 7200)
    assert scalar.read(img) == pytest.approx(7200)


def test_map_read_write_and_scale():
    img = FlashImage(bytes(0x600))
    boost = Map("boost", 0x400, rows=4, cols=4,
                scaling=Scaling(dtype="u16", factor=0.1, unit="kPa"))
    # seed a known table
    table = [[200.0 + 10 * (r * 4 + c) for c in range(4)] for r in range(4)]
    boost.write(img, table)
    read_back = boost.read(img)
    for r in range(4):
        for c in range(4):
            assert read_back[r][c] == pytest.approx(table[r][c])
    # +10% with a ceiling
    boost.scale_all(img, 1.10, clamp_phys=250.0)
    scaled = boost.read(img)
    assert scaled[0][0] == pytest.approx(220.0)
    assert all(cell <= 250.0 + 1e-6 for row in scaled for cell in row)


def test_definition_loads():
    d = CalibrationDefinition.from_file(DEF_PATH)
    assert d.profile == "simos18.1"
    assert "boost_target" in d.list_maps()
    boost = d.get_map("boost_target")
    assert boost.rows == 8 and boost.cols == 8
    assert boost.x_axis is not None and boost.x_axis.name == "rpm_axis"


def test_checksum_algorithms():
    data = bytes(range(256))
    assert compute_checksum("crc32", data) == compute_checksum("crc32", data)
    assert 0 <= compute_checksum("sum16", data) <= 0xFFFF
    assert 0 <= compute_checksum("sum32", data) <= 0xFFFFFFFF
    with pytest.raises(ValueError):
        compute_checksum("bogus", data)


def test_end_to_end_read_cal_and_decode():
    # Read the demo image out of the simulated ECU, then decode a map with the def.
    link, ecu = make_fake_pair(0x7E0, 0x7E8)
    client = UdsClient(link)
    client.security_access(0x11, make_seed_key_fn(ecu.sa2_script))
    # Read the first 0x600 bytes of the CAL block at its real SIMOS18.1 address.
    raw = client.upload(ecu.cal_base, 0x600)
    assert raw == ecu.cal_memory[:0x600]

    d = CalibrationDefinition.from_file(DEF_PATH)
    image = d.open_image(raw, name="sim")
    boost = d.get_map("boost_target")
    table = boost.read(image)          # must not raise / addresses in range
    assert len(table) == 8 and len(table[0]) == 8
    text = boost.as_text(image)
    assert "boost_target" in text
