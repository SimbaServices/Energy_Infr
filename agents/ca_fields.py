"""Shade California fields from CalGEM's monthly gas-blown filing.

WellSTAR does not publish a vented or flared volume on the well layer.
Form OG110D does publish gas blown by field. The map draws the field
boundary for each field with a positive volume in the latest month.
"""

from __future__ import annotations

import calendar
import csv
import io
import json
import urllib.request
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DISPOSITION = (
    "https://calgem-pid.conservation.ca.gov/pid/"
    "2026CaliforniaOilAndGasFieldMonthlyDisposition.csv"
)
BOUNDARIES = (
    "https://gis.conservation.ca.gov/server/rest/services/CalGEM/Admin_Bounds/"
    "MapServer/0/query?where=1%3D1&outFields=NAME,FIELD_CODE,District"
    "&returnGeometry=true&outSR=4326&f=geojson"
)


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _fetch(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "Energy_Infr state agent"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def _code(value) -> str:
    text = str(value or "").strip()
    if text.isdigit():
        return text.zfill(3)
    return text


def _centroid(geometry: dict) -> tuple[float, float]:
    rings = []
    if geometry["type"] == "Polygon":
        rings = [geometry["coordinates"][0]]
    elif geometry["type"] == "MultiPolygon":
        rings = [polygon[0] for polygon in geometry["coordinates"]]
    ring = max(rings, key=len)
    points = ring[:-1] if len(ring) > 1 else ring
    count = len(points) or 1
    lon = sum(point[0] for point in points) / count
    lat = sum(point[1] for point in points) / count
    return round(lat, 5), round(lon, 5)


def _merge(features: list[dict]) -> dict | None:
    polygons = []
    for feature in features:
        geometry = feature["geometry"]
        if geometry["type"] == "Polygon":
            polygons.append(geometry["coordinates"])
        elif geometry["type"] == "MultiPolygon":
            polygons.extend(geometry["coordinates"])
    if not polygons:
        return None
    if len(polygons) == 1:
        return {"type": "Polygon", "coordinates": polygons[0]}
    return {"type": "MultiPolygon", "coordinates": polygons}


def build() -> dict:
    disposition = csv.DictReader(io.StringIO(_fetch(DISPOSITION, 60).decode("utf-8-sig")))
    by_month: dict[str, list[dict]] = defaultdict(list)
    for row in disposition:
        blown = float(row.get("GasBlown") or 0)
        if blown <= 0:
            continue
        period = str(row.get("DispositionDate") or "")[:7].replace("-", "")
        if len(period) != 6:
            continue
        by_month[period].append(row)
    if not by_month:
        raise ValueError("the disposition file has no positive gas-blown rows")
    period = max(by_month)
    days = calendar.monthrange(int(period[:4]), int(period[4:]))[1]
    totals: dict[str, dict] = {}
    unplaced_mcf = 0.0
    for row in by_month[period]:
        code = _code(row.get("FieldCode"))
        blown = float(row["GasBlown"])
        if code == "000":
            unplaced_mcf += blown
            continue
        entry = totals.get(code)
        if entry is None:
            totals[code] = {
                "name": str(row.get("fieldname") or "").strip(),
                "district": str(row.get("District") or "").strip(),
                "mcf": blown,
            }
        else:
            entry["mcf"] += blown

    boundaries = json.loads(_fetch(BOUNDARIES, 90).decode("utf-8"))
    grouped: dict[str, list[dict]] = defaultdict(list)
    for feature in boundaries.get("features") or []:
        grouped[_code(feature["properties"].get("FIELD_CODE"))].append(feature)

    features = []
    missing = []
    for code, entry in totals.items():
        parts = grouped.get(code) or []
        if not parts:
            missing.append(entry["name"] or code)
            continue
        geometry = _merge(parts)
        if geometry is None:
            missing.append(entry["name"] or code)
            continue
        lat, lon = _centroid(geometry)
        name = str(parts[0]["properties"].get("NAME") or entry["name"] or code)
        district = str(parts[0]["properties"].get("District") or entry["district"])
        mmcfd = entry["mcf"] / 1000 / days
        features.append({
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "unit": "field",
                "kind": "field",
                "district": district,
                "lease_no": code,
                "lease_name": name,
                "field_name": name,
                "operator_no": "",
                "operator_name": "",
                "period": period,
                "flared_mcf": round(entry["mcf"], 1),
                "produced_mcf": 0,
                "flared_mmcfd": round(mmcfd, 3),
                "wells": 0,
                "county": "",
                "lat": lat,
                "lon": lon,
            },
        })
    features.sort(key=lambda feature: feature["properties"]["flared_mmcfd"], reverse=True)
    placed_mcf = sum(feature["properties"]["flared_mcf"] for feature in features)
    month = f"{period[:4]}-{period[4:]}"
    status = (
        f"{len(features)} California fields are shaded from CalGEM form OG110D gas blown "
        f"for {month} ({placed_mcf:,.0f} Mcf). "
        f"The filing is by field, so the map uses the field boundary instead of a well. "
        f"Source: {DISPOSITION}."
    )
    if unplaced_mcf:
        status += f" {unplaced_mcf:,.0f} Mcf is filed as Any Field and has no boundary."
    if missing:
        status += " No boundary was published for " + ", ".join(missing) + "."
    return {
        "features": features,
        "status": status,
        "source_url": DISPOSITION,
        "period": period,
        "unplaced_mcf": unplaced_mcf,
    }


def write_summary(summary_path: Path, built: dict) -> None:
    summary = {}
    if summary_path.is_file():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            summary = {}
    features = built["features"]
    total = round(sum(row["properties"]["flared_mmcfd"] for row in features), 2)
    period = built["period"]
    month = f"{period[:4]}-{period[4:]}"
    summary.update({
        "kicker": "California",
        "title": "Vented and flared gas",
        "updated_at": _now(),
        "leases": len(features),
        "lease_unit": "field",
        "flared_mmcfd": total,
        "flared_mcf": round(sum(row["properties"]["flared_mcf"] for row in features)),
        "oil_leases": 0,
        "gas_wells": 0,
        "lease_status": built["status"],
        "headline": (
            f"{total} MMcfd of gas blown on {len(features)} fields in {month}, "
            "from CalGEM form OG110D. The shade follows that field filing."
        ),
        "top": [
            {
                "lease_name": row["properties"]["lease_name"],
                "field_name": row["properties"]["field_name"],
                "operator_name": "",
                "county": "",
                "kind": "field",
                "district": row["properties"]["district"],
                "lease_no": row["properties"]["lease_no"],
                "period": month,
                "flared_mmcfd": round(row["properties"]["flared_mmcfd"], 2),
                "flared_mcf": row["properties"]["flared_mcf"],
                "produced_mcf": 0,
                "lat": row["properties"]["lat"],
                "lon": row["properties"]["lon"],
            }
            for row in features[:25]
        ],
    })
    method = summary.get("method") or ""
    citation = f" Field volumes were taken from {DISPOSITION} on {_now()[:10]}."
    if DISPOSITION not in method:
        summary["method"] = (method + citation).strip()
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")


def main() -> None:
    out_dir = ROOT / "web" / "data" / "states" / "ca"
    out_dir.mkdir(parents=True, exist_ok=True)
    built = build()
    (out_dir / "leases.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": built["features"]}),
        encoding="utf-8",
    )
    write_summary(out_dir / "summary.json", built)
    print(built["status"])


if __name__ == "__main__":
    main()
