from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')
orig=s

SIPRI_IMG='data:image/jpeg;base64,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'

thumb=f'<span class="srdm-app-icon srdm-thumb-icon" aria-label="SIPRI portal screenshot"><img src="{SIPRI_IMG}" alt="SIPRI Portal" style="width:100%;height:100%;object-fit:cover;border-radius:12px;display:block"></span>'

# Shared icon sizing.
if 'SRDM_SIPRI_SCREENSHOT_ICON_V1' not in s:
    css='''\n/* SRDM_SIPRI_SCREENSHOT_ICON_V1 */\n.srdm-app-icon.srdm-thumb-icon{width:68px!important;height:58px!important;min-width:68px!important;padding:0!important;overflow:hidden!important;background:#fff!important;border-radius:12px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important}\n'''
    s=s.replace('</style>',css+'\n</style>',1)

# 1) Planner -> SIPRI dashboard card: replace its first icon, regardless of current emoji/generic chart.
patterns=[
    r'(<a[^>]*href=["\'][^"\']*planner-sipri-dashboard-hi\.html[^"\']*["\'][^>]*>)(.*?)(</a>)',
    r'(<a[^>]*>)(?P<body>.*?प्लानर\s*से\s*SIPRI\s*Portal.*?कार्य\s*योजना\s*डैशबोर्ड.*?)(</a>)'
]
for pat in patterns:
    m=re.search(pat,s,flags=re.S|re.I)
    if m:
        whole=m.group(0)
        patched=re.sub(r'<span class="srdm-app-icon[^"]*"[^>]*>.*?</span>',thumb,whole,count=1,flags=re.S|re.I)
        if patched==whole:
            patched=whole.replace('>', '>'+thumb, 1)
        s=s[:m.start()]+patched+s[m.end():]
        break

# 2) Keep Jal Ganga separate and always show water-drop icon.
jgsa_card='''<a class="srdm-app-card srdm-portal-card srdm-portal-jgsa" href="https://jgsa.nregsmp.org/" target="_blank" rel="noopener noreferrer" style="text-decoration:none">\n      <span class="srdm-app-icon">💧</span><span class="srdm-app-copy"><strong>Dashboard - Jal Ganga Sanvardhan Abhiyan 2026</strong><span>Official JGSA portal</span></span><span class="srdm-app-new">New</span>\n    </a>'''
if 'Dashboard - Jal Ganga Sanvardhan Abhiyan 2026</strong>' in s:
    s=re.sub(r'<a class="srdm-app-card srdm-portal-card srdm-portal-jgsa"[^>]*>.*?</a>',jgsa_card,s,count=1,flags=re.S)
else:
    # Insert after Planner-to-SIPRI dashboard card when available, otherwise after Planner Portal card.
    target=re.search(r'<a[^>]*href=["\'][^"\']*planner-sipri-dashboard-hi\.html[^"\']*["\'][^>]*>.*?</a>',s,flags=re.S|re.I)
    if not target:
        target=re.search(r'<a[^>]*>.*?Planner Portal.*?</a>',s,flags=re.S|re.I)
    if target:
        s=s[:target.end()]+'\n    '+jgsa_card+s[target.end():]

# 3) Keep RIMS card road-themed (do not alter title/link).
# If an existing RIMS card has a generic icon, leave existing road thumbnail untouched; only mark for CSS compatibility.

if s!=orig:
    p.write_text(s,encoding='utf-8')
    print('SIPRI screenshot icon + Jal Ganga water-drop card patched.')
else:
    print('No changes required.')
