"""Build PMAY-G columns from verified R6.9 and R6.12 report data."""
import csv
import gzip
import json
from collections import Counter
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
PMAY = 'Constr of PMAY-G House for Individuals'


def js_data(path):
    return json.loads(path.read_text(encoding='utf-8-sig').split('=', 1)[1].strip().rstrip(';'))


def main():
    root = ROOT
    gp = js_data(root / 'gp-emuster-data.js')
    status = json.loads((root / 'data/mis-6.12-status.json').read_text(encoding='utf-8-sig'))
    previous_path = root / 'pmay-janpad-summary-data.js'
    previous = js_data(previous_path)
    janpads = set(previous['rows'])
    if len(janpads) != 8 or not gp['gpProgressVerified']:
        raise ValueError('8 Janpads and verified R6.9 work detail required')

    ongoing = Counter()
    pmay_codes = set()
    with (root / 'data/Ongoing_Works_dynamic_work_details_latest.csv').open(encoding='utf-8-sig', newline='') as source:
        for row in csv.DictReader(source):
            if row['Work Status'].strip() != 'Ongoing' or row['Work Type'].strip() != PMAY:
                continue
            code = row['Work Code'].strip()
            if not code or code in pmay_codes:
                raise ValueError('Missing or duplicate R6.12 PMAY work code')
            pmay_codes.add(code)
            ongoing[row['Janpad / Block Name'].strip().upper()] += 1
    if set(ongoing) != janpads:
        raise ValueError('Incomplete R6.12 PMAY ongoing coverage')

    works = Counter()
    mr_codes = set()
    for row in gp['works']:
        if row['type'].strip() != PMAY:
            continue
        code = row['code'].strip()
        if not code or code in mr_codes or row['janpad'] not in janpads:
            raise ValueError('Invalid R6.9 PMAY work code or Janpad')
        mr_codes.add(code)
        works[row['janpad']] += 1

    labour_date = previous['labourDate']
    labour = {name: row['pmayLabour'] for name, row in previous['rows'].items()}
    fetch_status = json.loads((root / 'data/fetch-status.json').read_text(encoding='utf-8-sig'))
    fresh_labour_date = fetch_status.get('pmayLabourDate')
    if fresh_labour_date:
        with (root / 'data/official-summary.csv').open(encoding='utf-8-sig', newline='') as source:
            labour = {row['janpad']: int(row['pmayLabour']) for row in csv.DictReader(source)}
        if set(labour) != janpads:
            raise ValueError('Incomplete R6.9 PMAY labour coverage')
        labour_date = fresh_labour_date

    recovery = Counter()
    with gzip.open(root / 'ongoing-details.json.gz', 'rt', encoding='utf-8') as source:
        recovery_codes = {
            (row['janpad'], row['code']) for row in json.load(source)
            if float(row.get('recoveryWork') or 0) > 0 and row['janpad'] in janpads
        }
    for name, _ in recovery_codes:
        recovery[name] += 1

    payload = {
        'labourDate': labour_date,
        'mrDate': gp['sourceLastUpdated'],
        'ongoingDate': datetime.fromisoformat(status['updatedAt']).astimezone(ZoneInfo('Asia/Kolkata')).strftime('%d-%m-%Y'),
        'rows': {name: {'pmayLabour': labour[name], 'pmayMR': works[name], 'pmayOngoing': ongoing[name],
                        'recoveryWorks': recovery[name]}
                 for name in sorted(janpads)},
    }
    tmp = previous_path.with_suffix('.tmp')
    tmp.write_text('window.SRDM_PMAY_JANPAD=' + json.dumps(payload, ensure_ascii=False) + ';\n', encoding='utf-8')
    tmp.replace(previous_path)
    print(f'PMAY-G: Labour {sum(labour.values())}, Works with MR {sum(works.values())}, Ongoing {sum(ongoing.values())}')


if __name__ == '__main__':
    main()
