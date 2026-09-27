"""Pull current EIA API series. The key is read from outside this project.

Looks for EIA_API_KEY, then C:\\Users\\Sam Parker\\Take_Action\\eia_api.txt.
Responses are saved under data/raw/api without the key.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "api"
KEY_FILE = Path(r"C:\Users\Sam Parker\Take_Action\eia_api.txt")
USER_AGENT = "US-Pipelines-research/1.0"

# STEO marketed-production series that replaced the Drilling Productivity Report
# regions after June 2024. Niobrara is the shale-formation series; Anadarko has
# no matching STEO marketed total.
STEO_SERIES = [
    "NGPRPUS",
    "NGMPPM",
    "NGMPHA",
    "NGMPAP",
    "NGMPBK",
    "NGMPEF",
    "SNGPRNI",
]


def api_key() -> str:
    key = os.environ.get("EIA_API_KEY", "").strip()
    if not key and KEY_FILE.is_file():
        key = KEY_FILE.read_text(encoding="utf-8").strip()
    if not key:
        raise SystemExit("No EIA API key in EIA_API_KEY or the key file outside this project.")
    return key


def get(path: str, params: list[tuple[str, str]]) -> dict:
    query = urllib.parse.urlencode(params + [("api_key", api_key())])
    request = urllib.request.Request(
        "https://api.eia.gov/v2/" + path + "?" + query,
        headers={"User-Agent": USER_AGENT},
    )
    try:
        with urllib.request.urlopen(request, timeout=180) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        detail = error.read().decode("utf-8", "replace")[:300]
        raise SystemExit(f"EIA API {error.code} for {path}: {detail}") from None


def save(name: str, payload) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    print(f"wrote {path.name} ({path.stat().st_size} bytes)")


def fetch_steo() -> None:
    params = [
        ("frequency", "monthly"),
        ("data[0]", "value"),
        ("start", "2025-01"),
        ("end", "2026-09"),
        ("sort[0][column]", "period"),
        ("sort[0][direction]", "desc"),
        ("length", "5000"),
    ]
    params.extend(("facets[seriesId][]", series) for series in STEO_SERIES)
    rows = get("steo/data/", params)["response"]["data"]
    save("steo_regions.json", rows)
    latest = {}
    for row in rows:
        latest.setdefault(row.get("seriesId"), row)
    for series, row in latest.items():
        print(f"  {series} {row.get('period')} {row.get('value')} {row.get('unit')}")


def fetch_citygate() -> None:
    params = [
        ("frequency", "annual"),
        ("data[0]", "value"),
        ("facets[process][]", "PG1"),
        ("start", "2024"),
        ("end", "2025"),
        ("sort[0][column]", "period"),
        ("sort[0][direction]", "desc"),
        ("length", "5000"),
    ]
    rows = get("natural-gas/pri/sum/data/", params)["response"]["data"]
    save("citygate_annual.json", rows)
    print(f"  citygate rows {len(rows)}")


def fetch_hubs() -> None:
    url = (
        "https://services2.arcgis.com/ZOdjAzAQ2B0f85zi/arcgis/rest/services/"
        "NaturalGas_TradingHubs_US_EIA/FeatureServer/0/query?"
        + urllib.parse.urlencode(
            {
                "where": "1=1",
                "outFields": "*",
                "returnGeometry": "true",
                "outSR": "4326",
                "f": "geojson",
            }
        )
    )
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=120) as response:
        payload = json.loads(response.read().decode("utf-8"))
    path = ROOT / "data" / "raw" / "geo" / "trading_hubs.geojson"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload), encoding="utf-8")
    print(f"wrote trading hubs ({len(payload.get('features') or [])} points)")
    if payload.get("features"):
        print("  fields", sorted((payload["features"][0].get("properties") or {}).keys()))


def fetch_flared() -> None:
    params = [
        ("frequency", "annual"),
        ("data[0]", "value"),
        ("start", "2023"),
        ("end", "2025"),
        ("sort[0][column]", "period"),
        ("sort[0][direction]", "desc"),
        ("length", "5000"),
    ]
    params.extend(("facets[process][]", process) for process in ("VGV", "FGW"))
    rows = get("natural-gas/prod/sum/data/", params)["response"]["data"]
    save("vented_flared_annual.json", rows)
    latest = {}
    for row in rows:
        if row.get("process") != "VGV":
            continue
        area = row.get("area-name") or row.get("duoarea")
        latest.setdefault(area, row)
    print(f"  vented/flared areas {len(latest)}")
    for area, row in list(latest.items())[:8]:
        print(f"  {area} {row.get('period')} {row.get('value')}")


def main() -> None:
    fetch_steo()
    fetch_citygate()
    fetch_hubs()
    fetch_flared()


if __name__ == "__main__":
    main()
