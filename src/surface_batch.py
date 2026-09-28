#!/usr/bin/env python3
"""Stage surface parcels on this machine and append one batch over SSH.

County sites are fetched locally. The tunnel is used only for a single copy
and insert. The remote helper is deleted when the batch finishes.
"""
import argparse
import sqlite3
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STAGE = ROOT / "data" / "surface-stage"
HOST = "propeval"
KEY = str(Path.home() / ".ssh" / "id_ed25519_wellnav")
SSH = ["ssh", "-p", "2222", "-o", "ConnectTimeout=20", "-i", KEY, HOST]
SCP = ["scp", "-P", "2222", "-o", "ConnectTimeout=20", "-i", KEY]
REMOTE_ROOT = "/home/propeval/Energy_Infr/db/parcels/surface"

DDL = """
CREATE TABLE IF NOT EXISTS surface_parcels (
    prop_id TEXT PRIMARY KEY,
    county_code TEXT NOT NULL,
    county_name TEXT NOT NULL,
    tax_year INTEGER NOT NULL,
    owner_name TEXT,
    contact TEXT,
    legal_desc TEXT,
    situs TEXT,
    source_url TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS meta (
    key TEXT PRIMARY KEY,
    value TEXT
);
"""

REMOTE_HELPER = r"""
import sqlite3
from datetime import datetime, timezone
import sys
code = sys.argv[1]
src = sqlite3.connect("/tmp/surface-batch-%s.sqlite" % code)
dst_path = "/home/propeval/Energy_Infr/db/parcels/surface/tx-%s.sqlite" % code
dst = sqlite3.connect(dst_path)
dst.executescript(open("/tmp/surface-batch-ddl.sql", encoding="utf-8").read())
rows = list(src.execute("select * from surface_parcels"))
dst.executemany(
    "INSERT OR REPLACE INTO surface_parcels VALUES (?,?,?,?,?,?,?,?,?,?)",
    rows,
)
total = dst.execute("select count(*) from surface_parcels").fetchone()[0]
now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
dst.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('row_count', ?)", (str(total),))
dst.execute("INSERT OR REPLACE INTO meta(key, value) VALUES ('batch_appended_at', ?)", (now,))
dst.commit()
print(total)
"""


def stage_path(code):
    STAGE.mkdir(parents=True, exist_ok=True)
    return STAGE / f"tx-{code}.sqlite"


def open_stage(code):
    conn = sqlite3.connect(stage_path(code))
    conn.executescript(DDL)
    return conn


def add_rows(code, rows):
    conn = open_stage(code)
    conn.executemany(
        "INSERT OR REPLACE INTO surface_parcels VALUES (?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    count = conn.execute("select count(*) from surface_parcels").fetchone()[0]
    conn.close()
    return count


def flush(code):
    local = stage_path(code)
    if not local.exists():
        raise SystemExit(f"no local stage for {code}")
    ddl_path = STAGE / "ddl.sql"
    helper_path = STAGE / "flush_helper.py"
    ddl_path.write_text(DDL, encoding="utf-8")
    helper_path.write_text(REMOTE_HELPER, encoding="utf-8")
    remote_db = f"/tmp/surface-batch-{code}.sqlite"
    subprocess.check_call(SCP + [str(local), f"{HOST}:{remote_db}"])
    subprocess.check_call(SCP + [str(ddl_path), f"{HOST}:/tmp/surface-batch-ddl.sql"])
    subprocess.check_call(SCP + [str(helper_path), f"{HOST}:/tmp/surface-batch-flush.py"])
    out = subprocess.check_output(
        SSH + [f"python3 /tmp/surface-batch-flush.py {code}; rm -f /tmp/surface-batch-flush.py /tmp/surface-batch-ddl.sql {remote_db}"],
        text=True,
    )
    print(out.strip())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("command", choices=("flush",))
    parser.add_argument("code", help="county code, for example 003")
    args = parser.parse_args()
    flush(args.code)


if __name__ == "__main__":
    main()
