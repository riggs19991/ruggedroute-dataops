"""
Software ISO-TP tests using an in-memory raw-CAN loopback.

We wire two SoftwareIsoTpLink endpoints to a shared frame fabric so a payload sent
by the "tester" link is segmented, flow-controlled, and reassembled by the "ECU"
link, and vice versa. This exercises single-frame, multi-frame, flow control, block
size, and sequence handling without any hardware.
"""

from __future__ import annotations

import queue
import threading
import time
from typing import Optional

import pytest

from vagtune.transport.base import CanFrame, RawCanTransport, TransportError, TransportTimeout
from vagtune.transport.isotp import (
    IsoTpConfig,
    SoftwareIsoTpLink,
    decode_stmin,
    encode_stmin,
    physical_request_id,
)


class LoopbackFabric:
    """Shared bus: frames written by one endpoint are readable by the other(s).

    Uses blocking queues so that a sender waiting on flow control and a receiver
    reassembling a multi-frame message can genuinely run on two threads.
    """

    def __init__(self) -> None:
        self._endpoints = []

    def register(self, ep: "LoopbackTransport") -> None:
        self._endpoints.append(ep)

    def publish(self, sender: "LoopbackTransport", frame: CanFrame) -> None:
        for ep in self._endpoints:
            if ep is not sender:
                ep._inbox.put(frame)


class LoopbackTransport(RawCanTransport):
    def __init__(self, fabric: LoopbackFabric) -> None:
        super().__init__()
        self.fabric = fabric
        self._inbox: "queue.Queue[CanFrame]" = queue.Queue()
        fabric.register(self)

    def open(self) -> None:
        self._open = True

    def close(self) -> None:
        self._open = False

    def send(self, frame: CanFrame) -> None:
        self.fabric.publish(self, frame)

    def recv(self, timeout: float) -> Optional[CanFrame]:
        try:
            return self._inbox.get(timeout=max(0.0, timeout))
        except queue.Empty:
            return None


def _make_pair(cfg_a=None, cfg_b=None):
    fabric = LoopbackFabric()
    ta, tb = LoopbackTransport(fabric), LoopbackTransport(fabric)
    ta.open(); tb.open()
    a = SoftwareIsoTpLink(ta, tx_id=0x7E0, rx_id=0x7E8, config=cfg_a or IsoTpConfig())
    b = SoftwareIsoTpLink(tb, tx_id=0x7E8, rx_id=0x7E0, config=cfg_b or IsoTpConfig())
    return a, b


def test_stmin_encoding_roundtrip():
    assert decode_stmin(0x00) == 0.0
    assert decode_stmin(0x0A) == 0.010
    assert decode_stmin(0x7F) == 0.127
    assert abs(decode_stmin(0xF1) - 0.0001) < 1e-9
    assert abs(decode_stmin(0xF5) - 0.0005) < 1e-9
    assert encode_stmin(0.010) == 0x0A
    assert encode_stmin(0.0005) == 0xF5
    assert encode_stmin(0.0) == 0x00


def test_single_frame_roundtrip():
    a, b = _make_pair()
    a.send(b"\x3E\x00")        # tester-present, fits a single frame
    assert b.recv(0.5) == b"\x3E\x00"


def test_single_frame_max_7_bytes():
    a, b = _make_pair()
    payload = bytes(range(7))
    a.send(payload)
    assert b.recv(0.5) == payload


def test_multi_frame_roundtrip():
    # 100-byte payload must become FF + consecutive frames with flow control.
    a, b = _make_pair()
    payload = bytes((i * 7) & 0xFF for i in range(100))

    received = {}

    def receiver():
        received["data"] = b.recv(2.0)

    t = threading.Thread(target=receiver)
    t.start()
    a.send(payload)
    t.join(timeout=3.0)
    assert received["data"] == payload


def test_multi_frame_with_block_size():
    # Receiver asks for block size 4; sender must wait for a new FC every 4 CFs.
    a, b = _make_pair(cfg_b=IsoTpConfig(rx_block_size=4))
    payload = bytes((0xA0 + (i % 16)) for i in range(60))

    received = {}

    def receiver():
        received["data"] = b.recv(2.0)

    t = threading.Thread(target=receiver)
    t.start()
    a.send(payload)
    t.join(timeout=3.0)
    assert received["data"] == payload


def test_padding_applied():
    cfg = IsoTpConfig(tx_padding=0x55)
    fabric = LoopbackFabric()
    ta, tb = LoopbackTransport(fabric), LoopbackTransport(fabric)
    ta.open(); tb.open()
    a = SoftwareIsoTpLink(ta, 0x7E0, 0x7E8, config=cfg)
    a.send(b"\x3E\x00")
    frame = tb._inbox.get(timeout=0.5)
    assert len(frame.data) == 8
    assert frame.data[3:] == bytes([0x55] * 5)


def test_empty_payload_rejected():
    a, _ = _make_pair()
    with pytest.raises(ValueError):
        a.send(b"")


# ---- 0.2.0 additions: extra_rx_ids, last_rx_id, stray/invalid frame handling ------

def _raw_pair():
    fabric = LoopbackFabric()
    ta, tb = LoopbackTransport(fabric), LoopbackTransport(fabric)
    ta.open(); tb.open()
    return ta, tb


def test_extra_rx_ids_accept_and_last_rx_id():
    ta, tb = _raw_pair()
    tester = SoftwareIsoTpLink(ta, tx_id=0x7DF, rx_id=0x7E8, extra_rx_ids=[0x7E9, 0x77A])
    assert tester.accept_ids == frozenset({0x7E8, 0x7E9, 0x77A})
    assert tester.last_rx_id is None
    tb.send(CanFrame(0x7E9, b"\x02\x7E\x00"))
    tb.send(CanFrame(0x7EA, b"\x02\x7E\x00"))     # not accepted
    tb.send(CanFrame(0x77A, b"\x02\x7E\x00"))
    assert tester.recv(0.5) == b"\x7E\x00" and tester.last_rx_id == 0x7E9
    assert tester.recv(0.5) == b"\x7E\x00" and tester.last_rx_id == 0x77A
    assert tester.recv(0.05) is None


def test_stray_fc_and_orphan_cf_are_skipped_not_fatal():
    ta, tb = _raw_pair()
    link = SoftwareIsoTpLink(ta, 0x7E0, 0x7E8)
    tb.send(CanFrame(0x7E8, b"\x30\x00\x00"))          # stray flow control
    tb.send(CanFrame(0x7E8, b"\x21\x01\x02\x03"))      # orphan consecutive frame
    tb.send(CanFrame(0x7E8, b""))                      # empty frame
    tb.send(CanFrame(0x7E8, b"\x08\x01\x02\x03\x04\x05\x06\x07"))  # SF length 8 (invalid)
    tb.send(CanFrame(0x7E8, b"\x00\x01"))              # SF length 0 (invalid)
    tb.send(CanFrame(0x7E8, b"\x02\x50\x03"))          # the real one
    assert link.recv(0.5) == b"\x50\x03"


def test_first_frame_announcing_fewer_than_8_bytes_is_ignored():
    ta, tb = _raw_pair()
    link = SoftwareIsoTpLink(ta, 0x7E0, 0x7E8)
    tb.send(CanFrame(0x7E8, b"\x10\x05\x01\x02\x03\x04\x05\x00"))  # FF with FF_DL = 5
    tb.send(CanFrame(0x7E8, b"\x10\x00\x00\x00\x10\x00\x00\x00"))  # FF with length escape
    tb.send(CanFrame(0x7E8, b"\x03\x62\xF1\x90"))
    assert link.recv(0.5) == b"\x62\xF1\x90"
    # No flow control must have been sent for the invalid first frames.
    assert tb._inbox.empty()


def test_recv_zero_timeout_takes_buffered_frame():
    ta, tb = _raw_pair()
    link = SoftwareIsoTpLink(ta, 0x7E0, 0x7E8)
    assert link.recv(0.0) is None
    tb.send(CanFrame(0x7E8, b"\x02\x7E\x00"))
    assert link.recv(0.0) == b"\x7E\x00"


def test_multi_frame_completes_when_caller_polls_with_short_timeout():
    # A receiver polling recv() with a short timeout (like a simulated ECU or a
    # keepalive-aware client) must finish a transfer it has already acknowledged,
    # even if the caller's timeout expires mid-transfer: N_Cr governs CF waits.
    a, b = _make_pair()
    payload = bytes((i * 3) & 0xFF for i in range(300))
    result = {}

    def receiver():
        deadline = time.monotonic() + 3.0
        while time.monotonic() < deadline:
            got = b.recv(0.001)
            if got is not None:
                result["data"] = got
                return

    t = threading.Thread(target=receiver)
    t.start()
    time.sleep(0.02)
    a.send(payload)
    t.join(timeout=4.0)
    assert result.get("data") == payload


def test_reassembly_ignores_frames_from_other_responders():
    ta, tb = _raw_pair()
    link = SoftwareIsoTpLink(ta, 0x7DF, 0x7E8, extra_rx_ids=[0x7E9])
    payload = bytes(range(20))
    result = {}

    def receiver():
        result["data"] = link.recv(1.0)

    t = threading.Thread(target=receiver)
    t.start()
    tb.send(CanFrame(0x7E8, bytes([0x10, 20]) + payload[:6]))
    fc = tb._inbox.get(timeout=1.0)
    # ISO 15765-4: the FC for a response on 0x7E8 goes to its physical request id 0x7E0,
    # never to the functional id the request went out on.
    assert fc.arbitration_id == 0x7E0 and fc.data[0] == 0x30
    tb.send(CanFrame(0x7E9, b"\x21\xAA\xAA\xAA\xAA\xAA\xAA\xAA"))   # another ECU's CF, ignored
    tb.send(CanFrame(0x7E8, bytes([0x21]) + payload[6:13]))
    tb.send(CanFrame(0x7E8, bytes([0x22]) + payload[13:20]))
    t.join(timeout=2.0)
    assert result["data"] == payload
    assert link.last_rx_id == 0x7E8


def test_owns_transport_closes_it():
    ta, _ = _raw_pair()
    link = SoftwareIsoTpLink(ta, 0x7E0, 0x7E8, owns_transport=True)
    link.close()
    assert not ta.is_open
    ta2, _ = _raw_pair()
    link2 = SoftwareIsoTpLink(ta2, 0x7E0, 0x7E8)
    link2.close()
    assert ta2.is_open


# ---- functional addressing: FC target policy, concurrent responders, N_Cr --------

def test_physical_request_id_pairing_rules():
    assert physical_request_id(0x7E8) == 0x7E0 and physical_request_id(0x7EF) == 0x7E7
    assert physical_request_id(0x77A) == 0x710        # gateway (verified VAG pair)
    assert physical_request_id(0x77D) == 0x713        # ABS
    assert physical_request_id(0x779) == 0x70F        # Haldex
    assert physical_request_id(0x18DAF110) == 0x18DA10F1
    assert physical_request_id(0x123) is None


def test_flow_control_ids_default_override_and_functional_send_refused():
    ta, _ = _raw_pair()
    physical = SoftwareIsoTpLink(ta, 0x7E0, 0x7E8)
    assert physical.flow_control_ids == {0x7E8: 0x7E0} and not physical.is_functional
    functional = SoftwareIsoTpLink(ta, 0x7DF, 0x7E8, extra_rx_ids=[0x7E9, 0x77A, 0x123])
    assert functional.is_functional
    assert functional.flow_control_ids == {0x7E8: 0x7E0, 0x7E9: 0x7E1, 0x77A: 0x710, 0x123: 0x7DF}
    custom = SoftwareIsoTpLink(ta, 0x7DF, 0x7E8, extra_rx_ids=[0x7E9],
                               flow_control_ids={0x7E9: 0x600})
    assert custom.flow_control_ids == {0x7E8: 0x7E0, 0x7E9: 0x600}
    by_fn = SoftwareIsoTpLink(ta, 0x7DF, 0x7E8, extra_rx_ids=[0x7E9],
                              flow_control_ids=lambda rid: rid + 0x100)
    assert by_fn.flow_control_ids == {0x7E8: 0x8E8, 0x7E9: 0x8E9}
    # ISO 15765-4: a functional request must fit a single frame.
    with pytest.raises(TransportError):
        functional.send(bytes(8))
    functional.send(bytes(7))      # still fine


def test_two_responders_interleaved_multi_frame_on_functional_link():
    ta, tb = _raw_pair()
    link = SoftwareIsoTpLink(ta, 0x7DF, 0x7E8, extra_rx_ids=[0x77A])
    engine = bytes(range(20))
    gateway = bytes(range(100, 118))
    got = {}

    def receiver():
        for _ in range(2):
            p = link.recv(1.0)
            got[link.last_rx_id] = p

    t = threading.Thread(target=receiver)
    t.start()
    tb.send(CanFrame(0x7E8, bytes([0x10, 20]) + engine[:6]))
    tb.send(CanFrame(0x77A, bytes([0x10, 18]) + gateway[:6]))       # second FF mid-reassembly
    fcs = {}
    for _ in range(2):
        fc = tb._inbox.get(timeout=1.0)
        fcs[fc.arbitration_id] = fc.data[0]
    assert fcs == {0x7E0: 0x30, 0x710: 0x30}                       # one FC each, physical ids
    tb.send(CanFrame(0x77A, bytes([0x21]) + gateway[6:13]))
    tb.send(CanFrame(0x7E8, bytes([0x21]) + engine[6:13]))
    tb.send(CanFrame(0x77A, bytes([0x22]) + gateway[13:18]))         # gateway completes first
    tb.send(CanFrame(0x7E8, bytes([0x22]) + engine[13:20]))
    t.join(timeout=3.0)
    assert got == {0x77A: gateway, 0x7E8: engine}
    assert link.receiving == frozenset()


def test_ecu_side_link_ignores_flow_control_on_functional_id():
    # The simulated ECU listens on 0x7E0 and 0x7DF; a FC on 0x7DF must not release
    # its multi-frame response (a real ECU never accepts FC on the functional id).
    ta, tb = _raw_pair()
    ecu = SoftwareIsoTpLink(ta, tx_id=0x7E8, rx_id=0x7E0, extra_rx_ids=[0x7DF],
                            config=IsoTpConfig(n_bs=0.2))
    result = {}

    def sender():
        try:
            ecu.send(bytes(range(30)))
            result["sent"] = True
        except TransportTimeout as exc:
            result["error"] = str(exc)

    t = threading.Thread(target=sender)
    t.start()
    ff = tb._inbox.get(timeout=1.0)
    assert ff.data[0] >> 4 == 0x1
    tb.send(CanFrame(0x7DF, b"\x30\x00\x00"))          # FC on the functional id: ignored
    t.join(timeout=2.0)
    assert "N_Bs" in result.get("error", "")
    assert tb._inbox.empty()                              # no consecutive frames went out

    # The same FC on the physical id does release the transfer.
    t = threading.Thread(target=sender)
    t.start()
    tb._inbox.get(timeout=1.0)
    tb.send(CanFrame(0x7E0, b"\x30\x00\x00"))
    t.join(timeout=2.0)
    assert result.get("sent") is True


def test_n_cr_timeout_drops_partial_and_raises():
    ta, tb = _raw_pair()
    link = SoftwareIsoTpLink(ta, 0x7E0, 0x7E8, config=IsoTpConfig(n_cr=0.1))
    tb.send(CanFrame(0x7E8, bytes([0x10, 20]) + bytes(6)))
    t0 = time.monotonic()
    with pytest.raises(TransportTimeout) as exc:
        link.recv(0.01)           # caller timeout is short; N_Cr governs once the FF is in
    assert "0x7E8" in str(exc.value)
    assert 0.08 <= time.monotonic() - t0 < 1.0
    assert link.receiving == frozenset()
    tb.send(CanFrame(0x7E8, b"\x02\x7E\x00"))
    assert link.recv(0.5) == b"\x7E\x00"                  # link keeps working afterwards


def test_sequence_error_drops_partial_and_raises():
    ta, tb = _raw_pair()
    link = SoftwareIsoTpLink(ta, 0x7E0, 0x7E8)
    tb.send(CanFrame(0x7E8, bytes([0x10, 20]) + bytes(6)))
    tb.send(CanFrame(0x7E8, bytes([0x23]) + bytes(7)))     # expected seq 1, got 3
    with pytest.raises(TransportError):
        link.recv(0.5)
    assert link.receiving == frozenset()
