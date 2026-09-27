-- Research database for U.S. natural gas takeaway and the high-voltage grid.
-- Geometries are GeoJSON in WGS84 (lon, lat). Volumes in the balance tables are
-- daily averages (MMcf/d) derived from annual MMcf where the source is annual.

PRAGMA foreign_keys = ON;

CREATE TABLE sources (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    url TEXT,
    retrieved_on TEXT,
    vintage TEXT,
    license TEXT,
    notes TEXT
);

CREATE TABLE pipelines (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    operator TEXT,
    pipe_type TEXT,
    status TEXT,
    length_miles REAL,
    geojson TEXT NOT NULL
);

CREATE TABLE transmission_lines (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    line_id TEXT,
    line_type TEXT,
    status TEXT,
    owner TEXT,
    voltage_kv REAL,
    volt_class TEXT,
    sub_1 TEXT,
    sub_2 TEXT,
    length_miles REAL,
    geojson TEXT NOT NULL
);

CREATE TABLE areas (
    id INTEGER PRIMARY KEY,
    area_type TEXT NOT NULL,          -- state, offshore, national, other
    name TEXT NOT NULL UNIQUE,
    abbr TEXT,
    lat REAL,
    lon REAL
);

CREATE TABLE volumes (
    id INTEGER PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    source_id INTEGER REFERENCES sources(id),
    product TEXT NOT NULL,            -- dry_production, consumption
    period TEXT NOT NULL,             -- YYYY
    volume_mmcf REAL NOT NULL,
    UNIQUE (area_id, product, period)
);

CREATE TABLE border_crossings (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    pipeline TEXT,
    state_from TEXT,
    county_from TEXT,
    state_to TEXT,
    county_to TEXT,
    year INTEGER NOT NULL,
    capacity_mmcfd REAL
);

CREATE TABLE state_flows (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    state_from TEXT NOT NULL,
    state_to TEXT NOT NULL,
    year INTEGER NOT NULL,
    capacity_mmcfd REAL NOT NULL
);

CREATE TABLE state_outflow (
    area_id INTEGER REFERENCES areas(id),
    source_id INTEGER REFERENCES sources(id),
    year INTEGER NOT NULL,
    capacity_mmcfd REAL NOT NULL,
    PRIMARY KEY (area_id, year)
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    name TEXT NOT NULL,
    operator TEXT,
    project_type TEXT,
    status TEXT,
    in_service_year INTEGER,
    completed_on TEXT,
    states TEXT,
    begin_state TEXT,
    end_state TEXT,
    region TEXT,
    capacity_mmcfd REAL,
    capacity_note TEXT,
    miles REAL,
    diameter_in REAL,
    cost_millions TEXT,
    demand_served TEXT,
    docket TEXT,
    notes TEXT,
    lat REAL,
    lon REAL,
    firm INTEGER NOT NULL DEFAULT 0,  -- construction, approved, part completed
    open INTEGER NOT NULL DEFAULT 0   -- firm plus applied, announced, proposed
);

CREATE TABLE basins (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    name TEXT NOT NULL UNIQUE,
    period TEXT,
    gas_mmcfd REAL,
    oil_bbld REAL,
    lat REAL,
    lon REAL,
    states TEXT,
    location_note TEXT,
    miles_to_230kv REAL,
    firm_planned_mmcfd REAL,
    open_planned_mmcfd REAL,
    dry_shale_mmcfd REAL,
    dry_shale_period TEXT,
    dry_shale_note TEXT
);

CREATE TABLE hubs (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    region TEXT,
    lat REAL,
    lon REAL,
    location_quality TEXT,
    notes TEXT
);

CREATE TABLE hub_prices (
    id INTEGER PRIMARY KEY,
    hub_id INTEGER REFERENCES hubs(id),
    source_id INTEGER REFERENCES sources(id),
    period TEXT NOT NULL,             -- YYYY-MM
    usd_per_mmbtu REAL,
    usd_per_mcf REAL,
    heat_mmbtu_per_mcf REAL,
    UNIQUE (hub_id, period)
);

CREATE TABLE citygate_prices (
    id INTEGER PRIMARY KEY,
    area_id INTEGER REFERENCES areas(id),
    source_id INTEGER REFERENCES sources(id),
    period TEXT NOT NULL,
    usd_per_mcf REAL NOT NULL,
    UNIQUE (area_id, period)
);

CREATE TABLE location_premiums (
    area_id INTEGER PRIMARY KEY REFERENCES areas(id),
    period TEXT,
    citygate_usd_per_mcf REAL,
    henry_usd_per_mcf REAL,
    premium_usd_per_mcf REAL,
    value_kind TEXT NOT NULL,
    method TEXT NOT NULL
);

CREATE TABLE pipeline_hub_links (
    id INTEGER PRIMARY KEY,
    hub_id INTEGER REFERENCES hubs(id),
    pipeline TEXT,
    state_from TEXT,
    capacity_mmcfd REAL,
    relationship TEXT
);

CREATE TABLE balances (
    area_id INTEGER PRIMARY KEY REFERENCES areas(id),
    production_year TEXT,
    consumption_year TEXT,
    capacity_year INTEGER,
    production_mmcfd REAL,
    consumption_mmcfd REAL,
    net_supply_mmcfd REAL,
    outflow_mmcfd REAL,
    firm_planned_mmcfd REAL,
    open_planned_mmcfd REAL,
    gap_mmcfd REAL,
    gap_firm_mmcfd REAL,
    gap_open_mmcfd REAL,
    method TEXT NOT NULL
);

CREATE TABLE interconnects (
    id INTEGER PRIMARY KEY,
    lat REAL NOT NULL,
    lon REAL NOT NULL,
    voltage_kv REAL,
    owner TEXT,
    pipeline_operator TEXT,
    distance_miles REAL,
    cost_usd_per_mile REAL,
    cost_usd_per_mw_mile REAL,
    cost_usd_per_mwh_mile REAL,
    method TEXT NOT NULL
);

CREATE TABLE methods (
    id INTEGER PRIMARY KEY,
    name TEXT NOT NULL,
    body TEXT NOT NULL
);

CREATE TABLE series_points (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    series_id TEXT NOT NULL,
    name TEXT,
    period TEXT NOT NULL,
    value REAL,
    units TEXT,
    kind TEXT
);

CREATE TABLE hub_basis (
    id INTEGER PRIMARY KEY,
    hub_name TEXT NOT NULL,
    period TEXT NOT NULL,
    basis_usd_per_mmbtu REAL,
    notes TEXT,
    source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE line_cost_ranges (
    id INTEGER PRIMARY KEY,
    voltage_kv INTEGER NOT NULL,
    circuit TEXT NOT NULL,
    geography TEXT NOT NULL,
    cost_usd_per_mile_low REAL,
    cost_usd_per_mile_high REAL,
    method TEXT NOT NULL,
    source_id INTEGER REFERENCES sources(id)
);

CREATE TABLE state_takeaway (
    area_id INTEGER PRIMARY KEY REFERENCES areas(id),
    flared_mmcfd REAL,
    flared_period TEXT,
    gross_mmcfd REAL,
    flared_share REAL,
    operators INTEGER,
    top_operator TEXT,
    top_share REAL,
    hhi REAL,
    interstate_miles REAL,
    intrastate_miles REAL,
    gathering_miles REAL,
    method TEXT NOT NULL
);

CREATE TABLE county_takeaway (
    fips TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    state_abbr TEXT,
    operators INTEGER,
    top_operator TEXT,
    top_share REAL,
    hhi REAL,
    interstate_miles REAL,
    intrastate_miles REAL,
    gathering_miles REAL,
    gather_only INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE permian_leases (
    id INTEGER PRIMARY KEY,
    source_id INTEGER REFERENCES sources(id),
    kind TEXT NOT NULL,                 -- oil lease or gas well
    district_code TEXT NOT NULL,
    district_name TEXT NOT NULL,
    lease_no TEXT NOT NULL,
    lease_name TEXT,
    field_name TEXT,
    operator_no TEXT,
    operator_name TEXT,
    period TEXT NOT NULL,               -- YYYYMM
    flared_mcf REAL NOT NULL,
    produced_mcf REAL NOT NULL,
    flared_mmcfd REAL NOT NULL,
    lat REAL,
    lon REAL,
    wells INTEGER,
    county_fips TEXT,
    county_name TEXT
);

CREATE TABLE state_leases (
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
);

CREATE INDEX idx_state_leases_state ON state_leases(state_code, flared_mmcfd);

CREATE INDEX idx_pipelines_operator ON pipelines(operator);
CREATE INDEX idx_pipelines_type ON pipelines(pipe_type);
CREATE INDEX idx_transmission_kv ON transmission_lines(voltage_kv);
CREATE INDEX idx_crossings_states ON border_crossings(state_from, state_to);
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_volumes_area ON volumes(area_id, product, period);
