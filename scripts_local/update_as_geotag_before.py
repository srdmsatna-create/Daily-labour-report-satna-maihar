#!/usr/bin/env python3
"""Fetch AS-approved /YD/ work rows and before-stage geotag status."""
import json
import re
import sys
import time
from datetime import date, datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

ROOT = Path(__file__).resolve().parents[1]
SEARCH_URL = (
    "https://vbgramgrep.dord.gov.in/vbgramg/specific_work_search_rpt.aspx"
    "?payload=O9l6bN6AlHZgNqmUmUbD-_Wlw6J25huImwdkIbmM4uSNTDKRaZbIdLI-cc4ucZ2mr5bWHHTiru9H_pAMTgtJ6SwRjR4hgE7P6n-GOWd4wdVj0rfZ2rxv6aEsaYMEaJ-sHEPzh8QI6VVN-tQY2mMZtEOiK7ITn6wQQgYNPYR1PiYAuOH4zKOOj9_6ueUj57Lp"
)
FY = "2026-2027"
DATE_FROM = date(2026, 10, 1)
BLOCKS = ["AMARPATAN", "MAIHAR", "MAJHGAWAN", "NAGOD", "RAMNAGAR", "RAMPUR BAGHELAN", "SATNA", "UNCHAHARA"]
MAIHAR_BLOCKS = {"AMARPATAN", "MAIHAR", "RAMNAGAR"}
SOURCE_HOST = "vbgramgrep.dord.gov.in"
AS_LABEL = "Administrative/ Financial Sanction"
GEOTAG_LABEL = "Geotagged Photograph of the Project/Work at three stages-before,during and after"


def clean(value):
    return re.sub(r"\s+", " ", str(value or "")).strip()


def norm(value):
    return re.sub(r"[^a-z0-9]+", " ", clean(value).lower()).strip()


def parse_date(value):
    for fmt in ("%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(clean(value), fmt).date()
        except ValueError:
            pass
    return None


def safe_href(base, href):
    url = urljoin(base, href)
    parsed = urlparse(url)
    if parsed.scheme != "https" or parsed.hostname != SOURCE_HOST:
        raise ValueError("Unexpected official link host")
    return url


def extract_work_rows(page):
    return page.locator("table").evaluate_all("""tables => {
      const clean = s => (s || '').replace(/\\s+/g, ' ').trim();
      for (const table of tables) {
        const rows = Array.from(table.rows).filter(r => r.closest('table') === table);
        const headers = rows.map(r => Array.from(r.cells).map(c => clean(c.innerText)));
        const hi = headers.findIndex(c => c.some(x => /Work Code/i.test(x)) && c.some(x => /Work Name/i.test(x)));
        if (hi < 0) continue;
        const h = headers[hi].map(x => x.toLowerCase());
        const ix = {fy:h.findIndex(x=>/work start fin year/i.test(x)),code:h.findIndex(x=>/work code/i.test(x)),name:h.findIndex(x=>/work name/i.test(x)),status:h.findIndex(x=>/work status/i.test(x)),view:h.findIndex(x=>/view e-work file/i.test(x))};
        return rows.slice(hi+1).map(r => {
          const c=Array.from(r.cells), get=i=>i>=0&&c[i]?clean(c[i].innerText):'';
          const a=ix.view>=0&&c[ix.view]?c[ix.view].querySelector('a[href]'):null;
          return {fy:get(ix.fy),code:get(ix.code),name:get(ix.name),status:get(ix.status),href:a?a.href:''};
        }).filter(x=>x.code && x.href);
      }
      return [];
    }""")


def extract_detail(page):
    return page.locator("table").evaluate_all("""tables => {
      const clean=s=>(s||'').replace(/\\s+/g,' ').trim(), fields={}, docs={};
      for(const table of tables){
        const rows=Array.from(table.rows).filter(r=>r.closest('table')===table);
        for(const row of rows){
          const cells=Array.from(row.cells).map(c=>clean(c.innerText));
          for(let i=0;i+1<cells.length;i+=2) if(cells[i]) fields[cells[i]]=cells[i+1]||'';
          if(cells.length>=3){
            const label=cells[1], a=row.querySelector('a[href]');
            if(/Administrative\\/ Financial Sanction/i.test(label)) docs.as={status:a?clean(a.innerText):cells[2],href:a?a.href:''};
            if(/Geotagged Photograph of the Project\\/Work/i.test(label)) docs.geotag={status:a?clean(a.innerText):cells[2],href:a?a.href:''};
          }
        }
      }
      return {fields,docs};
    }""")


def before_stage_status(page):
    """Read only the Before stage; overall document availability is not enough."""
    result = page.locator("#ContentPlaceHolder1_gvwdisplay").evaluate("""table => {
      if(!table) return {text:document.body.innerText,rows:[],images:[]};
      const clean=s=>(s||'').replace(/\\s+/g,' ').trim();
      const rows=Array.from(table.rows).map(r=>({text:clean(r.innerText),cells:Array.from(r.cells).map(c=>({text:clean(c.innerText),images:Array.from(c.querySelectorAll('img')).map(i=>({src:i.src,alt:i.alt,title:i.title})),links:Array.from(c.querySelectorAll('a[href]')).map(a=>({text:clean(a.innerText),href:a.href}))}))}));
      return {text:clean(table.innerText),rows,images:Array.from(table.querySelectorAll('img')).map(i=>({src:i.src,alt:i.alt,title:i.title}))};
    }""")
    text = clean(result.get("text"))
    if re.search(r"not available", text, re.I):
        return "Not Available"
    rows = result.get("rows", [])
    # Prefer an explicitly labelled Before row/cell when the portal supplies one.
    for row in rows:
        cells = row.get("cells", [])
        for i, cell in enumerate(cells):
            if re.search(r"\\bbefore\\b|पूर्व", cell.get("text", ""), re.I):
                has_media = bool(cell.get("images") or cell.get("links"))
                if not has_media and i + 1 < len(cells):
                    has_media = bool(cells[i + 1].get("images") or cells[i + 1].get("links"))
                return "Available" if has_media else "Not Available"
    # Some portal versions put stage labels in the preceding row and photos beneath.
    for i, row in enumerate(rows):
        if re.search(r"\\bbefore\\b|पूर्व", row.get("text", ""), re.I):
            if i + 1 < len(rows):
                next_row = rows[i + 1]
                if any(c.get("images") or c.get("links") for c in next_row.get("cells", [])):
                    return "Available"
            return "Not Available"
    return "Unknown"


def extract_as_sanction_date(page, expected_code):
    """Read the sanction date from the official AS document listing."""
    return page.locator("table").evaluate_all("""tables => {
      const clean=s=>(s||'').replace(/\\s+/g,' ').trim();
      for(const table of tables){
        const rows=Array.from(table.rows).filter(r=>r.closest('table')===table);
        const header=rows.map(r=>Array.from(r.cells).map(c=>clean(c.innerText)));
        const hi=header.findIndex(c=>c.some(x=>/Work Code/i.test(x))&&c.some(x=>/Sanction Date/i.test(x)));
        if(hi<0) continue;
        const h=header[hi].map(x=>x.toLowerCase());
        const codeIx=h.findIndex(x=>/work code/i.test(x)), dateIx=h.findIndex(x=>/sanction date/i.test(x));
        for(const row of rows.slice(hi+1)){
          const cells=Array.from(row.cells).map(c=>clean(c.innerText));
          if(cells[codeIx]===expected_code) return cells[dateIx]||'';
        }
      }
      return '';
    }""")


def setup_search(page, block):
    page.goto(SEARCH_URL, wait_until="networkidle", timeout=90000)
    page.wait_for_timeout(1000)
    if not page.locator("#ContentPlaceHolder1_ddl_state").count():
        title = page.title()
        body = clean(page.locator("body").inner_text())[:1200]
        raise RuntimeError(f"Search form missing for {block}; title={title!r}; url={page.url!r}; body={body!r}")
    for selector, label in (("#ContentPlaceHolder1_ddl_state", "MADHYA PRADESH"),
                            ("#ContentPlaceHolder1_ddl_dist", "SATNA"),
                            ("#ContentPlaceHolder1_ddl_blk", block),
                            ("#ContentPlaceHolder1_ddlFin_year", FY)):
        page.locator(selector).select_option(label=label, timeout=30000)
        page.wait_for_timeout(900)
    page.locator("#ContentPlaceHolder1_Button1").click(timeout=30000)
    page.wait_for_timeout(1200)


def main():
    from playwright.sync_api import sync_playwright
    fetched_at = datetime.now(timezone.utc).isoformat()
    rows = []
    excluded = {"notYD": 0, "wrongFY": 0, "detailErrors": 0, "noAS": 0, "beforeCutoff": 0}
    candidates = 0
    with sync_playwright() as p:
        try: browser = p.chromium.launch(channel="chrome", headless=True)
        except Exception: browser = p.chromium.launch(headless=True)
        try:
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
                extra_http_headers={"Cache-Control":"no-cache", "Pragma":"no-cache"})
            from vbgram_access import session_cookies
            cookies = session_cookies()
            if cookies: context.add_cookies(cookies)
            search, detail, gallery = context.new_page(), context.new_page(), context.new_page()
            for block in BLOCKS:
                print("Search " + block, flush=True)
                setup_search(search, block)
                works = extract_work_rows(search)
                print("  official rows: " + str(len(works)), flush=True)
                for work in works:
                    if work["fy"] != FY:
                        excluded["wrongFY"] += 1; continue
                    if not re.search(r"(?:^|/)YD(?:/|$)", clean(work["code"]), re.I):
                        excluded["notYD"] += 1; continue
                    candidates += 1
                    url = safe_href(search.url, work["href"])
                    try:
                        detail.goto(url, wait_until="domcontentloaded", timeout=90000)
                        parsed = extract_detail(detail)
                        fields, docs = parsed["fields"], parsed["docs"]
                        header = clean(detail.locator("#ContentPlaceHolder1_lbl_head").inner_text())
                        panchayat_match = re.search(r"Panchayat\s*:\s*(.+)$", header, re.I)
                        code = clean(fields.get("Work Code:", work["code"]))
                        if not re.search(r"(?:^|/)YD(?:/|$)", code, re.I):
                            excluded["notYD"] += 1; continue
                        start_date = parse_date(fields.get("Work Start Date(DD/MM/YYYY):", ""))
                        as_doc = docs.get("as", {})
                        if norm(as_doc.get("status")) != "available" or not as_doc.get("href"):
                            excluded["noAS"] += 1; continue
                        gallery.goto(safe_href(detail.url, as_doc["href"]), wait_until="domcontentloaded", timeout=90000)
                        sanction_date = parse_date(extract_as_sanction_date(gallery, code))
                        if not sanction_date or sanction_date < DATE_FROM:
                            excluded["beforeCutoff"] += 1; continue
                        geo_doc = docs.get("geotag", {})
                        stage_status = "Not Available"
                        if norm(geo_doc.get("status")) == "available" and geo_doc.get("href"):
                            gallery.goto(safe_href(detail.url, geo_doc["href"]), wait_until="domcontentloaded", timeout=90000)
                            stage_status = before_stage_status(gallery)
                        elif norm(geo_doc.get("status")) not in ("not available", "unavailable"):
                            stage_status = "Unknown"
                        rows.append({
                            "district": "MAIHAR" if block in MAIHAR_BLOCKS else "SATNA",
                            "block": block,
                            "panchayat": clean(fields.get("Panchayat :", panchayat_match.group(1) if panchayat_match else "")),
                            "financialYear": FY,
                            "workCode": code,
                            "workName": clean(fields.get("Work Name:", work["name"])),
                            "workStatus": clean(fields.get("Work Status:", work["status"])),
                            "workStartDate": start_date.isoformat() if start_date else "",
                            "asSanctionDate": sanction_date.isoformat(),
                            "asStatus": "Available",
                            "beforePhotoStatus": stage_status,
                            "source": url,
                        })
                    except Exception as error:
                        excluded["detailErrors"] += 1
                        print("  detail failed for " + work["code"] + ": " + str(error)[:180], flush=True)
                    if candidates % 20 == 0: print("  checked YD candidates: " + str(candidates), flush=True)
                    time.sleep(0.12)
            search.close(); detail.close(); gallery.close()
        finally: browser.close()

    if excluded["detailErrors"]:
        raise RuntimeError(f"{excluded['detailErrors']} detail pages failed; previous complete snapshot retained")
    rows.sort(key=lambda r: (r["district"], r["block"], r["panchayat"], r["workCode"]))
    yes = sum(r["beforePhotoStatus"] == "Available" for r in rows)
    no = sum(r["beforePhotoStatus"] == "Not Available" for r in rows)
    data = {
        "title": "AS स्वीकृत Yuktdhara कार्यों की Before Geotag स्थिति",
        "financialYear": FY, "dateFrom": DATE_FROM.isoformat(), "workCodePattern": "/YD/",
        "stage": "before", "fetchedAt": fetched_at, "source": SEARCH_URL,
        "candidateCount": candidates, "asAvailableCount": len(rows),
        "beforePhotoAvailable": yes, "beforePhotoNotAvailable": no,
        "beforePhotoUnknown": sum(r["beforePhotoStatus"] == "Unknown" for r in rows),
        "excluded": excluded, "rows": rows,
    }
    (ROOT / "data").mkdir(exist_ok=True)
    (ROOT / "data" / "as-geotag-before-latest.json").write_text(json.dumps(data, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    (ROOT / "as-geotag-before-data.js").write_text("window.AS_GEOTAG_BEFORE="+json.dumps(data, ensure_ascii=False, separators=(",",":"))+";\n", encoding="utf-8")
    patch_index()
    print("SUCCESS before-stage counts: AS="+str(len(rows))+", available="+str(yes)+", not available="+str(no)+", unknown="+str(data["beforePhotoUnknown"]), flush=True)


def patch_index():
    path = ROOT / "index.html"
    source = path.read_text(encoding="utf-8")
    href = "as-geotag-before.html?v=20261103-r39-before"
    if href in source: return
    pattern = re.compile(r'(<a class="srdm-app-card srdm-portal-card" href="yuktdhara-r33-1\.html[^\"]*"[^>]*>.*?</a>)', re.S)
    card = ('\n    <a class="srdm-app-card srdm-portal-card" href="'+href+'" style="text-decoration:none;--app-accent:#176da7">'
            '<span class="srdm-app-icon">📍</span><span class="srdm-app-copy"><strong>AS स्वीकृत Yuktdhara कार्यों की Before Geotag स्थिति</strong>'
            '<span>FY 2026-27 • 01-10-2026 से • Work Code /YD/ • केवल stages-before फोटो</span></span><span class="srdm-app-new">New</span></a>')
    updated, count = pattern.subn(lambda m: m.group(1)+card, source, count=1)
    if count != 1: raise RuntimeError("R-3 Yuktdhara menu insertion point not found; index.html left untouched")
    path.write_text(updated, encoding="utf-8")


if __name__ == "__main__":
    try: main()
    except Exception as error:
        print("FAILED AS-before-Geotag fetch; previous data retained: "+str(error), file=sys.stderr, flush=True)
        sys.exit(1)
