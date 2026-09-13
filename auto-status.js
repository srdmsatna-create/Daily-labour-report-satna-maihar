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
