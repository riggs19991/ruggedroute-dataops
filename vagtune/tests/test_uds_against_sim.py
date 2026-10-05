"""
End-to-end UDS tests against the simulated ECU.

These drive the real UdsClient over the FakeIsoTpLink, so the request/response
framing, NRC handling, security-access seed/key, and upload loop are all exercised
exactly as they would be against hardware.
"""

from __future__ import annotations

import pytest

from vagtune.transport.fake import make_fake_pair
from vagtune.uds.client import UdsClient
from vagtune.uds.exceptions import NegativeResponse
from vagtune.vag.ecu import VagEcuSession
from vagtune.vag.sa2 import Sa2Interpreter, make_seed_key_fn


def _session():
    link, ecu = make_fake_pair(0x7E0, 0x7E8)
    client = UdsClient(link)
    return client, ecu


def test_session_control():
    client, ecu = _session()
    client.diagnostic_session_control(0x03)
    assert ecu.session == 0x03


def test_read_vin():
    client, ecu = _session()
    vin = client.read_data_by_identifier(0xF190)
    assert vin == b"WVWZZZAUZLW000001"


def test_identity_block():
    client, ecu = _session()
    session = VagEcuSession(client)
    identity = session.read_identity()
    assert identity.vin == "WVWZZZAUZLW000001"
    assert identity.part_number == "8V0906259H"
    assert "TFSI" in (identity.system_name or "")


def test_read_dtcs():
    client, ecu = _session()
    session = VagEcuSession(client)
    dtcs = session.read_dtcs(0xFF)
    assert len(dtcs) == 2
    codes = {d.code for d in dtcs}
    # 0x011200 -> P0112, 0x056100 -> U... per the decode rules
    assert "P0112" in codes


def test_clear_dtcs():
    client, ecu = _session()
    session = VagEcuSession(client)
    session.clear_dtcs()
    assert ecu.dtcs == []
    assert session.read_dtcs(0xFF) == []


def test_security_access_success():
    client, ecu = _session()
    seed_key = make_seed_key_fn(ecu.sa2_script)
    client.security_access(0x11, seed_key)
    assert ecu.security_unlocked is True


def test_security_access_wrong_key_rejected():
    client, ecu = _session()

    def bad_key(level, seed):
        return b"\x00\x00\x00\x00"

    with pytest.raises(NegativeResponse) as exc:
        client.security_access(0x11, bad_key)
    assert exc.value.nrc == 0x35  # invalidKey


def test_upload_requires_security():
    client, ecu = _session()
    with pytest.raises(NegativeResponse) as exc:
        client.upload(0x0000, 256)
    assert exc.value.nrc == 0x33  # securityAccessDenied


def test_upload_after_unlock_matches_memory():
    client, ecu = _session()
    client.security_access(0x11, make_seed_key_fn(ecu.sa2_script))
    data = client.upload(0x0000, 1024)
    assert data == ecu.memory[:1024]


def test_upload_full_image_multiblock():
    client, ecu = _session()
    client.security_access(0x11, make_seed_key_fn(ecu.sa2_script))
    seen = []
    data = client.upload(0x0000, 4096, progress=lambda d, t: seen.append((d, t)))
    assert data == ecu.memory[:4096]
    assert seen and seen[-1][0] == 4096


def test_read_memory_by_address():
    client, ecu = _session()
    data = client.read_memory_by_address(0x0010, 8)
    assert data == ecu.memory[0x10:0x18]


def test_unknown_did_raises_out_of_range():
    client, ecu = _session()
    with pytest.raises(NegativeResponse) as exc:
        client.read_data_by_identifier(0xABCD)
    assert exc.value.nrc == 0x31
