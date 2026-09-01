"""
SRDM SATNA — VB-G RAM G Cloud Diagnostic Fetcher V2

Purpose:
- Retry official R6.9 page access on GitHub Actions.
- Save diagnostics when the cloud runner gets a blocked/different page.
- NEVER update dashboard data unless all 8 Janpads and required dropdowns parse.
"""

import csv
import json
import re
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent if HERE.name.lower() == "scripts_local" else HERE

CSV_PATH = ROOT / "data" / "official-summary.csv"
STATUS_JSON = ROOT / "data" / "fetch-status.json"
STATUS_JS = ROOT / "auto-status.js"
DIAG_DIR = ROOT / "diagnostics"
DIAG_DIR.mkdir(parents=True, exist_ok=True)

REPORT_URL = "https://vbgramgrep.dord.gov.in/VBGRAMG/dpc_sms_new.aspx?payload=c_dCXx6L-IMkcEdlRICw87o-OWrumZUuTOVJCtXMwo49VCcKVJKknrfE_4qO0AT_WQTG3yWM7D1kNUU7DSpTx1H8j3SYUjwu3q4dQX_CfBdu4ni8Iou1EYozxNZb5rwNvD2JMp78Hx-qNCdsq3ux6X1MITBA5uUF3gtds07lUIHnl4ONcwgjtjtzvWYQ0UDGVInRFjvVbtwWWXI7s8-I3jU8QwBBMeYwU7dbbckRQbgR_S8b6XGjuQ6EwEUi4ba3pW06r3n-L-iVwCLbYfyloXs1UzJGGw9YBlOFBm-hlzE"

JANPAD_ORDER = [
    "AMARPATAN", "MAIHAR", "MAJHGAWAN", "NAGOD",
    "RAMNAGAR", "RAMPUR BAGHELAN", "SATNA", "UNCHAHARA"
]

INDIVIDUAL_CATEGORY = "Works on Individuals Land (Category IV)"
PMAY_STATUS = "Constr of PMAY-G House for Individuals"
EK_BAGIYA_STATUS = "Block Plantation-Hort-Trees in fields-Individuals"


def clean_text(value):
    value = re.sub(r"<[^>]+>", "", value or "")
    value = value.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", value).strip()


def number(value):
    s = re.sub(r"[^\d.]", "", clean_text(value))
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def row_data(html):
    out = {}
    for row_html in re.findall(r"<tr[^>]*>(.*?)</tr>", html, re.I | re.S):
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", row_html, re.I | re.S)
        clean = [clean_text(c) for c in cells]
        clean = [c for c in clean if c]
        janpad = None
        janpad_index = None
        for i, cell in enumerate(clean):
            name = cell.upper().strip()
            for j in JANPAD_ORDER:
                if name == j or j in name or name in j:
                    janpad = j
                    janpad_index = i
                    break
            if janpad:
                break
        if not janpad:
            continue
        nums = [number(c) for c in clean[janpad_index + 1:]]
        if nums:
            out[janpad] = nums
    return out


def parse_all_report(html):
    rows = row_data(html)
    data = {}
    for j, nums in rows.items():
        if len(nums) < 6:
            continue
        total_gp = nums[0]
        gp_progress = nums[1]
        data[j] = {
            "totalGP": total_gp,
            "musterGP": gp_progress,
            "dysfunctionalGP": max(0, total_gp - gp_progress),
            "labourAll": nums[2],
            "mrAll": nums[3],
            "noEkyc": nums[4],
            "mrs": nums[5],
        }
    return data


def parse_category_report(html):
    rows = row_data(html)
    data = {}
    for j, nums in rows.items():
        if len(nums) < 6:
            continue
        data[j] = {
            "gps": nums[0],
            "gpsProgress": nums[1],
            "labour": nums[2],
            "ongoingMRWorks": nums[3],
            "noEkyc": nums[4],
            "mrs": nums[5],
        }
    return data


def select_label(select, label):
    try:
        select.select_option(label=label)
        return
    except Exception:
        options = select.locator("option").all()
        target = re.sub(r"\s+", " ", label).strip().lower()
        for opt in options:
            txt = re.sub(r"\s+", " ", (opt.inner_text() or "")).strip()
            if txt.lower() == target or target in txt.lower() or txt.lower() in target:
                select.select_option(value=opt.get_attribute("value"))
                return
        raise RuntimeError(f"Dropdown option not found: {label}")


def submit_and_wait(page):
    try:
        page.get_by_role("button", name=re.compile(r"submit", re.I)).click()
    except Exception:
        page.locator("input[type=submit],button[type=submit]").first.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(1500)


def save_diag(page, attempt, reason):
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = DIAG_DIR / f"attempt_{attempt}_{stamp}"
    try:
        (prefix.with_suffix(".html")).write_text(page.content(), encoding="utf-8")
    except Exception:
        pass
    try:
        page.screenshot(path=str(prefix.with_suffix(".png")), full_page=True)
    except Exception:
        pass

    info = {
        "attempt": attempt,
        "reason": reason,
        "url": page.url,
        "title": "",
        "select_count": 0,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    try:
        info["title"] = page.title()
    except Exception:
        pass
    try:
        info["select_count"] = page.locator("select").count()
    except Exception:
        pass

    try:
        body = page.locator("body").inner_text(timeout=5000)
        info["body_preview"] = body[:4000]
    except Exception:
        info["body_preview"] = ""

    (prefix.with_suffix(".json")).write_text(
        json.dumps(info, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    return info


def fetch_reports():
    from playwright.sync_api import sync_playwright

    last_error = None

    with sync_playwright() as p:
        for attempt in range(1, 4):
            browser = None
            try:
                browser = p.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ],
                )
                context = browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/128.0.0.0 Safari/537.36"
                    ),
                    locale="en-IN",
                    timezone_id="Asia/Kolkata",
                    viewport={"width": 1440, "height": 1000},
                    extra_http_headers={
                        "Accept-Language": "en-IN,en;q=0.9,hi;q=0.8",
                        "Cache-Control": "no-cache",
                        "Pragma": "no-cache",
                    },
                )
                page = context.new_page()
                response = page.goto(REPORT_URL, wait_until="domcontentloaded", timeout=60000)
                page.wait_for_timeout(5000)

                status = response.status if response else None
                selects = page.locator("select")
                select_count = selects.count()

                if status and status >= 400:
                    reason = f"HTTP status {status}"
                    info = save_diag(page, attempt, reason)
                    raise RuntimeError(f"{reason}; diagnostics saved; final_url={info.get('url')}")

                if select_count < 3:
                    reason = f"R6.9 filters not found: expected 3 dropdowns, got {select_count}"
                    info = save_diag(page, attempt, reason)

                    preview = (info.get("body_preview") or "").lower()
                    hints = []
                    for token in ["access denied", "unauthorized", "forbidden", "captcha", "cloudflare", "error"]:
                        if token in preview:
                            hints.append(token)
                    hint_text = f"; page hints={','.join(hints)}" if hints else ""

                    raise RuntimeError(
                        f"{reason}; diagnostics saved; title={info.get('title')}; "
                        f"final_url={info.get('url')}{hint_text}"
                    )

                # 1) ALL
                work_category = selects.nth(1)
                proposed_status = selects.nth(2)
                select_label(work_category, "ALL")
                select_label(proposed_status, "ALL")
                submit_and_wait(page)
                all_html = page.content()

                # 2) Individual
                selects = page.locator("select")
                work_category = selects.nth(1)
                proposed_status = selects.nth(2)
                select_label(work_category, INDIVIDUAL_CATEGORY)
                select_label(proposed_status, "ALL")
                submit_and_wait(page)
                individual_html = page.content()

                # 3) PMAY-G
                selects = page.locator("select")
                work_category = selects.nth(1)
                proposed_status = selects.nth(2)
                select_label(work_category, INDIVIDUAL_CATEGORY)
                select_label(proposed_status, PMAY_STATUS)
                submit_and_wait(page)
                pmay_html = page.content()

                # 4) Ek Bagiya
                selects = page.locator("select")
                work_category = selects.nth(1)
                proposed_status = selects.nth(2)
                select_label(work_category, INDIVIDUAL_CATEGORY)
                select_label(proposed_status, EK_BAGIYA_STATUS)
                submit_and_wait(page)
                ek_html = page.content()

                browser.close()
                return all_html, individual_html, pmay_html, ek_html

            except Exception as exc:
                last_error = exc
                try:
                    if browser:
                        browser.close()
                except Exception:
                    pass
                if attempt < 3:
                    time.sleep(8 * attempt)

    raise RuntimeError(f"Cloud fetch failed after 3 attempts: {last_error}")


def combine_reports(all_html, individual_html, pmay_html, ek_html):
    base = parse_all_report(all_html)
    individual = parse_category_report(individual_html)
    pmay = parse_category_report(pmay_html)
    ek = parse_category_report(ek_html)

    data = {}
    for j in JANPAD_ORDER:
        if j not in base:
            continue
        d = dict(base[j])

        if j in individual:
            d["labourIndividual"] = individual[j]["labour"]
            d["mrIndividual"] = individual[j]["mrs"]

        if j in pmay:
            d["pmayLabour"] = pmay[j]["labour"]
            d["pmayOngoing"] = pmay[j]["ongoingMRWorks"]
            d["pmayMR"] = pmay[j]["mrs"]

        if j in ek:
            d["ekLabour"] = ek[j]["labour"]
            d["ekOngoing"] = ek[j]["ongoingMRWorks"]
            d["ekMR"] = ek[j]["mrs"]

        data[j] = d
    return data


def update_csv(new_data):
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    required = [
        "totalGP", "musterGP", "dysfunctionalGP",
        "labourAll", "mrAll", "noEkyc", "mrs",
        "labourIndividual", "mrIndividual",
        "pmayLabour", "pmayOngoing", "pmayMR",
        "ekLabour", "ekOngoing", "ekMR",
    ]

    for name in required:
        if name not in fieldnames:
            fieldnames.append(name)

    for r in rows:
        j = (r.get("janpad") or "").strip().upper()
        if j not in new_data:
            continue
        d = new_data[j]
        for key in required:
            if key in d:
                r[key] = str(int(round(d[key])))

    with open(CSV_PATH, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)


def update_status(ok, note):
    today = datetime.now().strftime("%d-%m-%Y")
    status = {
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "ok": ok,
        "source": "Official VB-G RAM G R6.9 (GitHub cloud diagnostic V2)",
        "steps": [{"step": "R6.9 category fetch", "ok": ok, "detail": note}],
        "officialDate": today if ok else None,
        "note": note,
        "finishedAt": datetime.now(timezone.utc).isoformat(),
    }

    # On failure we only write diagnostics/status in workspace; workflow will NOT commit it.
    STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATUS_JSON.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8")
    STATUS_JS.write_text(
        "window.AUTO_FETCH_STATUS=" +
        json.dumps(status, ensure_ascii=False, separators=(",", ":")) + ";\n",
        encoding="utf-8",
    )


def main():
    try:
        all_html, individual_html, pmay_html, ek_html = fetch_reports()
        data = combine_reports(all_html, individual_html, pmay_html, ek_html)

        if len(data) != 8:
            raise RuntimeError(
                f"Safety stop: parsed {len(data)}/8 Janpads. Existing dashboard data not updated."
            )

        # Strong safety: only now overwrite the CSV.
        update_csv(data)

        ind_lab = sum(d.get("labourIndividual", 0) for d in data.values())
        ind_mr = sum(d.get("mrIndividual", 0) for d in data.values())
        pmay_lab = sum(d.get("pmayLabour", 0) for d in data.values())
        pmay_mr = sum(d.get("pmayMR", 0) for d in data.values())
        ek_lab = sum(d.get("ekLabour", 0) for d in data.values())
        ek_mr = sum(d.get("ekMR", 0) for d in data.values())

        note = (
            f"8/8 Janpads. "
            f"Individual Labour/MR={int(ind_lab)}/{int(ind_mr)}; "
            f"PMAY Labour/MR={int(pmay_lab)}/{int(pmay_mr)}; "
            f"Ek Bagiya Labour/MR={int(ek_lab)}/{int(ek_mr)}."
        )
        update_status(True, note)
        print("SUCCESS:", note)

    except Exception as e:
        msg = str(e)
        print("FAILED:", msg)
        update_status(False, msg)
        sys.exit(1)


if __name__ == "__main__":
    main()
