#!/usr/bin/env python3
"""Append one date-stamped R33.1, muster and attached-worker snapshot."""
from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
TZ = ZoneInfo("Asia/Kolkata")
HISTORY = ROOT / "data" / "yuktdhara-mr-labour-history.json"
SATNA = {"MAJHGAWAN", "NAGOD", "RAMPUR BAGHELAN", "SATNA", "UNCHAHARA"}


def load_js_object(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"No JSON object found in {path}")
    return json.loads(text[start : end + 1])


def main() -> None:
    yuk = load_js_object(ROOT / "yuktdhara-official-data.js")
    muster = load_js_object(ROOT / "muster-emb-data.js")
    workers = load_js_object(ROOT / "shramik-gp-progress-data.js")
    if not yuk.get("rows") or not muster.get("rows") or not workers.get("blocks"):
        raise ValueError("One or more source snapshots are empty; history was not changed.")

    muster_by_block = {str(r["block"]).upper(): r for r in muster["rows"]}
    workers_by_block = {str(r["janpad"]).upper(): r for r in workers["blocks"]}
    rows = []
    for item in yuk["rows"]:
        block = str(item["block"]).upper()
        mr = muster_by_block.get(block, {})
        labour = workers_by_block.get(block, {})
        rows.append({
            "district": "SATNA" if block in SATNA else "MAIHAR",
            "janpad": block,
            "newWorksCreated": int(item.get("worksCreated", 0) or 0),
            "worksYetToStart": int(item.get("yetToStart", 0) or 0),
            "worksOngoing": int(item.get("ongoing", 0) or 0),
            "worksCompleted": int(item.get("completed", 0) or 0),
            "musterIssuedTotal": int(mr.get("issued", 0) or 0),
            "workersAttachedTotal": int(labour.get("labour", 0) or 0),
        })
    rows.sort(key=lambda r: (r["district"], r["janpad"]))

    HISTORY.parent.mkdir(parents=True, exist_ok=True)
    history = json.loads(HISTORY.read_text(encoding="utf-8")) if HISTORY.exists() else {
        "title": "R-33.1 नवीन कार्यों का तारीखवार MR/श्रमिक snapshot",
        "scopeNote": (
            "R-33.1 नए कार्य की स्थिति जनपद/उपयंत्री स्तर पर देता है। "
            "मस्टर रोल और संलग्न श्रमिक के उपलब्ध आँकड़े जनपद-स्तर के कुल हैं; "
            "वे केवल नवीन R-33.1 कार्यों के work-code स्तर पर अलग नहीं हैं। "
            "दैनिक बदलाव पिछले दर्ज snapshot से निकाले जाते हैं।"
        ),
        "snapshots": [],
    }

    now = datetime.now(TZ)
    date_key = now.date().isoformat()
    previous = sorted(
        (s for s in history["snapshots"] if s.get("snapshotDate") != date_key),
        key=lambda s: s["snapshotDate"],
    )[-1:] 
    previous_snapshot = previous[0] if previous else None
    old_rows = {r["janpad"]: r for r in (previous_snapshot or {}).get("rows", [])}

    for row in rows:
        old = old_rows.get(row["janpad"])
        row["musterIssuedChange"] = (
            row["musterIssuedTotal"] - old["musterIssuedTotal"] if old else None
        )
        row["workersAttachedChange"] = (
            row["workersAttachedTotal"] - old["workersAttachedTotal"] if old else None
        )

    snapshot = {
        "snapshotDate": date_key,
        "capturedAt": now.isoformat(timespec="seconds"),
        "yuktdharaDataDate": yuk.get("officialDate"),
        "yuktdharaUpdatedAt": yuk.get("updatedAt"),
        "musterDataDate": muster.get("officialDate"),
        "musterUpdatedAt": muster.get("updatedAt"),
        "workersDataDate": workers.get("date"),
        "workersSourceLastUpdated": workers.get("sourceLastUpdated"),
        "previousSnapshotDate": previous_snapshot.get("snapshotDate") if previous_snapshot else None,
        "rows": rows,
    }
    snapshots = [s for s in history["snapshots"] if s.get("snapshotDate") != date_key]
    snapshots.append(snapshot)
    snapshots.sort(key=lambda s: s["snapshotDate"])
    history["snapshots"] = snapshots
    HISTORY.write_text(json.dumps(history, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Recorded {date_key}: {len(rows)} Janpads; sources {yuk.get('officialDate')}, "
          f"{muster.get('officialDate')}, {workers.get('date')}")


if __name__ == "__main__":
    main()
