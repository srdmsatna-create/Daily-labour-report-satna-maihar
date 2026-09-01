from pathlib import Path
import re, shutil

REPO = Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
P = REPO / "index.html"

if not P.exists():
    raise SystemExit("index.html not found")

B = REPO / "index.before_REMOVE_RAW_CODE_FINAL.bak.html"
if not B.exists():
    shutil.copy2(P, B)

s = P.read_text(encoding="utf-8")

ids = [
    "srdmFontPrintExcelStyle",
    "srdmFontPrintExcelScript",
    "srdmDirectFinalV2Style",
    "srdmDirectFinalV2Script",
    "srdmPrintBothOrientationStyle",
    "srdmPrintBothOrientationScript",
    "srdmCleanPrintStyle",
    "srdmCleanPrintScript",
    "srdmSinglePagePrintScript",
]
for _id in ids:
    s = re.sub(
        rf'<(?:script|style)\s+id="{re.escape(_id)}"[^>]*>.*?</(?:script|style)>',
        '',
        s,
        flags=re.I | re.S
    )

# Remove raw/broken JS that is currently visible on the page.
for token in [
    "function enrichHtml(mode)",
    "function officialPrint(){",
    "function printPortrait(){",
    "function portraitOfficialHtml(){",
]:
    while token in s:
        pos = s.find(token)
        start = max(0, pos - 60)
        gt = s.rfind(">", 0, pos)
        if gt >= 0 and pos - gt < 160:
            start = gt + 1
        end_script = s.find("</script>", pos)
        next_script = s.find("<script", pos + len(token))
        next_body = s.find("</body>", pos)
        candidates = [x for x in [end_script, next_script, next_body] if x >= 0]
        if not candidates:
            s = s[:start]
            break
        end = min(candidates)
        if end == end_script:
            end += len("</script>")
        s = s[:start] + s[end:]

# Remove visible template artifacts left by malformed code.
for pat in [
    r"\$\{esc\(title\)\}",
    r"\$\{esc\(meta\)\}",
    r"\$\{table\.outerHTML\}",
]:
    s = re.sub(pat, "", s)

# Avoid duplicate Excel buttons.
while s.count('id="excelBtn"') > 1:
    last = s.rfind('<button id="excelBtn"')
    end = s.find("</button>", last)
    if end < 0:
        break
    s = s[:last] + s[end + len("</button>"):]

if 'id="excelBtn"' not in s:
    anchor = '<button id="csvBtn">CSV Export</button>'
    if anchor in s:
        s = s.replace(anchor, anchor + '\n    <button id="excelBtn" class="excel-btn">Excel Download</button>', 1)

# Both orientations remain available.
s = s.replace(
    '<option value="portrait" selected>Portrait</option><option value="landscape">Landscape</option>',
    '<option value="portrait">Portrait</option><option value="landscape" selected>Landscape</option>'
)

MARK = "SRDM_CLEAN_SINGLE_TABLE_PRINT_FINAL_01_09_2026"
if MARK not in s:
    style = '''
<style id="srdmCleanSingleTablePrintFinalStyle">
/* SRDM_CLEAN_SINGLE_TABLE_PRINT_FINAL_01_09_2026 */
.excel-btn{background:#16794b!important;color:white!important;border-color:#16794b!important;font-weight:900!important}
.report-table th,.report-table td{font-size:calc(11.2px * var(--table-font-scale))!important;line-height:1.25!important}
</style>
'''
    if "</head>" not in s:
        raise RuntimeError("</head> not found")
    s = s.replace("</head>", style + "\n</head>", 1)

    js = r'''
<script id="srdmCleanSingleTablePrintFinalScript">
/* SRDM_CLEAN_SINGLE_TABLE_PRINT_FINAL_01_09_2026 */
(function(){
  function byId(id){ return document.getElementById(id); }
  function safeText(v){
    return String(v == null ? "" : v)
      .replace(/&/g,"&amp;")
      .replace(/</g,"&lt;")
      .replace(/>/g,"&gt;")
      .replace(/"/g,"&quot;");
  }
  function cleanTableHtml(){
    var t = byId("reportTable");
    if(!t) return "";
    var c = t.cloneNode(true);
    var bad = c.querySelectorAll("script,style,template,noscript");
    for(var i=0;i<bad.length;i++) bad[i].remove();
    var all = c.querySelectorAll("*");
    for(var j=0;j<all.length;j++){
      all[j].style.transform="none";
      all[j].style.rotate="none";
      all[j].style.writingMode="horizontal-tb";
    }
    return c.outerHTML;
  }
  function doPrint(ev){
    if(ev){
      ev.preventDefault();
      ev.stopPropagation();
      if(ev.stopImmediatePropagation) ev.stopImmediatePropagation();
    }
    var orient = byId("printOrientation");
    var mode = orient && orient.value==="portrait" ? "portrait" : "landscape";
    var title = byId("viewTitle") ? byId("viewTitle").textContent : "VBGRAMG Report";
    var meta = byId("viewMeta") ? byId("viewMeta").textContent : "";
    var table = cleanTableHtml();
    if(!table) return;

    var page = mode==="portrait" ? "A4 portrait" : "A4 landscape";
    var font = mode==="portrait" ? "6.8px" : "8.0px";

    var html = '<!doctype html><html><head><meta charset="utf-8"><title>'+safeText(title)+'</title>'+
      '<style>'+
      '@page{size:'+page+';margin:6mm}'+
      '*{box-sizing:border-box}html,body{margin:0;padding:0;background:#fff;transform:none!important}'+
      'body{font-family:Arial,sans-serif;color:#142238}'+
      'h1{font-size:16px;line-height:1.1;margin:0 0 2px;color:#0b3159}'+
      '.meta{font-size:9px;color:#607286;margin:0 0 6px}'+
      'table{width:100%!important;min-width:0!important;max-width:100%!important;border-collapse:collapse!important;table-layout:fixed!important;font-size:'+font+'!important;transform:none!important;writing-mode:horizontal-tb!important}'+
      'th,td{border:1px solid #7293b5!important;padding:2.4px 1.8px!important;text-align:center!important;vertical-align:middle!important;white-space:normal!important;overflow-wrap:anywhere!important;line-height:1.15!important;transform:none!important;writing-mode:horizontal-tb!important}'+
      'th{background:#cfe0f5!important;color:#0a3158!important;font-weight:800!important}'+
      '.badge{font-size:inherit!important;padding:1px 2px!important}'+
      '</style></head><body>'+
      '<h1>'+safeText(title)+'</h1><div class="meta">'+safeText(meta)+'</div>'+
      table+
      '</body></html>';

    var w = window.open("","_blank","width=1180,height=900");
    if(!w){ alert("Print popup blocked है।"); return; }
    w.document.open();
    w.document.write(html);
    w.document.close();
    w.focus();
    setTimeout(function(){ w.print(); },400);
  }

  var orient = byId("printOrientation");
  if(orient){
    orient.disabled=false;
    orient.title="Portrait या Landscape चुनें";
  }

  var btn = byId("printBtn");
  if(btn){
    btn.textContent="Print / PDF";
    btn.addEventListener("click",doPrint,true);
  }

  var excel = byId("excelBtn");
  if(excel){
    excel.addEventListener("click",function(){
      var title = byId("viewTitle") ? byId("viewTitle").textContent : "VBGRAMG Report";
      var meta = byId("viewMeta") ? byId("viewMeta").textContent : "";
      var table = cleanTableHtml();
      if(!table) return;
      var html = '<html><head><meta charset="utf-8"></head><body><h2>'+safeText(title)+'</h2><p>'+safeText(meta)+'</p>'+table+'</body></html>';
      var blob = new Blob(["\ufeff",html],{type:"application/vnd.ms-excel;charset=utf-8"});
      var a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = "VBGRAMG-current-report.xls";
      document.body.appendChild(a);
      a.click();
      a.remove();
      setTimeout(function(){ URL.revokeObjectURL(a.href); },500);
    });
  }
})();
</script>
'''
    if "</body>" not in s:
        raise RuntimeError("</body> not found")
    s = s.replace("</body>", js + "\n</body>", 1)

P.write_text(s, encoding="utf-8")

for token in ["function enrichHtml(mode)", "Part A — GP / Screen-2 / Individual Land", "Part B — Community / PMAY-G / Ek Bagiya / Recovery"]:
    if token in s:
        raise SystemExit("CLEANUP FAILED: still contains " + token)

print("RAW CODE REMOVED")
print("CLEAN SINGLE-TABLE PRINT INSTALLED")
