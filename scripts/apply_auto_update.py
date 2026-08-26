#!/usr/bin/env python3
import json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
st=json.loads((ROOT/'data'/'fetch-status.json').read_text(encoding='utf-8'))
mode=st.get('updateMode')
if mode=='workbook':
    cmd=[sys.executable,str(ROOT/'scripts'/'update_daily_report.py')]
    print('Applying official update mode:',mode)
    raise SystemExit(subprocess.call(cmd,cwd=ROOT))
elif mode=='summary':
    cmd=[sys.executable,str(ROOT/'scripts'/'merge_official_summary.py')]
    print('Applying official update mode:',mode)
    raise SystemExit(subprocess.call(cmd,cwd=ROOT))
elif mode=='workbook+summary':
    print('Applying official update mode:',mode)
    rc=subprocess.call([sys.executable,str(ROOT/'scripts'/'update_daily_report.py')],cwd=ROOT)
    if rc: raise SystemExit(rc)
    # Critical: live portal Screen-2 always runs LAST and therefore wins.
    raise SystemExit(subprocess.call([sys.executable,str(ROOT/'scripts'/'merge_official_summary.py')],cwd=ROOT))
else:
    raise SystemExit('No valid updateMode from official fetch')
