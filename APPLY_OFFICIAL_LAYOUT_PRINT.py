from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start='<!-- ===== OFFICIAL LAYOUT PRINT V2 ===== -->'
end='<!-- ===== END OFFICIAL LAYOUT PRINT V2 ===== -->'
if start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+s[b:]

block=r'''
<!-- ===== OFFICIAL LAYOUT PRINT V2 ===== -->
<style>
body[data-report-view="official"] .report-card,
body[data-report-view="official"] .report-head,
body[data-report-view="official"] #reportTable,
body[data-report-view="official"] #reportTable th,
body[data-report-view="official"] #reportTable td{
  font-family:"Times New Roman", Times, serif!important;
}
body[data-report-view="official"] .table-wrap{width:100%!important;max-width:100%!important;overflow-x:auto!important;border-radius:8px!important}
body[data-report-view="official"] #reportTable{border-collapse:collapse!important;min-width:1180px!important;width:100%!important;table-layout:auto!important}
body[data-report-view="official"] #reportTable th{font-size:14px!important;font-weight:700!important;padding:5px 3px!important;line-height:1.08!important;white-space:normal!important;word-break:normal!important;text-align:center!important}
body[data-report-view="official"] #reportTable td{font-size:19px!important;font-weight:700!important;padding:5px 3px!important;line-height:1.06!important;white-space:normal!important;word-break:normal!important}
body[data-report-view="official"] #reportTable th,body[data-report-view="official"] #reportTable td{border:1.3px solid #6489a3!important;vertical-align:middle!important;min-width:40px!important}
body[data-report-view="official"] #reportTable th:nth-child(1),body[data-report-view="official"] #reportTable td:nth-child(1){min-width:58px!important;width:58px!important;white-space:nowrap!important}
body[data-report-view="official"] #reportTable th:nth-child(2),body[data-report-view="official"] #reportTable td:nth-child(2){min-width:102px!important;width:102px!important;white-space:normal!important}
body[data-report-view="official"] #reportTable th:nth-child(3),body[data-report-view="official"] #reportTable td:nth-child(3){min-width:82px!important;width:82px!important}
body[data-report-view="official"] #reportTable th:nth-child(4),body[data-report-view="official"] #reportTable td:nth-child(4){min-width:62px!important;width:62px!important}
body[data-report-view="official"] #reportTable th:nth-child(n+5),body[data-report-view="official"] #reportTable td:nth-child(n+5){min-width:46px!important}
body[data-report-view="official"] #reportTable th:last-child,body[data-report-view="official"] #reportTable td:last-child{min-width:54px!important;width:54px!important;max-width:54px!important}
body[data-report-view="official"] #reportTable tbody tr.total-row td{font-size:19px!important;font-weight:700!important}
@media(max-width:900px){body[data-report-view="official"] #reportTable{min-width:1160px!important}body[data-report-view="official"] #reportTable th{font-size:13px!important}body[data-report-view="official"] #reportTable td{font-size:18px!important}}
</style>
<script>
(function(){
  const txt=e=>String(e?.textContent||'').replace(/\s+/g,' ').trim();
  const VASULI={'RAMPUR BAGHELAN':44,'MAIHAR':59,'NAGOD':155,'MAJHGAWAN':41,'UNCHAHARA':51,'AMARPATAN':71,'RAMNAGAR':61,'SATNA':67};

  function isOfficial(){
    try{ if(typeof view!=='undefined') return view==='official'; }catch(e){}
    return /Official Janpad Daily Report/i.test(txt(document.getElementById('viewTitle')));
  }

  function compactHeader(t){
    if(!t || !t.tHead || t.tHead.rows.length<2 || !t.tBodies.length) return;
    const h1=t.tHead.rows[0], h2=t.tHead.rows[1], body=t.tBodies[0];
    [...h1.cells].forEach(th=>{ if(/ALL TYPES OF WORKS/i.test(txt(th)) && txt(th)!=='All Types of Works') th.textContent='All Types of Works'; });
    const hs=[...h2.cells].map(x=>txt(x).toUpperCase());
    const totalIdx=hs.indexOf('TOTAL GP'), progIdx=hs.indexOf('GP PROGRESS');
    if(totalIdx>=0 && progIdx>=0){
      const grp=[...h1.cells].find(x=>txt(x).toUpperCase()==='GRAM PANCHAYAT');
      if(grp) grp.colSpan=Math.max(1,(parseInt(grp.colSpan||'3',10)-1));
      h2.cells[progIdx].textContent='GP Progress / Total GPs';
      h2.deleteCell(totalIdx);
      [...body.rows].forEach(tr=>{
        if(tr.cells.length<4) return;
        const total=txt(tr.cells[2]), prog=txt(tr.cells[3]);
        tr.cells[3].textContent=prog+' / '+total;
        tr.deleteCell(2);
      });
    }
  }

  function patchVasuli(t){
    if(!t || !t.tBodies || !t.tBodies.length) return;
    [...t.tBodies[0].rows].forEach(tr=>{
      if(!tr.cells.length) return;
      const vals=[...tr.cells].map(c=>txt(c).toUpperCase());
      const cell=tr.cells[tr.cells.length-1];
      const isTotal=tr.classList.contains('total-row')||vals.includes('TOTAL')||vals.includes('योग');
      if(isTotal){
        if(txt(cell)!=='549') cell.textContent='549';
        cell.style.cssText += ';background:#0f766e!important;color:#fff!important;font-weight:700!important';
        return;
      }
      const jp=txt(tr.cells[1]).toUpperCase();
      if(!Object.prototype.hasOwnProperty.call(VASULI,jp)) return;
      const v=String(VASULI[jp]);
      if(txt(cell)!==v) cell.textContent=v;
      cell.style.cssText += ';background:#dcfce7!important;color:#166534!important;font-weight:700!important';
    });
  }

  function run(){
    const official=isOfficial();
    if(document.body) document.body.dataset.reportView=official?'official':'';
    if(!official) return;
    const t=document.getElementById('reportTable');
    if(!t) return;
    compactHeader(t);
    patchVasuli(t);
  }

  function boot(){
    run();
    document.addEventListener('click',()=>setTimeout(run,80),true);
    document.addEventListener('change',()=>setTimeout(run,80),true);
    try{
      if(typeof render==='function' && !render.__srdmOfficialSafe){
        const baseRender=render;
        const wrapped=function(){const out=baseRender.apply(this,arguments);setTimeout(run,0);return out;};
        wrapped.__srdmOfficialSafe=true;
        render=wrapped;
      }
    }catch(e){}
  }

  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',boot); else boot();
})();
</script>
<!-- ===== END OFFICIAL LAYOUT PRINT V2 ===== -->
'''
if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: Stable Official Janpad patch applied; no MutationObserver loop')
