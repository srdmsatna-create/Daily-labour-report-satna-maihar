"""e-MB pending ledger from official R4.4 details; rules: emb-lambit-logic.xlsx."""
import html,json,re,sys,urllib.parse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,date,timezone
from html.parser import HTMLParser
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT=Path(__file__).resolve().parents[1]
BLOCKS={'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}
R42_URL='https://vbgramgrep.dord.gov.in/VBGRAMG/state_html/emuster_wagelist_rpt.aspx?payload=ARG2d3cO8l846Lqa07xuwU5wIT2b7MwukTclsRltaLZVbLO_y7qRbwoXWJf150TXMYVbQXhpWiv4F1NFQdvtb55q2z9g0WLcP0HrbCuJZfgFz577TJQN2-JmSGNPqMe9tkbIhISp8z9s_IC7o8gSSlh96lWgUaeBZHislNQ_UVvm1e1NF8MP8zZ2olTYO6ytEBziiPKYHwyHoSxMR5pSDf3vJtNuwkh_YynSPVxUeZ0'
SCHEMA='emb-lambit-logic-v1'
_BROWSER=None
def clean(s):return re.sub(r'\s+',' ',str(s or '').replace('\xa0',' ')).strip()
def key(s):return clean(s).upper()
def read_js(p):return json.loads(p.read_text(encoding='utf-8-sig').split('=',1)[1].strip().rstrip(';'))

class Rows(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.rows=[];self.row=None;self.cell=None
 def handle_starttag(self,t,a):
  if t=='tr':self.row=[]
  elif t in ('td','th') and self.row is not None:self.cell={'text':'','links':[]}
  elif t=='a' and self.cell is not None:
   h=dict(a).get('href','')
   if h and not h.startswith(('javascript:','#')):self.cell['links'].append(h)
  elif t=='br' and self.cell is not None:self.cell['text']+=' '
 def handle_data(self,s):
  if self.cell is not None:self.cell['text']+=s
 def handle_endtag(self,t):
  if t in ('td','th') and self.cell is not None and self.row is not None:
   self.cell['text']=clean(self.cell['text']);self.row.append(self.cell);self.cell=None
  elif t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
def rows(s):p=Rows();p.feed(s);p.close();return p.rows
def get(url):
 if _BROWSER is None:raise RuntimeError('Local Chrome report reader has not started')
 s,base=_BROWSER.get(url)
 if re.search(r'__doPostBack\([^)]*Page\$|Page\$\d+',s,re.I):raise ValueError('Paginated source requires complete export; counts withheld')
 return rows(s),base
def block_links(rr,base):
 out={}
 for r in rr:
  if len(r)>1 and key(r[1]['text']) in BLOCKS and r[1]['links']:out[key(r[1]['text'])]=urllib.parse.urljoin(base,r[1]['links'][0])
 if set(out)!=BLOCKS:raise ValueError('All eight official Janpad links required')
 return out
def count(s):
 s=s.replace(',','')
 if not re.fullmatch(r'\d+',s):raise ValueError('Invalid official count')
 return int(s)
def zero_mrs(rr,expected):
 for i,r in enumerate(rr):
  hits=[j for j,c in enumerate(r) if re.fullmatch(r'(?:e[- ]?)?muster\s*(?:roll)?\s*(?:no\.?|number)|MR\s*(?:no\.?|number)',c['text'],re.I)]
  if len(hits)!=1:continue
  ci=hits[0];out=set()
  for r in rr[i+1:]:
   if len(r)<=ci:continue
   v=clean(r[ci]['text'])
   if re.fullmatch(r'\d+(?:[/-]\d+)*',v):out.add(v)
  if len(out)==expected:return out
 raise ValueError('Zero Attendance detail count/header mismatch')
def load_zero_attendance():
 root,base=get(R42_URL);links=block_links(root,base);tasks=[];gpseen=set()
 for block,url in links.items():
  rr,base=get(url)
  for r in rr:
   if len(r)<10 or not r[0]['text'].isdigit() or r[1]['text'].isdigit() or key(r[1]['text'])=='TOTAL':continue
   gp=key(r[1]['text']);gpseen.add((block,gp))
   for ci in (5,9):
    n=count(r[ci]['text'])
    if n:
     if len(r[ci]['links'])!=1:raise ValueError('Missing Zero Attendance link: '+block+' '+gp)
     tasks.append((block,gp,urllib.parse.urljoin(base,r[ci]['links'][0]),n))
 def one(t):
  b,g,u,n=t;rr,_=get(u);return {(b,g,mr) for mr in zero_mrs(rr,n)}
 result=set()
 with ThreadPoolExecutor(max_workers=5) as pool:
  for part in pool.map(one,tasks):result.update(part)
 return result,gpseen
def pending_rows(rr,block,gp,zero,today):
 out={};invalid=0
 for r in rr:
  if len(r)<6:continue
  c=[x['text'] for x in r];code=c[1]
  if not re.fullmatch(r'\d+/[A-Za-z]+/\d+',code):continue
  name,mr,raw,measured=c[2:6]
  if not mr:raise ValueError('MR number missing')
  if re.search(r'IAY|PMAY',code+' '+name,re.I):continue
  if (block,key(gp),mr) in zero or measured:continue
  try:ended=datetime.strptime(raw,'%d/%m/%Y').date()
  except ValueError:
   try:ended=datetime.strptime(raw,'%d-%m-%Y').date()
   except ValueError:invalid+=1;continue
  age=(today-ended).days
  if age<5:continue
  k=(code,mr,ended.isoformat());v={'code':code,'name':name,'mr':mr,'mrDate':ended.isoformat(),'days':age}
  if k in out and out[k]!=v:raise ValueError('Conflicting MR detail')
  out[k]=v
 return list(out.values()),invalid
def validate(d):
 if d.get('schemaVersion')!=SCHEMA or d.get('available') is not True or not d.get('zeroAttendanceVerified'):raise ValueError('Verified detail and Zero Attendance source required')
 if len(d.get('coverage',[]))!=8 or any(r['checked']+r['failed']!=r['expected'] for r in d['coverage']):raise ValueError('GP coverage arithmetic failed')
 if len({(r['block'],r['panchayat']) for r in d['gpRows']})!=len(d['gpRows']):raise ValueError('Duplicate GP')
 if sum(r['checked'] for r in d['coverage'])!=len(d['gpRows']) or sum(r['failed'] for r in d['coverage'])!=d['failedGP']:raise ValueError('GP coverage total mismatch')
 for r in d['gpRows']:
  if r['pending']!=len(r['details']) or any(v['days']<5 for v in r['details']):raise ValueError('Invalid pending details')
 if d['totalPending']!=sum(r['pending'] for r in d['gpRows']):raise ValueError('Summary mismatch')
def main():
 mapping=read_js(ROOT/'muster-emb-data.js');gpmap={(key(r['block']),key(r['panchayat'])):r for r in mapping['gpRows']}
 if len(gpmap)!=695:raise ValueError('695 GP mappings required')
 root,base=get(mapping['source']);links=block_links(root,base)
 jobs=[];coverage=[]
 for b,url in links.items():
  rr,base=get(url);seen=set()
  for r in rr:
   if len(r)<2 or not r[0]['text'].isdigit() or r[1]['text'].isdigit():continue
   gp=key(r[1]['text'])
   if (b,gp) not in gpmap:continue
   detail={urllib.parse.urljoin(base,u) for c in r for u in c['links'] if 'MusterRolle_EMBStatus_dtl.aspx' in u}
   if len(detail)!=1:raise ValueError('Exactly one GP detail link required: '+b+' '+gp)
   seen.add(gp);jobs.append((b,gp,detail.pop()))
  # Portal omits unissued GPs; still require every GP with issued MRs.
  required={g for (j,g),r in gpmap.items() if j==b and r['issued']>0}
  if not required.issubset(seen):raise ValueError('Issued GP details missing: '+b)
  coverage.append({'block':b,'expected':len(seen),'checked':0,'failed':0})
 zero,zerogps=load_zero_attendance();today=datetime.now(ZoneInfo('Asia/Kolkata')).date()
 def one(t):
  b,g,u=t
  if (b,g) not in zerogps:raise ValueError('Zero Attendance GP coverage missing: '+b+' '+g)
  rr,_=get(u)
  headers=' '.join(c['text'] for r in rr for c in r if len(r)>=6 and not any('/' in x['text'] and re.match(r'\d+/',x['text']) for x in r))
  if not re.search(r'muster|\bMR\b',headers,re.I) or not re.search(r'measure|e.?mb|माप',headers,re.I):raise ValueError('GP detail header missing; not counted as zero')
  details,invalid=pending_rows(rr,b,g,zero,today);m=gpmap[(b,g)]
  return {'block':b,'district':'MAIHAR' if b in {'AMARPATAN','MAIHAR','RAMNAGAR'} else 'SATNA','panchayat':g,'engineer':m.get('engineer') if m.get('engineer') not in (None,'','Unmapped') else '—','cluster':m.get('cluster') or '—','pending':len(details),'details':details,'invalidDates':invalid}
 result=[];failures=[]
 with ThreadPoolExecutor(max_workers=5) as pool:
  fs=[(t,pool.submit(one,t)) for t in jobs]
  for t,f in fs:
   try:result.append(f.result());next(c for c in coverage if c['block']==t[0])['checked']+=1
   except Exception as e:failures.append({'block':t[0],'panchayat':t[1],'engineer':gpmap[(t[0],t[1])].get('engineer') or '—','district':'MAIHAR' if t[0] in {'AMARPATAN','MAIHAR','RAMNAGAR'} else 'SATNA','reason':str(e)});next(c for c in coverage if c['block']==t[0])['failed']+=1
 if not result:raise ValueError('No GP detail could be read; previous report retained')
 d={'schemaVersion':SCHEMA,'available':True,'source':mapping['source'],'zeroSource':R42_URL,'sourceDate':None,'fetchedAt':datetime.now(timezone.utc).isoformat(),'thresholdDays':5,'zeroAttendanceVerified':True,'zeroCount':len(zero),'coverage':coverage,'gpRows':result,'totalPending':sum(r['pending'] for r in result),'checkedGP':len(result),'affectedGP':sum(r['pending']>0 for r in result),'failedGP':len(failures),'failedPages':failures}
 validate(d);p=ROOT/'data/emb-pending-latest.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(p)
 print('Verified pending e-MB:',len(result),'GPs;',d['totalPending'],'MRs',flush=True)
if __name__=='__main__':
 from emb_browser_reader import BrowserReader
 result=0
 try:
  _BROWSER=BrowserReader()
  print('Local Chrome: reading R4.4 GP details and R4.2 Zero Attendance; five pages at a time.',flush=True)
  # Open the user's R4.2 landing page in the same ordinary persistent session.
  _BROWSER.get(R42_URL)
  main()
 except Exception as e:print('FAILED: pending e-MB retained:',e,flush=True);result=1
 finally:
  if _BROWSER is not None:_BROWSER.close()
 sys.exit(result)
