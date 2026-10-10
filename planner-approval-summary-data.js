window.PLANNER_APPROVAL_SUMMARY=[["Maihar","Amarpatan","Assistant Engineer - Amarpatan",3661,25,3,22,14,0],["Maihar","Maihar","Assistant Engineer - Maihar",8566,139,35,104,68,0],["Satna","Majhgawan","Assistant Engineer - Majhgawan",2466,235,168,67,38,130],["Satna","Nagod","Assistant Engineer - Nagod",2639,213,165,48,35,130],["Maihar","Ramnagar","Assistant Engineer - Ramnagar",5578,246,86,160,78,8],["Satna","Rampur baghelan","Assistant Engineer - Rampur baghelan",3186,144,52,92,90,0],["Satna","Sohawal","Assistant Engineer - Sohawal",3221,299,125,174,79,46],["Satna","Unchahara","Assistant Engineer - Unchahara",1087,153,134,19,9,125]];
window.PLANNER_APPROVAL_TOTALS={"plannerDetail":30404,"sipri":1454,"aeApproved":768,"aePending":686,"stateReviewed":411,"statePending":439};
window.PLANNER_SIPRI_SOURCE={"uploadedDate":"10-10-2026","files":["Planning_Summary_Report (7).xlsx","Planning_Summary_Report (8).xlsx"]};
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