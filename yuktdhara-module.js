(function () {
  'use strict';
  const DATA = window.YUKTDHARA_DATA;
  if (!DATA) return;

  const MAIHAR = new Set(['AMARPATAN', 'MAIHAR', 'RAMNAGAR']);
  const SATNA = new Set(['MAJHGAWAN', 'NAGOD', 'RAMPUR BAGHELAN', 'SATNA', 'UNCHAHARA']);
  const $ = (id) => document.getElementById(id);
  const esc = (value) => String(value ?? '').replace(/[&<>"']/g, (char) => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const normalize = (value) => String(value ?? '').trim().toUpperCase().replace(/[^A-Z0-9\u0900-\u097F]+/g, '');
  const normalizeJanpad = (value) => normalize(value) === 'RAMPORBAGHELAN' ? 'RAMPURBAGHELAN' : normalize(value);
  const keyOf = (janpad, gp) => `${normalizeJanpad(janpad)}|${normalize(gp)}`;
  const districtOf = (janpad) => MAIHAR.has(janpad) ? 'MAIHAR' : SATNA.has(janpad) ? 'SATNA' : 'OTHER';
  const displayJanpad = (janpad) => janpad === 'SATNA' ? 'SOHAWAL' : janpad;
  const fmt = (value) => Number(value || 0).toLocaleString('en-IN');

  const mapping = new Map(DATA.mapping.map((row) => [keyOf(row.janpad, row.gp), row]));
  const sets = {};
  Object.entries(DATA.lists).forEach(([name, rows]) => { sets[name] = new Set(rows.map((row) => keyOf(row.janpad, row.gp))); });
  const gpRows = DATA.lists.master.map((row) => {
    const map = mapping.get(keyOf(row.janpad, row.gp)) || {};
    const janpad = String(row.janpad || map.janpad || '').trim().toUpperCase();
    const id = keyOf(janpad, row.gp);
    return {
      district: districtOf(janpad), janpad, gp: row.gp,
      engineer: map.engineer || 'UNMAPPED', cluster: map.cluster || '',
      started: sets.started.has(id), submitted: sets.submitted.has(id),
      notStarted: sets.notStarted.has(id), gasApproved: sets.gasApproved.has(id)
    };
  });

  const css = document.createElement('style');
  css.textContent = `
    #yuktdharaReport{position:fixed;inset:0;z-index:100000;background:#f3f7fb;color:#102033;overflow:auto;display:none;font-family:Inter,"Noto Sans Devanagari","Segoe UI",Arial,sans-serif}
    #yuktdharaReport.open{display:block}.yukt-shell{max-width:1500px;margin:0 auto;padding:22px 24px 42px}
    .yukt-head{display:flex;justify-content:space-between;gap:18px;align-items:center;background:linear-gradient(135deg,#3b1d93,#7048d8);color:#fff;border-radius:20px;padding:22px 26px;box-shadow:0 16px 38px rgba(64,36,145,.22)}
    .yukt-head h1{margin:0;font-size:28px}.yukt-head p{margin:6px 0 0;color:#e6ddff}.yukt-actions{display:flex;flex-wrap:wrap;gap:9px;justify-content:flex-end}
    .yukt-btn{border:0;border-radius:10px;padding:11px 15px;font-weight:750;cursor:pointer;background:#fff;color:#3b1d93}.yukt-btn.secondary{background:#efeaff}.yukt-btn.close{background:#271064;color:#fff;border:1px solid #957cff}
    .yukt-kpis{display:grid;grid-template-columns:repeat(5,minmax(150px,1fr));gap:13px;margin:17px 0}.yukt-kpi{background:#fff;border:1px solid #dce5ef;border-radius:15px;padding:16px 18px;box-shadow:0 5px 16px rgba(31,56,88,.06)}
    .yukt-kpi span{display:block;color:#61738b;font-size:13px;font-weight:700}.yukt-kpi b{display:block;font-size:28px;margin-top:5px}.yukt-kpi.started{border-top:4px solid #ef9f21}.yukt-kpi.submitted{border-top:4px solid #1976d2}.yukt-kpi.notstarted{border-top:4px solid #d8415a}.yukt-kpi.gas{border-top:4px solid #08a36a}.yukt-kpi.total{border-top:4px solid #7048d8}
    .yukt-controls{display:grid;grid-template-columns:repeat(4,minmax(170px,1fr)) auto;gap:10px;background:#fff;border:1px solid #dce5ef;border-radius:15px;padding:14px;margin-bottom:14px;align-items:end}
    .yukt-controls label{font-size:12px;font-weight:800;color:#53657c}.yukt-controls select{display:block;width:100%;margin-top:5px;padding:10px;border:1px solid #bfcddd;border-radius:9px;background:#fff;font-size:14px}
    .yukt-meta{display:flex;justify-content:space-between;gap:10px;align-items:center;margin:10px 2px;color:#53657c;font-size:13px}.yukt-table-wrap{background:#fff;border:1px solid #dce5ef;border-radius:15px;overflow:auto;box-shadow:0 5px 16px rgba(31,56,88,.05)}
    .yukt-table{border-collapse:separate;border-spacing:0;width:100%;min-width:1180px;font-size:13px}.yukt-table th{position:sticky;top:0;background:#eef2ff;color:#382477;padding:12px 10px;border-bottom:2px solid #cfd7f5;text-align:left;z-index:2}.yukt-table td{padding:11px 10px;border-bottom:1px solid #e6edf4;vertical-align:top}.yukt-table tbody tr:hover{background:#fafbff}.yukt-table td.num,.yukt-table th.num{text-align:center;font-weight:800}
    .yukt-status{display:inline-flex;min-width:32px;justify-content:center;border-radius:999px;padding:4px 8px;font-weight:850}.yukt-status.s{background:#fff0d6;color:#9a5900}.yukt-status.u{background:#dfeeff;color:#075ca8}.yukt-status.n{background:#ffe4e9;color:#a91c38}.yukt-status.g{background:#daf7eb;color:#08794f}
    .yukt-gps summary{cursor:pointer;color:#4d2ead;font-weight:750}.yukt-gp-list{max-width:520px;max-height:210px;overflow:auto;margin-top:7px;display:grid;gap:5px}.yukt-gp{background:#f5f7fb;border:1px solid #e0e7f0;border-radius:8px;padding:7px 8px}.yukt-gp b{display:block}.yukt-tags{display:flex;gap:4px;flex-wrap:wrap;margin-top:3px}.yukt-tag{font-size:10px;border-radius:999px;padding:2px 6px;background:#e8edf4;color:#405269}.yukt-source{color:#5e6d81}.yukt-source a{color:#4d2ead;font-weight:700}
    @media(max-width:900px){.yukt-shell{padding:12px}.yukt-head{align-items:flex-start;flex-direction:column}.yukt-kpis{grid-template-columns:repeat(2,1fr)}.yukt-controls{grid-template-columns:1fr 1fr}.yukt-actions{justify-content:flex-start}}
    @media(max-width:520px){.yukt-kpis,.yukt-controls{grid-template-columns:1fr}.yukt-head h1{font-size:22px}}
    @media print{body.yuktdhara-print>*:not(#yuktdharaReport){display:none!important}body.yuktdhara-print #yuktdharaReport{position:static!important;display:block!important;overflow:visible!important;background:#fff!important}body.yuktdhara-print .yukt-actions,body.yuktdhara-print .yukt-controls{display:none!important}body.yuktdhara-print .yukt-shell{max-width:none;padding:0}body.yuktdhara-print .yukt-head{box-shadow:none;border:1px solid #888;color:#111;background:#fff}body.yuktdhara-print .yukt-head p{color:#444}.yukt-table th{position:static}.yukt-table-wrap{overflow:visible;box-shadow:none}.yukt-table{min-width:0;font-size:9px}.yukt-gps details:not([open]) summary::after{content:' (GP list available in Excel)'}}
  `;
  document.head.appendChild(css);

  const report = document.createElement('section');
  report.id = 'yuktdharaReport';
  report.setAttribute('aria-label', 'Bhuvan Yuktdhara Sub Engineer-wise Report');
  report.innerHTML = `<div class="yukt-shell">
    <header class="yukt-head"><div><h1>Bhuvan Yuktdhara — Sub Engineer-wise Report</h1><p>District Satna (5 Janpad) • District Maihar (3 Janpad) • Official status as on ${esc(DATA.asOf)}</p></div>
      <div class="yukt-actions"><button class="yukt-btn secondary" id="yuktOfficial">Official Bhuvan</button><button class="yukt-btn" id="yuktExcel">Excel Download</button><button class="yukt-btn" id="yuktPrint">Print / PDF</button><button class="yukt-btn close" id="yuktClose">Dashboard पर वापस</button></div></header>
    <div class="yukt-kpis" id="yuktKpis"></div>
    <div class="yukt-controls">
      <label>District<select id="yuktDistrict"><option value="ALL">Satna + Maihar</option><option value="SATNA">SATNA</option><option value="MAIHAR">MAIHAR</option></select></label>
      <label>Janpad<select id="yuktJanpad"><option value="ALL">सभी Janpad</option></select></label>
      <label>Sub Engineer<select id="yuktEngineer"><option value="ALL">सभी Sub Engineer</option></select></label>
      <label>GP Status<select id="yuktStatus"><option value="ALL">सभी GP</option><option value="started">Plan Started</option><option value="submitted">Plan Submitted</option><option value="notStarted">Plan Not Started</option><option value="gasApproved">GAS Approved</option></select></label>
      <button class="yukt-btn secondary" id="yuktReset">Reset</button>
    </div>
    <div class="yukt-meta"><b id="yuktResultMeta"></b><span class="yukt-source">Source: <a href="${esc(DATA.officialUrl)}" target="_blank" rel="noopener noreferrer">NRSC Bhuvan Yuktdhara</a></span></div>
    <div class="yukt-table-wrap"><table class="yukt-table" id="yuktTable"></table></div>
  </div>`;
  document.body.appendChild(report);

  function values(rows, key) { return [...new Set(rows.map((row) => row[key]).filter(Boolean))].sort((a,b) => a.localeCompare(b, 'hi')); }
  function setOptions(select, items, label, display) {
    const current = select.value;
    select.innerHTML = `<option value="ALL">${esc(label)}</option>` + items.map((item) => `<option value="${esc(item)}">${esc(display ? display(item) : item)}</option>`).join('');
    if ([...select.options].some((option) => option.value === current)) select.value = current;
  }
  function filtered() {
    const district = $('yuktDistrict').value, janpad = $('yuktJanpad').value, engineer = $('yuktEngineer').value, status = $('yuktStatus').value;
    return gpRows.filter((row) => (district === 'ALL' || row.district === district) && (janpad === 'ALL' || row.janpad === janpad) && (engineer === 'ALL' || row.engineer === engineer) && (status === 'ALL' || row[status]));
  }
  function cascade() {
    let rows = gpRows;
    const district = $('yuktDistrict').value;
    if (district !== 'ALL') rows = rows.filter((row) => row.district === district);
    setOptions($('yuktJanpad'), values(rows, 'janpad'), 'सभी Janpad', displayJanpad);
    if ($('yuktJanpad').value !== 'ALL') rows = rows.filter((row) => row.janpad === $('yuktJanpad').value);
    setOptions($('yuktEngineer'), values(rows, 'engineer'), 'सभी Sub Engineer');
  }
  function grouped(rows) {
    const groups = new Map();
    rows.forEach((row) => {
      const id = `${row.district}|${row.janpad}|${row.engineer}`;
      if (!groups.has(id)) groups.set(id, {district:row.district, janpad:row.janpad, engineer:row.engineer, clusters:new Set(), gps:[]});
      const group = groups.get(id); if (row.cluster) group.clusters.add(row.cluster); group.gps.push(row);
    });
    return [...groups.values()].map((group) => ({...group, cluster:[...group.clusters].sort((a,b)=>a.localeCompare(b,'hi')).join(', '), total:group.gps.length, started:group.gps.filter(x=>x.started).length, submitted:group.gps.filter(x=>x.submitted).length, notStarted:group.gps.filter(x=>x.notStarted).length, gasApproved:group.gps.filter(x=>x.gasApproved).length})).sort((a,b)=>a.district.localeCompare(b.district)||a.janpad.localeCompare(b.janpad)||a.engineer.localeCompare(b.engineer,'hi'));
  }
  function gpDetail(group) {
    return `<details class="yukt-gps"><summary>${fmt(group.gps.length)} संबंधित GP नाम</summary><div class="yukt-gp-list">${group.gps.sort((a,b)=>a.gp.localeCompare(b.gp)).map((row)=>`<div class="yukt-gp"><b>${esc(row.gp)}</b><div class="yukt-tags">${row.started?'<span class="yukt-tag">Started</span>':''}${row.submitted?'<span class="yukt-tag">Submitted</span>':''}${row.notStarted?'<span class="yukt-tag">Not Started</span>':''}${row.gasApproved?'<span class="yukt-tag">GAS Approved</span>':''}</div></div>`).join('')}</div></details>`;
  }
  function render() {
    const rows = filtered(), groups = grouped(rows);
    const count = (key) => rows.filter((row) => row[key]).length;
    $('yuktKpis').innerHTML = [
      ['total','कुल GP',rows.length],['started','Plan Started GP',count('started')],['submitted','Plan Submitted GP',count('submitted')],['notstarted','Plan Not Started GP',count('notStarted')],['gas','GAS Approved GP',count('gasApproved')]
    ].map(([cls,label,value])=>`<div class="yukt-kpi ${cls}"><span>${label}</span><b>${fmt(value)}</b></div>`).join('');
    $('yuktResultMeta').textContent = `${groups.length} Sub Engineer rows • ${rows.length} GP • ${$('yuktDistrict').value==='ALL'?'2 District / 8 Janpad':$('yuktDistrict').value}`;
    $('yuktTable').innerHTML = `<thead><tr><th>District</th><th>Janpad</th><th>Sub Engineer</th><th>Cluster(s)</th><th class="num">कुल GP</th><th class="num">Plan Started</th><th class="num">Plan Submitted</th><th class="num">Plan Not Started</th><th class="num">GAS Approved</th><th>संबंधित GP नाम</th></tr></thead><tbody>${groups.map((g)=>`<tr><td><b>${esc(g.district)}</b></td><td>${esc(displayJanpad(g.janpad))}</td><td><b>${esc(g.engineer)}</b></td><td>${esc(g.cluster)}</td><td class="num">${fmt(g.total)}</td><td class="num"><span class="yukt-status s">${fmt(g.started)}</span></td><td class="num"><span class="yukt-status u">${fmt(g.submitted)}</span></td><td class="num"><span class="yukt-status n">${fmt(g.notStarted)}</span></td><td class="num"><span class="yukt-status g">${fmt(g.gasApproved)}</span></td><td>${gpDetail(g)}</td></tr>`).join('') || '<tr><td colspan="10">Current filter में GP नहीं मिला।</td></tr>'}</tbody>`;
    window.__YUKTDHARA_EXPORT = {rows, groups};
  }
  function exportExcel() {
    const current = window.__YUKTDHARA_EXPORT || {rows:filtered(),groups:grouped(filtered())};
    const summary = current.groups.map((g)=>({'District':g.district,'Janpad':displayJanpad(g.janpad),'Sub Engineer':g.engineer,'Cluster(s)':g.cluster,'कुल GP':g.total,'Plan Started GP':g.started,'Plan Submitted GP':g.submitted,'Plan Not Started GP':g.notStarted,'GAS Approved GP':g.gasApproved,'संबंधित GP नाम':g.gps.map(x=>x.gp).sort().join(', ')}));
    const detail = current.rows.map((r)=>({'District':r.district,'Janpad':displayJanpad(r.janpad),'Sub Engineer':r.engineer,'Cluster':r.cluster,'GP Name':r.gp,'Plan Started':r.started?'Yes':'No','Plan Submitted':r.submitted?'Yes':'No','Plan Not Started':r.notStarted?'Yes':'No','GAS Approved':r.gasApproved?'Yes':'No'}));
    if (window.XLSX) {
      const book = XLSX.utils.book_new(); XLSX.utils.book_append_sheet(book, XLSX.utils.json_to_sheet(summary), 'Sub Engineer Summary'); XLSX.utils.book_append_sheet(book, XLSX.utils.json_to_sheet(detail), 'GP Status Detail'); XLSX.writeFile(book, `Bhuvan_Yuktdhara_Sub_Engineer_${DATA.asOf}.xlsx`); return;
    }
    const cols = Object.keys(summary[0] || {}), csv = '\uFEFF' + [cols, ...summary.map(row=>cols.map(col=>`"${String(row[col]??'').replace(/"/g,'""')}"`))].map(row=>row.join(',')).join('\n');
    const link=document.createElement('a');link.href=URL.createObjectURL(new Blob([csv],{type:'text/csv;charset=utf-8'}));link.download=`Bhuvan_Yuktdhara_Sub_Engineer_${DATA.asOf}.csv`;link.click();setTimeout(()=>URL.revokeObjectURL(link.href),1000);
  }
  function open() { report.classList.add('open'); document.body.style.overflow='hidden'; cascade(); render(); report.scrollTop=0; }
  function close() { report.classList.remove('open'); document.body.style.overflow=''; }
  $('yuktClose').addEventListener('click', close);
  $('yuktOfficial').addEventListener('click', ()=>window.open(DATA.officialUrl,'_blank','noopener'));
  $('yuktExcel').addEventListener('click', exportExcel);
  $('yuktPrint').addEventListener('click', ()=>{document.body.classList.add('yuktdhara-print');window.print();setTimeout(()=>document.body.classList.remove('yuktdhara-print'),300);});
  $('yuktReset').addEventListener('click', ()=>{$('yuktDistrict').value='ALL';$('yuktJanpad').value='ALL';$('yuktEngineer').value='ALL';$('yuktStatus').value='ALL';cascade();render();});
  ['yuktDistrict','yuktJanpad','yuktEngineer','yuktStatus'].forEach((id)=>$(id).addEventListener('change',()=>{if(id!=='yuktStatus')cascade();render();}));
  document.addEventListener('click',(event)=>{const trigger=event.target.closest('#yuktdharaLauncher,[data-yuktdhara-open]');if(trigger){event.preventDefault();open();}});
  document.addEventListener('keydown',(event)=>{if(event.key==='Escape'&&report.classList.contains('open'))close();});
})();
