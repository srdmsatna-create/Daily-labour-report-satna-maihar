#!/usr/bin/env python3
"""Merge date-bounded SECURE /YD/ TS counts into the AS/Before report."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_JSON = ROOT / "data" / "secure-ts-yuktadhara-fy2026-27.json"
AS_JS = ROOT / "as-geotag-before-data.js"


def norm(value):
    return re.sub(r"[^A-Z0-9]+", " ", str(value or "").upper()).strip()


def main():
    secure = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    if secure.get("startDate") != "2026-10-01" or secure.get("workCodePattern") != "/YD/":
        raise RuntimeError("SECURE snapshot must be FY 2026-27, from 01-10-2026, and /YD/ only")
    source = AS_JS.read_text(encoding="utf-8")
    match = re.fullmatch(r"\\s*window\\.AS_GEOTAG_BEFORE\\s*=\\s*(\\{.*\\})\\s*;?\\s*", source, re.S)
    if not match:
        raise RuntimeError("Unexpected AS_GEOTAG_BEFORE data file format")
    report = json.loads(match.group(1))

    blocks = {str(x["blockCode"]): x for x in secure["blocks"]}
    block_codes_by_name = {norm(x["janpad"]): str(x["blockCode"]) for x in secure["blocks"]}
    # The source portal has sometimes labelled block 1712002 as SATNA; SECURE's current
    # Janpad master identifies that same code as SOHAWAL.
    block_codes_by_name["SATNA"] = "1712002"
    block_counts = {code: int(item["ydTsCount"]) for code, item in blocks.items()}

    for row in report.get("janpadSummary", []):
        code = str(row.get("blockCode") or block_codes_by_name.get(norm(row.get("block")), ""))
        if code not in blocks:
            raise RuntimeError(f"SECURE source missing Janpad mapping for {row.get('block')}")
        row["blockCode"] = code
        row["block"] = str(blocks[code]["janpad"]).upper()
        row["district"] = str(blocks[code]["district"]).upper()
        row["tsCount"] = block_counts[code]

    merged = {str(x.get("panchayatCode") or norm(x.get("district")) + "|" + norm(x.get("block")) + "|" + norm(x.get("panchayat"))): x
              for x in report.get("gpSummary", [])}
    for row in merged.values():
        row["tsCount"] = 0

    for gp in secure.get("panchayats", []):
        pcode = str(gp["panchayatCode"])
        item = merged.get(pcode)
        if item is None:
            item = {"asAvailable": 0, "beforeAvailable": 0, "beforeNotAvailable": 0, "unknown": 0}
            merged[pcode] = item
        item.update({
            "district": str(gp["district"]).upper(),
            "block": str(gp["block"]).upper(),
            "panchayat": gp["panchayat"],
            "blockCode": str(gp["blockCode"]),
            "panchayatCode": pcode,
            "tsCount": int(gp.get("ydTsCount", 0)),
        })

    # Normalize legacy GP labels by their official block code.
    for item in merged.values():
        pcode = str(item.get("panchayatCode") or "")
        code = pcode[:7]
        if code in blocks:
            item["blockCode"] = code
            item["block"] = str(blocks[code]["janpad"]).upper()
            item["district"] = str(blocks[code]["district"]).upper()

    report["gpSummary"] = sorted(
        [x for x in merged.values() if any(int(x.get(k, 0) or 0) for k in
         ("tsCount", "asAvailable", "beforeAvailable", "beforeNotAvailable", "unknown"))],
        key=lambda x: (norm(x.get("district")), norm(x.get("block")), norm(x.get("panchayat")))
    )
    report["secureTs"] = {
        "fy": secure["fy"], "dateFrom": secure["startDate"], "dateTo": secure["endDate"],
        "snapshotAt": secure["snapshotAt"], "source": secure["source"],
        "basis": secure["basis"], "workCodePattern": "/YD/",
        "totalYdTs": secure["totals"]["ydTsCount"], "warnings": secure.get("warnings", []),
    }
    report["source"] = (
        "AS / Before: AS sanction date >= 01-10-2026; Work Code ID contains /YD/. "
        "SECURE TS: approved TS date 01-10-2026 through snapshot date; Work Code ID contains /YD/; "
        "FY 2026-2027. Janpad names follow the SECURE master."
    )

    for code, expected in block_counts.items():
        actual = sum(int(x.get("tsCount", 0)) for x in report["gpSummary"]
                     if str(x.get("blockCode", "")) == code)
        if actual != expected:
            raise RuntimeError(f"GP /YD/ TS sum for {blocks[code]['janpad']} is {actual}; expected {expected}")

    mismatches = [(x.get("block", ""), int(x.get("asAvailable", 0)), int(x.get("tsCount", 0)))
                  for x in report.get("janpadSummary", [])
                  if int(x.get("asAvailable", 0)) > int(x.get("tsCount", 0))]
    if mismatches:
        detail = ", ".join(f"{b}: AS={a}, SECURE /YD/ TS={t}" for b, a, t in mismatches)
        raise RuntimeError("Refusing inconsistent AS/TS totals: " + detail)

    AS_JS.write_text("window.AS_GEOTAG_BEFORE=" + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\\n",
                     encoding="utf-8")
    print(f"Merged SECURE /YD/ TS totals: {secure['totals']['ydTsCount']} across {len(report['gpSummary'])} GP rows")


if __name__ == "__main__":
    main()
