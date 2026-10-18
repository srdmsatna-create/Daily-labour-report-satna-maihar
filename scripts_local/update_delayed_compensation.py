"""Fetch R14.1 delayed compensation columns 3, 4 and 10 from the official portal."""
import argparse,json,os,re,sys,urllib.request
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
from html.parser import HTMLParser
from vbgram_access import open_url
ROOT=Path(__file__).resolve().parents[1]
SOURCE="https://vbgramgrep.dord.gov.in/vbgramg/state_html/delay_comp.aspx?payload=Wa9ApVQrWUX5074SaLB90maQfuH1Jgp2TO9QKeKiVvptrQBHWVXkubg0Hy2J-pLin3ezWwyap_fBtth21PyNXlSNziQNm0xxBEtkmUXdcAiIBubfDRK-0hZ9MAkpcH7Y32xLZBlANeC98axW5IbD-URRajOMlpctKt8vI5HW6vomogPqntPmIOCuMMjTTNwuE8ANHhKjEbZZGGP8atBYWZfePvXgfLj_jVgK-ARGSdkqeB2ZCNy8_JA874lpKIg8"
BLOCKS={'AMARPATAN','MAIHAR','RAMNAGAR','MAJHGAWAN','NAGOD','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}
FIELDS=('compPayableDays','compPayableAmount','compNotDueDays')
class Rows(HTMLParser):
 def __init__(self):
  super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row=[]
  if tag in ('td','th'):self.cell=[]
 def handle_data(self,value):
  if self.cell is not None:self.cell.append(value)
 def handle_endtag(self,tag):
  if tag in ('td','th') and self.cell is not None:
   if self.row is not None:self.row.append(' '.join(''.join(self.cell).split()))
   self.cell=None
  if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
def number(value):
 value=value.replace(',','').strip()
 if not re.fullmatch(r'\d+(?:\.\d+)?',value):raise ValueError('Non-numeric portal cell')
 return float(value) if '.' in value else int(value)
def parse(source):
 if not re.search(r'Delayed\s+Compensation',source,re.I) or not re.search(r'2026\s*-\s*2027',source):raise ValueError('Unexpected report or financial year')
 parser=Rows();parser.feed(source);rows=[];official=[]
 for cells in parser.rows:
  if len(cells)<10:continue
  name=' '.join(cells[1].upper().split())
  if name in BLOCKS:rows.append({'block':name,**dict(zip(FIELDS,(number(cells[i]) for i in (2,3,9))))})
  elif name=='TOTAL':official.append(dict(zip(FIELDS,(number(cells[i]) for i in (2,3,9)))))
 payload={'schemaVersion':1,'financialYear':'2026-2027','source':SOURCE,'fetchedAt':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'rows':rows}
 validate(payload)
 totals={key:sum(row[key] for row in rows) for key in FIELDS}
 if not official or any(abs(total[key]-totals[key])>0.01 for total in official for key in FIELDS):raise ValueError('Janpad totals do not match official district total')
 payload['totals']=totals
 return payload
def validate(payload):
 rows=payload.get('rows',[])
 if len(rows)!=8 or {row.get('block') for row in rows}!=BLOCKS:raise ValueError('All eight unique Janpads required')
 for row in rows:
  for key in FIELDS:
   value=row.get(key)
   if not isinstance(value,(int,float)) or value<0 or value!=value or value==float('inf'):raise ValueError('Invalid compensation value')
 if payload.get('financialYear')!='2026-2027':raise ValueError('Unexpected financial year')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--html',help='Parse a downloaded official response');args=parser.parse_args()
 url=os.environ.get('VBGRAM_DELAY_COMP_URL',SOURCE)
 if args.html:source=Path(args.html).read_text(encoding='utf-8-sig')
 else:
  request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
  source=open_url(request,timeout=90).read().decode('utf-8-sig')
 payload=parse(source);payload['source']=url
 target=ROOT/'data/delayed-compensation-latest.json';target.parent.mkdir(exist_ok=True,parents=True)
 temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temporary.replace(target)
 print('Verified delayed compensation: 8 Janpads; columns 3, 4 and 10 reconcile with official total.')
if __name__=='__main__':main()
