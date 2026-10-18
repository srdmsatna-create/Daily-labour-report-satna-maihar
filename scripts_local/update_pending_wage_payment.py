"""Build pending wage payment from FTO district column 4 -> detail columns 8 minus 13."""
import argparse,json,os,re,time,urllib.request,urllib.parse
from pathlib import Path
from html.parser import HTMLParser
from datetime import datetime
from zoneinfo import ZoneInfo
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
from update_delayed_compensation import BLOCKS
from vbgram_access import session_opener
ROOT=Path(__file__).resolve().parents[1]
SOURCE="https://vbgramgrep.dord.gov.in/VBGRAMG/FTO/FTOReport.aspx?payload=q_4mhjc4o52KJHP_5wn18JCk0xH5S2cCeE-HbbKETQGI8_5UTabnFFQsvngT1XQ8o7joAtcACKkINtS06-fyM9ItonNAUFCPOyqDpPC9Bqsi4SR9xOvuNZ502_ZRSfU9DMNBUHTgXRr6BK6Vy5-BfXhCsqoIj6wdCznnUzUpVZdYapanPO8rbpWG6snBHeY6dAt7mo0GoYf3pYUaN4z3tV-xRuTbmDzJMFZE909f7p3Iqbq0XBJifQyKNrjvBoKq"
class Table(HTMLParser):
 def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,tag,attrs):
  if tag=='tr':self.row=[]
  if tag in ('td','th'):self.cell={'text':'','links':[]}
  if tag=='a' and self.cell is not None:self.cell['links'].append(dict(attrs).get('href',''))
 def handle_data(self,value):
  if self.cell is not None:self.cell['text']+=value
 def handle_endtag(self,tag):
  if tag in ('td','th') and self.cell is not None:
   self.cell['text']=' '.join(self.cell['text'].split())
   if self.row is not None:self.row.append(self.cell)
   self.cell=None
  if tag=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
def table(source):
 parser=Table();parser.feed(source);return parser.rows
def amount(value):
 value=value.replace(',','').strip()
 if not re.fullmatch(r'\d+(?:\.\d+)?',value):raise ValueError('Non-numeric official FTO amount')
 return Decimal(value)
def fetch(url):
 if urllib.parse.urlparse(url).hostname!='vbgramgrep.dord.gov.in':raise ValueError('Unexpected source host')
 for attempt in range(3):
  try:
   request=urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'})
   return session_opener().open(request,timeout=75).read().decode('utf-8-sig')
  except Exception:
   if attempt==2:raise RuntimeError('Official FTO source could not be read; previous data retained') from None
   time.sleep(1+attempt)
def parent_rows(source,url):
 if not re.search(r'2026\s*-\s*2027',source):raise ValueError('Unexpected FTO financial year')
 result=[]
 for row in table(source):
  if len(row)<4 or row[1]['text'].upper() not in BLOCKS:continue
  block=row[1]['text'].upper();count=int(amount(row[3]['text']))
  links=[urllib.parse.urljoin(url,link) for link in row[3]['links'] if 'fto_sign_detail.aspx' in link.lower()]
  if len(links)!=1:raise ValueError('Column 4 detail link missing: '+block)
  result.append({'block':block,'expectedFtos':count,'detailSource':links[0]})
 if len(result)!=8 or {r['block'] for r in result}!=BLOCKS:raise ValueError('Eight unique column 4 Janpad links required')
 return result
def detail_totals(source,expected):
 rows=table(source)
 headers=[r for r in rows if len(r)>=14 and r[7]['text'].replace(' ','').lower()=='amount(inrs.)' and 'totalprocessedamount' in r[12]['text'].replace(' ','').lower()]
 if not headers:raise ValueError('Detail columns 8 and 13 not found')
 details=[r for r in rows if len(r)>=14 and r[0]['text'].isdigit() and re.fullmatch(r'171200[1-8]',r[2]['text'])]
 if expected and not details:raise ValueError('Detail rows missing')
 if len({r[3]['text'] for r in details})!=len(details):raise ValueError('Duplicate FTO records')
 a=sum((amount(r[7]['text']) for r in details),Decimal(0));p=sum((amount(r[12]['text']) for r in details),Decimal(0))
 totals=[r for r in rows if len(r)>=14 and any(c['text'].upper()=='TOTAL' for c in r[:3])]
 if (expected or details) and (not totals or any(amount(r[7]['text'])!=a or amount(r[12]['text'])!=p or int(amount(r[6]['text']))!=len(details) for r in totals)):raise ValueError('Official detail total mismatch')
 return {'amount':float(a),'totalProcessedAmount':float(p),'pendingWageAmount':float(a-p),'ftoCount':len(details)}
def validate(payload):
 rows=payload.get('rows',[])
 if len(rows)!=8 or {r.get('block') for r in rows}!=BLOCKS or payload.get('basis')!='parent-column-4-detail-8-minus-13':raise ValueError('Complete verified wage feed required')
 for row in rows:
  if abs(row['pendingWageAmount']-(row['amount']-row['totalProcessedAmount']))>0.01:raise ValueError('FTO count or pending amount mismatch')
  if any(not isinstance(row[k],(int,float)) or row[k]<0 or row[k]!=row[k] or row[k]==float('inf') for k in ('amount','totalProcessedAmount','pendingWageAmount')):raise ValueError('Invalid wage amount')
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--parent-html');args=parser.parse_args()
 url=os.environ.get('VBGRAM_PENDING_WAGE_URL',SOURCE)
 source=Path(args.parent_html).read_text(encoding='utf-8-sig') if args.parent_html else fetch(url)
 parents=parent_rows(source,url)
 def worker(parent):
  print('Reading column 4 FTO detail: '+parent['block'],flush=True)
  source=fetch(parent['detailSource']);result={**parent,**detail_totals(source,parent['expectedFtos'])};result['parentCountMatches']=result['ftoCount']==parent['expectedFtos']
  if parent['expectedFtos'] and not all(r[2]['text']=={'AMARPATAN':'1712006','MAIHAR':'1712008','RAMNAGAR':'1712007','MAJHGAWAN':'1712001','NAGOD':'1712003','RAMPUR BAGHELAN':'1712005','SATNA':'1712002','UNCHAHARA':'1712004'}[parent['block']] for r in table(source) if len(r)>=14 and r[0]['text'].isdigit() and re.fullmatch(r'171200[1-8]',r[2]['text'])):raise ValueError('Wrong Janpad detail')
  return result
 with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(worker,parents))
 payload={'schemaVersion':1,'financialYear':'2026-2027','basis':'parent-column-4-detail-8-minus-13','source':url,'fetchedAt':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'rows':rows}
 validate(payload);payload['totals']={key:round(sum(r[key] for r in rows),2) for key in ('amount','totalProcessedAmount','pendingWageAmount')}
 target=ROOT/'data/pending-wage-payment-latest.json';target.parent.mkdir(parents=True,exist_ok=True);temp=target.with_suffix('.tmp')
 temp.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temp.replace(target)
 print('Verified all 8 Janpads. Pending wage amount: '+str(payload['totals']['pendingWageAmount']),flush=True)
if __name__=='__main__':main()
