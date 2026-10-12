import requests,json,re
from bs4 import BeautifulSoup
from urllib.parse import urljoin
BASE='https://planner.nregsmp.org/reports/hierarchy.php?district=1712&financialYearId=2&status=4&view=block'
h=requests.get(BASE,headers={'User-Agent':'Mozilla/5.0'},timeout=45);h.raise_for_status();s=BeautifulSoup(h.text,'html.parser')
links=[]
for a in s.find_all('a',href=True):
    t=a.get_text(' ',strip=True).upper()
    if t in {'AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'}:
        u=urljoin(BASE,a['href'])
        if 'view=block' in u:u=u.replace('view=block','view=gp')
        elif 'view=' not in u:u += ('&' if '?' in u else '?')+'view=gp'
        links.append((t,u))
        break
out={}
for name,u in links[:1]:
    r=requests.get(u,headers={'User-Agent':'Mozilla/5.0'},timeout=45);r.raise_for_status();bs=BeautifulSoup(r.text,'html.parser')
    arr=[]
    for ti,table in enumerate(bs.find_all('table')):
        rows=[]
        for tr in table.find_all('tr')[:8]:
            cells=[c.get_text(' ',strip=True) for c in tr.find_all(['th','td'])]
            if cells:rows.append(cells)
        if rows:arr.append({'table':ti,'rows':rows})
    out[name]={'url':u,'tables':arr}
open('planner-gp-probe.json','w',encoding='utf-8').write(json.dumps(out,ensure_ascii=False,indent=2))
print(json.dumps(out,ensure_ascii=False)[:12000])
