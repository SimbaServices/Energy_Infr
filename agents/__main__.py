"""Refresh every state agent, then optionally publish the site tree.

    python -m agents
    python -m agents --state nm
    python -m agents --publish

Publishing copies web/ to ENERGY_WEB_ROOT (default /var/www/energy) after a
successful pass. The copy is a separate tree so nginx does not read the
checkout, and so this job never touches the property-evaluation app.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import traceback
from datetime import datetime, timezone
from pathlib import Path

from agents.catalog import AGENTS, BY_CODE
from agents.eia import latest as eia_latest
from agents.infra import clip_network, state_counties, write_collection
from agents.leases import acquire
from agents.pois import build as build_pois

ROOT = Path(__file__).resolve().parents[1]
WEB = ROOT / "web" / "data"
STATES = WEB / "states"


def _now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _summary(agent, counties, network, poi_count, lease_result, eia) -> dict:
    leases = lease_result["leases"]
    located = [feature["properties"] for feature in leases]
    flared = round(sum(row["flared_mmcfd"] for row in located), 2)
    by_field = bool(located) and located[0].get("unit") == "field"
    headline = (
        f"{eia['mmcfd']} MMcfd is the EIA {eia['year']} state total for vented and flared gas "
        f"({eia['mmcf']:,.0f} MMcf that year). "
        if eia else
        "EIA has no vented-and-flared total stored for this state. "
    )
    if by_field:
        headline = (
            f"{flared} MMcfd of gas blown on {len(located):,} fields, "
            "from the state field filing. The shade follows that filing."
        )
    elif located:
        headline += (
            f"{len(located):,} locations on the map have a published vented or flared volume, "
            f"summing to {flared} in the source units scaled to MMcfd."
        )
    else:
        headline += "Lease circles are still empty. " + lease_result["status"]
    return {
        "kicker": agent.name,
        "title": "Vented and flared gas",
        "headline": headline,
        "method": (
            "Pipelines are the EIA centerline compilation from January 2020, clipped to this state. "
            "Transmission lines are the public 230 kV-and-above subset in the project database. "
            "A tie-in point is a stored 230 kV-or-higher line midpoint within 3 miles of a gas-pipeline midpoint. "
            "Points of interconnection are substations and taps of 69 kV and above, from the same public "
            "substation republish and transmission-line archive used for the Texas Permian view. "
            "The EIA state total is process VGV. "
            + lease_result["status"]
        ),
        "updated_at": _now(),
        "tape_posted": "",
        "leases": len(located),
        "lease_unit": "field" if by_field else "lease",
        "flared_mmcfd": flared,
        "flared_mcf": round(sum(row["flared_mcf"] for row in located)),
        "oil_leases": sum(row.get("kind") == "oil" for row in located),
        "gas_wells": sum(row.get("kind") == "gas" for row in located),
        "counties": [feature["properties"]["name"] for feature in counties],
        "pipelines": network["pipelines"],
        "transmission": network["transmission"],
        "tieins": network["tieins"],
        "pois": poi_count,
        "eia": eia,
        "lease_status": lease_result["status"],
        "probes": lease_result["probes"],
        "top": [
            {
                "lease_name": row["lease_name"],
                "field_name": row["field_name"],
                "operator_name": row["operator_name"],
                "county": row["county"],
                "kind": row["kind"],
                "district": row["district"],
                "lease_no": row["lease_no"],
                "period": row["period"],
                "flared_mmcfd": round(row["flared_mmcfd"], 2),
                "flared_mcf": row["flared_mcf"],
                "produced_mcf": row["produced_mcf"],
                "lat": row.get("lat", feature["geometry"]["coordinates"][1] if feature["geometry"]["type"] == "Point" else None),
                "lon": row.get("lon", feature["geometry"]["coordinates"][0] if feature["geometry"]["type"] == "Point" else None),
            }
            for feature, row in list(zip(leases, located))[:25]
        ],
    }


def run_one(agent) -> dict:
    out_dir = STATES / agent.code
    out_dir.mkdir(parents=True, exist_ok=True)
    counties, box = state_counties(agent.fips)
    write_collection(out_dir / "counties.geojson", counties)
    network = clip_network(out_dir, box)
    try:
        poi_count = build_pois(out_dir, agent.postal, agent.name, counties, box)
        poi_error = ""
    except Exception as exc:
        poi_count = 0
        poi_error = str(exc)
        write_collection(out_dir / "pois.geojson", [])
    lease_result = acquire(agent.code, agent.services, out_dir)
    if poi_error:
        lease_result["status"] += f" Substation fetch failed: {poi_error}"
    eia = eia_latest(agent.eia_area)
    summary = _summary(agent, counties, network, poi_count, lease_result, eia)
    (out_dir / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(
        f"{agent.code}: pipelines {network['pipelines']} lines {network['transmission']} "
        f"tie-ins {network['tieins']} pois {poi_count} leases {summary['leases']}"
    )
    return {
        "ok": True,
        "updated_at": summary["updated_at"],
        "leases": summary["leases"],
        "pipelines": network["pipelines"],
        "transmission": network["transmission"],
        "tieins": network["tieins"],
        "pois": poi_count,
        "lease_status": lease_result["status"],
    }


def write_index(results: dict) -> None:
    regions = [{
        "id": "permian",
        "label": "Texas Permian",
        "path": "data",
    }]
    regions.extend(
        {"id": agent.code, "label": agent.name, "path": f"data/states/{agent.code}"}
        for agent in AGENTS
    )
    payload = {
        "default": "permian",
        "updated_at": _now(),
        "regions": regions,
        "agents": results,
    }
    (WEB / "regions.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")


def publish() -> None:
    """Copy the site into the nginx root. The parent directory stays put."""
    target = Path(os.environ.get("ENERGY_WEB_ROOT", "/var/www/energy"))
    target.mkdir(parents=True, exist_ok=True)
    source = ROOT / "web"
    seen = set()
    for path in source.rglob("*"):
        rel = path.relative_to(source)
        dest = target / rel
        seen.add(rel.as_posix())
        if path.is_dir():
            dest.mkdir(parents=True, exist_ok=True)
            continue
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(path, dest)
    for path in target.rglob("*"):
        rel = path.relative_to(target).as_posix()
        if path.is_file() and rel not in seen:
            path.unlink()
    print(f"published {target}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Refresh state map agents")
    parser.add_argument("--state", action="append", default=[], help="State code, repeatable")
    parser.add_argument("--publish", action="store_true")
    args = parser.parse_args()
    selected = [BY_CODE[code] for code in args.state] if args.state else list(AGENTS)
    results = {}
    if (WEB / "regions.json").is_file():
        try:
            results.update(json.loads((WEB / "regions.json").read_text(encoding="utf-8")).get("agents") or {})
        except json.JSONDecodeError:
            results = {}
    for agent in selected:
        try:
            results[agent.code] = run_one(agent)
        except Exception:
            traceback.print_exc()
            results[agent.code] = {"ok": False, "updated_at": _now(), "error": traceback.format_exc()[-500:]}
    write_index(results)
    if args.publish:
        publish()


if __name__ == "__main__":
    main()
