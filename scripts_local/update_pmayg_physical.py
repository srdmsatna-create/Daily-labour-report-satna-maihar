"""R-7.1: VBGRAMG physically completed PMAY-G cohort and both portal ledgers."""
import csv, hashlib, html, json, math, os, re, sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from zoneinfo import ZoneInfo
from update_pmayg import NREGA_URL, VBG_URL, norm, block_key, open_with_retry
import update_mis_612_work_details as mis
from update_ek_bagiya_payment import cells, number, ledger_amounts
ROOT=mis.ROOT
PREFIX='ctl00$ContentPlaceHolder1$'

def fetch(url, fy, status, kinds=None):
    kinds=kinds or ['Constr of PMAY-G House for Individuals','IAY Houses']
    today=datetime.now(ZoneInfo('Asia/Kolkata')).date().isoformat()
    cache=Path(os.environ.get('PMAY_FETCH_CACHE_DIR',str(ROOT/'data'/'pmayg-fetch-cache')))/'physical';cache.mkdir(parents=True,exist_ok=True)
    key=hashlib.sha256((url+'|'+fy+'|'+status+'|'+today+'|v1'+('|'+';'.join(kinds) if len(kinds)!=2 else '')).encode()).hexdigest()
    path=cache/(key+'.json')
    if path.exists():
        try:return json.loads(path.read_text(encoding='utf-8'))
        except json.JSONDecodeError:path.unlink(missing_ok=True)
    opener=mis.session_opener();page,base=open_with_retry(opener,url)
    fields=mis.hidden_fields(page);mis.selected_values(page,fields)
    fields.update({'__EVENTTARGET':PREFIX+'ddl_dist',PREFIX+'ddl_state':'17',PREFIX+'ddl_dist':'1712'})
    page,base=open_with_retry(opener,mis.form_action(page,base),mis.urllib.parse.urlencode(fields).encode())
    if 'value="1712006"' not in page:raise ValueError('Eight-Janpad form missing')
    output=[];dates=set()
    for kind in kinds:
        fields=mis.hidden_fields(page);mis.selected_values(page,fields)
        fields.update({'__EVENTTARGET':'',PREFIX+'ddl_blk':'ALL',PREFIX+'ddl_pan':'ALL',PREFIX+'Ddlworkcategory':'ALL',PREFIX+'ddlFin_year':fy,PREFIX+'Ddlwork_status':status,PREFIX+'ddlprostatus':kind,PREFIX+'filter':'ALL',PREFIX+'Button1':'Submit'})
        print('Fetching '+('VBGRAMG' if 'vbgram' in url else 'MGNREGA')+' '+fy+' '+status+' '+kind,flush=True)
        result,_=open_with_retry(opener,mis.form_action(page,base),mis.urllib.parse.urlencode(fields).encode())
        if not re.search('Amount paid since inception',result,re.I):raise ValueError('Payment header missing')
        rows=list(cells(result))
        if not rows and not re.search(r'No\s+(?:Record|Data)',result,re.I):raise ValueError('Unverified empty report')
        for c in rows:
            if not re.search('PMAY|IAY',c[7]+' '+c[10]+' '+c[11],re.I):raise ValueError('PMAY filter failed')
            if status=='06' and c[5].lower()!='physically completed':raise ValueError('Physical status mismatch')
            if fy!='ALL' and c[4] not in (fy,fy[:5]+fy[-2:]):raise ValueError('Work start FY mismatch')
        date=re.search(r'Report last Updated on:\s*(\d{2}/\d{2}/\d{4})',result)
        if not date:raise ValueError('Official source date missing')
        dates.add(date.group(1));output.extend(rows)
        print('Received '+str(len(rows))+' works',flush=True)
    if len(dates)!=1:raise ValueError('Inconsistent source dates')
    value={'rows':output,'date':dates.pop(),'fy':fy,'status':status}
    temp=path.with_suffix('.'+str(os.getpid())+'.tmp')
    temp.write_text(json.dumps(value,ensure_ascii=False),encoding='utf-8');os.replace(temp,path);return value

def compile_report(nrega, vbg, dates):
    def index(rr):
        out={}
        for c in rr:
            code=re.sub(r'\s+','',c[6]).upper()
            if code in out and out[code]!=c:raise ValueError('Conflicting duplicate '+code)
            out[code]=c
        return out
    ni=index(nrega);vi=index(vbg)
    master=list(csv.DictReader((ROOT/'gp-sector-engineer-master-25-09-2026.csv').open(encoding='utf-8-sig')))
    mapping={(block_key(m['Janpad']),norm(m[k])):m for m in master for k in ['Gram_Panchayat','GP_20Sep_Name']}
    rows=[]
    for code,c in vi.items():
        if c[5].lower()!='physically completed':raise ValueError('Cohort is not physically completed')
        m=mapping.get((block_key(c[2]),norm(c[3])))
        if not m:raise ValueError('GP mapping missing '+c[2]+'/'+c[3])
        a=ni.get(code)
        if a and (block_key(a[2])!=block_key(c[2]) or norm(a[3])!=norm(c[3])):raise ValueError('Source GP mismatch '+code)
        sources={}
        for system,rec in [('MGNREGA',a),('VBGRAMG',c)]:
            if rec is None:continue
            ledger,raw=ledger_amounts(rec,system)
            sources[system]={'booked':ledger['bsw']+ledger['bsm'],'paid':ledger['pw']+ledger['pm'],'wageBooked':ledger['bsw'],'materialBooked':ledger['bsm'],'wagePaid':ledger['pw'],'materialPaid':ledger['pm'],'totalMandays':number(rec[24]),'currentMandays':number(rec[25]),'rawColumns':raw,'status':rec[5],'workStartFY':rec[4]}
        booked=sum(x['booked'] for x in sources.values());paid=sum(x['paid'] for x in sources.values())
        nmd=sources.get('MGNREGA',{}).get('totalMandays',0);vmd=sources['VBGRAMG']['currentMandays']
        rows.append(dict(code=code,name=c[7],type=c[11] or c[10],status='Physically Completed',fy=c[4],district=m['District'],janpad=c[2],gp=c[3],engineer=m['Sub_Engineer'],cluster=m['Sector'],sanction=number(c[15]),booked=booked,paid=paid,pending=round(booked-paid,2),sanctionBalance=round(number(c[15])-booked,2),nregaMandays=nmd,vbgMandays=vmd,mandays=nmd+vmd,sources=sources,coverage='Both' if a else 'VBGRAMG only',amountMismatch=paid>booked+0.01))
    if not rows:raise ValueError('No verified physically completed PMAY-G works')
    d=dict(schemaVersion=1,basis='vbg-physical-pmayg-v1',fetchedAt=datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),sourceDates=dates,sourceUrls={'MGNREGA':NREGA_URL,'VBGRAMG':VBG_URL},cohort='VBGRAMG FY 2026-27 Physically Completed PMAY-G/IAY, all work-start years',nregaWorkStartFY=sorted({c[4] for c in vbg}),requestedMGNREGAYears=['2025-2026','2026-2027'],vbgReportFY='2026-2027',nregaRows=len(ni),vbgRows=len(vi),rows=rows,bookedBasis='MGNREGA 21+22; VBGRAMG max(21,17)+max(22,18); one ledger per portal/work code',paidBasis='MGNREGA 23+24; VBGRAMG max(23,19)+max(24,20)',mandaysBasis='MGNREGA total (25) + VBGRAMG current FY (26); cumulative totals across snapshots are not added')
    validate(d);return d

def validate(d):
    if not set('MGNREGA '+fy for fy in {r['fy'] for r in d.get('rows',[])}).issubset(d.get('sourceDates',{})):raise ValueError('Older cohort financial-year source missing')
    if d.get('basis')!='vbg-physical-pmayg-v1' or not d.get('sourceDates') or not d.get('rows'):raise ValueError('Incomplete physical PMAY-G snapshot')
    if len({r['code'] for r in d['rows']})!=len(d['rows']) or len(d['rows'])!=d['vbgRows']:raise ValueError('Cohort deduplication mismatch')
    for r in d['rows']:
        if r['status']!='Physically Completed' or not r['cluster']:raise ValueError('Physical status/mapping invalid')
        if any(not math.isfinite(r[k]) or r[k]<0 for k in ['booked','paid','nregaMandays','vbgMandays','mandays']):raise ValueError('Invalid ledger')
        if abs(r['pending']-(r['booked']-r['paid']))>0.011 or r['mandays']!=r['nregaMandays']+r['vbgMandays']:raise ValueError('Physical ledger arithmetic failed')

def main():
    vbg=fetch(VBG_URL,'ALL','06')
    # Inception totals already contain 2025-26 and 2026-27. Include old-start
    # cohort works too; adding cumulative year snapshots would double count.
    def read_year(fy):
        kinds=sorted({c[11] for c in vbg['rows'] if c[4]==fy})
        # Two requested years retain their complete cached ledger; old cohorts
        # are read separately to avoid the portal's oversized ALL-year failure.
        return fetch(NREGA_URL,fy,'ALL',None if fy in ('2025-2026','2026-2027') else kinds)
    with ThreadPoolExecutor(max_workers=3) as pool:
        nrega=list(pool.map(read_year,sorted({c[4] for c in vbg['rows']},reverse=True)))
    d=compile_report([c for report in nrega for c in report['rows']],vbg['rows'],{'VBGRAMG 2026-27':vbg['date'],**{'MGNREGA '+r['fy']:r['date'] for r in nrega}})
    p=ROOT/'data/pmayg-physical-latest.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(d,ensure_ascii=False),encoding='utf-8');os.replace(tmp,p)
    print('SUCCESS R-7.1: '+str(len(d['rows']))+' verified works',flush=True)
if __name__=='__main__':
    try:main()
    except Exception as e:print('FAILED R-7.1; previous verified snapshot retained: '+str(e),flush=True);sys.exit(1)
