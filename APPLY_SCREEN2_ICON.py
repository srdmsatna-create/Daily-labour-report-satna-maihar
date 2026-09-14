from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

# Replace the icon only on the Official Janpad / Screen-2 launcher card.
pat = re.compile(r'(<button[^>]*data-srdm-view=["\']official["\'][^>]*>\s*)<span class=["\']srdm-app-icon["\']>.*?</span>', re.I | re.S)
repl = r'''\1<span class="srdm-app-icon srdm-screen2-photo-icon"><img src="screen2-workers-icon.svg" alt="Screen-2 workers icon"></span>'''
s, n = pat.subn(repl, s, count=1)

# Add/refresh dedicated icon styling.
start = '<!-- ===== SCREEN2 PHOTO ICON V1 ===== -->'
end = '<!-- ===== END SCREEN2 PHOTO ICON V1 ===== -->'
if start in s and end in s:
    a = s.index(start)
    b = s.index(end, a) + len(end)
    s = s[:a] + s[b:]

style = r'''
<!-- ===== SCREEN2 PHOTO ICON V1 ===== -->
<style>
.srdm-app-icon.srdm-screen2-photo-icon{
  padding:0!important;
  overflow:hidden!important;
  background:#fff!important;
  border:1px solid #d9e5f4!important;
  box-shadow:0 8px 20px rgba(25,74,123,.12)!important;
}
.srdm-app-icon.srdm-screen2-photo-icon img{
  width:100%!important;
  height:100%!important;
  display:block!important;
  object-fit:cover!important;
  object-position:center!important;
  border-radius:inherit!important;
}
</style>
<!-- ===== END SCREEN2 PHOTO ICON V1 ===== -->
'''

if '</head>' in s:
    s = s.replace('</head>', style + '\n</head>', 1)
else:
    s += style

p.write_text(s, encoding='utf-8')
print(f'DONE: Screen-2 photo icon applied; card replacements={n}')
