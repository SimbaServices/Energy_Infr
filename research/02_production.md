# Public U.S. natural gas production

Checked 2026-09-26 from public EIA and Census pages. No login and no paywalled series. Every volume below was read from a file downloaded that day. A blank cell in an EIA workbook is reported as unpublished, not as zero.

The latest **state monthly** series is **marketed production for June 2026**. State **dry** production is annual, and the latest year with state cells filled is **2024**. The 2025 dry workbook has a U.S. total and blank state cells. Play-level dry shale rates in the September 2026 Short-Term Energy Outlook chart file run through **August 2026**.

## 1. Where the state volumes are

Natural Gas Monthly, data for June 2026, release date August 31, 2026, next release September 30, 2026:

https://www.eia.gov/naturalgas/monthly/

| Series | HTML table | Excel download | Unit | Latest period in the file |
| --- | --- | --- | --- | --- |
| U.S. supply, including dry gas | https://www.eia.gov/dnav/ng/ng_sum_sndm_s1_m.htm | https://www.eia.gov/naturalgas/monthly/xls/ngm01vmall.xls | Billion cubic feet | June 2026 |
| Gross withdrawals, selected states and Federal Gulf of America | https://www.eia.gov/dnav/ng/ng_prod_sum_a_EPG0_FGW_mmcf_m.htm | https://www.eia.gov/naturalgas/monthly/xls/ngm06vmall.xls | Million cubic feet | June 2026 |
| Marketed production, selected states and Federal Gulf of America | https://www.eia.gov/dnav/ng/ng_prod_sum_a_EPG0_VGM_mmcf_m.htm | https://www.eia.gov/naturalgas/monthly/xls/ngm07vmall.xls | Million cubic feet | June 2026 |
| Annual dry production by state (supply and disposition) | https://www.eia.gov/dnav/ng/ng_sum_snd_a_EPG0_FPD_Mmcf_a.htm | https://www.eia.gov/dnav/ng/xls/NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls | Million cubic feet | 2025 for the U.S.; 2024 for states |
| Annual marketed production | https://www.eia.gov/dnav/ng/ng_prod_sum_a_epg0_vgm_mmcf_a.htm | https://www.eia.gov/dnav/ng/xls/NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls | Million cubic feet | 2025 for EIA-914 areas; 2024 for the other individual states |

The workbook Contents sheets say the monthly data are current through 6/2026 and the annual data through 2025. Both were released 8/31/2026. In the files, a monthly date is stored as the 15th of that month and an annual date is stored as June 30 of that year. The periods in the tables below use the Contents labels (June 2026, year 2025, year 2024), not those nominal day numbers.

Monthly Energy Review Table 4.1 CSV (https://www.eia.gov/totalenergy/data/browser/csv.php?tbl=T04.01) has national gross withdrawals, marketed production (wet), NGPL, and dry production in billion cubic feet. The copy downloaded on 2026-09-26 ends at **May 2026**, so the August 31 Natural Gas Monthly is newer for June.

Local copies, all under 5 MB:

- `data/raw/production/ngm01_supply.xls`
- `data/raw/production/ngm06_gross.xls`
- `data/raw/production/ngm07_marketed.xls`
- `data/raw/production/NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls`
- `data/raw/production/NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls`
- `data/raw/production/mer_t0401.csv`
- `data/raw/production/eia_state_production_latest.csv` (state snapshot joined to Census internal points)
- `data/raw/production/eia_steo_fig43_dry_shale_bcfd.csv` (January 2009–August 2026)

The standalone figure workbook https://www.eia.gov/outlooks/steo/xls/Fig43.xlsx does not contain the plotted numbers. They are on sheet 43 of https://www.eia.gov/outlooks/steo/xls/chart-gallery.xlsx (Short-Term Energy Outlook, September 2026). The natural gas data catalog dates that shale figure to September 9, 2026: https://www.eia.gov/naturalgas/data.php

### API v2

EIA’s API requires a free key. Register at https://www.eia.gov/opendata/register.php. Technical notes: https://www.eia.gov/opendata/documentation.php. Catalog: https://www.eia.gov/opendata/.

A request with no key returns HTTP 403 `API_KEY_MISSING` before the server checks the path, including for a nonsense path. This session did not confirm child-route names.

The downloaded workbooks do publish source keys. Use those with a key in the series browser:

| Source key in the workbook | What the workbook label says |
| --- | --- |
| `N9010US2` | U.S. gross withdrawals, MMcf |
| `N9050US2` | U.S. marketed production, MMcf |
| `N9070US2` | U.S. dry production, MMcf |
| `N9010US1`, `N9050US1`, `N9060US1`, `N9070US1` | Same concepts in the national summary, billion cubic feet (`N9060US1` is natural gas plant liquids, gaseous equivalent) |

State columns use the same prefix plus a state code, for example `N9050TX2` is Texas marketed production in MMcf. The HTML path encodes the same series family: `EPG0_FGW` gross withdrawals, `EPG0_VGM` marketed production, `EPG0_FPD` dry production, `mmcf`, and `m` or `a` for monthly or annual.

## 2. Dry, gross withdrawals, and marketed production

From the Natural Gas Monthly glossary, August 2026, https://www.eia.gov/naturalgas/monthly/pdf/glossary.pdf:

- **Gross withdrawals** are the full well-stream volume, including natural gas plant liquids and nonhydrocarbon gases, and excluding lease condensate. They include royalty gas and gas used in field operations.
- **Marketed production** is gross withdrawals minus gas used for repressuring, minus gas vented and flared, minus nonhydrocarbon gases removed in treating or processing. It still includes gas used in field and processing operations.
- **Dry natural gas production** is consumer-grade gas. EIA’s glossary states it equals marketed production minus natural gas plant liquids production. Storage withdrawals are not production.

June 2026 national totals from `ngm01vmall.xls` (billion cubic feet) match that identity within rounding: marketed 3,709.286 minus plant liquids 339.784 equals 3,369.502, and the dry row is 3,369.501.

Do not label a marketed or gross cell as dry gas. State monthly dry production is not in these files. The supply-and-disposition workbook leaves every state dry cell blank for 2025 and fills the U.S. dry total only.

## 3. Volumes confirmed from the files

### United States, June 2026

Source: https://www.eia.gov/naturalgas/monthly/xls/ngm01vmall.xls

| Series | Billion cubic feet | Million cubic feet |
| --- | ---: | ---: |
| Gross withdrawals | 4,065.425 | 4,065,425 |
| Marketed production (wet) | 3,709.286 | 3,709,286 |
| Natural gas plant liquids, gaseous equivalent | 339.784 | 339,784 |
| Dry production | 3,369.501 | 3,369,501 |

The state marketed workbook’s U.S. June 2026 cell is 3,709,286.15 MMcf, the same quantity before the national summary rounds to three decimals of a billion cubic feet.

### Marketed production by area, June 2026, million cubic feet

Source: https://www.eia.gov/naturalgas/monthly/xls/ngm07vmall.xls

These are the areas EIA publishes individually each month (Form EIA-914 states, Alaska, and the Federal Gulf of America). Everyone else is one residual.

| Area | MMcf |
| --- | ---: |
| Texas | 1,092,928.866 |
| Pennsylvania | 634,166.91 |
| New Mexico | 370,931.152 |
| Louisiana | 353,917.459 |
| West Virginia | 310,557.9 |
| Oklahoma | 244,824.18 |
| Ohio | 177,705.93 |
| Colorado | 154,179.615 |
| North Dakota | 102,267.796 |
| Wyoming | 74,773.432 |
| Federal Offshore — Gulf of America | 59,572.374 |
| Alaska | 29,924.181 |
| Utah | 28,321.501 |
| Other states | 27,562.026 |
| Arkansas | 25,707.06 |
| Kansas | 9,740.31 |
| California | 8,592.94 |
| Montana | 3,612.518 |
| United States | 3,709,286.15 |

“Other states” in this monthly file, since 2006, covers Alabama, Arizona, Florida, Idaho, Illinois, Indiana, Kentucky, Maryland, Michigan, Mississippi, Missouri, Nebraska, Nevada, New York, Oregon, South Dakota, Tennessee, and Virginia. Federal Offshore Pacific is in California through 2020 and in Other states starting in 2021. The individual monthly cells for those other states are blank in the June 2026 sheet. Their latest separate marketed totals in the annual file are for **2024**, except the Other states sum, which is also filled for 2025 (354,686 MMcf).

### Annual marketed production, 2025, million cubic feet

Source: https://www.eia.gov/dnav/ng/xls/NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls

| Area | MMcf |
| --- | ---: |
| Texas | 12,656,556 |
| Pennsylvania | 7,675,792 |
| New Mexico | 4,130,971 |
| Louisiana | 3,813,990 |
| West Virginia | 3,599,989 |
| Oklahoma | 2,877,738 |
| Ohio | 2,100,726 |
| Colorado | 1,869,619 |
| North Dakota | 1,197,922 |
| Wyoming | 938,131 |
| Federal Offshore — Gulf of America | 706,233 |
| Other states | 354,686 |
| Alaska | 368,956 |
| Utah | 336,533 |
| Arkansas | 323,323 |
| Kansas | 122,273 |
| California | 111,955 |
| Montana | 43,718 |
| United States | 43,229,110 |

### Dry production by state, 2024, million cubic feet

Source: https://www.eia.gov/dnav/ng/xls/NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls

This is the latest year with state dry cells filled. The 2025 row in the same file is U.S. only: **39,287,583 MMcf**. U.S. dry production in 2024 was **37,724,931 MMcf**.

Largest states in 2024:

| Area | Dry production, MMcf |
| --- | ---: |
| Texas | 10,054,195 |
| Pennsylvania | 7,299,117 |
| Louisiana | 3,598,072 |
| New Mexico | 3,329,399 |
| West Virginia | 3,112,501 |
| Oklahoma | 2,487,492 |
| Ohio | 2,082,466 |
| Colorado | 1,633,009 |
| Wyoming | 998,117 |
| North Dakota | 948,321 |
| Federal Offshore — Gulf of America | 592,862 |
| Arkansas | 355,170 |
| Alaska | 350,833 |
| Utah | 291,928 |

The same file has a 2024 dry figure for every other producing state that EIA lists, including very small volumes (Missouri 1 MMcf, Nevada 4, Maryland 5). Those rows are in `eia_state_production_latest.csv`. Onshore and state-offshore splits sit inside the state total in the workbook and are not repeated in that CSV. Federal offshore is kept, because it is not inside a state total.

### Dry shale gas by formation, August 2026

Source: sheet 43 of https://www.eia.gov/outlooks/steo/xls/chart-gallery.xlsx, titled “Dry shale natural gas production by formation,” Short-Term Energy Outlook, September 2026.

Sheet 43 does not print a unit. STEO Table 10b in the same outlook labels shale dry natural gas production in **billion cubic feet per day**: https://www.eia.gov/outlooks/steo/tables/pdf/10btab.pdf and https://www.eia.gov/outlooks/steo/report/natgas.php. The monthly rates below are on that scale. The one-page PDF did not extract as an aligned table, so quarterly cells from Table 10b are not repeated here.

Months after August 2026 are stored as zero through December 2027. Those zeros are not production and are omitted from the CSV. The sheet does not mark which of the nonzero months are estimates versus settled history. EIA’s data catalog calls the figure “estimated monthly production derived from state administrative data.”

| Formation | August 2026, billion cubic feet per day |
| --- | ---: |
| Marcellus | 27.126 |
| Permian | 23.251 |
| Haynesville | 14.479 |
| Utica | 6.756 |
| Eagle Ford | 4.304 |
| Rest of U.S. | 3.907 |
| Niobrara-Codell | 2.941 |
| Bakken | 2.848 |
| Woodford | 2.62 |
| Mississippian | 2.307 |
| Barnett | 1.475 |
| Fayetteville | 0.679 |

There is no single “Appalachia” column. Adding the published Marcellus and Utica rates gives 33.882 billion cubic feet per day. That sum is arithmetic on the two cells, not an EIA total. There is also no Anadarko column. Woodford and Mississippian are the named formations in this figure that sit in that part of the Mid-Continent. Older state shale-gas tables (https://www.eia.gov/dnav/ng/NG_PROD_SHALEGAS_S1_A.htm) stop at 2021 and were released December 30, 2022, so they are not the current play series.

## 4. Map points

### States

Census does not ship a GeoJSON for the 2024 cartographic boundaries. The 2024 naming note lists shapefile, geodatabase, geopackage, and KML: https://www2.census.gov/geo/tiger/GENZ2024/2024_file_name_def.pdf. Landing page: https://www.census.gov/geographies/mapping-files/time-series/geo/cartographic-boundary.html.

Direct files that returned HTTP 200 on 2026-09-26:

| File | URL | Size reported by the server |
| --- | --- | ---: |
| States, 1:20,000,000 shapefile | https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_20m.zip | about 183 KB |
| States, 1:5,000,000 shapefile | https://www2.census.gov/geo/tiger/GENZ2024/shp/cb_2024_us_state_5m.zip | 1,122,055 bytes |
| States, 1:20,000,000 KML | https://www2.census.gov/geo/tiger/GENZ2024/kml/cb_2024_us_state_20m.zip | 158,066 bytes |

State FIPS and an interior point are in the 2024 national states gazetteer (tab-delimited, interior points in `INTPTLAT` and `INTPTLONG`):

https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_Gaz_state_national.zip

Index page (the Census URL uses the spelling “gazetter”): https://www.census.gov/geographies/reference-files/2024/geo/gazetter-file.html

Those interior points are inside the state polygon. They are the right pin when a geometric center would fall outside, as with Michigan or Hawaii. A local copy of the zip is `data/raw/production/2024_Gaz_state_national.zip`. The same coordinates are joined onto `eia_state_production_latest.csv`.

TIGERweb also serves January 1, 2024 state polygons as GeoJSON, including `INTPTLAT`, `INTPTLON`, `CENTLAT`, and `CENTLON`. One Texas query on 2026-09-26 returned an interior point of +31.4347032, −099.2818238, which matches the gazetteer at the printed precision. Texas alone was about 2.5 MB of GeoJSON, so this is the detailed boundary, not the 1:20,000,000 file.

https://tigerweb.geo.census.gov/arcgis/rest/services/TIGERweb/tigerWMS_ACS2024/MapServer/80/query?where=1%3D1&outFields=STATE,NAME,STUSAB,INTPTLAT,INTPTLON&returnGeometry=true&outSR=4326&f=geojson

`STATE` is the two-digit FIPS code. Federal offshore areas have no state FIPS and no gazetteer point.

Interior points for the largest June 2026 producers:

| State | FIPS | Latitude | Longitude |
| --- | --- | ---: | ---: |
| Texas | 48 | 31.434703 | −99.281824 |
| Pennsylvania | 42 | 40.904604 | −77.827523 |
| New Mexico | 35 | 34.434684 | −106.131618 |
| Louisiana | 22 | 30.708319 | −91.604621 |
| West Virginia | 54 | 38.647285 | −80.618327 |
| Oklahoma | 40 | 35.590081 | −97.486779 |
| Ohio | 39 | 40.414930 | −82.711997 |
| Colorado | 08 | 38.993767 | −105.508712 |
| North Dakota | 38 | 47.442174 | −100.460826 |
| Wyoming | 56 | 42.989659 | −107.544392 |

### Plays and basins

EIA does not publish a lat/lon table of basin centroids. The agency’s maps page links an interactive atlas of major tight oil and shale gas plays in the Lower 48: https://atlas.eia.gov/apps/ac6b8a0cf7b14d9882877984364fb112/explore (from https://www.eia.gov/maps/). That app does not offer a small centroid download.

A public ArcGIS polygon layer whose description credits EIA, the U.S. Geological Survey, state geological agencies, and Enverus has play names and basin names. Item metadata lists a publication date of 2019-10-15 and an abstract that says the 2021 description includes a September 2019 Delaware boundary update: https://www.arcgis.com/sharing/rest/content/items/3f001fba00dc4add8dbd00542d61e4da/info/metadata/metadata.xml

The points below are WGS84 polygon centroids returned by that service on 2026-09-26 (`returnCentroid=true`). They are pins for a schematic map, not well locations, and the polygons are older than the August 2026 production rates.

Query (no geometry, small JSON):

https://services.arcgis.com/hOpd7wfnKm16p9D9/arcgis/rest/services/Extractive_Industries/FeatureServer/1/query?where=1%3D1&outFields=Shale_play,Basin&returnGeometry=false&returnCentroid=true&outSR=4326&f=json

| Play | Basin on the polygon | Longitude | Latitude |
| --- | --- | ---: | ---: |
| Marcellus | Appalachian | −79.4573 | 40.1799 |
| Utica | Appalachian | −79.1834 | 40.8834 |
| Haynesville-Bossier | TX-LA-MS Salt Basin | −94.0702 | 32.0252 |
| Bakken | Williston | −103.2601 | 48.0831 |
| Eagle Ford | Western Gulf | −98.7009 | 28.7842 |
| Woodford | Anadarko | −98.1016 | 35.4870 |
| Niobrara | Denver Basin | −104.4973 | 40.8736 |
| Wolfcamp | Permian | −103.6672 | 31.7545 |
| Bone Spring | Permian | −103.7165 | 31.8483 |
| Delaware | Permian | −103.7476 | 31.9799 |
| Spraberry | Permian | −101.7678 | 31.9832 |
| Barnett | Ft. Worth | −98.3712 | 32.4084 |
| Fayetteville | Arkoma | −92.9132 | 35.4128 |

The Permian is several stacked plays, so there is no single official pin. Wolfcamp, Bone Spring, and Delaware sit near each other. Spraberry is farther east. Niobrara has other polygons (Powder River, Piceance, Park, North-Central Montana, Raton); the Denver Basin row is the one that matches the DJ/Niobrara-Codell area people usually mean. A December 2023 EIA map of Lower 48 shale plays is a picture, not coordinates: https://www.eia.gov/maps/images/lower-48/shale_gas_2023.pdf
