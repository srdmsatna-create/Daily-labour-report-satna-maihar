from pathlib import Path
import shutil

REPO = Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")
P = REPO / "index.html"

if not P.exists():
    raise SystemExit("index.html not found")

B = REPO / "index.before_SINGLE_PAGE_PRINT_FIX.bak.html"
if not B.exists():
    shutil.copy2(P, B)

s = P.read_text(encoding="utf-8")
MARK = "SRDM_SINGLE_PAGE_PRINT_NO_SPLIT_01_09_2026"

if MARK not in s:
    js = r'''
<script id="srdmSinglePagePrintScript">
/* SRDM_SINGLE_PAGE_PRINT_NO_SPLIT_01_09_2026 */
(function(){
  const $id=id=>document.getElementById(id);

  function esc(v){
    return String(v??'')
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;')
      .replace(/"/g,'&quot;');
  }

  function currentView(){
    try{return view||''}catch(e){return ''}
  }

  function cleanTable(){
    const src=$id('reportTable');
    if(!src)return null;
    const t=src.cloneNode(true);
    t.querySelectorAll('script,style,template,noscript').forEach(x=>x.remove());
    t.querySelectorAll('*').forEach(el=>{
      if(el.style){
        el.style.transform='none';
        el.style.rotate='none';
        el.style.writingMode='horizontal-tb';
      }
    });
    return t.outerHTML;
  }

  function buildPrintHtml(orientation){
    const table=cleanTable();
    if(!table)return null;

    const title=$id('viewTitle')?.textContent||'VBGRAMG Report';
    const meta=$id('viewMeta')?.textContent||'';
    const v=currentView();
    const isLand=orientation==='landscape';

    let font=9.2;
    if(v==='official') font=isLand?7.7:6.4;
    else if(v==='engineer') font=isLand?6.8:5.8;
    else if(v==='ongoingdetail') font=isLand?6.2:5.4;
    else font=isLand?8.8:8.0;

    const pageSize=isLand?'A4 landscape':'A4 portrait';

    return `<!doctype html><html><head><meta charset="utf-8"><title>${esc(title)}</title>
    <style>
      @page{size:${pageSize};margin:6mm}
      *{box-sizing:border-box}
      html,body{margin:0!important;padding:0!important;background:#fff!important;transform:none!important;rotate:none!important}
      body{font-family:Arial,'Noto Sans Devanagari',sans-serif;color:#142238}
      h1{font-size:16px;line-height:1.1;margin:0 0 2px;color:#0b3159}
      .meta{font-size:9px;line-height:1.1;color:#607286;margin:0 0 6px}
      .sheet{width:100%;max-width:100%;overflow:visible!important;transform:none!important}
      table{width:100%!important;min-width:0!important;max-width:100%!important;border-collapse:collapse!important;table-layout:fixed!important;font-size:${font}px!important;transform:none!important;rotate:none!important;writing-mode:horizontal-tb!important}
      th,td{border:1px solid #7293b5!important;padding:2.2px 1.6px!important;text-align:center!important;vertical-align:middle!important;white-space:normal!important;overflow-wrap:anywhere!important;word-break:normal!important;line-height:1.12!important;transform:none!important;rotate:none!important;writing-mode:horizontal-tb!important}
      th{background:#cfe0f5!important;color:#0a3158!important;font-weight:800!important}
      .badge{font-size:inherit!important;padding:1px 2px!important}
      script,style,template,noscript{display:none!important}
    </style></head>
    <body>
      <h1>${esc(title)}</h1>
      <div class="meta">${esc(meta)}</div>
      <div class="sheet">${table}</div>
    </body></html>`;
  }

  function singlePagePrint(e){
    if(e){
      e.preventDefault();
      e.stopPropagation();
      e.stopImmediatePropagation();
    }

    const orientation=$id('printOrientation')?.value==='portrait' ? 'portrait' : 'landscape';
    const html=buildPrintHtml(orientation);
    if(!html)return;

    const w=window.open('','_blank','width=1180,height=900');
    if(!w){
      alert('Print popup blocked है। Browser में pop-up allow करें।');
      return;
    }

    w.document.open();
    w.document.write(html);
    w.document.close();
    w.focus();
    setTimeout(()=>w.print(),450);
  }

  const orient=$id('printOrientation');
  if(orient){
    orient.disabled=false;
    orient.title='Portrait या Landscape चुनें';
  }

  const btn=$id('printBtn');
  if(btn){
    btn.textContent='Print / PDF';
    btn.addEventListener('click',singlePagePrint,true);
  }
})();
</script>
'''
    if "</body>" not in s:
        raise RuntimeError("</body> not found")
    s = s.replace("</body>", js + "\n</body>", 1)

P.write_text(s,encoding="utf-8")
print("SINGLE PAGE PRINT FIX INSTALLED")
