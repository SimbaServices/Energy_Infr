import os
import xlrd

base = r"C:\Users\Sam Parker\Take_Action\US_Pipelines\data\raw\production"
files = [
    "NG_SUM_SND_A_EPG0_FPD_MMCF_A.xls",
    "ngm07_marketed.xls",
    "ngm01_supply.xls",
    "ngm06_gross.xls",
]
for f in files:
    p = os.path.join(base, f)
    print("\n====", f, os.path.getsize(p))
    wb = xlrd.open_workbook(p)
    print("sheets", wb.sheet_names())
    for name in wb.sheet_names()[:2]:
        sh = wb.sheet_by_name(name)
        print("---", name, sh.nrows, sh.ncols)
        for r in range(min(12, sh.nrows)):
            vals = [sh.cell_value(r, c) for c in range(min(6, sh.ncols))]
            print(r, vals)
