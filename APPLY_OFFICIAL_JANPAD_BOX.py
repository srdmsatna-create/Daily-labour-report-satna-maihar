from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Remove the previous broken compact-view patch if present.
old_start = '<!-- ===== OFFICIAL JANPAD BOX V1 ===== -->'
old_end = '<!-- ===== END OFFICIAL JANPAD BOX V1 ===== -->'
if old_start in s and old_end in s:
    a = s.index(old_start)
    b = s.index(old_end, a) + len(old_end)
    s = s[:a] + s[b:]

# Remove an older copy of this safe patch when re-running.
start = '<!-- ===== OFFICIAL JANPAD BOX V2 SAFE ===== -->'
end = '<!-- ===== END OFFICIAL JANPAD BOX V2 SAFE ===== -->'
if start in s and end in s:
    a = s.index(start)
    b = s.index(end, a) + len(end)
    s = s[:a] + s[b:]

block = r'''
<!-- ===== OFFICIAL JANPAD BOX V2 SAFE ===== -->
<style>
/* Official Janpad Daily Report: DO NOT remove/reorder any column. */
body[data-report-view="official"] #reportTable{
  border-collapse:collapse!important;
  border-spacing:0!important;
  width:100%!important;
  min-width:1450px!important;
  table-layout:auto!important;
  border:2px solid #356a60!important;
}
body[data-report-view="official"] #reportTable th,
body[data-report-view="official"] #reportTable td{
  border:1.4px solid #6f91a7!important;
  font-size:13.5px!important;
  line-height:1.18!important;
  padding:7px 6px!important;
  vertical-align:middle!important;
  white-space:normal!important;
  overflow-wrap:anywhere!important;
}
body[data-report-view="official"] #reportTable thead th{
  font-size:13.5px!important;
  font-weight:900!important;
  text-align:center!important;
}
body[data-report-view="official"] #reportTable tbody td{
  font-weight:700!important;
}
body[data-report-view="official"] #reportTable tbody td:first-child,
body[data-report-view="official"] #reportTable tbody td:nth-child(2){
  text-align:left!important;
}
body[data-report-view="official"] .table-wrap{
  border:2px solid #356a60!important;
  border-radius:8px!important;
  overflow:auto!important;
  background:#fff!important;
}
/* Visually keep PMAY-G and Ek Bagiya as clear boxed groups without changing data/columns. */
body[data-report-view="official"] #reportTable thead tr:first-child th:nth-last-child(2),
body[data-report-view="official"] #reportTable thead tr:first-child th:last-child{
  box-shadow:inset 0 0 0 1px #356a60!important;
}
@media(max-width:900px){
  body[data-report-view="official"] #reportTable th,
  body[data-report-view="official"] #reportTable td{font-size:12px!important;padding:6px 5px!important}
}
</style>
<script>
(function(){
  // Safety cleanup only. The old patch marked the table after deleting columns.
  // This script NEVER deletes/reorders cells; normal app rendering restores the full original layout.
  function cleanOfficialMarker(){
    if(document.body.dataset.reportView!=='official') return;
    const t=document.getElementById('reportTable');
    if(t) t.removeAttribute('data-official-compact');
  }
  if(document.readyState==='loading'){
    document.addEventListener('DOMContentLoaded', cleanOfficialMarker);
  }else cleanOfficialMarker();
  document.addEventListener('click',()=>setTimeout(cleanOfficialMarker,20),true);
})();
</script>
<!-- ===== END OFFICIAL JANPAD BOX V2 SAFE ===== -->
'''

if '</body>' not in s:
    raise SystemExit('index.html has no </body>')
s = s.replace('</body>', block + '\n</body>', 1)
p.write_text(s, encoding='utf-8')
print('DONE: Official Janpad original columns preserved; full box and larger font applied')
