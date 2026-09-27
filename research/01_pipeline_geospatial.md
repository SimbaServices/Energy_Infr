# Public U.S. natural gas pipeline geospatial and capacity data

Checked 2026-09-26 from public government and research pages. No restricted HIFLD or NPMS layers were requested.

The drawn centerlines and the capacity tables are different datasets. The public centerline has operator, type, status, and length. It does not have pipeline name, diameter, or capacity in MMcf/d. Capacity is in EIA’s state-to-state workbook, at the grain of a border crossing, not a map segment.

## 1. EIA interstate and intrastate centerline

EIA compiled this polyline layer from FERC Form 567 and other public sources. The layer description says it was updated January 2020. EIA’s own ArcGIS organization no longer hosts the layer. Three public copies of that compile were still queryable on 2026-09-26.

### Recommended service (DOE / NETL)

- Layer page: https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3
- Query (GeoJSON, page with `resultOffset`; `maxRecordCount` is 2,000): https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer/3/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=geojson
- Parent service also has crude, products, and HGL lines: https://arcgis.netl.doe.gov/server/rest/services/Hosted/EIA_pipeline_data/FeatureServer
- Capability is Query. Advertised export formats: sqlite, filegdb, shapefile, csv, geojson. There is no single zip URL on this service.
- Copyright text on the layer is blank. Attribute the geometry to the U.S. Energy Information Administration.

Fields: `fid`, `typepipe` (alias TYPEPIPE), `operator` (length 50), `shape_leng`, `shape__len`, `miles`, `km`, plus virtual `SHAPE__Length`. Subtypes: Interstate, Intrastate, Gathering.

A count query on 2026-09-26 returned **32,961** features:

| TYPEPIPE | Features | Sum of `miles` |
| --- | ---: | ---: |
| Interstate | 17,996 | 148,839.12 |
| Intrastate | 14,896 | 75,101.44 |
| Gathering | 69 | 2,547.42 |

The `miles` values are segment lengths stored on the features. Summing them is not a claim of unique route miles.

Not on this layer: pipeline name, diameter, status, or capacity in MMcf/d.

### File download of the same compile (DataLumos / former HIFLD Open)

Catalog page (files listed there; this page does not publish a stable hotlink): https://www.datalumos.org/datalumos/project/239743/version/V1/view

DOI: https://doi.org/10.3886/E239743V1

Posted 2025-11-06. Summary text: major natural gas transmission pipelines, including interstate, intrastate, and gathering; compiled by EIA; updated January 2020. Original distribution URL recorded as https://hifld-geoplatform.hub.arcgis.com/

| File | Listed size |
| --- | --- |
| `natural-gas-interstate-and-intrastate-pipelines-shapefile.zip` | 2.9 MB |
| `natural-gas-interstate-and-intrastate-pipelines-geojson.zip` | 3.2 MB |
| `natural-gas-interstate-and-intrastate-pipelines-geopackage.zip` | 3.3 MB |
| `natural-gas-interstate-and-intrastate-pipelines-file_geodatabase.zip` | 2.8 MB |
| `metadata.xml` | 7.8 KB |

License on the catalog page: **Public Domain Mark**. ICPSR states it distributes the deposit as received and has not reviewed it.

Citation requested on the page: U.S. Energy Information Administration and U.S. Department of Homeland Security, HIFLD OPEN Natural Gas Interstate and Intrastate Pipelines, Ann Arbor, MI: Inter-university Consortium for Political and Social Research, 2025-11-06, https://doi.org/10.3886/E239743V1

The feature count above is from the live services, not from unzipping this archive.

### Other public copies

U.S. DOT hosted feature service, description `NaturalGas_Pipelines_US_202001`, same **32,961** features, all `Status` = `Operating` in a group-by on 2026-09-26:

https://geo.dot.gov/server/rest/services/Hosted/Natural_Gas_Pipelines_US_EIA/FeatureServer/0

Fields: `objectid`, `typepipe`, `operator`, `status`, `shape_leng`. Item access information: U.S. Energy Information Administration. Copyright text is blank.

Esri Living Atlas view (not the preferred download):

https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Natural_Gas_Interstate_and_Intrastate_Pipelines_1/FeatureServer/0

Item: https://www.arcgis.com/home/item.html?id=9833ca6c8103490b8ad145a30f0522ee

Fields: `FID`, `TYPEPIPE`, `Operator`, `Status`, `Shape_Leng`, `Shape__Length`. A group-by returned Interstate 17,996 and Intrastate 14,896 only (**32,892**). The 69 Gathering lines are absent. Item license: **Esri Master License Agreement**. The item says the layer is checked against the federal source when updates are available. The service reports a data last-edit timestamp of 2025-07-01 UTC; the feature counts still match the January 2020 interstate and intrastate totals.

## 2. HIFLD / GeoPlatform

HIFLD Open is no longer a public catalog. The DataLumos deposit says it was archived from HIFLD Open, which was **deactivated on August 26, 2025**, and records the old hub at https://hifld-geoplatform.hub.arcgis.com/

The current DHS HIFLD page (updated 2025-09-04) describes only **HIFLD Secure** on the DHS Geospatial Information Infrastructure. Access requires a GII account, a MyHIFLD profile, and an approved Data Use Agreement. Non-DHS users need a DHS-authorized Login.gov account. https://www.dhs.gov/gmo/hifld

That layer is restricted. It was not queried.

The public substitute for the old HIFLD Open natural gas polyline is the DataLumos deposit in section 1, plus the DOE and DOT services. Those copies do not add name, diameter, or MMcf/d capacity.

## 3. EIA state-to-state capacity spreadsheet

Landing page: https://www.eia.gov/naturalgas/data.php#pipelines (the workbook’s own contents sheet also cites https://www.eia.gov/naturalgas/data.cfm#pipelines)

Current file, downloaded 2026-09-26, HTTP 200, **4,115,317 bytes**:

https://www.eia.gov/naturalgas/pipelines/EIA-StatetoStateCapacity_Jan2026.xlsx

Workbook contents: units are million cubic feet per day (MMcf/d); updated annually; updated-date serial 46053 = 2026-01-31; release-date serial 46056 = 2026-02-03. Internal file name on the contents sheet is `EIA-StatetoStateCapacity.xlsx`. Sources line: public press releases and state and federal agency websites, including the Federal Energy Regulatory Commission. January 2026 note: updated from the EIA Natural Gas Pipeline Projects tracker published in January 2026. Contact on the sheet: Eulalia.Munoz-Cortijo@eia.gov.

The data sheet is **Pipeline State2State Capacity**. Column names in row 2:

`year`, `Pipeline`, `Region From`, `Region To`, `State From`, `County From`, `State To`, `County To`, `Capacity (mmcfd)`, `Notes`

Opened file: **19,311** data rows, year values from **1990 through 2025** (33 distinct years). For **2025**: **664** rows and **171** distinct `Pipeline` values. The sum of `Capacity (mmcfd)` on those 2025 rows is **589,777**. That sum adds border crossings. It is not a national system capacity, and the notes say capacity may be combined when segments share the same state-to-state connection. The notes cell still says “13,000+” crossings; the sheet row count above is what is in the file.

Other sheets are pivots and lookups built from that page: Contents, Major Pipeline Summary, Inflow By Region, Outflow By Region, Region to Region Capacity Map, Inflow By State, Outflow By State, Inflow By State and Pipeline, Outflow By State and Pipeline, Regions, State2StateAIMMS, Pipeline State2State CapacityH, InFlow Single Year, Outflow Single Year.

Major Pipeline Summary header row: `Pipeline`, `Segment`, `State From`, `State To`, then one column per year. The 2025 values on the first three Algonquin Gas Transmission rows are 1,625, 1,830, and 1,235 MMcf/d.

`Regions` columns: `States`, `State Names2`, `Regions` (codes such as AB / Alberta / Canada).

There is no diameter column and no latitude/longitude.

Prior releases linked from the same EIA page include `EIA-StatetoStateCapacity_Jan2025.xlsx` and `EIA-StatetoStateCapacity_Feb2024.xlsx`, under https://www.eia.gov/naturalgas/pipelines/

## 4. Other public layers suitable for a research map

### EIA Energy Atlas

The atlas home page is https://atlas.eia.gov/ and https://www.eia.gov/maps/ points users there. A public search of the EIA ArcGIS organization (`orgid:FGr1D95XCGALKXqM`, “natural gas”) on 2026-09-26 did not return feature services for pipeline centerlines, LNG terminals, underground storage facilities, or processing plants. It did return symbol images with those titles, and one polygon service:

- Natural Gas Storage Regions (regions used by the Weekly Natural Gas Storage Report, classification date 2015-11-19): https://services7.arcgis.com/FGr1D95XCGALKXqM/arcgis/rest/services/Natural_Gas_Storage_Regions/FeatureServer
- License text on that item: **None (public use)**. Attribute U.S. Energy Information Administration. These are storage regions, not storage fields.

Listing the atlas hub content group returned HTTP 403, so this is not a full inventory of every atlas page.

### Current EIA attribute tables (no coordinates)

Natural gas pipeline projects, August 2026, HTTP 200, **1,165,018 bytes**:

https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx

Sheet **Natural Gas Pipeline Projects** columns: `Last Updated Date`, `Project Name`, `Pipeline Operator Name`, `Project Type`, `Status`, `Completed Date`, `Year In Service Date`, `State(s)`, `Beg_State`, `End_State`, `Region(s)`, `Beg_Region`, `End_Region`, `Thru_Region`, `Cost (millions)`, `Miles`, `Additional Capacity (MMcf/d)`, `Pipeline Diameter (Inches)`, `Pipeline Type`, `Authority`, `Docket/Permit  Number`, `Crosses State Border`, `Notes`, `Demand Served`. Release date on the contents sheet is 2026-08-04 (serial 46238). This is projects, not the existing centerline. It does carry diameter and incremental MMcf/d.

U.S. liquefaction capacity, 2Q 2026, HTTP 200, **44,287 bytes**:

https://www.eia.gov/naturalgas/importsexports/liquefactioncapacity/U.S.liquefactioncapacity_2026_Q2.xlsx

Sheet **Existing & Under Construction** (row 2 headers, with Bcf/d and Mtpa unit subheaders in row 3): `Project name`, `Train`, `Baseload nameplate capacity per Train`, `Peak nameplate capacity per Train`, `Project status`, `In-service date`, `Date of the start of commercial service`, `Location (U.S. state)`, DOE-authorized export quantity columns and docket numbers (FTA and non-FTA), `FERC-authorized export quantity`, `FERC docket number`, `Project type`, `Operator`. Release date 2026-06-30. Location is a state, not a point. Sabine Pass Train 1 is stored as 0.59 Bcf/d baseload and 4.5 Mtpa.

### NACEI point layers (public, older)

North American Cooperation on Energy Information, with U.S. DOE, Natural Resources Canada, and Mexico’s energy ministry. Map service:

https://geoappext.nrcan.gc.ca/arcgis/rest/services/NACEI/energy_infrastructure_of_north_america_en/MapServer

Use statement on the service: free and unrestricted if the source is acknowledged as “North American Cooperation on Energy Information (NACEI).” Open Government Portal license: **Open Government Licence – Canada**. Catalog records were last modified 2021-05-19. The files are a 2017 extract, not a 2026 atlas refresh.

| Layer | Direct downloads | Vintage on the catalog | Feature count queried 2026-09-26 |
| --- | --- | --- | --- |
| Natural gas pipeline border crossings (MapServer/2) | [shp](https://ftp.maps.canada.ca/pub/nacei_cnaie/energy_infrastructure/BorderCrossingsNaturalGas_NorthAmerica_201708_SHP.zip), [xlsx](https://ftp.maps.canada.ca/pub/nacei_cnaie/energy_infrastructure/BorderCrossingsNaturalGas_NorthAmerica_201708.xlsx) | Published 2017-11-21; coverage 2017-01-01 to 2017-06-01 | 99, and all 99 match United States in `Country`, `FrmCountry`, or `ToCountry` |
| LNG terminals (MapServer/5) | [shp](https://ftp.maps.canada.ca/pub/nacei_cnaie/energy_infrastructure/LNG_ImportExportTerminals_NorthAmerica_201708_SHP.zip), [xlsx](https://ftp.maps.canada.ca/pub/nacei_cnaie/energy_infrastructure/LNG_ImportExportTerminals_NorthAmerica_201708.xlsx) | Coverage 2016-01-01 to 2017-07-01; copyright “August 2017” | 15 North America, **11** `Country = 'United States'` |
| Underground storage (MapServer/37) | [shp](https://ftp.maps.canada.ca/pub/nacei_cnaie/energy_infrastructure/NaturalGasUndergroundStorage_NorthAmerica_201701_SHP.zip), [xlsx](https://ftp.maps.canada.ca/pub/nacei_cnaie/energy_infrastructure/NaturalGasUndergroundStorage_NorthAmerica_201701.xlsx) | Coverage 2004-01-01 to 2016-12-01 | 448 North America, **391** United States |
| Processing plants (MapServer/4) | [shp](https://ftp.maps.canada.ca/pub/nacei_cnaie/energy_infrastructure/NaturalGasProcessingPlants_NorthAmerica_201708_SHP.zip), [xlsx](https://ftp.maps.canada.ca/pub/nacei_cnaie/energy_infrastructure/NaturalGasProcessingPlants_NorthAmerica_201708.xlsx) | Coverage 2014-01-01 to 2017-08-01 | 1,278 North America, **551** United States |

Catalog pages:

- https://open.canada.ca/data/en/dataset/e313db89-4219-4a5e-a543-772a86068710
- https://open.canada.ca/data/en/dataset/e08eec16-7c7a-4253-9bee-ea640d400a54
- https://open.canada.ca/data/en/dataset/07b63e0e-09bb-4c4f-b057-63a58d40553a
- https://open.canada.ca/data/en/dataset/636b9550-3700-4e66-8259-5cfc8159a784

Fields:

- Border crossings: `Pipeline`, `Owner`, `Latitude`, `Longitude`, `City`, `County`, `StateProv`, `FrmState`, `FrmCountry`, `ToState`, `ToCountry`, `NumPipes`, `Diam_Inch`, `MaxOP_psi`, `Vol_MMcfd`, `Source`, `Period`, plus metric twins. `Diam_Inch` and `Vol_MMcfd` are strings.
- LNG: `Facility`, `Owner`, `Operator`, `Latitude`, `Longitude`, `City`, `County`, `StateProv`, `Address`, `ImpExp` (Import, Export, Import / Export), `Regas_Bcfd`, `Liq_Bcfd`, `Stora_MMcf`, `Source`, `Period`, plus MTPA and volume twins.
- Storage: `FieldName`, `Reservoir`, `Owner`, `Latitude`, `Longitude`, `City`, `County`, `StateProv`, `FieldType`, `Base_MMcf`, `Work_MMcf`, `Total_MMcf`, `Deli_MMcfd`, `Source`, `Period`, plus km³ twins.
- Processing plants: `Facility`, `Owner`, `Operator`, `Latitude`, `Longitude`, `City`, `County`, `StateProv`, `Address`, `Capa_MMcfd`, `Source`, `Period`, `Capa_km3d`.

MapServer layer 2 is the 99 border-crossing points, not the 32,961-feature transmission network.

## 5. Recommended ingest

Download these two files first.

1. **Centerlines, shapefile.** `natural-gas-interstate-and-intrastate-pipelines-shapefile.zip` (2.9 MB) from https://www.datalumos.org/datalumos/project/239743/version/V1/view. Public Domain Mark. If a live endpoint is easier than the catalog download, page the NETL GeoJSON query in section 1 (`resultOffset` step of 2,000, `outSR=4326`). Expect about 33,000 line features. Use the DOT service only if `Status` is required; on 2026-09-26 every feature was `Operating`.
2. **Capacity, xlsx.** https://www.eia.gov/naturalgas/pipelines/EIA-StatetoStateCapacity_Jan2026.xlsx (4,115,317 bytes). Read the sheet `Pipeline State2State Capacity`. Keep year 2025 as the current cross-section (664 rows, 171 pipeline names).

Do not join those two on a shared key. The centerline has no pipeline name. `Operator` is a 50-character company string and will not match `Pipeline` reliably. Store capacity crossings separately. Leave diameter and MMcf/d null on drawn segments.

Optional later, not part of the first two downloads: NACEI shapefiles for points (2016–2017 vintage), the August 2026 projects workbook for new diameter and incremental capacity, and the 2Q 2026 liquefaction workbook for current export capacity by state and train.

### Field mapping

**pipelines** (one row per 2025 `Pipeline` string, 171 names in the file checked):

| Column | Source field |
| --- | --- |
| name | `Pipeline` |
| operator | same string; this workbook does not split owner and operator |
| capacity is not a pipeline total | do not store the 589,777 MMcf/d sum on the pipeline row |
| source | `eia_state_to_state_jan2026` |

**pipeline_segments** (one row per centerline part):

| Column | Source field |
| --- | --- |
| source_fid | `fid` / `FID` |
| name | null |
| operator | `operator` / `Operator` |
| type | `typepipe` / `TYPEPIPE` (`Interstate`, `Intrastate`, `Gathering`) |
| status | `status` from the DOT service, if loaded; otherwise null |
| length_miles | `miles`, or length from geometry |
| length_km | `km` on the NETL service |
| capacity_mmcfd | null |
| diameter_in | null |
| geom | polyline, store as WGS84 (EPSG:4326) |

**pipeline crossings** (add this table; it is the capacity fact, not a centerline):

| Column | Source field |
| --- | --- |
| year | `year` |
| pipeline_name | `Pipeline` |
| region_from, region_to | `Region From`, `Region To` |
| state_from, county_from | `State From`, `County From` |
| state_to, county_to | `State To`, `County To` |
| capacity_mmcfd | `Capacity (mmcfd)` |
| notes | `Notes` |

**storage** (NACEI, filter `Country = United States`, 391 points):

| Column | Source field |
| --- | --- |
| name | `FieldName` |
| owner | `Owner` |
| reservoir | `Reservoir` |
| field_type | `FieldType` |
| base_gas_mmcf | `Base_MMcf` |
| working_gas_mmcf | `Work_MMcf` |
| total_capacity_mmcf | `Total_MMcf` |
| max_delivery_mmcfd | `Deli_MMcfd` |
| state | `StateProv` |
| period | `Period` |
| geom | point from `Latitude`, `Longitude` |

**lng_terminals**: use NACEI for the point (11 U.S. points) and the 2Q 2026 liquefaction workbook for current capacity. Do not copy 2017 `Liq_Bcfd` into the current capacity column.

| Column | Source field |
| --- | --- |
| name | NACEI `Facility`; match loosely to workbook `Project name` |
| owner, operator | NACEI `Owner`, `Operator`; workbook `Operator` is current |
| trade_role | NACEI `ImpExp` |
| state | workbook `Location (U.S. state)` or NACEI `StateProv` |
| baseload_bcfd, baseload_mtpa | workbook columns C and D |
| status | workbook `Project status` |
| geom | NACEI latitude/longitude only |

**processing_plants** (NACEI, 551 U.S. points):

| Column | Source field |
| --- | --- |
| name | `Facility` |
| owner | `Owner` |
| operator | `Operator` |
| capacity_mmcfd | `Capa_MMcfd` |
| state | `StateProv` |
| period | `Period` |
| geom | point from `Latitude`, `Longitude` |

## License and access

- EIA workbook and the EIA storage-regions item: public government data. The storage-regions item says “None (public use).” Attribute the U.S. Energy Information Administration. No warranty is stated on that item.
- DataLumos centerline zip: Public Domain Mark. Cite the DOI above.
- DOE NETL and DOT feature services: public Query, blank copyright text, EIA as the compiler. Prefer these over the Esri view.
- Esri Living Atlas copy: Esri Master License Agreement, and it drops Gathering lines.
- HIFLD Secure / the old GeoPlatform hub: **restricted**. Account, profile, and Data Use Agreement required. Not used here.
- NACEI files and map service: Open Government Licence – Canada, with the NACEI acknowledgement. Geometry and capacities are from about 2016–2017.
