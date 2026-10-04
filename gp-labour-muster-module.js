(function(){
const title='जनपद / उपयंत्री / सेक्टरवार — संलग्न श्रमिक संख्या का वर्गवार सारांश';
let box;
function draw(){
 if(!box){box=document.createElement('section');box.id='gpLabourMusterModule';box.style.cssText='margin:16px 0;padding:16px;border:2px solid #14588c;border-radius:12px;background:#fff;color:#102b46';document.getElementById('reportTable').parentElement.insertAdjacentElement('afterend',box);}
 box.hidden=view!=='official';if(box.hidden)return;
 const data=sortRows(filteredRows(),'labour',['janpad','panchayat']);
 const date=autoMeta?.sourceDates?.RepDay||extractDate(reportTitle)||'तिथि उपलब्ध नहीं';
 const bands=[[0,0,'शून्य'],[1,1,'01'],[2,2,'02'],[3,3,'03'],[4,4,'04'],[5,5,'05'],[6,10,'06 से 10'],[11,20,'11 से 20'],[21,30,'21 से 30'],[31,50,'31 से 50'],[51,100,'51 से 100'],[101,Infinity,'100 से अधिक']];
 const groups=new Map(),seen=new Set();
 for(const r of data){
 const key=normJanpad(r.janpad)+'¦'+clean(r.panchayat).toUpperCase();
 if(seen.has(key))continue;seen.add(key);
 const j=normJanpad(r.janpad);
 const engineer=clean(r.engineer)||'नाम उपलब्ध नहीं',sector=clean(r.cluster)||'सेक्टर उपलब्ध नहीं';
 const groupKey=[j,engineer,sector].join('¦');
 if(!groups.has(groupKey))groups.set(groupKey,{janpad:j,engineer,sector,total:0,counts:bands.map(()=>0),missing:0});
 const g=groups.get(groupKey);g.total++;
 const n=r.labour===null||r.labour===undefined||clean(r.labour)===''?NaN:Number(r.labour);
 const bi=Number.isInteger(n)&&n>=0?bands.findIndex(b=>n>=b[0]&&n<=b[1]):-1;
 if(bi<0)g.missing++;else g.counts[bi]++;
 }
 const summary=[...groups.values()].sort((a,b)=>a.janpad.localeCompare(b.janpad,'hi')||a.engineer.localeCompare(b.engineer,'hi')||a.sector.localeCompare(b.sector,'hi'));
 const hasMissing=summary.some(g=>g.missing>0);
 const headers=['जनपद का नाम','उपयंत्री का नाम','सेक्टर का नाम','कुल प्रभार की ग्राम पंचायत',...bands.map(b=>b[2]+' श्रमिक वाली GPs'),...(hasMissing?['श्रमिक डेटा अनुपलब्ध GPs']:[])];
 let table='<table style="width:100%;border-collapse:collapse"><thead><tr>'+headers.map(x=>'<th>'+esc(x)+'</th>').join('')+'</tr></thead><tbody>';
 const cells=g=>[g.total,...g.counts,...(hasMissing?[g.missing]:[])].map(v=>'<td style="font-weight:800;text-align:center">'+fmt(v)+'</td>').join('');
 const janpads=[...new Set(summary.map(g=>g.janpad))];
 for(const janpad of janpads){
 const entries=summary.filter(g=>g.janpad===janpad);
 table+=entries.map(g=>'<tr>'+[g.janpad,g.engineer,g.sector].map(v=>'<td style="font-weight:800">'+esc(v)+'</td>').join('')+cells(g)+'</tr>').join('');
 const subtotal={total:entries.reduce((s,g)=>s+g.total,0),counts:bands.map((b,i)=>entries.reduce((s,g)=>s+g.counts[i],0)),missing:entries.reduce((s,g)=>s+g.missing,0)};
 table+='<tr style="background:#dbeafe;font-weight:800"><td colspan="3">'+esc(janpad)+' — जनपद कुल</td>'+cells(subtotal)+'</tr>';
 }
 if(!summary.length)table+='<tr><td colspan="'+headers.length+'">चयन के लिए ग्राम पंचायत डेटा उपलब्ध नहीं है।</td></tr>';
 table+='<tr style="background:#e5f0fa;font-weight:800"><td colspan="3">कुल</td>'+[summary.reduce((s,g)=>s+g.total,0),...bands.map((b,i)=>summary.reduce((s,g)=>s+g.counts[i],0)),...(hasMissing?[summary.reduce((s,g)=>s+g.missing,0)]:[])].map(v=>'<td style="text-align:center">'+fmt(v)+'</td>').join('')+'</tr></tbody></table>';
 const note='GP स्रोत की तिथि: '+date+' • जनपद, उपयंत्री एवं क्लस्टर के ऊपर दिए फ़िल्टर लागू हैं।';
 box.innerHTML='<style>#gpLabourMusterModule th,#gpLabourMusterModule td{border:1px solid #7894ac;padding:7px}#gpLabourMusterModule th{background:#14588c;color:white}#gpLabourMusterModule tbody tr:nth-child(even){background:#f0f6fb}@media print{#gpLabourMusterModule{display:none}}</style><h2 style="margin:0 0 8px">'+title+'</h2><p>'+esc(note)+'</p><p style="color:#9a3412">ग्राम पंचायत के उपलब्ध स्रोत आँकड़े दिखाए गए हैं; जनपद के अद्यतन कुल से इनका अंतर हो सकता है।</p><button type="button" id="gpLabourMusterPrint" style="padding:9px 15px;background:#14588c;color:white;border:0;border-radius:7px;font-weight:800">इस मॉड्यूल का प्रिंट / PDF</button><div style="overflow:auto;margin-top:12px">'+table+'</div>';
 document.getElementById('gpLabourMusterPrint').onclick=()=>{
 const w=window.open('','_blank');if(!w){alert('प्रिंट के लिए popup अनुमति दें।');return;}
 w.document.write('<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>'+title+'</title><style>@page{size:A4 landscape;margin:8mm}body{font-family:Arial,sans-serif;color:#111}table{width:100%;border-collapse:collapse;font-size:9px}th,td{border:1px solid #333;padding:4px}th{background:#e5f0fa}thead{display:table-header-group}tr{break-inside:avoid}h2{font-size:18px}</style></head><body><h2>'+title+'</h2><p>'+esc(note)+'</p>'+table+'</body></html>');
 w.onload=()=>w.print();w.document.close();};
}
const old=render;render=function(){const result=old.apply(this,arguments);draw();return result;};draw();
})();