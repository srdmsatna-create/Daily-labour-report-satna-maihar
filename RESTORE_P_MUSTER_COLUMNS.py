from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

# Remove the older compact patch that deleted PMAY/Ek Bagiya columns from the rendered table.
start='<!-- ===== OFFICIAL JANPAD BOX V1 ===== -->'
end='<!-- ===== END OFFICIAL JANPAD BOX V1 ===== -->'
if start in s and end in s:
    a=s.index(start); b=s.index(end,a)+len(end); s=s[:a]+s[b:]

# Add a last-running guard so PMAY-G / Ek Bagiya always show Ongoing + MR Issued + MR %.
start2='<!-- ===== RESTORE LIVE MR COLUMNS V1 ===== -->'
end2='<!-- ===== END RESTORE LIVE MR COLUMNS V1 ===== -->'
if start2 in s and end2 in s:
    a=s.index(start2); b=s.index(end2,a)+len(end2); s=s[:a]+s[b:]

block=r'''
<!-- ===== RESTORE LIVE MR COLUMNS V1 ===== -->
<script>
(function(){
  function pct1(a,b){return Number(b||0)>0?((Number(a||0)*100/Number(b||0)).toFixed(1)+'%'):'0.0%'}

  // Keep verified R6.12 Ongoing counts, but live MR Issued values from today's official source.
  const verified={
    'AMARPATAN':{all:1383,pmay:865,ek:109},
    'MAIHAR':{all:2482,pmay:1512,ek:86},
    'MAJHGAWAN':{all:2204,pmay:1255,ek:85},
    'NAGOD':{all:2311,pmay:1637,ek:99},
    'RAMNAGAR':{all:1166,pmay:910,ek:105},
    'RAMPUR BAGHELAN':{all:3264,pmay:2713,ek:75},
    'SATNA':{all:1048,pmay:422,ek:94},
    'UNCHAHARA':{all:1829,pmay:1185,ek:102}
  };
  function applyVerified(){
    if(!Array.isArray(official))return;
    for(const r of official){
      const j=String(r.janpad||'').trim().toUpperCase(),v=verified[j];
      if(!v)continue;
      r.ongoingAll=v.all; r.pmayOngoing=v.pmay; r.ekOngoing=v.ek;
      // r.pmayMR and r.ekMR intentionally NOT changed: they stay today's live official MR issued values.
    }
  }

  renderOfficial=function(){
    applyVerified();
    const data=sortRows(officialFiltered().map(r=>({...r,ongoing:num(r.ongoingAll),worksMR:num(r.mrAll),labour:num(r.labourAll),gpsProgress:num(r.musterGP)})),'ongoing',['janpad']);
    lastExport=data;
    $('viewTitle').textContent='Official Janpad Daily Report';
    $('viewMeta').textContent=`${data.length} Janpad • R6.12 verified ongoing + Live MR • ${todayDate()}`;
    let h=`<thead><tr><th rowspan="2">District</th><th rowspan="2">Janpad</th><th colspan="3">Gram Panchayat</th><th colspan="5">All Types of Works / Screen-2</th><th colspan="2">Individual Land (Cat-IV)</th><th colspan="3">Community Works</th><th colspan="3">PMAY-G</th><th colspan="4">Ek Bagiya</th></tr><tr><th>Total GP</th><th>GP Progress</th><th>Dysfunctional</th><th>Labour</th><th>Works with MR</th><th>Total Ongoing Work</th><th>Muster Rolls</th><th>MR %</th><th>Labour</th><th>Works MR</th><th>Labour</th><th>Works MR</th><th>Share %</th><th>Ongoing</th><th>MR Issued</th><th>MR %</th><th>Labour</th><th>Ongoing</th><th>MR Issued</th><th>MR %</th></tr></thead><tbody>`;
    for(const r of data){
      h+=`<tr>${cell(districtOf(r.janpad))}${cell(r.janpad)}${cell(r.totalGP,true)}${cell(r.musterGP,true)}${cell(r.dysfunctionalGP,true)}${cell(r.labourAll,true)}${cell(r.mrAll,true)}${cell(r.ongoingAll,true)}${cell(r.mrs||0,true)}<td>${badge(r.mrAll,r.ongoingAll)}</td>${cell(r.labourIndividual,true)}${cell(r.mrIndividual,true)}${cell(r.labourCommunity,true)}${cell(r.mrCommunity,true)}<td>${badge(r.mrCommunity,r.mrAll)}</td>${cell(r.pmayOngoing,true)}${cell(r.pmayMR,true)}<td>${pct1(r.pmayMR,r.pmayOngoing)}</td>${cell(r.ekLabour,true)}${cell(r.ekOngoing,true)}${cell(r.ekMR,true)}<td>${pct1(r.ekMR,r.ekOngoing)}</td></tr>`;
    }
    const keys=['totalGP','musterGP','dysfunctionalGP','labourAll','mrAll','mrs','ongoingAll','labourIndividual','mrIndividual','labourCommunity','mrCommunity','pmayOngoing','pmayMR','ekLabour','ekOngoing','ekMR'],t={};
    keys.forEach(k=>t[k]=sum(data,k));
    h+=`<tr class="total-row"><td>TOTAL</td><td></td>${cell(t.totalGP,true)}${cell(t.musterGP,true)}${cell(t.dysfunctionalGP,true)}${cell(t.labourAll,true)}${cell(t.mrAll,true)}${cell(t.ongoingAll,true)}${cell(t.mrs,true)}<td>${pct1(t.mrAll,t.ongoingAll)}</td>${cell(t.labourIndividual,true)}${cell(t.mrIndividual,true)}${cell(t.labourCommunity,true)}${cell(t.mrCommunity,true)}<td>${pct1(t.mrCommunity,t.mrAll)}</td>${cell(t.pmayOngoing,true)}${cell(t.pmayMR,true)}<td>${pct1(t.pmayMR,t.pmayOngoing)}</td>${cell(t.ekLabour,true)}${cell(t.ekOngoing,true)}${cell(t.ekMR,true)}<td>${pct1(t.ekMR,t.ekOngoing)}</td></tr></tbody>`;
    $('reportTable').innerHTML=h;
  };

  // Engineer report keeps same three PMAY and four Ek Bagiya columns. Its ongoing counts are apportioned
  // from the verified Janpad totals while MR Issued remains apportioned from today's official values.
  const oldEngineerOfficialData=engineerOfficialData;
  engineerOfficialData=function(list){applyVerified();return oldEngineerOfficialData(list)};

  applyVerified();
})();
</script>
<!-- ===== END RESTORE LIVE MR COLUMNS V1 ===== -->
'''

if '</body>' not in s: raise SystemExit('index.html has no </body>')
s=s.replace('</body>',block+'\n</body>',1)
p.write_text(s,encoding='utf-8')
print('DONE: PMAY-G and Ek Bagiya Ongoing + MR Issued + MR % restored')
