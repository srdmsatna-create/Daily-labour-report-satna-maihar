from pathlib import Path
import shutil, re, os

REPO=Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
INDEX=REPO/"index.html"
SRC=Path(__file__).resolve().parent

if not INDEX.exists():
    raise SystemExit("index.html not found")

backup=REPO/"index.before_FINAL_READABLE_PRINT_V2.bak.html"
if not backup.exists():
    shutil.copy2(INDEX, backup)

def copy_if_needed(src: Path, dst: Path):
    src=src.resolve()
    dst=dst.resolve()
    if src == dst:
        print("SKIP COPY - already in repo:", dst.name)
        return
    if dst.exists():
        try:
            if src.read_bytes() == dst.read_bytes():
                print("SKIP COPY - same content:", dst.name)
                return
        except Exception:
            pass
    shutil.copyfile(src, dst)
    print("COPIED:", dst.name)

copy_if_needed(SRC/"srdm-readable-print-final.css", REPO/"srdm-readable-print-final.css")
copy_if_needed(SRC/"srdm-readable-print-final.js", REPO/"srdm-readable-print-final.js")

s=INDEX.read_text(encoding="utf-8")

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
        ends=[x for x in [s.find("<script",pos+1),s.find("</script>",pos),s.find("</body>",pos)] if x>=0]
        if not ends:
            s=s[:start]
            break
        end=min(ends)
        if s.startswith("</script>",end):
            end+=9
        s=s[:start]+s[end:]

s=s.replace(
    '<option value="portrait" selected>Portrait</option><option value="landscape">Landscape</option>',
    '<option value="portrait">Portrait</option><option value="landscape" selected>Landscape</option>'
)

css_tag='<link rel="stylesheet" href="srdm-readable-print-final.css?v=20260901v2">'
# remove old versioned reference if present
s=re.sub(r'<link rel="stylesheet" href="srdm-readable-print-final\.css\?v=[^"]+">','',s)
if css_tag not in s:
    s=s.replace("</head>", css_tag+"\n</head>",1)

js_tag='<script src="srdm-readable-print-final.js?v=20260901v2"></script>'
s=re.sub(r'<script src="srdm-readable-print-final\.js\?v=[^"]+"></script>','',s)
if js_tag not in s:
    s=s.replace("</body>", js_tag+"\n</body>",1)

INDEX.write_text(s,encoding="utf-8")

final=INDEX.read_text(encoding="utf-8")
for token in [
    "function enrichHtml(mode)",
    "${makeTable(hA,rowsA,8.5)}",
    "Part A — GP / Screen-2 / Individual Land",
    "Part B — Community / PMAY-G / Ek Bagiya / Recovery"
]:
    if token in final:
        raise SystemExit("VERIFY FAILED: "+token)

print("FINAL READABLE PRINT V2 PATCH OK")
