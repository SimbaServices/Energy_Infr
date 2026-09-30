"""Match flared leases for one shard of Texas counties.

Accepts the API records that do not start with record type 3, and keeps a
lease when its number and name agree even if the field name was left off the
well record. Counties with no well or API file are skipped.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path("/home/propeval/Energy_Infr")
COUNTIES = Path("/var/www/energy-sandbox/data/texas/counties.geojson")
BASIN = ROOT / "data" / "haynesville-tx" / "build.py"


def norm(text: str) -> str:
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def names_agree(record: str, lease_name: str) -> bool:
    raw = lease_name.strip()
    want = norm(raw)
    if len(want) < 4:
        return bool(raw) and re.search(rf"(?<![A-Z0-9]){re.escape(raw)}(?![A-Z0-9])", record) is not None
    return want in norm(record)


def api_records(path: Path, county: str):
    for raw in path.read_bytes().splitlines():
        line = raw.decode("latin1")
        if len(line) < 120 or line[7:10] != county or not line[7:15].isdigit():
            continue
        yield line


def match_lease(line: str, by_number: dict):
    numbers = set()
    for token in re.findall(r"\d{5,6}", line):
        numbers.add(("oil", token[-5:]))
        if len(token) >= 6:
            numbers.add(("gas", token[-6:]))
    hits = []
    for kind, number in numbers:
        for row in by_number.get((kind, number), ()):
            if not names_agree(line, row["lease_name"]):
                continue
            field = norm(row["field_name"])
            field_ok = len(field) >= 4 and field in norm(line)
            hits.append((field_ok, len(norm(row["lease_name"])), row["flared_mcf"], row))
    if not hits:
        return None
    hits.sort(key=lambda hit: hit[:3], reverse=True)
    return hits[0][3]


def load_basin():
    sys.path.insert(0, str(ROOT / "src"))
    spec = importlib.util.spec_from_file_location("haynesville_build", BASIN)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--shard", type=int, required=True)
    parser.add_argument("--shards", type=int, default=8)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    hb = load_basin()
    counties = json.loads(COUNTIES.read_text())["features"]
    codes = sorted(feature["properties"]["fips"] for feature in counties)
    names = {feature["properties"]["fips"]: feature["properties"]["name"] for feature in counties}
    mine = [code for index, code in enumerate(codes) if index % args.shards == args.shard]
    dispositions = hb.load_dispositions()
    by_number = hb.index_dispositions(dispositions)
    chosen = {}
    county_of_api = {}
    points_by_county = {}
    operator_votes = defaultdict(Counter)
    for county in mine:
        api_path = hb.RRC / "api" / f"cc{county}"
        well_path = hb.RRC / "wells" / f"well{county}.zip"
        if not api_path.is_file() or not well_path.is_file():
            print(f"  {county} {names.get(county)} missing files", flush=True)
            continue
        points = hb.dbf_points(well_path)
        points_by_county[county] = points
        matched = flared = 0
        for line in api_records(api_path, county):
            row = match_lease(line, by_number)
            if row is None:
                continue
            api = line[7:15]
            if api not in points:
                continue
            matched += 1
            if row["flared_mcf"] <= 0:
                continue
            flared += 1
            key = (row["kind"], row["district"], row["lease_no"])
            prev = chosen.get(api)
            if prev is None:
                chosen[api] = (key, county, hb.operator_name(line))
                county_of_api[api] = county
            if chosen[api][2] == "" :
                name = hb.operator_name(line)
                if name:
                    chosen[api] = (key, county, name)
            operator_votes[key][chosen[api][2]] += 1
        print(f"  {county} {names.get(county)} wells {len(points)} matched {matched} flared {flared}", flush=True)

    groups = defaultdict(list)
    for api, (key, county, op_name) in chosen.items():
        lat, lon = points_by_county[county][api]
        groups[key].append((lat, lon, county, op_name))

    features = []
    for key, wells in groups.items():
        row = dict(dispositions[key])
        if row["flared_mcf"] <= 0:
            continue
        row["flared_mmcfd"] = row["flared_mcf"] / 1000 / hb.days_in(row["period"])
        fips = Counter(item[2] for item in wells).most_common(1)[0][0]
        votes = operator_votes.get(key)
        features.append({
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    round(sum(item[1] for item in wells) / len(wells), 5),
                    round(sum(item[0] for item in wells) / len(wells), 5),
                ],
            },
            "properties": {
                "kind": row["kind"],
                "district": row["district"],
                "lease_no": row["lease_no"],
                "lease_name": row["lease_name"],
                "field_name": row["field_name"],
                "operator_no": row["operator_no"],
                "operator_name": votes.most_common(1)[0][0] if votes and votes.most_common(1)[0][0] else "",
                "period": f"{row['period'][:4]}-{row['period'][4:6]}" if len(row["period"]) == 6 else row["period"],
                "flared_mcf": row["flared_mcf"],
                "produced_mcf": row["produced_mcf"],
                "flared_mmcfd": round(row["flared_mmcfd"], 3),
                "wells": len(wells),
                "county": names.get(fips, fips),
            },
        })
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out / "leases.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}, separators=(",", ":")),
        encoding="utf-8",
    )
    summary = {"shard": args.shard, "counties": len(mine), "leases": len(features)}
    (args.out / "summary.json").write_text(json.dumps(summary), encoding="utf-8")
    print(json.dumps(summary), flush=True)


if __name__ == "__main__":
    main()
