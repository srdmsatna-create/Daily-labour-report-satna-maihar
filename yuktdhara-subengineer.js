(function(){
'use strict';
const D=window.YUKTDHARA_DATA,root=document.getElementById('yuktdharaSubEngineerApp');if(!D||!root)return;
const outer=document.getElementById('yuktdharaMonitoring'),outerHead=outer&&outer.querySelector(':scope > div:first-child');
if(outerHead){const meta=outerHead.querySelector('small'),badge=outerHead.querySelector('span');if(meta)meta.textContent=`Bhuvan NRSC • SATNA (5 Janpad) + MAIHAR (3 Janpad) • Live status ${D.asOf||''}`;if(badge)badge.textContent=`${Number((D.counts||{}).master||0).toLocaleString('en-IN')} GP`;}
const M=new Set(['AMARPATAN','MAIHAR','RAMNAGAR']),S=new Set(['MAJHGAWAN','NAGOD','RAMPUR BAGHELAN','SATNA','UNCHAHARA']);
const $=id=>document.getElementById(id),e=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c])),n=v=>String(v??'').trim().toUpperCase().replace(/[^A-Z0-9\u0900-\u097F]+/g,''),nj=v=>n(v)==='RAMPORBAGHELAN'?'RAMPURBAGHELAN':n(v),key=(j,g)=>nj(j)+'|'+n(g),district=j=>M.has(j)?'MAIHAR':S.has(j)?'SATNA':'OTHER',jp=j=>j==='SATNA'?'SOHAWAL':j,fmt=v=>Number(v||0).toLocaleString('en-IN');
const lists=D.lists||{},mm=new Map((D.mapping||[]).map(x=>[key(x.janpad,x.gp),x])),sets={};Object.entries(lists).forEach(([k,v])=>sets[k]=new Set((v||[]).map(x=>key(x.janpad,x.gp))));
['started','submitted','notStarted','gasApproved'].forEach(k=>sets[k]||(sets[k]=new Set()));
const rows=(lists.master||[]).map(x=>{const m=mm.get(key(x.janpad,x.gp))||{},j=String(x.janpad).trim().toUpperCase(),id=key(j,x.gp);return{district:district(j),janpad:j,gp:x.gp,engineer:m.engineer||'UNMAPPED',cluster:m.cluster||'',started:sets.started.has(id),submitted:sets.submitted.has(id),notStarted:sets.notStarted.has(id),gasApproved:sets.gasApproved.has(id)}});
const style=document.createElement('style');style.textContent=`
.yukt-se{margin-top:20px;padding-top:18px;border-top:2px dashed #cbb8eb}.yukt-se-head{display:flex;justify-content:space-between;gap:12px;align-items:center}.yukt-se-head h3{margin:0;color:#54299b;font-size:22px}.yukt-se-head p{margin:4px 0;color:#667085}.yukt-se-actions{display:flex;gap:8px}.yukt-se button{border:0;border-radius:9px;padding:9px 13px;background:#6f42c1;color:#fff;font-weight:800;cursor:pointer}.yukt-se-kpis{display:grid;grid-template-columns:repeat(5,1fr);gap:10px;margin:14px 0}.yukt-se-kpi{border:1px solid #dfd5ef;border-radius:12px;background:#faf8ff;padding:12px}.yukt-se-kpi small{display:block;color:#667085;font-weight:700}.yukt-se-kpi b{display:block;font-size:24px;color:#3f1b79;margin-top:3px}.yukt-se-filters{display:grid;grid-template-columns:repeat(4,1fr) auto;gap:9px;margin:12px 0}.yukt-se-filters label{font-size:12px;font-weight:800;color:#59677a}.yukt-se-filters select{display:block;width:100%;padding:9px;margin-top:4px;border:1px solid #cbbddd;border-radius:8px;background:#fff}.yukt-se-wrap{overflow:auto;border:1px solid #ddd2ed;border-radius:12px}.yukt-se-table{width:100%;min-width:1150px;border-collapse:collapse;font-size:12px}.yukt-se-table th{background:#54299b;color:#fff;padding:9px 7px;border:1px solid #7652b7}.yukt-se-table td{padding:8px 7px;border:1px solid #e2d9ef;vertical-align:top}.yukt-se-table td.num{text-align:center;font-weight:900}.yukt-se-table tbody tr:nth-child(even){background:#fbf9ff}.yukt-se details summary{cursor:pointer;color:#54299b;font-weight:800}.yukt-se-gps{max-height:180px;overflow:auto;margin-top:5px}.yukt-se-gp{padding:5px 6px;border-bottom:1px solid #eee}.yukt-se-tag{font-size:9px;background:#eee7fa;border-radius:10px;padding:2px 5px;margin-right:3px}.yukt-se-meta{margin:8px 0;color:#667085;font-size:12px}.yukt-se-source{float:right}.yukt-se-source a{color:#54299b;font-weight:800}@media(max-width:850px){.yukt-se-kpis{grid-template-columns:repeat(2,1fr)}.yukt-se-filters{grid-template-columns:1fr 1fr}.yukt-se-head{align-items:flex-start;flex-direction:column}}@media print{.yukt-se-actions,.yukt-se-filters{display:none!important}.yukt-se-table{min-width:0;font-size:8px}.yukt-se-wrap{overflow:visible}}

/* Consistent borders and status colours for screen and print. */
#yuktdharaSubEngineerApp .yukt-se-wrap{border:2px solid #39205e}
#yuktdharaSubEngineerApp .yukt-se-table{border:2px solid #39205e}
#yuktdharaSubEngineerApp .yukt-se-table th,#yuktdharaSubEngineerApp .yukt-se-table td{border:1.5px solid #57406f}
#yuktdharaSubEngineerApp .yukt-se-kpi{border:1.5px solid #57406f}
#yuktdharaSubEngineerApp .yukt-started{color:#087538!important;font-weight:900!important}
#yuktdharaSubEngineerApp .yukt-not-started{color:#c01823!important;font-weight:900!important}
#yuktdharaSubEngineerApp th.yukt-started{background:#075d36!important;color:#fff!important}
#yuktdharaSubEngineerApp th.yukt-not-started{background:#a51722!important;color:#fff!important}
#yuktdharaSubEngineerApp .yukt-se-kpi:nth-child(2) small,#yuktdharaSubEngineerApp .yukt-se-kpi:nth-child(2) b{color:#087538!important;font-weight:900}
#yuktdharaSubEngineerApp .yukt-se-kpi:nth-child(4) small,#yuktdharaSubEngineerApp .yukt-se-kpi:nth-child(4) b{color:#c01823!important;font-weight:900}
@media print{#yuktdharaSubEngineerApp *{-webkit-print-color-adjust:exact;print-color-adjust:exact}}

#yuktdharaSubEngineerApp .yukt-se-wrap{border-radius:0}
#yuktdharaSubEngineerApp .yukt-se-table{table-layout:fixed;min-width:1100px;font-size:14px}
#yuktdharaSubEngineerApp .yukt-se-table th{line-height:1.35;padding:8px 4px}
#yuktdharaSubEngineerApp .yukt-se-table td{line-height:1.35;padding:7px 5px;overflow-wrap:break-word}
#yuktdharaSubEngineerApp .yukt-se-table td.num{font-size:17px;white-space:nowrap;vertical-align:middle}
#yuktdharaSubEngineerApp .yukt-se-table th:nth-child(1){width:7%}
#yuktdharaSubEngineerApp .yukt-se-table th:nth-child(2){width:13%}
#yuktdharaSubEngineerApp .yukt-se-table th:nth-child(3){width:16%}
#yuktdharaSubEngineerApp .yukt-se-table th:nth-child(4){width:16%}
#yuktdharaSubEngineerApp .yukt-se-table th:nth-child(n+5):nth-child(-n+9){width:7%}
#yuktdharaSubEngineerApp .yukt-se-table th:nth-child(10){width:13%}

#yuktdharaSubEngineerApp .yukt-se-table .yse-sort{display:block;width:100%;border:0;border-radius:0;padding:0;background:transparent;color:inherit;font:inherit;font-weight:800;line-height:inherit;text-align:center}
#yuktdharaSubEngineerApp .yse-sort:focus-visible{outline:2px solid white;outline-offset:2px}

#yuktdharaSubEngineerApp .yukt-se-table th:nth-child(2){width:15%}
#yuktdharaSubEngineerApp .yukt-se-table th:nth-child(4){width:14%}
#yuktdharaSubEngineerApp .yukt-se-table td:nth-child(2){white-space:nowrap;font-size:13px}
#yuktdharaSubEngineerApp .yukt-se-table .yse-total td{font-weight:900;border-top:2px solid #39205e}
#yuktdharaSubEngineerApp .yse-total-janpad{background:#e9ddfb!important}
#yuktdharaSubEngineerApp .yse-total-district{background:#d5c2f0!important}
#yuktdharaSubEngineerApp .yse-total-grand{background:#39205e!important;color:#fff}
#yuktdharaSubEngineerApp .yse-total-grand .yukt-started,#yuktdharaSubEngineerApp .yse-total-grand .yukt-not-started{color:#fff!important}

#yuktdharaSubEngineerApp .yukt-se-table td:nth-child(4){font-size:12px!important;line-height:1.25!important}

/* Apply compact cluster type in both embedded and standalone report views. */
@media screen {
body:not(#srdm-font-reserved-a):not(#srdm-font-reserved-b):not(#srdm-font-reserved-c) table.yukt-se-table tbody td:nth-child(4){
font-size:12px!important;line-height:1.2!important;font-weight:500!important;padding:5px!important;
}
body:not(#srdm-font-reserved-a):not(#srdm-font-reserved-b):not(#srdm-font-reserved-c) table.yukt-se-table thead th:nth-child(4),
body:not(#srdm-font-reserved-a):not(#srdm-font-reserved-b):not(#srdm-font-reserved-c) table.yukt-se-table thead th:nth-child(4) button,
body:not(#srdm-font-reserved-a):not(#srdm-font-reserved-b):not(#srdm-font-reserved-c) table.yukt-se-table thead th:nth-child(4) span{
font-size:13px!important;line-height:1.2!important;
}
}
`;document.head.appendChild(style);
root.innerHTML=`<div class="yukt-se"><div class="yukt-se-head"><div><h3>Bhuvan Yuktdhara — Sub Engineer-wise</h3><p>District Satna (5 Janpad) • District Maihar (3 Janpad) • ${e(D.asOf)}</p></div><div class="yukt-se-actions"><button id="yseExcel">Excel Download</button><button id="ysePrint">Print / PDF</button></div></div><div id="yseKpis" class="yukt-se-kpis"></div><div class="yukt-se-filters"><label>District<select id="yseDistrict"><option value="ALL">Satna + Maihar</option><option>SATNA</option><option>MAIHAR</option></select></label><label>Janpad<select id="yseJanpad"><option value="ALL">सभी Janpad</option></select></label><label>Sub Engineer<select id="yseEngineer"><option value="ALL">सभी Sub Engineer</option></select></label><label>Status<select id="yseStatus"><option value="ALL">सभी GP</option><option value="started">Plan Started</option><option value="submitted">Plan Submitted</option><option value="notStarted">Plan Not Started</option><option value="gasApproved">GAS Approved</option></select></label><button id="yseReset">Reset</button></div><div class="yukt-se-meta"><b id="yseMeta"></b><span class="yukt-se-source">Source: <a href="${e(D.officialUrl)}" target="_blank" rel="noopener">Bhuvan NRSC</a></span></div><div class="yukt-se-wrap"><table class="yukt-se-table" id="yseTable"></table></div></div>`;
function vals(a,k){return[...new Set(a.map(x=>x[k]).filter(Boolean))].sort((a,b)=>a.localeCompare(b,'hi'))}function opts(el,a,label,display){const cur=el.value;el.innerHTML=`<option value="ALL">${label}</option>`+a.map(v=>`<option value="${e(v)}">${e(display?display(v):v)}</option>`).join('');if([...el.options].some(o=>o.value===cur))el.value=cur}
function cascade(){let a=rows;if($('yseDistrict').value!=='ALL')a=a.filter(x=>x.district===$('yseDistrict').value);opts($('yseJanpad'),vals(a,'janpad'),'सभी Janpad',jp);if($('yseJanpad').value!=='ALL')a=a.filter(x=>x.janpad===$('yseJanpad').value);opts($('yseEngineer'),vals(a,'engineer'),'सभी Sub Engineer')}
function filtered(){const d=$('yseDistrict').value,j=$('yseJanpad').value,se=$('yseEngineer').value,st=$('yseStatus').value;return rows.filter(x=>(d==='ALL'||x.district===d)&&(j==='ALL'||x.janpad===j)&&(se==='ALL'||x.engineer===se)&&(st==='ALL'||x[st]))}
function group(a){const m=new Map();a.forEach(x=>{const k=[x.district,x.janpad,x.engineer].join('|');if(!m.has(k))m.set(k,{district:x.district,janpad:x.janpad,engineer:x.engineer,clusters:new Set(),gps:[]});const g=m.get(k);if(x.cluster)g.clusters.add(x.cluster);g.gps.push(x)});return[...m.values()].map(g=>({...g,cluster:[...g.clusters].sort().join(', '),total:g.gps.length,started:g.gps.filter(x=>x.started).length,submitted:g.gps.filter(x=>x.submitted).length,notStarted:g.gps.filter(x=>x.notStarted).length,gasApproved:g.gps.filter(x=>x.gasApproved).length})).sort((a,b)=>a.district.localeCompare(b.district)||a.janpad.localeCompare(b.janpad)||a.engineer.localeCompare(b.engineer,'hi'))}
function names(g){return`<details><summary>${fmt(g.gps.length)} GP नाम</summary><div class="yukt-se-gps">${g.gps.sort((a,b)=>a.gp.localeCompare(b.gp)).map(x=>`<div class="yukt-se-gp"><b>${e(x.gp)}</b><br>${x.started?'<span class="yukt-se-tag yukt-started">Started</span>':''}${x.submitted?'<span class="yukt-se-tag">Submitted</span>':''}${x.notStarted?'<span class="yukt-se-tag yukt-not-started">Not Started</span>':''}${x.gasApproved?'<span class="yukt-se-tag">GAS Approved</span>':''}</div>`).join('')}</div></details>`}
let sortKey=null,sortDirection=1;
const sortColumns=[['district','District'],['janpad','Janpad'],['engineer','Sub Engineer'],['cluster','Cluster(s)'],['total','कुल GP'],['started','Started'],['submitted','Submitted'],['notStarted','Not Started'],['gasApproved','GAS Approved']];
function sortHeader(key,label){const arrow=sortKey===key?(sortDirection===1?'↑':'↓'):'↕';return '<button type="button" class="yse-sort" data-sort="'+key+'" aria-label="'+e(label)+' — '+(sortKey===key?(sortDirection===1?'आरोही':'अवरोही'):'क्रम बदलें')+'">'+e(label)+' <span aria-hidden="true">'+arrow+'</span></button>'}
function reportRows(groups){
 const out=[],metrics=['total','started','submitted','notStarted','gasApproved'];
 function total(items,d,j,label,kind){const r={district:d,janpad:j,engineer:label,cluster:'',gps:[],totalKind:kind};for(const k of metrics)r[k]=items.reduce((v,x)=>v+x[k],0);return r}
 const districts=[...new Set(groups.map(r=>r.district))].sort();
 for(const d of districts){const dg=groups.filter(r=>r.district===d);for(const j of [...new Set(dg.map(r=>r.janpad))].sort()){const jg=dg.filter(r=>r.janpad===j);out.push(...jg,total(jg,d,j,'जनपद योग','janpad'))}out.push(total(dg,d,'','जिला योग','district'))}
 if(groups.length)out.push(total(groups,'','','Grand Total','grand'));
 return out;
}
function draw(){const a=filtered(),g=group(a);if(sortKey)g.sort((x,y)=>{const av=x[sortKey],bv=y[sortKey];const cmp=typeof av==='number'?av-bv:String(av).localeCompare(String(bv),'hi',{numeric:true});return cmp*sortDirection||x.janpad.localeCompare(y.janpad)||x.engineer.localeCompare(y.engineer,'hi')});const c=k=>a.filter(x=>x[k]).length;$('yseKpis').innerHTML=[['कुल GP',a.length],['Plan Started',c('started')],['Plan Submitted',c('submitted')],['Plan Not Started',c('notStarted')],['GAS Approved',c('gasApproved')]].map(x=>`<div class="yukt-se-kpi"><small>${x[0]}</small><b>${fmt(x[1])}</b></div>`).join('');$('yseMeta').textContent=`${g.length} Sub Engineer rows • ${a.length} GP`;$('yseTable').innerHTML=`<thead><tr>${sortColumns.map(([key,label])=>'<th'+(key==='started'?' class="yukt-started"':key==='notStarted'?' class="yukt-not-started"':'')+' aria-sort="'+(sortKey===key?(sortDirection===1?'ascending':'descending'):'none')+'">'+sortHeader(key,label)+'</th>').join('')}<th>संबंधित GP नाम</th></tr></thead><tbody>${reportRows(g).map(x=>`<tr${x.totalKind?' class="yse-total yse-total-'+x.totalKind+'"':''}><td><b>${x.district}</b></td><td>${jp(x.janpad)}</td><td><b>${e(x.engineer)}</b></td><td><b>${e(x.cluster)}</b></td><td class="num">${x.total}</td><td class="num yukt-started">${x.started}</td><td class="num">${x.submitted}</td><td class="num yukt-not-started">${x.notStarted}</td><td class="num">${x.gasApproved}</td><td>${x.totalKind?'':names(x)}</td></tr>`).join('')}</tbody>`;window.__YSE={a,g:reportRows(g)}}
$('yseTable').addEventListener('click',event=>{const button=event.target.closest('button[data-sort]');if(!button)return;const key=button.dataset.sort;if(sortKey===key)sortDirection*=-1;else{sortKey=key;sortDirection=1}draw()});
function printReport(){
const copy=$('yseTable').cloneNode(true);
copy.querySelectorAll('.yse-sort').forEach(b=>b.replaceWith(document.createTextNode(b.textContent)));
copy.querySelectorAll('details').forEach(d=>{const summary=d.querySelector('summary');d.replaceWith(document.createTextNode(summary?summary.textContent:''))});
const allRows=[...copy.tBodies[0].rows],pageCount=Math.min(3,Math.max(1,Math.ceil(allRows.length/26)));
const perPage=Math.ceil(allRows.length/pageCount),pages=[];
const widths=[7,13,16,13,6,6,7,8,8,16];
for(let i=0;i<pageCount;i++){
 const table=copy.cloneNode(true);table.tBodies[0].replaceChildren(...allRows.slice(i*perPage,(i+1)*perPage).map(r=>r.cloneNode(true)));
 table.insertAdjacentHTML('afterbegin','<colgroup>'+widths.map(w=>'<col style="width:'+w+'%">').join('')+'</colgroup>');
 pages.push('<section class="yse-print-page"><div class="yse-page-content"><h2>Yuktdhara Monitoring Report — उपयंत्रीवार रिपोर्ट</h2><p class="meta">'+e(D.asOf)+' • '+e($('yseMeta').textContent)+' • जिला: '+e($('yseDistrict').selectedOptions[0].textContent)+' • जनपद: '+e($('yseJanpad').selectedOptions[0].textContent)+' • पृष्ठ '+(i+1)+'/'+pageCount+'</p>'+table.outerHTML+'</div></section>');
}
const frame=document.createElement('iframe');frame.style.cssText='position:fixed;left:-12000px;top:0;width:1100px;height:800px;border:0';document.body.appendChild(frame);
const doc=frame.contentDocument;
const css='@page{size:A4 landscape;margin:6mm}*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}body{margin:0;font-family:"Nirmala UI",Mangal,Arial,sans-serif;color:#152238}.yse-print-page{break-after:page;page-break-after:always}.yse-print-page:last-child{break-after:auto;page-break-after:auto}h2{font-size:13pt;margin:0 0 1.5mm}.meta{font-size:8pt;margin:0 0 2mm}table{width:100%;table-layout:fixed;border-collapse:collapse;border:.4mm solid #39205e}thead{display:table-header-group}tr{break-inside:avoid;page-break-inside:avoid}th,td{border:.3mm solid #57406f;padding:1mm .8mm;line-height:1.2;overflow-wrap:break-word;vertical-align:middle;font-size:8.5pt}th{background:#54299b;color:#fff;font-weight:800}td.num{text-align:center;font-weight:900;font-size:10pt;white-space:nowrap}tbody tr:nth-child(even){background:#f7f3fc}td:nth-child(2){font-size:8pt}td:nth-child(4){font-size:8pt;line-height:1.2;font-weight:800}.yse-total td{font-weight:900;border-top:.5mm solid #39205e}.yse-total-janpad{background:#e9ddfb!important}.yse-total-district{background:#d5c2f0!important}.yse-total-grand{background:#39205e!important;color:white}.yse-total-grand .yukt-started,.yse-total-grand .yukt-not-started{color:white}.yukt-started{color:#087538;font-weight:900}.yukt-not-started{color:#c01823;font-weight:900}th.yukt-started{background:#075d36;color:#fff}th.yukt-not-started{background:#a51722;color:#fff}';
doc.open();doc.write('<!doctype html><html><head><meta charset="utf-8"><title>Yuktdhara Monitoring Report</title><style>'+css+'</style></head><body>'+pages.join('')+'</body></html>');doc.close();
frame.contentWindow.onafterprint=()=>setTimeout(()=>frame.remove(),1000);
Promise.resolve(doc.fonts?.ready).then(()=>setTimeout(()=>{
 // Each section has its own heading and fits the printable A4 landscape area.
 const availableHeight=196*96/25.4;
 doc.querySelectorAll('.yse-page-content').forEach(el=>{const height=el.getBoundingClientRect().height;if(height>availableHeight)el.style.zoom=String(availableHeight/height);});
 frame.contentWindow.focus();frame.contentWindow.print();
},300));
}
function excel(){const q=window.__YSE||{a:filtered(),g:group(filtered())},sum=q.g.map(x=>({'District':x.district,'Janpad':jp(x.janpad),'Sub Engineer':x.engineer,'Cluster(s)':x.cluster,'कुल GP':x.total,'Plan Started':x.started,'Plan Submitted':x.submitted,'Plan Not Started':x.notStarted,'GAS Approved':x.gasApproved,'GP Names':x.gps.map(y=>y.gp).sort().join(', ')})),det=q.a.map(x=>({'District':x.district,'Janpad':jp(x.janpad),'Sub Engineer':x.engineer,'Cluster':x.cluster,'GP Name':x.gp,'Started':x.started?'Yes':'No','Submitted':x.submitted?'Yes':'No','Not Started':x.notStarted?'Yes':'No','GAS Approved':x.gasApproved?'Yes':'No'}));if(window.XLSX){const b=XLSX.utils.book_new();XLSX.utils.book_append_sheet(b,XLSX.utils.json_to_sheet(sum),'Sub Engineer Summary');XLSX.utils.book_append_sheet(b,XLSX.utils.json_to_sheet(det),'GP Detail');XLSX.writeFile(b,'Bhuvan_Yuktdhara_Sub_Engineer_02-09-2026.xlsx');return}alert('Excel library load नहीं हुई। Internet connection के साथ पुनः प्रयास करें।')}
['yseDistrict','yseJanpad','yseEngineer','yseStatus'].forEach(id=>$(id).addEventListener('change',()=>{if(id!=='yseStatus')cascade();draw()}));$('yseReset').onclick=()=>{$('yseDistrict').value='ALL';$('yseJanpad').value='ALL';$('yseEngineer').value='ALL';$('yseStatus').value='ALL';cascade();draw()};$('yseExcel').onclick=excel;$('ysePrint').onclick=printReport;cascade();draw();
})();
