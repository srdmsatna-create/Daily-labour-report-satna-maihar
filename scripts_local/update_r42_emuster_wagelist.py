#!/usr/bin/env python3
"""Fetch the official R4.2 E-Mustroll and Wagelist block summary."""
import html, json, os, re, urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo
from vbgram_access import open_url

ROOT=Path(__file__).resolve().parents[1]
URL=os.environ.get("R42_EMUSTER_WAGELIST_URL","").strip() or "https://vbgramgrep.dord.gov.in/VBGRAMG/state_html/emuster_wagelist_rpt.aspx?payload=-Up9kj5YnDyqzHwpVYm1ynIzwpr6GnkI4iUkxP9NQfOW81eBLTCTNzsypEwJ3qAnMeS3w_G_i1hCvcNENIcQIX0SV1McbWTL5ujzxKIUzRoOJL1C5NxsjCCIk1jIoCJXb_ccpFAElQCvXMAT6jxrt0iwS3PaBiQo6ZW5iAir3FdGySW-NFCbwZmw1GnToWDpPC7dCFOhXxcX3wzeWq83zXS_nGkKxIMgkRUy3lxCJZM"
BLOCKS=("AMARPATAN","MAIHAR","MAJHGAWAN","NAGOD","RAMNAGAR","RAMPUR BAGHELAN","SATNA","UNCHAHARA")
FIELDS=("uIssued","uFilled","uDeleted","uZero","uTotal","sIssued","sFilled","sZero","sTotal","wagelists","covered")
def clean(s): return re.sub(r"\\s+"," ",html.unescape(re.sub(r"<[^>]*>","",s or ""))).strip()
def number(s):
    raw=re.sub(r"[^0-9]","",s or "")
    return int(raw or "0")
def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0","Cache-Control":"no-cache"})
    source=open_url(req,timeout=90).read().decode("utf-8","ignore")
    rows=[]
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>",source,re.I|re.S):
        cells=[clean(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",tr,re.I|re.S)]
        if len(cells)<13 or cells[1].upper() not in BLOCKS: continue
        row={"block":cells[1].upper()}
        row.update({k:number(cells[i+2]) for i,k in enumerate(FIELDS)})
        if row["uTotal"]!=row["uFilled"]+row["uZero"] or row["sTotal"]!=row["sFilled"]+row["sZero"]:
            raise ValueError("Official R4.2 total columns do not reconcile")
        rows.append(row)
    if len(rows)!=8 or {r["block"] for r in rows}!=set(BLOCKS):
        raise ValueError(f"Expected all 8 Satna Janpads; received {len(rows)}")
    totals={k:sum(r[k] for r in rows) for k in FIELDS}
    m=re.search(r"Report Last Updated On\\s*:\\s*([^<]+)",source,re.I)
    data={"title":"R4.2 Report on E-Mustroll and Wagelist generated for FY 2026-2027","financialYear":"2026-2027","district":"SATNA","checkedDate":datetime.now(ZoneInfo("Asia/Kolkata")).strftime("%d-%m-%Y"),"officialDate":clean(m.group(1)) if m else "","fetchedAt":datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),"source":URL,"rows":rows,"totals":totals}
    validate(data)
    return data
def validate(d):
    if d.get("financialYear")!="2026-2027" or len(d.get("rows",[]))!=8 or {r.get("block") for r in d["rows"]}!=set(BLOCKS):
        raise ValueError("Invalid R4.2 coverage")
    for r in d["rows"]:
        if any(type(r.get(k)) is not int or r[k]<0 for k in FIELDS): raise ValueError("Invalid R4.2 count")
        if r["uTotal"]!=r["uFilled"]+r["uZero"] or r["sTotal"]!=r["sFilled"]+r["sZero"]: raise ValueError("R4.2 totals do not reconcile")
    totals={k:sum(r[k] for r in d["rows"]) for k in FIELDS}
    if d.get("totals")!=totals: raise ValueError("R4.2 block totals do not reconcile")
def main():
    d=fetch()
    path=ROOT/"data"/"r42-emuster-wagelist.json";path.parent.mkdir(parents=True,exist_ok=True)
    tmp=path.with_suffix(".tmp");tmp.write_text(json.dumps(d,ensure_ascii=False,indent=2)+"\\n",encoding="utf-8");os.replace(tmp,path)
    print("R4.2 VERIFIED: 8 Janpads; "+str(d["totals"]["wagelists"])+" wagelists; source checked "+d["checkedDate"],flush=True)
if __name__=="__main__":main()
