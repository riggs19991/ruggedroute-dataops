# vagtune 0.2.0 — implementer digest of the protocol facts

Companion to `FACTS_REGISTRY.md` (→ `docs/PROTOCOL_FACTS.md`). This file does not add facts; it tells the
slice implementers which registry items to build on, which to flag, which to leave as a raw-send + trace
workflow, how the sheet-to-sheet conflicts were settled, and which experiments on the real cars come first.
Section references (§n) are registry sections. "V" = verified in the registry, "R" = reported there.

Scope reminder: diagnostics (identify, measuring values, DTCs + freeze frame) and the owner-level functions
(coding, adaptation, basic settings, output tests, Login/function 11). No reflashing, no security algorithms,
no immobiliser. Rule 8.1 of `DESIGN_0.2.md`: anything built from an R item carries `# UNVERIFIED:` + docstring,
warns once at runtime, and may not drive a write without `confirm=True`.

---

## (a) Module maps

Protocol column = what the real Auto-Scan of that car proves (ASAM/ROD line printed ⇒ UDS; only `Labels:` ⇒
KWP2000 over TP 2.0; registry §8). Address columns give the TP 2.0 logical address (destination byte of the
`0x200` setup frame, reply on `0x200+addr`) or the UDS request→response pair, each with its evidence status.
Part numbers / component strings are what VCDS printed on that car (or the closest sibling, marked).

### 2008 VW R32 Mk5 (US) — scan A, `WVWKC71K18W108211`, gateway coding `ED831F075003020000` (every module KWP2000/TP 2.0; registry §8 F)

| Addr | VCDS name | Protocol | TP 2.0 logical / UDS ids (status) | Part no. (SW / HW) | Component string |
|---|---|---|---|---|---|
| 01 | Engine | KWP/TP 2.0 (V: no ASAM/ROD; ME7.1.1). Generic OBD-II on 0x7E0/0x7E8 (V: ISO 15765-4 standard; not yet traced on this car). UDS `10 03` on 0x7E0: unknown | TP 2.0 **0x01** → 0x201, tester TX **0x740** (V for PQ35 engines: three captures) | 022 906 032 KR / 022 906 032 GP | `R32-DQ-LEV2 G 1098` (coding 0000178, WSC 01279 785 00200) |
| 02 | Auto Trans (DQ250) | KWP/TP 2.0 (V) | TP 2.0 **0x02**, tester TX **0x760** (R medium-high: speedPulserPro "confirmed from VCDS SavvyCAN capture", Mk5 DSG). OBD 0x7E1/0x7E9 (R medium) | 02E 300 011 CC / 02E 927 770 AD | `GSG DSG 082 1405` (coding 0000020, WSC 04940 001 00001) |
| 03 | ABS Brakes | KWP/TP 2.0 (V) | TP 2.0 **0x03** (R medium: PQ35 ABS emulator's choice). ODIS 0x713→0x77D is a UDS slot and is **not expected to answer** here | 1K0 907 379 AB / same | `ESP 4MOTION MK60 0102` (coding 0021128) |
| 04 | Steering Angle (G85) | sub-node of 03, not a scannable module (V) | — | — | status "OK" from gateway list only |
| 08 | Auto HVAC | KWP/TP 2.0 (V) | unknown | 1K0 907 044 BS / same | `ClimatronicPQ35 120 1111` |
| 09 | Cent. Elect. | KWP/TP 2.0 (V) | 0x20 (R low: converter table only) | 3C0 937 049 AJ / same | `Bordnetz-SG H54 2202` (30-byte coding; sub: wiper 1K1 955 119 E, RLS 1K0 955 559 AF) |
| 0F | Digital Radio | KWP/TP 2.0 (V) | unknown | 8E0 035 593 H / same | `SDAR SIRIUS H06 0080` |
| 15 | Airbags | KWP/TP 2.0 (V) | 0x05 (R low: converter table) | 1K0 909 605 AB / same | `6T AIRBAG VW8R 034 8000` (coding 0013908) |
| 16 | Steering wheel | KWP/TP 2.0 (V) | unknown | 1K0 953 549 AQ / same | `J0527 036 0070` (coding 0012122) |
| 17 | Instruments | KWP/TP 2.0 (V) | **0x07** (R medium: one forum assertion, no sniff quoted) | 1K6 920 974 D / same | `KOMBIINSTRUMENT VDD 1216` (coding 0007203 = options 7, USA, impulse 3) |
| 19 | CAN Gateway | KWP/TP 2.0 (V) | **0x1F** → 0x21F (V: sniff + reproduction, two posters, Skoda paper); tester TX predicted 0x32E (R medium) | 1K0 907 530 L / 1K0 907 951 | `J533 Gateway H07 0052` (long coding = installation list, layout 3, bit-exact) |
| 22 | AWD (Haldex Gen2) | KWP/TP 2.0 (V: `.lbl`, coding 0000001; "Cannot be reached" in scan A) | **0x0A** → 0x20A, tester TX **0x764** (V high: OpenHaldex-C6 capture; 0x22 silent). ODIS 0x70F→0x779 is Gen5/MQB only | 1K0 907 554 L (scan A) — family A/C/F/L | `Haldex 4Motion 0116` (`0115` on F, `0105` on A) |
| 25 | Immobilizer | same ECU as 17 (V) | — | 1K6 920 974 DX | `IMMO VDD 2216` — **out of scope** |
| 37 | Navigation (MFD2) | KWP/TP 2.0 (V) | unknown | 1K0 919 887 G | `Navigation 0050` (coding 0000101) |
| 42 / 52 | Door Elect. Driver / Pass. (MIN3) | KWP/TP 2.0 (V) | 0x22 door driver (R low: converter table) | 1K0 959 701 M / 1K0 959 702 M | `Tuer-SG 006 120A` (coding 0001077 / 0001076) |
| 44 | Steering Assist (EPS) | KWP/TP 2.0 (V) | **0x09** → 0x209, tester TX **0x7A8** (V on a bench 1K0 909 144 E without gateway; on-car R medium) | 1K1 909 144 M | `EPS_ZFLS Kl.141 H08 1901` |
| 46 | Central Conv. (KSG, also serves 65) | KWP/TP 2.0 (V) | 0x21 (R low: converter table) | 1K0 959 433 CT / same | `KSG PQ35 RDK 052 0221` |
| 47 | Sound System | KWP/TP 2.0 (V) | unknown | 1K6 035 456 B / same | `08K Audioverst. 0006` |
| 55 | Headlight Range | KWP/TP 2.0 (V) | unknown | 1T0 907 357 | `Dynamische LWR 0003` (coding 0000004) |
| 56 | Radio | KWP/TP 2.0 (V) | 0x52 (R low: converter table) | 1K0 035 095 H | `Radio 0050` (coding 0010046) |
| 65 | Tire Pressure | = module 46 (V) | — | 1K0 959 433 CT | `RDK 0450` (coding 0100101) |

Not fitted / not scanned on this car: 62/72 (2-door), 76, 7D, 1C, 2E, 4F, 77.

### 2012 VW Golf TDI Mk6 (US) — scan B, `WVWNM7AJ2CW126467`, 7N0 gateway coding `350002`, no 02 (manual gearbox); DSG row from sibling scan C (2010 Jetta CJAA, 1K0 gateway) (registry §8 G)

| Addr | VCDS name | Protocol | TP 2.0 logical / UDS ids (status) | Part no. (SW / HW) | Component string |
|---|---|---|---|---|---|
| 01 | Engine (CJA, EDC17CP14) | **KWP/TP 2.0** (V: no ASAM/ROD in scans B and C; seishuku's 2013 Jetta `03L 906 019 HE` polled with TP 2.0 + `21 xx`; Ross-Tech "CAN protocol EDC" procedures). Generic OBD-II on 0x7E0/0x7E8 (V standard). UDS `22 F187` on 0x7E0: **untested** | TP 2.0 **0x01** → 0x201, tester TX 0x740 expected (V for the family) | 03L 906 019 EE / 03L 907 309 AA | `R4 2,0L EDC G000SG 1181` (coding 0050072, label 03L-906-022-CBE.clb) |
| 02 | Auto Trans (DQ250, if fitted) | KWP/TP 2.0 (V: scan C/D, no ASAM) | TP 2.0 0x02, tester TX 0x760 (R medium-high) | 02E 300 052 / 02E 927 770 AJ (scan C) | `GSG DSG AG6 440 1920` (coding 0000020) |
| 03 | ABS Brakes (J104) | KWP/TP 2.0 (V) — indirect TPMS lives here on 2011+ NAR cars | TP 2.0 0x03 (R medium) | 1K0 907 379 BJ / same | `ESP MK60EC1 H31 0121` (coding 114B400C49240000880F02EA92200042B70000) |
| 08 | Auto HVAC (J301) | **UDS** (V: ASAM EV_ACManueBHBVW36X / .rod) | **0x746 → 0x7B0** (V id; mapping high) | 7N0 907 426 AN / same | `AC Manuell H19 0304` (coding 0000001002) |
| 09 | Cent. Elect. (J519, BCM) | KWP/TP 2.0 (V) — may not answer with doors locked | 0x20 (R low) | 1K0 937 086 P / same | `BCM PQ35 M 110 0651` (30-byte coding; sub wiper 5K1 955 119) |
| 15 | Airbags (J234) | **UDS** (V) | **0x715 → 0x77F** (V id; high) | 5K0 959 655 H / same | `AirbagVW10G 013 0724` (coding 00003131) |
| 16 | Steering wheel (J527) | **UDS** on this build (V: EV_SMLSNGKUDS); the 1K0 953 549 CD variant (scan C) is KWP | **0x70C → 0x776** (V id; high) | 5K0 953 507 BC / 5K0 953 549 E | `Lenks.Modul 008 0080` (coding 108A140000) |
| 17 | Instruments (J285) | **UDS** (V: EV_Kombi_UDS_VDD_RM09) | **0x714 → 0x77E** (V id; high, also NefMoto "UDS ID is 714h") | 5K0 920 972 C / same | `KOMBI H03 0607` (coding 270F01) |
| 19 | CAN Gateway (J533, 7N0) | KWP/TP 2.0 (V: no ASAM in scans B and D) — installation list is a separate function, not the 3-byte coding | TP 2.0 0x1F (R: verified only for 1K0 907 530); UDS 0x710 → 0x77A (ODIS slot) — **test both** | 7N0 907 530 H / 1K0 907 951 | `J533 Gateway H42 1620` (coding 350002) |
| 1C | Position Sensing | KWP/TP 2.0 (V) | unknown | 5N0 919 879 / same | `Kompass 001 0001` (coding 0000002) |
| 25 | Immobilizer (J334, in cluster) | UDS (V) | 0x711 → 0x77B | 5K0 953 234 | `IMMO H03 0607` — **out of scope** |
| 2E | Media Player 3 (J650) | KWP/TP 2.0 (V) | unknown | 5N0 035 342 E / same | `SG EXT.PLAYER H13 0240` (coding 010000) |
| 42 / 52 | Door Elect. Driver / Pass. (GEN3) | KWP/TP 2.0 (V) | 0x22 (R low) | 5K0 959 701 H / 5K0 959 702 H | `Tuer-SG 009 2105` (coding 0001204) |
| 44 | Steering Assist (EPS) | KWP/TP 2.0 (V) | **0x09** → 0x209, tester TX 0x7A8 (V bench; this is the 1K0 909 144 family pq-flasher talks to) | 1K0 909 144 M | `EPS_ZFLS Kl. 70 3201` |
| 46 | Central Conv. | merged into 09 (V, Ross-Tech) — in scan list, prints no block | — | — | — |
| 56 | Radio (J503, RCD510) | KWP/TP 2.0 (V) | 0x52 (R low) | 1K0 035 180 AE / same | `Radio Prem-8 H02 0016` (coding 01000400040005) |
| 62 / 72 | Door Rear Left / Right (GEN3) | KWP/TP 2.0 (V) | unknown | 5K0 959 703 D / 5K0 959 704 D | `Tuer-SG 007 2101` (coding 0001168) |
| 77 | Telephone (J412) | **UDS** (V: EV_UHVNA) | **0x76B → 0x7D5** (V id) | 5K0 035 730 E / same | `TELEFON H09 2902` (coding 0A10040000010100) |

Not on this car but possible on the family (scan D, Passat NMS): 05 KESSY (UDS 0x732/0x79C), 2B ELV (UDS 0x731/0x79B),
36 seat memory (KWP), 47 10-ch amp (UDS 0x76F/0x7D9), 4F EZE_2 (KWP), GEN4 doors (UDS 0x74A/0x7B4, 0x74B/0x7B5 with
rear doors as sub-systems), 37/56 RNS-MID (KWP). 65 is absent on the 2012 Golf (indirect TPMS in 03).

**Rules the autoscan must follow (from these maps):** (1) never derive the TP 2.0 destination byte from the
address word — only 01/02/03 coincide; (2) never treat silence on an ODIS UDS id as "module absent" — on the R32
every module is KWP, on the Golf the engine/ABS/BCM/gateway/EPS/doors/radio are KWP; (3) identify every
responder by its `1A 9B` (KWP) or `22 F187` (UDS) part number, not by the id it answered on; (4) probe all 256
TP 2.0 destination bytes and all 0x700..0x7FF UDS ids, because the gateway's installation list is a configured
expectation (R32 scan A lists 22 as installed but unreachable).

---

## (b) What to implement

### Implement as verified (registry section in brackets)

Transport / hardware
- J2534 v04.04: the 14 entry points, `PASSTHRU_MSG` layout (`DataSize = 4 + payload`, big-endian id in `Data[0:4]`), RxStatus classification (TxDone 0x09, loopback 0x01, RxStart 0x02, pad error 0x10, 29-bit 0x100), TxFlags (`ISO15765_FRAME_PAD` 0x40), PASS/BLOCK/FLOW_CONTROL filter semantics (pass-all = mask 0/pattern 0, DataSize 4), `ERR_TIMEOUT` 0x09 vs `ERR_BUFFER_EMPTY` 0x10 vs `ERR_BUFFER_OVERFLOW` 0x12 (partial batch is data), the complete error-code table, SET_CONFIG parameters (ISO15765_BS 0x1E, STMIN 0x1F, BS_TX 0x22, STMIN_TX 0x23, WFT_MAX 0x25), never NULL `pInput`, **always a non-zero write timeout**, OpenPort 10 filters/10 periodics per channel, filter by id because the raw CAN channel echoes our own frames, 32-bit `op20pt32.dll` → 32-bit Python, `c_ulong` width per driver [§1].
- Functional OBD on an ISO15765 channel: 8 FLOW_CONTROL filters 0x7E8+i / flow 0x7E0+i, all with `ISO15765_FRAME_PAD` [§1 3.1].
- python-can: SocketCAN (`bitrate 500000 restart-ms 100`), gs_usb/candleLight, Kvaser, PCAN; slcan last resort (no hardware timestamps) [§1 §5]. ELM327/STN are OBD-II-only; refuse them for TP 2.0 [§1 §6].
- TP 2.0: setup `dest C0 00 10 00 03 01` on 0x200, reply `00 D0 rxlo rxhi txlo txhi 01` on 0x200+dest with validity nibbles 0 (parse both ids from the reply; never assume 0x740), negatives D6/D7/D8, `A0 0F 8A FF 32 FF` → `A1 BS T1 T2 T3 T4`, timing codec (`unit = (b>>6)`, `n = b & 0x3F`; 0x8A = 100 ms, 0x4A = 10 ms, 0x32 = 5 ms, 0x0A = 1 ms, 0xFF = 6300 ms), `A3` → `A1` keep-alive in both directions (answer an incoming A3 with our parameters), `A8` ↔ `A8`, `A4` treated as channel closed, data PCI `op<<4 | seq` with ops 0/1/2/3/B/9, 7 payload bytes per frame, 2-byte big-endian length in the first frame (mask with 0x7FFF), per-direction 4-bit sequence counters persisting across messages, ACK = `B0 | ((seq+1) & 0xF)` sent after op 0 or 1 only, sender waits ≤ T1 for the ACK, ACK-request on frame index BS−1, own inter-frame gap ≥ peer's T3, inline A3/A1 handling inside a response stream, `7F SID 78` arrives as a complete TP message that must be ACKed and then discarded, retransmit from the sequence carried in a NAK/mis-sequenced ACK (max 5 × 100 ms), only one channel per module (send A8 before re-opening; on D6..D8 send A8 to the tx id in the refusal, wait 300 ms, retry), multiple channels via 0x300..0x30F [§2, §7.3]. Reference state machine in §2 §8 (change its `REQ_PARAMS` T3 to 0x32 per conflict C7).
- ISO-TP / ISO 15765-4: 0x7DF single-frame functional requests, responses 0x7E8..0x7EF (+8), VAG extended range +0x6A, FC to the responder's physical id with `30 00 00`, DLC always 8, padding configurable (accept anything), N_As/N_Ar 25 ms / N_Bs 75 ms / N_Cr 150 ms for legislated OBD, P2CAN 50 ms, P2*CAN 5 s on NRC 0x78, `busyRepeatRequest` 0x21 retry after 200 ms up to 5 times, one reassembly per responder [§3].
- KWP2000: `SID [params]` with no framing, `+0x40` positive, `7F SID NRC`, 0x78 keep waiting without resending, 0x21/0x23 resend after a delay, `10 89` → `50 89` (repeatable), bare `3E` → `7E`, complete NRC table (PY's UDS-only codes excluded) [§4]. `1A 9B` → byte-exact record (0..10 part number, 11 = 0x20, 12..15 sw version, 16 coding type 00/03/10, 18..19 short coding BE, 20..25 WSC block, 26.. component text), `1A 91` → length-prefixed records until 0xFF (length counts itself), fallback 9B → 91, `7F 1A 11` for unknown options [§7.5]. `21 <group>` → `61 <group>` + fields `(formula, A, B)` walked **by formula id** (5F/76 length-prefixed, 3F rest-of-message, A0 = 5 data bytes), 8-field (26-byte) replies on PQ35 engines, consensus formula table 0x01–0xB5 (KL column), `7F 21 11/31` = no such group [§7.7]. `18 02 FF 00` (fallback `18 00 FF 00`) → `58 n` + n × `DTC_hi DTC_lo status`; status low nibble = VCDS elaboration code, bit 6 clear = Intermittent; `14 FF 00` → `54 FF 00`; 5-digit number = raw 16-bit value, P/C/B/U decimal rule for 0x4000–0x7FFF [§7.8]. `31 B8 00 00` capability query → `71 B8` + 01xx pairs (read-only) [§7.10]. `23 addr(3) size` → `63 data` (read-only probe, no byte skipped) [§4].
- UDS: SID table incl. 0x83, complete NRC table, `19 01/02/03/04/06/14` request and response layouts (snapshot/extended sizes must be supplied — return raw with the DID list when unknown), status-byte bits, DTCFormatIdentifier values, `14 FF FF FF` → `54`, `10 xx` → `50 xx P2(ms,16) P2*(10 ms,16)`, `3E 80`, `11 xx`, `28 ct cm`, `85 01/02`, `2F DID ctl [state]` layouts (returnControl 0, resetToDefault 1, freeze 2, shortTermAdjustment 3), `31 01/02/03 RID` layouts and RID ranges, ISO DIDs 0xF180–0xF19F, VAG DIDs (F187/F189/F191/F1A3/F197/F1AD/F19E/F1A2/F17C/F1F4/F1DF/F186/F18C/F1A5/F15B/0600/0405/0407/0408/295A/295B/F40D/F442), `22 06 00` long-coding read, F15B 10-byte records (BCD date, CRC8 poly 0x07), OBD-mirror DIDs 0xF4xx ↔ PID, 3-byte DTC = 2 SAE bytes + FTB, 6-digit number = decimal of the 2 SAE bytes, VCDS priority table [§5, §7.6, §7.8].
- OBD-II: everything in §6 — framing, Table 7 response rules (no answer = unsupported), supported-bitmap walker, the complete PID table with byte counts (needed to walk multi-PID replies), PID 4F/50 scaling override, PID 01/41 bit decode incl. the compression-ignition column, PID 03/12/1C/51/5F/65/13/1D enumerations, Mode 02 (`02 PID 00`), Modes 03/07 (`43 n` + 2-byte DTCs, `43 00` when none), Mode 04 (functional, `7F 04 22` possible), Mode 06 9-byte records + OBDMID/TID/UASID tables, Mode 08 TID 01, Mode 09 InfoTypes 02/04/06/08/0A/0B with NODI.
- VAG application data: ODIS UDS id table (90 rows, +0x6A rule, four shared slots), address-word names 01..7F/91..A3/B0..B6, Mk5 gateway long-coding layouts 1/2/3 (installation bitmap, bit-exact on three cars), DTC description DB `dtc_db.json` (strip the 42 placeholder rows and the 00543 joke text), the 83-row KWP elaboration table, the 31-row FTB consensus table (secondary sources — keep a provenance flag) [§7.1, §7.2, §7.4, §7.9].
- ECU knowledge as *label data* (not logic): VW standardized gasoline groups 000–137 for the R32, CJAA MVBs 002.4 / 011 / 099 / 100 / 108 / 240 / 241 / 086 / 089 / 046.2, DQ250 group list incl. 019 = three temperatures and the 060–069 basic-settings sequence, Haldex Gen2 groups 0x01/0x02/0x7D exist, ME7Logger `.ecu` parser (11 fields, `phys = A*raw − B`, inverse form, bitmask, 1/2-byte big-endian) [§9].

### Implement but flag UNVERIFIED (warn once; `confirm=True` for anything that writes)

- TP 2.0 logical addresses other than engine 0x01, EPS 0x09, Haldex Gen2 0x0A, gateway 0x1F: cluster 0x07 (medium), ABS 0x03 (medium), DSG 0x02 (medium-high), converter-table values 0x20/0x05/0x21/0x22/0x52 (low). Ship the table as a hint; fill it per car from the probe / `1A 9F` [§7.3 R].
- The `00 03 00 03` fallback setup form; the 0xD7 "stale channel" recovery; 500 ms keep-alive vs a ~1 s drop; KWP `3E` every ~1 s in addition to A3; T3 direction; BS = 15 [§2 R, §7.3].
- `1A 9F` gateway installation list: vag-blocks' parser (two length-prefixed records, 4-byte entries `[moduleNumber, tp20Address, ?, flags]`, bit0 present, bits1-4 status) — medium; dump the raw reply alongside [§7.4 R].
- 48-bit WSC/importer/equipment packing `v & 0x1FFFF / (v>>17) & 0x3FF / v>>27` (high, reproduces Basano's decoder) and the `5A 9A` long-coding record layout (medium) [§7.5 R].
- "8 fields = groups N and N+128" (medium) — show 8 fields raw, label the second half only after the on-car check [§7.7 R].
- Address word → UDS id inference table (Reported §1 of addresses) — use as the probe order, identify by F187 [§7.2 R].
- KWP status bits 4/5/7 (bit 7 = MIL low-medium), elaboration texts 002/003/005/006/009/015 (medium), `18 03 FF 00` supported-codes read (medium) — display only [§7.8 R].
- Formula variants kept as named alternates: 0x08 raw-16 (VB/PY), 0x14 VB/PY form, 0x0E/0x21/0x5E OpenHaldex forms for Haldex fields, 0x51 three-way split, 0x27 /255 vs /256, 0x2D ×100, 0x2E [§7.7 table; conflict C15].
- UDS: 0x2C ALFID 0x14 layout (medium-high), 0x2A format (medium), 0x4F session (low), coding write `2E 06 00` (medium — write, confirm=True), UDS adaptation = DID read/write + routine (medium, DIDs from ODX only), 0x19 06 record contents (medium), FTB rows outside the 31-row consensus (medium/low; autodtcs rows conflicting with the consensus flagged per C14), VCDS `[nnn]` bracket = decimal status byte (convention), `- NNN -` field decimal vs hex [§5 R, §7.6 R, §7.8 R, §7.9 R].
- OBD: Mode 0A payload `4A n …` (high), VW ECU pad byte 0xAA (low-medium), DSG answering functional OBD (medium), PID 0x68 length (medium), spark/compression readiness expectations for the two engines, PID 4F bytes B/C/D as further overrides (medium — implement only Data A and PID 50) [§6 R].
- J2534/Tactrix: RxStart = 0x02 (high), empty read → 0x10 (medium), `ReadMsgs(Timeout=1)` ≈ 6–8 ms overshoot (medium), pre-3.11 Windows `sleep` granularity (medium) [§1 R].
- ECU-level: ME7.1.1 group numbers beyond the standardized table and the 014/015 misfire offset (R-D1), DQ250 clutch-adaptation group 067 for SW 1405 (derive from the verified rule, confirm on car), CJAA group 020 field order, EGR reset channels 118/123 (medium), regeneration basic-settings group / driving-regen channel numbers (low), Haldex Gen2 group contents (low-medium), cluster adaptation channel list (verified for 1K6 920 97x but still label-driven) [§9 R].
- CLAUDE.md "verified" ABS 0x713/0x77D and Haldex 0x70F/0x779: keep as ODIS slots in `addresses.py`, mark "not expected on PQ35 KWP modules" (C27).

### Do not implement — support a raw-send + trace workflow instead (`kwp raw HEX`, `uds raw HEX`, `sniff`)

- KWP owner-level **writes** whose byte forms are only modelled (all low confidence): adaptation save `31 BB 01 03 …`, basic-settings start/stop `31 B8 01 01` / `32 B8 01 01`, output tests `31 B8 01 02` / `31 B9 01 02` / `31 B8 01 07`, login `31 B8 01 05` + `31 B9 01 05 <code>`, short-coding write `31 BB 01 04 …`, long-coding write (`3B 9A …`?), KWP freeze frame (`12 …` or a `18` status variant). Provide the read-only adaptation probe (`31 B8 01 03`, `31 B9 01 03 <ch>`, `31 BA 01 03`, `32 B8 01 03`) behind the UNVERIFIED flag, and a `kwp raw` command plus a sniffer so the real VCDS bytes can be captured on each car (§10). [§7.10 R]
- Any `27 xx` seed/key for coding/adaptation on KWP or UDS modules (level and algorithm unknown; algorithms are out of scope in any case). Record the level byte VCDS uses, nothing more. [§7.10]
- UDS DIDs behind VCDS's named adaptation channels (Mk6 cluster `ESI: Resetting ESI`, DPF carbon-mass reset, IMA-ISA) — ODX-only; capture with `uds raw`/sniff. [§7.6 R, §9 I]
- `1A 9F` *writes* / gateway installation-list editing (gateway coding write) — no byte layout known. [§7.4]
- ME7 RAM logging on the R32: ME7Logger does not support the Mk5 R32 image (ST10 bootrom), its `B7` handler method is unverified and bootrom-specific, and no R32 variable addresses exist. Implement the `.ecu` parser and a generic read-only `23` probe only; no logger profile for 022906032KR until Q1/Q2 are answered. [§9 B, §10 ecus Q1]
- TP 2.0 broadcast frames (0x23/0x24) and non-0x01 application types. [§2 §5]
- Mode 08 TID 01 (EVAP leak-test conditioning) — not a diagnostic read. [§6 §8]
- Everything out of scope: flashing services (0x34–0x37, 0x31 FF00/0202/0203, 0x85/0x02 programming sessions, KWP `31 C4/C5`, SA2 scripts), immobiliser (address 25, `10 84 14`, 0xEF90), `PassThruSetProgrammingVoltage`, the OpenPort `atx` bootloader command.

---

## (c) Conflicts between sheets and how they were settled

Full register with both sides quoted: registry §0 (C1–C28). Summary of the decisions taken for 0.2.0:

| # | conflict | decision | status |
|---|---|---|---|
| C1 | TP 2.0 BS 0x0F = 15 or 16 frames | ACK-request on frame index BS−1, never >15 unacknowledged; receiver tolerates either | unresolved on the wire — tp20 Q4 / addresses Q11 |
| C2 | HVAC UDS id 0x744/0x7AE (brief) vs 0x746/0x7B0 (ODIS) | 0x746/0x7B0; 46 is 0x70D/0x777 | resolved |
| C3 | EDC17CP14/CJAA = UDS (uds_vag, j2534, obd2 headers; DESIGN/CLAUDE) vs KWP/TP 2.0 (addresses §D, ecus §F1) | KWP2000 over TP 2.0 at 0x01 (three independent verified sources); the DESIGN table's "ABS, gateway, BCM are UDS" is also wrong for the 2012 Golf (scans B/C/D). Still probe `0x7E0: 03 22 F1 87` once | resolved; one experiment left |
| C4 | setup frame `00 10 00 03` vs `00 03 00 03` (MED17.5) | first form first, second on silence | unresolved — addresses Q13 |
| C5 | who sends `A0` | tester sends A0, module answers A1 (traces beat JAZDW's table text) | resolved |
| C6 | reply to incoming `A3`: `A3` or `A1` | `A1` + our parameters | resolved |
| C7 | default T3 0x4A (tp20 §8 code) / 0x0A (PQF) / 0x32 (addresses, OpenHaldex) | 0x32 (5 ms); 0x0A degraded a MED17.5 | resolved |
| C8 | tester TX id 0x740 hard-coded | parse the `D0` reply (0x740 / 0x7A8 / 0x764 / 0x760 seen) | resolved |
| C9 | keep-alive 500 ms vs ~1 s channel drop | A3 ≤ 500 ms idle; measure the true timeout | resolved for implementation; tp20 Q2 |
| C10 | Haldex 0x22 vs 0x0A | 0x0A | resolved |
| C11 | gateway 0x19 vs 0x1F | 0x1F | resolved |
| C12 | KWP DTC hex-nibble (scirocco-dash) vs decimal rule | decimal (`N5 = raw16`), triple-verified | resolved |
| C13 | KWP `58` records 2 vs 3 bytes | 3 bytes | resolved |
| C14 | FTB 0x15/0x1C/0x1D/0x71/0x72 (autodtcs vs vinfast+neomotive) | neomotive/vinfast consensus primary; autodtcs rows flagged | unresolved — dtc_db Q3 |
| C15 | formula ids 0x04/0x08/0x12/0x14/0x19/0x27/0x2D/0x2E/0x51/0x5E/0x0E/0x21 | KL consensus column; alternates retained as named variants | unresolved per id — kwp Q10 |
| C16 | misfire groups 014/015 vs 015/016 | label-driven; default to the standardized table | unresolved — ecus Q4 |
| C17 | SA level 0x11/0x12 (CLAUDE) unsourced | demoted to Reported; irrelevant to 0.2.0 diagnostics | resolved (demoted) |
| C18 | pad byte 0x00/0xCC/0x55/0xAA | configurable tester pad, accept anything; log what ECUs send | resolved |
| C19 | Tactrix write Timeout=0 behaviour | always non-zero timeout | resolved |
| C20 | Tactrix DLL delivers raw CAN frames to the ISO15765 channel when both are open | `j2534` kind = CAN channel only (software ISO-TP + TP 2.0); `j2534-fw` separately; test on native Windows | unresolved — j2534 OQ1 |
| C21 | J2534 integer width | per-driver (`c_ulong` Windows/bisak, `c_uint32` roffe) | resolved |
| C22 | PID 0x68 3 vs 7 bytes | use the ECU's own PCI length; never combine 0x68 | unresolved — obd2 Q3 |
| C23 | PID 1C values 14–16 | newer J1979-DA assignment | resolved |
| C24 | UASID 0x2E boolean vs percent | boolean, log raw | unresolved in the standard |
| C25 | `63` reply byte skip (bri3d) | no skip | resolved |
| C26 | KWP status bit 7 = MIL | display only, flagged | unresolved — kwp Q3 |
| C27 | CLAUDE.md ABS/Haldex UDS ids "verified" | correct ODIS slots, but not the protocol of these cars' modules | resolved (reinterpreted) |
| C28 | `5A 9B` part-number description | same bytes; use the offset table | not a conflict |

Also noted (no action): `tp20.md` and `addresses.md` repeat the TP 2.0 frame formats — both copies kept (§2, §7.3) because the second carries the on-car exceptions; `obd2.md` §1 is placed under ISO-TP (§3) and referenced from §6.

---

## (d) Top open questions — only the real cars can answer (ignition on, engine off unless stated; 500 kbit/s, 11-bit, DLC 8)

The full list (100 items) is registry §10. These are the ones that gate 0.2.0 features, with the exact frames.

1. **Build each car's TP 2.0 address table and tester-TX ids** (gates autoscan and every KWP module).
   For `dest` in 0x00..0xFF: send `0x200: dest C0 00 10 00 03 01`; wait 300 ms for `0x200+dest`; on silence after ~11 tries 50 ms apart retry once with `dest C0 00 03 00 03 01`; on `00 D0 00 03 xx 0y 01` record tester-TX = `(0y<<8)|xx`, send `A0 0F 8A FF 32 FF` on it, expect `A1 …` on 0x300, then `10 00 02 10 89` → `B1` → `10 00 02 50 89`, then `11 00 02 1A 9B` and log the whole `5A 9B` record (fallback `1A 91`); close with `A8`. On `D6/D7/D8` send `A8` to the tx id in bytes 4–5, wait 300 ms, retry. Expected: R32 — 0x01 (0x740), 0x02 (0x760), 0x03, 0x07, 0x09 (0x7A8), 0x0A (0x764), 0x1F; Golf — 0x01, 0x03, 0x09, 0x1F plus whatever the BCM/doors/radio/compass answer on. Record which bytes answer but are not real modules (identify by `1A 9B`).
2. **Gateway installation list**: on the channel to 0x1F send `1A 9F`; dump raw. R32: expect records matching the 22 modules decoded from coding `ED831F075003020000` and a status word (0000 / 0010 / 1100). Golf (7N0): also try UDS `0x710: 03 22 F1 87 55 55 55 55` → `0x77A: … 62 F1 87 …`; if it answers, scan DIDs 0x0600..0x06FF and 0xF1xx for a list-shaped payload.
3. **Which modules are UDS**: for every request id in the ODIS table plus 0x7E0..0x7E7 send `03 22 F1 87 55 55 55 55`, wait 100 ms for `id+0x6A` (or +8); repeat after `02 10 03` for modules that refuse in default session. Expect on the Golf: 0x714, 0x711, 0x715, 0x746, 0x70C, 0x76B. On both cars test the engine once: `0x7E0: 02 10 03 55 55 55 55 55` and `03 22 F1 87 …` — decides whether `identify --module 01` uses UDS, KWP/TP 2.0 or OBD-II only (C3).
4. **OBD-II responder map and bitmaps**: `0x7DF: 02 01 00 …` → log every 0x7E8..0x7EF with its 4-byte bitmap; then per responder `01 00 20 40 60 80 A0` and `01 C0 E0`, `02 00 00 20 00 40 00`, `06 00 20 40 60 80 A0`, `08 00`, `09 00`, bare `0A`; `0x7E1: 02 01 00` physically for the DSG. Record pad bytes in the replies and the FirstFrame/FC behaviour of `09 04` with FC padding 00/55/AA.
5. **KWP DTC bytes and status on the R32**: with a stored fault (or after unplugging the MAF briefly → P0101) send `18 02 FF 00` then `18 00 FF 00`; expect `58 01 40 65 ss` (0x4065 = 16485 = P0101, decimal rule) not `01 01`; compare `ss` low nibble with VCDS's "- NNN -" text and bit 6 with "Intermittent"; also `18 03 FF 00`. Then `14 FF 00` → `54 FF 00`.
6. **FTB decimal vs hex and the 0x1C/0x71 rows on the TDI**: `19 02 FF` on each UDS module → `59 02 mask` + 4-byte records; pair each third byte with VCDS's `- NNN -` field for the same fault (one electrical fault provoked by unplugging a sensor, one intermittent by re-plugging before clearing). Settles C14 and the bracket convention.
7. **8-field groups**: on the R32 engine `21 02` and `21 82` (and `21 01` / `21 81`, `21 00`); if `21 82` is refused (`7F 21 31`) or equals bytes 12..23 of the `61 02` reply, the N/N+128 rule holds.
8. **Owner-level function bytes** (gates the whole §7.10 write side): with VCDS (HEX-CAN) and a passive CAN sniffer on the OBD port, capture (a) TBA basic settings group 060 on the R32 engine and 061/060 on the DSG, (b) an adaptation channel read on the cluster, (c) a Login with a deliberately wrong code on the engine, (d) one ABS output test, (e) a coding read (`[07]`). Expect `31 B8 01 xx` / `31 B9` / `31 BA` / `31 BB` / `32 B8` forms, or `21 <group>` after a session switch, or `30 <lid>` for output tests, or `27 xx`; record session byte, request/response bytes and timing.
9. **TP 2.0 block size and idle timeout**: send a ≥16-frame request (e.g. a 110-byte `3B`/`2C` definition that the module will refuse harmlessly, or read a long `18 00 FF 00` reply on a module with many DTCs) and count frames before the ACK wait; then open 0x01, send `10 89`, stop all traffic and log the time until `A8`/silence; repeat with `A3` every 1 s, 2 s, 5 s; then after 15 s of A3-only keep-alive send `21 02` to see whether the 0x89 session needs `3E`.
10. **WSC packing and `1A 9A`**: compare bytes 20..25 of each module's `5A 9B` with VCDS's `Shop #: WSC xxxxx yyy zzzzz` line for the same car (R32 engine prints `01279 785 00200`); send `1A 9A` to the long-coded engine and compare with its coding.
11. **Formula-id disagreements on real fields**: Haldex 0x0A groups `21 01`, `21 02`, `21 7D` after `10 89` — any `0E xx yy` / `21 xx yy` / `5E xx yy` field with A ≠ 100 / B ≠ 200 discriminates OpenHaldex's forms from KL's; compare with VCDS group 001/002/125 of address 22. Likewise engine fields using 0x08/0x14/0x19/0x27 vs VCDS display.
12. **CJAA group map**: `21 g` for g = 0x01..0xFF on the engine channel; identify 011 (rpm / boost spec / boost act / N75 %), 020 (rail pressure — blip the throttle: specified leads), 099 (EGT ×3), 108/241 (soot), 240 (since-regen), 086/089 (readiness; compare with `0x7E0: 02 01 01` at the same moment), 046.2 (coolant), 118/123 adaptation names (read only).
13. **DQ250**: dest 0x02 `1A 9B` (expect `02E300011CC … GSG DSG 082 1405`), `21 13` with brake pressed and engine running (three temperatures), and while VCDS runs group 061/060/067 log `21 3C`/`21 3D`/`21 43` to learn which service carries "Basic Settings".
14. **Tactrix on native Windows**: open CAN(5) + ISO15765(6) together, send `01 00` to 0x7DF on the ISO15765 channel and see which channel delivers the raw frames (C20); log `RxStatus`/`DataSize`/`ExtraDataIndex` of every message during one `identify` (expect TxDone 0x09/4 bytes, RxStart 0x02, loopback 0x01 with four zero bytes); 1000 × `PassThruReadMsgs(Timeout=1)` on an idle channel for the real poll granularity; confirm 0x09 vs 0x10 on an empty read.
15. **ME7.1.1 RAM read**: on the R32 engine channel send `23 00 F8 88 01` and `2C F0 03 01 00 F8 88 02` + `21 F0`; log `63 …` / `6C F0` vs `7F 23/2C nrc` (0x11/0x12/0x33/0x80). Decides whether any RAM logging is possible on that car at all (the `.ecu` format is only a container until Q2 provides addresses).
