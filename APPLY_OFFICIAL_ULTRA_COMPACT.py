from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')
start='<!-- ===== OFFICIAL ULTRA COMPACT WIDTH V1 ===== -->'
end='<!-- ===== END OFFICIAL ULTRA COMPACT WIDTH V1 ===== -->'
if start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+s[b:]

block=r'''
<!-- ===== OFFICIAL ULTRA COMPACT WIDTH V1 ===== -->
<style>
body[data-report-view="official"] #reportTable{
  min-width:1120px!important;
  table-layout:auto!important;
}
body[data-report-view="official"] #reportTable th,
body[data-report-view="official"] #reportTable td{
  padding:5px 3px!important;
}
body[data-report-view="official"] #reportTable .print-select-col{
  width:34px!important;min-width:34px!important;max-width:34px!important;
}
body[data-report-view="official"] #reportTable th:nth-child(2),
body[data-report-view="official"] #reportTable td:nth-child(2){
  width:58px!important;min-width:58px!important;max-width:58px!important;
}
body[data-report-view="official"] #reportTable th:nth-child(3),
body[data-report-view="official"] #reportTable td:nth-child(3){
  width:82px!important;min-width:82px!important;max-width:82px!important;
}
body[data-report-view="official"] #reportTable th:nth-child(4),
body[data-report-view="official"] #reportTable td:nth-child(4){
  width:76px!important;min-width:76px!important;max-width:76px!important;
}
body[data-report-view="official"] #reportTable th:nth-child(5),
body[data-report-view="official"] #reportTable td:nth-child(5){
  width:64px!important;min-width:64px!important;max-width:64px!important;
}
body[data-report-view="official"] #reportTable th:nth-child(6),
body[data-report-view="official"] #reportTable td:nth-child(6){
  width:46px!important;min-width:46px!important;max-width:46px!important;
}
body[data-report-view="official"] #reportTable th:nth-child(n+7),
body[data-report-view="official"] #reportTable td:nth-child(n+7){
  min-width:44px!important;
}
body[data-report-view="official"] #reportTable th:last-child,
body[data-report-view="official"] #reportTable td:last-child{
  width:52px!important;min-width:52px!important;max-width:52px!important;
}
</style>
<!-- ===== END OFFICIAL ULTRA COMPACT WIDTH V1 ===== -->
'''

if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: Official Janpad widths reduced to minimum practical size')
