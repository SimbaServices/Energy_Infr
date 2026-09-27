import xlrd

def dump_last_nonempty(path, sheet, years=(2024, 2025)):
    wb = xlrd.open_workbook(path)
    sh = wb.sheet_by_name(sheet)
    labels = [sh.cell_value(2, c) for c in range(sh.ncols)]
    print("\nFILE", path.split("\\")[-1], "SHEET", sheet, "ncols", sh.ncols)
    # show date serial of last 3 rows
    for r in range(sh.nrows - 3, sh.nrows):
        raw = sh.cell_value(r, 0)
        dt = xlrd.xldate_as_datetime(raw, wb.datemode)
        print(" row", r, "raw", raw, "dt", dt.date())
    for r in range(3, sh.nrows):
        dt = xlrd.xldate_as_datetime(sh.cell_value(r, 0), wb.datemode)
        if dt.year in years and dt.month in (1, 6, 12):
            vals = []
            for c in range(1, sh.ncols):
                v = sh.cell_value(r, c)
                if v != "":
                    vals.append((labels[c], v))
            print(f" {dt.date()} filled {len(vals)}")
            if dt.year == 2024 or dt.month == 12 or r == sh.nrows - 1:
                for name, v in vals:
                    print(f"   {name}: {v}")


dump_last_nonempty(
    r"C:\Users\Sam Parker\Take_Action\US_Pipelines\data\raw\production\NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls",
    "Data 1",
)
wb = xlrd.open_workbook(
    r"C:\Users\Sam Parker\Take_Action\US_Pipelines\data\raw\production\NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls"
)
for name in wb.sheet_names():
    if name == "Contents":
        continue
    dump_last_nonempty(
        r"C:\Users\Sam Parker\Take_Action\US_Pipelines\data\raw\production\NG_PROD_SUM_A_EPG0_VGM_MMCF_A.xls",
        name,
        years=(2025,),
    )
