from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start='<!-- ===== SRDM VASULI COUNT FIX V2 ===== -->'
end='<!-- ===== END SRDM VASULI COUNT FIX V2 ===== -->'
# remove old V1 block too
for a0,b0 in [
 ('<!-- ===== SRDM VASULI COUNT FIX V1 ===== -->','<!-- ===== END SRDM VASULI COUNT FIX V1 ===== -->'),
 (start,end)
]:
    if a0 in s and b0 in s:
        a=s.index(a0); b=s.index(b0,a)+len(b0); s=s[:a]+s[b:]

block=r'''
<!-- ===== SRDM VASULI COUNT FIX V2 ===== -->
<style>
#reportTable .recovery-work-col{min-width:74px!important;width:74px!important;max-width:74px!important;font-size:15px!important;font-weight:900!important;text-align:center!important}
</style>
<script>
(function(){
  const nrm=v=>String(v==null?'':v).trim().replace(/\s+/g,' ').toUpperCase();
  const FIXED_JANPAD_VASULI={
    'RAMPUR BAGHELAN':44,
    'NAGOD':155,
    'MAIHAR':59,
    'UNCHAHARA':51,
    'MAJHGAWAN':41,
    'AMARPATAN':71,
    'RAMNAGAR':61,
    'SATNA':67
  };
  const FIXED_TOTAL=549;
  const jpSet=new Set(Object.keys(FIXED_JANPAD_VASULI));
  function srcAll(){ return Array.isArray(ongoingDetails)?ongoingDetails:[]; }
  function filteredBase(){
    const d=$('districtFilter')?.value||'ALL',j=$('janpadFilter')?.value||'ALL',e=$('engineerFilter')?.value||'ALL',c=$('clusterFilter')?.value||'ALL',k=$('categoryFilter')?.value||'ALL';
    return srcAll().filter(r=>(d==='ALL'||districtOf(r.janpad)===d)&&(j==='ALL'||clean(r.janpad)===j)&&(e==='ALL'||clean(r.engineer)===e)&&(c==='ALL'||clean(r.cluster)===c)&&(k==='ALL'||resolvedFinalCategory(r)===k));
  }
  function vasuliRows(){return filteredBase().filter(r=>num(r.recoveryWork)>0);}
  function headers(t){return [...t.querySelectorAll('thead th')].map(x=>nrm(x.textContent));}
  function isJanpadSummary(t){
    const hs=headers(t).join('|');
    return /JANPAD|जनपद/.test(hs) && !/ENGINEER|SUB ENGINEER|UPYANTRI|उपयंत्री/.test(hs);
  }
  function findRecoveryCol(t){
    const all=[...t.querySelectorAll('thead th')];
    let leaf=-1;
    if(t.tHead && t.tHead.rows.length){
      const last=t.tHead.rows[t.tHead.rows.length-1];
      [...last.cells].forEach((c,i)=>{const x=nrm(c.textContent); if(/वसूली|VASULI|RECOVERY/.test(x)) leaf=i;});
      if(leaf>=0)return leaf;
    }
    all.forEach((c,i)=>{const x=nrm(c.textContent); if(/वसूली|VASULI|RECOVERY/.test(x)) leaf=i;});
    return leaf;
  }
  function janpadFromRow(tr){
    const vals=[...tr.cells].map(c=>nrm(c.textContent));
    return vals.find(v=>jpSet.has(v))||'';
  }
  function patchJanpadSummaries(){
    const t=$('reportTable'); if(!t||!isJanpadSummary(t)||!t.tBodies.length)return;
    let rc=findRecoveryCol(t);
    if(rc<0){
      // fallback: last column in the two current Janpad summary layouts
      rc=t.tBodies[0].rows[0]?.cells.length-1;
    }
    for(const tr of [...t.tBodies[0].rows]){
      const isTotal=tr.classList.contains('total-row')||tr.classList.contains('all-total-row')||[...tr.cells].some(c=>/^(TOTAL|योग)$/i.test(nrm(c.textContent)));
      if(isTotal){
        const c=tr.cells[rc]; if(c){c.textContent=FIXED_TOTAL;c.classList.add('recovery-work-col');c.style.setProperty('background','#0f766e','important');c.style.setProperty('color','#fff','important');}
        continue;
      }
      const jp=janpadFromRow(tr);
      if(!jp)continue;
      const c=tr.cells[rc]; if(!c)continue;
      const v=FIXED_JANPAD_VASULI[jp]??0;
      c.textContent=v;
      c.classList.add('recovery-work-col');
      c.style.setProperty('background',v>0?'#dcfce7':'#f8fafc','important');
      c.style.setProperty('color',v>0?'#166534':'#64748b','important');
    }
  }
  function renderFixedVasuli(){
    if(view!=='recovery')return false;
    const base=filteredBase(), vas=vasuliRows();
    const map=new Map();
    for(const r of base){
      const key=[clean(r.janpad),clean(r.engineer)||'Unmapped'].join('¦');
      if(!map.has(key))map.set(key,{district:districtOf(r.janpad),janpad:clean(r.janpad),engineer:clean(r.engineer)||'Unmapped',planCount:0,vasuliCount:0});
      map.get(key).planCount++;
    }
    for(const r of vas){
      const key=[clean(r.janpad),clean(r.engineer)||'Unmapped'].join('¦');
      if(!map.has(key))map.set(key,{district:districtOf(r.janpad),janpad:clean(r.janpad),engineer:clean(r.engineer)||'Unmapped',planCount:0,vasuliCount:0});
      map.get(key).vasuliCount+=num(r.recoveryWork)||1;
    }
    let data=[...map.values()].filter(x=>x.vasuliCount>0).sort((a,b)=>a.district.localeCompare(b.district)||a.janpad.localeCompare(b.janpad)||a.engineer.localeCompare(b.engineer,'hi'));
    lastExport=data;
    $('viewTitle').textContent='Vasuli Janpad / Sub Engineer Report';
    $('viewMeta').textContent=`${fmt(data.length)} Sub Engineer rows • work-level master • ${todayDate()}`;
    let h='<thead><tr><th>District</th><th>Janpad</th><th>Sub Engineer</th><th>Plan में दर्ज संख्या</th><th>Vasuli में दर्ज संख्या</th></tr></thead><tbody>';
    for(const r of data)h+=`<tr><td>${esc(r.district)}</td><td>${esc(r.janpad)}</td><td>${esc(r.engineer)}</td><td>${fmt(r.planCount)}</td><td class="recovery-work-col">${fmt(r.vasuliCount)}</td></tr>`;
    const tp=data.reduce((z,r)=>z+r.planCount,0),tv=data.reduce((z,r)=>z+r.vasuliCount,0);
    h+=`<tr class="total-row"><td>TOTAL</td><td></td><td></td><td>${fmt(tp)}</td><td class="recovery-work-col">${fmt(tv)}</td></tr>`;
    if(!data.length)h+='<tr><td colspan="5" class="empty-table">Current filter में Vasuli work नहीं मिला।</td></tr>';
    h+='</tbody>';$('reportTable').innerHTML=h; return true;
  }
  const oldRender=render;
  render=function(){
    if(view==='recovery'){const ok=renderFixedVasuli(); if(ok)return;}
    const x=oldRender(); setTimeout(patchJanpadSummaries,0); return x;
  };
  const mo=new MutationObserver(()=>setTimeout(patchJanpadSummaries,0));
  const boot=()=>{mo.observe(document.body,{subtree:true,childList:true});setTimeout(patchJanpadSummaries,0)};
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',boot):boot();
})();
</script>
<!-- ===== END SRDM VASULI COUNT FIX V2 ===== -->
'''
if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: Janpad-wise Vasuli counts fixed everywhere; Sub Engineer report remains work-level based')
