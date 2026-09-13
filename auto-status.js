window.AUTO_FETCH_STATUS={"startedAt":"2026-09-13T04:03:47.324043+00:00","ok":true,"source":"Official VB-G RAM G R6.9 (local PC fetch)","steps":[{"step":"R6.9 category fetch","ok":true,"detail":"8/8 Janpads. Individual Labour/MR=1435/1171; PMAY Labour/MR=1165/1024; Ek Bagiya Labour/MR=229/124."}],"officialDate":"13-09-2026","note":"8/8 Janpads. Individual Labour/MR=1435/1171; PMAY Labour/MR=1165/1024; Ek Bagiya Labour/MR=229/124.","finishedAt":"2026-09-13T04:03:47.324057+00:00"};
(function(){
  function addPlannerSipriCard(){
    if(document.querySelector('.srdm-portal-planner-sipri')) return;
    var sipri=document.querySelector('.srdm-portal-sipri');
    var grid=sipri?sipri.parentElement:document.querySelector('.srdm-app-grid');
    if(!grid) return;
    var card=document.createElement('a');
    card.className='srdm-app-card srdm-portal-card srdm-portal-planner-sipri';
    card.href='planner-sipri-dashboard-hi.html';
    card.target='_blank';
    card.rel='noopener noreferrer';
    card.style.textDecoration='none';
    card.innerHTML='<span class="srdm-app-icon">📊</span><span class="srdm-app-copy"><strong>प्लानर से SIPRI Portal पर कार्य योजना डैशबोर्ड</strong><span>उपयंत्री / क्लस्टर नामवार प्रगति</span></span><span class="srdm-app-new">New</span>';
    if(sipri && sipri.parentElement===grid) sipri.insertAdjacentElement('afterend',card); else grid.appendChild(card);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',addPlannerSipriCard); else addPlannerSipriCard();
  setTimeout(addPlannerSipriCard,500);
})();

(function(){
  function forceR613ReadableFont(){
    var title=document.getElementById('viewTitle');
    var table=document.getElementById('reportTable');
    if(!title||!table) return;
    if((title.textContent||'').indexOf('R6.13 Style Dashboard for Incomplete Works')<0) return;
    title.style.setProperty('font-size','30px','important');
    title.style.setProperty('font-weight','900','important');
    var meta=document.getElementById('viewMeta');
    if(meta){meta.style.setProperty('font-size','15px','important');meta.style.setProperty('font-weight','700','important');}
    table.querySelectorAll('th').forEach(function(el){
      el.style.setProperty('font-size','16px','important');
      el.style.setProperty('line-height','1.2','important');
      el.style.setProperty('padding','9px 7px','important');
      el.style.setProperty('font-weight','900','important');
    });
    table.querySelectorAll('td').forEach(function(el){
      el.style.setProperty('font-size','16px','important');
      el.style.setProperty('line-height','1.25','important');
      el.style.setProperty('padding','9px 7px','important');
      el.style.setProperty('font-weight','700','important');
    });
    table.querySelectorAll('td:nth-child(2)').forEach(function(el){
      el.style.setProperty('font-size','16.5px','important');
      el.style.setProperty('font-weight','800','important');
      el.style.setProperty('min-width','220px','important');
    });
  }
  function start(){
    forceR613ReadableFont();
    var table=document.getElementById('reportTable');
    var title=document.getElementById('viewTitle');
    if(table){new MutationObserver(function(){setTimeout(forceR613ReadableFont,0);}).observe(table,{childList:true,subtree:true});}
    if(title){new MutationObserver(function(){setTimeout(forceR613ReadableFont,0);}).observe(title,{childList:true,subtree:true,characterData:true});}
    setTimeout(forceR613ReadableFont,300);
    setTimeout(forceR613ReadableFont,1000);
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start); else start();
})();
