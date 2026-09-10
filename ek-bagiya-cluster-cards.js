(function(){
  'use strict';
  const table=document.getElementById('reportTable'),title=document.getElementById('viewTitle');
  if(!table||!title)return;
  const filters=['districtFilter','janpadFilter','engineerFilter','clusterFilter'].map(id=>document.getElementById(id));
  if(filters.some(x=>!x))return;

  const style=document.createElement('style');
  style.textContent=`
  .ebk-panel{display:none;margin:0 0 15px;padding:14px;border:2px solid #15855f;border-radius:18px;background:linear-gradient(150deg,#f7fffb,#f0f8ff);box-shadow:0 8px 24px rgba(13,94,70,.10)}body[data-report-view="ekbagiya"] .ebk-panel{display:block}.ebk-head{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;flex-wrap:wrap;margin-bottom:10px}.ebk-head h3{margin:0;color:#075c45;font-size:22px;line-height:1.25}.ebk-head p{margin:3px 0 0;color:#557065;font-size:14px}.ebk-tools{display:flex;gap:8px;flex-wrap:wrap}.ebk-tools select{min-height:40px;padding:7px 10px;border:1.5px solid #15855f;border-radius:10px;background:#fff;color:#17483a;font-size:14px;font-weight:800}.ebk-summary{margin-bottom:11px;padding:9px 12px;border-radius:10px;background:#dff6ec;color:#075c45;font-size:14px;font-weight:900}.ebk-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(305px,1fr));gap:12px}.ebk-card{position:relative;overflow:hidden;padding:14px 14px 13px 19px;border:2px solid #30a46c;border-radius:16px;background:#fff;box-shadow:0 7px 18px rgba(20,91,68,.09)}.ebk-card:before{content:"";position:absolute;inset:0 auto 0 0;width:7px;background:#16a34a}.ebk-card.poor{border-color:#e5484d;background:linear-gradient(145deg,#fff,#fff1f2)}.ebk-card.poor:before{background:#dc2626}.ebk-card.watch{border-color:#f0a000;background:linear-gradient(145deg,#fff,#fffbeb)}.ebk-card.watch:before{background:#f59e0b}.ebk-top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}.ebk-name{font-size:18px;font-weight:950;color:#123f73;line-height:1.3}.ebk-place{margin-top:3px;color:#587083;font-size:13px;font-weight:800}.ebk-badge{white-space:nowrap;padding:5px 9px;border-radius:999px;background:#16a34a;color:#fff;font-size:12px;font-weight:950}.ebk-card.poor .ebk-badge{background:#dc2626}.ebk-card.watch .ebk-badge{background:#f59e0b;color:#4b2e00}.ebk-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:11px}.ebk-stat{padding:8px 5px;border:1px solid #d8e7e1;border-radius:10px;background:rgba(255,255,255,.86);text-align:center}.ebk-stat b{display:block;color:#083f64;font-size:18px;line-height:1.15}.ebk-stat span{display:block;margin-top:3px;color:#607487;font-size:12px;font-weight:800;line-height:1.2}.ebk-money{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:8px}.ebk-money div{padding:7px 8px;border-radius:9px;background:rgba(230,243,238,.72);color:#365b4f;font-size:12px;font-weight:800}.ebk-money b{display:block;margin-top:2px;color:#075c45;font-size:15px}.ebk-alert{margin-top:9px;color:#a52a2a;font-size:13px;font-weight:900}.ebk-empty{padding:18px;border:1px dashed #9db8ac;border-radius:12px;text-align:center;color:#587067;background:#fff}@media(max-width:720px){.ebk-grid{grid-template-columns:1fr}.ebk-head h3{font-size:19px}.ebk-tools{width:100%}.ebk-tools select{flex:1;min-width:145px}}@media print{.ebk-tools{display:none!important}.ebk-panel{padding:12px!important}.ebk-grid{grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important}.ebk-card{break-inside:avoid!important;page-break-inside:avoid!important;box-shadow:none!important;padding:14px 13px 13px 18px!important}.ebk-name{font-size:21px!important}.ebk-place{font-size:14px!important}.ebk-badge{font-size:13px!important}.ebk-summary{font-size:15px!important}.ebk-stat b{font-size:21px!important}.ebk-stat span{font-size:13px!important;line-height:1.25!important}.ebk-money div{font-size:13px!important}.ebk-money b{font-size:18px!important}.ebk-alert{font-size:14px!important}.report-table.ekbagiya-grid th,.report-table.ekbagiya-grid td{font-size:8.5px!important;line-height:1.2!important;padding:2.6px!important}}
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
    const source=typeof WORK_DETAILS!=='undefined'&&Array.isArray(WORK_DETAILS)?WORK_DETAILS:[];
    return source.filter(r=>{
      if(!['2025-2026','2026-2027'].includes(clean(r['Fin Year'])))return false;
      const district=clean(r.Zila)||(['AMARPATAN','MAIHAR','RAMNAGAR'].includes(clean(r.Janpad).toUpperCase())?'MAIHAR':'SATNA');
      if(df!=='ALL'&&district!==df||jf!=='ALL'&&r.Janpad!==jf||ef!=='ALL'&&r.Upyantri!==ef||cf!=='ALL'&&r.Cluster!==cf)return false;
      const code=clean(r['Work Code']);if(code&&seen.has(code))return false;if(code)seen.add(code);return true;
    });
  }
  function syncReportColumns(rows){
    const head=table.querySelector('thead tr');if(!head)return;
    ['Verified Works','>90%'].forEach(label=>{const target=[...head.cells].find(h=>clean(h.textContent)===label);if(target){const i=target.cellIndex;table.querySelectorAll('tr').forEach(tr=>{if(tr.cells[i])tr.cells[i].remove()})}});
    if(head.querySelector('.ebk-prior-mandays'))return;
    const aprJun=[...head.cells].find(h=>/Mandays\s*01 Apr.?30 Jun/i.test(clean(h.textContent)));if(!aprJun)return;
    const insertAt=aprJun.cellIndex,byEngineer=new Map(),byJanpad=new Map();let all=0;
    rows.forEach(r=>{const v=num(r['Previous Mandays']),k=[clean(r.Janpad),clean(r.Upyantri),clean(r.Cluster)].join('¦'),j=clean(r.Janpad);byEngineer.set(k,(byEngineer.get(k)||0)+v);byJanpad.set(j,(byJanpad.get(j)||0)+v);all+=v});
    const th=document.createElement('th');th.className='ebk-prior-mandays';th.innerHTML='Mandays From Work Start Date<br>To 31 March 2026';head.insertBefore(th,aprJun);
    table.querySelectorAll('tbody tr').forEach(tr=>{const td=[...tr.cells],first=clean(td[0]?.textContent),jan=clean(td[1]?.textContent),eng=clean(td[2]?.textContent),cl=clean(td[3]?.textContent);let v=0;
      if(/^ALL TOTAL$/i.test(first)||/^TOTAL$/i.test(first))v=all;
      else if(/ TOTAL$/i.test(jan))v=byJanpad.get(jan.replace(/\s+TOTAL$/i,''))||0;
      else v=byEngineer.get([jan,eng,cl].join('¦'))||0;
      const c=document.createElement('td');c.className='ebk-prior-mandays';c.textContent=fmt(v);tr.insertBefore(c,tr.cells[insertAt]||null);
    });
  }
  function render(){
    if(document.body.dataset.reportView!=='ekbagiya')return;
    const rows=filteredWorks();
    syncReportColumns(rows);
    if(!rows.length){summary.textContent='चयनित filter में Report Card data उपलब्ध नहीं है।';grid.innerHTML='<div class="ebk-empty">कोई KPI कार्ड नहीं मिला।</div>';return}
    const groups=new Map();
    rows.forEach(r=>{
      const key=[clean(r.Janpad),clean(r.Upyantri),clean(r.Cluster)].join('¦');
      if(!groups.has(key))groups.set(key,{janpad:r.Janpad,engineer:r.Upyantri||'Unmapped',cluster:r.Cluster||'Unmapped',works:0,active:0,nil:0,mandays:0,sanction:0,bookedWage:0,bookedMaterial:0,booked:0,gps:new Set()});
      const x=groups.get(key),currentMandays=num(r['Mandays 2026-2027']);
      if(clean(r['Work Status']).toLowerCase()==='ongoing')x.works++;
      if(currentMandays>0)x.active++;else x.nil++;
      x.mandays+=currentMandays;x.sanction+=num(r['Sanction Amount Total']);x.bookedWage+=num(r['Overall Booked Wages']);x.bookedMaterial+=num(r['Overall Booked Material']);x.booked+=num(r['Overall Total Booked']);x.gps.add(gpKey(r.Janpad,r['Panchayat Name']));
    });
    let cards=[...groups.values()].map(x=>{x.expPct=x.sanction?100*x.booked/x.sanction:0;x.nilPct=(x.active+x.nil)?100*x.nil/(x.active+x.nil):0;x.status=(x.mandays===0||x.nilPct>=75||x.expPct<5)?'poor':(x.nilPct>=40||x.expPct<15?'watch':'good');return x});
    cards=cards.filter(x=>(statusFilter.value==='ALL'||x.status===statusFilter.value)&&(issueFilter.value==='ALL'||issueFilter.value==='zeroMandays'&&x.mandays===0||issueFilter.value==='nilWorks'&&x.nil>0||issueFilter.value==='lowExp'&&x.expPct<15)).sort((a,b)=>({poor:0,watch:1,good:2}[a.status]-{poor:0,watch:1,good:2}[b.status])||b.nilPct-a.nilPct||a.janpad.localeCompare(b.janpad)||a.engineer.localeCompare(b.engineer,'hi'));
    const count={poor:0,watch:0,good:0};cards.forEach(x=>count[x.status]++);summary.textContent=`${cards.length} उपयंत्री–क्लस्टर • खराब ${count.poor} • सुधार आवश्यक ${count.watch} • अच्छी प्रगति ${count.good} • Report Card parameters`;
    if(!cards.length){grid.innerHTML='<div class="ebk-empty">चयनित filter में कोई KPI कार्ड नहीं मिला।</div>';return}
    grid.innerHTML=cards.map(x=>{const label=x.status==='poor'?'खराब प्रगति':x.status==='watch'?'सुधार आवश्यक':'अच्छी प्रगति';return `<article class="ebk-card ${x.status}"><div class="ebk-top"><div><div class="ebk-name">${esc(x.engineer)}</div><div class="ebk-place">${esc(x.janpad)} • ${esc(x.cluster)} • ${fmt(x.gps.size)} GP</div></div><span class="ebk-badge">${label}</span></div><div class="ebk-stats"><div class="ebk-stat"><b>${fmt(x.works)}</b><span>Ongoing कार्य</span></div><div class="ebk-stat"><b>${fmt(x.mandays)}</b><span>01 Jul–Today मानव दिवस</span></div><div class="ebk-stat"><b>${fmt(x.active)}</b><span>Active कार्य</span></div><div class="ebk-stat"><b>${fmt(x.nil)}</b><span>NIL कार्य</span></div><div class="ebk-stat"><b>${x.nilPct.toFixed(1)}%</b><span>NIL अनुपात</span></div><div class="ebk-stat"><b>${x.expPct.toFixed(1)}%</b><span>व्यय प्रगति</span></div></div><div class="ebk-money"><div>स्वीकृति ₹ लाख<b>${lakh(x.sanction)}</b></div><div>Booked Wages ₹ लाख<b>${lakh(x.bookedWage)}</b></div><div>Booked Material ₹ लाख<b>${lakh(x.bookedMaterial)}</b></div><div>Total Booked ₹ लाख<b>${lakh(x.booked)}</b></div><div>शेष ₹ लाख<b>${lakh(Math.max(0,x.sanction-x.booked))}</b></div></div>${x.status==='poor'?'<div class="ebk-alert">⚠ प्राथमिक समीक्षा आवश्यक</div>':''}</article>`}).join('');
  }
  statusFilter.addEventListener('change',render);issueFilter.addEventListener('change',render);filters.forEach(x=>x.addEventListener('change',()=>setTimeout(render,0)));
  new MutationObserver(render).observe(document.body,{attributes:true,attributeFilter:['data-report-view']});
  render();
})();
