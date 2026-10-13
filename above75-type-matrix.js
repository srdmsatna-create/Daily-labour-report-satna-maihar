/* Work-type rows and Janpad columns, with separate district totals. */
(()=>{
 const blocks=[['AMARPATAN','अमरपाटन'],['MAIHAR','मैहर'],['RAMNAGAR','रामनगर'],['MAJHGAWAN','मझगवाँ'],['NAGOD','नागौद'],['RAMPURBAGHELAN','रामपुर बघेलान'],['SOHAWAL','सोहावल'],['UNCHAHARA','उचेहरा']];
 function block(v){const k=String(v||'').toUpperCase().replace(/[^A-Z0-9]/g,'');return k==='SATNA'?'SOHAWAL':k;}
 function aggregate(records){
  const groups=new Map(),totals=Array(8).fill(0);
  for(const r of records){const i=blocks.findIndex(b=>b[0]===block(r.janpad));if(i<0)throw Error('जनपद का मिलान नहीं: '+r.janpad);const type=r.type||'प्रकार उपलब्ध नहीं';if(!groups.has(type))groups.set(type,Array(8).fill(0));groups.get(type)[i]++;totals[i]++;}
  return {groups,totals};
 }
 // Exposed only for verification; does not change the source data.
 window.workTypeMatrixAggregate=aggregate;
 const original=renderSummary;
 renderSummary=function(){
  if(reportView!=='typeMatrix')return original();
  const target=document.getElementById('summaryReport');
  document.getElementById('workReport').style.display='none';target.style.display='block';
  document.querySelectorAll('[data-summary-view]').forEach(b=>b.classList.toggle('active',b.dataset.summaryView===reportView));
  try{
   const {groups,totals}=aggregate(shown),sum=(xs,a,b)=>xs.slice(a,b).reduce((x,y)=>x+y,0);
   const cells=xs=>xs.slice(0,3).map(x=>'<td class="num">'+n(x)+'</td>').join('')+'<td class="num district-total">'+n(sum(xs,0,3))+'</td>'+xs.slice(3).map(x=>'<td class="num">'+n(x)+'</td>').join('')+'<td class="num district-total">'+n(sum(xs,3,8))+'</td><td class="num grand-total">'+n(sum(xs,0,8))+'</td>';
   let serial=0;
   const rows=[...groups].sort((a,b)=>a[0].localeCompare(b[0],'hi',{numeric:true})).map(([type,xs])=>'<tr><td class="num">'+n(++serial)+'</td><th scope="row">'+esc(type)+'</th>'+cells(xs)+'</tr>').join('');
   target.innerHTML='<h2>कार्य-प्रकारवार / जनपदवार गोशवारा — कार्य संख्या</h2><table class="work-type-matrix"><thead><tr><th rowspan="2">क्रमांक</th><th rowspan="2">कार्य का प्रकार</th><th colspan="4">मैहर जिला</th><th colspan="6">सतना जिला</th><th rowspan="2" class="grand-total">दोनों जिले<br>महायोग</th></tr><tr>'+blocks.slice(0,3).map(b=>'<th>'+b[1]+'</th>').join('')+'<th class="district-total">मैहर योग</th>'+blocks.slice(3).map(b=>'<th>'+b[1]+'</th>').join('')+'<th class="district-total">सतना योग</th></tr></thead><tbody>'+rows+'</tbody><tfoot><tr><th colspan="2">जनपद / जिला / दोनों जिलों का कुल योग</th>'+cells(totals)+'</tr></tfoot></table>';
  }catch(e){target.textContent=e.message;}
 };
 const style=document.createElement('style');style.textContent='.work-type-matrix{min-width:1100px;table-layout:fixed}.work-type-matrix th,.work-type-matrix td{padding:7px 4px;text-align:center;border:1px solid #314b63}.work-type-matrix th:nth-child(2){width:200px}.work-type-matrix tbody th{text-align:left;background:#fff}.work-type-matrix .district-total{background:#e0ebf6;font-weight:800}.work-type-matrix .grand-total{background:#c9e7d5;font-weight:900}.work-type-matrix tfoot{font-weight:900;background:#eef2f5}@media print{.work-type-matrix{min-width:0;width:100%;font-size:9pt}.work-type-matrix th,.work-type-matrix td{font-size:9pt!important;padding:5px 2px!important}.work-type-matrix th:nth-child(2){width:160px}}';document.head.append(style);
})();
