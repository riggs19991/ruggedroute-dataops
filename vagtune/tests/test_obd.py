"""
OBD-II tests: PID decoders against the fact sheet's examples, PID 01 for both
ignition types, bitmap walk, DTC/Mode 06/Mode 09 parsers, the client against the
simulated ECU (single link and two responders on a FakeCanBus + CanRouter), NRC 0x78
handling, the composite OBD+UDS brain and the preset hooks.
"""

from __future__ import annotations

import logging
import threading
import time
from typing import Dict, List, Optional, Tuple

import pytest

from vagtune.obd import pids as P
from vagtune.obd.client import (
    Mode06Result,
    ObdClient,
    ObdNegativeResponse,
    ObdTiming,
    ObdTimeout,
    parse_mode06_records,
)
from vagtune.obd.sim import CompositeEcu, ObdNode, SimulatedObdEcu, add_obd_nodes
from vagtune.transport.base import IsoTpLink
from vagtune.transport.fake import FakeIsoTpLink, SimulatedEcu
from vagtune.transport.fakebus import FakeCanBus, SimulatedVehicle
from vagtune.transport.isotp import SoftwareIsoTpLink
from vagtune.transport.router import CanRouter
from vagtune.uds.client import UdsClient

FAST = ObdTiming(p2=0.05, p2_star=1.0)


def H(s: str) -> bytes:
    return bytes.fromhex(s)


# ======================================================================= bitmaps

def test_parse_supported_iso_example():
    assert P.parse_supported(0, H("BE1FA813")) == {
        0x01, 0x03, 0x04, 0x05, 0x06, 0x07, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x13, 0x15, 0x1C, 0x1F, 0x20}
    assert P.parse_supported(0x20, H("80000001")) == {0x21, 0x40}
    assert P.parse_supported(0xE0, H("00000002")) == {0xFF}
    with pytest.raises(ValueError):
        P.parse_supported(0, b"\x00")


def test_build_supported_roundtrip_and_chain():
    ids = {0x01, 0x03, 0x04, 0x05, 0x06, 0x07, 0x0C, 0x0D, 0x0E, 0x0F, 0x10, 0x11, 0x13, 0x15, 0x1C, 0x1F, 0x20}
    assert P.build_supported(0, sorted(ids)) == H("BE1FA813")
    assert P.parse_supported(0x40, P.build_supported(0x40, [0x42, 0x60])) == {0x42, 0x60}
    assert P.next_support_id(0x00) == 0x20 and P.next_support_id(0xC0) == 0xE0 and P.next_support_id(0xE0) is None
    assert P.is_support_id(0xA0) and not P.is_support_id(0xA1)


# ====================================================================== decoders

VECTORS: List[Tuple[int, str, object]] = [
    (0x02, "01 30", "P0130"), (0x02, "00 00", None),
    (0x03, "02 00", {"fuel_system_1": "closed loop (oxygen sensor feedback)",
                     "fuel_system_2": "engine off (no status)"}),
    (0x03, "03 00", {"fuel_system_1": "invalid (0x03)", "fuel_system_2": "engine off (no status)"}),
    (0x04, "80", 50.19607843137255), (0x04, "FF", 100.0),
    (0x05, "46", 30), (0x05, "00", -40), (0x05, "FF", 215),
    (0x06, "80", 0.0), (0x07, "00", -100.0), (0x08, "FF", 99.21875), (0x09, "40", -50.0),
    (0x0A, "FF", 765), (0x0B, "21", 33),
    (0x0C, "20 80", 2080.0), (0x0C, "FF FF", 16383.75),
    (0x0D, "3C", 60), (0x0E, "80", 0.0), (0x0E, "00", -64.0), (0x0F, "28", 0),
    (0x10, "01 2C", 3.0), (0x10, "FF FF", 655.35),
    (0x11, "FF", 100.0),
    (0x12, "01", "upstream of first catalytic converter"), (0x12, "08", "pump commanded on for diagnostics"),
    (0x12, "00", "none"), (0x12, "03", "invalid (0x03)"),
    (0x13, "33", {"B1S1": True, "B1S2": True, "B1S3": False, "B1S4": False,
                  "B2S1": True, "B2S2": True, "B2S3": False, "B2S4": False}),
    (0x14, "6E 80", {"voltage": 0.55, "stft": 0.0}), (0x17, "FF FF", {"voltage": 1.275, "stft": None}),
    (0x1B, "00 00", {"voltage": 0.0, "stft": -100.0}),
    (0x1C, "01", "OBD-II (CARB)"), (0x1C, "06", "EOBD"), (0x1C, "21", "HD EOBD-IV (Heavy Duty Euro OBD Stage VI)"),
    (0x1C, "FB", "not available for assignment (SAE J1939 special meaning)"), (0x1C, "40", "reserved (64)"),
    (0x1D, "05", {"B1S1": True, "B1S2": False, "B2S1": True, "B2S2": False,
                  "B3S1": False, "B3S2": False, "B4S1": False, "B4S2": False}),
    (0x1E, "01", {"pto_active": True}), (0x1E, "80", {"pto_active": False}),
    (0x1F, "00 78", 120), (0x21, "FF FF", 65535),
    (0x22, "FF FF", 5177.265), (0x23, "00 FA", 2500),
    (0x24, "80 00 80 00", {"lambda": 1.0, "voltage": 4.0}), (0x2B, "FF FF FF FF", {"lambda": 65535 * 2 / 65536, "voltage": 65535 * 8 / 65536}),
    (0x2C, "FF", 100.0), (0x2D, "80", 0.0), (0x2E, "40", 25.098039215686274), (0x2F, "00", 0.0),
    (0x30, "05", 5), (0x31, "01 2C", 300),
    (0x32, "80 00", -8192.0), (0x32, "7F FF", 8191.75), (0x32, "00 00", 0.0),
    (0x33, "63", 99),
    (0x34, "80 00 80 00", {"lambda": 1.0, "current": 0.0}), (0x3B, "00 00 00 00", {"lambda": 0.0, "current": -128.0}),
    (0x3C, "03 E8", 60.0), (0x3F, "00 00", -40.0),
    (0x42, "38 40", 14.4), (0x43, "00 33", 20.0), (0x44, "80 00", 1.0),
    (0x45, "1A", 10.196078431372548), (0x46, "3C", 20), (0x47, "FF", 100.0), (0x48, "00", 0.0),
    (0x49, "0C", 4.705882352941177), (0x4A, "0C", 4.705882352941177), (0x4B, "80", 50.19607843137255),
    (0x4C, "1A", 10.196078431372548), (0x4D, "00 10", 16), (0x4E, "00 F0", 240),
    (0x4F, "04 05 06 19", {"max_lambda": 4, "max_o2_voltage": 5, "max_o2_current": 6, "max_map": 250}),
    (0x50, "0A 00 00 00", {"max_maf": 100}),
    (0x51, "01", "gasoline"), (0x51, "04", "diesel"), (0x51, "13", "hybrid diesel"), (0x51, "30", "reserved (48)"),
    (0x52, "FF", 100.0), (0x53, "FF FF", 327.675),
    (0x54, "80 00", -32768), (0x54, "7F FF", 32767),
    (0x55, "80 7E", {"bank1": 0.0, "bank3": -1.5625}), (0x58, "FF 00", {"bank2": 99.21875, "bank4": -100.0}),
    (0x59, "FF FF", 655350), (0x5A, "FF", 100.0), (0x5B, "00", 0.0), (0x5C, "80", 88),
    (0x5D, "69 00", 0.0), (0x5D, "00 00", -210.0), (0x5E, "00 28", 2.0),
    (0x5F, "0E", "Heavy Duty Vehicles (EURO IV) B1"), (0x5F, "01", "reserved (0x01)"),
    (0x61, "7D", 0), (0x62, "FF", 130), (0x63, "01 40", 320),
    (0x64, "7D 8C 96 A0 AA", {"idle": 0, "point1": 15, "point2": 25, "point3": 35, "point4": 45}),
    (0x65, "0F 0A", {"pto_active": False, "auto_trans_in_gear": True, "manual_trans_in_gear": False, "glow_plug_lamp_on": True}),
    (0x65, "00 FF", {}),
    (0x66, "03 00 40 00 20", {"sensor_a": 2.0, "sensor_b": 1.0}), (0x66, "01 00 40 00 20", {"sensor_a": 2.0}),
    (0x67, "03 82 50", {"sensor_1": 90, "sensor_2": 40}),
    (0x68, "03 82 50", {"B1S1": 90, "B1S2": 40}),
    (0x68, "3F 82 50 28 29 2A 2B", {"B1S1": 90, "B1S2": 40, "B1S3": 0, "B2S1": 1, "B2S2": 2, "B2S3": 3}),
    (0x69, "3F FF 80 80 00 FF 40", {"commanded_egr_a": 100.0, "actual_egr_a": 128 / 2.55, "egr_error_a": 0.0,
                                     "commanded_egr_b": 0.0, "actual_egr_b": 100.0, "egr_error_b": 64 / 1.28 - 100}),
    (0x6A, "05 FF 00 80 00", {"commanded_a": 100.0, "commanded_b": 128 / 2.55}),
    (0x6B, "11 32 00 00 00", {"egr_temp_a_b1s1": 10}),
    (0x6B, "10 32 00 00 00", {"egr_temp_a_b1s1": 160}),
    (0x6C, "0F FF 00 FF 00", {"commanded_a": 100.0, "relative_a": 0.0, "commanded_b": 100.0, "relative_b": 0.0}),
    (0x6D, "3F 00 FA 00 F8 50 01 00 00 F0 28",
     {"commanded_rail_pressure_a": 2500, "rail_pressure_a": 2480, "fuel_temperature_a": 40,
      "commanded_rail_pressure_b": 2560, "rail_pressure_b": 2400, "fuel_temperature_b": 0}),
    (0x6E, "0F 00 01 00 02 00 03 00 04", {"commanded_icp_a": 10, "icp_a": 20, "commanded_icp_b": 30, "icp_b": 40}),
    (0x6F, "03 65 64", {"compressor_inlet_a": 101, "compressor_inlet_b": 100}),
    (0x6F, "0C 10 11", {"compressor_inlet_a": 128, "compressor_inlet_b": 136}),
    (0x70, "3F 0C A0 0C B0 0D 00 0D 10 0E",
     {"commanded_boost_a": 101.0, "boost_a": 101.5, "commanded_boost_b": 104.0, "boost_b": 104.5,
      "control_status_a": "closed loop", "control_status_b": "fault present"}),
    (0x71, "3F 80 80 FF 00 09", {"commanded_vgt_a": 128 / 2.55, "vgt_position_a": 128 / 2.55,
                                 "commanded_vgt_b": 100.0, "vgt_position_b": 0.0,
                                 "control_status_a": "open loop", "control_status_b": "closed loop"}),
    (0x72, "0F FF 00 FF 00", {"commanded_a": 100.0, "position_a": 0.0, "commanded_b": 100.0, "position_b": 0.0}),
    (0x73, "03 29 04 00 64", {"bank1": 105.0, "bank2": 1.0}),
    (0x74, "03 0B B8 00 01", {"turbo_a": 30000, "turbo_b": 10}),
    (0x75, "0F 50 64 0B B8 0D AC", {"compressor_inlet": 40, "compressor_outlet": 60, "turbine_inlet": 260.0, "turbine_outlet": 310.0}),
    (0x76, "01 50 64 0B B8 0D AC", {"compressor_inlet": 40}),
    (0x77, "0F 50 51 52 53", {"B1S1": 40, "B1S2": 41, "B2S1": 42, "B2S2": 43}),
    (0x78, "03 0B B8 0D AC 00 00 00 00", {"S1": 260.0, "S2": 310.0}),
    (0x79, "0F 00 00 00 00 00 00 FF FF", {"S1": -40.0, "S2": -40.0, "S3": -40.0, "S4": 6513.5}),
    (0x7A, "07 00 32 29 04 28 D2", {"delta_pressure": 0.5, "inlet_pressure": 105.0, "outlet_pressure": 104.5}),
    (0x7B, "01 FF CE 00 00 00 00", {"delta_pressure": -0.5}),
    (0x7C, "0F 0D AC 0D 48 00 00 FF FF", {"b1_inlet": 310.0, "b1_outlet": 300.0, "b2_inlet": -40.0, "b2_outlet": 6513.5}),
    (0x7D, "09", {"inside_control_area": True, "outside_control_area": False,
                  "inside_manufacturer_carve_out": False, "nte_deficiency_active": True}),
    (0x7E, "02", {"inside_control_area": False, "outside_control_area": True,
                  "inside_manufacturer_carve_out": False, "nte_deficiency_active": False}),
    (0x7F, "07 00 01 E2 40 00 00 3A 98 00 00 00 05", {"total": 123456, "idle": 15000, "with_pto": 5}),
    (0x81, "03" + " 00 00 00 01 00 00 00 02 00 00 00 03 00 00 00 04" + " 00" * 24,
     {"aecd1_timer1": 1, "aecd1_timer2": 2, "aecd2_timer1": 3, "aecd2_timer2": 4}),
    (0x8A, "10" + " 00" * 32 + " 00 00 00 09 00 00 00 0A",
     {"aecd20_timer1": 9, "aecd20_timer2": 10}),
    (0x83, "05 00 50 00 00 00 60 00 00", {"B1S1": 80, "B2S1": 96}),
    (0x84, "50", 40),
    (0x85, "0F 00 C8 01 90 80 00 00 00 3C", {"avg_reagent_consumption": 1.0, "avg_demanded_consumption": 2.0,
                                             "reagent_tank_level": 128 / 2.55, "warning_mode_time": 60}),
    (0x86, "03 00 50 00 A0", {"B1S1": 1.0, "B2S1": 2.0}),
    (0x87, "03 0C A0 0C C0", {"sensor_a": 101.0, "sensor_b": 102.0}),
    (0x8B, "7F 03 80 01 E0 01 90", {"dpf_regen_in_progress": True, "dpf_regen_type": "active",
                                    "nox_adsorber_regen_in_progress": False,
                                    "nox_adsorber_desulfurization_in_progress": False,
                                    "normalized_trigger": 128 / 2.55, "avg_time_between_regens": 480,
                                    "avg_distance_between_regens": 400}),
    (0x8C, "11 10 00 00 00 00 00 00 00 20 00 00 00 00 00 00 00",
     {"concentration_B1S1": 0x1000 * 0.001526, "lambda_B1S1": 0x2000 * 0.000122}),
    (0x9C, "88 00 00 00 00 00 00 10 00 00 00 00 00 00 00 20 00",
     {"concentration_B2S4": 0x1000 * 0.001526, "lambda_B2S4": 0x2000 * 0.000122}),
    (0x8D, "FF", 100.0), (0x8E, "7D", 0),
    (0x8F, "0F 03 00 64 02 00 C8", {"b1s1_active": True, "b1s1_regenerating": True, "b1s1_normalized_output": 1.0,
                                    "b2s1_active": False, "b2s1_regenerating": True, "b2s1_normalized_output": 2.0}),
    (0x90, "4D 00 10", {"all_monitors_complete": False, "mi_status": "continuous",
                        "display_strategy": "discriminatory", "continuous_mi_hours": 16}),
    (0x91, "02 00 10 00 20", {"ecu_mi_status": "short", "continuous_mi_hours": 16, "highest_b1_counter_hours": 32}),
    (0x92, "07 05", {"fuel_pressure_control_1_closed_loop": True, "injection_quantity_1_closed_loop": False,
                     "injection_timing_1_closed_loop": True}),
    (0x93, "01 00 2A", {"cumulative_continuous_mi_hours": 42}),
    (0x94, "3F 03 00 01 00 02 00 03 00 04 00 05", {"warning_active": True, "level1": "enabled", "level2": "inactive",
                                                   "level3": "inactive", "reagent_quality_hours": 1,
                                                   "reagent_consumption_hours": 2, "dosing_activity_hours": 3,
                                                   "egr_valve_hours": 4, "monitoring_system_hours": 5}),
    (0x98, "01 0B B8 00 00 00 00 00 00", {"S5": 260.0}),
    (0x99, "08 00 00 00 00 00 00 0B B8", {"S8": 260.0}),
    (0x9B, "00 00 00 FF", 100.0),
    (0x9D, "01 02 03 04", "01 02 03 04"), (0x9E, "AB CD", "AB CD"),
    (0xA2, "00 40", 2.0), (0xA4, "02 00 03 E8", {"gear_ratio": 1.0}), (0xA4, "00 00 03 E8", {}),
    (0xA5, "01 64 00 00", {"dosing": 50.0}), (0xA6, "00 00 00 64", 10.0),
    (0xA9, "01 01 00 00", {"abs_disabled": True}),
    (0xC6, "01 00 02 00 03 00 04", {"status": 1, "removal_block_counter": 2, "liquid_reagent_failure_counter": 3,
                                    "monitoring_malfunction_counter": 4}),
    (0xC7, "01 02", "01 02"),
]


@pytest.mark.parametrize("pid,hexdata,expected", VECTORS, ids=[f"{v[0]:02X}" for v in VECTORS])
def test_decoder_vectors(pid, hexdata, expected):
    value = P.decode_pid(pid, H(hexdata))
    if isinstance(expected, float):
        assert value == pytest.approx(expected)
    elif isinstance(expected, dict):
        assert set(value) == set(expected)
        for k, v in expected.items():
            if isinstance(v, float):
                assert value[k] == pytest.approx(v), k
            else:
                assert value[k] == v, k
    else:
        assert value == expected


def test_every_pid_row_decodes_a_full_length_sample():
    """No decoder may crash on a buffer of its declared length (any byte pattern)."""
    for pid, d in P.PIDS.items():
        n = d.nbytes if d.nbytes is not None else 7
        for fill in (0x00, 0xFF, 0x55):
            P.decode_pid(pid, bytes([fill]) * n)
    assert len(P.PIDS) >= 170
    assert P.pid_length(0x68) is None and P.PIDS[0x68].unverified
    assert P.pid_name(0xFE).startswith("PID FE")
    assert P.decode_pid(0xFE, b"\x01\x02") == "01 02"
    with pytest.raises(ValueError):
        P.PIDS[0x0C].decode(b"\x01")


def test_bitmap_pid_decoders():
    assert P.decode_pid(0x00, H("BE1FA813")) == P.parse_supported(0, H("BE1FA813"))
    assert P.decode_pid(0xC0, H("00000000")) == set()


def test_scaling_overrides_pid4f_and_pid50():
    # ISO B.60 worked example: Data A = 4 -> 0.0000610/bit; raw 7D00 -> 1.953.
    sc = P.ScalingOverrides(pid4f_a=4)
    assert sc.lambda_scale == pytest.approx(4 / 65535)
    assert P.decode_pid(0x44, H("7D 00"), sc) == pytest.approx(1.953, abs=0.001)
    assert P.decode_pid(0x24, H("7D 00 80 00"), sc)["lambda"] == pytest.approx(1.953, abs=0.001)
    assert P.decode_pid(0x34, H("7D 00 80 00"), sc)["lambda"] == pytest.approx(1.953, abs=0.001)
    assert P.decode_pid(0x44, H("80 00")) == pytest.approx(1.0)
    sc2 = P.ScalingOverrides(pid50_a=10)
    assert sc2.maf_scale == pytest.approx(100 / 65535)
    assert P.decode_pid(0x10, H("FF FF"), sc2) == pytest.approx(100.0)
    assert P.decode_pid(0x10, H("FF FF")) == pytest.approx(655.35)
    assert P.DEFAULT_SCALING.lambda_scale == pytest.approx(2 / 65536)
    assert P.DEFAULT_SCALING.maf_scale == 0.01


def test_pid01_decode_spark_elm_example_and_compression():
    # ELM: 41 01 81 07 65 04 -> MIL on, 1 DTC (spark).
    s = P.decode_monitor_status(H("81 07 65 04"))
    assert s.mil and s.dtc_count == 1 and not s.compression_ignition and s.ignition == "spark"
    assert {n: (m.available, m.complete) for n, m in s.continuous.items()} == {
        "misfire": (True, True), "fuel_system": (True, True), "components": (True, True)}
    nc = {n: (m.available, m.complete) for n, m in s.non_continuous.items()}
    assert nc == {"catalyst": (True, True), "heated_catalyst": (False, True), "evap": (True, False),
                  "secondary_air": (False, True), "gpf_or_ac_refrigerant": (False, True),
                  "o2_sensor": (True, True), "o2_heater": (True, True), "egr_vvt": (False, True)}
    assert s.incomplete() == ["evap"] and not s.ready
    # Compression ignition: B bit 3 set, misfire not complete, C/D use the CI table.
    c = P.decode_monitor_status(H("00 1D EB 42"))
    assert c.compression_ignition and not c.mil and c.dtc_count == 0
    assert c.continuous["misfire"].available and not c.continuous["misfire"].complete
    assert not c.continuous["fuel_system"].available
    assert set(c.non_continuous) == {"nmhc_catalyst", "nox_scr_aftertreatment", "boost_pressure",
                                     "exhaust_gas_sensor", "pm_filter", "egr_vvt"}
    assert c.non_continuous["nox_scr_aftertreatment"].complete is False
    assert c.non_continuous["pm_filter"].complete is False
    assert c.non_continuous["nmhc_catalyst"].complete is True
    assert set(c.incomplete()) == {"misfire", "nox_scr_aftertreatment", "pm_filter"}
    # PID 41: byte A is 0; ignition can be forced from PID 01 knowledge.
    t = P.decode_monitor_status(H("00 07 05 01"), this_cycle=True, compression_ignition=True)
    assert t.this_cycle and t.compression_ignition and t.dtc_count == 0
    assert t.non_continuous["nmhc_catalyst"].available and not t.non_continuous["nmhc_catalyst"].complete
    assert P.MonitorState("evap", True, False).label == "Evaporative system"
    with pytest.raises(ValueError):
        P.decode_monitor_status(b"\x00\x00")


def test_encode_monitor_status_roundtrip():
    raw = P.encode_monitor_status(mil=True, dtc_count=3, compression_ignition=False,
                                  supported={"misfire": True, "fuel_system": True, "components": True,
                                             "catalyst": True, "evap": True, "o2_sensor": True},
                                  complete={"evap": False, "misfire": False})
    assert raw == H("83 17 25 04")
    s = P.decode_monitor_status(raw)
    assert s.dtc_count == 3 and not s.continuous["misfire"].complete and not s.non_continuous["evap"].complete
    assert P.encode_monitor_status(mil=True, dtc_count=3, compression_ignition=True, supported={},
                                   complete={}, this_cycle=True) == H("00 08 00 00")


def test_walk_records_mode01_and_mode02_iso_example():
    body = H("0C 20 80 04 80 05 28")
    assert P.walk_records(body) == [(0x0C, None, H("20 80")), (0x04, None, H("80")), (0x05, None, H("28"))]
    # ISO Tables 141/142: 42 0C 00 20 80 04 00 80 05 00 28 -> 2080 rpm, 50.2 %, 0 °C (order differs).
    recs = P.walk_records(H("0C 00 20 80 04 00 80 05 00 28"), with_frame=True)
    assert [(r[0], r[1]) for r in recs] == [(0x0C, 0), (0x04, 0), (0x05, 0)]
    assert P.decode_pid(0x0C, recs[0][2]) == 2080.0
    assert P.decode_pid(0x04, recs[1][2]) == pytest.approx(50.2, abs=0.01)
    assert P.decode_pid(0x05, recs[2][2]) == 0
    # A variable-length PID swallows the rest of the payload.
    assert P.walk_records(H("05 28 68 03 82 50")) == [(0x05, None, H("28")), (0x68, None, H("03 82 50"))]


def test_dtc_codec_iso_and_elm_examples():
    assert P.decode_dtc(0x01, 0x43) == "P0143"
    assert P.decode_dtc(0xC1, 0x58) == "U0158"
    assert P.decode_dtc(0xD0, 0x16) == "U1016"
    assert P.decode_dtc(0x40, 0x35) == "C0035" and P.decode_dtc(0x81, 0x00) == "B0100"
    assert P.encode_dtc("P0143") == H("01 43") and P.encode_dtc("U0158") == H("C1 58")
    assert P.decode_dtc(*P.encode_dtc("B3FFF")) == "B3FFF"
    with pytest.raises(ValueError):
        P.encode_dtc("X0001")
    assert P.parse_dtc_list(H("06 01 43 01 96 02 34 02 CD 03 57 0A 24")) == [
        "P0143", "P0196", "P0234", "P02CD", "P0357", "P0A24"]
    assert P.parse_dtc_list(H("00")) == [] and P.parse_dtc_list(b"") == []
    assert P.parse_dtc_list(H("01 04 43")) == ["P0443"]
    assert P.parse_dtc_list(H("02 04 43 00 00")) == ["P0443"]      # zero filler skipped


def test_uas_apply_and_mode06_iso_example():
    assert P.uas_apply(0x0A, 0x0BB0) == (pytest.approx(0.365, abs=0.001), "V", True)
    assert P.uas_apply(0x10, 0x48) == (72, "ms", True)
    assert P.uas_apply(0x24, 150) == (150, "counts", True)
    assert P.uas_apply(0x16, 0x0000) == (pytest.approx(-40.0), "°C", True)
    assert P.uas_apply(0x16, 0xFFFF) == (pytest.approx(6513.5), "°C", True)
    assert P.uas_apply(0x39, 0x0000) == (pytest.approx(-327.68), "%", True)
    assert P.uas_apply(0x96, 0xFE70) == (pytest.approx(-40.0), "°C", True)
    assert P.uas_apply(0xAF, 0xD8F0) == (pytest.approx(-100.0), "%", True)
    assert P.uas_apply(0x1E, 0x8013) == (pytest.approx(1.0, abs=0.001), "λ", True)
    assert P.uas_apply(0x33, 0x1000) == (pytest.approx(1.0, abs=0.001), "λ", True)
    assert P.uas_apply(0x2E, 0x0001) == (True, "bool", True) and P.uas_apply(0x2E, 0) == (False, "bool", True)
    assert P.uas_apply(0xFC, 0x8000) == (pytest.approx(-327.68), "kPa", True)
    value, unit, known = P.uas_apply(0x7E, 0x1234)
    assert (value, known) == (0x1234, False) and "0x7E" in unit
    assert P.uas_raw(0x81, 0xFFFF) == -1 and P.uas_raw(0x01, 0xFFFF) == 0xFFFF

    # ISO Table 168.
    recs = parse_mode06_records(H("01 01 0A 0B B0 0B B0 0B B0 01 05 10 00 48 00 00 00 64 01 85 24 00 96 00 4B FF FF"))
    assert [(r.obdmid, r.tid, r.uasid) for r in recs] == [(1, 1, 0x0A), (1, 5, 0x10), (1, 0x85, 0x24)]
    assert recs[0].value == pytest.approx(0.365, abs=0.001) and recs[0].min == recs[0].max == recs[0].value
    assert recs[0].passed and recs[0].completed and recs[0].unit == "V"
    assert (recs[1].value, recs[1].min, recs[1].max, recs[1].unit) == (72, 0, 100, "ms") and recs[1].passed
    assert (recs[2].value, recs[2].min, recs[2].max) == (150, 75, 65535) and recs[2].passed
    assert recs[2].tid_name == "Manufacturer defined TID 85" and recs[0].obdmid_name == "Oxygen sensor monitor B1S1"
    assert recs[0].tid_name == "Rich-to-lean sensor threshold voltage"
    # Table 170: not completed since erasure -> zeros, flagged.
    (nr,) = parse_mode06_records(H("21 87 2E 00 00 00 00 00 00"))
    assert not nr.completed and nr.passed and nr.obdmid_name == "Catalyst monitor bank 1"
    # Fail: signed compare (UASID AF): -5 % below min -2 %.
    (f,) = parse_mode06_records(H("31 80 AF FE 0C FF 38 00 C8"))
    assert f.value == pytest.approx(-5.0) and f.min == pytest.approx(-2.0) and not f.passed
    # Trailing fragment dropped, not crashed.
    assert len(parse_mode06_records(H("01 01 0A 0B B0 0B B0 0B B0 01 05"))) == 1
    assert P.obdmid_name(0xE5) == "Manufacturer defined OBDMID E5" and P.obdmid_name(0x11) == "OBDMID 11 (reserved)"
    assert P.obdmid_name(0xA3) == "Misfire cylinder 2 data" and P.tid_name(0x0B).startswith("EWMA")


def test_mode09_parsers_iso_examples():
    assert P.decode_vehicle_info(0x02, 1, H("31 47 31 4A 43 35 34 34 34 52 37 32 35 32 33 36 37")) == "1G1JC5444R7252367"
    calid = b"JMB*36761500" + b"\0" * 4 + b"JMB*4787261111" + b"\0" * 2
    assert P.decode_vehicle_info(0x04, 2, calid) == ["JMB*36761500", "JMB*4787261111"]
    assert P.decode_vehicle_info(0x06, 2, H("17 91 BC 82 16 E0 62 BE")) == ["1791BC82", "16E062BE"]
    assert P.decode_vehicle_info(0x06, 1, H("98 12 34 76")) == ["98123476"]
    ipt = P.decode_vehicle_info(0x08, 4, H("04 00 0D 09 03 38 03 B1"))
    assert ipt == {"OBDCOND": 1024, "IGNCYCCNTR": 3337, "CATCOMP1": 824, "CATCOND1": 945}
    assert P.decode_vehicle_info(0x0A, 1, H("45 43 4D 00 2D 45 6E 67 69 6E 65 20 43 6F 6E 74 72 6F 6C 00")) == "ECM-Engine Control"
    assert P.decode_vehicle_info(0x0A, 1, H("41 42 53 31 2D 41 6E 74 69 6C 6F 63 6B 20 42 72 61 6B 65 31")) == "ABS1-Antilock Brake1"
    full = P.decode_vehicle_info(0x0B, 18, b"".join(i.to_bytes(2, "big") for i in range(18)))
    assert list(full) == list(P.IPT_COMPRESSION_NAMES) and full["FUELCOND"] == 17
    assert P.decode_vehicle_info(0x0C, 1, H("AA BB")) == "AA BB"


def test_mode09_ipt20_names_flagged_unverified(caplog):
    P._reset_unverified_warnings()
    with caplog.at_level(logging.WARNING, logger="vagtune.obd.pids"):
        v = P.decode_vehicle_info(0x08, 20, b"".join(i.to_bytes(2, "big") for i in range(20)))
        P.decode_vehicle_info(0x08, 20, b"".join(i.to_bytes(2, "big") for i in range(20)))
    assert list(v)[16:] == ["SO2SCOMP1", "SO2SCOND1", "SO2SCOMP2", "SO2SCOND2"]
    assert sum("UNVERIFIED mapping" in r.message for r in caplog.records) == 1


def test_format_value():
    assert P.format_value(800.0, "rpm") == "800 rpm"
    assert P.format_value(10.196078, "%") == "10.2 %"
    assert P.format_value(True) == "yes" and P.format_value(None) == "-"
    assert P.format_value({"voltage": 0.55, "stft": None}, "", {"voltage": "V"}) == "voltage=0.55 V, stft=-"
    assert P.format_value({}, "") == "(no supported items)"
    assert P.format_value({0x01, 0x20}) == "01, 20"
    assert P.format_value(["A", "B"]) == "A, B"


# ================================================================ client (single)

def _client(ecu: SimulatedObdEcu, timing: ObdTiming = FAST, **kw) -> ObdClient:
    return ObdClient(FakeIsoTpLink(0x7E0, 0x7E8, ecu), timing=timing, **kw)


def test_supported_bitmap_walk_single_and_batched():
    tdi = SimulatedObdEcu("golf-tdi-2012")
    for batch in (False, True):
        c = _client(tdi, batch_bitmaps=batch)
        tdi.requests.clear()
        got = c.supported_pids()
        assert got == tdi.supported_pids() - set(P.SUPPORT_BASES)
        assert {0x23, 0x5E, 0x61, 0x7A, 0x7C, 0x83, 0x8B, 0x92} <= got
        assert not got & set(P.SUPPORT_BASES)
        if batch:
            assert tdi.requests == [H("01 00 20 40 60 80 A0")]
        else:
            assert tdi.requests == [H("01 00"), H("01 20"), H("01 40"), H("01 60"), H("01 80")]
        assert c.supported_pids() == got and len(tdi.requests) == (1 if batch else 5)   # cached
    r32 = SimulatedObdEcu("r32-2008")
    c = _client(r32)
    assert c.supported_pids() == r32.supported_pids() - set(P.SUPPORT_BASES)
    assert r32.requests == [H("01 00"), H("01 20"), H("01 40")]
    # The Mode 02 bitmap is constant whether or not a frame is stored (ISO Table 7 e/f).
    assert c.supported_pids(0x02) == {0x02} | {p for p in r32.values if p <= 0x60}
    assert r32.requests[-3:] == [H("02 00 00"), H("02 20 00"), H("02 40 00")]


def test_read_pids_chunking_and_decoding():
    r32 = SimulatedObdEcu("r32-2008")
    c = _client(r32)
    r32.requests.clear()
    vals = c.read_pids([0x0C, 0x05, 0x04, 0x0B, 0x0F, 0x11, 0x1C, 0x00, 0x68])
    assert r32.requests[0] == H("01 00")              # bitmap PID never mixed with data PIDs
    assert r32.requests[1] == H("01 68")              # variable-length PID alone (silent: unsupported)
    assert r32.requests[2] == H("01 0C 05 04 0B 0F 11") and r32.requests[3] == H("01 1C")
    assert vals[0x0C].value == 800.0 and vals[0x0C].unit == "rpm" and vals[0x0C].pretty() == "800 rpm"
    assert vals[0x05].value == 90 and vals[0x1C].value == "OBD-II (CARB)"
    assert vals[0x00].value == {p for p in c.supported_pids() if p <= 0x20} | {0x20}
    assert 0x68 not in vals
    assert str(vals[0x0C]) == "0C Engine speed: 800 rpm"
    v = c.read_pid(0x13)
    assert v.value["B1S1"] and v.value["B2S2"] and not v.value["B1S3"]
    with pytest.raises(ObdTimeout):
        c.read_pid(0x5E)                                 # unsupported on the R32 -> silence
    r32.nrc_on_unsupported = True
    with pytest.raises(ObdNegativeResponse) as exc:
        c.read_pid(0x5E)
    assert exc.value.unsupported and exc.value.nrc == 0x12 and exc.value.response_id == 0x7E8


def test_scaling_override_is_read_from_the_ecu_once(caplog):
    r32 = SimulatedObdEcu("r32-2008")
    r32.values[0x4F] = H("04 00 00 19")
    r32.values[0x50] = H("0A 00 00 00")
    r32.values[0x44] = H("7D 00")
    r32.values[0x34] = H("7D 00 80 00")
    r32.values[0x10] = H("FF FF")
    c = _client(r32)
    with caplog.at_level(logging.INFO, logger="vagtune.obd.client"):
        assert c.read_pid(0x44).value == pytest.approx(1.953, abs=0.001)
        assert c.read_pid(0x10).value == pytest.approx(100.0)
        n = len(r32.requests)
        assert c.read_pid(0x34).value["lambda"] == pytest.approx(1.953, abs=0.001)
        assert len(r32.requests) == n + 1                    # no re-read of 4F/50
    assert any("PID 4F maxima" in r.message for r in caplog.records)
    c.set_scaling(0x7E8, P.ScalingOverrides())
    assert c.read_pid(0x44).value == pytest.approx(0x7D00 * 2 / 65536)


def test_monitor_status_both_profiles_and_this_cycle():
    r32 = SimulatedObdEcu("r32-2008")
    r32.dtcs = ["P0300"]
    c = _client(r32)
    s = c.monitor_status()
    assert s.mil and s.dtc_count == 1 and s.ignition == "spark"
    assert set(s.incomplete()) == {"catalyst", "evap"}
    r32.monitors_disabled_this_cycle = {"evap"}
    t = c.monitor_status(this_cycle=True)
    assert t.this_cycle and t.dtc_count == 0 and not t.non_continuous["evap"].available
    assert t.non_continuous["catalyst"].available and not t.non_continuous["catalyst"].complete
    tdi = SimulatedObdEcu("golf-tdi-2012")
    s2 = _client(tdi).monitor_status()
    assert s2.compression_ignition and not s2.mil
    assert set(s2.non_continuous) == {"nmhc_catalyst", "nox_scr_aftertreatment", "boost_pressure",
                                      "exhaust_gas_sensor", "pm_filter", "egr_vvt"}
    assert s2.incomplete() == ["nox_scr_aftertreatment"]


def test_dtcs_read_clear_and_refusal_while_running():
    tdi = SimulatedObdEcu("golf-tdi-2012")
    tdi.dtcs = ["P0401", "P2002"]
    tdi.pending_dtcs = ["P0299"]
    tdi.permanent_dtcs = ["P0420"]
    c = _client(tdi)
    assert c.read_dtcs() == ["P0401", "P2002"]
    assert c.read_dtcs(0x07) == ["P0299"]
    assert c.read_dtcs(0x0A) == ["P0420"]
    assert c.monitor_status().dtc_count == 2 and c.monitor_status().mil
    with pytest.raises(ValueError):
        c.read_dtcs(0x04)
    tdi.engine_running = True
    assert c.clear_dtcs() == {0x7E8: 0x22}
    assert c.read_dtcs() == ["P0401", "P2002"]
    tdi.engine_running = False
    assert c.clear_dtcs() == {0x7E8: None}
    assert c.read_dtcs() == [] and c.read_dtcs(0x07) == []
    assert c.read_dtcs(0x0A) == ["P0420"]                    # Mode 04 never clears permanent DTCs
    assert not c.monitor_status().mil and c.monitor_status().dtc_count == 0
    assert c.read_pid(0x31).value == 0 and c.read_pid(0x4E).value == 0
    r32 = SimulatedObdEcu("r32-2008")
    assert _client(r32).read_dtcs_all(0x0A) == {}            # 7F 0A 11: not supported, no raise


def test_freeze_frame():
    r32 = SimulatedObdEcu("r32-2008")
    c = _client(r32)
    assert c.freeze_frame() == {0x02: c.freeze_frame()[0x02]} and c.freeze_frame()[0x02].value is None
    r32.dtcs = ["P0171"]
    r32.values[0x0C] = H("20 80")
    ff = c.freeze_frame()
    assert ff[0x02].value == "P0171" and ff[0x02].frame == 0 and ff[0x02].mode == 0x02
    assert ff[0x0C].value == 2080.0 and ff[0x05].value == 90
    assert all(v.frame == 0 for v in ff.values())
    r32.requests.clear()
    sel = c.freeze_frame([0x0C, 0x05, 0x04, 0x0B], frame=0)
    assert r32.requests == [H("02 0C 00 05 00 04 00"), H("02 0B 00")]   # 3 pairs per request
    assert set(sel) == {0x0C, 0x05, 0x04, 0x0B}
    with pytest.raises(ObdTimeout):
        c.freeze_frame([0x0C], frame=1)                                    # only frame 0 stored


def test_vehicle_info_and_supported_infotypes():
    r32 = SimulatedObdEcu("r32-2008")
    c = _client(r32)
    assert c.supported_infotypes() == {0x02, 0x04, 0x06, 0x08, 0x0A}
    assert c.vin() == "WVWKD71K58W000001"
    assert c.vehicle_info(0x04).value == ["022906032GR 0006"]
    assert c.vehicle_info(0x06).value == ["5A3C18F0"]
    ipt = c.vehicle_info(0x08)
    assert ipt.nodi == 16 and ipt.value["OBDCOND"] == 150 and ipt.name.startswith("In-use")
    assert c.vehicle_info(0x0A).value == "ECM-EngineControl"
    with pytest.raises(ObdTimeout):
        c.vehicle_info(0x0B)
    with pytest.raises(ValueError):
        c.vehicle_info(0x00)
    tdi = SimulatedObdEcu("golf-tdi-2012")
    assert _client(tdi).vehicle_info(0x0B).value["HCCATCOMP"] == 200


def test_mode06_results_via_client():
    r32 = SimulatedObdEcu("r32-2008")
    c = _client(r32)
    mids = c.supported_obdmids()
    assert {0x01, 0x02, 0x05, 0x06, 0x21, 0x22, 0x41, 0x81, 0xA1, 0xA7} <= mids and 0xA8 not in mids
    res = c.monitor_test_results()
    assert all(isinstance(r, Mode06Result) for r in res)
    by_mid = {}
    for r in res:
        by_mid.setdefault(r.obdmid, []).append(r)
    assert set(by_mid) == mids
    assert by_mid[0x01][0].value == pytest.approx(0.365, abs=0.001)
    assert not by_mid[0x22][0].completed
    assert by_mid[0x82][0].value == pytest.approx(-0.16) and by_mid[0x82][0].passed
    r32.requests.clear()
    only = c.monitor_test_results([0xA2, 0x00])
    assert r32.requests == [H("06 A2")] and [r.obdmid for r in only] == [0xA2, 0xA2]
    tcm = SimulatedObdEcu("dq250-tcm")
    assert _client(tcm).monitor_test_results_all() == {}                  # 7F 06 11


def test_unverified_mode0a_warns_once(caplog):
    P._reset_unverified_warnings()
    tdi = SimulatedObdEcu("golf-tdi-2012")
    c = _client(tdi)
    with caplog.at_level(logging.WARNING, logger="vagtune.obd.pids"):
        c.read_dtcs(0x0A)
        c.read_dtcs(0x0A)
        c.read_dtcs(0x03)
    msgs = [r.message for r in caplog.records if "UNVERIFIED mapping" in r.message]
    assert len(msgs) == 1 and "Mode 0A" in msgs[0]


def test_unverified_pid68_warns_once_and_decodes_by_length(caplog):
    P._reset_unverified_warnings()
    tdi = SimulatedObdEcu("golf-tdi-2012")
    tdi.values[0x68] = H("03 82 50")
    c = _client(tdi)
    with caplog.at_level(logging.WARNING, logger="vagtune.obd.pids"):
        assert c.read_pid(0x68).value == {"B1S1": 90, "B1S2": 40}
        tdi.values[0x68] = H("3F 82 50 28 29 2A 2B")
        assert c.read_pid(0x68).value["B2S3"] == 3
    assert sum("UNVERIFIED mapping" in r.message for r in caplog.records) == 1


def test_sim_rejects_malformed_and_unknown_services():
    ecu = SimulatedObdEcu("r32-2008")
    assert ecu.handle(b"\x01") == H("7F 01 12")
    assert ecu.handle(b"\x01" + bytes(range(1, 8))) == H("7F 01 12")
    assert ecu.handle(H("02 0C")) == H("7F 02 12")
    assert ecu.handle(H("06 01 02")) == H("7F 06 12")
    assert ecu.handle(H("09 02 04")) == H("7F 09 12")
    assert ecu.handle(H("08 01")) == H("7F 08 11") and ecu.handle(H("0B")) == H("7F 0B 11")
    assert ecu.handle(H("05")) == H("7F 05 11")
    assert ecu.handle(b"") is None and ecu.handle(H("01 C0")) is None
    with pytest.raises(KeyError):
        SimulatedObdEcu("no-such-car")
    c = _client(ecu)
    with pytest.raises(ObdNegativeResponse) as exc:
        c.request(H("08 01"))
    assert exc.value.unsupported and "serviceNotSupported" in str(exc.value)
    with pytest.raises(ValueError):
        c.request_all(b"")


# ============================================================== NRC 0x78 handling

class _ScriptedLink(IsoTpLink):
    """Replays a scripted list of (response_id, payload) per request."""

    def __init__(self, script: Dict[bytes, List[Tuple[int, bytes]]]) -> None:
        super().__init__(0x7DF, 0x7E8)
        self.script = script
        self.queue: List[Tuple[int, bytes]] = []
        self.last_rx_id: Optional[int] = None
        self.sent: List[bytes] = []

    def send(self, payload: bytes) -> None:
        self.sent.append(payload)
        self.queue = list(self.script.get(payload, []))

    def recv(self, timeout: float) -> Optional[bytes]:
        if self.queue:
            rid, payload = self.queue.pop(0)
            self.last_rx_id = rid
            return payload
        time.sleep(min(timeout, 0.005))
        return None

    def flush_rx(self) -> None:
        self.queue.clear()

    def close(self) -> None:
        pass


def test_response_pending_per_responder_and_duplicates(caplog):
    link = _ScriptedLink({
        H("09 06"): [(0x7E8, H("7F 09 78")), (0x7E9, H("49 06 01 98 12 34 76")),
                     (0x7E8, H("7F 09 78")), (0x7E8, H("49 06 02 17 91 BC 82 16 E0 62 BE")),
                     (0x7E8, H("49 06 01 00 00 00 01"))],
        H("03"): [(0x7E8, H("7F 03 78"))] * 5,
        H("01 00"): [(0x7E8, H("41 00 BE 1F A8 13")), (0x7EA, H("7F 01 11")), (0x7E9, H("7F 02 11"))],
    })
    c = ObdClient(link, timing=ObdTiming(p2=0.05, p2_star=0.5, pending_limit=3))
    with caplog.at_level(logging.WARNING, logger="vagtune.obd.client"):
        info = c.vehicle_info_all(0x06)
    assert info[0x7E8].value == ["1791BC82", "16E062BE"] and info[0x7E9].value == ["98123476"]
    assert any("duplicate reply from 0x7E8" in r.message for r in caplog.records)
    # pending_limit exceeded -> that responder is dropped, no hang beyond the window.
    t0 = time.monotonic()
    assert c.read_dtcs_all(0x03) == {}
    assert time.monotonic() - t0 < 0.5
    # Negative replies are kept per responder; one for another SID is ignored.
    raw = c.request_all(H("01 00"))
    assert raw == {0x7E8: H("41 00 BE 1F A8 13"), 0x7EA: H("7F 01 11")}
    assert c.responders == {0x7E8, 0x7E9}                    # 0x7E9 answered CVN; 0x7EA only negatively
    assert c.query_all(H("01 00")) == {0x7E8: H("00 BE 1F A8 13")}
    assert c.request(H("01 00")) == H("00 BE 1F A8 13")
    with pytest.raises(ObdNegativeResponse):
        c.request(H("01 00"), response_id=0x7EA)
    with pytest.raises(ObdTimeout):
        c.request(H("01 00"), response_id=0x7EB)
    with pytest.raises(ObdTimeout) as exc:
        c.request(H("07"))
    assert "no ECU answered OBD mode 0x07 on 0x7DF" in str(exc.value)


def test_known_responders_end_the_window_early():
    r32 = SimulatedObdEcu("r32-2008")
    link = _ScriptedLink({H("01 00"): [(0x7E8, b"\x41" + r32._pid_data(0x00))],
                          H("01 0C"): [(0x7E8, H("41 0C 0C 80"))]})
    c = ObdClient(link, timing=ObdTiming(p2=2.0))
    t0 = time.monotonic()
    assert c.discover() == {0x7E8}
    assert time.monotonic() - t0 >= 1.9                      # unknown responders: full window
    t0 = time.monotonic()
    assert c.read_pid(0x0C).value == 800.0
    assert time.monotonic() - t0 < 1.0                       # known responder answered: early exit


# ============================================================ composite + presets

def test_composite_ecu_routes_obd_and_uds():
    obd = SimulatedObdEcu("r32-2008")
    uds = SimulatedEcu()
    comp = CompositeEcu(obd, uds)
    assert comp.handle(H("01 0C")) == H("41 0C 0C 80")
    assert comp.handle(H("22 F1 90")) == b"\x62\xF1\x90" + uds.identifiers[0xF190]
    assert comp.handle(H("0A")) == H("7F 0A 11") and comp.handle(H("0B")) == H("7F 0B 11")
    silent = CompositeEcu(obd)
    assert silent.handle(H("22 F1 90")) is None and silent.handle_all(H("3E 00")) == []
    assert silent.handle(H("09 02")) == b"\x49\x02\x01" + b"WVWKD71K58W000001"
    tdi = SimulatedObdEcu("golf-tdi-2012")
    assert CompositeEcu(tdi).handle_all(H("04")) == [H("7F 04 78"), H("44")]
    assert CompositeEcu(tdi, uds).handle_all(H("3E 00")) == [H("7E 00")]
    with pytest.raises(TypeError):
        CompositeEcu(object())
    with pytest.raises(TypeError):
        CompositeEcu(obd, object())


@pytest.fixture
def two_ecus():
    bus = FakeCanBus()
    engine = SimulatedObdEcu("golf-tdi-2012")
    engine.dtcs = ["P0401"]
    tcm = SimulatedObdEcu("dq250-tcm")
    tcm.dtcs = ["P0730"]
    e_uds, t_uds = SimulatedEcu(), SimulatedEcu()
    t_uds.identifiers[0xF187] = b"02E300053E"
    nodes = [ObdNode(bus, CompositeEcu(engine, e_uds), request_id=0x7E0, response_id=0x7E8, name="engine"),
             ObdNode(bus, CompositeEcu(tcm, t_uds), request_id=0x7E1, response_id=0x7E9, name="tcm")]
    for n in nodes:
        n.start()
    router = CanRouter(bus.attach("tester"), name="tester")
    link = SoftwareIsoTpLink(router.endpoint(set(range(0x7E8, 0x7F0))), 0x7DF, 0x7E8,
                             extra_rx_ids=range(0x7E9, 0x7F0), owns_transport=True)
    client = ObdClient(link, timing=ObdTiming(p2=0.3, p2_star=2.0))
    yield client, engine, tcm, router, bus
    client.close()
    router.close()
    for n in nodes:
        n.stop()


def test_functional_request_two_responders(two_ecus):
    client, engine, tcm, router, bus = two_ecus
    assert client.functional
    assert client.discover() == {0x7E8, 0x7E9} and client.responders == {0x7E8, 0x7E9}
    sup = client.supported_pids_all()
    assert set(sup) == {0x7E8, 0x7E9}
    assert sup[0x7E9] == {0x0D, 0x1C, 0x42, 0x01, 0x41} and 0x23 in sup[0x7E8]
    assert client.supported_pids() == sup[0x7E8]           # engine preferred
    vals = client.read_pids_all([0x0D, 0x1C, 0x23])
    assert vals[0x7E8][0x23].value == 2500 and 0x23 not in vals[0x7E9]
    assert vals[0x7E9][0x0D].response_id == 0x7E9 and vals[0x7E9][0x1C].value == "OBD-II (CARB)"
    assert client.read_pid(0x0D, response_id=0x7E9).response_id == 0x7E9

    status = client.monitor_status_all()
    assert status[0x7E8].compression_ignition and status[0x7E8].dtc_count == 1
    assert not status[0x7E9].compression_ignition and status[0x7E9].dtc_count == 1
    assert client.read_dtcs_all() == {0x7E8: ["P0401"], 0x7E9: ["P0730"]}
    assert client.read_dtcs() == ["P0401", "P0730"]
    assert client.read_dtcs_all(0x0A) == {0x7E8: []}        # TCM: 7F 0A 11

    # Multi-frame CALID from both ECUs (FF/CF interleave on the bus, keyed by id).
    cal = client.vehicle_info_all(0x04)
    assert cal[0x7E8].value == ["03L906018MK 9978"] and cal[0x7E9].value == ["02E300053E 1211"]
    names = client.vehicle_info_all(0x0A)
    assert names[0x7E8].value == "ECM-EngineControl" and names[0x7E9].value == "TCM-TransmissionCtl"
    assert set(client.vehicle_info_all(0x02)) == {0x7E8}   # the TCM has no VIN
    assert client.supported_infotypes_all()[0x7E9] == {0x04, 0x06, 0x0A}

    # 7F 09 78 preamble from the engine through the real node path; TCM answers at once.
    cvn = client.vehicle_info_all(0x06)
    assert cvn[0x7E8].value == ["12345678"] and cvn[0x7E9].value == ["00A1B2C3"]
    assert engine.requests.count(H("09 06")) == 1

    # Mode 06: only the engine supports it.
    res = client.monitor_test_results_all()
    assert set(res) == {0x7E8} and {r.obdmid for r in res[0x7E8]} == set(engine.mode06)

    # Mode 04 functionally: engine sends 7F 04 78 first, then 44; TCM 44 at once.
    assert client.clear_dtcs() == {0x7E8: None, 0x7E9: None}
    assert client.read_dtcs_all() == {0x7E8: [], 0x7E9: []}
    engine.engine_running = True
    assert client.clear_dtcs() == {0x7E8: 0x22, 0x7E9: None}

    # UDS still works on the same nodes (CompositeEcu), physically addressed.
    uds = UdsClient(SoftwareIsoTpLink(router.endpoint([0x7E9]), 0x7E1, 0x7E9, owns_transport=True))
    try:
        assert uds.read_data_by_identifier(0xF187) == b"02E300053E"
    finally:
        uds.close()


def test_physical_link_returns_as_soon_as_its_ecu_answers(two_ecus):
    client, engine, tcm, router, bus = two_ecus
    phys = ObdClient(SoftwareIsoTpLink(router.endpoint([0x7E9]), 0x7E1, 0x7E9, owns_transport=True),
                     timing=ObdTiming(p2=2.0))
    try:
        assert not phys.functional
        t0 = time.monotonic()
        assert phys.read_dtcs() == ["P0730"]
        assert time.monotonic() - t0 < 1.0
        assert phys.supported_pids() == {0x0D, 0x1C, 0x42, 0x01, 0x41}
        with pytest.raises(ObdTimeout):
            phys.read_pid(0x23)
    finally:
        phys.close()


def test_obd_node_sends_preambles_and_survives_handler_errors():
    bus = FakeCanBus()
    brain = SimulatedObdEcu("golf-tdi-2012")
    brain.clear_pending_replies = 2
    node = ObdNode(bus, brain, request_id=0x7E0, response_id=0x7E8, name="e")
    node.start()
    router = CanRouter(bus.attach("tester"))
    raw = router.endpoint([0x7E8])
    try:
        raw.send(__import__("vagtune.transport.base", fromlist=["CanFrame"]).CanFrame(0x7E0, H("01 04 55 55 55 55 55 55")))
        frames = [raw.recv(1.0) for _ in range(3)]
        assert [f.data[:4] for f in frames] == [H("03 7F 04 78"), H("03 7F 04 78"), H("01 44 55 55")]

        def boom(_req):
            raise RuntimeError("bug")
        brain.handle_all = boom                      # type: ignore[assignment]
        raw.send(__import__("vagtune.transport.base", fromlist=["CanFrame"]).CanFrame(0x7E0, H("01 03 55 55 55 55 55 55")))
        f = raw.recv(1.0)
        assert f is not None and f.data[:4] == H("03 7F 03 10") and node.handler_errors == 1
    finally:
        raw.close()
        router.close()
        node.stop()


def test_preset_hooks_populate_car_presets_and_wrap_existing_nodes():
    v = SimulatedVehicle("r32-2008")
    names = v.node_names()
    assert "obd-engine" in names and "obd-tcm" in names
    eng = next(n for n in v.nodes if n.name == "obd-engine")
    assert isinstance(eng, ObdNode) and isinstance(eng.ecu, CompositeEcu) and eng.ecu.uds is None
    assert eng.ecu.obd.profile == "r32-2008" and not eng.ecu.obd.compression_ignition
    assert eng.ecu.obd.values[0x13] == b"\x33"
    assert eng.ecu.handle(H("10 03")) is None                 # ME7.1.1: no UDS on 0x7E0
    tdi = SimulatedVehicle("golf-tdi-2012")
    tdi_eng = next(n for n in tdi.nodes if n.name == "obd-engine")
    assert tdi_eng.ecu.obd.compression_ignition and tdi_eng.ecu.obd.supports_permanent_dtcs

    # Another slice's node already on 0x7E0 -> wrapped, not duplicated.
    bus_vehicle = SimulatedVehicle("demo")
    before = bus_vehicle.node_names()
    brains = add_obd_nodes(bus_vehicle, engine_profile="golf-tdi-2012", tcm_profile=None)
    assert bus_vehicle.node_names() == before
    engine_node = bus_vehicle.node("engine")
    assert isinstance(engine_node.ecu, CompositeEcu) and isinstance(engine_node.ecu.uds, SimulatedEcu)
    assert engine_node.ecu.obd is brains["engine"]
    assert engine_node.ecu.handle(H("22 F1 87")) == b"\x62\xF1\x87" + b"8V0906259H"
    assert engine_node.ecu.handle(H("01 0C")) == H("41 0C 0D 48")
    with bus_vehicle:
        router = CanRouter(bus_vehicle.bus.attach("t"))
        c = ObdClient(SoftwareIsoTpLink(router.endpoint([0x7E8]), 0x7E0, 0x7E8, owns_transport=True), timing=FAST)
        try:
            assert c.vin() == "WVWDM7AJ4CW000002"        # plain UdsNode delivers the final reply
        finally:
            c.close()
            router.close()


def test_two_clients_two_threads_one_router(two_ecus):
    client, engine, tcm, router, bus = two_ecus
    errors: List[str] = []

    def worker(tx: int, rx: int, expect: List[str]) -> None:
        c = ObdClient(SoftwareIsoTpLink(router.endpoint([rx]), tx, rx, owns_transport=True), timing=ObdTiming(p2=0.5))
        try:
            for _ in range(10):
                if c.read_dtcs() != expect:
                    errors.append(f"{rx:X}")
        except Exception as exc:                       # pragma: no cover
            errors.append(repr(exc))
        finally:
            c.close()

    threads = [threading.Thread(target=worker, args=(0x7E0, 0x7E8, ["P0401"])),
               threading.Thread(target=worker, args=(0x7E1, 0x7E9, ["P0730"]))]
    for t in threads:
        t.start()
    for t in threads:
        t.join(10.0)
    assert errors == []
