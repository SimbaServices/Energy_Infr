"""Join the Texas basin maps into one statewide view.

County outlines are every Texas county. Leases, pipelines, transmission lines,
and points of interconnection are the features already published for the Texas
region options. A feature that fell in two basins is kept once.

The basin folders stay on disk. This script only writes web/data/texas.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2] if len(Path(__file__).resolve().parents) > 2 else Path("/home/propeval/Energy_Infr")
WEB = ROOT / "web" / "data"
COUNTIES = ROOT / "data" / "raw" / "geo" / "counties.geojson"

# Permian files sit in web/data itself. The other names are sibling folders.
BASINS = (
    "",
    "eagle-ford",
    "barnett",
    "haynesville-tx",
    "east-texas",
    "gulf-coast",
    "panhandle",
)


def load_collection(path: Path) -> list:
    if not path.is_file():
        return []
    payload = json.loads(path.read_text(encoding="utf-8"))
    return payload.get("features") or []


def write_collection(path: Path, features: list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")),
        encoding="utf-8",
    )


def geometry_token(geometry) -> str:
    return json.dumps(geometry, sort_keys=True, separators=(",", ":"))


def lease_key(feature) -> tuple:
    props = feature.get("properties") or {}
    lease_no = props.get("lease_no")
    if lease_no not in (None, ""):
        return ("lease", str(props.get("district") or ""), str(lease_no), str(props.get("kind") or ""))
    return ("lease-geom", geometry_token(feature.get("geometry")))


def poi_key(feature) -> tuple:
    props = feature.get("properties") or {}
    if props.get("id") not in (None, ""):
        return ("poi", str(props["id"]))
    coords = (feature.get("geometry") or {}).get("coordinates") or [None, None]
    return ("poi-xy", round(float(coords[0]), 5), round(float(coords[1]), 5))


def line_key(feature) -> tuple:
    props = feature.get("properties") or {}
    return (
        str(props.get("operator") or props.get("owner") or ""),
        str(props.get("pipe_type") or props.get("voltage_kv") or ""),
        geometry_token(feature.get("geometry")),
    )


def prefer_lease(current, candidate) -> dict:
    current_value = float((current.get("properties") or {}).get("flared_mmcfd") or 0)
    candidate_value = float((candidate.get("properties") or {}).get("flared_mmcfd") or 0)
    return candidate if candidate_value > current_value else current


def prefer_poi(current, candidate) -> dict:
    current_kv = float((current.get("properties") or {}).get("max_kv") or 0)
    candidate_kv = float((candidate.get("properties") or {}).get("max_kv") or 0)
    return candidate if candidate_kv > current_kv else current


def gather(web: Path, filename: str, key_fn, prefer) -> list:
    chosen = {}
    order = []
    for basin in BASINS:
        folder = web if basin == "" else web / basin
        for feature in load_collection(folder / filename):
            key = key_fn(feature)
            if key not in chosen:
                order.append(key)
                chosen[key] = feature
            else:
                chosen[key] = prefer(chosen[key], feature)
    return [chosen[key] for key in order]


def texas_counties(path: Path) -> list:
    payload = json.loads(path.read_text(encoding="utf-8"))
    features = []
    for feature in payload["features"]:
        props = feature["properties"]
        if str(props.get("STATE")) != "48":
            continue
        features.append({
            "type": "Feature",
            "geometry": feature["geometry"],
            "properties": {"name": props["NAME"], "fips": props["COUNTY"]},
        })
    features.sort(key=lambda feature: feature["properties"]["name"])
    if not features:
        raise RuntimeError(f"no Texas counties in {path}")
    return features


def point_lat_lon(feature) -> tuple[float | None, float | None]:
    geometry = feature.get("geometry") or {}
    kind = geometry.get("type")
    coords = geometry.get("coordinates")
    if kind == "Point" and coords:
        return float(coords[1]), float(coords[0])
    return None, None


def build(web: Path, counties_path: Path, out: Path) -> dict:
    counties = texas_counties(counties_path)
    leases = gather(web, "leases.geojson", lease_key, prefer_lease)
    pois = gather(web, "pois.geojson", poi_key, prefer_poi)
    pipelines = gather(web, "pipelines.geojson", line_key, lambda current, _candidate: current)
    transmission = gather(web, "transmission.geojson", line_key, lambda current, _candidate: current)

    located = []
    for feature in leases:
        props = feature.get("properties") or {}
        if props.get("flared_mmcfd") is None:
            continue
        lat, lon = point_lat_lon(feature)
        located.append((feature, props, lat, lon))
    flared = round(sum(float(props["flared_mmcfd"]) for _feature, props, _lat, _lon in located), 2)
    top = sorted(located, key=lambda item: float(item[1]["flared_mmcfd"]), reverse=True)[:25]
    summary = {
        "kicker": "Texas",
        "title": "Vented and flared gas by lease",
        "headline": (
            f"{flared} MMcfd filed on {len(located):,} leases with a surface location "
            f"({sum(props.get('kind') == 'oil' for _feature, props, _lat, _lon in located):,} oil leases and "
            f"{sum(props.get('kind') == 'gas' for _feature, props, _lat, _lon in located):,} gas wells). "
            "Circle size follows that filing."
        ),
        "method": (
            "This view is every Texas county. Leases, pipelines, transmission lines, and points of "
            "interconnection are the features already mapped for the Texas basin views, joined into one map. "
            "A feature that fell in two basins is kept once. Volumes are the vented-or-flared column on the "
            "Railroad Commission Form PR tapes used for those views. Pipelines are the EIA centerline "
            "compilation from January 2020. Transmission lines are the public 230 kV-and-above subset. "
            "Points of interconnection are substations and taps of 69 kV and above."
        ),
        "leases": len(located),
        "lease_unit": "lease",
        "flared_mmcfd": flared,
        "flared_mcf": round(sum(float(props.get("flared_mcf") or 0) for _feature, props, _lat, _lon in located)),
        "oil_leases": sum(props.get("kind") == "oil" for _feature, props, _lat, _lon in located),
        "gas_wells": sum(props.get("kind") == "gas" for _feature, props, _lat, _lon in located),
        "counties": [feature["properties"]["name"] for feature in counties],
        "pipelines": len(pipelines),
        "transmission": len(transmission),
        "tieins": 0,
        "pois": len(pois),
        "top": [
            {
                "lease_name": props.get("lease_name"),
                "field_name": props.get("field_name"),
                "operator_name": props.get("operator_name"),
                "county": props.get("county"),
                "kind": props.get("kind"),
                "district": props.get("district"),
                "lease_no": props.get("lease_no"),
                "period": props.get("period"),
                "flared_mmcfd": round(float(props.get("flared_mmcfd") or 0), 2),
                "flared_mcf": props.get("flared_mcf"),
                "produced_mcf": props.get("produced_mcf"),
                "lat": lat,
                "lon": lon,
            }
            for _feature, props, lat, lon in top
        ],
    }
    write_collection(out / "counties.geojson", counties)
    write_collection(out / "leases.geojson", leases)
    write_collection(out / "pois.geojson", pois)
    write_collection(out / "pipelines.geojson", pipelines)
    write_collection(out / "transmission.geojson", transmission)
    write_collection(out / "tieins.geojson", [])
    (out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"texas: counties {len(counties)} leases {len(leases)} "
        f"pipelines {len(pipelines)} lines {len(transmission)} pois {len(pois)}"
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the statewide Texas map folder")
    parser.add_argument("--web-data", type=Path, default=WEB)
    parser.add_argument("--counties", type=Path, default=COUNTIES)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    out = args.out or (args.web_data / "texas")
    build(args.web_data, args.counties, out)


if __name__ == "__main__":
    main()
