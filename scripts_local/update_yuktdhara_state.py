"""Refresh the 52-district Yuktdhara monitoring snapshot atomically."""
import json,os,re,sys,urllib.request
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from html import unescape
ROOT=Path(__file__).resolve().parents[1]
URL='https://vbgramgrep.dord.gov.in/vbgramg/Yuktdhara_rpt.aspx?payload=I01hdt8Z7y24sN56TPoNURxE-quMyvmtGoLf2F-fd-Vl8-jGhNZ1BrjPGth165kzZFWcB5RBvotvNacDnpYYiILgmrYHPVY_vjK9DBDOfqqoJ9gF-KduFUg7OyL35WdbmmalI19Jn06CvqOGCHDR-zG1munAu39ePJ9oiWV2OH31jHJpmUeKpOSJSgi3B9e1'
KEYS=['gp','gpReceived','worksReceived','worksCreated','yetToStart','ongoing']
def clean(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]+>','',s))).strip()
def number(s):
 n=float(s.replace(',',''))
 if n<0 or not n.is_integer():raise ValueError('Invalid count')
 return int(n)
def parse(source):
 rows=[];total=None
 for tr in re.findall(r'<tr\b[^>]*>(.*?)</tr>',source,re.S|re.I):
  c=[clean(x) for x in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]>',tr,re.S|re.I)]
  if len(c)<9:continue
  positions=[2,3,5,6,8,9] if len(c)>=11 else [2,3,4,5,6,7]
  if c[0].isdigit() and c[1] and not c[1].isdigit():rows.append(dict(district=c[1].upper(),**dict(zip(KEYS,[number(c[i]) for i in positions]))))
  elif any(x.lower() in ('total','grand total') for x in c[:2]):total=dict(zip(KEYS,[number(c[i]) for i in positions]))
 if len(rows)!=52 or len({r['district'] for r in rows})!=52:raise ValueError('Expected 52 unique districts')
 sums={k:sum(r[k] for r in rows) for k in KEYS}
 if total is None or total!=sums:raise ValueError('State totals mismatch')
 if not any(r['district']=='SATNA' and r['gp']==695 for r in rows):raise ValueError('SATNA coverage missing')
 return rows,total
def main():
 req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0','Cache-Control':'no-cache'})
 with urllib.request.urlopen(req,timeout=90) as response:source=response.read().decode('utf-8','ignore')
 rows,totals=parse(source)
 m=re.search(r'(?:Report last Updated on:|Shedule_updated_date[^>]*>)\s*(\d{2}/\d{2}/\d{4})',source,re.I)
 d=dict(financialYear='2026-2027',fetchedAt=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),officialDate=m.group(1) if m else '',source=URL,rows=rows,totals=totals)
 p=ROOT/'data/yuktdhara-state-latest.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+'\n');os.replace(tmp,p)
 print('SUCCESS Yuktdhara state: 52 districts; '+str(totals),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('FAILED: state snapshot retained: '+str(e),flush=True);sys.exit(1)
