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


def main() -> None:
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    mode = sys.argv[1]
    if mode == "hub":
        hub(sys.argv[2], sys.argv[3])
    elif mode == "tnris":
        tnris(sys.argv[2], sys.argv[3], sys.argv[4], sys.argv[5])
    else:
        sys.exit(f"unknown helper mode {mode!r}")


if __name__ == "__main__":
    main()
