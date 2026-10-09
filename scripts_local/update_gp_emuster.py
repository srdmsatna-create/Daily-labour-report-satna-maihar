"""Laptop Chrome: official block -> GP -> column 6 -> work list. Fail closed."""
import argparse, json, re, sys, os
from pathlib import Path
from datetime import datetime, timezone
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
TYPES = ['PMAY-G','CC Road','Gravel Road','Play Ground','Khet Talab','Dug Pond','Old Water Bodies','Water Structure','Ek Bagiya','Other Plantation','Other Works']
BLOCKS = {'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}
GRID = """()=>Array.from(document.querySelectorAll('table')).map(t=>{const g=[];Array.from(t.rows).filter(r=>r.closest('table')===t).forEach((r,y)=>{g[y]??=[];let x=0;Array.from(r.cells).forEach(c=>{while(g[y][x]!==undefined)x++;const v={text:c.innerText.trim(),links:Array.from(c.querySelectorAll('a[href]')).map(a=>a.href)};for(let dy=0;dy<c.rowSpan;dy++){g[y+dy]??=[];for(let dx=0;dx<c.colSpan;dx++)g[y+dy][x+dx]=v}x+=c.colSpan})});return g})"""

def clean(v): return re.sub(r'\s+', ' ', str(v or '')).strip()
def key(v): return re.sub(r'[^A-Z0-9\u0900-\u097f]', '', clean(v).upper())
def block(v):
    v=clean(v).upper()
    return {'SOHAWAL':'SATNA','RAMPURBAGHELAN':'RAMPUR BAGHELAN'}.get(v,v)
def count(v):
    s=clean(v).replace(',','')
    if not re.fullmatch(r'\d+',s): raise ValueError('Invalid official count: '+s)
    return int(s)
def read_js(path):
    s=path.read_text(encoding='utf-8-sig');return json.loads(s.split('=',1)[1].strip().rstrip(';'))
def classify(name, kind):
    n=clean(name).lower(); t=(n+' '+clean(kind).lower())
    if re.search(r'pmay|pradhan.*awas|प्रधान.*आवास',t):return 'PMAY-G'
    if re.search(r'^(?:ek\s+)?bagiya\b|^एक\s+बगिया|^(?:एक\s+)?माँ.*बगिया|^ek\s+ma+a?\s+ke\s+naam',n):return 'Ek Bagiya'
    if re.search(r'khet\s*talab|farm\s*pond|खेत\s*तालाब',t):return 'Khet Talab'
    if re.search(r'dug\s*pond|डग\s*पोंड|डुग\s*पोंड',t):return 'Dug Pond'
    if re.search(r'old\s*water|renovation.*(?:water\s*bod|traditional\s*water)|पुरान.*(?:तालाब|जल)',t):return 'Old Water Bodies'
    if re.search(r'play\s*(?:ground|field)|खेल.*मैदान',t):return 'Play Ground'
    if re.search(r'gravel|grewal|greval|graval|ग्रेवल|ग्रेवल|मुरुम|mur+am',t):return 'Gravel Road'
    if re.search(r'(?:\bcc\b|cement\s*concrete|सीसी|सी\.सी).*?(?:road|सड़क)|(?:road|सड़क).*?(?:\bcc\b|cement\s*concrete)',t):return 'CC Road'
    if re.search(r'stop\s*dam|check\s*dam|water\s*(?:structure|conserv|harvest)|recharge|percolation|जल.*(?:संरक्षण|संचय)|स्टाप|चेक.*डैम',t):return 'Water Structure'
    if re.search(r'plantation|horticulture|afforestation|वृक्षारोपण|पौधरोपण|चारागाह|बगिया',t):return 'Other Plantation'
    return 'Other Works'

def blocks_from(tables):
    found={}
    for table in tables:
        for row in table:
            if len(row)<6:continue
            b=block(row[1]['text'])
            if b not in BLOCKS:continue
            try:gp,progress,labour,works=count(row[2]['text']),count(row[3]['text']),count(row[4]['text']),count(row[5]['text'])
            except ValueError:continue
            item={'janpad':b,'gps':gp,'progressGP':progress,'labour':labour,'works':works,'links':row[1]['links'],'workLinks':row[5]['links']}
            if b in found and found[b]!=item:raise ValueError('Ambiguous block rows: '+b)
            found[b]=item
    if set(found)!=BLOCKS:raise ValueError('Expected 8 Janpad hyperlinks; found '+str(list(found)))
    if sum(r['gps'] for r in found.values())!=695:raise ValueError('Expected 695 GPs in source')
    return found

def header_col(names, pattern):
    indices=[i for i,n in enumerate(names) if re.search(pattern,n,re.I)]
    return indices[0] if len(indices)==1 else None
def gps_from(tables, expected):
    candidates=[]
    for table in tables:
        for hi,row in enumerate(table):
            names=[clean(c['text']) for c in row]
            gi=header_col(names,r'^(?:gram\s*)?panchayat(?:s|\s*name)?$|^GP\s*name$')
            li=header_col(names,r'expected.*labour|labour.*engagement')
            wi=header_col(names,r'ongoing\s*works.*muster|works.*MR.*issued')
            mi=header_col(names,r'^No\.?\s*of\s*Muster\s*Rolls|^Muster\s*Rolls\s*\(MRs\)')
            if None in (gi,li,wi):continue
            pi=header_col(names,r'(?:GPs?|gram\s*panchayats?).*works?\s*in\s*progress|^works?\s*in\s*progress$')
            out={}
            for r in table[hi+1:]:
                if len(r)<=max(gi,li,wi) or re.search(r'\btotal\b',r[gi]['text'],re.I):continue
                try:labour,works=count(r[li]['text']),count(r[wi]['text'])
                except ValueError:continue
                gp=clean(r[gi]['text'])
                if not gp or gp.isdigit():continue
                gk=key(gp)
                if gk in out:raise ValueError('Duplicate GP: '+gp)
                out[gk]={'panchayat':gp,'labour':labour,'worksMR':works,'mrs':count(r[mi]['text']) if mi is not None else None,'workLinks':r[wi]['links'],'gpsProgress':count(r[pi]['text']) if pi is not None else None}
            if len(out)==expected['gps'] and sum(g['labour'] for g in out.values())==expected['labour'] and sum(g['worksMR'] for g in out.values())==expected['works']:candidates.append(list(out.values()))
    if not candidates:raise ValueError('GP table missing/incomplete or GP/labour/work totals do not match '+expected['janpad'])
    result=candidates[0]
    progress_verified=all(g['gpsProgress'] in (0,1) for g in result) and sum(g['gpsProgress'] or 0 for g in result)==expected['progressGP']
    for gp in result:
        gp['gpProgressVerified']=progress_verified
        if not progress_verified:
            gp['gpsProgress']=None
    return result

def works_from(tables, expected, gp=None):
    candidates=[]
    for table in tables:
        for hi,row in enumerate(table):
            names=[clean(c['text']) for c in row]
            ci=header_col(names,r'work\s*(?:code|id)')
            ni=header_col(names,r'work\s*name|name\s*of\s*(?:the\s*)?work')
            ti=header_col(names,r'^(?:permissible\s*work|type\s*of\s*work|work\s*type|work\s*category|category\s*of\s*work)$')
            li=header_col(names,r'expected.*labour|labour.*engagement|^(?:no\.?\s*of\s*)?(?:workers|labour|labourers)$')
            if ci is None or ni is None or ti is None:continue
            out={}
            for r in table[hi+1:]:
                if len(r)<=max(ci,ni,ti):continue
                code=clean(r[ci]['text']);name=clean(r[ni]['text']);kind=clean(r[ti]['text'])
                if not re.search(r'\d{5,}',code) or not name or not kind:continue
                item={'code':code,'name':name,'type':kind,'category':classify(name,kind),'panchayat':gp}
                item['labour']=count(r[li]['text']) if li is not None else None
                if code in out and out[code]!=item:raise ValueError('Conflicting duplicate work code '+code)
                out[code]=item
            if len(out)==expected:candidates.append(list(out.values()))
    if not candidates:raise ValueError('Work detail incomplete: expected '+str(expected)+' unique codes; pagination/export may be required')
    return candidates[0]

def main():
    a=argparse.ArgumentParser();a.add_argument('--url',required=True);a.add_argument('--headed',action='store_true');args=a.parse_args()
    from playwright.sync_api import sync_playwright
    master=read_js(ROOT/'auto-data.js')['rows']
    ongoing=read_js(ROOT/'ongoing-details.js')
    categories={clean(r['code']):r.get('finalCategory') or 'Other Works' for r in ongoing}
    work_categories=sorted(set(categories.values()))
    sys.path.insert(0,str(ROOT/'scripts'))
    from update_daily_report import final_category
    mapping={(block(r['janpad']),key(r['panchayat'])):r for r in master}
    debug=ROOT/'data'/'gp-emuster-debug';debug.mkdir(parents=True,exist_ok=True)
    def dump(name,value):(debug/(name+'.json')).write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8')
    output=[];all_works=[]
    with sync_playwright() as p:
        try:browser=p.chromium.launch(channel='chrome',headless=not args.headed)
        except Exception:browser=p.chromium.launch(headless=not args.headed)
        ctx=browser.new_context();page=ctx.new_page()
        def fetch(url):
            if urlparse(url).hostname!='vbgramgrep.dord.gov.in':raise ValueError('Unexpected source host')
            response=page.goto(url,wait_until='domcontentloaded',timeout=90000)
            if response and response.status>=400:raise ValueError('Official HTTP '+str(response.status))
            page.locator('table').first.wait_for(timeout=30000)
            return page.evaluate(GRID)
        try:
            top=fetch(args.url);dump('main',top);blocks=blocks_from(top)
            date_match=re.search(r'(?:report\s*)?last\s*updated(?:\s*on)?\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',page.locator('body').inner_text(),re.I)
            source_date=date_match.group(1).replace('/','-') if date_match else 'तिथि उपलब्ध नहीं'
            for b,summary in blocks.items():
                print('Janpad: '+b,flush=True)
                errors=[];gps=None
                for url in summary['links']:
                    try:
                        tables=fetch(url);dump(b+'-gp',tables);gps=gps_from(tables,summary);break
                    except Exception as e:errors.append(str(e))
                if gps is None:raise ValueError(b+' GP fetch failed: '+'; '.join(errors))
                for gp in gps:
                    mk=(b,key(gp['panchayat']))
                    if mk not in mapping:raise ValueError('GP engineer mapping missing: '+str(mk))
                    entry=mapping[mk].copy();entry.update({k:v for k,v in gp.items() if k!='workLinks'});entry['janpad']=b
                    counts=dict.fromkeys(work_categories,0);works=[]
                    if gp['worksMR']:
                        errors=[];verified=False
                        for url in gp['workLinks']:
                            try:
                                tables=fetch(url);dump(b+'-'+key(gp['panchayat'])+'-works',tables)
                                works=works_from(tables,gp['worksMR'],gp['panchayat']);verified=True;break
                            except Exception as e:errors.append(str(e))
                        if not verified:raise ValueError(b+'/'+gp['panchayat']+': '+'; '.join(errors))
                    for work in works:
                        work['category']=categories.get(work['code']) or final_category(work['name'],work['type'],'2026-2027')
                        counts[work['category']]=counts.get(work['category'],0)+1;work['janpad']=b
                    if all(w['labour'] is not None for w in works) and sum(w['labour'] for w in works)!=gp['labour']:
                        raise ValueError('Work labour total differs from official GP labour: '+b+'/'+gp['panchayat'])
                    entry['issuedWorks']=counts;output.append(entry);all_works.extend(works)
                    print('  '+gp['panchayat']+': '+str(len(works))+' works verified',flush=True)
        finally:browser.close()
    expected=sum(x['works'] for x in blocks.values())
    if len(output)!=695 or len({(r['janpad'],key(r['panchayat'])) for r in output})!=695:raise ValueError('695 unique GPs required')
    if len(all_works)!=expected or len({w['code'] for w in all_works})!=expected:raise ValueError('Work list total/unique codes mismatch')
    payload={'source':args.url,'fetchedAt':datetime.now(timezone.utc).isoformat(),'date':source_date,'gpProgressVerified':all(r.get('gpProgressVerified') for r in output),'totalWorks':expected,'workCategories':sorted(set(work_categories)|{w['category'] for w in all_works}),'rows':output,'works':all_works}
    path=ROOT/'gp-emuster-data.js';temp=path.with_suffix('.tmp')
    temp.write_text('window.GP_WORK_TYPE_MUSTER_REPORT = '+json.dumps(payload,ensure_ascii=False)+';\n',encoding='utf-8');os.replace(temp,path)
    print('SUCCESS: 695 GP, '+str(expected)+' unique MR-issued works, all master work categories. '+str(path),flush=True)

if __name__=='__main__':
    try:main()
    except Exception as e:print('FAILED: '+str(e)+'; previous report preserved.',file=sys.stderr);sys.exit(1)
