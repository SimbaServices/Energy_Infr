"""Read the EIA vented-and-flared series already stored with this project."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data" / "raw" / "api" / "vented_flared_annual.json"


def latest(eia_area: str) -> dict:
    if not PATH.is_file():
        return {}
    rows = [
        row for row in json.loads(PATH.read_text(encoding="utf-8"))
        if row.get("duoarea") == eia_area
        and row.get("process") == "VGV"
        and row.get("value") not in (None, "")
    ]
    if not rows:
        return {}
    rows.sort(key=lambda row: str(row.get("period") or ""), reverse=True)
    row = rows[0]
    mmcf = float(row["value"])
    return {
        "year": str(row["period"]),
        "mmcf": mmcf,
        "mmcfd": round(mmcf / 365, 2),
        "series": row.get("series") or "",
    }
