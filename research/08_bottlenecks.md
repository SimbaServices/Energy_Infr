# Natural gas bottlenecks: production versus takeaway

Research date: 2026-09-26. Sources are public pages from the U.S. Energy Information Administration (EIA, the statistical arm of the Department of Energy), the Federal Energy Regulatory Commission (FERC), and state regulators only where EIA cites their decisions (Railroad Commission of Texas; California Public Utilities Commission). No paywalled figure is used as a capacity. Every volume below is a number printed on the cited page, with the page date. Those volumes are illustrations of corridors. They are not a balanced inventory as of September 26, 2026.

The app should recompute balances from the latest public files, not from the narrative figures copied here:

- Dry production and consumption by state: [EIA natural gas data](https://www.eia.gov/naturalgas/data.php). Dry production equals marketed production less extraction loss ([table definitions](https://www.eia.gov/dnav/ng/TblDefs/ng_sum_snd_tbldef2.asp)).
- Border capacity already in service: [state-to-state capacity](https://www.eia.gov/naturalgas/data.php#pipelines), January 2026 release listed on that page.
- Projects not yet in the capacity file: [pipeline projects tracker](https://www.eia.gov/naturalgas/data.php#pipelines), August 2026 workbook listed on that page.
- LNG sinks: [U.S. liquefaction capacity](https://www.eia.gov/naturalgas/data.php) (existing, under construction, and approved) and [exports by point of exit](https://www.eia.gov/dnav/ng/ng_move_poe2_a_EPG0_ENP_Mmcf_a.htm).
- A flow check, not a capacity: [interstate movements by state](https://www.eia.gov/dnav/ng/ng_move_ist_a2dcu_nus_a.htm).

## Formula in plain language

For a producing state or basin, start with dry production in million cubic feet per day. If the series is only published as marketed production, use that and label it; do not mix the two. Subtract gas used inside the same area, subtract feedgas to LNG export terminals inside the area, and subtract the nameplate capacity of pipelines that leave the area. What is left is the takeaway balance.

A positive balance means production is larger than local use, LNG export, and outbound pipe capacity. That is a candidate glut: gas is being produced faster than it can be burned locally or carried out. A negative balance means the nameplate outlets are larger than production. That spare nameplate is not proof the pipes are unconstrained, and it is not a reason to paint a consuming region as a glut.

For a consuming region, use a different subtraction. Local consumption minus local production minus inbound pipeline capacity minus LNG import sendout. A positive result is a delivery shortfall. New England and Southern California fail that test in cold or outage periods even though they produce little gas. Calling them gluts because production minus outbound capacity is near zero would misread the constraint.

## What the app should compute

Work in MMcfd. EIA narrative pages usually print Bcf/d. One Bcf/d is 1,000 MMcfd. Annual million cubic feet divided by the number of days in the period is MMcfd. Do not divide a Drilling Productivity Report gross-withdrawal rate by a dry-production definition.

Geography is either a state or a named basin. EIA’s Drilling Productivity Report regions that matter here are Appalachia, Permian (West Texas and southeastern New Mexico), and Haynesville (Louisiana and Texas). A basin balance must sum the states in the basin and must not also be drawn as those states, or the same gas is counted twice.

For geography `g` and a day or month:

- `P` = dry production, MMcfd. Fallback: marketed production, labeled.
- `D_local` = end-use consumption in `g` plus lease, plant, and pipeline fuel assigned to `g`, MMcfd.
- `X_lng` = natural gas received for liquefaction at export terminals located in `g`, MMcfd. This is a sink inside the state. It is not outbound interstate capacity.
- `X_pipe_export` = pipeline exports to Mexico or Canada that leave from points inside `g`, if those crossings are not already inside outbound border capacity.
- `C_out` = sum of nameplate capacity on pipelines whose surveyed direction leaves `g` (state border, international border, or offshore). Use the EIA state-to-state capacity file. Respect direction. A bidirectional line contributes only the capacity in the outbound direction.
- `C_in` = the same file, inbound direction.
- `S_lng_import` = sendout from LNG import terminals serving `g`, MMcfd. This term matters for New England. It is not an LNG export.

Producing-area takeaway balance:

`B_takeaway = P − D_local − X_lng − X_pipe_export − C_out`

Consuming-area delivery balance:

`B_delivery = D_local − P − C_in − S_lng_import`

A screen that is only `P − C_out` is useful as a diagnostic and is the wrong map color. Texas and Louisiana production is largely connected to Gulf Coast demand and LNG by pipelines that never cross a state line. EIA reported that in 2023, 5.2 Bcf/d of intrastate capacity was added, nearly all of it in Texas and Louisiana to serve Gulf Coast markets including LNG, while interstate additions were 0.9 Bcf/d ([March 20, 2024](https://www.eia.gov/todayinenergy/detail.php?id=61623)). EIA’s own rule on that point: interstate lines cross state or international borders or serve export demand at a border or an LNG terminal; intrastate lines do not cross state borders ([March 17, 2025](https://www.eia.gov/todayinenergy/detail.php?id=64744)). Subtract `D_local` and `X_lng` before comparing production with outbound interstate capacity, or the Gulf Coast looks like a glut when it is a demand center.

Storage is not an extra term in the average balance. It shifts gas across days. EIA’s February 2023 *Short-Term Energy Outlook* supplement treats storage withdrawals as more than 20 percent of winter supply nationally and notes that New England has no underground storage to buffer a pipeline shortfall ([supplement PDF](https://www.eia.gov/outlooks/steo/special/supplements/2023/2023_sp_01.pdf)). Show winter and summer balances separately. Do not add working-gas capacity to `C_out`.

## Hypothetical case

Hold `P`, `D_local`, and current LNG feedgas at the latest actual month. Add capacity, do not add a production forecast.

Include a project only when all of the following are true:

1. Status is approved or under construction. EIA’s Annual Energy Outlook 2022 *No Interstate Pipeline Builds* case uses that same cut: before the year when the model is allowed to invent pipes, it loads projects that are already approved or under construction from the Natural Gas Pipeline Projects Tracker ([AEO2022 Issues in Focus](https://www.eia.gov/outlooks/aeo/IIF_pipeline/)). Leave out announced, pending, pre-filing, on hold, and cancelled projects. FERC’s [pending](https://www.ferc.gov/industries-data/natural-gas/major-pipeline-projects-pending) table is not approval. FERC’s [approved major projects](https://www.ferc.gov/industries-data/natural-gas/approved-major-pipeline-projects-1997-present) table is the certificate list, with capacity in MMcf/d.
2. The project has an in-service date, and the case date is on or after that date. EIA assumes known projects come online in November of the expected in-service year, because projects have tended to start before winter ([AEO2026 Natural Gas Market Module assumptions, April 2026](https://www.eia.gov/outlooks/aeo/assumptions/pdf/NGMM_Assumptions.pdf); same November rule in the AEO2022 case). The app should prefer the month in the tracker. If the month is missing, use November of the stated year and label the assumption.
3. The added capacity is not already inside the baseline capacity file. Completed projects are history. Adding them again double-counts. Example: EIA’s May 3, 2023 article listed Louisiana Energy Gateway (1.8 Bcf/d) and New Generation Gas Gathering (1.7 Bcf/d) as future Haynesville takeaway if finished by the end of 2024 ([May 3, 2023](https://www.eia.gov/todayinenergy/detail.php?id=56361)). EIA later reported both in service as of October 2025 ([February 25, 2026](https://www.eia.gov/todayinenergy/detail.php?id=67225)). A 2026 case must not add them.

FERC construction context, not an extra status: a company cannot start construction until the Commission issues a certificate, the company accepts it, other permits are in hand, and certificate conditions are met ([FERC landowner guide](https://www.ferc.gov/interstate-natural-gas-facility-my-land-what-do-i-need-know)). “Under construction” is downstream of approval.

Apply the added capacity to the term it actually changes:

- A line that crosses out of `g` increases `C_out`.
- A line to an LNG export terminal inside `g` increases the terminal’s feedgas capability (`X_lng` ceiling), not `C_out`. Some of that pipe is FERC-jurisdictional and some is Railroad Commission of Texas-jurisdictional ([December 12, 2023](https://www.eia.gov/todayinenergy/detail.php?id=61062)).
- A gathering line to an in-state hub (Haynesville to Gillis) is intrastate or gathering. It raises the chance that gas can reach an LNG header. It is not outbound capacity from Louisiana.

Then recompute `B_takeaway` and `B_delivery`. Production stays at the latest actual. That is the case. It answers “what if the pipes that are already approved or being built open on time,” not “what if drilling rises.”

The August 2026 tracker workbook was not opened for this note. Read its status column. Keep values that are approved or under construction. If a status string is unseen, exclude the project and log the string. Do not guess a synonym.

## Assumptions and limits

Nameplate capacity is not a flow. EIA’s archived pipeline write-up gives three utilization ideas: average throughput versus capacity at a state or regional boundary, system flow versus an estimated peak, and peak-day deliveries versus capacity. A line can look lightly used on an annual average and still be full on the peak day. Reported volumes can also exceed nameplate when several contracts stack along one pipe: a 200 MMcf/d segment carrying three successive 100 MMcf/d hauls is reported as 300 MMcf/d while no single section is over half full ([pipeline capacity and utilization](https://www.eia.gov/naturalgas/archive/analysis_publications/ngpipeline/usage.html)).

EIA’s own network model does not treat 100 percent as the normal operating point. The transportation charge stays fairly flat at low utilization and rises sharply as utilization approaches 100 percent. A binding flow limit on an arc widens the price gap between nodes ([NGMM assumptions, April 2026](https://www.eia.gov/outlooks/aeo/assumptions/pdf/NGMM_Assumptions.pdf)). For LNG, that same assumptions document sets average utilization at 98 percent in 2027 and 90 percent in 2028 and later, with new trains starting well below that in the first months. The hypothetical case should show nameplate and, beside it, the same balance with a utilization factor below 1. Do not bury the factor. A reasonable display is nameplate and 90 percent of nameplate, labeled as a sensitivity, not as a measured flow.

Other limits:

- The state-to-state file misses intrastate lines and gathering. In 2022 the interstate file recorded only 897 MMcf/d of additions, the least since EIA’s series began in 1995, while Gulf Coast takeaway was being built inside Texas and Louisiana ([March 2, 2023](https://www.eia.gov/todayinenergy/detail.php?id=55699)). About 65 percent of capacity built in 2025 was intrastate ([February 25, 2026](https://www.eia.gov/todayinenergy/detail.php?id=67225)).
- Maintenance can remove the spare the annual balance implies. Waha traded at discounts of more than $5.00/MMBtu from September 2022 through January 2023 during maintenance, and the El Paso Line 2000 outage from August 2021 through February 2023 cut westbound Permian flows ([August 21, 2023](https://www.eia.gov/todayinenergy/detail.php?id=60180)).
- A full book of firm contracts is not spare capacity. Mountain Valley Pipeline’s full 2.0 Bcf/d was signed for at least 20 years ([June 14, 2024](https://www.eia.gov/todayinenergy/detail.php?id=62323)).
- Associated gas in the Permian keeps growing when oil drilling pays, even if the gas price is low. EIA treats associated-dissolved volumes as not responding to the current natural gas price inside the balancing model ([NGMM assumptions, April 2026](https://www.eia.gov/outlooks/aeo/assumptions/pdf/NGMM_Assumptions.pdf)). Holding Permian production constant is the conservative hypothetical. Haynesville and Appalachia dry-gas drilling does respond to price, so a constant-production case can overstate a future glut if low prices would have cut drilling.
- Gross withdrawals (Drilling Productivity Report) are larger than dry production. The 2023 regional figures below are gross. Do not subtract them from dry-gas capacity without saying so.
- Basin outlines cross states. Permian gas is in Texas and New Mexico. Haynesville gas is in Louisiana and Texas. Appalachia gas in EIA’s production articles is the Northeast region, mainly Pennsylvania, West Virginia, and Ohio.
- Direction matters. A reversal changes which side of the border is `C_out`.
- Fully subscribed expansions and header projects can share the same downstream bottleneck. Adding every project’s nameplate along one corridor overstates relief if they deliver into the same full hub.

## Corridors

Prices are the public evidence EIA uses when capacity figures are incomplete. EIA states the mechanism directly: when production growth outruns takeaway additions, constraints push the Waha price down, and the basis to Henry Hub widens while the constraint lasts and narrows when it eases ([September 10, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63044)). Eastern Gas South (formerly Dominion South) trades at a discount to Henry Hub because Appalachian supply exceeds local demand and outbound pipes are constrained ([October 23, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63504)).

### Permian / Waha — producing-area takeaway, east, south, and west

West Texas and southeastern New Mexico. Most of the gas is associated. In 2023 the region accounted for 19 percent of U.S. gross withdrawals and averaged 23.3 Bcf/d, up 2.6 Bcf/d from the prior year ([March 27, 2024](https://www.eia.gov/todayinenergy/detail.php?id=61646)). The Drilling Productivity Report put 2022 Permian natural gas at a then-record 21.2 Bcf/d, up 2.7 Bcf/d from 2021 ([August 21, 2023](https://www.eia.gov/todayinenergy/detail.php?id=60180)). Because production rose faster than takeaway, Waha is typically cheaper than other hubs and sometimes negative ([October 23, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63504)).

EIA’s constraint evidence for 2024, as of September 10, 2024: Waha was below zero on 46 percent of trading days that year, including every day from July 26 through the article date. The low that year, as of that article, was −$6.41/MMBtu on August 29. The average basis to Henry Hub was −$2.07/MMBtu, versus an average 42 cents below Henry Hub in the second half of 2021 ([September 10, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63044)).

Directions EIA has described:

- East and toward the Gulf Coast. The February 2023 STEO supplement said about 1.4 Bcf/d of eastbound Permian takeaway was due by the end of 2023 and another 2.5 Bcf/d by the end of 2024. It did not name the pipes in that sentence. Matterhorn Express, 2.5 Bcf/d from Waha to the Katy area, was expected in September 2024 ([September 10, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63044)) and is listed among 2024 completions ([March 17, 2025](https://www.eia.gov/todayinenergy/detail.php?id=64744)). Do not treat 2.5 Bcf/d Matterhorn as future capacity in a 2026 case.
- South toward Agua Dulce and LNG. As of May 26, 2026, EIA describes Blackcomb as a 365-mile, 2.5 Bcf/d line under construction, Waha to Agua Dulce, then slated for the third quarter of 2026, “further clearing the Waha bottleneck.” The same article gives Hugh Brinson as 2.2 Bcf/d of Permian takeaway, phase 1 expected in the fourth quarter of 2026 and phase 2 in the first quarter of 2027 ([May 26, 2026](https://www.eia.gov/todayinenergy/detail.php?id=67707)). This note does not confirm that Blackcomb actually entered service after that article.
- West toward California and Arizona. El Paso Natural Gas Line 2000 was out from August 2021 through February 2023 and reduced westbound flows ([August 21, 2023](https://www.eia.gov/todayinenergy/detail.php?id=60180)). In January 2022 EIA reported the 600 MMcf/d segment from the Black River station in West Texas to the California border effectively removed from service ([January 20, 2022 weekly](https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2022/01_20/)). In the week of February 29, 2024, a Line 2000 force majeure had cut westbound operational capacity at the Gila constraint by 48 percent (0.6 Bcf/d) and at Casa C by 58 percent (0.3 Bcf/d) ([February 29, 2024 weekly](https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2024/02_29/)).
- To the Mexico border. As of September 10, 2024, EIA listed the Saguaro Connector at 2.8 Bcf/d from the Permian to the U.S.–Mexico border, expected in 2027–28, inside a group of three projects (with Apex at 2.0 Bcf/d to Port Arthur, expected in 2026, and Blackcomb at 2.5 Bcf/d) that EIA then said were approved and totaled 7.3 Bcf/d. Separately, EIA said other announced Permian projects totaled 7.0 Bcf/d and might enter between 2025 and 2028 if built ([September 10, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63044)). Announced projects stay out of the hypothetical case.

As of May 26, 2026, EIA still described new Texas pipes as debottlenecking Waha. Developers’ plans in the tracker then showed 44.9 Bcf/d of U.S. capacity slated for 2026 and 2027, of which 31.6 Bcf/d (about 70 percent) was already under construction, 29.7 Bcf/d originated in Texas, and 8.4 Bcf/d was in Louisiana ([May 26, 2026](https://www.eia.gov/todayinenergy/detail.php?id=67707)). Those national totals mix LNG headers and takeaway. They are not a Permian surplus.

### Haynesville to Gulf Coast LNG — producing area next to the demand sink

Northeastern Texas and northwestern Louisiana. March 2023 dry production from the Haynesville play averaged 14.5 Bcf/d ([May 3, 2023](https://www.eia.gov/todayinenergy/detail.php?id=56361)). EIA’s Drilling Productivity Report gross withdrawals for the Haynesville region were 16.8 Bcf/d in 2023, 13 percent of the U.S. total, up 1.4 Bcf/d from 2022. Growth slowed because the Henry Hub price fell (average $2.54/MMBtu in 2023 versus $6.42/MMBtu in 2022) and the formation is deep, so drilling needs a higher gas price ([March 27, 2024](https://www.eia.gov/todayinenergy/detail.php?id=61646)). The February 2023 STEO supplement said Haynesville might need more capacity for southbound market growth. It did not print a deficit in Bcf/d.

Takeaway figures EIA published, with dates:

- Around 16 Bcf/d of takeaway out of Haynesville as of the May 3, 2023 article, attributed there to S&P Global Commodity Insights. EIA itself then listed three projects that would add 5.0 Bcf/d by the end of 2024 if on time: Louisiana Energy Gateway 1.8, NG3 1.7, and Gillis Access 1.5.
- Gillis Access at 1.5 Bcf/d, Gillis Hub to Gulf Coast LNG, is among 2024 completions ([March 17, 2025](https://www.eia.gov/todayinenergy/detail.php?id=64744)). LEG at 1.8 Bcf/d and NG3 at 1.7 Bcf/d were in service as of October 2025. EIA called that 2025 intrastate capacity gathering into the wider system, Haynesville to the Gillis Hub ([February 25, 2026](https://www.eia.gov/todayinenergy/detail.php?id=67225)).
- LEAP reached 1.9 Bcf/d as of June 2024 after a 0.2 Bcf/d phase, Haynesville to the Gillis Hub ([March 17, 2025](https://www.eia.gov/todayinenergy/detail.php?id=64744)). Phases 1 and 2 had added a combined 0.7 Bcf/d in 2023 ([March 20, 2024](https://www.eia.gov/todayinenergy/detail.php?id=61623)).

The constraint to map is southbound: Haynesville supply versus LNG feedgas on the Louisiana and Texas coast, not an interstate exit from Louisiana. LNG-bound pipes EIA described as under construction, partly completed, or approved as of December 12, 2023, totaled more than 20.0 Bcf/d toward five terminals then under construction, of which about 13.5 Bcf/d of pipe was under construction. Named capacities on that page: Golden Pass Pipeline expansion 2.5 Bcf/d; Port Arthur Louisiana Connector and Texas Connector, 2.0 Bcf/d each; Gator Express, two pipes at about 2.0 Bcf/d each; Evangeline Pass 1.1 Bcf/d; Venice Extension 1.3 Bcf/d; ADCC 1.7 Bcf/d; Corpus Christi Stage III Pipeline 1.5 Bcf/d; Rio Bravo, two pipes totaling 4.5 Bcf/d ([December 12, 2023](https://www.eia.gov/todayinenergy/detail.php?id=61062)). Later EIA pages repeat Rio Bravo at up to 4.5 Bcf/d with a second-half-of-2026 target, the Louisiana Connector at 2.0 Bcf/d in the second half of 2026, Evangeline Pass as a 2025 completion of 1.1 Bcf/d into Plaquemines, and a 0.4 Bcf/d Texas-to-eastern-Louisiana pathway completed in 2025 ([May 26, 2026](https://www.eia.gov/todayinenergy/detail.php?id=67707); [February 25, 2026](https://www.eia.gov/todayinenergy/detail.php?id=67225)). Use the August 2026 tracker to see which of the December 2023 list are already in service.

### Appalachia — out of basin, and a trapped-gas price

In 2023 Appalachia was the largest gross-withdrawal region: 37.7 Bcf/d, 29 percent of U.S. gross production, up only 1.2 Bcf/d (3 percent). EIA’s reason: not enough pipeline takeaway to move more gas to demand markets. In 2022 the Northeast had no major new pipeline capacity, and 2023 interstate projects were upgrades to existing lines or compressors ([March 27, 2024](https://www.eia.gov/todayinenergy/detail.php?id=61646)). Eastern Gas South prices sit below Henry Hub for that reason ([October 23, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63504)).

Older capacity path, still the public description of direction: Northeast takeaway rose from 4.5 Bcf/d in 2008 to 24.5 Bcf/d in 2020, an increase of 16.5 Bcf/d from 2014 to 2020, much of it aimed at the Midwest. EIA also described added takeaway from Appalachia to Canada and to the Southeast. Pipes in the region are most full in late summer, when local consumption is lowest ([September 1, 2021](https://www.eia.gov/todayinenergy/detail.php?id=49377)). Read “west” here as EIA’s Midwest direction, not as a separate westbound header with its own published capacity.

Directions with project figures:

- South. Mountain Valley Pipeline, up to 2.0 Bcf/d, Wetzel County, West Virginia, to Transco compressor station 165 in Pittsylvania County, Virginia. FERC authorized operations on June 11, 2024. The full capacity is under long-term agreements ([June 14, 2024](https://www.eia.gov/todayinenergy/detail.php?id=62323); also listed as a 2024 completion, [March 17, 2025](https://www.eia.gov/todayinenergy/detail.php?id=64744)).
- Further south on Transco. Southeast Supply Enhancement, 1.6 Bcf/d, Transco from Virginia to Alabama, expected in 2027 ([May 26, 2026](https://www.eia.gov/todayinenergy/detail.php?id=67707)).
- East toward the coast. Regional Energy Access, a little more than 0.8 Bcf/d, on Transco between Luzerne County, Pennsylvania, and Middlesex County, New Jersey, a 2024 completion ([March 17, 2025](https://www.eia.gov/todayinenergy/detail.php?id=64744)).
- Toward the Gulf. Columbia Gulf’s Louisiana XPress added 493 MMcf/d Mississippi-to-Louisiana and 50 MMcf/d Tennessee-to-Mississippi, described as increasing deliverability from the Appalachian Basin, and was part of the 897 MMcf/d of interstate additions in 2022 ([March 2, 2023](https://www.eia.gov/todayinenergy/detail.php?id=55699)).

AEO2022’s no-new-interstate-pipe case is the qualitative map of what a takeaway cap does. It loaded only approved or under-construction projects before 2024, then added no unplanned interstate capacity through 2050. Versus the Reference case in 2050, the East supply region (Marcellus and Utica) produced 3.6 Tcf less dry gas, the Gulf Coast produced 0.7 Tcf more, and the Southwest produced 0.4 Tcf more. Interregional capacity from the Mid-Atlantic and Ohio region to the Eastern Midwest was 5.1 Bcf/d lower. Delivered prices in the Middle Atlantic were $0.69/MMBtu lower, because gas was trapped, and prices in the East North Central census division were about $1.25/MMBtu higher, because that division received less Appalachian gas ([AEO2022 Issues in Focus](https://www.eia.gov/outlooks/aeo/IIF_pipeline/)). A later outlook still treats East growth as requiring pipes to the Gulf Coast: in most AEO2026 cases, East-region production rises from 37 Bcf/d in 2025 to between 66 and 73 Bcf/d by 2050, and that growth requires infrastructure toward Gulf Coast demand. In the high oil and gas supply case, pushing still more Marcellus eastward is uneconomic because of the extra pipeline cost ([AEO2026 narrative](https://www.eia.gov/outlooks/aeo/pdf/AEO_Narrative.pdf)).

### New England — winter delivery shortfall, not a glut

New England is not a producing region and has no underground storage, so LNG imports are the marginal winter supply ([February 2023 STEO supplement](https://www.eia.gov/outlooks/steo/special/supplements/2023/2023_sp_01.pdf); [October 23, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63504)). Algonquin Citygate volatility tracks peak demand against limited pipeline capacity.

Published operating snapshots, not a design basis for the app:

- The week ending January 11, 2022, New England consumption for heating and power rose to 4.9 Bcf/d. January 1–31 demand averaged over 4.1 Bcf/d. From January 7–21, gas-fired generation fell 14 percent versus the prior week because pipes could not serve the plants, and oil-fired generation reached as much as 20 percent of electric supply in some hours. On peak days, LNG has contributed up to 35 percent of New England gas supply. January 2022 Algonquin Citygate averaged $20.55/MMBtu and exceeded $28/MMBtu on several days ([February 3, 2022](https://www.eia.gov/todayinenergy/detail.php?id=51158)).
- Import terminals serving that market, as stated in EIA’s January 20, 2022 weekly: Everett LNG 0.7 Bcf/d near Boston, Northeast Gateway 0.5 Bcf/d offshore near Boston, and Saint John (formerly Canaport) 1.0 Bcf/d in New Brunswick, with Saint John gas reaching New England on Maritimes & Northeast. An earlier EIA article stated Northeast Gateway at 0.4 Bcf/d ([April 23, 2019 article, id 39432](https://www.eia.gov/todayinenergy/detail.php?id=39432)). Use the later public terminal file if the two disagree; do not average them.

Color this region with `B_delivery`, and only in winter. A summer average will hide the constraint. AEO2022 found only 0.05 Bcf/d less capacity into New England from Canada in the no-build case, which is a small modeled change. The public constraint is the pipes already there, not a missing 2050 expansion.

### Pacific Northwest and the Sumas border

EIA’s September 11, 2025 article is the opposite of a 2025 bottleneck: with plentiful upstream supply and “minimal sustained pipeline capacity constraints,” net flows from Canada into the Pacific Northwest averaged 4.5 Bcf/d in February 2025, the highest February-comparable month in data back to 2012. Northwest Sumas averaged $1.59/MMBtu through August 2025. British Columbia production averaged 7.8 Bcf/d in July and Alberta production reached 11.6 Bcf/d in March, both cited by EIA from S&P Global Insights. August flows fell as Western Canadian LNG demand pulled gas away. Jackson Prairie storage, 24.6 Bcf working capacity, was more than 95 percent full as of September 7, 2025 ([September 11, 2025](https://www.eia.gov/todayinenergy/detail.php?id=66084)).

The same hub has spiked when upstream capacity failed. The February 2023 STEO supplement says the Pacific Northwest (Idaho, Oregon, Washington) draws on the Rockies, Canada, and California, and that December 2022 cold weather, weaker Canadian imports, and limited flows from California put Sumas at an average of about $27/MMBtu, up from about $10/MMBtu in November. The October 25, 2018 weekly, after the Westcoast rupture in British Columbia, said the Westcoast system can move up to 1.7 Bcf/d in winter and would operate that winter at 0.9 to 1.3 Bcf/d; Sumas imports had been about 930 MMcf/d the week before the rupture and about 460 MMcf/d after October 18 ([October 25, 2018 weekly](https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2018/10_25/)).

Map rule: do not hard-code the Pacific Northwest as a current glut or a current deficit. Flag it when Sumas basis blows out or when inbound capacity from Canada is derated. EIA’s 2025 description is ample supply.

### Southern California — inbound and storage, fed in part by Permian gas

California is far from the main producing basins and depends on pipeline connections ([February 2023 STEO supplement](https://www.eia.gov/outlooks/steo/special/supplements/2023/2023_sp_01.pdf)). SoCal Citygate covers consumption in the Los Angeles Basin averaging about 2.5 Bcf/d in 2023, and the price includes the haul from the border into the distribution system ([October 23, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63504)). Kern River, at the Opal hub in Wyoming, is described as the only interstate pipe that delivers Rockies gas directly to Southern California; EIA, citing the pipeline owner, says it receives about 25 percent of Rockies supply and its deliveries are about 25 percent of California demand.

CPUC actions EIA reported: SoCalGas Northern Zone receipts (Topock, Needles, Kramer Junction) were raised to 1.4 Bcf/d in November 2023, almost 90 percent of capacity before the October 2017 shutdown of Line 235-2, and El Paso Line 2000 returned in February 2023 ([Today in Energy, id 61644](https://www.eia.gov/todayinenergy/detail.php?id=61644)). On August 31, 2023, the CPUC raised the Aliso Canyon working-gas cap from about 41.2 Bcf to 68.6 Bcf (an increase of 27.4 Bcf). Uncapped working capacity is 86.2 Bcf. The CPUC’s stated reason was winter reliability and price moderation ([September 7, 2023 weekly](https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2023/09_07/)). This is a delivery and storage constraint on an importing system. It is not a production glut.

### Smaller producing takeaway EIA has named

These are not the main constrained corridors in recent EIA writing. They are in the public record so the app does not drop them:

- Eagle Ford toward the Gulf and Agua Dulce. 2022 production rose 0.8 Bcf/d, 14 percent ([August 21, 2023](https://www.eia.gov/todayinenergy/detail.php?id=60180)). 2023 intrastate additions included the Eagle Ford Project at 2.0 Bcf/d and the Spears Expansion at 1.0 Bcf/d ([March 20, 2024](https://www.eia.gov/todayinenergy/detail.php?id=61623)). Verde Pipeline, up to 1.0 Bcf/d from Webb County to Agua Dulce, is a 2024 completion ([March 17, 2025](https://www.eia.gov/todayinenergy/detail.php?id=64744)).
- Bakken. North Bakken Expansion provided 0.25 Bcf/d of additional takeaway from the core Bakken in North Dakota, completed in the first quarter of 2022 ([Today in Energy, id 52478](https://www.eia.gov/todayinenergy/detail.php?id=52478)). Grasslands South added 0.1 Bcf/d from the Bakken to an interconnect in Wyoming, part of 2023 interstate additions ([March 20, 2024](https://www.eia.gov/todayinenergy/detail.php?id=61623)).

## Map styling

Draw two different balances. Do not use one red scale for both.

- Producing areas, `B_takeaway`. Amber when positive (production above local use, LNG, and outbound nameplate). Gray near zero. A pale green or neutral tone when negative, meaning spare nameplate, not a second kind of emergency. The amber is trapped supply. EIA’s picture of it is a discount to Henry Hub, as at Waha and Eastern Gas South.
- Consuming areas, `B_delivery`. Blue when positive (consumption above local production, inbound nameplate, and LNG import sendout). Gray near zero. The blue is a delivery shortfall. EIA’s picture of it is a winter premium, as at Algonquin Citygate, and an outage premium, as at Sumas in December 2022 or SoCal when westbound capacity was cut.
- Do not color Texas or Louisiana amber from `P − C_out` alone. Run the full takeaway balance so in-state power, industry, and LNG feedgas are sinks.
- Offer a winter view and a late-summer view. Appalachian pipes are most full when regional consumption is lowest. New England binds in the cold.

Bottleneck flag, drawn on top of the color, including where nameplate looks adequate:

- Takeaway flag if `B_takeaway` is positive.
- Delivery flag if `B_delivery` is positive in the season being drawn.
- Basis flag if the local hub’s discount to Henry Hub has widened the way EIA describes for Waha: compare the current basis with a period EIA treated as less constrained, rather than with a universal cutoff. The published comparison is Waha at 42 cents below Henry Hub in the second half of 2021 versus $2.07 below in 2024 through September 10, and negative absolute prices on 46 percent of 2024 trading days to that date. For a delivery region, the flag is a premium, not a discount.
- Growth flag if gross or dry production is still rising and outbound capacity additions for that geography are zero or only compressor upgrades, which is how EIA described Appalachia in 2022 and 2023.
- Outage flag if a posted operational capacity on a border constraint is below nameplate. Line 2000 is the public example: nameplate on the map would have missed a 600 MMcf/d segment out of service.

The flag can fire when the amber or blue balance is near zero. That is the point of the flag. Firm contracts, maintenance, and utilization below 100 percent leave a constraint that nameplate does not show. Do not require the flag and the color to agree.
