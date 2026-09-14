from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
orig=s

# 1) Remove every previously injected Official layout block. These accumulated over repeated patches.
start='<!-- ===== OFFICIAL LAYOUT PRINT V2 ===== -->'
end='<!-- ===== END OFFICIAL LAYOUT PRINT V2 ===== -->'
removed=0
while start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end)
    s=s[:a]+s[b:]
    removed+=1

# 2) Disable expensive page-wide observers from known helper patches.
repls = {
"new MutationObserver(()=>setTimeout(apply,60)).observe(document.body,{subtree:true,childList:true});":"/* disabled: page-wide observer caused report freeze */",
"new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true,characterData:true});":"/* disabled: page-wide district-average observer caused report freeze */",
"new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true});":"/* disabled: page-wide observer caused report freeze */",
}
observer_hits=0
for old,new in repls.items():
    c=s.count(old)
    if c:
        s=s.replace(old,new)
        observer_hits+=c

# 3) Add one lightweight Official Janpad presentation block: CSS only + click/change delayed formatting.
block=r'''
<!-- ===== OFFICIAL SAFE FAST V1 ===== -->
<style>
body[data-report-view="official"] .report-card,
body[data-report-view="official"] .report-head,
body[data-report-view="official"] #reportTable,
body[data-report-view="official"] #reportTable th,
body[data-report-view="official"] #reportTable td{font-family:"Times New Roman",Times,serif!important}
body[data-report-view="official"] #reportTable th{font-size:14px!important;font-weight:700!important;padding:5px 3px!important;line-height:1.08!important}
body[data-report-view="official"] #reportTable td{font-size:19px!important;font-weight:700!important;padding:5px 3px!important;line-height:1.06!important}
</style>
<script>
(function(){
 const txt=e=>String(e?.textContent||'').replace(/\s+/g,' ').trim();
 const V={'RAMPUR BAGHELAN':44,'MAIHAR':59,'NAGOD':155,'MAJHGAWAN':41,'UNCHAHARA':51,'AMARPATAN':71,'RAMNAGAR':61,'SATNA':67};
 function official(){try{return typeof view!=='undefined'&&view==='official'}catch(e){return /Official Janpad Daily Report/i.test(txt(document.getElementById('viewTitle')))}}
 function apply(){
   const ok=official(); if(document.body)document.body.dataset.reportView=ok?'official':''; if(!ok)return;
   const t=document.getElementById('reportTable'); if(!t||!t.tHead||!t.tBodies.length)return;
   const h1=t.tHead.rows[0],h2=t.tHead.rows[1];
   [...h1.cells].forEach(th=>{if(/ALL TYPES OF WORKS/i.test(txt(th)))th.textContent='All Types of Works'});
   if(h2){
     const hs=[...h2.cells].map(x=>txt(x).toUpperCase()),a=hs.indexOf('TOTAL GP'),b=hs.indexOf('GP PROGRESS');
     if(a>=0&&b>=0){
       const g=[...h1.cells].find(x=>txt(x).toUpperCase()==='GRAM PANCHAYAT'); if(g)g.colSpan=Math.max(1,(parseInt(g.colSpan||'3',10)-1));
       h2.cells[b].textContent='GP Progress / Total GPs'; h2.deleteCell(a);
       [...t.tBodies[0].rows].forEach(tr=>{if(tr.cells.length<4)return;const total=txt(tr.cells[2]),prog=txt(tr.cells[3]);tr.cells[3].textContent=prog+' / '+total;tr.deleteCell(2)});
     }
   }
   [...t.tBodies[0].rows].forEach(tr=>{
     if(!tr.cells.length)return; const vals=[...tr.cells].map(c=>txt(c).toUpperCase()),last=tr.cells[tr.cells.length-1];
     if(tr.classList.contains('total-row')||vals.includes('TOTAL')||vals.includes('योग')){last.textContent='549';return}
     const jp=txt(tr.cells[1]).toUpperCase(); if(Object.prototype.hasOwnProperty.call(V,jp))last.textContent=String(V[jp]);
   });
 }
 function schedule(){clearTimeout(window.__srdmFastTimer);window.__srdmFastTimer=setTimeout(apply,120)}
 if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',schedule);else schedule();
 document.addEventListener('click',schedule,true);document.addEventListener('change',schedule,true);
})();
</script>
<!-- ===== END OFFICIAL SAFE FAST V1 ===== -->
'''
# Remove duplicate safe block before adding one.
ss='<!-- ===== OFFICIAL SAFE FAST V1 ===== -->'; ee='<!-- ===== END OFFICIAL SAFE FAST V1 ===== -->'
while ss in s and ee in s:
    a=s.index(ss); b=s.index(ee,a)+len(ee); s=s[:a]+s[b:]
if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)

p.write_text(s,encoding='utf-8')
print(f'DONE: removed Official blocks={removed}; disabled page-wide observers={observer_hits}; size {len(orig)} -> {len(s)}')
