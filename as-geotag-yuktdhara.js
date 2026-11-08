/* R33.1 GP-verified counts, shared with the daily updater. */
(()=>{
'use strict';
const Y=window.YUKTDHARA_RECEIVED,D=window.AS_GEOTAG_BEFORE,M=window.YUKTDHARA_DATA,T=window.SECURE_TS_DATA;
const fields=['worksReceived','worksCreated','yetToStart'],labels=['Works Received from Yuktdhara','Works Created in VB-G RAM G','Works yet to Start'];
const e=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const norm=v=>String(v||'').toUpperCase().replace(/[^A-Z0-9\u0900-\u097F]/g,''),block=v=>({SATNA:'SOHAWAL',RAMPORBAGHELAN:'RAMPURBAGHELAN'}[norm(v)]||norm(v));
const district=b=>['AMARPATAN','MAIHAR','RAMNAGAR'].includes(block(b))?'MAIHAR':'SATNA',fmt=v=>v==null?'—':Number(v).toLocaleString('en-IN');
const sum=(rows,k)=>rows.length&&rows.every(r=>r[k]!=null)?rows.reduce((s,r)=>s+Number(r[k]),0):null;
const cells=rows=>fields.map(k=>'<td class="yd-num">'+fmt(sum(rows,k))+'</td>').join('');
const table=document.querySelector('#janpadPanel table');table.querySelector('thead tr').insertAdjacentHTML('beforeend',labels.map(l=>'<th class="yd-head">'+l+'</th>').join(''));
for(const tr of document.querySelectorAll('#summaryRows tr')){
 const d=tr.cells[0].textContent,b=tr.cells[1].textContent;
 const rr=(Y?.blocks||[]).filter(r=>tr.classList.contains('total')||b==='जिला योग'?tr.classList.contains('total')||district(r.block)===d:block(r.block)===block(b));
 tr.insertAdjacentHTML('beforeend',cells(rr));
}
// Build the AS/Before and SECURE crosswalk from the official GP code (the
// first component of each VB-G RAM G work code), not from display names.
const secureYdWorks=(T?.works||[]).filter(w=>/(?:^|\\/)YD(?:\\/|$)/i.test(String(w.code||'')));
const ydTsByPcode=new Map();
for(const w of secureYdWorks){const pcode=String(w.pcode||String(w.code||'').split('/')[0]);ydTsByPcode.set(pcode,(ydTsByPcode.get(pcode)||0)+1)}
const gpByCode=new Map((T?.panchayats||[]).map(g=>[String(g.pcode||''),{
 district:g.district,block:g.janpad,panchayat:g.panchayat,pcode:String(g.pcode||''),
 tsCount:ydTsByPcode.get(String(g.pcode||''))||0,asAvailable:0,beforeAvailable:0,beforeNotAvailable:0,unknown:0
}]));
let crosswalkRows=0;
for(const w of (D?.rows||[])){
 const code=String(w.workCode||''),pcode=code.split('/')[0],g=gpByCode.get(pcode);
 if(!g)continue;
 crosswalkRows++;
 if(w.asStatus==='Available')g.asAvailable++;
 if(w.beforePhotoStatus==='Available')g.beforeAvailable++;
 if(w.beforePhotoStatus==='Not Available')g.beforeNotAvailable++;
 if(w.beforePhotoStatus==='Unknown')g.unknown++;
}
const gpSummary=[...gpByCode.values()];
const hasVerifiedBreakdown=gpSummary.length===695 && rows.length>0 && crosswalkRows===rows.length;
const panel=document.createElement('section');panel.id='engineerPanel';panel.className='panel';panel.style.marginTop='10px';
panel.innerHTML='<div class="section-title-row"><h2>जिला / जनपद / उपयंत्रीवार योग</h2><button class="section-print" onclick="printReport(\'engineer\')">उपयंत्री PDF Print</button></div><div class="filters"><select id="ydDistrict"><option value="">सभी जिले</option><option>MAIHAR</option><option>SATNA</option></select><select id="ydBlock"><option value="">सभी जनपद</option></select><input id="ydEngineer" type="search" placeholder="उपयंत्री खोजें"></div><div class="wrap"><table class="summary"><thead><tr><th>जिला</th><th>जनपद</th><th>उपयंत्री</th><th>SECURE से जारी TS संख्या (/YD/)</th><th>AS से जारी संख्या</th><th>Before Geo Tag किए गए कार्य</th><th>शेष Geo Tag (APO / GRS / सचिव)</th>'+labels.map(l=>'<th class="yd-head">'+l+'</th>').join('')+'</tr></thead><tbody id="ydEngineers"></tbody></table></div><p class="meta" id="ydMeta"></p>';
document.getElementById('janpadPanel').after(panel);
if(!hasVerifiedBreakdown){const warning=document.createElement('p');warning.className='meta';warning.textContent='GP/उपयंत्रीवार AS–SECURE TS crosswalk उपलब्ध नहीं है। इन चार कॉलमों में — का अर्थ स्रोत डेटा उपलब्ध नहीं है।';panel.appendChild(warning)}
const mapping=new Map((M?.mapping||[]).map(r=>[block(r.janpad)+'|'+norm(r.gp),r.engineer]));
const groups=new Map((Y?.rows||[]).map(r=>[block(r.janpad)+'|'+r.engineer,{...r,ts:0,as:0,geo:0}]));
for(const r of gpSummary){const engineer=mapping.get(block(r.block)+'|'+norm(r.panchayat))||'मैपिंग उपलब्ध नहीं',key=block(r.block)+'|'+engineer;if(!groups.has(key))groups.set(key,{janpad:r.block,engineer,ts:0,as:0,geo:0});const a=groups.get(key);a.ts+=Number(r.tsCount||0);a.as+=Number(r.asAvailable||0);a.geo+=Number(r.beforeAvailable||0)}
const rows=[...groups.values()].sort((a,b)=>district(a.janpad).localeCompare(district(b.janpad))||a.janpad.localeCompare(b.janpad)||a.engineer.localeCompare(b.engineer,'hi'));
const $=id=>document.getElementById(id);
function fillBlocks(){const d=$('ydDistrict').value;$('ydBlock').innerHTML='<option value="">सभी जनपद</option>'+[...new Set(rows.filter(r=>!d||district(r.janpad)===d).map(r=>r.janpad))].map(b=>'<option value="'+e(b)+'">'+e(block(b)==='SOHAWAL'?'SOHAWAL':b)+'</option>').join('')}
function metric(rr){if(!hasVerifiedBreakdown)return Array(4).fill('<td class="yd-num">—</td>').join('')+cells(rr);const ts=sum(rr,'ts'),as=sum(rr,'as'),geo=sum(rr,'geo');return [ts,as,geo,as-geo].map(v=>'<td class="yd-num">'+fmt(v)+'</td>').join('')+cells(rr)}
function render(){const d=$('ydDistrict').value,b=$('ydBlock').value,q=$('ydEngineer').value.trim().toLowerCase(),rr=rows.filter(r=>(!d||district(r.janpad)===d)&&(!b||r.janpad===b)&&(!q||r.engineer.toLowerCase().includes(q)));let html='';for(const dd of ['MAIHAR','SATNA']){const dr=rr.filter(r=>district(r.janpad)===dd);if(!dr.length)continue;for(const bb of [...new Set(dr.map(r=>r.janpad))]){const br=dr.filter(r=>r.janpad===bb);for(const r of br)html+='<tr><td>'+dd+'</td><td>'+e(block(bb)==='SOHAWAL'?'SOHAWAL':bb)+'</td><td>'+e(r.engineer)+'</td>'+metric([r])+'</tr>';html+='<tr class="janpad-total"><td>'+dd+'</td><td>'+e(bb)+'</td><td>जनपद योग</td>'+metric(br)+'</tr>'}html+='<tr class="'+dd.toLowerCase()+'"><td>'+dd+'</td><td colspan="2">जिला योग</td>'+metric(dr)+'</tr>'}html+=rr.length?'<tr class="total"><td colspan="3">कुल योग</td>'+metric(rr)+'</tr>':'<tr><td colspan="11">कोई रिकॉर्ड नहीं मिला।</td></tr>';$('ydEngineers').innerHTML=html}
fillBlocks();render();$('ydDistrict').onchange=()=>{fillBlocks();render()};$('ydBlock').onchange=render;$('ydEngineer').oninput=render;
const diffs=(Y?.blocks||[]).filter(r=>r.summaryYetToStart!=null&&r.summaryYetToStart!==r.yetToStart);
const note='R33.1 • '+(Y?.officialDate||'डेटा उपलब्ध नहीं')+' • पंचायत विवरण से उपयंत्री, जनपद एवं जिला योग। '+diffs.map(r=>(block(r.block)==='SOHAWAL'?'SOHAWAL':r.block)+': Works yet to Start — जनपद स्रोत '+r.summaryYetToStart+', पंचायत विवरण '+r.yetToStart+'; यहाँ पंचायत विवरण का योग लिया गया है।').join(' ')+(Y?.success===false?' पिछला सत्यापित डेटा; नवीन fetch असफल।':'');
$('ydMeta').textContent=note;const source=document.createElement('p');source.className='meta';source.textContent=note;document.getElementById('janpadPanel').append(source);
})();
