#!/usr/bin/env python3
"""Convert the latest official dynamic_work_details CSV into portal JS.

The official CSV contains work-level data but not Engineer/Cluster. Those fields are
joined from AUTO_REPORT rows by Janpad + Panchayat, with the previous ongoing JS as
an additional fallback. This lets the work-level screen refresh automatically
without requiring a manual Daily Report.xlsx upload.
"""
import csv, json, re, sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
CSV_PATH = DATA / 'Ongoing_Works_dynamic_work_details_latest.csv'
AUTO = ROOT / 'auto-data.js'
OUT = ROOT / 'ongoing-details.js'
ALLOWED_STATUS = {'ONGOING', 'COMPLETED', 'PHYSICALLY COMPLETED'}


def clean(v):
    return '' if v is None else str(v).strip()

def num(v):
    try:
        return float(str(v).replace(',', '').strip() or 0)
    except Exception:
        return 0.0

def norm(v):
    return re.sub(r'\s+', ' ', clean(v)).strip().upper()

def norm_janpad(v):
    x = norm(v)
    return 'SATNA' if x == 'SOHAWAL' else x

def load_js_json(path, prefix):
    s = path.read_text(encoding='utf-8').strip()
    s = re.sub(r'^' + re.escape(prefix) + r'\s*=\s*', '', s).rstrip(';')
    return json.loads(s)

def build_mapping():
    mapping = {}
    if AUTO.exists():
        try:
            data = load_js_json(AUTO, 'window.AUTO_REPORT')
            for r in data.get('rows', []):
                j = norm_janpad(r.get('janpad'))
                gp = norm(r.get('panchayat'))
                if j and gp:
                    mapping[(j, gp)] = (clean(r.get('engineer')), clean(r.get('cluster')))
        except Exception as e:
            print('WARN auto-data mapping:', e)
    # Preserve old mapping where RepDay lacks a row.
    if OUT.exists():
        try:
            old = load_js_json(OUT, 'window.ONGOING_DETAILS')
            for r in old:
                key = (norm_janpad(r.get('janpad')), norm(r.get('panchayat')))
                mapping.setdefault(key, (clean(r.get('engineer')), clean(r.get('cluster'))))
        except Exception as e:
            print('WARN previous ongoing mapping:', e)
    return mapping

def load_previous():
    if not OUT.exists(): return {}
    try:
        return {clean(r.get('code')): r for r in load_js_json(OUT, 'window.ONGOING_DETAILS') if clean(r.get('code'))}
    except Exception as e:
        print('WARN previous work data:', e); return {}

def pick(r, *names):
    for name in names:
        if name in r and clean(r.get(name)):
            return r.get(name)
    return ''

def main():
    if not CSV_PATH.exists():
        raise SystemExit(f'Missing latest ongoing CSV: {CSV_PATH}')
    mp = build_mapping()
    previous = load_previous()
    rows = []
    with CSV_PATH.open('r', encoding='utf-8-sig', newline='') as f:
        rd = csv.DictReader(f)
        required = {'Work Code','Work Name','Work Status'}
        if not required.issubset(set(rd.fieldnames or [])):
            raise SystemExit('Official ongoing CSV missing expected headers')
        for i, r in enumerate(rd, 1):
            status = norm(pick(r, 'Work Status', 'Status'))
            if status not in ALLOWED_STATUS:
                continue
            j = norm_janpad(pick(r, 'Janpad / Block Name', 'Janpad', 'Block', 'Block Name'))
            gp = clean(pick(r, 'Panchayat Name', 'Panchayat', 'Gram Panchayat'))
            eng, clu = mp.get((j, norm(gp)), ('', ''))
            code = clean(pick(r, 'Work Code', 'Workcode'))
            old = previous.get(code, {})
            wage = num(pick(r, 'Booked Since Inception Wages (Rs)', 'NREGA Booked Wages', 'Booked Wages'))
            material = num(pick(r, 'Booked Since Inception Material (Rs)', 'NREGA Booked Material', 'Booked Material'))
            sanction = num(pick(r, 'Total Sanction (Rs)', 'NREGA Total Sanction', 'Total Sanction'))
            booked = wage + material or num(pick(r, 'NREGA Total Booked', 'Total Booked'))
            rows.append({
                'sno': len(rows)+1,
                'district': clean(pick(r, 'District Name', 'District')),
                'janpad': j,
                'engineer': eng,
                'cluster': clu,
                'panchayat': gp,
                'fy': clean(pick(r, 'Work Start Fin Year', 'Work FY', 'Financial Year')),
                'status': clean(pick(r, 'Work Status', 'Status')),
                'code': code,
                'name': clean(pick(r, 'Work Name', 'Name of Work')),
                'type': clean(pick(r, 'Work Type', 'Original Work Category')),
                'finalCategory': clean(old.get('finalCategory')) or clean(pick(r, 'Final Work Category')),
                'sanction': sanction,
                'bookedWage': wage,
                'bookedMaterial': material,
                'booked': booked,
                'expPct': (booked * 100 / sanction) if sanction else 0.0,
                'mandays': num(pick(r, 'Total Mandays', 'FY Mandays Total (GP)')),
                'currentFYMandays': num(pick(r, 'Mandays Generated Current FY', '01 Jul–Today')),
                'nregaAprJunMandays': num(pick(r, '01 Apr–30 Jun')),
                'julyMandays': num(pick(r, '01 Jul–Today')),
                'recoveryDone': old.get('recoveryDone', old.get('recoveryDoneWork', '')),
                'recoveryAmount': num(old.get('recoveryAmount', old.get('recoveryAmountRs', 0))),
                'recoveryWorkCount': num(old.get('recoveryWorkCount', 0)),
            })
    if not rows:
        raise SystemExit('Official ongoing CSV produced zero rows; refusing to overwrite previous data')
    payload = rows
    OUT.write_text('window.ONGOING_DETAILS=' + json.dumps(payload, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    mapped = sum(1 for r in rows if r['engineer'])
    status_counts = {s: sum(1 for r in rows if norm(r['status']) == s) for s in sorted(ALLOWED_STATUS)}
    print(f'Updated MIS 6.12 work details: {len(rows)} works; engineer mapping {mapped}/{len(rows)}; status={status_counts}; {datetime.now(timezone.utc).isoformat()}')

if __name__ == '__main__':
    main()
