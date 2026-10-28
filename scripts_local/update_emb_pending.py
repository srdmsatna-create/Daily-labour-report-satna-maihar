"""e-MB pending ledger from official R4.4 details; rules: emb-lambit-logic.xlsx."""
import gzip,html,json,re,sys,time,urllib.parse
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
def zero_mrs(rr,expected,allow_detail_count=False):
 # Match semantic headers despite punctuation, line breaks and abbreviations.
 # Never guess a numeric column when the report header cannot be identified.
 observed=[]
 for i,r in enumerate(rr):
  hits=[]
  for j,c in enumerate(r):
   label=re.sub(r'[^a-z0-9]','',c['text'].lower())
   if re.fullmatch(r'(?:e)?(?:muster(?:roll)?|mr)(?:no|number)(?:s)?',label):hits.append(j)
  if len(hits)!=1:continue
  ci=hits[0];out=set();works=set();serials=[];identities=set()
  for detail in rr[i+1:]:
   # Official detail records have a numeric serial; ignore totals, legends
   # and the numeric column-number row immediately below the header.
   if len(detail)<=ci or not detail or not detail[0]['text'].isdigit():continue
   if len(detail)>2 and all(re.fullmatch(r'\d+',c['text']) for c in detail):continue
   v=clean(detail[ci]['text'])
   if not re.fullmatch(r'\d+(?:[/-]\d+)*',v):raise ValueError('Invalid Zero Attendance MR record')
   if re.fullmatch(r'\d+(?:[/-]\d+)*',v):
    source=' '.join(c['text']+' '+' '.join(c['links']) for c in detail)
    source=re.sub(r'\s*/\s*','/',urllib.parse.unquote(source))
    codes=set(re.findall(r'\d+/[A-Za-z]+/\d+',source))
    if len(codes)>1:raise ValueError('Zero Attendance work identity ambiguous: '+source[:400])
    code=next(iter(codes),None);identity=(code,v)
    if identity in identities:raise ValueError('Repeated Zero Attendance detail record')
    identities.add(identity);serials.append(int(detail[0]['text']));out.add((code,v))
    if code is not None:works.add(code)
  observed.append(len(out))
  if serials!=list(range(1,len(serials)+1)):raise ValueError('Incomplete Zero Attendance detail serials')
  # R4.2 summary links can count works, while their detail lists MRs.
  # Reconcile either unit using complete, identified detail records.
  if len(out)==expected or (out and all(code is not None for code,mr in out) and len(works)==expected):
   if len(out)!=expected:print(f'Zero Attendance reconciled: {expected} works / {len(out)} MRs',flush=True)
   return out
  # After fresh-parent retries, complete identified MR details are authoritative.
  # The portal summary can lag behind details in more than one GP.
  if allow_detail_count and out and all(code is not None for code,mr in out):
   print(f'Zero Attendance detail accepted: summary={expected}; verified detail={len(out)} MRs',flush=True)
   return out
 raise ValueError(f'Zero Attendance detail count/header mismatch: expected={expected}; observed={observed}; headers='+repr([[c['text'] for c in r] for r in rr[:8]]))

def zero_tasks(rr,base,block):
 tasks=[];gpseen=set()
 for r in rr:
  if len(r)<10 or not r[0]['text'].isdigit() or r[1]['text'].isdigit() or key(r[1]['text'])=='TOTAL':continue
  gp=key(r[1]['text']);gpseen.add((block,gp))
  for ci in (5,9):
   n=count(r[ci]['text'])
   if n:
    if len(r[ci]['links'])!=1:raise ValueError('Missing Zero Attendance link: '+block+' '+gp)
    tasks.append((block,gp,urllib.parse.urljoin(base,r[ci]['links'][0]),n,ci))
 return tasks,gpseen

def load_zero_attendance():
 root,base=get(R42_URL);links=block_links(root,base);tasks=[];gpseen=set()
 for block,url in links.items():
  rr,base=get(url);part,seen=zero_tasks(rr,base,block)
  tasks.extend(part);gpseen.update(seen)
 def one(t):
  b,g,u,n,ci=t
  for attempt in range(3):
   try:
    if attempt:
     # Refresh the parent too: counts and detail links can change mid-run.
     parent,pbase=get(links[b]);fresh,_=zero_tasks(parent,pbase,b)
     matches=[x for x in fresh if x[1]==g and x[4]==ci]
     if not matches:
      if (b,g) not in zero_tasks(parent,pbase,b)[1]:raise ValueError('GP missing from refreshed summary')
      return set()
     if len(matches)!=1:raise ValueError('Duplicate Zero Attendance GP summary')
     _,_,u,n,_=matches[0]
    rr,_=get(u)
    # Reject detail links that resolve to a different block or panchayat.
    for i,row in enumerate(rr):
     labels=[re.sub(r'[^a-z]','',c['text'].lower()) for c in row]
     if 'block' in labels and 'gp' in labels:
      bi,gi=labels.index('block'),labels.index('gp')
      for detail in rr[i+1:]:
       if detail and detail[0]['text'].isdigit() and len(detail)>max(bi,gi):
        if all(c['text'].isdigit() for c in detail):continue
        if key(detail[bi]['text']).replace(' ','')!=b.replace(' ','') or key(detail[gi]['text'])!=g:
         raise ValueError('Zero Attendance detail belongs to a different GP')
    return {(b,g,code,mr) for code,mr in zero_mrs(rr,n,allow_detail_count=(attempt==2))}
   except Exception as exc:
    if attempt==2:raise ValueError(f'{b}/{g} Zero Attendance column {ci+1}: {exc}') from exc
    print(f'Retrying Zero Attendance {b}/{g} ({attempt+2}/3): {exc}',flush=True)
    time.sleep(2*(attempt+1))
 result=set()
 with ThreadPoolExecutor(max_workers=3) as pool:
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
  if (block,key(gp),code,mr) in zero or (block,key(gp),None,mr) in zero or measured:continue
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
 if d.get('schemaVersion')!=SCHEMA or d.get('available') is not True or not d.get('paymentPendingVerified'):raise ValueError('Verified payment-pending source required')
 if len(d.get('coverage',[]))!=8 or any(r['checked']+r['failed']!=r['expected'] for r in d['coverage']):raise ValueError('GP coverage arithmetic failed')
 if len({(r['block'],r['panchayat']) for r in d['gpRows']})!=len(d['gpRows']):raise ValueError('Duplicate GP')
 if sum(r['checked'] for r in d['coverage'])!=len(d['gpRows']) or sum(r['failed'] for r in d['coverage'])!=d['failedGP']:raise ValueError('GP coverage total mismatch')
 for r in d['gpRows']:
  if r['pending']!=len(r['details']):raise ValueError('Payment-pending detail count mismatch')
  if len({(v['code'],v['mr']) for v in r['details']})!=r['pending']:raise ValueError('Duplicate payment-pending MR')
 if d['totalPending']!=sum(r['pending'] for r in d['gpRows']):raise ValueError('Summary mismatch')
def read_gp_jobs(jobs,one,restart=None):
 # Preserve successful GP reads. Retry just unavailable pages, with fewer
 # parallel tabs after a timeout/crash, and a fresh browser session.
 pending=list(jobs);result=[];failures=[]
 for attempt in range(3):
  failures=[]
  if attempt:
   print(f'Recovering {len(pending)} unread GPs, attempt {attempt+1}/3',flush=True)
   if restart:restart()
  with ThreadPoolExecutor(max_workers=3 if attempt==0 else 2) as pool:
   fs=[(t,pool.submit(one,t)) for t in pending]
   for t,f in fs:
    try:result.append(f.result())
    except Exception as exc:failures.append((t,exc))
  if not failures:break
  pending=[t for t,_ in failures]
 return result,failures

def main():
 mapping=read_js(ROOT/'muster-emb-data.js')
 gpmap={(key(r['block']),key(r['panchayat'])):r for r in mapping['gpRows']}
 if len(gpmap)!=695:raise ValueError('695 GP mappings required')
 payment=json.loads((ROOT/'data/pending-mr-fto.json').read_text(encoding='utf-8-sig'))
 if payment.get('sourceMode')!='payment-pending' or payment.get('filterVerified') is not True:raise ValueError('Verified S5.26 Pending for Payment filter required')
 stage=payment.get('reports',{}).get('mr',{})
 if not stage.get('available') or set(stage.get('coverage',[]))!=BLOCKS:raise ValueError('All eight payment-pending block reports required')
 details_path=ROOT/payment.get('detailsFile','')
 if not details_path.is_file():raise ValueError('Payment-pending detail file missing')
 payment_rows=json.loads(gzip.decompress(details_path.read_bytes()))
 if len(payment_rows)!=payment.get('detailCount'):raise ValueError('Payment-pending detail count mismatch')
 by_gp={}
 for row in payment_rows:
  block=key(row.get('block'));gp=key(row.get('panchayat'))
  if (block,gp) not in gpmap:raise ValueError('Payment-pending GP mapping missing: '+block+'/'+gp)
  code=clean(row.get('workCode'));mr=clean(row.get('mr'))
  if not re.fullmatch(r'\d+/\S+',code) or not mr:raise ValueError('Payment-pending MR identity incomplete: '+block+'/'+gp)
  bucket=by_gp.setdefault((block,gp),{});identity=(code,mr)
  detail={'code':code,'name':'Pending for Payment','mr':mr,'mrDate':clean(row.get('closureDate')),'days':0,'status':'Pending for Payment','firstPending':bool(row.get('firstPending')),'secondPending':bool(row.get('secondPending'))}
  for fmt in ('%d/%m/%Y','%d-%m-%Y'):
   try:
    detail['days']=max(0,(datetime.now(ZoneInfo('Asia/Kolkata')).date()-datetime.strptime(detail['mrDate'],fmt).date()).days);break
   except ValueError:pass
  old=bucket.get(identity)
  if old:
   old['firstPending']=old['firstPending'] or detail['firstPending'];old['secondPending']=old['secondPending'] or detail['secondPending']
  else:bucket[identity]=detail
 gpRows=[];coverage=[]
 for block in sorted(BLOCKS):
  gps=sorted(g for (b,g) in gpmap if b==block)
  for gp in gps:
   m=gpmap[(block,gp)];vals=list(by_gp.get((block,gp),{}).values())
   gpRows.append({'block':block,'district':'MAIHAR' if block in {'AMARPATAN','MAIHAR','RAMNAGAR'} else 'SATNA','panchayat':gp,'engineer':m.get('engineer') if m.get('engineer') not in (None,'','Unmapped') else '—','cluster':m.get('cluster') or '—','pending':len(vals),'details':vals,'invalidDates':0})
  n=len(gps);coverage.append({'block':block,'expected':n,'checked':n,'failed':0})
 d={'schemaVersion':SCHEMA,'available':True,'source':stage['source'],'sourceDate':stage.get('sourceDate'),'fetchedAt':stage.get('fetchedAt') or datetime.now(timezone.utc).isoformat(),'thresholdDays':0,'paymentPendingVerified':True,'sourceMode':'payment-pending','coverage':coverage,'gpRows':gpRows,'totalPending':sum(r['pending'] for r in gpRows),'checkedGP':len(gpRows),'affectedGP':sum(r['pending']>0 for r in gpRows),'failedGP':0,'failedPages':[]}
 validate(d);p=ROOT/'data/emb-pending-latest.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8');tmp.replace(p)
 print('Verified Pending for Payment:',len(gpRows),'GPs;',d['totalPending'],'distinct MRs',flush=True)
if __name__=='__main__':
 result=0
 try:main()
 except Exception as e:print('FAILED: Pending for Payment e-MB count retained:',e,flush=True);result=1
 sys.exit(result)
