"""
SRDM Satna — Local Daily Auto-Update Script
Runs on your own PC (not cloud), so the official government portal
does not block it like it blocks GitHub's cloud servers.

What it does each time it runs:
  1. Opens the official VB-G RAM G report link using a real (Playwright) browser
  2. Reads the 8-Janpad Screen-2 summary table
  3. Updates data/official-summary.csv
  4. Rebuilds auto-data.js from the CSV
  5. Updates data/fetch-status.json / auto-status.js with today's timestamp
"""
import csv, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent  # assumes script sits in <repo>/scripts_local/
CSV_PATH = ROOT / "data" / "official-summary.csv"
STATUS_JSON = ROOT / "data" / "fetch-status.json"
STATUS_JS = ROOT / "auto-status.js"

# ---- EDIT THIS: paste your saved R6.9 report link here ----
REPORT_URL = "https://vbgramgrep.dord.gov.in/VBGRAMG/dpc_sms_new.aspx?payload=c_dCXx6L-IMkcEdlRICw87o-OWrumZUuTOVJCtXMwo49VCcKVJKknrfE_4qO0AT_WQTG3yWM7D1kNUU7DSpTx1H8j3SYUjwu3q4dQX_CfBdu4ni8Iou1EYozxNZb5rwNvD2JMp78Hx-qNCdsq3ux6X1MITBA5uUF3gtds07lUIHnl4ONcwgjtjtzvWYQ0UDGVInRFjvVbtwWWXI7s8-I3jU8QwBBMeYwU7dbbckRQbgR_S8b6XGjuQ6EwEUi4ba3pW06r3n-L-iVwCLbYfyloXs1UzJGGw9YBlOFBm-hlzE"
# -------------------------------------------------------------

JANPAD_ORDER = ['AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA']

def fetch_table():
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36'
        )
        page.goto(REPORT_URL, wait_until='networkidle', timeout=60000)
        page.wait_for_timeout(2000)
        html = page.content()
        browser.close()
        return html

def parse_table(html):
    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S)
    data = {}

    for r in rows:
        cells = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
        clean = [re.sub('<[^>]+>', '', c).strip() for c in cells]
        clean = [c for c in clean if c != '']

        if len(clean) < 20:
            continue

        name = clean[0].upper().strip()

        # Match against known janpad names
        for j in JANPAD_ORDER:
            if j in name or name in j:
                nums = []

                for c in clean[1:]:
                    n = re.sub(r'[^\d.]', '', c)
                    nums.append(float(n) if n else 0)

                if len(nums) >= 20:
                    data[j] = {
                        'totalGP': nums[0],
                        'musterGP': nums[1],
                        'dysfunctionalGP': nums[2],

                        'labourAll': nums[3],
                        'mrAll': nums[4],
                        'ongoingAll': nums[5],
                        'mrs': nums[6],
                         'labourIndividual': nums[8],
                        'mrIndividual': nums[9],

                        'labourCommunity': nums[10],
                        'mrCommunity': nums[11],

                        'pmayOngoing': nums[13],
                        'pmayMR': nums[14],

                        'ekLabour': nums[16],
                        'ekOngoing': nums[17],
                        'ekMR': nums[18],
                    }

                break

    return data


def update_csv(new_data):
    rows = []

    with open(CSV_PATH, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for r in reader:
            j = r['janpad'].strip().upper()

            if j in new_data:
                d = new_data[j]

                r['totalGP'] = str(int(d['totalGP']))
                r['musterGP'] = str(int(d['musterGP']))
                r['dysfunctionalGP'] = str(int(d['dysfunctionalGP']))

                r['labourAll'] = str(int(d['labourAll']))
                r['mrAll'] = str(int(d['mrAll']))
                r['ongoingAll'] = str(int(d['ongoingAll']))
                r['mrs'] = str(int(d['mrs']))

                r['labourIndividual'] = str(int(d['labourIndividual']))
                r['mrIndividual'] = str(int(d['mrIndividual']))

                r['labourCommunity'] = str(int(d['labourCommunity']))
                r['mrCommunity'] = str(int(d['mrCommunity']))

                r['pmayOngoing'] = str(int(d['pmayOngoing']))
                r['pmayMR'] = str(int(d['pmayMR']))

                r['ekLabour'] = str(int(d['ekLabour']))
                r['ekOngoing'] = str(int(d['ekOngoing']))
                r['ekMR'] = str(int(d['ekMR']))

            rows.append(r)

    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)

    print(f"Updated {CSV_PATH} for {len(new_data)} janpads")