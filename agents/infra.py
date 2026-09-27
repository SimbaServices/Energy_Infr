"""Clip the national layers the Permian map already uses onto one state."""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "db" / "us_pipelines.sqlite"
COUNTIES = ROOT / "data" / "raw" / "geo" / "counties.geojson"


def iter_coords(geometry):
    kind = geometry.get("type")
    coords = geometry.get("coordinates")
    if kind == "LineString":
        yield from coords
    elif kind == "MultiLineString":
        for line in coords:
            yield from line
    elif kind == "Point":
        yield coords
    elif kind == "Polygon":
        for ring in coords:
            yield from ring
    elif kind == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                yield from ring


def hits_box(geometry, box):
    min_lon, min_lat, max_lon, max_lat = box
    return any(
        min_lon <= lon <= max_lon and min_lat <= lat <= max_lat
        for lon, lat in iter_coords(geometry)
    )


def round_geom(geometry):
    def rnd(pair):
        return [round(pair[0], 5), round(pair[1], 5)]

    kind = geometry["type"]
    if kind == "LineString":
        return {"type": kind, "coordinates": [rnd(pair) for pair in geometry["coordinates"]]}
    if kind == "MultiLineString":
        return {
            "type": kind,
            "coordinates": [[rnd(pair) for pair in line] for line in geometry["coordinates"]],
        }
    if kind == "Point":
        return {"type": kind, "coordinates": rnd(geometry["coordinates"])}
    return geometry


def write_collection(path: Path, features: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )


def state_counties(fips: str):
    payload = json.loads(COUNTIES.read_text(encoding="utf-8"))
    features = []
    for feature in payload["features"]:
        props = feature["properties"]
        if props.get("STATE") != fips:
            continue
        features.append({
            "type": "Feature",
            "geometry": feature["geometry"],
            "properties": {"name": props["NAME"], "fips": props["COUNTY"]},
        })
    if not features:
        raise RuntimeError(f"no counties for state fips {fips}")
    lons = []
    lats = []
    for feature in features:
        for lon, lat in iter_coords(feature["geometry"]):
            lons.append(lon)
            lats.append(lat)
    box = (min(lons), min(lats), max(lons), max(lats))
    return features, box


def clip_network(out_dir: Path, box) -> dict:
    counties_note = {}
    pipes = []
    lines = []
    tieins = []
    conn = sqlite3.connect(DB)
    try:
        for operator, pipe_type, geometry_text in conn.execute(
            "SELECT operator, pipe_type, geojson FROM pipelines"
        ):
            geometry = json.loads(geometry_text)
            if hits_box(geometry, box):
                pipes.append({
                    "type": "Feature",
                    "geometry": round_geom(geometry),
                    "properties": {"operator": operator or "", "pipe_type": pipe_type or ""},
                })
        for owner, voltage, geometry_text in conn.execute(
            "SELECT owner, voltage_kv, geojson FROM transmission_lines"
        ):
            geometry = json.loads(geometry_text)
            if hits_box(geometry, box):
                lines.append({
                    "type": "Feature",
                    "geometry": round_geom(geometry),
                    "properties": {"owner": owner or "", "voltage_kv": voltage},
                })
        for lat, lon, voltage, owner, operator, distance in conn.execute(
            """
            SELECT lat, lon, voltage_kv, owner, pipeline_operator, distance_miles
            FROM interconnects
            WHERE lon BETWEEN ? AND ? AND lat BETWEEN ? AND ?
            """,
            (box[0], box[2], box[1], box[3]),
        ):
            tieins.append({
                "type": "Feature",
                "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
                "properties": {
                    "voltage_kv": voltage,
                    "owner": owner or "",
                    "pipeline_operator": operator or "",
                    "distance_miles": round(distance, 2),
                },
            })
    finally:
        conn.close()
    write_collection(out_dir / "pipelines.geojson", pipes)
    write_collection(out_dir / "transmission.geojson", lines)
    write_collection(out_dir / "tieins.geojson", tieins)
    counties_note["pipelines"] = len(pipes)
    counties_note["transmission"] = len(lines)
    counties_note["tieins"] = len(tieins)
    return counties_note
