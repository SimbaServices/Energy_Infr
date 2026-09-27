# U.S. transmission and interconnection costs

Research date: 2026-09-26. Public sources only (MISO, DOE/NREL National Transmission Planning Study, LBNL, EIA). No paywalled figures are used.

Industry sources publish new-line costs in **$/mile** (sometimes by state and voltage) or, less often, in **$/MW-mile**. They do not publish a tariff in **$/MWh/mile**. Section 3 gives an illustrative conversion only. Database fields in Section 4 stay null wherever a number was not printed by a source.

## 1. New transmission line costs by voltage

Two recent public tables cover the requested voltages. They are not interchangeable: different geographies, dollar years, and what is included. Do not average them into one national number.

### 1.1 MISO exploratory costs, $/mile

**Source:** Midcontinent Independent System Operator, *Transmission Cost Estimation Guide for MTEP24*, May 1, 2024.  
**URL:** https://cdn.misoenergy.org/20240501%20PSC%20Item%2004%20MISO%20Transmission%20Cost%20Estimation%20Guide%20for%20MTEP24632680.pdf

Tables 4.1-1 and 4.1-2 give exploratory **$/mile** by MISO state for new AC lines. Each figure **includes 30% contingency and 7.5% allowance for funds used during construction (AFUDC)**. MISO says these are high-level screening estimates and should not be used as the planning-cycle cost of a specific solution (Section 4).

**Dollar year (quoted as printed).** The opening paragraph says both of the following: “All cost estimate data in this document are in 2023 U.S. dollars. Cost data was escalated from 2023 U.S. dollars to 2024 U.S. dollars at a rate of 5%.” The guide does not resolve that conflict. The ranges below are the table values, not a further inflation of those values.

A later guide, *Transmission Cost Estimation Guide for MTEP25* (2025 dollars; most categories escalated 4% from 2024), states that exploratory $/mile costs are in workbook Tables 4.1-1 through 4.1-4. Those workbook numbers were not extracted here, so **no 2025 $/mile figures are reported**.  
**URL:** https://cdn.misoenergy.org/MISO%20Transmission%20Cost%20Estimation%20Guide%20for%20MTEP25337433.pdf

Ranges below are the minimum and maximum across the states printed in the MTEP24 tables (Arkansas, Illinois, Indiana, Iowa, Kentucky, Louisiana, Michigan, Minnesota, Mississippi, Missouri, Montana, North Dakota, South Dakota, Texas, Wisconsin). This is a MISO-footprint state range, not a U.S. national range.

| Voltage | New single circuit, $/mile | New double circuit, $/mile |
| --- | --- | --- |
| 115 kV | $1.8 million–$2.2 million | $2.6 million–$3.1 million |
| 230 kV | $2.0 million–$2.6 million | $3.3 million–$4.0 million |
| 345 kV | $3.2 million–$4.1 million | $5.5 million–$6.4 million |
| 500 kV | $4.1 million–$5.1 million | not published (Table 4.1-2 stops at 345 kV) |

Low end of each single-circuit range is Montana (115, 230, and 345 kV) or Montana / North Dakota / South Dakota (500 kV). High end is Louisiana and/or Mississippi, except 115 kV single circuit, where Louisiana, Mississippi, and Texas are all $2.2 million/mile.

**$/MW-mile is not published.** Table 3.1-5 does publish the exploratory conductor’s power rating, which is the input a model would need before any per-MW figure could be calculated:

| Voltage | Conductor (per circuit) | Power rating |
| --- | --- | --- |
| 115 kV | 1 × 795 kcmil ACSS | 329 MVA |
| 230 kV | 1 × 795 kcmil ACSS | 657 MVA |
| 345 kV | 2 × 795 kcmil ACSS | 1,792 MVA |
| 500 kV | 3 × 954 kcmil ACSR | 2,598 MVA |

Related, still in the same guide (Table 4.2-1), exploratory **substation** costs to add one position, including the same 30% contingency and 7.5% AFUDC. These are lump sums, not $/mile or $/kW:

| Voltage | Ring bus | Breaker-and-a-half | Double-breaker |
| --- | --- | --- | --- |
| 115 kV | $1.5 million | $2.0 million | $2.3 million |
| 230 kV | $2.2 million | $3.0 million | $3.4 million |
| 345 kV | $3.4 million | $4.9 million | $5.4 million |
| 500 kV | $5.3 million | $7.3 million | $8.0 million |

### 1.2 DOE / NREL National Transmission Planning Study base costs, $/mile

**Source:** U.S. Department of Energy, Grid Deployment Office, with NREL and PNNL, *National Transmission Planning Study*, Chapter 3, Appendix D, Table D-4, “Cost per Mile by Voltage Class.” Publication line in the chapter: October 2024 (DOE/GO-102024).  
**URL:** https://www.energy.gov/sites/default/files/2024-10/NationalTransmissionPlanningStudy-Chapter3.pdf

Table D-4 is a **base** cost before land-cover and terrain multipliers (Table D-3; multipliers from 1.0 on scrubbed/flat and farmland up to 2.25 on forested). Conductor is ACSR. The appendix says these base costs come from the WECC Transmission Calculator (Black & Veatch 2019), updated by E3 (2019). **No dollar year is printed on Table D-4.** Chapter 2 of the same study says real 2022 dollars are used unless otherwise noted; that sentence is not attached to Table D-4, so the table’s dollar year is left unspecified here.

| Voltage class | Cost per mile |
| --- | --- |
| 230 kV single circuit | $1,024,335 |
| 230 kV double circuit | $1,639,820 |
| 345 kV single circuit | $1,434,290 |
| 345 kV double circuit | $2,295,085 |
| 500 kV single circuit | $2,048,670 |
| 500 kV double circuit | $3,278,535 |

**115 kV is not in Table D-4.**

Chapter 2 states that interzonal AC costs in the capacity-expansion model are based on greenfield **500 kV, 1,500 MW, single-circuit** lines, expressed to the model in **$/MW-mile**, and that the resulting geographic costs are in Figure A-1. The figure’s dollar amounts are not printed in the text, so **no numeric $/MW-mile from that figure is recorded**. Text that is printed (Appendix A):

- DC line costs are assumed to be about **60% less** than the $/MW-mile costs shown in Figure A-1 for AC, based on the MISO 2021 cost guide.
- Converter stations: **$140/kW** for line-commutated converters and back-to-back ties, and **$180/kW** for voltage-source converters, also based on MISO 2021.
- A doubled-cost sensitivity applies a factor of 2 to interzonal $/MW-mile costs.

**Chapter 2 URL:** https://www.energy.gov/sites/default/files/2024-10/NationalTransmissionPlanningStudy-Chapter2.pdf

### 1.3 EIA

EIA states that it publishes utility transmission **expenditures** (Electric Power Annual, Table 8.3) and electricity **price** projections, and that it **does not publish** the cost to build or operate transmission lines. No EIA $/mile or $/MW-mile figure is available to store.  
**URL:** https://www.eia.gov/tools/faqs/faq.php?id=947&t=3

### 1.4 PJM, SPP, CAISO line-construction unit costs

No public PJM, SPP, or CAISO study located in this pass prints a 2024–2026 $/mile table for 115, 230, 345, and 500 kV comparable to the MISO guide. Those fields stay null rather than being inferred from MISO.

## 2. Generator interconnection costs (LBNL), $/kW

These are **study estimates** of the upgrades assigned to a generator (point of interconnection and broader network), in **$/kW of nameplate capacity**. They are not line construction costs in $/mile, and they are not $/MWh. LBNL notes that point-of-interconnection categories often **exclude** customer-owned equipment such as the generator step-up transformer and spur line. Withdrawn projects generally do not pay the full quoted cost. Means are pulled upward by a small number of high-cost projects; medians are lower where reported.

Hub for the briefs and project-level files: https://emp.lbl.gov/interconnection_costs

LBNL’s 2023 webinar states that **CAISO does not disclose project-level interconnection costs**, so there is no CAISO $/kW series in this set.  
**URL:** https://eta-publications.lbl.gov/sites/default/files/berkeley_lab_interconnection_cost_webinar.pdf

Dollar basis for the five ISO briefs below is **real 2022 dollars** (GDP deflator, nominal dollars as of the study year). The February 2026 non-ISO brief is **real 2024 dollars**. Do not pool those two dollar years into one number.

| Region | Recent window | Complete, mean $/kW | Active, mean $/kW | Withdrawn, mean $/kW | Report |
| --- | --- | --- | --- | --- | --- |
| MISO | 2019–2021 (active comparison is 2018 vs. 2019–2021) | 102 | 156 | 452 | Seel et al., October 2022. https://eta-publications.lbl.gov/sites/default/files/berkeley_lab_2022.10.06-_miso_interconnection_costs.pdf |
| PJM | Complete: 2020–2022 vs. 2000–2019. Active: 2020–2022. Withdrawn: recent mean as stated in the executive summary | 84 (median 30) | 240 (median 85) | 599 (median 244) | Seel et al., January 2023. https://eta-publications.lbl.gov/sites/default/files/berkeley_lab_2023.1.12-_pjm_interconnection_costs.pdf |
| SPP | 2020–2022 (active text: 2020–2023) | 57 | 106 (median 66) | 304 (median 184) | Seel et al., April 20, 2023. https://eta-publications.lbl.gov/sites/default/files/berkeley_lab_2023.04.20-_spp_interconnection_costs.pdf |
| NYISO | 2017–2021 | 234 (median 150) | 145 (median 108) | 241 (median 129) | Mulvaney Kemp et al., March 2023. https://eta-publications.lbl.gov/sites/default/files/nyiso_interconnection_costs_vfinal.pdf |
| ISO-NE | 2018–2021 | 114 (median 104) | 233 (median 126) | 613 (median 455) | Mulvaney Kemp et al., June 2023. https://eta-publications.lbl.gov/sites/default/files/iso-ne_interconnection_costs_vfinal.pdf |
| Non-ISO sample (PacifiCorp, BPA, Duke Energy Progress, Duke Energy Carolinas, Duke Energy Florida) | 2018–2024, real 2024$ | 194 | 294 | 671 | Seel et al., February 2026. https://eta-publications.lbl.gov/sites/default/files/2026-02/lbnl_2026.02.23_ba_interconnection_costs.pdf |

Within that non-ISO sample, recent average costs for **complete** projects are lowest at BPA (**$56/kW**) and highest at Duke Energy Carolinas (**$497/kW**). PacifiCorp has the most observations and pulls the pooled non-ISO mean up.

Point-of-interconnection vs. network, where the briefs split recent complete or recent projects (same dollar years and URLs as the table):

- **MISO, complete, 2018–2021:** local facilities about **$46/kW**. Network upgrades for complete projects **$57/kW** in 2019–2021. Withdrawn projects, recent: about **$67/kW** at the point of interconnection and **$388/kW** in network upgrades.
- **PJM, recent:** point-of-interconnection means about **$12/kW** (complete) and **$13/kW** (active). Network means **$71/kW** (complete), **$227/kW** (active), and **$563/kW** (withdrawn).
- **SPP, complete, 2020–2022:** point-of-interconnection about **$34/kW**; network about **$23/kW**.

For a map of an expected interconnect cost, the **complete** means are the projects that finished studies. **Active** means are higher and still preliminary. **Withdrawn** means describe projects that left the queue, often because the quoted network upgrades were large; they are a poor estimate of cost actually paid.

## 3. Illustrative conversion to $/MWh/mile

This is an illustration for labeling a map, **not a tariff, not a revenue requirement, and not a sourced database value.**

### Formula

If a capital cost is already in dollars per MW-mile:

`cost_usd_per_mwh_mile = cost_usd_per_mw_mile / (assumed_capacity_factor × hours_per_year × recovery_years)`

Assumptions used for the worked example:

| Input | Value | Why this value |
| --- | --- | --- |
| `hours_per_year` | 8,760 | Hours in a non-leap year |
| `assumed_capacity_factor` | 0.40 | Illustrative utilization of the circuit rating. It is not a plant-specific capacity factor and not a published transmission load factor. |
| `recovery_years` | 40 | MISO’s depreciable life in the same MTEP24 guide (Section 5: 40-year life, 2.5% straight-line depreciation per year). |

Denominator = 0.40 × 8,760 × 40 = **140,160 MWh per MW** over the recovery period.

This spreads **capital cost only**, in a straight line, with no return on capital, income tax, property tax, or operations and maintenance. MISO’s own benefit-cost method uses the present value of the first 20 years of annual revenue requirements and is a different calculation. Because return and taxes are omitted, this illustration is **lower than a transmission charge**.

### Worked example (derived, not a published $/MW-mile)

MISO does not publish $/MW-mile. The steps below divide the published 345 kV single-circuit range by the published 1,792 MVA rating, treating MVA as if it were MW. That overstates transferable MW whenever the line is not at unity power factor, and it therefore **understates** dollars per MWh.

- Low: $3,200,000 per mile / 1,792 MVA = **$1,785.71 per MVA-mile**
- High: $4,100,000 per mile / 1,792 MVA = **$2,287.95 per MVA-mile**

Then:

- $1,785.71 / 140,160 = **$0.0127 per MWh per mile**
- $2,287.95 / 140,160 = **$0.0163 per MWh per mile**

So, under these assumptions only, a 345 kV single-circuit MISO exploratory capital cost illustrates about **$0.013–$0.016 per MWh per mile**. Label it as an illustration. Do not store it in `cost_usd_per_mwh_mile` as a sourced value.

The same formula can be applied to any other voltage **after** a sourced $/mile is divided by a sourced MW (or MVA, labeled as MVA) rating. Until that division is an explicit method step, leave `cost_usd_per_mw_mile` and `cost_usd_per_mwh_mile` null.

## 4. Recommended database fields

Use one row per source, voltage, and circuit type. Store a range when the source published a range. Leave a field null when the source did not publish that unit.

Suggested columns, matching the request, plus `circuit` and `geography` so single-circuit and double-circuit rows and MISO-vs-national scope are not collapsed:

`voltage_kv`, `circuit`, `geography`, `cost_usd_per_mile`, `cost_usd_per_mw_mile`, `assumed_capacity_factor`, `cost_usd_per_mwh_mile`, `method`, `source`, `year`

| voltage_kv | circuit | geography | cost_usd_per_mile | cost_usd_per_mw_mile | assumed_capacity_factor | cost_usd_per_mwh_mile | method | source | year |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 115 | single | MISO states in Table 4.1-1 | 1800000–2200000 | null | null | null | Exploratory capital cost; includes 30% contingency and 7.5% AFUDC. Dollar-year sentence in the guide conflicts (2023 and 2024). | MISO Transmission Cost Estimation Guide for MTEP24, Table 4.1-1 | 2024 |
| 230 | single | MISO states in Table 4.1-1 | 2000000–2600000 | null | null | null | same | same, Table 4.1-1 | 2024 |
| 345 | single | MISO states in Table 4.1-1 | 3200000–4100000 | null | null | null | same | same, Table 4.1-1 | 2024 |
| 500 | single | MISO states in Table 4.1-1 | 4100000–5100000 | null | null | null | same | same, Table 4.1-1 | 2024 |
| 115 | double | MISO states in Table 4.1-2 | 2600000–3100000 | null | null | null | same | same, Table 4.1-2 | 2024 |
| 230 | double | MISO states in Table 4.1-2 | 3300000–4000000 | null | null | null | same | same, Table 4.1-2 | 2024 |
| 345 | double | MISO states in Table 4.1-2 | 5500000–6400000 | null | null | null | same | same, Table 4.1-2 | 2024 |
| 500 | double | MISO | null | null | null | null | not published | same, Table 4.1-2 | 2024 |
| 115 | — | NTP Study Table D-4 | null | null | null | null | not in table | DOE/NREL/PNNL National Transmission Planning Study, Chapter 3, Table D-4 | 2024 |
| 230 | single | Base cost before terrain multiplier; dollar year not printed on the table | 1024335 | null | null | null | WECC Transmission Calculator (Black & Veatch 2019) as updated by E3 (2019); ACSR | same, Table D-4 | 2024 |
| 345 | single | same | 1434290 | null | null | null | same | same, Table D-4 | 2024 |
| 500 | single | same | 2048670 | null | null | null | same | same, Table D-4 | 2024 |
| 230 | double | same | 1639820 | null | null | null | same | same, Table D-4 | 2024 |
| 345 | double | same | 2295085 | null | null | null | same | same, Table D-4 | 2024 |
| 500 | double | same | 3278535 | null | null | null | same | same, Table D-4 | 2024 |

`cost_usd_per_mw_mile`, `assumed_capacity_factor`, and `cost_usd_per_mwh_mile` are null on every sourced row. The 0.40 / 8,760 / 40 illustration in Section 3 is a method note, not a sourced field value.

Generator interconnection costs are a different object. Keep them in a separate table, for example `region`, `request_status`, `cost_usd_per_kw_mean`, `cost_usd_per_kw_median`, `dollar_year`, `study_window`, `source`, `year`, and do not write those $/kW figures into `cost_usd_per_mile`.

## 5. What the map should show

Use **MISO Table 4.1-1 single-circuit $/mile** when the segment voltage is 115, 230, 345, or 500 kV and a MISO-footprint screening cost is acceptable. Show the **range**, not a midpoint that the guide did not publish.

Use **NTP Study Table D-4** only if the map is explicitly using that base cost, and show that terrain multipliers are not yet applied and that 115 kV is missing.

If the map must display **$/MWh/mile**, compute it in the legend from Section 3 and mark it “illustration, not a tariff.” Leave the stored `cost_usd_per_mwh_mile` null until that method is applied in code from the sourced $/mile and a stated rating.
