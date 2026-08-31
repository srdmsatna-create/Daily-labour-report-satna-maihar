from pathlib import Path
import re, sys, datetime

repo = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path.cwd()
idx = repo/'index.html'
if not idx.exists():
    print('ERROR: index.html not found:', idx)
    sys.exit(2)

s = idx.read_text(encoding='utf-8', errors='ignore')
orig = s

# Remove prior V3 zero mandays script block if present
s = re.sub(r'\s*<!-- SRDM_ZERO_MANDAYS_FINAL_V3_START -->.*?<!-- SRDM_ZERO_MANDAYS_FINAL_V3_END -->\s*', '\n', s, flags=re.S)
s = re.sub(r'\s*<!-- SRDM_ZERO_MANDAYS_FINAL_V4_START -->.*?<!-- SRDM_ZERO_MANDAYS_FINAL_V4_END -->\s*', '\n', s, flags=re.S)
# Remove any prior zero tab buttons only, preserving other tabs
s = re.sub(r'<button[^>]*id=["\']srdmZeroMandaysBtn["\'][^>]*>.*?</button>\s*', '', s, flags=re.S|re.I)

# Insert button immediately after Mandays Generation tab when possible
pat = re.compile(r'(<button[^>]*data-view=["\']mandaysgen["\'][^>]*>.*?Mandays Generation.*?</button>)', re.I|re.S)
m = pat.search(s)
if not m:
    print('ERROR: Mandays Generation tab not found in index.html; patch aborted.')
    sys.exit(3)
button = '<button class="tab mandays-tab" id="srdmZeroMandaysBtn" data-view="zeromandays" style="border:2px solid #b42318!important;background:#fff4f2!important;color:#8a1c13!important;font-weight:800!important">Zero Mandays Generation</button>'
s = s[:m.end()] + button + s[m.end():]

# V4 logic: always reads existing window.SRDM_V8_MONTHLY data used by Mandays Generation
script = r'''
<!-- SRDM_ZERO_MANDAYS_FINAL_V4_START -->
<style id="srdmZeroV4Style">
#srdmZeroMandaysBtn{display:inline-flex!important;visibility:visible!important;opacity:1!important;position:relative!important;z-index:999!important}
#srdmZeroTools{display:flex;flex-wrap:wrap;gap:8px;align-items:center;margin:10px 0;padding:10px;border:1px solid #ddd;border-radius:10px;background:#fff}
#srdmZeroTools select,#srdmZeroTools button{padding:7px 9px;border:1px solid #bbb;border-radius:8px;background:#fff}
#srdmZeroSummary{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:8px;margin:10px 0}
#srdmZeroSummary .zcard{padding:10px 12px;border:1px solid #ead7d4;border-radius:10px;background:#fff8f7}.zcard small{display:block;color:#666}.zcard b{font-size:20px}
</style>
<script>
(function(){
 const $=id=>document.getElementById(id), clean=x=>String(x??'').trim(), esc=x=>clean(x).replace(/[&<>\"]/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','\"':'&quot;'}[m]));
 const districtOf=j=>/^(AMARPATAN|MAIHAR|RAMNAGAR)$/i.test(clean(j))?'MAIHAR':'SATNA';
 function getData(){
   const a=Array.isArray(window.SRDM_V8_MONTHLY)?window.SRDM_V8_MONTHLY:[];
   return a.map(r=>({janpad:clean(r.janpad||r.Janpad||r.block),engineer:clean(r.engineer||r.Engineer||r.subengineer||r.subEngineer)||'Unmapped',cluster:clean(r.cluster||r.Cluster)||'Unmapped',panchayat:clean(r.panchayat||r.gp||r.GP||r.gramPanchayat),All:Number(r.All||0),April:Number(r.April||0),May:Number(r.May||0),June:Number(r.June||0),July:Number(r.July||0),August:Number(r.August||0)})).filter(r=>r.janpad&&r.panchayat);
 }
 function opts(id,arr,label){const e=$(id);if(!e)return;e.innerHTML='<option value="ALL">'+label+'</option>'+arr.map(v=>'<option value="'+esc(v)+'">'+esc(v)+'</option>').join('')}
 function state(){return {m:$('zmMonth')?.value||'August',d:$('zmDistrict')?.value||'ALL',j:$('zmJanpad')?.value||'ALL',e:$('zmEngineer')?.value||'ALL',c:$('zmCluster')?.value||'ALL',g:$('zmGP')?.value||'ALL'}}
 function match(r,f,level=5){if(level>=1&&f.d!=='ALL'&&districtOf(r.janpad)!==f.d)return false;if(level>=2&&f.j!=='ALL'&&r.janpad!==f.j)return false;if(level>=3&&f.e!=='ALL'&&r.engineer!==f.e)return false;if(level>=4&&f.c!=='ALL'&&r.cluster!==f.c)return false;if(level>=5&&f.g!=='ALL'&&r.panchayat!==f.g)return false;return true}
 function cascade(changed){const D=getData(),f=state();
   if(changed==='zmDistrict'){if($('zmJanpad'))$('zmJanpad').value='ALL';if($('zmEngineer'))$('zmEngineer').value='ALL';if($('zmCluster'))$('zmCluster').value='ALL';if($('zmGP'))$('zmGP').value='ALL'}
   if(changed==='zmJanpad'){if($('zmEngineer'))$('zmEngineer').value='ALL';if($('zmCluster'))$('zmCluster').value='ALL';if($('zmGP'))$('zmGP').value='ALL'}
   if(changed==='zmEngineer'){if($('zmCluster'))$('zmCluster').value='ALL';if($('zmGP'))$('zmGP').value='ALL'}
   if(changed==='zmCluster'){if($('zmGP'))$('zmGP').value='ALL'}
   let q=state(); opts('zmJanpad',[...new Set(D.filter(r=>q.d==='ALL'||districtOf(r.janpad)===q.d).map(r=>r.janpad))].sort(),'सभी Janpad'); if(q.j!=='ALL'&&[...$('zmJanpad').options].some(o=>o.value===q.j))$('zmJanpad').value=q.j;
   q=state(); opts('zmEngineer',[...new Set(D.filter(r=>match(r,q,2)).map(r=>r.engineer))].sort(),'सभी Sub Engineer'); if(q.e!=='ALL'&&[...$('zmEngineer').options].some(o=>o.value===q.e))$('zmEngineer').value=q.e;
   q=state(); opts('zmCluster',[...new Set(D.filter(r=>match(r,q,3)).map(r=>r.cluster))].sort(),'सभी Cluster'); if(q.c!=='ALL'&&[...$('zmCluster').options].some(o=>o.value===q.c))$('zmCluster').value=q.c;
   q=state(); opts('zmGP',[...new Set(D.filter(r=>match(r,q,4)).map(r=>r.panchayat))].sort(),'सभी GP'); if(q.g!=='ALL'&&[...$('zmGP').options].some(o=>o.value===q.g))$('zmGP').value=q.g;
 }
 function zeroRows(){const f=state(),D=getData();const fld=f.m==='FY Total'?'All':f.m;return D.filter(r=>match(r,f,5)&&Number(r[fld]||0)===0)}
 function draw(){if(document.body.dataset.reportView!=='zeromandays')return;const f=state(),D=getData(),d=zeroRows(),fld=f.m==='FY Total'?'All':f.m,table=$('reportTable');if(!table)return;
   const all=D.filter(r=>match(r,f,5)),md=all.reduce((a,r)=>a+Number(r[fld]||0),0),gp=new Set(d.map(r=>r.janpad+'|'+r.panchayat));
   table.innerHTML='<thead><tr><th>SN</th><th>District</th><th>Janpad</th><th>Sub Engineer</th><th>Cluster</th><th>GP Name</th><th>Period</th><th>Mandays</th></tr></thead><tbody>'+d.map((r,i)=>`<tr><td>${i+1}</td><td>${districtOf(r.janpad)}</td><td>${esc(r.janpad)}</td><td>${esc(r.engineer)}</td><td>${esc(r.cluster)}</td><td>${esc(r.panchayat)}</td><td>${esc(f.m)}</td><td><b>0</b></td></tr>`).join('')+`<tr class="total-row"><td colspan="6">TOTAL ZERO MANDAYS GP</td><td>${esc(f.m)}</td><td>${gp.size.toLocaleString('en-IN')}</td></tr></tbody>`;
   const sm=$('srdmZeroSummary');if(sm)sm.innerHTML=`<div class="zcard"><small>Zero Mandays GP</small><b>${gp.size.toLocaleString('en-IN')}</b></div><div class="zcard"><small>Filtered GP Rows</small><b>${all.length.toLocaleString('en-IN')}</b></div><div class="zcard"><small>Total Mandays</small><b>${md.toLocaleString('en-IN')}</b></div><div class="zcard"><small>Period</small><b>${esc(f.m)}</b></div>`;
   if($('viewMeta'))$('viewMeta').textContent=`Zero Mandays GP Monitoring | ${f.m} | ${gp.size} Zero GP | Source: SRDM_V8_MONTHLY (${D.length} GP rows)`;
 }
 function renderZero(){document.body.dataset.reportView='zeromandays';document.querySelectorAll('.tab').forEach(x=>x.classList.remove('active'));$('srdmZeroMandaysBtn')?.classList.add('active');if($('viewTitle'))$('viewTitle').textContent='Zero Mandays Generation — GP Monitoring';
   ['srdmV8Tools','srdmV8Alert','srdmMandayTools','srdmMandayAlert','srdmMonthSummary','srdmZeroTools','srdmZeroSummary'].forEach(id=>$(id)?.remove()); const table=$('reportTable');if(!table)return;
   const tools=document.createElement('div');tools.id='srdmZeroTools';tools.innerHTML='<b>Zero Mandays Filters:</b><select id="zmMonth"><option>FY Total</option><option>April</option><option>May</option><option>June</option><option>July</option><option selected>August</option></select><select id="zmDistrict"><option value="ALL">सभी District</option><option value="SATNA">SATNA</option><option value="MAIHAR">MAIHAR</option></select><select id="zmJanpad"></select><select id="zmEngineer"></select><select id="zmCluster"></select><select id="zmGP"></select><button id="zmReset">Reset</button>';
   table.parentElement?.insertBefore(tools,table);const sm=document.createElement('div');sm.id='srdmZeroSummary';table.parentElement?.insertBefore(sm,table);
   ['zmMonth','zmDistrict','zmJanpad','zmEngineer','zmCluster','zmGP'].forEach(id=>$(id)?.addEventListener('change',()=>{cascade(id);draw()}));$('zmReset')?.addEventListener('click',()=>{renderZero()});cascade();draw();
 }
 function bind(){const b=$('srdmZeroMandaysBtn');if(!b)return;b.onclick=function(ev){ev.preventDefault();ev.stopPropagation();setTimeout(renderZero,10)}}
 bind();document.addEventListener('DOMContentLoaded',bind);setTimeout(bind,1000);setTimeout(bind,3000);
})();
</script>
<!-- SRDM_ZERO_MANDAYS_FINAL_V4_END -->
'''
# Insert before </body>
pos = s.lower().rfind('</body>')
if pos < 0:
    print('ERROR: </body> not found')
    sys.exit(4)
s = s[:pos] + script + '\n' + s[pos:]

# Force a unique deployment marker so Git must see a change
stamp = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
s = re.sub(r'<!-- SRDM_ZERO_V4_DEPLOY:[^>]*-->', '', s)
s = s.replace('</body>', f'<!-- SRDM_ZERO_V4_DEPLOY:{stamp} -->\n</body>')

idx.write_text(s, encoding='utf-8')

checks = {
 'button': s.count('id="srdmZeroMandaysBtn"')==1,
 'v4_script': 'SRDM_ZERO_MANDAYS_FINAL_V4_START' in s,
 'live_data': 'window.SRDM_V8_MONTHLY' in s,
 'deploy_marker': f'SRDM_ZERO_V4_DEPLOY:{stamp}' in s,
}
print('PATCH CHECKS:', checks)
if not all(checks.values()): sys.exit(5)
print('PATCHED:', idx)
print('DEPLOY MARKER:', stamp)
