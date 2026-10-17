"""Fetch Ek Bagiya Booked/Paid amounts from both official work reports."""
import html,json,re,urllib.parse,urllib.error,unicodedata,csv,time,socket,http.client
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
from pathlib import Path
import update_mis_612_work_details as mis
ROOT=Path(__file__).resolve().parents[1]
JANPADS=['AMARPATAN','MAIHAR','RAMNAGAR','MAJHGAWAN','NAGOD','RAMPUR BAGHELAN','SATNA','UNCHAHARA']
def cells(source):
 for row in re.findall(r'<tr\b[^>]*>(.*?)</tr>',source,re.S|re.I):
  c=[html.unescape(re.sub('<[^>]+>',' ',v)).strip() for v in re.findall(r'<t[hd]\b[^>]*>(.*?)</t[hd]>',row,re.S|re.I)]
  if len(c)>=32 and c[0].isdigit() and c[1]=='SATNA' and '/' in c[6]:yield c
def fetch_once(url,block="ALL",fy="ALL"):
 opener=mis.session_opener()
 source,base=mis.open_text(opener,url,timeout=90)
 fields=mis.hidden_fields(source);mis.selected_values(source,fields)
 fields.update({'__EVENTTARGET':'ctl00$ContentPlaceHolder1$ddl_dist','ctl00$ContentPlaceHolder1$ddl_state':'17','ctl00$ContentPlaceHolder1$ddl_dist':'1712'})
 source,base=mis.open_text(opener,mis.form_action(source,base),urllib.parse.urlencode(fields).encode(),timeout=90)
 if 'value="1712006"' not in source:raise ValueError('Official SATNA Janpad options missing')
 fields=mis.hidden_fields(source);mis.selected_values(source,fields)
 fields.update({'__EVENTTARGET':'','ctl00$ContentPlaceHolder1$ddl_blk':block,'ctl00$ContentPlaceHolder1$ddl_pan':'ALL','ctl00$ContentPlaceHolder1$ddlFin_year':fy,'ctl00$ContentPlaceHolder1$Ddlworkcategory':'IF','ctl00$ContentPlaceHolder1$Ddlwork_status':'ALL','ctl00$ContentPlaceHolder1$Button1':'Submit'})
 source,_=mis.open_text(opener,mis.form_action(source,base),urllib.parse.urlencode(fields).encode(),timeout=480)
 if not re.search('Amount paid since inception',source,re.I):raise ValueError('Official payment columns missing')
 rows=list(cells(source))
 if not rows:raise ValueError('Empty official source')
 if block=='ALL' and set(r[2] for r in rows)!=set(JANPADS):raise ValueError('Incomplete eight-Janpad source')
 date=re.search(r'Report last Updated on:\s*(\d{2}/\d{2}/\d{4})',source)
 return rows,date.group(1) if date else None
def fetch(url,block="ALL",fy="ALL"):
 # Retry the complete read-only form flow, not just a POST with stale
 # viewstate/cookies after the remote server resets the connection.
 for attempt in range(3):
  try:return fetch_once(url,block,fy)
  except (ConnectionError,TimeoutError,socket.timeout,urllib.error.URLError,http.client.HTTPException) as exc:
   if isinstance(exc,urllib.error.HTTPError) and exc.code not in (408,429,500,502,503,504):raise
   if attempt==2:raise RuntimeError(f'Payment source transport failed after 3 fresh sessions: block={block}, FY={fy}: {exc}') from exc
   print(f'Retrying payment source with fresh session ({attempt+2}/3), block={block}, FY={fy}: {exc}',flush=True)
   time.sleep(2*(attempt+1))

def number(value):
 value=value.replace(',','').strip()
 if not re.fullmatch(r'\d+(?:\.\d+)?',value):raise ValueError('Missing/invalid official amount')
 return float(value)
def scheme_codes(root=ROOT):
 with (root/'ek-bagiya/work_details.csv').open(encoding='utf-8-sig',newline='') as f:return {r['Work Code'].strip() for r in csv.DictReader(f) if r.get('Work Code')}
def is_bagiya(name,code,known):
 name=unicodedata.normalize('NFKD',name).replace('\u093c','')
 return code in known or bool(re.search(r'ब[ा]?ग[िी]य[ा]?|b(?:a|ai)[gk]i?(?:y|i)a',name,re.I))
ALLOWED_FYS={'2025-2026','2026-2027'}
PORTAL_FYS={'MGNREGA':('2025-2026','2026-2027'),'VBGRAMG':('2025-2026','2026-2027',)}
# Official R-6.12 columns: Booked current FY 17/18; Paid since inception 23/24.
PAYMENT_COLUMNS={'bw':17,'bm':18,'pw':23,'pm':24,'bsw':21,'bsm':22}
LOGIC_VERSION='sabhi-reports-logic-v1'
def ledger_amounts(c,system):
 # User workbook: NREGA inception columns; VBG uses the larger of current/inception.
 raw={str(i):number(c[i-1]) for i in range(17,27)}
 amounts={k:raw[str(column)] for k,column in PAYMENT_COLUMNS.items()}
 if system=='VBGRAMG':
  for key,current in [('bsw',17),('bsm',18),('pw',19),('pm',20)]:
   amounts[key]=max(amounts[key],raw[str(current)])
 return amounts,raw
def work_fy(value):
 value=value.strip().replace('/','-')
 return {'2025-26':'2025-2026','2026-27':'2026-2027'}.get(value,value)
def build(vbg,nrega,dates,urls,known=None):
 if known is None:known=scheme_codes()
 vbg=[c for c in vbg if work_fy(c[4]) in PORTAL_FYS['VBGRAMG']]
 nrega=[c for c in nrega if work_fy(c[4]) in ALLOWED_FYS]
 # Both work-start FYs are needed on both portals; the VBG ledger covers July onward.
 # Merge by work code, retaining one ledger per portal without requiring equal sets.
 master={}
 for system,rr in [('MGNREGA',nrega),('VBGRAMG',vbg)]:
  seen={}
  for c in rr:
   if not is_bagiya(c[7],c[6],known) or c[5].lower()=='deleted':continue
   code=c[6]
   if code in seen:
    if seen[code]!=c:raise ValueError('Conflicting duplicate official work code')
    continue
   seen[code]=c
   x=master.setdefault(code,{'code':code,'janpad':c[2],'name':c[7],'status':c[5],'sw':0,'sm':0,'bw':0,'bm':0,'pw':0,'pm':0,'bsw':0,'bsm':0,'sources':{},'panchayat':c[3],'financialYear':work_fy(c[4]),'nregaTotalMandays':0,'nregaAprJunMandays':0,'julyMandays':0})
   if x['janpad']!=c[2] or x['financialYear']!=work_fy(c[4]):raise ValueError('Work Janpad/FY mismatch')
   if system=='VBGRAMG':x['status']=c[5];x['julyMandays']=number(c[25])
   else:
    x['nregaTotalMandays']=number(c[24]);x['nregaAprJunMandays']=number(c[25])
    if x['nregaAprJunMandays']>x['nregaTotalMandays']:raise ValueError('NREGA manday periods invalid')
   x['sw']=max(x['sw'],number(c[13]));x['sm']=max(x['sm'],number(c[14]))
   amounts,raw=ledger_amounts(c,system)
   x['sources'][system]={**amounts,'rawColumns':raw,'mandaysTotal':number(c[24]),'mandaysCurrentFY':number(c[25]),'workFinancialYear':work_fy(c[4])}
   for k,v in amounts.items():x[k]+=v
 if not master:raise ValueError('No Ek Bagiya work details')
 for w in master.values():
  if w['pw']>w['bsw']+0.01 or w['pm']>w['bsm']+0.01:raise ValueError('Paid exceeds since-inception Booked: '+w['code'])
 summary=[]
 for j in JANPADS:
  works=[w for w in master.values() if w['janpad']==j and w['status'].lower() not in ('new','deleted')]
  if not works:raise ValueError('No sanctioned works for '+j)
  financial_works=[w for w in works if w['status'].lower() in ('ongoing','physically completed','completed')]
  summary.append(dict(janpad=j,works=len(works),ongoing=sum(w['status'].lower()=='ongoing' for w in works),financialWorks=len(financial_works),**{k:sum(w[k] for w in (works if k in ('sw','sm') else financial_works))/100000 for k in ('sw','sm','bw','bm','pw','pm','bsw','bsm')}))
 now=datetime.now(ZoneInfo('Asia/Kolkata'))
 return {'source':urls,'sourceDates':dates,'sourceDate':min(dates.values(),key=lambda d:datetime.strptime(d,'%d/%m/%Y')),'retrievedDate':now.strftime('%d/%m/%Y'),'checkedAt':datetime.now(timezone.utc).isoformat(),'rows':summary,'workCount':len(master),'works':list(master.values()),'financialBasis':'Sanction includes all unique approved/ongoing/completed/closed works, excluding New and Deleted. Booked/Paid includes ongoing and completed works.','financialYears':sorted(ALLOWED_FYS),'sourceFinancialYears':{k:list(v) for k,v in PORTAL_FYS.items()},'r612Columns':PAYMENT_COLUMNS,'pendingBasis':'Since-inception booked minus since-inception paid: Wages col21-col23; Material col22-col24','bookedBasis':'Amount Booked in current Fin Year (columns 17/18)','paidBasis':'Amount paid since inception (columns 23/24)','deduplication':'One work per code; one ledger entry per code per portal; NREGA and VBGRAMG Booked/Paid ledger amounts added; sanction counted once','basis':'Verified master work codes plus normalized Hindi/English scheme spelling variants; sanctioned excludes New; Booked/Paid is MGNREGA plus VBGRAMG'}
def attach_mapping(d,root=ROOT):
 text=(root/'shramik-niyojan-data.js').read_text(encoding='utf-8-sig')
 mapping=json.loads(text.split('=',1)[1].strip().rstrip(';'))
 key=lambda j,p:(' '.join(j.upper().split()),' '.join(p.upper().split()))
 gps={key(r['janpad'],r['panchayat']):r for r in mapping['gpMandaysRows']}
 if len(gps)!=695:raise ValueError('Complete GP engineer/cluster mapping required')
 for w in d['works']:
  gp=gps.get(key(w['janpad'],w['panchayat']))
  if not gp or not gp.get('engineer') or not gp.get('cluster'):raise ValueError('Missing work GP mapping: '+w['code'])
  w.update(engineer=gp['engineer'],cluster=gp['cluster'],district=gp['district'])
 d['mappingDate']=mapping['officialDate']
 return d
def main():
 urls={'VBGRAMG':mis.URL,'MGNREGA':mis.URL.replace('https://vbgramgrep.dord.gov.in/VBGRAMG/','https://mnregaweb4.dord.gov.in/netnregarep/')}
 # This dropdown is Work Start FY, not the financial period of the VBG ledger.
 # Fetch both allowed work-start years so old works with July-onward activity survive.
 vbg,vd=fetch(urls['VBGRAMG'],fy='ALL');print('VBGRAMG source fetched (all work-start FYs)',flush=True)
 blocks={'AMARPATAN':'1712006','MAIHAR':'1712008','MAJHGAWAN':'1712001','NAGOD':'1712003','RAMNAGAR':'1712007','RAMPUR BAGHELAN':'1712005','SATNA':'1712002','UNCHAHARA':'1712004'}
 tasks=[(j,c,fy) for j,c in blocks.items() for fy in PORTAL_FYS['MGNREGA']]
 def read(task):
  j,c,fy=task;rr,date=fetch(urls['MGNREGA'],c,fy)
  if {r[2] for r in rr}!={j}:raise ValueError('NREGA Janpad mismatch')
  return rr,date
 with ThreadPoolExecutor(max_workers=4) as pool:results=list(pool.map(read,tasks))
 dates={date for _,date in results}
 if len(dates)!=1 or None in dates:raise ValueError('NREGA source dates incomplete/inconsistent')
 nrega=[r for rr,_ in results for r in rr];nd=dates.pop();print('MGNREGA source fetched',flush=True)
 if not vd:raise ValueError('VBGRAMG official source date missing')
 d=attach_mapping(build(vbg,nrega,{'VBGRAMG':vd,'MGNREGA':nd},urls))
 d.update(logicVersion=LOGIC_VERSION,logicSource='sabhi-reports-logic.xlsx',bookedBasis='MGNREGA columns 21/22 + VBGRAMG max(21,17)/max(22,18)',paidBasis='MGNREGA columns 23/24 + VBGRAMG max(23,19)/max(24,20)',pendingBasis='Combined Booked minus Combined Paid, separately for Wage and Material',sourceFinancialYears={'MGNREGA':['2025-2026','2026-2027'],'VBGRAMG':['2025-2026','2026-2027']},reportFinancialYears={'VBGRAMG':'2026-2027'})
 path=ROOT/'data/ek-bagiya-payment-latest.json';path.parent.mkdir(exist_ok=True)
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)
 print('Verified current payment snapshot: eight Janpads')
if __name__=='__main__':main()
