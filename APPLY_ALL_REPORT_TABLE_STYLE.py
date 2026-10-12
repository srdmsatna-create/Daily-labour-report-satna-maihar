from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

css_start = '/* ===== SRDM ALL REPORT TABLE STYLE V1 ===== */'
css_end = '/* ===== END SRDM ALL REPORT TABLE STYLE V1 ===== */'
js_start = '<!-- ===== SRDM DISTRICT AVERAGE HIGHLIGHT V1 ===== -->'
js_end = '<!-- ===== END SRDM DISTRICT AVERAGE HIGHLIGHT V1 ===== -->'

if css_start in s and css_end in s:
    a = s.index(css_start); b = s.index(css_end, a) + len(css_end); s = s[:a] + s[b:]
if js_start in s and js_end in s:
    a = s.index(js_start); b = s.index(js_end, a) + len(js_end); s = s[:a] + s[b:]

css = r'''
/* ===== SRDM ALL REPORT TABLE STYLE V1 ===== */
.report-table,.alert-table,.dys-alert-table,.district-dys-table{border-collapse:collapse!important;border-spacing:0!important}
.report-table{min-width:940px!important;width:100%!important;table-layout:auto!important}
.report-table th,.report-table td,.alert-table th,.alert-table td,.dys-alert-table th,.dys-alert-table td,.district-dys-table th,.district-dys-table td{border:1.35px solid #4f7f76!important;font-size:13px!important;line-height:1.18!important;padding:6px 6px!important;vertical-align:middle!important;overflow-wrap:anywhere!important;word-break:normal!important}
.report-table th,.alert-table th,.dys-alert-table th,.district-dys-table th{font-size:13px!important;font-weight:900!important;text-align:center!important}
.report-table td,.report-table th{white-space:normal!important}
.report-table td:nth-child(1),.report-table th:nth-child(1){min-width:68px!important;width:auto!important}
.report-table td:nth-child(2),.report-table th:nth-child(2){min-width:105px!important;width:auto!important}
.report-table td:nth-child(3),.report-table th:nth-child(3){min-width:82px!important;width:auto!important}
.table-wrap{border:2px solid #356a60!important;border-radius:7px!important}
.report-table tbody tr.srdm-below-district-average>td,.alert-table tbody tr.srdm-below-district-average>td,.dys-alert-table tbody tr.srdm-below-district-average>td,.district-dys-table tbody tr.srdm-below-district-average>td{background:#fff0c9!important;color:#7a3e00!important;font-weight:800!important;border-top-color:#e3a72f!important;border-bottom-color:#e3a72f!important}
.report-table tbody tr.srdm-below-district-average>td.srdm-progress-cell,.alert-table tbody tr.srdm-below-district-average>td.srdm-progress-cell,.dys-alert-table tbody tr.srdm-below-district-average>td.srdm-progress-cell,.district-dys-table tbody tr.srdm-below-district-average>td.srdm-progress-cell{background:#f6c453!important;color:#5b2c00!important;font-weight:950!important;box-shadow:inset 0 0 0 2px #d89213!important}
@media(max-width:900px){.report-table th,.report-table td,.alert-table th,.alert-table td,.dys-alert-table th,.dys-alert-table td,.district-dys-table th,.district-dys-table td{font-size:12px!important;padding:5px!important}}
/* ===== END SRDM ALL REPORT TABLE STYLE V1 ===== */
'''

if '</style>' not in s: raise SystemExit('index.html has no </style>')
s = s.replace('</style>', css + '\n</style>', 1)

js = r'''
<!-- ===== SRDM DISTRICT AVERAGE HIGHLIGHT V1 ===== -->
<script>
(function(){
  const MAIHAR=new Set(['AMARPATAN','MAIHAR','RAMNAGAR']),SATNA=new Set(['MAJHGAWAN','NAGOD','RAMPUR BAGHELAN','SOHAWAL','SATNA','UNCHAHARA']);
  const norm=v=>String(v==null?'':v).trim().toUpperCase().replace(/\s+/g,' ');
  const districtFrom=v=>{const x=norm(v);if(MAIHAR.has(x)||x.includes('MAIHAR'))return'MAIHAR';if(SATNA.has(x)||x.includes('SATNA'))return'SATNA';return''};
  const parsePct=v=>{const m=String(v==null?'':v).replace(/,/g,'').match(/-?\d+(?:\.\d+)?/);return m?Number(m[0]):NaN};
  const headers=t=>Array.from(t.querySelectorAll('thead tr:last-child th')).map(x=>norm(x.textContent));
  const idx=(hs,tests)=>hs.findIndex(h=>tests.some(t=>t.test(h)));
  function known(){try{if(typeof rows==='undefined'||typeof engineerData!=='function')return null;const a={SATNA:{p:0,t:0},MAIHAR:{p:0,t:0}};for(const r of engineerData(rows)){const d=districtFrom(r.janpad);if(!a[d])continue;a[d].p+=Number(r.gpsProgress)||0;a[d].t+=Number(r.gps)||0}const o={};for(const d of Object.keys(a))if(a[d].t>0)o[d]=a[d].p*100/a[d].t;return o}catch(e){return null}}
  function styleTable(t){if(!t.tBodies||!t.tBodies.length)return;const hs=headers(t);if(!hs.length)return;const pi=idx(hs,[/^%\s*PROGRESS$/,/PROGRESS\s*%/,/%\s*PROGRESS/,/GP.*PROGRESS.*%/,/प्रगति.*%/]);if(pi<0)return;const ei=idx(hs,[/ENGINEER/,/UPYANTRI/,/SUB\s*ENG/,/उपयंत्री/,/उपयंत्र/]);if(ei<0)return;const ji=idx(hs,[/JANPAD/,/BLOCK/,/जनपद/]),di=idx(hs,[/DISTRICT/,/जिला/]),k=known(),vis={SATNA:[],MAIHAR:[],ALL:[]},rr=[];for(const tr of Array.from(t.tBodies[0].rows)){tr.classList.remove('srdm-below-district-average');Array.from(tr.cells).forEach(td=>td.classList.remove('srdm-progress-cell'));if(tr.classList.contains('total-row')||tr.classList.contains('janpad-total-row')||tr.classList.contains('all-total-row')||tr.cells.length<=pi)continue;const eng=tr.cells[ei]?norm(tr.cells[ei].textContent):'';if(!eng||eng==='-'||eng==='TOTAL'||eng.includes('योग'))continue;const v=parsePct(tr.cells[pi].textContent);if(!Number.isFinite(v))continue;let d='';if(di>=0&&tr.cells[di])d=districtFrom(tr.cells[di].textContent);if(!d&&ji>=0&&tr.cells[ji])d=districtFrom(tr.cells[ji].textContent);rr.push({tr,v,d});(vis[d]||vis.ALL).push(v)}const all=rr.length?rr.reduce((a,x)=>a+x.v,0)/rr.length:NaN;for(const x of rr){let av=k&&x.d&&Number.isFinite(k[x.d])?k[x.d]:NaN;if(!Number.isFinite(av)){const a=vis[x.d]||[];av=a.length?a.reduce((q,v)=>q+v,0)/a.length:all}if(Number.isFinite(av)&&x.v<av){x.tr.classList.add('srdm-below-district-average');x.tr.cells[pi]&&x.tr.cells[pi].classList.add('srdm-progress-cell');x.tr.title=`Below ${x.d||'District'} Average: ${x.v.toFixed(1)}% < ${av.toFixed(1)}%`}else if(x.tr.title&&x.tr.title.startsWith('Below '))x.tr.removeAttribute('title')}}
  function apply(){document.querySelectorAll('table').forEach(styleTable)}let q=false;const schedule=()=>{if(q)return;q=true;requestAnimationFrame(()=>{q=false;apply()})};const start=()=>{apply();new MutationObserver(schedule).observe(document.body,{childList:true,subtree:true,characterData:true});document.addEventListener('change',()=>setTimeout(apply,0),true);document.addEventListener('click',()=>setTimeout(apply,40),true)};document.readyState==='loading'?document.addEventListener('DOMContentLoaded',start):start();
})();
</script>
<!-- ===== END SRDM DISTRICT AVERAGE HIGHLIGHT V1 ===== -->
'''

if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',js+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: all report tables updated')
