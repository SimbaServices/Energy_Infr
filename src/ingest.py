"""Load public EIA and grid files into db/us_pipelines.sqlite.

Re-running rebuilds the database from the files in data/raw.
"""

from __future__ import annotations

import hashlib
import json
import math
import sqlite3
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path

import openpyxl
import xlrd

ROOT = Path(__file__).resolve().parents[1]
DB_PATH = ROOT / "db" / "us_pipelines.sqlite"
SCHEMA = ROOT / "db" / "schema.sql"
RAW = ROOT / "data" / "raw"

# EIA's typical dry-gas heat content, used only to show Henry Hub in $/Mcf
# beside citygate prices that EIA already publishes in $/Mcf.
HEAT_MMBTU_PER_MCF = 1.037
RETRIEVED = "2026-09-26"

ABBR = {
    "AL": "Alabama",
    "AK": "Alaska",
    "AZ": "Arizona",
    "AR": "Arkansas",
    "CA": "California",
    "CO": "Colorado",
    "CT": "Connecticut",
    "DE": "Delaware",
    "DC": "District of Columbia",
    "FL": "Florida",
    "GA": "Georgia",
    "HI": "Hawaii",
    "ID": "Idaho",
    "IL": "Illinois",
    "IN": "Indiana",
    "IA": "Iowa",
    "KS": "Kansas",
    "KY": "Kentucky",
    "LA": "Louisiana",
    "ME": "Maine",
    "MD": "Maryland",
    "MA": "Massachusetts",
    "MI": "Michigan",
    "MN": "Minnesota",
    "MS": "Mississippi",
    "MO": "Missouri",
    "MT": "Montana",
    "NE": "Nebraska",
    "NV": "Nevada",
    "NH": "New Hampshire",
    "NJ": "New Jersey",
    "NM": "New Mexico",
    "NY": "New York",
    "NC": "North Carolina",
    "ND": "North Dakota",
    "OH": "Ohio",
    "OK": "Oklahoma",
    "OR": "Oregon",
    "PA": "Pennsylvania",
    "RI": "Rhode Island",
    "SC": "South Carolina",
    "SD": "South Dakota",
    "TN": "Tennessee",
    "TX": "Texas",
    "UT": "Utah",
    "VT": "Vermont",
    "VA": "Virginia",
    "WA": "Washington",
    "WV": "West Virginia",
    "WI": "Wisconsin",
    "WY": "Wyoming",
}
NAME_TO_ABBR = {name: abbr for abbr, name in ABBR.items()}

FIRM_STATUS = {"construction", "approved", "part completed"}
OPEN_STATUS = FIRM_STATUS | {"applied", "pre-applied", "announced", "proposed"}

# Representative anchors so DPR regions can be drawn. These are not wellheads.
BASIN_ANCHORS = {
    "Anadarko Region": (35.55, -98.35, "OK,TX", "Anchor placed in western Oklahoma."),
    "Appalachia Region": (39.85, -80.35, "PA,OH,WV", "Anchor placed in southwestern Pennsylvania."),
    "Bakken Region": (48.15, -103.05, "ND,MT", "Anchor placed in western North Dakota."),
    "Eagle Ford Region": (28.40, -98.55, "TX", "Anchor placed in south Texas."),
    "Haynesville Region": (32.40, -93.85, "LA,TX", "Anchor placed near the Louisiana-Texas border."),
    "Niobrara Region": (40.65, -104.55, "CO,WY", "Anchor placed in northeastern Colorado."),
    "Permian Region": (31.85, -102.10, "TX,NM", "Anchor placed in the Midland Basin."),
}

BASIN_KEYWORDS = {
    "Permian Region": ("permian", "waha", "matterhorn", "blackcomb", "whistler"),
    "Haynesville Region": ("haynesville",),
    "Appalachia Region": ("appalachia", "mountain valley"),
    "Bakken Region": ("bakken",),
    "Eagle Ford Region": ("eagle ford",),
    "Anadarko Region": ("anadarko",),
    "Niobrara Region": ("niobrara", "piceance"),
}

BALANCE_METHOD = (
    "Takeaway gap = (dry production − in-state consumption) − interstate "
    "border outflow capacity, all in MMcf/d. Annual MMcf is divided by 365.25. "
    "Planned cases add EIA project capacity once, onto the project's beginning "
    "state. Firm projects are Construction, Approved, and Part Completed. "
    "The open case also adds Applied, Pre-applied, Announced, and Proposed. "
    "On Hold and Completed are excluded from both cases. LNG exports and "
    "intrastate pipelines are not part of the border-capacity total."
)


def haversine_miles(lon1: float, lat1: float, lon2: float, lat2: float) -> float:
    radius = 3958.7613
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlmb = math.radians(lon2 - lon1)
    a = math.sin(dphi / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dlmb / 2) ** 2
    return 2 * radius * math.asin(min(1.0, math.sqrt(a)))


def geometry_miles(geometry: dict) -> float:
    if geometry["type"] == "LineString":
        parts = [geometry["coordinates"]]
    else:
        parts = geometry["coordinates"]
    total = 0.0
    for part in parts:
        for (lon1, lat1), (lon2, lat2) in zip(part, part[1:]):
            total += haversine_miles(lon1, lat1, lon2, lat2)
    return total


def geometry_midpoint(geometry: dict) -> tuple[float, float] | None:
    if geometry["type"] == "LineString":
        coords = geometry["coordinates"]
    elif geometry["coordinates"]:
        coords = max(geometry["coordinates"], key=len)
    else:
        return None
    if not coords:
        return None
    lon, lat = coords[len(coords) // 2]
    return lat, lon


def ring_centroid(ring: list) -> tuple[float, float]:
    lon = sum(point[0] for point in ring) / len(ring)
    lat = sum(point[1] for point in ring) / len(ring)
    return lat, lon


def geometry_centroid(geometry: dict) -> tuple[float, float] | None:
    if geometry["type"] == "Polygon":
        return ring_centroid(geometry["coordinates"][0])
    if geometry["type"] == "MultiPolygon" and geometry["coordinates"]:
        ring = max((poly[0] for poly in geometry["coordinates"]), key=len)
        return ring_centroid(ring)
    return None


def as_float(value) -> float | None:
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        if isinstance(value, float) and math.isnan(value):
            return None
        return float(value)
    text = str(value).strip().replace(",", "")
    if not text or text.lower() in {"--", "na", "n/a", "w", "*"}:
        return None
    if "-" in text[1:]:
        parts = [part.strip() for part in text.split("-") if part.strip()]
        try:
            nums = [float(part) for part in parts]
        except ValueError:
            return None
        return sum(nums) / len(nums) if nums else None
    try:
        return float(text)
    except ValueError:
        return None


def excel_year(book: xlrd.Book, value) -> int | None:
    if value == "" or value is None:
        return None
    if isinstance(value, str):
        return int(value[:4]) if value[:4].isdigit() else None
    try:
        parsed = xlrd.xldate_as_datetime(value, book.datemode)
    except Exception:
        return None
    return parsed.year


def connect() -> sqlite3.Connection:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.executescript(SCHEMA.read_text(encoding="utf-8"))
    conn.execute("PRAGMA journal_mode = WAL")
    conn.execute("PRAGMA synchronous = OFF")
    return conn


def add_source(conn, name, url, vintage, notes, license_text="U.S. government work, public domain") -> int:
    cur = conn.execute(
        """
        INSERT INTO sources (name, url, retrieved_on, vintage, license, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (name, url, RETRIEVED, vintage, license_text, notes),
    )
    return int(cur.lastrowid)


def read_eia_series(path: Path, label_marker: str) -> dict[str, list[tuple[int, float]]]:
    """Return {series name: [(year, value), ...]} for an EIA .xls extract."""
    book = xlrd.open_workbook(path)
    found: dict[str, list[tuple[int, float]]] = {}
    for sheet in book.sheets():
        header_row = None
        for row_idx in range(min(8, sheet.nrows)):
            if sheet.cell_value(row_idx, 0) == "Date":
                header_row = row_idx
                break
        if header_row is None:
            continue
        for col in range(1, sheet.ncols):
            label = str(sheet.cell_value(header_row, col) or "")
            if label_marker not in label:
                continue
            name = label.split(label_marker)[0].strip(" -")
            points = []
            for row_idx in range(header_row + 1, sheet.nrows):
                value = as_float(sheet.cell_value(row_idx, col))
                year = excel_year(book, sheet.cell_value(row_idx, 0))
                if value is None or year is None:
                    continue
                points.append((year, value))
            if points:
                found[name] = points
    return found


def latest(points: list[tuple[int, float]]) -> tuple[int, float]:
    return max(points, key=lambda item: item[0])


def value_in_year(points: list[tuple[int, float]], year: int) -> float | None:
    for point_year, value in points:
        if point_year == year:
            return value
    return None


def load_areas_and_volumes(conn) -> dict[str, int]:
    production_source = add_source(
        conn,
        "EIA dry natural gas production",
        "https://www.eia.gov/dnav/ng/ng_prod_sum_a_EPG0_FPD_mmcf_a.htm",
        "Annual series, Data 1 latest year 2025 and Data 2 latest year 2024, release noted on the workbook as 2026-08-31",
        "State and offshore dry production in MMcf. Onshore and state-offshore splits are omitted so state totals are not double counted.",
    )
    consumption_source = add_source(
        conn,
        "EIA natural gas total consumption",
        "https://www.eia.gov/dnav/ng/ng_cons_sum_a_EPG0_VC0_mmcf_a.htm",
        "Annual series through 2025",
        "Total consumption includes end use and lease, plant, and pipeline fuel. It does not include LNG or pipeline exports.",
    )
    dry = read_eia_series(RAW / "production" / "dry_production_mmcf_annual.xls", "Dry Natural Gas Production")
    consumption = read_eia_series(
        RAW / "production" / "consumption_mmcf_annual.xls",
        "Natural Gas Total Consumption",
    )
    if "U.S." not in dry and "U.S" not in "".join(dry):
        # The national series is labeled "U.S."
        pass
    if not dry:
        raise SystemExit("No dry production series were read from the EIA workbook.")

    ids: dict[str, int] = {}

    def area_id(name: str, area_type: str, abbr: str | None = None) -> int:
        if name in ids:
            return ids[name]
        cur = conn.execute(
            "INSERT INTO areas (area_type, name, abbr) VALUES (?, ?, ?)",
            (area_type, name, abbr),
        )
        ids[name] = int(cur.lastrowid)
        return ids[name]

    def classify(name: str) -> tuple[str, str | None] | None:
        if name in {"U.S.", "US", "United States"}:
            return "national", None
        if name in NAME_TO_ABBR:
            return "state", NAME_TO_ABBR[name]
        if "Federal Offshore" in name or name.startswith("Gulf"):
            return "offshore", None
        if name == "Other States":
            return "other", None
        if "--" in name or "Onshore" in name or "Offshore" in name:
            return None
        return "other", None

    for name, points in dry.items():
        kind = classify(name)
        if kind is None:
            continue
        area_type, abbr = kind
        aid = area_id(name, area_type, abbr)
        conn.executemany(
            """
            INSERT OR REPLACE INTO volumes (area_id, source_id, product, period, volume_mmcf)
            VALUES (?, ?, 'dry_production', ?, ?)
            """,
            [(aid, production_source, str(year), value) for year, value in points],
        )

    for name, points in consumption.items():
        if name in {"U.S.", "US", "United States"}:
            aid = area_id(name, "national", None)
        elif name in NAME_TO_ABBR:
            aid = area_id(name, "state", NAME_TO_ABBR[name])
        else:
            continue
        conn.executemany(
            """
            INSERT OR REPLACE INTO volumes (area_id, source_id, product, period, volume_mmcf)
            VALUES (?, ?, 'consumption', ?, ?)
            """,
            [(aid, consumption_source, str(year), value) for year, value in points],
        )
    return ids


def attach_state_shapes(conn, ids: dict[str, int]) -> dict[str, tuple[float, float]]:
    collection = json.loads((RAW / "geo" / "us-states.json").read_text(encoding="utf-8"))
    centroids = {}
    for feature in collection["features"]:
        name = feature["properties"].get("name")
        centroid = geometry_centroid(feature["geometry"])
        if not name or centroid is None:
            continue
        lat, lon = centroid
        centroids[name] = (lat, lon)
        if name not in ids and name in NAME_TO_ABBR:
            cur = conn.execute(
                "INSERT INTO areas (area_type, name, abbr, lat, lon) VALUES ('state', ?, ?, ?, ?)",
                (name, NAME_TO_ABBR[name], lat, lon),
            )
            ids[name] = int(cur.lastrowid)
        elif name in ids:
            conn.execute("UPDATE areas SET lat = ?, lon = ? WHERE id = ?", (lat, lon, ids[name]))
    missing = [
        row["name"]
        for row in conn.execute("SELECT name FROM areas WHERE area_type = 'state' AND lat IS NULL")
    ]
    if missing:
        print("states without a map shape:", ", ".join(missing))
    return centroids


def load_capacity(conn, ids: dict[str, int]) -> None:
    source = add_source(
        conn,
        "EIA state-to-state natural gas pipeline capacity",
        "https://www.eia.gov/naturalgas/pipelines/EIA-StatetoStateCapacity.xlsx",
        "Workbook contents list an update date of 2026-01-31; flow year used here is 2025",
        "Border capacity is nameplate MMcf/d, not measured flow. State totals come from the Outflow By State total rows.",
    )
    workbook = openpyxl.load_workbook(
        RAW / "projects" / "EIA-StatetoStateCapacity.xlsx",
        read_only=True,
        data_only=True,
    )
    sheet = workbook["Outflow By State"]
    rows = sheet.iter_rows(values_only=True)
    header = None
    year_columns = {}
    current_from = None
    pair_rows = []
    for row in rows:
        cells = list(row)
        if header is None:
            if cells and cells[0] == "State From":
                header = cells
                for index, cell in enumerate(cells):
                    if isinstance(cell, int):
                        year_columns[cell] = index
            continue
        state_from = cells[0] or current_from
        if cells[0]:
            current_from = cells[0]
        state_to = cells[1]
        if not state_from:
            continue
        label = str(state_from).strip()
        if label.endswith(" Total"):
            state_name = label[: -len(" Total")].strip()
            if 2025 in year_columns and state_name in ids:
                capacity = as_float(cells[year_columns[2025]])
                if capacity is not None:
                    conn.execute(
                        """
                        INSERT OR REPLACE INTO state_outflow (area_id, source_id, year, capacity_mmcfd)
                        VALUES (?, ?, 2025, ?)
                        """,
                        (ids[state_name], source, capacity),
                    )
            continue
        if not state_to or 2025 not in year_columns:
            continue
        capacity = as_float(cells[year_columns[2025]])
        if capacity is None:
            continue
        pair_rows.append((str(state_from).strip(), str(state_to).strip(), capacity))
    conn.executemany(
        """
        INSERT INTO state_flows (source_id, state_from, state_to, year, capacity_mmcfd)
        VALUES (?, ?, ?, 2025, ?)
        """,
        [(source, origin, destination, capacity) for origin, destination, capacity in pair_rows],
    )

    detail = workbook["Pipeline State2State Capacity"]
    detail_rows = detail.iter_rows(values_only=True)
    detail_header = None
    crossing_batch = []
    for row in detail_rows:
        cells = list(row)
        if detail_header is None:
            if cells and cells[0] == "year":
                detail_header = [str(cell).strip() if cell else "" for cell in cells]
            continue
        record = {detail_header[index]: cells[index] if index < len(cells) else None for index in range(len(detail_header))}
        if as_float(record.get("year")) != 2025:
            continue
        crossing_batch.append(
            (
                source,
                record.get("Pipeline"),
                record.get("State From"),
                record.get("County From"),
                record.get("State To"),
                record.get("County To"),
                2025,
                as_float(record.get("Capacity (mmcfd)")),
            )
        )
    conn.executemany(
        """
        INSERT INTO border_crossings (
            source_id, pipeline, state_from, county_from, state_to, county_to, year, capacity_mmcfd
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        crossing_batch,
    )
    workbook.close()
    print(f"border crossings in 2025: {len(crossing_batch)}")


def load_projects(conn, centroids: dict[str, tuple[float, float]]) -> None:
    source = add_source(
        conn,
        "EIA natural gas pipeline projects",
        "https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects.xlsx",
        "Current sheet covers projects tracked from 2025; rows in that sheet were last updated through July 2026. Historical sheet supplies 2024 completions.",
        "Additional capacity is the project's reported MMcf/d. A range, when published, is stored as the midpoint and noted.",
    )
    workbook = openpyxl.load_workbook(
        RAW / "projects" / "EIA-NaturalGasPipelineProjects.xlsx",
        read_only=True,
        data_only=True,
    )

    def consume(sheet_name: str, minimum_year: int | None) -> None:
        sheet = workbook[sheet_name]
        rows = sheet.iter_rows(values_only=True)
        next(rows)
        headers = [str(cell).strip() if cell else "" for cell in next(rows)]
        for raw in rows:
            record = {headers[index]: raw[index] if index < len(raw) else None for index in range(len(headers))}
            name = record.get("Project Name")
            if not name:
                continue
            year = record.get("Year In Service Date")
            year_num = int(year) if isinstance(year, (int, float)) and year else None
            if minimum_year is not None and (year_num is None or year_num < minimum_year):
                continue
            status = str(record.get("Status") or "").strip()
            begin = str(record.get("Beg_State") or "").strip() or None
            lat = lon = None
            if begin and ABBR.get(begin) in centroids:
                lat, lon = centroids[ABBR[begin]]
                digest = int(hashlib.md5(str(name).encode()).hexdigest()[:6], 16)
                lat += ((digest % 100) - 50) / 50 * 0.45
                lon += (((digest // 100) % 100) - 50) / 50 * 0.45
            capacity_raw = record.get("Additional Capacity (MMcf/d)")
            capacity_note = None
            if isinstance(capacity_raw, str) and "-" in capacity_raw[1:]:
                capacity_note = f"Workbook published a range ({capacity_raw}); the stored value is the midpoint."
            completed = record.get("Completed Date")
            if isinstance(completed, datetime):
                completed = completed.date().isoformat()
            elif completed:
                completed = str(completed)
            else:
                completed = None
            key = status.lower()
            conn.execute(
                """
                INSERT INTO projects (
                    source_id, name, operator, project_type, status, in_service_year,
                    completed_on, states, begin_state, end_state, region, capacity_mmcfd,
                    capacity_note, miles, diameter_in, cost_millions, demand_served,
                    docket, notes, lat, lon, firm, open
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    source,
                    str(name).strip(),
                    record.get("Pipeline Operator Name"),
                    record.get("Project Type"),
                    status,
                    year_num,
                    completed,
                    record.get("State(s)"),
                    begin,
                    record.get("End_State"),
                    record.get("Region(s)"),
                    as_float(capacity_raw),
                    capacity_note,
                    as_float(record.get("Miles")),
                    as_float(record.get("Pipeline Diameter (Inches)")),
                    None if record.get("Cost (millions)") is None else str(record.get("Cost (millions)")),
                    record.get("Demand Served"),
                    record.get("Docket/Permit  Number"),
                    record.get("Notes"),
                    lat,
                    lon,
                    1 if key in FIRM_STATUS else 0,
                    1 if key in OPEN_STATUS else 0,
                ),
            )

    consume("Natural Gas Pipeline Projects", None)
    consume("Historical Projects (1996-2024)", 2024)
    workbook.close()


def load_prices(conn, ids: dict[str, int]) -> tuple[float | None, str | None]:
    henry_source = add_source(
        conn,
        "EIA Henry Hub natural gas spot price",
        "https://www.eia.gov/dnav/ng/hist/rngwhhdM.htm",
        "Monthly series through the latest month in the workbook (August 2026 at retrieval)",
        "Dollars per MMBtu. The $/Mcf column multiplies by 1.037 MMBtu per Mcf.",
    )
    city_source = add_source(
        conn,
        "EIA natural gas citygate price",
        "https://www.eia.gov/dnav/ng/ng_pri_sum_a_EPG0_PG1_DMCF_a.htm",
        "Annual citygate price through 2025",
        "Already in dollars per thousand cubic feet, treated here as $/Mcf.",
    )
    book = xlrd.open_workbook(RAW / "prices" / "henry_hub_monthly.xls")
    sheet = book.sheet_by_name("Data 1")
    header_row = next(i for i in range(6) if sheet.cell_value(i, 0) == "Date")
    hub = conn.execute(
        """
        INSERT INTO hubs (name, region, lat, lon, location_quality, notes)
        VALUES (
            'Henry Hub',
            'Gulf Coast',
            29.9616,
            -92.0354,
            'approximate',
            'Mapped at Erath, Louisiana, the town where Henry Hub operates. This is a town centroid for the map, not a surveyed meter location.'
        )
        """
    )
    hub_id = int(hub.lastrowid)
    latest_price = None
    latest_period = None
    annual: dict[int, list[float]] = defaultdict(list)
    for row_idx in range(header_row + 1, sheet.nrows):
        raw_date = sheet.cell_value(row_idx, 0)
        price = as_float(sheet.cell_value(row_idx, 1))
        if price is None or raw_date == "":
            continue
        parsed = xlrd.xldate_as_datetime(raw_date, book.datemode)
        period = f"{parsed.year:04d}-{parsed.month:02d}"
        per_mcf = price * HEAT_MMBTU_PER_MCF
        conn.execute(
            """
            INSERT INTO hub_prices (hub_id, source_id, period, usd_per_mmbtu, usd_per_mcf, heat_mmbtu_per_mcf)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (hub_id, henry_source, period, price, per_mcf, HEAT_MMBTU_PER_MCF),
        )
        annual[parsed.year].append(per_mcf)
        if latest_period is None or period > latest_period:
            latest_period = period
            latest_price = per_mcf
    daily_path = RAW / "prices" / "eia_henry_hub_daily_RNGWHHD.csv"
    if daily_path.is_file():
        latest_daily = None
        for line in daily_path.read_text(encoding="utf-8").splitlines()[1:]:
            if "," not in line:
                continue
            stamp, raw_value = line.split(",", 1)
            value = as_float(raw_value)
            if value is None:
                continue
            latest_daily = (stamp.strip(), value)
        if latest_daily is not None:
            stamp, value = latest_daily
            conn.execute(
                """
                INSERT OR REPLACE INTO hub_prices (
                    hub_id, source_id, period, usd_per_mmbtu, usd_per_mcf, heat_mmbtu_per_mcf
                ) VALUES (?, ?, ?, ?, ?, ?)
                """,
                (hub_id, henry_source, stamp, value, value * HEAT_MMBTU_PER_MCF, HEAT_MMBTU_PER_MCF),
            )
            if latest_period is None or stamp > latest_period:
                latest_period = stamp
                latest_price = value * HEAT_MMBTU_PER_MCF

    citygates = read_eia_series(RAW / "prices" / "citygate_annual.xls", "Natural Gas Citygate Price")
    for name, points in citygates.items():
        if name not in ids:
            continue
        conn.executemany(
            """
            INSERT OR REPLACE INTO citygate_prices (area_id, source_id, period, usd_per_mcf)
            VALUES (?, ?, ?, ?)
            """,
            [(ids[name], city_source, str(year), value) for year, value in points],
        )
        year, citygate = latest(points)
        henry_values = annual.get(year)
        if not henry_values:
            continue
        henry_avg = sum(henry_values) / len(henry_values)
        conn.execute(
            """
            INSERT OR REPLACE INTO location_premiums (
                area_id, period, citygate_usd_per_mcf, henry_usd_per_mcf,
                premium_usd_per_mcf, value_kind, method
            ) VALUES (?, ?, ?, ?, ?, 'citygate_premium', ?)
            """,
            (
                ids[name],
                str(year),
                citygate,
                henry_avg,
                citygate - henry_avg,
                "Citygate price minus the average Henry Hub price for the same calendar year, after converting Henry Hub from $/MMBtu to $/Mcf at 1.037. This is a delivered-price gap, not a gathering tariff. It includes transmission and local distribution charges.",
            ),
        )
    return latest_price, latest_period


def load_lines(conn, table: str, path: Path, source_id: int, columns: list[str]) -> int:
    collection = json.loads(path.read_text(encoding="utf-8"))
    rows = []
    for feature in collection["features"]:
        props = feature["properties"]
        miles = geometry_miles(feature["geometry"])
        payload = [props.get(column) for column in columns]
        rows.append([source_id, *payload, miles, json.dumps(feature["geometry"], separators=(",", ":"))])
    placeholders = ", ".join(["?"] * (len(columns) + 3))
    names = ", ".join(["source_id", *columns, "length_miles", "geojson"])
    conn.executemany(f"INSERT INTO {table} ({names}) VALUES ({placeholders})", rows)
    return len(rows)


def load_basins(conn) -> None:
    source = add_source(
        conn,
        "EIA Drilling Productivity Report",
        "https://www.eia.gov/petroleum/drilling/xls/dpr-data.xlsx",
        "Regional monthly workbook. The stored month is the latest month in the file that is not after 2026-09.",
        "Natural gas total production is published in Mcf/d and stored here as MMcf/d. The newest DPR month can include EIA's short-term estimate.",
    )
    workbook = openpyxl.load_workbook(RAW / "production" / "eia_dpr.xlsx", read_only=True, data_only=True)
    for sheet_name in workbook.sheetnames:
        if sheet_name not in BASIN_ANCHORS:
            continue
        sheet = workbook[sheet_name]
        rows = list(sheet.iter_rows(max_row=2, values_only=True))
        if len(rows) < 2:
            continue
        label_row, header_row = rows[0], rows[1]
        gas_label = next((index for index, value in enumerate(label_row) if value and "Natural gas" in str(value)), None)
        if gas_label is None:
            continue
        total_col = next(
            (
                index
                for index in range(gas_label, len(header_row))
                if header_row[index] and "Total production" in str(header_row[index])
            ),
            None,
        )
        oil_label = next((index for index, value in enumerate(label_row) if value and str(value).startswith("Oil")), None)
        oil_col = None
        if oil_label is not None:
            oil_col = next(
                (
                    index
                    for index in range(oil_label, len(header_row))
                    if header_row[index] and "Total production" in str(header_row[index])
                ),
                None,
            )
        chosen = None
        for row in sheet.iter_rows(min_row=3, values_only=True):
            stamp = row[0]
            gas = as_float(row[total_col]) if total_col is not None and total_col < len(row) else None
            if not isinstance(stamp, datetime) or gas is None:
                continue
            if stamp.date() <= date(2026, 9, 30):
                oil = as_float(row[oil_col]) if oil_col is not None and oil_col < len(row) else None
                chosen = (stamp, gas, oil)
        if chosen is None:
            continue
        stamp, gas_mcfd, oil = chosen
        lat, lon, states, note = BASIN_ANCHORS[sheet_name]
        conn.execute(
            """
            INSERT INTO basins (
                source_id, name, period, gas_mmcfd, oil_bbld, lat, lon, states, location_note
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source,
                sheet_name,
                f"{stamp.year:04d}-{stamp.month:02d}",
                gas_mcfd / 1000.0,
                oil,
                lat,
                lon,
                states,
                note,
            ),
        )
    workbook.close()


DRY_SHALE_PLAYS = {
    "Permian Region": (["Permian"], "August 2026 dry shale for the Permian formation."),
    "Haynesville Region": (["Haynesville"], "August 2026 dry shale for the Haynesville formation."),
    "Eagle Ford Region": (["Eagle Ford"], "August 2026 dry shale for the Eagle Ford formation."),
    "Bakken Region": (["Bakken"], "August 2026 dry shale for the Bakken formation."),
    "Niobrara Region": (
        ["Niobrara-Codell"],
        "August 2026 dry shale for Niobrara-Codell only. The circle is the broader June 2024 Drilling Productivity Report region.",
    ),
    "Appalachia Region": (
        ["Marcellus", "Utica"],
        "August 2026 dry shale is Marcellus plus Utica. The circle is STEO marketed production for the whole Appalachia region.",
    ),
}


def load_marketed_june(conn, ids: dict[str, int]) -> None:
    path = RAW / "production" / "eia_state_production_latest.csv"
    if not path.is_file():
        return
    source = add_source(
        conn,
        "EIA Natural Gas Monthly marketed production",
        "https://www.eia.gov/naturalgas/monthly/xls/ngm07vmall.xls",
        "June 2026, released with the Natural Gas Monthly on 2026-08-31",
        "Monthly marketed production in MMcf. Newer than the 2024 state dry-production cells. Not used in the takeaway-gap calculation.",
    )
    inserted = 0
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        parts = line.split(",")
        if len(parts) < 9 or parts[5] != "marketed_production" or parts[6] != "2026-06":
            continue
        name = parts[0]
        if name not in ids:
            continue
        value = as_float(parts[8])
        if value is None:
            continue
        conn.execute(
            """
            INSERT OR REPLACE INTO volumes (area_id, source_id, product, period, volume_mmcf)
            VALUES (?, ?, 'marketed_production', '2026-06', ?)
            """,
            (ids[name], source, value),
        )
        inserted += 1
    print(f"June 2026 marketed production rows: {inserted}")


def load_dry_shale(conn) -> None:
    path = RAW / "production" / "eia_steo_fig43_dry_shale_bcfd.csv"
    if not path.is_file():
        return
    source = add_source(
        conn,
        "EIA STEO dry shale gas by formation",
        "https://www.eia.gov/outlooks/steo/xls/chart-gallery.xlsx",
        "Chart gallery sheet 43, September 2026 outlook, values through August 2026",
        "Dry shale gas in billion cubic feet per day. A different series from STEO regional marketed production.",
    )
    latest: dict[str, float] = {}
    for line in path.read_text(encoding="utf-8").splitlines()[1:]:
        month, formation, value, _units, _source = line.split(",", 4)
        if month != "2026-08":
            continue
        parsed = as_float(value)
        if parsed is not None:
            latest[formation] = parsed
    for basin_name, (plays, note) in DRY_SHALE_PLAYS.items():
        if not all(play in latest for play in plays):
            continue
        mmcfd = sum(latest[play] for play in plays) * 1000
        conn.execute(
            """
            UPDATE basins
            SET dry_shale_mmcfd = ?, dry_shale_period = '2026-08', dry_shale_note = ?
            WHERE name = ?
            """,
            (mmcfd, note, basin_name),
        )
    print(f"dry shale August 2026 plays loaded from source {source}")


FIPS_TO_ABBR = {
    "01": "AL", "02": "AK", "04": "AZ", "05": "AR", "06": "CA", "08": "CO", "09": "CT",
    "10": "DE", "11": "DC", "12": "FL", "13": "GA", "15": "HI", "16": "ID", "17": "IL",
    "18": "IN", "19": "IA", "20": "KS", "21": "KY", "22": "LA", "23": "ME", "24": "MD",
    "25": "MA", "26": "MI", "27": "MN", "28": "MS", "29": "MO", "30": "MT", "31": "NE",
    "32": "NV", "33": "NH", "34": "NJ", "35": "NM", "36": "NY", "37": "NC", "38": "ND",
    "39": "OH", "40": "OK", "41": "OR", "42": "PA", "44": "RI", "45": "SC", "46": "SD",
    "47": "TN", "48": "TX", "49": "UT", "50": "VT", "51": "VA", "53": "WA", "54": "WV",
    "55": "WI", "56": "WY",
}

TAKEAWAY_METHOD = (
    "EIA does not publish gathering capacity or a tariff at the producer meter. "
    "Vented and flared gas (process VGV) is the measured volume that did not enter a sales stream. "
    "The share divides that volume by gross withdrawals (process FGW). Both are annual million cubic feet for 2024, "
    "divided by 365.25 to show million cubic feet per day. A higher share means a larger fraction of withdrawn gas "
    "never reached a pipeline. It is not a gathering fee and not a nameplate. "
    "Mapped buyers assign each January 2020 EIA centerline to the county containing the segment midpoint. "
    "Operator concentration uses interstate and intrastate miles only. Gathering miles are separate: that layer is about "
    "2,550 miles and is not a national inventory of gathering systems. One mapped operator means one transmission-scale "
    "company in this layer, not one gatherer. No mapped centerline means no interstate or intrastate midpoint in the county."
)


def _outer_rings(geometry: dict) -> list[list]:
    kind = geometry.get("type")
    coords = geometry.get("coordinates") or []
    if kind == "Polygon" and coords:
        return [coords[0]]
    if kind == "MultiPolygon":
        return [poly[0] for poly in coords if poly]
    return []


def _point_in_ring(lon: float, lat: float, ring: list) -> bool:
    inside = False
    previous = len(ring) - 1
    for index, point in enumerate(ring):
        lon_a, lat_a = point[0], point[1]
        lon_b, lat_b = ring[previous][0], ring[previous][1]
        if (lat_a > lat) != (lat_b > lat):
            edge = (lon_b - lon_a) * (lat - lat_a) / ((lat_b - lat_a) or 1e-15) + lon_a
            if lon < edge:
                inside = not inside
        previous = index
    return inside


def _concentration(miles_by_operator: dict[str, float]) -> tuple[int, str | None, float | None, float | None]:
    total = sum(miles_by_operator.values())
    if total <= 0:
        return 0, None, None, None
    ranked = sorted(miles_by_operator.items(), key=lambda item: item[1], reverse=True)
    score = sum((miles / total) ** 2 for _, miles in ranked) * 10000
    return len(ranked), ranked[0][0], ranked[0][1] / total, score


def load_takeaway(conn, ids: dict[str, int]) -> None:
    path = RAW / "api" / "vented_flared_annual.json"
    flared: dict[str, dict[str, float]] = defaultdict(dict)
    if path.is_file():
        source = add_source(
            conn,
            "EIA vented and flared natural gas",
            "https://api.eia.gov/v2/natural-gas/prod/sum/",
            "Annual 2024. Vented and flared is process VGV. Gross withdrawals are process FGW.",
            "Million cubic feet. The share is vented and flared divided by gross withdrawals. States EIA did not publish are left blank, not zero.",
        )
        for row in json.loads(path.read_text(encoding="utf-8")):
            if str(row.get("period")) != "2024" or row.get("process") not in {"VGV", "FGW"}:
                continue
            value = as_float(row.get("value"))
            name = place_name(str(row.get("area-name") or ""))
            if value is None or name not in ids:
                continue
            product = "vented_flared" if row["process"] == "VGV" else "gross_withdrawals"
            flared[name][product] = value
            conn.execute(
                """
                INSERT OR REPLACE INTO volumes (area_id, source_id, product, period, volume_mmcf)
                VALUES (?, ?, ?, '2024', ?)
                """,
                (ids[name], source, product, value),
            )
        print(f"vented and flared areas: {sum(1 for item in flared.values() if 'vented_flared' in item)}")

    county_path = RAW / "geo" / "counties.geojson"
    counties = []
    grid: dict[tuple[int, int], list[int]] = defaultdict(list)
    if county_path.is_file():
        for feature in json.loads(county_path.read_text(encoding="utf-8"))["features"]:
            props = feature.get("properties") or {}
            abbr = FIPS_TO_ABBR.get(str(props.get("STATE") or "").zfill(2))
            rings = _outer_rings(feature.get("geometry") or {})
            if not abbr or not rings:
                continue
            points = [point for ring in rings for point in ring]
            min_lon = min(point[0] for point in points)
            max_lon = max(point[0] for point in points)
            min_lat = min(point[1] for point in points)
            max_lat = max(point[1] for point in points)
            index = len(counties)
            counties.append(
                {
                    "fips": str(feature.get("id") or f"{props.get('STATE')}{props.get('COUNTY')}").zfill(5),
                    "name": props.get("NAME") or "County",
                    "abbr": abbr,
                    "rings": rings,
                    "min_lon": min_lon,
                    "max_lon": max_lon,
                    "min_lat": min_lat,
                    "max_lat": max_lat,
                    "box": max(max_lon - min_lon, 0) * max(max_lat - min_lat, 0),
                }
            )
            for lon_cell in range(math.floor(min_lon), math.floor(max_lon) + 1):
                for lat_cell in range(math.floor(min_lat), math.floor(max_lat) + 1):
                    grid[(lon_cell, lat_cell)].append(index)

    county_miles: dict[int, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    state_miles: dict[str, dict[str, dict[str, float]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(float)))
    if counties:
        for row in conn.execute("SELECT operator, pipe_type, length_miles, geojson FROM pipelines"):
            midpoint = geometry_midpoint(json.loads(row["geojson"]))
            if midpoint is None:
                continue
            lat, lon = midpoint
            candidates = grid.get((math.floor(lon), math.floor(lat)), [])
            matches = []
            for index in candidates:
                county = counties[index]
                if not (county["min_lon"] <= lon <= county["max_lon"] and county["min_lat"] <= lat <= county["max_lat"]):
                    continue
                if any(_point_in_ring(lon, lat, ring) for ring in county["rings"]):
                    matches.append(index)
            if not matches:
                continue
            chosen = min(matches, key=lambda index: counties[index]["box"])
            kind = row["pipe_type"] if row["pipe_type"] in {"Interstate", "Intrastate", "Gathering"} else "Other"
            operator = (row["operator"] or "Unnamed").strip() or "Unnamed"
            miles = row["length_miles"] or 0.0
            county_miles[chosen][kind][operator] += miles
            state_miles[counties[chosen]["abbr"]][kind][operator] += miles
        for index, kinds in county_miles.items():
            county = counties[index]
            transmission = defaultdict(float)
            for kind in ("Interstate", "Intrastate"):
                for operator, miles in kinds.get(kind, {}).items():
                    transmission[operator] += miles
            operators, top_operator, top_share, score = _concentration(transmission)
            gathering = sum(kinds.get("Gathering", {}).values())
            conn.execute(
                """
                INSERT INTO county_takeaway (
                    fips, name, state_abbr, operators, top_operator, top_share, hhi,
                    interstate_miles, intrastate_miles, gathering_miles, gather_only
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    county["fips"],
                    county["name"],
                    county["abbr"],
                    operators,
                    top_operator,
                    top_share,
                    score,
                    sum(kinds.get("Interstate", {}).values()),
                    sum(kinds.get("Intrastate", {}).values()),
                    gathering,
                    1 if operators == 0 and gathering > 0 else 0,
                ),
            )
        print(f"counties with a mapped centerline: {len(county_miles)}")

    for name, area_id in ids.items():
        volumes = flared.get(name, {})
        vented = volumes.get("vented_flared")
        gross = volumes.get("gross_withdrawals")
        if vented is None and name not in ABBR.values() and name != "U.S.":
            continue
        abbr = NAME_TO_ABBR.get(name)
        kinds = state_miles.get(abbr or "", {})
        transmission = defaultdict(float)
        for kind in ("Interstate", "Intrastate"):
            for operator, miles in kinds.get(kind, {}).items():
                transmission[operator] += miles
        operators, top_operator, top_share, score = _concentration(transmission)
        if vented is None and operators == 0 and abbr:
            continue
        share = None if vented is None or not gross else vented / gross
        conn.execute(
            """
            INSERT INTO state_takeaway (
                area_id, flared_mmcfd, flared_period, gross_mmcfd, flared_share,
                operators, top_operator, top_share, hhi,
                interstate_miles, intrastate_miles, gathering_miles, method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                area_id,
                None if vented is None else vented / 365.25,
                None if vented is None else "2024",
                None if gross is None else gross / 365.25,
                share,
                operators if abbr else None,
                top_operator,
                top_share,
                score,
                sum(kinds.get("Interstate", {}).values()) if abbr else None,
                sum(kinds.get("Intrastate", {}).values()) if abbr else None,
                sum(kinds.get("Gathering", {}).values()) if abbr else None,
                TAKEAWAY_METHOD,
            ),
        )


def compute_balances(conn) -> None:
    areas = conn.execute("SELECT id, name, abbr, area_type FROM areas").fetchall()
    for area in areas:
        if area["area_type"] not in {"state", "national", "offshore", "other"}:
            continue
        production_rows = conn.execute(
            """
            SELECT period, volume_mmcf FROM volumes
            WHERE area_id = ? AND product = 'dry_production' ORDER BY period
            """,
            (area["id"],),
        ).fetchall()
        consumption_rows = conn.execute(
            """
            SELECT period, volume_mmcf FROM volumes
            WHERE area_id = ? AND product = 'consumption' ORDER BY period
            """,
            (area["id"],),
        ).fetchall()
        if not production_rows and not consumption_rows:
            continue
        production = {row["period"]: row["volume_mmcf"] for row in production_rows}
        consumption = {row["period"]: row["volume_mmcf"] for row in consumption_rows}
        shared = sorted(set(production) & set(consumption))
        if shared:
            year = shared[-1]
            prod_mmcf = production[year]
            cons_mmcf = consumption[year]
            prod_year = cons_year = year
        elif production:
            prod_year = max(production)
            prod_mmcf = production[prod_year]
            cons_mmcf = None
            cons_year = None
        else:
            continue
        prod_mmcfd = prod_mmcf / 365.25
        cons_mmcfd = None if cons_mmcf is None else cons_mmcf / 365.25
        net = None if cons_mmcfd is None else prod_mmcfd - cons_mmcfd
        outflow_row = conn.execute(
            "SELECT year, capacity_mmcfd FROM state_outflow WHERE area_id = ?",
            (area["id"],),
        ).fetchone()
        outflow = outflow_row["capacity_mmcfd"] if outflow_row else None
        capacity_year = outflow_row["year"] if outflow_row else None
        firm = open_cap = 0.0
        if area["abbr"]:
            sums = conn.execute(
                """
                SELECT
                    COALESCE(SUM(CASE WHEN firm = 1 THEN capacity_mmcfd END), 0) AS firm_cap,
                    COALESCE(SUM(CASE WHEN open = 1 THEN capacity_mmcfd END), 0) AS open_cap
                FROM projects
                WHERE begin_state = ?
                """,
                (area["abbr"],),
            ).fetchone()
            firm = sums["firm_cap"] or 0.0
            open_cap = sums["open_cap"] or 0.0
        gap = gap_firm = gap_open = None
        if net is not None and outflow is not None:
            gap = net - outflow
            gap_firm = net - (outflow + firm)
            gap_open = net - (outflow + open_cap)
        conn.execute(
            """
            INSERT INTO balances (
                area_id, production_year, consumption_year, capacity_year,
                production_mmcfd, consumption_mmcfd, net_supply_mmcfd, outflow_mmcfd,
                firm_planned_mmcfd, open_planned_mmcfd, gap_mmcfd, gap_firm_mmcfd,
                gap_open_mmcfd, method
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                area["id"],
                prod_year,
                cons_year,
                capacity_year,
                prod_mmcfd,
                cons_mmcfd,
                net,
                outflow,
                firm,
                open_cap,
                gap,
                gap_firm,
                gap_open,
                BALANCE_METHOD,
            ),
        )


def tag_basin_projects(conn) -> None:
    projects = conn.execute("SELECT name, notes, capacity_mmcfd, firm, open FROM projects").fetchall()
    for basin in conn.execute("SELECT id, name FROM basins"):
        firm = open_cap = 0.0
        keywords = BASIN_KEYWORDS.get(basin["name"], ())
        for project in projects:
            text = f"{project['name']} {project['notes'] or ''}".lower()
            if not any(keyword in text for keyword in keywords):
                continue
            capacity = project["capacity_mmcfd"] or 0.0
            if project["firm"]:
                firm += capacity
            if project["open"]:
                open_cap += capacity
        conn.execute(
            "UPDATE basins SET firm_planned_mmcfd = ?, open_planned_mmcfd = ? WHERE id = ?",
            (firm, open_cap, basin["id"]),
        )


def build_interconnects(conn) -> None:
    pipe_buckets: dict[tuple[int, int], list[tuple[float, float, str]]] = defaultdict(list)
    cell = 0.08
    for row in conn.execute("SELECT operator, geojson FROM pipelines"):
        geometry = json.loads(row["geojson"])
        midpoint = geometry_midpoint(geometry)
        if midpoint is None:
            continue
        lat, lon = midpoint
        pipe_buckets[(round(lat / cell), round(lon / cell))].append((lat, lon, row["operator"] or ""))
    if not pipe_buckets:
        return
    trans_points = []
    for row in conn.execute("SELECT owner, voltage_kv, geojson FROM transmission_lines"):
        geometry = json.loads(row["geojson"])
        midpoint = geometry_midpoint(geometry)
        if midpoint is None or row["voltage_kv"] is None:
            continue
        trans_points.append((midpoint[0], midpoint[1], row["voltage_kv"], row["owner"] or ""))

    best: dict[tuple[int, int], dict] = {}
    for lat, lon, voltage, owner in trans_points:
        base = (round(lat / cell), round(lon / cell))
        nearest = None
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                for plat, plon, operator in pipe_buckets.get((base[0] + dx, base[1] + dy), ()):
                    distance = haversine_miles(lon, lat, plon, plat)
                    if nearest is None or distance < nearest[0]:
                        nearest = (distance, operator)
        if nearest is None or nearest[0] > 3:
            continue
        key = (round(lat / 0.22), round(lon / 0.22))
        current = best.get(key)
        if current is None or voltage > current["voltage_kv"]:
            best[key] = {
                "lat": lat,
                "lon": lon,
                "voltage_kv": voltage,
                "owner": owner,
                "operator": nearest[1],
                "distance_miles": nearest[0],
            }
    method = (
        "Each point is the midpoint of a public 230 kV-or-higher transmission line "
        "that falls within 3 miles of a natural gas pipeline midpoint. Points are "
        "thinned to the highest voltage in each roughly 15-mile cell. "
        "cost_usd_per_mwh_mile is left empty: published studies report $/mile or "
        "$/MW-mile, and this database does not convert those into a tariff."
    )
    conn.executemany(
        """
        INSERT INTO interconnects (
            lat, lon, voltage_kv, owner, pipeline_operator, distance_miles,
            cost_usd_per_mile, cost_usd_per_mw_mile, cost_usd_per_mwh_mile, method
        ) VALUES (?, ?, ?, ?, ?, ?, NULL, NULL, NULL, ?)
        """,
        [
            (item["lat"], item["lon"], item["voltage_kv"], item["owner"], item["operator"], item["distance_miles"], method)
            for item in best.values()
        ],
    )

    basin_rows = conn.execute("SELECT id, lat, lon FROM basins").fetchall()
    for basin in basin_rows:
        nearest = None
        for lat, lon, _voltage, _owner in trans_points:
            distance = haversine_miles(basin["lon"], basin["lat"], lon, lat)
            if nearest is None or distance < nearest:
                nearest = distance
        conn.execute("UPDATE basins SET miles_to_230kv = ? WHERE id = ?", (nearest, basin["id"]))
    print(f"interconnect cells within 3 miles: {len(best)}")


def link_henry_hub(conn) -> None:
    hub = conn.execute("SELECT id FROM hubs WHERE name = 'Henry Hub'").fetchone()
    if hub is None:
        return
    rows = conn.execute(
        """
        SELECT pipeline, state_from, SUM(capacity_mmcfd) AS capacity_mmcfd
        FROM border_crossings
        WHERE state_to = 'Louisiana' AND pipeline IS NOT NULL AND capacity_mmcfd IS NOT NULL
        GROUP BY pipeline, state_from
        HAVING SUM(capacity_mmcfd) > 0
        ORDER BY capacity_mmcfd DESC
        """
    ).fetchall()
    conn.executemany(
        """
        INSERT INTO pipeline_hub_links (hub_id, pipeline, state_from, capacity_mmcfd, relationship)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            (
                hub["id"],
                row["pipeline"],
                row["state_from"],
                row["capacity_mmcfd"],
                "2025 interstate nameplate into Louisiana, the Henry Hub state. This is not a path-level delivery right to the hub.",
            )
            for row in rows
        ],
    )


STEO_BASINS = {
    "NGMPPM": "Permian Region",
    "NGMPHA": "Haynesville Region",
    "NGMPAP": "Appalachia Region",
    "NGMPBK": "Bakken Region",
    "NGMPEF": "Eagle Ford Region",
}

# Last public EIA Natural Gas Weekly Update, week ending 2026-01-21.
# Only the prices that issue printed, matched to pricing-hub names.
NGWU_SPOTS = {
    "Henry Hub": 4.98,
    "Houston Ship Channel": 4.55,
    "Florida Gas Zone 3": 5.03,
    "Chicago Citygate": 4.79,
}

# EIA Today in Energy, Sept. 10, 2024, citing NGI. Basis = hub minus Henry.
WAHA_BASIS = (
    "2024-01-01/2024-09-10",
    -2.07,
    "Year-to-date 2024 average through the Sept. 10, 2024 EIA article: Waha $2.07/MMBtu below Henry Hub. Not a current spot.",
)


def place_name(label: str) -> str:
    name = str(label or "").strip()
    upper = name.upper()
    if upper in {"U.S.", "US", "UNITED STATES"}:
        return "U.S."
    if upper.startswith("USA-"):
        return ABBR.get(upper.split("-", 1)[1], name)
    if name.isupper():
        return name.title()
    return name


def apply_eia_api(conn, ids: dict[str, int]) -> None:
    api_dir = RAW / "api"
    steo_path = api_dir / "steo_regions.json"
    if steo_path.is_file():
        source = add_source(
            conn,
            "EIA Short-Term Energy Outlook regional gas",
            "https://api.eia.gov/v2/steo/",
            "Monthly STEO through 2026-09. Later months in the outlook are forecasts and were not stored.",
            "Marketed production for Permian, Haynesville, Appalachia, Bakken, and Eagle Ford. Niobrara is the shale-formation series SNGPRNI. Values are billion cubic feet per day.",
        )
        rows = json.loads(steo_path.read_text(encoding="utf-8"))
        kept = [row for row in rows if str(row.get("period") or "") <= "2026-09"]
        conn.executemany(
            """
            INSERT INTO series_points (source_id, series_id, name, period, value, units, kind)
            VALUES (?, ?, ?, ?, ?, ?, 'outlook-month')
            """,
            [
                (
                    source,
                    row.get("seriesId"),
                    row.get("seriesDescription"),
                    row.get("period"),
                    as_float(row.get("value")),
                    row.get("unit") or row.get("units"),
                )
                for row in kept
            ],
        )
        latest: dict[str, dict] = {}
        for row in kept:
            series = row.get("seriesId")
            if series not in latest or str(row.get("period")) > str(latest[series].get("period")):
                latest[series] = row
        for series, basin_name in STEO_BASINS.items():
            row = latest.get(series)
            value = as_float(row.get("value")) if row else None
            if value is None:
                continue
            units = str(row.get("unit") or "")
            mmcfd = value * 1000 if "billion" in units.lower() else None
            if mmcfd is None:
                print(f"skipped {series}: units {units!r}")
                continue
            conn.execute(
                """
                UPDATE basins
                SET source_id = ?, period = ?, gas_mmcfd = ?,
                    location_note = location_note || ' ' || ?
                WHERE name = ?
                """,
                (
                    source,
                    row.get("period"),
                    mmcfd,
                    f"Volume replaced with STEO {series}, {units}. The 2026-09 value is an outlook month, not a final EIA-914 total. Anadarko and Niobrara stay on the June 2024 Drilling Productivity Report: STEO has no Anadarko marketed total, and its Niobrara series is only the Codell formation.",
                    basin_name,
                ),
            )
        print("STEO basins", {name: latest.get(series, {}).get("period") for series, name in STEO_BASINS.items()})

    city_path = api_dir / "citygate_annual.json"
    if city_path.is_file():
        source = add_source(
            conn,
            "EIA API citygate price",
            "https://api.eia.gov/v2/natural-gas/pri/sum/",
            "Annual citygate, process PG1, 2024 and 2025",
            "Dollars per Mcf. State names come from the API area-name field.",
        )
        rows = json.loads(city_path.read_text(encoding="utf-8"))
        by_area: dict[str, list[tuple[str, float]]] = defaultdict(list)
        for row in rows:
            name = place_name(row.get("area-name") or "")
            value = as_float(row.get("value"))
            period = str(row.get("period") or "")
            if name in ids and value is not None and period:
                by_area[name].append((period, value))
        henry_year = {}
        for row in conn.execute(
            """
            SELECT substr(period, 1, 4) AS year, AVG(usd_per_mcf) AS avg_mcf
            FROM hub_prices
            WHERE length(period) = 7
            GROUP BY substr(period, 1, 4)
            """
        ):
            henry_year[row["year"]] = row["avg_mcf"]
        conn.execute("DELETE FROM location_premiums")
        written = 0
        for name, points in by_area.items():
            year, citygate = max(points, key=lambda item: item[0])
            henry_avg = henry_year.get(year)
            if henry_avg is None:
                continue
            conn.execute(
                """
                INSERT OR REPLACE INTO location_premiums (
                    area_id, period, citygate_usd_per_mcf, henry_usd_per_mcf,
                    premium_usd_per_mcf, value_kind, method
                ) VALUES (?, ?, ?, ?, ?, 'citygate_premium', ?)
                """,
                (
                    ids[name],
                    year,
                    citygate,
                    henry_avg,
                    citygate - henry_avg,
                    "EIA API annual citygate minus the average Henry Hub price for that year, converted at 1.037 MMBtu per Mcf. Delivered-price gap, not a gathering tariff.",
                ),
            )
            written += 1
        print(f"citygate premiums from API: {written}")

    hub_path = RAW / "geo" / "trading_hubs.geojson"
    if hub_path.is_file():
        source = add_source(
            conn,
            "EIA natural gas trading hub approximate centers",
            "https://services2.arcgis.com/ZOdjAzAQ2B0f85zi/arcgis/rest/services/NaturalGas_TradingHubs_US_EIA/FeatureServer/0",
            "Public feature copy. Attribute Period is 202002. Points are approximate centers.",
            "Not a surveyed meter map. The EIA organization service for this layer required a token and was not used.",
        )
        collection = json.loads(hub_path.read_text(encoding="utf-8"))
        for feature in collection.get("features") or []:
            props = feature.get("properties") or {}
            name = props.get("HubName") or props.get("Name") or props.get("NAME")
            if not name:
                continue
            name = str(name).strip()
            geometry = feature.get("geometry") or {}
            coords = geometry.get("coordinates") or [None, None]
            lon, lat = coords[0], coords[1]
            if name.lower() == "henry hub":
                conn.execute(
                    """
                    UPDATE hubs
                    SET lat = ?, lon = ?, location_quality = 'published approximate center',
                        notes = ?
                    WHERE name = 'Henry Hub'
                    """,
                    (
                        lat,
                        lon,
                        "Approximate center from the public EIA trading-hub point layer (Period 202002), near Erath, Louisiana. Not a surveyed meter.",
                    ),
                )
                continue
            conn.execute(
                """
                INSERT OR IGNORE INTO hubs (name, region, lat, lon, location_quality, notes)
                VALUES (?, ?, ?, ?, 'approximate', ?)
                """,
                (
                    name,
                    props.get("Region") or props.get("REGION"),
                    lat,
                    lon,
                    "Approximate center from the public EIA trading-hub point layer, Period 202002.",
                ),
            )
        for hub_name, price in NGWU_SPOTS.items():
            if hub_name == "Henry Hub":
                continue
            hub = conn.execute("SELECT id FROM hubs WHERE name = ?", (hub_name,)).fetchone()
            if hub is None:
                print("no hub point for", hub_name)
                continue
            conn.execute(
                """
                INSERT INTO hub_prices (hub_id, source_id, period, usd_per_mmbtu, usd_per_mcf, heat_mmbtu_per_mcf)
                VALUES (?, ?, '2026-01-21', ?, ?, ?)
                """,
                (hub["id"], source, price, price * HEAT_MMBTU_PER_MCF, HEAT_MMBTU_PER_MCF),
            )
        waha = conn.execute("SELECT id FROM hubs WHERE name = 'Waha'").fetchone()
        if waha is not None:
            period, basis, notes = WAHA_BASIS
            conn.execute(
                """
                INSERT INTO hub_basis (hub_name, period, basis_usd_per_mmbtu, notes, source_id)
                VALUES ('Waha', ?, ?, ?, ?)
                """,
                (period, basis, notes, source),
            )

    miso = add_source(
        conn,
        "MISO Transmission Cost Estimation Guide for MTEP24",
        "https://cdn.misoenergy.org/20240501%20PSC%20Item%2004%20MISO%20Transmission%20Cost%20Estimation%20Guide%20for%20MTEP24632680.pdf",
        "Tables 4.1-1 and 4.1-2, May 1, 2024. Dollar-year sentence in the guide says both 2023 and 2024 dollars.",
        "Exploratory $/mile for new AC lines in the printed MISO states, including 30% contingency and 7.5% AFUDC. A screening range, not a project estimate. $/MWh/mile is not published.",
    )
    nrel = add_source(
        conn,
        "DOE National Transmission Planning Study Table D-4",
        "https://www.energy.gov/sites/default/files/2024-10/NationalTransmissionPlanningStudy-Chapter3.pdf",
        "October 2024. Base cost before terrain multipliers. Dollar year is not printed on Table D-4.",
        "Single-circuit and double-circuit base $/mile. 115 kV is not in the table.",
    )
    miso_rows = [
        (115, "single", 1_800_000, 2_200_000),
        (230, "single", 2_000_000, 2_600_000),
        (345, "single", 3_200_000, 4_100_000),
        (500, "single", 4_100_000, 5_100_000),
        (115, "double", 2_600_000, 3_100_000),
        (230, "double", 3_300_000, 4_000_000),
        (345, "double", 5_500_000, 6_400_000),
    ]
    conn.executemany(
        """
        INSERT INTO line_cost_ranges (
            voltage_kv, circuit, geography, cost_usd_per_mile_low, cost_usd_per_mile_high, method, source_id
        ) VALUES (?, ?, 'MISO states in the MTEP24 tables', ?, ?, ?, ?)
        """,
        [
            (
                kv,
                circuit,
                low,
                high,
                "Exploratory capital cost per mile. Range is the low and high state in the MISO table, not a midpoint.",
                miso,
            )
            for kv, circuit, low, high in miso_rows
        ],
    )
    nrel_rows = [
        (230, "single", 1_024_335),
        (345, "single", 1_434_290),
        (500, "single", 2_048_670),
        (230, "double", 1_639_820),
        (345, "double", 2_295_085),
        (500, "double", 3_278_535),
    ]
    conn.executemany(
        """
        INSERT INTO line_cost_ranges (
            voltage_kv, circuit, geography, cost_usd_per_mile_low, cost_usd_per_mile_high, method, source_id
        ) VALUES (?, ?, 'National base cost before terrain multipliers', ?, ?, ?, ?)
        """,
        [
            (kv, circuit, cost, cost, "Table D-4 base cost per mile. Terrain multipliers are not applied.", nrel)
            for kv, circuit, cost in nrel_rows
        ],
    )


def write_methods(conn) -> None:
    conn.execute(
        "INSERT INTO methods (name, body) VALUES (?, ?)",
        ("Takeaway gap", BALANCE_METHOD),
    )
    conn.execute(
        "INSERT INTO methods (name, body) VALUES (?, ?)",
        (
            "Dollars per MWh per mile",
            "Stored line costs are $/mile ranges from MISO MTEP24 and the DOE transmission study. "
            "Those sources do not publish $/MWh/mile. An illustration, not a tariff: divide the MISO 345 kV single-circuit "
            "range ($3.2–$4.1 million per mile) by the guide's 1,792 MVA rating, then by 0.40 × 8,760 × 40. "
            "That is about $0.013–$0.016 per MWh per mile, capital only, with MVA treated as MW. It is not written into the cost column.",
        ),
    )
    conn.execute(
        "INSERT INTO methods (name, body) VALUES (?, ?)",
        (
            "Gathering cost",
            "No national public series of gathering fees by takeaway node was loaded. "
            "The map shows the EIA citygate premium over Henry Hub as a delivered-price gap. "
            "Separately, AEO 2026's Natural Gas Market Module uses one national transport-or-gathering assumption of $0.36 per Mcf in 2025 dollars. "
            "That is a model input for every supply node, not a measured fee at a named hub.",
        ),
    )
    conn.execute(
        "INSERT INTO methods (name, body) VALUES (?, ?)",
        ("Flared gas and mapped buyers", TAKEAWAY_METHOD),
    )


def sanity(conn) -> None:
    us = conn.execute(
        """
        SELECT production_mmcfd, consumption_mmcfd, production_year
        FROM balances b JOIN areas a ON a.id = b.area_id
        WHERE a.name = 'U.S.'
        """
    ).fetchone()
    if us is None or us["production_mmcfd"] is None:
        raise SystemExit("National production did not load.")
    bcfd = us["production_mmcfd"] / 1000
    if not 70 <= bcfd <= 140:
        raise SystemExit(f"National dry production looks wrong: {bcfd:.1f} Bcf/d")
    henry = conn.execute(
        "SELECT period, usd_per_mmbtu FROM hub_prices ORDER BY period DESC LIMIT 1"
    ).fetchone()
    if henry is None or not 0.5 <= henry["usd_per_mmbtu"] <= 30:
        raise SystemExit("Henry Hub price failed the range check.")
    pipes = conn.execute("SELECT COUNT(*) AS n, SUM(length_miles) AS miles FROM pipelines").fetchone()
    print(
        f"U.S. dry production {bcfd:.1f} Bcf/d in {us['production_year']}; "
        f"Henry Hub {henry['usd_per_mmbtu']:.2f} $/MMBtu in {henry['period']}; "
        f"{pipes['n']} pipeline segments, {pipes['miles']:.0f} calculated miles"
    )


def main() -> None:
    conn = connect()
    try:
        ids = load_areas_and_volumes(conn)
        centroids = attach_state_shapes(conn, ids)
        load_capacity(conn, ids)
        load_projects(conn, centroids)
        latest_mcf, latest_period = load_prices(conn, ids)
        print(f"latest Henry Hub ${latest_mcf:.2f}/Mcf in {latest_period}" if latest_mcf else "no Henry Hub price")
        pipe_source = add_source(
            conn,
            "EIA natural gas pipeline centerlines",
            "https://geo.dot.gov/server/rest/services/hosted/Natural_Gas_Pipelines_US_EIA/FeatureServer/0",
            "EIA compilation described as updated January 2020; queried from the public DOT feature service",
            "Interstate, intrastate, and a small number of gathering segments. Mileage is calculated from the simplified centerline.",
        )
        count = load_lines(
            conn,
            "pipelines",
            RAW / "pipelines" / "eia_pipelines.geojson",
            pipe_source,
            ["operator", "pipe_type", "status"],
        )
        print(f"pipelines loaded: {count}")
        load_takeaway(conn, ids)
        transmission_path = RAW / "geo" / "transmission_230kv.geojson"
        if transmission_path.exists():
            grid_source = add_source(
                conn,
                "HIFLD electric power transmission lines, 230 kV and above",
                "https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Electric_Power_Transmission_Lines/FeatureServer/0",
                "Feature service last edited 2023-09-05; subset is VOLTAGE >= 230",
                "Public transmission centerlines. Sub-230 kV lines are omitted so the map shows the bulk supply grid.",
            )
            grid_count = load_lines(
                conn,
                "transmission_lines",
                transmission_path,
                grid_source,
                ["line_id", "line_type", "status", "owner", "voltage_kv", "volt_class", "sub_1", "sub_2"],
            )
            print(f"transmission lines loaded: {grid_count}")
        load_basins(conn)
        load_marketed_june(conn, ids)
        compute_balances(conn)
        tag_basin_projects(conn)
        if transmission_path.exists():
            build_interconnects(conn)
        link_henry_hub(conn)
        apply_eia_api(conn, ids)
        load_dry_shale(conn)
        write_methods(conn)
        sanity(conn)
        conn.commit()
    finally:
        conn.close()
    print(f"wrote {DB_PATH}")


if __name__ == "__main__":
    main()
