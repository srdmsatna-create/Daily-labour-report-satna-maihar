from pathlib import Path
import shutil

REPO=Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
P=REPO/"index.html"
if not P.exists(): raise SystemExit("index.html not found")
B=REPO/"index.before_DIRECT_FINAL_FIX_V2.bak.html"
if not B.exists(): shutil.copy2(P,B)
s=P.read_text(encoding="utf-8")
MARK="SRDM_DIRECT_FINAL_FIX_V2_01_09_2026"

if 'id="excelBtn"' not in s:
    old='<button id="csvBtn">CSV Export</button>'
    if old not in s: raise RuntimeError("CSV Export button anchor not found")
    s=s.replace(old,old+'\n    <button id="excelBtn" class="excel-btn">Excel Download</button>',1)

s=s.replace('<option value="portrait">Portrait</option><option value="landscape" selected>Landscape</option>',
            '<option value="portrait" selected>Portrait</option><option value="landscape">Landscape</option>')
s=s.replace("if(o){o.value='landscape';o.dispatchEvent(new Event('change'));}",
            "if(o){o.value='portrait';o.dispatchEvent(new Event('change'));}")
s=s.replace("let fontScale=1;","let fontScale=1.18;",1)

oldrec="""if(total)n=recoverySource().length;else{const scope={};if(iJan>=0&&td[iJan])scope.janpad=clean(td[iJan].textContent);if(iEng>=0&&td[iEng])scope.engineer=clean(td[iEng].textContent);if(iCl>=0&&td[iCl])scope.cluster=clean(td[iCl].textContent);if(iGp>=0&&td[iGp])scope.gp=clean(td[iGp].textContent);if(iCode>=0&&td[iCode])scope.code=clean(td[iCode].textContent);if(iCat>=0&&td[iCat])scope.category=clean(td[iCat].textContent);if(iDist>=0&&td[iDist])scope.district=clean(td[iDist].textContent);n=recoveryCountForScope(scope)}"""
newrec="""if(total)n=recoverySource().length;else{const scope={};if(iJan>=0&&td[iJan])scope.janpad=clean(td[iJan].textContent);if(!scope.janpad){const known=['AMARPATAN','MAIHAR','MAJHGAWAN','NAGOD','RAMNAGAR','RAMPUR BAGHELAN','SATNA','UNCHAHARA'];for(const c of td){const v=String(clean(c.textContent)||'').trim().toUpperCase();if(known.includes(v)){scope.janpad=v;break;}}}if(iEng>=0&&td[iEng])scope.engineer=clean(td[iEng].textContent);if(iCl>=0&&td[iCl])scope.cluster=clean(td[iCl].textContent);if(iGp>=0&&td[iGp])scope.gp=clean(td[iGp].textContent);if(iCode>=0&&td[iCode])scope.code=clean(td[iCode].textContent);if(iCat>=0&&td[iCat])scope.category=clean(td[iCat].textContent);if(iDist>=0&&td[iDist])scope.district=clean(td[iDist].textContent);n=recoveryCountForScope(scope)}"""
if oldrec in s: s=s.replace(oldrec,newrec,1)

if MARK not in s:
    css="""
<style id="srdmDirectFinalV2Style">
/* SRDM_DIRECT_FINAL_FIX_V2_01_09_2026 */
.excel-btn{background:#147a4a!important;color:#fff!important;border-color:#147a4a!important;font-weight:900!important}
.report-table th,.report-table td{font-size:calc(11.2px * var(--table-font-scale))!important;line-height:1.30!important;padding:5px 4px!important}
.report-table th{font-weight:900!important}
@media print{@page{size:A4 portrait!important;margin:8mm!important}}
</style>
"""
    if "</head>" not in s: raise RuntimeError("</head> not found")
    s=s.replace("</head>",css+"\n</head>",1)

    js=r"""
<script id="srdmDirectFinalV2Script">
/* SRDM_DIRECT_FINAL_FIX_V2_01_09_2026 */
(function(){
  const REC={AMARPATAN:61,MAIHAR:41,MAJHGAWAN:51,NAGOD:155,RAMNAGAR:67,'RAMPUR BAGHELAN':44,SATNA:59,UNCHAHARA:71};
  const esc=v=>String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  const n=v=>{const x=Number(v)||0;return Number.isInteger(x)?x.toLocaleString('en-IN'):x.toLocaleString('en-IN',{maximumFractionDigits:2})};
  const pc=(a,b)=>Number(b)?((Number(a)||0)*100/Number(b)).toFixed(1)+'%':'0.0%';
  const cv=()=>{try{return view||''}catch(e){return ''}};
  const cr=()=>{try{return Array.isArray(lastExport)?lastExport:[]}catch(e){return []}};
  const dist=j=>{try{return districtOf(j)}catch(e){return ''}};

  function excelDownload(){
    const table=document.getElementById('reportTable');if(!table)return;
    const title=document.getElementById('viewTitle')?.textContent||'VBGRAMG Report';
    const meta=document.getElementById('viewMeta')?.textContent||'';
    const html='<!doctype html><html><head><meta charset="utf-8"><style>'+
      'body{font-family:Arial,sans-serif}h2{color:#0b3159;font-size:16px}table{border-collapse:collapse;width:100%;font-size:11px}'+
      'th,td{border:1px solid #7d9bb9;padding:5px}th{background:#cfe0f5;color:#0a3158;font-weight:800}</style></head><body>'+
      '<h2>'+esc(title)+'</h2><p>'+esc(meta)+'</p>'+table.outerHTML+'</body></html>';
    const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\ufeff',html],{type:'application/vnd.ms-excel;charset=utf-8'}));
    a.download='VBGRAMG-'+(cv()||'report')+'-'+new Date().toISOString().slice(0,10)+'.xls';
    document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),500);
  }

  function tbl(h,rows){return '<table><thead><tr>'+h.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+
      rows.map(r=>'<tr>'+r.map(x=>'<td>'+esc(x)+'</td>').join('')+'</tr>').join('')+'</tbody></table>'}

  function officialPrint(){
    const data=cr(),v=cv(),eng=v==='engineer';if(!data.length)return null;
    const preH=eng?['District','Janpad','Sub Engineer','Cluster']:['District','Janpad'];
    const A=preH.concat(['Total GP','GP Progress','Dysfunctional','Labour','Works with MR','Total Ongoing','Muster Rolls','MR %','Individual Labour','Individual Works MR']);
    const B=preH.concat(['Community Labour','Community Works MR','Share %','PMAY-G Ongoing','PMAY-G MR Issued','PMAY MR %','Ek Bagiya Labour','Ek Bagiya Ongoing','Ek Bagiya MR Issued','Ek Bagiya MR %','Recovery']);
    const prefix=r=>eng?[r.district||dist(r.janpad),r.janpad,r.engineer||'',r.cluster||'']:[dist(r.janpad),r.janpad];
    const AR=data.map(r=>prefix(r).concat([n(r.totalGP),n(r.musterGP),n(r.dysfunctionalGP),n(r.labourAll),n(r.mrAll),n(r.ongoingAll),n(r.mrs),pc(r.mrAll,r.ongoingAll),n(r.labourIndividual),n(r.mrIndividual)]));
    const BR=data.map(r=>prefix(r).concat([n(r.labourCommunity),n(r.mrCommunity),pc(r.mrCommunity,r.mrAll),n(r.pmayOngoing),n(r.pmayMR),pc(r.pmayMR,r.pmayOngoing),n(r.ekLabour),n(r.ekOngoing),n(r.ekMR),pc(r.ekMR,r.ekOngoing),REC[String(r.janpad||'').trim().toUpperCase()]??'']));
    const title=document.getElementById('viewTitle')?.textContent||'Official Janpad Daily Report';
    const meta=document.getElementById('viewMeta')?.textContent||'';
    return '<!doctype html><html><head><meta charset="utf-8"><style>@page{size:A4 portrait;margin:8mm}body{font-family:Arial,sans-serif;color:#132238;margin:0}'+
      'h1{font-size:18px;color:#0b3159;margin:0}.meta{font-size:10px;color:#64748b;margin:3px 0 9px}h2{font-size:13px;color:#0b3159}.page{page-break-after:always}.page:last-child{page-break-after:auto}'+
      'table{width:100%;border-collapse:collapse;table-layout:fixed;font-size:8.5px}th,td{border:1px solid #7596b8;padding:3px 2px;text-align:center;word-break:break-word}th{background:#cfe0f5;color:#0a3158;font-weight:800}</style></head><body>'+
      '<section class="page"><h1>'+esc(title)+'</h1><div class="meta">'+esc(meta)+' • Portrait</div><h2>Part A — GP / Screen-2 / Individual Land</h2>'+tbl(A,AR)+'</section>'+
      '<section class="page"><h1>'+esc(title)+'</h1><div class="meta">'+esc(meta)+' • Portrait</div><h2>Part B — Community / PMAY-G / Ek Bagiya / Recovery</h2>'+tbl(B,BR)+'</section></body></html>';
  }

  function printPortrait(){
    let html=null;const v=cv();if(v==='official'||v==='engineer')html=officialPrint();
    if(!html){
      const table=document.getElementById('reportTable');if(!table)return;
      const title=document.getElementById('viewTitle')?.textContent||'VBGRAMG Report';
      const meta=document.getElementById('viewMeta')?.textContent||'';
      html='<!doctype html><html><head><meta charset="utf-8"><style>@page{size:A4 portrait;margin:8mm}body{font-family:Arial,sans-serif}table{width:100%;border-collapse:collapse;font-size:9px}th,td{border:1px solid #7596b8;padding:4px;text-align:center;word-break:break-word}th{background:#cfe0f5}</style></head><body><h1>'+
        esc(title)+'</h1><div>'+esc(meta)+'</div>'+table.outerHTML+'</body></html>';
    }
    const w=window.open('','_blank','width=900,height=1000');if(!w){alert('Print popup blocked है।');return;}
    w.document.open();w.document.write(html);w.document.close();w.focus();setTimeout(()=>w.print(),300);
  }

  document.getElementById('excelBtn')?.addEventListener('click',excelDownload);
  const old=document.getElementById('printBtn');if(old){const b=old.cloneNode(true);old.parentNode.replaceChild(b,old);b.addEventListener('click',printPortrait);}
  const orient=document.getElementById('printOrientation');if(orient){orient.value='portrait';orient.disabled=true;orient.title='A4 Portrait fixed';}
  document.documentElement.style.setProperty('--table-font-scale','1.18');
})();
</script>
"""
    if "</body>" not in s: raise RuntimeError("</body> not found")
    s=s.replace("</body>",js+"\n</body>",1)

P.write_text(s,encoding="utf-8")
print("INDEX PATCH OK")
