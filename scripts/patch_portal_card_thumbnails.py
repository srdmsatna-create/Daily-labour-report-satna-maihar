from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')
orig = s

CSS_MARK = '/* SRDM_PORTAL_THUMBNAILS_V1 */'
css = r'''
/* SRDM_PORTAL_THUMBNAILS_V1 */
.srdm-portal-card .srdm-app-icon.srdm-thumb-icon{
  width:68px!important;height:50px!important;min-width:68px!important;
  padding:0!important;overflow:hidden!important;border-radius:12px!important;
  background:#fff!important;display:inline-flex!important;align-items:center!important;justify-content:center!important;
  box-shadow:0 7px 18px var(--app-shadow,rgba(0,0,0,.18))!important;
}
.srdm-portal-card .srdm-app-icon.srdm-thumb-icon svg{width:100%!important;height:100%!important;display:block!important}
.srdm-portal-jgsa .srdm-app-icon{font-size:30px!important}
'''
if CSS_MARK not in s:
    s = s.replace('</style>', css + '\n</style>', 1)

planner_thumb = '''<span class="srdm-app-icon srdm-thumb-icon" aria-label="Planner portal thumbnail">
<svg viewBox="0 0 136 100" role="img" aria-label="Planner Portal"><defs><linearGradient id="pg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#007c91"/><stop offset="1" stop-color="#20c5b5"/></linearGradient></defs><rect width="136" height="100" rx="14" fill="url(#pg)"/><circle cx="41" cy="40" r="17" fill="#fff" opacity=".18"/><circle cx="41" cy="36" r="7" fill="#fff"/><path d="M25 67c3-13 29-13 32 0" fill="#fff"/><path d="M69 62c10-8 18-18 27-18 10 0 17 8 29 2" fill="none" stroke="#eafffb" stroke-width="5" stroke-linecap="round"/><text x="67" y="31" font-family="Arial,sans-serif" font-size="14" font-weight="900" fill="#fff">PLAN</text><text x="67" y="47" font-family="Arial,sans-serif" font-size="14" font-weight="900" fill="#fff">NER</text></svg>
</span>'''

rims = '''<span class="srdm-app-icon srdm-thumb-icon" aria-label="RIMS gravel road thumbnail">
<svg viewBox="0 0 136 100" role="img" aria-label="Gravel Road"><defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#7cc8f5"/><stop offset="1" stop-color="#e7f5ff"/></linearGradient><linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#a88d6b"/><stop offset="1" stop-color="#66513f"/></linearGradient></defs><rect width="136" height="100" rx="14" fill="url(#sky)"/><path d="M0 55 Q28 42 52 55 T103 52 T136 48V100H0Z" fill="#56a35f"/><path d="M49 100 L65 52 L78 52 L105 100Z" fill="url(#road)"/><path d="M67 100 L70 55" stroke="#e6d7ba" stroke-width="3" stroke-dasharray="7 7" opacity=".9"/><g fill="#d4c2a7" opacity=".95"><circle cx="58" cy="82" r="2.5"/><circle cx="82" cy="88" r="2.1"/><circle cx="71" cy="72" r="1.8"/><circle cx="91" cy="95" r="2.6"/><circle cx="62" cy="93" r="1.9"/></g><text x="9" y="18" font-family="Arial,sans-serif" font-size="11" font-weight="900" fill="#2c2c2c">RIMS</text></svg>
</span>'''

planner_card = '<a class="srdm-app-card srdm-portal-card srdm-portal-sipri" href="planner-portal-dashboard.html" style="text-decoration:none">\n      '+planner_thumb+'<span class="srdm-app-copy"><strong>Planner Portal</strong><span>Janpad-wise • Panchayat-wise • New Work संख्या</span></span>\n    </a>'

jgsa_card = '''<a class="srdm-app-card srdm-portal-card srdm-portal-jgsa" href="https://jgsa.nregsmp.org/" target="_blank" rel="noopener noreferrer" style="text-decoration:none">
      <span class="srdm-app-icon">💧</span><span class="srdm-app-copy"><strong>Dashboard - Jal Ganga Sanvardhan Abhiyan 2026</strong><span>Official JGSA portal</span></span><span class="srdm-app-new">New</span>
    </a>'''

# Keep Planner Portal as its own dashboard card.
if 'Planner Portal</strong>' in s:
    s = re.sub(r'<a class="srdm-app-card srdm-portal-card srdm-portal-sipri"[^>]*>.*?</a>', planner_card, s, count=1, flags=re.S)
elif 'SIPRI Portal</strong>' in s:
    s = re.sub(r'<a class="srdm-app-card srdm-portal-card srdm-portal-sipri"[^>]*>.*?</a>', planner_card, s, count=1, flags=re.S)

# Jal Ganga must always remain a separate visible card with water-drop icon.
if 'Dashboard - Jal Ganga Sanvardhan Abhiyan 2026</strong>' in s:
    s = re.sub(r'<a class="srdm-app-card srdm-portal-card srdm-portal-jgsa"[^>]*>.*?</a>', jgsa_card, s, count=1, flags=re.S)
else:
    # insert immediately after Planner Portal card
    s = s.replace(planner_card, planner_card + '\n    ' + jgsa_card, 1)

# Keep RIMS thumbnail.
s = re.sub(r'<span class="srdm-app-icon(?: [^"]*)?">.*?</span>(?=<span class="srdm-app-copy"><strong>Road Information &amp; Management System \(RIMS\)</strong>)', rims, s, flags=re.S)

if s != orig:
    p.write_text(s, encoding='utf-8')
    print('Planner Portal + Jal Ganga + RIMS cards restored/patched.')
else:
    print('No changes required.')
