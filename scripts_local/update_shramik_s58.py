"""Fetch FY 2026–27 S5.8 ongoing counts for 52 source districts and 17 Janpads."""
import json
import os
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from urllib.parse import urljoin, urlsplit

from official_report_tables import ReportTables

from update_shramik_state import norm, number, write_js
from update_mis_612_work_details import open_text
from vbgram_access import session_opener

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


def read_counts(source, names):
    document = ReportTables(source)
    title = document.text
    if not re.search(r"S5\.8.*ongoing works.*2026[-–]2027", title, re.I):
        raise ValueError("Official FY 2026–27 S5.8 heading not found")
    for rows in document.tables:
        header = next((cells for cells in rows if any(norm(c.text) == "TOTAL WORKS ONGOING" for c in cells)), None)
        if header is None:
            continue
        column = next(i for i, c in enumerate(header) if norm(c.text) == "TOTAL WORKS ONGOING")
        if not column:
            continue
        counts, links = {}, {}
        for cells in rows:
            if len(cells) <= column:
                continue
            name = norm(cells[column - 1].text)
            if name not in names:
                continue
            if name in counts:
                raise ValueError(f"Duplicate S5.8 row: {name}")
            counts[name] = number(cells[column].text)
            hrefs = cells[column - 1].links
            if len(hrefs) == 1:
                links[name] = hrefs[0]
        if counts.keys() == names:
            return counts, links
        if counts:
            raise ValueError(f"S5.8 coverage incomplete: {len(counts)}/{len(names)}; missing {', '.join(sorted(names - counts.keys()))}")
    raise ValueError("S5.8 Total Works Ongoing column missing or empty")


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
    url = os.environ.get('SHRAMIK_S58_URL') or URL
    page, effective_url = open_text(session_opener(), url, timeout=60)
    districts, links = read_counts(page, district_names(ROOT))

    def read_district(item):
        district, names = item
        if district not in links:
            raise ValueError(f"S5.8 district link missing: {district}")
        detail = urljoin(effective_url, links[district])
        if urlsplit(detail).hostname != urlsplit(effective_url).hostname:
            raise ValueError(f"Unexpected S5.8 district link host: {district}")
        source, _ = open_text(session_opener(), detail, timeout=60)
        title = ReportTables(source).text
        if not re.search(r"District\s*:\s*" + district + r"\b", title, re.I):
            raise ValueError(f"S5.8 returned the wrong district: {district}")
        counts, _ = read_counts(source, names)
        return district, counts

    with ThreadPoolExecutor(max_workers=2) as pool:
        blocks = dict(pool.map(read_district, BLOCKS.items()))
    payload = {'source': url, 'retrievedDate': datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat(),
               'districts': districts, 'blocks': blocks}
    validate(payload, ROOT)
    write_js(ROOT / 'shramik-s58-ongoing.js', 'window.SHRAMIK_S58', payload)
    print('S5.8 verified: 52 districts and 17 Janpads', flush=True)


if __name__ == '__main__':
    main()
