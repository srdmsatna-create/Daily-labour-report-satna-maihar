'use strict';
(()=>{
const $=id=>document.getElementById(id),esc=v=>String(v??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const names={AMARPATAN:'अमरपाटन',MAIHAR:'मैहर',RAMNAGAR:'रामनगर',MAJHGAWAN:'मझगवां',NAGOD:'नागौद','RAMPUR BAGHELAN':'रामपुर बघेलान',SATNA:'सोहावल',UNCHAHARA:'उचेहरा'},titles={mr:'लंबित मस्टरोल',first:'FTO — प्रथम हस्ताक्षर हेतु लंबित',second:'FTO — द्वितीय हस्ताक्षर हेतु लंबित'};
const district=b=>['AMARPATAN','MAIHAR','RAMNAGAR'].includes(b)?'MAIHAR':'SATNA',dn=d=>d==='MAIHAR'?'मैहर':'सतना',fmt=n=>n.toLocaleString('en-IN');let data={reports:{}},key='mr',exportRows=[];
function filter(rows){return rows.filter(r=>($('district').value==='ALL'||district(r.block)===$('district').value)&&($('block').value==='ALL'||r.block===$('block').value))}
function updateBlocks(){const old=$('block').value;const bs=Object.keys(names).filter(b=>$('district').value==='ALL'||district(b)===$('district').value);$('block').innerHTML='<option value="ALL">सभी जनपद</option>'+bs.map(b=>'<option value="'+b+'">'+names[b]+'</option>').join('');if(bs.includes(old))$('block').value=old}
function render(){
 const report=data.reports[key]||{},valid=report.available===true,rows=filter(report.rows||[]),gp=$('view').value==='gp';
 $('title').textContent=titles[key];$('date').textContent='स्रोत तिथि: '+(valid?report.sourceDate:'उपलब्ध नहीं');
 for(const k of Object.keys(titles)){const r=data.reports[k];$(k+'Count').textContent=r?.available?fmt(filter(r.rows).reduce((s,x)=>s+x.pending,0)):'—'}
 document.querySelectorAll('[role=tab]').forEach(b=>b.setAttribute('aria-selected',String(b.dataset.key===key)));
 const heads=['क्र.','जिला','जनपद',...(gp?['ग्राम पंचायत']:[]),titles[key]];$('head').innerHTML='<tr>'+heads.map(h=>'<th>'+esc(h)+'</th>').join('')+'</tr>';
 $('status').textContent=valid?'आधिकारिक स्रोत से प्राप्त रिपोर्ट; नीचे चयनित फ़िल्टर का विवरण है।':'इस रिपोर्ट का आधिकारिक स्रोत जुड़ना शेष है। आँकड़े उपलब्ध नहीं हैं; इन्हें शून्य नहीं माना गया है।';
 $('source').replaceChildren();if(valid&&report.source){const a=document.createElement('a');a.href=report.source;a.target='_blank';a.rel='noopener noreferrer';a.textContent='आधिकारिक स्रोत खोलें ↗';$('source').append(a)}
 exportRows=[heads];$('export').disabled=!valid;
 if(!valid){$('body').innerHTML='<tr><td colspan="'+heads.length+'" class="empty">'+esc(titles[key])+' — डेटा उपलब्ध नहीं</td></tr>';return}
 let display=rows;if(!gp){const groups=new Map();for(const r of rows){if(!groups.has(r.block))groups.set(r.block,{block:r.block,pending:0});groups.get(r.block).pending+=r.pending}display=[...groups.values()]}
 display.sort((a,b)=>a.block.localeCompare(b.block)||(a.panchayat||'').localeCompare(b.panchayat||''));
 $('body').innerHTML=display.map((r,i)=>{const line=[i+1,dn(district(r.block)),names[r.block],...(gp?[r.panchayat]:[]),r.pending];exportRows.push(line);return '<tr>'+line.map((v,j)=>'<td'+(j===line.length-1?' class="num"':'')+'>'+esc(v)+'</td>').join('')+'</tr>'}).join('')||'<tr><td class="empty" colspan="'+heads.length+'">चयनित फ़िल्टर में कोई रिकॉर्ड नहीं है।</td></tr>';
 if(display.length){const total=rows.reduce((s,r)=>s+r.pending,0);$('body').innerHTML+='<tr class="total"><td colspan="'+(heads.length-1)+'">चयनित विवरण का योग</td><td class="num">'+fmt(total)+'</td></tr>';exportRows.push(['चयनित विवरण का योग',...Array(heads.length-2).fill(''),total])}
}
async function load(){try{const res=await fetch('data/pending-mr-fto.json?t='+Date.now(),{cache:'no-store'});if(!res.ok)throw Error('report unavailable');const next=await res.json();if(next.schemaVersion!==1)throw Error('invalid schema');for(const k of Object.keys(titles)){const r=next.reports?.[k];if(!r||!Array.isArray(r.rows))throw Error('invalid report');if(r.available&&(!r.sourceDate||!r.source||!r.rows.length||r.rows.some(x=>!names[x.block]||!x.panchayat||!Number.isInteger(x.pending)||x.pending<0)))throw Error('invalid rows')}data=next;render()}catch(e){data={reports:{}};render();$('status').textContent='रिपोर्ट फ़ाइल नहीं पढ़ी जा सकी। ताज़ा करें; उपलब्ध न होने को शून्य नहीं माना गया है।'}}
$('district').onchange=()=>{updateBlocks();render()};$('block').onchange=$('view').onchange=render;$('reset').onclick=()=>{$('district').value='ALL';updateBlocks();$('block').value='ALL';render()};document.querySelectorAll('[role=tab]').forEach(b=>b.onclick=()=>{key=b.dataset.key;render()});$('print').onclick=()=>window.print();$('refresh').onclick=load;
$('export').onclick=()=>{const cell=v=>'"'+String(typeof v==='string'&&/^[=+@\-]/.test(v)?"'"+v:v).replace(/"/g,'""')+'"';const csv='\ufeff'+exportRows.map(r=>r.map(cell).join(',')).join('\r\n');const url=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));const a=document.createElement('a');a.href=url;a.download='pending-'+key+'.csv';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)};updateBlocks();load();
})();
