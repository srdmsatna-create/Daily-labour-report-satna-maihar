"""Read public SECURE TS Register; publish only a complete, dated snapshot."""
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal
from html.parser import HTMLParser
import http.cookiejar
import json
import os

# Use Windows native certificate validation, including its issuer-chain lookup.
# Certificate and hostname verification remain enabled.
if os.name == 'nt':
    try:
        import truststore
    except ImportError as exc:
        raise RuntimeError(
            'SECURE on Windows requires truststore. Run: py -m pip install truststore'
        ) from exc
    truststore.inject_into_ssl()
from pathlib import Path
import threading
import time
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BASE = 'https://secure.dord.gov.in/reportv2/'
FY = '2026-2027'
START = date(2026, 9, 1)
IST = timezone(timedelta(hours=5, minutes=30))
EXPECTED = {'1712006': ('Amarpatan', 'Maihar', 75),
            '1712008': ('Maihar', 'Maihar', 115),
            '1712001': ('Majhgawan', 'Satna', 96),
            '1712003': ('Nagod', 'Satna', 94),
            '1712007': ('Ramnagar', 'Maihar', 55),
            '1712005': ('Rampur baghelan', 'Satna', 97),
            '1712002': ('Sohawal', 'Satna', 93),
            '1712004': ('Unchahara', 'Satna', 70)}


class Meta(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = {}

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'meta' and a.get('name') in ('_csrf', '_csrf_header'):
            self.values[a['name']] = a.get('content', '')


class Client:
    def __init__(self):
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar()))
        with self.opener.open(BASE + 'tsregister?mvsl=69', timeout=45) as r:
            parser = Meta()
            parser.feed(r.read().decode('utf-8'))
        self.headers = {parser.values['_csrf_header']: parser.values['_csrf'],
                        'Referer': BASE + 'tsregister?mvsl=69'}
        self.count_warnings = []

    def table(self, endpoint, expected_count=None, **extra):
        rows, total = [], None
        while total is None or len(rows) < total:
            params = dict(Scode='17', year=FY, draw=1, start=len(rows),
                          length=1000, searchkey='', **extra)
            request = urllib.request.Request(BASE + 'reports/' + endpoint,
                data=urllib.parse.urlencode(params).encode(), headers=self.headers)
            # Transient transport/server failures get two bounded retries.
            for attempt in range(3):
                try:
                    with self.opener.open(request, timeout=45) as response:
                        payload = json.load(response)
                    break
                except (OSError, ValueError):
                    if attempt == 2:
                        raise
                    time.sleep(attempt + 1)
            page = payload.get('data')
            count = int(payload['recordsFiltered'])
            if not isinstance(page, list) or count < 0:
                raise ValueError('Invalid SECURE response: ' + endpoint)
            if total is not None and count != total:
                raise ValueError('SECURE count changed during pagination; rerun required')
            total = count
            if not page and len(rows) < total:
                raise ValueError(f'Incomplete SECURE page: {endpoint} {extra}; got {len(rows)} of {total}')
            rows.extend(page)
            # SECURE's Maihar metadata says 121 while its full list contains
            # the independently known 115 GPs. Accept only the exact master
            # count, then verify identities and block aggregates below.
            if expected_count is not None and len(rows) == expected_count:
                if total < expected_count:
                    raise ValueError('SECURE metadata is smaller than the GP master')
                if total != expected_count:
                    self.count_warnings.append(dict(endpoint=endpoint, filters=extra,
                        reported=total, received=expected_count))
                break
            if len(rows) > total:
                raise ValueError('SECURE pagination exceeds reported count')
            if total == 0:
                break
        return rows


def approved_date(value):
    text = str(value or '').strip()
    for fmt in ('%Y-%m-%d', '%d-%m-%Y', '%d/%m/%Y'):
        try:
            return datetime.strptime(text, fmt).date()
        except ValueError:
            pass
    raise ValueError('Invalid TS approval date: ' + text)


def eligible(value, end):
    return START <= approved_date(value) <= min(end, date(2027, 3, 31))


def validate(d, today=None):
    today = today or datetime.now(IST).date()
    if d.get('schemaVersion') != 1 or d.get('fy') != FY or d.get('startDate') != START.isoformat():
        raise ValueError('Invalid SECURE date policy')
    if d.get('date') != today.isoformat() or d.get('endDate') != today.isoformat() or not d.get('success'):
        raise ValueError('Current complete SECURE snapshot required')
    gps, blocks, works = d['panchayats'], d['blocks'], d['works']
    if len(blocks) != 8 or {b['blockCode'] for b in blocks} != set(EXPECTED):
        raise ValueError('SECURE requires all 8 Janpads')
    if len(gps) != 695 or len({g['pcode'] for g in gps}) != 695:
        raise ValueError('SECURE requires 695 unique GP codes')
    if any(g['blockCode'] not in EXPECTED or not g['pcode'].startswith(g['blockCode']) for g in gps):
        raise ValueError('SECURE GP code does not belong to its Janpad')
    if len({w['code'] for w in works}) != len(works):
        raise ValueError('Duplicate SECURE work codes')
    for w in works:
        if not eligible(w['tsDate'], today) or w['blockCode'] not in EXPECTED:
            raise ValueError('SECURE work outside selected date/block scope')
        if w['code'].split('/')[0] != w['pcode'] or Decimal(str(w['amount'])) < 0:
            raise ValueError('Invalid SECURE work identity/amount')
    for b in blocks:
        members = [g for g in gps if g['blockCode'] == b['blockCode']]
        ww = [w for w in works if w['blockCode'] == b['blockCode']]
        if len(members) != EXPECTED[b['blockCode']][2] or b['tsCount'] != len(ww):
            raise ValueError('SECURE Janpad/GP count mismatch: ' + b['janpad'])
        if sum(g['tsCount'] for g in members) != b['tsCount']:
            raise ValueError('SECURE GP detail totals mismatch')
        if sum(Decimal(str(w['amount'])) for w in ww) != Decimal(str(b['tsAmount'])):
            raise ValueError('SECURE amount totals mismatch')
        if sum(g['sourceTotalWorks'] for g in members) != b['sourceTotalWorks']:
            raise ValueError('SECURE source work totals mismatch')
        if sum(g['sourceCurrentTS'] for g in members) != b['sourceCurrentTS']:
            raise ValueError('SECURE source TS totals mismatch')
    if d['totals']['tsCount'] != len(works) or sum(g['tsCount'] for g in gps) != len(works):
        raise ValueError('SECURE grand total mismatch')
    if sum(Decimal(str(w['amount'])) for w in works) != Decimal(str(d['totals']['tsAmount'])):
        raise ValueError('SECURE grand amount mismatch')
    for g in gps:
        ww = [w for w in works if w['pcode'] == g['pcode']]
        if g['tsCount'] != len(ww):
            raise ValueError('SECURE GP works mismatch')
        if any(w['blockCode'] != g['blockCode'] for w in ww):
            raise ValueError('SECURE GP/Janpad mapping mismatch')
    return True


def fetch(root=ROOT, workers=4):
    today = datetime.now(IST).date()
    if today < START or today > date(2027, 3, 31):
        raise ValueError('This TS policy is for FY 2026-27; update the policy before a new FY')
    client = Client()
    source_blocks = client.table('tsregisterbk', Dcode='1712')
    if len(source_blocks) != 8 or {str(b['bcode']) for b in source_blocks} != set(EXPECTED):
        raise ValueError('Unexpected SECURE Janpads')
    gp_rows = []
    for b in source_blocks:
        bc = str(b['bcode'])
        rows = client.table('tsregisterpt', expected_count=EXPECTED[bc][2], Bcode=bc)
        if len(rows) != EXPECTED[bc][2]:
            raise ValueError('Missing SECURE GPs: ' + str(b['bname']))
        for g in rows:
            gp_rows.append(dict(g, blockCode=bc))
        print('SECURE GP list: ' + str(b['bname']) + ' ' + str(len(rows)), flush=True)
    local = threading.local()

    def read_gp(g):
        # No current works and no current/previous TS means no eligible detail.
        # Inspect every GP with works, even if its summary TS count is zero.
        if not any(int(g.get(k) or 0) for k in ('totalnrega', 'current_tscount', 'prev_tscount')):
            return g, []
        if not hasattr(local, 'client'):
            local.client = Client()
        rows = local.client.table('tswork', Pcode=str(g['pcode']))
        if len(rows) < int(g.get('current_tscount') or 0) + int(g.get('prev_tscount') or 0):
            raise ValueError('TS work detail incomplete for ' + str(g['pcode']))
        return g, rows

    works, gps, seen = [], [], set()
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = [pool.submit(read_gp, g) for g in gp_rows]
        completed = 0
        for f in as_completed(futures):
            try:
                g, raw = f.result()
            except Exception as exc:
                for pending in futures:
                    pending.cancel()
                print('SECURE FAILED; previous snapshot retained: '+str(exc),flush=True)
                raise
            bc = g['blockCode']
            janpad, district, _ = EXPECTED[bc]
            selected = []
            for r in raw:
                code = str(r['wcode']).strip()
                if code.split('/')[0] != str(g['pcode']) or code in seen:
                    raise ValueError('Duplicate or wrongly mapped SECURE work: ' + code)
                seen.add(code)
                if eligible(r['tsdate'], today):
                    amount = Decimal(str(r['tsamt']))
                    if not amount.is_finite() or amount < 0:
                        raise ValueError('Invalid SECURE TS amount')
                    selected.append(dict(district=district, janpad=janpad, blockCode=bc,
                        pcode=str(g['pcode']), panchayat=g['pname'], code=code,
                        name=r['wname'], tsNo=str(r['tsno']),
                        tsDate=approved_date(r['tsdate']).isoformat(), amount=float(amount),
                        approvedBy=r.get('approvingauth', '')))
            works.extend(selected)
            gps.append(dict(district=district, janpad=janpad, blockCode=bc,
                pcode=str(g['pcode']), panchayat=g['pname'], tsCount=len(selected),
                tsAmount=float(sum((Decimal(str(w['amount'])) for w in selected), Decimal(0))),
                sourceTotalWorks=int(g['totalnrega'] or 0),
                sourceCurrentTS=int(g['current_tscount'] or 0), rawTSCount=len(raw)))
            completed += 1
            if raw or completed % 50 == 0 or completed == 695:
                print(f'SECURE [{completed}/695] {janpad}/{g["pname"]}: {len(selected)} eligible TS', flush=True)
    blocks = []
    for b in source_blocks:
        bc = str(b['bcode'])
        ww = [w for w in works if w['blockCode'] == bc]
        blocks.append(dict(janpad=EXPECTED[bc][0], district=EXPECTED[bc][1], blockCode=bc,
            tsCount=len(ww), tsAmount=float(sum((Decimal(str(w['amount'])) for w in ww), Decimal(0))),
            sourceTotalWorks=int(b['totalnrega'] or 0), sourceCurrentTS=int(b['current_tscount'] or 0)))
    payload = dict(schemaVersion=1, success=True, fy=FY, date=today.isoformat(),
        fetchedAt=datetime.now(IST).isoformat(), startDate=START.isoformat(), endDate=today.isoformat(),
        source=BASE+'tsregister?mvsl=69',
        sourceCountWarnings=client.count_warnings,
        basis='TS approved On, inclusive 01 October 2026 through snapshot date; selected FY 2026-2027',
        blocks=blocks, panchayats=sorted(gps, key=lambda x:(x['blockCode'], x['pcode'])),
        works=sorted(works, key=lambda x:(x['blockCode'],x['pcode'],x['code'])),
        totals=dict(tsCount=len(works),tsAmount=float(sum((Decimal(str(w['amount'])) for w in works),Decimal(0)))))
    validate(payload, today)
    target = Path(root)/'secure-ts-data.js'
    temp = target.with_suffix('.tmp')
    temp.write_text('window.SECURE_TS_DATA = '+json.dumps(payload, ensure_ascii=False)+';\n',encoding='utf-8')
    os.replace(temp, target)
    print('SECURE SUCCESS: 8 Janpads / 695 GPs; eligible TS = '+str(len(works)),flush=True)
    return payload


if __name__ == '__main__':
    p = argparse.ArgumentParser()
    p.add_argument('--workers', type=int, choices=range(1,5), default=4)
    args = p.parse_args()
    fetch(workers=args.workers)
