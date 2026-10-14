"""Apply the verified GP master to each daily feed before validation/publication."""
import csv, io, json, re
from pathlib import Path

def key(v):
    return re.sub(r'[^A-Z0-9]', '', str(v or '').upper())

def apply(root, files):
    root = Path(root)
    with (root/'gp-sector-engineer-master-25-09-2026.csv').open(encoding='utf-8-sig', newline='') as f:
        master = list(csv.DictReader(f))
    sectors = {}; gps = {}
    for r in master:
        j = key(r['Janpad']); sectors[j,key(r['Sector'])] = r['Sub_Engineer']
        for gp in (r['Gram_Panchayat'],r['GP_20Sep_Name']):
            gps[j,key(gp)] = r['Sub_Engineer']
    def fix(o, parent=''):
        if isinstance(o,list):
            for v in o: fix(v,parent)
        elif isinstance(o,dict):
            j=key(o.get('janpad') or o.get('block') or o.get('Janpad') or o.get('Janpad / Block Name') or parent)
            gp=key(o.get('panchayat') or o.get('gp') or o.get('Gram_Panchayat') or o.get('Panchayat Name') or o.get('GP'))
            sector=key(o.get('cluster') or o.get('Cluster') or o.get('Sector') or o.get('sector'))
            name=gps.get((j,gp)) or sectors.get((j,sector))
            if name:
                for field in ('engineer','Engineer','Sub_Engineer','Sub Engineer','Engname','Upyantri','Engineer/Cluster'):
                    if isinstance(o.get(field),str): o[field]=name
            for v in o.values():
                if isinstance(v,(list,dict)): fix(v,j)
    for filename in files:
        p=root/filename
        if not p.exists(): continue
        if p.suffix in ('.json','.js'):
            original=p.read_text(encoding='utf-8-sig'); prefix=''; suffix='\n'
            text=original.strip()
            if p.suffix=='.js':
                if '=' not in text: continue
                prefix,text=text.split('=',1);prefix+=' = ';text=text.strip().rstrip(';');suffix=';\n'
            try: data=json.loads(text)
            except json.JSONDecodeError: continue
            fix(data)
            p.write_text(prefix+json.dumps(data,ensure_ascii=False)+suffix,encoding='utf-8')
        elif p.suffix=='.csv':
            with p.open(encoding='utf-8-sig',newline='') as f:
                reader=csv.DictReader(f);fields=reader.fieldnames;rows=list(reader)
            for r in rows: fix(r)
            with p.open('w',encoding='utf-8-sig',newline='') as f:
                writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(rows)
