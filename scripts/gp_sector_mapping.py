"""Apply approved 25-09-2026 GP engineer changes from the published 695-GP master."""
import csv
import re
from pathlib import Path

MASTER = Path(__file__).resolve().parents[1] / "gp-sector-engineer-master-25-09-2026.csv"

def _key(value):
    return re.sub(r"[^A-Z0-9]", "", str(value or "").upper())

def _load():
    out = {}
    with MASTER.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            if not row["Correction"]:
                continue
            janpad = _key(row["Janpad"])
            for gp in (row["Gram_Panchayat"], row["GP_20Sep_Name"]):
                out[janpad, _key(gp)] = row["Sub_Engineer"]
    return out

OVERRIDES = _load()

def apply_sector_correction(row):
    janpad = _key(row.get("janpad") or row.get("block") or row.get("Janpad"))
    gp = _key(row.get("panchayat") or row.get("gp") or row.get("Gram_Panchayat"))
    engineer = OVERRIDES.get((janpad, gp))
    if engineer:
        row["engineer"] = engineer
    return row
