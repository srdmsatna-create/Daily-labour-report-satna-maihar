#!/usr/bin/env python3
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/'auto-data.js'
s=p.read_text(encoding='utf-8')
m=re.search(r'window.AUTO_REPORT=(.*);\s*$',s,re.S)
if not m: raise SystemExit('AUTO_REPORT not found')
d=json.loads(m.group(1)); meta=d.get('meta',{})
rows=d.get('rows',[]); daily=d.get('daily',[]); official=d.get('official',[])
if not rows or not daily or not official: raise SystemExit('Missing rows/daily/official data')

def sm(a,k): return sum(float(x.get(k) or 0) for x in a)
gp=sm(daily,'totalGP'); prog=sm(daily,'gpsProgress'); mr=sm(daily,'worksMR'); mrs=sm(daily,'mrs'); labour=sm(daily,'labour')
if gp < 600 or gp > 800: raise SystemExit(f'Total GP out of safe range: {gp}')
if not (0 <= prog <= gp): raise SystemExit('GP progress invalid')
if mr <= 0: raise SystemExit('Works with MR is zero — reject publish')
if mrs <= 0: raise SystemExit('Muster Rolls is zero — reject publish')
if labour <= 0: raise SystemExit('Labour Engagement is zero — reject publish')
if sm(official,'ongoingAll') <= 0: raise SystemExit('Official ongoing works is zero')
print(json.dumps({'gp':gp,'progress':prog,'dysfunctional':gp-prog,'worksMR':mr,'musterRolls':mrs,'labour':labour,'officialOngoing':sm(official,'ongoingAll'),'source':meta.get('source')},ensure_ascii=False,indent=2))
