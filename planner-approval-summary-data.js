window.PLANNER_APPROVAL_SUMMARY=[["Maihar","Amarpatan","Assistant Engineer - Amarpatan",3661,25,8,17,10,0],["Maihar","Maihar","Assistant Engineer - Maihar",8566,137,71,66,50,21],["Satna","Majhgawan","Assistant Engineer - Majhgawan",2466,189,141,48,38,103],["Satna","Nagod","Assistant Engineer - Nagod",2639,149,133,16,5,128],["Maihar","Ramnagar","Assistant Engineer - Ramnagar",5578,243,163,80,25,138],["Satna","Rampur baghelan","Assistant Engineer - Rampur baghelan",3186,117,87,30,29,58],["Satna","Sohawal","Assistant Engineer - Sohawal",3221,168,69,99,49,20],["Satna","Unchahara","Assistant Engineer - Unchahara",1087,37,15,22,0,15]];
window.PLANNER_APPROVAL_TOTALS={plannerDetail:30404,sipri:1065,aeApproved:687,aePending:378,stateReviewed:206,statePending:483};

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