"""
CLI tests for every ``obd`` subcommand through ``vagtune.cli.main`` against a
test-only simulated vehicle preset hosting two CompositeEcu nodes (engine 0x7E0/0x7E8
+ DSG 0x7E1/0x7E9), plus the car presets populated by the OBD hooks.
"""

from __future__ import annotations

import pytest

from vagtune.cli import build_parser, main
from vagtune.obd.sim import add_obd_nodes
from vagtune.transport.fake import SimulatedEcu
from vagtune.transport.fakebus import SimulatedVehicle, get_default_vehicle, reset_default_vehicle

PRESET = "obd-test-r32"
PRESET_TDI = "obd-test-tdi"
FAST = ("--window", "0.1")


def _hook_r32(vehicle: SimulatedVehicle) -> None:
    brains = add_obd_nodes(vehicle, engine_profile="r32-2008", tcm_profile="dq250-tcm",
                           engine_uds=SimulatedEcu(), tcm_uds=SimulatedEcu())
    brains["engine"].dtcs = ["P0300", "P0171"]
    brains["engine"].pending_dtcs = ["P0420"]
    brains["tcm"].dtcs = ["P0730"]


def _hook_tdi(vehicle: SimulatedVehicle) -> None:
    brains = add_obd_nodes(vehicle, engine_profile="golf-tdi-2012", tcm_profile=None, engine_uds=SimulatedEcu())
    brains["engine"].permanent_dtcs = ["P2002"]


@pytest.fixture(scope="module", autouse=True)
def _presets():
    SimulatedVehicle.register_preset_hook(PRESET, _hook_r32)
    SimulatedVehicle.register_preset_hook(PRESET_TDI, _hook_tdi)
    yield
    for name in (PRESET, PRESET_TDI):
        SimulatedVehicle.PRESETS.pop(name, None)
        SimulatedVehicle._PRESET_HOOKS.pop(name, None)


@pytest.fixture(autouse=True)
def _fresh_vehicle():
    reset_default_vehicle()
    yield
    reset_default_vehicle()


def run(capsys, *argv: str) -> tuple[int, str, str]:
    rc = main(["obd", *argv, "--vehicle", PRESET, *FAST] if "--vehicle" not in argv else ["obd", *argv, *FAST])
    out, err = capsys.readouterr()
    return rc, out, err


def test_parser_registers_obd_subcommands():
    parser = build_parser()
    sub = next(a for a in parser._actions if a.dest == "command")
    assert "obd" in sub.choices
    osub = next(a for a in sub.choices["obd"]._actions if a.dest == "obd_command")
    assert set(osub.choices) == {"status", "pids", "read", "dtc", "clear", "vin", "readiness", "monitors", "freeze"}


def test_status_two_responders(capsys):
    rc, out, _ = run(capsys, "status")
    assert rc == 0
    assert "--- ECU 0x7E8 (#1, request 0x7E0) ---" in out
    assert "--- ECU 0x7E9 (#2, request 0x7E1) ---" in out
    assert "MIL: ON    confirmed DTCs: 2    ignition: spark    readiness: INCOMPLETE" in out
    assert "MIL: ON    confirmed DTCs: 1    ignition: spark    readiness: complete" in out
    assert "Catalyst                     yes        no" in out
    assert "Evaporative system           yes        no" in out
    assert "Oxygen sensor heater         yes        yes" in out
    assert "Heated catalyst              no         -" in out


def test_status_compression_ignition(capsys):
    rc, out, _ = run(capsys, "status", "--vehicle", PRESET_TDI)
    assert rc == 0
    assert "---" not in out                                  # a single responder: no header
    assert "ignition: compression" in out
    assert "NOx / SCR aftertreatment     yes        no" in out
    assert "PM filter                    yes        yes" in out
    assert "Evaporative" not in out


def test_readiness(capsys):
    rc, out, _ = run(capsys, "readiness")
    assert rc == 0
    assert "Enabled now" in out and "Done now" in out
    assert "Not yet complete: Catalyst, Evaporative system" in out
    assert "Not yet complete: none" in out


def test_pids(capsys):
    rc, out, _ = run(capsys, "pids")
    assert rc == 0
    assert "0C  Engine speed" in out and "13  O2 sensors present (2 banks)" in out
    assert "supported in mode 01:" in out
    assert "3 supported in mode 01" not in out and "5 supported in mode 01" in out   # the TCM: 0D 1C 42 + 01 41
    rc, out, _ = run(capsys, "pids", "--mode", "09")
    assert rc == 0 and "02  VIN" in out and "0A  ECU name" in out
    rc, out, _ = run(capsys, "pids", "--mode", "06")
    assert rc == 0 and "A7  Misfire cylinder 6 data" in out and "21  Catalyst monitor bank 1" in out
    rc, out, _ = run(capsys, "pids", "--mode", "02")
    assert rc == 0 and "02  DTC that caused freeze frame" in out


def test_read(capsys):
    rc, out, _ = run(capsys, "read", "0C", "05", "0x13", "1c", "42")
    assert rc == 0
    assert "0C  Engine speed: 800 rpm" in out
    assert "05  Engine coolant temperature: 90 °C" in out
    assert "13  O2 sensors present (2 banks): B1S1=yes, B1S2=yes, B1S3=no" in out
    assert "1C  OBD standard this vehicle conforms to: OBD-II (CARB)" in out
    assert "42  Control module voltage: 14.4 V" in out
    assert "not supported here: 05 0C 13" in out            # the TCM block
    rc, out, _ = run(capsys, "read", "5E")
    assert rc == 1 and "No ECU answered" in out
    with pytest.raises(SystemExit):
        main(["obd", "read", "zz"])


def test_read_physical_single_ecu(capsys):
    rc, out, _ = run(capsys, "read", "0D", "--physical", "--module", "02")
    assert rc == 0
    assert "---" not in out and "0D  Vehicle speed: 0 km/h" in out


def test_dtc_variants(capsys):
    rc, out, _ = run(capsys, "dtc")
    assert rc == 0
    assert "2 confirmed fault code(s):" in out
    assert "P0300  Random/Multiple Cylinder Misfire Detected" in out and "P0171" in out
    assert "P0730" in out and "3 confirmed fault code(s) across 2 ECU(s)." in out
    rc, out, _ = run(capsys, "dtc", "--pending")
    assert rc == 0 and "P0420" in out and "No pending fault codes." in out
    rc, out, _ = run(capsys, "dtc", "--permanent")
    assert rc == 1 and "No ECU answered mode 0A (permanent DTCs)." in out
    rc, out, _ = run(capsys, "dtc", "--permanent", "--vehicle", PRESET_TDI)
    assert rc == 0 and "1 permanent fault code(s):" in out and "P2002" in out
    rc, out, err = run(capsys, "dtc", "--pending", "--permanent")
    assert rc == 2 and "choose one" in err


def test_clear_requires_yes_and_reports_refusal(capsys):
    rc, out, _ = run(capsys, "clear")
    assert rc == 2 and "Refusing to clear" in out
    engine = get_default_vehicle(PRESET).node("obd-engine").ecu.obd
    assert engine.clears == 0 and engine.dtcs == ["P0300", "P0171"]

    rc, out, _ = run(capsys, "clear", "--yes")
    assert rc == 0
    assert "ECU 0x7E8 (#1, request 0x7E0): cleared" in out and "ECU 0x7E9 (#2, request 0x7E1): cleared" in out
    assert "2 of 2 ECU(s) cleared" in out
    assert engine.clears == 1 and engine.dtcs == []
    rc, out, _ = run(capsys, "dtc")
    assert rc == 0 and "No confirmed fault codes." in out and "fault code(s):" not in out

    engine.engine_running = True
    rc, out, _ = run(capsys, "clear", "--yes")
    assert rc == 1
    assert "ECU 0x7E8 (#1, request 0x7E0): refused, conditionsNotCorrect (NRC 0x22) (engine running?)" in out
    assert "1 of 2 ECU(s) cleared" in out


def test_vin(capsys):
    rc, out, _ = run(capsys, "vin")
    assert rc == 0
    assert "VIN        WVWKD71K58W000001" in out
    assert "CALID      022906032GR 0006" in out and "CALID      02E300053E 1211" in out
    assert "CVN        5A3C18F0" in out and "CVN        00A1B2C3" in out
    assert "ECU name   ECM-EngineControl" in out and "ECU name   TCM-TransmissionCtl" in out
    assert "supported InfoTypes: 02 04 06 08 0A" in out and "supported InfoTypes: 04 06 0A" in out
    assert "OBDCOND" not in out
    rc, out, _ = run(capsys, "vin", "--ipt", "--vehicle", PRESET_TDI)
    assert rc == 0 and "IPT (compression):" in out and "HCCATCOMP    200" in out and "VIN        WVWDM7AJ4CW000002" in out


def test_monitors(capsys):
    rc, out, _ = run(capsys, "monitors")
    assert rc == 0
    assert "---" not in out                                  # only the engine supports Mode 06
    assert "Oxygen sensor monitor B1S1 / Rich-to-lean sensor threshold voltage" in out
    assert "0.365" in out and "PASS [V]" in out
    assert "not run [counts]" in out
    assert "Misfire cylinder 6 data / EWMA misfire counts" in out
    assert "record(s); 0 failing." in out
    rc, out, _ = run(capsys, "monitors", "A2")
    assert rc == 0 and "2 record(s)" in out and "Oxygen sensor" not in out
    rc, out, _ = run(capsys, "monitors", "--vehicle", PRESET_TDI)
    assert rc == 0 and "PM filter monitor bank 1" in out and "kPa" in out


def test_freeze(capsys):
    rc, out, _ = run(capsys, "freeze")
    assert rc == 0
    assert "Freeze frame 0 stored for P0300  Random/Multiple Cylinder Misfire Detected" in out
    assert "0C  Engine speed [frame 0]: 800 rpm" in out
    assert "Freeze frame 0 stored for P0730" in out and "0D  Vehicle speed [frame 0]: 0 km/h" in out
    rc, out, _ = run(capsys, "freeze", "--vehicle", PRESET_TDI)
    assert rc == 0 and "No freeze frame 0 stored (PID 02 = 0000)." in out and "[frame 0]" not in out
    rc, out, _ = run(capsys, "freeze", "0C", "05", "--frame", "0")
    assert rc == 0 and "05  Engine coolant temperature [frame 0]: 90 °C" in out and "0B  Intake" not in out
    rc, out, _ = run(capsys, "freeze", "--frame", "1", "0C")
    assert rc == 0 and out.count("No freeze frame 1 stored (PID 02 = 0000).") == 2 and "[frame" not in out
    rc = main(["obd", "freeze", "--vehicle", "demo", *FAST])
    out, _ = capsys.readouterr()
    assert rc == 1 and "No ECU answered Mode 02 for frame 0." in out


def test_batch_bitmaps_works_for_every_mode(capsys):
    rc, out, _ = run(capsys, "freeze", "--batch-bitmaps")
    assert rc == 0 and "0C  Engine speed [frame 0]: 800 rpm" in out
    rc, out, _ = run(capsys, "pids", "--mode", "02", "--batch-bitmaps")
    assert rc == 0 and "02  DTC that caused freeze frame" in out
    rc, out, _ = run(capsys, "pids", "--batch-bitmaps")
    assert rc == 0 and "0C  Engine speed" in out
    engine = get_default_vehicle(PRESET).node("obd-engine").ecu.obd
    assert all(len(r) <= 7 for r in engine.requests)


def test_pids_mode_is_restricted_to_bitmap_services(capsys):
    engine = get_default_vehicle(PRESET).node("obd-engine").ecu.obd
    for bad in ("03", "04", "07", "0A", "0B"):
        with pytest.raises(SystemExit):
            main(["obd", "pids", "--mode", bad, "--vehicle", PRESET, *FAST])
    assert engine.requests == []                               # nothing malformed reached the bus
    _, err = capsys.readouterr()
    assert "has no supported-ID bitmaps" in err
    rc, out, _ = run(capsys, "pids", "--mode", "08")
    assert rc == 1 and "No ECU answered the mode 08 supported-ID request." in out


def test_window_must_be_positive(capsys):
    for bad in ("0", "-1", "abc"):
        with pytest.raises(SystemExit):
            main(["obd", "status", "--vehicle", PRESET, "--window", bad])
    _, err = capsys.readouterr()
    assert "window must be > 0" in err


def test_car_presets_answer_obd_but_not_uds(capsys):
    rc, out, _ = run(capsys, "status", "--vehicle", "r32-2008")
    assert rc == 0 and "ignition: spark" in out and "ECU 0x7E9" in out
    rc, out, _ = run(capsys, "vin", "--vehicle", "golf-tdi-2012")
    assert rc == 0 and "WVWDM7AJ4CW000002" in out
    # The KWP-only R32 engine stays silent on UDS -> identify times out, as before.
    rc, out, err = main(["identify", "--transport", "fake", "--vehicle", "r32-2008"]), *capsys.readouterr()
    assert rc == 1 and "no response to service 0x10" in err


def test_no_responder_is_a_clean_error(capsys):
    rc = main(["obd", "status", "--vehicle", "demo", *FAST])     # demo preset has no OBD brain
    out, err = capsys.readouterr()
    assert rc == 1 and "No ECU answered Mode 01 PID 01." in out
    rc = main(["obd", "vin", "--vehicle", "demo", *FAST])
    out, err = capsys.readouterr()
    assert rc == 1 and "No ECU answered Mode 09 InfoType 00." in out
