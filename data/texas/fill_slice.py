"""Build one slice of the Texas counties that were left out of the basin maps.

Writes leases, pipelines, transmission, counties, and points of interconnection
for the given county FIPS codes. An empty flare layer is allowed: some counties
have no matched vented or flared volume. Outputs stay in --out.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
BASIN = ROOT / "data" / "haynesville-tx" / "build.py"


def load_basin():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("haynesville_build", BASIN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def stored_file(path: Path) -> bool:
    return path.is_file() and path.stat().st_size > 1000


def main() -> None:
    parser = argparse.ArgumentParser(description="Fill one slice of uncovered Texas counties")
    parser.add_argument("--counties", required=True, help="Comma-separated 3-digit county FIPS")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    codes = [part.strip() for part in args.counties.split(",") if part.strip()]
    if not codes or any(len(code) != 3 or not code.isdigit() for code in codes):
        raise SystemExit("counties must be 3-digit FIPS codes")

    hb = load_basin()
    hb.COUNTIES = codes
    hb.OUT = args.out
    hb.CACHE = args.out / "cache"
    hb.CACHE.mkdir(parents=True, exist_ok=True)
    hb.DISTRICTS = tuple(f"{i:02d}" for i in range(100))

    wells_ready = all(stored_file(hb.RRC / "wells" / f"well{code}.zip") for code in codes)
    api_ready = all(stored_file(hb.RRC / "api" / f"cc{code}") for code in codes)
    if wells_ready:
        print("using stored wells", flush=True)
    else:
        print("downloading wells", flush=True)
        try:
            hb.download_wells()
        except SystemExit as exc:
            print(f"wells incomplete: {exc}", flush=True)
    if api_ready:
        print("using stored api", flush=True)
    else:
        print("downloading api", flush=True)
        try:
            hb.download_api()
        except SystemExit as exc:
            print(f"api incomplete: {exc}", flush=True)

    dispositions = hb.load_dispositions()
    by_number = hb.index_dispositions(dispositions)
    print("disposition leases", len(dispositions), flush=True)
    chosen = {}
    county_of_api = {}
    points_by_county = {}
    operator_votes = defaultdict(Counter)
    for county in codes:
        api_path = hb.RRC / "api" / f"cc{county}"
        well_path = hb.RRC / "wells" / f"well{county}.zip"
        if not api_path.exists() or not well_path.exists():
            print(f"  {county} skipped api={api_path.exists()} wells={well_path.exists()}", flush=True)
            continue
        points = hb.dbf_points(well_path)
        points_by_county[county] = points
        matched = 0
        for line in hb.api_records(api_path, county):
            key = hb.match_lease(line, by_number)
            if key is None:
                continue
            api = line[7:15]
            if api not in points:
                continue
            date = hb.completion_date(line)
            name = hb.operator_name(line)
            prev = chosen.get(api)
            if prev is None or date >= prev[0]:
                chosen[api] = (date, key, name)
                county_of_api[api] = county
            matched += 1
        print(f"  {county} surface wells {len(points):6} name-matched {matched:6}", flush=True)

    groups = defaultdict(list)
    for api, (_date, key, op_name) in chosen.items():
        county = county_of_api[api]
        lat, lon = points_by_county[county][api]
        groups[key].append((lat, lon, county, op_name))
        if op_name:
            operator_votes[key][op_name] += 1

    county_features, prepared, county_names = hb.load_county_geoms()
    leases = []
    for key, wells in groups.items():
        row = dict(dispositions[key])
        if row["flared_mcf"] <= 0 and row["produced_mcf"] <= 0:
            continue
        row["flared_mmcfd"] = row["flared_mcf"] / 1000 / hb.days_in(row["period"])
        row["lat"] = sum(item[0] for item in wells) / len(wells)
        row["lon"] = sum(item[1] for item in wells) / len(wells)
        row["wells"] = len(wells)
        fips = Counter(item[2] for item in wells).most_common(1)[0][0]
        row["county_fips"] = "48" + fips
        row["county_name"] = county_names.get(fips, fips)
        row["district_code"] = row.pop("district")
        row["district_name"] = hb.DISTRICT_NAME.get(row["district_code"], row["district_code"])
        votes = operator_votes.get(key)
        row["operator_name"] = votes.most_common(1)[0][0] if votes else ""
        leases.append(row)

    located = [row for row in leases if row["flared_mcf"] > 0]
    located.sort(key=lambda row: row["flared_mmcfd"], reverse=True)
    print("leases with a well", len(leases), "with flared gas", len(located), flush=True)

    features = []
    for row in located:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(row["lon"], 5), round(row["lat"], 5)]},
            "properties": {
                "kind": row["kind"],
                "district": row["district_name"],
                "lease_no": row["lease_no"],
                "lease_name": row["lease_name"],
                "field_name": row["field_name"],
                "operator_no": row["operator_no"],
                "operator_name": row["operator_name"],
                "period": f"{row['period'][:4]}-{row['period'][4:6]}" if len(row["period"]) == 6 else row["period"],
                "flared_mcf": row["flared_mcf"],
                "produced_mcf": row["produced_mcf"],
                "flared_mmcfd": round(row["flared_mmcfd"], 3),
                "wells": row["wells"],
                "county": row["county_name"],
            },
        })
    args.out.mkdir(parents=True, exist_ok=True)
    hb.write_collection(args.out / "leases.geojson", features)
    hb.write_collection(args.out / "counties.geojson", county_features)

    pipes, lines, tieins = hb.clip_network(prepared)
    hb.write_collection(args.out / "pipelines.geojson", pipes)
    hb.write_collection(args.out / "transmission.geojson", lines)
    hb.write_collection(args.out / "tieins.geojson", [])
    print("pipelines", len(pipes), "transmission", len(lines), flush=True)

    poi_error = ""
    try:
        pois = hb.build_pois_layer(county_features)
    except Exception as exc:
        pois = []
        poi_error = str(exc)
        print("poi fetch failed", poi_error, flush=True)
    hb.write_collection(args.out / "pois.geojson", pois)
    print("pois", len(pois), flush=True)

    summary = {
        "retrieved_on": datetime.now(timezone.utc).date().isoformat(),
        "counties": [county_names[code] for code in codes],
        "leases": len(located),
        "flared_mmcfd": round(sum(row["flared_mmcfd"] for row in located), 2),
        "pipelines": len(pipes),
        "transmission": len(lines),
        "pois": len(pois),
        "poi_error": poi_error,
        "tieins": 0,
    }
    (args.out / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
