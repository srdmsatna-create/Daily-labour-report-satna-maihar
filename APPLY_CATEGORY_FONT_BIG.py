from pathlib import Path

p = Path('index.html')
if not p.exists():
    raise SystemExit('ERROR: index.html not found')

s = p.read_text(encoding='utf-8')
start = '<!-- SRDM_CATEGORY_FIN_FONT_BIG_V1 -->'
end = '<!-- /SRDM_CATEGORY_FIN_FONT_BIG_V1 -->'
block = '''<!-- SRDM_CATEGORY_FIN_FONT_BIG_V1 -->
<style id="SRDM_CATEGORY_FIN_FONT_BIG_V1">
/* Larger readable text for category / expenditure financial reports. Data and widths unchanged. */
body[data-report-view="category"] .report-table th,
body[data-report-view="category"] .report-table td,
body[data-report-view="expbucket"] .report-table th,
body[data-report-view="expbucket"] .report-table td,
body[data-report-view="ongoingall"] .report-table th,
body[data-report-view="ongoingall"] .report-table td{
  font-size:14px!important;
  line-height:1.18!important;
  padding:6px 5px!important;
}
body[data-report-view="category"] .report-table th,
body[data-report-view="expbucket"] .report-table th,
body[data-report-view="ongoingall"] .report-table th{
  font-size:13px!important;
  font-weight:900!important;
}
body[data-report-view="category"] .report-table td:first-child,
body[data-report-view="expbucket"] .report-table td:first-child,
body[data-report-view="ongoingall"] .report-table td:first-child{
  font-weight:800!important;
}
body[data-report-view="category"] .exp-pct-chip,
body[data-report-view="expbucket"] .exp-pct-chip{
  font-size:12px!important;
  padding:3px 7px!important;
}
@media(max-width:1500px){
  body[data-report-view="category"] .report-table th,
  body[data-report-view="category"] .report-table td,
  body[data-report-view="expbucket"] .report-table th,
  body[data-report-view="expbucket"] .report-table td,
  body[data-report-view="ongoingall"] .report-table th,
  body[data-report-view="ongoingall"] .report-table td{
    font-size:13px!important;
  }
  body[data-report-view="category"] .report-table th,
  body[data-report-view="expbucket"] .report-table th,
  body[data-report-view="ongoingall"] .report-table th{
    font-size:12px!important;
  }
}
</style>
<!-- /SRDM_CATEGORY_FIN_FONT_BIG_V1 -->'''

if start in s and end in s:
    a = s.index(start)
    b = s.index(end, a) + len(end)
    s = s[:a] + block + s[b:]
else:
    pos = s.lower().rfind('</head>')
    if pos < 0:
        raise SystemExit('ERROR: </head> not found; file not changed')
    s = s[:pos] + block + '\n' + s[pos:]

p.write_text(s, encoding='utf-8')
print('DONE: Category financial report font enlarged safely')
print('Body font: 14px (13px on smaller laptop screens)')
print('Header font: 13px (12px on smaller laptop screens)')
print('Data/counts/financial logic: UNCHANGED')
