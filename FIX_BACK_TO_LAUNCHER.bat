@echo off
setlocal EnableExtensions
cd /d "%~dp0"
title SRDM SATNA - FIX BACK TO LAUNCHER

echo ===============================================
echo SRDM SATNA - FIX BACK TO APPLICATION LAUNCHER
echo ===============================================
echo.

git pull --rebase --autostash origin main
if errorlevel 1 goto :err

set PY=python
where py >nul 2>nul && set PY=py
%PY% FIX_BACK_TO_LAUNCHER.py
if errorlevel 1 goto :err

git add index.html FIX_BACK_TO_LAUNCHER.py FIX_BACK_TO_LAUNCHER.bat
git commit -m "Fix report back button to SRDM launcher"
if errorlevel 1 echo No new local changes to commit, continuing...

git push origin main
if errorlevel 1 goto :err

echo.
echo SUCCESS: Back button fix published.
echo Wait 1-3 minutes, then open srdmsatna.online and press Ctrl+F5.
echo.
pause
exit /b 0

:err
echo.
echo ERROR: Back button fix did not complete. Send this screen.
pause
exit /b 1
