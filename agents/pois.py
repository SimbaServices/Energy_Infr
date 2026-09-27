"""69 kV points of interconnection for one state.

Same sources as src/build_pois.py: the public substation republish and the
Esri transmission-line archive. Cached under data/raw/agents so a later run
can reuse a file from the same UTC day.
"""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import build_pois  # noqa: E402

RAW = ROOT / "data" / "raw" / "agents"
SUBSTATION_URL = build_pois.SUBSTATION_URL
LINE_URL = build_pois.LINE_URL


def _params(where: str, box: str, fields: str) -> dict:
    return {
        "where": where,
        "geometry": box,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": fields,
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    }


def build(out_dir: Path, postal: str, state_name: str, counties: list, box) -> int:
    day = datetime.now(timezone.utc).date().isoformat()
    cache = RAW / postal.lower()
    box_text = f"{box[0]},{box[1]},{box[2]},{box[3]}"
    county_pairs = [(feature["properties"]["name"], feature["geometry"]) for feature in counties]
    county_names = {name.upper() for name, _geometry in county_pairs}

    substations = build_pois.load_or_fetch(
        cache / f"substations-{day}.geojson",
        SUBSTATION_URL,
        _params(
            f"STATE = '{postal}' AND (MAX_VOLT >= 69 OR MAX_VOLT < 0)",
            box_text,
            "ID,NAME,CITY,STATE,COUNTY,TYPE,STATUS,LINES,MAX_VOLT,MIN_VOLT,MAX_INFER,MIN_INFER,SOURCEDATE",
        ),
    )
    lines = build_pois.load_or_fetch(
        cache / f"lines69-{day}.geojson",
        LINE_URL,
        {
            **_params(
                "VOLTAGE >= 69 AND STATUS = 'IN SERVICE'",
                box_text,
                "ID,OWNER,VOLTAGE,SUB_1,SUB_2,STATUS",
            ),
            "geometryPrecision": "5",
        },
    )
    buckets, cell = build_pois.index_lines(lines)
    features = []
    for feature in substations["features"]:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") != "Point":
            continue
        lon, lat = geometry["coordinates"][:2]
        props = feature.get("properties") or {}
        county = build_pois.county_of(lon, lat, county_pairs)
        if county is None and (props.get("COUNTY") or "").upper() in county_names:
            county = build_pois.place(props.get("COUNTY"))
        if county is None:
            continue
        max_kv = build_pois.volts(props.get("MAX_VOLT"))
        min_kv = build_pois.volts(props.get("MIN_VOLT"))
        raw_name = props.get("NAME") or ""
        hits = build_pois.lines_near(lon, lat, buckets, cell, raw_name)
        if max_kv is None:
            if not hits:
                continue
            max_kv = max(hit["voltage_kv"] for hit in hits)
        if max_kv < 69:
            continue
        if min_kv is not None and min_kv > max_kv:
            min_kv, max_kv = max_kv, min_kv
        owner_rows = build_pois.owners_of(hits)
        circuits = []
        seen = set()
        for hit in hits:
            if not hit["from_name"] and not hit["to_name"]:
                continue
            key = (hit["from_name"], hit["to_name"], hit["voltage_kv"], hit["owner"])
            if key in seen:
                continue
            seen.add(key)
            circuits.append({
                "owner": hit["owner"],
                "voltage_kv": hit["voltage_kv"],
                "miles": hit["miles"],
                "from_name": hit["from_name"],
                "to_name": hit["to_name"],
            })
            if len(circuits) == 3:
                break
        kind = build_pois.type_label(props.get("TYPE"))
        display = (
            ("Unnamed tap" if kind == "Tap" else "Unnamed substation")
            if build_pois.unnamed(raw_name)
            else build_pois.place(raw_name)
        )
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
            "properties": {
                "id": str(props.get("ID") or ""),
                "name": display,
                "type": kind,
                "status": build_pois.status_label(props.get("STATUS")),
                "city": build_pois.place(props.get("CITY")),
                "county": county,
                "state": state_name,
                "min_kv": min_kv,
                "max_kv": max_kv,
                "max_inferred": (props.get("MAX_INFER") or "").upper() == "Y"
                or build_pois.volts(props.get("MAX_VOLT")) is None,
                "min_inferred": (props.get("MIN_INFER") or "").upper() == "Y",
                "line_count": int(props.get("LINES") or 0),
                "owners": owner_rows,
                "circuits": circuits,
                "source_date": build_pois.source_day(props.get("SOURCEDATE")),
            },
        })
    features.sort(key=lambda feature: (-(feature["properties"]["max_kv"] or 0), feature["properties"]["name"]))
    (out_dir / "pois.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )
    return len(features)
