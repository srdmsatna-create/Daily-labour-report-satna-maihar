#!/usr/bin/env python3
"""Convert the latest official dynamic_work_details CSV into portal JS.

The official CSV contains work-level data but not Engineer/Cluster. Those fields are
joined from AUTO_REPORT rows by Janpad + Panchayat, with the previous ongoing JS as
an additional fallback.

MIS 6.12 after the VB-G RAM G migration can return zero/blank historic NREGA booked
values and does not carry the Apr-Jun split.  Preserve the live row list/status but
restore those historical NREGA values by Work Code from the reviewed 30-08 master.
"""
import csv, json, re, sys
from gp_sector_mapping import apply_sector_correction
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data'
CSV_PATH = DATA / 'Ongoing_Works_dynamic_work_details_latest.csv'
LEGACY_NREGA = DATA / 'Final_WorkCategory_30-08-2026.csv'
AUTO = ROOT / 'auto-data.js'
OUT = ROOT / 'ongoing-details.js'
ALLOWED_STATUS = {'NEW', 'APPROVED', 'ONGOING', 'SUSPENDED', 'COMPLETED', 'PHYSICALLY COMPLETED', 'DELETED'}


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

def classify_category(name, work_type, fy, previous=''):
    """Keep reviewed categories stable and classify newly appearing R6.12 works."""
    if clean(previous):
        return clean(previous)
    t = f'{clean(name)} {clean(work_type)}'.lower()
    rules = [
        (r'pmay|pradhan\s*mantri\s*awas', 'PMAY-G'),
        (r'iay\s*house|indira\s*awas', 'IAY Houses'),
        (r'amrit\s*sarovar', 'Amrit Sarovar'),
        (r'\bek\s+(?:maa?\s+)?(?:ki\s+)?bagiya\b|\bbagiya\b', 'Ek Bagiya'),
        (r'puliya|pulia|pulya|culvert|hume\s*pipe', 'Pulya'),
        (r'boundary|boundry|baund', 'Boundary Wall'),
        (r'\bpcc\b|\bcc\b|cement\s*concrete|\bnali\b|drain|grey\s*water|rural\s*connectivity', 'Cement Concrete'),
        (r'gravel|greval|grewal|graval|mur+am|murram|sudur|sudoor|\bbt\s*road', 'Gravel Road'),
        (r'farm\s*pond|khet\s*talab', 'Farm Pond'),
        (r'stop\s*dam|check\s*dam|percolation|water\s*harvesting|recharge\s*(?:pit|shaft)|roof\s*top|community\s*pond|pushkar', 'Water conservation & recharge'),
        (r'soak\s*pit|gabion|gully\s*plug|contour\s*(?:trench|bund)|loose\s*bould?er|medh\s*bandhan|new\s*talab', 'Watershed Related Works'),
        (r'dug\s*well\s*recharge|community\s*well|samuday.*koop', 'Dug Well Recharge'),
        (r'plantation|charagah|poshan\s*vatika|vasudha|vriksharopan|land\s*development', 'Gap Filling in Plantation'),
        (r'shanti\s*dham|mukti\s*dham|crematorium', 'Crematorium'),
        (r'panchayat\s*bhavan|community\s*(?:hall|bhawan)|samuday.*bhawan|mangal\s*bhawan', 'Panchayat and Community Hall'),
        (r'shauchalay|sanitary\s*complex|segregation|kachara|\bnadep\b|compost|toilet', 'SBM Works'),
        (r'play\s*ground|khel\s*maidan', 'Play Field'),
        (r'anganwadi|anganbadi|aganwadi', 'Anganwadi'),
        (r'kapil\s*dhara|kapildhara|open\s*dug\s*well', 'Kapildhara'),
        (r'cattle\s*shed|goat\s*shelter|poultry|pashu\s*shed', 'Poultry Cattle and Goat Shelter'),
        (r'micro\s*irrigation|irrigation\s*(?:open\s*)?well|irrigation\s*channel|field\s*channel', 'Irrigation infrastructure'),
    ]
    for pattern, category in rules:
        if re.search(pattern, t, re.I):
            return category
    return 'Other Works'

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

def load_legacy_nrega():
    """Reviewed NREGA snapshot used only for pre-migration booked/mandays cutoffs."""
    out = {}
    if not LEGACY_NREGA.exists():
        print('WARN legacy NREGA cutoff master missing:', LEGACY_NREGA)
        return out
    try:
        with LEGACY_NREGA.open('r', encoding='utf-8-sig', newline='') as f:
            rd = csv.DictReader(f)
            for r in rd:
                code = clean(r.get('Work Code'))
                if code:
                    out[code] = r
        print(f'Loaded legacy NREGA cutoff master: {len(out)} work codes')
    except Exception as e:
        print('WARN legacy NREGA cutoff master:', e)
    return out

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
    legacy = load_legacy_nrega()
    rows = []
    matched_legacy = restored_booked = restored_aprjun = 0
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
            hist = legacy.get(code, {})
            if hist:
                matched_legacy += 1

            live_wage = num(pick(r, 'Booked Since Inception Wages (Rs)', 'NREGA Booked Wages', 'Booked Wages'))
            live_material = num(pick(r, 'Booked Since Inception Material (Rs)', 'NREGA Booked Material', 'Booked Material'))
            hist_wage = num(hist.get('NREGA Booked Wages'))
            hist_material = num(hist.get('NREGA Booked Material'))
            # Never let the migration/reset make inception booked values lower than the reviewed NREGA history.
            wage = max(live_wage, hist_wage)
            material = max(live_material, hist_material)
            if (wage > live_wage) or (material > live_material):
                restored_booked += 1

            sanction = num(pick(r, 'Total Sanction (Rs)', 'NREGA Total Sanction', 'Total Sanction'))
            if not sanction:
                sanction = num(pick(r, 'Sanction Wages (Rs)')) + num(pick(r, 'Sanction Material (Rs)'))
            booked = wage + material
            if not booked:
                booked = max(num(pick(r, 'NREGA Total Booked', 'Total Booked')), num(hist.get('NREGA Total Booked')))

            total_mandays = num(pick(r, 'Total Mandays', 'FY Mandays Total (GP)'))
            current_fy_mandays = num(pick(r, 'Mandays Generated Current FY'))
            aprjun_live = num(pick(r, '01 Apr–30 Jun'))
            aprjun_hist = num(hist.get('01 Apr–30 Jun'))
            aprjun = aprjun_live if aprjun_live > 0 else aprjun_hist
            if aprjun > aprjun_live:
                restored_aprjun += 1
            july = num(pick(r, '01 Jul–Today'))
            if not july:
                # In current MIS 6.12 the Current FY column is the fresh post-migration period.
                july = current_fy_mandays
            if not july:
                july = num(hist.get('01 Jul–Today'))
            mandays_till_mar31 = max(0.0, total_mandays - current_fy_mandays)

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
                'type': clean(pick(r, 'Work Type', 'WORK TYPE as per new work creation Module', 'Original Work Category')),
                'finalCategory': classify_category(clean(pick(r, 'Work Name', 'Name of Work')), clean(pick(r, 'Work Type', 'WORK TYPE as per new work creation Module', 'Original Work Category')), clean(pick(r, 'Work Start Fin Year', 'Work FY', 'Financial Year')), old.get('finalCategory')),
                'sanction': sanction,
                'bookedWage': wage,
                'bookedMaterial': material,
                'booked': booked,
                'expPct': (booked * 100 / sanction) if sanction else 0.0,
                'mandays': total_mandays,
                'mandaysTillMar31': mandays_till_mar31,
                'currentFYMandays': current_fy_mandays,
                'nregaAprJunMandays': aprjun,
                'julyMandays': july,
                'recoveryDone': old.get('recoveryDone', old.get('recoveryDoneWork', '')),
                'recoveryWork': num(old.get('recoveryWork', 1 if old.get('recoveryDone', old.get('recoveryDoneWork', False)) else 0)),
                'recoveryAmount': num(old.get('recoveryAmount', old.get('recoveryAmountRs', 0))),
                'recoveryWorkCount': num(old.get('recoveryWorkCount', 0)),
            })
            # Keep the reviewed pre-migration MGNREGA expenditure unchanged for each work code.
            fixed_wage = num(old.get('nregaBookedWage', hist.get('NREGA Booked Wages')))
            fixed_material = num(old.get('nregaBookedMaterial', hist.get('NREGA Booked Material')))
            fixed_total = num(old.get('nregaBooked', fixed_wage + fixed_material))
            vb_wage = num(pick(r, 'Booked Current FY Wages (Rs)'))
            vb_material = num(pick(r, 'Booked Current FY Material (Rs)'))
            vb_total = vb_wage + vb_material
            overall = fixed_total + vb_total
            entry = rows[-1]
            entry.update({
                'nregaBookedWage': fixed_wage, 'nregaBookedMaterial': fixed_material,
                'nregaBooked': fixed_total, 'vbgBookedWage': vb_wage,
                'vbgBookedMaterial': vb_material, 'vbgBooked': vb_total,
                'overallBookedWage': fixed_wage + vb_wage,
                'overallBookedMaterial': fixed_material + vb_material,
                'overallBooked': overall, 'nregaExpPct': fixed_total * 100 / sanction if sanction else 0,
                'vbgExpPct': vb_total * 100 / sanction if sanction else 0,
                'overallExpPct': overall * 100 / sanction if sanction else 0,
                'bookedWage': vb_wage, 'bookedMaterial': vb_material,
                'booked': vb_total, 'expPct': overall * 100 / sanction if sanction else 0,
            })
    if not rows:
        raise SystemExit('Official ongoing CSV produced zero rows; refusing to overwrite previous data')
    for row in rows:
        apply_sector_correction(row)
    rows[0]['sourceDate'] = datetime.now(timezone.utc).date().isoformat()
    OUT.write_text('window.ONGOING_DETAILS=' + json.dumps(rows, ensure_ascii=False, separators=(',', ':')) + ';\n', encoding='utf-8')
    mapped = sum(1 for r in rows if r['engineer'])
    status_counts = {s: sum(1 for r in rows if norm(r['status']) == s) for s in sorted(ALLOWED_STATUS)}
    print(f'Updated MIS 6.12 work details: {len(rows)} works; engineer mapping {mapped}/{len(rows)}; status={status_counts}; legacy matched={matched_legacy}; booked restored={restored_booked}; Apr-Jun restored={restored_aprjun}; {datetime.now(timezone.utc).isoformat()}')

if __name__ == '__main__':
    main()
