@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - RESTORE ALL REPORTS TO LAST GOOD

echo ============================================================
echo SRDM SATNA - RESTORE ALL REPORTS TO LAST GOOD FORMAT
echo ============================================================
echo.
echo Restoring report UI/runtime from the last good build before
 echo today's format/encoding patches.
echo.
echo KEPT CURRENT: auto-data.js, official-summary.csv, fetch-status,
echo live MR/status data, muster data, yuktdhara data and other data files.
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

if not exist backup_before_last_good_restore mkdir backup_before_last_good_restore
copy /Y index.html backup_before_last_good_restore\index.html >nul 2>nul
copy /Y app.js backup_before_last_good_restore\app.js >nul 2>nul
copy /Y srdm-readable-print-final.js backup_before_last_good_restore\srdm-readable-print-final.js >nul 2>nul
copy /Y srdm-readable-print-final.css backup_before_last_good_restore\srdm-readable-print-final.css >nul 2>nul
copy /Y ongoing-details.js backup_before_last_good_restore\ongoing-details.js >nul 2>nul
copy /Y ONE_CLICK_DASHBOARD_DATA_UPDATE.bat backup_before_last_good_restore\ONE_CLICK_DASHBOARD_DATA_UPDATE.bat >nul 2>nul

set "GOOD=d1755533066dac9d1e196b062ba4e563fb05feb9"

echo Restoring index/app/print/runtime from %GOOD% ...
git checkout %GOOD% -- index.html app.js srdm-readable-print-final.js srdm-readable-print-final.css ongoing-details.js ONE_CLICK_DASHBOARD_DATA_UPDATE.bat update_files/ONE_CLICK_DASHBOARD_DATA_UPDATE.bat
if errorlevel 1 goto :err

REM Force a fresh browser load without rewriting file encoding.
powershell -NoProfile -Command "$p='index.html';$s=[IO.File]::ReadAllText($p,[Text.UTF8Encoding]::new($false));$s=$s -replace 'app\.js\?v=\d+','app.js?v=91401';$s=$s -replace 'ongoing-details\.js\?v=\d+','ongoing-details.js?v=91401';$s=$s -replace 'srdm-readable-print-final\.js\?v=\d+','srdm-readable-print-final.js?v=91401';$s=$s -replace 'srdm-readable-print-final\.css\?v=\d+','srdm-readable-print-final.css?v=91401';[IO.File]::WriteAllText($p,$s,[Text.UTF8Encoding]::new($false))"
if errorlevel 1 goto :err

git add index.html app.js srdm-readable-print-final.js srdm-readable-print-final.css ongoing-details.js ONE_CLICK_DASHBOARD_DATA_UPDATE.bat update_files/ONE_CLICK_DASHBOARD_DATA_UPDATE.bat
git diff --cached --quiet
if not errorlevel 1 goto :pushonly

git commit -m "Restore all reports to last good pre-patch format"
if errorlevel 1 goto :err

:pushonly
git push origin main
if errorlevel 1 goto :err

echo.
echo ============================================================
echo SUCCESS: LAST GOOD REPORT FORMAT RESTORED
 echo ============================================================
echo Current live data files were NOT rolled back.
echo.
echo 1. Wait 2-3 minutes.
echo 2. Close ALL srdmsatna.online tabs/windows.
echo 3. Open a NEW Chrome Incognito window.
echo 4. Open https://srdmsatna.online
 echo 5. Do not run any APPLY/FIX/font/icon/layout BAT.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Restore did not complete.
echo Send screenshot of this Command Prompt window.
echo.
pause
exit /b 1
