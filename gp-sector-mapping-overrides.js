/* 25-09-2026: authoritative sector corrections from gp-sector-engineer-master-25-09-2026.csv. */
(function(){
  const edits=[
    {janpad:'AMARPATAN',cluster:'TALA',old:'सत्यनारायण मिश्रा',name:'अनिल पटेल अति0 02'},
    {janpad:'MAJHGAWAN',cluster:'KARIGOHI',old:'रमाकांत त्रिपाठी अति0',name:'सत्यनारायण मिश्रा'},
    {janpad:'RAMPUR BAGHELAN',cluster:'BELA',old:'प्रमोद शुक्ला अति0',name:'श्रीमती अन्नपूर्णा सिंह'}
  ];
  function fix(root){
    if(!root||typeof root!=='object')return;
    const seen=new WeakSet(),stack=[root];
    while(stack.length){
      const o=stack.pop();if(!o||typeof o!=='object'||seen.has(o))continue;seen.add(o);
      if(!Array.isArray(o)){
        const j=String(o.janpad||o.block||o.Janpad||'').replace(/\s/g,'').toUpperCase();
        const c=String(o.cluster||o.Cluster||'').replace(/\s/g,'').toUpperCase();
        const e=edits.find(x=>j===x.janpad.replace(/\s/g,'')&&c===x.cluster);
        if(e){for(const key of ['engineer','Engineer','Upyantri','Sub Engineer','Engineer/Cluster'])
          if(typeof o[key]==='string'&&o[key].includes(e.old))o[key]=o[key].replaceAll(e.old,e.name);}
      }
      for(const v of Object.values(o))if(v&&typeof v==='object')stack.push(v);
    }
  }
  fix(window.AUTO_REPORT);fix(window.ONGOING_DETAILS);
  if(typeof UPYANTRI_ROWS!=='undefined')fix(UPYANTRI_ROWS);
})();
