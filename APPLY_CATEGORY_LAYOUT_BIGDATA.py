from pathlib import Path

p = Path('index.html')
if not p.exists():
    raise SystemExit('ERROR: index.html not found')

s = p.read_text(encoding='utf-8')
# remove prior category font blocks if present
for a,b in [
    ('<!-- SRDM_CATEGORY_FIN_FONT_BIG_V1 -->','<!-- /SRDM_CATEGORY_FIN_FONT_BIG_V1 -->'),
    ('<!-- SRDM_CATEGORY_FIN_FONT_BIG_V2 -->','<!-- /SRDM_CATEGORY_FIN_FONT_BIG_V2 -->')
]:
    while a in s and b in s:
        i=s.index(a); j=s.index(b,i)+len(b); s=s[:i]+s[j:]

block = r'''<!-- SRDM_CATEGORY_LAYOUT_BIGDATA_V1 -->
<style id="SRDM_CATEGORY_LAYOUT_BIGDATA_V1">
/* Category financial report: wider category, compact numeric columns, larger body data. */
body[data-report-view="category"] .report-table{
  table-layout:fixed!important;
  width:100%!important;
}
body[data-report-view="category"] .report-table th{
  font-size:11.5px!important;
  font-weight:900!important;
  line-height:1.08!important;
  padding:5px 3px!important;
  white-space:normal!important;
  word-break:break-word!important;
  text-align:center!important;
}
body[data-report-view="category"] .report-table td{
  font-size:15px!important;
  font-weight:750!important;
  line-height:1.12!important;
  padding:6px 4px!important;
  text-align:right!important;
  vertical-align:middle!important;
}
body[data-report-view="category"] .report-table th:nth-child(1),
body[data-report-view="category"] .report-table td:nth-child(1){
  width:160px!important;min-width:160px!important;max-width:160px!important;
  text-align:left!important;
  white-space:normal!important;
  overflow-wrap:anywhere!important;
  font-size:15px!important;
  font-weight:850!important;
}
body[data-report-view="category"] .report-table th:nth-child(2),
body[data-report-view="category"] .report-table td:nth-child(2){width:78px!important;min-width:78px!important;max-width:78px!important}
body[data-report-view="category"] .report-table th:nth-child(n+3):nth-child(-n+8),
body[data-report-view="category"] .report-table td:nth-child(n+3):nth-child(-n+8){width:62px!important;min-width:62px!important;max-width:62px!important}
body[data-report-view="category"] .report-table th:nth-child(n+9):nth-child(-n+14),
body[data-report-view="category"] .report-table td:nth-child(n+9):nth-child(-n+14){width:82px!important;min-width:82px!important;max-width:82px!important}
body[data-report-view="category"] .report-table th:last-child,
body[data-report-view="category"] .report-table td:last-child{
  width:64px!important;min-width:64px!important;max-width:64px!important;
  text-align:center!important;font-size:18px!important;font-weight:900!important;
}
body[data-report-view="category"] .exp-pct-chip{font-size:13px!important;font-weight:900!important;padding:3px 6px!important}
body[data-report-view="category"] .bucket-zero,
body[data-report-view="category"] .bucket-good{font-size:15px!important;font-weight:900!important}
@media(max-width:1500px){
  body[data-report-view="category"] .report-table td{font-size:14px!important}
  body[data-report-view="category"] .report-table th{font-size:10.8px!important}
  body[data-report-view="category"] .report-table th:nth-child(1),
  body[data-report-view="category"] .report-table td:nth-child(1){width:150px!important;min-width:150px!important;max-width:150px!important;font-size:14px!important}
}
</style>
<!-- /SRDM_CATEGORY_LAYOUT_BIGDATA_V1 -->'''

pos=s.lower().rfind('</head>')
if pos<0:
    raise SystemExit('ERROR: </head> not found; file not changed')
s=s[:pos]+block+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
print('DONE: Category layout/readability patch applied')
print('Work Category width: 160px')
print('Numeric columns: compact')
print('Body numeric font: 15px')
print('Counts/categories/financial logic: UNCHANGED')
