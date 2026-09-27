# Planned and recently completed U.S. natural gas pipeline projects

Research date: 2026-09-26. Figures below come from the EIA Natural Gas Pipeline Projects workbook released 2026-08-04, from EIA’s 2026-05-26 *Today in Energy* summary of an earlier tracker vintage, or from the public FERC Major Pipeline Projects Pending table fetched the same day (page stamp “As of 09/24/2026”). No projects are added from memory or trade press alone.

## Preferred source

EIA’s compilation is the practical structured dataset. It covers announced, pre-filed, applied, approved, under-construction, partly completed, on-hold, and completed transmission projects. FERC eLibrary is a public document archive (search by docket or accession number), not a project table, so it is a poor scrape target. Use EIA for the inventory and open a FERC docket only when a specific order or application is needed.

| What | URL |
| --- | --- |
| EIA natural gas data page (Pipeline projects release list) | https://www.eia.gov/naturalgas/data.php |
| Current file (stable name; this is what was downloaded) | https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects.xlsx |
| Same bytes, dated August 2026 filename | https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjectsAug2026.xlsx |
| Prior quarterly file | https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects_May2026.xlsx |
| EIA narrative snapshot (2026-05-26; tracker older than the August workbook) | https://www.eia.gov/todayinenergy/detail.php?id=67707 |
| FERC pending interstate capacity projects (HTML table, not a full inventory) | https://www.ferc.gov/industries-data/natural-gas/major-pipeline-projects-pending |
| FERC eLibrary (document search) | https://elibrary.ferc.gov/ |

The workbook Contents tab also points at https://www.eia.gov/naturalgas/data.cfm#pipelines and lists sources as FERC, trade press, company websites, and SEC filings, plus the Texas Railroad Commission pipeline-safety reports (http://www.rrc.state.tx.us/pipeline-safety/reports/) and FERC staff reports (https://ferc.gov/legal/staff-reports.asp).

### Downloaded file

- Path: `C:\Users\Sam Parker\Take_Action\US_Pipelines\data\raw\projects\EIA-NaturalGasPipelineProjects.xlsx`
- Source URL: https://www.eia.gov/naturalgas/pipelines/EIA-NaturalGasPipelineProjects.xlsx
- HTTP size: 1,165,018 bytes
- Server Last-Modified: Tue, 04 Aug 2026 12:37:12 GMT
- SHA-256: `5C278179984027F380DFA6E9BDB739DB628889DC25E6003F933B33F362EC469D`
- Contents-tab release date: 2026-08-04
- The August dated URL returned the same Content-Length (1,165,018). The May 2026 file is smaller (1,149,666) and is an older release.

EIA’s own note on the Contents tab: these figures are compiled, not surveyed; capacity that actually enters service can differ from the file; the file is not a forecast; and associated segments should not be added together or capacity will be double-counted. Gathering lines, distribution lines, and LNG marine terminals are generally excluded.

## Workbook structure and column definitions

Sheets:

- **Natural Gas Pipeline Projects** — projects from 2025 forward. 137 data rows under a header on row 2. Capacity unit: million cubic feet per day (MMcf/d). Update cadence on the Contents sheet: quarterly.
- **Historical Projects (1996-2024)** — completed history. The sheet name still says 1996–2024, but the 2026 enhancement note says non-active projects completed in 2025 were moved here. This download has 20 rows with in-service year 2025.
- **Definitions**, **Regions**, **Regions_OLD**, **State**.

Current-sheet columns (row 2), with definitions from the Definitions sheet where EIA provides them:

| Column | Definition in the file |
| --- | --- |
| Last Updated Date | Date the record was last updated |
| Project Name | Name as it appeared on press releases or government applications |
| Pipeline Operator Name | Natural gas transmission operator |
| Project Type | See type list below |
| Status | See status list below |
| Completed Date | Date completed or placed in service |
| Year In Service Date | Year placed in service, or the expected year |
| State(s) | States that gain the additional capacity |
| Beg_State / End_State | Present on the data sheet; not separately defined |
| Region(s), Beg_Region, End_Region, Thru_Region | Regions that gain capacity; region sheet defines the geography |
| Cost (millions) | Estimated cost from press releases or applications |
| Miles | Estimated mileage |
| Additional Capacity (MMcf/d) | Estimated additional capacity |
| Pipeline Diameter (Inches) | Estimated diameter |
| Pipeline Type | Interstate (FERC Natural Gas Act) or intrastate (typically state-regulated) |
| Authority | Not given a separate definition row; values in the file include FERC and TX RRC |
| Docket/Permit Number | FERC docket, or a state permit number for intrastate lines |
| Crosses State Border | Yes/No on the data sheet |
| Notes | Free text. `na` = not available; `-` = unknown |
| Demand Served | End use when known: Electric, Industrial, LDC, LNG, or a free-text mix |
| Website | Link label when EIA stored a source page |

**Project type** (Definitions): Conversion; Expansion (mainline capacity or mileage, including compression, looping, or extensions); Lateral; New Pipeline; Abandonment; Reversal (reverse flow or added bi-directional capacity); Upgrade (replacement of aging facilities that also adds capacity).

**Status** (Definitions): Announced; Pre-applied; Applied; Approved; Construction; Requested In Service; Part Completed; Completed; On Hold; Denied; Cancelled. This August file also uses **Proposed** (2 rows). That value is not on the Definitions sheet.

Current-sheet status counts: Applied 34, Construction 31, Approved 30, Announced 13, Pre-applied 10, On Hold 10, Completed 4, Part Completed 3, Proposed 2.

## How to read the August file against other public pages

EIA *Today in Energy*, 2026-05-26 (“Most planned natural gas pipeline capacity additions in 2026 and 2027 originate in Texas”), summarizes the tracker as it stood then:

- About 44.9 Bcf/d planned to enter service in the U.S. in 2026 and 2027.
- About 70% (31.6 Bcf/d) already under construction.
- More than 66% (29.7 Bcf/d) originates in Texas; Louisiana is second at 8.4 Bcf/d.
- Named then: Rio Bravo up to 4.5 Bcf/d, second half of 2026; Blackcomb 2.5 Bcf/d, third quarter 2026; Hugh Brinson 2.2 Bcf/d, phase 1 fourth quarter 2026 and phase 2 first quarter 2027; Port Arthur Louisiana Connector 2.0 Bcf/d, second half of 2026; Pelican by the end of 2027 as part of Louisiana’s 8.4 Bcf/d; Southeast Supply Enhancement 1.6 Bcf/d in 2027, Transco, Virginia to Alabama.

The August 4 workbook is later than that article. Where the article and the workbook differ, the lists below follow the workbook and say so.

FERC’s pending-projects page (fetched 2026-09-26; stamp “As of 09/24/2026”; “last updated on September 24, 2026”) lists major **interstate certificate applications that are still pending**. It leaves out abandonments, blanket-program jobs, storage, and LNG terminals that have no pipeline. It also leaves out projects that are already approved or under construction, and it leaves out Texas intrastate lines. A direct HTTP download of the page returned 403; the table text was read in a browser from the public URL above.

Several filings on that September 24 list are absent from the August 4 workbook (they were filed around or after the workbook’s last record updates): CP Express Pipeline Expansion (CP26-533, 1,900 MMcf/d, 0.19 mile, filed 2026-05-26), Franklin Farms on ETC Tiger (CP26-549, 1,000 MMcf/d, about 15 miles, LA, filed 2026-07-01), Northern Natural Gas Permian Basin Expansion (CP26-534, 361.6 MMcf/d, NM/TX, filed 2026-05-28), and Transco Leidy Access Expansion (CP26-576, 183.1 MMcf/d, PA, filed 2026-09-04). They are listed in the FERC supplement at the end. They are not treated as EIA workbook rows.

## Major open projects that change Permian, Haynesville, Appalachia, or LNG-feed capacity

Capacity is the workbook field **Additional Capacity (MMcf/d)** unless a note says otherwise. In-service year is **Year In Service Date**. Status and type are the workbook values with stray spaces removed. “Open” here means a status other than Completed, and On Hold is split out so it is not read as an active build.

Phased rows for one physical system (CP Express phases, Driftwood Line 200/300, the two MVP Southgate rows, Corpus Christi Stage III partial service) are listed as EIA recorded them. Do not add those rows into a single takeaway total.

### Permian takeaway and Permian-linked headers

| Project | Operator | Status | Type | Capacity (MMcf/d) | Expected in-service | States | What the file says |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Eiger Express Pipeline | WhiteWater Midstream | Construction | New Pipeline | 3,700 | 2028 | TX | Intrastate. Permian to the Katy Hub. Notes: upsized in Nov 2025 from 2.5 to 3.7 Bcf/d; mid-2028 in-service kept; 100% contracted. Docket field blank; partners named as ONEOK, Enbridge, and MPLX. |
| Blackfin Pipeline | WhiteWater Midstream | Construction | New Pipeline | 3,500 | 2027 | TX | Intrastate, T4-10453. Permian production to Gulf Coast markets. TX RRC: construction started 2024-10-01. Notes: in-service delayed by a compressor relocation in Conroe. Includes a short lateral toward Venture Global CP Express / CP2. |
| Blackcomb Pipeline | WhiteWater Midstream | Construction | New Pipeline | 2,500 | 2026 | TX | Intrastate, T4-10643, 365 miles. West Texas (Midland plants and Agua Blanca) to Agua Dulce. Notes: FID 2024-07-31; in-service moved from July to **November 2026**. The May 26 EIA article still said third quarter 2026. |
| Hugh Brinson Pipeline (formerly Warrior) Phase I & II | Energy Transfer LP | Part Completed | New Pipeline | 2,200 | 2026 | TX | Intrastate, T4-10370. Waha to Maypearl, plus a Midland lateral. Notes: Phase I 1.5 Bcf/d in commissioning (TX RRC and FERC PR26-71); Phase II compression to about 2.2 Bcf/d in **Q1 2027**. Connects toward Carthage and Katy. |
| Desert Southwest expansion | Transwestern | Pre-applied | Expansion | 2,300 | 2029 | NM, AZ | FERC PF26-9. Notes: Permian to Desert Southwest across TX/NM/AZ; upsized Dec 2025 to 48-inch / up to 2.3 Bcf/d; target Q4 2029; power demand in AZ/NM. |
| DeLa Express | DeLa Express LLC | Pre-applied | New Pipeline | 2,000 | 2028 | TX, LA | FERC PF24-4. Notes: about 690 miles from near Red Bluff, Loving County, TX (Permian) to Moss Bluff, Calcasieu Parish, LA, for Gulf Coast LNG; pre-filing accepted 2024-04-15; in-service targeted July 2028. |
| Saguaro Connector Pipeline and Saguaro border facility | Saguaro Connector Pipeline, LLC | Approved | New Pipeline and Lateral | 2,800 (text: “2800 (total project)”) | 2028 | TX, MX | Waha Hub to a Rio Grande border crossing in Hudspeth County, then Mexico. Docket CP23-29. Notes: design about 2.8 Bcf/d; construction not started; 2026-04-01 extension request moves completion from 2027-02-15 to **2030-02-15**, tied to Mexico LNG offtake. |
| Traverse Pipeline | WPC JV (WhiteWater/MPLX/Enbridge) + Targa | Construction | New Pipeline | 2,400 in the capacity column | 2027 | TX | Intrastate, T4-10688. **The notes say up to 1.75 Bcf/d**, bi-directional, Agua Dulce to Katy, supplied from Whistler, Blackcomb, and Matterhorn. FID 2025-04-03. This is a Gulf Coast header fed by Permian pipes, not a new Waha outlet by itself. Use 2,400 only as the capacity-column value and keep the 1.75 Bcf/d note beside it. |
| Apex | Targa Resources | On Hold | New Pipeline | 2,000 | 2027 | TX | Intrastate, T4-10456. Notes: Permian (Midland) toward Beaumont / Port Arthur; TX RRC permit had been renewed; status in the file is On Hold. |
| Forza pipeline (with Bull Run Extension) | Forza Pipeline LLC and Bull Run Pipeline LLC (Targa) | Applied | New Pipeline (Forza); Expansion (Bull Run) | 750 (Forza). Bull Run capacity cell is blank | 2028 | NM, TX | Dockets CP26-34 and CP26-35. Delaware Basin residue gas to Waha. FERC pending table, 2026-09-24: Forza 750 MMcf/d, 36 miles, filed 2025-12-03. Notes: service targeted Q2 2028. |
| Waha to Mexico (Wahalajara expansion) | ESENTIA Energy Systems | Construction | Expansion | 300 | 2027 | TX, MX | Notes: +300 MMcf/d on the existing Waha-to-Guadalajara system. Phase 1 +150 MMcf/d, FID Sept 2025, expected start Q1 2027. Mexican pipe is outside FERC. |
| Permian West Expansion | Kinder Morgan (El Paso Natural Gas) | Applied | Expansion | 82 | 2027 | TX | CP26-156. Small westbound loop from the Permian toward Willcox, AZ. Included only because the file names the basin; it is not a major Gulf-bound takeaway line. |

Gulf Coast Express Expansion (Kinder Morgan), +570 MMcf/d, Waha to Agua Dulce, is **Completed** in this workbook (in-service year 2026). It is listed under recent completions.

### Haynesville takeaway

| Project | Operator | Status | Type | Capacity (MMcf/d) | Expected in-service | States | What the file says |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Pelican Pipeline | WhiteWater Midstream | Construction | New Pipeline | 2,500 | 2027 | LA | Intrastate. Notes: Williams, LA to the Gillis Hub; FID 2024-10-31 at 1.75 Bcf/d; upsized 2025-07-30 to 42-inch / 2.5 Bcf/d; target **first half 2027**. May 26 EIA article said by the end of 2027. |
| South Mississippi Project | Energy Transfer | Announced | New Pipeline | 2,000 | 2028 | TX, LA, MS | Notes: open season late 2024 for up to 2 Bcf/d from Carthage, the Haynesville, and Perryville toward SONAT and FGT Zone 3. No FERC application as of the note. |
| Driftwood Line 200 and 300, Phases 1–3 | Driftwood LNG Pipeline LLC | Phase 1 Construction; Phases 2 and 3 Approved | New Pipeline | 2,400 / 2,200 / 1,000 | 2028 / 2029 / 2029 | LA | Docket CP21-465. Notes: Haynesville gas to the Lake Charles market. Phase capacities are stages of one Line 200 + Line 300 system whose notes give a combined design of 5.4 Bcf/d (5.7 Bcf/d seasonal max), not three independent pipes. |
| Driftwood LNG Pipeline | Driftwood LNG Pipeline LLC | Construction | New Pipeline | 4,000 | 2029 | LA | Dockets CP17-117 / CP17-118. Separate 96-mile feed line to the Woodside Louisiana LNG terminal near Carlyss, interconnecting with up to 14 interstate pipes. Notes: actively under construction; extension request to 2029-12-31. Do not add this 4,000 to the Line 200/300 phase rows without a shipper-path check. |
| Gillis Access Project Extension | TC Energy | Approved | Expansion | 1,400 | 2027 | LA | CP26-33, CP25-521. Notes: extends the 1.5 Bcf/d Gillis Access line (in service 2024) so more Haynesville gas can move through TC Energy’s Louisiana intrastate system toward industry and LNG. |
| Kosciusko Junction | Gulf South and Texas Gas | Applied | Expansion | 1,180 | 2029 | MS | CP25-547, CP25-549. About 112 miles. Notes: draft EIS 2026-04-01; final EIS issued 2026-07-24. Demand field: LNG/Other. The May EIA article ties Louisiana’s 2027 additions to Pelican; this row is a later-year Mississippi project on the same operator family. |

Delta Express (Venture Global), 2,000 MMcf/d, LA, is **On Hold**. Notes say the pre-filing was withdrawn 2025-06-10 and the project is not progressing.

### Appalachia takeaway and Appalachia-linked expansions

| Project | Operator | Status | Type | Capacity (MMcf/d) | Expected in-service | States | What the file says |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Borealis Project | Texas Gas Transmission | Announced | Expansion | 2,000 | 2030 | OH | Greenfield east-west line from Clarington (Marcellus/Utica hub) toward Texas Gas, aimed south/southwest to the Gulf Coast and, with Kosciusko Junction, toward Transco Station 85. Non-binding open season April 2025. No docket in the file. |
| Southeast Supply Enhancement | Transcontinental Gas Pipeline (Williams) | Construction | Expansion | 1,600 | 2027 | VA, NC, SC, GA, AL | CP25-10. 55.3 miles of 42-inch loop in Virginia and North Carolina plus compression changes down to Alabama. Notes: FERC certificate 2026-01-29; notice to proceed 2026-02-25; target **end of 2027**. Matches the May 26 EIA article (1.6 Bcf/d in 2027). Demand: LDC, electric, industrial. This is southbound capacity downstream of Appalachian receipts on Transco, not a new producing-basin trunk. |
| Crossroads Expansion | Crossroads Pipeline Co. (TC Energy) | Announced | Expansion | 1,500 | 2030 | OH, IN | Notes: non-binding open season Feb–Mar 2026 on the existing Wood County, OH to Lake County, IN system, for up to 1.5 Bcf/d aimed at power and data centers. Target 2030-11-01 if binding commitments follow. |
| Transco Power Express | Transcontinental Gas Pipe Line (Williams) | Announced | Expansion | 950 | 2030 | VA | Demand field: power / data centers in Northern Virginia. |
| Constitution Pipeline (revival) | Constitution Pipeline Co. LLC (Williams) | Pre-applied | New Pipeline | 650 | 2028 | PA, NY | CP13-499-006. Notes: 125-mile Marcellus line, Susquehanna County, PA to Schoharie County, NY; Williams asked FERC on 2025-12-19 to reinstate the certificate. FERC pending table, 2026-09-24: 650 MMcf/d, 125 miles, NY/PA, filed 2025-12-19. |
| MVP Boost | Mountain Valley Pipeline, LLC | Applied | Expansion | 600 | 2028 | WV, VA | CP26-14. Compression adding 600 MDth/d on the existing MVP mainline (notes: from 2.0 to 2.6 Bcf/d). FERC pending table, 2026-09-24: 600 MMcf/d, filed 2025-10-23. |
| MVP Southgate | Mountain Valley Pipeline, LLC | Construction | The file has both an Expansion row (“Amendment”) and a New Pipeline row, same capacity | 550 | 2028 | VA, NC | Both rows cite CP25-60 and the same amended project: route cut from 75 miles to about 31 miles, capacity raised from 375 to 550 MDth/d, Pittsylvania County, VA to Rockingham County, NC. Amended certificate Dec 2025. Notes on the New Pipeline row say a 4th Circuit stay of NC and VA water-quality certifications in March 2026 led to a voluntary construction halt pending argument on 2026-04-28. Treat as **one** 550 MMcf/d project recorded twice. |
| Appalachian Reliability | Eastern Gas Transmission and Storage | Approved | Expansion | 550 | 2028 | PA, OH | CP25-528. Notes: certificate issued 2026-06-18. Receipts in Armstrong County, PA, deliveries to Texas Eastern and Rockies Express. |
| Northeast Supply Enhancement | Transcontinental Gas Pipe Line | Construction | Expansion | 400 | 2027 | PA, NJ, NY | Demand field: LDC (National Grid NYC). |
| Clarington Connector | EQT Corp. | Announced | New Pipeline | 400 | 2028 | OH, PA | Notes: move Marcellus/Utica gas into Ohio for data-center and power load; connects toward Rover, REX, and Nexus. |
| Appalachia to Market II (Armagh and Entriken) | Texas Eastern | Construction | Upgrade | 55 | 2027 | PA, NJ | CP22-486. Small. Notes: extension request to place the project in service by 2027-06-30. Listed because the name is Appalachian; capacity is not major. |

### LNG feed lines

Many Permian and Haynesville rows above also have Demand Served = LNG (Blackcomb, Eiger, DeLa, Pelican, Driftwood, Gillis Access Extension). This section is the terminal laterals and header projects whose notes are specifically about feed gas.

| Project | Operator | Status | Type | Capacity (MMcf/d) | Expected in-service | States | What the file says |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Rio Bravo Pipeline | Rio Bravo Pipeline Company (Enbridge) | Construction | New Pipeline | 4,500 | 2026 | TX | CP16-455, CP20-481, CP23-519. About 138 miles from Kleberg County to the Port of Brownsville for NextDecade Rio Grande LNG. Notes: target **second half of 2026**. Same project the May 26 EIA article highlighted at up to 4.5 Bcf/d. |
| CP Express Phase 1 | Venture Global | Construction | New Pipeline | 1,800 | 2027 | TX, LA | CP22-22. About 85 miles of 48-inch pipe plus a 6-mile lateral into the CP2 terminal in Cameron Parish. Notes: Haynesville volumes into CP Express via TC Louisiana Intrastate; construction of Moss Lake compressor authorized Dec 2025; CP2 Phase 1 FID 2025-07-27. |
| CP Express Phase II | Venture Global | Construction | New Pipeline | 2,200 | 2027 | TX, LA | Same CP22-22 order. Notes: added compression at Moss Lake for full CP2 buildout. Phase 2 is not a second long-haul pipe. A **different** pending docket, CP26-533 “CP Express Pipeline Expansion” (1,900 MMcf/d, filed 2026-05-26), is on the Sept 24 FERC list and is **not** a row in this workbook. |
| Louisiana Connector (Port Arthur Pipeline) | Port Arthur Pipeline LLC | Part Completed | New Pipeline | 2,000 | 2026 | LA, TX | CP18-7 and later amendments. 72-mile, 42-inch line into Sempra Port Arthur LNG. Notes: a portion was approved for in-service by FERC on **2026-05-29**. The May 26 EIA article still described full second-half-2026 service. |
| Golden Pass Lateral | Golden Pass LNG Terminal LLC | Approved | Lateral | 2,600 | 2027 | TX | CP25-205. 0.22-mile supply lateral inside the terminal fence, up to 2.6 Bcf/d. Notes: Phase I ties to Kinder Morgan’s Trident intrastate line; certificate amendment Dec 2025. |
| Trident Intrastate Pipeline | Kinder Morgan | Construction | New Pipeline | 2,000 | 2027 | TX | T4-10662. 216 miles, Katy to the Port Arthur LNG/industrial corridor. Notes: Phase 1 early 2027; Phase 2 late 2028; contracts include Golden Pass LNG; interconnects with Texas Access. |
| Texas Access | Kinder Morgan Louisiana Pipeline | Applied | Expansion | 1,300 | 2028 | TX, LA | CP26-136. About 3 miles of 48-inch plus interconnects, moving up to 1.3 Bcf/d of Texas gas into the southwest Louisiana LNG corridor. Anchor: Woodside Louisiana LNG, 1.0 Bcf/d. FERC pending table, 2026-09-24: 1,300 MMcf/d, filed 2026-03-06. Notes: partial in-service Jan 2028, full April 2028. |
| Texas Gateway | Gulf South Pipeline | Applied | Expansion | 1,450 in the capacity column | 2029 | TX, LA | CP26-547. Notes: minimum 1.45 Bcf/d, Carthage Header to Beauregard Parish, target 2029-11-01, application filed 2026-06-26. **FERC pending table, 2026-09-24, lists 1,800 MMcf/d** and 155 miles. Both numbers are from those two public sources; the workbook cell is 1,450. |
| Mustang Express | Arm Energy Holdings LLC | Approved | New Pipeline | 2,500 | 2029 | TX | T4-10624. Intrastate. Cougar lateral to Katy, mainline Katy to Port Arthur, plus a storage lateral. Notes: anchor is Sempra Port Arthur LNG Phase 2; FID 2025-10-09; in-service targeted late 2028 / early 2029. |
| Corpus Christi Stage III Pipeline | Cheniere Corpus Christi | Construction | Expansion | 1,530 | 2027 | TX | CP18-513. 21-mile feed line to the Stage 3 trains. Notes: partial in-service Sept 2024 at 510,000 Dth/d; 2025-08-27 extension request to complete by 2029-12-31. |
| CCPL Expansion (Corpus Christi Stage IV) | Cheniere Corpus Christi Pipeline | Pre-applied | Expansion | 3,000 in the capacity column | 2030 in the year column | TX | Notes: about 26 miles of 42-inch adding **up to 2.75 Bcf/d**; application filed 2026-02-03; dockets PF25-10, CP26-82, CP26-87; notes say target in-service **4Q 2031** and FERC approval sought by May 2027. FERC pending table, 2026-09-24: **2,750 MMcf/d**, 25.8 miles, filed 2026-02-03. Report 3,000 as the workbook cell and 2,750 as the note and the FERC table. |
| Pipeline modifications (Lake Charles LNG) | Trunkline Gas | Construction | Expansion | 2,600 | 2031 | AR, MS, LA | CP14-119 and related. Notes: some facilities in service Jan 2024; FERC extension to 2031-12-31; project still pending FID by Energy Transfer. |
| Sabine Crossing | Cheniere (Sabine Crossing Pipeline, LLC) | Pre-applied | New Pipeline | 2,500 in the capacity column | 2031 | TX, LA | Docket in the file: CP25-505. 55.6 miles toward Sabine Pass Stage 5. **FERC pending table, 2026-09-24: 2,700 MMcf/d**, 55.6 miles, filed 2025-06-06. |
| Holbrook Expansion | Cameron Interstate Pipeline | Approved | Expansion | 1,079 | 2027 | LA | CP24-1. Compression only, incremental firm feed to Cameron LNG. Notes: construction scheduled to start 2026. |
| Texas Connector (Port Arthur Pipeline) | Sempra / Port Arthur Pipeline | Approved | New Pipeline | 494 | 2028 | TX | CP17-21, CP24-512. 31 miles for Port Arthur LNG Phase 2. The original public description of this project was often “about 2.0 Bcf/d”; **this workbook cell is 494**. |
| Lake Charles Expansion (Magnolia LNG) | Kinder Morgan Louisiana Pipeline | Approved | Reversal | 1,362 | 2029 | LA | CP14-511. Reversal to serve proposed Magnolia LNG. Notes: terminal still pre-FID; 2026-01-15 extension request to 2031-04-15. |
| TTC Connector | TTC Connector, LLC | Approved | New Pipeline | 300 | 2026 | TX | CP25-525. Up to 300,000 Dth/d from Tres Palacios storage toward Gulf South’s Coastal Bend Header for Freeport LNG. Notes: approved 2026-06-30; notice to proceed 2026-07-21; construction expected after 2026-08-03. |
| Alaska Nikiski LNG pipeline | 8 Star Alaska LLC | Approved | New Pipeline | 3,300 | 2029 | AK | CP17-178. Prudhoe Bay to Nikiski LNG. Outside the four Lower 48 themes. Included because it is one of the largest Approved rows in the file (notes: initial gas 2029). |

## Recently completed (confirmed in this workbook)

### Still on the current sheet (2026 activity)

| Project | Operator | Status | Type | Capacity (MMcf/d) | Year in file | States | Note from the file |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Gulf Coast Express Expansion | Kinder Morgan Energy Partners | Completed | Expansion | 570 | 2026 | TX | Compression-only. Waha to Agua Dulce. Notes say total GCX about 2.57 Bcf/d after the add, and “in-service targeted mid-2026.” Completed Date cell is blank; status is Completed. |
| Texas-Louisiana Expansion | NGPL (Kinder Morgan / Brookfield / ArcLight) | Completed | Expansion | 467 | Year cell says **2028** | TX, LA | CP24-8. Notes: in service **2026-07-10**. Shippers include Delfin and Golden Pass LNG. The year cell and the note disagree; both are in the row. |
| Hugh Brinson Phase I & II | Energy Transfer | Part Completed | New Pipeline | 2,200 | 2026 | TX | See Permian table. Phase I commissioning; Phase II still Q1 2027. |
| Louisiana Connector | Port Arthur Pipeline | Part Completed | New Pipeline | 2,000 | 2026 | LA, TX | See LNG table. Portion approved in service 2026-05-29 per the note. |
| Oracle data center laterals | Energy Transfer | Part Completed | Lateral | 900 | 2026 | TX | Off the North Texas system, sourced via Hugh Brinson, toward the Abilene Oracle campus. First lateral in service 2026-06-13. Electric demand, not an LNG lateral. |

Two other Completed rows on the current sheet are outside the basin focus: Bison XPress (Northern Border, 300 MMcf/d, ND/MT/WY, 2026; Bakken reversal) and Cumberland (Tennessee Gas, 245 MMcf/d, TN, completed 2026-05-26; TVA power plant).

### 2025 completions on the historical sheet (capacity at least about 700 MMcf/d, LNG or Haynesville or Texas Gulf)

| Project | Operator | Capacity (MMcf/d) | Completed date in file | States | File note |
| --- | --- | --- | --- | --- | --- |
| Golden Pass LNG bidirectional pipeline | Golden Pass Pipeline LLC | 2,500 | 2026-01-27 (in-service year cell is 2025) | LA, TX | Up to 2.5 Bcf/d of domestic feed to Golden Pass LNG. Notes: FERC in-service approvals Sept–Oct 2025; first LNG from Train 1 on 2026-03-30. |
| Louisiana Energy Gateway (LEG) | Transco (Williams) | 1,800 | 2025-10-01 | LA | Haynesville spine to Gillis. Notes also say placed in service 2025-07-23. Deliveries into Transco, Cameron Interstate, LA Storage, and TC Louisiana Intrastate. |
| New Generation Gas Gathering (NG3) | Momentum Midstream | 1,700 | 2025-10-01 | LA | Haynesville to Gillis. Notes: initial 1.7 Bcf/d, expandable to 2.2; official in-service 2025-10-01. |
| Venice Extension | Texas Eastern | 1,260 | 2024-12-15 (in-service year 2025) | LA | Reversal toward Plaquemines LNG via Gator Express. Notes: full service authorized 2024-12-26 for a 2025-01-01 start. |
| Evangeline Pass Phase 2 | Southern Natural Gas | 1,100 | 2025-05-29 | MS, LA | Haynesville-sourced gas to Plaquemines LNG. Notes: brings the two-phase project to full capacity after Phase 1 in 2024. |
| South Texas to Houston Market Expansion | Kinder Morgan (Tejas) | 781 | 2025-06-01 | TX | Intrastate Tejas looping and compression, about 0.781 Bcf/d toward Houston. Demand field: LNG. |
| East Lateral XPress | Columbia Gulf | 725 | 2025-05-01 | LA | Deliveries to Gator Express for Plaquemines LNG. |

For scale, the historical sheet’s large **2024** completions that set up this map include Matterhorn Express (WhiteWater, 2,500 MMcf/d, Waha to Katy, completed 2024-09-15), ADCC (WhiteWater, 1,700, Agua Dulce to Corpus Christi LNG, 2024-07-01), Gillis Access (TC Energy, 1,500, Haynesville to LNG, completed 2024-02-15), and both Gator Express laterals (Venture Global, 1,970 each, Plaquemines LNG).

## FERC pending list as a supplement, not a replacement

As of the 2026-09-24 table, interstate projects still pending that match the themes above include Constitution (650), Sabine Crossing (2,700 on FERC vs 2,500 in the EIA cell), Texas Access (1,300), MVP Boost (600), Forza (750), Texas Gateway (1,800 on FERC vs 1,450 in the EIA cell), CCPL Expansion (2,750 on FERC vs 3,000 in the EIA cell), Green Chile (Transwestern, CP26-80, 400 MMcf/d, NM, data-center power), and Florida Gas Transmission Phase IX (CP26-578, 526.75 MMcf/d, filed 2026-09-09). The EIA row for Florida is still “Announced” at 550 MMcf/d with in-service year 2028, which fits a filing that post-dates the August 4 workbook.

Confirmed on that FERC page and **absent** from the August 4 EIA sheet:

| FERC docket | Project | Applicant | Capacity (MMcf/d) | Miles | States | Filing date |
| --- | --- | --- | --- | --- | --- | --- |
| CP26-533-000 | CP Express Pipeline Expansion | Venture Global CP Express / CP2 LNG | 1,900 | 0.19 | TX | 2026-05-26 |
| CP26-549-000 | Franklin Farms | ETC Tiger Pipeline | 1,000 | 14.99 | LA | 2026-07-01 |
| CP26-534-000 | Permian Basin Expansion | Northern Natural Gas | 361.6 | 16.2 | NM, TX | 2026-05-28 |
| CP26-576-000 | Leidy Access Expansion | Transco | 183.1 | 3.38 | PA | 2026-09-04 |

Blackcomb, Hugh Brinson, Eiger, Pelican, Trident, Traverse, and Mustang Express are intrastate in the EIA file (Texas Railroad Commission T4 permits). They do not appear on this FERC interstate pending list, which is expected.

## Other public trackers

- **EIA workbook** is the one structured national file that mixes interstate and intrastate projects and keeps history.
- **FERC Major Pipeline Projects Pending** is the other public table, limited to pending interstate certificate cases and refreshed on its own calendar (this copy: 2026-09-24).
- **Texas Railroad Commission** permit records are the authority EIA cites for intrastate Texas lines.
- **FERC eLibrary** remains the system of record for the application, the order, and in-service letters. Retrieve by docket (the workbook’s docket column is the index). It does not replace the EIA sheet.
