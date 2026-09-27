"""Look for lease-level vented or flared volumes in each state's public service.

The Permian layer is a filing volume joined to a surface-well centroid. These
agents ask the same question of each state's published well or production
service: is there a vented or flared column, and can it be drawn as a point?
A service that only publishes locations is recorded and is not drawn as if it
were a flare volume.
"""

from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "agents"

VOLUME_HINTS = ("flare", "vent", "vgv", "flared", "vented")
NAME_HINTS = ("lease_name", "lease", "well_name", "wellname", "name", "facility")
OPERATOR_HINTS = ("operator", "operator_name", "operatorname", "company", "ogrid")
COUNTY_HINTS = ("county", "county_name", "parish")
FIELD_HINTS = ("field_name", "field", "fieldname")


def _get(url: str, timeout: int = 25):
    request = urllib.request.Request(url, headers={"User-Agent": "Energy_Infr state agent"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.load(response)


def _pick(fields: list[str], hints: tuple[str, ...]) -> str:
    lowered = {field.lower(): field for field in fields}
    for hint in hints:
        if hint in lowered:
            return lowered[hint]
    for hint in hints:
        for key, original in lowered.items():
            if hint in key:
                return original
    return ""


def _volume_field(fields: list[str]) -> str:
    for field in fields:
        token = field.lower()
        if any(hint in token for hint in VOLUME_HINTS) and "date" not in token:
            return field
    return ""


def probe(url: str) -> dict:
    """Return layer metadata, or an error string. Does not download features."""
    meta_url = url + ("&" if "?" in url else "?") + "f=json"
    try:
        payload = _get(meta_url)
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
        return {"url": url, "ok": False, "error": str(exc)}
    if payload.get("error"):
        return {"url": url, "ok": False, "error": json.dumps(payload["error"])[:300]}
    fields = [field.get("name") or "" for field in payload.get("fields") or []]
    return {
        "url": url,
        "ok": True,
        "name": payload.get("name") or "",
        "fields": fields,
        "volume_field": _volume_field(fields),
        "max_record_count": payload.get("maxRecordCount") or 2000,
    }


def _number(value) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def fetch_volumes(url: str, volume_field: str, meta: dict, dest: Path) -> list:
    """Page features that have a positive vented or flared volume."""
    page_size = min(int(meta.get("max_record_count") or 2000), 2000)
    name_field = _pick(meta["fields"], NAME_HINTS)
    operator_field = _pick(meta["fields"], OPERATOR_HINTS)
    county_field = _pick(meta["fields"], COUNTY_HINTS)
    field_field = _pick(meta["fields"], FIELD_HINTS)
    wanted = [volume_field, name_field, operator_field, county_field, field_field]
    out_fields = ",".join(dict.fromkeys(field for field in wanted if field))
    features = []
    offset = 0
    while True:
        query = urllib.parse.urlencode({
            "where": f"{volume_field} > 0",
            "outFields": out_fields or "*",
            "returnGeometry": "true",
            "outSR": "4326",
            "f": "geojson",
            "resultOffset": offset,
            "resultRecordCount": page_size,
        })
        payload = _get(url + "/query?" + query, timeout=180)
        batch = payload.get("features") or []
        features.extend(batch)
        if not payload.get("exceededTransferLimit") or not batch:
            break
        offset += len(batch)
        if offset > 200000:
            break
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps({"type": "FeatureCollection", "features": features}), encoding="utf-8")
    leases = []
    for feature in features:
        geometry = feature.get("geometry") or {}
        if geometry.get("type") != "Point":
            continue
        lon, lat = geometry["coordinates"][:2]
        props = feature.get("properties") or {}
        volume = _number(props.get(volume_field))
        if volume <= 0:
            continue
        leases.append({
            "type": "Feature",
            "geometry": {"type": "Point", "coordinates": [round(lon, 5), round(lat, 5)]},
            "properties": {
                "kind": "gas",
                "district": "",
                "lease_no": "",
                "lease_name": str(props.get(name_field) or "Unnamed"),
                "field_name": str(props.get(field_field) or ""),
                "operator_no": "",
                "operator_name": str(props.get(operator_field) or ""),
                "period": "",
                "flared_mcf": volume,
                "produced_mcf": 0,
                "flared_mmcfd": round(volume / 1000, 3),
                "wells": 1,
                "county": str(props.get(county_field) or ""),
                "volume_field": volume_field,
            },
        })
    leases.sort(key=lambda feature: feature["properties"]["flared_mcf"], reverse=True)
    return leases


def acquire(code: str, services: tuple[str, ...], out_dir: Path) -> dict:
    notes = []
    for url in services:
        meta = probe(url)
        notes.append({
            "url": url,
            "ok": meta.get("ok", False),
            "error": meta.get("error", ""),
            "volume_field": meta.get("volume_field", ""),
            "field_count": len(meta.get("fields") or []),
        })
        if not meta.get("ok"):
            continue
        volume_field = meta.get("volume_field") or ""
        if not volume_field:
            continue
        try:
            leases = fetch_volumes(url, volume_field, meta, RAW / code / "leases-raw.geojson")
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            notes[-1]["error"] = str(exc)
            continue
        (out_dir / "leases.geojson").write_text(
            json.dumps({"type": "FeatureCollection", "features": leases}),
            encoding="utf-8",
        )
        return {
            "leases": leases,
            "status": f"Drew {len(leases)} points from {volume_field} on {url}",
            "probes": notes,
        }
    if code == "ca":
        try:
            from agents.ca_fields import build as build_ca_fields

            built = build_ca_fields()
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError, ValueError) as exc:
            notes.append({"url": "calgem-og110d", "ok": False, "error": str(exc), "volume_field": "", "field_count": 0})
        else:
            features = built["features"]
            if features:
                (out_dir / "leases.geojson").write_text(
                    json.dumps({"type": "FeatureCollection", "features": features}),
                    encoding="utf-8",
                )
                return {"leases": features, "status": built["status"], "probes": notes}
    kept = _existing(out_dir / "leases.geojson")
    if kept:
        return {
            "leases": kept,
            "status": "The well service had no vented or flared column, so the filing already on the map was kept.",
            "probes": notes,
        }
    (out_dir / "leases.geojson").write_text(
        json.dumps({"type": "FeatureCollection", "features": []}),
        encoding="utf-8",
    )
    reached = [note for note in notes if note["ok"]]
    if not notes:
        status = "No well service is configured for this state."
    elif not reached:
        status = "The public well service did not respond on this run, so lease volumes were not updated."
    else:
        status = (
            "The public well service responded, and it does not publish a vented or flared column. "
            "Lease circles stay empty until a filing with that column is found."
        )
    return {"leases": [], "status": status, "probes": notes}


def _existing(path: Path) -> list[dict]:
    if not path.is_file():
        return []
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    features = payload.get("features") or []
    return features if isinstance(features, list) else []
