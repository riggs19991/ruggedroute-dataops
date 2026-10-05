"""
Simulated vehicle tests: UdsNode behind real ISO-TP on a FakeCanBus.

Covers: two UdsClients on one router talking to two nodes concurrently from two
threads without crosstalk; multi-frame request *and* response through the ECU-side
ISO-TP; a functional 0x7DF request answered by every node that listens; handler
exception -> NRC 0x10; stop() joins promptly; presets, hooks and the default vehicle.
"""

from __future__ import annotations

import threading
import time

import pytest

from vagtune.transport.base import CanFrame
from vagtune.transport.fake import SimulatedEcu
from vagtune.transport.fakebus import (
    FakeCanBus,
    SimulatedNode,
    SimulatedVehicle,
    UdsNode,
    get_default_vehicle,
    reset_default_vehicle,
)
from vagtune.transport.isotp import SoftwareIsoTpLink
from vagtune.transport.router import CanRouter
from vagtune.uds.client import UdsClient, UdsTiming
from vagtune.uds.exceptions import NegativeResponse
from vagtune.vag.ecu import VagEcuSession
from vagtune.vag.sa2 import make_seed_key_fn


@pytest.fixture
def demo():
    vehicle = SimulatedVehicle("demo")
    vehicle.start()
    tester = vehicle.bus.attach("tester")
    router = CanRouter(tester, name="tester")
    yield vehicle, router
    router.close()
    vehicle.stop()


def _client(router, tx, rx, **kw):
    return UdsClient(SoftwareIsoTpLink(router.endpoint({rx} | set(kw.get("extra_rx_ids", ()))),
                                       tx, rx, owns_transport=True, **kw))


def test_demo_preset_nodes(demo):
    vehicle, _ = demo
    assert vehicle.node_names() == ["engine", "gateway", "abs"]
    assert all(n.running for n in vehicle.nodes)
    with pytest.raises(KeyError):
        vehicle.node("cluster")
    with pytest.raises(KeyError):
        SimulatedVehicle("no-such-preset")


def test_identify_each_module_with_distinct_identifiers(demo):
    vehicle, router = demo
    expected = {
        (0x7E0, 0x7E8): ("8V0906259H", "R4 2.0L TFSI"),
        (0x710, 0x77A): ("7N0907530C", "J533 Gateway"),
        (0x713, 0x77D): ("1K0907379AC", "ESP MK60EC1"),
    }
    for (tx, rx), (part, name) in expected.items():
        client = _client(router, tx, rx)
        ident = VagEcuSession(client).read_identity()
        assert ident.part_number == part
        assert ident.system_name == name
        assert ident.vin == "WVWZZZAUZLW000001"
        client.close()


def test_two_clients_two_nodes_concurrently_no_crosstalk(demo):
    vehicle, router = demo
    results = {}
    errors = []

    def worker(name, tx, rx, expect_part):
        client = _client(router, tx, rx)
        try:
            for _ in range(40):
                part = client.read_data_by_identifier(0xF187)
                if part != expect_part:
                    errors.append((name, part))
                client.diagnostic_session_control(0x03)
            results[name] = True
        except Exception as exc:  # pragma: no cover - surfaced via assertion below
            errors.append((name, repr(exc)))
        finally:
            client.close()

    threads = [
        threading.Thread(target=worker, args=("engine", 0x7E0, 0x7E8, b"8V0906259H")),
        threading.Thread(target=worker, args=("gateway", 0x710, 0x77A, b"7N0907530C")),
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join(timeout=10.0)
    assert errors == []
    assert results == {"engine": True, "gateway": True}


def test_multi_frame_request_and_response_through_ecu_isotp(demo):
    vehicle, router = demo
    engine: SimulatedEcu = vehicle.node("engine").ecu
    client = _client(router, 0x7E0, 0x7E8)
    try:
        # Multi-frame RESPONSE: ReadMemoryByAddress of 200 bytes -> FF + 28 CFs from the ECU,
        # which must wait for our Flow Control first.
        data = client.read_memory_by_address(0x0000, 200)
        assert data == engine.memory[:200]

        # Multi-frame REQUEST: WriteDataByIdentifier with a 100-byte value -> our FF, the
        # ECU's FC, our CFs; the ECU must reassemble and dispatch it to a custom handler.
        received = {}

        def wdbi(request: bytes) -> bytes:
            received["req"] = request
            return bytes([0x6E, request[1], request[2]])

        engine.custom_handlers[0x2E] = wdbi
        payload = bytes(range(100))
        client.write_data_by_identifier(0x0102, payload)
        assert received["req"] == bytes([0x2E, 0x01, 0x02]) + payload

        # Full calibration-sized upload still works end to end (security + many blocks).
        client.security_access(0x11, make_seed_key_fn(engine.sa2_script))
        assert client.upload(engine.cal_base, 0x2000) == engine.cal_memory[:0x2000]
    finally:
        client.close()


def test_functional_request_answered_by_every_listening_node(demo):
    vehicle, router = demo
    # Functional tester: send to 0x7DF, accept every physical response id.
    rx_ids = {0x7E8, 0x77A, 0x77D}
    link = SoftwareIsoTpLink(router.endpoint(rx_ids), tx_id=0x7DF, rx_id=0x7E8,
                             extra_rx_ids=[0x77A, 0x77D], owns_transport=True)
    link.send(bytes([0x3E, 0x00]))        # TesterPresent, positive response requested
    responders = {}
    deadline = time.monotonic() + 1.0
    while len(responders) < 3 and time.monotonic() < deadline:
        payload = link.recv(0.2)
        if payload is not None:
            responders[link.last_rx_id] = payload
    assert set(responders) == rx_ids
    assert all(p == b"\x7E\x00" for p in responders.values())

    # A node created with functional_id=None ignores 0x7DF.
    deaf = SimulatedEcu()
    vehicle.add_node(UdsNode(vehicle.bus, deaf, request_id=0x7E1, response_id=0x7E9,
                             functional_id=None, name="deaf-tcu"))
    assert vehicle.node("deaf-tcu").running
    wide = SoftwareIsoTpLink(router.endpoint(rx_ids | {0x7E9}), tx_id=0x7DF, rx_id=0x7E8,
                             extra_rx_ids=[0x77A, 0x77D, 0x7E9], owns_transport=True)
    wide.send(bytes([0x3E, 0x00]))
    got = set()
    deadline = time.monotonic() + 0.7
    while time.monotonic() < deadline:
        if wide.recv(0.1) is not None:
            got.add(wide.last_rx_id)
    assert got == rx_ids
    # ...but it answers physically.
    tcu = _client(router, 0x7E1, 0x7E9)
    assert tcu.read_data_by_identifier(0xF190) == b"WVWZZZAUZLW000001"
    tcu.close()
    link.close()
    wide.close()


def test_handler_exception_becomes_general_reject(demo):
    vehicle, router = demo
    engine: SimulatedEcu = vehicle.node("engine").ecu

    def broken(request: bytes) -> bytes:
        raise RuntimeError("simulated handler bug")

    engine.custom_handlers[0x31] = broken
    client = _client(router, 0x7E0, 0x7E8)
    try:
        with pytest.raises(NegativeResponse) as exc:
            client.routine_control(0x0203)
        assert exc.value.nrc == 0x10
        assert vehicle.node("engine").handler_errors == 1
        # Node is still alive and serving afterwards.
        assert client.read_data_by_identifier(0xF190) == b"WVWZZZAUZLW000001"
    finally:
        client.close()


def test_node_ignores_garbage_frames_and_keeps_serving(demo):
    vehicle, router = demo
    raw = router.endpoint(None)
    raw.send(CanFrame(0x7E0, b"\x21\x01\x02\x03"))            # orphan CF
    raw.send(CanFrame(0x7E0, b"\x30\x00\x00"))                # stray FC
    raw.send(CanFrame(0x7E0, b"\x10\x05\x01\x02\x03\x04\x05"))  # FF announcing 5 bytes (invalid)
    client = _client(router, 0x7E0, 0x7E8)
    try:
        assert client.read_data_by_identifier(0xF187) == b"8V0906259H"
    finally:
        client.close()
        raw.close()


def test_stop_joins_promptly_and_detaches():
    bus = FakeCanBus()
    node = UdsNode(bus, SimulatedEcu(), request_id=0x7E0, response_id=0x7E8, name="e")
    node.start()
    assert node.running
    assert node.transport in bus.transports
    t0 = time.monotonic()
    node.stop()
    assert time.monotonic() - t0 < 1.0
    assert not node.running
    assert node.transport not in bus.transports
    node.stop()  # idempotent


def test_vehicle_start_stop_and_context_manager():
    vehicle = SimulatedVehicle("demo")
    assert not vehicle.started and not any(n.running for n in vehicle.nodes)
    with vehicle:
        assert vehicle.started and all(n.running for n in vehicle.nodes)
        late = UdsNode(vehicle.bus, SimulatedEcu(), request_id=0x7E1, response_id=0x7E9, name="tcu")
        vehicle.add_node(late)
        assert late.running                      # added to a running vehicle -> started
        with pytest.raises(ValueError):
            vehicle.add_node(UdsNode(vehicle.bus, SimulatedEcu(), request_id=0x7E2,
                                     response_id=0x7EA, name="tcu"))
    assert not vehicle.started and not any(n.running for n in vehicle.nodes)


def test_register_preset_hook_adds_nodes_and_new_presets():
    calls = []

    def add_tcu(vehicle: SimulatedVehicle) -> None:
        calls.append(vehicle.preset)
        vehicle.add_node(UdsNode(vehicle.bus, SimulatedEcu(), request_id=0x7E1,
                                 response_id=0x7E9, name="hooked-tcu"))

    SimulatedVehicle.register_preset_hook("test-hook-preset", add_tcu)
    try:
        assert "test-hook-preset" in SimulatedVehicle.available_presets()
        v = SimulatedVehicle("test-hook-preset")
        assert v.node_names() == ["hooked-tcu"]
        assert calls == ["test-hook-preset"]
        with pytest.raises(TypeError):
            SimulatedVehicle.register_preset_hook("x", "not callable")
    finally:
        SimulatedVehicle.PRESETS.pop("test-hook-preset", None)
        SimulatedVehicle._PRESET_HOOKS.pop("test-hook-preset", None)


def test_car_presets_exist_and_are_hook_populated():
    for preset in ("golf-tdi-2012", "r32-2008"):
        v = SimulatedVehicle(preset)
        # Base builder adds nothing; nodes come from other slices' hooks.
        assert all(isinstance(n, SimulatedNode) for n in v.nodes)


def test_default_vehicle_lifecycle():
    reset_default_vehicle()
    try:
        v1 = get_default_vehicle()
        assert v1.preset == "demo" and v1.started
        assert get_default_vehicle() is v1
        assert get_default_vehicle("demo") is v1
        v2 = get_default_vehicle("r32-2008")
        assert v2 is not v1 and v2.preset == "r32-2008" and v2.started
        assert not v1.started
        reset_default_vehicle()
        assert not v2.started
        assert get_default_vehicle().preset == "demo"
    finally:
        reset_default_vehicle()


def test_fake_bus_latency_delays_delivery():
    bus = FakeCanBus(latency=0.05)
    a, b = bus.attach("a"), bus.attach("b")
    t0 = time.monotonic()
    a.send(CanFrame(0x1, b"\x00"))
    assert b.recv(0.5) is not None
    assert time.monotonic() - t0 >= 0.045
    assert a.recv(0.0) is None               # no self-reception
    assert bus.frames_published == 1


def _vin_via(vehicle, tx=0x7E0, rx=0x7E8):
    tester = vehicle.bus.attach("tester")
    router = CanRouter(tester)
    client = UdsClient(SoftwareIsoTpLink(router.endpoint([rx]), tx, rx, owns_transport=True),
                       UdsTiming(p2_timeout=1.0))
    try:
        return client.read_data_by_identifier(0xF190)
    finally:
        client.close()
        router.close()


def test_vehicle_restart_after_stop_answers_again():
    v = SimulatedVehicle("demo")
    v.start()
    assert _vin_via(v) == b"WVWZZZAUZLW000001"
    v.stop()
    assert not any(n.transport.is_open for n in v.nodes)
    v.start()
    time.sleep(0.1)
    assert v.started and all(n.running for n in v.nodes)
    assert all(n.transport.is_open and n.transport in v.bus.transports for n in v.nodes)
    try:
        assert _vin_via(v) == b"WVWZZZAUZLW000001"
        assert _vin_via(v, 0x710, 0x77A) == b"WVWZZZAUZLW000001"
    finally:
        v.stop()


def test_vehicle_context_manager_twice_and_node_restart():
    v = SimulatedVehicle("demo")
    for _ in range(2):
        with v:
            assert _vin_via(v, 0x713, 0x77D) == b"WVWZZZAUZLW000001"
    node = v.node("engine")
    node.start()
    node.stop()
    node.start()
    time.sleep(0.1)
    assert node.running and node.transport.is_open
    node.stop()


def test_default_vehicle_restarts_after_external_stop():
    reset_default_vehicle()
    try:
        v = get_default_vehicle()
        v.stop()
        assert get_default_vehicle() is v and v.started
        assert _vin_via(v) == b"WVWZZZAUZLW000001"
    finally:
        reset_default_vehicle()


def test_functional_multi_frame_answered_by_two_nodes(demo):
    vehicle, router = demo
    big = bytes(range(40))
    for name in ("engine", "gateway"):
        vehicle.node(name).ecu.custom_handlers[0x09] = lambda req: b"\x49\x02" + big   # OBD VIN-style
    rx = {0x7E8, 0x77A, 0x77D}
    link = SoftwareIsoTpLink(router.endpoint(rx), tx_id=0x7DF, rx_id=0x7E8,
                             extra_rx_ids=[0x77A, 0x77D], owns_transport=True)
    try:
        link.send(b"\x09\x02")
        got = {}
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline and len(got) < 3:
            p = link.recv(0.3)
            if p is not None:
                got[link.last_rx_id] = p
        assert got[0x7E8] == got[0x77A] == b"\x49\x02" + big
        assert got[0x77D] == b"\x7F\x09\x11"                 # abs: serviceNotSupported
    finally:
        link.close()


def test_node_rejects_flow_control_on_functional_id(demo):
    # Tester sends a physical request whose multi-frame response needs FC; FC on 0x7DF
    # must leave the node waiting (N_Bs), FC on 0x7E0 must release it.
    vehicle, router = demo
    raw = router.endpoint([0x7E8])
    # ReadMemoryByAddress alfid 0x22 (2-byte addr, 2-byte len), 40 bytes -> 41-byte response.
    raw.send(CanFrame(0x7E0, b"\x06\x23\x22\x00\x00\x00\x28\x55"))
    ff = raw.recv(1.0)
    assert ff is not None and ff.data[0] >> 4 == 0x1
    raw.send(CanFrame(0x7DF, b"\x30\x00\x00"))
    assert raw.recv(0.3) is None                                   # no CF: FC on 0x7DF ignored
    raw.send(CanFrame(0x7E0, b"\x30\x00\x00"))
    cf = raw.recv(1.0)
    assert cf is not None and cf.data[0] == 0x21
    raw.close()
