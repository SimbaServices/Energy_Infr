"""Local surface-ownership service for the sandbox map.

Listens on 127.0.0.1 only. The sandbox nginx site proxies /api/ to it.
Parcel shapes come from the copied mineral databases. Owner names and
mailing addresses come from the copied county appraisal rolls under
db/parcels/surface, which are opened read-only. The service makes no
outbound network request.
"""
import datetime
import json
import math
import re
import sqlite3
import struct
import threading
import time
from collections import OrderedDict
from concurrent.futures import ThreadPoolExecutor
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

HOST = "127.0.0.1"
PORT = 8766
ROOT = Path("/home/propeval/Energy_Infr/db/parcels")
SURFACE = ROOT / "surface"
MERGED = SURFACE / "surface_all.sqlite"
RADIUS_MILES = 2.0
PAGE_SIZE = 8
TAX_YEAR = datetime.date.today().year - 1
MILES_PER_DEG = 69.0
CANDIDATE_LIMIT = 20000
CACHE_LIMIT = 24
RECHECK_SECONDS = 120.0
FIELDS = (
    "prop_id",
    "county_name",
    "tax_year",
    "owner_name",
    "contact",
    "legal_desc",
    "situs",
    "source_url",
)


def haversine(lat1, lon1, lat2, lon2):
    radius = 3958.8
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * radius * math.asin(math.sqrt(a))


def point_in_ring(lon, lat, ring):
    inside = False
    j = len(ring) - 1
    for i, (x1, y1) in enumerate(ring):
        x2, y2 = ring[j]
        if ((y1 > lat) != (y2 > lat)) and (lon < (x2 - x1) * (lat - y1) / ((y2 - y1) or 1e-15) + x1):
            inside = not inside
        j = i
    return inside


def decode_wkb(blob):
    if not blob:
        return None
    data = bytes(blob)
    if len(data) < 9:
        return None
    order = "<" if data[0] == 1 else ">"
    kind = struct.unpack_from(order + "I", data, 1)[0] & 0xFF
    offset = 5

    def read_point():
        nonlocal offset
        x, y = struct.unpack_from(order + "dd", data, offset)
        offset += 16
        return [x, y]

    def read_ring():
        nonlocal offset
        count = struct.unpack_from(order + "I", data, offset)[0]
        offset += 4
        return [read_point() for _ in range(count)]

    def read_rings(count):
        return [read_ring() for _ in range(count)]

    if kind == 3:
        rings = struct.unpack_from(order + "I", data, offset)[0]
        offset += 4
        return {"type": "Polygon", "coordinates": read_rings(rings)}
    if kind == 6:
        parts = struct.unpack_from(order + "I", data, offset)[0]
        offset += 4
        polygons = []
        for _ in range(parts):
            order = "<" if data[offset] == 1 else ">"
            part_kind = struct.unpack_from(order + "I", data, offset + 1)[0] & 0xFF
            offset += 5
            if part_kind != 3:
                return None
            rings = struct.unpack_from(order + "I", data, offset)[0]
            offset += 4
            polygons.append(read_rings(rings))
        return {"type": "MultiPolygon", "coordinates": polygons}
    return None


def contains(geometry, lon, lat):
    if not geometry:
        return False
    if geometry["type"] == "Polygon":
        polygons = [geometry["coordinates"]]
    elif geometry["type"] == "MultiPolygon":
        polygons = geometry["coordinates"]
    else:
        return False
    for rings in polygons:
        if not rings:
            continue
        if point_in_ring(lon, lat, rings[0]):
            if all(not point_in_ring(lon, lat, hole) for hole in rings[1:]):
                return True
    return False


def open_ro(path):
    """A read-only handle, so a pin lookup can never write or lock a roll."""
    path = Path(path)
    if not path.exists():
        return None
    try:
        return sqlite3.connect(f"file:{path}?mode=ro", uri=True)
    except sqlite3.Error:
        return None


def connect(name):
    return open_ro(ROOT / name)


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def normal(value):
    return clean(value).upper()


def box(lat, lon):
    dlat = RADIUS_MILES / MILES_PER_DEG
    dlon = RADIUS_MILES / (MILES_PER_DEG * max(0.2, math.cos(math.radians(lat))))
    return lon - dlon, lat - dlat, lon + dlon, lat + dlat


def rtree_ids(conn, table, west, south, east, north):
    try:
        rows = conn.execute(
            f"""
            SELECT id FROM {table}
            WHERE minx <= ? AND maxx >= ? AND miny <= ? AND maxy >= ?
            """,
            (east, west, north, south),
        ).fetchall()
        return [row[0] for row in rows]
    except sqlite3.Error:
        return None


def texas_lands(lat, lon):
    conn = connect("minerals.db")
    if conn is None:
        return []
    west, south, east, north = box(lat, lon)
    ids = rtree_ids(conn, "surveys_tx_rtree", west, south, east, north)
    if ids is None:
        query = """
            SELECT id, survey_name, abstract_label, abstract_number, block_number, survey_number, geom, minx, miny, maxx, maxy
            FROM surveys_tx
            WHERE minx <= ? AND maxx >= ? AND miny <= ? AND maxy >= ?
        """
        params = (east, west, north, south)
        rows = conn.execute(query, params).fetchall()
    else:
        if not ids:
            conn.close()
            return []
        marks = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"""
            SELECT id, survey_name, abstract_label, abstract_number, block_number, survey_number, geom, minx, miny, maxx, maxy
            FROM surveys_tx WHERE id IN ({marks})
            """,
            ids,
        ).fetchall()
    lands = []
    for survey_id, name, abstract, abstract_number, block, section, geom, minx, miny, maxx, maxy in rows:
        geometry = decode_wkb(geom)
        cy = ((miny or 0) + (maxy or 0)) / 2
        cx = ((minx or 0) + (maxx or 0)) / 2
        inside = contains(geometry, lon, lat)
        distance = 0.0 if inside else haversine(lat, lon, cy, cx)
        if not inside and distance > RADIUS_MILES:
            continue
        lands.append({
            "id": f"tx-survey-{survey_id}",
            "state": "TX",
            "survey_id": survey_id,
            "county_code": "",
            "county": "",
            "account": "",
            "geo_id": "",
            "label": " ".join(part for part in (abstract, name) if part),
            "block": block or "",
            "section": section or "",
            "survey": name or "",
            "abstract": abstract or "",
            "abstract_number": abstract_number or "",
            "distance": distance,
            "inside": inside,
            "geometry": geometry,
        })
    conn.close()
    return lands


def other_lands(lat, lon, filename, table, state):
    conn = connect(filename)
    if conn is None:
        return []
    west, south, east, north = box(lat, lon)
    rtree = f"{table}_rtree"
    ids = rtree_ids(conn, rtree, west, south, east, north)
    columns = "id, county_code, county_name, prop_id, geom, cx, cy"
    extra = ", upc" if state == "NM" else ", geo_id"
    if ids is None:
        rows = conn.execute(
            f"""
            SELECT {columns}{extra} FROM {table}
            WHERE minx <= ? AND maxx >= ? AND miny <= ? AND maxy >= ?
            """,
            (east, west, north, south),
        ).fetchall()
    elif not ids:
        conn.close()
        return []
    else:
        marks = ",".join("?" for _ in ids)
        rows = conn.execute(
            f"SELECT {columns}{extra} FROM {table} WHERE id IN ({marks})",
            ids,
        ).fetchall()
    lands = []
    for row in rows:
        parcel_id, code, county, prop_id, geom, cx, cy, alt = row
        if cx is None or cy is None:
            continue
        distance = haversine(lat, lon, cy, cx)
        geometry = decode_wkb(geom)
        inside = contains(geometry, lon, lat)
        if not inside and distance > RADIUS_MILES:
            continue
        lands.append({
            "id": f"{state.lower()}-{parcel_id}",
            "state": state,
            "county_code": code or "",
            "county": (county or "").upper(),
            "account": prop_id or alt or "",
            "geo_id": alt or "",
            "label": prop_id or "",
            "block": "",
            "section": "",
            "survey": "",
            "abstract": "",
            "abstract_number": "",
            "distance": 0.0 if inside else distance,
            "inside": inside,
            "geometry": geometry,
        })
    conn.close()
    return lands


def nearby(lat, lon):
    lands = texas_lands(lat, lon)
    lands.extend(other_lands(lat, lon, "ks_minerals.db", "parcels_ks", "KS"))
    lands.extend(other_lands(lat, lon, "nm_minerals.db", "parcels_nm", "NM"))
    lands.sort(key=lambda item: (not item["inside"], item["distance"], item["id"]))
    return lands


COUNTY_NAMES = {}
COUNTY_LOCK = threading.Lock()


def county_code_from_abstract(number, label):
    digits = re.sub(r"\D", "", str(number or ""))
    match = re.search(r"A-\s*0*(\d+)", str(label or ""), re.I)
    abstract = match.group(1) if match else ""
    if abstract and digits.endswith(abstract) and len(digits) > len(abstract):
        return digits[: -len(abstract)]
    return ""


def county_name_for(code):
    code = str(code or "").strip()
    if not code:
        return ""
    with COUNTY_LOCK:
        cached = COUNTY_NAMES.get(code)
    if cached is not None:
        return cached
    name = ""
    conn = connect("minerals.db")
    if conn is not None:
        row = conn.execute(
            """
            SELECT county_name FROM parcels_tx
            WHERE county_code = ? AND county_name IS NOT NULL AND trim(county_name) != ''
            LIMIT 1
            """,
            (code,),
        ).fetchone()
        conn.close()
        if row and row[0]:
            name = str(row[0]).strip().upper()
    with COUNTY_LOCK:
        COUNTY_NAMES[code] = name
    return name


def fill_county(land):
    if land.get("state") != "TX":
        return land
    if not land.get("county_code"):
        code = county_code_from_abstract(land.get("abstract_number"), land.get("abstract"))
        if code and county_name_for(code):
            land["county_code"] = code
    if not land.get("county"):
        name = county_name_for(land.get("county_code"))
        if name:
            land["county"] = name
    return land


def attach_account(land):
    if land["state"] != "TX" or land.get("account"):
        return land
    conn = connect("minerals.db")
    if conn is None:
        return land
    account = conn.execute(
        """
        SELECT county_code, county_name, prop_id, geo_id
        FROM parcels_tx
        WHERE survey_id = ? AND prop_id IS NOT NULL AND trim(prop_id) != ''
        LIMIT 1
        """,
        (land["survey_id"],),
    ).fetchone()
    conn.close()
    if account is None:
        return land
    land["county_code"] = account[0] or ""
    land["county"] = (account[1] or "").upper()
    land["account"] = account[2] or ""
    land["geo_id"] = account[3] or ""
    return land


MERGED_READY = None
MERGED_CHECKED = 0.0
MERGED_LOCK = threading.Lock()


def merged_ready():
    """True once the merge job has written surface_parcels and stamped meta."""
    global MERGED_READY, MERGED_CHECKED
    now = time.monotonic()
    with MERGED_LOCK:
        if MERGED_READY or (MERGED_READY is False and now - MERGED_CHECKED < RECHECK_SECONDS):
            return bool(MERGED_READY)
    ready = False
    conn = open_ro(MERGED)
    if conn is not None:
        try:
            tables = {row[0] for row in conn.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
            if {"surface_parcels", "meta"} <= tables:
                stamp = conn.execute("SELECT value FROM meta WHERE key = 'merged_at'").fetchone()
                ready = bool(stamp and clean(stamp[0]))
        except sqlite3.Error:
            ready = False
        finally:
            conn.close()
    with MERGED_LOCK:
        MERGED_READY = ready
        MERGED_CHECKED = now
    return ready


def code_variants(code):
    code = clean(code)
    if not code:
        return []
    found = [code]
    if code.isdigit():
        for other in (code.zfill(3), code.lstrip("0") or code):
            if other not in found:
                found.append(other)
    return found


def sources_for(state, codes):
    """The merged roll first, then the per-county file it was built from."""
    found = []
    if merged_ready():
        found.append(("merged", MERGED))
    for code in codes:
        path = SURFACE / f"{state.lower()}-{code}.sqlite"
        if path.exists():
            found.append(("county", path))
    return found


def read_rows(kind, path, state, codes, where, params):
    conn = open_ro(path)
    if conn is None:
        return []
    columns = ", ".join(FIELDS)
    if kind == "merged":
        marks = ",".join("?" for _ in codes)
        clause = f"state = ? AND county_code IN ({marks})"
        args = [state] + list(codes)
    else:
        clause = "1 = 1"
        args = []
    if where:
        clause += f" AND {where}"
        args.extend(params)
    try:
        rows = conn.execute(
            f"SELECT {columns} FROM surface_parcels WHERE {clause} LIMIT {CANDIDATE_LIMIT}",
            args,
        ).fetchall()
    except sqlite3.Error:
        return []
    finally:
        conn.close()
    return [dict(zip(FIELDS, row)) for row in rows]


def block_token(block):
    text = normal(block)
    match = re.fullmatch(r"(\d+)\s+([A-Z0-9-]+)", text)
    if match:
        return f"{match.group(1)}-{match.group(2)}"
    return text.replace(" ", "-")


def section_in(legal, section):
    token = normal(section)
    if not token:
        return False
    pattern = r"\b(?:SEC|SECT|SECTION)S?\.?\s*:?\s*0*" + re.escape(token) + r"(?![0-9A-Z])"
    return re.search(pattern, legal) is not None


def block_in(legal, token):
    parts = [re.escape(part) for part in re.split(r"[\s-]+", normal(token)) if part]
    if not parts:
        return False
    body = r"[\s-]+".join(parts)
    pattern = r"\b(?:BLK|BLOCK)S?\.?\s*:?\s*" + body + r"(?![0-9A-Z-])"
    return re.search(pattern, legal) is not None


def abstract_in(legal, abstract):
    digits = re.sub(r"\D", "", normal(abstract))
    if not digits:
        return False
    pattern = (
        r"\b(?:ABSTRACT|ABST|ABS)\.?\s*:?\s*0*" + digits + r"(?![0-9])"
        r"|\bA-\s*0*" + digits + r"(?![0-9])"
    )
    return re.search(pattern, legal) is not None


ABSTRACTS = re.compile(r"\b(?:ABSTRACT|ABST|ABS)\.?\s*:?\s*((?:0*\d+)(?:\s*(?:&|AND|,)\s*0*\d+)*)")


def abstract_conflict(legal, abstract):
    """The roll states an abstract for this tract and it is not ours."""
    digits = re.sub(r"\D", "", normal(abstract)).lstrip("0")
    if not digits:
        return False
    stated = set()
    for group in ABSTRACTS.findall(legal):
        stated.update(part.lstrip("0") for part in re.split(r"\D+", group) if part)
    if not stated:
        return False
    return digits not in stated


def legal_score(legal, land):
    """How strongly a stored legal description names this survey's tract.

    The count of agreeing identifiers, or zero when the row is a
    different tract. A section on its own is never enough, because the
    same section number repeats across blocks.
    """
    text = normal(legal)
    if not text:
        return 0
    if abstract_conflict(text, land.get("abstract")):
        return 0
    marks = 0
    if block_in(text, land.get("block")):
        marks += 1
    if abstract_in(text, land.get("abstract")):
        marks += 1
    section = clean(land.get("section"))
    if not section:
        return marks if marks > 1 else 0
    if not marks or not section_in(text, section):
        return 0
    return marks + 1


FRACTION = re.compile(r"\bUND\b|\bINT\b|\d\s*/\s*\d|%")
NOT_LAND = re.compile(r"IMPROVEMENT ONLY|MOBILE HOME|MANUFACTUR|\bMH\b")


def rank(row):
    """Prefer this tax year, whole tracts, and the plainest description."""
    legal = normal(row.get("legal_desc"))
    try:
        year = int(row.get("tax_year") or 0)
    except (TypeError, ValueError):
        year = 0
    return (
        0 if year == TAX_YEAR else 1,
        -year,
        1 if NOT_LAND.search(legal) else 0,
        1 if FRACTION.search(legal) else 0,
        len(legal),
        clean(row.get("prop_id")),
    )


def account_terms(account):
    account = clean(account)
    if not account:
        return []
    found = [account]
    if account.isdigit():
        bare = account.lstrip("0")
        if bare and bare not in found:
            found.append(bare)
    return found


def like_terms(land):
    """One selective literal, in the spellings the rolls actually use."""
    block = block_token(land.get("block"))
    section = clean(land.get("section"))
    digits = re.sub(r"\D", "", normal(land.get("abstract")))
    if len(block) >= 2:
        spaced = block.replace("-", " ")
        return [block, spaced] if spaced != block else [block]
    if len(section) >= 2:
        return [section]
    if digits:
        return [digits]
    return [block] if block else []


SURFACE_CACHE = OrderedDict()
SURFACE_CACHE_LOCK = threading.Lock()


def candidates(state, codes, terms):
    if not terms:
        return []
    key = (state, tuple(codes), tuple(terms))
    with SURFACE_CACHE_LOCK:
        found = SURFACE_CACHE.get(key)
        if found is not None:
            SURFACE_CACHE.move_to_end(key)
            return found
    where = " OR ".join("legal_desc LIKE ?" for _ in terms)
    params = [f"%{term}%" for term in terms]
    rows = []
    for kind, path in sources_for(state, codes):
        rows = read_rows(kind, path, state, codes, f"({where})", params)
        if rows:
            break
    with SURFACE_CACHE_LOCK:
        SURFACE_CACHE[key] = rows
        while len(SURFACE_CACHE) > CACHE_LIMIT:
            SURFACE_CACHE.popitem(last=False)
    return rows


def by_account(state, codes, account):
    terms = account_terms(account)
    if not terms:
        return None
    marks = ",".join("?" for _ in terms)
    for kind, path in sources_for(state, codes):
        rows = read_rows(kind, path, state, codes, f"prop_id IN ({marks})", terms)
        if rows:
            rows.sort(key=rank)
            return rows[0]
    return None


def surface_row(land):
    """The stored appraisal-roll row for one nearby parcel, or nothing."""
    state = clean(land.get("state"))
    codes = code_variants(land.get("county_code"))
    if not state or not codes:
        return None, ""
    found = by_account(state, codes, land.get("account"))
    if found:
        return found, "account"
    matched = []
    for row in candidates(state, codes, like_terms(land)):
        score = legal_score(row.get("legal_desc"), land)
        if score:
            matched.append(((-score,) + rank(row), row))
    if not matched:
        return None, ""
    matched.sort(key=lambda item: item[0])
    return matched[0][1], "legal"


def enrich(land):
    land = fill_county(attach_account(land))
    row, matched_on = surface_row(land)
    owner = clean(row.get("owner_name")) if row else ""
    contact = clean(row.get("contact")) if row else ""
    county = land["county"].title() if land["county"] else ""
    if not county and row:
        county = clean(row.get("county_name")).title()
    try:
        year = int(row["tax_year"]) if row and row.get("tax_year") else None
    except (TypeError, ValueError):
        year = None
    return {
        "id": land["id"],
        "state": land["state"],
        "county": county,
        "account": land["account"],
        "owner": owner,
        "contact": contact,
        "inside": land["inside"],
        "geometry": land["geometry"],
        "tax_year": year if owner else None,
        "source_url": clean(row.get("source_url")) if owner else "",
        "legal": clean(row.get("legal_desc")) if owner else "",
        "matched_on": matched_on if owner else "",
    }


class Handler(BaseHTTPRequestHandler):
    def do_POST(self):
        if self.path.split("?", 1)[0] != "/api/surface-owners":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length") or 0)
        try:
            payload = json.loads(self.rfile.read(length) or b"{}")
            lat = float(payload["lat"])
            lon = float(payload["lon"])
            page = max(0, int(payload.get("page") or 0))
        except (KeyError, TypeError, ValueError, json.JSONDecodeError):
            self.respond(400, {"error": "A latitude and longitude are required."})
            return
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            self.respond(400, {"error": "That pin is outside the map."})
            return
        lands = nearby(lat, lon)
        start = page * PAGE_SIZE
        chosen = lands[start:start + PAGE_SIZE]
        with ThreadPoolExecutor(max_workers=4) as pool:
            rows = list(pool.map(enrich, chosen))
        pages = max(1, math.ceil(len(lands) / PAGE_SIZE)) if lands else 1
        self.respond(200, {
            "page": page,
            "pages": pages,
            "total": len(lands),
            "radius_miles": RADIUS_MILES,
            "rows": rows,
        })

    def respond(self, status, payload):
        body = json.dumps(payload).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        print(fmt % args)


if __name__ == "__main__":
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    source = "merged roll" if merged_ready() else "per-county rolls"
    print(f"surface owners on {HOST}:{PORT}, tax year {TAX_YEAR}, reading {source}", flush=True)
    server.serve_forever()
