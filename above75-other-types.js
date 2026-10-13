/* Consolidate rainfall harvesting and singleton types within the full expense scope. */
function applyOtherWorkGrouping(){
 const mode=typeof sourceMode==='undefined'?'allAbove75':sourceMode.value;
 for(const r of data)if(r._originalType===undefined)r._originalType=r.type;
 const scope=data.filter(r=>mode==='allAbove75'||(mode==='above100'?r.cost>r.san:r.cost*100<r.san*99));
 const counts=new Map();for(const r of scope)counts.set(r._originalType,(counts.get(r._originalType)||0)+1);
 for(const r of data)r.type=r._originalType==='वर्षा जल संचयन'||counts.get(r._originalType)===1?'अन्य कार्य':r._originalType;
}
