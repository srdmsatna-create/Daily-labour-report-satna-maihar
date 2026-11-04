"""
SRDM Satna — Local Daily Auto-Update Script (corrected)

R6.9 portal mapping:
  - ALL: main Screen-2 values
  - Individual: Work Category = Works on Individuals Land (Category IV), Proposed Status = ALL
  - PMAY-G: Work Category = Works on Individuals Land (Category IV),
            Proposed Status = Constr of PMAY-G House for Individuals
  - Ek Bagiya: Work Category = Works on Individuals Land (Category IV),
               Proposed Status = Block Plantation-Hort-Trees in fields-Individuals

For the three category reports, the script reads:
  - Labour = "Maximum Expected Unskilled Labour Engagement as per e-Muster Roll"
  - Muster Rolls = "No. of Muster Rolls (MRs)"
"""

import csv
import os
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Works correctly whether this file is kept in repo root or in scripts_local.
ROOT = HERE.parent if HERE.name.lower() == "scripts_local" else HERE

CSV_PATH = ROOT / "data" / "official-summary.csv"
STATUS_JSON = ROOT / "data" / "fetch-status.json"
STATUS_JS = ROOT / "auto-status.js"

REPORT_URL = "https://vbgramgrep.dord.gov.in/VBGRAMG/dpc_sms_new.aspx?payload=c_dCXx6L-IMkcEdlRICw87o-OWrumZUuTOVJCtXMwo49VCcKVJKknrfE_4qO0AT_WQTG3yWM7D1kNUU7DSpTx1H8j3SYUjwu3q4dQX_CfBdu4ni8Iou1EYozxNZb5rwNvD2JMp78Hx-qNCdsq3ux6X1MITBA5uUF3gtds07lUIHnl4ONcwgjtjtzvWYQ0UDGVInRFjvVbtwWWXI7s8-I3jU8QwBBMeYwU7dbbckRQbgR_S8b6XGjuQ6EwEUi4ba3pW06r3n-L-iVwCLbYfyloXs1UzJGGw9YBlOFBm-hlzE"

JANPAD_ORDER = [
    "AMARPATAN", "MAIHAR", "MAJHGAWAN", "NAGOD",
    "RAMNAGAR", "RAMPUR BAGHELAN", "SATNA", "UNCHAHARA"
]
REPORT_URL = os.environ.get('VBGRAM_DAILY_REPORT_URL','').strip() or REPORT_URL

INDIVIDUAL_CATEGORY = "Works on Individuals Land (Category IV)"
PMAY_STATUS = "Constr of PMAY-G House for Individuals"
EK_BAGIYA_STATUS = "Block Plantation-Hort-Trees in fields-Individuals"


def _clean_text(value):
    value = re.sub(r"<[^>]+>", "", value or "")
    value = value.replace("&nbsp;", " ")
    return re.sub(r"\s+", " ", value).strip()


def _number(value):
    s = re.sub(r"[^\d.]", "", _clean_text(value))
    try:
        return float(s) if s else 0.0
    except ValueError:
        return 0.0


def _row_data(html):
    """Return {JANPAD: [numeric cells after the Janpad cell]}."""
    from bs4 import BeautifulSoup
    out = {}
    for row in BeautifulSoup(html, 'html.parser').find_all('tr'):
        cells = row.find_all(['td','th'], recursive=False)
        # Layout tables can contain an entire nested report; never parse those
        # as one numeric row or shift values by dropping blank cells.
        if any(cell.find('table') for cell in cells):
            continue
        clean = [cell.get_text(' ', strip=True) for cell in cells]
        indices = [i for i,cell in enumerate(clean) if cell.upper().strip() in JANPAD_ORDER]
        if len(indices) != 1:
            continue
        i = indices[0];janpad = clean[i].upper().strip()
        nums = [_number(c) for c in clean[i + 1:]]
        if len(nums) >= 6:
            if janpad in out and out[janpad] != nums:
                raise ValueError('Conflicting official source rows: ' + janpad)
            out[janpad] = nums

    return out


def parse_all_report(html):
    """
    R6.9 ALL report columns after Blocks:
      Total GP, GP with Works in Progress, Labour,
      Ongoing Works for which MR issued, Workers without e-KYC, No. of MRs.
    """
    rows = _row_data(html)
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
            "mrAll": nums[3],       # works for which MR has been issued
            "noEkyc": nums[4],
            "mrs": nums[5],         # actual number of Muster Rolls
        }
    return data


def parse_category_report(html):
    """
    Category report columns after Blocks:
      Total GP, GP with Works in Progress, Labour,
      Ongoing Works for which MR issued, Workers without e-KYC, No. of MRs.
    """
    rows = _row_data(html)
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


def _select_label(select, label):
    """Select a dropdown item by visible label, with a text-match fallback."""
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


def _submit_and_wait(page):
    try:
        page.get_by_role("button", name=re.compile(r"submit", re.I)).click()
    except Exception:
        page.locator("input[type=submit],button[type=submit]").first.click()
    page.wait_for_load_state("networkidle", timeout=60000)
    page.wait_for_timeout(1200)


def _select_with_option(page, label, exclude=None):
    """Find a select by available option text, independent of form order."""
    target = re.sub(r"\s+", " ", label).strip().lower()
    matches = []
    for i in range(page.locator("select").count()):
        control = page.locator("select").nth(i)
        if exclude is not None and i == exclude:
            continue
        labels = [re.sub(r"\s+", " ", (opt.inner_text() or "")).strip().lower()
                  for opt in control.locator("option").all()]
        if any(text == target or target in text for text in labels):
            matches.append(i)
    if len(matches) != 1:
        raise RuntimeError(
            f"R6.9 dropdown for {label!r} is not unique; matching indexes={matches}, "
            f"total selects={page.locator('select').count()}"
        )
    return page.locator("select").nth(matches[0]), matches[0]


def _r69_category(page):
    return _select_with_option(page, INDIVIDUAL_CATEGORY)


def _r69_status(page, category_index):
    try:
        return _select_with_option(page, PMAY_STATUS, exclude=category_index)[0]
    except RuntimeError as exc:
        try:
            title = page.title()
            visible = re.sub(r"\s+", " ", page.locator("body").inner_text())[:1000]
        except Exception as detail_exc:
            title = "unavailable"
            visible = "page diagnostic failed: " + str(detail_exc)
        raise RuntimeError(
            f"{exc}; URL={page.url!r}; title={title!r}; page says: {visible}"
        ) from exc

def fetch_reports():
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        # The official R6.9 page serves only its header to headless Chromium.
        # Use a visible browser session, matching normal portal access on this PC.
        browser = p.chromium.launch(
            headless=False,
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
        )
        context.add_init_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
        )
        cookies=[]
        for pair in os.environ.get('VBGRAM_COOKIE','').split(';'):
            if '=' in pair:
                k,v=pair.strip().split('=',1)
                cookies.append({'name':k,'value':v,'domain':'vbgramgrep.dord.gov.in','path':'/'})
        if cookies:context.add_cookies(cookies)
        page=context.new_page()
        response = page.goto(REPORT_URL, wait_until="domcontentloaded", timeout=60000)
        # R6.9 controls can appear after the page shell. Wait for the form instead
        # of checking after a fixed 1.5 seconds.
        try:
            page.locator("select").first.wait_for(state="attached", timeout=20000)
        except Exception:
            try:
                title = page.title()
                visible = re.sub(r"\s+", " ", page.locator("body").inner_text())[:1000]
            except Exception as detail_exc:
                title = "unavailable"
                visible = "page diagnostic failed: " + str(detail_exc)
            status = response.status if response else "unknown"
            current_url = page.url
            browser.close()
            raise RuntimeError(
                f"R6.9 form did not render within 20 seconds; HTTP={status}; "
                f"URL={current_url!r}; title={title!r}; page says: {visible}"
            )

        page.wait_for_load_state("networkidle", timeout=60000)
        try:
            work_category, category_index = _r69_category(page)
        except RuntimeError as exc:
            visible = re.sub(r"\s+", " ", page.locator("body").inner_text())[:500]
            browser.close()
            raise RuntimeError(f"{exc}; page says: {visible}") from exc

        # 1) ALL report
        _select_label(work_category, "ALL")
        page.wait_for_load_state("networkidle", timeout=60000)
        proposed_status = _r69_status(page, category_index)
        _select_label(proposed_status, "ALL")
        page.wait_for_load_state("networkidle", timeout=60000)
        _submit_and_wait(page)
        all_html = page.content()

        # 2) Individual
        work_category, category_index = _r69_category(page)
        _select_label(work_category, INDIVIDUAL_CATEGORY)
        page.wait_for_load_state("networkidle", timeout=60000)
        proposed_status = _r69_status(page, category_index)
        _select_label(proposed_status, "ALL")
        _submit_and_wait(page)
        individual_html = page.content()

        # 3) PMAY-G
        work_category, category_index = _r69_category(page)
        _select_label(work_category, INDIVIDUAL_CATEGORY)
        page.wait_for_load_state("networkidle", timeout=60000)
        proposed_status = _r69_status(page, category_index)
        _select_label(proposed_status, PMAY_STATUS)
        _submit_and_wait(page)
        pmay_html = page.content()

        # 4) Ek Bagiya
        work_category, category_index = _r69_category(page)
        _select_label(work_category, INDIVIDUAL_CATEGORY)
        page.wait_for_load_state("networkidle", timeout=60000)
        proposed_status = _r69_status(page, category_index)
        _select_label(proposed_status, EK_BAGIYA_STATUS)
        _submit_and_wait(page)
        ek_html = page.content()

        browser.close()

    return all_html, individual_html, pmay_html, ek_html


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
    rows = []
    with open(CSV_PATH, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = list(reader.fieldnames or [])
        rows = list(reader)

    # pmayLabour is needed by the corrected dashboard mapping.
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

    print(f"Updated {CSV_PATH} for {len(new_data)} janpads")


def update_status(ok, note):
    today = datetime.now().strftime("%d-%m-%Y")
    status = {
        "startedAt": datetime.now(timezone.utc).isoformat(),
        "ok": ok,
        "source": "Official VB-G RAM G R6.9 (local PC fetch)",
        "steps": [{"step": "R6.9 category fetch", "ok": ok, "detail": note}],
        "officialDate": today,
        "note": note,
        "finishedAt": datetime.now(timezone.utc).isoformat(),
    }
    STATUS_JSON.parent.mkdir(parents=True, exist_ok=True)
    STATUS_JSON.write_text(
        json.dumps(status, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    STATUS_JS.write_text(
        "window.AUTO_FETCH_STATUS=" +
        json.dumps(status, ensure_ascii=False, separators=(",", ":")) +
        ";\n",
        encoding="utf-8",
    )


def main():
    try:
        all_html, individual_html, pmay_html, ek_html = fetch_reports()
        data = combine_reports(all_html, individual_html, pmay_html, ek_html)
        for j in JANPAD_ORDER:
            if j in data:
                d=data[j]
                print(f"Official ALL {j}: GP={d['totalGP']:g}; progress={d['musterGP']:g}; labour={d['labourAll']:g}; MR works={d['mrAll']:g}", flush=True)

        if len(data) < 8:
            raise RuntimeError(
                f"Only {len(data)}/8 Janpads parsed. Existing CSV was not changed."
            )

        update_csv(data)

        # Print totals as a quick validation against the portal screenshots.
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
        print("Next: python scripts\\merge_official_summary.py")

    except Exception as e:
        print(f"FAILED: {e}")
        update_status(False, str(e))
        sys.exit(1)


if __name__ == "__main__":
    main()
