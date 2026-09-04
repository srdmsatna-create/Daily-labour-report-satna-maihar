#!/usr/bin/env python3
"""Update the SRDM Shramik Niyojan dashboard from the official Persondays report."""

import html
import json
import math
import os
import re
import sys
import urllib.parse
from datetime import date, datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "shramik-niyojan-data.js"

CURRENT_URL = os.environ.get(
    "SHRAMIK_FY2627_URL",
    "https://vbgramgrep.dord.gov.in/VBGRAMG/demand_emp_demand.aspx?file1=empprov&page1=d&lflag=eng&state_name=MADHYA+PRADESH&state_code=17&district_name=SATNA&district_code=1712&fin_year=2026-2027&source=national&rbl=0&rblhpb=Household&Digest=kG%2fjf+M7b1AUbpMqWwepqQ",
)

TARGETS = {
    "AMARPATAN": {"august": 19419, "september": 17907},
    "MAIHAR": {"august": 18773, "september": 17026},
    "MAJHGAWAN": {"august": 11998, "september": 8476},
    "NAGOD": {"august": 13562, "september": 15107},
    "RAMNAGAR": {"august": 14041, "september": 23956},
    "RAMPUR BAGHELAN": {"august": 29893, "september": 32711},
    "SATNA": {"august": 18156, "september": 18331},
    "UNCHAHARA": {"august": 13072, "september": 10649},
}
ORDER = list(TARGETS)
MAIHAR_BLOCKS = {"AMARPATAN", "MAIHAR", "RAMNAGAR"}


def clean(value):
    value = html.unescape(re.sub(r"<[^>]+>", "", value or ""))
    return re.sub(r"\s+", " ", value).strip()


def norm(value):
    return clean(value).upper().replace("RAMPOR BAGHELAN", "RAMPUR BAGHELAN")


def number(value):
    try:
        return int(round(float(re.sub(r"[^0-9.-]", "", clean(value).replace(",", "")) or 0)))
    except Exception:
        return 0


def district(block):
    return "MAIHAR" if norm(block) in MAIHAR_BLOCKS else "SATNA"


def month_values_after(cells, entity_index):
    values = [number(x) for x in cells[entity_index + 1 :]]
    if len(values) < 6:
        return None
    return {"august": values[4], "september": values[5]}


def parse_block_rows(source):
    result = {}
    links = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", source, re.I | re.S):
        raw_cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.I | re.S)
        cells = [clean(x) for x in raw_cells]
        for i, cell in enumerate(cells):
            block = norm(cell)
            if block not in TARGETS:
                continue
            values = month_values_after(cells, i)
            if values:
                result[block] = values
            href = re.search(r'href=["\']([^"\']+)["\']', raw_cells[i], re.I)
            if not href:
                href = re.search(r'href=["\']([^"\']+)["\']', tr, re.I)
            if href:
                links[block] = html.unescape(href.group(1))
            break
    return result, links


def parse_gp_rows(source):
    result = {}
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", source, re.I | re.S):
        cells = [clean(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.I | re.S)]
        if len(cells) < 8 or not re.fullmatch(r"\d+", cells[0] or ""):
            continue
        gp = norm(cells[1])
        if not gp or gp in {"TOTAL", "BLOCK TOTAL"}:
            continue
        values = month_values_after(cells, 1)
        if values:
            result[gp] = values
    return result


def report_date(source):
    plain = clean(source)
    match = re.search(r"(?:As\s*on|updated\s*(?:on|date)?)\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})", plain, re.I)
    return match.group(1) if match else datetime.now().strftime("%d-%m-%Y")


def load_mapping():
    text = (ROOT / "auto-data.js").read_text(encoding="utf-8", errors="ignore")
    match = re.search(r"window\.AUTO_REPORT\s*=\s*(\{.*\});\s*$", text, re.S)
    if not match:
        raise RuntimeError("auto-data.js mapping could not be read")
    payload = json.loads(match.group(1))
    mapping = {}
    for row in payload.get("rows", []):
        block, gp = norm(row.get("janpad")), norm(row.get("panchayat"))
        if block in TARGETS and gp:
            mapping[(block, gp)] = {
                "engineer": clean(row.get("engineer")) or "Unmapped",
                "cluster": clean(row.get("cluster")) or "Unmapped",
            }
    return mapping


def previous_url():
    explicit = os.environ.get("SHRAMIK_FY2526_URL")
    if explicit:
        return explicit
    return CURRENT_URL.replace("fin_year=2026-2027", "fin_year=2025-2026")


def fetch_report(page, url, require_all_blocks=True):
    page.goto(url, wait_until="domcontentloaded", timeout=90000)
    page.wait_for_timeout(2000)
    source = page.content()
    blocks, links = parse_block_rows(source)
    if require_all_blocks and set(blocks) != set(TARGETS):
        raise RuntimeError(f"Persondays report parsed only {len(blocks)}/8 Janpads")
    if require_all_blocks and sum(x["august"] + x["september"] for x in blocks.values()) <= 0:
        raise RuntimeError("Persondays report returned zero August/September achievement")
    gp_rows = {}
    for block, href in links.items():
        detail_url = urllib.parse.urljoin(page.url, href)
        page.goto(detail_url, wait_until="domcontentloaded", timeout=90000)
        page.wait_for_timeout(800)
        gp_rows[block] = parse_gp_rows(page.content())
    return blocks, gp_rows, report_date(source)


def parse_date(value):
    for pattern in ("%d-%m-%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(value, pattern).date()
        except ValueError:
            pass
    return date.today()


def remaining_september_days(as_on):
    d = parse_date(as_on)
    if d < date(2026, 9, 1):
        return 30
    if d > date(2026, 9, 30):
        return 0
    return max(0, 30 - d.day)


def calc(target, august, september, days):
    achievement = august + september
    difference = max(0, target - achievement)
    daily = math.ceil(difference / days) if days else 0
    return {
        "target": target,
        "augustAchievement": august,
        "septemberAchievement": september,
        "achievement": achievement,
        "difference": difference,
        "remainingDays": days,
        "dailyRequired": daily,
        "dailyTarget125": math.ceil((difference / days) * 1.25) if days else 0,
        "achievementPct": round((achievement * 100 / target), 2) if target else 0,
    }


def main():
    from playwright.sync_api import sync_playwright

    mapping = load_mapping()
    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/128 Safari/537.36"
        )
        page = context.new_page()
        current_blocks, current_gp, official_date = fetch_report(page, CURRENT_URL)
        previous_gp = {}
        previous_warning = ""
        try:
            _, previous_gp, _ = fetch_report(page, previous_url(), require_all_blocks=False)
        except Exception as exc:
            previous_warning = f"FY 2025-26 Sub Engineer baseline unavailable: {exc}"
        browser.close()

    days = remaining_september_days(official_date)
    janpad_rows = []
    for block in ORDER:
        baseline = TARGETS[block]["august"] + TARGETS[block]["september"]
        cur = current_blocks[block]
        janpad_rows.append({
            "level": "janpad", "district": district(block), "janpad": block,
            "engineer": "", "cluster": "",
            **calc(baseline, cur["august"], cur["september"], days),
        })

    # Exact Sub Engineer rows are produced only when both FYs have GP detail.
    engineer_rows = []
    grouped = {}
    all_keys = set()
    if previous_gp:
        for block in ORDER:
            all_keys.update((block, gp) for gp in current_gp.get(block, {}))
            all_keys.update((block, gp) for gp in previous_gp.get(block, {}))
        for block, gp in all_keys:
            owner = mapping.get((block, gp), {"engineer": "Unmapped", "cluster": "Unmapped"})
            key = (block, owner["engineer"], owner["cluster"])
            row = grouped.setdefault(key, {"target": 0, "august": 0, "september": 0})
            cur = current_gp.get(block, {}).get(gp, {})
            prev = previous_gp.get(block, {}).get(gp, {})
            row["august"] += int(cur.get("august", 0))
            row["september"] += int(cur.get("september", 0))
            row["target"] += int(prev.get("august", 0)) + int(prev.get("september", 0))
    for (block, engineer, cluster), values in sorted(grouped.items()):
        engineer_rows.append({
            "level": "engineer", "district": district(block), "janpad": block,
            "engineer": engineer, "cluster": cluster,
            **calc(values["target"], values["august"], values["september"], days),
        })

    payload = {
        "title": "श्रमिक नियोजन",
        "financialYear": "2026-2027",
        "officialDate": official_date,
        "updatedAt": datetime.now(timezone.utc).isoformat(),
        "source": CURRENT_URL,
        "remainingSeptemberDays": days,
        "targetTotal": sum(x["target"] for x in janpad_rows),
        "rows": janpad_rows,
        "engineerRows": engineer_rows,
        "warnings": [x for x in [previous_warning] if x],
    }
    OUT.write_text(
        "window.SHRAMIK_NIYOJAN=" + json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )
    print(f"Shramik Niyojan updated: 8 Janpads, {len(engineer_rows)} Sub Engineer rows, as on {official_date}")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"FAILED: {exc}")
        sys.exit(1)
