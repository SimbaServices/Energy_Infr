# Public proxies for U.S. natural gas gathering costs

Research date: 2026-09-26. Public web pages and government or vendor PDFs only. No paywalled price-index history was purchased or reconstructed.

## Finding

There is no public series of average gathering fees, in dollars per Mcf, paid at each takeaway node. Gathering contracts are private. The Energy Information Administration (EIA) said in 2012 that it would not build a wellhead price from hub prices, because transportation, processing, and related costs are not public in a form EIA can use.

What is public, and what the database can store honestly:

- Historical U.S. wellhead prices through 2012, in $/Mcf, and Henry Hub spot prices, in $/MMBtu. These are different products and different units.
- State and U.S. citygate prices, in $/Mcf. These are a downstream local-distribution cost, past the takeaway node.
- Location value at a few hubs, as basis versus Henry Hub. EIA publishes the narratives; the daily hub history EIA cites usually comes from Natural Gas Intelligence (NGI) or, in older articles, IHS Markit. EIA does not publish a free bulk series for Waha or Eastern Gas South (formerly Dominion South).
- One government modeling assumption that bundles “transport or gathering” into a single national number: $0.36 per thousand cubic feet in 2025 dollars in the Annual Energy Outlook 2026. It is not a measured node tariff.
- Company-level FERC Form 2 gathering and transmission revenue schedules, and path-specific recourse rates on FERC eTariff. Those are pipeline filings, not a basin gathering average.

## 1. Wellhead price versus Henry Hub

EIA’s wellhead price is the reported value of marketed production divided by the quantity. EIA’s definition says that price includes costs prior to shipment from the lease, including gathering and compression, plus state production and severance charges. The series is not a pure wellhead netback, and it is not a gathering tariff.

**Last year with data: 2012.** Monthly values run through December 2012. Every month from January 2013 forward is published as not available. The page still shows that gap; the wellhead history page reviewed here was released 2026-08-31.

| Year | U.S. wellhead, nominal $/Mcf | Henry Hub spot, nominal $/MMBtu |
| --- | ---: | ---: |
| 2010 | 4.48 | 4.37 |
| 2011 | 3.95 | 4.00 |
| 2012 | 2.66 | 2.75 |

Sources: [EIA wellhead annual history](https://www.eia.gov/dnav/ng/hist/n9190us3a.htm), [EIA wellhead monthly history](https://www.eia.gov/dnav/ng/hist/n9190us3m.htm), [EIA Henry Hub annual history](https://www.eia.gov/dnav/ng/hist/rngwhhda.htm). December 2012 wellhead was $3.35/Mcf. The 2012 monthly wellhead path was $2.89, $2.46, $2.25, $1.89, $1.94, $2.54, $2.59, $2.86, $2.71, $3.03, $3.35, $3.35.

EIA stopped the series for data-quality and conceptual reasons, tied to the end of voluntary Form EIA-895. Notice: Energy Information Administration, “Notice of Change to the Publication of Natural Gas Wellhead Prices,” 77 Fed. Reg. 71788 (Dec. 4, 2012), [GovInfo](https://www.govinfo.gov/content/pkg/FR-2012-12-04/html/2012-29232.htm). Current table notes repeat the cutoff: discontinued for January 2013 forward, [EIA price definitions](https://www.eia.gov/dnav/ng/TblDefs/ng_pri_sum_tbldef2.asp).

Before the stop, EIA’s preliminary monthly wellhead price was a statistical estimate from NYMEX Henry Hub futures and spot prices at Henry Hub, Carthage, Katy, Waha, and Blanco. Hub prices used in that method included processing, gathering, and transportation fees to the hubs. The 2012 notice says a wellhead price could be derived from nearby spot prices only if transportation, processing, and related costs were known, and that EIA had no plan to do that analysis. Henry Hub spot prices were the published replacement benchmark, not a continued wellhead series.

Do not subtract $2.75/MMBtu from $2.66/Mcf and call the result a gathering cost. The units differ, the wellhead figure already folds in lease-level costs, and EIA refused that derivation.

Henry Hub annual averages on the same EIA page, nominal $/MMBtu, for recent full years: 2020 $2.03, 2021 $3.89, 2022 $6.45, 2023 $2.53, 2024 $2.19, 2025 $3.52. Monthly Henry Hub through August 2026 (page released 2026-09-23): January $7.72, February $3.62, March $3.04, April $2.77, May $2.94, June $3.15, July $2.89, August $2.78. September 2026 was not yet on that page. Source: [EIA Henry Hub monthly history](https://www.eia.gov/dnav/ng/hist/rngwhhdM.htm).

## 2. Citygate prices

A citygate is where a gas utility receives gas from a pipeline or transmission system. The citygate price is the total cost those utilities report for gas received there, including acquisition, storage, transportation, and other charges in getting gas for resale. It is collected on Form EIA-857. It sits downstream of gathering and of interstate transport. It is a reference for delivered supply cost by state, not a takeaway-node gathering fee.

U.S. average citygate price, nominal dollars per thousand cubic feet, from [EIA U.S. natural gas prices](https://www.eia.gov/dnav/ng/ng_pri_sum_dcu_nus_a.htm), confirmed on the page downloaded 2026-09-26:

| Year | U.S. citygate, $/Mcf |
| --- | ---: |
| 2020 | 3.43 |
| 2021 | 6.02 |
| 2022 | 6.87 |
| 2023 | 5.56 |
| 2024 | 4.25 |
| 2025 | 4.85 |

Natural Gas Annual Table 22 gives the state detail for 2020–2024, also in nominal dollars per thousand cubic feet: [table_022.pdf](https://www.eia.gov/naturalgas/annual/pdf/table_022.pdf). The 2024 U.S. total in that table is $4.25/Mcf, matching the national page. Selected 2024 state citygates near producing areas:

| State | 2024 citygate, $/Mcf |
| --- | ---: |
| New Mexico | 3.39 |
| Texas | 3.25 |
| Colorado | 3.69 |
| Wyoming | 3.91 |
| Louisiana | 3.91 |
| North Dakota | 4.37 |
| West Virginia | 4.38 |
| Arkansas | 4.65 |
| Pennsylvania | 4.61 |
| Ohio | 4.92 |
| Oklahoma | 6.19 |
| U.S. | 4.25 |

Across all states in that 2024 table, the low is Idaho at $2.84/Mcf and the high is Hawaii at $24.03/Mcf. Hawaii is an LNG-supplied market and is not a lower-48 gathering analog. Some 2025 state cells on the data browser were unavailable (the national $4.85 average is the firm 2025 figure confirmed here).

For scale only, the same national price page shows 2025 residential at $15.34/Mcf and electric power at $4.02/Mcf. Those are end-use prices, further downstream than citygate.

## 3. Basis as a location-value proxy

Define basis the way this database should store it:

**basis = hub price − Henry Hub price**

A producing hub that trades below Henry Hub has a negative basis. EIA articles sometimes describe the same fact as “dollars below Henry Hub,” which is the positive gap. They are the same observation with the sign flipped. Keep one sign in the database and document it.

Basis is the market value of pipeline-quality gas at a hub relative to Henry Hub. It is measured at the hub, after gas has already been gathered. A wide negative basis can be many dollars and can go below zero when takeaway is full. That is a capacity discount, not a gathering fee. Store it as observed location value. Do not copy it into a gathering-cost column.

EIA’s own daily republication of Intercontinental Exchange (ICE) prices covers a short list of hubs used beside electricity markets (Algonquin Citygates, TETCO-M3, Chicago Citygates, Henry, Malin, PG&E Citygate, SoCal), from March 2014. It does not include Waha or Dominion South / Eastern Gas South. Source: [EIA wholesale markets](https://www.eia.gov/electricity/wholesale/).

Confirmed EIA figures that cite commercial index providers:

**Waha (Permian takeaway hub), versus Henry Hub, $/MMBtu.** [EIA Today in Energy, Sept. 10, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63044), prices from NGI:

- Year to date 2024 through that article: Waha averaged $2.07 below Henry Hub, so basis = −$2.07/MMBtu.
- Second half of 2021: Waha averaged $0.42 below Henry Hub, so basis = −$0.42/MMBtu.
- Waha was below zero on 46% of trading days in 2024 through the article date, including every day since July 26, 2024. Lowest print cited: −$6.41/MMBtu on August 29, 2024.

[EIA Natural Gas Weekly Update for Aug. 21–28, 2024](https://www.eia.gov/naturalgas/weekly/archivenew_ngwu/2024/08_29/), also citing NGI: on Aug. 28, 2024, Henry Hub was $1.89/MMBtu and Waha was −$3.67/MMBtu, so that day’s basis was −$5.56/MMBtu. The same update said Waha had been below zero on 45% of 2024 trading days as of that week. The share differs from the Sept. 10 article because the as-of dates differ. Store the as-of date with the figure.

**Eastern Gas South, formerly Dominion South (Appalachia).** [EIA Today in Energy, Oct. 23, 2024](https://www.eia.gov/todayinenergy/detail.php?id=63504) says prices there tend to be discounted to Henry Hub because Appalachian supply exceeds local demand and takeaway is constrained. That article does not print a numeric average basis.

Older EIA numeric spreads, described as dollars lower than Henry Hub (database basis = the negative of these amounts):

- [EIA Today in Energy, Aug. 2, 2018](https://www.eia.gov/todayinenergy/detail.php?id=36772), with IHS Markit: summer 2015 Dominion South was $1.48/MMBtu lower; summer 2017 it was $1.07/MMBtu lower; winter spreads “in recent years” averaged $0.90/MMBtu lower. June 2018: Dominion South $0.71/MMBtu lower; Marcellus hub $1.01/MMBtu lower; Leidy $1.04/MMBtu lower.
- [EIA Today in Energy, Aug. 2020 differentials article](https://www.eia.gov/todayinenergy/detail.php?id=45037): as of Aug. 17, 2020, S&P Global Market Intelligence forward basis swaps for winter 2020–21 were Waha −$0.47/MMBtu and Dominion South −$0.48/MMBtu. Those are forward quotes cited by EIA, not a historical spot average. The same snapshot had SoCal Citygate +$1.11, Algonquin Citygate +$2.28, and Transco Zone 5 +$0.95, which are demand-area premia, not gathering.

Hubs that can stand in for takeaway nodes in the public record: Waha for the Permian; Eastern Gas South (and, in older EIA text, Dominion South, Leidy, and a Marcellus hub) for Appalachia. Haynesville liquidity is discussed by EIA around the Houston Ship Channel and Gulf Coast connections, not as a published Haynesville gathering tariff.

## 4. Tariffs, transport rates, and published cost ranges

### EIA model assumption (the only government $/Mcf “gathering” number confirmed)

In the Natural Gas Market Module, EIA sets each supply-node “wellhead” price equal to the model spot price minus one assumed transport or gathering charge. The charge does not vary by basin. Variable pipeline tariffs on state-to-state routes are separate curves, fit to historical basis, capacity, and flows, and they rise when a route is full.

| Outlook | Assumption | Dollar year | Status |
| --- | --- | --- | --- |
| AEO 2026 assumptions, April 2026 | $0.36 per thousand cubic feet | 2025 dollars | Current model input |
| AEO 2025 assumptions | $0.35 per thousand cubic feet | 2024 dollars | Prior model input |
| AEO 2022 assumptions | $0.31 per thousand cubic feet | 2021 dollars | Prior model input |

Sources: [AEO 2026 Natural Gas Market Module assumptions (PDF)](https://www.eia.gov/outlooks/aeo/assumptions/pdf/NGMM_Assumptions.pdf); AEO 2025 assumptions PDF (same EIA series; a public copy is also archived by Catalyst Cooperative); [AEO 2022 assumptions on energy.gov](https://www.energy.gov/documents/44-eia-assumptions-annual-energy-outlook-2022pdf).

Label every one of these **estimated**, method `EIA NGMM uniform transport-or-gathering subtraction`, geography `national supply node`, not a named takeaway hub. The wording is “transport or gathering.” It is not an observed fee and not a range.

### FERC

FERC Form 2 (major interstate pipelines) is a public financial report. The instructions include schedules for revenues from transportation of gas of others through gathering facilities (pages 302–303) and through transmission facilities (pages 304–305), plus quantities by rate schedule. A company-level average could be computed later as gathering revenue divided by gathering quantity for filers that report both. That average is an observed FERC accounting statistic for that pipeline’s reported gathering, for that year. It is not a node tariff, and many gathering systems never file it. Form landing page: [FERC Form 2](https://www.ferc.gov/industries-data/natural-gas/resources/industry-forms/form-no-2-major-natural-gas-pipeline-annual). Blank form with the schedule list: [form-2.pdf](https://www.ferc.gov/sites/default/files/2021-05/form-2.pdf).

Recourse rates live in individual tariff sheets on [FERC eTariff](https://etariff.ferc.gov/). They are path- and pipeline-specific ceiling rates for interstate transportation. They are not a published gathering menu by basin. No national FERC summary of gathering cost in $/Mcf was found.

Negotiated interstate rates may reference basis. FERC treats basis as a market signal of the value of capacity between two points, including cases where a wide basis suggests more capacity is needed. That policy history is in the Jan. 26, 2006 rehearing order, [71 Fed. Reg. 4362 and related notices](https://www.govinfo.gov/content/pkg/FR-2006-01-26/pdf/E6-993.pdf). It authorizes a pricing mechanism. It does not publish the gathering fees producers pay.

### Vendor full-cycle studies (do not store as gathering tariffs)

Incorrys, “North American Oil and Gas Full Cycle Cost,” August 2021, public PDF: [incorrys.com](https://www.incorrys.com/videos/NorthAmericanOilandGasFulCycleCost-Aug2021.pdf). Two sentences are relevant and must stay labeled as vendor estimates:

- Haynesville processing and gathering “can be as low as” $0.30–$0.40/Mcf. That is a combined floor, not an average tariff, and it includes processing.
- Stated basis differentials of about −$0.11/Mcf in the Haynesville and −$0.84/Mcf in the Marcellus and Utica. These are components of their full-cycle cost, not EIA spot prints.

Incorrys, “North American Natural Gas Full Cycle Cost and Resources,” April 2025, public PDF: [incorrys.com](https://www.incorrys.com/videos/NorthAmericanGasCost-April2025.pdf). Scope is wells drilled from Q1 2022 through Q3 2024. “Assumed HH differential” means the Henry Hub gap they put into the cost model. Operating cost in this deck is lifting and field processing, which is wider than gathering. Full-cycle breakevens are not gathering costs. Confirmed assumed differentials and operating costs:

| Area | Assumed HH differential | Average operating cost | What operating cost includes |
| --- | ---: | ---: | --- |
| Haynesville | $0.15/Mcf | $0.86/Mcf | Lifting and field processing, per their component note |
| Marcellus NE | $0.73/Mcf | $1.13/Mcf | Same |
| Marcellus SW | $0.73/Mcf | $2.09/Mcf | Same |
| Utica | $0.73/Mcf | $1.08/Mcf | Same |
| Permian | $1.04/Mcf | $1.46/Mcf | Same |
| Eagle Ford | $1.04/Mcf | $2.23/Mcf | Same |

The April 2025 summary full-cycle costs (Utica $1.92/Mcf, Marcellus $3.39, Haynesville $3.43, Permian $5.66) include capital, return, royalties, basis, and liquids. Do not load them as gathering.

EIA’s lease-equipment and operating-cost study runs through 2009 and is an equipment and lifting-cost index, not a gathering tariff. It was not used for any $/Mcf gathering figure here.

## 5. Recommended database method

Store three layers. Only the third is an estimate, and only when a public document states a gathering or bundled gathering-and-transport figure.

**Observed prices.** One row per place, period, and series. Places are hubs or states, not an inferred lease. Keep the published unit. Henry Hub and most hub indexes are $/MMBtu. Wellhead and citygate are $/Mcf. Do not convert them onto one unit inside the load. If a later step converts, store the heat-content factor as its own field and cite it.

**Observed basis.** For a hub that has a same-day or same-month price in the same unit as Henry Hub: `basis = hub_price - henry_hub_price`. This is location value at the hub. It can be negative and it can exceed any plausible gathering fee. Column role stays `basis`, not `gathering_cost`.

**Estimated gathering.** Leave the gathering-cost fields null unless a cited public report gives a number or a range for gathering, or for a bundle that the report itself names as gathering. Record the range as published (`low` and `high`) when the source says “as low as” or gives a band. Record a point only when the source gives a point. The AEO $0.36/Mcf (2025 dollars) may be stored once, scoped to the national model, as an estimate. It should not be copied onto Waha, Eastern Gas South, or any other node as if it were measured there.

Suggested columns:

| Column | Contents |
| --- | --- |
| `place_id` | Hub, state, pipeline, or `US_NGMM`. No fake node id. |
| `period` | Year, month, or the article’s as-of date. |
| `series` | `wellhead`, `henry_hub`, `citygate`, `hub_spot`, `basis`, `gathering_cost`. |
| `value` | Number as published. Null if the source gives only a range. |
| `value_low`, `value_high` | Used when the source gives a band. |
| `unit` | `USD_per_Mcf` or `USD_per_MMBtu`. |
| `dollar_year` | `nominal`, or the real-dollar year the source names (2025, 2024, 2021). |
| `observation_type` | `observed` or `estimated`. |
| `method` | Short label, for example `EIA-857 citygate`, `hub minus Henry Hub`, `EIA NGMM uniform transport-or-gathering subtraction`, `Incorrys Aug 2021 processing and gathering floor`. |
| `source` | Agency or publisher, document title, table. |
| `source_url` | Public URL. |
| `source_year` | Year of the statistic, plus the publication date if the figure is year-to-date. |

Practical load for this project:

1. Load EIA Henry Hub (daily or monthly) as `observed`.
2. Load EIA citygate by state and the U.S. total as `observed`, `series = citygate`. Keep it in a downstream table so it is not joined as a gathering fee.
3. Load EIA wellhead only through 2012, `observed`, with `method` noting the series ended and that the price already includes lease-level costs.
4. Load basis only where both legs are observed in $/MMBtu. For Waha and Eastern Gas South, EIA articles are spot citations with as-of dates, not a complete history. A full history needs a licensed index or a later public extract. Do not fill gaps with modeled basis.
5. Insert gathering estimates only for the rows in the table below. Everywhere else, `gathering_cost` stays null.

### Rows that may be stored as gathering estimates

| Place | Period | Type | Value | Unit | Method | Source |
| --- | --- | --- | --- | --- | --- | --- |
| National NGMM supply node | AEO 2026 (assumptions dated April 2026) | estimated | 0.36 | $/Mcf, 2025 dollars | Uniform subtraction from spot to create a model wellhead; transport or gathering, not separated, not by basin | EIA NGMM assumptions |
| National NGMM supply node | AEO 2025 | estimated | 0.35 | $/Mcf, 2024 dollars | Same method, prior vintage | EIA NGMM assumptions |
| National NGMM supply node | AEO 2022 | estimated | 0.31 | $/Mcf, 2021 dollars | Same method, prior vintage | EIA, AEO 2022 assumptions |
| Haynesville | August 2021 vendor deck | estimated | 0.30–0.40, described as “as low as” | $/Mcf | Processing and gathering together; a floor, not an average paid fee | Incorrys full-cycle cost, Aug. 2021 |

No other $/Mcf gathering figure in this review was both public and actually a gathering cost. Basis figures, citygate prices, full-cycle breakevens, and FERC transmission recourse rates stay in their own series.
