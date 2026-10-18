"""Fetch official timely FTO generation status for the eight Janpads."""
import argparse,json,os,re,urllib.request
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from update_delayed_compensation import Rows,number,BLOCKS
from vbgram_access import open_url
ROOT=Path(__file__).resolve().parents[1]
SOURCE="https://vbgramgrep.dord.gov.in/vbgramg/Paymentstatus.aspx?payload=Gp6O_k1cykTFF_DROerGZbGuvTVPALF_QmsBtzjwEntRgPtcNH-suqVIrk3S7_hJcyQW9zgzdQYzReXtLtDs5aIfgUucCYGdswtPBBoaBpROjYMbBmWrS3j4Cu_CRrTTfvc7ElnKOGtPcmpYldNdHlxI3K0I6l8bEZj7UbeO5Xc8fZbXzeL6Q9vb9a5sOGHXBIRgj8jb1tOGPkM30aEPtNh4XcqqlV8sUKaP3YAmMNcZgOJApZILpSCGc3xMP596"
FIELDS=('mustersIssued','mustersFilled','pendingWithin8','pendingOver8','timelyFtoPct','delay9to15Pct','delay15PlusPct')
def validate(payload):
 rows=payload.get('rows',[])
 if len(rows)!=8 or {row.get('block') for row in rows}!=BLOCKS:raise ValueError('All eight unique timely payment Janpads required')
 for row in rows+[payload.get('totals',{})]:
  for key in FIELDS:
   value=row.get(key)
   if not isinstance(value,(int,float)) or value<0 or value!=value or value==float('inf') or (key.endswith('Pct') and value>100):raise ValueError('Invalid timely payment value: '+key)
 for key in FIELDS[:4]:
  if sum(row[key] for row in rows)!=payload['totals'][key]:raise ValueError('Timely payment total mismatch: '+key)
 if payload.get('financialYear')!='2026-2027':raise ValueError('Unexpected timely payment financial year')
def parse(source):
 if not re.search(r'Timely\s+Payment',source,re.I) or not re.search(r'2026\s*-\s*2027',source):raise ValueError('Unexpected timely payment report')
 parser=Rows();parser.feed(source);rows=[];totals=[]
 for cells in parser.rows:
  if len(cells)<9:continue
  name=' '.join(cells[1].upper().split())
  if name not in BLOCKS and name!='TOTAL':continue
  values=dict(zip(FIELDS,(number(cells[i]) for i in range(2,9))))
  if name=='TOTAL':totals.append(values)
  else:rows.append({'block':name,**values})
 if not totals or any(row!=totals[0] for row in totals):raise ValueError('Official timely payment totals missing or inconsistent')
 payload={'schemaVersion':1,'financialYear':'2026-2027','source':SOURCE,'fetchedAt':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'rows':rows,'totals':totals[0],'basis':'Official timely FTO generation within T+8 days; not bank credit confirmation'}
 validate(payload);return payload
def main():
 parser=argparse.ArgumentParser();parser.add_argument('--html');args=parser.parse_args()
 url=os.environ.get('VBGRAM_TIMELY_PAYMENT_URL',SOURCE)
 source=Path(args.html).read_text(encoding='utf-8-sig') if args.html else open_url(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=90).read().decode('utf-8-sig')
 payload=parse(source);payload['source']=url
 target=ROOT/'data/timely-payment-latest.json';target.parent.mkdir(parents=True,exist_ok=True)
 temporary=target.with_suffix('.tmp');temporary.write_text(json.dumps(payload,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');temporary.replace(target)
 print('Verified timely FTO payment: 8 Janpads and official totals.')
if __name__=='__main__':main()
