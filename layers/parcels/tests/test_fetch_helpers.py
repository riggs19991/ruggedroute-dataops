"""fetch_helpers: the hub download/v1 poller must survive transient endpoint
failures, and sources.json must keep MN on the gis.data.mn.gov hub item.

Why: the Q4 scheduled run 37349704081 (2026-10-05) lost ND to a single HTTP 400
on the first poll and MN to a dead GDRS bulk URL (gisdata.mn.gov moved to an
ArcGIS Hub). Nothing here touches the network: every endpoint answer is a
scripted fake (fixtures over live services; the live check is the `probe`
CLI mode, run outside the test suite).
"""

import io
import json
import sys
import urllib.error
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))
import fetch_helpers as fh  # noqa: E402

SOURCES = json.loads((Path(__file__).parent.parent / "sources.json").read_text(encoding="utf-8"))
URL = "https://hub.example/api/download/v1/items/abc/filegdb?redirect=false&layers=0"

MN_ITEM = "69148d3959194a05a23964cc60f6517b"
# Fields of layer 1 "Plan Parcels Open" of
# https://enterprise.gisdata.mn.gov/aghost/rest/services/us_mn_state_mngeo/plan_parcels_open/FeatureServer
# as published on 2026-10-12, frozen here so the mapping is checked without a live query.
MN_LIVE_FIELDS_2026_10_12 = {
    "objectid", "county_pin", "state_pin", "anumberpre", "anumber", "anumbersuf", "st_pre_mod",
    "st_pre_dir", "st_pre_typ", "st_pre_sep", "st_name", "st_pos_typ", "st_pos_dir", "st_pos_mod",
    "sub_type1", "sub_id1", "sub_type2", "sub_id2", "zip", "zip4", "ctu_name", "ctu_id_txt", "postcomm",
    "co_code", "co_name", "state_code", "lot", "block", "plat_name", "owner_name", "owner_more",
    "own_add_l1", "own_add_l2", "own_add_l3", "own_add_l4", "tax_name", "tax_add_l1", "tax_add_l2",
    "tax_add_l3", "tax_add_l4", "landmark", "homestead", "acres_poly", "acres_deed", "emv_land",
    "emv_bldg", "emv_total", "tax_year", "mkt_year", "tax_capac", "total_tax", "spec_asses",
    "useclass1", "useclass2", "useclass3", "useclass4", "multi_uses", "tax_exempt", "xuseclass1",
    "xuseclass2", "xuseclass3", "xuseclass4", "dwell_type", "home_style", "fin_sq_ft", "garage",
    "garagesqft", "basement", "heating", "cooling", "year_built", "num_units", "sale_date",
    "sale_value", "green_acre", "open_space", "ag_preserv", "agpre_enrd", "agpre_expd", "abb_legal",
    "edit_date", "exp_date", "polyptrel", "n_standard", "ownership", "school_dst", "wshd_dst",
    "section", "township", "range", "range_dir", "prin_mer", "Shape__Area", "Shape__Length",
}


class FakeClock:
    """Monotonic clock that only advances when the poller sleeps."""

    def __init__(self):
        self.t = 0.0

    def __call__(self):
        return self.t

    def sleep(self, seconds):
        self.t += seconds


def http_error(code, body=b""):
    reason = {400: "Bad Request", 500: "Internal Server Error"}.get(code, "Error")
    return urllib.error.HTTPError(URL, code, reason, {}, io.BytesIO(body))


def scripted(answers):
    """fetch(url) that returns or raises the scripted answers in order, repeating the last one.

    A callable answer is invoked per poll so each raised HTTPError carries a
    fresh body stream, as a real urlopen failure would."""
    calls = []

    def fetch(url):
        calls.append(url)
        answer = answers[min(len(calls) - 1, len(answers) - 1)]
        if callable(answer):
            answer = answer()
        if isinstance(answer, BaseException):
            raise answer
        return answer

    fetch.calls = calls
    return fetch


def envelope(**fields):
    return json.dumps(fields).encode()


COMPLETED = envelope(status="Completed", resultUrl="https://hub.example/result.zip")


def poll(fetch, clock, log=None, **kw):
    return fh.poll_hub_job(URL, fetch=fetch, sleep=clock.sleep, clock=clock,
                           log=(log.append if log is not None else (lambda m: None)), **kw)


def test_hub_poll_retries_a_first_poll_http_400_then_completes():
    fetch = scripted([
        http_error(400, b'{"message":["layers must not be less than 0"],"error":"Bad Request"}'),
        envelope(status="Pending", message="Up to date download file is being generated."),
        COMPLETED,
    ])
    clock, log = FakeClock(), []
    job = poll(fetch, clock, log, interval_s=15)
    assert job["resultUrl"] == "https://hub.example/result.zip"
    assert len(fetch.calls) == 3
    assert clock.t == 30                      # two waits of 15 s, none before the first poll
    assert any("HTTP 400" in m and "layers must not be less than 0" in m for m in log), log


def test_hub_poll_survives_network_error_and_html_body():
    fetch = scripted([urllib.error.URLError("connection reset"), b"<html>503 upstream</html>", COMPLETED])
    clock, log = FakeClock(), []
    job = poll(fetch, clock, log)
    assert job["resultUrl"] == "https://hub.example/result.zip"
    assert len(fetch.calls) == 3
    assert any("URLError" in m for m in log), log
    assert any("JSONDecodeError" in m and "503 upstream" in m for m in log), log   # the body itself is logged


def test_hub_poll_waits_out_exporting_status_and_a_result_less_completed():
    fetch = scripted([
        envelope(status="ExportingData", resultUrl=None, progressInPercent=0),
        envelope(status="Completed"),          # no resultUrl yet: keep polling
        COMPLETED,
    ])
    clock = FakeClock()
    job = poll(fetch, clock)
    assert job["resultUrl"] and len(fetch.calls) == 3


def test_hub_poll_gives_up_after_the_deadline_naming_the_last_error():
    fetch = scripted([lambda: http_error(500, b"gateway exploded")])
    clock = FakeClock()
    with pytest.raises(fh.HubJobError) as err:
        poll(fetch, clock, deadline_s=60, interval_s=15)
    assert "HTTP 500" in str(err.value) and "gateway exploded" in str(err.value)
    assert clock.t > 60 and len(fetch.calls) >= 5


def test_hub_download_streams_the_result_and_refuses_tiny_files(tmp_path):
    job = {"status": "Completed", "resultUrl": "https://hub.example/result.zip"}
    streamed = []

    def stream(url, out):
        streamed.append(url)
        out.write_bytes(b"PK" + b"\0" * 2000)
        return 2002

    fh.hub(URL, str(tmp_path / "ok.dl"), poll=lambda u: job, stream=stream)
    assert streamed == ["https://hub.example/result.zip"]

    def tiny(url, out):
        out.write_bytes(b"{}")
        return 2

    with pytest.raises(SystemExit):
        fh.hub(URL, str(tmp_path / "tiny.dl"), poll=lambda u: job, stream=tiny)


def test_hub_download_exits_nonzero_when_the_job_never_completes(tmp_path):
    def never(url):
        raise fh.HubJobError("hub download never completed")

    with pytest.raises(SystemExit) as err:
        fh.hub(URL, str(tmp_path / "x.dl"), poll=never, stream=lambda u, o: 0)
    assert "never completed" in str(err.value.code)


def test_hub_probe_accepts_a_pending_envelope_and_rejects_non_envelopes():
    fetch = scripted([http_error(400, b"nope"), envelope(status="Pending", message="being generated")])
    clock = FakeClock()
    job = fh.probe(URL, fetch=fetch, sleep=clock.sleep, clock=clock, deadline_s=60, interval_s=10,
                   log=lambda m: None)
    assert job["status"] == "Pending" and len(fetch.calls) == 2

    not_a_job = scripted([b'{"hello": "world"}'])
    clock = FakeClock()
    with pytest.raises(fh.HubJobError):
        fh.probe(URL, fetch=not_a_job, sleep=clock.sleep, clock=clock, deadline_s=20, interval_s=10,
                 log=lambda m: None)


def test_sources_mn_is_the_hub_fgdb_export_of_layer_1_of_the_new_item():
    mn = SOURCES["MN"]
    assert mn["mode"] == "hub"
    assert len(mn["urls"]) == 1
    url = mn["urls"][0]
    assert url.startswith(f"https://gis.data.mn.gov/api/download/v1/items/{MN_ITEM}/filegdb")
    assert "redirect=false" in url
    assert "layers=1" in url                  # layer 0 is the per-county metadata polygons
    assert "resources.gisdata.mn.gov" not in url
    assert "layer" not in mn                  # single-class export; the hub does not publish the class name


def test_sources_mn_mapping_uses_only_live_non_owner_fields():
    mapping = SOURCES["MN"]["fields"]
    assert mapping == {"apn": "state_pin", "county": "co_name", "acres": "acres_poly"}
    assert set(mapping.values()) <= MN_LIVE_FIELDS_2026_10_12
    forbidden = ("owner", "own_add", "tax_name", "tax_add")
    assert not [v for v in mapping.values() if any(f in v for f in forbidden)]


def test_sources_hub_entries_all_use_the_job_api_with_redirect_false():
    hub_units = [u for u, c in SOURCES.items() if isinstance(c, dict) and c.get("mode") == "hub"]
    assert "MN" in hub_units and "ND" in hub_units
    for unit in hub_units:
        url = SOURCES[unit]["urls"][0]
        assert "/api/download/v1/items/" in url and "redirect=false" in url, unit
