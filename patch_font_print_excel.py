from pathlib import Path
import shutil

REPO = Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
INDEX = REPO / "index.html"

if not INDEX.exists():
    raise SystemExit("index.html not found")

bak = REPO / "index.before_font_print_excel_fix.bak.html"
if not bak.exists():
    shutil.copy2(INDEX, bak)

s = INDEX.read_text(encoding="utf-8")
MARKER = "SRDM_FONT_PRINT_EXCEL_FIX_01_09_2026"

if 'id="excelBtn"' not in s:
    target = '<button id="csvBtn">CSV Export</button>'
    repl = target + '\n    <button id="excelBtn" class="excel-btn" title="Current report Excel में डाउनलोड करें">Excel Download</button>'
    if target not in s:
        raise RuntimeError("CSV Export button not found")
    s = s.replace(target, repl, 1)

s = s.replace(
    '<option value="portrait">Portrait</option><option value="landscape" selected>Landscape</option>',
    '<option value="portrait" selected>Portrait</option><option value="landscape">Landscape</option>',
    1
)

s = s.replace(
    "if(o){o.value='landscape';o.dispatchEvent(new Event('change'));}",
    "if(o){o.value='portrait';o.dispatchEvent(new Event('change'));}"
)

s = s.replace("let fontScale=1;", "let fontScale=1.15;", 1)

style = '''
<style id="srdmFontPrintExcelStyle">
/* SRDM_FONT_PRINT_EXCEL_FIX_01_09_2026 */
.excel-btn{
  background:#16794b!important;color:#fff!important;border-color:#16794b!important;
  font-weight:900!important;box-shadow:0 3px 10px rgba(22,121,75,.16)
}
.report-table th,.report-table td{
  font-size:calc(11px * var(--table-font-scale))!important;
  line-height:1.28!important;
}
body[data-report-view="official"] .official-grid th,
body[data-report-view="official"] .official-grid td{
  font-size:calc(10.6px * var(--table-font-scale))!important;
  padding:5px 4px!important;
}
body[data-report-view="engineer"] .engineer-grid th,
body[data-report-view="engineer"] .engineer-grid td{
  font-size:calc(10.2px * var(--table-font-scale))!important;
  padding:4px!important;
}
@media print{
  @page{size:A4 portrait!important;margin:8mm!important}
  .report-table th,.report-table td{
    font-size:8.5px!important;
    line-height:1.2!important;
    padding:3px!important;
    white-space:normal!important;
  }
}
</style>
'''
if MARKER not in s:
    if "</head>" not in s:
        raise RuntimeError("</head> not found")
    s = s.replace("</head>", style + "\n</head>", 1)

script = r'''
<script id="srdmFontPrintExcelScript">
/* SRDM_FONT_PRINT_EXCEL_FIX_01_09_2026 */
(function(){
  function esc(v){
    return String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;')
      .replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }

  function downloadCurrentExcel(){
    const table=document.getElementById('reportTable');
    if(!table){alert('Report table नहीं मिला।');return;}
    const title=(document.getElementById('viewTitle')?.textContent||'VBGRAMG Report').trim();
    const meta=(document.getElementById('viewMeta')?.textContent||'').trim();
    const clone=table.cloneNode(true);
    const html=`<!doctype html><html><head><meta charset="utf-8">
    <style>
      body{font-family:Arial,'Noto Sans Devanagari',sans-serif}
      h2{font-size:16px;margin:0 0 4px;color:#0b3159}
      p{font-size:10px;color:#64748b;margin:0 0 10px}
      table{border-collapse:collapse;width:100%;font-size:11px}
      th{background:#cfe0f5;color:#0a3158;font-weight:700;text-align:center}
      th,td{border:1px solid #7d9bb9;padding:5px;vertical-align:middle}
      tr:last-child td{font-weight:700;background:#d9e8f8}
    </style></head><body><h2>${esc(title)}</h2><p>${esc(meta)}</p>${clone.outerHTML}</body></html>`;
    const blob=new Blob(['\ufeff',html],{type:'application/vnd.ms-excel;charset=utf-8'});
    const a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download=`VBGRAMG-${String(window.view||'report')}-${new Date().toISOString().slice(0,10)}.xls`;
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(()=>URL.revokeObjectURL(a.href),500);
  }

  function rowsToTable(headers, rows){
    return `<table><thead><tr>${headers.map(x=>`<th>${esc(x)}</th>`).join('')}</tr></thead>
    <tbody>${rows.map(r=>`<tr>${r.map(x=>`<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  }

  function officialPortraitHtml(){
    const data=Array.isArray(window.lastExport)?window.lastExport:[];
    if(!data.length)return null;
    const fmtN=v=>{
      const n=Number(v)||0;
      return Number.isInteger(n)?n.toLocaleString('en-IN'):n.toLocaleString('en-IN',{maximumFractionDigits:2});
    };
    const pct=(a,b)=>b?((Number(a)||0)*100/(Number(b)||0)).toFixed(1)+'%':'0.0%';

    const isEngineer=(window.view==='engineer');
    const aHeaders=isEngineer
      ? ['District','Janpad','Sub Engineer','Cluster','Total GP','GP Progress','Dysfunctional','Labour','Works with MR','Total Ongoing','Muster Rolls','MR %','Individual Labour','Individual Works MR']
      : ['District','Janpad','Total GP','GP Progress','Dysfunctional','Labour','Works with MR','Total Ongoing','Muster Rolls','MR %','Individual Labour','Individual Works MR'];

    const aRows=data.map(r=>{
      const pre=isEngineer?[r.district||'',r.janpad||'',r.engineer||'',r.cluster||'']:[(typeof districtOf==='function'?districtOf(r.janpad):r.district||''),r.janpad||''];
      return [...pre,fmtN(r.totalGP),fmtN(r.musterGP),fmtN(r.dysfunctionalGP),fmtN(r.labourAll),fmtN(r.mrAll),fmtN(r.ongoingAll),fmtN(r.mrs),pct(r.mrAll,r.ongoingAll),fmtN(r.labourIndividual),fmtN(r.mrIndividual)];
    });

    const bHeaders=isEngineer
      ? ['District','Janpad','Sub Engineer','Cluster','Community Labour','Community Works MR','Share %','PMAY-G Ongoing','PMAY-G MR Issued','PMAY MR %','Ek Bagiya Labour','Ek Bagiya Ongoing','Ek Bagiya MR Issued','Ek Bagiya MR %','Recovery']
      : ['District','Janpad','Community Labour','Community Works MR','Share %','PMAY-G Ongoing','PMAY-G MR Issued','PMAY MR %','Ek Bagiya Labour','Ek Bagiya Ongoing','Ek Bagiya MR Issued','Ek Bagiya MR %','Recovery'];

    const recMap={AMARPATAN:61,MAIHAR:41,MAJHGAWAN:51,NAGOD:155,RAMNAGAR:67,'RAMPUR BAGHELAN':44,SATNA:59,UNCHAHARA:71};
    const bRows=data.map(r=>{
      const pre=isEngineer?[r.district||'',r.janpad||'',r.engineer||'',r.cluster||'']:[(typeof districtOf==='function'?districtOf(r.janpad):r.district||''),r.janpad||''];
      const rec=recMap[String(r.janpad||'').trim().toUpperCase()] ?? '';
      return [...pre,fmtN(r.labourCommunity),fmtN(r.mrCommunity),pct(r.mrCommunity,r.mrAll),fmtN(r.pmayOngoing),fmtN(r.pmayMR),pct(r.pmayMR,r.pmayOngoing),fmtN(r.ekLabour),fmtN(r.ekOngoing),fmtN(r.ekMR),pct(r.ekMR,r.ekOngoing),rec];
    });

    const title=(document.getElementById('viewTitle')?.textContent||'Official Janpad Daily Report');
    const meta=(document.getElementById('viewMeta')?.textContent||'');
    return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title>
    <style>
      @page{size:A4 portrait;margin:8mm}
      *{box-sizing:border-box}
      body{font-family:Arial,'Noto Sans Devanagari',sans-serif;color:#132238;margin:0}
      h1{font-size:18px;margin:0;color:#0b3159}
      .meta{font-size:10px;color:#64748b;margin:3px 0 10px}
      h2{font-size:13px;color:#0b3159;margin:0 0 6px}
      .page{page-break-after:always}
      .page:last-child{page-break-after:auto}
      table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:8.2px}
      th,td{border:1px solid #7596b8;padding:3.2px 2px;text-align:center;vertical-align:middle;word-break:break-word}
      th{background:#cfe0f5;color:#0a3158;font-weight:800}
      tbody tr:nth-child(even){background:#f5f8fc}
      @media print{body{margin:0}}
    </style></head><body>
      <section class="page"><h1>${esc(title)}</h1><div class="meta">${esc(meta)} • Portrait Print</div><h2>Part A — GP / Screen-2 / Individual Land</h2>${rowsToTable(aHeaders,aRows)}</section>
      <section class="page"><h1>${esc(title)}</h1><div class="meta">${esc(meta)} • Portrait Print</div><h2>Part B — Community / PMAY-G / Ek Bagiya / Recovery</h2>${rowsToTable(bHeaders,bRows)}</section>
    </body></html>`;
  }

  function printCurrentPortrait(){
    let html=null;
    if(window.view==='official'||window.view==='engineer') html=officialPortraitHtml();
    if(!html){
      const table=document.getElementById('reportTable');
      if(!table)return;
      const title=document.getElementById('viewTitle')?.textContent||'VBGRAMG Report';
      const meta=document.getElementById('viewMeta')?.textContent||'';
      html=`<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title>
      <style>@page{size:A4 portrait;margin:8mm}body{font-family:Arial,sans-serif;color:#132238}h1{font-size:18px;color:#0b3159;margin:0}.meta{font-size:10px;color:#64748b;margin:3px 0 10px}table{width:100%;border-collapse:collapse;font-size:9px}th,td{border:1px solid #7596b8;padding:4px;text-align:center;word-break:break-word}th{background:#cfe0f5;color:#0a3158}</style>
      </head><body><h1>${esc(title)}</h1><div class="meta">${esc(meta)}</div>${table.outerHTML}</body></html>`;
    }
    const w=window.open('','_blank','width=900,height=1000');
    if(!w){alert('Print window blocked है। Browser में pop-up allow करें।');return;}
    w.document.open();w.document.write(html);w.document.close();
    w.focus();
    setTimeout(()=>{w.print();},350);
  }

  const excel=document.getElementById('excelBtn');
  excel?.addEventListener('click',downloadCurrentExcel);

  const oldPrint=document.getElementById('printBtn');
  if(oldPrint){
    const p=oldPrint.cloneNode(true);
    oldPrint.parentNode.replaceChild(p,oldPrint);
    p.addEventListener('click',printCurrentPortrait);
  }

  const orient=document.getElementById('printOrientation');
  if(orient){orient.value='portrait';orient.disabled=true;orient.title='Print fixed to A4 Portrait';}

  document.documentElement.style.setProperty('--table-font-scale','1.15');
})();
</script>
'''
if 'id="srdmFontPrintExcelScript"' not in s:
    if "</body>" not in s:
        raise RuntimeError("</body> not found")
    s = s.replace("</body>", script + "\n</body>", 1)

INDEX.write_text(s, encoding="utf-8")
print("UI patch complete: larger font + portrait print + Excel download")
