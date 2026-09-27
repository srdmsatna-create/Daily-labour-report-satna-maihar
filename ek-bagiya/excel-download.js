(function(){
  function parseCSV(text){
    text=text.replace(/^\uFEFF/,'');
    const rows=[];let row=[],cell='',quoted=false;
    for(let i=0;i<text.length;i++){
      const c=text[i],n=text[i+1];
      if(quoted){if(c==='"'&&n==='"'){cell+='"';i++}else if(c==='"')quoted=false;else cell+=c}
      else if(c==='"')quoted=true;
      else if(c===','){row.push(cell);cell=''}
      else if(c==='\n'){row.push(cell.replace(/\r$/,''));rows.push(row);row=[];cell=''}
      else cell+=c;
    }
    if(cell||row.length){row.push(cell.replace(/\r$/,''));rows.push(row)}
    return rows;
  }
  function esc(v){return String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
  function sheetXML(name,rows){
    const textCols=new Set(['Zila','Janpad','Upyantri','Cluster','Engineer/Cluster','Panchayat Name','Work Code','Work Name','Work Status','Fin Year','Expenditure Bucket','New Exp Band','NREGA Match Status','VBGRAMG Match Status','Source Work Type','Mapping Status']);
    const headers=rows[0]||[];
    const body=rows.map((r,ri)=>'<Row>'+r.map((v,i)=>{
      const raw=String(v??''),numeric=!ri?false:!textCols.has(headers[i])&&raw!==''&&Number.isFinite(Number(raw.replace(/,/g,'')));
      return '<Cell'+(!ri?' ss:StyleID="Header"':'')+'><Data ss:Type="'+(numeric?'Number':'String')+'">'+esc(numeric?Number(raw.replace(/,/g,'')):raw)+'</Data></Cell>';
    }).join('')+'</Row>').join('');
    return '<Worksheet ss:Name="'+esc(name)+'"><Table>'+body+'</Table><WorksheetOptions xmlns="urn:schemas-microsoft-com:office:excel"><FreezePanes/><FrozenNoSplit/><SplitHorizontal>1</SplitHorizontal><TopRowBottomPane>1</TopRowBottomPane></WorksheetOptions></Worksheet>';
  }
  window.downloadExcelWorkbook=async function(btn){
    const old=btn.textContent;btn.disabled=true;btn.textContent='Excel बन रहा है…';
    try{
      const [rankText,workText]=await Promise.all(['upyantri_rank_full_table.csv','work_details.csv'].map(x=>fetch(x,{cache:'no-store'}).then(r=>{if(!r.ok)throw new Error(x);return r.text()})));
      const xml='<?xml version="1.0"?><Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet" xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"><Styles><Style ss:ID="Header"><Font ss:Bold="1" ss:Color="#FFFFFF"/><Interior ss:Color="#155F95" ss:Pattern="Solid"/></Style></Styles>'+sheetXML('Upyantri Ranking',parseCSV(rankText))+sheetXML('Work Details',parseCSV(workText))+'</Workbook>';
      const a=document.createElement('a');a.href=URL.createObjectURL(new Blob(['\uFEFF'+xml],{type:'application/vnd.ms-excel'}));a.download='Ek_Bagiya_Work_Details_756_09-09-2026.xls';document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(a.href),1000);
    }catch(e){alert('Excel download तैयार नहीं हो पाया। कृपया दोबारा प्रयास करें।')}
    finally{btn.disabled=false;btn.textContent=old}
  };
})();


(function(){
  const pick=(o,...keys)=>{for(const k of keys){if(o&&o[k]!==undefined&&o[k]!==null&&String(o[k])!=='')return o[k]}return ''};
  const num=v=>{const n=Number(String(v??'').replace(/,/g,''));return Number.isFinite(n)?n:0};
  const fmt=v=>typeof v==='number'?v.toLocaleString('en-IN',{maximumFractionDigits:2}):String(v??'');
  const esc=v=>String(v??'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');

  function getWorks(){
    let rows=[];
    try{
      if(Array.isArray(window.WORK_DETAILS)) rows=window.WORK_DETAILS;
      else if(typeof WORK_DETAILS!=='undefined'&&Array.isArray(WORK_DETAILS)) rows=WORK_DETAILS;
      else if(Array.isArray(window.EK_BAGIYA_WORK_DETAILS)) rows=window.EK_BAGIYA_WORK_DETAILS;
    }catch(e){}
    const seen=new Set();
    return rows.filter(r=>{
      const code=String(pick(r,'Work Code','workCode','code')).trim();
      if(!code||seen.has(code))return false;
      seen.add(code);return true;
    });
  }

  function renderAllWorks(){
    const works=getWorks();
    if(!works.length)return;
    let box=document.getElementById('srdmEkAll755Works');
    if(!box){
      box=document.createElement('section');
      box.id='srdmEkAll755Works';
      box.style.cssText='margin:22px auto 32px;max-width:1650px;background:#fff;border:1px solid #c7d5e5;border-radius:14px;box-shadow:0 5px 18px rgba(20,50,85,.08);overflow:hidden';
      const footer=document.querySelector('footer');
      if(footer&&footer.parentNode)footer.parentNode.insertBefore(box,footer);else document.body.appendChild(box);
    }
    const rows=works.slice().sort((a,b)=>
      String(pick(a,'Janpad')).localeCompare(String(pick(b,'Janpad')),'hi')||
      String(pick(a,'Upyantri','Engineer/Cluster','Sub Engineer')).localeCompare(String(pick(b,'Upyantri','Engineer/Cluster','Sub Engineer')),'hi')||
      String(pick(a,'Panchayat Name','GP')).localeCompare(String(pick(b,'Panchayat Name','GP')),'hi')||
      String(pick(a,'Work Code')).localeCompare(String(pick(b,'Work Code')))
    );
    let h='<div style="padding:14px 16px;background:linear-gradient(125deg,#0b3159,#1769aa);color:#fff"><div style="font-size:20px;font-weight:900">एक बगिया माँ के नाम — सभी '+rows.length+' कार्यों की एक साथ सूची</div><div style="font-size:12px;opacity:.9;margin-top:4px">कोई 300-row limit नहीं • सभी verified works नीचे एक ही सूची में</div></div>';
    h+='<div style="overflow:auto;max-height:none"><table style="border-collapse:collapse;min-width:2050px;width:100%;font-size:12px"><thead><tr>'+
      ['S.No.','District','Janpad','Sub Engineer / Upyantri','Cluster','GP','FY','Status','Work Code','Work Name','Sanction ₹','MGNREGA Booked ₹','VB-G RAM G Booked ₹','Overall Booked ₹','Overall Exp %','MGNREGA Mandays Till 31 Mar 2026','NREGA Mandays 01 Apr–30 Jun','Mandays 01 Jul–Today']
      .map(x=>'<th style="position:sticky;top:0;z-index:2;background:#d5e5f6;color:#07325e;border:1px solid #8aa2bd;padding:7px 6px;text-align:center">'+x+'</th>').join('')+
      '</tr></thead><tbody>';
    rows.forEach((r,i)=>{
      const san=num(pick(r,'Sanction Amount Total','Sanction Total Rs','sanction'));
      const nrega=num(pick(r,'MGNREGA Total Booked Till 30 June','MGNREGA Booked ₹','nregaBooked'));
      const vbg=num(pick(r,'VBGRAMG Total Booked','VB-G RAM G Booked ₹','vbgBooked'));
      const overall=num(pick(r,'Overall Total Booked','Overall Booked ₹','overallBooked')) || (nrega+vbg);
      const exp=pick(r,'Overall Expenditure %','Overall Exp %');
      const tillMar=pick(r,'Mandays 2025-2026','MGNREGA Mandays Generate Till 31 March 2026','mandaysTillMar31');
      const aprJun=pick(r,'NREGA Till 30 June Mandays','Mandays 01 Apr-30 Jun 2026','NREGA Mandays 01 Apr–30 Jun','nregaAprJunMandays');
      const jul=pick(r,'Mandays 2026-2027','Mandays 01 Jul–Today','julyMandays');
      const vals=[
        i+1,pick(r,'Zila','District'),pick(r,'Janpad'),pick(r,'Upyantri','Engineer/Cluster','Sub Engineer'),pick(r,'Cluster'),
        pick(r,'Panchayat Name','GP'),pick(r,'Fin Year','FY'),pick(r,'Work Status','Status'),pick(r,'Work Code'),pick(r,'Work Name'),
        san,nrega,vbg,overall,(String(exp).includes('%')?exp:(num(exp).toFixed(1)+'%')),tillMar,aprJun,jul
      ];
      h+='<tr>'+vals.map((v,j)=>'<td style="border:1px solid #aab8c8;padding:6px 5px;vertical-align:top;'+(j===9?'min-width:320px;text-align:left;':'text-align:center;')+'">'+esc(typeof v==='number'?fmt(v):v)+'</td>').join('')+'</tr>';
    });
    h+='</tbody></table></div>';
    box.innerHTML=h;
  }

  function boot(){
    renderAllWorks();
    setTimeout(renderAllWorks,800);
    setTimeout(renderAllWorks,2200);
  }
  if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',boot,{once:true});else boot();
})();
