# Public U.S. electric transmission data for a research map

Checked 2026-09-26. Public endpoints only. No logins, no HIFLD Secure, no CEII.

## Recommendation

Use the Esri Federal User Community feature service **U.S. Electric Power Transmission Lines (Archive)**. It is public, returns GeoJSON with no token, and has voltage, owner, status, and type. Filter to lines at **230 kV and above that are in service** (8,308 features). Do not pull the full 94,619-line layer.

Public-domain alternative if the app should not depend on the Esri Master License Agreement: the DataLumos snapshot of HIFLD Open transmission lines (Creative Commons Public Domain Mark 1.0). That is a file, not a live query service. Compressed GeoJSON is listed at 37.7 MB. It was not downloaded for this note.

HIFLD Open itself was deactivated on 2026-08-26. HIFLD Secure and FERC CEII were not opened.

## 1. Transmission lines

### Use this service

| | |
|---|---|
| Title | U.S. Electric Power Transmission Lines (Archive) |
| Owner | `Federal_User_Community` (Esri). Access `public`. |
| Item | https://www.arcgis.com/home/item.html?id=d4090758322c4d32a4cd002ffaa0aa12 |
| FeatureServer | https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/US_Electric_Power_Transmission_Lines/FeatureServer/0 |
| Geometry | Polyline. Query formats: JSON, geoJSON, PBF. Max 2,000 records per query. |
| Capabilities | Query, Extract, ChangeTracking |
| Stated currency | Item page: **Last Data Update 09/30/2024**. Archived; will no longer be updated. |
| Service edit date | Layer `dataLastEditDate` is 2025-08-26 (the same day HIFLD Open was deactivated). Item metadata modified 2026-06-01. |
| Feature count | 94,619 (`where=1=1`, `returnCountOnly=true`) |

Spatial reference of the service is Web Mercator (3857). Request `outSR=4326` for GeoJSON in longitude/latitude.

### Key fields observed

From the layer definition, confirmed on a two-feature GeoJSON sample:

| Field | Meaning | Sample values |
|---|---|---|
| `VOLTAGE` | Kilovolts, double | `1000`, `765`, `345`, `230` |
| `VOLT_CLASS` | Text class | `DC`, `735 AND ABOVE`, `500`, `345`, `220-287`, `100-161`, `UNDER 100`, `NOT AVAILABLE`, `SUB 100`, `Unknown` |
| `OWNER` | Owner name | `BONNEVILLE POWER ADMINISTRATION`, `APPALACHIAN POWER CO`, `NOT AVAILABLE` |
| `STATUS` | Operating status | `IN SERVICE` (73,684), `NOT AVAILABLE` (20,819), `INACTIVE` (91), `UNDER CONSTRUCTION` (25) |
| `TYPE` | Line type | `AC; OVERHEAD` (77,715), `OVERHEAD` (15,773), `AC; UNDERGROUND` (376), `UNDERGROUND` (98), `DC; OVERHEAD` (11), `DC; UNDERGROUND` (1), `NOT AVAILABLE` (645) |
| `SUB_1`, `SUB_2` | Named line ends | `CELILO` / `SYLMAR EAST`; also `UNKNOWN…` values |
| `INFERRED` | `Y`/`N` | `N` on the sampled high-voltage lines |
| `ID` | Line id, string | `200823`, `100170` |
| `SOURCE`, `SOURCEDATE` | Provenance | Present. `SOURCEDATE` is a source citation date, not the layer vintage. |
| `NAICS_CODE`, `NAICS_DESC`, `VAL_METHOD`, `VAL_DATE` | Present | Not needed for the map |

Voltage class counts (all statuses): `100-161` 44,665; `UNDER 100` 30,348; `NOT AVAILABLE` 8,822; `220-287` 7,305; `345` 2,602; `500` 815; `735 AND ABOVE` 46; `DC` 14.

`VOLTAGE >= 230` is the right numeric filter. It covers the 220–287 kV class, 345, 500, 735+, and DC, and it drops unknown voltage.

Sample returned without a token (attributes only):

- `ID` `200823`, `TYPE` `DC; OVERHEAD`, `STATUS` `IN SERVICE`, `OWNER` `BONNEVILLE POWER ADMINISTRATION`, `VOLTAGE` 1000, `VOLT_CLASS` `DC`, `INFERRED` `N`, `SUB_1` `CELILO`, `SUB_2` `SYLMAR EAST`
- `ID` `100170`, `TYPE` `AC; OVERHEAD`, `STATUS` `IN SERVICE`, `OWNER` `APPALACHIAN POWER CO`, `VOLTAGE` 765, `VOLT_CLASS` `735 AND ABOVE`, `SUB_1` `CLOVERDALE 765KV`, `SUB_2` `JACKSONS FERRY`

### Exact query for a manageable subset

8,308 features match `VOLTAGE >= 230 AND STATUS = 'IN SERVICE'`. At `resultRecordCount` 2,000 that is five pages (`resultOffset` 0, 2000, 4000, 6000, 8000). A response sets `exceededTransferLimit` when more rows exist.

```
https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/US_Electric_Power_Transmission_Lines/FeatureServer/0/query?where=VOLTAGE+%3E%3D+230+AND+STATUS+%3D+%27IN+SERVICE%27&outFields=ID,TYPE,STATUS,OWNER,VOLTAGE,VOLT_CLASS,SUB_1,SUB_2&returnGeometry=true&outSR=4326&geometryPrecision=4&maxAllowableOffset=0.01&resultRecordCount=2000&resultOffset=0&f=geojson
```

`where` text:

```
VOLTAGE >= 230 AND STATUS = 'IN SERVICE'
```

Tighter backbone, 2,832 features:

```
VOLTAGE >= 345 AND STATUS = 'IN SERVICE'
```

`maxAllowableOffset` is in degrees when `outSR=4326`. `0.01` is about 1 km. `geometryPrecision=4` is about 11 meters. A 20-feature sample with `geometryPrecision=3` and `maxAllowableOffset=0.02` was 7.6 KB. Thirty full-precision 500 kV lines (no offset) were 75 KB, about 2.5 KB each. A full-precision national pull of 94,619 lines is the multi-hundred-megabyte case. The filtered query is not.

### Bulk download

- The archive service advertises Extract, and `supportedExportFormats` includes geojson, shapefile, file geodatabase, and others. A full export is public. It was not run.
- **DataLumos / ICPSR public snapshot:** [HIFLD OPEN Transmission Lines](https://doi.org/10.3886/E240591V1). Catalog page: https://www.datalumos.org/datalumos/project/240591/view . Files listed: `transmission-lines-1-geojson.zip` 37.7 MB and `transmission-lines-1-shapefile.zip` 40.8 MB, modified 2025-11-24. Time period on the study: 2025-02-19. Marked Public. License: Creative Commons Public Domain Mark 1.0. Archived because HIFLD Open was deactivated on 2025-08-26. Not downloaded.
- Older GeoPlatform-linked service still answers, but it is a worse copy: 52,244 features, `dataLastEditDate` 2023-09-05, Query only, blank license, owner `cherndon0`. URL: https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Electric_Power_Transmission_Lines/FeatureServer/0 . The hub page still titled this “Electric Power Transmission Lines” (https://hifld-geoplatform.opendata.arcgis.com/datasets/geoplatform::electric-power-transmission-lines). Do not prefer it.
- `https://services2.arcgis.com/1cdV1mIckpAyI7Wo/arcgis/rest/services/Electric_Power_Transmission_Lines/FeatureServer` returned `Invalid URL` on this check. Do not use it.

The U.S. Energy Atlas page at https://atlas.eia.gov is a hub shell. EIA does not publish its own transmission FeatureServer. EIA’s FAQ points transmission maps to HIFLD.

## 2. Substations

No official national substation feature service was public on this check.

- Hub slugs `geoplatform::electric-substations` and `electric-substations` on `hifld-geoplatform.opendata.arcgis.com` returned a generic ArcGIS Hub page, not a dataset.
- `https://services1.arcgis.com/Hp6G80Pky0om7QvQ/arcgis/rest/services/Electric_Substations/FeatureServer/0` returned `Invalid URL`.
- Search of `Federal_User_Community` feature services for “substation” did not return a substation layer.
- **Skipped:** HIFLD Secure (GII account, profile, and annual data-use agreement). https://www.dhs.gov/gmo/hifld describes Secure as commercially licensed and controlled data.
- **Skipped:** FERC Critical Energy/Electric Infrastructure Information, including Form 715 transmission-system filings. FERC treats that material as CEII and requires a request. https://www.ferc.gov/ceii . CEII is engineering and vulnerability detail beyond the location of the infrastructure. This note did not request it.
- EIA FAQ 567 (https://www.eia.gov/tools/faqs/faq.php?id=567&t=3), as published in public search text, says EIA and HIFLD do not publish electric substation locations. A direct reload of that FAQ timed out during this check, so the wording was not re-copied from the live page.

A **third-party** feature service still returns the old HIFLD Open substation schema with no token. It is not a DHS or EIA endpoint. The item has a blank license and a blank description. Owner: `ccs3543_ut_austin`. Item `76058e9a7f034719a988f9c2a7d81935`, modified 2025-12-01. Use it only as a public republish of the former open layer, and do not present it as the current government product.

```
https://services1.arcgis.com/7DRakJXKPEhwv0fM/arcgis/rest/services/Electric_Substations/FeatureServer/0
```

Count: 75,328 points. `MAX_VOLT >= 230` returns 6,692. Missing voltage is stored as `-999999`, so a numeric filter drops those rows.

Fields observed on one GeoJSON feature: `ID`, `NAME`, `CITY`, `STATE`, `ZIP`, `TYPE`, `STATUS`, `COUNTY`, `COUNTYFIPS`, `COUNTRY`, `LATITUDE`, `LONGITUDE`, `NAICS_CODE`, `NAICS_DESC`, `SOURCE`, `SOURCEDATE`, `VAL_METHOD`, `VAL_DATE`, `LINES`, `MAX_VOLT`, `MIN_VOLT`, `MAX_INFER`, `MIN_INFER`.

Sample: `ID` `108092`, `NAME` `UNKNOWN108092`, `TYPE` `SUBSTATION`, `STATUS` `IN SERVICE`, Powhatan, Lawrence County, Arkansas. `MAX_VOLT` and `MIN_VOLT` were `-999999`. `LINES` was 0. Point at longitude `-91.13421`, latitude `36.09085`.

There is no `OWNER` field on this layer. Line end names (`SUB_1` / `SUB_2`) do not reliably join to substation `ID`.

## 3. How to keep the map small

1. Query the archive service above. Do not export all voltages.
2. Use `VOLTAGE >= 230 AND STATUS = 'IN SERVICE'` (8,308 lines). Use `VOLTAGE >= 345 AND STATUS = 'IN SERVICE'` (2,832) if the map only needs the extra-high-voltage backbone.
3. Request only `ID,TYPE,STATUS,OWNER,VOLTAGE,VOLT_CLASS,SUB_1,SUB_2`.
4. Set `outSR=4326`, `geometryPrecision=4`, and `maxAllowableOffset=0.01`.
5. Page with `resultRecordCount=2000` and `resultOffset`.
6. For a viewport, add an envelope (`geometry`, `geometryType=esriGeometryEnvelope`, `inSR=4326`, `spatialRel=esriSpatialRelIntersects`) instead of loading the country at once.
7. Do not use the 2023 GeoPlatform service as a “simplified EIA atlas” stand-in. It is the same kind of linework, smaller and older, and it has no license text.

`SUB_1` and `SUB_2` are names, including placeholders such as `UNKNOWN202159`. They are labels, not a connectivity key to a substation layer or to a gas plant.

## 4. Gas-fired power plants (demand nodes)

### Use this service

| | |
|---|---|
| Title | Power Plants in the U.S. |
| Owner | `Federal_User_Community`. Access `public`. |
| Item | https://www.arcgis.com/home/item.html?id=b063316fac7345dba4bae96eaa813b2f |
| Credits on the item | Energy Information Administration (EIA) |
| FeatureServer | https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Power_Plants_in_the_US/FeatureServer/0 |
| Layer name | `PowerPlants_US_EIA`. Point. GeoJSON. Max 2,000 records. |
| Coverage | Operable plants of 1 MW or more, including operating, standby, and short- or long-term out of service. |
| Item text | “This layer is checked monthly for updates.” Item modified 2026-09-22. Layer `dataLastEditDate` is 2025-07-01. |

Every one of the 13,446 features has `Period` = `202502` (February 2025). The monthly-check sentence on the item is not reflected in the period attribute. Source text on the sampled plant: `EIA-860, EIA-860M and EIA-923`.

### Fields observed

`Plant_Code`, `Plant_Name`, `Utility_ID`, `Utility_Na`, `sector_nam`, `Street_Add`, `City`, `County`, `State`, `Zip`, `PrimSource`, `source_des`, `tech_desc`, `Install_MW`, `Total_MW`, `Bat_MW`, `Bio_MW`, `Coal_MW`, `Geo_MW`, `Hydro_MW`, `HydroPS_MW`, `NG_MW`, `Nuclear_MW`, `Crude_MW`, `Solar_MW`, `Wind_MW`, `Other_MW`, `Source`, `Period`, `Longitude`, `Latitude`.

`NG_MW` is a double (natural-gas summer capacity, MW). `Bat_MW`, `Bio_MW`, `Geo_MW`, and `Other_MW` are strings in the schema. Primary fuels observed in the service definition include `natural gas`.

Counts:

- All plants: 13,446
- `NG_MW > 0`: 2,088 (any natural-gas capacity; this is the pipeline demand set)
- `PrimSource = 'natural gas'`: 1,983 (gas is the main fuel)

Sample, no token: Plant `56407`, West County Energy Center, Florida Power & Light Co, Florida, `PrimSource` `natural gas`, `NG_MW` 3777, `Total_MW` 3777, `Install_MW` 4263, `tech_desc` `Natural Gas Fired Combined Cycle`, point longitude `-80.3747`, latitude `26.6986`, `Period` `202502`.

### Exact gas-plant query

2,088 points fit in two pages of 2,000.

```
https://services2.arcgis.com/FiaPA4ga0iQKduv3/arcgis/rest/services/Power_Plants_in_the_US/FeatureServer/0/query?where=NG_MW+%3E+0&outFields=Plant_Code,Plant_Name,Utility_Na,State,PrimSource,NG_MW,Total_MW,Install_MW,tech_desc,Source,Period&returnGeometry=true&outSR=4326&resultRecordCount=2000&resultOffset=0&f=geojson
```

An older public copy (`PowerPlant` on `services7.arcgis.com`, owner `jshirley_TrueGrid`, data last edited 2023-06-28) is the same kind of atlas extract and is stale. Do not use it. HIFLD Open generating units (https://doi.org/10.3886/E239227V1) is a public-domain plant snapshot from the closed HIFLD Open catalog, not a current EIA layer.

### Newer generator table, not a map service

Form EIA-860M is the public monthly generator inventory (plants of 1 MW or more). Index, no login:

https://www.eia.gov/electricity/data/eia860m/

On 2026-09-26 the HTML listed workbook paths including `/electricity/data/eia860m/xls/august_generator2026.xlsx`, `october_generator2026.xlsx`, and `december_generator2026.xlsx`. A HEAD of the December file returned HTTP 503, so that file was not confirmed. Annual EIA-860 plant files, which include latitude and longitude, are linked from https://www.eia.gov/electricity/data/eia860/ . Neither workbook was downloaded. For the map, use the feature service. Use a later 860M file only if a specific month must be newer than `Period` `202502`.

These plant points are not electrically tied to a transmission segment. Proximity to a 230 kV line is a spatial overlap, not an interconnection record.

## 5. Text the map should show

**Transmission lines (Esri archive service)**

> U.S. Electric Power Transmission Lines (Archive). Source: U.S. Government. Hosted by Esri, Federal User Community. Last data update stated by Esri: September 30, 2024. This layer is archived and is no longer maintained. Use of this hosted service is under the Esri Master License Agreement. https://www.arcgis.com/home/item.html?id=d4090758322c4d32a4cd002ffaa0aa12

**Transmission lines if the app uses the DataLumos file instead**

> Oak Ridge National Laboratory and United States Department of Homeland Security. HIFLD OPEN Transmission Lines. Ann Arbor, MI: Inter-university Consortium for Political and Social Research [distributor], 2025-11-24. https://doi.org/10.3886/E240591V1 This work is marked with the Creative Commons Public Domain Mark 1.0.

**Power plants**

> Power Plants in the U.S. Source: U.S. Energy Information Administration (EIA-860, EIA-860M, and EIA-923), reporting period 202502. Hosted by Esri, Federal User Community, under the Esri Master License Agreement. https://www.arcgis.com/home/item.html?id=b063316fac7345dba4bae96eaa813b2f

EIA’s own reuse page says EIA information products may be used and distributed, and asks for an acknowledgment with a publication date, for example: “Source: U.S. Energy Information Administration (Feb 2025).” Page: https://www.eia.gov/about/copyrights_reuse.php

**Substations, only if the unofficial republish is shown**

The hosting item has no license string. Do not invent one. If those points are drawn, label them as a public republish of the former HIFLD Open substation schema (host account `ccs3543_ut_austin`, item updated 2025-12-01), not as a current DHS layer, and point readers at the HIFLD Open deactivation note. Historical HIFLD Open compilers of that schema were Oak Ridge National Laboratory, Los Alamos National Laboratory, Idaho National Laboratory, and the NGA Homeland Security Infrastructure Program Team.
