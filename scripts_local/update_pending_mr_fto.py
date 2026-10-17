"""Read S5.26, payment-pending mode, all eight Satna/Maihar blocks."""
import asyncio,gzip,json,re,sys
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from update_emb_pending import rows
ROOT=Path(__file__).resolve().parents[1]
SOURCE='https://vbgramgrep.dord.gov.in/VBGRAMG/dynamic_muster_track.aspx?lflag=eng&state_code=17&fin_year=2026-2027&state_name=%u092e%u0927%u094d%u092f+%u092a%u094d%u0930%u0926%u0947%u0936+&Digest=ezij5U1uSQA7sfgabVR88g'
BLOCKS={'AMARPATAN':75,'MAIHAR':115,'MAJHGAWAN':96,'NAGOD':94,'RAMNAGAR':55,'RAMPUR BAGHELAN':97,'SATNA':93,'UNCHAHARA':70}
def summarize(rr):
 start=next((i for i,r in enumerate(rr) if len(r)==14 and r[2]['text'].lower()=='muster roll number' and r[10]['text'].lower()=='fto no.'),None)
 if start is None:raise ValueError('S5.26 tracking table/header missing; not treated as zero')
 groups={};serial=[];details=[];seen_details=set()
 for row in rr[start+1:]:
  c=[x['text'] for x in row]
  if not c or not c[0].isdigit():continue
  if len(c)!=14:raise ValueError('Incomplete S5.26 record')
  serial.append(int(c[0]));gp=c[1];k=(c[5],c[2]);g=groups.setdefault(gp,{x:set() for x in ('mr','first','second','missingFtoFirst','missingFtoSecond','knownFirst','knownSecond')})
  if not gp or not c[2] or not re.match(r'\d+/',c[5]):raise ValueError('MR identity missing')
  g['mr'].add(k)
  date=lambda s:bool(re.fullmatch(r'\d{1,2}[-/]\d{1,2}[-/]\d{4}',s))
  first='pending' in c[12].lower() or (bool(c[10]) and not date(c[12]))
  second=not first and date(c[12]) and not date(c[13])
  identity=tuple(c[1:])
  if identity not in seen_details:
   seen_details.add(identity)
   details.append(dict(zip(('panchayat','mr','staff','recordNo','workCode','closureDate','fillingStatus','wageListDate','wageListNo','ftoNo','ftoDate','firstSignDate','secondSignDate'),c[1:]),firstPending=first,secondPending=second))
  for stage,active in [('First',first),('Second',second)]:
   if active:
    g[stage.lower()].add(k)
    if c[10]:g['known'+stage].add(c[10])
    else:g['missingFto'+stage].add(k)
 if serial and serial!=list(range(1,len(serial)+1)):raise ValueError('Missing/repeated serials; complete source required')
 return {'rawRows':len(serial),'details':details,'groups':{gp:{k:len(v) for k,v in g.items()} for gp,g in groups.items()}}
def build(blocks,source=SOURCE):
 if set(blocks)!=set(BLOCKS):raise ValueError('All eight blocks must be fetched before publication')
 stamp=datetime.now(ZoneInfo('Asia/Kolkata'));reports={}
 for stage in ('mr','first','second'):
  result=[]
  for block,part in blocks.items():
   for gp,g in part['groups'].items():result.append({'block':block,'panchayat':gp,'pending':g[stage]})
  reports[stage]={'available':True,'sourceDate':stamp.strftime('%d/%m/%Y'),'fetchedAt':stamp.isoformat(),'source':source,'unit':'musterRoll','coverage':list(BLOCKS),'rows':result}
 d={'schemaVersion':1,'reports':reports,'sourceMode':'payment-pending','counts':'Distinct work code + muster roll per GP; first/second are associated muster rolls, not unique FTO orders','sourceSummary':{b:{k:v for k,v in p.items() if k!='details'} for b,p in blocks.items()},'details':[dict(r,block=b) for b,p in blocks.items() for r in p.get('details',[])],'filterVerified':True}
 validate(d);return d
def validate(d):
 if d.get('schemaVersion')!=1 or d.get('sourceMode')!='payment-pending' or d.get('filterVerified') is not True:raise ValueError('Invalid tracking snapshot')
 for stage in ('mr','first','second'):
  r=d['reports'][stage]
  if not r.get('available') or set(r.get('coverage',[]))!=set(BLOCKS):raise ValueError('Incomplete block coverage')
  seen=set()
  for row in r['rows']:
   k=(row['block'],row['panchayat'])
   if k in seen or k[0] not in BLOCKS or not k[1] or type(row['pending']) is not int or row['pending']<0:raise ValueError('Invalid/duplicate GP count')
   seen.add(k)
 details=d.get('details')
 if details is None:
  if d.get('detailsFile')!='data/pending-mr-fto-details.json.gz':raise ValueError('Datewise detail file missing')
  details=json.loads(gzip.decompress((ROOT/d['detailsFile']).read_bytes()))
  if len(details)!=d.get('detailCount'):raise ValueError('Detail count mismatch')
 if set(r['block'] for r in details)!=set(BLOCKS):raise ValueError('All eight blocks require datewise details')
 for stage in ('mr','first','second'):
  counts={}
  for r in details:
   if stage!='mr' and not r[stage+'Pending']:continue
   counts.setdefault((r['block'],r['panchayat']),set()).add((r['workCode'],r['mr']))
  for r in d['reports'][stage]['rows']:
   if r['pending']!=len(counts.get((r['block'],r['panchayat']),set())):raise ValueError('Detail/summary reconciliation failed')

async def postback(page,action,step,timeout=90000):
 # ASP.NET may use a full navigation OR an UpdatePanel POST. A response
 # wait handles both, without waiting for a navigation that never occurs.
 try:
  async with page.expect_response(lambda r:r.request.method=='POST' and r.url.split('?')[0]==page.url.split('?')[0],timeout=timeout) as pending:
   await action()
  response=await pending.value
  await response.finished()
  if response.status>=400:raise ValueError(f'HTTP {response.status}')
  await page.wait_for_load_state('domcontentloaded',timeout=timeout)
  await page.wait_for_function("() => document.readyState !== 'loading' && !(window.Sys && Sys.WebForms && Sys.WebForms.PageRequestManager.getInstance().get_isInAsyncPostBack())",timeout=timeout)
 except Exception as exc:raise RuntimeError(f'S5.26 {step}: {exc}') from exc

async def select_report_option(page,selector,label):
 control=page.locator(selector)
 # Selecting the already selected state/GP does not fire a postback.
 selected=await control.locator('option:checked').all_text_contents()
 if selected and selected[0].strip()==label:return
 async def action():await control.select_option(label=label)
 await postback(page,action,selector+' -> '+label)
 await page.wait_for_function("([selector,label]) => { const e=document.querySelector(selector); return e && e.selectedOptions.length && e.selectedOptions[0].textContent.trim()===label; }",arg=[selector,label],timeout=30000)

async def fetch_block(context,block,n):
 page=await context.new_page()
 async def select(selector,label):await select_report_option(page,selector,label)
 try:
  response=await page.goto(SOURCE,wait_until='domcontentloaded',timeout=90000)
  if response is not None and response.status>=400:raise ValueError('Official portal refused report')
  await select('#ContentPlaceHolder1_ddl_state','MADHYA PRADESH')
  await select('#ContentPlaceHolder1_ddl_dist','SATNA')
  await select('#ContentPlaceHolder1_ddl_blk',block)
  gps=await page.locator('#ContentPlaceHolder1_ddl_pan option').all_text_contents();gps=[g.strip() for g in gps if g.strip() not in ('Select','ALL','')]
  if len(gps)!=n:raise ValueError('GP coverage mismatch: '+block)
  await select('#ContentPlaceHolder1_ddl_pan','ALL')
  radio=page.locator('#ContentPlaceHolder1_Rbtn_pay_1')
  if not await radio.is_checked():
   await postback(page,radio.check,'payment-pending filter')
  await postback(page,page.locator('#ContentPlaceHolder1_Button1').click,'generate '+block,180000)
  if not await page.locator('#ContentPlaceHolder1_Rbtn_pay_1').is_checked():raise ValueError('Payment pending filter not retained')
  body=await page.content()
  if re.search(r'Page\$\d+',body):raise ValueError('Paginated tracking report requires all pages')
  part=summarize(rows(body))
  if not set(part['groups']).issubset(set(gps)):raise ValueError('Unrecognized GP in report: '+block)
  fields=('mr','first','second','missingFtoFirst','missingFtoSecond','knownFirst','knownSecond')
  for gp in gps:part['groups'].setdefault(gp,dict.fromkeys(fields,0))
  print('S5.26 verified:',block,'GPs',n,'source rows',part['rawRows'],flush=True)
  return part
 finally:await page.close()

async def fetch(context):
 result={}
 for block,n in BLOCKS.items():
  for attempt in range(3):
   try:
    result[block]=await fetch_block(context,block,n)
    break
   except Exception as exc:
    if attempt==2:raise RuntimeError(f'{block} failed after 3 fresh-page attempts: {exc}') from exc
    print(f'Retrying S5.26 {block} ({attempt+2}/3): {exc}',flush=True)
    await asyncio.sleep(2*(attempt+1))
 return build(result)
def main():
 from emb_browser_reader import BrowserReader
 reader=BrowserReader()
 try:d=asyncio.run_coroutine_threadsafe(fetch(reader.context),reader.loop).result(timeout=3600)
 finally:reader.close()
 details=d.pop('details');d['detailsFile']='data/pending-mr-fto-details.json.gz';d['detailCount']=len(details)
 dp=ROOT/d['detailsFile'];dt=dp.with_suffix('.tmp');dt.write_bytes(gzip.compress(json.dumps(details,ensure_ascii=False,separators=(',',':')).encode('utf-8')));dt.replace(dp)
 p=ROOT/'data/pending-mr-fto.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False,separators=(',',':')),encoding='utf-8');tmp.replace(p)
 print('SUCCESS: S5.26 pending MR/FTO stages, eight blocks, 695 GPs')
if __name__=='__main__':
 try:main()
 except Exception as e:print('Pending MR/FTO refresh failed; previous snapshot retained:',e,flush=True);sys.exit(1)
