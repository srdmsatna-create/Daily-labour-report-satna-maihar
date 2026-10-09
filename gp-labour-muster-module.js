(function(){
const mergedCategory=t=>['IAY Houses','PMAY G','PMAY-G'].includes(String(t).trim())?'PMAY-G':t;
const title='उपयंत्री/सेक्टरवार कार्य-श्रेणीवार — प्रगतिरत कार्य, MR जारी कार्य एवं संलग्न श्रमिक';
let box;
function draw(){
 if(!box){box=document.createElement('section');box.id='gpLabourMusterModule';box.style.cssText='margin:16px 0;padding:16px;border:2px solid #14588c;border-radius:12px;background:#fff;color:#102b46';document.getElementById('reportTable').parentElement.insertAdjacentElement('afterend',box);}
 box.hidden=view!=='official';if(box.hidden)return;
 const live=window.GP_WORK_TYPE_MUSTER_REPORT;
 const today=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Kolkata',day:'2-digit',month:'2-digit',year:'numeric'}).format(new Date()).replaceAll('/','-');
 const actual=new Map();for(const r of live?.rows||[]){const j=normJanpad(r.janpad);if(!actual.has(j))actual.set(j,{labour:0,works:0,gps:0});const a=actual.get(j);a.labour+=Number(r.labour);a.works+=Number(r.worksMR);a.gps++;}
 const mismatch=(official||[]).filter(r=>{const a=actual.get(normJanpad(r.janpad));return !a||a.labour!==Number(r.labourAll)||a.works!==Number(r.mrAll)||a.gps!==Number(r.totalGP);});
 if(!live||live.date!==today||mismatch.length){box.innerHTML='<h2>'+title+'</h2><p style="color:#b91c1c;font-weight:800">GP / कार्य-प्रकार डेटा का आज की जनपद रिपोर्ट से मिलान लंबित है। GP डेटा की तिथि: '+esc(live?.date||'अनुपलब्ध')+'। '+esc(mismatch.map(r=>normJanpad(r.janpad)).join(', '))+'। अपडेट BAT चलाएँ।</p>';return;}
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
 const issuedCount=workRow?.detailWorks??workRow?.worksMR;
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
 const columnWidths=headers.map((x,i)=>i===0?95:i===1?240:i===2?60:i===3?60:i<4+bands.length?48:x.includes('मस्टर रोल जारी कार्यों की कुल संख्या')?110:76);
 let table='<table style="width:'+columnWidths.reduce((a,b)=>a+b,0)+'px;table-layout:fixed;border-collapse:collapse"><colgroup>'+columnWidths.map(w=>'<col style="width:'+w+'px">').join('')+'</colgroup><thead><tr>'+headers.map((x,i)=>'<th'+(i===2?' style="width:60px;min-width:60px;max-width:60px;white-space:normal"':x.includes('मस्टर रोल जारी कार्यों की कुल संख्या')?' style="background:#15803d;color:#fff;font-weight:900"':'')+'>'+(i===2?'कुल प्रभार की<br>ग्राम पंचायत':esc(x))+'</th>').join('')+'</tr></thead><tbody>';
 const pair=(g,i)=>{
 const mr=g.workCounts[i],ongoing=g.ongoingCounts[i],missing=g.workMissing[i];
 const value=fmt(mr)+(missing?'*':'')+' / '+fmt(ongoing);
 if(missing)return '<span style="font-weight:900;color:#9a3412" title="'+esc('कम से कम '+fmt(mr)+' कार्यों में MR जारी है। कुछ GP का कार्य-प्रकार विवरण अनुपलब्ध है; यह पूर्ण कुल नहीं है।')+'">'+value+'</span>';
 const gap=Math.max(0,ongoing-mr);
 const cls=ongoing>0&&mr===0?'mr-none':gap>0?'mr-gap':'mr-ok';
 const hint=ongoing>0&&mr===0?'MR जारी नहीं':gap>0?'MR रहित: '+fmt(gap):'';
 return '<span class="'+cls+'" title="'+esc(hint||'MR जारी कार्य / कुल प्रगतिरत कार्य')+'">'+value+'</span>';
 };
 const cells=g=>[g.total,g.workingGP,...g.counts,...(hasMissing?[g.missing]:[])].map(v=>'<td style="font-weight:800;text-align:center">'+fmt(v)+'</td>').join('')+workTypes.map((type,i)=>(type==='Amrit Sarovar'?'<td style="font-weight:800;text-align:center;white-space:nowrap;color:#15803d;background:#ecfdf5;font-weight:900">'+(g.issuedMissing?'—':fmt(g.issuedTotal))+' / '+fmt(g.ongoing)+'</td>':'')+'<td style="font-weight:800;text-align:center">'+pair(g,i)+'</td>').join('');
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
 const workTable='';
 const note='* = उपलब्ध GP से सत्यापित MR जारी कार्यों का जोड़; कुछ GP का विवरण लंबित होने से पूर्ण संख्या अधिक हो सकती है। लाल: प्रगतिरत कार्य हैं, MR जारी नहीं • नारंगी: कुछ प्रगतिरत कार्यों में MR जारी नहीं • कार्य-प्रकार के प्रत्येक कॉलम में: मस्टर रोल जारी कार्यों की कुल संख्या / कुल प्रगतिरत कार्य • जनपद, उपयंत्री एवं क्लस्टर के ऊपर दिए फ़िल्टर लागू हैं।';
 box.innerHTML='<style>.mr-none{display:block;background:#fee2e2;color:#b91c1c;font-weight:900;padding:3px;border:1px solid #ef4444;border-radius:3px}.mr-gap{display:block;background:#fff7ed;color:#9a3412;font-weight:800;padding:3px}.mr-ok{color:#15803d;font-weight:800}#gpLabourMusterModule table{font-size:13px;table-layout:auto}#gpLabourMusterModule th{white-space:normal!important;overflow-wrap:break-word;min-width:0;max-width:none;line-height:1.3}#gpLabourMusterModule th,#gpLabourMusterModule td{border:1px solid #7894ac;padding:3px}#gpLabourMusterModule table:first-of-type th:nth-child(3),#gpLabourMusterModule table:first-of-type td:nth-child(3){width:60px!important;min-width:60px!important;max-width:60px!important;white-space:normal!important;overflow-wrap:anywhere;padding:3px!important;text-align:center;font-size:14px;line-height:1.3}#gpLabourMusterModule th:nth-child(2),#gpLabourMusterModule td:nth-child(2){white-space:nowrap;min-width:0;text-align:left}#gpLabourMusterModule th{background:#14588c;color:white}#gpLabourMusterModule tbody tr:nth-child(even){background:#f0f6fb}@media print{#gpLabourMusterModule{display:none}}</style><h2 style="margin:0 0 8px">'+title+'</h2><p style="text-align:right;font-weight:800;margin:4px 0 10px"><strong>दिनांक: '+esc(date)+'</strong></p><p>'+esc(note)+'</p>'+((live.sourceDifferences||[]).length?'<p style="color:#9a3412;font-weight:800">सरकारी सारांश एवं सरकारी कार्य-विवरण में अंतर: '+esc(live.sourceDifferences.map(r=>r.janpad+'/'+r.panchayat+' — सारांश '+r.summaryWorks+', विवरण '+r.detailWorks).join('; '))+'. कार्य-श्रेणी गणना विवरण के अनुसार है; जनपद योग सरकारी सारांश के अनुसार हैं।</p>':'')+'<p style="color:#9a3412">ग्राम पंचायत के उपलब्ध स्रोत आँकड़े दिखाए गए हैं; जनपद के अद्यतन कुल से इनका अंतर हो सकता है। कॉलम 6 से प्राप्त MR जारी वाले कार्यों की कार्य प्रकारवार संख्या दिखाई जाएगी। सत्यापित कार्य सूची उपलब्ध न होने पर — दिखाया गया है। CC Road और Gravel Road, Rural Connectivity के अंतर्गत हैं।</p><button type="button" id="gpLabourMusterPrint" style="padding:9px 15px;background:#14588c;color:white;border:0;border-radius:7px;font-weight:800">इस मॉड्यूल का प्रिंट / PDF</button><div style="overflow:auto;margin-top:12px">'+table+workTable+'</div>';
 document.getElementById('gpLabourMusterPrint').onclick=()=>{
 const w=window.open('','_blank');if(!w){alert('प्रिंट के लिए popup अनुमति दें।');return;}
 w.document.write('<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>'+title+'</title><style>.mr-none{display:block;background:#fee2e2;color:#b91c1c;font-weight:900;padding:3px;border:1px solid #ef4444;border-radius:3px}.mr-gap{display:block;background:#fff7ed;color:#9a3412;font-weight:800;padding:3px}.mr-ok{color:#15803d;font-weight:800}@page{size:A4 landscape;margin:8mm}body{font-family:Arial,sans-serif;color:#111}table{width:100%!important;table-layout:fixed!important;border-collapse:collapse;font-size:9px}col{width:auto!important}th,td{border:1px solid #333;padding:4px}th{background:#e5f0fa}table:first-of-type th:nth-child(3),table:first-of-type td:nth-child(3){width:9mm;max-width:9mm;padding:2px;white-space:normal}th:nth-child(2),td:nth-child(2){white-space:nowrap;text-align:left;width:1%}thead{display:table-header-group}tr{break-inside:avoid}h2{font-size:18px}</style></head><body><h2>'+title+'</h2><p style="text-align:right;font-weight:800;margin:4px 0 10px"><strong>दिनांक: '+esc(date)+'</strong></p><p>'+esc(note)+'</p>'+((live.sourceDifferences||[]).length?'<p style="color:#9a3412;font-weight:800">सरकारी सारांश एवं सरकारी कार्य-विवरण में अंतर: '+esc(live.sourceDifferences.map(r=>r.janpad+'/'+r.panchayat+' — सारांश '+r.summaryWorks+', विवरण '+r.detailWorks).join('; '))+'. कार्य-श्रेणी गणना विवरण के अनुसार है; जनपद योग सरकारी सारांश के अनुसार हैं।</p>':'')+''+table+workTable+'</body></html>');
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