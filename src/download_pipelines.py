"""Download the public EIA natural gas pipeline layer from the DOT feature service.

Source: U.S. Energy Information Administration pipeline centerlines, hosted for
public query by the U.S. Department of Transportation. About 33,000 segments
covering interstate, intrastate, and gathering lines. Geometry is requested in
WGS84. No login is required.
"""

from __future__ import annotations

import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "raw" / "pipelines" / "eia_pipelines.geojson"

SERVICE = (
    "https://geo.dot.gov/server/rest/services/hosted/"
    "Natural_Gas_Pipelines_US_EIA/FeatureServer/0/query"
)
PAGE = 2000
USER_AGENT = "US-Pipelines-research/1.0 (public EIA pipeline map)"


def fetch(params: dict) -> dict:
    url = SERVICE + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=180) as response:
        return json.loads(response.read().decode("utf-8"))


def esri_to_geometry(geometry: dict | None) -> dict | None:
    if not geometry or "paths" not in geometry:
        return None
    paths = []
    for path in geometry["paths"]:
        cleaned = []
        for point in path:
            lon = round(float(point[0]), 5)
            lat = round(float(point[1]), 5)
            if cleaned and cleaned[-1] == [lon, lat]:
                continue
            cleaned.append([lon, lat])
        if len(cleaned) >= 2:
            paths.append(cleaned)
    if not paths:
        return None
    if len(paths) == 1:
        return {"type": "LineString", "coordinates": paths[0]}
    return {"type": "MultiLineString", "coordinates": paths}


def main() -> None:
    count = fetch({"where": "1=1", "returnCountOnly": "true", "f": "json"})["count"]
    print(f"segments reported by service: {count}", flush=True)
    features = []
    offset = 0
    while offset < count:
        started = time.time()
        page = fetch(
            {
                "where": "1=1",
                "outFields": "typepipe,operator,status",
                "returnGeometry": "true",
                "outSR": "4326",
                "orderByFields": "objectid",
                "resultOffset": str(offset),
                "resultRecordCount": str(PAGE),
                "f": "json",
            }
        )
        batch = page.get("features") or []
        if not batch:
            break
        for feature in batch:
            attrs = feature.get("attributes") or {}
            geometry = esri_to_geometry(feature.get("geometry"))
            if geometry is None:
                continue
            features.append(
                {
                    "type": "Feature",
                    "properties": {
                        "pipe_type": attrs.get("typepipe"),
                        "operator": attrs.get("operator"),
                        "status": attrs.get("status"),
                    },
                    "geometry": geometry,
                }
            )
        offset += len(batch)
        print(
            f"  {offset}/{count} in {time.time() - started:.1f}s",
            flush=True,
        )
        if len(batch) < PAGE and not page.get("exceededTransferLimit"):
            break

    collection = {
        "type": "FeatureCollection",
        "name": "EIA natural gas pipelines",
        "source": SERVICE,
        "features": features,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(collection, separators=(",", ":")), encoding="utf-8")
    print(f"wrote {len(features)} features to {OUT}", flush=True)


if __name__ == "__main__":
    main()
