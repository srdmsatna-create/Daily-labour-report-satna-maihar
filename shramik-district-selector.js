(function(){
'use strict';
const section=document.getElementById('shramikNiyojanReport');
if(!section)return;
const sourceNames=["AGAR-MALWA","ALIRAJPUR","ANUPPUR","ASHOK NAGAR","BALAGHAT","BARWANI","BETUL","BHIND","BHOPAL","BURHANPUR","CHHATARPUR","CHHINDWARA","DAMOH","DATIA","DEWAS","DHAR","DINDORI","GUNA","GWALIOR","HARDA","INDORE","JABALPUR","JHABUA","KATNI","KHANDWA","KHARGONE","MANDLA","MANDSAUR","MORENA","NARMADAPURAM","NARSINGHPUR","NEEMUCH","NIWARI","PANNA","RAISEN","RAJGARH","RATLAM","REWA","SAGAR","SATNA","SEHORE","SEONI","SHAHDOL","SHAJAPUR","SHEOPUR","SHIVPURI","SIDHI","SINGRAULI","TIKAMGARH","UJJAIN","UMARIA","VIDISHA"], region=['रीवा','मऊगंज','सतना','मैहर','SIDHI','SINGRAULI'];
const names=sourceNames.flatMap(name=>name==='REWA'?['रीवा','मऊगंज']:name==='सतना'?['सतना','मैहर']:[name]);
const tools=section.querySelector('.sn-tools'), originalWrap=section.querySelector('.sn-wrap'), originalKpis=section.querySelector('.sn-kpis');
const label=document.createElement('label');label.style.cssText='display:grid;gap:3px;font-weight:850;color:#075d46';
label.textContent='प्रदेश के 52 स्रोत जिले';
const select=document.createElement('select');select.id='snStateDistrict';select.innerHTML='<option value="__ALL__">सभी 52 जिले — जिलावार रिपोर्ट</option><option value="__REWA__">रीवा संभाग — 6 जिले</option><option value="__BLOCK__">जनपदवार — सतना, मैहर, रीवा, मऊगंज</option><option value="__SATNA_MAIHAR_NOV__">नवंबर रिपोर्ट — सतना + मैहर</option>'+names.map(n=>'<option value="'+n+'">'+n+'</option>').join('');
label.appendChild(select);tools.insertBefore(label,tools.firstChild);
const metricLabel=document.createElement('label');metricLabel.style.cssText=label.style.cssText;metricLabel.textContent='रैंकिंग पैरामीटर';const metricSelect=document.createElement('select');metricSelect.id='snRankParameter';metricSelect.innerHTML='<option value="achievement">उपलब्धि %</option><option value="labour">आज संलग्न श्रमिक</option><option value="mr">मस्टर रोल जारी %</option>';metricLabel.appendChild(metricSelect);label.insertAdjacentElement('afterend',metricLabel);
const rank=document.createElement('div');rank.id='snSatnaRank';rank.style.cssText='display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:12px 0';
rank.innerHTML='<div class="sn-kpi"><small>सतना — प्रदेश में स्थान (52 स्रोत जिले)</small><strong id="snStateRank">तुलना डेटा उपलब्ध नहीं</strong></div><div class="sn-kpi"><small>सतना — रीवा संभाग में स्थान</small><strong id="snDivisionRank">तुलना डेटा उपलब्ध नहीं</strong><small>रीवा • मऊगंज • सतना • मैहर • सीधी • सिंगरौली</small></div>';
section.querySelector('.sn-head').insertAdjacentElement('afterend',rank);
const state=document.createElement('div');state.id='snStateDistrictReport';state.hidden=true;
state.innerHTML='<h3 id="snStateTitle" style="color:#075d46"></h3><p id="snStateDate" class="sn-warning"></p><div class="sn-wrap"><table class="sn-table"><thead>'+'<tr>'+ ["S.No","जिला नाम","कुल GPs","कार्य प्रगतिरत GPs","बिना प्रगतिरत कार्य GPs","बिना प्रगतिरत कार्य GPs %","वित्तीय वर्ष<br>2025–26 जुलाई<br>से नवंबर तक<br>NREGA लक्ष्य<br>दिवस (लाख)","कुल सृजित मानव दिवस<br>(लाख)","अंतर<br>(लाख)","शेष दिन","प्रतिदिन श्रमिक का लक्ष्य","आज संलग्न श्रमिक","उपलब्धि %","कमी","कुल प्रगतिरत कार्य","आज कार्यों पर जारी मस्टर रोल","मस्टर रोल जारी %"].map(h=>'<th>'+h+'</th>').join('')+'</tr>'+'</thead><tbody id="snStateRows"></tbody></table></div>';
originalWrap.insertAdjacentElement('afterend',state);
let sortColumn=null,sortDirection='desc';
const sortHeaders=[...state.querySelectorAll('thead th')];
sortHeaders.forEach((th,i)=>{
 if(i===0){th.textContent='क्र.';return;}
 const button=document.createElement('button');button.type='button';button.className='sn-column-sort';button.innerHTML=th.innerHTML+' <span class="sn-sort-arrow" aria-hidden="true">↕</span>';button.title='आरोही / अवरोही क्रम';button.setAttribute('aria-label',th.textContent+' — क्रम बदलें');th.replaceChildren(button);
 button.addEventListener('click',()=>{sortDirection=sortColumn===i?(sortDirection==='asc'?'desc':'asc'):(i===1?'asc':'desc');sortColumn=i;render();});
});
function gpStats(d){
 const sum=k=>d.rows.every(r=>r[k]!=null&&Number.isFinite(Number(r[k])))?d.rows.reduce((a,r)=>a+Number(r[k]),0):null;
 const total=sum('totalGP'),active=sum('workingGP');
 const inactive=total!=null&&active!=null&&active>=0&&active<=total?total-active:null;
 return [total,active,inactive,inactive==null||!total?null:inactive*100/total];
}
function sortValue(d,name,i,days){
 if(i===1)return name;
 if(!valid(d))return null;
 const sum=k=>d.rows.reduce((a,r)=>a+Number(r[k]||0),0),known=k=>d.rows.every(r=>r[k]!=null)?sum(k):null;
 const target=sum('target'),achievement=sum('vbgramJulyNovember'),gap=Math.max(0,target-achievement),daily=days?Math.ceil(gap/days):0,labour=known('todayLabour'),ongoing=known('ongoing'),mr=known('mrIssued');
 return [null,name,...gpStats(d),target,achievement,gap,days,daily,labour,achievement*100/target,labour==null?null:Math.max(0,daily-labour),ongoing,mr,ongoing==null||mr==null?null:ongoing?mr*100/ongoing:0][i];
}

const boxStyle=document.createElement('style');
boxStyle.textContent='#snStateDistrictReport .sn-wrap{border:2px solid #075d46;border-radius:10px;overflow:auto;background:#fff}#snStateDistrictReport table{border-collapse:collapse;width:100%}#snStateDistrictReport th,#snStateDistrictReport td{border:1px solid #739c8e!important;padding:9px 7px!important;vertical-align:middle}#snStateDistrictReport th{background:#075d46;color:#fff;font-size:15px;min-width:105px;white-space:normal}#snStateDistrictReport th:nth-child(1){min-width:42px}#snStateDistrictReport th:nth-child(2){min-width:160px}#snStateDistrictReport td{font-size:17px}#snStateDistrictReport .sn-missing{display:block;padding:5px;border:1px solid #b9c8c2;border-radius:4px;background:#f1f5f3;color:#56635d;font-size:12px;text-align:center}';
boxStyle.textContent+='#snStateDistrictReport th,#snStateDistrictReport td{border:2px solid #547c6f!important;font-weight:900!important}';
boxStyle.textContent+='#snStateDistrictReport .sn-table{table-layout:fixed;min-width:1580px}#snStateDistrictReport .sn-table th,#snStateDistrictReport .sn-table td{width:auto;min-width:0}#snStateDistrictReport .sn-table th:nth-child(1),#snStateDistrictReport .sn-table td:nth-child(1){width:42px}#snStateDistrictReport .sn-table th:nth-child(2),#snStateDistrictReport .sn-table td:nth-child(2){width:140px}#snStateDistrictReport .sn-table th:nth-child(3),#snStateDistrictReport .sn-table td:nth-child(3){width:120px}#snStateDistrictReport .sn-table td:nth-child(2){white-space:normal}#snStateDistrictReport .sn-table td:nth-child(3),#snStateDistrictReport .sn-table td:nth-child(4),#snStateDistrictReport .sn-table td:nth-child(5){text-align:right}#snStateDistrictReport .sn-missing{background:transparent;color:inherit;border:0;font-size:17px}@media print{#snStateDistrictReport .sn-table{min-width:0!important;width:100%!important}#snStateDistrictReport .sn-table th,#snStateDistrictReport .sn-table td{font-size:8.5pt!important;padding:1.2mm .6mm!important;width:auto!important;min-width:0!important}#snStateDistrictReport .sn-table td:nth-child(15),#snStateDistrictReport .sn-table td:nth-child(16){color:#111!important;background:#f2f2f2!important;font-weight:950!important}#snStateDistrictReport .sn-table th:nth-child(1),#snStateDistrictReport .sn-table td:nth-child(1){width:3%!important}#snStateDistrictReport .sn-table th:nth-child(2),#snStateDistrictReport .sn-table td:nth-child(2){width:10%!important}}';
boxStyle.textContent+='#snStateDistrictReport .sn-table td:nth-child(n+3){white-space:nowrap!important;word-break:normal!important;overflow-wrap:normal!important;font-variant-numeric:tabular-nums}#snStateDistrictReport .sn-table td{font-size:16px!important}#snStateDistrictReport .sn-table tr:last-child td{font-weight:950!important}@media print{#snStateDistrictReport .sn-table td{font-size:8.5pt!important}#snStateDistrictReport .sn-table tr:last-child td{font-size:8pt!important}#snStateDistrictReport .sn-table th:nth-child(1),#snStateDistrictReport .sn-table td:nth-child(1){width:3%!important}#snStateDistrictReport .sn-table th:nth-child(2),#snStateDistrictReport .sn-table td:nth-child(2){width:9%!important}#snStateDistrictReport .sn-table th:nth-child(3),#snStateDistrictReport .sn-table td:nth-child(3){width:8%!important}#snStateDistrictReport .sn-table th:nth-child(4),#snStateDistrictReport .sn-table td:nth-child(4){width:8%!important}#snStateDistrictReport .sn-table th:nth-child(5),#snStateDistrictReport .sn-table td:nth-child(5){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(6),#snStateDistrictReport .sn-table td:nth-child(6){width:8%!important}#snStateDistrictReport .sn-table th:nth-child(7),#snStateDistrictReport .sn-table td:nth-child(7){width:8%!important}#snStateDistrictReport .sn-table th:nth-child(8),#snStateDistrictReport .sn-table td:nth-child(8){width:4%!important}#snStateDistrictReport .sn-table th:nth-child(9),#snStateDistrictReport .sn-table td:nth-child(9){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(10),#snStateDistrictReport .sn-table td:nth-child(10){width:6%!important}#snStateDistrictReport .sn-table th:nth-child(15),#snStateDistrictReport .sn-table td:nth-child(15){width:5%!important}#snStateDistrictReport .sn-table th:nth-child(16),#snStateDistrictReport .sn-table td:nth-child(16){width:5%!important}#snStateDistrictReport .sn-table th:nth-child(13),#snStateDistrictReport .sn-table td:nth-child(13){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(14),#snStateDistrictReport .sn-table td:nth-child(14){width:9%!important}#snStateDistrictReport .sn-table th:nth-child(15),#snStateDistrictReport .sn-table td:nth-child(15){width:5%!important}}';
boxStyle.textContent+='#snStateDistrictReport .sn-table th:nth-child(1),#snStateDistrictReport .sn-table td:nth-child(1){width:3%!important}#snStateDistrictReport .sn-table th:nth-child(2),#snStateDistrictReport .sn-table td:nth-child(2){width:9%!important}#snStateDistrictReport .sn-table th:nth-child(3),#snStateDistrictReport .sn-table td:nth-child(3){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(4),#snStateDistrictReport .sn-table td:nth-child(4){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(5),#snStateDistrictReport .sn-table td:nth-child(5){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(6),#snStateDistrictReport .sn-table td:nth-child(6){width:8%!important}#snStateDistrictReport .sn-table th:nth-child(7),#snStateDistrictReport .sn-table td:nth-child(7){width:8%!important}#snStateDistrictReport .sn-table th:nth-child(8),#snStateDistrictReport .sn-table td:nth-child(8){width:3%!important}#snStateDistrictReport .sn-table th:nth-child(9),#snStateDistrictReport .sn-table td:nth-child(9){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(10),#snStateDistrictReport .sn-table td:nth-child(10){width:6%!important}#snStateDistrictReport .sn-table th:nth-child(15),#snStateDistrictReport .sn-table td:nth-child(15){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(16),#snStateDistrictReport .sn-table td:nth-child(16){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(13),#snStateDistrictReport .sn-table td:nth-child(13){width:7%!important}#snStateDistrictReport .sn-table th:nth-child(14),#snStateDistrictReport .sn-table td:nth-child(14){width:9%!important}#snStateDistrictReport .sn-table th:nth-child(15),#snStateDistrictReport .sn-table td:nth-child(15){width:5%!important}';
boxStyle.textContent+='#snStateDistrictReport .sn-table th{background:#075d46!important;color:#fff!important;text-align:center;line-height:1.05;padding:5px 3px!important}#snStateDistrictReport .sn-table td{padding:5px 3px!important;color:#102a43}#snStateDistrictReport .sn-table td:nth-child(15){text-align:center!important;background:#fff!important;color:#8b1010!important}#snStateDistrictReport .sn-table td:nth-child(16){background:#ffdddd!important;color:#8b1010!important}#snStateDistrictReport .sn-achievement-pill{display:inline-block;border:2px solid #8b1010;border-radius:20px;padding:3px 8px;background:#fff1f1;font-weight:950}#snStateDistrictReport .sn-table tr:last-child td{color:#fff}#snStateDistrictReport .sn-table tr:last-child td:nth-child(15),#snStateDistrictReport .sn-table tr:last-child td:nth-child(16){color:#8b1010}@media print{#snStateDistrictReport .sn-achievement-pill{border-color:#111;color:#111;padding:1px 3px}#snStateDistrictReport .sn-table th,#snStateDistrictReport .sn-table td{padding:1mm .5mm!important}}';
boxStyle.textContent+='#shramikNiyojanReport .sn-wrap{width:100%;max-width:100%;box-sizing:border-box}#shramikNiyojanReport .sn-table{width:100%!important;max-width:100%!important;min-width:0!important;table-layout:fixed!important}#shramikNiyojanReport .sn-table th,#shramikNiyojanReport .sn-table td{box-sizing:border-box!important;text-align:center!important;padding:5px 2px!important;min-width:0!important;vertical-align:middle!important}#shramikNiyojanReport .sn-table th{white-space:normal!important;overflow-wrap:anywhere!important;font-size:clamp(11px,.95vw,15px)!important;line-height:1.12!important}#shramikNiyojanReport .sn-table td{font-size:clamp(11px,.95vw,16px)!important;line-height:1.15!important}#shramikNiyojanReport .sn-table td:nth-child(2){white-space:normal!important;overflow-wrap:anywhere!important}#shramikNiyojanReport .sn-pct,#shramikNiyojanReport .sn-achievement-pill{box-sizing:border-box!important;min-width:0!important;max-width:100%!important;padding:3px 4px!important;font-size:inherit!important}#snStateDistrictReport .sn-table tr:last-child td{font-size:clamp(10px,.85vw,14px)!important}@media(max-width:800px){#shramikNiyojanReport .sn-table{min-width:1080px!important;max-width:none!important}}@media print{#shramikNiyojanReport .sn-table{min-width:0!important;max-width:100%!important}#shramikNiyojanReport .sn-table th,#shramikNiyojanReport .sn-table td{font-size:8pt!important;padding:1mm .4mm!important}#snStateDistrictReport .sn-table tr:last-child td{font-size:7.5pt!important}}';
boxStyle.textContent+='#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(2){white-space:nowrap!important;word-break:normal!important;overflow-wrap:normal!important;font-size:clamp(9px,.72vw,12px)!important;letter-spacing:0!important;text-align:center!important}@media print{#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(2){font-size:6.5pt!important;white-space:nowrap!important}}';
boxStyle.textContent+='#snStateDistrictReport .sn-column-sort{display:block;width:100%;border:0;background:transparent;color:inherit;font:inherit;font-weight:inherit;line-height:inherit;text-align:center;padding:0;cursor:pointer}#snStateDistrictReport .sn-column-sort:focus-visible{outline:2px solid #ffe066;outline-offset:2px}#snStateDistrictReport .sn-sort-arrow{display:inline-block;color:#ffe066;white-space:nowrap;font-size:14px}#snStateDistrictReport th[aria-sort=ascending] .sn-sort-arrow,#snStateDistrictReport th[aria-sort=descending] .sn-sort-arrow{color:#ffcb47;font-weight:950}@media print{#snStateDistrictReport .sn-sort-arrow{display:none}}';
boxStyle.textContent+='#shramikNiyojanReport #snStateDistrictReport .sn-table{min-width:1900px!important}#snStateDistrictReport .sn-table td:nth-child(6){color:#9b1717;background:#fff0ee}@media print{#shramikNiyojanReport #snStateDistrictReport .sn-table{min-width:0!important}}';
boxStyle.textContent+="#shramikNiyojanReport #snStateDistrictReport .sn-wrap{overflow-x:auto!important}#shramikNiyojanReport #snStateDistrictReport .sn-table{table-layout:fixed!important;width:2250px!important;min-width:2250px!important;max-width:none!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th{height:auto!important;white-space:normal!important;word-break:normal!important;overflow-wrap:normal!important;font-size:15px!important;line-height:1.3!important;padding:10px 6px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table td{font-size:17px!important;padding:9px 6px!important;white-space:nowrap!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(1),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(1){width:48px!important;min-width:48px!important;max-width:48px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(2),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(2){width:160px!important;min-width:160px!important;max-width:160px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(3),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(3){width:90px!important;min-width:90px!important;max-width:90px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(4),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(4){width:110px!important;min-width:110px!important;max-width:110px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(5),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(5){width:90px!important;min-width:90px!important;max-width:90px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(6),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(6){width:100px!important;min-width:100px!important;max-width:100px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(7),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(7){width:130px!important;min-width:130px!important;max-width:130px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(8),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(8){width:130px!important;min-width:130px!important;max-width:130px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(9),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(9){width:110px!important;min-width:110px!important;max-width:110px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(10),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(10){width:120px!important;min-width:120px!important;max-width:120px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(11),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(11){width:120px!important;min-width:120px!important;max-width:120px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(12),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(12){width:65px!important;min-width:65px!important;max-width:65px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(13),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(13){width:120px!important;min-width:120px!important;max-width:120px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(14),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(14){width:110px!important;min-width:110px!important;max-width:110px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(15),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(15){width:95px!important;min-width:95px!important;max-width:95px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(16),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(16){width:110px!important;min-width:110px!important;max-width:110px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(17),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(17){width:115px!important;min-width:115px!important;max-width:115px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(18),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(18){width:125px!important;min-width:125px!important;max-width:125px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(19),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(19){width:95px!important;min-width:95px!important;max-width:95px!important}@media print{#shramikNiyojanReport #snStateDistrictReport .sn-table{width:100%!important;min-width:0!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th,#shramikNiyojanReport #snStateDistrictReport .sn-table td{width:auto!important;min-width:0!important;max-width:none!important;font-size:7pt!important;padding:1mm .4mm!important}}";
boxStyle.textContent+="#shramikNiyojanReport #snStateDistrictReport .sn-table{width:1700px!important;min-width:1700px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th{font-size:14px!important;line-height:1.35!important;padding:8px 4px!important;overflow-wrap:normal!important}#shramikNiyojanReport #snStateDistrictReport .sn-table td{font-size:16px!important;padding:7px 4px!important}#snStateDistrictReport .sn-table tr:last-child td:nth-child(6){background:#ffe1db!important;color:#8b1717!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(1),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(1){width:36px!important;min-width:36px!important;max-width:36px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(2),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(2){width:140px!important;min-width:140px!important;max-width:140px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(3),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(3){width:70px!important;min-width:70px!important;max-width:70px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(4),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(4){width:95px!important;min-width:95px!important;max-width:95px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(5),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(5){width:110px!important;min-width:110px!important;max-width:110px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(6),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(6){width:110px!important;min-width:110px!important;max-width:110px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(7),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(7){width:105px!important;min-width:105px!important;max-width:105px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(8),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(8){width:105px!important;min-width:105px!important;max-width:105px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(9),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(9){width:90px!important;min-width:90px!important;max-width:90px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(10),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(10){width:95px!important;min-width:95px!important;max-width:95px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(11),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(11){width:90px!important;min-width:90px!important;max-width:90px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(12),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(12){width:50px!important;min-width:50px!important;max-width:50px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(13),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(13){width:100px!important;min-width:100px!important;max-width:100px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(14),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(14){width:90px!important;min-width:90px!important;max-width:90px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(15),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(15){width:75px!important;min-width:75px!important;max-width:75px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(16),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(16){width:85px!important;min-width:85px!important;max-width:85px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(17),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(17){width:95px!important;min-width:95px!important;max-width:95px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(18),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(18){width:105px!important;min-width:105px!important;max-width:105px!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(19),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(19){width:80px!important;min-width:80px!important;max-width:80px!important}@media print{@page{size:A4 landscape;margin:8mm}#shramikNiyojanReport,#snStateDistrictReport,#shramikNiyojanReport #snStateDistrictReport .sn-wrap{overflow:visible!important;max-height:none!important;height:auto!important}#shramikNiyojanReport #snStateDistrictReport .sn-table{display:table!important;width:100%!important;min-width:0!important;max-width:100%!important}#snStateDistrictReport thead{display:table-header-group!important}#snStateDistrictReport tbody{display:table-row-group!important}#snStateDistrictReport tr{break-inside:avoid!important;page-break-inside:avoid!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th,#shramikNiyojanReport #snStateDistrictReport .sn-table td{width:auto!important;min-width:0!important;max-width:none!important;font-size:7.5pt!important;line-height:1.25!important;padding:1.2mm .6mm!important;position:static!important}#snStateDistrictReport th{print-color-adjust:exact;-webkit-print-color-adjust:exact}#snStateDistrictReport .sn-table tr:last-child td:nth-child(6){color:#8b1717!important}}";
boxStyle.textContent+="@media print{@page{size:A4 portrait;margin:5mm}#shramikNiyojanReport #snStateDistrictReport .sn-table{width:100%!important;min-width:0!important;table-layout:fixed!important;break-inside:auto!important;page-break-inside:auto!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th,#shramikNiyojanReport #snStateDistrictReport .sn-table td{font-size:5pt!important;line-height:1.05!important;padding:.55mm .2mm!important;border-width:.15mm!important;letter-spacing:-.1px!important;width:auto!important;min-width:0!important;max-width:none!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th{font-size:5pt!important;word-break:normal!important;overflow-wrap:anywhere!important}#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(2){white-space:normal!important;overflow-wrap:anywhere!important;font-size:4.8pt!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(1),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(1){width:3%!important}#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(2),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(2){width:10%!important}#snStateDistrictReport .sn-achievement-pill,#snStateDistrictReport .sn-missing{font-size:inherit!important;padding:0!important;min-width:0!important}#snStateTitle{font-size:10pt!important;margin:0 0 2mm!important}#snStateDate{font-size:6pt!important;margin:0 0 2mm!important}#snStateDistrictReport .sn-wrap{border-width:.2mm!important;border-radius:0!important;overflow:visible!important;max-height:none!important}#snStateDistrictReport .sn-table tr:last-child td{font-size:5pt!important}}";
boxStyle.textContent+='@media screen{#shramikNiyojanReport #snStateDistrictReport .sn-table th:nth-child(12),#shramikNiyojanReport #snStateDistrictReport .sn-table td:nth-child(12){width:130px!important;min-width:130px!important;max-width:130px!important}}';
section.appendChild(boxStyle);
// Reuse the district-table design for the local Janpad table.
originalWrap.id='snLocalDistrictReport';
const localStyle=document.createElement('style');
localStyle.textContent=boxStyle.textContent.replace(/#snStateDistrictReport/g,'#snLocalDistrictReport').replace(/nth-child\((\d+)\)/g,(_,n)=>'nth-child('+(Number(n)===2?3:Number(n)>=3?Number(n)+3:Number(n))+')');
localStyle.textContent+='#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(2),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(2){width:90px!important;min-width:90px!important;max-width:90px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(4),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(4),#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(5),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(5){width:120px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table .sn-pct{font-size:inherit!important;white-space:nowrap!important;padding:3px 8px!important}@media print{#shramikNiyojanReport #snLocalDistrictReport .sn-table th,#shramikNiyojanReport #snLocalDistrictReport .sn-table td{width:auto!important;min-width:0!important;max-width:none!important}}';
// Local identity columns contain names, unlike the state's numeric columns.
localStyle.textContent+=`#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(-n+5),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(-n+5){white-space:normal!important;word-break:normal!important;overflow-wrap:anywhere!important;line-height:1.3!important;font-size:16px!important;max-width:none!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(4),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(4){width:160px!important;min-width:160px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(5),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(5){width:145px!important;min-width:145px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(n+2):nth-child(-n+5){text-align:left!important}@media print{#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(-n+5),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(-n+5){font-size:5pt!important;line-height:1.15!important;min-width:0!important;width:auto!important;white-space:normal!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(4),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(4){width:10%!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(5),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(5){width:9%!important}}`;

// Give name columns the space recovered from district and Janpad.
localStyle.textContent+=`#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(2),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(2){width:65px!important;min-width:65px!important;max-width:65px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(3),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(3){width:100px!important;min-width:100px!important;max-width:100px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(4),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(4){width:180px!important;min-width:180px!important;max-width:180px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(5),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(5){width:160px!important;min-width:160px!important;max-width:160px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(-n+5){white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important;line-height:1.3!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(2),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(3){font-size:14px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(4),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(5){font-size:16px!important;text-align:left!important}@media print{#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(-n+5),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(-n+5){width:auto!important;min-width:0!important;max-width:none!important;font-size:5pt!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(2),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(2){width:4%!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(3),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(3){width:6%!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(4),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(4){width:11%!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(5),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(5){width:10%!important}}`;

localStyle.textContent+=`#shramikNiyojanReport #snLocalDistrictReport .sn-table tr.sn-grand td,#shramikNiyojanReport #snLocalDistrictReport .sn-table tr.sn-total td{background:#075d46!important;color:#fff!important;border-color:#8fc6b5!important;font-weight:950!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table tr.sn-grand .sn-pct,#shramikNiyojanReport #snLocalDistrictReport .sn-table tr.sn-total .sn-pct{background:#fff!important;color:#075d46!important;border-color:#fff!important}`;
localStyle.textContent+=`@media screen{#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(2),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(2){width:50px!important;min-width:50px!important;max-width:50px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(3),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(3){width:80px!important;min-width:80px!important;max-width:80px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(n+6){overflow-wrap:normal!important;word-break:normal!important;font-variant-numeric:tabular-nums}#shramikNiyojanReport #snLocalDistrictReport .sn-table th{overflow-wrap:anywhere!important}}`;

localStyle.textContent+=`@media screen{#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(7),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(7),#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(8),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(8){width:70px!important;min-width:70px!important;max-width:70px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(9),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(9){width:78px!important;min-width:78px!important;max-width:78px!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(n+7):nth-child(-n+9){font-size:13px!important;padding:7px 3px!important;line-height:1.2!important}#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(n+7):nth-child(-n+9){padding:7px 3px!important}}`;
localStyle.textContent+=`@media screen{#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(3),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(3){width:110px!important;min-width:110px!important;max-width:110px!important}}`;
// Let report tables flow below the summary instead of moving as one print block.
localStyle.textContent+=`@media print{
#shramikNiyojanReport #snLocalDistrictReport,
#shramikNiyojanReport #snStateDistrictReport,
#shramikNiyojanReport #snStateDistrictReport .sn-wrap{
  overflow:visible!important;height:auto!important;max-height:none!important;
  break-inside:auto!important;page-break-inside:auto!important;
  break-before:auto!important;page-break-before:auto!important;
}
#shramikNiyojanReport #snLocalDistrictReport .sn-table,
#shramikNiyojanReport #snStateDistrictReport .sn-table{
  break-inside:auto!important;page-break-inside:auto!important;
}
#shramikNiyojanReport .sn-table th{position:static!important}
#shramikNiyojanReport .sn-table thead{display:table-header-group!important}
#shramikNiyojanReport .sn-table tr{break-inside:avoid!important;page-break-inside:avoid!important}
}`;
// Final local-table widths, after inherited state-table styles.
localStyle.textContent+=`@media screen{
#shramikNiyojanReport #snLocalDistrictReport .sn-table{min-width:1320px!important;table-layout:fixed!important}
#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(1),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(1){width:58px!important;min-width:58px!important;max-width:58px!important;white-space:nowrap!important;font-size:14px!important}
#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(2),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(2){width:78px!important;min-width:78px!important;max-width:78px!important;white-space:nowrap!important;font-size:16px!important}
#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(3),#shramikNiyojanReport #snLocalDistrictReport .sn-table td:nth-child(3){width:130px!important;min-width:130px!important;max-width:130px!important;font-size:16px!important;overflow-wrap:normal!important;word-break:normal!important}
#shramikNiyojanReport #snLocalDistrictReport .sn-table th:nth-child(-n+3){overflow-wrap:normal!important;word-break:normal!important;line-height:1.35!important}
#shramikNiyojanReport #snLocalDistrictReport .sn-table .sn-pct{box-sizing:border-box!important;min-width:0!important;max-width:100%!important;white-space:nowrap!important;font-size:14px!important;padding:3px!important}
}`;
section.appendChild(localStyle);

const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=v=>v==null?'—':Number(v).toLocaleString('en-IN');
const ongoingSnapshotDate='09-11-2026';
const novemberDate='10-11-2026';
// Official R6.9 district and Janpad figures, dated 10-11-2026.
const emuster=Object.fromEntries(`AGAR-MALWA|236|174|4753|3540
ALIRAJPUR|288|254|4843|843
ANUPPUR|277|3|10|6
ASHOK NAGAR|328|145|2347|1801
BALAGHAT|690|611|4274|1185
BARWANI|409|404|16477|2061
BETUL|554|323|2043|980
BHIND|439|15|65|50
BHOPAL|222|192|3245|2265
BURHANPUR|167|83|904|613
CHHATARPUR|559|348|3992|2333
CHHINDWARA|790|660|10548|2136
DAMOH|459|281|3430|1529
DATIA|290|5|27|11
DEWAS|496|298|3351|1288
DHAR|763|359|2605|1549
DINDORI|364|155|2659|347
GUNA|421|169|1866|1540
GWALIOR|263|0|0|0
HARDA|220|159|885|596
INDORE|334|145|701|341
JABALPUR|527|335|3252|1925
JHABUA|375|178|1949|804
KATNI|407|163|1625|313
KHANDWA|419|306|3263|1639
KHARGONE|589|527|9704|3109
MANDLA|490|327|3160|774
MANDSAUR|468|345|6272|3835
MORENA|478|0|0|0
NARMADAPURAM|427|366|2534|1934
NARSINGHPUR|450|375|3271|2534
NEEMUCH|243|178|1631|1077
NIWARI|136|125|1290|537
PANNA|386|161|1858|863
RAISEN|521|442|5573|3537
RAJGARH|622|479|12692|8456
RATLAM|419|352|7148|3579
REWA|820|677|5253|3544
SAGAR|766|521|3902|2858
SATNA|695|644|4109|2410
SEHORE|542|417|5261|3762
SEONI|635|476|7391|948
SHAHDOL|390|18|228|42
SHAJAPUR|352|279|4246|2824
SHEOPUR|236|0|0|0
SHIVPURI|587|4|11|11
SIDHI|400|386|6982|4305
SINGRAULI|316|313|6165|2486
TIKAMGARH|324|219|2916|1733
UJJAIN|609|462|3594|2307
UMARIA|236|13|74|16
VIDISHA|577|546|8246|5679
गंगेव|88|80|661|394
हनुमना|98|68|637|482
जवा|80|64|315|153
मऊगंज|82|79|817|471
नईगढ़ी|76|59|524|433
रायपुर कर्चुलियान|104|100|745|535
रीवा|92|85|560|382
सिरमौर|103|77|686|452
त्योंथर|97|65|308|242
अमरपाटन|75|64|336|229
मैहर|115|108|573|335
मझगवां|96|95|654|233
नागौद|94|85|756|438
रामनगर|55|55|255|187
रामपुर बघेलान|97|81|836|607
सोहावल|93|93|490|265
उचेहरा|70|63|209|116`.split('\n').map(line=>{
 const [name,...values]=line.split('|');
 const [totalGP,workingGP,todayLabour,mrIssued]=values.map(Number);
 return [name,{totalGP,workingGP,todayLabour,mrIssued}];
}));
const districtLabour={"AGAR-MALWA":4613,"ALIRAJPUR":4894,"ANUPPUR":8,"ASHOK NAGAR":2611,"BALAGHAT":4467,"BARWANI":16083,"BETUL":2039,"BHIND":101,"BHOPAL":3237,"BURHANPUR":959,"CHHATARPUR":3581,"CHHINDWARA":11212,"DAMOH":2248,"DATIA":29,"DEWAS":3417,"DHAR":2560,"DINDORI":2679,"GUNA":1906,"GWALIOR":0,"HARDA":801,"INDORE":762,"JABALPUR":3228,"JHABUA":1721,"KATNI":1727,"KHANDWA":3004,"KHARGONE":8706,"MANDLA":3101,"MANDSAUR":7009,"MORENA":0,"NARMADAPURAM":2461,"NARSINGHPUR":3332,"NEEMUCH":1782,"NIWARI":1199,"PANNA":1886,"RAISEN":5483,"RAJGARH":12613,"RATLAM":7456,"REWA":4433,"SAGAR":3411,"SATNA":4111,"SEHORE":5133,"SEONI":8144,"SHAHDOL":120,"SHAJAPUR":4536,"SHEOPUR":0,"SHIVPURI":10,"SIDHI":6784,"SINGRAULI":5981,"TIKAMGARH":2830,"UJJAIN":4501,"UMARIA":94,"VIDISHA":8331};
const blockLabour={"अमरपाटन":332,"मैहर":576,"रामनगर":326,"मझगवां":651,"नागौद":726,"रामपुर बघेलान":789,"सोहावल":490,"उचेहरा":221};
function parseNovember(text, labourByName, metrics={}) {
 return Object.fromEntries(text.trim().split('\n').map(line=>{
  const [name,...parts]=line.split('|'),[target,vbgramJulyNovember,labour]=parts.map(Number);
  return [name,{...metrics[name],target,vbgramJulyNovember,
   achievement:vbgramJulyNovember,todayLabour:labour??labourByName[name]}];
 }));
}
// Official S5.8 Total Works Ongoing, FY 2026–27.
const districtOngoing={"MORENA":7043,"BHIND":7621,"GWALIOR":6138,"DATIA":4099,"SHIVPURI":21244,"GUNA":13932,"TIKAMGARH":11772,"CHHATARPUR":12871,"PANNA":10345,"SAGAR":21478,"DAMOH":21189,"SATNA":15782,"REWA":17783,"SHAHDOL":4386,"SIDHI":16942,"MANDSAUR":24286,"RATLAM":13393,"UJJAIN":10397,"SHAJAPUR":8425,"DEWAS":10365,"JHABUA":19442,"DHAR":21629,"INDORE":3920,"KHARGONE":14355,"KHANDWA":12660,"RAJGARH":19768,"VIDISHA":18083,"BHOPAL":8729,"SEHORE":17804,"RAISEN":15119,"BETUL":13909,"NARMADAPURAM":13958,"JABALPUR":13366,"NARSINGHPUR":11890,"MANDLA":8975,"CHHINDWARA":12110,"SEONI":9238,"BALAGHAT":7337,"SHEOPUR":12013,"UMARIA":9123,"NEEMUCH":6832,"BARWANI":12766,"HARDA":4943,"KATNI":4015,"DINDORI":5938,"ANUPPUR":3566,"BURHANPUR":5297,"ASHOK NAGAR":21475,"ALIRAJPUR":6348,"SINGRAULI":9546,"AGAR-MALWA":18920,"NIWARI":3687};
const novemberDistricts=parseNovember(`AGAR-MALWA|804021|500061
ALIRAJPUR|1176343|310232
ANUPPUR|336661|105292
ASHOK NAGAR|1019851|399231
BALAGHAT|440465|204267
BARWANI|1298138|429448
BETUL|870866|262389
BHIND|193639|36993
BHOPAL|352583|192736
BURHANPUR|331842|153696
CHHATARPUR|1089599|330434
CHHINDWARA|1211574|786147
DAMOH|1504447|444546
DATIA|212223|49479
DEWAS|1350229|249113
DHAR|2516273|646919
DINDORI|1034295|1566060
GUNA|1070779|317578
GWALIOR|324748|56455
HARDA|290483|95650
INDORE|324021|110141
JABALPUR|810742|329131
JHABUA|928588|261146
KATNI|682126|319451
KHANDWA|1269827|330805
KHARGONE|2279680|530898
MANDLA|975995|408573
MANDSAUR|1312689|529657
MORENA|4728121|34790
NARMADAPURAM|630655|223265
NARSINGHPUR|554714|318472
NEEMUCH|477806|258117
NIWARI|136097|63121
PANNA|598360|129011
RAISEN|760298|419820
RAJGARH|1079319|689059
RATLAM|1274948|596484
REWA|775315|298916
SAGAR|966818|449799
SATNA|763652|189704
SEHORE|1010208|442411
SEONI|856160|243053
SHAHDOL|626178|198075
SHAJAPUR|828892|276332
SHEOPUR|1276795|184414
SHIVPURI|1739272|413552
SIDHI|941331|352884
SINGRAULI|1070426|201685
TIKAMGARH|389993|204198
UJJAIN|1371847|317430
UMARIA|453002|103684
VIDISHA|798604|689225`,districtLabour);
const novemberBlocks={
 सतना:parseNovember(`मझगवां|62985|14619
नागौद|93742|30502
रामपुर बघेलान|175416|32911
सोहावल|110216|16041
उचेहरा|60684|15481`,blockLabour),
 मैहर:parseNovember(`अमरपाटन|78203|22445
मैहर|94107|36066
रामनगर|88299|21639`,blockLabour),
 रीवा:parseNovember(`गंगेव|92802|40015|470
जवा|90617|19352|281
रायपुर कर्चुलियान|83366|41397|696
रीवा|66699|21786|527
सिरमौर|136879|23938|605
त्योंथर|54409|25651|292`,{},{
 'गंगेव':{totalGP:88,workingGP:64,mrIssued:328},'जवा':{totalGP:80,workingGP:56,mrIssued:136},
 'रायपुर कर्चुलियान':{totalGP:104,workingGP:99,mrIssued:503},'रीवा':{totalGP:92,workingGP:83,mrIssued:388},
 'सिरमौर':{totalGP:103,workingGP:70,mrIssued:405},'त्योंथर':{totalGP:97,workingGP:59,mrIssued:226}}),
 मऊगंज:parseNovember(`मऊगंज|68040|39591|597
हनुमना|108246|48353|564
नईगढ़ी|74257|41496|514`,{},{
 'मऊगंज':{totalGP:82,workingGP:77,mrIssued:387},'हनुमना':{totalGP:98,workingGP:56,mrIssued:439},
 'नईगढ़ी':{totalGP:76,workingGP:58,mrIssued:428}})
};
const janpadOngoing={"अमरपाटन":1401,"मैहर":2445,"मझगवां":2155,"नागौद":2482,"रामनगर":1238,"रामपुर बघेलान":3261,"सोहावल":1085,"उचेहरा":1701,"गंगेव":1476,"हनुमना":2631,"जवा":1437,"मऊगंज":1822,"नईगढ़ी":2321,"रायपुर कर्चुलियान":2625,"रीवा":1259,"सिरमौर":2210,"त्योंथर":2202};
function records(){
 const saved=window.SHRAMIK_DISTRICT_REPORTS?.labourDate===ongoingSnapshotDate?window.SHRAMIK_DISTRICT_REPORTS.districts:{};
 const wrap=rows=>({rows});
 const result=Object.fromEntries(Object.entries(novemberDistricts).map(([name,row])=>[
  name,wrap([{...(saved[name]?.rows[0]||{}),...row,...emuster[name],ongoing:districtOngoing[name]}])
 ]));
 for(const [district,blocks] of Object.entries(novemberBlocks)){
  const rows=Object.entries(blocks).map(([name,row])=>{
   const merged={...row,...emuster[name],ongoing:janpadOngoing[name]};
   result[district+' / '+name]=wrap([merged]);
   return merged;
  });
  result[district]=wrap(rows);
 }
 return result;
}
function valid(d){return d?.rows.length>0&&d.rows.every(r=>Number.isFinite(r.target)&&Number.isFinite(r.achievement));}
function score(d){
 if(!valid(d))return null;
 const sum=k=>d.rows.reduce((a,r)=>a+Number(r[k]),0),known=k=>d.rows.every(r=>r[k]!=null&&Number.isFinite(Number(r[k])));
 if(metricSelect.value==='labour')return known('todayLabour')?sum('todayLabour'):null;
 if(metricSelect.value==='mr')return known('mrIssued')&&known('ongoing')&&sum('ongoing')>0?sum('mrIssued')*100/sum('ongoing'):null;
 return sum('achievement')*100/sum('target');
}
function ranks(){
 const all=records();
 const rankFor=(list,satnaScore)=>satnaScore!=null&&list.every(n=>score(all[n])!=null)?(1+list.filter(n=>score(all[n])>satnaScore).length)+' / '+list.length:'तुलना डेटा उपलब्ध नहीं';
 document.getElementById('snStateRank').textContent=rankFor(sourceNames,score(all.SATNA));
 document.getElementById('snDivisionRank').textContent=rankFor(region,score(all['सतना']));
}
function render(){
 const selected=select.value, external=!!selected;
 originalWrap.hidden=external;originalKpis.hidden=false;state.hidden=!external;
 document.getElementById('snWarnings').hidden=external;
 section.querySelector('.sn-head h2').nextElementSibling.textContent=external?'वित्तीय वर्ष 2025–26 जुलाई से नवंबर के NREGA लक्ष्य के विरुद्ध वित्तीय वर्ष 2026–27 जुलाई से नवंबर की VB-G RAM G उपलब्धि':'वित्तीय वर्ष 2025–26 जुलाई से अक्टूबर में सृजित मानव दिवस के विरुद्ध वित्तीय वर्ष 2026–27 की उपलब्धि';
 if(external)document.getElementById('snDate').textContent='दिनांक '+novemberDate;
 for(const id of ['snLevel','snDistrict','snJanpad','snEngineer','snCluster','snSort']){const el=document.getElementById(id);if(el){const field=el.closest('label')||el;field.hidden=external;field.style.display=external?'none':'';}}
 for(const id of ['snLevel','snDistrict','snJanpad','snEngineer','snCluster','snSort']){const el=document.getElementById(id);if(el)el.disabled=external;}
 if(!external){const el=document.getElementById('snDistrict');el.value='ALL';el.dispatchEvent(new Event('change'));ranks();return;}
 const all=records();
 const chosen=[...(selected==='__ALL__'?sourceNames:selected==='__REWA__'?region:selected==='__BLOCK__'?Object.keys(all).filter(n=>n.includes(' / ')):selected==='__SATNA_MAIHAR_NOV__'?Object.keys(all).filter(n=>/^(सतना|मैहर) \/ /.test(n)):[selected])];
 const [day, month, year]=novemberDate.split('-').map(Number);
 const days=Math.max(0,(Date.UTC(2026,10,30)-Date.UTC(year,month-1,day))/86400000);
 if(sortColumn!=null)chosen.sort((a,b)=>{const av=sortValue(all[a],a,sortColumn,days),bv=sortValue(all[b],b,sortColumn,days);if(av==null||bv==null)return av==null?(bv==null?a.localeCompare(b):1):-1;const diff=typeof av==='string'?av.localeCompare(bv):av-bv;return (sortDirection==='asc'?diff:-diff)||a.localeCompare(b);});
 sortHeaders.forEach((th,i)=>{th.setAttribute('aria-sort',i===sortColumn?(sortDirection==='asc'?'ascending':'descending'):'none');const arrow=th.querySelector('.sn-sort-arrow');if(arrow)arrow.textContent=i===sortColumn?(sortDirection==='asc'?'↑':'↓'):'↕';});
 document.getElementById('snStateDate').textContent='दिनांक '+novemberDate;document.getElementById('snStateDate').hidden=true;
 document.getElementById('snStateTitle').textContent=selected==='__ALL__'?'प्रदेश के 52 जिले — जिलावार श्रमिक नियोजन रिपोर्ट':selected==='__REWA__'?'रीवा संभाग — जिलावार श्रमिक नियोजन रिपोर्ट':selected==='__BLOCK__'?'जनपदवार श्रमिक नियोजन रिपोर्ट':selected==='__SATNA_MAIHAR_NOV__'?'सतना + मैहर — नवंबर की जनपदवार श्रमिक नियोजन रिपोर्ट':selected+' — जिलावार श्रमिक नियोजन रिपोर्ट';
 const kpiRows=all['सतना'].rows.concat(all['मैहर'].rows);
 const kpiSum=k=>kpiRows.reduce((sum,row)=>sum+row[k],0);
 const kpiTarget=kpiSum('target'),kpiAchievement=kpiSum('achievement'),kpiGap=Math.max(0,kpiTarget-kpiAchievement),kpiDaily=Math.ceil(kpiGap/days);
 [fmt(kpiTarget),fmt(kpiAchievement),fmt(kpiGap),fmt(kpiDaily),(kpiAchievement*100/kpiTarget).toFixed(1)+'%',fmt(Math.max(0,kpiDaily-kpiSum('todayLabour')))].forEach((v,i)=>{const kpi=originalKpis.querySelectorAll('strong')[i];if(kpi)kpi.textContent=v;});
 const totals={totalGP:0,workingGP:0,inactiveGP:0,target:0,achievement:0,gap:0,daily:0,labour:0,ongoing:0,mr:0}, complete={totalGP:true,workingGP:true,inactiveGP:true,labour:true,ongoing:true,mr:true}, tb=document.getElementById('snStateRows');
 function cells(values){return values.map((v,j)=>'<td style="'+(j===1?'text-align:left;font-weight:850;':j===12?'text-align:right;font-weight:950;color:#06452b;background:#e6f2eb;':j===13?'text-align:right;font-weight:950;color:#7f1010;background:#fbeaea;':'text-align:right;font-weight:800;')+'">'+(v==null?'<span class="sn-missing">—</span>':typeof v==='string'?(j===12?'<span class="sn-achievement-pill">'+esc(v)+'</span>':esc(v)):(j>=6&&j<=8?Number(v/100000).toLocaleString('en-IN',{minimumFractionDigits:2,maximumFractionDigits:2}):fmt(v)))+'</td>').join('');}
 tb.innerHTML=chosen.map((name,i)=>{
  const d=all[name];if(!valid(d))return '<tr><td>'+ (i+1) +'</td><td>'+esc(name)+'</td><td colspan="15">समान अवधि के आँकड़े उपलब्ध नहीं हैं</td></tr>';
  const sum=k=>d.rows.reduce((a,r)=>a+Number(r[k]||0),0);
  const target=sum('target'),achievement=sum('vbgramJulyNovember'),gap=Math.max(0,target-achievement),daily=days?Math.ceil(gap/days):0;
  const known=k=>d.rows.every(r=>r[k]!=null)?sum(k):null;
  const labour=known('todayLabour'),ongoing=known('ongoing'),mr=known('mrIssued'),incomplete=known('incompleteWorks');
  for(const [k,v] of Object.entries({target,achievement,gap,daily}))totals[k]+=v;
  for(const [k,v] of Object.entries({labour,ongoing,mr})){if(v==null)complete[k]=false;else totals[k]+=v;}
  const gp=gpStats(d);
  for(const [j,k] of ['totalGP','workingGP','inactiveGP'].entries()){if(gp[j]==null)complete[k]=false;else totals[k]+=gp[j];}
  const values=[i+1,name,...gp.slice(0,3),gp[3]==null?null:gp[3].toFixed(2)+'%',target,achievement,gap,days,daily,labour,(achievement*100/target).toFixed(1)+'%',labour==null?null:Math.max(0,daily-labour),ongoing,mr,ongoing==null||mr==null?null:ongoing?(mr*100/ongoing).toFixed(1)+'%':'0.0%'];
  return '<tr'+(name==='SATNA'?' style="background:#d8f3df;"':'')+'>'+cells(values)+'</tr>';
 }).join('');
 if(chosen.every(n=>valid(all[n]))){totals.gap=Math.max(0,totals.target-totals.achievement);totals.daily=Math.ceil(totals.gap/days);tb.innerHTML+='<tr style="background:#075d46;color:white;">'+cells(['','योग',complete.totalGP?totals.totalGP:null,complete.workingGP?totals.workingGP:null,complete.inactiveGP?totals.inactiveGP:null,complete.totalGP&&complete.workingGP&&totals.totalGP>0?((totals.totalGP-totals.workingGP)*100/totals.totalGP).toFixed(2)+'%':null,totals.target,totals.achievement,totals.gap,days,totals.daily,complete.labour?totals.labour:null,(totals.achievement*100/totals.target).toFixed(1)+'%',complete.labour?Math.max(0,totals.daily-totals.labour):null,complete.ongoing?totals.ongoing:null,complete.mr?totals.mr:null,complete.ongoing&&complete.mr?(totals.ongoing?(totals.mr*100/totals.ongoing).toFixed(1):'0.0')+'%':null])+'</tr>';}
 ranks();
}
document.getElementById('snExcel').addEventListener('click',e=>{if(!select.value)return;e.preventDefault();e.stopImmediatePropagation();const table=state.querySelector('table'),lines=[...table.rows].map(r=>[...r.cells].map(c=>'"'+c.innerText.replace(/"/g,'""')+'"').join(',')).join('\r\n'),a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\ufeff'+lines],{type:'text/csv;charset=utf-8'}));a.download=(select.value==='__SATNA_MAIHAR_NOV__'?'Shramik_Satna_Maihar_November_':'Shramik_Report_')+novemberDate+'.csv';a.click();URL.revokeObjectURL(a.href)},true);

const singlePrint=document.createElement('button');
singlePrint.type='button';singlePrint.textContent='एक पेज Print / PDF';singlePrint.style.cssText='padding:8px 12px;background:#075d46;color:white;border:0;border-radius:6px;font-weight:800';
tools.appendChild(singlePrint);
singlePrint.addEventListener('click',()=>{
 if(!select.value){
  const source=originalWrap.querySelector('table');
  const copy=source.cloneNode(true);
  const hidden=[...source.tHead.rows[0].cells].map((c,i)=>getComputedStyle(c).display==='none'?i:-1).filter(i=>i>=0);
  for(const row of copy.rows){if(row.cells.length!==source.tHead.rows[0].cells.length)continue;for(const i of [...hidden].reverse())row.cells[i].remove();}
  copy.querySelectorAll('colgroup').forEach(c=>c.remove());
  const count=copy.tHead.rows[0].cells.length;
  const identity=document.getElementById('snLevel').value==='engineer'?[3,5,9,12,10]:[3,5,10];
  const remainder=(100-identity.reduce((a,b)=>a+b,0))/(count-identity.length);
  const cg=document.createElement('colgroup');for(let i=0;i<count;i++){const c=document.createElement('col');c.style.width=(identity[i]??remainder)+'%';cg.appendChild(c)}copy.prepend(cg);
  const frame=document.createElement('iframe');frame.style.cssText='position:fixed;width:1100px;height:800px;left:-12000px;top:0;border:0';document.body.appendChild(frame);
  const doc=frame.contentDocument;
  doc.open();doc.write('<!doctype html><html><head><meta charset="utf-8"><title>श्रमिक नियोजन</title><style>@page{size:A4 landscape;margin:5mm}*{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}body{margin:0;font-family:"Nirmala UI",Mangal,Arial,sans-serif}h2{font-size:13pt;margin:0 0 2mm}.date{text-align:right;font-size:8pt;margin:0 0 2mm}table{width:100%;table-layout:fixed;border-collapse:collapse}thead{display:table-header-group}tr{break-inside:avoid}th,td{border:.25mm solid #547c6f;padding:1.1mm .5mm;font-size:7pt;line-height:1.3;width:auto!important;min-width:0!important;max-width:none!important}th{background:#075d46;color:white;text-align:center;overflow-wrap:normal;word-break:normal}td{font-weight:800;text-align:center;white-space:nowrap}td:nth-child(3){white-space:normal;word-break:normal}span,button{font:inherit;min-width:0!important;max-width:100%;padding:0!important;border:0!important;background:transparent!important;color:inherit!important}.sn-sort-arrow{display:none}.sn-grand,.sn-total{background:#dcece5}.sn-shortage{background:#ffe0df;color:#8b1717}</style></head><body><h2>श्रमिक नियोजन — मानव दिवस लक्ष्य एवं उपलब्धि</h2><p class="date">'+esc(document.getElementById('snDate').textContent)+'</p>'+copy.outerHTML+'</body></html>');doc.close();
  frame.contentWindow.focus();setTimeout(()=>frame.contentWindow.print(),300);frame.contentWindow.onafterprint=()=>setTimeout(()=>frame.remove(),1000);return;
 }
 const frame=document.createElement('iframe');frame.style.cssText='position:fixed;width:1px;height:1px;left:-10000px;top:0;border:0';document.body.appendChild(frame);
 const doc=frame.contentDocument;
 const title=document.getElementById('snStateTitle').textContent;
 const date=document.getElementById('snStateDate').textContent;
 doc.open();doc.write('<!doctype html><html><head><meta charset="utf-8"><title>'+esc(title)+'</title><style>@page{size:A4 portrait;margin:5mm}*{box-sizing:border-box}body{margin:0;font-family:Arial,sans-serif;color:#102e3b}h2{font-size:10pt;margin:0 0 2mm}p{font-size:6pt;margin:0 0 2mm}table{border-collapse:collapse;table-layout:fixed;width:100%;font-variant-numeric:tabular-nums}thead{display:table-header-group}tr{break-inside:avoid;height:3.7mm}th,td{border:.15mm solid #66877c!important;font-size:5pt!important;line-height:1.08!important;padding:.4mm .2mm!important;min-width:0!important;width:auto!important;height:auto!important;max-width:none!important;white-space:normal!important;overflow-wrap:anywhere}th{background:#075d46!important;color:white!important;font-weight:bold}th:first-child,td:first-child{width:3%!important}th:nth-child(2),td:nth-child(2){width:10%!important}td:nth-child(n+3){white-space:nowrap!important}span,button{font:inherit!important;padding:0!important;border:0!important;background:transparent!important;color:inherit!important;min-width:0!important}button{display:block;width:100%}.sn-sort-arrow{display:none}tbody tr:last-child td{background:#dcece5!important;color:#102e3b!important;font-weight:bold}*{-webkit-print-color-adjust:exact;print-color-adjust:exact}</style></head><body><h2>'+esc(title)+'</h2><p>'+esc(date)+'</p>'+state.querySelector('table').outerHTML+'</body></html>');doc.close();
 frame.contentWindow.focus();setTimeout(()=>frame.contentWindow.print(),300);
 frame.contentWindow.onafterprint=()=>setTimeout(()=>frame.remove(),1000);
});

// Route the normal Print/PDF button through the same isolated local layout.
const localPrintButton=document.getElementById('snReadablePrint');
if(localPrintButton)localPrintButton.addEventListener('click',event=>{
 event.preventDefault();event.stopImmediatePropagation();singlePrint.click();
},true);
metricSelect.addEventListener('change',ranks);select.addEventListener('change',render);
document.getElementById('shramikNiyojanLauncher').addEventListener('click',render);
new MutationObserver(()=>{if(select.value&&!section.classList.contains('sn-cluster-mode'))render();}).observe(originalKpis,{childList:true});
render();
})();

