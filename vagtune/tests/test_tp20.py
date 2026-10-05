"""
VW TP 2.0 tests: tester (Tp20Channel) against the simulated module (Tp20Node) on a
FakeCanBus, byte-exact against the traces in the research sheet.

Covers: timing codec; setup/parameter handshake bytes; single- and multi-frame in
both directions including a block-size ACK mid-message and the 48-byte 1A 9B reply;
sequence wrap F->0; wrong-ACK retransmission (both sides); 0x9X not-ready; an A3
arriving mid-response; keepalive; A8 both ways; D8 refusal; setup retry on silence
and the alternate setup form; the address probe; Tactrix-style echoes of our own
frames; TransportContext("fake").tp20_channel end to end.
"""

from __future__ import annotations

import queue
import threading
import time
from types import SimpleNamespace
from typing import List, Tuple

import pytest

from vagtune.transport import TransportContext
from vagtune.transport.base import CanFrame, RawCanTransport, TransportNotOpen
from vagtune.transport.fakebus import FakeCanBus, FakeCanTransport, SimulatedNode, SimulatedVehicle, \
    reset_default_vehicle
from vagtune.transport.router import CanRouter
from vagtune.transport.tp20 import (
    APP_TYPE_TEXT,
    SetupResponse,
    Tp20Channel,
    Tp20ChannelClosed,
    Tp20ChannelRefused,
    Tp20Error,
    Tp20Params,
    Tp20Timeout,
    build_setup_request,
    decode_timing,
    encode_timing,
    frame_opcode,
    parse_setup_response,
    probe_tp20_addresses,
    split_message,
    tester_rx_ids_in_use as rx_ids_in_use,
)
import vagtune.transport.tp20 as tp20_module
from vagtune.transport.tp20_sim import MODULE_DEFAULT_PARAMS, Tp20Node, Tp20Responder

h = bytes.fromhex

# The 48-byte readEcuIdentification reply from the NefMoto trace (5A 9B + 46 bytes).
IDENT_1A9B = h(
    "5A 9B 31 4B 30"
    "39 30 37 31 31 35 4C"
    "20 20 30 30 33 30 10"
    "00 00 00 00 06 46 22"
    "04 F5 32 2E 30 6C 20"
    "52 34 2F 34 56 20 54"
    "46 53 49 20 20 20 20"
    "20"
)
assert len(IDENT_1A9B) == 48


def kwp_handler(request: bytes):
    """A tiny KWP2000 brain for the simulated modules."""
    sid = request[0]
    if request == b"\x10\x89":
        return b"\x50\x89"
    if request == b"\x1A\x9B":
        return IDENT_1A9B
    if sid == 0x3E:
        return b"\x7E"
    if sid == 0x21:
        return b"\x61" + request[1:2] + bytes(range(24))
    if sid == 0x3B:                                   # writeDataByLocalId: echo length
        return b"\x7B" + request[1:2] + len(request).to_bytes(2, "big")
    if sid == 0x23:                                   # readMemoryByAddress: n bytes pattern
        n = request[4]
        return b"\x63" + bytes((i * 7) & 0xFF for i in range(n))
    if request == b"\x31\xB8\x00\x00":                # responsePending then the answer
        return [b"\x7F\x31\x78", b"\x71\xB8\x01"]
    if sid == 0xFE:
        raise RuntimeError("handler exploded")
    return bytes([0x7F, sid, 0x11])


def drain(transport: FakeCanTransport) -> List[Tuple[int, bytes]]:
    out = []
    while True:
        try:
            f = transport.inbox.get_nowait()
        except queue.Empty:
            return out
        out.append((f.arbitration_id, bytes(f.data)))


def wait_for(predicate, timeout: float = 1.0, step: float = 0.005) -> bool:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if predicate():
            return True
        time.sleep(step)
    return predicate()


class _Env:
    def __init__(self, transport_cls=FakeCanTransport) -> None:
        self.bus = FakeCanBus()
        self.spy = self.bus.attach("spy")
        tester = transport_cls(self.bus, "tester")
        tester.open()
        self.router = CanRouter(tester, name="tester", poll_interval=0.01)
        self.nodes: List[SimulatedNode] = []
        self.channels: List[Tp20Channel] = []

    def add(self, addr: int, tester_tx_id: int, handler=kwp_handler, **kw) -> Tp20Node:
        node = Tp20Node(self.bus, handler, logical_address=addr, tester_tx_id=tester_tx_id, **kw)
        node.start()
        self.nodes.append(node)
        return node

    def channel(self, addr: int = 0x01, **kw) -> Tp20Channel:
        kw.setdefault("keepalive", False)
        ch = Tp20Channel(self.router, addr, **kw)
        self.channels.append(ch)
        return ch

    def close(self) -> None:
        for ch in self.channels:
            ch.close()
        self.router.close()
        for n in self.nodes:
            n.stop()


@pytest.fixture
def env():
    e = _Env()
    yield e
    e.close()


@pytest.fixture
def engine_env(env):
    env.add(0x01, 0x740, name="engine")
    return env


# ============================================================================ codecs

def test_timing_decode_vectors():
    assert decode_timing(0x8A) == pytest.approx(100.0)
    assert decode_timing(0x4A) == pytest.approx(10.0)
    assert decode_timing(0x32) == pytest.approx(5.0)
    assert decode_timing(0x0A) == pytest.approx(1.0)
    assert decode_timing(0xFF) == pytest.approx(6300.0)
    assert decode_timing(0x00) == 0.0
    with pytest.raises(ValueError):
        decode_timing(0x100)


def test_timing_encode_vectors_and_roundtrip():
    assert encode_timing(100) == 0x8A
    assert encode_timing(10) == 0x4A
    assert encode_timing(5) == 0x32
    assert encode_timing(1) == 0x0A
    assert encode_timing(6300) == 0xFF
    assert encode_timing(9999) == 0xFF
    assert encode_timing(0) == 0x00
    assert encode_timing(0.3) == 0x03
    for raw in range(256):
        assert decode_timing(encode_timing(decode_timing(raw))) == pytest.approx(decode_timing(raw))
    with pytest.raises(ValueError):
        encode_timing(-1)


def test_params_bytes_and_properties():
    p = Tp20Params()
    assert p.to_bytes() == h("A0 0F 8A FF 32 FF")                 # registry conflict C7: T3 5 ms
    assert p.t1_ack_timeout == pytest.approx(0.1)
    assert p.t3_min_interframe == pytest.approx(0.005)
    assert MODULE_DEFAULT_PARAMS.to_bytes(0xA1) == h("A1 0F 8A FF 4A FF")   # every traced module
    assert MODULE_DEFAULT_PARAMS.t3_min_interframe == pytest.approx(0.01)
    q = Tp20Params.from_bytes(h("A1 0F 8A FF 32 FF"))
    assert q.t3_min_interframe == pytest.approx(0.005) and q.block_size == 15
    assert Tp20Params.make(block_size=8, t1_ms=100, t3_ms=5).to_bytes() == h("A0 08 8A FF 32 FF")
    assert Tp20Params(block_size=0x20).effective_block_size == 15
    assert Tp20Params(block_size=0).effective_block_size == 1
    with pytest.raises(Tp20Error):
        Tp20Params.from_bytes(h("B1 0F 8A FF 4A FF"))
    with pytest.raises(ValueError):
        Tp20Params(t1=0x100)


def test_setup_request_forms():
    assert build_setup_request(0x01) == h("01 C0 00 10 00 03 01")
    assert build_setup_request(0x09) == h("09 C0 00 10 00 03 01")
    assert build_setup_request(0x1F, tx_id=0x301) == h("1F C0 00 10 01 03 01")
    assert build_setup_request(0x01, rx_id=0x300) == h("01 C0 00 03 00 03 01")   # MED17.5 form


def test_setup_response_parse():
    r = parse_setup_response(h("00 D0 00 03 40 07 01"))
    assert r.ok and r.rx_id == 0x300 and r.tx_id == 0x740 and r.rx_valid and r.tx_valid and r.app == 1
    r = parse_setup_response(h("00 D0 00 03 A8 07 01"))
    assert r.tx_id == 0x7A8
    r = parse_setup_response(h("00 D0 00 13 40 07 01"))
    assert r.rx_id == 0x300 and not r.rx_valid
    assert parse_setup_response(h("00 D8 00 03 40 07 01")).opcode == 0xD8
    with pytest.raises(Tp20Error, match="TP 1.6"):
        parse_setup_response(h("01 D0 A1"))
    with pytest.raises(Tp20Error):
        parse_setup_response(h("00 D0 00 03"))


def test_split_message():
    assert split_message(b"\x10\x89") == [h("00 02 10 89")]
    chunks = split_message(bytes(12))
    assert chunks == [h("00 0C 00 00 00 00 00"), bytes(7)]
    with pytest.raises(ValueError):
        split_message(b"")
    with pytest.raises(Tp20Error):
        split_message(bytes(0x8000))


# ========================================================================= handshake

def test_connect_handshake_byte_exact(engine_env):
    env = engine_env
    ch = env.channel(0x01)
    ch.connect()
    assert ch.connected and ch.setup_form == "standard"
    assert ch.tx_id == 0x740 and ch.rx_id == 0x300
    assert ch.ecu_rx_id == 0x740 and ch.ecu_tx_id == 0x300
    assert ch.peer_params == MODULE_DEFAULT_PARAMS
    assert ch.t1 == pytest.approx(0.1) and ch.t3 == pytest.approx(0.01) and ch.block_size == 15
    time.sleep(0.02)
    assert drain(env.spy)[:4] == [
        (0x200, h("01 C0 00 10 00 03 01")),
        (0x201, h("00 D0 00 03 40 07 01")),
        (0x740, h("A0 0F 8A FF 32 FF")),
        (0x300, h("A1 0F 8A FF 4A FF")),
    ]
    assert rx_ids_in_use(env.router) == {0x300: "tp20-01"}
    ch.connect()                       # idempotent
    assert ch.stats["tx_frames"] == 2


def test_single_frame_exchange_byte_exact(engine_env):
    env = engine_env
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    ch.send(b"\x10\x89")
    assert ch.recv(1.0) == b"\x50\x89"
    time.sleep(0.02)
    assert drain(env.spy) == [
        (0x740, h("10 00 02 10 89")),
        (0x300, h("B1")),
        (0x300, h("10 00 02 50 89")),
        (0x740, h("B1")),
    ]


def test_ident_48_byte_response_matches_trace(engine_env):
    env = engine_env
    ch = env.channel(0x01)
    ch.connect()
    ch.send(b"\x10\x89")
    assert ch.recv(1.0) == b"\x50\x89"
    drain(env.spy)
    ch.send(b"\x1A\x9B")
    assert ch.recv(1.0) == IDENT_1A9B
    time.sleep(0.02)
    assert drain(env.spy) == [
        (0x740, h("11 00 02 1A 9B")),
        (0x300, h("B2")),
        (0x300, h("21 00 30 5A 9B 31 4B 30")),
        (0x300, h("22 39 30 37 31 31 35 4C")),
        (0x300, h("23 20 20 30 30 33 30 10")),
        (0x300, h("24 00 00 00 00 06 46 22")),
        (0x300, h("25 04 F5 32 2E 30 6C 20")),
        (0x300, h("26 52 34 2F 34 56 20 54")),
        (0x300, h("27 46 53 49 20 20 20 20")),
        (0x300, h("18 20")),
        (0x740, h("B9")),
    ]
    assert ch.stats["rx_messages"] == 2 and ch.stats["tx_messages"] == 2


def test_eps_assigns_different_tx_id(env):
    env.add(0x09, 0x7A8, name="eps")
    ch = env.channel(0x09, params=Tp20Params(t3=0x0A))
    ch.connect()
    assert ch.tx_id == 0x7A8
    ch.send(b"\x10\x89")
    assert ch.recv(1.0) == b"\x50\x89"
    time.sleep(0.02)
    frames = drain(env.spy)
    assert frames[:4] == [
        (0x200, h("09 C0 00 10 00 03 01")),
        (0x209, h("00 D0 00 03 A8 07 01")),
        (0x7A8, h("A0 0F 8A FF 0A FF")),
        (0x300, h("A1 0F 8A FF 4A FF")),
    ]


# ============================================================== multi-frame / blocks

def test_long_request_block_size_ack_mid_message(engine_env):
    env = engine_env
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    payload = b"\x3B\x01" + bytes(range(120))          # 122 + 2 length bytes = 18 frames
    ch.send(payload)
    assert ch.recv(1.0) == b"\x7B\x01\x00\x7A"
    time.sleep(0.02)
    frames = drain(env.spy)
    ours = [d for (i, d) in frames if i == 0x740 and (d[0] >> 4) <= 3]
    assert len(ours) == 18
    assert [d[0] for d in ours] == [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29,
                                    0x2A, 0x2B, 0x2C, 0x2D, 0x0E, 0x2F, 0x20, 0x11]
    acks = [d for (i, d) in frames if i == 0x300 and (d[0] >> 4) == 0xB]
    assert acks == [h("BF"), h("B2")]
    assert b"".join(d[1:] for d in ours)[2:] == payload
    assert ch.stats["retransmissions"] == 0


def test_long_response_block_acks(engine_env):
    env = engine_env
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    ch.send(h("23 00 00 00 96"))                           # 150 bytes -> 151 + 2 = 22 frames
    resp = ch.recv(2.0)
    assert resp == b"\x63" + bytes((i * 7) & 0xFF for i in range(150))
    time.sleep(0.02)
    frames = drain(env.spy)
    theirs = [d for (i, d) in frames if i == 0x300 and (d[0] >> 4) <= 3]
    assert len(theirs) == 22
    assert (theirs[14][0] >> 4) == 0x0 and (theirs[21][0] >> 4) == 0x1
    our_acks = [d for (i, d) in frames if i == 0x740 and (d[0] >> 4) == 0xB]
    assert our_acks == [h("BF"), h("B6")]


def test_sequence_counters_wrap_across_messages(engine_env):
    env = engine_env
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    for _ in range(17):
        ch.send(b"\x3E")
        assert ch.recv(1.0) == b"\x7E"
    time.sleep(0.02)
    frames = drain(env.spy)
    ours = [d[0] for (i, d) in frames if i == 0x740 and (d[0] >> 4) <= 3]
    theirs = [d[0] for (i, d) in frames if i == 0x300 and (d[0] >> 4) <= 3]
    assert ours == [0x10 | (k & 0xF) for k in range(17)]
    assert theirs == [0x10 | (k & 0xF) for k in range(17)]
    assert ours[15] == 0x1F and ours[16] == 0x10
    acks_to_us = [d[0] for (i, d) in frames if i == 0x300 and (d[0] >> 4) == 0xB]
    assert acks_to_us[15] == 0xB0 and acks_to_us[16] == 0xB1


def test_two_messages_after_one_ack(engine_env):
    ch = engine_env.channel(0x01)
    ch.connect()
    ch.send(h("31 B8 00 00"))
    assert ch.recv(1.0) == h("7F 31 78")
    assert ch.recv(1.0) == h("71 B8 01")


def test_length_msb_is_masked(engine_env):
    env = engine_env
    env.nodes[0].responder.length_msb = True
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    ch.send(b"\x1A\x9B")
    assert ch.recv(1.0) == IDENT_1A9B
    time.sleep(0.02)
    first = [d for (i, d) in drain(env.spy) if i == 0x300 and len(d) == 8][0]
    assert first[:3] == h("20 80 30")


def test_peer_block_size_and_t3_are_honoured(env):
    env.add(0x01, 0x740, params=Tp20Params(block_size=8, t3=0x32))
    ch = env.channel(0x01)
    ch.connect()
    assert ch.block_size == 8 and ch.t3 == pytest.approx(0.005)
    drain(env.spy)
    ch.send(b"\x3B\x02" + bytes(50))                      # 52 + 2 = 54 -> 8 frames
    assert ch.recv(1.0) == b"\x7B\x02\x00\x34"
    time.sleep(0.02)
    frames = drain(env.spy)
    ours = [d[0] for (i, d) in frames if i == 0x740 and (d[0] >> 4) <= 3]
    assert ours == [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x17]
    ch.send(b"\x3B\x03" + bytes(60))                      # 62 + 2 = 64 -> 10 frames: ACK at the 8th
    assert ch.recv(1.0) == b"\x7B\x03\x00\x3E"
    time.sleep(0.02)
    frames = drain(env.spy)
    ours = [d[0] for (i, d) in frames if i == 0x740 and (d[0] >> 4) <= 3]
    assert ours == [0x28, 0x29, 0x2A, 0x2B, 0x2C, 0x2D, 0x2E, 0x0F, 0x20, 0x11]
    assert [d for (i, d) in frames if i == 0x300 and (d[0] >> 4) == 0xB] == [h("B0"), h("B2")]


# =============================================================== error handling

def test_wrong_ack_tester_retransmits_from_acked_sequence(engine_env):
    env = engine_env
    env.nodes[0].responder.drop_once = {1}
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    payload = b"\x3B\x01" + bytes(range(12))               # 14 + 2 = 16 bytes -> 3 frames
    ch.send(payload)
    assert ch.recv(1.0) == b"\x7B\x01\x00\x0E"
    assert ch.stats["retransmissions"] == 1
    time.sleep(0.02)
    frames = drain(env.spy)
    ours = [d[0] for (i, d) in frames if i == 0x740 and (d[0] >> 4) <= 3]
    assert ours == [0x20, 0x21, 0x12, 0x21, 0x12]
    assert [d for (i, d) in frames if i == 0x300 and (d[0] >> 4) == 0xB] == [h("B1"), h("B3")]


def test_module_retransmits_then_disconnects_on_wrong_acks(env):
    """Replays the NefMoto trace from the ECU's side: a tester that ACKs the 48-byte
    ident reply with the wrong value gets a retransmission from the acknowledged
    sequence, three times, then A8."""
    node = env.add(0x01, 0x740, name="engine", ack_timeout=0.5)
    raw = env.bus.attach("rawtester")

    def recv_on(arb_id: int, timeout: float = 1.0) -> bytes:
        deadline = time.monotonic() + timeout
        while True:
            remaining = deadline - time.monotonic()
            assert remaining > 0, f"nothing on 0x{arb_id:X}"
            f = raw.recv(remaining)
            if f is not None and f.arbitration_id == arb_id:
                return bytes(f.data)

    raw.send(CanFrame(0x200, h("01 C0 00 10 00 03 01")))
    assert recv_on(0x201) == h("00 D0 00 03 40 07 01")
    raw.send(CanFrame(0x740, h("A0 0F 8A FF 32 FF")))
    assert recv_on(0x300) == h("A1 0F 8A FF 4A FF")
    raw.send(CanFrame(0x740, h("10 00 02 1A 9B")))
    assert recv_on(0x300) == h("B1")
    frames = [recv_on(0x300) for _ in range(8)]
    assert frames[0] == h("20 00 30 5A 9B 31 4B 30") and frames[-1] == h("17 20")
    for round_ in range(3):
        raw.send(CanFrame(0x740, h("B2")))                 # wrong: should be B8
        resent = [recv_on(0x300) for _ in range(6)]
        assert [d[0] for d in resent] == [0x22, 0x23, 0x24, 0x25, 0x26, 0x17]
    raw.send(CanFrame(0x740, h("B2")))
    assert recv_on(0x300) == h("A8")
    assert wait_for(lambda: not node.responder.channel_open)
    assert node.responder.stats["retransmissions"] == 4
    raw.close()


def test_not_ready_then_ack_within_wait(engine_env):
    env = engine_env
    r = env.nodes[0].responder
    r.not_ready_count = 1
    r.not_ready_release = 0.03
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    ch.send(b"\x10\x89")
    assert ch.recv(1.0) == b"\x50\x89"
    assert ch.stats["naks"] == 1 and ch.stats["retransmissions"] == 0
    time.sleep(0.02)
    frames = drain(env.spy)
    assert [d for (i, d) in frames if i == 0x300][:3] == [h("91"), h("B1"), h("10 00 02 50 89")]
    assert [d for (i, d) in frames if i == 0x740 and (d[0] >> 4) <= 3] == [h("10 00 02 10 89")]


def test_not_ready_without_release_retransmits_after_t_wait(engine_env):
    env = engine_env
    r = env.nodes[0].responder
    r.not_ready_count = 1
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    t0 = time.monotonic()
    ch.send(b"\x10\x89")
    assert time.monotonic() - t0 >= Tp20Channel.T_WAIT
    assert ch.recv(1.0) == b"\x50\x89"
    assert ch.stats["naks"] == 1 and ch.stats["retransmissions"] == 1
    time.sleep(0.02)
    frames = drain(env.spy)
    assert [d for (i, d) in frames if i == 0x740 and (d[0] >> 4) <= 3] == [h("10 00 02 10 89")] * 2
    assert [d for (i, d) in frames if i == 0x300][:2] == [h("91"), h("B1")]


def test_not_ready_exhausted_raises(engine_env):
    env = engine_env
    env.nodes[0].responder.not_ready_count = 50
    ch = env.channel(0x01)
    ch.connect()
    with pytest.raises(Tp20Error, match="not ready"):
        ch.send(b"\x10\x89")
    assert ch.stats["naks"] == Tp20Channel.MAX_NAK + 1


def test_ack_timeout_raises_tp20_timeout(engine_env):
    env = engine_env
    node = env.nodes[0]
    ch = env.channel(0x01)
    ch.connect()
    node.stop()                                            # module vanishes
    t0 = time.monotonic()
    with pytest.raises(Tp20Timeout):
        ch.send(b"\x10\x89")
    assert 0.08 <= time.monotonic() - t0 < 1.0
    node.start()                                           # fresh module: old channel is gone
    ch.disconnect()                                        # releases 0x300 (no A8 comes back)
    assert rx_ids_in_use(env.router) == {}
    ch2 = env.channel(0x01)
    ch2.connect()
    ch2.send(b"\x3E")
    assert ch2.recv(1.0) == b"\x7E"


def test_handler_exception_becomes_general_reject(engine_env):
    ch = engine_env.channel(0x01)
    ch.connect()
    ch.send(b"\xFE\x01")
    assert ch.recv(1.0) == h("7F FE 10")
    assert engine_env.nodes[0].responder.stats["handler_errors"] == 1
    ch.send(b"\x3E")
    assert ch.recv(1.0) == b"\x7E"


def test_tp16_reply_is_rejected(env):
    class Tp16Decoy(SimulatedNode):
        def __init__(self, bus, addr):
            super().__init__(f"tp16-{addr:02X}")
            self.addr = addr
            self.transport = bus.attach(self.name)

        def run(self):
            while not self.should_stop:
                f = self.transport.recv(0.02)
                if f is not None and f.arbitration_id == 0x200 and f.data[:2] == bytes([self.addr, 0xC0]):
                    self.transport.send(CanFrame(0x200 + self.addr, bytes([self.addr, 0xD0, 0xA1])))

        def on_stopped(self):
            self.transport.close()

    decoy = Tp16Decoy(env.bus, 0x05)
    decoy.start()
    env.nodes.append(decoy)
    ch = env.channel(0x05, setup_timeout=0.1)
    with pytest.raises(Tp20Error, match="TP 1.6"):
        ch.connect()


# ============================================================ control frames

def test_inline_a3_during_response_is_answered_and_stripped(engine_env):
    env = engine_env
    env.nodes[0].responder.inject_a3_before_frame = 3
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    ch.send(b"\x1A\x9B")
    assert ch.recv(1.0) == IDENT_1A9B
    assert ch.stats["inline_a3"] == 1 and ch.stats["stall_prompts"] == 0
    time.sleep(0.02)
    frames = drain(env.spy)
    i_a3 = frames.index((0x300, h("A3")))
    assert frames[i_a3 + 1] == (0x740, h("A1 0F 8A FF 32 FF"))     # our params, as A1
    assert frames[i_a3 - 1][1][0] == 0x22 and frames[i_a3 + 2][1][0] == 0x23


def test_module_stops_block_after_its_keepalive_and_is_prompted(engine_env):
    env = engine_env
    r = env.nodes[0].responder
    r.inject_a3_before_frame = 3
    r.stop_block_after_a3 = True
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    ch.send(b"\x1A\x9B")
    assert ch.recv(2.0) == IDENT_1A9B
    assert ch.stats["stall_prompts"] == 1 and ch.stats["inline_a3"] == 1
    time.sleep(0.02)
    frames = drain(env.spy)
    i_a3 = frames.index((0x300, h("A3")))
    assert frames[i_a3 + 1] == (0x740, h("A1 0F 8A FF 32 FF"))
    assert frames[i_a3 + 2] == (0x740, h("B3"))            # prompt: resume from seq 3
    assert frames[i_a3 + 3][1][0] == 0x23


def test_keepalive_exchange_keeps_module_alive(env):
    node = env.add(0x01, 0x740, idle_timeout=0.3)
    ch = env.channel(0x01, keepalive=True, keepalive_idle=0.1)
    ch.connect()
    drain(env.spy)
    time.sleep(0.75)
    assert ch.connected and node.responder.channel_open
    assert ch.stats["keepalives"] >= 4 and ch.stats["keepalive_misses"] == 0
    frames = drain(env.spy)
    a3 = [f for f in frames if f == (0x740, h("A3"))]
    a1 = [f for f in frames if f == (0x300, h("A1 0F 8A FF 4A FF"))]
    assert len(a3) >= 4 and len(a1) >= 4
    assert frames[frames.index(a3[0]) + 1] == (0x300, h("A1 0F 8A FF 4A FF"))
    ch.send(b"\x3E")
    assert ch.recv(1.0) == b"\x7E"


def test_channel_test_returns_peer_params(env):
    env.add(0x01, 0x740, params=Tp20Params(block_size=8, t3=0x4A))
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    assert ch.channel_test() == Tp20Params(block_size=8, t3=0x4A)
    time.sleep(0.02)
    assert drain(env.spy) == [(0x740, h("A3")), (0x300, h("A1 08 8A FF 4A FF"))]
    with pytest.raises(Tp20Error):
        env.channel(0x02, setup_timeout=0.02).channel_test()


def test_module_idle_timeout_a8_closes_channel(env):
    env.add(0x01, 0x740, idle_timeout=0.2)
    ch = env.channel(0x01)                                  # no keepalive
    ch.connect()
    drain(env.spy)
    assert wait_for(lambda: not ch.connected, timeout=1.0)
    time.sleep(0.02)
    assert drain(env.spy) == [(0x300, h("A8")), (0x740, h("A8"))]
    with pytest.raises(Tp20ChannelClosed, match="A8"):
        ch.send(b"\x3E")
    with pytest.raises(Tp20ChannelClosed):
        ch.recv(0.01)
    ch.connect()                                            # explicit reconnect works
    ch.send(b"\x3E")
    assert ch.recv(1.0) == b"\x7E"


def test_tester_disconnect_a8_both_ways(engine_env):
    env = engine_env
    node = env.nodes[0]
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    ch.disconnect()
    assert not ch.connected
    assert wait_for(lambda: not node.responder.channel_open)
    assert node.responder.last_close_reason == "tester sent A8"
    time.sleep(0.02)
    assert drain(env.spy) == [(0x740, h("A8")), (0x300, h("A8"))]
    ch.disconnect()                                         # idempotent
    ch.close()
    with pytest.raises(TransportNotOpen):
        ch.send(b"\x3E")
    assert env.router.endpoints == []


def test_a4_and_a0_from_module_close_channel(engine_env):
    env = engine_env
    evil = env.bus.attach("evil")
    ch = env.channel(0x01)
    ch.connect()
    evil.send(CanFrame(0x300, h("A4")))
    assert wait_for(lambda: not ch.connected)
    with pytest.raises(Tp20ChannelClosed, match="A4"):
        ch.send(b"\x3E")
    env.nodes[0].responder.reset()
    ch.connect()
    evil.send(CanFrame(0x300, h("A0 0F 8A FF 4A FF")))
    assert wait_for(lambda: not ch.connected)
    with pytest.raises(Tp20ChannelClosed, match="A0"):
        ch.recv(0.01)
    evil.close()


def test_d8_refusal_while_channel_open(engine_env):
    env = engine_env
    ch1 = env.channel(0x01)
    ch1.connect()
    ch2 = env.channel(0x01, tester_rx_id=0x301)
    with pytest.raises(Tp20ChannelRefused) as exc:
        ch2.connect()
    assert exc.value.code == 0xD8 and "no resources" in str(exc.value)
    assert exc.value.tester_tx_id == 0x740 and exc.value.logical_address == 0x01
    ch1.disconnect()
    ch2.connect()
    assert ch2.tx_id == 0x740 and ch2.rx_id == 0x301
    ch2.send(b"\x3E")
    assert ch2.recv(1.0) == b"\x7E"


def test_d6_for_unsupported_application_type(engine_env):
    env = engine_env
    raw = env.bus.attach("raw")
    raw.send(CanFrame(0x200, h("01 C0 00 10 00 03 20")))
    f = raw.recv(0.5)
    assert f is not None and f.arbitration_id == 0x201 and f.data[1] == 0xD6
    raw.close()


# ====================================================================== setup retry

def test_setup_retry_on_silence_then_alternate_form(env):
    env.add(0x01, 0x740, require_valid_rx_id=True)          # MED17.5 quirk
    ch = env.channel(0x01, setup_timeout=0.05)
    ch.connect()
    assert ch.setup_form == "alternate" and ch.tx_id == 0x740
    time.sleep(0.02)
    setups = [d for (i, d) in drain(env.spy) if i == 0x200]
    assert setups == [h("01 C0 00 10 00 03 01")] * 3 + [h("01 C0 00 03 00 03 01")]
    ch.send(b"\x3E")
    assert ch.recv(1.0) == b"\x7E"


def test_setup_silent_address_times_out(engine_env):
    env = engine_env
    ch = env.channel(0x02, setup_timeout=0.05, setup_retries=2)
    t0 = time.monotonic()
    with pytest.raises(Tp20Timeout, match="0x02"):
        ch.connect()
    assert 0.2 <= time.monotonic() - t0 < 1.0
    time.sleep(0.02)
    setups = [d for (i, d) in drain(env.spy) if i == 0x200]
    assert setups == [h("02 C0 00 10 00 03 01")] * 2 + [h("02 C0 00 03 00 03 01")] * 2
    assert not ch.connected
    ch.close()


def test_auto_connect_on_first_send(engine_env):
    ch = engine_env.channel(0x01)
    assert not ch.connected
    ch.send(b"\x3E")
    assert ch.connected and ch.recv(1.0) == b"\x7E"
    ch2 = engine_env.channel(0x02, auto_connect=False)
    with pytest.raises(Tp20Error, match="not connected"):
        ch2.send(b"\x3E")


# ============================================================================= probe

def test_probe_addresses(env):
    env.add(0x01, 0x740, name="engine")
    env.add(0x09, 0x7A8, name="eps")
    env.add(0x0A, 0x764, name="haldex")
    env.add(0x1F, 0x32E, name="gateway")
    env.add(0x03, 0x7A0, name="abs-med17-style", require_valid_rx_id=True)

    class Tp16Decoy(SimulatedNode):
        def __init__(self, bus):
            super().__init__("tp16")
            self.transport = bus.attach(self.name)

        def run(self):
            while not self.should_stop:
                f = self.transport.recv(0.02)
                if f is not None and f.arbitration_id == 0x200 and f.data[:2] == h("05 C0"):
                    self.transport.send(CanFrame(0x205, h("05 D0 A1")))

        def on_stopped(self):
            self.transport.close()

    decoy = Tp16Decoy(env.bus)
    decoy.start()
    env.nodes.append(decoy)

    drain(env.spy)
    results = probe_tp20_addresses(env.router, [0x01, 0x02, 0x03, 0x05, 0x09, 0x0A, 0x1F],
                                   gap=0.005, settle=0.15)
    assert {a: (r.status, r.tester_tx_id, r.setup_form) for a, r in results.items()} == {
        0x01: ("open", 0x740, "standard"),
        0x02: ("silent", None, None),
        0x03: ("open", 0x7A0, "alternate"),
        0x05: ("tp16", None, "standard"),
        0x09: ("open", 0x7A8, "standard"),
        0x0A: ("open", 0x764, "standard"),
        0x1F: ("open", 0x32E, "standard"),
    }
    assert results[0x01].raw == h("00 D0 00 03 40 07 01")
    assert results[0x05].raw == h("05 D0 A1")
    assert all(results[a].released for a in (0x01, 0x03, 0x09, 0x0A, 0x1F))
    assert not results[0x02].released and not results[0x05].released
    # Sequential by default (sheet OPEN Q.1 method): every 0xD0 is followed by our A8 on
    # the assigned tx id and the module's A8 before the next 0xC0 goes out, and every
    # setup asks for the same single tester id 0x300.
    frames = drain(env.spy)
    open_at_once = 0
    for arb, data in frames:
        if arb == 0x200:
            assert open_at_once == 0, "a 0xC0 went out while another channel was still open"
            assert data[4:6] == h("00 03")
        elif 0x201 <= arb <= 0x2FF and len(data) == 7 and data[1] == 0xD0:
            open_at_once += 1
        elif arb == 0x300 and data == h("A8"):
            open_at_once -= 1
    assert open_at_once == 0
    for node in env.nodes[:5]:
        assert wait_for(lambda n=node: not n.responder.channel_open), node
        assert node.responder.last_close_reason == "tester sent A8"
    assert env.router.endpoints == []
    # a channel can be opened right after the probe (everything was disconnected)
    ch = env.channel(0x0A)
    ch.connect()
    assert ch.tx_id == 0x764


def test_probe_reports_busy_module(engine_env):
    env = engine_env
    ch = env.channel(0x01)
    ch.connect()
    results = probe_tp20_addresses(env.router, [0x01], tester_rx_id=0x301, gap=0.005, settle=0.1)
    assert results[0x01].status == "busy-d8" and results[0x01].tester_tx_id == 0x740
    assert ch.connected
    ch.send(b"\x3E")
    assert ch.recv(1.0) == b"\x7E"


# ============================================================== adapter echoes

class EchoingFakeCanTransport(FakeCanTransport):
    """A Tactrix-like raw CAN channel: our own frames come back as ordinary frames."""

    def send(self, frame: CanFrame) -> None:
        super().send(frame)
        self._deliver(frame)


def test_echo_of_own_frames_does_not_confuse_receiver():
    env = _Env(transport_cls=EchoingFakeCanTransport)
    try:
        env.add(0x01, 0x740, name="engine")
        ch = env.channel(0x01, keepalive=True, keepalive_idle=0.1)
        ch.connect()
        ch.send(b"\x10\x89")
        assert ch.recv(1.0) == b"\x50\x89"
        ch.send(b"\x1A\x9B")
        assert ch.recv(1.0) == IDENT_1A9B
        ch.send(b"\x3B\x01" + bytes(range(120)))
        assert ch.recv(1.0) == b"\x7B\x01\x00\x7A"
        time.sleep(0.3)                                    # keepalive A3 echoes too
        assert ch.connected and ch.stats["sequence_errors"] == 0
        assert ch.stats["keepalive_misses"] == 0
        assert env.router.stats["dropped_unmatched"] >= ch.stats["tx_frames"]
        ch.disconnect()
        assert not ch.connected
        results = probe_tp20_addresses(env.router, [0x01, 0x02], gap=0.005, settle=0.1)
        assert results[0x01].status == "open" and results[0x02].status == "silent"
    finally:
        env.close()


# ================================================================= node lifecycle

def test_node_restart_forgets_channel(engine_env):
    env = engine_env
    node = env.nodes[0]
    ch = env.channel(0x01)
    ch.connect()
    node.stop()
    assert not node.running and not node.transport.is_open
    node.start()
    assert node.running and not node.responder.channel_open
    ch2 = env.channel(0x01, tester_rx_id=0x302)
    ch2.connect()
    ch2.send(b"\x3E")
    assert ch2.recv(1.0) == b"\x7E"


def test_responder_rejects_bad_handler_and_addresses(env):
    with pytest.raises(TypeError):
        Tp20Responder(env.bus.attach("x"), 0x01, object(), tester_tx_id=0x740)
    with pytest.raises(ValueError):
        Tp20Responder(env.bus.attach("y"), 0x00, kwp_handler, tester_tx_id=0x740)
    with pytest.raises(ValueError):
        Tp20Channel(env.router, 0xF0)
    with pytest.raises(ValueError):
        Tp20Channel(env.router, 0x01, params=Tp20Params(block_size=0x10))


# =========================================================== TransportContext

def _tp20_test_preset(vehicle: SimulatedVehicle) -> None:
    vehicle.add_node(Tp20Node(vehicle.bus, kwp_handler, logical_address=0x01, tester_tx_id=0x740,
                              name="engine-kwp"))


SimulatedVehicle.register_preset_hook("tp20-test", _tp20_test_preset)


@pytest.fixture
def fresh_default_vehicle():
    reset_default_vehicle()
    yield
    reset_default_vehicle()


def test_transport_context_fake_tp20_channel_end_to_end(fresh_default_vehicle):
    with TransportContext("fake", vehicle_preset="tp20-test") as ctx:
        assert ctx.vehicle.node_names() == ["engine-kwp"]
        ch = ctx.tp20_channel(0x01)
        assert isinstance(ch, Tp20Channel) and ch.router is ctx.router
        ch.connect()
        assert ch.tx_id == 0x740 and ch.setup_form == "standard"
        ch.send(b"\x10\x89")
        assert ch.recv(1.0) == b"\x50\x89"
        ch.send(b"\x1A\x9B")
        assert ch.recv(1.0) == IDENT_1A9B
        ch.close()
        assert ctx.router.endpoints == []
        assert not ctx.vehicle.node("engine-kwp").responder.channel_open


def test_transport_context_demo_has_no_tp20_module(fresh_default_vehicle):
    with TransportContext("fake") as ctx:
        ch = ctx.tp20_channel(0x01, setup_timeout=0.02, setup_retries=1)
        with pytest.raises(Tp20Timeout):
            ch.connect()


# ================================================================ review findings

def test_frame_opcode_is_a_function_of_the_index():
    bs = 15
    assert [frame_opcode(i, 18, bs) for i in range(18)] == [0x2] * 14 + [0x0, 0x2, 0x2, 0x1]
    assert [frame_opcode(i, 1, bs) for i in range(1)] == [0x1]
    assert [frame_opcode(i, 15, bs) for i in range(15)] == [0x2] * 14 + [0x1]
    assert [frame_opcode(i, 10, 8) for i in range(10)] == [0x2] * 7 + [0x0, 0x2, 0x1]
    assert frame_opcode(0, 5, 0) == 0x0 and frame_opcode(0, 2, 1) == 0x0   # bs 0 clamps to 1


def test_application_type_table():
    assert APP_TYPE_TEXT == {0x01: "diagnostics (KWP2000)", 0x10: "infotainment communication",
                             0x20: "application protocol", 0x21: "WFS/WIV immobiliser"}
    exc = Tp20ChannelRefused(0xD6, "application type not supported", logical_address=0x01, app=0x20)
    assert "0xD6" in str(exc) and "application protocol" in str(exc) and exc.app == 0x20


def test_not_ready_at_block_boundary_resends_same_pci_and_waits(engine_env):
    """Finding 1/10: a 0x9X on the 15th (block-end, 0x0E) frame must be answered by
    re-sending that very frame with its ACK request after T_WAIT, not by a 0x2E
    duplicate followed by the next block."""
    env = engine_env
    env.nodes[0].responder.not_ready_count = 1
    ch = env.channel(0x01)
    ch.connect()
    drain(env.spy)
    t0 = time.monotonic()
    ch.send(b"\x3B\x01" + bytes(range(120)))               # 18 frames: block end at index 14
    assert time.monotonic() - t0 >= Tp20Channel.T_WAIT
    assert ch.recv(1.0) == b"\x7B\x01\x00\x7A"
    assert ch.stats["naks"] == 1 and ch.stats["retransmissions"] == 1
    time.sleep(0.02)
    frames = drain(env.spy)
    ours = [d[0] for (i, d) in frames if i == 0x740 and (d[0] >> 4) <= 3]
    assert ours == [0x20, 0x21, 0x22, 0x23, 0x24, 0x25, 0x26, 0x27, 0x28, 0x29, 0x2A, 0x2B, 0x2C,
                    0x2D, 0x0E, 0x0E, 0x2F, 0x20, 0x11]
    theirs = [d[0] for (i, d) in frames if i == 0x300 and (d[0] >> 4) in (0x9, 0xB)]
    assert theirs == [0x9F, 0xBF, 0xB2]
    i_nak = frames.index((0x300, h("9F")))
    assert frames[i_nak + 1][1][0] == 0x0E                 # nothing else went out before the retry


class _RawModule(threading.Thread):
    """A scripted module on a raw FakeCanTransport: answers the handshake, then plays
    ``script`` (a list of frames for 0x300) once the A0 arrives, 20 ms apart."""

    def __init__(self, bus: FakeCanBus, script: List[bytes], tester_tx_id: int = 0x740) -> None:
        super().__init__(daemon=True)
        self.transport = bus.attach("raw-module")
        self.script = script
        self.tester_tx_id = tester_tx_id
        self.seen: List[Tuple[int, bytes]] = []
        self.stop_flag = threading.Event()
        self.start()

    def run(self) -> None:
        while not self.stop_flag.is_set():
            f = self.transport.recv(0.05)
            if f is None:
                continue
            self.seen.append((f.arbitration_id, bytes(f.data)))
            if f.arbitration_id == 0x200 and f.data[1] == 0xC0:
                self.transport.send(CanFrame(0x201, h("00 D0 00 03 40 07 01")))
            elif f.arbitration_id == self.tester_tx_id and f.data[0] == 0xA0:
                self.transport.send(CanFrame(0x300, h("A1 0F 8A FF 4A FF")))
                for data in self.script:
                    time.sleep(0.02)
                    self.transport.send(CanFrame(0x300, data))

    def close(self) -> None:
        self.stop_flag.set()
        self.join(1.0)
        self.transport.close()


def test_truncated_and_zero_length_messages_are_refused(env):
    """Finding 2/11: a message shorter than its announced length, or announcing length
    0, is never delivered; it is still ACKed so the module's counter stays in step and
    the next well-formed message gets through."""
    module = _RawModule(env.bus, [h("10 00 10 61 01"), h("11 00 00"), h("12 00 01 7E")])
    try:
        ch = env.channel(0x01, setup_timeout=0.5)
        ch.connect()
        assert ch.recv(1.0) == b"\x7E"                     # only the well-formed one
        assert ch.recv(0.1) is None
        assert ch.stats["malformed_messages"] == 2 and ch.stats["rx_messages"] == 1
        acks = [d for (i, d) in module.seen if i == 0x740 and (d[0] >> 4) == 0xB]
        assert acks == [h("B1"), h("B2"), h("B3")]
    finally:
        module.close()


def test_same_tester_rx_id_is_refused_and_none_allocates(env):
    """Finding 5: two channels on one router may not share a tester receive id (both
    modules would transmit on it); ``tester_rx_id=None`` takes the lowest free id."""
    env.add(0x01, 0x740, name="engine")
    env.add(0x02, 0x7E1, name="dsg")
    ch1 = env.channel(0x01)
    ch1.connect()
    ch2 = env.channel(0x02)                                 # also 0x300
    with pytest.raises(Tp20Error, match="0x300 is already used by tp20-01"):
        ch2.connect()
    assert not ch2.connected and env.nodes[1].responder.stats["setups"] == 0   # refused before any frame
    ch3 = env.channel(0x02, tester_rx_id=None)
    assert ch3.rx_id == 0
    ch3.connect()
    assert ch3.rx_id == 0x301 and ch3.ecu_tx_id == 0x301 and ch3.tx_id == 0x7E1
    assert rx_ids_in_use(env.router) == {0x300: "tp20-01", 0x301: "tp20-02"}
    ch1.send(b"\x1A\x9B")
    ch3.send(b"\x3E")
    assert ch1.recv(1.0) == IDENT_1A9B and ch3.recv(1.0) == b"\x7E"
    assert ch1.stats["sequence_errors"] == 0 and ch3.stats["sequence_errors"] == 0
    ch1.disconnect()                                        # releases 0x300 ...
    assert rx_ids_in_use(env.router) == {0x301: "tp20-02"}
    ch3.disconnect()                                        # ... and the DSG module itself
    ch2.connect()                                           # so the refused channel can take 0x300
    assert ch2.rx_id == 0x300 and ch2.connected
    assert rx_ids_in_use(env.router) == {0x300: "tp20-02"}
    with pytest.raises(Tp20Error, match="already used"):
        probe_tp20_addresses(env.router, [0x01], settle=0.05)       # the probe claims ids too
    assert env.nodes[0].responder.stats["setups"] == 1               # nothing was sent by it
    ch2.close()
    assert rx_ids_in_use(env.router) == {}


def test_concurrent_channels_on_distinct_ids_from_two_threads(env):
    env.add(0x01, 0x740, name="engine")
    env.add(0x02, 0x7E1, name="dsg")
    ch1 = env.channel(0x01, tester_rx_id=0x300)
    ch2 = env.channel(0x02, tester_rx_id=0x301)
    ch1.connect()
    ch2.connect()
    errors: List[str] = []

    def worker(ch: Tp20Channel, label: str) -> None:
        for k in range(20):
            try:
                ch.send(b"\x1A\x9B" if k % 2 else b"\x3B\x01" + bytes(range(60)))
                r = ch.recv(2.0)
                exp = IDENT_1A9B if k % 2 else b"\x7B\x01\x00\x3E"
                if r != exp:
                    errors.append(f"{label}#{k}: {r!r}")
            except Exception as exc:                        # noqa: BLE001 - reported below
                errors.append(f"{label}#{k}: {exc!r}")
                return

    threads = [threading.Thread(target=worker, args=(ch1, "ch1")),
               threading.Thread(target=worker, args=(ch2, "ch2"))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(10)
    assert errors == []
    assert ch1.stats["sequence_errors"] == 0 and ch2.stats["sequence_errors"] == 0
    assert ch1.stats["rx_messages"] == 20 and ch2.stats["rx_messages"] == 20


def test_flush_rx_mid_reply_discards_that_reply_without_phantoms(env):
    """Finding 6: flush_rx() during a multi-frame reply must not turn its tail into
    fabricated messages (TP 2.0 has no first-frame marker); the reply is reassembled
    on its real length and then discarded."""
    env.add(0x01, 0x740, name="engine")
    ch = env.channel(0x01, params=Tp20Params(t3=0x85))      # ask the module for 50 ms spacing
    ch.connect()
    ch.send(b"\x1A\x9B")                                    # 8 frames -> ~0.35 s on the wire
    assert ch.recv(0.1) is None                             # client gives up early ...
    ch.flush_rx()                                           # ... and flushes before its next request
    time.sleep(0.6)
    assert ch.recv(0.0) is None
    assert ch.stats["discarded_messages"] == 1 and ch.stats["rx_messages"] == 0
    assert ch.stats["malformed_messages"] == 0 and ch.stats["sequence_errors"] == 0
    ch.send(b"\x3E")
    assert ch.recv(1.0) == b"\x7E"
    ch.send(b"\x1A\x9B")
    assert ch.recv(1.0) == IDENT_1A9B


class _AbandonResponder(Tp20Responder):
    """First response: send only the first two frames (op 'more'), then forget it."""

    def __init__(self, *args, **kw) -> None:
        super().__init__(*args, **kw)
        self.abandon_next = True

    def send_message(self, payload: bytes) -> bool:
        if not self.abandon_next:
            return super().send_message(payload)
        self.abandon_next = False
        chunks = split_message(payload)
        for i in range(2):
            seq = self.tx_seq
            self._send(bytes([(0x2 << 4) | seq]) + chunks[i])
            self.tx_seq = (seq + 1) & 0xF
            time.sleep(0.01)
        return True


class _NoA1Responder(Tp20Responder):
    """Opens the channel (D0) but ignores the tester's first ``ignore_a0`` A0 frames."""

    def __init__(self, *args, ignore_a0: int = 2, **kw) -> None:
        super().__init__(*args, **kw)
        self.ignore_a0 = ignore_a0

    def handle_frame(self, frame: CanFrame) -> None:
        d = frame.data
        if (self.channel_open and frame.arbitration_id == self.tester_tx_id and d
                and d[0] == 0xA0 and self.ignore_a0 > 0):
            self.ignore_a0 -= 1
            self._last_activity = time.monotonic()
            return
        super().handle_frame(frame)


class _CustomNode(Tp20Node):
    """A Tp20Node around a Tp20Responder subclass."""

    def __init__(self, bus: FakeCanBus, responder_cls, *, logical_address: int, tester_tx_id: int,
                 handler=kwp_handler, name: str = "custom", **responder_kw) -> None:
        SimulatedNode.__init__(self, name)
        self.bus = bus
        self.transport = bus.attach(self.name)
        self.responder = responder_cls(self.transport, logical_address, handler,
                                       tester_tx_id=tester_tx_id, name=self.name, **responder_kw)
        self.logical_address = logical_address
        self.tester_tx_id = tester_tx_id


def test_abandoned_partial_is_dropped_and_next_reply_is_clean(env):
    """Finding 7: a module that stops mid-message and never resumes must not have its
    stale bytes glued to its next message; the partial is prompted once (T1) and
    abandoned after PARTIAL_TIMEOUT_FACTOR x T1 of silence."""
    node = _CustomNode(env.bus, _AbandonResponder, logical_address=0x01, tester_tx_id=0x740,
                       name="engine")
    node.start()
    env.nodes.append(node)
    ch = env.channel(0x01)
    ch.connect()
    ch.send(b"\x1A\x9B")
    t0 = time.monotonic()
    assert ch.recv(0.5) is None
    assert wait_for(lambda: ch.stats["abandoned_partials"] == 1, timeout=0.5)
    assert 0.25 <= time.monotonic() - t0 < 0.6               # abandoned at ~3 x T1, not never
    assert ch.stats["stall_prompts"] == 1
    ch.send(b"\x3E")
    assert ch.recv(1.0) == b"\x7E"
    assert ch.stats["rx_messages"] == 1 and ch.stats["malformed_messages"] == 0


def test_failed_params_handshake_releases_half_open_module(env):
    """Finding 8: after a 0xD0 the module holds a channel; when the A0/A1 step fails the
    tester must send A8 on the assigned tx id before raising, or every retry gets D8."""
    node = _CustomNode(env.bus, _NoA1Responder, logical_address=0x01, tester_tx_id=0x740,
                       name="engine", ignore_a0=2)
    node.start()
    env.nodes.append(node)
    ch = env.channel(0x01, setup_timeout=0.05, setup_retries=2)
    with pytest.raises(Tp20Timeout, match="A1"):
        ch.connect()
    time.sleep(0.05)
    frames = drain(env.spy)
    assert [d for (i, d) in frames if i == 0x740] == [h("A0 0F 8A FF 32 FF")] * 2 + [h("A8")]
    assert (0x300, h("A8")) in frames                        # module confirmed
    assert not node.responder.channel_open and node.responder.last_close_reason == "tester sent A8"
    assert rx_ids_in_use(env.router) == {}            # the claim was released too
    ch.connect()                                             # D0 again, not D8
    assert ch.connected and node.responder.stats["refused"] == 0


def test_concurrent_auto_connect_runs_one_handshake(engine_env):
    """Finding 9: recv() on one thread and send() on another, both auto-connecting a
    fresh channel, must share one handshake (the module sees exactly one 0xC0)."""
    env = engine_env
    node = env.nodes[0]
    for round_ in range(3):
        ch = env.channel(0x01, tester_rx_id=0x300 + round_)
        results: dict = {}

        def rx() -> None:
            try:
                results["rx"] = ch.recv(1.5)
            except Exception as exc:                        # noqa: BLE001
                results["rx"] = exc

        def tx() -> None:
            try:
                ch.send(b"\x3E")
                results["tx"] = "ok"
            except Exception as exc:                        # noqa: BLE001
                results["tx"] = exc

        before = node.responder.stats["setups"]
        a = threading.Thread(target=rx)
        b = threading.Thread(target=tx)
        a.start()
        b.start()
        a.join(5)
        b.join(5)
        assert results.get("tx") == "ok", results
        assert results.get("rx") == b"\x7E", results
        assert node.responder.stats["setups"] == before + 1 and node.responder.stats["refused"] == 0
        ch.close()
        assert wait_for(lambda: not node.responder.channel_open)


def test_probe_concurrency_uses_distinct_ids_and_is_marked_unverified(env):
    """Finding 3: the default probe is sequential (tested in test_probe_addresses);
    ``concurrency`` > 1 keeps that many channels open on distinct tester ids and warns
    once that simultaneous channels are only reported."""
    for addr, tx in ((0x01, 0x740), (0x02, 0x741), (0x03, 0x7A0), (0x1F, 0x32E)):
        env.add(addr, tx, name=f"m{addr:02X}")
    tp20_module._unverified_warned.discard("tp20-probe-concurrent")
    drain(env.spy)
    results = probe_tp20_addresses(env.router, [0x01, 0x02, 0x03, 0x1F], gap=0.005, settle=0.15,
                                   concurrency=4)
    assert "tp20-probe-concurrent" in tp20_module._unverified_warned
    assert {a: (r.status, r.tester_tx_id, r.released) for a, r in results.items()} == {
        0x01: ("open", 0x740, True), 0x02: ("open", 0x741, True),
        0x03: ("open", 0x7A0, True), 0x1F: ("open", 0x32E, True)}
    frames = drain(env.spy)
    requested = [int.from_bytes(d[4:6], "little") & 0x7FF for (i, d) in frames if i == 0x200]
    assert sorted(requested) == [0x300, 0x301, 0x302, 0x303]
    a8_confirmations = sorted(i for (i, d) in frames if 0x300 <= i <= 0x303 and d == h("A8"))
    assert a8_confirmations == [0x300, 0x301, 0x302, 0x303]
    assert rx_ids_in_use(env.router) == {} and env.router.endpoints == []
    for node in env.nodes:
        assert wait_for(lambda n=node: not n.responder.channel_open)
    with pytest.raises(ValueError):
        probe_tp20_addresses(env.router, [0x01], concurrency=17)
