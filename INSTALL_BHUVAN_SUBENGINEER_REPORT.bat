@echo off
setlocal EnableExtensions
title SRDM SATNA - Install Bhuvan Sub Engineer Report
color 0A
set "ROOT=C:\Users\welcome\Daily-labour-report-satna-maihar"
if not exist "%ROOT%\index.html" (
  echo ERROR: Dashboard folder not found: %ROOT%
  pause
  exit /b 2
)
cd /d "%ROOT%"
where py >nul 2>nul && (set "PY=py -3") || (set "PY=python")
copy /Y "%~dp0APPLY_BHUVAN_SUBENGINEER_REPORT.py" "%ROOT%\APPLY_BHUVAN_SUBENGINEER_REPORT.py" >nul || goto :fail
%PY% "%ROOT%\APPLY_BHUVAN_SUBENGINEER_REPORT.py" --repo "%ROOT%" || goto :fail
git add -- index.html bhuvan-subengineer-data.js scripts_local/update_bhuvan_subengineer.py
if exist ONE_CLICK_DASHBOARD_DATA_UPDATE.bat git add -- ONE_CLICK_DASHBOARD_DATA_UPDATE.bat
git diff --cached --quiet && goto :nochange
git commit -m "Add Bhuvan Yuktdhara Sub Engineer auto report" || goto :fail
git pull --rebase --autostash origin main || goto :fail
git push origin main || goto :fail
echo.
echo SUCCESS - Bhuvan Sub Engineer report generated and published.
echo Wait 1-3 minutes, then press Ctrl+Shift+R on srdmsatna.online
pause
exit /b 0
:nochange
echo Report is already installed. Data file was refreshed; nothing new to publish.
pause
exit /b 0
:fail
echo.
echo ERROR - Installation/publish stopped. No false success shown.
pause
exit /b 1
