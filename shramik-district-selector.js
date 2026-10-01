(function(){
'use strict';
const section=document.getElementById('shramikNiyojanReport');
if(!section)return;
const names=["AGAR-MALWA","ALIRAJPUR","ANUPPUR","ASHOK NAGAR","BALAGHAT","BARWANI","BETUL","BHIND","BHOPAL","BURHANPUR","CHHATARPUR","CHHINDWARA","DAMOH","DATIA","DEWAS","DHAR","DINDORI","GUNA","GWALIOR","HARDA","INDORE","JABALPUR","JHABUA","KATNI","KHANDWA","KHARGONE","MANDLA","MANDSAUR","MORENA","NARMADAPURAM","NARSINGHPUR","NEEMUCH","NIWARI","PANNA","RAISEN","RAJGARH","RATLAM","REWA","SAGAR","SATNA","SEHORE","SEONI","SHAHDOL","SHAJAPUR","SHEOPUR","SHIVPURI","SIDHI","SINGRAULI","TIKAMGARH","UJJAIN","UMARIA","VIDISHA"], region=['REWA','SATNA','SIDHI','SINGRAULI'];
const tools=section.querySelector('.sn-tools'), originalWrap=section.querySelector('.sn-wrap'), originalKpis=section.querySelector('.sn-kpis');
const label=document.createElement('label');label.style.cssText='display:grid;gap:3px;font-weight:850;color:#075d46';
label.textContent='प्रदेश के 52 स्रोत जिले';
const select=document.createElement('select');select.id='snStateDistrict';select.innerHTML='<option value="">वर्तमान सतना + मैहर रिपोर्ट</option>'+names.map(n=>'<option value="'+n+'">'+n+'</option>').join('');
label.appendChild(select);tools.insertBefore(label,tools.firstChild.nextSibling);
const rank=document.createElement('div');rank.id='snSatnaRank';rank.style.cssText='display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:10px;margin:12px 0';
rank.innerHTML='<div class="sn-kpi"><small>सतना — प्रदेश में स्थान (52 स्रोत जिले)</small><strong id="snStateRank">तुलना डेटा उपलब्ध नहीं</strong></div><div class="sn-kpi"><small>सतना — रीवा संभाग में स्थान</small><strong id="snDivisionRank">तुलना डेटा उपलब्ध नहीं</strong><small>रीवा • सतना • सीधी • सिंगरौली</small></div>';
section.querySelector('.sn-head').insertAdjacentElement('afterend',rank);
const state=document.createElement('div');state.id='snStateDistrictReport';state.hidden=true;
state.innerHTML='<h3 id="snStateTitle" style="color:#075d46"></h3><div class="sn-wrap"><table class="sn-table"><thead>'+originalWrap.querySelector('thead').innerHTML+'</thead><tbody id="snStateRows"></tbody></table></div>';
originalWrap.insertAdjacentElement('afterend',state);
const esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const fmt=v=>v==null?'—':Number(v).toLocaleString('en-IN');
function records(){return window.SHRAMIK_DISTRICT_REPORTS?.districts||{};}
function valid(d){return d&&d.officialDate===window.SHRAMIK_NIYOJAN?.officialDate&&d.period==='2025-26-Jul-Oct_vs_2026-27-Jul-Sep-Oct'&&Array.isArray(d.rows)&&d.rows.length>0&&d.rows.every(r=>Number(r.target)>0&&Number.isFinite(Number(r.achievement)));}
function score(d){const t=d.rows.reduce((a,r)=>a+Number(r.target),0),a=d.rows.reduce((a,r)=>a+Number(r.achievement),0);return a*100/t;}
function ranks(){
 const all=records(),satna=all.SATNA;
 document.getElementById('snStateRank').textContent=names.every(n=>valid(all[n]))?(1+names.filter(n=>score(all[n])>score(satna)).length)+' / 52':'तुलना डेटा उपलब्ध नहीं';
 document.getElementById('snDivisionRank').textContent=region.every(n=>valid(all[n]))?(1+region.filter(n=>score(all[n])>score(satna)).length)+' / 4':'तुलना डेटा उपलब्ध नहीं';
}
function render(){
 const selected=select.value,external=selected&&selected!=='SATNA';
 originalWrap.hidden=!!external;originalKpis.hidden=!!external;state.hidden=!external;
 for(const id of ['snLevel','snDistrict','snJanpad','snEngineer','snCluster','snSort','snExcel']){const el=document.getElementById(id);if(el)el.disabled=!!external;}
 if(selected==='SATNA'){
  const district=document.getElementById('snDistrict');district.value='SATNA';district.dispatchEvent(new Event('change'));
 }else if(!selected){
  const district=document.getElementById('snDistrict');district.value='ALL';district.dispatchEvent(new Event('change'));
 }
 if(external){
  document.getElementById('snStateTitle').textContent=selected+' — श्रमिक नियोजन';
  const d=records()[selected],tb=document.getElementById('snStateRows');
  if(!valid(d)){tb.innerHTML='<tr><td colspan="18" style="text-align:center;padding:24px">इस जिले की समान अवधि की सत्यापित जनपदवार रिपोर्ट अभी उपलब्ध नहीं है।</td></tr>';}
  else tb.innerHTML=d.rows.map((r,i)=>{
   const days=Number(window.SHRAMIK_NIYOJAN.remainingOctoberDays),gap=Math.max(0,Number(r.target)-Number(r.achievement)),daily=days?Math.ceil(gap/days):0;
   const values=[i+1,selected,r.janpad,'—','—',r.target,r.julyToSeptemberAchievement,r.octoberAchievement,r.achievement,gap,days,daily,r.todayLabour,(Number(r.achievement)/Number(r.target)*100).toFixed(1)+'%',r.todayLabour==null?null:Math.max(0,daily-r.todayLabour),r.ongoing,r.mrIssued,r.ongoing?((r.mrIssued||0)/r.ongoing*100).toFixed(1)+'%':'—'];
   return '<tr>'+values.map((v,j)=>'<td>'+(j<5||typeof v==='string'?esc(v):fmt(v))+'</td>').join('')+'</tr>';
  }).join('');
 }
 ranks();
}
select.addEventListener('change',render);ranks();
})();
