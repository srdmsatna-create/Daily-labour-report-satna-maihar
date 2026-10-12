"""Official MIS 6.12 PMAY-G/IAY, all years, Approved and Ongoing."""
import json, csv, re, sys, os
from datetime import datetime
from zoneinfo import ZoneInfo
from update_mis_612_work_details import ROOT, URL, session_opener, open_text, hidden_fields, selected_values, form_action, ResultRows, urllib

def norm(s):return re.sub(r'[^A-Z0-9]','',str(s).upper())
def main():
 opener=session_opener();src,url=open_text(opener,URL)
 d=hidden_fields(src);selected_values(src,d);d.update({'__EVENTTARGET':'ctl00$ContentPlaceHolder1$ddl_dist','ctl00$ContentPlaceHolder1$ddl_state':'17','ctl00$ContentPlaceHolder1$ddl_dist':'1712'})
 src,url=open_text(opener,form_action(src,url),urllib.parse.urlencode(d).encode())
 if 'value="1712006"' not in src:raise ValueError('District/block form did not load')
 base=hidden_fields(src);selected_values(src,base)
 prefix='ctl00$ContentPlaceHolder1$'
 base.update({'__EVENTTARGET':'',prefix+'ddl_blk':'ALL',prefix+'ddl_pan':'ALL',prefix+'Ddlworkcategory':'ALL',prefix+'ddlFin_year':'ALL',prefix+'filter':'ALL',prefix+'Button1':'Submit'})
 rows=[]
 for status,label in [('03','Ongoing'),('02','Approved')]:
  for kind in ['Constr of PMAY-G House for Individuals','IAY Houses']:
   payload=dict(base);payload.update({prefix+'Ddlwork_status':status,prefix+'ddlprostatus':kind})
   print('Fetching '+label+' / '+kind,flush=True)
   page,_=open_text(opener,form_action(src,url),urllib.parse.urlencode(payload).encode(),timeout=300)
   if 'Work Code' not in page and 'Work_Code' not in page and not re.search(r'No\s+(?:Record|Data)',page,re.I):raise ValueError('Unrecognized report response')
   parser=ResultRows(label);parser.feed(page);parser.close()
   for r in parser.rows:
    if r['Work Status'].lower()!=label.lower():raise ValueError('Status filter mismatch')
    if not re.search(r'PMAY|IAY',r['Work Type']+' '+r['Work Name'],re.I):raise ValueError('PMAY filter mismatch')
   print('Rows: '+str(len(parser.rows)),flush=True);rows.extend(parser.rows)
 master=list(csv.DictReader((ROOT/'gp-sector-engineer-master-25-09-2026.csv').open(encoding='utf-8-sig')))
 mapping={}
 for m in master:
  for k in ['Gram_Panchayat','GP_20Sep_Name']:mapping[(norm(m['Janpad']),norm(m[k]))]=m
 unique={};unmapped=[]
 for r in rows:
  m=mapping.get((norm(r['Janpad / Block Name']),norm(r['Panchayat Name'])))
  if not m:unmapped.append(r['Janpad / Block Name']+'/'+r['Panchayat Name'])
  def number(k):return float(r[k].replace(',','') or 0)
  item={'district':m['District'] if m else '', 'janpad':r['Janpad / Block Name'],'cluster':m['Sector'] if m else 'Mapping pending','gp':r['Panchayat Name'],'engineer':m['Sub_Engineer'] if m else '', 'fy':r['Work Start Fin Year'],'status':r['Work Status'],'code':r['Work Code'],'name':r['Work Name'],'type':r['Work Type'],'sanction':number('Total Sanction (Rs)'),'booked':number('Booked Since Inception Wages (Rs)')+number('Booked Since Inception Material (Rs)'),'mandays':number('Total Mandays')}
  if item['code'] in unique and unique[item['code']]!=item:raise ValueError('Conflicting work code')
  unique[item['code']]=item
 if not unique:raise ValueError('Empty PMAY report')
 if unmapped:raise ValueError('Unmapped GP: '+str(sorted(set(unmapped))))
 years=re.findall(r'value="(20\d\d-20\d\d)"',src)
 output={'source':'VBGRAMG MIS / KIS 6.012 (6.12)','officialUrl':URL,'fetchedAt':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'allYears':True,'years':sorted(set(years),reverse=True),'rows':list(unique.values()),'includesIAY':True}
 p=ROOT/'data/pmayg-latest.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(output,ensure_ascii=False),encoding='utf-8');os.replace(tmp,p)
 print('SUCCESS PMAY-G: '+str(len(unique))+' verified works',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('FAILED PMAY-G; previous snapshot retained: '+str(e),flush=True);sys.exit(1)
