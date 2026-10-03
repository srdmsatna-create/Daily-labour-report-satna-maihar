"""Refresh 52 source districts from official monthly Persondays and R6.9 tables.
All rows must match the known source districts before a snapshot is replaced.
"""
import calendar,json,os,re,sys
from pathlib import Path
from datetime import datetime,timezone,timedelta
IST=timezone(timedelta(hours=5,minutes=30))
ROOT=Path(__file__).resolve().parent.parent
PERIOD='2025-26-Jul-Oct_vs_2026-27-Jul-Sep-Oct'
MONTHLY=os.environ.get('SHRAMIK_STATE_PERSONDAYS_URL') or 'https://vbgramgrep.dord.gov.in/VBGRAMG/demand_emp_demand.aspx?lflag=eng&file1=empprov&page1=s&state_name=MADHYA+PRADESH&state_code=17&fin=2026-2027&fin_year=2026-2027&source=national&Digest=T5jPevIAyKZwnVDL7xdTaQ'
LABOUR=os.environ.get('SHRAMIK_STATE_LABOUR_URL') or 'https://vbgramgrep.dord.gov.in/VBGRAMG/dpc_sms_new.aspx?payload=pjXZ1SaedD2l9B9KBeJqaVN_RZ3A4xihd5AKgmnsi85zIicpn5VAaJjaVi1eyMSA4Rlaxhzi-y8Nxu99z2MmCuw0B7eyqCRquSyQRCwScdayNxCiEkbk4W8l6QZhleaZxwCujblVHncKsfyQwBtvAUbxByEFyryl_xK6THoQe42vJTXALX5P42nO1Z3TPDar7HRzJswuZMYsV3EdFAU1Ww'
MONTHS=('april','may','june','july','august','september','october','november','december','january','february','march')
def norm(v):return re.sub(r'\s+',' ',str(v).strip()).upper().replace('HOSHANGABAD','NARMADAPURAM').replace('ASHOKNAGAR','ASHOK NAGAR')
def number(v):
 s=re.sub(r'[\s,]','',str(v))
 if not re.fullmatch(r'\d+(?:\.0+)?',s):raise ValueError('Non-numeric official monthly cell: '+str(v)[:60])
 return int(float(s))
def write_js(path,name,payload):
 tmp=path.with_suffix(path.suffix+'.tmp');tmp.write_text(name+'='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8');os.replace(tmp,path)
def read_js(path):return json.loads(path.read_text(encoding='utf-8-sig').split('=',1)[1].strip().rstrip(';'))
def parse_monthly(tables,names):
 candidates=[]
 for table in tables:
  out={}
  for row in table:
   for i,c in enumerate(row):
    name=norm(c)
    if name not in names:continue
    if len(row[i+1:])<12:break
    try:values=[number(v) for v in row[i+1:i+13]]
    except ValueError:break
    if name in out and out[name]!=dict(zip(MONTHS,values)):raise RuntimeError('Conflicting monthly rows: '+name)
    out[name]=dict(zip(MONTHS,values));break
  if set(out)==set(names):candidates.append(out)
 if not candidates:raise RuntimeError('Complete 52-district April-March Persondays table not found')
 if any(x!=candidates[0] for x in candidates):raise RuntimeError('Ambiguous state monthly tables')
 return candidates[0]
def parse_labour(tables,names):
 # Header-based matching avoids treating No. of Muster Rolls as MR-issued works.
 fields={'totalGP':r'(?:total|no\.?\s*of|number\s*of)\s*(?:gram\s*panchayats?|gps)\b', 'labourGP':r'(?:gps|gram\s*panchayats?).*(?:labour|labor).*(?:engag|employ)|(?:labour|labor).*(?:engag|employ).*(?:gps|gram\s*panchayats?)', 'todayLabour':r'maximum.*(?:labour|labor).*engagement|today.*(?:labour|labor)', 'mrIssued':r'works.*(?:mr|muster).*issued', 'musterRollCount':r'(?:no\.?|number).*muster.*roll', 'ongoing':r'total.*(?:ongoing|progress).*works|total.*works.*(?:ongoing|progress)'}
 candidates=[]
 for table in tables:
  first=next((i for i,row in enumerate(table) if any(norm(c) in names for c in row)),None)
  if first is None:continue
  width=max(map(len,table),default=0)
  headers=[' '.join(dict.fromkeys(row[i] for row in table[:first] if i<len(row) and row[i])) for i in range(width)]
  cols={}
  for field,pattern in fields.items():
   hits=[i for i,h in enumerate(headers) if re.search(pattern,h,re.I)]
   if len(hits)==1:cols[field]=hits[0]
  if 'todayLabour' not in cols:continue
  out={}
  for row in table[first:]:
   match=[norm(c) for c in row if norm(c) in names]
   if len(match)!=1:continue
   try:out[match[0]]={k:number(row[i]) for k,i in cols.items()}
   except (ValueError,IndexError):continue
  if set(out)==set(names):candidates.append(out)
 if not candidates:raise RuntimeError('52-district R6.9 labour header or rows incomplete')
 if any(x!=candidates[0] for x in candidates):raise RuntimeError('Ambiguous labour tables')
 return candidates[0]
def validate_monthly_progress(monthly,previous):
 total=sum(sum(r[k] for k in ('july','august','september')) for r in monthly.values())
 if total==0:
  raise RuntimeError('All 52 districts show zero July-September Persondays; reject unrelated or empty source')
 old_rows=previous.get('districts',{})
 for name,r in monthly.items():
  prior=sum(x.get('julyToSeptemberAchievement',0) for x in old_rows.get(name,{}).get('rows',[]))
  if prior>0 and sum(r[k] for k in ('july','august','september'))==0:
   raise RuntimeError('Previously nonzero July-September Persondays became zero: '+name)
GRID='''tables=>tables.map(t=>{const grid=[];Array.from(t.rows).forEach((r,ri)=>{grid[ri]??=[];let ci=0;Array.from(r.cells).forEach(c=>{while(grid[ri][ci]!==undefined)ci++;for(let dy=0;dy<c.rowSpan;dy++){grid[ri+dy]??=[];for(let dx=0;dx<c.colSpan;dx++)grid[ri+dy][ci+dx]=c.innerText.trim()}ci+=c.colSpan})});return grid})'''
def fetch(page,url,persondays=False):
 response=page.goto(url,wait_until='domcontentloaded',timeout=60000)
 if response and response.status>=400:raise RuntimeError('Official HTTP '+str(response.status))
 page.wait_for_timeout(1500)
 text=page.inner_text('body')
 if re.search('verify you are human|checking your browser|access denied',text,re.I):raise RuntimeError('Official browser verification required')
 if persondays:
  radios=page.locator('input[type="radio"]')
  for i in range(radios.count()):
   r=radios.nth(i)
   if re.sub(r'\s','',r.get_attribute('value') or '').lower()=='persondays' and not r.is_checked():r.check();page.wait_for_timeout(1500);break
 return page.locator('table').evaluate_all(GRID)
def main():
 from playwright.sync_api import sync_playwright
 base=json.loads((ROOT/'shramik-fy2526-fixed-baseline.json').read_text(encoding='utf-8'))
 targets={norm(r['district']):r['total'] for r in base['rows']}
 if len(targets)!=52:raise RuntimeError('52 fixed district targets required')
 with sync_playwright() as p:
  try:b=p.chromium.launch(channel='chrome',headless=True)
  except Exception:b=p.chromium.launch(headless=True)
  try:
   context=b.new_context()
   cookie=os.environ.get('VBGRAM_COOKIE','')
   cookies=[]
   for pair in cookie.split(';'):
    if '=' in pair:
     k,v=pair.strip().split('=',1);cookies.append({'name':k,'value':v,'domain':'vbgramgrep.dord.gov.in','path':'/'})
   if cookies:context.add_cookies(cookies)
   page=context.new_page()
   debug=ROOT/'data'/'shramik-state-debug';debug.mkdir(parents=True,exist_ok=True)
   stamp=datetime.now(timezone.utc).isoformat();today=datetime.now(IST).strftime('%d-%m-%Y')
   warnings=[];labour={};labour_date=None;monthly=None;match=None
   # R6.9 is independent: a monthly-report outage must not stop labour refresh.
   try:
    labour_tables=fetch(page,LABOUR)
    (debug/'labour-tables.json').write_text(json.dumps(labour_tables,ensure_ascii=False),encoding='utf-8')
    labour=parse_labour(labour_tables,targets)
    labour_match=re.search(r'As\s*on\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',page.inner_text('body'),re.I)
    labour_date=labour_match.group(1).replace('/','-') if labour_match else today
   except Exception as e:warnings.append('Labour/MR not refreshed: '+str(e))
   try:
    monthly_tables=fetch(page,MONTHLY,True)
    (debug/'monthly-tables.json').write_text(json.dumps(monthly_tables,ensure_ascii=False),encoding='utf-8')
    candidate=parse_monthly(monthly_tables,targets)
    validate_monthly_progress(candidate,read_js(ROOT/'shramik-district-reports.js'))
    monthly=candidate
    match=re.search(r'As\s*on\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',page.inner_text('body'),re.I)
    date=match.group(1).replace('/','-') if match else today
   except Exception as e:
    warnings.append('Persondays not refreshed: '+str(e))
    if not labour:raise RuntimeError('; '.join(warnings))
  finally:b.close()
 previous=read_js(ROOT/'shramik-district-reports.js')
 if monthly is None:
  payload=read_js(ROOT/'shramik-district-reports.js')
  districts=payload['districts']
  if set(districts)!=set(targets):raise RuntimeError('Complete previous 52-district snapshot required')
  for name,d in districts.items():
   if len(d['rows'])!=1:raise RuntimeError('District summary required')
   for field in ('todayLabour','mrIssued','musterRollCount','totalGP','labourGP'):d['rows'][0][field]=labour[name].get(field)
   if labour[name].get('ongoing') is not None:d['rows'][0]['ongoing']=labour[name]['ongoing']
   d['rows'][0]['incompleteWorks']=d['rows'][0].get('ongoing')
  payload.update(labourSource=LABOUR,labourDate=labour_date,updatedAt=stamp,warnings=warnings)
 else:
  districts={}
  for name,m in monthly.items():
   a=sum(m[k] for k in ('july','august','september'));r={'janpad':'जिला योग','target':targets[name],'julyAchievement':m['july'],'augustMonthlyAchievement':m['august'],'septemberMonthlyAchievement':m['september'],'julyToSeptemberAchievement':a,'octoberAchievement':m['october'],'achievement':a+m['october'],'todayLabour':None,'ongoing':None,'mrIssued':None,'incompleteWorks':None}
   r.update(labour.get(name,{}))
   if r.get('ongoing') is None:r['ongoing']=previous.get('districts',{}).get(name,{}).get('rows',[{}])[0].get('ongoing')
   r['incompleteWorks']=r['ongoing']
   districts[name]={'officialDate':date,'dateBasis':'portal' if match else 'fetched','period':PERIOD,'detailLevel':'district','rows':[r]}
  payload={'source':MONTHLY,'labourSource':LABOUR,'labourDate':labour_date,'snapshotDate':date,'dateBasis':'portal' if match else 'fetched','updatedAt':stamp,'warnings':warnings,'districts':districts}
 payload['ongoingDate']=labour_date if labour and all(v.get('ongoing') is not None for v in labour.values()) else previous.get('ongoingDate',previous.get('snapshotDate'))
 write_js(ROOT/'shramik-district-reports.js','window.SHRAMIK_DISTRICT_REPORTS',payload)
 write_js(ROOT/'shramik-state-refresh-status.js','window.SHRAMIK_STATE_REFRESH_STATUS',{'checkedAt':stamp,'success':True,'districtCount':52,'persondaysSuccess':monthly is not None,'labourSuccess':bool(labour),'warnings':warnings})
 print('SUCCESS: 52-district Persondays '+('refreshed' if monthly is not None else 'previous snapshot retained')+'; labour/MR '+('refreshed' if labour else 'unavailable'),flush=True)
 for w in warnings:print(w,flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:
  write_js(ROOT/'shramik-state-refresh-status.js','window.SHRAMIK_STATE_REFRESH_STATUS',{'checkedAt':datetime.now(timezone.utc).isoformat(),'success':False,'message':str(e)})
  print('FAILED: last verified 52-district data retained: '+str(e),flush=True);sys.exit(1)
