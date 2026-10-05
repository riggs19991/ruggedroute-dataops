"""Generic OBD-II (SAE J1979 / ISO 15765-4): PID tables, client and simulated ECU.

Importing this package also registers the OBD simulator's preset hooks for the
``r32-2008`` and ``golf-tdi-2012`` simulated vehicles (see :mod:`vagtune.obd.sim`).
"""

from __future__ import annotations

from .pids import (
    PIDS,
    UASIDS,
    MonitorState,
    MonitorStatus,
    PidDef,
    ScalingOverrides,
    decode_dtc,
    decode_monitor_status,
    decode_pid,
    decode_vehicle_info,
    format_value,
    infotype_name,
    parse_dtc_list,
    parse_supported,
    uas_apply,
)
from .client import (
    Mode06Result,
    ObdClient,
    ObdError,
    ObdNegativeResponse,
    ObdProtocolError,
    ObdTimeout,
    ObdTiming,
    ObdValue,
    VehicleInfo,
    parse_mode06_records,
)
from .sim import CompositeEcu, ObdNode, SimulatedObdEcu, add_obd_nodes

__all__ = [
    "PIDS", "UASIDS", "MonitorState", "MonitorStatus", "PidDef", "ScalingOverrides",
    "decode_dtc", "decode_monitor_status", "decode_pid", "decode_vehicle_info", "format_value", "infotype_name",
    "parse_dtc_list", "parse_supported", "uas_apply",
    "Mode06Result", "ObdClient", "ObdError", "ObdNegativeResponse", "ObdProtocolError",
    "ObdTimeout", "ObdTiming", "ObdValue", "VehicleInfo", "parse_mode06_records",
    "CompositeEcu", "ObdNode", "SimulatedObdEcu", "add_obd_nodes",
]
