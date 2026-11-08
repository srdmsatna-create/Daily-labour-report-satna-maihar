#!/usr/bin/env python3
"""Rebuild AS/Before + SECURE /YD/ + R33.1 Janpad totals from source snapshots."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AS_JSON = ROOT / "data" / "as-geotag-before-latest.json"
SECURE_JSON = ROOT / "data" / "secure-ts-yuktadhara-fy2026-27.json"
YUKTDHARA_JS = ROOT / "yuktdhara-official-data.js"
AS_JS = ROOT / "as-geotag-before-data.js"


def read_js(path):
    text = path.read_text(encoding="utf-8-sig")
    if "=" not in text:
        raise ValueError("Unexpected JS data format: " + str(path))
    return json.loads(text.split("=", 1)[1].strip().rstrip(";"))


def norm(value):
    return re.sub(r"[^A-Z0-9]+", " ", str(value or "").upper()).strip()


def main():
    source = json.loads(AS_JSON.read_text(encoding="utf-8"))
    secure = json.loads(SECURE_JSON.read_text(encoding="utf-8"))
    yuk = read_js(YUKTDHARA_JS)

    if source.get("financialYear") != "2026-2027" or source.get("dateFrom") != "2026-10-01" or source.get("workCodePattern") != "/YD/":
        raise ValueError("AS source must cover FY 2026-27, from 01-10-2026, /YD/ only")
    if secure.get("fy") != "2026-2027" or secure.get("startDate") != "2026-10-01" or secure.get("workCodePattern") != "/YD/":
        raise ValueError("SECURE source must cover FY 2026-27, from 01-10-2026, /YD/ only")
    if yuk.get("financialYear") != "2026-2027" or len(yuk.get("rows", [])) != 8:
        raise ValueError("R33.1 source must contain all eight FY 2026-27 Janpads")
    if len(secure.get("blocks", [])) != 8 or secure.get("totals", {}).get("ydTsCount") != sum(int(b.get("ydTsCount", 0)) for b in secure.get("blocks", [])):
        raise ValueError("SECURE /YD/ Janpad counts are incomplete")

    blocks = {str(b["blockCode"]): {
        "blockCode": str(b["blockCode"]),
        "block": str(b["janpad"]).upper(),
        "district": str(b["district"]).upper(),
        "tsCount": int(b.get("ydTsCount", 0)),
    } for b in secure["blocks"]}
    by_name = {norm(b["block"]): code for code, b in blocks.items()}
    # VBGRAMG sometimes labels block 1712002 as SATNA; SECURE master names it SOHAWAL.
    by_name["SATNA"] = "1712002"

    created = {}
    for row in yuk["rows"]:
        code = by_name.get(norm(row.get("block")))
        if code is None:
            raise ValueError("R33.1 Janpad missing from SECURE master: " + str(row.get("block")))
        created[code] = int(row.get("worksCreated", 0))

    janpad = {}
    for code, block in blocks.items():
        janpad[code] = dict(block, ydWorksCreated=created.get(code, 0),
            asAvailable=0, beforeAvailable=0, beforeNotAvailable=0, unknown=0)

    gps = {}
    rows = source.get("rows", [])
    for row in rows:
        work_code = str(row.get("workCode", ""))
        if (row.get("financialYear") != "2026-2027" or "/YD/" not in work_code.upper()
                or str(row.get("asSanctionDate", "")) < "2026-10-01"):
            raise ValueError("AS row outside date/FY/Work Code scope: " + work_code)
        pcode = work_code.split("/", 1)[0]
        block_code = next((code for code in blocks if work_code.startswith(code)), None)
        if not block_code or not pcode.startswith(block_code):
            raise ValueError("AS Work Code does not map to SECURE Janpad: " + work_code)
        block = janpad[block_code]
        block["asAvailable"] += 1
        status = row.get("beforePhotoStatus")
        status_key = {"Available": "beforeAvailable", "Not Available": "beforeNotAvailable"}.get(status, "unknown")
        block[status_key] += 1
        item = gps.setdefault(pcode, {
            "district": block["district"], "block": block["block"], "blockCode": block_code,
            "panchayat": row.get("panchayat", ""), "panchayatCode": pcode,
            "asAvailable": 0, "beforeAvailable": 0, "beforeNotAvailable": 0, "unknown": 0, "tsCount": 0,
        })
        item["asAvailable"] += 1
        item[status_key] += 1

    for row in secure.get("panchayats", []):
        code, pcode = str(row["blockCode"]), str(row["panchayatCode"])
        if code not in blocks or not pcode.startswith(code):
            raise ValueError("SECURE GP does not map to its Janpad: " + pcode)
        item = gps.setdefault(pcode, {
            "asAvailable": 0, "beforeAvailable": 0, "beforeNotAvailable": 0, "unknown": 0,
        })
        item.update({
            "district": str(row["district"]).upper(), "block": str(row["block"]).upper(),
            "blockCode": code, "panchayat": row["panchayat"], "panchayatCode": pcode,
            "tsCount": int(row.get("ydTsCount", 0)),
        })

    gp_rows = sorted(
        [row for row in gps.values() if int(row.get("tsCount", 0)) or int(row.get("asAvailable", 0))],
        key=lambda row: (row["blockCode"], norm(row.get("panchayat")))
    )
    for code, block in blocks.items():
        members = [row for row in gp_rows if row.get("blockCode") == code]
        if sum(int(row.get("tsCount", 0)) for row in members) != block["tsCount"]:
            raise ValueError("GP /YD/ TS rows do not reconcile for " + block["block"])
        if sum(int(row.get("asAvailable", 0)) for row in members) != janpad[code]["asAvailable"]:
            raise ValueError("GP AS rows do not reconcile for " + block["block"])

    report = dict(source)
    report.update({
        "asAvailableCount": len(rows),
        "beforePhotoAvailable": sum(row.get("beforePhotoStatus") == "Available" for row in rows),
        "beforePhotoNotAvailable": sum(row.get("beforePhotoStatus") == "Not Available" for row in rows),
        "beforePhotoUnknown": sum(row.get("beforePhotoStatus") == "Unknown" for row in rows),
        "janpadSummary": list(janpad.values()),
        "gpSummary": gp_rows,
        "secureTs": {
            "fy": secure["fy"], "dateFrom": secure["startDate"], "dateTo": secure["endDate"],
            "snapshotAt": secure["snapshotAt"], "source": secure["source"], "basis": secure["basis"],
            "workCodePattern": "/YD/", "totalYdTs": secure["totals"]["ydTsCount"],
            "warnings": secure.get("warnings", []),
        },
        "yuktdhara": {
            "financialYear": yuk["financialYear"], "officialDate": yuk.get("officialDate", ""),
            "updatedAt": yuk.get("updatedAt", ""), "source": yuk.get("source", ""),
            "totalWorksCreated": sum(int(row.get("worksCreated", 0)) for row in yuk["rows"]),
        },
        "source": (
            "AS / Before: FY 2026-2027; AS sanction date from 01-10-2026; Work Code /YD/. "
            "SECURE TS: approved TS date from 01-10-2026 to snapshot; Work Code /YD/. "
            "Yuktdhara created Work Code count: official VBGRAMG R33.1."
        ),
    })
    if report["asAvailableCount"] != int(source.get("asAvailableCount", len(rows))):
        raise ValueError("AS detail row count does not match the source total")
    if sum(row["ydWorksCreated"] for row in report["janpadSummary"]) != report["yuktdhara"]["totalWorksCreated"]:
        raise ValueError("R33.1 created-work count does not reconcile")

    AS_JS.write_text(
        "window.AS_GEOTAG_BEFORE=" + json.dumps(report, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8"
    )
    print("Rebuilt report from AS rows, SECURE /YD/ rows and R33.1: "
          + str(report["asAvailableCount"]) + " AS, "
          + str(report["secureTs"]["totalYdTs"]) + " TS, "
          + str(report["yuktdhara"]["totalWorksCreated"]) + " created Work Codes.")


if __name__ == "__main__":
    main()
