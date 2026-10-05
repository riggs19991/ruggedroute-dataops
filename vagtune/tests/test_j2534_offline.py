"""
J2534 binding tests without Windows or a device.

``_load_library`` is monkeypatched to return a fake PassThru library made of plain
Python callables that honour the ctypes calling convention the binding uses
(``byref`` out-parameters, PASSTHRU_MSG arrays). This exercises the pure-Python
logic: device/channel lifecycle, message packing, filter setup, ioctl config, the
read loops and error mapping. The Linux construct-fail paths are covered too.

``FakeLibrary.PassThruReadMsgs`` follows SAE J2534-1 v04.04 to the letter, because
the binding's correctness on real hardware hinges on it: with ``Timeout > 0`` the
call *blocks* (holding whatever lock the caller holds) until ``pNumMsgs`` messages
were read or the timeout expires, then returns ``ERR_TIMEOUT`` with the partial
count; with ``Timeout == 0`` it returns at once with what is buffered
(``ERR_BUFFER_EMPTY`` when nothing is).
"""

from __future__ import annotations

import ctypes
import platform
import threading
import time
from ctypes import c_ulong

import pytest

from vagtune.transport import TransportContext, make_isotp_link
from vagtune.transport import j2534 as J
from vagtune.transport.base import CanFrame, TransportError, TransportNotOpen
from vagtune.transport.router import CanRouter


def _deref(arg) -> ctypes._SimpleCData:
    """Resolve a ``byref(x)`` argument (or a ctypes object) to the underlying object."""
    return getattr(arg, "_obj", arg)


class FakeLibrary:
    """Minimal PassThru DLL stand-in with scripted RX messages and full call logging."""

    def __init__(self) -> None:
        self.calls: list = []
        self.open_devices: set = set()
        self.channels: dict = {}            # channel id -> protocol
        self.filters: list = []             # (channel, type, mask, pattern, flow, txflags)
        self.written: list = []             # (channel, protocol, txflags, data)
        self.configs: list = []             # (channel, param, value)
        self.ioctls: list = []              # (channel, ioctl id)
        self.rx: dict = {}                  # channel id -> list[(RxStatus, data)]
        self.next_device = 7
        self.next_channel = 100
        self.next_filter = 1
        self.fail_connect_with: int | None = None
        self.vbatt_mv = 12345
        self.read_calls: list = []          # Timeout argument of every PassThruReadMsgs

    # -- helpers used by tests -----------------------------------------------------

    def queue_rx(self, channel_id: int, data: bytes, rx_status: int = 0) -> None:
        self.rx.setdefault(channel_id, []).append((rx_status, data))

    def channel_for(self, protocol: int) -> int:
        return next(cid for cid, proto in self.channels.items() if proto == protocol)

    # -- PassThru API -------------------------------------------------------------

    def PassThruOpen(self, name, device_id_ptr):
        self.calls.append("Open")
        dev = self.next_device
        self.next_device += 1
        _deref(device_id_ptr).value = dev
        self.open_devices.add(dev)
        return J.STATUS_NOERROR

    def PassThruClose(self, device_id):
        self.calls.append("Close")
        self.open_devices.discard(int(getattr(device_id, "value", device_id)))
        return J.STATUS_NOERROR

    def PassThruConnect(self, device_id, protocol, flags, baud, channel_id_ptr):
        self.calls.append(("Connect", int(protocol), int(flags), int(baud)))
        if self.fail_connect_with is not None:
            return self.fail_connect_with
        if int(protocol) in self.channels.values():
            return 0x14  # ERR_CHANNEL_IN_USE
        cid = self.next_channel
        self.next_channel += 1
        self.channels[cid] = int(protocol)
        _deref(channel_id_ptr).value = cid
        return J.STATUS_NOERROR

    def PassThruDisconnect(self, channel_id):
        cid = int(getattr(channel_id, "value", channel_id))
        self.calls.append(("Disconnect", cid))
        self.channels.pop(cid, None)
        return J.STATUS_NOERROR

    def PassThruReadMsgs(self, channel_id, msgs, count_ptr, timeout_ms):
        cid = int(getattr(channel_id, "value", channel_id))
        count = _deref(count_ptr)
        want = count.value
        timeout_ms = int(timeout_ms)
        self.read_calls.append(timeout_ms)
        deadline = time.monotonic() + timeout_ms / 1000.0
        n = 0
        while n < want:
            pending = self.rx.get(cid, [])
            if pending:
                status, data = pending.pop(0)
                m = msgs[n]
                m.ProtocolID = self.channels[cid]
                m.RxStatus = status
                m.DataSize = len(data)
                ctypes.memmove(m.Data, data, len(data))
                n += 1
                continue
            if timeout_ms == 0 or time.monotonic() >= deadline:
                break
            time.sleep(0.001)          # a real DLL blocks here (and releases the GIL)
        count.value = n
        if n == want:
            return J.STATUS_NOERROR
        if timeout_ms == 0:
            return J.STATUS_NOERROR if n else J.ERR_BUFFER_EMPTY
        return J.ERR_TIMEOUT           # partial (possibly empty) batch, pNumMsgs = n

    def PassThruWriteMsgs(self, channel_id, msgs, count_ptr, timeout_ms):
        cid = int(getattr(channel_id, "value", channel_id))
        count = _deref(count_ptr)
        for i in range(count.value):
            m = msgs[i]
            self.written.append((cid, m.ProtocolID, m.TxFlags, bytes(m.Data[:m.DataSize])))
        return J.STATUS_NOERROR

    def PassThruStartMsgFilter(self, channel_id, filter_type, mask_ptr, pattern_ptr, flow_ptr, fid_ptr):
        cid = int(getattr(channel_id, "value", channel_id))

        def data(p):
            if p is None:
                return None
            m = _deref(p)
            return bytes(m.Data[:m.DataSize])

        self.filters.append((cid, int(filter_type), data(mask_ptr), data(pattern_ptr), data(flow_ptr),
                             _deref(mask_ptr).TxFlags))
        _deref(fid_ptr).value = self.next_filter
        self.next_filter += 1
        return J.STATUS_NOERROR

    def PassThruStopMsgFilter(self, channel_id, filter_id):
        self.calls.append(("StopFilter", int(filter_id)))
        return J.STATUS_NOERROR

    def PassThruIoctl(self, channel_id, ioctl_id, input_ptr, output_ptr):
        cid = int(getattr(channel_id, "value", channel_id))
        ioctl_id = int(ioctl_id)
        self.ioctls.append((cid, ioctl_id))
        if ioctl_id == J.SET_CONFIG:
            lst = _deref(input_ptr)
            for i in range(lst.NumOfParams):
                cfg = lst.ConfigPtr[i]
                if cfg.Parameter == J.STMIN_TX:
                    return 0x01  # ERR_NOT_SUPPORTED, like many devices
                self.configs.append((cid, cfg.Parameter, cfg.Value))
        elif ioctl_id == J.READ_VBATT:
            _deref(output_ptr).value = self.vbatt_mv
        return J.STATUS_NOERROR

    def PassThruGetLastError(self, buf):
        buf.value = b"fake detail"
        return J.STATUS_NOERROR


@pytest.fixture
def fake_lib(monkeypatch):
    lib = FakeLibrary()
    monkeypatch.setattr(J, "_load_library", lambda path: lib)
    return lib


def test_device_and_two_channels_share_one_handle(fake_lib):
    dev = J.J2534Device("fake.dll")
    assert not dev.is_open
    can = J.J2534RawCanTransport(device=dev)
    can.open()
    assert dev.is_open and fake_lib.calls.count("Open") == 1
    link = J.J2534IsoTpLink(0x7E0, 0x7E8, device=dev)
    assert fake_lib.calls.count("Open") == 1               # shared device, opened once
    assert sorted(fake_lib.channels.values()) == [J.CAN, J.ISO15765]
    assert len(dev.channels) == 2
    assert dev.read_battery_voltage() == pytest.approx(12.345)

    link.close()
    assert not can._chan is None and can.is_open             # the other channel survives
    assert list(fake_lib.channels.values()) == [J.CAN]
    assert "Close" not in fake_lib.calls                      # shared device stays open
    can.close()
    assert dev.is_open                                        # neither owned the device
    dev.close()
    assert not dev.is_open and fake_lib.calls.count("Close") == 1
    assert fake_lib.channels == {}
    dev.close()                                               # idempotent


def test_raw_can_transport_packing_filter_and_read_loop(fake_lib):
    t = J.J2534RawCanTransport(dll_path="fake.dll")
    with pytest.raises(TransportNotOpen):
        t.send(CanFrame(0x7E0, b"\x00"))
    t.open()
    cid = fake_lib.channel_for(J.CAN)
    assert ("Connect", J.CAN, 0, 500_000) in fake_lib.calls
    # buffers cleared on connect, pass-all filter installed
    assert (cid, J.CLEAR_RX_BUFFER) in fake_lib.ioctls and (cid, J.CLEAR_TX_BUFFER) in fake_lib.ioctls
    assert fake_lib.filters == [(cid, J.PASS_FILTER, b"\x00" * 4, b"\x00" * 4, None, J.ISO15765_FRAME_PAD)]

    t.send(CanFrame(0x7E0, b"\x02\x10\x03"))
    t.send_many([CanFrame(0x7E0, b"\x21\x01"), CanFrame(0x7E1, b"\x22\x02")])
    assert fake_lib.written == [
        (cid, J.CAN, J.ISO15765_FRAME_PAD, b"\x00\x00\x07\xE0\x02\x10\x03"),
        (cid, J.CAN, J.ISO15765_FRAME_PAD, b"\x00\x00\x07\xE0\x21\x01"),
        (cid, J.CAN, J.ISO15765_FRAME_PAD, b"\x00\x00\x07\xE1\x22\x02"),
    ]

    assert t.recv(0.0) is None                                 # ERR_BUFFER_EMPTY -> None
    assert t.recv(0.01) is None                                # ERR_TIMEOUT -> None
    fake_lib.queue_rx(cid, b"\x00\x00")                        # too short to be a frame: dropped
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8\x06\x50\x03\x00\x32\x01\xF4")
    frame = t.recv(0.0)
    assert frame == CanFrame(0x7E8, b"\x06\x50\x03\x00\x32\x01\xF4")
    assert t.recv(0.0) is None
    assert all(tmo == 0 for tmo in fake_lib.read_calls)          # the DLL is never asked to block
    t.set_accept_ids([0x7E8])
    t.close()
    assert fake_lib.calls.count("Close") == 1                  # owned device closed
    with pytest.raises(TransportNotOpen):
        t.recv(0.0)


def test_isotp_link_flow_control_filter_config_and_recv(fake_lib):
    link = J.J2534IsoTpLink(0x7E0, 0x7E8, dll_path="fake.dll", stmin_tx=5)
    cid = fake_lib.channel_for(J.ISO15765)
    assert ("Connect", J.ISO15765, 0, 500_000) in fake_lib.calls
    # our receive-side FC parameters, STMIN_TX rejected by the device without failing
    assert (cid, J.ISO15765_BS, 0) in fake_lib.configs and (cid, J.ISO15765_STMIN, 0) in fake_lib.configs
    assert fake_lib.filters == [(cid, J.FLOW_CONTROL_FILTER, b"\xFF\xFF\xFF\xFF",
                                 b"\x00\x00\x07\xE8", b"\x00\x00\x07\xE0", J.ISO15765_FRAME_PAD)]
    assert link.flow_control_filter_id == 1

    link.send(bytes([0x22, 0xF1, 0x90]))
    assert fake_lib.written == [(cid, J.ISO15765, J.ISO15765_FRAME_PAD, b"\x00\x00\x07\xE0\x22\xF1\x90")]

    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8", J.RX_START_OF_MESSAGE)   # indication, skipped
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE9\x62\x00")                   # other ECU, skipped
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8\x62\xF1\x90" + b"WVW")
    assert link.recv(0.5) == b"\x62\xF1\x90WVW"
    assert link.recv(0.01) is None
    link.flush_rx()
    assert (cid, J.CLEAR_RX_BUFFER) in fake_lib.ioctls[-1:]
    link.close()
    assert fake_lib.channels == {} and fake_lib.calls.count("Close") == 1
    with pytest.raises(TransportNotOpen):
        link.send(b"\x3E\x00")
    link.close()


def test_extended_ids_set_flags(fake_lib):
    t = J.J2534RawCanTransport(dll_path="fake.dll", extended=True)
    t.open()
    assert ("Connect", J.CAN, J.CAN_29BIT_ID, 500_000) in fake_lib.calls
    t.send(CanFrame(0x18DA10F1, b"\x01", is_extended_id=True))
    cid, proto, flags, data = fake_lib.written[0]
    assert flags & J.CAN_29BIT_ID_TX and data[:4] == b"\x18\xDA\x10\xF1"
    t.close()


def test_connect_error_maps_to_j2534error_and_releases_owned_device(fake_lib):
    fake_lib.fail_connect_with = 0x14   # ERR_CHANNEL_IN_USE
    with pytest.raises(J.J2534Error) as exc:
        J.J2534IsoTpLink(0x7E0, 0x7E8, dll_path="fake.dll")
    assert exc.value.code == 0x14 and "ERR_CHANNEL_IN_USE" in str(exc.value)
    assert "fake detail" in str(exc.value)
    assert isinstance(exc.value, TransportError)
    assert fake_lib.calls.count("Close") == 1       # owned device cleaned up on failure


def test_channel_api_validation(fake_lib):
    dev = J.J2534Device("fake.dll")
    ch = dev.connect(J.CAN)
    with pytest.raises(ValueError):
        ch.start_msg_filter(J.FLOW_CONTROL_FILTER, b"\x00" * 4, b"\x00" * 4)           # needs flow bytes
    with pytest.raises(ValueError):
        ch.start_msg_filter(J.PASS_FILTER, b"\x00" * 4, b"\x00" * 4, b"\x00" * 4)      # must not have them
    fid = ch.start_msg_filter(J.PASS_FILTER, b"\x00" * 4, b"\x00" * 4)
    assert ch.filter_ids == [fid]
    ch.stop_msg_filter(fid)
    assert ch.filter_ids == [] and ("StopFilter", fid) in fake_lib.calls
    assert ch.write([], 10) == 0
    ch.disconnect()
    assert not ch.is_connected
    with pytest.raises(TransportNotOpen):
        ch.read(1, 0)
    ch.disconnect()  # idempotent
    dev.close()


def test_mk_msg_rejects_oversize():
    with pytest.raises(ValueError):
        J._mk_msg(J.CAN, bytes(J.PASSTHRU_DATA_SIZE + 1), 0)


@pytest.mark.skipif(platform.system() == "Windows", reason="Linux/macOS failure paths")
def test_construct_fail_cleanly_without_windows(tmp_path, monkeypatch):
    monkeypatch.delenv("VAGTUNE_J2534_DLL", raising=False)
    with pytest.raises(TransportError):
        J.J2534Device()
    with pytest.raises(TransportError):
        J.J2534RawCanTransport()
    t = J.J2534RawCanTransport(dll_path=str(tmp_path / "op20pt32.dll"))
    with pytest.raises(TransportError) as exc:
        t.open()
    assert "Windows" in str(exc.value)
    with pytest.raises(TransportError):
        J.J2534IsoTpLink(0x7E0, 0x7E8, dll_path=str(tmp_path / "op20pt32.dll"))
    assert J.default_dll_path() is None


# ---- review findings: lock convoy, partial batches, leaks, RxStatus, shared channel ----

def test_send_latency_not_stalled_by_router_reader(fake_lib):
    # The router reader polls recv(0.05) forever; with a DLL that blocks for its
    # Timeout, sends from another thread must still complete in microseconds.
    t = J.J2534RawCanTransport(dll_path="fake.dll")
    router = CanRouter(t, name="j2534")
    ep = router.endpoint([0x7E8])
    time.sleep(0.1)
    latencies = []
    t0 = time.monotonic()
    for i in range(20):
        t1 = time.monotonic()
        ep.send(CanFrame(0x7E0, bytes([0x21, i])))
        latencies.append(time.monotonic() - t1)
    total = time.monotonic() - t0
    router.close()
    assert total < 0.1, f"20 sends took {total*1000:.0f} ms (max {max(latencies)*1000:.1f} ms)"
    assert all(tmo == 0 for tmo in fake_lib.read_calls)


def test_device_lock_never_held_while_waiting_for_data(fake_lib):
    dev = J.J2534Device("fake.dll")
    ch = dev.connect(J.CAN)
    acquired = {}

    def reader():
        acquired["msgs"] = ch.read(1, 200)

    t = threading.Thread(target=reader)
    t.start()
    time.sleep(0.05)
    t0 = time.monotonic()
    assert dev.lock.acquire(timeout=0.5)        # must be free while the reader waits
    dev.lock.release()
    assert time.monotonic() - t0 < 0.05
    fake_lib.queue_rx(ch.channel_id.value, b"\x00\x00\x07\xE8\x01")
    t.join(timeout=1.0)
    assert len(acquired["msgs"]) == 1
    dev.close()


def test_channel_read_returns_as_soon_as_one_message_arrives(fake_lib):
    dev = J.J2534Device("fake.dll")
    ch = dev.connect(J.CAN)
    cid = ch.channel_id.value
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8\x01")
    t0 = time.monotonic()
    msgs = ch.read(4, 500)                       # fewer than 4 available: no waiting
    assert len(msgs) == 1 and time.monotonic() - t0 < 0.1
    assert ch.read(4, 0) == []
    t0 = time.monotonic()
    assert ch.read(4, 30) == []                  # empty: waits the timeout, then []
    assert 0.025 <= time.monotonic() - t0 < 0.5
    with pytest.raises(ValueError):
        ch.read(0, 0)
    dev.close()


class PartialTimeoutLibrary(FakeLibrary):
    """Vendor variant: reports ERR_TIMEOUT with a partial count even at Timeout 0."""

    def PassThruReadMsgs(self, channel_id, msgs, count_ptr, timeout_ms):
        rc = super().PassThruReadMsgs(channel_id, msgs, count_ptr, timeout_ms)
        if rc == J.STATUS_NOERROR and _deref(count_ptr).value < 4:
            return J.ERR_TIMEOUT
        return rc


def test_partial_batch_with_err_timeout_is_delivered(monkeypatch):
    lib = PartialTimeoutLibrary()
    monkeypatch.setattr(J, "_load_library", lambda path: lib)
    link = J.J2534IsoTpLink(0x7E0, 0x7E8, dll_path="fake.dll")
    cid = lib.channel_for(J.ISO15765)
    lib.queue_rx(cid, b"\x00\x00\x07\xE8\x62\xF1\x90" + b"WVWZZZAUZLW000001")
    t0 = time.monotonic()
    assert link.recv(0.5) == b"\x62\xF1\x90WVWZZZAUZLW000001"
    assert time.monotonic() - t0 < 0.2
    link.close()


def test_raw_transport_open_failure_releases_owned_device(fake_lib):
    fake_lib.fail_connect_with = 0x14
    t = J.J2534RawCanTransport(dll_path="fake.dll")
    with pytest.raises(J.J2534Error):
        t.open()
    assert fake_lib.calls.count("Close") == 1 and not t.device.is_open and not t.is_open
    # A shared device is left to its owner.
    dev = J.J2534Device("fake.dll")
    dev.open()
    shared = J.J2534RawCanTransport(device=dev)
    with pytest.raises(J.J2534Error):
        shared.open()
    assert dev.is_open and fake_lib.calls.count("Close") == 1
    dev.close()


def test_context_j2534_releases_device_when_connect_fails(fake_lib):
    fake_lib.fail_connect_with = 0x14
    with pytest.raises(TransportError):
        TransportContext("j2534", dll_path="fake.dll")
    assert fake_lib.calls.count("Close") == 1
    fake_lib.fail_connect_with = None
    with TransportContext("j2534", dll_path="fake.dll") as ctx:
        assert ctx.router is not None
    assert fake_lib.calls.count("Close") == 2 and fake_lib.channels == {}


def test_rx_status_flags_are_honoured(fake_lib):
    t = J.J2534RawCanTransport(dll_path="fake.dll")
    t.open()
    cid = fake_lib.channel_for(J.CAN)
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE0", J.RX_TX_INDICATION)          # TxDone: dropped
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE0\x02\x10\x03", J.RX_TX_MSG_TYPE)  # loopback: dropped
    fake_lib.queue_rx(cid, b"\x18\xDA\xF1\x10\x01", J.RX_CAN_29BIT_ID)
    frame = t.recv(0.0)
    assert frame == CanFrame(0x18DAF110, b"\x01", is_extended_id=True) and frame.is_extended_id
    assert t.recv(0.0) is None
    t.close()

    link = J.J2534IsoTpLink(0x7E0, 0x7E8, dll_path="fake.dll")
    cid = fake_lib.channel_for(J.ISO15765)
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8\x62\x00", J.RX_TX_INDICATION)
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8\x62\x00", J.RX_TX_MSG_TYPE)
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8", J.RX_START_OF_MESSAGE)
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8\x62\x01", J.RX_ISO15765_PADDING_ERROR)  # logged, kept
    assert link.recv(0.1) == b"\x62\x01"
    assert link.recv(0.0) is None
    link.close()


def test_shared_iso15765_channel_serves_several_links(fake_lib):
    with TransportContext("j2534-fw", dll_path="fake.dll") as ctx:
        assert ctx.fw_channel is not None and ctx.fw_channel.is_open
        assert list(fake_lib.channels.values()) == [J.ISO15765]
        engine = ctx.isotp_link(0x7E0, 0x7E8)
        gateway = ctx.isotp_link(0x710, 0x77A)            # second live link: no second connect
        assert ("Connect", J.ISO15765, 0, 500_000) in fake_lib.calls
        assert fake_lib.calls.count("Open") == 1 and len(fake_lib.channels) == 1
        cid = fake_lib.channel_for(J.ISO15765)
        assert [(f[3], f[4]) for f in fake_lib.filters] == [
            (b"\x00\x00\x07\xE8", b"\x00\x00\x07\xE0"),
            (b"\x00\x00\x07\x7A", b"\x00\x00\x07\x10"),
        ]
        with pytest.raises(TransportError):
            ctx.isotp_link(0x7E0, 0x7E8)                   # same response id twice
        # A message for the gateway read while the engine link waits is not lost.
        fake_lib.queue_rx(cid, b"\x00\x00\x07\x7A\x50\x03")
        fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8\x50\x03\x00\x32\x01\xF4")
        assert engine.recv(0.5) == b"\x50\x03\x00\x32\x01\xF4"
        assert gateway.recv(0.0) == b"\x50\x03" and gateway.last_rx_id == 0x77A
        engine.send(b"\x3E\x80")
        assert fake_lib.written[-1] == (cid, J.ISO15765, J.ISO15765_FRAME_PAD, b"\x00\x00\x07\xE0\x3E\x80")
        gateway.flush_rx()                                 # shared channel: no CLEAR_RX_BUFFER
        assert (cid, J.CLEAR_RX_BUFFER) not in fake_lib.ioctls[3:]
        engine.close()
        assert ("StopFilter", 1) in fake_lib.calls
        again = ctx.isotp_link(0x7E0, 0x7E8)               # id is free again after close
        again.close()
        gateway.close()
        assert ctx.fw_channel.links == []
    assert fake_lib.channels == {} and fake_lib.calls.count("Close") == 1
    with pytest.raises(TransportNotOpen):
        gateway.recv(0.0)


def test_functional_fw_link_installs_one_filter_per_responder(fake_lib):
    link = J.J2534IsoTpLink(0x7DF, 0x7E8, dll_path="fake.dll", extra_rx_ids=[0x7E9, 0x77A])
    assert link.flow_control_ids == {0x7E8: 0x7E0, 0x7E9: 0x7E1, 0x77A: 0x710}
    assert sorted(link.filter_ids) == [0x77A, 0x7E8, 0x7E9]
    assert [(f[3], f[4]) for f in fake_lib.filters] == [
        (b"\x00\x00\x07\x7A", b"\x00\x00\x07\x10"),
        (b"\x00\x00\x07\xE8", b"\x00\x00\x07\xE0"),
        (b"\x00\x00\x07\xE9", b"\x00\x00\x07\xE1"),
    ]
    cid = fake_lib.channel_for(J.ISO15765)
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE9\x49\x02\x01")
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xE8\x49\x02\x02")
    fake_lib.queue_rx(cid, b"\x00\x00\x07\xEA\x49\x02\x03")        # not ours: dropped
    assert link.recv(0.1) == b"\x49\x02\x01" and link.last_rx_id == 0x7E9
    assert link.recv(0.1) == b"\x49\x02\x02" and link.last_rx_id == 0x7E8
    assert link.recv(0.05) is None and link.channel.dropped_unrouted == 1
    link.close()
    assert fake_lib.calls.count("Close") == 1


def test_extended_id_reaches_j2534_channel_for_every_entry_point(fake_lib):
    link = make_isotp_link("j2534", 0x18DA10F1, 0x18DAF110, dll_path="fake.dll", extended_id=True)
    try:
        assert ("Connect", J.CAN, J.CAN_29BIT_ID, 500_000) in fake_lib.calls
        assert link.extended_id and link.flow_control_ids == {0x18DAF110: 0x18DA10F1}
    finally:
        link.close()
    with TransportContext("j2534-fw", dll_path="fake.dll", extended_id=True) as ctx:
        assert ("Connect", J.ISO15765, J.CAN_29BIT_ID, 500_000) in fake_lib.calls
        fw = ctx.isotp_link(0x18DA10F1, 0x18DAF110)
        assert fake_lib.filters[-1][5] & J.CAN_29BIT_ID_TX
        fw.send(b"\x3E\x00")
        assert fake_lib.written[-1][2] & J.CAN_29BIT_ID_TX
        with pytest.raises(TransportError):
            J.J2534IsoTpLink(0x7E0, 0x7E8, channel=ctx.fw_channel, extended_id=False)
        fw.close()
