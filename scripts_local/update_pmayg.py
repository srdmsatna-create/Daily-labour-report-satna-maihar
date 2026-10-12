"""Official MIS 6.12 PMAY-G/IAY, all years, Approved and Ongoing."""
import json, csv, re, sys, os
from datetime import datetime
from zoneinfo import ZoneInfo
from update_mis_612_work_details import ROOT, URL, session_opener, open_text, hidden_fields, selected_values, form_action, ResultRows, urllib

NREGA_URL = 'https://mnregaweb4.dord.gov.in/netnregarep/dynamic_work_details.aspx?payload=1A6ER1_wmGucIcI52WXSl9SkSWhbH7D3haJAJXUMlyb14ejtY0bcdGB_dPLenxioqvwn54kAvAJcdWMn8bG6bEOKIFFaagksd7d05w89LAE5g8XeBjPemgG8WXtByI9jz0JwvqaF69nYig9mt_HPIJtQGJDa0qodof_n3qpTR4uWxP2M3JrjrIfdHr2407Wf'
VBG_URL = 'https://vbgramgrep.dord.gov.in/VBGRAMG/dynamic_work_details.aspx?payload=ftnyL9stdXeAc7zMQW8cHY09zYjD7YVdkcCL1EOM3Wm_8lISfAJzdF6JhnQsT5n17zpy7r_Vba0PwONGLjnUmidzdUwQaYSFBWiqr8uMNsbD7W7oGi8r9C5028sI0yPRNL4IbdUTLIJyaorEpuLA8Q4t0xSSpie_wrjIAKCgcGA7aPT1CYMPdmkLhKSFE6NZ'

def norm(s):return re.sub(r'[^A-Z0-9]','',str(s).upper())
def fetch_source(source_url):
 opener=session_opener();src,url=open_text(opener,source_url)
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
 return rows

def combine_sources(nrega_rows,vbg_rows):
 def index(rows):
  out={}
  for r in rows:
   code=r['Work Code']
   if code in out and out[code]!=r:raise ValueError('Conflicting source work code: '+code)
   out[code]=r
  return out
 nrega=index(nrega_rows);vbg=index(vbg_rows);compiled=[]
 def md(row,key):
  if row is None:return 0
  value=row.get(key,'').replace(',','').strip()
  if not value:raise ValueError('Missing '+key+' for '+row['Work Code'])
  number=float(value)
  if number<0:raise ValueError('Negative mandays')
  return number
 for code in sorted(set(nrega)|set(vbg)):
  a=nrega.get(code);b=vbg.get(code)
  # NREGA total includes prior years; VBGRAMG Current FY is the separate new period.
  n=md(a,'Total Mandays');v=md(b,'Mandays Generated Current FY')
  r=dict(b or a);r['Total Mandays']=str(n+v)
  r['_nregaMandays']=n;r['_vbgMandays']=v
  r['_sourceCoverage']='Both' if a and b else 'MGNREGA only' if a else 'VBGRAMG only'
  compiled.append(r)
 return compiled

def main():
 nrega_url=os.environ.get('MGNREGA_PMAY_R612_URL','').strip() or NREGA_URL
 vbg_url=os.environ.get('VBGRAMG_PMAY_R612_URL','').strip() or VBG_URL
 if urllib.parse.urlparse(nrega_url).hostname==urllib.parse.urlparse(vbg_url).hostname:raise ValueError('Distinct official MGNREGA and VBGRAMG sources required')
 print('Fetching MGNREGA FY 2026-27 (all work-start years)',flush=True)
 nrega_rows=fetch_source(nrega_url)
 print('Fetching VBGRAMG FY 2026-27 (all work-start years)',flush=True)
 vbg_rows=fetch_source(vbg_url)
 if not nrega_rows or not vbg_rows:raise ValueError('Both source reports must return work rows before compilation')
 rows=combine_sources(nrega_rows,vbg_rows)
 master=list(csv.DictReader((ROOT/'gp-sector-engineer-master-25-09-2026.csv').open(encoding='utf-8-sig')))
 mapping={}
 for m in master:
  for k in ['Gram_Panchayat','GP_20Sep_Name']:mapping[(norm(m['Janpad']),norm(m[k]))]=m
 unique={};unmapped=[]
 for r in rows:
  m=mapping.get((norm(r['Janpad / Block Name']),norm(r['Panchayat Name'])))
  if not m:unmapped.append(r['Janpad / Block Name']+'/'+r['Panchayat Name'])
  def number(k):return float(r[k].replace(',','') or 0)
  item={'district':m['District'] if m else '', 'janpad':r['Janpad / Block Name'],'cluster':m['Sector'] if m else 'Mapping pending','gp':r['Panchayat Name'],'engineer':m['Sub_Engineer'] if m else '', 'fy':r['Work Start Fin Year'],'status':r['Work Status'],'code':r['Work Code'],'name':r['Work Name'],'type':r['Work Type'],'sanction':number('Total Sanction (Rs)'),'booked':number('Booked Since Inception Wages (Rs)')+number('Booked Since Inception Material (Rs)'),'mandays':number('Total Mandays'),'nregaMandays':r['_nregaMandays'],'vbgMandays':r['_vbgMandays'],'sourceCoverage':r['_sourceCoverage'],'targetMandays':90,'balanceMandays':max(90-number('Total Mandays'),0)}
  if item['code'] in unique and unique[item['code']]!=item:raise ValueError('Conflicting work code')
  unique[item['code']]=item
 if not unique:raise ValueError('Empty PMAY report')
 if unmapped:raise ValueError('Unmapped GP: '+str(sorted(set(unmapped))))
 years=[f'{y}-{y+1}' for y in range(2005,2027)]
 output={'source':'MGNREGA + VBGRAMG Report 6.12','officialUrl':vbg_url,'fetchedAt':datetime.now(ZoneInfo('Asia/Kolkata')).isoformat(),'allYears':True,'years':sorted(set(years),reverse=True),'rows':list(unique.values()),'includesIAY':True,'nregaUrl':nrega_url,'nregaRows':len(nrega_rows),'vbgRows':len(vbg_rows),'mandaysMode':'MGNREGA inception total + VBGRAMG current FY separate period'}
 p=ROOT/'data/pmayg-latest.json';tmp=p.with_suffix('.tmp');tmp.write_text(json.dumps(output,ensure_ascii=False),encoding='utf-8');os.replace(tmp,p)
 print('SUCCESS PMAY-G: '+str(len(unique))+' verified works',flush=True)
if __name__=='__main__':
 try:main()
 except Exception as e:print('FAILED PMAY-G; previous snapshot retained: '+str(e),flush=True);sys.exit(1)
