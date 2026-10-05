"""
SAE J2534 PassThru binding (Windows).

This talks to a pass-thru DLL (Tactrix OpenPort 2.0 ships ``op20pt32.dll``) through
ctypes. The objects, bottom up:

* :class:`J2534Device` - one opened PassThru device (``PassThruOpen``/``Close``).
  ``connect(protocol, flags, baud)`` returns a :class:`J2534Channel`; a device can
  carry a ``CAN`` channel and an ``ISO15765`` channel at the same time, which is
  how a TP 2.0 link (raw CAN) and a firmware ISO-TP link (flashing) share one cable.

* :class:`J2534Channel` - one protocol channel: ``write``/``read``/``ioctl``/
  ``ioctl_config``/``start_msg_filter``/``stop_msg_filter``/``disconnect``.

* :class:`J2534RawCanTransport` - individual CAN frames via the ``CAN`` protocol.
  Used by the :class:`~vagtune.transport.router.CanRouter` for the "universal" mode
  (software ISO-TP + TP 2.0 on the same bus) and for bus sniffing.

* :class:`J2534IsoTpChannel` - one ``ISO15765`` channel that several links share.
  J2534-1 allows a single channel per protocol per device, so every ISO-TP link on
  a cable must live on the same channel: the channel owns the FLOW_CONTROL filters
  (one per response id) and routes each received message to the link that
  registered that id.

* :class:`J2534IsoTpLink` - a full ISO-TP link via the ``ISO15765`` protocol, where
  the *firmware* performs segmentation and flow control. This is the path you want
  for flashing: STmin/BS are handled on the device, so consecutive frames are not
  bottlenecked by USB latency. ``extra_rx_ids`` gives a functional (0x7DF) link one
  flow-control filter per responder (0x7E8..0x7EF), as ISO 15765-4 requires.

Both public transport classes accept an optional ``device=`` so they can share one
opened :class:`J2534Device`; without it each opens (and closes) its own. A link also
accepts ``channel=`` to join an existing :class:`J2534IsoTpChannel`.

Threading: every DLL call is serialised on ``J2534Device.lock``, but the lock is
**never held while waiting**. ``PassThruReadMsgs`` is always called with
``Timeout = 0`` and the caller sleeps in short slices between polls, so a reader
thread polling an idle bus cannot starve ``send()`` on another thread (TP 2.0 ACKs
and ISO-TP consecutive frames have millisecond budgets). ``RxStatus`` flags are
honoured: loopback / transmit-done indications are dropped, the ISO15765
start-of-message indication is recognised by its flag (not only by its length), and
padding errors are logged.

The DLL is resolved in this order:
  1. explicit ``dll_path`` argument,
  2. ``VAGTUNE_J2534_DLL`` environment variable,
  3. the Windows registry PassThruSupport.04.04 enumeration (first installed device),
  4. the common Tactrix default install path.

Everything here imports cleanly on non-Windows machines (so tests and the CLI's
``--help`` run anywhere); actually opening a device requires Windows + the DLL, and
attempting it elsewhere raises :class:`~vagtune.transport.base.TransportError`.
The pure-Python logic (message packing, filter setup, read loop) is testable
anywhere by monkeypatching :func:`_load_library` to return a fake DLL object (see
``tests/test_j2534_offline.py``).
"""

from __future__ import annotations

import ctypes
import logging
import os
import platform
import threading
import time
from collections import deque
from ctypes import POINTER, Structure, byref, c_char_p, c_long, c_ubyte, c_ulong, c_void_p, create_string_buffer
from typing import Any, Deque, Dict, FrozenSet, Iterable, List, Optional, Sequence, Tuple

from .base import CanFrame, IsoTpLink, RawCanTransport, TransportError, TransportNotOpen
from .isotp import FUNCTIONAL_IDS, FlowControlPolicy, physical_request_id

log = logging.getLogger(__name__)

# ---- J2534 constants -----------------------------------------------------------
CAN = 5
ISO15765 = 6

CAN_500K = 500_000

# Connect flags
CAN_29BIT_ID = 0x00000100

# TxFlags
ISO15765_FRAME_PAD = 0x00000040
CAN_29BIT_ID_TX = 0x00000100

# ---- RxStatus flags (SAE J2534-1 v04.04 section 7.2.3) ----------------------------
# Honoured by J2534RawCanTransport.recv / J2534IsoTpChannel.pump (see _rx_status_accepts).
RX_TX_MSG_TYPE = 0x00000001          # message is a loopback / transmit echo
RX_START_OF_MESSAGE = 0x00000002     # ISO15765: first frame received, data follows later
RX_BREAK = 0x00000004                # J1850 break (never on CAN)
RX_TX_INDICATION = 0x00000008        # transmit done indication
RX_ISO15765_PADDING_ERROR = 0x00000010
RX_ISO15765_ADDR_TYPE = 0x00000080   # extended addressing used
RX_CAN_29BIT_ID = 0x00000100

# Filter types
PASS_FILTER = 0x00000001
BLOCK_FILTER = 0x00000002
FLOW_CONTROL_FILTER = 0x00000003

# Ioctl IDs (SAE J2534-1 v04.04 table)
GET_CONFIG = 0x01
SET_CONFIG = 0x02
READ_VBATT = 0x03
CLEAR_TX_BUFFER = 0x07
CLEAR_RX_BUFFER = 0x08
CLEAR_PERIODIC_MSGS = 0x09
CLEAR_MSG_FILTERS = 0x0A

# SCONFIG parameters
LOOPBACK = 0x03
ISO15765_BS = 0x1E        # block size WE advertise in our flow control (receive side)
ISO15765_STMIN = 0x1F     # STmin WE advertise in our flow control (receive side)
BS_TX = 0x22              # optional: override block size when transmitting
STMIN_TX = 0x23           # optional: override STmin when transmitting (not all devices)

# Return codes
STATUS_NOERROR = 0x00
ERR_TIMEOUT = 0x09
ERR_BUFFER_EMPTY = 0x10
ERR_BUFFER_FULL = 0x11

_ERR_NAMES = {
    0x01: "ERR_NOT_SUPPORTED", 0x02: "ERR_INVALID_CHANNEL_ID", 0x03: "ERR_INVALID_PROTOCOL_ID",
    0x04: "ERR_NULL_PARAMETER", 0x05: "ERR_INVALID_IOCTL_VALUE", 0x06: "ERR_INVALID_FLAGS",
    0x07: "ERR_FAILED", 0x08: "ERR_DEVICE_NOT_CONNECTED", 0x09: "ERR_TIMEOUT",
    0x0A: "ERR_INVALID_MSG", 0x0B: "ERR_INVALID_TIME_INTERVAL", 0x0C: "ERR_EXCEEDED_LIMIT",
    0x0D: "ERR_INVALID_MSG_ID", 0x0E: "ERR_DEVICE_IN_USE", 0x0F: "ERR_INVALID_IOCTL_ID",
    0x10: "ERR_BUFFER_EMPTY", 0x11: "ERR_BUFFER_FULL", 0x12: "ERR_BUFFER_OVERFLOW",
    0x13: "ERR_PIN_INVALID", 0x14: "ERR_CHANNEL_IN_USE", 0x15: "ERR_MSG_PROTOCOL_ID",
    0x16: "ERR_INVALID_FILTER_ID", 0x17: "ERR_NO_FLOW_CONTROL", 0x18: "ERR_NOT_UNIQUE",
    0x19: "ERR_INVALID_BAUDRATE", 0x1A: "ERR_INVALID_DEVICE_ID",
}

PASSTHRU_DATA_SIZE = 4128


class PASSTHRU_MSG(Structure):
    _fields_ = [
        ("ProtocolID", c_ulong),
        ("RxStatus", c_ulong),
        ("TxFlags", c_ulong),
        ("Timestamp", c_ulong),
        ("DataSize", c_ulong),
        ("ExtraDataIndex", c_ulong),
        # c_ubyte, not c_char: ctypes hands a c_char array *field* back as a bytes
        # object cut at the first NUL, and every 11-bit CAN id starts with 00 00, so
        # a c_char Data field reads back empty and every frame would be dropped.
        ("Data", c_ubyte * PASSTHRU_DATA_SIZE),
    ]


class SCONFIG(Structure):
    _fields_ = [("Parameter", c_ulong), ("Value", c_ulong)]


class SCONFIG_LIST(Structure):
    _fields_ = [("NumOfParams", c_ulong), ("ConfigPtr", POINTER(SCONFIG))]


class J2534Error(TransportError):
    def __init__(self, code: int, where: str, detail: str = "") -> None:
        name = _ERR_NAMES.get(code, f"0x{code:02X}")
        msg = f"{where} failed: {name}"
        if detail:
            msg += f" ({detail})"
        super().__init__(msg)
        self.code = code
        self.name = name


def default_dll_path() -> Optional[str]:
    """Best-effort discovery of a J2534 DLL. Returns ``None`` if nothing is found."""
    env = os.environ.get("VAGTUNE_J2534_DLL")
    if env and os.path.exists(env):
        return env

    if platform.system() == "Windows":
        dll = _registry_dll()
        if dll:
            return dll
        tactrix = r"C:\Program Files (x86)\OpenECU\OpenPort 2.0\drivers\openport 2.0\op20pt32.dll"
        if os.path.exists(tactrix):
            return tactrix
    return None


def _registry_dll() -> Optional[str]:  # pragma: no cover - Windows/registry only
    try:
        import winreg  # type: ignore
    except Exception:
        return None
    for root in (winreg.HKEY_LOCAL_MACHINE,):
        for base in (r"SOFTWARE\WOW6432Node\PassThruSupport.04.04", r"SOFTWARE\PassThruSupport.04.04"):
            try:
                with winreg.OpenKey(root, base) as key:
                    i = 0
                    while True:
                        sub = winreg.EnumKey(key, i)
                        with winreg.OpenKey(key, sub) as device:
                            try:
                                func, _ = winreg.QueryValueEx(device, "FunctionLibrary")
                                if func and os.path.exists(func):
                                    return func
                            except FileNotFoundError:
                                pass
                        i += 1
            except FileNotFoundError:
                continue
            except OSError:
                break
    return None


def _load_library(dll_path: str) -> Any:
    """Load the PassThru DLL. Raises :class:`TransportError` off-Windows or on load failure.

    Tests monkeypatch this to return a fake object exposing the ``PassThru*`` callables.
    """
    if platform.system() != "Windows":
        raise TransportError("J2534 pass-thru devices are only supported on Windows")
    if not os.path.exists(dll_path):
        raise TransportError(f"J2534 DLL not found: {dll_path}")
    try:
        # J2534 exports are __stdcall; WinDLL binds that convention on 32-bit
        # Python (on x64 Python stdcall == cdecl, so this is correct there too).
        return ctypes.WinDLL(dll_path)
    except OSError as exc:
        bits = platform.architecture()[0]
        if getattr(exc, "winerror", None) == 193:
            raise TransportError(
                f"{os.path.basename(dll_path)} is not the same bitness as this Python "
                f"({bits}). Most J2534 drivers (e.g. Tactrix op20pt32.dll) are 32-bit: "
                f"run a 32-bit Python, or point --dll at the vendor's 64-bit DLL if one ships."
            ) from exc
        raise TransportError(f"could not load J2534 DLL {dll_path}: {exc}") from exc


class _J2534Dll:
    """Thin wrapper that binds the PassThru functions with their ctypes signatures."""

    def __init__(self, dll_path: str, *, library: Any = None) -> None:
        self._dll = library if library is not None else _load_library(dll_path)
        self._bind()

    def _fn(self, name: str, argtypes: list, restype: Any = c_long) -> Any:
        fn = getattr(self._dll, name)
        # Real ctypes function pointers take argtypes/restype; a fake library made of
        # plain Python callables may not accept attribute assignment - that is fine.
        try:
            fn.argtypes = argtypes
            fn.restype = restype
        except (AttributeError, TypeError):
            pass
        return fn

    def _bind(self) -> None:
        self.Open = self._fn("PassThruOpen", [c_void_p, POINTER(c_ulong)])
        self.Close = self._fn("PassThruClose", [c_ulong])
        self.Connect = self._fn("PassThruConnect", [c_ulong, c_ulong, c_ulong, c_ulong, POINTER(c_ulong)])
        self.Disconnect = self._fn("PassThruDisconnect", [c_ulong])
        self.ReadMsgs = self._fn("PassThruReadMsgs", [c_ulong, POINTER(PASSTHRU_MSG), POINTER(c_ulong), c_ulong])
        self.WriteMsgs = self._fn("PassThruWriteMsgs", [c_ulong, POINTER(PASSTHRU_MSG), POINTER(c_ulong), c_ulong])
        self.StartMsgFilter = self._fn("PassThruStartMsgFilter", [
            c_ulong, c_ulong, POINTER(PASSTHRU_MSG), POINTER(PASSTHRU_MSG),
            POINTER(PASSTHRU_MSG), POINTER(c_ulong),
        ])
        self.StopMsgFilter = self._fn("PassThruStopMsgFilter", [c_ulong, c_ulong])
        self.Ioctl = self._fn("PassThruIoctl", [c_ulong, c_ulong, c_void_p, c_void_p])
        self.GetLastError = self._fn("PassThruGetLastError", [c_char_p])

    def last_error(self) -> str:
        buf = create_string_buffer(80)
        try:
            self.GetLastError(buf)
            return buf.value.decode(errors="replace")
        except Exception:
            return ""


# ============================================================== device + channel

class J2534Device:
    """One opened PassThru device; hands out protocol channels.

    Lifecycle: ``open()`` loads the DLL and calls ``PassThruOpen``; ``connect()``
    creates a channel (``PassThruConnect``) and clears its buffers; ``close()``
    disconnects every channel still attached and calls ``PassThruClose``. All DLL
    calls are serialised on one re-entrant lock because PassThru DLLs are not
    required to be thread-safe - and the lock is never held across a wait (see
    :meth:`J2534Channel.read`). ``read_poll_interval`` is the sleep between two
    ``PassThruReadMsgs(Timeout=0)`` polls while a reader waits for data.
    """

    def __init__(self, dll_path: Optional[str] = None) -> None:
        self.dll_path = dll_path or default_dll_path()
        if not self.dll_path:
            raise TransportError("No J2534 DLL found. Pass dll_path=... or set VAGTUNE_J2534_DLL.")
        self._dll: Optional[_J2534Dll] = None
        self.device_id = c_ulong(0)
        self._opened = False
        self._channels: List["J2534Channel"] = []
        self.lock = threading.RLock()
        self.read_poll_interval = 0.001

    @property
    def is_open(self) -> bool:
        return self._opened

    @property
    def channels(self) -> List["J2534Channel"]:
        with self.lock:
            return list(self._channels)

    @property
    def dll(self) -> _J2534Dll:
        if self._dll is None:
            raise TransportNotOpen("J2534 device is not open")
        return self._dll

    def check(self, rc: int, where: str) -> None:
        if rc != STATUS_NOERROR:
            detail = self._dll.last_error() if self._dll is not None else ""
            raise J2534Error(rc, where, detail)

    def open(self) -> None:
        with self.lock:
            if self._opened:
                return
            dll = _J2534Dll(self.dll_path)
            dll_check = dll.Open(None, byref(self.device_id))
            self._dll = dll
            self.check(dll_check, "PassThruOpen")
            self._opened = True
            log.info("opened J2534 device %d via %s", self.device_id.value, self.dll_path)

    def connect(self, protocol: int, flags: int = 0, baud: int = CAN_500K) -> "J2534Channel":
        """Connect a protocol channel (opening the device first if needed)."""
        with self.lock:
            self.open()
            channel_id = c_ulong(0)
            self.check(self.dll.Connect(self.device_id, protocol, flags, baud, byref(channel_id)),
                       f"PassThruConnect(protocol={protocol})")
            channel = J2534Channel(self, protocol, channel_id.value)
            self._channels.append(channel)
            try:
                channel.ioctl(CLEAR_RX_BUFFER)
                channel.ioctl(CLEAR_TX_BUFFER)
            except TransportError:
                channel.disconnect()
                raise
            log.debug("J2534 channel %d connected (protocol %d, %d bit/s)", channel_id.value, protocol, baud)
            return channel

    def _release(self, channel: "J2534Channel") -> None:
        with self.lock:
            try:
                self._channels.remove(channel)
            except ValueError:
                pass

    def read_battery_voltage(self) -> float:
        """READ_VBATT ioctl (device-level): battery voltage in volts."""
        with self.lock:
            out = c_ulong(0)
            self.check(self.dll.Ioctl(self.device_id, READ_VBATT, None, byref(out)),
                       "PassThruIoctl(READ_VBATT)")
            return out.value / 1000.0

    def close(self) -> None:
        with self.lock:
            if not self._opened:
                return
            for channel in list(self._channels):
                try:
                    channel.disconnect()
                except TransportError as exc:
                    log.debug("channel disconnect during device close: %s", exc)
            try:
                rc = self.dll.Close(self.device_id)
                if rc != STATUS_NOERROR:
                    log.debug("PassThruClose returned %s", _ERR_NAMES.get(rc, hex(rc)))
            finally:
                self._opened = False
                log.info("closed J2534 device %d", self.device_id.value)

    def __enter__(self) -> "J2534Device":
        self.open()
        return self

    def __exit__(self, *exc) -> None:
        self.close()


class J2534Channel:
    """One protocol channel on a :class:`J2534Device`."""

    def __init__(self, device: J2534Device, protocol: int, channel_id: int) -> None:
        self.device = device
        self.protocol = protocol
        self.channel_id = c_ulong(channel_id)
        self._connected = True
        self.filter_ids: List[int] = []

    @property
    def is_connected(self) -> bool:
        return self._connected

    def _require(self) -> _J2534Dll:
        if not self._connected:
            raise TransportNotOpen(f"J2534 channel {self.channel_id.value} is disconnected")
        return self.device.dll

    def ioctl_config(self, param: int, value: int) -> None:
        """SET_CONFIG one SCONFIG parameter."""
        dll = self._require()
        cfg = SCONFIG(Parameter=param, Value=value)
        lst = SCONFIG_LIST(NumOfParams=1, ConfigPtr=ctypes.pointer(cfg))
        with self.device.lock:
            self.device.check(dll.Ioctl(self.channel_id, SET_CONFIG, byref(lst), None),
                              f"PassThruIoctl(SET_CONFIG {param:#x})")

    def ioctl(self, ioctl_id: int, input_ptr: Any = None, output_ptr: Any = None) -> None:
        """Generic PassThruIoctl on this channel (CLEAR_RX_BUFFER etc.)."""
        dll = self._require()
        with self.device.lock:
            self.device.check(dll.Ioctl(self.channel_id, ioctl_id, input_ptr, output_ptr),
                              f"PassThruIoctl({ioctl_id:#x})")

    def start_msg_filter(self, filter_type: int, mask: bytes, pattern: bytes,
                         flow_control: Optional[bytes] = None, *, tx_flags: int = 0) -> int:
        """Install a PASS/BLOCK/FLOW_CONTROL filter; returns the filter id.

        ``mask``/``pattern``/``flow_control`` are the raw message data bytes (4-byte
        CAN id prefix, as the protocol expects). A flow-control filter requires
        ``flow_control``; the others must leave it ``None``.
        """
        dll = self._require()
        if (filter_type == FLOW_CONTROL_FILTER) != (flow_control is not None):
            raise ValueError("flow_control bytes are required for (and only for) FLOW_CONTROL_FILTER")
        mask_msg = _mk_msg(self.protocol, mask, tx_flags)
        patt_msg = _mk_msg(self.protocol, pattern, tx_flags)
        flow_msg = _mk_msg(self.protocol, flow_control, tx_flags) if flow_control is not None else None
        fid = c_ulong(0)
        with self.device.lock:
            self.device.check(
                dll.StartMsgFilter(self.channel_id, filter_type, byref(mask_msg), byref(patt_msg),
                                   byref(flow_msg) if flow_msg is not None else None, byref(fid)),
                f"PassThruStartMsgFilter(type={filter_type})",
            )
        self.filter_ids.append(fid.value)
        return fid.value

    def stop_msg_filter(self, filter_id: int) -> None:
        dll = self._require()
        with self.device.lock:
            self.device.check(dll.StopMsgFilter(self.channel_id, filter_id), "PassThruStopMsgFilter")
        if filter_id in self.filter_ids:
            self.filter_ids.remove(filter_id)

    def write(self, msgs: Sequence[PASSTHRU_MSG], timeout_ms: int) -> int:
        """PassThruWriteMsgs; returns how many messages the driver accepted."""
        dll = self._require()
        n = len(msgs)
        if n == 0:
            return 0
        arr = (PASSTHRU_MSG * n)(*msgs)
        count = c_ulong(n)
        with self.device.lock:
            self.device.check(dll.WriteMsgs(self.channel_id, arr, byref(count), timeout_ms),
                              "PassThruWriteMsgs")
        return count.value

    def read(self, max_msgs: int, timeout_ms: int) -> List[PASSTHRU_MSG]:
        """Return up to ``max_msgs`` received messages, waiting at most ``timeout_ms``
        for the *first* one. An empty list means nothing arrived in time.

        Protocol behaviour this is built around (SAE J2534-1 v04.04 PassThruReadMsgs):
        with a non-zero Timeout the DLL **blocks** until ``pNumMsgs`` messages were
        read or the timeout expires, and then returns ``ERR_TIMEOUT`` with
        ``pNumMsgs`` set to the number actually read. Two things follow:

        * the DLL is only ever asked with ``Timeout = 0`` (returns at once with
          whatever is buffered), and the wait happens here, in short sleeps *outside*
          the device lock - a reader thread polling an idle bus must not hold the
          lock for 50 ms at a time and starve every ``send()``;
        * a partial batch (``ERR_TIMEOUT``/``ERR_BUFFER_EMPTY`` with a non-zero count,
          which some vendor DLLs produce even at Timeout 0) is returned, never
          discarded, so a single response is not lost because fewer than
          ``max_msgs`` messages were available.
        """
        dll = self._require()
        if max_msgs < 1:
            raise ValueError("max_msgs must be >= 1")
        deadline = time.monotonic() + max(0, timeout_ms) / 1000.0
        poll = self.device.read_poll_interval
        arr = (PASSTHRU_MSG * max_msgs)()
        while True:
            count = c_ulong(max_msgs)
            with self.device.lock:
                rc = dll.ReadMsgs(self.channel_id, arr, byref(count), 0)
                if rc not in (STATUS_NOERROR, ERR_BUFFER_EMPTY, ERR_TIMEOUT):
                    self.device.check(rc, "PassThruReadMsgs")
            n = min(int(count.value), max_msgs)
            if n > 0:
                return [arr[i] for i in range(n)]
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                return []
            time.sleep(min(poll, remaining))

    def disconnect(self) -> None:
        if not self._connected:
            return
        try:
            with self.device.lock:
                rc = self.device.dll.Disconnect(self.channel_id)
                if rc != STATUS_NOERROR:
                    log.debug("PassThruDisconnect returned %s", _ERR_NAMES.get(rc, hex(rc)))
        finally:
            self._connected = False
            self.device._release(self)

    def __repr__(self) -> str:
        return f"<J2534Channel id={self.channel_id.value} protocol={self.protocol} connected={self._connected}>"


# ===================================================================== messages

def _mk_msg(protocol: int, data: bytes, tx_flags: int) -> PASSTHRU_MSG:
    if len(data) > PASSTHRU_DATA_SIZE:
        raise ValueError(f"PASSTHRU_MSG data too long ({len(data)} > {PASSTHRU_DATA_SIZE})")
    m = PASSTHRU_MSG()
    m.ProtocolID = protocol
    m.TxFlags = tx_flags
    m.DataSize = len(data)
    ctypes.memmove(m.Data, data, len(data))
    return m


def _msg_data(m: PASSTHRU_MSG) -> bytes:
    return bytes(m.Data[:m.DataSize])


def _id_bytes(arb_id: int, extended: bool) -> bytes:
    return arb_id.to_bytes(4, "big")  # J2534 CAN/ISO15765 always use a 4-byte ID prefix


_RX_DROP_MASK = RX_TX_MSG_TYPE | RX_TX_INDICATION


def _rx_status_accepts(rx_status: int, where: str) -> bool:
    """RxStatus policy shared by the CAN and ISO15765 receive paths.

    * ``TX_MSG_TYPE`` (loopback echo of our own transmission) and ``TX_INDICATION``
      (transmit-done notice) are not bus traffic: dropped.
    * ``ISO15765_PADDING_ERROR`` is logged; the message itself is still delivered
      (the firmware already reassembled it).
    """
    if rx_status & _RX_DROP_MASK:
        log.debug("%s: dropping %s message (RxStatus 0x%X)", where,
                  "loopback" if rx_status & RX_TX_MSG_TYPE else "tx-indication", rx_status)
        return False
    if rx_status & RX_ISO15765_PADDING_ERROR:
        log.warning("%s: ISO15765 padding error reported by the device (RxStatus 0x%X)", where, rx_status)
    return True


# =================================================================== transports

class J2534RawCanTransport(RawCanTransport):
    """Frame-level CAN over a J2534 device (``CAN`` protocol).

    Pass ``device=`` to share an already-created :class:`J2534Device` with another
    transport (e.g. a :class:`J2534IsoTpLink` on the same cable); the transport then
    leaves the device open when it closes. Without it the transport opens its own
    device and closes it in :meth:`close` - and also when :meth:`open` fails half
    way (a ``PassThruConnect`` error must not leave the device ``PassThruOpen``'d,
    or the next attempt fails with ``ERR_DEVICE_IN_USE`` until the process exits).

    Receive path: messages are read in batches (``READ_BATCH``) into a local buffer
    and handed out one frame per :meth:`recv`; loopback/TX-indication messages are
    dropped per their ``RxStatus``; a 29-bit id is flagged from ``RX_CAN_29BIT_ID``.
    """

    READ_BATCH = 32

    def __init__(self, dll_path: Optional[str] = None, bitrate: int = CAN_500K,
                 extended: bool = False, *, device: Optional[J2534Device] = None) -> None:
        super().__init__(bitrate=bitrate)
        self.device = device if device is not None else J2534Device(dll_path)
        self._owns_device = device is None
        self.dll_path = self.device.dll_path
        self.extended = extended
        self._tx_flags = ISO15765_FRAME_PAD | (CAN_29BIT_ID_TX if extended else 0)
        self._chan: Optional[J2534Channel] = None
        self._accept: List[int] = []
        self._rx_buf: Deque[PASSTHRU_MSG] = deque()

    def open(self) -> None:
        if self._open:
            return
        self.device.open()
        flags = CAN_29BIT_ID if self.extended else 0
        chan: Optional[J2534Channel] = None
        try:
            chan = self.device.connect(CAN, flags, self.bitrate)
            self._chan = chan
            self._install_pass_all_filter()
        except Exception:
            self._chan = None
            if chan is not None:
                try:
                    chan.disconnect()
                except TransportError as exc:
                    log.debug("disconnect after failed open reported %s", exc)
            if self._owns_device:
                self.device.close()
            raise
        self._rx_buf.clear()
        self._open = True
        log.info("opened J2534 CAN channel via %s", self.dll_path)

    def _install_pass_all_filter(self) -> None:
        # A CAN channel needs at least one PASS filter or it reads nothing.
        assert self._chan is not None
        self._chan.start_msg_filter(PASS_FILTER, b"\x00\x00\x00\x00", b"\x00\x00\x00\x00",
                                    tx_flags=self._tx_flags)

    def close(self) -> None:
        if not self._open:
            return
        try:
            if self._chan is not None:
                self._chan.disconnect()
        finally:
            self._chan = None
            self._open = False
            self._rx_buf.clear()
            if self._owns_device:
                self.device.close()

    def _channel(self) -> J2534Channel:
        if not self._open or self._chan is None:
            raise TransportNotOpen("J2534 CAN channel not open")
        return self._chan

    def send(self, frame: CanFrame) -> None:
        chan = self._channel()
        payload = _id_bytes(frame.arbitration_id, frame.is_extended_id) + frame.data
        chan.write([_mk_msg(CAN, payload, self._tx_flags)], timeout_ms=100)

    def send_many(self, frames: Sequence[CanFrame]) -> None:
        chan = self._channel()
        msgs = [
            _mk_msg(CAN, _id_bytes(f.arbitration_id, f.is_extended_id) + f.data, self._tx_flags)
            for f in frames
        ]
        if msgs:
            chan.write(msgs, timeout_ms=200)

    def _accept_rx_status(self, rx_status: int) -> bool:
        """Receive-path RxStatus policy; see :func:`_rx_status_accepts`."""
        return _rx_status_accepts(rx_status, "J2534 CAN")

    def _frame_from_msg(self, m: PASSTHRU_MSG) -> Optional[CanFrame]:
        if not self._accept_rx_status(m.RxStatus):
            return None
        raw = _msg_data(m)
        if len(raw) < 4:
            log.debug("J2534 CAN: dropping %d-byte message (no id prefix)", len(raw))
            return None
        arb = int.from_bytes(raw[:4], "big")
        extended = self.extended or bool(m.RxStatus & RX_CAN_29BIT_ID) or arb > 0x7FF
        return CanFrame(arb, raw[4:], is_extended_id=extended)

    def recv(self, timeout: float) -> Optional[CanFrame]:
        chan = self._channel()
        deadline = time.monotonic() + max(0.0, timeout)
        while True:
            if not self._rx_buf:
                remaining_ms = int(max(0.0, deadline - time.monotonic()) * 1000)
                msgs = chan.read(self.READ_BATCH, remaining_ms)
                if not msgs:
                    return None
                self._rx_buf.extend(msgs)
            frame = self._frame_from_msg(self._rx_buf.popleft())
            if frame is not None:
                return frame

    def flush_rx(self) -> None:
        self._rx_buf.clear()
        if self._open and self._chan is not None:
            self._chan.ioctl(CLEAR_RX_BUFFER)

    def set_accept_ids(self, arbitration_ids: Iterable[int]) -> None:
        # The pass-all filter already admits everything; software filtering in the
        # ISO-TP layer / router handles narrowing. Recorded for completeness.
        self._accept = list(arbitration_ids)


class J2534IsoTpChannel:
    """One ``ISO15765`` channel on a device, shared by any number of :class:`J2534IsoTpLink`.

    J2534-1 permits one channel per protocol per device, so a keepalive link on the
    engine and an identify link on the gateway (autoscan, a GUI) must share this
    object. It owns the channel and its FLOW_CONTROL filters - one per response id,
    whose flow-control id is the responder's *physical* request id (so a functional
    0x7DF link collects 0x7E8..0x7EF, each with its own FC) - and routes every
    received message to the link that registered that response id.

    There is no reader thread: whichever link is waiting in ``recv()`` calls
    :meth:`pump`, which reads a batch (``PassThruReadMsgs`` with Timeout 0, the wait
    happens in :meth:`J2534Channel.read` outside the device lock) and delivers each
    message to its link's inbox. A link waiting for its own response therefore also
    feeds the other links; the device lock keeps concurrent pumps from two threads
    safe, and the inbox queues are locked.

    ``stmin_tx`` is the optional STMIN_TX override (best effort; many devices reject
    it). ``flush_rx`` on a shared channel must not clear the device buffer (it holds
    other links' traffic); links drain their own inbox instead.
    """

    READ_BATCH = 8

    def __init__(self, device: J2534Device, *, bitrate: int = CAN_500K, extended: bool = False,
                 tx_padding: bool = True, stmin_tx: int = 0, owns_device: bool = False) -> None:
        self.device = device
        self.bitrate = bitrate
        self.extended = extended
        self.tx_flags = ISO15765_FRAME_PAD if tx_padding else 0
        if extended:
            self.tx_flags |= CAN_29BIT_ID_TX
        self.stmin_tx = stmin_tx
        self._owns_device = owns_device
        self.chan: Optional[J2534Channel] = None
        self._lock = threading.Lock()
        self._routes: Dict[int, "J2534IsoTpLink"] = {}
        self.dropped_unrouted = 0

    @property
    def is_open(self) -> bool:
        return self.chan is not None and self.chan.is_connected

    @property
    def links(self) -> List["J2534IsoTpLink"]:
        with self._lock:
            return list(dict.fromkeys(self._routes.values()))

    def open(self) -> None:
        if self.is_open:
            return
        self.device.open()
        flags = CAN_29BIT_ID if self.extended else 0
        chan: Optional[J2534Channel] = None
        try:
            chan = self.device.connect(ISO15765, flags, self.bitrate)
            # Receive side: tell the ECU it may blast consecutive frames at us with no
            # block limit and no inter-frame gap (we are a laptop; we can keep up).
            for param, value in ((ISO15765_BS, 0), (ISO15765_STMIN, 0)):
                try:
                    chan.ioctl_config(param, value)
                except J2534Error as exc:
                    log.debug("device rejected config %#x=%d (%s); using firmware default",
                              param, value, exc)
            # Transmit side: honour the ECU's requested STmin by default. STMIN_TX is an
            # optional override some devices support for ECUs that ask for a slower rate
            # than they can really take (common on older VAG TCUs). Best-effort only.
            if self.stmin_tx:
                try:
                    chan.ioctl_config(STMIN_TX, self.stmin_tx)
                except J2534Error:
                    log.debug("device does not support STMIN_TX override")
        except Exception:
            if chan is not None:
                try:
                    chan.disconnect()
                except TransportError as exc:
                    log.debug("disconnect after failed open reported %s", exc)
            if self._owns_device:
                self.device.close()
            raise
        self.chan = chan
        log.info("opened J2534 ISO15765 channel via %s", self.device.dll_path)

    def _channel(self) -> J2534Channel:
        if self.chan is None or not self.chan.is_connected:
            raise TransportNotOpen("J2534 ISO-TP channel not open")
        return self.chan

    # -- link registry ---------------------------------------------------------------

    def attach(self, link: "J2534IsoTpLink") -> Dict[int, int]:
        """Register ``link`` for its response ids; returns ``{rx_id: filter_id}``.

        Each response id gets a FLOW_CONTROL filter (mask FFFFFFFF, pattern rx_id,
        flow = that responder's physical request id). Two live links cannot claim the
        same response id: the device would reject the duplicate filter, and the
        message could only go to one of them anyway.
        """
        chan = self._channel()
        with self._lock:
            for rid in link.accept_ids:
                owner = self._routes.get(rid)
                if owner is not None:
                    raise TransportError(
                        f"response id 0x{rid:X} already belongs to live link {owner!r} on this "
                        f"ISO15765 channel; close it before opening another link to that module"
                    )
            installed: Dict[int, int] = {}
            try:
                for rid in sorted(link.accept_ids):
                    installed[rid] = chan.start_msg_filter(
                        FLOW_CONTROL_FILTER,
                        b"\xFF\xFF\xFF\xFF",
                        _id_bytes(rid, self.extended),
                        _id_bytes(link.flow_control_ids[rid], self.extended),
                        tx_flags=self.tx_flags,
                    )
            except Exception:
                for fid in installed.values():
                    try:
                        chan.stop_msg_filter(fid)
                    except TransportError as exc:
                        log.debug("filter rollback reported %s", exc)
                raise
            for rid in link.accept_ids:
                self._routes[rid] = link
            return installed

    def detach(self, link: "J2534IsoTpLink") -> None:
        with self._lock:
            for rid, owner in list(self._routes.items()):
                if owner is link:
                    del self._routes[rid]
        chan = self.chan
        if chan is not None and chan.is_connected:
            for fid in link.filter_ids.values():
                try:
                    chan.stop_msg_filter(fid)
                except TransportError as exc:
                    log.debug("stopping filter %d on link close reported %s", fid, exc)

    # -- data path -------------------------------------------------------------------

    def write(self, data: bytes) -> None:
        self._channel().write([_mk_msg(ISO15765, data, self.tx_flags)], timeout_ms=2000)

    def pump(self, timeout: float) -> int:
        """Read one batch (waiting up to ``timeout`` for the first message) and route it.

        Returns the number of payloads delivered to link inboxes.
        """
        chan = self._channel()
        msgs = chan.read(self.READ_BATCH, int(max(0.0, timeout) * 1000))
        delivered = 0
        for m in msgs:
            if not _rx_status_accepts(m.RxStatus, "J2534 ISO15765"):
                continue
            raw = _msg_data(m)
            if len(raw) < 4:
                continue
            if m.RxStatus & RX_START_OF_MESSAGE or len(raw) == 4:
                # The firmware announces a First Frame with a zero-length indication
                # (RxStatus START_OF_MESSAGE, DataSize 4); the reassembled payload
                # follows as its own message. The length check keeps DLLs that forget
                # the flag from producing an empty payload.
                continue
            arb = int.from_bytes(raw[:4], "big")
            with self._lock:
                link = self._routes.get(arb)
            if link is None:
                self.dropped_unrouted += 1
                log.debug("J2534 ISO15765: no link for response id 0x%X; message dropped", arb)
                continue
            link._deliver(arb, raw[4:])
            delivered += 1
        return delivered

    def clear_device_buffer(self) -> None:
        self._channel().ioctl(CLEAR_RX_BUFFER)

    # -- lifecycle -------------------------------------------------------------------

    def close(self) -> None:
        """Disconnect the channel (every attached link becomes unusable) and close the
        device if this channel opened it. Idempotent."""
        chan = self.chan
        self.chan = None
        with self._lock:
            links = list(dict.fromkeys(self._routes.values()))
            self._routes.clear()
        for link in links:
            link._mark_closed()
        try:
            if chan is not None:
                chan.disconnect()
        finally:
            if self._owns_device:
                self.device.close()

    def __enter__(self) -> "J2534IsoTpChannel":
        self.open()
        return self

    def __exit__(self, *exc) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<J2534IsoTpChannel open={self.is_open} links={len(self.links)}>"


class J2534IsoTpLink(IsoTpLink):
    """ISO-TP via the J2534 ``ISO15765`` protocol (device-side segmentation).

    The link lives on a :class:`J2534IsoTpChannel`. Pass ``channel=`` to join one
    that other links share (what :class:`~vagtune.transport.context.TransportContext`
    does); otherwise the link creates a private channel - on ``device=`` if given
    (left open on close) or on a device it opens and closes itself.

    ``extra_rx_ids`` widens the link to several responders (functional addressing:
    ``tx_id=0x7DF``, ``extra_rx_ids=range(0x7E9, 0x7F0)``); each gets its own
    flow-control filter and :attr:`last_rx_id` names the responder of the payload
    :meth:`recv` returned. ``flow_control_ids`` overrides the default FC pairing
    (see :func:`vagtune.transport.isotp.physical_request_id`).
    """

    INBOX_LIMIT = 256

    def __init__(
        self,
        tx_id: int,
        rx_id: int,
        *,
        dll_path: Optional[str] = None,
        extended_id: bool = False,
        bitrate: int = CAN_500K,
        tx_padding: bool = True,
        stmin_tx: int = 0,
        device: Optional[J2534Device] = None,
        channel: Optional[J2534IsoTpChannel] = None,
        extra_rx_ids: Iterable[int] = (),
        flow_control_ids: FlowControlPolicy = None,
    ) -> None:
        super().__init__(tx_id, rx_id, extended_id=extended_id)
        self.extra_rx_ids: FrozenSet[int] = frozenset(int(i) for i in extra_rx_ids)
        self.accept_ids: FrozenSet[int] = frozenset({rx_id}) | self.extra_rx_ids
        self.is_functional = tx_id in FUNCTIONAL_IDS
        self.flow_control_ids: Dict[int, int] = self._resolve_flow_control_ids(flow_control_ids)
        self.last_rx_id: Optional[int] = None
        self.filter_ids: Dict[int, int] = {}
        self._inbox: Deque[Tuple[int, bytes]] = deque()
        self._inbox_lock = threading.Lock()
        self.dropped = 0
        self._closed = False

        if channel is not None:
            if channel.extended != extended_id:
                raise TransportError("link extended_id does not match the shared channel's id width")
            self.channel = channel
            self._owns_channel = False
        else:
            dev = device if device is not None else J2534Device(dll_path)
            self.channel = J2534IsoTpChannel(dev, bitrate=bitrate, extended=extended_id,
                                             tx_padding=tx_padding, stmin_tx=stmin_tx,
                                             owns_device=device is None)
            self._owns_channel = True
        self.device = self.channel.device
        self.dll_path = self.device.dll_path
        self.bitrate = self.channel.bitrate
        self.stmin_tx = self.channel.stmin_tx
        try:
            self.channel.open()
            self.filter_ids = self.channel.attach(self)
        except Exception:
            if self._owns_channel:
                self.channel.close()
            raise

    def _resolve_flow_control_ids(self, policy: FlowControlPolicy) -> Dict[int, int]:
        table: Dict[int, int] = {}
        for rid in sorted(self.accept_ids):
            target: Optional[int] = None
            if policy is not None:
                target = policy.get(rid) if hasattr(policy, "get") else policy(rid)  # type: ignore[union-attr]
            if target is None:
                if rid == self.rx_id and not self.is_functional:
                    target = self.tx_id
                else:
                    target = physical_request_id(rid)
                    if target is None:
                        log.debug("no physical request id known for responder 0x%X; "
                                  "flow control filter will use tx id 0x%X", rid, self.tx_id)
                        target = self.tx_id
            table[rid] = int(target)
        return table

    @property
    def flow_control_filter_id(self) -> Optional[int]:
        """The FLOW_CONTROL filter id bound to ``rx_id`` (``None`` once closed)."""
        return self.filter_ids.get(self.rx_id)

    @property
    def is_open(self) -> bool:
        return not self._closed and self.channel.is_open

    def _require_open(self) -> J2534IsoTpChannel:
        if self._closed or not self.channel.is_open:
            raise TransportNotOpen("J2534 ISO-TP channel not open")
        return self.channel

    # -- inbox (fed by J2534IsoTpChannel.pump) ------------------------------------------

    def _deliver(self, arbitration_id: int, payload: bytes) -> None:
        with self._inbox_lock:
            if len(self._inbox) >= self.INBOX_LIMIT:
                self._inbox.popleft()
                self.dropped += 1
                log.debug("%r: inbox overflow, dropped oldest payload (total %d)", self, self.dropped)
            self._inbox.append((arbitration_id, payload))

    def _take(self) -> Optional[Tuple[int, bytes]]:
        with self._inbox_lock:
            return self._inbox.popleft() if self._inbox else None

    def _mark_closed(self) -> None:
        self._closed = True
        self.filter_ids = {}

    # -- IsoTpLink API ---------------------------------------------------------------------

    def send(self, payload: bytes) -> None:
        chan = self._require_open()
        if not payload:
            raise ValueError("ISO-TP payload must be at least one byte")
        chan.write(_id_bytes(self.tx_id, self.extended_id) + payload)

    def recv(self, timeout: float) -> Optional[bytes]:
        """Receive one complete payload addressed to one of :attr:`accept_ids`.

        Payloads for *other* links on the shared channel that the pump reads while
        this link waits are delivered to those links, not lost.
        """
        chan = self._require_open()
        deadline = time.monotonic() + max(0.0, timeout)
        first = True
        while True:
            item = self._take()
            if item is not None:
                self.last_rx_id, payload = item
                return payload
            remaining = deadline - time.monotonic()
            if remaining <= 0 and not first:
                return None
            first = False
            chan.pump(max(0.0, remaining))
            if self._closed:
                raise TransportNotOpen("J2534 ISO-TP channel closed while receiving")

    def flush_rx(self) -> None:
        """Drop buffered payloads for this link.

        A private channel also clears the device's receive buffer (CLEAR_RX_BUFFER);
        a shared one must not (it holds other links' traffic), so stale messages are
        pumped into their inboxes first and only this inbox is emptied.
        """
        if self._closed or not self.channel.is_open:
            return
        if self._owns_channel:
            self.channel.clear_device_buffer()
        else:
            self.channel.pump(0.0)
        with self._inbox_lock:
            self._inbox.clear()

    def close(self) -> None:
        if self._closed:
            return
        try:
            if self._owns_channel:
                self.channel.close()
            else:
                self.channel.detach(self)
        finally:
            self._mark_closed()
            with self._inbox_lock:
                self._inbox.clear()

    def __repr__(self) -> str:
        extra = f" +{len(self.extra_rx_ids)}" if self.extra_rx_ids else ""
        return f"<J2534IsoTpLink tx=0x{self.tx_id:X} rx=0x{self.rx_id:X}{extra}>"
