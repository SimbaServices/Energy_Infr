# U.S. natural gas hubs and public prices

Retrieved 2026-09-26 from public pages only. No Platts, S&P, or other login-gated terminals were used. Prices and coordinates below are copied from fetched files or pages. Where a location is only a place name, or a secondary page gives an approximate point, that is labeled.

## Units

Hub spot prices in the EIA Henry Hub series, the (discontinued) Natural Gas Weekly Update, and FRED copies of the EIA series are **dollars per million Btu ($/MMBtu)**.

EIA citygate (`N3050US3`) and wellhead (`N9190US3`) prices are **dollars per thousand cubic feet ($/Mcf)**. Those units are not the same as $/MMBtu. A Mcf-to-MMBtu conversion needs a heat-content assumption, and heat content is not constant.

Published assumptions, not a single identity:

- EIA FAQ “How do I convert natural gas prices…” (https://www.eia.gov/tools/faqs/faq.php?id=45) uses the 2025 U.S. average heat content of natural gas delivered to end-use sectors, about **1,037 Btu per cubic foot**. Under that assumption, 1 Mcf = 1.037 MMBtu, and **$/Mcf divided by 1.037 = $/MMBtu**. The reverse is $/MMBtu multiplied by 1.037.
- EIA’s energy conversion calculator (https://www.eia.gov/energyexplained/units-and-calculators/energy-conversion-calculators.php) uses **1 cubic foot = 1,036 Btu**, described there as the U.S. average for natural gas delivered to consumers in 2026 (an estimate). That implies 1 Mcf = 1.036 MMBtu.
- EIA Today in Energy (https://www.eia.gov/todayinenergy/detail.php?id=63144) reported the 2023 national average for dry natural gas at 1,036 Btu/cf and Texas at 1,018 Btu/cf. Produced and delivered gas should not be forced onto one factor.

This note does not convert citygate or wellhead observations into $/MMBtu.

## Latest confirmed prices

### Henry Hub spot (EIA), $/MMBtu

| Observation | Value | Date in the file | Series |
| --- | --- | --- | --- |
| Latest daily | 2.90 | 2026-09-22 | `RNGWHHD` daily |
| August 2026 monthly average | 2.78 | 2026-08-15 (EIA’s mid-month stamp) | `RNGWHHD` monthly |

Daily workbook contents, downloaded 2026-09-26 from https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDd.xls : latest data for 9/22/2026, release date 9/23/2026, next release 9/30/2026. Series page: https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm. The HTML history page fetched the same day still showed a 9/2/2026 release and stopped at early September; the workbook is the newer file.

Recent daily values from that workbook (blank days are weekends or holidays and are omitted from the CSV):

| Date | $/MMBtu |
| --- | --- |
| 2026-09-16 | 3.00 |
| 2026-09-17 | 2.90 |
| 2026-09-18 | 2.97 |
| 2026-09-21 | 2.93 |
| 2026-09-22 | 2.90 |

FRED series `DHHNGSP` (https://fred.stlouisfed.org/series/DHHNGSP, CSV https://fred.stlouisfed.org/graph/fredgraph.csv?id=DHHNGSP) is the same EIA series. The CSV downloaded the same day also ends at 2026-09-22 = 2.90. Monthly FRED `MHHNGSP` ends at 2026-08-01 = 2.78, matching the EIA monthly workbook (release date on that workbook: 9/23/2026).

2026 monthly Henry Hub averages from the EIA monthly workbook (https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDm.xls), $/MMBtu:

| Month | Price |
| --- | --- |
| Jan 2026 | 7.72 |
| Feb | 3.62 |
| Mar | 3.04 |
| Apr | 2.77 |
| May | 2.94 |
| Jun | 3.15 |
| Jul | 2.89 |
| Aug | 2.78 |

### U.S. citygate (EIA), $/Mcf

Series `N3050US3`, workbook https://www.eia.gov/dnav/ng/hist_xls/N3050US3m.xls, page https://www.eia.gov/dnav/ng/hist/n3050us3m.htm. Contents sheet: latest data for 6/2026, release date 8/31/2026, next release 9/30/2026. Definition (https://www.eia.gov/dnav/ng/tbldefs/ng_pri_sum_tbldef2.asp): price paid by local distribution companies for gas received from a pipeline or transmission system, from Form EIA-857. This is a national delivered-to-citygate average, not a trading-hub spot price.

| Month | $/Mcf |
| --- | --- |
| Jan 2026 | 6.74 |
| Feb | 6.55 |
| Mar | 4.80 |
| Apr | 4.33 |
| May | 4.37 |
| Jun | 5.38 |

Annual page: https://www.eia.gov/dnav/ng/hist/n3050us3a.htm. U.S. price summary table: https://www.eia.gov/dnav/ng/ng_pri_sum_dcu_nus_a.htm.

### U.S. wellhead (EIA), $/Mcf, discontinued

Series `N9190US3`, workbook https://www.eia.gov/dnav/ng/hist_xls/N9190US3m.xls, page https://www.eia.gov/dnav/ng/hist/n9190us3M.htm. The workbook’s last numeric value is **December 2012 = 3.35 $/Mcf** (stamped 2012-12-15). Later months through the sheet’s “latest data for 6/2026” are blank. EIA’s table definition says the wellhead-price estimate was discontinued as of January 2013.

### Other hubs: last public EIA spot table is January 2026

The Natural Gas Weekly Update’s last issue is the week ending Wednesday, January 21, 2026 (release January 22, 2026). EIA says that issue is the final one: https://www.eia.gov/naturalgas/weekly/. Spot prices there are $/MMBtu and are attributed to NGI’s Daily Gas Price Index.

Explicit prices in that issue:

| Point | Wednesday 2026-01-21 | Notes in the issue |
| --- | --- | --- |
| Henry Hub | 4.98 | up 1.86 from 3.12 the prior Wednesday |
| Houston Ship Channel | 4.55 | up 2.08 from 2.47 |
| Florida Gas Zone 3 | 5.03 | up 1.42 from 3.61; called a key receipt point for gas consumed in Florida |
| New York (table column) | 5.52 | column is labeled “New York,” not Transco Zone 6 NY |
| Chicago (table column) | 4.79 | |
| California composite average | 2.84 | average of NGI prices for Malin, PG&E Citygate, and Southern California Border Avg. |

The narrative says Transco Zone 6 NY **fell $1.49/MMBtu** that week. It does not print the level on January 21. No later public EIA table of these hub spots was found. The wholesale ICE page still describes natural-gas files, but the historical table fetched on 2026-09-26 links natural-gas workbooks only for 2014–2017. Electricity files continue through 2026. See https://www.eia.gov/electricity/wholesale/.

No current FERC hub-by-hub spot price table was found on the public pages used for this note.

## Coordinates

Two public point layers were queried. Neither is a surveyed meter map of 2026 price assessments.

1. **Pricing-hub approximate centers.** Anonymous query of feature service `NaturalGas_TradingHubs_US_EIA` returned 32 points. Item description: “Each hub location is identified by an **approximate central point**.” The ArcGIS item owner is a University of Kansas account, not the EIA organization. The license text is written as an EIA disclaimer. EIA’s own feature service (`services7.arcgis.com`, org `FGr1D95XCGALKXqM`, layer “Natural Gas Trading Hubs”) returned “Token Required,” so it was not downloaded. Every point in the public copy has `Period` = `202002`. Treat these as approximate centers, not legal delivery points.
   - Query: https://services2.arcgis.com/ZOdjAzAQ2B0f85zi/arcgis/rest/services/NaturalGas_TradingHubs_US_EIA/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=geojson
   - Same wording on the HIFLD Open catalog (GeoJSON zip listed, not downloaded here): https://www.datalumos.org/datalumos/project/240246/version/V1/view and https://portal.datarescueproject.org/datasets/hifld-open-natural-gas-trading-hubs/

2. **EIA/HIFLD physical market centers, mostly 2008.** Anonymous query of `HIFLD_US_Natural_Gas_Market_Hubs` (58 points). Search text says the data originate with EIA. Attributes include status and `Yearofdata`, usually 2008 or 2009. This is the older market-center inventory, not the 2026 price-index map. Several names that sound like today’s indexes (Waha, Katy, Dominion, Opal) are different points from the pricing-hub layer.
   - Query: https://services2.arcgis.com/LYMgRMwHfrWWEg3s/arcgis/rest/services/HIFLD_US_Natural_Gas_Market_Hubs/FeatureServer/0/query?where=1%3D1&outFields=*&returnGeometry=true&outSR=4326&f=geojson

Latitude north, longitude west as negative. Pricing-layer numbers are the attribute fields.

| Hub | Coordinates | Status |
| --- | --- | --- |
| Henry Hub | Pricing/HIFLD market center: 29.895494663, -92.063093854 (Erath; HIFLD county spelled Vermillion). Wikipedia, fetched 2026-09-26: 29.89861, -92.06861 (https://en.wikipedia.org/wiki/Henry_Hub). | Published points. The two sources differ by a few hundred meters. Use the EIA/HIFLD point for a map that follows that layer; label Wikipedia separately. |
| Waha | Pricing layer: 31.5819732588, -103.189521718. | Approximate center. HIFLD has several older Waha sites in Pecos or Reeves County, not this coordinate. See pipeline section. |
| Katy | Pricing layer: 29.750094818, -95.786092891. | Matches the HIFLD **Katy Storage Center** (ENSTOR; Fort Bend / “Weller” county; status operational, year of data 2008), not the separate **Katy (DCP) Hub** at 29.8331, -95.8512 (Waller County; year of data 2003). |
| Houston Ship Channel | Unknown. | EIA describes it as southeastern Texas in the Port of Houston (Today in Energy, https://www.eia.gov/todayinenergy/detail.php?id=63504). HIFLD’s inactive “Houston Hub” (29.774, -95.3936, Harris County, inactive 2003) is not identified as the Ship Channel price. |
| Chicago Citygate | Pricing layer: 41.7934361818, -87.9509282628. | Approximate center. HIFLD **Chicago Hub** (Enerchange / Nicor) is a different point: 41.5002, -88.2639. |
| Dominion South | Pricing layer: 40.4314455623, -79.6547956576. | Approximate center, still named Dominion South in that layer. |
| Eastern Gas South | No separate point. | EIA (same Today in Energy article) says Eastern Gas South was formerly Dominion South. Mapping it on the Dominion South approximate center is an assumption, not a new surveyed point. |
| TETCO M2 | Pricing layer “Texas Eastern M-2 (Receipts)”: 39.8767865321, -81.069178566. | Approximate center. Distinct from Texas Eastern M3 at 40.3756377447, -74.9400105729. EIA’s ICE product list uses **TETCO-M3**, not M2. |
| Algonquin Citygate | Pricing layer: 42.3042679484, -71.0873265081. | Approximate center. EIA text places the index with Boston and New England. |
| Transco Zone 6 NY | Pricing layer: 40.6924592569, -74.1524500979. | Approximate center. A separate “Transco Zone 6 non-NY” point is 40.3155431536, -74.7762026768. |
| SoCal Border | Pricing layer: 34.6909168697, -114.599678812. | Approximate center. Not the same point as SoCal Citygate. |
| SoCal Citygate | Pricing layer: 34.0489226583, -117.443841313. | Approximate center. EIA text: Los Angeles Basin. |
| PG&E Citygate | Pricing layer: 38.404894966, -121.913986787. | Matches HIFLD **Golden Gate Center** (California Gas Transmission; platform note “NGI, Gas Daily PG&E Citygate”). |
| Opal | HIFLD **Opal Hub**: 41.7684, -110.399 (Lincoln County, WY; Williams Field Services; operational 2008). Pricing layer **“Kern River Opal”**: 41.8367436739, -110.223184396. | Two published points. Do not treat them as one location. WyoHistory.org says the Opal plant is in Lincoln County, about 15 miles east of Kemmerer; that page does not give lat/lon (https://www.wyohistory.org/field-trips/opal-hub). |
| Cheyenne | Pricing layer and HIFLD **Cheyenne Hub**: 40.940693404, -104.79598979. | HIFLD state field is CO, county Weld, city field “Fort Collins,” administrator Colorado Interstate Gas, status operational, year of data 2008. |
| Ventura | Pricing layer: 43.1847784838, -93.4968330768. | Approximate center. Pipeline operator is not in that layer’s attributes. |
| Mich Con Citygate | Pricing layer “MichCon”: 42.1444715125, -83.3768831871. | Approximate center. |
| Dawn | Unknown. | Canadian. EIA’s 2008 market-center table places the Dawn Market Center in Ontario (Spectra Energy / Unionline; Dawn storage pools). It is not in either downloaded point file. |
| AECO | Unknown. | Canadian, commonly paired with Henry Hub as the Alberta benchmark. EIA 2008 table: AECO-C Hub, Alberta, Encana. Not in either downloaded point file. |
| Carthage | HIFLD only: 32.1595942775877, -94.2788931592213 (attribute 32.1596, -94.2789). | Panola County, TX. DCP Midstream. Status operational, year of data 2008. Not in the 32-point pricing layer. |
| NGPL Midcontinent | Pricing layer: 37.5860701365, -99.9332808651. | Approximate center. HIFLD **Mid-Continent Center** (ONEOK, Kansas) is a different point: 37.8699, -97.7721. |
| El Paso San Juan | No point with that name. | Nearest published physical hub in the HIFLD file is **Blanco Hub**, San Juan County, NM: 36.6863941986891, -107.956989551965 (attribute 36.6864, -107.957). Administrator Transwestern. Status operational, year of data 2009. Notes say it is a receipt/delivery operation rather than a formal hub, and the trading platform field says “Intercontinental Exch (San Juan).” Do not assume Blanco equals the El Paso San Juan price index. |
| Florida Gas Zone 3 | Unknown. | Named in the January 2026 EIA weekly narrative and in the public ICE product list. No lat/lon in the layers downloaded. |
| Transco Station 85 | Street address published; coordinates not surveyed here. | EPA/ADEM public notice: Transcontinental Gas Pipe Line Company, LLC, Compressor Station 85, **600 Pine View Road, Butler, Choctaw County, Alabama 36904** (https://www.epa.gov/system/files/documents/2025-02/a230021n_2_00pn.pdf). Wikimapia lists 32°3'25"N, 88°21'39"W. That coordinate is a **secondary, crowdsourced estimate**, not an agency survey (http://wikimapia.org/22441052/Transco-Compressor-Station-85). The pricing layer’s “Transco Zone 4” point (32.0721735693, -88.3788671754) is nearby but is not labeled Station 85. |

Other approximate centers in the same 32-point pricing layer, if useful on the map: Sumas 49.000494299, -122.219984774 (border; HIFLD lists the Sumas Center in British Columbia); Malin 42.033794638, -121.37198636; El Paso Permian 31.9610749569, -103.129344009; NGPL Texok zone 33.116534091, -94.2033229871; Agua Dulce 27.7488987587, -97.6254036216; Northern Natural Demarc 39.5314213619, -97.2620816888; Columbia Gas Appalachia 39.8978991256, -80.1930059354; Transco Zones 3, 4, and 5 as stored in `natural_gas_trading_hubs_approx.csv`.

## Which pipelines feed which hubs

Public documentation is partial and mostly older than the current pipe grid. EIA’s pipeline project spreadsheet (https://www.eia.gov/naturalgas/data.php#pipelines, August 2026 file linked from that page) is a project inventory, not a hub interconnect list.

### EIA market-center inventory (through about 2008–2009)

Source text: “Natural Gas Market Centers: A 2008 Update” (https://www.eia.gov/naturalgas/articles/mktctrsindex.php) and the EIA pipeline atlas page that cites the Natural Gas Market Hubs Database as of April 2009 (https://www.eia.gov/naturalgas/archive/analysis_publications/ngpipeline/MarketCenterHubsMap.html). Operator names below are those 2008/2009 attributes, not a claim about the 2026 operator.

| Place | What the public inventory says |
| --- | --- |
| Henry Hub | Sabine Hub Services / Sabine Pipeline. Header market center, started 1988, Erath, Louisiana. The report says customers used **11 interconnecting pipeline systems** and that Jefferson Island salt storage is the associated storage. It does not name all 11 in the portion reviewed. Interconnect capacity had risen about 50 percent from 2003 without adding pipelines. |
| Waha | Several sites, not one pipe. **Waha (EPGT) Texas Hub**: Enterprise Products Pipeline, production hub, Pecos County, operational in the 2008 file. **Waha (DCP/Atmos)**: DCP Midstream / Atmos Pipeline–Texas, Pecos County, operational in that file; notes say it provided access to the Guadalupe system west-to-east. **Waha (Atmos)**: inactive 2005. **Waha (Encina)**: Sid Richardson, inactive 2008. |
| Katy | **Katy (DCP)** on Guadalupe Pipeline (DCP), Waller County. **Katy Storage Center**, ENSTOR, 8-mile header, Fort Bend County. |
| Carthage | DCP, east Texas, Panola County. Notes say it mainly delivers tailgate gas from the East Texas plant. |
| Cheyenne Hub | Colorado Interstate Gas header. HIFLD notes: at the Cheyenne compressor station; “4 pipelines + CIG”; Weld County. |
| Opal Hub | Williams Field Services, at the Opal plant, Lincoln County, Wyoming. A separate inactive “Rocky Mountain Center” was administered for Northwest Pipeline at Opal and was inactive in 1999. |
| Chicago Hub | Enerchange, operator listed as Northern Illinois Gas (Nicor). Not a named list of the seven interstates in this table. |
| Dominion Hub | Dominion Transmission, entire-pipeline market center. Notes call the prices “North and South pricing points.” This is the older center, not a coordinate for today’s Eastern Gas South index. |
| Dawn | Ontario. Spectra Energy, Unionline, started 1985, 18 Dawn storage pools. Canadian. |
| AECO-C | Alberta. Encana, started 1990. Canadian. |
| Blanco / San Juan | Transwestern Gas Pipeline, San Juan County, New Mexico. |
| PG&E side | Golden Gate Center, California Gas Transmission, entire pipeline; the platform field names the PG&E Citygate price. |
| SoCal side | California Energy Hub, Southern California Gas, entire pipeline. |
| Malin | Gas Transmission Northwest / PG&E Gas Transmission-Northwest. Listed as combined into the GTN market center. |

### Henry Hub pipe names from later public pages

These lists do not match each other. Neither was checked against a current Sabine tariff in this pass.

- Wikipedia (page fetched 2026-09-26): Sabine Pipe Line LLC, owned by EnLink Midstream after a 2014 purchase from Chevron. “It interconnects with nine interstate and four intrastate pipelines: Acadian, Columbia Gulf Transmission, Gulf South Pipeline, Bridgeline, NGPL, Sea Robin, Southern Natural Pipeline, Texas Gas Transmission, Transcontinental Pipeline, Trunkline Pipeline, Jefferson Island, and Sabine.” That sentence says 13 pipes and then lists 12 names.
- S&P Global’s public Henry Hub explainer (page text in search; not a downloaded Platts price): Gulf South Pipeline, Southern Natural Gas, Natural Gas Pipeline Co. of America, Texas Gas Transmission, Sabine Pipe Line, Columbia Gulf Transmission, Transcontinental Gas Pipe Line, Trunkline Gas, Jefferson Island Pipeline, and Acadian Gas. It still described Sabine as a Chevron subsidiary and did not list Bridgeline or Sea Robin.

### EIA Today in Energy, qualitative only

Article https://www.eia.gov/todayinenergy/detail.php?id=63504. No article date was on the text fetched locally. It says locations are in the U.S. Energy Atlas “Natural Gas Infrastructure and Resources” layer.

- Henry Hub: Erath, Louisiana; NYMEX physical-delivery location.
- Houston Ship Channel: southeastern Texas, Port of Houston.
- Waha: West Texas, near Permian production; prices can be below Henry Hub and have been negative when takeaway is tight.
- SoCal Citygate: Southern California / Los Angeles Basin; includes the cost of moving gas from the California border into the distribution system.
- Opal: southwestern Wyoming; Kern River Gas Transmission is described as the interstate pipeline connected to Opal that delivers Rockies gas directly to Southern California (BHE cited in the article).
- Sumas: British Columbia–Washington border pricing hub.
- Chicago Citygate: “seven major interstate pipelines” from Canada, the Southwest, and the Gulf of Mexico, not named. “Linked to three pipelines that transport natural gas from Henry Hub,” also not named.
- Algonquin Citygate: Boston and the rest of New England; constrained pipeline capacity into the region.
- Transco Zone 6 NY: New York City; named for Transcontinental Gas Pipe Line, described as the main pipeline serving the eastern seaboard.
- Eastern Gas South, formerly Dominion South: mid-Atlantic / Appalachian supply hub, usually discounted to Henry Hub when takeaway is limited.

### ICE delivery-point labels (public PDF, not prices)

https://www.ice.com/publicdocs/NA_Phys_Gas_hubs.pdf names pools rather than lat/lon. Examples visible on the public table: Henry Hub (IHT); Houston Ship Channel as the Houston Pipe Line pool; Katy–ENSTOR and Katy–Lonestar pools; Gulf Coast Express at the Waha Hub; Florida Gas Transmission Zone 3 as gas downstream of station 10. The PDF is a contract location list, not a complete interconnect inventory.

### EIA wholesale page: which gas hub is paired with which power hub

https://www.eia.gov/electricity/wholesale/ (fetched 2026-09-26). Natural-gas product names on that page:

| Region | ICE natural gas product |
| --- | --- |
| New England | Algonquin Citygates |
| PJM | TETCO-M3 |
| Midwest | Chicago Citygates |
| Texas (paired with ERCOT North) | Henry |
| Northwest | Malin |
| Northern California | PG&E - Citygate |
| Southwest | Socal-Ehrenberg |
| Southern California | Socal-Citygate |

Waha, Katy, Dominion South / Eastern Gas South, TETCO M2, Opal, Cheyenne, Ventura, Mich Con, Dawn, AECO, Carthage, NGPL Midcontinent, El Paso San Juan, Florida Gas Zone 3, and Transco Station 85 are not in that eight-hub set.

## Download URLs and local files

Saved under `data/raw/prices/` on 2026-09-26. EIA monthly and daily dates in the converted CSVs use the workbook’s Excel date, which falls on the 15th for monthly series. That is the file’s stamp for the month, not a claim that the price was observed on the 15th.

| Local file | Source URL |
| --- | --- |
| `eia_henry_RNGWHHDd.xls` and `eia_henry_hub_daily_RNGWHHD.csv` | https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDd.xls |
| `eia_henry_RNGWHHDm.xls` and `eia_henry_hub_monthly_RNGWHHD.csv` | https://www.eia.gov/dnav/ng/hist_xls/RNGWHHDm.xls |
| `eia_citygate_N3050US3m.xls` and `eia_citygate_N3050US3m.csv` | https://www.eia.gov/dnav/ng/hist_xls/N3050US3m.xls |
| `eia_wellhead_N9190US3m.xls` and `eia_wellhead_N9190US3m.csv` | https://www.eia.gov/dnav/ng/hist_xls/N9190US3m.xls |
| `fred_DHHNGSP.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=DHHNGSP |
| `fred_MHHNGSP.csv` | https://fred.stlouisfed.org/graph/fredgraph.csv?id=MHHNGSP |
| `eia_trading_hubs_alt.geojson` and `natural_gas_trading_hubs_approx.csv` | Feature query linked in the coordinates section |
| `hifld_market_hubs.geojson` and `eia_hifld_market_hubs.csv` | Feature query linked in the coordinates section |

Series pages, if you want the HTML rather than the file:

- Daily Henry Hub: https://www.eia.gov/dnav/ng/hist/rngwhhdD.htm
- Weekly Henry Hub: https://www.eia.gov/dnav/ng/hist/rngwhhdw.htm (HTML fetched the same day still showed release date 9/2/2026 and a last printed week of 2026-08-28 at 2.81; the daily workbook is newer)
- Monthly Henry Hub: https://www.eia.gov/dnav/ng/hist/rngwhhdM.htm
- Citygate monthly: https://www.eia.gov/dnav/ng/hist/n3050us3m.htm
- Wellhead monthly: https://www.eia.gov/dnav/ng/hist/n9190us3M.htm

## Not confirmed

- No public spot price on or after 2026-09-26 was found for any hub other than Henry Hub. Henry Hub’s latest **published** daily observation in the EIA workbook is 2026-09-22, not the 26th.
- No $/MMBtu observation was confirmed for Waha, Katy, Dominion South, Eastern Gas South, TETCO M2, Algonquin, Transco Zone 6 NY, SoCal, PG&E, Opal, Cheyenne, Ventura, Mich Con, Dawn, AECO, Carthage, NGPL Midcontinent, El Paso San Juan, or Transco Station 85 later than the January 21, 2026 weekly narrative, and that narrative only prints levels for the points listed above.
- Dawn and AECO coordinates, Houston Ship Channel coordinates, and Florida Gas Zone 3 coordinates were not in the public layers downloaded.
- Short-Term Energy Outlook Henry Hub figures are forecasts, not spot prints. They were not used as observations.
