from pathlib import Path
import shutil, re

REPO=Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
INDEX=REPO/"index.html"
SRC=Path(__file__).resolve().parent

if not INDEX.exists():
    raise SystemExit("index.html not found")

backup=REPO/"index.before_FINAL_READABLE_PRINT.bak.html"
if not backup.exists():
    shutil.copy2(INDEX, backup)

# Copy external assets; this avoids JavaScript appearing as visible page text.
shutil.copy2(SRC/"srdm-readable-print-final.css", REPO/"srdm-readable-print-final.css")
shutil.copy2(SRC/"srdm-readable-print-final.js", REPO/"srdm-readable-print-final.js")

s=INDEX.read_text(encoding="utf-8")

# Remove all previous experimental injected print blocks if any remain.
ids=[
 "srdmFontPrintExcelStyle","srdmFontPrintExcelScript",
 "srdmDirectFinalV2Style","srdmDirectFinalV2Script",
 "srdmPrintBothOrientationStyle","srdmPrintBothOrientationScript",
 "srdmCleanPrintStyle","srdmCleanPrintScript",
 "srdmSinglePagePrintScript","srdmCleanSingleTablePrintFinalStyle",
 "srdmCleanSingleTablePrintFinalScript","srdmSafeExcelStyle","srdmSafeExcelOnly"
]
for _id in ids:
    s=re.sub(
        rf'<(?:script|style)\s+id="{re.escape(_id)}"[^>]*>.*?</(?:script|style)>',
        '',
        s,
        flags=re.I|re.S
    )

# Remove visible raw fragments from failed experiments.
for token in [
    "function enrichHtml(mode)",
    "function officialPrint(){",
    "function printPortrait(){",
    "${makeTable(hA,rowsA,8.5)}",
    "Part A — GP / Screen-2 / Individual Land",
    "Part B — Community / PMAY-G / Ek Bagiya / Recovery"
]:
    while token in s:
        pos=s.find(token)
        start=max(0,pos-80)
        gt=s.rfind(">",0,pos)
        if gt>=0 and pos-gt<200:
            start=gt+1
        end_candidates=[x for x in [s.find("<script",pos+1),s.find("</script>",pos),s.find("</body>",pos)] if x>=0]
        if not end_candidates:
            s=s[:start]
            break
        end=min(end_candidates)
        if s.startswith("</script>",end):
            end+=9
        s=s[:start]+s[end:]

# Both orientation choices remain.
s=s.replace(
    '<option value="portrait" selected>Portrait</option><option value="landscape">Landscape</option>',
    '<option value="portrait">Portrait</option><option value="landscape" selected>Landscape</option>'
)

# Link external CSS once.
css_tag='<link rel="stylesheet" href="srdm-readable-print-final.css?v=20260901">'
if css_tag not in s:
    if "</head>" not in s: raise SystemExit("</head> missing")
    s=s.replace("</head>", css_tag+"\n</head>",1)

# Load external JS once.
js_tag='<script src="srdm-readable-print-final.js?v=20260901"></script>'
if js_tag not in s:
    if "</body>" not in s: raise SystemExit("</body> missing")
    s=s.replace("</body>", js_tag+"\n</body>",1)

INDEX.write_text(s,encoding="utf-8")

# Hard verify broken print source is not visible in HTML.
final=INDEX.read_text(encoding="utf-8")
for token in [
    "function enrichHtml(mode)",
    "${makeTable(hA,rowsA,8.5)}",
    "Part A — GP / Screen-2 / Individual Land",
    "Part B — Community / PMAY-G / Ek Bagiya / Recovery"
]:
    if token in final:
        raise SystemExit("VERIFY FAILED: "+token)

print("FINAL READABLE PRINT PATCH OK")
