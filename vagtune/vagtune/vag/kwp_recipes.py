"""
Owner-level KWP2000 *write* functions as documented byte recipes - deliberately
**not** as functions that send bytes.

Why (``docs/IMPLEMENTATION_NOTES.md`` (b) "Do not implement"): the byte forms of
login (VCDS function 11 / Coding-II), coding writes, adaptation save, basic-settings
start/stop and output tests on KWP2000-over-TP 2.0 modules are only *modelled* from
one real adaptation sequence (bri3d, a KWP2000 cluster) and the ``31 B8 00 00``
capability list; no fetched open-source tool writes coding, logs in or runs a basic
setting over TP 2.0, and PyVCDS's own implementation is ``NotImplementedError("Need
VCDS Trace to figure out KWP commands")``. All of them are REPORTED in
``docs/PROTOCOL_FACTS.md`` §7.10 at low (coding, login, basic settings, output
tests) or medium (adaptation) confidence, and every one of them *writes* to a
module. Rule 8.1 of ``DESIGN_0.2.md`` says nothing REPORTED may drive a write; the
notes go further and say: do not implement, provide the raw-send + trace workflow.

So this module ships a :data:`RECIPES` table that a user can

(a) read with ``kwp recipes`` - name, purpose, modelled request bytes with
    placeholders, expected reply, confidence, evidence and the exact VCDS-capture
    experiment that would verify it (IMPLEMENTATION_NOTES (d) item 8), and
(b) turn into bytes deliberately with :func:`render` for ``kwp raw --yes`` once the
    placeholders are filled in by hand.

:class:`vagtune.vag.kwp_session.VagKwpSession` raises ``NotImplementedError`` from
``login`` / ``write_coding`` / ``write_adaptation`` / ``basic_settings`` /
``output_test`` and points here. The only ``31 B8/B9/BA`` sequence the session does
send is the *read-only* adaptation probe (no ``31 BB`` save), flagged UNVERIFIED.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Dict, List, Mapping, Optional, Tuple, Union

from .dtc import warn_unverified

#: IMPLEMENTATION_NOTES (d) item 8 - the capture experiment every recipe points to.
EXPERIMENT_ITEM_8 = (
    "With VCDS (HEX-CAN) and a passive CAN sniffer on the OBD port, capture (a) TBA basic settings "
    "group 060 on the R32 engine and 061/060 on the DSG, (b) an adaptation channel read on the cluster, "
    "(c) a Login with a deliberately wrong code on the engine, (d) one ABS output test, (e) a coding read "
    "([07]). Expect `31 B8 01 xx` / `31 B9` / `31 BA` / `31 BB` / `32 B8` forms, or `21 <group>` after a "
    "session switch, or `30 <lid>` for output tests, or `27 xx`; record session byte, request/response "
    "bytes and timing."
)

_PLACEHOLDER_RE = re.compile(r"<([a-z0-9_]+)(?::(\d+))?>")
_BYTES_PLACEHOLDER_RE = re.compile(r"<([a-z0-9_]+)\.\.\.>")


@dataclass(frozen=True)
class Recipe:
    """One modelled owner-level function.

    ``request`` is a hex template; ``<name>`` is a 1-byte placeholder, ``<name:N>`` an
    N-byte big-endian one. ``writes`` is True for everything that changes module
    state. ``confidence`` is the registry's word for the byte form.
    """
    name: str
    vcds_function: str
    purpose: str
    request: str
    expected_reply: str
    confidence: str
    evidence: str
    experiment: str
    writes: bool = True
    preconditions: Tuple[str, ...] = ()
    notes: str = ""

    @property
    def placeholders(self) -> List[Tuple[str, int]]:
        """``(name, width)`` per placeholder; width 0 = variable-length bytes."""
        out = [(m.group(1), 0) for m in _BYTES_PLACEHOLDER_RE.finditer(self.request)]
        out += [(m.group(1), int(m.group(2) or 1)) for m in _PLACEHOLDER_RE.finditer(self.request)]
        return out

    @property
    def steps(self) -> List[str]:
        """The request templates, one per ``;``-separated step, comments stripped."""
        return [_strip_comment(s) for s in self.request.split(";")]

    def describe(self) -> str:
        lines = [
            f"{self.name}  [{self.vcds_function}]  confidence: {self.confidence}  "
            f"{'WRITES to the module' if self.writes else 'read-only'}",
            f"  purpose : {self.purpose}",
            f"  request : {self.request}",
            f"  reply   : {self.expected_reply}",
            f"  evidence: {self.evidence}",
        ]
        if self.preconditions:
            lines.append("  before  : " + "; ".join(self.preconditions))
        if self.notes:
            lines.append(f"  notes   : {self.notes}")
        lines.append(f"  verify  : {self.experiment}")
        return "\n".join(lines)


_ADAPT_EVIDENCE = (
    "bri3d DiagnosticSession.java clearCayenneClusterServiceIndicator (KWP2000 cluster): 31 B8 01 03 -> "
    "31 BA 01 03 -> 31 B9 01 03 02 -> 31 BA 01 03 -> 31 B9 01 03 00 00 -> 31 BA 01 03 -> "
    "31 BB 01 03 00 00 00 00 04 50 10 34 -> 31 BA 01 03 -> 31 B8 01 03; the 6 trailing bytes of the save "
    "are the WSC/importer/equipment block of the 5A 9B record (registry 7.10 verified sequence; the "
    "generalisation to every module and the 01xx function model are REPORTED)"
)

RECIPES: Tuple[Recipe, ...] = (
    Recipe(
        name="login",
        vcds_function="11 Login / Coding-II (16 Security Access)",
        purpose="enable adaptation/coding on modules that need the 5-digit code (and feature enables such as "
                "cruise control on ME7)",
        request="31 B8 01 05 ; 31 B9 01 05 <code:2>",
        expected_reply="71 B8 01 05 ; 71 B9 01 05 (7F 31 xx on a wrong code)",
        confidence="low (byte layout) / medium (that it is a 0x31 routine, not 27 xx)",
        evidence="DV capability code 0105 'Coding-II possible'; a Bosch 5.7 ABS answered 7F 27 11 to every 27 xx "
                 "while VCDS Login works on it (NEFM-20104); no fetched tool sends the login",
        experiment=EXPERIMENT_ITEM_8 + " Specifically (c): sniff a Login with a wrong code; expect 31 B8 01 05 / "
                   "31 B9 01 05 <code> or 27 xx.",
        preconditions=("10 89 session", "know the module's real login code (ME7 engines: 12233 reported, "
                       "R32: check the repair manual); wrong codes lock the module after a few attempts"),
        notes="Some modules do implement 27 01/02 with the PIN 'added to the seed unsigned' (NEFM-20104). "
              "Only the level byte VCDS uses should be recorded; no seed/key algorithm is implemented.",
    ),
    Recipe(
        name="coding-write-short",
        vcds_function="07 Recode (short coding, 0..65535)",
        purpose="write the 16-bit short coding of a type-03 module (what 5A 9B offsets 18..19 show)",
        request="31 BB 01 04 <coding:2> <wsc:6>",
        expected_reply="71 BB 01 04 (model) - then re-read 1A 9B and compare offsets 18..19",
        confidence="low",
        evidence="0104 '20-bit coding possible' capability code (DV); modelled on the bri3d adaptation save form; "
                 "PyVCDS setLongCode is NotImplementedError('Need VCDS Trace')",
        experiment=EXPERIMENT_ITEM_8 + " Specifically (e): a coding read then a recode to the SAME value on a "
                   "harmless module; capture the write bytes.",
        preconditions=("backup: full 5A 9B record saved", "Login if the module requires it",
                       "WSC/importer/equipment packed per the REPORTED 48-bit rule (pack_wsc_block)"),
        notes="Alternative: a 0104 routine variant; nobody has seen either on the wire.",
    ),
    Recipe(
        name="coding-write-long",
        vcds_function="07 Recode (long coding, up to 255 bytes)",
        purpose="write the long coding record of a type-10 module (what 1A 9A returns)",
        request="3B 9A <wsc:6> <sw_version...> 10 <len> <coding...> FF",
        expected_reply="7B 9A (model)",
        confidence="low",
        evidence="1A 9A read record from a single sniffed sample (VDS); the write form is a guess "
                 "(writeDataByLocalIdentifier of the same record) - no fetched code does it",
        experiment=EXPERIMENT_ITEM_8 + " Capture VCDS recoding the gateway (1K0 907 530 L, long coding) to its "
                   "current value; expect 3B 9A ... or 31 BB 01 04 ...",
        preconditions=("backup: full 5A 9B and 5A 9A records saved", "identity must match the backup"),
        notes="<sw_version...> is the 4 ASCII digits, <coding...> the long-coding bytes, <len> counts itself "
              "(1 + len(coding)); a 31 BB 01 04 routine variant is just as likely.",
    ),
    Recipe(
        name="adaptation-save",
        vcds_function="10 Adaptation [Save]",
        purpose="store a new value in an adaptation channel",
        request="31 B8 01 03 ; 31 B9 01 03 <channel> ; 31 B9 01 03 <value:2> ; 31 BB 01 03 <value:2> <wsc:6> ; 32 B8 01 03",
        expected_reply="71 B8 01 03 ; 71 B9 01 03 ... ; 71 BB 01 03 ... ; 72 B8 01 03",
        confidence="medium (one real implementation on one module)",
        evidence=_ADAPT_EVIDENCE,
        experiment=EXPERIMENT_ITEM_8 + " Specifically (b): an adaptation channel read, [Test] and a [Save] of the "
                   "unchanged value on the cluster.",
        preconditions=("backup: current channel value read first (read_adaptation_probe)",
                       "Login where the module requires it", "channel 00 save resets ALL adaptations (VCDS)"),
        notes="Steps: start, select channel, [Test] value, [Save] value + WSC block, stop. The read-only part "
              "(31 B8 01 03 / 31 B9 01 03 <ch> / 31 BA 01 03 / 32 B8 01 03) is implemented as "
              "VagKwpSession.read_adaptation_probe, flagged UNVERIFIED; the 31 BB save is not.",
    ),
    Recipe(
        name="basic-settings-start",
        vcds_function="04 Basic Settings [ON]",
        purpose="start a basic setting (e.g. throttle body adaptation group 060, DSG 060/061/067)",
        request="31 B8 01 01 ; 21 <group> ; 32 B8 01 01",
        expected_reply="71 B8 01 01 ; 61 <group> ... ; 72 B8 01 01",
        confidence="low",
        evidence="0101 'basic settings in KWP1281 mode' capability code (DV); VCDS tour says the measuring "
                 "values stay visible with an ON/OFF button; the sequence is a model",
        experiment=EXPERIMENT_ITEM_8 + " Specifically (a): TBA group 060 on the R32 engine and 061/060 on the "
                   "DSG; record whether the group number rides in 31 B8 01 01 <group> or in 21 <group>.",
        preconditions=("engine-specific preconditions (no DTCs, voltage > 11.5 V, coolant 5..95 C for TBA)",
                       "a wrong basic setting can change adaptation values"),
        notes="Steps: start (31 B8 01 01), then poll the group with 21 <group> while it runs, then stop "
              "(32 B8 01 01). Whether the group number rides in the 31 B8 request is unknown.",
    ),
    Recipe(
        name="basic-settings-stop",
        vcds_function="04 Basic Settings [OFF]",
        purpose="leave basic settings",
        request="32 B8 01 01",
        expected_reply="72 B8 01 01",
        confidence="low",
        evidence="stop form of the 0101 model (ISO 32 = stopRoutineByLocalIdentifier)",
        experiment=EXPERIMENT_ITEM_8 + " (a) - the [OFF] click of the same capture.",
    ),
    Recipe(
        name="output-test-sequential",
        vcds_function="03 Output Tests (fixed sequence)",
        purpose="run the module's actuator sequence; the module names each actuator by a fault-code number",
        request="31 B8 01 02 ; 31 B9 01 02",
        expected_reply="71 B8 01 02 <dtc_hi dtc_lo> ... (model)",
        confidence="low",
        evidence="0102 'output tests with fixed sequence' capability code (DV); VCDS: 'The ECU identifies which "
                 "output it is currently testing by sending a fault-code number'; 'only one time per session'",
        experiment=EXPERIMENT_ITEM_8 + " Specifically (d): one ABS output test; expect 31 B8 01 02 / 31 B9 "
                   "forms or 30 <lid> (inputOutputControlByLocalIdentifier).",
        preconditions=("engine not running", "most modules allow the sequence once per session"),
        notes="Each further 31 B9 01 02 is modelled to advance to the next actuator.",
    ),
    Recipe(
        name="output-test-selective",
        vcds_function="03 Output Tests (selective)",
        purpose="drive one named actuator",
        request="31 B8 01 07 <actuator_code:2>",
        expected_reply="71 B8 01 07 ... (model)",
        confidence="low",
        evidence="0107 'output tests with selective sequence' capability code (DV); needs label-file data for "
                 "the actuator codes (VCDS)",
        experiment=EXPERIMENT_ITEM_8 + " (d) with a selective test if the ABS label offers one.",
        preconditions=("engine not running",),
        notes="Alternative ISO form: 30 <lid> <controlParameter> (inputOutputControlByLocalIdentifier).",
    ),
    Recipe(
        name="security-access-27",
        vcds_function="16 Security Access (seed/key)",
        purpose="record which 27 xx level a module asks for; no key algorithm is implemented",
        request="27 <level>",
        expected_reply="67 <level> <seed...> or 7F 27 11 on modules that use the 0105 routine instead",
        confidence="low (level); algorithm out of scope",
        evidence="NEFM-20104: Bosch 5.7 ABS answers 7F 27 11; 'PIN added to the seed unsigned' on others; "
                 "VW_Flash fake data uses 27 03/04 (simulated, not proof)",
        experiment="Record the level byte VCDS sends on each module (sniff a Login / Security Access); nothing more.",
        writes=False,
        notes="Odd level = requestSeed. Only the level byte is to be recorded; sending a key is out of scope.",
    ),
    Recipe(
        name="freeze-frame-read",
        vcds_function="02 Fault Codes [Display Freeze Frame Data]",
        purpose="read priority / frequency / reset counter / mileage / time for a stored fault",
        request="12 <frame> 04 <dtc:2>",
        expected_reply="52 ... (ISO 8.4) - layout unknown",
        confidence="low",
        evidence="ISO 14230-3 readFreezeFrameData layout; VCDS shows the field names; no fetched VAG tool reads it",
        experiment="With a stored fault send 12 00 04 <dtc>, 12 01 04 <dtc>, 12 00 00, 18 03 FF 00 and 18 04 FF 00; "
                   "compare the bytes with VCDS's Fault Priority / Frequency / Reset counter / Mileage line "
                   "(registry 10.4 item 4).",
        writes=False,
        notes="Alternatives: 18 03 FF 00 / 18 04 FF 00 (a VAG status variant of readDTCByStatus).",
    ),
)

RECIPE_BY_NAME: Dict[str, Recipe] = {r.name: r for r in RECIPES}

#: The owner-level functions DESIGN_0.2 names on VagKwpSession that are NOT
#: implemented as byte-sending methods, mapped to the recipe(s) that document them.
WRITE_FUNCTIONS: Dict[str, Tuple[str, ...]] = {
    "login": ("login", "security-access-27"),
    "write_coding": ("coding-write-short", "coding-write-long"),
    "write_adaptation": ("adaptation-save",),
    "basic_settings": ("basic-settings-start", "basic-settings-stop"),
    "output_test": ("output-test-sequential", "output-test-selective"),
}


def recipes() -> List[Recipe]:
    return list(RECIPES)


def get_recipe(name: str) -> Recipe:
    try:
        return RECIPE_BY_NAME[name.strip().lower()]
    except KeyError:
        raise KeyError(f"no recipe {name!r}; known: {', '.join(RECIPE_BY_NAME)}") from None


def format_table() -> str:
    """The ``kwp recipes`` text."""
    head = ("Owner-level KWP2000 functions - MODELLED byte forms, not implemented as commands "
            "(IMPLEMENTATION_NOTES (b): capture VCDS first; send deliberately with `kwp raw --yes`).")
    return head + "\n\n" + "\n\n".join(r.describe() for r in RECIPES)


def not_implemented(function: str) -> NotImplementedError:
    """The exception VagKwpSession raises for a DESIGN-named write function."""
    names = WRITE_FUNCTIONS.get(function, ())
    which = ", ".join(names) if names else function
    return NotImplementedError(
        f"VagKwpSession.{function}: the KWP2000 byte form of this VAG function is only modelled "
        f"(registry 7.10 REPORTED, confidence low/medium) and it writes to the module. Missing: a VCDS "
        f"capture of the real request/response bytes on the car (IMPLEMENTATION_NOTES (d) item 8). "
        f"See `kwp recipes` ({which}) and send the bytes deliberately with `kwp raw --yes`.")


def pack_wsc_block(wsc: int, importer: int, equipment: int) -> bytes:
    """Inverse of the REPORTED 48-bit packing (``v = wsc | importer << 17 | equipment
    << 27``, big-endian 6 bytes) used in the 5A 9B record and the adaptation save.

    UNVERIFIED (registry 7.5 REPORTED, high): reproduces four samples and Basano's
    decoder but no fetched source pairs the bytes with a VCDS "Shop #" line. Warns once.
    """
    # UNVERIFIED: WSC/importer/equipment packing (registry 7.5 Reported, high).
    if not 0 <= wsc <= 0x1FFFF or not 0 <= importer <= 0x3FF or not 0 <= equipment <= 0x1FFFFF:
        raise ValueError("wsc must be 0..131071, importer 0..1023, equipment 0..2097151")
    warn_unverified("wsc-packing",
                    "WSC/importer/equipment 48-bit packing (v & 0x1FFFF / v>>17 & 0x3FF / v>>27) is REPORTED "
                    "(high); compare 5A 9B bytes 20..25 with a VCDS 'Shop #' line to confirm")
    v = (wsc & 0x1FFFF) | ((importer & 0x3FF) << 17) | ((equipment & 0x1FFFFF) << 27)
    return v.to_bytes(6, "big")


def _strip_comment(template: str) -> str:
    """Text after ``(`` in a template step is a comment (``A (or B)``: the first form
    renders; the alternative is documentation only)."""
    return template.split("(", 1)[0].strip()


def render(recipe_or_name, values: Optional[Mapping[str, Union[int, bytes]]] = None, *,
           step: int = 0) -> bytes:
    """Fill a recipe's placeholders and return the bytes of its ``step``-th request
    (templates separated by ``;``). Every placeholder must be supplied explicitly;
    text after ``(`` in a template is a comment and ignored. Alternatives written
    as ``A (or B)`` render the first form only.

    A ``<name:N>`` placeholder takes an int (rendered big-endian in N bytes; too
    large raises ``OverflowError``) or exactly N bytes - a bytes value of another
    length raises ``ValueError`` naming the placeholder and both lengths, because
    every recipe that takes one *writes* to the module and a misaligned WSC block or
    value field must never go out silently. ``<name...>`` takes bytes of any length.
    """
    recipe = recipe_or_name if isinstance(recipe_or_name, Recipe) else get_recipe(recipe_or_name)
    values = dict(values or {})
    steps = [_strip_comment(s) for s in recipe.request.split(";")]
    if not 0 <= step < len(steps):
        raise IndexError(f"recipe {recipe.name!r} has {len(steps)} step(s)")
    template = steps[step]
    out = bytearray()
    for token in template.split():
        if token.startswith("<"):
            m = _BYTES_PLACEHOLDER_RE.fullmatch(token)
            if m is not None:
                name = m.group(1)
                if name not in values:
                    raise KeyError(f"recipe {recipe.name!r} step {step} needs bytes for <{name}...>")
                out += bytes(values[name])
                continue
            m = _PLACEHOLDER_RE.fullmatch(token)
            if m is None:
                raise ValueError(f"bad placeholder {token!r} in recipe {recipe.name!r}")
            name, width = m.group(1), int(m.group(2) or 1)
            if name not in values:
                raise KeyError(f"recipe {recipe.name!r} step {step} needs a value for <{name}>")
            v = values[name]
            if isinstance(v, (bytes, bytearray)):
                if len(v) != width:
                    raise ValueError(f"recipe {recipe.name!r} step {step}: <{name}:{width}> needs exactly "
                                     f"{width} byte(s), got {len(v)} ({bytes(v).hex(' ')})")
                out += bytes(v)
            elif isinstance(v, bool) or not isinstance(v, int):
                raise TypeError(f"recipe {recipe.name!r} step {step}: <{name}> takes an int or {width} bytes, "
                                f"not {type(v).__name__}")
            else:
                if v < 0:
                    raise ValueError(f"recipe {recipe.name!r} step {step}: <{name}> must not be negative")
                out += v.to_bytes(width, "big")      # OverflowError when it does not fit
        else:
            out.append(int(token, 16))
    if recipe.writes:
        warn_unverified(f"recipe:{recipe.name}",
                        f"recipe {recipe.name!r} rendered: its byte form is {recipe.confidence} confidence and "
                        "it writes to the module; only send it deliberately after a backup")
    return bytes(out)


__all__ = ["Recipe", "RECIPES", "RECIPE_BY_NAME", "WRITE_FUNCTIONS", "EXPERIMENT_ITEM_8",
           "recipes", "get_recipe", "format_table", "not_implemented", "pack_wsc_block", "render"]
