"""States the host agents keep current.

Each entry is the same kind of view as the Texas Permian map: county outlines,
gas pipeline centerlines, 230 kV transmission, grid tie-in points, 69 kV
points of interconnection, and lease-level vented or flared gas when a public
filing exposes that column.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class StateAgent:
    code: str
    name: str
    postal: str
    fips: str
    eia_area: str
    # Public well or production services the agent probes, in order.
    # A service is used for lease circles only when it exposes a vented or
    # flared volume. Otherwise the agent records the field list and moves on.
    services: tuple[str, ...]


AGENTS: tuple[StateAgent, ...] = (
    StateAgent(
        "nm",
        "New Mexico",
        "NM",
        "35",
        "SNM",
        (
            "https://services5.arcgis.com/f4lpEvI6fkgVYigk/arcgis/rest/services/"
            "New_Mexico_Oil_and_Gas_Wells__Nov2024/FeatureServer/0",
        ),
    ),
    StateAgent(
        "co",
        "Colorado",
        "CO",
        "08",
        "SCO",
        (
            "https://gis.colorado.gov/public/rest/services/ENERGY/Oil_and_Gas_Locations/FeatureServer/0",
        ),
    ),
    StateAgent(
        "wy",
        "Wyoming",
        "WY",
        "56",
        "SWY",
        (
            "https://gis.wyo.gov/arcgis/rest/services/wogcc/wogcc_wells/FeatureServer/0",
        ),
    ),
    StateAgent(
        "ca",
        "California",
        "CA",
        "06",
        "SCA",
        (
            "https://gis.conservation.ca.gov/server/rest/services/WellSTAR/Wells/FeatureServer/0",
        ),
    ),
    StateAgent(
        "sd",
        "South Dakota",
        "SD",
        "46",
        "SSD",
        (
            "https://arcgis.sd.gov/arcgis/rest/services/DENR/Minerals_and_Mining/FeatureServer/0",
        ),
    ),
    StateAgent(
        "nd",
        "North Dakota",
        "ND",
        "38",
        "SND",
        (
            "https://gis.dmr.nd.gov/dmrpublicservices/rest/services/"
            "OilGasPublicMapDataVectorTiles/Wells/FeatureServer/0",
        ),
    ),
    StateAgent(
        "la",
        "Louisiana",
        "LA",
        "22",
        "SLA",
        (
            "https://sonriswww.dnr.state.la.us/gis/rest/services/Oil_Gas/Wells/FeatureServer/0",
        ),
    ),
    StateAgent(
        "ar",
        "Arkansas",
        "AR",
        "05",
        "SAR",
        (
            "https://gis.arkansas.gov/arcgis/rest/services/FEATURESERVICES/Oil_and_Gas/FeatureServer/0",
        ),
    ),
    StateAgent(
        "ks",
        "Kansas",
        "KS",
        "20",
        "SKS",
        (
            "https://services.kgs.ku.edu/arcgis/rest/services/oilgas/oilgas_wells/FeatureServer/0",
        ),
    ),
)

BY_CODE = {agent.code: agent for agent in AGENTS}
