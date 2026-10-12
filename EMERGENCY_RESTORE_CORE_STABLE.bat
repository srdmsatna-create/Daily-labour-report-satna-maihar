@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - FULL STABLE CORE RESTORE

echo ==========================================================
echo SRDM SATNA - FULL STABLE CORE RESTORE
echo ==========================================================
echo.
echo This restores the dashboard CORE from the last known stable
 echo 13-09-2026 version BEFORE today's report/layout patches.
echo.
echo RESTORED: index.html, app.js, ongoing-details.js,
echo           ONE_CLICK_DASHBOARD_DATA_UPDATE.bat
echo           update_files\ONE_CLICK_DASHBOARD_DATA_UPDATE.bat
echo.
echo KEPT CURRENT: auto-data.js, official-summary.csv,
echo               fetch-status, live MR/status data and other data files.
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

if not exist backup_before_core_restore mkdir backup_before_core_restore
copy /Y index.html backup_before_core_restore\index.html >nul 2>nul
copy /Y app.js backup_before_core_restore\app.js >nul 2>nul
copy /Y ongoing-details.js backup_before_core_restore\ongoing-details.js >nul 2>nul
copy /Y ONE_CLICK_DASHBOARD_DATA_UPDATE.bat backup_before_core_restore\ONE_CLICK_DASHBOARD_DATA_UPDATE.bat >nul 2>nul

REM Last known coherent core immediately before 13-Sep MIS repair and today's UI patches.
set "STABLE=402bc6b26d877baf70605f9fed6b146c26e044bc"

git checkout %STABLE% -- index.html app.js ongoing-details.js ONE_CLICK_DASHBOARD_DATA_UPDATE.bat update_files/ONE_CLICK_DASHBOARD_DATA_UPDATE.bat
if errorlevel 1 goto :err

REM Keep cache-busting version high so browsers do not reuse broken JS.
powershell -NoProfile -Command "$p='index.html';$s=Get-Content $p -Raw;$s=$s -replace 'app\.js\?v=\d+','app.js?v=9001';$s=$s -replace 'ongoing-details\.js\?v=\d+','ongoing-details.js?v=9001';$s=$s -replace 'styles\.css\?v=\d+','styles.css?v=9001';Set-Content -Path $p -Value $s -Encoding UTF8"
if errorlevel 1 goto :err

git add index.html app.js ongoing-details.js ONE_CLICK_DASHBOARD_DATA_UPDATE.bat update_files/ONE_CLICK_DASHBOARD_DATA_UPDATE.bat
git diff --cached --quiet
if not errorlevel 1 goto :pushonly

git commit -m "Emergency restore stable dashboard core and remove UI patch chain"
if errorlevel 1 goto :err

:pushonly
git push origin main
if errorlevel 1 goto :err

echo.
echo ==========================================================
echo SUCCESS: FULL STABLE CORE RESTORED AND PUBLISHED
echo ==========================================================
echo Current data files were NOT rolled back.
echo.
echo IMPORTANT:
echo 1. Wait 2-3 minutes.
echo 2. CLOSE ALL srdmsatna.online tabs/windows.
echo 3. Open a NEW Chrome Incognito window (Ctrl+Shift+N).
echo 4. Open https://srdmsatna.online
 echo 5. Test Janpad Daily Report first.
echo 6. DO NOT run any APPLY/FIX/icon/font/layout BAT today.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Full stable restore did not complete.
echo Send a screenshot of this window.
echo.
pause
exit /b 1
