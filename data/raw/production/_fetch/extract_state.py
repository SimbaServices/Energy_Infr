"""Extract latest confirmed state production rows from EIA workbooks."""
import csv
import os
from datetime import datetime

import xlrd

BASE = r"C:\Users\Sam Parker\Take_Action\US_Pipelines\data\raw\production"


def excel_date(n):
    if n == "" or n is None:
        return ""
    if isinstance(n, str):
        return n
    # EIA dates are Excel serials
    try:
        dt = xlrd.xldate_as_datetime(float(n), 0)
    except Exception:
        return str(n)
    if dt.month == 1 and dt.day == 1 and dt.year > 1900 and float(n) % 1 == 0:
        # annual series often stored as Jan 1
        pass
    return dt


def sheet_wide(path, sheet, out_csv):
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_name(sheet)
    keys = [sh.cell_value(1, c) for c in range(sh.ncols)]
    labels = [sh.cell_value(2, c) for c in range(sh.ncols)]
    rows = []
    for r in range(3, sh.nrows):
        raw_date = sh.cell_value(r, 0)
        dt = excel_date(raw_date)
        rec = {"date": dt.strftime("%Y-%m-%d") if isinstance(dt, datetime) else str(dt)}
        for c in range(1, sh.ncols):
            rec[labels[c] or keys[c]] = sh.cell_value(r, c)
        rows.append(rec)
    last = rows[-1]
    print(path, sheet, "nrows", len(rows), "last", last["date"])
    # write full sheet csv
    with open(out_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    print(" wrote", out_csv, os.path.getsize(out_csv))
    return rows


def print_year(rows, year):
    hits = [r for r in rows if r["date"].startswith(str(year))]
    if not hits:
        print(" no rows for", year)
        return
    # if monthly, print last month of that year plus the last row overall if year is latest
    target = hits[-1]
    print(" period", target["date"])
    for k, v in target.items():
        if k == "date":
            continue
        if v != "":
            print(f"  {k}: {v}")


if __name__ == "__main__":
    dry = sheet_wide(
        os.path.join(BASE, "NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls"),
        "Data 1",
        os.path.join(BASE, "eia_dry_production_by_state_annual.csv"),
    )
    print("--- DRY last year nonempty ---")
    print_year(dry, 2025)
    print("--- DRY 2024 sample nonempty count ---")
    y2024 = [r for r in dry if r["date"].startswith("2024")][-1]
    nonempty = sum(1 for k, v in y2024.items() if k != "date" and v != "")
    print("2024 date", y2024["date"], "nonempty", nonempty, "of", len(y2024) - 1)

    mkt = sheet_wide(
        os.path.join(BASE, "ngm07_marketed.xls"),
        "Data 1",
        os.path.join(BASE, "eia_ngm07_marketed_areas_monthly.csv"),
    )
    print("--- MARKETED selected areas last row ---")
    last = mkt[-1]
    print(" period", last["date"])
    for k, v in last.items():
        if k != "date":
            print(f"  {k}: {v}")

    mkt2 = sheet_wide(
        os.path.join(BASE, "ngm07_marketed.xls"),
        "Data 2",
        os.path.join(BASE, "eia_ngm07_marketed_other_states_monthly.csv"),
    )
    print("--- OTHER last row ---")
    last = mkt2[-1]
    print(" period", last["date"])
    for k, v in last.items():
        if k != "date" and v != "":
            print(f"  {k}: {v}")

    ann = xlrd.open_workbook(os.path.join(BASE, "NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls"))
    print("annual marketed sheets", ann.sheet_names())
    sh = ann.sheet_by_index(0)
    print("contents latest")
    for r in range(min(15, sh.nrows)):
        print([sh.cell_value(r, c) for c in range(min(6, sh.ncols))])
