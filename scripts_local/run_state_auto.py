"""Refresh and publish state data from an isolated checkout; never alter user work."""
import json, os, subprocess, sys, tempfile
from pathlib import Path
from datetime import datetime
ROOT=Path(__file__).resolve().parents[1]
LOGS=ROOT/'logs';LOGS.mkdir(exist_ok=True)

def run(args,cwd=ROOT,check=True):
 return subprocess.run(args,cwd=cwd,check=check,timeout=600)

def main():
 lock=open(LOGS/'state-auto.lock','a+b')
 if os.name=='nt':
  import msvcrt
  try:
   lock.seek(0);lock.write(b'0');lock.flush();lock.seek(0);msvcrt.locking(lock.fileno(),msvcrt.LK_NBLCK,1)
  except OSError:
   print('Another state update is running; skipped.',flush=True);return 0
 with open(LOGS/'state-auto.log','a',encoding='utf-8') as log:
  oldout,olderr=sys.stdout,sys.stderr
  sys.stdout=sys.stderr=log
  # Child processes share the same log without console prompts.
  def command(args,cwd=ROOT,check=True):
   return subprocess.run(args,cwd=cwd,stdout=log,stderr=log,check=check,timeout=600)
  work=None
  try:
   print('\nSTART '+datetime.now().isoformat(),flush=True)
   command(['git','fetch','origin','main'])
   work=Path(tempfile.mkdtemp(prefix='SRDM_STATE_'))/'checkout'
   command(['git','worktree','add','--detach',str(work),'origin/main'])
   result=command([sys.executable,'-u','scripts_local/update_shramik_state.py'],work,False)
   status=work/'shramik-state-refresh-status.js'
   if not status.exists():raise RuntimeError('No source status generated')
   st=json.loads(status.read_text().split('=',1)[1].strip().rstrip(';'))
   if result.returncode==0 and st.get('success'):
    data=json.loads((work/'shramik-district-reports.js').read_text().split('=',1)[1].strip().rstrip(';'))
    if len(data.get('districts',{}))!=52:raise RuntimeError('Incomplete district data; not published')
    if not st.get('persondaysSuccess'):print('WARNING: Persondays retained; inspect source status.',flush=True)
   else:print('WARNING: Source refresh failed; previous district data retained.',flush=True)
   command(['git','add','--','shramik-district-reports.js','shramik-state-refresh-status.js'],work)
   diff=command(['git','diff','--cached','--quiet'],work,False)
   if diff.returncode==1:
    command(['git','-c','user.name=SRDM Auto Updater','-c','user.email=srdm-auto@users.noreply.github.com','commit','-m','Refresh 52 district data and source status'],work)
    command(['git','push','origin','HEAD:main'],work)
    print('Published state data/status.',flush=True)
   elif diff.returncode!=0:raise RuntimeError('Git verification failed')
   print('END '+datetime.now().isoformat(),flush=True)
   return result.returncode
  except Exception as exc:
   print('ERROR: '+str(exc),flush=True);return 1
  finally:
   if work:command(['git','worktree','remove','--force',str(work)],check=False)
   sys.stdout,sys.stderr=oldout,olderr
if __name__=='__main__':sys.exit(main())
