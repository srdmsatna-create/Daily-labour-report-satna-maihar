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
  style.textContent+=' .ebk-detail-table{width:100%;border-collapse:collapse;table-layout:fixed;margin-top:9px;border:2px solid #173f35;background:#fff}.ebk-detail-table th,.ebk-detail-table td{border:1.5px solid #173f35;padding:6px 8px;line-height:1.3;vertical-align:middle;overflow-wrap:anywhere}.ebk-detail-table th{width:68%;text-align:left;font-size:13px;font-weight:800;color:#214c40;background:#edf6f1}.ebk-detail-table td{width:32%;text-align:right;font-size:19px;font-weight:900;color:#075c45;font-variant-numeric:tabular-nums}.ebk-detail-table thead th{background:#173f35;color:#fff}.ebk-detail-table thead th:last-child{width:32%;text-align:right}@media print{.ebk-detail-table th{font-size:13px!important}.ebk-detail-table td{font-size:20px!important}.ebk-detail-table{break-inside:avoid;border:2px solid #173f35!important}.ebk-detail-table th,.ebk-detail-table td{border:1.5px solid #173f35!important}}';
  style.textContent+=' .ebk-panel{border:0;border-radius:0;background:transparent;box-shadow:none;padding:0}.ebk-grid{display:block}.ebk-card,.ebk-card.poor,.ebk-card.watch{border:0;border-radius:0;background:transparent;box-shadow:none;padding:0;margin:0 0 22px;overflow:visible}.ebk-card:before{display:none}.ebk-top{padding:7px 0;border-bottom:2px solid #173f35}.ebk-badge,.ebk-card.poor .ebk-badge,.ebk-card.watch .ebk-badge{border-radius:0;background:transparent;color:#173f35;padding:0;white-space:normal}.ebk-summary{border-radius:0;background:transparent;padding:7px 0;border-bottom:2px solid #173f35}.ebk-empty{border:0;border-radius:0;background:transparent}@media print{.ebk-grid{display:block!important}.ebk-panel{padding:0!important;border:0!important;background:transparent!important}.ebk-card{padding:0!important;margin-bottom:16px!important;border:0!important;box-shadow:none!important}}';
  style.textContent+=' .ebk-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;align-items:start}.ebk-card,.ebk-card.poor,.ebk-card.watch{min-width:0;border:2px solid #173f35;border-radius:10px;background:#fff;box-shadow:none;padding:10px;margin:0;overflow:hidden}.ebk-top{padding:0 0 7px;gap:6px}.ebk-name{font-size:18px;overflow-wrap:anywhere}.ebk-place{font-size:12px;overflow-wrap:anywhere}.ebk-badge{font-size:11px;max-width:75px;text-align:right}.ebk-detail-table{margin-top:6px}.ebk-detail-table th,.ebk-detail-table td{padding:4px 6px;line-height:1.2}.ebk-detail-table th{font-size:12px;width:65%}.ebk-detail-table td{font-size:18px;width:35%}.ebk-detail-table thead th:last-child{width:35%}.ebk-alert{margin-top:6px;font-size:12px}@media(max-width:720px){.ebk-grid{grid-template-columns:1fr}}@media print{.ebk-grid{display:grid!important;grid-template-columns:repeat(2,minmax(0,1fr))!important;gap:10px!important}.ebk-card{border:2px solid #173f35!important;padding:9px!important;margin:0!important}.ebk-name{font-size:18px!important}.ebk-place{font-size:12px!important}.ebk-detail-table th{font-size:12px!important}.ebk-detail-table td{font-size:18px!important}.ebk-detail-table th,.ebk-detail-table td{padding:4px 6px!important}}';
  style.textContent+=' .ebk-card.poor .ebk-badge{background:#fff0cc;color:#754400;border:1px solid #a86a00;border-radius:5px;padding:4px 6px;max-width:90px;font-weight:900}.ebk-card.poor .ebk-alert{color:#754400}';
  style.textContent+=' .ebk-tools button{min-height:40px;padding:7px 12px;border:2px solid #173f35;border-radius:7px;background:#173f35;color:#fff;font-size:14px;font-weight:900;cursor:pointer}';
  document.head.appendChild(style);
  const panel=document.createElement('section');panel.className='ebk-panel';panel.id='ekBagiyaKpiCards';
  panel.innerHTML='<div class="ebk-head"><div><h3>उपयंत्री–क्लस्टर KPI कार्ड</h3><p>एक बगिया माँ के नाम — कार्य, live मानव दिवस एवं व्यय प्रगति</p></div><div class="ebk-tools"><button type="button" id="ebkPrintCards">KPI कार्ड Print / PDF</button><select id="ebkFY"><option value="ALL">FY 2025–26 + 2026–27</option><option value="2025-2026">FY 2025–26</option><option value="2026-2027">FY 2026–27</option></select><select id="ebkStatus"><option value="ALL">— सभी प्रगति —</option><option value="poor">खराब प्रगति</option><option value="watch">सुधार आवश्यक</option><option value="good">अच्छी प्रगति</option></select><select id="ebkIssue"><option value="ALL">— सभी निगरानी —</option><option value="zeroMandays">मानव दिवस शून्य</option><option value="nilWorks">शून्य व्यय वाले कार्य</option><option value="lowExp">व्यय 15% से कम</option></select></div></div><div class="ebk-summary" id="ebkSummary"></div><div class="ebk-grid" id="ebkGrid"></div>';
  table.closest('.table-wrap').parentNode.insertBefore(panel,table.closest('.table-wrap'));
  const grid=document.getElementById('ebkGrid'),summary=document.getElementById('ebkSummary'),statusFilter=document.getElementById('ebkStatus'),issueFilter=document.getElementById('ebkIssue');
  const clean=v=>String(v??'').trim(),num=v=>Number(v)||0,fmt=v=>new Intl.NumberFormat('en-IN').format(Math.round(num(v))),lakh=v=>(num(v)/100000).toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2}),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const firstNum=(r,keys)=>{for(const k of keys){if(r[k]!==undefined&&r[k]!==null&&r[k]!=='')return num(r[k])}return 0};
  function mandaysOf(r){
    // Keep the three periods strictly separate.
    // Before 31 Mar = historical mandays only.
    // 01 Apr-30 Jun = MGNREGA Nrega sheet "current year mandays" only.
    // 01 Jul-Till Date = VB-G RAM G July mandays only.
    const before=firstNum(r,['Mandays Before 31 March 2026','Mandays 2025-2026','Mandays From Work Start Date To 31 March 2026','Previous Mandays']);
    const aprJun=firstNum(r,['NREGA Till 30 June Mandays','Mandays 01 Apr-30 Jun 2026','Mandays 01 Apr–30 Jun 2026']);
    const july=firstNum(r,['Mandays 01 Jul-Till Date','Mandays 01 Jul–Till Date','01 Jul-Till Date Mandays','July Mandays','Mandays 2026-2027']);
    return {before,aprJun,july,total:before+aprJun+july};
  }
  let liveSnapshot=null,loadError=false;
  const gpKey=(j,p)=>[clean(j).toUpperCase(),clean(p).toUpperCase()].join('¦');
  function filteredWorks(){
    const [df,jf,ef,cf]=filters.map(x=>x.value),seen=new Set();
    const source=(liveSnapshot?.works||[]).filter(w=>clean(w.status).toLowerCase()==='ongoing').map(w=>({
      Zila:w.district,Janpad:w.janpad,Upyantri:w.engineer,Cluster:w.cluster,'Panchayat Name':w.panchayat,'Work Code':w.code,'Work Status':w.status,
      financialYear:w.financialYear,sanctionWage:w.sw,sanctionMaterial:w.sm,sources:w.sources,paidWage:w.pw,paidMaterial:w.pm,'Sanction Amount Total':w.sw+w.sm,'Overall Booked Wages':w.bsw,'Overall Booked Material':w.bsm,'Overall Total Booked':w.bsw+w.bsm,
      'Mandays Before 31 March 2026':Math.max(0,w.nregaTotalMandays-w.nregaAprJunMandays),
      'NREGA Till 30 June Mandays':w.nregaAprJunMandays,'Mandays 01 Jul-Till Date':w.julyMandays
    }));
    return source.filter(r=>{
      // Verified current ongoing work codes; engineer/cluster from the GP master.
      const district=clean(r.Zila)||(['AMARPATAN','MAIHAR','RAMNAGAR'].includes(clean(r.Janpad).toUpperCase())?'MAIHAR':'SATNA');
      if(document.getElementById('ebkFY').value!=='ALL'&&r.financialYear!==document.getElementById('ebkFY').value)return false;
      if(df!=='ALL'&&district!==df||jf!=='ALL'&&r.Janpad!==jf||ef!=='ALL'&&r.Upyantri!==ef||cf!=='ALL'&&r.Cluster!==cf)return false;
      const code=clean(r['Work Code']);if(code&&seen.has(code))return false;if(code)seen.add(code);return true;
    });
  }
  function syncReportColumns(rows){
    const head=table.querySelector('thead tr');if(!head)return;
    ['Verified Works','>90%'].forEach(label=>{const target=[...head.cells].find(h=>clean(h.textContent)===label);if(target){const i=target.cellIndex;table.querySelectorAll('tr').forEach(tr=>{if(tr.cells[i])tr.cells[i].remove()})}});
    const aprJun=[...head.cells].find(h=>/Mandays\s*01 Apr.?30 Jun/i.test(clean(h.textContent)));if(!aprJun)return;
    if(head.querySelector('.ebk-prior-mandays'))return;
    aprJun.innerHTML='Mandays<br>Before 31 March 2026';aprJun.classList.add('ebk-before-mandays');
    const insertAt=aprJun.cellIndex+1,byEngineer=new Map(),byJanpad=new Map();let all=0;
    rows.forEach(r=>{const v=mandaysOf(r).aprJun,k=[clean(r.Janpad),clean(r.Upyantri),clean(r.Cluster)].join('¦'),j=clean(r.Janpad);byEngineer.set(k,(byEngineer.get(k)||0)+v);byJanpad.set(j,(byJanpad.get(j)||0)+v);all+=v});
    const th=document.createElement('th');th.className='ebk-prior-mandays';th.innerHTML='Mandays<br>01 Apr–30 Jun 2026';head.insertBefore(th,head.cells[insertAt]||null);
    table.querySelectorAll('tbody tr').forEach(tr=>{const td=[...tr.cells],first=clean(td[0]?.textContent),jan=clean(td[1]?.textContent),eng=clean(td[2]?.textContent),cl=clean(td[3]?.textContent);let v=0;
      if(/^ALL TOTAL$/i.test(first)||/^TOTAL$/i.test(first))v=all;
      else if(/ TOTAL$/i.test(jan))v=byJanpad.get(jan.replace(/\s+TOTAL$/i,''))||0;
      else v=byEngineer.get([jan,eng,cl].join('¦'))||0;
      const c=document.createElement('td');c.className='ebk-prior-mandays';c.textContent=fmt(v);tr.insertBefore(c,tr.cells[insertAt]||null);
    });
  }
  function render(){
    if(document.body.dataset.reportView!=='ekbagiya')return;
    if(!liveSnapshot){summary.textContent=loadError?'आज उपलब्ध सत्यापित KPI विवरण लोड नहीं हुआ। पेज रिफ्रेश करें।':'सत्यापित कार्य एवं मानव दिवस लोड हो रहे हैं…';grid.innerHTML='';return}
    panel.querySelector('.ebk-head p').textContent='एक बगिया माँ के नाम — रिपोर्ट दिनांक '+liveSnapshot.retrievedDate+' • MGNREGA स्रोत '+liveSnapshot.sourceDates.MGNREGA+' • VB G RAM G स्रोत '+liveSnapshot.sourceDates.VBGRAMG;
    const rows=filteredWorks();
    if(!rows.length){summary.textContent='चयनित filter में Report Card data उपलब्ध नहीं है।';grid.innerHTML='<div class="ebk-empty">कोई KPI कार्ड नहीं मिला।</div>';return}
    const groups=new Map();
    rows.forEach(r=>{
      const key=[clean(r.Janpad),clean(r.Upyantri),clean(r.Cluster)].join('¦');
      if(!groups.has(key))groups.set(key,{janpad:r.Janpad,engineer:r.Upyantri||'Unmapped',cluster:r.Cluster||'Unmapped',works:0,active:0,nil:0,beforeMandays:0,aprJunMandays:0,julyMandays:0,mandays:0,sanction:0,sanctionWage:0,sanctionMaterial:0,bookedWage:0,bookedMaterial:0,booked:0,paidWage:0,paidMaterial:0,portals:{MGNREGA:{bw:0,bm:0,pw:0,pm:0,mandaysTotal:0,mandaysCurrentFY:0},VBGRAMG:{bw:0,bm:0,pw:0,pm:0,mandaysTotal:0,mandaysCurrentFY:0}},gps:new Set()});
      const x=groups.get(key),md=mandaysOf(r),currentMandays=md.july;
      x.paidWage+=num(r.paidWage);x.paidMaterial+=num(r.paidMaterial);for(const system of ['MGNREGA','VBGRAMG'])for(const k of ['bw','bm','pw','pm','mandaysTotal','mandaysCurrentFY'])x.portals[system][k]+=num(r.sources?.[system]?.[k==='bw'?'bsw':k==='bm'?'bsm':k]);
      if(clean(r['Work Status']).toLowerCase()==='ongoing')x.works++;
      if(num(r['Overall Total Booked'])>0)x.active++;else x.nil++;
      x.beforeMandays+=md.before;x.aprJunMandays+=md.aprJun;x.julyMandays+=md.july;x.mandays+=md.total;x.sanction+=num(r['Sanction Amount Total']);x.sanctionWage+=num(r.sanctionWage);x.sanctionMaterial+=num(r.sanctionMaterial);x.bookedWage+=num(r['Overall Booked Wages']);x.bookedMaterial+=num(r['Overall Booked Material']);x.booked+=num(r['Overall Total Booked']);x.gps.add(gpKey(r.Janpad,r['Panchayat Name']));
    });
    let cards=[...groups.values()].map(x=>{x.expPct=x.sanction?100*x.booked/x.sanction:0;x.nilPct=(x.active+x.nil)?100*x.nil/(x.active+x.nil):0;x.status=(x.mandays===0||x.nilPct>=75||x.expPct<5)?'poor':(x.nilPct>=40||x.expPct<15?'watch':'good');return x});
    cards=cards.filter(x=>(statusFilter.value==='ALL'||x.status===statusFilter.value)&&(issueFilter.value==='ALL'||issueFilter.value==='zeroMandays'&&x.mandays===0||issueFilter.value==='nilWorks'&&x.nil>0||issueFilter.value==='lowExp'&&x.expPct<15)).sort((a,b)=>({poor:0,watch:1,good:2}[a.status]-{poor:0,watch:1,good:2}[b.status])||b.nilPct-a.nilPct||a.janpad.localeCompare(b.janpad)||a.engineer.localeCompare(b.engineer,'hi'));
    const count={poor:0,watch:0,good:0};cards.forEach(x=>count[x.status]++);summary.textContent=`${cards.length} उपयंत्री–क्लस्टर • खराब ${count.poor} • सुधार आवश्यक ${count.watch} • अच्छी प्रगति ${count.good} • ${fmt(rows.length)} प्रगतिरत कार्य • कुल मानव दिवस ${fmt(rows.reduce((n,r)=>n+mandaysOf(r).total,0))}`;
    if(!cards.length){grid.innerHTML='<div class="ebk-empty">चयनित filter में कोई KPI कार्ड नहीं मिला।</div>';return}
    grid.innerHTML=cards.map(x=>{const label=x.status==='poor'?'खराब प्रगति':x.status==='watch'?'सुधार आवश्यक':'अच्छी प्रगति';return `<article class="ebk-card ${x.status}"><div class="ebk-top"><div><div class="ebk-name">${esc(x.engineer)}</div><div class="ebk-place">${esc(x.janpad)} • ${esc(x.cluster)} • ${fmt(x.gps.size)} GP</div></div><span class="ebk-badge">${label}</span></div><table class="ebk-detail-table"><tbody>${[['Ongoing कार्य',fmt(x.works)],['Total Mandays Generated',fmt(x.mandays)],['Active कार्य',fmt(x.active)],['NIL कार्य',fmt(x.nil)],['व्यय प्रगति',x.expPct.toFixed(1)+'%']].map(([label,value])=>'<tr><th scope="row">'+label+'</th><td>'+value+'</td></tr>').join('')}</tbody></table>${['BOTH'].map(system=>{const p=Object.fromEntries(['bw','bm','pw','pm','mandaysTotal','mandaysCurrentFY'].map(k=>[k,num(x.portals.MGNREGA[k])+num(x.portals.VBGRAMG[k])]));return '<div style="margin-top:10px;font-weight:900">'+'MGNREGA + VB G RAM G'+' • FY 2025–26 + 2026–27</div><table class="ebk-detail-table"><thead><tr><th>विवरण</th><th>राशि ₹ लाख</th></tr></thead><tbody>'+[['कुल स्वीकृति राशि',x.sanction],['मजदूरी स्वीकृति',x.sanctionWage],['सामग्री स्वीकृति',x.sanctionMaterial],['Booked Wage',p.bw],['Booked Material',p.bm],['Total Booked',p.bw+p.bm],['Paid Since Wage',p.pw],['Paid Since Material',p.pm],['Total Paid Since',p.pw+p.pm],['Pending Wage',p.bw-p.pw],['Pending Material',p.bm-p.pm],['Total Pending',p.bw+p.bm-p.pw-p.pm]].map(([label,value])=>'<tr><th scope="row">'+label+'</th><td>'+lakh(value)+'</td></tr>').join('')+'</tbody></table><table class="ebk-detail-table"><tbody><tr><th scope="row">Mandays Since Inception</th><td>'+fmt(x.mandays)+'</td></tr><tr><th scope="row">Current FY Mandays</th><td>'+fmt(p.mandaysCurrentFY)+'</td></tr></tbody></table>';}).join('')}${x.status==='poor'?'<div class="ebk-alert">⚠ प्राथमिक समीक्षा आवश्यक</div>':''}</article>`}).join('');
  }
  document.getElementById('ebkPrintCards').addEventListener('click',()=>{
    render();
    if(!liveSnapshot||!grid.querySelector('.ebk-card')){alert('प्रिंट के लिए KPI कार्ड उपलब्ध नहीं हैं।');return}
    const frame=document.createElement('iframe');
    frame.setAttribute('title','उपयंत्री–क्लस्टर KPI कार्ड प्रिंट');
    frame.style.cssText='position:fixed;width:1px;height:1px;bottom:0;left:0;border:0';
    document.body.appendChild(frame);
    const doc=frame.contentDocument;
    const selection=filters.map(el=>el.value==='ALL'?'':clean(el.options[el.selectedIndex]?.text)).filter(Boolean).join(' • ');
    doc.open();
    doc.write('<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>उपयंत्री–क्लस्टर KPI कार्ड</title><style>'+
      style.textContent+
      '@page{size:A4 landscape;margin:10mm}body{margin:0;font-family:Arial,sans-serif;color:#173f35}h1{font-size:20px;text-align:center;margin:0 0 4px}.print-meta{text-align:center;font-size:12px;margin:0 0 8px}.ebk-grid{display:grid!important;grid-template-columns:repeat(3,minmax(0,1fr))!important;gap:8px!important}.ebk-card{break-inside:avoid;page-break-inside:avoid}.ebk-detail-table th{font-size:11px!important}.ebk-detail-table td{font-size:17px!important}.ebk-name{font-size:17px!important}.ebk-place{font-size:11px!important}</style></head><body><h1>उपयंत्री–क्लस्टर KPI कार्ड</h1><p class="print-meta">'+esc(panel.querySelector('.ebk-head p').textContent)+'</p><p class="print-meta">'+esc(selection)+(selection?' • ':'')+esc(document.getElementById('ebkFY').selectedOptions[0].textContent)+'</p><p class="print-meta">'+esc(summary.textContent)+'</p><div class="ebk-grid">'+grid.innerHTML+'</div></body></html>');
    doc.close();
    const cleanup=()=>{if(frame.isConnected)frame.remove()};
    frame.contentWindow.addEventListener('afterprint',cleanup,{once:true});
    setTimeout(()=>{try{frame.contentWindow.focus();frame.contentWindow.print()}catch(e){cleanup();alert('प्रिंट शुरू नहीं हुआ। दोबारा प्रयास करें।')}},300);
  });
  document.getElementById('ebkFY').addEventListener('change',render);statusFilter.addEventListener('change',render);issueFilter.addEventListener('change',render);filters.forEach(x=>x.addEventListener('change',()=>setTimeout(render,0)));
  new MutationObserver(render).observe(document.body,{attributes:true,attributeFilter:['data-report-view']});
  render();
  fetch('data/ek-bagiya-payment-latest.json?live='+Date.now(),{cache:'no-store'}).then(r=>{if(!r.ok)throw Error('Source unavailable');return r.json()}).then(d=>{
    if(d.logicVersion!=='sabhi-reports-logic-v1'||!d.retrievedDate||!d.sourceDates||!Array.isArray(d.works)||!d.works.length)throw Error('Incomplete KPI source');
    if(d.works.some(w=>!w.engineer||!w.cluster||!Number.isFinite(w.julyMandays)||!Number.isFinite(w.nregaTotalMandays)||!Number.isFinite(w.nregaAprJunMandays)))throw Error('Incomplete KPI work mapping/mandays');
    liveSnapshot=d;window.EK_BAGIYA_VERIFIED_REPORT=d;
    if(typeof syncVerifiedEkBagiyaWorkData==='function')syncVerifiedEkBagiyaWorkData();
    if(typeof window.render==='function')window.render();
    render();
  }).catch(()=>{loadError=true;render()});
})();
