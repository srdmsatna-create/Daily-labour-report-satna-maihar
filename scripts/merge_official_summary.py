#!/usr/bin/env python3
import csv,json,re,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]
CSV=ROOT/'data'/'official-summary.csv'
AUTO=ROOT/'auto-data.js'
STATUS=ROOT/'data'/'fetch-status.json'
VALID={'AMARPATAN','MAIHAR','RAMNAGAR','MAJHGAWAN','NAGOD','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}
NUMFIELDS=['totalGP','musterGP','dysfunctionalGP','labourAll','mrAll','ongoingAll','labourIndividual','mrIndividual','labourCommunity','mrCommunity','pmayOngoing','pmayMR','ekLabour','ekOngoing','ekMR']

def num(v):
    try: return float(str(v).replace(',','').strip() or 0)
    except: return 0.0

def load_auto():
    s=AUTO.read_text(encoding='utf-8').strip()
    s=re.sub(r'^window\.AUTO_REPORT\s*=\s*','',s)
    s=s.rstrip(';')
    return json.loads(s)

def main():
    if not CSV.exists(): raise SystemExit('Missing data/official-summary.csv')
    with CSV.open(encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    got={str(r.get('janpad','')).strip().upper() for r in rows}
    if got != VALID: raise SystemExit(f'Official summary validation failed: {sorted(got)}')
    clean=[]
    for r in rows:
        z={'janpad':str(r['janpad']).strip().upper()}
        for k in NUMFIELDS:z[k]=num(r.get(k,0))
        if z['totalGP']<=0 or z['ongoingAll']<=0: raise SystemExit(f'Invalid official row: {z["janpad"]}')
        clean.append(z)
    data=load_auto()
    data['official']=clean
    # Update Screen-2-compatible fields that are exactly present in the official summary.
    # Keep mrs/noEkyc from last full workbook because they are not present in summary export.
    oldd={str(r.get('janpad','')).upper():r for r in data.get('daily',[])}
    daily=[]
    for o in clean:
        old=oldd.get(o['janpad'],{})
        daily.append({'janpad':o['janpad'],'totalGP':o['totalGP'],'gpsProgress':o['musterGP'],
                      'labour':o['labourAll'],'worksMR':o['mrAll'],
                      'noEkyc':num(old.get('noEkyc',0)),'mrs':num(old.get('mrs',o['mrAll']))})
    data['daily']=daily
    meta=data.setdefault('meta',{})
    meta.update({'mode':'auto','status':'ok','updatedAt':datetime.now(timezone.utc).isoformat(),
                 'source':'Official VB-G RAM G summary (browser table fallback)',
                 'officialSummaryRows':8})
    try:
        st=json.loads(STATUS.read_text(encoding='utf-8'))
        if st.get('officialDate'): meta.setdefault('sourceDates',{})['OfficialSummary']=st['officialDate']
    except Exception: pass
    AUTO.write_text('window.AUTO_REPORT='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print('Merged fresh official summary into auto-data.js; preserved detailed GP/engineer data from last full workbook.')
if __name__=='__main__': main()
