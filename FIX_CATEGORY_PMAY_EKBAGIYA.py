from pathlib import Path
import json

p = Path('ongoing-details.js')
raw = p.read_text(encoding='utf-8-sig').strip()
prefix = 'window.ONGOING_DETAILS='
if not raw.startswith(prefix):
    raise SystemExit('ERROR: ongoing-details.js format not recognized')
body = raw[len(prefix):]
if body.endswith(';'):
    body = body[:-1]
rows = json.loads(body)

FY_EK = {'2025-2026','2026-2027'}
changed_iay = 0
changed_ek = 0

for r in rows:
    cat = str(r.get('finalCategory','')).strip()
    fy = str(r.get('fy','')).strip()
    # IAY and PMAY are one dashboard category.
    if cat == 'IAY Houses':
        r['finalCategory'] = 'PMAY-G'
        changed_iay += 1
        cat = 'PMAY-G'
    # User-approved rule: Gap Filling works of FY 2025-26 and 2026-27 belong to Ek Bagiya.
    if cat == 'Gap Filling in Plantation' and fy in FY_EK:
        r['finalCategory'] = 'Ek Bagiya'
        changed_ek += 1

# Validate unique Work Codes after normalization.
ek_codes = {str(r.get('code','')).strip() for r in rows if str(r.get('finalCategory','')).strip() == 'Ek Bagiya' and str(r.get('code','')).strip()}
if len(ek_codes) != 756:
    raise SystemExit(f'ERROR: Ek Bagiya validation failed. Expected 756 unique works, found {len(ek_codes)}. File NOT changed.')

# IAY must no longer remain as a separate final category.
remaining_iay = sum(1 for r in rows if str(r.get('finalCategory','')).strip() == 'IAY Houses')
if remaining_iay:
    raise SystemExit(f'ERROR: IAY Houses still remains in {remaining_iay} rows. File NOT changed.')

out = prefix + json.dumps(rows, ensure_ascii=False, separators=(',',':')) + ';\n'
p.write_text(out, encoding='utf-8')
print('DONE: Category normalization applied safely')
print(f'IAY Houses -> PMAY-G rows: {changed_iay}')
print(f'Gap Filling FY 2025-26/2026-27 -> Ek Bagiya rows: {changed_ek}')
print(f'Ek Bagiya unique Work Codes: {len(ek_codes)}')
