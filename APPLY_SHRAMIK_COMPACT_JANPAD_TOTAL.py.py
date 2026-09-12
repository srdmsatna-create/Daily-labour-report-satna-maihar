from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parent
TARGET = ROOT / "shramik-niyojan.js"


def run(*args):
    subprocess.run(args, cwd=ROOT, check=True)


if not TARGET.exists():
    raise SystemExit("ERROR: Keep this file in the dashboard repository root beside shramik-niyojan.js")

text = TARGET.read_text(encoding="utf-8")

old_css = ".sn-table{width:100%;border-collapse:collapse;min-width:1980px;table-layout:fixed;border:2px solid #075d46}.sn-table th{background:#075d46;color:#fff;padding:11px 7px;border:2px solid #58a792;font-size:20px;line-height:1.2;position:sticky;top:0;z-index:1;vertical-align:middle}.sn-table td{padding:10px 8px;border:2px solid #8ebcaf;font-size:20px;line-height:1.25;font-weight:750;text-align:right;background-clip:padding-box;vertical-align:middle}"
new_css = ".sn-table{width:100%;border-collapse:collapse;min-width:1580px;table-layout:fixed;border:2px solid #075d46}.sn-table th{background:#075d46;color:#fff;padding:7px 4px;border:1px solid #58a792;font-size:16px;line-height:1.12;position:sticky;top:0;z-index:1;vertical-align:middle;overflow-wrap:anywhere}.sn-table td{padding:7px 5px;border:1px solid #8ebcaf;font-size:16px;line-height:1.18;font-weight:750;text-align:right;background-clip:padding-box;vertical-align:middle;overflow-wrap:anywhere}.sn-table th:nth-child(1),.sn-table td:nth-child(1){width:38px}.sn-table th:nth-child(2),.sn-table td:nth-child(2){width:64px}.sn-table th:nth-child(3),.sn-table td:nth-child(3){width:104px}.sn-table th:nth-child(4),.sn-table td:nth-child(4){width:112px}.sn-table th:nth-child(5),.sn-table td:nth-child(5){width:96px}"

old_total_css = ".sn-table .sn-total{background:#bfe7d6;color:#063d30;font-weight:950;border-top:3px solid #087f5b}"
new_total_css = ".sn-table .sn-janpad-total{background:#d9efe7!important;color:#063d30!important;font-weight:950;border-top:2px solid #087f5b;border-bottom:2px solid #087f5b}.sn-table .sn-total{background:#bfe7d6;color:#063d30;font-weight:950;border-top:3px solid #087f5b}"

old_draw = """    }else{
      rows.forEach(r=>h+=row(r,serial++));
      if(rows.length)h+=row(aggregate(rows,'कुल',dist.value==='ALL'?'':dist.value),'','sn-total');
    }"""
new_draw = """    }else if(level.value==='engineer'&&jan.value==='ALL'){
      order.forEach(j=>{
        const q=rows.filter(r=>nrm(r.janpad)===j);
        q.forEach(r=>h+=row(r,serial++));
        if(q.length)h+=row(aggregate(q,janpadName(j)+' जनपद कुल',q[0].district),'','sn-janpad-total');
      });
      if(rows.length)h+=row(aggregate(rows,dist.value==='ALL'?'सतना + मैहर महायोग':districtHindi(dist.value)+' जिला कुल',dist.value==='ALL'?'':dist.value),'','sn-total');
    }else{
      rows.forEach(r=>h+=row(r,serial++));
      if(rows.length)h+=row(aggregate(rows,'कुल',dist.value==='ALL'?'':dist.value),'','sn-total');
    }"""

if "sn-janpad-total" in text and "min-width:1580px" in text:
    print("Patch is already installed.")
else:
    missing = []
    if old_css not in text:
        missing.append("table CSS")
    if old_total_css not in text:
        missing.append("total-row CSS")
    if old_draw not in text:
        missing.append("draw function")
    if missing:
        raise SystemExit("ERROR: Expected code not found: " + ", ".join(missing))

    text = text.replace(old_css, new_css, 1)
    text = text.replace(old_total_css, new_total_css, 1)
    text = text.replace(old_draw, new_draw, 1)
    TARGET.write_text(text, encoding="utf-8")
    print("Updated shramik-niyojan.js")

try:
    run("git", "add", "--", "shramik-niyojan.js")
    diff = subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT)
    if diff.returncode != 0:
        run("git", "commit", "-m", "Compact Shramik columns and add Janpad totals")
        run("git", "pull", "--rebase")
        run("git", "push", "origin", "main")
        print("SUCCESS: Changes published to GitHub.")
    else:
        print("No new Git changes to publish.")
except subprocess.CalledProcessError as exc:
    print(f"Git stopped with exit code {exc.returncode}. The edited file is safe locally.")
    sys.exit(exc.returncode)
