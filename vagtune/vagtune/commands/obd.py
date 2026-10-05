"""Generic OBD-II commands: ``obd status|pids|read|dtc|clear|vin|readiness|monitors|freeze``.

Every subcommand talks *functionally* (0x7DF, answers from 0x7E8..0x7EF) by default,
so the engine ECU and a DSG that speaks OBD both answer; when more than one ECU
replies, each block is printed under a per-responder header. ``--physical`` addresses
the ``--module`` ids instead (one ECU). ``obd clear`` writes to every emissions ECU
and therefore needs ``--yes``.
"""

from __future__ import annotations

ORDER = 30  # help ordering: after diag (10) and calibration

import argparse
import logging
from typing import Any, Callable, Dict, List, Optional, Tuple

from ..obd import sim as _obd_sim  # noqa: F401  (registers the r32/golf-tdi preset hooks)
from ..obd import pids as P
from ..obd.client import (
    BITMAP_MODES,
    MODE_DTC_CONFIRMED,
    MODE_DTC_PENDING,
    MODE_DTC_PERMANENT,
    Mode06Result,
    ObdClient,
    ObdTiming,
    ObdValue,
)
from ..transport.context import TransportContext
from ..uds.exceptions import NRC_NAMES
from ..vag.dtc import describe_dtc
from ._common import open_context

log = logging.getLogger(__name__)

FUNCTIONAL_TX = 0x7DF
ENGINE_RX = 0x7E8
RESPONDER_RANGE = range(0x7E9, 0x7F0)


# ------------------------------------------------------------------ plumbing

def _open_client(args: argparse.Namespace) -> Tuple[TransportContext, ObdClient]:
    ctx = open_context(args)
    try:
        if args.physical:
            mod = args.module
            link = ctx.isotp_link(mod.request_id, mod.response_id)
        else:
            link = ctx.isotp_link(FUNCTIONAL_TX, ENGINE_RX, extra_rx_ids=RESPONDER_RANGE)
    except Exception:
        ctx.close()
        raise
    client = ObdClient(link, timing=ObdTiming(p2=args.window), batch_bitmaps=args.batch_bitmaps)
    return ctx, client


def ecu_label(rid: int) -> str:
    """``0x7E8`` -> ``ECU 0x7E8 (#1, request 0x7E0)`` per ISO 15765-4 Table 3."""
    if 0x7E8 <= rid <= 0x7EF:
        return f"ECU 0x{rid:03X} (#{rid - 0x7E7}, request 0x{rid - 8:03X})"
    return f"ECU 0x{rid:03X}"


def _blocks(per_ecu: Dict[int, Any], body: Callable[[int, Any], None]) -> None:
    """Print ``body(rid, value)`` per responder, with a header when there are several."""
    many = len(per_ecu) > 1
    for i, rid in enumerate(sorted(per_ecu)):
        if many:
            if i:
                print()
            print(f"--- {ecu_label(rid)} ---")
        body(rid, per_ecu[rid])


def _parse_pid(token: str) -> int:
    t = token.strip().lower()
    if t.startswith("0x"):
        t = t[2:]
    try:
        pid = int(t, 16)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"PID {token!r} is not a hex byte") from exc
    if not 0 <= pid <= 0xFF:
        raise argparse.ArgumentTypeError(f"PID {token!r} out of range 00..FF")
    return pid


def _parse_mode(token: str) -> int:
    """``--mode`` for ``obd pids``: only the services that carry Annex A bitmaps
    (01, 02, 06, 08, 09). ``03 00`` etc. would be a malformed request broadcast to
    every ECU, so anything else is an argument error."""
    mode = _parse_pid(token)
    if mode not in BITMAP_MODES:
        raise argparse.ArgumentTypeError(
            f"mode {token!r} has no supported-ID bitmaps; choose one of "
            + ", ".join(f"{m:02X}" for m in BITMAP_MODES))
    return mode


def _parse_window(token: str) -> float:
    """``--window`` must be a positive number of seconds: with 0 the client would only
    take a reply that is already buffered, which never happens on real hardware."""
    try:
        value = float(token)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"window {token!r} is not a number of seconds") from exc
    if not value > 0:
        raise argparse.ArgumentTypeError(f"window must be > 0 seconds (ISO P2 max is 0.05), got {token}")
    return value


def _yes_no(flag: bool) -> str:
    return "yes" if flag else "no"


def _print_monitor_table(status: P.MonitorStatus, this_cycle: Optional[P.MonitorStatus] = None) -> None:
    print(f"  MIL: {'ON' if status.mil else 'off'}    confirmed DTCs: {status.dtc_count}    "
          f"ignition: {status.ignition}    readiness: {'complete' if status.ready else 'INCOMPLETE'}")
    if this_cycle is None:
        print(f"  {'Monitor':<28} {'Supported':<10} {'Complete':<10}")
        for m in status.all_monitors():
            print(f"  {m.label:<28} {_yes_no(m.available):<10} {_yes_no(m.complete) if m.available else '-':<10}")
        return
    print(f"  {'Monitor':<28} {'Supported':<10} {'Complete':<10} {'Enabled now':<12} {'Done now':<10}")
    for m in status.all_monitors():
        t = (this_cycle.continuous.get(m.name) or this_cycle.non_continuous.get(m.name))
        enabled = _yes_no(t.available) if t else "?"
        done = (_yes_no(t.complete) if t and t.available else "-") if t else "?"
        print(f"  {m.label:<28} {_yes_no(m.available):<10} {_yes_no(m.complete) if m.available else '-':<10} "
              f"{enabled:<12} {done:<10}")


# ---------------------------------------------------------------- commands

def cmd_status(args: argparse.Namespace) -> int:
    ctx, client = _open_client(args)
    try:
        statuses = client.monitor_status_all()
        if not statuses:
            print("No ECU answered Mode 01 PID 01.")
            return 1
        _blocks(statuses, lambda rid, s: _print_monitor_table(s))
        return 0
    finally:
        client.close()
        ctx.close()


def cmd_readiness(args: argparse.Namespace) -> int:
    ctx, client = _open_client(args)
    try:
        since = client.monitor_status_all()
        if not since:
            print("No ECU answered Mode 01 PID 01.")
            return 1
        now = client.monitor_status_all(this_cycle=True)

        def body(rid: int, s: P.MonitorStatus) -> None:
            _print_monitor_table(s, now.get(rid))
            if rid not in now:
                print("  (PID 41 'this drive cycle' not supported by this ECU)")
            pending = s.incomplete()
            print(f"  Not yet complete: {', '.join(P.MONITOR_LABELS.get(n, n) for n in pending) or 'none'}")

        _blocks(since, body)
        return 0
    finally:
        client.close()
        ctx.close()


def cmd_pids(args: argparse.Namespace) -> int:
    ctx, client = _open_client(args)
    try:
        mode = args.mode
        per_ecu = client.supported_ids_all(mode)
        if not per_ecu:
            print(f"No ECU answered the mode {mode:02X} supported-ID request.")
            return 1

        def body(rid: int, ids: set) -> None:
            print(f"  {len(ids)} supported in mode {mode:02X}:")
            for pid in sorted(ids):
                if mode in (0x01, 0x02):
                    name = P.pid_name(pid)
                elif mode == 0x06:
                    name = P.obdmid_name(pid)
                elif mode == 0x09:
                    name = P.infotype_name(pid)
                else:
                    name = ""
                print(f"  {pid:02X}  {name}")

        _blocks(per_ecu, body)
        return 0
    finally:
        client.close()
        ctx.close()


def _print_values(values: Dict[int, ObdValue], indent: str = "  ") -> None:
    for pid in sorted(values):
        v = values[pid]
        frame = f" [frame {v.frame}]" if v.frame is not None else ""
        print(f"{indent}{pid:02X}  {v.name}{frame}: {v.pretty()}")


def cmd_read(args: argparse.Namespace) -> int:
    ctx, client = _open_client(args)
    try:
        per_ecu = client.read_pids_all(args.pids)
        if not per_ecu:
            print("No ECU answered (PID(s) " + " ".join(f"{p:02X}" for p in args.pids) + " unsupported?).")
            return 1
        wanted = set(args.pids)

        def body(rid: int, values: Dict[int, ObdValue]) -> None:
            _print_values(values)
            missing = sorted(wanted - set(values))
            if missing:
                print("  not supported here: " + " ".join(f"{p:02X}" for p in missing))

        _blocks(per_ecu, body)
        return 0
    finally:
        client.close()
        ctx.close()


def cmd_dtc(args: argparse.Namespace) -> int:
    if args.pending and args.permanent:
        print("error: choose one of --pending / --permanent", file=__import__("sys").stderr)
        return 2
    mode = MODE_DTC_PENDING if args.pending else MODE_DTC_PERMANENT if args.permanent else MODE_DTC_CONFIRMED
    kind = {MODE_DTC_CONFIRMED: "confirmed", MODE_DTC_PENDING: "pending", MODE_DTC_PERMANENT: "permanent"}[mode]
    ctx, client = _open_client(args)
    try:
        per_ecu = client.read_dtcs_all(mode)
        if not per_ecu:
            print(f"No ECU answered mode {mode:02X} ({kind} DTCs).")
            return 1
        total = sum(len(v) for v in per_ecu.values())

        def body(rid: int, codes: List[str]) -> None:
            if not codes:
                print(f"  No {kind} fault codes.")
                return
            print(f"  {len(codes)} {kind} fault code(s):")
            for code in codes:
                print(f"    {code}  {describe_dtc(code)}")

        _blocks(per_ecu, body)
        if len(per_ecu) > 1:
            print(f"\n{total} {kind} fault code(s) across {len(per_ecu)} ECU(s).")
        return 0
    finally:
        client.close()
        ctx.close()


def cmd_clear(args: argparse.Namespace) -> int:
    if not args.yes:
        print("Refusing to clear: Mode 04 erases confirmed/pending DTCs, freeze frames, readiness "
              "and Mode 06 results in EVERY emissions ECU. Re-run with --yes to confirm.")
        return 2
    ctx, client = _open_client(args)
    try:
        results = client.clear_dtcs()
        ok = 0
        for rid in sorted(results):
            nrc = results[rid]
            if nrc is None:
                ok += 1
                print(f"  {ecu_label(rid)}: cleared")
            else:
                hint = " (engine running?)" if nrc == 0x22 else ""
                print(f"  {ecu_label(rid)}: refused, {NRC_NAMES.get(nrc, '?')} (NRC 0x{nrc:02X}){hint}")
        print(f"{ok} of {len(results)} ECU(s) cleared diagnostic information. Permanent (mode 0A) DTCs "
              "are only cleared by the ECU itself after the monitor passes.")
        return 0 if ok == len(results) else 1
    finally:
        client.close()
        ctx.close()


def cmd_vin(args: argparse.Namespace) -> int:
    ctx, client = _open_client(args)
    try:
        supported = client.supported_infotypes_all()
        if not supported:
            print("No ECU answered Mode 09 InfoType 00.")
            return 1
        wanted = [(0x02, "VIN"), (0x04, "CALID"), (0x06, "CVN"), (0x0A, "ECU name")]
        if args.ipt:
            wanted += [(0x08, "IPT (spark)"), (0x0B, "IPT (compression)")]
        lines: Dict[int, List[str]] = {rid: [] for rid in supported}
        for infotype, label in wanted:
            if not any(infotype in ids for ids in supported.values()):
                continue
            for rid, info in client.vehicle_info_all(infotype).items():
                if isinstance(info.value, dict):
                    lines.setdefault(rid, []).append(f"{label}:")
                    lines[rid] += [f"    {k:<12} {v}" for k, v in info.value.items()]
                elif isinstance(info.value, list):
                    lines.setdefault(rid, []).append(f"{label:<10} " + ", ".join(info.value))
                else:
                    lines.setdefault(rid, []).append(f"{label:<10} {info.value}")

        def body(rid: int, rows: List[str]) -> None:
            print(f"  supported InfoTypes: " + " ".join(f"{i:02X}" for i in sorted(supported.get(rid, ()))))
            for row in rows:
                print(f"  {row}")

        _blocks(lines, body)
        return 0
    finally:
        client.close()
        ctx.close()


def cmd_monitors(args: argparse.Namespace) -> int:
    ctx, client = _open_client(args)
    try:
        per_ecu = client.monitor_test_results_all(args.obdmids or None)
        if not per_ecu:
            print("No ECU returned Mode 06 test results.")
            return 1

        def body(rid: int, results: List[Mode06Result]) -> None:
            print(f"  {'OBDMID':<6} {'TID':<4} {'Monitor / test':<70} {'Value':>12} {'Min':>12} {'Max':>12}  Result")
            last_mid = None
            for r in results:
                verdict = "not run" if not r.completed else ("PASS" if r.passed else "FAIL")
                mid_txt = f"{r.obdmid:02X}" if r.obdmid != last_mid else ""
                name = f"{r.obdmid_name} / {r.tid_name}" if r.obdmid != last_mid else f"  / {r.tid_name}"
                last_mid = r.obdmid
                fmt = lambda x: P.format_value(x, "", None, 4)  # noqa: E731
                print(f"  {mid_txt:<6} {r.tid:02X}   {name[:70]:<70} {fmt(r.value):>12} {fmt(r.min):>12} "
                      f"{fmt(r.max):>12}  {verdict} [{r.unit}]")
            print(f"  {len(results)} record(s); {sum(1 for r in results if r.completed and not r.passed)} failing.")

        _blocks(per_ecu, body)
        return 0
    finally:
        client.close()
        ctx.close()


def cmd_freeze(args: argparse.Namespace) -> int:
    ctx, client = _open_client(args)
    try:
        per_ecu = client.freeze_frame_all(args.pids or None, args.frame)
        if not per_ecu:
            print(f"No ECU answered Mode 02 for frame {args.frame}.")
            return 1

        def body(rid: int, values: Dict[int, ObdValue]) -> None:
            dtc = values.get(0x02)
            if dtc is not None and dtc.value is None:
                print(f"  No freeze frame {args.frame} stored (PID 02 = 0000).")
            elif dtc is not None:
                print(f"  Freeze frame {args.frame} stored for {dtc.value}  {describe_dtc(dtc.value)}")
            _print_values({p: v for p, v in values.items() if p != 0x02})

        _blocks(per_ecu, body)
        return 0
    finally:
        client.close()
        ctx.close()


# ---------------------------------------------------------------- registry

def _add_obd_args(sp: argparse.ArgumentParser, add_common_args: Callable[[argparse.ArgumentParser], None]) -> None:
    add_common_args(sp)
    sp.add_argument("--physical", action="store_true",
                    help="address the --module ids physically instead of broadcasting on 0x7DF")
    sp.add_argument("--window", type=_parse_window, default=0.25, metavar="SECONDS",
                    help="P2 collection window for responders, > 0 (ISO: 50 ms; default 0.25)")
    sp.add_argument("--batch-bitmaps", action="store_true",
                    help="request supported-ID bitmaps several per message (six; three for Mode 02) "
                         "instead of one per message")


def register(sub: argparse._SubParsersAction, add_common_args: Callable[[argparse.ArgumentParser], None]) -> None:
    obd = sub.add_parser("obd", help="generic OBD-II (SAE J1979) over 0x7DF: status, PIDs, DTCs, VIN, mode 06")
    osub = obd.add_subparsers(dest="obd_command", required=True)

    sp = osub.add_parser("status", help="MIL, DTC count and readiness (PID 01)")
    _add_obd_args(sp, add_common_args)
    sp.set_defaults(func=cmd_status)

    sp = osub.add_parser("readiness", help="readiness since clear (PID 01) and this drive cycle (PID 41)")
    _add_obd_args(sp, add_common_args)
    sp.set_defaults(func=cmd_readiness)

    sp = osub.add_parser("pids", help="list supported PIDs (or OBDMIDs / InfoTypes with --mode)")
    _add_obd_args(sp, add_common_args)
    sp.add_argument("--mode", type=_parse_mode, default=0x01, help="01 (default), 02, 06, 08 or 09")
    sp.set_defaults(func=cmd_pids)

    sp = osub.add_parser("read", help="read and decode Mode 01 PIDs")
    _add_obd_args(sp, add_common_args)
    sp.add_argument("pids", nargs="+", type=_parse_pid, metavar="PID", help="hex PID(s), e.g. 0C 05 10")
    sp.set_defaults(func=cmd_read)

    sp = osub.add_parser("dtc", help="read confirmed (03), --pending (07) or --permanent (0A) DTCs")
    _add_obd_args(sp, add_common_args)
    sp.add_argument("--pending", action="store_true")
    sp.add_argument("--permanent", action="store_true")
    sp.set_defaults(func=cmd_dtc)

    sp = osub.add_parser("clear", help="Mode 04: clear DTCs, freeze frames and readiness in every ECU")
    _add_obd_args(sp, add_common_args)
    sp.add_argument("--yes", action="store_true", help="required: this writes to every emissions ECU")
    sp.set_defaults(func=cmd_clear)

    sp = osub.add_parser("vin", help="Mode 09: VIN, calibration IDs, CVNs, ECU names")
    _add_obd_args(sp, add_common_args)
    sp.add_argument("--ipt", action="store_true", help="also print in-use performance tracking counters")
    sp.set_defaults(func=cmd_vin)

    sp = osub.add_parser("monitors", help="Mode 06 on-board monitoring test results")
    _add_obd_args(sp, add_common_args)
    sp.add_argument("obdmids", nargs="*", type=_parse_pid, metavar="OBDMID", help="limit to these OBDMIDs (hex)")
    sp.set_defaults(func=cmd_monitors)

    sp = osub.add_parser("freeze", help="Mode 02 freeze frame")
    _add_obd_args(sp, add_common_args)
    sp.add_argument("--frame", type=int, default=0, help="frame number (default 0)")
    sp.add_argument("pids", nargs="*", type=_parse_pid, metavar="PID", help="PIDs to read (default: all supported)")
    sp.set_defaults(func=cmd_freeze)
