window.PLANNER_APPROVAL_SUMMARY=[["Satna", "Amarpatan", "Assistant Engineer - Amarpatan", 3661, 25, 3, 22, 14, 0], ["Maihar", "Maihar", "Assistant Engineer - Maihar", 8566, 139, 35, 104, 68, 0], ["Satna", "Majhgawan", "Assistant Engineer - Majhgawan", 2466, 262, 190, 72, 38, 152], ["Satna", "Nagod", "Assistant Engineer - Nagod", 2639, 233, 170, 63, 35, 135], ["Maihar", "Ramnagar", "Assistant Engineer - Ramnagar", 5578, 246, 86, 160, 78, 8], ["Satna", "Rampur baghelan", "Assistant Engineer - Rampur baghelan", 3186, 156, 64, 92, 90, 0], ["Satna", "Sohawal", "Assistant Engineer - Sohawal", 3221, 323, 175, 148, 79, 96], ["Satna", "Unchahara", "Assistant Engineer - Unchahara", 1087, 181, 134, 47, 9, 125]];
window.PLANNER_APPROVAL_TOTALS={"plannerDetail": 30404, "sipri": 1565, "aeApproved": 857, "aePending": 708, "stateReviewed": 411, "statePending": 516};
window.PLANNER_SIPRI_SOURCE={"uploadedDate": "14-10-2026", "files": ["Planning_Summary_Report.xlsx", "Planning_Summary_Report (1).xlsx"], "sourceRows": 8569, "mappingSource": "gp-sector-engineer-master-25-09-2026.csv"};
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