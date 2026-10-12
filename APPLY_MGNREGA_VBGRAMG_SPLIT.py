from pathlib import Path
import json, sys, re, shutil, datetime

repo = Path(sys.argv[1] if len(sys.argv)>1 else r'C:\Users\welcome\Daily-labour-report-satna-maihar')
base_dir = Path(__file__).resolve().parent
base_file = base_dir / 'nrega-r612-baseline.json'
detail_file = repo / 'ongoing-details.js'
index_file = repo / 'index.html'

for p in (base_file, detail_file, index_file):
    if not p.exists():
        raise SystemExit(f'ERROR: file not found: {p}')

# ---------- load exact 29-Aug MGNREGA baseline by Work Code ----------
baseline = json.loads(base_file.read_text(encoding='utf-8'))

# ---------- load current verified R6.12 ongoing data ----------
raw = detail_file.read_text(encoding='utf-8-sig').strip()
prefix = 'window.ONGOING_DETAILS='
if not raw.startswith(prefix):
    raise SystemExit('ERROR: ongoing-details.js format not recognized')
body = raw[len(prefix):]
if body.endswith(';'): body = body[:-1]
rows = json.loads(body)

if len(rows) != 15687:
    raise SystemExit(f'ERROR: current ongoing count changed. Expected 15687, found {len(rows)}. Nothing changed.')

pmay = sum(1 for r in rows if str(r.get('finalCategory','')).strip() == 'PMAY-G')
iay = sum(1 for r in rows if str(r.get('finalCategory','')).strip() == 'IAY Houses')
ek = sum(1 for r in rows if str(r.get('finalCategory','')).strip() == 'Ek Bagiya')
if (pmay, iay, ek) != (10807, 0, 755):
    raise SystemExit(f'ERROR: verified category baseline changed. PMAY={pmay}, IAY={iay}, Ek Bagiya={ek}. Nothing changed.')

matched = 0
missing = []
sum_nrega = sum_vbg = sum_overall = 0.0
for r in rows:
    code = str(r.get('code','')).strip()
    vals = baseline.get(code)
    if vals is None:
        nw = nm = 0.0
        missing.append(code)
    else:
        matched += 1
        nw = float(vals[0] or 0)
        nm = float(vals[1] or 0)
    vw = float(r.get('bookedWage',0) or 0)
    vm = float(r.get('bookedMaterial',0) or 0)
    nb = nw + nm
    vb = vw + vm
    ow = nw + vw
    om = nm + vm
    ob = nb + vb
    san = float(r.get('sanction',0) or 0)
    r['nregaBookedWage'] = round(nw, 2)
    r['nregaBookedMaterial'] = round(nm, 2)
    r['nregaBooked'] = round(nb, 2)
    r['vbgBookedWage'] = round(vw, 2)
    r['vbgBookedMaterial'] = round(vm, 2)
    r['vbgBooked'] = round(vb, 2)
    r['overallBookedWage'] = round(ow, 2)
    r['overallBookedMaterial'] = round(om, 2)
    r['overallBooked'] = round(ob, 2)
    r['nregaExpPct'] = round((nb*100/san) if san else 0, 4)
    r['vbgExpPct'] = round((vb*100/san) if san else 0, 4)
    r['overallExpPct'] = round((ob*100/san) if san else 0, 4)
    sum_nrega += nb; sum_vbg += vb; sum_overall += ob

# ---------- backup ----------
stamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
backup_dir = repo.parent / 'SRDM_BACKUPS'
backup_dir.mkdir(exist_ok=True)
shutil.copy2(detail_file, backup_dir / f'ongoing-details.before-fin-split-{stamp}.js')
shutil.copy2(index_file, backup_dir / f'index.before-fin-split-{stamp}.html')

# ---------- save enriched work-level data ----------
detail_file.write_text(prefix + json.dumps(rows, ensure_ascii=False, separators=(',',':')) + ';\n', encoding='utf-8')

# ---------- patch only report functions; no observers, no navigation changes ----------
s = index_file.read_text(encoding='utf-8')

def replace_between(text, start_marker, end_marker, new_text):
    a = text.find(start_marker)
    if a < 0: raise SystemExit(f'ERROR: marker not found: {start_marker}')
    b = text.find(end_marker, a)
    if b < 0: raise SystemExit(f'ERROR: end marker not found after: {start_marker}')
    return text[:a] + new_text.rstrip() + '\n' + text[b:]

new_rebuild = r'''function rebuildCorrectedWorkData(){
 const wm=new Map(),cm=new Map(),bucket=p=>p<=0?'b0':p<=25?'b25':p<=60?'b60':p<=75?'b75':p<=90?'b90':'b90p';
 for(const r of ongoingDetails){
  const jan=clean(r.janpad),eng=clean(r.engineer)||'Unmapped',cl=clean(r.cluster)||'Unmapped',gp=clean(r.panchayat),cat=resolvedFinalCategory(r),san=num(r.sanction);
  const nrega=num(r.nregaBooked),vbg=num(r.vbgBooked ?? r.booked),overall=num(r.overallBooked ?? (nrega+vbg)),ep=san?overall*100/san:0;
  const wk=[jan,eng,cl,gp].join('¦');if(!wm.has(wk))wm.set(wk,{janpad:jan,engineer:eng,cluster:cl,panchayat:gp,workTotal:0,pmayOngoing:0,ekOngoing:0,currentFYActive:0});const z=wm.get(wk);z.workTotal++;if(/PMAY/i.test(cat))z.pmayOngoing++;if(cat==='Ek Bagiya Maa Ke Naam'||cat==='Ek Bagiya')z.ekOngoing++;if(num(r.julyMandays)>0||num(r.currentFYMandays)>0)z.currentFYActive++;
  const ck=[jan,eng,cl,gp,cat].join('¦');if(!cm.has(ck))cm.set(ck,{janpad:jan,engineer:eng,cluster:cl,panchayat:gp,category:cat,workCount:0,totalSanction:0,nregaBooked:0,vbgBooked:0,overallBooked:0,totalBooked:0,nregaAprJunMandays:0,julyMandays:0,b0:0,b25:0,b60:0,b75:0,b90:0,b90p:0});const q=cm.get(ck);q.workCount++;q.totalSanction+=san;q.nregaBooked+=nrega;q.vbgBooked+=vbg;q.overallBooked+=overall;q.totalBooked+=overall;q.nregaAprJunMandays+=num(r.nregaAprJunMandays);q.julyMandays+=num(r.julyMandays);q[bucket(ep)]++;
 }
 workmix=[...wm.values()];categorymix=[...cm.values()];
}
rebuildCorrectedWorkData();'''
s = replace_between(s, 'function rebuildCorrectedWorkData(){', 'function moneyLakh(v)', new_rebuild)

new_ongoing_all = r'''function renderOngoingAllSummary(){
  const src=categoryFiltered();
  const data=aggregate(src,['janpad','engineer','cluster'],['workCount','totalSanction','nregaBooked','vbgBooked','overallBooked','totalBooked','b0','b25','b60','b75','b90','b90p'])
    .sort((a,b)=>clean(a.janpad).localeCompare(clean(b.janpad),'hi')||clean(a.engineer).localeCompare(clean(b.engineer),'hi')||clean(a.cluster).localeCompare(clean(b.cluster),'hi'));
  const mm=aggregate(workmix,['janpad','engineer','cluster'],['workTotal','pmayOngoing','ekOngoing','currentFYActive']);
  const mmap=new Map(mm.map(r=>[[clean(r.janpad),clean(r.engineer),clean(r.cluster)].join('¦'),r]));
  for(const r of data){const x=mmap.get([clean(r.janpad),clean(r.engineer),clean(r.cluster)].join('¦'))||{};r.pmayOngoing=num(x.pmayOngoing);r.ekOngoing=num(x.ekOngoing);r.currentFYActive=num(x.currentFYActive);r.remaining=Math.max(0,num(r.totalSanction)-num(r.overallBooked));r.nregaExpPct=r.totalSanction?num(r.nregaBooked)*100/num(r.totalSanction):0;r.vbgExpPct=r.totalSanction?num(r.vbgBooked)*100/num(r.totalSanction):0;r.expPct=r.totalSanction?num(r.overallBooked)*100/num(r.totalSanction):0;}
  lastExport=data;$('viewTitle').textContent='Ongoing Work All: MGNREGA + VB-G RAM G Financial Split';$('viewMeta').textContent=`Verified R6.12 ongoing 15,687 • MGNREGA historical booked अलग • VB-G RAM G R6.12 booked अलग • Overall = दोनों का योग • ${todayDate()}`;
  let h=`<thead><tr><th>Janpad</th><th>Engineer / Upyantri</th><th>Cluster</th><th>Ongoing Works</th><th>PMAY-G</th><th>Ek Bagiya</th><th>Current FY Active</th><th>0%</th><th>1–25%</th><th>26–60%</th><th>61–75%</th><th>76–90%</th><th>&gt;90%</th><th>Sanction ₹ Lakh</th><th>MGNREGA Booked ₹ Lakh</th><th>MGNREGA Exp %</th><th>VB-G RAM G Booked ₹ Lakh</th><th>VB-G RAM G Exp %</th><th>Overall Booked ₹ Lakh</th><th>Overall Exp %</th><th>Remaining ₹ Lakh</th></tr></thead><tbody>`;
  for(const r of data){h+=`<tr>${cell(r.janpad)}${cell(r.engineer)}${cell(r.cluster)}${cell(r.workCount,true)}${cell(r.pmayOngoing,true)}${cell(r.ekOngoing,true)}${cell(r.currentFYActive,true)}${cell(r.b0,true)}${cell(r.b25,true)}${cell(r.b60,true)}${cell(r.b75,true)}${cell(r.b90,true)}${cell(r.b90p,true)}<td>${moneyLakh(r.totalSanction)}</td><td>${moneyLakh(r.nregaBooked)}</td><td>${r.nregaExpPct.toFixed(1)}%</td><td>${moneyLakh(r.vbgBooked)}</td><td>${r.vbgExpPct.toFixed(1)}%</td><td>${moneyLakh(r.overallBooked)}</td><td>${r.expPct.toFixed(1)}%</td><td>${moneyLakh(r.remaining)}</td></tr>`}
  const ks=['workCount','pmayOngoing','ekOngoing','currentFYActive','b0','b25','b60','b75','b90','b90p','totalSanction','nregaBooked','vbgBooked','overallBooked','remaining'],t={};ks.forEach(k=>t[k]=sum(data,k));const np=t.totalSanction?t.nregaBooked*100/t.totalSanction:0,vp=t.totalSanction?t.vbgBooked*100/t.totalSanction:0,op=t.totalSanction?t.overallBooked*100/t.totalSanction:0;
  h+=`<tr class="total-row"><td>TOTAL</td><td></td><td></td>${cell(t.workCount,true)}${cell(t.pmayOngoing,true)}${cell(t.ekOngoing,true)}${cell(t.currentFYActive,true)}${cell(t.b0,true)}${cell(t.b25,true)}${cell(t.b60,true)}${cell(t.b75,true)}${cell(t.b90,true)}${cell(t.b90p,true)}<td>${moneyLakh(t.totalSanction)}</td><td>${moneyLakh(t.nregaBooked)}</td><td>${np.toFixed(1)}%</td><td>${moneyLakh(t.vbgBooked)}</td><td>${vp.toFixed(1)}%</td><td>${moneyLakh(t.overallBooked)}</td><td>${op.toFixed(1)}%</td><td>${moneyLakh(t.remaining)}</td></tr>`;
  if(!data.length)h+=`<tr><td colspan="21" class="empty-table">Current filter में Ongoing Work data नहीं मिला।</td></tr>`;h+='</tbody>';$('reportTable').innerHTML=h;
}'''
s = replace_between(s, 'function renderOngoingAllSummary(){', 'function ekBagiyaFiltered(){', new_ongoing_all)

new_cat_bucket = r'''function renderCategoryBuckets(){const src=categoryFiltered();const data=aggregate(src,['category'],['workCount','totalSanction','nregaBooked','vbgBooked','overallBooked','totalBooked','b0','b25','b60','b75','b90','b90p']).sort((a,b)=>num(b.workCount)-num(a.workCount)||clean(a.category).localeCompare(clean(b.category),'hi'));data.forEach(r=>{r.nregaExpPct=r.totalSanction?num(r.nregaBooked)*100/num(r.totalSanction):0;r.vbgExpPct=r.totalSanction?num(r.vbgBooked)*100/num(r.totalSanction):0;r.expPct=r.totalSanction?num(r.overallBooked)*100/num(r.totalSanction):0});lastExport=data;$('viewTitle').textContent='Final Category-wise Ongoing Work Buckets';$('viewMeta').textContent=`${fmt(data.length)} Final Categories • MGNREGA और VB-G RAM G booked अलग-अलग • Overall Expenditure = दोनों का योग ÷ Total Sanction • ${todayDate()}`;let h=`<thead><tr><th>Work Category</th><th>Total Works</th><th>0%</th><th>1%–25%</th><th>26%–60%</th><th>61%–75%</th><th>76%–90%</th><th>&gt;90%</th><th>Sanction ₹ Lakh</th><th>MGNREGA Booked ₹ Lakh</th><th>MGNREGA Exp %</th><th>VB-G RAM G Booked ₹ Lakh</th><th>VB-G RAM G Exp %</th><th>Overall Booked ₹ Lakh</th><th>Overall Exp %</th></tr></thead><tbody>`;for(const r of data){h+=`<tr>${cell(r.category)}${cell(r.workCount,true)}<td class="bucket-zero">${fmt(r.b0)}</td>${cell(r.b25,true)}${cell(r.b60,true)}${cell(r.b75,true)}${cell(r.b90,true)}<td class="bucket-good">${fmt(r.b90p)}</td><td>${moneyLakh(r.totalSanction)}</td><td>${moneyLakh(r.nregaBooked)}</td><td>${r.nregaExpPct.toFixed(1)}%</td><td>${moneyLakh(r.vbgBooked)}</td><td>${r.vbgExpPct.toFixed(1)}%</td><td>${moneyLakh(r.overallBooked)}</td><td><span class="exp-pct-chip ${r.expPct===0?'critical':r.expPct<=25?'low':r.expPct>90?'good':''}">${r.expPct.toFixed(1)}%</span></td></tr>`}const t={};['workCount','totalSanction','nregaBooked','vbgBooked','overallBooked','b0','b25','b60','b75','b90','b90p'].forEach(k=>t[k]=sum(data,k));const np=t.totalSanction?t.nregaBooked*100/t.totalSanction:0,vp=t.totalSanction?t.vbgBooked*100/t.totalSanction:0,op=t.totalSanction?t.overallBooked*100/t.totalSanction:0;h+=`<tr class="total-row"><td>TOTAL</td>${cell(t.workCount,true)}${cell(t.b0,true)}${cell(t.b25,true)}${cell(t.b60,true)}${cell(t.b75,true)}${cell(t.b90,true)}${cell(t.b90p,true)}<td>${moneyLakh(t.totalSanction)}</td><td>${moneyLakh(t.nregaBooked)}</td><td>${np.toFixed(1)}%</td><td>${moneyLakh(t.vbgBooked)}</td><td>${vp.toFixed(1)}%</td><td>${moneyLakh(t.overallBooked)}</td><td>${op.toFixed(1)}%</td></tr>`;if(!data.length)h+=`<tr><td colspan="15" class="empty-table">Current filter में Category data नहीं मिला।</td></tr>`;h+='</tbody>';$('reportTable').innerHTML=h}'''
s = replace_between(s, 'function renderCategoryBuckets(){', 'function renderExpBuckets(){', new_cat_bucket)

new_cat_sub = r'''function renderCategorySubEngineer(){
 const src=categoryFiltered();const data=aggregate(src,['category','janpad','engineer','cluster'],['workCount','totalSanction','nregaBooked','vbgBooked','overallBooked','totalBooked','nregaAprJunMandays','julyMandays','b0','b25','b60','b75','b90','b90p']);
 data.forEach(r=>{r.remaining=Math.max(0,r.totalSanction-r.overallBooked);r.nregaExpPct=r.totalSanction?r.nregaBooked*100/r.totalSanction:0;r.vbgExpPct=r.totalSanction?r.vbgBooked*100/r.totalSanction:0;r.expPct=r.totalSanction?r.overallBooked*100/r.totalSanction:0});data.sort((a,b)=>clean(a.category).localeCompare(clean(b.category),'hi')||clean(a.janpad).localeCompare(clean(b.janpad),'hi')||clean(a.engineer).localeCompare(clean(b.engineer),'hi'));lastExport=data;
 $('viewTitle').textContent='Work Category × Sub Engineer — MGNREGA / VB-G RAM G Split';$('viewMeta').textContent=`${fmt(data.length)} Category/Sub Engineer rows • Verified R6.12 categories unchanged • ${todayDate()}`;
 let h=`<thead><tr><th>Work Category</th><th>District</th><th>Janpad</th><th>Sub Engineer</th><th>Cluster</th><th>Works</th><th>NREGA Mandays<br>01 Apr–30 Jun</th><th>Mandays<br>01 Jul–Today</th><th>0%</th><th>1–25%</th><th>26–60%</th><th>61–75%</th><th>76–90%</th><th>&gt;90%</th><th>Sanction ₹ Lakh</th><th>MGNREGA Booked ₹ Lakh</th><th>MGNREGA Exp %</th><th>VB-G RAM G Booked ₹ Lakh</th><th>VB-G RAM G Exp %</th><th>Overall Booked ₹ Lakh</th><th>Overall Exp %</th><th>Remaining ₹ Lakh</th></tr></thead><tbody>`;
 for(const r of data){h+=`<tr>${cell(r.category)}${cell(districtOf(r.janpad))}${cell(r.janpad)}${cell(r.engineer)}${cell(r.cluster)}${cell(r.workCount,true)}${cell(r.nregaAprJunMandays,true)}${cell(r.julyMandays,true)}<td class="bucket-zero">${fmt(r.b0)}</td>${cell(r.b25,true)}${cell(r.b60,true)}${cell(r.b75,true)}${cell(r.b90,true)}<td class="bucket-good">${fmt(r.b90p)}</td><td>${moneyLakh(r.totalSanction)}</td><td>${moneyLakh(r.nregaBooked)}</td><td>${r.nregaExpPct.toFixed(1)}%</td><td>${moneyLakh(r.vbgBooked)}</td><td>${r.vbgExpPct.toFixed(1)}%</td><td>${moneyLakh(r.overallBooked)}</td><td>${r.expPct.toFixed(1)}%</td><td>${moneyLakh(r.remaining)}</td></tr>`}
 const t={};['workCount','nregaAprJunMandays','julyMandays','b0','b25','b60','b75','b90','b90p','totalSanction','nregaBooked','vbgBooked','overallBooked'].forEach(k=>t[k]=sum(data,k));t.remaining=Math.max(0,t.totalSanction-t.overallBooked);const np=t.totalSanction?t.nregaBooked*100/t.totalSanction:0,vp=t.totalSanction?t.vbgBooked*100/t.totalSanction:0,op=t.totalSanction?t.overallBooked*100/t.totalSanction:0;h+=`<tr class="total-row"><td>TOTAL</td><td></td><td></td><td></td><td></td>${cell(t.workCount,true)}${cell(t.nregaAprJunMandays,true)}${cell(t.julyMandays,true)}${cell(t.b0,true)}${cell(t.b25,true)}${cell(t.b60,true)}${cell(t.b75,true)}${cell(t.b90,true)}${cell(t.b90p,true)}<td>${moneyLakh(t.totalSanction)}</td><td>${moneyLakh(t.nregaBooked)}</td><td>${np.toFixed(1)}%</td><td>${moneyLakh(t.vbgBooked)}</td><td>${vp.toFixed(1)}%</td><td>${moneyLakh(t.overallBooked)}</td><td>${op.toFixed(1)}%</td><td>${moneyLakh(t.remaining)}</td></tr>`;if(!data.length)h+=`<tr><td colspan="22" class="empty-table">Current filter में Category × Sub Engineer data नहीं मिला।</td></tr>`;h+='</tbody>';const table=$('reportTable');table.innerHTML=h;
}'''
s = replace_between(s, 'function renderCategorySubEngineer(){', 'function renderCategoryWorks(){', new_cat_sub)

new_cat_works = r'''function renderCategoryWorks(){
 const data=correctedWorkFiltered().slice().sort((a,b)=>resolvedFinalCategory(a).localeCompare(resolvedFinalCategory(b),'hi')||clean(a.janpad).localeCompare(clean(b.janpad),'hi')||clean(a.engineer).localeCompare(clean(b.engineer),'hi')||clean(a.code).localeCompare(clean(b.code)));lastExport=data;
 const cats=new Set(data.map(r=>resolvedFinalCategory(r))),sts=new Set(data.map(r=>clean(r.status)));$('viewTitle').textContent='MIS 6.12 — Engineer & Final Category-wise Work Details';$('viewMeta').textContent=`${fmt(data.length)} works • ${fmt(cats.size)} Final Work Categories • MGNREGA / VB-G RAM G split • ${[...sts].filter(Boolean).join(', ')||'Selected status'} • ${todayDate()}`;
 let h=`<thead><tr><th>S.No.</th><th>Status</th><th>Final Work Category</th><th>District</th><th>Janpad</th><th>Sub Engineer</th><th>Cluster</th><th>GP</th><th>FY</th><th>Work Code</th><th>Work Name</th><th>Sanction ₹</th><th>MGNREGA Booked ₹</th><th>MGNREGA Exp %</th><th>VB-G RAM G Booked ₹</th><th>VB-G Exp %</th><th>Overall Booked ₹</th><th>Overall Exp %</th><th>NREGA Mandays<br>01 Apr–30 Jun</th><th>Mandays<br>01 Jul–Today</th></tr></thead><tbody>`;
 data.forEach((r,i)=>{const cat=resolvedFinalCategory(r),san=num(r.sanction),nb=num(r.nregaBooked),vb=num(r.vbgBooked ?? r.booked),ob=num(r.overallBooked ?? (nb+vb));h+=`<tr>${cell(i+1,true)}${cell(r.status)}${cell(cat)}${cell(districtOf(r.janpad))}${cell(r.janpad)}${cell(r.engineer)}${cell(r.cluster)}${cell(r.panchayat)}${cell(r.fy)}${cell(r.code)}${cell(r.name)}<td>${san.toLocaleString('en-IN',{maximumFractionDigits:2})}</td><td>${nb.toLocaleString('en-IN',{maximumFractionDigits:2})}</td><td>${(san?nb*100/san:0).toFixed(1)}%</td><td>${vb.toLocaleString('en-IN',{maximumFractionDigits:2})}</td><td>${(san?vb*100/san:0).toFixed(1)}%</td><td>${ob.toLocaleString('en-IN',{maximumFractionDigits:2})}</td><td>${(san?ob*100/san:0).toFixed(1)}%</td>${cell(r.nregaAprJunMandays,true)}${cell(r.julyMandays,true)}</tr>`});if(!data.length)h+=`<tr><td colspan="20" class="empty-table">Current filter/category/status में work नहीं मिला।</td></tr>`;h+='</tbody>';$('reportTable').innerHTML=h;
}'''
s = replace_between(s, 'function renderCategoryWorks(){', 'function renderIncompleteWorks(){', new_cat_works)

new_details = r'''function renderOngoingDetails(){
 const data=filterRows(ongoingDetails).slice().sort((a,b)=>clean(a.janpad).localeCompare(clean(b.janpad),'hi')||clean(a.engineer).localeCompare(clean(b.engineer),'hi')||clean(a.panchayat).localeCompare(clean(b.panchayat),'hi')||clean(a.code).localeCompare(clean(b.code)));
 lastExport=data;$('viewTitle').textContent='Ongoing Works: Janpad-wise Work Sheet';$('viewMeta').innerHTML=`${fmt(data.length)} ongoing works • Verified R6.12 • MGNREGA / VB-G RAM G financial split • ${todayDate()}`;
 let h=`<thead><tr><th>S.No.</th><th>Janpad</th><th>Engineer / Upyantri</th><th>Cluster</th><th>GP</th><th>FY</th><th>Work Code</th><th>Work Name</th><th>Work Type</th><th>Sanction ₹</th><th>MGNREGA Booked ₹</th><th>MGNREGA Exp %</th><th>VB-G RAM G Booked ₹</th><th>VB-G Exp %</th><th>Overall Booked ₹</th><th>Overall Exp %</th><th>Total Mandays</th><th>NREGA 01 Apr–30 Jun Mandays</th><th>VBGRAMG 01 Jul–Today Mandays</th></tr></thead><tbody>`;
 for(let i=0;i<data.length;i++){const r=data[i],san=num(r.sanction),nb=num(r.nregaBooked),vb=num(r.vbgBooked ?? r.booked),ob=num(r.overallBooked ?? (nb+vb));h+=`<tr>${cell(i+1,true)}${cell(r.janpad)}${cell(r.engineer)}${cell(r.cluster)}${cell(r.panchayat)}${cell(r.fy)}${cell(r.code)}${cell(r.name)}${cell(r.type)}<td>${san.toLocaleString('en-IN',{maximumFractionDigits:2})}</td><td>${nb.toLocaleString('en-IN',{maximumFractionDigits:2})}</td><td>${(san?nb*100/san:0).toFixed(1)}%</td><td>${vb.toLocaleString('en-IN',{maximumFractionDigits:2})}</td><td>${(san?vb*100/san:0).toFixed(1)}%</td><td>${ob.toLocaleString('en-IN',{maximumFractionDigits:2})}</td><td>${(san?ob*100/san:0).toFixed(1)}%</td>${cell(r.mandays,true)}${cell(r.nregaAprJunMandays,true)}${cell(r.julyMandays,true)}</tr>`}
 if(!data.length)h+=`<tr><td colspan="19" class="empty-table">Current filter में Ongoing Work नहीं मिला।</td></tr>`;h+='</tbody>';$('reportTable').innerHTML=h;
}'''
s = replace_between(s, 'function renderOngoingDetails(){', 'function emusterReportDate(){', new_details)

# Add a build marker only; no DOM observers.
if 'SRDM_FIN_SPLIT_R612_2026_09_14' not in s:
    s = s.replace('</head>', '<meta name="srdm-fin-split" content="SRDM_FIN_SPLIT_R612_2026_09_14">\n</head>', 1)

index_file.write_text(s, encoding='utf-8')

print('====================================================')
print('SUCCESS DATA VALIDATION - FINANCIAL SPLIT')
print('R6.12 ongoing works        :', len(rows))
print('PMAY-G incl IAY            :', pmay)
print('IAY separate               :', iay)
print('Ek Bagiya ongoing          :', ek)
print('MGNREGA baseline matched   :', matched)
print('MGNREGA baseline missing   :', len(missing), '(treated as 0; mostly new works)')
print('MGNREGA booked total Rs    :', round(sum_nrega,2))
print('VB-G RAM G booked total Rs :', round(sum_vbg,2))
print('Overall booked total Rs    :', round(sum_overall,2))
print('Index patch                : OK')
print('Counts/categories           : UNCHANGED')
print('====================================================')
