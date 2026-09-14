from pathlib import Path

p=Path('index.html')
if not p.exists():
    raise SystemExit('ERROR: index.html not found')
s=p.read_text(encoding='utf-8')
start='<!-- SRDM_CATEGORY_NUMERIC_BIG_COMPACT_V1 -->'
end='<!-- /SRDM_CATEGORY_NUMERIC_BIG_COMPACT_V1 -->'
block='''<!-- SRDM_CATEGORY_NUMERIC_BIG_COMPACT_V1 -->
<style id="SRDM_CATEGORY_NUMERIC_BIG_COMPACT_V1">
/* Category report: larger numeric values, compact Overall Exp % column. Data logic unchanged. */
body[data-report-view="category"] .report-table td:not(:first-child){
  font-size:17px!important;
  font-weight:800!important;
  line-height:1.12!important;
}
body[data-report-view="category"] .report-table td:first-child{
  font-size:15px!important;
  font-weight:800!important;
}
body[data-report-view="category"] .report-table td:nth-child(9),
body[data-report-view="category"] .report-table td:nth-child(10),
body[data-report-view="category"] .report-table td:nth-child(12),
body[data-report-view="category"] .report-table td:nth-child(14){
  font-size:16px!important;
}
/* Overall Exp % is column 15 after financial split */
body[data-report-view="category"] .report-table th:nth-child(15),
body[data-report-view="category"] .report-table td:nth-child(15){
  width:64px!important;
  min-width:64px!important;
  max-width:64px!important;
  padding-left:2px!important;
  padding-right:2px!important;
}
body[data-report-view="category"] .report-table th:nth-child(15){
  font-size:11px!important;
  line-height:1.05!important;
}
body[data-report-view="category"] .report-table td:nth-child(15) .exp-pct-chip{
  font-size:15px!important;
  font-weight:900!important;
  padding:2px 5px!important;
  min-width:0!important;
}
/* Other percentage numeric values also larger */
body[data-report-view="category"] .report-table td:nth-child(11),
body[data-report-view="category"] .report-table td:nth-child(13){
  font-size:16px!important;
  font-weight:850!important;
}
/* Recovery/Vasuli numeric column stays strong */
body[data-report-view="category"] .report-table td:last-child{
  font-size:19px!important;
  font-weight:950!important;
}
@media(max-width:1500px){
  body[data-report-view="category"] .report-table td:not(:first-child){font-size:16px!important;}
  body[data-report-view="category"] .report-table td:nth-child(15) .exp-pct-chip{font-size:14px!important;}
}
</style>
<!-- /SRDM_CATEGORY_NUMERIC_BIG_COMPACT_V1 -->'''
if start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+block+s[b:]
else:
    pos=s.lower().rfind('</head>')
    if pos<0: raise SystemExit('ERROR: </head> not found; file not changed')
    s=s[:pos]+block+'\n'+s[pos:]
p.write_text(s,encoding='utf-8')
print('DONE: Overall Exp % compact and numeric values enlarged')
print('Overall Exp % width: 64px')
print('Numeric body font: 17px (16px on smaller screens)')
print('Data/counts/financial logic: UNCHANGED')
