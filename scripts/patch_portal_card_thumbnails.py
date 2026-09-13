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

sipri = '''<span class="srdm-app-icon srdm-thumb-icon" aria-label="SIPRI portal thumbnail">
<svg viewBox="0 0 136 100" role="img" aria-label="SIPRI Portal"><defs><linearGradient id="sg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#007c91"/><stop offset="1" stop-color="#20c5b5"/></linearGradient></defs><rect width="136" height="100" rx="14" fill="url(#sg)"/><path d="M10 72 C35 55 55 84 82 58 S118 50 130 34" fill="none" stroke="#bdf7ef" stroke-width="6" opacity=".9"/><circle cx="42" cy="42" r="13" fill="#fff" opacity=".96"/><path d="M42 24c-10 0-18 8-18 18 0 14 18 31 18 31s18-17 18-31c0-10-8-18-18-18zm0 24a7 7 0 1 1 0-14 7 7 0 0 1 0 14z" fill="#087c91"/><text x="73" y="41" font-family="Arial,sans-serif" font-size="19" font-weight="800" fill="#fff">SIPRI</text><text x="73" y="60" font-family="Arial,sans-serif" font-size="9" font-weight="700" fill="#eafffb">MP PORTAL</text></svg>
</span>'''

rims = '''<span class="srdm-app-icon srdm-thumb-icon" aria-label="RIMS gravel road thumbnail">
<svg viewBox="0 0 136 100" role="img" aria-label="Gravel Road"><defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#7cc8f5"/><stop offset="1" stop-color="#e7f5ff"/></linearGradient><linearGradient id="road" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#a88d6b"/><stop offset="1" stop-color="#66513f"/></linearGradient></defs><rect width="136" height="100" rx="14" fill="url(#sky)"/><path d="M0 55 Q28 42 52 55 T103 52 T136 48V100H0Z" fill="#56a35f"/><path d="M49 100 L65 52 L78 52 L105 100Z" fill="url(#road)"/><path d="M67 100 L70 55" stroke="#e6d7ba" stroke-width="3" stroke-dasharray="7 7" opacity=".9"/><g fill="#d4c2a7" opacity=".95"><circle cx="58" cy="82" r="2.5"/><circle cx="82" cy="88" r="2.1"/><circle cx="71" cy="72" r="1.8"/><circle cx="91" cy="95" r="2.6"/><circle cx="62" cy="93" r="1.9"/></g><text x="9" y="18" font-family="Arial,sans-serif" font-size="11" font-weight="900" fill="#2c2c2c">RIMS</text></svg>
</span>'''

# Replace the icon immediately associated with each visible card title.
s = re.sub(r'<span class="srdm-app-icon(?: [^"]*)?">.*?</span>(?=<span class="srdm-app-copy"><strong>SIPRI Portal</strong>)', sipri, s, flags=re.S)
s = re.sub(r'<span class="srdm-app-icon(?: [^"]*)?">.*?</span>(?=<span class="srdm-app-copy"><strong>Dashboard - Jal Ganga Sanvardhan Abhiyan 2026</strong>)', '<span class="srdm-app-icon">💧</span>', s, flags=re.S)
s = re.sub(r'<span class="srdm-app-icon(?: [^"]*)?">.*?</span>(?=<span class="srdm-app-copy"><strong>Road Information &amp; Management System \(RIMS\)</strong>)', rims, s, flags=re.S)

if s != orig:
    p.write_text(s, encoding='utf-8')
    print('Portal card thumbnails patched.')
else:
    print('No changes required.')
