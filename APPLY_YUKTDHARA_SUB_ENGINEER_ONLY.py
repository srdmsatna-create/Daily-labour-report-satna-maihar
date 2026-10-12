#!/usr/bin/env python3
import re
import shutil
import sys
from pathlib import Path

root = Path(sys.argv[sys.argv.index('--repo') + 1]).resolve() if '--repo' in sys.argv else Path.cwd()
index = root / 'index.html'
if not index.exists():
    raise RuntimeError('index.html not found')

text = index.read_text(encoding='utf-8')
main_start = '<!-- SRDM_YUKTDHARA_SECTION_START -->'
main_end = '<!-- SRDM_YUKTDHARA_SECTION_END -->'
if main_start not in text or main_end not in text:
    raise RuntimeError('Existing Yuktdhara report marker not found. Dashboard was not changed.')

addon_start = '<!-- SRDM_YUKTDHARA_SUBENGINEER_START -->'
addon_end = '<!-- SRDM_YUKTDHARA_SUBENGINEER_END -->'
text = re.sub(re.escape(addon_start) + r'.*?' + re.escape(addon_end), '', text, flags=re.S)
addon = (
    addon_start
    + '<div id="yuktdharaSubEngineerApp"></div>'
    + '<script src="yuktdhara-gp-data.js?v=02092026"></script>'
    + '<script src="yuktdhara-subengineer.js?v=02092026"></script>'
    + addon_end
)
position = text.index(main_end)
text = text[:position] + addon + text[position:]
index.write_text(text, encoding='utf-8')

here = Path(__file__).resolve().parent
for name in ('yuktdhara-gp-data.js', 'yuktdhara-subengineer.js'):
    source, target = here / name, root / name
    if source.resolve() != target.resolve():
        shutil.copy2(source, target)

print('SUCCESS: Existing dashboard preserved; Yuktdhara Sub Engineer section added only.')
