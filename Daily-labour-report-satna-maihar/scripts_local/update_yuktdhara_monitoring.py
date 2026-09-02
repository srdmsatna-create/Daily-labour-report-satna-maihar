#!/usr/bin/env python3
import html, json, re, shutil, sys, urllib.request
from datetime import datetime, timezone
from pathlib import Path

def get_root():
    if "--repo" in sys.argv:
        pos = sys.argv.index("--repo")
        if pos + 1 >= len(sys.argv):
            raise RuntimeError("--repo requires a folder path")
        return Path(sys.argv[pos + 1]).resolve()
    return Path.cwd()

ROOT = get_root()
URL = "https://vbgramgrep.dord.gov.in/vbgramg/Yuktdhara_rpt.aspx?payload=rCItcjm0CAVylohlZQkZjREFUa1xC6visCYEM0yVs67VaqioyxBCF688LA6322WU3bsunwYrI7BVFuRIR3HXqJNQs-qn1odYSxziqGDRC7BS3v_-Is3IxQ63YS7DPMBWl9i8fMAEd-pmNJZ20jlsU96bVjBZPAyyn0edeHjldrqYnKWc8JexV1kz0st7PjblPoRnRaxatyr0lgarVnCeZlXp733ThiyKU47IOkx9woZKpr5sQhAu1tZdsmlVw-RE"
BLOCKS = {"AMARPATAN","MAIHAR","MAJHGAWAN","NAGOD","RAMNAGAR","RAMPUR BAGHELAN","SATNA","UNCHAHARA"}

def clean(v): return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", "", v or ""))).strip()
def num(v):
    try: return int(float(re.sub(r"[^0-9.-]", "", v.replace(",", "")) or 0))
    except Exception: return 0

def fetch():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0","Cache-Control":"no-cache"})
    source=urllib.request.urlopen(req,timeout=90).read().decode("utf-8","ignore")
    rows=[]
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>",source,re.I|re.S):
        cells=[clean(x) for x in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>",tr,re.I|re.S)]
        if len(cells)>=9 and cells[1].upper() in BLOCKS:
            rows.append({"block":cells[1].upper(),"gp":num(cells[2]),"gpReceived":num(cells[3]),"worksReceived":num(cells[4]),"worksCreated":num(cells[5]),"yetToStart":num(cells[6]),"ongoing":num(cells[7]),"completed":num(cells[8])})
    if len(rows)!=8: raise RuntimeError(f"Expected 8 Yuktdhara blocks, got {len(rows)}")
    m=re.search(r'id="ContentPlaceHolder1_Shedule_updated_date"[^>]*>([^<]+)',source,re.I)
    payload={"title":"R33.1 Yuktdhara Monitoring Report","financialYear":"2026-2027","district":"SATNA","officialDate":clean(m.group(1)) if m else "","updatedAt":datetime.now(timezone.utc).isoformat(),"source":URL,"rows":rows}
    (ROOT/"yuktdhara-data.js").write_text("window.YUKTDHARA_REPORT="+json.dumps(payload,ensure_ascii=False,separators=(",",":"))+";\n",encoding="utf-8")
    print("Yuktdhara official data updated: 8 blocks")

STYLE='''<!-- SRDM_YUKTDHARA_STYLE_START --><style>
#yuktdharaLauncher{--app-accent:#6f42c1!important;--app-soft:#f3edff!important;--app-shadow:#6f42c155!important;border-color:#6f42c1!important;background:linear-gradient(135deg,#f2ebff,#fff 75%)!important}
#yuktdharaLauncher .srdm-app-icon{background:#6f42c1!important;color:#fff!important}
.yuktdhara-section{margin:18px 0;background:#fff;border:2px solid #6f42c1;border-radius:20px;padding:18px;box-shadow:0 10px 28px #6f42c122}
.yuktdhara-head{display:flex;justify-content:space-between;gap:12px;align-items:center;margin-bottom:13px}.yuktdhara-head h2{margin:0;color:#54299b}.yuktdhara-pill{background:#efe6ff;color:#54299b;border-radius:999px;padding:7px 12px;font-weight:900;font-size:12px}
.yuktdhara-table-wrap{overflow:auto}.yuktdhara-table{width:100%;border-collapse:collapse;min-width:1050px}.yuktdhara-table th{background:#54299b;color:#fff;padding:10px 8px;border:1px solid #7652b7;font-size:12px}.yuktdhara-table td{padding:9px 8px;border:1px solid #ded3ee;text-align:right;font-weight:700}.yuktdhara-table td:nth-child(2){text-align:left}.yuktdhara-table tbody tr:nth-child(even){background:#faf7ff}.yuktdhara-table .total-row{background:#efe6ff!important;color:#3f1b79;font-weight:950}.yuktdhara-source{text-align:right;margin-top:10px;font-size:12px;color:#667085}
</style><!-- SRDM_YUKTDHARA_STYLE_END -->'''

CARD='''<!-- SRDM_YUKTDHARA_CARD_START --><button type="button" class="srdm-app-card" id="yuktdharaLauncher"><span class="srdm-app-icon">⌖</span><span class="srdm-app-copy"><strong>Yuktdhara Monitoring Report</strong><span>FY 2026-27 • Satna block-wise monitoring</span></span><span class="srdm-app-new">New</span></button><script>(function(){var y=document.getElementById('yuktdharaLauncher');if(!y)return;var cards=document.querySelectorAll('button,a,.srdm-app-card');for(var i=0;i<cards.length;i++){var x=(cards[i].innerText||'').replace(/\\s+/g,' ').trim().toLowerCase();if(x.indexOf('vb-gram g statistics')>=0||x.indexOf('vb-g ram g statistics')>=0){if(cards[i].parentNode)cards[i].insertAdjacentElement('afterend',y);break}}})();</script><!-- SRDM_YUKTDHARA_CARD_END -->'''

SECTION='''<!-- SRDM_YUKTDHARA_SECTION_START --><section class="yuktdhara-section no-print" id="yuktdharaMonitoring"><div class="yuktdhara-head"><div><h2>Yuktdhara Monitoring Report</h2><small>R33.1 • SATNA District • Official block-wise status</small></div><span class="yuktdhara-pill">FY 2026-2027</span></div><div class="yuktdhara-table-wrap"><table class="yuktdhara-table"><thead><tr><th>SN</th><th>Block</th><th>Gram Panchayat</th><th>GPs Received Works</th><th>Works Received</th><th>Works Created in VB-G RAM G</th><th>Yet to Start</th><th>Ongoing</th><th>Completed</th></tr></thead><tbody id="yuktdharaBody"><tr><td colspan="9">Official Yuktdhara data loading…</td></tr></tbody></table></div><div class="yuktdhara-source"><span id="yuktdharaDate">FY 2026-27</span> • <a href="https://vbgramgrep.dord.gov.in/vbgramg/Yuktdhara_rpt.aspx?payload=rCItcjm0CAVylohlZQkZjREFUa1xC6visCYEM0yVs67VaqioyxBCF688LA6322WU3bsunwYrI7BVFuRIR3HXqJNQs-qn1odYSxziqGDRC7BS3v_-Is3IxQ63YS7DPMBWl9i8fMAEd-pmNJZ20jlsU96bVjBZPAyyn0edeHjldrqYnKWc8JexV1kz0st7PjblPoRnRaxatyr0lgarVnCeZlXp733ThiyKU47IOkx9woZKpr5sQhAu1tZdsmlVw-RE" target="_blank" rel="noopener noreferrer">Official Source</a></div></section><script src="yuktdhara-data.js"></script><script>(function(){const d=window.YUKTDHARA_REPORT,b=document.getElementById('yuktdharaBody');if(!b||!d||!Array.isArray(d.rows)){if(b)b.innerHTML='<tr><td colspan="9">Official data unavailable</td></tr>';return}const n=new Intl.NumberFormat('en-IN'),k=['gp','gpReceived','worksReceived','worksCreated','yetToStart','ongoing','completed'],t=Object.fromEntries(k.map(x=>[x,0]));b.innerHTML=d.rows.map((r,i)=>{k.forEach(x=>t[x]+=Number(r[x]||0));return `<tr><td>${i+1}</td><td><b>${r.block}</b></td>${k.map(x=>`<td>${n.format(r[x]||0)}</td>`).join('')}</tr>`}).join('')+`<tr class="total-row"><td></td><td>TOTAL</td>${k.map(x=>`<td>${n.format(t[x])}</td>`).join('')}</tr>`;const dt=document.getElementById('yuktdharaDate');if(dt)dt.textContent=`FY ${d.financialYear} • Last updated ${d.officialDate||'official portal'}`;document.getElementById('yuktdharaLauncher')?.addEventListener('click',()=>document.getElementById('yuktdharaMonitoring')?.scrollIntoView({behavior:'smooth',block:'start'}));})();</script><!-- SRDM_YUKTDHARA_SECTION_END -->'''

def install():
    index=ROOT/"index.html"
    if not index.exists(): raise RuntimeError("Run from dashboard project folder; index.html not found")
    s=index.read_text(encoding="utf-8")
    s=re.sub(r"(?s)<!-- SRDM_YUKTDHARA_STYLE_START -->.*?<!-- SRDM_YUKTDHARA_STYLE_END -->","",s)
    s=re.sub(r"(?s)<!-- SRDM_YUKTDHARA_CARD_START -->.*?<!-- SRDM_YUKTDHARA_CARD_END -->","",s)
    s=re.sub(r"(?s)<!-- SRDM_YUKTDHARA_SECTION_START -->.*?<!-- SRDM_YUKTDHARA_SECTION_END -->","",s)
    s=s.replace("</head>",STYLE+"</head>")
    card_anchor=re.search(r'(?s)(<button[^>]+id="vbgStatisticsLauncher".*?</button>)',s)
    if card_anchor:
        s=s[:card_anchor.end()]+CARD+s[card_anchor.end():]
    else:
        # Newer dashboards use generated cards without the old fixed ID.
        # Add safely before body end; CARD's small script moves it beside the
        # visible VB-G RAM G Statistics card when the page loads.
        if "</body>" not in s.lower(): raise RuntimeError("Dashboard body closing tag not found")
        pos=s.lower().rfind("</body>")
        s=s[:pos]+CARD+s[pos:]
    section_anchor=s.find('<section class="vbg-stat-section')
    if section_anchor>=0:
        s=s[:section_anchor]+SECTION+s[section_anchor:]
    else:
        pos=s.lower().rfind("</body>")
        s=s[:pos]+SECTION+s[pos:]
    index.write_text(s,encoding="utf-8")
    target=ROOT/"scripts_local"/"update_yuktdhara_monitoring.py";target.parent.mkdir(exist_ok=True)
    shutil.copy2(Path(__file__),target)
    bat=ROOT/"ONE_CLICK_DASHBOARD_DATA_UPDATE.bat"
    if bat.exists():
        b=bat.read_text(encoding="utf-8",errors="ignore")
        marker='REM YUKTDHARA_AUTO_UPDATE_V1'
        if marker not in b:
            anchor='REM 3. Rebuild dashboard data if merge/build scripts exist'
            block='REM YUKTDHARA_AUTO_UPDATE_V1\r\n%PYTHON_CMD% "scripts_local\\update_yuktdhara_monitoring.py" --update-only\r\nif errorlevel 1 (echo ERROR: Yuktdhara update failed.& pause& exit /b 1)\r\n\r\n'
            b=b.replace(anchor,block+anchor)
            bat.write_text(b,encoding="utf-8")
    print("Yuktdhara dashboard module installed")

if __name__=="__main__":
    fetch()
    if "--update-only" not in sys.argv: install()
