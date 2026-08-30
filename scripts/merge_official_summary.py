#!/usr/bin/env python3
import csv,json,re
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/'data'/'official-summary.csv'; AUTO=ROOT/'auto-data.js'; STATUS=ROOT/'data'/'fetch-status.json'
VALID={'AMARPATAN','MAIHAR','RAMNAGAR','MAJHGAWAN','NAGOD','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}
NUMFIELDS=['totalGP','musterGP','dysfunctionalGP','labourAll','mrAll','noEkyc','mrs','ongoingAll','labourIndividual','mrIndividual','labourCommunity','mrCommunity','pmayOngoing','pmayMR','ekLabour','ekOngoing','ekMR']
def num(v):
    try:return float(str(v).replace(',','').strip() or 0)
    except:return 0.0
def load_auto():
    s=AUTO.read_text(encoding='utf-8').strip(); s=re.sub(r'^window\.AUTO_REPORT\s*=\s*','',s).rstrip(';'); return json.loads(s)
def main():
    with CSV.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    got={str(r.get('janpad','')).strip().upper() for r in rows}
    if got!=VALID: raise SystemExit(f'Official summary validation failed: {sorted(got)}')
    clean=[]
    for r in rows:
        z={'janpad':str(r['janpad']).strip().upper()}
        for k in NUMFIELDS:z[k]=num(r.get(k,0))
        if z['totalGP']<=0 or z['musterGP']<=0: raise SystemExit(f'Invalid Screen-2 row: {z["janpad"]}')
        clean.append(z)
    data=load_auto()
    new_daily = [{
        'janpad': o['janpad'],
        'totalGP': o['totalGP'],
        'gpsProgress': o['musterGP'],
        'dysfunctionalGP': o['dysfunctionalGP'],

        'labour': o['labourAll'],
        'worksMR': o['mrAll'],
        'ongoing': o['ongoingAll'],
        'mrs': o['mrs'],

        'labourIndividual': o['labourIndividual'],
        'mrIndividual': o['mrIndividual'],

        'labourCommunity': o['labourCommunity'],
        'mrCommunity': o['mrCommunity'],

        'pmayOngoing': o['pmayOngoing'],
        'pmayMR': o['pmayMR'],

        'ekLabour': o['ekLabour'],
        'ekOngoing': o['ekOngoing'],
        'ekMR': o['ekMR']
    } for o in clean]
    # V51 freshness lock: change Last auto update ONLY when report values change.
    # A successful source check is still visible through auto-status.js/fetch-status.json.
    before=json.dumps({'official':data.get('official',[]),'daily':data.get('daily',[])},ensure_ascii=False,sort_keys=True,separators=(',',':'))
    after=json.dumps({'official':clean,'daily':new_daily},ensure_ascii=False,sort_keys=True,separators=(',',':'))
    changed=(before!=after)
    data['official']=clean
    data['daily']=new_daily
    meta=data.setdefault('meta',{})
    meta.update({'mode':'auto','status':'ok','source':'Official VB-G RAM G Screen-2 + rich summary','officialSummaryRows':8,'screen2Matched':True})
    if changed or not meta.get('updatedAt'):
        meta['updatedAt']=datetime.now(timezone.utc).isoformat()
    meta['dataChangedOnLastFetch']=changed
    try:
        st=json.loads(STATUS.read_text(encoding='utf-8'))
        if st.get('officialDate'): meta.setdefault('sourceDates',{})['OfficialSummary']=st['officialDate']
    except Exception: pass
    AUTO.write_text('window.AUTO_REPORT='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print('V51: Screen-2 merged. dataChangedOnLastFetch=', changed)
if __name__=='__main__': main()
