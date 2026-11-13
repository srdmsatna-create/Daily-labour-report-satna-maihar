"""Read official R5.1.1 FY persondays for Shramik Niyojan."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
import json
from pathlib import Path
import re
from urllib.parse import urljoin, urlsplit
from urllib.request import Request

from vbgram_access import HOST, open_url

ROOT = Path(__file__).resolve().parents[1]
SOURCE = 'https://vbgramgrep.dord.gov.in/VBGRAMG/citizen_html/demregister.aspx?payload=j6HEtKslSXGMDsXiy1KobglbOnhVX-Dd3nHPDm-OvbvmI-O6PGnkeZ0GkOaKWDdJvH8MGjiBk9UrleupzKK3dKpWiMbAmy_-po-ZWi9PSGS3aA7-WG3Q0croDJDOqkcdGM7fbln0aVc2ujCSjdaNBjCJ8f1YWn4MSu1IYodxWAmDPbPVFijOv87Cjt00GU_e'
FY = '2026-2027'
SATNA = {'AMARPATAN':75,'MAIHAR':115,'MAJHGAWAN':96,'NAGOD':94,'RAMNAGAR':55,
         'RAMPUR BAGHELAN':97,'SATNA':93,'UNCHAHARA':70}
REWA = {'GANGEV','HANUMANA','JAWA','MAUGANJ','NAIGARHI','RAIPUR KARCHULIYAN','REWA','SIRMOUR','TEONTHAR'}


class Grid(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows = []
        self.row = self.cell = None
        self.year_ok = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'form' and ('fin_year=' + FY) in a.get('action', ''):
            self.year_ok = True
        if tag == 'tr':
            self.row = []
        if tag in ('td', 'th') and self.row is not None:
            self.cell = ['', None, int(a.get('colspan', 1))]
        if tag == 'a' and self.cell is not None and 'demregister.aspx?' in a.get('href', ''):
            self.cell[1] = a['href']

    def handle_data(self, text):
        if self.cell is not None:
            self.cell[0] += text

    def handle_endtag(self, tag):
        if tag in ('td', 'th') and self.cell is not None and self.row is not None:
            self.cell[0] = ' '.join(self.cell[0].split())
            self.row.append(self.cell)
            self.cell = None
        if tag == 'tr' and self.row is not None:
            self.rows.append(self.row)
            self.row = None


def read(url, count):
    parts = urlsplit(url)
    if parts.scheme != 'https' or parts.hostname != HOST or not parts.path.lower().endswith('/demregister.aspx'):
        raise ValueError('Unexpected R5.1.1 link')
    with open_url(Request(url, headers={'User-Agent':'Mozilla/5.0'}), timeout=35) as response:
        source = response.read().decode('utf-8-sig')
    grid = Grid()
    grid.feed(source)
    if not grid.year_ok or 'R5.1.1 Employment Generated during the year' not in source:
        raise ValueError('R5.1.1 FY 2026-27 header missing')
    headers = [c[0].casefold() for row in grid.rows for c in row]
    if not any('persondays' in h.replace(' ', '') for h in headers):
        raise ValueError('Total Persondays header missing')
    width = 24
    # R5.1.1 labels Total Persondays as column 19. The second header row
    # omits the columns that span both header rows.
    col = 18
    rows, links, total = {}, {}, None
    for row in grid.rows:
        if len(row) != width:
            continue
        seq, name = row[0][0], row[1][0].upper()
        if name == 'TOTAL':
            total = int(row[col][0].replace(',', ''))
        elif seq.isdigit() and name and not name.isdigit():
            if name in rows:
                raise ValueError('Duplicate R5.1.1 row: '+name)
            rows[name] = int(row[col][0].replace(',', ''))
            if row[1][1]:
                links[name] = urljoin(url, row[1][1])
    if len(rows) != count or total != sum(rows.values()) or any(v < 0 for v in rows.values()):
        raise ValueError(f'R5.1.1 rows/total failed validation ({len(rows)}/{count})')
    return rows, links


def collect():
    districts, links = read(SOURCE, 52)
    with ThreadPoolExecutor(max_workers=8) as pool:
        sat_future = pool.submit(read, links['SATNA'], 8)
        rewa_future = pool.submit(read, links['REWA'], 9)
        satna, gp_links = sat_future.result()
        rewa, _ = rewa_future.result()
        if set(satna) != set(SATNA) or set(rewa) != REWA:
            raise ValueError('Unexpected R5.1.1 Janpad coverage')
        gps = dict(zip(SATNA, pool.map(lambda b: read(gp_links[b], SATNA[b])[0], SATNA)))
    if not sum(districts.values()):
        raise ValueError('Empty statewide Total Persondays')
    differences = {b:sum(gps[b].values())-satna[b] for b in satna if sum(gps[b].values()) != satna[b]}
    return {'fy':FY,'fetchedAt':datetime.now(timezone.utc).isoformat(),'source':SOURCE,
            'districts':districts,'rewa':rewa,'satna':satna,'gps':gps,'gpDifferences':differences}


def main():
    payload = collect()
    out = ROOT / 'shramik-r511-persondays.js'
    tmp = out.with_suffix('.tmp')
    tmp.write_text('window.SHRAMIK_R511='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    tmp.replace(out)
    print('R5.1.1 verified: 52 districts, 17 Janpads, 695 GPs',flush=True)


if __name__ == '__main__':
    main()
