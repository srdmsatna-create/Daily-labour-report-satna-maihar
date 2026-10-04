(function(){
const mergedCategory=t=>['IAY Houses','PMAY G','PMAY-G'].includes(String(t).trim())?'PMAY-G':t;
const title='उपयंत्री/सेक्टरवार कार्य-श्रेणीवार — प्रगतिरत कार्य, MR जारी कार्य एवं संलग्न श्रमिक';
let box;
function draw(){
 if(!box){box=document.createElement('section');box.id='gpLabourMusterModule';box.style.cssText='margin:16px 0;padding:16px;border:2px solid #14588c;border-radius:12px;background:#fff;color:#102b46';document.getElementById('reportTable').parentElement.insertAdjacentElement('afterend',box);}
 box.hidden=view!=='official';if(box.hidden)return;
 const live=window.GP_WORK_TYPE_MUSTER_REPORT;
 const sourceData=live&&Array.isArray(live.rows)?filterRows(live.rows):filteredRows();
 const data=sortRows(sourceData,'labour',['janpad','panchayat']);
 const date=live?.date||autoMeta?.sourceDates?.RepDay||extractDate(reportTitle)||'तिथि उपलब्ध नहीं';
 const bands=[[0,0,'शून्य'],[1,1,'01'],[2,2,'02'],[3,3,'03'],[4,4,'04'],[5,5,'05'],[6,10,'06 से 10'],[11,20,'11 से 20'],[21,30,'21 से 30'],[31,50,'31 से 50'],[51,100,'51 से 100'],[101,Infinity,'100 से अधिक']];
 const workTypes=[...new Set(['Amrit Sarovar',...(live?.workCategories||[]).map(mergedCategory),...ongoingDetails.map(r=>mergedCategory(r.finalCategory||'Other Works'))])].sort((a,b)=>a.localeCompare(b,'en'));
 if(!workTypes.length)workTypes.push('PMAY-G','Cement Concrete','Gravel Road','Play Field','Farm Pond','Watershed Related Works','Water conservation & recharge','Ek Bagiya','Gap Filling in Plantation','Other Works');
 // Count issued-MR works from column 6 drill-down by work type; do not use muster roll totals.
 const source=window.GP_WORK_TYPE_MUSTER_REPORT;
 const sourceRows=source&&Array.isArray(source.rows)?source.rows:[];
 const gpKey=r=>normJanpad(r.janpad)+'¦'+clean(r.panchayat).toUpperCase().replace(/[^A-Z0-9\u0900-\u097f]/g,'');
 const officialWorkCounts=new Map(sourceRows.map(r=>[gpKey(r),r]));
 const ongoingByGP=new Map(),ongoingTypesByGP=new Map(),seenOngoingCodes=new Set();
 for(const work of ongoingDetails){
  if(!work.code||seenOngoingCodes.has(work.code))continue;
  seenOngoingCodes.add(work.code);
  const k=gpKey(work);ongoingByGP.set(k,(ongoingByGP.get(k)||0)+1);
  if(!ongoingTypesByGP.has(k))ongoingTypesByGP.set(k,{});const types=ongoingTypesByGP.get(k);const type=mergedCategory(work.finalCategory||work.category||'Other Works');types[type]=(types[type]||0)+1;
 }
 const groups=new Map(),seen=new Set();
 for(const r of data){
 const key=normJanpad(r.janpad)+'¦'+clean(r.panchayat).toUpperCase();
 if(seen.has(key))continue;seen.add(key);
 const j=normJanpad(r.janpad);
 const engineer=clean(r.engineer)||'नाम उपलब्ध नहीं',sector=clean(r.cluster)||'सेक्टर उपलब्ध नहीं';
 const groupKey=[j,engineer,sector].join('¦');
 if(!groups.has(groupKey))groups.set(groupKey,{janpad:j,engineer,sector,total:0,ongoing:0,issuedTotal:0,issuedMissing:false,workingGP:0,counts:bands.map(()=>0),missing:0,ongoingCounts:workTypes.map(()=>0),workCounts:workTypes.map(()=>0),workMissing:workTypes.map(()=>false)});
 const g=groups.get(groupKey);g.total++;g.ongoing+=ongoingByGP.get(gpKey(r))||0;
 const workRow=officialWorkCounts.get(gpKey(r));
 const issuedCount=workRow?.worksMR;
 if(issuedCount===null||issuedCount===undefined||!Number.isInteger(Number(issuedCount))||Number(issuedCount)<0)g.issuedMissing=true;
 else g.issuedTotal+=Number(issuedCount);
 workTypes.forEach((type,i)=>{
 g.ongoingCounts[i]+=ongoingTypesByGP.get(gpKey(r))?.[type]||0;
 const raw=workRow?.issuedWorks;
 const v=type==='PMAY-G'&&raw?['PMAY-G','PMAY G','IAY Houses'].reduce((sum,k)=>sum+Number(raw[k]??0),0):raw?(raw[type]??0):undefined;
 if(v===null||v===undefined||v===''||!Number.isInteger(Number(v))||Number(v)<0)g.workMissing[i]=true;
 else g.workCounts[i]+=Number(v);
 });
 const n=r.labour===null||r.labour===undefined||clean(r.labour)===''?NaN:Number(r.labour);
 const bi=Number.isInteger(n)&&n>=0?bands.findIndex(b=>n>=b[0]&&n<=b[1]):-1;
 if(bi<0)g.missing++;else {g.counts[bi]++;if(n>0)g.workingGP++;}
 }
 const summary=[...groups.values()].sort((a,b)=>a.janpad.localeCompare(b.janpad,'hi')||a.engineer.localeCompare(b.engineer,'hi')||a.sector.localeCompare(b.sector,'hi'));
 const hasMissing=summary.some(g=>g.missing>0);
 const headers=['जनपद का नाम','उपयंत्री का नाम/सेक्टर का नाम','कुल प्रभार की ग्राम पंचायत','श्रमिक संलग्न GPs',...bands.map(b=>b[2]+' श्रमिक वाली GPs'),...(hasMissing?['श्रमिक डेटा अनुपलब्ध GPs']:[]),...workTypes.flatMap(t=>t==='Amrit Sarovar'?['मस्टर रोल जारी कार्यों की कुल संख्या / कुल प्रगतिरत कार्य',t]:[t])];
 let table='<table style="width:100%;border-collapse:collapse"><thead><tr>'+headers.map((x,i)=>'<th'+(i===2?' style="width:90px;min-width:90px;max-width:90px;white-space:normal"':'')+'>'+(i===2?'कुल प्रभार की<br>ग्राम पंचायत':esc(x))+'</th>').join('')+'</tr></thead><tbody>';
 const pair=(g,i)=>(g.workMissing[i]?'—':fmt(g.workCounts[i]))+' / '+fmt(g.ongoingCounts[i]);
 const cells=g=>[g.total,g.workingGP,...g.counts,...(hasMissing?[g.missing]:[])].map(v=>'<td style="font-weight:800;text-align:center">'+fmt(v)+'</td>').join('')+workTypes.map((type,i)=>(type==='Amrit Sarovar'?'<td style="font-weight:800;text-align:center;white-space:nowrap">'+(g.issuedMissing?'—':fmt(g.issuedTotal))+' / '+fmt(g.ongoing)+'</td>':'')+'<td style="font-weight:800;text-align:center">'+pair(g,i)+'</td>').join('');
 const janpads=[...new Set(summary.map(g=>g.janpad))];
 for(const janpad of janpads){
 const entries=summary.filter(g=>g.janpad===janpad);
 table+=entries.map(g=>'<tr>'+[g.janpad,g.engineer+' / '+g.sector].map(v=>'<td style="font-weight:800">'+esc(v)+'</td>').join('')+cells(g)+'</tr>').join('');
 const subtotal={total:entries.reduce((s,g)=>s+g.total,0),ongoing:entries.reduce((s,g)=>s+g.ongoing,0),issuedTotal:entries.reduce((s,g)=>s+g.issuedTotal,0),issuedMissing:entries.some(g=>g.issuedMissing),workingGP:entries.reduce((s,g)=>s+g.workingGP,0),counts:bands.map((b,i)=>entries.reduce((s,g)=>s+g.counts[i],0)),missing:entries.reduce((s,g)=>s+g.missing,0),ongoingCounts:workTypes.map((t,i)=>entries.reduce((s,g)=>s+g.ongoingCounts[i],0)),workCounts:workTypes.map((t,i)=>entries.reduce((s,g)=>s+g.workCounts[i],0)),workMissing:workTypes.map((t,i)=>entries.some(g=>g.workMissing[i]))};
 table+='<tr style="background:#dbeafe;font-weight:800"><td colspan="2">'+esc(janpad)+' — जनपद कुल</td>'+cells(subtotal)+'</tr>';
 }
 if(!summary.length)table+='<tr><td colspan="'+headers.length+'">चयन के लिए ग्राम पंचायत डेटा उपलब्ध नहीं है।</td></tr>';

 const grand={total:summary.reduce((s,g)=>s+g.total,0),workingGP:summary.reduce((s,g)=>s+g.workingGP,0),ongoing:summary.reduce((s,g)=>s+g.ongoing,0),issuedTotal:summary.reduce((s,g)=>s+g.issuedTotal,0),issuedMissing:summary.some(g=>g.issuedMissing),counts:bands.map((b,i)=>summary.reduce((s,g)=>s+g.counts[i],0)),missing:summary.reduce((s,g)=>s+g.missing,0),ongoingCounts:workTypes.map((t,i)=>summary.reduce((s,g)=>s+g.ongoingCounts[i],0)),workCounts:workTypes.map((t,i)=>summary.reduce((s,g)=>s+g.workCounts[i],0)),workMissing:workTypes.map((t,i)=>summary.some(g=>g.workMissing[i]))};
 table+='<tr style="background:#e5f0fa;font-weight:800"><td colspan="2">कुल</td>'+cells(grand)+'</tr></tbody></table>';
 const workSummary=new Map();
 const mapGP=new Map(data.map(r=>[gpKey(r),r]));
 const make=r=>{
 const master=mapGP.get(gpKey(r));if(!master)return null;
 const category=mergedCategory(r.finalCategory||r.category||'Other Works');
 const k=[normJanpad(master.janpad),clean(master.engineer),clean(master.cluster),category].join('¦');
 if(!workSummary.has(k))workSummary.set(k,{janpad:normJanpad(master.janpad),engineer:master.engineer,sector:master.cluster,category,ongoing:0,issued:0,labour:0,labourMissing:false});
 return workSummary.get(k);
 };
 const seenOngoing=new Set();
 for(const r of ongoingDetails){
 if(seenOngoing.has(r.code)||!r.code)continue;seenOngoing.add(r.code);
 const g=make(r);if(g)g.ongoing++;
 }
 const issued=live&&Array.isArray(live.works)?live.works:null,seenIssued=new Set();
 if(issued)for(const r of issued){
 if(seenIssued.has(r.code)||!r.code)continue;seenIssued.add(r.code);
 const g=make(r);if(!g)continue;g.issued++;
 if(r.labour===null||r.labour===undefined||r.labour===''||!Number.isFinite(Number(r.labour)))g.labourMissing=true;else g.labour+=Number(r.labour);
 }
 const summaryWorks=[...workSummary.values()].sort((a,b)=>a.janpad.localeCompare(b.janpad)||String(a.engineer).localeCompare(String(b.engineer),'hi')||String(a.sector).localeCompare(String(b.sector))||a.category.localeCompare(b.category));
 const workHeaders=['जनपद','उपयंत्री का नाम/सेक्टर का नाम','कार्य की श्रेणी','कुल प्रगतिरत कार्य','आज MR जारी वाले कार्य','संलग्न श्रमिक'];
 let workTable='<h3>उपयंत्री/सेक्टरवार कार्य-श्रेणीवार — प्रगतिरत कार्य, MR जारी कार्य एवं संलग्न श्रमिक</h3><p style="text-align:right;font-weight:800"><strong>दिनांक: '+esc(date)+'</strong></p><table style="width:100%;border-collapse:collapse"><thead><tr>'+workHeaders.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>';
 workTable+=summaryWorks.map(g=>'<tr>'+[g.janpad,g.engineer+' / '+g.sector,g.category].map(x=>'<td>'+esc(x)+'</td>').join('')+'<td>'+fmt(g.ongoing)+'</td><td>'+(issued?fmt(g.issued):'—')+'</td><td>'+(issued&&!g.labourMissing?fmt(g.labour):'—')+'</td></tr>').join('');
 workTable+='<tr style="background:#dbeafe;font-weight:800"><td colspan="3">कुल</td><td>'+fmt(summaryWorks.reduce((s,g)=>s+g.ongoing,0))+'</td><td>'+(issued?fmt(summaryWorks.reduce((s,g)=>s+g.issued,0)):'—')+'</td><td>'+(issued&&!summaryWorks.some(g=>g.labourMissing)?fmt(summaryWorks.reduce((s,g)=>s+g.labour,0)):'—')+'</td></tr></tbody></table>';
 const ongoingDates=[...new Set(ongoingDetails.map(r=>r.sourceDate).filter(Boolean))];
 workTable='<p>प्रगतिरत कार्य मास्टर की तिथि: '+esc(ongoingDates.join(', ')||'तिथि उपलब्ध नहीं')+' • MR/श्रमिक स्रोत: '+esc(live?.date||'अभी उपलब्ध नहीं')+'</p>'+workTable;
 const note='कार्य-प्रकार के प्रत्येक कॉलम में: मस्टर रोल जारी कार्यों की कुल संख्या / कुल प्रगतिरत कार्य • जनपद, उपयंत्री एवं क्लस्टर के ऊपर दिए फ़िल्टर लागू हैं।';
 box.innerHTML='<style>#gpLabourMusterModule table{font-size:14px;table-layout:auto}#gpLabourMusterModule th{white-space:normal!important;overflow-wrap:break-word;min-width:65px;max-width:140px;line-height:1.3}#gpLabourMusterModule th,#gpLabourMusterModule td{border:1px solid #7894ac;padding:7px}#gpLabourMusterModule table:first-of-type th:nth-child(3),#gpLabourMusterModule table:first-of-type td:nth-child(3){width:90px!important;min-width:90px!important;max-width:90px!important;white-space:normal!important;overflow-wrap:anywhere;padding:3px!important;text-align:center;font-size:14px;line-height:1.3}#gpLabourMusterModule th:nth-child(2),#gpLabourMusterModule td:nth-child(2){white-space:nowrap;width:1%;min-width:220px;text-align:left}#gpLabourMusterModule th{background:#14588c;color:white}#gpLabourMusterModule tbody tr:nth-child(even){background:#f0f6fb}@media print{#gpLabourMusterModule{display:none}}</style><h2 style="margin:0 0 8px">'+title+'</h2><p style="text-align:right;font-weight:800;margin:4px 0 10px"><strong>दिनांक: '+esc(date)+'</strong></p><p>'+esc(note)+'</p><p style="color:#9a3412">ग्राम पंचायत के उपलब्ध स्रोत आँकड़े दिखाए गए हैं; जनपद के अद्यतन कुल से इनका अंतर हो सकता है। कॉलम 6 से प्राप्त MR जारी वाले कार्यों की कार्य प्रकारवार संख्या दिखाई जाएगी। सत्यापित कार्य सूची उपलब्ध न होने पर — दिखाया गया है। CC Road और Gravel Road, Rural Connectivity के अंतर्गत हैं।</p><button type="button" id="gpLabourMusterPrint" style="padding:9px 15px;background:#14588c;color:white;border:0;border-radius:7px;font-weight:800">इस मॉड्यूल का प्रिंट / PDF</button><div style="overflow:auto;margin-top:12px">'+table+workTable+'</div>';
 document.getElementById('gpLabourMusterPrint').onclick=()=>{
 const w=window.open('','_blank');if(!w){alert('प्रिंट के लिए popup अनुमति दें।');return;}
 w.document.write('<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>'+title+'</title><style>@page{size:A4 landscape;margin:8mm}body{font-family:Arial,sans-serif;color:#111}table{width:100%;border-collapse:collapse;font-size:9px}th,td{border:1px solid #333;padding:4px}th{background:#e5f0fa}table:first-of-type th:nth-child(3),table:first-of-type td:nth-child(3){width:12mm;max-width:12mm;padding:2px;white-space:normal}th:nth-child(2),td:nth-child(2){white-space:nowrap;text-align:left;width:1%}thead{display:table-header-group}tr{break-inside:avoid}h2{font-size:18px}</style></head><body><h2>'+title+'</h2><p style="text-align:right;font-weight:800;margin:4px 0 10px"><strong>दिनांक: '+esc(date)+'</strong></p><p>'+esc(note)+'</p>'+table+workTable+'</body></html>');
 w.onload=()=>w.print();w.document.close();};
}
const old=render;render=function(){const result=old.apply(this,arguments);draw();return result;};draw();

// Load the verified data independently: the legacy page loader sits inside print HTML.
fetch('gp-emuster-data.js?live='+Date.now(),{cache:'no-store'})
 .then(r=>{if(!r.ok)throw new Error('GP data HTTP '+r.status);return r.text();})
 .then(text=>{
  const match=text.match(/^\s*window\.GP_WORK_TYPE_MUSTER_REPORT\s*=\s*([\s\S]*?)\s*;?\s*$/);
  if(!match)throw new Error('Unexpected GP data format');
  const parsed=JSON.parse(match[1]);
  if(!Array.isArray(parsed.rows)||parsed.rows.length!==695||!Array.isArray(parsed.works))throw new Error('Incomplete GP data');
  window.GP_WORK_TYPE_MUSTER_REPORT=parsed;
  draw();
 }).catch(error=>{console.error('GP report load failed',error);if(box){const p=document.createElement('p');p.style.color='#b91c1c';p.textContent='कार्य प्रकार डेटा लोड नहीं हुआ: '+error.message;box.prepend(p);}});

})();