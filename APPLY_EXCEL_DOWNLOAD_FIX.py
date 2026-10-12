from pathlib import Path
import shutil, re

REPO = Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
INDEX = REPO / "index.html"
SRC = Path(__file__).resolve().parent
JS_SRC = SRC / "srdm-excel-download-final.js"
JS_DST = REPO / "srdm-excel-download-final.js"

if not INDEX.exists():
    raise SystemExit("index.html not found")
if not JS_SRC.exists():
    raise SystemExit("srdm-excel-download-final.js missing beside installer")

# Backup index
bak = REPO / "index.before_excel_download_fix.bak.html"
if not bak.exists():
    shutil.copy2(INDEX, bak)

# Safe copy: if ZIP extracted inside repo, source==destination, so skip.
if JS_SRC.resolve() != JS_DST.resolve():
    shutil.copyfile(JS_SRC, JS_DST)
    print("Copied Excel JS")
else:
    print("Excel JS already inside repo; copy skipped")

s = INDEX.read_text(encoding="utf-8")

# Ensure Excel button exists.
if 'id="excelBtn"' not in s:
    anchor = '<button id="csvBtn">CSV Export</button>'
    if anchor not in s:
        raise SystemExit("CSV Export button not found")
    s = s.replace(anchor, anchor + '\n    <button id="excelBtn" class="excel-btn">Excel Download</button>', 1)

# Remove older version of this external script, then add fresh cache-busted script.
s = re.sub(
    r'<script src="srdm-excel-download-final\.js\?v=[^"]+"></script>\s*',
    '',
    s
)
tag = '<script src="srdm-excel-download-final.js?v=20260901excel2"></script>'
if tag not in s:
    if "</body>" not in s:
        raise SystemExit("</body> not found")
    s = s.replace("</body>", tag + "\n</body>", 1)

INDEX.write_text(s, encoding="utf-8")

# Verify
idx = INDEX.read_text(encoding="utf-8")
js = JS_DST.read_text(encoding="utf-8")
if 'id="excelBtn"' not in idx:
    raise SystemExit("VERIFY FAILED: Excel button missing")
if 'srdm-excel-download-final.js?v=20260901excel2' not in idx:
    raise SystemExit("VERIFY FAILED: Excel JS link missing")
if "SRDM_EXCEL_DOWNLOAD_FINAL_01_09_2026" not in js:
    raise SystemExit("VERIFY FAILED: Excel JS marker missing")

print("EXCEL DOWNLOAD FIX OK")
