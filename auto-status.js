window.AUTO_FETCH_STATUS={"startedAt":"2026-09-17T03:25:10.187948+00:00","ok":true,"source":"Official VB-G RAM G R6.9 (local PC fetch)","steps":[{"step":"R6.9 category fetch","ok":true,"detail":"8/8 Janpads. Individual Labour/MR=1172/947; PMAY Labour/MR=964/839; Ek Bagiya Labour/MR=172/89."}],"officialDate":"17-09-2026","note":"8/8 Janpads. Individual Labour/MR=1172/947; PMAY Labour/MR=964/839; Ek Bagiya Labour/MR=172/89.","finishedAt":"2026-09-17T03:25:10.187966+00:00"};
(function(){
  function latestOfficialDate(){
    return (window.SHRAMIK_NIYOJAN&&window.SHRAMIK_NIYOJAN.officialDate)||
           (window.AUTO_FETCH_STATUS&&window.AUTO_FETCH_STATUS.officialDate)||"";
  }
  function syncShramikDate(){
    var d=latestOfficialDate();
    if(!d||!document.body)return;
    var all=document.body.querySelectorAll('*');
    for(var i=0;i<all.length;i++){
      var el=all[i];
      if(el.children.length) continue;
      var t=(el.textContent||'').trim();
      if(/^दिनांक\s+\d{2}-\d{2}-\d{4}$/.test(t)){
        el.textContent='दिनांक '+d;
      }
    }
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',syncShramikDate);
  else syncShramikDate();
  setTimeout(syncShramikDate,500);
  setTimeout(syncShramikDate,1500);
  setTimeout(syncShramikDate,3000);
  if(window.MutationObserver){
    var mo=new MutationObserver(syncShramikDate);
    var start=function(){ if(document.body) mo.observe(document.body,{childList:true,subtree:true,characterData:true}); };
    if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',start); else start();
  }
})();
