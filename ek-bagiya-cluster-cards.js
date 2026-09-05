(function(){
  'use strict';
  const table=document.getElementById('reportTable'),title=document.getElementById('viewTitle');
  if(!table||!title)return;
  const filters=['districtFilter','janpadFilter','engineerFilter','clusterFilter'].map(id=>document.getElementById(id));
  if(filters.some(x=>!x))return;

  const style=document.createElement('style');
  style.textContent=`
  .ebk-panel{display:none;margin:0 0 15px;padding:14px;border:2px solid #15855f;border-radius:18px;background:linear-gradient(150deg,#f7fffb,#f0f8ff);box-shadow:0 8px 24px rgba(13,94,70,.10)}body[data-report-view="ekbagiya"] .ebk-panel{display:block}.ebk-head{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;margin-bottom:10px}.ebk-head h3{margin:0;color:#075c45;font-size:22px;line-height:1.25}.ebk-head p{margin:3px 0 0;color:#557065;font-size:14px}.ebk-tools{display:flex;gap:8px;flex-wrap:wrap}.ebk-tools select{min-height:40px;padding:7px 10px;border:1.5px solid #15855f;border-radius:10px;background:#fff;color:#17483a;font-size:14px;font-weight:800}.ebk-summary{margin-bottom:11px;padding:9px 12px;border-radius:10px;background:#dff6ec;color:#075c45;font-size:14px;font-weight:900}.ebk-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(305px,1fr));gap:12px}.ebk-card{position:relative;overflow:hidden;padding:14px 14px 13px 19px;border:2px solid #30a46c;border-radius:16px;background:#fff;box-shadow:0 7px 18px rgba(20,91,68,.09)}.ebk-card:before{content:"";position:absolute;inset:0 auto 0 0;width:7px;background:#16a34a}.ebk-card.poor{border-color:#e5484d;background:linear-gradient(145deg,#fff,#fff1f2)}.ebk-card.poor:before{background:#dc2626}.ebk-card.watch{border-color:#f0a000;background:linear-gradient(145deg,#fff,#fffbeb)}.ebk-card.watch:before{background:#f59e0b}.ebk-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}.ebk-name{font-size:18px;font-weight:950;color:#123f73;line-height:1.3}.ebk-place{margin-top:3px;color:#587083;font-size:13px;font-weight:800}.ebk-badge{white-space:nowrap;padding:5px 9px;border-radius:999px;background:#16a34a;color:#fff;font-size:12px;font-weight:950}.ebk-card.poor .ebk-badge{background:#dc2626}.ebk-card.watch .ebk-badge{background:#f59e0b;color:#4b2e00}.ebk-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:11px}.ebk-stat{padding:8px 5px;border:1px solid #d8e7e1;border-radius:10px;background:rgba(255,255,255,.86);text-align:center}.ebk-stat b{display:block;color:#083f64;font-size:18px;line-height:1.15}.ebk-stat span{display:block;margin-top:3px;color:#607487;font-size:12px;font-weight:800;line-height:1.2}.ebk-money{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:8px}.ebk-money div{padding:7px 8px;border-radius:9px;background:rgba(230,243,238,.72);color:#365b4f;font-size:12px;font-weight:800}.ebk-money b{display:block;margin-top:2px;color:#075c45;font-size:15px}.ebk-alert{margin-top:9px;color:#a52a2a;font-size:13px;font-weight:900}.ebk-empty{padding:18px;border:1px dashed #9db8ac;border-radius:12px;text-align:center;color:#587067;background:#fff}@media(max-width:720px){.ebk-grid{grid-template-columns:1fr}.ebk-head h3{font-size:19px}.ebk-tools{width:100%}.ebk-tools select{flex:1;min-width:145px}}@media print{.ebk-tools{display:none}.ebk-grid{grid-template-columns:repeat(2,1fr)}.ebk-card{break-inside:avoid;box-shadow:none}}
  `;
  document.head.appendChild(style);
  const panel=document.createElement('section');panel.className='ebk-panel';panel.id='ekBagiyaKpiCards';
  panel.innerHTML='<div class="ebk-head"><div><h3>उपयंत्री–क्लस्टर KPI कार्ड</h3><p>एक बगिया माँ के नाम — कार्य, live मानव दिवस एवं व्यय प्रगति</p></div><div class="ebk-tools"><select id="ebkStatus"><option value="ALL">— सभी प्रगति —</option><option value="poor">खराब प्रगति</option><option value="watch">सुधार आवश्यक</option><option value="good">अच्छी प्रगति</option></select><select id="ebkIssue"><option value="ALL">— सभी निगरानी —</option><option value="zeroMandays">मानव दिवस शून्य</option><option value="nilWorks">NIL कार्य वाले</option><option value="lowExp">व्यय 15% से कम</option></select></div></div><div class="ebk-summary" id="ebkSummary"></div><div class="ebk-grid" id="ebkGrid"></div>';
  table.closest('.table-wrap').parentNode.insertBefore(panel,table.closest('.table-wrap'));
  const grid=document.getElementById('ebkGrid'),summary=document.getElementById('ebkSummary'),statusFilter=document.getElementById('ebkStatus'),issueFilter=document.getElementById('ebkIssue');
  const clean=v=>String(v??'').trim(),num=v=>Number(v)||0,fmt=v=>new Intl.NumberFormat('en-IN').format(Math.round(num(v))),lakh=v=>(num(v)/100000).toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2}),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const gpKey=(j,p)=>[clean(j).toUpperCase(),clean(p).toUpperCase()].join('¦');
  function filteredWorks(){
    const [df,jf,ef,cf]=filters.map(x=>x.value),seen=new Set();
    return (window.ONGOING_DETAILS||[]).filter(r=>{
      if(!['2025-2026','2026-2027'].includes(clean(r.fy)))return false;
      if(!['Ek Bagiya','Ek Bagiya Maa Ke Naam'].includes(clean(r.finalCategory)))return false;
      const district=['AMARPATAN','MAIHAR','RAMNAGAR'].includes(clean(r.janpad).toUpperCase())?'MAIHAR':'SATNA';
      if(df!=='ALL'&&district!==df||jf!=='ALL'&&r.janpad!==jf||ef!=='ALL'&&r.engineer!==ef||cf!=='ALL'&&r.cluster!==cf)return false;
      const code=clean(r.code);if(code&&seen.has(code))return false;if(code)seen.add(code);return true;
    });
  }
  function render(){
    if(document.body.dataset.reportView!=='ekbagiya')return;
    const live=window.SHRAMIK_NIYOJAN||{},liveRows=Array.isArray(live.gpMandaysRows)?live.gpMandaysRows:[],liveMap=new Map(liveRows.map(r=>[gpKey(r.janpad,r.panchayat),num(r.julToday)]));
    if(!liveRows.length){summary.textContent='Official live Persondays उपलब्ध नहीं है। Auto Update चलाएँ।';grid.innerHTML='<div class="ebk-empty">पुराने दोहराए हुए मानव दिवस KPI में नहीं दिखाए गए हैं।</div>';return}
    const groups=new Map();
    filteredWorks().forEach(r=>{
      const key=[clean(r.janpad),clean(r.engineer),clean(r.cluster)].join('¦'),gk=gpKey(r.janpad,r.panchayat),mandays=liveMap.get(gk)||0;
      if(!groups.has(key))groups.set(key,{janpad:r.janpad,engineer:r.engineer||'Unmapped',cluster:r.cluster||'Unmapped',works:0,active:0,nil:0,mandays:0,sanction:0,booked:0,gps:new Set()});
      const x=groups.get(key);x.works++;if(mandays>0)x.active++;else x.nil++;if(!x.gps.has(gk)){x.gps.add(gk);x.mandays+=mandays}x.sanction+=num(r.sanction);x.booked+=num(r.booked);
    });
    let cards=[...groups.values()].map(x=>{x.expPct=x.sanction?100*x.booked/x.sanction:0;x.nilPct=x.works?100*x.nil/x.works:0;x.status=(x.mandays===0||x.nilPct>=75||x.expPct<5)?'poor':(x.nilPct>=40||x.expPct<15?'watch':'good');return x});
    cards=cards.filter(x=>(statusFilter.value==='ALL'||x.status===statusFilter.value)&&(issueFilter.value==='ALL'||issueFilter.value==='zeroMandays'&&x.mandays===0||issueFilter.value==='nilWorks'&&x.nil>0||issueFilter.value==='lowExp'&&x.expPct<15)).sort((a,b)=>({poor:0,watch:1,good:2}[a.status]-{poor:0,watch:1,good:2}[b.status])||b.nilPct-a.nilPct||a.janpad.localeCompare(b.janpad)||a.engineer.localeCompare(b.engineer,'hi'));
    const count={poor:0,watch:0,good:0};cards.forEach(x=>count[x.status]++);summary.textContent=`${cards.length} उपयंत्री–क्लस्टर • खराब ${count.poor} • सुधार आवश्यक ${count.watch} • अच्छी प्रगति ${count.good} • Portal date ${live.officialDate||''}`;
    if(!cards.length){grid.innerHTML='<div class="ebk-empty">चयनित filter में कोई KPI कार्ड नहीं मिला।</div>';return}
    grid.innerHTML=cards.map(x=>{const label=x.status==='poor'?'खराब प्रगति':x.status==='watch'?'सुधार आवश्यक':'अच्छी प्रगति';return `<article class="ebk-card ${x.status}"><div class="ebk-top"><div><div class="ebk-name">${esc(x.engineer)}</div><div class="ebk-place">${esc(x.janpad)} • ${esc(x.cluster)} • ${fmt(x.gps.size)} GP</div></div><span class="ebk-badge">${label}</span></div><div class="ebk-stats"><div class="ebk-stat"><b>${fmt(x.works)}</b><span>Ongoing कार्य</span></div><div class="ebk-stat"><b>${fmt(x.mandays)}</b><span>01 Jul–Today मानव दिवस</span></div><div class="ebk-stat"><b>${fmt(x.active)}</b><span>Active कार्य</span></div><div class="ebk-stat"><b>${fmt(x.nil)}</b><span>NIL कार्य</span></div><div class="ebk-stat"><b>${x.nilPct.toFixed(1)}%</b><span>NIL अनुपात</span></div><div class="ebk-stat"><b>${x.expPct.toFixed(1)}%</b><span>व्यय प्रगति</span></div></div><div class="ebk-money"><div>स्वीकृति ₹ लाख<b>${lakh(x.sanction)}</b></div><div>व्यय ₹ लाख<b>${lakh(x.booked)}</b></div><div>शेष ₹ लाख<b>${lakh(Math.max(0,x.sanction-x.booked))}</b></div></div>${x.status==='poor'?'<div class="ebk-alert">⚠ प्राथमिक समीक्षा आवश्यक</div>':''}</article>`}).join('');
  }
  statusFilter.addEventListener('change',render);issueFilter.addEventListener('change',render);filters.forEach(x=>x.addEventListener('change',()=>setTimeout(render,0)));
  new MutationObserver(render).observe(document.body,{attributes:true,attributeFilter:['data-report-view']});
  render();
})();
