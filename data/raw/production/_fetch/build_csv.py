"""Build a small latest-period state production CSV from the downloaded EIA workbooks."""
import csv
import os
from datetime import datetime

import xlrd

BASE = r"C:\Users\Sam Parker\Take_Action\US_Pipelines\data\raw\production"
GAZ = os.path.join(BASE, "_fetch", "gaz", "2024_Gaz_state_national.txt")


def num(v):
    if v == "" or v is None:
        return ""
    x = float(v)
    if abs(x - round(x)) < 1e-4:
        return str(int(round(x)))
    return f"{x:.3f}".rstrip("0").rstrip(".")


def sheet_rows(path, sheet):
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_name(sheet)
    labels = [sh.cell_value(2, c) for c in range(sh.ncols)]
    out = []
    for r in range(3, sh.nrows):
        dt = xlrd.xldate_as_datetime(sh.cell_value(r, 0), wb.datemode)
        vals = {labels[c]: sh.cell_value(r, c) for c in range(1, sh.ncols)}
        out.append((dt, vals))
    return out


def load_gaz():
    # file is tab-separated, first line is header. Census files sometimes use Latin-1.
    raw = open(GAZ, "rb").read()
    text = raw.decode("latin-1")
    lines = text.splitlines()
    header = lines[0].split("\t")
    idx = {h.strip(): i for i, h in enumerate(header)}
    rows = {}
    for line in lines[1:]:
        parts = line.split("\t")
        if len(parts) < len(header):
            continue
        name = parts[idx["NAME"]].strip()
        rows[name] = {
            "usps": parts[idx["USPS"]].strip(),
            "fips": parts[idx["GEOID"]].strip(),
            "lat": parts[idx["INTPTLAT"]].strip(),
            "lon": parts[idx["INTPTLONG"]].strip(),
        }
    return rows


def area_name(label):
    # drop the metric phrase so the remainder is the geography
    cuts = [
        " Dry Natural Gas Production (Million Cubic Feet)",
        " Dry Natural Gas Production (MMcf)",
        " Dry Production of Natural Gas (Million Cubic Feet)",
        " Natural Gas Marketed Production (MMcf)",
        " Marketed Production of Natural Gas (Million Cubic Feet)",
        " Natural Gas Gross Withdrawals (MMcf)",
    ]
    compact = " ".join(label.split())
    for c in cuts:
        c2 = " ".join(c.split())
        if compact.endswith(c2):
            return compact[: -len(c2)].strip()
    return compact


def skip_area(area):
    # State onshore/offshore splits are already inside the state total.
    # Keep Federal Offshore areas; they are not inside a state total.
    if area.startswith("Federal Offshore"):
        return False
    return "--" in area or area.endswith("onshore")


def main():
    gaz = load_gaz()
    # name fixes
    gaz_alias = {
        "U.S.": None,
        "Federal Offshore--Gulf of America": None,
        "Other States": None,
    }
    rows = []

    def add(area, series, period, frequency, value, source_url, source_file):
        if skip_area(area):
            return
        meta = gaz.get(area)
        rows.append(
            {
                "area": area,
                "usps": "" if not meta else meta["usps"],
                "state_fips": "" if not meta else meta["fips"],
                "intpt_lat": "" if not meta else meta["lat"],
                "intpt_lon": "" if not meta else meta["lon"],
                "series": series,
                "period": period,
                "frequency": frequency,
                "value_mmcf": num(value),
                "source_url": source_url,
                "source_file": source_file,
            }
        )

    dry_url = "https://www.eia.gov/dnav/ng/xls/NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls"
    dry = sheet_rows(os.path.join(BASE, "NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls"), "Data 1")
    for year in (2024, 2025):
        hit = [item for item in dry if item[0].year == year]
        if not hit:
            continue
        dt, vals = hit[-1]
        for label, value in vals.items():
            if value == "":
                continue
            add(
                area_name(label),
                "dry_production",
                str(year),
                "annual",
                value,
                dry_url,
                "NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls",
            )

    mkt_url = "https://www.eia.gov/naturalgas/monthly/xls/ngm07vmall.xls"
    mkt = sheet_rows(os.path.join(BASE, "ngm07_marketed.xls"), "Data 1")
    dt, vals = mkt[-1]
    period = dt.strftime("%Y-%m")
    for label, value in vals.items():
        if value == "":
            continue
        add(
            area_name(label),
            "marketed_production",
            period,
            "monthly",
            value,
            mkt_url,
            "ngm07_marketed.xls Data 1",
        )
    mkt2 = sheet_rows(os.path.join(BASE, "ngm07_marketed.xls"), "Data 2")
    dt, vals = mkt2[-1]
    for label, value in vals.items():
        if value == "":
            continue
        add(
            area_name(label),
            "marketed_production",
            dt.strftime("%Y-%m"),
            "monthly",
            value,
            mkt_url,
            "ngm07_marketed.xls Data 2",
        )

    ann_url = "https://www.eia.gov/dnav/ng/xls/NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls"
    for sheet in ("Data 1", "Data 2"):
        ann = sheet_rows(os.path.join(BASE, "NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls"), sheet)
        for year in (2024, 2025):
            hit = [item for item in ann if item[0].year == year]
            if not hit:
                continue
            dt, vals = hit[-1]
            for label, value in vals.items():
                if value == "":
                    continue
                area = area_name(label)
                if area.startswith("Alabama--"):
                    continue
                add(
                    area,
                    "marketed_production",
                    str(year),
                    "annual",
                    value,
                    ann_url,
                    f"NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls {sheet}",
                )

    out = os.path.join(BASE, "eia_state_production_latest.csv")
    fields = list(rows[0].keys())
    with open(out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    print("rows", len(rows), "bytes", os.path.getsize(out))
    print("unmatched", sorted({r["area"] for r in rows if r["state_fips"] == "" and r["area"] not in ("U.S.", "Federal Offshore--Gulf of America", "Other States")}))


if __name__ == "__main__":
    main()
