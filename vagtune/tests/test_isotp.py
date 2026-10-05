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
from typing import Optional

import pytest

from vagtune.transport.base import CanFrame, RawCanTransport
from vagtune.transport.isotp import IsoTpConfig, SoftwareIsoTpLink, decode_stmin, encode_stmin


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
