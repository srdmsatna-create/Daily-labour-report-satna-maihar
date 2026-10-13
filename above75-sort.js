/* Sort report columns; retain totals at the bottom. */
(()=>{
 const collator=new Intl.Collator('hi',{numeric:true,sensitivity:'base'});
 function value(cell){const text=(cell?.textContent||'').trim();const clean=text.replace(/[₹,%\s]/g,'');return /^-?\d+(?:\.\d+)?$/.test(clean)?Number(clean):text;}
 function sort(table,index,direction){
 const body=table.tBodies[0];if(!body)return;
 const rows=[...body.rows],totals=rows.filter(r=>r.querySelector('[colspan]')||/^(?:कुल योग|योग|कुल)$/.test(r.cells[0]?.textContent.trim()));
 const records=rows.filter(r=>!totals.includes(r));
 records.sort((a,b)=>{const x=value(a.cells[index]),y=value(b.cells[index]);return direction*(typeof x==='number'&&typeof y==='number'?x-y:collator.compare(String(x),String(y)));});
 body.append(...records,...totals);
 table.dataset.sortColumn=index;table.dataset.sortDirection=direction;
 table.querySelectorAll('thead th').forEach((th,i)=>{th.setAttribute('aria-sort',i===index?(direction===1?'ascending':'descending'):'none');const arrow=th.querySelector('.sort-arrow');if(arrow)arrow.textContent=i===index?(direction===1?' ▲':' ▼'):' ↕';});
 }
 function install(){document.querySelectorAll('table').forEach(table=>{
 table.querySelectorAll('thead tr:last-child th').forEach((th,index)=>{
 if(th.dataset.sortReady)return;th.dataset.sortReady='1';th.tabIndex=0;th.style.cursor='pointer';th.title='क्लिक: आरोही ▲ / अवरोही ▼';th.setAttribute('aria-sort','none');
 const arrow=document.createElement('span');arrow.className='sort-arrow';arrow.textContent=' ↕';arrow.setAttribute('aria-hidden','true');th.append(arrow);
 const activate=()=>sort(table,index,Number(table.dataset.sortColumn)===index&&table.dataset.sortDirection==='1'?-1:1);
 th.addEventListener('click',activate);th.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();activate();}});
 });
 });}
 const style=document.createElement('style');style.textContent='.sort-arrow{white-space:nowrap;color:#135e99;font-weight:900}';document.head.append(style);
 install();new MutationObserver(records=>{if(records.some(r=>[...r.addedNodes].some(n=>n.nodeType===1&&(n.matches('table,thead,th')||n.querySelector('thead')))))install();}).observe(document.body,{childList:true,subtree:true});
})();
