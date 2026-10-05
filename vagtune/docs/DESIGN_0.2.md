# vagtune 0.2.0 design — "every module" diagnostics for a 2008 R32 and a 2012 Golf TDI

Status: binding spec for the 0.2.0 implementation. Interfaces below are fixed so that
independent slices integrate without edits to each other's files. Protocol *facts*
(byte values, formulas, tables) come from `docs/PROTOCOL_FACTS.md`; this file is about
*structure*.

## 1. Why the architecture changes

The owner's cars are PQ35 (Golf Mk5/Mk6 platform):

| Car | Engine ECU | Protocol reality |
|-----|-----------|------------------|
| 2008 R32 Mk5 (BUB VR6) | Bosch ME7.1.1 | Almost every module speaks **KWP2000 over VW TP 2.0** (CAN). Only generic OBD-II is UDS-style ISO-TP. |
| 2012 Golf TDI Mk6 (CJAA) | Bosch EDC17CP14 | **Mixed**: engine, ABS, gateway, cluster, BCM, airbag are UDS over ISO-TP; DSG (02E) and several body/comfort modules are still TP 2.0 / KWP2000. |

0.1.0 could only speak UDS to one fixed CAN ID pair. 0.2.0 therefore adds a second
transport (TP 2.0), a second application protocol (KWP2000), generic OBD-II, a bus-wide
module discovery, and a frame-level simulated *vehicle* so all of it is testable offline.

Everything stays layered. Dependency direction (no upward imports):

```
transport  <-  (isotp, tp20, router, fakebus, context)
uds, kwp, obd  <-  transport
vag        <-  uds, kwp, obd, transport      (VAG knowledge + sessions + autoscan)
calibration, flash, datalog  <-  vag
commands   <-  everything (CLI only; the future GUI calls the same library objects)
```

## 2. Transport layer

### 2.1 `transport/router.py` — one physical bus, many logical links (NEW, foundation)

Problem: ISO-TP links, TP 2.0 channels, the OBD functional link and keepalive threads
all need to read from the *same* CAN interface at the same time. A link that calls
`transport.recv()` directly steals frames meant for another link.

```python
class CanRouter:
    def __init__(self, transport: RawCanTransport, *, name: str = "") -> None
    def endpoint(self, accept: Iterable[int] | Callable[[CanFrame], bool] | None = None,
                 *, name: str = "", queue_size: int = 4096) -> "RouterEndpoint"
        # accept=None  -> receives every frame (monitor / sniffer)
        # accept=ids   -> receives frames whose arbitration_id is in the set
    def send(self, frame: CanFrame) -> None          # serialised with a lock
    def send_many(self, frames: Sequence[CanFrame]) -> None
    def close(self) -> None                           # stops reader thread, closes transport
    @property transport -> RawCanTransport
    stats: dict (rx_frames, tx_frames, dropped_unmatched, dropped_overflow)

class RouterEndpoint(RawCanTransport):
    # A RawCanTransport view: send() -> router.send(); recv() -> own queue;
    # flush_rx() -> clears own queue; set_accept_ids() -> replaces the accept set;
    # close() -> unsubscribes. open() is a no-op (the router owns the real transport).
```

* One daemon reader thread per router, started lazily on first `endpoint()`; it calls
  `transport.recv(0.05)` in a loop and fans frames out to every endpoint whose
  predicate matches (a frame may go to several endpoints, e.g. a sniffer).
* Endpoint queues are bounded; on overflow the oldest frame is dropped and
  `stats["dropped_overflow"]` increments (logged at debug).
* `SoftwareIsoTpLink(router.endpoint([rx_id]), tx_id, rx_id)` works unchanged.
* `SoftwareIsoTpLink` gains an optional `extra_rx_ids: Iterable[int] = ()` so a
  simulated ECU can listen on both its physical request id and the functional 0x7DF.

### 2.2 `transport/tp20.py` — VW TP 2.0 (NEW)

```python
class Tp20Error(TransportError); class Tp20ChannelRefused(Tp20Error); class Tp20Timeout(TransportTimeout)

@dataclass
class Tp20Params:  # see PROTOCOL_FACTS §TP2.0 for encodings and defaults
    block_size: int = 0x0F
    t1_ack_timeout: float          # seconds (encoded as 0x8A by default)
    t3_min_interframe: float       # seconds (encoded as 0x32 by default)
    ... (raw bytes kept too, so what we send is exactly what the facts say)

class Tp20Channel(IsoTpLink):
    """KWP payload link over TP 2.0. Same send()/recv()/flush_rx()/close() contract as IsoTpLink."""
    def __init__(self, router: CanRouter, logical_address: int, *, tester_tx_id: int = 0x300,
                 params: Tp20Params | None = None, keepalive: bool = True) -> None
    def connect(self) -> None        # 0x200 setup (0xC0) -> 0xD0 response -> 0xA0/0xA1 params; raises Tp20ChannelRefused
    def send(self, payload: bytes) -> None       # segments, waits for 0xB0 ACKs per block, honours T3
    def recv(self, timeout: float) -> bytes | None  # reassembles, sends ACKs, handles 0x90 not-ready / 0xA3 tests
    def channel_test(self) -> None   # 0xA3
    def disconnect(self) -> None     # 0xA8
    def close(self) -> None          # stops keepalive thread, disconnects (best effort)
    ecu_tx_id / ecu_rx_id properties (assigned by the ECU during setup)

class Tp20Responder:
    """ECU side for the simulated vehicle: listens on 0x200 for its logical address,
    assigns IDs, negotiates params, reassembles requests, hands payloads to a handler,
    segments responses, keeps the channel until 0xA8 or inactivity timeout."""
    def __init__(self, router_or_endpoint_factory, logical_address: int, handler: Callable[[bytes], bytes | None],
                 *, ecu_tx_id: int, ecu_rx_id: int) -> None
    start()/stop()

def probe_tp20_addresses(router: CanRouter, addresses: Iterable[int], *, timeout: float = 0.05) -> list[int]
    # sends a setup request per address, returns the ones that answered 0xD0 (then disconnects each)
```

Keepalive: a thread sends 0xA3 every `keepalive_interval` (default 1.0 s) while idle;
it shares the channel's send lock with foreground traffic.

### 2.3 `transport/fakebus.py` — frame-level simulated vehicle (NEW, foundation)

```python
class FakeCanBus:                      # the fabric
    def attach(self, name: str = "") -> "FakeCanTransport"
    def publish(self, sender: "FakeCanTransport", frame: CanFrame) -> None   # to every other endpoint
    latency: float = 0.0               # optional per-frame delay for timing tests

class FakeCanTransport(RawCanTransport): open/close/send/recv/flush_rx; plus .inbox for tests

class SimulatedNode(ABC):
    name: str
    def start(self) -> None / stop(self) -> None   # runs its own daemon thread

class UdsNode(SimulatedNode):
    """A SimulatedEcu (or any object with .handle(bytes)->bytes|None) behind software ISO-TP."""
    def __init__(self, bus: FakeCanBus, ecu, *, request_id: int, response_id: int,
                 functional_id: int | None = 0x7DF, name: str = "")

class SimulatedVehicle:
    def __init__(self, preset: str = "demo") -> None
    bus: FakeCanBus; nodes: list[SimulatedNode]
    def add_node(self, node: SimulatedNode) -> None
    def start(self) -> None / stop(self) -> None
    def node(self, name: str) -> SimulatedNode
    PRESETS: dict[str, Callable[["SimulatedVehicle"], None]]   # "demo", "golf-tdi-2012", "r32-2008"
    @classmethod
    def register_preset_hook(cls, preset: str, hook: Callable[["SimulatedVehicle"], None]) -> None
        # other slices (tp20/kwp sim, obd sim) add their nodes to a preset without editing fakebus.py

def get_default_vehicle(preset: str | None = None) -> SimulatedVehicle   # process-global, lazily started
def reset_default_vehicle() -> None                                        # for tests
```

* `transport/fake.py` (`SimulatedEcu`, `FakeIsoTpLink`, `make_fake_pair`) stays as is for
  the existing unit tests; `SimulatedEcu` is reused as the UDS brain inside `UdsNode`.
* Presets: `demo` = the 0.1.0 SIMOS18.1 engine at 0x7E0/0x7E8 plus a gateway (0x710/0x77A)
  and ABS (0x713/0x77D) built from `SimulatedEcu` with different identifiers;
  `golf-tdi-2012` and `r32-2008` are populated by preset hooks from the UDS, KWP/TP2.0
  and OBD slices to mirror the module maps in `PROTOCOL_FACTS.md`.

### 2.4 `transport/context.py` — one object that opens hardware and hands out links (NEW, foundation)

```python
class TransportContext:
    KINDS = ("fake", "can", "j2534", "j2534-fw")
    def __init__(self, kind: str, *, dll_path: str | None = None, can_interface: str = "socketcan",
                 can_channel: str = "can0", bitrate: int = 500_000, vehicle_preset: str | None = None) -> None
    def isotp_link(self, tx_id: int, rx_id: int, *, extra_rx_ids: Iterable[int] = ()) -> IsoTpLink
    def tp20_channel(self, logical_address: int, **kw) -> "Tp20Channel"   # raises TransportError on j2534-fw
    def raw_endpoint(self, accept=None) -> RawCanTransport                 # sniffing / probing
    @property router -> CanRouter | None
    def close(self) -> None;  __enter__/__exit__
```

| kind | what it opens | ISO-TP | TP 2.0 |
|------|---------------|--------|--------|
| `fake` | `get_default_vehicle(preset)` + `FakeCanTransport` + `CanRouter` | software | yes |
| `can` | `PythonCanTransport` + `CanRouter` | software | yes |
| `j2534` | `J2534RawCanTransport` (CAN protocol) + `CanRouter` | software | yes — the universal mode |
| `j2534-fw` | `J2534IsoTpLink` per link (device ISO15765 channel) | firmware (fast; flashing) | no (clear error) |

`transport.make_isotp_link(kind, ...)` remains as a thin wrapper (`fake` now routes through
the simulated vehicle, so the CLI exercises real ISO-TP framing offline).

### 2.5 `transport/j2534.py` (EXTEND)

* `_J2534Device` split so one opened device can carry a CAN channel and an ISO15765
  channel; keep public classes working.
* `J2534RawCanTransport.recv` must honour `RxStatus` flags (drop TX_INDICATION / loopback,
  START_OF_MESSAGE indications) per PROTOCOL_FACTS, not only the length heuristic.
* `J2534IsoTpLink` gains `functional_rx_ids` support: install a FLOW_CONTROL filter per
  responder so OBD functional requests to 0x7DF collect 0x7E8..0x7EF.

## 3. Protocol clients

### 3.1 `uds/` (EXTEND)

`UdsClient` additions (all tested against `SimulatedEcu`, which grows accordingly):

* `read_data_by_identifiers(dids: Sequence[int]) -> dict[int, bytes]` (multi-DID 0x22;
  needs a size oracle for splitting; falls back to single reads when sizes unknown).
* `read_dtc_count(status_mask)`, `read_dtc_snapshot(dtc, record=0xFF)`,
  `read_dtc_extended_data(dtc, record=0xFF)`, `read_supported_dtcs()`; parsers in `uds/dtc.py`
  return dataclasses (`DtcSnapshot`, `DtcExtendedData`) and never guess DID sizes silently:
  snapshot DID payloads are returned raw with the DID list when sizes are unknown.
* `write_data_by_identifier` already exists; add `io_control` convenience
  (return-control / short-term-adjustment) and `routine_start/stop/results`.
* `dynamically_define_did(...)` + `clear_dynamic_did` (0x2C) for fast logging where supported.
* `communication_control(...)` (0x28).
* `scan_dids(range, *, batch) -> dict[int, bytes]` honouring NRC 0x31/0x13/0x7F/0x33 semantics.
* `download(address, size, data, progress)` = RequestDownload → TransferData writes →
  TransferExit (the write-side mirror of `upload`), used only by `flash/`.

### 3.2 `kwp/` (NEW): KWP2000 (ISO 14230-3) client over any `IsoTpLink`-shaped payload link

```python
kwp/services.py    SIDs, VAG session ids, ident options, NRC names (from PROTOCOL_FACTS)
kwp/exceptions.py  KwpError, KwpNegativeResponse(sid, nrc), KwpTimeout
kwp/client.py      class KwpClient(link, timing):
                     request(payload) -> bytes  (handles 0x78 pending, busy 0x21/0x23 retries)
                     start_diagnostic_session(kind=0x89), stop_diagnostic_session(), tester_present()
                     read_ecu_identification(option) -> bytes
                     read_data_by_local_id(lid) -> bytes          # measuring block raw
                     read_dtc_by_status(group=0xFF00) -> list[(dtc:int, status:int)]
                     clear_diagnostic_information(group=0xFF00)
                     read_memory_by_address(addr, length, addr_bytes=3)
                     security_access(level, seed_key_fn), write_data_by_local_id(lid, data)
                     start_routine_by_local_id(lid, data), stop_routine..., request_routine_results...
                     io_control_by_local_id(lid, data)
                     start_tester_present(interval) / stop_tester_present()
```

### 3.3 `obd/` (NEW): generic OBD-II

```python
obd/pids.py    PID table (mode 01/02): name, bytes, decoder(bytes)->value|dict, unit, min/max; supported-PID bitmap helpers
obd/client.py  class ObdClient(link_functional_or_physical):
                 supported_pids(mode=0x01) -> set[int]; read_pid(pid) -> ObdValue; read_pids(...)
                 monitor_status() -> MonitorStatus (MIL, count, spark/compression, per-monitor ready)
                 read_dtcs(mode=0x03|0x07|0x0A) -> list[str]; clear_dtcs()
                 freeze_frame(frame=0) -> dict; vehicle_info(infotype) (VIN, CALID, CVN, ECU name, IPT)
                 monitor_test_results() -> list[Mode06Result]   (OBDMID/TID/UASID decode)
obd/sim.py     SimulatedObdEcu.handle(request)->response, plus a preset hook adding it at 0x7E8 (and the
               TDI/VR6 differences: compression vs spark monitors, DPF PIDs)
```

Functional addressing: an `IsoTpLink` with tx 0x7DF and `extra_rx_ids` 0x7E8..0x7EF;
`ObdClient.request_all(payload)` collects every responder within P2 and returns
`{response_id: payload}`; single-ECU helpers use the first/engine response.

## 4. VAG application layer (`vag/`)

* `vag/addresses.py` (NEW): the full address-word table (`VagModule(address, name, short,
  uds_request_id, uds_response_id)`), `resolve_module(token)` accepting `"01"`, `"0x19"`, `"19"`,
  `"engine"`, `"gateway"`; `uds_ids_for(address)`; `ALL_ADDRESS_WORDS`. `vag/modules.py` keeps
  its public names (`MODULES`, `ModuleAddress`, `IDENT_DIDS`) but builds from addresses.py.
* `vag/vehicles.py` (NEW): presets `golf-tdi-2012`, `r32-2008` (and `demo`): expected modules,
  protocol per module (`"uds" | "kwp-tp20" | "either"`), typical part-number prefixes, notes,
  `verified: bool` per row. Used by autoscan ordering and by the CLI `--vehicle` help.
* `vag/measuring_blocks.py` (NEW): KWP group decoding (formula table, enumerations, text) →
  `MeasuringValue(formula_id, a, b, value, unit, text)`; also `obd_mirror_did_decoder(did)` for
  UDS 0xF4xx values via `obd/pids.py`.
* `vag/dtc.py` (EXTEND): SAE J2012-DA failure-type-byte table; `VagDtc` dataclass (sae_code,
  ftb, status, legacy_number, description, ftb_text, status_text); `legacy_number(code)`;
  description DB loaded from `vagtune/data/dtc_db.json` (lazy, cached); KWP 2-byte + status decode.
* `vag/kwp_session.py` (NEW): `VagKwpSession(client)`: `read_identification()` (0x1A options →
  `KwpIdentity` with part number, component, coding, WSC), `read_dtcs()`, `clear_dtcs()`,
  `read_group(n) -> list[MeasuringValue]`, `login(code)`, `read_coding()/write_coding(...)`,
  `read_adaptation(channel)/write_adaptation(...)`, `basic_settings(group)`, `output_test(...)`,
  `read_ram(addr, n)` — every call whose service mapping is *unverified* in PROTOCOL_FACTS must
  (a) carry a docstring saying so, (b) emit `log.warning("UNVERIFIED mapping ...")` once, and
  (c) be listed in `docs/PROTOCOL_FACTS.md` under Reported.
* `vag/ecu.py` (EXTEND `VagEcuSession`): `read_coding()/write_coding(new, *, backup_path)`,
  `read_adaptation_did/write_...`, `scan_dids()`, `io_control(...)`, `routine(...)`,
  `read_dtcs_detailed()` (with snapshot/extended), `login(code)` (security level 0x03/0x04 per
  facts), `read_measuring_did(did)`; `EcuIdentity` extended with every ident DID.
* `vag/autoscan.py` (NEW): `autoscan(ctx, *, vehicle_preset=None, uds_ids=range(0x700,0x7FF),
  tp20_addresses=range(1,0x80), progress=...) -> ScanReport`; per module found: protocol,
  ids, identification, DTC list, coding (read-only). `ScanReport.to_text()` (VCDS-style) and
  `.to_json()`.
* `vag/me7.py` (NEW): ME7Logger `.ecu` definition parser (`Me7Definition`, `Me7Variable`) and
  `Me7RamLogger(kwp_client, definition)` using 0x23 (or the verified method) to sample
  variables → rows for `datalog`.
* `vag/profiles.py` (EXTEND): add `EDC17CP14` (UDS; blocks/SA2 marked unknown unless verified),
  `ME7_1_1` (KWP/TP 2.0), `DQ250_02E` (KWP), `HALDEX_GEN2` (KWP) with `protocol` field and
  `verified_flash_metadata: bool`. `guess_profile` uses F197/F187 and KWP part numbers.
* `vag/coding.py` (NEW): the safety wrapper used by both UDS and KWP coding/adaptation writes:
  mandatory `backup_path` written *before* the write (JSON: module, ids, identity, old value,
  timestamp), refuse if identity differs from the backup, `dry_run` default **True**, explicit
  `confirm=True` required, read-back verification after write.

## 5. `flash/` (NEW, Phase-2 roadmap item 5, UDS only in 0.2.0)

`flash/uds_flash.py`: `write_block(session, block, image, *, backup: bytes, dry_run=True,
progress)` = identity check vs backup → programming session → SA2 unlock → erase routine →
`download` → checksum routine → reset → re-identify. Implemented and tested against an
extended `SimulatedEcu` (which gains RequestDownload/TransferData-write/erase/checksum/reset
handling). Real ECUs are gated by `profile.verified_flash_metadata`; without it the call raises
`NotImplementedError` naming what is missing (SA2 script, block map, checksum algorithm).

## 6. `datalog/` (NEW)

`datalog/channels.py`: `Channel` protocol (`name`, `unit`, `sample() -> float | str | None`) with
implementations `UdsDidChannel`, `ObdPidChannel`, `KwpGroupChannel` (one group → N channels),
`Me7RamChannel`; `datalog/logger.py`: `DataLogger(channels, *, interval, duration, csv_path,
on_row)` with monotonic timestamps, ISO-8601 wall clock column, graceful stop, per-channel
error column rather than aborting the run.

## 7. CLI (`cli.py` + `commands/`)

`cli.py` keeps `build_parser()`/`main()`. Subcommands register from `commands/<area>.py`
via `register(sub, add_common_args)`; `commands/_common.py` provides `add_common_args(parser)`
(`--transport {fake,can,j2534,j2534-fw}`, `--dll`, `--can-interface`, `--can-channel`,
`--vehicle PRESET`, `--module TOKEN`) and `open_context(args) -> TransportContext`.

| area module | subcommands |
|-------------|-------------|
| `commands/diag.py` | `scan`, `identify`, `dtc` (0.1.0 behaviour, now via context, `--module` accepts address words) |
| `commands/calibration.py` | `read-cal`, `show-map`, `scale-map`, `sa2` |
| `commands/autoscan.py` | `autoscan [--json out] [--tp20-only/--uds-only]` |
| `commands/obd.py` | `obd status`, `obd pids`, `obd read PID...`, `obd dtc [--pending/--permanent]`, `obd clear`, `obd vin`, `obd readiness`, `obd monitors`, `obd freeze` |
| `commands/kwp.py` | `kwp ident`, `kwp dtc [--clear]`, `kwp group N [N...] [--watch]`, `kwp login CODE`, `kwp coding [--write HEX --yes]`, `kwp adapt CH [--write VAL --yes]`, `kwp basic GROUP`, `kwp raw HEX`, `kwp ram ADDR LEN` |
| `commands/uds.py` | `uds did READ 0xF190...`, `uds did-scan [--from --to]`, `uds dtc [--detail]`, `uds routine ID [--data]`, `uds io DID OPTION [--data]`, `uds raw HEX`, `uds login CODE` |
| `commands/coding.py` | `coding read`, `coding backup`, `coding write --hex ... --backup FILE --yes`, `coding restore FILE --yes` (UDS or KWP chosen by module protocol) |
| `commands/datalog.py` | `log --channel SPEC... --interval --duration --out file.csv` |
| `commands/me7.py` | `me7 info DEF.ecu`, `me7 log DEF.ecu VAR... --out` |
| `commands/flash.py` | `flash backup`, `flash write --bin --backup --dry-run/--yes` |
| `commands/sniff.py` | `sniff [--id ...] [--duration]` (router monitor endpoint) |

Every command works against `--transport fake --vehicle <preset>` and is exercised by a CLI
test (`tests/test_cli_fake.py`) that runs it through `main()`.

## 8. Rules for every slice

1. Facts come from `docs/PROTOCOL_FACTS.md`. Anything in its *Reported* lists must be marked
   in code (`# UNVERIFIED:` comment + docstring) and warn once at runtime; nothing Reported may
   drive a *write* without `confirm=True`.
2. No stubs. If something can't be finished, raise `NotImplementedError("<what is missing>")`.
3. Every protocol feature has a simulator-backed test. Hardware modules still import on Linux.
4. File ownership is strict (see the implementation plan); shared registration goes through the
   hooks above (`SimulatedVehicle.register_preset_hook`, `commands/<area>.register`).
5. Safety invariants (unchanged + extended): backup before any write; identity must match the
   backup; checksums recomputed before any flash; dry-run is the default for coding/adaptation/
   flash; the CLI requires `--yes` for anything that writes to a module.
6. Logging via `logging.getLogger(__name__)`; `print()` only in `commands/`.
