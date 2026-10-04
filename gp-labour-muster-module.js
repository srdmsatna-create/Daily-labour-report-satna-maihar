(function(){
const title='ग्राम पंचायतवार संलग्न श्रमिक एवं मस्टर रोल संख्या';
let box;
function draw(){
 if(!box){box=document.createElement('section');box.id='gpLabourMusterModule';box.style.cssText='margin:16px 0;padding:16px;border:2px solid #14588c;border-radius:12px;background:#fff;color:#102b46';document.getElementById('reportTable').parentElement.insertAdjacentElement('afterend',box);}
 box.hidden=view!=='official';if(box.hidden)return;
 const data=sortRows(filteredRows(),'labour',['janpad','panchayat']);
 const date=autoMeta?.sourceDates?.RepDay||extractDate(reportTitle)||'तिथि उपलब्ध नहीं';
 const value=v=>v===null||v===undefined||v===''?'उपलब्ध नहीं':fmt(v);
 let table='<table style="width:100%;border-collapse:collapse"><thead><tr>'+['क्र.','जिला','जनपद','ग्राम पंचायत','उपयंत्री','क्लस्टर','संलग्न श्रमिक','मस्टर रोल संख्या'].map(x=>'<th>'+x+'</th>').join('')+'</tr></thead><tbody>';
 table+=data.map((r,i)=>'<tr>'+[i+1,districtOf(r.janpad),r.janpad,r.panchayat,r.engineer,r.cluster,value(r.labour),value(r.mrs)].map((v,j)=>'<td'+(j>=6?' style="font-weight:800;color:#14588c"':'')+'>'+esc(v)+'</td>').join('')+'</tr>').join('');
 if(!data.length)table+='<tr><td colspan="8">चयन के लिए ग्राम पंचायत डेटा उपलब्ध नहीं है।</td></tr>';
 table+='<tr style="background:#e5f0fa;font-weight:800"><td colspan="6">कुल — '+fmt(data.length)+' ग्राम पंचायत</td><td>'+fmt(sum(data,'labour'))+'</td><td>'+fmt(sum(data,'mrs'))+'</td></tr></tbody></table>';
 const note='GP स्रोत की तिथि: '+date+' • जनपद, उपयंत्री एवं क्लस्टर के ऊपर दिए फ़िल्टर लागू हैं।';
 box.innerHTML='<style>#gpLabourMusterModule th,#gpLabourMusterModule td{border:1px solid #7894ac;padding:7px}#gpLabourMusterModule th{background:#14588c;color:white}#gpLabourMusterModule tbody tr:nth-child(even){background:#f0f6fb}@media print{#gpLabourMusterModule{display:none}}</style><h2 style="margin:0 0 8px">'+title+'</h2><p>'+esc(note)+'</p><p style="color:#9a3412">ग्राम पंचायत के उपलब्ध स्रोत आँकड़े दिखाए गए हैं; जनपद के अद्यतन कुल से इनका अंतर हो सकता है।</p><button type="button" id="gpLabourMusterPrint" style="padding:9px 15px;background:#14588c;color:white;border:0;border-radius:7px;font-weight:800">इस मॉड्यूल का प्रिंट / PDF</button><div style="overflow:auto;margin-top:12px">'+table+'</div>';
 document.getElementById('gpLabourMusterPrint').onclick=()=>{
 const w=window.open('','_blank');if(!w){alert('प्रिंट के लिए popup अनुमति दें।');return;}
 w.document.write('<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>'+title+'</title><style>@page{size:A4 landscape;margin:8mm}body{font-family:Arial,sans-serif;color:#111}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #333;padding:4px}th{background:#e5f0fa}thead{display:table-header-group}tr{break-inside:avoid}h2{font-size:18px}</style></head><body><h2>'+title+'</h2><p>'+esc(note)+'</p>'+table+'</body></html>');
 w.document.close();w.onload=()=>w.print();};
}
const old=render;render=function(){const result=old.apply(this,arguments);draw();return result;};draw();
})();