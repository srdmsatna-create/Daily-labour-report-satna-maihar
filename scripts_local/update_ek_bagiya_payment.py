"""Fetch Ek Bagiya Booked/Paid amounts from both official work reports."""
import html,json,re,urllib.parse
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
def fetch(url,block="ALL",fy="ALL"):
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
def number(value):
 value=value.replace(',','').strip()
 if not re.fullmatch(r'\d+(?:\.\d+)?',value):raise ValueError('Missing/invalid official amount')
 return float(value)
def build(vbg,nrega,dates,urls):
 master={}
 for system,rr in [('MGNREGA',nrega),('VBGRAMG',vbg)]:
  seen=set()
  for c in rr:
   if not re.search(r'बगिया|bagiya|bagia',c[7],re.I) or c[5].lower()=='deleted':continue
   code=c[6]
   if code in seen:raise ValueError('Duplicate official work code')
   seen.add(code)
   x=master.setdefault(code,{'code':code,'janpad':c[2],'name':c[7],'status':c[5],'sw':0,'sm':0,'bw':0,'bm':0,'pw':0,'pm':0,'sources':{},'panchayat':c[3],'nregaTotalMandays':0,'nregaAprJunMandays':0,'julyMandays':0})
   if x['janpad']!=c[2]:raise ValueError('Work Janpad mismatch')
   if system=='VBGRAMG':x['status']=c[5];x['julyMandays']=number(c[25])
   else:
    x['nregaTotalMandays']=number(c[24]);x['nregaAprJunMandays']=number(c[25])
    if x['nregaAprJunMandays']>x['nregaTotalMandays']:raise ValueError('NREGA manday periods invalid')
   x['sw']=max(x['sw'],number(c[13]));x['sm']=max(x['sm'],number(c[14]))
   amounts={k:number(c[i]) for k,i in [('bw',20),('bm',21),('pw',22),('pm',23)]}
   x['sources'][system]=amounts
   for k,v in amounts.items():x[k]+=v
 if not master:raise ValueError('No Ek Bagiya work details')
 summary=[]
 for j in JANPADS:
  works=[w for w in master.values() if w['janpad']==j and w['status'].lower() not in ('new','deleted')]
  if not works:raise ValueError('No sanctioned works for '+j)
  summary.append(dict(janpad=j,works=len(works),ongoing=sum(w['status'].lower()=='ongoing' for w in works),**{k:sum(w[k] for w in works)/100000 for k in ('sw','sm','bw','bm','pw','pm')}))
 now=datetime.now(ZoneInfo('Asia/Kolkata'))
 return {'source':urls,'sourceDates':dates,'sourceDate':min(dates.values(),key=lambda d:datetime.strptime(d,'%d/%m/%Y')),'retrievedDate':now.strftime('%d/%m/%Y'),'checkedAt':datetime.now(timezone.utc).isoformat(),'rows':summary,'workCount':len(master),'works':list(master.values()),'basis':'Unique non-deleted Ek Bagiya codes; sanctioned excludes New; Booked/Paid is MGNREGA plus VBGRAMG'}
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
 vbg,vd=fetch(urls['VBGRAMG']);print('VBGRAMG source fetched',flush=True)
 blocks={'AMARPATAN':'1712006','MAIHAR':'1712008','MAJHGAWAN':'1712001','NAGOD':'1712003','RAMNAGAR':'1712007','RAMPUR BAGHELAN':'1712005','SATNA':'1712002','UNCHAHARA':'1712004'}
 tasks=[(j,c,fy) for j,c in blocks.items() for fy in ('2025-2026','2026-2027')]
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
 path=ROOT/'data/ek-bagiya-payment-latest.json';path.parent.mkdir(exist_ok=True)
 temp=path.with_suffix('.tmp');temp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');temp.replace(path)
 print('Verified current payment snapshot: eight Janpads')
if __name__=='__main__':main()
