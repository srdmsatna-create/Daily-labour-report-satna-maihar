"""Official MIS 6.12 PMAY-G/IAY, all years, Approved and Ongoing."""
import json, csv, re, sys, os, time, hashlib, threading
import urllib.error
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from update_mis_612_work_details import ROOT, URL, session_opener, open_text, hidden_fields, selected_values, form_action, ResultRows, urllib

NREGA_URL = 'https://mnregaweb4.dord.gov.in/netnregarep/dynamic_work_details.aspx?payload=1A6ER1_wmGucIcI52WXSl9SkSWhbH7D3haJAJXUMlyb14ejtY0bcdGB_dPLenxioqvwn54kAvAJcdWMn8bG6bEOKIFFaagksd7d05w89LAE5g8XeBjPemgG8WXtByI9jz0JwvqaF69nYig9mt_HPIJtQGJDa0qodof_n3qpTR4uWxP2M3JrjrIfdHr2407Wf'
VBG_URL = 'https://vbgramgrep.dord.gov.in/VBGRAMG/dynamic_work_details.aspx?payload=ftnyL9stdXeAc7zMQW8cHY09zYjD7YVdkcCL1EOM3Wm_8lISfAJzdF6JhnQsT5n17zpy7r_Vba0PwONGLjnUmidzdUwQaYSFBWiqr8uMNsbD7W7oGi8r9C5028sI0yPRNL4IbdUTLIJyaorEpuLA8Q4t0xSSpie_wrjIAKCgcGA7aPT1CYMPdmkLhKSFE6NZ'

class ExpenditureRows(ResultRows):
 def handle_endtag(self,tag):
  cells=list(self.row or []) if tag.lower()=='tr' else []
  before=len(self.rows)
  super().handle_endtag(tag)
  if len(self.rows)>before:
   self.rows[-1]['Current FY Wages']=cells[16]
   self.rows[-1]['Current FY Material']=cells[17]

def norm(s):return re.sub(r'[^A-Z0-9]','',str(s).upper())
def block_key(s):
 key=norm(s)
 return 'SOHAWAL' if key=='SATNA' else key
def open_with_retry(opener,url,data=None,timeout=60):
 for attempt in range(1,4):
  stop=threading.Event();started=time.monotonic()
  def heartbeat():
   while not stop.wait(15):
    print('Waiting for official portal response: '+str(int(time.monotonic()-started))+' sec (attempt '+str(attempt)+'/3)',flush=True)
  worker=threading.Thread(target=heartbeat,daemon=True);worker.start()
  try:return open_text(opener,url,data,timeout=min(timeout,60))
  except Exception as e:
   retryable=isinstance(e,(TimeoutError,urllib.error.URLError))
   if isinstance(e,urllib.error.HTTPError):retryable=e.code in (408,429,500,502,503,504)
   if not retryable or attempt==3:raise
   print('Temporary portal failure; retry '+str(attempt)+'/2',flush=True)
  finally:stop.set();worker.join(timeout=1)


def fetch_source(source_url):
 opener=session_opener();src,url=open_with_retry(opener,source_url)
 d=hidden_fields(src);selected_values(src,d);d.update({'__EVENTTARGET':'ctl00$ContentPlaceHolder1$ddl_dist','ctl00$ContentPlaceHolder1$ddl_state':'17','ctl00$ContentPlaceHolder1$ddl_dist':'1712'})
 src,url=open_with_retry(opener,form_action(src,url),urllib.parse.urlencode(d).encode())
 if 'value="1712006"' not in src:raise ValueError('District/block form did not load')
 base=hidden_fields(src);selected_values(src,base)
 prefix='ctl00$ContentPlaceHolder1$'
 base.update({'__EVENTTARGET':'',prefix+'ddl_blk':'ALL',prefix+'ddl_pan':'ALL',prefix+'Ddlworkcategory':'ALL',prefix+'ddlFin_year':'ALL',prefix+'filter':'ALL',prefix+'Button1':'Submit'})
 cache_dir=Path(os.environ.get('PMAY_FETCH_CACHE_DIR','')) if os.environ.get('PMAY_FETCH_CACHE_DIR') else ROOT/'data'/'pmayg-fetch-cache';cache_dir.mkdir(parents=True,exist_ok=True)
 today=datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()
 rows=[]
 for status,label in [('03','Ongoing')]:
  for kind in ['ALL']:
   key=hashlib.sha256((source_url+'|above75-v1|'+today+'|'+status+'|'+kind).encode()).hexdigest()
   cache=cache_dir/(key+'.json')
   if cache.exists():
    saved=json.loads(cache.read_text(encoding='utf-8'))
    if saved.get('date')==today and saved.get('status')==label:
     rows.extend(saved['rows']);print('CHECKPOINT '+label+' / '+kind+': '+str(len(saved['rows']))+' rows',flush=True);continue
   payload=dict(base);payload.update({prefix+'Ddlwork_status':status,prefix+'ddlprostatus':kind})
   print('Fetching '+label+' / '+kind,flush=True)
   page,_=open_with_retry(opener,form_action(src,url),urllib.parse.urlencode(payload).encode(),timeout=180)
   if 'Work Code' not in page and 'Work_Code' not in page and not re.search(r'No\s+(?:Record|Data)',page,re.I):raise ValueError('Unrecognized report response')
   parser=ExpenditureRows(label);parser.feed(page);parser.close()
   for r in parser.rows:
    if r['Work Status'].lower()!=label.lower():raise ValueError('Status filter mismatch')

   temp=cache.with_suffix('.tmp');temp.write_text(json.dumps({'date':today,'status':label,'rows':parser.rows},ensure_ascii=False),encoding='utf-8');os.replace(temp,cache)
   print('Rows: '+str(len(parser.rows)),flush=True);rows.extend(parser.rows)
 return rows


def main():
 nrega=fetch_source(NREGA_URL);vbg=fetch_source(VBG_URL)
 if not nrega or not vbg:raise ValueError('Both official ongoing reports required')
 def index(rows):
  out={}
  for r in rows:
   if r['Work Code'] in out:raise ValueError('Duplicate Work Code')
   out[r['Work Code']]=r
  return out
 nrega=index(nrega);vbg=index(vbg)
 master=list(csv.DictReader((ROOT/'gp-sector-engineer-master-25-09-2026.csv').open(encoding='utf-8-sig')))
 mapping={}
 for m in master:
  for k in ['Gram_Panchayat','GP_20Sep_Name']:mapping[(block_key(m['Janpad']),norm(m[k]))]=m
 def number(r,k):
  v=r.get(k,'').replace(',','').strip()
  if not v:raise ValueError('Missing expenditure field '+k)
  v=float(v)
  if v<0:raise ValueError('Negative amount')
  return v
 rows=[];missing=[]
 for code,a in nrega.items():
  b=vbg.get(code)
  if b is None:missing.append({'code':code,'janpad':a['Janpad / Block Name'],'gp':a['Panchayat Name']});continue
  sanction=number(a,'Total Sanction (Rs)')
  old=number(a,'Booked Since Inception Wages (Rs)')+number(a,'Booked Since Inception Material (Rs)')
  fresh=number(b,'Current FY Wages')+number(b,'Current FY Material')
  m=mapping.get((block_key(a['Janpad / Block Name']),norm(a['Panchayat Name'])))
  if not m:raise ValueError('GP mapping missing: '+a['Panchayat Name'])
  rows.append({'code':code,'name':a['Work Name'],'janpad':a['Janpad / Block Name'],'panchayat':a['Panchayat Name'],'cluster':m['Sector'],'engineer':m['Sub_Engineer'],'fy':a['Work Start Fin Year'],'status':'Ongoing','type':a['Work Type'],'sanction':sanction,'nregaBooked':old,'vbgBooked':fresh,'overallBooked':old+fresh,'overallExpPct':(old+fresh)*100/sanction if sanction else None})
 if not rows:raise ValueError('No matched works; publication refused')
 output={'source':'MGNREGA FY 2026-27 Ongoing + VBGRAMG FY 2026-27 current expenditure','fetchedAt':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'allWorkYears':True,'nregaCount':len(nrega),'vbgCount':len(vbg),'matchedCount':len(rows),'unmatched':missing,'rows':rows}
 p=ROOT/'data/above75-latest.json';p.parent.mkdir(exist_ok=True);t=p.with_suffix('.tmp');t.write_text(json.dumps(output,ensure_ascii=False),encoding='utf-8');os.replace(t,p)
 print('SUCCESS above75: matched='+str(len(rows))+'; pending VBGRAMG match='+str(len(missing)),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('FAILED above75; previous data retained: '+str(e),flush=True);sys.exit(1)
