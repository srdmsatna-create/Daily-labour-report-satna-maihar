"""Refresh the Satna/Maihar R-10.1 e-KYC and VB-GRAM G liability snapshot."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
import json
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from update_pending_wage_payment import BLOCKS, amount, fetch, table

ROOT = Path(__file__).resolve().parents[1]
EKYC_SOURCE = "https://vbgramgrep.dord.gov.in/VBGRAMG/AdhaarStatus.aspx?page=D&short_name=&state_name=MADHYA+PRADESH&state_code=17&district_name=SATNA&district_code=1712&fin_year=2026-2027&source=national&Digest=xJ6WAz2l1aMieSCmXXx%2fsQ"
MATERIAL_SOURCE = "https://vbgramgrep.dord.gov.in/VBGRAMG/state_html/executive_agency_report_new.aspx?payload=dOLei81_Q1_tjQsOFP2ejyCqE1cc-AIh-1fl4-BQbHdK0UpcBE8mCTi-wimyVibBi_OLK251H51DjQmOg9EZY8ycJz9rXKJSY6OtF0y2GuWFzQKYGTtcwrzbME3jMxfpw7G-wdocdJbHHj0pT75B1sRr3g_V03nEfE5FDGrFqStlAkEM2BfKCJKSa3s_afuhXWp6oYDMrdQGaEvyx9qdSHMSR0uYn2r9HTKmIKweCDA"


def parse(source, kind):
    if "2026-2027" not in source or "SATNA" not in source:
        raise ValueError(f"Unexpected district or financial year: {kind}")
    rows = [[cell["text"] for cell in row] for row in table(source)]
    if kind == "ekyc":
        expected_header = ["Aadhaar Seeded", "e-KYC Done", "% of e-KYC"]
        if not any(row[3:6] == expected_header for row in rows):
            raise ValueError("Official e-KYC columns not found")
        columns = (3, 4)
    else:
        if not any(row[2:4] == ["Labour Expenditure", "Material Expenditure"] for row in rows) or not any(
            row[:6] == ["Paid", "Unpaid", "Total", "Paid", "Unpaid", "Total"] for row in rows
        ) or "Amount in Lakhs" not in source:
            raise ValueError("Official material unpaid column or unit not found")
        columns = (3, 6)

    values = {}
    for row in rows:
        if len(row) <= max(columns):
            continue
        name = row[1].upper()
        if name not in BLOCKS and name != "TOTAL":
            continue
        if name in values:
            raise ValueError(f"Duplicate {kind} row: {name}")
        values[name] = tuple(amount(row[index]) for index in columns)
        if kind == "ekyc":
            seeded, done = values[name]
            if seeded != seeded.to_integral_value() or done != done.to_integral_value() or done > seeded:
                raise ValueError(f"Invalid e-KYC counts: {name}")
            if seeded and (done * 100 / seeded).quantize(Decimal(".01"), rounding=ROUND_HALF_UP) != amount(row[5]):
                raise ValueError(f"Official e-KYC percentage mismatch: {name}")

    total = values.pop("TOTAL", None)
    if set(values) != BLOCKS or total is None:
        raise ValueError(f"Expected eight official Janpads and a total: {kind}")
    sums = tuple(sum(row[i] for row in values.values()) for i in range(len(columns)))
    if sums != total:
        raise ValueError(f"Official {kind} sum mismatch: {sums} versus {total}")
    return values


LEGACY_YEARS = tuple(f"{year}-{year + 1}" for year in range(2021, 2027))
LEGACY_BASE = "https://mnregaweb4.dord.gov.in/netnrega/writereaddata/citizen_out/"


def legacy_url(financial_year):
    start, end = financial_year.split("-")
    return f"{LEGACY_BASE}funddisreport_1712_eng_{start[-2:]}{end[-2:]}_.html"


def parse_legacy(source, financial_year):
    if f"Financial Year {financial_year}" not in source or "District:SATNA" not in source:
        raise ValueError(f"Unexpected MGNREGA district or year: {financial_year}")
    rows = [[cell["text"] for cell in row] for row in table(source)]
    pending_headers = ["On Unskilled Wage", "On Semi-skilled and Skilled Wage", "On Material", "Tax", "Total"]
    if not any("Payment due*" in row for row in rows) or not any(row[-5:] == pending_headers for row in rows):
        raise ValueError(f"Missing MGNREGA payment due columns: {financial_year}")

    data = {}
    for row in rows:
        if len(row) != 23:
            continue
        block = row[1].upper()
        if block not in BLOCKS and block != "TOTAL":
            continue
        if block in data:
            raise ValueError(f"Duplicate MGNREGA block: {block}, {financial_year}")
        data[block] = tuple(amount(row[index]) for index in (18, 19, 20))
    total = data.pop("TOTAL", None)
    if set(data) != BLOCKS or total is None:
        raise ValueError(f"Incomplete MGNREGA block coverage: {financial_year}")
    for i, report_total in enumerate(total):
        if abs(sum(row[i] for row in data.values()) - report_total) > Decimal(".05"):
            raise ValueError(f"MGNREGA payment due total mismatch: {financial_year}")
    return {
        block: (int(wage * 100_000), int((skilled + material) * 100_000))
        for block, (wage, skilled, material) in data.items()
    }


def fetch_legacy(financial_year, download_dir):
    if download_dir:
        start, end = financial_year.split("-")
        path = download_dir / f"srdm-fund-{start[-2:]}{end[-2:]}_.html"
        if not path.exists():
            return None
        source = path.read_text(encoding="utf-8-sig")
    else:
        request = Request(legacy_url(financial_year), headers={"User-Agent": "Mozilla/5.0"})
        try:
            with urlopen(request, timeout=35) as response:
                source = response.read().decode("utf-8-sig")
        except HTTPError as error:
            if error.code == 404:
                return None
            raise
    return parse_legacy(source, financial_year)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ekyc-html", type=Path)
    parser.add_argument("--material-html", type=Path)
    parser.add_argument("--legacy-html-dir", type=Path)
    args = parser.parse_args()

    def read(file, url, kind):
        return parse(file.read_text(encoding="utf-8-sig") if file else fetch(url), kind)

    with ThreadPoolExecutor(max_workers=6) as pool:
        ekyc = pool.submit(read, args.ekyc_html, EKYC_SOURCE, "ekyc")
        material = pool.submit(read, args.material_html, MATERIAL_SOURCE, "material")
        legacy_futures = {year: pool.submit(fetch_legacy, year, args.legacy_html_dir) for year in LEGACY_YEARS}
        ekyc, material = ekyc.result(), material.result()
        legacy = {year: future.result() for year, future in legacy_futures.items()}
    target = ROOT / "data/statistics-ekyc-material-latest.json"
    previous = json.loads(target.read_text(encoding="utf-8")) if target.exists() else {}
    previous_years = set(previous.get("mgnrega", {}).get("years", []))
    available_years = [year for year, data in legacy.items() if data is not None]
    required_years = previous_years | {"2024-2025", "2025-2026", "2026-2027"}
    if not required_years.issubset(available_years):
        raise ValueError("Previously verified MGNREGA financial reports missing")

    rows = []
    for block in sorted(BLOCKS):
        seeded, done = ekyc[block]
        wage_lakh, material_lakh = material[block]
        rows.append({
            "block": block,
            "aadhaarSeeded": int(seeded),
            "eKycDone": int(done),
            "pendingWageAmount": int(wage_lakh * 100_000),
            "pendingMaterialAmount": int(material_lakh * 100_000),
            "mgnregaWageAmount": sum(legacy[year][block][0] for year in available_years),
            "mgnregaMaterialAmount": sum(legacy[year][block][1] for year in available_years),
        })
    payload = {
        "financialYear": "2026-2027",
        "fetchedAt": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        "sources": {"eKyc": EKYC_SOURCE, "material": MATERIAL_SOURCE},
        "rows": rows,
        "mgnrega": {
            "years": available_years,
            "missingYears": [year for year in LEGACY_YEARS if year not in available_years],
            "sources": {year: legacy_url(year) for year in available_years},
            "basis": "Financial Statement payment due: wage column 19; material columns 20 + 21",
        },
    }
    temporary = target.with_suffix(".tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(target)
    print("Verified eight Janpads against official e-KYC and material totals.")


if __name__ == "__main__":
    main()
