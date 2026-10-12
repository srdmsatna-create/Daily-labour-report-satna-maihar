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
