#!/usr/bin/env python3
"""Merge independent SECURE FY /YD/ counts into the AS/Before report data."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA_JSON = ROOT / "data" / "secure-ts-yuktadhara-fy2026-27.json"
AS_JS = ROOT / "as-geotag-before-data.js"


def key(district, block, panchayat):
    return (str(district or "").strip().upper(), str(block or "").strip().upper(), str(panchayat or "").strip().upper())


def main():
    secure = json.loads(DATA_JSON.read_text(encoding="utf-8"))
    source = AS_JS.read_text(encoding="utf-8")
    match = re.fullmatch(r"\s*window\.AS_GEOTAG_BEFORE\s*=\s*(\{.*\})\s*;?\s*", source, re.S)
    if not match:
        raise RuntimeError("Unexpected AS_GEOTAG_BEFORE data file format")
    report = json.loads(match.group(1))

    block_counts = {str(x["janpad"]).strip().upper(): int(x["ydTsCount"]) for x in secure["blocks"]}
    for row in report.get("janpadSummary", []):
        block = str(row.get("block", "")).strip().upper()
        if block not in block_counts:
            raise RuntimeError(f"SECURE source missing Janpad {block}")
        row["tsCount"] = block_counts[block]

    merged = {key(x.get("district"), x.get("block"), x.get("panchayat")): x for x in report.get("gpSummary", [])}
    for gp in secure.get("panchayats", []):
        k = key(gp.get("district"), gp.get("block"), gp.get("panchayat"))
        item = merged.get(k)
        yd_count = int(gp.get("ydTsCount", 0))
        if item is None and yd_count == 0:
            continue
        if item is None:
            item = {
                "district": gp["district"], "block": gp["block"], "panchayat": gp["panchayat"],
                "asAvailable": 0, "beforeAvailable": 0, "beforeNotAvailable": 0, "unknown": 0,
            }
            merged[k] = item
        item["tsCount"] = yd_count
        item["blockCode"] = gp["blockCode"]
        item["panchayatCode"] = gp["panchayatCode"]
        item["secureCurrentTsAllCodes"] = int(gp.get("secureCurrentTsAllCodes", 0))

    report["gpSummary"] = sorted(merged.values(), key=lambda x: key(x.get("district"), x.get("block"), x.get("panchayat")))
    report["secureTs"] = {
        "fy": secure["fy"], "snapshotAt": secure["snapshotAt"], "source": secure["source"],
        "basis": secure["basis"], "totalYdTs": secure["totals"]["ydTsCount"],
        "warnings": secure.get("warnings", []),
    }
    report["source"] = (
        "AS: R22.1 / Administrative-Financial Sanction Date from 01-10-2026; "
        "Before: R36.1 stages-before status; SECURE TS: full FY 2026-2027 "
        "approved work rows whose Work Code contains /YD/, independently counted by GP."
    )

    # The independent GP rows must add back to every Janpad and district total.
    for block, expected in block_counts.items():
        actual = sum(int(x.get("tsCount", 0)) for x in report["gpSummary"] if str(x.get("block", "")).strip().upper() == block)
        if actual != expected:
            raise RuntimeError(f"GP /YD/ TS sum for {block} is {actual}; SECURE block sum is {expected}")

    AS_JS.write_text("window.AS_GEOTAG_BEFORE=" + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Merged SECURE /YD/ TS totals: {secure['totals']['ydTsCount']} across {len(report['gpSummary'])} AS/TS GPs")
    for row in report.get("janpadSummary", []):
        if int(row.get("asAvailable", 0)) > int(row.get("tsCount", 0)):
            print(f"SOURCE MISMATCH {row['block']}: AS {row['asAvailable']} > SECURE /YD/ TS {row['tsCount']}")


if __name__ == "__main__":
    main()
