"""
CanRouter / RouterEndpoint tests on top of the in-memory FakeCanBus.

Covers: fan-out to several endpoints, a monitor endpoint that sees everything,
unmatched-frame accounting, bounded queues with drop-oldest + counter, precise
recv timeouts, set_accept_ids, endpoint close/unsubscribe, and close() stopping the
reader thread and the transport.
"""

from __future__ import annotations

import threading
import time

import pytest

from vagtune.transport.base import CanFrame, TransportNotOpen
from vagtune.transport.fakebus import FakeCanBus
from vagtune.transport.router import CanRouter, RouterEndpoint


def _bus_pair():
    """(router over transport A, raw transport B) on one fake bus."""
    bus = FakeCanBus()
    a = bus.attach("router-side")
    b = bus.attach("peer")
    return CanRouter(a, name="test"), b


def _wait(predicate, timeout=1.0) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(0.002)
    return predicate()


def test_router_opens_transport_and_starts_reader_lazily():
    bus = FakeCanBus()
    t = bus.attach("x")
    t.close()
    router = CanRouter(t)
    assert t.is_open
    assert not router.reader_alive
    ep = router.endpoint([0x7E8])
    assert router.reader_alive
    assert isinstance(ep, RouterEndpoint) and ep.is_open
    router.close()


def test_fan_out_to_multiple_endpoints_and_monitor():
    router, peer = _bus_pair()
    e1 = router.endpoint([0x7E8], name="engine")
    e2 = router.endpoint({0x77A}, name="gateway")
    mon = router.endpoint(None, name="sniffer")
    pred = router.endpoint(lambda f: f.data[:1] == b"\x62", name="positive-rdbi")

    peer.send(CanFrame(0x7E8, b"\x62\xF1\x90\x41"))
    peer.send(CanFrame(0x77A, b"\x50\x03\x00\x32\x01\xF4"))
    peer.send(CanFrame(0x123, b"\x00"))          # nobody listens by id -> monitor only

    assert e1.recv(0.5).arbitration_id == 0x7E8
    assert e1.recv(0.05) is None
    assert e2.recv(0.5).arbitration_id == 0x77A
    assert e2.recv(0.05) is None
    seen = [mon.recv(0.5) for _ in range(3)]
    assert [f.arbitration_id for f in seen] == [0x7E8, 0x77A, 0x123]
    assert pred.recv(0.5).arbitration_id == 0x7E8
    assert pred.recv(0.05) is None
    assert router.stats["rx_frames"] == 3
    # 0x123 matched the monitor, so nothing counts as unmatched yet.
    assert router.stats["dropped_unmatched"] == 0

    mon.close()
    pred.close()
    peer.send(CanFrame(0x124, b"\x00"))
    assert _wait(lambda: router.stats["dropped_unmatched"] == 1)
    router.close()


def test_send_goes_through_router_and_counts():
    router, peer = _bus_pair()
    ep = router.endpoint([0x7E8])
    ep.send(CanFrame(0x7E0, b"\x02\x10\x03"))
    ep.send_many([CanFrame(0x7E0, b"\x01"), CanFrame(0x7E0, b"\x02")])
    frames = [peer.recv(0.5) for _ in range(3)]
    assert [f.data for f in frames] == [b"\x02\x10\x03", b"\x01", b"\x02"]
    assert router.stats["tx_frames"] == 3
    router.close()


def test_overflow_drops_oldest_and_counts():
    router, peer = _bus_pair()
    ep = router.endpoint([0x100], queue_size=4)
    for i in range(10):
        peer.send(CanFrame(0x100, bytes([i])))
    assert _wait(lambda: ep.received == 10)
    assert ep.dropped == 6
    assert router.stats["dropped_overflow"] == 6
    kept = []
    while (f := ep.recv(0.0)) is not None:
        kept.append(f.data[0])
    assert kept == [6, 7, 8, 9]       # oldest dropped, newest kept, order preserved
    router.close()


def test_recv_timeout_is_honoured():
    router, _peer = _bus_pair()
    ep = router.endpoint([0x7E8])
    t0 = time.monotonic()
    assert ep.recv(0.2) is None
    elapsed = time.monotonic() - t0
    assert 0.18 <= elapsed < 0.6
    assert ep.recv(0.0) is None     # zero timeout returns immediately
    router.close()


def test_set_accept_ids_replaces_filter():
    router, peer = _bus_pair()
    ep = router.endpoint([0x7E8])
    peer.send(CanFrame(0x7E9, b"\x01"))
    assert ep.recv(0.1) is None
    ep.set_accept_ids([0x7E9])
    assert ep.accept_ids == frozenset({0x7E9})
    peer.send(CanFrame(0x7E9, b"\x02"))
    peer.send(CanFrame(0x7E8, b"\x03"))
    got = ep.recv(0.5)
    assert got is not None and got.data == b"\x02"
    assert ep.recv(0.1) is None
    router.close()


def test_endpoint_close_unsubscribes_and_raises_on_use():
    router, peer = _bus_pair()
    ep = router.endpoint([0x7E8])
    other = router.endpoint([0x7E8])
    ep.close()
    assert not ep.is_open
    assert ep not in router.endpoints and other in router.endpoints
    peer.send(CanFrame(0x7E8, b"\x01"))
    assert other.recv(0.5) is not None
    with pytest.raises(TransportNotOpen):
        ep.recv(0.05)
    with pytest.raises(TransportNotOpen):
        ep.send(CanFrame(0x7E0, b"\x01"))
    with pytest.raises(TransportNotOpen):
        ep.open()
    ep.close()  # idempotent
    router.close()


def test_endpoint_list_can_change_while_reader_runs():
    router, peer = _bus_pair()
    stop = threading.Event()

    def churn():
        while not stop.is_set():
            e = router.endpoint([0x200])
            e.close()

    t = threading.Thread(target=churn, daemon=True)
    t.start()
    keeper = router.endpoint([0x7E8])
    for i in range(200):
        peer.send(CanFrame(0x7E8, bytes([i & 0xFF])))
    got = 0
    while got < 200 and keeper.recv(1.0) is not None:
        got += 1
    stop.set()
    t.join(timeout=2.0)
    assert got == 200
    router.close()


def test_close_stops_reader_thread_and_closes_transport():
    router, peer = _bus_pair()
    ep = router.endpoint([0x7E8])
    thread = router._thread
    assert thread is not None and thread.is_alive()
    router.close()
    assert not thread.is_alive()
    assert router.is_closed
    assert not router.transport.is_open
    assert not ep.is_open
    with pytest.raises(TransportNotOpen):
        router.endpoint([0x7E8])
    with pytest.raises(TransportNotOpen):
        router.send(CanFrame(0x7E0, b"\x00"))
    router.close()  # idempotent


def test_context_manager_closes():
    bus = FakeCanBus()
    with CanRouter(bus.attach("a")) as router:
        router.endpoint(None)
    assert router.is_closed


def test_bad_predicate_does_not_kill_reader():
    router, peer = _bus_pair()

    def boom(frame):
        raise RuntimeError("predicate bug")

    router.endpoint(boom, name="bad")
    good = router.endpoint([0x7E8], name="good")
    peer.send(CanFrame(0x7E8, b"\x01"))
    assert good.recv(0.5) is not None
    assert router.reader_alive
    router.close()


def _blocked_consumer(ep, timeout=5.0):
    result = {}

    def consumer():
        t0 = time.monotonic()
        try:
            result["frame"] = ep.recv(timeout)
        except TransportNotOpen as exc:
            result["error"] = str(exc)
        result["elapsed"] = time.monotonic() - t0

    t = threading.Thread(target=consumer, daemon=True)
    t.start()
    time.sleep(0.05)
    return t, result


def test_endpoint_close_wakes_blocked_recv():
    router, _peer = _bus_pair()
    ep = router.endpoint([0x7E8], name="waiter")
    t, result = _blocked_consumer(ep)
    ep.close()
    t.join(timeout=1.0)
    assert not t.is_alive()
    assert "error" in result and result["elapsed"] < 0.5
    router.close()


def test_router_close_wakes_blocked_recv_and_keeps_queued_frames():
    router, peer = _bus_pair()
    ep = router.endpoint(None, name="sniffer")
    t, result = _blocked_consumer(ep)
    t0 = time.monotonic()
    router.close()
    assert time.monotonic() - t0 < 0.5
    t.join(timeout=1.0)
    assert not t.is_alive() and "error" in result and result["elapsed"] < 0.5
    # Frames delivered before a router-side close are still drained, then it raises.
    router2, peer2 = _bus_pair()
    ep2 = router2.endpoint([0x7E8])
    peer2.send(CanFrame(0x7E8, b"\x01"))
    assert _wait(lambda: ep2.pending == 1)
    router2.close()
    assert ep2.recv(0.0).data == b"\x01"
    with pytest.raises(TransportNotOpen):
        ep2.recv(0.0)
