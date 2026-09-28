"""Place Texas Permian lease flare volumes and write the map files.

Reads the RRC Form PR gas-disposition tapes and the county API / well
files in data/raw/rrc. Does not rebuild the rest of the database.
"""
import calendar
import json
import re
import sqlite3
import struct
import zipfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RRC = ROOT / "data" / "raw" / "rrc"
DB = ROOT / "db" / "us_pipelines.sqlite"
WEB = ROOT / "web" / "data"
COUNTIES = [
    "003", "033", "103", "105", "109", "115", "135", "165", "169", "173",
    "227", "235", "301", "317", "329", "335", "371", "383", "389", "415",
    "431", "443", "461", "475", "495", "501",
]
DISTRICTS = ("09", "10", "11")
DISTRICT_NAME = {"09": "7C", "10": "08", "11": "8A"}
BOX = (-104.4, 29.8, -99.6, 34.2)  # lon, lat, lon, lat


def norm(text):
    return re.sub(r"[^A-Z0-9]", "", text.upper())


def names_agree(record, lease_name):
    raw = lease_name.strip()
    want = norm(raw)
    if len(want) < 4:
        return bool(raw) and re.search(rf"(?<![A-Z0-9]){re.escape(raw)}(?![A-Z0-9])", record)
    return want in norm(record)


def days_in(period):
    return calendar.monthrange(int(period[:4]), int(period[4:6]))[1]


def operator_name(record):
    text = re.sub(r"\s+\d.*$", "", record[94:128]).strip()
    letters = sum(ch.isalpha() for ch in text)
    if letters < 3:
        return ""
    return re.sub(r"\s+", " ", text)


def load_dispositions():
    """Latest tape row for each lease. Volumes are Mcf for that month."""
    rows = {}
    # oil: lease at 2:7, period at 7:13, name 36:68, field 68:100, operator 16:22
    # gas: id at 2:8, period at 8:14, name 70:102, field 38:70, operator 18:24
    with (RRC / "olf102").open("rb") as handle:
        for raw in handle:
            rec = raw[:200].decode("latin1")
            key = ("oil", rec[0:2], rec[2:7])
            period = rec[7:13]
            prev = rows.get(key)
            if prev and prev["period"] > period:
                continue
            rows[key] = {
                "kind": "oil",
                "district": rec[0:2],
                "lease_no": rec[2:7],
                "period": period,
                "lease_name": rec[36:68].strip(),
                "field_name": rec[68:100].strip(),
                "operator_no": rec[16:22].strip(),
                "flared_mcf": int(rec[131:140]),
                "produced_mcf": int(rec[176:185]),
            }
    with (RRC / "gsf102").open("rb") as handle:
        for raw in handle:
            rec = raw[:200].decode("latin1")
            key = ("gas", rec[0:2], rec[2:8])
            period = rec[8:14]
            prev = rows.get(key)
            if prev and prev["period"] > period:
                continue
            rows[key] = {
                "kind": "gas",
                "district": rec[0:2],
                "lease_no": rec[2:8],
                "period": period,
                "lease_name": rec[70:102].strip(),
                "field_name": rec[38:70].strip(),
                "operator_no": rec[18:24].strip(),
                "flared_mcf": int(rec[130:137]),
                "produced_mcf": int(rec[172:179]),
            }
    return rows


def dbf_points(path):
    """API -> (lat, lon) from the surface-well shapefile, NAD83."""
    with zipfile.ZipFile(path) as zf:
        name = next(item for item in zf.namelist() if item.lower().endswith("s.dbf"))
        data = zf.read(name)
    count = struct.unpack_from("<I", data, 4)[0]
    header = struct.unpack_from("<H", data, 8)[0]
    recsize = struct.unpack_from("<H", data, 10)[0]
    fields = []
    pos = 32
    offset = 1
    while pos < header - 1 and data[pos] != 0x0D:
        desc = data[pos : pos + 32]
        fields.append((desc[:11].split(b"\x00")[0].decode(), offset, desc[16]))
        offset += desc[16]
        pos += 32
    index = {name: (start, length) for name, start, length in fields}
    points = {}
    for i in range(count):
        rec = data[header + i * recsize : header + (i + 1) * recsize]
        if rec[:1] == b"*":
            continue
        def value(field):
            start, length = index[field]
            return rec[start : start + length].decode("latin1").strip()
        api = value("API")
        try:
            lat = float(value("LAT83"))
            lon = float(value("LONG83"))
        except ValueError:
            continue
        if not (25 < lat < 37 and -107 < lon < -93):
            continue
        points[api] = (lat, lon)
    return points


def api_records(path, county):
    for raw in path.read_bytes().splitlines():
        # 3201/3202 in the Midland Basin, 3103/3104 in the Delaware Basin.
        if not raw.startswith(b"3"):
            continue
        line = raw.decode("latin1")
        if len(line) < 240 or line[7:10] != county or not line[7:15].isdigit():
            continue
        yield line


def match_lease(line, dispositions):
    """Return a disposition key when the lease id and the lease name agree."""
    oil_no = line[182:187]
    if oil_no.isdigit():
        for district in DISTRICTS:
            row = dispositions.get(("oil", district, oil_no))
            if row and names_agree(line, row["lease_name"]):
                return ("oil", district, oil_no)
    for start in (176, 170):
        gas_no = line[start : start + 6]
        if not gas_no.isdigit():
            continue
        for district in DISTRICTS:
            row = dispositions.get(("gas", district, gas_no))
            if row and names_agree(line, row["lease_name"]):
                return ("gas", district, gas_no)
    return None


def iter_coords(geometry):
    kind = geometry["type"]
    coords = geometry["coordinates"]
    if kind == "LineString":
        yield from coords
    elif kind == "MultiLineString":
        for line in coords:
            yield from line
    elif kind == "Point":
        yield coords


def hits_box(geometry, box):
    min_lon, min_lat, max_lon, max_lat = box
    return any(min_lon <= lon <= max_lon and min_lat <= lat <= max_lat for lon, lat in iter_coords(geometry))


def round_geom(geometry):
    def rnd(pair):
        return [round(pair[0], 5), round(pair[1], 5)]
    kind = geometry["type"]
    if kind == "LineString":
        return {"type": kind, "coordinates": [rnd(p) for p in geometry["coordinates"]]}
    if kind == "MultiLineString":
        return {"type": kind, "coordinates": [[rnd(p) for p in line] for line in geometry["coordinates"]]}
    if kind == "Point":
        return {"type": kind, "coordinates": rnd(geometry["coordinates"])}
    return geometry


def write_layers(conn, leases, box):
    WEB.mkdir(parents=True, exist_ok=True)
    features = []
    for row in leases:
        if row["lat"] is None or row["flared_mcf"] <= 0:
            continue
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
                "period": row["period"],
                "flared_mcf": row["flared_mcf"],
                "produced_mcf": row["produced_mcf"],
                "flared_mmcfd": round(row["flared_mmcfd"], 3),
                "wells": row["wells"],
                "county": row["county_name"],
            },
        })
    (WEB / "leases.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )
    print("lease points", len(features))

    pipes = []
    for operator, pipe_type, geometry_text in conn.execute("SELECT operator, pipe_type, geojson FROM pipelines"):
        geometry = json.loads(geometry_text)
        if hits_box(geometry, box):
            pipes.append({
                "type": "Feature",
                "geometry": round_geom(geometry),
                "properties": {"operator": operator or "", "pipe_type": pipe_type or ""},
            })
    (WEB / "pipelines.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": pipes}),
        encoding="utf-8",
    )
    print("pipelines", len(pipes))

    lines = []
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
    (WEB / "transmission.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": lines}),
        encoding="utf-8",
    )
    print("transmission", len(lines))

    (WEB / "tieins.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": []}),
        encoding="utf-8",
    )

    counties = json.loads((ROOT / "data" / "raw" / "geo" / "counties.geojson").read_text(encoding="utf-8"))
    wanted = set(COUNTIES)
    county_features = []
    names = {}
    for feature in counties["features"]:
        props = feature["properties"]
        if props.get("STATE") == "48" and props.get("COUNTY") in wanted:
            county_features.append({
                "type": "Feature",
                "geometry": feature["geometry"],
                "properties": {"name": props["NAME"], "fips": props["COUNTY"]},
            })
            names[props["COUNTY"]] = props["NAME"]
    (WEB / "counties.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": county_features}),
        encoding="utf-8",
    )
    return names


def main():
    dispositions = load_dispositions()
    print("disposition leases", len(dispositions))
    # api -> list of (completion date, key, operator name)
    chosen = {}
    county_of_api = {}
    points_by_county = {}
    operator_votes = defaultdict(Counter)
    for county in COUNTIES:
        api_path = RRC / "api" / f"cc{county}"
        well_path = RRC / "wells" / f"well{county}.zip"
        if not api_path.exists() or not well_path.exists():
            raise SystemExit(f"missing {county}: api={api_path.exists()} wells={well_path.exists()}")
        points = dbf_points(well_path)
        points_by_county[county] = points
        matched = 0
        for line in api_records(api_path, county):
            key = match_lease(line, dispositions)
            if key is None:
                continue
            api = line[7:15]
            if api not in points:
                continue
            date = line[220:228]
            if not date.isdigit():
                date = "00000000"
            name = operator_name(line)
            prev = chosen.get(api)
            if prev is None or date >= prev[0]:
                chosen[api] = (date, key, name)
                county_of_api[api] = county
            matched += 1
        print(f"  {county} surface wells {len(points):6} name-matched {matched:6}")

    groups = defaultdict(list)
    for api, (_date, key, op_name) in chosen.items():
        county = county_of_api[api]
        lat, lon = points_by_county[county][api]
        groups[key].append((lat, lon, county, op_name))
        if op_name:
            operator_votes[key][op_name] += 1

    county_names = {}
    counties = json.loads((ROOT / "data" / "raw" / "geo" / "counties.geojson").read_text(encoding="utf-8"))
    for feature in counties["features"]:
        props = feature["properties"]
        if props.get("STATE") == "48":
            county_names[props["COUNTY"]] = props["NAME"]

    leases = []
    for key, wells in groups.items():
        row = dict(dispositions[key])
        if row["flared_mcf"] <= 0 and row["produced_mcf"] <= 0:
            continue
        row["flared_mmcfd"] = row["flared_mcf"] / 1000 / days_in(row["period"])
        row["lat"] = sum(item[0] for item in wells) / len(wells)
        row["lon"] = sum(item[1] for item in wells) / len(wells)
        row["wells"] = len(wells)
        fips = Counter(item[2] for item in wells).most_common(1)[0][0]
        row["county_fips"] = "48" + fips
        row["county_name"] = county_names.get(fips, fips)
        row["district_code"] = row.pop("district")
        row["district_name"] = DISTRICT_NAME.get(row["district_code"], row["district_code"])
        votes = operator_votes.get(key)
        row["operator_name"] = votes.most_common(1)[0][0] if votes else ""
        leases.append(row)

    located = [row for row in leases if row["flared_mcf"] > 0]
    located.sort(key=lambda row: row["flared_mmcfd"], reverse=True)
    print("leases with a well", len(leases), "with flared gas", len(located))
    if located:
        print("largest", located[0]["lease_name"], round(located[0]["flared_mmcfd"], 2), "MMcfd")
        print("drawn total", round(sum(row["flared_mmcfd"] for row in located), 1), "MMcfd")

    conn = sqlite3.connect(DB)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS permian_leases (
            id INTEGER PRIMARY KEY,
            source_id INTEGER REFERENCES sources(id),
            kind TEXT NOT NULL,
            district_code TEXT NOT NULL,
            district_name TEXT NOT NULL,
            lease_no TEXT NOT NULL,
            lease_name TEXT,
            field_name TEXT,
            operator_no TEXT,
            operator_name TEXT,
            period TEXT NOT NULL,
            flared_mcf REAL NOT NULL,
            produced_mcf REAL NOT NULL,
            flared_mmcfd REAL NOT NULL,
            lat REAL,
            lon REAL,
            wells INTEGER,
            county_fips TEXT,
            county_name TEXT
        )
        """
    )
    conn.execute("DELETE FROM permian_leases")
    source = conn.execute("SELECT id FROM sources WHERE name = ?", ("RRC Form PR gas disposition",)).fetchone()
    if source is None:
        cur = conn.execute(
            """
            INSERT INTO sources (name, url, retrieved_on, vintage, license, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                "RRC Form PR gas disposition",
                "https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/",
                "2026-09-26",
                "Tape posted 2026-09-26; API folder 2026-09-23; well layers 2026-09-26",
                "Public RRC download",
                "Oil file olf102 and gas file gsf102. One vented-or-flared column. Lease locations from MAF016 joined to surface-well LAT83/LONG83.",
            ),
        )
        source_id = cur.lastrowid
    else:
        source_id = source[0]
    conn.executemany(
        """
        INSERT INTO permian_leases (
            source_id, kind, district_code, district_name, lease_no, lease_name,
            field_name, operator_no, operator_name, period, flared_mcf, produced_mcf,
            flared_mmcfd, lat, lon, wells, county_fips, county_name
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        [
            (
                source_id, row["kind"], row["district_code"], row["district_name"], row["lease_no"],
                row["lease_name"], row["field_name"], row["operator_no"], row["operator_name"],
                row["period"], row["flared_mcf"], row["produced_mcf"], row["flared_mmcfd"],
                row["lat"], row["lon"], row["wells"], row["county_fips"], row["county_name"],
            )
            for row in leases
        ],
    )
    conn.commit()

    pad = 0.15
    if located:
        box = (
            min(row["lon"] for row in located) - pad,
            min(row["lat"] for row in located) - pad,
            max(row["lon"] for row in located) + pad,
            max(row["lat"] for row in located) + pad,
        )
    else:
        box = BOX
    write_layers(conn, leases, box)
    conn.close()

    def mmcfd(rows):
        return round(sum(row["flared_mmcfd"] for row in rows), 2)

    summary = {
        "tape_posted": "2026-09-26",
        "api_folder": "2026-09-23",
        "wells_posted": "2026-09-26",
        "leases": len(located),
        "flared_mmcfd": mmcfd(located),
        "flared_mcf": round(sum(row["flared_mcf"] for row in located)),
        "oil_leases": sum(row["kind"] == "oil" for row in located),
        "gas_wells": sum(row["kind"] == "gas" for row in located),
        "counties": [county_names.get(code, code) for code in COUNTIES],
        "top": [
            {
                "lease_name": row["lease_name"],
                "field_name": row["field_name"],
                "operator_name": row["operator_name"],
                "county": row["county_name"],
                "kind": row["kind"],
                "district": row["district_name"],
                "lease_no": row["lease_no"],
                "period": f"{row['period'][:4]}-{row['period'][4:6]}",
                "flared_mmcfd": round(row["flared_mmcfd"], 2),
                "flared_mcf": row["flared_mcf"],
                "produced_mcf": row["produced_mcf"],
                "lat": round(row["lat"], 5),
                "lon": round(row["lon"], 5),
            }
            for row in located[:25]
        ],
    }
    (WEB / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("summary written")


if __name__ == "__main__":
    main()
