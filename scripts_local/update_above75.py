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


import html,math
BaseRows=ExpenditureRows
class ExpenditureRows(BaseRows):
 def handle_endtag(self,tag):
  cells=list(self.row or []) if tag.lower()=='tr' else [];n=len(self.rows);super().handle_endtag(tag)
  if len(self.rows)>n:self.rows[-1].update(paidWages=cells[22],paidMaterial=cells[23])
def fetch_source(source_url,status,label):
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
 for status,label in [(status,label)]:
  for kind in ['ALL']:
   key=hashlib.sha256((source_url+'|r613-paid-inspection|'+today+'|'+status+'|'+kind).encode()).hexdigest()
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


R613_URLS=['https://mnregaweb4.dord.gov.in/netnregarep/incomplete_works_Yearwise.aspx?payload=wlzcDkNgHsc1Bqk56sgn0cRHAZRE5bP2FwOm2Qq0je66lRYnpzRheqn29gJJheJ9CaJtM8RTrWs1rxPwAoNXQym-VjO0GmHKE6lJt6VsOGs9puWbJahcgoNsYmLcbGE4-0wBQJx-ABBDc_HZ_CROqiutmaLJD-358w32JVEDtUZ_qSCX8YD7oEoAEQwQ2c1OZt2Z8AukQRTbY_XSHEDnil26rqKffXb7bfm3V5hgP9-cT-0rnS2-jCqQ-8VI9kIF', 'https://vbgramgrep.dord.gov.in/VBGRAMG/incomplete_works_Yearwise.aspx?payload=zNVdSezGPZEO5qnUauuNyrKXu3I5UPwSHnyG_YQrImXAYNKQG6UsdzLiMmvM1oMAkfiMpurs-eRmDMRcaQe233MOvvhD3GcnBv0xAA8yQWuJAa8k7YT8uOpgKPJBDpB8m7-ohnSIjaAsKsn_usika7sWulAvmKGgN401-zec2jTyMw4aRNXD4dSwrO9go3cw7xFRxTY0JCvDsvwF87JbPChGtJ_UmVqS1Qt0xwa5pcpl_HdoR9WgTYyPADkzsOtc']
def official_summary(url):
 from bs4 import BeautifulSoup
 page,_=open_with_retry(session_opener(),url)
 expected={'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPURBAGHELAN','SOHAWAL','UNCHAHARA'}
 rows={}
 soup=BeautifulSoup(page,'html.parser')
 for tr in soup.find_all('tr'):
  cells=[re.sub(r'\s+',' ',cell.get_text(' ',strip=True)).strip() for cell in tr.find_all(['td','th'],recursive=False)]
  if len(cells)<12 or not cells[0].strip().isdigit():
   continue
  block=block_key(cells[1])
  if block not in expected:
   continue
  def count(value):
   digits=re.sub(r'[,\s]','',value)
   if not digits.isdigit():
    raise ValueError('Invalid R6.13 summary count for '+cells[1]+': '+value)
   return int(digits)
  item=dict(janpad=cells[1],incomplete=count(cells[2]),band75to100=count(cells[10]),above100=count(cells[11]))
  if block in rows and rows[block]!=item:
   raise ValueError('Conflicting official R6.13 rows for '+cells[1])
  rows[block]=item
 if set(rows)!=expected:
  raise ValueError('Official R6.13 summary incomplete: found '+str(len(rows))+'/8 Satna Janpads')
 return list(rows.values())

def main():
 official=official_summary(R613_URLS[0]);vbg=official_summary(R613_URLS[1])
 raw=[]
 for status,label in [('03','Ongoing'),('04','Suspended'),('06','Physically Completed')]:raw.extend(fetch_source(NREGA_URL,status,label))
 master=list(csv.DictReader((ROOT/'gp-sector-engineer-master-25-09-2026.csv').open(encoding='utf-8-sig')));mapping={}
 for m in master:
  for k in ['Gram_Panchayat','GP_20Sep_Name']:mapping[(block_key(m['Janpad']),norm(m[k]))]=m
 def number(r,k):
  v=float(str(r.get(k,'')).replace(',','').strip())
  if not math.isfinite(v) or v<0:raise ValueError('Invalid amount '+k)
  return v
 rows=[];seen=set()
 for a in raw:
  code=a['Work Code'].strip()
  if code in seen:raise ValueError('Duplicate work code '+code)
  seen.add(code);san=number(a,'Total Sanction (Rs)');paid=number(a,'paidWages')+number(a,'paidMaterial')
  m=mapping.get((block_key(a['Janpad / Block Name']),norm(a['Panchayat Name'])))
  if not m:raise ValueError('Missing GP mapping '+a['Janpad / Block Name']+' / '+a['Panchayat Name'])
  rows.append(dict(code=code,name=a['Work Name'],janpad=a['Janpad / Block Name'],panchayat=a['Panchayat Name'],cluster=m['Sector'],engineer=m['Sub_Engineer'],fy=a['Work Start Fin Year'],status=a['Work Status'],type=a['Work Type'],sanction=san,nregaBooked=paid,paidWages=number(a,'paidWages'),paidMaterial=number(a,'paidMaterial'),overallBooked=paid,overallExpPct=paid*100/san if san else None))
 validation=[]
 for o in official:
  rr=[r for r in rows if block_key(r['janpad'])==block_key(o['janpad']) and r['sanction']>0]
  band=sum(r['overallBooked']*100>r['sanction']*75 and r['overallBooked']*100<r['sanction']*99 for r in rr)
  above=sum(r['overallBooked']>r['sanction'] for r in rr)
  if band!=o['band75to100'] or above!=o['above100']:raise ValueError('R6.13 count mismatch '+o['janpad']+': detail '+str(band)+' / '+str(above)+' official '+str(o['band75to100'])+' / '+str(o['above100'])+'; previous report retained')
  validation.append(dict(janpad=o['janpad'],band=band,above100=above,ok=True))
 output=dict(schemaVersion=3,basis='r613-paid-validated',source='Official MGNREGA R6.13, reconciled to MIS paid since inception',fetchedAt=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),nregaCount=sum(r['incomplete'] for r in official),detailedCount=len(rows),officialSummary=official,vbgOfficialSummary=vbg,validation=validation,above75Count=sum(r['overallBooked']*100>r['sanction']*75 for r in rows if r['sanction']>0),bandCount=sum(r['band75to100'] for r in official),rows=rows)
 p=ROOT/'data/above75-latest.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(output,ensure_ascii=False),encoding='utf-8');os.replace(t,p)
 print('SUCCESS: R6.13 matched for all 8 Janpads. Official 75-100 band='+str(output['bandCount'])+'; above100='+str(sum(x['above100'] for x in official)),flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('FAILED: '+str(e),flush=True);sys.exit(1)
