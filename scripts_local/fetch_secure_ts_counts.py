#!/usr/bin/env python3
"""Fetch FY 2026-27 SECURE TS work rows and count only /YD/ work codes."""
from __future__ import annotations

import json
import re
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = "https://secure.dord.gov.in/reportv2/"
PAGE = BASE + "tsregister?mvsl=69"
STATE_CODE = "17"
DISTRICT_CODE = "1712"
FY = "2026-2027"
YD_RE = re.compile(r"(?:^|/)YD(?:/|$)", re.I)
EXPECTED_GP_COUNTS = {
    "AMARPATAN": 75, "MAIHAR": 115, "RAMNAGAR": 55,
    "MAJHGAWAN": 96, "NAGOD": 94, "RAMPUR BAGHELAN": 97,
    "SATNA": 93, "UNCHAHARA": 70,
}


class MetaParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.meta = {}
        self.inputs = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta" and a.get("name") in ("_csrf", "_csrf_header"):
            self.meta[a["name"]] = a.get("content", "")
        if tag == "input" and a.get("id") == "contextPath":
            self.inputs[a["id"]] = a.get("value", "")


class Fetcher:
    def __init__(self):
        self.cookies = {}
        self.csrf = ""
        self.csrf_header = ""
        self.context_path = "/reportv2/"

    def get_page(self):
        req = urllib.request.Request(PAGE, headers={"User-Agent": "Mozilla/5.0", "Cache-Control": "no-cache"})
        with urllib.request.urlopen(req, timeout=45) as response:
            for item in response.headers.get_all("Set-Cookie", []):
                first = item.split(";", 1)[0]
                if "=" in first:
                    key, value = first.split("=", 1)
                    self.cookies[key] = value
            body = response.read().decode("utf-8", "replace")
        parser = MetaParser()
        parser.feed(body)
        self.csrf = parser.meta.get("_csrf", "")
        self.csrf_header = parser.meta.get("_csrf_header", "")
        self.context_path = parser.inputs.get("contextPath", "/reportv2/") or "/reportv2/"
        if not self.csrf or not self.csrf_header:
            raise RuntimeError("SECURE page did not provide CSRF metadata")

    def post_json(self, endpoint: str, data: dict, attempts=3):
        payload = urllib.parse.urlencode(data).encode()
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json, text/javascript, */*; q=0.01",
            "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
            "X-Requested-With": "XMLHttpRequest",
            "Referer": PAGE,
            self.csrf_header: self.csrf,
        }
        if self.cookies:
            headers["Cookie"] = "; ".join(f"{k}={v}" for k, v in self.cookies.items())
        req = urllib.request.Request(urllib.parse.urljoin(BASE, endpoint), data=payload, headers=headers, method="POST")
        last = None
        for attempt in range(attempts):
            try:
                with urllib.request.urlopen(req, timeout=45) as response:
                    raw = response.read().decode("utf-8", "replace")
                parsed = json.loads(raw)
                if "data" not in parsed or not isinstance(parsed["data"], list):
                    raise RuntimeError(f"Unexpected SECURE response at {endpoint}: {raw[:300]}")
                return parsed
            except Exception as exc:
                last = exc
                if attempt + 1 < attempts:
                    time.sleep(1.0 * (attempt + 1))
        raise RuntimeError(f"SECURE request failed at {endpoint}: {last}")


def dt(start=0, length=1000):
    return {
        "draw": "1", "start": str(start), "length": str(length),
        "search[value]": "", "search[regex]": "false",
        "order[0][column]": "0", "order[0][dir]": "asc",
    }


def fetch_all(fetcher, endpoint, filters, limit=100):
    rows, total = [], None
    start = 0
    while total is None or start < total:
        params = dt(start, limit)
        params.update(filters)
        result = fetcher.post_json(endpoint, params)
        part = result["data"]
        filtered = int(result.get("recordsFiltered", len(part)) or 0)
        total = filtered
        rows.extend(part)
        if not part:
            break
        start += len(part)
        if start >= total:
            break
    return rows, total or 0


def main():
    f = Fetcher()
    f.get_page()
    common = {"Scode": STATE_CODE, "year": FY, "searchkey": ""}
    district_params = dt(length=100)
    district_params.update({**common, "searchkey": "SATNA"})
    districts = f.post_json("reports/tsregister", district_params)["data"]
    satna = next((x for x in districts if x.get("dcode") == DISTRICT_CODE), None)
    if not satna:
        raise RuntimeError("District SATNA (1712) not present in SECURE district response")

    blocks, block_total = fetch_all(f, "reports/tsregisterbk", {**common, "Dcode": DISTRICT_CODE})
    output_blocks, output_gps, all_works, warnings = [], [], [], []
    for block in blocks:
        bcode = str(block.get("bcode", ""))
        bname = str(block.get("bname", "")).strip().upper()
        print(f"SECURE TS: {bname}", flush=True)
        gps, gp_total = fetch_all(f, "reports/tsregisterpt", {**common, "Bcode": bcode})
        approved_sum = sum(int(x.get("current_tscount") or 0) for x in gps)
        expected_block = int(block.get("current_tscount") or 0)
        expected_gp_count = EXPECTED_GP_COUNTS.get(bname)
        if expected_gp_count is not None and len(gps) != expected_gp_count:
            warnings.append({"block": bname, "kind": "panchayat_rows_incomplete", "expected": expected_gp_count, "received": len(gps), "backendRecordsFiltered": gp_total})
        elif expected_gp_count is None and len(gps) != gp_total:
            warnings.append({"block": bname, "kind": "panchayat_rows_incomplete", "reported": gp_total, "received": len(gps)})
        if approved_sum != expected_block:
            warnings.append({"block": bname, "kind": "panchayat_approved_sum_mismatch", "reported": expected_block, "received": approved_sum})
        candidates = [gp for gp in gps if int(gp.get("current_tscount") or 0) > 0]

        def fetch_gp(gp):
            pcode = str(gp.get("pcode", ""))
            works, work_total = fetch_all(f, "reports/tswork", {**common, "Pcode": pcode}, limit=100)
            return gp, works, work_total

        block_works = []
        # The official report has one work-detail request per GP. A small bounded
        # pool avoids long serial runs while keeping traffic moderate.
        with ThreadPoolExecutor(max_workers=4) as pool:
            future_map = {pool.submit(fetch_gp, gp): gp for gp in candidates}
            for done, future in enumerate(as_completed(future_map), 1):
                gp = future_map[future]
                pcode = str(gp.get("pcode", ""))
                pname = str(gp.get("pname", "")).strip()
                works, work_total = future.result()[1:]
                if len(works) != work_total:
                    warnings.append({"block": bname, "panchayat": pname, "kind": "work_rows_incomplete", "reported": work_total, "received": len(works)})
                for w in works:
                    code = str(w.get("wcode", "")).strip()
                    if not YD_RE.search(code):
                        continue
                    block_works.append({
                        "district": "MAIHAR" if bname in {"AMARPATAN", "MAIHAR", "RAMNAGAR"} else "SATNA",
                        "block": bname,
                        "blockCode": bcode,
                        "panchayat": pname,
                        "panchayatCode": pcode,
                        "workCode": code,
                        "workName": str(w.get("wname", "")).strip(),
                        "tsNo": str(w.get("tsno", "")).strip(),
                        "tsDate": str(w.get("tsdate", "")).strip(),
                    })
                if done % 10 == 0 or done == len(candidates):
                    print(f"  work detail GPs: {done}/{len(candidates)}", flush=True)
        block_works.sort(key=lambda w: (w["panchayat"], w["workCode"]))
        all_works.extend(block_works)
        gp_counts = {}
        for w in block_works:
            gp_counts[w["panchayatCode"]] = gp_counts.get(w["panchayatCode"], 0) + 1
        for gp in gps:
            pcode = str(gp.get("pcode", ""))
            output_gps.append({
                "district": "MAIHAR" if bname in {"AMARPATAN", "MAIHAR", "RAMNAGAR"} else "SATNA",
                "block": bname, "blockCode": bcode,
                "panchayat": str(gp.get("pname", "")).strip(), "panchayatCode": pcode,
                "secureCurrentTsAllCodes": int(gp.get("current_tscount") or 0),
                "ydTsCount": gp_counts.get(pcode, 0),
            })
        output_blocks.append({
            "district": "MAIHAR" if bname in {"AMARPATAN", "MAIHAR", "RAMNAGAR"} else "SATNA",
            "janpad": bname, "blockCode": bcode,
            "secureCurrentTsAllCodes": expected_block,
            "panchayatRowsReported": gp_total, "panchayatRowsExpected": expected_gp_count,
            "panchayatRowsReceived": len(gps),
            "securePanchayatTsSum": approved_sum,
            "ydTsCount": len(block_works),
        })
        print(f"  GP rows {len(gps)}/{gp_total}, SECURE TS {approved_sum}, /YD/ TS {len(block_works)}", flush=True)

    # One work code should count once in this register snapshot.
    seen = set()
    deduped = []
    for work in all_works:
        key = (work["blockCode"], work["workCode"])
        if key not in seen:
            seen.add(key)
            deduped.append(work)
    data = {
        "success": True, "fy": FY, "snapshotAt": datetime.now(timezone.utc).isoformat(),
        "basis": "SECURE TS approved works for selected FY 2026-2027; Work Code contains /YD/; no Oct 1 TS-date cutoff",
        "source": PAGE, "district": "SATNA", "districtCode": DISTRICT_CODE,
        "blocks": output_blocks, "panchayats": output_gps, "works": deduped,
        "totals": {"janpadCount": len(output_blocks), "panchayatCount": len(output_gps), "ydTsCount": len(deduped)},
        "warnings": warnings,
    }
    out = ROOT / "data" / "secure-ts-yuktadhara-fy2026-27.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    js_out = ROOT / "secure-ts-data.js"
    js_out.write_text("window.SECURE_TS_DATA=" + json.dumps({
        "schemaVersion": 2, "success": True, "fy": FY,
        "date": datetime.now().date().isoformat(), "fetchedAt": data["snapshotAt"],
        "startDate": None, "endDate": None, "source": PAGE,
        "basis": data["basis"], "blocks": data["blocks"],
        "panchayats": data["panchayats"], "works": data["works"],
        "totals": data["totals"], "warnings": warnings,
    }, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Saved {out}; /YD/ TS total={len(deduped)}; warnings={len(warnings)}", flush=True)


if __name__ == "__main__":
    main()
