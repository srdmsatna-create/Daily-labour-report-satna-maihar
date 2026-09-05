(function(){
  'use strict';
  const report=window.MUSTER_EMB_REPORT;
  const section=document.getElementById('musterEmbMonitoring');
  const blockFilter=document.getElementById('musterBlockFilter');
  const engineerFilter=document.getElementById('musterEngineerFilter');
  const anchor=document.getElementById('musterZeroAlert');
  if(!report||!Array.isArray(report.gpRows)||!section||!blockFilter||!engineerFilter||!anchor)return;

  const style=document.createElement('style');
  style.textContent=`
  .mec-panel{margin:14px 0 16px}.mec-head{display:flex;align-items:flex-end;justify-content:space-between;gap:12px;margin-bottom:10px;flex-wrap:wrap}.mec-head h3{margin:0;color:#123f73;font-size:21px;line-height:1.25}.mec-head p{margin:3px 0 0;color:#5a6f84;font-size:14px}.mec-legend{display:flex;gap:7px;flex-wrap:wrap;font-size:13px;font-weight:800}.mec-legend span{padding:5px 9px;border-radius:999px}.mec-legend .poor{background:#fee2e2;color:#991b1b}.mec-legend .watch{background:#fef3c7;color:#92400e}.mec-legend .good{background:#dcfce7;color:#166534}.mec-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(285px,1fr));gap:12px}.mec-card{position:relative;border:2px solid #b8cee0;border-radius:16px;padding:14px;background:#fff;box-shadow:0 7px 18px rgba(18,63,115,.09);overflow:hidden}.mec-card:before{content:"";position:absolute;inset:0 auto 0 0;width:7px;background:#2e7d32}.mec-card.mec-poor{border-color:#ef4444;background:linear-gradient(145deg,#fff 0%,#fff1f2 100%)}.mec-card.mec-poor:before{background:#dc2626}.mec-card.mec-watch{border-color:#f59e0b;background:linear-gradient(145deg,#fff 0%,#fffbeb 100%)}.mec-card.mec-watch:before{background:#f59e0b}.mec-card.mec-good{border-color:#22c55e;background:linear-gradient(145deg,#fff 0%,#f0fdf4 100%)}.mec-top{display:flex;justify-content:space-between;gap:9px;align-items:flex-start;padding-left:5px}.mec-title{font-size:18px;font-weight:950;color:#123f73;line-height:1.25}.mec-sub{margin-top:3px;font-size:14px;font-weight:800;color:#566b7e}.mec-badge{white-space:nowrap;border-radius:999px;padding:5px 9px;font-size:12px;font-weight:950}.mec-poor .mec-badge{background:#dc2626;color:#fff}.mec-watch .mec-badge{background:#f59e0b;color:#4b2e00}.mec-good .mec-badge{background:#16a34a;color:#fff}.mec-stats{display:grid;grid-template-columns:repeat(4,1fr);gap:7px;margin-top:12px}.mec-stat{padding:8px 5px;border:1px solid #dce7f0;border-radius:10px;background:rgba(255,255,255,.83);text-align:center}.mec-stat b{display:block;color:#0b355d;font-size:18px;line-height:1.15}.mec-stat span{display:block;margin-top:3px;color:#5e7183;font-size:12px;font-weight:750;line-height:1.2}.mec-progress{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:9px}.mec-rate{background:rgba(255,255,255,.75);border-radius:9px;padding:7px 9px;color:#354f67;font-size:13px;font-weight:800}.mec-rate b{float:right;color:#123f73}.mec-alerts{margin-top:9px;padding-left:5px;color:#8a3a14;font-size:13px;font-weight:850;line-height:1.4}.mec-empty{padding:18px;border:1px dashed #aebfd0;border-radius:12px;text-align:center;color:#5d7185;background:#f8fbfe}.mec-summary{margin:0 0 10px;padding:9px 12px;border-radius:11px;background:#edf6ff;color:#17466e;font-size:14px;font-weight:850}@media(max-width:720px){.mec-grid{grid-template-columns:1fr}.mec-stats{grid-template-columns:repeat(2,1fr)}.mec-head h3{font-size:19px}}@media print{.mec-grid{grid-template-columns:repeat(2,1fr)}.mec-card{break-inside:avoid;box-shadow:none}.mec-panel{page-break-before:always}}
  `;
  document.head.appendChild(style);

  const panel=document.createElement('div');
  panel.className='mec-panel';
  panel.innerHTML='<div class="mec-head"><div><h3>उपयंत्री–क्लस्टर कार्ड — Muster Roll एवं e‑MB</h3><p>चयनित जनपद/उपयंत्री के अनुसार live KPI स्थिति</p></div><div class="mec-legend"><span class="poor">खराब प्रगति</span><span class="watch">सुधार आवश्यक</span><span class="good">अच्छी प्रगति</span></div></div><div id="mecSummary" class="mec-summary"></div><div id="mecGrid" class="mec-grid"></div>';
  anchor.parentNode.insertBefore(panel,anchor);
  const grid=document.getElementById('mecGrid'),summary=document.getElementById('mecSummary');
  const cols=['issued','filled','embFilled','noEmb','pendingEmb','verifiedAE','pendingVerification'];
  const num=v=>Number(v)||0;
  const fmt=v=>new Intl.NumberFormat('en-IN').format(Math.round(num(v)));
  const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const pct=(a,b)=>b?100*a/b:0;

  function renderCards(){
    const rows=report.gpRows.filter(r=>(blockFilter.value==='ALL'||r.block===blockFilter.value)&&(engineerFilter.value==='ALL'||r.engineer===engineerFilter.value));
    const groups=new Map();
    rows.forEach(r=>{
      const key=[r.block,r.engineer||'Unmapped',r.cluster||'Unmapped'].join('¦');
      if(!groups.has(key))groups.set(key,{block:r.block,engineer:r.engineer||'Unmapped',cluster:r.cluster||'Unmapped',gp:0,...Object.fromEntries(cols.map(c=>[c,0]))});
      const x=groups.get(key);x.gp++;cols.forEach(c=>x[c]+=num(r[c]));
    });
    const cards=[...groups.values()].map(x=>{
      x.fillPct=pct(x.filled,x.issued);x.embPct=pct(x.embFilled,x.filled);
      x.status=(x.fillPct<50||x.embPct<40)?'poor':(x.fillPct>=70&&x.embPct>=55?'good':'watch');
      return x;
    }).sort((a,b)=>({poor:0,watch:1,good:2}[a.status]-{poor:0,watch:1,good:2}[b.status])||a.block.localeCompare(b.block)||a.engineer.localeCompare(b.engineer,'hi'));
    const statusCount={poor:0,watch:0,good:0};cards.forEach(x=>statusCount[x.status]++);
    summary.textContent=`${cards.length} उपयंत्री–क्लस्टर • खराब ${statusCount.poor} • सुधार आवश्यक ${statusCount.watch} • अच्छी प्रगति ${statusCount.good}`;
    if(!cards.length){grid.innerHTML='<div class="mec-empty">चयनित filter में कोई उपयंत्री–क्लस्टर नहीं मिला।</div>';return}
    grid.innerHTML=cards.map(x=>{
      const label=x.status==='poor'?'खराब प्रगति':x.status==='watch'?'सुधार आवश्यक':'अच्छी प्रगति';
      return `<article class="mec-card mec-${x.status}"><div class="mec-top"><div><div class="mec-title">${esc(x.engineer)}</div><div class="mec-sub">${esc(x.block)} • ${esc(x.cluster)} • ${fmt(x.gp)} GP</div></div><span class="mec-badge">${label}</span></div><div class="mec-stats"><div class="mec-stat"><b>${fmt(x.issued)}</b><span>MR जारी</span></div><div class="mec-stat"><b>${fmt(x.filled)}</b><span>MR भरे</span></div><div class="mec-stat"><b>${fmt(x.embFilled)}</b><span>e‑MB भरे</span></div><div class="mec-stat"><b>${fmt(x.verifiedAE)}</b><span>AE सत्यापित</span></div></div><div class="mec-progress"><div class="mec-rate">MR भराव <b>${x.fillPct.toFixed(1)}%</b></div><div class="mec-rate">e‑MB पूर्णता <b>${x.embPct.toFixed(1)}%</b></div></div><div class="mec-alerts">e‑MB रहित: ${fmt(x.noEmb)} &nbsp;•&nbsp; e‑MB लंबित: ${fmt(x.pendingEmb)} &nbsp;•&nbsp; सत्यापन लंबित: ${fmt(x.pendingVerification)}</div></article>`;
    }).join('');
  }
  blockFilter.addEventListener('change',()=>setTimeout(renderCards,0));
  engineerFilter.addEventListener('change',renderCards);
  renderCards();
})();
