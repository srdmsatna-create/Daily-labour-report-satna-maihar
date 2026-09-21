#!/usr/bin/env python3
"""Import a verified R6.12 workbook into the work-level dashboard data.

Only Ongoing rows are exported.  The reviewed MGNREGA-to-30-June fields in
the workbook are kept fixed, while the current VB-G RAM G values come from
the imported snapshot. Existing Apr-Jun/recovery fields are retained by Work
Code where the workbook does not contain an equivalent split.
"""
import argparse
import json
from collections import Counter
from pathlib import Path

from openpyxl import load_workbook

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "ongoing-details.js"
NREGA_BASELINE = ROOT / "nrega-r612-baseline.json"


def clean(value):
    return "" if value is None else str(value).strip()


def num(value):
    try:
        return float(str(value).replace(",", "").strip() or 0)
    except Exception:
        return 0.0


def load_previous():
    if not OUT.exists():
        return {}
    text = OUT.read_text(encoding="utf-8-sig").strip()
    prefix = "window.ONGOING_DETAILS="
    if not text.startswith(prefix):
        raise SystemExit("Existing ongoing-details.js format is not recognized")
    rows = json.loads(text[len(prefix):].rstrip(";"))
    return {clean(row.get("code")): row for row in rows if clean(row.get("code"))}


def load_nrega_baseline():
    if not NREGA_BASELINE.is_file():
        raise SystemExit(f"MGNREGA baseline not found: {NREGA_BASELINE}")
    raw = json.loads(NREGA_BASELINE.read_text(encoding="utf-8-sig"))
    return {clean(code): values for code, values in raw.items() if clean(code)}


def normalized_category(raw, old):
    category = clean(raw)
    if category == "IAY Houses":
        return "PMAY-G"
    if category == "Ek Bagiya Maa Ke Naam":
        return "Ek Bagiya"
    if category == "Ek Bagiya — older FY (outside selected scope)":
        return clean(old.get("finalCategory")) or "Gap Filling in Plantation"
    return category or clean(old.get("finalCategory")) or "Other Works"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook", type=Path)
    args = parser.parse_args()
    if not args.workbook.is_file():
        parser.error("Workbook not found")

    previous = load_previous()
    nrega_baseline = load_nrega_baseline()
    book = load_workbook(args.workbook, read_only=True, data_only=True)
    if "All Works" not in book:
        raise SystemExit("Required 'All Works' sheet is missing")
    values = book["All Works"].values
    columns = list(next(values))
    ix = {name: i for i, name in enumerate(columns)}
    required = [
        "Work Status", "Work Code", "Work Name", "Work Start Fin Yr",
        "Work Type", "Final Category", "District", "Janpad", "Panchayat",
        "Sanction Total Rs", "Since Inception Booked Wages Rs",
        "Since Inception Booked Material Rs", "Current FY Booked Wages Rs",
        "Current FY Booked Material Rs", "Total Mandays (portal)",
        "Current FY Mandays (portal)",
        "MGNREGA Booked Wages to 30 Jun Rs (fixed)",
        "MGNREGA Booked Material to 30 Jun Rs (fixed)",
        "Previous Mandays in 13 Sep file (fixed)",
        "Sub Engineer / Upyantri (13 Sep mapping)", "Cluster (13 Sep mapping)",
    ]
    missing = [name for name in required if name not in ix]
    if missing:
        raise SystemExit("Missing workbook columns: " + ", ".join(missing))

    rows = []
    codes = set()
    for source in values:
        if clean(source[ix["Work Status"]]).upper() != "ONGOING":
            continue
        code = clean(source[ix["Work Code"]])
        if not code:
            continue
        if code in codes:
            raise SystemExit("Duplicate Work Code: " + code)
        codes.add(code)
        old = previous.get(code, {})
        sanction = num(source[ix["Sanction Total Rs"]])
        # The workbook is generated with lookup formulae.  In a non-Excel run their
        # cached values can be zero, so use the reviewed fixed baseline by Work Code.
        # Only genuinely new/unmatched works fall back to the workbook's fixed fields.
        fixed = nrega_baseline.get(code)
        if fixed is not None:
            nrega_wage = num(fixed[0] if len(fixed) > 0 else 0)
            nrega_material = num(fixed[1] if len(fixed) > 1 else 0)
        else:
            nrega_wage = num(source[ix["MGNREGA Booked Wages to 30 Jun Rs (fixed)"]])
            nrega_material = num(source[ix["MGNREGA Booked Material to 30 Jun Rs (fixed)"]])
        vbg_wage = num(source[ix["Current FY Booked Wages Rs"]])
        vbg_material = num(source[ix["Current FY Booked Material Rs"]])
        # Dashboard definition: Overall = fixed MGNREGA + current VB-G RAM G.
        overall_wage = nrega_wage + vbg_wage
        overall_material = nrega_material + vbg_material
        overall = overall_wage + overall_material
        current_mandays = num(source[ix["Current FY Mandays (portal)"]])
        previous_mandays = num(source[ix["Previous Mandays in 13 Sep file (fixed)"]])
        rows.append({
            "sno": len(rows) + 1,
            "district": clean(source[ix["District"]]),
            "janpad": clean(source[ix["Janpad"]]).upper(),
            "engineer": clean(source[ix["Sub Engineer / Upyantri (13 Sep mapping)"]]),
            "cluster": clean(source[ix["Cluster (13 Sep mapping)"]]),
            "panchayat": clean(source[ix["Panchayat"]]),
            "fy": clean(source[ix["Work Start Fin Yr"]]),
            "status": "Ongoing",
            "code": code,
            "name": clean(source[ix["Work Name"]]),
            "type": clean(source[ix["Work Type"]]),
            "finalCategory": normalized_category(source[ix["Final Category"]], old),
            "sanction": sanction,
            "bookedWage": vbg_wage,
            "bookedMaterial": vbg_material,
            "booked": vbg_wage + vbg_material,
            "expPct": ((vbg_wage + vbg_material) * 100 / sanction) if sanction else 0,
            "mandays": num(source[ix["Total Mandays (portal)"]]),
            "mandaysTillMar31": max(0, previous_mandays - num(old.get("nregaAprJunMandays"))),
            "currentFYMandays": current_mandays,
            "nregaAprJunMandays": num(old.get("nregaAprJunMandays")),
            "julyMandays": current_mandays,
            "recoveryDone": old.get("recoveryDone", False),
            "recoveryWork": num(old.get("recoveryWork")),
            "recoveryAmount": num(old.get("recoveryAmount")),
            "recoveryWorkCount": num(old.get("recoveryWorkCount")),
            "nregaBookedWage": nrega_wage,
            "nregaBookedMaterial": nrega_material,
            "nregaBooked": nrega_wage + nrega_material,
            "vbgBookedWage": vbg_wage,
            "vbgBookedMaterial": vbg_material,
            "vbgBooked": vbg_wage + vbg_material,
            "overallBookedWage": overall_wage,
            "overallBookedMaterial": overall_material,
            "overallBooked": overall,
            "nregaExpPct": (nrega_wage + nrega_material) * 100 / sanction if sanction else 0,
            "vbgExpPct": (vbg_wage + vbg_material) * 100 / sanction if sanction else 0,
            "overallExpPct": overall * 100 / sanction if sanction else 0,
        })

    if len(rows) != 15618 or len(codes) != 15618:
        raise SystemExit(f"Expected 15,618 unique Ongoing works; got rows={len(rows)}, unique={len(codes)}")
    counts = Counter(row["finalCategory"] for row in rows)
    if counts["PMAY-G"] != 10742 or counts["Ek Bagiya"] != 755:
        raise SystemExit(f"Category validation failed: PMAY-G={counts['PMAY-G']}, Ek Bagiya={counts['Ek Bagiya']}")
    OUT.write_text("window.ONGOING_DETAILS=" + json.dumps(rows, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Imported {len(rows):,} Ongoing works; PMAY-G={counts['PMAY-G']:,}; Ek Bagiya={counts['Ek Bagiya']:,}; categories={len(counts)}")


if __name__ == "__main__":
    main()
