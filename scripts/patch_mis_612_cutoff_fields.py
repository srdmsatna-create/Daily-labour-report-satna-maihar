#!/usr/bin/env python3
"""Idempotently restore the missing 31-Mar mandays display in MIS 6.12 work detail.

No existing field/header is renamed or removed. Only the requested cutoff column is
inserted between Exp % and the already existing Apr-Jun column.
"""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APP = ROOT / 'app.js'
s = APP.read_text(encoding='utf-8')

label = '<th>Mandays<br>till 31 Mar 2026</th>'
if label in s:
    print('MIS 6.12 cutoff display already present')
    raise SystemExit(0)

old_header = '<th>Exp %</th><th>NREGA Mandays<br>01 Apr–30 Jun</th><th>Mandays<br>01 Jul–Today</th>'
new_header = '<th>Exp %</th><th>Mandays<br>till 31 Mar 2026</th><th>NREGA Mandays<br>01 Apr–30 Jun</th><th>Mandays<br>01 Jul–Today</th>'
if old_header not in s:
    raise SystemExit('MIS 6.12 categoryworks header signature not found; refusing unsafe UI patch')
s = s.replace(old_header, new_header, 1)

old_row = "</td>${cell(r.nregaAprJunMandays,true)}${cell(r.julyMandays,true)}</tr>`});if(!data.length)h+=`<tr><td colspan=\"18\" class=\"empty-table\">Current filter/category/status में work नहीं मिला।</td></tr>"
new_row = "</td>${cell(r.mandaysTillMar31 ?? Math.max(0,num(r.mandays)-num(r.currentFYMandays)),true)}${cell(r.nregaAprJunMandays,true)}${cell(r.julyMandays,true)}</tr>`});if(!data.length)h+=`<tr><td colspan=\"19\" class=\"empty-table\">Current filter/category/status में work नहीं मिला।</td></tr>"
if old_row not in s:
    raise SystemExit('MIS 6.12 categoryworks row signature not found; refusing partial UI patch')
s = s.replace(old_row, new_row, 1)

APP.write_text(s, encoding='utf-8')
print('MIS 6.12: added requested Mandays till 31 Mar 2026 display; existing fields unchanged')
