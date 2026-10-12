#!/usr/bin/env python3
"""Stage 3 parcels fetch helpers for the two non-trivial source shapes.

hub    — ArcGIS Hub download/v1 API with redirect=false returns a JSON job
         envelope, NOT the file (VT, ME, ND, MN). Poll until status=Completed,
         then stream resultUrl (an ephemeral signed blob, ~1h expiry — never
         cache it; re-request the API every run). Every poll failure is
         retryable until the deadline: see poll_hub_job.

probe  — one bounded look at a hub job endpoint; exits 0 on ANY job envelope
         (Pending counts). Used as a live source check, never in tests.

tnris  — TX StratMap land parcels ship as 254 per-county zips listed by the
         api.tnris.org resources manifest (paginated JSON, no auth). County
         FIPS is embedded in every zip filename, so shard filtering needs no
         attribute reads. Each shard downloads its FIPS range.

Usage:
    fetch_helpers.py hub   <api_url> <out_file>
    fetch_helpers.py probe <api_url>
    fetch_helpers.py tnris <manifest_url> <fips_min> <fips_max> <out_dir>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")


def get(url: str, timeout: int = 120) -> bytes:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read()


def stream_to(url: str, out: Path, timeout: int = 300) -> int:
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    size = 0
    with urllib.request.urlopen(req, timeout=timeout) as resp, out.open("wb") as f:
        while chunk := resp.read(1 << 20):
            f.write(chunk)
            size += len(chunk)
    return size


# Hub download/v1 jobs are regenerated on demand and the endpoint is not atomic
# about it: ND's Q4 run (37349704081, 2026-10-05) died on ONE HTTP 400 from the
# first poll, while the same URL answered 200 + Pending a week later. So every
# poll failure (HTTP error, network error, non-JSON body) is retryable until the
# deadline, and the response body is logged so the next failure can be read
# from the run log instead of guessed at.
HUB_DEADLINE_S = 5400     # MN's 2.7M-parcel FGDB export can take well over 30 min to generate
HUB_INTERVAL_S = 15
HUB_READY_STATUSES = ("Completed", "CompletedWithErrors", "")


class HubJobError(RuntimeError):
    """The hub job endpoint never produced what was asked of it before the deadline."""


def _snippet(body: bytes, n: int = 300) -> str:
    return body[:n].decode("utf-8", "replace")


def _fetch_job(api_url: str, fetch=get, log=print) -> tuple[dict | None, str]:
    """One poll of the job endpoint: (envelope, description) or (None, error description)."""
    try:
        job = json.loads(fetch(api_url))
    except urllib.error.HTTPError as e:
        body = _snippet(e.read() if e.fp is not None else b"")
        last = f"HTTP {e.code} {e.reason}: {body}"
        log(f"  hub job endpoint answered {last}")
        return None, last
    except (urllib.error.URLError, OSError, ValueError) as e:
        # URLError: DNS/connection failures; OSError: socket timeouts;
        # ValueError: JSON decode errors (an HTML error shell, a truncated body).
        last = f"{type(e).__name__}: {str(e)[:200]}"
        log(f"  hub job endpoint failed: {last}")
        return None, last
    if not isinstance(job, dict):
        last = f"envelope is not an object: {str(job)[:120]!r}"
        log(f"  hub job endpoint returned {last}")
        return None, last
    last = f"status={job.get('status', '')!r} message={str(job.get('message', ''))[:120]!r}"
    return job, last


def poll_hub_job(api_url: str, *, fetch=get, sleep=time.sleep, clock=time.monotonic,
                 deadline_s: float = HUB_DEADLINE_S, interval_s: float = HUB_INTERVAL_S,
                 log=print) -> dict:
    """Poll a hub download/v1 job until it reports a resultUrl.

    HTTP errors, network errors and non-JSON bodies are logged and retried;
    Pending / ExportingData envelopes are waited out. Raises HubJobError once
    the deadline passes. fetch / sleep / clock / log are injectable for tests.
    """
    deadline = clock() + deadline_s
    while True:
        job, last = _fetch_job(api_url, fetch, log)
        if job is not None and job.get("resultUrl") and job.get("status", "") in HUB_READY_STATUSES:
            return job
        if clock() > deadline:
            raise HubJobError(f"hub download never completed within {deadline_s:g}s for {api_url}; last: {last}")
        log(f"  hub job {last} — waiting {interval_s:g}s")
        sleep(interval_s)


def hub(api_url: str, out_file: str, *, poll=poll_hub_job, stream=stream_to) -> None:
    """Poll a hub download/v1 job until Completed, then stream resultUrl."""
    try:
        job = poll(api_url)
    except HubJobError as e:
        sys.exit(str(e))
    size = stream(job["resultUrl"], Path(out_file))
    print(f"  downloaded {size} bytes -> {out_file}")
    if size < 1024:
        sys.exit(f"hub download suspiciously small ({size} bytes) — refusing")


def probe(api_url: str, *, fetch=get, sleep=time.sleep, clock=time.monotonic,
          deadline_s: float = 120, interval_s: float = 10, log=print) -> dict:
    """One bounded look at a hub job endpoint: succeeds on ANY job envelope.

    A Pending / ExportingData answer counts (the export is being generated);
    a JSON body that is not a job envelope, or nothing but errors until the
    deadline, raises HubJobError. This is the live source check for the hub
    units; tests never call it against the network.
    """
    deadline = clock() + deadline_s
    while True:
        job, last = _fetch_job(api_url, fetch, log)
        if job is not None and ("status" in job or "resultUrl" in job):
            log(f"  hub job envelope: status={job.get('status', '')!r} "
                f"resultUrl={'yes' if job.get('resultUrl') else 'no'}")
            return job
        if clock() > deadline:
            raise HubJobError(f"no job envelope from {api_url} within {deadline_s:g}s; last: {last}")
        sleep(interval_s)


def curl_to(url: str, dest: Path) -> None:
    """Download with curl + browser-ish headers. data.geographic.texas.gov's
    WAF 403s cloud-runner requests: urllib AND bare curl both failed from CI
    (runs 1-2, 2026-08-10) while working from residential IPs. The Referer +
    Accept headers are the last same-network attempt; if TX still 403s, the
    path is a Cloudflare Worker proxy or a mirrored copy in R2 — not more
    header games."""
    subprocess.run(["curl", "-fSL", "--retry", "3", "--retry-delay", "5",
                    "-A", UA,
                    "-H", "Referer: https://data.geographic.texas.gov/",
                    "-H", "Accept: */*",
                    "-H", "Accept-Language: en-US,en;q=0.9",
                    "-o", str(dest), url], check=True)


def tnris(manifest_url: str, fips_min: str, fips_max: str, out_dir: str) -> None:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    urls: list[str] = []
    page_url = manifest_url
    while page_url:
        data = json.loads(get(page_url))
        for res in data.get("results", []):
            href = res.get("resource") or ""
            m = re.search(r"_(\d{5})_lp\.zip$", href)
            if m and fips_min <= m.group(1) <= fips_max:
                urls.append(href)
        page_url = data.get("next")
    if not urls:
        sys.exit(f"tnris manifest yielded no zips in FIPS [{fips_min}, {fips_max}]")
    print(f"  {len(urls)} county zips in FIPS [{fips_min}, {fips_max}]")
    for i, url in enumerate(sorted(urls), 1):
        dest = out / url.rsplit("/", 1)[-1]
        curl_to(url, dest)
        if dest.read_bytes()[:2] != b"PK":
            sys.exit(f"FETCH FAILED: {dest} is not a zip")
        print(f"  [{i}/{len(urls)}] {dest.name} ({dest.stat().st_size} bytes)")


def replica(layer_url: str, where: str, out_file: str) -> None:
    """ArcGIS createReplica bulk extract — async job, poll, download the
    filegdb zip. RETAINED FOR SMALL EXTRACTS ONLY: the 199-row probe passed
    (~10s) but multi-million-row extracts STALL server-side (FL run
    31449720301: frozen at ExportingData/107k records, lastUpdatedTime dead
    30 min). No unit uses this mode today; FL moved to FDOR bulk zips."""
    import urllib.parse
    root, layer_id = layer_url.rsplit("/", 1)
    body = urllib.parse.urlencode({
        "f": "json",
        "replicaName": "rr_extract",
        "layers": layer_id,
        "layerQueries": json.dumps({layer_id: {
            "queryOption": "useFilter", "useGeometry": False,
            "where": where or "1=1"}}),
        "returnAttachments": "false",
        "async": "true",
        "syncModel": "none",
        "dataFormat": "filegdb",
        "targetType": "client",
    }).encode()
    req = urllib.request.Request(f"{root}/createReplica", data=body,
                                 headers={"User-Agent": UA})
    job = json.loads(urllib.request.urlopen(req, timeout=120).read())
    status_url = job.get("statusUrl")
    if not status_url:
        sys.exit(f"createReplica gave no statusUrl: {job}")
    deadline = time.monotonic() + 5400  # a full-shard extract can take a while
    while True:
        st = json.loads(get(f"{status_url}?f=json"))
        status, result_url = st.get("status"), st.get("resultUrl")
        if status == "Completed" and result_url:
            print(f"  extract complete: {st.get('recordCount')} records")
            break
        if status in ("Failed", "CompletedWithErrors") or time.monotonic() > deadline:
            sys.exit(f"createReplica job ended badly: {st}")
        print(f"  extract status={status!r} — waiting 30s")
        time.sleep(30)
    size = stream_to(result_url, Path(out_file), timeout=1800)
    print(f"  downloaded {size} bytes -> {out_file}")


def mirror(release_api_url: str, fips_min: str, fips_max: str, out_dir: str) -> None:
    """TX county zips from OUR GitHub release mirror: data.geographic.texas.gov
    IP-blocks cloud runners (urllib AND curl 403 from CI, runs 1-3), so the
    public-domain zips are mirrored to a release on this repo from a
    residential IP (scripts/mirror_tx.sh) and CI pulls them from github.com."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    rel = json.loads(get(release_api_url))
    assets = []
    for a in rel.get("assets", []):
        m = re.search(r"_(\d{5})_lp\.zip$", a.get("name", ""))
        if m and fips_min <= m.group(1) <= fips_max:
            assets.append((a["name"], a["browser_download_url"]))
    if not assets:
        sys.exit(f"release mirror has no zips in FIPS [{fips_min}, {fips_max}]")
    print(f"  {len(assets)} mirrored county zips in FIPS [{fips_min}, {fips_max}]")
    for i, (name, url) in enumerate(sorted(assets), 1):
        dest = out / name
        curl_to(url, dest)
        if dest.read_bytes()[:2] != b"PK":
            sys.exit(f"FETCH FAILED: {dest} is not a zip")
        print(f"  [{i}/{len(assets)}] {name} ({dest.stat().st_size} bytes)")


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    mode = sys.argv[1]
    if mode == "hub":
        hub(sys.argv[2], sys.argv[3])
    elif mode == "probe":
        try:
            probe(sys.argv[2])
        except HubJobError as e:
            sys.exit(str(e))
    elif mode == "tnris":
        tnris(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    elif mode == "replica":
        replica(sys.argv[2], sys.argv[3], sys.argv[4])
    elif mode == "mirror":
        mirror(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        sys.exit(f"unknown helper mode {mode!r}")


if __name__ == "__main__":
    main()
