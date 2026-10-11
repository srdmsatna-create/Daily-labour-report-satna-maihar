(function(){
const mergedCategory=t=>['IAY Houses','PMAY G','PMAY-G'].includes(String(t).trim())?'PMAY-G':t;
const title='उपयंत्री/सेक्टरवार कार्य-श्रेणीवार — प्रगतिरत कार्य, MR जारी कार्य एवं संलग्न श्रमिक';
let box;
let columnSort=null;
let moduleJanpad='ALL';
const lowLabourGP=g=>g.counts.slice(1,6).reduce((a,b)=>a+b,0);
const lowLabourPercentage=g=>g.workingGP>0?lowLabourGP(g)*100/g.workingGP:null;
const mrPercentage=g=>!g.issuedMissing&&g.ongoing>0?g.issuedTotal*100/g.ongoing:null;
function draw(){
 if(!box){box=document.createElement('section');box.id='gpLabourMusterModule';box.style.cssText='margin:16px 0;padding:16px;border:2px solid #14588c;border-radius:12px;background:#fff;color:#102b46';document.getElementById('reportTable').parentElement.insertAdjacentElement('afterend',box);}
 let topPrint=document.getElementById('gpModuleTopPrint');
 if(!topPrint&&document.getElementById('printBtn')){
  topPrint=document.createElement('button');topPrint.id='gpModuleTopPrint';topPrint.textContent='कार्य-श्रेणी Print / PDF';
  topPrint.className=document.getElementById('printBtn').className;
  document.getElementById('printBtn').insertAdjacentElement('afterend',topPrint);
  topPrint.onclick=()=>document.getElementById('gpLabourMusterPrint')?.click();
 }
 box.hidden=view!=='official';if(topPrint)topPrint.hidden=box.hidden;if(box.hidden)return;
 const live=window.GP_WORK_TYPE_MUSTER_REPORT;
 const today=new Intl.DateTimeFormat('en-GB',{timeZone:'Asia/Kolkata',day:'2-digit',month:'2-digit',year:'numeric'}).format(new Date()).replaceAll('/','-');
 const actual=new Map();for(const r of live?.rows||[]){const j=normJanpad(r.janpad);if(!actual.has(j))actual.set(j,{labour:0,works:0,gps:0});const a=actual.get(j);a.labour+=Number(r.labour);a.works+=Number(r.detailWorks??r.worksMR);a.gps++;}
 const mismatch=(official||[]).filter(r=>{const a=actual.get(normJanpad(r.janpad));return !a||a.labour!==Number(r.labourAll)||a.gps!==Number(r.totalGP);});
 if(!live||live.date!==today||mismatch.length){box.innerHTML='<h2>'+title+'</h2><p style="color:#b91c1c;font-weight:800">GP / कार्य-प्रकार डेटा का आज की जनपद रिपोर्ट से मिलान लंबित है। GP डेटा की तिथि: '+esc(live?.date||'अनुपलब्ध')+'। '+esc(mismatch.map(r=>normJanpad(r.janpad)).join(', '))+'। अपडेट BAT चलाएँ।</p>';return;}
 const sourceData=live&&Array.isArray(live.rows)?filterRows(live.rows):filteredRows();
 const data=sortRows(sourceData.filter(r=>moduleJanpad==='ALL'||normJanpad(r.janpad)===moduleJanpad),'labour',['janpad','panchayat']);
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
 const headers=['जनपद का नाम','उपयंत्री का नाम/सेक्टर का नाम','कुल प्रभार की ग्राम पंचायत','श्रमिक संलग्न GPs',...bands.map(b=>b[2]+' श्रमिक वाली GPs'),'1–5 श्रमिक वाली कुल GPs','1–5 श्रमिक वाली GPs %',...(hasMissing?['श्रमिक डेटा अनुपलब्ध GPs']:[]),...workTypes.flatMap(t=>t==='Amrit Sarovar'?['मस्टर रोल जारी कार्यों की कुल संख्या / कुल प्रगतिरत कार्य','मस्टर रोल जारी %',t]:[t])];
 const sortValues=g=>[g.janpad,g.engineer+' / '+g.sector,g.total,g.workingGP,...g.counts,lowLabourGP(g),lowLabourPercentage(g),...(hasMissing?[g.missing]:[]),...workTypes.flatMap((t,i)=>t==='Amrit Sarovar'?[g.issuedMissing?null:g.issuedTotal,mrPercentage(g),g.workMissing[i]?null:g.workCounts[i]]:[g.workMissing[i]?null:g.workCounts[i]])];
 const compareGroups=(a,b)=>{
  if(!columnSort)return 0;
  const x=sortValues(a)[columnSort.index],y=sortValues(b)[columnSort.index];
  if(x==null||y==null)return x==null?(y==null?0:1):-1;
  const order=typeof x==='number'&&typeof y==='number'?x-y:String(x).localeCompare(String(y),'hi',{numeric:true});
  return columnSort.direction==='asc'?order:-order;
 };
 const columnWidths=headers.map((x,i)=>i===0?180:i===1?260:i===2?76:i===3?76:i<4+bands.length?54:x.includes('मस्टर रोल जारी कार्यों की कुल संख्या')?180:110);
 let table='<table style="width:'+columnWidths.reduce((a,b)=>a+b,0)+'px;table-layout:fixed;border-collapse:collapse"><colgroup>'+columnWidths.map(w=>'<col style="width:'+w+'px">').join('')+'</colgroup><thead><tr>'+headers.map((x,i)=>'<th'+(x==='PMAY-G'?' class="pmay-column"':'')+(i===2?' style="width:60px;min-width:60px;max-width:60px;white-space:normal"':x.includes('मस्टर रोल जारी कार्यों की कुल संख्या')?' style="background:#15803d;color:#fff;font-weight:900"':'')+'>'+'<button type="button" class="gp-mr-sort" data-column="'+i+'" aria-label="'+esc(x)+' — आरोही / अवरोही क्रम" title="आरोही / अवरोही क्रम">'+(i===2?'कुल प्रभार की<br>ग्राम पंचायत':esc(x))+' <span class="gp-mr-sort-arrow">'+(columnSort?.index===i?(columnSort.direction==='asc'?'▲':'▼'):'↕')+'</span></button></th>').join('')+'</tr></thead><tbody>';
 const pair=(g,i)=>{
 const mr=g.workCounts[i],ongoing=g.ongoingCounts[i],missing=g.workMissing[i];
 const value=fmt(mr)+(missing?'*':'')+' / '+fmt(ongoing);
 if(missing)return '<span style="font-weight:900;color:#9a3412" title="'+esc('कम से कम '+fmt(mr)+' कार्यों में MR जारी है। कुछ GP का कार्य-प्रकार विवरण अनुपलब्ध है; यह पूर्ण कुल नहीं है।')+'">'+value+'</span>';
 const gap=Math.max(0,ongoing-mr);
 const cls=ongoing>0&&mr===0?'mr-none':gap>0?'mr-gap':'mr-ok';
 const hint=ongoing>0&&mr===0?'MR जारी नहीं':gap>0?'MR रहित: '+fmt(gap):'';
 return '<span class="'+cls+'" title="'+esc(hint||'MR जारी कार्य / कुल प्रगतिरत कार्य')+'">'+value+'</span>';
 };
 const cells=g=>[g.total,g.workingGP,...g.counts,...(hasMissing?[g.missing]:[])].map(v=>'<td style="font-weight:800;text-align:center">'+fmt(v)+'</td>').join('')+'<td class="low-labour">'+fmt(lowLabourGP(g))+'</td><td class="low-labour">'+(lowLabourPercentage(g)==null?'—':lowLabourPercentage(g).toFixed(2)+'%')+'</td>'+workTypes.map((type,i)=>(type==='Amrit Sarovar'?'<td style="font-weight:800;text-align:center;white-space:nowrap;color:#15803d;background:#ecfdf5;font-weight:900">'+(g.issuedMissing?'—':fmt(g.issuedTotal))+' / '+fmt(g.ongoing)+'</td><td style="font-weight:900;text-align:center;color:#15803d;background:#ecfdf5">'+(mrPercentage(g)==null?'—':mrPercentage(g).toFixed(2)+'%')+'</td>':'')+'<td'+(type==='PMAY-G'?' class="pmay-column"':'')+' style="font-weight:800;text-align:center">'+pair(g,i)+'</td>').join('');
 const janpadTotals=[];
 const janpads=[...new Set(summary.map(g=>g.janpad))];
 if(columnSort?.index===0)janpads.sort((a,b)=>(columnSort.direction==='asc'?1:-1)*a.localeCompare(b,'hi'));
 for(const janpad of janpads){
 const entries=summary.filter(g=>g.janpad===janpad).sort(compareGroups);
 table+=entries.map(g=>'<tr>'+[g.janpad,g.engineer+' / '+g.sector].map(v=>'<td style="font-weight:800">'+esc(v)+'</td>').join('')+cells(g)+'</tr>').join('');
 const subtotal={total:entries.reduce((s,g)=>s+g.total,0),ongoing:entries.reduce((s,g)=>s+g.ongoing,0),issuedTotal:entries.reduce((s,g)=>s+g.issuedTotal,0),issuedMissing:entries.some(g=>g.issuedMissing),workingGP:entries.reduce((s,g)=>s+g.workingGP,0),counts:bands.map((b,i)=>entries.reduce((s,g)=>s+g.counts[i],0)),missing:entries.reduce((s,g)=>s+g.missing,0),ongoingCounts:workTypes.map((t,i)=>entries.reduce((s,g)=>s+g.ongoingCounts[i],0)),workCounts:workTypes.map((t,i)=>entries.reduce((s,g)=>s+g.workCounts[i],0)),workMissing:workTypes.map((t,i)=>entries.some(g=>g.workMissing[i]))};
 janpadTotals.push({janpad,...subtotal});
 table+='<tr style="background:#dbeafe;font-weight:800"><td colspan="2">'+esc(janpad)+' — जनपद कुल</td>'+cells(subtotal)+'</tr>';
 }
 if(!summary.length)table+='<tr><td colspan="'+headers.length+'">चयन के लिए ग्राम पंचायत डेटा उपलब्ध नहीं है।</td></tr>';

 const grand={total:summary.reduce((s,g)=>s+g.total,0),workingGP:summary.reduce((s,g)=>s+g.workingGP,0),ongoing:summary.reduce((s,g)=>s+g.ongoing,0),issuedTotal:summary.reduce((s,g)=>s+g.issuedTotal,0),issuedMissing:summary.some(g=>g.issuedMissing),counts:bands.map((b,i)=>summary.reduce((s,g)=>s+g.counts[i],0)),missing:summary.reduce((s,g)=>s+g.missing,0),ongoingCounts:workTypes.map((t,i)=>summary.reduce((s,g)=>s+g.ongoingCounts[i],0)),workCounts:workTypes.map((t,i)=>summary.reduce((s,g)=>s+g.workCounts[i],0)),workMissing:workTypes.map((t,i)=>summary.some(g=>g.workMissing[i]))};
 table+='<tr style="background:#e5f0fa;font-weight:800"><td colspan="2">कुल</td>'+cells(grand)+'</tr></tbody></table>';
 const summaryHeaders=['जनपद का नाम','कुल प्रभार की ग्राम पंचायत','श्रमिक संलग्न GPs',...bands.map(b=>b[2]+' श्रमिक वाली GPs'),'1–5 श्रमिक वाली कुल GPs','1–5 श्रमिक वाली GPs %','मस्टर रोल जारी कार्यों की कुल संख्या / कुल प्रगतिरत कार्य','मस्टर रोल जारी %'];
 const summaryCells=g=>[g.total,g.workingGP,...g.counts].map(v=>'<td>'+fmt(v)+'</td>').join('')+'<td class="low-labour">'+fmt(lowLabourGP(g))+'</td><td class="low-labour">'+(lowLabourPercentage(g)==null?'—':lowLabourPercentage(g).toFixed(2)+'%')+'</td>'+'<td style="background:#ecfdf5;color:#15803d">'+(g.issuedMissing?'—':fmt(g.issuedTotal))+' / '+fmt(g.ongoing)+'</td><td style="background:#ecfdf5;color:#15803d">'+(mrPercentage(g)==null?'—':mrPercentage(g).toFixed(2)+'%')+'</td>';
 const summaryTable='<table class="janpad-short-summary" style="width:100%;border-collapse:collapse"><thead><tr>'+summaryHeaders.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>'+janpadTotals.map(g=>'<tr><td>'+esc(g.janpad)+'</td>'+summaryCells(g)+'</tr>').join('')+'<tr style="background:#dbeafe"><td>कुल</td>'+summaryCells(grand)+'</tr></tbody></table>';
 const zeroPercent=g=>g.total>0?g.counts[0]*100/g.total:0;
 const zeroSummary=janpadTotals.map(g=>esc(g.janpad)+': '+fmt(g.counts[0])+' / '+fmt(g.total)+' GP ('+zeroPercent(g).toFixed(2)+'%)').join(' • ');
 const labourWarning='<p style="border:2px solid #b91c1c;background:#fff1f2;color:#991b1b;padding:12px;font-size:16px;font-weight:900;line-height:1.6">चेतावनी: शून्य श्रमिक वाली ग्राम पंचायतें — '+zeroSummary+'। संबंधित जनपद में शून्य श्रमिक वाली GP का प्रतिशत जितना है, उसके अनुसार सतत समीक्षा एवं सुधार हेतु संबंधित APO और उपयंत्री की जिम्मेदारी तय की जाएगी। शून्य श्रमिक वाली GP के GRS एवं सचिव तथा संबंधित APO एवं उपयंत्री से कारण बताओ नोटिस द्वारा स्पष्टीकरण लिया जाएगा। जिन जनपदों की ग्राम पंचायतों में 5 या उससे कम श्रमिक संलग्न हैं, वहाँ संबंधित APO द्वारा सतत समीक्षा न किया जाना प्रगति में बाधक है। संबंधित APO नियमित समीक्षा कर श्रमिक नियोजन बढ़ाना सुनिश्चित करें। जिन ग्राम पंचायतों में 5 या उससे कम श्रमिक संलग्न पाए जाएँगे, उनके संबंधित उपयंत्री, ग्राम रोजगार सहायक (GRS) एवं सचिव की जिम्मेदारी तय की जाएगी।</p>';
 const noticeControls='<div style="margin:12px 0;padding:12px;border:2px solid #991b1b"><strong>कारण बताओ नोटिस का प्रारूप</strong> <select id="gpNoticeJanpad">'+janpadTotals.map(g=>'<option value="'+esc(g.janpad)+'">'+esc(g.janpad)+'</option>').join('')+'</select> <select id="gpNoticeRole"><option>APO</option><option>उपयंत्री</option><option>ग्राम रोजगार सहायक (GRS)</option><option>सचिव</option></select> <button type="button" id="gpNoticePrint">नोटिस प्रारूप Print / PDF</button></div>';
 const shortSummary='<h2 style="margin:18px 0 8px">जनपदवार श्रमिक एवं MR कार्य सारांश</h2><button type="button" id="gpJanpadSummaryPrint" style="padding:9px 15px;background:#14588c;color:white;border:0;border-radius:7px;font-weight:800">जनपद सारांश Print / PDF</button><div style="overflow:auto;margin-top:10px">'+summaryTable+'</div>'+labourWarning+noticeControls;
 const workTable='';
 const filterJanpads=[...new Set((live.rows||[]).map(r=>normJanpad(r.janpad)))].sort();
 const janpadTabs='<div id="gpModuleJanpadTabs" style="display:flex;gap:6px;flex-wrap:wrap;margin:10px 0">'+['ALL',...filterJanpads].map(j=>'<button type="button" data-janpad="'+esc(j)+'" style="padding:8px 12px;border:1px solid #14588c;border-radius:6px;font-weight:800;background:'+(moduleJanpad===j?'#14588c;color:white':'white;color:#14588c')+'">'+esc(j==='ALL'?'सभी जनपद':j)+'</button>').join('')+'</div>';
 box.innerHTML='<style>.pmay-column{background:#ede9fe!important;color:#5b21b6!important}.pmay-column .mr-gap,.pmay-column .mr-ok{background:transparent;color:#5b21b6;font-weight:900}th.pmay-column{background:#6d28d9!important;color:#fff!important}#gpLabourMusterModule .gp-mr-sort{display:block;width:100%;border:0;background:transparent;color:inherit;font:inherit;font-weight:900;line-height:inherit;text-align:center;padding:0;cursor:pointer}#gpLabourMusterModule .gp-mr-sort:focus-visible{outline:2px solid #facc15}#gpLabourMusterModule .gp-mr-sort-arrow{color:#fde047;white-space:nowrap}.mr-none{display:block;background:#fee2e2;color:#b91c1c;font-weight:900;padding:3px;border:1px solid #ef4444;border-radius:3px}.mr-gap{display:block;background:#fff7ed;color:#9a3412;font-weight:800;padding:3px}.mr-ok{color:#15803d;font-weight:800}#gpLabourMusterModule table{font-size:13px;table-layout:auto}#gpLabourMusterModule th{white-space:normal!important;overflow-wrap:break-word;min-width:0;max-width:none;line-height:1.3}#gpLabourMusterModule th,#gpLabourMusterModule td{border:1px solid #7894ac;padding:3px}#gpLabourMusterModule table:first-of-type th:nth-child(3),#gpLabourMusterModule table:first-of-type td:nth-child(3){width:76px!important;min-width:76px!important;max-width:76px!important;white-space:normal!important;overflow-wrap:anywhere;padding:3px!important;text-align:center;font-size:14px;line-height:1.3}#gpLabourMusterModule th:nth-child(2),#gpLabourMusterModule td:nth-child(2){white-space:nowrap;min-width:0;text-align:left}#gpLabourMusterModule th{background:#14588c;color:white}#gpLabourMusterModule tbody tr:nth-child(even){background:#f0f6fb}#gpLabourMusterModule table{border:2px solid #1f2937!important;border-collapse:collapse!important}#gpLabourMusterModule th,#gpLabourMusterModule td{border:1.5px solid #1f2937!important;line-height:1.5!important;vertical-align:middle;padding:7px 5px!important;box-sizing:border-box}#gpLabourMusterModule td{font-size:19px!important;font-weight:900!important;white-space:normal!important;overflow-wrap:break-word}#gpLabourMusterModule th{font-size:14px!important}#gpLabourMusterModule td span{line-height:1.5!important}#gpLabourMusterModule .janpad-short-summary{min-width:1450px;table-layout:fixed}#gpLabourMusterModule .janpad-short-summary th:first-child{width:140px}#gpLabourMusterModule table:not(.janpad-short-summary) td:first-child{white-space:nowrap!important;overflow-wrap:normal!important}#gpLabourMusterModule .janpad-short-summary{min-width:1580px!important;table-layout:fixed!important}#gpLabourMusterModule .janpad-short-summary th:first-child,#gpLabourMusterModule .janpad-short-summary td:first-child{width:185px!important;white-space:nowrap!important;overflow-wrap:normal!important}#gpLabourMusterModule .janpad-short-summary td{text-align:center!important;white-space:nowrap!important;overflow-wrap:normal!important}#gpLabourMusterModule .janpad-short-summary td:first-child{text-align:left!important}#gpLabourMusterModule .janpad-short-summary th:nth-last-child(2),#gpLabourMusterModule .janpad-short-summary td:nth-last-child(2){width:160px!important}#gpLabourMusterModule .janpad-short-summary th:last-child,#gpLabourMusterModule .janpad-short-summary td:last-child{width:100px!important}#gpLabourMusterModule .janpad-short-summary th:nth-last-child(-n+2){background:#15803d!important;color:#fff!important}.low-labour{background:#f3e8ff!important;color:#6b21a8!important;font-weight:900!important}#gpLabourMusterModule .janpad-short-summary td:nth-child(3){background:#cffafe!important;color:#155e75!important}#gpLabourMusterModule .janpad-short-summary tbody tr:last-child td{font-size:22px!important;font-weight:900!important;background:#dbeafe}#gpLabourMusterModule .janpad-short-summary th:nth-child(3){background:#0e7490!important}@media print{#gpLabourMusterModule{display:none}}</style><h2 style="margin:0 0 8px">'+title+'</h2>'+janpadTabs+'<p style="text-align:right;font-weight:800;margin:4px 0 10px"><strong>दिनांक: '+esc(date)+'</strong></p>'+''+'<button type="button" id="gpLabourMusterPrint" style="padding:9px 15px;background:#14588c;color:white;border:0;border-radius:7px;font-weight:800">इस मॉड्यूल का प्रिंट / PDF</button><div style="overflow:auto;margin-top:12px">'+table+workTable+'</div>'+shortSummary;
 box.querySelectorAll('.gp-mr-sort').forEach(button=>{
  const index=Number(button.dataset.column);
  button.closest('th').setAttribute('aria-sort',columnSort?.index===index?(columnSort.direction==='asc'?'ascending':'descending'):'none');
  button.onclick=()=>{columnSort={index,direction:columnSort?.index===index&&columnSort.direction==='asc'?'desc':'asc'};draw();};
 });
 box.querySelectorAll('#gpModuleJanpadTabs button').forEach(b=>b.onclick=()=>{moduleJanpad=b.dataset.janpad;draw();});
 document.getElementById('gpNoticePrint').onclick=()=>{
 const selected=document.getElementById('gpNoticeJanpad').value;
 const role=document.getElementById('gpNoticeRole').value;
 const g=janpadTotals.find(x=>x.janpad===selected);if(!g)return;
 const w=window.open('','_blank');if(!w){alert('प्रिंट के लिए popup अनुमति दें।');return;}
 const text='<h2 style="text-align:center">कारण बताओ नोटिस — प्रारूप</h2><p>कार्यालय: ____________________<br>क्रमांक: __________ &nbsp; दिनांक: __________</p><p>प्रति,<br>नाम: ____________________<br>पद: '+esc(role)+'<br>जनपद पंचायत: '+esc(selected)+'<br>संबंधित ग्राम पंचायत / सेक्टर: ____________________</p><p><strong>विषय: शून्य / 5 या उससे कम श्रमिक नियोजन एवं नियमित समीक्षा के संबंध में स्पष्टीकरण।</strong></p><p>रिपोर्ट दिनांक '+esc(date)+' के उपलब्ध आँकड़ों में जनपद '+esc(selected)+' की कुल '+fmt(g.total)+' ग्राम पंचायतों में '+fmt(g.counts[0])+' ग्राम पंचायतों में शून्य श्रमिक संलग्न हैं, जिसका प्रतिशत '+zeroPercent(g).toFixed(2)+'% है। श्रमिक संलग्न '+fmt(g.workingGP)+' ग्राम पंचायतों में '+fmt(lowLabourGP(g))+' ग्राम पंचायतों में 1–5 श्रमिक संलग्न हैं ('+(lowLabourPercentage(g)==null?'—':lowLabourPercentage(g).toFixed(2)+'%')+')। ये जनपद स्तर के आँकड़े हैं; आपके प्रभार की संबंधित ग्राम पंचायतों का विवरण नीचे संलग्न किया जाए।</p><p>आपके प्रभार की GP तथा सत्यापित श्रमिक संख्या: ____________________<br>समीक्षा में पाए गए तथ्य / अवधि: ____________________</p><p>उक्त स्थिति के संबंध में श्रमिक नियोजन कम अथवा शून्य रहने के कारण, आपके द्वारा की गई समीक्षा, रोजगार माँग पर की गई कार्रवाई, कार्य एवं मस्टर रोल उपलब्ध कराने के प्रयास तथा सुधार की कार्ययोजना साक्ष्यों सहित दिनांक __________ तक प्रस्तुत करें।</p><p>उत्तर एवं अभिलेखों की समीक्षा के आधार पर संबंधित APO, उपयंत्री, ग्राम रोजगार सहायक एवं सचिव की भूमिका तथा जिम्मेदारी निर्धारित की जाएगी। उत्तर प्राप्त न होने या असंतोषजनक पाए जाने पर सक्षम अधिकारी द्वारा लागू नियमों के अनुसार आगे की कार्रवाई पर विचार किया जाएगा।</p><p>संलग्न: संबंधित GP की सत्यापित सूची / रिपोर्ट<br><br>हस्ताक्षर: ____________________<br>नाम एवं पद, सक्षम अधिकारी: ____________________</p>';
 w.document.write('<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>कारण बताओ नोटिस प्रारूप</title><style>@page{size:A4 portrait;margin:15mm}body{font-family:Arial,sans-serif;font-size:16px;line-height:1.65;color:#111}h2{font-size:20px}p{margin:12px 0}</style></head><body contenteditable="true">'+text+'</body></html>');
 w.document.close();Promise.resolve(w.document.fonts?.ready).then(()=>{w.focus();w.setTimeout(()=>w.print(),500);});
 };
 document.getElementById('gpJanpadSummaryPrint').onclick=()=>{
 const w=window.open('','_blank');if(!w){alert('प्रिंट के लिए popup अनुमति दें।');return;}
 w.document.write('<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>जनपदवार श्रमिक एवं MR कार्य सारांश</title><style>.low-labour{background:#f3e8ff;color:#6b21a8;font-weight:900}tbody tr:last-child td{font-size:19px;font-weight:900}@page{size:A4 landscape;margin:7mm}body{font-family:Arial,sans-serif;color:#111;-webkit-print-color-adjust:exact;print-color-adjust:exact}h2{font-size:18px}table{width:100%;table-layout:fixed;border-collapse:collapse}th,td{border:1.5px solid #111;padding:7px 3px;text-align:center;line-height:1.5}th{font-size:11px;background:#14588c;color:white;overflow-wrap:anywhere}td{font-size:17px;font-weight:900;line-height:1.5;vertical-align:middle;white-space:nowrap}th:first-child,td:first-child{width:27mm;text-align:left;overflow-wrap:anywhere}th:nth-last-child(2),td:nth-last-child(2){width:30mm}thead{display:table-header-group}tr{break-inside:avoid}</style></head><body><h2>जनपदवार श्रमिक एवं MR कार्य सारांश</h2><p style="text-align:right;font-weight:bold">दिनांक: '+esc(date)+'</p>'+summaryTable+labourWarning+'</body></html>');
 w.document.close();Promise.resolve(w.document.fonts?.ready).then(()=>{w.focus();w.setTimeout(()=>w.print(),500);});
 };
 document.getElementById('gpLabourMusterPrint').onclick=()=>{
 // Split wide reports into readable pages, repeating identifying columns.
 const original=box.querySelector('table');
 const printParts=[];
 for(let start=4;start<headers.length;start+=6){
  const indices=[0,1,2,3,...Array.from({length:Math.min(6,headers.length-start)},(_,i)=>start+i)];
  const copy=document.createElement('table');
  for(const section of ['thead','tbody']){
   const target=document.createElement(section);
   for(const row of original.querySelector(section).rows){
    const tr=document.createElement('tr');tr.style.cssText=row.style.cssText;
    let logical=0;
    for(const cell of row.cells){
     const span=cell.colSpan||1;
     const count=indices.filter(i=>i>=logical&&i<logical+span).length;
     if(count){const clone=cell.cloneNode(true);clone.colSpan=count;clone.removeAttribute('style');tr.appendChild(clone);}
     logical+=span;
    }
    target.appendChild(tr);
   }
   copy.appendChild(target);
  }
  printParts.push('<section class="print-part"><h3>भाग '+(printParts.length+1)+' — '+esc(headers.slice(start,start+6).join(' • '))+'</h3>'+copy.outerHTML+'</section>');
 }
 const w=window.open('','_blank');if(!w){alert('प्रिंट के लिए popup अनुमति दें।');return;}
 w.document.write('<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>'+title+'</title><style>.pmay-column{background:#ede9fe!important;color:#5b21b6!important}.pmay-column .mr-gap,.pmay-column .mr-ok{background:transparent;color:#5b21b6;font-weight:900}th.pmay-column{background:#6d28d9!important;color:#fff!important}.print-part{break-before:page}.print-part:first-of-type{break-before:auto}.print-part h3{margin:6px 0}thead{display:table-header-group}tbody tr{page-break-inside:avoid}td:first-child,th:first-child{width:27mm;overflow-wrap:anywhere}td:nth-child(3),th:nth-child(3),td:nth-child(4),th:nth-child(4){width:14mm}body{-webkit-print-color-adjust:exact;print-color-adjust:exact}td{font-size:17px;line-height:1.5;text-align:center;font-weight:900;vertical-align:middle;overflow-wrap:break-word}th{font-size:12px;overflow-wrap:anywhere}h3{font-size:13px}.mr-none{display:block;background:#fee2e2;color:#b91c1c;font-weight:900;padding:3px;border:1px solid #ef4444;border-radius:3px}.mr-gap{display:block;background:#fff7ed;color:#9a3412;font-weight:800;padding:3px}.mr-ok{color:#15803d;font-weight:800}.low-labour{background:#f3e8ff;color:#6b21a8;font-weight:900}tbody tr:last-child td{font-size:19px;font-weight:900}@page{size:A4 landscape;margin:8mm}body{font-family:Arial,sans-serif;color:#111}table{width:100%!important;table-layout:fixed!important;border-collapse:collapse;font-size:14px;font-weight:800}col{width:auto!important}th,td{border:1.5px solid #111;padding:6px 3px;line-height:1.5}th{background:#e5f0fa}table:first-of-type th:nth-child(3),table:first-of-type td:nth-child(3){width:9mm;max-width:9mm;padding:2px;white-space:normal}th:nth-child(2),td:nth-child(2){white-space:normal;text-align:left;width:42mm}thead{display:table-header-group}tr{break-inside:avoid}h2{font-size:18px}button{border:0;background:transparent;color:inherit;font:inherit;font-weight:bold;padding:0}.gp-mr-sort-arrow{display:none}</style></head><body><h2>'+title+'</h2><p style="text-align:right;font-weight:800;margin:4px 0 10px"><strong>दिनांक: '+esc(date)+'</strong></p>'+''+''+printParts.join('')+workTable+'</body></html>');
 w.document.close();Promise.resolve(w.document.fonts?.ready).then(()=>{w.focus();w.setTimeout(()=>w.print(),500);});};
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