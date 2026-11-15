"""Refresh R6.17 district/GP totals and R6.22 BHUVAN work-code details."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlparse
from urllib.error import HTTPError
from urllib.request import Request
from time import sleep

from official_report_tables import ReportTables
from vbgram_access import session_opener

from update_secure_ts import EXPECTED, IST

ROOT = Path(__file__).resolve().parents[1]
URL = 'https://vbgramgrep.dord.gov.in/VBGRAMG/Secure_work.aspx?payload=YQL26U5Cur1To85X_ocjWXCXQLMXsSv9vpIIc7xmJMlIoHwNL91rGCgC1Ke_ie9b-a9DYoKRg3vO-kWZkWUovCx2e_SPYg05SZ3_4ClT8ZY9ygchbWsxx_1p4leHIFjeDMk-R8wcF5-xXfK_qpBS79z0CpYxeVZdsfjdnq1jLvbErn97JtjbZXfgI1-aMpU6RruDmtefzLka-9E1Um66bgotkl52pMOe9oSkJ4l5eo06wc8W3VcGWIDRY-lqu8OV'
OUTPUT = ROOT / 'data/r617-secure-bhuvan.json'
BLOCK_COUNTS = {name.upper(): count for name, _, count in EXPECTED.values()}
BLOCK_COUNTS['SATNA'] = BLOCK_COUNTS.pop('SOHAWAL')
FIELDS = ('sentSecure', 'consumedSecure', 'sentBhuvan', 'receivedBhuvan')
WORK = re.compile(r'\((\d{10}/[A-Z0-9/]+/\d+)\)\s*$', re.I)


def read(url):
    if urlparse(url).hostname != urlparse(URL).hostname:
        raise ValueError('Unexpected R6.17 link host')
    for attempt in range(3):
        try:
            request = Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with session_opener().open(request, timeout=40) as response:
                return ReportTables(response.read().decode("utf-8-sig", errors="replace"))
        except OSError as error:
            if isinstance(error, HTTPError) and error.code not in (408, 429, 500, 502, 503, 504):
                raise
            if attempt == 2:
                raise
            sleep(attempt + 1)


def text(cell):
    return cell.text


def table_rows(doc, header):
    for rows in doc.tables:
        if rows and any(header in text(cell) for cell in rows[0]):
            return rows[1:]
    raise ValueError('Missing government table for ' + header)


def counts(cells):
    return {key: int(text(cell).replace(',', '')) for key, cell in zip(FIELDS, cells[2:], strict=True)}


def linked(cell):
    links = cell.links
    if len(links) != 1:
        raise ValueError('Missing government drill-down link')
    return urljoin(URL, links[0])


def verify_sum(parent, children):
    if any(parent[key] != sum(row[key] for row in children) for key in FIELDS):
        raise ValueError('R6.17 GP and Janpad totals do not reconcile for ' + parent.get('janpad', 'district'))


def read_block(task):
    block, url = task
    gps, tasks = [], []
    for cells in table_rows(read(url), 'Panchayats'):
        if len(cells) != 6 or not text(cells[0]).isdigit() or text(cells[1]).isdigit():
            continue
        gp = {'janpad': block['janpad'], 'gp': text(cells[1]), **counts(cells)}
        gps.append(gp)
        for index in (2, 3):
            field = FIELDS[index - 2]
            if gp[field]:
                gp[field + 'Link'] = linked(cells[index])
        for index in (4, 5):
            field = FIELDS[index - 2]
            if gp[field]:
                tasks.append((gp, field, linked(cells[index])))
    if not 0 < len(gps) <= BLOCK_COUNTS[block['janpad']] or len({gp['gp'] for gp in gps}) != len(gps):
        raise ValueError('Incomplete R6.17 GP coverage for ' + block['janpad'])
    verify_sum(block, gps)
    return gps, tasks


def read_works(task):
    gp, field, url = task
    works = {}
    for cells in table_rows(read(url), 'Work Name(Work Code)'):
        if len(cells) != 4 or text(cells[1]) != gp['gp']:
            continue
        title = text(cells[2])
        match = WORK.search(title)
        if not match:
            raise ValueError('Unexpected R6.22 work status for ' + gp['gp'])
        code = match[1].upper()
        if code in works:
            raise ValueError('Duplicate R6.22 work code ' + code)
        works[code] = {'name': title[:match.start()].strip(), 'status': text(cells[3])}
    if len(works) != gp[field]:
        raise ValueError(f'R6.22 count mismatch for {gp["janpad"]}/{gp["gp"]}/{field}')
    return gp, field, works


def fetch(output=OUTPUT):
    doc = read(URL)
    report_date = re.search(r'Report last Updated on:\s*(\d{1,2}/\d{1,2}/\d{4})', text(doc))
    if not report_date:
        raise ValueError('R6.17 report date unavailable')
    jobs, total = [], None
    for cells in table_rows(doc, 'Blocks'):
        if len(cells) != 6:
            continue
        name = text(cells[1])
        if name == 'Total':
            total = counts(cells)
        if name in BLOCK_COUNTS:
            jobs.append(({'janpad': name, **counts(cells)}, linked(cells[1])))
    blocks = [block for block, _ in jobs]
    if len(blocks) != len(BLOCK_COUNTS) or {b['janpad'] for b in blocks} != set(BLOCK_COUNTS) or total is None:
        raise ValueError('Incomplete R6.17 Janpad coverage')
    verify_sum(total, blocks)
    with ThreadPoolExecutor(max_workers=8) as pool:
        results = list(pool.map(read_block, jobs))
    print(f'R6.17: {len(blocks)} Janpads and {sum(len(gps) for gps, _ in results)} GPs matched', flush=True)
    work_tasks = [task for _, tasks in results for task in tasks]
    with ThreadPoolExecutor(max_workers=12) as pool:
        for index, (gp, field, works) in enumerate(pool.map(read_works, work_tasks), 1):
            gp[field + 'Works'] = works
            if index % 25 == 0:
                print(f'R6.22: {index}/{len(work_tasks)} detail pages verified', flush=True)
    gps = [gp for rows, _ in results for gp in rows]
    for gp in gps:
        if not set(gp.get('receivedBhuvanWorks', {})) <= set(gp.get('sentBhuvanWorks', {})):
            raise ValueError('R6.22 received work not in sent list: ' + gp['gp'])
    for field in ('sentBhuvan', 'receivedBhuvan'):
        if len({code for gp in gps for code in gp.get(field + 'Works', {})}) != total[field]:
            raise ValueError('R6.22 work codes are not unique across GPs')
    payload = {'officialDate': report_date[1], 'retrievedAt': datetime.now(IST).isoformat(),
               'source': URL, 'blocks': blocks, 'gps': gps, 'totals': total}
    tmp = output.with_suffix('.tmp')
    tmp.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':'))+'\n', encoding='utf-8')
    tmp.replace(output)
    print(f'R6.22: {total["sentBhuvan"]} sent and {total["receivedBhuvan"]} received work codes verified', flush=True)


if __name__ == '__main__':
    fetch()
