"""Transcribe the supplied 22/23 September VC source reports without inventing Janpad data."""
import json
import re
from pathlib import Path

from pptx import Presentation
import subprocess

UPLOAD = Path('../upload')
OUT = Path('vc-alert-data.json')
sources = {
    'yuktGp': ('Yuktdhara GP 23092026.pdf', 2),
    'yuktWorks': ('Yuktdhara Works 23092026.pdf', 3),
    'persondays': ('PD wrt last year 23092026.pdf', 2),
    'nmms': ('NMMS Usages 23092026.pdf', 3),
    'fto': ('Wage FTOs pending in VBGRAMGSoft 23092026.pdf', 2),
}
data = {}
for key, (filename, count) in sources.items():
    raw = subprocess.check_output(['pdftotext', '-layout', str(UPLOAD / filename), '-'], text=True)
    rows = {}
    for line in raw.splitlines():
        match = re.match(r'^\s*\d{1,2}\s+([A-Z][A-Z -]+?)\s{2,}(.+?)\s*$', line)
        if not match:
            continue
        district = match.group(1).strip()
        parts = match.group(2).split()
        if len(parts) != count + (1 if key in ('yuktGp', 'yuktWorks', 'persondays', 'nmms') else 0):
            # Percent is kept as a source value, but all numeric measures are taken independently.
            continue
        numbers = [p for p in parts if re.fullmatch(r'-?\d+(?:\.\d+)?', p)]
        if len(numbers) != count:
            continue
        if not all(re.fullmatch(r'-?\d+(?:\.\d+)?', v) for v in numbers):
            continue
        rows[district] = [float(v) if '.' in v else int(v) for v in numbers]
    if len(rows) != 52:
        raise ValueError(f'{key}: expected 52 district rows, found {len(rows)}')
    data[key] = rows

gaushala = {}
for slide in Presentation(UPLOAD / 'Gaushala.pptx').slides:
    for shape in slide.shapes:
        if not shape.has_table:
            continue
        for row in shape.table.rows:
            cells = [c.text.strip() for c in row.cells]
            if re.fullmatch(r'\d+', cells[0]) and len(cells) >= 7:
                gaushala[cells[1]] = [int(x) for x in cells[2:7]]
if len(gaushala) != 52:
    raise ValueError(f'gaushala: {len(gaushala)} district rows')
data['gaushala'] = gaushala

geotag = {}
for slide in Presentation(UPLOAD / 'GeoTag.pptx').slides:
    for shape in slide.shapes:
        if not shape.has_table:
            continue
        for row in shape.table.rows:
            cells = [c.text.strip() for c in row.cells]
            if re.fullmatch(r'\d+', cells[0]) and len(cells) >= 7:
                geotag[cells[1]] = [int(cells[i].replace(',', '')) for i in (2,3,5,6)]
if len(geotag) != 52:
    raise ValueError(f'geotag: {len(geotag)} district rows')
data['geotag'] = geotag

names = sorted(data['yuktGp'])
for key, rows in data.items():
    if set(rows) != set(names):
        raise ValueError(f'{key}: mismatch {set(rows)^set(names)}')

output = {
    'sourceDate': '23/09/2026', 'geotagDate':'22/09/2026',
    'scope': '52 source districts; SATNA includes MAIHAR in these state-level reports',
    'sources': {**{k: v[0] for k,v in sources.items()}, 'gaushala':'Gaushala.pptx', 'geotag':'GeoTag.pptx', 'janpadYukt':'yuktdhara-official-data.js (R33.1, 23/09/2026)'},
    'districts': {name:{key:rows[name] for key,rows in data.items()} for name in names},
}
official_js = Path('yuktdhara-official-data.js').read_text(encoding='utf-8')
official = json.loads(official_js[official_js.index('{'):].rstrip(';\n'))
if official['officialDate'] != output['sourceDate']:
    raise ValueError('Janpad and district Yuktdhara data have different dates')
janpads = {}
for row in official['rows']:
    name = 'SOHAWAL' if row['block'] == 'SATNA' else row['block']
    janpads[name] = {k:row[k] for k in ('gp','gpReceived','worksReceived','worksCreated')}
if len(janpads) != 8 or sum(v['gp'] for v in janpads.values()) != 695 or sum(v['gpReceived'] for v in janpads.values()) != data['yuktGp']['SATNA'][1] or sum(v['worksReceived'] for v in janpads.values()) != data['yuktWorks']['SATNA'][0]:
    raise ValueError('Janpad Yuktdhara totals do not match 52-district source reports')
output['janpads'] = janpads
OUT.write_text(json.dumps(output, ensure_ascii=False, separators=(',',':'))+'\n', encoding='utf-8')
print('Wrote', OUT, 'with', len(names), 'districts and', len(data), 'report types')
