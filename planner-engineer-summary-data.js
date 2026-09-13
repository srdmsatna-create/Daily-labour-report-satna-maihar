window.PLANNER_ENGINEER_SUMMARY=[["Maihar","Amarpatan","अनिल पटेल",1340,0],["Maihar","Amarpatan","अनिल पटेल अति0",833,7],["Maihar","Amarpatan","अनिल पटेल अतिरिक्त 02",394,13],["Maihar","Amarpatan","अश्वनी पटेल",337,3],["Maihar","Amarpatan","श्रीमती साधना चौरे",195,2],["Maihar","Amarpatan","सुनील मिश्रा",562,0],["Maihar","Maihar","योगेन्द्र सिंह अतिरिक्त",1046,6],["Maihar","Maihar","जय अर्खेल",765,23],["Maihar","Maihar","धनंजय त्रिपाठी",762,2],["Maihar","Maihar","बृजेश सिंह",723,5],["Maihar","Maihar","योगेन्द्र सिंह",856,3],["Maihar","Maihar","राज रंजन तिवारी",827,2],["Maihar","Maihar","राज रंजन तिवारी अति0",1344,17],["Maihar","Maihar","राजा भैया सिंह",1183,3],["Maihar","Maihar","श्रीमती मीना अग्रवाल",1079,6],["Maihar","Maihar","सुरेश सिंह",881,3],["Maihar","Ramnagar","अनिल पाण्डेय",1178,0],["Maihar","Ramnagar","राजा राम चंदेल",1101,0],["Maihar","Ramnagar","राजा राम चंदेल अति0",1149,0],["Maihar","Ramnagar","श्रीमती साधना सिंह",1217,0],["Maihar","Ramnagar","संजय गुप्ता",1253,0],["Satna","Majhgawan","सत्य नारायण मिश्रा",568,40],["Satna","Majhgawan","आशीष तिवारी",356,2],["Satna","Majhgawan","आशीष तिवारी अति0",389,14],["Satna","Majhgawan","देवेन्द्र सिंह",364,0],["Satna","Majhgawan","रमाकांत त्रिपाठी",396,18],["Satna","Majhgawan","रमाकांत त्रिपाठी अति0",392,0],["Satna","Majhgawan","सतीस समेले",325,0],["Satna","Nagod","कौशल पटेल",352,1],["Satna","Nagod","कौशल पटेल अति0",357,16],["Satna","Nagod","निशा तिवारी",355,0],["Satna","Nagod","प्रमोद तिवारी",389,5],["Satna","Nagod","राजीवलोचन त्रिपाठी",330,0],["Satna","Nagod","रितेश राजपूत",330,9],["Satna","Nagod","संकल्प राणा",354,0],["Satna","Nagod","हेमंत तिवारी",307,0],["Satna","Rampur baghelan","अजय खरे",381,5],["Satna","Rampur baghelan","भूपेन्द्र सिंह संविदा",389,14],["Satna","Rampur baghelan","मनोज खम्परिया",389,3],["Satna","Rampur baghelan","मनोज खम्परिया अति0",394,20],["Satna","Rampur baghelan","मोतीलाल लढ़िया",387,2],["Satna","Rampur baghelan","रमेश सिंह",386,1],["Satna","Rampur baghelan","प्रमोद शुक्ला",387,3],["Satna","Rampur baghelan","श्रीमती अन्नपूर्णा सिंह",384,4],["Satna","Sohawal","आशुतोष वर्मा",441,36],["Satna","Sohawal","कुलदीप पयासी",431,30],["Satna","Sohawal","धर्मेन्द्र कोरी",427,12],["Satna","Sohawal","महेन्‍द्र पारधी",424,31],["Satna","Sohawal","व्हीके मिश्रा अति0",426,0],["Satna","Sohawal","व्‍ही0के0मिश्रा",427,28],["Satna","Sohawal","शिवलाल भारती",444,24],["Satna","Sohawal","संजय पाण्डेय",478,27],["Satna","Unchahara","दीपक सिंह",183,28],["Satna","Unchahara","राकेश ताम्रकार",163,11],["Satna","Unchahara","राकेश ताम्रकार अति0",152,1],["Satna","Unchahara","राज कुमार पाण्डेय",147,0],["Satna","Unchahara","राज कुमार पाण्डेय अति 0",171,0],["Satna","Unchahara","हरनाम  सिंह",166,0]];
window.PLANNER_OFFICIAL={total:32994,blocks:{Amarpatan:4061,Maihar:9466,Majhgawan:2790,Nagod:2774,Ramnagar:5898,'Rampur baghelan':3365,Sohawal:3498,Unchahara:1142}};

(function(){
  const districtOf=j=>['Amarpatan','Maihar','Ramnagar'].includes(j)?'Maihar':'Satna';
  const norm=s=>String(s||'').replace(/\s+/g,' ').trim().toLowerCase();
  function ensureName(obj,name){let i=obj.e.indexOf(name);if(i<0){obj.e.push(name);i=obj.e.length-1;}return i;}
  window.applyPlannerEngineerCorrections=function(obj){
    if(!obj||!Array.isArray(obj.r)||!Array.isArray(obj.b)||!Array.isArray(obj.e)||!Array.isArray(obj.l))return obj;
    const idxAkh=ensureName(obj,'अखिलेश सोनी अति0');
    const idxSatya=ensureName(obj,'सत्य नारायण मिश्रा');
    const idxAnil2=ensureName(obj,'अनिल पटेल अतिरिक्त 02');
    const idxYogExtra=ensureName(obj,'योगेन्द्र सिंह अतिरिक्त');
    const idxAnnap=ensureName(obj,'श्रीमती अन्नपूर्णा सिंह');
    for(const r of obj.r){
      const jan=obj.b[r[1]],cl=String(obj.l[r[4]]||'').toUpperCase(),eng=norm(obj.e[r[3]]);
      if(jan==='Majhgawan'&&cl==='PRATAPPUR') r[3]=idxAkh;
      else if(jan==='Majhgawan'&&cl==='BADKHERA') r[3]=idxSatya;
      else if(jan==='Amarpatan'&&(eng.includes('सत्यनारायण')||eng.includes('सत्य नारायण'))) r[3]=idxAnil2;
      else if(jan==='Maihar'&&eng.includes('अभिषेक तिवारी')) r[3]=idxYogExtra;
      else if(jan==='Rampur baghelan'&&eng.includes('प्रमोद शुक्ला')&&(eng.includes('अति')||eng.includes('अतिरिक्त'))) r[3]=idxAnnap;
    }
    return obj;
  };
  const nativeParse=JSON.parse.bind(JSON);
  JSON.parse=function(text,reviver){
    const obj=nativeParse(text,reviver);
    if(obj&&Array.isArray(obj.r)&&Array.isArray(obj.b)&&Array.isArray(obj.e)&&Array.isArray(obj.l)) return window.applyPlannerEngineerCorrections(obj);
    return obj;
  };
  async function ensureGzip(){
    if(window.PNWD_GZIP)return;
    await new Promise((resolve,reject)=>{const s=document.createElement('script');s.src='planner-new-work-data-gzip.js';s.onload=resolve;s.onerror=reject;document.head.appendChild(s);});
  }
  async function rebuildSummary(){
    try{
      await ensureGzip();
      if(!window.PNWD_GZIP||typeof DecompressionStream==='undefined')return;
      const bin=Uint8Array.from(atob(window.PNWD_GZIP),c=>c.charCodeAt(0));
      const ds=new DecompressionStream('gzip');
      const txt=await new Response(new Blob([bin]).stream().pipeThrough(ds)).text();
      const obj=window.applyPlannerEngineerCorrections(nativeParse(txt));
      const map=new Map();
      for(const r of obj.r){
        const jan=obj.b[r[1]],eng=obj.e[r[3]],district=districtOf(jan),planner=Number(r[5]||0),sipri=Number(r[6]||0);
        const key=district+'|'+jan+'|'+eng;
        const cur=map.get(key)||[district,jan,eng,0,0];cur[3]+=planner;cur[4]+=sipri;map.set(key,cur);
      }
      const rebuilt=[...map.values()].sort((a,b)=>a[1].localeCompare(b[1])||a[2].localeCompare(b[2],'hi'));
      window.PLANNER_ENGINEER_SUMMARY.splice(0,window.PLANNER_ENGINEER_SUMMARY.length,...rebuilt);
      if(typeof window.updateCascade==='function')window.updateCascade();
      if(typeof window.render==='function')window.render();
      if(typeof window.renderAll==='function')window.renderAll();
      window.dispatchEvent(new CustomEvent('plannerEngineerSummaryRebuilt'));
    }catch(e){console.warn('Planner engineer summary rebuild skipped',e);}
  }
  window.addEventListener('DOMContentLoaded',()=>{
    const R=window.PLANNER_ENGINEER_SUMMARY||[];
    const d=document.getElementById('district'),j=document.getElementById('janpad'),e=document.getElementById('engineer');
    if(d&&j&&e){
      const uniq=a=>[...new Set(a.filter(Boolean))].sort((x,y)=>x.localeCompare(y,'hi'));
      const setOptions=(el,vals,label,keep)=>{el.innerHTML='<option value="ALL">'+label+'</option>'+vals.map(v=>'<option value="'+String(v).replace(/"/g,'&quot;')+'">'+v+'</option>').join('');el.value=vals.includes(keep)?keep:'ALL';};
      const updateEngineers=()=>{const dv=d.value,jv=j.value,old=e.value;setOptions(e,uniq(R.filter(x=>(dv==='ALL'||x[0]===dv)&&(jv==='ALL'||x[1]===jv)).map(x=>x[2])),'सभी उपयंत्री',old);};
      const updateJanpads=()=>{const dv=d.value,old=j.value;setOptions(j,uniq(R.filter(x=>dv==='ALL'||x[0]===dv).map(x=>x[1])),'सभी जनपद',old);updateEngineers();};
      d.addEventListener('change',updateJanpads);j.addEventListener('change',updateEngineers);updateJanpads();
    }
    const note=document.querySelector('.note');
    if(note){
      note.innerHTML='<b>Report Date:</b> 13-09-2026';
      note.style.padding='8px 12px';
      note.style.borderLeft='4px solid #146fd1';
      note.style.fontWeight='700';
    }
    rebuildSummary();
  });
})();