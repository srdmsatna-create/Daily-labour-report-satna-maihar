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
    # Save the raw page for debugging if parsing fails
    debug_path = ROOT / "debug_page.html"
    debug_path.write_text(html, encoding='utf-8')

    rows = re.findall(r'<tr[^>]*>(.*?)</tr>', html, re.S)
    print(f"DEBUG: found {len(rows)} <tr> rows total in page")

    data = {}
    for r in rows:
        cells = re.findall(r'<t[dh][^>]*>(.*?)</t[dh]>', r, re.S)
        clean = [re.sub('<[^>]+>', '', c).strip() for c in cells]
        clean = [c for c in clean if c != '']
        # Row shape is: [SNo, BlockName, TotalGP, GPProgress, Labour, MR, noEKYC, MRs]
        if len(clean) < 8:
            continue
        name = clean[1].upper().strip()
        for j in JANPAD_ORDER:
            if j in name or name in j:
                nums = []
                for c in clean[2:8]:
                    n = re.sub(r'[^\d.]', '', c)
                    nums.append(float(n) if n else 0)
                if len(nums) >= 6:
                    data[j] = {
                        'totalGP': nums[0], 'musterGP': nums[1], 'labourAll': nums[2],
                        'mrAll': nums[3], 'noEkyc': nums[4], 'mrs': nums[5],
                    }
                break

    print(f"DEBUG: matched {len(data)}/8 janpads: {list(data.keys())}")
    if len(data) < 8:
        print(f"DEBUG: raw page saved to {debug_path} for inspection")
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
                r['dysfunctionalGP'] = str(max(0, int(d['totalGP']) - int(d['musterGP'])))
                r['labourAll'] = str(int(d['labourAll']))
                r['mrAll'] = str(int(d['mrAll']))
                r['noEkyc'] = str(int(d['noEkyc']))
                r['mrs'] = str(int(d['mrs']))
            rows.append(r)
    with open(CSV_PATH, 'w', encoding='utf-8-sig', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fieldnames)
        w.writeheader()
        w.writerows(rows)
    print(f"Updated {CSV_PATH} for {len(new_data)} janpads")

def update_status(ok, note):
    today = datetime.now().strftime('%d-%m-%Y')
    status = {
        'startedAt': datetime.now(timezone.utc).isoformat(),
        'ok': ok,
        'source': 'Official VB-G RAM G (local PC fetch)',
        'steps': [{'step': 'local browser fetch', 'ok': ok, 'detail': note}],
        'officialDate': today,
        'note': note,
    }
    status['finishedAt'] = datetime.now(timezone.utc).isoformat()
    STATUS_JSON.write_text(json.dumps(status, ensure_ascii=False, indent=2), encoding='utf-8')
    STATUS_JS.write_text(
        'window.AUTO_FETCH_STATUS=' + json.dumps(status, ensure_ascii=False, separators=(',', ':')) + ';\n',
        encoding='utf-8'
    )

def main():
    if 'PASTE_YOUR' in REPORT_URL:
        print("ERROR: Edit this file and paste your R6.9 report link into REPORT_URL first.")
        sys.exit(1)
    try:
        html = fetch_table()
        data = parse_table(html)
        if len(data) < 8:
            print(f"WARNING: only found {len(data)}/8 janpads. Not updating (data may be wrong).")
            update_status(False, f"Only {len(data)}/8 janpads parsed; kept previous data.")
            sys.exit(1)
        update_csv(data)
        update_status(True, f"{len(data)}/8 janpads updated from local PC fetch.")
        print("SUCCESS. Now run: python scripts/merge_official_summary.py")
    except Exception as e:
        print(f"FAILED: {e}")
        update_status(False, str(e))
        sys.exit(1)

if __name__ == '__main__':
    main()
