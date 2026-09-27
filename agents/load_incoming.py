"""Load one state snapshot from stdin into us_pipelines.sqlite and the map.

The payload is a single JSON object. A snapshot with lease rows replaces that
state's rows. An empty lease list leaves the table alone.
"""

from __future__ import annotations

import calendar
import json
import os
import shutil
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

from agents.catalog import BY_CODE
from agents.infra import state_counties

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "db" / "us_pipelines.sqlite"
WEB = ROOT / "web" / "data" / "states"
MAX_BYTES = 80_000_000

DDL = """
CREATE TABLE IF NOT EXISTS state_leases (
    id INTEGER PRIMARY KEY,
    state_code TEXT NOT NULL,
    source_id INTEGER REFERENCES sources(id),
    kind TEXT NOT NULL,
    district_code TEXT,
    district_name TEXT,
    lease_no TEXT,
    lease_name TEXT,
    field_name TEXT,
    operator_no TEXT,
    operator_name TEXT,
    period TEXT NOT NULL,
    flared_mcf REAL NOT NULL,
    produced_mcf REAL NOT NULL,
    flared_mmcfd REAL NOT NULL,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    wells INTEGER,
    county_fips TEXT,
    county_name TEXT,
    source_url TEXT NOT NULL,
    retrieved_on TEXT NOT NULL
)
"""


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _period(value: str) -> str:
    text = str(value or "").strip()
    if len(text) == 6 and text.isdigit():
        year, month = int(text[:4]), int(text[4:])
        if 1990 <= year <= 2100 and 1 <= month <= 12:
            return text
    if len(text) == 7 and text[4] == "-" and text[:4].isdigit() and text[5:].isdigit():
        year, month = int(text[:4]), int(text[5:])
        if 1990 <= year <= 2100 and 1 <= month <= 12:
            return f"{year:04d}{month:02d}"
    raise ValueError(f"period must be YYYYMM, got {value!r}")


def _days(period: str) -> int:
    return calendar.monthrange(int(period[:4]), int(period[4:]))[1]


def _num(value, name: str) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        raise ValueError(f"{name} must be a number") from None


def read_payload() -> dict:
    raw = sys.stdin.buffer.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise SystemExit("payload larger than 80 MB")
    try:
        payload = json.loads(raw.decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid JSON: {exc}") from None
    if not isinstance(payload, dict):
        raise SystemExit("payload must be a JSON object")
    return payload


def normalize(payload: dict) -> tuple[str, list[dict], str, str, str]:
    code = str(payload.get("state") or "").strip().lower()
    if code not in BY_CODE:
        raise SystemExit(f"unknown state {code!r}")
    source_url = str(payload.get("source_url") or "").strip()
    source_name = str(payload.get("source_name") or "").strip() or source_url
    retrieved_on = str(payload.get("retrieved_on") or _now()[:10])
    notes = str(payload.get("notes") or "").strip()
    if not source_url.startswith("https://"):
        raise SystemExit("source_url must be an https URL")
    rows_in = payload.get("leases") or []
    if not isinstance(rows_in, list):
        raise SystemExit("leases must be a list")
    _counties, box = state_counties(BY_CODE[code].fips)
    pad = 0.2
    min_lon, min_lat, max_lon, max_lat = box
    rows = []
    for item in rows_in:
        if not isinstance(item, dict):
            continue
        period = _period(item.get("period"))
        flared_mcf = _num(item.get("flared_mcf"), "flared_mcf")
        if flared_mcf <= 0:
            continue
        produced = _num(item.get("produced_mcf") or 0, "produced_mcf")
        lat = _num(item.get("lat"), "lat")
        lon = _num(item.get("lon"), "lon")
        if not (min_lat - pad <= lat <= max_lat + pad and min_lon - pad <= lon <= max_lon + pad):
            continue
        if item.get("flared_mmcfd") is None:
            mmcfd = flared_mcf / 1000 / _days(period)
        else:
            mmcfd = _num(item.get("flared_mmcfd"), "flared_mmcfd")
        kind = str(item.get("kind") or "oil").strip().lower()
        if kind not in {"oil", "gas"}:
            kind = "oil"
        rows.append({
            "kind": kind,
            "district_code": str(item.get("district_code") or ""),
            "district_name": str(item.get("district_name") or ""),
            "lease_no": str(item.get("lease_no") or ""),
            "lease_name": str(item.get("lease_name") or "Unnamed"),
            "field_name": str(item.get("field_name") or ""),
            "operator_no": str(item.get("operator_no") or ""),
            "operator_name": str(item.get("operator_name") or ""),
            "period": period,
            "flared_mcf": flared_mcf,
            "produced_mcf": produced,
            "flared_mmcfd": mmcfd,
            "lat": lat,
            "lon": lon,
            "wells": int(item.get("wells") or 1),
            "county_fips": str(item.get("county_fips") or ""),
            "county_name": str(item.get("county_name") or ""),
            "source_url": str(item.get("source_url") or source_url),
            "retrieved_on": retrieved_on,
        })
    return code, rows, source_name, source_url, notes


def store(code: str, rows: list[dict], source_name: str, source_url: str, notes: str) -> None:
    if not rows:
        print(f"{code}: no located leases, existing rows kept")
        return
    conn = sqlite3.connect(DB)
    try:
        conn.execute(DDL)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_state_leases_state ON state_leases(state_code, flared_mmcfd)")
        cur = conn.execute(
            """
            INSERT INTO sources (name, url, retrieved_on, vintage, license, notes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                source_name,
                source_url,
                rows[0]["retrieved_on"],
                rows[0]["period"],
                "Public state filing",
                notes[:2000],
            ),
        )
        source_id = cur.lastrowid
        conn.execute("DELETE FROM state_leases WHERE state_code = ?", (code,))
        conn.executemany(
            """
            INSERT INTO state_leases (
                state_code, source_id, kind, district_code, district_name, lease_no,
                lease_name, field_name, operator_no, operator_name, period,
                flared_mcf, produced_mcf, flared_mmcfd, lat, lon, wells,
                county_fips, county_name, source_url, retrieved_on
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            [
                (
                    code, source_id, row["kind"], row["district_code"], row["district_name"],
                    row["lease_no"], row["lease_name"], row["field_name"], row["operator_no"],
                    row["operator_name"], row["period"], row["flared_mcf"], row["produced_mcf"],
                    row["flared_mmcfd"], row["lat"], row["lon"], row["wells"],
                    row["county_fips"], row["county_name"], row["source_url"], row["retrieved_on"],
                )
                for row in rows
            ],
        )
        conn.commit()
    finally:
        conn.close()
    write_map(code, rows, source_name, source_url, notes)
    print(f"{code}: stored {len(rows)} leases")


def write_map(code: str, rows: list[dict], source_name: str, source_url: str, notes: str) -> None:
    out_dir = WEB / code
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = sorted(rows, key=lambda row: row["flared_mmcfd"], reverse=True)
    features = []
    for row in rows:
        features.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(row["lon"], 5), round(row["lat"], 5)]},
            "properties": {
                "kind": row["kind"],
                "district": row["district_name"] or row["district_code"],
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
    (out_dir / "leases.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": features}),
        encoding="utf-8",
    )
    summary_path = out_dir / "summary.json"
    summary = {}
    if summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = {}
    total = round(sum(row["flared_mmcfd"] for row in rows), 2)
    agent = BY_CODE[code]
    summary.update({
        "kicker": agent.name,
        "title": "Vented and flared gas",
        "updated_at": _now(),
        "leases": len(rows),
        "flared_mmcfd": total,
        "flared_mcf": round(sum(row["flared_mcf"] for row in rows)),
        "oil_leases": sum(row["kind"] == "oil" for row in rows),
        "gas_wells": sum(row["kind"] == "gas" for row in rows),
        "lease_status": f"{len(rows)} leases from {source_name}. {notes}".strip(),
        "headline": (
            f"{total} MMcfd on {len(rows)} leases with a location, from {source_name}. "
            "Circle size follows that filing."
        ),
        "top": [
            {
                "lease_name": row["lease_name"],
                "field_name": row["field_name"],
                "operator_name": row["operator_name"],
                "county": row["county_name"],
                "kind": row["kind"],
                "district": row["district_name"] or row["district_code"],
                "lease_no": row["lease_no"],
                "period": f"{row['period'][:4]}-{row['period'][4:]}",
                "flared_mmcfd": round(row["flared_mmcfd"], 2),
                "flared_mcf": row["flared_mcf"],
                "produced_mcf": row["produced_mcf"],
                "lat": round(row["lat"], 5),
                "lon": round(row["lon"], 5),
            }
            for row in rows[:25]
        ],
    })
    method = summary.get("method") or ""
    citation = f" Lease volumes were taken from {source_url} on {rows[0]['retrieved_on']}."
    if source_url not in method:
        summary["method"] = (method + citation).strip()
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    publish_state(code)


def publish_state(code: str) -> None:
    target_root = Path(os.environ.get("ENERGY_WEB_ROOT", "/var/www/energy"))
    source = WEB / code
    dest = target_root / "data" / "states" / code
    if not target_root.is_dir():
        print("map root is not on this machine; database updated only")
        return
    dest.mkdir(parents=True, exist_ok=True)
    for path in source.iterdir():
        if path.is_file():
            shutil.copy2(path, dest / path.name)
    print(f"published {dest}")


def main() -> None:
    code, rows, source_name, source_url, notes = normalize(read_payload())
    store(code, rows, source_name, source_url, notes)


if __name__ == "__main__":
    main()
