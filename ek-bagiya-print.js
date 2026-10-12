(function(){
  const $=id=>document.getElementById(id);
  const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  function activeEk(){
    return document.querySelector('#v64MainTabs .tab.active')?.dataset?.view==='ekbagiya';
  }
  function sync(){
    const sel=$('ekPrintScope'), go=$('ekPrintGoBtn'), normal=$('printBtn');
    const on=activeEk();
    if(sel) sel.style.display=on?'inline-flex':'none';
    if(go) go.style.display=on?'inline-flex':'none';
    if(normal) normal.style.display=on?'none':'inline-flex';
  }
  function cloneClean(node){
    if(!node)return null;
    const x=node.cloneNode(true);
    x.querySelectorAll('script,style,button,select,input,.no-print').forEach(n=>n.remove());
    return x.outerHTML;
  }
  function printEk(){
    if(!activeEk()){return;}
    const scope=$('ekPrintScope')?.value||'summary';
    const title=$('viewTitle')?.textContent||'एक बगिया माँ के नाम';
    const meta=$('viewMeta')?.textContent||'';
    const summary=cloneClean($('ekBlockSummary'))||'';
    const detail=cloneClean($('reportTable'))||'';
    let content='';
    if(scope==='summary') content=summary;
    else if(scope==='detail') content='<div class="title"><h1>'+esc(title)+'</h1><p>'+esc(meta)+'</p></div>'+detail;
    else content='<div class="title"><h1>'+esc(title)+'</h1><p>'+esc(meta)+'</p></div>'+summary+detail;
    if(!content){alert('Ek Bagiya print data अभी तैयार नहीं है।');return;}
    const doc='<!doctype html><html lang="hi"><head><meta charset="utf-8"><title>'+esc(title)+'</title><style>'+
      '@page{size:A4 landscape;margin:7mm}*{box-sizing:border-box}html,body{margin:0;padding:0;background:#fff;color:#111;font-family:Arial,"Noto Sans Devanagari",sans-serif;-webkit-print-color-adjust:exact;print-color-adjust:exact}'+
      '.title{text-align:center;margin:0 0 4mm}.title h1{font-size:17pt;margin:0 0 1mm}.title p{font-size:8pt;margin:0;color:#475569}'+
      '.ek-block-summary{display:block!important;margin:0 0 5mm!important;border:0!important;border-radius:0!important;overflow:visible!important;background:#fff!important}.ek-block-title{background:#b7ddea!important;color:#0670bc!important;text-align:center!important;font-size:14pt!important;font-weight:900!important;padding:2mm!important;text-decoration:underline!important}'+
      '.table-wrap,.ek-block-wrap{display:block!important;overflow:visible!important;max-height:none!important;border:0!important}'+
      '#ekBlockTable,.ek-block-table{width:100%!important;min-width:0!important;max-width:100%!important;table-layout:fixed!important;border-collapse:collapse!important}'+
      '#ekBlockTable th,#ekBlockTable td,.ek-block-table th,.ek-block-table td{border:1px solid #5f6b76!important;font-size:8pt!important;line-height:1.12!important;padding:1.6mm .7mm!important;text-align:center!important;white-space:normal!important;word-break:break-word!important}'+
      '#ekBlockTable th,.ek-block-table th{background:#eef5ff!important;font-weight:800!important}'+
      '#reportTable{width:100%!important;min-width:0!important;max-width:100%!important;table-layout:fixed!important;border-collapse:collapse!important;margin-top:3mm}'+
      '#reportTable th,#reportTable td{border:1px solid #6f86a1!important;font-size:6pt!important;line-height:1.08!important;padding:.65mm .4mm!important;text-align:center!important;white-space:normal!important;word-break:break-word!important;overflow-wrap:anywhere!important}'+
      '#reportTable th{background:#123f72!important;color:#fff!important;font-weight:800!important}#reportTable thead,#ekBlockTable thead{display:table-header-group!important}#reportTable tr,#ekBlockTable tr{break-inside:avoid!important;page-break-inside:avoid!important}.district-total td,.grand-total td,.total-row td{font-weight:900!important;background:#dbe9fb!important}'+
      '</style></head><body>'+content+'<script>window.onload=function(){setTimeout(function(){window.print()},250)}<\/script></body></html>';
    const blob=new Blob([doc],{type:'text/html'});
    const url=URL.createObjectURL(blob);
    const w=window.open(url,'_blank');
    if(!w){URL.revokeObjectURL(url);alert('Browser ने print window block की है। Pop-ups allow करें।');return;}
    setTimeout(()=>URL.revokeObjectURL(url),15000);
  }
  window.addEventListener('DOMContentLoaded',()=>{
    $('ekPrintGoBtn')?.addEventListener('click',printEk);
    document.querySelectorAll('#v64MainTabs .tab').forEach(b=>b.addEventListener('click',()=>setTimeout(sync,20)));
    sync();
  });
})();