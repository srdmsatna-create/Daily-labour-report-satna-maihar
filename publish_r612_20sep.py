#!/usr/bin/env python3
"""Publish the 20 Sep R6.12 snapshot without changing the 13 Sep baseline.

Usage: py -3 publish_r612_20sep.py VBGRAMG_R612_Satna_Maihar_20-09-2026.xlsx C:/path/to/Daily-labour-report-satna-maihar
Requires: py -3 -m pip install openpyxl
"""
import argparse
import csv
import html
import json
import subprocess
import sys
from collections import Counter
from datetime import date, datetime
from pathlib import Path

try:
    from openpyxl import load_workbook
except ImportError:
    sys.exit("openpyxl is missing. Run: py -3 -m pip install openpyxl")

EXPECTED = {"Ongoing": 15618, "Completed": 109, "Physically Completed": 1123}
FIXED = ("MGNREGA Booked Wages to 30 Jun Rs (fixed)",
         "MGNREGA Booked Material to 30 Jun Rs (fixed)")
ROOT = "r612-20-09-2026"
REPO_NAME = "srdmsatna-create/daily-labour-report-satna-maihar"


def git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], check=True,
                          text=True, capture_output=True).stdout.strip()


def plain(value):
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return "" if value is None else value


def write_csv(path, columns, rows):
    with path.open("w", encoding="utf-8-sig", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(columns)
        writer.writerows(rows)


def write_page(path, title, count, json_file, other_link):
    title = html.escape(title)
    path.write_text(f'''<!doctype html>
<html lang="hi"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>R6.12 | {title} | 20.09.2026</title>
<style>body{{font:16px system-ui;margin:0;color:#162534;background:#f4f7fa}}header,main{{max-width:1200px;margin:auto;padding:20px}}header{{background:#153b61;color:white;max-width:none}}header div{{max-width:1200px;margin:auto}}a{{color:#075b9e}}header a{{color:white}}.box{{background:white;border-radius:10px;padding:18px;margin:16px 0;box-shadow:0 2px 12px #dce4ec}}input{{padding:12px;width:min(100%,410px);font-size:16px}}table{{border-collapse:collapse;width:100%;font-size:14px}}th,td{{border:1px solid #dae1e8;padding:9px;text-align:left;vertical-align:top}}th{{background:#e9f0f6;position:sticky;top:0}}.scroll{{overflow:auto;max-height:68vh}}button{{padding:8px 14px;margin:6px;cursor:pointer}}@media print{{header,input,button,.nav{{display:none}}.scroll{{max-height:none;overflow:visible}}}}</style>
<header><div><h1>R6.12 — {title}</h1><p>Satna + Maihar · 20.09.2026 · {count:,} कार्य</p></div></header>
<main><div class="box nav"><a href="{other_link}">दूसरी स्थिति की रिपोर्ट</a> · <a href="{json_file[:-5]}.csv">पूरा CSV डाउनलोड करें</a></div>
<div class="box"><p>MGNREGA के 13.09.2026 fixed baseline कॉलम मूल फ़ाइल से सुरक्षित रखे गए हैं। यहाँ VBGRAMG snapshot की अलग स्थिति दिखाई गई है।</p>
<input id="q" placeholder="कार्य कोड, जनपद, उपयंत्री या श्रेणी खोजें" aria-label="खोज"><p id="summary"></p>
<div class="scroll"><table><thead><tr><th>जिला</th><th>जनपद</th><th>GP</th><th>उपयंत्री</th><th>क्लस्टर</th><th>कार्य कोड</th><th>कार्य</th><th>श्रेणी</th><th>स्थिति</th><th>स्वीकृत ₹</th><th>बुक्ड ₹</th><th>मानव दिवस</th></tr></thead><tbody id="rows"></tbody></table></div>
<button id="prev">पिछला</button><span id="page"></span><button id="next">अगला</button></div></main>
<script>
let data=[],filtered=[],page=0;const size=100;const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({{'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}}[c]));
function render(){{document.querySelector('#summary').textContent=filtered.length.toLocaleString('en-IN')+' कार्य';document.querySelector('#page').textContent=' पृष्ठ '+(page+1)+' / '+Math.max(1,Math.ceil(filtered.length/size))+' ';document.querySelector('#rows').innerHTML=filtered.slice(page*size,(page+1)*size).map(r=>'<tr>'+r.map(v=>'<td>'+esc(v)+'</td>').join('')+'</tr>').join('');document.querySelector('#prev').disabled=page===0;document.querySelector('#next').disabled=(page+1)*size>=filtered.length}}
document.querySelector('#q').oninput=e=>{{const q=e.target.value.trim().toLowerCase();filtered=q?data.filter(r=>r.some(x=>String(x).toLowerCase().includes(q))):data;page=0;render()}};
document.querySelector('#prev').onclick=()=>{{page--;render()}};document.querySelector('#next').onclick=()=>{{page++;render()}};
fetch('{json_file}').then(r=>{{if(!r.ok)throw Error(r.status);return r.json()}}).then(d=>{{data=filtered=d;render()}}).catch(e=>document.querySelector('#summary').textContent='डेटा लोड नहीं हुआ: '+e);
</script></html>''', encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workbook", type=Path)
    parser.add_argument("repo", type=Path)
    parser.add_argument("--prepare-only", action="store_true", help="Generate files without git commit/push")
    args = parser.parse_args()
    repo = args.repo.resolve()
    if not args.workbook.is_file() or not repo.is_dir():
        parser.error("Excel file or repository directory not found")
    remote = git(repo, "remote", "get-url", "origin").lower().removesuffix(".git")
    if REPO_NAME not in remote:
        sys.exit("Wrong repository origin; no files changed: " + remote)
    if git(repo, "status", "--porcelain"):
        sys.exit("Repository has uncommitted changes. Commit or set them aside first; no files changed.")
    if not args.prepare_only:
        git(repo, "pull", "--ff-only", "origin", "main")

    book = load_workbook(args.workbook, read_only=True, data_only=True)
    if "All Works" not in book or "Ek Bagiya" not in book:
        sys.exit("Required worksheets are missing")
    source = book["All Works"].values
    columns = list(next(source))
    required = ["Work Code", "Work Status", "Work Start Fin Yr", "Final Category",
                "Sub Engineer / Upyantri (13 Sep mapping)", "Cluster (13 Sep mapping)", *FIXED]
    if any(k not in columns for k in required):
        sys.exit("Required workbook columns are missing")
    index = {key: columns.index(key) for key in columns}
    groups = {status: [] for status in EXPECTED}
    codes = set()
    for row in source:
        code = row[index["Work Code"]]
        if not code:
            continue
        if code in codes:
            sys.exit("Duplicate Work Code: " + str(code))
        codes.add(code)
        status = str(row[index["Work Status"]]).strip()
        if status not in groups:
            sys.exit("Unexpected Work Status: " + status)
        if any(not row[index[k]] for k in required[3:6]):
            sys.exit("Missing category/engineer/cluster for " + str(code))
        groups[status].append([plain(value) for value in row])
    counts = {key: len(value) for key, value in groups.items()}
    if counts != EXPECTED or len(codes) != 16850:
        sys.exit(f"Status count mismatch: {counts}; expected {EXPECTED}. No files changed.")
    bag = book["Ek Bagiya"].values
    bag_columns = list(next(bag))
    bi = {key: bag_columns.index(key) for key in bag_columns}
    bag_rows = [r for r in bag if r[bi["Work Code"]]]
    if len(bag_rows) != 755 or Counter(str(r[bi["Work Start Fin Yr"]]) for r in bag_rows) != {"2025-2026": 746, "2026-2027": 9}:
        sys.exit("Ek Bagiya count/FY mismatch. No files changed.")
    all_by_code = {r[index["Work Code"]]: r for rows in groups.values() for r in rows}
    for row in bag_rows:
        match = all_by_code.get(row[bi["Work Code"]])
        if match is None or any(row[bi[k]] is None or row[bi[k]] != match[index[k]] for k in FIXED):
            sys.exit("Fixed MGNREGA baseline mismatch: " + str(row[bi["Work Code"]]))

    folder = repo / ROOT
    folder.mkdir(exist_ok=True)
    selected = ["District", "Janpad", "Panchayat", "Sub Engineer / Upyantri (13 Sep mapping)",
                "Cluster (13 Sep mapping)", "Work Code", "Work Name", "Final Category",
                "Work Status", "Sanction Total Rs", "Booked Total Since Inception Rs", "Total Mandays (portal)"]
    outputs = []
    for name, rows in (("ongoing", groups["Ongoing"]),
                       ("completed", groups["Completed"] + groups["Physically Completed"])):
        csv_path = folder / (name + ".csv")
        json_path = folder / (name + ".json")
        write_csv(csv_path, columns, rows)
        json_path.write_text(json.dumps([[r[index[k]] for k in selected] for r in rows],
                                        ensure_ascii=False, separators=(",", ":"), default=str), encoding="utf-8")
        outputs.extend([csv_path, json_path])
    ongoing_page = folder / "index.html"
    completed_page = folder / "completed.html"
    write_page(ongoing_page, "Ongoing", 15618, "ongoing.json", "completed.html")
    write_page(completed_page, "Completed + Physically Completed", 1232, "completed.json", "index.html")
    outputs.extend([ongoing_page, completed_page])
    print("Verified: 16,850 total; 15,618 Ongoing; 109 Completed; 1,123 Physically Completed; 755 fixed-baseline Ek Bagiya.")
    print("Prepared:", folder)
    if args.prepare_only:
        return
    git(repo, "add", "--", *(str(p.relative_to(repo)) for p in outputs))
    git(repo, "commit", "-m", "Publish 20 Sep R6.12 status-separated VBGRAMG snapshot")
    git(repo, "push", "origin", "main")
    print("Published to GitHub Pages path: /" + ROOT + "/")


if __name__ == "__main__":
    main()
