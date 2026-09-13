/* SRDM FINAL READABLE PRINT + NAV ICON JS */
(function(){
  "use strict";
  function byId(id){ return document.getElementById(id); }
  function esc(v){return String(v==null?"":v).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");}

  function iconFor(el){
    var key=(el.getAttribute('data-view')||'')+' '+(el.textContent||'');
    key=key.toLowerCase();
    var map=[
      [/official|daily|overview|summary|dashboard/, '▦'],
      [/district|zila/, '◆'],
      [/janpad|block/, '▥'],
      [/engineer|upyantri|sub engineer/, '⚙'],
      [/cluster/, '⌘'],
      [/gram panchayat|\bgp\b|panchayat/, '⌂'],
      [/category|shreni/, '▤'],
      [/ongoing|work details|works/, '☷'],
      [/ek bagi|बगिया/, '♣'],
      [/mandays|labour|persondays/, '♟'],
      [/expenditure|expense|booked/, '₹'],
      [/recovery|vasuli|वसूली/, '↺'],
      [/muster|mr\b/, '✓'],
      [/emuster|e-muster/, '☑'],
      [/priority|alert/, '!'],
      [/dysfunctional|nil|zero/, '⚠'],
      [/state/, '◉'],
      [/download|excel|csv/, '⇩'],
      [/print|pdf/, '⎙']
    ];
    for(var i=0;i<map.length;i++) if(map[i][0].test(key)) return map[i][1];
    return '•';
  }

  function installIcons(root){
    root=root||document;
    var nodes=root.querySelectorAll('.tab,[data-view],.sidebar a,.sidebar button,.nav-item,.menu-item');
    for(var i=0;i<nodes.length;i++){
      var el=nodes[i];
      if(el.dataset.srdmIcon==='1') continue;
      if(el.querySelector('.srdm-nav-icon')){el.dataset.srdmIcon='1';continue;}
      var span=document.createElement('span');
      span.className='srdm-nav-icon';
      span.setAttribute('aria-hidden','true');
      span.textContent=iconFor(el);
      el.insertBefore(span,el.firstChild);
      el.dataset.srdmIcon='1';
    }
  }

  function ensureSipriIcon(root){
    root=root||document;
    var cards=root.querySelectorAll ? root.querySelectorAll('.srdm-portal-sipri') : [];
    for(var i=0;i<cards.length;i++){
      var icon=cards[i].querySelector('.srdm-app-icon');
      if(icon){
        icon.textContent='💧';
        icon.setAttribute('aria-label','Water drop');
      }
    }
  }

  function cleanedTable(){
    var src=byId('reportTable'); if(!src)return null;
    var t=src.cloneNode(true),bad=t.querySelectorAll('script,style,template,noscript,.srdm-nav-icon');
    for(var i=0;i<bad.length;i++)bad[i].remove();
    var all=t.querySelectorAll('*');
    for(var j=0;j<all.length;j++){
      all[j].removeAttribute('width');
      all[j].style.transform='none';all[j].style.rotate='none';all[j].style.writingMode='horizontal-tb';all[j].style.whiteSpace='normal';
    }
    return t.outerHTML;
  }

  function printCurrent(ev){
    if(ev){ev.preventDefault();ev.stopPropagation();if(ev.stopImmediatePropagation)ev.stopImmediatePropagation();}
    var orientation='landscape',sel=byId('printOrientation'); if(sel&&sel.value==='portrait')orientation='portrait';
    var table=cleanedTable(); if(!table)return;
    var title=byId('viewTitle')?byId('viewTitle').textContent:'VBGRAMG Report';
    var meta=byId('viewMeta')?byId('viewMeta').textContent:'';
    var font=orientation==='portrait'?'8.6px':'10.6px';
    var page=orientation==='portrait'?'A4 portrait':'A4 landscape';
    var html="<!doctype html><html><head><meta charset='utf-8'><title>"+esc(title)+"</title><style>"+
      "@page{size:"+page+";margin:5mm}*{box-sizing:border-box}html,body{margin:0!important;padding:0!important;background:#fff!important;transform:none!important;rotate:none!important}"+
      "body{font-family:Arial,'Noto Sans Devanagari',sans-serif;color:#132238}h1{font-size:18px;line-height:1.1;margin:0 0 3px;color:#0b3159}.meta{font-size:10px;line-height:1.15;color:#607286;margin:0 0 7px}.sheet{width:100%;max-width:100%;overflow:visible!important}"+
      "table{width:100%!important;min-width:0!important;max-width:100%!important;border-collapse:collapse!important;table-layout:fixed!important;font-size:"+font+"!important;transform:none!important;writing-mode:horizontal-tb!important}"+
      "th,td{border:1px solid #688cb2!important;padding:3.6px 2.4px!important;text-align:center!important;vertical-align:middle!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important;line-height:1.22!important;transform:none!important;rotate:none!important;writing-mode:horizontal-tb!important}"+
      "th{background:#cfe0f5!important;color:#0a3158!important;font-weight:800!important}script,style,template,noscript{display:none!important}</style></head><body><h1>"+esc(title)+"</h1><div class='meta'>"+esc(meta)+"</div><div class='sheet'>"+table+"</div></body></html>";
    var w=window.open('','_blank','width=1250,height=900'); if(!w){alert('Print popup blocked है। Browser में pop-up allow करें।');return;}
    w.document.open();w.document.write(html);w.document.close();w.focus();setTimeout(function(){w.print();},450);
  }

  function install(){
    installIcons(document);
    ensureSipriIcon(document);
    var orient=byId('printOrientation');if(orient){orient.disabled=false;orient.title='Portrait या Landscape चुनें';}
    var btn=byId('printBtn');if(btn&&!btn.dataset.srdmReadablePrint){btn.dataset.srdmReadablePrint='1';btn.addEventListener('click',printCurrent,true);}
    var obs=new MutationObserver(function(muts){
      for(var i=0;i<muts.length;i++){
        for(var j=0;j<muts[i].addedNodes.length;j++){
          var n=muts[i].addedNodes[j];
          if(n.nodeType===1){installIcons(n);ensureSipriIcon(n);}
        }
      }
      ensureSipriIcon(document);
    });
    obs.observe(document.body,{childList:true,subtree:true});
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',install);else install();
})();
