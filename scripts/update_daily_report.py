#!/usr/bin/env python3
import os, sys, json, re, urllib.request, tempfile
from pathlib import Path
from datetime import datetime, timezone
from openpyxl import load_workbook

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'auto-data.js'
INCOMING=ROOT/'incoming'/'Daily Report.xlsx'
ROOT_XLSX=ROOT/'Daily Report.xlsx'
URL=os.environ.get('DAILY_REPORT_XLSX_URL','').strip()

def n(v):
    try:return float(v or 0)
    except:return 0

def c(v): return '' if v is None else str(v).strip()
def up(v): return c(v).upper()

def obtain():
    if URL:
        fd, name=tempfile.mkstemp(suffix='.xlsx'); os.close(fd)
        req=urllib.request.Request(URL,headers={'User-Agent':'Mozilla/5.0 DailyReportBot/1.0'})
        with urllib.request.urlopen(req,timeout=90) as r, open(name,'wb') as f:f.write(r.read())
        return Path(name), URL
    if INCOMING.exists(): return INCOMING, 'repo:incoming/Daily Report.xlsx'
    if ROOT_XLSX.exists(): return ROOT_XLSX, 'repo:Daily Report.xlsx'
    raise SystemExit('No source workbook. Set DAILY_REPORT_XLSX_URL secret or add incoming/Daily Report.xlsx')

def val(ws,row,col): return ws.cell(row=row,column=col).value

def extract_date(text):
    m=re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{4})', c(text))
    return f'{int(m.group(1)):02d}-{int(m.group(2)):02d}-{m.group(3)}' if m else None

def parse(path):
    wb=load_workbook(path,data_only=True,read_only=True)
    for sh in ('RepDay','Sheet1','VBG'):
        if sh not in wb.sheetnames: raise SystemExit(f'Missing sheet: {sh}')
    rep=wb['RepDay']; title=c(val(rep,1,1)); rep_date=extract_date(title); rows=[]; gpmap={}
    for i in range(4,rep.max_row+1):
        if not c(val(rep,i,1)) or not c(val(rep,i,2)) or not c(val(rep,i,6)): continue
        r={'janpad':up(val(rep,i,1)),'engineer':c(val(rep,i,2)),'cluster':c(val(rep,i,3)),'ongoing':n(val(rep,i,4)),'panchayat':up(val(rep,i,6)),'gps':n(val(rep,i,7)),'gpsProgress':n(val(rep,i,8)),'labour':n(val(rep,i,9)),'worksMR':n(val(rep,i,10)),'noEkyc':n(val(rep,i,11)),'mrs':n(val(rep,i,12))}
        rows.append(r);gpmap[(r['janpad'],r['panchayat'])]=(r['engineer'],r['cluster'])
    s1=wb['Sheet1']; sheet1_title=c(val(s1,1,1)); sheet1_date=extract_date(sheet1_title); official=[]
    for i in (4,5,6,8,9,10,11,12):
        if not c(val(s1,i,2)):continue
        official.append({'janpad':up(val(s1,i,2)),'totalGP':n(val(s1,i,3)),'musterGP':n(val(s1,i,4)),'dysfunctionalGP':n(val(s1,i,5)),'labourAll':n(val(s1,i,6)),'mrAll':n(val(s1,i,7)),'ongoingAll':n(val(s1,i,8)),'labourIndividual':n(val(s1,i,10)),'mrIndividual':n(val(s1,i,11)),'labourCommunity':n(val(s1,i,12)),'mrCommunity':n(val(s1,i,13)),'pmayOngoing':n(val(s1,i,15)),'pmayMR':n(val(s1,i,16)),'ekLabour':n(val(s1,i,18)),'ekOngoing':n(val(s1,i,19)),'ekMR':n(val(s1,i,20))})
    v=wb['VBG']; wm={}
    inst=re.compile(r'(school|prathmik|madhyamik|shala|vidyalaya|प्राथमिक|माध्यमिक|शाला|विद्यालय)',re.I)
    for i in range(5,v.max_row+1):
        jan,gp,fy,status,code,name,wt=up(val(v,i,3)),up(val(v,i,4)),c(val(v,i,5)),c(val(v,i,6)).lower(),c(val(v,i,7)),c(val(v,i,8)),c(val(v,i,9))
        if not jan or not gp or not code or 'ongoing' not in status:continue
        eng,cl=gpmap.get((jan,gp),('Unmapped','Unmapped'));key=(jan,eng,cl,gp)
        z=wm.setdefault(key,{'janpad':jan,'engineer':eng,'cluster':cl,'panchayat':gp,'workTotal':0,'pmayOngoing':0,'ekOngoing':0,'currentFYActive':0})
        z['workTotal']+=1
        if 'pmay' in wt.lower():z['pmayOngoing']+=1
        if wt.lower()=='ek bagiya' and fy in ('2025-2026','2026-2027') and not inst.search(name):z['ekOngoing']+=1
        if n(val(v,i,22))>0:z['currentFYActive']+=1
    return {'title':title,'rows':rows,'official':official,'workmix':list(wm.values()),'_sourceDates':{'RepDay':rep_date,'Sheet1':sheet1_date}}

path,source=obtain();data=parse(path)
dates=data.pop('_sourceDates',{})
data['meta']={'mode':'auto','status':'ok','updatedAt':datetime.now(timezone.utc).isoformat(),'source':source,'rowCount':len(data['rows']),'sourceDates':dates}
OUT.write_text('window.AUTO_REPORT='+json.dumps(data,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')
print(f'Wrote {OUT} with {len(data["rows"])} GP rows')
