"""Fetch official received-work GP counts; never substitute Bhuvan planning counts."""
import json, re, sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path.cwd()
OUTPUT = 'yuktdhara-received-data.js'

def norm(value):
    return re.sub(r'[^A-Z0-9\u0900-\u097F]', '', str(value).upper())

def jan(value):
    n = norm(value)
    return {'SATNA':'SOHAWAL','RAMPORBAGHELAN':'RAMPURBAGHELAN'}.get(n,n)

def read_js(path):
    return json.loads(path.read_text(encoding='utf-8-sig').split('=',1)[1].strip().rstrip(';'))

def number(value):
    s = str(value).strip().replace(',','')
    if not re.fullmatch(r'\d+',s): raise ValueError('Missing/invalid source count: '+s)
    return int(s)

# Flatten spans and retain links at their original column positions.
GRID = '''tables=>tables.map(t=>{const g=[];Array.from(t.rows).filter(r=>r.closest('table')===t).forEach((r,y)=>{g[y]??=[];let x=0;Array.from(r.cells).forEach(c=>{while(g[y][x]!==undefined)x++;const v={text:c.innerText.trim(),links:Array.from(c.querySelectorAll('a[href]')).map(a=>a.href)};for(let dy=0;dy<c.rowSpan;dy++){g[y+dy]??=[];for(let dx=0;dx<c.colSpan;dx++)g[y+dy][x+dx]=v}x+=c.colSpan})});return g})'''

def gp_counts(tables, expected_gp, expected_works):
    candidates=[]
    for table in tables:
        for hi, header in enumerate(table):
            names=[re.sub(r'\s+',' ',c['text']).lower() for c in header]
            gps=[i for i,s in enumerate(names) if re.fullmatch(r'(?:gram\s*)?panchayat(?:\s*name)?|gp\s*name',s)]
            works=[i for i,s in enumerate(names) if re.search(r'(?:works?\s+received|received\s+(?:from\s+(?:yd|yuktdhara)|works?))',s) and not re.search(r'gp|panchayat',s)]
            if len(gps)!=1 or len(works)!=1:continue
            gi,wi=gps[0],works[0]; out={}; totals=[]
            for row in table[hi+1:]:
                if max(gi,wi)>=len(row):continue
                name=row[gi]['text'].strip()
                if re.search(r'\btotal\b',name,re.I):
                    totals.append(number(row[wi]['text']));continue
                if not name or norm(name) in {'PANCHAYAT','GRAM PANCHAYAT','PANCHAYATNAME'}:continue
                try:count=number(row[wi]['text'])
                except ValueError:continue
                key=norm(name)
                if key in out:raise RuntimeError('Duplicate GP in received-work source: '+name)
                out[key]={'gp':name,'worksReceived':count}
            if sum(x['worksReceived'] for x in out.values())!=expected_works:continue
            if sum(x['worksReceived']>0 for x in out.values())!=expected_gp:continue
            if any(t!=expected_works for t in totals):continue
            candidates.append(out)
    if not candidates:raise RuntimeError('GP detail missing or does not reconcile with official block totals')
    if any(c!=candidates[0] for c in candidates):raise RuntimeError('Ambiguous GP received-work tables')
    return list(candidates[0].values())

def aggregate(blocks, details, mapping):
    master={}
    for m in mapping:
        k=(jan(m['janpad']),norm(m['gp']))
        engineer=m.get('engineer','').strip()
        if not engineer or engineer.lower()=='unmapped':continue
        if k in master and master[k]!=engineer:raise RuntimeError('Conflicting GP engineer mapping: '+str(k))
        master[k]=engineer
    sums=defaultdict(lambda:{'gpReceived':0,'worksReceived':0})
    for block in blocks:
        b=jan(block['block']); rows=details[b]
        if sum(r['worksReceived'] for r in rows)!=block['worksReceived'] or sum(r['worksReceived']>0 for r in rows)!=block['gpReceived']:
            raise RuntimeError('Block/GP totals mismatch: '+b)
        for r in rows:
            if not r['worksReceived']:continue
            k=(b,norm(r['gp']))
            if k not in master:raise RuntimeError('Received GP has no exact engineer mapping: '+str(k))
            a=sums[(b,master[k])];a['gpReceived']+=1;a['worksReceived']+=r['worksReceived']
    # Explicit validated zeros for engineers with no receiving GP.
    for (b,g),e in master.items():sums[(b,e)]
    return [{'janpad':b,'engineer':e,**v} for (b,e),v in sorted(sums.items())]

def collect():
    from playwright.sync_api import sync_playwright
    summary=read_js(ROOT/'yuktdhara-official-data.js')
    blocks=summary['rows']
    if len(blocks)!=8 or len({jan(b['block']) for b in blocks})!=8:raise RuntimeError('Eight unique official blocks required')
    mapping=read_js(ROOT/'yuktdhara-data.js')['mapping']
    with sync_playwright() as p:
        try:browser=p.chromium.launch(channel='chrome',headless=True)
        except Exception:browser=p.chromium.launch(headless=True)
        try:
            context=browser.new_context();page=context.new_page()
            def fetch(url):
                if urlparse(url).hostname!='vbgramgrep.dord.gov.in':raise RuntimeError('Unexpected official link host')
                response=page.goto(url,wait_until='domcontentloaded',timeout=60000)
                if response and response.status>=400:raise RuntimeError('Official HTTP '+str(response.status))
                return page.locator('table').evaluate_all(GRID)
            top=fetch(summary['source']);links={}
            for table in top:
                for row in table:
                    if len(row)<5:continue
                    b=jan(row[1]['text'])
                    if b in {jan(x['block']) for x in blocks}:
                        urls=row[3]['links']
                        if urls:links[b]=urls[0]
            details={}
            for block in blocks:
                b=jan(block['block'])
                if block['gpReceived']==0 and block['worksReceived']==0:details[b]=[];continue
                if b not in links:raise RuntimeError('GP drill-down link missing: '+b)
                details[b]=gp_counts(fetch(links[b]),block['gpReceived'],block['worksReceived'])
            rows=aggregate(blocks,details,mapping)
        finally:browser.close()
    return {'success':True,'updatedAt':datetime.now(timezone.utc).isoformat(),'officialDate':summary.get('officialDate'),'blocks':blocks,'rows':rows,'source':summary['source']}

def main():
    output=ROOT/OUTPUT
    try:payload=collect();print('Yuktdhara received GP/engineer counts reconciled for 8 blocks',flush=True)
    except Exception as e:
        payload=read_js(output) if output.exists() else {'rows':[],'blocks':[]}
        payload.update(success=False,message=str(e))
        print('YUKTDHARA RECEIVED NOT REFRESHED: '+str(e)+'; previous detail retained with its original date.',flush=True)
    payload['checkedAt']=datetime.now(timezone.utc).isoformat()
    temp=output.with_suffix('.tmp');temp.write_text('window.YUKTDHARA_RECEIVED='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8');temp.replace(output)

if __name__=='__main__':main()
