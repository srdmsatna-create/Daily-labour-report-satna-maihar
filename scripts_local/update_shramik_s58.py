"""Fetch FY 2026–27 S5.8 ongoing counts for 52 source districts and 17 Janpads."""
import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from update_shramik_state import GRID, norm, number, write_js

ROOT = Path(__file__).resolve().parents[1]
URL = (
    'https://vbgramgrep.dord.gov.in/VBGRAMG/state_html/allwrkexp_dtl_main.aspx?payload='
    'kqEuY6uZqB9r_uodloUMfnfq7A-R7QvhF74uLIhDG2QFZ3O34Etoz3kMYqGMqPv70RZazi4oEIbQ1uVvS-qwQfW8aWCU3ImkAOoH5w39kXnYcQnBy___T1JAL2nNWpIaMbNSddkweR9oTWeG480j9px_L4Er8SmUaoWcBA4PTLNWsXlbx5mApZYrkWIYSkn4qFuvGycvQ2JLnRlKq9R8zQGLjD0F6n16Y-pGeUt3bP8ne3vJh8Ggx0uGpW7czfYwZFsrA0QK_Ev9CsOMVJgfdQ'
)
BLOCKS = {
    'SATNA': set('AMARPATAN|MAIHAR|MAJHGAWAN|NAGOD|RAMNAGAR|RAMPUR BAGHELAN|SATNA|UNCHAHARA'.split('|')),
    'REWA': set('GANGEV|HANUMANA|JAWA|MAUGANJ|NAIGARHI|RAIPUR KARCHULIYAN|REWA|SIRMOUR|TEONTHAR'.split('|')),
}


def district_names(root):
    baseline = json.loads((root / 'shramik-fy2526-fixed-baseline.json').read_text(encoding='utf-8'))
    return {norm(row['district']) for row in baseline['rows']}


def read_counts(page, names):
    page.get_by_text(re.compile(r'S5\.8.*ongoing works.*2026[-–]2027', re.I)).first.wait_for()
    candidates = []
    for table in page.locator('table').evaluate_all(GRID):
        header = next((row for row in table if any(norm(cell) == 'TOTAL WORKS ONGOING' for cell in row)), [])
        if not header:
            continue
        column = next(i for i, cell in enumerate(header) if norm(cell) == 'TOTAL WORKS ONGOING')
        counts = {}
        for row in table:
            if len(row) <= column or column < 1:
                continue
            name = norm(row[column - 1])
            if name in names:
                if name in counts:
                    raise ValueError(f'Duplicate S5.8 row: {name}')
                counts[name] = number(row[column])
        if counts.keys() == names:
            candidates.append(counts)
    if not candidates or any(counts != candidates[0] for counts in candidates):
        raise ValueError('S5.8 Total Works Ongoing column missing, incomplete or ambiguous')
    return candidates[0]


def validate(payload, root):
    if payload['retrievedDate'] != datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat():
        raise ValueError('Current S5.8 retrieval required')
    if payload['districts'].keys() != district_names(root) or payload['blocks'].keys() != BLOCKS.keys():
        raise ValueError('Incomplete S5.8 district coverage')
    for district, names in BLOCKS.items():
        counts = payload['blocks'][district]
        if counts.keys() != names or sum(counts.values()) != payload['districts'][district]:
            raise ValueError(f'S5.8 {district} Janpad totals differ from the state table')


def main():
    from playwright.sync_api import sync_playwright

    url = os.environ.get('SHRAMIK_S58_URL') or URL
    with sync_playwright() as playwright:
        try:
            browser = playwright.chromium.launch(channel='chrome', headless=True)
        except Exception:
            browser = playwright.chromium.launch(headless=True)
        context = browser.new_context()
        cookies = []
        for pair in os.environ.get('VBGRAM_COOKIE', '').split(';'):
            name, sep, value = pair.strip().partition('=')
            if name and sep:
                cookies.append({'name': name, 'value': value, 'domain': 'vbgramgrep.dord.gov.in', 'path': '/'})
        if cookies:
            context.add_cookies(cookies)
        page = context.new_page()
        response = page.goto(url, wait_until='domcontentloaded', timeout=60000)
        if response and response.status >= 400:
            raise RuntimeError(f'S5.8 state source HTTP {response.status}')
        districts = read_counts(page, district_names(ROOT))
        blocks = {}
        for district, names in BLOCKS.items():
            page.get_by_role('link', name=district, exact=True).click()
            page.get_by_text(re.compile(r'District\s*:\s*' + district, re.I)).first.wait_for()
            blocks[district] = read_counts(page, names)
            page.go_back(wait_until='domcontentloaded')
    payload = {'source': url, 'retrievedDate': datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat(),
               'districts': districts, 'blocks': blocks}
    validate(payload, ROOT)
    write_js(ROOT / 'shramik-s58-ongoing.js', 'window.SHRAMIK_S58', payload)
    print('S5.8 verified: 52 districts and 17 Janpads', flush=True)


if __name__ == '__main__':
    main()
