"""Refresh verified payment JSON from the configured official work-level feed.

Feed contract: sourceDate DD/MM/YYYY, source URL, and eight Janpad rows
with works, ongoing, sw/sm, bw/bm, pw/pm in lakh rupees.
Never date-stamp the historical CSV as a current payment report.
"""
import json, math, os, urllib.request
from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
JANPADS=['AMARPATAN','MAIHAR','RAMNAGAR','MAJHGAWAN','NAGOD','RAMPUR BAGHELAN','SATNA','UNCHAHARA']
def validate(d):
 today=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d/%m/%Y')
 if d.get('sourceDate')!=today or not d.get('source'):raise ValueError('Today dated official payment feed required')
 rows=d.get('rows',[])
 if len(rows)!=8 or {r.get('janpad') for r in rows}!=set(JANPADS):raise ValueError('Eight unique Janpads required')
 for r in rows:
  for k in ['works','ongoing','sw','sm','bw','bm','pw','pm']:
   v=r.get(k)
   if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or v<0:raise ValueError('Missing/invalid '+k)
  if int(r['works'])!=r['works'] or int(r['ongoing'])!=r['ongoing']:raise ValueError('Integer work counts required')
 d['rows']=sorted(rows,key=lambda r:JANPADS.index(r['janpad']))
 return d
def main():
 url=os.environ.get('EK_BAGIYA_PAYMENT_SOURCE_URL','').strip()
 if not url:raise RuntimeError('EK_BAGIYA_PAYMENT_SOURCE_URL not configured; previous dated payment figures retained')
 request=urllib.request.Request(url,headers={'User-Agent':'SRDM Daily Payment Reader','Cache-Control':'no-cache'})
 with urllib.request.urlopen(request,timeout=90) as response:d=validate(json.load(response))
 d['checkedAt']=datetime.now(timezone.utc).isoformat()
 path=ROOT/'data/ek-bagiya-payment-latest.json';path.parent.mkdir(exist_ok=True)
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)
 print('Verified current payment snapshot: eight Janpads')
if __name__=='__main__':main()
