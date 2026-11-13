"""Refresh FY-wide SECURE register counts for the R-3.7 dashboard."""
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import json
from pathlib import Path

from update_secure_ts import Client, EXPECTED, FY, IST

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / 'data' / 'r37-secure-register.json'


def collect_register(kind):
    client = Client()
    column = f'current_{kind}count'
    blocks = client.table(f'{kind}registerbk', Dcode='1712')
    expected = {str(b['bcode']): int(b[column]) for b in blocks}
    if set(expected) != set(EXPECTED):
        raise ValueError(f'Incomplete {kind.upper()} block register')
    gps = {}
    for block, (_, _, size) in EXPECTED.items():
        rows = client.table(f'{kind}registerpt', expected_count=size, Bcode=block)
        counts = {}
        for row in rows:
            code = str(row['pcode'])
            count = int(row[column] or 0)
            if not code.startswith(block) or code in counts or count < 0:
                raise ValueError(f'Invalid {kind.upper()} GP register: {code}')
            counts[code] = {'gp': row['pname'], 'count': count}
        if len(counts) != size or sum(r['count'] for r in counts.values()) != expected[block]:
            raise ValueError(f'{kind.upper()} GP totals differ from block {block}')
        gps.update(counts)
    return gps


def collect():
    with ThreadPoolExecutor(max_workers=2) as pool:
        ts, admin = pool.map(collect_register, ('ts', 'as'))
    if ts.keys() != admin.keys():
        raise ValueError('SECURE TS and AS GP coverage differs')
    return {
        'fy': FY,
        'updatedAt': datetime.now(IST).isoformat(),
        'gps': [{
            'code': code, 'gp': row['gp'], 'ts': row['count'], 'as': admin[code]['count'],
        } for code, row in sorted(ts.items())],
    }


if __name__ == '__main__':
    data = collect()
    tmp = OUTPUT.with_suffix('.tmp')
    tmp.write_text(json.dumps(data, ensure_ascii=False, separators=(',', ':')) + '\n', encoding='utf-8')
    tmp.replace(OUTPUT)
    print(f"SECURE R-3.7: {len(data['gps'])} GPs verified", flush=True)
