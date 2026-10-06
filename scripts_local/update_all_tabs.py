"""Refresh each dashboard data feed independently; roll back failed partial writes."""
import json,os,subprocess,sys
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parent.parent
GROUPS=[
 ('daily_labour',[['scripts_local/local_auto_update.py'],['scripts/merge_official_summary.py'],['scripts/validate_auto_data.py']],['auto-data.js','auto-status.js','data/official-summary.csv','data/fetch-status.json']),
 ('shramik_59',[['scripts_local/update_shramik_niyojan.py']],['shramik-niyojan-data.js']),
 ('shramik_52',[['scripts_local/update_shramik_state.py']],['shramik-district-reports.js','shramik-state-refresh-status.js']),
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
 if group=='shramik_59':
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
  if len(data(root/'data/rejected-wage-latest.json').get('rows',[]))!=8:raise ValueError('Expected 8 rejected wage Janpads')
 elif group=='mis_612':
  if not data(root/'ongoing-details.js'):raise ValueError('MIS work details empty')
 elif group=='yuktdhara':
  if len(data(root/'yuktdhara-official-data.js').get('rows',[]))!=8:raise ValueError('Yuktdhara Janpads incomplete')
 elif group=='block_statistics':
  if len(data(root/'vbg-block-stats.js').get('rows',[]))!=8:raise ValueError('Block statistics incomplete')
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
   else:subprocess.run([sys.executable,'-u']+command,cwd=root,check=True,timeout=300)
  validator(group,root)
  return {'success':True,'files':files}
 except Exception as e:
  restore(root,saved)
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
