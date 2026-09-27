"""Write Permian points of interconnection for the map.

A point of interconnection here is a substation or tap at 69 kV or higher
inside the Texas counties drawn on the map. Locations come from a public
republish of the former HIFLD Open substation layer. That layer has no owner
field, so the owner is taken from in-service transmission lines of 69 kV or
higher that pass within half a mile.

The line layer is the Esri archive of U.S. Electric Power Transmission Lines.
"""
import json
import math
import re
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web" / "data"
RAW = ROOT / "data" / "raw" / "geo"
COUNTIES = WEB / "counties.geojson"
SUBSTATION_CACHE = RAW / "permian_substations.geojson"
LINE_CACHE = RAW / "permian_lines_69kv.geojson"
OUT = WEB / "pois.geojson"

BOX = "-104.4,29.8,-99.6,34.2"
NEAR_MILES = 0.5
NAMED_END_MILES = 1.5

SUBSTATION_URL = (
    "https://services1.arcgis.com/7DRakJXKPEhwv0fM/arcgis/rest/services/"
    "Electric_Substations/FeatureServer/0/query"
)
LINE_URL = (
    "https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/"
    "US_Electric_Power_Transmission_Lines/FeatureServer/0/query"
)


def fetch_geojson(url, params):
    features = []
    offset = 0
    while True:
        page = dict(params)
        page["resultOffset"] = offset
        page["resultRecordCount"] = 2000
        query = url + "?" + urllib.parse.urlencode(page)
        request = urllib.request.Request(query, headers={"User-Agent": "US_Pipelines map"})
        with urllib.request.urlopen(request, timeout=180) as response:
            payload = json.load(response)
        batch = payload.get("features") or []
        features.extend(batch)
        if not payload.get("exceededTransferLimit") or not batch:
            break
        offset += len(batch)
    return {"type": "FeatureCollection", "features": features}


def load_or_fetch(path, url, params):
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    collection = fetch_geojson(url, params)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(collection), encoding="utf-8")
    print(f"cached {path.name}: {len(collection['features'])}")
    return collection


def point_in_ring(x, y, ring):
    inside = False
    j = len(ring) - 1
    for i, point in enumerate(ring):
        xi, yi = point[0], point[1]
        xj, yj = ring[j][0], ring[j][1]
        if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def point_in_polygon(x, y, rings):
    if not rings or not point_in_ring(x, y, rings[0]):
        return False
    return not any(point_in_ring(x, y, hole) for hole in rings[1:])


def county_of(lon, lat, counties):
    for name, geometry in counties:
        kind = geometry["type"]
        if kind == "Polygon" and point_in_polygon(lon, lat, geometry["coordinates"]):
            return name
        if kind == "MultiPolygon":
            for rings in geometry["coordinates"]:
                if point_in_polygon(lon, lat, rings):
                    return name
    return None


def volts(value):
    if value is None:
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    if number < 0:
        return None
    if number < 40:
        rounded = round(number, 1)
        if rounded == int(rounded):
            return int(rounded)
        return rounded
    return int(round(number))


def place(text):
    raw = (text or "").strip()
    if not raw:
        return ""
    if raw.isupper():
        raw = raw.title()
    return re.sub(r"\bMc([a-z])", lambda match: "Mc" + match.group(1).upper(), raw)


def unnamed(name):
    token = (name or "").strip().upper()
    if not token or token.startswith("UNKNOWN") or token in {"#5", "NONE", "NULL"}:
        return True
    if re.fullmatch(r"TAP\d+", token):
        return True
    return token.replace("#", "").isdigit()


def generic_end(name):
    token = (name or "").strip().upper()
    return (
        not token
        or token in {"NOT AVAILABLE", "NONE", "NULL", "UNKNOWN", "N/A"}
        or token.startswith("UNKNOWN")
        or token.startswith("TAP")
        or token.isdigit()
    )


def norm(text):
    return "".join(ch for ch in (text or "").upper() if ch.isalnum())


def segment_miles(lon, lat, start, end):
    lat0 = math.radians(lat)
    kx = 69.172 * math.cos(lat0)
    ky = 68.703
    ax = (start[0] - lon) * kx
    ay = (start[1] - lat) * ky
    bx = (end[0] - lon) * kx
    by = (end[1] - lat) * ky
    dx = bx - ax
    dy = by - ay
    denom = dx * dx + dy * dy
    if denom == 0:
        return math.hypot(ax, ay)
    t = max(0.0, min(1.0, (-ax * dx - ay * dy) / denom))
    return math.hypot(ax + t * dx, ay + t * dy)


def parts(geometry):
    kind = geometry["type"]
    if kind == "LineString":
        return [geometry["coordinates"]]
    if kind == "MultiLineString":
        return geometry["coordinates"]
    return []


def index_lines(collection):
    cell = 0.25
    buckets = {}
    for feature in collection["features"]:
        geometry = feature.get("geometry") or {}
        props = feature.get("properties") or {}
        voltage = volts(props.get("VOLTAGE"))
        if voltage is None or voltage < 69:
            continue
        owner = (props.get("OWNER") or "").strip()
        sub_1 = props.get("SUB_1") or ""
        sub_2 = props.get("SUB_2") or ""
        for line in parts(geometry):
            if len(line) < 2:
                continue
            record = {
                "owner": owner,
                "voltage": voltage,
                "sub_1": sub_1,
                "sub_2": sub_2,
                "coords": line,
            }
            seen = set()
            for start, end in zip(line, line[1:]):
                min_lon, max_lon = sorted((start[0], end[0]))
                min_lat, max_lat = sorted((start[1], end[1]))
                for ix in range(math.floor(min_lon / cell), math.floor(max_lon / cell) + 1):
                    for iy in range(math.floor(min_lat / cell), math.floor(max_lat / cell) + 1):
                        key = (ix, iy)
                        if key in seen:
                            continue
                        seen.add(key)
                        buckets.setdefault(key, []).append(record)
    return buckets, cell


def lines_near(lon, lat, buckets, cell, station_name):
    ix = math.floor(lon / cell)
    iy = math.floor(lat / cell)
    found = []
    seen = set()
    station_key = norm(station_name)
    station_named = not unnamed(station_name) and len(station_key) >= 4
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            for record in buckets.get((ix + dx, iy + dy), ()):
                identity = id(record)
                if identity in seen:
                    continue
                seen.add(identity)
                coords = record["coords"]
                distance = min(
                    segment_miles(lon, lat, start, end)
                    for start, end in zip(coords, coords[1:])
                )
                ends = (coords[0], coords[-1])
                end_distance = min(segment_miles(lon, lat, end, end) for end in ends)
                name_hit = station_named and station_key in {norm(record["sub_1"]), norm(record["sub_2"])}
                if distance <= NEAR_MILES or (name_hit and end_distance <= NAMED_END_MILES):
                    found.append({
                        "owner": record["owner"],
                        "voltage_kv": record["voltage"],
                        "miles": round(min(distance, end_distance), 2),
                        "from_name": "" if generic_end(record["sub_1"]) else place(record["sub_1"]),
                        "to_name": "" if generic_end(record["sub_2"]) else place(record["sub_2"]),
                        "named": bool(name_hit and end_distance <= NAMED_END_MILES),
                    })
    found.sort(key=lambda item: (item["miles"], -item["voltage_kv"]))
    return found


def owners_of(hits):
    grouped = {}
    for hit in hits:
        name = hit["owner"] or "NOT AVAILABLE"
        row = grouped.get(name)
        if row is None:
            row = {
                "name": name,
                "voltages_kv": [],
                "miles": hit["miles"],
                "named": hit["named"],
            }
            grouped[name] = row
        if hit["voltage_kv"] not in row["voltages_kv"]:
            row["voltages_kv"].append(hit["voltage_kv"])
        row["miles"] = min(row["miles"], hit["miles"])
        row["named"] = row["named"] or hit["named"]
    rows = list(grouped.values())
    for row in rows:
        row["voltages_kv"].sort(reverse=True)
    rows.sort(key=lambda row: (row["miles"], row["name"]))
    return rows


def status_label(value):
    token = (value or "").strip().upper()
    if token == "IN SERVICE":
        return "In service"
    if token in {"UNDER CONST", "UNDER CONSTRUCTION"}:
        return "Under construction"
    if token in {"", "NOT AVAILABLE", "NULL"}:
        return "Status not published"
    return place(token)


def type_label(value):
    token = (value or "").strip().upper()
    if token == "SUBSTATION":
        return "Substation"
    if token == "TAP":
        return "Tap"
    if token in {"", "NOT AVAILABLE"}:
        return "Substation"
    return place(token)


def source_day(value):
    try:
        millis = float(value)
    except (TypeError, ValueError):
        return ""
    if millis <= 0:
        return ""
    return datetime.fromtimestamp(millis / 1000, timezone.utc).date().isoformat()


def build():
    counties_fc = json.loads(COUNTIES.read_text(encoding="utf-8"))
    counties = [
        (feature["properties"]["name"], feature["geometry"])
        for feature in counties_fc["features"]
    ]
    county_names = {name.upper() for name, _geometry in counties}

    substations = load_or_fetch(SUBSTATION_CACHE, SUBSTATION_URL, {
        "where": "STATE = 'TX' AND (MAX_VOLT >= 69 OR MAX_VOLT < 0)",
        "geometry": BOX,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "ID,NAME,CITY,STATE,COUNTY,TYPE,STATUS,LINES,MAX_VOLT,MIN_VOLT,MAX_INFER,MIN_INFER,SOURCEDATE",
        "returnGeometry": "true",
        "outSR": "4326",
        "f": "geojson",
    })
    lines = load_or_fetch(LINE_CACHE, LINE_URL, {
        "where": "VOLTAGE >= 69 AND STATUS = 'IN SERVICE'",
        "geometry": BOX,
        "geometryType": "esriGeometryEnvelope",
        "inSR": "4326",
        "spatialRel": "esriSpatialRelIntersects",
        "outFields": "ID,OWNER,VOLTAGE,SUB_1,SUB_2,STATUS",
        "returnGeometry": "true",
        "outSR": "4326",
        "geometryPrecision": "5",
        "f": "geojson",
    })
    buckets, cell = index_lines(lines)
    print("lines indexed", sum(len(items) for items in buckets.values()))

    features = []
    skipped_voltage = 0
    for feature in substations["features"]:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") != "Point":
            continue
        lon, lat = geometry["coordinates"][:2]
        props = feature.get("properties") or {}
        county = county_of(lon, lat, counties)
        if county is None and (props.get("COUNTY") or "").upper() in county_names:
            county = place(props.get("COUNTY"))
        if county is None:
            continue
        max_kv = volts(props.get("MAX_VOLT"))
        min_kv = volts(props.get("MIN_VOLT"))
        raw_name = props.get("NAME") or ""
        hits = lines_near(lon, lat, buckets, cell, raw_name)
        if max_kv is None:
            if not hits:
                skipped_voltage += 1
                continue
            max_kv = max(hit["voltage_kv"] for hit in hits)
        if max_kv < 69:
            skipped_voltage += 1
            continue
        if min_kv is not None and min_kv > max_kv:
            min_kv, max_kv = max_kv, min_kv
        owner_rows = owners_of(hits)
        circuits = []
        seen_circuits = set()
        for hit in hits:
            if not hit["from_name"] and not hit["to_name"]:
                continue
            key = (hit["from_name"], hit["to_name"], hit["voltage_kv"], hit["owner"])
            if key in seen_circuits:
                continue
            seen_circuits.add(key)
            circuits.append({
                "owner": hit["owner"],
                "voltage_kv": hit["voltage_kv"],
                "miles": hit["miles"],
                "from_name": hit["from_name"],
                "to_name": hit["to_name"],
            })
            if len(circuits) == 3:
                break
        kind = type_label(props.get("TYPE"))
        display = ("Unnamed tap" if kind == "Tap" else "Unnamed substation") if unnamed(raw_name) else place(raw_name)
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
            "properties": {
                "id": str(props.get("ID") or ""),
                "name": display,
                "type": kind,
                "status": status_label(props.get("STATUS")),
                "city": place(props.get("CITY")),
                "county": county,
                "state": "Texas",
                "min_kv": min_kv,
                "max_kv": max_kv,
                "max_inferred": (props.get("MAX_INFER") or "").upper() == "Y" or volts(props.get("MAX_VOLT")) is None,
                "min_inferred": (props.get("MIN_INFER") or "").upper() == "Y",
                "line_count": int(props.get("LINES") or 0),
                "owners": owner_rows,
                "circuits": circuits,
                "source_date": source_day(props.get("SOURCEDATE")),
            },
        })

    features.sort(key=lambda feature: (-(feature["properties"]["max_kv"] or 0), feature["properties"]["name"]))
    OUT.write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )
    with_owner = sum(1 for feature in features if any(
        row["name"] and row["name"] != "NOT AVAILABLE" for row in feature["properties"]["owners"]
    ))
    print("points", len(features), "with a named owner", with_owner, "dropped for voltage", skipped_voltage)
    counts = {}
    for feature in features:
        for row in feature["properties"]["owners"]:
            counts[row["name"]] = counts.get(row["name"], 0) + 1
    for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
        print(f"  {count:4}  {name}")


if __name__ == "__main__":
    build()
