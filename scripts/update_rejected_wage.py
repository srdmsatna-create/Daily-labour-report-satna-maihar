#!/usr/bin/env python3
"""Refresh R8.1.5 summary, preserving the verified 22 Sep baseline.

Fails closed when official page layout changes. Does not overwrite a verified snapshot.
"""
import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'data/rejected-wage-latest.json'
SAVED_SOURCE = ROOT / 'vc-rejected-wage-janpad.json'
SOURCE = os.environ.get('REJECTED_WAGE_SOURCE_URL', '').strip() or (json.loads(SAVED_SOURCE.read_text()).get('sourceUrl', '') if SAVED_SOURCE.exists() else '') or 'https://vbgramgrep.dord.gov.in/VBGRAMG/rej_trans_track.aspx?lflag=eng&page=d&state_name=MADHYA+PRADESH&state_code=17&district_name=SATNA&district_code=1712&fin_year=2026-2027&source=national&rdbutton=0&Digest=bxHEcyU8JyvdJ3rs8H7x9g'
JANPADS = {'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}
DIST = {'AMARPATAN':'MAIHAR','MAIHAR':'MAIHAR','RAMNAGAR':'MAIHAR'}

def number(value):
    raw = re.sub(r'[^0-9.-]', '', value or '')
    return int(float(raw)) if raw and raw not in ('-', '.') else 0

def key(value):
    return re.sub(r'\s+', ' ', value.upper().strip()).replace('RAMPOR BAGHELAN','RAMPUR BAGHELAN').replace('SOHAWAL','SATNA')

def parse(tables):
    for table in tables:
        rows = [[re.sub(r'\s+', ' ', cell).strip() for cell in row] for row in table]
        matches = []
        for row in rows:
            where = next((i for i, val in enumerate(row) if key(val) in JANPADS), None)
            if where is None or len(row) < where + 6: continue
            matches.append((where, row))
        if len({key(row[i]) for i,row in matches}) != 8: continue
        result = []
        for i,row in matches:
            # Official R8.1.5 district table: Janpad, rejected count/amount,
            # pending regeneration count/amount, success count/amount, bank pending count/amount.
            vals = [number(x) for x in row[i+1:i+9]]
            if len(vals) < 8: raise ValueError('Incomplete summary columns')
            janpad = key(row[i]);total,total_amount,pending,pending_amount,success,success_amount,bank_pending,bank_amount=vals
            if min(vals)<0 or pending>total or pending_amount>total_amount or total != pending+success+bank_pending or total_amount != pending_amount+success_amount+bank_amount:
                raise ValueError('Invalid official summary amounts')
            result.append(dict(fy='2026-27',janpad=janpad,district=DIST.get(janpad,'SATNA'),total=total,totalAmount=total_amount,pending=pending,pendingAmount=pending_amount,muster=None,fto=None,success=success,successAmount=success_amount,bankPending=bank_pending,bankPendingAmount=bank_amount,reasons={}))
        if len(result)==8 and len({r['janpad'] for r in result})==8:
            return sorted(result,key=lambda r:r['janpad'])
    raise ValueError('Official R8.1.5 table with eight Janpads was not found; existing data preserved')


SOURCES = [["2026-27","VBGRAMG","https://vbgramgrep.dord.gov.in/VBGRAMG/rej_trans_track.aspx?payload=0vSCJ0SdjbPqw_1Z7gcp4nH6psnabeedYbef_CD0kyf_nn9KS5f5BgQDfj2Ee2usR_XX0oRf5V3Aq-Hpm6UMIH9sQGFc6QFcQL7qjEhxH6GXu6Dl2JlhNKKACsCbaO2K0UXk0b_Ax9iwgo6XUiv8F9eaCymKxNJFPZOaSk2PR9F7EDuprC5ztoiELHkw_l2sQvhqoTNCDSpAbeUfIEQswnXp6nQ-o-sdLnlqkPM0naNKA1Jdbxy__HFwcn4-8Iym"],["2026-27","MGNREGA","https://mnregaweb4.dord.gov.in/netnrega/rej_trans_track.aspx?payload=lYKfJ2he503a2YjN-5H7rx8HSsNRo1hermf0qeU_UlB-axSLVwnJu6NiuDrXgPJztMbSfR9MsUWQpNTCeEazgNJTD8aQSNQlSVdbKgsSHUvEGaBqGfG31BUlgofOA-LQ6_735w3aB-rWGqfvlqbvW1EaNRz819i2krnKW9tb6xCA-lw7Xt6Ayd3P6a5DaPfg8aT-ZH9Xw5i0ATpwg1VE2BEaI8n2EayBeDyJPNUlzEbT0lHAbj3AyjToqfssgKfU"],["2025-26","MGNREGA","https://mnregaweb4.dord.gov.in/netnrega/rej_trans_track.aspx?payload=8ukSMQaHDuIVpJc6HGStTTblGhC8E-Cg_Nc6rldRs3DHAvej-I21X43qjtm51qYCeUaDJREBCRutj0cc5SB8E6RTKGhQQ_a7yi5QMWpya3eCi8OqhsvpL8RJ-PGipOYIPqhS7oRK9oKBAa8ciS2Rg-63GZxu0R6ZZR7CcNA2mC9qiwZhaev1EGiHyu9BUQPJJwzVOEy0ZcaZK2thNn70SDZ_VPCOvhKtDn_tn1DThKW3kVqrmEnIlmXC5BX7NNZw"],["2024-25","MGNREGA","https://mnregaweb4.dord.gov.in/netnrega/rej_trans_track.aspx?payload=vE_M27MKxEOIApk_444sLsNWE1c0ggCEHDgIq-5K5sDRw7MqXQhElBuOPezf42iAKicGFHY-Blt4hGdxb3o3zXJ6dKFypKhciPMIPoB-2YchFLO4yLKdJlo-MjYn0Lb4cmVTwXlIQay3spiTTUxO_kE39B3Up68Cor6SQXBJOOX6aGpaDPNxg7Sn0X8nHC2pi842k4hDJWF-PW1HQ_vD2JJSHZh_yZttREUz2Z_v0tt6hL5HtPz2j67E_CP928g0"]]
FIELDS = ('total','totalAmount','pending','pendingAmount','success','successAmount','bankPending','bankPendingAmount')

def combine(snapshots):
    result = []
    for fy in ('2024-25','2025-26','2026-27'):
        groups = [s for s in snapshots if s['fy'] == fy]
        expected = 2 if fy == '2026-27' else 1
        if len(groups) != expected:
            raise ValueError('Missing source for ' + fy)
        for janpad in sorted(JANPADS):
            parts = [next(r for r in s['rows'] if r['janpad'] == janpad) for s in groups]
            row = dict(parts[0])
            row.update({k: sum(r[k] for r in parts) for k in FIELDS})
            row.update(fy=fy,scheme='MGNREGA + VBGRAMG' if fy == '2026-27' else 'MGNREGA',muster=None,fto=None,reasons={})
            result.append(row)
    return result

async def main():
    from playwright.async_api import async_playwright
    snapshots = []
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        try:
            page = await browser.new_page()
            for fy, scheme, url in SOURCES:
                response = await page.goto(url, wait_until='domcontentloaded', timeout=90000)
                print(f'{scheme} FY {fy}: HTTP {response.status if response else "none"}', flush=True)
                if not response or response.status >= 400:
                    raise RuntimeError(f'{scheme} {fy} unavailable; previous published data retained')
                await page.wait_for_timeout(2500)
                tables = await page.locator('table').evaluate_all('(tables) => tables.map(t => [...t.rows].map(r => [...r.cells].map(c => c.innerText)))')
                rows = parse(tables)
                for row in rows: row['fy'] = fy
                snapshots.append(dict(fy=fy,scheme=scheme,url=url,rows=rows))
                print(f'Validated {scheme} {fy}: 8 Janpads', flush=True)
        finally:
            await browser.close()
    rows = combine(snapshots)
    now = datetime.now(ZoneInfo('Asia/Kolkata'))
    today = now.date().isoformat()
    old = json.loads(DEST.read_text(encoding='utf-8')) if DEST.exists() else None
    prior = ({'date':old['date'],'rows':old['rows']} if old and old.get('combined') and old.get('date') != today else old.get('previous') if old and old.get('combined') else None)
    DEST.parent.mkdir(exist_ok=True)
    tmp = DEST.with_suffix('.tmp')
    tmp.write_text(json.dumps({'date':today,'fetchedAt':now.isoformat(timespec='seconds'),'combined':True,'sources':snapshots,'rows':rows,'previous':prior},ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    tmp.replace(DEST)
    print('SUCCESS: 24 Janpad/FY rows; FY 2026-27 = MGNREGA + VBGRAMG. All four sources validated.',flush=True)

if __name__ == '__main__': asyncio.run(main())
