from pathlib import Path
import re, sys, shutil

REPO = Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")

LOCK = {
    "AMARPATAN": (1044,109),
    "MAIHAR": (1814,86),
    "MAJHGAWAN": (1536,85),
    "NAGOD": (1896,100),
    "RAMNAGAR": (986,106),
    "RAMPUR BAGHELAN": (2943,75),
    "SATNA": (473,94),
    "UNCHAHARA": (1303,101),
}

RECOVERY = {
    "AMARPATAN":61,
    "MAIHAR":41,
    "MAJHGAWAN":51,
    "NAGOD":155,
    "RAMNAGAR":67,
    "RAMPUR BAGHELAN":44,
    "SATNA":59,
    "UNCHAHARA":71,
}

def backup(path: Path):
    if path.exists():
        bak = path.with_suffix(path.suffix + ".before_lock_recovery_fix.bak")
        if not bak.exists():
            shutil.copy2(path, bak)

def patch_merge():
    p = REPO / "scripts" / "merge_official_summary.py"
    if not p.exists():
        raise RuntimeError(f"Missing {p}")
    backup(p)
    s = p.read_text(encoding="utf-8")
    marker = "# SRDM_LOCK_RECOVERY_RESTORE_01_09_2026"
    if marker in s:
        print("merge lock already installed")
        return

    # Insert datetime.date import safely.
    if "from datetime import datetime,timezone" in s:
        s = s.replace("from datetime import datetime,timezone",
                      "from datetime import datetime,timezone,date", 1)
    elif "from datetime import datetime, timezone" in s:
        s = s.replace("from datetime import datetime, timezone",
                      "from datetime import datetime, timezone, date", 1)

    # Find clean.append(z), and inject lock immediately before it.
    needle = "        clean.append(z)"
    if needle not in s:
        raise RuntimeError("Could not find clean.append(z) in merge_official_summary.py")

    lock_lines = [
        "        # SRDM_LOCK_RECOVERY_RESTORE_01_09_2026",
        "        _LOCK_END = date(2026,9,6)",
        "        _LOCK = {",
    ]
    for j,(pm,ek) in LOCK.items():
        lock_lines.append(f"            {j!r}: ({pm},{ek}),")
    lock_lines += [
        "        }",
        "        if datetime.now().date() <= _LOCK_END and z['janpad'] in _LOCK:",
        "            z['pmayOngoing'], z['ekOngoing'] = _LOCK[z['janpad']]",
        needle,
    ]
    s = s.replace(needle, "\n".join(lock_lines), 1)
    p.write_text(s, encoding="utf-8")
    print("merge lock installed")

def patch_recovery_js(path: Path):
    if not path.exists():
        return False
    s = path.read_text(encoding="utf-8")
    marker = "SRDM JANPAD RECOVERY FIX 01-09-2026"
    if marker in s:
        print(path.name, "recovery fix already installed")
        return True

    old = """if(total)n=recoverySource().length;else{const scope={};if(iJan>=0&&td[iJan])scope.janpad=clean(td[iJan].textContent);if(iEng>=0&&td[iEng])scope.engineer=clean(td[iEng].textContent);if(iCl>=0&&td[iCl])scope.cluster=clean(td[iCl].textContent);if(iGp>=0&&td[iGp])scope.gp=clean(td[iGp].textContent);if(iCode>=0&&td[iCode])scope.code=clean(td[iCode].textContent);if(iCat>=0&&td[iCat])scope.category=clean(td[iCat].textContent);if(iDist>=0&&td[iDist])scope.district=clean(td[iDist].textContent);n=recoveryCountForScope(scope)}"""
    new = """if(total)n=recoverySource().length;else{const scope={};/* SRDM JANPAD RECOVERY FIX 01-09-2026 */if(iJan>=0&&td[iJan])scope.janpad=clean(td[iJan].textContent);if(!scope.janpad){const known=['AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'];const hit=td.map(x=>clean(x.textContent)).find(x=>known.includes(normJanpad(x)));if(hit)scope.janpad=normJanpad(hit);}if(iEng>=0&&td[iEng])scope.engineer=clean(td[iEng].textContent);if(iCl>=0&&td[iCl])scope.cluster=clean(td[iCl].textContent);if(iGp>=0&&td[iGp])scope.gp=clean(td[iGp].textContent);if(iCode>=0&&td[iCode])scope.code=clean(td[iCode].textContent);if(iCat>=0&&td[iCat])scope.category=clean(td[iCat].textContent);if(iDist>=0&&td[iDist])scope.district=clean(td[iDist].textContent);n=recoveryCountForScope(scope)}"""

    if old not in s:
        raise RuntimeError(f"Recovery insertion point not found in {path.name}")
    backup(path)
    s = s.replace(old, new, 1)
    path.write_text(s, encoding="utf-8")
    print(path.name, "Janpad recovery fix installed")
    return True

def apply_lock_to_csv():
    import csv
    candidates = [REPO/"data"/"official-summary.csv", REPO/"official-summary.csv"]
    p = next((x for x in candidates if x.exists()), None)
    if not p:
        raise RuntimeError("official-summary.csv not found")
    backup(p)
    with p.open(encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        fields = list(reader.fieldnames or [])
    for k in ["pmayOngoing","ekOngoing"]:
        if k not in fields: fields.append(k)
    found=set()
    for r in rows:
        j=(r.get("janpad") or "").strip().upper()
        if j in LOCK:
            r["pmayOngoing"]=str(LOCK[j][0])
            r["ekOngoing"]=str(LOCK[j][1])
            found.add(j)
    if found != set(LOCK):
        raise RuntimeError(f"CSV Janpad validation failed. Found {sorted(found)}")
    with p.open("w", encoding="utf-8-sig", newline="") as f:
        w=csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)
    print("CSV lock applied:", p)

def verify_recovery_source():
    # Verify expected Janpad counts from embedded ongoing-details if present.
    p=REPO/"ongoing-details.js"
    if not p.exists():
        print("ongoing-details.js not found; recovery source verification skipped")
        return
    s=p.read_text(encoding="utf-8", errors="ignore")
    # Lightweight regex count of recoveryWork:1 by janpad from JSON-like objects.
    counts={k:0 for k in RECOVERY}
    for m in re.finditer(r'\{[^{}]*?"janpad":"([^"]+)"[^{}]*?"recoveryWork":([0-9.]+)[^{}]*?\}',s):
        j=m.group(1).strip().upper()
        try: rw=float(m.group(2))
        except: rw=0
        if j in counts and rw>0: counts[j]+=1
    # Only hard-fail when parsing finds recovery objects but disagrees.
    if sum(counts.values())>0 and counts != RECOVERY:
        raise RuntimeError(f"Recovery source counts mismatch: {counts}")
    print("Recovery expected Janpad counts:", RECOVERY, "total", sum(RECOVERY.values()))

if __name__ == "__main__":
    patch_merge()
    ok_index = patch_recovery_js(REPO/"index.html")
    ok_app = patch_recovery_js(REPO/"app.js") if (REPO/"app.js").exists() else False
    if not ok_index:
        raise RuntimeError("index.html was not patched")
    apply_lock_to_csv()
    verify_recovery_source()
    print("PATCH COMPLETE")
