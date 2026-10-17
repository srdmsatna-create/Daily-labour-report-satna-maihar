window.PLANNER_APPROVAL_SUMMARY=[["Maihar","Amarpatan","Assistant Engineer - Amarpatan",3661,25,3,22,14,0],["Maihar","Maihar","Assistant Engineer - Maihar",8566,140,35,105,68,0],["Satna","Majhgawan","Assistant Engineer - Majhgawan",2466,286,137,149,38,99],["Satna","Nagod","Assistant Engineer - Nagod",2639,270,145,125,35,110],["Maihar","Ramnagar","Assistant Engineer - Ramnagar",5578,246,78,168,78,0],["Satna","Rampur baghelan","Assistant Engineer - Rampur baghelan",3186,169,67,102,90,0],["Satna","Sohawal","Assistant Engineer - Sohawal",3221,344,164,180,79,85],["Satna","Unchahara","Assistant Engineer - Unchahara",1087,181,134,47,9,125]];
window.PLANNER_APPROVAL_TOTALS={"plannerDetail":30404,"sipri":1661,"aeApproved":763,"aePending":898,"stateReviewed":411,"statePending":419};
window.PLANNER_SIPRI_SOURCE={"uploadedDate":"17-10-2026","files":["Planning_Summary_Report (2).xlsx","Planning_Summary_Report (3).xlsx"],"sourceRows":8569,"mappingSource":"gp-sector-engineer-master-25-09-2026.csv","sourceFiles":[{"file":"Planning_Summary_Report (2).xlsx","sha256":"0e8b2f10c5a463be453f00284ec15e7846309d7c89175dc29f113f02a6b1d000","rows":5103},{"file":"Planning_Summary_Report (3).xlsx","sha256":"dcb152f655a11933c0cd7d7085d3bef6a8967a32c0e83181b43799f5cf39b015","rows":3466}],"mappedRows":8569,"unmappedRows":0,"districtLabelsNormalized":423,"sipriAbovePlannerRows":71};
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