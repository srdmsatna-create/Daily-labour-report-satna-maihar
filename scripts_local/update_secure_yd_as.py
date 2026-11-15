"""Read the approved SECURE AS register for the Yuktdhara report."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path
import threading

from update_r37_secure_register import collect_register
from update_secure_ts import Client, EXPECTED, FY, FY_START, IST, approved_date

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data/secure-as-yuktdhara.json'


def validate(payload):
    today = datetime.now(IST).date()
    if (payload['fy'] != FY or payload['startDate'] != FY_START.isoformat()
            or datetime.fromisoformat(payload['snapshotAt']).astimezone(IST).date() != today
            or payload['gpCount'] != sum(size for _, _, size in EXPECTED.values())):
        raise ValueError('Current SECURE AS coverage of all 695 GPs required')
    codes = set()
    for row in payload['works']:
        code = row['workCode']
        if (code in codes or '/YD/' not in code or code[:7] not in EXPECTED
                or not FY_START <= approved_date(row['asDate']) <= today):
            raise ValueError('Invalid or duplicate SECURE AS work: ' + code)
        codes.add(code)


def fetch(output=OUTPUT):
    gps = collect_register('as')
    today = datetime.now(IST).date()
    local = threading.local()

    def work_rows(item):
        gp, summary = item
        if not summary['count']:
            return []
        if not hasattr(local, 'client'):
            local.client = Client()
        works = local.client.table('aswork', Pcode=gp)
        if len(works) < summary['count']:
            raise ValueError('Incomplete SECURE AS work detail for ' + gp)
        verified = []
        for row in works:
            code = str(row['wcode']).strip().upper()
            if '/YD/' not in code:
                continue
            if code.split('/')[0] != gp:
                raise ValueError('SECURE AS work belongs to a different GP: ' + code)
            approved = approved_date(row['asdate'])
            if approved is not None and FY_START <= approved <= today:
                verified.append({'workCode': code, 'asDate': approved.isoformat()})
        return verified

    with ThreadPoolExecutor(max_workers=16) as pool:
        works = [work for batch in pool.map(work_rows, gps.items()) for work in batch]
    payload = {'fy': FY, 'startDate': FY_START.isoformat(),
               'snapshotAt': datetime.now(IST).isoformat(), 'gpCount': len(gps),
               'source': 'https://secure.dord.gov.in/reportv2/asregister?mvsl=69',
               'works': sorted(works, key=lambda row: row['workCode'])}
    validate(payload)
    tmp = output.with_suffix('.tmp')
    tmp.write_text(json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    tmp.replace(output)
    print(f'SECURE AS: {len(works)} /YD/ works verified for {len(gps)} GPs', flush=True)


if __name__ == '__main__':
    fetch()
