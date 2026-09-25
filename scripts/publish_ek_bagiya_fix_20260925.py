from pathlib import Path
import json, re, zipfile, xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]

# ---- MGNREGA authoritative current-FY mandays: incoming/Daily Report.xlsx -> Nrega!G/V ----
def clean(v): return str(v or '').strip()
def num(v):
    try: return float(v or 0)
    except: return 0.0

def load_nrega_current_fy(xlsx):
    NS='http://schemas.openxmlformats.org/spreadsheetml/2006/main'
    RNS='http://schemas.openxmlformats.org/officeDocument/2006/relationships'
    with zipfile.ZipFile(xlsx) as z:
        sst=[]
        if 'xl/sharedStrings.xml' in z.namelist():
            rt=ET.fromstring(z.read('xl/sharedStrings.xml'))
            for si in rt.findall(f'{{{NS}}}si'):
                sst.append(''.join(t.text or '' for t in si.iter(f'{{{NS}}}t')))
        wb=ET.fromstring(z.read('xl/workbook.xml'))
        rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        ridmap={r.attrib['Id']:r.attrib['Target'] for r in rels}
        target=None
        for sh in wb.find(f'{{{NS}}}sheets'):
            if sh.attrib.get('name')=='Nrega':
                target=ridmap.get(sh.attrib.get(f'{{{RNS}}}id')); break
        if not target: raise RuntimeError('Nrega sheet not found')
        path='xl/'+target.lstrip('/') if not target.startswith('xl/') else target
        root=ET.fromstring(z.read(path)); data=root.find(f'{{{NS}}}sheetData')
        def cv(c):
            v=c.find(f'{{{NS}}}v'); raw=(v.text or '') if v is not None else ''
            return sst[int(raw)] if c.attrib.get('t')=='s' and raw else raw
        out={}
        for row in list(data)[4:]:
            cells={re.match(r'([A-Z]+)',c.attrib['r']).group(1):cv(c) for c in row.findall(f'{{{NS}}}c')}
            code=clean(cells.get('G',''))
            if code: out[code]=num(cells.get('V',''))
        return out

nmap=load_nrega_current_fy(ROOT/'incoming'/'Daily Report.xlsx')

# ---- ongoing-details.js ----
op=ROOT/'ongoing-details.js'
s=op.read_text(encoding='utf-8-sig').strip()
prefix='window.ONGOING_DETAILS='
if not s.startswith(prefix): raise RuntimeError('Unexpected ongoing-details.js format')
arr=json.loads(s[len(prefix):].rstrip(';'))
matched=0; ek_count=0; ek_sum=0; ek_pos=0
for r in arr:
    code=clean(r.get('code'))
    if code in nmap:
        r['nregaAprJunMandays']=nmap[code]; matched+=1
    if clean(r.get('finalCategory')) in ('Ek Bagiya','Ek Bagiya Maa Ke Naam'):
        v=num(nmap.get(code,0)); r['nregaAprJunMandays']=v
        ek_count+=1; ek_sum+=v; ek_pos += 1 if v>0 else 0
if ek_count != 755: raise RuntimeError(f'Ek Bagiya count expected 755, got {ek_count}')
if int(ek_sum) != 1916: raise RuntimeError(f'Ek Bagiya Apr-Jun mandays expected 1916, got {ek_sum}')
op.write_text(prefix+json.dumps(arr,ensure_ascii=False,separators=(',',':'))+';\n',encoding='utf-8')

# ---- main dashboard Ek Bagiya table ----
ip=ROOT/'index.html'; idx=ip.read_text(encoding='utf-8-sig')
start=idx.find('function ekBagiyaFiltered(){')
end=idx.find('\nfunction renderEkBagiyaDashboard(){',start)
if start<0 or end<0: raise RuntimeError('ekBagiyaFiltered block not found')
newfun=r'''function ekBagiyaFiltered(){
  const d=$('districtFilter').value,j=$('janpadFilter').value,e=$('engineerFilter').value,c=$('clusterFilter').value;
  const old=typeof WORK_DETAILS!=='undefined'&&Array.isArray(WORK_DETAILS)?WORK_DETAILS:[];
  const oldByCode=new Map(old.map(r=>[clean(r['Work Code']),r]));
  const live=(Array.isArray(ongoingDetails)?ongoingDetails:[]).filter(r=>{const cat=resolvedFinalCategory(r);return cat==='Ek Bagiya'||cat==='Ek Bagiya Maa Ke Naam';});
  const source=live.map((r,i)=>{
    const code=clean(r.code),o=oldByCode.get(code)||{};
    const san=num(r.sanction)||num(o['Sanction Amount Total']);
    const nw=num(r.nregaBookedWage),nm=num(r.nregaBookedMaterial),vw=num(r.vbgBookedWage),vm=num(r.vbgBookedMaterial);
    const nb=Number.isFinite(+r.nregaBooked)?num(r.nregaBooked):(nw+nm), vb=Number.isFinite(+r.vbgBooked)?num(r.vbgBooked):(vw+vm);
    const ow=Number.isFinite(+r.overallBookedWage)?num(r.overallBookedWage):(nw+vw), om=Number.isFinite(+r.overallBookedMaterial)?num(r.overallBookedMaterial):(nm+vm), ob=Number.isFinite(+r.overallBooked)?num(r.overallBooked):(nb+vb);
    const pre=num(r.mandaysTillMar31)||num(o['Mandays 2025-2026']), apr=num(r.nregaAprJunMandays), jul=num(r.julyMandays), total=pre+apr+jul;
    const ws=num(o['Wage Sanctioned']), ms=num(o['Material Sanctioned'])||Math.max(0,san-ws), ep=san?ob*100/san:0;
    return {...o,index:i,'S.No':i+1,Zila:r.district||o.Zila||'',Janpad:r.janpad||o.Janpad||'',Upyantri:r.engineer||o.Upyantri||'',Cluster:r.cluster||o.Cluster||'',
      'Panchayat Name':r.panchayat||o['Panchayat Name']||'','Work Code':code,'Work Name':r.name||o['Work Name']||'','Work Status':r.status||o['Work Status']||'Ongoing','Fin Year':r.fy||o['Fin Year']||'',
      'Sanction Amount Total':san,'Wage Sanctioned':ws,'Material Sanctioned':ms,
      'MGNREGA Booked Wages Till 30 June':nw,'MGNREGA Booked Material Till 30 June':nm,'MGNREGA Total Booked Till 30 June':nb,
      'VBGRAMG Booked Wages':vw,'VBGRAMG Booked Material':vm,'VBGRAMG Total Booked':vb,
      'Overall Booked Wages':ow,'Overall Booked Material':om,'Overall Total Booked':ob,
      'Amount Booked Since Inception Wages':ow,'Amount Booked Since Inception Material':om,'Overall Expenditure %':ep,
      'Remaining Wages':Math.max(0,ws-ow),'Remaining Material':Math.max(0,ms-om),
      'Mandays 2025-2026':pre,'NREGA Till 30 June Mandays':apr,'Mandays 01 Apr-30 Jun 2026':apr,'Mandays 2026-2027':jul,'Mandays Generated Current FY':apr+jul,'Total Mandays':total,
      'Mapping Status':'LIVE: MGNREGA Nrega sheet Current FY + VB-G RAM G July-Till Date'};
  });
  return source.filter(r=>(d==='ALL'||clean(r.Zila)===d)&&(j==='ALL'||clean(r.Janpad)===j)&&(e==='ALL'||clean(r.Upyantri)===e)&&(c==='ALL'||clean(r.Cluster)===c));
}'''
idx=idx[:start]+newfun+idx[end:]
idx=idx.replace("x.nregaAprJunMandays+=num(r['Mandays 2025-2026']);x.julyMandays+=num(r['Mandays 2026-2027']);x.totalMandays+=num(r['Total Mandays']);\n    if(num(r['Mandays 2026-2027'])>0)x.activeWorks++;else x.nilMandays++;",
                "x.nregaAprJunMandays+=num(r['NREGA Till 30 June Mandays']);x.julyMandays+=num(r['Mandays 2026-2027']);x.totalMandays+=num(r['Total Mandays']);\n    if(num(r['NREGA Till 30 June Mandays'])>0||num(r['Mandays 2026-2027'])>0)x.activeWorks++;if(num(r['Mandays 2026-2027'])===0)x.nilMandays++;")
ip.write_text(idx,encoding='utf-8')

# ---- fallback ek-bagiya/data.js ----
dp=ROOT/'ek-bagiya'/'data.js'; dtxt=dp.read_text(encoding='utf-8')
m1=re.search(r'^const UPYANTRI_ROWS=(\[.*?\]);\s*const WORK_DETAILS=',dtxt,re.S)
m2=re.search(r'const WORK_DETAILS=(\[.*\]);\s*$',dtxt,re.S)
if m1 and m2:
    up=json.loads(m1.group(1)); works=json.loads(m2.group(1))
    for w in works:
        code=clean(w.get('Work Code')); apr=num(nmap.get(code,0)); pre=num(w.get('Mandays 2025-2026')); jul=num(w.get('Mandays 2026-2027'))
        w['NREGA Till 30 June Mandays']=apr; w['Mandays 01 Apr-30 Jun 2026']=apr; w['Previous Mandays']=pre
        w['Mandays Generated Current FY']=apr+jul; w['Total Mandays']=pre+apr+jul
    groups={}
    for w in works:
        key=(w.get('Zila',''),w.get('Janpad',''),w.get('Upyantri',''),w.get('Cluster',''))
        g=groups.setdefault(key,{'apr':0,'jul':0,'pre':0,'total':0,'active':0})
        apr=num(w.get('NREGA Till 30 June Mandays')); jul=num(w.get('Mandays 2026-2027')); pre=num(w.get('Mandays 2025-2026'))
        g['apr']+=apr; g['jul']+=jul; g['pre']+=pre; g['total']+=pre+apr+jul; g['active'] += 1 if apr+jul>0 else 0
    for u in up:
        g=groups.get((u.get('Zila',''),u.get('Janpad',''),u.get('Upyantri',''),u.get('Cluster','')))
        if g:
            u['NREGA Till 30 June Mandays']=g['apr']; u['VBGRAMG Current FY Mandays']=g['jul']; u['Total Mandays Generated']=g['total']; u['Total Mandays']=g['total']
            u['more than zero mandays work of current year']=g['active']; u['0 zero mandays work of current year']=max(0,int(num(u.get('Sanction Works')))-g['active'])
    dp.write_text('const UPYANTRI_ROWS='+json.dumps(up,ensure_ascii=False,separators=(',',':'))+';\\nconst WORK_DETAILS='+json.dumps(works,ensure_ascii=False,separators=(',',':'))+';\\n',encoding='utf-8')

# ---- separate Ek Bagiya dashboard: make expenditure + mandays use main live data ----
ep=ROOT/'ek-bagiya'/'dashboard.html'
es=ep.read_text(encoding='utf-8')
es=es.replace('डेटा स्थिति<strong>09 सितंबर 2026</strong>756 सत्यापित कार्य · Official MIS 6.12','डेटा स्थिति<strong>मुख्य डैशबोर्ड से Live Sync</strong>755 सत्यापित कार्य · MGNREGA + VB-G RAM G')
es=es.replace('आज की प्रगति 09.09','नवीनतम प्रगति')
es=es.replace("<td>\${fmt(w['Mandays 2025-2026'])}</td><td>\${fmt(w['Mandays 2026-2027'])}</td><td>\${fmt(w['Total Mandays'])}</td>","<td>\${fmt(w['NREGA Till 30 June Mandays'])}</td><td>\${fmt(w['Mandays 2026-2027'])}</td><td>\${fmt(w['Total Mandays'])}</td>")
marker='SRDM_LIVE_EK_SYNC_20260925'
if marker not in es:
    override=r'''<script src="../ongoing-details.js?live=20260925c"></script><script>
/* SRDM_LIVE_EK_SYNC_20260925 */
(()=>{
 const live=Array.isArray(window.ONGOING_DETAILS)?window.ONGOING_DETAILS:[];
 if(!live.length||typeof WORK_DETAILS==='undefined'||typeof UPYANTRI_ROWS==='undefined')return;
 const old=new Map(WORK_DETAILS.map(w=>[String(w['Work Code']||'').trim(),w]));
 const rows=live.filter(r=>['Ek Bagiya','Ek Bagiya Maa Ke Naam'].includes(String(r.finalCategory||'').trim())).map((r,i)=>{
   const code=String(r.code||'').trim(),o=old.get(code)||{},san=+r.sanction||+o['Sanction Amount Total']||0;
   const nw=+r.nregaBookedWage||0,nm=+r.nregaBookedMaterial||0,vw=+r.vbgBookedWage||0,vm=+r.vbgBookedMaterial||0;
   const nb=Number.isFinite(+r.nregaBooked)?+r.nregaBooked:nw+nm,vb=Number.isFinite(+r.vbgBooked)?+r.vbgBooked:vw+vm;
   const ow=Number.isFinite(+r.overallBookedWage)?+r.overallBookedWage:nw+vw,om=Number.isFinite(+r.overallBookedMaterial)?+r.overallBookedMaterial:nm+vm,ob=Number.isFinite(+r.overallBooked)?+r.overallBooked:nb+vb;
   const pre=Number.isFinite(+r.mandaysTillMar31)?+r.mandaysTillMar31:(+o['Mandays 2025-2026']||0),apr=+r.nregaAprJunMandays||0,jul=+r.julyMandays||0;
   const ws=+o['Wage Sanctioned']||0,ms=+o['Material Sanctioned']||Math.max(0,san-ws),ep=san?ob*100/san:0;
   return {...o,index:i,'S.No':i+1,Zila:r.district||o.Zila||'',Janpad:r.janpad||o.Janpad||'',Upyantri:r.engineer||o.Upyantri||'',Cluster:r.cluster||o.Cluster||'','Panchayat Name':r.panchayat||o['Panchayat Name']||'','Work Code':code,'Work Name':r.name||o['Work Name']||'','Work Status':r.status||o['Work Status']||'Ongoing','Sanction Amount Total':san,'Wage Sanctioned':ws,'Material Sanctioned':ms,'MGNREGA Booked Wages Till 30 June':nw,'MGNREGA Booked Material Till 30 June':nm,'MGNREGA Total Booked Till 30 June':nb,'VBGRAMG Booked Wages':vw,'VBGRAMG Booked Material':vm,'VBGRAMG Total Booked':vb,'Overall Booked Wages':ow,'Overall Booked Material':om,'Overall Total Booked':ob,'Amount Booked Since Inception Wages':ow,'Amount Booked Since Inception Material':om,'Overall Expenditure %':ep,'Remaining Wages':Math.max(0,ws-ow),'Remaining Material':Math.max(0,ms-om),'Mandays 2025-2026':pre,'NREGA Till 30 June Mandays':apr,'Mandays 01 Apr-30 Jun 2026':apr,'Mandays 2026-2027':jul,'Mandays Generated Current FY':apr+jul,'Total Mandays':pre+apr+jul};
 });
 WORK_DETAILS.splice(0,WORK_DETAILS.length,...rows);
 const groups=new Map();
 for(const w of rows){const k=[w.Zila,w.Janpad,w.Upyantri,w.Cluster].join('¦');let g=groups.get(k);if(!g){g={n:0,san:0,nw:0,nm:0,vw:0,vm:0,ow:0,om:0,pre:0,apr:0,jul:0,active:0};groups.set(k,g)}g.n++;g.san+=+w['Sanction Amount Total']||0;g.nw+=+w['MGNREGA Booked Wages Till 30 June']||0;g.nm+=+w['MGNREGA Booked Material Till 30 June']||0;g.vw+=+w['VBGRAMG Booked Wages']||0;g.vm+=+w['VBGRAMG Booked Material']||0;g.ow+=+w['Overall Booked Wages']||0;g.om+=+w['Overall Booked Material']||0;g.pre+=+w['Mandays 2025-2026']||0;g.apr+=+w['NREGA Till 30 June Mandays']||0;g.jul+=+w['Mandays 2026-2027']||0;if((+w['Mandays Generated Current FY']||0)>0)g.active++}
 for(const u of UPYANTRI_ROWS){const g=groups.get([u.Zila,u.Janpad,u.Upyantri,u.Cluster].join('¦'));if(!g)continue;u['Sanction Works']=g.n;u['Sanctioned cost(lakhs)']=g.san/100000;u['MGNREGA Booked Wages Till 30 June (lakh)']=g.nw/100000;u['MGNREGA Booked Material Till 30 June (lakh)']=g.nm/100000;u['MGNREGA Total Booked Till 30 June (lakh)']=(g.nw+g.nm)/100000;u['VBGRAMG Booked Wages (lakh)']=g.vw/100000;u['VBGRAMG Booked Material (lakh)']=g.vm/100000;u['VBGRAMG Total Booked (lakh)']=(g.vw+g.vm)/100000;u['Overall Booked Wages (lakh)']=g.ow/100000;u['Overall Booked Material (lakh)']=g.om/100000;u['Overall Total Booked (lakh)']=(g.ow+g.om)/100000;u['Overall Exp %']=g.san?(g.ow+g.om)*100/g.san:0;u['Mandays 2025-2026']=g.pre;u['NREGA Till 30 June Mandays']=g.apr;u['Mandays 2026-2027']=g.jul;u['VBGRAMG Current FY Mandays']=g.jul;u['Total Mandays']=g.pre+g.apr+g.jul;u['Total Mandays Generated']=g.pre+g.apr+g.jul;u['more than zero mandays work of current year']=g.active;u['0 zero mandays work of current year']=g.n-g.active}
 if(typeof refreshFilters==='function')refreshFilters();if(typeof renderAll==='function')renderAll();
})();
</script>'''
    es=es.replace('</body>',override+'\n</body>')
ep.write_text(es,encoding='utf-8')

print(f'PUBLISH OK | Nrega codes={len(nmap)} | matched={matched} | Ek Bagiya={ek_count} | Apr-Jun={int(ek_sum)} | positive={ek_pos}')
