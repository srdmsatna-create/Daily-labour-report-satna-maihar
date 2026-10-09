from pathlib import Path
from urllib.parse import urljoin
import json,re,datetime
import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

BASE='https://planner.nregsmp.org/reports/hierarchy.php?district=1712&financialYearId=2&status=4&view=block'
HEADERS={'User-Agent':'Mozilla/5.0 SRDM-SATNA/1.0'}
SESSION=requests.Session()
SESSION.mount('https://',HTTPAdapter(max_retries=Retry(total=2,connect=2,read=2,status=2,backoff_factor=1,status_forcelist=[502,503,504],allowed_methods=['GET'])))
JANPADS={'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}

def nint(s):
    m=re.search(r'[\d,]+',str(s))
    return int(m.group(0).replace(',','')) if m else 0

def get(url):
    r=SESSION.get(url,headers=HEADERS,timeout=(15,45))
    r.raise_for_status();return r.text

def rows_from_table(table):
    out=[]
    for tr in table.find_all('tr'):
        cells=[c.get_text(' ',strip=True) for c in tr.find_all(['th','td'])]
        if cells: out.append((tr,cells))
    return out

html=get(BASE); soup=BeautifulSoup(html,'html.parser')
blocks=[]; block_links={}
for table in soup.find_all('table'):
    for tr,c in rows_from_table(table):
        # Block-level row layout:
        # 0 #, 1 Block, 2 Spill total, 3 housing, 4 non-housing, 5 spill labour cost,
        # 6 spill total cost, 7 NEW WORK COUNT, 8 mat cost, 9 labour cost, 10 total cost,
        # 11 agri %, 12 NRM %, 13 TOTAL WORKS, ...
        if len(c)>=14 and c[0].strip().isdigit() and c[1].strip().upper() in JANPADS:
            name=c[1].strip().upper(); new=nint(c[7]); total=nint(c[13]); spill=nint(c[2])
            a=next((a for a in tr.find_all('a',href=True) if a.get_text(' ',strip=True).upper()==name and 'view=gp' in a['href']),None)
            if a: block_links[name]=urljoin(BASE,a['href'])
            blocks.append({'janpad':name,'newWorks':new,'spillWorks':spill,'totalWorks':total})

for name in [b['janpad'] for b in blocks]:
    if name not in block_links:
        for a in soup.find_all('a',href=True):
            if a.get_text(' ',strip=True).upper()==name:
                block_links[name]=urljoin(BASE,a['href']);break

gps=[]
for b in blocks:
    name=b['janpad']; url=block_links.get(name)
    if not url: continue
    if 'view=block' in url: url=url.replace('view=block','view=gp')
    elif 'view=' not in url: url += ('&' if '?' in url else '?')+'view=gp'
    try: bs=BeautifulSoup(get(url),'html.parser')
    except Exception as e:
        print('GP fetch failed',name,e);continue
    seen=set()
    for table in bs.find_all('table'):
        for tr,c in rows_from_table(table):
            # GP-level row layout verified from official Planner:
            # 0 #, 1 Block, 2 GP, 3 Resolution, 4 SPILL TOTAL, 5 housing, 6 non-housing,
            # 7 spill labour cost, 8 spill total cost, 9 NEW WORK COUNT,
            # 10 material, 11 labour, 12 total cost, 13 agri %, 14 NRM %,
            # 15 TOTAL WORKS, 16 material, 17 labour, 18 total cost, 19 mandays.
            # A block-filtered GP page omits the Block column (19 cells).
            # The district-wide GP page includes it (20 cells).
            offset=0 if len(c)==20 and c[1].strip().upper()==name else -1 if len(c)==19 else None
            if offset is not None and c[0].strip().isdigit():
                gp=c[2+offset].strip()
                if not gp or gp.upper() in {'TOTAL','GRAND TOTAL'}: continue
                spill=nint(c[4+offset]); new=nint(c[9+offset]); total=nint(c[15+offset])
                key=(name,gp.upper())
                if key in seen: continue
                seen.add(key)
                gps.append({'janpad':name,'panchayat':gp,'newWorks':new,'spillWorks':spill,'totalWorks':total})

# Validation: GP sums must reconcile to each Janpad's official counts.
validation=[]
for b in blocks:
    rr=[x for x in gps if x['janpad']==b['janpad']]
    validation.append({
        'janpad':b['janpad'],
        'gpCount':len(rr),
        'newWorksGpSum':sum(x['newWorks'] for x in rr),
        'newWorksJanpad':b['newWorks'],
        'spillGpSum':sum(x['spillWorks'] for x in rr),
        'spillJanpad':b['spillWorks'],
        'ok':bool(rr) and sum(x['newWorks'] for x in rr)==b['newWorks'] and sum(x['spillWorks'] for x in rr)==b['spillWorks'] and sum(x['totalWorks'] for x in rr)==b['totalWorks']
    })

payload={
 'financialYear':'2026-2027','district':'SATNA',
 'metric':'Number Of New Works Taken In Planner Portal',
 'source':BASE,'updatedAt':datetime.datetime.now(datetime.timezone.utc).isoformat(),
 'blocks':blocks,'panchayats':gps,'validation':validation,
 'totals':{'janpads':len(blocks),'panchayats':len(gps),'newWorks':sum(x['newWorks'] for x in blocks),'spillWorks':sum(x['spillWorks'] for x in blocks),'totalWorks':sum(x['totalWorks'] for x in blocks)}
}
Path('planner-portal-data.js').write_text('window.PLANNER_PORTAL_DATA='+json.dumps(payload,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print(json.dumps(payload['totals'],ensure_ascii=False))
print(json.dumps(validation,ensure_ascii=False))
