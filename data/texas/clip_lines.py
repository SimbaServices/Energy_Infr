"""Keep pipeline and transmission lines that cross Texas, one shard of the table.

A line is kept when a point along it, including points between vertices, falls
inside a Texas county. Outputs stay in --out.
"""

from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

DB = Path("/home/propeval/Energy_Infr/db/us_pipelines.sqlite")
COUNTIES = Path("/var/www/energy-sandbox/data/texas/counties.geojson")
STEP = 0.012


def pip(lon: float, lat: float, rings) -> bool:
    inside = False
    for ring in rings:
        j = len(ring) - 1
        for i, point in enumerate(ring):
            yi, xi = point[1], point[0]
            yj, xj = ring[j][1], ring[j][0]
            if ((yi > lat) != (yj > lat)) and (lon < (xj - xi) * (lat - yi) / ((yj - yi) or 1e-15) + xi):
                inside = not inside
            j = i
    return inside


def rings_of(geometry):
    if not geometry:
        return
    kind = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if kind == "Polygon":
        yield from coords
    elif kind == "MultiPolygon":
        for polygon in coords:
            yield from polygon


def load_counties():
    payload = json.loads(COUNTIES.read_text())
    prepared = []
    for feature in payload["features"]:
        geometry = feature["geometry"]
        rings = [ring for ring in rings_of(geometry) if ring]
        xs = [point[0] for ring in rings for point in ring]
        ys = [point[1] for ring in rings for point in ring]
        if not xs or not ys:
            continue
        prepared.append((min(xs), min(ys), max(xs), max(ys), rings))
    return prepared


def segments(geometry):
    kind = geometry["type"]
    coords = geometry["coordinates"]
    lines = coords if kind == "MultiLineString" else [coords]
    for line in lines:
        for start, end in zip(line, line[1:]):
            yield start, end


def hits(geometry, counties) -> bool:
    for start, end in segments(geometry):
        lon1, lat1 = start[0], start[1]
        lon2, lat2 = end[0], end[1]
        west, east = sorted((lon1, lon2))
        south, north = sorted((lat1, lat2))
        span = max(abs(lon2 - lon1), abs(lat2 - lat1))
        steps = max(1, int(span / STEP))
        for county in counties:
            min_lon, min_lat, max_lon, max_lat, rings = county
            if east < min_lon or west > max_lon or north < min_lat or south > max_lat:
                continue
            for step in range(steps + 1):
                t = step / steps
                lon = lon1 + (lon2 - lon1) * t
                lat = lat1 + (lat2 - lat1) * t
                if lon < min_lon or lon > max_lon or lat < min_lat or lat > max_lat:
                    continue
                if pip(lon, lat, rings):
                    return True
    return False


def round_geom(geometry):
    def rnd(pair):
        return [round(pair[0], 5), round(pair[1], 5)]

    kind = geometry["type"]
    if kind == "LineString":
        return {"type": kind, "coordinates": [rnd(pair) for pair in geometry["coordinates"]]}
    if kind == "MultiLineString":
        return {"type": kind, "coordinates": [[rnd(pair) for pair in line] for line in geometry["coordinates"]]}
    return geometry


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--shards", type=int, default=8)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    counties = load_counties()
    pipes = []
    lines = []
    conn = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        for operator, pipe_type, text in conn.execute(
            "SELECT operator, pipe_type, geojson FROM pipelines WHERE (rowid % ?) = ?",
            (args.shards, args.shard),
        ):
            geometry = json.loads(text)
            if hits(geometry, counties):
                pipes.append({
                    "type": "Feature",
                    "geometry": round_geom(geometry),
                    "properties": {"operator": operator or "", "pipe_type": pipe_type or ""},
                })
        for owner, voltage, text in conn.execute(
            "SELECT owner, voltage_kv, geojson FROM transmission_lines WHERE (rowid % ?) = ?",
            (args.shards, args.shard),
        ):
            geometry = json.loads(text)
            if hits(geometry, counties):
                lines.append({
                    "type": "Feature",
                    "geometry": round_geom(geometry),
                    "properties": {"owner": owner or "", "voltage_kv": voltage},
                })
    finally:
        conn.close()
    args.out.mkdir(parents=True, exist_ok=True)
    for name, features in (("pipelines.geojson", pipes), ("transmission.geojson", lines)):
        (args.out / name).write_text(
            json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")),
            encoding="utf-8",
        )
    summary = {"pipelines": len(pipes), "transmission": len(lines), "shard": args.shard}
    (args.out / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
