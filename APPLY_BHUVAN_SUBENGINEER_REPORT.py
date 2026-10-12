#!/usr/bin/env python3
"""Install/update the Bhuvan Yuktdhara Sub Engineer-wise report in SRDM."""
from __future__ import annotations
import argparse, datetime as dt, html, json, re, shutil, sys, unicodedata
from pathlib import Path
from urllib.request import Request, urlopen

SOURCE = "https://bhuvan-app2.nrsc.gov.in/planner_v3/yuktdhara_dashboard/public_dashboard/"
LISTS = {
    "started": "view_panchayats_started.php?level=district&state=17&district=1712",
    "submitted": "view_panchayats.php?level=district&state=17&district=1712",
    "notStarted": "view_panchayats_notstarted.php?level=district&state=17&district=1712",
    "gasApproved": "view_panchayats_gas_approved.php?level=district&state=17&district=1712",
}
PORTAL = SOURCE + "index.php?state=17&district=1712&go=1"
BEGIN = "<!-- SRDM_BHUVAN_SUBENGINEER_BEGIN -->"
END = "<!-- SRDM_BHUVAN_SUBENGINEER_END -->"

def norm(v):
    v = unicodedata.normalize("NFKD", str(v or "")).upper()
    return re.sub(r"[^A-Z0-9]", "", v)

def canon_block(v):
    n = norm(v)
    aliases = {"SATNA":"SOHAWAL", "RAMPURBAGHELAN":"RAMPUR BAGHELAN", "MAJHGAON":"MAJHGAWAN"}
    return aliases.get(n, str(v or "").strip().upper())

def district(block):
    return "Maihar" if canon_block(block) in {"MAIHAR","AMARPATAN","RAMNAGAR"} else "Satna"

def fetch_rows(path):
    req = Request(SOURCE + path, headers={"User-Agent":"Mozilla/5.0 SRDM-Auto-Update"})
    raw = urlopen(req, timeout=60).read().decode("utf-8", "replace")
    out=[]
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", raw, re.I|re.S):
        cells=[]
        for td in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", tr, re.I|re.S):
            text=html.unescape(re.sub(r"<[^>]+>", " ", td))
            cells.append(re.sub(r"\s+", " ", text).strip())
        if len(cells)>=5 and cells[0].isdigit():
            out.append((canon_block(cells[3]), cells[4].strip()))
    if not out and path != LISTS["gasApproved"]:
        raise RuntimeError("Bhuvan list returned no data: " + path)
    return out

def load_mapping(root):
    p=root/"auto-data.js"
    if not p.exists(): raise RuntimeError("auto-data.js not found in dashboard folder")
    text=p.read_text(encoding="utf-8-sig", errors="replace")
    m=re.search(r"window\.AUTO_REPORT\s*=\s*(\{.*\})\s*;?\s*$", text, re.S)
    if not m: raise RuntimeError("AUTO_REPORT data not found in auto-data.js")
    rows=json.loads(m.group(1)).get("rows",[])
    if not rows: raise RuntimeError("GP/Sub Engineer mapping is empty")
    return rows

def generate(root):
    mapping=load_mapping(root)
    lists={k:fetch_rows(v) for k,v in LISTS.items()}
    sets={k:{(norm(canon_block(b)),norm(g)) for b,g in vals} for k,vals in lists.items()}
    rows=[]
    for r in mapping:
        block=canon_block(r.get("janpad"))
        key=(norm(block),norm(r.get("panchayat")))
        rows.append({
            "district":district(block), "janpad":block, "engineer":str(r.get("engineer") or "Unmapped").strip(),
            "cluster":str(r.get("cluster") or "").strip(), "panchayat":str(r.get("panchayat") or "").strip(),
            "started":key in sets["started"], "submitted":key in sets["submitted"],
            # The official not-started HTML is capped at 500 rows. The portal's
            # own definition is the complement of Plan Started across all GPs.
            "notStarted":key not in sets["started"], "gasApproved":key in sets["gasApproved"],
        })
    raw_counts={k:len(v) for k,v in lists.items()}
    counts=dict(raw_counts)
    counts["notStarted"]=len(rows)-sum(bool(r["started"]) for r in rows)
    matched={k:sum(bool(r[k]) for r in rows) for k in LISTS}
    if counts["started"] and matched["started"] < counts["started"]-2:
        raise RuntimeError(f"GP mapping mismatch: portal started={counts['started']}, matched={matched['started']}")
    payload={"meta":{"source":"Bhuvan Yuktdhara, Satna legacy district (8 blocks)","portal":PORTAL,
              "updatedAt":dt.datetime.now(dt.timezone.utc).isoformat(),"totalGP":len(rows),"portalCounts":counts,
              "rawListCounts":raw_counts,"matchedCounts":matched},"rows":rows}
    (root/"bhuvan-subengineer-data.js").write_text("window.BHUVAN_SE_REPORT="+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    return payload

STYLE = r'''<style id="srdmBhuvanSeStyle">
#bhuvanSeReport{margin:20px 0;padding:18px;border:1px solid #bfd4ee;border-radius:18px;background:linear-gradient(145deg,#f8fbff,#edf5ff);color:#10233f;font:600 15px/1.35 Arial,sans-serif}.bse-head{display:flex;justify-content:space-between;gap:12px;align-items:center;flex-wrap:wrap}.bse-head h2{font-size:25px;margin:0;color:#0b3b75}.bse-meta{font-size:13px;color:#536b89}.bse-filters{display:flex;gap:9px;flex-wrap:wrap;margin:14px 0}.bse-filters select,.bse-filters button,.bse-filters a{font:700 14px Arial;padding:9px 12px;border:1px solid #8eb1da;border-radius:9px;background:#fff;color:#123e70;text-decoration:none}.bse-filters button{cursor:pointer;background:#0c4d8d;color:#fff}.bse-kpis{display:grid;grid-template-columns:repeat(5,minmax(120px,1fr));gap:9px;margin:10px 0 14px}.bse-kpi{padding:10px;border-radius:12px;background:#fff;border-left:5px solid #1677d2;box-shadow:0 2px 8px #0b3b7512}.bse-kpi b{display:block;font-size:22px;color:#0b3b75}.bse-tablewrap{overflow:auto;max-height:620px;border-radius:10px;border:1px solid #bfd4ee;background:#fff}.bse-table{width:100%;border-collapse:collapse;white-space:nowrap;font-size:14px}.bse-table th{position:sticky;top:0;background:#0b427c;color:#fff;padding:10px 8px;z-index:1}.bse-table td{padding:8px;border-bottom:1px solid #d8e4f2;text-align:center}.bse-table td:nth-child(-n+4){text-align:left}.bse-table tbody tr:nth-child(even){background:#f3f8fe}.bse-bad{color:#b42318;font-weight:800}.bse-good{color:#087a43;font-weight:800}.srdm-bhuvan-se-card{border-color:#12805c!important;background:linear-gradient(135deg,#edfff7,#fff)!important}.srdm-bhuvan-se-card .srdm-app-icon{background:#11875f!important;color:#fff!important}@media(max-width:900px){.bse-kpis{grid-template-columns:repeat(2,1fr)}#bhuvanSeReport{font-size:14px}}@media print{.bse-filters,.no-print{display:none!important}.bse-tablewrap{max-height:none;overflow:visible}}
</style>'''

CARD = r'''<button type="button" class="srdm-app-card srdm-bhuvan-se-card" onclick="document.getElementById('bhuvanSeReport').scrollIntoView({behavior:'smooth'})"><span class="srdm-app-icon">🛰</span><span class="srdm-app-copy"><strong>Bhuvan Yuktdhara Monitoring</strong><span>Sub Engineer-wise auto-update report</span></span><span class="srdm-app-new">New</span></button>'''

SECTION = r'''<section id="bhuvanSeReport">
 <div class="bse-head"><div><h2>Bhuvan Yuktdhara — Sub Engineer-wise Report</h2><div class="bse-meta" id="bseMeta">Official data loading…</div></div><a class="no-print" href="https://bhuvan-app2.nrsc.gov.in/planner_v3/yuktdhara_dashboard/public_dashboard/index.php?state=17&amp;district=1712&amp;go=1" target="_blank">Official Bhuvan Portal ↗</a></div>
 <div class="bse-filters no-print"><select id="bseDistrict"><option value="">All Districts</option><option>Satna</option><option>Maihar</option></select><select id="bseJanpad"><option value="">All Janpads</option></select><select id="bseEngineer"><option value="">All Sub Engineers</option></select><button id="bseRefresh">Refresh</button><button onclick="window.print()">Print / PDF</button><button id="bseCsv">Excel / CSV</button></div>
 <div class="bse-kpis" id="bseKpis"></div><div class="bse-tablewrap"><table class="bse-table"><thead><tr><th>District</th><th>Janpad</th><th>Sub Engineer</th><th>Cluster</th><th>Total GP</th><th>Plan Started</th><th>Plan Submitted</th><th>Not Started</th><th>GAS Approved</th><th>GP Details</th></tr></thead><tbody id="bseBody"><tr><td colspan="10">Official data loading…</td></tr></tbody></table></div>
</section>
<script src="bhuvan-subengineer-data.js?live=1"></script>
<script id="srdmBhuvanSeScript">(()=>{const q=x=>document.getElementById(x),D=q('bseDistrict'),J=q('bseJanpad'),E=q('bseEngineer'),esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));let last=[];const uniq=(a,k)=>[...new Set(a.map(x=>x[k]).filter(Boolean))].sort((a,b)=>a.localeCompare(b));function opts(el,vals,label,keep){el.innerHTML='<option value="">All '+label+'</option>'+vals.map(v=>'<option>'+esc(v)+'</option>').join('');if(vals.includes(keep))el.value=keep}function filtered(){return (window.BHUVAN_SE_REPORT?.rows||[]).filter(r=>(!D.value||r.district===D.value)&&(!J.value||r.janpad===J.value)&&(!E.value||r.engineer===E.value))}function render(){let all=window.BHUVAN_SE_REPORT?.rows||[],j=J.value,e=E.value;opts(J,uniq(all.filter(r=>!D.value||r.district===D.value),'janpad'),'Janpads',j);opts(E,uniq(all.filter(r=>(!D.value||r.district===D.value)&&(!J.value||r.janpad===J.value)),'engineer'),'Sub Engineers',e);let a=filtered(),g={};a.forEach(r=>{let k=[r.district,r.janpad,r.engineer,r.cluster].join('|'),x=g[k]||(g[k]={...r,total:0,started:0,submitted:0,notStarted:0,gasApproved:0,gps:[]});x.total++;['started','submitted','notStarted','gasApproved'].forEach(z=>x[z]+=r[z]?1:0);x.gps.push(r.panchayat)});last=Object.values(g);let sums=z=>a.reduce((n,r)=>n+(z==='total'||r[z]?1:0),0);q('bseKpis').innerHTML=[['Total GP',sums('total')],['Plan Started',sums('started')],['Plan Submitted',sums('submitted')],['Not Started',sums('notStarted')],['GAS Approved',sums('gasApproved')]].map((x,i)=>'<div class="bse-kpi"><span>'+x[0]+'</span><b class="'+(i===3?'bse-bad':'')+'">'+x[1]+'</b></div>').join('');q('bseBody').innerHTML=last.length?last.map(x=>'<tr><td>'+esc(x.district)+'</td><td>'+esc(x.janpad)+'</td><td>'+esc(x.engineer)+'</td><td>'+esc(x.cluster)+'</td><td>'+x.total+'</td><td class="bse-good">'+x.started+'</td><td>'+x.submitted+'</td><td class="bse-bad">'+x.notStarted+'</td><td>'+x.gasApproved+'</td><td title="'+esc(x.gps.join(', '))+'">'+esc(x.gps.slice(0,3).join(', '))+(x.gps.length>3?' …':'')+'</td></tr>').join(''):'<tr><td colspan="10">No matching data</td></tr>';let m=window.BHUVAN_SE_REPORT?.meta;q('bseMeta').textContent=m?'SATNA legacy 8 Janpads split into Satna (5) + Maihar (3) • Updated '+new Date(m.updatedAt).toLocaleString('en-IN'):'Data unavailable';D.onchange=render;J.onchange=render;E.onchange=render;q('bseRefresh').onclick=render;q('bseCsv').onclick=()=>{let h=['District','Janpad','Sub Engineer','Cluster','Total GP','Plan Started','Plan Submitted','Not Started','GAS Approved','GP Names'],rows=last.map(x=>[x.district,x.janpad,x.engineer,x.cluster,x.total,x.started,x.submitted,x.notStarted,x.gasApproved,x.gps.join('; ')]),csv='\ufeff'+[h,...rows].map(r=>r.map(v=>'"'+String(v).replace(/"/g,'""')+'"').join(',')).join('\r\n'),a=document.createElement('a');a.href=URL.createObjectURL(new Blob([csv],{type:'text/csv'}));a.download='Bhuvan_Yuktdhara_SubEngineer_Report.csv';a.click();URL.revokeObjectURL(a.href)};render()}if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',render);else render()})();</script>'''

def install_html(root):
    p=root/"index.html"
    if not p.exists(): raise RuntimeError("index.html not found in dashboard folder")
    s=p.read_text(encoding="utf-8",errors="replace")
    s=re.sub(re.escape(BEGIN)+r".*?"+re.escape(END),"",s,flags=re.S)
    s=re.sub(r'<style id="srdmBhuvanSeStyle(?:Head)?">.*?</style>\s*', '', s, flags=re.S)
    s=s.replace("</head>",STYLE.replace('<style id="srdmBhuvanSeStyle">','<style id="srdmBhuvanSeStyleHead">')+"\n</head>",1)
    # Section and script go at body end; card is inserted into existing launcher grid by runtime relocation.
    loader=f'''<script id="srdmBhuvanSeCardLoader">(()=>{{let g=document.querySelector('#srdmApplications .srdm-app-grid');if(g&&!g.querySelector('.srdm-bhuvan-se-card'))g.insertAdjacentHTML('beforeend',{json.dumps(CARD)});}})();</script>'''
    s=s.replace("</body>",BEGIN+"\n"+SECTION+"\n"+loader+"\n"+END+"\n</body>",1)
    p.write_text(s,encoding="utf-8")

def hook_auto(root):
    p=root/"ONE_CLICK_DASHBOARD_DATA_UPDATE.bat"
    if not p.exists(): return False
    s=p.read_text(encoding="utf-8",errors="replace")
    marker="REM SRDM_BHUVAN_SUBENGINEER_AUTO"
    if marker not in s:
        line='\n'+marker+'\nif exist "scripts_local\\update_bhuvan_subengineer.py" %PYTHON_CMD% "scripts_local\\update_bhuvan_subengineer.py" --repo "%CD%" --update-only\n'
        pos=s.lower().find("git add")
        s=s[:pos]+line+s[pos:] if pos>=0 else s+line
        p.write_text(s,encoding="utf-8")
    return True

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--repo",default=".");ap.add_argument("--update-only",action="store_true");a=ap.parse_args()
    root=Path(a.repo).resolve(); print("Dashboard folder:",root)
    payload=generate(root)
    if not a.update_only:
        install_html(root)
        dest=root/"scripts_local"/"update_bhuvan_subengineer.py";dest.parent.mkdir(exist_ok=True)
        if Path(__file__).resolve()!=dest.resolve(): shutil.copy2(__file__,dest)
        hook_auto(root)
    print("SUCCESS:",len(payload["rows"]),"GP rows;",payload["meta"]["matchedCounts"])
if __name__=="__main__":
    try: main()
    except Exception as e: print("ERROR:",e,file=sys.stderr);sys.exit(1)
