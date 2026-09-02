#!/usr/bin/env python3
import html, json, re, shutil, sys, urllib.parse, urllib.request
from datetime import datetime, timezone
from pathlib import Path

def get_root():
    if "--repo" in sys.argv:
        i=sys.argv.index("--repo")
        if i+1>=len(sys.argv): raise RuntimeError("--repo requires a folder path")
        return Path(sys.argv[i+1]).resolve()
    return Path.cwd()

ROOT=get_root()
URL="https://vbgramgrep.dord.gov.in/VBGRAMG/MusterRolle_EMBStatus.aspx?payload=ZXiXTJ0HzQl7fz4W7woa23KDguzp-Is4I63qmc6Kyc1jl3ibJtUhejzlAtv-fAxwYpqJyyVqtiJi6sPlWJ357Cb4q5KyW0qMVPUtVVbI2jF4KrNWijPnHjLZhYy2hn-IsDls6eL7mtZ3bO4TEFNgNLvBwskkuj-k-JBiAHVCc1URsDldWZBA_b0p11E4y43kiQmP7PzLsOsegcEuX8tvBUfVun1-KPT6ttJfedEcB7dCuEcZY6uUT99T_4E5JucKgEhkZbRWFH7ERjpKjdJv4w"
BLOCKS={"AMARPATAN","MAIHAR","MAJHGAWAN","NAGOD","RAMNAGAR","RAMPUR BAGHELAN","SATNA","UNCHAHARA"}

def clean(v): return re.sub(r"\s+"," ",html.unescape(re.sub(r"<[^>]+>","",v or ""))).strip()
def num(v):
    try: return int(float(re.sub(r"[^0-9.-]","",v.replace(",","")) or 0))
    except Exception: return 0

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0","Cache-Control":"no-cache"})
    src=urllib.request.urlopen(req,timeout=90).read().decode("utf-8","ignore")
    rows=[]
    keys=["issued","filled","embFilled","noEmb","pendingEmb","verifiedAE","pendingVerification"]
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>",src,re.I|re.S):
        cells=[clean(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",tr,re.I|re.S)]
        if len(cells)>=9 and cells[1].upper() in BLOCKS:
            row={"block":cells[1].upper()}
            row.update({k:num(cells[i+2]) for i,k in enumerate(keys)})
            rows.append(row)
    if len(rows)!=8: raise RuntimeError(f"Expected 8 Satna blocks, got {len(rows)}")
    m=re.search(r'id="ContentPlaceHolder1_Shedule_updated_date"[^>]*>([^<]+)',src,re.I)
    # Read the existing authoritative GP -> Engineer mapping.
    gpmap={}
    auto=ROOT/"auto-data.js"
    if auto.exists():
        raw=auto.read_text(encoding="utf-8",errors="ignore")
        mm=re.search(r"window\.AUTO_REPORT\s*=\s*(\{.*?\});\s*(?:\n|$)",raw,re.S)
        if mm:
            try:
                ar=json.loads(mm.group(1))
                for r in ar.get("rows",[]):
                    j=clean(str(r.get("janpad",""))).upper(); g=clean(str(r.get("panchayat",""))).upper()
                    if j and g: gpmap[(j,g)]={"engineer":clean(str(r.get("engineer",""))) or "Unmapped","cluster":clean(str(r.get("cluster","")))}
            except Exception: pass
    # Follow every official block link and collect GP-level monitoring rows.
    gp_rows=[]
    for block in sorted(BLOCKS):
        lm=re.search(r'href="(MusterRolle_EMBStatus\.aspx\?payload=[^"]+)"[^>]*>\s*'+re.escape(block)+r'\s*</a>',src,re.I)
        if not lm: continue
        burl=urllib.parse.urljoin(URL,html.unescape(lm.group(1)))
        breq=urllib.request.Request(burl,headers={"User-Agent":"Mozilla/5.0","Cache-Control":"no-cache"})
        bsrc=urllib.request.urlopen(breq,timeout=90).read().decode("utf-8","ignore")
        for tr in re.findall(r"<tr[^>]*>(.*?)</tr>",bsrc,re.I|re.S):
            cells=[clean(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",tr,re.I|re.S)]
            # Exclude the portal's column-number guide row: 1,2,3,...,9.
            if len(cells)>=9 and cells[0].isdigit() and not cells[1].isdigit() and cells[1].upper()!="TOTAL":
                gp=cells[1].upper(); mp=gpmap.get((block,gp),{"engineer":"Unmapped","cluster":""})
                z={"block":block,"panchayat":gp,"engineer":mp["engineer"],"cluster":mp["cluster"]}
                z.update({k:num(cells[i+2]) for i,k in enumerate(keys)});gp_rows.append(z)
    if len(gp_rows)<500: raise RuntimeError(f"Expected Satna GP detail, got only {len(gp_rows)} rows")
    data={"title":"R4.4 Muster Roll & e-MB Monitoring Report","financialYear":"2026-2027","district":"SATNA","officialDate":clean(m.group(1)) if m else "","updatedAt":datetime.now(timezone.utc).isoformat(),"source":URL,"rows":rows,"gpRows":gp_rows,"mappingCount":len(gpmap)}
    (ROOT/"muster-emb-data.js").write_text("window.MUSTER_EMB_REPORT="+json.dumps(data,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    print(f"Muster Roll & e-MB updated: 8 blocks, {len(gp_rows)} GP rows, Engineer mapping joined")

STYLE='''<!-- SRDM_MUSTER_EMB_STYLE_START --><style>
#musterEmbLauncher{--app-accent:#e65100!important;--app-soft:#fff3e8!important;--app-shadow:#e6510055!important;border-color:#e65100!important;background:linear-gradient(135deg,#fff0e3,#fff 75%)!important}
#musterEmbLauncher .srdm-app-icon{background:#e65100!important;color:#fff!important}.muster-emb-section{margin:18px 0;background:#fff;border:2px solid #e65100;border-radius:20px;padding:18px;box-shadow:0 10px 28px #e6510022}.muster-emb-head{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:13px}.muster-emb-head h2{margin:0;color:#b33d00}.muster-emb-pill{background:#fff0e3;color:#a43700;border-radius:999px;padding:7px 12px;font-weight:900;font-size:12px}.muster-emb-wrap{overflow:auto}.muster-emb-table{width:100%;border-collapse:collapse;min-width:1380px;table-layout:fixed}.muster-emb-table th{background:#b33d00;color:#fff;padding:10px 5px;border:1px solid #d26932;font-size:11px;white-space:normal}.muster-emb-table td{padding:8px 6px;border:1px solid #f0d2c2;text-align:right;font-weight:700;overflow-wrap:anywhere}.muster-emb-table td:nth-child(2),.muster-emb-table td:nth-child(3),.muster-emb-table td:nth-child(11){text-align:left}.muster-emb-table th:nth-child(1){width:42px}.muster-emb-table th:nth-child(2){width:120px}.muster-emb-table th:nth-child(3){width:185px}.muster-emb-table th:nth-child(4),.muster-emb-table th:nth-child(5),.muster-emb-table th:nth-child(7){width:90px}.muster-emb-table th:nth-child(6){width:115px}.muster-emb-table th:nth-child(8),.muster-emb-table th:nth-child(9){width:125px}.muster-emb-table th:nth-child(10){width:145px}.muster-emb-table th:nth-child(11){width:175px}.muster-emb-table tbody tr:nth-child(even){background:#fff8f3}.muster-emb-table .total-row{background:#ffe6d5!important;color:#8b2e00;font-weight:950}.muster-emb-source{text-align:right;margin-top:10px;font-size:12px;color:#667085}
</style><!-- SRDM_MUSTER_EMB_STYLE_END -->'''

CARD='''<!-- SRDM_MUSTER_EMB_CARD_START --><button type="button" class="srdm-app-card" id="musterEmbLauncher"><span class="srdm-app-icon">M</span><span class="srdm-app-copy"><strong>Muster Roll &amp; e-MB Monitoring</strong><span>FY 2026-27 • Satna block-wise status</span></span><span class="srdm-app-new">New</span></button><script>(function(){var y=document.getElementById('musterEmbLauncher');if(!y)return;var a=document.getElementById('yuktdharaLauncher');if(a){a.insertAdjacentElement('afterend',y);return}var c=document.querySelectorAll('button,a,.srdm-app-card');for(var i=0;i<c.length;i++){var x=(c[i].innerText||'').replace(/\\s+/g,' ').toLowerCase();if(x.indexOf('vb-gram g statistics')>=0||x.indexOf('vb-g ram g statistics')>=0){c[i].insertAdjacentElement('afterend',y);break}}})();</script><!-- SRDM_MUSTER_EMB_CARD_END -->'''

SECTION='''<!-- SRDM_MUSTER_EMB_SECTION_START --><section class="muster-emb-section no-print" id="musterEmbMonitoring"><div class="muster-emb-head"><div><h2>Muster Roll &amp; e-MB Monitoring Report</h2><small>R4.4 • SATNA • Gram Panchayat-wise + Sub Engineer mapping</small></div><span class="muster-emb-pill">FY 2026-2027</span></div><div style="display:flex;gap:10px;flex-wrap:wrap;margin:0 0 12px"><select id="musterBlockFilter" style="padding:10px;border:1px solid #e65100;border-radius:9px"><option value="ALL">— सभी जनपद —</option></select><select id="musterEngineerFilter" style="padding:10px;border:1px solid #e65100;border-radius:9px"><option value="ALL">— सभी उपयंत्री —</option></select><button type="button" onclick="window.print()" style="padding:10px 16px;border:0;border-radius:9px;background:#123f73;color:#fff;font-weight:800">प्रिंट / PDF बनाएँ</button><button type="button" id="musterCsv" style="padding:10px 16px;border:1px solid #123f73;border-radius:9px;background:#fff;color:#123f73;font-weight:800">Excel डाउनलोड</button></div><div class="muster-emb-wrap"><table class="muster-emb-table"><thead><tr><th>क्र.</th><th>जनपद</th><th>ग्राम पंचायत</th><th>कुल MR जारी</th><th>कुल MR भरे</th><th>e-MB भरा (TA/JE)</th><th>e-MB रहित</th><th>e-MB लंबित (T+5)</th><th>e-MB सत्यापित (AE)</th><th>सत्यापन लंबित (T+5)</th><th>उपयंत्री</th></tr></thead><tbody id="musterEmbBody"><tr><td colspan="11">Official data loading…</td></tr></tbody></table></div><div class="muster-emb-source"><span id="musterEmbDate">FY 2026-27</span> • <a href="'''+URL+'''" target="_blank" rel="noopener noreferrer">Portal पर खोलें</a></div></section><script src="muster-emb-data.js"></script><script>(function(){const d=window.MUSTER_EMB_REPORT,b=document.getElementById('musterEmbBody'),bf=document.getElementById('musterBlockFilter'),ef=document.getElementById('musterEngineerFilter'),k=['issued','filled','embFilled','noEmb','pendingEmb','verifiedAE','pendingVerification'],n=new Intl.NumberFormat('en-IN');if(!d||!Array.isArray(d.gpRows)){b.innerHTML='<tr><td colspan="11">Official GP data unavailable</td></tr>';return}const uniq=a=>[...new Set(a.filter(Boolean))].sort((x,y)=>x.localeCompare(y,'hi'));uniq(d.gpRows.map(r=>r.block)).forEach(x=>bf.add(new Option(x,x)));function engineers(){const old=ef.value;ef.innerHTML='<option value="ALL">— सभी उपयंत्री —</option>';uniq(d.gpRows.filter(r=>bf.value==='ALL'||r.block===bf.value).map(r=>r.engineer)).forEach(x=>ef.add(new Option(x,x)));if([...ef.options].some(o=>o.value===old))ef.value=old}function render(){const rows=d.gpRows.filter(r=>(bf.value==='ALL'||r.block===bf.value)&&(ef.value==='ALL'||r.engineer===ef.value)),t=Object.fromEntries(k.map(x=>[x,0]));b.innerHTML=rows.map((r,i)=>{k.forEach(x=>t[x]+=Number(r[x]||0));return `<tr><td>${i+1}</td><td><b>${r.block}</b></td><td>${r.panchayat}</td>${k.map(x=>`<td>${n.format(r[x]||0)}</td>`).join('')}<td><b>${r.engineer||'Unmapped'}</b></td></tr>`}).join('')+`<tr class="total-row"><td></td><td>TOTAL</td><td>${n.format(rows.length)} GP</td>${k.map(x=>`<td>${n.format(t[x])}</td>`).join('')}<td></td></tr>`}bf.onchange=()=>{engineers();render()};ef.onchange=render;engineers();render();document.getElementById('musterCsv').onclick=()=>{const rows=d.gpRows.filter(r=>(bf.value==='ALL'||r.block===bf.value)&&(ef.value==='ALL'||r.engineer===ef.value)),head=['Janpad','Gram Panchayat','MR Issued','MR Filled','e-MB Filled','No e-MB','Pending e-MB','AE Verified','Pending Verification','Upyantri'],csv=[head,...rows.map(r=>[r.block,r.panchayat,...k.map(x=>r[x]),r.engineer])].map(a=>a.map(v=>'"'+String(v??'').replace(/"/g,'""')+'"').join(',')).join('\r\n'),a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\ufeff'+csv],{type:'text/csv'}));a.download='Muster_eMB_Engineer_GP_Report.csv';a.click()};document.getElementById('musterEmbDate').textContent=`FY ${d.financialYear} • Last updated ${d.officialDate||'portal'} • ${d.gpRows.length} GP`;document.getElementById('musterEmbLauncher')?.addEventListener('click',()=>document.getElementById('musterEmbMonitoring')?.scrollIntoView({behavior:'smooth'}));})();</script><!-- SRDM_MUSTER_EMB_SECTION_END -->'''

def install():
    index=ROOT/"index.html"
    if not index.exists(): raise RuntimeError("index.html not found")
    s=index.read_text(encoding="utf-8")
    for name in ("STYLE","CARD","SECTION"):
        s=re.sub(rf"(?s)<!-- SRDM_MUSTER_EMB_{name}_START -->.*?<!-- SRDM_MUSTER_EMB_{name}_END -->","",s)
    p=s.lower().rfind("</head>"); s=s[:p]+STYLE+s[p:]
    # Keep the CSV row separator escaped inside the generated JavaScript.
    safe_section=SECTION.replace("join('\r\n')","join('\\\\r\\\\n')")
    p=s.lower().rfind("</body>"); s=s[:p]+CARD+safe_section+s[p:]
    index.write_text(s,encoding="utf-8")
    target=ROOT/"scripts_local"/"update_muster_emb_monitoring.py";target.parent.mkdir(exist_ok=True);shutil.copy2(Path(__file__),target)
    bat=ROOT/"ONE_CLICK_DASHBOARD_DATA_UPDATE.bat"
    if bat.exists():
        b=bat.read_text(encoding="utf-8",errors="ignore")
        if "MUSTER_EMB_AUTO_UPDATE_V1" not in b:
            block='REM MUSTER_EMB_AUTO_UPDATE_V1\r\n%PYTHON_CMD% "scripts_local\\update_muster_emb_monitoring.py" --update-only\r\nif errorlevel 1 (echo ERROR: Muster e-MB update failed.& pause& exit /b 1)\r\n\r\n'
            anchors=['REM 3. Rebuild dashboard data if merge/build scripts exist','git add']
            for a in anchors:
                if a in b: b=b.replace(a,block+a,1);break
            else: b=block+b
            bat.write_text(b,encoding="utf-8")
    print("Muster Roll & e-MB dashboard module installed")

if __name__=="__main__":
    fetch()
    if "--update-only" not in sys.argv: install()
