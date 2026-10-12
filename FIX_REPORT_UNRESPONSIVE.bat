@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - FIX REPORT UNRESPONSIVE

echo ===============================================
echo SRDM SATNA - FIX REPORT UNRESPONSIVE
echo ===============================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% FIX_REPORT_UNRESPONSIVE.py
if errorlevel 1 goto :err

git add index.html FIX_REPORT_UNRESPONSIVE.py FIX_REPORT_UNRESPONSIVE.bat
git commit -m "Fix report page unresponsive performance"
if errorlevel 1 (
  echo No new local changes to commit, continuing...
)
git push origin main
if errorlevel 1 goto :err

echo.
echo SUCCESS: Report freeze fix published.
echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Repair did not complete. Send this screen.
pause
exit /b 1
