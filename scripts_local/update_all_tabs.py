"""Refresh each dashboard data feed independently; roll back failed partial writes."""
import csv,json,os,subprocess,sys,runpy,time,codecs
from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent.parent
GP_URL=os.environ.get('VBGRAM_DAILY_REPORT_URL','').strip() or runpy.run_path(str(ROOT/'scripts_local/local_auto_update.py'),run_name='source_config')['REPORT_URL']
GROUPS=[
 ('shramik_complete',[
  ['scripts_local/local_auto_update.py'],['scripts/merge_official_summary.py'],
  ['scripts_local/update_gp_emuster.py','--url',GP_URL],
  ['scripts_local/update_shramik_niyojan.py'],['scripts_local/update_shramik_state.py']
 ],['auto-data.js','auto-status.js','data/official-summary.csv','data/fetch-status.json',
    'shramik-gp-progress-data.js','gp-emuster-data.js','shramik-niyojan-data.js','shramik-district-reports.js',
    'shramik-state-refresh-status.js','shramik-refresh-status.js']),
 ('muster_emb',[['scripts_local/update_muster_emb_monitoring.py','--update-only']],['muster-emb-data.js']),
 ('pending_mr_fto',[['scripts_local/update_pending_mr_fto.py']],['data/pending-mr-fto.json','data/pending-mr-fto-details.json.gz']),
 ('emb_pending',[['scripts_local/update_emb_pending.py']],['data/emb-pending-latest.json']),
 ('yuktdhara_state',[['scripts_local/update_yuktdhara_state.py']],['data/yuktdhara-state-latest.json']),
 ('yuktdhara',[['scripts_local/update_yuktdhara_monitoring.py','--update-only'],['scripts_local/update_yuktdhara_received.py']],['yuktdhara-data.js','yuktdhara-official-data.js','yuktdhara-received-data.js']),
 ('pending_wage_payment',[['scripts_local/update_pending_wage_payment.py']],['data/pending-wage-payment-latest.json']),
 ('timely_payment',[['scripts_local/update_timely_payment.py']],['data/timely-payment-latest.json']),
 ('delayed_compensation',[['scripts_local/update_delayed_compensation.py']],['data/delayed-compensation-latest.json']),
 ('block_statistics',[['scripts_local/update_satna_block_statistics.py']],['vbg-block-stats.js']),
 ('mis_612',[['scripts_local/update_mis_612_work_details.py']],['data/Ongoing_Works_dynamic_work_details_latest.csv','data/mis-6.12-status.json','ongoing-details.js']),
 ('pmayg_physical',[['scripts_local/update_pmayg_physical.py']],['data/pmayg-physical-latest.json']),
 ('pmayg',[['scripts_local/update_pmayg.py']],['data/pmayg-latest.json']),
 ('above75',[['scripts_local/update_above75.py']],['data/above75-latest.json']),
 ('planner',[['scripts/fetch_planner_portal_summary.py']],['planner-portal-data.js']),
 ('secure_ts',[['scripts_local/update_secure_ts.py']],['secure-ts-data.js']),
 ('ek_bagiya_payment',[['scripts_local/update_ek_bagiya_payment.py']],['data/ek-bagiya-payment-latest.json']),
 ('rejected_wage',[['scripts/update_rejected_wage.py']],['data/rejected-wage-latest.json'])
]
OUTPUTS=list(dict.fromkeys(f for _,_,files in GROUPS for f in files))+['all-tabs-auto-status.json']
def data(path):
 s=path.read_text(encoding='utf-8-sig').strip()
 return json.loads(s.split('=',1)[1].strip().rstrip(';') if path.suffix=='.js' else s)
def validate(group,root):
 if group=='secure_ts':
  runpy.run_path(str(root/'scripts_local/update_secure_ts.py'))['validate'](data(root/'secure-ts-data.js'))
 elif group=='shramik_complete':
  validate_shramik(root)
 elif group=='shramik_59':
  d=data(root/'shramik-niyojan-data.js')
  if len(d.get('engineerRows',[]))!=59 or len(d.get('gpMandaysRows',[]))!=695 or sum(r['target'] for r in d['engineerRows'])!=621552:raise ValueError('Expected verified 59 engineers, 695 GPs and target 621552')
 elif group=='shramik_52':
  d=data(root/'shramik-district-reports.js')
  if len(d.get('districts',{}))!=52:raise ValueError('Expected all 52 districts')
 elif group=='pending_mr_fto':
  d=data(root/'data/pending-mr-fto.json')
  runpy.run_path(str(root/'scripts_local/update_pending_mr_fto.py'))['validate'](d)
  if any(datetime.fromisoformat(r['fetchedAt']).astimezone(ZoneInfo('Asia/Kolkata')).date()!=datetime.now(ZoneInfo('Asia/Kolkata')).date() for r in d['reports'].values()):raise ValueError('Current pending MR/FTO snapshot required')
 elif group=='emb_pending':
  d=data(root/'data/emb-pending-latest.json')
  runpy.run_path(str(root/'scripts_local/update_emb_pending.py'))['validate'](d)
  if d.get('failedGP',0):raise ValueError(f"Incomplete e-MB coverage: {d['failedGP']} unread GPs; not a fully verified report")
  if datetime.fromisoformat(d['fetchedAt']).astimezone(ZoneInfo('Asia/Kolkata')).date()!=datetime.now(ZoneInfo('Asia/Kolkata')).date():raise ValueError('Current pending e-MB detail required')
 elif group=='muster_emb':
  d=data(root/'muster-emb-data.js')
  if len(d.get('rows',[]))!=8 or len(d.get('gpRows',[]))!=695:raise ValueError('Expected 8 Janpads and 695 GPs')
 elif group=='planner':
  d=data(root/'planner-portal-data.js')
  if len(d.get('blocks',[]))!=8 or len(d.get('panchayats',[]))!=695 or len(d.get('validation',[]))!=8 or not all(r['ok'] for r in d['validation']):raise ValueError('Planner GP totals incomplete or do not reconcile')
 elif group=='rejected_wage':
  d=data(root/'data/rejected-wage-latest.json');rows=d.get('rows',[])
  janpads={'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}
  expected={(fy,j) for fy in ('2024-25','2025-26','2026-27') for j in janpads}
  actual={(r.get('fy'),norm(r.get('janpad'))) for r in rows}
  if len(rows)!=24 or actual!=expected:raise ValueError('Expected 24 unique rejected wage Janpad/FY records: 8 Janpads for each of 3 years')
  if d.get('date')!=datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat() or not d.get('combined'):raise ValueError('Current combined rejected wage snapshot required')
 elif group=='ek_bagiya_payment':
  d=data(root/'data/ek-bagiya-payment-latest.json')
  if d.get('logicVersion')!='sabhi-reports-logic-v1' or len(d.get('rows',[]))!=8 or d.get('retrievedDate')!=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d/%m/%Y') or not d.get('sourceDates') or not d.get('works'):raise ValueError('Current complete payment source required')
 elif group=='pmayg_physical':
  runpy.run_path(str(root/'scripts_local/update_pmayg_physical.py'))['validate'](data(root/'data/pmayg-physical-latest.json'))
 elif group=='pmayg':
  d=data(root/'data/pmayg-latest.json');rows=d.get('rows',[])
  if not d.get('allYears') or not rows or not d.get('nregaRows') or not d.get('vbgRows'):raise ValueError('Both PMAY sources and all work-start years required')
  if len({r['code'] for r in rows})!=len(rows):raise ValueError('Duplicate PMAY work codes')
  for r in rows:
   if r['status'] not in ('Ongoing','Approved') or not r.get('cluster'):raise ValueError('Invalid PMAY status/mapping')
   if abs(r['mandays']-r['nregaMandays']-r['vbgMandays'])>0.000001 or abs(r['balanceMandays']-max(90-r['mandays'],0))>0.000001:raise ValueError('PMAY mandays arithmetic failed')
 elif group=='above75':
  d=data(root/'data/above75-latest.json');rr=d.get('rows',[])
  if d.get('schemaVersion')!=3 or d.get('basis')!='r613-paid-validated' or not rr or d.get('detailedCount')!=len(rr):raise ValueError('Above75 R6.13 snapshot incomplete')
  if datetime.fromisoformat(d['fetchedAt']).astimezone(ZoneInfo('Asia/Kolkata')).date()!=datetime.now(ZoneInfo('Asia/Kolkata')).date():raise ValueError('Current Above75 snapshot required')
  if len({r['code'] for r in rr})!=len(rr):raise ValueError('Duplicate Above75 work codes')
  import math
  key=lambda value: norm(value).replace(' ','').replace('SATNA','SOHAWAL')
  expected={'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPURBAGHELAN','SOHAWAL','UNCHAHARA'}
  official=d.get('officialSummary',[]);checks=d.get('validation',[])
  if len(official)!=8 or {key(r['janpad']) for r in official}!=expected or len(checks)!=8 or {key(r['janpad']) for r in checks}!=expected or not all(r.get('ok') is True for r in checks):raise ValueError('Above75 requires all 8 verified R6.13 Janpads')
  for r in rr:
   amounts=[r[k] for k in ('sanction','paidWages','paidMaterial','nregaBooked','overallBooked')]
   if any(not math.isfinite(v) or v<0 for v in amounts) or r['status'] not in ('Ongoing','Suspended','Physically Completed') or key(r['janpad']) not in expected:raise ValueError('Invalid Above75 detail')
   if abs(r['overallBooked']-r['paidWages']-r['paidMaterial'])>0.000001 or abs(r['nregaBooked']-r['overallBooked'])>0.000001:raise ValueError('Above75 paid arithmetic failed')
  for o in official:
   members=[r for r in rr if key(r['janpad'])==key(o['janpad']) and r['sanction']>0]
   band=sum(r['overallBooked']*100>r['sanction']*75 and r['overallBooked']*100<r['sanction']*99 for r in members)
   above=sum(r['overallBooked']>r['sanction'] for r in members)
   c=next(r for r in checks if key(r['janpad'])==key(o['janpad']))
   if (band,above)!=(o['band75to100'],o['above100']) or (band,above)!=(c['band'],c['above100']):raise ValueError('Above75 R6.13 reconciliation failed: '+o['janpad'])
  if d['nregaCount']!=sum(r['incomplete'] for r in official) or d['bandCount']!=sum(r['band75to100'] for r in official) or d['above75Count']!=sum(r['overallBooked']*100>r['sanction']*75 for r in rr if r['sanction']>0):raise ValueError('Above75 summary totals failed')
 elif group=='mis_612':
  if not data(root/'ongoing-details.js'):raise ValueError('MIS work details empty')
 elif group=='yuktdhara_state':
  d=data(root/'data/yuktdhara-state-latest.json');rr=d.get('rows',[])
  if len(rr)!=52 or len({r['district'] for r in rr})!=52:raise ValueError('52 unique Yuktdhara districts required')
  if any(sum(r[k] for r in rr)!=v for k,v in d['totals'].items()):raise ValueError('Yuktdhara state totals mismatch')
  if datetime.fromisoformat(d['fetchedAt']).astimezone(ZoneInfo('Asia/Kolkata')).date()!=datetime.now(ZoneInfo('Asia/Kolkata')).date():raise ValueError('Today verified state snapshot required')
 elif group=='yuktdhara':
  if len(data(root/'yuktdhara-official-data.js').get('rows',[]))!=8:raise ValueError('Yuktdhara Janpads incomplete')
  received=data(root/'yuktdhara-received-data.js')
  today=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d-%m-%Y')
  if not received.get('success') or received.get('officialDate','').replace('/','-')!=today or not received.get('rows'):raise ValueError('Current verified Yuktdhara GP/engineer detail required: '+str(received.get('message','stale or empty detail')))
 elif group=='pending_wage_payment':
  d=data(root/'data/pending-wage-payment-latest.json')
  runpy.run_path(str(root/'scripts_local/update_pending_wage_payment.py'))['validate'](d)
  if datetime.fromisoformat(d['fetchedAt']).astimezone(ZoneInfo('Asia/Kolkata')).date()!=datetime.now(ZoneInfo('Asia/Kolkata')).date():raise ValueError('Today verified pending wage payment required')
 elif group=='timely_payment':
  d=data(root/'data/timely-payment-latest.json')
  runpy.run_path(str(root/'scripts_local/update_timely_payment.py'))['validate'](d)
  if datetime.fromisoformat(d['fetchedAt']).astimezone(ZoneInfo('Asia/Kolkata')).date()!=datetime.now(ZoneInfo('Asia/Kolkata')).date():raise ValueError('Today official timely payment snapshot required')
 elif group=='delayed_compensation':
  d=data(root/'data/delayed-compensation-latest.json')
  runpy.run_path(str(root/'scripts_local/update_delayed_compensation.py'))['validate'](d)
  if datetime.fromisoformat(d['fetchedAt']).astimezone(ZoneInfo('Asia/Kolkata')).date()!=datetime.now(ZoneInfo('Asia/Kolkata')).date():raise ValueError('Today official delayed compensation snapshot required')
 elif group=='block_statistics':
  if len(data(root/'vbg-block-stats.js').get('rows',[]))!=8:raise ValueError('Block statistics incomplete')
def norm(value):return ' '.join(str(value or '').split()).upper()
def validate_shramik(root):
 today=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d-%m-%Y')
 gp=data(root/'shramik-gp-progress-data.js');sn=data(root/'shramik-niyojan-data.js');state=data(root/'shramik-district-reports.js');auto=data(root/'auto-data.js')
 if gp.get('date')!=today or not gp.get('gpProgressVerified'):raise ValueError('Current verified GP progress snapshot required')
 if sn.get('officialDate','').replace('/','-')!=today or state.get('snapshotDate')!=today:raise ValueError('All Shramik views must use today\'s snapshot')
 validate('shramik_59',root);validate('shramik_52',root)
 status=data(root/'shramik-state-refresh-status.js')
 if not all(status.get(k) for k in ('success','persondaysSuccess','labourSuccess','gpSuccess')):raise ValueError('52-district full refresh incomplete')
 rows=gp.get('rows',[]);keys={(norm(r['janpad']),norm(r['panchayat'])) for r in rows}
 monthly={(norm(r['janpad']),norm(r['panchayat'])) for r in sn['gpMandaysRows']}
 if len(rows)!=695 or len(keys)!=695 or keys!=monthly:raise ValueError('695 unique GP details must match monthly GP master')
 # Use the actual official parent rows read in the GP browser session.
 # The category reader runs earlier in a separate session; its ALL values
 # must not be combined with another parent/GP snapshot.
 parents={norm(r['janpad']):r for r in gp.get('blocks',[])}
 expected={'AMARPATAN':75,'MAIHAR':115,'MAJHGAWAN':96,'NAGOD':94,'RAMNAGAR':55,'RAMPUR BAGHELAN':97,'SATNA':93,'UNCHAHARA':70}
 if len(gp.get('blocks',[]))!=8 or set(parents)!=set(expected):raise ValueError('All 8 unique official GP parent rows required')
 for j,p in parents.items():
  rr=[r for r in rows if norm(r['janpad'])==j]
  actual=(len(rr),sum(r['gpsProgress'] for r in rr),sum(r['labour'] for r in rr),sum(r['worksMR'] for r in rr))
  if p['gps']!=expected[j] or actual!=(p['gps'],p['progressGP'],p['labour'],p['works']):raise ValueError('GP details do not match their official parent: '+j)
  if not {'noEkyc','mrs'}<=p.keys():raise ValueError('Official ALL parent columns incomplete: '+j)
 path=root/'data/official-summary.csv'
 with path.open(encoding='utf-8-sig',newline='') as f:
  reader=csv.DictReader(f);fields=reader.fieldnames;summary=list(reader)
 if len(summary)!=8 or {norm(r['janpad']) for r in summary}!=set(expected):raise ValueError('Official category summary incomplete')
 for r in summary:
  p=parents[norm(r['janpad'])]
  for k,v in {'totalGP':p['gps'],'musterGP':p['progressGP'],'dysfunctionalGP':p['gps']-p['progressGP'],'labourAll':p['labour'],'mrAll':p['works'],'noEkyc':p['noEkyc'],'mrs':p['mrs']}.items():r[k]=v
 with path.open('w',encoding='utf-8-sig',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(summary)
 subprocess.run([sys.executable,'scripts/merge_official_summary.py'],cwd=root,check=True)
 auto=data(root/'auto-data.js')
 auto.setdefault('meta',{})['dailyParentFetchedAt']=gp['fetchedAt']
 auto['meta']['dailyParentSource']=gp['source']
 official={norm(r['janpad']):r for r in auto['official']}
 if len(official)!=8:raise ValueError('8 official Janpads required')
 for j,o in official.items():
  members=[r for r in rows if norm(r['janpad'])==j]
  totals={'totalGP':len(members),'musterGP':sum(r['gpsProgress'] for r in members),'labourAll':sum(r['labour'] for r in members),'mrAll':sum(r['worksMR'] for r in members)}
  differences={k:{'official':o.get(k),'GP_total':v} for k,v in totals.items() if float(o.get(k,-1))!=v}
  if differences:raise ValueError('Live GP/Janpad total mismatch: '+j+' '+json.dumps(differences,ensure_ascii=False))
  if any(r['gpsProgress'] not in (0,1) for r in members):raise ValueError('Invalid GP progress flag')
 validate_work_types(root,gp)
 # Replace old workbook daily metrics only after every feed validates.
 auto['rows']=rows
 auto.setdefault('meta',{}).setdefault('sourceDates',{})['RepDay']=today
 auto['meta']['gpProgressVerified']=True
 p=root/'auto-data.js';p.write_text('window.AUTO_REPORT = '+json.dumps(auto,ensure_ascii=False)+';\n',encoding='utf-8')
def validate_work_types(root,gp):
 d=data(root/'gp-emuster-data.js')
 if d.get('date')!=gp['date'] or not d.get('gpProgressVerified'):raise ValueError('Today verified GP work-type snapshot required')
 keys=lambda rr:{(norm(r['janpad']),norm(r['panchayat'])):r for r in rr}
 workrows=d.get('rows',[]);detail=keys(workrows);progress=keys(gp['rows'])
 if len(workrows)!=695 or len(detail)!=695 or set(detail)!=set(progress):raise ValueError('Work-type feed must contain the same 695 GPs')
 for k,r in detail.items():
  if any(r.get(f)!=progress[k].get(f) for f in ('labour','gpsProgress')):raise ValueError('Work-type GP snapshot differs: '+str(k))
  if r.get('summaryWorksMR',r.get('worksMR'))!=progress[k].get('worksMR'):raise ValueError('Work-type summary reference differs: '+str(k))
  issued=r.get('issuedWorks')
  if not isinstance(issued,dict) or any(not isinstance(v,int) or v<0 for v in issued.values()) or sum(issued.values())!=r['worksMR']:raise ValueError('MR-issued work categories incomplete: '+str(k))
 works=d.get('works',[]);expected=sum(r['worksMR'] for r in workrows)
 if d.get('totalWorks')!=expected or len(works)!=expected or len({w['code'] for w in works})!=expected:raise ValueError('MR-issued work list count/unique codes do not reconcile')

def restore(root,saved):
 for name,content in saved.items():
  p=root/name
  if content is None:
   if p.exists():p.unlink()
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
def run_logged(command,root,group,timeout):
 # Keep child errors even when the outer BAT log is unavailable. Stream
 # progress to the console while storing an exact per-report log on disk.
 log=root/'data/daily-run-logs'/f'{group}.log'
 log.parent.mkdir(parents=True,exist_ok=True)
 with log.open('ab') as output:
  output.write(('\nCOMMAND '+repr(command)+'\n').encode('utf-8'));output.flush()
  offset=output.tell()
  with log.open('rb') as reader:
   reader.seek(offset)
   decoder=codecs.getincrementaldecoder('utf-8')(errors='replace')
   args=[sys.executable,'-u']+command
   with subprocess.Popen(args,cwd=root,stdout=output,stderr=subprocess.STDOUT) as process:
    deadline=time.monotonic()+timeout
    while True:
     try:process.wait(timeout=min(0.25,max(0.001,deadline-time.monotonic())))
     except subprocess.TimeoutExpired:pass
     text=decoder.decode(reader.read())
     if text:print(text,end='',flush=True)
     if process.poll() is not None:
      text=decoder.decode(reader.read(),final=True)
      if text:print(text,end='',flush=True)
      if process.returncode:raise subprocess.CalledProcessError(process.returncode,args)
      return
     if time.monotonic()>=deadline:
      process.kill();process.wait()
      raise subprocess.TimeoutExpired(args,timeout)

def refresh_group(group,commands,files,root=ROOT,executor=None,validator=validate):
 saved={f:(root/f).read_bytes() if (root/f).exists() else None for f in files}
 try:
  for command in commands:
   if executor:executor(command,root)
   else:run_logged(command,root,group,timeout=7200 if command[0] in ('scripts_local/update_gp_emuster.py','scripts_local/update_secure_ts.py','scripts_local/update_pending_mr_fto.py','scripts_local/update_ek_bagiya_payment.py','scripts_local/update_emb_pending.py') else 1800 if command[0] in ('scripts_local/update_yuktdhara_received.py','scripts_local/update_mis_612_work_details.py','scripts_local/update_pmayg_physical.py','scripts_local/update_pmayg.py','scripts_local/update_above75.py') else 900)
  runpy.run_path(str(root/'scripts_local/apply_sector_allocations.py'))['apply'](root,files)
  validator(group,root)
  return {'success':True,'files':files}
 except Exception as e:
  restore(root,saved)
  print(group + ': validation/fetch failed: ' + str(e), flush=True)
  log=root/'data/daily-run-logs'/f'{group}.log'
  tail=log.read_bytes()[-6000:].decode('utf-8','replace') if log.exists() else ''
  return {'success':False,'message':str(e),'errorTail':tail,'files':files}
def main():
 states={}
 for i,(group,commands,files) in enumerate(GROUPS,1):
  print(f'[{i}/{len(GROUPS)}] Refresh {group}',flush=True)
  states[group]=refresh_group(group,commands,files)
  print(group+': '+('SUCCESS' if states[group]['success'] else 'FAILED — previous verified files restored'),flush=True)
 payload={'checkedAt':datetime.now(timezone.utc).isoformat(),'schedule':'08:00 Asia/Kolkata','reports':states,'success':all(r['success'] for r in states.values())}
 p=ROOT/'all-tabs-auto-status.json';t=p.with_suffix('.tmp');t.write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf-8');os.replace(t,p)
 # Keep failed sources visible to the scheduler while allowing fresh sources to publish.
 return 0 if payload['success'] else 1
if __name__=='__main__':sys.exit(main())

