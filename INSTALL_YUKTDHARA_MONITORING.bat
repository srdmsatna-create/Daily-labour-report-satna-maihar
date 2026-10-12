@echo off
setlocal EnableExtensions
title SRDM SATNA - Install Yuktdhara Monitoring
color 0A
set "REPO=C:\Users\welcome\Daily-labour-report-satna-maihar"
if not exist "%REPO%\index.html" (color 0C& echo ERROR: Dashboard folder not found: %REPO%& pause& exit /b 1)
cd /d "%REPO%"
where py >nul 2>&1 && set "PY=py"
if not defined PY set "PY=python"
%PY% "%~dp0APPLY_YUKTDHARA_MODULE.py"
if errorlevel 1 (color 0C& echo ERROR: Yuktdhara module installation failed.& pause& exit /b 2)
git add -- index.html yuktdhara-data.js scripts_local/update_yuktdhara_monitoring.py ONE_CLICK_DASHBOARD_DATA_UPDATE.bat
git commit -m "Add official Yuktdhara Monitoring Report module"
git pull --rebase --autostash
if errorlevel 1 goto :fail
git push
if errorlevel 1 goto :fail
echo SUCCESS - Yuktdhara Monitoring Report published.
echo Wait 1-3 minutes and press Ctrl+Shift+R.
pause
exit /b 0
:fail
color 0C
echo ERROR: Module installed locally but GitHub publish failed.
pause
exit /b 3
