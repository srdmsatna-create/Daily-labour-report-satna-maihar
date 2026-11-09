#!/usr/bin/env python3
"""Append a date-stamped R33.1 /YD ongoing-work and issued-MR work-code match."""
from __future__ import annotations
import json, re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Kolkata")
HISTORY = ROOT / "data" / "yuktdhara-mr-labour-history.json"
SATNA = {"MAJHGAWAN", "NAGOD", "RAMPUR BAGHELAN", "SATNA", "UNCHAHARA"}

def load_js(path: Path):
    text = path.read_text(encoding="utf-8")
    match = re.search(r"=\\s*(\\{.*\\}|\\[.*\\])\\s*;?\\s*$", text, re.S)
    if not match:
        raise ValueError(f"No JSON payload found in {path}")
    return json.loads(match.group(1))

def norm(value):
    return re.sub(r"\\s+", " ", str(value or "")).strip().upper()

def main():
    yuk = load_js(ROOT / "yuktdhara-official-data.js")
    ongoing = load_js(ROOT / "ongoing-details.js")
    emuster = load_js(ROOT / "gp-emuster-data.js")
    workers = load_js(ROOT / "shramik-gp-progress-data.js")
    if not yuk.get("rows") or not ongoing or not emuster.get("works") or not workers.get("rows"):
        raise ValueError("One or more current source snapshots are empty; history was not changed.")

    issued_codes = {norm(w.get("code")) for w in emuster["works"] if w.get("code")}
    labour_by_gp = {(norm(r.get("janpad")), norm(r.get("panchayat"))): int(r.get("labour", 0) or 0)
                    for r in workers["rows"]}
    r331_by_janpad = {norm(r.get("block")): int(r.get("ongoing", 0) or 0) for r in yuk["rows"]}

    ongoing_yukt = []
    for w in ongoing:
        code = norm(w.get("code"))
        if "/YD/" not in code or norm(w.get("status")) != "ONGOING":
            continue
        janpad = norm(w.get("janpad"))
        panchayat = norm(w.get("panchayat"))
        ongoing_yukt.append({
            "district": "SATNA" if janpad in SATNA else "MAIHAR",
            "janpad": janpad,
            "panchayat": panchayat,
            "code": str(w.get("code") or "").strip(),
            "name": str(w.get("name") or "").strip(),
            "mrIssued": code in issued_codes,
        })

    matched = [w for w in ongoing_yukt if w["mrIssued"]]
    matched_gps = {(w["janpad"], w["panchayat"]) for w in matched if w["janpad"] and w["panchayat"]}
    workers_on_matched_gps = sum(labour_by_gp.get(gp, 0) for gp in matched_gps)

    grouped = {}
    for w in ongoing_yukt:
        grouped.setdefault(w["janpad"], []).append(w)
    rows = []
    for janpad in sorted(set(r331_by_janpad) | set(grouped)):
        block_ongoing = grouped.get(janpad, [])
        matched_rows = [w for w in block_ongoing if w["mrIssued"]]
        old_codes = set()
        rows.append({
            "district": "SATNA" if janpad in SATNA else "MAIHAR",
            "janpad": janpad,
            "r331OngoingWorks": r331_by_janpad.get(janpad, 0),
            "r612YuktdharaOngoingWorks": len(block_ongoing),
            "ongoingWorksWithIssuedMR": len(matched_rows),
            "matchedPanchayats": len({w["panchayat"] for w in matched_rows}),
            "workersOnMatchedPanchayats": sum(labour_by_gp.get((janpad, p), 0) for p in {w["panchayat"] for w in matched_rows}),
            "matchedWorks": [{"code": w["code"], "panchayat": w["panchayat"], "name": w["name"]} for w in matched_rows],
        })
    rows.sort(key=lambda r: (r["district"], r["janpad"]))

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    history = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else {
        "title": "R-33.1 प्रगतिरत Yuktdhara कार्यों का तारीखवार MR/श्रमिक रिकॉर्ड",
        "scopeNote": "",
        "snapshots": [],
    }
    now = datetime.now(TZ)
    date_key = now.date().isoformat()
    previous = sorted((s for s in history["snapshots"] if s.get("snapshotDate") != date_key),
                      key=lambda s: s["snapshotDate"])[-1:]
    previous_snapshot = previous[0] if previous else None
    old_rows = {r["janpad"]: r for r in (previous_snapshot or {}).get("rows", [])}
    for row in rows:
        old = old_rows.get(row["janpad"])
        old_codes = {w.get("code") for w in old.get("matchedWorks", [])} if old else set()
        current_codes = {w.get("code") for w in row["matchedWorks"]}
        row["newMrMatchedWorksSincePrevious"] = len(current_codes - old_codes) if old and "matchedWorks" in old else None
        row["matchedMrWorkChange"] = row["ongoingWorksWithIssuedMR"] - int(old.get("ongoingWorksWithIssuedMR", 0)) if old and "ongoingWorksWithIssuedMR" in old else None

    snapshot = {
        "snapshotDate": date_key,
        "capturedAt": now.isoformat(timespec="seconds"),
        "yuktdharaDataDate": yuk.get("officialDate"),
        "yuktdharaUpdatedAt": yuk.get("updatedAt"),
        "mis612UpdatedAt": None,
        "emusterDataDate": emuster.get("date"),
        "emusterFetchedAt": emuster.get("fetchedAt"),
        "workersDataDate": workers.get("date"),
        "workersSourceLastUpdated": workers.get("sourceLastUpdated"),
        "previousSnapshotDate": previous_snapshot.get("snapshotDate") if previous_snapshot else None,
        "totalR331OngoingWorks": sum(r["r331OngoingWorks"] for r in rows),
        "totalR612YuktdharaOngoingWorks": sum(r["r612YuktdharaOngoingWorks"] for r in rows),
        "totalOngoingWorksWithIssuedMR": sum(r["ongoingWorksWithIssuedMR"] for r in rows),
        "matchedPanchayats": len(matched_gps),
        "workersOnMatchedPanchayats": workers_on_matched_gps,
        "rows": rows,
    }
    status_path = ROOT / "data" / "mis-6.12-status.json"
    if status_path.exists():
        try:
            snapshot["mis612UpdatedAt"] = json.loads(status_path.read_text(encoding="utf-8")).get("updatedAt")
        except (ValueError, OSError):
            pass
    snapshots = [s for s in history["snapshots"] if s.get("snapshotDate") != date_key]
    snapshots.append(snapshot)
    snapshots.sort(key=lambda s: s["snapshotDate"])
    history["title"] = "R-33.1 प्रगतिरत Yuktdhara कार्यों का तारीखवार MR/श्रमिक रिकॉर्ड"
    history["scopeNote"] = (
        "R-33.1 जनपदवार प्रगतिरत संख्या देता है। कामों का work-code मिलान R-6.12 में ongoing "
        "/YD/ codes और GP e-Muster में MR-जारी work-code सूची के intersection से है। "
        "संलग्न श्रमिक केवल उन matched कामों वाली पंचायतों का GP कुल है; स्रोत में काम-विशिष्ट "
        "श्रमिक संख्या उपलब्ध नहीं है। यह गिनती MR-जारी कामों की है, अलग-अलग MR पर्चियों की नहीं।"
    )
    history["snapshots"] = snapshots
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(f"Recorded {date_key}: R33.1 ongoing {snapshot['totalR331OngoingWorks']}; "
          f"R6.12 /YD/ ongoing {snapshot['totalR612YuktdharaOngoingWorks']}; "
          f"with issued MR {snapshot['totalOngoingWorksWithIssuedMR']}")

if __name__ == "__main__":
    main()
