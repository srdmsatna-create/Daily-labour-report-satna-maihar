from pathlib import Path
import shutil

REPO = Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
P = REPO / "index.html"

if not P.exists():
    raise SystemExit("index.html not found")

B = REPO / "index.before_PRINT_BOTH_ORIENTATION_FIX.bak.html"
if not B.exists():
    shutil.copy2(P, B)

s = P.read_text(encoding="utf-8")
MARK = "SRDM_PRINT_BOTH_ORIENTATION_PDF_FIT_01_09_2026"

# Keep both Portrait and Landscape options available.
s = s.replace(
    '<option value="portrait" selected>Portrait</option><option value="landscape">Landscape</option>',
    '<option value="portrait">Portrait</option><option value="landscape" selected>Landscape</option>'
)

# Undo previous forced/disabled portrait snippets if present.
s = s.replace(
    "if(orient){orient.value='portrait';orient.disabled=true;orient.title='A4 Portrait fixed';}",
    "if(orient){orient.disabled=false;orient.title='Portrait या Landscape चुनें';}"
)
s = s.replace(
    "if(orient){orient.value='portrait';orient.disabled=true;orient.title='Print fixed to A4 Portrait';}",
    "if(orient){orient.disabled=false;orient.title='Portrait या Landscape चुनें';}"
)

if MARK not in s:
    css = '''
<style id="srdmPrintBothOrientationStyle">
/* SRDM_PRINT_BOTH_ORIENTATION_PDF_FIT_01_09_2026 */
#printOrientation{
  min-width:112px!important;
  font-weight:850!important;
  color:#123b69!important;
  background:#fff!important;
}
@media print{
  html,body{overflow:visible!important}
  .table-wrap,.report-wrap,.report-card{overflow:visible!important}
}
</style>
'''
    if "</head>" not in s:
        raise RuntimeError("</head> not found")
    s = s.replace("</head>", css + "\n</head>", 1)

    js = r'''
<script id="srdmPrintBothOrientationScript">
/* SRDM_PRINT_BOTH_ORIENTATION_PDF_FIT_01_09_2026 */
(function(){
  const $id=id=>document.getElementById(id);
  const esc=v=>String(v??'')
    .replace(/&/g,'&amp;').replace(/</g,'&lt;')
    .replace(/>/g,'&gt;').replace(/"/g,'&quot;');

  function currentView(){ try{return view||''}catch(e){return ''} }
  function currentRows(){ try{return Array.isArray(lastExport)?lastExport:[]}catch(e){return []} }
  function district(j){ try{return districtOf(j)}catch(e){return ''} }
  function num(v){
    const n=Number(v)||0;
    return Number.isInteger(n)?n.toLocaleString('en-IN'):n.toLocaleString('en-IN',{maximumFractionDigits:2});
  }
  function pct(a,b){
    return Number(b)?((Number(a)||0)*100/Number(b)).toFixed(1)+'%':'0.0%';
  }
  function makeTable(headers,rows,fontSize){
    return `<table style="font-size:${fontSize}px"><thead><tr>${headers.map(x=>`<th>${esc(x)}</th>`).join('')}</tr></thead><tbody>${rows.map(r=>`<tr>${r.map(x=>`<td>${esc(x)}</td>`).join('')}</tr>`).join('')}</tbody></table>`;
  }

  function portraitOfficialHtml(){
    const data=currentRows(), v=currentView();
    if(!data.length)return null;
    const engineer=v==='engineer';
    const preH=engineer?['District','Janpad','Sub Engineer','Cluster']:['District','Janpad'];
    const prefix=r=>engineer
      ? [r.district||district(r.janpad),r.janpad,r.engineer||'',r.cluster||'']
      : [district(r.janpad),r.janpad];

    const REC={AMARPATAN:61,MAIHAR:41,MAJHGAWAN:51,NAGOD:155,RAMNAGAR:67,'RAMPUR BAGHELAN':44,SATNA:59,UNCHAHARA:71};

    const hA=preH.concat(['Total GP','GP Progress','Dysfunctional','Labour','Works with MR','Total Ongoing','Muster Rolls','MR %','Individual Labour','Individual Works MR']);
    const rowsA=data.map(r=>prefix(r).concat([
      num(r.totalGP),num(r.musterGP),num(r.dysfunctionalGP),
      num(r.labourAll),num(r.mrAll),num(r.ongoingAll),num(r.mrs),
      pct(r.mrAll,r.ongoingAll),num(r.labourIndividual),num(r.mrIndividual)
    ]));

    const hB=preH.concat(['Community Labour','Community Works MR','Share %','PMAY-G Ongoing','PMAY-G MR Issued','PMAY MR %','Ek Bagiya Labour','Ek Bagiya Ongoing','Ek Bagiya MR Issued','Ek Bagiya MR %','Recovery']);
    const rowsB=data.map(r=>prefix(r).concat([
      num(r.labourCommunity),num(r.mrCommunity),pct(r.mrCommunity,r.mrAll),
      num(r.pmayOngoing),num(r.pmayMR),pct(r.pmayMR,r.pmayOngoing),
      num(r.ekLabour),num(r.ekOngoing),num(r.ekMR),pct(r.ekMR,r.ekOngoing),
      REC[String(r.janpad||'').trim().toUpperCase()]??''
    ]));

    const title=$id('viewTitle')?.textContent||'Official Janpad Daily Report';
    const meta=$id('viewMeta')?.textContent||'';

    return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title>
    <style>
      @page{size:A4 portrait;margin:8mm}
      *{box-sizing:border-box}
      body{font-family:Arial,'Noto Sans Devanagari',sans-serif;color:#132238;margin:0}
      h1{font-size:18px;margin:0;color:#0b3159}
      .meta{font-size:10px;color:#64748b;margin:3px 0 10px}
      h2{font-size:13px;color:#0b3159;margin:0 0 6px}
      .page{page-break-after:always}.page:last-child{page-break-after:auto}
      table{width:100%;border-collapse:collapse;table-layout:fixed}
      th,td{border:1px solid #7596b8;padding:3px 2px;text-align:center;vertical-align:middle;word-break:break-word}
      th{background:#cfe0f5;color:#0a3158;font-weight:800}
      tbody tr:nth-child(even){background:#f5f8fc}
    </style></head><body>
      <section class="page"><h1>${esc(title)}</h1><div class="meta">${esc(meta)} • A4 Portrait • Part A</div><h2>GP / Screen-2 / Individual Land</h2>${makeTable(hA,rowsA,8.5)}</section>
      <section class="page"><h1>${esc(title)}</h1><div class="meta">${esc(meta)} • A4 Portrait • Part B</div><h2>Community / PMAY-G / Ek Bagiya / Recovery</h2>${makeTable(hB,rowsB,8.5)}</section>
    </body></html>`;
  }

  function genericHtml(mode){
    const table=$id('reportTable');
    if(!table)return null;
    const title=$id('viewTitle')?.textContent||'VBGRAMG Report';
    const meta=$id('viewMeta')?.textContent||'';
    const isLandscape=mode==='landscape';
    const wide=(currentView()==='official'||currentView()==='engineer');
    const font=isLandscape?(wide?7.3:8.8):(wide?6.4:8.8);
    const pageSize=isLandscape?'A4 landscape':'A4 portrait';

    return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title>
    <style>
      @page{size:${pageSize};margin:7mm}
      *{box-sizing:border-box}
      body{font-family:Arial,'Noto Sans Devanagari',sans-serif;color:#132238;margin:0}
      h1{font-size:18px;color:#0b3159;margin:0}
      .meta{font-size:10px;color:#64748b;margin:3px 0 10px}
      .print-box{width:100%;overflow:visible}
      table{width:100%!important;min-width:0!important;border-collapse:collapse!important;table-layout:fixed!important;font-size:${font}px!important}
      th,td{border:1px solid #7596b8!important;padding:2.6px 2px!important;text-align:center!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:break-word!important;line-height:1.18!important}
      th{background:#cfe0f5!important;color:#0a3158!important;font-weight:800!important}
      .badge{font-size:inherit!important;padding:1px 3px!important}
    </style></head><body>
      <h1>${esc(title)}</h1>
      <div class="meta">${esc(meta)} • ${isLandscape?'A4 Landscape':'A4 Portrait'}</div>
      <div class="print-box">${table.outerHTML}</div>
    </body></html>`;
  }

  function doPrint(){
    const orientation=$id('printOrientation')?.value==='portrait'?'portrait':'landscape';
    const v=currentView();
    let html=null;

    if(orientation==='portrait' && (v==='official'||v==='engineer')){
      html=portraitOfficialHtml();
    }
    if(!html)html=genericHtml(orientation);
    if(!html)return;

    const w=window.open('','_blank','width=1100,height=900');
    if(!w){alert('Print popup blocked है। Browser में pop-up allow करें।');return;}
    w.document.open();w.document.write(html);w.document.close();w.focus();
    setTimeout(()=>w.print(),350);
  }

  const orient=$id('printOrientation');
  if(orient){
    orient.disabled=false;
    orient.title='Portrait या Landscape चुनें';
    if(!['portrait','landscape'].includes(orient.value))orient.value='landscape';
  }

  const old=$id('printBtn');
  if(old){
    const b=old.cloneNode(true);
    old.parentNode.replaceChild(b,old);
    b.textContent='Print / PDF';
    b.addEventListener('click',doPrint);
  }
})();
</script>
'''
    if "</body>" not in s:
        raise RuntimeError("</body> not found")
    s = s.replace("</body>", js + "\n</body>", 1)

P.write_text(s,encoding="utf-8")
print("PRINT BOTH ORIENTATION PATCH OK")
