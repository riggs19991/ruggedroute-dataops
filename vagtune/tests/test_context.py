"""
TransportContext tests.

The ``fake`` kind is exercised end to end (identify engine + gateway, raw endpoint,
link cleanup); the hardware kinds are checked for clean failure on a machine without
hardware; tp20_channel reports the missing TP 2.0 module as a TransportError.
"""

from __future__ import annotations

import platform
import threading
import time

import pytest

from vagtune.transport import TransportContext, make_isotp_link
from vagtune.transport.base import CanFrame, TransportError, TransportNotOpen
from vagtune.transport.fakebus import reset_default_vehicle
from vagtune.transport.isotp import SoftwareIsoTpLink
from vagtune.uds.client import UdsClient
from vagtune.vag.ecu import VagEcuSession


@pytest.fixture(autouse=True)
def _fresh_default_vehicle():
    reset_default_vehicle()
    yield
    reset_default_vehicle()


def test_fake_kind_identify_engine_and_gateway():
    with TransportContext("fake") as ctx:
        assert ctx.kind == "fake"
        assert ctx.router is not None and ctx.supports_raw_frames
        assert ctx.vehicle.preset == "demo" and ctx.vehicle.started
        assert "fake" in ctx.describe()

        engine = VagEcuSession(UdsClient(ctx.isotp_link(0x7E0, 0x7E8)))
        gateway = VagEcuSession(UdsClient(ctx.isotp_link(0x710, 0x77A)))
        try:
            engine.enter_extended_session()
            gateway.enter_extended_session()
            e = engine.read_identity()
            g = gateway.read_identity()
            assert e.part_number == "8V0906259H" and e.system_name == "R4 2.0L TFSI"
            assert g.part_number == "7N0907530C" and g.system_name == "J533 Gateway"
            assert e.vin == g.vin == "WVWZZZAUZLW000001"
            assert engine.detect_profile(e) is None      # demo F197 names no known family
            assert gateway.detect_profile(g) is None
            assert [d.code for d in engine.read_dtcs()] == ["P0112", "P0561"]
            assert gateway.read_dtcs() == []
        finally:
            engine.client.close()
            gateway.client.close()
        # closing the UDS clients unsubscribed their endpoints
        assert ctx.router.endpoints == []
    assert ctx.router.is_closed
    with pytest.raises(TransportError):
        ctx.isotp_link(0x7E0, 0x7E8)


def test_fake_kind_vehicle_preset_selection():
    with TransportContext("fake", vehicle_preset="r32-2008") as ctx:
        assert ctx.vehicle.preset == "r32-2008"
    with TransportContext("fake", vehicle_preset="demo") as ctx:
        assert ctx.vehicle.preset == "demo"
    with pytest.raises(KeyError):
        TransportContext("fake", vehicle_preset="not-a-car")


def test_isotp_link_extra_rx_ids_and_raw_endpoint():
    with TransportContext("fake") as ctx:
        link = ctx.isotp_link(0x7DF, 0x7E8, extra_rx_ids=[0x77A, 0x77D])
        assert isinstance(link, SoftwareIsoTpLink)
        assert link.accept_ids == frozenset({0x7E8, 0x77A, 0x77D})
        sniffer = ctx.raw_endpoint(None)
        link.send(bytes([0x3E, 0x00]))
        seen = set()
        for _ in range(3):
            p = link.recv(0.5)
            assert p == b"\x7E\x00"
            seen.add(link.last_rx_id)
        assert seen == {0x7E8, 0x77A, 0x77D}
        frames = []
        while (f := sniffer.recv(0.05)) is not None:
            frames.append(f)
        ids = {f.arbitration_id for f in frames}
        # the sniffer saw the responses (the tester's own TX is not echoed by the bus)
        assert {0x7E8, 0x77A, 0x77D} <= ids
        link.close()
        sniffer.close()


def test_tp20_channel_builds_a_real_channel():
    """tp20_channel hands out a Tp20Channel on the fake router (connect is lazy here,
    so no simulated TP 2.0 module is needed for the construction to succeed)."""
    from vagtune.transport.tp20 import Tp20Channel
    with TransportContext("fake") as ctx:
        ch = ctx.tp20_channel(0x01, auto_connect=False)
        try:
            assert isinstance(ch, Tp20Channel)
            assert ch.logical_address == 0x01
            assert ch.connected is False
        finally:
            ch.close()


def test_unknown_kind_rejected():
    with pytest.raises(TransportError):
        TransportContext("bluetooth")


@pytest.mark.skipif(platform.system() == "Windows", reason="raw-DLL path is exercised on Windows only")
def test_j2534_fw_on_non_windows_raises_transport_error(tmp_path, monkeypatch):
    monkeypatch.delenv("VAGTUNE_J2534_DLL", raising=False)
    # Without any DLL discoverable the error is "no DLL"; with a path it is "Windows only".
    with pytest.raises(TransportError):
        TransportContext("j2534-fw")
    with pytest.raises(TransportError) as exc:
        TransportContext("j2534-fw", dll_path=str(tmp_path / "op20pt32.dll"))
    assert "Windows" in str(exc.value) or "not found" in str(exc.value)
    with pytest.raises(TransportError):
        TransportContext("j2534", dll_path=str(tmp_path / "op20pt32.dll"))


def test_can_kind_without_python_can_or_interface_fails_cleanly():
    # Either python-can is missing (TransportError) or the interface cannot be opened
    # (python-can raises its own error). Both must surface, never hang.
    pytest.importorskip("can", reason="python-can not installed; TransportError path covered below")
    with pytest.raises(Exception):
        TransportContext("can", can_interface="socketcan", can_channel="vcan-does-not-exist")


def test_can_kind_transport_error_when_python_can_missing(monkeypatch):
    import vagtune.transport.socketcan as sc
    monkeypatch.setattr(sc, "_HAVE_CAN", False)
    with pytest.raises(TransportError):
        TransportContext("can")


def test_make_isotp_link_fake_uses_real_framing_and_releases_hardware():
    link = make_isotp_link("fake", tx_id=0x7E0, rx_id=0x7E8)
    assert isinstance(link, SoftwareIsoTpLink)
    ctx = link.context
    client = UdsClient(link)
    data = client.read_memory_by_address(0x0000, 50)    # multi-frame response over the bus
    assert data == bytes(range(50))
    client.close()
    assert ctx.router.is_closed
    with pytest.raises(TransportError):
        make_isotp_link("nope", 1, 2)


def test_make_isotp_link_other_module_and_preset():
    link = make_isotp_link("fake", tx_id=0x713, rx_id=0x77D, vehicle_preset="demo")
    try:
        assert UdsClient(link).read_data_by_identifier(0xF197) == b"ESP MK60EC1"
    finally:
        link.close()


def test_context_close_wakes_blocked_raw_endpoint_consumer():
    ctx = TransportContext("fake")
    sniffer = ctx.raw_endpoint(None, name="sniffer")
    result = {}

    def consumer():
        t0 = time.monotonic()
        try:
            result["frame"] = sniffer.recv(5.0)        # like `sniff --duration 5`
        except TransportNotOpen as exc:
            result["error"] = str(exc)
        result["elapsed"] = time.monotonic() - t0

    t = threading.Thread(target=consumer, daemon=True)
    t.start()
    time.sleep(0.1)
    ctx.close()
    t.join(timeout=1.0)
    assert not t.is_alive()
    assert "error" in result and result["elapsed"] < 0.5


def test_functional_multi_frame_responses_from_several_modules():
    # ReadMemoryByAddress is answered multi-frame by every demo module; a functional
    # link must collect all three, each flow-controlled on its physical request id.
    with TransportContext("fake") as ctx:
        link = ctx.isotp_link(0x7DF, 0x7E8, extra_rx_ids=[0x77A, 0x77D])
        assert link.flow_control_ids == {0x7E8: 0x7E0, 0x77A: 0x710, 0x77D: 0x713}
        link.send(bytes([0x23, 0x22, 0, 0, 0, 40]))      # RMBA, fits one frame (functional rule)
        got = {}
        deadline = time.monotonic() + 2.0
        while len(got) < 3 and time.monotonic() < deadline:
            p = link.recv(0.3)
            if p is not None:
                got[link.last_rx_id] = p
        assert set(got) == {0x7E8, 0x77A, 0x77D}
        assert all(p == b"\x63" + bytes(range(40)) for p in got.values())
        link.close()
