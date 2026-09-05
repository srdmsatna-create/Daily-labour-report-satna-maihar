#!/usr/bin/env python3
"""Fetch SATNA MIS 6.12 work rows for three statuses without browser automation."""
import csv, html, json, re, subprocess, sys, tempfile
import urllib.parse, urllib.request
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
OUT_CSV=ROOT/'data'/'Ongoing_Works_dynamic_work_details_latest.csv'
URL='https://vbgramgrep.dord.gov.in/VBGRAMG/dynamic_work_details.aspx?payload=4PmH2eRA9khYNUNqz1h5yt9D8POKLA7Afp0nercX3xt22K65u-hNco55SZiMHr78IufQr-Pyxw1-2tJEz-65UMtG5kOTBzCEHurJmRrAtoAIfVSTK-qhJdX02vLZMWrVbwM-oS9xX58g6SiO5ODhhFid9RqKvnwTnS-hLkXfa1-25phIp66JlphIcilUU7cK'
STATUSES=[('03','Ongoing'),('05','Completed'),('06','Physically Completed')]
FIELDS=['District Name','Janpad / Block Name','Panchayat Name','Work Start Fin Year','Work Status','Work Code','Work Name','Work Type','Original Work Category','Total Sanction (Rs)','Booked Since Inception Wages (Rs)','Booked Since Inception Material (Rs)','Total Mandays','Mandays Generated Current FY']

def clean(v): return re.sub(r'\s+',' ',html.unescape(str(v or ''))).strip()

class ResultRows(HTMLParser):
    def __init__(self,status):
        super().__init__(convert_charrefs=True);self.status=status;self.in_cell=False;self.cell=[];self.row=None;self.rows=[]
    def handle_starttag(self,tag,attrs):
        tag=tag.lower()
        if tag=='tr':self.row=[]
        elif tag in ('td','th') and self.row is not None:self.in_cell=True;self.cell=[]
        elif tag=='br' and self.in_cell:self.cell.append(' ')
    def handle_data(self,data):
        if self.in_cell:self.cell.append(data)
    def handle_endtag(self,tag):
        tag=tag.lower()
        if tag in ('td','th') and self.in_cell:
            self.row.append(clean(''.join(self.cell)));self.in_cell=False
        elif tag=='tr' and self.row is not None:
            c=self.row;self.row=None
            if len(c)>=32 and c[0].isdigit() and c[1].upper()=='SATNA' and c[6] and '/' in c[6]:
                self.rows.append({'District Name':c[1],'Janpad / Block Name':c[2],'Panchayat Name':c[3],'Work Start Fin Year':c[4],'Work Status':c[5] or self.status,'Work Code':c[6],'Work Name':c[7],'Original Work Category':c[9],'Work Type':c[11] or c[10],'Total Sanction (Rs)':c[15],'Booked Since Inception Wages (Rs)':c[20],'Booked Since Inception Material (Rs)':c[21],'Total Mandays':c[24],'Mandays Generated Current FY':c[25]})

def hidden_fields(src):
    d={}
    for tag in re.findall(r'<input[^>]+type=["\']hidden["\'][^>]*>',src,re.I):
        n=re.search(r'name=["\']([^"\']+)',tag,re.I);v=re.search(r'value=["\']([^"\']*)',tag,re.I)
        if n:d[html.unescape(n.group(1))]=html.unescape(v.group(1) if v else '')
    return d

def form_action(src,base):
    m=re.search(r'<form[^>]+action=["\']([^"\']+)',src,re.I)
    if not m:raise RuntimeError('MIS 6.12 form action not found')
    return urllib.parse.urljoin(base,html.unescape(m.group(1)))

def open_text(opener,url,data=None,timeout=120):
    req=urllib.request.Request(url,data=data,headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128 Safari/537.36','Content-Type':'application/x-www-form-urlencoded','Cache-Control':'no-cache'})
    with opener.open(req,timeout=timeout) as r:return r.read().decode('utf-8','ignore'),r.geturl()

def selected_values(src,d):
    for sm in re.finditer(r'<select[^>]+name=["\']([^"\']+)["\'][^>]*>(.*?)</select>',src,re.I|re.S):
        name=html.unescape(sm.group(1));body=sm.group(2)
        o=re.search(r'<option[^>]*selected=["\']selected["\'][^>]*value=["\']([^"\']*)',body,re.I) or re.search(r'<option[^>]*value=["\']([^"\']*)',body,re.I)
        if o:d[name]=html.unescape(o.group(1))

def fetch():
    opener=urllib.request.build_opener(urllib.request.HTTPCookieProcessor())
    home,home_url=open_text(opener,URL)
    d=hidden_fields(home);d.update({'__EVENTTARGET':'ctl00$ContentPlaceHolder1$ddl_dist','ctl00$ContentPlaceHolder1$ddl_state':'17','ctl00$ContentPlaceHolder1$ddl_dist':'1712'})
    district,district_url=open_text(opener,form_action(home,home_url),urllib.parse.urlencode(d).encode())
    if 'value="1712006"' not in district:raise RuntimeError('SATNA block options did not load')
    base=hidden_fields(district);selected_values(district,base)
    base.update({'__EVENTTARGET':'','ctl00$ContentPlaceHolder1$ddl_state':'17','ctl00$ContentPlaceHolder1$ddl_dist':'1712','ctl00$ContentPlaceHolder1$ddl_blk':'ALL','ctl00$ContentPlaceHolder1$ddl_pan':'ALL','ctl00$ContentPlaceHolder1$Ddlworkcategory':'ALL','ctl00$ContentPlaceHolder1$ddlprostatus':'ALL','ctl00$ContentPlaceHolder1$ddlexp':'ALL','ctl00$ContentPlaceHolder1$ddlexpnest':'ALL','ctl00$ContentPlaceHolder1$ddlFin_year':'ALL','ctl00$ContentPlaceHolder1$filter':'ALL','ctl00$ContentPlaceHolder1$Button1':'Submit'})
    action=form_action(district,district_url);all_rows=[];counts={}
    for code,name in STATUSES:
        payload=dict(base);payload['ctl00$ContentPlaceHolder1$Ddlwork_status']=code
        req=urllib.request.Request(action,data=urllib.parse.urlencode(payload).encode(),headers={'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/128 Safari/537.36','Content-Type':'application/x-www-form-urlencoded','Cache-Control':'no-cache'})
        parser=ResultRows(name)
        with opener.open(req,timeout=300) as response:
            while True:
                chunk=response.read(1024*1024)
                if not chunk:break
                parser.feed(chunk.decode('utf-8','ignore'))
        parser.close();counts[name]=len(parser.rows)
        if not parser.rows:raise RuntimeError(f'MIS 6.12 returned zero {name} rows')
        all_rows.extend(parser.rows);print(f'MIS 6.12 {name}: {len(parser.rows)} rows')
    unique={(r['Work Code'],r['Work Status'].upper()):r for r in all_rows}
    return list(unique.values()),counts

def main():
    rows,counts=fetch();OUT_CSV.parent.mkdir(exist_ok=True)
    with tempfile.NamedTemporaryFile('w',encoding='utf-8-sig',newline='',delete=False,dir=OUT_CSV.parent,suffix='.tmp') as f:
        w=csv.DictWriter(f,fieldnames=FIELDS);w.writeheader();w.writerows(rows);temp=Path(f.name)
    temp.replace(OUT_CSV)
    subprocess.run([sys.executable,str(ROOT/'scripts'/'update_ongoing_csv.py')],cwd=ROOT,check=True)
    meta={'source':'Official MIS Report 6.12','officialUrl':URL,'updatedAt':datetime.now(timezone.utc).isoformat(),'rows':len(rows),'statusCounts':counts}
    (ROOT/'data'/'mis-6.12-status.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    print(f'SUCCESS: MIS 6.12 live work list updated: {len(rows)} rows')

if __name__=='__main__':
    try:main()
    except Exception as exc:
        print('ERROR: MIS 6.12 live update failed; existing dashboard data preserved.',exc);sys.exit(1)
