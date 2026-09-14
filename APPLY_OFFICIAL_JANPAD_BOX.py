from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start='<!-- ===== OFFICIAL JANPAD BOX V1 ===== -->'
end='<!-- ===== END OFFICIAL JANPAD BOX V1 ===== -->'
if start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+s[b:]

block=r'''
<!-- ===== OFFICIAL JANPAD BOX V1 ===== -->
<style>
body[data-report-view="official"] #reportTable{border-collapse:collapse!important;table-layout:auto!important;min-width:980px!important;width:100%!important}
body[data-report-view="official"] #reportTable th,
body[data-report-view="official"] #reportTable td{border:1.5px solid #4f7f76!important;font-size:14px!important;line-height:1.2!important;padding:7px 7px!important;white-space:normal!important;vertical-align:middle!important}
body[data-report-view="official"] #reportTable thead th{font-size:14px!important;font-weight:900!important;text-align:center!important}
body[data-report-view="official"] #reportTable tbody td{font-weight:650!important}
body[data-report-view="official"] #reportTable .official-pmay-only,
body[data-report-view="official"] #reportTable .official-ek-only{background:#e9f6ef!important;font-weight:900!important;text-align:center!important;min-width:82px!important}
body[data-report-view="official"] .table-wrap{border:2px solid #356a60!important;border-radius:8px!important;overflow:auto!important}
</style>
<script>
(function(){
  function compactOfficial(){
    if(document.body.dataset.reportView!=='official') return;
    const t=document.getElementById('reportTable');
    if(!t||!t.tHead||!t.tBodies.length) return;
    const top=t.tHead.rows[0], sub=t.tHead.rows[1];
    if(!top||!sub) return;
    const topTexts=[...top.cells].map(c=>c.textContent.trim().toUpperCase());
    if(!topTexts.includes('PMAY-G')||!topTexts.some(x=>x.includes('EK BAGIYA'))) return;
    if(t.dataset.officialCompact==='1') return;

    // Original leaf columns are 0..21. Keep PMAY Ongoing (15) and Ek Bagiya Ongoing (19), remove other PMAY/Ek columns.
    const remove=[21,20,18,17,16];
    for(const row of [...t.tBodies[0].rows]){
      for(const i of remove){ if(row.cells[i]) row.deleteCell(i); }
    }

    // Rebuild second header row after removing PMAY MR/MR% and Ek Labour/MR/MR%.
    for(const i of [19,18,17,16,15]){ if(sub.cells[i]) sub.deleteCell(i); }
    const pm=document.createElement('th'); pm.textContent='Ongoing'; pm.className='official-pmay-only';
    const ek=document.createElement('th'); ek.textContent='Ongoing'; ek.className='official-ek-only';
    sub.appendChild(pm); sub.appendChild(ek);

    // Top header groups: PMAY-G and Ek Bagiya become single boxed columns.
    const topCells=[...top.cells];
    const pmTop=topCells.find(c=>c.textContent.trim().toUpperCase()==='PMAY-G');
    const ekTop=topCells.find(c=>c.textContent.trim().toUpperCase().includes('EK BAGIYA'));
    if(pmTop){pmTop.colSpan=1;pmTop.classList.add('official-pmay-only')}
    if(ekTop){ekTop.colSpan=1;ekTop.classList.add('official-ek-only')}

    // Move the two kept body columns to the end and mark boxed cells.
    for(const row of [...t.tBodies[0].rows]){
      const n=row.cells.length;
      if(n>=17){
        row.cells[n-2]?.classList.add('official-pmay-only');
        row.cells[n-1]?.classList.add('official-ek-only');
      }
    }
    t.dataset.officialCompact='1';
  }
  let busy=false;
  const run=()=>{if(busy)return;busy=true;requestAnimationFrame(()=>{busy=false;compactOfficial()})};
  new MutationObserver(run).observe(document.body,{childList:true,subtree:true});
  document.addEventListener('click',()=>setTimeout(run,30),true);
  document.addEventListener('change',()=>setTimeout(run,0),true);
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',run);else run();
})();
</script>
<!-- ===== END OFFICIAL JANPAD BOX V1 ===== -->
'''

if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: Official Janpad PMAY-G and Ek Bagiya Ongoing boxed; font enlarged')
