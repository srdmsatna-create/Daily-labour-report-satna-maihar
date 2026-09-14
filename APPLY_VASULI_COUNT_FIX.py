from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start='<!-- ===== SRDM VASULI COUNT FIX V1 ===== -->'
end='<!-- ===== END SRDM VASULI COUNT FIX V1 ===== -->'
if start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+s[b:]

block=r'''
<!-- ===== SRDM VASULI COUNT FIX V1 ===== -->
<style>
#reportTable .recovery-work-col{min-width:74px!important;width:74px!important;max-width:74px!important;font-size:14px!important;font-weight:900!important;text-align:center!important}
</style>
<script>
(function(){
  const nrm=v=>String(v==null?'':v).trim().replace(/\s+/g,' ').toUpperCase();
  const jpSet=new Set(['AMARPATAN','MAIHAR','RAMNAGAR','MAJHGAWAN','NAGOD','RAMPUR BAGHELAN','SATNA','SOHAWAL','UNCHAHARA']);
  function srcAll(){ return Array.isArray(ongoingDetails)?ongoingDetails:[]; }
  function filteredBase(){
    const d=$('districtFilter')?.value||'ALL',j=$('janpadFilter')?.value||'ALL',e=$('engineerFilter')?.value||'ALL',c=$('clusterFilter')?.value||'ALL',k=$('categoryFilter')?.value||'ALL';
    return srcAll().filter(r=>(d==='ALL'||districtOf(r.janpad)===d)&&(j==='ALL'||clean(r.janpad)===j)&&(e==='ALL'||clean(r.engineer)===e)&&(c==='ALL'||clean(r.cluster)===c)&&(k==='ALL'||resolvedFinalCategory(r)===k));
  }
  function vasuliRows(){return filteredBase().filter(r=>num(r.recoveryWork)>0);}
  function inferScope(tr){
    const vals=[...tr.cells].map(c=>clean(c.textContent));
    const scope={};
    scope.janpad=vals.find(v=>jpSet.has(nrm(v)))||'';
    const engs=new Set(srcAll().map(r=>clean(r.engineer)).filter(Boolean));
    const cls=new Set(srcAll().map(r=>clean(r.cluster)).filter(Boolean));
    const gps=new Set(srcAll().map(r=>clean(r.panchayat)).filter(Boolean));
    scope.engineer=vals.find(v=>engs.has(v))||'';
    scope.cluster=vals.find(v=>cls.has(v))||'';
    scope.gp=vals.find(v=>gps.has(v))||'';
    return scope;
  }
  function countFor(scope){
    let a=vasuliRows();
    if(scope.janpad)a=a.filter(r=>clean(r.janpad)===scope.janpad);
    if(scope.engineer)a=a.filter(r=>clean(r.engineer)===scope.engineer);
    if(scope.cluster)a=a.filter(r=>clean(r.cluster)===scope.cluster);
    if(scope.gp)a=a.filter(r=>clean(r.panchayat)===scope.gp);
    return a.reduce((z,r)=>z+(num(r.recoveryWork)||1),0);
  }
  function fixRecoveryColumn(){
    if(view==='recovery')return;
    const t=$('reportTable'); if(!t)return;
    const rows=[...t.querySelectorAll('tbody tr')];
    for(const tr of rows){
      const c=tr.querySelector('td.recovery-work-col'); if(!c)continue;
      const total=tr.classList.contains('total-row')||tr.classList.contains('all-total-row')||[...tr.cells].slice(0,4).some(x=>/^(TOTAL|योग)$/i.test(clean(x.textContent)));
      const v=total?vasuliRows().reduce((z,r)=>z+(num(r.recoveryWork)||1),0):countFor(inferScope(tr));
      c.textContent=fmt(v);
      c.classList.toggle('recovery-positive',v>0&&!total); c.classList.toggle('recovery-zero',v===0&&!total);
      c.style.setProperty('background',total?'#0f766e':v>0?'#dcfce7':'#f8fafc','important');
      c.style.setProperty('color',total?'#fff':v>0?'#166534':'#64748b','important');
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
    $('viewMeta').textContent=`${fmt(data.length)} Sub Engineer rows • fixed from work-level master • ${todayDate()}`;
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
    const x=oldRender(); setTimeout(fixRecoveryColumn,0); return x;
  };
  const mo=new MutationObserver(()=>setTimeout(fixRecoveryColumn,0));
  const boot=()=>{mo.observe(document.body,{subtree:true,childList:true});setTimeout(fixRecoveryColumn,0)};
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',boot):boot();
})();
</script>
<!-- ===== END SRDM VASULI COUNT FIX V1 ===== -->
'''
if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: Vasuli Janpad and Sub Engineer counts fixed from work-level master')
