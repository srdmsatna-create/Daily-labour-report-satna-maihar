from pathlib import Path
import re

index_path = Path('index.html')
thumb_source = Path('scripts/patch_portal_card_thumbnails.py').read_text(encoding='utf-8')
m = re.search(r"SIPRI_IMG='([^']+)'", thumb_source, flags=re.S)
if not m:
    raise SystemExit('SIPRI_IMG data URI not found')
sipri_img = m.group(1)

s = index_path.read_text(encoding='utf-8')
orig = s

planner_svg = '''<span class="srdm-app-icon srdm-thumb-icon" aria-label="Planner Portal">
<svg viewBox="0 0 136 100" role="img" aria-label="Planner Portal"><defs><linearGradient id="plannerG" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#0877ef"/><stop offset="1" stop-color="#20a7df"/></linearGradient></defs><rect width="136" height="100" rx="14" fill="url(#plannerG)"/><rect x="27" y="24" width="82" height="52" rx="8" fill="#fff" opacity=".96"/><rect x="38" y="55" width="10" height="12" fill="#19a76f"/><rect x="55" y="45" width="10" height="22" fill="#f0b429"/><rect x="72" y="35" width="10" height="32" fill="#ed5252"/><rect x="89" y="28" width="10" height="39" fill="#0d5bd7"/><text x="68" y="88" text-anchor="middle" font-family="Arial,sans-serif" font-size="12" font-weight="900" fill="#fff">PLANNER</text></svg>
</span>'''

sipri_thumb = f'''<span class="srdm-app-icon srdm-thumb-icon" aria-label="SIPRI Portal screenshot"><img src="{sipri_img}" alt="SIPRI Portal" style="width:100%;height:100%;object-fit:cover;border-radius:12px;display:block"></span>'''

road_svg = '''<span class="srdm-app-icon srdm-thumb-icon" aria-label="RIMS gravel road thumbnail">
<svg viewBox="0 0 136 100" role="img" aria-label="Gravel Road"><defs><linearGradient id="sky2" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#7cc8f5"/><stop offset="1" stop-color="#e7f5ff"/></linearGradient><linearGradient id="road2" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#a88d6b"/><stop offset="1" stop-color="#66513f"/></linearGradient></defs><rect width="136" height="100" rx="14" fill="url(#sky2)"/><path d="M0 55 Q28 42 52 55 T103 52 T136 48V100H0Z" fill="#56a35f"/><path d="M49 100 L65 52 L78 52 L105 100Z" fill="url(#road2)"/><path d="M67 100 L70 55" stroke="#e6d7ba" stroke-width="3" stroke-dasharray="7 7"/><g fill="#d4c2a7"><circle cx="58" cy="82" r="2.5"/><circle cx="82" cy="88" r="2.1"/><circle cx="71" cy="72" r="1.8"/><circle cx="91" cy="95" r="2.6"/></g><text x="9" y="18" font-family="Arial,sans-serif" font-size="11" font-weight="900" fill="#2c2c2c">RIMS</text></svg>
</span>'''

cards = f'''<a class="srdm-app-card srdm-portal-card srdm-portal-planner" href="planner-portal-dashboard.html" style="text-decoration:none">
      {planner_svg}<span class="srdm-app-copy"><strong>Planner Portal</strong><span>Janpad-wise • Panchayat-wise • New Work संख्या</span></span><span class="srdm-app-new">New</span>
    </a>
    <a class="srdm-app-card srdm-portal-card srdm-portal-jgsa" href="https://jgsa.nregsmp.org/" target="_blank" rel="noopener noreferrer" style="text-decoration:none">
      <span class="srdm-app-icon">💧</span><span class="srdm-app-copy"><strong>Dashboard - Jal Ganga Sanvardhan Abhiyan 2026</strong><span>Official JGSA portal</span></span><span class="srdm-app-new">New</span>
    </a>
    <a class="srdm-app-card srdm-portal-card srdm-portal-rims" href="https://geoportal.mp.gov.in/" target="_blank" rel="noopener noreferrer" style="text-decoration:none">
      {road_svg}<span class="srdm-app-copy"><strong>Road Information &amp; Management System (RIMS)</strong><span>Official RIMS geoportal</span></span>
    </a>
    <a class="srdm-app-card srdm-portal-card srdm-portal-planner-sipri" href="planner-sipri-dashboard-hi.html" style="text-decoration:none">
      {sipri_thumb}<span class="srdm-app-copy"><strong>प्लानर से SIPRI Portal पर कार्य योजना डैशबोर्ड</strong><span>उपयंत्री / क्लस्टर नामवार प्रगति</span></span><span class="srdm-app-new">New</span>
    </a>
    '''

pattern = re.compile(r'(<div class="srdm-app-grid">\s*)(?:<a class="srdm-app-card srdm-portal-card.*?</a>\s*)+(?=<button type="button" class="srdm-app-card")', re.S)
match = pattern.search(s)
if not match:
    raise SystemExit('Portal card block not found in index.html')
s = s[:match.start()] + match.group(1) + cards + s[match.end():]

if 'SRDM_FIXED_PORTAL_CARDS_V2' not in s:
    css = '''\n/* SRDM_FIXED_PORTAL_CARDS_V2 */\n.srdm-portal-card .srdm-app-icon.srdm-thumb-icon{width:70px!important;height:70px!important;min-width:70px!important;padding:0!important;overflow:hidden!important;background:#fff!important;border-radius:15px!important;display:inline-flex!important;align-items:center!important;justify-content:center!important}.srdm-portal-card .srdm-app-icon.srdm-thumb-icon svg,.srdm-portal-card .srdm-app-icon.srdm-thumb-icon img{width:100%!important;height:100%!important;display:block!important;object-fit:cover!important}.srdm-portal-jgsa .srdm-app-icon{font-size:34px!important;background:#04a6b7!important;color:#fff!important}\n'''
    s = s.replace('</style>', css + '\n</style>', 1)

index_path.write_text(s, encoding='utf-8')
print('Launcher cards rewritten:', s != orig)
for needle in ['Planner Portal</strong>', 'Dashboard - Jal Ganga Sanvardhan Abhiyan 2026</strong>', 'Road Information &amp; Management System (RIMS)</strong>', 'प्लानर से SIPRI Portal पर कार्य योजना डैशबोर्ड</strong>']:
    print(needle, s.count(needle))
