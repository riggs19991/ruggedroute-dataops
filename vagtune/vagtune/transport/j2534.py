"""
SAE J2534 PassThru binding (Windows).

This talks to a pass-thru DLL (Tactrix OpenPort 2.0 ships ``op20pt32.dll``) through
ctypes. Two things live here:

* :class:`J2534RawCanTransport` - individual CAN frames via the ``CAN`` protocol.
  Useful for bus sniffing and the software-ISO-TP fallback.

* :class:`J2534IsoTpLink` - a full ISO-TP link via the device's ``ISO15765``
  protocol, where the *firmware* performs segmentation and flow control. This is
  the path you want for flashing: STmin/BS are handled on the device, so consecutive
  frames are not bottlenecked by USB latency.

The DLL is resolved in this order:
  1. explicit ``dll_path`` argument,
  2. ``VAGTUNE_J2534_DLL`` environment variable,
  3. the Windows registry PassThruSupport.04.04 enumeration (first installed device),
  4. the common Tactrix default install path.

Everything here imports cleanly on non-Windows machines (so tests and the CLI's
``--help`` run anywhere); actually opening a device requires Windows + the DLL.
"""

from __future__ import annotations

import ctypes
import logging
import os
import platform
import time
from ctypes import POINTER, Structure, byref, c_char, c_char_p, c_long, c_ulong, c_void_p, create_string_buffer
from typing import Iterable, List, Optional

from .base import CanFrame, IsoTpLink, RawCanTransport, TransportError, TransportNotOpen, TransportTimeout

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

# Filter types
PASS_FILTER = 0x00000001
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


class PASSTHRU_MSG(Structure):
    _fields_ = [
        ("ProtocolID", c_ulong),
        ("RxStatus", c_ulong),
        ("TxFlags", c_ulong),
        ("Timestamp", c_ulong),
        ("DataSize", c_ulong),
        ("ExtraDataIndex", c_ulong),
        ("Data", c_char * 4128),
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


class _J2534Dll:
    """Thin ctypes wrapper that loads the DLL and exposes the PassThru functions."""

    def __init__(self, dll_path: str) -> None:
        if platform.system() != "Windows":
            raise TransportError("J2534 pass-thru devices are only supported on Windows")
        if not os.path.exists(dll_path):
            raise TransportError(f"J2534 DLL not found: {dll_path}")
        try:
            # J2534 exports are __stdcall; WinDLL binds that convention on 32-bit
            # Python (on x64 Python stdcall == cdecl, so this is correct there too).
            self._dll = ctypes.WinDLL(dll_path)
        except OSError as exc:
            bits = platform.architecture()[0]
            if getattr(exc, "winerror", None) == 193:
                raise TransportError(
                    f"{os.path.basename(dll_path)} is not the same bitness as this Python "
                    f"({bits}). Most J2534 drivers (e.g. Tactrix op20pt32.dll) are 32-bit: "
                    f"run a 32-bit Python, or point --dll at the vendor's 64-bit DLL if one ships."
                ) from exc
            raise TransportError(f"could not load J2534 DLL {dll_path}: {exc}") from exc
        self._bind()

    def _bind(self) -> None:
        d = self._dll
        self.Open = d.PassThruOpen
        self.Open.argtypes = [c_void_p, POINTER(c_ulong)]
        self.Open.restype = c_long

        self.Close = d.PassThruClose
        self.Close.argtypes = [c_ulong]
        self.Close.restype = c_long

        self.Connect = d.PassThruConnect
        self.Connect.argtypes = [c_ulong, c_ulong, c_ulong, c_ulong, POINTER(c_ulong)]
        self.Connect.restype = c_long

        self.Disconnect = d.PassThruDisconnect
        self.Disconnect.argtypes = [c_ulong]
        self.Disconnect.restype = c_long

        self.ReadMsgs = d.PassThruReadMsgs
        self.ReadMsgs.argtypes = [c_ulong, POINTER(PASSTHRU_MSG), POINTER(c_ulong), c_ulong]
        self.ReadMsgs.restype = c_long

        self.WriteMsgs = d.PassThruWriteMsgs
        self.WriteMsgs.argtypes = [c_ulong, POINTER(PASSTHRU_MSG), POINTER(c_ulong), c_ulong]
        self.WriteMsgs.restype = c_long

        self.StartMsgFilter = d.PassThruStartMsgFilter
        self.StartMsgFilter.argtypes = [
            c_ulong, c_ulong, POINTER(PASSTHRU_MSG), POINTER(PASSTHRU_MSG),
            POINTER(PASSTHRU_MSG), POINTER(c_ulong),
        ]
        self.StartMsgFilter.restype = c_long

        self.Ioctl = d.PassThruIoctl
        self.Ioctl.argtypes = [c_ulong, c_ulong, c_void_p, c_void_p]
        self.Ioctl.restype = c_long

        self.GetLastError = d.PassThruGetLastError
        self.GetLastError.argtypes = [c_char_p]
        self.GetLastError.restype = c_long

    def last_error(self) -> str:
        buf = create_string_buffer(80)
        try:
            self.GetLastError(buf)
            return buf.value.decode(errors="replace")
        except Exception:
            return ""


class _J2534Device:
    """Owns a device handle and one protocol channel."""

    def __init__(self, dll: _J2534Dll, protocol: int, flags: int, baud: int) -> None:
        self.dll = dll
        self.protocol = protocol
        self.device_id = c_ulong(0)
        self.channel_id = c_ulong(0)
        self._opened = False
        self._connected = False
        self._open(flags, baud)

    def _check(self, rc: int, where: str) -> None:
        if rc != STATUS_NOERROR:
            raise J2534Error(rc, where, self.dll.last_error())

    def _open(self, flags: int, baud: int) -> None:
        self._check(self.dll.Open(None, byref(self.device_id)), "PassThruOpen")
        self._opened = True
        self._check(
            self.dll.Connect(self.device_id, self.protocol, flags, baud, byref(self.channel_id)),
            "PassThruConnect",
        )
        self._connected = True
        self.ioctl_u32(CLEAR_RX_BUFFER, None)
        self.ioctl_u32(CLEAR_TX_BUFFER, None)

    def ioctl_config(self, param: int, value: int) -> None:
        cfg = SCONFIG(Parameter=param, Value=value)
        lst = SCONFIG_LIST(NumOfParams=1, ConfigPtr=ctypes.pointer(cfg))
        self._check(self.dll.Ioctl(self.channel_id, SET_CONFIG, byref(lst), None),
                    f"PassThruIoctl(SET_CONFIG {param:#x})")

    def ioctl_u32(self, ioctl_id: int, _unused) -> None:
        self._check(self.dll.Ioctl(self.channel_id, ioctl_id, None, None),
                    f"PassThruIoctl({ioctl_id:#x})")

    def write(self, msgs: List[PASSTHRU_MSG], timeout_ms: int) -> None:
        n = len(msgs)
        arr = (PASSTHRU_MSG * n)(*msgs)
        count = c_ulong(n)
        self._check(self.dll.WriteMsgs(self.channel_id, arr, byref(count), timeout_ms),
                    "PassThruWriteMsgs")

    def read(self, max_msgs: int, timeout_ms: int) -> List[PASSTHRU_MSG]:
        arr = (PASSTHRU_MSG * max_msgs)()
        count = c_ulong(max_msgs)
        rc = self.dll.ReadMsgs(self.channel_id, arr, byref(count), timeout_ms)
        if rc in (ERR_BUFFER_EMPTY, ERR_TIMEOUT):
            return []
        self._check(rc, "PassThruReadMsgs")
        return [arr[i] for i in range(count.value)]

    def close(self) -> None:
        try:
            if self._connected:
                self.dll.Disconnect(self.channel_id)
                self._connected = False
        finally:
            if self._opened:
                self.dll.Close(self.device_id)
                self._opened = False


def _mk_msg(protocol: int, data: bytes, tx_flags: int) -> PASSTHRU_MSG:
    m = PASSTHRU_MSG()
    m.ProtocolID = protocol
    m.TxFlags = tx_flags
    m.DataSize = len(data)
    ctypes.memmove(m.Data, data, len(data))
    return m


def _id_bytes(arb_id: int, extended: bool) -> bytes:
    return arb_id.to_bytes(4, "big")  # J2534 CAN/ISO15765 always use a 4-byte ID prefix


class J2534RawCanTransport(RawCanTransport):
    """Frame-level CAN over a J2534 device (``CAN`` protocol)."""

    def __init__(self, dll_path: Optional[str] = None, bitrate: int = CAN_500K,
                 extended: bool = False) -> None:
        super().__init__(bitrate=bitrate)
        self.dll_path = dll_path or default_dll_path()
        if not self.dll_path:
            raise TransportError(
                "No J2534 DLL found. Pass dll_path=... or set VAGTUNE_J2534_DLL."
            )
        self.extended = extended
        self._tx_flags = ISO15765_FRAME_PAD | (CAN_29BIT_ID_TX if extended else 0)
        self._dev: Optional[_J2534Device] = None
        self._accept: List[int] = []

    def open(self) -> None:
        if self._open:
            return
        dll = _J2534Dll(self.dll_path)
        flags = CAN_29BIT_ID if self.extended else 0
        self._dev = _J2534Device(dll, CAN, flags, self.bitrate)
        self._install_pass_all_filter()
        self._open = True
        log.info("opened J2534 CAN channel via %s", self.dll_path)

    def _install_pass_all_filter(self) -> None:
        # A CAN channel needs at least one PASS filter or it reads nothing.
        mask = _mk_msg(CAN, b"\x00\x00\x00\x00", self._tx_flags)
        patt = _mk_msg(CAN, b"\x00\x00\x00\x00", self._tx_flags)
        fid = c_ulong(0)
        self._dev._check(
            self._dev.dll.StartMsgFilter(self._dev.channel_id, PASS_FILTER,
                                         byref(mask), byref(patt), None, byref(fid)),
            "PassThruStartMsgFilter(PASS)",
        )

    def close(self) -> None:
        if not self._open:
            return
        try:
            self._dev.close()
        finally:
            self._dev = None
            self._open = False

    def send(self, frame: CanFrame) -> None:
        if not self._open:
            raise TransportNotOpen("J2534 CAN channel not open")
        payload = _id_bytes(frame.arbitration_id, frame.is_extended_id) + frame.data
        self._dev.write([_mk_msg(CAN, payload, self._tx_flags)], timeout_ms=100)

    def send_many(self, frames) -> None:
        if not self._open:
            raise TransportNotOpen("J2534 CAN channel not open")
        msgs = [
            _mk_msg(CAN, _id_bytes(f.arbitration_id, f.is_extended_id) + f.data, self._tx_flags)
            for f in frames
        ]
        if msgs:
            self._dev.write(msgs, timeout_ms=200)

    def recv(self, timeout: float) -> Optional[CanFrame]:
        if not self._open:
            raise TransportNotOpen("J2534 CAN channel not open")
        msgs = self._dev.read(1, int(max(0.0, timeout) * 1000))
        for m in msgs:
            raw = bytes(m.Data[:m.DataSize])
            if len(raw) < 4:
                continue
            arb = int.from_bytes(raw[:4], "big")
            return CanFrame(arb, raw[4:], is_extended_id=self.extended)
        return None

    def set_accept_ids(self, arbitration_ids: Iterable[int]) -> None:
        # The pass-all filter already admits everything; software filtering in the
        # ISO-TP layer handles narrowing. Recorded for completeness.
        self._accept = list(arbitration_ids)


class J2534IsoTpLink(IsoTpLink):
    """ISO-TP via the J2534 ``ISO15765`` protocol (device-side segmentation)."""

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
    ) -> None:
        super().__init__(tx_id, rx_id, extended_id=extended_id)
        self.dll_path = dll_path or default_dll_path()
        if not self.dll_path:
            raise TransportError("No J2534 DLL found. Pass dll_path=... or set VAGTUNE_J2534_DLL.")
        self.bitrate = bitrate
        self._tx_flags = ISO15765_FRAME_PAD if tx_padding else 0
        if extended_id:
            self._tx_flags |= CAN_29BIT_ID_TX
        self.stmin_tx = stmin_tx
        self._dev: Optional[_J2534Device] = None
        self._open_device()

    def _open_device(self) -> None:
        dll = _J2534Dll(self.dll_path)
        flags = CAN_29BIT_ID if self.extended_id else 0
        self._dev = _J2534Device(dll, ISO15765, flags, self.bitrate)
        # Receive side: tell the ECU it may blast consecutive frames at us with no
        # block limit and no inter-frame gap (we are a laptop; we can keep up).
        for param, value in ((ISO15765_BS, 0), (ISO15765_STMIN, 0)):
            try:
                self._dev.ioctl_config(param, value)
            except J2534Error as exc:
                log.debug("device rejected config %#x=%d (%s); using firmware default",
                          param, value, exc)
        # Transmit side: honour the ECU's requested STmin by default. STMIN_TX is an
        # optional override some devices support for ECUs that ask for a slower rate
        # than they can really take (common on older VAG TCUs). Best-effort only.
        if self.stmin_tx:
            try:
                self._dev.ioctl_config(STMIN_TX, self.stmin_tx)
            except J2534Error:
                log.debug("device does not support STMIN_TX override")
        self._install_flow_control_filter()

    def _install_flow_control_filter(self) -> None:
        """A flow-control filter binds tx_id<->rx_id so the firmware auto-handles FC."""
        id_mask = b"\xFF\xFF\xFF\xFF"
        mask = _mk_msg(ISO15765, id_mask, self._tx_flags)
        patt = _mk_msg(ISO15765, _id_bytes(self.rx_id, self.extended_id), self._tx_flags)
        flow = _mk_msg(ISO15765, _id_bytes(self.tx_id, self.extended_id), self._tx_flags)
        fid = c_ulong(0)
        self._dev._check(
            self._dev.dll.StartMsgFilter(self._dev.channel_id, FLOW_CONTROL_FILTER,
                                         byref(mask), byref(patt), byref(flow), byref(fid)),
            "PassThruStartMsgFilter(FLOW_CONTROL)",
        )

    def send(self, payload: bytes) -> None:
        if self._dev is None:
            raise TransportNotOpen("J2534 ISO-TP channel not open")
        data = _id_bytes(self.tx_id, self.extended_id) + payload
        self._dev.write([_mk_msg(ISO15765, data, self._tx_flags)], timeout_ms=2000)

    def recv(self, timeout: float) -> Optional[bytes]:
        if self._dev is None:
            raise TransportNotOpen("J2534 ISO-TP channel not open")
        deadline = time.monotonic() + timeout
        while True:
            remaining_ms = int(max(0.0, deadline - time.monotonic()) * 1000)
            msgs = self._dev.read(4, remaining_ms)
            for m in msgs:
                raw = bytes(m.Data[:m.DataSize])
                if len(raw) < 4:
                    continue
                # The firmware emits a zero-length "start of message" indication
                # (RxStatus bit) before the full frame; skip anything with no payload.
                if len(raw) == 4:
                    continue
                arb = int.from_bytes(raw[:4], "big")
                if arb == self.rx_id:
                    return raw[4:]
            if time.monotonic() >= deadline:
                return None

    def flush_rx(self) -> None:
        if self._dev is not None:
            self._dev.ioctl_u32(CLEAR_RX_BUFFER, None)

    def close(self) -> None:
        if self._dev is not None:
            try:
                self._dev.close()
            finally:
                self._dev = None
