"""
CLI tests: every subcommand run through ``main()`` against ``--transport fake``.

Assertions are on key substrings of the real output so the user-visible behaviour
is pinned without making the tests brittle to whitespace.
"""

from __future__ import annotations

import os

import pytest

from vagtune.cli import build_parser, main
from vagtune.commands._common import ADDRESS_WORDS, resolve_module
from vagtune.transport.fakebus import reset_default_vehicle
from vagtune.vag import modules as vag_modules

DEF_PATH = os.path.join(os.path.dirname(__file__), "..", "definitions", "simos18.1.example.json")
SIMOS18_SCRIPT = "6802814A10680493080820094A05872212195482499307122011824A058703112010824A0181494C"


@pytest.fixture(autouse=True)
def _fresh_vehicle():
    reset_default_vehicle()
    yield
    reset_default_vehicle()


def run(capsys, *argv) -> tuple[int, str, str]:
    rc = main(list(argv))
    out, err = capsys.readouterr()
    return rc, out, err


def test_parser_lists_all_commands():
    parser = build_parser()
    sub = next(a for a in parser._actions if a.dest == "command")
    assert set(sub.choices) == {"scan", "identify", "dtc", "read-cal", "show-map", "scale-map", "sa2"}


def test_resolve_module_tokens():
    assert resolve_module("engine") is vag_modules.MODULES["engine"]
    assert resolve_module("GATEWAY") is vag_modules.MODULES["gateway"]
    assert resolve_module("01") is vag_modules.MODULES["engine"]
    assert resolve_module("1") is vag_modules.MODULES["engine"]
    assert resolve_module("0x19") is vag_modules.MODULES["gateway"]
    assert resolve_module("19") is vag_modules.MODULES["gateway"]
    assert resolve_module("03").response_id == 0x77D
    assert resolve_module("22").name == "haldex"
    for word, (name, req, resp) in ADDRESS_WORDS.items():
        mod = vag_modules.MODULES[name]
        assert (mod.request_id, mod.response_id) == (req, resp), word
    with pytest.raises(ValueError):
        resolve_module("cluster")
    with pytest.raises(ValueError):
        resolve_module("0x99")


def test_identify_engine(capsys):
    rc, out, _ = run(capsys, "identify", "--transport", "fake")
    assert rc == 0
    assert "ECU Identification" in out
    assert "WVWZZZAUZLW000001" in out
    assert "8V0906259H" in out
    assert "R4 2.0L TFSI" in out
    # The 0.1.0 demo engine's F197 does not name a known family, so no profile line
    # (guess_profile keys on F197; the ODX version F1A2 "SC8_..." is not consulted).
    assert "Detected profile" not in out


def test_identify_prints_detected_profile_when_f197_matches(capsys):
    from vagtune.transport.fakebus import get_default_vehicle
    get_default_vehicle("demo").node("engine").ecu.identifiers[0xF197] = b"SIMOS18.1 R4 2.0L TFSI"
    rc, out, _ = run(capsys, "identify", "--transport", "fake", "--module", "01")
    assert rc == 0
    assert "Detected profile: Continental SIMOS 18.1 (MQB 2.0T)  (key: simos18.1)" in out


def test_identify_gateway_by_address_word(capsys):
    rc, out, _ = run(capsys, "identify", "--transport", "fake", "--module", "19")
    assert rc == 0
    assert "7N0907530C" in out
    assert "J533 Gateway" in out
    assert "Detected profile" not in out


def test_identify_abs_by_name_and_forced_profile(capsys):
    rc, out, _ = run(capsys, "identify", "--module", "abs", "--profile", "simos18.1")
    assert rc == 0
    assert "ESP MK60EC1" in out and "1K0907379AC" in out


def test_identify_bad_module_is_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["identify", "--module", "bogus"])
    assert exc.value.code == 2
    assert "unknown module 'bogus'" in capsys.readouterr().err


def test_scan(capsys):
    rc, out, _ = run(capsys, "scan", "--transport", "fake")
    assert rc == 0
    assert "[engine      ] tx=0x7E0 rx=0x7E8  responded (VIN: WVWZZZAUZLW000001)" in out
    assert "[gateway     ] tx=0x710 rx=0x77A  responded (VIN: WVWZZZAUZLW000001)" in out
    assert "[abs         ] tx=0x713 rx=0x77D  responded (VIN: WVWZZZAUZLW000001)" in out
    assert "[transmission] tx=0x7E1 rx=0x7E9  no response (UdsTimeout)" in out
    assert "[haldex      ] tx=0x70F rx=0x779  no response (UdsTimeout)" in out
    assert "3 module(s) responded." in out


def test_dtc_read_and_clear(capsys):
    rc, out, _ = run(capsys, "dtc", "--transport", "fake")
    assert rc == 0
    assert "2 fault code(s):" in out
    assert "P0112  (0x011200, status 0x2F)  Intake Air Temperature Sensor Circuit Low" in out
    assert "P0561" in out

    rc, out, _ = run(capsys, "dtc", "--transport", "fake", "--module", "19")
    assert rc == 0
    assert out.strip() == "No stored fault codes."

    rc, out, _ = run(capsys, "dtc", "--module", "0x03")
    assert rc == 0
    assert "1 fault code(s):" in out and "C0035" in out

    rc, out, _ = run(capsys, "dtc", "--transport", "fake", "--clear")
    assert rc == 0 and "Cleared diagnostic information." in out
    rc, out, _ = run(capsys, "dtc", "--transport", "fake")
    assert rc == 0 and "No stored fault codes." in out


def test_read_cal_show_map_scale_map(capsys, tmp_path):
    stock = tmp_path / "stock.bin"
    rc, out, err = run(capsys, "read-cal", "--transport", "fake", "--out", str(stock))
    assert rc == 1 and "No SA2 script available" in err      # profile cannot be auto-detected
    rc, out, _ = run(capsys, "read-cal", "--transport", "fake", "--profile", "simos18.1", "--out", str(stock))
    assert rc == 0
    assert "reading calibration..." in out
    assert f"Wrote 524288 bytes to {stock}" in out
    assert stock.stat().st_size == 524288

    rc, out, _ = run(capsys, "show-map", "--def", DEF_PATH, "--bin", str(stock))
    assert rc == 0
    assert "Maps in" in out and "boost_target" in out

    rc, out, _ = run(capsys, "show-map", "--def", DEF_PATH, "--bin", str(stock), "--map", "boost_target")
    assert rc == 0
    assert out.startswith("boost_target  [8x8]")

    tune = tmp_path / "tune.bin"
    rc, out, _ = run(capsys, "scale-map", "--def", DEF_PATH, "--bin", str(stock), "--map", "boost_target",
                     "--multiplier", "1.05", "--clamp", "300", "--out", str(tune))
    assert rc == 0
    assert "Before:" in out and "After:" in out
    assert "Applied x1.05 (clamped at 300.0)" in out
    assert "byte(s) changed" in out
    assert f"Wrote modified image to {tune}" in out
    assert tune.stat().st_size == 524288
    assert tune.read_bytes() != stock.read_bytes()

    rc, out, _ = run(capsys, "scale-map", "--def", DEF_PATH, "--bin", str(stock), "--map", "boost_target",
                     "--multiplier", "1.0")
    assert rc == 0 and "no changes" in out and "(no --out given; changes not saved)" in out


def test_sa2(capsys):
    rc, out, _ = run(capsys, "sa2", "--script", SIMOS18_SCRIPT, "--seed", "1A2B3C4D")
    assert rc == 0
    assert "seed = 0x1A2B3C4D" in out
    assert "key  = 0x" in out and "key bytes = " in out


def test_vehicle_preset_without_nodes_times_out_cleanly(capsys):
    rc, out, err = run(capsys, "identify", "--transport", "fake", "--vehicle", "r32-2008")
    assert rc == 1
    assert "error: no response to service 0x10" in err


def test_j2534_fw_without_dll_reports_error(capsys, monkeypatch):
    monkeypatch.delenv("VAGTUNE_J2534_DLL", raising=False)
    rc, out, err = run(capsys, "identify", "--transport", "j2534-fw")
    assert rc == 1
    assert "error:" in err and "J2534" in err


def test_verbose_reraises(capsys, monkeypatch):
    monkeypatch.delenv("VAGTUNE_J2534_DLL", raising=False)
    from vagtune.transport.base import TransportError
    with pytest.raises(TransportError):
        main(["-vv", "identify", "--transport", "j2534"])
