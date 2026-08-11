#!/usr/bin/env bash
# TX StratMap land-parcel mirror refresh — RUN FROM A RESIDENTIAL IP.
#
# data.geographic.texas.gov IP-blocks cloud runners (CI curl/urllib both 403;
# residential IPs work — verified 2026-08-10), so CI pulls the public-domain
# county zips from a GitHub release on this repo instead. Re-run this script
# when TxGIO ships a new vintage (stratmap26, ...), then update the release
# tag in layers/parcels/sources.json (TX_1..TX_3).
#
# Usage: mirror_tx.sh <collection_id> <release_tag> [work_dir]
#   e.g. mirror_tx.sh 0fa04328-872e-481c-b453-126a74777593 tx-stratmap25
# Find the new collection_id at:
#   https://api.tnris.org/api/v1/collections?search=land%20parcels
set -euo pipefail

COLLECTION="${1:?collection_id required}"
TAG="${2:?release tag required (e.g. tx-stratmap26)}"
WORK="${3:-tx_mirror_work}"
REPO="riggs19991/ruggedroute-dataops"
UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"

mkdir -p "$WORK"
cd "$WORK"

echo "== manifest"
python3 - "$COLLECTION" <<'PY' > urls.txt
import json, sys, urllib.request
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/126.0"
urls, page = [], f"https://api.tnris.org/api/v1/resources?collection_id={sys.argv[1]}&limit=254"
while page:
    req = urllib.request.Request(page, headers={"User-Agent": UA})
    d = json.load(urllib.request.urlopen(req, timeout=60))
    urls += [r["resource"] for r in d.get("results", []) if (r.get("resource") or "").endswith("_lp.zip")]
    page = d.get("next")
print("\n".join(sorted(set(urls))))
PY
echo "$(wc -l < urls.txt) county zips"

echo "== download (6 parallel, resumable — rerun on partial failure)"
xargs -P 6 -I{} sh -c 'f=$(basename "{}"); [ -s "$f" ] || curl -sfL --retry 3 --retry-delay 5 -A "'"$UA"'" -o "$f" "{}" || echo "FAIL {}" >&2' < urls.txt
for f in *.zip; do head -c 2 "$f" | grep -q PK || { echo "BAD ZIP: $f" >&2; exit 1; }; done

echo "== release upload"
gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1 || \
  gh release create "$TAG" --repo "$REPO" --title "TX StratMap land-parcel mirror ($TAG)" \
    --notes "Public-domain TxGIO StratMap per-county land-parcel zips (collection $COLLECTION). CI mirror — see layers/parcels/sources.json TX_* notes."
ls *.zip | sort | split -l 32 - batch_
for b in batch_*; do
  gh release upload "$TAG" --repo "$REPO" $(cat "$b") --clobber
  echo "uploaded $b"
done
rm -f batch_*

echo "== verify"
COUNT=$(gh release view "$TAG" --repo "$REPO" --json assets --jq '.assets | length')
echo "$COUNT assets on $TAG (expect 254)"
[ "$COUNT" -ge 254 ] || { echo "asset count short" >&2; exit 1; }
echo "done — now update the release tag in layers/parcels/sources.json if it changed"
