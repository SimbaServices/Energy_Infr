"""Build the Texas Haynesville map files.

Same inputs as src/load_permian.py: RRC Form PR tapes (olf102, gsf102),
the statewide API extract, and the surface-well shapefiles. County well and
API files that are not already on disk are retrieved from the same RRC
GoDrive links. Outputs stay in this folder. Louisiana and Oklahoma are not
included.
"""
import calendar
import json
import re
import sqlite3
import struct
import sys
import zipfile
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

import build_pois  # noqa: E402
import download_permian as dl  # noqa: E402

OUT = Path(__file__).resolve().parent
RRC = ROOT / "data" / "raw" / "rrc"
DB = ROOT / "db" / "us_pipelines.sqlite"
COUNTIES_PATH = ROOT / "data" / "raw" / "geo" / "counties.geojson"
CACHE = OUT / "cache"

WELL_LINK = "https://mft.rrc.texas.gov/link/d551fb20-442e-4b67-84fa-ac3f23ecabb4"
API_LINK = "https://mft.rrc.texas.gov/link/701db9a3-32b5-488d-812b-cd6ff7d0fe85"
API_FOLDER = "2026-09-23"
RRC_CATALOG = "https://www.rrc.texas.gov/resource-center/research/data-sets-available-for-download/"
SUBSTATION_URL = build_pois.SUBSTATION_URL
LINE_URL = build_pois.LINE_URL

# Named in the request, then Texas counties that share a border with one of
# those eight in data/raw/geo/counties.geojson. No Louisiana parish is included.
COUNTIES = [
    "183",  # Gregg
    "203",  # Harrison
    "347",  # Nacogdoches
    "365",  # Panola
    "401",  # Rusk
    "403",  # Sabine
    "405",  # San Augustine
    "419",  # Shelby
    "005",  # Angelina, borders Nacogdoches
    "073",  # Cherokee, borders Rusk and Nacogdoches
    "241",  # Jasper, shares a border with San Augustine
    "315",  # Marion, borders Harrison
    "351",  # Newton, borders Sabine
    "423",  # Smith, borders Gregg and Rusk
    "459",  # Upshur, borders Gregg and Harrison
]
# Tape codes for RRC districts 6, 5, 6E, and 3. Haynesville and Carthage
# filings on these tapes are districts 06 and 05. 07 is the East Texas field
# (6E) in Gregg and Rusk. 03 is the line under Jasper and Newton.
DISTRICTS = ("06", "05", "07", "03")
DISTRICT_NAME = {"03": "03", "05": "05", "06": "06", "07": "6E"}


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


COMPANY_END = re.compile(
    r"(?:L\.\s*L\.\s*C\.|L\.L\.C\.|L\.\s*P\.|L\.P\.|L\.\s*C\.|CORPORATION|COMPANY|LLC|INC\.?|CORP|LTD)\.?$"
)
DATE = re.compile(r"(?:19|20)\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01])")


def operator_name(record):
    """Operator text from the well record. The Permian column is shifted on these rows."""
    parts = [part.strip() for part in re.split(r"\s{2,}", record[15:220])]
    for part in parts:
        part = part.strip(" ,")
        if not COMPANY_END.search(part):
            continue
        name = re.sub(r"\s+", " ", part).strip()
        name = re.sub(r"^(?:\d{2,6}\s+)+", "", name).strip(" ,-")
        letters = sum(ch.isalpha() for ch in name)
        if letters < 3 or len(name) > 48:
            continue
        return name
    return ""


def completion_date(record):
    """Completion dates on these rows are not at the Permian column."""
    dates = [match.group(0) for match in DATE.finditer(record[120:])]
    if not dates:
        return "00000000"
    return max(dates)


def load_dispositions():
    rows = {}
    oil_path = RRC / "olf102"
    gas_path = RRC / "gsf102"
    missing = [str(path) for path in (oil_path, gas_path) if not path.exists()]
    if missing:
        raise SystemExit("missing Form PR tape: " + ", ".join(missing))
    with oil_path.open("rb") as handle:
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
    with gas_path.open("rb") as handle:
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
        if not raw.startswith(b"3"):
            continue
        line = raw.decode("latin1")
        if len(line) < 240 or line[7:10] != county or not line[7:15].isdigit():
            continue
        yield line


def index_dispositions(dispositions):
    """Lease number -> rows. The API extract does not keep the id at one column."""
    by_number = {}
    for (kind, _district, number), row in dispositions.items():
        by_number.setdefault((kind, number), []).append(row)
    return by_number


def id_candidates(line):
    """Gas ids are 6 digits and oil ids are 5, often packed in a longer number."""
    found = []
    for match in re.finditer(r"(?<!\d)(\d{5,12})(?!\d)", line):
        token = match.group(1)
        if len(token) == 12:
            found.append(("gas", token[:6]))
            found.append(("gas", token[-6:]))
            found.append(("oil", token[-5:]))
        elif len(token) == 6:
            found.append(("gas", token))
            found.append(("oil", token[-5:]))
        elif len(token) == 5:
            found.append(("oil", token))
        else:
            found.append(("gas", token[-6:]))
            found.append(("oil", token[-5:]))
    seen = set()
    out = []
    for item in found:
        if item in seen or set(item[1]) == {"0"}:
            continue
        seen.add(item)
        out.append(item)
    return out


def match_lease(line, by_number):
    hits = []
    for kind, number in id_candidates(line):
        for row in by_number.get((kind, number), ()):
            if row["district"] not in DISTRICTS:
                continue
            if not names_agree(line, row["lease_name"]):
                continue
            field = row["field_name"].strip()
            if len(norm(field)) < 4 or norm(field) not in norm(line):
                continue
            hits.append((len(norm(row["lease_name"])), row))
    if not hits:
        return None
    hits.sort(key=lambda item: item[0], reverse=True)
    row = hits[0][1]
    return (row["kind"], row["district"], row["lease_no"])


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
    elif kind == "Polygon":
        for ring in coords:
            yield from ring
    elif kind == "MultiPolygon":
        for polygon in coords:
            for ring in polygon:
                yield from ring


def point_in_geom(lon, lat, geometry):
    kind = geometry["type"]
    if kind == "Polygon":
        return build_pois.point_in_polygon(lon, lat, geometry["coordinates"])
    if kind == "MultiPolygon":
        return any(build_pois.point_in_polygon(lon, lat, rings) for rings in geometry["coordinates"])
    return False


def bounds_of(geometry):
    lons = []
    lats = []
    for lon, lat in iter_coords(geometry):
        lons.append(lon)
        lats.append(lat)
    return (min(lons), min(lats), max(lons), max(lats))


def geometry_hits(geometry, counties):
    for lon, lat in iter_coords(geometry):
        for bbox, geom in counties:
            min_lon, min_lat, max_lon, max_lat = bbox
            if not (min_lon <= lon <= max_lon and min_lat <= lat <= max_lat):
                continue
            if point_in_geom(lon, lat, geom):
                return True
    return False


def write_collection(path, features):
    path.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")


def file_names(html):
    return {name: row for row, name in dl.file_index(html).items()}


def page_until(op, link, view, html, predicate):
    """Walk the GoDrive table. predicate(names, html, view) returns a truthy hit or None."""
    first = 0
    seen = set()
    while True:
        names = file_names(html)
        if not names:
            return None
        fresh = [name for name in names if name not in seen]
        if not fresh and first > 0:
            return None
        seen.update(names)
        hit = predicate(names, html, view)
        if hit is not None:
            return hit
        first += 250
        if first > 4000:
            return None
        html = dl.ajax(op, link, dl.page_form(view, first))
        view = dl.viewstate(html)


def download_named_files(op, link, view, html, wanted, dest_of):
    missing = set(wanted)
    first = 0
    seen = set()
    while missing:
        names = file_names(html)
        if not names:
            break
        if set(names) <= seen and first > 0:
            break
        seen.update(names)
        for name, row in names.items():
            if name not in missing:
                continue
            dest = dest_of(name)
            dl.download_named(op, link, view, row, dest)
            missing.discard(name)
        if not missing:
            break
        first += 250
        if first > 2000:
            break
        html = dl.ajax(op, link, dl.page_form(view, first))
        view = dl.viewstate(html)
    return sorted(missing)


def download_wells():
    wanted = {f"well{code}.zip" for code in COUNTIES}
    op = dl.opener()
    page = dl.call(op, WELL_LINK).decode("utf-8", "replace")
    view = dl.viewstate(page)
    missing = download_named_files(
        op,
        WELL_LINK,
        view,
        page,
        wanted,
        lambda name: RRC / "wells" / name,
    )
    if missing:
        raise SystemExit("missing well shapefiles: " + ", ".join(missing))


def folder_ids(html):
    return dict(re.findall(r'id="(fileTable:\d+:j_id_2d)"[^>]*>([^<]+)<', html))


def download_api():
    wanted = {f"maf016.cc{code}" for code in COUNTIES}
    op = dl.opener()
    page = dl.call(op, API_LINK).decode("utf-8", "replace")
    view = dl.viewstate(page)
    found = {}
    first = 0
    seen = set()
    while True:
        folders = folder_ids(page)
        if not folders:
            break
        labels = set(folders.values())
        if labels <= seen and first > 0:
            break
        seen.update(labels)
        found.update({label: source for source, label in folders.items()})
        if API_FOLDER in found:
            break
        first += 250
        if first > 4000:
            break
        page = dl.ajax(op, API_LINK, dl.page_form(view, first))
        view = dl.viewstate(page)
    if API_FOLDER not in found:
        dates = sorted(label for label in found if re.fullmatch(r"\d{4}-\d{2}-\d{2}", label))
        shown = ", ".join(dates[-8:]) if dates else "none"
        raise SystemExit(f"missing API folder {API_FOLDER}. Latest folders seen: {shown}")
    source = found[API_FOLDER]
    inside = dl.ajax(
        op,
        API_LINK,
        {
            "javax.faces.partial.ajax": "true",
            "javax.faces.source": source,
            "javax.faces.partial.execute": source,
            "javax.faces.partial.render": "breadcrumbForm fileList toolbarForm messages",
            "fileList_SUBMIT": "1",
            "javax.faces.ViewState": view,
            source: source,
        },
    )
    view = dl.viewstate(inside)
    missing = download_named_files(
        op,
        API_LINK,
        view,
        inside,
        wanted,
        lambda name: RRC / "api" / f"cc{name[-3:]}",
    )
    if missing:
        raise SystemExit("missing API extracts: " + ", ".join(missing))


def load_county_geoms():
    payload = json.loads(COUNTIES_PATH.read_text(encoding="utf-8"))
    wanted = set(COUNTIES)
    features = []
    prepared = []
    names = {}
    for feature in payload["features"]:
        props = feature["properties"]
        if props.get("STATE") != "48" or props.get("COUNTY") not in wanted:
            continue
        geometry = feature["geometry"]
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {"name": props["NAME"], "fips": props["COUNTY"]},
        })
        prepared.append((bounds_of(geometry), geometry))
        names[props["COUNTY"]] = props["NAME"]
    missing = [code for code in COUNTIES if code not in names]
    if missing:
        raise SystemExit("county polygons missing for " + ", ".join(missing))
    return features, prepared, names


def clip_network(prepared):
    pipes = []
    lines = []
    conn = sqlite3.connect(f"file:{DB.as_posix()}?mode=ro", uri=True)
    try:
        for operator, pipe_type, geometry_text in conn.execute(
            "SELECT operator, pipe_type, geojson FROM pipelines"
        ):
            geometry = json.loads(geometry_text)
            if geometry_hits(geometry, prepared):
                pipes.append({
                    "type": "Feature",
                    "geometry": _round_geom(geometry),
                    "properties": {"operator": operator or "", "pipe_type": pipe_type or ""},
                })
        for owner, voltage, geometry_text in conn.execute(
            "SELECT owner, voltage_kv, geojson FROM transmission_lines"
        ):
            geometry = json.loads(geometry_text)
            if geometry_hits(geometry, prepared):
                lines.append({
                    "type": "Feature",
                    "geometry": _round_geom(geometry),
                    "properties": {"owner": owner or "", "voltage_kv": voltage},
                })
        tieins = []
        for lat, lon, voltage, owner, operator, distance in conn.execute(
            """
            SELECT lat, lon, voltage_kv, owner, pipeline_operator, distance_miles
            FROM interconnects
            """
        ):
            if any(point_in_geom(lon, lat, geom) for bbox, geom in prepared if _in_bbox(lon, lat, bbox)):
                tieins.append({
                    "type": "Feature",
                    "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
                    "properties": {
                        "voltage_kv": voltage,
                        "owner": owner or "",
                        "pipeline_operator": operator or "",
                        "distance_miles": round(distance, 2) if distance is not None else None,
                    },
                })
    finally:
        conn.close()
    return pipes, lines, tieins


def _in_bbox(lon, lat, bbox):
    min_lon, min_lat, max_lon, max_lat = bbox
    return min_lon <= lon <= max_lon and min_lat <= lat <= max_lat


def _round_geom(geometry):
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


def build_pois_layer(county_features):
    lons = []
    lats = []
    for feature in county_features:
        for lon, lat in iter_coords(feature["geometry"]):
            lons.append(lon)
            lats.append(lat)
    box = (min(lons) - 0.05, min(lats) - 0.05, max(lons) + 0.05, max(lats) + 0.05)
    box_text = f"{box[0]},{box[1]},{box[2]},{box[3]}"
    county_pairs = [(feature["properties"]["name"], feature["geometry"]) for feature in county_features]
    county_names = {name.upper() for name, _geometry in county_pairs}
    substations = build_pois.load_or_fetch(
        CACHE / "substations.geojson",
        SUBSTATION_URL,
        {
            "where": "STATE = 'TX' AND (MAX_VOLT >= 69 OR MAX_VOLT < 0)",
            "geometry": box_text,
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "ID,NAME,CITY,STATE,COUNTY,TYPE,STATUS,LINES,MAX_VOLT,MIN_VOLT,MAX_INFER,MIN_INFER,SOURCEDATE",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
        },
    )
    lines = build_pois.load_or_fetch(
        CACHE / "lines69.geojson",
        LINE_URL,
        {
            "where": "VOLTAGE >= 69 AND STATUS = 'IN SERVICE'",
            "geometry": box_text,
            "geometryType": "esriGeometryEnvelope",
            "inSR": "4326",
            "spatialRel": "esriSpatialRelIntersects",
            "outFields": "ID,OWNER,VOLTAGE,SUB_1,SUB_2,STATUS",
            "returnGeometry": "true",
            "outSR": "4326",
            "geometryPrecision": "5",
            "f": "geojson",
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
                "state": "Texas",
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
    return features


def main():
    print("downloading wells", flush=True)
    download_wells()
    print("downloading api", flush=True)
    download_api()
    dispositions = load_dispositions()
    by_number = index_dispositions(dispositions)
    print("disposition leases", len(dispositions), flush=True)
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
            key = match_lease(line, by_number)
            if key is None:
                continue
            api = line[7:15]
            if api not in points:
                continue
            date = completion_date(line)
            name = operator_name(line)
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

    county_features, prepared, county_names = load_county_geoms()
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
    print("leases with a well", len(leases), "with flared gas", len(located), flush=True)
    if not located:
        raise SystemExit("no flared leases matched; refusing to write an empty flare layer")

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
                "period": row["period"],
                "flared_mcf": row["flared_mcf"],
                "produced_mcf": row["produced_mcf"],
                "flared_mmcfd": round(row["flared_mmcfd"], 3),
                "wells": row["wells"],
                "county": row["county_name"],
            },
        })
    write_collection(OUT / "leases.geojson", features)
    write_collection(OUT / "counties.geojson", county_features)

    pipes, lines, tieins = clip_network(prepared)
    write_collection(OUT / "pipelines.geojson", pipes)
    write_collection(OUT / "transmission.geojson", lines)
    write_collection(OUT / "tieins.geojson", tieins)
    print("pipelines", len(pipes), "transmission", len(lines), "tieins", len(tieins), flush=True)

    poi_error = ""
    try:
        pois = build_pois_layer(county_features)
    except Exception as exc:
        pois = []
        poi_error = str(exc)
        print("poi fetch failed", poi_error, flush=True)
    write_collection(OUT / "pois.geojson", pois)
    print("pois", len(pois), flush=True)

    def mmcfd(rows):
        return round(sum(row["flared_mmcfd"] for row in rows), 2)

    summary = {
        "tape_posted": "2026-09-26",
        "api_folder": API_FOLDER,
        "wells_posted": "",
        "retrieved_on": datetime.now(timezone.utc).date().isoformat(),
        "leases": len(located),
        "flared_mmcfd": mmcfd(located),
        "flared_mcf": round(sum(row["flared_mcf"] for row in located)),
        "oil_leases": sum(row["kind"] == "oil" for row in located),
        "gas_wells": sum(row["kind"] == "gas" for row in located),
        "counties": [county_names[code] for code in COUNTIES],
        "pipelines": len(pipes),
        "transmission": len(lines),
        "tieins": len(tieins),
        "pois": len(pois),
        "poi_error": poi_error,
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
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    county_lines = "\n".join(
        f"{code}  {county_names[code]} County" for code in COUNTIES
    )
    poi_note = (
        "The substation service did not return points. " + poi_error
        if poi_error
        else "Substations were filtered to the counties above after a bounding-box query."
    )
    source = f"""Texas Haynesville
Retrieved {summary['retrieved_on']}

Counties
Named in the request: Gregg, Harrison, Nacogdoches, Panola, Rusk, Sabine, San Augustine, Shelby.
Adjacent Texas counties are those that share a boundary segment with one of those eight in data/raw/geo/counties.geojson: Angelina, Cherokee, Jasper, Marion, Newton, Smith, Upshur.
Cass does not share a boundary segment with the named eight.
Not included: Louisiana parishes, Oklahoma, and every other Texas county.

{county_lines}

Flare volumes
Texas Railroad Commission Form PR gas disposition, files olf102 (oil) and gsf102 (gas) in data/raw/rrc.
Catalog: {RRC_CATALOG}
The project source table records this tape posting as 2026-09-26. One vented-or-flared column, latest month on the tape for each lease. Mcf for that month, divided by days in the month, is MMcfd.
Oil tape districts 05, 06, and 07 are RRC districts 5, 6, and 6E. 6E is the East Texas field. District 03 is included because Jasper and Newton sit on that line. Haynesville and Carthage field names on these tapes are in districts 05 and 06.
A lease is drawn only when its number, lease name, and field name occur on a well record in one of the counties above. The point is the centroid of those surface wells. The volume is the whole lease, not a split for wells outside the county list.

Well locations
Surface latitude and longitude (LAT83, LONG83, NAD83) from the RRC well shapefiles.
{WELL_LINK}
API extract folder {API_FOLDER}, file maf016:
{API_LINK}
The number in the API extract is not in one fixed column, so the join reads the 5-digit oil and 6-digit gas ids packed in that record and keeps a row only when the lease name and field name both agree.

Pipelines
EIA natural gas pipeline centerlines in db/us_pipelines.sqlite, kept when a vertex falls in one of the counties.
https://geo.dot.gov/server/rest/services/hosted/Natural_Gas_Pipelines_US_EIA/FeatureServer/0

Transmission
Public 230 kV-and-above lines in the same database, kept when a vertex falls in one of the counties.
https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Electric_Power_Transmission_Lines/FeatureServer/0

Tie-ins
Rows already computed in the interconnects table: the midpoint of a transmission line within 3 miles of a gas pipeline midpoint, thinned to the highest voltage in each cell. A point is kept only when it falls in one of the counties. No new points were calculated for this folder.

Points of interconnection
Public substation republish, 69 kV and above, and in-service transmission lines used to name the utility within half a mile. Same services as src/build_pois.py.
{SUBSTATION_URL}
{LINE_URL}
{poi_note}

No hub assignments or prices are in this folder.

Record counts
leases with flared gas: {summary['leases']}
flared Mcf in the latest month on each lease: {summary['flared_mcf']}
flared MMcfd: {summary['flared_mmcfd']}
oil leases: {summary['oil_leases']}
gas wells: {summary['gas_wells']}
pipelines: {summary['pipelines']}
transmission lines: {summary['transmission']}
tie-ins: {summary['tieins']}
points of interconnection: {summary['pois']}
"""
    (OUT / "SOURCE.txt").write_text(source, encoding="utf-8")
    print("largest", located[0]["lease_name"], round(located[0]["flared_mmcfd"], 2), "MMcfd", flush=True)
    print("summary written", flush=True)


if __name__ == "__main__":
    main()
