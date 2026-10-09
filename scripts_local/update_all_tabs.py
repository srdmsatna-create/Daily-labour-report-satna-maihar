"""Refresh each dashboard data feed independently; roll back failed partial writes."""
import json,os,subprocess,sys,runpy
from pathlib import Path
from datetime import datetime,timezone
from zoneinfo import ZoneInfo
ROOT=Path(__file__).resolve().parent.parent
GP_URL=os.environ.get('VBGRAM_DAILY_REPORT_URL','').strip() or runpy.run_path(str(ROOT/'scripts_local/local_auto_update.py'),run_name='source_config')['REPORT_URL']
GROUPS=[
 ('shramik_complete',[
  ['scripts_local/local_auto_update.py'],['scripts/merge_official_summary.py'],
  ['scripts_local/update_gp_emuster.py','--url',GP_URL,'--gp-only'],
  ['scripts_local/update_shramik_niyojan.py'],['scripts_local/update_shramik_state.py']
 ],['auto-data.js','auto-status.js','data/official-summary.csv','data/fetch-status.json',
    'shramik-gp-progress-data.js','shramik-niyojan-data.js','shramik-district-reports.js',
    'shramik-state-refresh-status.js','shramik-refresh-status.js']),
 ('muster_emb',[['scripts_local/update_muster_emb_monitoring.py','--update-only']],['muster-emb-data.js']),
 ('yuktdhara',[['scripts_local/update_yuktdhara_monitoring.py','--update-only']],['yuktdhara-data.js','yuktdhara-official-data.js']),
 ('block_statistics',[['scripts_local/update_satna_block_statistics.py']],['vbg-block-stats.js']),
 ('mis_612',[['scripts_local/update_mis_612_work_details.py']],['data/Ongoing_Works_dynamic_work_details_latest.csv','data/mis-6.12-status.json','ongoing-details.js']),
 ('planner',[['scripts/fetch_planner_portal_summary.py']],['planner-portal-data.js']),
 ('rejected_wage',[['scripts/update_rejected_wage.py']],['data/rejected-wage-latest.json'])
]
OUTPUTS=list(dict.fromkeys(f for _,_,files in GROUPS for f in files))+['all-tabs-auto-status.json']
def data(path):
 s=path.read_text(encoding='utf-8-sig').strip()
 return json.loads(s.split('=',1)[1].strip().rstrip(';') if path.suffix=='.js' else s)
def validate(group,root):
 if group=='shramik_complete':
  validate_shramik(root)
 elif group=='shramik_59':
  d=data(root/'shramik-niyojan-data.js')
  if len(d.get('engineerRows',[]))!=59 or len(d.get('gpMandaysRows',[]))!=695 or sum(r['target'] for r in d['engineerRows'])!=621552:raise ValueError('Expected verified 59 engineers, 695 GPs and target 621552')
 elif group=='shramik_52':
  d=data(root/'shramik-district-reports.js')
  if len(d.get('districts',{}))!=52:raise ValueError('Expected all 52 districts')
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
 elif group=='mis_612':
  if not data(root/'ongoing-details.js'):raise ValueError('MIS work details empty')
 elif group=='yuktdhara':
  if len(data(root/'yuktdhara-official-data.js').get('rows',[]))!=8:raise ValueError('Yuktdhara Janpads incomplete')
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
 official={norm(r['janpad']):r for r in auto['official']}
 if len(official)!=8:raise ValueError('8 official Janpads required')
 for j,o in official.items():
  members=[r for r in rows if norm(r['janpad'])==j]
  totals={'totalGP':len(members),'musterGP':sum(r['gpsProgress'] for r in members),'labourAll':sum(r['labour'] for r in members),'mrAll':sum(r['worksMR'] for r in members)}
  differences={k:{'official':o.get(k),'GP_total':v} for k,v in totals.items() if float(o.get(k,-1))!=v}
  if differences:raise ValueError('Live GP/Janpad total mismatch: '+j+' '+json.dumps(differences,ensure_ascii=False))
  if any(r['gpsProgress'] not in (0,1) for r in members):raise ValueError('Invalid GP progress flag')
 # Replace old workbook daily metrics only after every feed validates.
 auto['rows']=rows
 auto.setdefault('meta',{}).setdefault('sourceDates',{})['RepDay']=today
 auto['meta']['gpProgressVerified']=True
 p=root/'auto-data.js';p.write_text('window.AUTO_REPORT = '+json.dumps(auto,ensure_ascii=False)+';\n',encoding='utf-8')
def restore(root,saved):
 for name,content in saved.items():
  p=root/name
  if content is None:
   if p.exists():p.unlink()
  else:p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(content)
def refresh_group(group,commands,files,root=ROOT,executor=None,validator=validate):
 saved={f:(root/f).read_bytes() if (root/f).exists() else None for f in files}
 try:
  for command in commands:
   if executor:executor(command,root)
   else:subprocess.run([sys.executable,'-u']+command,cwd=root,check=True,timeout=1800 if '--gp-only' in command else 900)
  validator(group,root)
  return {'success':True,'files':files}
 except Exception as e:
  restore(root,saved)
  print(group + ': validation/fetch failed: ' + str(e), flush=True)
  return {'success':False,'message':str(e),'files':files}
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
