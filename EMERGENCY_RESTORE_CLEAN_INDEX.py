from pathlib import Path
import shutil

REPO = Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
INDEX = REPO / "index.html"

preferred = [
    REPO / "index.html.before_lock_recovery_fix.bak",
    REPO / "index.before_font_print_excel_fix.bak.html",
    REPO / "index.before_DIRECT_FINAL_FIX_V2.bak.html",
    REPO / "index.before_PRINT_BOTH_ORIENTATION_FIX.bak.html",
    REPO / "index.before_SINGLE_PAGE_PRINT_FIX.bak.html",
    REPO / "index.before_REMOVE_RAW_CODE_FINAL.bak.html",
]

bad = [
    "function enrichHtml(mode)",
    "${esc(title)}",
    "${esc(meta)}",
    "${table.outerHTML}",
    "${makeTable(hA,rowsA,8.5)}",
    "Part A — GP / Screen-2 / Individual Land",
    "Part B — Community / PMAY-G / Ek Bagiya / Recovery",
    "srdmDirectFinalV2Script",
    "srdmPrintBothOrientationScript",
    "srdmCleanPrintScript",
    "srdmSinglePagePrintScript",
]

def score(text):
    return sum(text.count(x) for x in bad)

candidates=[]
seen=set()
for p in preferred + list(REPO.glob("index*.bak*")):
    if p in seen or not p.exists():
        continue
    seen.add(p)
    try:
        t=p.read_text(encoding="utf-8")
    except Exception:
        continue
    if "<html" in t.lower() and "</html>" in t.lower():
        candidates.append((score(t), -len(t), p, t))

if not candidates:
    raise SystemExit("No usable index backup found.")

candidates.sort(key=lambda x:(x[0],x[1]))
sc, _, chosen, s = candidates[0]
if sc != 0:
    raise SystemExit("No CLEAN backup found. Best candidate: %s score=%s" % (chosen.name, sc))

if INDEX.exists():
    shutil.copy2(INDEX, REPO / "index.BROKEN_RAW_CODE_01_09_2026.bak.html")

INDEX.write_text(s, encoding="utf-8")
print("RESTORED CLEAN INDEX FROM:", chosen.name)

s = INDEX.read_text(encoding="utf-8")

# Slightly larger font only.
s = s.replace("let fontScale=1;", "let fontScale=1.12;", 1)

# Both print orientations remain available; default Landscape.
s = s.replace(
    '<option value="portrait" selected>Portrait</option><option value="landscape">Landscape</option>',
    '<option value="portrait">Portrait</option><option value="landscape" selected>Landscape</option>'
)

# Add Excel button if absent.
if 'id="excelBtn"' not in s:
    anchor = '<button id="csvBtn">CSV Export</button>'
    if anchor in s:
        s = s.replace(anchor, anchor + '\n    <button id="excelBtn" class="excel-btn">Excel Download</button>', 1)

safe_excel = """
<style id="srdmSafeExcelStyle">
.excel-btn{background:#16794b!important;color:#fff!important;border-color:#16794b!important;font-weight:900!important}
</style>
<script id="srdmSafeExcelOnly">
(function(){
  var b=document.getElementById("excelBtn");
  if(!b)return;
  b.addEventListener("click",function(){
    var t=document.getElementById("reportTable");
    if(!t)return;
    var c=t.cloneNode(true);
    var bad=c.querySelectorAll("script,style,template,noscript");
    for(var i=0;i<bad.length;i++){bad[i].remove();}
    var title=document.getElementById("viewTitle");
    var meta=document.getElementById("viewMeta");
    var html="<html><head><meta charset='utf-8'></head><body><h2>"+
      (title?title.textContent:"VBGRAMG Report")+"</h2><p>"+
      (meta?meta.textContent:"")+"</p>"+c.outerHTML+"</body></html>";
    var blob=new Blob(["\\ufeff",html],{type:"application/vnd.ms-excel;charset=utf-8"});
    var a=document.createElement("a");
    a.href=URL.createObjectURL(blob);
    a.download="VBGRAMG-current-report.xls";
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function(){URL.revokeObjectURL(a.href);},500);
  });
})();
</script>
"""

if 'id="srdmSafeExcelOnly"' not in s:
    if "</body>" not in s:
        raise SystemExit("</body> not found")
    s=s.replace("</body>", safe_excel + "\n</body>", 1)

INDEX.write_text(s, encoding="utf-8")

final=INDEX.read_text(encoding="utf-8")
for token in bad:
    if token in final:
        raise SystemExit("VERIFY FAILED: raw marker remains: "+token)

print("VERIFY OK: RAW CODE / PART A / PART B REMOVED")
print("Original Print/PDF restored. Excel Download retained.")
