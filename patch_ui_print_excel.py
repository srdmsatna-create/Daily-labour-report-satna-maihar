from pathlib import Path
import shutil

REPO = Path(r"C:\Users\welcome\Daily-labour-report-satna-maihar")

def backup(p):
    if p.exists():
        b = p.with_suffix(p.suffix + ".before_ui_print_excel_fix.bak")
        if not b.exists():
            shutil.copy2(p,b)

def patch_html(p):
    if not p.exists():
        raise RuntimeError(f"Missing {p}")
    backup(p)
    s=p.read_text(encoding="utf-8")

    old='<select id="printOrientation" class="print-select" title="Print page orientation"><option value="portrait">Portrait</option><option value="landscape" selected>Landscape</option></select>'
    new='<select id="printOrientation" class="print-select" title="Print page orientation"><option value="portrait" selected>Portrait</option><option value="landscape">Landscape</option></select>'
    s=s.replace(old,new,1)

    old2="view=b.dataset.view;const o=$('printOrientation');if(o){o.value='landscape';o.dispatchEvent(new Event('change'));}render()"
    s=s.replace(old2,"view=b.dataset.view;render()",1)

    s=s.replace("let fontScale=1;","let fontScale=1.18;",1)

    if 'id="excelBtn"' not in s:
        needle='<button id="csvBtn">CSV Export</button>'
        if needle not in s:
            raise RuntimeError("CSV Export button not found")
        s=s.replace(needle, needle+'\n    <button id="excelBtn" class="excel-btn" title="Current report Excel download">Excel Download</button>',1)

    marker="/* SRDM UI PRINT EXCEL FIX 01-09-2026 */"
    if marker not in s:
        css = """
/* SRDM UI PRINT EXCEL FIX 01-09-2026 */
:root{--table-font-scale:1.18}
.report-table th{font-size:calc(11.4px * var(--table-font-scale));line-height:1.22}
.report-table td{font-size:calc(11.2px * var(--table-font-scale));line-height:1.25;padding:6px 6px}
.excel-btn{background:#198754!important;color:#fff!important;border-color:#198754!important;font-weight:850!important}
@media print{
  @page{size:A4 portrait!important;margin:6mm!important}
  body{zoom:.82}
  .report-table{width:100%!important;min-width:0!important;table-layout:fixed!important}
  .report-table th,.report-table td{white-space:normal!important;overflow-wrap:anywhere!important;word-break:break-word!important;line-height:1.13!important}
  body.print-portrait .report-table.official-grid th,
  body.print-portrait .report-table.official-grid td{font-size:calc(6.6px * var(--table-font-scale))!important;padding:2px 2px!important}
}
"""
        pos=s.rfind("</style>")
        if pos < 0:
            raise RuntimeError("</style> not found")
        s=s[:pos]+css+s[pos:]

    jsmarker="SRDM EXCEL DOWNLOAD FIX 01-09-2026"
    if jsmarker not in s:
        js = """
<script>
/* SRDM EXCEL DOWNLOAD FIX 01-09-2026 */
(function(){
  function safeSheetName(v){return String(v||'Report').replace(/[\\\\/\\?\\*\\[\\]\\:]/g,' ').trim().slice(0,31)||'Report';}
  function excelExport(){
    if(!Array.isArray(lastExport)||!lastExport.length){alert('इस report में export करने के लिए data नहीं है।');return;}
    if(typeof XLSX==='undefined'){alert('Excel library load नहीं हुई।');return;}
    const cleanRows=lastExport.map(r=>{const o={};Object.keys(r||{}).forEach(k=>o[k]=(r[k]===null||r[k]===undefined)?'':r[k]);return o;});
    const ws=XLSX.utils.json_to_sheet(cleanRows);
    if(ws['!ref']){
      const range=XLSX.utils.decode_range(ws['!ref']);
      const widths=[];
      for(let c=range.s.c;c<=range.e.c;c++){
        let max=10;
        for(let rr=range.s.r;rr<=Math.min(range.e.r,300);rr++){
          const cell=ws[XLSX.utils.encode_cell({r:rr,c})];
          const val=cell?String(cell.v??''):'';
          max=Math.max(max,Math.min(36,val.length+2));
        }
        widths.push({wch:max});
      }
      ws['!cols']=widths;
      ws['!autofilter']={ref:XLSX.utils.encode_range({s:{r:0,c:0},e:{r:range.e.r,c:range.e.c}})};
    }
    const wb=XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb,ws,safeSheetName(view));
    XLSX.writeFile(wb,`VBGRAMG-${view}-${todayDate()}.xlsx`);
  }
  document.getElementById('excelBtn')?.addEventListener('click',excelExport);
  const o=document.getElementById('printOrientation');
  if(o){o.value='portrait';o.dispatchEvent(new Event('change'));}
})();
</script>
"""
        pos=s.lower().rfind("</body>")
        if pos<0:
            raise RuntimeError("</body> not found")
        s=s[:pos]+js+s[pos:]

    p.write_text(s,encoding="utf-8")
    print("UI/Print/Excel patch applied")

if __name__=="__main__":
    patch_html(REPO/"index.html")
