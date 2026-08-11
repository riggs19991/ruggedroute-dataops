#!/usr/bin/env python3
"""Stage 3 parcels fetch helpers for the two non-trivial source shapes.

hub    — ArcGIS Hub download/v1 API with redirect=false returns a JSON job
         envelope, NOT the file (VT, ME). Poll until status=Completed, then
         stream resultUrl (an ephemeral signed blob, ~1h expiry — never cache
         it; re-request the API every run).

tnris  — TX StratMap land parcels ship as 254 per-county zips listed by the
         api.tnris.org resources manifest (paginated JSON, no auth). County
         FIPS is embedded in every zip filename, so shard filtering needs no
         attribute reads. Each shard downloads its FIPS range.

Usage:
    fetch_helpers.py hub   <api_url> <out_file>
    fetch_helpers.py tnris <manifest_url> <fips_min> <fips_max> <out_dir>
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import time
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


def hub(api_url: str, out_file: str) -> None:
    """Poll a hub download/v1 job until Completed, then stream resultUrl."""
    deadline = time.monotonic() + 1800
    while True:
        job = json.loads(get(api_url))
        status = job.get("status", "")
        result_url = job.get("resultUrl")
        if result_url and status in ("Completed", "CompletedWithErrors", ""):
            break
        if time.monotonic() > deadline:
            sys.exit(f"hub download never completed: last status={status!r} for {api_url}")
        print(f"  hub job status={status!r} — waiting 15s")
        time.sleep(15)
    size = stream_to(result_url, Path(out_file))
    print(f"  downloaded {size} bytes -> {out_file}")
    if size < 1024:
        sys.exit(f"hub download suspiciously small ({size} bytes) — refusing")


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
