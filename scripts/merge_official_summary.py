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
        z['dysfunctionalGP']=max(0,z['totalGP']-z['musterGP'])
        clean.append(z)
    data=load_auto(); data['official']=clean
    data['daily']=[{'janpad':o['janpad'],'totalGP':o['totalGP'],'gpsProgress':o['musterGP'],'labour':o['labourAll'],'worksMR':o['mrAll'],'noEkyc':o['noEkyc'],'mrs':o['mrs']} for o in clean]
    meta=data.setdefault('meta',{}); meta.update({'mode':'auto','status':'ok','updatedAt':datetime.now(timezone.utc).isoformat(),'source':'Official VB-G RAM G Screen-2 + rich summary','officialSummaryRows':8,'screen2Matched':True})
    try:
        st=json.loads(STATUS.read_text(encoding='utf-8'))
        if st.get('officialDate'): meta.setdefault('sourceDates',{})['OfficialSummary']=st['officialDate']
    except Exception: pass
    AUTO.write_text('window.AUTO_REPORT='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
    print('V46: Screen-2 exact shared metrics merged; rich ongoing/category fields preserved.')
if __name__=='__main__': main()
