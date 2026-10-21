window.PLANNER_APPROVAL_SUMMARY=[["Maihar","Amarpatan","Assistant Engineer - Amarpatan",3661,25,3,22,14,0],["Maihar","Maihar","Assistant Engineer - Maihar",8566,140,35,105,68,0],["Satna","Majhgawan","Assistant Engineer - Majhgawan",2466,345,153,192,38,115],["Satna","Nagod","Assistant Engineer - Nagod",2639,275,145,130,35,110],["Maihar","Ramnagar","Assistant Engineer - Ramnagar",5578,263,78,185,78,0],["Satna","Rampur baghelan","Assistant Engineer - Rampur baghelan",3186,169,67,102,90,0],["Satna","Sohawal","Assistant Engineer - Sohawal",3221,344,164,180,79,85],["Satna","Unchahara","Assistant Engineer - Unchahara",1087,196,134,62,9,125]];
window.PLANNER_APPROVAL_TOTALS={"plannerDetail":30404,"sipri":1757,"aeApproved":779,"aePending":978,"stateReviewed":411,"statePending":435};
window.PLANNER_SIPRI_SOURCE={"uploadedDate":"21-10-2026","files":["Planning_Summary_Report (7)(1).xlsx","Planning_Summary_Report (6).xlsx"],"sourceRows":8569,"mappingSource":"gp-sector-engineer-master-25-09-2026.csv","sourceFiles":[{"file":"Planning_Summary_Report (7)(1).xlsx","sha256":"0c2f0747894f8abb15a5d7b522441cfe57748729366ffa858eb38f87ecab7ae7","rows":5103},{"file":"Planning_Summary_Report (6).xlsx","sha256":"37ee773433be656e90275176551ba8348af4a8f071fcc9c7a3bd5cf8b17c3c86","rows":3466}],"mappedRows":8569,"unmappedRows":0,"districtLabelsNormalized":423,"sipriAbovePlannerRows":78};
// Layout readability override for Planner→SIPRI Sub Engineer report.
window.addEventListener('DOMContentLoaded',()=>{
  const st=document.createElement('style');
  st.textContent=`
    .engineer-summary{min-width:1080px!important;max-width:1180px!important;margin:0 auto!important;table-layout:fixed!important}
    .engineer-summary th:nth-child(1),.engineer-summary td:nth-child(1){width:8%!important}
    .engineer-summary th:nth-child(2),.engineer-summary td:nth-child(2){width:17%!important;white-space:nowrap!important}
    .engineer-summary th:nth-child(3),.engineer-summary td:nth-child(3){width:27%!important;white-space:nowrap!important}
    .engineer-summary th:nth-child(4),.engineer-summary td:nth-child(4){width:16%!important}
    .engineer-summary th:nth-child(5),.engineer-summary td:nth-child(5){width:11%!important}
    .engineer-summary th:nth-child(6),.engineer-summary td:nth-child(6){width:11%!important}
    .engineer-summary th:nth-child(7),.engineer-summary td:nth-child(7){width:10%!important}
  `;
  document.head.appendChild(st);
});
