# vagtune protocol facts registry (source-verified; "Verified" vs "Reported / unverified")

Status: **implementers' ground truth for vagtune 0.2.0** (becomes `vagtune/docs/PROTOCOL_FACTS.md`).
Consolidated 2026-10-05 from the eight verified research sheets `tp20.md`, `addresses.md`, `obd2.md`,
`uds_vag.md`, `j2534_can.md`, `dtc_db.md`, `kwp_vag.md`, `ecus.md` (plus the data file `dtc_db.json`).
Every fact below is copied **verbatim** from those sheets (each of which was independently re-verified
against re-fetched sources on 2026-10-05); the only new text in this file is the layer skeleton, the
cross-reference notes, the conflict register (§0) and the appendix. Nothing was added, re-derived or
"improved"; where two sheets disagree both statements are kept and the disagreement is listed in §0.

Cars: **2008 VW R32 Mk5** (1K, US; 3.2 VR6 BUB, Bosch ME7.1.1, DQ250 02E DSG, Haldex Gen2 4Motion) and
**2012 VW Golf TDI Mk6** (5K, US; 2.0 CR TDI CJAA, Bosch EDC17CP14, DQ250 02E or 6MT). Both: 500 kbit/s,
11-bit CAN on OBD pins 6/14 behind a J533 gateway.

Scope: reading and understanding what the control modules report (identification, measuring values,
fault codes with freeze frames) and the owner-level workshop functions (coding, adaptation, basic
settings, output tests, Login/function 11). Reflashing, security algorithms and immobiliser topics are
**out of scope** and are not documented here (the few bytes that appear — e.g. SA2 scripts quoted from an
open-source flasher, or the `10 84 14` session — are listed only so that sniffed traffic can be recognised;
they must not be implemented).

### How to read this file

* Each layer section has exactly two sub-lists: **Verified (source)** — a source was fetched and re-read
  and supports the exact claim; every bullet ends with `(src: URL)` or a short key defined in that layer's
  source-key table — and **Reported / unverified (confidence)** — from memory, from an unfetchable or
  secondary source, or inferred; each item states a confidence (high / medium / low) and what would confirm it.
* Rule 8.1 of `DESIGN_0.2.md` applies: anything taken from a *Reported* list must be marked `# UNVERIFIED:`
  in code, warn once at runtime, and may not drive a write without `confirm=True`.
* Byte values are hex unless stated. `TX` = tester → ECU, `RX` = ECU → tester. `A,B,C,…` = data bytes.
* The sheets cross-reference each other by file name; the mapping to this file is:
  `j2534_can.md` → §1, `tp20.md` → §2, ISO-TP material → §3, `kwp_vag.md` → §4 and §7.5/7.7/7.8/7.10,
  `uds_vag.md` → §5 and §7.6/7.8/7.10, `obd2.md` → §3 and §6, `addresses.md` → §7.1–7.4 and §8,
  `dtc_db.md` → §7.8/7.9, `ecus.md` → §8 and §9. All OPEN QUESTIONS are collected in §10.
* Verification-pass annotations in the sheets (`[corrected]`, `[added]`, `[downgraded]`, `[promoted]`,
  `[CORRECTED]`, `[NEW]`) are preserved as they stand.

### Table of contents

0. Cross-sheet conflict register (summary; resolutions in `IMPLEMENTATION_NOTES.md`)
1. CAN / J2534 pass-thru / hardware (python-can, OpenPort 2.0, ELM/STN limits, OBD connector)
2. VW TP 2.0 transport (channel setup, parameters, timing codec, data frames, ACK/sequence rules)
3. ISO-TP (ISO 15765-2) and ISO 15765-4 legislated-OBD transport rules
4. KWP2000 services (ISO 14230-3): message model, sessions, memory services, NRC table
5. UDS services (ISO 14229-1): SIDs, NRC table, 0x19 layouts, 0x14/0x85/0x28/0x2F/0x31, sessions, 0x11/0x3E
6. OBD-II (SAE J1979 / ISO 15031-5): modes 01–0A, complete PID table, PID 01 decode, mode 06 UASIDs, mode 09
7. VAG application layer: address words, ODIS UDS id table, TP 2.0 logical addresses, gateway installation
   list, identification layouts (KWP `1A xx`, UDS DIDs, workshop code), measuring-block formula table,
   DTC formats and numbering, DTC description DB and fault-type tables, login/coding/adaptation/basic
   settings/output tests
8. Per-car module maps (real VCDS Auto-Scans of both cars and sibling cars)
9. ECU-specific diagnostic knowledge (ME7.1.1 groups, EDC17CP14/CJAA groups and service functions, DQ250,
   Haldex Gen2, gateway/cluster, ME7Logger `.ecu` format)
10. Open questions (consolidated, with the exact request bytes)
11. Appendix: fact counts per layer


---

## 0. Cross-sheet conflict register

The eight sheets were written by independent agents. Where they disagree, **both statements are kept in
place below** (nothing was silently harmonised). This register lists every disagreement found while
consolidating, the sections where each side appears, and the working resolution adopted by
`IMPLEMENTATION_NOTES.md` §(c). "Unresolved" means only the real car can decide.

| # | topic | side A (section) | side B (section) | working resolution |
|---|---|---|---|---|
| C1 | TP 2.0 block size 0x0F = 15 or 16 frames | JAZDW prose "send 16 packets at a time" (§2 Reported) | ICH / K2C / EliasTuning "15 packets", BS range 1..15 (§2, §7.3) | Request ACK on frame index BS−1 (every 15th); never send >15 unacknowledged frames — safe under either reading. Unresolved on the wire (§10, tp20 Q4 / addresses Q11). |
| C2 | HVAC (08) UDS ids | task brief 0x744/0x7AE | ODIS table `LL_AirCondiUDS 0x746/0x7B0` (§7.2) | Resolved: 0x746/0x7B0; 0x744 does not exist in the ODIS table. Likewise 46 ≠ 0x746 (it is 0x70D/0x777). |
| C3 | EDC17CP14 (CJAA) protocol | `uds_vag.md`, `j2534_can.md` header, `obd2.md` header, `DESIGN_0.2.md` and `CLAUDE.md` assume UDS/ISO-TP | `addresses.md` §D + `ecus.md` §F1: CJAA 03L 906 019/022 family speaks **KWP2000 over TP 2.0 at logical 0x01** (seishuku's 2013 Jetta code + README; no ASAM/ROD line in scans B/C; Ross-Tech "CAN protocol EDC" procedures); only the Passat CKRA 03L 906 012 EDC17 is UDS (scan D) | Resolved in favour of KWP/TP 2.0 (verified three ways). Still probe `0x7E0: 03 22 F1 87` once (§10). The DESIGN table row "engine, ABS, gateway, cluster, BCM, airbag are UDS" is wrong for engine, ABS (MK60EC1), BCM and the 7N0 gateway on the 2012 Golf — only cluster/immo, airbag, HVAC, steering-column module (5K0 953 549 E) and telephone (5K0 035 730) printed ASAM/ROD. |
| C4 | TP 2.0 channel-setup request form | every library + the real VAG tester: `dest C0 00 10 00 03 01` (RX id "invalid") (§2) | a 2009 Scirocco MED17.5 ignored that form and required `dest C0 00 03 00 03 01` (§7.3) | Unresolved: send `00 10 00 03` first, retry with `00 03 00 03` on silence (addresses Q13). |
| C5 | Direction of `A0` parameters request | JAZDW *table* text and K2C comment: module → tester | all traces, JAZDW's own example, both ECU emulators: **tester sends A0, module answers A1** (§2 §3) | Resolved: tester sends A0. |
| C6 | Reply to an incoming `A3` channel test | JAZDW-SRC / SPECK answer with `A3` | VWTPLIB, VDS, NOTYAL, spec text: answer with the 6-byte `A1` parameters (§2 §3) | Resolved: answer `A1 0F 8A FF 4A FF`-style parameters. |
| C7 | Default T3 in the tester's `A0` | `tp20.md` §8 reference code uses `A0 0F 8A FF 4A FF` (10 ms); PQF/PyVCDS/dongle use `0A` (1 ms) | `addresses.md` §D: MED17.5 accepted T3=0x0A then degraded; stable at `32` (5 ms); OpenHaldex "confirmed VW captures: 0F 8A FF 32 FF" | Resolved: default `A0 0F 8A FF 32 FF`; never 0x0A. Always pace own frames by the peer's T3. |
| C8 | Tester-TX CAN id after setup | several libraries hard-code 0x740 | engine 0x740, EPS 0x7A8, Haldex Gen2 0x764, DSG 0x760 (SP), gateway predicted 0x32E (§2, §7.3, §9) | Resolved: always parse bytes 4–5 of the `D0` reply. |
| C9 | Keep-alive interval | JAZDW-SRC 500 ms, SPECK 600 ms, PyVCDS 500 ms; "module idle timeout not measured" (§2 Reported) | scirocco-dash: "ECU drops the channel after roughly a second of silence"; EliasTuning `T_CT_AKTIV_MS = 1000` (§7.3) | Resolved: `A3` at least every 500 ms when idle; measure the true timeout (§10). |
| C10 | Haldex Gen2 TP 2.0 address | address word 22 assumed = logical 0x22 (brief; NefMoto FWD-Jetta "answer at 0x22") | OpenHaldex-C6: answers at **0x0A**, 0x22 silent on a 4Motion 1K0 (§7.3) | Resolved: 0x0A (high); the thing answering 0x22 on the FWD Jetta is not a Haldex. |
| C11 | Gateway TP 2.0 address | address word 19 | NefMoto sniff + reproduction and the Skoda paper: **0x1F** (§2, §7.3) | Resolved: 0x1F. General rule: logical address ≠ address word except 01/02/03. |
| C12 | KWP 2-byte DTC → text rule | scirocco-dash `dtc_str` uses the SAE hex-nibble rule (0x4065 → "P0065") | KLineKWP1281Lib, VCDS, Bentley, Ross-Tech titles: decimal rule (0x4065 = 16485 = P0101), verified three ways (§7.8) | Resolved: decimal rule (`N5 = raw16`; P/C/B/U only for 0x4000–0x7FFF). |
| C13 | KWP `58` reply record size | PyVCDS steps 2 bytes | DV emulator, scirocco-dash, bri3d, NefMoto M-box trace: **3 bytes** `DTC_hi DTC_lo status` (§7.8) | Resolved: 3 bytes. |
| C14 | UDS failure-type byte (FTB) 0x15–0x1D, 0x71–0x73 | `uds_vag.md` Reported (autodtcs.com): `15 Circuit open`, `1C current below threshold`, `1D current above threshold`, `71 actuator stuck low`, `72 actuator stuck high` | `dtc_db.md` §G (vinfast + neomotive agree): `15 Short to Battery or Open`, `18 current below`, `19 current above`, `1C voltage out of range`, `1D current out of range`, `71 Actuator Stuck`, `72 Stuck Open`, `73 Stuck Closed` | Unresolved between secondary sources; `dtc_db.md` §G (two independent tables agreeing, ISO-Annex-D-shaped) is taken as primary, autodtcs rows flagged. Confirm on the TDI (§10, dtc_db Q3). |
| C15 | KWP measuring-value formulas 0x04 sign, 0x08, 0x12, 0x14, 0x19, 0x27, 0x2D, 0x2E, 0x51, 0x5E, 0x0E, 0x21 | vag-blocks / PyVCDS / OpenHaldex variants (§7.7 table columns) | KLineKWP1281Lib + blafusel + bri3d consensus column (§7.7) | Resolved: implement the consensus column (KL); keep the alternates as named variants; OpenHaldex's 0x0E/0x21/0x5E forms are retained for Haldex fields pending the on-car test (kwp Q10). |
| C16 | Misfire-counter group numbers on ME7 | Ross-Tech misfire page: 014 = cyl 1-3, 015 = cyl 4-6 | Ross-Tech standardized table: 014 summary, 015 = cyl 1-3, 016 = cyl 4-6 (§9 D1/D2) | Unresolved (ecus Q4); label-file driven. |
| C17 | UDS SecurityAccess level for calibration | `CLAUDE.md` "requestSeed 0x11 / sendKey 0x12" | not present in any fetched VW_Flash file; fake testdata uses 03/04 (§5/§7.10 Reported) | Demoted to Reported (medium). Out of scope for 0.2.0 diagnostics anyway. |
| C18 | ISO-TP padding byte | ELM/OBDLink default 0x00; ISO 15765-2 suggests 0xCC; VW_Flash tester 0x55; VAG ECU replies 0xAA (aep log, OpenHaldex) | — | Resolved: configurable tester pad (default 0x55 or 0x00), DLC always 8, accept any pad on receive; record what each ECU sends (§10). |
| C19 | Tactrix `PassThruWriteMsgs(Timeout=0)` | RF-RE disassembly: "returns ERR_TIMEOUT immediately, frame never sent" | OP-AB byte tap of the real DLL: sends unnumbered `att… 1000000`, returns 0, next command stalls ~1 s (§1) | Resolved: always pass a non-zero write timeout. |
| C20 | Tactrix DLL channel routing with CAN(5) + ISO15765(6) open | project design assumes both channels usable at once | OP-AB (under Wine/box64): every channel-5 frame is delivered to the ISO15765 channel, none to the CAN channel (§1) | Unresolved on native Windows (j2534 OQ1); `j2534` kind = CAN channel only is the safe default. |
| C21 | J2534 `unsigned long` width | Windows DLL: 4 bytes; bisak Linux/macOS driver: 8 bytes (`c_ulong`) | roffe driver: 32-bit ABI (`c_uint32`) (§1) | Resolved: per-driver ABI switch. |
| C22 | OBD PID 0x68 byte count | Wikipedia: 3 bytes | DashLogic: 7 bytes (§6) | Unresolved: never combine 0x68 in multi-PID requests until the ECU's own length is seen. |
| C23 | OBD PID 1C values 14–16 | ISO 15031-5:2006 (EURO IV/V/EEV) | Wikipedia / J1979-DA (moved to PID 5F; 14 = OBD+EOBD+KOBD …) (§6) | Resolved: newer (W) assignment. |
| C24 | ISO 15031-5 UASID 0x2E | Annex E: boolean | Table 170: "Percent 0,00 %" (§6) | Unresolved inconsistency in the standard; decode as boolean, log raw. |
| C25 | KWP `63` ReadMemoryByAddress reply | bri3d skips one byte after `63` | ISO 14230-3 and me7-logger: data starts immediately after `63` (§4) | Resolved: no skipped byte. |
| C26 | KWP DTC status byte bit 7 = MIL | bri3d `isCEL`; VCDS "MIL ON" only seen on a UDS record | 21 real KWP records never had bit 7 set (§7.8) | Unresolved (low–medium); display only. |
| C27 | Project `CLAUDE.md` "verified" UDS ids for ABS 0x713/0x77D and Haldex 0x70F/0x779 | ODIS slots (valid for UDS ABS / Gen5 Haldex on MQB) | on these cars ABS MK60/MK60EC1 and Haldex Gen2 are KWP/TP 2.0 modules (§8, §9 H) | Resolved: the ids are correct ODIS slots but will not answer on the two target cars; autoscan must not treat silence there as "absent". |
| C28 | `5A 9B` part-number field | `addresses.md` §D: "first 10 characters … then 2 spaces, then 4-digit version" | `kwp_vag.md` §2: offsets 0..10 = 11-char part number (10 chars + pad space), 11 = constant 0x20, 12..15 = version | Not a conflict — same bytes, two descriptions; use the kwp_vag offset table. |


---

## 1. CAN / J2534 pass-thru / hardware

Source sheet: `j2534_can.md` (re-verified 2026-10-05 against fresh fetches; `[corrected]`/`[promoted]` marks are the verifier's).
Covers the SAE J2534-1 v04.04 API surface, `PASSTHRU_MSG` / RxStatus / TxFlags tables, CAN-channel filter and timeout
semantics, the Tactrix OpenPort 2.0 behaviour measured on the wire, ISO15765-channel flow-control filters and config
parameters, the complete error-code table, python-can hardware, why ELM327/STN cannot run TP 2.0, and the OBD connector.
Notation: `(src: KEY)` cites the source-key table below.

### Source key for this layer (verbatim from the sheet)

Source key (every URL below was fetched and read in this session unless marked *unreachable*):

| key | URL | what it is |
|---|---|---|
| SAE | https://netcult.ch/elmue/HUD%20ECU%20Hacker/J2534%20PassThrough.pdf | SAE J2534-1 "Revised DEC2004" (= v04.04), full text (pdftotext → `sae.txt`, line numbers below refer to that file) |
| DLH | https://www.dashlogic.com/download/j2534%20pass%20thru%20device%20interface%20source%20code/J2534_v0404.h | DashLogic `J2534_v0404.h` (J2534-1 + J2534-2 defines, prototypes) |
| FSH | https://raw.githubusercontent.com/Comer352L/FreeSSM/master/src/J2534.h | FreeSSM `J2534.h` (defines + structs) |
| CXH | https://raw.githubusercontent.com/charlie-x/J2534-Sim/master/J2534.h | J2534-Sim header |
| OP-README | https://raw.githubusercontent.com/bisak/openport-j2534/main/README.md | open-source OpenPort 2.0 J2534 driver (macOS/Linux) |
| OP-API | https://raw.githubusercontent.com/bisak/openport-j2534/main/docs/API.md | same project, per-call behaviour on the cable |
| OP-PROTO | https://raw.githubusercontent.com/bisak/openport-j2534/main/docs/PROTOCOL.md | same project, the cable's USB wire protocol, measured (firmware 1.17.4877) |
| OP-AB | https://raw.githubusercontent.com/bisak/openport-j2534/main/docs/AB-OFFICIAL.md | same project, byte-for-byte A/B against Tactrix's Windows `op20pt32.dll` 1.02.0.4868 (run under Wine/box64, see §2.2 caveat) |
| RF-README | https://raw.githubusercontent.com/roffe/libj2534_openport2/master/README.md | second open-source OpenPort 2.0 Linux driver |
| RF-RE | https://raw.githubusercontent.com/roffe/libj2534_openport2/master/RE_NOTES.md | disassembly notes on `op20pt32.dll` |
| TAC | https://www.tactrix.com/index.php?page=shop.product_details&flypage=flypage.tpl&product_id=17&category_id=6&option=com_virtuemart&Itemid=53&redirected=1&Itemid=53 | Tactrix OpenPort 2.0 product page |
| TACDL | https://www.tactrix.com/index.php?Itemid=61 | Tactrix "Download Drivers + J2534 DLL" page |
| PC-BUS | https://python-can.readthedocs.io/en/stable/bus.html | python-can Bus API |
| PC-MSG | https://python-can.readthedocs.io/en/stable/message.html | python-can Message |
| PC-SC | https://python-can.readthedocs.io/en/stable/interfaces/socketcan.html | python-can SocketCAN |
| PC-SL | https://python-can.readthedocs.io/en/stable/interfaces/slcan.html | python-can slcan |
| SLPY | https://raw.githubusercontent.com/hardbyte/python-can/main/can/interfaces/slcan.py | python-can slcan source |
| PC-GS | https://python-can.readthedocs.io/en/stable/interfaces/gs_usb.html | python-can gs_usb |
| PC-PCAN | https://python-can.readthedocs.io/en/stable/interfaces/pcan.html | python-can PCAN |
| PC-KV | https://python-can.readthedocs.io/en/stable/interfaces/kvaser.html | python-can Kvaser |
| PC-VEC | https://python-can.readthedocs.io/en/stable/interfaces/vector.html | python-can Vector |
| CL-FW | https://raw.githubusercontent.com/candle-usb/candleLight_fw/master/README.md | candleLight gs_usb firmware |
| KERN | https://www.kernel.org/doc/html/latest/networking/can.html | Linux SocketCAN docs |
| CANRAW | https://raw.githubusercontent.com/torvalds/linux/master/include/uapi/linux/can/raw.h | Linux `can/raw.h` (socket option defaults) |
| KVKC | https://raw.githubusercontent.com/torvalds/linux/master/drivers/net/can/usb/Kconfig | Linux CAN-USB Kconfig (kvaser_usb device list) |
| KISOTP | https://docs.kernel.org/networking/iso15765-2.html | Linux ISO-TP socket docs |
| ISOTP-PY | https://can-isotp.readthedocs.io/en/latest/isotp/implementation.html | python can-isotp parameter table |
| KVL | https://www.kvaser.com/product/kvaser-leaf-light-hs-v2/ | Kvaser Leaf Light v2 page |
| W-OBD | https://en.wikipedia.org/w/index.php?title=On-board_diagnostics&action=raw | OBD-II / J1962 connector pinout (wikitext) |
| W-PID | https://en.wikipedia.org/w/index.php?title=OBD-II_PIDs&action=raw | CAN IDs for OBD-II (wikitext) |
| W-TP | https://en.wikipedia.org/w/index.php?title=ISO_15765-2&action=raw | ISO 15765-2 (wikitext) |
| W-ELM | https://en.wikipedia.org/w/index.php?title=ELM327&action=raw | ELM327 (wikitext) |
| W-USB | https://en.wikipedia.org/w/index.php?title=USB_communications&action=raw | USB frame timing (wikitext) |
| PINVW | https://pinoutguide.com/CarElectronics/volkswagen_obd2_pinout.shtml | VW OBD-II pinout |
| RT-CAN | https://www.ross-tech.com/vcds/canbus.php | Ross-Tech "CAN-Bus information" |
| SSP269 | https://www.volkspage.net/technik/ssp/ssp/SSP_269_d1.pdf | VW Self-Study Programme 269 (CAN II: drivetrain/convenience CAN, gateway) |
| JAZ | https://jazdw.net/tp20 | VW TP 2.0 protocol write-up |
| ICH | https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/ | I CAN Hack knowledge base, TP 2.0 chapter (same author as pq-flasher; worked byte-level examples from a PQ35 EPS) |
| PQF-README | https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/README.md | pq-flasher (Python TP 2.0/KWP2000 EPS flasher) |
| PQF-TP20 | https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/tp20.py | its TP 2.0 implementation |
| PYV-README | https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/README.md | PyVCDS (python-can TP 2.0/KWP2000) |
| PYV-TP | https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vwtp.py | its TP 2.0 implementation |
| VWF | https://raw.githubusercontent.com/bri3d/VW_Flash/master/lib/connections/j2534_connection.py | VW_Flash (Simos18 flasher) J2534 connection class |
| FRPM | https://www.scantool.net/scantool/downloads/678/obdlink_frpm_e.pdf | OBDLink/STN "Family Reference and Programming Manual" rev E |
| ELMDS | https://cdn.sparkfun.com/assets/learn_tutorials/8/3/ELM327DS.pdf | ELM327 datasheet ("ELM327DSI", 82 pages) |
| MXP | https://www.scantool.net/obdlink-mxp/ | OBDLink MX+ product page |
| SXP | https://www.scantool.net/obdlink-sx/ | OBDLink SX product page |
| VCX | https://vxdiag.com/pages/vcx-nano-products-features | VXDIAG VCX NANO features |
| DLVW | http://www.dashlogic.com/drewtech_mongoose_pro_vw | Drew Tech MongoosePro VW (reseller page) |
| REGI | https://raw.githubusercontent.com/keenanlaws/J2534-Registry-Info/master/README.md | sample dump of `PassThruSupport.04.04` registry entries |
| CSS | https://www.csselectronics.com/pages/uds-protocol-tutorial-unified-diagnostic-services | CSS Electronics UDS tutorial (padding) |
| PYTIME | https://docs.python.org/3/library/time.html | `time.sleep()` resolution |
| SCANDOC | https://scandoc.org/en/develop/j2534/pt_readmsg.html | third-party PassThruReadMsgs write-up (secondary) |

Unreachable this session: canable.io (TLS failure), drewtech.com product/download pages (404), api.github.com (403).

Notation: `(src: KEY)` cites the table above. Byte values are hex unless stated.

### Verified (source)

#### 0. API surface an implementer needs (prototypes, structs, ABI) — added by the verification pass

- All fourteen entry points, exactly as declared (DLH lines 396–409; SAE §7.2.x prototypes agree):
```c
long PassThruOpen(void *pName, unsigned long *pDeviceID);
long PassThruClose(unsigned long DeviceID);
long PassThruConnect(unsigned long DeviceID, unsigned long ProtocolID, unsigned long Flags, unsigned long BaudRate, unsigned long *pChannelID);
long PassThruDisconnect(unsigned long ChannelID);
long PassThruReadMsgs(unsigned long ChannelID, PASSTHRU_MSG *pMsg, unsigned long *pNumMsgs, unsigned long Timeout);
long PassThruWriteMsgs(unsigned long ChannelID, PASSTHRU_MSG *pMsg, unsigned long *pNumMsgs, unsigned long Timeout);
long PassThruStartPeriodicMsg(unsigned long ChannelID, PASSTHRU_MSG *pMsg, unsigned long *pMsgID, unsigned long TimeInterval);
long PassThruStopPeriodicMsg(unsigned long ChannelID, unsigned long MsgID);
long PassThruStartMsgFilter(unsigned long ChannelID, unsigned long FilterType, PASSTHRU_MSG *pMaskMsg, PASSTHRU_MSG *pPatternMsg, PASSTHRU_MSG *pFlowControlMsg, unsigned long *pFilterID);
long PassThruStopMsgFilter(unsigned long ChannelID, unsigned long FilterID);
long PassThruSetProgrammingVoltage(unsigned long DeviceID, unsigned long PinNumber, unsigned long Voltage);
long PassThruReadVersion(unsigned long DeviceID, char *pFirmwareVersion, char *pDllVersion, char *pApiVersion);
long PassThruGetLastError(char *pErrorDescription);
long PassThruIoctl(unsigned long ChannelID, unsigned long IoctlID, void *pInput, void *pOutput);
```
  (src: DLH 396–409; SAE §7.2)
- Calling convention on Windows is `__stdcall` (`#define PTAPI __stdcall //WINAPI`, FSH `#define APICALL __stdcall`); Linux open drivers export plain cdecl. In ctypes: `ctypes.WinDLL` on Windows, `ctypes.CDLL` for the open-source `.so`/`.dylib`. (src: DLH 60–69; FSH 232; RF-README "plain cdecl")
- `pName` of `PassThruOpen` "Must be NULL (reserved for future use with multiple devices)". (src: SAE line 817)
- `PassThruReadVersion`: "A buffer of at least eighty (80) characters must be allocated for each" of the three strings. (src: SAE line 1784)
- `PassThruStartPeriodicMsg` `TimeInterval`: "in milliseconds. The valid range is 5-65535 milliseconds"; ERR_INVALID_TIME_INTERVAL (0x0B) otherwise. The OpenPort firmware accepts 4 ms and 65,536 ms when passed through; the DLL passes them through. (src: SAE 1314–1315; OP-AB "Where they agree")
- Ioctl structures (used for GET_CONFIG/SET_CONFIG, FIVE_BAUD_INIT):
```c
typedef struct { unsigned long Parameter; unsigned long Value; } SCONFIG;
typedef struct { unsigned long NumOfParams; SCONFIG *ConfigPtr; } SCONFIG_LIST;   /* pInput of GET_CONFIG/SET_CONFIG, pOutput NULL */
typedef struct { unsigned long NumOfBytes; unsigned char *BytePtr; } SBYTE_ARRAY;  /* FIVE_BAUD_INIT in/out */
```
  READ_VBATT / READ_PROG_VOLTAGE: pInput NULL, pOutput → `unsigned long` millivolts. (src: SAE 2029–2046, 1975–1980; FSH 210–225; DLH 217–229)
- Message size limits the DLL must enforce (SAE Figure 42): CAN min/max Tx 4/12 and Rx 4/12 ("4 bytes of CANID, followed by up to 8 data bytes"); ISO15765 4/4099 ("4 bytes of CAN ID, followed by up to 4095 data bytes"); ISO15765 with extended address 5/4100. DataSize outside the Tx range → ERR_INVALID_MSG; received messages outside the Rx range "shall be discarded with no error". (src: SAE §8.3 Figure 42, §8.4, §8.5)
- Windows registry layout for discovering DLLs: `HKEY_LOCAL_MACHINE\Software\PassThruSupport.04.04\<Vendor - Device>` with string values `Vendor`, `Name`, `ConfigApplication`, `FunctionLibrary` (path of the DLL) and DWORD capability flags named after the protocols (`CAN`, `ISO15765`, …, 1 = supported). "Only one key shall be created per DLL installed." (src: SAE §9.2 Figure 46, lines 2961–2990; REGI shows real entries, e.g. `C:\Program Files (x86)\Drew Technologies, Inc\J2534\MongoosePro Chrysler\monps432.dll`)
- Protocol ids: J1850VPW 1, J1850PWM 2, ISO9141 3, ISO14230 4, CAN 5, ISO15765 6, SCI_A_ENGINE 7, SCI_A_TRANS 8, SCI_B_ENGINE 9, SCI_B_TRANS 10. (src: FSH 25–34; SAE Figure 10)

#### 1. PASSTHRU_MSG, RxStatus, TxFlags, indications

##### 1.1 Message structure
- `PASSTHRU_MSG` = `{ unsigned long ProtocolID; RxStatus; TxFlags; Timestamp; DataSize; ExtraDataIndex; unsigned char Data[4128]; }` — six `unsigned long` then 4128 data bytes. (src: SAE lines 2633–2640; DLH; FSH 199–207; CXH `PASSTHRU_MSG_DATA_SIZE (4128)`)
- "The total message size (in bytes) is the DataSize, and includes header bytes, ID bytes, and data bytes." "When using CAN or ISO 15765-4, the first 4 bytes of Data contain the CAN ID. Data[0] contains CAN ID bits 28-24 (the three most significant bits will be zero), Data[1] contains bits 23-16, Data[2] contains bits 15-8, and Data[3] contains bits 7-0." (big-endian). The spec's example message: "DataSize: 14. The size of our example message, including the CAN ID." So **DataSize = 4 + payload length**; an 8-byte CAN frame has DataSize 12. (src: SAE 2626, §8.3, line 3446)
- Timestamp: "Received message timestamp (microseconds): For the START_OF_FRAME indication, the timestamp is for the start of the first bit of the message. For all other indications and transmit and receive messages, the timestamp is the end of the last bit of the message." (src: SAE §8.2 lines 2652–2656; FSH comment `/* receive message timestamp(in microseconds) */`)
- ExtraDataIndex: "When no extra data bytes are present in the message, ExtraDataIndex shall be set equal to DataSize." "For received messages, ExtraDataIndex shall be equal to DataSize, except when the interface is returning SAE J1850 PWM IFR bytes." For indications "ExtraDataIndex must be zero". (src: SAE §8.2, §8.5 line 2763, §8.6 line 2775)
- "The application must fill all fields for each PASSTHRU_MSG structure passed to the API, except for RxStatus, Timestamp, and ExtraDataIndex. These three fields are only valid when reading a message or indication". (src: SAE §8.2 lines 2668–2670)
- Tactrix OpenPort 2.0 timestamp: "counts microseconds since power-on (two frames 1.2 s apart differed by 1,238,083) and wraps about every 71 minutes" (2^32 µs = 71.6 min). (src: OP-PROTO §7.1 lines 373–374)

##### 1.2 RxStatus bits (SAE J2534-1 Figure 43) — values confirmed in three headers
| name | bit | value | meaning |
|---|---|---|---|
| TX_MSG_TYPE | 0 | 0x00000001 | "0 = received i.e. this message was transmitted on the bus by another node, 1 = transmitted i.e. this is the echo of the message transmitted by the PassThru device" |
| START_OF_MESSAGE (FSH alias ISO15765_FIRST_FRAME) | 1 | 0x00000002 | "first byte of an ISO9141 or ISO14230 message or first frame of an ISO15765 multi-frame message" |
| RX_BREAK | 2 | 0x00000004 | break received — "SAE J2610 and SAE J1850 VPW only" (never on CAN) |
| TX_INDICATION (FSH alias TX_DONE) | 3 | 0x00000008 | "ISO 15765 TxDone indication- CANID and extended address, if present, shall be included in the message structure" |
| ISO15765_PADDING_ERROR | 4 | 0x00000010 | "For ProtocolID ISO 15765 a CAN frame was received with less than 8 data bytes" |
| (reserved) | 5–6 | — | "Reserved for SAE – Shall be set to 0" |
| ISO15765_ADDR_TYPE | 7 | 0x00000080 | "1= extended address is first byte after the CAN ID" |
| CAN_29BIT_ID | 8 | 0x00000100 | "0 = 11-bit Identifier, 1 = 29-bit Identifier" |
| reserved SAE | 9–15 | — | 0 |
| reserved J2534-2 | 16–23 | — | 0 (J2534-2 defines SW_CAN_HV_RX = 0x00010000 here, src: DLH 334) |
| tool-specific | 24–31 | — | "Tool manufacturer specific – Shall be set to 0" |
(src: SAE §8.7.1 Figure 43 lines 2799–2841; DLH 322–328; FSH 172–179)

- Valid RxStatus combinations (SAE Figure 44; "The RxStatus bits CAN_29BIT_ID and ISO15765_ADDR_TYPE are not shown because they do not affect the message/indication type"), as full 32-bit values with those two masked off:
  - Normal received message: `0x00`
  - RxStart (ISO15765 FirstFrame seen): `0x02`
  - RxBreak: `0x04` (not CAN)
  - RxPadError: `0x10`
  - **TxDone: `0x09`** (TX_DONE=1 and TX_MSG_TYPE=1 in Figure 44; Appendix A.2.3: "A TxDone indication is composed of: TX_MSG_TYPE = 1, TX_DONE=1 and ISO15765_PADDING_ERROR = 0")
  - Loopback message: `0x01`
  (src: SAE §8.7.2 Figure 44 lines 2852–2878; A.2.3 line 3490)
- Ordering rule: "If a transmit message generated a loopback message and TxDone indication, the TxDone indication shall always be queued first." (src: SAE §7.2.5 lines 1068–1069; §8.7.2 line 2854)

##### 1.3 TxFlags bits (SAE Figure 45)
| name | bit | value | note |
|---|---|---|---|
| ISO15765_FRAME_PAD | 6 | 0x00000040 | "0 = no padding, 1 = pad all flow controlled messages to a full CAN frame using zeroes" |
| ISO15765_ADDR_TYPE (FSH alias ISO15765_EXT_ADDR) | 7 | 0x00000080 | extended addressing |
| CAN_29BIT_ID | 8 | 0x00000100 | 29-bit id (same value as the connect flag) |
| WAIT_P3_MIN_ONLY | 9 | 0x00000200 | ISO 14230 only: "After a response is received for a physical request, the wait time shall be reduced to P3_MIN" |
| SW_CAN_HV_TX | 10 | 0x00000400 | **J2534-2** (single-wire CAN high-voltage wake-up); in J2534-1 bits 15–10 are "Reserved for SAE – shall be set to 0" (src: DLH 354; SAE Figure 45) |
| BLOCKING | 16 | 0x00010000 | legacy 02.02-API blocking transmit flag; in 04.04 bits 21–16 are "Reserved for SAE J2534-2 – shall be set to 0" (src: FSH 185; SAE) |
| SCI_MODE | 22 | 0x00400000 | SCI half-duplex |
| SCI_TX_VOLTAGE | 23 | 0x00800000 | "apply 20V after message transmit" (SCI) |
(src: SAE §8.7.3 Figure 45 lines 2884–2922; DLH 343–354; FSH 183–193)
- "The interface shall ignore any flags that do not apply to the current channel." (src: SAE §8.7.3)
- Connect flags (PassThruConnect `Flags`): CAN_29BIT_ID 0x00000100, ISO9141_NO_CHECKSUM 0x00000200, CAN_ID_BOTH 0x00000800, ISO9141_K_LINE_ONLY 0x00001000. ERR_INVALID_MSG when "The CAN_29_BIT flag of the message does not match the CAN_29_BIT flag passed to PassThruConnect, unless the CAN_ID_BOTH bit was set on connect"; ERR_MSG_PROTOCOL_ID "when the ProtocolID field in the message does not match the Protocol ID specified when opening the channel". (src: FSH 165–168; DLH 173–176; SAE §8.4)

##### 1.4 Indications on CAN vs ISO15765 channels (what to expect in the read queue)
- SAE Figure 11: on a **CAN** channel the only things that can appear are Normal Messages and Loopback Messages (if enabled). On an **ISO15765-4** channel: Normal Message, RxStart Indication, TxDone Indication, Loopback Message. RxBreak only on J1850 VPW and SCI. (src: SAE §7.2.5 Figure 11 lines 1080–1093)
- TxDone: "A TxDone indication (ISO 15765 only) is generated by the DLL after a SingleFrame message is sent, or the last frame of a multi-segment transmission is sent. DataSize shall be 4 (or 5 when the message was using Extended Addressing). Data shall contain the CAN ID (and possible Extended Address) of the message just sent. If loopback is on, the TxDone indication shall precede the loopback message in the receive queue." (src: SAE §8.6 lines 2778–2783)
- RxStart: "An RxStart indication is generated by the DLL when starting to receive a message on ISO9141 or ISO14230, or when receiving the FirstFrame signal of a multi-segment ISO 15765 message." Its `RxStatus` has START_OF_MESSAGE = 1, DataSize 4 ("5 with extended addressing"), ExtraDataIndex 0, "The message data will contain the CAN ID of the sender." "single-frame messages do not generate an RxStart indication". "Application writers should not assume that the complete message will always follow the RxStart indication" (other messages may be interleaved). (src: SAE §8.6 line 2794; A.4 lines 3552–3554; A.5 lines 3647–3648; lines 3622–3625)
- "Filters shall not be applied to indications or loopback messages." (src: SAE §7.2.9 line 1490)
- **Loopback is OFF by default** (`LOOPBACK` 0x03 default 0). "Loopback messages must only be sent after successful transmission of a message. Loopback frames are not subject to message filtering." (src: SAE config table lines 2125–2132; DLH 246 `[0]`)
- **[promoted]** Tactrix OpenPort 2.0 / `op20pt32.dll`, measured on a 2009 Audi 1.9 TDI: the TxDone indication is delivered as **`RxStatus 9`, `DataSize 4`** with the CAN id in Data, i.e. exactly the spec's TX_MSG_TYPE | TX_DONE. "J2534-1 §8.6 defines the indication as `TX_MSG_TYPE | TX_DONE`, `DataSize` 4, `Data` the CAN id of the message sent, `ExtraDataIndex` 0, and that is how both Tactrix's DLL (measured on the Audi: `RxStatus 9`, `DataSize 4`) and this driver deliver it." (src: OP-PROTO §7.5 lines 439–444)
- On the cable (firmware 1.17.4877) every successful ISO15765 transmit produces exactly one transmit-indication frame (`0x10`) carrying the 4-byte CAN id and no data, "right after the `aro`"; "Periodic messages produce none". A segmented receive arrives as "a `0x80` frame with the id only, then `0x40` frames with id + data" (chunks of up to 70 data bytes, each repeating the id, the last marked `0x40`) which the DLL delivers as a 4-byte START_OF_MESSAGE indication followed by the whole message; Tactrix's own `canlogger`/`klogger` samples begin `dump_msg` with `if (msg->RxStatus & START_OF_MESSAGE) return;`. The DLL strips the repeated id from every chunk after the first (fed a 600-byte reply with the id only in the first chunk it delivered 598 bytes). Against the live bench ECU "Both drivers sent identical commands and delivered every reply identically: the TxDone indication with the CAN id, the first-frame indication, and the reassembled message, with the same `RxStatus` and `ExtraDataIndex`." (src: OP-PROTO §7.3, §7.5, §7.6; OP-AB "Long replies", "Against a live ECU")
- Tactrix raw CAN channel: "On a raw CAN channel (5) every frame arrives with status `0x00`, our own and the ECU's alike … Raw CAN has no transport layer: one frame is one whole message." The delivered J2534 message (both drivers identical) is `RxStatus` 0, DataSize = 4 + dlc (their example: "`DataSize` 8, `ExtraDataIndex` 8, CAN id first" for a 4-data-byte frame), ExtraDataIndex = DataSize. (src: OP-PROTO §7.8 lines 508–513)
- **Tactrix raw CAN echoes your own frames even without LOOPBACK**: "On a raw CAN channel with a filter that passes everything, the frame you just sent comes back as an ordinary `0x00` frame. That is not a loopback: with a filter that excludes its id, it does not come back. A CAN node sees its own transmission on the bus, and an open filter shows it to you like any ECU's frame. Filter by id." (src: OP-PROTO §7.7 lines 472–477)
- Tactrix LOOPBACK on raw CAN (`ats<ch> 3 1`) adds a *second*, separate frame, status `0x20`, "whose payload is four zero bytes instead of the CAN id"; "Tactrix's DLL delivers it as a `TX_MSG_TYPE` message of four zero bytes". "With nothing on the bus the transmit fails with `are 9` before any echo: the echo follows a successful transmit." (src: OP-PROTO §7.7 lines 479–484)
- Tactrix LOOPBACK on ISO15765: the echoes (one `0x20` frame per CAN frame the cable sent, plus the flow-control frames the cable sends while receiving, "id and data intact (`00 00 07 b5 30 00 00 00 00 00 00 00`)") are reported by the firmware on raw CAN channel 5, and "Tactrix's DLL delivers the `0x20` frames to the ISO 15765 channel unchanged (`ProtocolID` CAN, `TX_MSG_TYPE`)"; the DLL queues TxDone before the echo. (src: OP-PROTO §7.7 lines 486–503; OP-AB "Routing")
- Cable status byte on CAN (firmware's own, not J2534): `0x80` START, `0x40` END, `0x20` LOOPBACK, `0x10` transmit indication, `0x02` 29-bit id ("`0x02` follows the 29-bit id exactly and nothing else"; Tactrix firmware 1.44 changelog "return CAN_29BIT_ID flag on appropriate read results"). (src: OP-PROTO §7.2, §7.4)

**Implementation form — receive dispatch for a J2534 read (both channel kinds):**
```python
TX_MSG_TYPE=0x01; START_OF_MESSAGE=0x02; TX_INDICATION=0x08; PAD_ERR=0x10; ADDR_TYPE=0x80; RX_29BIT=0x100
def classify(msg):                       # msg: PASSTHRU_MSG after PassThruReadMsgs
    st = msg.RxStatus
    if st & TX_MSG_TYPE:                 # TxDone (0x09) or loopback (0x01): never ECU data
        return "txdone" if st & TX_INDICATION else "loopback"
    if st & START_OF_MESSAGE:            # ISO15765 RxStart: DataSize 4 (5 with ext addr), data = CAN id only
        return "rxstart"
    if msg.DataSize < 4:                 # malformed
        return "drop"
    can_id = int.from_bytes(bytes(msg.Data[:4]), "big")
    hdr = 5 if st & ADDR_TYPE else 4
    payload = bytes(msg.Data[hdr:msg.DataSize])
    flags = {"pad_error": bool(st & PAD_ERR), "ext": bool(st & RX_29BIT)}
    return ("data", can_id, payload, msg.Timestamp)   # Timestamp in microseconds
```
Do **not** rely on `DataSize == 4` alone to detect indications on a CAN channel: a legitimate raw CAN frame with DLC 0 also has DataSize 4; use RxStatus. On an ISO15765 channel a 4-byte message with RxStatus 0 cannot occur for a received ECU message (PCI-stripped payload is >= 1 byte), so the current "length heuristic" in `j2534.py` is safe there but wrong on the CAN channel. Also: on the Tactrix DLL a raw-CAN loopback echo is a `TX_MSG_TYPE` message of **four zero bytes** (not the id), and the raw CAN channel returns your own frames as RxStatus 0 — filter by id (see §2.5 rule 4).

#### 2. CAN protocol channel: filters, timeouts, latency

##### 2.1 Filter semantics (PassThruStartMsgFilter)
- FilterType values: PASS_FILTER 0x00000001, BLOCK_FILTER 0x00000002, FLOW_CONTROL_FILTER 0x00000003. (src: SAE §7.2.9; DLH 182–184; FSH 130–132)
- "The default filter behavior after PassThruConnect is to block all messages, which means no messages will be placed in the receive queue until a PASS_FILTER has been set. Messages that match a PASS_FILTER can still be blocked by a BLOCK_FILTER". (src: SAE §7.2.9 line 1429, "For all protocols except ISO 15765")
- Mask semantics: pMaskMsg is "the mask message that will be ANDed to each incoming message"; "If the result matches this pattern message and the FilterType is PASS_FILTER, then the incoming message will be added to the receive queue". "When using the CAN protocol, setting the first 4 bytes of pMaskMsg to $FF makes the filter specific to one CAN ID." "Message bytes in the received message that are beyond the DataSize of the pattern message will be treated as 'don't care'." (src: SAE §7.2.9.2 lines 1548–1580)
- Therefore a PASS filter with **mask = 00 00 00 00, pattern = 00 00 00 00, DataSize 4** admits every CAN id ((id & 0) == 0 is always true). Confirmed on the OpenPort: "A message filter is mandatory before the device forwards any received frame (a pass-all filter is mask 0 / pattern 0)." and the open driver's smoke test opens "raw CAN @ 500 kbit, pass-all filter, sniff 3 s". (src: SAE mask/pattern rules; RF-README "How it works" item 3; RF-RE §4 item 3)
- "Both pMaskMsg and pPatternMsg must have the same DataSize and TxFlags. Otherwise, the interface shall return ERR_INVALID_MSG" (spec). pFlowControlMsg "must be null when requesting a PASS_FILTER or a BLOCK_FILTER". On a CAN channel "FLOW_CONTROL_FILTERs must not be used and shall cause the interface to return ERR_INVALID_FILTER_ID". (src: SAE lines 1425–1427, 1588)
- Tactrix DLL deviations measured: mask and pattern of different lengths → `ERR_FAILED` (not ERR_INVALID_MSG); NULL mask/pattern or flow-control filter with no flow-control message → `ERR_FAILED` (not ERR_NULL_PARAMETER); a flow-control message passed with a PASS/BLOCK filter is **ignored**, not rejected ("refusing it would fail an application that passes a zeroed message rather than NULL"); filter types 0 and 4 are sent to the cable, which answers `are 22` = ERR_INVALID_FILTER_ID. (src: OP-AB "Return codes", "Requests refused", "Where they agree")
- Filter action table (SAE Figure 16): message passes only if (a PASS filter exists and matches) AND NOT (a BLOCK filter matches); every other row is Block. (src: SAE §7.2.9 Figure 16)
- "PassThruClose shall delete all filters on all channels for the device."; PassThruDisconnect: "After this call, all filters associated with the channel" are deleted. CLEAR_MSG_FILTERS Ioctl = 0x0A; on the OpenPort it is the single cable command `atk<ch> -1`, which "removes every filter on the channel and answers `aro` even when there are none". (src: SAE lines 1028, 1406; DLH 225; OP-PROTO §4 lines 221–225)
- Spec minimum: "A minimum of ten message filters shall be supported by the interface" and a "minimum of ten periodic messages" (FSH comments ERR_EXCEEDED_LIMIT: "The limit(ten) of filter/periodic messages has been exceeded"). OpenPort 2.0 limits (measured) are exactly that: **10 filters per channel** ("an eleventh live `atf` on a channel" → `are 12` = ERR_EXCEEDED_LIMIT 0x0C), 10 periodic messages per channel ("an eleventh `atm`" → `are 12`); "Filter ids are never reused within a session: they count up across all channels and restart only at `ata` or `atz`". (src: SAE lines 1290, 1404; FSH 111; OP-PROTO §4, §6; OP-API; OP-AB)

**Implementation form — CAN channel setup for TP 2.0 + sniffing (11-bit, 500 kbit):**
```
PassThruConnect(dev, CAN=5, Flags=0, BaudRate=500000, &ch)
# pass-everything (router/sniffer):
mask    = PASSTHRU_MSG(ProtocolID=5, TxFlags=0, DataSize=4, Data=00 00 00 00)
pattern = PASSTHRU_MSG(ProtocolID=5, TxFlags=0, DataSize=4, Data=00 00 00 00)
PassThruStartMsgFilter(ch, PASS_FILTER=1, &mask, &pattern, NULL, &fid)
# or one-id (e.g. only the ECU's TP 2.0 tx id 0x300):
mask.Data = 00 00 07 FF ; pattern.Data = 00 00 03 00      # mask 0x7FF keeps the 11 id bits
```
Transmit a raw frame: `msg = PASSTHRU_MSG(ProtocolID=5, TxFlags=0, DataSize=4+len(data), Data=id.to_bytes(4,'big')+data)`; `PassThruWriteMsgs(ch, &msg, &n=1, Timeout=ms>0)`. CAN DataSize must be 4..12: the cable answers `are 10` (ERR_INVALID_MSG) to CAN writes of 0, 3 or 13 bytes and the Tactrix DLL does not pre-check them. (src: OP-AB "Requests refused")

##### 2.2 PassThruReadMsgs timeout semantics
- Prototype: `long PassThruReadMsgs(unsigned long ChannelID, PASSTHRU_MSG *pMsg, unsigned long *pNumMsgs, unsigned long Timeout)`. (src: SAE §7.2.5.1; DLH 400)
- "Read timeout (in milliseconds). If a value of 0 is specified the function retrieves up to pNumMsgs messages and returns immediately. Otherwise, the API will not return until the Timeout has expired, an error has occurred, or the desired number of messages have been read. If the number of messages requested have been read, the function shall not return ERR_TIMEOUT, even if the timeout value is zero." (src: SAE §7.2.5.2 lines 1122–1126)
- Return codes (Figure 12): ERR_TIMEOUT = 0x09 "Timeout. Device could not read the specified number of messages. The actual number of messages read is placed in <NumMsgs>. **If a timeout occurs and there are no available messages, ERR_BUFFER_EMPTY must be returned.**" ERR_BUFFER_EMPTY = 0x10 "Protocol message buffer empty, no messages available to read." ERR_BUFFER_OVERFLOW = 0x12 "Indicates a buffer overflow occurred and messages were lost. The actual number of messages read is placed in <NumMsgs>." (so the surviving messages are still returned — handle 0x12 as data + warning, not as fatal). (src: SAE §7.2.5.3 lines 1128–1160)
- Hence a compliant device returns ERR_BUFFER_EMPTY (0x10) when nothing at all arrived, ERR_TIMEOUT (0x09) only when *some but fewer than requested* arrived. Treat both as "no more data" and always read `pNumMsgs` back — it holds the count actually filled, even on 0x09/0x12. (src: SAE as above)
- "All messages and indications shall be read in the order that they occurred on the bus." "On ISO 15765, PCI bytes are transparently removed by the API." (src: SAE §7.2.5 lines 1067–1072)
- Tactrix `op20pt32.dll` measured in the A/B harness: `PassThruReadMsgs(timeout=0)` on an idle channel "returns after ~6 ms" (the open driver "returns in microseconds"); the DLL has a "~6 ms polling granularity of `ReadMsgs`"; `ReadMsgs(100)` / `ReadMsgs(500)` return at 107 / 508 ms (the open driver: 99.5 / 501 ms). **Caveat added by the verification pass:** these DLL numbers were taken with the DLL running under Wine + box64 *interpreted* ("`BOX64_DYNAREC=0`", "The DLL runs interpreted, so its CPU-bound work is tens of times slower than native, and per-call latencies cannot be compared. What can be compared are the waits the DLL chooses, which are wall-clock" — the 500 ms / 5 s / 300 ms / ~6 ms / 107 / 508 ms figures). "treat its timings as upper bounds". (src: OP-AB "Where the two drivers differ" table; "Timing"; "How the DLL runs without Windows")
- Tactrix DLL waits for the cable's `aro <seq>` reply "500 ms for most commands, 5 s for `atr` and `atg`" (READ_VBATT and GET_CONFIG), then returns ERR_TIMEOUT; "It ignores a reply without its number." (src: OP-PROTO §4 lines 261–262; OP-AB "What Tactrix's DLL sends")
- The open driver (not the DLL) queues "up to 1 MiB (about 29,000 raw CAN frames)" per channel and returns ERR_BUFFER_OVERFLOW with the surviving messages still delivered. (src: OP-API)
- A shipped Python J2534 reader-thread pattern that flashes real VW ECUs (VW_Flash/Simos18 via Tactrix): the rx thread loops `PassThruReadMsgs(channelID, protocol, 1, 1)` — one message, **1 ms timeout** — and pushes each message into a queue; `specific_wait_frame` then waits on that queue with a 4 s timeout; `ISO15765_STMIN`/`ISO15765_BS` are set to 0 via SET_CONFIG right after connect. (src: VWF lines 51–120, 160–200)

##### 2.3 PassThruWriteMsgs timeout semantics
- "Write timeout (in milliseconds). When a value of 0 is specified, the function queues as many of the specified messages as possible and returns immediately. When a value greater than 0 is specified, the function will block until the Timeout has expired, an error has occurred, or the desired number of messages have been transmitted on the vehicle network. Even if the device can buffer only one packet at a time, this function shall be able to send an arbitrary number of packets if a Timeout value is supplied … If the number of messages requested have been written, the function shall not return ERR_TIMEOUT, even if the timeout value is zero. When an ERR_TIMEOUT is returned, only the number of messages that were sent on the vehicle network is known. The number of messages queued is unknown." pNumMsgs "On return will contain the actual number of messages that were transmitted (when Timeout is non-zero) or placed in the transmit queue (when Timeout is zero)." ERR_BUFFER_FULL (0x11) "Only applies when Timeout is zero." (src: SAE §7.2.6.2 lines 1200–1225; Figure 13 lines 1266–1268)
- "Only one message per protocol can be in transmission at a time (with one exception- See PassThruStartPeriodicMsg)". "The messages are placed in the buffer and sent in the order they were received." "Specifying a non-zero Timeout performs a blocking write." (src: SAE §7.2.6 lines 1166–1172)
- Bus errors: devices "shall use the Retry strategy" for "All CAN errors, such as bus off, lack of acknowledgement, loss of arbitration, and no connection (lack of terminating resistor)"; "If the error condition persists, a blocking write will wait the specified timeout and return ERR_TIMEOUT … After returning from the function, the device does not stop the retries. The only functions that will stop the retries are PassThruDisconnect (on that protocol), PassThruClose, or PassThruIoctl (with an IoctllD of CLEAR_TX_BUFFER)." (src: SAE §6.10.2 lines 718–734)
- **[corrected] Tactrix write timeout on the wire.** The DLL sends `att<proto> <DataSize> <TxFlags> <budget_us> <seq>` + payload, where `<budget_us>` is the caller's Timeout × 1000 ("is how long the cable may try to get the message onto the bus, in microseconds"), **with 1,000,000 substituted when Timeout is 0** — measured on the byte tap: `att6 6 64 1000000` (Timeout 0, no sequence number) vs `att6 6 64 1000000 7` (Timeout 1000). For Timeout = 0 "the DLL does not wait … It returns 0 with one message sent, as J2534 asks"; but because the command is unnumbered the cable gives no reply at all, "and while the firmware keeps trying, the next command (`atc6`) goes unanswered for about a second, so the DLL's `PassThruDisconnect` straight after returns `ERR_TIMEOUT`." A replayed reflash tool passing 5000 ms sent `5000000`; "Without it, the firmware's ~1 s default would cut short a 257-byte transfer paced by a slow ECU." (src: OP-AB "What Tactrix's DLL sends"; OP-PROTO §4 lines 214–217) — The earlier bullet quoted RF-RE's disassembly reading ("timeout==0 → 3-arg form … A zero timeout makes the firmware return `ERR_TIMEOUT` immediately without ever putting the frame on the bus"); that reading is contradicted by OP-AB's tap of the real DLL (1.02.0.4868) against the real cable and is **moved to REPORTED**. Both sources agree on the practical rule: **always pass a nonzero write timeout (e.g. 100–1000 ms for diagnostics, several seconds for flash-page transfers)**.
- Tactrix: "Every transmit returns 9 (`ERR_TIMEOUT`)" means "Nothing on the bus acknowledged the frame: no ECU connected, or the ignition is off." "With no ECU, transmits fail with `ERR_TIMEOUT` on both sides for want of a second node." (src: OP-README troubleshooting; OP-AB "Against the cable")
- Tactrix DLL after a transmit the cable times out (`are 9`) returns ERR_TIMEOUT with `pNumMsgs` "left as the caller set it (3 for a three-message write that sent one)" — contrary to the spec; the open driver returns the number sent. (src: OP-AB "Return codes")
- Tactrix DLL "picks the channel from the message's `ProtocolID`": a CAN-protocol message written to an ISO15765 channel "goes out as `att5`" (raw), an ISO15765 message written to a CAN channel returns ERR_INVALID_PROTOCOL_ID. Always set `ProtocolID` = the channel's protocol. (src: OP-AB "Routing")

##### 2.4 Tactrix OpenPort 2.0 USB path and latency numbers
- Hardware (vendor page): "72Mhz 32-bit processor", "USB 2.0 full speed device (USB-A/Mini cable included)", "CAN 2.0 (CAN/ISO15765)", "K-line (ISO9141/ISO14230(KWP2000)/dual K line)", "J2534 PassThru support with Windows DLL", "Standalone datalogs to microSD / microSDHC card without a laptop", "Supports 12 volt vehicles", price $169.00. (src: TAC lines 25–40)
- USB descriptor: VID:PID `0403:cc4d`, manufacturer "Tactrix", product "OpenPort 2.0", "USB 1.1, bus-powered at 100 mA"; a standard CDC-ACM device: interface 0 CDC control (class 02/02/01 "AT commands V.250") with 16-byte interrupt IN 0x81, interface 1 CDC data with **64-byte bulk OUT 0x02 / bulk IN 0x82**. "The DLL's own transport is just `ReadFile`/`WriteFile` on that endpoint pair" (through `openport.sys`, "a 20 KB KMDF bulk read/write driver"); the DLL "issues one overlapped `ReadFile` of 8191 bytes from a reader thread". (src: OP-PROTO §1 lines 51–60; RF-RE §1; OP-AB "How the DLL runs")
- USB full speed divides bus time into **1 ms frames**: "The host controller divides bus time into 1 ms frames when using low speed (1.5 Mbit/s) and full speed (12 Mbit/s), or 125 μs microframes when using high speed (480 Mbit/s)." (src: W-USB line 44)
- Wire protocol is line-oriented ASCII (`ato…` open, `att…` transmit + payload, `atf…` filter, `atk` stop filter, `ats/atg` set/get config, `atr` analog read, `atm/atn` periodic start/stop, `atv` voltage, `ata` close all, `atz` reset, `ati` identify) with a sequence number (1..0xFFFF, wraps to 1) on every command that the device echoes (`aro <seq>` success, `are <j2534_err> <seq>` error); received frames are length-prefixed binary records `'a' 'r' <chan-digit> <len> <status> <timestamp:4 BE µs> <id:4 BE> <data>` ("len counts every byte after it: len = 9 + datalen"), max 250 payload bytes per record; "after `ar`, a digit `'1'..'6'` is a binary frame for that protocol id; a letter is an ASCII reply". (src: RF-RE §4; OP-PROTO §3, §7.1 lines 360–376)
- Native (non-DLL) call costs on the cable: `PassThruOpen` ≈ 2 ms, `PassThruClose` ≈ 11 ms ("against the DLL's 24 and 6 ms for the same wire work"); open driver's `ReadMsgs(100)` returns at 99.5 ms. (src: OP-AB "Timing")
- K-line through the cable (not CAN; given only as an end-to-end timing example): a fast init took 126–132 ms on the car and 126 ms on the bench with nothing on pin 7; a 5-byte K-line echo with LOOPBACK took 24 ms (10400 baud). (src: OP-AB "On the Audi")

##### 2.5 Is a 100 ms TP 2.0 ACK window (T1) achievable from Python over J2534 raw CAN? — **Yes**, with the design below.
Facts the answer rests on (all verified):
- TP 2.0 channel parameters: 6-byte `A0` request / `A1` response = `Opcode BS T1 T2 T3 T4`; "T1 Timing parameter 1, time to wait for ACK. T1 should be greater than 4*T3"; "T3 … interval between two packets"; T2, T4 "always 0xFF". Timing byte: bits 7–6 = units (0x0 = 0.1 ms, 0x1 = 1 ms, 0x2 = 10 ms, 0x3 = 100 ms), bits 5–0 = "Scale" (multiplier 0..63). `0x8A` = `10 001010` → 10 ms × 10 = **100 ms**; `0x0A` → 0.1 ms × 10 = 1 ms; `0x32` → 0.1 ms × 50 = 5 ms; `0x4A` → 1 ms × 10 = 10 ms. (src: JAZ "Channel parameters", "Timing parameters"; ICH "Timing Parameters" ("`0x8A` = 10 001010 = 10 ms × 10 = 100 ms"); PQF-TP20 comments "T1: 0x8a (time to wait for ack, 10ms * 10 = 100ms)", "0x4a: 1ms * 10 = 10ms"; PYV-TP `scale = [.1, 1, 10, 100]`, `acktime = buf[1] >> 6`, `(scale[acktime] * (buf[1] & 0x3F)) * 0.001`)
- The ECU's T1 governs how fast *our* ACK must land after the last frame of a block it sends us (its "time to wait for ACK"); the tester's T1 governs how long we wait for the ECU's ACK. Worked example from a PQ35 EPS: tester `A0 0F 8A FF 0A FF` (BS 15, T1 100 ms, T3 1 ms) → ECU `A1 0F 8A FF 4A FF` (BS 15, T1 100 ms, **T3 10 ms**: "ECU bumps the inter-packet gap to 10 ms"). jazdw's example trace uses tester `A0 0F 8A FF 32 FF` and ECU `A1 0F 8A FF 4A FF`. (src: ICH "Channel Parameters" example; JAZ example table; PQF-TP20 "Receive timing parameters (e.g. a10f8aff4aff)")
- ACK/sequence rule: data frames carry `op<<4 | seq`; op 0x0 = "Waiting for ACK, more packets follow (max block size reached)", 0x1 = "Waiting for ACK, last packet", 0x2 = "Not waiting for ACK, more packets to follow", 0x3 = "Not waiting for ACK, last packet", 0xB = "ACK, ready for more data", 0x9 = "ACK, not ready for more data". "both tester and ECU have their own counter that persists between transmissions. The counter is incremented after each data transmission. An ACK does not increment any counter, but is expected to use the counter value of the last data transmission that is being acknowledged plus one" → ACK byte = `0xB0 | ((last_rx_seq + 1) & 0xF)`. The first frame of a message carries a big-endian 2-byte total length before the payload. (src: ICH "Data Transmission"; JAZ "Data transmission"; PQF-TP20 `send_ack`/`wait_for_ack`)
- Channel setup: request on CAN id 0x200 = `<dest> C0 <rxid_lo> <rxV|rx_hi> <txid_lo> <txV|tx_hi> 01`, reply on `0x200 + dest` = `00 D0 …` (D6..D8 negative); the tester asks the ECU to transmit on 0x300 (V nibble 0) and leaves its own rx id invalid (V nibble 1); **the ECU then assigns the id the tester must transmit on** — 0x740 for the engine ECU in jazdw's trace, but **0x7A8 for the EPS (logical 0x09)** in icanhack's trace (`00 D0 00 03 A8 07 01`). Never hardcode 0x740: parse bytes 4–5 of the `D0` reply (little-endian 16-bit, V in the top nibble). (src: ICH "Channel Setup" example; JAZ "Channel setup"; PQF-TP20 `open_channel` `struct.unpack("<xBHHB", dat)`)
- Keepalive: `0xA3` "Channel test (1 byte). The ECU responds with an 0xA1 message. Used to keep the channel alive."; `0xA4` Break ("receiver discards all data since last ACK"); `0xA8` Disconnect ("Receiver responds with a disconnect"). PyVCDS pings with `0xA3` every 0.5 s. (src: ICH; JAZ; PYV-TP `pingthread` `time.sleep(.5)`)
- Two independent **Python** TP 2.0 stacks run with T1 = 100 ms through a USB CAN adapter: pq-flasher (comma.ai panda over USB — `from panda import Panda`, `panda.can_recv()`, `panda.can_send(addr, dat, bus, timeout_ms)`; `timeout=0.1`; `time_between_packets = 0.01` after the ECU's `A1`) reflashed a PQ35 EPS over TP 2.0 + KWP2000 ("Transfer data 100% 4080/4096 [00:06, 618.70it/s]"); PyVCDS (python-can + SocketCAN, "officially tested adapter hardware is a CANdleLight board (STM32F072) running the candleLight_fw") implements "VWTP 2.0, AKA 'TP20'" with the same 0x8A parameter and waits `time.sleep(self.acktime)` for ACKs. (src: PQF-README; PQF-TP20; PYV-README lines 26–31; PYV-TP lines 84–148, 232–234)
- The whole J2534 path is bounded by ms-scale numbers: USB full-speed 1 ms frames (W-USB); Tactrix DLL read polling granularity ≈ 6 ms and `ReadMsgs(100)` returning at 107 ms (OP-AB, emulated — upper bound); native open-driver `PassThruOpen` 2 ms (OP-AB); the cable is a 72 MHz MCU with a 64-byte bulk pipe (TAC, OP-PROTO). A 15-frame TP 2.0 block at 500 kbit/s occupies ≈ 15 × ~0.25 ms ≈ 4 ms of bus time (derived); the ACK clock starts at the last frame.
- Python side: `time.sleep()` "The suspension time may be longer than requested by an arbitrary amount, because of the scheduling of other activity in the system." Windows: "On Windows 10 and newer the implementation uses a high-resolution timer which provides resolution of 100 nanoseconds"; "Changed in version 3.11: On Unix, the clock_nanosleep() and nanosleep() functions are now used if available. On Windows, a waitable timer is now used." Unix: `clock_nanosleep()` "(resolution: 1 nanosecond)". `time.perf_counter()` uses the "clock with the highest available resolution to measure a short duration". **[corrected]** the earlier "(previously ≈ 15.6 ms)" is not in the docs and is moved to REPORTED. (src: PYTIME "time.sleep", "perf_counter")
- python-can `Bus.recv(timeout)` returns "None on timeout or a Message object"; `Message.timestamp` "the message was received since the epoch in seconds. Where possible this will be timestamped in hardware." (src: PC-BUS line 167; PC-MSG lines 118–119)

Reasoning: ECU-side ACK deadline 100 ms vs. a worst-case tester path of (USB 1 ms + DLL poll 6 ms + Python dispatch < 1 ms + `PassThruWriteMsgs` round trip ≈ USB 1 ms + cable TX + `aro` ≈ a few ms) ≈ 10–20 ms, i.e. >= 5× margin (derived from the verified numbers above). The margin collapses only if the ACK is *not* written from the thread that reads the frame (e.g. handed through a queue to a worker that sleeps >= 50 ms) or if `PassThruReadMsgs` is called with a long blocking timeout while the ACK is pending. Design rules that keep the margin:
1. The reader thread polls `PassThruReadMsgs(ch, buf[N], &N, Timeout=1..10 ms)` in a loop (small timeout; the DLL adds ≈ 6 ms anyway; VW_Flash uses 1 ms with N=1) and, for a TP 2.0 data frame whose op nibble is 0x0/0x1 (ACK expected), calls `PassThruWriteMsgs` for the ACK **inline** before returning the payload to the router queue.
2. Write the ACK with a nonzero Timeout (>= 50 ms; a Timeout of 0 makes the Tactrix DLL send an unnumbered command whose reply is lost and stalls the next command ~1 s) and check the return code: ERR_TIMEOUT means the frame was never acknowledged on the bus.
3. Keep our own T3 (inter-frame gap we promise the ECU) >= the ECU's requested value (10 ms for the EPS example); `time.sleep()` for 1–10 ms uses a 100 ns timer on Windows 10+ and `clock_nanosleep` on Unix (Python >= 3.11); on 3.10/Windows use a busy-wait on `perf_counter()` for sub-15 ms gaps or require >= 3.11.
4. Because the Tactrix raw CAN channel returns our own transmitted frames as ordinary 0x00 messages when the PASS filter admits their id, the TP 2.0 receiver must ignore frames whose id is our own tx id (whatever the `D0` reply assigned — 0x740, 0x7A8, …) or install the PASS filter on the ECU's id (0x300 + n) only. (src: OP-PROTO §7.7)
5. Keepalive: send 0xA3 (channel test) periodically (PyVCDS: every 0.5 s); the ECU answers with the `A1` parameters response; T1 does not apply to it. (src: ICH; JAZ; PYV-TP)

##### 2.6 Timestamp units and DataSize on the CAN channel (summary for the router)
- Timestamp µs (32-bit; wraps every ≈ 71.6 min on Tactrix). Convert to a monotonic float by unwrapping: `if ts < last: base += 1<<32`. (src: SAE §8.2; OP-PROTO §7.1)
- DataSize = 4 + dlc for every raw CAN frame; ExtraDataIndex = DataSize. (src: SAE §8.3/§8.5; OP-PROTO §7.8)

#### 3. ISO15765 channel for functional OBD-II (0x7DF → 0x7E8..0x7EF)

##### 3.1 Flow-control filter rules (SAE §6.5.6, §7.2.9 "For ISO 15765", Appendix A)
- "PASS_FILTERs and BLOCK_FILTERs must not be used and shall cause the interface to return ERR_INVALID_FILTER_ID". (src: SAE line 1488)
- Device requirement 6.5.6(f): "No single frame or multi-frame messages can be received without matching a flow control filter. No multi-frame messages can be transmitted without matching a flow control filter." and §7.2.9: "Non-segmented messages do not need to match a FLOW_CONTROL_FILTER" (for transmit). (src: SAE lines 581–582, 1492)
- "Both the pFlowControlMsg ID and the pPatternMsg ID must be unique (not match any IDs in any other filters). The only exception is that pPatternMsg can equal pFlowControlMsg to allow for receiving functionally addressed messages. In this case, only non-segmented messages can be received". ERR_NOT_UNIQUE = 0x18 "A CAN ID in pPatternMsg or pFlowControlMsg matches either ID in an existing FLOW_CONTROL_FILTER". (src: SAE lines 1503–1507; DLH 165)
- For a FLOW_CONTROL_FILTER "The mask shall consist of 4 or 5 bytes of $FF, with a corresponding DataSize" (5 only with ISO15765_ADDR_TYPE); the only allowed exception is "Data[0] can be $E3" to mask the priority bits of a 29-bit id (ISO 15765-2 Annex A). "All 3 message pointers must have the same DataSize and TxFlags." (src: SAE lines 1502, 1557–1561)
- Device requirement 6.5.6(e): "Receive a multi-frame message with an ISO15765_BS of 0 and an ISO15765_STMIN of 0"; (g) "Periodic messages will not be suspended during transmission or reception of a multi-frame segmented message." (src: SAE lines 579–584)
- Functional addressing: "The OBD Request is transmitted from the Tester to the ECU using functional addressing. Because segmented transfer is not possible on functional addresses, the message must fit in a single frame. The OBD Response is a message from the ECU to the Tester using physical addressing. Unlike other protocols, the responses are not sequential. In fact, the responses can overlap, as if each ECU were having a private conversation with the Tester." (src: SAE A.1 lines 3272–3278)
- Receive mechanics (A.4): on a FirstFrame whose CAN id matches a filter's pPatternMsg, the device will "Place an RxStart indication in the API receive queue" (START_OF_MESSAGE set, data = sender's CAN id, DataSize 4/5, ExtraDataIndex 0), "Send a FlowControl frame to the conversation partner. The FlowStatus field shall be set to ContinueToSend. The CAN ID of this segment comes from the filter's corresponding pFlowControlMsg … The BS (BlockSize) and STmin (SeparationTime minimum) parameters default to zero, but can be changed with the SET_CONFIG Ioctl", collect the ConsecutiveFrames, then queue "the assembled message … The CAN ID of the assembled message will be the CAN ID of the sender." "If the FirstFrame does not match any flow control filters, then the message must be ignored by the device." Single frames (A.5): "Upon matching a filter, the pass-thru device will strip the PCI byte and queue the packet for reception. If the SingleFrame does not match a flow control filter, it must be discarded." (src: SAE A.4 lines 3548–3567; A.5 lines 3643–3648)
- OpenPort confirmation: "A request sent to the functional id `0x7DF` still needs its flow-control filter on the ECU's own ids (for example `0x7E8`/`0x7E0`), or every multi-frame reply stalls after the first frame." and "Pad ISO 15765 requests. Set the `ISO15765_FRAME_PAD` TxFlag on every ISO 15765 message and on the flow-control message of its filter. The cable pads only when asked, and many ECUs ignore a frame shorter than 8 bytes." "The cable does ISO-TP. The host sends a whole service request and receives a whole reply; the cable sends first and consecutive frames, answers with flow-control frames when receiving, and honours the ECU's block size and separation time when sending." (src: OP-API "Before you start"; OP-PROTO §5 lines 309–316)
- A flow-control message whose TxFlags differ from mask/pattern → Tactrix DLL `ERR_FAILED`, nothing sent. (src: OP-AB "Return codes")
- OBD-II CAN ids: "The diagnostic reader initiates a query using CAN ID 7DFh, which acts as a broadcast address, and accepts responses from any ID in the range 7E8h to 7EFh. ECUs that can respond to OBD queries listen both to the functional broadcast ID of 7DFh and one assigned ID in the range 7E0h to 7E7h. Their response has an ID of their assigned ID plus 8 e.g. 7E8h through 7EFh." "multi-frame communication requires a response to the specific ECU ID rather than to ID 7DFh." Request frame at 7DFh "using 8 data bytes": byte 0 = "Number of additional data bytes: 2", byte 1 = Service, byte 2 = PID, bytes 3–7 "not used (ISO 15765-2 suggests CCh)"; "All CAN frames sent using ISO-TP use a data length of 8 bytes (and DLC of 8). It is recommended to pad the unused data bytes with 0xCC." (VW tools' pad byte: see Open Questions.) (src: W-PID lines 2513–2552)

**Implementation form — functional OBD-II on a J2534 ISO15765 channel:**
```
PassThruConnect(dev, ISO15765=6, Flags=0, BaudRate=500000, &ch)
PAD = 0x40                                   # ISO15765_FRAME_PAD on every message AND on all three filter messages
for i in range(8):                           # 8 filters: one per possible responder
    mask = MSG(ProtocolID=6, TxFlags=PAD, DataSize=4, Data=FF FF FF FF)
    patt = MSG(ProtocolID=6, TxFlags=PAD, DataSize=4, Data=be32(0x7E8+i))   # what we receive
    flow = MSG(ProtocolID=6, TxFlags=PAD, DataSize=4, Data=be32(0x7E0+i))   # id the device uses for our FC frames
    PassThruStartMsgFilter(ch, FLOW_CONTROL_FILTER=3, &mask, &patt, &flow, &fid[i])
# optional but allowed: a 9th filter with pattern == flow == 0x7DF (only single-frame rx; not needed for OBD-II)
PassThruIoctl(ch, SET_CONFIG, SCONFIG_LIST[ISO15765_BS=0x1E:0, ISO15765_STMIN=0x1F:0])   # defaults are already 0
req = MSG(ProtocolID=6, TxFlags=PAD, DataSize=4+2, Data=00 00 07 DF 01 0C)   # service 01 PID 0C, no PCI byte: API adds it
PassThruWriteMsgs(ch, &req, &1, Timeout=1000)
# then PassThruReadMsgs with timeout ~ P2 (50 ms) repeatedly until ERR_BUFFER_EMPTY/ERR_TIMEOUT with 0 msgs,
# collecting: TxDone (RxStatus 0x09, DataSize 4, id 0x7DF) -> ignore; RxStart (0x02) -> ignore;
# data messages: Data[0:4] = 0x7E8..0x7EF, Data[4:] = 41 0C hh ll (PCI already stripped)
```
Note the 10-filter-per-channel limit on the OpenPort 2.0 (src: OP-API, OP-PROTO §6): 8 OBD filters + at most 2 more (0x7E0/0x7E8 is already among the 8). Stop the 8 OBD filters (or `CLEAR_MSG_FILTERS`) before opening a UDS session to another module that is also in 0x7E0..0x7E7 (e.g. TCU 0x7E1/0x7E9) with a different padding/flags setup, otherwise ERR_NOT_UNIQUE.

##### 3.2 ISO15765 configuration parameters (SET_CONFIG / GET_CONFIG = Ioctl 0x02 / 0x01)
| parameter | id | valid | default | meaning (SAE table) |
|---|---|---|---|---|
| DATA_RATE | 0x01 | 5–500000 | protocol specific | "Represents the desired baud rate. An ERR_INVALID_IOCTL_VALUE will be returned if the desired baud rate cannot be achieved within the tolerance specified"; interface stays "at the previous baud rate" |
| LOOPBACK | 0x03 | 0 (OFF) / 1 (ON) | 0 | "1 = Echo transmitted messages, including periodic messages, in the receive queue." |
| BIT_SAMPLE_POINT | 0x17 | 0–100 (%) | 80 | "For a protocol ID of CAN" |
| SYNC_JUMP_WIDTH | 0x18 | 0–100 (%) | 15 | "For a protocol ID of CAN" |
| ISO15765_BS | 0x1E | 0x0–0xFF | 0 | block size the interface reports to the vehicle for receiving segmented transfers (our FC) |
| ISO15765_STMIN | 0x1F | 0x0–0xFF | 0 | separation time the interface reports to the vehicle for receiving (our FC) |
| BS_TX | 0x22 | 0x0–0xFF, 0xFFFF | 0xFFFF | override of the vehicle's BS when *we* transmit; 0xFFFF = use vehicle's value (DashLogic name `ISO15765_BS_TX`) |
| STMIN_TX | 0x23 | 0x0–0xFF, 0xFFFF | 0xFFFF | override of the vehicle's STmin when we transmit; 0xFFFF = use vehicle's value (DashLogic name `ISO15765_STMIN_TX`) |
| ISO15765_WFT_MAX | 0x25 | 0x0–0xFF | 0 | number of WAIT flow control frames allowed (N_WFTmax) during a multi-segment transfer |
(src: SAE Figure 36 config table lines 2117–2300; DLH 245–280; FSH 54–93)
- Ioctl ids: GET_CONFIG 0x01, SET_CONFIG 0x02, READ_VBATT 0x03, FIVE_BAUD_INIT 0x04, FAST_INIT 0x05, CLEAR_TX_BUFFER 0x07, CLEAR_RX_BUFFER 0x08, CLEAR_PERIODIC_MSGS 0x09, CLEAR_MSG_FILTERS 0x0A, CLEAR_FUNCT_MSG_LOOKUP_TABLE 0x0B, ADD_TO_FUNCT_MSG_LOOKUP_TABLE 0x0C, DELETE_FROM_FUNCT_MSG_LOOKUP_TABLE 0x0D, READ_PROG_VOLTAGE 0x0E. The FUNCT_MSG_LOOKUP_TABLE ioctls are for J1850PWM functional addresses, not CAN. **[corrected]** On the Tactrix DLL `CLEAR_FUNCT_MSG_LOOKUP_TABLE` returns **0 with nothing sent** (the open driver returns ERR_NOT_SUPPORTED); `READ_PROG_VOLTAGE` with `pInput` NULL returns -1 with nothing sent on the Tactrix DLL (pass a pin number). (src: DLH 217–229; FSH 40–50; SAE §7.3; OP-AB "Return codes")
- Tactrix cable supports on ISO 15765 exactly: `DATA_RATE, LOOPBACK, BIT_SAMPLE_POINT, SYNC_JUMP_WIDTH, ISO15765_BS, ISO15765_STMIN, BS_TX, STMIN_TX, ISO15765_WFT_MAX` ("Anything else answers `ERR_NOT_SUPPORTED`"; cable parameter numbers 30/31/34/35/37 = 0x1E/0x1F/0x22/0x23/0x25). Both drivers send a SET_CONFIG list in full and return "the last one's status" (`[3, 127]` gives ERR_NOT_SUPPORTED, `[127, 3]` gives 0), so put the parameter you care about last or set them one per call. "Neither converts units". (src: OP-API "Configuration parameters", "IOCTLs"; OP-PROTO §5; OP-AB "Where they agree")
- Tactrix DLL **crashes the calling process** when GET_CONFIG/SET_CONFIG receive a NULL `pInput` ("read fault at address 0") or FAST_INIT receives NULL `pInput` ("write fault at 0x11") — never pass NULL. (src: OP-AB "Crashes")
- ISO 15765-2 FC frame: byte0 = `0x3F` where F = FlowStatus (0 = ContinueToSend, 1 = Wait, 2 = Overflow/abort), byte1 = BS ("A value of zero allows the remaining frames to be sent without flow control or delay"), byte2 = STmin ("values up to 127 (0x7F) specify the minimum number of milliseconds … values in the range 241 (0xF1) to 249 (0xF9) specify delays increasing from 100 to 900 microseconds"); FF carries "The 12-bit length field … allows up to 4095 bytes of user data"; "Prior versions were limited to a maximum payload size of 4095 bytes" (2016 edition: up to 2^32−1). (src: W-TP lines 71–95)
- python can-isotp defaults for comparison: `rx_flowcontrol_timeout` 1000 ms, `rx_consecutive_frame_timeout` 1000 ms, `blocksize` 8, `stmin` 0, `wftmax` 0, `max_frame_size` 4095. (src: ISOTP-PY parameter table)
- Linux ISO-TP socket (CAN_ISOTP): `frame_txtime` is "frame transmission time (defined as N_As/N_Ar inside the ISO standard)"; options `CAN_ISOTP_TX_PADDING`/`RX_PADDING` with `txpad_content`/`rxpad_content`, `CAN_ISOTP_CHK_PAD_LEN`/`CHK_PAD_DATA`; `wftmax` "maximum number of wait frames provided in flow control frames" and "no support is present for sending 'wait frames'". Errors: `-ETIMEDOUT` rx data timeout, `-ECOMM` flow control reception timeout, `-EMSGSIZE` FC overflow, `-EBADMSG` wrong padding. (src: KISOTP)

##### 3.3 Error codes (complete, SAE Figure 47 / headers)
STATUS_NOERROR 0x00; ERR_NOT_SUPPORTED 0x01; ERR_INVALID_CHANNEL_ID 0x02; ERR_INVALID_PROTOCOL_ID 0x03; ERR_NULL_PARAMETER 0x04; ERR_INVALID_IOCTL_VALUE 0x05; ERR_INVALID_FLAGS 0x06; ERR_FAILED 0x07; ERR_DEVICE_NOT_CONNECTED 0x08; ERR_TIMEOUT 0x09; ERR_INVALID_MSG 0x0A; ERR_INVALID_TIME_INTERVAL 0x0B; ERR_EXCEEDED_LIMIT 0x0C; ERR_INVALID_MSG_ID 0x0D; ERR_DEVICE_IN_USE 0x0E; ERR_INVALID_IOCTL_ID 0x0F; ERR_BUFFER_EMPTY 0x10; ERR_BUFFER_FULL 0x11; ERR_BUFFER_OVERFLOW 0x12; ERR_PIN_INVALID 0x13; ERR_CHANNEL_IN_USE 0x14; ERR_MSG_PROTOCOL_ID 0x15; ERR_INVALID_FILTER_ID 0x16; ERR_NO_FLOW_CONTROL 0x17; ERR_NOT_UNIQUE 0x18; ERR_INVALID_BAUDRATE 0x19; ERR_INVALID_DEVICE_ID 0x1A. (src: FSH 97–126; DLH; SAE Figure 47) — matches `_ERR_NAMES` in `j2534.py`.
- Tactrix-specific codes seen from the cable: `are 119` = `ERR_OEM_VOLTAGE_TOO_HIGH` (0x77), `are 120` = `ERR_OEM_VOLTAGE_TOO_LOW` (0x78). The cable's `are <n>` carries the J2534 code unchanged; measured map: `are 1` NOT_SUPPORTED (unsupported config parameter), `are 3` INVALID_PROTOCOL_ID (J1850), `are 5` INVALID_IOCTL_VALUE, `are 7` FAILED (malformed command), `are 9` TIMEOUT (transmit with nothing on the bus), `are 10` INVALID_MSG (wrong payload length), `are 12` EXCEEDED_LIMIT (11th filter/periodic), `are 13` INVALID_MSG_ID (no such periodic), `are 19` PIN_INVALID, `are 20` CHANNEL_IN_USE (second `ato` on a protocol), `are 22` INVALID_FILTER_ID (unknown filter id / filter type 0 or 4). (src: OP-PROTO §6)
- Tactrix DLL return-code quirks: a call before `PassThruOpen`/after `PassThruClose` → ERR_INVALID_CHANNEL_ID (2) (spec: ERR_INVALID_DEVICE_ID); unknown Ioctl id → ERR_INVALID_CHANNEL_ID (2) (spec: ERR_INVALID_IOCTL_ID); NULL filter message → ERR_FAILED (7). (src: OP-AB "Return codes")

#### 4. Tactrix OpenPort 2.0 and other J2534 devices

##### 4.1 OpenPort 2.0 specifics
- DLL: `op20pt32.dll`, registered under `HKLM\SOFTWARE\PassThruSupport.04.04\Tactrix Inc. - OpenPort 2.0 J2534 ISO/CAN/VPW/PWM`; "advertises CAN, ISO9141, ISO14230, ISO15765 (J1850 PWM/VPW are listed 0 = unsupported)"; exports the 14 J2534 v04.04 entry points (ordinals 1–14); Themida-packed, "C++/Boost inside"; the shipped kernel driver `openport.sys` ("Microsoft KMDF 1.9 bulk sample … dated 2014") binds `USB\VID_0403&PID_CC4B/CC4C/CC4D` but "is not actually required" because the cable is CDC-ACM. (src: RF-RE §1–§3)
- **[corrected]** Versions: the Tactrix DLL measured by OP-AB is **`op20pt32.dll` 1.02.0.4868**; cable firmware 1.17.4877 (`ari main code version : 1.17.4877`); API string "04.04". The string `firmware=1.17.4877 dll=1.0.0 api=04.04` quoted earlier is the *open Linux driver's* own version report, not Tactrix's. (src: OP-AB "Results"; RF-README smoke test; OP-PROTO §4)
- **[promoted, partial]** `op20pt32.dll` is a **32-bit x86 image**: the unpacked code "is plaintext x86" (RF-RE §3) and the A/B harness that loads it is compiled with `i686-w64-mingw32-gcc` and run under an "x86-64 Wine 11.17 wow64 build" (OP-AB "How the DLL runs without Windows"); Tactrix's download page offers a single "Openport drivers and J2534 DLL for Windows XP/Vista/7/8/10" package and names no 64-bit DLL. (src: RF-RE; OP-AB; TACDL) — whether Tactrix ships *any* 64-bit DLL elsewhere remains REPORTED.
- Protocol channels in firmware: 3 = ISO9141 (K, pin 7), 4 = ISO14230 (K, pin 7), **5 = CAN (pins 6 and 14), 6 = ISO15765 (pins 6 and 14)**, 7/8 = ISO9141/14230 on L (pin 15), 9 = ISO9141_INNO (RS-232 receive on the 2.5 mm jack). J2534 ids 1, 2, 7–10 → `ato0`, `are 3`, ERR_INVALID_PROTOCOL_ID. "The baud rate is not checked" by the cable (`ato5 0 123456 0` is accepted). (src: OP-PROTO §5 table and notes)
- **CAN (5) and ISO15765 (6) can be open at the same time**: "Channels 5, 6 and 3 opened together" and "there is no limit on open channels: 5, 6, 7 and 9 open together". A second open of the same protocol → `are 20` = ERR_CHANNEL_IN_USE (0x14); protocols sharing a line (3/4 on K, 7/8 on L) exclude each other with `are 3`. (src: OP-PROTO §4 line 208, §5 lines 281, 299–302)
- Channel count: Tactrix's own header (`j2534_tactrix.h`) states "Three concurrent channels maximum, each a different protocol" (src: RF-README "Hardware limits", RF-RE §4), while the other project measured four open at once (src: OP-PROTO §5, and its §12 table "Three channels at most | same | 5, 6, 7 and 9 open together"). Either way CAN + ISO15765 together is within the limit.
- Not supported by the cable: SW-CAN, SCI, J1850 PWM/VPW; ISO14230 at 10400 baud only. (src: RF-README; RF-RE §4; OP-README)
- **DLL routing quirk, critical for vagtune's "CAN + ISO15765 on one device" design**: with both a raw CAN and an ISO 15765 channel open, Tactrix's DLL delivers "every channel-5 frame to the ISO 15765 channel, none to the CAN channel" (the open macOS/Linux driver keeps them on the CAN channel: "channel-5 frames stay on the CAN channel"). Also the DLL "picks the firmware channel from the message: CAN on an ISO 15765 channel goes out as `att5`; ISO 15765 on a CAN channel returns `ERR_INVALID_PROTOCOL_ID`". (src: OP-API "Differences from Tactrix's driver"; OP-AB "Routing"; OP-PROTO §7.7 lines 500–504)
- Loopback echoes for ISO15765 transmits are generated on channel 5 and the DLL hands them to the ISO15765 channel with `ProtocolID = CAN` and TX_MSG_TYPE set; order on the DLL: "TxDone first" (the open driver: wire order). (src: OP-PROTO §7.7; OP-AB "Routing")
- DLL crashes the calling process when GET_CONFIG/SET_CONFIG/FAST_INIT receive a NULL input pointer (never pass NULL). (src: OP-API; OP-AB "Crashes")
- The DLL does **not** validate: CAN at 0 baud, an ISO15765 write of 4100 bytes, a 3-byte CAN periodic — all are sent to the cable ("the 4100-byte message is attempted and times out; the malformed periodic repeats"). CAN writes of 0, 3 or 13 bytes and ISO15765 writes of 3 bytes (or 4 with extended addressing) are sent and get `are 10` = ERR_INVALID_MSG from the cable. (src: OP-AB "Requests refused before they reach the cable")
- Periodic messages (PassThruStartPeriodicMsg): `atm<ch> <interval_us> 0 <TxFlags> <len> <seq>` + payload, 10 per channel, scheduled inside the cable; "A running periodic message produces no transmit indication"; "If your process dies, a periodic message keeps transmitting until the next `PassThruOpen`, which resets the cable. The same is true of Tactrix's driver." Periodic ids "keep counting across sessions while the cable is powered". `CLEAR_PERIODIC_MSGS` = one cable command (`atl<ch>`). (src: OP-API "Before you start"; OP-AB "Other commands", "Wire differences", "Results")
- microSD card inserted → cable enumerates as USB mass storage / "may boot into standalone logging mode"; `PassThruOpen` returns 8 (ERR_DEVICE_NOT_CONNECTED) "USB mass storage". Remove the card and re-plug. (src: OP-README troubleshooting; RF-README)
- `PassThruOpen`/`PassThruClose` both reset the cable's state ("no channel, periodic message or pin voltage carries over between sessions"); on the wire the Tactrix DLL opens with `\r\n\r\n`, `ati`, `ata` (close all channels) and closes with `atz` (reset); `CLEAR_RX_BUFFER` "sends nothing; it clears the DLL's own queue". If `ati` gets no reply the DLL sends `tbi\n` three times 300 ms apart and returns ERR_DEVICE_NOT_CONNECTED. (src: OP-API; OP-AB "What Tactrix's DLL sends")
- Programming voltage: the cable can put 5–20 V on a connector pin (READ_PROG_VOLTAGE reads 8, 12, 16 or 17) or short it to ground; the DLL passes requests through unchecked ("Grounding K (`atv 7 -2`) under an open ISO 9141 channel … sent, 0; the channel stops working"); `SetProgrammingVoltage(pin, VOLTAGE_OFF)` is `atv 12 -1`. Never call PassThruSetProgrammingVoltage for VW CAN work. (src: OP-API "Programming voltage"; OP-AB)
- The cable's `atx` command: RF-RE states "`atx` enters the bootloader and the following commands erase/rewrite flash. Never send it." (OP-PROTO lists `atx<ch> <n>` as "unknown; answers `are 7 <n>`"). Never send raw commands to the serial node. (src: RF-RE §4; OP-PROTO §4)
- ABI: J2534 integers are `unsigned long` → 4 bytes on Windows (32-bit DLL), **8 bytes on 64-bit macOS/Linux** with the bisak driver ("The header declares J2534's integers as `unsigned long`, as the standard does, so on 64-bit macOS and Linux they are 8 bytes. Use `ctypes.c_ulong`. A tool that assumes 32-bit integers (`c_uint32`, Rust `u32`) will not work with this library."). Note the roffe driver instead exports "a 32-bit `unsigned long` ABI" (its own `j2534.h`), so `c_ulong` is right for Windows and bisak, but **not** for roffe's `.so` on 64-bit Linux (use `c_uint32` there). `j2534.py` currently uses `c_ulong`. (src: OP-README "From Python"; RF-README "Use")
- Linux/macOS alternatives to the Windows DLL exist and are verified against real ECUs: `bisak/openport-j2534` (GPL-3.0-or-later, libusb, `libj2534.so`/`.dylib`, J2534-1 04.04 all 14 functions, "ISO 15765 … Tested on vehicles and against a live ECU", "Raw CAN. Works.", K-line implemented but unconfirmed; udev rule for 0403:cc4d) and `roffe/libj2534_openport2` (Apache-2.0, cdc_acm `/dev/ttyACM*`, `~/.passthru/openport2.json`, CAN/ISO15765/ISO9141/ISO14230 connect verified, "PassThruReadMsgs ✅ binary RX frames decoded (validated vs Kvaser)", periodic messages and five-baud/fast init "ERR_NOT_SUPPORTED"). (src: OP-README; RF-README)

##### 4.2 Other devices
- **Drew Technologies MongoosePro VW** (product code GMPROVW, $489.95 at the reseller): "J2534 and J2534-1 compliant device driver", "Support for VW/Audi erWin and ODIS software USB Diagnostics tool for CAN and ISO9141/KWP2000", "Supports 2004MY & newer", "Supports Windows 7," (list truncated on the page), bus-powered by USB. J1850 not listed. DLL name not stated on the page. (src: DLVW lines 38–52)
- Drew Tech's registered DLL naming pattern from a real registry dump: `MongoosePro Chrysler` → `C:\Program Files (x86)\Drew Technologies, Inc\J2534\MongoosePro Chrysler\monps432.dll` (CAN, ISO15765, J1850VPW, SCI); `CarDAQ PLUS` → `C:\WINDOWS\system32\CDPLS432.DLL`; `AVIT` → `davit432.DLL`. All under `Program Files (x86)`, i.e. 32-bit DLLs. (src: REGI)
- **VXDIAG VCX NANO**: "a standardized VCI vehicle diagnostic interface designed based on the SAE-J2534 and ISO-22900 PDU international standards", "SAE-J2534-1/2 Pass-Thru with EURO 5", "ISO-22900 MVCI & D-PDU", "J2534 OEM-level ECU reprogramming functionality", "Supports multi-channel simultaneous operation, e.g., 2-wire CAN or K-line simultaneous operation", protocols incl. ISO-9141/14230 K-Line and SAE-J2411 SWCAN; "NOTE : The VXDIAG VCX NANO is limited to supporting software for a single car brand."; "It also supports both third-party and OEM diagnostic software." Whether a generic J2534 DLL usable from third-party code is installed is not stated. (src: VCX lines 19–53)
- **OBDLink MX+ / SX / EX and all STN11xx/STN2xxx** are **not J2534** devices: the MX+ page sells "support of the de facto standard ELM327 command set", "Class 1.5 Bluetooth v3.0", "~100 PIDs/second for PC & Android", and contains no reflashing/programming claim (src: MXP); the SX is a USB 2.0 ELM327-compatible STN device, "~200 PIDs/second", $49.95, "no longer in production. It had been superseded by OBDLink EX", no J2534 or reflash mention (src: SXP); the STN reference manual never mentions J2534 (grep of the full text: zero hits) and describes a UART command interpreter "fully compatible with the de facto industry standard ELM327 command set" (src: FRPM lines 140, 216).

#### 5. python-can hardware for raw 500 kbit/s CAN

- **python-can API**: `Bus.recv(timeout)` → "None on timeout or a Message object"; `Bus.send(msg, timeout)`: "If > 0, wait up to this many seconds for message to be ACK'ed or for transmit queue to be ready depending on driver implementation"; `can.ThreadSafeBus` wrapper for multi-threaded use; `Message.timestamp` float seconds since epoch ("Where possible this will be timestamped in hardware"); `Message.is_rx` (constructor default True) distinguishes echoed TX frames. (src: PC-BUS lines 167, 177, 273–276; PC-MSG lines 66, 118–119, 194)
- **SocketCAN (Linux kernel subsystem)**: `sudo ip link set can0 up type can bitrate 500000`; `SocketcanBus(channel, receive_own_messages=False, local_loopback=True, fd=False, can_filters=None, ignore_rx_error_frames=False)`; "usage of nanosecond timings from the kernel"; serial slcan adapters attach via `slcand` (`slcand -f -o -c -s5 /dev/ttyAMA0`, interfaces named `slcan\d+`). Kernel: `CAN_RAW_LOOPBACK` "/* local loopback (default:on) */", `CAN_RAW_RECV_OWN_MSGS` "/* receive my own msgs (default:off) */" ("The reception of the CAN frames on the same socket that was sending the CAN frame is assumed to be unwanted and therefore disabled by default"); `ip link set canX type can … restart-ms TIME-MS` (RESTART-MS := { 0 | NUMBER }, the doc's example shows `restart-ms 100`) enables automatic bus-off recovery; `ioctl(s, SIOCGSTAMP, &tv)` gives the frame timestamp. (src: PC-SC lines 103–117, 248–273; KERN lines 339, 464–485, 855–880; CANRAW lines 63–64)
- **gs_usb (candleLight / CANable / cantact / Geschwister Schneider)**: `pip install "python-can[gs-usb]"`, "libusb must be installed" (Windows: "a tool such as Zadig can be used to set the USB device driver to libusbK"); "Windows, Linux and Mac."; bitrates "10K, 20K, 50K, 83.333K, 100K, 125K, 250K, 500K, 800K and 1M are supported in this interface, as implemented in the upstream gs_usb package's set_bitrate method"; "Message filtering is not supported in Geschwister Schneider USB/CAN devices and bytewerk.org candleLight USB CAN interfaces" (filter in Python). On Linux the same device is natively a SocketCAN interface via the mainline `gs_usb` module ("works out-of-the-box with linux distros packaging this module, e.g. Ubuntu"); the firmware "also implements WCID USB descriptors and thus can be used on recent Windows versions without installing a driver". Supported boards: candleLight (STM32F072xB, HubertD and linux-automation variants), candleLight FD (STM32G0B1CBT), cantact (STM32F042C6), canable "(cantact clone)" (STM32F042C6), CANable-MKS 1.0 (STM32F072xB), FYSETC UCAN (STM32F072xB), etc.; "STM32G431-based devices (e.g. CANable-MKS 2.0) are not supported by this project yet."; "there is a bug in the gs_usb module in linux<4.5 that can crash the kernel on device removal." (src: PC-GS lines 66–104; CL-FW lines 4–45)
- **slcan (Lawicel ASCII over serial)**: `slcanBus(channel, tty_baudrate=115200, bitrate=None, timing=None, sleep_after_open=2, rtscts=False, listen_only=False, timeout=0.001)`; channel `/dev/ttyUSB0@115200`, `COM4@9600`, `socket://` or `rfc2217://` remote ports; "CAN FD and the BitTimingFd class have partial support according to the non-standard slcan protocol implementation in the CANABLE 2.0 firmware: currently only data rates of 2M and 5M". **[corrected]** The python-can slcan page as fetched contains no "lacks hardware timestamp" / "serial latency" sentences; the no-hardware-timestamp fact is instead established by the driver source: received messages are built with `timestamp=time.time(),  # Better than nothing...` (host clock at parse time). (src: PC-SL lines 66–99; SLPY line 325) — Derived: at 115200 bps one slcan frame line (`t7E88` + 16 hex + `\r` ≈ 21 chars ≈ 1.8 ms) limits throughput to ≈ 550 frames/s, far below a saturated 500 kbit/s bus (≈ 4000 frames/s) but adequate on the near-idle VW diagnostic CAN; prefer candleLight/gs_usb firmware on the same CANable hardware.
- **PCAN-USB**: python-can `pcan` uses PCAN-Basic on Windows (`PcanBus(channel='PCAN_USBBUS1', … bitrate=500000, receive_own_messages=False)`, "Default is 500 kbit/s"; `auto_reset` "Enable automatic recovery in bus off scenario. Resetting the driver takes ~500ms during which" the bus is unresponsive); on Linux use SocketCAN ("Beginning with version 3.4, Linux kernels support the PCAN adapters natively via SocketCAN"). (src: PC-PCAN lines 71–88, 116, 166–167)
- **Kvaser Leaf Light v2**: $463.00; "Kvaser Leaf Light v2 is an End of Life product … suggested replacement products" → Kvaser Leaf v3 $370.00; "8000 messages per second, each time-stamped with 100 microsecond accuracy"; "Supports both 11-bit (CAN 2.0A) and 29-bit (CAN 2.0B active) identifiers"; "High-speed CAN connection (compliant with ISO 11898-2), up to 1 Mbit/s"; "Galvanic isolation … as standard"; "USB 2.0 compliant connector"; Operating System "Windows 7 (IA-32 and x86-64), Windows 8 (IA-32 and x86-64), Windows 10 (IA-32 and x86-64), Windows 11 (x86-64), Linux"; drivers: CANlib (Windows/Linux SDK, "Do not install if using SocketCAN") and "Kvaser SocketCAN Drivers for Linux … Only needed if current kernel version of SocketCAN does not recognize new hardware". **[promoted]** The mainline kernel driver is `CAN_KVASER_USB` ("Kvaser CAN/USB interface"), whose device list includes "Kvaser Leaf Light v2", "Kvaser Leaf Light R v2" and "Kvaser Leaf v3" → `modprobe kvaser_usb`. python-can `kvaser`: `single_handle` ("Use one Kvaser CANLIB bus handle for both reading and writing"), `receive_own_messages` ("Only works if single_handle is also False"), `can_filters` via `set_filters()`, two handles are needed "if receiving and sending messages in different threads". (src: KVL lines 122–137, 162–171, 232–236, 255–290; KVKC lines 67–106; PC-KV lines 69–139)
- **Vector (VN1610 etc.)**: XL Driver Library, "Only Windows is supported", `app_name` from Vector Hardware Config (default `'CANalyzer'`), `rx_queue_size` "CAN: range 16…32768" (default 16384), `poll_interval=0.01`; `flush_tx_buffer()` "will flush the queue and send a high voltage message (ID = 0, DLC = 0, no data)" (do not call on a live bus). (src: PC-VEC lines 66–143)
- SAE J2534-1 §6.5.5 requires every pass-thru device to support raw CAN: "a. 125, 250, and 500 kbps b. 11 and 29 bit identifiers c. Support for 80% ± 2% and 68.5% ± 2% bit sample point d. Allow raw CAN messages. This protocol can be used to handle any custom CAN messaging protocol, including custom flow control mechanisms." and §6.5.6(d): "If the application does not use the ISO 15765-2 transport layer flow control functionality, the CAN protocol will allow for any custom transport layer." → TP 2.0 over a J2534 CAN channel is within the standard's intent. (src: SAE lines 558–577)

#### 6. Why ELM327 / STN (OBDLink) dongles cannot run TP 2.0 or flashing

ELM327 (verified from datasheet and Wikipedia):
- It is "a programmed microcontroller produced for translating the on-board diagnostics (OBD) interface" (originally a PIC18F2480) with a command set "similar to the Hayes AT commands", driven over a UART at 38400 bps by default (9600 "if pin 6 = 0V at power up"); PP 0C sets the RS232 divisor: "The baud rate (in kbps) is given by 4000 ÷ (PP 0C value). For example, 500 kbps requires a setting of 08 (since 4000/8 = 500)" (default 68 = 38.4). Its CAN protocols 6/7 are "ISO 15765-4 CAN (11 bit ID, 500 kbaud)" / 29-bit. (src: W-ELM lines 5–7, 58; ELMDS lines 389, 1461–1463, 3618–3624)
- Raw CAN send: with `AT CAF0` "you must provide all of the required data bytes exactly as they are to be sent – the ELM327 will not perform any formatting for you other than to add some trailing 'padding' bytes to ensure that the required eight data bytes are sent"; sends are limited to "eight data bytes" per command ("long sends (eight data bytes) and long receives (unlimited …)"). The header is set once with `AT SH`. (src: ELMDS lines 622, 782–783)
- Receive: it answers a *request* with whatever arrives until `AT ST`/adaptive timeout; it auto-sends an ISO 15765 FlowControl "in response to a 'First Frame' reply, as long as the CFC setting is on" — there is no API to send a user frame *in reply to a received frame* within a bounded time, which is what a TP 2.0 ACK is. (src: ELMDS line 760)
- Monitoring (`AT MA/MR/MT`) is modal: "the ELM327 remains silent while monitoring, so periodic 'wakeup' messages are not sent …, IFRs are not sent, and the CAN module does not acknowledge messages."; "The monitoring mode can be stopped by putting a logic low level on the RTS pin, or by sending a single RS232 character"; "The IC will always finish a task that is in progress (printing a line, for example) before printing 'STOPPED' and returning to wait for your input, so it is best to wait for the prompt character ('>') to be sent". Hence monitor-then-transmit costs a full stop/prompt/command cycle each time and frames arriving while the host is transmitting are lost. (src: ELMDS lines 2415–2440)
- **[promoted]** `BUFFER FULL`: "The ELM327 provides a 512 byte internal RS232 transmit buffer so that OBD messages can be received quickly, stored, and sent to the computer at a more constant rate. Occasionally (particularly with CAN systems) the buffer will fill at a faster rate than it is being emptied by the PC. Eventually it may become full, and no more data can be stored (it is lost)." Remedies offered: higher baud rate, `AT H0`/`AT S0`, `AT CRA`/`CM`/`CF` filters. (src: ELMDS lines 4869–4885)
- Timestamps: none are provided on any output line (grep of the full datasheet text for "timestamp": zero hits). (src: ELMDS)
- Clones: "ELM327 copies were widely sold in devices claiming to contain an ELM327 device, and problems have been reported with the copies. The problems reflect bugs that were present in ELM's version 1.4 microcode"; "they may falsely report the version number as the current version provided by the genuine ELM327, and in some cases report an as-yet non-existent version … The actual functions of these copies are nonetheless limited to the functions of the original ELM327 v1.4, with their inherent deficiencies." (src: W-ELM lines 64–66)
- PyVCDS, a working Python TP 2.0 stack, states flatly: "THE ELM327 IS NOT SUPPORTED. earlier versions have numerous bugs around raw CAN transport, which includes the clones." and lists "any adapter that works with the aformentioned software (ie: NOT a hex-can or ELM327)". (src: PYV-README lines 22, 27)

OBDLink / STN11xx/STN2xxx (verified from the FRPM):
- "Fully compatible with the ELM327 AT command set", "Feature-rich parallel extended ST command set", "UART baud rates from 38 bps to 10 Mbps", "Large (up to 4KB) data transfers" (note 2: "Only available on specific OBDLink devices. See STPX for details"); non-legislated protocols incl. "ISO 11898 (raw CAN)" (STP 31/32 = "ISO 11898, 11-bit/29-bit Tx, 500kbps, var DLC"; 51/52 125 kbps; 61/62 33.3 kbps). (src: FRPM lines 216–232, 1963–1964, 1982)
- `STPX param1 [, …, paramN]` "Send arbitrary message" / "Transmit arbitrary message on OBD bus": params `h:` header/CAN id, `d:` data or `l:` length (then a `DATA>` prompt), `t:` "Response timeout", `r:` "Expected response count", `x:` extra (ISO 15765 extended address), `f:` flags; example `STPX h:686AF1, d:0100, t:50, r:1`. Max message size by device: OBDLink MX+, OBDLink EX, STN2100, STN2120 = 4k; OBDLink LX, OBDLink MX, OBDLink SX, STN1110, STN1170 = 2k. It is a **request/response** primitive that waits for replies. (src: FRPM lines 1406, 2086–2135)
- `STM [n]` "Monitor OBD bus using current filters", `STMA [n]` "Monitor all messages on OBD bus"; `STCMM mode`: 0 = "Receive only – no CAN ACKs (default)", 1 = "Normal node – with CAN ACKs", 2 = "Receive all frames, including frames with errors – no CAN ACKs." So in the default monitor mode the dongle does not even ACK frames on the bus. (src: FRPM lines 1426, 1442–1443, 2248–2265)
- `STCSEGT 0|1` "Turn CAN Tx segmentation off*/on" (default off); `STCFCPA txadd[ext], rxadd[ext]` flow-control address pairs (e.g. `STCFCPA 7E0 F2, 7E8 A2`); `STCSTM ms` "Set additional time for ISO 15765-2 minimum Separation Time (STmin) … The combined values have a maximum of 127 milliseconds"; `STCTOR fcTimeout, cfTimeout` with defaults `fcTimeout = 75 ms`, `cfTimeout = 150 ms` — the device implements ISO 15765 segmentation itself, but still only inside the request/response model. (src: FRPM lines 1423–1431, 2274–2340)
- "OBDLink ICs support a maximum of three physical CAN channels: High Speed CAN, Medium Speed CAN, and Single Wire CAN. Internally, the OBDLink has only one CAN peripheral that can be mapped to different IC pins under software control. This means that only one CAN channel can be active at a time." (src: FRPM lines 1994–1999)
- No J2534 driver/API exists for them (no mention anywhere in the FRPM, MX+ or SX pages); the MX+ is Bluetooth-only. (src: FRPM; MXP; SXP)

Derived conclusion (from the verified facts above): both families expose an ASCII, prompt-driven, half-duplex command interpreter. TP 2.0 needs (a) a continuously open receive path **and** (b) an unsolicited transmit (the ACK `Bx`) within the ECU's T1 (typically 100 ms) of the last frame of each block, plus keep-alives every ~0.5–1 s, plus our own inter-frame T3 pacing — none of which maps onto "send request, wait for responses, prompt" or onto a monitor mode that must be interrupted to transmit. The STN `STPX`+`STM` pair can be scripted to approximate it, but each monitor→transmit transition costs a prompt cycle and any frame arriving while not monitoring is lost; there is no frame timestamp and no J2534 API. Flashing over UDS/ISO-TP would additionally hit the 2 k/4 k message cap and the lack of BS/STmin control toward the ECU. They remain fine for the OBD-II/J1979 slice only.

#### 7. OBD-II connector pinout and what PQ35 exposes on it

- SAE J1962 Type A pinout (all 16 pins): 1 manufacturer discretion (**"Audi: Switched +12 to tell a scan tool whether the ignition is on." "VW: Switched +12 to tell a scan tool whether the ignition is on."**); 2 J1850 Bus+; 3 manufacturer discretion; 4 **chassis ground**; 5 **signal ground**; 6 **CAN high "(ISO 15765-4 and SAE J2284)"**; 7 **K-line "(ISO 9141-2 and ISO 14230-4)"**; 8 manufacturer discretion; 9 manufacturer discretion; 10 J1850 Bus−; 11 manufacturer discretion; 12 manufacturer discretion; 13 manufacturer discretion; 14 **CAN low "(ISO 15765-4 and SAE J2284)"**; 15 L-line (ISO 9141-2 and ISO 14230-4); 16 **battery voltage "(+12 Volt for type A connector) (+24 Volt for type B connector)"**. Protocol list: "ISO 15765 CAN (250 kbit/s or 500 kbit/s)"; "as of 2008 all vehicles sold in the US are required to implement CAN". (src: W-OBD lines 108–186, 265)
- VW-specific table: pin 1 "IGN – Switched to +12V when the ignition is on", 4 CGND, 5 SGND "Signal ground", 6 CAN High, 7 K-LINE, 14 CAN Low, 15 "ISO 9141-2 L-LINE", 16 +12 V; pins 2/10 (J1850) not used; vehicle table lists "2.0 TDi, Diesel (163HP)" and later 1.9 TDI entries with "CAN 11bit (500kb)" while older entries use K-line protocols on pin 7. (src: PINVW)
- Ross-Tech: "CAN is considerably faster than ISO-9141 (500 kbps vs. 10.4 kbps)"; "With very few exceptions*, all 2008 and newer VW/Audi Group cars require CAN"; "All Golf platform cars (Mk5/Mk6/Mk7) including: 2003+ VW Touran (1T chassis), 2004+ VW Golf/Rabbit/GTI (1K chassis) …" require CAN for diagnostics. (src: RT-CAN lines 44–60)
- VW SSP 269 (2003, the generation just before PQ35): "The drivetrain CAN data bus can be found as a "switched CAN data bus" on the OBD connector. However, the activation procedure is not currently supported by VAS 5051, which means that measurements cannot be conducted via the OBD connector." and "Since the Gateway has access to all of the information via the CAN data bus, this is also used as a diagnosis interface. Interrogation of the diagnosis information is presently done via the COM wire of the Gateway, with introduction of the Touran, a CAN data bus diagnosis wire will be used." Drivetrain CAN 500 kBit/s; convenience/infotainment CAN 100 kBit/s (first convenience CAN was 62.5 kBit/s); "The different data bus systems, drivetrain CAN and convenience/infotainment CAN should only be connected in the vehicle via the Gateway." (src: SSP269 text lines 118–140, 828–834, 872–880, 886–891)
- pq-flasher on a 2010 Golf (PQ35): dumping the EPS via CCP "needs to be done using a direct connection to the EPS, and can't be done through the OBD-II port since there is a gateway that blocks the CCP addresses", so they used a J533 harness — i.e. on PQ35 the OBD port is **not** the raw powertrain bus; the gateway sits between. (src: PQF-README "Dump the existing firmware")
- J533 = "Diagnosis interface for data bus" (SSP 269 key); openpilot's J533 page: "The role of the Gateway (also known J533) is the exchange of data between the CAN databus systems ('powertrain CAN databus,' 'convenience CAN databus' and 'infotainment CAN databus') and the conversion of diagnostic data from CAN databus systems." (src: SSP269 line 918; https://raw.githubusercontent.com/wiki/commaai/openpilot/VW-J533-(Gateway)-Cable.md)

---

### Reported / unverified (confidence)

- **Mk5/Mk6 PQ35 OBD pins 6/14 carry a dedicated "diagnostic CAN" to the J533 gateway at 500 kbit/s, not the powertrain CAN; the gateway proxies TP 2.0 (0x200/0x300/0x7xx) and UDS/ISO-TP (0x7E0/0x7E8 etc.) to the right internal bus.** Confidence: high (SSP 269 says the Touran — first PQ35 car — introduces a "CAN data bus diagnosis wire"; pq-flasher confirms the gateway blocks non-diagnostic traffic on a 2010 Golf; Ross-Tech confirms 500 kbps CAN diagnostics; openpilot's J533 page says the gateway does "the conversion of diagnostic data"). Not verified: the exact term and whether *any* powertrain broadcast frames (0x280 engine, 0x1A0 ABS …) are visible at the OBD port on these two cars. Confirm with `candump can0` on each car (Open Question 5).
- **Tactrix ships no 64-bit `op20pt32` DLL at all.** Confidence: high (the DLL is verified x86-only, see §4.1; the download page lists one package for XP..10 and no 64-bit variant; the earlier project already observed WinError 193 from 64-bit Python). What would confirm: `dumpbin /headers op20pt32.dll` → `machine (x86)` and a directory listing of the Tactrix driver install showing no `*64*.dll`.
- **RF-RE's reading that a Tactrix write with Timeout = 0 "makes the firmware return `ERR_TIMEOUT` immediately without ever putting the frame on the bus".** Confidence: low — **contradicted** by OP-AB's byte tap (the DLL sends `att… 1000000` unnumbered and returns 0; the cable keeps trying for ~1 s). Moved out of VERIFIED. Irrelevant if vagtune always passes a nonzero timeout (it must).
- **Tactrix returns ERR_BUFFER_EMPTY (0x10), not ERR_TIMEOUT (0x09), from an empty `PassThruReadMsgs`.** Confidence: medium (OP-AB: "Every timeout code … in the `errors` scenario" agreed between the spec-conformant open driver and the DLL, implying 0x10; the code is not printed). Keep treating both as "nothing to read". Confirm per Open Question 3.
- **Tactrix delivers the ISO15765 RxStart indication with RxStatus exactly 0x02 (START_OF_MESSAGE only).** Confidence: high (OP-AB: both drivers delivered "the first-frame indication … with the same `RxStatus` and `ExtraDataIndex`", and the open driver sets `ISO15765_FIRST_FRAME` = 0x02 with DataSize 4, ExtraDataIndex 0; the numeric value for the DLL was not printed, unlike TxDone's "RxStatus 9"). Confirm by logging RxStatus in the first live session (Open Question 2).
- **`PassThruReadMsgs(Timeout=1)` on the Tactrix DLL overshoots to ≈ 6–8 ms.** Confidence: medium — derived from the measured ~6 ms polling granularity and 107 ms for `ReadMsgs(100)`, both taken under box64/Wine emulation ("treat its timings as upper bounds"). Confirm per Open Question 3 on native Windows.
- **Pre-3.11 CPython `time.sleep()` on Windows had ≈ 15.6 ms granularity.** Confidence: medium (common knowledge of the Windows default timer tick; not stated in the Python docs, which only say Windows 10+ uses a 100 ns high-resolution timer and that 3.11 switched to a waitable timer). Confirm with a `perf_counter()` loop on the owner's Python.
- **Serial slcan adapters add transmission latency relative to native CAN interfaces.** Confidence: high as a derived fact (ASCII line per frame at 115200 bps ≈ 1.8 ms per frame; the python-can docs page does not state it). Prefer gs_usb/candleLight firmware.
- **CANable 2.0 price ≈ US$ 30–45; candleLight boards ≈ €30–40.** Confidence: medium (canable.io unreachable in both sessions: HTTP 503 / TLS failure). Confirm on canable.io / linux-automation.com.
- **STN `STCMM 1` plus `STM` plus `STPX` cannot interleave within 100 ms reliably over Bluetooth (MX+) because of BT SPP latency (tens of ms, bursty).** Confidence: medium (BT latency is common knowledge, no figure fetched). Irrelevant if the device is excluded for the structural reasons in §6.
- **Drew Tech MongoosePro VW DLL is named on the `monps432.dll` pattern (e.g. `monpv432.dll`/`MongoosePro VW.dll`) under `C:\Program Files (x86)\Drew Technologies, Inc\J2534\MongoosePro VW\`, 32-bit, and supports CAN + ISO15765 channels simultaneously.** Confidence: low (only the Chrysler variant's registry entry and the generic reseller text were fetched; drewtech.com pages 404). Confirm from the registry `PassThruSupport.04.04` enumeration on a PC with the driver installed.
- **VCX NANO installs a brand-specific J2534 DLL (e.g. for GM/Ford) that third-party code can load; the VW/ODIS variant is licensed per brand.** Confidence: low-medium (VCX page: "limited to supporting software for a single car brand"; "supports both third-party and OEM diagnostic software"). Confirm by enumerating `PassThruSupport.04.04` after install.
- **TP 2.0 ECUs on these cars answer the parameters request with T1 = 0x8A (100 ms) and T3 = 0x4A (10 ms) or similar.** Confidence: medium-high for PQ35 modules in general (icanhack's worked example `A1 0F 8A FF 4A FF` is from a 2010 Golf EPS 1K0909144E; jazdw's engine-ECU trace shows the same bytes); unknown per module on the R32 (ME7.1.1, DQ250, Haldex, ABS, …). Always use the ECU's reported T1/T3 and BS (Open Question 4).
- **ISO 15765-2 timing N_As/N_Ar = 1000 ms, N_Bs = 1000 ms, N_Cr = 1000 ms, N_Br/N_Cs implementation-defined (< 1000 ms).** Confidence: high (standard values; can-isotp's defaults of 1000 ms for the FC and CF timeouts are verified; the kernel ISO-TP doc confirms the names N_As/N_Ar but gives no values). Confirm in ISO 15765-2 §9.6 if a copy is available.
- **VW ECUs pad ISO-TP frames with 0xAA (older) or 0x00 and expect padded (DLC 8) requests; the J2534 ISO15765_FRAME_PAD pads with zeroes.** Confidence: high for "expect DLC 8" (OP-API: "many ECUs ignore a frame shorter than 8 bytes", verified; SAE: pad "using zeroes", verified) and for "0xAA is a common pad value" (CSS: "Padding (e.g. 0x00, 0xAA, ...)"; W-PID: ISO 15765-2 suggests 0xCC); the VW-specific pad byte per generation is from memory. Confirm from a trace of VCDS/ODIS on either car (Open Question 7).
- **The roffe driver's 32-bit `unsigned long` ABI on 64-bit Linux means `c_uint32` must be used for it.** Confidence: high (RF-README says "32-bit `unsigned long` ABI"; not tested here). Only matters if that driver is chosen over bisak's.

---


---

## 2. VW TP 2.0 transport (SAE J2819 / "VWTP20")

Source sheet: `tp20.md` (verification pass 2026-10-05). The transport under KWP2000 on every PQ35 module that is not UDS.
Includes the 7-byte channel-setup frame, the 6-byte parameter frame with the T1..T4 timing codec (encoder/decoder given),
the data-frame PCI opcodes, ACK/sequence rules, broadcast frames, ten pitfalls each tied to a source, a byte-level worked
example from a real PQ35 engine trace, and a reconciled reference state machine. Addressing (which logical address a module
answers on) is in §7.3; the application bytes inside the frames are §4 and §7.

### Source key for this layer (verbatim from the sheet)

Sources actually fetched (all facts in VERIFIED cite one of these):

| key | what | URL |
|---|---|---|
| JAZDW | Jared Wiltshire's protocol writeup (the primary open description) | https://jazdw.net/tp20 |
| JAZDW-SRC | Wiltshire's own implementation (VAG Blocks, ELM327/STN based, Qt) | https://raw.githubusercontent.com/jazdw/vag-blocks/master/tp20.cpp , .../tp20.h , .../README.md |
| ICH | I CAN Hack knowledge base chapter 10 | https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/ |
| ICH-BLOG | I CAN Hack blog part 1 (real sniff of a commercial dongle talking to a 2010 Golf Mk6 EPS, part 1K0909144E) | https://icanhack.nl/blog/vw-part1/ |
| PQF | pq-flasher `tp20.py` (comma panda; author flashed a PQ35 EPS with it) | https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/tp20.py , .../kwp2000.py , .../README.md |
| PYVCDS | PyVCDS `vwtp.py` (socketCAN; README: experiments "on an old (2007...) VW") | https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vwtp.py , .../kwp.py , .../README.md |
| TEENSY | seishuku `vwtpkwp2k.c` (Teensy 3.1; the file does not say which ECU it was tested on) | https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c |
| NEFM | NefMoto thread with two real CAN traces (seishuku's unspecified engine ECU; Basano's "1K0907115L ... 2.0l R4/4V TFSI") | http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2 |
| NEFM-GW | NefMoto thread "VW TP2.0 can't connect to CAN Gateway" (Mk5 Jetta, ELM327, J533 answers at 0x1F) | http://nefariousmotorsports.com/forum/index.php?topic=14242.0 |
| K2C | PyPI `kwp2000-can` 0.1.0 sdist (J2534 raw-CAN implementation) `tp20/transport.py`, `frames.py`, `constants.py`, `timing.py` | https://files.pythonhosted.org/packages/49/68/6a5f857bc3c01cc86c803adfeabbda4caf266d97f9595fc41a82c4267c58/kwp2000_can-0.1.0.tar.gz (index: https://pypi.org/project/kwp2000-can/) |
| ESP32LOG | xerootg `vwtp.c` (ESP32 port of stm32-vagcanlogger) | https://raw.githubusercontent.com/xerootg/esp32_tp20_datalogger/master/main/vwtp.c |
| STM32LOG | JacekGreniger `sw/vwtp.c` (the STM32F103 original of ESP32LOG, Elektronika Praktyczna 01/2011 logger) | https://raw.githubusercontent.com/JacekGreniger/stm32-vagcanlogger/master/sw/vwtp.c , .../sw/vwtp.h , .../README.md |
| VWTPLIB | domnulvlad `VWTPLib.h/.cpp` + sketch: a dual-role TP 2.0 library (active = tester, `passive` = module side); the KWP1281→TP2.0 converter runs it in *module* mode so diagnostic software sees a TP 2.0 ECU | https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/VWTPLib.h , .../VWTPLib.cpp , .../KWP1281-VWTP2.0_converter_ESP32.ino , .../vwtp.h |
| NOTYAL | notyal `vwcanread` `include/vwtp20defs.h` (constants transcribed from SAE J2819 FEB2008), `src/vwtp20.cpp`, `src/vwtpchannel.cpp` (unfinished logger) | https://raw.githubusercontent.com/notyal/vwcanread/async-tasksched/include/vwtp20defs.h , .../src/vwtp20.cpp , .../src/vwtpchannel.cpp |
| SPECK | SpeckMobil `tp20.h/.cpp` (2014, Qt/ELM327, "Derived from VAG Blocks") | https://raw.githubusercontent.com/Boromatic/SpeckMobil/master/tp20.h , .../tp20.cpp , .../README.md |
| VDS | michaeldove `vag-diag-sim` `vagvehicle.py` (socketCAN ECU-side simulator used to develop PyVCDS) | https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py |
| SAE | SAE International catalogue page for J2819_201905 (scope text, issue/stabilisation dates; standard body not fetched) | https://saemobilus.sae.org/content/J2819_201905/ |
| J2819 | mystandards.biz catalogue entry for SAE J2819 (abstract only) | https://www.mystandards.biz/standard/sae-j2819-1.5.2019.html |
| SKODA | arXiv 1910.09410 "Cyber-Security Internals of a Skoda Octavia vRS" (real-car TP 2.0 setup to the gateway) | https://arxiv.org/pdf/1910.09410 |
| JAS | jas-hacks blog (i.MX6SX TP2.0/KWP2000 stack) | http://jas-hacks.blogspot.com/2017/01/imx6sx-prototype-vw-vag-vehicle.html |
| NEFM-EDC15 | NefMoto thread on EDC15 "CAN TP" (TP 1.6-like, for contrast) | http://nefariousmotorsports.com/forum/index.php?topic=12567.0 |
| BLAFUSEL | blafusel.de VAG KW 2000 page (K-line; only cites the TP 1.6/2.0 book) | http://www.blafusel.de/obd/vag_kw2000.html |

Not reachable this session (403): forum.autosportlabs.com t=5581 and p=27149, pdfcoffee
"Diagnostics in CANoe" and "J2819 - Base For TP20", Vector AN-IND-1-001 PDF, scribd mirror
of JAZDW, standards.globalspec.com, digital-kaos t-298699, api.github.com. Nothing in
VERIFIED depends on them.

Notation: `TX` = tester → ECU, `RX` = ECU → tester. All CAN IDs 11-bit, 500 kbit/s (see CLAUDE.md).

### Verified (source)

#### 0. Identity of the protocol

- TP 2.0 is a VAG-proprietary transport that opens a point-to-point *channel* between tester and one module; once open, segmented payloads (normally KWP2000) are exchanged. Four frame classes exist: broadcast, channel setup, channel parameters, data transmission. "Volkswagen however uses it's own transport protocol in its vehicles, known as VW TP 2.0 ... Typically the payload of TP 2.0 will be ISO 14230-3, Keyword Protocol 2000 (KWP2000) application layer messages." (src: https://jazdw.net/tp20). JAZDW's own caveat applies to everything derived from it: "I have worked all of this out from various presentations and documents that I have found on the net and from logging data. I have not had any access to the official documentation from VW" (src: https://jazdw.net/tp20); ICH: "There is no official specification of TP 2.0, so the protocol description here is based on reverse engineering work by Jared Wiltshire" (src: https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/).
- It is standardised for J2534 tools as **SAE J2819 "TP2.0 Vehicle Diagnostic Protocol"** (Information Report): "This Technical Information Report defines the diagnostic communication protocol TP2.0. This document should be used in conjunction with SAE J2534-2 in order to fully implement the communication protocol in an SAE J2534 interface. Some Volkswagen of America and Audi of America vehicles are equipped with ECU(s), in which a TP2.0 proprietary diagnostic communication protocol is implemented." Citation line: "SAE Standard J2819_201905, Stabilized May 2019, Issued February 2008"; prior revision J2819_200802. `[corrected: now cited from SAE's own page]` (src: https://saemobilus.sae.org/content/J2819_201905/ ; same abstract at https://www.mystandards.biz/standard/sae-j2819-1.5.2019.html). notyal's header is explicitly "Reference: SAE J2819 FEB2008 / TP2.0 Vehicle Diagnostic Protocol" (src: https://raw.githubusercontent.com/notyal/vwcanread/async-tasksched/include/vwtp20defs.h).
- There is an older, incompatible **TP 1.6** with fixed parameters: "there is an older VW TP 1.6 which was used in some vehicles. TP 1.6 is fairly similar but some of the parameters are fixed." (src: https://jazdw.net/tp20). A real example of the non-2.0 variant on EDC15: setup is a 3-byte frame on **0x214** `01 C0 A1` answered on 0x201 `01 D0 A1` ("0xA1 - offset from 0x700 for channel (means 0x7A1 will be id for comms)"), then params on 0x7A1 `A0 0F 8A FF 32 FF` → "ECU replies on 0x7A1 with it's timing parameters" `A1 01 94 83 82 D4` — note BOTH directions on 0x7A1 and non-0xFF T2/T4 (src: http://nefariousmotorsports.com/forum/index.php?topic=12567.0). Not relevant to PQ35 engines but the autoscan must not mistake it for TP 2.0. The German K-line page only notes that CAN uses "TP 1.6/2.0 - siehe z. B. ISBN 978-3-8348-0447-1" (a textbook; not fetched) (src: http://www.blafusel.de/obd/vag_kw2000.html). `[added]`

#### 1. CAN identifiers

- Channel-setup requests are sent on CAN ID **0x200**; the addressed module answers on **0x200 + logical address** (engine 0x01 → 0x201, EPS 0x09 → 0x209). "The channel setup request message should be sent from CAN ID 0x200 and the response will sent with CAN ID 0x200 + the destination modules logical address" (src: https://jazdw.net/tp20). Trace: `0.339 0x200 09c00010000301` / `0.342 0x209 00d00003a80701` (src: https://icanhack.nl/blog/vw-part1/).
- J2819 wording as transcribed by notyal: "Identifier: Fixed address of the sending (active) ECU. Range between 0x200 through 0x2EF", "Destination: TP-target address of the recipient (lower 8 bits of the ECU's assigned Identifier) Destination < 0xFx" (src: https://raw.githubusercontent.com/notyal/vwcanread/async-tasksched/include/vwtp20defs.h). I.e. every TP 2.0 node owns fixed ID 0x200 + its logical address; the tester is logical 0x00 → 0x200.
- After setup the channel uses two *negotiated* IDs. Testers conventionally ask the module to transmit on **0x300** (PyVCDS allocates 0x300..0x30F round-robin so several modules can be open at once: `self.next = 0x300 ... if addr == 0x310: addr = 0x300` — src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vwtp.py). "You should request the destination module to transmit using CAN ID 0x300 to 0x310 and set the validity nibble for RX ID to invalid. The VW modules seem to respond that you should transmit using CAN ID 0x740." (src: https://jazdw.net/tp20)
- The ID the tester must transmit on is **chosen by the module** and must be read from the 0xD0 response, never assumed: engine (0x01) answered **0x740** in three independent traces (src: https://jazdw.net/tp20 ; http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2 ; comment "Example: 0x201 7 0x00 0xD0 0x00 0x03 0x40 0x07 0x01" in https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c); EPS (0x09) answered **0x7A8** (src: https://icanhack.nl/blog/vw-part1/). The module-side emulator confirms the module picks this value: `VWTPLib diag_VWTP(VWTP_sendFunction, 0, 0x740); // 0x740 is the CAN ID on which VWTP will request to receive from. This ID is normally used by the Engine module, you might need to change it to avoid problems if opening a diagnostic session with the original ECM and with this converter at the same time.` (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/vwtp.h). The vag-diag-sim engine simulator likewise answers `00 d0 00 <rx-hi> 40 07 01` (`MY_CHANNEL_ADDRESS_DOUBLE = 0x740`) (src: https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py). `[added]`
- Raw-CAN receive filters therefore need: 0x200+dest during setup, then the negotiated module-TX ID (0x300..0x30F). ESP32LOG resets the filter before setup (`CAN_ResetFilter0()`) and sets `CAN_SetFilter0(testerId)` (0x300) only after the 0xD0 arrives (src: https://raw.githubusercontent.com/xerootg/esp32_tp20_datalogger/master/main/vwtp.c); identical in the STM32 original (src: https://raw.githubusercontent.com/JacekGreniger/stm32-vagcanlogger/master/sw/vwtp.c).
- **Real-car evidence for non-engine modules on PQ35** `[added]`: on a Mk5 Jetta with an ELM327 the author "was able to successfully communicate with the engine, transmission, ABS modules and some others" via TP 2.0 setup frames; the J533 gateway did NOT answer at 0x19 but a sniffed app "goes to 0x1F address instead", after which readEcuIdentification returned `1K0907530R  0062BJ533  Gateway   H06`; a second poster: "In all VW cars the gateway uses address 0x1F" and "clusters are referred to as module 17-Instruments, while their TP20 address is 07h and their UDS ID is 714h" (src: http://nefariousmotorsports.com/forum/index.php?topic=14242.0). The Skoda paper opened its channel to the gateway with "CAN ID 0x200 with the following data 1f c0 00 10 00 03 01" on a real Octavia vRS and reports "without respecting a specific timing in between commands resulted in a connection drop" (src: https://arxiv.org/pdf/1910.09410).

#### 2. Channel setup frame (7 bytes, opcode 0xC0 / 0xD0 / 0xD6..0xD8)

Request, sent on 0x200:

| byte | value | meaning |
|---|---|---|
| 0 | dest | logical address of target module (0x01 engine, 0x09 EPS, 0x1F gateway, …) |
| 1 | 0xC0 | setup request |
| 2 | RX ID low | bits 0..7 of the CAN ID the *recipient* shall listen on |
| 3 | V·RXpref | high nibble = validity (0 valid, 1 invalid), low nibble = bits 8..10 of RX ID |
| 4 | TX ID low | bits 0..7 of the CAN ID the *recipient* shall transmit on |
| 5 | V·TXpref | high nibble validity, low nibble bits 8..10 |
| 6 | 0x01 | application type (0x01 = diagnostics/KWP) |

(src: https://jazdw.net/tp20 table "Channel setup"; byte-level encoding "a low byte holding the lower 8 bits of the 11-bit CAN ID, and a 'validity + prefix' byte where the high nibble is the validity flag (0x0 = valid, 0x1 = invalid) and the low nibble is the upper nibble of the CAN ID. Read together as a little-endian 16-bit value, this gives V·ID with V in the top nibble." src: https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/ ; notyal struct comment `rx_valid : 4; // RX Valid? 0=Valid, 1=Invalid` src: https://raw.githubusercontent.com/notyal/vwcanread/async-tasksched/include/vwtp20defs.h)

- Canonical request used by every implementation: **`dest C0 00 10 00 03 01`** = "I don't care where you listen (RX invalid, 0x1000), transmit on 0x300 (TX valid), KWP". PQF: `self.can_send(bytes([module]) + b"\xc0\x00\x10\x00\x03\x01", BROADCAST_ADDR)` with comment `RX ID: V = 1 (invalid), 0x1000 / TX ID: 0x300 + V = 0 (valid), 0x0300` (src: https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/tp20.py). Same literal in JAZDW-SRC `writeToElmStr(toHex(dest, 2) + " C0 00 10 00 03 01")`, TEENSY, ESP32LOG/STM32LOG `{0x01, 0xC0, 0x00, 0x10, 0x00, 0x03, 0x01}`, NOTYAL `f.data[3] = 0x1 << 4 | 0x0; f.data[5] = 0x0 << 4 | 0x3`, K2C `rx_id=0x0000 ... rx_valid=True # rx_id is invalid` (K2C's flag naming is inverted but the bytes are the same), SPECK.
- Positive response on 0x200+dest: **`00 D0 rxlo rxhi txlo txhi 01`**. Byte 0 is **0x00**, not the module address: "Destination | 00 | Logical address of the tester (always 0x00)" (src: https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/); TEENSY: "Byte0, TP2.0 module ID (module response is always 0x00?)"; all traces show `00 D0 ...`. The module-side emulator sends `{0x00, 0xD0, ...}` (src: VWTPLIB .ino `static uint8_t dynamic_channel_response[] = {0x00, 0x00, 0x00, 0x03, 0x2E, 0x03, 0x01}` then `dynamic_channel_response[1] = 0xD0; // CHANNEL_OK`); vag-diag-sim sends `[0x00, 0xd0, 0x00, remote_logical_id, 0x40, MY_CHANNEL_ADDRESS, 0x01]` (src: VDS). Byte 6 is echoed ("Application | App | 01 | Echoed." src: ICH).
- Field semantics are always *from the recipient's point of view* (this is the only reading under which request and response are consistent — see OPEN QUESTIONS for the wording confusion in secondary sources). Operationally, every implementation does the same thing with the response:
  - bytes 2–3 → the ID the **tester receives on** (echo of what it asked for, 0x300). TEENSY `_rxID=_RxMsg.Data[2]+(_RxMsg.Data[3]<<8)`; ESP32LOG checks `((msg.payload[3]<<8) | msg.payload[2]) == testerId`; PQF `assert rx == 0x300  # We asked for this`.
  - bytes 4–5 → the ID the **tester transmits on** (0x740 / 0x7A8). TEENSY `_txID=_RxMsg.Data[4]+(_RxMsg.Data[5]<<8)`; ESP32LOG `ecuId = (msg.payload[5]<<8) | msg.payload[4]; //address where you need to send messages to ecu`; PQF `self.tx_addr = tx`; JAZDW-SRC `txID = (setup.txPre << 8) + setup.txID`. (NOTYAL names these the other way round — `ecuID = ...data[2]`, `clientID = ...data[4]` — but then transmits on `clientID`, i.e. the same wiring.)
  - Validity nibbles in the response must both be 0: JAZDW-SRC `if (setup.opcode != 0xD0 || rxID != 0x300 || setup.rxV > 0 || setup.txV > 0) { setChannelClosed(); }`; PYVCDS `assert blob[5] & 0x10 == 0, "ECU gave us an invalid TX address?"`.
  - Example: `201 00 D0 00 03 40 07 01` → tester RX 0x300, tester TX 0x740 (src: https://jazdw.net/tp20). `0x209 00d00003a80701` → tester RX 0x300, TX 0x7A8 (src: https://icanhack.nl/blog/vw-part1/).
- Negative responses (opcode in byte 1; frame is still 7 bytes):
  - **0xD6** = "Application type not supported"
  - **0xD7** = "Application type temporarily not supported"
  - **0xD8** = "Temporarily no resources are free"
  (src: https://raw.githubusercontent.com/notyal/vwcanread/async-tasksched/include/vwtp20defs.h, transcribed from J2819 FEB2008; range 0xD6..0xD8 also in https://jazdw.net/tp20 and https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/). The module-side emulator returns 0xD8 **only when a 0xC0 for the same module arrives while a channel is open AND the requested module-TX ("session") ID differs from the open one**: `if (VWTP_requested_sending_id != VWTP_send_ID) { dynamic_channel_response[1] = 0xD8; // CHANNEL_NO_RESOURCES ... } else { need_to_send_dynamic_channel_response = true; }` i.e. a repeated setup with the *same* RX ID is answered 0xD0 again; comment: "The ID used by most diagnostic software is 300, but sessions with IDs 301, 302, etc. can be opened at the same time, but not for the same module." `[corrected]` (src: VWTPLIB .ino). vag-diag-sim simply ignores a second setup ("I already have an arbitration ID, maybe channel is already setup.") (src: VDS). `[added]`
- Application types (byte 6): **0x01** diagnostics ("SD Diagnostics"), **0x10** infotainment communication, **0x20** application protocol, **0x21** WFS/WIV (immobiliser) (src: https://raw.githubusercontent.com/notyal/vwcanread/async-tasksched/include/vwtp20defs.h). Only 0x01 is relevant to vagtune; PyVCDS notes non-0x01 ("proto != 1") traffic is seen on the internal bus and is framed differently (see REPORTED).
- Timeouts used for the 0xD0 wait: PQF 0.1 s (`timeout: float = 0.1`), PYVCDS 0.3 s (`timeout = .3  #300ms timeout for connect interrogation`; 0.2 s on reconnect), K2C 1.0 s (`timeout: float = 1.0`), ESP32LOG/STM32LOG 1000 ms `CAN_RX_GATEWAY_TIMEOUT //maximum time (ms) for receiving message from gateway` (the extra time is for the gateway to relay). NOTYAL retries the 0xC0 up to 20 times at 50 ms spacing (`delay(50); channelInit(); ... if (++counter > 20)`). PYVCDS retransmits the A0 up to 6 times at 100 ms if no A1 arrives. Reconciled: wait ≥ 300 ms, retry the setup a few times.
- Sequence counters (both directions) are reset to 0 when a channel is set up (JAZDW-SRC `rxSeq = 0; txSeq = 0;` in openChannel; PQF `self.tx_seq = 0; self.rx_seq = 0` after params; VWTPLIB `seq_inbound = seq_outbound = msg_seq_expected = 0` in attemptConnect; VDS resets `kwp_resp_seq = 0` on A8; ESP32LOG `nextSN = 0`).

#### 3. Channel parameters (opcodes 0xA0 / 0xA1 / 0xA3 / 0xA4 / 0xA8)

Frame is 1 byte (A3, A4, A8) or 6 bytes (A0, A1): `op BS T1 T2 T3 T4` (src: https://jazdw.net/tp20 "The channel parameters type has a length of 1 or 6 bytes").

| op | len | meaning | reply |
|---|---|---|---|
| 0xA0 | 6 | parameters request — sent by the tester on its TX ID immediately after 0xD0 | 0xA1 from the module |
| 0xA1 | 6 | parameters response (module's own BS/T1..T4) | none |
| 0xA3 | 1 | channel test / keepalive | 0xA1 (6 bytes) from the peer |
| 0xA4 | 1 | break — "receiver discards all data since last ACK" | none |
| 0xA8 | 1 | disconnect — "channel is no longer open. Receiver should reply with a disconnect" | 0xA8 |

(src: https://jazdw.net/tp20 ; https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/ "0xA3: Channel test (1 byte). The ECU responds with an 0xA1 message. Used to keep the channel alive." "0xA8: Disconnect (1 byte). Closes the channel. Receiver responds with a disconnect."; notyal J2819 names: `CONNSETUP 0xA0`, `CONNACK 0xA1`, `CONNTEST 0xA3`, `BREAK 0xA4`, `DISCONN 0xA8`.)

- Direction: the *tester* sends 0xA0 and the module answers 0xA1 in every trace (`740 A0 0F 8A FF 32 FF` / `300 A1 0F 8A FF 4A FF`, src: https://jazdw.net/tp20 example and NEFM; `0x7a8 a00f8aff0aff` / `0x300 a10f8aff4aff`, ICH-BLOG). Beware JAZDW's *table* text, which says the opposite ("0xA0 Parameters request, used for destination module to initiator"; K2C copied this comment) — the examples and all traces override it. The module-side library answers an incoming 0xA0 with its 0xA1 and treats an 0xA0 arriving *while connected* as "The connection was reinitialized" → terminate (src: VWTPLIB.cpp `_respond`). vag-diag-sim answers 0xA0 with `A1 0F 8A FF 4A FF` (src: VDS).
- **BS** = block size = number of data frames the sender may send before it must stop and wait for an ACK. All testers request **0x0F**; all observed modules answer 0x0F (JAZDW, NEFM, ICH-BLOG, TEENSY). JAZDW-SRC and SPECK reject `param.bs > 0xF`. (On whether 0x0F means 15 or 16 frames see REPORTED/OPEN QUESTIONS; JAZDW-SRC `i % bs == bs-1`, VWTPLIB `(current_frame + 1) % TP_max_block_length == 0` and K2C `block_count >= self._block_size` all put the ACK-requesting 0x0X frame on the **15th** frame, which is safe under either reading.)
- **T1..T4 encoding** (one byte each): bits 7–6 = unit, bits 5–0 = multiplier 0..63; value = unit × multiplier.

  | bits 7–6 | unit |
  |---|---|
  | 00 | 0.1 ms |
  | 01 | 1 ms |
  | 10 | 10 ms |
  | 11 | 100 ms |

  "Bits 7 and 6 encode the time units and the lower six bits encode a multiplier ... For example 0x8A = 10 001010 = 10 ms × 10 = 100 ms." (src: https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/; identical table in https://jazdw.net/tp20 and in K2C `timing.py`: `UNITS_MASK = 0xC0`, `SCALE_MASK = 0x3F`; TEENSY comment "Time Base: 00 = 0.1ms 01 = 1ms 10 = 10ms 11 = 100ms Time: 0..63"; NOTYAL `decodeTimingMs`). Worked values: 0x8A = 100 ms; 0x4A = 1 ms×10 = 10 ms (ICH "ECU bumps the inter-packet gap to 10 ms"); 0x32 = 0.1 ms×50 = 5 ms (TEENSY "set to 5ms"); 0x0A = 0.1 ms×10 = 1 ms (ICH "total 1 ms"; PQF comment); 0xFF = 100 ms×63 = 6300 ms (max encodable, "0-6300ms" in TEENSY comment, K2C "Use maximum value (100ms * 63 = 6300ms) return 0xFF").

  ```python
  def tp20_time_decode(b: int) -> float:      # milliseconds
      return (0.1, 1.0, 10.0, 100.0)[(b >> 6) & 3] * (b & 0x3F)
  def tp20_time_encode(ms: float) -> int:     # smallest-error encoding (K2C timing.py algorithm)
      best = None
      for u, unit in enumerate((0.1, 1.0, 10.0, 100.0)):
          n = round(ms / unit)
          if 0 <= n <= 63:
              err = abs(ms - n * unit)
              if best is None or err < best[0]:
                  best = (err, (u << 6) | n)
      return 0xFF if best is None else best[1]
  ```
  (K2C's own docstring examples are wrong — `decode(0x8A)` is documented as 10.0 and `parse(0x8A)` as `MS_1` — but its code returns 100.0; do not copy the docstrings.) `[added]`
- **Meaning of T1..T4**: T1 = "time to wait for ACK. T1 should be greater than 4*T3"; T2 = "always 0xFF"; T3 = "interval between two packets"; T4 = "always 0xFF" (src: https://jazdw.net/tp20). TEENSY comments: "T1 (tx message timeout) 0-6300ms, set to 100ms", "T3 (minimum time for tx packets) 0-6300ms, set to 5ms". ICH: T3 is the "Interval between packets requested by the tester", the ECU's T3 "bumps the inter-packet gap to 10 ms".
- **Typical tester requests** (all verified in source/traces): `A0 0F 8A FF 32 FF` (T3 = 5 ms; JAZDW example, TEENSY, ESP32LOG/STM32LOG, NEFM trace, K2C default `t3: int = 0x32`, NOTYAL), `A0 0F 8A FF 0A FF` (T3 = 1 ms; PQF, PYVCDS, ICH-BLOG commercial dongle), `A0 0F 8A FF 4A FF` (T3 = 10 ms; JAZDW-SRC, VWTPLIB). **Typical module response**: `A1 0F 8A FF 4A FF` (BS 15, T1 100 ms, T3 10 ms) in every trace from engine (two different engine ECUs in NEFM, JAZDW's) and EPS modules (src: JAZDW, NEFM, ICH-BLOG, TEENSY comment); both ECU simulators hard-code the same reply (VDS, VWTPLIB `VWTP_PROVIDE_PARAMETERS`).
- Observed consequences of T3: in ICH-BLOG the EPS answered T3 = 0x4A (10 ms) and its consecutive frames are timestamped exactly 10 ms apart (`0.662, 0.672, 0.682 ... 0.732`). In NEFM (Basano's engine) the module also answered 0x4A but its frames are ~6 ms apart (`254, 261, 267, 272, 278, 284, 290, 296` ms). So a module's own T3 is not a strict statement about its own spacing; treat the peer's T3 as **the minimum gap you must leave between your own consecutive frames** (VWTPLIB does exactly this: `_message_delay` ← received T3, `_message_timeout` ← received T1; SPECK derives `minimumSendTime = (mintime / 10) + 1` ms from the received T3).
- Implementations' actual inter-frame delay when sending to the ECU: PQF 10 ms (`self.time_between_packets = 0.01`, applied after *every* frame including ACKs), ESP32LOG/STM32LOG 12 ms (`delayT3 = 12; //intermessage delay`), VWTPLIB received T3 (default `VWTP_DELAY 5`), VDS 5.5 ms (`time.sleep(0.0055)` before every send), K2C `time.sleep(self._t3 / 1000.0)` where `_t3` is the *raw byte* from `parse_parameters_response` (0x4A → 74 ms — a bug, see pitfalls).
- A3 keepalive exchange in a real trace: `1033 740 1 A3` → `1034 300 6 A1 F 8A FF 4A FF` (1 ms later) (src: http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2). TEENSY `CAN_VWKWP_ChannelTest()` expects `Data[0]==0xA1` back; ESP32LOG `VWTP_ACK()` requires `len == 6 && payload[0] == 0xA1`; JAZDW-SRC `sendKeepAlive()` requires a 6-byte 0xA1 and refreshes `bs/t1/t3` from it, closing the channel otherwise; SPECK tolerates up to `MNCT 5` consecutive missing A1s before closing.
- The module may itself send 0xA3; the tester must answer with its 0xA1 parameters. VWTPLIB (module side) replies to 0xA3 with `A1 0F 8A FF 4A FF`; VDS (module side) `elif opcode == 0xa3: #keep alive packet` → `[0xa1, 0x0f, 0x8a, 0xff, 0x4a, 0xff]`; NOTYAL replies to an incoming 0xA3 with `A1 0F 8A FF 4A FF`; JAZDW-SRC `checkForCommands()` detects an incoming 0xA3 inside a response stream, answers, restarts its keepalive timer and strips the frame before parsing data. (JAZDW-SRC and SPECK answer with the string "A3", which contradicts the other three and the spec text; PYVCDS does not answer at all — `elif op == 0xA3: pass #FIXME`. Answer with A1.)
- Keepalive intervals used by testers: JAZDW-SRC `keepAliveTimer.setInterval(500)` ms, SPECK `T_CTa 600 //Connection Test Timeout in ms` (and any data write restarts the timer: "write data is equivalent to keep alive"), PYVCDS `time.sleep(.5)` then `_send([0xa3])`, plus KWP `testerPresent` every 1 s (`timeout/2` with timeout 2 s, src: PyVCDS kwp.py). NOTYAL sends A3 whenever nothing has been sent for T1 (100 ms). Reconciled: an idle channel should see an A3 at least every 500 ms (see OPEN QUESTIONS for the true module timeout).
- Disconnect: tester sends `A8` on its TX ID; module replies `A8` on its TX ID. K2C waits up to 0.5 s for `data[0] == 0xA8` on rx id; VWTPLIB waits T1 (`_wait_for_disconnect_response`); PYVCDS waits 0.1 s (`fin.get(timeout=.1)`). JAZDW example ends `740 A8` (src: https://jazdw.net/tp20). If the module sends A8 unsolicited the tester must consider the channel closed and may reply A8 (PYVCDS `self._send([0xa8]) #respond if this was remote-initiated`; VWTPLIB `_on_termination(true, false)`). A module also sends A8 after a protocol violation (see §6 pitfall 1).
- Break 0xA4: PYVCDS sends `A4` after an ACK timeout before retrying the block (`#missed an ACK, send a BRK to flush the buffers`); JAZDW-SRC and SPECK treat an incoming A4 like A8 (`else if (op == 0xA8 || op == 0xA4) { setChannelClosed(); }`). No trace shows A4 in use.

#### 4. Data transmission frames (2..8 bytes)

Byte 0 is the PCI: high nibble opcode, low nibble sequence number 0x0..0xF.

| hi nibble | meaning (sender's statement) | receiver must |
|---|---|---|
| 0x0 | more frames follow **and** I am waiting for an ACK (block size reached) | send ACK, then expect more |
| 0x1 | this is the last frame of the message, waiting for ACK | send ACK; message complete |
| 0x2 | more frames follow, no ACK wanted | nothing |
| 0x3 | last frame, no ACK wanted ("seldom used (usually, FF is used instead of LF)" — VWTPLIB.h) | nothing; message complete |
| 0xB | ACK, ready for next frame | — |
| 0x9 | ACK, **not** ready for next frame | — |

(src: https://jazdw.net/tp20 "Op | 0x0 Waiting for ACK, more packets to follow (i.e. reached max block size value as specified above) | 0x1 Waiting for ACK, this is last packet | 0x2 Not waiting for ACK, more packets to follow | 0x3 Not waiting for ACK, this is last packet | 0xB ACK, ready for next packet | 0x9 ACK, not ready for next packet"; identical in ICH and K2C `constants.py`; VWTPLIB.h names them `PCI_FF 0x1`, `PCI_CF 0x2`, `PCI_LF 0x3`, `PCI_FC 0x0`, `PCI_ACK 0xB`, `PCI_NAK 0x9`, `PCI_CMD 0xA`.)

- Payload capacity: 7 bytes per frame after the PCI byte. "Up to 7 bytes of payload can be sent at a time." (src: https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/)
- **Length prefix**: the first frame of every message carries a 2-byte **big-endian** length of the application message (the KWP bytes only; the two length bytes are not counted), so the first frame carries at most 5 application bytes. "The first 2 bytes of the first packet sent contain the length of the message." (src: https://jazdw.net/tp20); ICH: "Length | Len | 00 02 | Big-endian total payload length (2 bytes). Only present in the first frame of a message." PQF `payload = struct.pack(">H", len(dat)) + dat`; K2C `payload.append((length >> 8) & 0xFF); payload.append(length & 0xFF)`; JAZDW-SRC `tmp.len = data[1] << 8 | data[2]`. Trace: `21 00 30 5A 9B ...` → length 0x0030 = 48 bytes = `5A 9B` + 46 bytes of identification text (NEFM). `21 00 1A 61 01 ...` → 26 bytes (JAZDW).
- JAZDW-SRC (and SPECK, which inherited it) masks the length: `length &= 0x7FFF; // mask off MSB, some modules seem to set this for some reason`.
- **Sequence numbering**: each side keeps its own 4-bit counter that persists across messages for the life of the channel; it increments by one per data frame sent (not per message) and wraps 0xF → 0x0. "both tester and ECU have their own counter that persists between transmissions. The counter is incremented after each data transmission. An ACK does not increment any counter, but is expected to use the counter value of the last data transmission that is being acknowledged plus one." (src: https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/). Trace evidence: tester requests `10..`, `11..`, `12..`, `13..`, `14..`, `15..` across six separate KWP requests (NEFM Basano; ICH-BLOG `10.., 11.., 12..`); ECU reply frames `2C 2D 2E 1F` then next reply starts `20` (wrap) (NEFM).
- **ACK value** = (sequence of the frame being acknowledged + 1) & 0xF, sent as `0xB0 | value`. Trace: ECU frames `21 22 23 14` → tester `B5`; tester frame `18 20` (last, seq 8) → ECU `B9`; ECU frames `2C 2D 2E 1F` (seq F) → tester `B0` (src: http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2); EPS frames `22..28, 19` → `BA` (ICH-BLOG). PQF: `seq = (self.tx_seq + 1) & 0xF; if self.can_recv() != bytes([0xB0 | seq]): raise RuntimeError("Wrong ack received")`; TEENSY `_TxMsg.Data[0]=0xB0+(_RxMsg.Data[0]+1&0x0F)`; ESP32LOG `frameNumber = (msg.payload[0]+1) & 0x0F ... msg.payload[0] = 0xB0 | frameNumber`.
- When an ACK is *required*: after a frame with opcode 0x0 or 0x1 (`if (!(dt.opcode & 0x02)) { // send ACK`, JAZDW-SRC; K2C `if opcode in (DATA_OP_WAIT_ACK_MORE, DATA_OP_WAIT_ACK_LAST): ack`; PYVCDS `if op & 0x20 == 0 and seq == self.seq: self._ack(seq + 1)`). The sender must not transmit the next frame of that message until the ACK arrives (PQF `send()` waits for ACK after the last frame; JAZDW-SRC waits after every `0x0X` block-end frame and after the final `0x1X`; K2C `_wait_for_ack` after both).
- Sender's choice of opcode (reconciled from JAZDW-SRC `sendData`, K2C `_send_segmented`, VWTPLIB `send`):

  ```python
  def tp20_segment(app_msg: bytes, bs: int, seq: int):
      """Yield (pci_byte, chunk). seq is the sender's running 4-bit counter."""
      payload = len(app_msg).to_bytes(2, "big") + app_msg
      chunks = [payload[i:i+7] for i in range(0, len(payload), 7)]
      for i, chunk in enumerate(chunks):
          last = (i == len(chunks) - 1)
          block_end = ((i + 1) % bs == 0)          # JAZDW-SRC: i % bs == bs-1 ; VWTPLIB: (current_frame+1) % bs == 0
          if last:          op = 0x1               # last frame -> always ask for ACK
          elif block_end:   op = 0x0               # block full -> ask for ACK, more follow
          else:             op = 0x2               # plain consecutive frame
          yield (op << 4) | (seq & 0xF), chunk
          seq = (seq + 1) & 0xF
  ```
  After yielding an op 0x0 or 0x1 frame the sender waits ≤ T1 for `0xB0|((seq_of_that_frame+1)&0xF)`. Note that a block counter restarts after each ACK: K2C `if need_ack: block_count = 0`; VWTPLIB counts `FC_frames` per block. (PYVCDS differs: `blksize = buf[0] + 1` and `elif i == self.blksize` — it would send 17 frames before asking for an ACK; untested on hardware for long requests.)
- Receiver assembly (reconciled from PQF `recv`, K2C `recv`, VWTPLIB `_receive`, PYVCDS `_recv`): accumulate `frame[1:]` for every data frame; take the 16-bit length from the first two accumulated bytes; ACK after op 0x0/0x1 with `0xB0 | ((seq+1)&0xF)`; the message is complete when op is 0x1 or 0x3 (and/or `len(buffer) >= length`, which is K2C's completion test). PQF asserts `len(data) == length` and — be aware — ACKs **only** on op 0x1 (`if typ == 0x1: self.send_ack()`), i.e. it would stall on a > 15-frame ECU reply; K2C and PYVCDS ACK on both 0x0 and 0x1. `[corrected]`
- Timing seen on a real engine ECU (NEFM Basano, ms column): request → ECU ACK in 2 ms (246→248); ECU ACK → first response frame 6 ms (248→254); tester's ACK of the last frame 5 ms after it (296→301); module reply frames 6 ms apart; A0→A1 7 ms (24→31). On the EPS (ICH-BLOG): A0→A1 9 ms (0.343→0.352); request→ACK 5 ms (0.407→0.412) and 9 ms (0.643→0.652); ACK→first response frame 10 ms (0.412→0.422, 0.652→0.662); 10 ms spacing. `[corrected: exact timestamps]`
- ACK not ready (0x9X): meaning per JAZDW "ACK, not ready for next packet". Observed handling in code only (no trace in this session): K2C accepts a 0x9X carrying the expected sequence, sleeps 10 ms and keeps waiting for the 0xBX (`if opcode == DATA_OP_ACK_NOT_READY: ... time.sleep(0.01)`); SPECK waits `T_wait 100 //wait for receiver ready in ms` then re-sends (`txSeq --; //debug`) with a commented-out limit `MNTB 5 //Maximum acceptances of receiver not ready`; VWTPLIB on receiving 0x9X sets `_wait_for_nak`, resends **from the sequence carried in the NAK** after `T_WAIT 100 // milliseconds to wait before repeating a not-acknowledged message`, and gives up after 5 consecutive NAKs (`NAK_counter >= 5`) (src: VWTPLIB.h/.cpp). PYVCDS logs "ACK but not ready. this is unhandled, spray and pray!". The two independent "100 ms, 5 tries" choices (SPECK `T_wait`/`MNTB`, VWTPLIB `T_WAIT`/5) suggest a common spec origin (see REPORTED).
- ACK with unexpected sequence: VWTPLIB treats a 0xBX whose low nibble ≠ its next outbound seq as "frame missed" and retransmits from the acknowledged sequence (`if (received_seq != seq_outbound % 16) { show_debug_info(FRAME_MISSED); ack_seq_expected = received_seq; _resend_frame = true; }`). This mirrors what the real engine ECU did in NEFM when the tester ACKed with the wrong value (see §6 pitfall 1).

#### 5. Broadcast frames (opcodes 0x23 / 0x24)

- 7 bytes: `dest 0x23 k1 k2 k3 k4 resp` where k1..k4 are up to 4 KWP bytes and `resp` = 0x00 "response expected" or 0x55/0xAA "no response expected". "The broadcast type has a fixed length of 7 bytes. It is sent 5 times in case of packet loss. Not sure what it is actually used for yet." 0x24 = broadcast response (src: https://jazdw.net/tp20 ; same in https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/ "The broadcast packets have no form of ACK, so they are sent 5 times."; notyal `BCAST_REQ 0x23`, `BCAST_RESP 0x24`; K2C `RESP_REQ_NO_RESPONSE = 0x55`, `RESP_REQ_NO_RESPONSE_ALT = 0xAA`). No implementation fetched uses it; vagtune does not need it.

#### 6. Known pitfalls (each tied to a fetched source)

1. **Wrong ACK sequence ⇒ retransmission then A8.** Real engine-ECU trace (seishuku, Teensy 3.1 and STM32F429, ECU model not stated in the thread) `[corrected: not identifiable as EDC17]`: tester ACKed the 4-frame reply `21 22 23 14` with `B2` instead of `B5`; the ECU re-sent frame `22`, then `14` three times, then sent `A8` and dropped the channel ("Your last ack should be B5h, not B2h" — Basano). Fix confirmed by the original poster: "the tester ack after the last data packet must follow the last sequence (eg. 0x13 last packet, 0xb4 ack). The opposite is also true, tester outgoing data with 0x18 would get an ack of 0xb9." (src: http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2)
2. **Module keepalive fired mid-block.** "If a module's keep-alive timer goes off while it's sending a block, it sends the keep-alive but doesn't continue the block afterwards. The solution is to send an 'acknowledge' message with the last received frame's sequence +1, to tell the module to retransmit from that point." and, if the module believed the block finished, acknowledging the wrong value makes it "start sending an apparently infinite block containing garbage" — VWTPLIB terminates the channel when it sees a second 0x0X (flow-control) frame in one message (`if (FC_counter >= 2) { _on_termination(true, true); ...}`) (src: VWTPLIB.cpp comments in `_receive`). Also JAZDW-SRC strips an inline `A3` and answers it before parsing the rest of the reply.
3. **ECU may emit more than one KWP message after one ACK** (e.g. a second message immediately after the acknowledged one); JAZDW-SRC handles "Got a more than one message" by restarting first-frame parsing (src: JAZDW-SRC `recvData`: `keepGoing = true; firstPacket = true; emit log("Warning: Got a more than one message")`). Receiver must therefore be a stream parser keyed on PCI, not "one message per request".
4. **KWP negative response 0x78 (responsePending) arrives as a complete TP message that must be ACKed**, then the real answer follows as a new message with the ECU's next sequence: ESP32LOG/STM32LOG state `REQUEST_PENDING_RECEIVED_SEND_ACK` is entered when a `0x1X` frame has `msg.len == 6 && payload[3]==0x7F && payload[4]==SID && payload[5]==0x78`; it ACKs with `0xB0 | frameNumber` and returns to `RECEIVE_FIRST_MSG` (src: https://raw.githubusercontent.com/xerootg/esp32_tp20_datalogger/master/main/vwtp.c ; identical in https://raw.githubusercontent.com/JacekGreniger/stm32-vagcanlogger/master/sw/vwtp.c).
5. **Length MSB set by some modules** — mask with 0x7FFF (src: JAZDW-SRC, SPECK).
6. **ELM327/STN clones are not fit for TP 2.0**: "The ELM327 is designed for reading OBD-II PIDs and its raw CAN mode is limited which makes implementing VW TP 2.0 difficult." (src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/README.md); "THE ELM327 IS NOT SUPPORTED. earlier versions have numerous bugs around raw CAN transport, which includes the clones." (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/README.md). JAZDW-SRC had to clamp receive timeouts to 1020 ms in 4 ms steps (`if (msecs > 1020) msecs = 1020; ... // each increment is 4ms ... "AT ST "`) and switch header/DLC display on (`AT H1`, `AT D1`, user protocol `AT PB C0 01` = 500 kbps 11-bit). Use J2534 raw CAN or python-can.
7. **Accurate timing matters**: the tester must answer within the module's T1 (100 ms) and must not send consecutive frames faster than the module's T3 (10 ms observed). "Implementing TP2.0 is a challenge as accurate timings are required to correctly deal with time out and error scenarios in addition to implementing logic to cater for varying ECU behaviours depending on their age." (src: http://jas-hacks.blogspot.com/2017/01/imx6sx-prototype-vw-vag-vehicle.html); "without respecting a specific timing in between commands resulted in a connection drop" (src: https://arxiv.org/pdf/1910.09410).
8. **Bugs in the reference code not to copy**: JAZDW-SRC and SPECK `lenBA.append(len & 0x0F)` (low length byte masked to 4 bits — breaks any request ≥ 16 bytes); PYVCDS `assert blob[0] == dest` (response byte 0 is 0x00, so this would fail on a real car) and `(rx / 256) & 255` (float in Python 3), plus it never answers an incoming A3; K2C sleeps the *raw* T3 byte in ms (0x4A → 74 ms per frame) and hard-codes `DEFAULT_TX_ID = 0x740  # VW modules typically respond with this` as the constructor default; PQF rejects messages > 255 bytes (`if len(dat) > 0xFF: raise ValueError("Packet longer than 255 bytes not supported")`) although the length field is 16-bit, and only ACKs 0x1X frames; TEENSY does not track the ECU's sequence at all ("TO-DO: This probably should track packet sequence") and only ACKs the last frame; ESP32LOG/STM32LOG check consecutive-frame continuity within one reply (`(msg.payload[0] & 0x0F) == frameNumber`) but derive the expected value from whatever first frame arrives, never from the previous message `[corrected]`; NOTYAL extracts the opcode with `>> 8` instead of `>> 4` (never worked for data frames).
9. **Only one channel per module.** The module-side emulator answers 0xD8 to a second 0xC0 for the same module while a channel is open on a *different* RX ID, and re-answers 0xD0 for the same RX ID (src: VWTPLIB .ino). Always send A8 before re-opening, and treat a 0xD8 as "wait and retry / someone else (gateway, another tool) holds the channel".
10. **Module logical address ≠ VCDS address for most modules.** The open-source VCDS-address → TP 2.0-logical-address table (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/vwtp.h, `MODULE_ID_TO_LOGICAL_ID[]`) has identical values only for 01 engine→0x01, 02 transmission→0x02, 03 ABS→0x03; e.g. VCDS 09 central electrics→0x20, 15 airbag→0x05, 17 instruments→0x07, 19 gateway→0x1F, 22 AWD/Haldex→0x0A, 44 steering assist→0x09, 46 comfort→0x21, 56 radio→0x52. Independent real-car confirmation: EPS (VCDS 44) is TP 2.0 dest 0x09 (ICH-BLOG/PQF); gateway (VCDS 19) is 0x1F and instruments (VCDS 17) are 0x07 (NEFM-GW; the same thread's author got "responses from modules it's not supposed to have like AWD (0x22)" — 0x22 is door electronics in the table, i.e. exactly this confusion); a real Octavia addressed the gateway as `1f` (SKODA). The full table is another agent's deliverable; the mechanism fact for this document is: *the byte in the 0xC0 frame is the TP 2.0 logical address, which must come from a lookup table, not from the two-digit VCDS address.*

#### 7. Complete worked example (byte level)

Engine ECU, logical address 0x01, PQ35 Golf (identification string "1K0907115L 0030 ... 2.0l R4/4V TFSI"; the ECU family is not stated in the source — a 2.0 TFSI of that era is normally MED9.1, inferred). Every frame below is taken verbatim from a real trace (src: http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2, Basano's log; times in ms) except the two frames marked `[expected]`, whose content is specified by JAZDW/K2C/VWTPLIB and not present in that log.

```
 t(ms) dir  CAN-ID  DLC  data                      TP 2.0 meaning                                 KWP2000 meaning
   19  TX   0x200   7    01 C0 00 10 00 03 01      setup: dest 01, RX-invalid, TX=0x300, app 01
   21  RX   0x201   7    00 D0 00 03 40 07 01      OK: tester listens 0x300, transmits 0x740
   24  TX   0x740   6    A0 0F 8A FF 32 FF         params: BS 15, T1 100ms, T3 5ms
   31  RX   0x300   6    A1 0F 8A FF 4A FF         module params: BS 15, T1 100ms, T3 10ms
   34  TX   0x740   5    10 00 02 10 89            seq0, last, want ACK; len 2                     startDiagnosticSession 0x89
   37  RX   0x300   1    B1                        ACK (0+1)
   44  RX   0x300   5    10 00 02 50 89            ECU seq0, last, want ACK; len 2                 positive response 0x50 0x89
   46  TX   0x740   1    B1                        ACK (0+1)
  246  TX   0x740   5    11 00 02 1A 9B            seq1, last, want ACK; len 2                     readEcuIdentification 0x9B
  248  RX   0x300   1    B2                        ACK (1+1)
  254  RX   0x300   8    21 00 30 5A 9B 31 4B 30   ECU seq1, more, no ACK; len 0x0030=48           5A 9B "1K0"
  261  RX   0x300   8    22 39 30 37 31 31 35 4C   seq2                                            "907115L"
  267  RX   0x300   8    23 20 20 30 30 33 30 10   seq3                                            "  0030" 0x10
  272  RX   0x300   8    24 00 00 00 00 06 46 22   seq4                                            binary ident bytes
  278  RX   0x300   8    25 04 F5 32 2E 30 6C 20   seq5                                            ... "2.0l "
  284  RX   0x300   8    26 52 34 2F 34 56 20 54   seq6                                            "R4/4V T"
  290  RX   0x300   8    27 46 53 49 20 20 20 20   seq7                                            "FSI    "
  296  RX   0x300   2    18 20                     ECU seq8, LAST, want ACK                        " "   (48 bytes total: 5+6*7+1)
  301  TX   0x740   1    B9                        ACK (8+1)
  501  TX   0x740   7    12 00 04 31 B8 00 00      seq2, last; len 4                               startRoutineByLocalId B8 0000
  503  RX   0x300   1    B3                        ACK
  513  RX   0x300   8    29 00 12 71 B8 01 01 01   ECU seq9, more; len 0x12=18                      71 B8 ...
  519  RX   0x300   8    2A 03 01 02 01 06 01 07   seqA
  525  RX   0x300   7    1B 01 08 01 0D 01 18      seqB, LAST, want ACK
  527  TX   0x740   1    BC                        ACK (B+1)
  729  TX   0x740   5    13 00 02 21 02            seq3, last; len 2                               readDataByLocalId 02
  731  RX   0x300   1    B4                        ACK
  738  RX   0x300   8    2C 00 1A 61 02 01 C8 00   ECU seqC, more; len 26
  744  RX   0x300   8    2D 21 85 85 16 FF 00 19   seqD
  749  RX   0x300   8    2E 00 00 25 00 00 25 04   seqE
  756  RX   0x300   8    1F 1D 25 02 7A 25 00 00   seqF, LAST, want ACK
  758  TX   0x740   1    B0                        ACK (F+1 wraps to 0)
  958  TX   0x740   5    14 00 02 21 71            seq4
  960  RX   0x300   1    B5
  966  RX   0x300   8    20 00 1A 61 71 01 C8 00   ECU seq0 (wrapped)
  972  RX   0x300   8    21 21 85 85 21 FF 13 12
  978  RX   0x300   8    22 7D CA 25 00 00 25 00
  985  RX   0x300   8    13 00 25 00 00 25 00 00   seq3, LAST
  987  TX   0x740   1    B4
 1033  TX   0x740   1    A3                        channel test (keepalive, idle ~45 ms here)
 1034  RX   0x300   6    A1 0F 8A FF 4A FF         module answers with its parameters
 1187  TX   0x740   5    15 00 02 21 73            seq5 ... (continues: 1189 B6, 1195 24.., 1201 25.., 1207 26.., 1213 17.., 1216 B8)
   —   TX   0x740   1    A8                        disconnect                      [expected; src: JAZDW example "740 A8"]
   —   RX   0x300   1    A8                        module confirms                 [expected; src: K2C/VWTPLIB wait for A8]
```

Independent second trace (EPS, dest 0x09, commercial dongle; src: https://icanhack.nl/blog/vw-part1/) shows the identical pattern with different IDs and a 1 ms T3 request: `0x200 09 C0 00 10 00 03 01` → `0x209 00 D0 00 03 A8 07 01` → `0x7A8 A0 0F 8A FF 0A FF` → `0x300 A1 0F 8A FF 4A FF` → `0x7A8 10 00 02 10 89` → `0x300 B1` → `0x300 10 00 02 50 89` → `0x7A8 B1` → (second `11 00 02 10 89` / `B2` / `11 00 02 50 89` / `B2`) → `0x7A8 12 00 02 1A 9B` → `0x300 B3` → `0x300 22 00 30 5A 9B 31 4B 30` … `0x300 19 20` → `0x7A8 BA`. Note the dongle sent startDiagnosticSession 0x89 twice and the EPS answered 0x50 0x89 both times (a repeated session request is harmless). `[added]`

#### 8. Reference tester state machine (implementation form, reconciled)

```python
class Tp20Channel:
    # constants
    SETUP_ID = 0x200
    REQ_PARAMS = bytes([0xA0, 0x0F, 0x8A, 0xFF, 0x4A, 0xFF])   # BS 15, T1 100 ms, T3 10 ms
    T_SETUP   = 0.3     # s to wait for 0xD0 (PYVCDS 0.3, ESP32LOG 1.0)
    T_KEEP    = 0.5     # s idle before sending 0xA3 (JAZDW-SRC 0.5, SPECK 0.6, PYVCDS 0.5)
    T_WAIT    = 0.1     # s to wait after a 0x9X "not ready" before retrying (SPECK T_wait, VWTPLIB T_WAIT)
    MAX_NAK   = 5       # consecutive 0x9X before giving up (SPECK MNTB, VWTPLIB NAK_counter)

    def open(self, dest: int, want_rx: int = 0x300):
        req = bytes([dest, 0xC0, 0x00, 0x10, want_rx & 0xFF, (want_rx >> 8) & 0x0F, 0x01])
        can.send(self.SETUP_ID, req)
        rsp = can.recv(0x200 + dest, timeout=self.T_SETUP)        # retry 0xC0 a few times
        if rsp[1] in (0xD6, 0xD7, 0xD8): raise SetupRefused(rsp[1])
        if rsp[1] != 0xD0 or len(rsp) != 7: raise SetupError(rsp)
        if (rsp[3] & 0x10) or (rsp[5] & 0x10): raise SetupError("invalid id")
        self.rx_id = rsp[2] | ((rsp[3] & 0x0F) << 8)              # expect == want_rx
        self.tx_id = rsp[4] | ((rsp[5] & 0x0F) << 8)              # 0x740 for engine; never assume
        self.tx_seq = self.rx_seq = 0
        can.send(self.tx_id, self.REQ_PARAMS)
        p = can.recv(self.rx_id, timeout=0.1)                     # A1 BS T1 T2 T3 T4
        if p[0] != 0xA1 or len(p) != 6: raise SetupError(p)
        self.bs = p[1]; self.t1 = decode(p[2]) / 1000; self.t3 = decode(p[4]) / 1000

    def send(self, kwp: bytes):
        for pci, chunk in tp20_segment(kwp, self.bs, self.tx_seq):
            can.send(self.tx_id, bytes([pci]) + chunk)
            self.tx_seq = (self.tx_seq + 1) & 0xF
            if (pci >> 4) in (0x0, 0x1):
                self._wait_ack(expected=self.tx_seq)             # 0xB0|tx_seq within T1
            else:
                sleep(self.t3)

    def _wait_ack(self, expected):
        naks = 0
        while True:
            f = self._recv_ctrl(timeout=self.t1)                 # handles A3/A8 inline
            if f[0] == 0xB0 | expected: return
            if f[0] & 0xF0 == 0x90:                              # not ready: wait T_WAIT, keep waiting / retransmit
                naks += 1
                if naks >= self.MAX_NAK: raise AckError(f)
                sleep(self.T_WAIT); continue                     # or retransmit from f[0]&0xF (VWTPLIB)
            raise AckError(f)                                    # wrong seq: retransmit from f[0]&0xF (VWTPLIB)

    def recv(self) -> bytes:
        buf = bytearray(); length = None
        while True:
            f = self._recv_ctrl(timeout=self.t1 if buf else self.t_response)
            op, seq = f[0] >> 4, f[0] & 0xF
            if op > 0x3: raise ProtocolError(f)                   # stray ACK
            self.rx_seq = seq
            buf += f[1:]
            if op in (0x0, 0x1):
                can.send(self.tx_id, bytes([0xB0 | ((seq + 1) & 0xF)]))
            if op in (0x1, 0x3):
                length = int.from_bytes(buf[:2], "big") & 0x7FFF
                msg = bytes(buf[2:2 + length])
                if msg[:1] == b"\x7F" and len(msg) >= 3 and msg[2] == 0x78:   # responsePending
                    buf.clear(); continue                          # real answer follows
                return msg

    def _recv_ctrl(self, timeout):
        """Receive on rx_id; transparently answer A3, raise on A8/A4, drop A1 echoes."""
        while True:
            f = can.recv(self.rx_id, timeout)
            if f[0] == 0xA3: can.send(self.tx_id, bytes([0xA1]) + self.REQ_PARAMS[1:]); continue
            if f[0] == 0xA1 and len(f) == 6: continue             # reply to our keepalive
            if f[0] in (0xA8, 0xA4): self.closed = True; raise ChannelClosed(f[0])
            if f[0] == 0xA0: self.closed = True; raise ChannelClosed(0xA0)   # peer re-initialised
            return f

    def keepalive(self):            # call from a timer when idle >= T_KEEP
        can.send(self.tx_id, b"\xA3")                              # expect A1 within T1

    def close(self):
        can.send(self.tx_id, b"\xA8")
        try: can.recv(self.rx_id, timeout=0.5)                     # expect A8
        finally: self.closed = True
```

---

### Reported / unverified (confidence)

- **Module idle timeout** that actually drops the channel without keepalives: not measured in any fetched source. Confidence that 500 ms A3 spacing is safe: *high* (JAZDW-SRC 500 ms and SPECK 600 ms shipped on ELM327 hardware, PYVCDS 500 ms; NEFM shows a 200 ms request cadence with no A3 at all). The SpeckMobil constant name `T_CTa 600 //Connection Test Timeout in ms` suggests the spec names a connection-test timer; its value is unknown. Confirm on car: open channel, stop all traffic, log the time until the module sends A8 (or stops answering A3).
- **Spec parameter names `T_Wait`, `MNTB`, `T_CT`/`T_CTa`, `MNCT`** (SPECK: "wait for receiver ready in ms" = 100, "Maximum acceptances of receiver not ready" = 5, "Connection Test Timeout in ms" = 600, "Maximum Repeats of connection test" = 5; VWTPLIB independently uses `T_WAIT 100` and 5 NAKs). Confidence *medium* that these mirror J2819/VW-spec parameters with those defaults; the numbers were not seen in a trace. Would be confirmed by the J2819 text (paywalled) or the pdfcoffee "J2819 - Base For TP20" copy (403 this session).
- **KWP-level tester present** is still required in addition to A3 on some modules (session timeout, ISO 14230 S3 ≈ 5 s typical): PyVCDS sends `testerPresent` (0x3E) every ~1 s alongside A3. Confidence *medium*; confirm by holding a channel alive with A3 only for > 10 s and then issuing a request that needs the 0x89 session.
- **T3 direction**: whether the module's A1 T3 is "my minimum gap" or "your minimum gap" is not stated anywhere fetched; evidence is mixed (EPS respected its own 10 ms, engine sent at ~6 ms while advertising 10 ms). Confidence that "use peer's T3 as your own minimum gap" is safe: *high* (VWTPLIB and SPECK do this; PQF uses a fixed 10 ms; ESP32LOG 12 ms). Confirm by sending a 3-frame request at 1 ms spacing and watching for 0x9X/A4/A8.
- **T1 direction**: likewise ambiguous; both sides advertise 0x8A in all traces. Use 100 ms as ACK timeout. Confidence *high*.
- **BS = 15 vs 16**: JAZDW's own prose says "send 16 packets at a time" for 0x0F while ICH says "15 packets between ACKs", K2C says `# 15 packets`, PYVCDS uses `buf[0] + 1 # 0 is "1 frame"`. Confidence *medium* that 0x0F = 15 frames before mandatory ACK. Safe implementation: ACK-request on frame index `bs-1` (every 15th), as JAZDW-SRC, VWTPLIB and K2C do. Confirm with a ≥ 16-frame request (e.g. a 110-byte writeDataByLocalIdentifier / transferData) and observe whether the ECU accepts a 16th consecutive 0x2X frame.
- **Non-KWP application types (0x10/0x20/0x21) carry no 2-byte length prefix**: PYVCDS applies the length only `if proto == 1` and traces "raw" VWTP for `proto != 1`. Confidence *low*; irrelevant for diagnostics.
- **Multiple simultaneous channels** (e.g. engine on 0x300/0x740 and gearbox on 0x301/0x7xx) work: implied by JAZDW ("0x300 to 0x310"), PYVCDS allocator and VWTPLIB comments ("sessions with IDs 301, 302, etc. can be opened at the same time, but not for the same module"). Confidence *medium*. Confirm on car by opening 0x01 and 0x02 together and checking the gearbox's assigned tester-TX ID.
- **Tester-TX ID assignment rule**: whether the module-assigned tester-TX ID follows a formula is unknown; data points: engine 0x01→0x740 (three traces), EPS 0x09→0x7A8 (one trace), and both ECU simulators default a *gateway/other* response to 0x32E (VWTPLIB `{0x00,0x00,0x00,0x03,0x2E,0x03,0x01}`, VDS `controller_ident_handler` for 0x1F → `[0x00,0xd0,0x00,0x03,0x2e,0x03,0x01]`, `MY_ADDRESS = 0x32e`), which hints that a real J533 gateway assigns 0x32E — *medium* for the gateway value, *low* that any formula exists. Always parse the 0xD0.
- **Gateway behaviour on PQ35**: 0x200 setup frames from the OBD port are routed by the J533 gateway to the target module's bus; the gateway does not alter TP 2.0 (PQF README notes the gateway *does* block CCP: "can't be done through the OBD-II port since there is a gateway that blocks the CCP addresses"). The Skoda paper says "the Gateway Module (GM) will only allow specific data requested to flow to the OBD-II port". Confidence *medium*. Confirm by sniffing the powertrain bus directly (J533 harness) while opening a channel from OBD.
- **Gateway installed-module list**: "control unit number and address list is returned by CAN Gateway module as a response to KWP request with an SID of 1A and 9F parameter. So CAN Gateway has a number 19 and address of 1F in that list." (NEFM-GW, single forum post, no bytes shown). Confidence *medium*; a cheap autoscan primer if it works — confirm by sending `1A 9F` to 0x1F and logging the reply.
- **TP 1.6 on PQ35 cars**: none expected on 2008+ modules; EDC15-era only. Confidence *high* that both target cars are TP 2.0 (R32 ME7.1.1) or UDS (CJAA EDC17CP14 engine; other 2012 modules mixed).
- **J2534 specifics** for TP 2.0: SAE J2819 defines TP 2.0 for J2534-2 interfaces, but no fetched open-source J2534 code uses a dedicated protocol ID; K2C does raw CAN (`CAN` protocol, pass filters) — confidence *high* that raw CAN + software TP 2.0 is the practical route with Tactrix OpenPort 2.0 (its J2534 DLL exposes CAN; whether `op20pt32.dll` exposes a TP 2.0 protocol is unknown — *low*). Timing risk: USB round-trip for the ACK must stay < 100 ms; use a dedicated reader thread and send the ACK immediately on the final frame.
- **0xA4 break semantics** ("discard since last ACK") beyond JAZDW's one-line description: *medium*; no trace.
- **D6/D7/D8 strings** come from a header transcribed from J2819 and from an emulator, not from the standard text itself: *high*.
- **TEENSY was tested on an EDC17 (CJA)** `[downgraded]`: the fetched file does not say what ECU it ran against; seishuku's NEFM post only says Teensy 3.1 / STM32F429. Confidence *low*; irrelevant to the byte-level facts, which are confirmed by the traces.
- **Basano's trace ECU is a MED9.1** `[downgraded]`: only the ident string "1K0907115L 0030 ... 2.0l R4/4V TFSI" is in the source. Confidence *medium* (1K0907115L is a 2.0 TFSI Bosch ECU of the Mk5 era).


---

## 3. ISO-TP (ISO 15765-2) and ISO 15765-4 legislated-OBD transport

Assembled from `obd2.md` §1, `j2534_can.md` §3.2, `uds_vag.md` §S and the project's own tested facts. ISO-TP is the
transport under UDS (§5) and OBD-II (§6). The source keys are those of §1 (J2534 sheet) and §6 (OBD sheet).

### Verified (source)

#### 3.1 ISO 15765-4 addressing, DLC/padding, bit rates, initialisation and timing (verbatim from `obd2.md` §1)

- Diagnostic addresses: tester (external test equipment) source address = **0xF1**; functional target "legislated OBD system" = **0x33**; each OBD ECU has a physical address `xx`. (src: ISO4 Table 2: "Functional request Legislated OBD system = 33 hex External test equipment = F1 hex"; "Physical response External test equipment = F1 hex Legislated-OBD ECU = xx hex"; "Physical request Legislated OBD ECU = xx hex External test equipment = F1 hex")
- 11-bit IDs (ISO4 Table 3): **0x7DF** functional request; **0x7E0..0x7E7** physical request to ECU #1..#8; **0x7E8..0x7EF** physical response from ECU #1..#8 (response = request + 8). "While not required for current implementations, it is strongly recommended (and may be required by applicable legislation) that for future implementations the following 11-bit CAN identifier assignments be used: 7E0/7E8 for ECM (engine control module); 7E1/7E9 for TCM (transmission control module)." (src: ISO4 §6.3.2.2, Table 3)
- The physical request ID is **only required for FlowControl frames** in legislated OBD: "the physical request CAN Id shall only be used for physically addressed FlowControl frames sent by the external test equipment" (src: ISO4 §6.3.2.1). OBD data requests go out functionally on 0x7DF. Physically-addressed requests on 0x7E0 do work in practice: ELM example `>AT SH 7E0` / `>01 00` → `7E8 06 41 00 BE 3F B8 13 00`, `>01 05` → `7E8 03 41 05 46 00 00 00 00` (src: ELM p.44).
- Max 8 OBD ECUs per vehicle: "The maximum number of legislated-OBD-related ECUs in a vehicle shall not exceed eight (8). The network layer of the external test equipment shall be capable of receiving segmented data from eight (8) legislated-OBD ECUs in parallel" → keep one ISO-TP reassembly context per response ID. (src: ISO4 §6.4.3)
- 29-bit IDs (ISO4 Table 4/5, normal fixed addressing): `CAN_ID = (0b110 << 26) | (R=0 << 25) | (DP=0 << 24) | PF << 16 | TA << 8 | SA` with PF = **219 dec (0xDB)** functional / **218 dec (0xDA)** physical, i.e. the top byte is 0x18.
  - **0x18DB33F1** functional request; **0x18DAxxF1** physical request to ECU xx; **0x18DAF1xx** physical response from ECU xx. (src: ISO4 Table 5 "18 DB 33 F1 … 18 DA xx F1 Physical request CAN identifier from external test equipment to ECU #xx … 18 DA F1 xx Physical response CAN identifier from ECU #xx to external test equipment"; ISO2 §7.3.3 Table 20 "Normal fixed addressing, N_TAtype = physical: 110 (bin) 0 0 218 (dec) N_TA N_SA" and Table 21 "N_TAtype = functional: … 219 (dec) N_TA N_SA"; CSS: "If the vehicle responds, you will see responses with CAN IDs 0x18DAF100 to 0x18DAF1FF (typically 18DAF110 and 18DAF11E)"; OBDLINK example `STCFCPA 18DA10F1, 18DAF110`)
  - Note: icanhack.nl states the opposite ("ECU listen range 0x18DAF1xx, response 0x18DAxxF1") — that page is wrong; ISO4/ISO2/CSS/OBDLink all agree with the above.
- DLC: "The CAN DLC (data length code) contained in every diagnostic CAN frame shall always be set to eight (8). The unused data bytes of a CAN frame are undefined. Any diagnostic CAN frame with a DLC value less than eight (8) shall be ignored by the receiving entity." (src: ISO4 §7) → always transmit DLC 8 with padding; on receive, ignore the DLC and use the PCI length; drop frames with DLC < 8 when in strict mode.
- Padding value: ISO 15765-2:2004 §7.4.2 "CAN frame data padding": "The DLC is always set to 8. If the N_PDU to be transmitted is shorter than 8 bytes, then the sender has to set the DLC to the maximum value 8 (padding of unused data bytes)" — **no padding value is prescribed** (src: ISO2 §7.4.2). §7.4.3 "CAN frame data optimization" allows DLC < 8 in generic ISO-TP, but ISO4 §7 forbids it for legislated OBD (see above). Wikipedia: "All CAN frames sent using ISO-TP use a data length of 8 bytes (and DLC of 8). It is recommended to pad the unused data bytes with 0xCC" and the request table says "not used (ISO 15765-2 suggests CCh)"; PYUDS: "Unless specified otherwise, the padding value shall be 0xCC, which minimizes bit stuffing and signal distortion" (src: W "CAN (11-bit) bus format"; PYUDS "CAN Frame Data Padding"). ELM327 and OBDLink pad with **0x00** by default: programmable parameter "26 CAN filler byte (used to pad out messages) 00 to FF, default 00" (src: ELM p.? PP table row 26; OBDLINK PP table row 26, identical wording); Wikipedia response table says the unused bytes "may be 00h or 55h". **bri3d/VW_Flash (open-source Simos/DQ250/DQ381 flashing tool) sends with `params = {"tx_padding": 0x55}` and `conn.tpsock.set_opts(txpad=0x55, …)` for both SocketCAN and J2534** (src: VWF lines 36/45) → VW ECUs demonstrably accept 0x55-padded tester frames. → Implementation: pad with a configurable byte (default 0x55 or 0x00), accept anything on receive. (The correction from the first pass: the ELM sentence "response has been padded with 00's as required by the SAE standard for this mode" is about unused DTC slots `0000` in a K-line/J1850 Mode 03 response, **not** CAN frame filler — the CAN filler fact is PP 26.)
- Bit rates: external test equipment shall support **500 kbit/s and 250 kbit/s**; the CAN controller "shall support the protocol specifications CAN 2.0A (standard format) and CAN 2.0B passive (29 bit ID extended format)"; nominal baudrate tolerance of the tester ±0.15 %. (src: ISO4 §8.2/§8.3)
- Initialization sequence (ISO4 §4): with the first bit rate in `baudrateRecord` (default = all baudrates of §8.3, i.e. 250k and 500k; "can be superseded by any other list of baudrates, e.g. single 500 kBit/s"), connect, "transmit a functionally addressed service 01 hex request message (read-supported PIDs) using the legislated-OBD 11 bit functional request CAN identifier"; on a CAN error disconnect and try the next baudrate; start P2CAN; collect every response (SingleFrame or FirstFrame) in 0x7E8..0x7EF (each response ID = one ECU); on P2CAN timeout with no 11-bit response, repeat with 29-bit **0x18DB33F1** and collect 0x18DAF1xx. "Where one or more of the received response messages are negative response messages with response code 21 hex (busyRepeatRequest), the external test equipment shall start the initialization sequence (Connector A) again after a minimum delay of 200 ms. If the negative response(s) appear(s) on six (6) subsequent sequences, the external test equipment will assume that the vehicle is not compliant with ISO 15765-4" (i.e. 5 retries). (src: ISO4 §4.2.1–4.3, Figures 2/3). "Service $01 with PID $00 is defined as the universal 'initialization/keep alive/ping' message for all emissions-related OBD ECUs." (src: ISO5 §7.1.1). "There is no need for any diagnostic service to be sent to the legislated-OBD-related ECU to keep the default [session alive]" (src: ISO4 §6.1).
- Network-layer timing for OBD (ISO4 Table 6): **N_As/N_Ar timeout 25 ms**, **N_Bs timeout 75 ms**, **N_Cr timeout 150 ms**, performance requirements (N_Br + N_Ar) < 25 ms, (N_Cs + N_As) < 50 ms. (These are tighter than the generic ISO 15765-2 1000 ms values.) (src: ISO4 Table 6)
- Tester FlowControl parameters (ISO4 Table 7): **N_WFTmax = 0** ("No FlowControl wait frames are allowed for legislated OBD. The FlowControl frame sent by the external test equipment following the FirstFrame of an ECU response message shall contain the FlowStatus FS set to 0 (ClearToSend)"), **BS = 0** ("A single FlowControl frame shall be transmitted by the external test equipment for the duration of a segmented message transfer. This unique FlowControl frame shall follow the FirstFrame of an ECU response message"), **STmin = 0**. "If a reduced implementation of the ISO 15765-2 network layer is done in a legislated-OBD ECU … any FlowControl frame … using different FlowControl frame parameter values … shall be ignored by the receiving legislated-OBD ECU (treated as an unknown network layer protocol data unit)." → send FC `30 00 00` + padding on the physical request ID (0x7E0+n) after each FirstFrame from 0x7E8+n; never send FC with BS≠0 or STmin≠0 to an OBD ECU. (src: ISO4 Table 7)
- Application timing (ISO5 Table 5): **P2CAN min 0 / max 50 ms** "Time between external test equipment request message and the receipt of all unsegmented response messages and all first frames of segmented response message(s)"; **P2\*CAN 0..5000 ms** "Time between the successful reception of a negative response message with response code $78 and the next response message (positive or negative …)". "A negative response message with NRC 78 hex shall not be used as a response message to a service $01 request" (src: ISO5 §5.2.2.6 Table 5 and §5.2.4.3 "this is not allowed for service $01"). Client behaviour for functional requests: start P2CAN on N_USData.con; "either stops its P2CAN in case it knows the servers to be expected to respond and all servers have responded, or keeps the P2CAN running if the client does not know the servers"; on NRC 78 from server #1 "the client establishes an enhanced P2*CAN timer for observation of further server #1 response(s)" while continuing P2CAN for other servers (src: ISO5 §5.2.4.2/5.2.4.3). → for functional requests, wait the full 50 ms (plus margin) and accept every responder; for 0x78, extend the window to 5 s for that responder only.
- ISO 15765-4 relationship: "The CAN identifier shall always be followed by an eight (8) byte CAN frame data field … Depending on the message type, up to three (3) bytes (FlowControl) are used for the PCI (Protocol Control Information) prior to the Service Identifier (only included in single frame or first frame)". CAN frame = [PCI][SID][data...] in SF/FF; PCI occupies 1 byte (SF/CF), 2 bytes (FF) or 3 bytes (FC). (src: ISO5 §5.3.6/5.3.7, Table 14)
- All OBD request messages are at most 7 bytes (6 PIDs max, or 3×(PID,frame#) for Mode 02, or 1 TID + up to 5 data bytes for Mode 08) so they always fit a single ISO-TP frame; only responses are ever multi-frame. (src: ISO5 Tables 125/127/137/157/173/175/181: "#2 PID#1 … #7 PID#6")


#### 3.2 ISO 15765-2 flow control, Linux ISO-TP socket and python can-isotp parameters (verbatim from `j2534_can.md` §3.2)

- ISO 15765-2 FC frame: byte0 = `0x3F` where F = FlowStatus (0 = ContinueToSend, 1 = Wait, 2 = Overflow/abort), byte1 = BS ("A value of zero allows the remaining frames to be sent without flow control or delay"), byte2 = STmin ("values up to 127 (0x7F) specify the minimum number of milliseconds … values in the range 241 (0xF1) to 249 (0xF9) specify delays increasing from 100 to 900 microseconds"); FF carries "The 12-bit length field … allows up to 4095 bytes of user data"; "Prior versions were limited to a maximum payload size of 4095 bytes" (2016 edition: up to 2^32−1). (src: W-TP lines 71–95)
- python can-isotp defaults for comparison: `rx_flowcontrol_timeout` 1000 ms, `rx_consecutive_frame_timeout` 1000 ms, `blocksize` 8, `stmin` 0, `wftmax` 0, `max_frame_size` 4095. (src: ISOTP-PY parameter table)
- Linux ISO-TP socket (CAN_ISOTP): `frame_txtime` is "frame transmission time (defined as N_As/N_Ar inside the ISO standard)"; options `CAN_ISOTP_TX_PADDING`/`RX_PADDING` with `txpad_content`/`rxpad_content`, `CAN_ISOTP_CHK_PAD_LEN`/`CHK_PAD_DATA`; `wftmax` "maximum number of wait frames provided in flow control frames" and "no support is present for sending 'wait frames'". Errors: `-ETIMEDOUT` rx data timeout, `-ECOMM` flow control reception timeout, `-EMSGSIZE` FC overflow, `-EBADMSG` wrong padding. (src: KISOTP)


#### 3.3 ISO-TP / UDS timing defaults (verbatim from `uds_vag.md` §S)

- S3 server = 5000 ms keepalive window. CONFIRMED (embetronicx, §P).
- ISO 15765-2 defines the flow-control frame (3 PCI bytes), the **block size** ("count of
  frames that may be sent before waiting for the next flow control frame; a value of zero
  [means no further FC]") and **STmin** (separation time). CONFIRMED present (src:
  https://en.wikipedia.org/wiki/ISO_15765-2, re-read). **The numeric default timeouts
  (N_As/N_Bs/N_Cr, P2_client, P2*_client) are NOT on that page** — they remain REPORTED
  below; always prefer the P2/P2* values returned in the 0x10 response (§P).

---


#### 3.4 Project-verified facts carried over from `CLAUDE.md` (already tested in `transport/isotp.py`)

- Project-verified UDS physical IDs on these cars (CLAUDE "Verified protocol facts"): "Bus: 500 kbps, 11-bit IDs. Engine 0x7E0→0x7E8, TCU 0x7E1→0x7E9, Haldex 0x70F→0x779, ABS 0x713→0x77D, gateway 0x710→0x77A. Functional broadcast 0x7DF." (Whether the TCU answers *OBD* services on 0x7E9 is a separate, open question.)

- ISO 15765-4 functional addressing: requests to 0x7DF must fit a single frame; the FC for a multi-frame *response* goes to the responder's **physical** request id (0x7E8 -> 0x7E0; VAG extended range 0x76A..0x77F -> id - 0x6A, e.g. 0x77A -> 0x710); an ECU ignores FC on 0x7DF. `isotp.physical_request_id()` is the table. (src: /home/user/ruggedroute-dataops/vagtune/CLAUDE.md)

- ISO-TP receiver must re-send FC after every `rx_block_size` CFs; `recv(timeout)` bounds the wait for a payload to *start*, each CF then gets its own N_Cr window. (src: CLAUDE.md "Gotchas already paid for")

### Reported / unverified (confidence)

- **Padding byte VW ECUs transmit**: VAG ECUs are widely believed to pad diagnostic frames with **0xAA**. Confidence: **low–medium** (common knowledge from VCDS traces, no document fetched; the open-source VW_Flash tool shows only the *tester* side, 0x55). Confirm from any CAN capture of the car's responses (look at bytes after the PCI length in a `41 00` SF). Tester side: 0x55 is proven acceptable to VW Simos/DSG ECUs by VW_Flash (VERIFIED above); 0x00 and 0xCC are expected to work too but are not demonstrated for these ECUs.
- **No 29-bit OBD on either car**: both are 11-bit, 500 kbit/s, ECM at 0x7E0/0x7E8, TCM (DQ250 "02E" DSG) at 0x7E1/0x7E9 and the DSG does respond to functional 0x7DF Service 01 PID 00 and Mode 03/07 (gearbox DTCs are emissions-relevant). Confidence: **high** for 11-bit/500k and the UDS IDs (CLAUDE.md verified facts match ISO4 recommendations), **medium** for the DSG answering OBD services. A web search found no primary source either way. Confirm: send `7DF 02 01 00` and record all 0x7E8..0x7EF responders.
- **ISO 15765-4:2016 edition** also defines CAN FD / OBDonUDS variants and explicitly lists the padding value as "not specified"; ISO 15765-2:2016 recommends 0xCC. Confidence: **medium** (summarised by W/PYUDS, both of which were fetched and do say 0xCC; the 2016 ISO texts themselves were not fetched).

- **Mk5/Mk6 PQ35 OBD pins 6/14 carry a dedicated "diagnostic CAN" to the J533 gateway at 500 kbit/s, not the powertrain CAN; the gateway proxies TP 2.0 (0x200/0x300/0x7xx) and UDS/ISO-TP (0x7E0/0x7E8 etc.) to the right internal bus.** Confidence: high (SSP 269 says the Touran — first PQ35 car — introduces a "CAN data bus diagnosis wire"; pq-flasher confirms the gateway blocks non-diagnostic traffic on a 2010 Golf; Ross-Tech confirms 500 kbps CAN diagnostics; openpilot's J533 page says the gateway does "the conversion of diagnostic data"). Not verified: the exact term and whether *any* powertrain broadcast frames (0x280 engine, 0x1A0 ABS …) are visible at the OBD port on these two cars. Confirm with `candump can0` on each car (Open Question 5).
- **ISO 15765-2 timing N_As/N_Ar = 1000 ms, N_Bs = 1000 ms, N_Cr = 1000 ms, N_Br/N_Cs implementation-defined (< 1000 ms).** Confidence: high (standard values; can-isotp's defaults of 1000 ms for the FC and CF timeouts are verified; the kernel ISO-TP doc confirms the names N_As/N_Ar but gives no values). Confirm in ISO 15765-2 §9.6 if a copy is available.
- **VW ECUs pad ISO-TP frames with 0xAA (older) or 0x00 and expect padded (DLC 8) requests; the J2534 ISO15765_FRAME_PAD pads with zeroes.** Confidence: high for "expect DLC 8" (OP-API: "many ECUs ignore a frame shorter than 8 bytes", verified; SAE: pad "using zeroes", verified) and for "0xAA is a common pad value" (CSS: "Padding (e.g. 0x00, 0xAA, ...)"; W-PID: ISO 15765-2 suggests 0xCC); the VW-specific pad byte per generation is from memory. Confirm from a trace of VCDS/ODIS on either car (Open Question 7).

- **P2 client ≈ 50 ms, P2\* client ≈ 5000 ms** — medium; standard ISO 14229 client defaults
  but not on any page fetched this session. Always prefer the 0x10-response values.

- **high**: VAG ISO-TP padding is 0x55 on tester frames and 0xAA on ECU frames in the fetched log (one `7E8` line transcribed with 0x55); OpenHaldex-C6 pads its UDS requests with 0xAA. Padding value is not semantically significant.


---

## 4. KWP2000 services (ISO 14230-3) as carried over TP 2.0

Source sheet: `kwp_vag.md` (verification pass 2026-10-05; all 180 formula rows re-checked). This layer holds the ISO-level
parts: message model and pending/busy handling, sessions (`10 89`), tester present, `23`/`2C` memory services and the
complete KWP2000 NRC table. The VAG-specific uses of KWP (`1A` identification options and record layouts, `21` measuring
blocks and the formula table, `18` fault codes and status byte, `31 B8..BB` owner-level functions) are in §7.5, §7.7,
§7.8 and §7.10 — same sheet, same source keys.

### Source key for this layer (verbatim from the sheet)

Sources fetched (short keys used in the text; every bullet still carries the full URL):

| key | what | URL |
|---|---|---|
| ISO | ISO/DIS 14230-3 draft (public PDF, 93 pp.) — service formats, NRC table, timing figures | http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf |
| VB | jazdw/vag-blocks `kwp2000.cpp/.h` (Qt/ELM327 tool, real VAG TP 2.0 cars) | https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp , .../kwp2000.h |
| PY | baconwaifu/PyVCDS `kwp.py`, `vw.py`, `vag-block.py`, `kwp_trace.py`, `blocks.json` (tested on a 2007 VW over socketCAN) | https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py , .../vw.py , .../vag-block.py , .../kwp_trace.py , .../blocks.json |
| PQF | I-CAN-hack/pq-flasher `kwp2000.py` (PQ35 EPS over TP 2.0, comma panda) | https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py |
| TE | seishuku/teensycanbusdisplay `vwtpkwp2k.c` (Teensy, engine ECU over TP 2.0) | https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c |
| DV | domnulvlad KWP1281→VWTP2.0 converter (emulates a TP 2.0/KWP2000 module so VCDS can talk to it; .ino, responses.h, KWP2000_SID.h) | https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP1281-VWTP2.0_converter_ESP32.ino , .../responses.h , .../KWP2000_SID.h |
| KL | domnulvlad/KLineKWP1281Lib `KLineKWP1281Lib.cpp` (KWP1281 K-line library; VAG measuring-value formula table 0x01..0xB5 shared with KWP2000) | https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/main/src/KLineKWP1281Lib.cpp |
| B3 | bri3d/kwp2000 Android logger (`DiagnosticSession.java`, `MeasurementValue.java`, `DiagnosticTroubleCode.java`; VAG KWP2000 over K-line, Porsche Cayenne/VW) | https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java , .../MeasurementValue.java , .../DiagnosticTroubleCode.java |
| VDS | michaeldove/vag-diag-sim `vagvehicle.py` (socketCAN simulator of an Audi 8P MED9.1 engine built from sniffed traces) | https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py |
| SC | vinistoisr/scirocco-dash `board/tp20.py` (CircuitPython, 2009 Scirocco 2.0 TSI, J533 gateway; formulas checked against the car) | https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py |
| SP | adamforbes92/speedPulserPro (`SpeedPulserPro_uds.cpp`; Mk5 DSG over TP 2.0, "Protocol confirmed from VCDS SavvyCAN capture"). [corrected] the `.h` at the same path returns 404, so constants named in the `.cpp` (`KWP_DIAG_MODE_DEV`, `TP20_DSG_MODULE`) are attested only by the `.cpp` comments | https://raw.githubusercontent.com/adamforbes92/speedPulserPro/main/PlatformIO/src/SpeedPulserPro_uds.cpp |
| OH | Forbes-Automotive/OpenHaldex-C6 `src/OpenHaldexC6_UDS.cpp` (Haldex Gen2 1K0 and Gen4 0AY over TP 2.0/KWP; "Confirmed against VCDS-displayed values"). [corrected] the raw file was fetched in full in the verification pass (branch `main`) | https://raw.githubusercontent.com/Forbes-Automotive/OpenHaldex-C6/main/src/OpenHaldexC6_UDS.cpp |
| KCE | eszakivizikigyo/kw1281-can-extension `Kwp2000/Kwp2000CanDialog.cs`, `Cli/Program.cs` (.NET, KWP2000 over TP 2.0) | https://raw.githubusercontent.com/eszakivizikigyo/kw1281-can-extension/master/Kwp2000/Kwp2000CanDialog.cs , .../Cli/Program.cs |
| ME7 | nyetwurk/me7-logger `kwp/kwp.go` (Go, ME7Logger work-alike, K-line) | https://raw.githubusercontent.com/nyetwurk/me7-logger/master/kwp/kwp.go |
| PC | victorwitkamp/PoloCornering `decode_diagnostic_payload.py` (decoder for Carista app traces) | https://raw.githubusercontent.com/victorwitkamp/PoloCornering/main/obd-on-pc/decode_diagnostic_payload.py |
| BLA | blafusel.de "VAG KW 2000 Protokoll" (real `5A 9B` dump of ME7 022 906 032 GK) and "KW 1281" formula table | https://www.blafusel.de/obd/vag_kw2000.html , https://www.blafusel.de/obd/obd2_kw1281.html |
| RT-x | Ross-Tech VCDS tour pages (m-blocks, b-settings, adaptation, recode, login, securityaccess, out_test, dtc_screen, open_screen, autoscan, single_screen) and the "Standardized Measuring Block Groups for Gasoline Engines" tables | https://www.ross-tech.com/vcds/tour/<page>.php , https://www.ross-tech.com/vag-com/m_blocks/ |
| RT-W | Ross-Tech wiki Functions table; 02E DSG page | https://wiki.ross-tech.com/wiki/index.php/Functions , https://wiki.ross-tech.com/wiki/index.php/6-Speed_Direct_Shift_Gearbox_(DSG/02E) |
| NEFM-9182 | real TP 2.0/KWP traces of PQ35 engines: seishuku's first post (Teensy, `21 01`) and Basano's reply (full `10 89` / `1A 9B` / `31 B8 00 00` / `21 02` / `21 71` / `21 73` capture of 1K0907115L). [corrected] fetched and read directly in the verification pass, not only via `tp20.md` | http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2 |
| NEFM-271 / -8652 / -14547 / -19082 / -20104 | nefariousmotorsports threads (ME7 logging services; VAG 0x18 format; 9B layout; Arduino ME7Logger; "KWP2089 security access") | http://nefariousmotorsports.com/forum/index.php?topic=<n>.0;wap2 |
| TDI-440170, TDI-462915, MTD, CADDY | real VCDS Auto-Scans with KWP modules (fault lines + "Fault Status" bytes) | https://forums.tdiclub.com/index.php?threads/got-my-vcds-help-read-my-codes.440170/ , https://forums.tdiclub.com/showthread.php?t=462915 , https://www.myturbodiesel.com/threads/cleaning-up-vcds-error-codes-list-guidance.35158/ , https://caddy2k.com/forum/viewtopic.php?t=46728 |
| TDI-DSG | tdiclub "Measuring block for DSG temp" (Ross-Tech staff answer) | https://forums.tdiclub.com/index.php?threads/measuring-block-for-dsg-temp.318269/ |

### Verified (source)

#### 0. Message model, positive/negative responses, pending/busy handling

- A KWP2000 message over TP 2.0 is just `SID [parameters…]` — no format byte, no addresses, no checksum (those exist only on K-line). "Over CAN, KWP2000 messages are just [service_byte, ...body] without the K-line framing (format byte, addresses, checksum)." (src: https://raw.githubusercontent.com/eszakivizikigyo/kw1281-can-extension/master/Kwp2000/Kwp2000CanDialog.cs). TP 2.0 adds a 2-byte big-endian length in front (see `tp20.md`): TE builds `10|seq, 00, 02, 10, 89` for the 2-byte message `10 89` (src: https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c).
- Positive response SID = request SID + 0x40 ("the response is the same number with bit 0x40 … set", PY; `if service_type + 0x40 != resp_sid: raise InvalidServiceIdError`, PQF). Negative response is `7F <requestSID> <responseCode>` (ISO Table 6.1.2.3 and every other 6.x.2.3 table: byte1 `7F`, byte2 request SID, byte3 responseCode 00-7F KWP2000ResponseCode / 80-FF manufacturerSpecific). (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py ; https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py ; http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf)
- The ISO service-ID table (request → positive response): 10→50 startDiagnosticSession, 14→54 clearDiagnosticInformation, 18→58 readDiagnosticTroubleCodesByStatus, 1A→5A readEcuIdentification, 20→60 stopDiagnosticSession, 21→61 readDataByLocalIdentifier, 23→63 readMemoryByAddress, 2C→6C dynamicallyDefineLocalIdentifier, 31→71 startRoutineByLocalIdentifier, 32→72 stopRoutineByLocalIdentifier, 33→73 requestRoutineResultsByLocalIdentifier, 3B→7B writeDataByLocalIdentifier, 3D→7D writeMemoryByAddress, 3E→7E testerPresent, 80→C0 escCode. (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf Table 4.3). The full SID lists in PY `requests` and PQF `SERVICE_TYPE` agree with it and add 0x11 ecuReset, 0x12 readFreezeFrameData, 0x13 readDiagnosticTroubleCodes, 0x17 readStatusOfDiagnosticTroubleCodes, 0x22 readDataByCommonIdentifier, 0x26 setDataRates, 0x27 securityAccess, 0x2E writeDataByCommonIdentifier, 0x2F/0x30 inputOutputControlByCommon/LocalIdentifier, 0x34–0x3A download/upload/transfer/routine-by-address, 0x82 stopCommunication. (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py ; https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py)
- **responsePending (0x78) loop**: on `7F <SID> 78` the tester keeps waiting for the real answer and must not re-send. PY: `elif resp[2] == 0x78: raise EWAIT` → caught in `request()` and simply `recv()`s again ("recv is blocking, so just immediately keep waiting"). KCE: `if responseBody[0]==service && responseBody[1]==reqCorrectlyRcvdRspPending: continue; // Wait for actual response`. B3: `readBytes()` recurses on `responseBytes[0]==0x7F && responseBytes[2]==0x78`. SC: `if len(resp)>=3 and resp[0]==0x7F and resp[2]==0x78:` keep receiving. ISO 5.3.1.4.1: "The negative response message may be sent once or multiple times … During the period of (a) negative response message(s) the testerPresent service shall be disabled in the client!" and the wait between pending messages is P2* = "P2min to P3max". (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py ; https://raw.githubusercontent.com/eszakivizikigyo/kw1281-can-extension/master/Kwp2000/Kwp2000CanDialog.cs ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf)
- **busy-RepeatRequest (0x21) and routineNotComplete (0x23)** → re-send the same request after a short delay. PY: `if resp[2] == 0x21 or resp[2] == 0x23: raise EAGAIN` → `time.sleep(self.transport.packival)` then the request is repeated. ISO 5.3.1.3: after `routineNotComplete` the client repeats the request and the server answers `busy-RepeatRequest` until it can answer positively ("The client shall send another request … until the server responds with a response code not equal to busy-RepeatRequest"). (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py ; http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf)
- PY maps the other NRCs it handles to exceptions: 0x33 → EPERM (securityAccessDenied), 0x31 → ENOENT (requestOutOfRange, used by PY to mean "no such block/option"), 0x35 → EAUTH, 0x12 → EINVAL, 0x11 → serviceNotSupported. (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py)
- VB receive path: `respCode = data[0]; param = data[1]; data.remove(0,2)`; `0x7F` → log "negative KWP response to <param> command" + reason byte; `0x50` → startDiagHandler; `0x5A` with param 0x91/0x9B/0x9F → short-id / long-id / module-list handlers; `0x61` → blockDataHandler(param = group). (src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp)

#### 1. StartDiagnosticSession 0x10, StopDiagnosticSession 0x20, TesterPresent 0x3E, timing

- Request `10 <diagnosticMode>`, positive response `50 <diagnosticMode>`; ISO defines no mode values ("00-7F reservedByDocument, 80-FF manufacturerSpecific"). Rules: "If a diagnostic session has been requested by the client which is already running the server shall send a positive response message"; "There shall be only one session active at a time"; without any request a default session is active that must support at least stopCommunication and testerPresent. (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §6.1)
- **VAG value 0x89 = standard diagnostic session**: every fetched tool opens with `10 89` and expects `50 89`: VB `startDiag(int param = 0x89)` sends `0x10, param`; PY `k.begin(0x89) #0x89 is diag, 0x85 is PROG`; PQF `SESSION_TYPE.DIAGNOSTIC = 0x89` (also `PROGRAMMING = 0x85`, `ENGINEERING_MODE = 0x86`); TE comment "KWP2000 Parameter 0x89 (manufacturer specific)"; DV `diagnosticMode_standardDiagnosticMode 0x89` and the emulator answers `50 89`; SC "0x89 is the plain VAG diagnostic session. Not required by every ECU; measuring blocks usually work without it."; OH sends `{0x10, 0x89}` to the Haldex; SP sends `{KWP_START_DIAG_SESSION, KWP_DIAG_MODE_DEV}` to the Mk5 DSG and checks `kwpBuf[0] == 0x50 && kwpBuf[1] == KWP_DIAG_MODE_DEV` ([corrected] the constant's value is given only by the `.cpp` comment "mode 0x89 = development/extended", the header is not fetchable); real traces: engine `10 00 02 10 89` → `10 00 02 50 89` (NEFM-9182) and EPS (ICH blog, quoted in `tp20.md`). BLA on K-line: `82 10 F1 10 89 1C` → `82 F1 10 50 89 5C`, the reason VAG's dialect is nicknamed "KWP2089". (src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.h ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py ; https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/responses.h ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; https://raw.githubusercontent.com/adamforbes92/speedPulserPro/main/PlatformIO/src/SpeedPulserPro_uds.cpp ; https://www.blafusel.de/obd/vag_kw2000.html ; http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2)
- Other session values seen in code (not needed for diagnostics, listed for recognition only): 0x85 programming (PQF, PY), 0x86 "engineering mode"/development (PQF; NEFM-19082 shows a K-line `03 10 86 63 FC` request to an ME7 and notes "The speed does change with starting the development session"), 0x81 = ME7's stock/default session in ME7 (`SessionDefault = 0x81 // Programming (0x85) and development (0x86) are not requested`). [added] KCE sends a **two-parameter** `10 84 14` (`StartDiagnosticSession(0x84, 0x14)`, reply checked as `Body[0] == 0x84`) to a VDO instrument cluster before reading its EEPROM — an immobiliser-related use that is out of scope here; listed only so a sniffed `10 84 14` can be recognised. (src: https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py ; http://nefariousmotorsports.com/forum/index.php?topic=19082.0;wap2 ; https://raw.githubusercontent.com/nyetwurk/me7-logger/master/kwp/kwp.go ; https://raw.githubusercontent.com/eszakivizikigyo/kw1281-can-extension/master/Kwp2000/Kwp2000CanDialog.cs ; https://raw.githubusercontent.com/eszakivizikigyo/kw1281-can-extension/master/Cli/Program.cs)
- A Bosch 5.7 ABS/ESP on K-line answered `7F 10 11` (serviceNotSupported) to every startDiagnosticSession value except 0x89 (poster's own test). (src: http://nefariousmotorsports.com/forum/index.php?topic=20104.0;wap2)
- StopDiagnosticSession: request `20`, positive response `60`; "The default session cannot be disabled by a stopDiagnosticSession service"; after it the default timing parameters are active again. No fetched VAG tool sends it; PQF and B3 end a session with `82` (stopCommunication, "0x82 : Log off") instead. (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §6.2 ; https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java)
- TesterPresent: request `3E [responseRequired]` with 01 = yes, 02 = no; positive response `7E`; "If the user optional parameter responseRequired is not included in the testerPresent request message the server shall send a testerPresent positive response." (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §6.4). VAG tools send the bare `3E` and expect `7E`: PY `sess.request("testerPresent")` (packs `3E` with no parameter) every `timeout/2` = 1 s from a thread started by `begin()`; B3 `sendTesterPresent()` sends `{0x3E}`. (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java)
- Timing as implemented: PY waits up to 1 s for each response (`self.recv(1)`, `queue.Empty → ETIME`) and retries busy after `packival`; VB passes per-request receive timeouts to the TP layer, `slowRecvTimeout(40)` for session/ident/misc, `normRecvTimeout(24)` for channel open, `fastRecvTimeout(16)` for block reads, and polls open blocks round-robin with `readBlockTimer.setInterval(500)` ms; SC uses 1.0 s per request, 1.5 s for DTC reads and 3.0 s for clear; TE/SP give 1000 ms for the session reply and SP 300 ms for a block read. (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py ; https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; https://raw.githubusercontent.com/adamforbes92/speedPulserPro/main/PlatformIO/src/SpeedPulserPro_uds.cpp)
- ISO timing names used above: P2 = server response time, P3 = time between end of a response and the next request, P2* (pending) = P2min…P3max; the example "P2max = $F2 (18850 ms)" shows that accessTimingParameter can stretch P2 to tens of seconds; the numeric defaults are in ISO 14230-2 §4.4.1 (not fetched). (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §5.3.1.4)

#### 5. ReadMemoryByAddress 0x23 and DynamicallyDefineLocalIdentifier 0x2C (RAM logging)

- ISO 7.3: request `23 <addrHi> <addrMid> <addrLo> <memorySize> [transmissionMode] [maxResponses]`, positive response `63 <recordValue#1…m> [addrHi addrMid addrLo]` (the trailing address is user-optional). (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §7.3)
- Implementations: B3 `{0x23, addr>>16, addr>>8, addr, bytes}` and returns `resultingBytes[2 : 2+bytes]` (i.e. it skips one byte after `63` — see note); KCE `readMemoryByAddress` sends `addr[2] addr[1] addr[0] count` and returns the whole body after the SID, reading in `maxReadLength: 32` chunks; ME7 `ReadMemory(addr, n)` refuses `n <= 0 || n > 254`, sends `23` + 3 address bytes + n and checks `pay[0] == 0x63` and `len(pay) >= 1+n` (data = `pay[1:1+n]`, i.e. no byte between `63` and the data — B3's `copyOfRange(2, …)` skip is therefore suspect) [added]; Fiat/VAG discussion: "Read memory by address requests takes a three byte memory address and a one byte memory size … The response just includes the read data … you can read a maximum of 254 bytes from one memory range"; "you are required to be in a Development diagnostic session to use ReadMemoryByAddress [on ME7], while DynamicallyDefineLocalIdentifier only requires a Standard diagnostic session"; "if you ask for too much data to be read when the engine is running at a high RPM, the watch dog timer goes off and resets the ECU". ME7Logger's own stack uses `SessionDefault = 0x81` and "development (0x86) [is] not requested" for its stock-handler logging. (src: https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java ; https://raw.githubusercontent.com/eszakivizikigyo/kw1281-can-extension/master/Kwp2000/Kwp2000CanDialog.cs ; https://raw.githubusercontent.com/nyetwurk/me7-logger/master/kwp/kwp.go ; http://nefariousmotorsports.com/forum/index.php?topic=271.0;wap2)
- ISO 7.4 DDLI: request `2C <dynamicallyDefinedLocalIdentifier> ` + repeated definitions; by memory address each definition is `03 <positionInDDLI> <memorySize> <addrHi> <addrMid> <addrLo>` (6 bytes), by local identifier `01 <pos> <size> <recordLocalId> <positionInRecord>`, `04` clears; positive response `6C <ddli>`; afterwards `21 <ddli>` returns `61 <ddli> <data>`. (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §7.4)
- B3 `writeDynamicallyDefinedIdentifier`: ddli = `0xF0 + n` (n ≤ 15), up to 20 records of `03, i, length, addrHi, addrMid, addrLo`; ME7 forum: "Each dynamically defined local identifier can have a max of three entries … Each entry can … read a maximum of 255 bytes … but a KWP2000 message has a maximum of 253 data bytes after the service ID and local identifier in the response"; ME7Logger's Go port builds a `2C` defineByMemoryAddress frame as "the other stock service" but samples with `23`. (src: https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java ; http://nefariousmotorsports.com/forum/index.php?topic=271.0;wap2 ; https://raw.githubusercontent.com/nyetwurk/me7-logger/master/kwp/kwp.go)
- On ME7 "ReadDataByLocalIdentifier and ReadDataByCommonIdentifier don't appear to work … there are no local or common identifier defined, so you can't read anything besides the ECU identification data" (the measuring-block LIDs are the VAG `21 <group>` layer, which that poster did not count). PY's `readDataByCommonIdentifier` 0x22 takes a big-endian 16-bit id and is only used for brute-force mapping. (src: http://nefariousmotorsports.com/forum/index.php?topic=271.0;wap2 ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py)

#### 7. KWP2000 negative response codes (ISO 14230-3 Table 4.4)

| hex | name |
|---|---|
| 10 | generalReject |
| 11 | serviceNotSupported |
| 12 | subFunctionNotSupported-invalidFormat |
| 21 | busy-RepeatRequest |
| 22 | conditionsNotCorrect or requestSequenceError |
| 23 | routineNotComplete |
| 31 | requestOutOfRange |
| 33 | securityAccessDenied |
| 35 | invalidKey |
| 36 | exceedNumberOfAttempts |
| 37 | requiredTimeDelayNotExpired |
| 40 | downloadNotAccepted |
| 41 | improperDownloadType |
| 42 | can'tDownloadToSpecifiedAddress |
| 43 | can'tDownloadNumberOfBytesRequested |
| 50 | uploadNotAccepted |
| 51 | improperUploadType |
| 52 | can'tUploadFromSpecifiedAddress |
| 53 | can'tUploadNumberOfBytesRequested |
| 71 | transferSuspended |
| 72 | transferAborted |
| 74 | illegalAddressInBlockTransfer |
| 75 | illegalByteCountInBlockTransfer |
| 76 | illegalBlockTransferType |
| 77 | blockTransferDataChecksumError |
| 78 | reqCorrectlyRcvd-RspPending (requestCorrectlyReceived-ResponsePending) |
| 79 | incorrectByteCountDuringBlockTransfer |
| 80–FF | manufacturerSpecificCodes |

(src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §4.4). PQF's `_negative_response_codes` and PY's `responses` carry the identical names; PY additionally lists UDS-only codes (0x13, 0x14, 0x24, 0x25, 0x70, 0x73, 0x7E, 0x7F) and 0x80 "serviceNotSupportedInActiveDiagnosticMode" — these are not KWP2000 codes ("KWP2000 has no such thing, it can only ever send 0x11" for a wrong session). (src: https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp.py ; http://nefariousmotorsports.com/forum/index.php?topic=20104.0;wap2)

---

### Reported / unverified (confidence)

- **Session keep-alive need**: whether a VAG TP 2.0 module drops the 0x89 session (not the TP channel) without `3E` is unmeasured; PY sends `3E` every 1 s, VB/SC/SP send none and rely on continuous `21` polling plus TP 2.0 A3 keepalives. Confidence **medium** that A3 alone keeps the channel but `3E` is needed for the session after ~5 s idle (ISO S3 behaviour). Confirm (OPEN QUESTIONS 5).
- **P2 on PQ35 modules**: all fetched tools get engine replies within ~10 ms (NEFM trace: request at 246 ms, ACK 248 ms, first reply frame 254 ms); `7F xx 78` is only expected for routines/clear/security. Confidence **high** for the order of magnitude.


---

## 5. UDS services (ISO 14229-1) as used by VAG modules

Source sheet: `uds_vag.md` (adversarially re-verified; primary sources: Wikipedia UDS, pylessard/python-udsoncan source,
uds.readthedocs.io did/rid pages, bri3d/VW_Flash source, Ross-Tech tour/wiki pages). This layer holds the ISO-level
services: SID table, complete NRC table, `0x19` subfunctions and response layouts, DTC status byte, `0x14`, `0x85`, `0x28`,
`0x2F`, `0x31` and routine-id ranges, `0x10` sessions and P2 timing, `0x11`, `0x3E`. The VAG DID catalogue, workshop-code
layout, 3-byte DTC format and numbering, SecurityAccess/coding notes and the OBD-mirror DIDs are in §7.6, §7.8 and §7.10.

### Verified (source)

#### A. Service IDs (request SID → response SID = SID+0x40)

- Full UDS service table (src: https://en.wikipedia.org/wiki/Unified_Diagnostic_Services,
  re-fetched, table reproduced exactly):
  - 0x10 DiagnosticSessionControl → 0x50
  - 0x11 ECUReset → 0x51
  - 0x14 ClearDiagnosticInformation → 0x54
  - 0x19 ReadDTCInformation → 0x59
  - 0x22 ReadDataByIdentifier → 0x62
  - 0x23 ReadMemoryByAddress → 0x63
  - 0x24 ReadScalingDataByIdentifier → 0x64
  - 0x27 SecurityAccess → 0x67
  - 0x28 CommunicationControl → 0x68
  - 0x29 Authentication → 0x69
  - 0x2A ReadDataByPeriodicIdentifier → 0x6A
  - 0x2C DynamicallyDefineDataIdentifier → 0x6C
  - 0x2E WriteDataByIdentifier → 0x6E
  - 0x2F InputOutputControlByIdentifier → 0x6F
  - 0x31 RoutineControl → 0x71
  - 0x34 RequestDownload → 0x74
  - 0x35 RequestUpload → 0x75
  - 0x36 TransferData → 0x76
  - 0x37 RequestTransferExit → 0x77
  - 0x38 RequestFileTransfer → 0x78
  - 0x3D WriteMemoryByAddress → 0x7D
  - 0x3E TesterPresent → 0x7E
  - **0x83 AccessTimingParameter → 0xC3** (was missing from the prior sheet; present in
    the Wikipedia table — add it)
  - 0x84 SecuredDataTransmission → 0xC4
  - 0x85 ControlDTCSetting(s) → 0xC5 (Wikipedia spells it "ControlDTCSettings"; udsoncan
    and ISO use the singular "ControlDTCSetting")
  - 0x86 ResponseOnEvent → 0xC6
  - 0x87 LinkControl → 0xC7
- Negative response layout: byte0=0x7F, byte1=echoed request SID, byte2=NRC. CONFIRMED
  verbatim (src: Wikipedia UDS — "#1 0x7F Negative Response SID #2 SID … value from
  request message #3 NRC reason for the rejection").
- Suppress positive response: OR 0x80 into the subfunction byte (bit 7 =
  suppressPosRspMsgIndicationBit); the echo of the subfunction in the positive response
  masks off 0x80. **Attribution corrected:** this is NOT stated on the fetched Wikipedia
  page; it is confirmed by udsoncan (Response.py exposes `suppress_positive_response`) and
  by VW_Flash testdata where `3E 00`→`7E 00` is the non-suppressed form (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/Response.py ;
  https://raw.githubusercontent.com/bri3d/VW_Flash/master/lib/constants.py testdata).

#### B. Complete NRC table (0x10..0x94)

Exact names/values re-read from udsoncan ResponseCode.py (src:
https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/ResponseCode.py).
Every value below matched the source line for line this session.

| NRC | Name |
|-----|------|
| 0x10 | GeneralReject |
| 0x11 | ServiceNotSupported |
| 0x12 | SubFunctionNotSupported |
| 0x13 | IncorrectMessageLengthOrInvalidFormat |
| 0x14 | ResponseTooLong |
| 0x21 | BusyRepeatRequest |
| 0x22 | ConditionsNotCorrect |
| 0x24 | RequestSequenceError |
| 0x25 | NoResponseFromSubnetComponent |
| 0x26 | FailurePreventsExecutionOfRequestedAction |
| 0x31 | RequestOutOfRange |
| 0x33 | SecurityAccessDenied |
| 0x34 | AuthenticationRequired |
| 0x35 | InvalidKey |
| 0x36 | ExceedNumberOfAttempts |
| 0x37 | RequiredTimeDelayNotExpired |
| 0x38 | SecureDataTransmissionRequired |
| 0x39 | SecureDataTransmissionNotAllowed |
| 0x3A | SecureDataVerificationFailed |
| 0x50 | CertificateVerificationFailed_InvalidTimePeriod |
| 0x51 | CertificateVerificationFailed_InvalidSignature |
| 0x52 | CertificateVerificationFailed_InvalidChainOfTrust |
| 0x53 | CertificateVerificationFailed_InvalidType |
| 0x54 | CertificateVerificationFailed_InvalidFormat |
| 0x55 | CertificateVerificationFailed_InvalidContent |
| 0x56 | CertificateVerificationFailed_InvalidScope |
| 0x57 | CertificateVerificationFailed_InvalidCertificate (ISO note: revoked cert) |
| 0x58 | OwnershipVerificationFailed |
| 0x59 | ChallengeCalculationFailed |
| 0x5A | SettingAccessRightsFailed |
| 0x5B | SessionKeyCreationDerivationFailed |
| 0x5C | ConfigurationDataUsageFailed |
| 0x5D | DeAuthenticationFailed |
| 0x70 | UploadDownloadNotAccepted |
| 0x71 | TransferDataSuspended |
| 0x72 | GeneralProgrammingFailure |
| 0x73 | WrongBlockSequenceCounter |
| 0x78 | RequestCorrectlyReceived_ResponsePending |
| 0x7E | SubFunctionNotSupportedInActiveSession |
| 0x7F | ServiceNotSupportedInActiveSession |
| 0x81 | RpmTooHigh |
| 0x82 | RpmTooLow |
| 0x83 | EngineIsRunning |
| 0x84 | EngineIsNotRunning |
| 0x85 | EngineRunTimeTooLow |
| 0x86 | TemperatureTooHigh |
| 0x87 | TemperatureTooLow |
| 0x88 | VehicleSpeedTooHigh |
| 0x89 | VehicleSpeedTooLow |
| 0x8A | ThrottlePedalTooHigh |
| 0x8B | ThrottlePedalTooLow |
| 0x8C | TransmissionRangeNotInNeutral |
| 0x8D | TransmissionRangeNotInGear |
| 0x8F | BrakeSwitchNotClosed |
| 0x90 | ShifterLeverNotInPark |
| 0x91 | TorqueConverterClutchLocked |
| 0x92 | VoltageTooHigh |
| 0x93 | VoltageTooLow |
| 0x94 | ResourceTemporarilyNotAvailable |

- udsoncan also defines an alternate naming for the 0x38 range used when
  SecuredDataTransmission is involved (src: same ResponseCode.py): `0x38 GeneralSecurityViolation,
  0x39 SecuredModeRequested, 0x3A InsufficientProtection, 0x3B TerminationWithSignatureRequested,
  0x3C AccessDenied, 0x3D VersionNotSupported, 0x3E SecuredLinkNotSupported,
  0x3F CertificateNotAvailable, 0x40 AuditTrailInformationNotAvailable` (these are the
  0x38+n aliases; do not use alongside the certificate names above for the same bytes —
  context decides). Treat any unlisted code as "reserved/manufacturer-specific" per the
  ranges below.
- Ranges (ISO 14229 general pattern; the named codes above are the ones udsoncan
  enumerates): 0x00 positiveResponse; 0x01-0x0F ISOSAEReserved; 0x15-0x20 reserved;
  0x3B-0x4F reserved; 0x5E-0x6F reserved; 0x74-0x77 reserved; 0x79-0x7D reserved;
  0x80 reserved; 0x95-0xEF reserved; 0xF0-0xFE vehicleManufacturerSpecific; 0xFF reserved.
- The transport layer must special-case **NRC 0x78** (ResponsePending: keep waiting in the
  P2* window) and be ready for **0x14** (ResponseTooLong). CONFIRMED by name in the table.

#### C. ReadDTCInformation 0x19 — subfunctions and response layouts

Subfunction constants re-read from udsoncan services/ReadDTCInformation.py (src:
https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/ReadDTCInformation.py).
All values matched the source this session.

| Sub | Name |
|-----|------|
| 0x01 | reportNumberOfDTCByStatusMask |
| 0x02 | reportDTCByStatusMask |
| 0x03 | reportDTCSnapshotIdentification |
| 0x04 | reportDTCSnapshotRecordByDTCNumber |
| 0x05 | reportDTCSnapshotRecordByRecordNumber |
| 0x06 | reportDTCExtendedDataRecordByDTCNumber |
| 0x07 | reportNumberOfDTCBySeverityMaskRecord |
| 0x08 | reportDTCBySeverityMaskRecord |
| 0x09 | reportSeverityInformationOfDTC |
| 0x0A | reportSupportedDTCs |
| 0x0B | reportFirstTestFailedDTC |
| 0x0C | reportFirstConfirmedDTC |
| 0x0D | reportMostRecentTestFailedDTC |
| 0x0E | reportMostRecentConfirmedDTC |
| 0x0F | reportMirrorMemoryDTCByStatusMask |
| 0x10 | reportMirrorMemoryDTCExtendedDataRecordByDTCNumber |
| 0x11 | reportNumberOfMirrorMemoryDTCByStatusMask |
| 0x12 | reportNumberOfEmissionsRelatedOBDDTCByStatusMask |
| 0x13 | reportEmissionsRelatedOBDDTCByStatusMask |
| 0x14 | reportDTCFaultDetectionCounter |
| 0x15 | reportDTCWithPermanentStatus |
| 0x16 | reportDTCExtDataRecordByRecordNumber |
| 0x17 | reportUserDefMemoryDTCByStatusMask |
| 0x18 | reportUserDefMemoryDTCSnapshotRecordByDTCNumber |
| 0x19 | reportUserDefMemoryDTCExtDataRecordByDTCNumber |
| 0x1A | reportSupportedDTCExtDataRecord (added; defined in source, marked `# todo`) |
| 0x42 | reportWWHOBDDTCByMaskRecord |
| 0x55 | reportWWHOBDDTCWithPermanentStatus |
| 0x56 | reportDTCInformationByDTCReadinessGroupIdentifier (added; defined in source, `# todo`) |

Response layouts (src: same file; the parser logic was re-read this session and the byte
offsets below come straight from `interpret_response`):

- **0x01 reportNumberOfDTCByStatusMask**
  - Request: `19 01 <StatusMask>`
  - Response: `59 01 <DTCStatusAvailabilityMask> <DTCFormatIdentifier> <DTCCount_hi> <DTCCount_lo>`.
    CONFIRMED: `status_availability = data[1]`, `dtc_format = data[2]`,
    `dtc_count = unpack('>H', data[3:5])` — count is 16-bit big-endian.
- **0x02 reportDTCByStatusMask** (and the "availability-mask + 4-byte records" group:
  0x0A reportSupportedDTCs, 0x0F mirror, 0x13 emissions, 0x15 permanent,
  0x0B/0x0C/0x0D/0x0E first/most-recent, 0x17 userDef — all parsed identically)
  - Request: `19 02 <StatusMask>`; for 0x0A: `19 0A` (no mask). To read all faults with
    current status VCDS-style, VAG modules accept `19 02 FF`.
  - Response: `59 02 <DTCStatusAvailabilityMask>` then repeating 4-byte records
    `<DTC_hi> <DTC_mid> <DTC_lo> <StatusByte>`. CONFIRMED (dtc = `unpack('>L','\x00'+data[i:i+3])`,
    status = `data[i+3]`).
- **0x03 reportDTCSnapshotIdentification**: `59 03` then repeating 4-byte records
  `<DTC(3)> <SnapshotRecordNumber(1)>`. CONFIRMED.
- **0x04 reportDTCSnapshotRecordByDTCNumber** (freeze frame)
  - Request: `19 04 <DTC_hi> <DTC_mid> <DTC_lo> <RecordNumber>` (0xFF = all records).
  - Response: `59 04 <DTC(3)> <StatusByte>` then, repeating per snapshot record:
    `<RecordNumber(1)> <NumberOfDIDs(1)>` then that many `<DID(2)> <data(len)>` pairs.
    CONFIRMED. **Data length per DID is NOT in the message** — the parser must know each
    DID's byte size a priori (udsoncan comment, re-read verbatim: "As standard does not
    specify the length of the DID, we craft it based on a config").
- **0x06 reportDTCExtendedDataRecordByDTCNumber**
  - Request: `19 06 <DTC_hi> <DTC_mid> <DTC_lo> <ExtDataRecordNumber>` (0xFF/0xFE = all;
    the request validator caps the record number at 0xEF per ISO-14229:2020, but accepts
    0xFF/0xFE as the "all records" sentinels in practice).
  - Response: `59 06 <DTC(3)> <StatusByte>` then repeating `<RecordNumber(1, non-zero)>
    <ExtData(size)>`. CONFIRMED. **ExtData size per record is not in the message** — must be
    supplied via `extended_data_size` (int or per-DTC dict); a record number of 0 is
    reserved/illegal.
- **0x14 reportDTCFaultDetectionCounter**: `59 14` then repeating `<DTC(3)> <Counter(1)>`.
  CONFIRMED (`dtc.fault_counter = dtc_bytes[3]`). The counter is the fault-maturing counter,
  useful for "almost failing" DTCs.
- DTCFormatIdentifier values (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/common/dtc.py):
  `0 = ISO15031_6 (== SAE_J2012_DA_DTCFormat_00), 1 = ISO14229_1, 2 = SAE_J1939_73,
  3 = ISO11992_4, 4 = SAE_J2012_DA_DTCFormat_04`. CONFIRMED verbatim. VAG UDS modules
  report **0x01 (ISO14229-1)** or **0x00** for the 3-byte format (which value a given VAG
  module returns is per-module — see OPEN QUESTIONS).
- FunctionalGroupIdentifiers: `0x33 EMISSIONS_SYSTEM_GROUP, 0xD0 SAFETY_SYSTEM_GROUP,
  0xFE VOBD_SYSTEM`. CONFIRMED verbatim (same dtc.py).

#### D. DTC status byte bits (ISO 14229 Annex D)

From udsoncan dtc.py `Status.get_byte_as_int` / `set_byte` (src:
https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/common/dtc.py).
Re-read this session; bit assignments matched line for line.

| Bit | Mask | Name |
|-----|------|------|
| 0 | 0x01 | testFailed |
| 1 | 0x02 | testFailedThisOperationCycle |
| 2 | 0x04 | pendingDTC |
| 3 | 0x08 | confirmedDTC |
| 4 | 0x10 | testNotCompletedSinceLastClear |
| 5 | 0x20 | testFailedSinceLastClear |
| 6 | 0x40 | testNotCompletedThisOperationCycle |
| 7 | 0x80 | warningIndicatorRequested |

Implementation (exact, matches existing `vagtune/uds/services.py DtcStatus`):
```python
TEST_FAILED=0x01; TEST_FAILED_THIS_CYCLE=0x02; PENDING=0x04; CONFIRMED=0x08
TEST_NOT_COMPLETE_SINCE_CLEAR=0x10; TEST_FAILED_SINCE_CLEAR=0x20
TEST_NOT_COMPLETE_THIS_CYCLE=0x40; WARNING_INDICATOR_REQUESTED=0x80
```

- Severity byte (subfunctions 0x08/0x09): bit5 0x20 maintenanceOnly, bit6 0x40
  checkAtNextExit, bit7 0x80 checkImmediately; low 5 bits = DTC class (class0..class4 =
  0x01/0x02/0x04/0x08/0x10). CONFIRMED verbatim (same dtc.py Severity/DtcClass).

#### I. ClearDiagnosticInformation 0x14

- Request: `14 <hi> <mid> <lo>`; the 3-byte group is the DTC mask; **0xFFFFFF = all
  DTCs/groups**. CONFIRMED verbatim (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/ClearDiagnosticInformation.py
  — docstring "DTC mask ranging from 0 to 0xFFFFFF. 0xFFFFFF means all DTCs"; the request
  builder packs `hb/mb/lb` as the 3 bytes).
- 2020-era optional 4th byte `memorySelection` (introduced in the 2013 ISO version;
  omit for 2008-2013 ECUs). CONFIRMED (same file).
- Positive response: `54` with no data. Typical negatives: 0x13, 0x22, 0x31.
- VAG note: the flash flow sends OBD-II mode `04` (clear) BEFORE switching to UDS as an
  essential "knock" to start the diagnostic process in the ASW. CONFIRMED (src: VW_Flash
  docs/docs.md re-read this session — "Clear Diagnostic Trouble Codes over OBD-II byte `04`
  … This is an essential 'knock' which starts the diagnostic process in the Application
  Software"; lib/constants.py testdata pairs `b"\x04": b"\x04"`).

#### J. ControlDTCSetting 0x85 and CommunicationControl 0x28

- ControlDTCSetting: `85 01` = ON, `85 02` = OFF; SettingType range 0..0x7F; optional
  DTCSettingControlOptionRecord bytes may follow. CONFIRMED (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/ControlDTCSetting.py
  — `on=1, off=2`, `validate_int(setting_type, min=0, max=0x7F)`).
- CommunicationControl controlType: `0 enableRxAndTx, 1 enableRxAndDisableTx,
  2 disableRxAndEnableTx, 3 disableRxAndTx, 4 enableRxAndDisableTxWithEnhancedAddressInformation,
  5 enableRxAndTxWithEnhancedAddressInformation`. CONFIRMED verbatim (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/CommunicationControl.py).
  Request: `28 <controlType> <communicationType> [<nodeId_hi> <nodeId_lo>]`; the nodeId
  2 bytes are required/allowed only for controlType 4/5 on the 2013+ standard.
- communicationType byte (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/common/CommunicationType.py):
  `byte = (message_type & 0x3) | ((subnet & 0xF) << 4)` — low 2 bits = message class
  (bit0 0x01 normalMsg, bit1 0x02 networkManagementMsg), high nibble (bits7-4) = subnet
  (0x0 = node/this subnet, 0xF = all/network). CONFIRMED verbatim. So "disable all tx,
  normal messages, all subnets" = `28 03 01`; VW silences the bus with `28 03 01` during
  flash and re-enables with `28 00 01` (the specific VW values are convention/trace, not in
  the fetched udsoncan source — see REPORTED).

#### K. InputOutputControlByIdentifier 0x2F (output/actuator tests)

- controlOptionRecord first byte: `0 returnControlToECU, 1 resetToDefault,
  2 freezeCurrentState, 3 shortTermAdjustment`. CONFIRMED verbatim (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/InputOutputControlByIdentifier.py
  — enum + `control_param` range check 0..3).
- Request: `2F <DID_hi> <DID_lo> <controlOption(1)> [controlState...] [controlEnableMaskRecord...]`.
  Response: `6F <DID_hi> <DID_lo> <controlOption echo> [status/data...]`. CONFIRMED (the
  response carries `did_echo` + `control_param_echo`).
- Output test pattern: `2F <DID> 03 <value>` drives an actuator (shortTermAdjustment);
  `2F <DID> 00` returns control. VAG exposes actuators as manufacturer DIDs (per-module;
  the specific DID numbers are in the ODX/label files — see REPORTED).

#### L. RoutineControl 0x31 and routine ID ranges — CORRECTED

- Subfunctions: `1 startRoutine, 2 stopRoutine, 3 requestRoutineResults`. CONFIRMED (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/RoutineControl.py).
  Request: `31 <subfn(1)> <RID_hi> <RID_lo> [routineControlOptionRecord...]`
  (`struct.pack('>H', routine_id)`). Response: `71 <subfn> <RID_hi> <RID_lo> [statusRecord...]`
  (`routine_id_echo = unpack('>H', data[1:3])`). CONFIRMED.
- **Routine ID ranges — corrected against uds.readthedocs.io/rid.html** (re-fetched this
  session because the previously-cited docs.rs page is now HTTP 404):
  - `0x0000-0x00FF` ISOSAEReserved
  - `0x0100-0x01FF` TachographTestIds
  - `0x0200-0xDFFF` VehicleManufacturerSpecific
  - `0xE000-0xE1FF` OBDTestIds
  - `0xE200` **"Execute SPL"** (NOT deployLoop — prior sheet was wrong)
  - `0xE201` DeployLoopRoutineID
  - `0xE202-0xE2FF` SafetySystemRoutineIDs (prior sheet said 0xE201-0xE2FF — off by one)
  - `0xE300-0xEFFF` ISOSAEReserved
  - `0xF000-0xFEFF` SystemSupplierSpecific
  - `0xFF00` eraseMemory
  - `0xFF01` checkProgrammingDependencies
  - `0xFF02-0xFFFF` ISOSAEReserved — **so `0xFF02 eraseMirrorMemoryDTCs` is NOT confirmed by
    this source; demoted to REPORTED.**
  (src: https://uds.readthedocs.io/en/latest/pages/knowledge_base/rid.html)
- VAG/Simos flash routines — **only one routine literally appears in the VW_Flash
  testdata**: `31 01 02 03` → `71 01 02 03` (startRoutine, RID **0x0203**). The eraseMemory
  (0xFF00) and checksum/verify steps are described in docs/docs.md as narrative procedure
  steps ("Erase Block procedure", "Checksum procedure") **without explicit request bytes**,
  so their exact RID bytes on VAG are REPORTED, not captured. CLAUDE.md records the project
  fact "checksum verify routine (0x31 0x0202)"; confirm the real RID (0x0202 vs 0x0203 vs
  other) with a trace. (src: lib/constants.py testdata; docs/docs.md steps re-read this
  session.)

#### P. DiagnosticSessionControl 0x10 — sessions and P2 timing

- Session types: `1 defaultSession, 2 programmingSession, 3 extendedDiagnosticSession,
  4 safetySystemDiagnosticSession`; 0x40-0x5F manufacturer-specific, 0x60-0x7E
  supplier-specific. CONFIRMED (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/DiagnosticSessionControl.py).
- Response (2013+ form): `50 <session> <P2_hi> <P2_lo> <P2*_hi> <P2*_lo>` (5 data bytes).
  udsoncan decodes `p2_server_max = a/1000` (s) and `p2_star_server_max = (b*10)/1000` (s) —
  i.e. **P2 is in ms, P2\* is in 10 ms units**, both 16-bit big-endian. CONFIRMED verbatim
  (same file: `len(response.data) != 5` guard, then those two formulas).
- The **0x4F session is real on VAG** and is exercised by VW_Flash testdata (`10 4F` →
  `50 4F 12 23 34 45`, alongside `10 03` and `10 02`). CONFIRMED present (src:
  lib/constants.py testdata). Its precise semantics are REPORTED (see below). NB the testdata
  P2/P2* bytes (`12 23 34 45`) are placeholder values, not a real module's timing.
- S3 (tester-present keepalive) timeout ≈ 5 s; the tester must send `3E 80` well within 5 s
  to hold a non-default session. CONFIRMED (src:
  https://embetronicx.com/tutorials/automotive/uds-protocol/diagnostics-and-communication-management/
  — "after … 5 seconds, the ECU goes back to the default session").

#### Q. ECUReset 0x11 and TesterPresent 0x3E

- ECUReset subfunctions: `0x01 hardReset, 0x02 keyOffOnReset, 0x03 softReset,
  0x04 enableRapidPowerShutDown, 0x05 disableRapidPowerShutDown`. Request `11 <sub>` →
  `51 <sub>`. CONFIRMED (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/ECUReset.py).
- TesterPresent: `3E 00` → `7E 00`; `3E 80` suppresses the positive response (keepalive).
  CONFIRMED (`3E 00`→`7E 00` is in VW_Flash testdata; _sid=0x3E in udsoncan TesterPresent.py).

#### S. ISO-TP / UDS timing defaults (for the transport layer)

- S3 server = 5000 ms keepalive window. CONFIRMED (embetronicx, §P).
- ISO 15765-2 defines the flow-control frame (3 PCI bytes), the **block size** ("count of
  frames that may be sent before waiting for the next flow control frame; a value of zero
  [means no further FC]") and **STmin** (separation time). CONFIRMED present (src:
  https://en.wikipedia.org/wiki/ISO_15765-2, re-read). **The numeric default timeouts
  (N_As/N_Bs/N_Cr, P2_client, P2*_client) are NOT on that page** — they remain REPORTED
  below; always prefer the P2/P2* values returned in the 0x10 response (§P).

---

### Reported / unverified (confidence)

- **0xFF02 eraseMirrorMemoryDTCs routine** — low. rid.html lists 0xFF02-0xFFFF as ISOSAEReserved
  (no named 0xFF02). The eraseMirrorMemory routine exists in some ISO editions; confirm per
  module.
- **P2 client ≈ 50 ms, P2\* client ≈ 5000 ms** — medium; standard ISO 14229 client defaults
  but not on any page fetched this session. Always prefer the 0x10-response values.
- **0x4F session semantics on VAG** — low/medium. Exercised by VW_Flash testdata (so the
  session byte is real on VAG) but whether it is an EOL/end-of-line session or another
  extended variant is unconfirmed.
- **DynamicallyDefineDataIdentifier 0x2C for fast logging — layout CORRECTED, VAG support
  high.** udsoncan confirms the subfunctions `1 defineByIdentifier, 2 defineByMemoryAddress,
  3 clearDynamicallyDefinedDataIdentifier` (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/DynamicallyDefineDataIdentifier.py).
  VW_Flash testdata exercises `2C 03 F2 00` (clear) and a large `2C 02 F2 00 ...` (define by
  memory address) building a logging list, plus `22 F2 00` read-back.
  **Correction to the prior sheet:** the per-entry format is NOT "`D0 <3-byte addr> <1-byte
  size>` with D0 as the addressAndLengthFormatIdentifier". Re-reading the captured bytes,
  the request is `2C 02 F2 00 14  D0 01 B3 AA 01  D0 01 20 22 02  D0 01 24 00 02 …`, i.e.:
  - `2C 02` defineByMemoryAddress, `F2 00` dynamic DID,
  - **`14` = the addressAndLengthFormatIdentifier (ALFID): high nibble 1 = memorySize is
    1 byte, low nibble 4 = memoryAddress is 4 bytes**,
  - then repeating entries of **4-byte address + 1-byte size**, where the addresses all begin
    with `0xD0…` because that is the Simos RAM region (e.g. `0xD001B3AA` size 1,
    `0xD0012022` size 2). The `D0` is the top byte of the RAM address, not a format byte.
  This is medium-high confidence (clean arithmetic fit against the capture); confirm the
  ALFID=0x14 reading and that the read-back `62 F2 00 …` echoes the same entries, on a real
  module with `2C`/`22 F2 00`. (src: lib/constants.py testdata, re-read this session.)
- **2A ReadDataByPeriodicIdentifier** — medium (format from ISO 14229; udsoncan's
  implementation is a stub that `raise NotImplementedError`, CONFIRMED this session, so it is
  NOT a source for the byte layout). Reported format: `2A <txMode> <pDID1> <pDID2>…` with
  txMode `01 slow, 02 medium, 03 fast, 04 stop`; periodic DIDs are the low byte of the
  0xF200-0xF2FF range; responses arrive as unsolicited `<pDID> <data>` frames. Confirm from
  ISO 14229 text or a trace.

---


---

## 6. OBD-II (SAE J1979 / ISO 15031-5) over ISO 15765-4

Source sheet: `obd2.md` (independently re-verified 2026-10-05). Addressing, DLC/padding, bit rates, the initialisation sequence
and the ISO 15765-4 network-layer timing are in §3.1 (same sheet, §1). This layer holds: framing/NRCs/response rules, the
supported-bitmap scheme, the **complete Mode 01 PID table 00–C8** with byte counts and formulas, the PID 4F/50 scaling
override, PID 01/41 bit decode, enumerated PIDs, Mode 02, Modes 03/07/0A/04, Mode 06 with the complete OBDMID, TID and
UASID tables, Mode 08, Mode 09 InfoTypes with parsers, and the readiness semantics relevant to both cars.

### Source key for this layer (verbatim from the sheet)

| key | URL | what it is |
|---|---|---|
| W | https://en.wikipedia.org/wiki/OBD-II_PIDs (raw wikitext via `?action=raw`) | primary PID/formula table |
| ISO5 | https://share.qclt.com/%E6%B1%BD%E8%BD%A6%E8%AF%8A%E6%96%AD%E5%8D%8F%E8%AE%AE2/ISO-15031-5[1].pdf | full BS ISO 15031-5:2006 (= SAE J1979 2006): services, Annex A (supported bitmaps), B (PIDs), D (OBDMIDs), E (UASIDs), F (Mode 08 TIDs), G (InfoTypes). Note: curl needs `--globoff` because of the `[1]` in the URL. |
| ISO5-2011 | https://cdn.standards.iteh.ai/samples/50816/e3bb5908f78b44b8876857d54f75bdde/ISO-15031-5-2011.pdf | ISO 15031-5:2011 **preview (TOC + foreword only)** |
| ISO4 | https://testerpresent.com.au/DiagInfo/ISO%2015765-4%202005E.pdf | full ISO 15765-4:2005: CAN IDs, DLC, timing, init sequence |
| ISO2 | https://netcult.ch/elmue/HUD%20ECU%20Hacker/ISO%2015765-2.pdf | ISO 15765-2:2004 (padding clause 7.4.2/7.4.3, Annex/7.3.3 29-bit normal-fixed addressing). pdftotext output is mirrored line-by-line; reverse each line before grepping. |
| PYOBD | https://raw.githubusercontent.com/brendan-w/python-OBD/master/obd/{UnitsAndScaling.py,commands.py,decoders.py,protocols/protocol_can.py,codes.py} | open-source decoder (secondary) |
| ELM | https://cdn.sparkfun.com/assets/learn_tutorials/8/3/ELM327DS.pdf | ELM327 datasheet (worked CAN examples, PP 26) |
| CSS | https://www.csselectronics.com/pages/obd2-explained-simple-intro | 29-bit IDs, vendor intro |
| DASH | https://www.dashlogic.com/docs/technical/obdii_pids | vendor listing of J1979 PIDs incl. $5F/$65/$69–$9C byte layouts |
| GM6 | https://gsi.ext.gm.com/gmspo/mode6/pdf/GM%20CAN%20mode%20$06%20data%20final_dm.pdf | GM Mode $06 definitions (cross-check of OBDMID/TID/UASID usage) |
| UDSW | https://en.wikipedia.org/wiki/Unified_Diagnostic_Services | NRC names |
| OBDW | https://en.wikipedia.org/wiki/On-board_diagnostics | DTC letter/digit meaning |
| OBDLINK | https://www.scantool.net/scantool/downloads/678/obdlink_frpm_e.pdf | OBDLink manual (filler-byte default, 29-bit example) |
| PYUDS | https://uds.readthedocs.io/en/latest/pages/knowledge_base/can.html | py-uds knowledge base (addressing formats, padding 0xCC) |
| VWF | https://raw.githubusercontent.com/bri3d/VW_Flash/master/lib/connections/connection_setup.py | open-source VW (Simos/DSG) UDS flashing tool: ISO-TP tester padding value |
| VWS | https://en.wikipedia.org/wiki/Volkswagen_emissions_scandal (raw) | WVU test-vehicle table (Jetta 2.0 TDI = LNT, Passat 2.0 TDI = SCR) |
| CLAUDE | /home/user/ruggedroute-dataops/vagtune/CLAUDE.md | project's own previously verified facts (UDS IDs) |

Not fetchable in this session (403 / 404): api.github.com (use raw.githubusercontent.com), Wikipedia "Volkswagen_EA189" (page does not exist).

### Verified (source)

#### 2. Message framing, positive/negative responses, NRCs

- Positive response SID = request SID + 0x40 (`41,42,43,44,46,47,48,49`; `4A` for 0x0A — see REPORTED for the 0A payload). (src: W response table "Same as query, except that 40h is added to the service value. So: 41h = show current data; 42h = freeze frame; etc."; ISO5 Table 126 "SIDPR 41")
- Negative response (ISO5 Table 11 "Negative response message format for ISO 14230-4, ISO 15765-4"): `7F <requestSID> <ResponseCode>` — exactly 3 bytes.
- NRCs defined for OBD (ISO5 Table 12). **Only 0x21, 0x22 and 0x78 are marked "Supported by ISO 15765-4"**; 0x10, 0x11, 0x12 are listed as ISO 14230-4 (K-line) codes: **0x10** generalReject, **0x11** serviceNotSupported, **0x12** subFunctionNotSupported-InvalidFormat, **0x21** busy-RepeatRequest ("this negative response code is only allowed to be used during the initialization sequence of the protocol"; "If the server (ECU) is able to perform the diagnostic task but needs additional time … response code $78 are used instead of $21"), **0x22** conditionsNotCorrectOrRequestSequenceError, **0x78** requestCorrectlyReceived-ResponsePending ("may be repeated by the ECU(s) … until the positive response message with the requested data is available"). (src: ISO5 Table 12). A VW ECU may still send other UDS NRCs; UDS names (src: UDSW NRC table): 0x13 incorrectMessageLengthOrInvalidFormat, 0x14 responseTooLong, 0x31 requestOutOfRange, 0x33 securityAccessDenied, 0x7E SubFunctionNotSupportedInActiveSession, 0x7F serviceNotSupportedInActiveSession. Implementation: decode any NRC byte with the UDS table, never fail on an unexpected one.
- Response rules on CAN (ISO5 Table 7 "Proper response from server/ECU for ISO 15765-4 protocol", verbatim rows): a) "All ECUs must respond to Service $01 PID $00 if Service $01 is supported"; b) "Service $01 unsupported PID requested — The ECU shall not respond"; c) "Service $01 supported PID requested — Respond within P2 timing (no negative response message with response code $78 allowed)"; e/f) Service $02 with no freeze frame: "PID $02 indicates $0000, but if PIDs are requested, ECU must not respond except if supported PIDs ($00, $20, …) have been requested"; h) "Service $02 unsupported PID requested, Freeze Frame stored — The ECU shall not respond"; j) "Service $03/$07 supported, no DTCs stored — Positive response indicating no DTCs is required"; m) "Service $04 supported, conditions not correct — Negative response is required ($7F, $04, $22)"; n) "Service $04 supported, conditions correct — Positive response message required. Negative response messages(s) ($7F, $04, $78) allowed until positive response message available"; p) "Service $06 supported TID requested, no stored data available — Positive response required, test values, min and max limits must be set to $00"; q/s) unsupported OBDMID → "The ECU shall not respond"; u/v/w) Service $08: respond within P2 / `7F 08 22` / unsupported TID no response; y) "Service $09 supported INFOTYPE requested, data available (VIN, CVN, CALID) — Respond within P2 timing"; z) "data not available, conditions correct (CVN) — Initial negative response message ($7F $09, $78) required within P2max (50 ms) and consecutive negative response message(s) ($7F, $09, $78) is (are) required within P2max (5,0 seconds) until positive response is sent"; aa) "($7F, $09, $22) … prior to 2005 MY only"; bb) "Service $09 unsupported INFOTYPE requested — The ECU shall not respond". → A missing response must be treated as "not supported", with the timeout = P2CAN.
- Multi-PID requests (ISO5 §7.1.1, Tables 127/128): "The request message may contain up to six (6) PIDs. An external test equipment is not allowed to request a combination of PIDs supported and PIDs, which report data values. The ECU shall support requests for up to six (6) PIDs. The request message may contain the same PID multiple times. The ECU shall treat each PID as a separate parameter and respond with data for each PID (data returned may be different for the same PID) as often as requested. The order of the PIDs in the response message is not required to match the order in the request message." The response is `41` followed by concatenated `[PID][data A..D]` records. Response lengths are implicit, so the parser needs the per-PID byte count table (section 3) to walk a multi-PID response.
- Supported-ID bitmap (ISO5 Annex A, Table A.1): response to `01 00` is `41 00 A B C D`; "Data A bit 7 → 01, Data A bit 6 → 02 … Data D bit 0 → 20" with "0 = not supported, 1 = supported"; `20` covers 0x21..0x40, `40` → 0x41..0x60, `60` → 0x61..0x80, `80` → 0x81..0xA0, `A0` → 0xA1..0xC0, `C0` → 0xC1..0xE0, `E0` → 0xE1..0xFF ("Data D bit 1 → FF; Data D bit 0 ISO/SAE reserved (set to 0)"). "To request PIDs supported range from $C1 - $FF another request message with PID#1 = $C0 and PID#2 = $E0 shall be sent" (so one request can carry `00 20 40 60 80 A0`, a second `C0 E0`). Same scheme for Service 02 PIDs, Service 06 OBDMIDs, Service 08 TIDs, Service 09 InfoTypes ("same concept for PIDs/TIDs/Infotypes support in Services $01, $02, $06, $08, $09"). "ECU(s) shall respond to all supported ranges if requested. A range is defined as a block of 32 PIDs … The ECU shall not respond to unsupported PID ranges unless subsequent ranges have a supported PID(s)". (src: ISO5 Table A.1, §7.1.2.1/7.1.2.2, §7.6.1, §7.8.1, §7.9.1). Worked example (W "Service 01 PID 00"): `BE1FA813` → supported 01, 03, 04, 05, 06, 07, 0C, 0D, 0E, 0F, 10, 11, 13, 15, 1C, 1F and 20. Implementation:

```python
def parse_supported(base: int, abcd: bytes) -> set[int]:
    bits = int.from_bytes(abcd, "big")
    return {base + 32 - i for i in range(32) if bits >> i & 1}   # i=31 -> base+1 ... i=0 -> base+32
# walk: base=0; while base+0x20 in supported: request base+0x20 (up to 0xE0)
```

#### 3. Mode 01 (`01 <PID>` → `41 <PID> <data>`) complete PID table

Letters A,B,C,… = data bytes in order after the echoed PID. Formulas are implementation form (Python). `u16(A,B) = A*256+B`, `s16(A,B) = u16(A,B) - 65536 if u16(A,B) > 32767 else u16(A,B)`. "bytes" = number of data bytes returned (needed to walk multi-PID responses). Sources: W for every row (byte count, name, formula, min/max, unit re-checked row by row against the raw wikitext) unless noted; DASH for the $5F and $65–$9C byte layouts (re-checked against the dashlogic page); ISO5 Annex B for $01,$02,$03,$12,$13,$1C,$1D,$1E,$32,$41,$4F,$50,$51,$54 wording.

| PID | bytes | name | decode | unit | min..max |
|---|---|---|---|---|---|
| 00 | 4 | PIDs supported 01–20 | bitmap (sec. 2) | — | — |
| 01 | 4 | Monitor status since DTCs cleared | bit decode (sec. 4.1) | — | — |
| 02 | 2 | DTC that caused freeze frame (Mode 02 only) | DTC decode (sec. 6); `0000` = no freeze frame (ISO5 Table B.3 "$0000 indicates no freeze frame data") | — | — |
| 03 | 2 | Fuel system status | A = fuel system 1, B = fuel system 2, enumeration (sec. 4.2) | — | — |
| 04 | 1 | Calculated engine load | `A*100/255` | % | 0..100 |
| 05 | 1 | Engine coolant temperature | `A-40` | °C | -40..215 |
| 06 | 1 | STFT bank 1 | `A*100/128-100` | % | -100..99.2 |
| 07 | 1 | LTFT bank 1 | `A*100/128-100` | % | -100..99.2 |
| 08 | 1 | STFT bank 2 | `A*100/128-100` | % | -100..99.2 |
| 09 | 1 | LTFT bank 2 | `A*100/128-100` | % | -100..99.2 |
| 0A | 1 | Fuel pressure (gauge) | `3*A` | kPa | 0..765 |
| 0B | 1 | Intake manifold absolute pressure | `A` | kPa | 0..255 |
| 0C | 2 | Engine speed | `u16(A,B)/4` | rpm | 0..16383.75 |
| 0D | 1 | Vehicle speed | `A` | km/h | 0..255 |
| 0E | 1 | Timing advance | `A/2-64` | ° BTDC | -64..63.5 |
| 0F | 1 | Intake air temperature | `A-40` | °C | -40..215 |
| 10 | 2 | MAF air flow rate | `u16(A,B)/100` — **but if PID 50 byte A ≠ 0, scale = `A50*10/65535` g/s per bit** (ISO5 Table B.61, see note after table) | g/s | 0..655.35 |
| 11 | 1 | Throttle position | `A*100/255` | % | 0..100 |
| 12 | 1 | Commanded secondary air status | enumeration (sec. 4.3) | — | — |
| 13 | 1 | O2 sensors present (2 banks) | bit A0..A3 = B1S1..B1S4, A4..A7 = B2S1..B2S4 (1 = present); "PID $13 shall only be supported by a given vehicle if PID $1D is not supported. In no case shall a vehicle support both PIDs" (ISO5 Table B.20) | — | — |
| 14 | 2 | O2 sensor 1 (B1S1) | V = `A/200`; STFT = `B*100/128-100`; `B==0xFF` → "sensor is not used in trim calculation" (W; ISO5 B.22 "$FF if this sensor is not used") | V, % | 0..1.275, -100..99.2 |
| 15 | 2 | O2 sensor 2 (B1S2) | same as 14 | | |
| 16 | 2 | O2 sensor 3 (B1S3) | same as 14 | | |
| 17 | 2 | O2 sensor 4 (B1S4) | same as 14 | | |
| 18 | 2 | O2 sensor 5 (B2S1) | same as 14 | | |
| 19 | 2 | O2 sensor 6 (B2S2) | same as 14 | | |
| 1A | 2 | O2 sensor 7 (B2S3) | same as 14 | | |
| 1B | 2 | O2 sensor 8 (B2S4) | same as 14 | | |
| 1C | 1 | OBD standard this vehicle conforms to | enumeration (sec. 4.4) | — | 1..250 |
| 1D | 1 | O2 sensors present (4 banks) | A0..A7 = B1S1,B1S2,B2S1,B2S2,B3S1,B3S2,B4S1,B4S2 (W; ISO5 Table B.24 identical) | — | — |
| 1E | 1 | Auxiliary input status | A0 = PTO active ("0 = PTO not active (OFF); 1 = PTO active (ON)"); A1..A7 "ISO/SAE reserved (Bits shall be reported as '0')" (src: ISO5 Table B.25; W "A0 == Power Take Off (PTO) status (1 == active) [A1..A7] not used"). python-OBD `aux_input_status` reads `(d[0] >> 7) & 1` (bit 7), which is wrong. | — | — |
| 1F | 2 | Run time since engine start | `u16(A,B)` | s | 0..65535 |
| 20 | 4 | PIDs supported 21–40 | bitmap | | |
| 21 | 2 | Distance traveled with MIL on | `u16(A,B)` | km | 0..65535 |
| 22 | 2 | Fuel rail pressure (relative to manifold vacuum) | `u16(A,B)*0.079` | kPa | 0..5177.265 |
| 23 | 2 | Fuel rail gauge pressure (diesel / GDI) | `u16(A,B)*10` | kPa | 0..655350 |
| 24 | 4 | O2 sensor 1 λ + voltage | λ = `u16(A,B)*2/65536`; V = `u16(C,D)*8/65536` — **λ scale is overridden by PID 4F byte A when non-zero** (see note) | ratio, V | 0..<2, 0..<8 |
| 25 | 4 | O2 sensor 2 | same as 24 | | |
| 26 | 4 | O2 sensor 3 | same as 24 | | |
| 27 | 4 | O2 sensor 4 | same as 24 | | |
| 28 | 4 | O2 sensor 5 | same as 24 | | |
| 29 | 4 | O2 sensor 6 | same as 24 | | |
| 2A | 4 | O2 sensor 7 | same as 24 | | |
| 2B | 4 | O2 sensor 8 | same as 24 | | |
| 2C | 1 | Commanded EGR | `A*100/255` | % | 0..100 |
| 2D | 1 | EGR error | `A*100/128-100` | % | -100..99.2 |
| 2E | 1 | Commanded evaporative purge | `A*100/255` | % | 0..100 |
| 2F | 1 | Fuel tank level input | `A*100/255` | % | 0..100 |
| 30 | 1 | Warm-ups since codes cleared | `A` | count | 0..255 |
| 31 | 2 | Distance traveled since codes cleared | `u16(A,B)` | km | 0..65535 |
| 32 | 2 | Evap system vapor pressure | `s16(A,B)/4` (two's complement; ISO5 Table B.38: "($8000) −8192 Pa … ($7FFF) 8191.75 Pa, 0,25 Pa (1/4) per bit signed"; W "(AB is two's complement signed)") | Pa | -8192..8191.75 |
| 33 | 1 | Absolute barometric pressure | `A` | kPa | 0..255 |
| 34 | 4 | O2 sensor 1 λ + current | λ = `u16(A,B)*2/65536` (PID 4F override applies); I = `u16(C,D)/256-128` | ratio, mA | 0..<2, -128..<128 |
| 35 | 4 | O2 sensor 2 | same as 34 | | |
| 36 | 4 | O2 sensor 3 | same as 34 | | |
| 37 | 4 | O2 sensor 4 | same as 34 | | |
| 38 | 4 | O2 sensor 5 | same as 34 | | |
| 39 | 4 | O2 sensor 6 | same as 34 | | |
| 3A | 4 | O2 sensor 7 | same as 34 | | |
| 3B | 4 | O2 sensor 8 | same as 34 | | |
| 3C | 2 | Catalyst temperature B1S1 | `u16(A,B)/10-40` | °C | -40..6513.5 |
| 3D | 2 | Catalyst temperature B2S1 | same | | |
| 3E | 2 | Catalyst temperature B1S2 | same | | |
| 3F | 2 | Catalyst temperature B2S2 | same | | |
| 40 | 4 | PIDs supported 41–60 | bitmap | | |
| 41 | 4 | Monitor status this drive cycle | like PID 01 but A is always 0 (sec. 4.1) | | |
| 42 | 2 | Control module voltage | `u16(A,B)/1000` | V | 0..65.535 |
| 43 | 2 | Absolute load value | `u16(A,B)*100/255` | % | 0..25700 |
| 44 | 2 | Commanded λ (equivalence ratio) | `u16(A,B)*2/65536` (PID 4F override applies) | ratio | 0..<2 |
| 45 | 1 | Relative throttle position | `A*100/255` | % | 0..100 |
| 46 | 1 | Ambient air temperature | `A-40` | °C | -40..215 |
| 47 | 1 | Absolute throttle position B | `A*100/255` | % | 0..100 |
| 48 | 1 | Absolute throttle position C | `A*100/255` | % | |
| 49 | 1 | Accelerator pedal position D | `A*100/255` | % | |
| 4A | 1 | Accelerator pedal position E | `A*100/255` | % | |
| 4B | 1 | Accelerator pedal position F | `A*100/255` | % | |
| 4C | 1 | Commanded throttle actuator | `A*100/255` | % | |
| 4D | 2 | Time run with MIL on | `u16(A,B)` | min | 0..65535 |
| 4E | 2 | Time since trouble codes cleared | `u16(A,B)` | min | 0..65535 |
| 4F | 4 | Max values: λ, O2 V, O2 mA, MAP ("External Test Equipment Configuration Information #1", "not intended for display") | `A` ratio, `B` V, `C` mA, `D*10` kPa (W; ISO5 Table B.60) — **scaling override, see note** | | 255,255,255,2550 |
| 50 | 4 | Max MAF ("Configuration Information #2") | `A*10` g/s; B,C,D reserved (W; ISO5 Table B.61) — **scaling override for PID 10, see note** | g/s | 0..2550 |
| 51 | 1 | Fuel type | enumeration (sec. 4.5) | | |
| 52 | 1 | Ethanol fuel % | `A*100/255` | % | 0..100 |
| 53 | 2 | Absolute evap system vapor pressure | `u16(A,B)/200` | kPa | 0..327.675 |
| 54 | 2 | Evap system vapor pressure | `s16(A,B)` (two's complement; ISO5 Table B.65 "1 Pa, signed"; W "(AB is two's complement signed)"). ISO5: a vehicle supports $32 or $54, never both. | Pa | -32768..32767 |
| 55 | 2 | Short term secondary O2 trim, A: bank 1, B: bank 3 | `A*100/128-100`, `B*100/128-100` | % | -100..99.2 |
| 56 | 2 | Long term secondary O2 trim, A: bank 1, B: bank 3 | same | | |
| 57 | 2 | Short term secondary O2 trim, A: bank 2, B: bank 4 | same | | |
| 58 | 2 | Long term secondary O2 trim, A: bank 2, B: bank 4 | same | | |
| 59 | 2 | Fuel rail absolute pressure | `u16(A,B)*10` | kPa | 0..655350 |
| 5A | 1 | Relative accelerator pedal position | `A*100/255` | % | 0..100 |
| 5B | 1 | Hybrid battery pack remaining life | `A*100/255` | % | 0..100 |
| 5C | 1 | Engine oil temperature | `A-40` | °C | -40..210 |
| 5D | 2 | Fuel injection timing | `u16(A,B)/128-210` | ° | -210..301.992 |
| 5E | 2 | Engine fuel rate | `u16(A,B)/20` | L/h | 0..3212.75 |
| 5F | 1 | Emission requirements vehicle is designed to | enumeration (sec. 4.6) | | |
| 60 | 4 | PIDs supported 61–80 | bitmap | | |
| 61 | 1 | Driver's demand engine percent torque | `A-125` | % | -125..130 |
| 62 | 1 | Actual engine percent torque | `A-125` | % | -125..130 |
| 63 | 2 | Engine reference torque | `u16(A,B)` | N·m | 0..65535 |
| 64 | 5 | Engine percent torque data | `A-125` idle, `B-125` point1, `C-125` point2, `D-125` point3, `E-125` point4 | % | -125..130 |
| 65 | 2 | Auxiliary input/output supported | bit decode (sec. 4.7) | | |
| 66 | 5 | Mass air flow sensor A/B | A0 = sensor A supported, A1 = sensor B supported; A: `u16(B,C)/32`; B: `u16(D,E)/32` (W, DASH) | g/s | 0..2047.96875 |
| 67 | 3 | Engine coolant temperature 1/2 | A0,A1 support bits; `B-40`, `C-40` (W; DASH prints "°C = B - 40" for sensor 2 too, an obvious copy error) | °C | -40..215 |
| 68 | 3 (W) / 7 (DASH) | Intake air temperature sensors | W: A0/A1 = sensor 1/2, `B-40`, `C-40`. DASH: A0..A5 = B1S1,B1S2,B1S3,B2S1,B2S2,B2S3 supported; `B-40`,`C-40`,`D-40`,`E-40`,`F-40`,`G-40` | °C | -40..215 |
| 69 | 7 | Commanded EGR and EGR error | A0 cmd EGR A sup, A1 actual EGR A sup, A2 EGR A error sup, A3/A4/A5 same for EGR B; `B/2.55` cmd A %, `C/2.55` actual A %, `D/1.28-100` error A %, `E/2.55`, `F/2.55`, `G/1.28-100` for B (src: DASH) | % | |
| 6A | 5 | Commanded diesel intake air flow control / relative position | A0 cmd A sup, A1 rel A sup, A2 cmd B sup, A3 rel B sup; `B/2.55`, `C/2.55`, `D/2.55`, `E/2.55` (src: DASH) | % | |
| 6B | 5 | EGR temperature | A0..A3 = sensor A(B1S1),C(B1S2),B(B2S1),D(B2S2) supported at 1 °C res; A4..A7 = same sensors wide-range (4 °C res); byte order B=A(B1S1), C=C(B1S2), D=B(B2S1), E=D(B2S2); value `X-40` or wide `X*4-40` (src: DASH) | °C | |
| 6C | 5 | Commanded throttle actuator control / relative throttle position | A0 cmd A, A1 rel A, A2 cmd B, A3 rel B supported; `B/2.55`,`C/2.55`,`D/2.55`,`E/2.55` (src: DASH) | % | |
| 6D | 11 | Fuel pressure control system | A0 cmd rail P A, A1 rail P A, A2 fuel temp A, A3 cmd rail P B, A4 rail P B, A5 fuel temp B supported; cmd A `u16(B,C)*10` kPa; actual A `u16(D,E)*10` kPa; temp A `F-40` °C; cmd B `u16(G,H)*10`; actual B `u16(I,J)*10`; temp B `K-40` (src: DASH) | kPa, °C | |
| 6E | 9 | Injection pressure control system | A0 cmd ICP A, A1 ICP A, A2 cmd ICP B, A3 ICP B supported; `u16(B,C)*10`, `u16(D,E)*10`, `u16(F,G)*10`, `u16(H,I)*10` kPa (src: DASH) | kPa | |
| 6F | 3 | Turbocharger compressor inlet pressure | A0 sensor A (1 kPa res), A1 sensor B (1 kPa), A2 sensor A wide (8 kPa res), A3 sensor B wide; `B` or `B*8`; `C` or `C*8` (src: DASH) | kPa | |
| 70 | 10 | Boost pressure control | A0 cmd boost A, A1 boost sensor A, A2 boost A control status, A3/A4/A5 same for B; cmd A `u16(B,C)/32`; sensor A `u16(D,E)/32`; cmd B `u16(F,G)/32`; sensor B `u16(H,I)/32`; J bits1-0 = A status, bits3-2 = B status: 00 reserved, 01 open loop, 10 closed loop, 11 fault present (src: DASH; W's row reads "Sensor 1: (256D+E)/0.03125" which is a typo for ×0.03125 = /32 — W's own max 2047.96875 = 65535/32) | kPa | 0..2047.97 |
| 71 | 6 | VGT control | A0 cmd VGT A pos, A1 VGT A pos, A2 VGT A status, A3/A4/A5 for B; `B/2.55`,`C/2.55`,`D/2.55`,`E/2.55` %; F bits1-0 A status, bits3-2 B status (00 res, 01 open loop, 10 closed loop, 11 fault) (src: DASH) | % | |
| 72 | 5 | Wastegate control | A0 cmd A, A1 pos A, A2 cmd B, A3 pos B; `B/2.55`,`C/2.55`,`D/2.55`,`E/2.55` (src: DASH) | % | |
| 73 | 5 | Exhaust pressure | A0 bank1, A1 bank2 supported; `u16(B,C)/100`, `u16(D,E)/100` (src: DASH) | kPa | |
| 74 | 5 | Turbocharger RPM | A0 turbo A, A1 turbo B; `u16(B,C)*10`, `u16(D,E)*10` (src: DASH) | rpm | |
| 75 | 7 | Turbocharger A temperature | A0 comp inlet, A1 comp outlet, A2 turbine inlet, A3 turbine outlet supported; `B-40`, `C-40` °C; `u16(D,E)/10-40`, `u16(F,G)/10-40` °C (src: DASH) | °C | |
| 76 | 7 | Turbocharger B temperature | same layout as 75 (src: DASH) | °C | |
| 77 | 5 | Charge air cooler temperature | A0 B1S1, A1 B1S2, A2 B2S1, A3 B2S2; `B-40`,`C-40`,`D-40`,`E-40` (src: DASH) | °C | |
| 78 | 9 | EGT bank 1 | A0..A3 = sensor 1..4 supported (A7-A4 reserved); S1 `u16(B,C)/10-40`, S2 `u16(D,E)/10-40`, S3 `u16(F,G)/10-40`, S4 `u16(H,I)/10-40` (src: W "Service 01 PID 78 and 79"; DASH) | °C | -40..6513.5 |
| 79 | 9 | EGT bank 2 | same as 78 | °C | |
| 7A | 7 | DPF bank 1 | A0 delta P, A1 inlet P, A2 outlet P supported; delta `s16(B,C)/100` ("two's complement signed", DASH), inlet `u16(D,E)/100`, outlet `u16(F,G)/100` (src: DASH) | kPa | |
| 7B | 7 | DPF bank 2 | same as 7A | kPa | |
| 7C | 9 | DPF temperature | A0 B1 inlet, A1 B1 outlet, A2 B2 inlet, A3 B2 outlet; `u16(B,C)/10-40`, `u16(D,E)/10-40`, `u16(F,G)/10-40`, `u16(H,I)/10-40` (src: DASH; W gives the formula `(256A+B)/10-40` without the layout) | °C | |
| 7D | 1 | NOx NTE control area status | A0 inside NOx control area, A1 outside, A2 inside manufacturer NTE carve-out, A3 NTE deficiency active (src: DASH) | | |
| 7E | 1 | PM NTE control area status | same bits for PM (src: DASH) | | |
| 7F | 13 | Engine run time | A0 total run time sup, A1 total idle sup, A2 total with PTO sup; total `B<<24|C<<16|D<<8|E`; idle `F<<24|G<<16|H<<8|I`; PTO `J<<24|K<<16|L<<8|M` (src: DASH for the three u32 fields — DASH captions all three "Total Engine Run Time", the idle/PTO assignment follows the support-bit order; W gives the B..E formula) | s | |
| 80 | 4 | PIDs supported 81–A0 | bitmap | | |
| 81 | 41 | Run time for EI-AECD #1–#5 | A0..A4 = AECD #1..#5 supported; then 10 × u32 big-endian: AECD1 timer1, AECD1 timer2, AECD2 t1, AECD2 t2 … AECD5 t2 (src: DASH) | s | |
| 82 | 41 | Run time for EI-AECD #6–#10 | same layout (src: DASH) | s | |
| 83 | 9 | NOx sensor | A0 B1S1, A1 B1S2, A2 B2S1, A3 B2S2 supported; `u16(B,C)`, `u16(D,E)`, `u16(F,G)`, `u16(H,I)` (src: DASH) | ppm | |
| 84 | 1 | Manifold surface temperature | `A-40` (src: DASH) | °C | |
| 85 | 10 | NOx reagent system | A0 avg reagent consumption sup, A1 avg demanded consumption sup, A2 tank level sup, A3 warning-mode time sup; `u16(B,C)/200` L/h, `u16(D,E)/200` L/h, `F/2.55` % (W: `F*100/255`), `G<<24|H<<16|I<<8|J` s (src: DASH, W) | | |
| 86 | 5 | PM sensor | A0 B1S1, A1 B2S1 supported; `u16(B,C)/80`, `u16(D,E)/80` mg/m³ (DASH prints "mg/mm³") (src: DASH) | | |
| 87 | 5 | Intake manifold absolute pressure A/B | A0, A1 supported; `u16(B,C)/32`, `u16(D,E)/32` (src: DASH) | kPa | |
| 88 | 13 | SCR inducement system | A: bit7 inducement active, bit3 NOx too high, bit2 reagent consumption deviation, bit1 incorrect reagent, bit0 reagent level low; B: bits7-4 = 20K-history (same 4 flags, bit7 NOx … bit4 level), bits3-0 = 10K-history; C: bits7-4 = 40K-history, bits3-0 = 30K-history; D-E km inducement active in current 10K block; F-G km in current block; H-I, J-K, L-M km inducement active in 20K/30K/40K blocks (u16 each; DASH prints "(256 * B) + C" for every pair, which is a copy error for the respective pair) (src: DASH) | km | |
| 89 | 41 | Run time for EI-AECD #11–#15 | as 81 (src: DASH) | s | |
| 8A | 41 | Run time for EI-AECD #16–#20 | as 81 (src: DASH) | s | |
| 8B | 7 | Diesel aftertreatment status | A0 DPF regen status sup, A1 DPF regen type sup, A2 NOx adsorber regen status sup, A3 NOx adsorber desulfurization status sup, A4 normalized trigger sup, A5 avg time between regens sup, A6 avg distance sup; B0 DPF regen in progress, B1 regen type (0 passive, 1 active), B2 NOx adsorber desorption (regen) in progress, B3 desulfurization in progress; `C/2.55` % normalized trigger; `u16(D,E)` min avg time between regens; `u16(F,G)` km avg distance between regens (src: DASH) | | |
| 8C | 17 | O2 sensor (wide range) | A0..A3 = concentration B1S1,B1S2,B2S1,B2S2 sup; A4..A7 = lambda B1S1,B1S2,B2S1,B2S2 sup; concentration `u16(B,C)*0.001526`, `u16(D,E)*…`, `u16(F,G)*…`, `u16(H,I)*…` %; lambda `u16(J,K)*0.000122`, `u16(L,M)*…`, `u16(N,O)*…`, `u16(P,Q)*…` (src: DASH) | %, λ | |
| 8D | 1 | Throttle position G | `A/2.55` (src: DASH "Throttle % = A / 2.55"; W gives only 0..100 %, no formula) | % | 0..100 |
| 8E | 1 | Engine friction percent torque | `A-125` (src: W, DASH) | % | -125..130 |
| 8F | 7 | PM sensor bank 1 & 2 | A0 B1S1 operating status sup, A1 B1S1 signal sup, A2 B2S1 status sup, A3 B2S1 signal sup; B0 B1S1 actively measuring, B1 B1S1 regenerating; `u16(C,D)/100` % normalized output B1S1; E0/E1 same flags B2S1; `u16(F,G)/100` % B2S1 (src: DASH) | | |
| 90 | 3 | WWH-OBD vehicle OBD system info | A bit6 readiness (0 = all monitors complete), bits5-2 MI status (0 off, 1 on-demand, 2 short, 3 continuous, 0xE error, 0xF n/a), bits1-0 display strategy (0 nondiscriminatory, 1 discriminatory, 3 n/a); `u16(B,C)` continuous-MI hours (src: DASH) | h | |
| 91 | 5 | WWH-OBD ECU OBD system info | A bits3-0 ECU MI status (same enum); `u16(B,C)` continuous MI hours; `u16(D,E)` highest ECU B1 counter hours (src: DASH) | h | |
| 92 | 2 | Fuel system control status (compression ignition) | A0 fuel pressure ctrl 1 sup, A1 inj quantity 1, A2 inj timing 1, A3 idle fuel balance 1, A4..A7 same for ctrl 2; B same bit positions = "in closed loop" (src: DASH) | | |
| 93 | 3 | WWH-OBD vehicle OBD counters | A0 cumulative continuous MI counter sup; `u16(B,C)` hours (src: DASH) | h | |
| 94 | 12 | NOx control driver inducement status/counters | A0..A5 support (warning status, reagent quality ctr, reagent consumption ctr, absence of dosing ctr, EGR valve ctr, monitoring system ctr); B bit0 warning active, bits2-1 level1 status, bits4-3 level2, bits6-5 level3 (0 inactive,1 enabled,2 active,3 not supported); `u16(C,D)` reagent quality h; `u16(E,F)` reagent consumption h; `u16(G,H)` dosing activity h; `u16(I,J)` EGR valve h; `u16(K,L)` monitoring system h (src: DASH) | h | |
| 95–97 | — | reserved (DASH; absent from W) | | | |
| 98 | 9 | EGT bank 1 sensors 5–8 | A0..A3 = S5..S8 sup; `u16(B,C)/10-40` … `u16(H,I)/10-40` (src: DASH) | °C | |
| 99 | 9 | EGT bank 2 sensors 5–8 | same (src: DASH) | °C | |
| 9A | 6 | Hybrid/EV system data, battery, voltage | layout not given (src: W; DASH lists 9A as reserved) | | |
| 9B | 4 | Diesel exhaust fluid sensor data | `D*100/255` % (src: W; DASH lists 9B as reserved) | % | |
| 9C | 17 | O2 sensor data (wide range, sensors 3/4) | same layout as 8C for B1S3,B1S4,B2S3,B2S4 (src: DASH) | | |
| 9D | 4 | Engine fuel rate | layout not given (src: W; DASH reserved) | g/s | |
| 9E | 2 | Engine exhaust flow rate | layout not given (src: W; DASH reserved) | kg/h | |
| 9F | 9 | Fuel system percentage use | layout not given (src: W; DASH reserved) | | |
| A0 | 4 | PIDs supported A1–C0 | bitmap | | |
| A1 | 9 | NOx sensor corrected data | layout not given (src: W) | ppm | |
| A2 | 2 | Cylinder fuel rate | `u16(A,B)/32` (src: W) | mg/stroke | 0..2047.97 |
| A3 | 9 | Evap system vapor pressure | layout not given (src: W) | Pa | |
| A4 | 4 | Transmission actual gear | A1 = supported; `u16(C,D)/1000` (src: W "[A1]==Supported (256C+D)/1000") | ratio | 0..65.535 |
| A5 | 4 | Commanded DEF dosing | A0 = supported; `B/2` (src: W "[A0]= 1:Supported; 0:Unsupported B/2") | % | 0..127.5 |
| A6 | 4 | Odometer | `(A<<24|B<<16|C<<8|D)/10` (src: W) | km | 0..429496729.5 |
| A7 | 4 | NOx sensor concentration sensors 3 and 4 | layout not given (src: W) | | |
| A8 | 4 | NOx sensor corrected concentration sensors 3 and 4 | layout not given (src: W) | | |
| A9 | 4 | ABS disable switch state | A0 = supported; B0 = 1 yes (src: W "[A0]= 1:Supported; 0:Unsupported [B0]= 1:Yes;0:No") | | |
| C0 | 4 | PIDs supported C1–E0 | bitmap | | |
| C3 | 2 | Fuel level input A/B | W: "Returns numerous data, including Drive Condition ID and Engine Speed*" (W itself marks this with an asterisk — treat as unreliable) | | |
| C4 | 8 | Exhaust particulate control system diagnostic time/count | W: "B5 is Engine Idle Request, B6 is Engine Stop Request*, First byte = Time in seconds, Second byte = Count" (unreliable in W) | | |
| C5 | 4 | Fuel pressure A and B | (src: W, no formula) | kPa | 0..5177 |
| C6 | 7 | Particulate control inducement: byte1 status; 2-3 removal/block counter; 4-5 liquid reagent failure counter; 6-7 monitoring malfunction counter | (src: W) | h | 0..65535 |
| C7 | 2 | Distance since reflash or module replacement | (src: W, no formula; presumably `u16(A,B)`) | km | |
| C8 | 1 | NCD and PCD warning lamp status | (src: W, bit field not given) | | |

**PID 4F / 50 scaling override (ISO5 Tables B.60/B.61, must be implemented):** "If Data A [of PID $4F] is reported as $00, the external test equipment shall use the 'Maximum value for Equivalence Ratio' included in the original PID definition (1,999 / 65535 = 0,0000305 per bit). If the value reported in Data A of PID $4F is greater than $00, that value shall be divided by 65535 to calculate the scaling per bit to use to display Equivalence Ratio" for PIDs $24–$2B, $34–$3B and $44 (worked example: Data A = 4 → 0.0000610 per bit; raw $7D00 → 1.953). Likewise PID $50 Data A: "If Data A is reported as $00 … (655,35 g/s / 65535 bits = 0,01 g/s per bit). If the value reported in Data A of PID $50 is greater than $00, that value shall be multiplied by 10 g/s and then divided by 65 535 to calculate the scaling per bit" for PID $10. Bytes B/C/D of PID 4F (max O2 V, max O2 mA, max MAP) are described in W only as maxima; ISO5:2006 B.60 only specifies the Data A rule in the fetched text.

```python
def lambda_scale(pid4f_A: int | None) -> float:
    return (pid4f_A / 65535) if pid4f_A else 2 / 65536      # 2/65536 = 0.0000305 per bit
def maf_scale(pid50_A: int | None) -> float:
    return (pid50_A * 10 / 65535) if pid50_A else 0.01
```

Note on the ISO 15031-5:2006 version: it defines PIDs 01–5A (Tables B.2–B.71) and Table B.72 "PID $5A - $FF" lists **"5B - FF ISO/SAE reserved"**; everything above 0x5A comes from later J1979/J1979-DA editions (W, DASH). ISO 15031-5:2011 (TOC fetched, ISO5-2011) is "technically equivalent to SAE J1979:2010, with the addition of new capabilities required by revised regulations from the California Air Resources Board and revised regulations from the European Commission" and its TOC contains **no annexes at all** (Bibliography follows §8.10 directly) — the PID/OBDMID/UASID/InfoType definitions were moved out of the standard (SAE J1979-DA), which is why W/DASH are the only open sources for PIDs ≥ 0x5B.

#### 4. Bit-encoded / enumerated PIDs

##### 4.1 PID 01 (monitor status since DTCs cleared) and PID 41 (this drive cycle)

Byte A: bit7 = MIL on ("0 = MIL OFF; 1 = MIL ON"); bits6..0 = number of confirmed emission DTCs ("# of DTCs stored in this ECU", hex to decimal, 0..127). "The MIL status shall indicate 'OFF' during the key-on, engine-off bulb check unless the MIL has also been commanded 'ON' for a detected malfunction." ELM example `41 01 81 07 65 04` → MIL on, 1 DTC ("simply subtract 128 (or 80 hex) from the number"). (src: ISO5 Table B.2; W; ELM "Interpreting Trouble Codes"). PID 41: "identical form … with one exception - the first byte is always zero" (src: W; ISO5 Table B.46 "A byte 1 of 4 Reserved – shall be reported as $00").

Byte B (common/continuous monitors): bit0 misfire **supported**, bit1 fuel system supported, bit2 comprehensive component supported; **bit3 = ignition type: 0 = spark (Otto/Wankel), 1 = compression (diesel)** (src: W "B3 Indication of engine type 0 = Spark ignition (e.g. Otto or Wankel engines) 1 = Compression ignition (e.g. Diesel engines)"; ISO5:2006 Table B.2 still shows bit3 "ISO/SAE reserved (bit shall be reported as '0')" — the CI flag was added in a later J1979); bit4 misfire **not complete** (0 = complete), bit5 fuel system not complete, bit6 components not complete, bit7 reserved. Polarity (ISO5 B.2): "0 = monitor not supported (NO), 1 = monitor supported (YES)" for bits 0–2; "0 = monitor complete, or not applicable (YES); 1 = monitor not complete (NO)" for bits 4–6. (W table: Components B2/B6, Fuel System B1/B5, Misfire B0/B4.)

Byte C = availability (1 = supported), byte D = incompleteness (1 = not complete) of the non-continuous monitors; bit meaning depends on B bit3 (src: W tables "Bytes C and D are mapped as follows for spark ignition engine types" / "alternatively mapped as follows for compression ignition engine types"; ISO5 Table B.2 for the spark column except bit 4):

| bit | spark ignition (B3 = 0) | compression ignition (B3 = 1) |
|---|---|---|
| 0 | Catalyst | NMHC catalyst |
| 1 | Heated catalyst | NOx/SCR aftertreatment monitor |
| 2 | Evaporative system | reserved |
| 3 | Secondary air system | Boost pressure |
| 4 | Gasoline particulate filter (W; "A/C system refrigerant monitoring" in ISO5:2006 Table B.2) | reserved |
| 5 | Oxygen sensor | Exhaust gas sensor |
| 6 | Oxygen sensor heater | PM filter monitoring |
| 7 | EGR and/or VVT system | EGR and/or VVT system |

PID 41 semantics (ISO5 Table B.46): byte B low nibble / byte C = monitor **enabled this monitoring cycle** ("0 = monitor disabled for rest of this monitoring cycle or not supported (NO); 1 = monitor enabled for this monitoring cycle (YES)"), byte B high nibble / byte D = **completion this cycle** ("0 = monitor complete this monitoring cycle, or not supported (YES); 1 = monitor not complete this monitoring cycle (NO)"); "If a non-continuous monitor is not supported or always shows 'complete', the corresponding PID $41 bits shall indicate disabled and complete"; "data byte B bit 2 … shall always show CCM … as enabled". The "disabled" state is meant for conditions the driver cannot fix by driving (soak time, ambient temperature, BARO), never for rpm/load/throttle.

```python
SPARK = ["catalyst","heated_catalyst","evap","secondary_air","gpf_or_ac","o2_sensor","o2_heater","egr_vvt"]
CI    = ["nmhc_catalyst","nox_scr","reserved2","boost","reserved4","exhaust_gas_sensor","pm_filter","egr_vvt"]
def decode_pid01(A,B,C,D):
    mil = bool(A & 0x80); dtc_count = A & 0x7F
    ci = bool(B & 0x08)
    common = {n: (bool(B>>i & 1), not bool(B>>(i+4) & 1))   # (supported, complete)
              for i,n in enumerate(["misfire","fuel_system","components"])}
    names = CI if ci else SPARK
    specific = {n: (bool(C>>i & 1), not bool(D>>i & 1)) for i,n in enumerate(names)}
    return mil, dtc_count, ci, common, specific
```

##### 4.2 PID 03 fuel system status
Byte A = fuel system 1, byte B = fuel system 2, each one-hot (ISO5 Table B.4: "Unused bits shall be reported as '0'; no more than one bit at a time can be set to a '1'"): **0** = engine off ("If the engine is off and the ignition is on, all bits in Data Byte A and Data Byte B shall be reported as '0'"), **1** (bit0) = "Open loop - has not yet satisfied conditions to go closed loop"; **2** (bit1) = "Closed loop - using oxygen sensor(s) as feedback for fuel control"; **4** (bit2) = "Open loop due to driving conditions (e.g. power enrichment, deceleration enleanment)"; **8** (bit3) = "Open loop - due to detected system fault"; **16** (bit4) = "Closed loop, but fault with at least one oxygen sensor - may be using single oxygen sensor for fuel control"; bits 5-7 reserved = 0. "Any other value is an invalid response" (W). (src: ISO5 Table B.4; W)

##### 4.3 PID 12 commanded secondary air status
One-hot: **1** "upstream of first catalytic converter", **2** "downstream of first catalytic converter inlet", **4** "atmosphere / off", **8** "Pump commanded on for diagnostics" (W only; ISO5:2006 Table B.19 defines only bits 0-2, "3-7 ISO/SAE reserved"). (src: ISO5 Table B.19; W)

##### 4.4 PID 1C OBD standard (state encoded)
1 OBD-II (CARB), 2 OBD (EPA), 3 OBD and OBD-II, 4 OBD-I, 5 not OBD compliant, 6 EOBD, 7 EOBD+OBD-II, 8 EOBD+OBD, 9 EOBD+OBD+OBD-II, 10 JOBD, 11 JOBD+OBD-II, 12 JOBD+EOBD, 13 JOBD+EOBD+OBD-II, 14 (EURO IV B1 per ISO5 / "OBD, EOBD, and KOBD" per W), 15 (EURO V B2 per ISO5 / "OBD, OBD II, EOBD, and KOBD" per W), 16 (EURO EEC C per ISO5 / reserved per W), 17 EMD, 18 EMD+, 19 HD OBD-C, 20 HD OBD, 21 WWH OBD, 22 reserved, 23 HD EOBD-I, 24 HD EOBD-I N, 25 HD EOBD-II, 26 HD EOBD-II N, 27 HD ZEV, 28 OBDBr-1, 29 OBDBr-2, 30 KOBD, 31 IOBD I, 32 IOBD II, 33 "Heavy Duty Euro OBD Stage VI (HD EOBD-IV)", 34 OBD+OBD-II+HD OBD, 35 OBDBr-3; W then says "53-250 Reserved" (values 36–52 are simply absent from W's table); **251–255 "Not available for assignment (SAE J1939 special meaning)"** (W; ISO5 B.23 "FB - FF ISO/SAE - Not available for assignment, SAE J1939 special meaning"). (src: W "Service 01 PID 1C"; ISO5 Table B.23 for 01–11, "12 - FA ISO/SAE reserved", FB–FF). Values 14–16 differ between ISO5:2006 and W; the W list is the newer one.

##### 4.5 PID 51 fuel type (state encoded)
0 not available, 1 gasoline, 2 methanol, 3 ethanol, 4 diesel, 5 LPG, 6 CNG, 7 propane, 8 electric, 9 bifuel gasoline, 10 bifuel methanol, 11 bifuel ethanol, 12 bifuel LPG, 13 bifuel CNG, 14 bifuel propane, 15 bifuel electricity, 16 bifuel electric+combustion, 17 hybrid gasoline, 18 hybrid ethanol, 19 hybrid diesel, 20 hybrid electric, 21 hybrid electric+combustion, 22 hybrid regenerative, 23 bifuel diesel; "Any other value is reserved by ISO/SAE". (src: W; ISO5 Table B.62 for 01–0F, "10 – FF ISO/SAE reserved"). ISO5 note: a gasoline car with < 10 % ethanol reports $09 (bi-fuel gasoline) and PID 52 ≤ 10 %.

##### 4.6 PID 5F emission requirements (state encoded, 1 byte)
`0x0E` = Heavy Duty Vehicles (EURO IV) B1, `0x0F` = Heavy Duty Vehicles (EURO V) B2, `0x10` = Heavy Duty Vehicles (EURO EEV) C, "All Others = Reserved" (src: DASH; W only says "Bit Encoded" and gives no table). Light-duty cars normally do not support PID 5F.

##### 4.7 PID 65 auxiliary inputs/outputs (2 bytes)
A = supported flags: bit0 PTO status, bit1 auto-trans neutral/drive status, bit2 manual-trans neutral gear status, bit3 glow plug lamp status; bits7-4 reserved. B = states: bit0 PTO (1 = active), bit1 auto trans (0 = park/neutral, 1 = in gear), bit2 manual trans (0 = neutral, 1 = in gear), bit3 glow plug lamp (1 = on). (src: DASH)

##### 4.8 PID 13 / 1D O2 sensor presence
PID 13: A0..A3 = bank 1 sensors 1..4, A4..A7 = bank 2 sensors 1..4 ("Where sensor 1 is closest to the engine"). PID 1D: A0..A7 = B1S1,B1S2,B2S1,B2S2,B3S1,B3S2,B4S1,B4S2. A vehicle supports exactly one of the two. (src: ISO5 Tables B.20/B.24; W)

#### 5. Mode 02 freeze frame (`02 <PID> <frame#>` → `42 <PID> <frame#> <data>`)

- Request = `02 PID FRNO`; up to 3 (PID, frame#) pairs per request (7 bytes; Table 137 "#2 PID#1, #3 frame #, #4 PID#2, #5 frame #, #6 PID#3, #7 frame #"). Response = `42` then records `[PID][FRNO][data A..D]`, "data B - D depend on selected PID", data length per PID as in Mode 01. (src: ISO5 Tables 137/138)
- Frame # `0x00` = the (first/mandatory) freeze frame; "The frame number identifies the freeze frame, which includes emission-related data values in case an emission-related DTC is detected by the ECU". (src: ISO5 §7.2.3.3; example Table 139: `02 02 00`)
- PID 02 returns the 2-byte DTC that caused the freeze frame, decoded exactly as Mode 03 bytes (Table 140 example `42 02 00 01 30` = P0130); `00 00` = no freeze frame stored ("If no freeze frame data are stored, then the parameter value of PID $02 … is set to $00 00. If the external test equipment requests a PID excluding $00, $02, $20, $40, etc., the ECU shall not send a response message"). (src: ISO5 §7.2.4.2, Tables 140/144; W: "PID $02 is used to obtain the DTC that triggered the freeze frame")
- Worked example (ISO5 Tables 141/142): request `02 0C 00 05 00 04 00` → response `42 0C 00 20 80 04 00 80 05 00 28` (2080 rpm, load 50.2 %, ECT 0 °C; order of records differs from the request).
- Supported-PID bitmaps for Mode 02 are requested as `02 00 00`, `02 20 00`, … (PID + frame#). (src: ISO5 Table 135)
- PID 01 is Mode 01 only; PID 02 is Mode 02 only. (src: W services table rows for 01/02)

#### 6. Modes 03 / 07 / 0A (DTCs) and Mode 04 (clear)

- Requests are the bare SID: `03`, `07`, (`0A`). CAN response: `43 <#DTC> [DTC_hi DTC_lo]…` — Table 146: "#2 # of DTC = [no emission-related DTCs stored 00, emission-related DTCs stored 01 - FF]", "C = Conditional — DTC#1 - DTC#m are only included if # of DTC parameter value ≠ $00". Same for `47` (Table 172). Example: ECM with six DTCs → `43 06 01 43 01 96 02 34 02 CD 03 57 0A 24`; ABS with none → `43 00`; TCM → `43 01 04 43` (P0443). (src: ISO5 Tables 146–150, 172; PYOBD protocol_can.py comment "43 03 11 11 22 22 33 33 / [DTC] [DTC] [DTC]" with `num_dtc_bytes = message.data[1] * 2`; ELM: "the ISO 15765-4 (CAN) protocol is very similar, but it adds an extra data byte (in the second position), showing how many data items (DTCs) are to follow")
- Mode 03 = "confirmed" DTCs; Mode 07 = "pending" ("detected during current or last completed driving cycle … Service $07 is required for all DTCs and is independent of Service $03 … reported in the same format as the DTCs in Service $03"); Mode 0A = permanent DTCs — existence verified: W services table "0A Permanent Diagnostic Trouble Codes (DTCs) (Cleared DTCs)"; ELM mode list "0A - request permanent trouble codes"; ISO 15031-5:2011 TOC "8.10 Service 0x0A — Request emission-related diagnostic trouble codes with permanent status" (p.127, CAN section). ELM on Mode 04: it does "not erase permanent (mode 0A) trouble codes (these are reset by the ECU only)". The 0A payload format is in REPORTED. (src: ISO5 §7.7.1; W; ELM; ISO5-2011 TOC)
- Recommended sequence (ISO5 §6.3.1, two-step process): "Step 1: Send a Service $01, PID $01 request to get the number of emission-related DTCs from all ECUs … Step 2: Send a Service $03 request … If additional DTCs are set between the time that the number of DTCs are reported by an ECU, and the DTCs are reported by an ECU, then the number of DTCs reported could exceed the number expected … In this case, the external test equipment shall repeat this cycle until the number of DTCs reported equals the number expected based on the Service $01, PID $01 response." (On CAN, Table 7 j) additionally requires a `43 00` response from ECUs without DTCs.)
- DTC 2-byte encoding: "The first two (2) bits (high order) of the first (1) byte for each DTC indicate whether the DTC is a Powertrain, Chassis, Body, or Network DTC … The second two (2) bits shall indicate the first digit of the DTC (0 through 3). The second (2) nibble of the first (1) byte and the entire second (2) byte are the next three (3) hexadecimal characters of the actual DTC reported as hexadecimal. A Powertrain DTC transmitted as $0143 shall be displayed as P0143." Category bits: `00` P, `01` C, `10` B, `11` U (W Service 03 table "A7-A6 Category 00: P - Powertrain 01: C - Chassis 10: B - Body 11: U - Network"); worked example `C1 58` → "U0158" (W). ELM first-hex-digit table: 0→P0, 1→P1, 2→P2, 3→P3, 4→C0, 5→C1, 6→C2, 7→C3, 8→B0, 9→B1, A→B2, B→B3, C→U0, D→U1, E→U2, F→U3 ("if the received code was D016, you would replace the D with U1"). (src: ISO5 §6.3.1/§7.3.1; W "Service 03 (no PID required)"; ELM "Interpreting Trouble Codes")
- Meaning of the 2nd character (OBDW): "0 – Indicates a generic (SAE defined) code; 1 – Indicates a manufacturer-specific (OEM) code; 2 – For the 'P' category this indicates a generic (SAE defined) code, For other categories indicates a manufacturer-specific (OEM) code; 3 – For the 'P' category this is indicates a code that has been 'jointly' defined, For other categories this has been reserved for future use". 3rd character for P-codes (OBDW): 0 fuel/air metering & auxiliary emission controls, 1 fuel/air metering, 2 fuel/air metering (injector circuit), 3 ignition systems or misfires, 4 auxiliary emission controls, 5 vehicle speed control and idle control systems, 6 computer and output circuit, 7 transmission, 8 transmission, A–F hybrid trouble codes.

```python
def decode_dtc(hi: int, lo: int) -> str:
    return "PCBU"[hi >> 6] + str((hi >> 4) & 3) + f"{hi & 0xF:X}{lo:02X}"
def parse_dtc_response(payload: bytes):      # payload = bytes after SID 0x43/0x47/0x4A
    n = payload[0]; body = payload[1:1+2*n]
    return [decode_dtc(body[i], body[i+1]) for i in range(0, len(body), 2) if (body[i], body[i+1]) != (0, 0)]
```

- Mode 04: request `04`, response `44` (no data). "All ECUs shall respond to this request message with ignition ON and with the engine not running. For safety and/or technical design reasons, ECUs that can not perform this operation under other conditions, such as with the engine running, shall send a negative response message with response code $22 - conditionsNotCorrect"; `7F 04 78` allowed while clearing (Table 7 n). What it clears (ISO5 §7.4.1, complete list): "MIL and number of diagnostic trouble codes (Service $01, PID $01); Clear the I/M (Inspection/Maintenance) readiness bits (Service $01, PID $01 and $41); Confirmed diagnostic trouble codes (Service $03); Pending diagnostic trouble codes (Service $07); Diagnostic trouble code for freeze frame data (Service $02, PID $02); Freeze frame data (Service $02); Status of system monitoring tests (Service $01, PID $01); On-board monitoring test results (Service $06); Distance travelled while MIL is activated (PID $21); Number of warm-ups since DTCs cleared (PID $30); Distance travelled since DTCs cleared (PID $31); Time run by the engine while MIL is activated (PID $4D); Time since diagnostic trouble codes cleared (PID $4E); Reset misfire counts of standardized Test ID $0B to zero (Service $06). Other manufacturer-specific 'clearing/resetting' actions may also occur". It does not clear permanent (Mode 0A) DTCs (ELM). Send functionally on 0x7DF so every ECU clears. (src: ISO5 §7.4, Tables 151–156; W "Clears all stored trouble codes and turns the MIL off"; ELM)

#### 7. Mode 06 on CAN — on-board monitoring test results

- Supported OBDMIDs: `06 00` (up to six bitmap IDs per request, e.g. `06 00 20 40 60 80 A0`, then `06 C0 E0`), response `46 [MID][A B C D]…` (records only for supported ranges). "The request message including supported On-Board Diagnostic Monitor IDs may contain up to six (6) OBDMIDs. A request message including an On-Board Diagnostic Monitor ID, which reports test values shall only contain one (1) OBDMID. An external test equipment shall not request a combination of OBDMIDs supported and a single OBDMID, which report test values." (src: ISO5 §7.6.1, Tables 157/158)
- Test values: request `06 <OBDMID>` (exactly **one** OBDMID per request); response `46` followed by one or more **9-byte records**: `[OBDMID][S/MDTID][UASID][TV hi][TV lo][MINTL hi][MINTL lo][MAXTL hi][MAXTL lo]` (Table 160 column order "On-Board Diagnostic Monitor ID, Std./Manuf. Defined TID#1, Unit And Scaling ID#1, Test Value (High Byte)#1, Test Value (Low Byte)#1, Min. Test Limit (High Byte)#1, Min. Test Limit (Low Byte)#1, Max. Test Limit (High Byte)#1, Max. Test Limit (Low Byte)#1"). Worked example (Table 168): `46 01 01 0A 0B B0 0B B0 0B B0 01 05 10 00 48 00 00 00 64 01 85 24 00 96 00 4B FF FF` = OBDMID 01 (O2 B1S1): TID 01 UAS 0A value 0x0BB0 → "0,365 V" (min = max = value, constant); TID 05 UAS 10 value 0x48 → "0,072 s", min 0, max 0x64 = "0,100 s"; manufacturer TID 0x85 (133) UAS 24 value 150 counts, min 75, max 65535 ("FF FF"). (src: ISO5 Table 160, Table 168; PYOBD decoders.monitor "look at data in blocks of 9 bytes (one test result)", truncating any non-multiple of 9)
- Not-yet-run monitors report TV = MIN = MAX = `$0000` ("If an On-Board Diagnostic Monitor has not been completed at least once since Clear/reset emission-related diagnostic information or battery disconnect, then the parameters Test Value (Results), Minimum Test Limit, and Maximum Test Limit shall be set to zero ($0000) values"; example Table 170 `46 21 87 2E 00 00 00 00 00 00` — "Monitor not completed at least once since erasure"). (src: ISO5 §7.6.1, Table 170)
- Pass/fail: pass iff `MINTL <= TV <= MAXTL` ("The Test Value shall be within the Minimum and Maximum Test Limit to indicate a 'Pass' result"; Table 165: "if the Test Value is less than the Minimum Test Value results in a 'Fail' condition; if the Test Value equals the Minimum Test Value results in a 'Pass' condition"; Table 166 symmetric for the maximum). "For the Standardized Test IDs that are constant values, the Minimum Test Limit shall be the same value as reported for the Test Value" (and the maximum likewise). (src: ISO5 Tables 164–166)
- "Since some Test IDs for a completed monitor will show incomplete, PID $41 must be used to determine monitor completion status." (src: ISO5 §7.6.1)
- OBDMID table (ISO5 Annex D, Table D.1, re-read in full): `00` supported 01–20; `01..10` Oxygen Sensor Monitor B1S1,B1S2,B1S3,B1S4,B2S1..B2S4,B3S1..B3S4,B4S1..B4S4; `11–1F` reserved; `20` supported 21–40; `21..24` Catalyst Monitor Bank 1..4; `25–30` reserved; `31..34` EGR Monitor Bank 1..4; `35–38` reserved in ISO5:2006 (= VVT Monitor Bank 1..4 in PYOBD commands `MONITOR_VVT_B1..B4` / later J1979); `39` EVAP Monitor (Cap Off) (PYOBD: "Cap Off / 0.150\""), `3A` EVAP (0,090"), `3B` EVAP (0,040"), `3C` EVAP (0,020"), `3D` Purge Flow Monitor; `3E–3F` reserved; `40` supported 41–60; `41..50` Oxygen Sensor Heater Monitor B1S1..B4S4 (same order as 01..10); `51–5F` reserved; `60` supported 61–80; `61..64` Heated Catalyst Monitor Bank 1..4; `65–70` reserved; `71..74` Secondary Air Monitor 1..4; `75–7F` reserved; `80` supported 81–A0; `81..84` Fuel System Monitor Bank 1..4; `85–9F` reserved in ISO5:2006 (PYOBD/later J1979: `85`,`86` Boost Pressure Control Monitor Bank 1/2; `90`,`91` NOx Absorber Monitor Bank 1/2; `98`,`99` NOx Catalyst Monitor Bank 1/2; GM6 uses OBDMIDs `85` ("Turbocharger Vane Position …", "Monitoring for Underboost/Overboost"), `90` ("Nox Trap Efficiency Below Threshold Bank 1") and `98`); `A0` supported A1–C0; `A1` Misfire Monitor General Data; `A2..AD` Misfire Cylinder 1..12 Data; `AE–BF` reserved in ISO5:2006 (PYOBD: `B0`,`B1` PM Filter Monitor Bank 1/2; GM6 uses `B2` and `B3` "Particulate Filter … Bank 2"); `C0` supported C1–E0; `C1–DF` reserved; `E0` supported E1–FF; `E1–FF` "Vehicle manufacturer defined OBDMIDs". Annex D also notes "The cylinder most remote of the flywheel is defined as cylinder number 1".
- Standardized TIDs (ISO5 Table 161; PYOBD codes.TEST_IDS has the same 12 names): `00` reserved, `01` rich-to-lean sensor threshold voltage (constant), `02` lean-to-rich threshold voltage (constant), `03` low sensor voltage for switch time calculation (constant), `04` high sensor voltage for switch time calculation (constant), `05` rich-to-lean sensor switch time (calculated), `06` lean-to-rich sensor switch time (calculated), `07` minimum sensor voltage for test cycle (calculated), `08` maximum sensor voltage for test cycle (calculated), `09` time between sensor transitions (calculated), `0A` sensor period (calculated), `0B` "EWMA (Exponential Weighted Moving Average) misfire counts for last ten (10) driving cycles (calculated, rounded to an integer value) … 0,1 * (current misfire counts) + 0,9 * (previous misfire counts average) … This TEST ID shall be reported with OBD Monitor IDs $A2 – $AD … and the Scaling ID $24", `0C` "Misfire counts for last/current driving cycles", `0D–7F` reserved for future standardization, `80–FE` Manufacturer Defined Test ID range (Table 162), `FF` reserved.
- UASID table (ISO5 Annex E, every row re-read; value = raw16 × scale (+ offset); "$01 - $7F are unsigned Scaling Identifiers, and $80 - $FE are signed Scaling Identifiers. Unit and Scaling IDs $00 and $FF are ISO/SAE reserved"; signed = two's complement, $8000 = minimum):

| UASID | unit | scale/bit | notes |
|---|---|---|---|
| 01 | raw | 1 | |
| 02 | raw | 0.1 | |
| 03 | raw | 0.01 | |
| 04 | raw | 0.001 | |
| 05 | raw | 0.0000305 | max 1.999 |
| 06 | raw | 0.000305 | max 19.988 |
| 07 | rpm | 0.25 | max 16384 |
| 08 | km/h | 0.01 | |
| 09 | km/h | 1 | |
| 0A | V | 0.000122 (0.122 mV) | max 7.99 V |
| 0B | V | 0.001 | |
| 0C | V | 0.01 | |
| 0D | mA | 0.00390625 | max 255.996 mA |
| 0E | A | 0.001 | |
| 0F | A | 0.01 | |
| 10 | ms | 1 | |
| 11 | s | 0.1 (100 ms) | |
| 12 | s | 1 | |
| 13 | mΩ | 1 | |
| 14 | Ω | 1 | |
| 15 | kΩ | 1 | |
| 16 | °C | 0.1, **offset −40** | "0000 = −40 °C, FFFF = +6513.5 °C" |
| 17 | kPa | 0.01 | gauge |
| 18 | kPa | 0.0117 | air pressure, max 766.76 |
| 19 | kPa | 0.079 | fuel pressure, max 5177.27 |
| 1A | kPa | 1 | gauge |
| 1B | kPa | 10 | diesel pressure, max 655350 |
| 1C | ° | 0.01 | |
| 1D | ° | 0.5 | |
| 1E | λ | 0.0000305 | max 1.999 ($8013 ≈ 1.000) |
| 1F | A/F ratio | 0.05 | max 3276.75 |
| 20 | ratio | 0.0039062 | max 255.993 |
| 21 | Hz | 0.001 (1 mHz) | |
| 22 | Hz | 1 | |
| 23 | kHz | 1 | |
| 24 | counts | 1 | |
| 25 | km | 1 | |
| 26 | V/ms | 0.0001 (0.1 mV/ms) | max 6.5535 |
| 27 | g/s | 0.01 | |
| 28 | g/s | 1 | |
| 29 | Pa/s | 0.25 | max 16.384 kPa/s |
| 2A | kg/h | 0.001 | |
| 2B | switches | 1 | |
| 2C | g/cyl | 0.01 | |
| 2D | mg/stroke | 0.01 | |
| 2E | bool | "state encoded 0000 false 0001 true" | **ISO5:2006 is internally inconsistent: Table 170 labels UASID 2E "Percent … 0,00 %"** (presumably meaning 2F); python-OBD decodes 2E as `any(bool(x) for x in bytes)` |
| 2F | % | 0.01 | |
| 30 | % | 0.001526 | FFFF = 100.00 % |
| 31 | L | 0.001 | |
| 32 | inch | 0.0000305 | max 1.999 in |
| 33 | λ | 0.00024414 | $1000 = 1.00 λ, max 15.99976 |
| 34 | min | 1 | |
| 35 | s | 0.01 (10 ms) | |
| 36 | g | 0.01 | |
| 37 | g | 0.1 | |
| 38 | g | 1 | |
| 39 | % | 0.01, **offset −327.68** | "0000 = −327.68 %, FFFF = +327.67 %" (unsigned raw with offset) |
| 81 | raw, signed | 1 | |
| 82 | raw, signed | 0.1 | |
| 83 | raw, signed | 0.01 | |
| 84 | raw, signed | 0.001 | |
| 85 | raw, signed | 0.0000305 | ±0.999 |
| 86 | raw, signed | 0.000305 | ±9.994 |
| 8A | V, signed | 0.000122 | ±3.9977 V |
| 8B | V, signed | 0.001 | |
| 8C | V, signed | 0.01 | |
| 8D | mA, signed | 0.00390625 | ±128 mA |
| 8E | A, signed | 0.001 | |
| 90 | ms, signed | 1 | |
| 96 | °C, signed | 0.1 | $8000 = −3276.8 °C (no offset; $FE70 = −40 °C) |
| 9C | °, signed | 0.01 | |
| 9D | °, signed | 0.5 | |
| A8 | g/s, signed | 1 | |
| A9 | Pa/s, signed | 0.25 | ±8192 |
| AF | %, signed | 0.01 | $D8F0 = −100 % |
| B0 | %, signed | 0.003052 | ±100 % |
| B1 | mV/s, signed | 2 | |
| FD | kPa, signed | 0.001 | absolute |
| FE | Pa, signed | 0.25 | |

  Additional UASIDs not in ISO5:2006 but present in PYOBD `UAS_IDS` (and several confirmed in use by GM6): `3A` g 0.001, `3B` g 0.0001, `3C` µs 0.1 (GM6: "0.1 µs / bit"), `3D` mA 0.01, `3E` mm² 0.00006103516, `3F` L 0.01 (PYOBD only — GM6 does **not** use 3F), `40` ppm 1, `41` µA 0.01 (GM6: "0 to 655.35 uAmps 0.01 uAmps / bit"), `87` ppm signed 1, `99` kPa signed 0.1, `AD` mg/stroke signed 0.01, `AE` mg/stroke signed 0.1, `FC` kPa signed 0.01 (GM6: "-327.68 to +327.67 kPa 0.01 kPa / bit"); GM6 additionally uses `8F` = "1 µs / bit" signed (−32768..32767 µs) and `FB` = "10 kPa / bit" signed (−327680..+327670 kPa), neither of which is in PYOBD. (src: PYOBD UnitsAndScaling.py; GM6)

```python
UAS = {0x01:(1,0,"raw"), 0x0A:(0.000122,0,"V"), 0x10:(1,0,"ms"), 0x16:(0.1,-40,"degC"), 0x24:(1,0,"counts"), ...}
def uas_apply(uasid: int, raw: int) -> float:
    scale, offset, unit = UAS[uasid]
    if uasid & 0x80 and raw > 0x7FFF: raw -= 0x10000
    return raw*scale + offset
def parse_mode06(payload: bytes):   # payload = bytes after 0x46
    for i in range(0, len(payload) - len(payload) % 9, 9):
        mid, tid, uas = payload[i], payload[i+1], payload[i+2]
        tv, mn, mx = (int.from_bytes(payload[i+3+2*k:i+5+2*k], "big") for k in range(3))
        yield mid, tid, uas, uas_apply(uas,tv), uas_apply(uas,mn), uas_apply(uas,mx), (mn <= tv <= mx)
```
(python-OBD compares raw values; comparing scaled values is equivalent for monotonic scalings. For signed UASIDs compare the sign-extended raw values, not the unsigned ones.)

- Mode 05 is K-line/J1850 only: W services table "05 Test results, oxygen sensor monitoring (non CAN only)" and "06 Test results, other component/system monitoring (Test results, oxygen sensor monitoring for CAN only)"; on CAN the O2 results come from Mode 06 OBDMIDs 01–10. (src: W; ISO5 §6.6.1 "This service can be used as an alternative to Service $05 to report oxygen sensor test results")

#### 8. Mode 08 (control of on-board system/test/component)

- Supported TIDs: `08 00` (bitmaps as usual, "may contain up to six (6) Test IDs") → `48 00 A B C D`. "The order of the TIDs in the response message is not required to match the order in the request message." (src: ISO5 §7.8.1, Tables 173/174)
- Only one standardized TID exists: **TID $01 Evaporative system leak test** ("This service enables the conditions required to conduct an evaporative system leak test, but does not actually run the test. An example is to close a purge solenoid, preventing leakage if the system is pressurized"); `$02 – $FF ISO/SAE reserved`. On CAN: request `08 01` with no data bytes ("For ISO 15765-4 protocol, DATA_A - DATA_E shall not be included in the request and response message"), positive response `48 01` (Table 178); conditions not correct → `7F 08 22` ("If the conditions are not proper to run the test, the vehicle shall respond with a negative response message with a response code $22"; Table 180). (src: ISO5 Annex F Table F.1, Tables 177–180)
- General CAN format allows `08 TID [A..E]` / `48 TID [A..E]` with up to 5 data bytes ("Presence and values of Data A - E parameter depend on Test ID"), "A request message including a Test ID with optional data shall only contain one (1) Test ID". (src: ISO5 Tables 175/176)
- It is a gasoline/EVAP function; neither VW is likely to support it beyond TID 01 (see REPORTED).

#### 9. Mode 09 (vehicle information) on CAN

- Supported InfoTypes: `09 00` (up to 6 bitmap IDs) → `49 00 A B C D` (records). (src: ISO5 §7.9.1, Tables 181/182)
- Data: request `09 <INFOTYPE>` (one per request: "A request message including an InfoType, which reports vehicle information shall only contain one (1) Infotype"); response `49 <INFOTYPE> <NODI> <data…>` (Table 184: "#2 InfoType, #3 NOfDataItems (NODI), #4 data #1 … #m data #m") where **NODI = number of data items** ("A request message with the InfoType for CVN … may cause the ECU to send a response message that contains multiple CVNs. The amount of CVNs is included in the 'Number of data items' parameter. For InfoType $08, In-use Performance Tracking, there are 16 data items specified in Annex G. Therefore, the parameter number of data items shall have a value of 16 (dec)"). (src: ISO5 Table 184, §7.9.3.3)
- The odd "message count" InfoTypes (01, 03, 05, 07, 09) are for K-line/J1850 only: "For ISO 15765-4, support for this parameter is not recommended/required for the ECU and the external test equipment. The response message format is not specified." (src: ISO5 Annex G Tables G.1/G.3/G.5/G.7/G.9; W rows 01/03/05/07/09 "Only for ISO 9141-2, ISO 14230-4 and SAE J1850")
- InfoType 02 VIN: `49 02 01` + 17 ASCII bytes in one ISO-TP message ("For ISO 15765-4, there is only one response message, which contains all VIN characters without any filling bytes"); example Table 186 `49 02 01 31 47 31 4A 43 35 34 34 34 52 37 32 35 32 33 36 37` = "1G1JC5444R7252367". ELM CAN example (headers off, 20 bytes = `49 02 01` + 17): `014` / `0: 49 02 01 31 44 34` / `1: 47 50 30 30 52 35 35` / `2: 42 31 32 33 34 35 36`. "If INFOTYPE $02 (VIN) is indicated as supported, the ECU shall respond within P2max timing even if the VIN is missing or incomplete. For example, a development ECU may respond with $FF characters for VIN because the VIN has not been programmed." (src: ISO5 Table G.2, Table 186, §7.9.1; ELM p.44; W: "17-char VIN, ASCII-encoded")
- InfoType 04 CALID: `49 04 <n>` + n × 16 ASCII bytes, "Calibration identifications can include a maximum of sixteen (16) characters … Any unused data bytes shall be reported as $00 and filled at the end of the calibration identification … Vehicle controllers that contain calibration identifications shall store and report sixteen (16) ASCII-character calibration identifications, even though they may not use all sixteen (16) characters"; example Table 188: `49 04 02` + "JMB*36761500" `00 00 00 00` + "JMB*4787261111" `00 00`. ELM CAN example (two ECUs): `7E8 10 13 49 04 01 35 36 30 / 7E8 21 32 38 39 34 39 41 43 / 7E8 22 00 00 00 00 00 00 31` and the same from 7E9 (0x13 = 19 bytes = `49 04 01` + 16; note the FF/CF frames of the two ECUs interleave on the bus, so reassembly must be keyed by CAN ID). (src: ISO5 Table G.4, Table 188; ELM p.45)
- InfoType 06 CVN: `49 06 <n>` + n × 4 bytes ("4 byte hex (most significant byte reported as Data A)"; "If the calculation technique does not use all four (4) bytes, the CVN shall be right justified and filled with $00"); "The CVN (or group of CVNs) assigned to a CALID shall be reported in the same order as the CALIDs are reported". Two methods: #1 precomputed per trip and stored in NVM, #2 computed on request; in both, "If the CVN(s) are requested before they have been computed, a negative response message with response code $78 … shall be sent by the ECU(s) until the positive response message is available". Example Tables 190/192/193: `7F 09 78` … `49 06 02 17 91 BC 82 16 E0 62 BE` (ECU #1), `49 06 01 98 12 34 76` (ECU #2). (src: ISO5 Table G.6, Tables 189–193)
- InfoType 08 IPT (spark ignition): `49 08 10` + 16 × u16 big-endian ("32 bytes … unsigned numeric (most significant byte reported as Data A)") in this order: OBDCOND, IGNCYCCNTR, CATCOMP1, CATCOND1, CATCOMP2, CATCOND2, O2SCOMP1, O2SCOND1, O2SCOMP2, O2SCOND2, EGRCOMP, EGRCOND, AIRCOMP, AIRCOND, EVAPCOMP, EVAPCOND (worked example Table 195 `49 08 10 04 00 0D 09 03 38 03 B1 …` = OBDCOND 1024, IGNCYCCNTR 3337, CATCOMP1 824, CATCOND1 945, …). "Data values, which are not implemented (e.g. bank 2 of the catalyst monitor of a 1-bank system) shall be reported as $0000. If a vehicle utilizes Variable Valve Timing (VVT) in place of EGR, the VVT in-use data shall be reported in place of the EGR in-use data." Newer J1979 appends SO2SCOMP1, SO2SCOND1, SO2SCOMP2, SO2SCOND2 (20 items, NODI 0x14) (src: ISO5 Table G.8, Table 195; W "Service 09 PID 08" list of 20 mnemonics and row 08 "4 or 5 messages, each one containing 4 bytes (two values)", row 07 "8 if sixteen values … 9 if eighteen … 10 if twenty values").
- InfoType 0A ECUNAME: `49 0A 01` + 20 bytes: "Data bytes 1-4, 'XXXX', contains ECU acronym; Data byte 5, '-', ($2D) contains delimiter; Data bytes 6-20, 'YYYYYYYYYYYYYYY', contains text name … any unused bytes shall be filled with $00 … All non-zero hex bytes … are left justified within each field"; e.g. `45 43 4D 00 2D 45 6E 67 69 6E 65 20 43 6F 6E 74 72 6F 6C 00` = "ECM-Engine Control", `41 42 53 31 2D 41 6E 74 69 6C 6F 63 6B 20 42 72 61 6B 65 31` = "ABS1-Antilock Brake1". Standard acronyms (Table G.10): ABS, AFCM, AHCM, BECM, BSCM, CCM, CTCM, DMCM, ECCI, ECM, FACM, FICM, FPCM, FWDC, GPCM (Glow Plug Control Module), GSM, HPCM, IPC, PCM, SGCM, TACM, TCCM, TCM, UDM (Urea Dosing Control Module). (src: ISO5 Table G.10, Table 197)
- InfoType 0B IPT (compression ignition): 18 × u16 in order OBDCOND, IGNCNTR, HCCATCOMP, HCCATCOND, NCATCOMP, NCATCOND, NADSCOMP, NADSCOND, PMCOMP, PMCOND, EGSCOMP, EGSCOND, EGRCOMP, EGRCOND, BPCOMP, BPCOND, FUELCOMP, FUELCOND (W row 0B: "5 messages, each one containing 4 bytes (two values)") → on CAN expect `49 0B 12` + 36 bytes. (src: W "Service 09 PID 0B"; ISO5:2006 Table G.11 lists "0B – FF ISO/SAE reserved")
- InfoTypes 0C–FF: reserved in ISO5:2006 (Table G.11); later J1979 adds e.g. ESN/EROTAN (names only, see REPORTED).

```python
def parse_mode09(payload: bytes):      # after 0x49
    infotype, nodi, data = payload[0], payload[1], payload[2:]
    if infotype == 0x02: return data[:17].decode("ascii", "replace")
    if infotype == 0x04: return [data[16*i:16*i+16].rstrip(b"\0").decode("ascii","replace") for i in range(nodi)]
    if infotype == 0x06: return [data[4*i:4*i+4].hex().upper() for i in range(nodi)]
    if infotype in (0x08, 0x0B): return [int.from_bytes(data[2*i:2*i+2],"big") for i in range(nodi)]
    if infotype == 0x0A: return data[:4].rstrip(b"\0").decode() + "-" + data[5:20].rstrip(b"\0").decode()
```

#### 10. Readiness semantics relevant to the two cars (verified generic facts)

- Compression-ignition readiness bits (PID 01 byte C/D with B3 = 1): bit0 NMHC catalyst, bit1 NOx/SCR aftertreatment, bit3 boost pressure, bit5 exhaust gas sensor, bit6 PM filter, bit7 EGR/VVT; bits 2 and 4 reserved. Spark ignition: bit0 catalyst, bit1 heated catalyst, bit2 EVAP, bit3 secondary air, bit4 GPF (W) / A/C refrigerant (ISO5:2006), bit5 O2 sensor, bit6 O2 heater, bit7 EGR/VVT. (src: W tables, section 4.1)
- "Misfire monitoring shall always indicate complete for spark-ignition engines. Misfire monitoring shall indicate complete for compression-ignition engines after the misfire evaluation is complete. Fuel system monitoring shall always indicate complete for both spark-ignition and compression-ignition engines. Comprehensive component monitoring shall always indicate complete on both spark-ignition and compression-ignition engines." (src: ISO5 Table B.2)
- "Fuel system monitoring shall be supported on vehicles that utilize oxygen sensors for closed loop fuel feedback control, and utilize a fuel system monitor, typically spark-ignition engines." "Misfire monitoring shall be supported on both spark-ignition and compression-ignition vehicles if the vehicle utilizes a misfire monitor." (src: ISO5 Table B.2)
- US-market EA189 2.0 TDI aftertreatment split (WVU/ICCT test vehicles, model years 2012/2013): "Vehicle A Volkswagen Jetta 2.0 TDI … Fitted with a lean-NOx trap (LNT) emission treatment system"; "Vehicle B Volkswagen Passat 2.0 TDI … Fitted with the same engine as Vehicle A, but with a urea-based selective catalytic reduction (SCR) emission treatment system." (src: VWS table "WVU measurement"). The 2012 Golf TDI uses the same CJAA engine/aftertreatment as the Jetta TDI — that equivalence is REPORTED (own knowledge), see below.
- Diesel-specific Mode 01 PIDs exist for the CJAA class of engine: 23 (rail gauge pressure ×10 kPa), 5E (fuel rate), 61–64 (torque), 6B (EGR temp), 6D (rail pressure control), 6F/70 (turbo inlet / boost control), 71 (VGT), 73 (exhaust pressure), 74 (turbo rpm), 78 (EGT bank 1), 7A/7B (DPF ΔP), 7C (DPF temperature), 7F (engine run time), 83 (NOx sensor), 8B (aftertreatment status incl. DPF regen in progress and NOx adsorber regen/desulfurization), 92 (fuel system control status CI). Whether EDC17CP14 in a MY2012 US Golf implements any of 0x61+ must be read from the 0x60/0x80 bitmaps (OPEN QUESTIONS).
- Project-verified UDS physical IDs on these cars (CLAUDE "Verified protocol facts"): "Bus: 500 kbps, 11-bit IDs. Engine 0x7E0→0x7E8, TCU 0x7E1→0x7E9, Haldex 0x70F→0x779, ABS 0x713→0x77D, gateway 0x710→0x77A. Functional broadcast 0x7DF." (Whether the TCU answers *OBD* services on 0x7E9 is a separate, open question.)

---

### Reported / unverified (confidence)

- **Mode 0A (permanent DTCs) payload format** `4A <#DTC> [DTC…]`, identical to Mode 03/07 on CAN. The *existence* of Service 0A in the CAN section of ISO 15031-5:2011 (§8.10, 2 pages) is verified from the TOC; the message tables are not in the free preview. Confidence: **high** (W lists service 0A; ELM lists "0A - request permanent trouble codes" and says Mode 04 does not erase them; python-OBD does not implement it). Confirm with a trace on the 2012 TDI (CARB required permanent-DTC reporting from MY2010, so the TDI should answer; the 2008 R32 probably returns nothing). What would confirm: ISO 15031-5:2011 §8.10 Table or a CAN capture showing `4A nn …`.
- **Padding byte VW ECUs transmit**: VAG ECUs are widely believed to pad diagnostic frames with **0xAA**. Confidence: **low–medium** (common knowledge from VCDS traces, no document fetched; the open-source VW_Flash tool shows only the *tester* side, 0x55). Confirm from any CAN capture of the car's responses (look at bytes after the PCI length in a `41 00` SF). Tester side: 0x55 is proven acceptable to VW Simos/DSG ECUs by VW_Flash (VERIFIED above); 0x00 and 0xCC are expected to work too but are not demonstrated for these ECUs.
- **No 29-bit OBD on either car**: both are 11-bit, 500 kbit/s, ECM at 0x7E0/0x7E8, TCM (DQ250 "02E" DSG) at 0x7E1/0x7E9 and the DSG does respond to functional 0x7DF Service 01 PID 00 and Mode 03/07 (gearbox DTCs are emissions-relevant). Confidence: **high** for 11-bit/500k and the UDS IDs (CLAUDE.md verified facts match ISO4 recommendations), **medium** for the DSG answering OBD services. A web search found no primary source either way. Confirm: send `7DF 02 01 00` and record all 0x7E8..0x7EF responders.
- **2008 R32 (BUB, ME7.1.1)**: spark ignition (B3 = 0); PID 13 expected `0x33` (B1S1,B1S2,B2S1,B2S2: two pre-cat wideband sensors and two post-cat narrowband sensors; the VR6 is treated as two banks); Mode 06 OBDMIDs expected 01,02,05,06 (O2), 21,22 (cat), 39–3D (EVAP, US car), 41,42,45,46 (heaters), 71 (secondary air, if fitted), 81,82 (fuel), A1–A7 (misfire, 6 cylinders). ME7.1.1 is an older Bosch ECU (2002-era design) that may support only Mode 01/02/03/04/06/07/09(02,04,06) with no 0x41+ PIDs. Confidence: **medium** (own knowledge). Confirm with PID 00/20/40 bitmaps and `06 00 20 40 60 80 A0`.
- **2012 Golf TDI (CJAA, EDC17CP14)**: compression ignition (B3 = 1). Aftertreatment = DOC + DPF + **NOx storage catalyst (LNT/NSC)**, dual-circuit (HP+LP) EGR, **no SCR/urea**. The LNT-vs-SCR split between the Jetta/Golf-class and the Passat is now VERIFIED for the Jetta 2.0 TDI (VWS); that the 2012 Golf TDI carries the identical CJAA engine and LNT package as the Jetta TDI is own knowledge. Confidence: **high**. Consequences: PID 01 byte C should show NMHC cat, NOx aftertreatment (the LNT monitor is reported under the "NOx/SCR" bit), boost, exhaust gas sensor, PM filter, EGR supported; PID 85/88/94 (reagent/SCR) and Mode 06 OBDMID 98/99 (NOx catalyst) are not expected, OBDMID 90/91 (NOx adsorber) and B0 (PM filter) are plausible; PID 13 likely `0x03` (wideband B1S1 + B1S2) or `0x01`. Confidence for the PID-level predictions: **low–medium**; must be read from the bitmaps.
- **Mode 06 misfire on diesel**: EDC17 may report A1–A5 with TID 0B/0C; CARB diesel misfire monitoring in 2012 was limited, so A2–A5 may be absent. Confidence: **low**.
- **Mode 09 on VW**: InfoType 02 VIN, 04 CALID (VW reports the software part number/version string, e.g. "03L906018xx ####" format), 06 CVN (one or more 4-byte values), 08 (R32) / 0B (TDI) IPT, 0A ECUNAME ("ECM-EngineControl" or similar) are typically supported; CVN on Bosch ECUs is usually available immediately (method #1) but may answer `7F 09 78` first. Confidence: **medium**. Confirm with `09 00`.
- **IPT NODI values**: 0x10 (16 items) or 0x14 (20 items) for InfoType 08; 0x12 (18 items) for 0B. Confidence: **high** for 16 (ISO5 §7.9.3.3 "shall have a value of 16"), **high** for 18 (W item list + "5 messages"), **medium** for the 20-item spark variant (W says "4 or 5 messages"). Parser must use NODI, not a fixed length.
- **Later InfoTypes** (J1979-DA, not fetched): 0x0C ESN engine serial number, 0x0D EROTAN exhaust regulation or type approval number, 0x12 FEOCNTR counters, 0x14 EVAP distance, etc. Names only; byte layouts unknown. Confidence: **low**. Neither 2008 nor 2012 VW is expected to support them.
- **PID 1C values 14–16**: the ISO5:2006 assignments (EURO IV B1 / EURO V B2 / EURO EEC C) were later moved to PID 5F and the slots reassigned (14 = OBD+EOBD+KOBD, …) as listed in W. Confidence: **high** that the current J1979-DA matches W (DASH's PID 5F table reproduces exactly the three moved values). For decoding a 2008/2012 VW the practical values are 1 (OBD-II CARB) for US cars, 6/7 for EU cars.
- **ISO 15765-4:2016 edition** also defines CAN FD / OBDonUDS variants and explicitly lists the padding value as "not specified"; ISO 15765-2:2016 recommends 0xCC. Confidence: **medium** (summarised by W/PYUDS, both of which were fetched and do say 0xCC; the 2016 ISO texts themselves were not fetched).
- **PID 0x9D (engine fuel rate, 4 bytes) / 0x9E (exhaust flow, 2 bytes)**: formulas **unknown**, not in any fetched source (W/CSS give unit only, DASH marks them reserved). Confidence: **low**; do not implement formulas, only raw dump.
- **PID 0x68 byte count**: W says 3 bytes (2 sensors), DASH says 7 bytes (6 sensors). The ECU's actual response length decides; a multi-PID walker should not include 0x68 in combined requests until the length is confirmed. Confidence: **medium** that DASH reflects the current J1979-DA.
- **PID 4F bytes B/C/D as scaling overrides**: ISO5:2006 B.60 (fetched) only defines the Data A rule for λ; W says B/C/D are the maxima for O2 voltage (V), O2 current (mA) and MAP (D×10 kPa). Whether a non-zero B/C/D is meant to rescale PIDs 24–2B (voltage), 34–3B (current) and 0B is **not stated** in the fetched text. Confidence: **medium** that later J1979 editions apply the same "divide by 65535 / 255" rule. Implement only the Data A (λ) and PID 50 (MAF) overrides; log 4F B/C/D.
- **Mode 04 behaviour on the DSG**: a DSG that answers Mode 03 should also answer `44` (or `7F 04 22` with engine running). Confidence: **medium**.

---


---

## 7. VAG application layer

Everything Volkswagen-specific that sits on top of §2–§6: how modules are named and addressed, what their
identification records look like, how measuring values and fault codes are encoded, and how the owner-level
functions map onto services. Sub-sections keep the two-list structure.


### 7.1 Addressing model and VCDS address words

Source sheet: `addresses.md` §A/§B (38 of 38 URLs re-fetched). The three address namespaces, VCDS/ODIS address words and names, Ross-Tech gateway-coding names, the complete numeric 01..7F / 91..A3 / B0..B6 list.

#### Verified (source)

**The single most important finding:** there are THREE independent address namespaces on a PQ35
car, and only one of them is the familiar VCDS "address word":

| namespace | example for the instrument cluster | where it is used |
|---|---|---|
| VCDS/ODIS **address word** (the "17" in "17-Instruments") | `0x17` | human UI, label files, the gateway installation list |
| **TP 2.0 logical address** (byte 0 of the `0x200` channel-setup frame) | `0x07` (reported, single forum post), NOT `0x17` | KWP2000-over-CAN modules |
| **UDS/ISO-TP CAN ID pair** | `0x714` → `0x77E` | UDS modules |

The task brief assumed "TP 2.0 logical address == address word". That is only true for some
modules (engine `0x01` is verified); for the gateway it is `0x1F` not `0x19`, for the EPS it is
`0x09` not `0x44`, and for the Mk5 Haldex it is `0x0A` not `0x22` (OpenHaldex-C6 explicitly reports
that `0x22` did NOT answer). See VERIFIED §D and OPEN QUESTIONS §1. The implementer must not
hard-code "logical = address word"; use the gateway's installed-module list (KWP `1A 9F`, format
unknown) and/or a probe of all 256 destination bytes, identifying each responder by `1A 9B`.

##### A. Addressing model — primary/open-source sources

- VW uses its own transport, **TP 2.0**, under KWP2000 on CAN: "Typically the payload of TP 2.0 will be ISO 14230-3, Keyword Protocol 2000 (KWP2000) application layer messages." (src: https://jazdw.net/tp20) — re-fetched, exact sentence present. The page itself warns: "I have not had any access to the official documentation from VW so take any information with a grain of salt."
- TP 2.0 channel setup is a 7-byte frame on CAN ID **0x200**; the reply comes on **0x200 + destination logical address**: "The channel setup request message should be sent from CAN ID 0x200 and the response will sent with CAN ID 0x200 + the destination modules logical address e.g. for the engine control unit (0x01) the response would be 0x201." (src: https://jazdw.net/tp20)
- Same statement from a second implementation: "This is done on the broadcast address of 0x200. We expect a reply on 0x200 + module logial address." (src: https://raw.githubusercontent.com/pd0wm/pq-flasher/master/tp20.py — re-fetched, verbatim)
- **[added in verification]** A third, independent implementation (Python, J2534) encodes the same rule and cites a VW document "TP2.0_1_1" by section: `CAN_ID_SETUP_REQUEST = 0x200`, `CAN_ID_SETUP_RESPONSE_BASE = 0x200  # Response is 0x200 + destination logical address` with comment "(TP2.0_1_1 §4.1)". Its static parameters, attributed to "TP2.0_1_1 §5.1": `T_E_MS = 50` (connection-setup timeout), `TN_MS = 50` (network latency), `MNTC = 10` (max repetitions of connection setup; "11 total attempts"), `MNT = 2` (max ACK retries on T1 timeout), `MNCT = 5` (max channel-test timeouts), `T_CT_AKTIV_MS = 1000` (connection-test timer), `T_CT_PASSIV_MS = 1050`, `T_WAIT_MS = 100` (delay after RNR), `MNTB = 5` (max block retransmits), block size range "0 < BS < 16" (`BS_MIN = 1`, `BS_MAX = 15`), TPDU priority CA/CT > BR > ACK > DT/CS/DC. The VW document itself is not public; these numbers are what the library hard-codes. (src: https://raw.githubusercontent.com/EliasTuning/KWP2000-CAN/master/kwp2000_can/protocols/can/tp20/constants.py) — consistent with the aep trace below, where the real VAG tester sent the setup frame 10 times before giving up.
- UDS modules answer on request + 0x6A in the 0x700 range: opendbc defines `VOLKSWAGEN_RX_OFFSET = 0x6a` and applies it with `rx_offset=VOLKSWAGEN_RX_OFFSET` to the request whitelisted for `[Ecu.srs, Ecu.eps, Ecu.fwdRadar, Ecu.fwdCamera]`, while the engine/transmission request has no rx_offset (i.e. standard +8 for 0x7E0/0x7E1). Also `extra_ecus=[(Ecu.fwdCamera, 0x74f, None)]`. (src: https://raw.githubusercontent.com/commaai/opendbc/master/opendbc/car/volkswagen/values.py — re-fetched, lines 647-669)
- opendbc's VW firmware query is `0x22 F187 F189 F1A3` in one request (ReadDataByIdentifier, VEHICLE_MANUFACTURER_SPARE_PART_NUMBER, VEHICLE_MANUFACTURER_ECU_SOFTWARE_VERSION_NUMBER, APPLICATION_DATA_IDENTIFICATION), expecting `0x62`; the regex for the F187 answer is `\xf1\x87[\x00-\xff]{17,58}`. The comment warns "The 0xF187 SW part number query should return in the form of N[NX][NX] NNN NNN [X[X]], where N=number, X=letter, and the trailing two letters are optional. Performance tuners sometimes tamper with that field (e.g. 8V0 9C0 BB0 1 from COBB/EQT)". (src: same file, lines 635-650)
- The EDIABAS/EDIC parameter set for VAG CAN diagnostics carries a **separate "CAN address" (wake address), tester address and ECU address**: `ParEdicWakeAddress = (byte)CommParameterProtected[5]; ParEdicTesterAddress = (byte) CommParameterProtected[70]; ParEdicEcuAddress = (byte) CommParameterProtected[71];` (lines 1776-1778) and the TP 2.0 send path does `// replace ecu address with the CAN address` / `sendData[1] = ParEdicWakeAddress;` (lines 4417-4418). I.e. VW's own tooling data model distinguishes the ECU (diagnostic) address from the CAN/TP2.0 address. (src: https://raw.githubusercontent.com/uholeschak/ediabaslib/master/EdiabasLib/EdiabasLib/EdInterfaceObd.cs — re-fetched; note a different code path (line 1705-1706) uses `CommParameterProtected[88]`/`[5]` for tester/ECU on K-line, so the slot numbers are per-protocol)
- Ross-Tech: "Each controller is listed as a number and a description, i.e., [01-Engine]. The number corresponds to the controller number that you'd find in your Factory Repair Manual in the instructions for using a VAG-1551 or other factory diagnostic tool." Direct entry of any address (e.g. 5F) is allowed ("Simply type the address such as 5F into the text entry box and click [Go!]"). "In CAN based cars that have a proper Gateway supporting an Installation List, VCDS will automatically populate one or more Installed tabs containing buttons for only those control modules that are actually installed in the car. It does take about 1.5 seconds to get the list from the Gateway". (src: https://www.ross-tech.com/vcds/tour/scm_screen.php — re-fetched, verbatim)
- Ross-Tech Auto-Scan: "If you select Auto Detect (CAN Only) as the Chassis Type on newer cars which have a fully CAN-based diagnostic system, VCDS can automatically determine which modules are installed in a particular car and perform an Auto-Scan of exactly those modules." The Gateway Installation List "is only available on Gateways in cars using a direct CAN connection for diagnostics ... takes about 3 seconds to query the car's Gateway to find out what modules are installed in the car and what their status is. Any modules having fault codes should show a 'Malfunction' and will be highlighted in RED ... Changes to the Gateway Installation List can be made using the Gateway Coding function". Auto-Scan output "also shows the applicable ROD files (used by UDS modules) and Label Files." (src: https://www.ross-tech.com/vcds/tour/autoscan.php — re-fetched, verbatim)
- Ross-Tech: "Control modules using the newest UDS/ODX protocol require a special .ROD file for VCDS to interpret data and they do not support traditional Measuring Blocks or Adaptation channel numbers." (src: http://wiki.ross-tech.com/wiki/index.php/Control_Module_Maps — re-fetched, verbatim)
  - Consequence used below: in an Auto-Scan, a module block that prints `ASAM Dataset:` / `ROD:` lines is UDS; one that prints only `Labels: xxx.lbl/.clb` with no ASAM/ROD lines is KWP (TP 2.0). Verified on an MQB Golf 7 scan where every address (01 02 03 08 09 15 16 17 19 42 44 52 5F 75) prints `ASAM Dataset:`; two of them (01, 5F) print `ROD: N/A` and are still UDS. (src: https://forums.tdiclub.com/index.php?threads/1st-vcds-scan.436803/ — re-fetched)
- SSP 307 (VW self-study programme, Golf 5 data bus diagnosis interface J533): "The immobiliser control unit J362 can be found in the dash panel insert ... The diagnosis connection is made via address word 25. Communication is only possible via the diagnosis CAN data bus with vehicle diagnosis, testing and information system VAS 5051."; the VAS tester talks to J533 over the "Diagnosis CAN data bus"; "The COM lead used until now is still required for diagnosis of the engine and gearbox control units in OBD mode." (src: http://www.volkspage.net/technik/ssp/ssp/SSP_307_d2.pdf — re-fetched, text extracted with pdftotext; the exact sentences are on the "Immobiliser"/"Diagnosis" pages)
- A hobbyist CAN trace of a commercial VAG tester on the OBD port shows it first tries `200 [7] 01 C0 00 10 00 03 01` (TP 2.0 setup to logical 0x01) **10 times**, then `000 [1] A8`, then `7E0 [8] 02 10 03 55 55 55 55 55` (UDS DiagnosticSessionControl extended), then ten 3-byte frames `200 [3] 01 C0 A0` (meaning unknown), `7A0 [1] A8`, `7E0 [8] 02 09 00 55 ...` and `7DF [8] 02 09 00 55 ...` (OBD mode 9). The car answered `7E8 [8] 06 50 03 00 1E 01 E0 55`. **Correction from the verification pass:** this car is a high-voltage EV/hybrid (the author reads battery SOC with `765 03 22 1D D0` → `7CF 04 62 1D D0 B6 AA AA AA`), NOT a Mk5-era petrol car; its 0x7E0 behaviour says nothing about the R32's ME7.1.1. Padding in that log is 0x55 on tester frames and 0xAA on ECU frames at 0x7CF, but the `7E8` reply is transcribed with a trailing `55`. (src: https://raw.githubusercontent.com/aep/vag_reverse_engineering/master/LOG.md — re-fetched, verbatim)

##### B. VCDS address words and official names (as printed by VCDS)

Verified strings, exactly as VCDS prints them in Auto-Scans re-fetched this session (scan A = 2008 R32, src: https://forums.ross-tech.com/index.php?threads/3627/ ; scan B = 2012 Golf TDI, src: https://forums.tdiclub.com/showthread.php?t=336315 ; scan C = 2010 Jetta TDI CJAA, src: https://forums.tdiclub.com/showthread.php?p=4298172 ; scan D = 2012 Passat NMS TDI, src: https://forums.tdiclub.com/showthread.php?t=440503 ; scan E = Golf 7, src: https://forums.tdiclub.com/index.php?threads/1st-vcds-scan.436803/ ; scan F **[added in verification]** = Mk5 Golf 2.0 TDI 4Motion BMM, src: https://forums.tdiclub.com/index.php?threads/vw-golf-mkv-2-0tdi-4motion-rear-door-module-errors.406046/):

- `01-Engine`, `02-Auto Trans`, `03-ABS Brakes`, `04-Steering Angle`, `08-Auto HVAC`, `09-Cent. Elect.`, `0F-Digital Radio`, `15-Airbags`, `16-Steering wheel`, `17-Instruments`, `19-CAN Gateway`, `22-AWD`, `25-Immobilizer`, `37-Navigation`, `42-Door Elect, Driver`, `44-Steering Assist`, `46-Central Conv.`, `47-Sound System`, `52-Door Elect, Pass.`, `55-Headlight Range`, `56-Radio`, `65-Tire Pressure` (scan A status list, lines 227-248 of the thread text).
- `Address 05: Acc/Start Auth. (J518)`, `Address 1C: Position Sensing`, `Address 2B: Steer. Col. Lock (J764)`, `Address 2E: Media Player 3 (J650)`, `Address 36: Seat Mem. Drvr (J136)`, `Address 4F: Centr. Electr. II (J520)`, `Address 62: Door, Rear Left`, `Address 72: Door, Rear Right`, `Address 77: Telephone (J412)` (scans B, C, D); `Address 55: Xenon Range`, `Address 76: Park Assist`, `Address 7D: Aux. Heat` (scan F).
- `Address 5F: Information Electr. (J794)`, `Address 75: Telematics (J949)` (scan E).
- Names used by Ross-Tech's own gateway coding tables (bracketed address words): [01] Engine Electronics, [11] Engine Electronics II, [02] Transmission Electronics, [03] Brake Electronics (ABS), [53] Parking Brake, [04]/[00] Steering Angle Sensor (G85), [44] Steering Assist, [15] Airbags, [55] Xenon Range, [22] All Wheel Drive, [13] Distance Regulation, [14] Suspension Electronics, [4C] Tire Pressure Monitoring II, [10] Park/Steering Assist, [32] Differential Locking, [17] Instrument Cluster, [25] Immobilizer, [09] Central Electronics, [46] Central Convenience, [42]/[52]/[62]/[72] Door Electronics (Driver/Passenger/Rear Left/Rear Right), [36] Seat Memory (Driver), [65] Tire Pressure Monitoring, [16] Steering Wheel Electronics, [08] Climate Control, [76] Parking Aid / Park Assist, [7D] Auxiliary Heating, [18] Auxiliary Heater, [26] Auto Roof, [69] Trailer, [06] Seat Memory (Passenger), [3D] Special Function, [6D] Trunk Electronic, [63] Easy Entry Driver Side, [73] Easy Entry Passenger Side, [47] Sound System, [75] Telematics / Telematic/Emergency Call, [37] Navigation, [57] TV-Tuner, [0F] Radio (digital), [56] Radio (analog), [77] Telephone, [1C] Position Sensing, [5D] Operations, [6C] Rear View Camera, [59] Tow Protection, [4F] Central Electronics II, [19] CAN-Gateway / CAN-Gateway (Standard), [3C] Lane Change Assist, [5C] Lane Maintenance Assist. (src: http://wiki.ross-tech.com/wiki/index.php/VW_Golf_(1K)_CAN-Gateway — re-fetched, oldid=4359)
- Ross-Tech's Mk6 Golf page lists these addresses for the 5K/52: [01], [02] ("6-Speed Direct Shift Gearbox (DSG/02E)", "6-Speed Automatic Transmission (09G)", "7-Speed Direct Shift Gearbox (DSG/0AM)"), [03] ("Brake Electronics (MK60EC1)" / "(MK70M)"), [08] ("Climatic" label 3C8-907-336.LBL / "Climatronic" label 5K0-907-044.LBL), [09] ("Central Electronics / Body Control Module (BCM)", "Make sure to have all Doors unlocked, otherwise this Control Module may not communicate with the Scan Tool/VCDS."), [10] Parking Aid 2, [15] Airbags (label 5K0-959-655.clb, ROD EV_AirbaVW10SMEVW360_VW36.rod), [16] Steering Wheel Electronics (labels 1K0-953-549-MY8/MY9.lbl, 5K0-953-569.clb, ROD EV_VW360SteerWheelUDS.rod), [17] Instrument Cluster, [18] Auxiliary Heating, [19] Gateway, [1C] Position Sensing, [22] All-Wheel-Drive, [25] Immobilizer, [2B] Steering Column Lock, [2E] Media Player, [37] Navigation, [42] Door Electronics Driver (1K0-959-701-MIN3/MAX3.LBL), [44] Steering Assist, [46] Comfort System ("has been integrated with the Central Electronics / Body Control Module (BCM) and is no longer available as a separate Address/Module"), [47] Sound System, [52] Door Electronics Passenger, [55] Headlight Aim Control ("Xenon with AFS", labels 5M0-907-357-V1/V2.LBL), [56] Radio (Analog) ("The RNS-310 and RNS-315 do not communicate with a scan tool. Use address 37-Navigation (J794) instead."), [62]/[72] Door Electronics Rear Left/Right (1K0-959-703/704-GEN3.LBL), [65] Tire Pressure Monitoring, [69] Trailer, [77] Telephone. (src: https://wiki.ross-tech.com/wiki/index.php/VW_Golf/Golf_Plus_(5K/52) — re-fetched, oldid=8558)
  - **[added in verification]** Two further statements on that page matter for the autoscan: "Mid 2010 and later production 5K/52/AJ platform vehicles use UDS Protocol rear doors which are sub systems (slaves) of the front addresses 42 and 52. If the individual rear door modules do not communicate with VCDS, check the front doors (#42/52) looking at their sub-system modules" — yet the 2012 Golf in scan B still has standalone KWP rear doors (`5K0 959 703 D`/`704 D`, labels ...-GEN3.lbl), so this is build-dependent; and "The 2011 NAR (North American Region) vehicles are equipped with the Indirect TPMS which is a function of the ABS Brake Electronics (MK60EC1) system. Address [65] - Tire Pressure Monitoring is NOT used." (matches scan B: no 65). (src: same page)
- Mk6 BCM page: "Address 09: Cent. Elect. (J519) Labels: 1K0-937-08x-09.clb", "Part No SW: 1K0 937 084 G HW: 1K0 937 084 G / Component: BCM PQ35 B 110 0651" and "Part No SW: 5K0 937 086 L HW: 5K0 937 086 L / Component: BCM PQ35 M 011 0048"; "Make sure to have all Doors unlocked, otherwise this Control Module may not communicate with VCDS!"; "The Comfort System known from earlier Models has been integrated with the Central Electronics / Body Control Module (BCM) and is no longer available as a separate Address/Module." (src: https://wiki.ross-tech.com/wiki/index.php/VW_Golf_(5K)_Body_Control_Module — re-fetched, verbatim)
- A complete numeric list 01..7F plus LT3 (91..A3) and B0..B6 exists at mr-fix (re-fetched; it is a transcription with visible errors: it lists "29" twice ("29 – HVAC rear", "29 – Left light (headlight?)"; HVAC rear is 28 everywhere else) and "19 – CAN getaway"). Its entries, verbatim apart from obvious typos: 01 Engine electronics 1, 02 Automatic transmission, 03 ABS brakes, 04 Steering angle, 05 Ignition authorization, 06 Passengers seat memory, 07 Control head, 08 Automatic heat/ventilation/air condition, 09 Central electronics, 0B Secondary air heater, 0D Left sliding door, 0E Media player 1, 0F Digital radio, 10 Parking/steering assist, 11 Engine electronics 2, 12 Clutch, 13 Distance control (ACC?), 14 Suspension electronics, 15 Airbags, 16 Steering wheel, 17 Instruments, 18 Auxiliary heating, 19 CAN gateway, 1B Active steering, 1C Position sensing, 1D Driver identification, 1E Media Player 2, 1F Satellite tuner, 21 Engine electronics 3, 22 AWD, 23 Brake booster, 24 Antislip (ESP?), 25 Immobilizer, 26 Electrical sunroof, 27 Control head rear, 28(printed 29) HVAC rear, 29 Left light, 2D Intercom, 2E Media Player 3, 2F Digital TV, 31 Engine, 32 Differential locks, 34 Level control, 35 Central locks, 36 Drivers seat memory, 37 Navigation, 38 Roof electronics, 39 Right light, 3C Side assist, 3D Special function, 3E Media player 4, 41 Diesel fuel pump, 42 Driver door electronics, 43 Brake assistant, 44 Steering assistant, 45 Interior monitor, 46 Central convenience, 47 Sound system (amplifier?), 48 Rear seat drivers side, 49 Auto light switch, 4C Tire pressure 2, 4D Data transfer, 4E Control head right rear, 4F Central electronics 2, 51 Electric drive, 52 Passenger door electronics, 53 Parking brake, 54 Rear spoiler, 55 Xenon range, 56 Radio, 57 TV tuner, 58 Auxiliary fuel tank, 59 Tow protection, 5C Lane assist, 5D Operations, 5E Control head left rear, 5F Information electronics, 61 Battery regulator, 62 Rear left door, 63 Entry assist driver, 64 Stabilizers, 65 Tire pressure, 66 Seat & mirror adjustment / seat rear, 67 Voice control, 68 Wipers electronics, 69 Trailer, 6C Rear view camera, 6D Trunk electronics, 6E Control head roof, 6F Central convenience 2, 71 Battery charger, 72 Rear right door, 73 Entry assist passenger, 74 Chassis control, 75 Emergency call / Telematics, 76 Parking aid, 77 Telephone, 78 Right slide door, 7D Auxiliary heater, 7E Control head dashboard, 7F Information electronics 2, 91..A3 LT3 (91 Engine, 92 Transmission, 93 Immobiliser, 94 Airbag, 95 ESP, 96 Instruments, 97 Trip recorder, 98 Tire pressure, 99 Ignition switch, 9A Central locks, 9B Driver door, 9C HVAC, 9D Auxiliary heater (fuel), 9E Auxiliary heater (electric), 9F Stationary heater (water), A0 Radio, A1 Navigation, A2 CD changer, A3 Telephone), B0 Roof display, B1 Upper console, B2 Park assist, B3 Trailer module, B4 Central electronic, B5 Special function, B6 Steering wheel. (src: http://mr-fix.info/vag-control-modules-list-for-vcds/ — re-fetched)
- The same list, in C-enum form (identical numbers 0x01..0x7F, plus LT3 0x91..), was quoted on NefMoto as "Found on github some time ago related to VAG cars": `ECU = 0x01, AUTO_TRANS = 0x02, ABS = 0x03, STEERING_ANGLE = 0x04, ACC_START_AUTHORIZATION = 0x05, SEAT_MEMORY_PASS = 0x06, CONTROL_HEAD = 0x07, AUTO_HVAC = 0x08, CENTRAL_ELECTRONICS = 0x09, SECONDARY_AIR_HEATING = 0x0B, DOOR_SLIDE_LEFT = 0x0D, MEDIA_PLAYER_1 = 0x0E, DIGITAL_RAIDO = 0x0F, PARK_ASSIST = 0x10, ECU_II = 0x11, CLUTCH = 0x12, AUTO_DIST_REG = 0x13, SUSPENSION_ELECTRONICS = 0x14, AIRBAG = 0x15, STEERING_WHEEL = 0x16, INSTRUMENTS = 0x17, AUX_HEAT = 0x18, CAN_GATEWAY = 0x19, ACTIVE_STEERING = 0x1B, POSITION_SENSING = 0x1C, DRIVER_IDENTIFICATION = 0x1D, MEDIA_PLAYER_2 = 0x1E, SAT_TUNER = 0x1F, ECU_III = 0x21, AWD = 0x22, BRAKE_BOOSTER = 0x23, ANTI_SLIP = 0x24, IMMOBILIZER = 0x25, AUTO_ROOF = 0x26, CONTROL_HEAD_REAR = 0x27, HVAC_REAR = 0x28, LEFT_LIGHT = 0x29, INTERCOM = 0x2D, MEDIA_PLAYER_3 = 0x2E, DIGITAL_TV = 0x2F, ENGINE_OTHER = 0x31, DIFFERENTIAL_LOCKS = 0x32, LEVEL_CONTROL = 0x34, CENTRAL_LOCKS = 0x35, SEAT_MEMORY_DRIVER = 0x36, NAVIGATION = 0x37, ROOF_ELECTRONICS = 0x38, RIGHT_LIGHT = 0x39, LANE_CHANGE = 0x3C, SPECIAL_FUNCTION = 0x3D, MEDIA_PLAYER_4 = 0x3E, DIESEL_PUMP = 0x41, DOOR_ELECTRONICS_DRIVER = 0x42, BRAKE_ASSIST = 0x43, STEERING_ASSIST = 0x44, INTERNAL_MONITOR = 0x45, CENTRAL_CONV = 0x46, SOUND_SYSTEM = 0x47, SEAT_REAR_DRIVER = 0x48, AUTOMATIC_LIGHT = 0x49, TIRE_PRESSURE_II = 0x4C, DATA_TRANSFER = 0x4D, CONTROL_HEAD_RIGHT_REAR = 0x4E, CENTRAL_ELECTRONICS_II = 0x4F, ELECTRIC_DRIVE = 0x51, DOOR_ELECTRONICS_PASS = 0x52, PARKING_BRAKE = 0x53, REAR_SPOILER = 0x54, HEADLIGHT_RANGE = 0x55, RADIO = 0x56, TV_TUNER = 0x57, AUX_FUEL_TANK = 0x58, TOW_PROTECTION = 0x59, LANE_MAINTAIN = 0x5C, OPERATIONS = 0x5D, CONTROL_HEAD_LEFT_REAR = 0x5E, INFROMATION_ELECTRONICS = 0x5F, BATTERY_REGULATOR = 0x61, DOOR_ELECTRONICS_REAR_LEFT = 0x62, ENTRY_ASSIST_DRIVER = 0x63, STABILIZERS = 0x64, TIRE_PRESSURE = 0x65, SEAT_REAR = 0x66, VOICE_CONTROL = 0x67, WIPER_ELECTRONICS = 0x68, TRAILER = 0x69, BACKUP_CAMERA = 0x6C, TRUNK_ELECTRONICS = 0x6D, CONTROL_HEAD_ROOF = 0x6E, CENTRAL_CONV_II = 0x6F, BATTERY_CHARGER = 0x71, DOOR_ELECTRONICS_REAR_RIGHT = 0x72, ENTRY_ASSIST_PASS = 0x73, CHASSIS_CONTROL = 0x74, TELEMATICS = 0x75, PARK_ASSIST_II = 0x76, TELEPHONE = 0x77, DOOR_SLIDE_RIGHT = 0x78, AUX_HEAT_II = 0x7D, CONTROL_HEAD_DASH = 0x7E, INFORMATION_ELECTRONICS_II = 0x7F, LT3_ENGINE = 0x91, LT3_TRANSMISSION_ = 0x92, LT3_IMMO = 0x93, LT3_AIRBAG = 0x94, LT3_ESP = 0x95, LT3_INSTRUMENTS = 0x96, LT3_TRIP_RECORDER = 0x97, LT3_TIRE_PRESSURE = 0x98, LT3_IGN_SWITCH = 0x99, LT3_CENTRAL_LOCKS = 0x9A, LT3_DRIVER_DOOR = 0x9B, LT3_HVAC = 0x9C, LT3_AUX_HEAT_FUEL = 0x9D, LT3_AUX_HEAD_ELEC = 0x9E, ...` (src: http://nefariousmotorsports.com/forum/index.php?topic=9949.0 — re-fetched, verbatim incl. the typos DIGITAL_RAIDO / INFROMATION_ELECTRONICS). Note: this enum is the VCDS *address word* list; the same thread shows it is NOT the K-line physical address list (see §D).
- Address words that do not appear in any fetched list (gaps in the 0x01..0x7F scheme): 0x00, 0x0A, 0x0C, 0x1A, 0x20, 0x2A, 0x2C, 0x30, 0x33, 0x3A, 0x3B, 0x3F, 0x40, 0x4A, 0x4B, 0x50, 0x5A, 0x5B, 0x60, 0x6A, 0x6B, 0x70, 0x79, 0x7A, 0x7B, 0x7C. (0x2B Steering Column Lock does exist — scan D.) Newer MQB-era address words above 0x7F (81, 82, 8C, A5, A9, B7, BB, C6, CA ...) are outside these lists and are not needed for PQ35 cars. (derived from the lists above)

#### Reported / unverified (confidence)

##### 0. Items moved out of VERIFIED by the verification pass

- **medium**: OBDeleven's installation-list colour semantics ("working but not installed in the Gateway installation list (YELLOW), or installed but not reachable (BLACK)") — the page https://forum.obdeleven.com/thread/6969/messed-gateway-list-pls-help returned HTTP 406 to both WebFetch and curl; the wording comes from a search-engine summary only. The *concept* (list = configured expectation, not a live scan) is independently supported by Ross-Tech ("Changes to the Gateway Installation List can be made using the Gateway Coding function") and by the R32 scan (22 listed but "Cannot be reached"). What would confirm: fetching the page, or OBDeleven's own manual.
- **low** (was implied in the R32 protocol table): "the aep log shows `7E8 06 50 03 ...` on a Mk5-era car" — wrong; that car is an EV/hybrid (HV battery SOC via 0x765/0x7CF). It is NOT evidence that a 2008 ME7.1.1 answers UDS `10 03` on 0x7E0.

##### 5. Other reported facts

- **high**: VCDS uses label files named after the part-number prefix (`1K0-907-379-60EC1F.clb`, `03L-906-022-CBE.clb`); `.lbl` plain text, `.clb` compiled/encrypted ("CLB LABELS ARE NOT, AND WILL *NEVER* BE SUPPORTED ... The entire purpose of CLB files is to prevent competitors from trivially using them" — PyVCDS README, fetched). Not a protocol indicator (scan B's UDS cluster uses a `.clb`, its KWP compass a `.lbl`).
- **high**: VAG ISO-TP padding is 0x55 on tester frames and 0xAA on ECU frames in the fetched log (one `7E8` line transcribed with 0x55); OpenHaldex-C6 pads its UDS requests with 0xAA. Padding value is not semantically significant.
- **medium**: the ODIS-derived `LL_*UDS` IDs are also what ODIS/VCDS use on PQ35 UDS modules (not only MQB) — scan B's UDS modules (cluster 5K0 920, airbag VW10) are PQ35 parts and the +0x6A scheme predates MQB (opendbc applies it to PQ cars too). What would confirm: a trace of VCDS reading 17 on the Golf showing 0x714/0x77E.
- **low**: Haldex label names "0AY-907-554-V1.clb / Haldex 4Motion 3016" (TT 8J) — search-engine snippet only; the ttforum page is paywalled (HTTP 402 via tollbit). The Mk5 label "1K0-907-554.lbl / Haldex 4Motion 0115" IS verified (scan F).
- **low**: K-line physical addresses (cluster 0x61, transmission 0x26?) — irrelevant for these two CAN-only cars; mentioned only because they prove VCDS translates the address word per transport.
- **medium**: on PQ35 "every module that owns body state except 09 and 17 sits ABOVE 0x3F -- 0x42 door driver, 0x46 comfort, 0x52 door passenger, 0x55 headlight aim, 0x56 radio. A 0x00-0x3F sweep therefore looks convincingly complete while missing exactly the modules worth having" — the scirocco-dash author's rationale for probing address words as TP 2.0 dests; given §D (EPS 0x09, Haldex 0x0A, gateway 0x1F) the safe sweep is all 256 bytes, not a curated list.

---


### 7.2 UDS (ISO-TP, 11-bit) request/response CAN id table (ODIS)

Source sheet: `addresses.md` §C (90 rows diffed programmatically against the source — identical) and Reported §1 (address word → ODIS link inference).

#### Verified (source)

##### C. UDS (ISO-TP, 11-bit) request/response CAN IDs — full table

Source: "A comprehensive collection of VAG UDS CAN IDs extracted from ODIS". Reproduced verbatim (ODIS logical-link name → request → response). **Verification pass: the source was re-fetched and the 90 rows below were diffed programmatically against it — identical, same order.** (src: https://raw.githubusercontent.com/ConnorHowell/vag-uds-ids/main/readme.md)

| ODIS logical link | Request | Response |
|---|---|---|
| LL_ParkiAssis2UDS | 0x70A | 0x774 |
| LL_HighBeamAssisUDS | 0x730/0x748 | 0x79A/0x7B2 |
| LL_SpeciFunct2UDS | 0x72B | 0x795 |
| LL_EnginContrModul1UDS | 0x7E0 | 0x7E8 |
| LL_EnginContrModul2UDS | 0x7E2 | 0x7EA |
| LL_TransContrModulUDS | 0x7E1 | 0x7E9 |
| LL_AllWheelContrUDS | 0x70F/0x71D | 0x779/0x787 |
| LL_LockElectUDS | 0x71E | 0x788 |
| LL_Brake1UDS | 0x713 | 0x77D |
| LL_AdaptCruisContrUDS | 0x757 | 0x7C1 |
| LL_SteerAngleSendeUDS | 0x751 | 0x7BB |
| LL_WheelDampeElectUDS | 0x772 | 0x7DC |
| LL_RideContrSysteUDS | 0x755 | 0x7BF |
| LL_KessyUDS | 0x732 | 0x79C |
| LL_AirbaUDS | 0x715 | 0x77F |
| LL_ImmobUDS | 0x711 | 0x77B |
| LL_SeatAdjusPasseSideUDS | 0x74D | 0x7B7 |
| LL_SteerColumElectUDS | 0x70C | 0x776 |
| LL_ElectRoofContrUDS | 0x72D | 0x797 |
| LL_DashBoardUDS | 0x714 | 0x77E |
| LL_AirCondiUDS | 0x746 | 0x7B0 |
| LL_AuxilParkiHeateUDS | 0x76A | 0x7D4 |
| LL_ClimaContrUnitRearUDS | 0x71A | 0x784 |
| LL_CentrElectUDS | 0x70E | 0x778 |
| LL_GatewUDS | 0x710 | 0x77A |
| LL_ActivSteerUDS | 0x716 | 0x780 |
| LL_SteerColumLockiUDS | 0x731 | 0x79B |
| LL_VehicPositDetecUDS | 0x750 | 0x7BA |
| LL_SlidiDoorLeftUDS | 0x733 | 0x79D |
| LL_MediaPlayePosit1UDS | 0x770 | 0x7DA |
| LL_MediaPlayePosit3UDS | 0x76E | 0x7D8 |
| LL_AirCondiComprUDS | 0x719 | 0x783 |
| LL_TachoUDS | 0x771 | 0x7DB |
| LL_DriveMotorContrModulUDS | 0x7E6 | 0x7EE |
| LL_BatteRegulUDS | 0x728 | 0x792 |
| LL_DoorElectDriveSideUDS | 0x74A | 0x7B4 |
| LL_DoorElectPasseSideUDS | 0x74B | 0x7B5 |
| LL_ParkiBrakeUDS | 0x752 | 0x7BC |
| LL_SteerAssisUDS | 0x712 | 0x77C |
| LL_HeadlRegulUDS | 0x754 | 0x7BE |
| LL_TirePressMonit1UDS | 0x70B | 0x775 |
| LL_SeatAdjusDriveSideUDS | 0x74C | 0x7B6 |
| LL_CentrModulComfoSysteUDS | 0x70D | 0x777 |
| LL_RadioUDS | 0x718 | 0x782 |
| LL_NavigUDS | 0x76C | 0x7D6 |
| LL_SoundSysteUDS | 0x76F | 0x7D9 |
| LL_TVTunerUDS | 0x76D | 0x7D7 |
| LL_TrailFunctUDS | 0x747 | 0x7B1 |
| LL_SensoElectUDS | 0x721 | 0x78B |
| LL_LaneChangAssisUDS | 0x74E | 0x7B8 |
| LL_SpeciFunctUDS | 0x72C | 0x796 |
| LL_InforContrUnit1UDS | 0x773 | 0x7DD |
| LL_PreteFrontRightUDS | 0x75F | 0x7C9 |
| LL_BatteChargUDS | 0x765 | 0x7CF |
| LL_GearShiftContrModulUDS | 0x753 | 0x7BD |
| LL_HeadUpDisplUDS | 0x71B | 0x785 |
| LL_NightVisioUDS | 0x727 | 0x791 |
| LL_ArmreUDS | 0x739 | 0x7A3 |
| LL_TelemUDS | 0x767 | 0x7D1 |
| LL_OnBoardCamerUDS | 0x726 | 0x790 |
| LL_ParkiAssisUDS | 0x70A | 0x774 |
| LL_TelepUDS | 0x76B | 0x7D5 |
| LL_SlidiDoorRightUDS | 0x734 | 0x79E |
| LL_MultiContoSeatDriveSideUDS | 0x735 | 0x79F |
| LL_MultiContoSeatPasseSideUDS | 0x736 | 0x7A0 |
| LL_MultiContoSeatRearDriveSideUDS | 0x737 | 0x7A1 |
| LL_AdaptCruisContr2UDS | 0x756 | 0x7C0 |
| LL_CamerSysteRearViewUDS | 0x769 | 0x7D3 |
| LL_BatteEnergContrModulUDS | 0x7E5 | 0x7ED |
| LL_DeckLidContrUnitUDS | 0x723 | 0x78D |
| LL_MultiContoSeatRearPasseSideUDS | 0x738 | 0x7A2 |
| LL_DashBoardDisplUnitUDS | 0x716 | 0x780 |
| LL_ImageProceElectUDS | 0x758 | 0x7C2 |
| LL_CentrModulComfoSyste2UDS | 0x745 | 0x7AF |
| LL_PreteFrontLeftUDS | 0x75E | 0x7C8 |
| LL_FrontSensoDriveAssisSysteUDS | 0x74F | 0x7B9 |
| LL_MicroContrUnitUDS | 0x763 | 0x7CD |
| LL_InfotInterUDS | 0x749 | 0x7B3 |
| LL_AccesStartInterUDS | 0x732 | 0x79C |
| LL_ExterCommuInterUDS | 0x76B | 0x7D5 |
| LL_ElectRoofContr2UDS | 0x73D | 0x7A7 |
| LL_ActuaForStrucBorneSoundUDS | 0x71C | 0x786 |
| LL_AuxilDisplContrUnitUDS | 0x73C | 0x7A6 |
| LL_WheelBrakeRearRightUDS | 0x720 | 0x78A |
| LL_AssemMountUDS | 0x72E | 0x798 |
| LL_WheelBrakeRearLeftUDS | 0x71F | 0x789 |
| LL_DoorElectRearDriveSideUDS | 0x73E | 0x7A8 |
| LL_ReducContrModulUDS | 0x72A | 0x794 |
| LL_DoorElectRearPasseSideUDS | 0x73F | 0x7A9 |
| LL_SensoBrakeSysteUDS | 0x762 | 0x7CC |

- Arithmetic check on the table (re-run programmatically in the verification pass, zero exceptions): every 0x70x..0x77x pair satisfies `response = request + 0x6A` (e.g. 0x710+0x6A=0x77A, 0x713+0x6A=0x77D, 0x746+0x6A=0x7B0, 0x773+0x6A=0x7DD, 0x70A+0x6A=0x774); the 0x7E0..0x7E7 powertrain range uses `response = request + 8` (0x7E0→0x7E8, 0x7E1→0x7E9, 0x7E2→0x7EA, 0x7E5→0x7ED, 0x7E6→0x7EE). (derived from the table above; the +0x6A rule is also opendbc's `VOLKSWAGEN_RX_OFFSET = 0x6a`.)
- A second site republishes the same pairs for the common modules: Engine 1 0x7E0/0x7E8, Engine 2 0x7E2/0x7EA, Transmission 0x7E1/0x7E9, AllWheelDrive 0x70F/0x779, Gateway 0x710/0x77A, ABS 0x713/0x77D, Dashboard 0x714/0x77E, SRS 0x715/0x77F, HVAC 0x746/0x7B0. (src: https://wiki.mr-fix.info/index.php?title=CAN-BUS_sniffing — re-fetched; it cites "↑ https://github.com/ConnorHowell/vag-uds-ids", so it is not independent.)
- Independent corroboration of individual IDs: cluster "UDS ID is 714h" (src: http://nefariousmotorsports.com/forum/index.php?topic=14242.0, poster H2Deetoo); fwdCamera 0x74F and rx_offset 0x6A (src: opendbc values.py above); **[added in verification]** Haldex Gen5 on MQB "0x70F -> 0x779 (VCDS uses 0x70F on Bus 0, bridged to Bus 1; response confirmed from a SavvyCAN capture)" and VAQ/Quersperre "0x71E -> 0x788 per the K-matrix" (src: https://raw.githubusercontent.com/Forbes-Automotive/OpenHaldex-C6/b3805750a3cb79e994aec4ac30e52ea4eda7547f/src/OpenHaldexC6_UDS.cpp); vagtune's existing `modules.py` already uses 0x7E0/0x7E8, 0x7E1/0x7E9, 0x713/0x77D, 0x70F/0x779, 0x710/0x77A (src: /home/user/ruggedroute-dataops/vagtune/vagtune/vag/modules.py).
- Four anomalies inside the ODIS-derived table that code must tolerate (confirmed by a duplicate scan of the re-fetched table): (1) `0x716/0x780` is listed for both LL_ActivSteerUDS and LL_DashBoardDisplUnitUDS; (2) `0x70A/0x774` for both LL_ParkiAssisUDS and LL_ParkiAssis2UDS; (3) `0x732/0x79C` for both LL_KessyUDS and LL_AccesStartInterUDS; (4) `0x76B/0x7D5` for both LL_TelepUDS and LL_ExterCommuInterUDS. These are different ODIS link names for the same physical slot across generations. (derived from the table.)
- **The task brief's seed values "08 HVAC 0x744/0x7AE" and "46 central conv 0x746/0x7B0" do not match the ODIS table**: 0x746/0x7B0 is LL_AirCondiUDS (HVAC, address 08) and the comfort/convenience module (46) is LL_CentrModulComfoSysteUDS 0x70D/0x777. 0x744 does not appear in the table at all. Use the table, not the brief. (src: ConnorHowell table above.)
- The functional (broadcast) OBD request ID 0x7DF is used by VAG testers (`7DF [8] 02 09 00 55 55 55 55 55`), as is physical `7E0 [8] 02 09 00 ...`. (src: https://raw.githubusercontent.com/aep/vag_reverse_engineering/master/LOG.md)

#### Reported / unverified (confidence)

##### 1. Address word → UDS CAN ID mapping (inferred from ODIS link names; IDs themselves are verified)

Confidence **high** where the ODIS name is unambiguous, **medium** where two address words share a concept. Confirm by sending `03 22 F1 87` to the request ID and reading `62 F1 87 <part number>`; the part-number prefix identifies the module.

| Addr | VCDS name | ODIS link (verified ID) | Req → Resp | conf. |
|---|---|---|---|---|
| 01 | Engine | LL_EnginContrModul1UDS | 0x7E0 → 0x7E8 | high |
| 11 | Engine II | LL_EnginContrModul2UDS | 0x7E2 → 0x7EA | high |
| 02 | Auto Trans | LL_TransContrModulUDS | 0x7E1 → 0x7E9 | high |
| 51 | Electric Drive | LL_DriveMotorContrModulUDS | 0x7E6 → 0x7EE | medium |
| 8C (MQB) | Battery Energy Ctrl | LL_BatteEnergContrModulUDS | 0x7E5 → 0x7ED | medium |
| 03 | ABS Brakes | LL_Brake1UDS | 0x713 → 0x77D | high |
| 04 | Steering Angle | LL_SteerAngleSendeUDS | 0x751 → 0x7BB | high |
| 05 | Acc/Start Auth. | LL_KessyUDS / LL_AccesStartInterUDS | 0x732 → 0x79C | high |
| 06 | Seat Mem. Pass | LL_SeatAdjusPasseSideUDS | 0x74D → 0x7B7 | high |
| 08 | Auto HVAC | LL_AirCondiUDS | 0x746 → 0x7B0 | high |
| 09 | Cent. Elect. | LL_CentrElectUDS | 0x70E → 0x778 | high |
| 0D | Left sliding door | LL_SlidiDoorLeftUDS | 0x733 → 0x79D | high |
| 0E | Media Player 1 | LL_MediaPlayePosit1UDS | 0x770 → 0x7DA | high |
| 10 | Park/Steer Assist | LL_ParkiAssisUDS | 0x70A → 0x774 | medium (76 Park Assist II shares the slot: LL_ParkiAssis2UDS is the same ID) |
| 13 | Auto Dist. Reg (ACC) | LL_AdaptCruisContrUDS | 0x757 → 0x7C1 | high (opendbc fwdRadar uses +0x6A; ID from ODIS) |
| 14 | Susp. Elect. (DCC) | LL_WheelDampeElectUDS | 0x772 → 0x7DC | high |
| 15 | Airbags | LL_AirbaUDS | 0x715 → 0x77F | high |
| 16 | Steering wheel | LL_SteerColumElectUDS | 0x70C → 0x776 | high |
| 17 | Instruments | LL_DashBoardUDS | 0x714 → 0x77E | high (also NefMoto "UDS ID is 714h") |
| 18 / 7D | Aux. Heat | LL_AuxilParkiHeateUDS | 0x76A → 0x7D4 | medium (which of 18/7D is fuzzy) |
| 19 | CAN Gateway | LL_GatewUDS | 0x710 → 0x77A | high |
| 1B | Active Steering | LL_ActivSteerUDS | 0x716 → 0x780 | medium (ID shared with 7E) |
| 1C | Position Sensing | LL_VehicPositDetecUDS | 0x750 → 0x7BA | high |
| 22 | AWD | LL_AllWheelContrUDS | 0x70F → 0x779 (alt 0x71D → 0x787) | high for Gen5/MQB; **does not apply to the Mk5 Gen2 Haldex (KWP/TP 2.0 at 0x0A, §D)** |
| 25 | Immobilizer | LL_ImmobUDS | 0x711 → 0x77B | high |
| 26 | Auto Roof | LL_ElectRoofContrUDS | 0x72D → 0x797 | high |
| 28 | HVAC Rear | LL_ClimaContrUnitRearUDS | 0x71A → 0x784 | high |
| 2B | Steer. Col. Lock | LL_SteerColumLockiUDS | 0x731 → 0x79B | high |
| 2E | Media Player 3 | LL_MediaPlayePosit3UDS | 0x76E → 0x7D8 | high |
| 34 | Level Control | LL_RideContrSysteUDS | 0x755 → 0x7BF | medium |
| 35 | Central Locks | LL_LockElectUDS | 0x71E → 0x788 | medium (OpenHaldex calls 0x71E/0x788 the MQB "VAQ/Quersperre" = front differential lock, which is address 32 Differential Locking, not 35) |
| 36 | Seat Mem. Drvr | LL_SeatAdjusDriveSideUDS | 0x74C → 0x7B6 | high |
| 37 | Navigation | LL_NavigUDS | 0x76C → 0x7D6 | high |
| 3C | Lane Change | LL_LaneChangAssisUDS | 0x74E → 0x7B8 | high |
| 3D | Special Function | LL_SpeciFunctUDS (2: LL_SpeciFunct2UDS) | 0x72C → 0x796 (0x72B → 0x795) | high |
| 42 | Door Elect, Driver | LL_DoorElectDriveSideUDS | 0x74A → 0x7B4 | high |
| 44 | Steering Assist | LL_SteerAssisUDS | 0x712 → 0x77C | high |
| 46 | Central Conv. | LL_CentrModulComfoSysteUDS | 0x70D → 0x777 | high |
| 47 | Sound System | LL_SoundSysteUDS | 0x76F → 0x7D9 | high |
| 4F | Centr. Electr. II | (no ODIS UDS link in the list) | ? | — (PQ35 4F is KWP; scan D) |
| 52 | Door Elect, Pass. | LL_DoorElectPasseSideUDS | 0x74B → 0x7B5 | high |
| 53 | Parking Brake | LL_ParkiBrakeUDS | 0x752 → 0x7BC | high |
| 55 | Headlight Range | LL_HeadlRegulUDS | 0x754 → 0x7BE | high |
| 56 | Radio | LL_RadioUDS | 0x718 → 0x782 | high |
| 57 | TV Tuner | LL_TVTunerUDS | 0x76D → 0x7D7 | high |
| 5F | Information Electr. | LL_InforContrUnit1UDS | 0x773 → 0x7DD | high |
| 61 | Battery Regul. | LL_BatteRegulUDS | 0x728 → 0x792 | high |
| 62 | Door, Rear Left | LL_DoorElectRearDriveSideUDS | 0x73E → 0x7A8 | high |
| 65 | Tire Pressure | LL_TirePressMonit1UDS | 0x70B → 0x775 | high |
| 69 | Trailer | LL_TrailFunctUDS | 0x747 → 0x7B1 | high |
| 6C | Back-up Cam. | LL_CamerSysteRearViewUDS | 0x769 → 0x7D3 | high |
| 6D | Trunk Elect. | LL_DeckLidContrUnitUDS | 0x723 → 0x78D | high |
| 6F | Centr. Conv. II | LL_CentrModulComfoSyste2UDS | 0x745 → 0x7AF | high |
| 71 | Battery Charger | LL_BatteChargUDS | 0x765 → 0x7CF | high (the aep EV reads its HV-battery SOC exactly there) |
| 72 | Door, Rear Right | LL_DoorElectRearPasseSideUDS | 0x73F → 0x7A9 | high |
| 75 | Telematics | LL_TelemUDS | 0x767 → 0x7D1 | high |
| 76 | Park Assist | LL_ParkiAssis2UDS | 0x70A → 0x774 | medium |
| 77 | Telephone | LL_TelepUDS / LL_ExterCommuInterUDS | 0x76B → 0x7D5 | high |
| 78 | Right slide door | LL_SlidiDoorRightUDS | 0x734 → 0x79E | high |
| 7E | Dash Board Display | LL_DashBoardDisplUnitUDS | 0x716 → 0x780 | medium (shared with 1B) |
| 81 (MQB) | Gear Shift Ctrl | LL_GearShiftContrModulUDS | 0x753 → 0x7BD | medium |
| 82 (MQB) | Head-Up Display | LL_HeadUpDisplUDS | 0x71B → 0x785 | medium |
| A5 (MQB) | Front Sensors Driver Assist | LL_FrontSensoDriveAssisSysteUDS | 0x74F → 0x7B9 | high (opendbc fwdCamera 0x74f) |
| — | (no classic address word) | LL_HighBeamAssisUDS 0x730/0x748, LL_AirCondiComprUDS 0x719, LL_TachoUDS 0x771, LL_SensoElectUDS 0x721, LL_PreteFrontRight/Left 0x75F/0x75E, LL_NightVisio 0x727, LL_Armre 0x739, LL_OnBoardCamer 0x726, LL_MultiContoSeat* 0x735..0x738, LL_AdaptCruisContr2 0x756, LL_ImageProceElect 0x758, LL_MicroContrUnit 0x763, LL_InfotInter 0x749, LL_ElectRoofContr2 0x73D, LL_ActuaForStrucBorneSound 0x71C, LL_AuxilDisplContrUnit 0x73C, LL_WheelBrakeRearRight/Left 0x720/0x71F, LL_AssemMount 0x72E, LL_ReducContrModul 0x72A, LL_SensoBrakeSyste 0x762 | low (MQB/MLB-era; not expected on PQ35) |


### 7.3 TP 2.0 frame formats and logical addresses (the `0xC0` destination byte)

Source sheet: `addresses.md` §D and Reported §2. The frame-format bullets duplicate §2 (kept verbatim because they carry additional on-car observations: the MED17.5 request-form exception, the `D7` recovery rule, the T3=0x0A degradation, Haldex Gen2 0x0A/0x764, CJAA at 0x01).

#### Verified (source)

##### D. TP 2.0 — frame formats and logical addresses

Frame formats (src: https://jazdw.net/tp20 ; cross-checked with https://icanhack.nl/knowledge-base/diagnostics/vw-tp20/ and the code in https://raw.githubusercontent.com/pd0wm/pq-flasher/master/tp20.py and https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c — all four re-fetched):

- Broadcast (7 bytes, sent 5 times): `[Dest][Opcode 0x23 req / 0x24 resp][KWP SID+params (4 bytes)][RespReq 0x00 = response expected, 0x55 or 0xAA = none]`. jazdw: "Not sure what it is actually used for yet." icanhack: "useful to quickly send a message without needing a (long) response, and without needing to open a channel first."
- Channel setup (7 bytes, CAN ID 0x200; reply on 0x200+Dest): `[Dest][Opcode][RX ID low][RX V<<4 | RX prefix][TX ID low][TX V<<4 | TX prefix][App]` with Opcode 0xC0 setup request, 0xD0 positive response, 0xD6..0xD8 negative; V nibble 0x0 = CAN ID valid, 0x1 = invalid; App 0x01 (KWP). jazdw: "You should request the destination module to transmit using CAN ID 0x300 to 0x310 and set the validity nibble for RX ID to invalid. The VW modules seem to respond that you should transmit using CAN ID 0x740." icanhack adds: in the response, byte 0 is "Logical address of the tester (always 0x00)".
  - Exact tester request bytes used by every fetched implementation: `<dest> C0 00 10 00 03 01` (RX ID invalid = 0x1000 nibble set; TX ID 0x300 valid; app 0x01). pq-flasher: `self.can_send(bytes([module]) + b"\xc0\x00\x10\x00\x03\x01", BROADCAST_ADDR)`; VAG Blocks: `writeToElmStr(toHex(dest, 2) + " C0 00 10 00 03 01")` and it validates `setup.opcode != 0xD0 || rxID != 0x300 || setup.rxV > 0 || setup.txV > 0` (src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/tp20.cpp, lines 530-537 — re-fetched); the real VAG tester in the aep trace sent exactly `01 C0 00 10 00 03 01`.
  - **[added in verification] Exception measured on a 2009 Scirocco MED17.5 (J533 gateway):** "both ID fields of the REQUEST must carry a real, valid ID. The widely-copied form that puts 0x0010 -- the 'not valid' marker, high nibble 1 -- in bytes 2-3 is ignored with no reply at all. Sending 0x300 in both fields works: `tx 0x200: 01 C0 00 03 00 03 01` / `rx 0x201: 00 D0 00 03 40 07 01`". This conflicts with the aep trace of a real VAG tester using `00 10`; the implementation must try `00 10 00 03` first and fall back to `00 03 00 03`. (src: https://raw.githubusercontent.com/vinistoisr/scirocco-dash/5df95ec2114ec10ca7862eacb352a95ea5642f66/board/tp20.py, module docstring — one car, author's own measurement)
  - ECU response examples: engine `201 00 D0 00 03 40 07 01` (ECU listens on 0x300, tester must send on 0x740) (jazdw, seishuku, scirocco-dash); EPS `209 00 D0 00 03 A8 07 01` (tester must send on 0x7A8) (icanhack); **[added]** Haldex Gen2 1K0: "tester TX 0x764, ECU TX 0x300" (OpenHaldex-C6, below). pq-flasher parses it as `struct.unpack("<xBHHB", dat)` → status, rx, tx, app (little-endian 16-bit IDs: `00 03` = 0x300, `A8 07` = 0x7A8). So the tester-TX id granted by a module is module-specific (0x740, 0x7A8, 0x764 seen) — never assume 0x740.
  - **[added in verification]** A negative setup reply (typically `D7`) "means the module still has a channel open from an earlier, unclosed session. The advertised tx id is still in the reply, so disconnect there and ask again" — i.e. on `D6..D8`, send `A8` to the TX id in bytes 4-5 of the refusal, wait ~300 ms, retry. (src: scirocco-dash tp20.py `_connect_once`)
- Channel parameters (6 bytes or 1 byte): `[Opcode][BS][T1][T2][T3][T4]`; 0xA0 request (6), 0xA1 response (6), 0xA3 channel test (1; reply is a 0xA1 parameter response), 0xA4 break (1), 0xA8 disconnect (1; receiver replies with disconnect). "T1 should be greater than 4*T3", "T2 always 0xFF", "T4 always 0xFF". Timing byte: bits 7-6 = units (0x0 = 0.1 ms, 0x1 = 1 ms, 0x2 = 10 ms, 0x3 = 100 ms), bits 5-0 = scale. Example `A0 0F 8A FF 32 FF`: T1 0x8A = 10 ms×10 = 100 ms, T3 0x32 = 0.1 ms×50 = 5 ms; ECU replies `A1 0F 8A FF 4A FF` (T3 0x4A = 1 ms×10 = 10 ms). pq-flasher and the commercial dongle in the icanhack sniff send `A0 0F 8A FF 0A FF` (T3 = 1 ms); VAG Blocks sends `A0 0F 8A FF 4A FF` (T3 = 10 ms, line 555); seishuku and OpenHaldex-C6 ("Byte values from confirmed VW captures: 0F 8A FF 32 FF") use `32`.
  - **BS semantics are ambiguous between sources:** jazdw's example comment says `0F` = "Tell ECU module to send 16 packets at a time", icanhack says "15 packets between ACKs", EliasTuning says "DEFAULT_BLOCK_SIZE = 0x0F  # 15 packets" with range 1..15, VAG Blocks rejects `param.bs > 0xF`. Treat BS=0x0F as "send up to 15 frames then expect an ACK" and never send more than 15 unacknowledged frames. (OPEN Q.11)
  - **[added in verification]** Timing field experiment on a MED17.5: "T3=0x0A was ACCEPTED by the MED17.5 at handshake and then the channel degraded -- ~6 Hz with multi-second stalls and periodic channel drops, versus a stable 13+ at 5 ms" (T3 = 0x32). Default to `0F 8A FF 32 FF`. (src: scirocco-dash tp20.py)
- Data (2..8 bytes): `[Op<<4 | Seq][payload ≤7]`; Op 0x0 = more follows, expect ACK; 0x1 = last, expect ACK; 0x2 = more, no ACK; 0x3 = last, no ACK; 0xB = ACK ready; 0x9 = ACK not ready. Seq counts 0..0xF and wraps. "The first 2 bytes of the first packet sent contain the length of the message" (big-endian: `00 02`, `00 1A`, `00 30` in the examples). icanhack on the counters: "both tester and ECU have their own counter that persists between transmissions. The counter is incremented after each data transmission. An ACK does not increment any counter, but is expected to use the counter value of the last data transmission that is being acknowledged plus one." ACK byte = `0xB0 | ((received seq + 1) & 0xF)`. pq-flasher: `wait_for_ack` expects `bytes([0xB0 | ((self.tx_seq + 1) & 0xF)])`; `send_ack` sends `0xB0 | ((self.rx_seq + 1) & 0xF)`; segmentation uses `(0x10 if last else 0x20) | tx_seq` + 7 payload bytes; seishuku: `0xB0+(_RxMsg.Data[0]+1&0x0F)`.
- Full worked exchange (engine, measuring block 1): `200 01 C0 00 10 00 03 01` / `201 00 D0 00 03 40 07 01` / `740 A0 0F 8A FF 32 FF` / `300 A1 0F 8A FF 4A FF` / `740 10 00 02 10 89` (KWP startDiagnosticSession 0x89) / `300 B1` / `300 10 00 02 50 89` / `740 B1` / `740 11 00 02 21 01` (readDataByLocalIdentifier group 1) / `300 B2` / `300 21 00 1A 61 01 01 00 00` / `300 22 27 00 00 22 00 80 1A` / `300 23 32 4B 25 02 7A 25 00` / `300 14 00 25 00 00 25 00 00` / `740 B5` / `740 A8`. (src: https://jazdw.net/tp20 — re-fetched, verbatim)
- Second full exchange, EPS on the bench (dongle → 0x7A8, ECU → 0x300), timestamps in s: `0.339 200 09 C0 00 10 00 03 01` / `0.342 209 00 D0 00 03 A8 07 01` / `0.343 7A8 A0 0F 8A FF 0A FF` / `0.352 300 A1 0F 8A FF 4A FF` / `0.407 7A8 10 00 02 10 89` / `300 B1` / `300 10 00 02 50 89` / `7A8 B1` / `7A8 11 00 02 10 89` (sent a second time, seq 1) / `300 B2` / `300 11 00 02 50 89` / `7A8 B2` / `7A8 12 00 02 1A 9B` / `300 B3` / `300 22 00 30 5A 9B 31 4B 30` / `300 23 39 30 39 31 34 34 45` / `300 24 20 20 32 35 30 31 00` / `300 25 00 00 00 00 06 40 16` / `300 26 05 4D 45 50 53 5F 5A` / `300 27 46 4C 53 20 4B 6C 2E` / `300 28 20 31 38 34 20 20 20` / `300 19 20` / `7A8 BA`. Length 0x0030 = 48 bytes = `5A 9B` + 46 bytes ident. (src: https://icanhack.nl/blog/vw-part1/ — re-fetched, verbatim)
- Keep-alive: `740 A3` (channel test) answered by `300 A1 0F 8A FF 4A FF`. (src: https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c lines "// Example: 0x740 1 0xA3" / "// Example: 0x300 6 0xA1 0x0F 0x8A 0xFF 0x4A 0xFF") **[added]** "either side may send A3; the reply is an A1. The ECU drops the channel after roughly a second of silence." (src: scirocco-dash tp20.py) — consistent with `T_CT_AKTIV_MS = 1000` in EliasTuning's constants. Send A3 at least every ~500 ms when idle.
- KWP2000 over TP 2.0 as used on PQ35: session 0x10 with 0x89 (diagnostic), 0x85 (programming), 0x86 (engineering); ReadEcuIdentification 0x1A with 0x9B (ident) / 0x9C (flash status); security 0x27 levels 1/2 (programming seed/key) and 3/4; routines 0x31 with 0xC4 erase flash / 0xC5 calculate flash checksum; NRC table incl. 0x78 responsePending. (src: https://raw.githubusercontent.com/pd0wm/pq-flasher/master/kwp2000.py — re-fetched) — the full KWP service list and semantics belong to another fact sheet; quoted here only because it fixes the ident call used for module discovery: `1A 9B` → `5A 9B` + ASCII `"1K0909144E  2501\0\0\0\0------EPS_ZFLS Kl. 184    "` (README: `ECU identification b'1K0909144E  2501\x00\x00\x00\x00------EPS_ZFLS Kl. 184    '`, `Flash status b'\x00\x1b\x0f\x00--------.--.--'`) (src: https://raw.githubusercontent.com/pd0wm/pq-flasher/master/README.md and https://icanhack.nl/blog/vw-part1/). The first 10 characters of the `5A 9B` payload are the part number without spaces ("1K0909144E"), then 2 spaces, then a 4-digit software version ("2501"). scirocco-dash additionally tries `1A 91` when `1A 9B` fails.

TP 2.0 **logical addresses** — what is actually verified (sources fetched; each line says what kind of evidence it is):

- Engine = `0x01` (response on 0x201): jazdw worked example; seishuku code (`// Example: 0x201 7 0x00 0xD0 ...`); scirocco-dash measured on a 2009 MED17.5; aep's trace of a real VAG tester (`200 [7] 01 C0 00 10 00 03 01`). **Evidence: three independent captures.** (src: https://jazdw.net/tp20 ; https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/5df95ec2114ec10ca7862eacb352a95ea5642f66/board/tp20.py ; https://raw.githubusercontent.com/aep/vag_reverse_engineering/master/LOG.md)
- Electro-mechanical power steering (VCDS address **44**, part 1K0 909 144 E/M/Y, "EPS_ZFLS") answers TP 2.0 channel setup at logical address **0x09** (response on 0x209): sniffed from a commercial dongle — `0.339 0x200 b'09c00010000301' # dongle - Request channel open`, reply on `0x209` `00d00003a80701`, then KWP `10 89` and `1a 9b` returning `1K0909144E  2501 ... EPS_ZFLS Kl. 184`; pq-flasher hard-codes `TP20Transport(p, 0x9, bus=args.bus)` in 01_dump.py (line 29) and 03_flasher.py (lines 57, 70, 113). **Evidence: one sniff of a commercial tool + working code, bench setup (EPS alone, no gateway).** (src: https://icanhack.nl/blog/vw-part1/ ; https://raw.githubusercontent.com/pd0wm/pq-flasher/master/01_dump.py ; https://raw.githubusercontent.com/pd0wm/pq-flasher/master/03_flasher.py — all re-fetched)
- **[added in verification] Haldex Gen2 coupling (VCDS address 22, 1K0 907 554) answers at logical address `0x0A` (response on 0x20A), and `0x22` does not:** "Confirmed from a SavvyCAN/VCDS capture of a 1K0 Gen2 Haldex: the module enumerates at logical address 0x0A and answers on 0x20A. (Address 0x22 / '22-AWD' carried over from the S3 sources did NOT respond on this platform — that reference was misleading.)" `#define KWP_TP20_HALDEX_ADDR 0x0Au // logical (diagnostic) address (confirmed 1K0 Gen2)`; "(confirmed 1K0 Gen2 capture: tester TX 0x764, ECU TX 0x300)"; the project then does `10 89` and `21 <group>` over that channel. **Evidence: code comments describing the author's VCDS capture; the capture itself is not published.** (src: https://raw.githubusercontent.com/Forbes-Automotive/OpenHaldex-C6/b3805750a3cb79e994aec4ac30e52ea4eda7547f/include/OpenHaldexC6_defs.h lines 600-611 ; .../src/OpenHaldexC6_UDS.cpp lines 330-345)
- CAN gateway (VCDS address **19**, 1K0 907 530 R on a Mk5 Jetta) does NOT answer channel setup to 0x19 but DOES answer at **0x1F**: poster fastboatster: "Every time I sent a channel setup message to 0x19 address, I got nothing back." ... "I have recorded a Bluetooth sniff log and it looks like it goes to 0x1F address instead. When I tried to open a diag session with my software and read control unit info, I got: `1K0907530R  0062BJ533  Gateway   H06`"; poster H2Deetoo: "In all VW cars the gateway uses address 0x1F." and "For example clusters are referred to as module 17-Instruments, while their TP20 address is 07h and their UDS ID is 714h."; fastboatster later: "control unit number and address list is returned by CAN Gateway module as a response to KWP request with an SID of 1A and 9F parameter. So CAN Gateway has a number 19 and address of 1F in that list." **Evidence: forum thread, two posters, one of whom reproduced the sniff with his own code (ident string quoted). The cluster = 0x07 claim is a bare assertion → REPORTED.** (src: http://nefariousmotorsports.com/forum/index.php?topic=14242.0 — re-fetched, verbatim)
- The same thread reports that blind channel-setup probing on a FWD Mk5 Jetta "got responses from modules it's not supposed to have like AWD (0x22)" — i.e. on a Mk5 the TP 2.0 destination byte 0x22 is answered by something that is not a Haldex; combined with the OpenHaldex finding (real Haldex at 0x0A, nothing at 0x22 on a 4Motion car) this shows the TP 2.0 address space ≠ address-word space. (src: same)
- VCDS on K-line KWP2000 uses yet another number: for 17-Instruments the sniffed request header was `81 61 F1 1A 92 <cs>` → physical K-line address 0x61 for the cluster. Not relevant on CAN-only cars but shows VCDS translates the address word per transport. (src: http://nefariousmotorsports.com/forum/index.php?topic=9949.0 — re-fetched)
- On the Mk5 Jetta the poster "was able to successfully communicate with the engine, transmission, ABS modules and some others" by TP 2.0 (the destination bytes are not quoted). (src: http://nefariousmotorsports.com/forum/index.php?topic=14242.0)
- **[added in verification] CJAA EDC17CP14 (2012-era 2.0 CR TDI) speaks KWP2000 over TP 2.0 at logical 0x01:** seishuku's `teensycanbusdisplay` README: "Custom aux display for my 2013 VW Jetta TDI, displays turbo pressure, coolant temp, exhaust temp, and DPF soot load. An example of using VW TP2.0 and KWP2000 to poll diagnostic data."; its `vwtpkwp2k.c` opens TP 2.0 to dest `0x01` (`_TxMsg.Data[0]=0x01; // TP2.0 module ID (ECU)`), expects `0x201 ... 0xD0 ... 0x40 0x07`, starts session `10 89` and reads measuring blocks with `21 <LocalID>` (example `0x740 5 0x10 0x00 0x02 0x21 0x72`); and in the NefMoto thread the same author posted his car's VCDS block: `Address 01: Engine (CJA) Labels: 03L-906-022-CBE.clb / Part No SW: 03L 906 019 HE HW: 03L 907 309 AA / Component: R4 2,0L EDC G000SG 4606 / Coding: 0050072`. This is the same ECU family as the owner's 2012 Golf TDI (scan B: `03L 906 019 EE / 03L 907 309 AA / R4 2,0L EDC G000SG 1181`). (src: https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/README.md ; https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c ; http://nefariousmotorsports.com/forum/index.php?topic=9182.0 — all fetched)

#### Reported / unverified (confidence)

##### 2. TP 2.0 logical addresses (the destination byte) — what is known and what is not

Summary table of everything found (VERIFIED rows repeated for one-stop lookup):

| module (VCDS addr) | TP 2.0 dest | reply ID | tester TX id granted | evidence | confidence |
|---|---|---|---|---|---|
| Engine (01) | 0x01 | 0x201 | 0x740 | three captures (§D) | verified |
| EPS 1K0 909 144 (44) | 0x09 | 0x209 | 0x7A8 | one sniff, bench, no gateway | verified-bench; on-car **medium** |
| Haldex Gen2 1K0 907 554 (22) | 0x0A | 0x20A | 0x764 | OpenHaldex-C6 code comment citing a VCDS/SavvyCAN capture; 0x22 silent | high |
| Gateway 1K0 907 530 (19) | 0x1F | 0x21F | ? | forum sniff + reproduction, second poster agrees | high |
| Cluster (17) | 0x07 | 0x207 | ? | single forum assertion (H2Deetoo), no sniff quoted | **medium** |
| ABS MK60 (03) | 0x03 | 0x203 | 0x740 (emulator default) | a hobbyist "MK60 PQ35 ABS emulator" uses `kAbsLogicalAddr = 0x03` and claims it "answers the gateway/scanner without the ABS dropping out of the installation list" (src: https://raw.githubusercontent.com/pandolfipedro/pq35-abs-emulator/33c43fb40cde5c21dd4565f5b3104f932a81d217/pq35-abs-emulator/pq35-abs-emulator.ino) — the author's choice may be an assumption | **medium** |
| Transmission (02) | 0x02 ? | | | NefMoto OP "was able to communicate with ... transmission" while assuming address words; bytes not quoted | **medium-low** |
| everything else (08, 09, 0F, 15, 16, 25, 37, 42/52/62/72, 46, 47, 55, 56, 65, 1C, 2E, 4F, 76, 77, 7D) | unknown | | | no table found anywhere | — |

- **low, conflicting**: a GitHub ESP32 project carries a table `{0x20, "Central Electrics (BCM)", 0x70C, 0x776} // Corrected (UDS 70C/776, TP2.0 20)`, `{0x1F, "Gateway J533", 0x710, 0x77A} // Corrected (TP2.0 1F)`, `{0x28, "Steering Assist", 0x712, 0x77C} // Corrected (TP2.0 28)`, `{0x33, "ACC / Auto Distance", 0x757, 0x7C1} // Corrected (TP2.0 33)`, `{0x42, "Driver Door Electronics", 0x711, 0x77B} // Added (UDS 711/77B)`. Its EPS = 0x28 contradicts the sniffed 0x09, its BCM UDS ID 0x70C contradicts ODIS (0x70C is the steering-column module; BCM is 0x70E), and 0x711 is the immobilizer, not a door. Provenance unknown ("Corrected" by whom is not stated). Do NOT use; listed so nobody re-imports it. (src: https://raw.githubusercontent.com/Abricosvw/Dashboard_P5/02ea1d693389d5715bd0c2dd8cbc6456b4c2b8d2/main/diagnostic_tester.c — fetched)
- **medium**: the Mk5 gateway returns the installed-module list as a KWP2000 ReadEcuIdentification `1A 9F` response (one forum poster who sniffed a commercial app and reproduced it; quoted in §D). The byte layout of the `5A 9F ...` response was NOT given and no open-source parser was found (GitHub code search for `1A 9F`, `0x9F` + gateway, and "Verbauliste" returned nothing relevant). What would confirm: send `1A 9F` on a TP 2.0 channel to dest 0x1F and dump the reply; expect repeated records containing (address word, TP 2.0 address, status) — the R32 should yield 22 entries matching the coding decode in VERIFIED §E, and the status should reproduce VCDS's `0000` / `0010` / `1100` words.
- **medium**: KWP `1A` sub-identifiers other than 0x9B/0x9C are used by VAG tools: the ABS emulator answers `1A 91`, `1A 9B`, `1A 87`, `1A 90` all with its part-number string (`1K0907379 0143`) and everything else with `5A xx "OK"`, implying the scanner/gateway it was tested against sends some of those; scirocco-dash falls back from `1A 9B` to `1A 91`. (src: pq35-abs-emulator.ino; scirocco-dash tp20.py) What would confirm: trace VCDS opening any KWP module.
- **medium**: because address-word ≠ logical address, the implementation must keep a per-car table `{address_word: tp20_logical}` learned from `1A 9F` or from a probe, and must not assume `0x200 + address_word`.
- **low**: whether the EPS keeps logical 0x09 on the car (behind the gateway) — on a bench it had no gateway. The gateway may re-map. Confirm with a trace of VCDS opening 44.
- **low**: an open-source tool (kw1281-can-extension) scans TP 2.0 dests 0x01..0x7F and, when `1A 9B` fails on an open channel, tries **UDS `22 F187` tunnelled inside TP 2.0** ("UDS over TP2.0"). No evidence any VAG module accepts UDS payloads over TP 2.0; listed as an idea only. (src: https://raw.githubusercontent.com/eszakivizikigyo/kw1281-can-extension/8db9573d94a553fab43ef813b44a68c46ec3d192/Cli/Program.cs)
- **medium**: a 2009 MED17.5 engine ECU "answers generic OBD-II on ISO-TP but ignores UDS" (scirocco-dash README/docstring: "its manufacturer diagnostics are KWP2000 carried over VW's proprietary TP 2.0 transport"). Supports the expectation that the R32's older ME7.1.1 also answers only OBD-II modes on 0x7E0 — but MED17.5 ≠ ME7.1.1; test (OPEN Q.7).


### 7.4 Gateway installation list (Mk5 1K0 907 530 long coding; 7N0 907 530)

Source sheets: `addresses.md` §E (three coding layouts re-read bit by bit; three real-car cross-checks bit-exact), `ecus.md` §I, `tp20.md` Reported.

#### Verified (source)

##### E. Gateway installation list

- **Mk5 gateway 1K0 907 530 (KWP)**: the installation list IS the long coding; Ross-Tech documents three layouts by hardware index. **Verification pass: all three layouts below were re-read bit by bit against the page (oldid=4359) and match.** (src: http://wiki.ross-tech.com/wiki/index.php/VW_Golf_(1K)_CAN-Gateway)

  Layout 1 — "Coding (through Index F)", 7 bytes:
  - Byte 00: bit0 [01] Engine, bit1 [02] Transmission, bit2 [03] ABS, bit3 [00] Steering Angle Sensor (G85), bit4 [15] Airbags, bit5 [44] Steering Assist, bit6 [55] Xenon Range, bit7 [22] AWD
  - Byte 01: bit0 [09] Central Electronics, bit1 [46] Central Convenience, bit2 [42], bit3 [52], bit4 [62], bit5 [72], bit6 [36] Seat Memory Driver, bit7 [65] TPMS
  - Byte 02: bit0 [16] Steering Wheel, bit1 [08] Climate, bit2 [76] Parking Aid, bit3 [7D] Aux Heating, bit4 [18] Aux Heater, bit5 [26] Auto Roof, bit6 [69] Trailer, bit7 [06] Seat Memory Passenger
  - Byte 03: bit0 [3D] Special Function, bit1 [47] Sound System, bit2 [75] Telematics, bit3 [37] Navigation, bit4 [57] TV-Tuner, bit5 [0F] Radio digital, bit6 [56] Radio analog, bit7 [77] Telephone
  - Byte 04: bit0 [17] Instrument Cluster, bit1 [25] Immobilizer, bit2 [19] CAN-Gateway, bit3 [1C] Position Sensing, bit4 [5D] Operations
  - Byte 05 Manufacturer/Model; Byte 06 Options.

  Layout 2 — "Coding (from Index F through Index K)", 8 bytes: Bytes 00..03 identical to layout 1; Byte 04 adds bit5 [14] Suspension Electronics, bit6 [4C] TPMS II, bit7 [11] Engine II; Byte 05: bit0 [10] Park/Steering Assistant, bit1 [63] Easy Entry Driver, bit2 [73] Easy Entry Passenger; Byte 06 Manufacturer/Model; Byte 07 Options.

  Layout 3 — "Coding (from Index L)", 9 bytes:
  - Byte 00: bit0 [01], bit1 [11], bit2 [02], bit3 [03], bit4 [53] Parking Brake, bit5 [04] Steering Angle Sensor (G85), bit6 [44], bit7 [15]
  - Byte 01: bit0 [55], bit1 [22], bit2 [13] Distance Regulation, bit3 [14], bit4 [4C], bit5 [10], bit6 [32] Differential Locking, bit7 [17]
  - Byte 02: bit0 [25], bit1 [09], bit2 [46], bit3 [42], bit4 [52], bit5 [62], bit6 [72], bit7 [36]
  - Byte 03: bit0 [65], bit1 [16], bit2 [08], bit3 [76], bit4 [7D], bit5 [26], bit6 [69], bit7 [06]
  - Byte 04: bit0 [3D] (the wiki prints "Byte 03 Bit 0" here — confirmed present on the re-fetched page; an obvious typo for Byte 04 Bit 0), bit1 [6D] Trunk Electronic, bit2 [63], bit3 [73], bit4 [47], bit5 [75], bit6 [37], bit7 [57]
  - Byte 05: bit0 [0F], bit1 [56], bit2 [77], bit3 [18], bit4 [1C], bit5 [5D], bit6 [6C] Rear View Camera, bit7 [59] Tow Protection
  - Byte 06: bit0 [4F] Central Electronics II, bit1 [19] CAN-Gateway (Standard), bit2 [3C] Lane Change Assist, bit3 [5C] Lane Maintenance Assist
  - Byte 07 Manufacturer/Model; Byte 08 Options.

- Cross-check 1 — Layout 3 on the real 2008 R32 (gateway `1K0 907 530 L`, index L, coding `ED831F075003020000`, src: https://forums.ross-tech.com/index.php?threads/3627/): Byte0 0xED → 01,02,03,04,44,15; Byte1 0x83 → 55,22,17; Byte2 0x1F → 25,09,46,42,52; Byte3 0x07 → 65,16,08; Byte4 0x50 → 47,37; Byte5 0x03 → 0F,56; Byte6 0x02 → 19. That is exactly the set VCDS listed for the car (`Scan: 01 02 03 08 09 0F 15 16 17 19 22 25 37 42 44 46 47 52 55 56` plus `04-Steering Angle -- Status: OK` and `65-Tire Pressure -- Status: OK`). Bit-exact match, 22 of 22. (derived; re-checked)
- **[added in verification]** Cross-check 2 — Layout 2 on a Mk5 Golf 2.0 TDI 4Motion (gateway `1K0 907 530 H`, index H, `J533__Gateway H12 0150`, coding `FD3F0F4007000002`, 8 bytes): Byte0 0xFD → 01,03,00(G85),15,44,55,22 (bit1 = 0: manual gearbox); Byte1 0x3F → 09,46,42,52,62,72; Byte2 0x0F → 16,08,76,7D; Byte3 0x40 → 56; Byte4 0x07 → 17,25,19; Bytes 5,6 = 00; Byte7 0x02. VCDS printed `Scan: 01 03 08 09 15 16 17 19 22 25 42 44 46 52 55 56 62 72 76 7D` — bit-exact, 20 of 20 (G85 is not scanned as a module). (src: https://forums.tdiclub.com/index.php?threads/vw-golf-mkv-2-0tdi-4motion-rear-door-module-errors.406046/ — fetched)
- **[added in verification]** Cross-check 3 — a **10-byte** coding on a late 1K0 gateway: 2010 Jetta TDI (scan C) gateway `1K0 907 530 AA`, `J533 Gateway H07 0081`, labels 1K0-907-530-V4.clb, coding `ED807F07001602002002` (20 hex chars). Decoding bytes 0-6 with Layout 3: Byte0 0xED → 01,02,03,04,44,15; Byte1 0x80 → 17; Byte2 0x7F → 25,09,46,42,52,62,72; Byte3 0x07 → 65,16,08; Byte4 0x00; Byte5 0x16 → 56,77,1C; Byte6 0x02 → 19. VCDS printed `Scan: 01 02 03 08 09 15 16 17 19 1C 25 42 44 46 52 56 62 65 72 77` — bit-exact, 20 of 20. Bytes 7-9 (`00 20 02`) are therefore Manufacturer/Model, Options, and a third byte whose meaning the Ross-Tech page does not document (OPEN Q.12). The Ross-Tech forum thread's `1K0 907 530 S` example `E9807F06500602002103` is also 10 bytes and decodes plausibly with Layout 3 (01,03,04,44,15 / 17 / 25,09,46,42,52,62,72 / 16,08 / 47,37 / 56,77 / 19) for that A3's `Scan: 01 03 08 09 15 16 17 19 25 37 42 44 46 47 52 56 62 72 77` — bit-exact, 19 of 19. (src: https://forums.tdiclub.com/showthread.php?p=4298172 ; https://forums.ross-tech.com/index.php?threads/12357/ — both re-fetched; derivation mine)
- **Mk6/late gateway 7N0 907 530 (as fitted to 2011+ PQ35)**: coding is only 3 bytes (6 hex characters, e.g. `Coding: 350002` on the 2012 Golf TDI, `461000` on the 2012 Passat NMS; src: scans B and D) and the installation list is NOT in the coding. Ross-Tech's Uwe: "Three bytes of new Gateway's coding define characteristics of car and should be documented in Long Coding Helper, while Installation List needs to be done separately using the dedicated function for that." A poster replacing `1K0 907 530 S` (20-character coding `E9807F06500602002103`) with `7N0907530AK`: "new unit won't accept all of that code (from memory only 6 characters)"; another: "You can't just copy the old code, it won't work as the new gateway has different byte length than the old one ... manually check the right boxes in installation list." (src: https://forums.ross-tech.com/index.php?threads/12357/ — re-fetched; the "only 6 characters" is the poster's recollection, the two 7N0 scans confirm 6 hex chars)

- Mk5 gateway installation list = long coding (layouts verified in `addresses.md` §E). No open source documents a `1A 9F` reply layout (GitHub/Web searches this session: none) — remains Q11.

#### Reported / unverified (confidence)

- **medium**: the Mk5 gateway returns the installed-module list as a KWP2000 ReadEcuIdentification `1A 9F` response (one forum poster who sniffed a commercial app and reproduced it; quoted in §D). The byte layout of the `5A 9F ...` response was NOT given and no open-source parser was found (GitHub code search for `1A 9F`, `0x9F` + gateway, and "Verbauliste" returned nothing relevant). What would confirm: send `1A 9F` on a TP 2.0 channel to dest 0x1F and dump the reply; expect repeated records containing (address word, TP 2.0 address, status) — the R32 should yield 22 entries matching the coding decode in VERIFIED §E, and the status should reproduce VCDS's `0000` / `0010` / `1100` words.

R-I1. Gateway `1A 9F` installation-list reply layout: unknown (sibling medium that the service exists). Q11.

- **Gateway behaviour on PQ35**: 0x200 setup frames from the OBD port are routed by the J533 gateway to the target module's bus; the gateway does not alter TP 2.0 (PQF README notes the gateway *does* block CCP: "can't be done through the OBD-II port since there is a gateway that blocks the CCP addresses"). The Skoda paper says "the Gateway Module (GM) will only allow specific data requested to flow to the OBD-II port". Confidence *medium*. Confirm by sniffing the powertrain bus directly (J533 harness) while opening a channel from OBD.
- **Gateway installed-module list**: "control unit number and address list is returned by CAN Gateway module as a response to KWP request with an SID of 1A and 9F parameter. So CAN Gateway has a number 19 and address of 1F in that list." (NEFM-GW, single forum post, no bytes shown). Confidence *medium*; a cheap autoscan primer if it works — confirm by sending `1A 9F` to 0x1F and logging the reply.


### 7.5 KWP identification: `1A` options and the `5A 9B` / `5A 91` / `5A 9A` / `5A 9F` record layouts

Source sheet: `kwp_vag.md` §2 (option table from fetched code; byte-exact `5A 9B` layout fitted to three real dumps).

#### Verified (source)

##### 2. ReadEcuIdentification 0x1A

- Request `1A <identificationOption>`, positive response `5A <identificationRecordValue…>`; ISO leaves options 80-FF and the record content to the manufacturer. (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §6.6). Every VAG implementation echoes the option as byte 2 of the response (`5A 9B …`, `5A 91 …`, `5A 9A …`): VB `if (param == 0x91) shortIdHandler… else if (param == 0x9B) longIdHandler… else if (param == 0x9F) queryModulesHandler`. (src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp)
- **Option table as seen in fetched code** (names are the tools' own):

| option | name in code | who uses it |
|---|---|---|
| 0x86 | "Extended Ident" (PY kwp_trace), "retained Carista KWP debug … 86" (PC) | PY, PC, SC ident_dump |
| 0x87, 0x88, 0x89, 0x8A | probed by SC `ident_dump` (no decode) | SC |
| 0x90 | "ISO-standard vehicleIdentificationNumber" — SC tries 0x90 first for the VIN, then falls back to picking a 17-char token out of 0x9B/0x91 text | SC |
| 0x91 | hardware number / "Read raw VAG number (ECU ID)" (PY), `ECUIdentification_hardwareNumber` (DV), `ECU_ID` (VDS) | VB, PY, DV, VDS, SC |
| 0x92 | "System Supplier Hardware ID" (PY); B3 reads `1A 92` and sums bytes 2..6 of the reply for its seed/ECU-id | PY, B3 |
| 0x94 | "System Supplier Software ID" (PY) | PY, SC |
| 0x95–0x97 | probed by SC | SC |
| 0x9A | "Unknown (0x9A)" (PY), `KWP_ECU_ID_VAG_NUMBER_3` (VDS), "Carista VAG CAN long coding" (PC) | PY, VDS, PC, SC |
| 0x9B | "ECU Ident" (PY), `ECU_IDENT` (PQF), `ECUIdentification_standardIdentification` (DV), `COMPONENT_ID` (VDS), "Carista VAG CAN ECU info" (PC) | everyone |
| 0x9C | "Flash Status" (PY), `STATUS_FLASH` (PQF) | PY, PQF |
| 0x9F | `ECUIdentification_installationList` (DV), gateway module list (VB), "Carista VAG CAN ECU list" (PC) | VB, DV, PC |

(src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/kwp_trace.py ; https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP2000_SID.h ; https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://raw.githubusercontent.com/victorwitkamp/PoloCornering/main/obd-on-pc/decode_diagnostic_payload.py ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java ; https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp)

- **`5A 9B` reply layout, byte-exact** (offsets counted from the first byte after `5A 9B`; DV's emulator is the only *commented* source, and three real dumps fit it exactly):

| offset | len | content | DV comment |
|---|---|---|---|
| 0 | 11 | VAG part number, ASCII, right-padded with spaces (e.g. `1K0907115L ` = 10 chars + 1 space) | "Software version" (sic — it is the part number) |
| 11 | 1 | `0x20` | "Constant" |
| 12 | 4 | software version, 4 ASCII digits (`0030`, `2501`, `6243`, `0010`) | "Programming status" |
| 16 | 1 | coding type: `0x00` no coding, `0x03` short coding, `0x10` long coding | "Coding (00 - no coding, 03 - short coding, 10 - long coding)" |
| 17 | 1 | `0x00` | "Constant" |
| 18 | 2 | short coding, big-endian (`00 AC` = 172 on the ME7 dump); zero when long coding | "Short coding (high byte, low byte)" |
| 20 | 6 | WSC / importer / equipment number, packed (see REPORTED for the bit layout) | "WSC, Imp., Geraet" |
| 26 | n | component/identification text, ASCII, space padded (`2.0l R4/4V TFSI    `, `MOTRONIC ME7.1.*G   `, `KWP1281<->VWTP2.0  `) | "Identification" |

  DV: `'K','W','P','E','M','U','0','0','1',' ',' ', 0x20, '0','0','0','0', 0x00 /*coding*/, 0x00, 0x00,0x00 /*short coding*/, 0x00×6 /*WSC, Imp., Geraet*/, "KWP1281<->VWTP2.0  "` with total length `0x30` = 48. Real ME7 (022 906 032 GK, K-line): `30 32 32 39 30 36 30 33 32 47 4B | 20 | 36 32 34 33 | 03 | 00 | 00 AC | 00 00 00 00 19 23 | 4D 4F 54 52 4F 4E 49 43 20 4D 45 37 2E 31 2E 2A 47 20 20 20` ("022906032GK", " ", "6243", 03, 00, 00AC, 6 bytes, "MOTRONIC ME7.1.*G   "). Real PQ35 engine over TP 2.0 (NEFM-9182, length 0x30): `31 4B 30 39 30 37 31 31 35 4C 20 | 20 | 30 30 33 30 | 10 | 00 00 00 | 00 06 46 22 04 F5 | 32 2E 30 6C 20 52 34 2F 34 56 20 54 46 53 49 20 20 20 20 20` ("1K0907115L ", " ", "0030", 10 = long coding, zero short coding, 6 bytes, "2.0l R4/4V TFSI    " — 48 bytes incl. `5A 9B`). VDS (sniffed Audi 8P): `5A 9B "8P0907115AQ" 20 "0010" 10 00 00 00 01 DC 5A 10 00 BF "2.0l R4/4V TFSI    "`. VB `longIdHandler` reads the part number as bytes 0..15 and the component text from byte 26 to the end (trailing spaces chopped); PY `readPN` takes `req[2:14]` (= offsets 0..11 of the payload) and `req[0x1c:]` (= offset 26) as the name; PC decodes `value[0x10]` (offset 16) as "coding_type_selector" and `value[0x14:0x1A]` (offsets 20..25) as "initial_value6" ([added] PC's `value = data[2:]` with `data` starting at `5A`, so its indices are the same payload offsets as this table; it also takes `value[:12]` as the part-number ASCII). [added] Basano's logger printed, directly under the raw 9B frames of the NEFM-9182 capture, the decoded lines `1K0907115L  0030`, `1269`, `785`, `200`, `2.0l R4/4V TFSI` — i.e. its decoder turns the 6 bytes `00 06 46 22 04 F5` into WSC 1269 / importer 785 / equipment 200 (see REPORTED for the bit packing that reproduces this). (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/responses.h ; https://www.blafusel.de/obd/vag_kw2000.html ; http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2 (frames quoted in tp20.md §7) ; https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/victorwitkamp/PoloCornering/main/obd-on-pc/decode_diagnostic_payload.py)
- The nefariousmotorsports description of the same record from a VAG document: bytes 1…11 "VW / Audi-Part number 7 Bit-ASCII", 12 "Space (0x20)", 13…16 "Configuration Program status and programmability / Data status", "Byte 17 contains the number of coding table and the length of coding information, Byte 18 to 20 is coding in hex" (1-based numbering, consistent with the table above: byte 17 = offset 16 = coding type/length, bytes 18-20 = offsets 17..19). (src: http://nefariousmotorsports.com/forum/index.php?topic=14547.0;wap2)
- The EPS example `1K0909144E  2501` from the ICH blog and the engine `1K0907115L  0030` are exactly offsets 0..15 printed as text (11-char part number + space + 4-digit version). (src: http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2 ; https://icanhack.nl/blog/vw-part1/ as quoted in tp20.md)
- **`5A 91` reply** = a sequence of length-prefixed ASCII records terminated by `0xFF`, where the length byte counts itself: VDS `5A 91 0E "8P0907115B" 20 20 20 FF` (0x0E = 14 = 1 + 13 chars); DV `5A 91 0E 'HW000      ' 20 20 FF`; VB `shortIdHandler`: `len = data[i]; for j in 1..len-1 collect chars; i += len; stop at 0xFF`; PY: `l = req[2]; pn = req[3:2+l] #length byte includes itself...`. The record is the hardware number (DV name) / "VAG Number" as VCDS prints it. (src: https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/responses.h ; https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py)
- PY falls back from `1A 9B` to `1A 91` when 9B fails ("Fault retrieving full ID block, falling back to plain part number!"); VB requests 9B then 91 after every session start; SC tries 9B then 91. (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py)
- **`5A 9A` reply (long coding)**, as the sniff-derived simulator sends it: `5A 9A 01 DC 5A 10 00 BF 30 30 31 30 10 09 01 03 00 0C 18 0F 01 60 FF` — i.e. the same 6 WSC/imp/equipment bytes as in 9B (`01 DC 5A 10 00 BF`), the 4-digit sw version `0010`, the coding-type byte `10`, then `09` and 8 bytes `01 03 00 0C 18 0F 01 60`, then `FF`. PC labels option 0x9A "Carista VAG CAN long coding". (src: https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://raw.githubusercontent.com/victorwitkamp/PoloCornering/main/obd-on-pc/decode_diagnostic_payload.py). Interpretation of `09` + 8 bytes is in REPORTED.
- **`5A 9F` gateway installation list** (sent to the J533 gateway, TP 2.0 dest 0x1F): VB sends `1A 9F` right after opening the channel to module 31 (0x1F) and parses the reply with `interpretRawData` (same len-prefixed-records-until-0xFF rule as 0x91) expecting exactly 2 records; record 0 is a list of **4-byte entries** `[moduleNumber, tp20Address, ?, flags]` where `flags & 0x01` = module present and `(flags & 0x1E) >> 1` = status; entries with address 0x13 are skipped ("module numbers 0x0 and 0x4 seem to report this addr but these modules dont exist"); only entries with flags != 0 are kept. VB then closes the gateway channel and opens the chosen module by `tp20Address`. (src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp)
- VAG modules answer `1A xx` for unknown options with a negative response: DV's emulator returns `7F 1A 11` for anything but 0x91/0x9B; PY's bruteforce treats `7F …` as "invalid group or something". (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/responses.h ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py)

#### Reported / unverified (confidence)

- **WSC / importer / equipment packing in the 6-byte block** (offsets 20..25 of `5A 9B`, same block in `5A 9A` and in the adaptation `31 BB … save`): treat the 6 bytes as a 48-bit big-endian integer `v`; **WSC = v & 0x1FFFF (17 bits), importer = (v >> 17) & 0x3FF (10 bits), equipment = v >> 27 (21 bits)**. Derived in this session from the four samples: blafusel ME7 `00 00 00 00 19 23` → WSC 06435 / 000 / 00000; NEFM 1K0907115L `00 06 46 22 04 F5` → 01269 / 785 / 00200; VDS 8P0907115AQ `01 DC 5A 10 00 BF` → 00191 / 264 / 15243; B3 save block `00 00 04 50 10 34` → 04148 / 552 / 00000. The alternative orders (WSC in the top bits, or little-endian) give equipment numbers > 99999 for two of the samples. Supporting: the KWP1281 formula ids 0x38/0x39 "Code for WSC16=0 / =1" show WSC is a 17-bit quantity. [corrected — corroborated] Basano's logger output in NEFM-9182 prints `1269 / 785 / 200` directly under the `00 06 46 22 04 F5` frames, exactly what this packing yields (re-computed in the verification pass: NEFM → (1269, 785, 200), blafusel → (6435, 0, 0), VDS → (191, 264, 15243), B3 → (4148, 552, 0)); that decoder is independent of this sheet but its own provenance (VCDS-matched or not) is unknown. Confidence raised to **high**, still not VERIFIED because no fetched source pairs the bytes with a VCDS "Shop #" line. Confirm: read `1A 9B` on a module whose VCDS "Shop #: WSC xxxxx yyy zzzzz" line is known and compare.
- **`5A 9A` long-coding record layout**: `[6 bytes WSC/imp/equip] [4 ASCII sw version] [coding type 0x10] [len byte, counting itself: 0x09] [8 coding bytes] [0xFF]` — from the single VDS sample `01 DC 5A 10 00 BF 30 30 31 30 10 09 01 03 00 0C 18 0F 01 60 FF`; the 8 bytes look like a MED9 engine long coding (compare the well-known Audi A3 2.0T pattern `0403010A180F0160`). Confidence **medium** (one sniffed sample, no decoder). Confirm: `1A 9A` on the R32 engine (long-coding ECU, VCDS shows 8-byte coding) and the Golf TDI's TP 2.0 modules.

- **medium**: KWP `1A` sub-identifiers other than 0x9B/0x9C are used by VAG tools: the ABS emulator answers `1A 91`, `1A 9B`, `1A 87`, `1A 90` all with its part-number string (`1K0907379 0143`) and everything else with `5A xx "OK"`, implying the scanner/gateway it was tested against sends some of those; scirocco-dash falls back from `1A 9B` to `1A 91`. (src: pq35-abs-emulator.ino; scirocco-dash tp20.py) What would confirm: trace VCDS opening any KWP module.


### 7.6 UDS identification: DID catalogue, VAG DIDs, coding DID 0x0600, workshop code / fingerprint, OBD-mirror DIDs

Source sheet: `uds_vag.md` §M/§N/§R and `ecus.md` R-I2. Response strings quoted from VW_Flash testdata are **simulated** Simos18 values — they prove the request/response shape, not what the owner's modules return.

#### Verified (source)

##### M. DID catalogue (ReadDataByIdentifier 0x22 / WriteDataByIdentifier 0x2E)

Standard ISO identification DIDs 0xF180-0xF1FF — spot-checked against did.html this session
(names present and matched: 0xF180 BootSoftwareIdentification, 0xF184 applicationSoftwareFingerprint,
0xF187 vehicleManufacturerSparePartNumber, 0xF190 VIN, 0xF192 systemSupplierECUHardwareNumber,
0xF197 systemNameOrEngineType, 0xF198 repairShopCodeOrTesterSerialNumber, 0xF199 programmingDate,
0xF19F EntityData). Full table (src:
https://uds.readthedocs.io/en/latest/pages/knowledge_base/did.html):

| DID | Name |
|-----|------|
| 0xF180 | bootSoftwareIdentification |
| 0xF181 | applicationSoftwareIdentification |
| 0xF182 | applicationDataIdentification |
| 0xF183 | bootSoftwareFingerprint |
| 0xF184 | applicationSoftwareFingerprint |
| 0xF185 | applicationDataFingerprint |
| 0xF186 | ActiveDiagnosticSession |
| 0xF187 | vehicleManufacturerSparePartNumber |
| 0xF188 | vehicleManufacturerECUSoftwareNumber |
| 0xF189 | vehicleManufacturerECUSoftwareVersionNumber |
| 0xF18A | systemSupplierIdentifier |
| 0xF18B | ECUManufacturingDate |
| 0xF18C | ECUSerialNumber |
| 0xF18D | supportedFunctionalUnits |
| 0xF18E | vehicleManufacturerKitAssemblyPartNumber |
| 0xF190 | VIN |
| 0xF191 | vehicleManufacturerECUHardwareNumber |
| 0xF192 | systemSupplierECUHardwareNumber |
| 0xF193 | systemSupplierECUHardwareVersionNumber |
| 0xF194 | systemSupplierECUSoftwareNumber |
| 0xF195 | systemSupplierECUSoftwareVersionNumber |
| 0xF197 | systemNameOrEngineType |
| 0xF198 | repairShopCodeOrTesterSerialNumber |
| 0xF199 | programmingDate |
| 0xF19A | calibrationRepairShopCode/CalibrationEquipmentSerialNumber |
| 0xF19B | calibrationDate |
| 0xF19C | calibrationEquipmentSoftwareNumber |
| 0xF19D | ECUInstallationDate |
| 0xF19E | ODXFileIdentifier |
| 0xF19F | EntityDataIdentifier |

VAG-specific DIDs actually enumerated by VW_Flash `data_records` (src:
https://raw.githubusercontent.com/bri3d/VW_Flash/master/lib/constants.py — re-read this
session; list reproduced exactly, including the two VW_Flash `parse_type` values: 0=string,
1/2=binary):

| DID | VW meaning (VW_Flash label) |
|-----|-----------|
| 0xF190 | VIN Vehicle Identification Number |
| 0xF19E | ASAM/ODX File Identifier |
| 0xF1A2 | ASAM/ODX File Version |
| 0xF40D | Vehicle Speed |
| 0xF806 | Calibration Verification Numbers |
| 0xF187 | VW Spare Part Number |
| 0xF189 | VW Application Software Version Number |
| 0xF191 | VW ECU Hardware Number |
| 0xF1A3 | VW ECU Hardware Version Number |
| 0xF197 | VW System Name Or Engine Type |
| 0xF1AD | Engine Code Letters |
| 0xF1AA | VW Workshop System Name |
| 0x0405 | State Of Flash Memory |
| 0x0407 | VW Logical Software Block Counter Of Programming Attempts |
| 0x0408 | VW Logical Software Block Counter Of Successful Programming Attempts |
| 0x0600 | **VW Coding Value (long coding)** |
| 0xF186 | Active Diagnostic Session |
| 0xF18C | ECU Serial Number |
| 0xF17C | VW FAZIT Identification String |
| 0xF442 | Control Module Voltage |
| 0xEF90 | Immobilizer Status SHE |
| 0xF1F4 | Boot Loader Identification |
| 0xF1DF | ECU Programming Information |
| 0xF1F1 | Tuning Protection SO2 |
| 0xF1E0 | (unlabeled in source) |
| 0x12FC | (unlabeled) |
| 0x12FF | (unlabeled) |
| 0xFD52 | (unlabeled) |
| 0xFD83 | (unlabeled) |
| 0xFDFA | (unlabeled) |
| 0xFDFC | (unlabeled) |
| 0x295A | Vehicle Mileage |
| 0x295B | Control Module Mileage |
| 0xF15B | Fingerprint and Programming Date |
| 0xF1A5 | VW Coding Repair Shop Code Or Serial Number (Coding Fingerprint) |
| 0xF1AB | VW Logical Software Block Version |
| 0xF804 | Calibration ID |
| 0xF17E | ECU Production Change Number |

- Real response bytes (captured in VW_Flash fake-connection `testdata`, re-read this
  session; src: lib/constants.py). These are **simulated** values from the VW_Flash fake
  connection, representative of a Simos18 petrol ECU — they confirm the request/response
  SHAPE, not that the owner's cars return these exact strings:
  - `22 F1 90` → `62 F1 90` + "3VW12345678912345" (VIN, 17 chars)
  - `22 F1 87` → `62 F1 87` + "8V0906264M " (spare part number)
  - `22 F1 89` → `62 F1 89` + "0004" (sw version)
  - `22 F1 91` → `62 F1 91` + "06L907309B " (hw number)
  - `22 F1 A3` → `62 F1 A3` + "H31" (hw version)
  - `22 F1 97` → `62 F1 97` + "R4 2.0l TFSI " (system name — note: petrol Simos, not TDI)
  - `22 F1 AD` → `62 F1 AD` + "DGUA" (engine code letters)
  - `22 F1 9E` → `62 F1 9E` + "EV_ECM18TFS0208V0906264L\x00" (ODX id)
  - `22 F1 A2` → `62 F1 A2` + "001004" (ODX version)
  - `22 F1 7C` → `62 F1 7C` + "ZSC-86415.07.18784303 20" (FAZIT)
  - `22 F1 F4` → `62 F1 F4` + "MDG1  CB.06.031.5 013.00     " (bootloader id)
  - `22 06 00` → `62 06 00 09 19 00 12 24 26 00 0E 30 04` (**long coding value, 10 bytes**)
  - `22 F1 A5` → `62 F1 A5 00 00 03 78 1F D7` (coding fingerprint / WSC+serial, 6 bytes)
  - `22 04 05` → `62 04 05 00` (state of flash memory, 1 byte)
  - `22 F1 5B` → `62 F1 5B` + five repeats of the 10-byte record `20 07 17 42 04 20 42 B1 3D 00`
    (see §N)
- **Coding read**: `22 06 00` → `62 06 00 <coding bytes...>`; coding length is
  module-dependent (10 bytes in this capture). CONFIRMED (testdata).

##### N. Workshop code / fingerprint layout (0xF15B, 0xF1A5, 0xF198/0xF199)

Re-read from VW_Flash workshop_code.py this session (src:
https://raw.githubusercontent.com/bri3d/VW_Flash/master/lib/workshop_code.py):
- 0xF15B "Fingerprint and Programming Date" is a concatenation of fixed **10-byte** records
  (`[payload[i:i+10] for i in range(0, len, 10)]`); the workshop code itself is **bytes
  0..8 (9 bytes)** of each record, the 10th byte is padding:
  - bytes0-2 = flash date, **BCD-coded** (`convert_from_bcd(year), month, day`),
  - byte3 = CRC8 of the ASW blocks flashed (`asw_checksum`),
  - bytes4-7 = CAL ID / 4 user bytes (`cal_id = workshop_code[4:8]`),
  - byte8 = CRC8 of bytes0-7 (`workshop_code_is_valid` = `crc8_hash(code[0:8]) == code[8]`).
  CONFIRMED verbatim, including the field slicing.
- CRC8 is table-driven, **polynomial 0x07, init 0** (SMBus/CRC-8): confirmed because
  `crc8_table[1] == 0x07` in the source table and `crc8_hash` does
  `sum = table[sum ^ byte]`. CONFIRMED.
- Captured record `20 07 17 42 04 20 42 B1 3D 00`: date 2020-07-17, ASW-CRC 0x42,
  CAL-ID/user bytes `04 20 42 B1`, workshop CRC 0x3D, pad 0x00. CONFIRMED against testdata.
  (Note: workshop_code.py has a legacy-detect branch: `if code[3]==0x42 and code[4]==0x04`
  it flags the code as "old"; that matches this capture, so VW_Flash would read this sample
  as an older-format fingerprint.)
- 0xF198 repairShopCodeOrTesterSerialNumber and 0xF199 programmingDate are the standardized
  ISO equivalents written during reprogramming (CONFIRMED present in did.html). VAG also uses
  0xF15A (coding log, per CLAUDE.md) / 0xF15B (programming log) and 0xF1A5 (coding
  fingerprint: WSC + serial). The WSC "5-digit workshop code / 3-digit importer" meaning is
  REPORTED (see below; option_screen.php was fetched but the exact WSC digit breakdown
  wording was not isolated).

##### R. OBD-II (mode 01/03/09) for the generic layer

- Mode 03 DTCs: 2 bytes each, same letter/digit packing as the UDS SAE bytes; no status
  byte. CONFIRMED (src: https://en.wikipedia.org/wiki/OBD-II_PIDs).
- Mode 01 PID formulas — **every formula below re-verified verbatim against the Wikipedia
  table this session** (A,B,C,D are the data bytes; `100/255·A` is written as `A/2.55`):
  - `04` Calculated engine load % = `(100/255)·A` (= A/2.55)
  - `05` Engine coolant temp °C = `A − 40`
  - `0A` Fuel pressure (gauge) kPa = `3·A`
  - `0B` Intake manifold abs pressure kPa = `A`
  - `0C` Engine speed rpm = `(256·A + B)/4`
  - `0D` Vehicle speed km/h = `A`
  - `0F` Intake air temp °C = `A − 40`
  - `10` MAF g/s = `(256·A + B)/100`
  - `11` Throttle position % = `(100/255)·A`
  - `1F` Run time since start s = `256·A + B`
  - `2F` Fuel tank level % = `(100/255)·A`
  - `42` Control module voltage V = `(256·A + B)/1000`
  - `5E` Engine fuel rate L/h = `(256·A + B)/20`
- Mode 09: PID 02 VIN (17 ASCII), PID 04 Calibration ID, PID 06 CVN (4 bytes each),
  PID 0A ECU name. (src: same Wikipedia page; widely corroborated — the VIN/CALID/CVN rows
  are on the page.)
- OBD mirror DIDs: UDS **0xF400-0xF5FF** map to the J1979 PIDs (DID 0xF4xx ↔ PID 0xxx), e.g.
  0xF40D = vehicle speed (PID 0x0D), 0xF442 = control module voltage (PID 0x42). CONFIRMED:
  the 0xF400-0xF5FF "OBDDataIdentifier" range is present in did.html, and VW_Flash
  `data_records` lists 0xF40D and 0xF442 with exactly those meanings.

#### Reported / unverified (confidence)

- **Coding write `2E 06 00 <bytes>` → `6E 06 00`** — medium. VW_Flash only *reads* 0x0600;
  the write direction is the symmetric WriteDataByIdentifier, gated behind SecurityAccess, and
  is how ODIS/VCDS write long coding. Confirm with a VCDS "recode" CAN trace on a live module.
- **Adaptation on UDS modules** — medium. VCDS exposes "Adaptation" on UDS/ODX modules as a
  drop-down of channels named by ODX identifiers (`IDExxxxx`); each channel is a DID read with
  `22` and written with `2E` after login; "Basic Setting" runs a RoutineControl (`31`); a
  Save/reset channel restores factory adaptations. (src:
  https://www.ross-tech.com/vcds/tour/adaptation_screen.php, re-fetched.) The exact DID
  numbers per channel live in the ODX, not a fixed range. Confirm by dumping a module's ODX or
  tracing VCDS.
- **VAG 0x19 0x06 extended-data record contents** — medium. Reported: record(s) carry
  priority, frequency, aging/unlearning counter, odometer (mileage, 3-4 bytes) and a
  date/time stamp; VCDS surfaces Priority/Frequency/Reset-counter/Mileage/Date-time from
  these (the Priority/Frequency/Reset-counter *fields* are VERIFIED from dtc_screen.php in
  §H, but their exact byte offsets/widths inside the 0x06 records are not). Confirm per module
  with `19 06 <dtc> FF`.
- **Measuring values / "IDE" numbers** — medium. VCDS "Measuring Blocks" on UDS modules read
  named values via `22 <DID>`; the DID↔IDE mapping lives in ODX/label files, not a fixed
  range (manufacturer range ~0x0100-0xA5FF). The OBD-mirror subset 0xF4xx is standardized
  (§R). Confirm per module from label files.

R-I2. Mk6 UDS cluster service-interval **DIDs**: VCDS names only; the DID numbers behind `ESI: Resetting ESI` etc. are in the ODX/`.rod` file `EV_Kombi_UDS_VDD_RM09_VW36.rod`, not open. Low. Q12.


### 7.7 KWP measuring blocks (`21 <group>`): record layout, complete formula table 0x01–0xB5, group conventions

Source sheet: `kwp_vag.md` §3 (every formula row re-checked against the fetched sources; disagreement columns kept) and §3.2; `ecus.md` R-H1.

#### Verified (source)

##### 3. ReadDataByLocalIdentifier 0x21 — "measuring blocks"

- ISO: request `21 <recordLocalIdentifier> [transmissionMode 01 single/02 slow/03 medium/04 fast/05 stop] [maximumNumberOfResponsesToSend]`, positive response `61 <recordLocalIdentifier> <recordValue#1…m>`; record content is manufacturer specific. (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §7.1)
- VAG: `21 <group>` where group = the VCDS measuring-block number 0x00..0xFF; reply `61 <group>` followed by **3-byte fields `(formulaId, A, B)`**: VB `decodeBlockData(data[i*3], data[i*3+1], data[i*3+2])` for i in 0..3; PY `parseBlock`: `buf = block[2:]` then 3-byte fields; B3 `for i=2; i<len-3; i+=3`; TE "Byte3 0x61, Byte4 LID, Byte5-7 data … `_DecodeValue(_temp[3*Index+2], …)`"; SC `read_block` returns `r[2:]` after checking `r[1]==n`; DV emulator builds `61 <block>` + `{formula,A,B}`×4. (src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java ; https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/responses.h)
- **Real PQ35 engine replies carry 8 fields (26 bytes)**, not 4: NEFM-9182 `21 02` → `61 02 | 01 C8 00 | 21 85 85 | 16 FF 00 | 19 00 00 | 25 00 00 | 25 04 1D | 25 02 7A | 25 00 00` and `21 71` → `61 71 | 01 C8 00 | 21 85 85 | 21 FF 13 | 12 7D CA | 25 00 00 | 25 00 00 | 25 00 00 | 25 00 00` (TP 2.0 length 0x1A = 26); the same thread's first post (seishuku, Teensy) shows `21 01` → `61 01 | 01 73 00 | 27 46 00 | 64 50 00 | 05 09 80 | 25 02 7A | 25 00 00 | 25 00 00 | 25 00 00` (length 0x1A, engine off), and Basano's `21 73` → `61 73 | 01 C8 00 | 21 85 85 | 12 FA 1C | 60 64 65 | 36 14 A9 | 36 0D 9B | 36 10 E9 | 36 0E C3` [added]. TE's example for `21 72` is also 26 bytes (`0x1A`) with 8 fields (`08 0A FF`, `08 0A FF`, `71 0A 80`, `71 0A 80`, `68 0F 8F`, `7E 03 39`, `7E 03 39`, `25 00 00`). VDS (sniffed 8P) sends 8 fields for groups 0x02, 0x14 and 0x73 too. PY: "measuring blocks can be *up to* 4 fields long; some are "8" (need a firmware dump to investigate that...)". VB decodes only the first 4. DV: "Normally, via KWP2000, only blocks 1-254 are accessible, and blocks 128-254 are actually requested as 1-127. For example, requesting block 1 will provide the data for blocks 1 and 128 in the same message: 4 measurements for 1 and 4 measurements for 128." (src: http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2 ; https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c ; https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP1281-VWTP2.0_converter_ESP32.ino)
- Variable-length fields exist: formula **0x5F** = ASCII text with a length byte (`5F <len> <len bytes>`; PY `0x5F: … a[1:a[0]+1].decode("ascii"), size 4` flag; DV sends block 0 as `5F <len> "<part number><ident>"`; KL: "For formula 5F (ASCII text with known length) and 76 (HEX bytes with known length), the length is specified in the 2nd byte"), **0x76** = hex bytes with length byte, **0x3F** = ASCII text without length (last field of the group; KL converts it to 5F), **0xA0** = value with variable units (KL), **0x8B/0x8C/0x93** = value mapped through a 17-byte table supplied by the module, **0x8D** = string from a module-supplied list (KL). Any parser must therefore walk fields by formula id, not assume 3 bytes. (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP1281-VWTP2.0_converter_ESP32.ino ; https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/main/src/KLineKWP1281Lib.cpp)
- An unsupported group gets a negative response (DV emulator: `7F 21 11` for a block that "does not exist"; PY treats `7F 21 31` requestOutOfRange as "no such block"); SC returns None unless the reply starts with `61`. (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP1281-VWTP2.0_converter_ESP32.ino ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py)

###### 3.1 Formula table (physical = f(A, B); A = first data byte, B = second)

Columns: VB = vag-blocks, PY = PyVCDS, B3 = bri3d, KL = KLineKWP1281Lib (NW = A, MW = B), BL = blafusel KW1281 table (decimal ids, "Alle Angaben sind noch unbestätigt" except √ rows), SC = scirocco-dash (ids decimal). "✓" = identical to the consensus column. Disagreements are stated explicitly; where only KL (plus BL) documents an id, the row is KL's and is marked so.

| id | consensus formula | unit | VB | PY | B3 | KL | BL/SC/others | notes |
|---|---|---|---|---|---|---|---|---|
| 0x01 | A·B·0.2 | rpm | A·B/5 ✓ | ✓ | ✓ | ✓ | BL ✓, SC ✓, TE ✓ | agreement everywhere |
| 0x02 | A·B·0.002 | % (load) | – | ✓ | A·B/500 ✓ | ✓ | BL ✓, SC ✓ | |
| 0x03 | A·B·0.002 | ° (throttle) | – | – | A·B/500 ✓ | ✓ | BL ✓, SC ✓ | |
| 0x04 | (B−127)·A·0.01, B>127 → °ATDC, B<127 → °BTDC | ° | abs(B−127)·0.01·A + ATDC/BTDC ✓ | (B−127)·0.01·A "BTDC negative" | ✓ | (B−127)·A·(−0.01) (BTDC positive) | BL ✓, SC ✓ | sign convention only |
| 0x05 | (B−100)·A·0.1 | °C | – | – | A·B/10 − 10·A ✓ | ✓ | BL ✓ (√), SC ✓, TE ✓ | |
| 0x06 | A·B·0.001 | V | – | – | ✓ | ✓ | BL ✓ (√), SC ✓, OH ✓ (Haldex supply voltage) [added] | |
| 0x07 | A·B·0.01 | km/h | ✓ | ✓ | ✓ | ✓ | BL ✓ (√), SC ✓ | |
| 0x08 | A·B·0.1 | (none) | **raw (A<<8\|B) "Binary"** | raw hex | A·B/10 | ✓ | BL ✓, SC ✓ | VB/PY disagree (raw 16-bit); KL/B3/BL/SC say 0.1·A·B |
| 0x09 | (B−127)·A·0.02 | ° (steering) | – | – | (B−127)·A/50 ✓ | ✓ | BL ✓ | |
| 0x0A | B==0 → "COLD" else "WARM" | text | – | – | ✓ | MW?1:0 ✓ | BL ✓ | |
| 0x0B | 1 + (B−128)·A·0.0001 | λ factor | – | – | ✓ | ✓ | BL ✓ | |
| 0x0C | A·B·0.001 | Ω | – | – | ✓ | ✓ | BL ✓ | |
| 0x0D | (B−127)·A·0.001 | mm | – | – | ✓ | ✓ | BL ✓ | |
| 0x0E | A·B·0.005 | bar | – | – | A·B/200 ✓ | ✓ | BL ✓; **OH uses 0.01·A·(B−100)** for Haldex oil pressure (its example a=27,b=200 → 27 bar gives the same number under both formulas, so it does not discriminate) [added] | OH vs KL/B3/BL disagree; see OPEN 10 |
| 0x0F | A·B·0.01 | ms | – | – | ✓ | ✓ | BL ✓, SC ✓ | |
| 0x10 | bit field: bits = B & A (A = mask) | bits | raw 16-bit | raw hex | B & A ✓ | MWb & NWb ✓ | BL "Bin. Bits" | VB/PY show all 16 bits; KL/B3 AND the bytes |
| 0x11 | chr(A) chr(B) | 2 ASCII chars | ✓ | ✓ | prints decimal | ✓ | BL ✓ | |
| 0x12 | A·B·0.04 | mbar | A·B/25 ✓ | **A·B·25 (bug)** | A·B/25 ✓ | ✓ | BL ✓, SC ✓ (18 = pressure) | PyVCDS multiplies instead of dividing |
| 0x13 | A·B·0.01 | l | – | – | ✓ | ✓ | BL ✓ (√ Tankinhalt) | |
| 0x14 | (B−128)·A/128 | % (λ integrator) | **A·B/128 − 1** | A·B/128 − 1 | ✓ | ✓ | BL ✓; SC uses A·(B−128)·0.01 (fitted) | VB/PY subtract 1 instead of A; KL/B3/BL agree |
| 0x15 | A·B·0.001 | V | ✓ | ✓ | ✓ | ✓ | BL ✓, SC ✓ (21) | |
| 0x16 | A·B·0.001 | ms | ✓ | ✓ | ✓ | ✓ | BL ✓, SC ✓ (22) | |
| 0x17 | A·B/256 | % (duty) | ✓ | ✓ | **B/256/A (bug)** | ✓ | BL ✓, SC ✓ (23) | |
| 0x18 | A·B·0.001 | A | – | ✓ | ✓ | ✓ | BL ✓, OH ✓ (Haldex clutch valve current, a=10,b=191 → 1.910 A) [added] | |
| 0x19 | (256·B + A)/180 | g/s (MAF) | – | **(100/A)·B** | (B·256+B)/182 (typo) | ✓ | BL B·1.421+A/182 ≈ ✓; SC same as BL and verified at idle | PY diverges; use KL/BL |
| 0x1A | B − A | °C | ✓ | ✓ | ✓ | ✓ | BL ✓, SC ✓ (26), OH ✓ (Haldex oil/plate temperature) [added] | |
| 0x1B | (B−128)·A·0.01 | ° (ignition) | – | – | abs(B−128)·A/100 ± | ✓ | BL ✓; SC (27) ✓ verified against OBD PID 0x0E | |
| 0x1C | B − A | – | – | – | ✓ | ✓ | BL ✓ | |
| 0x1D | B<A → "Map 1" else "Map 2" | text | – | – | – | ✓ | BL ✓ | |
| 0x1E | B/12·A | °KW (knock) | – | – | ✓ | ✓ | BL ✓ | |
| 0x1F | B/2560·A | °C | – | – | ✓ | ✓ | BL ✓ | |
| 0x20 | signed(B) (B>128 → B−256) | – | – | – | ✓ | ✓ | BL ✓ | |
| 0x21 | 100·B/A (A==0 → 100·B) | % | ✓ | ✓ | ✓ | ✓ (no A==0 guard) | BL ✓ (√), SC ✓ (33); **OH uses 0.01·A·B** for Haldex clutch duty (its example a=100,b=40 → 40 % is identical under both formulas, so it does not discriminate) [added] | OH vs everyone else; see OPEN 10 |
| 0x22 | (B−128)·A·0.01 | kW | ✓ | ✓ | ✓ | ✓ | BL ✓, SC ✓ (34) | VDS uses 0x22 fields for group 020 knock retard |
| 0x23 | A·B/100 | l/h | ✓ | ✓ | ✓ | ✓ | BL ✓ (√) | |
| 0x24 | A·2560 + B·10 = (A·256+B)·10 | km | – | ✓ | ✓ | ✓ | BL ✓ (√) | |
| 0x25 | raw 16-bit (A<<8\|B) index into a module/label text table | text | raw "Binary" | raw | – | "Text from table" | BL "???"; VDS/NEFM use `25 00 00` as empty filler; SP: DSG group 001 field 1 is `25 hi lo` with km/h = raw/3 (VCDS capture) | VCDS resolves the text from the label file |
| 0x26 | (B−128)·A·0.001 | °KW | – | – | ✓ | ✓ | BL ✓ | |
| 0x27 | A·B/256 | mg/stroke (fuel) | ✓ | ✓ | – | A·B/255 | BL B/256·A ✓ | KL uses /255 |
| 0x28 | (A·255+B−4000)·0.1 | A | – | – | – | ✓ | BL B·0.1+25.5·A−400 ✓ | KL/BL |
| 0x29 | A·255 + B | Ah | – | – | – | ✓ | BL ✓ | KL/BL |
| 0x2A | (A·255+B−4000)·0.1 | kW | – | – | – | ✓ | BL ✓ | KL/BL |
| 0x2B | (A·255+B)·0.1 | V | – | – | – | ✓ | BL ✓ | KL/BL |
| 0x2C | time "A:B" (h:m) | time | – | – | – | B/100 + A ✓ | BL "a : b h:m" ✓ | KL/BL |
| 0x2D | A·B·0.1 | l/km | – | – | – | ✓ | BL 0.1·A·B/100 | disagree ×100 |
| 0x2E | ((A·256)+B−32768)·0.00275 | °KW | – | – | – | ✓ | BL (A·B−3200)·0.0027 | disagree (BL likely garbled) |
| 0x2F | (B−128)·A | ms | – | – | – | ✓ | BL ✓ | KL/BL |
| 0x30 | A·255 + B | – | – | – | – | ✓ | BL ✓ | KL/BL |
| 0x31 | A·B·0.025 | mg/stroke (air) | A·B/40 ✓ | ✓ | – | ✓ | BL (B/4)·A·0.1 ✓ | |
| 0x32 | (B−128)·100/A (A==0 → /0.01) | mbar | – | – | – | ✓ | BL ✓ | KL/BL |
| 0x33 | (B−128)·A/255 | mg/stroke Δ | ✓ | ✓ | – | ✓ | BL ✓ | |
| 0x34 | (B−50)·A·0.02 | Nm | – | – | – | ✓ | BL B·0.02·A − A ✓ | KL/BL |
| 0x35 | ((B−128)·256 + A)/180 | g/s | – | – | – | ✓ | BL (B−128)·1.4222+0.006·A ✓ | KL/BL |
| 0x36 | A·256 + B | count | ✓ | ✓ | ✓ | ✓ | BL ✓, SC ✓ (54; verified as odometer/10 in block 075) | |
| 0x37 | A·B/200 | s | ✓ | ✓ | ✓ | ✓ | BL ✓ | |
| 0x38 | A·256 + B | WSC (bit16 = 0) | – | – | – | (A<<8)&B (bug for \|) | BL ✓ | |
| 0x39 | A·256 + B + 65536 | WSC (bit16 = 1) | – | – | – | ✓ | BL ✓ | |
| 0x3A | signed(B)·1.023 | misfires /s | – | – | – | ✓ | BL 1.0225·B / 1.0225·(256−B) | |
| 0x3B | (A·256+B)/32768 | – | – | – | – | ✓ | BL ✓ | |
| 0x3C | (A·256+B)/100 | s | – | – | – | ✓ | BL ✓ | |
| 0x3D | (B−128)/A (A==0 → B−128) | – | – | – | – | ✓ | BL ✓ | |
| 0x3E | A·B·0.256 | s | – | – | – | ✓ | BL ✓ | |
| 0x3F | ASCII text, no length byte (rest of message) | text | – | – | – | converted to 5F | BL chr(A)chr(B)"?" | |
| 0x40 | A + B | Ω | – | – | – | ✓ | BL ✓ (√) | |
| 0x41 | (B−127)·A·0.01 | mm | – | – | – | ✓ | BL ✓ | |
| 0x42 | A·B/512 | V | – | – | – | ✓ | BL A·B/511.12 ≈ | |
| 0x43 | signed16(A,B)·2.5 | ° (steering) | – | – | – | ✓ | BL 640·A + 2.5·B ✓ (unsigned) | |
| 0x44 | signed16·0.1358 | °/s | – | – | – | ✓ | BL (256A+B)/7.365 ✓ | |
| 0x45 | signed16·0.3255 | bar | – | – | – | ✓ | BL (256A+B)·0.3254 ✓ | |
| 0x46 | signed16·0.192 | m/s² | – | – | – | ✓ | BL ✓ | |
| 0x47 | A·B | cm | – | – | – | ✓ | – | KL only |
| 0x48 | (A·255 + B·(211−A))/4080 | V | – | – | – | ✓ | – | KL only |
| 0x49 | A·B·0.01 | Ω | – | – | – | ✓ | – | KL only |
| 0x4A | A·B·0.1 | months | – | – | – | ✓ | – | KL only |
| 0x4B | A·256 + B | fault code | – | – | – | ✓ | – | KL only |
| 0x4C | A·255 + B | kΩ | – | – | – | ✓ | – | KL only |
| 0x4D | (255·A + B·60)/4080 | V | – | – | – | ✓ | – | KL only |
| 0x4E | signed(B)·1.819 | misfires /s | – | – | – | ✓ | – | KL only |
| 0x4F | B | channel number | – | – | – | ✓ | – | KL only |
| 0x50 | (A·256+B)/100 | kΩ | – | – | – | ✓ | – | KL only |
| 0x51 | signed16(A,B)·0.04375 | ° (steering angle) | (A·112000 + B·436)/1000 "torsion, check formula" | (A·11200 + B·436)/1000 | – | ✓ | – | VB and PY differ from each other (×10 on A) and from KL on B; KL's 0.04375°/LSB |
| 0x52 | signed16·0.00981 | m/s² | – | – | – | ✓ | – | KL only |
| 0x53 | signed16·0.01 | bar | – | – | – | ✓ | SC (83): raw16·0.01 bar absolute, fitted against OBD PID 0x23 on the car ✓ | |
| 0x54 | signed16·0.0973 | m/s² | – | – | – | ✓ | – | KL only |
| 0x55 | signed16·0.002865 | °/s | – | – | – | ✓ | – | KL only |
| 0x56 | A·B·0.1 | A | – | – | – | ✓ | – | KL only |
| 0x57 | (B−128)·A·0.1 | °/s | – | – | – | ✓ | – | KL only |
| 0x58 | A·B·0.01 | kΩ | – | – | – | ✓ | – | KL only |
| 0x59 | A·256 + B | h (on-time) | – | – | – | ✓ | – | KL only |
| 0x5A | A·B·0.1 | kg | – | – | – | ✓ | – | KL only |
| 0x5B | (B−128)·A·0.1 | ° (steering) | – | – | – | ✓ | – | KL only |
| 0x5C | A·B | km | – | – | – | ✓ | – | KL only |
| 0x5D | (B−128)·A·0.001 | Nm | – | – | – | ✓ | – | KL only |
| 0x5E | (B−128)·A·0.1 | Nm | A·(B/50 − 1) "check formula" | same as VB | – | ✓ | SC (94) copies VB; **OH `0.1f * a * ((int)b - 128)` for Haldex "est. torque", "Confirmed against VCDS-displayed values"** (a=160,b=255 → 2032 Nm; VB's formula would give 656) [added] | KL + OH agree; VB/PY/SC carry VB's self-flagged guess |
| 0x5F | `5F <len> <ASCII…>` | text | – | ✓ (size flag 4) | – | ✓ | DV uses it for block 0 | length-prefixed |
| 0x60 | A·B·0.1 | mbar | – | – | – | ✓ | TE ✓ (mbar), VDS uses 0x60 in group 115 field 4 | |
| 0x61 | (B−A)·5 | °C (cat) | – | – | – | ✓ | – | KL only |
| 0x62 | A·B·0.1 | impulses/km | – | – | – | ✓ | – | KL only |
| 0x63 | signed16 | – | – | – | – | ✓ | – | KL only |
| 0x64 | A·B·0.1 | bar | – | – | – | ✓ | – | KL only |
| 0x65 | A·B·0.001 | l/mm | – | – | – | ✓ | – | KL only |
| 0x66 | A·B·0.1 | mm (fuel level) | – | – | – | ✓ | – | KL only |
| 0x67 | A + B·0.05 | V | – | – | – | ✓ | – | KL only |
| 0x68 | (B−128)·A·0.2 | ml | – | – | – | ✓ | – | KL only |
| 0x69 | (B−128)·A·0.01 | m | – | – | – | ✓ | – | KL only |
| 0x6A | (B−128)·A·0.1 | km/h | – | – | – | ✓ | – | KL only |
| 0x6B | hex(A) hex(B) | hex text | – | – | – | ✓ | – | KL only |
| 0x6C / 0x6D / 0x6E | "Environment" / N/A / "Workshop" (text, undecoded) | text | – | – | – | listed, unknown | – | KL only |
| 0x6F | 0x6F0000 \| (A<<8) \| B | km | – | – | – | ✓ | – | KL only (odd) |
| 0x70 | (B−128)·A·0.001 | ° | – | – | – | ✓ | – | KL only |
| 0x71 | (B−128)·A·0.01 | – | – | – | – | ✓ | TE/NEFM-like replies use 0x71 fields | KL only |
| 0x72 | (B−128)·A | m (altitude) | – | – | – | ✓ | – | KL only |
| 0x73 | signed16 | W | – | – | – | ✓ | – | KL only |
| 0x74 | signed16 | rpm | – | – | – | ✓ | – | KL only |
| 0x75 | (B−64)·A·0.01 | °C | – | – | – | ✓ | – | KL only |
| 0x76 | `76 <len> <bytes>` | hex bytes | – | – | – | ✓ | – | length-prefixed |
| 0x77 | A·B·0.01 | % | – | – | – | ✓ | – | KL only |
| 0x78 | A·B·1.41 | ° | – | – | – | ✓ | – | KL only |
| 0x79 | ((B·256)+A)·0.5 | – | – | – | – | ✓ | – | KL only |
| 0x7A | ((B·256)+A−32768)·0.01 | – | – | – | – | ✓ | – | KL only |
| 0x7B | raw 16-bit text-table index | text | – | – | – | ✓ | – | like 0x25 |
| 0x7C | A·B·0.1 | mA | – | – | – | ✓ | – | KL only |
| 0x7D | A − B | dB | – | – | – | ✓ | – | KL only |
| 0x7E | A·B·0.1 | – | – | – | – | ✓ | TE "grams" | |
| 0x7F | date: 200000 + (B&0x7F)·100 + (((A&7)<<1)\|(B>>7)) + ((A&0xF8)>>3)·0.01 → yyyy.mm.dd | date | – | – | – | ✓ | – | KL only |
| 0x80 | A·B | rpm | – | – | – | ✓ | – | KL only |
| 0x81 | A·B/256 | % | – | – | – | ✓ | – | KL only |
| 0x82 | A·B/2560 | A | – | – | – | ✓ | – | KL only |
| 0x83 | A·B·0.5 − 30 | ° | – | – | – | ✓ | – | KL only |
| 0x84 | A·B·0.5 | ° | – | – | – | ✓ | – | KL only |
| 0x85 | A·B/256 | V | – | – | – | ✓ | – | KL only |
| 0x86 | A·B | km/h | – | – | – | ✓ | – | KL only |
| 0x87 | A·B | – | – | – | – | ✓ | – | KL only |
| 0x88 | bits = B & A | bits | – | – | – | ✓ | – | KL only |
| 0x89 | A·B·0.01 | ms | – | – | – | ✓ | – | KL only |
| 0x8A | A·B·0.001 | V (knock) | – | – | – | ✓ | – | KL only |
| 0x8B / 0x8C / 0x93 | value mapped through a 17-byte table sent by the module | rpm / °C / % | – | – | – | listed | – | KL only |
| 0x8D | string from a module-supplied list | text | – | – | – | listed | – | KL only |
| 0x8E | chr(A) chr(B) | text | – | – | – | ✓ | – | KL only |
| 0x8F | (B−128)·A·0.01 | ° | – | – | – | ✓ | – | KL only |
| 0x90 / 0x91 | A·B·0.01 | l/h / – | – | – | – | ✓ | – | KL only |
| 0x92 | 1 + (B−128)·A·0.0001 | λ | – | – | – | ✓ | – | KL only |
| 0x94 | (B−128)·A·0.25 | slip rpm | – | – | – | ✓ | – | KL only |
| 0x95 | (B−100)·A·0.1 | °C | – | – | – | ✓ | – | KL only |
| 0x96 | (256·B + A)/180 | g/s | – | – | – | ✓ | – | KL only |
| 0x97 | (B−128)·A·0.01 | kW | – | – | – | ✓ | – | KL only |
| 0x98 | A·B·0.025 | mg/stroke | – | – | – | ✓ | – | KL only |
| 0x99 | (B−128)·A/255 | mg/stroke | – | – | – | ✓ | – | KL only |
| 0x9A | A·B | ° | – | – | – | ✓ | – | KL only |
| 0x9B | A·B·0.01 − 90 | ° | – | – | – | ✓ | – | KL only |
| 0x9C / 0x9D | (A·256+B) / signed16 | cm | – | – | – | ✓ | – | KL only |
| 0x9E | (A·256+B)·0.01 | km/h | – | – | – | ✓ | – | KL only |
| 0x9F | ((B−127)·256 + A)·0.1 | °C | – | – | – | ✓ | – | KL only |
| 0xA0 | value with variable units: **5 data bytes** `A0 NW B C D E` (see bullet below) | var | – | – | – | decoded (5-byte layout) | DV: "not handled properly by diagnostic software when received via VWTP" | [corrected] layout now documented |
| 0xA1 | bin(A) bin(B) | bits | – | – | – | ✓ | – | KL only |
| 0xA2 | A·B·0.448 | ° | – | – | – | ✓ | – | KL only |
| 0xA3 | B/100 + A | hh:mm | – | – | – | ✓ | – | KL only |
| 0xA4 | B≤100 → B; 100<B≤200 → B−100; else B | % | – | – | – | ✓ | – | KL only |
| 0xA5 | (B·256)+A−32768 | mA | – | – | – | ✓ | – | KL only |
| 0xA6 | signed16·2.5 | °/s | – | – | – | ✓ | – | KL only |
| 0xA7 | A·B·0.001 | mΩ | – | – | – | ✓ | – | KL only |
| 0xA8 | (256·A+B)·0.01 | % | – | – | – | ✓ | – | KL only |
| 0xA9 | A·B + 200 | mV (Nernst) | – | – | – | ✓ | – | KL only |
| 0xAA / 0xAB | A·B/2560 | g (NH3 / NOx) | – | – | – | ✓ | – | KL only |
| 0xAC | A·B | mg/km NOx | – | – | – | ✓ | – | KL only |
| 0xAD | A·B·0.1 | mg/s NOx | – | – | – | ✓ | – | KL only |
| 0xAE | A·B·0.01 | km (avg DEF) | – | – | – | ✓ | – | KL only |
| 0xAF | A·B·0.005 | bar (DEF) | – | – | – | ✓ | – | KL only |
| 0xB0 | A·B·0.1 | ppm NOx | – | – | – | ✓ | – | KL only |
| 0xB1 | (A−128)·256 + B | Nm | – | – | – | ✓ | – | KL only |
| 0xB2 | ((A−128)·256 + B)·6/51 | °/s | – | – | – | ✓ | – | KL only |
| 0xB3 | (A·256+B)·10 | – | – | – | – | ✓ | – | KL only |
| 0xB4 | A·B/256 | kg/h | – | – | – | ✓ | – | KL only |
| 0xB5 | A·B·0.001 | mg/s | – | – | – | ✓ | – | KL only; "There are no valid formulas after B5" (KL) |

(src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/MeasurementValue.java ; https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/main/src/KLineKWP1281Lib.cpp ; https://www.blafusel.de/obd/obd2_kw1281.html ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c ; https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://raw.githubusercontent.com/adamforbes92/speedPulserPro/main/PlatformIO/src/SpeedPulserPro_uds.cpp)

- The same formula ids are used by KWP1281 and KWP2000 modules — DV copies KWP1281 measurement bytes verbatim into KWP2000 `61` replies and VCDS displays them ("Because the measurement response is copied directly from KWP1281 to VWTP, issues may arise for some formulas that were phased out by KWP2000"). [corrected] KL's `getMeasurementType()` has **three** classes, not two: `UNKNOWN` (not decodable as a 2-byte value) = 0x00, 0x3F, 0x6C, 0x6D, 0x6E, 0x5F, 0x76, 0xA0; `TEXT` = 0x0A, 0x10, 0x88, 0x11, 0x8E, 0x1D, 0x25, 0x7B, 0x2C, 0x6B, 0x7F, 0xA1, **0x8D**; everything else `VALUE` (numeric). (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP1281-VWTP2.0_converter_ESP32.ino ; https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/main/src/KLineKWP1281Lib.cpp)
- [added] **Formula 0xA0 byte layout** (KL `getMeasurementValue`/`getMeasurementUnits`, "measurement with variable units"; the field is `A0` + **5** data bytes `NW B C D E`, `measurement_data_length` must be 5): `WORD_BC = (B << 8) | C`; if `D & 0x80` and the unit code is not 0x23, `WORD_BC = -WORD_BC`; `BYTE_DL = D & 0x0F`, `BYTE_DH = (D >> 4) & 7`; **value = NW · WORD_BC · BYTE_DL · 10^(−BYTE_DH)**. Units: `E >> 6` selects a prefix (0 none, 1 "k", 2 "m", 3 "u") and `E & 0x3F` the base unit (0x01 V, 0x02 V/s, 0x03 A, 0x04 capacity, 0x05 Ω, 0x06 W, 0x07 W/m², 0x08 W/cm², 0x09 Wh, 0x0A Ws, 0x0B distance, 0x0C m/s, 0x0D acceleration, 0x0E distance (cm), 0x0F speed, 0x10 volume, 0x11 l/100 km, 0x12 fuel-level factor, 0x13 l/h, 0x14 l/km, 0x15 time, 0x16 h, 0x17 months, 0x18 mass, 0x19 mass flow, 0x1A mg/stroke, 0x1B torque, 0x1C N, 0x1D pressure, 0x1E angle, 0x1F angle °, 0x20 temperature, 0x21 °F, 0x22 turn rate, **0x23 ignition angle: sign bit of D means BTDC (set) / ATDC (clear) instead of a negative value**, 0x24 rpm, 0x25 %, 0x26/0x27 correction, 0x28 misfires, 0x29 impulses, 0x2A dB attenuation). DV warns this formula is "not handled properly by diagnostic software when received via VWTP", so a KWP2000 module is unlikely to send it, but a parser must still skip 6 bytes for it. (src: https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/main/src/KLineKWP1281Lib.cpp ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP1281-VWTP2.0_converter_ESP32.ino)
- [added] Table-mapped formulas in KL: for 0x8B/0x8C/0x93 the module supplies a **17-byte** table with the group header (`data_table_length != 17` → nan); `idx = MW / 16`, clamped to 15; `result = table[idx] + (table[idx+1] − table[idx]) · (MW % 16) / 16`; 0x8B returns `result · NW`, 0x8C/0x93 return `result − NW`. For 0x8D the table is a list of `0x03`-separated ASCII strings and MW selects the string. These tables only exist in KWP1281 group headers; over KWP2000 the `61` reply has no header, so 0x8B–0x8D/0x93 cannot be decoded from a `21` reply alone. (src: https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/main/src/KLineKWP1281Lib.cpp)
- Label files: VCDS/VAG-COM plain-text `.lbl` lines are `group,field,desc[,subdesc[,longdesc]]` with field 0 = group name (VB `loadLabelFile`: `blockNum = parts[0]; pos = parts[1] (0..4)`; a `;` line containing `=` after a field is the bit description). Files are found by part number `XXX-XXX-XXX[-SS].lbl` or via `REDIRECT` lines in `XX-aa.lbl` (aa = module address). (src: https://raw.githubusercontent.com/jazdw/vag-blocks/master/kwp2000.cpp ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/label.py)

###### 3.2 Conventional group numbers

- Ross-Tech's "Standardized Measuring Block Groups for Gasoline Engines" (for engines "starting about 1999-2000"): **000** = 10 raw fields (RPM, load, coolant temp, voltage, throttle pot, idle valve, idle learning, λ control, λ learning values); **001** RPM / coolant temp / λ control value bank 1 (or injection adjustment) / λ control value bank 2 or basic-setting condition bit field (bit0 coolant >80 °C, bit1 RPM <2000, bit2 throttle closed, bit3 λ control OK, bit4 idle switch, bit5 A/C compressor OFF, bit6 cat temp reached, bit7 no DTC); **002** RPM / load / mean injection time / air mass (MAF systems) or intake manifold pressure; **003** RPM / air mass or MAP / throttle angle / ignition angle; **004** RPM / voltage / coolant temperature / intake air temperature; **005** RPM / load / speed / operating condition text (idle, partial load, full load, SA, BA); **006** RPM / load / IAT / altitude correction [%]; **010** RPM / load / throttle / ignition angle; **011** RPM / coolant / IAT / ignition angle; **014** RPM / load / misfire counter / misfire recognition text; **015/016/017/019** misfire counters cyl 1-3 / 4-6 / 7-9 / 10-12 + recognition; **018** misfire load/RPM window; **020** ignition retard cyl 1-4 [°KW]; **021** retard cyl 5-8; **022–025** RPM / load / retard pairs; **026/027** knock sensor voltages cyl 1-4 / 5-8; **028** knock sensor test; **030** O2 sensor status bits (control active / sensor ready / heater ON) per sensor; **031** O2 voltages or λ actual/specified (linear sensors); **032** λ learning values: bank 1 idle / bank 1 partial load / bank 2 idle / bank 2 partial load [%]; **033** λ control value + sensor voltage per bank; **050–057** idle speed control (actual/specified RPM, A/C, …); **060** throttle body adaptation (ESB/E-Gas); **061–066** E-Gas / cruise control; **070–078** EVAP, EGR, secondary air tests; **080** manufacturer code / date / change status / test stand / running number; **081** VIN / serial / type test number; **082** flash tool code / flash date / HW-SW group types; **090–096** camshaft adjustment; **099** compatibility λ regulation; **100** readiness bits; **101–107** fuel injection; **110** load; **111** boost adaptation; **112** EGT; **113** RPM / load / throttle / air pressure; **114** boost specified/actual load + duty; **115** "Boost pressure control" (the Ross-Tech page gives only the title; the field layout RPM / load / **boost pressure specified** / **boost pressure actual** [mbar] is from the real `21 73` replies: NEFM-9182 `01 C8 00 | 21 85 85 | 12 FA 1C | 60 64 65` and VDS `01 | 21 | 12 | 60` [corrected attribution]); **116** boost correction factors; **117** RPM / pedal / throttle / boost spec; **118** RPM / IAT / N75 duty / pressure before throttle; **119** boost adaptation + duty; **120** ASR/FDR torque; **122** transmission torque interface; **125** CAN bus participants (Transmission / ABS / cluster / A/C) ; **126/127** more CAN participants (ADR, LWS, airbag, electrical, all-wheel, level, steering wheel); **130–137** engine cooling. (src: https://www.ross-tech.com/vag-com/m_blocks/001-009.html , .../010-019.html , .../020-029.html , .../030-049.html , .../050-059.html , .../060-069.html , .../070-079.html , .../080-085.html , .../090-098.html , .../099-100.html , .../101-109.html , .../110-119.html , .../120-129.html , .../130-137.html , .../000.html)
- Real-car cross-checks of that convention: NEFM-9182 engine group 002 = `01 rpm | 21 load% | 16 inj ms | 19 MAF g/s` ✓; VDS group 0x02 = `01, 21, 16, 19` ✓, group 0x14 (020) = four `0x22` ±kW/° fields (knock retard) ✓, group 0x73 (115) = `01 rpm | 21 load | 12 mbar (spec) | 60 mbar (actual)` ✓; SC: block 032 "is the documented lambda/fuel-trim group" (formula 0x14), block 003 field 4 = ignition advance (0x1B), block 075 field 8 = odometer/10 (0x36), block 106 fields 1-2 = fuel rail pressure (0x53); PY `blocks.json` names groups 0x50/0x51/0x52 (80/81/82) "Manufacture Mark / Serial Numbers / Revision Info" and VB reads block 81 as the ID block. (src: http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2 ; https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/blocks.json)
- VCDS mechanics: groups 000-255, 4 fields each except "Group 000 and any other group that displays 10 fields instead of 4"; "Most 1996 and newer ECUs have Groups through the 200 range, but there are often 'gaps' in the numbers"; sampling halves per extra group displayed ("3 groups simultaneously runs at around 1/3"); for UDS modules the function does not exist. (src: https://www.ross-tech.com/vcds/tour/m-blocks.php)
- **02E DSG**: group 019 = three temperatures: "Control Module Temp (G510), Clutch Oil Temp (G509), Transmission Fluid (G93)" (Ross-Tech staff); the DSG wiki page uses group 019 as the fluid-temperature precondition and lists basic-setting groups 060 (synch point), 061 (engaged calibration), 062 (clutch adaptation, sw < 0800), 063, 065, 067 (clutch adaptation, sw ≥ 0800), 068, 069. SP (VCDS capture, Mk5 DSG, TP 2.0 dest 0x02, tester TX 0x760): group 001 field 1 = `25 hi lo`, vehicle speed = raw/3 km/h. (src: https://forums.tdiclub.com/index.php?threads/measuring-block-for-dsg-temp.318269/ ; https://wiki.ross-tech.com/wiki/index.php/6-Speed_Direct_Shift_Gearbox_(DSG/02E) ; https://raw.githubusercontent.com/adamforbes92/speedPulserPro/main/PlatformIO/src/SpeedPulserPro_uds.cpp)
- **Haldex over TP 2.0 (OH)** [corrected — the full file does name groups]: OH opens TP 2.0 to logical 0x0A (`KWP_TP20_HALDEX_ADDR`, channel-setup byte 7 = `0x01 /* application = KWP2000 */`), sends `{0x10, 0x89}`, then polls `{0x21, group}` and accepts `buf[0] == 0x61 && buf[1] == group`, treating `7F` as "NRC xx". Group lists "confirmed from VCDS captures": **Gen2 (1K0 — the R32's generation): groups 0x01, 0x02, 0x7D** (OH only dumps these raw; no field decode); **Gen4 (0AY): group 0x01 = oil temp, plate temp, supply voltage (fields 0-2); group 0x03 = oil pressure, est. torque, clutch duty, clutch valve current (fields 0-3)**, each field `[formula][a][b]` at `buf[2 + 3k]`, scaled with `vagScale()` (0x06 V, 0x0E bar, 0x18 A, 0x1A °C, 0x21 %, 0x5E Nm — see the formula table; unknown formulas fall back to raw `b`). (src: https://raw.githubusercontent.com/Forbes-Automotive/OpenHaldex-C6/main/src/OpenHaldexC6_UDS.cpp)

#### Reported / unverified (confidence)

- **8 fields per `21` reply = groups N and N+128**: DV's statement ("requesting block 1 will provide the data for blocks 1 and 128 in the same message") explains the 26-byte replies seen on PQ35 engines; the per-block "upper half" would then be the label-file group N+128. Confidence **medium**. Confirm: request `21 02` and `21 82` on the R32 engine — if 0x82 is refused (`7F 21 31`) or returns the same 4 fields that appear at offsets 12..23 of the `61 02` reply, the rule holds.
- **KWPBridge** (dspl1236) README claims a different 24-formula table (e.g. "0x08: (A×256+B)×0.25 RPM", "0x12: (A×256+B)×0.1−273.15 °C") — that is the Hitachi/early-Motronic KWP1281 dialect of 1989-91 Audis, not the VAG standard table above. Confidence **high** that it does not apply to PQ35 modules.

R-H1. **KWP measuring-block read over TP 2.0**: verified skeleton from SEISHUKU (fetched): request payload `21 <group>` (`0x21 readDataByLocalIdentifier`, "LocalID = Local Identifier parameter (RLOCID)"), positive reply `61 <group>` followed by the field data, which the code decodes as triples `(formula id f, a, b)` with `_DecodeValue(f,a,b)`: `0x01` RPM `a*b*0.2`; `0x05` °C `a*(b-100)*0.1`; `0x60` mbar and `0x7E` grams `a*b*0.1`; default raw `a*256+b`. The worked frame example in that source's comment is internally inconsistent (overlapping bytes), so it is not reproduced. The full formula-id table (1..70 and the 0x60+/0x7E+ ids used over TP 2.0) is the KWP sheet's domain (nefarious topic 22, sibling-cached). Medium-high that the same `21/61` scheme applies to all four KWP modules on these cars (engine CJAA, ME7.1.1, DQ250, Haldex).


### 7.8 DTC formats and numbering (UDS 3-byte, KWP 2-byte + status, SAE letters, VAG 5-digit and 6-digit numbers, VCDS rendering)

Source sheets: `uds_vag.md` §E–§H, `kwp_vag.md` §4, `dtc_db.md` §B/§C. The 5-digit rule is confirmed three independent ways; the 6-digit number is the decimal value of the 2 SAE bytes.

#### Verified (source)

##### E. 3-byte DTC format and the SAE letter/digit decode

- A VAG UDS DTC is **2 SAE bytes + 1 FTB byte**. The letter/digit packing of the 2 SAE
  bytes is the standard SAE J2012 / OBD-II scheme (src:
  https://en.wikipedia.org/wiki/OBD-II_PIDs, which documents the same 2-byte DTC encoding
  for mode 03; also existing `vagtune/vag/dtc.py`):
  Byte0 top 2 bits select the letter `00=P, 01=C, 10=B, 11=U`; byte0 bits5-4 = first digit
  (0-3); byte0 bits3-0 = second digit (hex); byte1 hi nibble = third digit; byte1 lo nibble
  = fourth digit. Byte2 = **FTB** (failure type byte), NOT part of the 5-char code.
  Example: `P0299` packs to SAE bytes `02 99`; byte0=0x02 → top2=00=P, b5-4=0→"0",
  b3-0=2→"2"; byte1=0x99 → "99". With FTB 0x00 the 3-byte DTC is `02 99 00`. ✓
  (Fuzzy part, now resolved: the *bit layout* is convention/ISO, not spelled out on the
  Wikipedia page re-fetched; the page confirms the 2-byte letter+4-digit encoding and the
  P/C/B/U letter mapping, which is what matters.)
- Implementation:
```python
LET = "PCBU"
def sae_code(b0, b1):
    return f"{LET[b0>>6]}{(b0>>4)&3}{b0&0xF:X}{(b1>>4)&0xF:X}{b1&0xF:X}"
```

##### F. VAG legacy 5-digit fault number rule — CONFIRMED

`N = 16384 + (first_P_digit * 1024) + decimal_value_of_last_three_digits`, where the "last
three digits" are read as a **decimal** integer. Equivalently
`N = 0x4000 + int(Pxyzw[1])*0x400 + int(Pxyzw[2:5], 10)`.

Re-verified this session against the **exact page titles** of the four Ross-Tech Wiki pages
(the title string is `<5digit>/<Pcode>/<6digit>`):

| P-code | 5-digit (from RT title) | computed | match |
|--------|-------------------------|----------|-------|
| P0101 | 16485 | 16485 | ✓ |
| P0299 | 16683 | 16683 | ✓ |
| P1556 | 17964 | 17964 | ✓ |
| P1602 | 18010 | 18010 | ✓ |
| P1557 | 17965 | 17965 | ✓ (rule) |
| P0506 | 16890 | 16890 | ✓ (extra) |
| P0000 | 16384 | 16384 | ✓ (base) |

(src, titles re-read this session: `16485/P0101/000257`, `16683/P0299/000665`,
`17964/P1556/005462`, `18010/P1602/005634` at
http://wiki.ross-tech.com/wiki/index.php/16485/P0101/000257 etc.)

```python
def vag5_from_pcode(p):            # p like "P0299"; valid for letter 'P' only
    return 0x4000 + int(p[1])*0x400 + int(p[2:5], 10)
def pcode_from_vag5(n):
    n -= 0x4000; return f"P{n//0x400}{n%0x400:03d}"
```
Only clean for P0/P1/P2/P3 (first digit 0-3, fits 2 bits). This is the **legacy KWP-era**
numbering; UDS modules also carry the 6-digit code below.

##### G. VAG UDS 6-digit fault number — CONFIRMED relation

The 6-digit number in each Ross-Tech title is the **decimal value of the 2-byte SAE code**
(the first two bytes of the 3-byte UDS DTC), zero-padded to 6 digits:
- P0101 → SAE `01 01` → 0x0101 = 257 → `000257` ✓
- P0299 → `02 99` → 0x0299 = 665 → `000665` ✓
- P1556 → `15 56` → 0x1556 = 5462 → `005462` ✓
- P1602 → `16 02` → 0x1602 = 5634 → `005634` ✓
(src: the four RT page titles re-read this session, matched exactly.)
Implementation: `six = int.from_bytes(sae_two_bytes, "big")`; display `f"{six:06d}"`.
The FTB (3rd byte) is shown separately by VCDS.

##### H. VCDS UDS display format, priority/frequency, and the [status] bracket

- VCDS shows the fault over two lines. **Re-verified quote** (src:
  https://www.ross-tech.com/vcds/tour/dtc_screen.php, re-read this session): the first line
  is the fault described "by elaborators describing the condition of the fault. **The second
  line contains the P-code, or generic OBD-II code (if it exists -- there are thousands of
  VAG codes without generic OBD-II equivalents)**". (The earlier sheet's paraphrase "plus
  additional fault information" was not on the page; corrected to the exact wording.)
- The `[nnn]` bracket in a VCDS UDS line (e.g. "P0299 00 [096]") is the **decimal value of
  the DTC status byte**; `00` is the FTB byte. This decode is arithmetic, not a page quote:
  `[096]` = 0x60 = testFailedSinceLastClear(0x20) + testNotCompletedThisOperationCycle(0x40)
  → "not currently failing but failed since last clear" (intermittent); `[032]` = 0x20
  (failed since last clear only); `[008]` = 0x08 (confirmed); `[009]` = 0x09 (confirmed +
  testFailed = active). (Status bit meanings from §D; the bracket-is-status-byte convention
  is widely used but is NOT literally stated on dtc_screen.php — flag as convention.)
- **Priority table CONFIRMED verbatim** (src: dtc_screen.php, re-read this session):
  `0 Undefined by manufacturer; 1 strong influence on drivability, immediate stop required;
  2 requires an immediate service appointment; 3 correct at next service; 4 recommends an
  action, otherwise drivability might be affected; 5 no influence on drivability; 6 long-term
  influence on drivability; 7 influences comfort functions, not drivability; 8 General Note`.
- **Frequency** = "how many times the conditions that caused the fault have recurred, during
  all driving cycles"; **Reset counter** = "a number pre-assigned to each fault, with the
  number of problem-free driving cycles before [it self-clears]". CONFIRMED verbatim
  (dtc_screen.php). These come from the 0x04 snapshot and 0x06 extended-data records.

##### 4. Fault codes: ReadDiagnosticTroubleCodesByStatus 0x18, ClearDiagnosticInformation 0x14, freeze frame

- ISO 8.2: request `18 <statusOfDTC#1…> <groupOfDTC#1…>`, reply `58 <numberOfDTC> [DTC(n bytes) statusOfDTC(n bytes)]×numberOfDTC`; "listOfDTCAndStatus is only present if numberOfDTC is > $00"; format/length of statusOfDTC and groupOfDTC are manufacturer specific. 0x17 readStatusOfDTC has the same reply layout under `57`. (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §8.2, §8.3)
- **VAG request = `18 02 FF 00`** (statusOfDTC 0x02, groupOfDTC 0xFF00 = all), falling back to **`18 00 FF 00`**: PY tries `b"\x02\xff\x00"` first ("status 02, group FF00; All Tripped Hex DTCs", mimicking a commercial scanner) and on NRC 0x12 `b"\x00\xff\x00"`; SC tries the same two in the same order; B3 uses `18 00 FF 00`; NEFM-8652: `18 02 FF FF` → `7F 18 12`, `18 00 FF 00` works on an ME7 M-box: "returns the number of stored codes and then a list of three bytes where the first two represent the "P" code and the third is a bitmap showing the code status". DV defines `readFaultCodes_getSupportedFaultCodes 0x03` (`18 03 …` = the list of codes a module can set; the emulator refuses it). (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java ; http://nefariousmotorsports.com/forum/index.php?topic=8652.0;wap2 ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP2000_SID.h)
- **VAG reply = `58 <count>` then `count` × 3 bytes `DTC_hi DTC_lo status`**: DV emulator header `{0x00,0x00 /*len*/, 0x58, count /* DTCs: High, Low, Status */}` with `response_length = 2 + 3*count`; SC `for i in range(0, count*3, 3): (body[i], body[i+1], body[i+2])`; B3 `parseDTCs` 3-byte records from offset 2; PY (incorrectly) steps 2 bytes. (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP1281-VWTP2.0_converter_ESP32.ino ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticTroubleCode.java)
- **The status byte, as VCDS prints it ("Fault Status: bbbbbbbb") on KWP2000 modules**, decoded from real Auto-Scans: the low nibble is the 3-digit "elaboration" shown after the P-code, bit 6 clear means "Intermittent". Pairs seen (code → status): `000 - -` → 01100000; `000 - - - Intermittent` → 00100000; `004 - No Signal/Communication` → 01100100; `007 - Short to Ground` → 01100111; `008 - Implausible Signal` → 01101000; `010 - Open or Short to Plus - Intermittent` → 00101010 and 00111010; `011 - Open Circuit - Intermittent` → 00101011 (3×); `012 - Electrical Fault in Circuit` → 01101100 (4×); `013 - Check DTC Memory` → 01101101; `014 - Defective` → 01101110; `014 - Defective - Intermittent` → 00101110. [corrected] Re-counted with module context: the four scans contain **21 KWP2000 fault records** on addresses 02 (auto trans), 03 (ABS), 09 (central electrics), 0F (radio), 19 (gateway), 44 (steering assist) and 65 (TPMS) — 16 distinct code/status pairs after removing the duplicated MTD scan — and in **every one** `status & 0x0F == elaboration` and `Intermittent ⇔ bit6 == 0`; bit 5 was set in every KWP record; bit 4 was set only in the two central-electrics `00111010` records; bit 7 was never set in a KWP2000 record. The same scans also contain records from UDS modules (printed in VCDS's UDS style `B10AC F0 [008] - Too High / Intermittent - Confirmed - Tested Since Memory Clear` with `Fault Status: 00000001`, and the 2010 CJA engine's `050197 … U0415 - 000 - - MIL ON` with `Fault Status: 11100000`); those are UDS status bytes (ISO 14229 bit 0 testFailed, bit 7 warningIndicatorRequested) and were **excluded** — the `11100000`/"MIL ON" record is the only bit-7 observation and it is UDS, so bit 7 = MIL on KWP2000 modules stays REPORTED. (src: https://forums.tdiclub.com/index.php?threads/got-my-vcds-help-read-my-codes.440170/ ; https://forums.tdiclub.com/showthread.php?t=462915 ; https://www.myturbodiesel.com/threads/cleaning-up-vcds-error-codes-list-guidance.35158/ ; https://caddy2k.com/forum/viewtopic.php?t=46728)
- Two independent code interpretations agree with that: DV converts a KWP1281 elaboration into the KWP2000 status by table-mapping it to a 4-bit code, then `elaboration_code |= 0b00010000` always and `|= 0b01000000` only if the KWP1281 fault was **not** intermittent ("If the fault is "intermittent" in KWP1281, convert it to "Active" in KWP2000"); B3 decodes bit0 aboveThreshold, bit1 belowThreshold, bit2 noInput, bit3 invalidInput, bit4 "complete", bit5 "wasPresent", bit6 "isPresent", bit7 "isCEL" (and `noReason = (status & 0x0F) == 0`). [added] Do **not** copy B3's DTC-number line `((int)bytes[0] & 0xFF) << 8 + (int)bytes[1] & 0xFF`: Java binds `+` tighter than `<<` and `&` loosest, so it computes `((b0 & 0xFF) << (8 + b1)) & 0xFF`, not `b0<<8 | b1`; the intended value is `DTC_hi·256 + DTC_lo` as DV, SC and KL use. (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/KWP1281-VWTP2.0_converter_ESP32.ino ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticTroubleCode.java)
- DV's KWP1281-elaboration → KWP2000-nibble table (index = KWP1281 code & 0x7F, from `KWP1281_to_KWP2000_fault_status_table[]`): 0x00→0, 0x01→6, 0x02→7, 0x03→4, 0x04→3, 0x05→B, 0x06→1, 0x07→2, 0x08→1, 0x09→1, 0x0A→2, 0x0B→2, 0x0C→1, 0x0D→2, 0x0E→1, 0x0F→2, 0x10→8, 0x11→8, 0x12→1, 0x13→2, 0x14→5, 0x15–0x18→E, 0x19→8, 0x1A→B, 0x1B→8, 0x1C→6, 0x1D→7, 0x1E→A, 0x1F→9, 0x20→1, 0x21→2, 0x22→0, 0x23→0, 0x24→B, 0x25→E, 0x26→6, 0x27→7, 0x28→C, 0x29→4, 0x2A→1, 0x2B→E, 0x2C→C, 0x2D→3, 0x2E→E, 0x2F→4, 0x30→8, 0x31→4, 0x32→3, 0x33→3, 0x34→1, 0x35→2, 0x36→5, 0x37→5, 0x38→E, 0x39→C, 0x3A→3, 0x3B→3, 0x3C→E, 0x3D→E, 0x3E→5, 0x3F→1, 0x40–0x42→F, 0x43→3, 0x44–0x4B→E, 0x4C→C, 0x4D→C, 0x4E→4, 0x4F→D, 0x50→C, 0x51→B, 0x52→B. With the KWP1281 names in `dtc_db.md` §F (0x1C short to plus → 6, 0x1D short to ground → 7, 0x24 open circuit → B = 11, 0x12/0x13 upper/lower limit → 1/2, 0x31 no communication → 4, 0x10/0x1B signal outside spec/implausible → 8, 0x39 electric circuit failure → C = 12, 0x04 mechanical → 3) this reproduces the VCDS texts above. (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/responses.h)
- Verbatim KWP2000 elaboration texts seen in fetched scans (code → VCDS text): 000 "-", 001 "Upper Limit Exceeded", 004 "No Signal/Communication", 007 "Short to Ground", 008 "Implausible Signal", 010 "Open or Short to Plus", 011 "Open Circuit", 012 "Electrical Fault in Circuit", 013 "Check DTC Memory", 014 "Defective". (src: same four scans as above)
- **5-digit VAG number = the 16-bit DTC value in decimal**; SAE P/C/B/U codes occupy 0x4000–0x7FFF (16384–32767) with the letter in bits 13-12 (0 P, 1 C, 2 B, 3 U), the second character in bits 11-10 and the **last three digits as a decimal number in the low 10 bits**: KL `isOBDFaultCode: fault_code >= 0x4000 && fault_code <= 0x7FFF`, `getOBDFaultCode`: letter from `(fault_code >> 12) & 0xF` (4 P, 5 C, 6 B, 7 U), `category_code = ((fault_code >> 8) & 0xF) / 4`, `converted_dtc = fault_code - ((letter<<4 | category<<2) << 8)`, rejected if > 999, printed `"%c%d%03d"`. Checks: 0x4065 = 16485 = P0101, 0x4000 = 16384 = P0000; numbers < 16384 (e.g. 00332, 01516, 02391, 00927 in the scans above) are factory codes without an SAE equivalent. (src: https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/main/src/KLineKWP1281Lib.cpp ; https://forums.tdiclub.com/index.php?threads/got-my-vcds-help-read-my-codes.440170/ ; cross-ref dtc_db.md §C)
- Disagreement to resolve on the car: SC's `dtc_str` decodes the 2 bytes with the SAE J2012 **hex-nibble** rule (`letter = "PCBU"[(hi>>6)&3]; "%s%d%X%02X" % (letter, (hi>>4)&3, hi&0xF, lo)`, so 0x4065 would print "P0065"), while KL/VCDS use the decimal rule (0x4065 = P0101). SC's author did not validate this against a known code. See OPEN QUESTIONS 3. (src: https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py)
- **Clear**: `14 FF 00` → `54 FF 00` (DV emulator `VWTP_clear_fault_codes_response = {00,03, 0x54, 0xFF, 0x00}`; B3 `{0x14, 0xFF, 0x00}`; SC tries `14 FF 00` then `14 FF FF` and accepts a `54` reply). ISO 8.5: request `14 [groupOfDiagnosticInformation…]`, reply `54 [same group bytes]` ("parameter shall be present if present in the request"); "If the server(s) doesn't have any DTC … stored the server(s) shall send a positive response". SC warns clearing also discards freeze frames and resets readiness. (src: https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/responses.h ; https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java ; https://raw.githubusercontent.com/vinistoisr/scirocco-dash/main/board/tp20.py ; http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §8.5)
- Freeze frame on KWP2000 modules, as VCDS shows it: "Fault Status", "Fault Priority" (0 undefined … 1 immediate stop … 5 no influence on drivability … 8 general note), "Fault Frequency" (0–254 occurrences), "Reset counter" (problem-free driving cycles left), "Mileage", "Time Indication", "Date"/"Time", and sometimes a second block of measured values ("Term 15 Off, Voltage: 12.55 V"); "The [Display Freeze Frame Data] checkbox adds Freeze Frame data for Fault Codes on control modules using the KWP-2000 or CAN protocols … cars which were re-designed after 2003 will likely have some control modules that support it". ISO's generic service is `12 <freezeFrameNumber> [recordAccessMethodIdentifier 00 all/01 localId/02 commonId/03 memoryAddress/04 byDTC] [recordIdentification…]` → `52 …`. Which bytes VCDS actually sends is not in any fetched source (see REPORTED/OPEN). (src: https://www.ross-tech.com/vcds/tour/dtc_screen.php ; https://forums.tdiclub.com/index.php?threads/got-my-vcds-help-read-my-codes.440170/ ; http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf §8.4)
- Alternative DTC read used by PY's `getDTC`: `13 <group>` readDiagnosticTroubleCodes (reply `53 <count> <DTC_hi DTC_lo>…`, 2 bytes per code, no status) over groups 0..255. (src: https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py)

##### B. DTC byte encoding (ISO 15031-6 / SAE J2012, needed to map a 2-byte DTC to text)

- The 2-byte SAE DTC: bits 15–14 = system letter (00 P, 01 C, 10 B, 11 U), bits 13–12 = first digit (0–3), bits 11–8 = second hex digit, bits 7–0 = last two hex digits. `code = "PCBU"[b0>>6] + str((b0>>4)&3) + f"{b0&0xF:X}{b1:02X}"`. Already implemented in `vagtune/vag/dtc.py::decode_dtc_number` (reads the first two bytes of the 3-byte UDS DTC; third byte = failure type). Primary-source confirmation: Wikipedia OBD-II PIDs (quoted in §A) and the SAE J2012:2002 OCR ("hexadecimal base 16", designators B0–B3/C0–C3/P0–P3/U0–U3). Independent implementation confirmation: KLineKWP1281Lib `getOBDFaultCode()` (§F) decodes letter from `(code>>12)&0xF` ∈ {4,5,6,7} → P,C,B,U and digit from `((code>>8)&0xF)/4` for the 0x4000–0x7FFF window, which is the same bit layout. Re-checked by the verifier against the fresh Ross-Tech title crawl: of the 430 titles that carry both a P-code and a 6-digit number, **428 satisfy `NNNNNN == int(two_byte_code)`**; the 2 misses are title typos (`16764/P0380/000869`, 0x0380 = 896; `P1576/005493`, 0x1576 = 5494). (src: https://en.wikipedia.org/wiki/OBD-II_PIDs ; SAE J2012 OCR; https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/84f90a9a1dc28d8706187fdbf9144e60799e6afe/src/KLineKWP1281Lib.cpp ; computed over `rt_fc_titles.txt`)

##### C. VAG 5-digit (KWP-era) factory number rule — CONFIRMED (three independent ways)

- `N5 = 16384 + LETTER*4096 + int(code[1],16)*1024 + int(code[2:5])` with `LETTER = {P:0, C:1, B:2, U:3}` and **the last three characters read as decimal**. Equivalently **N5 is simply the raw 16-bit fault number the KWP module sends** (`DTC_H<<8 | DTC_L`): 0x4000 = 16384 sets bit 14, the letter occupies bits 13–12, the second character bits 11–10, and the lower 10 bits hold the decimal 000–999 value. Defined only when the last three characters are decimal digits (hex-letter codes such as P17BF have no 5-digit number; they carry a 6-digit number instead). Checks: P0000→16384, P0101→16485, P0299→16683, P1556→17964, P1602→18010, P1296→17704, U0103→28775, U1100→29796, U1101→29797, P3101→19557. Verifier's recount on the fresh crawl: **460 of 467** titles with both a 5-digit and a P-code match; the 7 misses are `31896/U1400/054272` (should be 30096), `17627/P1220` (17628), `17673/P1266/004710` (17674), `19559/P3101/012545` (19557), `16920/P0000/000000`, and the two hex-letter titles `P130A/04874`, `P047F/00115` whose "5-digit" is a mis-formatted 6-digit value. Against the Bentley table: 772 of 774 (misses `16395 P0020` — 16395 is P0011; `17721 P1319` — 17721 is P1313). Against vag-hub: 2100 of 2102 (misses `18853 P2420`, `18854 P2421`). (src: computed over the fresh Ross-Tech crawl, `bentley.txt`, `vaghub.html` in the verify directory; the same rule is in the sibling `uds_vag.md` §F)
- **[NEW] Independent implementation of the same rule** in KLineKWP1281Lib `KLineKWP1281Lib.cpp` (reads KWP1281 fault memory, where each fault is 3 bytes `DTC_H, DTC_L, DTC_ELABORATION`): `isOBDFaultCode(fault_code) { return fault_code >= 0x4000 && fault_code <= 0x7FFF; }`; `getOBDFaultCode`: `switch ((fault_code >> 0xC) & 0xF) { case 4: 'P'; case 5: 'C'; case 6: 'B'; case 7: 'U'; }`, `category_code = ((fault_code >> 8) & 0xF) / 4`, `converted_dtc = fault_code - (((((fault_code >> 0xC) & 0xF) << 4) | (category_code << 2)) << 8)`, rejects `converted_dtc > 999`, prints `"%c%d%03d"`. Numbers < 0x4000 are looked up in its factory table (§F), numbers > 0x7FFF also exist in that table (e.g. 0x8000 "Message Identifer 0", 0x8355 "Gateway", 0xFFFF "Internal Control Module Memory Error"). (src: https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/84f90a9a1dc28d8706187fdbf9144e60799e6afe/src/KLineKWP1281Lib.cpp)
- Inverse: `code = "PCBU"[(N5-16384)//4096] + f"{((N5-16384)%4096)//1024}{(N5-16384)%1024:03d}"` — valid only for 16384 ≤ N5 ≤ 32767 (and the last-three field < 1000 by construction). Numbers 00000–16383 are factory-only codes with no SAE equivalent → look them up in `vag_5digit_only` / the §F table; numbers ≥ 32768 are also factory-only (546 in the §F table). (src: same)
- 6-digit UDS-era number: `N6 = (LETTER<<14) | (int(code[1],16)<<12) | int(code[2:],16)` i.e. the decimal value of the 2-byte SAE DTC, printed with 6 digits (P0101→000257, P0299→000665, P1556→005462, P1602→005634, P173C→005948, P00AF→000175, P2404→009220, U1013→053267, P2002→008194, P0401→001025, P1296→004758). **[CORRECTED]** Ross-Tech's title `13636352/U1013` is **0xD01300** (= 0xD013 × 256, the 3-byte DTCRecord with failure-type byte 0x00 read as a 24-bit integer), not "0xD00D00". (src: Ross-Tech titles, forum 7680 and forum 22128 above)

#### Reported / unverified (confidence)

- **Freeze frame bytes**: VCDS's per-fault "Fault Priority / Frequency / Reset counter / Mileage / Time Indication / Date-Time" on KWP2000 modules most likely come from `12 <frame#> 04 <DTC_hi> <DTC_lo>` (readFreezeFrameData by DTC) or a VAG-specific `18` status value (0x03?) that appends the record; the KWP1281-era "0118 HEX-coded fault codes" capability bit suggests a second (hex) DTC format exists on some modules. Confidence **low**. Confirm on car (OPEN QUESTIONS 4).
- **Status byte bits 4/5/7**: bit 5 ("wasPresent"/stored, B3) was set in every real KWP record fetched; bit 4 is forced on by DV; bit 7 = MIL/"warning lamp" (B3 `isCEL`; VCDS prints "MIL ON" on engine-module faults with the top bit set — the only fetched example, tdiclub-462915 address 01 CJA engine `U0415 - 000 - - MIL ON` → `11100000`, is a UDS module, where bit 7 is ISO 14229 warningIndicatorRequested, so it says nothing about KWP2000). [corrected] Confidence **low-medium** for bit 7 = MIL on KWP2000 modules, **low** for bits 4/5 semantics. Confirm: a VCDS scan of the R32 engine (KWP2000, 0x01) with a MIL-setting fault; expect `1xxxxxxx` in the `18 02 FF 00` reply.
- **Elaboration texts for the codes not seen verbatim**: 002 "Lower Limit Exceeded", 003 "Mechanical Malfunction", 005 "No or Incorrect Basic Setting / Adaptation", 006 "Short to Plus", 009 "Open or Short to Ground", 015 "Unknown Switch Condition" — from memory of VCDS scans plus the DV mapping (0x1C short-to-plus → 6, 0x13 lower limit → 2, 0x04 mechanical → 3, 0x14/0x36/0x37 → 5). Confidence **medium** (009/010/012/014 were confirmed by a search-engine snippet of a VCDS code list, not a fetched page). Confirm with any Auto-Scan that shows them.
- **VCDS "Supported Codes" (function 18)** = `18 03 FF 00` (DV `readFaultCodes_getSupportedFaultCodes 0x03`); reply format presumably identical to `58`. Confidence **medium**.
- **PyVCDS DTC parsing** (2-byte records) is wrong for `58` replies (3 bytes per record, verified above); do not copy it.

- **medium** — The VCDS "- NNN -" field between the P-code and the fault text (`P2002 - 007 -`, `P0401 - 001 -`, `P173C - 000 -`) is the raw third DTC byte (FTB) printed in **decimal**; on KWP modules VCDS prints it as `XX-YY` (elaboration code, then `10` when intermittent / `00` when static). The decimal/hex question cannot be settled from the fetched examples (000, 001, 002, 007 are the same in both); Ross-Tech headings `C10E2 01`/`C10E2 54` print it in hex. Confirm with OPEN QUESTION 3. If decimal, `007` = FTB 0x07 "Mechanical Failure" category for P2002 and `001`/`002` = "General Electrical Failure"/"General Signal Failure" for P0401 — plausible but unproven.
- **low** — The Ross-Tech `vag_fault_variants` suffixes are the VCDS rendering of the KWP elaboration byte (§F table). The mapping given in §F is by text matching; VCDS may use different strings for the same byte (e.g. "Electrical Fault in Circuit"). Build the byte→VCDS-text table on the car (OPEN QUESTION 3).


### 7.9 DTC description database (`dtc_db.json`) and fault-type tables (KWP elaboration 0x00–0x52, UDS FTB)

Source sheet: `dtc_db.md` (sources re-fetched, counts recomputed) plus the FTB rows of `uds_vag.md` Reported (see conflict C14: the autodtcs rows disagree with the two-table consensus in §G).

#### Verified (source)

Deliverable data file: `dtc_db.json` (same directory). Generator: `build_dtc_db.py` (same
directory; re-runnable, reads only files already fetched into this directory). JSON validated
with `python -c "import json; json.load(open(path))"`. **The JSON has NOT been regenerated by the
verifier**; see OPEN QUESTIONS 7–9 for the changes the generator needs (new tables, placeholder rows).

JSON shape (top-level keys):

| key | content |
|---|---|
| `source_notes` | provenance narrative (string) |
| `stats` | counts by prefix and by source |
| `codes` | `{"P0001": "Fuel Volume Regulator Control Circuit/Open", ...}` — 10698 codes, every description ≤ 90 chars (re-checked: max 90) |
| `provenance` | `{"P0001": "pyobd", ...}` — which fetched source each description came from (tags below). Re-checked counts: pyobd 2066, wal33d-generic 7183, bentley-vw 370, rosstech-wiki 344, vaghub-translated 728, memory-unverified 5, rosstech-forum-7680 1, actronics-page 1 |
| `vag_wording` | `{"P0101": "Mass Air Flow Sensor (G70): Implausible Signal", ...}` — 1113 entries of VW/Ross-Tech wording for the same code, when it differs from SAE |
| `vag_legacy` | `{"16485": "P0101", ...}` — KWP-era 5-digit factory number → P/U code (4107 entries, computed by the verified rule below) |
| `vag_5digit_only` | `{"00287": "ABS Wheel Speed Sensor Rear Right (G44)", ...}` — 409 factory numbers 00000–16383 that have **no** P-code (ABS, airbag, Haldex, comfort, cluster, gateway...). **The KLineKWP1281Lib table (§F) has 4279 such codes; 3872 of them are missing here.** |
| `vag_fault_variants` | `{"00287": ["Signal Outside Specifications", "Electrical Fault in Circuit", ...]}` — fault-type suffixes seen for a code (821 entries) |

Provenance tags: `pyobd` (python-OBD codes.py), `wal33d-generic` (Wal33D/dtc-database SQLite,
GENERIC rows), `bentley-vw` (Bentley Publishers VW DTC table PDF), `rosstech-wiki` (Ross-Tech
Wiki page headings), `rosstech-forum-7680`, `actronics-page`, `vaghub-translated` (vag-hub.com
list — machine-translated, low wording quality, gap-filler only), `memory-unverified`.

##### A. Sources actually fetched (all re-fetched by the verifier; sizes and counts recomputed)

- python-OBD `obd/codes.py` — a Python dict `DTC = {"P0001": "Fuel Volume Regulator Control Circuit/Open", ...}` with **2066 entries** (re-counted): P0001–P0999 contiguous except P0395–P0399 (994 decimal codes + P0A00–P0A29 hybrid codes = 1024 P0 entries; **no P0000**), P2000–P2795 in runs 2000–2071, 2075–2347, 2400–2447, 2500–2577, 2600–2671, 2700–2795 plus P2A00–P2A05 (645 entries), P3400–P3497 (98 entries, cylinder deactivation), U0001–U0431 in runs 0001–0235, 0300–0331, 0400–0431 (299 entries). No P1, B, C, U1/U3 codes. Longest description 90 chars (P2757). The file also defines `IGNITION_TYPE, BASE_TESTS, SPARK_TESTS, COMPRESSION_TESTS, FUEL_STATUS, AIR_STATUS, OBD_COMPLIANCE, FUEL_TYPES, TEST_IDS` (useful for the OBD-II domain). **[CORRECTED]** the "lntake" (lowercase-L) typo occurs in **48 entries, P3401–P3492** (odd/intake entries only), not P3401–P3496. (src: https://raw.githubusercontent.com/brendan-w/python-OBD/master/obd/codes.py)
- **[NEW] SAE J2012 (2002 edition, 62-page scan, OCR'd with tesseract)** — the actual standard, publicly mirrored. Appendix B/C list ~1190 code rows readable by OCR (P0 577, P2 484, P3 61, U0 68). Compared with python-OBD: 1189 codes shared; 569 identical after punctuation normalisation and 1051 of 1189 at ≥0.85 similarity, the remainder being OCR noise. So **python-OBD's P0/P2/U0 wording is the SAE J2012:2002 wording** (promoted from REPORTED). One systematic difference: J2012's table has a separate right-hand column with the bank/sensor qualifier that python-OBD drops — e.g. J2012 `P0420 Catalyst System Efficiency Below Threshold … Bank 1`, `P0030 HO2S Heater Control Circuit … Bank 1 Sensor 1`, `P2000 NOx Trap Efficiency Below Threshold … Bank 1`, vs python-OBD `P0420 Catalyst System Efficiency Below Threshold`. Section 5 of the OCR text: "5.4.1 B0XXX ISO/SAE CONTROLLED, 5.4.2 B1XXX MANUFACTURER CONTROLLED, 5.4.3 B2XXX MANUFACTURER CONTROLLED, 5.4.4 B3XXX RESERVED BY DOCUMENT" (same for C), "5.6.1 P0XXX ISO/SAE CONTROLLED, 5.6.2 P1XXX MANUFACTURER CONTROL, 5.6.3 P2XXX ISO/SAE CONTROLLED, 5.6.4 P3XXX MANUFACTURER CONTROLLED AND ISO/SAE RESERVED, 5.7.1 U0XXX ISO/SAE CONTROLLED, 5.7.2 U1XXX MANUFACTURER CONTROLLED, 5.7.3 U2XXX MANUFACTURER CONTROLLED, 5.7.4 U3XXX RESERVED"; "Some ranges have been expanded beyond 100 numbers by using the hexadecimal base 16 number system." (src: https://law.resource.org/pub/us/cfr/ibr/005/sae.j2012.2002.pdf ; OCR text at `/tmp/claude-0/-home-user-ruggedroute-dataops/48ce5be0-8644-5203-bb2d-ad0c5c5816d2/scratchpad/verify_dtc/sae_ocr.txt`)
- Wal33D/dtc-database `data/dtc_codes.db` (SQLite, MIT) — table `dtc_definitions(code, manufacturer, description, type, locale, is_generic, source_file)` with primary key `(code, manufacturer, locale)`; `manufacturer='GENERIC'` has 9415 rows (all locale `en`): B0 189, B1 7, B2 11, B3 93, C0 478, C1 19, C2 1, P0 3704, P1 32, P2 3495, P3 156, U0 1054, U1 1, U2 1, U3 174 (re-counted, exact). 6242 GENERIC codes have hex letters in the last three characters; minus the 36 that python-OBD also has (P0A00–P0A29, P2A00–P2A05) = 6206 extras, as stated. Its P1/B1/C1/U1/U2 "generic" rows are Ford/GM wording (`P1101 MAF Sensor Out Of Self Test Range./KOER Not Able To Complete KOER Aborted` re-confirmed) and were **excluded**. 13 GENERIC descriptions exceed 90 chars. It also contains placeholder rows such as `B3000 "B3000-B3999 ISO/SAE Reserved"` and `U1000/U2000/C1000 "Manufacturer Controlled DTC"` (filtered by the generator, except see §D "placeholder rows"). **[CORRECTED]** The `VOLKSWAGEN` manufacturer rows (528) are **all P1** codes (no P0 rows exist, so the original sheet's remark about "P0 rows being possible-causes text" is wrong); the code set is Bentley's P1 set minus 12 codes (P1221–P1223, P1296, P1297, P1344, P1474, P1705, P1740, P1764, P1776, P1777) plus P1780, and the **wording differs from Bentley** (Wal `P1101 Oxygen Sensor Circuit Bank 1 Sensor 1 Voltage Too Low/Air Leak` vs Bentley `P1101 O2 Sensor Heating Circ.,Bank1-Sensor1 Short to B+`) — Wal's VW rows are not used. (src: https://raw.githubusercontent.com/Wal33D/dtc-database/main/data/dtc_codes.db ; README https://raw.githubusercontent.com/Wal33D/dtc-database/main/README.md)
- Bentley Publishers "Volkswagen Diagnostic Trouble Codes — DTC Table - General" (23-page PDF, © 2001–2004 Robert Bentley, Inc., 2007 compilation) — `pdftotext -layout` gives 1728 lines; regex `^\s*(\d{5})\s+([PCBU][0-9A-F]{4})\s+(.+)$` yields **774 rows: 235 P0, 539 P1 (P1101 … P1866)**, every row with the factory 5-digit number (re-counted, exact). Quoted rows re-confirmed at these text lines: `16485 P0101` (l.135), `17704 P1296` (l.891), `17963 P1555`, `17964 P1556`, `17965 P1557` (l.1269–1273), `18010 P1602` (l.1339), `18057 P1649`, `18058 P1650` (l.1431–1433), plus the two typo rows `16395 P0020` (l.127) and `17721 P1319` (l.897). Page text re-confirmed: "DTCs are assigned two codes. The first code is a numerical code assigned by the factory. The second code is referred to as a P-code". (src: http://www.vaglinks.com/Docs/VW/BentleyPublishers.com_VW_DTC_Table.pdf)
- Ross-Tech Wiki `Special:AllPages` — **[CORRECTED]** a complete crawl by the verifier (7 listing pages, following "Next page (…)" links with URL-encoded continuation titles) returns **1598 titles total, of which 1040 match the fault-code title grammar**. The research agent's 1079 "selected" titles = these 1040 (minus 2) **plus 41 redirect titles** that `Special:AllPages` hides (e.g. `16490/P0106` → page `16490/P0106/000262`, `000175` → `P00AF/000175`, `18010/P1602` → `18010/P1602/005634`); fetching a redirect returns the target page, so the agent's "1079 real pages" is really 1038 distinct pages + 41 aliases. The crawl is therefore complete (resolves old OPEN QUESTION 6). Title formats in the 1040: `NNNNN` 418, `NNNNN/Pxxxx/NNNNNN` 344, `NNNNN/Pxxxx` 121, `Pxxxx` 68, `Pxxxx/NNNNNN` 86, `Pxxxx/NNNNN` 2 (`P047F/00115`, `P130A/04874` — hex-letter codes whose "5-digit" is really the 6-digit value, 0x130A = 4874), `NNNNNN` 1. Each page's first content heading is `<ids> - <Component>[: <fault type>]`; re-fetched and confirmed verbatim: `16485/P0101/000257 - Mass Air Flow Sensor (G70): Implausible Signal`, `17964/P1556 - Charge Pressure Control: Negative Deviation` (page title `17964/P1556/005462`), `16683/P0299/000665 - Boost Pressure Regulation: Control Range Not Reached`, `18010/P1602/005634 - Power Supply B+ Terminal 30: Voltage too Low`, `00287 - ABS Wheel Speed Sensor Rear Right (G44)` with sub-headings `: Signal Outside Specifications`, `: Electrical Fault in Circuit`, `: Mechanical Malfunction`; `01044 - Control Module Incorrectly Coded` (+ `: Implausible Signal`); `01314 - Engine Control Module` (+ `: No Communications`, `: Check DTC Memory`); `00668 - Supply Voltage Terminal 30` (+ `: Signal Outside Specifications`, `: Implausible Signal`). **[CORRECTED]** the P1296 page is `17704/P1296/004758` (0x1296 = 4758), heading `17704/P1296/004758 - Error in Mapped Cooling System`; the URL `/17704/P1296/005270` cited by the original sheet is an empty page. The wiki's own template page states the naming convention: "Page Name for VAG-OLD DTCs (DTC 00001-04500): '01234 - Your DTC Text'; Page Name for ALL other DTCs: '12345/P1234/123456 - YOUR DTC Text' (VAG / OBD2 / VAG-NEW)" and the secondary headline `NNNNN - ABC: DEF` is "ONLY for VAG-OLD DTC Entries (00001-04500)". Random re-fetch of 44 agent-selected pages vs the JSON: 41 headings identical to `vag_wording`/`vag_5digit_only`; the 3 misses are `00873` (page exists, `Bass Speaker Rear Right (R17)`, but missing from `vag_5digit_only`), `00543` (heading reads `17968 - Maximum Engine Speed Exceeded`) and `C10E2` (headings `C10E2 01 - Control Module for Electronic Parking Brake: Electrical Failure` and `C10E2 54 - …: Missing Calibration / Basic Setting` — a `CODE FTB -` format the generator's regex does not match; `B1916 04 - Backup Battery - Internal System Fault` is the third such page). (src: https://wiki.ross-tech.com/wiki/index.php?title=Special:AllPages&from=00000 and following pages; https://wiki.ross-tech.com/wiki/index.php/Fault_Code_(Template/Explanations) ; individual pages https://wiki.ross-tech.com/wiki/index.php/16485/P0101/000257 , /17964/P1556/005462 , /16683/P0299/000665 , /18010/P1602/005634 , /17704/P1296/004758 , /00287 , /01044 , /01314 , /00668 , /C10E2 ; full title list at `/tmp/claude-0/-home-user-ruggedroute-dataops/48ce5be0-8644-5203-bb2d-ad0c5c5816d2/scratchpad/verify_dtc/rt_alltitles.txt`)
- Ross-Tech forum thread 7680 ("0AM DSG Fault codes P173A P173B P173C P173D P173E P173F", 2016, poster SI-R32) — re-fetched; quotes the VCDS lines `005948 - Position Sensor 3 for Gear Selector` / `P173C - 000 - Implausible Signal - MIL ON` / `Fault Status: 11100000`. 0x173C = 5948, confirming the 6-digit rule for a DSG code. The thread title lists P173A–P173F but only P173C's text is quoted. (src: https://forums.ross-tech.com/index.php?threads/7680/)
- **[NEW] Ross-Tech forum thread 22128 ("2012 VW TDI Sportwagen, P0401 *and* P2002 codes")** — a VCDS Auto-Scan of exactly the owner's engine family: `Address 01: Engine (CJA)  Labels: 03L-906-022-CBE.clb / Part No SW: 03L 997 030 E  HW: 03L 907 309 AA / Component: R4 2.0l TDI G000AG 9983 / Coding: 0050078`, with fault lines `008194 - Particulate Trap Bank 1` / `P2002 - 007 - Efficiency Below Threshold - MIL ON` / `Fault Status: 11100111 / Fault Priority: 2` and `001025 - EGR System` / `P0401 - 001 - Insufficient Flow - Intermittent` (also `P0401 - 002 - …`). 0x2002 = 8194 and 0x0401 = 1025: the 6-digit rule holds on the EDC17CP14 itself, and the VCDS text for this ECU is split as `<component>` on the first line and `<fault type>` after the P-code. (src: https://forums.ross-tech.com/index.php?threads/22128/)
- **[NEW] Volkswagen Technical Bulletins hosted by NHTSA** — official VW wording for the TDI DPF family: TSB 01-18-13 "MIL ON DTC P0401, P2002 or P240F Exhaust Gas…" (applies to CJAA Golf/Jetta/SportWagen/Beetle); TSB SB-10065349 lists "DTC P2452: Diesel Particulate Filter Differential Pressure Sensor Circuit; DTC P2453: … Circuit Range/Performance; DTC P2454: … Circuit Low; DTC P2456: Diesel Particulate Filter Pressure Sensor "A" Circuit Intermittent/Erratic; DTC P2002: Particulate Trap Bank 1 Efficiency Below Threshold" stored in "the engine control module (ECM), J623 (address word 01)". All five codes exist in `codes` (P2452–P2456 from Wal33D, P2002 from python-OBD) and P240F exists (`EGR Slow Response`, Wal33D). (src: https://static.nhtsa.gov/odi/tsbs/2022/MC-10212132-0001.pdf ; https://static.nhtsa.gov/odi/tsbs/2013/SB-10065349-6903.pdf)
- Actronics page — re-fetched; "P17BF – Hydraulic Pump System Overload Protection" and "P189C – Function Restriction due to Insufficient Pressure Build-Up"; the page is titled "VW DQ200 DSG – P17BF & P189C Fault Code Explained", mentions DQ200 14× and 0AM 3×, and never mentions DQ250/02E (so the sheet's "not the R32's DQ250" is an inference from the page's scope, not a statement on the page). (src: https://www.actronics.co.uk/dq200-dsg-p17bf-p189c-fault-codes-tcu-repair)
- vag-hub.com "Volkswagen Error Codes list" — re-fetched; regex `(\d{5})\s+([PCBU][0-9A-F]{4})\s+(.+)` yields **2102 rows (P0 524, P1 950, P2 229, P3 399)**, exact. **[CORRECTED]** its P1296 text is `17704 P1296 Cooling system failure` (not "Malfunction of the cooling system"); `17964 P1556 Boost pressure regulator: out of control range (less than the lower limit)` and `17963 P1555 Maximum boost pressure exceeded` confirmed; `18278 P1870 KP-N262 left support valve: open circuit` confirmed. **[CORRECTED]** errors-codes.jimdofree.com/vag/ (2039 rows) and vag-coding.net (1904 rows) are **not mirrors**: they are different translations (jimdo `16394 P0010 Series 1: a malfunction in the valve timing`; vag-coding `16394 P0010 Intake camshaft sensor, line 1 – circuit failure`; vag-hub has its own wording). They were not used for wording. (src: https://www.vag-hub.com/vw-error-codes/ ; https://errors-codes.jimdofree.com/vag/ ; https://www.vag-coding.net/tutorials-information/fault-codes/)
- gist wzr1337 "OBD DTC diagnostic trouble code - a complete list (hopefully)" — re-fetched; JSON dict with 3745 codes (starts `P0000 No trouble code`); `P0005 Fuel Shutoff Valve Control Circuit / Open` (drops the SAE 'A'); `P1101` is the Ford text. **[CORRECTED]** vs python-OBD it shares 1088 P0/U0 codes and the wording differs in 725 of them (verifier's exact string compare; the original "704 of 1093" used a different normalisation). Not used for wording. (src: https://gist.githubusercontent.com/wzr1337/8af2731a5ffa98f9d506537279da7a0e/raw/)
- mytrile/obd-trouble-codes — re-fetched; a JSON **list of 3070** objects (not 3071) whose keys are the CSV header row (`{"P0100": "P0101", "Mass or Volume Air Flow Circuit Malfunction": "Mass or Volume Air Flow Circuit Range/Performance Problem"}`), i.e. a broken CSV conversion. Not used. (src: https://raw.githubusercontent.com/mytrile/obd-trouble-codes/master/obd-trouble-codes.json)
- todrobbins/dtcdb `generic.csv` — re-fetched; 491 lines, 469 P0 rows + 7 malformed. Not used. (src: https://raw.githubusercontent.com/todrobbins/dtcdb/master/generic.csv)
- **[NEW] Wikipedia "OBD-II PIDs", service 03 section** — "the first character (here 'U') represents the category … The first two bits (A7 and A6) of the first byte (A) represent the category. The remaining 14 bits represent the number. … since the second character is formed from only two bits, it can thus only be within the range 0–3. A7–A6: 00 P - Powertrain, 01 C - Chassis, 10 B - Body, 11 U - Network; A5–B0: Number (within category)". (src: https://en.wikipedia.org/wiki/OBD-II_PIDs)

##### D. Generic code families (what is in `codes` and where it came from)

- P0000–P0999: every entry of python-OBD (SAE J2012 powertrain) with its wording; P0395–P0399 (cylinder-1 pressure sensor: `P0395 Cylinder 1 Pressure Sensor Circuit`, `P0399 … Intermittent/Erratic`) came from Wal33D. Then every J2012-DA hex-letter code P0Axx–P0Fxx from Wal33D (e.g. `P0A2A Drive Motor A Temperature Sensor A Circuit`). `P0000` in the JSON is `Undocumented/Reserved Fault Code` (tag rosstech-wiki, from page `16920/P0000/000000`). (src: the files above)
- P2000–P2999: python-OBD runs listed in §A; gaps (P2072–P2074, P2348–P2399, P2448–P2499, P2578–P2599, P2672–P2699, P2796–P2999) and P2Axx–P2Fxx filled from Wal33D. (src: same)
- P3400–P3497: python-OBD (cylinder deactivation, "Cylinder N Deactivation/Intake Valve Control ..." / "Cylinder N Exhaust Valve Control ..."; python-OBD spells it "lntake" with a lowercase L in 48 entries P3401–P3492 — that typo is preserved in `codes` since the fetched wording was kept verbatim; fix with `.replace("lntake","Intake")` at load time). Other P34xx (P3498–P34C8, e.g. `P34C8 Camshaft Position Control Module Performance`) from Wal33D. (src: same)
- U0001–U0431: python-OBD; U0432–U0901 (`U0432 Invalid Data Received From Multi-axis Acceleration Sensor Module A` … `U0901 Invalid Data from Ion Sense Module`) and U3000–U3576 (`U3000 Control Module` … `U3576 Stack Differential Pressure Sensor Circuit`) from Wal33D. SAE marks U1xxx/U2xxx as manufacturer-controlled (J2012 §5.7.2/5.7.3): Wal33D has only the placeholders `U1000`/`U2000 Manufacturer Controlled DTC`, which were dropped. (src: same)
- B0001–B0134 (189 entries: `B0001 Driver Frontal Stage 1 Deployment Control` … `B0134 A/V Sensor Washer Fluid F Control Circuit`) and C0001–C066F (478 entries: `C0001 TCS Control Channel A Valve 1` … `C066F Service/Park Brake Chamber Pressure Too Low`) from Wal33D GENERIC. These are the only "standardized" body/chassis codes available in a fetched open file; SAE J2012:2002 itself lists no B0/C0 descriptions (reserved for later J2012-DA). (src: Wal33D DB above; SAE J2012 OCR)
- **[NEW] Placeholder rows present in `codes`** (42 entries whose "description" is a reservation note, all inherited verbatim from the sources): P0000, P0364, P0383, P0384, U0074, U0075, U0076, U0077, U0078, U0079, U0080, U0081, U0082, U0083, U0084, U0085, U0086, U0087, U0088, U0089, U0090, U0091, U0092, U0093, U0094, U0095, U0096, U0097, U0098, U0099, U0116, U0117, U0118, U0119, U0120, U0133, U0134, U0135, U0136, U0137, U0138, U0139. `P0364 Reserved`, `P0383/P0384 Reserved by SAE J2012`, `U00xx/U01xx Reserved by J2012` come from python-OBD; `P0000` from the Ross-Tech page. The loader should treat these as "no description" (regex `^(Reserved|Undocumented)`), otherwise `vagtune dtc` will print "Reserved by J2012" as if it were a fault text. (src: computed over `dtc_db.json` and `pyobd_codes.py`)

##### E. VAG-specific families present

- P1101–P1866: Bentley table (539 codes with 5-digit numbers), overridden by the Ross-Tech heading where a wiki page exists (344 codes carry tag `rosstech-wiki`; that count also includes the UDS-era VAG manufacturer codes B1xxx/B2xxx/C1xxx/U1xxx/P1xxx-with-hex-letters that exist only as Ross-Tech pages, e.g. `B100D Driver's Safety Belt Tensioner Igniter 2`, `U1013 Control Module Not Coded`). Re-fetched examples: `P1545 Throttle Valve Controller: Malfunction` (RT page `17953/P1545/005445`), `P1555 Boost Pressure Control: Upper Limit Exceeded`/Bentley `Charge Pressure Upper Limit exceeded`, `P1556 Charge Pressure Control: Negative Deviation`, `P1557 Charge Pressure Control: Positive Deviation`, `P1602 Power Supply B+ Terminal 30: Voltage too Low`, `P1625 Powertrain Data Bus: Implausible Message from TCU` (RT; Bentley `Data-Bus Powertrain Unplausible Message from Transm.Contr.`), `P1649 Powertrain Data Bus: Missing Message from ABS Controller`, `P1650 … from Instrument Cluster`, `P1854 Data-Bus Powertrain Hardware Defective`, `P1855 Data-Bus Powertrain Software version Contr.`, `P1296 Error in Mapped Cooling System` (RT page `17704/P1296/004758`) / `Cooling system malfunction` (Bentley). (src: Bentley PDF and Ross-Tech pages above)
- VAG P1000–P1100 and P1867–P1999, and VAG-controlled P3000–P3399 (TDI glow plug, CNG, misc.) only exist in the vag-hub translated list → included with tag `vaghub-translated` (728 codes: 354 P1, 374 P3); wording is readable but not VW's English (e.g. `P1870 KP-N262 left support valve: open circuit`; the §F table has `P1870 Transmission Mount Valve 1 (N262): Open Circuit`, which is the VCDS wording). (src: vag-hub.com above)
- DSG mechatronic codes verified from fetched pages: `P173C Position Sensor 3 for Gear Selector: Implausible Signal` (6-digit 005948, forum 7680), `P17BF Hydraulic Pump System Overload Protection`, `P189C Function Restriction due to Insufficient Pressure Build-Up` (Actronics, DQ200/0AM page; `P189C` also has a Ross-Tech page). P173A, P173B, P173D meaning confirmed by two secondary pages: eco-torque "P173A Gear Position Sensor 1 Signal Implausible / P173B Gear Position Sensor 2 … / P173C … 3 … / P173D Gear Position Sensor 4 Signal Implausible" and audiownersclub thread title "P173A – Position sensor 1 for Gear Selector: implausible"; all DQ200/0AM. The exact VCDS text `Position Sensor N for Gear Selector: Implausible Signal` for N=1,2,4 is by analogy with the verified P173C line (see REPORTED). (src: https://forums.ross-tech.com/index.php?threads/7680/ ; https://www.actronics.co.uk/dq200-dsg-p17bf-p189c-fault-codes-tcu-repair ; https://eco-torque.co.uk/blogs/news/understanding-the-0am-dsg-mechatronic-tcu-fault-codes-p173a-p173b-p173c-p173d )
- 5-digit-only factory codes (`vag_5digit_only`, 409 entries) — these are what the R32's KWP2000/TP2.0 modules (ABS 03, airbag 15, Haldex 22, gateway 19, comfort 46, cluster 17...) report; examples `00003 Control Module`, `00287 ABS Wheel Speed Sensor Rear Right (G44)`, `00668 Supply Voltage Terminal 30`, `01044 Control Module Incorrectly Coded`, `01314 Engine Control Module`, `00149 End of Line Programming not Completed`. Haldex-relevant entries present and cross-confirmed by the §F table: `01324 Control Module for All Wheel Drive (J492)`, `00290 ABS Wheel Speed Sensor Rear Left (G46)`, `00285 … Front Right (G45)`, `01312 Powertrain Data Bus`, `01299 Diagnostic Interface for Data Bus (J533)`, `01316 ABS Control Module`, `01315 Transmission Control Module`; **missing** from the JSON but in §F: `00448 Haldex Clutch Pump (V181)`, `00286 ABS Inlet/Outlet Valve; Rear Left (N139)`, `01313 Data Bus for Powertrain in Emergency-Mode`, `01311 Information Data Bus`, `00873 Bass Speaker Rear Right (R17)`. (src: Ross-Tech pages above; §F table)

##### F. [NEW] KLineKWP1281Lib fault-text tables (GPL-3, fetched raw; the most complete open VAG fault-text source found)

Repository `domnulvlad/KLineKWP1281Lib` (Arduino K-line KWP1281 library, v2.2.1, `LICENSE.md` = GNU GPL v3; credits blafusel.de, Alexander Grau, Mike Naberezny/vwradio). Commit `84f90a9a1dc28d8706187fdbf9144e60799e6afe`. All three files are plain `const char NAME_XXXX[] PROGMEM = "text";` lines plus a `{0xXXXX, NAME_XXXX}` lookup array (key == name suffix in every row, checked).

- `src/fault_code_description_EN.h` (519 KB): **4825 entries keyed by the raw 16-bit KWP fault number**: 4279 keys in 0x0000–0x3FF9 (= 5-digit 00000–16377, the factory-only range), **0 keys in 0x4000–0x7FFF** (that range is served by the OBD file below), 546 keys in 0x8000–0xFFFF (bus-message and internal entries, e.g. `0x8000 Message Identifer 0`, `0x8280 Message Identifier 280`, `0x82C5 Terminal Status`, `0xFFFF Internal Control Module Memory Error`). Spot values: `0x0000 End of output`, `0x0001 Brake Control Unit`, `0x0003 Control Module`, `0x0095 (149) End of Line Programming not Completed`, `0x011F (287) ABS Wheel Speed Sensor; Rear Right (G44)`, `0x029C (668) Supply Voltage Terminal 30`, `0x0414 (1044) Control Module Incorrectly Coded`, `0x0522 (1314) Engine Control Module`, `0x052C (1324) Control Module for All Wheel Drive (J492)`, `0x01C0 (448) Haldex Clutch Pump (V181)`, `0x021F (543) Maximum Engine Speed Exceeded -- Engine Warranty VOID! ;-)` (joke text, sanitize). Agreement with the 409 Ross-Tech-derived `vag_5digit_only` entries: 350 identical after punctuation normalisation, 28 near-identical, 29 differ only because the Ross-Tech heading embeds a fault-type suffix or a Ross-Tech note (e.g. RT `00522 Engine Coolant Temp. Sensor (G62): Break in wiring / short circuit to positive` vs lib `Engine Coolant Temperature Sensor (G62)`; RT `00811 System Not Ready for Interrogation (Ross-Tech: Check Fault Codes Later)` vs lib `System Not Ready for Interrogation`), 2 absent. Max length 92 chars. **3872 factory codes in this file are absent from `vag_5digit_only`.** (src: https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/84f90a9a1dc28d8706187fdbf9144e60799e6afe/src/fault_code_description_EN.h)
- `src/OBD_fault_code_description_EN.h` (558 KB): **4571 entries keyed by the 2-byte SAE DTC value** (`OBD2_FAULT_0001` = P0001 = 0x0001 … max key 0xD699 = U1699): P0 999, P1 1000, P2 815, P3 502, U0 563, U1 692 — **every decimal-digit P0/P1/P2/P3/U0/U1 code, VW/VCDS wording, no hex-letter codes**. Spot values: `P0001 Fuel Volume Regulator 1: Open Circuit`, `P0101 Mass Air Flow Sensor (G70): Implausible Signal`, `P0299 Boost Pressure Regulation: Control Range Not Reached`, `P0401 EGR System: Insufficient Flow`, `P0420 Catalyst System; Bank 1: Efficiency Below Threshold`, `P0671 Cylinder 1 Glow Plug Circuit (Q10): Electrical Fault`, `P0706 Transmission Range Sensor (F125): Implausible Signal`, `P0721 Transmission Output Speed Sensor (G195): Implausible Signal`, `P0730 Gear Ratio Monitoring: Incorrect Gear Ratio`, `P0731 Gear 1: Incorrect Ratio`, `P0736 Reverse Gear: Incorrect Ratio`, `P1296 Error in Mapped Cooling System (check Temp-Sensor and Thermostat)`, `P1545 Throttle Valve Controller: Malfunction`, `P1555 Charge Pressure: Maximum Limit Exceeded`, `P1556 Charge Pressure Control: Negative Deviation`, `P1602 Power Supply Terminal 30: Voltage too Low`, `P1649 Powertrain Data Bus: Missing Message from ABS Controller`, `P1650 … from Instrument Cluster`, `P1700 Brake Pressure Switch (F270): Implausible Signal`, `P1709 Gear Position Switch 1-3: Voltage too High`, `P1750 Supply Voltage: too Low`, `P1757 Supply Voltage: Open Circuit`, `P1850 Powertrain Data Bus: Missing Message from ECU`, `P1855 Powertrain Data Bus: Software Version Monitoring`, `P1866 Powertrain Data Bus: Missing Messages`, `P1895 Functional Restriction due to Pressure Drop`, `P2002 Particulate Trap Bank 1: Efficiency Below Threshold`, `P2463 Particle Filter: Excessive Soot Accumulation`, `P3000 Glow Plug Indictor Light (K29): Malfunction Message from Instrument Cluster`, `P3101 Motor for Intake Manifold Flap (V157): Open or Short to Ground`, `U0001 Powertrain Databus: Unspecified Malfunction`, `U0100 No Communication with Engine Control Module (SAE ECM/PCM)`, `U0121 No Communication with ABS Brake Control Module`, `U1013 Control module not coded`, `U1100 Component Protection: No Basic Setting`, `U1101 Component Protection: Active`, `U1699 Local Databus 32: Electrical Malfunction`, `P0000 SAE - Reserved by Document ISO/SAE J2012-2018` (placeholder). Agreement with the JSON's `vag_wording` on the 999 overlapping codes: 375 identical, 212 near-identical, 412 differ (mostly Bentley abbreviations vs VCDS long form, e.g. lib `P0122 Throttle Position Sensor (G69): Signal too Low` vs Bentley `Throttle/Pedal Pos.Sensor A Circ Low Input`). **763 codes in this file are absent from `codes` entirely** (e.g. P1353, P1383, P1390, P1695, P1708–P1731 — the DSG/automatic-transmission P17xx block). Max length 83 chars. (src: https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/84f90a9a1dc28d8706187fdbf9144e60799e6afe/src/OBD_fault_code_description_EN.h)
- `src/fault_code_elaboration_EN.h`: the **KWP1281 fault-type ("elaboration") byte table, 83 entries 0x00–0x52**, indexed by `elaboration_code & 0x7F`; `getFaultElaboration()` sets `is_intermittent = elaboration_code & 0x80` and clears bit 7 before the lookup. The fault record layout is "DTC_H, DTC_L, DTC_ELABORATION" (3 bytes per fault, `getFaultCode()` = `buf[3i]<<8 | buf[3i+1]`, `getFaultElaborationCode()` = `buf[3i+2]`). Complete table (hex, decimal as VCDS prints it, text):

| byte | dec | text |
|---|---|---|
| 0x00 | 0 | - |
| 0x01 | 1 | Signal Shorted to Plus |
| 0x02 | 2 | Signal Shorted to Ground |
| 0x03 | 3 | No Signal |
| 0x04 | 4 | Mechanical Malfunction |
| 0x05 | 5 | Input Open |
| 0x06 | 6 | Signal too High |
| 0x07 | 7 | Signal too Low |
| 0x08 | 8 | Control Limit Surpassed |
| 0x09 | 9 | Adaptation Limit Surpassed |
| 0x0A | 10 | Adaptation Limit Not Reached |
| 0x0B | 11 | Control Limit Not Reached |
| 0x0C | 12 | Adaptation Limit (Mul) Exceeded |
| 0x0D | 13 | Adaptation Limit (Mul) Not Reached |
| 0x0E | 14 | Adaptation Limit (Add) Exceeded |
| 0x0F | 15 | Adaptation Limit (Add) Not Reached |
| 0x10 | 16 | Signal Outside Specifications |
| 0x11 | 17 | Control Difference |
| 0x12 | 18 | Upper Limit |
| 0x13 | 19 | Lower Limit |
| 0x14 | 20 | Malfunction in Basic Setting |
| 0x15 | 21 | Front Pressure Build-up Time too Long |
| 0x16 | 22 | Front Pressure Reducing Time too Long |
| 0x17 | 23 | Rear Pressure Build-up Time too Long |
| 0x18 | 24 | Rear Pressure Reducing Time too Long |
| 0x19 | 25 | Unknown Switch Condition |
| 0x1A | 26 | Output Open |
| 0x1B | 27 | Implausible Signal |
| 0x1C | 28 | Short to Plus |
| 0x1D | 29 | Short to Ground |
| 0x1E | 30 | Open or Short to Plus |
| 0x1F | 31 | Open or Short to Ground |
| 0x20 | 32 | Resistance Too High |
| 0x21 | 33 | Resistance Too Low |
| 0x22 | 34 | No Elaboration Available |
| 0x23 | 35 | - |
| 0x24 | 36 | Open Circuit |
| 0x25 | 37 | Faulty |
| 0x26 | 38 | Output won't Switch or Short to Plus |
| 0x27 | 39 | Output won't Switch or Short to Ground |
| 0x28 | 40 | Short to Another Output |
| 0x29 | 41 | Blocked or No Voltage |
| 0x2A | 42 | Speed Deviation too High |
| 0x2B | 43 | Closed |
| 0x2C | 44 | Short Circuit |
| 0x2D | 45 | Connector |
| 0x2E | 46 | Leaking |
| 0x2F | 47 | No Communications or Incorrectly Connected |
| 0x30 | 48 | Supply voltage |
| 0x31 | 49 | No Communications |
| 0x32 | 50 | Setting (Early) Not Reached |
| 0x33 | 51 | Setting (Late) Not Reached |
| 0x34 | 52 | Supply Voltage Too High |
| 0x35 | 53 | Supply Voltage Too Low |
| 0x36 | 54 | Incorrectly Equipped |
| 0x37 | 55 | Adaptation Not Successful |
| 0x38 | 56 | In Limp-Home Mode |
| 0x39 | 57 | Electric Circuit Failure |
| 0x3A | 58 | Can't Lock |
| 0x3B | 59 | Can't Unlock |
| 0x3C | 60 | Won't Safe |
| 0x3D | 61 | Won't De-Safe |
| 0x3E | 62 | No or Incorrect Adjustment |
| 0x3F | 63 | Temperature Shut-Down |
| 0x40 | 64 | Not Currently Testable |
| 0x41 | 65 | Unauthorized |
| 0x42 | 66 | Not Matched |
| 0x43 | 67 | Set-Point Not Reached |
| 0x44 | 68 | Cylinder 1 |
| 0x45 | 69 | Cylinder 2 |
| 0x46 | 70 | Cylinder 3 |
| 0x47 | 71 | Cylinder 4 |
| 0x48 | 72 | Cylinder 5 |
| 0x49 | 73 | Cylinder 6 |
| 0x4A | 74 | Cylinder 7 |
| 0x4B | 75 | Cylinder 8 |
| 0x4C | 76 | Terminal 30 missing |
| 0x4D | 77 | Internal Supply Voltage |
| 0x4E | 78 | Missing Messages |
| 0x4F | 79 | Please Check Fault Codes |
| 0x50 | 80 | Single-Wire Operation |
| 0x51 | 81 | Open |
| 0x52 | 82 | Activated |

  Cross-check with Ross-Tech sub-headings in `vag_fault_variants`: `Signal Outside Specifications` = 0x10, `Implausible Signal` = 0x1B, `Short to Plus` = 0x1C, `Short to Ground` = 0x1D, `Open Circuit` = 0x24, `No Communications` = 0x31, `Mechanical Malfunction` = 0x04, `Upper Limit`/`Lower Limit` = 0x12/0x13, `Supply Voltage Too Low` = 0x35 (VCDS prints e.g. `35-10` for code 0x35 with the intermittent flag → see OPEN QUESTION 3), `Intermittent` = bit 7. Ross-Tech wordings `Electrical Fault in Circuit` and `Upper Limit Exceeded` have no exact row (nearest `0x39 Electric Circuit Failure`, `0x12 Upper Limit`), so this library's strings are its own rendering, not VCDS's verbatim. (src: https://raw.githubusercontent.com/domnulvlad/KLineKWP1281Lib/84f90a9a1dc28d8706187fdbf9144e60799e6afe/src/fault_code_elaboration_EN.h ; …/src/KLineKWP1281Lib.cpp lines 574–583 and 1127–1160)

##### G. [NEW] UDS failure-type byte (FTB, third DTC byte on EDC17/UDS modules) — open-source tables, consistent subset

ISO 14229-1 Annex D / ISO 15031-6 were not fetched (paywalled). Two unrelated open-source tables were fetched: `cmarshall108/vinfast-diagnostics tools/dtc_helper.py` (41 entries) and `neomotive/neomotive …/uds-catalog.default.json` key `faultTypes` (83 entries). The category (high-nibble) semantics are additionally given by piembsystech.com, which attributes them to ISO 15031: 0x0 General Failure Information, 0x1 General Electrical Failures, 0x2 General Signal Failures, 0x3 FM/PWM Failures, 0x4 System Internal Failures, 0x5 System Programming Failures, 0x6 Algorithm-Based Failures, 0x7 Mechanical Failures, 0x8 Bus Signal/Message Failures, 0x9 Component Failures, 0xA–0xE ISO/SAE reserved, 0xF manufacturer/supplier specific. Ross-Tech pages independently show FTB values in headings: `C10E2 01 … Electrical Failure`, `C10E2 54 … Missing Calibration / Basic Setting`, `B1916 04 … Internal System Fault`, matching 0x01/0x54/0x04 below.

**Values on which both fetched tables agree** (31 rows; text as in neomotive):

| FTB | text |
|---|---|
| 0x00 | No Subtype Information |
| 0x01 | General Electrical Failure |
| 0x02 | General Signal Failure |
| 0x04 | System Internal Failure |
| 0x07 | Mechanical Failure |
| 0x11 | Circuit Short to Ground |
| 0x12 | Circuit Short to Battery |
| 0x13 | Circuit Open |
| 0x14 | Circuit Short to Ground or Open |
| 0x15 | Circuit Short to Battery or Open |
| 0x16 | Circuit Voltage Below Threshold |
| 0x17 | Circuit Voltage Above Threshold |
| 0x18 | Circuit Current Below Threshold |
| 0x19 | Circuit Current Above Threshold |
| 0x1A | Circuit Resistance Below Threshold |
| 0x1B | Circuit Resistance Above Threshold |
| 0x1C | Circuit Voltage Out of Range |
| 0x1D | Circuit Current Out of Range |
| 0x29 | Signal Invalid |
| 0x2F | Signal Erratic |
| 0x49 | Internal Electronic Failure |
| 0x4A | Incorrect Component Installed |
| 0x54 | Missing Calibration |
| 0x62 | Signal Compare Failure |
| 0x71 | Actuator Stuck |
| 0x81 | Invalid Serial Data Received |
| 0x83 | Value of Signal Protection Calculation Incorrect |
| 0x87 | Missing Message |
| 0x88 | Bus Off |
| 0x92 | Performance or Incorrect Operation |
| 0x96 | Component Internal Failure |

(src: https://raw.githubusercontent.com/cmarshall108/vinfast-diagnostics/02700fbb2b7a44489f29d5f66077037ef6a855a9/tools/dtc_helper.py ; https://raw.githubusercontent.com/neomotive/neomotive/c9dd52b8bede3d80de0e97213af8048a215e91ba/software/dotnet/Apps/Shared/Neomotive.Uds/Data/uds-catalog.default.json ; https://piembsystech.com/dtc-failure-type-byte-ftb-category-definition/ ; https://wiki.ross-tech.com/wiki/index.php/C10E2). The remaining values (single-source or differently worded) are in REPORTED.

#### Reported / unverified (confidence)

- **medium** — FTB values where the two fetched open-source tables differ in wording (both fetched; neither is the standard):

| FTB | vinfast | neomotive |
|---|---|---|
| 0x08 | Signal bus / message failure | Bus Signal / Message Failure |
| 0x09 | Component failure | Component Internal Failure |
| 0x21 | Signal amplitude below minimum | Signal Amplitude < Min |
| 0x22 | Signal amplitude above maximum | Signal Amplitude > Max |
| 0x38 | Frequency / pulse width out of range | Signal Frequency Incorrect |
| 0x55 | Not programmed | Not Configured |
| 0x82 | Alive / sequence counter incorrect or not updated | Alive Counter Incorrect |
| 0x86 | Signal invalid / signal protection calculation failure | Signal Invalid |

  and values present in only one of them (46 rows):

| FTB | text | source |
|---|---|---|
| 0x03 | Frequency modulation / pulse width modulation failure | vinfast |
| 0x05 | System Programming Failure | neomotive |
| 0x1E | Circuit Resistance Out of Range | neomotive |
| 0x1F | Circuit Intermittent | neomotive |
| 0x23 | Signal Stuck Low | neomotive |
| 0x24 | Signal Stuck High | neomotive |
| 0x25 | Signal Shape / Waveform Failure | neomotive |
| 0x26 | Signal Rate of Change Below Threshold | neomotive |
| 0x27 | Signal Rate of Change Above Threshold | neomotive |
| 0x28 | Signal Bias Level Out of Range | neomotive |
| 0x31 | No Signal | neomotive |
| 0x36 | Signal Frequency Too Low | neomotive |
| 0x37 | Signal Frequency Too High | neomotive |
| 0x41 | General Checksum Failure | neomotive |
| 0x42 | General Memory Failure | neomotive |
| 0x43 | Special Memory Failure | neomotive |
| 0x44 | Data Memory Failure | neomotive |
| 0x45 | Program Memory Failure | neomotive |
| 0x46 | Calibration Memory Failure | neomotive |
| 0x47 | Watchdog / Safety MCU Failure | neomotive |
| 0x48 | Supervision Software Failure | neomotive |
| 0x51 | Not Programmed | neomotive |
| 0x52 | Not Activated | neomotive |
| 0x53 | Deactivated | neomotive |
| 0x61 | Signal Calculation Failure | neomotive |
| 0x63 | Circuit Protection Timeout | neomotive |
| 0x64 | Signal Plausibility Failure | neomotive |
| 0x65 | Signal Has Too Few Transitions | neomotive |
| 0x66 | Signal Has Too Many Transitions | neomotive |
| 0x67 | Signal Incorrect Event | neomotive |
| 0x72 | Actuator Stuck Open | neomotive |
| 0x73 | Actuator Stuck Closed | neomotive |
| 0x74 | Actuator Slipping | neomotive |
| 0x75 | Emergency Position Not Reachable | neomotive |
| 0x76 | Wrong Mounting Position | neomotive |
| 0x77 | Commanded Position Not Reachable | neomotive |
| 0x78 | Alignment / Adjustment Incorrect | neomotive |
| 0x79 | Mechanical Linkage Failure | neomotive |
| 0x7A | Fluid Leak / Seal Failure | neomotive |
| 0x89 | Signal invalid / invalid serial data | vinfast |
| 0x91 | Parametric Parameter at Limit | neomotive |
| 0x93 | No Operation | neomotive |
| 0x94 | Unexpected Operation | neomotive |
| 0x95 | Incorrect Assembly | neomotive |
| 0x97 | Component Function Obstructed | neomotive |
| 0x98 | Component Overtemperature | neomotive |

  What would confirm them: ISO 14229-1:2013 Annex D.2 table, or a VCDS/ODIS scan of the TDI showing the printed fault-type text next to the raw third byte (OPEN QUESTION 3). The neomotive set (83 rows, 0x00–0x98) matches the verifier's recollection of Annex D (0x51 Not Programmed, 0x52 Not Activated, 0x53 Deactivated, 0x54 Missing Calibration, 0x55 Not Configured; 0x71 Actuator Stuck, 0x72 Actuator Stuck Open, 0x73 Actuator Stuck Closed) better than vinfast's `0x55 Not programmed`; treat neomotive as primary when they conflict.
- **medium** — Wal33D's hex-letter generic codes (P0Axx…, P2Axx…, U3xxx, B0xxx, C0xxx) match SAE J2012-DA (2016+). The README claims "generic SAE J2012"; wording looks authentic (`C066F Service/Park Brake Chamber Pressure Too Low`, `U3002 Vehicle Identification Number`) but 13 descriptions exceeded 90 chars and were trimmed. The 2002 edition fetched by the verifier contains none of these codes, so they cannot be checked against it. Confirm against the J2012-DA digital annex (paywalled).
- **medium** — python-OBD codes that post-date J2012:2002 (P0A00–P0A29, P2A00–P2A05, the P3400–P3497 block, U0236–U0431 and the P2xxx codes above P2795) carry the wording of a later J2012 edition (2007/2012). Not checkable against the fetched 2002 scan (those rows are absent from it). Confirm against SAE J2012:2007 or later.
- **medium** — Exact VCDS text for P173A/P173B/P173D is `Position Sensor 1/2/4 for Gear Selector: Implausible Signal` (6-digit 005946/005947/005949) by analogy with the verified P173C line; two secondary pages confirm the meaning ("Gear Position Sensor 1/2/4 Signal Implausible"). P173E/P173F are listed only in the forum-thread title; their text in the JSON ("Gear Selector Position Sensors: Implausible Signal") is a guess — tag stays `memory-unverified` for E/F. Confirm with a DQ200 VCDS scan or a Ross-Tech page (none exists; the §F file has no hex-letter codes).
- **medium** — The DQ250 (02E, R32 2008, KWP2000 over TP2.0) mechatronic reports KWP-era codes via P07xx/P17xx with 5-digit numbers (e.g. 17090/P0706 range sensor, 17105/P0721 output speed, P0730–P0736 gear ratio monitoring, P1750 power supply, P1757, P1850/P1855 data-bus). The **wording** for all of these is now in the §F OBD file (quoted above) and the Ross-Tech page `17114/P0730/001840 - Gear Ratio Monitoring: Incorrect Gear Ratio` was re-fetched; **which ones a DQ250 actually emits is not verified** (the Ross-Tech 02E page re-fetched by the verifier, `6-Speed Direct Shift Gearbox (DSG/02E)`, covers coding/basic settings only and lists no fault codes). Confirm with a live scan.
- **medium** — Haldex 4Motion (module 22, J492) on the Mk5 R32 reports only 5-digit factory codes. Confirmed wording exists for 01324 (J492), 00448 (Haldex clutch pump V181), 00287/00290 (wheel speed sensors), 01044, 00668, 01314 (§E/§F). A web search confirms 01324 and 00448 appear together on failed Haldex ECUs and that VCDS calls the module "AWD Unit 22", but every forum thread with a full R32 Auto-Scan (r32oc.com, vwvortex.com) is behind a paywall (HTTP 402) and ecutesting.com returned 403, so no Mk5-specific code list was fetched. Unverified which numbers the Gen-2 controller emits.
- **medium** — EDC17CP14 (2012 TDI) reports UDS 3-byte DTCs. Verified so far on this exact ECU family (forum 22128): P2002, P0401; official VW TSBs add P240F, P2452, P2453, P2454, P2456. Typical others from memory: P0402 EGR, P242F ash, P2463 soot, P0671–P0674 glow plugs, P0087/P0088 rail pressure, P0299 underboost, P0101 MAF, P046C EGR position. All generic ones are in `codes`; the manufacturer-specific EDC17 ones (P1xxx with hex letters) appear only if Ross-Tech has a page. Confirm with a live `ReadDTCInformation` (0x19 0x02 0xFF) dump.
- **medium** — The VCDS "- NNN -" field between the P-code and the fault text (`P2002 - 007 -`, `P0401 - 001 -`, `P173C - 000 -`) is the raw third DTC byte (FTB) printed in **decimal**; on KWP modules VCDS prints it as `XX-YY` (elaboration code, then `10` when intermittent / `00` when static). The decimal/hex question cannot be settled from the fetched examples (000, 001, 002, 007 are the same in both); Ross-Tech headings `C10E2 01`/`C10E2 54` print it in hex. Confirm with OPEN QUESTION 3. If decimal, `007` = FTB 0x07 "Mechanical Failure" category for P2002 and `001`/`002` = "General Electrical Failure"/"General Signal Failure" for P0401 — plausible but unproven.
- **low** — The Ross-Tech `vag_fault_variants` suffixes are the VCDS rendering of the KWP elaboration byte (§F table). The mapping given in §F is by text matching; VCDS may use different strings for the same byte (e.g. "Electrical Fault in Circuit"). Build the byte→VCDS-text table on the car (OPEN QUESTION 3).
- **low** — The Bentley typos (16395 P0020, 17721 P1319), the vag-hub typos (18853/18854) and the seven Ross-Tech title anomalies are errors in those sources, not alternative numbering schemes. (They are the only exceptions in ~1,350 checked pairs across three independent sources.)
- **low** — KLineKWP1281Lib's text tables were derived from VCDS-Lite / VAG-COM label files (the README credits blafusel.de and vwradio but does not say where the fault strings came from). Their license is therefore GPL-3 by the repository's `LICENSE.md` but the underlying strings may be Ross-Tech's. If vagtune ships them, keep the provenance tag and do not claim them as original.

- **Partial FTB (failure-type byte) table — individual rows now VERIFIED, remaining rows
  REPORTED.** Re-fetched https://autodtcs.com/what-is-a-failure-type-byte-ftb/ this session;
  these rows matched the page verbatim and may be treated as confirmed (source is a
  secondary site, so keep a "secondary-source" flag in code):
  `00 No additional information; 11 Short to ground; 12 Short to battery; 13 Open circuit;
  14 Short to ground or open; 15 Circuit open (also phrased "short to battery or open");
  16 Circuit voltage below threshold; 17 Circuit voltage above threshold;
  1C Circuit current below threshold; 1D Circuit current above threshold; 2F Signal erratic;
  62 Signal compare failure; 71 Actuator stuck low; 72 Actuator stuck high;
  87 Bus signal or message failure; 96 Component internal failure;
  9D Component or system over-temperature`.
  - **Correction carried forward:** the original task's label for `0x1C` ("voltage out of
    range") is WRONG — the source says `0x1C = circuit current below threshold`. HIGH
    confidence on the correction.
- **FTB high-nibble category scheme — PROMOTE toward verified.** Re-fetched
  https://piembsystech.com/dtc-failure-type-byte-ftb-category-definition/ this session; all
  sixteen category rows matched verbatim: `0x00 General Failure Information; 0x01 General
  Electrical; 0x02 General Signal; 0x03 FM/PWM; 0x04 System Internal; 0x05 System
  Programming; 0x06 Algorithm-Based (plausibility); 0x07 Mechanical; 0x08 Bus
  Signal/Message; 0x09 Component; 0x0A-0x0E ISO/SAE reserved; 0x0F Vehicle
  Manufacturer/System Supplier specific`. (Secondary source — flag as such — but internally
  consistent and matches the confirmed rows above.) Still-uncertain individual subtypes:
  `0x29` "signal invalid" (medium), `0x31` "no signal" (medium), `0x49` "internal electronic
  failure" (medium — category 4 fits), `0x64` "signal plausibility failure" (medium —
  category 6 fits), `0x88` "bus off / no communication" (medium — category 8 fits). Confirm
  every remaining subtype against SAE J2012-DA (Digital Annex) or an ODX/CDD DTC database.


### 7.10 Login (function 11 / Security Access 16), coding (07), adaptation (10), basic settings (04), output tests (03) — service mappings

Source sheets: `kwp_vag.md` §6, `uds_vag.md` §O, `ecus.md` F1. **Only the KWP capability query `31 B8 00 00` and bri3d's adaptation sequence are verified; every other owner-level write mapping is Reported.** The SA2 scripts quoted in §O are flashing material from an open-source tool, listed for recognition only — out of scope.

#### Verified (source)

##### 6. Owner-level functions — what fetched code actually sends

- **Capability query `31 B8 00 00`** (startRoutineByLocalIdentifier B8, routine 0x0000): the real PQ35 engine answered `71 B8 01 01 01 03 01 02 01 06 01 07 01 08 01 0D 01 18` (NEFM-9182, TP 2.0 length 0x12); VDS replays `71 B8 01 01 01 03 01 02 01 06 01 07 01 08 01 0D 01 18` for `31 B8`; DV's emulator answers `71 B8 01 06` and documents the 2-byte codes: "0000 - no function supported, 0101 - basic settings in KWP1281 mode, 0102 - output tests with fixed sequence in KWP1281 mode, 0104 - 20-bit coding possible, 0105 - Coding-II possible, 0106 - reading measuring blocks in KWP1281 mode, 0107 - output tests with selective (non-fixed) sequence, 0108 - developer functions possible, 010D - immobilizer Gen4 supported, 0118 - HEX-coded fault codes supported" and "Warning: this SID is used for output tests; if they are enabled … the routine number must also be checked … `supported_functions_response` must only be sent when the diagnostic interface requests to "start" the routine with number 0x0000". PY: "startRoutineByLocalIdentifier has something relating to measuring blocks with argument 0xb8". So the real engine above advertises 0101, 0103, 0102, 0106, 0107, 0108, 010D, 0118 (0103 is not in DV's list; see REPORTED). (src: http://nefariousmotorsports.com/forum/index.php?topic=9182.0;wap2 ; https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://raw.githubusercontent.com/domnulvlad/KWP1281-VWTP2.0_converter_ESP32/main/KWP1281-VWTP2.0_converter_ESP32/responses.h ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py)
- **Adaptation (10) sequence as implemented by B3** on a KWP2000 instrument cluster (`clearCayenneClusterServiceIndicator`, all via `31 <routine> <params>` and every reply checked only for `!= 0x7F`):
  1. `31 B8 01 03` — "Start Adaptation"
  2. `31 BA 01 03` — "Read"
  3. `31 B9 01 03 02` — "Select channel 2"
  4. `31 BA 01 03` — "Read"
  5. `31 B9 01 03 00 00` — "Test data 00 00"
  6. `31 BA 01 03` — "Read"
  7. `31 BB 01 03 00 00 00 00 04 50 10 34` — "Save data - 2 bytes are data, last 6 are derived from return of 0x1A 0x9B ident, which is static for this module so hardcoded"
  8. `31 BA 01 03` — "Read"
  9. `31 B8 01 03` — "I think we should actually be calling stopLocalRoutine here..."
  The 6 trailing bytes of the save are the WSC/importer/equipment block of the `5A 9B` record (offsets 20..25). (src: https://raw.githubusercontent.com/bri3d/kwp2000/master/src/main/java/com/brianledbetter/kwplogger/KWP2000/DiagnosticSession.java)
- Routine services in ISO: `31 <routineLocalId> [params]` → `71 <routineLocalId> [results]`, `32` stop → `72`, `33` requestRoutineResults → `73` (PQF uses `31 C4`/`31 C5` + `33 C5` for flash routines, out of scope here). (src: http://www.internetsomething.com/kwp/KWP2000%20ISO%2014230-3.pdf Table 4.3 ; https://raw.githubusercontent.com/I-CAN-hack/pq-flasher/master/kwp2000.py)
- **Coding read**: short coding = bytes 18-19 of `5A 9B` (type byte 0x03); long coding read with `1A 9A` (VDS/PC; VCDS: "In modules that use Long Coding you will need to click on the [Coding - 07] button to see the current Coding value"). PY's `setLongCode` is `NotImplementedError("Need VCDS Trace to figure out KWP commands")` — i.e. no fetched open-source tool writes coding over KWP2000/TP 2.0. (src: https://raw.githubusercontent.com/michaeldove/vag-diag-sim/master/vagvehicle.py ; https://www.ross-tech.com/vcds/tour/open_screen.php ; https://raw.githubusercontent.com/baconwaifu/PyVCDS/master/vw.py)
- **VCDS semantics** (behavioural, from Ross-Tech): Adaptation = 255 channels, [Read] shows the stored value, [Test] "will tell the controller to temporarily use the new value", [Save] stores it; "Performing a [Save] to Channel 00 resets all adaptation values to their original factory defaults"; "Some Engine and Immobilizer controllers will require a valid Login before permitting you to [Test] or [Save]"; "Values put in with [Test] but not Saved will persist until controller is powered-down"; saving may be refused when WSC/Importer/Equipment are all zero, VCDS then offers 12345/123/12345. Recode: "Some Modules require a valid Login before you can re-code them"; WSC is sent with the coding and "The Importer Number is only relevant for recoding controllers that use KWP-2000"; long coding "up to 255 bytes". Login (function 11) = a 5-digit code "must be used on some (but not all) Control Modules before you can Recode or change Adaptation values. On others, it "enables" certain features like cruise control"; a disconnect after a login requires exiting and logging in again. Security Access (function 16) is "KWP-2000 only" and is VCDS's name for the same unlock on KWP2000/CAN/UDS modules. Basic settings: in "KWP-2000/CAN/UDS, there may be an [ON/OFF/Next] button that allows you to initiate and exit Basic Settings while still being able to see the values in the measuring groups"; "Multiple Groups are not permitted in Basic Settings". Output tests: "Most Control Modules will permit the Output Test Sequence to be run only one time per session"; "The ECU identifies which output it is currently testing by sending a fault-code number"; selective output tests need label-file data, "There is no way to efficiently query a control module to find out which outputs are supported"; "only available when the Engine is not running". (src: https://www.ross-tech.com/vcds/tour/adaptation_screen.php ; https://www.ross-tech.com/vcds/tour/recode_screen.php ; https://www.ross-tech.com/vcds/tour/login_screen.php ; https://www.ross-tech.com/vcds/tour/securityaccess.php ; https://www.ross-tech.com/vcds/tour/b-settings.php ; https://www.ross-tech.com/vcds/tour/out_test.php ; https://wiki.ross-tech.com/wiki/index.php/Functions)
- Security access via standard `27 01`/`27 02` is not how VCDS "Login" works on at least one VAG KWP2000 module: a Bosch 5.7 ABS answered `7F 27 11` to every `27 xx` (and VCDS has a working Security Access function for it); reply from an experienced member: "SA is not the only way to gain authorization, you have also $31, that can do whatever the implementation likes" and "In case of "PIN" then that's added to the seed unsigned and that's the key" (for modules that do implement 0x27). (src: http://nefariousmotorsports.com/forum/index.php?topic=20104.0;wap2)

##### O. SecurityAccess 0x27 — scripts VERIFIED, level DEMOTED

- Subfunction rule: odd subfunction = requestSeed, even = sendKey; for level L,
  requestSeed = `27 L` (odd) and sendKey = `27 (L+1)` (even). CONFIRMED (src:
  https://raw.githubusercontent.com/pylessard/python-udsoncan/master/udsoncan/services/SecurityAccess.py
  — `normalize_level`: RequestSeed forces odd, SendKey forces even; level range 0..0x7F).
  Request seed: `27 <odd> [dataRecord]` → `67 <odd> <seed...>`; send key: `27 <even>
  <key...>` → `67 <even>`. A seed of all-zero conventionally means "already unlocked"
  (convention, not stated in the fetched udsoncan source).
- **SA2 bytecode scripts per module — VERIFIED (hex strings present in VW_Flash source this
  session):**
  - Simos18.1: `6802814A10680493080820094A05872212195482499307122011824A058703112010824A0181494C`
    (src: lib/modules/simos18.py `sa2_script_s18`)
  - DQ250-MQB DSG: `68028149680593A55A55AA4A0587810595268249845AA5AA558703F780384C`
    (src: lib/modules/dq250mqb.py `dsg_sa2_script`)
  - Haldex Gen5: `6805814A05870A221289494C` (src: lib/modules/haldex4motion.py `haldex_sa2_script`)
  The SA2 VM runs the script against the seed to produce the key; vagtune implements this VM
  in `vag/sa2.py` (opcode semantics recorded as verified in CLAUDE.md).
- **DEMOTED: the specific requestSeed level 0x11 / sendKey 0x12.** This value does **not**
  appear anywhere in the VW_Flash files fetched this session (lib/constants.py,
  lib/simos_flash_utils.py, lib/modules/*, docs/docs.md, connection_setup.py — grep for
  `0x11` hits only an unrelated CRC-table entry). It is recorded in CLAUDE.md as a project
  fact, and the SA2 scripts above are what the seed/key uses, but the level byte itself is
  not sourced here → moved to REPORTED. (Notably, the VW_Flash **fake testdata uses level
  0x03/0x04**: `27 03`→`67 03 12 23 34 45` seed, `27 04 12 23 A1 88`→`67 04` key — that is
  simulated data, not proof of the real flash level, but it shows the fake exercises 27
  03/04. See OPEN QUESTIONS.)
- CAN IDs per module — CONFIRMED verbatim (src: lib/constants.py + lib/modules/*; note the
  VW_Flash field names are `rxid` = ECU response id, `txid` = tester request id):
  - Engine: `ControlModuleIdentifier(0x7E8, 0x7E0)` → tester sends 0x7E0, ECU answers 0x7E8.
  - DSG DQ250: `ControlModuleIdentifier(0x7E9, 0x7E1)` → 0x7E1 / 0x7E9.
  - Haldex: `ControlModuleIdentifier(0x779, 0x70F)` → 0x70F / 0x779.

- VCDS function numbers (the "[xx]" the wiki uses): `01 Control Unit Info, 02 Read Fault Codes, 03 Output Tests, 04 Basic Settings, 05 Clear Fault Codes, 07 Code Module, 08 Measuring Blocks, 10 Adaptation, 11 Login, 15 View Readiness` (src: RT-TDI). "Login Screen — Corresponds to VAG 1551/1552 function 11. The Login Function must be used on some (but not all) Control Modules before you can Recode or change Adaptation values. On others, it 'enables' certain features like cruise control" (src: RT-LOGIN). VCDS shows "Security Access - 16" for the same thing on newer modules (src: RT-DPF, RT-CRTDI).

#### Reported / unverified (confidence)

- **Adaptation/basic-settings/output-test/login all ride on `31 B8/B9/BA/BB <func hi> <func lo> …`** with the 2-byte function code from the capability list: 0101 basic settings, 0102 output tests (fixed sequence), **0103 adaptation** (absent from DV's list but advertised by the real engine and used by B3 as `01 03`), 0104 coding (20-bit), 0105 Coding-II (= VCDS Login), 0107 selective output tests. Model: `31 B8 01 xx` = start function xx, `31 B9 01 xx <args>` = select/test, `31 BA 01 xx` = read current value, `31 BB 01 xx <value> <6-byte WSC block>` = save, `32 B8 01 xx` = stop. Evidence: B3's adaptation sequence (verified above), DV's routine-number warning, PY's note. Confidence **medium** for adaptation (one real implementation), **low** for the exact byte forms of basic settings (0101), output tests (0102/0107), coding (0104) and login (0105). Confirm: sniff VCDS doing each function on the R32 (ABS output test, engine adaptation channel read, basic settings group 060, login 11463-style code) and compare with the model.
- **Adaptation read reply layout**: B3's "Read" (`31 BA 01 03`) returns a positive `71 BA …` whose payload presumably holds the channel number and the 16-bit value (VCDS shows a 5-digit value 0..65535 per channel, plus up to four decoded measuring fields); B3 discards it. Confidence **low**. Confirm on car: decode the bytes after `71 BA`.
- **Basic settings via measuring-block reads**: on KWP2000 modules VCDS reads the same `21 <group>` while a basic setting is active (the tour says the values stay visible and there is an ON/OFF button). Expected sequence: `31 B8 01 01` (start basic settings) → `21 <group>` polls → `32 B8 01 01` (stop). Confidence **low**.
- **Output tests**: `31 B8 01 02` starts the fixed sequence and each subsequent `31 B9 01 02` (or a re-read) advances to the next actuator, the reply naming the actuator by a 16-bit fault-code number (VCDS: "The ECU identifies which output it is currently testing by sending a fault-code number"); selective tests `31 B8 01 07` + the actuator's code. Confidence **low**.
- **Login (VCDS function 11 / "Coding-II")**: the 5-digit code is sent as part of the 0105 routine (`31 B8 01 05` then `31 B9 01 05 <code16> …`), **not** via `27 xx` on most VAG KWP2000 modules (the Bosch ABS evidence above). Some modules do implement `27 01/02` with the PIN "added to the seed unsigned" as the key (NEFM-20104). Confidence **low** for the byte layout, **medium** that it is a 0x31-based routine rather than 0x27. Confirm: sniff a VCDS login on the R32 engine (code 11463 enables cruise control on many ME7 ECUs per Ross-Tech's 1.8T page; check the R32's own code in the repair manual before sending anything).
- **Coding write**: with the model above, short coding = `31 BB 01 04 <coding16> <6-byte WSC block>`; long coding write would be a `3B 9A …` (writeDataByLocalIdentifier of the 9A record) or a 0104 routine variant. No fetched code does either. Confidence **low**. Do not implement without a trace.

- **SecurityAccess requestSeed level 0x11 / sendKey 0x12 for flashing** — medium. Recorded
  in CLAUDE.md as the SIMOS/MED17 calibration level, and the SA2 scripts (§O) are verified,
  but the level byte 0x11/0x12 is not present in any VW_Flash file fetched this session, and
  the fake testdata uses 0x03/0x04. Confirm with a CAN trace of a real `27 11`/`27 12`
  exchange, or by reading the VW_Flash client/connection code that issues the seed request.
- **SecurityAccess level + key algorithm for coding/adaptation** — medium/low. VW_Flash fake
  testdata uses `27 03`/`27 04` (seed/key level 3/4) and secondary sources (mk4-wiki,
  nefariousmotorsports) describe `27 03`/`27 04` for coding, distinct from the flash SA2
  unlock. Do NOT assume `key = seed + 0x00011170` (low confidence, seed-length-dependent) or
  that the key equals the 5-digit login as a u32. The mk4-wiki sid_27 page re-fetched this
  session describes only the generic `27 01` seed request, **not** the SA2 11/12 scheme — so
  it does not support that claim. Needs a trace.
- **VCDS 5-digit Login/Security-Access codes** — representative values VERIFIED against
  vag-coding.net this session (src:
  https://www.vag-coding.net/tutorials-information/vcds-secure-access-code-list/): `[01]
  Engine = 27971` (and 79153/12233 for injector adaptation), `[02] Auto Trans`, `[03] ABS
  Brakes = 11966`, Central Electronics `31347`, "auto-Hold" `20103`. The page also confirms a
  warning appears "after too many incorrect code attempts". **The specific "3 attempts → ~20
  min lockout" figure was NOT on the page** — demote that number to low confidence. Whether
  the 5-digit login on a UDS module is the KWP-era service (0x2B) vs the ODX-defined UDS
  seed/key remains unconfirmed; range is 00000-65535.

R-D2. Engine **Login** for adaptation on ME7 (`[11]`): memory says `12233` is the generic Bosch adaptation login on many ME7 gasoline ECUs; low. Confirm: VCDS balloon on `[11-Login]`.

R-F1. DQ250 **output tests** (`[03]`) on the 02E: label-driven sequential actuator test (solenoids N88-N92, N215/N216, N217/N218, N233/N371 click test) requiring engine running; content unverified (VTX-SOL only says "requires car running"). Low. Confirm: Q13.


---

## 8. Per-car module maps (real VCDS Auto-Scans)

Source sheets: `addresses.md` §F/§G/§H (scans A–F re-fetched and re-read row by row) and `ecus.md` §A. The protocol
column rule: a module block that prints `ASAM Dataset:`/`ROD:` lines is UDS; one that prints only `Labels:` with no
ASAM/ROD line is KWP2000 over TP 2.0 (Ross-Tech: UDS modules "do not support traditional Measuring Blocks or Adaptation
channel numbers"). The per-module protocol tables for the two cars are in the Reported list (inference from scans + memory).

### Verified (source)

#### F. 2008 VW R32 Mk5 (US) — module map from a real Auto-Scan

Scan A: VIN `WVWKC71K18W108211`, `Chassis Type: 1K (1K0)`, VCDS 14.10.2.0 (x64) / data 20150311, mileage 179010 km. (src: https://forums.ross-tech.com/index.php?threads/3627/ — re-fetched; every row below re-read). VCDS 14.10 prints ASAM/ROD lines for UDS modules (it does so in scan D below, same VCDS version), and **no module in this R32 scan printed an ASAM/ROD line** → every module below is KWP2000 over TP 2.0 (or diagnosed through its parent), not UDS.

| Addr | VCDS name | Part No SW / HW | Component string | Labels file | Coding |
|---|---|---|---|---|---|
| 01 | Engine | 022 906 032 KR / 022 906 032 GP | `R32-DQ-LEV2     G   1098` | 022-906-032-BDB.lbl | 0000178 |
| 02 | Auto Trans | 02E 300 011 CC / 02E 927 770 AD | `GSG DSG         082 1405` | 02E-927-770.lbl | 0000020 |
| 03 | ABS Brakes | 1K0 907 379 AB / same | `ESP 4MOTION MK60    0102` | 1K0-907-379-MK60-A.lbl | 0021128 |
| 04 | Steering Angle | (status "OK" from gateway list; no block scanned — G85 is a sub-node of 03) | | | |
| 08 | Auto HVAC | 1K0 907 044 BS / same | `ClimatronicPQ35 120 1111` | 1K0-907-044.lbl | |
| 09 | Cent. Elect. | 3C0 937 049 AJ / same | `Bordnetz-SG     H54 2202` | 3C0-937-049-30-H.lbl | 668F8F214004150047140000001400000008730B5C000100000000000000 (30 bytes); subsystems: wiper 1K1 955 119 E (`Wischer 050102 021 0501`, 1KX-955-119.CLB), rain/light sensor 1K0 955 559 AF (`RLS 140907 046 0204`) |
| 0F | Digital Radio | 8E0 035 593 H / same | `SDAR SIRIUS     H06 0080` | 8E0-035-593-SIR.lbl | |
| 15 | Airbags | 1K0 909 605 AB / same | `6T AIRBAG VW8R  034 8000` | 1K0-909-605.lbl | 0013908; subsystem seat-weight sensor 1K0 959 339 G `BF-Gewichtsens. 007 0007` + 6 serial-number-only satellites |
| 16 | Steering wheel | 1K0 953 549 AQ / same | `J0527           036 0070` | 1K0-953-549-MY8.lbl | 0012122; subsystem `E0221 002 0010` |
| 17 | Instruments | 1K6 920 974 D / same | `KOMBIINSTRUMENT VDD 1216` | 1K0-920-xxx-17.lbl | 0007203 |
| 19 | CAN Gateway | 1K0 907 530 L / HW 1K0 907 951 | `J533  Gateway   H07 0052` | 1K0-907-530-V3.clb | ED831F075003020000 |
| 22 | AWD | (installed per gateway; "Cannot be reached" / status `1100` in this scan — the car's fault) | | | |
| 25 | Immobilizer | 1K6 920 974 D / same (= the cluster) | `IMMO            VDD 1216` | 1K0-920-xxx-25.clb | |
| 37 | Navigation | 1K0 919 887 G | `Navigation     0050` (MFD2) | 1K0-919-887-MFD2.lbl | 0000101 |
| 42 | Door Elect, Driver | 1K0 959 701 M / same | `Tuer-SG         006 120A` | 1K0-959-701-MIN3.lbl | 0001077 |
| 44 | Steering Assist | 1K1 909 144 M | `EPS_ZFLS Kl.141 H08 1901` | 1Kx-909-14x-44.clb | |
| 46 | Central Conv. | 1K0 959 433 CT / same | `KSG PQ35 RDK 052 0221` | 1K0-959-433-MAX.clb | 139006885103281B0904058FB0080A04889C00; subsystems `Sounder n.mounted`, `NGS n.mounted`, `IRUE n.mounted` |
| 47 | Sound System | 1K6 035 456 B / same | `08K Audioverst.     0006` | 3C0-035-456.lbl | |
| 52 | Door Elect, Pass. | 1K0 959 702 M / same | `Tuer-SG         006 120A` | 1K0-959-702-MIN3.lbl | 0001076 |
| 55 | Headlight Range | 1T0 907 357 | `Dynamische LWR      0003` | 1T0-907-357.lbl | 0000004 |
| 56 | Radio | 1K0 035 095 H | `Radio        0050` | 1K0-035-095.lbl | 0010046 |
| 65 | Tire Pressure | 1K0 959 433 CT / same (= the comfort module; "RDK") | `RDK              0450`, Revision 00052000 | 3C0-959-433-65.lbl | 0100101 |

- Observations from scan A: the immobilizer (25) and cluster (17) are the same ECU (identical part number and version string); TPMS (65) and comfort (46) are the same ECU (KSG "RDK" = Reifendruckkontrolle); 04 is not scanned as a module; 62/72 (rear doors) are absent (US R32 is a 2-door) and correspondingly bits 5/6 of coding byte 2 are 0. The gateway status list printed `Malfunction 0010` for 03, 09, 0F, 17, 19 and `Cannot be reached 1100` for 22 — so the status word is a 4-digit code (`0000` OK, `0010` fault stored, `1100` unreachable) worth decoding from the `1A 9F` reply (OPEN Q.3).

#### G. 2012 VW Golf TDI Mk6 (US) and sibling CJAA/EDC17 cars — module maps from real Auto-Scans

Scan B: thread titled "vcds 2012 Golf issues", VIN `WVWNM7AJ2CW126467` (AJ = Golf Mk6, C = MY2012, W = Wolfsburg), VCDS Release 11.11.0 (x64) / data 20111111, VCDS printed `Chassis Type: 7N0` (VCDS keys the chassis string off the 7N0 gateway), `Scan: 01 03 08 09 15 16 17 19 1C 25 2E 42 44 46 52 56 62 72 77` (no 02 → manual gearbox). VCDS 11.11 prints ASAM/ROD for UDS modules (it did for 08, 15, 16, 17, 25, 77 in this very scan). (src: https://forums.tdiclub.com/showthread.php?t=336315 — re-fetched; every row re-read)

| Addr | VCDS name | Part No SW / HW | Component | Labels | ASAM dataset / ROD (⇒ UDS) |
|---|---|---|---|---|---|
| 01 | Engine (CJA) | 03L 906 019 EE / 03L 907 309 AA | `R4 2,0L EDC G000SG  1181`, Revision 12H14---, coding 0050072 | 03L-906-022-CBE.clb | none printed ⇒ KWP (TP 2.0) — now also confirmed by seishuku's 2013 Jetta (§D) |
| 03 | ABS Brakes (J104) | 1K0 907 379 BJ / same | `ESP MK60EC1   H31 0121`, Revision 00H31001, coding 114B400C49240000880F02EA92200042B70000 | 1K0-907-379-60EC1F.clb | none ⇒ KWP |
| 08 | Auto HVAC (J301) | 7N0 907 426 AN / same | `AC Manuell    H19 0304`, coding 0000001002 | None | EV_ACManueBHBVW36X A01010 / EV_ACManueBHBVW36X_VW36.rod ⇒ UDS |
| 09 | Cent. Elect. (J519) | 1K0 937 086 P / same | `BCM PQ35  M   110 0651`, Revision 00110 AC, 30-byte coding 6F180A1A90272AC4008800C17000854448010386534D8560648020200040; subsystem wiper 5K1 955 119 `Wischer 14091 26 0512` coding 009795 | 1K0-937-08x-09.clb | none ⇒ KWP |
| 15 | Airbags (J234) | 5K0 959 655 H / same | `AirbagVW10G   013 0724`, coding 00003131; satellites 5K0 959 339 / 5K0 959 354 | 5K0-959-655.clb | EV_AirbaVW10SMEVW360 A01014 / ..._VW36.rod ⇒ UDS |
| 16 | Steering wheel (J527) | 5K0 953 507 BC / 5K0 953 549 E | `Lenks.Modul   008 0080`, coding 108A140000; sub 3C8 959 537 D `E221__MFL-TK6 H06 0022` | 5K0-953-569.clb | EV_SMLSNGKUDS A05001 / EV_SMLSNGKUDS_VW36.rod ⇒ UDS |
| 17 | Instruments (J285) | 5K0 920 972 C / same | `KOMBI         H03 0607`, coding 270F01 | 5K0-920-xxx-17.clb | EV_Kombi_UDS_VDD_RM09 A04114 / ..._VW36.rod ⇒ UDS |
| 19 | CAN Gateway (J533) | 7N0 907 530 H / HW 1K0 907 951 | `J533  Gateway H42 1620`, Revision H42, coding 350002 | 7N0-907-530-V2.clb | none ⇒ KWP (see OPEN Q.4) |
| 1C | Position Sensing | 5N0 919 879 / same | `Kompass         001 0001`, coding 0000002 | 1Kx-919-xxx-1C.lbl | none ⇒ KWP |
| 25 | Immobilizer (J334) | 5K0 953 234 / same | `IMMO          H03 0607`, coding 000000 | 5K0-920-xxx-25.clb | EV_Immo_UDS_VDD_RM09 A03009 / ..._VW36.rod ⇒ UDS (lives in the cluster: same `H03 0607` version) |
| 2E | Media Player 3 (J650) | 5N0 035 342 E / same | `SG EXT.PLAYER H13 0240`, coding 010000 | 5N0-035-342.lbl | none ⇒ KWP |
| 42 | Door Elect, Driver | 5K0 959 701 H / same | `Tuer-SG         009 2105`, coding 0001204 | None | none ⇒ KWP |
| 44 | Steering Assist | 1K0 909 144 M | `EPS_ZFLS Kl. 70     3201`, Revision 00H20000 | 1Kx-909-14x-44.clb | none ⇒ KWP (this is the ECU family pq-flasher talks to at TP2.0 0x09) |
| 46 | Central Conv. | (in scan list; no block printed — merged into 09 per Ross-Tech) | | | |
| 52 | Door Elect, Pass. | 5K0 959 702 H / same | `Tuer-SG         009 2105`, coding 0001204 | None | none ⇒ KWP |
| 56 | Radio (J503) | 1K0 035 180 AE / same | `Radio Prem-8  H02 0016`, coding 01000400040005 | 5M0-035-1xx-56.clb | none ⇒ KWP |
| 62 | Door, Rear Left | 5K0 959 703 D / same | `Tuer-SG         007 2101`, coding 0001168 | 1K0-959-703-GEN3.lbl | none ⇒ KWP |
| 72 | Door, Rear Right | 5K0 959 704 D / same | `Tuer-SG         007 2101`, coding 0001168 | 1K0-959-704-GEN3.lbl | none ⇒ KWP |
| 77 | Telephone (J412) | 5K0 035 730 E / same | `TELEFON       H09 2902`, coding 0A10040000010100 | 7P6-035-730.clb | EV_UHVNA A01719 / EV_UHVNA_VW36.rod ⇒ UDS |

Scan C: 2010 Jetta TDI, VIN `3VWPL7AJ2AM609950`, `Chassis Type: 1K0`, VCDS Release 11.11.6 (x64), `Scan: 01 02 03 08 09 15 16 17 19 1C 25 42 44 46 52 56 62 65 72 77`. Same CJAA EDC17 family: 01 `Engine (CJA)` SW 03L 906 019 CM / HW **03L 906 022 TS**, `R4 2,0L EDC G000AG  7967`, coding 0050078, labels 03L-906-022-CBE.clb, **no ASAM/ROD**; 02 `Auto Trans` 02E 300 052 / 02E 927 770 AJ `GSG DSG AG6     440 1920` coding 0000020, labels 02E-300-0xx.lbl, no ASAM (⇒ DQ250 is KWP); 03 1K0 907 379 AP `ESP MK60EC1 H45 0107` coding 114B600C49220003881406E992190042B100, no ASAM; 08 3C8 907 336 N `Climatic H13 0203` with EV_Climatic A01001 / EV_Climatic_VW36.rod (UDS); 09 5K0 937 085 C `BCM PQ35 B++ 008 0019`, no ASAM; 15 5K0 959 655 B `AirbagVW10G 019 0706` EV_AirbaVW10SMEVW360 A01012 (UDS); 16 1K0 953 549 CD `J0527 055 0111` (1K0-953-549-MY9.lbl, no ASAM ⇒ KWP — note the Mk5-style steering column module here, unlike scan B's 5K0 953 549 E which is UDS); 17 5K0 920 970 L `KOMBI H08 0021` EV_KombiUDSMM9RM10 A04010 (UDS); 19 **1K0 907 530 AA** `J533 Gateway H07 0081`, 1K0-907-530-V4.clb, coding `ED807F07001602002002` (a 2010 car still has the 1K0 gateway, with a 10-byte coding — §E cross-check 3); 1C 5N0 919 879 Kompass; 25 5K0 920 970 L IMMO EV_ImmoUDSMM9RM10 (UDS); 42/52 1K0 959 701 AC / 702 AC (HW 1K0 959 793 N / 792 N) `J386 TUER-SG FT 1525` / `J387 TUER-SG BT 1525` (MIN3 labels, KWP); 44 1K0 909 144 H `EPS_ZFLS Kl. 70 2901`; 56 1K0 035 180 AC `Radio Prem-8 H10 0034`; 62 1K0 959 703 AH (HW 1K0 959 795 T) `J388 TUER-SG HL 1401`; **65 Tire Pressure (J502) = 5K0 937 085 C `RDK 008 0817`, coding 018705, i.e. the BCM** (labels 1K0-937-08x-65.clb); 72 1K0 959 704 AH (HW 1K0 959 794 T); 77 Telephone (J738) 1K8 035 730 C `Telefon H08 6600`, no ASAM ⇒ KWP (unlike scan B's 5K0 035 730 E which is UDS). (src: https://forums.tdiclub.com/showthread.php?p=4298172 — re-fetched)

Scan D: 2012 Passat NMS TDI (US), VIN `1VWCN7A36CC012590`, VCDS 14.10.2.0, `Chassis Type: A3 (7N0)`, `Scan: 01 02 03 05 08 09 15 16 17 19 25 2B 2E 36 37 42 44 46 47 4F`. Useful as the "late PQ35/PQ46 with 7N0 gateway" reference: 01 `Engine (J623-CKRA)` 03L 906 012 BP / 03L 907 309 S, `R4 2,0L EDC H21 2158`, coding 001D0012042400008000, labels 03L-906-012-CKR.clb, **ASAM EV_ECM20TDI01103L906012BP 004004 / ROD EV_ECM20TDI01103L906012.rod ⇒ this EDC17 variant IS UDS** (and its DTCs print as `18643 - ROD - Unknown Error Code`, i.e. VCDS needed the ROD); 02 02E 300 054 C / 02E 927 770 AL `GSG DSG AG6 511 2806` 02E-927-770.lbl, no ASAM ⇒ KWP; 03 1K0 907 379 BJ MK60EC1 `H31 0121`, no ASAM; 05 5K0 959 434 B / A `VWKESSYPQ35GP 085 0902` EV_KESSYPQ35G A02014 / EV_KESSYPQ35G_AU21.rod (UDS); 08 561 907 044 D `Climatronic H01 0102` EV_ACClimaBHBVW411 (UDS); 09 5K0 937 087 Q `BCM PQ35 H+ 111 0147`, no ASAM; 15 5C0 959 655 AirbagVW10G EV_AirbaVW10SMEVW360 A01024 (UDS); 16 1K5 953 521 AR / 5K0 953 569 E `LENKS.MODUL 014 0140` EV_SMLSNGVOLWSXS (UDS); 17 561 920 970 C `KOMBI H07 0507` EV_Kombi_UDS_VDD_RM09 (UDS); 19 **7N0 907 530 K / 1K0 907 951 `J533 Gateway H40 1620`, coding 461000, no ASAM**; 25 5K0 953 234 `IMMO H07 0507` EV_Immo_UDS_VDD_RM09 (UDS); 2B 5K0 905 861 A `ELV-PQ35 H20 0230` EV_ELVMarquMPVW36X (UDS); 2E 5N0 035 342 E; 36 561 959 760 `MEM-FS H04 0181`, no ASAM; 37 Navigation (J0506) 3C8 035 684 E / 3C0 035 684 E `RNS-MID H59 3690` labels 1T0-035-680.clb; 42 561 959 701 A / 3C0 959 793 C `TUER-SG FT 002 0525` EV_TSGFPQ25BRFVW46X (UDS door module, GEN4, with rear door 561 959 811 `J388__TSG_HL` as its subsystem — the "rear doors as slaves of 42/52" case); 44 1K0 909 144 M `EPS_ZFLS Kl. 290 3201`, no ASAM; 47 3T0 035 456 B `KonzernAmp10K H06 0362` EV_AudioVerst10KanalSTT3 (UDS); 4F 7N0 907 532 / 1K0 907 951 `EZE_2 H40 1620`, coding 01030108, no ASAM; 52 561 959 702 A EV_TSGBPQ25BRFVW46X (UDS); **56 `Radio (J0506)` = the same 3C8 035 684 E RNS-MID as 37** (same part/coding/VCID); 77 7P6 035 730 F `TELEFON H09 2902` EV_UHVNA (UDS). (src: https://forums.tdiclub.com/showthread.php?t=440503 — re-fetched)

Scan F **[added in verification]**: Mk5 Golf 2.0 TDI 4Motion (BMM, PD engine), VCDS Release 12.12.0 (x64), `Chassis Type: 1K (1K0)`, `Scan: 01 03 08 09 15 16 17 19 22 25 42 44 46 52 55 56 62 72 76 7D`. Relevant blocks: 01 03G 906 021 JG / 03G 906 021 AB `R4 2,0L EDC G000SG 9392` (03G-906-021-BMM.clb); 03 1K0 907 379 AB `ESP 4MOTION MK60 0102` (same part/version as the R32's ABS); 09 3C0 937 049 E `Bordnetz-SG H37 1002` (3C0-937-049-23-H.lbl); 17/25 1K0 920 863 B `KOMBIINSTRUMENT VN4 8112` / `IMMO VN4 8112`; 19 1K0 907 530 H / 1K0 907 951 `J533__Gateway H12 0150` coding FD3F0F4007000002 (1K0-907-530-V2.clb); **22 AWD: labels `1K0-907-554.lbl`, Part No `1K0 907 554 F`, Component `Haldex 4Motion 0115`, Coding `0000001`**; 42/52 1K0 959 701 N / 702 N (MAX3); 44 1K1 909 144 L `EPS_ZFLS Kl.070 H07 1806`; 46 1K0 959 433 BT `KSG PQ35 G2 020 0203`; 55 Xenon Range 1T0 907 357 `Dynamische LWR 0003`; 56 1K0 035 186 R `Radio BVX 020 0032`; 62 1K0 959 703 K, 72 5K0 959 704 (GEN3 labels); 76 Park Assist 1K0 919 283 A `22 Einparkhilfe 0101`; 7D Aux. Heat 1K0 963 235 E `PTC-Element 0404`. No ASAM/ROD lines anywhere ⇒ all KWP (TP 2.0). (src: https://forums.tdiclub.com/index.php?threads/vw-golf-mkv-2-0tdi-4motion-rear-door-module-errors.406046/)

- Pattern across scans B/C/D/F (all fetched): on 2010-2012 PQ35 cars the UDS modules are the ones with **5K0/7N0/561-era "VW36X/VDD_RM09/VW10" datasets**: cluster+immo (5K0 920 97x), airbag VW10 (5K0 959 655), HVAC (Climatic/Climatronic/AC Manuell), steering-column module 5K0 953 5xx, telephone 5K0/7P6 035 730, KESSY, ELV, amplifier, GEN4 door modules; while engine CJAA (03L 906 022), DSG 02E, ABS MK60EC1 (1K0 907 379), BCM (1K0/5K0 937 08x), EPS (1K0 909 144), MIN3/MAX3/GEN3 door modules, compass 1C, media player 2E, radio 1K0 035 180, 1K0/7N0 gateways, 4F, 1K8 035 730 telephone and every module on the Mk5 cars print no ASAM/ROD ⇒ KWP2000 over TP 2.0.

#### H. Haldex / AWD address 22 (what is verified)

- Address 22 exists in the Mk5 gateway installation list (layouts 1-3) and was set on the R32 (`Byte1 bit1 [22] All Wheel Drive` = 1 in `ED83...`) and on the 4Motion TDI (`Byte0 bit7` = 1 in `FD3F...`). (src: Ross-Tech wiki + scans A and F above)
- **[added in verification]** A Mk5 Golf 4Motion's Haldex module as VCDS prints it: `Address 22: AWD Labels: 1K0-907-554.lbl / Part No: 1K0 907 554 F / Component: Haldex 4Motion 0115 / Coding: 0000001` — short coding, `.lbl` label, no ASAM ⇒ KWP over TP 2.0. (src: scan F)
- **[added in verification]** Its TP 2.0 logical address on a 1K0 Gen2 Haldex is `0x0A` (reply on `0x20A`, tester TX id 0x764), and probing `0x22` got no answer. (src: OpenHaldex-C6, §D)
- ODIS has two UDS slots for AWD: `LL_AllWheelContrUDS 0x70F/0x71D → 0x779/0x787`; OpenHaldex-C6 uses 0x70F/0x779 only for the Gen5 (MQB) Haldex and KWP/TP 2.0 for Gen2/Gen4 ("The PQ-platform Haldex (AWD) controller is diagnosed with KWP2000 tunnelled over VW TP2.0, not raw UDS/ISO-TP."). (src: ConnorHowell table; OpenHaldex-C6 OpenHaldexC6_UDS.cpp)
- VCDS reports "No response from AWD controller (address 22)" when the Haldex is dead; forum consensus is to check wiring/ground before replacing. (src: https://forums.ross-tech.com/index.php?threads/3627/)

---

#### A. What the owner's modules actually print (real Auto-Scans fetched this session)

2008 R32 Mk5, US (VTX-R32F, VCDS Auto-Scan quoted verbatim; same ECU family/part numbers as sibling scan A):

| Addr | Labels | Part No SW / HW | Component | Revision / serial | Coding | notes |
|---|---|---|---|---|---|---|
| 01 Engine | `022-906-032-BDB.lbl` | `022 906 032 KR` / `022 906 032 GP` | `R32-DQ-LEV2 G 1098` | `1QH02---` / `VWX7Z0G43N98XU` | `0000178` | `Readiness: 0000 0000`; "No fault code found" |
| 02 Auto Trans | `02E-300-0xx.lbl` | `02E 300 011 CC` / `02E 927 770 AD` | `GSG DSG 082 1405` | `05108020` / `00001008191028` | `0000020` | DQ250 |
| 03 ABS | `1K0-907-379-MK60-A.lbl` | `1K0 907 379 AB` / same | `ESP 4MOTION MK60 0102` | `00H13001` | `0021128` | |
| 22 AWD | `1K0-907-554.lbl` | `1K0 907 554 L` (single part no, no SW/HW split) | `Haldex 4Motion 0116` | — | `0000001` | `Shop #: WSC 00000 000 00000` |
| 25 Immobilizer | `1K0-920-xxx-25.clb` | `1K6 920 974 DX` / same | `IMMO VDD 2216` | `V0002000` / `VWX7Z0G43N98XU` | — | same serial as engine (immo pairing) |

- The engine component string as VCDS prints it is `R32-DQ-LEV2 G 1098` (18 visible characters, VCDS pads the field) [corrected: not "20+"] — name field `R32-DQ-LEV2`, a 1-char software variant `G`, 4-digit SW version `1098`. VCDS also prints `Shop #: WSC 01279 785 00200` for the engine and `WSC 04940 001 00001` for the DSG (the WSC/importer/equipment triple from the `1A 9B` block) [added] (src: VTX-R32F, re-fetched). ME7Logger's Mk5 R32 image name confirms the Bosch numbers behind it: `VW Golf MK5 R32 0261201807 022906032KR 1037387913.bin` (HW `0261201807`, SW `1037387913`) (src: NEF-837).
- A Mk5 Golf 2.0 TDI 4Motion (earlier Gen2 revision) prints `Address 22: AWD Labels: 1K0-907-554.lbl Part No: 1K0 907 554 A Component: HALDEX 4Motion 0105 Coding: 0000001` (src: TDIC-HLDX). A Mk5 Golf GTI-forum 4Motion scan prints `Part No: 1K0 907 554 C` with the same label [added] (src: MK5GTI-H). Together with the R32 (`...554 L`, `0116`) and the sibling's scan F (`...554 F`, `0115`) the Gen2 family is `1K0 907 554 A/C/F/L …` / `Haldex 4Motion 01xx` / coding `0000001` / `.lbl` label, i.e. KWP2000 over TP 2.0 (no ASAM/ROD line printed in any of these scans) [corrected: the VCDS release of each scan was not checked, so "VCDS 14.x" was dropped].
- Contrast, Mk4 R32 (Gen1): `Address 22: AWD Labels: 02D-900-554.lbl Part No: 02D 900 554 UM Component: HALDEX LSC ECC 0002` (src: VTX-MB). Contrast, aftermarket HPA Gen2 controller: `Address 22: AWD Labels: None Part No: HW0 5Ha lde x Component: Tuning Coding: 0000001` — the `1A 9B` strings are free text, do not key logic on them (src: VTX-HLDX). Contrast, a Gen4 unit on an 8J TT: `Address 22: AWD Labels: 0AY-907-554-V1.clb PartNoSW: 0BR907554A HW: 0BR907554A` component `Haldex 4Motion 3016` — `.clb` label and a SW/HW split, i.e. a different (UDS-era) dataset [added] (src: TTF-3016).
- Gen4 Haldex on a 2013 Passat (UDS, for contrast only): fault printed as `00448 - Haldex Clutch Pump (V181)` with `Fault Status: 00101011 / Fault Priority: 3 / Fault Frequency: 1` (src: RT-FORUM-7527). The Gen2 units print KWP-style `00448 - Haldex Clutch Pump (V181) 014 - Defective` (src: TDIC-HLDX).

### Reported / unverified (confidence)

#### 3. Protocol per module — 2008 R32 Mk5 (from memory + the scan evidence)

| Addr | ECU family (memory) | Protocol | conf. | confirm by |
|---|---|---|---|---|
| 01 | Bosch **ME7.1.1**, 022 906 032 (R32 3.2 BUB) | KWP2000 / TP 2.0 (dest 0x01). Also answers generic OBD-II on 0x7E0/0x7E8 (modes 01/03/09). Whether it answers UDS-style `0x7E0 10 03` is unknown (the aep evidence was withdrawn — that car is an EV). | high / unknown | TP 2.0 open 0x01 → `1A 9B`; OBD `7DF 02 09 02`; `7E0 02 10 03` |
| 02 | Temic DQ250 **02E 300 011**, HW 02E 927 770 | KWP2000 / TP 2.0 (no ASAM in scan) | high | probe dest 0x02 (medium) |
| 03 | ATE/Teves **MK60** ESP 4MOTION, 1K0 907 379 AB | KWP2000 / TP 2.0 (dest 0x03 per the ABS emulator, medium) | high / medium | probe 0x03 |
| 04 | G85 steering angle sensor (sub-node of ABS; not a separately scannable module on PQ35) | n/a | high | — |
| 08 | Climatronic PQ35, 1K0 907 044 | KWP / TP 2.0 | high | probe |
| 09 | Bordnetz-SG 3C0 937 049 AJ ("highline" BCM; the R32 scan shows 3C0, not 1K0 937 049) | KWP / TP 2.0 | high | probe |
| 0F | SDARS Sirius tuner 8E0 035 593 | KWP / TP 2.0 (infotainment CAN via gateway) | high | probe |
| 15 | Airbag VW8R 1K0 909 605 | KWP / TP 2.0 | high | probe |
| 16 | Steering column module 1K0 953 549 (J527) | KWP / TP 2.0 | high | probe |
| 17 / 25 | Cluster VDD 1K6 920 974 D with integrated immobilizer | KWP / TP 2.0 (reported TP2.0 dest 0x07) | high / medium | probe 0x07 and 0x17 |
| 19 | J533 gateway 1K0 907 530 L (HW 1K0 907 951) | KWP / TP 2.0, **dest 0x1F** | high | `1A 9B` at 0x1F |
| 22 | Haldex Gen2 coupling ECU. On a Mk5 Golf 4Motion TDI it is **1K0 907 554 F "Haldex 4Motion 0115"** (verified, scan F); whether the R32 carries 1K0 907 554 or 0AY 907 554 is **not** verified (the vwvortex/r32oc/ttforum pages are paywalled, HTTP 402) | KWP / TP 2.0 at **dest 0x0A** (OpenHaldex-C6) — **not** the UDS 0x70F/0x779 slot (that is Haldex Gen5 on MQB) | high (protocol) / medium (part no.) | probe 0x0A, `1A 9B` |
| 37 | MFD2 navigation 1K0 919 887 | KWP / TP 2.0 | high | — |
| 42 / 52 | Door modules MIN3 1K0 959 701/702 | KWP / TP 2.0 | high | probe |
| 44 | ZF-Lenksysteme EPS 1K1 909 144 M (Gen2, curve "Kl.141") | KWP / TP 2.0, reported dest 0x09 | high | probe 0x09 |
| 46 | Comfort KSG 1K0 959 433 CT (also serves 65 TPMS "RDK") | KWP / TP 2.0 | high | probe |
| 47 | Amplifier 1K6 035 456 | KWP / TP 2.0 | high | — |
| 55 | Dynamic headlight range 1T0 907 357 | KWP / TP 2.0 | high | — |
| 56 | Radio 1K0 035 095 (RCD300-class) | KWP / TP 2.0 | high | — |
| 65 | = 46 (same ECU) | — | high | — |

#### 4. Protocol per module — 2012 Golf TDI Mk6 (CJAA)

| Addr | ECU (scan B/C unless noted) | Protocol | conf. | note |
|---|---|---|---|---|
| 01 | Bosch **EDC17CP14**, CJAA, SW 03L 906 019 xx / HW 03L 906 022 xx or 03L 907 309 xx, label 03L-906-022-CBE.clb | **KWP2000 / TP 2.0 at dest 0x01** — now VERIFIED (§D): seishuku polls his 2013 Jetta TDI's `03L 906 019 HE` with TP 2.0 + `21 xx`; two VCDS scans print no ASAM/ROD. The brief's "EDC17CP14 = UDS" is wrong for this variant; the Passat's EDC17 (03L 906 012 CKRA) IS UDS. Whether it *also* answers UDS `22 F187` on 0x7E0 is untested. | high | still test `7E0 03 22 F1 87` once (OPEN Q.2) |
| 02 | DQ250 02E 300 05x / 02E 927 770 AJ..AL (if DSG) | KWP / TP 2.0 (scans C and D) | high | — |
| 03 | MK60EC1 1K0 907 379 AP/BJ | KWP / TP 2.0 | high | indirect TPMS lives here on 2011+ NAR cars (Ross-Tech) |
| 05 | KESSY 5K0 959 434 (if fitted) | UDS (scan D) | high | 0x732/0x79C |
| 08 | Manual A/C 7N0 907 426 / Climatic 3C8 907 336 / Climatronic 5K0/561 907 044 | UDS | high | 0x746/0x7B0 |
| 09 | BCM PQ35 1K0 937 086 P or 5K0 937 08x | KWP / TP 2.0 | high | "all doors unlocked" caveat |
| 15 | Airbag VW10G 5K0 959 655 | UDS | high | 0x715/0x77F |
| 16 | 5K0 953 549 E "Lenks.Modul" → UDS; 1K0 953 549 CD "J0527" → KWP | mixed by build | high | 0x70C/0x776 when UDS |
| 17 / 25 | 5K0 920 97x KOMBI with immo | UDS | high | 0x714/0x77E and 0x711/0x77B |
| 19 | 7N0 907 530 H (2012) / 1K0 907 530 AA (2010) | KWP / TP 2.0 (no ASAM in scans B and D); 3-byte coding; installation list is a separate function on 7N0 | medium | OPEN Q.4 |
| 1C | Compass 5N0 919 879 | KWP | high | — |
| 2B | ELV 5K0 905 861 (if KESSY) | UDS | high | 0x731/0x79B |
| 2E | Media-In 5N0 035 342 | KWP | high | — |
| 36 | Seat memory 561 959 760 (if fitted) | KWP | high | — |
| 37/56 | RNS-MID 3C8 035 684 (both addresses) / RCD510 Radio Prem-8 1K0 035 180 at 56 | KWP (RCD510 Prem-8 prints no ASAM) | high | the brief's "RCD510 (KWP?)" — yes, KWP |
| 42/52/62/72 | 5K0 959 701..704 "Tuer-SG" (GEN3) → KWP, each its own address; 561/3C0 959 79x GEN4 → UDS with rear doors as sub-systems of 42/52 (scan D, Ross-Tech) | mixed by build | high | — |
| 44 | EPS_ZFLS 1K0 909 144 H/M | KWP / TP 2.0 (reported dest 0x09) | high | — |
| 46 | merged into 09 (Ross-Tech) — appears in scan list but prints no block | — | high | — |
| 47 | 10-ch amp 3T0 035 456 (if fitted) | UDS | high | — |
| 4F | EZE_2 7N0 907 532 (if fitted) | KWP | high | — |
| 65 | On the 2010 Jetta the BCM (5K0 937 085 C) answers 65 "RDK"; the 2012 Golf scan has no 65 (indirect TPMS in ABS) | KWP | high | — |
| 77 | UHV 5K0 035 730 (UDS) or 1K8 035 730 (KWP, scan C) | mixed by build | high | 0x76B/0x7D5 when UDS |

R-A. **ME7.1.1 BUB engine coding `0000178`** digit meaning: not documented on any fetched page (search this session found scans only). Low confidence memory: Mk5 ME7/MED9 engine coding is `0 0 0 0 1 7 8` with the last two digits a market/transmission/traction variant selector; do not decode. Confirm: read the VCDS "Coding" balloon text from `022-906-032-BDB.lbl` on the car.

R-F3. DQ250 **TP 2.0 logical address 0x02** — sibling `addresses.md` rates medium-low; the `02E-300-0xx.lbl` KWP module should answer `1A 9B` on that channel (Q8).

R-G1. Haldex Gen2 **part numbers**: early Mk5 R32 / 8P A3 used `0AY 907 554` with component `Haldex 4Motion 0043`, later `1K0 907 554 x` `01xx` (web-search summary of vwvortex scans, not opened; the verified members of the `1K0 907 554` family are now A, C, F, L — §A). Medium. Note that a later `0AY-907-554-V1.clb` / `0BR 907 554 A` / `Haldex 4Motion 3016` unit exists on 8J TTs (VERIFIED, TTF-3016) — a `.clb` module, not the Gen2 `.lbl` family. Haldex Gen2 TP 2.0 logical `0x0A` — sibling-verified (OpenHaldex-C6).


---

## 9. ECU-specific diagnostic knowledge

Source sheet: `ecus.md` (verification pass: every URL re-fetched, proof-of-work interstitials solved; `[corrected]`/`[added]`/
`[downgraded]`/`[promoted]` marks are the verifier's). Contents: ME7Logger `.ecu` format (verified from two genuine
ME7Info v1.20 files) and what it does on the wire; ME7 RAM variable names/factors (addresses are image-specific — not the
R32's); the VW standardized gasoline measuring-block groups and R32 usage; R32 fault-code pages; EDC17CP14/CJAA
measuring blocks, service functions and fault codes; DQ250 02E identity, basic-settings sequence, measuring blocks and
fault codes; Haldex Gen2; gateway and cluster. Conventions: "MVB" = VCDS measuring value block (`[08]` group), fields `.1 .. .4`.

### Source key for this layer (verbatim from the sheet)

| id | URL | what it is |
|---|---|---|
| RT-02E | https://wiki.ross-tech.com/wiki/index.php/6-Speed_Direct_Shift_Gearbox_(DSG/02E) (oldid 9789) | DQ250 coding / basic-settings sequence / test drive |
| RT-DPF | https://wiki.ross-tech.com/wiki/index.php/Diesel_Particle_Filter_Emergency_Regeneration | PD vs CR-TDI(CAN) vs UDS regeneration procedures, MVB numbers |
| RT-CRTDI | https://wiki.ross-tech.com/wiki/index.php/2.0L_CR_TDI (oldid 9802) | NAR 2.0 CR-TDI coding-II / adaptation / basic setting / IMA / G450 |
| RT-TBA | https://wiki.ross-tech.com/wiki/index.php/Throttle_Body_Alignment_(TBA) (oldid 9610) | group 060 procedure KWP vs UDS |
| RT-1K-KOMBI | https://wiki.ross-tech.com/wiki/index.php/VW_Golf_(1K)_Instrument_Cluster (oldid 7906) | Mk5 cluster coding digits, login, adaptation channels |
| RT-5K-KOMBI | https://wiki.ross-tech.com/wiki/index.php/VW_Golf_(5K)_Instrument_Cluster (oldid 8814) | Mk6 (UDS) cluster adaptation names |
| RT-RDY-UDS | https://wiki.ross-tech.com/wiki/index.php/Readiness_Test_(UDS_only) (oldid 9740) | UDS readiness routine + IDE numbers |
| RT-RDY-APB | https://wiki.ross-tech.com/wiki/index.php/Readiness_-_APB_Engine_Code (oldid 2916) | manual readiness on a KWP ME7 engine (group list) |
| RT-MISFIRE | https://wiki.ross-tech.com/wiki/index.php/Misfire_Diagnosis (oldid 9738) | misfire groups 014–017 |
| RT-FT | https://wiki.ross-tech.com/wiki/index.php/Fuel_Trim_Info (oldid 9295) | group 032/033/002 semantics |
| RT-EGR | https://wiki.ross-tech.com/wiki/index.php/Exhaust_Gas_Recirculation_(EGR)_Valve_Adaptation (oldid 9329) | gasoline EGR adaptation group 074 |
| RT-FP | https://wiki.ross-tech.com/wiki/index.php/Fuel_Pump_Basic_Settings_for_PD,_PPD,_and_CR_TDI_Engines (oldid 8669) | CR-TDI fuel pump basic setting group 035 |
| RT-ATBS | https://wiki.ross-tech.com/wiki/index.php/Automatic_Transmission_Basic_Settings (oldid 6156) | kick-down basic settings TCM 000 / ECM 063 |
| RT-SRI | https://wiki.ross-tech.com/wiki/index.php/SRI_Reset_Procedure (oldid 8810) | SRI reset, UDS clusters |
| RT-5K-TWEAKS | https://wiki.ross-tech.com/wiki/index.php/VW_Golf/Golf_Plus_(5K/52)_Tweaks | Mk6 cluster adaptation names |
| RT-P189C | https://wiki.ross-tech.com/wiki/index.php/P189C/006300 (oldid 7249) | DSG pressure build-up fault |
| RT-P189A | https://wiki.ross-tech.com/wiki/index.php/P189A_-_Clutch_1:_Clearance_too_Small (oldid 8567) | 0AM only |
| RT-P0300 | https://wiki.ross-tech.com/wiki/index.php/16684/P0300/000768 (oldid 9508) | |
| RT-P0299 | https://wiki.ross-tech.com/wiki/index.php/16683/P0299/000665 (oldid 9073) | has a CBEA/CJAA "Diesel" section |
| RT-P2002 | https://wiki.ross-tech.com/wiki/index.php/18434/P2002/008194 (oldid 7490) | CBEA/CJAA G450 note |
| RT-P2015 | https://wiki.ross-tech.com/wiki/index.php/18447/P2015/008213 (oldid 9219) | |
| RT-P2463 | https://wiki.ross-tech.com/wiki/index.php/18895/P2463/009315 (oldid 6974) | |
| RT-P0401 | https://wiki.ross-tech.com/wiki/index.php/16785/P0401/001025 (oldid 7846) | CBEA/CJAA J883 + EGR filter notes |
| RT-P0411 | https://wiki.ross-tech.com/wiki/index.php/16795/P0411/001041 (oldid 4723) | |
| RT-P0491 | https://wiki.ross-tech.com/wiki/index.php/P0491 (oldid 9238) | |
| RT-P0087 | https://wiki.ross-tech.com/wiki/index.php/16471/P0087/000135 (oldid 9428) | has the "MVB 208/209 field 3 cam adaptation ±8" note |
| RT-P0101 | https://wiki.ross-tech.com/wiki/index.php/16485/P0101/000257 (oldid 8933) | |
| RT-MB | https://www.ross-tech.com/vag-com/m_blocks/ and its 17 sub-pages `000.html, 001-009, 010-019, 020-029, 030-049, 050-059, 060-069, 070-079, 080-085, 090-098, 099-100, 101-109, 110-119, 120-129, 130-137, 140-147, 160-169` [corrected: exact sub-page names; `080-089.html` etc. do not exist (404)] | VW/Audi "standardized" gasoline engine measuring block groups |
| RT-LOGIN | https://www.ross-tech.com/vcds/tour/login_screen.php | VCDS Login = VAG 1551 function 11 |
| RT-SRI-TOUR | https://www.ross-tech.com/vcds/tour/sri-reset.php | SRI function text |
| RT-TDI | https://www.ross-tech.com/vag-com/cars/tdi.html | VCDS function numbers 01…15, ALH groups |
| RT-FORUM-7527 | https://forums.ross-tech.com/index.php?threads/7527/ | 2013 Passat Gen4 Haldex 00448 scan (UDS-style fault status) |
| VWTSB-DPF | https://static.nhtsa.gov/odi/tsbs/2013/MC-10070753-3639.pdf (VW Tech Tip TT 26-11-01, 2009-2013 Golf/Jetta TDI) | MVB 240/241/100, soot thresholds |
| VWTSB-EGRF | https://static.nhtsa.gov/odi/tsbs/2014/MC-10120330-9999.pdf | P2463 + EGR filter |
| VWTSB-P0299 | https://static.nhtsa.gov/odi/tsbs/2014/SB-10055860-4792.pdf | P0299 2.0 CR-TDI bulletin |
| NEF-837 | https://nefariousmotorsports.com/forum/index.php?action=printpage;topic=837.0 | setzi62's ME7Logger release thread (format, limits, Mk5 R32 answer) |
| NEF-19082 | https://nefariousmotorsports.com/forum/index.php?action=printpage;topic=19082.0 | "Arduino ME7Logger" thread: K-line trace of ME7Logger, prj's description of the method |
| VME7-ECU | https://raw.githubusercontent.com/sbloom82/VisualME7Logger/master/VisualME7Logger.Output/resources/ME7Logger/ecus/Audi%20A6%20allroad%202.7T%20BEL%20250HP%204Z7907551R.ori.ecu | a genuine ME7Info v1.20 `.ecu` (800 lines) |
| VME7-OUT | https://raw.githubusercontent.com/sbloom82/VisualME7Logger/master/VisualME7Logger.Output/resources/ME7Logger/logs/ME7Loggeroutput.txt | ME7Logger console output of a real session |
| VME7-COMM | https://raw.githubusercontent.com/sbloom82/VisualME7Logger/master/VisualME7Logger.Output/resources/ME7Logger/logs/example.commdata | ME7Info "connect overview" |
| VME7-H | https://raw.githubusercontent.com/sbloom82/VisualME7Logger/master/VisualME7Logger.Output/resources/ME7Logger/lib/ME7Logger.h | ME7Logger shared-library API |
| PB-ECU | https://pastebin.com/raw/NTysnYWX | second ME7Info v1.20 `.ecu` (8N0906018H, S3 1.8T) |
| NYET-QS | https://raw.githubusercontent.com/nyetwurk/me7-logger/master/QUICKSTART.md (+README.md, DEVELOPER.md, config/measurements.yaml) | open-source ME7Logger workalike |
| NEFMOTO-KWP | https://raw.githubusercontent.com/NefMoto/NefMotoOpenSource/master/Communication/KWP2000Actions.cs and KWP2000Interface.cs | KWP2000 ReadMemoryByAddress request layout |
| SEISHUKU | https://raw.githubusercontent.com/seishuku/teensycanbusdisplay/master/vwtpkwp2k.c | KWP `21 <group>` over TP 2.0, response layout |
| AUDIF-DSG | https://www.audi-forums.com/threads/dsg-data-readout-before-and-after.59526/ | VCDS DQ250 log (group labels) + VAS-PC "Measured value blocks for control unit J743 (DQ250)" list |
| TDIC-DSGT | https://forums.tdiclub.com/index.php?threads/measuring-block-for-dsg-temp.318269/ | Ross-Tech staff: group 019 = 3 temperature sensors |
| TDIC-DPF | https://forums.tdiclub.com/index.php?threads/clean-diesel-dpf-data-collection-thread.324067/ | owners' CJAA/CBEA MVB numbers |
| TDIC-LBL | https://forums.tdiclub.com/index.php?threads/more-complete-cbea-cjaa-measured-value-block-labels.451069/ | points to ERWIN "D3E802F8708-2_0L_TDI_Common_Rail_CBEA-CJAA.pdf" |
| TDIC-HLDX | https://forums.tdiclub.com/index.php?threads/awd-haldex-clutch-pump-code.526187/ | Mk5 4Motion Haldex 1K0 907 554 A scan, output-test behaviour |
| VTX-R32F | https://www.vwvortex.com/threads/r32-fault-codes-help.5923737/ | 2008 R32 Auto-Scan (engine/DSG/ABS/Haldex/immo idents) |
| VTX-R32FWD | https://www.vwvortex.com/threads/08-r32-fwd-only-vcds-codes.5775384/ | R32 Haldex faults 01073/01155 |
| VTX-HLDX | https://www.vwvortex.com/threads/vcds-codes-lots-of-em-haldex-not-working.5962078/ | R32 Haldex faults, "HW0 5Ha lde x / Tuning" ident of an HPA controller |
| VTX-GEN4 | https://www.vwvortex.com/threads/detailed-procedure-for-gen-4-haldex-fluid-and-filter-service.8894225/ | Haldex output-test step names |
| VTX-MB | https://www.vwvortex.com/threads/measuring-blocks.7224014/ | Mk4 R32 scan (Gen1 Haldex ident, for contrast) |
| TTF-CHAIN | https://www.ttforum.co.uk/threads/detecting-3-2l-vr6-chain-stretch-with-vcds.1836951/ | 3.2 VR6 groups 090/091/208/209 (translated German forum text) |
| TTF-HTEST | https://www.ttforum.co.uk/threads/haldex-test-via-vcds.2018153/ | Gen2 Haldex measuring blocks / output test behaviour (8J TT) |
| TTF-HPUMP | https://www.ttforum.co.uk/threads/haldex-gen2-pump-failure-fixed.2025356/ | Gen2 pump faults 00448/01324/01316 |
| R32OC-H | https://www.r32oc.com/threads/more-haldex-issues.260038/ | 01073 on Mk5 R32 Gen2 |
| R32OC-V | https://www.r32oc.com/threads/vcds-what-to-check-etc.50371/ | R32 owners: 032, 208/209 |
| ATI-G4 | https://automotivetechinfo.com/2019/08/vw-haldex-4motion-generation-iv/ | Gen4 Haldex groups 125/126/005/006/010-012/004, basic setting 051 |
| ECOT | https://eco-torque.co.uk/blogs/news/vw-audi-02e-dq250-dsg-mechatronic-failures-symptoms-fault-codes-fixes | DQ250 fault-code list (secondary) |
| MTD-DSG | https://www.myturbodiesel.com/threads/dsg-error-codes-and-transmission-not-shifting-correctly.34714/ | 18115/P1707, 17150/P0766 as VCDS prints them |
| MTD-P0299 | https://www.myturbodiesel.com/threads/2010-jetta-tdi-concerns-p0299-particulate-filter.26131/ | CJAA owner using 099/241/107 |
| VTX-SOL | https://www.vwvortex.com/threads/dsg-250-how-to-test-solenoid.9391167/ | DQ250 output test needs engine running (secondary) |
| VAGC-DSG | https://www.vag-coding.net/tutorials-information/vcds-reset-dsg/ | restates RT-02E; UDS DQ250 uses IDE02903 |
| DERP-ME7 [added] | https://raw.githubusercontent.com/derpston/me7/master/me7.py (+README.md) | open-source Python ME7 K-line logger (the repo the sibling cache calls "pylibme7"; the real repo name is `derpston/me7`) |
| VTX-CJAA-011 [added] | https://www.vwvortex.com/threads/2011-cjaa-tdi-low-boost-p0299.5366434/ | 2011 CJAA (`03L 906 022 PB`, `R4 2,0L EDC G000AG 9045`) VCDS log of group 011 + P0299 freeze frame |
| TDIC-334430 [added] | https://forums.tdiclub.com/index.php?threads/dpf-emergency-regeneration.334430/ | 2009 Jetta TDI owner's VCDS DPF group list 097/099/105/108/240/241 with field names |
| TDIC-444852 [added] | https://forums.tdiclub.com/showthread.php?t=444852 | "EGR Adaptation with VCDS on MK6 CJAA": long-adaptation channels 118/123 |
| TDIC-441819 [added] | https://forums.tdiclub.com/showthread.php?t=441819 | TDI owners: group 011 fields 2/3 read 1000 mbar key-on engine-off |
| MTD-38651 [added] | https://www.myturbodiesel.com/threads/cjaa-into-cbea-car-crank-no-start-rail-fuel-pressure.38651/ | CJAA owner: measuring block 020 = rail pressure actual vs specified |
| TUNEZ-ACT [added] | https://tunezilla.com/files/CBEA_CJAA_TurboActuatorAdaptation_VCDS.pdf | CBEA/CJAA turbo actuator adaptation = Basic Settings "Charge Pressure Control" |
| MALONE [added] | https://malonetuning.com/assets/files/vagcom_logging_guide.pdf | VCDS logging guide: block sets per engine family (CR-TDI 2009+: 001+003+004, 008+011+099) |
| VWTSB-RDY [added] | https://static.nhtsa.gov/odi/tsbs/2014/MC-10124424-9999.pdf | VW PROFI form for MY09-14 CBEA/CJAA; only its "Readiness-Bits and Driving Procedure" table (MVB 086/089 bit map, MWB 41/4, 136/4, 43/3, 138/3, 7/3, 100/1, 100/2) is used — the flash/campaign content is out of scope |
| VWTT-NOX [added] | https://static.nhtsa.gov/odi/tsbs/2019/MC-10169515-0001.pdf | VW Tech Tip 01-19-07TT (2009-2014 CBEA/CJAA): MVB 46/2 = coolant temperature |
| MK5GTI-H [added] | https://www.mk5golfgti.co.uk/forum/index.php?topic=130534.0 | Mk5 Golf 4Motion scan: `1K0 907 554 C`, label `1K0-907-554.lbl` |
| TTF-3016 [added] | https://www.ttforum.co.uk/threads/haldex-4motion-3016.1688361/ | contrast only: Gen4 unit prints `0AY-907-554-V1.clb / 0BR907554A / Haldex 4Motion 3016` |

### Verified (source)

#### B. ME7Logger `.ecu` definition file — format verified from a genuine ME7Info v1.20 file

Two independent ME7Info v1.20 outputs were fetched (VME7-ECU: `4Z7907551R`, 2.7T BEL; PB-ECU: `8N0906018H`, S3 1.8T); both have byte-identical structure.

**File skeleton** (comment char `;`, INI-style `[Section]`, `Key = Value` with `;` trailing comments allowed):

```
;
; ECU characteristics for logging with ME7Logger
;
; Generated by ME7Info v1.20 (c) mki, 11/2010-03/2013
;
; You can hand-edit this file to add new measurement variable definitions
; or to change existing definitions, e.g. to change a conversion formula.
;
; Flash image:  Audi A6 allroad 2.7T BEL 250HP 4Z7907551R.ori.bin (size=1048576)
; Used mapfile: me7_std.map
;
[Version]
Version           = 1.20

[Communication]
Connect      = SLOW-0x11    ; Possible values: SLOW-0x11, FAST-0x10
Communicate  = HM0          ; Possible values: HM0, HM2-0x10
LogSpeed     = 56000        ; Possible values: 10400, 14400, 19200, 38400, 56000, 76800, 125000
[Identification]
HWNumber          = {0261207769}
SWNumber          = {1037366370}
PartNumber        = {4Z7907551R  }
SWVersion         = {    }
EngineId          = {2.7L V6/5VT}

[Measurements]
; Conversion factors:
;   S -> 0 = unsigned, 1 = signed value
;   I -> 0 = normal, 1 = inverse conversion
;   A -> factor
;   B -> offset
; Normal conversion:  phys = A * internal - B
; Inverse conversion: phys = A / (internal - B)

;Name           , {Alias}                           , Address, Size, Bitmask, {Unit},    S, I,            A,      B, Comment
abo             , {CountStartsWithOilInFuel}        , 0x384021,  1,  0x0000, {#}       , 0, 0,            1,      0, {Anzahl Starts mit Benzin im Öl}
```
(src: VME7-ECU, lines 1–33 verbatim; PB-ECU identical except `LogSpeed` comment lists `57600` instead of `76800`.)

**Measurement line = 11 comma-separated fields, in this exact order** (src: VME7-ECU header line `;Name , {Alias} , Address, Size, Bitmask, {Unit}, S, I, A, B, Comment`):

| # | field | syntax | observed values |
|---|---|---|---|
| 1 | Name | bare identifier, Bosch variable name, `_w` suffix = 16-bit word, `_n` index suffixes `_0.._7` | `nmot`, `nmot_w`, `wkr_0`, `B_ll` |
| 2 | Alias | `{…}`, may be empty `{}` | `{EngineSpeed}` |
| 3 | Address | `0x` + 6 hex digits, ECU RAM address | `0x00F888` (internal RAM), `0x380416` (XRAM) |
| 4 | Size | `1` or `2` bytes | the BEL file has **262 one-byte and 503 two-byte** entries (765 total); the 8N0906018H file has 239 / 518 (757 total) [corrected: the original sheet had the two counts swapped; recounted from both files] |
| 5 | Bitmask | `0x0000` = whole value; non-zero = single-bit boolean | `0x0800` for `B_kr` (size 2) |
| 6 | Unit | `{…}`, may be empty | `{rpm}`, `{%}`, `{°KW}`, `{mbar}`, `{g/s}`, `{ms}`, `{V}`, `{km/h}`, `{°C}`, `{-}`, `{#}`, `{s}`, `{% DK}`, `{% PED}`, `{%/seg}` |
| 7 | S | `0` unsigned / `1` signed | |
| 8 | I | `0` normal / `1` inverse (no inverse entries exist in either fetched file — re-counted: 0 of 765 and 0 of 757) | |
| 9 | A | factor, decimal or scientific (`3.05176e-005`), may be negative (`-0.75`) | |
| 10 | B | offset, decimal (`48`, `50`, `273.15`, `0.2`, `1`) | |
| 11 | Comment | `{…}` German Bosch description, may be empty `{}` | |

Conversion: `phys = A * internal - B` (normal); `phys = A / (internal - B)` (inverse). Examples: `tmot , {CoolantTemperature}, 0x3806DB, 1, 0x0000, {°C}, 0, 0, 0.75, 48` → `0.75*raw - 48 °C`; `tabgm , 0x38483B, 1, …, {°C}, 0,0, 5, 50` → `5*raw - 50`; `tahsomf_w … 0.0234375, 273.15` (Kelvin→°C). Multi-byte values are big-endian ("word"): the open-source `derpston/me7` reader mirrors the `.ecu` fields in `Variable(name, addr, size=1, unit, factor, bitmask, offset, signed, inverse, comment)` and decodes with `struct.unpack(">" + {1:"B",2:"H"}[size])`, applies `value &= bitmask`, re-interprets as signed when `signed`, then `factor / (value - offset)` if `inverse` else the normal formula [promoted from R-B2: fetched this pass] (src: DERP-ME7 lines 47-115); the alias `(Word)` comments mark `_w` as 16-bit (src: VME7-ECU). **Caveat:** that reader is the only open implementation and its author says "Undergoing significant refactor, don't use this yet" (src: DERP-ME7 README); the ME7Logger binary itself is closed, so "big-endian" rests on this reader plus the C167 convention — the ECU-side byte order should still be sanity-checked against a known value (e.g. `nmot_w` vs `nmot`) on any car that is ever logged this way.

**Two-byte bit variables**: `B_kr , {} , 0x00FD8A, 2, 0x0800, {} , 0, 0, 1, 0, {Bedingung Klopfregelung aktiv}` and `B_ll , {} , 0x00FDA6, 2, 0x0008, …` — a 16-bit word is read and ANDed with the mask (src: VME7-ECU). The **mask and address are per-image**: in the 8N0906018H file `B_ll` is `0x00FD8A, 2, 0x0400` and `B_kr` is `0x00FD72, 2, 0x0008` [added] (src: PB-ECU). Likewise **factors can differ per image**: `ti_b1` is `0.004 ms/LSB` in the BEL file but `0.00266667` in the 8N0906018H file [added] (src: VME7-ECU, PB-ECU) — so a `.ecu`'s A/B columns must be taken from the matching image, never copied between images.

**Spaces, not tabs** separate fields in v1.x config files ("you MUST use spaces to separate fields, you can't use tabs" — nyet, 10 Aug 2011, re-checked); TABs were allowed from the 12.08.2011 update ("Allow TAB's also in trace config files") (src: NEF-837). The first release post advertised "Up to 127 independent variables can be logged at same time"; the v1.20 limits below supersede it [added] (src: NEF-837).

**Overlay/limits (v1.20, 10.07.2013)** (src: NEF-837, first post, verbatim): "Read additional ecu characteristics file `my_<ecufile>` if it exists in same directory as `<ecufile>`"; "Read additional log config file `my_<ecu>_template.cfg`"; "logging multiple bitvariables which use the same byte will read only one byte from ecu; logging two byte variables from neighbouring memory addresses will read only one merged word location"; limits "up to 254 bytes, up to 127 different memory locations (1 or 2 bytes), up to 254 variables"; "Up to 50 samples per second possible"; Linux port (`/dev/ttyS*`, `ftdi_sio`, libftdi1) and a shared library `libME7Logger.so/.dll`.

**Trace config (`.cfg`)**: the only key verified is `SamplesPerSecond=10` (open-source workalike's session.cfg, src: NYET-QS) and the DLL config struct `samples_per_second` "(1..50)", `baudrate` "0 (keep default from .ecu file)", `absolute_timestamps`, `sync_to_full_second` (src: VME7-H). ME7Logger's console lists the logged variables as `#no.: name, alias, addr, sz, bitm, S, I, A, B, unit` and then "Logged data size is 34 bytes. Really logged are 20 entries with 34 bytes." (23 variables requested, merged into 20 memory reads) (src: VME7-OUT).

**[Communication] semantics**: `Connect = SLOW-0x11` / `FAST-0x10` / `SLOW-0x00` + `DoubleDelay = 12 ; Possible values 1 .. 100 (delay in 100ms)` ("double slowinit", 12.08.2011 update, "This only allows to connect while engine not yet started") are the only documented values (src: NEF-837, .ecu comment `; Possible values: SLOW-0x11, FAST-0x10`). That the number after `SLOW-` is the 5-baud init address is **inferred** from setzi62's wording "This image allows connection to KWP2000 with slowinit to 0x01" and the console line `try connect slow(11)` [downgraded: the thread never spells out "0x11 = K-line address"; see R-B1] (src: NEF-837 post of 29 Mar 2012; VME7-OUT). ME7Info's connect overview enumerates only K-line options: "slow (0x01) -> KWP2000 / slow (0x31) -> KWP2000 / slow (0x33) -> SAE-J1979(KWP2000) / fast (HM2-phys(0x10)) -> KWP2000 / fast (HM3-func(0x31)) -> KWP2000 / KWP2000 communication: HM0/none(----), HM2/phys(0x10), HM3/func(0x31)" (src: VME7-COMM). **There is no CAN / TP 2.0 option anywhere in the format**; the DLL's interface types are `ITF_SERIAL` and `ITF_FTDI*` only (src: VME7-H).

**ME7Logger does NOT support the Mk5 R32 ME7.1.1.** An '08 R32 owner ran `ME7Info.exe "..\images\VW Golf MK5 R32 0261201807 022906032KR 1037387913.bin"` → "read 1300 map entries / mapped 186 aliases / written 0 definitions". setzi62: "this MK5 R32 image looks completely different to older R32 images (which can be processed by ME7Info). I think this ECU is based on ST10 which is C167 compatible, but the bootrom must be completely different. So, no chance to get the info tool working for this MK5 R32 image and also the logger will not run" (src: NEF-837, 10 Aug 2011). Consequence for vagtune: the `.ecu` *format* is reusable as a variable-definition format, but the ME7Logger program, its `.ecu` generator and its K-line method are not usable on the 2008 R32; any RAM logging on that car must go over TP 2.0/KWP (open question Q1).

**What ME7Logger does on the wire (K-line, ISO 14230)** — as far as open sources show:
- Console sequence of a real session: `try connect slow(11)` → `=> FLASH (slowinit)` → `ecuid reports software version` → `Started session86, speed=56000` → `Read ECU ID's` → `Found bootrom version 06.02/06.05 via readmem` → `Read pointer / Store handler / Verify handler / Redirect pointer / Test handler` → `Start logging (logdata size=34, 10 samples/second, 56000 baud)` (src: VME7-OUT).
- Sniffed bytes of the same start-up (a bench ME7 ECU whose exact variant the poster never states [corrected: the original said "ME7.5"; the poster only says "I have an ECU on the bench" and later that "arrays … are slightly different between the me7.5 and me7.1.1"]; K-line, length-byte-only header): `02 1A 94 B0` (ReadEcuIdentification, option 0x94 = system-supplier software number) → `0C 5A 94 31 30 33 37 33 36 33 33 35 34 FD` (= ASCII `1037363354`) → `03 10 86 63 FC` (StartDiagnosticSession, session 0x86, baud parameter 0x63) → `03 50 86 63 3C`; "The speed does change with staring the development session"; "After this there are 2 readMemoryBy Address commands" that find the bootrom version (`Found bootrom version 05.12/05.32 via readmem` in that trace; `06.02/06.05` in VME7-OUT) (src: NEF-19082, Cadensdad14, Feb 2021). The **baud byte after `10 86`** is tabulated in the open-source reader: `0x30` = 19200, `0x50` = 38400, `0x63` = 56000, `0x64` = 57600 (10400/14400/125000 left as `0x??`), request = `10 86 <baud>`; the author comments "Is this the actual function of 0x86?" [added] (src: DERP-ME7 `startdiagsession`). `0x63` = 56000 matches the trace and the `.ecu` default `LogSpeed = 56000`.
- prj (same thread): "ME7Logger uses a hack (stolen from APR) … It finds the DDLI buffer in RAM and then redirects the pointer to a different (empty) RAM area. Then fills that with WriteMemoryByAddress." and "ME7Logger's handler is bootrom specific" (src: NEF-19082). I.e. the fast sampling is **not** repeated `0x23` reads; it is a buffer read in one request per sample. The open-source `derpston/me7` reader shows the request bytes it uses for that per-sample read [promoted from R-B2; fetched this pass]: setup = `B7 03` followed by one 3-byte big-endian address per variable, with **`0x40` added to the most-significant address byte to request a 2-byte read** (`if var.size == 2: addr[0] += 0x40`; comment "0x03 probably means to expect three byte addresses. Untested."); each sample = the single byte `B7`; the reply is parsed as `[length, 0xF7 ("always seems to be 0xf7"), data bytes in request order, checksum]`; `3D addrHi addrMid addrLo len data…` = WriteMemoryByAddress; `0x82` StopCommunication; `3E` TesterPresent (src: DERP-ME7 lines 43-45, 376, 385-452). **Caveats**: these are the author's reverse-engineered bytes with "Untested" comments; whether `B7` is a standard-ish KWP service or only works after the ME7Logger handler is installed is not stated; the author's README says the library is unfinished.
- A poster's trace note: "ME7.5 doesn't seem to require Security Access for ReadMemoryByAddress and will read fine. ME7.1.1 does? You can see it in the ME7Logger trace too: it tries for a diagnostic session and gets 7F so then attempts to get Security Access (0x27 0x01) and is successful, then it retries a diagnostic session and is successful" (src: NEF-19082, adam-, 26 Jan 2023; the same poster's Mk4 VR6 is "ME7.1 (MK4 VR6)" — note the question mark: it is his reading of a trace, not a statement by the tool's author) [downgraded wording]. Recorded only as "the development session on a Mk4 ME7.1.x may be gated"; nothing about the algorithm is in scope, and the Mk5 R32's ME7.1.1 is a different image (ST10) anyway.
- KWP2000 **ReadMemoryByAddress request layout** (open-source NefMoto): `0x23, addr[23:16], addr[15:8], addr[7:0], size` (one size byte, "minus 4 for the address and size data"); positive response is `0x63` followed by `size` data bytes, read in consecutive blocks of `mMaxBlockSize` (src: NEFMOTO-KWP `getAddressAndSizeMessageData`, `ReadMemoryAction`). Max payload without length byte is 0x3F incl. SID, 0xFF with length byte (src: NEFMOTO-KWP `MAX_MESSAGE_DATA_SIZE_*`).

#### C. ME7 RAM variables of interest (names, units, factors — verified from the 2.7T BEL `.ecu`; **addresses are ECU-image-specific and do NOT apply to the R32**)

All rows below are verbatim from VME7-ECU (whitespace collapsed). Alias names are what ECUxPlot/VisualME7Logger show.

| name | alias | size | unit | S | A (factor) | B (offset) | meaning (comment) |
|---|---|---|---|---|---|---|---|
| nmot | EngineSpeed | 1 | rpm | 0 | 40 | 0 | Motordrehzahl |
| nmot_w | EngineSpeed | 2 | rpm | 0 | 0.25 | 0 | Motordrehzahl |
| nmotll | EngineIdlingSpeed | 1 | rpm | 0 | 10 | 0 | idle-range rpm |
| rl | EngineLoad | 1 | % | 0 | 0.75 | 0 | relative Luftfüllung |
| rl_w | EngineLoad | 2 | % | 0 | 0.0234375 | 0 | rel. Luftfüllung (Word) |
| rlsol_w | EngineLoadRequested | 2 | % | 0 | 0.0234375 | 0 | Soll-Füllung |
| rlmax_w | EngineLoadCorrected | 2 | % | 0 | 0.0234375 | 0 | max. erreichbare Füllung (turbo) |
| mshfm_w | MassAirFlow | 2 | g/s | 0 | 0.0277778 | 0 | Massenstrom HFM 16-bit |
| msdk_w | MassAirFlowAtThrottlePlate | 2 | g/s | 0 | 0.0277778 | 0 | |
| ti_b1 | FuelInjectorOnTime | 2 | ms | 0 | 0.004 (BEL) / **0.00266667** (8N0906018H) [corrected: per-image] | 0 | Einspritzzeit Bank 1 |
| zwout | IgnitionTimingAngleOverall | 1 | °KW | 1 | 0.75 | 0 | Zündwinkel-Ausgabe |
| zwist | IgnitionTimingAngle | 1 | °KW | 1 | 0.75 | 0 | Ist-Zündwinkel |
| zwgru / zwsol | — | 1 | °KW | 1 | 0.75 | 0 | Grund-ZW / Soll-ZW aus Momenteneingriff |
| wkr_0 … wkr_5 | IgnRetardKnockControlCyl1/5/3/2/6/4 | 1 | °KW | 0 | **-0.75** | 0 | zyl.-individuelle ZW-Spätverstellung KR (index = firing-order slot, alias gives the cylinder; re-checked: `wkr_0`→Cyl1, `_1`→Cyl5, `_2`→Cyl3, `_3`→Cyl2, `_4`→Cyl6, `_5`→Cyl4 = the V6 firing order 1-5-3-2-6-4; the 4-cyl 8N0906018H file only has `wkr_0..3`) |
| dwkrz_0 … dwkrz_7 | IgnitionRetardCyl1/5/3/2/6/4/0/0 | 1 | °KW | 1 | 0.75 | 0 | zyl.ind. ZW-Spätverstellung inkl. Dyn.vorhalt |
| rkrn_w_0 … _7 | KnockVoltageCyl… | 2 | V | 0 | 0.0195313 | 0 | normierter Referenzpegel Klopfregelung |
| tans | IntakeAirTemperature | 1 | °C | 0 | 0.75 | 48 | Ansaugluft-Temperatur |
| tmot | CoolantTemperature | 1 | °C | 0 | 0.75 | 48 | Motor-Temperatur |
| tmst | EngineStartTemperature | 1 | °C | 0 | 0.75 | 48 | |
| lamsbg_w | AirFuelRatioDesired | 2 | - | 0 | 0.000244141 | 0 | Lambdasoll Begrenzung (word) |
| lamsons_w | — | 2 | - | 0 | 0.000244141 | 0 | Lambda-Sollwert bezogen auf Sensor-Einbauort (the 2.7T file has no `lamsoni_w`; the 8N0906018H file has `lamsoni_w , {AirFuelRatioCurrent} … 0.000244141` [added] (src: PB-ECU); all are 1/4096 scaled) |
| fr_w | LambdaControl | 2 | - | 0 | 3.05176e-005 | 0 | Lambda-Regler-Ausgang (word) = STFT factor |
| fra_w | AdaptationPartial | 2 | - | 0 | 3.05176e-005 | 0 | multiplikative Gemischadaption (= LTFT partial-load) |
| rkte_w | — | 2 | % | 1 | 0.046875 | 0 | rel. Gemischanteil Tankentlüftung |
| vfzg | VehicleSpeed | 1 | km/h | 0 | 1.25 | 0 | Fahrzeuggeschwindigkeit |
| ub | BatteryVoltage | 1 | V | 0 | 0.0704 | 0 | Batteriespannung (the name is `ub`, not `uba`) |
| wped_w | AccelPedalPosition | 2 | % PED | 0 | 0.0015259 | 0 | normierter Fahrpedalwinkel |
| wdkba | ThrottlePlateAngle | 1 | % DK | 0 | 0.392157 | 0 | Drosselklappenwinkel |
| ps_w | — | 2 | mbar | 0 | 0.0390625 | 0 | Saugrohr-Absolutdruck |
| pus_w | BaroPressure | 2 | mbar | 0 | 0.0390625 | 0 | Umgebungsdruck |
| plsol_w / pvdkds_w / ldtvm | BoostPressureDesired / BoostPressureActual / WastegateDutyCycle | 2/2/1 | mbar/mbar/% | 0 | 0.0390625 / 0.0390625 / 0.390625 | 0 | turbo-only; n/a on the VR6 |
| tabgm / tabgm_w | EGTModelBeforeCat | 1/2 | °C | 0 | 5 / 0.0195312 | 50 | Abgastemperatur-Modell |
| tkatm | CatTemperatureModel | 1 | °C | 0 | 5 | 50 | |
| wnwe_w / wnwse_w | — | 2 | °KW | 1 | 0.0078125 | 0 | intake cam actual / set angle |
| dwnwsp_w | — | 2 | °KW | 1 | 0.015625 | 0 | deviation of cam adaptation angle from set-point |
| B_ll / B_kr | — | 2 | — | — | bitmask 0x0008 / 0x0800 | — | idle condition / knock control active |
| fcmEnd | NumberFaults | 1 | # | 0 | 1 | 0 | number of entries in the fault memory |
| perffilt_w / perfmax_w | CPU-Load / MAX-Load | 2 | % | 0 | 0.025 | 0 | ECU CPU load (ME7Info ≥1.17) |

- VCDS block 032 ↔ RAM: setzi62: "Variables fra_w, frao_w, frau_w are stored as unsigned word (16bit) in the ecu … when you log with VCDS, the ECU … delivers for each variable three bytes (a, b, c) … Byte c is a conversion formula number … In case of fra_w, frao_w, frau_w, the ecu always sets c = 20, so the formula for VCDS is: a*(b-128)/128 [in %]. The ecu sets a=50 … resolution of 50/128 = 0.390625% in a range of -50% .. +50%" (src: NEF-837). An ECUx-style definition list from the same thread for a 2.7T gives the LTFT RAM words as `INT16, Scale=(1.0/21.33)` for additive idle trims and `UINT16, Scale=(1.0/327.68), Offset=(-100)` for the multiplicative partial-load trims (src: NEF-837, post quoting `8D0907551M_0002 RAM Variables.txt`).

#### D. R32 ME7.1.1 (BUB) — measuring blocks owners use, with verified content

**D1. VW/Audi "standardized" gasoline engine group layout** (Ross-Tech's own transcription of the factory standard, "Use as a general guide for engines starting about 1999-2000 where more specific data is not available"; src: RT-MB, all 17 sub-pages fetched). Field order is `.1 .2 .3 .4`; `[unit]` per field. Only the variants relevant to a 2-bank, MAF, E-Gas, 6-cylinder engine are kept; "n/a VR6" marks groups that exist in the standard but not on this engine.

| Group | content (.1 / .2 / .3 / .4) |
|---|---|
| 000 | 10 raw fields, 2-bank: coolant temp / load / RPM / throttle angle / idle control / idle learning value / lambda control B1 / lambda control B2 / lambda adaptation (add) B1 / lambda adaptation (add) B2 |
| 001 | RPM [1/min] / coolant [°C] / lambda control value B1 [%] / lambda control value B2 [%] (2-bank). 1-bank variant .4 = "Adjustment requirements for basic setting" bit field `xxxxxxxx`: bit0 coolant >80 °C, bit1 RPM <2000, bit2 throttle closed, bit3 lambda control OK, bit4 idle switch closed, bit5 A/C compressor OFF, bit6 cat temp reached, bit7 no DTC stored (1 = attained) |
| 002 | RPM / load [%] / mean injection time [ms] / air mass [g/s] (MAF systems) |
| 003 | RPM / air mass [g/s] / throttle valve angle [%] / ignition angle actual [°KW] |
| 004 | RPM / voltage [V] / coolant [°C] / intake air temp [°C] |
| 005 | RPM / load / speed [km/h] / operating condition text (Idle, partial load, full load, SA = decel fuel cut-off, BA = acceleration enrichment) |
| 006 | RPM / load / intake air temp / altitude correction [%] (0 % = 0 m, -100 % = 10000 m) |
| 007 | (BDE) RPM / load / MAP [mbar] / brake booster pressure [mbar] |
| 008 | brake condition / supply voltage / vacuum pump for brake ON-OFF / brake booster pressure |
| 010 | RPM / load / throttle angle / ignition angle actual |
| 011 | RPM / coolant / intake air temp / ignition angle actual |
| 012 | distributor adjustment (crank tooth at cam flank) — n/a |
| 014 | misfire: RPM / load / misfire counter [n] / recognition "activated / locked" |
| 015 | misfire counters cyl 1 / 2 / 3 / recognition status |
| 016 | misfire counters cyl 4 / 5 / 6 / status |
| 017, 019 | cyl 7-9, 10-12 (n/a VR6) |
| 018 | misfire RPM/load window: lower RPM / upper RPM / lower load % / upper load % (all 0 when no misfire recognized) |
| 020 | knock control: ignition retard cyl 1 / 2 / 3 / 4 [°KW] ("always actual values") |
| 021 | retard cyl 5 / 6 / 7 / 8 |
| 022–025 | RPM / load / retard cyl 1,2 (022); 3,4 (023); 5,6 (024); 7,8 (025) |
| 026 / 027 | knock-sensor voltage cyl 1-4 / 5-8 [V] (amplifier factor included) |
| 028 | knock-sensor short-trip test: RPM / load / coolant / result text |
| 030 | O2 sensor status (2-bank): B1S1 / B1S2 / B2S1 / B2S2, each a 3-bit field `xxx`: bit0 control active, bit1 sensor ready, bit2 heater ON |
| 031 | O2 voltages [V] B1S1/B1S2/B2S1/B2S2; **linear-sensor variant**: lambda actual B1 / lambda specified B1 / lambda actual B2 / lambda specified B2 |
| 032 | O2 learning values (max): B1S1 idle [%] / B1S1 partial load [%] / B2S1 idle / B2S1 partial load |
| 033 | lambda control value: B1 control value [%] / B1 sensor voltage [V] / B2 control value / B2 voltage (linear variant: voltage before cat of the broadband sensor) |
| 034 / 035 | O2 ageing test before cat B1 / B2 (short trip): RPM / exhaust-cat temp / period length [s] (or "dynamic factor" for linear sensors) / result text `Test ON/Test OFF/B1-S1 OK/B1-S1 not OK` |
| 036 | post-cat sensor readiness: B1S2 voltage / result / B2S2 voltage / result |
| 037 / 038 | O2 sensors short trip B1 / B2: load / post-cat voltage / TV shift [ms] (or "D Lambda") / result |
| 039 | sensor exchange after cat: air mass / B1 voltage / B2 voltage / result |
| 040 | O2 heater resistance, combined wires: B1+2 S1 [Ω] / condition / B1+2 S2 [Ω] / condition |
| 041 | heater: B1S1 [Ω] / condition or duty [%] / B1S2 [Ω] / condition |
| 042 | heater: B2S1 [Ω] / condition / B2S2 [Ω] / condition |
| 043 / 044 | post-cat ageing B1 / B2: RPM / temp / voltage / result |
| 045 | NOx storage cat (n/a) |
| 046 / 047 | cat conversion test B1 / B2: RPM / cat temp / conversion measure / result `Cat B1 OK/not OK` |
| 048 / 049 | thermal cat diagnosis (BDE) |
| 050 | RPM actual / RPM specified / A/C request / A/C compressor (ON/OFF/decrease) |
| 051 | RPM actual / specified / driving range 0-6 (automatic) / supply voltage |
| 052 | RPM actual / specified / A/C readiness / rear window defroster |
| 053 | generator load: RPM actual / specified / voltage / generator load [%] |
| 054 | E-Gas: RPM / operating condition / accelerator pedal sensor 1 [%] / throttle angle [%] |
| 055 | idle control: RPM / idle control / idle learning value / conditions bits (A/C compressor, driving range, A/C readiness/defroster, steering to stop) |
| 056 | RPM actual / RPM specified / idle air control valve / conditions |
| 057 | RPM actual / specified / A/C compressor / duty cycle pressure receiver [%] |
| 058 | RPM / load / engine bearing 1 right / 2 left ON/OFF |
| 060 | **E-Gas adaptation**: throttle pot 1 [%] / pot 2 [%] / adaptation status counter [n] / text `ADP runs / ADP OK / ERROR` (ESB variant: pot / pot / operating condition / ADP text) |
| 061 | RPM / Ubat / throttle valve control actuation [%] / conditions bits |
| 062 | pot ratios U/Uref: throttle sensor 1 / sensor 2 / pedal sensor 1 / pedal sensor 2 (0→100 %) |
| 063 | **kick-down adaptation**: pedal sensor 1 / learned kick-down point / switch / result `ADP runs/ADP OK/ERROR` |
| 064 | throttle pot adaptation values: pot 1 lower / pot 2 lower / emergency air gap pot 1 / pot 2 [V] |
| 066 | cruise control: speed actual / switch bits / speed specified / lever bits (4- and 6-position variants, bit tables on the page) |
| 070 | EVAP purge test: opening degree [%] / lambda diag value / idle diag value / result `Fuel tank ventilation OK/not OK` |
| 071 | tank leak test: reed contact / DTC small-large leak / test status / result |
| 074 | EGR solenoid adaptation (gasoline): null position [V] / max stop [V] / pot value [V] / status |
| 075 / 076 | EGR short trip / EGR duty (n/a on the R32) |
| 077 / 078 | **secondary air test B1 / B2**: RPM / engine air mass [g/s] / SAI air mass [g/s] (or relative air mass for linear sensors) / result `Test ON/OFF/Abort/Syst. OK/not OK` |
| 080 | ECU id: manufacturer code+marking / manufacturing date dd.mm.yy / change status / test-stand no. / running no. |
| 081 | VIN / limit or serial no. / type test number |
| 082 | flash tool code / flash date / HW comp group+type / SW comp group+type |
| 090 | cam adjustment exhaust (continuous): RPM / duty cycle [%] / adjustment specified [°KW] / actual [°KW] (simple variant: RPM / adjustment ON-OFF / adj B1 / adj B2) |
| 091 | cam adjustment intake B1 (continuous): RPM / duty [%] / specified [°KW] / actual [°KW] |
| 092 | intake B2 |
| 093 | cam adaptation values: phase position intake B1 / intake B2 / exhaust B1 / exhaust B2 [°KW] ("displayed only when the phase adaptation was successfully concluded") |
| 094 / 096 | cam adjustment short-trip test intake / exhaust: RPM / phase position / result B1 / result B2 |
| 095 | **intake manifold change-over**: RPM / load / coolant / status `ein/aus` or `Off/step 1/step 2` |
| 097 | intake air change-over / snow flap |
| 098 | continuous exhaust cam B2 |
| 099 | lambda regulation shut-off (via basic setting): RPM / coolant / lambda reg [%] / lambda regulation ON-OFF (compatibility group) |
| 100 | readiness code: ready bits (1 = not concluded; bit0 cat, bit1 heated cat, bit2 AKF/EVAP, bit3 SL/SAI, bit4 A/C, bit5 O2 sensors, bit6 O2 heating, bit7 EGR) / coolant / time since start / OBD status bits (bit0 no warm-up possible, bit1 warm-up finished, bit4 ≥1 DTC, bit5 trip complete, bit6 driving cycle fulfilled, bit7 MIL ON) |
| 101 | fuel injection: RPM / load / mean injection time (0 at decel) [ms] / air mass [g/s] |
| 102 | RPM / coolant / intake air temp / mean injection time |
| 104 | start adaptation: start temp / temp adaptation factors 1,2,3 [%] |
| 105 | cylinder shut-off (n/a) |
| 107 | lambda regulation short trip: RPM / lambda reg B1 avg [%] / B2 avg [%] / result |
| 110 | full-load enrichment: RPM / coolant / avg injection time / throttle angle |
| 111–119 | boost pressure control groups (111 adaptation values per rpm range; 114 spec load/spec corrected/actual load/WG duty; 115 RPM/load/boost specified/actual [mbar]; 118 RPM/IAT/WG duty/pressure before throttle; …) — **n/a VR6** (R32 is naturally aspirated) |
| 112 | exhaust gas temperature: EGT B1 [°C] / enrichment factor B1 [%] / EGT B2 / factor B2 |
| 113 | RPM / load / throttle angle / air pressure [mbar] |
| 120 | ASR/FDR: RPM / specified torque ASR [Nm] / engine torque [Nm] / status |
| 122 | transmission: RPM / specified torque transmission [Nm] / engine torque [Nm] / "Engine intervention / no intervention" |
| 125 | CAN bus signals: Transmission / ABS / Instrument cluster / A/C (1 = present) |
| 126 | CAN: ADR / LWS (steering angle) / Airbag / Electrical wiring |
| 127 | CAN: All wheel / Level / Steering wheel |
| 130–137 | engine cooling: 130 map-cooling short trip; 131 engine-out temp / spec / radiator-out / thermostat duty; 132 radiator-out spec / Δ / heater pot / status bits; 134 oil temp / ambient / IAT / engine-out; 135 fan control test; 136 fan relays 1-4; 137 A/C requirements |

**D2. R32-specific verified usage**
- Fuel trims: "Block 032 in Engine. Shows your fuel trims. Will tell you if you have a bad MAF, vac leak, or over fueling (poss O2 sensor) issue" (R32 owner, src: R32OC-V). Ross-Tech: "The first field tells the fuel trim at idle (Additive). The second field tells the fuel trim at elevated engine speeds (Multiplicative). Negative values … too rich … Positive … too lean"; "Specifications for normal operation are usually somewhere near +/- 10%"; "zeros IN BOTH FIELDS indicates that either you just cleared codes … or something isn't working"; "check MVB 033 which should show values moving around" (real-time); MAF sanity: full-throttle run in one gear, "Group 002 usually shows air mass in g/s … peak airflow should be roughly 0.80 times your horsepower" (src: RT-FT). On the 2-bank VR6, 032 has all four fields (B1 idle / B1 partial / B2 idle / B2 partial) per the standard layout (src: RT-MB 030-049).
- Timing chain / cam adaptation on the 3.2 VR6 (label `022-906-032-BDB`): "blocks 208 & 209 'intake cam offset' & 'exhaust cam offset'. Anywhere between -8 & 8 is within tolerance" (src: TTF-CHAIN, post #3). Ross-Tech on the P0087 page, 3.6 L VR6 note: "Check Camshaft adaptations, must not exceed [-8.0 to +8.0]. Non-UDS (2006~2011) vehicles use Measuring Value Block group 208 and 209, field 3. UDS (2011 and newer) vehicles use Advanced Measuring Values, IDE00182 and IDE00184" (src: RT-P0087). Translated German-forum guidance quoted on TTF-CHAIN (re-checked verbatim): "ALWAYS reference blocks 90 & 91 when checking blocks 208 & 209"; "read when the engine is warm … minimum of about 60°C … at idle"; "Blocks 208 & 209 should be as close as possible to 0°, the spread should not exceed 3°. The absolute wear limit is 8° spread"; "Golf 5 R32 & Audi BUB only (intake adjustment range 52°/exhaust adjustment range 42°): For both blocks 90 & 91 the set-point value at idle is 0° … at a duty ratio of about 15.3%. The actual value should not be more than 0.5°"; "Around 11.25° deviation corresponds to a skip of 1 tooth" (src: TTF-CHAIN, post #4 — forum translation, treat the numbers as secondary). **Do not mix up with the Mk4 R32 figures on the same page** [added]: "Golf 4 R32 only (intake adjustment range 52°/exhaust adjustment range 22°): Block 90 (exhaust) set-point is 0° … Block 91 (intake) set-point is 22° between idle to about 1200RPM" — i.e. on the Mk4 the intake set-point is 22°, on the Mk5/BUB both are 0° at idle (src: TTF-CHAIN). Same thread, same post: "Values of -3° to -4° are usually associated with corresponding chain noise" [added].
- Misfire counters on KWP engines: "Group 014 – Misfire Recognition (Cylinders 1–3), Group 015 – (Cylinders 4–6)" per Ross-Tech's newer page (src: RT-MISFIRE) — note this is offset by one group from the standardized table (014 = summary, 015 = cyl 1-3, 016 = cyl 4-6 in RT-MB). Resolve on the car (Q4). "Reset Misfire Adaptions, clear Engine fault codes three times in a row, in 30 seconds of less" (src: RT-MISFIRE) — the P0300 page words the same procedure as "Clear the 01-Engine fault codes three times in a row in less than 29 seconds 'to remove the programed values'" [corrected: both wordings quoted; the "Not supported by all engine controllers" clause was not found on either re-fetched page and is dropped] (src: RT-P0300).
- Throttle body alignment (DBW engines using KWP-2000 or CAN, e.g. "Mk5 Golf 2.0T FSI"): key on, engine off → `[01-Engine] [Basic Settings-04] Group 060 [Go!]` → "Basic Settings: OFF" → `[ON/OFF/Next]` → "Basic Settings: ON", top-right "ADP RUN" → wait ~30 s → `[ON/OFF/Next]` off → `[Done, Go Back]`. Preconditions: no DTCs, "Battery voltage at least 11.5 V", throttle at idle position, coolant 5–95 °C, cycle ignition after clearing faults; the page's own protocol test: "Check to see if the engine speaks KWP-2000 or CAN by looking in the top left of the Open Controller Screen. UDS modules do not support conventional Measuring Blocks - 08 so that button will be grayed out" [added] (src: RT-TBA). For the UDS variant the basic setting is `IDE00754-Checking throttle valve adaptation` (src: RT-TBA).
- Kick-down adaptation (DBW, automatic): `[01-Engine] [Basic Settings-04] Group 063`, `[ON/OFF/Next]` on KWP/CAN engines, "Press accelerator pedal all the way to the floor … The 4th field of display should switch to ADP OK"; TCM side: `[02-Auto Trans] [Basic Settings-04] Group 000`, pedal to the floor 3–5 s, no on-screen feedback (src: RT-ATBS).
- Gasoline EGR valve adaptation: `[Meas. Blocks-08] Group 074` (`.1` min position V, `.2` max position V, `.3` pot voltage, `.4` adaptation status) → `[Switch to Basic Settings]` → "(Run) then it should change to (ADP OK)"; "For ECU's using ME 7.5, the coolant temp needs to be between 10 and 50 °C" (src: RT-EGR). (The R32 has no EGR valve; listed because the ME7 group exists.)
- Readiness on a KWP ME7 engine (APB 2.7T, same tool-flow as ME7.1.1): key on/engine off: clear codes; `060` TBA until "ADP OK"; `063` kick-down; engine idling: `071` leak test until "Syst.OK"; `070` EVAP until "EVAP OK"; `107` A/F control until "Syst.OK"; 1800–2200 rpm: `041`, `042` O2 heater until kΩ readings in fields 1 and 3; idle: `036` until "B1-S2 OK"/"B2-S2 OK"; 1520–2280 rpm: `034` "B1-S1 OK", `035` "B2-S1 OK"; idle: `037`, `038` "Syst. OK"; `043` "B1-S2 OK", `044` "B2-S2 OK"; 1880–2280 rpm: `046` "CAT B1 OK", `047` "CAT B2 OK"; idle: `077`, `078` secondary air "Syst. OK"; then `[Readiness]` must show no "Failed or Incomplete" (src: RT-RDY-APB). All of these are `[Switch to basic settings]` on the measuring-block group, i.e. KWP basic settings on the same group number.
- VCDS prints `Readiness: 0000 0000` for the R32 engine in both fetched scans (src: VTX-R32F) — the 8+8 readiness bit string is zero when all monitors are complete (semantics in `obd2.md`).

#### E. R32 fault codes — verified Ross-Tech wiki text (gasoline-relevant pages)
- `16684/P0300/000768 Random/Multiple Cylinder Misfire Detected`: causes intake leak, fuel supply, injectors, plugs/cables, coils, EGR stuck open, G40 cam sensor; "Check Misfire Recognition"; "Check Engine Speed Sensor (G28)"; "This DTC indicates that one or multiple cylinders are misfiring, but the ECU fails to identify the cylinder" (src: RT-P0300). P0301–P0306 are the cylinder-specific siblings (the page refers to "P0301 - P03??", src: RT-MISFIRE).
- `16795/P0411/001041 Secondary Air Injection System: Incorrect Flow Detected`: fuel pump relay J17, hoses carbonised, SAI pump V101, SAI pump relay J299, SAI solenoid N112 (src: RT-P0411).
- `P0491 Secondary Air Injection System: Bank 1: Insufficient Flow` (P0492 = bank 2 on the same page): fuse/relay, hoses to the combi valve, SAI solenoids, SAI pressure sensor, combi valves, "Secondary Air Injection ports in the cylinder head(s) plugged with carbon" (TPI 2033001 for 3.2 L Audi) (src: RT-P0491).
- `18447/P2015/008213 Intake Manifold Flap Position Sensor (Bank 1): Implausible Signal`: flap motor V157 / position sensor G336 "may be part of the same unit"; "Perform Output Tests/Basic Setting" (src: RT-P2015).
- `16485/P0101/000257 Mass Air Flow Sensor (G70): Implausible Signal`: MAF, leaks after MAF, restrictions, grounds; the page's logging advice reads verbatim "[meas. blocks-08], group 003 (3e gear, full throttle, from 1700-4000rpm)" (src: RT-P0101, re-checked in the HTML).
- `16471/P0087/000135 Fuel Rail/System Pressure: Too Low` (page covers 3.2 FSI / 3.6 VR6; not the port-injected BUB) (src: RT-P0087).
- P0128 (thermostat) and the lambda-heater/VVT codes were not fetched (see REPORTED).

#### F. 2012 Golf TDI Mk6 — EDC17CP14 (CJAA)

**F1. Protocol corroboration (KWP2000 over TP 2.0, numbered measuring blocks)**
- Ross-Tech's DPF page has three distinct procedures: "1.6l/2.0l R4 CR-TDI (**CAN**)" — uses `[Security Access - 16]` + `[Basic Settings - 04]` "Select Block for Regeneration while Standing" and **numbered MVBs 099/108/241/002**; versus "1.6l/2.0l R4 & 3.0l V6 CR-TDI (**UDS**)" — "Security Access is not typically needed", drop-down `Service regeneration of particle filter`, and named values "Particle filter, soot mass calculated/measured/time since last regeneration" (src: RT-DPF). VW's own Tech Tip for 2009-2013 Golf/Jetta TDI says "inspect Soot Load in MVB 241 and … KM since last re-gen in MVB 240/3" and explicitly "2012-2013 Passat does not have measured value block numbers" (the Passat NMS CKRA is the UDS EDC17 — sibling scan D) (src: VWTSB-DPF). The 2.0L CR TDI page: "Coding-II … is performed using the Coding-II function in vehicles with a CAN Protocol EDC. UDS Protocol control modules do not support this function" (src: RT-CRTDI). With sibling scan B (`03L-906-022-CBE.clb`, no ASAM/ROD line) this makes CJAA = KWP2000-over-CAN(TP 2.0), logical address per `addresses.md`.
- VCDS function numbers (the "[xx]" the wiki uses): `01 Control Unit Info, 02 Read Fault Codes, 03 Output Tests, 04 Basic Settings, 05 Clear Fault Codes, 07 Code Module, 08 Measuring Blocks, 10 Adaptation, 11 Login, 15 View Readiness` (src: RT-TDI). "Login Screen — Corresponds to VAG 1551/1552 function 11. The Login Function must be used on some (but not all) Control Modules before you can Recode or change Adaptation values. On others, it 'enables' certain features like cruise control" (src: RT-LOGIN). VCDS shows "Security Access - 16" for the same thing on newer modules (src: RT-DPF, RT-CRTDI).

**F2. Measuring blocks (numbered, CJAA/CBEA) — verified field assignments**

| MVB.field | content | source |
|---|---|---|
| 002.4 | coolant temperature (regen prerequisite > 70 °C) | RT-DPF |
| 099.2 | exhaust gas temperature before turbocharger | RT-DPF |
| 099.3 | EGT before particle filter | RT-DPF |
| 099.4 | EGT after particle filter | RT-DPF |
| 100.2 | temperature that rises to 350–600 °C during an active regeneration ("Monitor MVB 100/2") | VWTSB-DPF |
| 108.2 | particle filter soot mass (calculated) [g] — "Alternate group 241.2 if 108 is blank" | RT-DPF |
| 108.3 | particle filter soot mass (measured) [g] — alternate 241.3 | RT-DPF |
| 241.1 / .2 / .3 | ash load / calculated soot load / measured soot load ("MVB 241: Ash load, Calculated soot load, Measured soot load") | VWTSB-DPF; RT-DPF |
| 240.3 | distance in km since last regeneration ("MVB 240/3") | VWTSB-DPF |
| 240 (other fields) | an owner reads "group 240 gives me 27L, 550km, and 432 unknown units" (fuel since regen / km since regen / time since regen) | TDIC-DPF (owner post) |
| 105 | "# of requested regens" | TDIC-DPF (thread OP) |
| 108 or 241; "360,365 can also be used" | oil ash volume [ml] | TDIC-DPF (thread OP) |
| **097 / 099 / 105 / 108 / 240 / 241 field names** [added] | a 2009 Jetta TDI owner's VCDS group list ("VAGCOM DPF info"): `097 DPF Off-set`; `099 DPF Temperatures: xx xx xx`; `105: Requested regens / Temp / No Units`; `108 DPF: Oil Ash Volume / Particle filter carbon mass (spec.) / Particle filter carbon mass (act.)`; `240 Last Regen Information: Fuel Consumption since last regen / Mileage since last regen / Time elapsed since last regen`; `241 DPF Soot Load: DPF Oil Ash Volume [ml] / Soot Load (g) Calculated / Soot Load (g) Measured` — field numbering as listed (.1 .2 .3), consistent with RT-DPF (108.2/.3 = soot calc/meas) and VWTSB-DPF (241.1 ash, 240.3 km) | TDIC-334430 (owner post, label text as VCDS showed it) |
| **011.1 / .2 / .3 / .4** [added, verified from a 2011 CJAA log] | engine speed [/min] / boost pressure specified [mbar absolute] / boost pressure actual [mbar absolute] / N75 duty [%]. VCDS without labels printed `828 /min RPM / 1009.8 mbar Absolute Pres. / 999.6 mbar Absolute Pres. / 100.0 % Load` at idle; the poster (a VW tech using VAS 6052 and VCDS) annotates "1= engine rpm 2 = boost specified 3= boost actual , 4= duty cycle of N75 valve"; key-on-engine-off fields 2 and 3 read ~1000 mbar. The freeze frame of the same car's P0299 shows the same two pressures (`Absolute Pres.: 2356.2 mbar / 1948.2 mbar` at 3243 rpm, 101 km/h, Load 100 %) | VTX-CJAA-011 (`03L 906 022 PB / 03L 906 019 DA`, `R4 2,0L EDC G000AG 9045`, coding `0050078`); TDIC-441819 ("Group 11 … key on engine off field 2 and 3 should read 1000. Field 2 is what the ECM is asking for in boost and field 3 is what the engine is making") |
| **020** [added, partially verified] | rail pressure specified vs actual: a CJAA owner cranking a no-start engine reports "measuring block 020 the actual compared to the specified just stays at 8 or maybe sometimes bounces up to 50. But never higher than 80" (units/bar and field order not stated) | MTD-38651 (owner) |
| **Readiness-monitor MVBs 086 / 089** [added, VW document] | VW's own driving-cycle table for MY2009-2014 CBEA/CJAA: **MVB 089 = "not ready" bits** ("1 = not Ready, 0 = Readiness is set") and **MVB 086 = "ready" bits** ("0 = not ready, 1 = ready"), each field printed as an 8-bit string with bit 7 leftmost (`76543210`). 089/2 bit 4 = misfire monitoring; 089/4 bit 0 = NMHC catalyst (old SAE: catalyst); bit 1 = NOx/SCR after-treatment (old: heated catalyst); bit 3 = boost pressure system (old: secondary air); bit 5 = exhaust gas sensor (old: O2 sensor); bit 6 = PM filter (old: O2 sensor heater); bit 7 = EGR system. Ready-side counterparts: 086/1 bit 7 (EGR step 1), 086/1 bit 3, 086/1 bit 6 (EGR steps 2-3), 086/2 bits 7/6/4/5 (PM filter steps 1-4), 086/3 bits 0,1,4,2,3,5 and 086/4 bits 0,1,4,2,3,5 (exhaust-gas-sensor steps). Prerequisites in the same table: "LSU adaptation status MWB 41/4 and 136/4 = 1", "LSU needs to be active: MWB 43/3 and 138/3 = 1", "Airtemp. CACds MWB 7/3 > 0 deg Cel while coasting", "Engine temp. MWB 7/3 > 70 deg Cel" (sic — both quoted as 7/3), "MWB 100/2 > 300 deg Cel" (EGR monitor), "When MVB 100/1 > 575°C (1073°F)" (PM-filter monitor, MY2010 only) | VWTSB-RDY (readiness table only) |
| **046.2** [added] | coolant temperature ("monitor MVB 46/2. If temp drops below 87ºC replace the thermostat", 2009-2014 CBEA/CJAA) | VWTT-NOX |
| **100.1 / 100.2** [added] | 100/1 = an exhaust temperature that exceeds 575 °C during DPF regeneration; 100/2 = temperature > 300 °C for the EGR monitor and 350-600 °C during regen (VWTSB-DPF) | VWTSB-RDY, VWTSB-DPF |
| Malone's CR-TDI logging set [added] | "VAG TDI 2009+ Common Rail TDI: Log these blocks in 3rd gear: 001+003+004, 008+011+099" (block numbers only; field contents not given) | MALONE |
| 107.1/.2/.3 (CBBB RoW, "VCDS has no labels for it") | soot thresholds: no regen possible above / forced regen only above / regular regen starts at | MTD-P0299 (owner post) |
| 070.1 / 070.3 / 075.1-.4 | PD-TDI only: regen status bits (`xxxxxxx1` normal regen active, `xxxxxx1x` forced), regen counter/timer; EGT before turbo / before DPF / filter load % / EGT after DPF | RT-DPF (PD section; not CJAA) |

- Soot thresholds (CR-TDI CAN): "If either the calculated or measured soot mass is above 30g but below 40g you can initiate a regeneration while standing …; Once the values are above 40g (but below the max 45g) the regeneration while standing is no longer available and the regeneration while driving is the only way" (src: RT-DPF). VW: "start of normal driving regeneration is 18.9 grams"; "If soot load is between 2 grams and 39.9 grams normal regeneration can be performed. If soot load is over 39.9 grams … contact the Technician Helpline" (src: VWTSB-DPF).
- A 2010 Jetta CJAA owner: "Measuring block 108 was blank at blocks 2 & 3 so I had to use the alternate measuring block [241]"; "monitor blocks 99 & 241 … Block 99 shows all the temps in the exhaust system near the dpf … Before an actual regen started, the temps before and after the DPF were at most in the mid 300C range" (src: MTD-P0299).
- A fuller label set exists in VW ERWIN document `D3E802F8708-2_0L_TDI_Common_Rail_CBEA-CJAA.pdf` ("a more complete set of labels for the measured values for the CBEA/CJAA than what VCDS currently has"; "still stops short of 240/241") (src: TDIC-LBL) — not fetchable (paywalled); see Q6.

**F3. Service functions (CJAA, KWP/"CAN protocol" EDC17)**
- Regeneration while standing: prerequisites ignition ON, engine idling, tank ≥ ¼, N/P, parking brake, coolant > 70 °C (MVB 002.4), soot below spec (108.2/3 or 241.2/3), consumers ON, hood closed → `[Security Access - 16]` "Enter the Code shown by VCDS next to Adaptation Enabling (e.g. Regeneration while Standing)" → `[Basic Settings - 04]` "Select Block for Regeneration while Standing" → `[Go!]` → `[On/Off/Next]` if not automatically ON → "may take up to 30 minutes" → verify 099 + 108 (src: RT-DPF). The group number itself is only in the VCDS label file (Q7).
- Regeneration while driving: `[Security Access - 16]` (code shown next to "Regeneration while Driving") → `[Adaptation - 10]` "Select Channel for Regeneration while Driving" → `[Read]` → "Enter/Save 1 as new Value" → `[Save]`; drive > 60 km/h, 2000–2500 rpm, 10–15 min, EGT before turbo > 170 °C (099.2), before DPF > 150 °C (099.3), after DPF > 150 °C (099.4) (src: RT-DPF).
- Carbon-mass reset after DPF replacement: ignition ON engine OFF → `[Security Access -16]` code from balloon → `[Adaptation - 10]` "Carbon Mass (DPF Replacement)" (UDS: `[*IDE00275*] Particle filter initialization` or `[*IDE07903*] Adaptation of ash mass`) → "Save a new value of 1 … It's normal for that value to automatically change to 0 after it has been successfully saved" (src: RT-CRTDI).
- Injector quantity/voltage adjustment (IMA-ISA): `[01-Engine] [Adaptation - 10]` channels `071`..`074` = IMA-ISA value cylinder 1..4 (UDS: `IDE00263..IDE00266 Injector 1..4 correction value`); 7-character code from the injector using only `1,2,3,4,5,6,7,8,A,B,C,D,E,F,G,H,K,L,M,N,O,P,R,S,T,U,V,W,X,Y,Z`; `AAAAAAA` shown for an implausible value; `[Test]` `[Save]`; ignition OFF 10 s and re-verify; ECM rejects with "Request out of Range" if the wrong injector part number is fitted (src: RT-CRTDI).
- Fuel pump priming: `[01-Engine] [Basic Settings - 04]` group `035` ("if Available. Substitute using the details in the Special Notes section when needed") → `[Go!]` → `[ON/OFF/Next]` → "The electric fuel pump should run for 30 seconds"; "repeated no less than 3 times" after injector work; UDS variant "Transfer Fuel Pump (FP) test" from the drop-down (src: RT-FP, RT-CRTDI).
- Turbo actuator (VNT) adaptation on CBEA/CJAA [added]: engine running at idle → `[Engine] [Basic Settings]` → choose **"Charge Pressure Control"** from the drop-down → `[ON/OFF/Next]`; "The engine should idle up and cycle the actuator to open and close the vanes to find the new limits. Once the adaptation is complete the idle should return to normal" (src: TUNEZ-ACT — a tuner's one-page how-to; the group number behind the drop-down entry is not given, see Q7).
- EGR resets on a Mk6 CJAA via `[Adaptation]` (shown by VCDS as "Long adaptation") [added, REPORTED-grade — see R-E4]: "Channel 118 — Reset Exhaust Gas Recirculation (EGR) Low Pressure Valve (N345)" and "Channel 123 — Reset Exhaust Gas Recirculation (EGR) Valve (G212/N18)", each displayed with `Lambda x %, Bin Bits xxxxxxxx, Bin Bits xxxxxxxxx, Voltage x.xxx V`, stored value 0, "Putting in a 1 for the 'New Value' would reset the EGR but again, it required you to run Adaptation/calibration"; Basic Settings on that car offered "4 different EGR options" (src: TDIC-444852, thread "EGR Adaptation with VCDS on MK6 CJAA", post #4).
- G450 exhaust differential-pressure sensor adaptation on the CAN-protocol EDC: key ON engine OFF → `[Coding-2]` or `[Login-II]` → enter the code from the VCDS balloon → `[Do It!]` → ignition OFF 30 s; if not completed, five cycles of ignition ON 5 s / OFF 40 s. "Cruise Control Activation in addition to … G450 Adaptation is performed using the Coding-II function in vehicles with a CAN Protocol EDC" (src: RT-CRTDI). UDS variant: basic settings "Adaptation of diff. pressure sensor particulate filter" then "Resetting of learned values of difference pressure sensor" (src: RT-CRTDI).
- Readiness on UDS engines is a basic-settings routine "Automatic test sequence" with measuring values `IDE00450` operating instructions, `IDE00451` currently running routine, `IDE00030` status of actuator test, `IDE00727` test steps still to be performed, `IDE00021` engine speed, `IDE00025` coolant temperature; "This function is only available in UDS-based engine control modules. Non-UDS controllers use a different Readiness procedure" (src: RT-RDY-UDS) — i.e. not applicable to CJAA; for the KWP diesel the readiness bits are read with `[15]`/OBD mode 01 PID 01 (see `obd2.md`).

**F4. CJAA fault codes — verified wiki text**
- `18434/P2002/008194 Particle Filter Bank 1: Malfunction`: G450 exhaust pressure sensor or DPF; "Perform Emergency Regeneration"; "With CBEA and CJAA engines, the factory documentation may show the wrong part location for the Exhaust Pressure Sensor 1 (G450). This sensor is in a foil pouch just behind the oil cap" (src: RT-P2002).
- `18895/P2463/009315 Diesel Particle Filter: Excessive Soot Accumulation`: "Diesel Particle Filter 'full'"; "Perform Emergency Regeneration" (src: RT-P2463). VW TSB: high soot loads before regeneration can restrict the EGR filter; wipe test of the EGR filter; replace DPF and EGR filter together if sooty (src: VWTSB-EGRF).
- `16785/P0401/001025 EGR System: Insufficient Flow Detected`: on 2009-2012 NAR 2.0L CR TDI (CBEA, CJAA, CKRA) see TSB 26-13-03 / TPI 2031583 — a faulty exhaust pressure flap control module J883 may also set `P047F/001151 Exhaust Pressure Control Valve: Stuck Open`, `P0477 … "A" Low`, `P048A/001162 … Stuck Closed`, `P048B … Position Sensor/Switch Circuit`, `P048C … Range/Performance`; "Some TDI-CR engines have a filter for the EGR that can become restricted and cause a 'Insufficient Flow' code" (TSB 01 14 11 / 01 14 21, TPI 2034898); may accompany P2463 (src: RT-P0401).
- `16683/P0299/000665 Boost Pressure Regulation: Control Range Not Reached`: Diesel section: "2009-2014 VW NAR with 2.0 CR-TDI (CBEA/CJAA), TSB 21-14-03 or TPI 2026771 has several items to inspect and verify to factory design"; "Verify the mechanical part of the Exhaust Valve Control Module (J883) is not seized or binding" (src: RT-P0299; bulletin text in VWTSB-P0299 — titled "Engine Lacks Performance, Engine Warning Light ON, DTCs P2563, P2564, P0299 or P20D8 Stored in ECM" [added]: kinked/leaking vacuum hoses, leaking turbo vacuum diaphragm, "repair group 21 exhaust/turbo charging"). VCDS prints the same fault on a 2011 CJAA as `000665 - Boost Pressure Regulation: Control Range Not Reached / P0299 - 000 - - - MIL ON` with a KWP-era freeze frame `Fault Status: 11100000 / Fault Priority: 2 / Fault Frequency: 1 / Mileage: 3031 km / Time Indication: 0 / Date: 2002.14.27 / Time: 16:28:51` followed by `RPM / Speed / Load / Absolute Pres. / Absolute Pres. / Lambda / Lambda` [added — shows the CJAA freeze-frame field set and that VCDS can also print `P0299 - 001 - Upper Limit Exceeded`] (src: VTX-CJAA-011).
- `16485/P0101/000257 MAF (G70) Implausible Signal`: "It is not uncommon for a TDI to set Implausible Signal Mass Air Flow Sensor (G70) faults when the engine performance is reduced due to a mechanical problem" (fuel pump/filter, restrictions, cam/lifter) (src: RT-P0101).
- `16471/P0087/000135 Fuel Rail/System Pressure: Too Low`: "Check Measuring Values for Fuel Pressure", low-pressure leaks, fuel filter and in-pump filter, pump delivery, injector leak-back (src: RT-P0087).
- `18447/P2015/008213 Intake Manifold Flap Position Sensor (Bank 1): Implausible Signal`: V157 motor / G336 sensor, "Perform Output Tests/Basic Setting"; special software note for BRM PD (src: RT-P2015).
- An owner's CJAA with a boost leak logged `P0299, P0665 & P2459` (P2459 = DPF regeneration frequency) and later P0401 (src: MTD-P0299).

#### G. DQ250 / 02E (both cars) — verified

**G1. Identity and coding**: R32 `02E 300 011 CC / 02E 927 770 AD`, `GSG DSG 082 1405`, coding `0000020`, label `02E-300-0xx.lbl` (src: VTX-R32F); sibling scan C (2010 Jetta TDI DSG) `02E 300 052 / 02E 927 770 AJ`, `GSG DSG AG6 440 1920`, coding `0000020`. Ross-Tech: "When replacing this Mechatronic unit, simply copy the coding from the original Auto-Scan … If the original Coding is unknown, coding information can be found in the pop-up balloon within the VCDS [Coding-07] function" (src: RT-02E) — the digit meanings are not published on the page.

**G2. Basic-settings (clutch adaptation) sequence** (src: RT-02E, verbatim order; the VAS-PC text on AUDIF-DSG gives the same channel numbers):
Prerequisites: "Fluid Temperature 30...100 °C (86...210 °F), see Measuring Blocks, Group 019 (Fluid Level needs to be correct!)"; selector in P; ignition ON; engine idling ≥ 1 min; brake pedal held throughout; no throttle; cruise control OFF.
1. `[02 - Transmission] [Basic Settings - 04]` **Group 061** "Transmission Tolerances (Engaged Calibration)" → `[Go!]` → wait until Basic Settings switches to ON and numbers stop moving ("may take one minute"; the box makes noises).
2. **Group 060** "Transmission Tolerances (Synch. Point. Measurement)" → `[Go!]` → wait for ON.
3. Clutch adaptation: software version `< 0800` → **Group 062** `[Go!]` `[ON/OFF/Next]`; version `>= 0800` → **Group 067** `[Go!]` `[ON/OFF/Next]` (VAS-PC: "Channel 67 - The values for the clutch adaption are reset"; "A clutch adaption at standstill is not necessary here").
4. **Group 068** "Reset Values (Clutch Safety Function)".
5. **Group 065** "Reset Values (Pressure Adaptation)" (VAS-PC: "automatic main pressure adaption … reset to defaults").
6. **Group 063** "Reset Values (Steering Wheel Paddle Installation)" (VAS-PC: resets paddle fitting info to "not recognised").
7. **Group 069** "Reset Values (ESP & Tip Cruise Control Installation)".
8. `[Done, Go Back]`, ignition OFF 10 s, ON; `[Fault Codes - 02]` check/clear; defined test drive: Tiptronic from standstill to 6th, ~5 min each in 3rd/5th and 4th/6th, 1200–3500 rpm (TDI owners: 2000–2500 rpm sufficient), one sharp braking then full-throttle in D (oil return check), evaluate creep. "Some modules do not require the use of the [ON/OFF/Next] button … let the selected group and procedure finish on its own." Early 8N TT 062 may report `[18 | 18 | .285 | .24]` when finished. The VAS-PC text gives a slightly different defined test drive [added]: "Gearbox temperature > 30°C < 100° C … tiptronic off standstill up to … 6th gear. Drive repeatedly in each of 3rd, 4th, 5th and 6th gears for at least 2 minutes under constant load. Engine speed window for all gears 1500 - 3000 rpm" (src: AUDIF-DSG).
- The R32's `GSG DSG 082 1405` has SW version `1405` ≥ 0800 → **group 067** branch; verify on the car (Q9).

**G3. Measuring blocks**
VCDS labels as logged on a DQ250 (src: AUDIF-DSG, VCDS log "Group 006 … Group 018", field order .1–.4 with units as printed):

| Group | .1 | .2 | .3 | .4 |
|---|---|---|---|---|
| 006 | Selector Lever Position (`P`) | Valve current clutch valve 1 [A] | Safety valve 1 (N233) [%] | Main pressure valve current [A] (e.g. 0.840) |
| 007 | Selector Lever Position | Valve current clutch valve 2 [A] | Safety valve (N371) [%] | Main pressure valve current [A] |
| 010 | Accelerator pedal angle [%] | Kick-Down switch | Engine torque [Nm] | Engine torque (loss) [Nm] |
| 013 | Solenoid current clutch valve 1 [A] | Safety Valve 1 [%] | Solenoid Valve 1 (N88) [%] | Solenoid Valve 2 (N89) [%] |
| 014 | Solenoid current clutch valve 2 [A] | Safety Valve 2 [%] | Solenoid Valve 3 (N90) [%] | Solenoid Valve 4 (N91) [%] |
| 015 | Gear Selector 1-3 (raw 0..1023, e.g. 519) | Gear Selector 2-4 | Gear Selector 5-N | Gear Selector 6-R |
| 016 | Travel Distance Gear Selector 1-3 [mm] | 2-4 [mm] | 5-N [mm] | 6-R [mm] |
| 017 | Synchronous travel path 3rd gear [mm] | 2nd gear | N gear | R gear |
| 018 | Synchronous travel path 1st gear [mm] | 4th | 5th | 6th |

Factory list "Measured value blocks for control unit -J743 (DQ250 - 6Q)" (VAS-PC text posted on AUDIF-DSG; ranges as given):

| Block | fields |
|---|---|
| 1 | brake light switch (Brake/none) / brake test switch / shift-lock status (PN active/inactive) / speed 0..255 km/h |
| 2 | selector lever position (P,R,N,D,S,TT,PL,MI,ZS,ER) / plausibility-checked position / error byte from selector lever (0 inactive, 1 active) / engaged gear (P,R,N,D; Tiptronic 1..6) |
| 3 | lever position / checked position / Tiptronic Up on wheel / Tiptronic Down |
| 4 | lever position / direction of travel (Forward, Reverse, Not recognised) / output speed 1 (0..4080 rpm) / output speed 2 |
| 5 | lever position / start enable / supply voltage 1 (0..25.5 V) / supply voltage 2 |
| 6 | lever position / valve current clutch valve 1 (0..1.530 A) / duty cycle safety valve 1 (0..100 %) / main pressure valve current (0..1.530 A) |
| 7 | lever position / valve current clutch valve 2 / duty safety valve 2 / main pressure valve current |
| 8 | input speed (0..8160) / input shaft speed 1 / input shaft speed 2 / output speed (0..4080) |
| 9 | engine speed / input speed / output speed / output speed from CAN |
| 10 | accelerator pedal angle 0..100 % / kick-down switch / engine torque (-100..410 Nm) / engine torque loss (-50..205 Nm) |
| 11 | input shaft speed 1 / specified clutch torque K1 (-600..600 Nm) / valve current clutch valve 1 / **actual pressure clutch 1 (-327.68..327.67 bar)** |
| 12 | input shaft speed 2 / specified clutch torque K2 / valve current clutch valve 2 / actual pressure clutch 2 |
| 13 | specified current clutch valve 1 / duty safety valve 1 / duty gear actuator valve 1 / valve 2 |
| 14 | specified current clutch valve 2 / duty safety valve 2 / duty gear actuator valve 3 / valve 4 |
| 15 | travel measurement gear actuator 1-3 / 2-4 / 5-N / 6-R (0..1023 raw) |
| 16 | travel gear actuator 1-3 / 2-4 / 5-N / 6-R (-12.7..12.8 mm) |
| 17 | synchronous travel 3rd / 2nd / vacant / R (-12.7..12.8 mm) |
| 18 | synchronous travel 1st / 4th / 5th / 6th |
| **19** | **temperature standard / temperature reserve / temperature clutch (-250..250 °C) / empty-gas (idle) info** |
| 30 | lower adapted clutch pressure K1 / lower from microslip / upper from microslip / upper from macroslip (0..1.275 A) |
| 31 | same for K2 |
| 32 | current lower/upper pressure point clutch 1, clutch 2 from current-to-pressure adaptation (0..1.275 A) |
| 33 | main pressure adaption success/abort counters K1, K2 (0..65535) |
| 40 | flash checksum (0..255) |
| 41 | parameter set designation |
| 42–44 | mantissa of software parameters 1..10 |
| 45–47 | exponent of software parameters 1..10 |
| 48 | software designation DQ250 |
| 49 | min/max voltage at UH1, UH2 |
| 50 | selector lever part number (chars 1-12 part number, 16 programmability, 18-19 program version, 21-22 data level) |
| 51 / 52 / 53 [added] | display of internal error ID no. 0-3 / 4-7 / 8-11 (0..65535) |
| 60 / 61 [added] | "Data for basic calibration": status gear-actuator adaptation (synchronous 0-13, engaged 129-141) / sub-status (synchronous 0-3, engaged 128-137) / gear actuator index (0 = GS_13, 1 = GA_24, 2 = GA_5N, 3 = GA_6R) / gear actuator side (0 neutral, 1 side A = negative travels 3-2-N-R, 2 side B = positive travels 1-4-5-6) — i.e. what basic-settings groups 060/061 display while running |
| 62 [added] | status at standstill shaft 1 / shaft 2 (0 OFF, 1 EMPTY, 2 ENGAGE, 3 REFERENCE, 4 START VALUE, 5 RAMP, 6 CONTROL, 7 DONE, 8 CALCULATION, 16 MVB_INACTIVE, 17 MVB_WAIT, 18 MVB_RESULT, 19 MVB_ABORT_TESTER, 32 MVB_EMERGENCYRUNNING, 33 MVB_N_ENGINE, 34 MVB_ENGINE_NOK, 35 MVB_TEMPERATURE, 36 MVB_BRAKE, 37 MVB_ACCELERATORPEDAL, 38 MVB_V_VEH, 39 MVB_SELECTORLEVER, 40 MVB_M_ENGINE_LOSS, 41 MVB_M_ENGINE_MAX, 64 MVB_SYSTEM, 65 MVB_CLUTCH_NOK, 66 MVB_SIG_UNSTABLE, 67 MVB_DMMOT_CONTROL) / lower adapted clutch point K1 / K2 (0..1.275 A) — the clutch-adaptation group of SW < 0800 |
| 63 [added] | fitting info steering wheel paddles (0 not recognised / 1 recognised) / vacant ×3 |
| 64 [added] | number of exceedings of permissible centrifugal oil temperature (0..255) |
| 65 [added] | correction values main pressure adaption: low / high pressure on K1, low / high on K2 (-327.68..327.67 bar) |
| 66 [added] | adapted flags gear actuator 13 / 24 / 5N / 6R (0 inactive / 1 active) |
| 67 [added] | clutch adaption values for K1 / K2 (0..1.275 A) / vacant / vacant — the SW ≥ 0800 clutch-adaptation group |
| 68 [added] | clutch adaption values: lower current point adaption K1 / K2 (0..1.275 A) |
| 80 / 81 / 82 [added] | "Control unit identification": 80 = manufacturer works number and identifier hhh-kkk (7), date of manufacture dd.mm.yy (8), manufacturer modification status 12345678 (8), test status pppp (4), serial nnnn (4); 81 = chassis number (17), module/serial no. (14), type test number (7); 82 = flash tool code (13), flash date dd.mm.yy (8), hardware module (3) + sort key (2), software module (3) + sort key (2) — same scheme as the engine's standardized groups 080-082 |
| 125 / 126 [added] | CAN devices: engine / ABS / dash panel insert / selector lever (0 = no message, 1 = message OK); 126 = gateway / steering column module / vacant / vacant |
| 225 / 226 [added] | number of timeouts (0..255, "multiple of EMC timeout"): engine / ABS / dash panel / selector lever; 226 = gateway |

- Ross-Tech staff (TDIC-DSGT, Dana @ Ross-Tech): "the DSG should show readings from 3 sensors in that group [019]: Control Module Temp (G510), Clutch Oil Temp (G509), Transmission Fluid (G93)"; an owner saw "three numbers … around 55 to 58" and needed the brake pedal pressed for the block to populate.
- Group 019 is the temperature reference for the fluid-level/adaptation procedures (src: RT-02E).

**G4. DQ250 fault codes (as printed by VCDS / published lists)**
- `P189C/006300 - Function Restriction due to Insufficient Pressure Build-Up`: symptom "Unable to complete Basic Settings, fault will not clear"; causes wiring/connections/fuses/"Faulty Mechatronic Unit (V401-Hydraulic pump motor)" (src: RT-P189C — the page itself scopes the pin-9 check to "the 7-Speed Dual Clutch Transmission (DSG/0AM) … Pin 9 of the 25-Pin connector"; that V401 is a DQ200-only part and that the DQ250's pump is engine-driven is background knowledge, not on the page [downgraded wording]).
- `P189A - Clutch 1: Clearance too Small` is "0AM Transmissions" only (src: RT-P189A).
- VCDS prints DSG faults in the 5-digit + P-code form, e.g. `18115 - Interference in Mechatronic Module / P1707 - 013 - - Intermittent` and `17150 - Shift Solenoid 4 (N91) / P0766 - 000 - Open or Short to Ground - Intermittent` (src: MTD-DSG).
- Published DQ250 list (secondary, repair shop): `P0701 unit faulty; P0716 (17100) input speed sensor G182 implausible; P0722 (17106) output speed sensor G195 no signal; P0731..P0735 (17115..17119) gear 1..5 incorrect ratio; P0746 (17130) pressure control solenoid 1 N215; P0751 (17135) shift solenoid 1 N88; P0756 (17140) N89; P0761 (17145) N90; P0766 (17150) N91; P0771 (17155) N92; P0776 (17160) pressure control solenoid 2 N216; P1604 (18012) ECU defective; P1740 (18148) clutch temperature monitoring G509; P1746 (18154) supply voltage for solenoid valves; P1824 (18232) pressure control valve 3 N217; P1829 (18237) pressure control valve 4 N218; P1835 (18243) pressure control valve 5 N233 short to plus; P2723 (19155) N233 short to earth; P2732 (19164) pressure control valve 6 N371` (src: ECOT). The 5-digit numbers follow the VAG rule in `dtc_db.md` §C.
- Solenoid resistance "K1 and k2 pressure control solenoids need to read 4.5-6 ohms"; "DSG output test vagcom requires car running" (src: VTX-SOL, owner posts — secondary).

#### H. Haldex Gen2 (address 22) — verified
- Ident/coding: see §A. Faults seen on Mk5 Gen2 units: `01073 - Clutch Pressure System / 002 - Lower Limit Exceeded - Intermittent` and `01155 - Clutch / 003 - Mechanical Failure - Intermittent` (R32, src: VTX-R32FWD, VTX-HLDX); `00526 - Brake Light Switch-F / 008 - Implausible Signal` in the AWD module (src: VTX-HLDX); `00448 - Haldex Clutch Pump (V181) / 014 - Defective` (Mk5 TDI 4Motion, src: TDIC-HLDX), `011 - Open Circuit / Intermittent`, `002 - Lower Limit Exceeded` (quoted by an 8J TT owner from other people's scans while his own OBDeleven read `00448 - Haldex clutch pump Faulty`, `01324 - All wheel drive control module Please read DTC`, `01316 - Brake control module Please read DTC`; he also notes "I can't find a specific Ross Tech Wiki page for the 00448 fault code" [corrected attribution], src: TTF-HPUMP); companion ABS fault `01324 - Control Module for All Wheel Drive (J492) / 013 - Check DTC Memory` (src: TDIC-HLDX); `01316 - Brake control module` in the AWD module when the ABS has a fault (src: TTF-HPUMP). An R32 owner's 01073 "did mean low oil" (src: R32OC-H).
- Measuring blocks on a Gen2 (8J TT, VCDS): "I can see the Haldex voltage (12.4v), the temperature, the status of all of the switches, the fact that it's communicating with the ABS and the ECU, and also the status of the pump (which shows as off with the ignition off and on with the ignition on)" (src: TTF-HTEST) — group numbers not quoted (Q10).
- Output tests on Gen2: a sequential test — "when I go to output tests in vcds I have sequential test that enables the pump motor, engages the clutch, then disengages the clutch, finally switching pump motor off, but I can't select and run individual steps of it" (1K0 907 554 A; the newer label for version B adds basic settings such as "motor training") (src: TDIC-HLDX). VCDS step names: "Haldex Clutch Pump (V181) Activate" then "All wheel drive (AWD) Clutch Engaged" (older VCDS) / "Precharge Pump OFF, Precharge Pump ON, AWD Clutch Engaged, AWD Clutch Disengaged, Precharge Pump OFF, AWD Clutch Disengaged" (newer VCDS) (src: VTX-GEN4, Gen4 but same VCDS flow); an 8J Gen2 owner's first step shows "Precharge pump off" and must be advanced with `[Next]` (src: TTF-HTEST). Oil-service use: run the pump 1 min, engage the clutch 3 min, repeat 3× to purge air (src: VTX-GEN4).
- Gen4 (for the label-file family, not the R32): groups `125` (.0 CAN-Data Bus Communication, .1 Engine J623, .2 Transmission J217, .3 ABS J104, .4 Instruments J285) and `126` (.0 CAN, .1 Steering Angle Sensor G85, .2 CAN-Gateway J533), "1 = Active on the network"; monitoring groups 005/006 (digital signatures), 010–012 (CAN messages), log group 004 on a road test; Basic Settings group 051 after parts replacement (src: ATI-G4).

#### I. Gateway (19) and instrument cluster (17)
- Mk5 gateway installation list = long coding (layouts verified in `addresses.md` §E). No open source documents a `1A 9F` reply layout (GitHub/Web searches this session: none) — remains Q11.
- Mk5 cluster `1K6 920 974 D/DX` (KWP, `.lbl`): coding `00??x0x` options (+01 brake pad warning, +02 seatbelt warning, +04 washer fluid warning, +16 sedan), `00xx?0x` country (1 EU, 2 USA, 3 CDN, 4 GB, 5 JP, 6 SA, 7 AUS), `00xxx0?` distance impulse number (1=22188, 2=22076, 3=21960, 4=21848, 5=22304, 6=22420, 7=22532); **`13861` = "Adaptation Enabling"** (the page lists it under a heading "Security Access", i.e. the VCDS `[11-Login]`/`[16]` code) [corrected heading]; adaptation channels: `002` service reminder (0 = not due, 1 = due; save 0 to reset), `003` consumption correction (85…115 %, formula `new = old * calculated / displayed`), `004` language (1 DE, 2 EN, 3 FR, 4 IT, 5 ES, 6 PT, 7 none, 8 CZ), `009` mileage/odometer (1 = 10 km or 10 mi; only once before 100 km), `022` production mode, `030` fuel gauge (standard 100, 120…136, 1 Ω steps), `035` speed threshold (dynamic oil pressure, 250 rpm steps), `038` oil minimum detection, `039` oil level sensor (TOG) installed, `040` mileage since service (1 = 100 km), `041` time since service (days), `042` min distance to service (1 = 1000 km), `043` max distance to service (1000 km), `044` max time to service (days; 365 fixed, 730 flexible), `045` oil quality (1 fixed, 2 LongLife), `046` total consumption, `047` soot entry, `048` thermal load, `049` min time to service (days) (src: RT-1K-KOMBI). The R32's cluster coding `0007203` → options 7 (brake pad + seatbelt + washer), country 2 (USA), impulse number 3 (sibling scan A; decoded with this table).
- Mk6 cluster `5K0 920 972 C` (UDS): VCDS adaptation entries are named, not numbered: `ESI: Resetting ESI` (choose "Reset"), `FIX: Distance covered since last mileage-dependent inspection` (= 0), `FIX: Time since last time-dependent inspection` (= 0), `SID: maximum value of distance to service` / `SIA: …`, `SID: maximum value of time to service`, `ESI: Coding of Service Interval Extension (SIE)`, `Oil Quality`, `Staging`; "If an Adaptation Error warning indicating that the control module is Uninitialized you must let VCDS write defaults to the WSC, Importer and Equipment numbers before the value can be changed" (src: RT-5K-KOMBI, RT-5K-TWEAKS, RT-SRI). Ross-Tech: "On the latest cars using UDS/ODX … the SRI Reset function may only show choices for oil change 'Reset ESI / OIL (North America)…' and time based service 'Reset FIX&ESI / INSP (North America)…'" (src: RT-SRI-TOUR). The underlying UDS DIDs are not published anywhere fetched (Q12).

---

### Reported / unverified (confidence)

R-A. **ME7.1.1 BUB engine coding `0000178`** digit meaning: not documented on any fetched page (search this session found scans only). Low confidence memory: Mk5 ME7/MED9 engine coding is `0 0 0 0 1 7 8` with the last two digits a market/transmission/traction variant selector; do not decode. Confirm: read the VCDS "Coding" balloon text from `022-906-032-BDB.lbl` on the car.

R-B1. **ME7Logger `HM0 / HM2-0x10`** = KWP2000 header mode: `HM0` = header without address bytes (format byte with length only), `HM2` = header with target/source address bytes, physical target 0x10; `HM3-func(0x31)` = functional target 0x31; and **`SLOW-0x11` = 5-baud init to K-line address 0x11** [downgraded from VERIFIED: the thread says only "slowinit to 0x01" for another image and prints `try connect slow(11)`; it never states the number is the 5-baud address]. Medium (consistent with the ME7Info connect overview wording "slow (0x01)/(0x31)/(0x33)", "HM2/phys(0x10)", "HM3/func(0x31)", with the NEF-19082 trace using a length-only header (`02 1A 94 B0`) under `HM0`, and with ISO 14230-2 address modes). Confirm: an ME7Logger K-line trace of the init phase.

R-B2. [promoted — the byte facts now sit in VERIFIED §B; the repo is `derpston/me7`, not "pylibme7" (that path 404s)]. What **remains unverified**: that `B7 03 …` / `B7` is what ME7Logger itself sends after installing its bootrom-specific handler (prj says the handler redirects the DDLI buffer; `B7` is not an ISO 14230 service id), and whether the `0x40` MSB flag and the `0xF7` reply byte hold on any ECU other than the author's. Medium. Confirm: a K-line trace of ME7Logger's logging phase (any ME7.x car), compare with `B7`.

R-B3. ME7Logger's K-line start-up needs a development session (`10 86`) which on ME7.1.1 is refused (`7F`) until a level-1 access is done (NEF-19082 poster, Jan 2023). Medium. Out of scope beyond noting the gate.

R-C. **VR6-specific ME7 variables** not present in the 2.7T file: `wnwse_w/wnwe_w` exist (intake cam), exhaust-cam names `wnwa_w/wnwsa_w` (memory, medium); intake-manifold flap status `B_sa*`/`saugrohr` names unknown; secondary air `B_sls`, `mssls` (memory, low). Addresses for the R32 Mk5 image are unknown to every open source (ME7Info cannot parse it). Confirm only with a disassembly/A2L of `022906032KR`.

R-D1. VCDS group numbers on the R32 beyond those verified (the standardized table in §D1 was re-checked group by group against the re-fetched m_blocks pages; the misfire layout there is unambiguous: 014 = RPM / load / misfire counter / status, 015 = counters cyl 1/2/3, 016 = cyl 4/5/6, 017 = cyl 7/8/9): `001` (rpm/coolant/λ B1/λ B2), `002`, `003`, `004`, `005`, `020/021` (knock retard cyl 1-4 / 5-6), `030-033`, `077/078` (secondary air), `090/091`, `093/094`, `095` (manifold flap), `099`, `100`, `112`, `120`, `122`, `125-127`, `134` follow the standardized layout — high confidence that ME7.1.1 (2008) uses the standard numbering because the label file is a generic `022-906-032-BDB.lbl` and the standard says "engines from about 1999-2000"; but Ross-Tech's misfire page (014 = cyl 1-3) vs the standard (015 = cyl 1-3) shows per-ECU shifts exist. Confirm: Q4.

R-D2. Engine **Login** for adaptation on ME7 (`[11]`): memory says `12233` is the generic Bosch adaptation login on many ME7 gasoline ECUs; low. Confirm: VCDS balloon on `[11-Login]`.

R-D3. **P0128** "Coolant Thermostat (below regulating temperature)" is a common Mk5 R32 code (stuck-open thermostat; the 3.2 uses a map-controlled thermostat, groups 130-132); **P0011/P0014/P0021/P0024** cam-position "over-advanced/retarded" codes map to the 208/209 wear check; **P0030/P0036/P0050/P0056** O2 heater control circuit codes (B1S1/B1S2/B2S1/B2S2); **P2004/P2005** intake manifold runner control stuck open/closed; **P0171/P0174** system too lean B1/B2; **P1340**-style cam/crank correlation on VAG. Generic SAE meanings high, R32-specific prevalence medium (memory; DTC text tables are in `dtc_db.md`).

R-E1. **CJAA numbered groups not verified** [partly promoted: `011` = rpm / boost specified / boost actual / N75 duty is now VERIFIED from a 2011 CJAA log; `020` = rail pressure specified vs actual is verified as a group, field order and units not; `086/089` readiness bits, `041.4/136.4`, `043.3/138.3`, `007.3`, `046.2`, `100.1/.2` are VERIFIED from VW documents]. Still memory/typical EDC17 label files: `001` (rpm / injected quantity / coolant? / …), `003` (rpm / MAF specified / MAF actual / EGR duty), `004` (rpm / start of injection / …), `008` (rpm / torque limits …), `010` (rpm / MAP? / …), `013` (injector smooth-running corrections cyl 1-4, mg/stroke — a web-search summary of a TDIClub thread gives "-2.0 to +2.0 mg/R", not opened), `018`/`019` (glow plug status/current), `020` field order (specified first or actual first?), `023` (fuel metering valve duty), `090`-series DPF. Confidence low-medium for the exact numbers; the ERWIN PDF (TDIC-LBL) is the authority; Malone's CR-TDI set `001+003+004, 008+011+099` says which groups tuners log but not their fields. Confirm: Q6/Q7.

R-E2. **P0671–P0674** = "Cylinder 1..4 Glow Plug Circuit" (SAE generic) with VAG text "Glow Plug Cyl.1 (Q10) … Cyl.4 (Q13): electrical malfunction"; glow plug module J179/J52 feed; high (generic), not fetched. **P0670** glow plug module control circuit. **P2008** = "Intake Manifold Runner Control Circuit/Open (Bank 1)"; on CJAA the relevant flap codes are `P2015` and `P2004/P2005`. **P2459** = "DPF Regeneration Frequency" (seen in MTD-P0299 as the owner's code; meaning from memory, medium-high).

R-E3. The "Regeneration while Standing" **basic-settings group** on CBEA/CJAA label files is around **021** and the driving-regen adaptation channel around **062** in older label files (memory from forum posts; low; a web search this pass found nothing citable). The actuator adaptation is the drop-down entry "Charge Pressure Control" (VERIFIED name, unknown number). Confirm: Q7 by reading the `.clb` balloon or ODIS.

R-E4. [added] **EGR reset adaptation channels `118` (N345 low-pressure EGR valve) and `123` (G212/N18 EGR valve)** on a Mk6 CJAA — quoted in §F3 from a TDIClub post whose author's signature shows a 2006 Jetta (BRM) while the thread and the post text are about "the MK6 platform"; the channel numbers therefore need the owner's own label file to confirm. Medium. Confirm: open `[Adaptation]` on the 2012 Golf's engine and read channels 118/123 (read only).

R-F1. DQ250 **output tests** (`[03]`) on the 02E: label-driven sequential actuator test (solenoids N88-N92, N215/N216, N217/N218, N233/N371 click test) requiring engine running; content unverified (VTX-SOL only says "requires car running"). Low. Confirm: Q13.

R-F2. **P17BF/006079 "Hydraulic Pump: Play Protection"** and the accumulator-crack story are DQ200 (0AM) items; on the DQ250 the frequent mechatronic faults are the solenoid/valve set in §G4 plus `P173x` clutch-torque-plausibility codes (`P173A/P173B` … are 0AM clutch-position codes per the sibling-cached Ross-Tech thread "0AM DSG Fault codes P173A P173B …"). Medium. **P1735** is not a known VAG DSG code (memory). Confirm: read the R32 TCM fault memory on the car.

R-F3. DQ250 **TP 2.0 logical address 0x02** — sibling `addresses.md` rates medium-low; the `02E-300-0xx.lbl` KWP module should answer `1A 9B` on that channel (Q8).

R-G1. Haldex Gen2 **part numbers**: early Mk5 R32 / 8P A3 used `0AY 907 554` with component `Haldex 4Motion 0043`, later `1K0 907 554 x` `01xx` (web-search summary of vwvortex scans, not opened; the verified members of the `1K0 907 554` family are now A, C, F, L — §A). Medium. Note that a later `0AY-907-554-V1.clb` / `0BR 907 554 A` / `Haldex 4Motion 3016` unit exists on 8J TTs (VERIFIED, TTF-3016) — a `.clb` module, not the Gen2 `.lbl` family. Haldex Gen2 TP 2.0 logical `0x0A` — sibling-verified (OpenHaldex-C6).

R-G2. Gen2 Haldex measuring groups (memory, from the `1K0-907-554.lbl`): `001` supply voltage / oil temperature / pump status / clutch status; `002` wheel speeds; `003` pump current & clutch current; `005/006` switch & CAN status bits; `125/126` CAN participants. Low-medium — two further web searches and three more Gen2 threads this pass (MK5GTI-H, TTF-3016, TTF-HTEST) yielded no group numbers, only "voltage (12.4v), the temperature, the status of all of the switches … communicating with the ABS and the ECU … status of the pump". Confirm: Q10.

R-H1. **KWP measuring-block read over TP 2.0**: verified skeleton from SEISHUKU (fetched): request payload `21 <group>` (`0x21 readDataByLocalIdentifier`, "LocalID = Local Identifier parameter (RLOCID)"), positive reply `61 <group>` followed by the field data, which the code decodes as triples `(formula id f, a, b)` with `_DecodeValue(f,a,b)`: `0x01` RPM `a*b*0.2`; `0x05` °C `a*(b-100)*0.1`; `0x60` mbar and `0x7E` grams `a*b*0.1`; default raw `a*256+b`. The worked frame example in that source's comment is internally inconsistent (overlapping bytes), so it is not reproduced. The full formula-id table (1..70 and the 0x60+/0x7E+ ids used over TP 2.0) is the KWP sheet's domain (nefarious topic 22, sibling-cached). Medium-high that the same `21/61` scheme applies to all four KWP modules on these cars (engine CJAA, ME7.1.1, DQ250, Haldex).

R-I1. Gateway `1A 9F` installation-list reply layout: unknown (sibling medium that the service exists). Q11.

R-I2. Mk6 UDS cluster service-interval **DIDs**: VCDS names only; the DID numbers behind `ESI: Resetting ESI` etc. are in the ODX/`.rod` file `EV_Kombi_UDS_VDD_RM09_VW36.rod`, not open. Low. Q12.

R-I3. The `1A 9B` ident response layout for all KWP modules (part number 11 chars + component 20+ chars + coding + WSC) is the KWP sheet's domain; `1A 91/90/87/94` sub-identifiers are used by other tools (sibling). Not repeated.

---


---

## 10. Open questions — consolidated (only the real cars can answer; exact bytes given)

Verbatim OPEN QUESTIONS sections of every sheet. The implementer digest (`IMPLEMENTATION_NOTES.md` §(d)) ranks them and
gives the CAN-level experiment for the top items.


### 10.1 TP 2.0 (from `tp20.md`)

1. **Which 2008 R32 and 2012 Golf modules answer on 0x200+addr at all** and with which tester-TX IDs. Method: for each candidate logical address 0x00..0x7F send `addr C0 00 10 00 03 01`, wait 300 ms on 0x200+addr, log 0xD0/0xD6..0xD8/silence, then `A8`. (0xD8 ⇒ a channel is already open — e.g. the gateway or another tool.) Note the IDs returned in bytes 4–5. Expect at least engine 0x01 (R32), gearbox 0x02, ABS 0x03, instruments 0x07, EPS 0x09, Haldex 0x0A, gateway 0x1F (NEFM-GW shows a Mk5 Jetta answering on 0x01/0x02/0x03/0x1F).
2. **True module idle timeout** without A3 (see REPORTED). Also whether modules themselves send A3 when the tester is quiet, and how fast they expect the A1 back. Method: open 0x01, send `10 89`, then stop; log everything on 0x300 until A8 or silence; repeat with an A3 every 1 s, 2 s, 5 s.
3. **Whether ME7.1.1 (R32) ever answers 0x9X (not ready)** — e.g. during flash routines or 0x23 readMemoryByAddress bursts — and whether it resumes on a plain wait or needs retransmission from the NAK'd sequence. Method: send back-to-back readMemoryByAddress requests with T3 = 1 ms and capture; if a 0x9X appears, try (a) wait 100 ms and keep waiting for 0xBX, (b) retransmit from the NAK'd sequence.
4. **Block-size semantics** (15 vs 16) — see REPORTED, test with a ≥ 16-frame request (e.g. writeDataByLocalIdentifier/transferData of 110+ bytes): send 15 × 0x2X then a 16th 0x2X and see whether the ECU ACKs, ignores, or A8s; compare with ACK-request on the 15th.
5. **Exact minimum T3 the engine ECU tolerates** when the tester sends multi-frame requests (relevant for KWP transferData flashing throughput). Start at 10 ms, step down, watch for 0x9X/A4/A8.
6. **Multiple concurrent channels** across the gateway (engine + DSG + Haldex) — does the gateway or any module return 0xD8 for the second channel? Also: does a *repeated* 0xC0 with the same RX ID to an already-open module return 0xD0 (as the emulator does) or 0xD8?
7. **Behaviour on the 2012 car** where the engine is UDS/ISO-TP (0x7E0/0x7E8) but other modules may be TP 2.0: confirm that a 0x200 setup to 0x01 is refused/ignored there and that the autoscan falls back to UDS; confirm which 2012 modules (gateway 0x1F, instruments 0x07, ABS 0x03, comfort 0x21, …) still use TP 2.0. (NEFM-GW: instruments are "TP20 address 07h and their UDS ID is 714h" — some modules may answer both.)
8. **Length MSB** — does any module on these cars set bit 15 of the length (JAZDW-SRC masks it)? Log raw first frames.
9. **Ordering of `A1` vs data when the tester's A3 collides with an in-flight response** — verify that the inline-A3 handling of §8 (`_recv_ctrl`) never misattributes a 6-byte `A1` frame to the data stream (an ECU data frame can also start with 0xA? only if op nibble were 0xA, which is not a data opcode, so the check is unambiguous — confirm no module uses 0xAx data PCIs).
10. **Gateway tester-TX ID and 1A 9F** — open 0x1F on both cars, record the assigned tester-TX ID (0x32E predicted by the simulators), then send `1A 9F` and log the reply to see whether it is a usable installed-module list.
11. **Which negative setup code a sleeping/absent module produces** — on the R32, address a module that is not fitted (e.g. 0x0E) and one that is fitted but in a different app type; confirm silence vs 0xD6/0xD7 so the autoscan can distinguish "absent" from "busy".


### 10.2 Addressing and module discovery (from `addresses.md`)

1. **Build the TP 2.0 logical-address table for each car.** Procedure (both cars, ignition on, engine off):
   ```
   # (a) ask the gateway: open TP2.0 channel to dest 0x1F, KWP 1A 9F, dump raw reply (expect 5A 9F + records)
   send 0x200: 1F C0 00 10 00 03 01     ; expect 0x21F: 00 D0 00 03 xx 07 01  -> tester TX id = 0x7xx (module-specific!)
   (if silent after 11 tries 50 ms apart, retry with 1F C0 00 03 00 03 01 — the "both IDs valid" form that a MED17.5 required)
   send TXID : A0 0F 8A FF 32 FF        ; expect RXID 0x300: A1 ...
   send TXID : 10 00 02 1A 9F           ; expect B1 then data frames; log everything; send ACKs (B0|seq+1); A8 to close
   # (b) brute force: for dest in 0x00..0xFF: send 0x200: dest C0 00 10 00 03 01; wait 50 ms; record any 0x200+dest reply
   #     (use 0x300 as RX id; on D6..D8 send A8 to the TX id in bytes 4-5 of the refusal, wait 300 ms, retry once;
   #      send A8 on each opened channel; never leave a channel open — modules refuse a second setup)
   # (c) on every answering dest: 10 89 then 1A 9B (fallback 1A 91) -> part number string -> map to address word via the scan tables above
   ```
   Expected: engine at 0x01, gateway at 0x1F, EPS at 0x09, Haldex at 0x0A (R32 only), cluster at 0x07 (reported), ABS at 0x03 (reported). Record which dest bytes answer but are NOT real modules (the NefMoto "AWD 0x22 on a FWD car" effect — possibly the gateway answering as a proxy; a `1A 9B` ident resolves it). Record the tester-TX id each module grants (0x740 engine, 0x7A8 EPS, 0x764 Haldex seen) — two modules may not be open at once if they grant the same id.
2. **Which modules are UDS on each car**: for every request ID in VERIFIED §C plus 0x7E0..0x7E7, send ISO-TP SF `03 22 F1 87 55 55 55 55`, wait 100 ms for `request+0x6A` (or +8), then `62 F1 87 ...`. Repeat with `02 10 03` first for modules that refuse in default session. Expect on the R32: only 01 (0x7E0, generic OBD + maybe UDS ident) — everything else TP 2.0. Expect on the Golf: 0x714, 0x711, 0x715, 0x746, 0x70C (if 5K0 953 549 E), 0x76B; and test 0x7E0 once to learn whether the CJAA EDC17CP14 answers UDS ident in addition to its (verified) KWP/TP 2.0 interface.
3. **`1A 9F` response format** on 1K0 907 530: unknown byte layout; parse by inspection. Cross-check its 22 entries against the long-coding decode (VERIFIED §E) which is exact for the R32, and its per-module status against VCDS's `0000`/`0010`/`1100` status words.
4. **7N0 907 530 (Golf) installation list**: is the gateway KWP (no ASAM in two scans) with `1A 9F`, or UDS 0x710/0x77A with a DID? Try both: TP 2.0 dest 0x1F + `1A 9F`; and `0x710: 03 22 F1 87`. If UDS answers, scan DIDs 0x0600..0x06FF and 0xF1xx for a list-shaped payload (VCDS's "Installation List" button on 7N0 is a separate function, so it is a distinct DID/routine, not the 3-byte coding).
5. **Why brute-force probing is still needed even with an installation list**: the list is a *configured expectation* stored in the gateway, not a live scan (Ross-Tech: it is edited through gateway coding; the R32's own scan shows a listed-but-dead module 22). Retrofitted or unlisted modules (e.g. a Sirius tuner at 0F, aftermarket amp) and modules whose list bit is wrong are only found by probing all 256 TP 2.0 dest bytes and all 0x700..0x7FF UDS IDs.
6. **Haldex on the R32 (22)**: the sample scan could not reach it. Probe dest 0x0A (expected reply 0x20A, tester TX ~0x764); read `1A 9B` for the real part number (expect `1K0 907 554 x` per the Mk5 4Motion scan, or `0AY 907 554`) and compare with the `1A 9F` list entry.
7. **Engine OBD-II vs UDS on the ME7.1.1** (R32): check whether `7E0 02 10 03` is answered (`7E8 06 50 03 ...`) — a 2008 ME7.1.1 may only do OBD modes on 0x7E0 and KWP via TP 2.0 (as the 2009 MED17.5 does); needed to decide which client `vagtune identify` picks for address 01 on that car.
8. **Shared UDS IDs** (0x716 1B/7E, 0x70A 10/76, 0x732 05, 0x76B 77): when a module answers, identify it by F187/F197 rather than by ID.
9. **Padding and FC parameters per module**: PQ35 UDS modules (cluster 5K0 920) may use BS=0/STmin=0 or not; log the first FlowControl from each module and store it in the per-car profile.
10. **Door modules and "all doors unlocked"**: the Mk6 BCM (09) may not answer when locked (Ross-Tech) — the autoscan must retry 09/42/52/62/72 after an unlock and must not mark them "absent" on first silence.
11. **TP 2.0 block-size semantics**: send a >15-frame KWP response (e.g. `1A 9B` is only 8 frames; use `21 xx` with a long block or `18 00 FF 00` DTC read on a module with many DTCs) and count how many data frames the ECU sends before waiting for an ACK with BS=0x0F — 15 or 16. Also measure the real keep-alive window: stop sending for 0.5/1.0/1.5 s and see when the ECU sends `A8` (expected ~1 s per EliasTuning's `T_CT_AKTIV_MS = 1000` and the Scirocco observation).
12. **10-byte 1K0 907 530 codings (index S/AA)**: bytes 7-9 (`00 20 02` on the 2010 Jetta, `00 21 03` on the 2009 A3) are undocumented on the Ross-Tech page; read the R32's coding and the Golf's gateway, and diff against VCDS's Long Coding Helper if available. Only bytes 0-6 are the installation bitmap (verified bit-exact on two cars).
13. **Channel-setup request form**: on each car, try `dest C0 00 10 00 03 01` first (what the real VAG tester and every library send); if a module stays silent, retry with `dest C0 00 03 00 03 01` (what a 2009 MED17.5 required). Record which form each module accepted.
14. **Does the Mk5 gateway itself open TP 2.0 channels to modules** (as the ABS-emulator author implies, "answers the gateway ... without dropping out of the installation list")? Sniff the powertrain/comfort CAN with the gateway's Kufatec breakout (cf. kostaszaf/can-gateway-sniffer) for `0x200` frames not sent by the tester. If it does, those frames give the TP 2.0 address of every listed module for free.


### 10.3 J2534 / hardware (from `j2534_can.md`)

1. **Does the Tactrix Windows DLL really starve the raw CAN channel when an ISO15765 channel is also open?** OP-AB measured (under emulation, same DLL) that with both open "every channel-5 frame goes to the ISO 15765 channel, none to the CAN channel". If true on native Windows, vagtune's `TransportContext("j2534")` cannot run a router on the CAN channel while a `J2534IsoTpLink` is open on the same device. How: open CAN(5) + ISO15765(6) on the car, send `01 00` to 0x7DF on the ISO15765 channel, and watch which channel delivers the ECU's raw frames; also check whether frames delivered to the ISO15765 channel carry `ProtocolID = 5`. Decide between (a) "universal" mode = CAN channel only (software ISO-TP + TP 2.0, one channel), (b) ISO15765-only mode for flashing, with the router paused, or (c) the open-source driver on Linux/macOS, which keeps the channels separate.
2. **Exact RxStatus values delivered by the DLL for TxDone / RxStart / loopback / padding error on this firmware (expected 1.17.4877) and DLL (expected 1.02.0.4868).** How: log `RxStatus`, `DataSize`, `ExtraDataIndex`, `Timestamp` of every message during one `identify` and one 30-byte DID read; confirm TxDone = 0x09 with DataSize 4 (already measured by OP-PROTO on an Audi), RxStart = 0x02, loopback = 0x01 with four zero data bytes on raw CAN, then wire `_accept_rx_status` to RxStatus instead of lengths. Also record `PassThruReadVersion` output (firmware/DLL/API strings).
3. **Which return code (0x09 vs 0x10) the DLL gives on an empty read with Timeout > 0 and with Timeout = 0**, and the observed overshoot of `PassThruReadMsgs(Timeout=1)` (expected ≈ 6–8 ms, measured so far only under emulation). How: a 1000-iteration loop on an idle channel with `perf_counter()`. This fixes the reader thread's poll interval for TP 2.0.
4. **ACK latency budget and per-module TP 2.0 parameters on the real car**: log, for each TP 2.0 block the ECU sends, the Timestamp of its last frame vs. the Timestamp of our ACK's own echo (raw CAN returns our frames when the PASS filter admits our assigned tx id). Target < 30 ms; T1 is typically 100 ms. If the echo is not returned, use the DLL's ReadMsgs return time instead. Record each module's `D0` channel-setup reply (the tester tx id it assigns: 0x740? 0x7A8? …) and its `A1` reply (BS, T1, T3) rather than assuming 0x740 / 0x8A / 0x4A.
5. **What is actually on OBD pins 6/14 of the R32 and the Golf TDI**: a dedicated diagnostic CAN (quiet bus, only diagnostic ids) or the powertrain bus (periodic 0x280/0x288/0x380/0x5A0 … frames at 10–100 ms)? How: `candump -t a can0` (or a pass-all J2534 CAN filter) for 10 s with ignition on, engine off, no tester traffic; count unique ids. This decides whether live-data logging can read broadcast frames or must poll DIDs/measuring blocks through the gateway.
6. **Does the gateway forward TP 2.0 channel setup (0x200) to *every* module listed in the installation list, and which modules answer only KWP2000/TP 2.0 vs UDS on each car?** How: for each logical address 0x01..0x7F send `<addr> C0 00 10 00 03 01` on 0x200, wait 100 ms for `0x200+addr` (`00 D0 …` positive, `D6..D8` negative); separately send `02 10 03` (UDS) via ISO-TP to 0x7E0, 0x7E1, 0x710, 0x713, 0x70F … and record positives. Build the per-car module table from the results.
7. **Padding byte and DLC expectations**: does each module answer an unpadded (DLC 3) single-frame request? How: send `02 10 03` once with ISO15765_FRAME_PAD and once without on the ISO15765 channel; and on the CAN channel with DLC 3 vs DLC 8 (0x00, 0xAA and 0xCC padding). Record which combinations answer and what pad byte the ECU itself uses in its replies, so the software ISO-TP default (`pad=0x00`, `dlc=8`) is right for both cars.
8. **Filter budget on the OpenPort**: 10 filters per channel (= the SAE minimum). OBD-II functional needs 8. Confirm ERR_EXCEEDED_LIMIT (0x0C) on the 11th and that `CLEAR_MSG_FILTERS` (`atk<ch> -1`) truly removes all before the next module session (ERR_NOT_UNIQUE 0x18 otherwise); note filter ids are never reused within a session.
9. **Periodic TesterPresent via PassThruStartPeriodicMsg vs. a Python keepalive thread**: periodics keep running in the cable after a crash until the next PassThruOpen and generate no TxDone; decide whether to use them (lower jitter, survives GIL stalls) and always `CLEAR_PERIODIC_MSGS` in `close()`. For TP 2.0 the keepalive must be the 1-byte `A3` on the assigned tx id, every ~0.5–1 s.
10. **python-can path on Windows**: verify a CANable/candleLight with gs_usb firmware enumerates with WinUSB (Zadig) and that python-can `gs_usb` sustains the 10 ms T3 pacing; measure `Bus.recv(timeout=0.001)` overshoot. On Linux prefer SocketCAN (`ip link set can0 up type can bitrate 500000 restart-ms 100`).
11. **32-bit Python vs. a 64-bit toolchain**: confirm with `python -c "import struct,sys;print(struct.calcsize('P')*8)"` = 32 in the venv used with `op20pt32.dll` (the DLL is x86-only); if the owner wants 64-bit Python, the only verified options are the open-source drivers (Linux/macOS: bisak = 8-byte `c_ulong`, roffe = 4-byte ints) — there is no verified 64-bit Tactrix DLL.
12. **Write-timeout behaviour on native Windows**: confirm that `PassThruWriteMsgs(Timeout=0)` indeed returns 0 immediately and that the *next* call stalls ~1 s (OP-AB measured this under emulation); vagtune should never use Timeout 0, but the test documents why. Also confirm that a nonzero Timeout shows up as `att… <Timeout*1000>` if a serial tap is available.


### 10.4 KWP2000 (from `kwp_vag.md`)

1. **Identification record decode on both cars.** Per TP 2.0 module (engine 0x01, DSG 0x02, ABS 0x03, Haldex 0x0A, EPS 0x09, gateway 0x1F, cluster 0x07, …): send `10 89`, then `1A 9B`, `1A 91`, `1A 9A`, `1A 9C`, `1A 86`, `1A 90`, `1A 92`, `1A 94`, `1A 9F` (gateway only). Log every raw reply. Check: offset 16 of the 9B payload is 00/03/10; offsets 18-19 equal VCDS's short coding; the 6 bytes at 20..25 decode with the REPORTED packing to the "Shop #: WSC … " line of a VCDS Auto-Scan of the same car; 9A on long-coded modules returns the 8/… byte coding VCDS shows.
2. **8-field groups.** On the R32 engine send `21 01`, `21 02`, `21 81`, `21 82` and compare the second half of `61 01`/`61 02` with `61 81`/`61 82` (or with a `7F 21 31` refusal). Also read group `21 00` (expect 10 fields).
3. **DTC encoding of SAE codes.** Provoke one known P-code (e.g. unplug the MAF → P0101 on ME7; or read whatever is stored) and send `18 02 FF 00` then `18 00 FF 00`: record the raw 2 bytes. Expect `40 65` (decimal rule, 16485/P0101) rather than `01 01` (hex rule). Also try `18 03 FF 00` (supported codes) and note whether the module answers `58 …` or `7F 18 12`.
4. **Freeze frame.** With a stored fault, send `12 00 04 <DTC_hi> <DTC_lo>`, `12 01 04 <DTC_hi> <DTC_lo>`, `12 00 00`, and `18 03 FF 00`/`18 04 FF 00`; compare the bytes with VCDS's "Fault Priority / Frequency / Reset counter / Mileage / Time Indication" for the same fault (priority 1-8, frequency 0-254, reset counter 0-255 are single bytes; mileage probably 16- or 24-bit km).
5. **Session timeout.** Open a channel, send `10 89`, keep only TP 2.0 `A3` keepalives for 15 s, then send `21 02`: if it is refused or the ECU answers `7F 21 11`, the 0x89 session needs `3E` (then measure the longest `3E` interval that still works: 1, 2, 4, 8 s).
6. **Capability lists.** Send `31 B8 00 00` to every TP 2.0 module and record the `71 B8` list (expect 01xx pairs). This tells which functions each module tunnels and whether DSG/Haldex/ABS advertise 0103 (adaptation) and 0101 (basic settings).
7. **Adaptation read-only probe (safe).** On a module advertising 0103: `31 B8 01 03`, `31 B9 01 03 <ch>` for ch = 1, `31 BA 01 03`, then `32 B8 01 03`. Decode the `71 BA` payload (expect the channel and a 16-bit value equal to VCDS's "Stored Value"). Never send `31 BB` (save) during the probe.
8. **Login bytes.** Sniff VCDS (HEX-CAN) performing Login on the R32 engine with a known-harmless wrong code (it should be refused) and capture the request bytes; expect `31 B8 01 05` / `31 B9 01 05 <code>` per the REPORTED model, or `27 xx` if the module uses seed/key.
9. **Group map of DSG and Haldex.** Walk `21 01`…`21 FF` on 0x02 and 0x0A, log formula ids per field; compare with the VCDS label files (02E group 019 = three temperatures: G510 control module, G509 clutch oil, G93 fluid; group 001 field 1 = speed as raw/3 km/h under formula 0x25).
10. **Formula disagreements** (0x08, 0x14, 0x19, 0x25, 0x27, 0x51, 0x5E, and [added] 0x0E and 0x21 where OpenHaldex uses `0.01·A·(B−100)` / `0.01·A·B` against KL's `0.005·A·B` / `100·B/A`): find fields using those ids on the two cars and compare the decoded value with VCDS's display to pick the right formula. For 0x0E/0x21 a single Haldex sample with `A != 100` / `B != 200` discriminates: read `21 01`/`21 02`/`21 7D` on 0x0A (R32) and compare any `0E xx yy` / `21 xx yy` field with VCDS group 001/002/125 of the Haldex.
11. [added] **Haldex Gen2 group map.** OpenHaldex says a Gen2 (1K0) Haldex answers groups `0x01`, `0x02` and `0x7D` (125) but decodes none of them. On the R32 send `21 01`, `21 02`, `21 7D` to 0x0A after `10 89`, log the formula ids, and align with the VCDS label file for 1K0 907 554 (expect oil/plate temperature as `1A` fields, supply voltage `06`, clutch current `18`, pressure `0E`, duty `21`, torque `5E`).
12. [added] **Formula 0xA0 over KWP2000.** DV says KWP2000 tools mishandle it; check whether any `61` reply on the two cars ever contains `A0` (walk `21 01..FF` and search the raw bytes); if it does, verify the 5-byte layout above against VCDS's displayed value and unit.


### 10.5 UDS (from `uds_vag.md`)

1. **EDC17CP14 (2012 Golf TDI, CJAA) vs Simos18 DID set.** The VW_Flash DIDs/response strings
   are from a Simos18 *petrol* ECU (note `22 F1 97`→"R4 2.0l TFSI"). Confirm F187/F197/F19E
   strings and whether 0x0600 coding and 0x295A/0x295B mileage read identically on EDC17CP14.
   Trace `22 F1 87`, `22 F1 97`, `22 06 00`, `22 F1 5B` on the TDI. EDC17 needs its own
   calibration profile (not Simos18).
2. **R32 BUB ME7.1.1 is almost certainly NOT a UDS module.** 2008 R32 engine (ME7.1.1) is
   KWP2000-on-CAN / VW TP2.0. Probe UDS `10 03` at 0x7E0/0x7E8 first; on timeout, fall back to
   the TP2.0 + KWP2000 stack (separate fact sheet). Determine per-module which stack answers
   (newer modules — MK60 ABS, 7N0 gateway, cluster — are more likely UDS).
3. **Full SAE J2012-DA FTB table (0x00-0x98).** Only ~17 rows + the 16-row category scheme are
   confirmed (from secondary sites). Obtain SAE J2012-DA 201812 Digital Annex (Excel) or
   extract the DTC/FTB table from an ODX/CDD/label file to pin the uncertain subtypes exactly
   (0x29, 0x31, 0x49, 0x64, 0x88, and everything above 0x9D).
4. **Coding SecurityAccess level + algorithm per module.** Trace a VCDS/ODIS recode on each
   target module: capture the `27 <odd>`/`27 <even>` seed→key exchange (is it level 03/04,
   11/12, or other?) and the subsequent `2E 06 00` write. Determine whether the key is derived
   by an SA2 bytecode (likely newer modules) or a fixed formula, and how the 5-digit login
   maps in. Do NOT assume `key = seed + 0x11170`, and do NOT assume the flash level 0x11 is
   also the coding level (the fake testdata uses 03/04).
5. **Exact 0x19 0x06 extended-data record byte layout per module.** Trace `19 06 <dtc> FF` on
   a module with a stored fault; map each record number → (priority, frequency,
   aging/unlearning counter, mileage width 3 vs 4 bytes, timestamp format).
6. **0x04 snapshot DID sizes.** The freeze-frame parser needs each snapshot DID's byte size
   a priori (udsoncan cannot infer it). Capture `19 04 <dtc> FF` and cross-reference the DID
   list, or read the ODX. Likewise supply `extended_data_size` for 0x06 per module.
7. **DQ250-MQB TCU ISO-TP separation-time quirk.** VW_Flash uses a `dq3xx_hack` flag and
   `DSG_STMIN = 900000`; connection_setup default `st_min = 350000` (units: **microseconds** —
   confirmed by the `stmin_to_isotp` helper: `>1_000_000 µs` → ms pass-through, else
   `0xF0 + hundreds_of_µs`). So 350000 = 350 µs → ISO-TP STmin byte `0xF4` (0xF0+4 = 400 µs
   bucket), and 900000 = 900 µs → `0xF9`. Confirm the DQ250-MQB TCU's required separation time
   on the real TCU so multi-frame reads don't abort. (src: lib/connections/connection_setup.py
   + lib/constants.py `DSG_STMIN`, re-read this session — this corrects the prior sheet's
   "900 ms / ns?" uncertainty: the units are microseconds.)
8. **ALFID of the 0x2C memory-address logging list.** Confirm the `0x14` ALFID reading in §
   REPORTED (4-byte address + 1-byte size) and the `0xD0…` RAM addressing against a real Simos
   logger session (`2C 02 F2 00 …` then `22 F2 00`).
9. **Gateway (7N0) installed-module list.** Read the gateway's module-inventory DID to drive
   an autoscan of which addresses to probe. The exact DID is unconfirmed (likely a VAG-specific
   low-range DID); trace VCDS "Gateway Installation List" to capture the `22 <DID>` request and
   its response layout.


### 10.6 OBD-II (from `obd2.md`)

1. **Responder map**: send `7DF 02 01 00` (padded, DLC 8) at 500 kbit/s and log every ID in 0x7E8..0x7EF plus the full 4-byte bitmap each returns. Expected ECM 0x7E8; DSG 0x7E9 on both cars if fitted (owner said DQ250 on the R32, DSG or 6MT on the TDI). Record whether any other module (e.g. 0x7EA) answers. Then send `7E1 02 01 00` physically to see whether the TCU answers OBD when addressed directly even if it ignored the functional request.
2. **Bitmap walk** per responder: `01 00 20 40 60 80 A0` (legal in one request) then `01 C0 E0` → exact supported PID set; same for `02 00 00 20 00 40 00`, `06 00 20 40 60 80 A0`, `08 00`, `09 00`. Store per-VIN. Verify that the ECU does not answer unsupported ranges (Table 7 b) by sending `01 C0` alone and expecting silence.
3. **Response lengths of PIDs ≥ 0x60** on EDC17CP14 (esp. 0x67, 0x68, 0x6B, 0x6D, 0x70, 0x78, 0x7A, 0x7C, 0x8B): request each PID alone, compare the ISO-TP length (SF PCI nibble or FF length) with the byte counts in section 3; use the PCI length as truth for the record walker.
4. **Padding bytes**: (a) what the VW ECUs transmit after the PCI length in an SF such as `41 05 xx` (0xAA vs 0x00 vs 0x55); (b) whether they accept a tester FC `30 00 00 00 00 00 00 00`, `30 00 00 55 55 55 55 55` and `30 00 00 AA AA AA AA AA` — run `09 04` (multi-frame CALID) three times with each FC padding and check that all CFs arrive.
5. **Timing**: measure real P2 of each ECU to the functional request (timestamp of 0x7DF SF → first byte of each 0x7E8/0x7E9 frame); confirm the DSG does not need > 50 ms; verify behaviour on `7F 09 78` for Mode 09 06 (CVN) and `7F 04 78` for Mode 04 (how many repeats, interval).
6. **Mode 06 content**: dump `06 <mid>` for every supported OBDMID on both cars and keep the raw 9-byte records; verify UASIDs used are all in the table (log unknown ones instead of failing); check whether EDC17 reports misfire OBDMIDs A1–A5 and PM-filter B0; check whether any record uses UASID 0x2E and whether its values look boolean or percent (ISO5 inconsistency noted in §7).
7. **Mode 0A support** on each car: send `0A` functionally; expect `4A nn …` from the 2012 TDI, no response on the 2008 R32. Record the exact payload to confirm the `4A <count> <DTC pairs>` layout.
8. **Mode 02 frame numbers**: check if either ECU exposes more than frame 0 (`02 02 01`); ISO5 only guarantees frame 0.
9. **Mode 08 01**: on the R32 (gasoline, EVAP) check whether `08 00` lists TID 01 and what `08 01` returns with engine off (`48 01` vs `7F 08 22`). On the TDI expect no Mode 08 support at all.
10. **Mode 09**: exact CALID string(s) (VW part-number format), number of CVNs, ECUNAME presence, IPT NODI value (0x10/0x14 on R32, 0x12 on TDI); confirm VIN is 17 chars and matches the chassis; check whether the TCU (if it answers Mode 09) reports its own CALID/CVN like the TCM in the ISO5 example.
11. **PID 13 / 1D** on the VR6: confirm the bank/sensor layout (expected 0x33) so the O2 PIDs 14–17/18–1B and Mode 06 OBDMIDs 01/02/05/06 are labelled correctly.
12. **PID 1C** value on each car (US 1 vs EU 6/7) and whether PID 5F is supported at all.
13. **PID 4F / 50**: if the 0x40 bitmap lists 4F or 50, read them once per connection and check whether Data A is non-zero; if so, verify against the car's λ (PID 24/44 should read ≈ 1.0 at warm idle on the R32) that the override rule produces sane values.
14. **NRC set**: deliberately send an unsupported service (e.g. `0B`) and a malformed request (`01` with no PID) on 0x7DF and 0x7E0 and record whether the VW ECUs stay silent (ISO 15765-4 rule) or answer `7F xx 11/12/13` (UDS habit) — the parser must tolerate both.
15. **Multi-PID responses**: send `01 0C 0D 05 04 0B 0F` and verify the ECU returns all six records in one message and whether the order matches the request; verify the record walker on the real byte stream.


### 10.7 DTC database (from `dtc_db.md`)

1. **Which exact codes the two cars emit.** Pull `0x19 0x02 0xFF` (UDS, Golf TDI engine/DSG/ABS) and KWP `0x18 0x00 0xFF 0x00` (R32 modules over TP2.0) and log every 2-/3-byte DTC with its ECU address. Any code not found in `codes` should be added by hand from the VCDS/ODIS text — the DB cannot be made complete for manufacturer codes from open sources. Expected on the TDI engine (from forum 22128): `0x19 0x02 0xFF` → `59 02 <availabilityMask> 20 02 <FTB> <status> …` where `20 02` = P2002 and the status byte for the quoted "Fault Status: 11100111" is 0xE7.
2. **KWP 5-digit codes vs. DTC bytes.** For TP2.0/KWP modules, confirm on the car how the 2-byte DTC maps to the 5-digit number: expectation from this sheet (now backed by the KLineKWP1281Lib implementation) is `N5 = int(DTC_H<<8 | DTC_L)` always, with 0x4000–0x7FFF decoded to a P/C/B/U code by the §C rule (e.g. 0x011F = 00287, 0x4065 = 16485 = P0101). Verify with one ABS fault (unplug a wheel-speed sensor on the R32 → expect 0x011F/0x0122 = 00287/00290 with elaboration 0x10 "Signal Outside Specifications" or 0x39/0x1x electrical). Note KWP2000 (service 0x18) returns `58 <count> DTC_H DTC_L status…` — check whether the third byte on the Mk5 modules is the KWP1281 elaboration byte (§F table, bit 7 intermittent) or an ISO 14230 status byte; VCDS's `XX-YY` rendering suggests the former.
3. **Failure-type byte table.** Capture the third DTC byte alongside VCDS text on both cars: on the TDI (UDS) compare the raw FTB with VCDS's `- NNN -` field to settle decimal vs hex and to confirm the §G table; on the R32 (KWP) compare with the §F elaboration table and VCDS's `XX-YY` field (predict `YY` = `10` when byte & 0x80). Minimal test: provoke one electrical fault (unplug a sensor) and one "intermittent" (replug before clearing) and read both.
4. **Wording priority in the UI.** The JSON carries both SAE wording (`codes`) and VW wording (`vag_wording`); recommended: VW wording when present (now available for every decimal P0–P3/U0–U1 code from the §F OBD file), SAE as fallback, plus the 5-/6-digit number. Strip the §F joke text at 00543 and the `P0000` placeholder.
5. **Licensing.** python-OBD is GPL-2; KLineKWP1281Lib is GPL-3; Wal33D is MIT; the SAE text itself is copyrighted but facts are not. If the project wants to avoid any GPL question, regenerate the P0/P2/P3/U0 wording from Wal33D (MIT) using `provenance` to select, and keep the §F tables as an optional, separately-licensed data pack.
6. **Ross-Tech wiki coverage — RESOLVED.** The verifier's full crawl (`rt_alltitles.txt`, 1598 titles; `rt_fc_titles.txt`, 1040 fault-code pages) shows the listing has no more fault-code pages; the research agent's set already covered them (plus 41 redirects). Remaining gap: pages with `CODE FTB -` headings (`C10E2`, `B1916`) and the `00543`/`721152` oddities need a regex fix in `build_dtc_db.py` (`^([PCBU][0-9A-F]{4})\s+([0-9A-F]{2})\s*-\s*(.+)$`).
7. **Regenerate `vag_5digit_only` from §F.** Parse `fault_code_description_EN.h` (regex `const char KWP_FAULT_([0-9A-F]{4})\[\] PROGMEM = "(.*)";`, key = int(hex) = 5-digit number) → 4279 factory codes 00000–16377 plus 546 codes ≥ 32768; keep Ross-Tech text where it exists (identical in 378/409 cases) and tag the rest `kwp1281lib`. Add the 00873-type misses. Decide how to present the ≥ 32768 entries (VCDS shows them as 5-digit too, e.g. 32768).
8. **Regenerate `vag_wording` from §F.** Parse `OBD_fault_code_description_EN.h` (key = 2-byte SAE value → code via §B) → 4571 VW-worded codes; keep Ross-Tech text first (current VCDS), then this file, then Bentley. Also add its 763 codes missing from `codes` (P17xx DSG block, U1xxx) with the same tag, and drop or flag the 42 placeholder rows listed in §D.
9. **Add the two fault-type tables to the JSON** as `kwp_elaboration` (§F, 83 rows, applies to KWP1281/KWP2000 modules; bit 7 = intermittent) and `uds_ftb` (§G consensus rows VERIFIED, remaining rows tagged unverified) so `vagtune dtc` can print `P0401 - 01 - Insufficient Flow (General Electrical Failure)` style lines; confirm against item 3 before removing the "unverified" flags.


### 10.8 ECU-specific (from `ecus.md`)

Q1. **Can the R32's ME7.1.1 be RAM-logged over TP 2.0 at all?** Open TP 2.0 to dest 0x01 (per `tp20.md`), start a session, then send KWP `23 00 F8 88 01` (ReadMemoryByAddress, 3-byte address of `nmot`-class internal RAM `0x00F888`, 1 byte — the BEL address is only a probe; any low RAM address works) and look for `63 xx` vs `7F 23 <nrc>` (0x11 serviceNotSupported, 0x12 subFunctionNotSupported, 0x33 securityAccessDenied, 0x80 serviceNotSupportedInActiveSession). Also probe `2C` (DynamicallyDefineLocalIdentifier, e.g. `2C F0 03 01 00 F8 88 02` define by memory address) and `21 F0`. If `23` works, the `.ecu` *format* can carry R32 addresses once they are known (Q2). Only if `23` works, also probe the non-standard `B7 03 00 F8 88` + `B7` pair from `derpston/me7` (expect `7F B7 11` on anything but a handler-patched ME7).
Q2. R32 image variable addresses: obtain the stock `022906032KR` bin (the owner's, or the NEF-837 attachment) and derive `nmot/rl/tmot/tans/zwout/wkr_x/fr_w/fra_w/ti_b1/vfzg/ub` addresses; ME7Info cannot do it (verified). An A2L for `0261201807/1037387913` would be the primary source.
Q3. **Which VCDS groups exist on `022-906-032-BDB`**: on the TP 2.0/KWP channel send `21 <g>` for g = 0x01..0xFF and log which return `61 g …` vs `7F 21 xx`; record the formula ids per field. Specifically confirm 001-005, 014-018, 020-021, 026-028, 030-047, 050-057, 060-064, 066, 070-071, 077-078, 080-082, 090-096, 099-100, 101-102, 107, 112, 120-127, 130-137, 208-209.
Q4. Misfire counter group offset: at idle with one coil unplugged briefly, read `21 0E`, `21 0F`, `21 10` and see which group carries cylinder 1-3 counters (Ross-Tech page says 014/015, the standard says 015/016).
Q5. Cam-adaptation groups: read `21 5A` (090), `21 5B` (091), `21 D0` (208), `21 D1` (209) warm at idle; expect field 3 of 208/209 in °KW within ±8 and 090/091 set-point 0° with ~15.3 % duty.
Q6. CJAA full group map: send `21 <g>` for g = 0x01..0xFF on the engine channel and keep the `61` replies; cross-check against the ERWIN `D3E802F8708` labels if the owner can obtain the PDF. Specifically identify: boost specified/actual, rail pressure specified/actual, EGR specified/actual, injector corrections, glow plug status, soot (108/241), ash, km since regen (240.3), regen counter (105?), EGT (099).
Q7. Regeneration-while-standing basic-settings group and regeneration-while-driving adaptation channel numbers on `03L-906-022-CBE.clb`: read them from the VCDS balloon on the owner's car (do **not** run them for the test). Also record which `27 xx` level VCDS requests for "Adaptation Enabling" (only the level byte, for the session model).
Q8. DQ250 TP 2.0 address: probe dest 0x02 with `1A 9B`; expect `5A 9B` + `02E300011CC` … `GSG DSG 082 1405`. Then `21 13` (019) with the brake pedal pressed and engine running: expect three temperatures (G510/G509/G93) and an idle flag.
Q9. DQ250 software-version branch and the "Basic Settings" wire service: the R32 prints `1405`, so group 067 (not 062) should be the clutch-adaptation entry — confirm by watching which group VCDS offers. More important for the implementation: trace VCDS performing TBA group 060 on the R32 engine and group 061 on the DSG and record which KWP service carries "Basic Settings" over TP 2.0 (expected candidates: `21 <group>` after a `10 <session>` switch, or a `31 <localId>` StartRoutineByLocalIdentifier, or `30 <localId> …`); record the exact request/response bytes and the session byte.
Q10. Haldex Gen2 group map: on dest 0x0A send `21 01` … `21 0A`, `21 7D` (125), `21 7E` (126); expect supply voltage, oil temperature, pump status, switch bits, CAN participant bits. Record the `1A 9B` reply (`1K0 907 554 x` / `Haldex 4Motion 01xx`) and the fault memory (`18 02 FF 00` KWP ReadDTCByStatus — layout in the KWP sheet) to catch 01073/01155/00448.
Q11. Gateway installation list: on dest 0x1F (sibling, high) send `1A 9F` and dump the reply; expect 22 records for the R32 matching coding `ED831F075003020000`; infer the per-record layout (address word, status word 0000/0010/1100).
Q12. Mk6 cluster service DIDs: with VCDS connected to `17`, trace the `22 xx xx` reads VCDS performs while opening `[Adaptation]` and the `2E xx xx …` it writes on "ESI: Resetting ESI"; record DID numbers and lengths.
Q13. DQ250 output tests: trace VCDS `[03]` on the DSG (expect KWP `30 <localId> <controlParameter>` InputOutputControlByLocalIdentifier frames) and list the local ids used.
Q14. R32 engine `[03]` output tests and `[07]` coding: trace VCDS reading the coding (`1A 9B` includes it) and writing it (expect `3B` WriteDataByLocalIdentifier or `3D`); only read, do not write, on the owner's car.
Q15. [added] CJAA readiness via numbered groups: send `21 56` (086) and `21 59` (089) and compare the four 8-bit fields against OBD mode `01 01` (PID 01) read on 0x7E0 at the same moment; expect 089 bits set ⇔ monitor incomplete in PID 01 byte C/D, and 086 to be the inverse per VW's table. Also read `21 29` (041), `21 88` (136), `21 2B` (043), `21 8A` (138), `21 07` (007), `21 2E` (046), `21 64` (100) and record the formula ids per field so the ".4 = 1" / "°C" semantics from VWTSB-RDY can be decoded without labels.
Q16. [added] CJAA group 020 field order and units: idle and 2000 rpm, `21 14`; expect two pressure fields (formula id for bar/MPa) that move together — determine which is specified and which actual by blipping the throttle (specified leads). Likewise `21 0B` (011) to confirm field 4 is the N75 duty (formula id for %) on the owner's label.
Q17. [added] CJAA EGR reset channels: `[Adaptation]` on 01, read channels 118 and 123 (KWP `21`-based adaptation read is the KWP sheet's domain) and confirm the names "Reset EGR Low Pressure Valve (N345)" / "Reset EGR Valve (G212/N18)"; do not save a 1.
Q18. [added] DQ250 basic-settings progress: while VCDS runs group 061/060 on the R32's DSG, log `21 3C` (060) and `21 3D` (061) and check that the four fields follow the VAS-PC status/sub-status/index/side scheme (0-13 / 129-141 etc.); while 067 runs, `21 43` should show the two clutch currents in A. This also answers which KWP service carries "Basic Settings" (Q9).


---

## 11. Appendix — fact counts per layer

Counted automatically over the assembled text: a "fact" is one top-level bullet (or numbered item) in the list; table rows are counted separately (header rows included). Open-question items are listed in §10 and not counted here.

| section | verified bullets | reported bullets | table rows |
|---|---|---|---|
| 1. CAN / J2534 pass-thru / hardware | 146 | 16 | 31 |
| 2. VW TP 2.0 transport (SAE J2819 / "VWTP20") | 50 | 17 | 21 |
| 3. ISO-TP (ISO 15765-2) and ISO 15765-4 legislated-OBD transport | 22 | 8 | 0 |
| 4. KWP2000 services (ISO 14230-3) as carried over TP 2.0 | 20 | 2 | 29 |
| 5. UDS services (ISO 14229-1) as used by VAG modules | 36 | 5 | 99 |
| 6. OBD-II (SAE J1979 / ISO 15031-5) over ISO 15765-4 | 47 | 15 | 265 |
| 7.1 Addressing model and VCDS address words | 21 | 8 | 4 |
| 7.2 UDS (ISO-TP, 11-bit) request/response CAN id table (ODIS) | 6 | 0 | 156 |
| 7.3 TP 2.0 frame formats and logical addresses (the `0xC0` destination byte) | 16 | 7 | 9 |
| 7.4 Gateway installation list (Mk5 1K0 907 530 long coding; 7N0 907 530) | 6 | 4 | 0 |
| 7.5 KWP identification: `1A` options and the `5A 9B` / `5A 91` / `5A 9A` / `5A 9F` record layouts | 10 | 3 | 21 |
| 7.6 UDS identification: DID catalogue, VAG DIDs, coding DID 0x0600, workshop code / fingerprint, OBD-mirror DIDs | 10 | 5 | 70 |
| 7.7 KWP measuring blocks (`21 <group>`): record layout, complete formula table 0x01–0xB5, group conventions | 14 | 3 | 175 |
| 7.8 DTC formats and numbering (UDS 3-byte, KWP 2-byte + status, SAE letters, VAG 5-digit and 6-digit numbers, VCDS rendering) | 27 | 7 | 8 |
| 7.9 DTC description database (`dtc_db.json`) and fault-type tables (KWP elaboration 0x00–0x52, UDS FTB) | 27 | 13 | 181 |
| 7.10 Login (function 11 / Security Access 16), coding (07), adaptation (10), basic settings (04), output tests (03) — service mappings | 11 | 11 | 0 |
| 8. Per-car module maps (real VCDS Auto-Scans) | 11 | 3 | 93 |
| 9. ECU-specific diagnostic knowledge | 66 | 21 | 212 |
| **total** | **546** | **148** | — |

Open questions collected in §10: 100.
