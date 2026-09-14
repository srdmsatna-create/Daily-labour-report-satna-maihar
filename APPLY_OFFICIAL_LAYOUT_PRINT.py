from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start='<!-- ===== OFFICIAL LAYOUT PRINT V2 ===== -->'
end='<!-- ===== END OFFICIAL LAYOUT PRINT V2 ===== -->'
if start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+s[b:]

block=r'''
<!-- ===== OFFICIAL LAYOUT PRINT V2 ===== -->
<style>
body[data-report-view="official"] .report-card,
body[data-report-view="official"] .report-head,
body[data-report-view="official"] #reportTable,
body[data-report-view="official"] #reportTable th,
body[data-report-view="official"] #reportTable td,
body[data-report-view="official"] #officialPrintBar{
  font-family:"Times New Roman", Times, serif!important;
}
body[data-report-view="official"] .table-wrap{width:100%!important;max-width:100%!important;overflow-x:auto!important;border-radius:8px!important}
body[data-report-view="official"] #reportTable{border-collapse:collapse!important;min-width:1180px!important;width:100%!important;table-layout:auto!important}
/* Header compact; body data large and clear. */
body[data-report-view="official"] #reportTable th{font-size:14px!important;font-weight:700!important;padding:5px 3px!important;line-height:1.08!important;white-space:normal!important;word-break:normal!important;overflow-wrap:normal!important;text-align:center!important}
body[data-report-view="official"] #reportTable td{font-size:19px!important;font-weight:700!important;padding:5px 3px!important;line-height:1.06!important;white-space:normal!important;word-break:normal!important;overflow-wrap:normal!important}
body[data-report-view="official"] #reportTable th,body[data-report-view="official"] #reportTable td{border:1.3px solid #6489a3!important;vertical-align:middle!important;min-width:40px!important}
body[data-report-view="official"] #reportTable .print-select-col{width:32px!important;min-width:32px!important;max-width:32px!important;text-align:center!important;white-space:nowrap!important;padding:2px!important}
body[data-report-view="official"] #reportTable th:nth-child(2),body[data-report-view="official"] #reportTable td:nth-child(2){min-width:58px!important;width:58px!important;white-space:nowrap!important}
body[data-report-view="official"] #reportTable th:nth-child(3),body[data-report-view="official"] #reportTable td:nth-child(3){min-width:102px!important;width:102px!important;white-space:normal!important}
body[data-report-view="official"] #reportTable th:nth-child(4),body[data-report-view="official"] #reportTable td:nth-child(4){min-width:82px!important;width:82px!important}
body[data-report-view="official"] #reportTable th:nth-child(5),body[data-report-view="official"] #reportTable td:nth-child(5){min-width:62px!important;width:62px!important}
body[data-report-view="official"] #reportTable th:nth-child(n+6),body[data-report-view="official"] #reportTable td:nth-child(n+6){min-width:46px!important}
body[data-report-view="official"] #reportTable th:last-child,body[data-report-view="official"] #reportTable td:last-child{min-width:54px!important;width:54px!important;max-width:54px!important}
body[data-report-view="official"] #reportTable tbody tr.total-row td{font-size:19px!important;font-weight:700!important}
body[data-report-view="official"] #officialPrintBar{display:flex;gap:8px;align-items:center;flex-wrap:wrap;margin:8px 0 10px}
body[data-report-view="official"] #officialPrintBar button{font-family:"Times New Roman", Times, serif!important;border:1px solid #4d7898;background:#eef8ff;color:#173f60;padding:7px 10px;border-radius:8px;font-size:14px;font-weight:700;cursor:pointer}
body[data-report-view="official"] #officialPrintBar .count{font-size:14px;font-weight:700;color:#31536d}
@media(max-width:900px){body[data-report-view="official"] #reportTable{min-width:1160px!important}body[data-report-view="official"] #reportTable th{font-size:13px!important}body[data-report-view="official"] #reportTable td{font-size:18px!important}}
@media print{#officialPrintBar,.print-select-col{display:none!important}}
</style>
<script>
(function(){
  const txt=e=>String(e?.textContent||'').replace(/\s+/g,' ').trim();
  const VASULI={'RAMPUR BAGHELAN':44,'MAIHAR':59,'NAGOD':155,'MAJHGAWAN':41,'UNCHAHARA':51,'AMARPATAN':71,'RAMNAGAR':61,'SATNA':67};
  function isOfficial(){return document.body?.dataset?.reportView==='official'||/Official Janpad Daily Report/i.test(txt(document.getElementById('viewTitle')))}
  function compactHeader(t){
    if(!t?.tHead||t.tHead.rows.length<2||!t.tBodies.length)return;
    const h1=t.tHead.rows[0],h2=t.tHead.rows[1],body=t.tBodies[0];
    [...h1.cells].forEach(th=>{if(/ALL TYPES OF WORKS/i.test(txt(th)))th.textContent='All Types of Works'});
    const hs=[...h2.cells].map(x=>txt(x).toUpperCase());
    const a=hs.indexOf('TOTAL GP'),b=hs.indexOf('GP PROGRESS');
    if(a>=0&&b>=0){
      const grp=[...h1.cells].find(x=>txt(x).toUpperCase()==='GRAM PANCHAYAT');
      if(grp)grp.colSpan=Math.max(1,(parseInt(grp.colSpan||'3',10)-1));
      h2.cells[b].textContent='GP Progress / Total GPs';
      h2.deleteCell(a);
      [...body.rows].forEach(tr=>{
        if(tr.cells.length<4)return;
        const total=txt(tr.cells[2]),prog=txt(tr.cells[3]);
        tr.cells[3].textContent=prog+' / '+total;
        tr.deleteCell(2);
      });
    } else if(b>=0){
      h2.cells[b].textContent='GP Progress / Total GPs';
    }
  }
  function addChecks(t){
    const h1=t.tHead.rows[0],body=t.tBodies[0];
    if(!h1.querySelector('.print-select-col')){
      const th=document.createElement('th');th.textContent='Select';th.rowSpan=2;th.className='print-select-col';h1.insertBefore(th,h1.firstChild);
    }
    [...body.rows].forEach(tr=>{
      if(tr.querySelector('.print-select-col'))return;
      const td=document.createElement('td');td.className='print-select-col';
      if(!tr.classList.contains('total-row')&&!/^TOTAL$/i.test(txt(tr.cells[0]))){const c=document.createElement('input');c.type='checkbox';c.className='official-print-check';c.onchange=updateCount;td.appendChild(c)}
      tr.insertBefore(td,tr.firstChild);
    });
  }
  function patchVasuli(t){
    if(!t?.tBodies?.length)return;
    [...t.tBodies[0].rows].forEach(tr=>{
      if(!tr.cells.length)return;
      const vals=[...tr.cells].map(c=>txt(c).toUpperCase());
      const isTotal=tr.classList.contains('total-row')||vals.includes('TOTAL')||vals.includes('योग');
      const cell=tr.cells[tr.cells.length-1];
      if(isTotal){cell.textContent='549';cell.style.setProperty('background','#0f766e','important');cell.style.setProperty('color','#fff','important');cell.style.setProperty('font-weight','700','important');return}
      const jp=txt(tr.cells[2]).toUpperCase();
      if(!Object.prototype.hasOwnProperty.call(VASULI,jp))return;
      const v=VASULI[jp];
      cell.textContent=String(v);
      cell.style.setProperty('background','#dcfce7','important');
      cell.style.setProperty('color','#166534','important');
      cell.style.setProperty('font-weight','700','important');
    });
  }
  function updateCount(){const e=document.getElementById('officialPrintCount');if(e)e.textContent=document.querySelectorAll('.official-print-check:checked').length}
  function addBar(t){
    if(document.getElementById('officialPrintBar'))return;
    const wrap=t.closest('.table-wrap')||t.parentElement;if(!wrap)return;
    const b=document.createElement('div');b.id='officialPrintBar';
    b.innerHTML='<button id="selAllOff">Select All</button><button id="clearOff">Clear</button><button id="printOff">Print Selected</button><span class="count">Selected: <b id="officialPrintCount">0</b></span>';
    wrap.parentNode.insertBefore(b,wrap);
    document.getElementById('selAllOff').onclick=()=>{document.querySelectorAll('.official-print-check').forEach(x=>x.checked=true);updateCount()};
    document.getElementById('clearOff').onclick=()=>{document.querySelectorAll('.official-print-check').forEach(x=>x.checked=false);updateCount()};
    document.getElementById('printOff').onclick=()=>{
      const rows=[...t.tBodies[0].rows].filter(r=>r.querySelector('.official-print-check:checked'));
      if(!rows.length){alert('Pehle jis Janpad ka print chahiye use select kariye.');return}
      const c=t.cloneNode(true);[...c.tHead.rows].forEach(r=>{if(r.cells[0]?.classList.contains('print-select-col'))r.deleteCell(0)});
      c.tBodies[0].innerHTML='';rows.forEach(r=>{const x=r.cloneNode(true);if(x.cells[0]?.classList.contains('print-select-col'))x.deleteCell(0);c.tBodies[0].appendChild(x)});
      const w=window.open('','_blank','width=1500,height=950');if(!w)return;
      w.document.write('<html><head><title>Official Janpad Daily Report</title><style>@page{size:A4 landscape;margin:6mm}body{font-family:"Times New Roman",Times,serif;padding:4px}table{border-collapse:collapse;width:100%;table-layout:auto}th,td{font-family:"Times New Roman",Times,serif;border:1px solid #56758d;padding:4px 3px;text-align:center;vertical-align:middle}th{background:#dfeaf4;font-weight:700;font-size:11px}td{font-size:14px;font-weight:700}</style></head><body><h2>Official Janpad Daily Report</h2>'+c.outerHTML+'<script>window.onload=()=>window.print()<\/script></body></html>');w.document.close();
    };
  }
  function run(){const old=document.getElementById('officialPrintBar');if(old)old.style.display=isOfficial()?'flex':'none';if(!isOfficial())return;const t=document.getElementById('reportTable');if(!t)return;compactHeader(t);addChecks(t);patchVasuli(t);addBar(t);updateCount()}
  let lock=false;const sched=()=>{if(lock)return;lock=true;requestAnimationFrame(()=>{lock=false;run()})};
  const boot=()=>{run();new MutationObserver(sched).observe(document.body,{childList:true,subtree:true});document.addEventListener('click',()=>setTimeout(run,30),true)};
  document.readyState==='loading'?document.addEventListener('DOMContentLoaded',boot):boot();
})();
</script>
<!-- ===== END OFFICIAL LAYOUT PRINT V2 ===== -->
'''
if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: Official Janpad Times New Roman font applied')
