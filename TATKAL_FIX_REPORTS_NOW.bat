@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - TATKAL REPORT FIX

echo ======================================================
echo SRDM SATNA - TATKAL REPORT OPENING FIX
echo ======================================================
echo.
echo This restores ONLY the report UI/runtime files from the
 echo known-good 13-09-2026 build. Current data files stay current.
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set "GOOD=727059adfdaec2c65092abcae20b149996370f9c"

if not exist emergency_backup mkdir emergency_backup
copy /Y index.html emergency_backup\index_before_tatkal_fix.html >nul 2>nul
copy /Y app.js emergency_backup\app_before_tatkal_fix.js >nul 2>nul

REM Restore exact known-good UTF-8/UI files. No PowerShell re-encoding.
git checkout %GOOD% -- index.html app.js srdm-readable-print-final.js srdm-readable-print-final.css
if errorlevel 1 goto :err

REM Keep live/current data files untouched:
REM auto-data.js, auto-status.js, ongoing-details.js, muster-emb-data.js,
REM shramik-niyojan-data.js, vbg-block-stats.js, yuktdhara*.js, data/*

git add index.html app.js srdm-readable-print-final.js srdm-readable-print-final.css
git diff --cached --quiet
if not errorlevel 1 goto :pushonly

git commit -m "Tatkal restore known-good report UI runtime"
if errorlevel 1 goto :err

:pushonly
git push origin main
if errorlevel 1 goto :err

echo.
echo ======================================================
echo SUCCESS: REPORT UI RESTORED TO KNOWN-GOOD BUILD
echo ======================================================
echo Current dashboard data was NOT rolled back.
echo.
echo Wait 2 minutes.
echo Close ALL Chrome tabs of srdmsatna.online.
echo Open a NEW Incognito window and open srdmsatna.online.
echo Do not run any other APPLY/FIX BAT after this.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Tatkal fix did not complete.
echo Send a screenshot of this window.
echo.
pause
exit /b 1
