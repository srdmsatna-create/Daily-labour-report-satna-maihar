"""Fetch official received-work GP counts; never substitute Bhuvan planning counts."""
import json, os, re, sys, time
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

def gp_counts(tables, expected_gp, expected_works, expected_created=None, total_gp=None):
    candidates=[]
    diagnostics=[]
    for table in tables:
        for hi, header in enumerate(table):
            names=[re.sub(r'\s+',' ',c['text']).lower() for c in header]
            gps=[i for i,s in enumerate(names) if re.fullmatch(r'(?:gram\s*)?panchayats?(?:\s*name)?|gp\s*name',s)]
            works=[i for i,s in enumerate(names) if re.search(r'(?:works?\s+received|received\s+(?:from\s+(?:yd|yuktdhara)|works?))',s) and not re.search(r'gp|panchayat',s)]
            if len(gps)!=1 or len(works)!=1:continue
            gi,wi=gps[0],works[0]; out={}; totals=[]
            created=[i for i,s in enumerate(names) if 'works created' in s and ('vb-g' in s or 'vb g' in s)]
            ci=created[0] if len(created)==1 else None
            for row in table[hi+1:]:
                # Official tables have a second header row numbered 1,2,3,... .
                # It is column numbering, not a GP named "2" with three works.
                if all(c['text'].strip()==str(i+1) for i,c in enumerate(row)):continue
                if max(gi,wi)>=len(row):continue
                name=row[gi]['text'].strip()
                if re.search(r'\btotal\b',name,re.I):
                    totals.append(number(row[wi]['text']));continue
                if not name or norm(name) in {'PANCHAYAT','GRAM PANCHAYAT','PANCHAYATNAME'}:continue
                try:count=number(row[wi]['text'])
                except ValueError:continue
                key=norm(name)
                if key in out:raise RuntimeError('Duplicate GP in received-work source: '+name)
                out[key]={'gp':name,'worksReceived':count,'detailLinks':row[wi].get('links',[])}
                if ci is not None:
                    value=number(row[ci]['text'])
                    if value>count:raise RuntimeError('Created works exceed received GP works: '+name)
                    out[key]['worksCreated']=value
            actual_works=sum(x['worksReceived'] for x in out.values())
            actual_gp=sum(x['worksReceived']>0 for x in out.values())
            actual_created=sum(x.get('worksCreated',0) for x in out.values())
            diagnostics.append('received GPs '+str(actual_gp)+'/'+str(expected_gp)+', received works '+str(actual_works)+'/'+str(expected_works)+', created works '+str(actual_created)+'/'+str(expected_created)+', created column '+str(ci is not None))
            if total_gp is None:
                if actual_works!=expected_works or actual_gp!=expected_gp:continue
            elif len(out)!=total_gp or not totals:continue
            if any(t!=actual_works for t in totals):continue
            if expected_created is not None and (ci is None or sum(x.get('worksCreated',0) for x in out.values())!=expected_created):continue
            candidates.append(out)
    if not candidates:raise RuntimeError('GP detail does not reconcile: '+('; '.join(diagnostics) if diagnostics else 'received-work GP headers not found'))
    if any(c!=candidates[0] for c in candidates):raise RuntimeError('Ambiguous GP received-work tables')
    return list(candidates[0].values())

def work_types(tables, expected):
    candidates=[]
    for table in tables:
        for hi, header in enumerate(table):
            names=[re.sub(r'\s+',' ',c['text']).lower() for c in header]
            cols=[i for i,s in enumerate(names) if re.fullmatch(r'(?:permissible work|type of work|work type|work category|category of work|कार्य का प्रकार|कार्य प्रकार)',s)]
            if len(cols)!=1:continue
            ti=cols[0]; counts=defaultdict(int)
            for row in table[hi+1:]:
                if all(c['text'].strip()==str(i+1) for i,c in enumerate(row)):continue
                if ti>=len(row) or any(re.fullmatch(r'(?:grand )?total',c['text'].strip(),re.I) for c in row):continue
                try:number(row[0]['text'])
                except ValueError:continue
                value=row[ti]['text'].strip()
                if value:counts[value]+=1
            if sum(counts.values())==expected:candidates.append(dict(counts))
    if not candidates or any(x!=candidates[0] for x in candidates):
        raise RuntimeError('Work types missing or do not reconcile with received works')
    return candidates[0]

def aggregate(blocks, details, mapping):
    master={}
    for m in mapping:
        k=(jan(m['janpad']),norm(m['gp']))
        engineer=m.get('engineer','').strip()
        if not engineer or engineer.lower()=='unmapped':continue
        if k in master and master[k]!=engineer:raise RuntimeError('Conflicting GP engineer mapping: '+str(k))
        master[k]=engineer
    sums=defaultdict(lambda:{'gpReceived':0,'worksReceived':0,'workTypes':{},'typesComplete':True,'worksCreated':0})
    for block in blocks:
        b=jan(block['block']); rows=details[b]
        if sum(r['worksReceived'] for r in rows)!=block['worksReceived'] or sum(r['worksReceived']>0 for r in rows)!=block['gpReceived']:
            raise RuntimeError('Block/GP totals mismatch: '+b)
        if sum(r.get('worksCreated',0) for r in rows)!=block['worksCreated']:
            raise RuntimeError('Created work GP/block totals mismatch: '+b)
        for r in rows:
            if not r['worksReceived']:continue
            k=(b,norm(r['gp']))
            if k not in master:raise RuntimeError('Received GP has no exact engineer mapping: '+str(k))
            a=sums[(b,master[k])];a['gpReceived']+=1;a['worksReceived']+=r['worksReceived'];a['worksCreated']+=r['worksCreated']
            if 'workTypes' not in r:a['typesComplete']=False
            else:
                for label,count in r['workTypes'].items():a['workTypes'][label]=a['workTypes'].get(label,0)+count
    # Explicit validated zeros for engineers with no receiving GP.
    for (b,g),e in master.items():sums[(b,e)]
    return [{'janpad':b,'engineer':e,**v} for (b,e),v in sorted(sums.items())]


def block_counts(tables, previous):
    expected={jan(b['block']):b for b in previous}
    found={}
    fields=('gp','gpReceived','worksReceived','worksCreated','yetToStart','ongoing','completed')
    for table in tables:
        for row in table:
            if len(row)<9 or jan(row[1]['text']) not in expected:continue
            key=jan(row[1]['text'])
            try:values=[number(row[i]['text']) for i in range(2,9)]
            except ValueError:continue
            record={'block':expected[key]['block'],**dict(zip(fields,values))}
            if record['gp']!=expected[key]['gp']:raise RuntimeError('Official GP master changed: '+key)
            if key in found and found[key]!=record:raise RuntimeError('Conflicting official block rows: '+key)
            found[key]=record
    if set(found)!=set(expected):raise RuntimeError('Eight current official Yuktdhara parent rows required')
    return [found[jan(b['block'])] for b in previous]

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
            context=browser.new_context(extra_http_headers={'Cache-Control':'no-cache','Pragma':'no-cache'})
            from vbgram_access import session_cookies
            cookies=session_cookies()
            if cookies:context.add_cookies(cookies)
            page=context.new_page()
            def fetch(url, timeout=60000):
                if urlparse(url).hostname!='vbgramgrep.dord.gov.in':raise RuntimeError('Unexpected official link host')
                response=page.goto(url,wait_until='domcontentloaded',timeout=timeout)
                if response and response.status>=400:raise RuntimeError('Official HTTP '+str(response.status))
                return page.locator('table').evaluate_all(GRID)
            top=fetch(summary['source']);links={}
            blocks=block_counts(top,blocks)
            date_node=page.locator('#ContentPlaceHolder1_Shedule_updated_date')
            if date_node.count():summary['officialDate']=date_node.inner_text().strip()
            summary['rows']=[dict(b) for b in blocks]
            summary['updatedAt']=datetime.now(timezone.utc).isoformat()
            print('Using current browser-session Yuktdhara parent totals for all 8 blocks',flush=True)
            debug=ROOT/'data'/'yuktdhara-received-debug';debug.mkdir(parents=True,exist_ok=True)
            (debug/'block-tables.json').write_text(json.dumps(top,ensure_ascii=False),encoding='utf-8')
            for table in top:
                for row in table:
                    if len(row)<5:continue
                    b=jan(row[1]['text'])
                    if b in {jan(x['block']) for x in blocks}:
                        # The portal can link the block name rather than the GP count.
                        urls=list(dict.fromkeys(u for i in (1,3,4) for u in row[i]['links']))
                        if urls:links[b]=urls
            details={}
            for block in blocks:
                b=jan(block['block'])
                if block['gpReceived']==0 and block['worksReceived']==0:details[b]=[];continue
                if b not in links:raise RuntimeError('GP drill-down link missing: '+b)
                errors=[]
                for attempt in range(1,4):
                    for link_index,url in enumerate(links[b]):
                        try:
                            tables=fetch(url)
                            (debug/(b+'-attempt-'+str(attempt)+'-link-'+str(link_index)+'.json')).write_text(json.dumps(tables,ensure_ascii=False),encoding='utf-8')
                            (debug/(b+'-tables.json')).write_text(json.dumps(tables,ensure_ascii=False),encoding='utf-8')
                            details[b]=gp_counts(tables,block['gpReceived'],block['worksReceived'],block['worksCreated'],block['gp'])
                            break
                        except Exception as e:
                            message=b+' attempt '+str(attempt)+': '+str(e)
                            errors.append(message)
                            print(message,flush=True)
                    if b in details:break
                    if attempt<3:time.sleep(2*attempt)
                if b not in details:raise RuntimeError(b+': '+'; '.join(errors))
            for block in blocks:
                rr=details[jan(block['block'])]
                block['summaryGpReceived']=block['gpReceived'];block['summaryWorksReceived']=block['worksReceived']
                block['gpReceived']=sum(r['worksReceived']>0 for r in rr)
                block['worksReceived']=sum(r['worksReceived'] for r in rr)
            work_debug=[]
            pending=sum(gp['worksReceived']>0 for gp_rows in details.values() for gp in gp_rows)
            done=0
            print('Fetching work types for '+str(pending)+' receiving GPs...',flush=True)
            for block_name,gp_rows in details.items():
                for gp in gp_rows:
                    if not gp['worksReceived']:continue
                    done+=1
                    print('Work details ['+str(done)+'/'+str(pending)+'] '+block_name+' / '+gp['gp'],flush=True)
                    for url in gp.get('detailLinks',[]):
                        if not url.startswith('https://vbgramgrep.dord.gov.in/'):continue
                        try:
                            tables=fetch(url, timeout=20000)
                            work_debug.append({'block':block_name,'gp':gp['gp'],'worksReceived':gp['worksReceived'],'tables':tables})
                            (debug/'work-details.json').write_text(json.dumps(work_debug,ensure_ascii=False),encoding='utf-8')
                            gp['workTypes']=work_types(tables,gp['worksReceived'])
                            print('  Verified '+str(gp['worksReceived'])+' work types.',flush=True)
                            break
                        except Exception as e:
                            gp['typeMessage']=str(e)
                            print('  Work detail unavailable: '+str(e)[:160],flush=True)
                            if not any(v['block']==block_name and v['gp']==gp['gp'] for v in work_debug):
                                work_debug.append({'block':block_name,'gp':gp['gp'],'worksReceived':gp['worksReceived'],'error':str(e)})
                            (debug/'work-details.json').write_text(json.dumps(work_debug,ensure_ascii=False),encoding='utf-8')
            rows=aggregate(blocks,details,mapping)
        finally:browser.close()
    (ROOT/'yuktdhara-official-data.js').write_text('window.YUKTDHARA_REPORT='+json.dumps(summary,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
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
