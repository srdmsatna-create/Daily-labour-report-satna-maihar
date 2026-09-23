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
SOURCE = os.environ.get('REJECTED_WAGE_SOURCE_URL', '').strip() or 'https://vbgramgrep.dord.gov.in/VBGRAMG/rej_trans_track.aspx?lflag=eng&page=d&state_name=MADHYA+PRADESH&state_code=17&district_name=SATNA&district_code=1712&fin_year=2026-2027&source=national&rdbutton=0&Digest=bxHEcyU8JyvdJ3rs8H7x9g')
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
            # pending regeneration count/amount, muster, FTO, success, bank pending.
            vals = [number(x) for x in row[i+1:i+9]]
            if len(vals) < 8: raise ValueError('Incomplete summary columns')
            janpad = key(row[i]);total,total_amount,pending,pending_amount,muster,fto,success,bank_pending=vals
            if min(vals)<0 or pending>total or pending_amount>total_amount:
                raise ValueError('Invalid official summary amounts')
            result.append(dict(fy='2026-27',janpad=janpad,district=DIST.get(janpad,'SATNA'),total=total,totalAmount=total_amount,pending=pending,pendingAmount=pending_amount,muster=muster,fto=fto,success=success,bankPending=bank_pending,reasons={}))
        if len(result)==8 and len({r['janpad'] for r in result})==8:
            return sorted(result,key=lambda r:r['janpad'])
    raise ValueError('Official R8.1.5 table with eight Janpads was not found; existing data preserved')

async def main():
    from playwright.async_api import async_playwright
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(headless=True)
        page = await browser.new_page()
        response = await page.goto(SOURCE, wait_until='domcontentloaded', timeout=90000)
        if not response or response.status >= 400: raise RuntimeError('Official portal unavailable')
        await page.wait_for_timeout(2500)
        tables = await page.locator('table').evaluate_all('(tables) => tables.map(t => [...t.rows].map(r => [...r.cells].map(c => c.innerText)))')
        await browser.close()
    rows = parse(tables)
    today = datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()
    old = json.loads(DEST.read_text()) if DEST.exists() else None
    if old and old.get('date') == today and old.get('rows') == rows: return
    prior = {'date':old['date'],'rows':old['rows']} if old and old.get('date') != today else (old.get('previous') if old else None)
    DEST.parent.mkdir(exist_ok=True)
    tmp = DEST.with_suffix('.tmp')
    tmp.write_text(json.dumps({'date':today,'source':SOURCE,'rows':rows,'previous':prior},ensure_ascii=False,indent=2)+'\n')
    tmp.replace(DEST)
    print('Rejected wage updated:', today, len(rows), 'Janpads')

if __name__ == '__main__': asyncio.run(main())
