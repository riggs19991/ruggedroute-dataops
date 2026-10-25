"""T-0012: parcels `use` bucket — land-use classification.

One new whitelisted tile attribute with a closed 7-value vocabulary
(RES AG VAC COM IND FOREST GOV) that must match the Android client's USE_LABELS
exactly. Each wired unit's sources.json use_field/use_adapter pair routes its
assessment class through one adapter; the pins below are the values harvested
live on 2026-10-25 (service distinct-value queries, DBF reads, live-tile
decodes). Unknown/unmapped values yield None and the attribute is OMITTED —
never an "OTHER" bucket. qa_parcels re-gates the vocabulary on the normalized
output (Gate 1) and on decoded tiles (Gate 3).
"""

import importlib.util
import io
import json
import re
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

_LAYER = Path(__file__).resolve().parents[1]

_spec = importlib.util.spec_from_file_location("normalize_parcels_t0012", _LAYER / "normalize_parcels.py")
norm = importlib.util.module_from_spec(_spec)
sys.modules["normalize_parcels_t0012"] = norm
_spec.loader.exec_module(norm)

_qa_spec = importlib.util.spec_from_file_location("qa_parcels_t0012", _LAYER / "qa_parcels.py")
qa = importlib.util.module_from_spec(_qa_spec)
sys.modules["qa_parcels_t0012"] = qa
_qa_spec.loader.exec_module(qa)

VOCAB = {"RES", "AG", "VAC", "COM", "IND", "FOREST", "GOV"}

# adapter -> [(harvested raw value, expected bucket or None)] — brief-01 §6.
PINS = {
    "fl_dor": [
        ("000", "VAC"), ("001", "RES"), ("012", "COM"), ("048", "IND"),
        ("054", "FOREST"), ("060", "AG"), ("071", "GOV"), ("083", "GOV"),
        ("091", None), ("", None), ("XX", None),
    ],
    "ma_dor": [
        ("0101", "RES"), ("0300", "COM"), ("0400", "IND"), ("0601", "FOREST"),
        ("0712", "AG"), ("0900", "GOV"),
        ("010C", None),  # letter suffix -> omit
        ("0200", None),  # 2xx open space -> omit
        ("013", None),   # '13' after the zero-strip: too short -> omit
    ],
    "in_dlgf": [
        ("100", "AG"), ("199", "AG"), ("300", "IND"), ("400", "COM"),
        ("510", "RES"), ("600", "GOV"), ("000", None), ("068", None),
    ],
    "nj_modiv": [
        ("1", "VAC"), ("2", "RES"), ("3A", "AG"), ("3B", "AG"), ("4A", "COM"),
        ("4B", "IND"), ("4C", "RES"), ("15A", "GOV"), ("15F", "GOV"),
        ("5A", None), ("6A", None),
    ],
    "dc_class": [
        ("1A", "RES"), ("1B", "RES"), ("2", "COM"), ("3", "VAC"), ("4", "VAC"), ("", None),
    ],
    "wi_propclass": [
        ("1", "RES"), ("1,2,4", "RES"), ("4,5", "AG"), ("5M", "FOREST"), ("6", "FOREST"),
        ("5", "VAC"), ("7", None), ("2", "COM"),
    ],
    "mt_proptype": [
        ("VAC_R - Vacant Land - Rural", "VAC"), ("Vacant Land", "VAC"),
        ("Industrial Property", "IND"), ("IR - Industrial Rural", "IND"),
        ("Gravel Pit", "IND"), ("Oilfield Improvements", "IND"),
        ("Apartment", "RES"), ("Condominium", "RES"), ("Townhouse", "RES"),
        ("Mobile/RV Parks", "RES"), ("Exempt Property", "GOV"),
        ("Tribal Property", "GOV"), ("CA - Centrally Assessed", "GOV"),
        ("Locally Assessed Utility", "GOV"), ("Golf Course", "COM"),
        ("Improved Property", None), ("", None),
    ],
}

# unit -> (use_field, use_adapter) — brief-01 §2 wiring, minus NJ (run
# 40243912707: the statewide parcels gdb has no PROP_CLASS — that field lives
# on the MOD-IV composite SERVICE; FGDB -select hard-fails on unknown names).
WIRING = {
    "FL_1": ("DOR_UC", "fl_dor"), "FL_2": ("DOR_UC", "fl_dor"),
    "MA": ("USE_CODE", "ma_dor"), "IN": ("dlgf_prop_class_code", "in_dlgf"),
    "DC": ("CLASSTYPE", "dc_class"),
    "WI": ("PROPCLASS", "wi_propclass"), "MT": ("PropType", "mt_proptype"),
}
V1_STATES = ("FL", "MA", "IN", "DC", "WI", "MT")
# Probe-excluded 2026-10-25 — must never be wired blind. NJ joined after the
# live run proved its gdb lacks the field (future route: MOD-IV composite).
EXCLUDED_UNITS = ("TX_1", "TX_2", "TX_3", "CT", "MD", "VT", "HI", "NJ")
EXCLUDED_STATES = ("TX", "CT", "MD", "VT", "HI", "NJ")

FL_MAPPING = {"apn": "PARCEL_ID", "county": "CO_NO", "acres": "LND_SQFOOT"}
FL_RAW = {"PARCEL_ID": "X1", "CO_NO": "58.0", "LND_SQFOOT": "87120", "DOR_UC": "001"}


def _sources() -> dict:
    return json.loads((_LAYER / "sources.json").read_text(encoding="utf-8"))


# ── §1 adapters: harvested pins ──────────────────────────────────────────────

class AdapterPinsTest(unittest.TestCase):
    def _check(self, name):
        adapter = norm.USE_ADAPTERS[name]
        for raw, want in PINS[name]:
            with self.subTest(adapter=name, raw=raw):
                self.assertEqual(want, adapter(raw))

    def test_fl_dor(self):
        self._check("fl_dor")

    def test_ma_dor(self):
        self._check("ma_dor")

    def test_in_dlgf(self):
        self._check("in_dlgf")

    def test_nj_modiv(self):
        self._check("nj_modiv")

    def test_dc_class(self):
        self._check("dc_class")

    def test_wi_propclass(self):
        self._check("wi_propclass")

    def test_mt_proptype(self):
        self._check("mt_proptype")

    def test_registry_is_exactly_the_seven_pinned_adapters(self):
        self.assertEqual(set(PINS), set(norm.USE_ADAPTERS))
        self.assertIs(norm._use_fl_dor, norm.USE_ADAPTERS["fl_dor"])
        self.assertIs(norm._use_ma_dor, norm.USE_ADAPTERS["ma_dor"])
        self.assertIs(norm._use_in_dlgf, norm.USE_ADAPTERS["in_dlgf"])
        self.assertIs(norm._use_nj_modiv, norm.USE_ADAPTERS["nj_modiv"])
        self.assertIs(norm._use_dc_class, norm.USE_ADAPTERS["dc_class"])
        self.assertIs(norm._use_wi_propclass, norm.USE_ADAPTERS["wi_propclass"])
        self.assertIs(norm._use_mt_proptype, norm.USE_ADAPTERS["mt_proptype"])


class VocabularyTest(unittest.TestCase):
    def test_use_buckets_is_the_closed_seven_value_set(self):
        self.assertIsInstance(norm.USE_BUCKETS, frozenset)
        self.assertEqual(frozenset(VOCAB), norm.USE_BUCKETS)
        self.assertNotIn("OTHER", norm.USE_BUCKETS)

    def test_adapter_outputs_stay_inside_the_vocabulary(self):
        produced = {norm.USE_ADAPTERS[name](raw) for name, pins in PINS.items() for raw, _ in pins}
        produced.discard(None)
        self.assertLessEqual(produced, norm.USE_BUCKETS)
        # ...and the pinned harvest exercises every one of the 7 buckets
        self.assertEqual(VOCAB, produced)

    def test_both_whitelists_gain_use_in_lockstep(self):
        self.assertEqual(("apn", "county", "acres", "st", "use"), norm.WHITELIST)
        self.assertEqual(set(norm.WHITELIST), qa.WHITELIST)
        self.assertEqual(norm.USE_BUCKETS, qa.USE_BUCKETS)


# ── §1 plumbing: build_props ─────────────────────────────────────────────────

class BuildPropsUseTest(unittest.TestCase):
    def test_fl_dor_uc_buckets_into_use(self):
        props = norm.build_props(dict(FL_RAW), FL_MAPPING, "FL", acres_divisor=43560,
                                 use_field="DOR_UC", use_adapter="fl_dor")
        # T-0009 county translation and acres_divisor still apply alongside use
        self.assertEqual({"st": "FL", "apn": "X1", "county": "Orange", "acres": 2.0, "use": "RES"}, props)
        self.assertLessEqual(set(props), qa.WHITELIST)

    def test_without_use_field_there_is_no_use_key(self):
        props = norm.build_props(dict(FL_RAW), FL_MAPPING, "FL", acres_divisor=43560)
        self.assertEqual({"st": "FL", "apn": "X1", "county": "Orange", "acres": 2.0}, props)
        # an adapter without a field emits nothing either
        props = norm.build_props(dict(FL_RAW), FL_MAPPING, "FL", acres_divisor=43560,
                                 use_adapter="fl_dor")
        self.assertNotIn("use", props)

    def test_recased_header_found_through_lower_index(self):
        props = norm.build_props({"dor_uc": "054"}, FL_MAPPING, "FL",
                                 use_field="DOR_UC", use_adapter="fl_dor")
        self.assertEqual({"st": "FL", "use": "FOREST"}, props)

    def test_nullish_and_unmapped_values_omit_use(self):
        for raw in (" null ", "", "<Null>", "091", "XX"):
            with self.subTest(raw=raw):
                props = norm.build_props({"DOR_UC": raw}, FL_MAPPING, "FL",
                                         use_field="DOR_UC", use_adapter="fl_dor")
                self.assertEqual({"st": "FL"}, props)

    def test_raw_source_value_never_ships(self):
        props = norm.build_props({"MAP_PAR_ID": "12-3", "USE_CODE": "0101"},
                                 {"apn": "MAP_PAR_ID", "county": None, "acres": "LOT_SIZE"}, "MA",
                                 use_field="USE_CODE", use_adapter="ma_dor")
        self.assertEqual({"st": "MA", "apn": "12-3", "use": "RES"}, props)
        self.assertNotIn("0101", props.values())

    def test_junk_adapter_output_cannot_leak(self):
        for junk in ("RANCH", "OTHER", "res", "", 7, ["RES"]):
            with self.subTest(junk=junk), \
                 mock.patch.dict(norm.USE_ADAPTERS, {"fl_dor": lambda v, j=junk: j}):
                props = norm.build_props(dict(FL_RAW), FL_MAPPING, "FL", acres_divisor=43560,
                                         use_field="DOR_UC", use_adapter="fl_dor")
                self.assertNotIn("use", props)
                self.assertEqual("Orange", props["county"])

    def test_adapter_error_omits_use_instead_of_crashing(self):
        def boom(v):
            raise ValueError("odd upstream code")
        with mock.patch.dict(norm.USE_ADAPTERS, {"fl_dor": boom}):
            props = norm.build_props(dict(FL_RAW), FL_MAPPING, "FL", acres_divisor=43560,
                                     use_field="DOR_UC", use_adapter="fl_dor")
        self.assertEqual({"st": "FL", "apn": "X1", "county": "Orange", "acres": 2.0}, props)


class UseFieldScreeningTest(unittest.TestCase):
    def test_owner_or_address_use_field_is_refused(self):
        for field in ("OWNER_CLASS", "MAIL_USE", "own_use", "TAXPAYER_CL", "ADDR_USE"):
            with self.subTest(field=field), self.assertRaises(SystemExit):
                norm.check_mapping({"apn": "PIN", "county": None, "acres": None, "use": field})

    def test_non_apn_name_exemption_covers_the_use_role(self):
        norm.check_mapping({"apn": "PIN", "county": None, "acres": None, "use": "USE_NAME"})

    def test_every_wired_use_field_passes_the_screen(self):
        for field, _ in WIRING.values():
            norm.check_mapping({"use": field})


# ── §1 plumbing: main() reads + validates the sources.json pair ──────────────

class MainUseConfigTest(unittest.TestCase):
    BASE = {"fields": {"apn": "PIN", "county": None, "acres": None}}

    def _run_main(self, unit_cfg, fake_normalize=None):
        if fake_normalize is None:
            fake_normalize = mock.Mock(side_effect=AssertionError("normalize must not run"))
        with tempfile.TemporaryDirectory() as td:
            td = Path(td)
            (td / "sources.json").write_text(json.dumps({"ZZ": unit_cfg}), encoding="utf-8")
            argv = ["normalize_parcels.py", "--unit", "ZZ", "--src", str(td / "in.geojsonl"),
                    "--out", str(td / "build")]
            with mock.patch.object(norm, "__file__", str(td / "normalize_parcels.py")), \
                 mock.patch.object(sys, "argv", argv), \
                 mock.patch.object(norm, "normalize", fake_normalize), \
                 redirect_stdout(io.StringIO()):
                norm.main()
        return fake_normalize

    def _exit_message(self, unit_cfg) -> str:
        with self.assertRaises(SystemExit) as cm:
            self._run_main(unit_cfg)
        return str(cm.exception.code)

    @staticmethod
    def _recording_normalize():
        def fake(srcs, layer_hint, mapping, state, out_path, stats, *args, **kwargs):
            stats["kept"] = 1
        return mock.Mock(side_effect=fake)

    def test_unknown_adapter_name_exits_with_a_clear_message(self):
        msg = self._exit_message({**self.BASE, "use_field": "LANDUSE", "use_adapter": "no_such_adapter"})
        self.assertIn("unknown use_adapter 'no_such_adapter'", msg)
        self.assertIn("fl_dor", msg)  # names the known adapters

    def test_half_configured_pair_exits(self):
        self.assertIn("together", self._exit_message({**self.BASE, "use_field": "LANDUSE"}))
        self.assertIn("together", self._exit_message({**self.BASE, "use_adapter": "fl_dor"}))

    def test_forbidden_use_field_is_refused_before_anything_runs(self):
        msg = self._exit_message({**self.BASE, "use_field": "OWNER_CLASS", "use_adapter": "fl_dor"})
        self.assertIn("REFUSING mapping use='OWNER_CLASS'", msg)

    def test_configured_pair_reaches_normalize_but_not_the_mapping(self):
        fake = self._run_main({**self.BASE, "use_field": "DOR_UC", "use_adapter": "fl_dor"},
                              self._recording_normalize())
        call = fake.call_args
        self.assertEqual("DOR_UC", call.kwargs["use_field"])
        self.assertEqual("fl_dor", call.kwargs["use_adapter"])
        # use_field never joins the apn/county/acres mapping (extraction loop)
        self.assertEqual({"apn": "PIN", "county": None, "acres": None}, call.args[2])

    def test_unconfigured_unit_passes_none(self):
        fake = self._run_main(dict(self.BASE), self._recording_normalize())
        self.assertIsNone(fake.call_args.kwargs["use_field"])
        self.assertIsNone(fake.call_args.kwargs["use_adapter"])


# ── §1 plumbing: normalize() -select + null-rate stats ───────────────────────

def _fake_stream(props_list):
    fake = mock.Mock()
    fake.stdout = io.StringIO("".join(
        json.dumps({"type": "Feature", "geometry": {"type": "Point", "coordinates": [0, 1]},
                    "properties": p}) + "\n" for p in props_list))
    fake.wait = lambda: 0
    return fake


class NormalizeUseStatsTest(unittest.TestCase):
    FEATURES = [
        {"PARCEL_ID": "A", "CO_NO": "58", "DOR_UC": "001"},  # -> RES
        {"PARCEL_ID": "B", "DOR_UC": "091"},                 # unmapped -> omitted
        {"PARCEL_ID": "C"},                                  # column absent
    ]

    def _normalize(self, props_list, **use):
        stats: dict = {}
        with tempfile.TemporaryDirectory() as td, \
             mock.patch.object(norm, "ogr_stream", return_value=_fake_stream(props_list)) as ogr, \
             mock.patch.object(norm, "resolve_src", side_effect=lambda s: s), \
             redirect_stdout(io.StringIO()) as printed:
            out = Path(td) / "out.geojsonl"
            norm.normalize(["fake.zip"], None, dict(FL_MAPPING), "FL", out, stats,
                           acres_divisor=43560, **use)
            features = [json.loads(line) for line in out.read_text(encoding="utf-8").splitlines()]
        selected = ogr.call_args.args[2]
        return stats, selected, printed.getvalue(), features

    def test_configured_unit_selects_the_column_and_reports_its_rate(self):
        stats, selected, printed, features = self._normalize(
            self.FEATURES, use_field="DOR_UC", use_adapter="fl_dor")
        self.assertEqual(["PARCEL_ID", "CO_NO", "LND_SQFOOT", "DOR_UC"], selected)
        self.assertEqual("RES", features[0]["properties"]["use"])
        self.assertNotIn("use", features[1]["properties"])
        self.assertNotIn("use", features[2]["properties"])
        self.assertEqual(round(2 / 3, 4), stats["attr_null_rates"]["use"])
        self.assertIn(f"use={round(2 / 3, 4)}", printed)

    def test_configured_but_empty_is_1_0(self):
        stats, _, _, _ = self._normalize([{"PARCEL_ID": "A"}, {"PARCEL_ID": "B"}],
                                         use_field="DOR_UC", use_adapter="fl_dor")
        self.assertEqual(1.0, stats["attr_null_rates"]["use"])

    def test_not_configured_is_none_not_1_0(self):
        stats, selected, printed, features = self._normalize(self.FEATURES)
        self.assertIsNone(stats["attr_null_rates"]["use"])
        self.assertIn("use=None", printed)
        self.assertNotIn("DOR_UC", selected)
        self.assertTrue(all("use" not in f["properties"] for f in features))

    def test_t0009_rates_unchanged_by_use(self):
        with_use, _, _, _ = self._normalize(self.FEATURES, use_field="DOR_UC", use_adapter="fl_dor")
        without, _, _, _ = self._normalize(self.FEATURES)
        for attr in ("apn", "county", "acres"):
            self.assertEqual(without["attr_null_rates"][attr], with_use["attr_null_rates"][attr])
        self.assertEqual(0.0, with_use["attr_null_rates"]["apn"])
        self.assertEqual(round(2 / 3, 4), with_use["attr_null_rates"]["county"])
        self.assertEqual(3, with_use["kept"])


# ── §3 fetch_parcels.sh rest mode requests use_field ─────────────────────────

def _fields_snippet() -> str:
    text = (_LAYER / "fetch_parcels.sh").read_text(encoding="utf-8")
    m = re.search(r'FIELDS="\$\(python3 - "\$SOURCES" "\$UNIT" <<\'PY\'\n(.*?)\nPY\n', text, re.S)
    assert m, "rest-mode FIELDS heredoc not found in fetch_parcels.sh"
    return m.group(1)


def _rest_fields(sources_path: Path, unit: str) -> str:
    """Run the rest-mode FIELDS snippet exactly as the heredoc does (python3 - SOURCES UNIT)."""
    return subprocess.run([sys.executable, "-", str(sources_path), unit], input=_fields_snippet(),
                          capture_output=True, text=True, check=True).stdout.strip()


class FetchRestFieldsTest(unittest.TestCase):
    def test_ma_esridump_requests_use_code(self):
        self.assertEqual("MAP_PAR_ID,LOT_SIZE,USE_CODE", _rest_fields(_LAYER / "sources.json", "MA"))

    def test_units_without_use_field_are_unchanged(self):
        self.assertEqual("PARCEL_ID,County", _rest_fields(_LAYER / "sources.json", "UT"))

    def test_use_field_dedups_and_keeps_order(self):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "sources.json"
            p.write_text(json.dumps({"X": {"fields": {"apn": "A", "county": "B", "acres": None},
                                           "use_field": "B"}}), encoding="utf-8")
            self.assertEqual("A,B", _rest_fields(p, "X"))

    def test_ma_is_the_only_rest_unit_with_a_use_field(self):
        rest_use = {u for u, c in _sources().items()
                    if isinstance(c, dict) and c.get("mode") == "rest" and c.get("use_field")}
        self.assertEqual({"MA"}, rest_use)


# ── §2 sources.json wiring ───────────────────────────────────────────────────

class SourcesWiringTest(unittest.TestCase):
    def test_exactly_the_seven_v1_states_are_wired(self):
        wired = {u: (c.get("use_field"), c.get("use_adapter")) for u, c in _sources().items()
                 if isinstance(c, dict) and ("use_field" in c or "use_adapter" in c)}
        self.assertEqual(WIRING, wired)
        self.assertEqual(set(V1_STATES), {u.split("_")[0] for u in wired})

    def test_probe_excluded_units_stay_unwired(self):
        src = _sources()
        for unit in EXCLUDED_UNITS:
            with self.subTest(unit=unit):
                self.assertIn(unit, src)
                self.assertNotIn("use_field", src[unit])
                self.assertNotIn("use_adapter", src[unit])

    def test_wired_adapters_resolve_and_notes_name_the_probe(self):
        src = _sources()
        for unit, (_, adapter) in WIRING.items():
            with self.subTest(unit=unit):
                self.assertIn(adapter, norm.USE_ADAPTERS)
                self.assertIn("2026-10-25", src[unit]["notes"])


# ── §5 layer.json contract ───────────────────────────────────────────────────

class LayerContractTest(unittest.TestCase):
    def setUp(self):
        self.layer = json.loads((_LAYER / "layer.json").read_text(encoding="utf-8"))

    def test_use_schema_documents_buckets_states_lockstep_and_exclusions(self):
        doc = self.layer["schema"]["parcels"]["use"]
        for token in sorted(VOCAB) + list(V1_STATES) + list(EXCLUDED_STATES) + ["USE_LABELS", "lockstep"]:
            with self.subTest(token=token):
                self.assertRegex(doc, rf"\b{token}\b")

    def test_schema_keys_are_the_qa_whitelist(self):
        self.assertEqual(qa.WHITELIST, set(self.layer["schema"]["parcels"]))

    def test_qa_section_notes_the_vocabulary_gate_beside_the_whitelist(self):
        gates = self.layer["qa"]
        self.assertIn("use_vocabulary", gates)
        self.assertIn("{apn, county, acres, st, use}", gates["attribute_whitelist"])
        for bucket in VOCAB:
            self.assertIn(bucket, gates["use_vocabulary"])


# ── §4 qa_parcels vocabulary gate: Gate 1 scan + Gate 3 tile loop ────────────

def _write_geojsonl(path: Path, props_list) -> None:
    with path.open("w", encoding="utf-8") as f:
        for props in props_list:
            f.write(json.dumps({"type": "Feature",
                                "geometry": {"type": "Point", "coordinates": [0, 0]},
                                "properties": props}) + "\n")


class QaUseVocabularyGateTest(unittest.TestCase):
    def _gate1(self, props_list):
        with tempfile.TemporaryDirectory() as td:
            p = Path(td) / "parcels.geojsonl"
            _write_geojsonl(p, props_list)
            return qa.gate_whitelist(p)

    def _gate3(self, props_list):
        tile = {"parcels": {"extent": 4096, "features": [{"properties": p} for p in props_list]}}
        with mock.patch.object(qa, "pmtiles_bounds", return_value=(-82.0, 27.0, -80.0, 29.0)), \
             mock.patch.object(qa, "decode_tile", return_value=tile):
            return qa.gate_tiles(Path("ignored.pmtiles"))

    def test_gate1_accepts_every_bucket_and_absent_use(self):
        failures, count = self._gate1([{"st": "FL", "use": b} for b in sorted(VOCAB)] + [{"st": "FL"}])
        self.assertEqual([], failures)
        self.assertEqual(8, count)

    def test_gate1_fails_out_of_vocabulary_values(self):
        failures, count = self._gate1([
            {"st": "FL", "use": "RES"}, {"st": "FL", "use": "RANCH"}, {"st": "FL", "use": "RANCH"},
            {"st": "FL", "use": "res"}, {"st": "FL", "use": None}, {"st": "FL", "use": ["RES"]},
        ])
        self.assertEqual(6, count)
        self.assertEqual(4, len(failures), failures)  # one line per distinct bad value
        self.assertTrue(any(f.startswith("use vocabulary violation: 'RANCH' on 2 features")
                            for f in failures), failures)
        for shown in ("'res'", "None", "['RES']"):
            self.assertTrue(any(f.startswith(f"use vocabulary violation: {shown} on 1 features")
                                for f in failures), shown)

    def test_gate3_clean_tile_passes(self):
        self.assertEqual([], self._gate3([{"st": "FL", "use": "AG"}, {"st": "FL"}]))

    def test_gate3_fails_out_of_vocabulary_tile_value(self):
        failures = self._gate3([{"st": "FL", "use": "GOV"}, {"st": "FL", "use": "OTHER"}])
        self.assertTrue(failures)
        for f in failures:
            self.assertRegex(f, r"^tile \d+/\d+/\d+: use vocabulary violation: 'OTHER'$")

    def test_gate3_whitelist_break_does_not_mask_the_vocab_check(self):
        failures = self._gate3([{"st": "FL", "owner": "JANE Q PUBLIC"}, {"st": "FL", "use": "RANCH"}])
        self.assertTrue(any("non-whitelisted keys ['owner']" in f for f in failures), failures)
        self.assertTrue(any("use vocabulary violation: 'RANCH'" in f for f in failures), failures)


if __name__ == "__main__":
    unittest.main()
