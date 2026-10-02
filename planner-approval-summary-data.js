window.PLANNER_APPROVAL_SUMMARY=[["Maihar","Amarpatan","Assistant Engineer - Amarpatan",3661,25,6,19,11,0],["Maihar","Maihar","Assistant Engineer - Maihar",8566,137,58,79,50,8],["Maihar","Ramnagar","Assistant Engineer - Ramnagar",5578,243,131,112,42,89],["Satna","Majhgawan","Assistant Engineer - Majhgawan",2466,213,163,50,38,125],["Satna","Nagod","Assistant Engineer - Nagod",2639,149,98,51,35,63],["Satna","Rampur baghelan","Assistant Engineer - Rampur baghelan",3186,117,25,92,90,0],["Satna","Sohawal","Assistant Engineer - Sohawal",3221,220,58,162,79,0],["Satna","Unchahara","Assistant Engineer - Unchahara",1087,39,5,34,9,0]];
window.PLANNER_APPROVAL_TOTALS={"plannerDetail":30404,"sipri":1143,"aeApproved":544,"aePending":599,"stateReviewed":354,"statePending":285};
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