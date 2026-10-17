"""Import the two official Planning Summary exports into both planner dashboards.

Usage: python scripts_local/import_planning_summary.py FILE... --date YYYY-MM-DD
Read-only XLSX parser; writes dashboard data without altering source workbooks.
"""
import argparse,base64,csv,gzip,hashlib,json,re,zipfile
from collections import defaultdict
from datetime import date
from pathlib import Path
import xml.etree.ElementTree as ET
ROOT=Path(__file__).resolve().parents[1]
NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
BLOCKS=['Amarpatan','Maihar','Majhgawan','Nagod','Ramnagar','Rampur baghelan','Sohawal','Unchahara']
def key(value):return re.sub('[^A-Z0-9]','',str(value).upper())
def district(block):return 'Maihar' if block in ('Amarpatan','Maihar','Ramnagar') else 'Satna'
def xlsx_rows(path):
 with zipfile.ZipFile(path) as archive:
  strings=[''.join(t.text or '' for t in e.findall('.//x:t',NS)) for e in ET.fromstring(archive.read('xl/sharedStrings.xml')).findall('x:si',NS)] if 'xl/sharedStrings.xml' in archive.namelist() else []
  result=[]
  for row in ET.fromstring(archive.read('xl/worksheets/sheet1.xml')).findall('.//x:sheetData/x:row',NS):
   values={}
   for cell in row.findall('x:c',NS):
    v=cell.find('x:v',NS);value=v.text if v is not None else ''.join(t.text or '' for t in cell.findall('.//x:t',NS))
    if cell.get('t')=='s':value=strings[int(value)]
    values[re.sub(r'\d+','',cell.get('r'))]=value or ''
   result.append(values)
  if not result or result[0].get('G')!='Works Planned(Planner)' or result[0].get('H')!='Works Planned (SIPRI)':raise ValueError('Unexpected Planning Summary headers: '+str(path))
  return result[1:]
def integer(value):
 if value in ('',None):return 0
 n=float(value)
 if n<0 or not n.is_integer():raise ValueError('Invalid planning count: '+str(value))
 return int(n)
def dump(value):return json.dumps(value,ensure_ascii=False,separators=(',',':'))
def build(paths,source_date,root=ROOT):
 root=Path(root);master=list(csv.DictReader((root/'gp-sector-engineer-master-25-09-2026.csv').open(encoding='utf-8-sig',newline='')))
 mapping={}
 for m in master:
  for gp in (m['Gram_Panchayat'],m['GP_20Sep_Name']):
   k=(key(m['Janpad']),key(gp))
   if k in mapping and (mapping[k]['Sub_Engineer'],mapping[k]['Sector'])!=(m['Sub_Engineer'],m['Sector']):raise ValueError('Ambiguous GP mapping: '+str(k))
   mapping[k]=m
 canonical={key(b):b for b in BLOCKS};canonical['SATNA']='Sohawal'
 engineers=defaultdict(lambda:[0,0]);categories=defaultdict(lambda:[0,0]);blocks={b:[0,0,0,0] for b in BLOCKS};seen=set();metadata=[];source_rows=0;district_corrections=0;source_exceptions=[]
 for path in paths:
  rows=xlsx_rows(path);metadata.append({'file':path.name,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),'rows':len(rows)})
  for r in rows:
   source_rows+=1;b=canonical[key(r['B'])]
   if r['A'].strip().lower()!=district(b).lower():district_corrections+=1 # canonical Satna/Maihar split is Janpad-based
   identity=(b,key(r['C']),r['D'],r['E'])
   if identity in seen:raise ValueError('Duplicate Planning Summary record: '+str(identity))
   seen.add(identity)
   m=mapping.get((key(b),key(r['C'])))
   if not m:raise ValueError('GP mapping missing: '+b+'/'+r['C'])
   counts=[integer(r.get(c)) for c in ('G','H','N','S')]
   if counts[1]>counts[0]:source_exceptions.append({'block':b,'panchayat':r['C'],'structure':r['F'],'planner':counts[0],'sipri':counts[1]})
   for i,n in enumerate(counts):blocks[b][i]+=n
   er=engineers[(district(b),b,m['Sub_Engineer'])]
   cr=categories[(district(b),b,r['F'],m['Sub_Engineer'],m['Sector'])]
   for i in (0,1):er[i]+=counts[i];cr[i]+=counts[i]
 if any(not any(key(b)==key(k[1]) for k in engineers) for b in BLOCKS):raise ValueError('Eight Janpads required')
 erows=[list(k)+v for k,v in sorted(engineers.items())]
 approvals=[[district(b),b,'Assistant Engineer - '+b,p,s,a,max(0,s-a),rev,max(0,a-rev)] for b,(p,s,a,rev) in blocks.items()]
 totals={'plannerDetail':sum(x[0] for x in blocks.values()),'sipri':sum(x[1] for x in blocks.values()),'aeApproved':sum(x[2] for x in blocks.values()),'aePending':sum(r[6] for r in approvals),'stateReviewed':sum(x[3] for x in blocks.values()),'statePending':sum(r[8] for r in approvals)}
 # Source SA review totals are independent cumulative counters; do not clamp
 # reviewed to AE approvals when the exported source reports more reviews.
 dictionaries=[sorted({k[i] for k in categories}) for i in range(5)];indices=[{v:j for j,v in enumerate(values)} for values in dictionaries]
 packed=dict(zip(('d','b','c','e','l'),dictionaries));packed['r']=[[indices[i][k[i]] for i in range(5)]+v for k,v in sorted(categories.items())]
 portal=json.loads((root/'planner-portal-data.js').read_text().split('=',1)[1].strip().rstrip(';'))
 official={canonical[key(b['janpad'])]:b['newWorks'] for b in portal['blocks']}
 packed.update(uploadedDate=source_date.strftime('%d-%m-%Y'),tn=totals['plannerDetail'],ts=totals['sipri'],sr=source_rows,officialTotal=sum(official.values()),officialBlocks=[official[b] for b in packed['b']],detailTotal=totals['plannerDetail'],detailGap=sum(official.values())-totals['plannerDetail'])
 if sum(r[3] for r in erows)!=packed['tn'] or sum(r[4] for r in erows)!=packed['ts'] or sum(r[5] for r in packed['r'])!=packed['tn'] or sum(r[6] for r in packed['r'])!=packed['ts']:raise ValueError('Cross-dashboard reconciliation failed')
 provenance={'uploadedDate':source_date.strftime('%d-%m-%Y'),'files':[p.name for p in paths],'sourceRows':source_rows,'mappingSource':'gp-sector-engineer-master-25-09-2026.csv','sourceFiles':metadata,'mappedRows':source_rows,'unmappedRows':0,'districtLabelsNormalized':district_corrections,'sipriAbovePlannerRows':len(source_exceptions)}
 outputs={
 'planner-engineer-summary-data.js':'/* Planning Summary import; Janpad + GP mapping. */\nwindow.PLANNER_ENGINEER_SUMMARY='+dump(erows)+';\nwindow.PLANNER_OFFICIAL='+dump({'total':sum(official.values()),'blocks':official})+';\nwindow.PLANNER_IMPORT_DATE='+dump(source_date.strftime('%d-%m-%Y'))+';\n',
 'planner-new-work-data.js':'window.PNWD='+dump(packed)+';\n',
 'planner-new-work-data-gzip.js':"window.PNWD_GZIP='"+base64.b64encode(gzip.compress(dump(packed).encode(),mtime=0)).decode()+"';\n"
 }
 approval=root/'planner-approval-summary-data.js';old=approval.read_text();layout=old[old.index('// Layout readability'): ] if '// Layout readability' in old else ''
 outputs['planner-approval-summary-data.js']='window.PLANNER_APPROVAL_SUMMARY='+dump(approvals)+';\nwindow.PLANNER_APPROVAL_TOTALS='+dump(totals)+';\nwindow.PLANNER_SIPRI_SOURCE='+dump(provenance)+';\n'+layout
 outputs['data/planning-summary-import-status.json']=json.dumps({'date':source_date.isoformat(),'source':provenance,'totals':totals,'blocks':approvals,'categoryRows':len(packed['r']),'engineerRows':len(erows),'officialPlannerTotal':sum(official.values()),'detailGap':packed['detailGap'],'sourceExceptions':source_exceptions},ensure_ascii=False,indent=2)+'\n'
 return outputs,totals
if __name__=='__main__':
 parser=argparse.ArgumentParser();parser.add_argument('files',nargs='+',type=Path);parser.add_argument('--date',type=date.fromisoformat,required=True);args=parser.parse_args()
 outputs,totals=build(args.files,args.date)
 for path,content in outputs.items():(ROOT/path).write_text(content,encoding='utf-8')
 print(dump(totals))
