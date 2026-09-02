#!/usr/bin/env python3
"""Build Satna's 8-block VB-G RAM G At-a-Glance table from the official portal."""
import html, http.cookiejar, json, re, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "vbg-block-stats.js"
BASE = "https://vbgramgrep.dord.gov.in/VBGRAMG/vbgramg_ataglance/"
FORM = BASE + "At_a_glance.aspx"
BLOCKS = [
    ("AMARPATAN", "1712006"), ("MAIHAR", "1712008"),
    ("MAJHGAWAN", "1712001"), ("NAGOD", "1712003"),
    ("RAMNAGAR", "1712007"), ("RAMPUR BAGHELAN", "1712005"),
    ("SATNA", "1712002"), ("UNCHAHARA", "1712004"),
]

def hidden_fields(source):
    data = {}
    for tag in re.findall(r'<input[^>]+type="hidden"[^>]*>', source, re.I):
        name = re.search(r'name="([^"]+)"', tag, re.I)
        value = re.search(r'value="([^"]*)"', tag, re.I)
        if name:
            data[html.unescape(name.group(1))] = html.unescape(value.group(1) if value else "")
    return data

def text(value):
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", value or ""))).strip()

def number(value):
    try: return float(re.sub(r"[^0-9.-]", "", value.replace(",", "")) or 0)
    except Exception: return 0.0

def parse_metrics(source):
    metrics = {}
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", source, re.I | re.S):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row, re.I | re.S)
        if len(cells) >= 2:
            metrics[text(cells[0]).lower()] = text(cells[1])
    def find(*needles):
        for label, value in metrics.items():
            if all(n in label for n in needles): return number(value)
        return 0.0
    total = find("total no. of workers")
    active = find("total no. of active workers")
    return {
        "totalWorkers": total,
        "activeWorkers": active,
        "activeWorkerPct": round(active * 100 / total, 2) if total else 0,
        "hhBenefitted": find("total households worked"),
        "personDays": find("persondays of central liability"),
        "womenPct": find("women persondays out of total"),
        "assetsCreated": find("number of completed works"),
        "totalExpenditureLakh": find("total exp", "lakhs"),
    }

def fetch_block(block_name, block_code):
    jar = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    headers = {"User-Agent": "Mozilla/5.0", "Referer": FORM, "Cache-Control": "no-cache"}
    def request(payload=None):
        req = urllib.request.Request(FORM, data=payload, headers=headers)
        return opener.open(req, timeout=90).read().decode("utf-8", "ignore")
    def postback(source, target, values):
        data = hidden_fields(source)
        data.update({"__EVENTTARGET": target, "__EVENTARGUMENT": ""})
        data.update(values)
        return request(urllib.parse.urlencode(data).encode())

    source = request()
    source = postback(source, "ctl00$ContentPlaceHolder1$ddl_state", {
        "ctl00$ContentPlaceHolder1$ddl_state": "17"})
    source = postback(source, "ctl00$ContentPlaceHolder1$ddl_dist", {
        "ctl00$ContentPlaceHolder1$ddl_state": "17",
        "ctl00$ContentPlaceHolder1$ddl_dist": "1712"})
    source = postback(source, "ctl00$ContentPlaceHolder1$ddl_blk", {
        "ctl00$ContentPlaceHolder1$ddl_state": "17",
        "ctl00$ContentPlaceHolder1$ddl_dist": "1712",
        "ctl00$ContentPlaceHolder1$ddl_blk": block_code})
    data = hidden_fields(source)
    data.pop("__EVENTTARGET", None); data.pop("__EVENTARGUMENT", None)
    data.update({
        "ctl00$ContentPlaceHolder1$ddl_state": "17",
        "ctl00$ContentPlaceHolder1$ddl_dist": "1712",
        "ctl00$ContentPlaceHolder1$ddl_blk": block_code,
        "ctl00$ContentPlaceHolder1$ddl_pan": "",
        "ctl00$ContentPlaceHolder1$btproceed": "View Detail",
    })
    outer = request(urllib.parse.urlencode(data).encode())
    matches = re.findall(r'<iframe[^>]+src="([^"]+)"', outer, re.I)
    if not matches: raise RuntimeError(f"Official detail URL not returned for {block_name}")
    detail_url = urllib.parse.urljoin(BASE, html.unescape(matches[0]))
    detail = opener.open(urllib.request.Request(detail_url, headers=headers), timeout=90).read().decode("utf-8", "ignore")
    date_match = re.search(r"As on\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})", text(detail), re.I)
    row = {"block": block_name, **parse_metrics(detail)}
    return row, date_match.group(1) if date_match else ""

def main():
    rows, dates = [], []
    for name, code in BLOCKS:
        print(f"Fetching official At-a-Glance: {name}")
        row, official_date = fetch_block(name, code)
        if row["totalWorkers"] <= 0: raise RuntimeError(f"Invalid official data for {name}")
        rows.append(row); dates.append(official_date)
    payload = {
        "district": "SATNA", "financialYear": "2026-2027",
        "officialDate": max(dates) if dates else "",
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "source": FORM, "rows": rows,
    }
    OUT.write_text("window.VBG_BLOCK_STATS=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"Wrote {OUT} with {len(rows)} official block rows")

if __name__ == "__main__": main()
